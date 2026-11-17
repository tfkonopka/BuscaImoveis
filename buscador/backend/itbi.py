"""Consulta às transações de ITBI importadas (itbi.db, gerado por itbi_import.py)."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from statistics import median
from typing import Optional

from pydantic import BaseModel, Field

import geo
from models import Localizacao

DB_PATH = Path(__file__).with_name("itbi.db")

COLUNAS = ("id, ano, mes, periodo, bairro, zona, cl, logradouro, numero, complemento, "
           "tipologia, utilizacao, parte, valor, area, valor_m2, lat, lon, prec")


class ItbiParams(BaseModel):
    """Filtros da aba ITBI. `localizacao` tem a mesma forma da busca de anúncios;
    zona vazia ("") = cidade inteira."""

    localizacao: Localizacao = Field(default_factory=Localizacao)
    numero: Optional[str] = None            # só no modo rua: número do imóvel
    area_min: Optional[float] = None
    area_max: Optional[float] = None
    valor_min: Optional[float] = None
    valor_max: Optional[float] = None
    periodo_ini: Optional[int] = None       # AAAAMM
    periodo_fim: Optional[int] = None       # AAAAMM
    tipologias: list[str] = Field(default_factory=list)
    utilizacoes: list[str] = Field(default_factory=list)
    limite: int = 2000                      # teto de linhas devolvidas (as mais recentes)


def disponivel() -> bool:
    if not DB_PATH.exists():
        return False
    with sqlite3.connect(DB_PATH) as c:
        return bool(c.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='itbi'").fetchone())


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def meta() -> dict:
    if not disponivel():
        return {"disponivel": False}
    with _conn() as c:
        tot, pmin, pmax = c.execute("SELECT COUNT(*), MIN(periodo), MAX(periodo) FROM itbi").fetchone()
        tipos = [dict(r) for r in c.execute(
            "SELECT tipologia AS nome, COUNT(*) AS n FROM itbi GROUP BY tipologia ORDER BY n DESC")]
        usos = [dict(r) for r in c.execute(
            "SELECT utilizacao AS nome, COUNT(*) AS n FROM itbi GROUP BY utilizacao ORDER BY n DESC")]
        bairros = [r[0] for r in c.execute(
            "SELECT DISTINCT bairro FROM itbi WHERE bairro <> '' ORDER BY bairro")]
        imp = c.execute("SELECT valor FROM itbi_meta WHERE chave='importado_em'").fetchone()
    return {"disponivel": True, "total": tot, "periodo_min": pmin, "periodo_max": pmax,
            "tipologias": tipos, "utilizacoes": usos, "bairros": bairros,
            "importado_em": imp[0] if imp else None}


def _where(p: ItbiParams) -> tuple[str, list]:
    cond, args = [], []

    def add(sql: str, *vals) -> None:
        cond.append(sql)
        args.extend(vals)

    loc = p.localizacao
    if loc.tipo == "zona":
        if loc.zona:
            add("zona = ?", loc.zona)
    elif loc.tipo == "bairro":
        alvos = [geo.normalizar(b) for b in loc.bairros if b.strip()]
        if alvos:
            add(f"bairro_norm IN ({','.join('?' * len(alvos))})", *alvos)
    elif loc.tipo == "rua":
        if loc.rua:
            add("rua_norm LIKE ?", f"%{geo.normalizar(loc.rua)}%")
        if p.numero and p.numero.strip():
            add("numero = ?", p.numero.strip())
    elif loc.tipo == "poligono" and len(loc.poligono) >= 3:
        lats = [pt[0] for pt in loc.poligono]
        lons = [pt[1] for pt in loc.poligono]
        add("lat BETWEEN ? AND ? AND lon BETWEEN ? AND ?", min(lats), max(lats), min(lons), max(lons))

    if p.area_min is not None:
        add("area >= ?", p.area_min)
    if p.area_max is not None:
        add("area <= ?", p.area_max)
    if p.valor_min is not None:
        add("valor >= ?", p.valor_min)
    if p.valor_max is not None:
        add("valor <= ?", p.valor_max)
    if p.periodo_ini:
        add("periodo >= ?", p.periodo_ini)
    if p.periodo_fim:
        add("periodo <= ?", p.periodo_fim)
    if p.tipologias:
        add(f"tipologia IN ({','.join('?' * len(p.tipologias))})", *p.tipologias)
    if p.utilizacoes:
        add(f"utilizacao IN ({','.join('?' * len(p.utilizacoes))})", *p.utilizacoes)
    return (" WHERE " + " AND ".join(cond)) if cond else "", args


def _quantil(ordenado: list[float], q: float) -> Optional[float]:
    if not ordenado:
        return None
    return ordenado[min(len(ordenado) - 1, int(q * len(ordenado)))]


def buscar(p: ItbiParams) -> dict:
    where, args = _where(p)
    poligono = p.localizacao.poligono if p.localizacao.tipo == "poligono" else None
    limite = max(1, min(p.limite, 20000))
    linhas, m2s, valores = [], [], []
    por_ano: dict[int, list[float]] = {}
    total = sem_coord = 0
    with _conn() as c:
        cur = c.execute(f"SELECT {COLUNAS} FROM itbi{where} ORDER BY periodo DESC, id DESC", args)
        for r in cur:
            if poligono and not geo.dentro_do_poligono(r["lat"], r["lon"], poligono):
                continue
            total += 1
            valores.append(r["valor"])
            if r["valor_m2"]:
                m2s.append(r["valor_m2"])
                por_ano.setdefault(r["ano"], []).append(r["valor_m2"])
            if r["lat"] is None:
                sem_coord += 1
            if len(linhas) < limite:
                linhas.append(dict(r))
    m2s.sort()
    return {
        "total": total,
        "exibidos": len(linhas),
        "sem_coordenada": sem_coord,
        "stats": {
            "m2_mediana": _quantil(m2s, 0.5), "m2_p25": _quantil(m2s, 0.25), "m2_p75": _quantil(m2s, 0.75),
            "m2_media": (sum(m2s) / len(m2s)) if m2s else None,
            "valor_mediana": median(valores) if valores else None,
        },
        "por_ano": [{"ano": a, "n": len(v), "m2_mediana": median(v)} for a, v in sorted(por_ano.items())],
        "transacoes": linhas,
    }
