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


def sondar(n_amostra=400, n_detalhe=3):
    """
    Descobre COMO ler o desfecho de um mercado resolvido.

    A primeira sonda revelou que `outcomePrices` nem sempre traz 1/0 em
    mercado fechado -- mercados antigos vem zerados. Sem saber em quantos
    mercados cada metodo funciona, o estudo rodaria sobre uma amostra
    silenciosamente enviesada. Esta sonda tabula os formatos e testa as
    alternativas de leitura do desfecho.
    """
    # A ordem padrao devolve os mercados mais ANTIGOS (ids 12, 17, 18 de 2020).
    # Tenta inverter para pegar os recentes, e relata qual variante funcionou.
    brutos, variante = None, None
    for params in ({"order": "id", "ascending": "false"},
                   {"order": "endDate", "ascending": "false"},
                   {}):
        try:
            r = gamma_markets(limit=100, **params)
            if isinstance(r, dict):
                r = r.get("data", r.get("markets", []))
            if r:
                brutos, variante = r, (params or "ordem padrao")
                break
        except RuntimeError as e:
            print(f"  variante {params} falhou: {e}")
    if not brutos:
        print("NENHUMA variante de ordenacao funcionou")
        return
    print(f"ordenacao usada: {variante}")
    print(f"primeiro id={brutos[0].get('id')} endDate={brutos[0].get('endDate')}")
    print(f"ultimo   id={brutos[-1].get('id')} endDate={brutos[-1].get('endDate')}\n")

    # Tabela de formatos de outcomePrices sobre uma amostra maior
    print("=" * 70)
    print(f"FORMATOS DE outcomePrices em ate {n_amostra} mercados fechados")
    tally, exemplos, offset, vistos = {}, {}, 0, 0
    kw = variante if isinstance(variante, dict) else {}
    while vistos < n_amostra:
        try:
            lote = gamma_markets(limit=100, offset=offset, **kw)
        except RuntimeError:
            break
        if isinstance(lote, dict):
            lote = lote.get("data", lote.get("markets", []))
        if not lote:
            break
        for m in lote:
            pad = _padrao_precos(_talvez_json(_campo(m, "outcomePrices")))
            tally[pad] = tally.get(pad, 0) + 1
            exemplos.setdefault(pad, m)
            vistos += 1
        offset += 100
        time.sleep(0.1)
    for pad, c in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"  {c:>5}  ({c/max(vistos,1):5.1%})  {pad}")
    print(f"  total: {vistos}")

    # Campos que podem carregar o desfecho
    print("\n" + "=" * 70)
    print("CAMPOS LIGADOS A RESOLUCAO, por formato")
    for pad, m in exemplos.items():
        print(f"\n[{pad}] id={m.get('id')} | {str(m.get('question'))[:60]}")
        for k in ("closed", "active", "archived", "closedTime", "endDate",
                  "umaResolutionStatuses", "lastTradePrice", "bestBid",
                  "bestAsk", "spread", "liquidityNum", "volumeNum"):
            print(f"    {k}: {m.get(k)!r}")

    # O historico do CLOB resolve o desfecho quando outcomePrices nao resolve?
    print("\n" + "=" * 70)
    print("HISTORICO DO CLOB (ultimo preco indica o desfecho?)")
    testados = 0
    for pad, m in exemplos.items():
        toks = _talvez_json(_campo(m, "clobTokenIds"))
        if not toks:
            print(f"  [{pad}] sem clobTokenIds")
            continue
        try:
            h = historico_preco(str(toks[0]))
        except RuntimeError as e:
            print(f"  [{pad}] historico falhou: {e}")
            continue
        if not h:
            print(f"  [{pad}] historico VAZIO ({len(h)} pontos)")
        else:
            print(f"  [{pad}] {len(h)} pontos | primeiro={h[0][1]:.3f} "
                  f"ultimo={h[-1][1]:.3f} | outcomePrices={m.get('outcomePrices')}")
        testados += 1
        time.sleep(0.15)
        if testados >= n_detalhe:
            break


if __name__ == "__main__":
    import sys
    if "--sondar" in sys.argv:
        sondar()
