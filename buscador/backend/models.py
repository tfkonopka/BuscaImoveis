"""Modelos de dados do buscador: parâmetros de busca e imóvel normalizado."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class Localizacao(BaseModel):
    """Critério de localização. Use exatamente um dos modos abaixo.

    - tipo="zona": busca na zona inteira (ex.: Zona Sul).
    - tipo="bairro": um ou mais bairros (ex.: Copacabana, Ipanema).
    - tipo="rua": filtra por nome de rua (casa por substring normalizada).
    - tipo="poligono": filtra por polígono desenhado no mapa (ponto-em-polígono
      usando a coordenada aproximada do anúncio — ver limitação no README).
    """

    tipo: Literal["zona", "bairro", "rua", "poligono"] = "zona"
    zona: str = "Zona Sul"
    bairros: list[str] = Field(default_factory=list)
    rua: Optional[str] = None
    # polígono: lista de pontos [[lat, lon], ...]
    poligono: list[list[float]] = Field(default_factory=list)


class BuscaParams(BaseModel):
    """Parâmetros de uma busca. Também é o que se guarda em 'buscas salvas'."""

    portais: list[str] = Field(default_factory=lambda: ["zap", "vivareal"])
    operacao: Literal["venda", "aluguel"] = "venda"

    quartos_min: Optional[int] = None
    quartos_max: Optional[int] = None

    area_min: Optional[float] = None  # m²
    area_max: Optional[float] = None  # m²

    # Vagas: quantidade EXATA. 0 => somente anúncios com zero vagas.
    vagas: Optional[int] = None

    localizacao: Localizacao = Field(default_factory=Localizacao)

    # Teto de resultados por portal (protege contra varrer 60k anúncios).
    limite_por_portal: int = 100


class Imovel(BaseModel):
    """Imóvel normalizado — formato único vindo de qualquer portal."""

    portal: str
    id: str
    url: str
    titulo: str = ""
    preco: Optional[float] = None
    condominio: Optional[float] = None
    quartos: Optional[int] = None
    banheiros: Optional[int] = None
    vagas: Optional[int] = None
    area: Optional[float] = None
    endereco: str = ""
    rua: str = ""
    bairro: str = ""
    zona: str = ""
    lat: Optional[float] = None
    lon: Optional[float] = None
    coord_aproximada: bool = True
    fotos: list[str] = Field(default_factory=list)


class BuscaSalva(BaseModel):
    id: Optional[int] = None
    nome: str
    params: BuscaParams
    criado_em: Optional[str] = None
