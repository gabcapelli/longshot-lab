# Vies favorito-azarao em prediction markets — resultado

Gerado em 2026-09-21 15:40 UTC · 2117 mercados resolvidos · encerrados entre 2026-08-22 e 2026-09-16 · 974.5s

## Leitura rapida

Lead principal: **6h antes do fim** (cobertura 100.0% dos mercados).

**Existe vies, na direcao CONTRARIA a esperada:** azarao custa menos do que vale. Contraria a literatura e exigiria explicacao antes de qualquer aposta.

- Entre as apostas precificadas até 10%: preço médio **0.018**, aconteceu de fato **0.044** das vezes.

- Vies (preco − frequencia real): **-0.0262** em 248 apostas de azarao, p = 0.0040

- Faixa que a nula produziria: [-0.0181, +0.0141]

- Vender azarao (preco ≤ 0.10, spread 0.010): 84 apostas, **-0.0894R**, IC 95% [-0.110, +0.035]


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
| In-sample | 1270 | 185 | -0.0409 | 0.0028 | 98 | -0.0876R | [-0.152, -0.012] |
| Out-of-sample | 847 | 248 | -0.0262 | 0.0040 | 84 | -0.0894R | [-0.110, +0.035] |


## Calibracao — In-sample, lead 6h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 102 | 0.002 | 0.000 | [0.000, 0.036] | +0.002 |
| 2%–5% | 23 | 0.033 | 0.174 | [0.070, 0.371] | -0.141 **\*** |
| 5%–10% | 60 | 0.074 | 0.150 | [0.081, 0.261] | -0.076 **\*** |
| 10%–20% | 135 | 0.157 | 0.148 | [0.098, 0.218] | +0.009 |
| 20%–35% | 344 | 0.280 | 0.299 | [0.253, 0.350] | -0.019 |
| 35%–50% | 581 | 0.432 | 0.439 | [0.399, 0.480] | -0.007 |
| 50%–65% | 623 | 0.561 | 0.559 | [0.519, 0.597] | +0.003 |
| 65%–80% | 350 | 0.718 | 0.694 | [0.644, 0.740] | +0.023 |
| 80%–90% | 137 | 0.842 | 0.847 | [0.777, 0.898] | -0.004 |
| 90%–95% | 58 | 0.925 | 0.845 | [0.731, 0.916] | +0.080 **\*** |
| 95%–98% | 24 | 0.965 | 0.833 | [0.641, 0.933] | +0.132 **\*** |
| 98%–100% | 103 | 0.998 | 1.000 | [0.964, 1.000] | -0.002 |

*\* preco medio fora do IC da frequencia observada.*


## Calibracao — Out-of-sample, lead 6h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 184 | 0.002 | 0.000 | [0.000, 0.020] | +0.002 |
| 2%–5% | 18 | 0.037 | 0.167 | [0.058, 0.392] | -0.130 **\*** |
| 5%–10% | 45 | 0.075 | 0.178 | [0.093, 0.313] | -0.103 **\*** |
| 10%–20% | 71 | 0.156 | 0.296 | [0.202, 0.410] | -0.140 **\*** |
| 20%–35% | 173 | 0.280 | 0.306 | [0.242, 0.379] | -0.027 |
| 35%–50% | 347 | 0.429 | 0.421 | [0.370, 0.473] | +0.008 |
| 50%–65% | 362 | 0.567 | 0.575 | [0.523, 0.624] | -0.008 |
| 65%–80% | 176 | 0.719 | 0.693 | [0.622, 0.757] | +0.026 |
| 80%–90% | 70 | 0.843 | 0.700 | [0.585, 0.795] | +0.143 **\*** |
| 90%–95% | 44 | 0.924 | 0.841 | [0.706, 0.921] | +0.083 **\*** |
| 95%–98% | 20 | 0.962 | 0.800 | [0.584, 0.919] | +0.162 **\*** |
| 98%–100% | 184 | 0.998 | 1.000 | [0.980, 1.000] | -0.002 |

*\* preco medio fora do IC da frequencia observada.*


## Sensibilidade ao custo — lead 6h (out-of-sample)

| Spread | Apostas | Expectancia | IC 95% |
|---|---|---|---|
| 0.000 | 162 | -0.0145R | [-0.017, +0.002] |
| 0.005 | 57 | -0.0447R | [-0.065, +0.009] |
| 0.010 | 49 | -0.0548R | [-0.089, +0.009] |
| 0.020 | 44 | -0.0661R | [-0.107, +0.012] |

Um vies pode ser real e mesmo assim nao ser operavel: num mercado de 5 centavos, 1 centavo de spread leva um quinto do premio.


---

# Lead de 24h (secundario)

Cobertura: 76.8% dos mercados coletados.


**Existe vies, na direcao CONTRARIA a esperada:** azarao custa menos do que vale. Contraria a literatura e exigiria explicacao antes de qualquer aposta.


