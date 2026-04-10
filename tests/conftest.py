"""
Configuração global de testes SAPIENS.

Garante que variáveis de ambiente necessárias estejam definidas antes de
qualquer fixture ou teste ser executado, sem hardcodar senhas no código.
"""
import os
import secrets


def pytest_configure(config):
    """Define SAPIENS_ADMIN_PASSWORD com valor aleatório se não estiver no ambiente."""
    if not os.environ.get('SAPIENS_ADMIN_PASSWORD'):
        os.environ['SAPIENS_ADMIN_PASSWORD'] = secrets.token_urlsafe(12)
