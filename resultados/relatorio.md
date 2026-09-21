# Vies favorito-azarao em prediction markets — resultado

Gerado em 2026-09-21 16:08 UTC · 2027 mercados resolvidos · encerrados entre 2026-08-22 e 2026-09-16 · 1092.1s

## Leitura rapida

*Verificacao de alinhamento: o preco final do token lido converge para o desfecho registrado em 97.3% dos mercados.*

Lead principal: **6h antes do fim** (cobertura 100.0% dos mercados).

**Existe vies, na direcao CONTRARIA a esperada:** azarao custa menos do que vale. Contraria a literatura e exigiria explicacao antes de qualquer aposta.

- Entre as apostas precificadas até 10%: preço médio **0.028**, aconteceu de fato **0.061** das vezes.

- Vies (preco − frequencia real): **-0.0333** em 196 apostas de azarao, p = 0.0068

- Faixa que a nula produziria: [-0.0231, +0.0178]

- Vender azarao (preco ≤ 0.10, spread 0.010): 105 apostas, **-0.0722R**, IC 95% [-0.110, +0.035]


## Como ler

- **Vies** = preco medio menos frequencia real, medido SO entre as apostas baratas. Positivo significa azarao caro demais.

- Cada mercado entra com os **dois lados**: se o SIM custa 0,85, o NAO custa 0,15 e é o azarao daquele mercado. Olhar so o lado SIM esvaziaria as faixas baratas.

- Por isso o vies AGREGADO nao aparece: somando os dois lados ele e zero por construcao. Vies favorito-azarao sempre foi uma afirmacao sobre as pontas, nunca sobre a media geral.

- A **nula** nao e zero: e o que a sorte produziria se cada mercado fosse uma moeda honesta com a probabilidade que ele mesmo anuncia.

- **R** = valor arriscado. Vender SIM a p arrisca (1−p) para ganhar p.

- **Lead** = quanto antes do fim o preco foi lido. Cobertura medida: 6h em 100% dos mercados, 24h em ~50%. Por isso 6h e o principal: usar so 24h restringiria a amostra aos mercados de vida longa, que sao sistematicamente diferentes dos curtos.

- Contrapartida: quanto mais perto do fim, mais informado o preco, e mais **dificil** encontrar vies. Um achado em 6h seria forte; a ausencia dele pode ser em parte por isso.


---

# Lead de 6h (principal)

Cobertura: 100.0% dos mercados coletados.


**Existe vies, na direcao CONTRARIA a esperada:** azarao custa menos do que vale. Contraria a literatura e exigiria explicacao antes de qualquer aposta.


| Recorte | Mercados | Azaroes (≤10%) | Vies no azarao | p-valor | Backtest (n) | Expectancia | IC 95% |
|---|---|---|---|---|---|---|---|
| In-sample | 1216 | 143 | -0.0470 | 0.0034 | 94 | -0.0821R | [-0.115, -0.034] |
| Out-of-sample | 811 | 196 | -0.0333 | 0.0068 | 105 | -0.0722R | [-0.110, +0.035] |


## Calibracao — In-sample, lead 6h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 60 | 0.003 | 0.000 | [0.000, 0.060] | +0.003 |
| 2%–5% | 29 | 0.034 | 0.069 | [0.019, 0.220] | -0.035 |
| 5%–10% | 54 | 0.076 | 0.185 | [0.104, 0.308] | -0.109 **\*** |
| 10%–20% | 126 | 0.156 | 0.135 | [0.086, 0.205] | +0.022 |
| 20%–35% | 341 | 0.279 | 0.311 | [0.264, 0.362] | -0.032 |
| 35%–50% | 582 | 0.430 | 0.424 | [0.385, 0.465] | +0.006 |
| 50%–65% | 621 | 0.563 | 0.570 | [0.531, 0.608] | -0.007 |
| 65%–80% | 348 | 0.719 | 0.687 | [0.636, 0.733] | +0.032 |
| 80%–90% | 128 | 0.843 | 0.859 | [0.789, 0.909] | -0.017 |
| 90%–95% | 54 | 0.924 | 0.815 | [0.692, 0.896] | +0.109 **\*** |
| 95%–98% | 28 | 0.965 | 0.929 | [0.774, 0.980] | +0.037 |
| 98%–100% | 61 | 0.997 | 1.000 | [0.941, 1.000] | -0.003 |

