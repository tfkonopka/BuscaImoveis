# 🏠 Buscador de Imóveis — Rio de Janeiro (foco Zona Sul)

Busca anúncios ativos em portais imobiliários, com filtros por **quartos**,
**metragem (faixa)**, **vagas (quantidade exata)** e **localização** (zona,
bairro, rua ou **polígono desenhado no mapa**). Interface web, busca **sob
demanda** (só roda quando você clica) e **buscas salvas** para repetir depois.

> Projeto irmão do *Visualizador ITBI* (dados históricos de transações). Este
> aqui lida com **anúncios ao vivo**.

## Portais

| Portal | Status | Método |
|---|---|---|
| ZAP Imóveis | ✅ funcional | API interna (Glue API) |
| VivaReal | ✅ funcional | API interna (mesma Glue API) |
| OLX Imóveis | 🔧 conector a implementar | — |
| QuintoAndar | 🔧 conector a implementar | — |
| Imovelweb | 🔧 conector a implementar | — |

Os 3 conectores pendentes já aparecem na interface (como "em breve") e têm a
interface pronta em `backend/scrapers/` — basta implementar o método `buscar`.

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
