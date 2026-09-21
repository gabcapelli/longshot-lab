# longshot-lab

Teste do **vies favorito-azarao** em mercados de previsao (Polymarket).

A pergunta, em uma frase: **entre os mercados precificados a 5%, o evento
aconteceu menos de 5% das vezes?**

Se sim, azarao custa mais do que vale, e vender azarao de forma sistematica
tem valor esperado positivo. Nao e preciso prever nada -- so identificar o
preco e ter disciplina.

## Por que esta hipotese, e nao outra

Ela nao e um palpite. O vies favorito-azarao e uma das anomalias mais
documentadas em mercados de aposta, observada desde os anos 1940 em corridas
de cavalo e replicada em varios esportes e paises. A explicacao usual e
comportamental: azarao paga muito se der, e a chance de ganhar grande atrai
aposta demais, empurrando o preco acima do valor justo.

Tres consequencias praticas, que e por que ela veio antes das alternativas:

1. **Nao exige previsao.** As tentativas anteriores (price action, stat arb)
   exigiam enxergar no preco algo que o mercado nao enxerga. Esta so exige
   identificar preco fora da faixa.
2. **E falseavel com dado publico.** Mercado resolvido tem desfecho conhecido;
   basta comparar com o preco de antes.
3. **Fica onde o profissional nao esta.** Mercado de previsao e pequeno demais
   para caber capital institucional -- que e a razao de a anomalia poder
   sobreviver.

## O desenho

```
mercados binarios resolvidos do Polymarket
   |
   +-- preco a 24h do FIM (nao o preco final)
   |
   +-- IN-SAMPLE (60% mais antigos)   -> calibracao e vies
   |
   +-- OUT-OF-SAMPLE (40% mais novos) -> confirmacao
```

**Por que nao o preco final:** perto da resolucao o preco converge para o
desfecho por construcao. Usa-lo seria medir a propria resposta e encontrar
"previsao perfeita" em qualquer mercado.

## As defesas contra auto-engano

| Defesa | Fecha qual porta |
|---|---|
| **Buckets de preco pre-registrados** | Escolher fronteira depois de ver o dado fabrica vies que nao existe |
| **Nula de mercado calibrado** | Em bucket pequeno, ruido parece vies; a nula mede exatamente quanto ruido esperar |
| **Split temporal in/out-of-sample** | Detecta se o vies existiu no passado e sumiu |
| **IC de Wilson** | As proporcoes vivem perto de 0 e 1, onde o IC normal da limite negativo e cobertura errada |
| **Bootstrap de blocos semanais** | Mercados que resolvem na mesma semana sao correlacionados (mesma eleicao, mesmo evento) |
| **Tabela de sensibilidade ao spread** | Separa "o vies existe" de "da para explorar" |

### A nula nao e zero

A hipotese nula nao e "vies igual a zero". E: **cada mercado e uma moeda
honesta com a probabilidade que ele mesmo anuncia.** O codigo simula os
desfechos a partir dos proprios precos observados, milhares de vezes, e mede
que vies a pura sorte produziria naquele conjunto exato de precos e naquele
tamanho de amostra. So desvio maior que essa faixa conta como achado.

Sem isso, um bucket com 40 mercados produz "vies" impressionante toda vez.

### O custo pode matar um vies real

Vender a 5 centavos com 1 centavo de spread significa vender a 4,5 -- um
decimo do premio vai embora antes de comecar. O relatorio traz uma tabela de
sensibilidade justamente porque **"existe" e "da para explorar" sao perguntas
diferentes**, e a segunda e a que decide se vale operar.

## Validacao da maquinaria

`tests/test_sintetico.py` constroi dois mundos artificiais e exige que o
pipeline os separe:

| Mundo | Vies medido | p-valor | Backtest (sem custo) |
|---|---|---|---|
| **Enviesado** (azarao caro por construcao) | +0,0394 | 0,0003 | +0,0197R, IC [+0,011, +0,027] |
| **Honesto** (preco = probabilidade real) | −0,0019 | 0,69 | +0,0069R, IC [−0,001, +0,015] |

Mais um teste de nivel: 20 mundos honestos com sementes diferentes, exigindo
que a taxa de falso positivo a 5% fique proxima de 5%.

O teste de poder e o que torna um eventual resultado negativo interpretavel.
Um codigo que nunca acha nada passaria no teste de nivel sendo inutil -- e ai
"nao achei vies no Polymarket" seria indistinguivel de "meu codigo nao acha
vies nenhum". O CI roda essa validacao **antes** de tocar em dado real.

## Como rodar

Pelo GitHub Actions (aba Actions -> "estudo" -> Run workflow), em dois modos:

- **sondar** — imprime a estrutura crua que a API devolve. Rode primeiro: o
  leitor foi escrito sem acesso a API, entao conferir nomes de campo antes de
  confiar no resultado nao e zelo excessivo, e o minimo.
- **estudo** — roda a analise e publica `resultados/relatorio.md`.

Local:

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v    # valida a maquinaria
python -m lab.fetch --sondar               # confere o formato da API
python -m lab.study --max-mercados 3000    # roda o estudo
```

## Como ler o resultado

O relatorio comeca com um veredito explicito. Os tres desfechos possiveis:

- **Vies confirmado** (p < 0,05, vies positivo) — azarao custa mais do que
  vale. Ai a pergunta passa a ser a tabela de spread: sobra depois do custo?
- **Sem evidencia** — o desvio cabe no que a sorte produziria. Nao e "quase
  deu", e "nao da para distinguir de ruido".
- **Vies invertido** — azarao custa menos do que vale. Seria um achado, mas
  contrario a literatura, e exigiria explicacao antes de qualquer aposta.

Se der "sem evidencia", **nao varra limiar e lead ate fechar acima de zero.**
Isso e multiplicidade de teste, e e exatamente o erro que o desenho existe
para evitar.

## Limites conhecidos

- **Capacidade.** Mesmo que o vies exista, mercado de previsao e raso. Pode
  caber pouco dinheiro por aposta -- o retorno percentual nao se traduz em
  retorno absoluto grande.
- **Spread e profundidade nao sao modelados a fundo.** O estudo aplica um
  spread fixo, nao o livro de ofertas real de cada mercado. Em azarao ilíquido
  o custo verdadeiro pode ser pior.
- **Sobrevivencia.** So entram mercados que resolveram e que a API ainda
  devolve. Mercados removidos ou cancelados nao aparecem.
- **Risco de resolucao.** O estudo trata o desfecho como verdade. Disputa de
  resolucao, criterio ambiguo e resolucao contestada existem e nao estao
  modelados.
- **Nao e conselho de investimento.** Um vies medido no passado pode ter
  desaparecido, inclusive por ter sido descoberto.
