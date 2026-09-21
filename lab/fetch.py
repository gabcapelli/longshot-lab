"""
Coleta de mercados resolvidos do Polymarket.

Duas APIs publicas:
  - Gamma  (gamma-api.polymarket.com)  -> metadados e desfecho dos mercados
  - CLOB   (clob.polymarket.com)       -> historico de preco de cada token

O parser e deliberadamente TOLERANTE: campos sao lidos por varios nomes
possiveis e qualquer mercado que nao se encaixe e descartado com motivo
registrado, em vez de derrubar a coleta inteira. A contagem de descartes por
motivo sai no relatorio -- se um motivo dominar, o problema e o parser e nao
o mercado, e isso precisa ficar visivel em vez de silencioso.

Use `python -m lab.fetch --sondar` para imprimir a estrutura crua de alguns
mercados antes de confiar no parser.
"""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")


def _get(url, tentativas=4, timeout=30):
    """
    Nao reexecuta erro 5xx: a Gamma devolve 500 de forma deterministica para
    janelas de data antigas, e insistir so gasta tempo. Na primeira rodada
    sobre dado real, 37 dos 62 minutos foram gastos repetindo ~150 janelas que
    nunca iam responder. Erro de rede continua com retentativa, porque esse
    sim costuma ser transitorio.
    """
    espera, ultimo = 1.0, None
    for _ in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "longshot-lab"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if 500 <= e.code < 600:
                raise RuntimeError(f"HTTP {e.code} (sem retentativa): {url}") from e
            ultimo = e
            time.sleep(espera)
            espera *= 2
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            ultimo = e
            time.sleep(espera)
            espera *= 2
    raise RuntimeError(f"falhou apos {tentativas} tentativas: {url} -- {ultimo}")


def gamma_markets(limit=100, offset=0, **extra):
    params = {"closed": "true", "limit": limit, "offset": offset}
    params.update(extra)
    return _get(f"{GAMMA}/markets?{urllib.parse.urlencode(params)}")


def historico_preco(token_id, fidelity=60):
    """Serie de preco do token. Devolve lista de (timestamp_seg, preco)."""
    url = f"{CLOB}/prices-history?market={token_id}&interval=max&fidelity={fidelity}"
    d = _get(url)
    hist = d.get("history", d if isinstance(d, list) else [])
    out = []
    for ponto in hist:
        try:
            out.append((int(ponto["t"]), float(ponto["p"])))
        except (KeyError, TypeError, ValueError):
            continue
    out.sort()
    return out


# ---------------------------------------------------------------------------
# Parser tolerante
# ---------------------------------------------------------------------------

def _talvez_json(v):
    """Gamma devolve varias listas como STRING de JSON. Aceita os dois casos."""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return None
    return v


def _campo(m, *nomes):
    for n in nomes:
        if m.get(n) not in (None, ""):
            return m[n]
    return None


def interpretar(m):
    """
    Converte um mercado cru da Gamma no minimo que o estudo precisa.
    Devolve dict ou (None, motivo_do_descarte).
    """
    precos = _talvez_json(_campo(m, "outcomePrices", "outcome_prices"))
    nomes = _talvez_json(_campo(m, "outcomes"))
    tokens = _talvez_json(_campo(m, "clobTokenIds", "clob_token_ids"))

    if not precos or not nomes or len(precos) != 2 or len(nomes) != 2:
        return None, "nao e binario"
    try:
        precos = [float(x) for x in precos]
    except (TypeError, ValueError):
        return None, "preco nao numerico"

    # Mercado resolvido tem preco final em 1/0. Se nao convergiu, ou nao
    # resolveu, ou resolveu de forma ambigua -- nos dois casos nao serve.
    alto = max(precos)
    if alto < 0.99 or min(precos) > 0.01:
        return None, "sem desfecho definido"
    desfecho_idx = 0 if precos[0] > precos[1] else 1

    if not tokens or len(tokens) != 2:
        return None, "sem token do CLOB"

    fim = _campo(m, "endDate", "end_date", "endDateIso")
    if not fim:
        return None, "sem data de fim"

    volume = _campo(m, "volumeNum", "volume")
    try:
        volume = float(volume) if volume is not None else 0.0
    except (TypeError, ValueError):
        volume = 0.0

    return {
        "id": str(_campo(m, "id", "conditionId") or ""),
        # closedTime e o fechamento REAL; endDate e o horario previsto e pode
        # estar horas adiante (sonda viu endDate 16:30 com closedTime 13:10).
        # Ancorar no previsto joga a medida para antes de existir negociacao.
        "fechado_em": _campo(m, "closedTime"),
        "pergunta": _campo(m, "question", "title") or "",
        "slug": _campo(m, "slug") or "",
        "nomes": [str(x) for x in nomes],
        "token_sim": str(tokens[0]),
        "desfecho_sim": 1 if desfecho_idx == 0 else 0,
        "fim": str(fim),
        "volume": volume,
    }, None


