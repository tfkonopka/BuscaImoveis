"""Coletor da Glue API (ZAP e VivaReal — mesmo backend, muda portal/domínio).

Descoberto por inspeção: GET https://glue-api.zapimoveis.com.br/v2/listings
responde JSON com todos os campos necessários (quartos, metragem, vagas, rua,
coordenada aproximada). O filtro de localização usa `addressLocationId` no
formato "BR>Rio de Janeiro>NULL>Rio de Janeiro>{zona}>{bairro}".
"""
from __future__ import annotations

from typing import Optional

import httpx

from models import BuscaParams, Imovel
from scrapers.base import Scraper

GLUE_URL = "https://glue-api.zapimoveis.com.br/v2/listings"
GLUE_LOCATIONS = "https://glue-api.zapimoveis.com.br/v2/locations"

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

# Nos modos 'rua' e 'poligono' a API não filtra no servidor, então varremos
# mais páginas do bairro/zona e filtramos no código (até este teto bruto).
SCAN_CAP_REFINO = 480


def _loc_id(zona: str, bairro: Optional[str] = None) -> str:
    base = f"BR>Rio de Janeiro>NULL>Rio de Janeiro>{zona}"
    return f"{base}>{bairro}" if bairro else base


def _primeiro(v, conv=None):
    """Glue devolve listas (ex.: bedrooms:[2]). Pega o 1º elemento."""
    if isinstance(v, list):
        v = v[0] if v else None
    if v is None:
        return None
    return conv(v) if conv else v


def _quartos_range(p: BuscaParams) -> Optional[str]:
    if p.quartos_min is None and p.quartos_max is None:
        return None
    lo = p.quartos_min or 1
    hi = p.quartos_max or 5
    return ",".join(str(n) for n in range(lo, min(hi, 5) + 1))


class GlueScraper(Scraper):
    def __init__(self, nome: str, rotulo: str, portal: str, dominio: str):
        self.nome = nome
        self.rotulo = rotulo
        self.portal = portal  # "ZAP" | "VIVAREAL"
        self.dominio = dominio  # "www.zapimoveis.com.br"

    def _params_base(self, p: BuscaParams, loc_id: str, size: int, frm: int) -> dict:
        d: dict[str, str] = {
            "business": "RENTAL" if p.operacao == "aluguel" else "SALE",
            "listingType": "USED",
            "categoryPage": "RESULT",
            "portal": self.portal,
            "includeFields": "search",
            "size": str(size),
            "from": str(frm),
            "addressLocationId": loc_id,
            "addressCity": "Rio de Janeiro",
            "addressState": "Rio de Janeiro",
        }
        q = _quartos_range(p)
        if q:
            d["bedrooms"] = q
        if p.vagas is not None:
            d["parkingSpaces"] = str(p.vagas)
        if p.area_min is not None:
            d["usableAreasMin"] = str(int(p.area_min))
        if p.area_max is not None:
            d["usableAreasMax"] = str(int(p.area_max))
        return d

    def _locs(self, loc) -> list[str]:
        """Um ou mais addressLocationId conforme o modo de localização."""
        if loc.tipo == "bairro" and loc.bairros:
            return [_loc_id(loc.zona, b) for b in loc.bairros]
        # zona / poligono começam da zona inteira; refino é feito no código
        return [_loc_id(loc.zona)]

    async def _resolver_ruas(
        self, rua: str, client: httpx.AsyncClient, headers: dict
    ) -> list[str]:
        """Autocomplete do ZAP: resolve 'nome de rua' -> locationId(s) do bairro
        correspondente no RJ. O ZAP não filtra por rua no servidor; o filtro fino
        de rua é feito depois no código (geo.rua_casa)."""
        try:
            r = await client.get(
                GLUE_LOCATIONS,
                params={"q": rua, "portal": self.portal, "size": "10"},
                headers=headers,
                timeout=20,
            )
            r.raise_for_status()
            locs = r.json().get("street", {}).get("result", {}).get("locations", [])
        except Exception:
            return []
        ids: list[str] = []
        for loc in locs:
            a = loc.get("address", {})
            if a.get("city") == "Rio de Janeiro" and a.get("stateAcronym") == "RJ":
                lid = a.get("locationId")
                if lid and lid not in ids:
                    ids.append(lid)
        return ids

    def _to_imovel(self, item: dict) -> Optional[Imovel]:
        lst = item.get("listing") or {}
        link = item.get("link") or {}
        addr = lst.get("address") or {}
        point = addr.get("point") or {}
        preco = cond = None
        for pi in lst.get("pricingInfos") or []:
            if pi.get("price"):
                preco = float(pi["price"])
            if pi.get("monthlyCondoFee"):
                cond = float(pi["monthlyCondoFee"])
        lat = point.get("lat") or point.get("approximateLat")
        lon = point.get("lon") or point.get("approximateLon")
        _id = lst.get("id") or item.get("listing", {}).get("id")
        if not _id:
            return None
        href = link.get("href") or ""
        url = f"https://{self.dominio}{href}" if href.startswith("/") else (href or f"https://{self.dominio}")
        return Imovel(
            portal=self.nome,
            id=str(_id),
            url=url,
            titulo=(lst.get("title") or "").strip(),
            preco=preco,
            condominio=cond,
            quartos=_primeiro(lst.get("bedrooms"), int),
            banheiros=_primeiro(lst.get("bathrooms"), int),
            vagas=_primeiro(lst.get("parkingSpaces"), int),
            area=_primeiro(lst.get("usableAreas"), float),
            endereco=", ".join(
                x for x in [addr.get("street"), addr.get("neighborhood"), addr.get("zone")] if x
            ),
            rua=addr.get("street") or "",
            bairro=addr.get("neighborhood") or "",
            zona=addr.get("zone") or "",
            lat=float(lat) if lat not in (None, "") else None,
            lon=float(lon) if lon not in (None, "") else None,
            coord_aproximada=bool(point.get("aproximated", True)),
            fotos=[m.get("url", "").replace("{action}", "crop").replace("{width}", "600").replace("{height}", "450")
                   for m in (lst.get("medias") or []) if m.get("url")][:3],
        )

    async def buscar(self, params: BuscaParams, client: httpx.AsyncClient) -> list[Imovel]:
        headers = {"User-Agent": UA, "Accept": "application/json", "x-domain": self.dominio}
        size = 24  # teto da Glue API ("Size is above acceptable limit" acima disso)
        loc = params.localizacao

        if loc.tipo == "rua" and loc.rua:
            loc_ids = await self._resolver_ruas(loc.rua, client, headers)
            if not loc_ids:  # autocomplete não achou: cai para a zona inteira
                loc_ids = self._locs(loc)
            alvo = SCAN_CAP_REFINO
        elif loc.tipo == "poligono":
            loc_ids = self._locs(loc)
            alvo = SCAN_CAP_REFINO
        else:
            loc_ids = self._locs(loc)
            alvo = params.limite_por_portal

        out: list[Imovel] = []
        for loc_id in loc_ids:
            frm = 0
            while len(out) < alvo:
                q = self._params_base(params, loc_id, size, frm)
                r = await client.get(GLUE_URL, params=q, headers=headers, timeout=30)
                r.raise_for_status()
                listings = (
                    r.json().get("search", {}).get("result", {}).get("listings", [])
                )
                if not listings:
                    break
                for it in listings:
                    im = self._to_imovel(it)
                    if im:
                        out.append(im)
                frm += size
                if len(listings) < size:
                    break
        return out
