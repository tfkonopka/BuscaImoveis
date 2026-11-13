"""Utilidades compartilhadas pelos coletores que raspam HTML (OLX, QuintoAndar,
Imovelweb): bairros da Zona Sul, slug, parsing numérico e fetch com curl_cffi
(impersona o TLS do Chrome para passar pelo DataDome)."""
from __future__ import annotations

import re
from typing import Optional

from unidecode import unidecode

# Bairros da Zona Sul do Rio — usados quando a busca é por 'zona' (itera todos).
ZONA_SUL_BAIRROS = [
    "Copacabana", "Ipanema", "Leblon", "Botafogo", "Flamengo", "Laranjeiras",
    "Catete", "Glória", "Humaitá", "Urca", "Leme", "Gávea", "Jardim Botânico",
    "Lagoa", "São Conrado", "Cosme Velho", "Vidigal",
]

_OUTRAS_ZONAS = {
    "Zona Norte": ["Tijuca", "Vila Isabel", "Maracanã", "Grajaú", "Méier"],
    "Zona Oeste": ["Barra da Tijuca", "Recreio dos Bandeirantes", "Jacarepaguá", "Campo Grande"],
    "Centro": ["Centro", "Santa Teresa", "Lapa"],
}


def bairros_da_zona(zona: str) -> list[str]:
    if zona == "Zona Sul":
        return ZONA_SUL_BAIRROS
    return _OUTRAS_ZONAS.get(zona, ZONA_SUL_BAIRROS)


def slug(texto: Optional[str]) -> str:
    if not texto:
        return ""
    return "-".join(unidecode(texto).lower().split())


def so_digitos(texto) -> Optional[int]:
    """'R$ 1.650.000' -> 1650000 ; '130m²' -> 130 ; None se não houver dígito."""
    if texto is None:
        return None
    d = re.sub(r"[^\d]", "", str(texto))
    return int(d) if d else None


def fetch(url: str, timeout: int = 30) -> Optional[str]:
    """GET com curl_cffi impersonando o Chrome. Devolve o HTML ou None em falha."""
    from curl_cffi import requests as creq

    try:
        # Sem headers customizados: o impersonate="chrome" já envia o conjunto
        # coerente de cabeçalhos. Passar Accept-Language avulso quebra o
        # fingerprint e o ZAP responde 429.
        r = creq.get(url, impersonate="chrome", timeout=timeout)
        if r.status_code == 200:
            return r.text
    except Exception:
        return None
    return None
