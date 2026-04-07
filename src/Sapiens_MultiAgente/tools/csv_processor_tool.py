import pandas as pd
import numpy as np
from typing import Type, Optional, Dict, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import io


MAX_ROWS_IN_MEMORY = 100_000  # Acima disso usa chunking para estatísticas


class CSVProcessorToolInput(BaseModel):
    """Input schema for CSVProcessorTool."""
    file_path: str = Field(..., description="Path to the CSV file to process")
    separator: str = Field(default=',', description="CSV separator (comma, semicolon, tab, etc.)")
    encoding: str = Field(default='utf-8', description="File encoding")
    sample_size: int = Field(default=5, description="Number of sample rows to preview")


class CSVProcessorTool(BaseTool):
    name: str = "CSVProcessorTool"
    description: str = (
        "Ferramenta para processar e analisar arquivos CSV. Realiza leitura, "
        "limpeza básica de dados, análise estatística preliminar e fornece "
        "insights sobre a estrutura e qualidade dos dados."
    )
    args_schema: Type[BaseModel] = CSVProcessorToolInput

    def _run(self, file_path: str, separator: str = ',', encoding: str = 'utf-8', sample_size: int = 5) -> str:
        """
        Processa um arquivo CSV e retorna análise detalhada.

        Args:
            file_path: Caminho para o arquivo CSV
            separator: Separador do CSV
            encoding: Codificação do arquivo
            sample_size: Número de linhas para preview

        Returns:
            Relatório detalhado sobre o CSV processado
        """
        try:
            # Tentar diferentes separadores se o padrão não funcionar
            separators_to_try = [separator, ';', '\t', '|']

            df = None
            successful_sep = None

            for sep in separators_to_try:
                try:
                    df = pd.read_csv(file_path, sep=sep, encoding=encoding)
                    if len(df.columns) > 1:  # Se tem múltiplas colunas, provavelmente é o certo
                        successful_sep = sep
                        break
                except:
                    continue

            if df is None or df.empty:
                return "❌ ERRO: Não foi possível ler o arquivo CSV ou arquivo vazio."

            # Informações básicas
            num_rows = len(df)
            num_cols = len(df.columns)
            memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB

            large_file_warning = ""
            if num_rows > MAX_ROWS_IN_MEMORY:
                large_file_warning = (
                    f"\n⚠️ ARQUIVO GRANDE: {num_rows:,} linhas detectadas. "
                    "Estatísticas calculadas sobre o conjunto completo.\n"
                )

            # Análise de tipos de dados
            dtypes_info = self._analyze_data_types(df)

            # Análise de valores faltantes
            missing_info = self._analyze_missing_values(df)

            # Estatísticas básicas para colunas numéricas
            numeric_stats = self._get_numeric_statistics(df)

            # Preview dos dados
            preview = df.head(sample_size).to_string()

            # Relatório
            report = f"""
📊 ANÁLISE DE ARQUIVO CSV
{large_file_warning}
📁 Arquivo: {file_path}
📏 Dimensões: {num_rows:,} linhas × {num_cols} colunas
💾 Uso de memória: {memory_usage:.2f} MB
🔤 Separador detectado: '{successful_sep}'
🔄 Codificação: {encoding}

📋 TIPOS DE DADOS POR COLUNA:
{dtypes_info}

❓ VALORES FALTANTES:
{missing_info}

📈 ESTATÍSTICAS PARA COLUNAS NUMÉRICAS:
{numeric_stats}

👀 PREVIEW DOS DADOS (primeiras {sample_size} linhas):
```
{preview}
```

✅ ARQUIVO CSV PROCESSADO COM SUCESSO
"""

            return report

        except Exception as e:
            return f"❌ ERRO durante processamento do CSV: {str(e)}"

    def _analyze_data_types(self, df: pd.DataFrame) -> str:
        """Analisa tipos de dados das colunas."""
        type_counts = {}
        details = []

        for col in df.columns:
            dtype = str(df[col].dtype)
            if dtype not in type_counts:
                type_counts[dtype] = 0
            type_counts[dtype] += 1

            # Detalhes por coluna
            unique_count = df[col].nunique()
            sample_values = df[col].dropna().head(3).tolist()
            details.append(f"• {col}: {dtype} (únicos: {unique_count}) - Ex: {sample_values}")

        summary = f"Resumo: {type_counts}\n\nDetalhes por coluna:\n" + "\n".join(details)
        return summary

    def _analyze_missing_values(self, df: pd.DataFrame) -> str:
        """Analisa valores faltantes."""
        missing_counts = df.isnull().sum()
        total_missing = missing_counts.sum()

        if total_missing == 0:
            return "Nenhum valor faltante detectado."

        # Colunas com valores faltantes
        missing_cols = missing_counts[missing_counts > 0]
        missing_details = []

        for col, count in missing_cols.items():
            percentage = (count / len(df)) * 100
            missing_details.append(f"• {col}: {count} valores ({percentage:.1f}%)")

        return f"Total de valores faltantes: {total_missing}\n" + "\n".join(missing_details)

    def _get_numeric_statistics(self, df: pd.DataFrame) -> str:
        """Obtém estatísticas básicas para colunas numéricas."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) == 0:
            return "Nenhuma coluna numérica encontrada."

        stats = df[numeric_cols].describe().round(2)
        return stats.to_string()