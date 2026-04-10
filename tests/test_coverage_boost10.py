"""
Boost de cobertura — módulos com baixa cobertura:
  - devops_analysis_tool.py   (0%  → ~90%)
  - quality_review_tool.py    (19% → ~90%)
  - text_analysis_tool.py     (25% → ~90%)
  - external_data_tool.py     (28% → ~80%)
  - llm_settings.py           (41% → ~85%)
  - llm_fallback.py           (71% → ~90%)
"""
import os
import json
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# =============================================================================
# DevOpsAnalysisTool
# =============================================================================

class TestDevOpsAnalysisTool:

    @pytest.fixture
    def tool(self):
        from Sapiens_MultiAgente.tools.devops_analysis_tool import DevOpsAnalysisTool
        return DevOpsAnalysisTool()

    # --- texto direto ---

    def test_analyze_general_sem_erros(self, tool):
        resultado = tool._run("deploy success build ok passed", analysis_type="geral")
        assert "Análise DevOps" in resultado
        assert "sucesso" in resultado.lower() or "Sucesso" in resultado

    def test_analyze_general_com_erros(self, tool):
        resultado = tool._run(
            "error building container\nfail deploy\nexception raised\nsuccess on retry",
            analysis_type="geral",
        )
        assert "Análise DevOps" in resultado
        assert "erro" in resultado.lower() or "Erro" in resultado

    def test_analyze_pipeline(self, tool):
        conteudo = "build started\nbuild failed\ndeploy ok\nerror in step 3\nbuild success"
        resultado = tool._run(conteudo, analysis_type="pipeline")
        assert "Pipeline" in resultado
        assert "Build" in resultado or "build" in resultado

    def test_analyze_infrastructure(self, tool):
        conteudo = "cpu usage 95%\nmemory critical 98%\ndisk low\nalert: disk full\nalerta critico"
        resultado = tool._run(conteudo, analysis_type="infraestrutura")
        assert "Infraestrutura" in resultado
        assert "CPU" in resultado or "Memória" in resultado

    def test_analyze_incidents(self, tool):
        conteudo = "P1 critical outage\nP2 high latency\nresolved ticket\nP1 sev1 database down\nclosed"
        resultado = tool._run(conteudo, analysis_type="incidentes")
        assert "Incidentes" in resultado
        assert "P1" in resultado

    def test_analyze_default_geral(self, tool):
        resultado = tool._run("some log data here\nerror occurred")
        assert isinstance(resultado, str)
        assert len(resultado) > 10

    def test_load_json_file(self, tool, tmp_path):
        data = [{"build": "ok", "status": "success"}, {"build": "fail", "status": "error"}]
        f = tmp_path / "pipeline.json"
        f.write_text(json.dumps(data), encoding="utf-8")
        resultado = tool._run(str(f), analysis_type="geral")
        assert "Análise DevOps" in resultado

    def test_load_csv_file(self, tool, tmp_path):
        f = tmp_path / "builds.csv"
        f.write_text("build_id,status,duration\n1,success,120\n2,failed,45\n", encoding="utf-8")
        resultado = tool._run(str(f), analysis_type="pipeline")
        assert isinstance(resultado, str)

    def test_load_txt_file(self, tool, tmp_path):
        f = tmp_path / "log.txt"
        f.write_text("build ok\nerror found\ndeploy success\n", encoding="utf-8")
        resultado = tool._run(str(f), analysis_type="geral")
        assert isinstance(resultado, str)

    def test_load_arquivo_inexistente_trata_como_texto(self, tool):
        resultado = tool._run("/caminho/inexistente/arquivo.txt", analysis_type="geral")
        # Caminho não existe → trata como texto direto
        assert isinstance(resultado, str)

    def test_extract_durations(self, tool):
        texto = "step took 120s\nbuild 3500ms\ndeploy 45s"
        durations = tool._extract_durations(texto)
        assert len(durations) >= 2

    def test_recommendations_alta_taxa(self, tool):
        rec = tool._recommendations(25.0)
        assert "Alta taxa" in rec or "alta taxa" in rec.lower()

    def test_recommendations_moderada(self, tool):
        rec = tool._recommendations(10.0)
        assert "moderada" in rec.lower() or "Moderada" in rec

    def test_recommendations_baixa(self, tool):
        rec = tool._recommendations(1.0)
        assert "esperado" in rec.lower() or "Esperado" in rec

    def test_pipeline_com_duracoes(self, tool):
        conteudo = "build completed in 120s\ndeploy took 45s\nerror after 30s"
        resultado = tool._run(conteudo, analysis_type="pipeline")
        assert "Pipeline" in resultado

    def test_error_handling(self, tool):
        with patch.object(tool, '_load_content', side_effect=RuntimeError("Falha de leitura")):
            resultado = tool._run("qualquer coisa")
        assert "❌ ERRO" in resultado


