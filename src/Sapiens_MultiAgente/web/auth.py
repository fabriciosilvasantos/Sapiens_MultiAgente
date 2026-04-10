"""
Módulo de autenticação SAPIENS.
Gerencia usuários, sessões e controle de acesso.
"""

import os
import hashlib
import secrets
import sqlite3
import time
from collections import defaultdict
from datetime import datetime
from flask_login import LoginManager, UserMixin

# Reutiliza o mesmo DB_PATH definido em app.py via variável de ambiente
DB_PATH = os.getenv('SAPIENS_DB_PATH', 'sapiens.db')

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'

# Rastreamento de tentativas de login falhas (proteção por força bruta)
# Estrutura: {username: [(timestamp, ...), ...]}
_falhas_login: dict[str, list[float]] = defaultdict(list)
_MAX_TENTATIVAS = 5        # tentativas antes do bloqueio
_JANELA_BLOQUEIO = 300     # segundos (5 minutos)


def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _hash_senha(senha: str, salt: str) -> str:
    """Hash PBKDF2-SHA256 com salt individual por usuário (100 000 iterações)."""
    dk = hashlib.pbkdf2_hmac(
        'sha256',
        senha.encode('utf-8'),
        salt.encode('utf-8'),
        100_000,
    )
    return dk.hex()


def _hash_senha_legado(senha: str) -> str:
    """Hash SHA-256 simples usado no formato antigo (apenas para migração)."""
    salt = os.getenv('SAPIENS_PASSWORD_SALT', 'sapiens-salt-padrao')
    return hashlib.sha256(f"{salt}{senha}".encode()).hexdigest()


def verificar_bloqueio(username: str) -> tuple[bool, int]:
    """
    Verifica se o usuário está bloqueado por excesso de tentativas.
    Retorna (bloqueado, segundos_restantes).
    """
    agora = time.time()
    # Remove registros fora da janela
    _falhas_login[username] = [
        t for t in _falhas_login[username]
        if agora - t < _JANELA_BLOQUEIO
    ]
    falhas = len(_falhas_login[username])
    if falhas >= _MAX_TENTATIVAS:
        mais_recente = max(_falhas_login[username])
        restante = int(_JANELA_BLOQUEIO - (agora - mais_recente))
        return True, max(0, restante)
    return False, 0


def _registrar_falha(username: str):
    _falhas_login[username].append(time.time())


def _limpar_falhas(username: str):
    _falhas_login.pop(username, None)


def init_auth_db():
    """Cria tabela de usuários (com migração para coluna salt) e insere admin padrão."""
    with _get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT UNIQUE NOT NULL,
                senha_hash  TEXT NOT NULL,
                salt        TEXT NOT NULL DEFAULT '',
                nome        TEXT NOT NULL,
                admin       INTEGER NOT NULL DEFAULT 0,
                criado_em   TEXT NOT NULL
            )
        """)
        # Migração: adiciona coluna salt se não existir (deployments antigos)
        try:
            conn.execute("ALTER TABLE usuarios ADD COLUMN salt TEXT NOT NULL DEFAULT ''")
        except Exception:
            pass  # coluna já existe
        conn.commit()

        # Cria admin padrão se não existir nenhum usuário
        existe = conn.execute("SELECT 1 FROM usuarios LIMIT 1").fetchone()
        if not existe:
            senha_padrao = os.getenv('SAPIENS_ADMIN_PASSWORD')
            if not senha_padrao:
                import logging
                senha_padrao = secrets.token_urlsafe(16)
                logging.getLogger(__name__).warning(
                    "SAPIENS_ADMIN_PASSWORD não definida. "
                    "Senha gerada: %s  — altere após o primeiro login!",
                    senha_padrao,
                )
            novo_salt = secrets.token_hex(32)
            conn.execute("""
                INSERT INTO usuarios (username, senha_hash, salt, nome, admin, criado_em)
                VALUES (?, ?, ?, ?, 1, ?)
            """, ('admin', _hash_senha(senha_padrao, novo_salt), novo_salt,
                  'Administrador', datetime.now().isoformat()))
            conn.commit()


class Usuario(UserMixin):
    """Modelo de usuário para Flask-Login."""

    def __init__(self, id: int, username: str, nome: str, admin: bool):
        self.id = str(id)
        self.username = username
        self.nome = nome
        self.admin = admin

    @staticmethod
    def buscar_por_id(user_id: str):
        try:
            with _get_db() as conn:
                row = conn.execute(
                    "SELECT * FROM usuarios WHERE id = ?", (int(user_id),)
                ).fetchone()
            if row:
                return Usuario(row['id'], row['username'], row['nome'], bool(row['admin']))
        except Exception:
            pass
        return None

    @staticmethod
    def autenticar(username: str, senha: str):
        """
        Autentica o usuário. Verifica bloqueio antes de consultar o banco.
        Migra automaticamente hashes no formato legado para PBKDF2.
        """
        bloqueado, restante = verificar_bloqueio(username)
        if bloqueado:
            return None, f"Conta bloqueada. Tente novamente em {restante}s."

        try:
            with _get_db() as conn:
                row = conn.execute(
                    "SELECT * FROM usuarios WHERE username = ?", (username,)
                ).fetchone()

            if not row:
                _registrar_falha(username)
                return None, "Credenciais inválidas."

            salt = row['salt'] or ''
            autenticado = False

            if salt:
                # Formato novo: PBKDF2 com salt por usuário
                autenticado = row['senha_hash'] == _hash_senha(senha, salt)
            else:
                # Formato legado: SHA-256 com salt global
                autenticado = row['senha_hash'] == _hash_senha_legado(senha)
                if autenticado:
                    # Migra para PBKDF2
                    novo_salt = secrets.token_hex(32)
                    novo_hash = _hash_senha(senha, novo_salt)
                    with _get_db() as conn:
                        conn.execute(
                            "UPDATE usuarios SET senha_hash = ?, salt = ? WHERE id = ?",
                            (novo_hash, novo_salt, row['id'])
                        )
                        conn.commit()

            if autenticado:
                _limpar_falhas(username)
                return Usuario(row['id'], row['username'], row['nome'], bool(row['admin'])), None

            _registrar_falha(username)
            _, restante = verificar_bloqueio(username)
            tentativas_restantes = max(0, _MAX_TENTATIVAS - len(_falhas_login[username]))
            if tentativas_restantes == 0:
                return None, f"Conta bloqueada por {_JANELA_BLOQUEIO // 60} minutos."
            return None, f"Credenciais inválidas. {tentativas_restantes} tentativa(s) restante(s)."

        except Exception:
            return None, "Erro interno de autenticação."

    @staticmethod
    def criar(username: str, senha: str, nome: str, admin: bool = False):
        """Cria novo usuário com PBKDF2. Retorna True se criado, False se username já existe."""
        try:
            novo_salt = secrets.token_hex(32)
            with _get_db() as conn:
                conn.execute("""
                    INSERT INTO usuarios (username, senha_hash, salt, nome, admin, criado_em)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username, _hash_senha(senha, novo_salt), novo_salt,
                      nome, int(admin), datetime.now().isoformat()))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


@login_manager.user_loader
def carregar_usuario(user_id: str):
    return Usuario.buscar_por_id(user_id)
