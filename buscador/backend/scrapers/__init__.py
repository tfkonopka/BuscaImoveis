"""Registro de coletores disponíveis."""
from __future__ import annotations

from scrapers.base import Scraper, ScraperNaoImplementado
from scrapers.glue import GlueScraper

# Ordem = ordem de exibição na UI.
SCRAPERS: dict[str, Scraper] = {
    "zap": GlueScraper("zap", "ZAP Imóveis", "ZAP", "www.zapimoveis.com.br"),
    "vivareal": GlueScraper("vivareal", "VivaReal", "VIVAREAL", "www.vivareal.com.br"),
    # Conectores a implementar (cada um exige investigação própria):
    "olx": ScraperNaoImplementado("olx", "OLX Imóveis"),
    "quintoandar": ScraperNaoImplementado("quintoandar", "QuintoAndar"),
    "imovelweb": ScraperNaoImplementado("imovelweb", "Imovelweb"),
}


def get_scraper(nome: str) -> Scraper | None:
    return SCRAPERS.get(nome)