| Recorte | Mercados | Azaroes (≤10%) | Vies no azarao | p-valor | Backtest (n) | Expectancia | IC 95% |
|---|---|---|---|---|---|---|---|
| In-sample | 975 | 83 | -0.1107 | 0.0002 | 76 | -0.1049R | [-0.155, -0.035] |
| Out-of-sample | 651 | 112 | -0.0487 | 0.0228 | 100 | -0.0633R | [-0.087, +0.052] |


## Calibracao — In-sample, lead 24h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 22 | 0.009 | 0.091 | [0.025, 0.278] | -0.082 **\*** |
| 2%–5% | 21 | 0.031 | 0.190 | [0.077, 0.400] | -0.159 **\*** |
| 5%–10% | 36 | 0.071 | 0.194 | [0.098, 0.350] | -0.123 **\*** |
| 10%–20% | 131 | 0.150 | 0.183 | [0.126, 0.258] | -0.033 |
| 20%–35% | 296 | 0.283 | 0.314 | [0.264, 0.369] | -0.031 |
| 35%–50% | 458 | 0.426 | 0.402 | [0.358, 0.447] | +0.024 |
| 50%–65% | 473 | 0.569 | 0.590 | [0.545, 0.633] | -0.020 |
| 65%–80% | 298 | 0.714 | 0.688 | [0.633, 0.738] | +0.026 |
| 80%–90% | 132 | 0.847 | 0.811 | [0.735, 0.868] | +0.036 |
| 90%–95% | 40 | 0.926 | 0.825 | [0.680, 0.913] | +0.101 **\*** |
| 95%–98% | 20 | 0.968 | 0.800 | [0.584, 0.919] | +0.168 **\*** |
| 98%–100% | 23 | 0.991 | 0.913 | [0.732, 0.976] | +0.078 **\*** |

*\* preco medio fora do IC da frequencia observada.*


## Calibracao — Out-of-sample, lead 24h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 27 | 0.007 | 0.000 | [0.000, 0.125] | +0.007 |
| 2%–5% | 28 | 0.037 | 0.107 | [0.037, 0.272] | -0.070 **\*** |
| 5%–10% | 56 | 0.075 | 0.125 | [0.062, 0.236] | -0.050 |
| 10%–20% | 75 | 0.154 | 0.293 | [0.202, 0.404] | -0.139 **\*** |
| 20%–35% | 178 | 0.280 | 0.326 | [0.261, 0.398] | -0.046 |
| 35%–50% | 278 | 0.429 | 0.417 | [0.361, 0.476] | +0.012 |
| 50%–65% | 290 | 0.565 | 0.576 | [0.518, 0.631] | -0.011 |
| 65%–80% | 184 | 0.718 | 0.674 | [0.603, 0.737] | +0.044 |
| 80%–90% | 74 | 0.845 | 0.716 | [0.605, 0.806] | +0.129 **\*** |
| 90%–95% | 55 | 0.923 | 0.873 | [0.760, 0.937] | +0.051 |
| 95%–98% | 30 | 0.962 | 0.867 | [0.703, 0.947] | +0.095 **\*** |
| 98%–100% | 27 | 0.993 | 1.000 | [0.875, 1.000] | -0.007 |

*\* preco medio fora do IC da frequencia observada.*


## Sensibilidade ao custo — lead 24h (out-of-sample)

| Spread | Apostas | Expectancia | IC 95% |
|---|---|---|---|
| 0.000 | 89 | -0.0197R | [-0.032, +0.021] |
| 0.005 | 82 | -0.0240R | [-0.034, +0.038] |
| 0.010 | 79 | -0.0275R | [-0.037, +0.035] |
| 0.020 | 73 | -0.0351R | [-0.044, +0.030] |

Um vies pode ser real e mesmo assim nao ser operavel: num mercado de 5 centavos, 1 centavo de spread leva um quinto do premio.


---

## Sensibilidade a defasagem do preco

| Defasagem maxima | Mercados | Azaroes | Vies | p-valor |
|---|---|---|---|---|
| ≤ 0.5h | 462 | 161 | -0.0179 | 0.0538 |
| ≤ 1h | 843 | 248 | -0.0262 | 0.0040 |
| ≤ 2h | 847 | 248 | -0.0262 | 0.0040 |
| ≤ 6h | 847 | 248 | -0.0262 | 0.0040 |
| ≤ 12h | 847 | 248 | -0.0262 | 0.0040 |
| ≤ 24h | 847 | 248 | -0.0262 | 0.0040 |
| ≤ 48h | 847 | 248 | -0.0262 | 0.0040 |

**Esta e a tabela que decide se o achado e real.** O preco lido e o do ultimo negocio ANTES do instante medido. Se esse negocio aconteceu horas antes, o preco esta velho -- e um azarao que negociou a 0,05, subiu e ganhou entraria como 'custava 0,05 e aconteceu', fabricando sozinho a aparencia de azarao barato.

Se o vies encolher em direcao a zero conforme a tolerancia aperta, ele vinha de preco velho. Se ficar estavel, e do mercado.


---

## Descartes na coleta

| Motivo | Mercados |
|---|---|
| sem preco em nenhum lead | 1334 |
| sem preco no lead de 24h | 491 |
| sem desfecho definido | 49 |

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
