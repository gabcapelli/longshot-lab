"""
Validacao com mercados SINTETICOS de resposta conhecida.

Dois mundos:
  ENVIESADO  -- azarao custa mais do que vale, por construcao
  HONESTO    -- preco e exatamente a probabilidade verdadeira

Exige que o pipeline separe os dois. O teste de PODER (achar vies no mundo
enviesado) e tao importante quanto o de NIVEL (nao achar no honesto): um
codigo que nunca acha nada passaria no segundo sendo inutil, e ai um "nao
achei vies" sobre o Polymarket seria indistinguivel de "meu codigo nao acha
vies nenhum".
"""

import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lab.analise import (agregar, backtest_vender_azarao, tabela_calibracao,
                         teste_vies)

N = 6000
EXPOENTE_VIES = 0.85   # p = q**0.85 empurra azarao para cima; 1.0 = honesto


def mundo(enviesado, seed=3):
    """Devolve (precos, desfechos). Se enviesado, azarao custa mais do que vale."""
    rng = np.random.default_rng(seed)
    q = rng.beta(0.7, 2.0, N)              # muitas probabilidades baixas
    q = np.clip(q, 0.005, 0.995)
    p = q ** EXPOENTE_VIES if enviesado else q.copy()
    p = np.clip(p, 0.005, 0.995)
    y = (rng.random(N) < q).astype(float)  # desfecho segue a probabilidade VERDADEIRA
    return p, y


