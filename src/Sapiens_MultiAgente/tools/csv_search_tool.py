import pandas as pd
import os
from typing import Type, Optional, Dict, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class CSVSearchToolInput(BaseModel):
    """Input schema for CSVSearchTool."""
    file_path: str = Field(..., description="Path to the CSV file to search")
    search_query: Optional[str] = Field(default=None, description="Text to search for in any column")
    column_filters: Optional[Dict[str, Any]] = Field(default=None, description="Column-specific filters (e.g., {'column': 'value'})")
    numeric_filters: Optional[Dict[str, str]] = Field(default=None, description="Numeric filters (e.g., {'column': '>10'})")
    separator: str = Field(default=',', description="CSV separator")
    encoding: str = Field(default='utf-8', description="File encoding")
    max_results: int = Field(default=50, description="Maximum number of results to return")
    case_sensitive: bool = Field(default=False, description="Case sensitive search")


class CSVSearchTool(BaseTool):
    name: str = "CSVSearchTool"
    description: str = (
        "Ferramenta avançada para buscar e filtrar dados em arquivos CSV. Permite "
        "pesquisa de texto, filtros por coluna, filtros numéricos, e extração "
        "de dados específicos de datasets acadêmicos."
    )
    args_schema: Type[BaseModel] = CSVSearchToolInput

    def _run(self, file_path: str, search_query: Optional[str] = None,
             column_filters: Optional[Dict[str, Any]] = None,
             numeric_filters: Optional[Dict[str, str]] = None,
             separator: str = ',', encoding: str = 'utf-8',
             max_results: int = 50, case_sensitive: bool = False) -> str:
        """
        Busca e filtra dados em um arquivo CSV.

        Args:
            file_path: Caminho para o arquivo CSV
            search_query: Termo a buscar em qualquer coluna
            column_filters: Filtros específicos por coluna
            numeric_filters: Filtros numéricos (ex: '>10', '<=5')
            separator: Separador do CSV
            encoding: Codificação do arquivo
            max_results: Máximo de resultados
            case_sensitive: Busca case-sensitive

        Returns:
            Resultados da busca filtrada
        """
        if not os.path.exists(file_path):
            return f"❌ ERRO: Arquivo CSV não encontrado: {file_path}"

        try:
            # Carregar CSV
            df = pd.read_csv(file_path, sep=separator, encoding=encoding)

            if df.empty:
                return "❌ ERRO: Arquivo CSV está vazio."

            original_rows = len(df)

            # Aplicar filtros de coluna
            if column_filters:
                df = self._apply_column_filters(df, column_filters, case_sensitive)

            # Aplicar filtros numéricos
            if numeric_filters:
                df = self._apply_numeric_filters(df, numeric_filters)

            # Aplicar busca de texto
            if search_query:
                df = self._apply_text_search(df, search_query, case_sensitive)

            filtered_rows = len(df)

            if df.empty:
                return f"🔍 NENHUM RESULTADO ENCONTRADO\n\nFiltros aplicados: {self._format_filters(search_query, column_filters, numeric_filters)}\nTotal de linhas no arquivo: {original_rows}"

            # Limitar resultados
            if len(df) > max_results:
                df = df.head(max_results)
                limited = True
            else:
                limited = False

            # Preparar relatório
            report = f"""
🔍 RESULTADOS DA BUSCA EM CSV

📁 Arquivo: {os.path.basename(file_path)}
📊 Linhas originais: {original_rows}
📈 Linhas após filtros: {filtered_rows}
{'📋 Mostrando primeiros ' + str(max_results) + ' resultados' if limited else ''}

🔎 FILTROS APLICADOS:
{self._format_filters(search_query, column_filters, numeric_filters)}

📋 DADOS ENCONTRADOS:
"""

            # Mostrar preview dos dados
            preview = df.to_string(index=False, max_rows=20, max_cols=10)
            if len(df) > 20:
                preview += f"\n... (mais {len(df) - 20} linhas)"

            report += f"\n{preview}"

            # Estatísticas adicionais se houver colunas numéricas
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0 and len(df) > 1:
                report += "\n\n📈 ESTATÍSTICAS DOS RESULTADOS:"
                stats = df[numeric_cols].describe().round(2)
                report += "\n" + stats.to_string()

            return report

        except Exception as e:
            return f"❌ ERRO durante busca no CSV: {str(e)}"

    def _apply_column_filters(self, df: pd.DataFrame, filters: Dict[str, Any], case_sensitive: bool) -> pd.DataFrame:
        """Aplica filtros específicos por coluna."""
        for column, value in filters.items():
            if column in df.columns:
                if not case_sensitive and isinstance(value, str):
                    # Filtro case-insensitive para strings
                    df = df[df[column].astype(str).str.lower() == str(value).lower()]
                else:
                    df = df[df[column] == value]
        return df

    def _apply_numeric_filters(self, df: pd.DataFrame, filters: Dict[str, str]) -> pd.DataFrame:
        """Aplica filtros numéricos."""
        for column, condition in filters.items():
            if column in df.columns:
                try:
                    # Tentar converter coluna para numérica se necessário
                    if not pd.api.types.is_numeric_dtype(df[column]):
                        df[column] = pd.to_numeric(df[column], errors='coerce')

                    # Aplicar condição
                    if condition.startswith('>'):
                        threshold = float(condition[1:])
                        df = df[df[column] > threshold]
                    elif condition.startswith('<'):
                        threshold = float(condition[1:])
                        df = df[df[column] < threshold]
                    elif condition.startswith('>='):
                        threshold = float(condition[2:])
                        df = df[df[column] >= threshold]
                    elif condition.startswith('<='):
                        threshold = float(condition[2:])
                        df = df[df[column] <= threshold]
                    elif condition.startswith('=='):
                        threshold = float(condition[2:])
                        df = df[df[column] == threshold]
                    elif '!=' in condition:
                        threshold = float(condition.split('!=')[1])
                        df = df[df[column] != threshold]
                    else:
                        # Assumir igualdade
                        threshold = float(condition)
                        df = df[df[column] == threshold]

                except (ValueError, TypeError):
                    # Pular filtro se não conseguir aplicar
                    continue
        return df

    def _apply_text_search(self, df: pd.DataFrame, query: str, case_sensitive: bool) -> pd.DataFrame:
        """Aplica busca de texto em todas as colunas."""
        # Converter tudo para string para busca
        df_str = df.astype(str)

        if not case_sensitive:
            query = query.lower()
            mask = df_str.apply(lambda x: x.str.lower().str.contains(query, na=False)).any(axis=1)
        else:
            mask = df_str.apply(lambda x: x.str.contains(query, na=False)).any(axis=1)

        return df[mask]

    def _format_filters(self, search_query: Optional[str],
                        column_filters: Optional[Dict[str, Any]],
                        numeric_filters: Optional[Dict[str, str]]) -> str:
        """Formata os filtros aplicados para exibição."""
        filters_desc = []

        if search_query:
            filters_desc.append(f"• Busca de texto: '{search_query}'")

        if column_filters:
            for col, val in column_filters.items():
                filters_desc.append(f"• Filtro coluna '{col}': {val}")

        if numeric_filters:
            for col, cond in numeric_filters.items():
                filters_desc.append(f"• Filtro numérico '{col}': {cond}")

        if not filters_desc:
            filters_desc.append("• Nenhum filtro específico (busca geral)")

        return "\n".join(filters_desc)
