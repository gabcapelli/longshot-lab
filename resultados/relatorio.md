# Vies favorito-azarao em prediction markets — resultado

Gerado em 2026-09-21 14:37 UTC · 889 mercados resolvidos · encerrados entre 2026-08-22 e 2026-09-14 · 3708.1s

## Leitura rapida

Lead principal: **6h antes do fim** (cobertura 100.0% dos mercados).

**Existe vies, na direcao CONTRARIA a esperada:** azarao custa menos do que vale. Contraria a literatura e exigiria explicacao antes de qualquer aposta.

- Vies medio (preco − desfecho), out-of-sample: **-0.0577** em 356 mercados, p = 0.0250

- Faixa que a nula produziria: [-0.0521, +0.0490]

- Vender azarao (preco ≤ 0.10, spread 0.010): 10 apostas, **-0.1593R**, IC 95% [-0.279, +0.012]


## Como ler

- **Vies** = preco medio menos frequencia real. Positivo significa que o mercado cobra mais do que o evento vale.

- A **nula** nao e zero: e o que a sorte produziria se cada mercado fosse uma moeda honesta com a probabilidade que ele mesmo anuncia.

- **R** = valor arriscado. Vender SIM a p arrisca (1−p) para ganhar p.

- **Lead** = quanto antes do fim o preco foi lido. Cobertura medida: 6h em 100% dos mercados, 24h em ~50%. Por isso 6h e o principal: usar so 24h restringiria a amostra aos mercados de vida longa, que sao sistematicamente diferentes dos curtos.

- Contrapartida: quanto mais perto do fim, mais informado o preco, e mais **dificil** encontrar vies. Um achado em 6h seria forte; a ausencia dele pode ser em parte por isso.


---

# Lead de 6h (principal)

Cobertura: 100.0% dos mercados coletados.


**Existe vies, na direcao CONTRARIA a esperada:** azarao custa menos do que vale. Contraria a literatura e exigiria explicacao antes de qualquer aposta.


| Recorte | Mercados | Vies | p-valor | Backtest (n) | Expectancia | IC 95% |
|---|---|---|---|---|---|---|
| In-sample | 533 | +0.0232 | 0.2629 | 13 | -0.1263R | [-0.329, +0.045] |
| Out-of-sample | 356 | -0.0577 | 0.0250 | 10 | -0.1593R | [-0.279, +0.012] |


## Calibracao — In-sample, lead 6h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 7 | 0.010 | 0.000 | [0.000, 0.354] | +0.010 |
| 2%–5% | 2 | 0.027 | 0.000 | [0.000, 0.658] | +0.027 |
| 5%–10% | 6 | 0.076 | 0.333 | [0.097, 0.700] | -0.257 **\*** |
| 10%–20% | 17 | 0.141 | 0.176 | [0.062, 0.410] | -0.035 |
| 20%–35% | 37 | 0.262 | 0.324 | [0.196, 0.485] | -0.062 |
| 35%–50% | 57 | 0.426 | 0.368 | [0.255, 0.498] | +0.058 |
| 50%–65% | 361 | 0.511 | 0.468 | [0.417, 0.520] | +0.043 |
| 65%–80% | 26 | 0.714 | 0.846 | [0.665, 0.939] | -0.132 |
| 80%–90% | 14 | 0.838 | 0.786 | [0.524, 0.924] | +0.053 |
| 90%–95% | 2 | 0.923 | 1.000 | [0.342, 1.000] | -0.077 |
| 95%–98% | 4 | 0.956 | 0.750 | [0.301, 0.954] | +0.206 **\*** |
| 98%–100% | 0 | — | — | — | — |

*\* preco medio fora do IC da frequencia observada.*


## Calibracao — Out-of-sample, lead 6h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 1 | 0.017 | 0.000 | [0.000, 0.793] | +0.017 |
| 2%–5% | 3 | 0.030 | 0.000 | [0.000, 0.562] | +0.030 |
| 5%–10% | 6 | 0.083 | 0.333 | [0.097, 0.700] | -0.251 **\*** |
| 10%–20% | 14 | 0.156 | 0.357 | [0.163, 0.612] | -0.201 **\*** |
| 20%–35% | 30 | 0.290 | 0.400 | [0.246, 0.577] | -0.110 |
| 35%–50% | 37 | 0.440 | 0.541 | [0.384, 0.690] | -0.101 |
| 50%–65% | 233 | 0.516 | 0.549 | [0.485, 0.612] | -0.033 |
| 65%–80% | 20 | 0.707 | 0.800 | [0.584, 0.919] | -0.093 |
| 80%–90% | 9 | 0.842 | 0.889 | [0.565, 0.980] | -0.047 |
| 90%–95% | 2 | 0.905 | 0.500 | [0.095, 0.905] | +0.405 |
| 95%–98% | 1 | 0.976 | 1.000 | [0.207, 1.000] | -0.024 |
| 98%–100% | 0 | — | — | — | — |

*\* preco medio fora do IC da frequencia observada.*


