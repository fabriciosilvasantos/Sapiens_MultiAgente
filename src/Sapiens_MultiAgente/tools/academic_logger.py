import logging
import logging.handlers
import json
import os
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid
import yaml


class AcademicAuditor:
    """Sistema de auditoria acadêmica para SAPIENS"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or "src/Sapiens_MultiAgente/config/logging_config.yaml"
        self.config = self._load_config()
        self.sessao_id = str(uuid.uuid4())
        self.usuario_id = "sistema"  # Pode ser sobrescrito por autenticação futura
        self._lock = threading.Lock()
        self._setup_logging()
        self._eventos_auditoria = []

    def _load_config(self) -> Dict[str, Any]:
        """Carrega configurações de logging"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            return {}

    def _setup_logging(self):
        """Configura sistema de logging completo"""
        # Cria diretório de logs se não existir
        os.makedirs("logs", exist_ok=True)

        # Logger principal
        self.logger = logging.getLogger("sapiens_academico")
        self.logger.setLevel(logging.DEBUG)

        # Evita duplicação de handlers
        if self.logger.handlers:
            return

        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.config.get("logging", {}).get("nivel_console", "INFO")))

        # Handler para arquivo com rotação
        file_handler = logging.handlers.RotatingFileHandler(
            "logs/sapiens_academico.log",
            maxBytes=self.config.get("logging", {}).get("rotacao", {}).get("max_bytes", 10485760),
            backupCount=self.config.get("logging", {}).get("rotacao", {}).get("backup_count", 5)
        )
        file_handler.setLevel(getattr(logging, self.config.get("logging", {}).get("nivel_arquivo", "DEBUG")))

        # Formatação
        formatter = logging.Formatter(
            self.config.get("logging", {}).get("formato", {}).get(
                "formato_arquivo",
                "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s"
            )
        )
        console_formatter = logging.Formatter(
            self.config.get("logging", {}).get("formato", {}).get(
                "formato_console",
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(console_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Logger específico para auditoria
        self.auditoria_logger = logging.getLogger("sapiens_auditoria")
        auditoria_handler = logging.FileHandler("logs/auditoria_academica.jsonl")
        auditoria_handler.setLevel(logging.INFO)

        # Formatação JSON para auditoria
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "sessao_id": getattr(record, 'sessao_id', self.sessao_id),
                    "usuario_id": getattr(record, 'usuario_id', self.usuario_id),
                    "nivel": record.levelname,
                    "evento": record.getMessage(),
                    "componente": record.name,
                    "dados_adicionais": getattr(record, 'dados_adicionais', {}),
                    "ip_origem": getattr(record, 'ip_origem', 'localhost'),
                    "user_agent": getattr(record, 'user_agent', 'SAPIENS-System')
                }

                if hasattr(record, 'tempo_execucao_ms'):
                    log_entry["tempo_execucao_ms"] = record.tempo_execucao_ms

                return json.dumps(log_entry, ensure_ascii=False)

        auditoria_handler.setFormatter(JsonFormatter())
        self.auditoria_logger.addHandler(auditoria_handler)
        self.auditoria_logger.propagate = False

    def auditar_evento(
        self,
        evento: str,
        nivel: str = "INFO",
        dados_entrada: Optional[Dict] = None,
        dados_saida: Optional[Dict] = None,
        tempo_execucao_ms: Optional[float] = None,
        **kwargs
    ):
        """Registra evento na auditoria"""
        with self._lock:
            # Cria dicionário do evento
            evento_data = {
                "sessao_id": self.sessao_id,
                "usuario_id": self.usuario_id,
                "evento_tipo": evento,
                "dados_entrada": dados_entrada or {},
                "dados_saida": dados_saida or {},
                "tempo_execucao_ms": tempo_execucao_ms,
                **kwargs
            }

            # Adiciona campos extras obrigatórios
            evento_data.update({
                "ip_origem": kwargs.get("ip_origem", "localhost"),
                "user_agent": kwargs.get("user_agent", "SAPIENS-System"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

            # Armazena evento
            self._eventos_auditoria.append(evento_data)

            # Determina nível de criticidade
            eventos_criticos = self.config.get("auditoria", {}).get("eventos_criticidade_alta", [])
            eventos_medios = self.config.get("auditoria", {}).get("eventos_criticidade_media", [])

            if evento in eventos_criticos:
                self.auditoria_logger.critical(f"Evento crítico: {evento}", extra={
                    "dados_adicionais": evento_data,
                    "sessao_id": self.sessao_id,
                    "usuario_id": self.usuario_id
                })
            elif evento in eventos_medios:
                self.auditoria_logger.warning(f"Evento importante: {evento}", extra={
                    "dados_adicionais": evento_data,
                    "sessao_id": self.sessao_id,
                    "usuario_id": self.usuario_id
                })
            else:
                self.auditoria_logger.info(f"Evento: {evento}", extra={
                    "dados_adicionais": evento_data,
                    "sessao_id": self.sessao_id,
                    "usuario_id": self.usuario_id
                })

            # Também loga no logger geral
            self.logger.info(f"Auditoria - {evento}: {dados_entrada}")

    def iniciar_analise(self, topico_pesquisa: str, dados_fornecidos: Dict = None):
        """Audita início de análise"""
        self.auditar_evento(
            evento="inicio_analise",
            nivel="INFO",
            dados_entrada={
                "topico_pesquisa": topico_pesquisa,
                "dados_fornecidos": dados_fornecidos or {}
            }
        )

    def validar_dados(self, dados_validos: bool, detalhes: str = ""):
        """Audita validação de dados"""
        self.auditar_evento(
            evento="validacao_dados",
            nivel="WARNING" if not dados_validos else "INFO",
            dados_entrada={"dados_validos": dados_validos, "detalhes": detalhes}
        )

    def registrar_erro(self, erro: Exception, contexto: str = ""):
        """Audita erros do sistema"""
        self.auditar_evento(
            evento="erro_sistema",
            nivel="ERROR",
            dados_entrada={
                "erro_tipo": type(erro).__name__,
                "erro_mensagem": str(erro),
                "contexto": contexto
            }
        )

    def finalizar_analise(self, sucesso: bool, resultados: Dict = None):
        """Audita finalização de análise"""
        self.auditar_evento(
            evento="resultado_analise",
            nivel="INFO" if sucesso else "ERROR",
            dados_saida={"sucesso": sucesso, "resultados_resumo": resultados}
        )

    def get_estatisticas_auditoria(self) -> Dict[str, Any]:
        """Retorna estatísticas da sessão de auditoria"""
        return {
            "sessao_id": self.sessao_id,
            "total_eventos": len(self._eventos_auditoria),
            "eventos_por_tipo": self._agrupar_eventos_por_tipo(),
            "tempo_sessao_minutos": self._calcular_tempo_sessao(),
            "usuario_id": self.usuario_id
        }

    def _agrupar_eventos_por_tipo(self) -> Dict[str, int]:
        """Agrupa eventos por tipo"""
        eventos_por_tipo = {}
        for evento in self._eventos_auditoria:
            tipo = evento.get("evento_tipo", "desconhecido")
            eventos_por_tipo[tipo] = eventos_por_tipo.get(tipo, 0) + 1
        return eventos_por_tipo

    def _calcular_tempo_sessao(self) -> float:
        """Calcula tempo da sessão em minutos"""
        if not self._eventos_auditoria:
            return 0.0

        primeiro_evento = min(e.get("timestamp", "") for e in self._eventos_auditoria)
        ultimo_evento = max(e.get("timestamp", "") for e in self._eventos_auditoria)

        try:
            inicio = datetime.fromisoformat(primeiro_evento.replace('Z', '+00:00'))
            fim = datetime.fromisoformat(ultimo_evento.replace('Z', '+00:00'))
            diferenca = fim - inicio
            return diferenca.total_seconds() / 60
        except:
            return 0.0

    def exportar_auditoria_json(self, arquivo_path: str = None):
        """Exporta auditoria para arquivo JSON"""
        if arquivo_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo_path = f"logs/auditoria_export_{timestamp}.json"

        try:
            with open(arquivo_path, 'w', encoding='utf-8') as arquivo:
                json.dump({
                    "metadata": {
                        "sistema": "SAPIENS",
                        "versao": "2.0",
                        "data_exportacao": datetime.now(timezone.utc).isoformat(),
                        "sessao_id": self.sessao_id
                    },
                    "estatisticas": self.get_estatisticas_auditoria(),
                    "eventos": self._eventos_auditoria
                }, arquivo, indent=2, ensure_ascii=False)

            self.logger.info(f"Auditoria exportada para: {arquivo_path}")
            return arquivo_path

        except Exception as e:
            self.logger.error(f"Erro ao exportar auditoria: {e}")
            return None


# Instância global do auditor
auditor_global = AcademicAuditor()


def get_auditor() -> AcademicAuditor:
    """Retorna instância global do auditor"""
    return auditor_global


def auditar_tempo_execucao(func):
    """Decorador para auditar tempo de execução"""
    def wrapper(*args, **kwargs):
        import time
        inicio = time.time()
        try:
            resultado = func(*args, **kwargs)
            tempo_ms = (time.time() - inicio) * 1000
            get_auditor().auditar_evento(
                evento=f"execucao_{func.__name__}",
                dados_entrada={"args_count": len(args), "kwargs_keys": list(kwargs.keys())},
                tempo_execucao_ms=tempo_ms
            )
            return resultado
        except Exception as e:
            tempo_ms = (time.time() - inicio) * 1000
            get_auditor().registrar_erro(e, func.__name__)
            get_auditor().auditar_evento(
                evento=f"erro_{func.__name__}",
                dados_entrada={"erro": str(e)},
                tempo_execucao_ms=tempo_ms
            )
            raise
    return wrapper