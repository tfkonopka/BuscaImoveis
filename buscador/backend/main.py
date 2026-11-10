"""API do buscador de imóveis (FastAPI).

A busca só roda quando o endpoint POST /api/buscar é chamado (sob demanda).
Serve também o frontend estático em '/'.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import db
import geo
from models import BuscaParams, Imovel
from scrapers import SCRAPERS, get_scraper

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="Buscador de Imóveis RJ", version="0.1.0")


@app.on_event("startup")
def _startup() -> None:
    db.init_db()


# ---------------------------------------------------------------- filtragem
def _passa_filtros(im: Imovel, p: BuscaParams, avisos: set[str]) -> bool:
    if p.quartos_min is not None and (im.quartos is None or im.quartos < p.quartos_min):
        return False
    if p.quartos_max is not None and (im.quartos is None or im.quartos > p.quartos_max):
        return False
    if p.area_min is not None and (im.area is None or im.area < p.area_min):
        return False
    if p.area_max is not None and (im.area is None or im.area > p.area_max):
        return False
    if p.vagas is not None and (im.vagas is None or im.vagas != p.vagas):
        return False

    loc = p.localizacao
    if loc.tipo == "rua":
        if not geo.rua_casa(im.rua, loc.rua):
            return False
    elif loc.tipo == "poligono":
        if im.coord_aproximada:
            avisos.add(
                "Filtro por polígono usa coordenada APROXIMADA dos anúncios; "
                "resultados perto da borda podem estar imprecisos."
            )
        if not geo.dentro_do_poligono(im.lat, im.lon, loc.poligono):
            return False
    elif loc.tipo == "bairro" and loc.bairros:
        alvos = {geo.normalizar(b) for b in loc.bairros}
        if geo.normalizar(im.bairro) not in alvos:
            return False
    return True


def _dedupe(imoveis: list[Imovel]) -> list[Imovel]:
    vistos: set[tuple] = set()
    out: list[Imovel] = []
    for im in imoveis:
        chave = (
            geo.normalizar(im.rua),
            geo.normalizar(im.bairro),
            im.area,
            im.quartos,
            im.preco,
        )
        if chave in vistos:
            continue
        vistos.add(chave)
        out.append(im)
    return out


# ---------------------------------------------------------------- endpoints
@app.get("/api/portais")
def portais():
    return [
        {"nome": s.nome, "rotulo": s.rotulo, "disponivel": s.disponivel}
        for s in SCRAPERS.values()
    ]


class RespostaBusca(BaseModel):
    total: int
    por_portal: dict[str, int]
    avisos: list[str]
    imoveis: list[Imovel]


@app.post("/api/buscar", response_model=RespostaBusca)
async def buscar(params: BuscaParams):
    avisos: set[str] = set()
    ativos, por_portal = [], {}
    for nome in params.portais:
        s = get_scraper(nome)
        if s is None:
            avisos.add(f"Portal desconhecido ignorado: {nome}")
        elif not s.disponivel:
            avisos.add(f"Portal '{s.rotulo}' ainda não implementado — pulado.")
        else:
            ativos.append(s)

    brutos: list[Imovel] = []
    async with httpx.AsyncClient() as client:
        async def rodar(s):
            try:
                return s.nome, await s.buscar(params, client)
            except Exception as e:  # noqa: BLE001 — reporta falha do portal sem derrubar a busca
                avisos.add(f"Falha ao consultar {s.rotulo}: {type(e).__name__}")
                return s.nome, []

        for nome, lst in await asyncio.gather(*(rodar(s) for s in ativos)):
            por_portal[nome] = len(lst)
            brutos.extend(lst)

    filtrados = [im for im in brutos if _passa_filtros(im, params, avisos)]
    final = _dedupe(filtrados)
    return RespostaBusca(
        total=len(final),
        por_portal=por_portal,
        avisos=sorted(avisos),
        imoveis=final,
    )


# ------------------------------------------------- buscas salvas (CRUD)
@app.get("/api/buscas")
def listar_buscas():
    return db.listar_buscas()


class NovaBusca(BaseModel):
    nome: str
    params: BuscaParams


@app.post("/api/buscas")
def criar_busca(nb: NovaBusca):
    return db.salvar_busca(nb.nome, nb.params)


@app.delete("/api/buscas/{bid}")
def apagar_busca(bid: int):
    if not db.excluir_busca(bid):
        raise HTTPException(404, "Busca não encontrada")
    return {"ok": True}


# ------------------------------------------------- frontend estático
@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")


if FRONTEND.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND), name="static")
