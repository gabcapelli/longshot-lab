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


def sondar(n_amostra=80, dias_atras=120):
    """
    A pergunta que decide se o estudo e viavel: em quantos mercados eu
    consigo o preco de 24h ANTES do fim?

    A sonda anterior mostrou 100% de outcomePrices em formato 1/0 -- mas
    numa amostra so de mercados criados no mesmo dia (ordenar por id
    decrescente pega os recem-criados, que sao mercados de esports que duram
    horas). Um deles voltou com UM ponto de historico. Se isso valer em
    geral, o desenho cai, porque nao existe "preco de 24h antes".

    Esta versao vai atras de mercados que fecharam ha mais tempo e mede a
    distribuicao de historico disponivel, em vez de olhar um exemplo.
    """
    from datetime import datetime, timedelta, timezone as _tz
    limite = (datetime.now(_tz.utc) - timedelta(days=dias_atras)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Tenta filtrar por data de fim; se a API ignorar o filtro, cai para
    # paginacao profunda ordenada por endDate.
    tentativas = [
        {"order": "endDate", "ascending": "false", "end_date_max": limite},
        {"order": "endDate", "ascending": "false", "endDateMax": limite},
        {"order": "endDate", "ascending": "false"},
    ]
    lote, usado = [], None
    for params in tentativas:
        try:
            r = _buscar_lote(limit=100, **params)
        except RuntimeError as e:
            print(f"  variante {list(params)} falhou: {e}")
            continue
        if not r:
            continue
        fim0 = str(r[0].get("endDate", ""))
        print(f"  variante {list(params)}: primeiro endDate={fim0}")
        lote, usado = r, params
        if fim0 and fim0 < limite:   # o filtro pegou
            break
    if not lote:
        print("NENHUMA variante devolveu mercados")
        return
    print(f"\nusando: {usado}")

    # Junta uma amostra, pulando adiante se os primeiros forem recentes demais
    amostra, offset = [], 0
    while len(amostra) < n_amostra and offset < 3000:
        try:
            r = _buscar_lote(limit=100, offset=offset, **usado)
        except RuntimeError:
            break
        if not r:
            break
        for m in r:
            fim = str(m.get("endDate", ""))
            if fim and fim < limite:
                amostra.append(m)
        offset += 100
        time.sleep(0.1)
    print(f"amostra de {len(amostra)} mercados encerrados ha mais de {dias_atras} dias\n")
    if not amostra:
        print("Nenhum mercado antigo encontrado -- a paginacao nao alcanca.")
        return

    print("=" * 70)
    print("FORMATOS DE outcomePrices")
    tally = {}
    for m in amostra:
        pad = _padrao_precos(_talvez_json(_campo(m, "outcomePrices")))
        tally[pad] = tally.get(pad, 0) + 1
    for pad, c in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"  {c:>4} ({c/len(amostra):5.1%})  {pad}")

    print("\n" + "=" * 70)
    print("STATUS DE RESOLUCAO E VOLUME")
    uma, sem_vol = {}, 0
    for m in amostra:
        st = str(m.get("umaResolutionStatuses"))
        uma[st] = uma.get(st, 0) + 1
        if _campo(m, "volumeNum", "volume") is None:
            sem_vol += 1
    for st, c in sorted(uma.items(), key=lambda kv: -kv[1])[:6]:
        print(f"  {c:>4}  umaResolutionStatuses={st}")
    print(f"  sem volume legivel: {sem_vol}/{len(amostra)}")

    print("\n" + "=" * 70)
    print("HISTORICO DE PRECO -- A PERGUNTA QUE DECIDE O ESTUDO")
    pontos, com_24h, spans, erros = [], 0, [], 0
    from datetime import datetime as _dt
    for m in amostra[:n_amostra]:
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
        pontos.append(len(h))
        if h:
            spans.append((h[-1][0] - h[0][0]) / 86400.0)
            if any(t <= fim_ts - 24 * 3600 for t, _ in h):
                com_24h += 1
        time.sleep(0.12)
    n = len(pontos)
    if n:
        pontos_ord = sorted(pontos)
        print(f"  mercados testados: {n} (erros de busca: {erros})")
        print(f"  pontos de historico -- min={pontos_ord[0]} "
              f"mediana={pontos_ord[n//2]} max={pontos_ord[-1]}")
        print(f"  com 1 ponto ou menos: {sum(1 for x in pontos if x <= 1)}")
        if spans:
            sp = sorted(spans)
            print(f"  janela coberta (dias) -- mediana={sp[len(sp)//2]:.1f} max={sp[-1]:.1f}")
        print(f"  >>> COM PRECO A 24h DO FIM: {com_24h}/{n} ({com_24h/n:.1%})")
        print()
        if com_24h / n < 0.5:
            print("  VEREDITO: o desenho de 'preco a 24h do fim' NAO se sustenta")
            print("            nesta base. Seria preciso mudar o ponto de medida.")
        else:
            print("  VEREDITO: o desenho se sustenta.")


if __name__ == "__main__":
    import sys
    if "--sondar" in sys.argv:
        sondar()
