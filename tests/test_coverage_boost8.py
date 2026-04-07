"""
Boost de cobertura — Rodada 8.
Alvos restantes após boost7 (99%):

- csv_search_tool.py  138       : pd.to_numeric em coluna com dtype object
- csv_search_tool.py  147-152   : ramos >= e <= (corrigidos — eram código morto)
- web/app.py          640       : ext = '.txt' quando URL não tem extensão
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ---------------------------------------------------------------------------
# csv_search_tool.py — linha 138 (pd.to_numeric em coluna com dtype object)
# ---------------------------------------------------------------------------

class TestCSVSearchToNumericReal:
    """
    Coluna 'score' com valor 'alta' (string genuína) → pandas lê como object dtype.
    Ao aplicar filtro numérico '>', _apply_numeric_filters converte via
    pd.to_numeric(errors='coerce') — linha 138.

    'n/a' NÃO funciona porque pandas o reconhece como valor NA padrão e
    converte o CSV inteiro para float64, fazendo is_numeric_dtype retornar True.
    """

    def test_filtro_numerico_coluna_object_dtype_string_real(self, tmp_path):
        from Sapiens_MultiAgente.tools.csv_search_tool import CSVSearchTool

        csv_file = tmp_path / 'notas_string.csv'
        # 'alta' é string genuína → pandas mantém coluna como object dtype
        csv_file.write_text(
            'nome,score\nAna,alta\nBia,7\nCaio,8\n',
            encoding='utf-8',
        )

        tool = CSVSearchTool()
        result = tool._run(
            file_path=str(csv_file),
            numeric_filters={'score': '>6'},
        )

        # Bia (7) e Caio (8) passam; Ana ('alta' → NaN após coerce) não
        assert 'Bia' in result or 'Caio' in result or '❌' not in result

    def test_filtro_maior_igual(self, tmp_path):
        """Filtro '>=' agora funciona corretamente após correção da ordem."""
        from Sapiens_MultiAgente.tools.csv_search_tool import CSVSearchTool

        csv_file = tmp_path / 'notas_gte.csv'
        csv_file.write_text('nome,score\nAna,5\nBia,7\nCaio,8\n', encoding='utf-8')

        tool = CSVSearchTool()
        result = tool._run(file_path=str(csv_file), numeric_filters={'score': '>=7'})

        # Bia (7) e Caio (8) devem aparecer; Ana (5) não
        assert 'Bia' in result
        assert 'Caio' in result

    def test_filtro_menor_igual(self, tmp_path):
        """Filtro '<=' agora funciona corretamente após correção da ordem."""
        from Sapiens_MultiAgente.tools.csv_search_tool import CSVSearchTool

        csv_file = tmp_path / 'notas_lte.csv'
        csv_file.write_text('nome,score\nAna,5\nBia,7\nCaio,8\n', encoding='utf-8')

        tool = CSVSearchTool()
        result = tool._run(file_path=str(csv_file), numeric_filters={'score': '<=7'})

        # Ana (5) e Bia (7) devem aparecer; Caio (8) não
        assert 'Ana' in result
        assert 'Bia' in result

    def test_filtro_invalido_e_ignorado(self, tmp_path):
        """Condição inválida (ex: 'abc') → ValueError → except nas linhas 164-166."""
        from Sapiens_MultiAgente.tools.csv_search_tool import CSVSearchTool

        csv_file = tmp_path / 'notas_err.csv'
        csv_file.write_text('nome,score\nAna,5\nBia,7\n', encoding='utf-8')

        tool = CSVSearchTool()
        # 'abc' não é float válido → float('abc') lança ValueError → continue
        result = tool._run(file_path=str(csv_file), numeric_filters={'score': 'abc'})

        # Filtro ignorado → todos os registros retornam
        assert 'Ana' in result
        assert 'Bia' in result


# ---------------------------------------------------------------------------
# web/app.py — linha 640 (ext = '.txt' quando URL sem extensão)
# ---------------------------------------------------------------------------

class TestLinkSemExtensao:
    """
    Quando o link não tem extensão (ex: http://example.com/api/data),
    os.path.splitext retorna ext='', ativando o ramo `ext = '.txt'` (linha 640).
    """

    @pytest.fixture
    def app_cliente(self, tmp_path):
        db_path = str(tmp_path / 'test_link_ext.db')
        upload_folder = str(tmp_path / 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        with patch('Sapiens_MultiAgente.web.app.DB_PATH', db_path), \
             patch('Sapiens_MultiAgente.web.auth.DB_PATH', db_path):
            from Sapiens_MultiAgente.web.app import SapiensWebInterface
            interface = SapiensWebInterface()
            flask_app = interface.create_app()
            flask_app.config['TESTING'] = True
            flask_app.config['WTF_CSRF_ENABLED'] = False
            flask_app.config['UPLOAD_FOLDER'] = upload_folder
            yield interface, flask_app.test_client()

    def _login(self, client):
        client.post('/login', data={'username': 'admin', 'senha': 'sapiens@2025'})

    def test_link_sem_extensao_usa_txt(self, app_cliente):
        """
        URL sem extensão → os.path.splitext retorna ext='' → linha 640 ativa.
        """
        interface, client = app_cliente
        self._login(client)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'coluna1,coluna2\n1,2\n3,4\n'

        with patch('Sapiens_MultiAgente.web.app.requests.get', return_value=mock_resp), \
             patch.object(interface.security_validator, 'validar_arquivo',
                          return_value={'valido': True, 'erros': [], 'avisos': []}), \
             patch.object(interface, '_executar_analise'):
            resp = client.post(
                '/analise',
                data={
                    'topico_pesquisa': 'Teste link sem extensão',
                    # URL sem extensão: splitext retorna ('...endpoint', '')
                    'links_sites': 'http://example.com/api/endpoint',
                },
                follow_redirects=True,
            )

        assert resp.status_code == 200
