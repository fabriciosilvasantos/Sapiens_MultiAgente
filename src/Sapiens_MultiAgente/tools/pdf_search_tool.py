import os
from typing import Type, Optional, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import re
try:
    from PyPDF2 import PdfReader
except ImportError:
    # Fallback se PyPDF2 não estiver disponível
    PdfReader = None


class PDFSearchToolInput(BaseModel):
    """Input schema for PDFSearchTool."""
    file_path: str = Field(..., description="Path to the PDF file to search")
    search_query: Optional[str] = Field(default=None, description="Text to search for (case-insensitive)")
    page_range: Optional[str] = Field(default=None, description="Page range to search (e.g., '1-5' or 'all')")
    extract_text: bool = Field(default=False, description="Extract all text from the PDF")


class PDFSearchTool(BaseTool):
    name: str = "PDFSearchTool"
    description: str = (
        "Ferramenta para buscar e extrair texto de arquivos PDF. Permite pesquisa "
        "de termos específicos, extração de texto completo ou por páginas, "
        "e análise de conteúdo em documentos acadêmicos."
    )
    args_schema: Type[BaseModel] = PDFSearchToolInput

    def _run(self, file_path: str, search_query: Optional[str] = None,
             page_range: Optional[str] = None, extract_text: bool = False) -> str:
        """
        Busca ou extrai texto de um arquivo PDF.

        Args:
            file_path: Caminho para o arquivo PDF
            search_query: Termo a buscar (opcional)
            page_range: Intervalo de páginas (opcional)
            extract_text: Se deve extrair todo o texto

        Returns:
            Resultados da busca ou extração
        """
        if not os.path.exists(file_path):
            return f"❌ ERRO: Arquivo PDF não encontrado: {file_path}"

        if PdfReader is None:
            return "❌ ERRO: Biblioteca PyPDF2 não está instalada. Instale com: pip install PyPDF2"

        try:
            # Abrir PDF
            reader = PdfReader(file_path)
            num_pages = len(reader.pages)

            # Processar intervalo de páginas
            pages_to_process = self._parse_page_range(page_range, num_pages)

            # Extrair texto se solicitado
            if extract_text:
                return self._extract_full_text(reader, pages_to_process)

            # Buscar termo específico
            if search_query:
                return self._search_text(reader, search_query, pages_to_process)

            # Se nada especificado, retornar informações básicas
            return self._get_pdf_info(reader, file_path)

        except Exception as e:
            return f"❌ ERRO ao processar PDF: {str(e)}"

    def _parse_page_range(self, page_range: Optional[str], total_pages: int) -> List[int]:
        """Parse do intervalo de páginas."""
        if not page_range or page_range.lower() == 'all':
            return list(range(total_pages))

        try:
            if '-' in page_range:
                start, end = map(int, page_range.split('-'))
                start = max(0, start - 1)  # Converter para índice 0-based
                end = min(total_pages, end)  # Não exceder total de páginas
                return list(range(start, end))
            else:
                page = int(page_range) - 1  # 0-based
                return [max(0, min(page, total_pages - 1))]
        except:
            return list(range(total_pages))

    def _extract_full_text(self, reader: PdfReader, pages: List[int]) -> str:
        """Extrai todo o texto do PDF."""
        extracted_text = []

        for page_num in pages:
            try:
                page = reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    extracted_text.append(f"--- PÁGINA {page_num + 1} ---\n{text.strip()}")
            except Exception as e:
                extracted_text.append(f"--- PÁGINA {page_num + 1} --- (Erro: {str(e)})")

        if not extracted_text:
            return "❌ NENHUM TEXTO EXTRAÍDO do PDF. O arquivo pode conter apenas imagens ou estar protegido."

        return f"📄 TEXTO EXTRAÍDO DO PDF\n\n" + "\n\n".join(extracted_text)

    def _search_text(self, reader: PdfReader, query: str, pages: List[int]) -> str:
        """Busca por termo específico no PDF."""
        results = []
        query_lower = query.lower()

        for page_num in pages:
            try:
                page = reader.pages[page_num]
                text = page.extract_text()

                if text and query_lower in text.lower():
                    # Encontrar contexto ao redor da ocorrência
                    lines = text.split('\n')
                    matching_lines = []

                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            # Obter linhas de contexto
                            start = max(0, i - 2)
                            end = min(len(lines), i + 3)
                            context = '\n'.join(lines[start:end])
                            matching_lines.append(f"...{context}...")

                    if matching_lines:
                        results.append(f"📍 PÁGINA {page_num + 1}:\n" + '\n\n'.join(matching_lines))

            except Exception as e:
                results.append(f"📍 PÁGINA {page_num + 1}: Erro ao processar - {str(e)}")

        if not results:
            return f"🔍 TERMO NÃO ENCONTRADO: '{query}' não foi encontrado no PDF."

        total_occurrences = len(results)
        return f"🔍 RESULTADOS DA BUSCA POR '{query}'\n\nEncontrado em {total_occurrences} página(s):\n\n" + "\n\n".join(results)

    def _get_pdf_info(self, reader: PdfReader, file_path: str) -> str:
        """Retorna informações básicas do PDF."""
        num_pages = len(reader.pages)

        # Tentar extrair metadados
        metadata = {}
        try:
            if reader.metadata:
                metadata = {
                    'autor': reader.metadata.author,
                    'titulo': reader.metadata.title,
                    'assunto': reader.metadata.subject,
                    'criador': reader.metadata.creator,
                    'produtor': reader.metadata.producer,
                    'data_criacao': reader.metadata.creation_date,
                    'data_modificacao': reader.metadata.modification_date
                }
        except:
            pass

        info = f"""
📕 INFORMAÇÕES DO PDF

📁 Arquivo: {os.path.basename(file_path)}
📄 Número de páginas: {num_pages}

📋 METADADOS:
"""

        for key, value in metadata.items():
            if value:
                info += f"• {key.title()}: {value}\n"

        if not any(metadata.values()):
            info += "Nenhum metadado disponível.\n"

        # Preview da primeira página
        try:
            first_page = reader.pages[0]
            first_page_text = first_page.extract_text()[:500]  # Primeiros 500 caracteres
            if first_page_text.strip():
                info += f"\n👀 PREVIEW DA PRIMEIRA PÁGINA:\n{first_page_text}...\n"
        except:
            info += "\n👀 Preview não disponível.\n"

        return info