## Sensibilidade ao custo — lead 6h (out-of-sample)

| Spread | Apostas | Expectancia | IC 95% |
|---|---|---|---|
| 0.000 | 10 | -0.1548R | [-0.275, +0.017] |
| 0.005 | 10 | -0.1571R | [-0.277, +0.014] |
| 0.010 | 10 | -0.1593R | [-0.279, +0.012] |
| 0.020 | 10 | -0.1637R | [-0.283, +0.007] |

Um vies pode ser real e mesmo assim nao ser operavel: num mercado de 5 centavos, 1 centavo de spread leva um quinto do premio.


---

# Lead de 24h (secundario)

Cobertura: 34.2% dos mercados coletados.


**Existe vies, na direcao CONTRARIA a esperada:** azarao custa menos do que vale. Contraria a literatura e exigiria explicacao antes de qualquer aposta.


| Recorte | Mercados | Vies | p-valor | Backtest (n) | Expectancia | IC 95% |
|---|---|---|---|---|---|---|
| In-sample | 182 | -0.0192 | 0.5545 | 14 | -0.1790R | [-0.326, -0.115] |
| Out-of-sample | 122 | -0.1098 | 0.0070 | 9 | -0.0704R | [-0.126, +0.053] |


## Calibracao — In-sample, lead 24h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 2 | 0.010 | 0.000 | [0.000, 0.658] | +0.010 |
| 2%–5% | 3 | 0.024 | 0.000 | [0.000, 0.562] | +0.024 |
| 5%–10% | 7 | 0.073 | 0.286 | [0.082, 0.641] | -0.213 **\*** |
| 10%–20% | 22 | 0.147 | 0.227 | [0.101, 0.434] | -0.080 |
| 20%–35% | 31 | 0.266 | 0.323 | [0.186, 0.499] | -0.057 |
| 35%–50% | 34 | 0.430 | 0.441 | [0.289, 0.605] | -0.011 |
| 50%–65% | 45 | 0.556 | 0.489 | [0.350, 0.630] | +0.067 |
| 65%–80% | 21 | 0.710 | 0.857 | [0.654, 0.950] | -0.147 |
| 80%–90% | 12 | 0.843 | 0.750 | [0.468, 0.911] | +0.093 |
| 90%–95% | 1 | 0.930 | 1.000 | [0.207, 1.000] | -0.070 |
| 95%–98% | 4 | 0.955 | 0.750 | [0.301, 0.954] | +0.205 **\*** |
| 98%–100% | 0 | — | — | — | — |

*\* preco medio fora do IC da frequencia observada.*


## Calibracao — Out-of-sample, lead 24h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 0 | — | — | — | — |
| 2%–5% | 4 | 0.028 | 0.000 | [0.000, 0.490] | +0.028 |
| 5%–10% | 4 | 0.064 | 0.250 | [0.046, 0.699] | -0.186 |
| 10%–20% | 14 | 0.150 | 0.357 | [0.163, 0.612] | -0.207 **\*** |
| 20%–35% | 24 | 0.290 | 0.417 | [0.245, 0.612] | -0.126 |
| 35%–50% | 23 | 0.438 | 0.478 | [0.292, 0.670] | -0.040 |
| 50%–65% | 33 | 0.548 | 0.606 | [0.437, 0.753] | -0.058 |
| 65%–80% | 15 | 0.708 | 0.933 | [0.702, 0.988] | -0.225 |
| 80%–90% | 3 | 0.842 | 1.000 | [0.438, 1.000] | -0.158 |
| 90%–95% | 1 | 0.900 | 1.000 | [0.207, 1.000] | -0.100 |
| 95%–98% | 1 | 0.975 | 1.000 | [0.207, 1.000] | -0.025 |
| 98%–100% | 0 | — | — | — | — |

*\* preco medio fora do IC da frequencia observada.*


## Sensibilidade ao custo — lead 24h (out-of-sample)

| Spread | Apostas | Expectancia | IC 95% |
|---|---|---|---|
| 0.000 | 9 | -0.0655R | [-0.122, +0.058] |
| 0.005 | 9 | -0.0679R | [-0.124, +0.055] |
| 0.010 | 9 | -0.0704R | [-0.126, +0.053] |
| 0.020 | 9 | -0.0752R | [-0.131, +0.047] |

Um vies pode ser real e mesmo assim nao ser operavel: num mercado de 5 centavos, 1 centavo de spread leva um quinto do premio.


---

## Descartes na coleta

| Motivo | Mercados |
|---|---|
| sem preco em nenhum lead | 628 |
| sem preco no lead de 24h | 585 |
| sem desfecho definido | 3 |

Se um motivo inesperado dominar, o problema e o leitor da API e nao o mercado. Os descartes por lead sao esperados: medem a cobertura.


## Parametros
```
alvo = 4000
dias_max = 180
dias_min_fechado = 7
por_dia = 40
volume_min = 10000.0
leads = 6,24
limiar = 0.1
spread = 0.01
frac_is = 0.6
reps = 5000
sem_cache = False
```
