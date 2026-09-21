# Vies favorito-azarao em prediction markets — resultado

Gerado em 2026-09-21 16:37 UTC · 2493 mercados resolvidos · encerrados entre 2026-08-22 e 2026-09-21 · 1356.6s

## Leitura rapida

*Verificacao de alinhamento: o preco final do token lido converge para o desfecho registrado em 97.8% dos mercados.*

Lead principal: **6h antes do fim** (cobertura 100.0% dos mercados).

**Sem evidencia de vies.** O desvio observado cabe dentro do que a sorte produziria num mercado calibrado.

- Entre as apostas precificadas até 10%: preço médio **0.021**, aconteceu de fato **0.024** das vezes.

- Vies (preco − frequencia real): **-0.0028** em 374 apostas de azarao, p = 0.6791

- Faixa que a nula produziria: [-0.0162, +0.0132]

- Comprar azarao (preco ≤ 0.10, spread 0.010): 374 apostas, **-0.6438R**, IC 95% [-1.000, -0.551]

- Vender azarao (preco ≤ 0.10, spread 0.010): 196 apostas, **-0.0123R**, IC 95% [-0.028, +0.032]


Se o vies aponta azarao barato, a operacao que ganharia e **comprar**. Medir so a venda responderia a pergunta errada.


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


**Sem evidencia de vies.** O desvio observado cabe dentro do que a sorte produziria num mercado calibrado.


| Recorte | Mercados | Azaroes (≤10%) | Vies no azarao | p-valor | Backtest (n) | Expectancia | IC 95% |
|---|---|---|---|---|---|---|---|
| In-sample | 1495 | 511 | -0.0193 | 0.0022 | 229 | -0.0521R | [-0.097, -0.024] |
| Out-of-sample | 998 | 374 | -0.0028 | 0.6791 | 196 | -0.0123R | [-0.028, +0.032] |


## Calibracao — In-sample, lead 6h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 364 | 0.003 | 0.011 | [0.004, 0.028] | -0.008 **\*** |
| 2%–5% | 70 | 0.033 | 0.043 | [0.015, 0.119] | -0.010 |
| 5%–10% | 75 | 0.072 | 0.147 | [0.084, 0.244] | -0.074 **\*** |
| 10%–20% | 129 | 0.153 | 0.163 | [0.109, 0.236] | -0.010 |
| 20%–35% | 360 | 0.277 | 0.294 | [0.250, 0.343] | -0.018 |
| 35%–50% | 478 | 0.434 | 0.435 | [0.391, 0.480] | -0.001 |
| 50%–65% | 511 | 0.560 | 0.560 | [0.516, 0.602] | +0.001 |
| 65%–80% | 364 | 0.722 | 0.706 | [0.657, 0.750] | +0.016 |
| 80%–90% | 128 | 0.846 | 0.836 | [0.762, 0.890] | +0.010 |
| 90%–95% | 75 | 0.926 | 0.840 | [0.741, 0.906] | +0.086 **\*** |
| 95%–98% | 70 | 0.966 | 0.957 | [0.881, 0.985] | +0.009 |
| 98%–100% | 366 | 0.997 | 0.989 | [0.972, 0.996] | +0.007 **\*** |

*\* preco medio fora do IC da frequencia observada.*

Leia esta tabela como tendo METADE das linhas independentes: como cada mercado entra com os dois lados, a faixa 10-20% e a faixa 80-90% contem os MESMOS mercados, espelhados. A simetria entre elas e construcao, nao confirmacao.


## Calibracao — Out-of-sample, lead 6h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 249 | 0.004 | 0.000 | [0.000, 0.015] | +0.004 |
| 2%–5% | 54 | 0.034 | 0.019 | [0.003, 0.098] | +0.015 |
| 5%–10% | 69 | 0.072 | 0.116 | [0.060, 0.212] | -0.044 |
| 10%–20% | 98 | 0.154 | 0.265 | [0.188, 0.360] | -0.111 **\*** |
| 20%–35% | 191 | 0.274 | 0.366 | [0.301, 0.437] | -0.092 **\*** |
| 35%–50% | 328 | 0.432 | 0.402 | [0.351, 0.456] | +0.030 |
| 50%–65% | 346 | 0.564 | 0.592 | [0.540, 0.643] | -0.028 |
| 65%–80% | 190 | 0.725 | 0.632 | [0.561, 0.697] | +0.094 **\*** |
| 80%–90% | 97 | 0.844 | 0.732 | [0.636, 0.810] | +0.112 **\*** |
| 90%–95% | 69 | 0.926 | 0.884 | [0.788, 0.940] | +0.042 |
| 95%–98% | 53 | 0.965 | 0.981 | [0.901, 0.997] | -0.016 |
| 98%–100% | 252 | 0.996 | 1.000 | [0.985, 1.000] | -0.004 |

