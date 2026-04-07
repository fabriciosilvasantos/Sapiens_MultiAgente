import os
import re
import magic
import hashlib
import pandas as pd
from typing import Dict, List, Any
from pathlib import Path
import logging
from datetime import datetime


class AcademicSecurityValidator:
    """Validador de segurança para dados acadêmicos sensíveis"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("sapiens_security")

        # Configurações padrão
        self.config_padrao = {
            "max_file_size_mb": 100,
            "allowed_extensions": [".csv", ".xlsx", ".xls", ".pdf", ".docx", ".txt"],
            "blocked_extensions": [".exe", ".bat", ".cmd", ".scr", ".com", ".pif"],
            "require_encryption": False,
            "scan_for_malware": True,
            "validate_pii": True,
            "allowed_mime_types": [
                "text/csv",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel",
                "application/pdf",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "text/plain"
            ]
        }

        # Mescla configurações
        self.config = {**self.config_padrao, **self.config}

        # Padrões de dados pessoais sensíveis (PII)
        self.pii_patterns = {
            "cpf": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
            "telefone": r"\(\d{2}\)\s*\d{4,5}-\d{4}",
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "cep": r"\d{5}-?\d{3}",
            "rg": r"\d{1,2}\.?\d{3}\.?\d{3}-?\d{1}",
            "matricula": r"(?:matr[íi]cula|ra|enrollment)\s*:?\s*[\w\d]+",
            "nome_completo": r"(?:nome|name)\s*:?\s*[A-Za-zÀ-ÿÃÕÑÊÔÛÎÔÂÁÍÓÚÉÇÃ\s]+"
        }

    def validar_arquivo(self, arquivo_path: str) -> Dict[str, Any]:
        """
        Validação completa de segurança para arquivo acadêmico

        Args:
            arquivo_path: Caminho para o arquivo a ser validado

        Returns:
            Dicionário com resultado da validação
        """
        resultado = {
            "arquivo": arquivo_path,
            "valido": True,
            "erros": [],
            "avisos": [],
            "informacoes": {},
            "timestamp": datetime.now().isoformat()
        }

        try:
            # Verifica se arquivo existe
            if not os.path.exists(arquivo_path):
                resultado["valido"] = False
                resultado["erros"].append("Arquivo não encontrado")
                return resultado

            # 1. Validação básica do arquivo
            validacao_basica = self._validar_basico(arquivo_path)
            if not validacao_basica["valido"]:
                resultado["valido"] = False
                resultado["erros"].extend(validacao_basica["erros"])
                return resultado

            resultado["informacoes"].update(validacao_basica["informacoes"])

            # 2. Validação de tipo MIME
            mime_validation = self._validar_mime_type(arquivo_path)
            if not mime_validation["valido"]:
                resultado["valido"] = False
                resultado["erros"].extend(mime_validation["erros"])
            else:
                resultado["avisos"].extend(mime_validation.get("avisos", []))

            # 3. Validação de tamanho
            size_validation = self._validar_tamanho(arquivo_path)
            if not size_validation["valido"]:
                resultado["valido"] = False
                resultado["erros"].extend(size_validation["erros"])
            else:
                resultado["avisos"].extend(size_validation.get("avisos", []))

            # 4. Validação de dados pessoais (PII)
            if self.config.get("validate_pii", True):
                pii_validation = self._validar_pii(arquivo_path)
                resultado["avisos"].extend(pii_validation.get("avisos", []))
                resultado["informacoes"]["pii_encontrada"] = pii_validation.get("pii_encontrada", [])

            # 5. Validação de conteúdo (para arquivos de dados)
            if arquivo_path.lower().endswith(('.csv', '.xlsx', '.xls')):
                content_validation = self._validar_conteudo_dados(arquivo_path)
                if not content_validation["valido"]:
                    resultado["valido"] = False
                    resultado["erros"].extend(content_validation["erros"])
                resultado["avisos"].extend(content_validation.get("avisos", []))

            # 6. Cálculo de hash para auditoria
            hash_result = self._calcular_hash(arquivo_path)
            resultado["informacoes"]["hash_sha256"] = hash_result

        except Exception as e:
            resultado["valido"] = False
            resultado["erros"].append(f"Erro durante validação: {str(e)}")
            self.logger.error(f"Erro na validação de {arquivo_path}: {e}")

        return resultado

    def _validar_basico(self, arquivo_path: str) -> Dict[str, Any]:
        """Validação básica do arquivo"""
        resultado = {"valido": True, "erros": [], "informacoes": {}}

        try:
            # Verifica extensão
            arquivo_ext = Path(arquivo_path).suffix.lower()

            if arquivo_ext in self.config.get("blocked_extensions", []):
                resultado["valido"] = False
                resultado["erros"].append(f"Extensão bloqueada: {arquivo_ext}")
                return resultado

            if arquivo_ext not in self.config.get("allowed_extensions", []):
                resultado["valido"] = False
                resultado["erros"].append(f"Extensão não permitida: {arquivo_ext}")
                return resultado

            # Verifica se é arquivo regular
            if not os.path.isfile(arquivo_path):
                resultado["valido"] = False
                resultado["erros"].append("Caminho não é um arquivo válido")
                return resultado

            # Informações básicas
            stat = os.stat(arquivo_path)
            resultado["informacoes"] = {
                "tamanho_bytes": stat.st_size,
                "data_modificacao": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extensao": arquivo_ext
            }

        except Exception as e:
            resultado["valido"] = False
            resultado["erros"].append(f"Erro na validação básica: {str(e)}")

        return resultado

    def _validar_mime_type(self, arquivo_path: str) -> Dict[str, Any]:
        """Validação de tipo MIME"""
        resultado = {"valido": True, "erros": [], "avisos": []}

        try:
            # Detecta MIME type
            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(arquivo_path)

            resultado["informacoes"] = {"mime_type_detectado": mime_type}

            # Verifica se MIME type é permitido
            if mime_type not in self.config.get("allowed_mime_types", []):
                resultado["valido"] = False
                resultado["erros"].append(f"Tipo MIME não permitido: {mime_type}")
            else:
                resultado["avisos"].append(f"MIME type validado: {mime_type}")

        except Exception as e:
            resultado["valido"] = False
            resultado["erros"].append(f"Erro na detecção MIME: {str(e)}")

        return resultado

    def _validar_tamanho(self, arquivo_path: str) -> Dict[str, Any]:
        """Validação de tamanho do arquivo"""
        resultado = {"valido": True, "erros": [], "avisos": []}

        try:
            tamanho_bytes = os.path.getsize(arquivo_path)
            tamanho_mb = tamanho_bytes / (1024 * 1024)

            resultado["informacoes"] = {"tamanho_mb": round(tamanho_mb, 2)}

            # Verifica tamanho máximo
            max_size = self.config.get("max_file_size_mb", 100)
            if tamanho_mb > max_size:
                resultado["valido"] = False
                resultado["erros"].append(f"Arquivo muito grande: {tamanho_mb:.2f}MB (máximo: {max_size}MB)")
            elif tamanho_mb > (max_size * 0.8):  # 80% do limite
                resultado["avisos"].append(f"Arquivo grande: {tamanho_mb:.2f}MB (aproximando limite de {max_size}MB)")

        except Exception as e:
            resultado["valido"] = False
            resultado["erros"].append(f"Erro na validação de tamanho: {str(e)}")

        return resultado

    def _validar_pii(self, arquivo_path: str) -> Dict[str, Any]:
        """Validação de dados pessoais sensíveis (PII)"""
        resultado = {"valido": True, "erros": [], "avisos": [], "pii_encontrada": []}

        try:
            # Lê conteúdo do arquivo
            with open(arquivo_path, 'r', encoding='utf-8', errors='ignore') as arquivo:
                conteudo = arquivo.read()

            # Busca padrões PII
            pii_encontrada = []
            for pii_type, pattern in self.pii_patterns.items():
                matches = re.findall(pattern, conteudo, re.IGNORECASE)
                if matches:
                    pii_encontrada.append({
                        "tipo": pii_type,
                        "quantidade": len(matches),
                        "exemplos": matches[:3]  # Mostra apenas primeiros 3 exemplos
                    })

            resultado["pii_encontrada"] = pii_encontrada

            if pii_encontrada:
                resultado["avisos"].append(f"Dados pessoais detectados: {[p['tipo'] for p in pii_encontrada]}")

        except Exception as e:
            resultado["avisos"].append(f"Erro na validação PII: {str(e)}")

        return resultado

    def _validar_conteudo_dados(self, arquivo_path: str) -> Dict[str, Any]:
        """Validação específica para arquivos de dados (CSV, Excel)"""
        resultado = {"valido": True, "erros": [], "avisos": []}

        try:
            arquivo_ext = Path(arquivo_path).suffix.lower()

            if arquivo_ext == '.csv':
                df = pd.read_csv(arquivo_path)
            elif arquivo_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(arquivo_path)
            else:
                return resultado

            # Validações de qualidade dos dados
            total_celulas = df.size
            celulas_vazias = df.isnull().sum().sum()
            percentual_vazio = (celulas_vazias / total_celulas) * 100

            resultado["informacoes"] = {
                "linhas": len(df),
                "colunas": len(df.columns),
                "celulas_vazias": celulas_vazias,
                "percentual_dados_faltantes": round(percentual_vazio, 2)
            }

            # Avisos para qualidade
            if percentual_vazio > 50:
                resultado["avisos"].append(f"Muitos dados faltantes: {percentual_vazio:.1f}%")
            elif percentual_vazio > 20:
                resultado["avisos"].append(f"Dados faltantes significativos: {percentual_vazio:.1f}%")

        except Exception as e:
            resultado["valido"] = False
            resultado["erros"].append(f"Erro na validação de conteúdo: {str(e)}")

        return resultado

    def _calcular_hash(self, arquivo_path: str) -> str:
        """Calcula hash SHA-256 do arquivo para auditoria"""
        try:
            sha256 = hashlib.sha256()
            with open(arquivo_path, 'rb') as arquivo:
                for bloco in iter(lambda: arquivo.read(4096), b""):
                    sha256.update(bloco)
            return sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Erro ao calcular hash: {e}")
            return ""

    def validar_multiplos_arquivos(self, arquivos: List[str]) -> Dict[str, Any]:
        """Valida múltiplos arquivos"""
        resultado = {
            "total_arquivos": len(arquivos),
            "arquivos_validos": 0,
            "arquivos_invalidos": 0,
            "resultados": [],
            "timestamp": datetime.now().isoformat()
        }

        for arquivo in arquivos:
            validacao = self.validar_arquivo(arquivo)
            resultado["resultados"].append(validacao)

            if validacao["valido"]:
                resultado["arquivos_validos"] += 1
            else:
                resultado["arquivos_invalidos"] += 1

        resultado["taxa_sucesso"] = (resultado["arquivos_validos"] / resultado["total_arquivos"]) * 100

        return resultado

    def gerar_relatorio_seguranca(self, resultado_validacao: Dict[str, Any]) -> str:
        """Gera relatório de segurança em formato legível"""
        relatorio = []
        relatorio.append("=" * 60)
        relatorio.append("RELATÓRIO DE VALIDAÇÃO DE SEGURANÇA - SAPIENS")
        relatorio.append("=" * 60)
        relatorio.append(f"Arquivo: {resultado_validacao['arquivo']}")
        relatorio.append(f"Data: {resultado_validacao['timestamp']}")
        relatorio.append(f"Status: {'✅ VÁLIDO' if resultado_validacao['valido'] else '❌ INVÁLIDO'}")
        relatorio.append("")

        if resultado_validacao["erros"]:
            relatorio.append("🚨 ERROS ENCONTRADOS:")
            for erro in resultado_validacao["erros"]:
                relatorio.append(f"  • {erro}")
            relatorio.append("")

        if resultado_validacao["avisos"]:
            relatorio.append("⚠️  AVISOS:")
            for aviso in resultado_validacao["avisos"]:
                relatorio.append(f"  • {aviso}")
            relatorio.append("")

        if resultado_validacao["informacoes"]:
            relatorio.append("📊 INFORMAÇÕES:")
            for chave, valor in resultado_validacao["informacoes"].items():
                relatorio.append(f"  • {chave}: {valor}")
            relatorio.append("")

        relatorio.append("=" * 60)

        return "\n".join(relatorio)


# Função utilitária global
def validar_seguranca_arquivo(arquivo_path: str) -> Dict[str, Any]:
    """Função utilitária para validar arquivo"""
    validator = AcademicSecurityValidator()
    return validator.validar_arquivo(arquivo_path)
