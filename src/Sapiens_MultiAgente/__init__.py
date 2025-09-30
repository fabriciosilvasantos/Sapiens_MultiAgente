# SAPIENS - Plataforma Acadêmica Multiagente de Análise de Dados
"""
Plataforma acadêmica avançada para análise de dados usando múltiplos agentes especializados.
"""

__version__ = "2.0.0"
__author__ = "Fabricio Silva Santos"

from . import crew, main, web
from .crew import SapiensAcademicMultiAgentDataAnalysisPlatformCrew

__all__ = [
    'crew',
    'main',
    'web',
    'SapiensAcademicMultiAgentDataAnalysisPlatformCrew'
]