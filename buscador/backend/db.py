"""Persistência em SQLite: buscas salvas (com snapshot dos imóveis encontrados)."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from models import BuscaParams, BuscaSalva, Imovel

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
                imoveis   TEXT NOT NULL DEFAULT '[]',
                criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            )
            """
        )
        # Migração: adiciona a coluna 'imoveis' em bancos criados antes deste campo.
        cols = {r["name"] for r in c.execute("PRAGMA table_info(buscas_salvas)")}
        if "imoveis" not in cols:
            c.execute(
                "ALTER TABLE buscas_salvas ADD COLUMN imoveis TEXT NOT NULL DEFAULT '[]'"
            )


def _row_to_busca(r: sqlite3.Row) -> BuscaSalva:
    imoveis = [Imovel(**x) for x in json.loads(r["imoveis"] or "[]")]
    return BuscaSalva(
        id=r["id"],
        nome=r["nome"],
        params=BuscaParams(**json.loads(r["params"])),
        imoveis=imoveis,
        total=len(imoveis),
        criado_em=r["criado_em"],
    )


def listar_buscas() -> list[BuscaSalva]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM buscas_salvas ORDER BY criado_em DESC"
        ).fetchall()
    return [_row_to_busca(r) for r in rows]


def salvar_busca(
    nome: str, params: BuscaParams, imoveis: list[Imovel] | None = None
) -> BuscaSalva:
    imoveis = imoveis or []
    imoveis_json = json.dumps([im.model_dump() for im in imoveis], ensure_ascii=False)
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO buscas_salvas (nome, params, imoveis) VALUES (?, ?, ?)",
            (nome, params.model_dump_json(), imoveis_json),
        )
        row = c.execute(
            "SELECT * FROM buscas_salvas WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
    return _row_to_busca(row)


def excluir_busca(bid: int) -> bool:
    with _conn() as c:
        cur = c.execute("DELETE FROM buscas_salvas WHERE id = ?", (bid,))
    return cur.rowcount > 0
