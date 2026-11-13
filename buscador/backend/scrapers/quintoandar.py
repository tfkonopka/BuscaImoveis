"""Coletor do QuintoAndar. A 1ª página é renderizada no servidor (Next.js) e os
imóveis ficam em __NEXT_DATA__ → props.pageProps.initialState.houses, cada um com
id, salePrice/rentPrice, area, bedrooms, parkingSpots, address.address (rua),
neighbourhood, type, photos.

Limitação: só a 1ª página (~24 imóveis) por bairro vem no HTML; para a zona
inteira iteramos os bairros. Sem paginação profunda e sem coordenadas."""
from __future__ import annotations

import asyncio
import json
import re

import httpx

from models import BuscaParams, Imovel
from scrapers.base import Scraper
from scrapers.util import bairros_da_zona, fetch, slug


def _next_data(html: str) -> dict | None:
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


class QuintoAndarScraper(Scraper):
    nome = "quintoandar"
    rotulo = "QuintoAndar"

    def _url(self, op: str, bairro: str) -> str:
        acao = "alugar" if op == "aluguel" else "comprar"
        return f"https://www.quintoandar.com.br/{acao}/imovel/{slug(bairro)}-rio-de-janeiro-rj-brasil"

    def _to_imovel(self, h: dict, op: str) -> Imovel | None:
        _id = h.get("id")
        if not _id:
            return None
        if op == "aluguel" and not h.get("forRent"):
            return None
        if op == "venda" and not h.get("forSale"):
            return None
        preco = h.get("rentPrice") if op == "aluguel" else h.get("salePrice")
        addr = h.get("address") or {}
        rua = addr.get("address") or ""
        bairro = h.get("neighbourhood") or h.get("regionName") or ""
        fotos = [
            f"https://www.quintoandar.com.br/img/med/{p.get('url')}"
            for p in (h.get("photos") or []) if p.get("url")
        ][:3]
        return Imovel(
            portal=self.nome,
            id=str(_id),
            url=f"https://www.quintoandar.com.br/imovel/{_id}",
            titulo=(h.get("type") or "") + (f" · {bairro}" if bairro else ""),
            preco=float(preco) if preco else None,
            condominio=float(h["condoIptu"]) if h.get("condoIptu") else None,
            quartos=h.get("bedrooms"),
            banheiros=h.get("bathrooms"),
            vagas=h.get("parkingSpots"),
            area=float(h["area"]) if h.get("area") else None,
            endereco=", ".join(x for x in [rua, bairro, addr.get("city")] if x),
            rua=rua,
            bairro=bairro,
            zona="",
            lat=None,
            lon=None,
            coord_aproximada=True,
            fotos=fotos,
        )

    def _coletar_sync(self, params: BuscaParams, bairros: list[str], alvo: int) -> list[Imovel]:
        op = "aluguel" if params.operacao == "aluguel" else "venda"
        out: list[Imovel] = []
        for bairro in bairros:
            if len(out) >= alvo:
                break
            html = fetch(self._url(op, bairro))
            if not html:
                continue
            j = _next_data(html)
            if not j:
                continue
            houses = (
                j.get("props", {}).get("pageProps", {}).get("initialState", {}).get("houses", {})
            )
            for v in houses.values():
                if isinstance(v, dict) and v.get("id"):
                    im = self._to_imovel(v, op)
                    if im:
                        out.append(im)
        return out

    async def buscar(self, params: BuscaParams, client: httpx.AsyncClient) -> list[Imovel]:
        loc = params.localizacao
        bairros = loc.bairros if (loc.tipo == "bairro" and loc.bairros) else bairros_da_zona(loc.zona)
        alvo = max(params.limite_por_portal, 150) if loc.tipo in ("rua", "poligono") else params.limite_por_portal
        return await asyncio.to_thread(self._coletar_sync, params, bairros, alvo)