*\* preco medio fora do IC da frequencia observada.*

Leia esta tabela como tendo METADE das linhas independentes: como cada mercado entra com os dois lados, a faixa 10-20% e a faixa 80-90% contem os MESMOS mercados, espelhados. A simetria entre elas e construcao, nao confirmacao.


## Sensibilidade ao custo — lead 6h (out-of-sample)

| Spread | Comprar: expectancia | IC 95% | Vender: expectancia | IC 95% |
|---|---|---|---|---|
| 0.000 | -0.6130R | [-1.000, -0.512] | -0.0032R | [-0.011, +0.019] |
| 0.005 | -0.6291R | [-1.000, -0.532] | -0.0087R | [-0.022, +0.027] |
| 0.010 | -0.6438R | [-1.000, -0.551] | -0.0123R | [-0.028, +0.032] |
| 0.020 | -0.6698R | [-1.000, -0.584] | -0.0206R | [-0.038, +0.035] |
| 0.030 | -0.6920R | [-1.000, -0.612] | -0.0296R | [-0.050, +0.038] |
| 0.050 | -0.7282R | [-1.000, -0.658] | -0.0461R | [-0.074, +0.027] |

**Esta tabela decide se o achado vira dinheiro.** Quem compra paga a ponta de venda; num mercado de 3 centavos, 1 centavo de spread e um terco do preco. Um vies real pode nao sobreviver ao custo, e ai ele e verdadeiro e inutil ao mesmo tempo.


---

# Lead de 24h (secundario)

Cobertura: 84.1% dos mercados coletados.


**Sem evidencia de vies.** O desvio observado cabe dentro do que a sorte produziria num mercado calibrado.


| Recorte | Mercados | Azaroes (≤10%) | Vies no azarao | p-valor | Backtest (n) | Expectancia | IC 95% |
|---|---|---|---|---|---|---|---|
| In-sample | 1258 | 430 | -0.0206 | 0.0040 | 248 | -0.0448R | [-0.053, -0.038] |
| Out-of-sample | 839 | 318 | -0.0003 | 0.9528 | 192 | -0.0071R | [-0.020, +0.030] |


## Calibracao — In-sample, lead 24h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 286 | 0.005 | 0.000 | [0.000, 0.013] | +0.005 |
| 2%–5% | 71 | 0.033 | 0.085 | [0.039, 0.172] | -0.051 **\*** |
| 5%–10% | 68 | 0.072 | 0.162 | [0.093, 0.267] | -0.090 **\*** |
| 10%–20% | 123 | 0.146 | 0.203 | [0.142, 0.283] | -0.057 |
| 20%–35% | 297 | 0.277 | 0.300 | [0.250, 0.354] | -0.022 |
| 35%–50% | 404 | 0.430 | 0.411 | [0.364, 0.459] | +0.019 |
| 50%–65% | 415 | 0.566 | 0.578 | [0.530, 0.625] | -0.013 |
| 65%–80% | 300 | 0.720 | 0.703 | [0.649, 0.752] | +0.017 |
| 80%–90% | 122 | 0.850 | 0.803 | [0.724, 0.864] | +0.047 |
| 90%–95% | 71 | 0.925 | 0.831 | [0.727, 0.901] | +0.094 **\*** |
| 95%–98% | 69 | 0.966 | 0.913 | [0.823, 0.960] | +0.052 **\*** |
| 98%–100% | 290 | 0.995 | 1.000 | [0.987, 1.000] | -0.005 |

*\* preco medio fora do IC da frequencia observada.*

Leia esta tabela como tendo METADE das linhas independentes: como cada mercado entra com os dois lados, a faixa 10-20% e a faixa 80-90% contem os MESMOS mercados, espelhados. A simetria entre elas e construcao, nao confirmacao.


## Calibracao — Out-of-sample, lead 24h

