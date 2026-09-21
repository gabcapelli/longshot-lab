"""
Calibracao e backtest da regra de vender azarao.

CONTABILIDADE (vale conferir, porque quase todo erro deste estudo moraria aqui)

Vender SIM a um preco p significa ficar do lado NAO. Voce deposita (1-p) de
garantia, o outro lado deposita p. Se NAO acontece voce leva 1, tendo
arriscado (1-p): lucro = p. Se SIM acontece voce perde a garantia: lucro
= -(1-p).

Entao o lucro por unidade e sempre  p - y,  com y em {0,1}.
E o risco e sempre (1-p), que vira a unidade de R:

    R-multiplo = (p - y) / (1 - p)

Com p = 0,05: ganha 0,053R quando da NAO (frequente) e perde 1R quando da SIM
(raro). Se o mercado estiver calibrado, isso soma exatamente zero -- e por
isso que qualquer resultado diferente de zero e a medida do vies, ja em
unidade comparavel com os outros projetos.

BUCKETS PRE-REGISTRADOS. As faixas de preco estao fixas no codigo antes de
ver o dado. Escolher fronteira de bucket depois de olhar o resultado e o jeito
mais facil de fabricar um vies que nao existe.
"""

import numpy as np

from lab.stats import bootstrap_blocos_ci, nula_calibrada, pvalor_bilateral, wilson

# Fixos antes de ver o dado. Mais finos nas pontas, que e onde o vies
# favorito-azarao deveria aparecer, e onde o preco tem mais resolucao.
BUCKETS = [(0.00, 0.02), (0.02, 0.05), (0.05, 0.10), (0.10, 0.20),
           (0.20, 0.35), (0.35, 0.50), (0.50, 0.65), (0.65, 0.80),
           (0.80, 0.90), (0.90, 0.95), (0.95, 0.98), (0.98, 1.00)]


def observacoes(precos_sim, desfechos_sim, ts):
    """
    Cada mercado binario vira DUAS observacoes: o lado SIM a p, e o lado NAO a
    (1-p). Se o SIM custa 0,85, o NAO custa 0,15 -- e um azarao.

    Por que isso e obrigatorio: olhando so o lado SIM, as faixas baratas ficam
    quase vazias. Na primeira rodada sobre dado real o backtest teve DEZ
    apostas, porque quase nenhum token SIM de mercado esportivo esta abaixo de
    10 centavos -- o azarao daquele mercado e o outro lado, que eu estava
    jogando fora.

    Atencao ao usar: a media de (preco - desfecho) sobre os dois lados e ZERO
    por construcao, ja que (p - y) + ((1-p) - (1-y)) = 0. O vies agregado
    perde sentido aqui; o que se mede e o vies DENTRO das faixas de preco
    (ver teste_vies_azarao). Isso nao e perda: vies favorito-azarao sempre foi
    uma afirmacao sobre as pontas, nunca sobre a media geral.
    """
    p = np.asarray(precos_sim, dtype=float)
    y = np.asarray(desfechos_sim, dtype=float)
    t = np.asarray(ts, dtype=float)
    precos = np.concatenate([p, 1.0 - p])
    desfechos = np.concatenate([y, 1.0 - y])
    tempos = np.concatenate([t, t])
    # id do mercado, para o bootstrap saber que os dois lados sao o mesmo evento
    ids = np.concatenate([np.arange(len(p)), np.arange(len(p))])
    return precos, desfechos, tempos, ids


def teste_vies_azarao(p, y, limiar=0.10, reps=5000):
    """
    O teste de verdade: entre as observacoes precificadas ABAIXO do limiar, a
    frequencia real fica abaixo do preco?

    Restringir ao azarao e o que torna a pergunta a do vies favorito-azarao,
    em vez de uma afirmacao sobre o mercado inteiro.
    """
    p = np.asarray(p, dtype=float)
    y = np.asarray(y, dtype=float)
    m = (p > 0) & (p <= limiar)
    if m.sum() == 0:
        return {"n": 0, "limiar": limiar}
    r = teste_vies(p[m], y[m], reps=reps)
    r["limiar"] = limiar
    r["preco_medio"] = float(p[m].mean())
    r["freq_real"] = float(y[m].mean())
    return r


