from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import login_required, login_user, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from flasgger import Swagger
from werkzeug.utils import secure_filename
import os
import json
import uuid
import tempfile
import ipaddress
import sqlite3
import requests
from urllib.parse import urlparse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Importações do sistema SAPIENS
try:
    from ..tools.academic_logger import get_auditor
    from ..tools.security_validator import AcademicSecurityValidator
    from .auth import login_manager, init_auth_db, Usuario
except ImportError:
    # Fallback para import direto
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src', 'Sapiens_MultiAgente'))
    from tools.academic_logger import get_auditor
    from tools.security_validator import AcademicSecurityValidator
    from web.auth import login_manager, init_auth_db, Usuario


DB_PATH = os.getenv('SAPIENS_DB_PATH', 'sapiens.db')


def _get_db():
    """Retorna conexão SQLite com row_factory configurado."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    """Cria tabelas do banco se não existirem."""
    with _get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analises (
                id          TEXT PRIMARY KEY,
                usuario_id  TEXT NOT NULL DEFAULT 'sistema',
                topico      TEXT NOT NULL,
                status      TEXT NOT NULL DEFAULT 'processando',
                progresso   INTEGER NOT NULL DEFAULT 0,
                arquivos    TEXT NOT NULL DEFAULT '[]',
                resultados  TEXT,
                erro        TEXT,
                criado_em   TEXT NOT NULL,
                atualizado_em TEXT,
                concluido_em  TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_analises_usuario ON analises (usuario_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_analises_criado ON analises (criado_em DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_analises_status ON analises (status)")
        conn.commit()


class SapiensWebInterface:
    """Interface web para SAPIENS"""

    def __init__(self, host='127.0.0.1', port=4000, debug=False):
        self.host = host
        self.port = port
        self.debug = debug

        # Configurações de upload
        self.upload_config = {
            'UPLOAD_FOLDER': 'uploads',
            'MAX_CONTENT_LENGTH': 100 * 1024 * 1024,  # 100MB
            'ALLOWED_EXTENSIONS': {'csv', 'xlsx', 'xls', 'pdf', 'docx', 'txt'}
        }

        # Cria diretório de uploads e inicializa bancos
        os.makedirs(self.upload_config['UPLOAD_FOLDER'], exist_ok=True)
        _init_db()
        init_auth_db()

        # Inicializa componentes
        self.auditor = get_auditor()
        self.security_validator = AcademicSecurityValidator()

        # Cache em memória para análises ativas (sincronizado com o banco)
        self.analises_ativas = self._carregar_analises_ativas()

        # Monitor de métricas da plataforma
        from .monitoring import SapiensMonitor
        self.monitor = SapiensMonitor(DB_PATH)
        self.monitor.start()

    # ------------------------------------------------------------------
    # Persistência SQLite
    # ------------------------------------------------------------------

    def _carregar_analises_ativas(self) -> dict:
        """Marca análises órfãs como erro e retorna cache vazio (workers não sobrevivem a reinícios)."""
        try:
            with _get_db() as conn:
                conn.execute(
                    """UPDATE analises
                       SET status = 'erro',
                           erro = 'Análise interrompida (servidor reiniciado)',
                           atualizado_em = ?
                       WHERE status NOT IN ('concluida', 'erro')""",
                    (datetime.now().isoformat(),)
                )
                conn.commit()
        except Exception:
            pass
        return {}

    def _row_para_dict(self, row) -> dict:
        d = dict(row)
        d['arquivos'] = json.loads(d.get('arquivos') or '[]')
        return d

    def _salvar_analise(self, analise_id: str):
        """Persiste o estado atual da análise no banco."""
        info = self.analises_ativas.get(analise_id)
        if not info:
            return
        with _get_db() as conn:
            conn.execute("""
                INSERT INTO analises
                    (id, usuario_id, topico, status, progresso, arquivos, resultados, erro, criado_em, atualizado_em, concluido_em)
                VALUES
                    (:id, :usuario_id, :topico, :status, :progresso, :arquivos, :resultados, :erro, :criado_em, :atualizado_em, :concluido_em)
                ON CONFLICT(id) DO UPDATE SET
                    status        = excluded.status,
                    progresso     = excluded.progresso,
                    arquivos      = excluded.arquivos,
                    resultados    = excluded.resultados,
                    erro          = excluded.erro,
                    atualizado_em = excluded.atualizado_em,
                    concluido_em  = excluded.concluido_em
            """, {
                'id': analise_id,
                'usuario_id': info.get('usuario_id', 'sistema'),
                'topico': info.get('topico_pesquisa', ''),
                'status': info.get('status', 'processando'),
                'progresso': info.get('progresso', 0),
                'arquivos': json.dumps(info.get('arquivos', []), ensure_ascii=False),
                'resultados': info.get('resultados'),
                'erro': info.get('erro'),
                'criado_em': info.get('timestamp_inicio'),
                'atualizado_em': info.get('timestamp_atualizacao'),
                'concluido_em': info.get('timestamp_fim'),
            })
            conn.commit()

    def _buscar_analise(self, analise_id: str) -> dict | None:
        """Busca análise no cache ou no banco."""
        if analise_id in self.analises_ativas:
            return self.analises_ativas[analise_id]
        try:
            with _get_db() as conn:
                row = conn.execute(
                    "SELECT * FROM analises WHERE id = ?", (analise_id,)
                ).fetchone()
            if row:
                return self._row_para_dict(row)
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # Criação da aplicação Flask
    # ------------------------------------------------------------------

    def create_app(self):
        """Cria aplicação Flask com todas as rotas e middlewares."""
        app = Flask(__name__)
        app.config['UPLOAD_FOLDER'] = self.upload_config['UPLOAD_FOLDER']
        app.config['MAX_CONTENT_LENGTH'] = self.upload_config['MAX_CONTENT_LENGTH']

        # Carrega secret key de variável de ambiente
        app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

        # Autenticação
        login_manager.init_app(app)

        # Proteção CSRF
        CSRFProtect(app)

        # Documentação Swagger
        swagger_config = {
            'headers': [],
            'specs': [{
                'endpoint': 'apispec',
                'route': '/api/v1/spec.json',
                'rule_filter': lambda rule: rule.startswith('/api/'),
                'model_filter': lambda tag: True,
            }],
            'static_url_path': '/flasgger_static',
            'swagger_ui': True,
            'specs_route': '/api/docs',
        }
        swagger_template = {
            'info': {
                'title': 'SAPIENS API',
                'description': 'API REST da Plataforma Acadêmica Multiagente de Análise de Dados',
                'version': '1.0.0',
                'contact': {'name': 'SAPIENS', 'email': 'suporte@sapiens.edu.br'},
            },
            'securityDefinitions': {
                'cookieAuth': {'type': 'apiKey', 'in': 'cookie', 'name': 'session'}
            },
        }
        Swagger(app, config=swagger_config, template=swagger_template)

        # Rate limiting
        limiter = Limiter(
            get_remote_address,
            app=app,
            default_limits=["200 per hour", "50 per minute"],
            storage_uri="memory://"
        )

        # Registra rotas por grupo
        self._setup_template_filters(app)
        self._setup_auth_routes(app)
        self._setup_page_routes(app, limiter)
        self._setup_system_routes(app)
        self._setup_config_routes(app)
        self._setup_api_v1_routes(app)

        return app

    # ------------------------------------------------------------------
    # Setup de rotas — Template Filters
    # ------------------------------------------------------------------

    def _setup_template_filters(self, app):
        @app.template_filter('fmt_dt')
        def fmt_dt(value):
            if not value:
                return ''
            s = str(value)[:19].replace('T', ' ')
            try:
                dt = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                return dt.strftime('%d/%m/%Y %H:%M')
            except Exception:
                return s

    # ------------------------------------------------------------------
    # Setup de rotas — Autenticação
    # ------------------------------------------------------------------

    def _setup_auth_routes(self, app):
        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if current_user.is_authenticated:
                return redirect(url_for('index'))
            if request.method == 'POST':
                username = request.form.get('username', '').strip()
                senha = request.form.get('senha', '')
                usuario, msg_erro = Usuario.autenticar(username, senha)
                if usuario:
                    login_user(usuario)
                    next_page = request.args.get('next')
                    return redirect(next_page or url_for('index'))
                flash(msg_erro or 'Usuário ou senha incorretos.', 'error')
            return render_template('login.html')

        @app.route('/logout')
        @login_required
        def logout():
            logout_user()
            flash('Sessão encerrada com sucesso.', 'success')
            return redirect(url_for('login'))

    # ------------------------------------------------------------------
    # Setup de rotas — Páginas e funcionalidades principais
    # ------------------------------------------------------------------

    def _setup_page_routes(self, app, limiter):
        @app.route('/')
        @login_required
        def index():
            """Página inicial"""
            return render_template('index.html')

        @app.route('/sobre')
        def sobre():
            """Página sobre o SAPIENS"""
            return render_template('sobre.html')

        @app.route('/analise', methods=['GET', 'POST'])
        @login_required
        def analise():
            """Página de análise de dados"""
            if request.method == 'POST':
                return self._processar_analise(app)
            return render_template('analise.html')

        @app.route('/upload', methods=['POST'])
        @login_required
        @limiter.limit("5 per minute")
        def upload_arquivo():
            """Endpoint para upload de arquivos"""
            return self._handle_upload(app)

        @app.route('/status/<analise_id>')
        @login_required
        @limiter.limit("10 per minute")
        def status_analise(analise_id):
            """Verifica status de análise"""
            return self._get_analise_status(analise_id)

        @app.route('/resultados/<analise_id>')
        @login_required
        def resultados_analise(analise_id):
            """Exibe resultados da análise"""
            return self._get_analise_resultados(analise_id)

        @app.route('/historico')
        @login_required
        def historico():
            """Listagem de análises anteriores."""
            return self._get_historico(current_user.id)

        @app.route('/stream/<analise_id>')
        def stream_progresso(analise_id):
            """Server-Sent Events: envia progresso em tempo real."""
            from flask import Response
            return Response(self._event_generator(analise_id), mimetype='text/event-stream',
                            headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

        @app.route('/export/<analise_id>/<formato>')
        def export_analise(analise_id, formato):
            """Exporta resultados nos formatos: pdf, txt"""
            return self._exportar_analise(analise_id, formato)

    # ------------------------------------------------------------------
    # Setup de rotas — Sistema e monitoramento
    # ------------------------------------------------------------------

    def _setup_system_routes(self, app):
        @app.route('/status')
        @app.route('/api/health')
        @login_required
        def health_check():
            """Health check do sistema.
            ---
            tags:
              - Sistema
            responses:
              200:
                description: Sistema saudável
                schema:
                  type: object
                  properties:
                    status:
                      type: string
                      example: healthy
                    timestamp:
                      type: string
                      example: "2025-01-01T12:00:00"
                    versao:
                      type: string
                      example: "2.0.0"
            """
            import sqlite3 as _sqlite3

            # Verifica banco de dados
            db_ok = False
            total_analises = 0
            try:
                with _sqlite3.connect(DB_PATH) as conn:
                    total_analises = conn.execute("SELECT COUNT(*) FROM analises").fetchone()[0]
                    db_ok = True
            except Exception:
                pass

            # Verifica pasta de uploads
            upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
            upload_ok = os.path.isdir(upload_folder)

            analises_em_andamento = sum(
                1 for a in self.analises_ativas.values()
                if a.get('status') not in ('concluida', 'erro')
            )

            payload = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'sistema': 'SAPIENS Web Interface',
                'versao': '2.1.0',
                'banco_dados': 'ok' if db_ok else 'erro',
                'uploads': 'ok' if upload_ok else 'erro',
                'total_analises': total_analises,
                'analises_em_andamento': analises_em_andamento,
            }

            # Retorna HTML para browsers, JSON para clientes API
            accept = request.headers.get('Accept', '')
            if 'text/html' in accept:
                monitor_data = self.monitor.summary()
                return render_template('status.html', **payload, monitor=monitor_data)
            return jsonify(payload)

        @app.route('/api/monitoring')
        @login_required
        def api_monitoring():
            """Métricas de monitoramento da plataforma SAPIENS."""
            data = self.monitor.summary()
            data['history'] = self.monitor.history(last_n=20)
            return jsonify(data)

    # ------------------------------------------------------------------
    # Setup de rotas — Configuração LLM
    # ------------------------------------------------------------------

    def _setup_config_routes(self, app):
        @app.route('/api/config/llm', methods=['GET'])
        @login_required
        def api_llm_config_get():
            """Retorna configuração atual de LLM e modelos disponíveis."""
            from ..config.llm_settings import load_llm_config
            return jsonify(load_llm_config())

        @app.route('/api/config/llm', methods=['POST'])
        @login_required
        def api_llm_config_set():
            """Altera modelo padrão ou modelo de agente específico.

            Trocar modelo padrão (todos):  {"modelo": "deepseek_r1"}
            Trocar modelo de um agente:    {"agente": "revisor_de_qualidade_cientifica", "modelo": "deepseek_r1"}
            A troca é efetivada na próxima análise iniciada.
            """
            from ..config.llm_settings import set_active_model, set_agent_model
            data = request.get_json(silent=True) or {}
            chave = data.get("modelo", "").strip()
            agente = data.get("agente", "").strip()
            if not chave:
                return jsonify({"ok": False, "erro": "Campo 'modelo' obrigatório"}), 400
            try:
                if agente:
                    modelo = set_agent_model(agente, chave)
                    return jsonify({"ok": True, "agente": agente, "modelo": modelo})
                modelo = set_active_model(chave)
                return jsonify({"ok": True, "modelo_ativo": modelo})
            except ValueError as e:
                return jsonify({"ok": False, "erro": str(e)}), 400

    # ------------------------------------------------------------------
    # Setup de rotas — API REST v1
    # ------------------------------------------------------------------

    def _setup_api_v1_routes(self, app):
        @app.route('/api/v1/analises', methods=['GET'])
        @login_required
        def api_listar_analises():
            """Lista análises do usuário autenticado.
            ---
            tags:
              - Análises
            parameters:
              - name: status
                in: query
                type: string
                required: false
                description: "Filtrar por status: processando, concluida, erro"
              - name: limit
                in: query
                type: integer
                required: false
                default: 50
                description: Número máximo de resultados (máx 200)
            responses:
              200:
                description: Lista de análises
                schema:
                  type: object
                  properties:
                    analises:
                      type: array
                    total:
                      type: integer
              401:
                description: Não autenticado
            """
            filtro_status = request.args.get('status')
            limit = min(int(request.args.get('limit', 50)), 200)
            usuario_id = current_user.id

            try:
                with _get_db() as conn:
                    query = "SELECT * FROM analises WHERE usuario_id = ?"
                    params = [usuario_id]
                    if filtro_status:
                        query += " AND status = ?"
                        params.append(filtro_status)
                    query += " ORDER BY criado_em DESC LIMIT ?"
                    params.append(limit)
                    rows = conn.execute(query, params).fetchall()
                analises = [self._row_para_dict(r) for r in rows]
                return jsonify({'analises': analises, 'total': len(analises)})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/v1/analises', methods=['POST'])
        @login_required
        def api_iniciar_analise():
            """Inicia nova análise via API.
            ---
            tags:
              - Análises
            parameters:
              - in: body
                name: body
                required: true
                schema:
                  type: object
                  required: [topico_pesquisa]
                  properties:
                    topico_pesquisa:
                      type: string
                      example: "Análise de desempenho acadêmico 2024"
            responses:
              202:
                description: Análise iniciada com sucesso
                schema:
                  type: object
                  properties:
                    analise_id:
                      type: string
                    status:
                      type: string
                    links:
                      type: object
              400:
                description: Dados inválidos
              401:
                description: Não autenticado
            """
            data = request.get_json(silent=True)
            if not data or not data.get('topico_pesquisa'):
                return jsonify({'error': 'Campo topico_pesquisa é obrigatório'}), 400

            topico_pesquisa = str(data['topico_pesquisa']).strip()
            analise_id = str(uuid.uuid4())
            analise_info = {
                'id': analise_id,
                'usuario_id': current_user.id,
                'topico_pesquisa': topico_pesquisa,
                'status': 'processando',
                'arquivos': [],
                'timestamp_inicio': datetime.now().isoformat(),
                'progresso': 0
            }
            self.analises_ativas[analise_id] = analise_info
            self._salvar_analise(analise_id)
            self._executar_analise(analise_id)

            return jsonify({
                'analise_id': analise_id,
                'status': 'processando',
                'links': {
                    'status': f'/api/v1/analises/{analise_id}',
                    'resultados': f'/api/v1/analises/{analise_id}/resultados',
                    'stream': f'/stream/{analise_id}'
                }
            }), 202

        @app.route('/api/v1/analises/<analise_id>', methods=['GET'])
        @login_required
        def api_status_analise(analise_id):
            """Retorna status detalhado de uma análise.
            ---
            tags:
              - Análises
            parameters:
              - name: analise_id
                in: path
                type: string
                required: true
            responses:
              200:
                description: Dados da análise
              403:
                description: Sem permissão
              404:
                description: Análise não encontrada
            """
            info = self._buscar_analise(analise_id)
            if not info:
                return jsonify({'error': 'Análise não encontrada'}), 404
            if info.get('usuario_id') != current_user.id and not current_user.admin:
                return jsonify({'error': 'Sem permissão'}), 403
            return jsonify(info)

        @app.route('/api/v1/analises/<analise_id>/resultados', methods=['GET'])
        @login_required
        def api_resultados_analise(analise_id):
            """Retorna resultados completos de uma análise concluída.
            ---
            tags:
              - Análises
            parameters:
              - name: analise_id
                in: path
                type: string
                required: true
            responses:
              200:
                description: Resultados da análise
                schema:
                  type: object
                  properties:
                    analise_id:
                      type: string
                    topico_pesquisa:
                      type: string
                    resultados:
                      type: string
                    concluido_em:
                      type: string
              403:
                description: Sem permissão
              404:
                description: Análise não encontrada
              409:
                description: Análise ainda não concluída
            """
            info = self._buscar_analise(analise_id)
            if not info:
                return jsonify({'error': 'Análise não encontrada'}), 404
            if info.get('usuario_id') != current_user.id and not current_user.admin:
                return jsonify({'error': 'Sem permissão'}), 403
            if info.get('status') != 'concluida':
                return jsonify({
                    'error': 'Análise não concluída',
                    'status': info.get('status'),
                    'progresso': info.get('progresso')
                }), 409
            return jsonify({
                'analise_id': analise_id,
                'topico_pesquisa': info.get('topico_pesquisa'),
                'resultados': info.get('resultados'),
                'concluido_em': info.get('concluido_em') or info.get('timestamp_fim')
            })

    # ------------------------------------------------------------------
    # Helpers de validação
    # ------------------------------------------------------------------

    def _validar_url(self, url: str) -> tuple[bool, str]:
        """Valida URL para evitar SSRF. Retorna (valido, motivo)."""
        try:
            parsed = urlparse(url)

            # Apenas http e https são permitidos
            if parsed.scheme not in ('http', 'https'):
                return False, f"Esquema não permitido: '{parsed.scheme}'. Use http ou https."

            hostname = parsed.hostname
            if not hostname:
                return False, "URL sem hostname válido."

            # Bloquear hostnames internos/reservados
            blocked_hostnames = {
                'localhost', 'localhost.localdomain',
            }
            if hostname.lower() in blocked_hostnames:
                return False, "Acesso a endereços internos não é permitido."

            # Bloquear IPs privados/reservados
            try:
                addr = ipaddress.ip_address(hostname)
                if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
                    return False, "Acesso a endereços IP internos não é permitido."
            except ValueError:
                # hostname é um nome de domínio, não IP — ok
                pass

            # Bloquear metadata de cloud (AWS, GCP, Azure)
            blocked_prefixes = ('169.254.', '100.64.')
            if any(hostname.startswith(p) for p in blocked_prefixes):
                return False, "Acesso a endereços de metadata de cloud não é permitido."

            return True, "URL válida."

        except Exception as e:
            return False, f"URL inválida: {str(e)}"

    def _allowed_file(self, filename):
        """Verifica se extensão é permitida"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.upload_config['ALLOWED_EXTENSIONS']

    # ------------------------------------------------------------------
    # Processamento de análises
    # ------------------------------------------------------------------

    def _processar_analise(self, app):
        """Processa solicitação de análise"""
        try:
            # Obtém dados do formulário
            topico_pesquisa = request.form.get('topico_pesquisa', '').strip()
            links_sites = request.form.get('links_sites', '').strip()

            # Validação básica - apenas tópico é obrigatório
            if not topico_pesquisa:
                flash('Por favor, descreva o tópico de pesquisa.', 'error')
                return redirect(url_for('analise'))

            # Cria ID único para análise
            analise_id = str(uuid.uuid4())
            analise_info = {
                'id': analise_id,
                'usuario_id': current_user.id if current_user.is_authenticated else 'sistema',
                'topico_pesquisa': topico_pesquisa,
                'status': 'processando',
                'arquivos': [],
                'timestamp_inicio': datetime.now().isoformat(),
                'progresso': 0
            }

            # Processa links de sites (opcional)
            arquivos_processados = []
            if links_sites:
                for link in links_sites.split('\n'):
                    link = link.strip()
                    if link:
                        url_valida, motivo = self._validar_url(link)
                        if not url_valida:
                            flash(f'Link rejeitado ({motivo}): {link}', 'warning')
                            continue
                        try:
                            response = requests.get(link, timeout=10)
                            if response.status_code == 200:
                                # Determina extensão baseada no link
                                _, ext = os.path.splitext(link)
                                if not ext:
                                    ext = '.txt'

                                with tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir=app.config['UPLOAD_FOLDER']) as temp_file:
                                    temp_file.write(response.content)
                                    temp_filename = temp_file.name

                                # Valida segurança do arquivo
                                validacao = self.security_validator.validar_arquivo(temp_filename)

                                if validacao['valido']:
                                    arquivos_processados.append({
                                        'nome_original': link,
                                        'nome_arquivo': os.path.basename(temp_filename),
                                        'caminho': temp_filename,
                                        'tamanho': len(response.content),
                                        'validacao_seguranca': validacao
                                    })
                                else:
                                    # Remove arquivo inválido
                                    os.remove(temp_filename)
                                    flash(f'Link {link} rejeitado: {validacao["erros"][0]}', 'warning')
                            else:
                                flash(f'Falha ao baixar {link}: Status {response.status_code}', 'warning')
                        except Exception as e:
                            flash(f'Erro ao baixar {link}: {str(e)}', 'warning')

            # Processa arquivos enviados (opcional)
            arquivos_locais = request.files.getlist('arquivos')
            for arquivo in arquivos_locais:
                if arquivo and arquivo.filename and self._allowed_file(arquivo.filename):
                    filename = secure_filename(arquivo.filename)

                    # Gera nome único para arquivo
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

                    # Salva arquivo
                    arquivo.save(file_path)

                    # Valida segurança do arquivo
                    validacao = self.security_validator.validar_arquivo(file_path)

                    if validacao['valido']:
                        arquivos_processados.append({
                            'nome_original': arquivo.filename,
                            'nome_arquivo': unique_filename,
                            'caminho': file_path,
                            'tamanho': os.path.getsize(file_path),
                            'validacao_seguranca': validacao
                        })
                    else:
                        # Remove arquivo inválido
                        os.remove(file_path)
                        flash(f'Arquivo {arquivo.filename} rejeitado: {validacao["erros"][0]}', 'warning')

            # Registra análise na auditoria
            self.auditor.iniciar_analise(topico_pesquisa, {
                'arquivos_count': len(arquivos_processados),
                'analise_id': analise_id
            })

            # Atualiza informações da análise
            analise_info['arquivos'] = arquivos_processados
            analise_info['status'] = 'arquivos_validados'
            analise_info['progresso'] = 25
            self.analises_ativas[analise_id] = analise_info
            self._salvar_analise(analise_id)

            # Simula processamento (em produção, isso seria assíncrono)
            self._executar_analise(analise_id)

            flash(f'Análise iniciada com ID: {analise_id}', 'success')
            return redirect(url_for('resultados_analise', analise_id=analise_id))

        except Exception as e:
            self.auditor.registrar_erro(e, 'processar_analise')
            flash(f'Erro ao processar análise: {str(e)}', 'error')
            return redirect(url_for('analise'))

    def _handle_upload(self, app):
        """Manipula upload de arquivos via AJAX"""
        try:
            if 'arquivo' not in request.files:
                return jsonify({'error': 'Nenhum arquivo enviado'}), 400

            arquivo = request.files['arquivo']

            if arquivo.filename == '':
                return jsonify({'error': 'Nome de arquivo vazio'}), 400

            if not self._allowed_file(arquivo.filename):
                return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

            # Salva arquivo temporário
            filename = secure_filename(arquivo.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            arquivo.save(file_path)

            # Valida segurança
            validacao = self.security_validator.validar_arquivo(file_path)

            if validacao['valido']:
                return jsonify({
                    'success': True,
                    'filename': unique_filename,
                    'original_name': arquivo.filename,
                    'size': os.path.getsize(file_path),
                    'validacao': validacao
                })
            else:
                # Remove arquivo inválido
                os.remove(file_path)
                return jsonify({'error': f'Arquivo rejeitado: {validacao["erros"][0]}'}), 400

        except Exception as e:
            return jsonify({'error': f'Erro no upload: {str(e)}'}), 500

    # ------------------------------------------------------------------
    # Execução de análise (CrewAI)
    # ------------------------------------------------------------------

    def _executar_analise(self, analise_id: str):
        """Executa análise usando CrewAI"""
        import threading

        def _atualizar_status(updates: dict):
            if analise_id in self.analises_ativas:
                self.analises_ativas[analise_id].update(updates)
                self._salvar_analise(analise_id)

        def analise_worker():
            try:
                # Atualiza status inicial
                _atualizar_status({
                    'status': 'executando_analise',
                    'progresso': 25,
                    'timestamp_atualizacao': datetime.now().isoformat()
                })

                # Obtém dados da análise
                analise_info = self.analises_ativas.get(analise_id, {})
                topico_pesquisa = analise_info.get('topico_pesquisa', '')

                # Prepara caminhos dos arquivos para o crew
                arquivos_paths = [a['caminho'] for a in analise_info.get('arquivos', [])]

                # Atualiza progresso
                _atualizar_status({
                    'status': 'processando_dados',
                    'progresso': 50,
                    'timestamp_atualizacao': datetime.now().isoformat()
                })

                # Executa análise com CrewAI
                try:
                    from ..crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
                except ImportError:
                    # Fallback: adiciona 'src' ao path para import absoluto
                    import sys
                    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew

                crew_instance = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
                crew = crew_instance.crew()

                # Prepara inputs para o crew
                inputs = {
                    'topico_pesquisa': topico_pesquisa,
                    'arquivos_analisados': arquivos_paths
                }

                # Executa análise com timeout configurável
                import concurrent.futures
                crew_timeout = int(os.getenv('SAPIENS_CREW_TIMEOUT', str(2 * 60 * 60)))  # 2h padrão
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(crew.kickoff, inputs=inputs)
                    try:
                        resultados = future.result(timeout=crew_timeout)
                    except concurrent.futures.TimeoutError:
                        future.cancel()
                        raise TimeoutError(
                            f"Análise excedeu o tempo limite de {crew_timeout}s. "
                            "Ajuste SAPIENS_CREW_TIMEOUT se necessário."
                        )

                # Atualiza progresso final
                _atualizar_status({
                    'status': 'gerando_relatorio',
                    'progresso': 90,
                    'resultados': str(resultados),
                    'timestamp_atualizacao': datetime.now().isoformat()
                })

                # Finaliza análise
                _atualizar_status({
                    'status': 'concluida',
                    'progresso': 100,
                    'timestamp_fim': datetime.now().isoformat()
                })

                # Registra finalização na auditoria
                self.auditor.finalizar_analise(True, {
                    'analise_id': analise_id,
                    'progresso_final': 100,
                    'resultados_crew': str(resultados)
                })

                # Remove arquivos de upload após análise concluída
                self._limpar_arquivos_analise(analise_id)

            except Exception as e:
                # Registra erro
                self.auditor.registrar_erro(e, f'analise_{analise_id}')

                # Atualiza status para erro
                _atualizar_status({
                    'status': 'erro',
                    'erro': str(e),
                    'timestamp_atualizacao': datetime.now().isoformat()
                })

                # Remove arquivos mesmo em caso de erro
                self._limpar_arquivos_analise(analise_id)

        # Executa em background
        thread = threading.Thread(target=analise_worker)
        thread.daemon = True
        thread.start()

    # ------------------------------------------------------------------
    # SSE (Server-Sent Events)
    # ------------------------------------------------------------------

    def _event_generator(self, analise_id):
        """Gera eventos SSE para acompanhamento de progresso em tempo real."""
        import time
        ultimo_progresso = -1
        while True:
            info = self._buscar_analise(analise_id)
            if not info:
                yield "data: {\"erro\": \"Análise não encontrada\"}\n\n"
                break

            progresso = info.get('progresso', 0)
            status = info.get('status', '')

            if progresso != ultimo_progresso:
                payload = json.dumps({
                    'progresso': progresso,
                    'status': status,
                    'timestamp': datetime.now().isoformat()
                }, ensure_ascii=False)
                yield f"data: {payload}\n\n"
                ultimo_progresso = progresso

            if status in ('concluida', 'erro'):
                break

            time.sleep(1)

    # ------------------------------------------------------------------
    # Limpeza de arquivos
    # ------------------------------------------------------------------

    def _limpar_arquivos_analise(self, analise_id: str):
        """Remove arquivos de upload de uma análise específica e libera cache."""
        analise_info = self.analises_ativas.get(analise_id, {})
        for arquivo in analise_info.get('arquivos', []):
            caminho = arquivo.get('caminho', '')
            if caminho and os.path.exists(caminho):
                try:
                    os.remove(caminho)
                except Exception as e:
                    logger.warning("Nao foi possivel remover arquivo %s: %s", caminho, e)
        # Remove entrada do cache para evitar vazamento de memória
        self.analises_ativas.pop(analise_id, None)

    def _limpar_uploads_orfaos(self, max_idade_horas: int = 24):
        """Remove arquivos de upload sem análise associada com mais de max_idade_horas."""
        import time
        pasta = self.upload_config['UPLOAD_FOLDER']
        if not os.path.isdir(pasta):
            return
        agora = time.time()
        limite = max_idade_horas * 3600
        arquivos_ativos = {
            arquivo.get('caminho', '')
            for analise in self.analises_ativas.values()
            for arquivo in analise.get('arquivos', [])
        }
        for nome in os.listdir(pasta):
            caminho = os.path.join(pasta, nome)
            if caminho in arquivos_ativos:
                continue
            try:
                if os.path.isfile(caminho) and (agora - os.path.getmtime(caminho)) > limite:
                    os.remove(caminho)
            except Exception as e:
                logger.warning("Nao foi possivel remover upload orfao %s: %s", caminho, e)

    # ------------------------------------------------------------------
    # Status e resultados
    # ------------------------------------------------------------------

    def _get_analise_status(self, analise_id):
        """Retorna status da análise (cache ou banco)."""
        analise_info = self._buscar_analise(analise_id)
        if not analise_info:
            return jsonify({'error': 'Análise não encontrada'}), 404
        return jsonify(analise_info)

    def _get_analise_resultados(self, analise_id):
        """Retorna página de resultados (cache ou banco)."""
        analise_info = self._buscar_analise(analise_id)
        if not analise_info:
            flash('Análise não encontrada', 'error')
            return redirect(url_for('index'))

        if analise_info['status'] == 'concluida':
            return render_template('resultados.html', analise=analise_info)
        elif analise_info['status'] == 'erro':
            flash(f"A análise falhou: {analise_info.get('erro') or 'erro desconhecido'}", 'error')
            return redirect(url_for('historico'))
        else:
            return render_template('progresso.html', analise=analise_info)

    def _get_historico(self, usuario_id: str = None):
        """Retorna página com análises do usuário atual (ou todas se admin)."""
        try:
            with _get_db() as conn:
                if current_user.admin:
                    rows = conn.execute(
                        "SELECT * FROM analises ORDER BY criado_em DESC LIMIT 100"
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM analises WHERE usuario_id = ? ORDER BY criado_em DESC LIMIT 100",
                        (usuario_id,)
                    ).fetchall()
            # Filtra registros de testes automatizados (IDs com prefixo de fixture)
            analises = [
                self._row_para_dict(r) for r in rows
                if not str(r['id']).startswith('teste-')
            ]
        except Exception:
            analises = []
        return render_template('historico.html', analises=analises)

    # ------------------------------------------------------------------
    # Exportação de resultados
    # ------------------------------------------------------------------

    def _exportar_analise(self, analise_id: str, formato: str):
        """Exporta resultados da análise em PDF ou TXT."""
        from flask import make_response

        analise_info = self._buscar_analise(analise_id)
        if not analise_info or analise_info.get('status') != 'concluida':
            return jsonify({'error': 'Análise não encontrada ou não concluída'}), 404

        topico = analise_info.get('topico_pesquisa', 'Análise SAPIENS')
        resultados = analise_info.get('resultados', 'Sem resultados disponíveis.')
        timestamp = analise_info.get('timestamp_fim', datetime.now().isoformat())

        if formato == 'txt':
            conteudo = (
                f"SAPIENS - Relatório de Análise\n"
                f"{'=' * 60}\n"
                f"Tópico: {topico}\n"
                f"ID: {analise_id}\n"
                f"Concluído em: {timestamp}\n"
                f"{'=' * 60}\n\n"
                f"{resultados}\n"
            )
            response = make_response(conteudo)
            response.headers['Content-Type'] = 'text/plain; charset=utf-8'
            response.headers['Content-Disposition'] = (
                f'attachment; filename="sapiens_{analise_id[:8]}.txt"'
            )
            return response

        elif formato == 'pdf':
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import cm
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib import colors
                import io

                buf = io.BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=A4,
                                        leftMargin=2*cm, rightMargin=2*cm,
                                        topMargin=2*cm, bottomMargin=2*cm)
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle(
                    'SapiensTitle', parent=styles['Heading1'],
                    fontSize=16, textColor=colors.HexColor('#1a3a5c'), spaceAfter=12
                )
                body_style = ParagraphStyle(
                    'SapiensBody', parent=styles['Normal'],
                    fontSize=10, leading=14, spaceAfter=6
                )

                story = [
                    Paragraph("SAPIENS — Relatório de Análise", title_style),
                    Paragraph(f"<b>Tópico:</b> {topico}", body_style),
                    Paragraph(f"<b>ID:</b> {analise_id}", body_style),
                    Paragraph(f"<b>Concluído em:</b> {timestamp}", body_style),
                    Spacer(1, 0.5*cm),
                    Paragraph("<b>Resultados</b>", styles['Heading2']),
                    Spacer(1, 0.3*cm),
                ]

                # Quebra o texto em parágrafos para o PDF
                for linha in resultados.split('\n'):
                    texto = linha.strip()
                    if texto:
                        story.append(Paragraph(texto.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), body_style))
                    else:
                        story.append(Spacer(1, 0.2*cm))

                doc.build(story)
                buf.seek(0)

                response = make_response(buf.read())
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = (
                    f'attachment; filename="sapiens_{analise_id[:8]}.pdf"'
                )
                return response

            except ImportError:
                return jsonify({'error': 'reportlab não instalado. Execute: pip install reportlab'}), 500
            except Exception as e:
                return jsonify({'error': f'Erro ao gerar PDF: {str(e)}'}), 500

        else:
            return jsonify({'error': f"Formato '{formato}' não suportado. Use 'pdf' ou 'txt'."}), 400

    # ------------------------------------------------------------------
    # Inicialização e estatísticas
    # ------------------------------------------------------------------

    def run(self):
        """Executa interface web"""
        app = self.create_app()

        print(f"Iniciando SAPIENS Web Interface em http://{self.host}:{self.port}")
        print(f"Diretorio de uploads: {self.upload_config['UPLOAD_FOLDER']}")

        self.auditor.auditar_evento('inicializacao_interface_web', dados_entrada={
            'host': self.host,
            'port': self.port
        })

        app.run(host=self.host, port=self.port, debug=self.debug)

    def get_estatisticas(self):
        """Retorna estatísticas da interface"""
        return {
            'analises_ativas': len(self.analises_ativas),
            'arquivos_upload_total': sum(len(a['arquivos']) for a in self.analises_ativas.values()),
            'ultima_atividade': max((a.get('timestamp_inicio', '')) for a in self.analises_ativas.values()) if self.analises_ativas else None
        }


# Aplicação standalone
def create_web_interface():
    """Cria instância da interface web"""
    return SapiensWebInterface()


if __name__ == '__main__':
    interface = create_web_interface()
    interface.run()
