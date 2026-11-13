"""Registro de coletores disponíveis."""
from __future__ import annotations

from scrapers.base import Scraper
from scrapers.glue import GlueScraper
from scrapers.imovelweb import ImovelwebScraper
from scrapers.olx import OlxScraper
from scrapers.quintoandar import QuintoAndarScraper

# Ordem = ordem de exibição na UI.
SCRAPERS: dict[str, Scraper] = {
    "zap": GlueScraper("zap", "ZAP Imóveis", "ZAP", "www.zapimoveis.com.br"),
    "vivareal": GlueScraper("vivareal", "VivaReal", "VIVAREAL", "www.vivareal.com.br"),
    "olx": OlxScraper(),
    "quintoandar": QuintoAndarScraper(),
    "imovelweb": ImovelwebScraper(),
}


def get_scraper(nome: str) -> Scraper | None:
    return SCRAPERS.get(nome)