*\* preco medio fora do IC da frequencia observada.*


## Calibracao — Out-of-sample, lead 6h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 113 | 0.003 | 0.000 | [0.000, 0.033] | +0.003 |
| 2%–5% | 26 | 0.037 | 0.077 | [0.021, 0.241] | -0.040 |
| 5%–10% | 55 | 0.072 | 0.182 | [0.102, 0.303] | -0.110 **\*** |
| 10%–20% | 89 | 0.154 | 0.303 | [0.218, 0.405] | -0.150 **\*** |
| 20%–35% | 172 | 0.278 | 0.326 | [0.260, 0.399] | -0.047 |
| 35%–50% | 345 | 0.430 | 0.429 | [0.378, 0.482] | +0.001 |
| 50%–65% | 366 | 0.565 | 0.566 | [0.514, 0.615] | -0.000 |
| 65%–80% | 173 | 0.721 | 0.676 | [0.603, 0.742] | +0.045 |
| 80%–90% | 87 | 0.845 | 0.690 | [0.586, 0.777] | +0.156 **\*** |
| 90%–95% | 55 | 0.926 | 0.836 | [0.717, 0.911] | +0.090 **\*** |
| 95%–98% | 28 | 0.962 | 0.893 | [0.728, 0.963] | +0.069 |
| 98%–100% | 113 | 0.997 | 1.000 | [0.967, 1.000] | -0.003 |

*\* preco medio fora do IC da frequencia observada.*


## Sensibilidade ao custo — lead 6h (out-of-sample)

| Spread | Apostas | Expectancia | IC 95% |
|---|---|---|---|
| 0.000 | 129 | -0.0106R | [-0.023, +0.019] |
| 0.005 | 73 | -0.0218R | [-0.054, +0.016] |
| 0.010 | 69 | -0.0257R | [-0.061, +0.013] |
| 0.020 | 66 | -0.0321R | [-0.068, +0.012] |

Um vies pode ser real e mesmo assim nao ser operavel: num mercado de 5 centavos, 1 centavo de spread leva um quinto do premio.


---

# Lead de 24h (secundario)

Cobertura: 77.2% dos mercados coletados.


**Existe vies, na direcao CONTRARIA a esperada:** azarao custa menos do que vale. Contraria a literatura e exigiria explicacao antes de qualquer aposta.


| Recorte | Mercados | Azaroes (≤10%) | Vies no azarao | p-valor | Backtest (n) | Expectancia | IC 95% |
|---|---|---|---|---|---|---|---|
| In-sample | 938 | 93 | -0.0798 | 0.0030 | 89 | -0.0824R | [-0.094, -0.068] |
| Out-of-sample | 626 | 106 | -0.0519 | 0.0288 | 101 | -0.0633R | [-0.092, +0.063] |


## Calibracao — In-sample, lead 24h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 20 | 0.010 | 0.050 | [0.009, 0.236] | -0.040 |
| 2%–5% | 28 | 0.033 | 0.071 | [0.020, 0.226] | -0.038 |
| 5%–10% | 40 | 0.074 | 0.225 | [0.123, 0.375] | -0.151 **\*** |
| 10%–20% | 121 | 0.150 | 0.149 | [0.096, 0.223] | +0.002 |
| 20%–35% | 281 | 0.281 | 0.310 | [0.258, 0.366] | -0.028 |
| 35%–50% | 436 | 0.427 | 0.401 | [0.356, 0.448] | +0.026 |
| 50%–65% | 454 | 0.568 | 0.590 | [0.544, 0.635] | -0.022 |
| 65%–80% | 284 | 0.716 | 0.690 | [0.634, 0.741] | +0.026 |
| 80%–90% | 119 | 0.846 | 0.849 | [0.774, 0.902] | -0.002 |
| 90%–95% | 45 | 0.923 | 0.800 | [0.662, 0.891] | +0.123 **\*** |
| 95%–98% | 28 | 0.967 | 0.929 | [0.774, 0.980] | +0.038 |
| 98%–100% | 20 | 0.990 | 0.950 | [0.764, 0.991] | +0.040 |

