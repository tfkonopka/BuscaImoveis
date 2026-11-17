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
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS remetentes (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                nome   TEXT NOT NULL,
                numero TEXT NOT NULL DEFAULT ''
            )
            """
        )
        c.execute(
            "CREATE TABLE IF NOT EXISTS config (chave TEXT PRIMARY KEY, valor TEXT NOT NULL)"
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS contatos (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                imobiliaria_id   TEXT NOT NULL,
                imobiliaria_nome TEXT NOT NULL DEFAULT '',
                remetente_id     INTEGER,
                remetente_nome   TEXT NOT NULL DEFAULT '',
                telefone         TEXT NOT NULL DEFAULT '',
                anuncio_url      TEXT NOT NULL DEFAULT '',
                status           TEXT NOT NULL DEFAULT 'enviada',
                observacao       TEXT NOT NULL DEFAULT '',
                criado_em        TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            )
            """
        )
        c.execute(
            "CREATE INDEX IF NOT EXISTS ix_contatos_imob ON contatos (imobiliaria_id)"
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS itbi_buscas (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nome      TEXT NOT NULL,
                params    TEXT NOT NULL,
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


# ------------------------------------------------- WhatsApp: remetentes, mensagem, contatos
MENSAGEM_PADRAO = (
    "Olá! Meu nome é {remetente}. Vi o anúncio de vocês no ZAP em {bairro} ({link_anuncio}) "
    "e gostaria de saber se há mais imóveis semelhantes disponíveis. Obrigado!"
)


def listar_remetentes() -> list[dict]:
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM remetentes ORDER BY id")]


def criar_remetente(nome: str, numero: str) -> dict:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO remetentes (nome, numero) VALUES (?, ?)", (nome, numero)
        )
        return dict(c.execute("SELECT * FROM remetentes WHERE id = ?", (cur.lastrowid,)).fetchone())


def excluir_remetente(rid: int) -> bool:
    with _conn() as c:
        return c.execute("DELETE FROM remetentes WHERE id = ?", (rid,)).rowcount > 0


def obter_mensagem() -> str:
    with _conn() as c:
        r = c.execute("SELECT valor FROM config WHERE chave = 'mensagem_padrao'").fetchone()
    return r["valor"] if r else MENSAGEM_PADRAO


def salvar_mensagem(texto: str) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO config (chave, valor) VALUES ('mensagem_padrao', ?) "
            "ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor",
            (texto,),
        )


def listar_contatos() -> list[dict]:
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM contatos ORDER BY id DESC")]


def criar_contato(d: dict) -> dict:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO contatos (imobiliaria_id, imobiliaria_nome, remetente_id, remetente_nome,"
            " telefone, anuncio_url, status, observacao) VALUES (?,?,?,?,?,?,?,?)",
            (
                d["imobiliaria_id"], d.get("imobiliaria_nome", ""), d.get("remetente_id"),
                d.get("remetente_nome", ""), d.get("telefone", ""), d.get("anuncio_url", ""),
                d.get("status", "enviada"), d.get("observacao", ""),
            ),
        )
        return dict(c.execute("SELECT * FROM contatos WHERE id = ?", (cur.lastrowid,)).fetchone())


def atualizar_contato(cid: int, status: str | None, observacao: str | None) -> dict | None:
    with _conn() as c:
        if status is not None:
            c.execute("UPDATE contatos SET status = ? WHERE id = ?", (status, cid))
        if observacao is not None:
            c.execute("UPDATE contatos SET observacao = ? WHERE id = ?", (observacao, cid))
        r = c.execute("SELECT * FROM contatos WHERE id = ?", (cid,)).fetchone()
    return dict(r) if r else None


def excluir_contato(cid: int) -> bool:
    with _conn() as c:
        return c.execute("DELETE FROM contatos WHERE id = ?", (cid,)).rowcount > 0


# ------------------------------------------------- ITBI: buscas salvas (só os filtros)
def _busca_itbi(r: sqlite3.Row) -> dict:
    return {"id": r["id"], "nome": r["nome"], "params": json.loads(r["params"]),
            "criado_em": r["criado_em"]}


def listar_buscas_itbi() -> list[dict]:
    with _conn() as c:
        return [_busca_itbi(r) for r in c.execute("SELECT * FROM itbi_buscas ORDER BY id DESC")]


def salvar_busca_itbi(nome: str, params_json: str) -> dict:
    with _conn() as c:
        cur = c.execute("INSERT INTO itbi_buscas (nome, params) VALUES (?, ?)", (nome, params_json))
        return _busca_itbi(c.execute("SELECT * FROM itbi_buscas WHERE id = ?", (cur.lastrowid,)).fetchone())


def excluir_busca_itbi(bid: int) -> bool:
    with _conn() as c:
        return c.execute("DELETE FROM itbi_buscas WHERE id = ?", (bid,)).rowcount > 0
