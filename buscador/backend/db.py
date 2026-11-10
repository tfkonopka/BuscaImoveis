"""Persistência em SQLite: buscas salvas."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional

from models import BuscaParams, BuscaSalva

DB_PATH = Path(__file__).with_name("buscador.db")


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db() -> None:
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS buscas_salvas (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nome      TEXT NOT NULL,
                params    TEXT NOT NULL,
                criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            )
            """
        )


def listar_buscas() -> list[BuscaSalva]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM buscas_salvas ORDER BY criado_em DESC"
        ).fetchall()
    return [
        BuscaSalva(
            id=r["id"],
            nome=r["nome"],
            params=BuscaParams(**json.loads(r["params"])),
            criado_em=r["criado_em"],
        )
        for r in rows
    ]


def salvar_busca(nome: str, params: BuscaParams) -> BuscaSalva:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO buscas_salvas (nome, params) VALUES (?, ?)",
            (nome, params.model_dump_json()),
        )
        bid = cur.lastrowid
        row = c.execute(
            "SELECT * FROM buscas_salvas WHERE id = ?", (bid,)
        ).fetchone()
    return BuscaSalva(
        id=row["id"],
        nome=row["nome"],
        params=BuscaParams(**json.loads(row["params"])),
        criado_em=row["criado_em"],
    )


def excluir_busca(bid: int) -> bool:
    with _conn() as c:
        cur = c.execute("DELETE FROM buscas_salvas WHERE id = ?", (bid,))
    return cur.rowcount > 0