*\* preco medio fora do IC da frequencia observada.*


## Calibracao — Out-of-sample, lead 24h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 17 | 0.011 | 0.000 | [0.000, 0.184] | +0.011 |
| 2%–5% | 32 | 0.037 | 0.094 | [0.032, 0.242] | -0.056 |
| 5%–10% | 56 | 0.072 | 0.125 | [0.062, 0.236] | -0.053 |
| 10%–20% | 70 | 0.150 | 0.329 | [0.230, 0.445] | -0.179 **\*** |
| 20%–35% | 175 | 0.279 | 0.343 | [0.277, 0.416] | -0.064 |
| 35%–50% | 269 | 0.430 | 0.428 | [0.370, 0.487] | +0.002 |
| 50%–65% | 279 | 0.566 | 0.566 | [0.508, 0.623] | -0.001 |
| 65%–80% | 179 | 0.719 | 0.659 | [0.587, 0.725] | +0.060 |
| 80%–90% | 69 | 0.849 | 0.681 | [0.564, 0.779] | +0.168 **\*** |
| 90%–95% | 56 | 0.927 | 0.875 | [0.764, 0.938] | +0.052 |
| 95%–98% | 33 | 0.962 | 0.879 | [0.727, 0.952] | +0.083 **\*** |
| 98%–100% | 17 | 0.989 | 1.000 | [0.816, 1.000] | -0.011 |

*\* preco medio fora do IC da frequencia observada.*


## Sensibilidade ao custo — lead 24h (out-of-sample)

| Spread | Apostas | Expectancia | IC 95% |
|---|---|---|---|
| 0.000 | 83 | -0.0227R | [-0.042, +0.036] |
| 0.005 | 81 | -0.0258R | [-0.045, +0.051] |
| 0.010 | 79 | -0.0291R | [-0.050, +0.048] |
| 0.020 | 75 | -0.0358R | [-0.059, +0.042] |

Um vies pode ser real e mesmo assim nao ser operavel: num mercado de 5 centavos, 1 centavo de spread leva um quinto do premio.


---

## Sensibilidade a defasagem do preco

| Defasagem maxima | Mercados | Azaroes | Vies | p-valor |
|---|---|---|---|---|
| ≤ 0.5h | 389 | 105 | -0.0407 | 0.0074 |
| ≤ 1h | 806 | 196 | -0.0333 | 0.0068 |
| ≤ 2h | 811 | 196 | -0.0333 | 0.0068 |
| ≤ 6h | 811 | 196 | -0.0333 | 0.0068 |
| ≤ 12h | 811 | 196 | -0.0333 | 0.0068 |
| ≤ 24h | 811 | 196 | -0.0333 | 0.0068 |
| ≤ 48h | 811 | 196 | -0.0333 | 0.0068 |

**Esta e a tabela que decide se o achado e real.** O preco lido e o do ultimo negocio ANTES do instante medido. Se esse negocio aconteceu horas antes, o preco esta velho -- e um azarao que negociou a 0,05, subiu e ganhou entraria como 'custava 0,05 e aconteceu', fabricando sozinho a aparencia de azarao barato.

Se o vies encolher em direcao a zero conforme a tolerancia aperta, ele vinha de preco velho. Se ficar estavel, e do mercado.


---

## Descartes na coleta

| Motivo | Mercados |
|---|---|
| sem preco em nenhum lead | 1433 |
| sem preco no lead de 24h | 463 |
| sem desfecho definido | 40 |

Se um motivo inesperado dominar, o problema e o leitor da API e nao o mercado. Os descartes por lead sao esperados: medem a cobertura.


## Parametros
```
alvo = 3500
dias_max = 45
dias_min_fechado = 7
por_dia = 150
volume_min = 10000.0
leads = 6,24
limiar = 0.1
spread = 0.01
frac_is = 0.6
reps = 5000
max_defasagem = 6.0
sem_cache = False
```
