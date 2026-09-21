"""
Nucleo estatistico. Herdado do stat-arb-lab (bootstrap de blocos e FDR), mais
o que este estudo precisa de proprio.
"""

import math
import numpy as np


# ---------------------------------------------------------------------------
# OLS
# ---------------------------------------------------------------------------

def ols(X, y):
    """
    Devolve (coef, resid, se, ssr). X ja deve incluir a coluna de constante se
    ela for desejada. Levanta np.linalg.LinAlgError se X for singular.
    """
    XtX = X.T @ X
    XtXi = np.linalg.inv(XtX)
    coef = XtXi @ (X.T @ y)
    resid = y - X @ coef
    n, k = X.shape
    dof = max(n - k, 1)
    ssr = float(resid @ resid)
    s2 = ssr / dof
    se = np.sqrt(np.maximum(np.diag(XtXi) * s2, 0.0))
    return coef, resid, se, ssr


# ---------------------------------------------------------------------------
# Multiplicidade de teste
# ---------------------------------------------------------------------------

def benjamini_hochberg(pvalores, q=0.10):
    """
    Controle de FDR. Devolve mascara booleana de quais hipoteses sao rejeitadas
    mantendo a taxa esperada de falsa descoberta em q.
    """
    p = np.asarray(pvalores, dtype=float)
    n = len(p)
    if n == 0:
        return np.zeros(0, dtype=bool)
    ordem = np.argsort(p)
    limiares = q * (np.arange(1, n + 1) / n)
    passou = p[ordem] <= limiares
    mask = np.zeros(n, dtype=bool)
    if passou.any():
        corte = np.max(np.nonzero(passou)[0])
        mask[ordem[:corte + 1]] = True
    return mask


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def bootstrap_blocos_ci(valores, blocos, reps=5000, alpha=0.05, seed=20260921):
    """
    IC bootstrap para a MEDIA, reamostrando BLOCOS inteiros em vez de
    observacoes soltas.

    Por que blocos: trades de pares diferentes abertos na mesma semana nao sao
    independentes -- quando o mercado inteiro se move junto, varios pares
    disparam junto e acertam ou erram junto. Reamostrar trade a trade trataria
    n trades correlacionados como n observacoes independentes e devolveria um
    IC artificialmente estreito. Aqui `blocos` e o rotulo de bloco (ex. semana
    de calendario da entrada) e a reamostragem sorteia blocos com reposicao.

    Devolve (media, lo, hi, n_blocos).
    """
    valores = np.asarray(valores, dtype=float)
    if len(valores) == 0:
        return float("nan"), float("nan"), float("nan"), 0
    blocos = np.asarray(blocos)
    rotulos = np.unique(blocos)
    grupos = [valores[blocos == r] for r in rotulos]
    nb = len(grupos)
    rng = np.random.default_rng(seed)
    medias = np.empty(reps)
    for i in range(reps):
        escolha = rng.integers(0, nb, nb)
        amostra = np.concatenate([grupos[j] for j in escolha])
        medias[i] = amostra.mean()
    lo = float(np.percentile(medias, 100 * alpha / 2))
    hi = float(np.percentile(medias, 100 * (1 - alpha / 2)))
    return float(valores.mean()), lo, hi, nb


# ---------------------------------------------------------------------------
# Calibracao de probabilidade
# ---------------------------------------------------------------------------

def wilson(k, n, z=1.96):
    """
    Intervalo de confianca de Wilson para uma proporcao.

    Usado em vez do intervalo normal simples porque aqui as proporcoes vivem
    perto de 0 e de 1 -- exatamente onde o intervalo normal produz limites
    absurdos (negativos, ou acima de 1) e cobertura errada. Azarao com 2% de
    preco e o caso central deste estudo, entao a escolha importa.
    """
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    meio = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, centro - meio), min(1.0, centro + meio)


def nula_calibrada(precos, reps=5000, seed=20260921):
    """
    Distribuicao da estatistica de vies SOB A HIPOTESE NULA de que o mercado
    esta perfeitamente calibrado.

    Simula o desfecho de cada mercado como uma moeda viciada com a
    probabilidade que o PROPRIO preco afirma, e recalcula o vies. Repetindo,
    monta a distribuicao do vies que a pura sorte produziria num mercado
    honesto, com exatamente estes precos e este tamanho de amostra.

    Isso responde a unica pergunta que importa: o desvio observado e maior do
    que o acaso explicaria? Sem essa nula, qualquer ruido amostral em bucket
    pequeno viraria "descoberta de vies".

    Devolve array de vies medio simulado (preco - desfecho).
    """
    p = np.asarray(precos, dtype=float)
    rng = np.random.default_rng(seed)
    out = np.empty(reps)
    for i in range(reps):
        y = (rng.random(len(p)) < p).astype(float)
        out[i] = float(np.mean(p - y))
    out.sort()
    return out


def pvalor_bilateral(observado, nulos):
    """Fracao da nula pelo menos tao extrema quanto o observado, dos dois lados."""
    nulos = np.asarray(nulos)
    if len(nulos) == 0 or not np.isfinite(observado):
        return 1.0
    centro = float(np.mean(nulos))
    extremos = int(np.sum(np.abs(nulos - centro) >= abs(observado - centro)))
    return (extremos + 1) / (len(nulos) + 1)
