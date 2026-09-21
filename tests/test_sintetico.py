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