def tabela_calibracao(p, y):
    """
    Para cada faixa de preco: quantos mercados, preco medio, frequencia real
    com que o evento aconteceu, e a diferenca.

    Se o mercado for honesto, frequencia real ~ preco medio em toda faixa.
    Vies favorito-azarao seria: frequencia real ABAIXO do preco nas faixas
    baratas (azarao custa mais do que vale).
    """
    linhas = []
    for lo, hi in BUCKETS:
        m = (p >= lo) & (p < hi) if hi < 1.0 else (p >= lo) & (p <= hi)
        n = int(m.sum())
        if n == 0:
            linhas.append({"lo": lo, "hi": hi, "n": 0})
            continue
        k = int(y[m].sum())
        freq, f_lo, f_hi = wilson(k, n)
        preco_medio = float(p[m].mean())
        linhas.append({
            "lo": lo, "hi": hi, "n": n, "k": k,
            "preco_medio": preco_medio, "freq_real": freq,
            "freq_ic": [f_lo, f_hi],
            "diferenca": preco_medio - freq,
            # o preco esta fora do IC da frequencia observada?
            "fora_do_ic": not (f_lo <= preco_medio <= f_hi),
        })
    return linhas


def teste_vies(p, y, reps=5000):
    """
    Vies medio (preco - desfecho) contra a nula de mercado calibrado.

    A nula nao e "zero": e a distribuicao que o proprio conjunto de precos
    produziria se cada mercado fosse uma moeda honesta com a probabilidade que
    ele mesmo anuncia. Isso incorpora o tamanho da amostra e o formato da
    distribuicao de precos sem precisar supor nada.
    """
    if len(p) == 0:
        return {"n": 0}
    obs = float(np.mean(p - y))
    nulos = nula_calibrada(p, reps=reps)
    return {
        "n": len(p), "vies": obs,
        "nula_media": float(np.mean(nulos)),
        "nula_ic": [float(np.percentile(nulos, 2.5)), float(np.percentile(nulos, 97.5))],
        "p_valor": pvalor_bilateral(obs, nulos),
    }


def backtest_vender_azarao(p, y, ts, limiar=0.10, spread=0.01, taxa=0.0):
    """
    Regra: vender SIM em todo mercado cujo preco esteja em (0, limiar].

    `spread` e o custo de execucao em unidades de preco: quem vende leva a
    ponta de compra, abaixo do meio. Isso NAO e detalhe -- num mercado de 5
    centavos, 1 centavo de spread come um quinto do premio. Um vies real pode
    existir e ainda assim nao ser operavel, e o estudo precisa saber separar
    as duas coisas.
    """
    trades = []
    for pi, yi, ti in zip(p, y, ts):
        if not (0 < pi <= limiar):
            continue
        p_exec = pi - spread / 2.0     # vende na ponta de compra
        if p_exec <= 0:
            continue                    # spread engoliu o mercado inteiro
        risco = 1.0 - p_exec
        lucro = p_exec - yi - taxa * (1.0 - yi) * 1.0
        trades.append({
            "ts": int(ti), "preco": float(pi), "preco_exec": float(p_exec),
            "desfecho": int(yi), "lucro": float(lucro),
            "r_multiplo": float(lucro / risco) if risco > 1e-9 else float("nan"),
        })
    return trades


def agregar(trades, blocos, reps=5000):
    if not trades:
        return {"n": 0}
    r = np.array([t["r_multiplo"] for t in trades], dtype=float)
    lucro = np.array([t["lucro"] for t in trades], dtype=float)
    ok = np.isfinite(r)
    r, lucro, blocos = r[ok], lucro[ok], np.asarray(blocos)[ok]
    m_r, lo_r, hi_r, nb = bootstrap_blocos_ci(r, blocos, reps=reps)
    m_l, lo_l, hi_l, _ = bootstrap_blocos_ci(lucro, blocos, reps=reps)
    return {
        "n": int(len(r)), "n_blocos": nb,
        "exp_r": m_r, "ic_r": [lo_r, hi_r],
        "lucro_medio": m_l, "ic_lucro": [lo_l, hi_l],
        "taxa_acerto": float((r > 0).mean()),
    }