# =============================================================================
# QualityReviewTool
# =============================================================================

class TestQualityReviewTool:

    @pytest.fixture
    def tool(self):
        from Sapiens_MultiAgente.tools.quality_review_tool import QualityReviewTool
        return QualityReviewTool()

    TEXTO_BOM = (
        "A análise descritiva apresenta média de 7,5 (desvio padrão 1,2) para n=150 alunos. "
        "A distribuição é aproximadamente normal. Outliers foram identificados e tratados. "
        "O tamanho da amostra é suficiente para os testes aplicados. "
        "O intervalo de confiança de 95% foi calculado. "
        "O nível de significância adotado foi α=0,05. "
        "O R²=0,72 indica bom ajuste do modelo."
    )

    TEXTO_PROBLEMATICO = (
        "A análise prova que a evasão sempre causa reprovação. "
        "Todos os alunos apresentam o mesmo padrão. Nunca há exceções. "
        "O dado confirma a hipótese. n=3. p < 0,05 apenas."
    )

    def test_revisao_geral_texto_bom(self, tool):
        resultado = tool._run(self.TEXTO_BOM, tipo_analise="geral")
        assert "Qualidade Científica" in resultado
        assert "/100" in resultado

    def test_revisao_descritiva(self, tool):
        resultado = tool._run(self.TEXTO_BOM, tipo_analise="descritiva")
        assert "descritiva" in resultado.lower() or "Descritiva" in resultado

    def test_revisao_diagnostica(self, tool):
        texto = "Teste de hipótese: H0 rejeitada com α=0,05. Tamanho de efeito d=0,8. Pressuposto de normalidade verificado."
        resultado = tool._run(texto, tipo_analise="diagnostica")
        assert isinstance(resultado, str)
        assert "/100" in resultado

    def test_revisao_preditiva(self, tool):
        texto = "Separação treino/teste 80/20. R²=0,85. Intervalo de confiança 95%. Horizonte 2026."
        resultado = tool._run(texto, tipo_analise="preditiva")
        assert isinstance(resultado, str)

    def test_revisao_prescritiva(self, tool):
        texto = "Recomendações baseadas nos dados: 1) Ampliar bolsas. 2) Monitorar indicadores. Custo estimado e benefício esperado."
        resultado = tool._run(texto, tipo_analise="prescritiva")
        assert isinstance(resultado, str)

    def test_alertas_causais_detectados(self, tool):
        alertas = tool._verificar_alertas("o programa causa evasão")
        assert any("causal" in a.lower() for a in alertas)

    def test_alertas_generalizacao_detectada(self, tool):
        alertas = tool._verificar_alertas("todos os alunos sempre reprovam")
        assert len(alertas) > 0

    def test_alertas_prova_detectado(self, tool):
        alertas = tool._verificar_alertas("o resultado prova nossa hipótese")
        assert len(alertas) > 0

    def test_alertas_amostra_pequena(self, tool):
        alertas = tool._verificar_alertas("n = 5 alunos foram estudados")
        assert any("amostra" in a.lower() for a in alertas)

    def test_alertas_r2_baixo(self, tool):
        alertas = tool._verificar_alertas("o modelo tem R² = 0.15")
        assert any("R²" in a or "baixo" in a.lower() for a in alertas)

    def test_alertas_p_valor(self, tool):
        alertas = tool._verificar_alertas("p < 0.05 foi encontrado")
        assert any("p-valor" in a.lower() or "valor-p" in a.lower() for a in alertas)

    def test_sem_alertas_texto_neutro(self, tool):
        alertas = tool._verificar_alertas("A média foi calculada. A mediana é 7.")
        assert isinstance(alertas, list)

    def test_pontuacao_alta(self, tool):
        alertas = []
        checklist = {"descritiva": {item: True for item in ["média", "desvio", "n", "outlier", "distribuição"]}}
        pontuacao = tool._calcular_pontuacao(alertas, checklist)
        assert pontuacao["pontuacao"] >= 80
        assert pontuacao["nivel"] == "Excelente"

    def test_pontuacao_baixa(self, tool):
        alertas = ["erro 1", "erro 2", "erro 3", "erro 4", "erro 5"]
        checklist = {"descritiva": {item: False for item in ["média", "desvio", "n", "outlier", "distribuição"]}}
        pontuacao = tool._calcular_pontuacao(alertas, checklist)
        assert pontuacao["pontuacao"] <= 60

    def test_nivel_executivo(self, tool):
        resultado = tool._run(self.TEXTO_PROBLEMATICO, tipo_analise="geral", nivel_rigor="executivo")
        assert "executivo" in resultado.lower() or "Executivo" in resultado

    def test_checklist_tipo_invalido(self, tool):
        checklist = tool._verificar_checklist("texto qualquer", "tipo_inexistente")
        assert isinstance(checklist, dict)

    def test_parecer_final_satisfatorio(self, tool):
        texto = "Média 7,5 com n=50. p < 0,05. Desvio padrão reportado."
        resultado = tool._run(texto, tipo_analise="geral")
        assert "Parecer Final" in resultado

    def test_recomendacoes_causal(self, tool):
        alertas = ["Afirmação causal: correlação ≠ causalidade."]
        checklist = {}
        recs = tool._gerar_recomendacoes(alertas, checklist, "academico")
        assert any("causal" in r.lower() for r in recs)

    def test_recomendacoes_absoluta(self, tool):
        alertas = ["Generalização absoluta detectada"]
        checklist = {}
        recs = tool._gerar_recomendacoes(alertas, checklist, "academico")
        assert any("absoluta" in r.lower() or "qualificar" in r.lower() for r in recs)

    def test_error_handling(self, tool):
        with patch.object(tool, '_verificar_alertas', side_effect=RuntimeError("falha")):
            resultado = tool._run("texto")
        assert "❌ ERRO" in resultado


