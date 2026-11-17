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
**nome, contato, CRECI, 1 anúncio de exemplo** e o **total real de imóveis dela no
portal** (lido da página do anúncio durante a busca). Há filtro por faixa de total.

Endpoint: `POST /api/imobiliarias` (mesma forma de `BuscaParams`, mas só ZAP).

### WhatsApp (click-to-chat oficial)

Painel “💬 WhatsApp” na aba:

- **Remetentes** (ex.: você e sua esposa): escolha em *Enviando como*. O link
  `wa.me` abre o WhatsApp **logado no navegador/celular em uso** — o número
  cadastrado é só referência e o nome entra na mensagem.
- **Mensagem padrão** salva no banco, com variáveis `{imobiliaria}`, `{bairro}`,
  `{link_anuncio}`, `{remetente}` e prévia.
- **💬 Enviar WhatsApp** em cada card (só celulares de 11 dígitos): abre o chat com a
  mensagem pronta e registra o contato. Fixos têm “Marcar contactada” manual.
- **Controle**: quem contatou e quando, status (Enviada / Respondeu / Sem interesse),
  observação, “desfazer”, aviso ao reenviar para quem já foi contactada e filtro
  (todas / não contactadas / contactadas / por remetente).

Endpoints: `/api/whatsapp/remetentes`, `/mensagem`, `/contatos` (SQLite local).
Não há envio automático: você aperta Enviar no WhatsApp (sem API paga nem risco de banimento).

## Aba "ITBI (valores declarados)"

Mostra no mapa as **transações imobiliárias registradas no ITBI** da Prefeitura do Rio
(cidade inteira, de 2011 em diante): rua, número, complemento, bairro, tipo, área, mês/ano
e **valor declarado**, com R$/m². Tem as mesmas funções da aba de busca — localização por
zona/bairro/rua(+número)/polígono, filtros de área/valor/período/tipo, tabela ordenável com
seletor de colunas, seleção múltipla (ponto vermelho) e buscas salvas — mais um resumo de
preços (mediana, faixa 25%–75%, média e mediana por ano) calculado sobre **todas** as
transações do filtro.

**Importar/atualizar a base** (planilhas → `itbi.db`, ~250 MB, fora do git):

```bash
cd buscador/backend
PYTHONPATH=.deps python3 itbi_import.py --baixar     # baixa as planilhas e reimporta
```

- Fonte: planilhas `ITBI_TRANSACOES_*` da Secretaria Municipal de Fazenda
  (<https://fazenda.prefeitura.rio/itbi-valores-medios-por-m2-de-transacoes-imobiliarias-por-trecho-de-logradouro/>).
- Posição no mapa: cruzamento do código do logradouro + número com a camada
  `CadLog/Numero_de_porta` do ArcGIS da Prefeitura (≈71% no número exato; 94% na Zona Sul).
  Sem número cadastrado, usa o número vizinho na mesma rua ou o meio da rua (ponto mais
  claro no mapa); ≈2% ficam sem coordenada e aparecem só na tabela.
- `--refazer` baixa de novo também as bases geográficas (números de porta e logradouros).
- O valor é o **declarado** na guia do ITBI — pode diferir do preço de mercado.

Endpoints: `GET /api/itbi/meta`, `POST /api/itbi/buscar`, CRUD `/api/itbi/buscas`.

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
