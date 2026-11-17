"""Importa as planilhas de ITBI da Prefeitura do Rio para o SQLite local (itbi.db).

Uso:  PYTHONPATH=.deps python3 itbi_import.py [--baixar] [--refazer]

  --baixar   baixa de novo as 3 planilhas de fazenda.prefeitura.rio (dados_itbi/)
  --refazer  refaz também as bases geográficas (números de porta e logradouros)

Etapas (cada uma fica em cache no itbi.db):
  1. planilhas .xlsx  -> tabela `bruto`
  2. CadLog/Numero_de_porta (ArcGIS da Prefeitura) -> tabela `np` (cl, número, lat, lon)
  3. CadLog/Trechos_Logradouros -> tabela `logradouros` (nome oficial por código)
  4. bairros -> zona (regiões de planejamento) e tabela final `itbi`, geocodificada
"""
from __future__ import annotations

import bisect
import re
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
from unidecode import unidecode

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados_itbi"
DB_PATH = AQUI / "itbi.db"

PAGINA = "https://fazenda.prefeitura.rio/itbi-valores-medios-por-m2-de-transacoes-imobiliarias-por-trecho-de-logradouro/"
ARCGIS = "https://pgeo3.rio.rj.gov.br/arcgis/rest/services"
UA = {"User-Agent": "Mozilla/5.0"}

_ESC = re.compile(r"_x([0-9A-Fa-f]{4})_")


def txt(v) -> str:
    """Desfaz o escape OOXML (_x0020_ -> espaço) e apara."""
    if v is None:
        return ""
    return _ESC.sub(lambda m: chr(int(m.group(1), 16)), str(v)).strip()


def norm(s: str) -> str:
    return " ".join(unidecode(s or "").lower().split())


def inteiro(v):
    d = re.sub(r"\D", "", txt(v))
    return int(d) if d else None


def numero(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        try:
            return float(txt(v).replace(",", "."))
        except ValueError:
            return None


def conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA synchronous=OFF")
    return c


def existe(c, tabela: str) -> bool:
    return bool(c.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (tabela,)).fetchone())


# ------------------------------------------------------------ 0. download
def baixar_planilhas() -> None:
    DADOS.mkdir(exist_ok=True)
    html = httpx.get(PAGINA, headers=UA, timeout=60, follow_redirects=True).text
    links = sorted(set(re.findall(r'href="([^"]+ITBI_TRANSACOES[^"]+\.xlsx)"', html)))
    if not links:
        raise SystemExit("Não achei as planilhas ITBI_TRANSACOES na página da Fazenda.")
    for antigo in DADOS.glob("*.xlsx"):
        antigo.unlink()
    for u in links:
        m = re.search(r"ITBI_TRANSACOES_(?:PERIODO_)?(\d{4}_(?:\d{4}|diante))", u)
        destino = DADOS / f"itbi_{m.group(1) if m else Path(u).stem}.xlsx"
        print(f"⬇️  {u}")
        with httpx.stream("GET", u, headers=UA, timeout=300, follow_redirects=True) as r:
            r.raise_for_status()
            with open(destino, "wb") as f:
                for parte in r.iter_bytes(1 << 20):
                    f.write(parte)


# ------------------------------------------------------------ 1. planilhas
def importar_planilhas(c) -> None:
    import warnings

    import openpyxl

    warnings.simplefilter("ignore")
    arquivos = sorted(DADOS.glob("*.xlsx"))
    if not arquivos:
        raise SystemExit(f"Nenhuma planilha em {DADOS}. Rode com --baixar.")
    c.execute("DROP TABLE IF EXISTS bruto")
    c.execute(
        """CREATE TABLE bruto (ano INT, mes INT, cd_bairro INT, cl INT, numero TEXT,
           complemento TEXT, bairro TEXT, logradouro TEXT, tipologia TEXT, utilizacao TEXT,
           parte REAL, valor REAL, area REAL, valor_m2 REAL)"""
    )
    total = 0
    for arq in arquivos:
        t0 = time.time()
        wb = openpyxl.load_workbook(arq, read_only=True)
        ws = wb.worksheets[0]
        linhas = ws.iter_rows(values_only=True)
        cab = [txt(x).lower() for x in next(linhas)]
        idx = {nome: i for i, nome in enumerate(cab)}

        def col(*nomes):
            for n in nomes:
                if n in idx:
                    return idx[n]
            raise SystemExit(f"{arq.name}: coluna {nomes} não encontrada em {cab}")

        i_ano, i_mes, i_cdb, i_cl = col("ano"), col("mes"), col("cd_bairro"), col("cl")
        i_num, i_comp = col("numero"), col("complemento")
        i_bai, i_log = col("nm_bairro_norm", "bairro"), col("logradouro")
        i_tip, i_uti = col("ds_imovel_tipologia"), col("descricao")
        i_par, i_val = col("parte_transferida"), col("valor_transacoes", "vl_declarado")
        i_area, i_m2 = col("area"), col("valor_m2")
        lote = []
        for r in linhas:
            if r[i_ano] is None:
                continue
            lote.append((
                inteiro(r[i_ano]), inteiro(r[i_mes]), inteiro(r[i_cdb]), inteiro(r[i_cl]),
                txt(r[i_num]), txt(r[i_comp]), txt(r[i_bai]), txt(r[i_log]),
                txt(r[i_tip]), txt(r[i_uti]), numero(r[i_par]),
                numero(r[i_val]), numero(r[i_area]), numero(r[i_m2]),
            ))
            if len(lote) >= 50000:
                c.executemany("INSERT INTO bruto VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", lote)
                total += len(lote)
                lote = []
        c.executemany("INSERT INTO bruto VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", lote)
        total += len(lote)
        wb.close()
        c.commit()
        print(f"📄 {arq.name}: acumulado {total:,} linhas ({time.time()-t0:.0f}s)")


