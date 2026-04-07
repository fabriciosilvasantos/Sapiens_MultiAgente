import os
import magic
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import hashlib


class DataValidationToolInput(BaseModel):
    """Input schema for DataValidationTool."""
    file_path: str = Field(..., description="Path to the file to be validated")
    max_size_mb: int = Field(default=100, description="Maximum file size in MB")


class DataValidationTool(BaseTool):
    name: str = "DataValidationTool"
    description: str = (
        "Ferramenta para validar arquivos de dados, verificando tipo, tamanho, "
        "integridade e presença de dados pessoais (PII). Usada para garantir "
        "que arquivos fornecidos pelo usuário são válidos e seguros para análise."
    )
    args_schema: Type[BaseModel] = DataValidationToolInput

    def _run(self, file_path: str, max_size_mb: int = 100) -> str:
        """
        Valida um arquivo de dados.

        Args:
            file_path: Caminho para o arquivo
            max_size_mb: Tamanho máximo em MB (padrão 100MB)

        Returns:
            Relatório de validação com detalhes sobre o arquivo
        """
        if not os.path.exists(file_path):
            return f"❌ ERRO: Arquivo não encontrado: {file_path}"

        try:
            # Verificar tamanho do arquivo
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)

            if file_size_mb > max_size_mb:
                return f"❌ ERRO: Arquivo muito grande ({file_size_mb:.2f}MB). Limite: {max_size_mb}MB"

            # Detectar tipo de arquivo usando magic
            mime_type = magic.from_file(file_path, mime=True)
            file_extension = os.path.splitext(file_path)[1].lower()

            # Tipos aceitos
            accepted_types = {
                'text/csv': ['.csv'],
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
                'application/vnd.ms-excel': ['.xls'],
                'application/pdf': ['.pdf'],
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
                'application/msword': ['.doc'],
                'text/plain': ['.txt', '.md']
            }

            # Verificar se o tipo MIME é aceito
            is_accepted = False
            for accepted_mime, extensions in accepted_types.items():
                if mime_type == accepted_mime or file_extension in extensions:
                    is_accepted = True
                    break

            if not is_accepted:
                return f"❌ ERRO: Tipo de arquivo não suportado. MIME: {mime_type}, Extensão: {file_extension}"

            # Calcular hash SHA-256 para integridade
            sha256_hash = self._calculate_sha256(file_path)

            # Verificação básica de conteúdo para PII
            pii_warnings = self._check_pii_indicators(file_path, mime_type)

            # Relatório de validação
            report = f"""
✅ VALIDAÇÃO BEM-SUCEDIDA

📁 Arquivo: {os.path.basename(file_path)}
📊 Tamanho: {file_size_mb:.2f}MB
🏷️ Tipo MIME: {mime_type}
🔒 Hash SHA-256: {sha256_hash}

📋 Status: Arquivo válido para análise
"""

            if pii_warnings:
                report += "\n⚠️ AVISOS DE PII:\n" + "\n".join(pii_warnings)

            return report

        except Exception as e:
            return f"❌ ERRO durante validação: {str(e)}"

    def _calculate_sha256(self, file_path: str) -> str:
        """Calcula hash SHA-256 do arquivo."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _check_pii_indicators(self, file_path: str, mime_type: str) -> list:
        """
        Verifica indicadores básicos de dados pessoais (PII).
        Retorna lista de avisos se detectados.
        """
        warnings = []

        try:
            # Para arquivos de texto, fazer verificação básica
            if mime_type.startswith('text/') or mime_type == 'application/pdf':
                with open(file_path, 'rb') as f:
                    content = f.read(1024).lower()  # Ler primeiros 1KB

                    # Indicadores simples de PII
                    pii_indicators = [
                        b'cpf', b'cnpj', b'rg', b'email', b'telefone', b'celular',
                        b'endereco', b'cep', b'data_nascimento', b'nome_completo'
                    ]

                    for indicator in pii_indicators:
                        if indicator in content:
                            warnings.append(f"Possível dado pessoal detectado: {indicator.decode()}")

        except Exception:
            # Se não conseguir ler, não adicionar avisos
            pass

        return warnings
