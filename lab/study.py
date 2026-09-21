"""
Pipeline: vies favorito-azarao em mercados de previsao (Polymarket).

A pergunta: azarao custa mais do que vale? Ou seja, entre os mercados que o
Polymarket precificou a 5%, o evento aconteceu MENOS de 5% das vezes?

Desenho:
  1. Coleta mercados binarios ja resolvidos.
  2. Para cada um, pega o preco a uma distancia FIXA do fim (default 24h) --
     nao o preco final. O preco final converge para o desfecho por construcao;
     usa-lo seria medir a propria resposta.
  3. Compara preco contra desfecho, por faixa de preco pre-registrada.
  4. Testa contra a nula de mercado calibrado (simula desfechos a partir dos
     proprios precos).
  5. Backtest da regra de vender azarao, com custo de execucao.
  6. Divide por data em in-sample e out-of-sample.

O passo 4 e o que separa este estudo de um grafico bonito: em bucket pequeno,
qualquer ruido parece vies.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

from lab import fetch
from lab.analise import (BUCKETS, agregar, backtest_vender_azarao,
                         tabela_calibracao, teste_vies)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "resultados")
LIMIAR_PRINCIPAL = 0.10   # pre-registrado


def log(m):
    print(m, flush=True)


def _ts(iso):
    try:
        return int(datetime.fromisoformat(str(iso).replace("Z", "+00:00")).timestamp())
    except (ValueError, TypeError):
        return None


def coletar(max_mercados, volume_min, lead_horas, pausa=0.08, usar_cache=True):
    """Devolve (lista de mercados com preco no lead, contagem de descartes)."""
    cache = os.path.join(fetch.CACHE_DIR, f"mercados_{max_mercados}_{lead_horas}h.json")
    if usar_cache and os.path.exists(cache):
        with open(cache) as f:
            d = json.load(f)
        log(f"      cache: {len(d['mercados'])} mercados")
        return d["mercados"], d["descartes"]

    descartes, candidatos, offset = {}, [], 0
    log(f"[1/5] Coletando mercados resolvidos (alvo {max_mercados})...")
    while len(candidatos) < max_mercados:
        try:
            brutos = fetch.gamma_markets(limit=100, offset=offset)
        except RuntimeError as e:
            log(f"      parou de paginar: {e}")
            break
        if isinstance(brutos, dict):
            brutos = brutos.get("data", brutos.get("markets", []))
        if not brutos:
            break
        for m in brutos:
            lido, motivo = fetch.interpretar(m)
            if lido is None:
                descartes[motivo] = descartes.get(motivo, 0) + 1
                continue
            if lido["volume"] < volume_min:
                descartes["volume baixo"] = descartes.get("volume baixo", 0) + 1
                continue
            candidatos.append(lido)
        offset += 100
        time.sleep(pausa)
        if offset % 1000 == 0:
            log(f"      {offset} varridos, {len(candidatos)} candidatos")

    log(f"      {len(candidatos)} candidatos; buscando preco a {lead_horas}h do fim...")
    mercados = []
    for i, c in enumerate(candidatos[:max_mercados]):
        fim = _ts(c["fim"])
        if fim is None:
            descartes["data ilegivel"] = descartes.get("data ilegivel", 0) + 1
            continue
        alvo = fim - lead_horas * 3600
        try:
            hist = fetch.historico_preco(c["token_sim"])
        except RuntimeError:
            descartes["historico indisponivel"] = descartes.get("historico indisponivel", 0) + 1
            continue
        time.sleep(pausa)
        anteriores = [(t, pr) for t, pr in hist if t <= alvo]
        if not anteriores:
            descartes["sem preco antes do lead"] = descartes.get("sem preco antes do lead", 0) + 1
            continue
        t_uso, preco = anteriores[-1]
        # o ponto tem de estar perto do alvo; senao o mercado mal negociou
        if alvo - t_uso > 48 * 3600:
            descartes["preco velho demais"] = descartes.get("preco velho demais", 0) + 1
            continue
        if not (0.0 < preco < 1.0):
            descartes["preco fora de (0,1)"] = descartes.get("preco fora de (0,1)", 0) + 1
            continue
        mercados.append({**c, "preco": float(preco), "ts_preco": int(t_uso), "ts_fim": fim})
        if (i + 1) % 250 == 0:
            log(f"      {i+1}/{len(candidatos)} precos obtidos ({len(mercados)} validos)")

    os.makedirs(fetch.CACHE_DIR, exist_ok=True)
    with open(cache, "w") as f:
        json.dump({"mercados": mercados, "descartes": descartes}, f)
    return mercados, descartes


def semana(ts):
    d = datetime.fromtimestamp(ts, tz=timezone.utc).isocalendar()
    return f"{d[0]}-W{d[1]:02d}"


def analisar(mercados, rotulo, limiar, spread, reps):
    p = np.array([m["preco"] for m in mercados], dtype=float)
    y = np.array([m["desfecho_sim"] for m in mercados], dtype=float)
    ts = np.array([m["ts_fim"] for m in mercados], dtype=float)
    trades = backtest_vender_azarao(p, y, ts, limiar=limiar, spread=spread)
    blocos = [semana(t["ts"]) for t in trades]
    return {
        "rotulo": rotulo, "n_mercados": len(p),
        "calibracao": tabela_calibracao(p, y),
        "vies": teste_vies(p, y, reps=reps),
        "backtest": agregar(trades, blocos),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Vies favorito-azarao em prediction markets")
    ap.add_argument("--max-mercados", type=int, default=3000)
    ap.add_argument("--volume-min", type=float, default=5000.0)
    ap.add_argument("--lead-horas", type=int, default=24)
    ap.add_argument("--limiar", type=float, default=LIMIAR_PRINCIPAL)
    ap.add_argument("--spread", type=float, default=0.01)
    ap.add_argument("--frac-is", type=float, default=0.6)
    ap.add_argument("--reps", type=int, default=5000)
    ap.add_argument("--sem-cache", action="store_true")
    args = ap.parse_args(argv)

    t0 = time.time()
    os.makedirs(SAIDA, exist_ok=True)
    mercados, descartes = coletar(args.max_mercados, args.volume_min,
                                  args.lead_horas, usar_cache=not args.sem_cache)
    log(f"      {len(mercados)} mercados utilizaveis")
    for motivo, n in sorted(descartes.items(), key=lambda kv: -kv[1]):
        log(f"        descartado por {motivo}: {n}")
    if len(mercados) < 100:
        log("ERRO: mercados de menos para concluir qualquer coisa.")
        return 1

    mercados.sort(key=lambda m: m["ts_fim"])
    corte = int(len(mercados) * args.frac_is)
    log(f"[2/5] Divisao temporal: {corte} in-sample | {len(mercados)-corte} out-of-sample")

    log("[3/5] Calibracao e teste contra a nula de mercado honesto...")
    res = {
        "tudo": analisar(mercados, "tudo", args.limiar, args.spread, args.reps),
        "in_sample": analisar(mercados[:corte], "in-sample", args.limiar, args.spread, args.reps),
        "out_of_sample": analisar(mercados[corte:], "out-of-sample", args.limiar, args.spread, args.reps),
    }
    for k, v in res.items():
        vi = v["vies"]
        log(f"      {k:<14} n={vi.get('n',0):>5} vies={vi.get('vies',float('nan')):+.4f} "
            f"p={vi.get('p_valor',1):.4f} | backtest n={v['backtest'].get('n',0)}")

    log("[4/5] Sensibilidade ao custo de execucao...")
    p = np.array([m["preco"] for m in mercados[corte:]], dtype=float)
    y = np.array([m["desfecho_sim"] for m in mercados[corte:]], dtype=float)
    ts = np.array([m["ts_fim"] for m in mercados[corte:]], dtype=float)
    sens = []
    for sp in (0.0, 0.005, 0.01, 0.02):
        tr = backtest_vender_azarao(p, y, ts, limiar=args.limiar, spread=sp)
        ag = agregar(tr, [semana(t["ts"]) for t in tr])
        sens.append({"spread": sp, **ag})
        log(f"      spread {sp:.3f}: n={ag.get('n',0)} exp={ag.get('exp_r',float('nan')):+.4f}R")

    log("[5/5] Relatorio...")
    ctx = {"args": vars(args), "descartes": descartes, "n": len(mercados),
           "segundos": round(time.time() - t0, 1)}
    escrever(ctx, res, sens)
    with open(os.path.join(SAIDA, "resultado.json"), "w") as f:
        json.dump({"contexto": ctx, "resultados": res, "sensibilidade": sens},
                  f, indent=2, default=float)
    log(f"      resultados/relatorio.md ({ctx['segundos']}s)")
    return 0


def escrever(ctx, res, sens):
    L = ["# Vies favorito-azarao em prediction markets — resultado\n"]
    L.append(f"Gerado em {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC · "
             f"{ctx['n']} mercados resolvidos · preco a "
             f"{ctx['args']['lead_horas']}h do fim · {ctx['segundos']}s\n")

    oos = res["out_of_sample"]
    v = oos["vies"]
    L.append("## Leitura rapida\n")
    if v.get("n", 0) == 0:
        L.append("Sem mercados no out-of-sample.\n")
    else:
        if v["p_valor"] < 0.05 and v["vies"] > 0:
            veredito = ("**Existe vies: azarao custa mais do que vale.** O preco "
                        "medio fica acima da frequencia com que o evento acontece, "
                        "e a diferenca e maior do que o acaso explicaria.")
        elif v["p_valor"] < 0.05 and v["vies"] < 0:
            veredito = ("**Existe vies, na direcao CONTRARIA a esperada:** azarao "
                        "custa menos do que vale.")
        else:
            veredito = ("**Sem evidencia de vies.** O desvio observado cabe dentro "
                        "do que a sorte produziria num mercado calibrado.")
        L.append(veredito + "\n")
        L.append(f"- Vies medio (preco − desfecho), out-of-sample: **{v['vies']:+.4f}** "
                 f"em {v['n']} mercados, p = {v['p_valor']:.4f}\n")
        L.append(f"- Faixa que a nula produziria: "
                 f"[{v['nula_ic'][0]:+.4f}, {v['nula_ic'][1]:+.4f}]\n")
        b = oos["backtest"]
        if b.get("n", 0):
            L.append(f"- Vender azarao (preco ≤ {ctx['args']['limiar']:.2f}, spread "
                     f"{ctx['args']['spread']:.3f}): {b['n']} apostas, "
                     f"**{b['exp_r']:+.4f}R**, IC 95% "
                     f"[{b['ic_r'][0]:+.3f}, {b['ic_r'][1]:+.3f}]\n")

    L.append("\n## Como ler\n")
    L.append("- **Vies** = preco medio menos frequencia real. Positivo significa "
             "que o mercado cobra mais do que o evento vale.\n")
    L.append("- A **nula** nao e zero: e o que a sorte produziria se cada mercado "
             "fosse uma moeda honesta com a probabilidade que ele mesmo anuncia. "
             "So desvio maior que essa faixa conta.\n")
    L.append("- **R** = valor arriscado. Vender SIM a p arrisca (1−p) para ganhar p.\n")

    for chave, titulo in (("in_sample", "In-sample"), ("out_of_sample", "Out-of-sample")):
        r = res[chave]
        L.append(f"\n## Calibracao — {titulo} ({r['n_mercados']} mercados)\n")
        L.append("| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |")
        L.append("|---|---|---|---|---|---|")
        for b in r["calibracao"]:
            if b["n"] == 0:
                L.append(f"| {b['lo']:.0%}–{b['hi']:.0%} | 0 | — | — | — | — |")
                continue
            marca = " **\\***" if b["fora_do_ic"] else ""
            L.append(f"| {b['lo']:.0%}–{b['hi']:.0%} | {b['n']} | {b['preco_medio']:.3f} | "
                     f"{b['freq_real']:.3f} | [{b['freq_ic'][0]:.3f}, {b['freq_ic'][1]:.3f}] | "
                     f"{b['diferenca']:+.3f}{marca} |")
        L.append("")
        L.append("*\\* preco medio fora do IC da frequencia observada.*\n")

    L.append("\n## Sensibilidade ao custo de execucao\n")
    L.append("| Spread | Apostas | Expectancia | IC 95% |")
    L.append("|---|---|---|---|")
    for s in sens:
        if not s.get("n"):
            L.append(f"| {s['spread']:.3f} | 0 | — | — |")
            continue
        L.append(f"| {s['spread']:.3f} | {s['n']} | {s['exp_r']:+.4f}R | "
                 f"[{s['ic_r'][0]:+.3f}, {s['ic_r'][1]:+.3f}] |")
    L.append("")
    L.append("Um vies pode ser real e mesmo assim nao ser operavel. Num mercado de "
             "5 centavos, 1 centavo de spread leva um quinto do premio. Esta tabela "
             "separa 'existe' de 'da para explorar'.\n")

    L.append("\n## Descartes na coleta\n")
    L.append("| Motivo | Mercados |")
    L.append("|---|---|")
    for motivo, n in sorted(ctx["descartes"].items(), key=lambda kv: -kv[1]):
        L.append(f"| {motivo} | {n} |")
    L.append("")
    L.append("Se um motivo dominar, o problema provavelmente e o leitor da API e "
             "nao o mercado. Por isso a contagem aparece no relatorio.\n")

    L.append("\n## Parametros\n```")
    for k, val in ctx["args"].items():
        L.append(f"{k} = {val}")
    L.append("```\n")
    with open(os.path.join(SAIDA, "relatorio.md"), "w") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
