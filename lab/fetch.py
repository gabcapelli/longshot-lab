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
    espera, ultimo = 1.0, None
    for _ in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "longshot-lab"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
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


def coletar_periodo(dias_min_fechado=7, dias_max=540, volume_min=10000,
                    alvo=3000, pausa=0.08, verboso=True):
    """
    Varre mercados que JA TERMINARAM, caminhando para tras no tempo.

    Por que nao basta paginar: ordenado por endDate decrescente, os primeiros
    milhares de mercados tem data de fim em 2028-2029 -- sao apostas de
    horizonte longo. Paginar por offset nunca alcanca o passado. A solucao e
    mover a janela: a cada rodada, o teto vira a menor data de fim ja vista.

    `dias_min_fechado` evita mercados recem-encerrados, cuja resolucao ainda
    pode estar "proposed" e mudar.
    """
    from datetime import datetime, timedelta, timezone as _tz
    agora = datetime.now(_tz.utc)
    teto = agora - timedelta(days=dias_min_fechado)
    piso = agora - timedelta(days=dias_max)
    coletados, rodadas = {}, 0

    while len(coletados) < alvo and teto > piso and rodadas < 400:
        rodadas += 1
        params = {"order": "endDate", "ascending": "false",
                  "end_date_max": _iso(teto), "volume_num_min": volume_min}
        fins_vistos, novos = [], 0
        for offset in (0, 100, 200, 300, 400):
            try:
                lote = _buscar_lote(limit=100, offset=offset, **params)
            except RuntimeError as e:
                if verboso:
                    print(f"      lote falhou ({e}); segue")
                break
            if not lote:
                break
            for m in lote:
                mid = str(m.get("id") or m.get("conditionId") or "")
                fim = str(m.get("endDate") or "")
                if fim:
                    fins_vistos.append(fim)
                if mid and mid not in coletados:
                    coletados[mid] = m
                    novos += 1
            time.sleep(pausa)
            if len(coletados) >= alvo:
                break
        if not fins_vistos:
            break
        # move a janela para tras do menor fim visto; se nao andou, recua um dia
        menor = min(fins_vistos)
        try:
            novo_teto = datetime.fromisoformat(menor.replace("Z", "+00:00")) - timedelta(seconds=1)
        except ValueError:
            novo_teto = teto - timedelta(days=1)
        if novo_teto >= teto or novos == 0:
            novo_teto = teto - timedelta(days=1)
        teto = novo_teto
        if verboso and rodadas % 10 == 0:
            print(f"      {len(coletados)} mercados; janela ate {teto:%Y-%m-%d}")
    return list(coletados.values())


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
