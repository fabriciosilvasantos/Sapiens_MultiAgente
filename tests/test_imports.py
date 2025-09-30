"""
Testes básicos de import para SAPIENS
"""

import pytest
import sys
import os

# Adicionar src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_import_sapiens():
    """Testa se o pacote principal pode ser importado"""
    try:
        import Sapiens_MultiAgente
        assert Sapiens_MultiAgente.__version__ == "2.0.0"
        assert hasattr(Sapiens_MultiAgente, 'SapiensAcademicMultiAgentDataAnalysisPlatformCrew')
    except ImportError as e:
        pytest.fail(f"Falha ao importar Sapiens_MultiAgente: {e}")


def test_import_crew():
    """Testa se o módulo crew pode ser importado"""
    try:
        from Sapiens_MultiAgente.crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew
        assert SapiensAcademicMultiAgentDataAnalysisPlatformCrew is not None
    except ImportError as e:
        pytest.fail(f"Falha ao importar crew: {e}")


def test_import_tools():
    """Testa se as ferramentas podem ser importadas"""
    tools_to_test = [
        'DataValidationTool',
        'CSVProcessorTool',
        'StatisticalAnalysisTool',
        'PDFSearchTool',
        'DOCXSearchTool',
        'CSVSearchTool'
    ]

    for tool_name in tools_to_test:
        try:
            module = __import__(f'Sapiens_MultiAgente.tools.{tool_name.lower()}_tool',
                              fromlist=[tool_name])
            tool_class = getattr(module, tool_name)
            assert tool_class is not None
        except (ImportError, AttributeError) as e:
            pytest.fail(f"Falha ao importar {tool_name}: {e}")


def test_import_web():
    """Testa se o módulo web pode ser importado"""
    try:
        from Sapiens_MultiAgente.web.app import SapiensWebInterface
        assert SapiensWebInterface is not None
    except ImportError as e:
        pytest.fail(f"Falha ao importar web interface: {e}")


def test_config_files_exist():
    """Testa se os arquivos de configuração existem"""
    config_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'Sapiens_MultiAgente', 'config')

    required_files = [
        'agents.yaml',
        'tasks.yaml',
        'logging_config.yaml'
    ]

    for config_file in required_files:
        file_path = os.path.join(config_dir, config_file)
        assert os.path.exists(file_path), f"Arquivo de configuração faltando: {config_file}"


def test_template_files_exist():
    """Testa se os templates HTML existem"""
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'Sapiens_MultiAgente', 'web', 'templates')

    required_templates = [
        'base.html',
        'index.html',
        'analise.html',
        'sobre.html',
        'progresso.html',
        'resultados.html'
    ]

    for template_file in required_templates:
        file_path = os.path.join(template_dir, template_file)
        assert os.path.exists(file_path), f"Template HTML faltando: {template_file}"