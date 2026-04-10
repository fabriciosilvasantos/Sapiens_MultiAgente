"""
Gerenciamento de configuração de LLM para os agentes SAPIENS.

Lê/escreve llm_config.yaml. Suporta modelo global (ativo) e
modelo individual por agente (seção 'agentes'). A troca é efetivada
na próxima execução de análise sem reiniciar o servidor.
"""
import yaml
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent / "llm_config.yaml"


def load_llm_config() -> dict:
    """Retorna o conteúdo completo de llm_config.yaml."""
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_active_model() -> dict:
    """
    Retorna o modelo padrão (ativo) como dict:
    {nome, model_id, temperatura, descricao}
    """
    cfg = load_llm_config()
    ativo = cfg.get("ativo", "gemma_4_moe")
    modelos = cfg.get("modelos", {})
    if ativo not in modelos:
        ativo = next(iter(modelos))
    return modelos[ativo]


def get_model_for_agent(agent_name: str) -> dict:
    """
    Retorna o modelo configurado para um agente específico.
    Se o agente não tiver config individual, usa o modelo padrão (ativo).
    """
    cfg = load_llm_config()
    modelos = cfg.get("modelos", {})
    agentes = cfg.get("agentes", {})

    chave = agentes.get(agent_name) or cfg.get("ativo", "gemma_4_moe")
    if chave not in modelos:
        chave = cfg.get("ativo", next(iter(modelos)))
    return modelos[chave]


def list_models() -> dict:
    """Retorna dict {chave: {nome, model_id, temperatura, descricao}}."""
    return load_llm_config().get("modelos", {})


def get_active_key() -> str:
    """Retorna a chave do modelo padrão ativo (ex: 'gemma_4_moe')."""
    return load_llm_config().get("ativo", "gemma_4_moe")


def set_active_model(chave: str) -> dict:
    """
    Altera o modelo padrão (ativo) no arquivo YAML.
    Retorna o dict do modelo selecionado.
    Lança ValueError se a chave não existir.
    """
    cfg = load_llm_config()
    modelos = cfg.get("modelos", {})
    if chave not in modelos:
        raise ValueError(
            f"Modelo '{chave}' não encontrado. "
            f"Disponíveis: {list(modelos.keys())}"
        )
    cfg["ativo"] = chave
    _save(cfg)
    return modelos[chave]


def set_agent_model(agent_name: str, chave: str) -> dict:
    """
    Atribui um modelo específico a um agente.
    Retorna o dict do modelo selecionado.
    Lança ValueError se a chave não existir.
    """
    cfg = load_llm_config()
    modelos = cfg.get("modelos", {})
    if chave not in modelos:
        raise ValueError(
            f"Modelo '{chave}' não encontrado. "
            f"Disponíveis: {list(modelos.keys())}"
        )
    if "agentes" not in cfg:
        cfg["agentes"] = {}
    cfg["agentes"][agent_name] = chave
    _save(cfg)
    return modelos[chave]


def _save(cfg: dict) -> None:
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