| Faixa de preco | Mercados | Preco medio | Aconteceu de fato | IC 95% | Diferenca |
|---|---|---|---|---|---|
| 0%–2% | 189 | 0.005 | 0.000 | [0.000, 0.020] | +0.005 |
| 2%–5% | 61 | 0.034 | 0.033 | [0.009, 0.112] | +0.001 |
| 5%–10% | 66 | 0.072 | 0.076 | [0.033, 0.165] | -0.004 |
| 10%–20% | 67 | 0.152 | 0.224 | [0.141, 0.337] | -0.072 |
| 20%–35% | 186 | 0.276 | 0.355 | [0.290, 0.426] | -0.079 **\*** |
| 35%–50% | 264 | 0.439 | 0.436 | [0.377, 0.496] | +0.003 |
| 50%–65% | 271 | 0.557 | 0.557 | [0.498, 0.615] | -0.000 |
| 65%–80% | 189 | 0.721 | 0.646 | [0.575, 0.710] | +0.076 **\*** |
| 80%–90% | 67 | 0.845 | 0.791 | [0.679, 0.871] | +0.054 |
| 90%–95% | 66 | 0.927 | 0.909 | [0.816, 0.958] | +0.018 |
| 95%–98% | 63 | 0.965 | 0.968 | [0.891, 0.991] | -0.003 |
| 98%–100% | 189 | 0.995 | 1.000 | [0.980, 1.000] | -0.005 |

*\* preco medio fora do IC da frequencia observada.*

Leia esta tabela como tendo METADE das linhas independentes: como cada mercado entra com os dois lados, a faixa 10-20% e a faixa 80-90% contem os MESMOS mercados, espelhados. A simetria entre elas e construcao, nao confirmacao.


## Sensibilidade ao custo — lead 24h (out-of-sample)

| Spread | Comprar: expectancia | IC 95% | Vender: expectancia | IC 95% |
|---|---|---|---|---|
| 0.000 | -0.5512R | [-1.000, -0.451] | -0.0004R | [-0.008, +0.020] |
| 0.005 | -0.5723R | [-1.000, -0.477] | -0.0036R | [-0.015, +0.029] |
| 0.010 | -0.5913R | [-1.000, -0.501] | -0.0071R | [-0.020, +0.030] |
| 0.020 | -0.6244R | [-1.000, -0.542] | -0.0146R | [-0.031, +0.034] |
| 0.030 | -0.6522R | [-1.000, -0.576] | -0.0213R | [-0.040, +0.038] |
| 0.050 | -0.6966R | [-1.000, -0.630] | -0.0361R | [-0.058, +0.027] |

**Esta tabela decide se o achado vira dinheiro.** Quem compra paga a ponta de venda; num mercado de 3 centavos, 1 centavo de spread e um terco do preco. Um vies real pode nao sobreviver ao custo, e ai ele e verdadeiro e inutil ao mesmo tempo.


---

## Sensibilidade a defasagem do preco

| Defasagem maxima | Mercados | Azaroes | Vies | p-valor |
|---|---|---|---|---|
| ≤ 0.5h | 596 | 276 | -0.0023 | 0.6977 |
| ≤ 1h | 997 | 374 | -0.0028 | 0.6791 |
| ≤ 2h | 998 | 374 | -0.0028 | 0.6791 |
| ≤ 6h | 998 | 374 | -0.0028 | 0.6791 |
| ≤ 12h | 998 | 374 | -0.0028 | 0.6791 |
| ≤ 24h | 998 | 374 | -0.0028 | 0.6791 |
| ≤ 48h | 998 | 374 | -0.0028 | 0.6791 |

**Esta e a tabela que decide se o achado e real.** O preco lido e o do ultimo negocio ANTES do instante medido. Se esse negocio aconteceu horas antes, o preco esta velho -- e um azarao que negociou a 0,05, subiu e ganhou entraria como 'custava 0,05 e aconteceu', fabricando sozinho a aparencia de azarao barato.

Se o vies encolher em direcao a zero conforme a tolerancia aperta, ele vinha de preco velho. Se ficar estavel, e do mercado.


---

## Descartes na coleta

| Motivo | Mercados |
|---|---|
| sem preco em nenhum lead | 977 |
| sem preco no lead de 24h | 396 |
| sem desfecho definido | 30 |

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
