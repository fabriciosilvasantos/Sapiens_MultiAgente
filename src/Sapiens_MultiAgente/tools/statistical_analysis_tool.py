import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
from typing import Type, Optional, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import csv
import json

EXTENSOES_TABULARES = {".csv", ".txt", ".xlsx", ".xls", ".json"}
MAX_CATEGORIAS = 15  # categorias listadas por coluna na análise descritiva


class StatisticalAnalysisToolInput(BaseModel):
    """Input schema for StatisticalAnalysisTool."""
    file_path: Optional[str] = Field(
        default=None,
        description=(
            "Caminho do arquivo de dados (.csv, .xlsx, .xls, .json) — forma PREFERIDA. "
            "Use os caminhos recebidos na tarefa em vez de copiar os dados para 'data'."
        )
    )
    data: Optional[str] = Field(
        default=None,
        description="Dados inline em JSON (lista de registros ou dict de colunas). Use apenas para amostras pequenas."
    )
    analysis_type: str = Field(
        ...,
        description=(
            "Tipo de análise estatística a executar. Valores aceitos (português ou inglês): "
            "'descritiva' ou 'descriptive' — estatísticas descritivas e normalidade; "
            "'correlacao' ou 'correlation' — matriz de correlação; "
            "'teste_hipotese' ou 'hypothesis_test' — testes t e qui-quadrado; "
            "'regressao' ou 'regression' — regressão linear; "
            "'anova' ou 'anova_one_way' — ANOVA one-way com post-hoc Tukey."
        )
    )
    variables: Optional[List[str]] = Field(default=None, description="Variables to analyze")
    group_column: Optional[str] = Field(
        default=None,
        description="Column used as grouping factor for ANOVA (categorical variable)"
    )
    alpha: float = Field(default=0.05, description="Significance level for hypothesis tests")