def _padrao_precos(precos):
    """Rotula o formato de outcomePrices, para tabular o que a API devolve."""
    if not precos or len(precos) != 2:
        return "malformado"
    try:
        a, b = float(precos[0]), float(precos[1])
    except (TypeError, ValueError):
        return "nao numerico"
    if {round(a, 6), round(b, 6)} == {0.0, 1.0}:
        return "1/0 (desfecho explicito)"
    if a == 0.0 and b == 0.0:
        return "0/0 (zerado)"
    if abs(a + b - 1.0) < 0.02:
        return "soma 1 (preco vivo)"
    return f"outro ({a}, {b})"


def _buscar_lote(limit=100, offset=0, **extra):
    r = gamma_markets(limit=limit, offset=offset, **extra)
    if isinstance(r, dict):
        r = r.get("data", r.get("markets", []))
    return r or []


def _resumo_lote(lote):
    fins = sorted(str(m.get("endDate") or "") for m in lote if m.get("endDate"))
    vols = [v for v in (_campo(m, "volumeNum", "volume") for m in lote) if v is not None]
    vols = sorted(float(v) for v in vols)
    return {
        "n": len(lote),
        "fim_min": fins[0][:10] if fins else "?",
        "fim_max": fins[-1][:10] if fins else "?",
        "vol_min": vols[0] if vols else None,
        "vol_mediana": vols[len(vols) // 2] if vols else None,
    }


def _buscar_lote(limit=100, offset=0, **extra):
    r = gamma_markets(limit=limit, offset=offset, **extra)
    if isinstance(r, dict):
        r = r.get("data", r.get("markets", []))
    return r or []


# Filtros confirmados por sonda contra a API (2026-09-21):
#   volume_num_min  ACEITO
#   end_date_max    ACEITO
#   start_date_min  ACEITO
#   volumeNumMin / volume_min / endDateMax / end_date_min  IGNORADOS em silencio
#   liquidity_num_min  derruba a API com HTTP 500
# Filtro ignorado nao da erro: devolve o lote de sempre. Nao acrescente nome
# aqui sem passar pela sonda.
FILTROS_OK = ("volume_num_min", "end_date_max", "start_date_min")


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def coletar_periodo(dias_min_fechado=7, dias_max=180, volume_min=10000,
                    por_dia=40, alvo=4000, pausa=0.08, verboso=True):
    """
    Varre mercados JA ENCERRADOS, caminhando para tras um dia por vez.

    Por que nao basta paginar por offset: ordenado por endDate decrescente,
    os primeiros milhares de mercados tem data de fim em 2028-2029 (apostas de
    horizonte longo). A paginacao nunca alcanca o passado. A janela de data
    resolve.

    Por que `por_dia` em vez de esgotar cada dia: o Polymarket fecha centenas
    de mercados por dia, quase todos de esporte. Esgotar um dia antes de
    passar ao anterior gastaria a cota inteira em duas semanas de calendario,
    e o corte in/out-of-sample precisa de meses. Amostrar ate `por_dia` por
    dia da cobertura temporal uniforme com a mesma quantidade de chamadas.

    `dias_min_fechado` pula os mercados recem-encerrados, cuja resolucao pode
    estar apenas "proposed" e ainda mudar.
    """
    from datetime import datetime, timedelta, timezone as _tz
    agora = datetime.now(_tz.utc)
    coletados, dia, falhas_seguidas = {}, 0, 0
    total_dias = max(dias_max - dias_min_fechado, 1)
    # A Gamma responde 500 para janelas muito antigas. Depois de algumas
    # seguidas, nao ha mais historico alcancavel: parar em vez de varrer meses
    # de janelas mortas.
    MAX_FALHAS = 8

    while len(coletados) < alvo and dia < total_dias and falhas_seguidas < MAX_FALHAS:
        teto = agora - timedelta(days=dias_min_fechado + dia)
        params = {"order": "endDate", "ascending": "false",
                  "end_date_max": _iso(teto), "volume_num_min": volume_min}
        do_dia = 0
        for offset in (0, 100, 200):
            if do_dia >= por_dia or len(coletados) >= alvo:
                break
            try:
                lote = _buscar_lote(limit=100, offset=offset, **params)
            except RuntimeError as e:
                falhas_seguidas += 1
                if verboso and falhas_seguidas <= 3:
                    print(f"      janela {teto:%Y-%m-%d} falhou ({e})")
                break
            else:
                falhas_seguidas = 0
            if not lote:
                break
            for m in lote:
                if do_dia >= por_dia or len(coletados) >= alvo:
                    break
                mid = str(m.get("id") or m.get("conditionId") or "")
                if mid and mid not in coletados:
                    coletados[mid] = m
                    do_dia += 1
            time.sleep(pausa)
        dia += 1
        if verboso and dia % 10 == 0:
            print(f"      {len(coletados)} mercados; recuou ate {teto:%Y-%m-%d}")
    if verboso and falhas_seguidas >= MAX_FALHAS:
        print(f"      parou: a API nao devolve janelas anteriores a "
              f"{teto:%Y-%m-%d} (limite do historico alcancavel)")
    return list(coletados.values())


def precos_nos_leads(token_id, ancora_ts, leads=(6, 24), min_pontos=3,
                     max_defasagem_h=48):
    """
    Preco do token a N horas da ANCORA, numa unica busca.

    `min_pontos` exige que existam pelo menos N pontos de historico ANTES do
    instante medido, e que eles nao sejam todos identicos.

    Por que isso e obrigatorio: na primeira rodada sobre dado real, dois
    tercos dos mercados devolveram preco ~0,50 no lead de 6h. Nao era o
    mercado precificando meio a meio -- era o valor inicial de um mercado que
    ainda nao tinha negociado, lido como se fosse preco. O resultado saiu com
    p=0,025 e direcao invertida, inteiramente artefato.

    Preco so e preco depois que alguem negociou. Sem essa exigencia o estudo
    mede o valor padrao da plataforma, nao a opiniao do mercado.

    DEFASAGEM. O preco devolvido e o do ultimo negocio ANTES do instante
    medido, e `defasagem_h` diz quanto tempo antes. Isso importa mais do que
    parece: um azarao cujo ultimo negocio foi a 0,05 horas antes do fim, e que
    subiu e ganhou, seria registrado como "custava 0,05 e aconteceu" -- e isso
    sozinho fabrica a aparencia de azarao barato. Quem chama deve filtrar por
    defasagem e medir a sensibilidade do resultado a esse filtro.

    Devolve {horas: {"ts", "preco", "defasagem_h"}} para os leads validos.
    """
    hist = historico_preco(token_id)
    out = {}
    for horas in leads:
        alvo = ancora_ts - horas * 3600
        anteriores = [(t, p) for t, p in hist if t <= alvo]
        if len(anteriores) < min_pontos:
            continue
        precos_antes = [p for _t, p in anteriores]
        if max(precos_antes) - min(precos_antes) < 1e-9:
            continue          # serie inteira constante: nunca negociou
        t_uso, preco = anteriores[-1]
        defasagem_h = (alvo - t_uso) / 3600.0
        if defasagem_h > max_defasagem_h or not (0.0 < preco < 1.0):
            continue
        out[horas] = {"ts": int(t_uso), "preco": float(preco),
                      "defasagem_h": float(defasagem_h)}
    return out


def sondar(n_amostra=60):
    """
    Com os filtros ja descobertos, resta a pergunta que decide o desenho:
    em que fracao dos mercados existe preco a X horas do fim?
    """
    from datetime import datetime as _dt
    print("=" * 70)
    print("COLETA POR JANELA DE DATA (caminhando para tras)")
    mercados = coletar_periodo(dias_min_fechado=7, dias_max=540,
                               volume_min=10000, alvo=300)
    print(f"  {len(mercados)} mercados encerrados coletados")
    if not mercados:
        print("  NENHUM -- a estrategia de janela nao funcionou")
        return
    fins = sorted(str(m.get("endDate") or "")[:10] for m in mercados if m.get("endDate"))
    print(f"  datas de fim: de {fins[0]} a {fins[-1]}")

    tally = {}
    for m in mercados:
        pad = _padrao_precos(_talvez_json(_campo(m, "outcomePrices")))
        tally[pad] = tally.get(pad, 0) + 1
    print(f"  formatos de outcomePrices: {tally}")

    uteis = [m for m in mercados
             if _padrao_precos(_talvez_json(_campo(m, "outcomePrices"))) == "1/0 (desfecho explicito)"]
    print(f"  com desfecho legivel: {len(uteis)}/{len(mercados)}")

    print("\n" + "=" * 70)
    print("COBERTURA DE HISTORICO -- A PERGUNTA QUE DECIDE O DESENHO")
    leads = (1, 6, 24, 72)
    cobertura = {h: 0 for h in leads}
    pontos, testados, erros = [], 0, 0
    for m in uteis[:n_amostra]:
        toks = _talvez_json(_campo(m, "clobTokenIds"))
        fim_iso = _campo(m, "endDate")
        if not toks or not fim_iso:
            continue
        try:
            fim_ts = int(_dt.fromisoformat(str(fim_iso).replace("Z", "+00:00")).timestamp())
        except ValueError:
            continue
        try:
            h = historico_preco(str(toks[0]))
        except RuntimeError:
            erros += 1
            continue
        testados += 1
        pontos.append(len(h))
        for horas in leads:
            if any(t <= fim_ts - horas * 3600 for t, _ in h):
                cobertura[horas] += 1
        time.sleep(0.1)

    if not testados:
        print("  nenhum mercado testavel")
        return
    po = sorted(pontos)
    print(f"  testados: {testados} (erros: {erros})")
    print(f"  pontos de historico: min={po[0]} mediana={po[len(po)//2]} max={po[-1]}")
    print(f"  com <=1 ponto: {sum(1 for x in pontos if x <= 1)}/{testados}")
    print("\n  fracao com preco disponivel a N horas do fim:")
    for horas in leads:
        c = cobertura[horas]
        print(f"    {horas:>3}h antes: {c:>3}/{testados} ({c/testados:5.1%})")
    if cobertura[24] / testados >= 0.6:
        print("\n  VEREDITO: o lead de 24h se sustenta. Pode rodar o estudo.")
    else:
        melhor = max(leads, key=lambda h: (cobertura[h] / testados, -h))
        print(f"\n  VEREDITO: 24h tem cobertura baixa; melhor lead viavel e {melhor}h "
              f"({cobertura[melhor]/testados:.1%}).")


if __name__ == "__main__":
    import sys
    if "--sondar" in sys.argv:
        sondar()
