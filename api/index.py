import os
import sys
from pathlib import Path

# Adiciona o diretório src ao path para importar módulos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import json
import uuid
import tempfile
import requests
from datetime import datetime

# Importações do sistema SAPIENS
try:
    from Sapiens_MultiAgente.tools.academic_logger import get_auditor
    from Sapiens_MultiAgente.tools.security_validator import AcademicSecurityValidator
except ImportError:
    # Fallback para import direto
    sys.path.insert(0, str(project_root))
    from tools.academic_logger import get_auditor
    from tools.security_validator import AcademicSecurityValidator

# Configuração para Vercel
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Configurações de upload
UPLOAD_FOLDER = '/tmp/uploads'  # Usar /tmp no Vercel
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'pdf', 'docx', 'txt'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Cria diretório de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Inicializa componentes
auditor = get_auditor()
security_validator = AcademicSecurityValidator()

# Estado das análises (em produção, usar Redis ou banco)
analises_ativas = {}

def allowed_file(filename):
    """Verifica se extensão é permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        return processar_analise()
    return render_template('analise.html')

@app.route('/upload', methods=['POST'])
def upload_arquivo():
    """Endpoint para upload de arquivos"""
    try:
        if 'arquivo' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        arquivo = request.files['arquivo']

        if arquivo.filename == '':
            return jsonify({'error': 'Nome de arquivo vazio'}), 400

        if not allowed_file(arquivo.filename):
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

        # Salva arquivo temporário
        filename = secure_filename(arquivo.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        arquivo.save(file_path)

        # Valida segurança
        validacao = security_validator.validar_arquivo(file_path)

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

@app.route('/api/analisar', methods=['POST'])
def api_analisar():
    """API endpoint para análise (serverless)"""
    try:
        data = request.get_json()
        topico_pesquisa = data.get('topico_pesquisa', '').strip()

        if not topico_pesquisa:
            return jsonify({'error': 'Tópico de pesquisa obrigatório'}), 400

        # Cria ID único para análise
        analise_id = str(uuid.uuid4())
        analise_info = {
            'id': analise_id,
            'topico_pesquisa': topico_pesquisa,
            'status': 'processando',
            'timestamp_inicio': datetime.now().isoformat(),
            'progresso': 0
        }

        # Registra análise na auditoria
        auditor.iniciar_analise(topico_pesquisa, {
            'analise_id': analise_id
        })

        analises_ativas[analise_id] = analise_info

        # Processa análise síncrona (simplificada para serverless)
        try:
            from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew

            crew_instance = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
            crew = crew_instance.crew()

            # Prepara inputs
            inputs = {
                'topico_pesquisa': topico_pesquisa,
                'arquivos_analisados': []
            }

            # Executa análise
            resultados = crew.kickoff(inputs=inputs)

            # Atualiza análise como concluída
            analise_info.update({
                'status': 'concluida',
                'progresso': 100,
                'resultados': str(resultados),
                'timestamp_fim': datetime.now().isoformat()
            })

            # Registra finalização
            auditor.finalizar_analise(True, {
                'analise_id': analise_id,
                'resultados_crew': str(resultados)
            })

            return jsonify({
                'success': True,
                'analise_id': analise_id,
                'status': 'concluida',
                'resultados': str(resultados)
            })

        except Exception as e:
            # Atualiza análise como erro
            analise_info.update({
                'status': 'erro',
                'erro': str(e),
                'timestamp_atualizacao': datetime.now().isoformat()
            })

            auditor.registrar_erro(e, f'analise_{analise_id}')

            return jsonify({'error': f'Erro na análise: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': f'Erro geral: {str(e)}'}), 500

@app.route('/status/<analise_id>')
def status_analise(analise_id):
    """Verifica status de análise"""
    if analise_id not in analises_ativas:
        return jsonify({'error': 'Análise não encontrada'}), 404

    return jsonify(analises_ativas[analise_id])

@app.route('/resultados/<analise_id>')
def resultados_analise(analise_id):
    """Exibe resultados da análise"""
    if analise_id not in analises_ativas:
        flash('Análise não encontrada', 'error')
        return redirect(url_for('index'))

    analise_info = analises_ativas[analise_id]

    if analise_info['status'] == 'concluida':
        return render_template('resultados.html', analise=analise_info)
    else:
        return render_template('progresso.html', analise=analise_info)

@app.route('/api/health')
def health_check():
    """Health check para monitoramento"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'sistema': 'SAPIENS Web Interface - Vercel',
        'versao': '2.0.0'
    })

def processar_analise():
    """Processa solicitação de análise"""
    try:
        # Obtém dados do formulário
        topico_pesquisa = request.form.get('topico_pesquisa', '').strip()

        if not topico_pesquisa:
            flash('Por favor, descreva o tópico de pesquisa.', 'error')
            return redirect(url_for('analise'))

        # Cria ID único para análise
        analise_id = str(uuid.uuid4())
        analise_info = {
            'id': analise_id,
            'topico_pesquisa': topico_pesquisa,
            'status': 'processando',
            'timestamp_inicio': datetime.now().isoformat(),
            'progresso': 0
        }

        analises_ativas[analise_id] = analise_info

        # Simula processamento (em produção seria síncrono)
        try:
            from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew

            crew_instance = SapiensAcademicMultiAgentDataAnalysisPlatformCrew()
            crew = crew_instance.crew()

            inputs = {
                'topico_pesquisa': topico_pesquisa,
                'arquivos_analisados': []
            }

            resultados = crew.kickoff(inputs=inputs)

            # Atualiza análise como concluída
            analise_info.update({
                'status': 'concluida',
                'progresso': 100,
                'resultados': str(resultados),
                'timestamp_fim': datetime.now().isoformat()
            })

            flash(f'Análise iniciada com ID: {analise_id}', 'success')
            return redirect(url_for('resultados_analise', analise_id=analise_id))

        except Exception as e:
            analise_info.update({
                'status': 'erro',
                'erro': str(e)
            })

            auditor.registrar_erro(e, f'analise_{analise_id}')
            flash(f'Erro ao processar análise: {str(e)}', 'error')
            return redirect(url_for('analise'))

    except Exception as e:
        auditor.registrar_erro(e, 'processar_analise')
        flash(f'Erro ao processar análise: {str(e)}', 'error')
        return redirect(url_for('analise'))

# Configuração específica para Vercel
if __name__ == '__main__':
    # Apenas para desenvolvimento local
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

# Para Vercel serverless
app = app