class StatisticalAnalysisTool(BaseTool):
    name: str = "StatisticalAnalysisTool"
    description: str = (
        "Ferramenta avançada para análises estatísticas. Realiza análises descritivas, "
        "correlações, testes de hipóteses, regressões e outras análises estatísticas "
        "para apoiar decisões baseadas em dados acadêmicos. Informe o arquivo em 'file_path' "
        "(CSV/Excel/JSON) — não é preciso colar os dados no argumento."
    )
    args_schema: Type[BaseModel] = StatisticalAnalysisToolInput

    def _run(self, data: Optional[str] = None, analysis_type: str = "descriptive",
             variables: Optional[List[str]] = None, group_column: Optional[str] = None,
             alpha: float = 0.05, file_path: Optional[str] = None) -> str:
        """
        Executa análise estatística nos dados fornecidos.

        Args:
            data: Dados em formato JSON (alternativa a file_path)
            analysis_type: Tipo de análise desejada
            variables: Variáveis específicas para análise
            group_column: Coluna de agrupamento para ANOVA
            alpha: Nível de significância
            file_path: Caminho de arquivo CSV/Excel/JSON (tem precedência sobre data)

        Returns:
            Resultados da análise estatística
        """
        # Mapeamento PT→EN: aceita termos em português ou inglês
        _ALIASES = {
            "descritiva": "descriptive",
            "descritivo": "descriptive",
            "correlacao": "correlation",
            "correlação": "correlation",
            "teste_hipotese": "hypothesis_test",
            "teste_hipótese": "hypothesis_test",
            "hipotese": "hypothesis_test",
            "hipótese": "hypothesis_test",
            "regressao": "regression",
            "regressão": "regression",
            "anova": "anova_one_way",
        }
        analysis_type = _ALIASES.get(analysis_type.lower(), analysis_type.lower())

        try:
            if file_path:
                df = self._carregar_arquivo(file_path)
                if isinstance(df, str):
                    return df
            elif data:
                data_dict = json.loads(data)
                if not isinstance(data_dict, (list, dict)):
                    return "❌ ERRO: Formato de dados não suportado."
                df = pd.DataFrame(data_dict)
            else:
                return "❌ ERRO: Informe 'file_path' (caminho do arquivo de dados) ou 'data' (JSON)."

            if df.empty:
                return "❌ ERRO: Dados vazios fornecidos."

            # Para ANOVA, preserva a coluna de grupo antes de filtrar variáveis
            if analysis_type == "anova_one_way":
                return self._anova_one_way(df, group_column, variables, alpha)

            # Selecionar variáveis se especificadas
            if variables:
                available_vars = [v for v in variables if v in df.columns]
                if not available_vars:
                    return f"❌ ERRO: Nenhuma das variáveis especificadas encontrada: {variables}"
                df = df[available_vars]

            # Executar análise baseada no tipo
            if analysis_type == "descriptive":
                return self._descriptive_analysis(df)
            elif analysis_type == "correlation":
                return self._correlation_analysis(df)
            elif analysis_type == "hypothesis_test":
                return self._hypothesis_testing(df, alpha)
            elif analysis_type == "regression":
                return self._regression_analysis(df)
            else:
                return (
                    f"❌ ERRO: Tipo de análise não suportado: '{analysis_type}'. "
                    "Use: descritiva, correlacao, regressao, teste_hipotese, anova"
                )

        except json.JSONDecodeError:
            return "❌ ERRO: Dados não estão em formato JSON válido."
        except Exception as e:
            return f"❌ ERRO durante análise estatística: {str(e)}"

    def _carregar_arquivo(self, file_path: str):
        """Lê CSV/Excel/JSON em DataFrame; retorna string '❌ ERRO: ...' se não for possível."""
        caminho = Path(file_path).expanduser()
        extensao = caminho.suffix.lower()
        if extensao not in EXTENSOES_TABULARES:
            return (
                f"❌ ERRO: Extensão '{extensao or '(nenhuma)'}' não suportada para análise estatística. "
                "Use .csv, .xlsx, .xls ou .json."
            )
        if not caminho.is_file():
            return f"❌ ERRO: Arquivo não encontrado: {file_path}"

        if extensao in (".xlsx", ".xls"):
            return pd.read_excel(caminho)
        if extensao == ".json":
            return pd.read_json(caminho)
        # CSV: tolera arquivos em latin-1 e detecta o separador entre ',', ';', tab e '|'
        for encoding in ("utf-8-sig", "latin-1"):
            try:
                with open(caminho, encoding=encoding, newline="") as f:
                    amostra = f.read(64 * 1024)
                break
            except UnicodeDecodeError:
                continue
        try:
            separador = csv.Sniffer().sniff(amostra, delimiters=",;\t|").delimiter
        except csv.Error:
            separador = ","  # uma única coluna ou formato ambíguo
        return pd.read_csv(caminho, sep=separador, encoding=encoding)

    def _descriptive_analysis(self, df: pd.DataFrame) -> str:
        """Análise descritiva completa."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        report = "📊 ANÁLISE DESCRITIVA\n\n"

        if len(numeric_cols) > 0:
            report += "📈 VARIÁVEIS NUMÉRICAS:\n"
            desc_stats = df[numeric_cols].describe(percentiles=[.25, .5, .75, .9, .95]).round(3)
            report += desc_stats.to_string() + "\n\n"

            # Teste de normalidade (Shapiro-Wilk)
            report += "🔔 TESTE DE NORMALIDADE (Shapiro-Wilk):\n"
            for col in numeric_cols:
                try:
                    stat, p_value = stats.shapiro(df[col].dropna())
                    normality = "Normal" if p_value > 0.05 else "Não normal"
                    report += f"• {col}: {normality} (p={p_value:.3f})\n"
                except Exception:
                    report += f"• {col}: Não foi possível testar\n"
            report += "\n"

        if len(categorical_cols) > 0:
            report += "📊 VARIÁVEIS CATEGÓRICAS:\n"
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                distintos = len(value_counts)
                # Colunas quase únicas (nomes, matrículas, e-mails) não são categorias:
                # listar os valores exporia dados pessoais ao LLM sem valor analítico.
                if distintos > MAX_CATEGORIAS and distintos > 0.5 * df[col].notna().sum():
                    report += f"• {col}: {distintos} valores distintos (provável identificador — valores omitidos)\n\n"
                    continue
                report += f"• {col}:\n{value_counts.head(MAX_CATEGORIAS).to_string()}\n"
                if distintos > MAX_CATEGORIAS:
                    report += f"  … e mais {distintos - MAX_CATEGORIAS} categorias\n"
                report += "\n"

        return report

    def _correlation_analysis(self, df: pd.DataFrame) -> str:
        """Análise de correlação."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) < 2:
            return "❌ ERRO: Necessário pelo menos 2 variáveis numéricas para análise de correlação."

        # Matriz de correlação de Pearson
        corr_matrix = df[numeric_cols].corr(method='pearson').round(3)

        report = "🔗 ANÁLISE DE CORRELAÇÃO\n\n"
        report += "📊 MATRIZ DE CORRELAÇÃO (Pearson):\n"
        report += corr_matrix.to_string() + "\n\n"

        # Correlações significativas
        report += "🎯 CORRELAÇÕES SIGNIFICATIVAS (|r| > 0.5):\n"
        significant_corr = []

        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) > 0.5:
                    strength = self._interpret_correlation_strength(corr)
                    significant_corr.append(f"• {numeric_cols[i]} ↔ {numeric_cols[j]}: r = {corr} ({strength})")

        if significant_corr:
            report += "\n".join(significant_corr)
        else:
            report += "Nenhuma correlação forte detectada."

        return report

    def _hypothesis_testing(self, df: pd.DataFrame, alpha: float) -> str:
        """Testes de hipóteses."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) < 2:
            return "❌ ERRO: Necessário pelo menos 2 variáveis numéricas para testes de hipóteses."

        report = f"🧪 TESTES DE HIPÓTESES (α = {alpha})\n\n"

        # Testes t para médias
        if len(numeric_cols) >= 2:
            report += "📏 TESTES T PARA DIFERENÇA DE MÉDIAS:\n"
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    try:
                        var1, var2 = numeric_cols[i], numeric_cols[j]
                        data1 = df[var1].dropna()
                        data2 = df[var2].dropna()

                        if len(data1) > 0 and len(data2) > 0:
                            # Teste t independente
                            t_stat, p_value = stats.ttest_ind(data1, data2, equal_var=False)
                            significant = "Sim" if p_value < alpha else "Não"
                            report += f"• {var1} vs {var2}: t={t_stat:.3f}, p={p_value:.3f} (significativo: {significant})\n"
                    except Exception as e:
                        report += f"• Erro em {numeric_cols[i]} vs {numeric_cols[j]}: {str(e)}\n"

        return report

    def _regression_analysis(self, df: pd.DataFrame) -> str:
        """Análise de regressão linear simples."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) < 2:
            return "❌ ERRO: Necessário pelo menos 2 variáveis numéricas para regressão."

        report = "📈 ANÁLISE DE REGRESSÃO LINEAR\n\n"

        # Regressão simples entre primeira e segunda variável numérica
        x_col, y_col = numeric_cols[0], numeric_cols[1]

        try:
            # Remover valores faltantes
            clean_data = df[[x_col, y_col]].dropna()

            if len(clean_data) < 3:
                return "❌ ERRO: Dados insuficientes para regressão (mínimo 3 pontos)."

            X = clean_data[x_col].values.reshape(-1, 1)
            y = clean_data[y_col].values

            # Regressão linear
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import r2_score, mean_squared_error

            model = LinearRegression()
            model.fit(X, y)

            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
            mse = mean_squared_error(y, y_pred)
            slope = model.coef_[0]
            intercept = model.intercept_

            report += f"📊 Regressão: {y_col} = {slope:.3f} × {x_col} + {intercept:.3f}\n"
            report += f"📈 R² = {r2:.3f} (coeficiente de determinação)\n"
            report += f"📏 MSE = {mse:.3f} (erro quadrático médio)\n"

            # Interpretação
            if r2 > 0.8:
                interpretation = "Excelente ajuste"
            elif r2 > 0.6:
                interpretation = "Bom ajuste"
            elif r2 > 0.3:
                interpretation = "Ajuste moderado"
            else:
                interpretation = "Ajuste fraco"

            report += f"💡 Interpretação: {interpretation}\n"

        except Exception as e:
            report += f"❌ Erro na regressão: {str(e)}\n"

        return report

    def _anova_one_way(self, df: pd.DataFrame, group_column: Optional[str],
                       variables: Optional[List[str]], alpha: float) -> str:
        """
        ANOVA One-Way: testa se as médias de uma variável diferem entre grupos.

        Requer:
          - group_column: coluna categórica (fator)
          - variables: lista com pelo menos 1 variável numérica dependente
        """
        if not group_column:
            return (
                "❌ ERRO: ANOVA requer 'group_column' com o nome da coluna de agrupamento "
                "(variável categórica independente)."
            )
        if group_column not in df.columns:
            return f"❌ ERRO: Coluna de grupo '{group_column}' não encontrada nos dados."

        # Variáveis dependentes numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if variables:
            target_cols = [v for v in variables if v in numeric_cols]
        else:
            target_cols = [c for c in numeric_cols if c != group_column]

        if not target_cols:
            return "❌ ERRO: Nenhuma variável numérica dependente encontrada para ANOVA."

        grupos = df[group_column].dropna().unique()
        if len(grupos) < 2:
            return f"❌ ERRO: ANOVA requer pelo menos 2 grupos. Encontrado: {len(grupos)}."

        report = f"📊 ANOVA ONE-WAY (α = {alpha})\n"
        report += f"🔑 Fator (grupo): {group_column} — {len(grupos)} grupos: {list(grupos)}\n\n"

        for col in target_cols:
            report += f"━━━ Variável dependente: {col} ━━━\n"
            try:
                # Coletar amostras por grupo
                amostras = [
                    df.loc[df[group_column] == g, col].dropna().values
                    for g in grupos
                ]
                # Remover grupos sem dados
                amostras = [a for a in amostras if len(a) > 0]
                if len(amostras) < 2:
                    report += "  ⚠️  Dados insuficientes após remoção de NaN.\n\n"
                    continue

                # ANOVA F-test
                f_stat, p_value = stats.f_oneway(*amostras)
                significativo = p_value < alpha

                report += f"  F = {f_stat:.4f}, p = {p_value:.4f}\n"
                report += f"  Resultado: {'✅ Diferença significativa' if significativo else '❌ Sem diferença significativa'} "
                report += f"(p {'<' if significativo else '>='} {alpha})\n"

                # Tamanho do efeito: eta² = SS_between / SS_total
                grand_mean = np.concatenate(amostras).mean()
                ss_between = sum(len(a) * (a.mean() - grand_mean) ** 2 for a in amostras)
                ss_total = sum(((v - grand_mean) ** 2) for a in amostras for v in a)
                eta2 = ss_between / ss_total if ss_total > 0 else 0
                report += f"  Eta² = {eta2:.4f} ({self._interpretar_eta2(eta2)})\n"

                # Estatísticas por grupo
                report += "  Médias por grupo:\n"
                for g, a in zip(grupos, amostras):
                    report += f"    • {g}: n={len(a)}, média={a.mean():.3f}, dp={a.std():.3f}\n"

                # Teste de Levene (homogeneidade de variâncias) — pressuposto da ANOVA
                lev_stat, lev_p = stats.levene(*amostras)
                variancia_ok = lev_p > alpha
                report += (
                    f"  Levene (homog. variâncias): F={lev_stat:.3f}, p={lev_p:.4f} "
                    f"→ {'✅ OK' if variancia_ok else '⚠️ Variâncias heterogêneas — considere Welch ANOVA'}\n"
                )

                # Post-hoc: Tukey HSD (par-a-par) quando ANOVA é significativa
                if significativo and len(amostras) > 2:
                    report += "  Post-hoc Tukey HSD (comparações par-a-par):\n"
                    for i in range(len(grupos)):
                        for j in range(i + 1, len(grupos)):
                            _, p_tukey = stats.ttest_ind(amostras[i], amostras[j], equal_var=variancia_ok)
                            # Correção de Bonferroni simples como aproximação
                            n_comparacoes = len(grupos) * (len(grupos) - 1) / 2
                            p_adj = min(p_tukey * n_comparacoes, 1.0)
                            sinal = "✅" if p_adj < alpha else "—"
                            report += (
                                f"    {sinal} {grupos[i]} vs {grupos[j]}: "
                                f"p_adj={p_adj:.4f}\n"
                            )

            except Exception as e:
                report += f"  ❌ Erro: {e}\n"
            report += "\n"

        return report

    def _interpretar_eta2(self, eta2: float) -> str:
        """Interpreta o tamanho do efeito pelo eta²."""
        if eta2 >= 0.14:
            return "efeito grande"
        elif eta2 >= 0.06:
            return "efeito médio"
        elif eta2 >= 0.01:
            return "efeito pequeno"
        return "efeito negligenciável"

    def _interpret_correlation_strength(self, corr: float) -> str:
        """Interpreta a força da correlação."""
        abs_corr = abs(corr)
        if abs_corr >= 0.9:
            return "Correlação muito forte"
        elif abs_corr >= 0.7:
            return "Correlação forte"
        elif abs_corr >= 0.5:
            return "Correlação moderada"
        elif abs_corr >= 0.3:
            return "Correlação fraca"
        else:
            return "Correlação muito fraca"
