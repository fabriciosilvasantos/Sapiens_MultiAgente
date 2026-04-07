import json
import base64
import io
from typing import Type, Optional, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import pandas as pd
import numpy as np

try:
    import matplotlib
    matplotlib.use('Agg')  # Backend sem display
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ChartGeneratorToolInput(BaseModel):
    """Input schema for ChartGeneratorTool."""
    data: str = Field(..., description="JSON string com os dados para o gráfico")
    chart_type: str = Field(
        ...,
        description=(
            "Tipo de gráfico: histogram, bar, line, scatter, boxplot, correlation_heatmap"
        )
    )
    x_column: Optional[str] = Field(default=None, description="Coluna para eixo X")
    y_column: Optional[str] = Field(default=None, description="Coluna para eixo Y")
    title: Optional[str] = Field(default=None, description="Título do gráfico")
    output_path: Optional[str] = Field(
        default=None,
        description="Caminho para salvar o gráfico (PNG). Se vazio, retorna base64."
    )


class ChartGeneratorTool(BaseTool):
    name: str = "ChartGeneratorTool"
    description: str = (
        "Gera visualizações gráficas a partir de dados: histogramas, gráficos de barras, "
        "linhas, dispersão, boxplot e heatmap de correlação. Retorna o caminho do arquivo "
        "PNG salvo ou uma string base64 da imagem."
    )
    args_schema: Type[BaseModel] = ChartGeneratorToolInput

    def _run(
        self,
        data: str,
        chart_type: str,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        title: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> str:
        if not MATPLOTLIB_AVAILABLE:
            return "❌ ERRO: matplotlib não está instalado. Execute: pip install matplotlib"

        try:
            data_dict = json.loads(data)
            df = pd.DataFrame(data_dict) if isinstance(data_dict, (list, dict)) else None
            if df is None or df.empty:
                return "❌ ERRO: Dados vazios ou formato inválido."
        except (json.JSONDecodeError, ValueError) as e:
            return f"❌ ERRO ao interpretar dados: {e}"

        chart_type = chart_type.lower()
        fig, ax = plt.subplots(figsize=(10, 6))
        chart_title = title or chart_type.replace('_', ' ').title()

        try:
            if chart_type == 'histogram':
                col = x_column or df.select_dtypes(include=[np.number]).columns[0]
                ax.hist(df[col].dropna(), bins=30, edgecolor='black', color='steelblue', alpha=0.8)
                ax.set_xlabel(col)
                ax.set_ylabel('Frequência')

            elif chart_type == 'bar':
                col = x_column or df.columns[0]
                counts = df[col].value_counts().head(20)
                counts.plot(kind='bar', ax=ax, color='steelblue', edgecolor='black')
                ax.set_xlabel(col)
                ax.set_ylabel('Contagem')
                plt.xticks(rotation=45, ha='right')

            elif chart_type == 'line':
                num_cols = df.select_dtypes(include=[np.number]).columns
                cols = [y_column] if y_column and y_column in df.columns else list(num_cols[:3])
                x = df[x_column] if x_column and x_column in df.columns else df.index
                for c in cols:
                    ax.plot(x, df[c], label=c, marker='o', markersize=3)
                ax.set_xlabel(x_column or 'Índice')
                ax.set_ylabel('Valor')
                ax.legend()

            elif chart_type == 'scatter':
                num_cols = df.select_dtypes(include=[np.number]).columns
                if len(num_cols) < 2:
                    plt.close(fig)
                    return "❌ ERRO: Scatter exige pelo menos 2 colunas numéricas."
                xc = x_column if x_column in df.columns else num_cols[0]
                yc = y_column if y_column in df.columns else num_cols[1]
                ax.scatter(df[xc], df[yc], alpha=0.5, color='steelblue', edgecolors='none')
                ax.set_xlabel(xc)
                ax.set_ylabel(yc)

            elif chart_type == 'boxplot':
                num_cols = df.select_dtypes(include=[np.number]).columns[:8]
                df[list(num_cols)].boxplot(ax=ax)
                plt.xticks(rotation=45, ha='right')
                ax.set_ylabel('Valor')

            elif chart_type == 'correlation_heatmap':
                num_df = df.select_dtypes(include=[np.number])
                if num_df.shape[1] < 2:
                    plt.close(fig)
                    return "❌ ERRO: Heatmap exige pelo menos 2 colunas numéricas."
                corr = num_df.corr()
                im = ax.imshow(corr, cmap='RdYlGn', vmin=-1, vmax=1)
                plt.colorbar(im, ax=ax)
                ax.set_xticks(range(len(corr.columns)))
                ax.set_yticks(range(len(corr.columns)))
                ax.set_xticklabels(corr.columns, rotation=45, ha='right', fontsize=8)
                ax.set_yticklabels(corr.columns, fontsize=8)
                for i in range(len(corr)):
                    for j in range(len(corr.columns)):
                        ax.text(j, i, f'{corr.iloc[i, j]:.2f}', ha='center', va='center', fontsize=7)

            else:
                plt.close(fig)
                return f"❌ ERRO: Tipo de gráfico '{chart_type}' não suportado."

            ax.set_title(chart_title, fontsize=14, fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.4)
            plt.tight_layout()

            if output_path:
                fig.savefig(output_path, dpi=120, bbox_inches='tight')
                plt.close(fig)
                return f"✅ Gráfico salvo em: {output_path}"
            else:
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
                plt.close(fig)
                buf.seek(0)
                b64 = base64.b64encode(buf.read()).decode('utf-8')
                return f"data:image/png;base64,{b64}"

        except Exception as e:
            plt.close(fig)
            return f"❌ ERRO ao gerar gráfico: {e}"