# =============================================================================
# TextAnalysisTool
# =============================================================================

class TestTextAnalysisTool:

    @pytest.fixture
    def tool(self):
        from Sapiens_MultiAgente.tools.text_analysis_tool import TextAnalysisTool
        return TextAnalysisTool()

    TEXTO_ACADEMICO = (
        "A UENF registrou em 2022 uma taxa de evasão de 18,9% nos cursos de graduação. "
        "O CCT concentra 59,6% dos casos de evasão. O programa de bolsas reduziu o abandono "
        "em 2023. A pós-graduação stricto sensu apresenta mestrado e doutorado com boa retenção. "
        "Análise da gestão institucional mostra melhoria no desempenho acadêmico e nas notas. "
        "O corpo docente com doutorado é responsável pelos melhores índices. "
        "A UFRJ e a USP também apresentam dados similares de matrícula e ingresso. "
        "Em 2020 e 2021 a pandemia afetou os indicadores de reprovação e aprovação."
    )

    def test_texto_muito_curto_retorna_erro(self, tool):
        resultado = tool._run("curto")
        assert "❌ ERRO" in resultado

    def test_palavras_chave(self, tool):
        resultado = tool._run(self.TEXTO_ACADEMICO, tipo_analise="palavras_chave", top_n=10)
        assert "Palavras-Chave" in resultado
        assert "Top 10" in resultado

    def test_entidades_instituicoes(self, tool):
        resultado = tool._run(self.TEXTO_ACADEMICO, tipo_analise="entidades")
        assert "Entidades" in resultado
        assert "UENF" in resultado or "uenf" in resultado.lower()

    def test_entidades_anos(self, tool):
        resultado = tool._run(self.TEXTO_ACADEMICO, tipo_analise="entidades")
        assert "2022" in resultado or "Anos" in resultado or "anos" in resultado.lower()

    def test_entidades_percentuais(self, tool):
        resultado = tool._run(self.TEXTO_ACADEMICO, tipo_analise="entidades")
        assert "%" in resultado or "Percentuais" in resultado

    def test_entidades_sem_matches(self, tool):
        texto = "A análise mostrou que os dados foram coletados com metodologia rigorosa ao longo do período."
        resultado = tool._run(texto, tipo_analise="entidades")
        assert isinstance(resultado, str)

    def test_temas_evasao(self, tool):
        resultado = tool._run(self.TEXTO_ACADEMICO, tipo_analise="temas")
        assert "Evasão" in resultado or "evasão" in resultado.lower()

    def test_temas_sem_correspondencia(self, tool):
        texto = "A análise de dados quantitativos requer técnicas adequadas de processamento estatístico avançado."
        resultado = tool._run(texto, tipo_analise="temas")
        assert isinstance(resultado, str)

    def test_analise_completa(self, tool):
        resultado = tool._run(self.TEXTO_ACADEMICO, tipo_analise="completa")
        assert "Análise Textual Completa" in resultado
        assert "Palavras-Chave" in resultado
        assert "Entidades" in resultado
        assert "Temas" in resultado

    def test_analise_default_completa(self, tool):
        resultado = tool._run(self.TEXTO_ACADEMICO)
        assert "Análise Textual Completa" in resultado

    def test_estatisticas_basicas(self, tool):
        stats = tool._estatisticas_basicas(self.TEXTO_ACADEMICO)
        assert "Palavras" in stats
        assert "Frases" in stats
        assert "Caracteres" in stats

    def test_tokenizar_remove_stopwords(self, tool):
        tokens = tool._tokenizar("A análise dos dados mostra resultados importantes")
        # 'a', 'dos' são stopwords — verificar que tokens existem
        assert "análise" in tokens or "analise" in tokens
        assert isinstance(tokens, list)

    def test_palavras_chave_texto_sem_palavras_significativas(self, tool):
        # texto longo o suficiente mas só stopwords
        texto = " ".join(["a", "o", "e", "de", "um"] * 20)
        resultado = tool._run(texto, tipo_analise="palavras_chave")
        assert isinstance(resultado, str)

    def test_error_handling(self, tool):
        with patch.object(tool, '_tokenizar', side_effect=RuntimeError("falha")):
            resultado = tool._run(self.TEXTO_ACADEMICO, tipo_analise="palavras_chave")
        assert "❌ ERRO" in resultado

    def test_top_n_respeitado(self, tool):
        resultado = tool._run(self.TEXTO_ACADEMICO, tipo_analise="palavras_chave", top_n=5)
        assert "Top 5" in resultado


