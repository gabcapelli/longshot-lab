"""
Pipeline: vies favorito-azarao em mercados de previsao (Polymarket).

A pergunta: entre os mercados precificados a 5%, o evento aconteceu menos de
5% das vezes? Se sim, azarao custa mais do que vale.

Desenho:
  1. Coleta mercados binarios ja resolvidos, amostrando por DIA de encerramento
     para cobrir meses (ver fetch.coletar_periodo).
  2. Para cada um, pega o preco a N horas do fim -- nunca o preco final, que
     converge para o desfecho por construcao e faria o estudo medir a propria
     resposta.
  3. Compara preco contra desfecho, por faixa de preco pre-registrada.
  4. Testa contra a nula de mercado calibrado.
  5. Backtest da regra de vender azarao, com custo de execucao.
  6. Divide por data em in-sample e out-of-sample.

SOBRE OS DOIS LEADS. Sonda de 2026-09-21 mediu a cobertura de historico:
6h existe em 100% dos mercados, 24h em apenas 50%. Usar so 24h restringiria
a amostra aos mercados de vida longa -- um recorte sistematicamente diferente
(os curtos sao esportivos). Entao 6h e o lead PRINCIPAL, por nao ter perda de
amostra, e 24h entra como secundario, com a ressalva de recorte.

A contrapartida: 6h antes do fim o preco ja e mais informado que 24h antes,
o que torna o teste mais DIFICIL de passar. Achar vies em 6h seria um achado
mais forte; nao achar pode ser em parte por isso. Esta assimetria esta no
relatorio, nao so aqui.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

from lab import fetch
from lab.analise import (agregar, backtest_vender_azarao, observacoes,
                         tabela_calibracao, teste_vies_azarao)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "resultados")


def log(m):
    print(m, flush=True)


def _ts(iso):
    """Aceita '2026-09-14T12:00:00Z' e '2026-09-14 13:10:48+00' (closedTime)."""
    if not iso:
        return None
    txt = str(iso).strip().replace("Z", "+00:00")
    if txt.endswith("+00"):
        txt += ":00"
    try:
        return int(datetime.fromisoformat(txt).timestamp())
    except (ValueError, TypeError):
        return None


def semana(ts):
    d = datetime.fromtimestamp(ts, tz=timezone.utc).isocalendar()
    return f"{d[0]}-W{d[1]:02d}"


def coletar(args, leads):
    cache = os.path.join(fetch.CACHE_DIR,
                         f"mkt_{args.alvo}_{args.dias_max}_{args.volume_min}.json")
    if not args.sem_cache and os.path.exists(cache):
        with open(cache) as f:
            d = json.load(f)
        log(f"      cache: {len(d['mercados'])} mercados")
        return d["mercados"], d["descartes"]

    log(f"[1/5] Coletando mercados encerrados (alvo {args.alvo}, "
        f"ate {args.dias_max} dias atras, volume >= {args.volume_min:,.0f})...")
    brutos = fetch.coletar_periodo(
        dias_min_fechado=args.dias_min_fechado, dias_max=args.dias_max,
        volume_min=args.volume_min, por_dia=args.por_dia, alvo=args.alvo)
    log(f"      {len(brutos)} mercados brutos; lendo precos...")

    descartes, mercados = {}, []
    for i, bruto in enumerate(brutos):
        lido, motivo = fetch.interpretar(bruto)
        if lido is None:
            descartes[motivo] = descartes.get(motivo, 0) + 1
            continue
        # Ancora no fechamento REAL quando existe; endDate e so o previsto.
        fim = _ts(lido.get("fechado_em")) or _ts(lido["fim"])
        if fim is None:
            descartes["data ilegivel"] = descartes.get("data ilegivel", 0) + 1
            continue
        try:
            precos = fetch.precos_nos_leads(lido["token_sim"], fim, leads=leads)
        except RuntimeError:
            descartes["historico indisponivel"] = descartes.get("historico indisponivel", 0) + 1
            continue
        time.sleep(0.07)
        if not precos:
            descartes["sem preco em nenhum lead"] = descartes.get("sem preco em nenhum lead", 0) + 1
            continue
        for horas in leads:
            if horas not in precos:
                k = f"sem preco no lead de {horas}h"
                descartes[k] = descartes.get(k, 0) + 1
        mercados.append({**lido, "ts_fim": fim,
                         "precos": {str(h): p for h, (_t, p) in precos.items()}})
        if (i + 1) % 400 == 0:
            log(f"      {i+1}/{len(brutos)} lidos ({len(mercados)} utilizaveis)")

    os.makedirs(fetch.CACHE_DIR, exist_ok=True)
    with open(cache, "w") as f:
        json.dump({"mercados": mercados, "descartes": descartes}, f)
    return mercados, descartes


def fracao_no_inicial(p, centro=0.5, tol=0.02):
    """
    Fracao dos precos colada no valor inicial da plataforma.

    Guarda automatica contra o erro que invalidou a primeira rodada: se muita
    massa estiver em ~0,50, o estudo esta lendo o preco padrao de mercados que
    nunca negociaram, e nao opiniao de mercado. O relatorio avisa sozinho em
    vez de depender de alguem reparar na tabela.
    """
    if len(p) == 0:
        return 0.0
    return float(np.mean(np.abs(np.asarray(p, dtype=float) - centro) <= tol))


def analisar(mercados, rotulo, limiar, spread, reps):
    p_sim = np.array([m["preco"] for m in mercados], dtype=float)
    y_sim = np.array([m["desfecho_sim"] for m in mercados], dtype=float)
    ts_m = np.array([m["ts_fim"] for m in mercados], dtype=float)
    # Os dois lados de cada mercado: o azarao costuma ser o lado NAO.
    P, Y, T, _ids = observacoes(p_sim, y_sim, ts_m)
    trades = backtest_vender_azarao(P, Y, T, limiar=limiar, spread=spread)
    blocos = [semana(t["ts"]) for t in trades]
    return {"rotulo": rotulo, "n_mercados": len(p_sim), "n_obs": int(len(P)),
            "fracao_no_inicial": fracao_no_inicial(p_sim),
            "calibracao": tabela_calibracao(P, Y),
            "vies_azarao": teste_vies_azarao(P, Y, limiar=limiar, reps=reps),
            "backtest": agregar(trades, blocos)}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Vies favorito-azarao em prediction markets")
    ap.add_argument("--alvo", type=int, default=4000)
    ap.add_argument("--dias-max", type=int, default=180)
    ap.add_argument("--dias-min-fechado", type=int, default=7)
    ap.add_argument("--por-dia", type=int, default=40)
    ap.add_argument("--volume-min", type=float, default=10000.0)
    ap.add_argument("--leads", default="6,24", help="horas antes do fim, separadas por virgula")
    ap.add_argument("--limiar", type=float, default=0.10)
    ap.add_argument("--spread", type=float, default=0.01)
    ap.add_argument("--frac-is", type=float, default=0.6)
    ap.add_argument("--reps", type=int, default=5000)
    ap.add_argument("--sem-cache", action="store_true")
    args = ap.parse_args(argv)

    leads = [int(x) for x in str(args.leads).split(",") if x.strip()]
    t0 = time.time()
    os.makedirs(SAIDA, exist_ok=True)

    mercados, descartes = coletar(args, leads)
    log(f"      {len(mercados)} mercados utilizaveis")
    for motivo, n in sorted(descartes.items(), key=lambda kv: -kv[1]):
        log(f"        {motivo}: {n}")
    if len(mercados) < 100:
        log("ERRO: mercados de menos para concluir qualquer coisa.")
        return 1

    fins = sorted(m["ts_fim"] for m in mercados)
    log(f"[2/5] Periodo coberto: {datetime.fromtimestamp(fins[0], tz=timezone.utc):%Y-%m-%d}"
        f" a {datetime.fromtimestamp(fins[-1], tz=timezone.utc):%Y-%m-%d}")

    resultados, sens = {}, {}
    for horas in leads:
        sub = [{**m, "preco": m["precos"][str(horas)]}
               for m in mercados if str(horas) in m["precos"]]
        cob = len(sub) / len(mercados)
        log(f"[3/5] Lead {horas}h: {len(sub)} mercados ({cob:.1%} de cobertura)")
        if len(sub) < 100:
            log("      poucos mercados neste lead; pulando")
            continue
        sub.sort(key=lambda m: m["ts_fim"])
        corte = int(len(sub) * args.frac_is)
        resultados[horas] = {
            "cobertura": cob,
            "tudo": analisar(sub, "tudo", args.limiar, args.spread, args.reps),
            "in_sample": analisar(sub[:corte], "in-sample", args.limiar, args.spread, args.reps),
            "out_of_sample": analisar(sub[corte:], "out-of-sample", args.limiar, args.spread, args.reps),
        }
        v = resultados[horas]["out_of_sample"]["vies_azarao"]
        log(f"      OOS azaroes n={v.get('n', 0)} vies={v.get('vies', float('nan')):+.4f} "
            f"p={v.get('p_valor', 1):.4f}")

        oos = sub[corte:]
        p = np.array([m["preco"] for m in oos], dtype=float)
        y = np.array([m["desfecho_sim"] for m in oos], dtype=float)
        ts = np.array([m["ts_fim"] for m in oos], dtype=float)
        linhas = []
        for sp in (0.0, 0.005, 0.01, 0.02):
            tr = backtest_vender_azarao(p, y, ts, limiar=args.limiar, spread=sp)
            linhas.append({"spread": sp, **agregar(tr, [semana(t["ts"]) for t in tr])})
        sens[horas] = linhas

    if not resultados:
        log("ERRO: nenhum lead com amostra suficiente.")
        return 1

    log("[4/5] Relatorio...")
    ctx = {"args": vars(args), "leads": leads, "descartes": descartes,
           "n": len(mercados),
           "periodo": [f"{datetime.fromtimestamp(fins[0], tz=timezone.utc):%Y-%m-%d}",
                       f"{datetime.fromtimestamp(fins[-1], tz=timezone.utc):%Y-%m-%d}"],
           "segundos": round(time.time() - t0, 1)}
    escrever(ctx, resultados, sens)
    with open(os.path.join(SAIDA, "resultado.json"), "w") as f:
        json.dump({"contexto": ctx, "resultados": resultados, "sensibilidade": sens},
                  f, indent=2, default=float)
    log(f"[5/5] resultados/relatorio.md ({ctx['segundos']}s)")
    return 0


def _veredito(v):
    if v.get("n", 0) == 0:
        return "Sem amostra."
    if v["p_valor"] < 0.05 and v["vies"] > 0:
        return ("**Existe vies: azarao custa mais do que vale.** O preco medio fica "
                "acima da frequencia com que o evento acontece, e a diferenca e "
                "maior do que o acaso explicaria.")
    if v["p_valor"] < 0.05 and v["vies"] < 0:
        return ("**Existe vies, na direcao CONTRARIA a esperada:** azarao custa "
                "menos do que vale. Contraria a literatura e exigiria explicacao "
                "antes de qualquer aposta.")
    return ("**Sem evidencia de vies.** O desvio observado cabe dentro do que a "
            "sorte produziria num mercado calibrado.")


def escrever(ctx, resultados, sens):
    a = ctx["args"]
    principal = ctx["leads"][0]
    L = ["# Vies favorito-azarao em prediction markets — resultado\n"]
    L.append(f"Gerado em {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC · "
             f"{ctx['n']} mercados resolvidos · encerrados entre "
             f"{ctx['periodo'][0]} e {ctx['periodo'][1]} · {ctx['segundos']}s\n")

    suspeito = max((resultados[h]["tudo"].get("fracao_no_inicial", 0.0)
                    for h in resultados), default=0.0)
    L.append("## Leitura rapida\n")
    if suspeito > 0.25:
        L.append(f"> **AVISO: {suspeito:.0%} dos precos estao a menos de 2 centavos "
                 "de 0,50.** Isso costuma significar que o preco lido e o valor "
                 "inicial da plataforma, de mercados que ainda nao tinham "
                 "negociado -- e nao opiniao de mercado. Qualquer numero abaixo "
                 "deve ser tratado como artefato ate essa concentracao cair.\n")
    if principal in resultados:
        r = resultados[principal]
        v = r["out_of_sample"]["vies"]
        L.append(f"Lead principal: **{principal}h antes do fim** "
                 f"(cobertura {r['cobertura']:.1%} dos mercados).\n")
        L.append(_veredito(v) + "\n")
        if v.get("n", 0):
            L.append(f"- Entre as apostas precificadas até {a['limiar']:.0%}: preço médio "
                     f"**{v['preco_medio']:.3f}**, aconteceu de fato "
                     f"**{v['freq_real']:.3f}** das vezes.\n")
            L.append(f"- Vies (preco − frequencia real): **{v['vies']:+.4f}** em "
                     f"{v['n']} apostas de azarao, p = {v['p_valor']:.4f}\n")
            L.append(f"- Faixa que a nula produziria: "
                     f"[{v['nula_ic'][0]:+.4f}, {v['nula_ic'][1]:+.4f}]\n")
        b = r["out_of_sample"]["backtest"]
        if b.get("n", 0):
            L.append(f"- Vender azarao (preco ≤ {a['limiar']:.2f}, spread "
                     f"{a['spread']:.3f}): {b['n']} apostas, **{b['exp_r']:+.4f}R**, "
                     f"IC 95% [{b['ic_r'][0]:+.3f}, {b['ic_r'][1]:+.3f}]\n")

    L.append("\n## Como ler\n")
    L.append("- **Vies** = preco medio menos frequencia real, medido SO entre as "
             "apostas baratas. Positivo significa azarao caro demais.\n")
    L.append("- Cada mercado entra com os **dois lados**: se o SIM custa 0,85, o "
             "NAO custa 0,15 e é o azarao daquele mercado. Olhar so o lado SIM "
             "esvaziaria as faixas baratas.\n")
    L.append("- Por isso o vies AGREGADO nao aparece: somando os dois lados ele e "
             "zero por construcao. Vies favorito-azarao sempre foi uma afirmacao "
             "sobre as pontas, nunca sobre a media geral.\n")
    L.append("- A **nula** nao e zero: e o que a sorte produziria se cada mercado "
             "fosse uma moeda honesta com a probabilidade que ele mesmo anuncia.\n")
    L.append("- **R** = valor arriscado. Vender SIM a p arrisca (1−p) para ganhar p.\n")
    L.append(f"- **Lead** = quanto antes do fim o preco foi lido. Cobertura medida: "
             f"6h em 100% dos mercados, 24h em ~50%. Por isso {principal}h e o "
             "principal: usar so 24h restringiria a amostra aos mercados de vida "
             "longa, que sao sistematicamente diferentes dos curtos.\n")
    L.append("- Contrapartida: quanto mais perto do fim, mais informado o preco, e "
             "mais **dificil** encontrar vies. Um achado em 6h seria forte; a "
             "ausencia dele pode ser em parte por isso.\n")

    for horas in ctx["leads"]:
        if horas not in resultados:
            continue
        r = resultados[horas]
        marca = " (principal)" if horas == principal else " (secundario)"
        L.append(f"\n---\n\n# Lead de {horas}h{marca}\n")
        L.append(f"Cobertura: {r['cobertura']:.1%} dos mercados coletados.\n")
        vo = r["out_of_sample"]["vies_azarao"]
        L.append(f"\n{_veredito(vo)}\n")

        L.append(f"\n| Recorte | Mercados | Azaroes (≤{a['limiar']:.0%}) | Vies no azarao | "
                 "p-valor | Backtest (n) | Expectancia | IC 95% |")
        L.append("|---|---|---|---|---|---|---|---|")
        for chave, nome in (("in_sample", "In-sample"), ("out_of_sample", "Out-of-sample")):
            d = r[chave]
            v, b = d["vies_azarao"], d["backtest"]
            if b.get("n", 0):
                bt = f"{b['n']} | {b['exp_r']:+.4f}R | [{b['ic_r'][0]:+.3f}, {b['ic_r'][1]:+.3f}]"
            else:
                bt = "0 | — | —"
            L.append(f"| {nome} | {d['n_mercados']} | {v.get('n', 0)} | "
                     f"{v.get('vies', float('nan')):+.4f} | "
                     f"{v.get('p_valor', 1):.4f} | {bt} |")
        L.append("")

        for chave, nome in (("in_sample", "In-sample"), ("out_of_sample", "Out-of-sample")):
            L.append(f"\n## Calibracao — {nome}, lead {horas}h\n")
            L.append("| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |")
            L.append("|---|---|---|---|---|---|")
            for b in r[chave]["calibracao"]:
                if b["n"] == 0:
                    L.append(f"| {b['lo']:.0%}–{b['hi']:.0%} | 0 | — | — | — | — |")
                    continue
                marca_ic = " **\\***" if b["fora_do_ic"] else ""
                L.append(f"| {b['lo']:.0%}–{b['hi']:.0%} | {b['n']} | {b['preco_medio']:.3f} | "
                         f"{b['freq_real']:.3f} | [{b['freq_ic'][0]:.3f}, {b['freq_ic'][1]:.3f}] | "
                         f"{b['diferenca']:+.3f}{marca_ic} |")
            L.append("")
            L.append("*\\* preco medio fora do IC da frequencia observada.*\n")

        L.append(f"\n## Sensibilidade ao custo — lead {horas}h (out-of-sample)\n")
        L.append("| Spread | Apostas | Expectancia | IC 95% |")
        L.append("|---|---|---|---|")
        for s in sens.get(horas, []):
            if not s.get("n"):
                L.append(f"| {s['spread']:.3f} | 0 | — | — |")
                continue
            L.append(f"| {s['spread']:.3f} | {s['n']} | {s['exp_r']:+.4f}R | "
                     f"[{s['ic_r'][0]:+.3f}, {s['ic_r'][1]:+.3f}] |")
        L.append("")
        L.append("Um vies pode ser real e mesmo assim nao ser operavel: num mercado "
                 "de 5 centavos, 1 centavo de spread leva um quinto do premio.\n")

    L.append("\n---\n\n## Descartes na coleta\n")
    L.append("| Motivo | Mercados |")
    L.append("|---|---|")
    for motivo, n in sorted(ctx["descartes"].items(), key=lambda kv: -kv[1]):
        L.append(f"| {motivo} | {n} |")
    L.append("")
    L.append("Se um motivo inesperado dominar, o problema e o leitor da API e nao o "
             "mercado. Os descartes por lead sao esperados: medem a cobertura.\n")

    L.append("\n## Parametros\n```")
    for k, val in a.items():
        L.append(f"{k} = {val}")
    L.append("```\n")
    with open(os.path.join(SAIDA, "relatorio.md"), "w") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
