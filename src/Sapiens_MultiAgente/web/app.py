from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import json
import uuid
import tempfile
import requests
from datetime import datetime
from pathlib import Path

# Importações do sistema SAPIENS
try:
    from ..tools.academic_logger import get_auditor
    from ..tools.security_validator import AcademicSecurityValidator
except ImportError:
    # Fallback para import direto
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from tools.academic_logger import get_auditor
    from tools.security_validator import AcademicSecurityValidator


class SapiensWebInterface:
    """Interface web básica para SAPIENS"""

    def __init__(self, host='127.0.0.1', port=5000, debug=False):
        self.host = host
        self.port = port
        self.debug = debug

        # Configurações de upload
        self.upload_config = {
            'UPLOAD_FOLDER': 'uploads',
            'MAX_CONTENT_LENGTH': 100 * 1024 * 1024,  # 100MB
            'ALLOWED_EXTENSIONS': {'csv', 'xlsx', 'xls', 'pdf', 'docx', 'txt'}
        }

        # Cria diretório de uploads
        os.makedirs(self.upload_config['UPLOAD_FOLDER'], exist_ok=True)

        # Inicializa componentes
        self.auditor = get_auditor()
        self.security_validator = AcademicSecurityValidator()

        # Estado das análises
        self.analises_ativas = {}

    def create_app(self):
        """Cria aplicação Flask"""
        app = Flask(__name__)
        app.config['UPLOAD_FOLDER'] = self.upload_config['UPLOAD_FOLDER']
        app.config['MAX_CONTENT_LENGTH'] = self.upload_config['MAX_CONTENT_LENGTH']

        # Carrega secret key de variável de ambiente
        app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

        # Rotas principais
        @app.route('/')
        def index():
            """Página inicial"""
            return render_template('index.html')

        @app.route('/sobre')
        def sobre():
            """Página sobre o SAPIENS"""
            return render_template('sobre.html')

        @app.route('/analise', methods=['GET', 'POST'])
        def analise():
            """Página de análise de dados"""
            if request.method == 'POST':
                return self._processar_analise(app)
            return render_template('analise.html')

        @app.route('/upload', methods=['POST'])
        def upload_arquivo():
            """Endpoint para upload de arquivos"""
            return self._handle_upload(app)

        @app.route('/status/<analise_id>')
        def status_analise(analise_id):
            """Verifica status de análise"""
            return self._get_analise_status(analise_id)

        @app.route('/resultados/<analise_id>')
        def resultados_analise(analise_id):
            """Exibe resultados da análise"""
            return self._get_analise_resultados(analise_id)

        @app.route('/api/health')
        def health_check():
            """Health check para monitoramento"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'sistema': 'SAPIENS Web Interface',
                'versao': '2.0.0'
            })

        return app

    def run(self, host='127.0.0.1', port=5000, debug=False):
        """Executa a aplicação Flask"""
        app = self.create_app()
        app.run(host=host, port=port, debug=debug)

    def _allowed_file(self, filename):
        """Verifica se extensão é permitida"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.upload_config['ALLOWED_EXTENSIONS']

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

            # Combina arquivos locais e de links
            todos_arquivos = arquivos_processados

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

    def _executar_analise(self, analise_id: str):
        """Executa análise usando CrewAI"""
        import threading
        from crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew

        def analise_worker():
            try:
                # Atualiza status inicial
                if analise_id in self.analises_ativas:
                    self.analises_ativas[analise_id].update({
                        'status': 'executando_analise',
                        'progresso': 25,
                        'timestamp_atualizacao': datetime.now().isoformat()
                    })

                # Obtém dados da análise
                analise_info = self.analises_ativas.get(analise_id, {})
                topico_pesquisa = analise_info.get('topico_pesquisa', '')

                # Prepara caminhos dos arquivos para o crew
                arquivos_paths = []
                if 'arquivos' in analise_info:
                    for arquivo in analise_info['arquivos']:
                        arquivos_paths.append(arquivo['caminho'])

                # Atualiza progresso
                if analise_id in self.analises_ativas:
                    self.analises_ativas[analise_id].update({
                        'status': 'processando_dados',
                        'progresso': 50,
                        'timestamp_atualizacao': datetime.now().isoformat()
                    })

                # Executa análise com CrewAI
                try:
                    from ..crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
                except ImportError:
                    # Fallback para import direto
                    import sys
                    import os
                    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
                    from crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        
                crew_instance = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
                crew = crew_instance.crew()

                # Prepara inputs para o crew
                inputs = {
                    'topico_pesquisa': topico_pesquisa,
                    'arquivos_analisados': arquivos_paths
                }

                # Executa análise
                resultados = crew.kickoff(inputs=inputs)

                # Atualiza progresso final
                if analise_id in self.analises_ativas:
                    self.analises_ativas[analise_id].update({
                        'status': 'gerando_relatorio',
                        'progresso': 90,
                        'resultados': str(resultados),  # Armazena resultados
                        'timestamp_atualizacao': datetime.now().isoformat()
                    })

                # Simula tempo de geração de relatório
                import time
                time.sleep(2)

                # Finaliza análise
                if analise_id in self.analises_ativas:
                    self.analises_ativas[analise_id].update({
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

            except Exception as e:
                # Registra erro
                self.auditor.registrar_erro(e, f'analise_{analise_id}')

                # Atualiza status para erro
                if analise_id in self.analises_ativas:
                    self.analises_ativas[analise_id].update({
                        'status': 'erro',
                        'erro': str(e),
                        'timestamp_atualizacao': datetime.now().isoformat()
                    })

        # Executa em background
        thread = threading.Thread(target=analise_worker)
        thread.daemon = True
        thread.start()

    def _get_analise_status(self, analise_id):
        """Retorna status da análise"""
        if analise_id not in self.analises_ativas:
            return jsonify({'error': 'Análise não encontrada'}), 404

        return jsonify(self.analises_ativas[analise_id])

    def _get_analise_resultados(self, analise_id):
        """Retorna página de resultados"""
        if analise_id not in self.analises_ativas:
            flash('Análise não encontrada', 'error')
            return redirect(url_for('index'))

        analise_info = self.analises_ativas[analise_id]

        if analise_info['status'] == 'concluida':
            # Em produção, aqui seriam exibidos os resultados reais
            return render_template('resultados.html', analise=analise_info)
        else:
            # Mostra página de progresso
            return render_template('progresso.html', analise=analise_info)

    def run(self):
        """Executa interface web"""
        app = self.create_app()

        print("🚀 Iniciando SAPIENS Web Interface...")
        print(f"📡 Servidor: http://{self.host}:{self.port}")
        print(f"📁 Diretório de uploads: {self.upload_config['UPLOAD_FOLDER']}")

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