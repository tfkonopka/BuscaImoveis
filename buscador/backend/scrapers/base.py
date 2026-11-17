"""Interface comum para todos os coletores de portais."""
from __future__ import annotations

import abc

import httpx

from models import BuscaParams, Imovel


class Scraper(abc.ABC):
    """Contrato que todo portal implementa.

    O resto do app só conhece esta interface — trocar 'API interna' por
    'navegador headless' em um portal não afeta nada fora do scraper.
    """

    nome: str = "base"
    rotulo: str = "Base"
    disponivel: bool = True  # False = conector ainda não implementado
    tem_coordenadas: bool = False  # True = anúncios trazem lat/lon (permite busca por polígono)

    @abc.abstractmethod
    async def buscar(self, params: BuscaParams, client: httpx.AsyncClient) -> list[Imovel]:
        """Retorna imóveis brutos do portal (filtragem fina é feita depois)."""
        raise NotImplementedError


class ScraperNaoImplementado(Scraper):
    """Stub: aparece na UI como indisponível, mas o app roda ponta a ponta."""

    disponivel = False

    def __init__(self, nome: str, rotulo: str):
        self.nome = nome
        self.rotulo = rotulo

    async def buscar(self, params: BuscaParams, client: httpx.AsyncClient) -> list[Imovel]:
        return []
