"""Coletor do Imovelweb. Bloqueia httpx comum (DataDome 403); usamos curl_cffi.
Os anúncios vêm em window.__PRELOADED_STATE__ → ...listPostings, cada um com
postingId, priceOperationTypes, expenses, mainFeatures (área/quartos/vagas via
label), postingLocation (rua + bairro) e url."""
from __future__ import annotations

import asyncio
import json

import httpx

from models import BuscaParams, Imovel
from scrapers.base import Scraper
from scrapers.util import bairros_da_zona, fetch, slug, so_digitos
from unidecode import unidecode


def _preloaded(html: str) -> dict | None:
    chave = "__PRELOADED_STATE__ = "
    i = html.find(chave)
    if i < 0:
        return None
    try:
        obj, _ = json.JSONDecoder().raw_decode(html[i + len(chave):])
        return obj
    except Exception:
        return None


def _buscar_chave(o, chave, prof=0):
    if prof > 7 or not isinstance(o, (dict, list)):
        return None
    if isinstance(o, dict):
        if chave in o:
            return o[chave]
        for v in o.values():
            r = _buscar_chave(v, chave, prof + 1)
            if r is not None:
                return r
    else:
        for v in o:
            r = _buscar_chave(v, chave, prof + 1)
            if r is not None:
                return r
    return None


def _features(p: dict) -> dict:
    """Mapeia mainFeatures (keyed CFTxxx) por rótulo normalizado."""
    area = quartos = banheiros = vagas = None
    for f in (p.get("mainFeatures") or {}).values():
        lab = unidecode((f.get("label") or "")).lower()
        val = so_digitos(f.get("value"))
        if "util" in lab and val:
            area = val
        elif "total" in lab and area is None:
            area = val
        elif "quarto" in lab:
            quartos = val
        elif "banheiro" in lab:
            banheiros = val
        elif "vaga" in lab or "gara" in lab:
            vagas = val
    return {"area": area, "quartos": quartos, "banheiros": banheiros, "vagas": vagas}


class ImovelwebScraper(Scraper):
    nome = "imovelweb"
    rotulo = "Imovelweb"

    def _url(self, op: str, bairro: str, pagina: int) -> str:
        base = f"https://www.imovelweb.com.br/apartamentos-{op}-{slug(bairro)}-rio-de-janeiro"
        return base + (f"-pagina-{pagina}.html" if pagina > 1 else ".html")

    def _to_imovel(self, p: dict, op: str) -> Imovel | None:
        _id = p.get("postingId")
        if not _id:
            return None
        alvo_op = "Aluguel" if op == "aluguel" else "Venda"
        preco = None
        for pot in (p.get("priceOperationTypes") or []):
            if (pot.get("operationType") or {}).get("name") == alvo_op:
                precos = pot.get("prices") or []
                if precos:
                    preco = so_digitos(precos[0].get("amount"))
        if preco is None:  # anúncio não é da operação buscada
            return None
        feat = _features(p)
        loc = p.get("postingLocation") or {}
        rua = ((loc.get("address") or {}).get("name") or "").strip().rstrip(",").strip()
        bairro = (loc.get("location") or {}).get("name") or ""
        url = p.get("url") or ""
        if url.startswith("/"):
            url = "https://www.imovelweb.com.br" + url
        fotos = [
            pic.get("url") for pic in (p.get("visiblePictures", {}).get("pictures") or [])
            if isinstance(pic, dict) and pic.get("url")
        ][:3]
        return Imovel(
            portal=self.nome,
            id=str(_id),
            url=url or "https://www.imovelweb.com.br",
            titulo=(p.get("title") or "").strip(),
            preco=preco,
            condominio=so_digitos((p.get("expenses") or {}).get("amount")),
            quartos=feat["quartos"],
            banheiros=feat["banheiros"],
            vagas=feat["vagas"] if feat["vagas"] is not None else 0,
            area=feat["area"],
            endereco=", ".join(x for x in [rua, bairro] if x),
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
            for pagina in range(1, 5):
                if len(out) >= alvo:
                    return out
                html = fetch(self._url(op, bairro, pagina))
                if not html:
                    break
                st = _preloaded(html)
                if not st:
                    break
                postings = _buscar_chave(st, "listPostings") or []
                if not postings:
                    break
                for p in postings:
                    im = self._to_imovel(p, op)
                    if im:
                        out.append(im)
        return out

    async def buscar(self, params: BuscaParams, client: httpx.AsyncClient) -> list[Imovel]:
        loc = params.localizacao
        bairros = loc.bairros if (loc.tipo == "bairro" and loc.bairros) else bairros_da_zona(loc.zona)
        alvo = max(params.limite_por_portal, 150) if loc.tipo in ("rua", "poligono") else params.limite_por_portal
        return await asyncio.to_thread(self._coletar_sync, params, bairros, alvo)