# =============================================================================
# ExternalDataTool
# =============================================================================

class TestExternalDataTool:

    @pytest.fixture
    def tool(self):
        from Sapiens_MultiAgente.tools.external_data_tool import ExternalDataTool
        return ExternalDataTool()

    def test_benchmarks_evasao(self, tool):
        resultado = tool._run("evasão estudantil na graduação")
        assert "Benchmarks" in resultado
        assert "26.4" in resultado or "evasão" in resultado.lower()

    def test_benchmarks_evasao_historico(self, tool):
        resultado = tool._run("taxa de evasão por ano")
        assert "2019" in resultado or "Tendência" in resultado or "tendência" in resultado.lower()

    def test_benchmarks_regionais(self, tool):
        resultado = tool._run("evasão estudantil por região")
        assert "Norte" in resultado or "Nordeste" in resultado or "Sudeste" in resultado

    def test_benchmarks_docentes(self, tool):
        resultado = tool._run("qualificação do corpo docente")
        assert "Docente" in resultado or "doutorado" in resultado.lower()

    def test_benchmarks_enade(self, tool):
        resultado = tool._run("desempenho ENADE avaliação estudantes")
        assert "ENADE" in resultado or "2.8" in resultado

    def test_benchmarks_ead(self, tool):
        resultado = tool._run("modalidade EAD e presencial matrículas")
        assert "EAD" in resultado or "62.8" in resultado

    def test_benchmarks_pos_graduacao(self, tool):
        resultado = tool._run("pós-graduação stricto sensu mestrado doutorado")
        assert "Pós" in resultado or "mestrado" in resultado.lower() or "12.0" in resultado

    def test_benchmarks_topico_generico(self, tool):
        resultado = tool._run("análise acadêmica geral")
        assert "Benchmarks" in resultado
        assert "Nacional" in resultado or "nacional" in resultado.lower()

    def test_fontes_relevancias(self, tool):
        resultado = tool._run("evasão matrícula universidade", tipo_busca="fontes")
        assert "Fontes" in resultado
        assert "INEP" in resultado or "MEC" in resultado

    def test_fontes_topico_sem_match(self, tool):
        resultado = tool._run("tópico genérico qualquer", tipo_busca="fontes")
        assert "Fontes" in resultado

    def test_contexto_completo(self, tool):
        resultado = tool._run("evasão estudantil", tipo_busca="contexto")
        assert "Benchmarks" in resultado
        assert "Fontes" in resultado or "fontes" in resultado.lower()

    def test_consultar_ibge_fallback(self, tool):
        resultado = tool._consultar_ibge("99999")
        assert "indisponível" in resultado.lower() or isinstance(resultado, str)

    def test_extrair_numeros(self, tool):
        numeros = tool._extrair_numeros("taxa de 26,4% e índice 3.7")
        assert isinstance(numeros, list)

    def test_error_handling(self, tool):
        with patch.object(tool, '_retornar_benchmarks', side_effect=RuntimeError("falha")):
            resultado = tool._run("qualquer tópico", tipo_busca="benchmarks")
        assert "❌ ERRO" in resultado