# ------------------------------------------------------------ 2/3. ArcGIS
def _paginar(cli: httpx.Client, camada: str, campos: str, oid: str, ini: int, fim: int,
             geometria: bool) -> list[dict]:
    """Lê os registros com ini < oid <= fim (paginação por chave, 2000 por página)."""
    out, ultimo = [], ini
    while True:
        params = {
            "where": f"{oid}>{ultimo} AND {oid}<={fim}", "outFields": f"{oid},{campos}",
            "orderByFields": oid, "resultRecordCount": 2000, "f": "json",
            "returnGeometry": "true" if geometria else "false", "outSR": 4326,
        }
        for tentativa in range(5):
            try:
                d = cli.get(f"{ARCGIS}/{camada}/query", params=params).json()
                feats = d["features"]
                break
            except Exception:  # noqa: BLE001 — servidor público oscila; tenta de novo
                time.sleep(2 + tentativa * 3)
        else:
            raise SystemExit(f"Falha ao consultar {camada} (oid>{ultimo})")
        if not feats:
            return out
        out.extend(feats)
        ultimo = feats[-1]["attributes"][oid]


def _baixar_camada(camada: str, campos: str, oid: str, geometria: bool) -> list[dict]:
    with httpx.Client(headers=UA, timeout=90) as cli:
        est = cli.get(f"{ARCGIS}/{camada}/query", params={
            "where": "1=1", "f": "json", "outStatistics":
            f'[{{"statisticType":"max","onStatisticField":"{oid}","outStatisticFieldName":"mx"}}]'}).json()
        maximo = int(next(iter(est["features"][0]["attributes"].values())))
        passo = 40000
        faixas = [(i, min(i + passo, maximo)) for i in range(0, maximo, passo)]
        feitos, out = 0, []
        with ThreadPoolExecutor(6) as ex:
            for parte in ex.map(lambda f: _paginar(cli, camada, campos, oid, f[0], f[1], geometria), faixas):
                out.extend(parte)
                feitos += 1
                print(f"\r   {camada}: {feitos}/{len(faixas)} faixas · {len(out):,} registros", end="")
        print()
        return out


def importar_np(c) -> None:
    feats = _baixar_camada("CadLog/Numero_de_porta/MapServer/0", "cl,np", "objectid", True)
    c.execute("DROP TABLE IF EXISTS np")
    c.execute("CREATE TABLE np (cl INT, np INT, lat REAL, lon REAL)")
    linhas = []
    for f in feats:
        a, g = f["attributes"], f.get("geometry")
        cl, n = inteiro(a.get("cl")), inteiro(a.get("np"))
        if g and cl is not None and n is not None:
            linhas.append((cl, n, round(g["y"], 6), round(g["x"], 6)))
    c.executemany("INSERT INTO np VALUES (?,?,?,?)", linhas)
    c.commit()
    print(f"📍 números de porta: {len(linhas):,}")