class TestMundoEnviesado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p, cls.y = mundo(enviesado=True)
        cls.vies = teste_vies(cls.p, cls.y, reps=2000)

    def test_detecta_o_vies(self):
        self.assertGreater(self.vies["vies"], 0, "vies deveria ser positivo")
        self.assertLess(self.vies["p_valor"], 0.01,
                        "nao detectou um vies construido de proposito")

    def test_vies_aparece_nas_faixas_baratas(self):
        """O vies favorito-azarao e um fenomeno de PONTA: tem de aparecer no
        azarao, nao espalhado por igual em todas as faixas."""
        tab = [b for b in tabela_calibracao(self.p, self.y) if b["n"] > 30]
        baratas = [b for b in tab if b["hi"] <= 0.20]
        self.assertTrue(baratas, "sem faixas baratas com amostra")
        self.assertTrue(all(b["diferenca"] > 0 for b in baratas),
                        "alguma faixa barata nao mostrou azarao caro")

    def test_backtest_lucra_sem_custo(self):
        tr = backtest_vender_azarao(self.p, self.y, np.arange(N), limiar=0.10, spread=0.0)
        ag = agregar(tr, np.arange(len(tr)) // 50, reps=2000)
        self.assertGreater(ag["n"], 200, "poucas apostas para concluir")
        self.assertGreater(ag["exp_r"], 0, "nao lucrou onde o vies existe")
        self.assertGreater(ag["ic_r"][0], 0, "IC deveria estar inteiro acima de zero")

    def test_custo_corroi_o_lucro(self):
        """Spread maior tem de reduzir a expectancia, sempre. Se nao reduzir,
        a contabilidade de custo esta errada."""
        exps = []
        for sp in (0.0, 0.01, 0.02):
            tr = backtest_vender_azarao(self.p, self.y, np.arange(N), limiar=0.10, spread=sp)
            exps.append(agregar(tr, np.arange(len(tr)) // 50, reps=500)["exp_r"])
        self.assertTrue(exps[0] > exps[1] > exps[2],
                        f"custo nao reduziu a expectancia monotonicamente: {exps}")


class TestMundoHonesto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p, cls.y = mundo(enviesado=False, seed=11)
        cls.vies = teste_vies(cls.p, cls.y, reps=2000)

    def test_nao_inventa_vies(self):
        self.assertGreater(self.vies["p_valor"], 0.05,
                           f"acusou vies num mercado honesto "
                           f"(vies={self.vies['vies']:+.4f}, p={self.vies['p_valor']:.4f})")

    def test_vies_proximo_de_zero(self):
        self.assertLess(abs(self.vies["vies"]), 0.02,
                        "vies medido longe de zero num mercado calibrado")

    def test_nivel_do_teste(self):
        """Repete o mundo honesto com sementes diferentes: a taxa de falso
        positivo a 5% tem de ficar perto de 5%."""
        rejeicoes = 0
        repeticoes = 20
        for s in range(repeticoes):
            p, y = mundo(enviesado=False, seed=100 + s)
            if teste_vies(p, y, reps=600)["p_valor"] < 0.05:
                rejeicoes += 1
        self.assertLessEqual(rejeicoes, 4,
                             f"{rejeicoes}/{repeticoes} falsos positivos: teste anticonservador")


class TestContabilidade(unittest.TestCase):
    def test_r_multiplo(self):
        """Vender SIM a 0,05: ganha 0,05/0,95 se NAO; perde 1R se SIM."""
        tr = backtest_vender_azarao(np.array([0.05, 0.05]), np.array([0.0, 1.0]),
                                    np.array([0, 1]), limiar=0.10, spread=0.0)
        self.assertAlmostEqual(tr[0]["r_multiplo"], 0.05 / 0.95, places=9)
        self.assertAlmostEqual(tr[1]["r_multiplo"], -1.0, places=9)

    def test_spread_reduz_preco_de_venda(self):
        tr = backtest_vender_azarao(np.array([0.10]), np.array([0.0]), np.array([0]),
                                    limiar=0.20, spread=0.02)
        self.assertAlmostEqual(tr[0]["preco_exec"], 0.09, places=9)

    def test_ignora_fora_do_limiar(self):
        tr = backtest_vender_azarao(np.array([0.5, 0.05]), np.array([0.0, 0.0]),
                                    np.array([0, 1]), limiar=0.10, spread=0.0)
        self.assertEqual(len(tr), 1, "apostou em mercado acima do limiar")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestDoisLados(unittest.TestCase):
    """Os dois lados de cada mercado, e por que o vies agregado morre com eles."""

    def setUp(self):
        from lab.analise import observacoes
        self.obs = observacoes(np.array([0.85, 0.30, 0.05]),
                               np.array([1.0, 0.0, 0.0]),
                               np.array([1, 2, 3]))

    def test_dobra_a_amostra(self):
        P, Y, T, I = self.obs
        self.assertEqual(len(P), 6)
        self.assertEqual(len(np.unique(I)), 3, "ids de mercado nao pareados")

    def test_lado_nao_e_o_complemento(self):
        P, Y, _T, _I = self.obs
        self.assertAlmostEqual(P[0] + P[3], 1.0, places=12)
        self.assertAlmostEqual(Y[0] + Y[3], 1.0, places=12)

    def test_vies_agregado_e_zero_por_construcao(self):
        """Se este teste falhar, a contabilidade dos dois lados esta errada --
        e o relatorio nao pode reportar vies agregado."""
        P, Y, _T, _I = self.obs
        self.assertAlmostEqual(float(np.mean(P - Y)), 0.0, places=12)

    def test_azarao_aparece_no_lado_certo(self):
        """Mercado com SIM a 0,85 tem azarao no NAO, a 0,15 -- e e ele que a
        regra deve pegar."""
        from lab.analise import backtest_vender_azarao
        P, Y, T, _I = self.obs
        tr = backtest_vender_azarao(P, Y, T, limiar=0.20, spread=0.0)
        precos = sorted(round(t["preco"], 2) for t in tr)
        self.assertEqual(precos, [0.05, 0.15],
                         f"regra pegou os precos errados: {precos}")


class TestCompraEVenda(unittest.TestCase):
    """Os dois lados da operacao, e o sinal do spread em cada um."""

    def test_contabilidade_da_compra(self):
        from lab.analise import backtest_comprar_azarao
        tr = backtest_comprar_azarao(np.array([0.05, 0.05]), np.array([1.0, 0.0]),
                                     np.array([0, 1]), limiar=0.10, spread=0.0)
        self.assertAlmostEqual(tr[0]["r_multiplo"], 0.95 / 0.05, places=9)
        self.assertAlmostEqual(tr[1]["r_multiplo"], -1.0, places=9)

    def test_spread_encarece_a_compra_e_barateia_a_venda(self):
        """Quem compra paga a ponta de venda; quem vende leva a de compra.
        Se os dois se movessem no mesmo sentido, o custo estaria errado."""
        from lab.analise import backtest_comprar_azarao
        c = backtest_comprar_azarao(np.array([0.10]), np.array([0.0]),
                                    np.array([0]), limiar=0.20, spread=0.02)
        v = backtest_vender_azarao(np.array([0.10]), np.array([0.0]),
                                   np.array([0]), limiar=0.20, spread=0.02)
        self.assertGreater(c[0]["preco_exec"], 0.10, "compra deveria pagar mais")
        self.assertLess(v[0]["preco_exec"], 0.10, "venda deveria receber menos")

    def test_custo_corroi_a_compra(self):
        from lab.analise import agregar, backtest_comprar_azarao
        p, y = mundo(enviesado=False, seed=5)
        exps = []
        for sp in (0.0, 0.01, 0.02):
            tr = backtest_comprar_azarao(p, y, np.arange(len(p)), limiar=0.10, spread=sp)
            exps.append(agregar(tr, np.arange(len(tr)) // 50, reps=400)["exp_r"])
        self.assertTrue(exps[0] > exps[1] > exps[2],
                        f"spread nao encareceu a compra: {exps}")
