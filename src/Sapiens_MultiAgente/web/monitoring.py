"""
Módulo de monitoramento da plataforma SAPIENS.

Coleta métricas do sistema (CPU, memória, disco) e do banco de dados
(contagem de análises) em intervalos regulares via thread background.
"""

import sqlite3
import threading
import time
from collections import deque
from datetime import datetime

try:
    import psutil
    _PSUTIL_OK = True
except ImportError:
    _PSUTIL_OK = False


class SapiensMonitor:
    """Coleta métricas da plataforma a cada 30 s em background."""

    INTERVAL = 30  # segundos entre coletas

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._history: deque = deque(maxlen=120)  # ~60 min de histórico
        self._lock = threading.Lock()
        self._running = False
        self._start_time = datetime.now().isoformat()

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Inicia a coleta em thread daemon (não bloqueia o servidor)."""
        if self._running:
            return
        self._running = True
        # Coleta inicial imediata
        self._collect()
        t = threading.Thread(target=self._collect_loop, daemon=True, name="sapiens-monitor")
        t.start()

    def stop(self) -> None:
        self._running = False

    # ------------------------------------------------------------------
    # Loop de coleta
    # ------------------------------------------------------------------

    def _collect_loop(self) -> None:
        while self._running:
            time.sleep(self.INTERVAL)
            if self._running:
                self._collect()

    def _collect(self) -> None:
        snap = self._snapshot()
        with self._lock:
            self._history.append(snap)

    def _snapshot(self) -> dict:
        snap: dict = {
            "ts": datetime.now().isoformat(),
            "cpu_pct": None,
            "mem_pct": None,
            "mem_used_mb": None,
            "disk_pct": None,
            "disk_free_gb": None,
            "analises_total": 0,
            "analises_ok": 0,
            "analises_erro": 0,
            "analises_em_andamento": 0,
            "uptime_inicio": self._start_time,
        }

        # Métricas de sistema
        if _PSUTIL_OK:
            try:
                snap["cpu_pct"] = psutil.cpu_percent(interval=0.5)
                mem = psutil.virtual_memory()
                snap["mem_pct"] = mem.percent
                snap["mem_used_mb"] = round(mem.used / 1024 / 1024, 1)
                disk = psutil.disk_usage("/")
                snap["disk_pct"] = disk.percent
                snap["disk_free_gb"] = round(disk.free / 1024 / 1024 / 1024, 2)
            except Exception:
                pass

        # Métricas do banco de dados
        try:
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                row = conn.execute(
                    """SELECT
                        COUNT(*),
                        SUM(CASE WHEN status = 'concluida' THEN 1 ELSE 0 END),
                        SUM(CASE WHEN status = 'erro'      THEN 1 ELSE 0 END),
                        SUM(CASE WHEN status NOT IN ('concluida','erro') THEN 1 ELSE 0 END)
                    FROM analises"""
                ).fetchone()
                if row:
                    snap["analises_total"] = row[0] or 0
                    snap["analises_ok"] = row[1] or 0
                    snap["analises_erro"] = row[2] or 0  # noqa: F841
                    snap["analises_em_andamento"] = row[3] or 0
        except Exception:
            pass

        return snap

    # ------------------------------------------------------------------
    # Acesso às métricas
    # ------------------------------------------------------------------

    def current(self) -> dict:
        """Retorna o snapshot mais recente (coleta síncrona se vazio)."""
        with self._lock:
            if self._history:
                return dict(self._history[-1])
        return self._snapshot()

    def history(self, last_n: int = 20) -> list:
        """Retorna os últimos N snapshots."""
        with self._lock:
            snaps = list(self._history)
        return snaps[-last_n:]

    def summary(self) -> dict:
        """Retorna resumo com status semáforo (ok / aviso / critico)."""
        snap = self.current()
        total = snap["analises_total"]
        ok = snap["analises_ok"]
        taxa_sucesso = round(ok / total * 100, 1) if total else 100.0

        def nivel(pct: float | None, warn: float = 70, crit: float = 90) -> str:
            if pct is None:
                return "desconhecido"
            if pct >= crit:
                return "critico"
            if pct >= warn:
                return "aviso"
            return "ok"

        return {
            **snap,
            "taxa_sucesso_analises": taxa_sucesso,
            "nivel_cpu": nivel(snap["cpu_pct"]),
            "nivel_mem": nivel(snap["mem_pct"]),
            "nivel_disk": nivel(snap["disk_pct"]),
        }