def importar_logradouros(c) -> None:
    feats = _baixar_camada("CadLog/Trechos_Logradouros/MapServer/0",
                           "cl,completo,bairro", "cod_trecho", True)
    nomes, bairros, pontos = {}, defaultdict(Counter), defaultdict(list)
    for f in feats:
        a = f["attributes"]
        cl = inteiro(a.get("cl"))
        if cl is None:
            continue
        if a.get("completo"):
            nomes[cl] = a["completo"].strip()
        if a.get("bairro"):
            bairros[cl][a["bairro"].strip()] += 1
        for caminho in (f.get("geometry") or {}).get("paths") or []:
            pontos[cl].extend(caminho)
    c.execute("DROP TABLE IF EXISTS logradouros")
    c.execute("CREATE TABLE logradouros (cl INT PRIMARY KEY, nome TEXT, bairro TEXT, lat REAL, lon REAL)")
    linhas = []
    for cl in set(nomes) | set(pontos):
        pts = pontos.get(cl) or []
        # ponto real da rua mais próximo do centro (não a média, que pode cair fora da via)
        lat = lon = None
        if pts:
            mx, my = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
            px, py = min(pts, key=lambda p: (p[0] - mx) ** 2 + (p[1] - my) ** 2)[:2]
            lat, lon = round(py, 6), round(px, 6)
        b = bairros[cl].most_common(1)
        linhas.append((cl, nomes.get(cl, ""), b[0][0] if b else "", lat, lon))
    c.executemany("INSERT INTO logradouros VALUES (?,?,?,?,?)", linhas)
    c.commit()
    print(f"🛣️  logradouros: {len(linhas):,}")


def importar_bairros(c) -> None:
    with httpx.Client(headers=UA, timeout=60) as cli:
        d = cli.get(f"{ARCGIS}/Fazenda/ITBI/MapServer/1/query", params={
            "where": "1=1", "outFields": "codbairro,bairro,area_planejamento,cod_rp,rp",
            "returnDistinctValues": "true", "returnGeometry": "false", "f": "json"}).json()
    c.execute("DROP TABLE IF EXISTS bairros")
    c.execute("CREATE TABLE bairros (cd INT PRIMARY KEY, nome TEXT, zona TEXT, regiao TEXT)")
    for f in d["features"]:
        a = f["attributes"]
        ap, rp = str(a["area_planejamento"]).strip(), str(a["cod_rp"]).strip()
        zona = ("Centro" if ap == "1" else "Zona Sul" if rp == "2.1"
                else "Zona Norte" if ap in ("2", "3") else "Zona Oeste")
        c.execute("INSERT OR REPLACE INTO bairros VALUES (?,?,?,?)",
                  (int(a["codbairro"]), a["bairro"].strip(), zona, (a["rp"] or "").strip()))
    c.commit()
    print(f"🏘️  bairros: {c.execute('SELECT COUNT(*) FROM bairros').fetchone()[0]}")


# ------------------------------------------------------------ 4. tabela final
_ABREV = {"avn": "Avenida", "av": "Avenida", "etr": "Estrada", "est": "Estrada", "pca": "Praça",
          "tva": "Travessa", "trv": "Travessa", "lgo": "Largo", "bco": "Beco", "ald": "Alameda",
          "lad": "Ladeira", "rod": "Rodovia", "cam": "Caminho", "via": "Via", "pr": "Praia",
          "pra": "Praia", "r": "Rua", "blv": "Boulevard", "vde": "Viaduto"}
_MINUSC = {"de", "da", "do", "das", "dos", "e"}


def bonito(logr: str) -> str:
    """'AVN CHRISOSTOMO PIMENTEL' -> 'Avenida Chrisostomo Pimentel' (só para nomes sem cadastro)."""
    partes = logr.split()
    if not partes:
        return ""
    if partes[0].lower().rstrip(".") in _ABREV:
        partes[0] = _ABREV[partes[0].lower().rstrip(".")]
    return " ".join(p.lower() if p.lower() in _MINUSC and i else p.capitalize()
                    for i, p in enumerate(partes))


