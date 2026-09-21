# Contexto do projeto — longshot-lab

> Laboratorio de pesquisa. Nao e producao, nao tem dinheiro real. O produto e
> um numero com intervalo de confianca.

## De onde isto veio

Terceiro teste de uma serie. Os dois anteriores morreram, e vale saber de que:

1. **`gabcapelli/trading-monitor`** — checklist mecanico de price action.
   Expectancia -0,147R, IC 95% [-0,289, -0,001], n=539, replicado 3 dias
   depois. Morreu por evidencia.
2. **`gabcapelli/stat-arb-lab`** — pairs trading em perpetuos de cripto.
   Nao chegou a ter backtest util: **nao existe cointegracao para operar**.
   1 par de 47 intra-setor contra 2,4 que o acaso produziria, replicado em 1H
   e 4H. O diagnostico explicou o mecanismo: correlacao mediana de retornos de
   0,79, mas dos 41 pares com correlacao >= 0,70, quarenta falham no teste de
   cointegracao. Retorno correlacionado nao e nivel cointegrado.

**O padrao das duas mortes:** ambas apostavam que o Gabriel enxerga no preco
publico algo que o mercado nao enxerga, em ativos liquidos e muito disputados.

**Este projeto muda de familia.** Nao aposta em ser mais esperto: aposta numa
anomalia comportamental documentada, num mercado pequeno demais para atrair
capital institucional. Se este tambem morrer, o que morre nao e mais uma
estrategia -- e a tese de que ha edge acessivel ao varejo nesse formato.

## Decisoes metodologicas (nao reabrir sem motivo novo)

- **Buckets de preco pre-registrados** em `analise.BUCKETS`, fixados antes de
  ver dado real. Nao ajuste fronteira depois de olhar resultado.
- **Preco a distancia fixa do fim** (default 24h), nunca o preco final. O
  preco final converge para o desfecho por construcao.
- **A nula e "mercado calibrado", nao "vies zero"** (`stats.nula_calibrada`).
  Simula desfechos a partir dos proprios precos. E o que impede ruido de
  bucket pequeno virar descoberta.
- **IC de Wilson**, nao normal: as proporcoes vivem perto de 0 e 1.
- **Bootstrap de blocos semanais**, herdado do stat-arb-lab. Mercados que
  resolvem na mesma semana (mesma eleicao, mesmo evento) sao correlacionados.
- **Tabela de sensibilidade ao spread** sai sempre. Vies real e vies operavel
  sao perguntas diferentes.
- **Contabilidade do R**: vender SIM a p arrisca (1-p) para ganhar p, entao
  R-multiplo = (p - y)/(1 - p). Conferida por teste. Nao mexa sem refazer o
  teste.

## O parser da API foi escrito as cegas

Sessoes do Claude Code na web nao tem acesso de rede ao Polymarket (bloqueio
de politica do proxy). O leitor em `fetch.py` foi escrito sem nunca ter visto
uma resposta real da Gamma, entao:

- Ele e **tolerante de proposito**: le campos por varios nomes possiveis e
  descarta o que nao encaixa, com motivo registrado.
- A **contagem de descartes por motivo sai no relatorio**. Se um motivo
  dominar, o problema e o parser, nao o mercado.
- Existe o modo `python -m lab.fetch --sondar`, que imprime a estrutura crua.
  **Rode isso antes de confiar em qualquer resultado.**

## A validacao sintetica e obrigatoria

`tests/test_sintetico.py` prova que o pipeline acha vies no mundo enviesado
(+0,0394, p=0,0003) e nao acha no honesto (-0,0019, p=0,69), alem de aferir a
taxa de falso positivo em 20 mundos honestos.

Isso nao e cerimonia de CI: **e o que torna um resultado negativo
interpretavel.** Sem o teste de poder, "nao achei vies" seria indistinguivel
de "meu codigo nao acha vies nenhum" -- a ambiguidade que o trading-monitor
levou meses para eliminar.

## Como o Gabriel gosta de trabalhar

- Fonte de verdade e a documentacao estruturada; nao assuma o que nao esta escrito.
- Testar hipotese em vez de assumir; exigir criterio objetivo de credibilidade.
- Ao identificar problema no output, ele nomeia direto e espera correcao
  substantiva.
- Comeca por resumo objetivo e compacto; ressalva vem depois, se ele pedir.
- **Explique em linguagem simples.** Ele pediu isso explicitamente. Jargao sem
  traducao nao ajuda ninguem a decidir.
- **Resultado negativo e resultado.** Nao varra limiar nem lead ate o IC
  fechar acima de zero.
