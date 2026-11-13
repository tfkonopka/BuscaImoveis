# 🏠 Buscador de Imóveis — Rio de Janeiro (foco Zona Sul)

Busca anúncios ativos em portais imobiliários, com filtros por **quartos**,
**metragem (faixa)**, **vagas (quantidade exata)** e **localização** (zona,
bairro, rua ou **polígono desenhado no mapa**). Interface web, busca **sob
demanda** (só roda quando você clica) e **buscas salvas** para repetir depois.

> Projeto irmão do *Visualizador ITBI* (dados históricos de transações). Este
> aqui lida com **anúncios ao vivo**.

## Portais

| Portal | Status | Método | Rua? | Mapa/polígono? |
|---|---|---|---|---|
| ZAP Imóveis | ✅ funcional | API interna (Glue API) | sim | sim (coord. aprox.) |
| VivaReal | ✅ funcional | API interna (mesma Glue API) | sim | sim (coord. aprox.) |
| OLX Imóveis | ✅ funcional | HTML (RSC Next.js) via curl_cffi | não | não |
| QuintoAndar | ✅ funcional | HTML (`__NEXT_DATA__`) | sim | não |
| Imovelweb | ✅ funcional | HTML (`__PRELOADED_STATE__`) via curl_cffi | sim | não |

**Anti-bot:** OLX e Imovelweb usam DataDome e bloqueiam requisições comuns (403).
Por isso usamos **`curl_cffi`** (impersona o TLS do Chrome) nesses dois. ZAP/VivaReal
usam a Glue API (JSON) e QuintoAndar renderiza no servidor (basta `httpx`).

**Diferenças por portal:**
- OLX não expõe **rua** nem **coordenadas** na listagem → não entra nos modos
  *rua* e *polígono*.
- QuintoAndar e Imovelweb trazem **rua** (modo *rua* funciona), mas sem coordenadas
  (não entram no *polígono*).
- QuintoAndar traz ~24 imóveis por bairro (1ª página); na busca por *zona* iteramos
  os bairros da Zona Sul para somar mais resultados.
- Só ZAP/VivaReal têm coordenadas → o filtro por **polígono** só se aplica a eles.

## Como rodar

```bash
cd buscador/backend
pip3 install --target=.deps -r requirements.txt      # 1ª vez (sem precisar de sudo/venv)
PYTHONPATH=.deps .deps/bin/uvicorn main:app --host 127.0.0.1 --port 8777
```

Depois abra <http://127.0.0.1:8777> no navegador.

> Se o seu ambiente tiver `python3-venv`, pode usar venv normalmente em vez do
> `--target=.deps`.

## Como usar

1. Marque os **portais** desejados.
2. Defina **quartos** (mín/máx), **área** (mín/máx) e **vagas** (exato — `0`
   retorna só anúncios sem vaga).
3. Escolha o modo de **localização**:
   - **Zona** — zona inteira (ex.: Zona Sul).
   - **Bairro** — um ou mais bairros separados por vírgula.
   - **Rua** — nome da rua (resolvido via autocomplete do portal).
   - **Polígono** — desenhe a área no mapa com a ferramenta ▱.
4. Clique em **🔎 Buscar agora**.
5. Opcional: dê um nome e **Salve a busca** para repetir depois.

## Aba "Imobiliárias" (só ZAP)

Levanta os anunciantes de uma localização no ZAP e mostra, por imobiliária:
**nome, contato (telefone + WhatsApp), CRECI, 1 anúncio de exemplo** e **quantos
anúncios dela aparecem na amostra** coletada.

> A contagem é feita sobre a amostra baixada (o ZAP não permite filtrar/contar por
> anunciante, nem expõe facetas). Aumente a amostra para se aproximar do total na
> região. Nome, contato e anúncio de exemplo são exatos.

Endpoint: `POST /api/imobiliarias` (mesma forma de `BuscaParams`, mas só ZAP).

## Arquitetura

```
backend/
├── main.py            FastAPI: POST /api/buscar, CRUD /api/buscas, serve o front
├── models.py          Modelos (BuscaParams, Imovel, BuscaSalva)
├── db.py              SQLite (buscas salvas)
├── geo.py             normalização, match de rua, ponto-em-polígono (sem libs nativas)
└── scrapers/
    ├── base.py        interface comum (Scraper) + stub p/ conectores pendentes
    ├── glue.py        coletor ZAP/VivaReal (Glue API)
    └── __init__.py    registro de portais
frontend/
└── index.html         UI (Leaflet + Leaflet.draw), vanilla JS
```

A busca roda os coletores em paralelo, normaliza tudo para o modelo `Imovel`,
aplica os filtros finos no servidor e **deduplica** (ZAP e VivaReal compartilham
base, então o mesmo anúncio não aparece duas vezes).

## ⚠️ Limitações conhecidas

- **Coordenadas são aproximadas** nos anúncios (os portais deslocam de
  propósito), então o filtro por **polígono** pode ser impreciso perto da borda.
  O filtro por **rua** usa o nome textual da rua (mais confiável).
- A coleta depende de **APIs internas não oficiais** dos portais, que podem
  mudar sem aviso e cujos Termos de Uso restringem scraping. Uso pessoal.
- Há um teto de resultados por portal para não varrer dezenas de milhares de
  anúncios a cada busca.

## Licença / uso

Ferramenta de uso pessoal/educacional. Respeite os Termos de Uso dos portais.