def montar_itbi(c) -> None:
    print("🧭 geocodificando…")
    exato: dict[tuple[int, int], tuple[float, float]] = {}
    por_rua: dict[int, list] = defaultdict(list)
    for cl, n, lat, lon in c.execute("SELECT cl, np, lat, lon FROM np"):
        exato.setdefault((cl, n), (lat, lon))
        por_rua[cl].append((n, lat, lon))
    for lst in por_rua.values():
        lst.sort()
    nums_rua = {cl: [x[0] for x in lst] for cl, lst in por_rua.items()}
    logr = {cl: (nome, bairro, lat, lon)
            for cl, nome, bairro, lat, lon in c.execute("SELECT * FROM logradouros")}
    bairros = {cd: (nome, zona) for cd, nome, zona, _ in c.execute("SELECT * FROM bairros")}
    bairro_por_nome = {norm(nome): (nome, zona) for nome, zona in bairros.values()}

    def localizar(cl, n):
        """-> (lat, lon, precisão)  1 = número exato · 2 = nº vizinho na mesma rua · 3 = só a rua."""
        if cl is None:
            return None, None, 0
        if n is not None and (cl, n) in exato:
            return (*exato[(cl, n)], 1)
        lst = por_rua.get(cl)
        if lst and n is not None:
            nums = nums_rua[cl]
            i = bisect.bisect_left(nums, n)
            cands = [lst[j] for j in range(max(0, i - 4), min(len(lst), i + 4))]
            mesmo_lado = [x for x in cands if x[0] % 2 == n % 2] or cands
            viz = min(mesmo_lado, key=lambda x: abs(x[0] - n))
            return viz[1], viz[2], 2
        if cl in logr and logr[cl][2] is not None:
            return logr[cl][2], logr[cl][3], 3
        if lst:
            meio = lst[len(lst) // 2]
            return meio[1], meio[2], 3
        return None, None, 0

    c.execute("DROP TABLE IF EXISTS itbi")
    c.execute(
        """CREATE TABLE itbi (
            id INTEGER PRIMARY KEY, ano INT, mes INT, periodo INT,
            bairro TEXT, bairro_norm TEXT, zona TEXT,
            cl INT, logradouro TEXT, rua_norm TEXT, numero TEXT, complemento TEXT,
            tipologia TEXT, utilizacao TEXT, parte REAL, valor REAL, area REAL, valor_m2 REAL,
            lat REAL, lon REAL, prec INT)"""
    )
    prec_cont, lote, n_total = Counter(), [], 0
    cur = c.cursor()
    for (ano, mes, cdb, cl, num, comp, bai, log, tip, uti, parte, valor, area, m2) in cur.execute(
            "SELECT * FROM bruto"):
        if not ano or not mes or not valor or valor <= 0:
            continue
        n = inteiro(num)
        lat, lon, prec = localizar(cl, n)
        prec_cont[prec] += 1
        oficial = logr.get(cl)
        nome_rua = (oficial[0] if oficial and oficial[0] else bonito(log))
        if cdb in bairros:
            nome_b, zona = bairros[cdb]
        elif norm(bai) in bairro_por_nome:
            nome_b, zona = bairro_por_nome[norm(bai)]
        elif oficial and norm(oficial[1]) in bairro_por_nome:
            nome_b, zona = bairro_por_nome[norm(oficial[1])]
        else:
            nome_b, zona = bai.title(), ""
        if area and area > 0:
            m2 = valor / area if not m2 else m2
        else:
            area, m2 = None, None
        lote.append((ano, mes, ano * 100 + mes, nome_b, norm(nome_b), zona, cl, nome_rua,
                     norm(nome_rua), num, comp, tip.replace("_", " "), uti, parte, valor, area,
                     round(m2, 2) if m2 else None, lat, lon, prec))
        if len(lote) >= 50000:
            c.executemany("INSERT INTO itbi (ano,mes,periodo,bairro,bairro_norm,zona,cl,logradouro,"
                          "rua_norm,numero,complemento,tipologia,utilizacao,parte,valor,area,valor_m2,"
                          "lat,lon,prec) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", lote)
            n_total += len(lote)
            lote = []
    c.executemany("INSERT INTO itbi (ano,mes,periodo,bairro,bairro_norm,zona,cl,logradouro,"
                  "rua_norm,numero,complemento,tipologia,utilizacao,parte,valor,area,valor_m2,"
                  "lat,lon,prec) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", lote)
    n_total += len(lote)
    for nome, cols in (("ix_itbi_bairro", "bairro_norm, periodo"), ("ix_itbi_zona", "zona, periodo"),
                       ("ix_itbi_cl", "cl"), ("ix_itbi_lat", "lat")):
        c.execute(f"CREATE INDEX {nome} ON itbi ({cols})")
    c.execute("DROP TABLE IF EXISTS itbi_meta")
    c.execute("CREATE TABLE itbi_meta (chave TEXT PRIMARY KEY, valor TEXT)")
    c.execute("INSERT INTO itbi_meta VALUES ('importado_em', datetime('now','localtime'))")
    c.commit()
    c.execute("ANALYZE")
    print(f"✅ itbi: {n_total:,} transações")
    rot = {1: "número exato", 2: "nº vizinho na mesma rua", 3: "só a rua", 0: "sem coordenada"}
    for p, q in sorted(prec_cont.items(), key=lambda x: -x[1]):
        print(f"   {rot[p]:<26} {q:>9,}  ({100*q/max(n_total,1):.1f}%)")


def main() -> None:
    args = set(sys.argv[1:])
    if "--baixar" in args:
        baixar_planilhas()
    c = conn()
    if "--baixar" in args or not existe(c, "bruto"):
        importar_planilhas(c)
    if "--refazer" in args or not existe(c, "np"):
        importar_np(c)
    if "--refazer" in args or not existe(c, "logradouros"):
        importar_logradouros(c)
    if "--refazer" in args or not existe(c, "bairros"):
        importar_bairros(c)
    montar_itbi(c)
    c.close()


if __name__ == "__main__":
    main()
