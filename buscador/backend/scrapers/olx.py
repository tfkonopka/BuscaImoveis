"""Coletor do OLX. O site bloqueia httpx comum (DataDome 403); usamos curl_cffi
(impersona TLS do Chrome). Os anúncios vêm embutidos no payload RSC do Next.js
(scripts self.__next_f.push). Lá cada anúncio tem listId, price, url, location e
um array `properties` com rooms, size, garage_spaces, condominio.

Limitações do OLX: o resultado de listagem NÃO traz rua nem coordenadas — logo
os modos 'rua' e 'poligono' não filtram anúncios do OLX."""
from __future__ import annotations

import asyncio
import json
import re

import httpx

from models import BuscaParams, Imovel
from scrapers.base import Scraper
from scrapers.util import bairros_da_zona, fetch, slug, so_digitos


def _parse_olx(html: str) -> list[dict]:
    scripts = re.findall(r'__next_f\.push\(\[1,\s*(".*?")\]\)', html, re.S)
    if not scripts:
        return []
    blob = "".join(json.loads(s) for s in scripts)
    achados: list[list] = []

    def varrer(o):
        if isinstance(o, list):
            if o and isinstance(o[0], dict) and "listId" in o[0]:
                achados.append(o)
            for x in o:
                varrer(x)
        elif isinstance(o, dict):
            for v in o.values():
                varrer(v)

    dec = json.JSONDecoder()
    for linha in blob.split("\n"):
        c = linha.find(":")
        if c < 0:
            continue
        try:
            obj, _ = dec.raw_decode(linha[c + 1:])
            varrer(obj)
        except Exception:
            continue
    return max(achados, key=len) if achados else []


def _img(a: dict) -> list[str]:
    out = []
    for im in (a.get("images") or []):
        u = im.get("original") or im.get("url") if isinstance(im, dict) else None
        if u:
            out.append(u)
    return out[:3]


class OlxScraper(Scraper):
    nome = "olx"
    rotulo = "OLX Imóveis"

    def _url(self, op: str, zona: str, bairro: str, pagina: int) -> str:
        base = (
            f"https://www.olx.com.br/imoveis/{op}/estado-rj/"
            f"rio-de-janeiro-e-regiao/{slug(zona)}/{slug(bairro)}"
        )
        return base + (f"?o={pagina}" if pagina > 1 else "")

    def _to_imovel(self, a: dict) -> Imovel | None:
        _id = a.get("listId")
        if not _id:
            return None
        props = {p.get("name"): p.get("value") for p in (a.get("properties") or [])}
        loc = a.get("location") or ""
        bairro = loc.split(",")[-1].strip() if loc else ""
        vagas = so_digitos(props.get("garage_spaces"))
        return Imovel(
            portal=self.nome,
            id=str(_id),
            url=a.get("url") or "https://www.olx.com.br",
            titulo=(a.get("subject") or "").strip(),
            preco=so_digitos(a.get("price")),
            condominio=so_digitos(props.get("condominio")),
            quartos=so_digitos(props.get("rooms")),
            banheiros=so_digitos(props.get("bathrooms")),
            vagas=vagas if vagas is not None else 0,
            area=so_digitos(props.get("size")),
            endereco=loc,
            rua="",  # OLX não expõe rua na listagem
            bairro=bairro,
            zona="",
            lat=None,
            lon=None,
            coord_aproximada=True,
            fotos=_img(a),
        )

    def _coletar_sync(self, params: BuscaParams, bairros: list[str], alvo: int) -> list[Imovel]:
        op = "aluguel" if params.operacao == "aluguel" else "venda"
        out: list[Imovel] = []
        for bairro in bairros:
            for pagina in range(1, 6):
                if len(out) >= alvo:
                    return out
                html = fetch(self._url(op, params.localizacao.zona, bairro, pagina))
                if not html:
                    break
                ads = _parse_olx(html)
                if not ads:
                    break
                for a in ads:
                    im = self._to_imovel(a)
                    if im:
                        out.append(im)
        return out

    async def buscar(self, params: BuscaParams, client: httpx.AsyncClient) -> list[Imovel]:
        loc = params.localizacao
        bairros = loc.bairros if (loc.tipo == "bairro" and loc.bairros) else bairros_da_zona(loc.zona)
        alvo = max(params.limite_por_portal, 150) if loc.tipo in ("rua", "poligono") else params.limite_por_portal
        return await asyncio.to_thread(self._coletar_sync, params, bairros, alvo)
