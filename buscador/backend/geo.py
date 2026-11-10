"""Utilidades de localização: normalização de texto, rua e ponto-em-polígono."""
from __future__ import annotations

from typing import Optional

from unidecode import unidecode


def normalizar(texto: Optional[str]) -> str:
    """minúsculas, sem acento, espaços colapsados — para comparar nomes."""
    if not texto:
        return ""
    return " ".join(unidecode(texto).lower().split())


def rua_casa(rua_imovel: Optional[str], alvo: Optional[str]) -> bool:
    """True se o nome da rua do imóvel contém o alvo (normalizado)."""
    if not alvo:
        return True
    r, a = normalizar(rua_imovel), normalizar(alvo)
    if not r:
        return False
    return a in r or r in a


def dentro_do_poligono(
    lat: Optional[float], lon: Optional[float], pontos: list[list[float]]
) -> bool:
    """Ponto-em-polígono por ray casting. `pontos` = [[lat, lon], ...].

    Sem dependência nativa (evita libgeos/shapely). Polígono inválido
    (<3 vértices) não filtra nada; coordenada ausente => fora.
    """
    if not pontos or len(pontos) < 3:
        return True
    if lat is None or lon is None:
        return False
    x, y = lon, lat
    dentro = False
    n = len(pontos)
    j = n - 1
    for i in range(n):
        yi, xi = pontos[i][0], pontos[i][1]
        yj, xj = pontos[j][0], pontos[j][1]
        intersecta = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersecta:
            dentro = not dentro
        j = i
    return dentro