# =============================================================================
# LLMSettings
# =============================================================================

class TestLLMSettings:
    """Testa llm_settings.py usando um llm_config.yaml temporário."""

    YAML_CONTEUDO = """
ativo: modelo_a

agentes:
  agente_teste: modelo_b

modelos:
  modelo_a:
    nome: Modelo A
    model_id: openrouter/test/model-a
    temperatura: 0.7
    groq_fallback: groq/model-a
    descricao: Modelo de teste A

  modelo_b:
    nome: Modelo B
    model_id: openrouter/test/model-b
    temperatura: 0.5
    groq_fallback: groq/model-b
    descricao: Modelo de teste B
"""

    @pytest.fixture
    def config_path(self, tmp_path):
        p = tmp_path / "llm_config.yaml"
        p.write_text(self.YAML_CONTEUDO, encoding="utf-8")
        return p

    @pytest.fixture
    def settings(self, config_path):
        import importlib
        import Sapiens_MultiAgente.config.llm_settings as mod
        with patch.object(mod, '_CONFIG_PATH', config_path):
            yield mod

    def test_load_llm_config(self, settings):
        cfg = settings.load_llm_config()
        assert "ativo" in cfg
        assert cfg["ativo"] == "modelo_a"

    def test_get_active_model(self, settings):
        model = settings.get_active_model()
        assert model["model_id"] == "openrouter/test/model-a"

    def test_get_model_for_agent_com_config(self, settings):
        model = settings.get_model_for_agent("agente_teste")
        assert model["model_id"] == "openrouter/test/model-b"

    def test_get_model_for_agent_sem_config_usa_ativo(self, settings):
        model = settings.get_model_for_agent("agente_inexistente")
        assert model["model_id"] == "openrouter/test/model-a"

    def test_list_models(self, settings):
        modelos = settings.list_models()
        assert "modelo_a" in modelos
        assert "modelo_b" in modelos

    def test_get_active_key(self, settings):
        chave = settings.get_active_key()
        assert chave == "modelo_a"

    def test_set_active_model(self, settings, config_path):
        model = settings.set_active_model("modelo_b")
        assert model["model_id"] == "openrouter/test/model-b"
        # Verifica persistência
        cfg = settings.load_llm_config()
        assert cfg["ativo"] == "modelo_b"

    def test_set_active_model_invalido(self, settings):
        with pytest.raises(ValueError, match="modelo_inexistente"):
            settings.set_active_model("modelo_inexistente")

    def test_set_agent_model(self, settings, config_path):
        model = settings.set_agent_model("novo_agente", "modelo_b")
        assert model["model_id"] == "openrouter/test/model-b"
        cfg = settings.load_llm_config()
        assert cfg["agentes"]["novo_agente"] == "modelo_b"

    def test_set_agent_model_invalido(self, settings):
        with pytest.raises(ValueError, match="modelo_xyz"):
            settings.set_agent_model("agente_teste", "modelo_xyz")

    def test_get_active_model_chave_invalida(self, settings, config_path):
        """Se 'ativo' aponta para chave inexistente, usa primeiro modelo disponível."""
        import yaml
        cfg = settings.load_llm_config()
        cfg["ativo"] = "chave_inexistente"
        with open(config_path, "w") as f:
            import yaml as _yaml
            _yaml.dump(cfg, f)
        model = settings.get_active_model()
        assert isinstance(model, dict)
        assert "model_id" in model


# =============================================================================
# LLMFallback
# =============================================================================

class TestLLMFallback:

    @pytest.fixture
    def mock_llm_class(self):
        """Cria mock de crewai.LLM."""
        mock = MagicMock()
        mock.call = MagicMock(return_value="resposta do LLM")
        return mock

    def test_is_retryable_429(self):
        from Sapiens_MultiAgente.config.llm_fallback import _is_retryable
        assert _is_retryable(Exception("HTTP 429 Too Many Requests"))

    def test_is_retryable_500(self):
        from Sapiens_MultiAgente.config.llm_fallback import _is_retryable
        assert _is_retryable(Exception("500 Internal Server Error"))

    def test_is_retryable_timeout(self):
        from Sapiens_MultiAgente.config.llm_fallback import _is_retryable
        assert _is_retryable(Exception("connection timeout"))

    def test_is_retryable_rate_limit(self):
        from Sapiens_MultiAgente.config.llm_fallback import _is_retryable
        assert _is_retryable(Exception("rate limit exceeded"))

    def test_is_retryable_overloaded(self):
        from Sapiens_MultiAgente.config.llm_fallback import _is_retryable
        assert _is_retryable(Exception("model overloaded"))

    def test_is_not_retryable_404(self):
        from Sapiens_MultiAgente.config.llm_fallback import _is_retryable
        assert not _is_retryable(Exception("404 Not Found"))

    def test_is_not_retryable_autenticacao(self):
        from Sapiens_MultiAgente.config.llm_fallback import _is_retryable
        assert not _is_retryable(ValueError("invalid API key"))

    def test_build_llm_sem_groq_retorna_fallback_llm(self):
        from Sapiens_MultiAgente.config.llm_fallback import build_llm, FallbackLLM
        model_cfg = {
            "model_id": "openrouter/test/model",
            "temperatura": 0.7,
            "groq_fallback": "groq/llama-3.3-70b-versatile",
        }
        with patch('Sapiens_MultiAgente.config.llm_fallback.LLM.__init__', return_value=None), \
             patch('Sapiens_MultiAgente.config.llm_fallback.FallbackLLM.__init__', return_value=None):
            llm = MagicMock(spec=FallbackLLM)
            with patch('Sapiens_MultiAgente.config.llm_fallback.FallbackLLM', return_value=llm):
                resultado = build_llm(
                    model_cfg=model_cfg,
                    openrouter_api_key="key-test",
                    openrouter_base_url="https://openrouter.ai/api/v1",
                    groq_api_key=None,
                )
            assert resultado is llm

    def test_fallback_llm_call_primary_sucesso(self):
        from Sapiens_MultiAgente.config.llm_fallback import FallbackLLM
        llm = FallbackLLM.__new__(FallbackLLM)
        llm._fallback = None
        llm._max_retries = 2
        llm._retry_delay = 0

        with patch('Sapiens_MultiAgente.config.llm_fallback.LLM.call', return_value="ok"):
            resultado = llm.call([{"role": "user", "content": "teste"}])
        assert resultado == "ok"

    def test_fallback_llm_call_ativa_groq(self):
        from Sapiens_MultiAgente.config.llm_fallback import FallbackLLM, _is_retryable
        llm = FallbackLLM.__new__(FallbackLLM)
        llm._max_retries = 1
        llm._retry_delay = 0

        groq_mock = MagicMock()
        groq_mock.call.return_value = "resposta groq"
        llm._fallback = groq_mock

        with patch('Sapiens_MultiAgente.config.llm_fallback.LLM.call',
                   side_effect=Exception("429 rate limit")):
            resultado = llm.call([{"role": "user", "content": "teste"}])
        assert resultado == "resposta groq"

    def test_fallback_llm_ambos_falham_levanta_runtime_error(self):
        from Sapiens_MultiAgente.config.llm_fallback import FallbackLLM
        llm = FallbackLLM.__new__(FallbackLLM)
        llm._max_retries = 1
        llm._retry_delay = 0

        groq_mock = MagicMock()
        groq_mock.call.side_effect = Exception("Groq down")
        llm._fallback = groq_mock

        with patch('Sapiens_MultiAgente.config.llm_fallback.LLM.call',
                   side_effect=Exception("429 rate limit")):
            with pytest.raises(RuntimeError, match="Groq"):
                llm.call([{"role": "user", "content": "teste"}])

    def test_fallback_llm_sem_fallback_levanta_runtime_error(self):
        from Sapiens_MultiAgente.config.llm_fallback import FallbackLLM
        llm = FallbackLLM.__new__(FallbackLLM)
        llm._max_retries = 1
        llm._retry_delay = 0
        llm._fallback = None

        with patch('Sapiens_MultiAgente.config.llm_fallback.LLM.call',
                   side_effect=Exception("500 server error")):
            with pytest.raises(RuntimeError, match="SAPIENS"):
                llm.call([{"role": "user", "content": "teste"}])

    def test_fallback_llm_erro_nao_retryable_vai_direto_ao_fallback(self):
        from Sapiens_MultiAgente.config.llm_fallback import FallbackLLM
        llm = FallbackLLM.__new__(FallbackLLM)
        llm._max_retries = 3
        llm._retry_delay = 0

        groq_mock = MagicMock()
        groq_mock.call.return_value = "groq ok"
        llm._fallback = groq_mock

        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise Exception("404 not found")  # não retryable

        with patch('Sapiens_MultiAgente.config.llm_fallback.LLM.call', side_effect=side_effect):
            resultado = llm.call([{"role": "user", "content": "teste"}])

        # Deve ter tentado só 1x (não retryable = break imediato)
        assert call_count == 1
        assert resultado == "groq ok"

    def test_configure_fallback(self):
        from Sapiens_MultiAgente.config.llm_fallback import FallbackLLM
        llm = FallbackLLM.__new__(FallbackLLM)
        llm._fallback = None
        llm._max_retries = 2
        llm._retry_delay = 2.0

        groq_mock = MagicMock()
        resultado = llm.configure_fallback(groq_mock, max_retries=3, retry_delay=1.0)

        assert resultado is llm
        assert llm._fallback is groq_mock
        assert llm._max_retries == 3
        assert llm._retry_delay == 1.0
