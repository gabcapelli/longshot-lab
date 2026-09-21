"""
Leitura de preco nos leads: exigencia de negociacao real e defasagem.

Os dois guardas testados aqui existem por causa de erros que ja produziram um
resultado falso sobre dado real:

  - Sem exigir negociacao anterior, o estudo lia o valor inicial de 0,50 de
    mercados que nunca negociaram e o tratava como opiniao de mercado.
  - Sem limitar a defasagem, um preco de horas antes era tratado como o preco
    do instante medido -- e um azarao que negociou barato, subiu e ganhou
    entraria como "custava pouco e aconteceu", fabricando azarao barato.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lab import fetch

H = 3600
FIM = 1_000_000          # ancora ficticia


class TestPrecosNosLeads(unittest.TestCase):
    def setUp(self):
        self._orig = fetch.historico_preco

    def tearDown(self):
        fetch.historico_preco = self._orig

    def _com_historico(self, pontos):
        fetch.historico_preco = lambda _tok, fidelity=60: sorted(pontos)

    def test_le_o_ultimo_preco_antes_do_lead(self):
        self._com_historico([(FIM - 10 * H, 0.20), (FIM - 7 * H, 0.30),
                             (FIM - 5 * H, 0.40), (FIM - 1 * H, 0.90)])
        r = fetch.precos_nos_leads("t", FIM, leads=(6,), min_pontos=2)
        self.assertIn(6, r)
        self.assertAlmostEqual(r[6]["preco"], 0.30, places=9,
                               msg="pegou preco posterior ao instante medido")
        self.assertAlmostEqual(r[6]["defasagem_h"], 1.0, places=6)

    def test_rejeita_serie_constante(self):
        """Mercado que nunca negociou: serie inteira no valor inicial."""
        self._com_historico([(FIM - (12 - i) * H, 0.50) for i in range(6)])
        r = fetch.precos_nos_leads("t", FIM, leads=(6,), min_pontos=2)
        self.assertEqual(r, {}, "aceitou preco de mercado que nunca negociou")

    def test_rejeita_historico_curto_demais(self):
        self._com_historico([(FIM - 9 * H, 0.10), (FIM - 8 * H, 0.20)])
        r = fetch.precos_nos_leads("t", FIM, leads=(6,), min_pontos=3)
        self.assertEqual(r, {}, "aceitou preco com pontos de menos")

    def test_rejeita_preco_velho_demais(self):
        """Ultimo negocio 20h antes do instante medido, tolerancia de 6h."""
        self._com_historico([(FIM - 40 * H, 0.05), (FIM - 30 * H, 0.06),
                             (FIM - 26 * H, 0.05)])
        r = fetch.precos_nos_leads("t", FIM, leads=(6,), min_pontos=2,
                                   max_defasagem_h=6)
        self.assertEqual(r, {}, "aceitou preco com 20h de defasagem")

    def test_aceita_o_mesmo_preco_com_tolerancia_folgada(self):
        """Mesmo dado, tolerancia larga: entra, mas com defasagem registrada --
        e por isso que a tabela de sensibilidade consegue existir."""
        self._com_historico([(FIM - 40 * H, 0.05), (FIM - 30 * H, 0.06),
                             (FIM - 26 * H, 0.05)])
        r = fetch.precos_nos_leads("t", FIM, leads=(6,), min_pontos=2,
                                   max_defasagem_h=48)
        self.assertIn(6, r)
        self.assertAlmostEqual(r[6]["defasagem_h"], 20.0, places=6)

    def test_leads_independentes(self):
        """Um lead pode existir e o outro nao, na mesma serie."""
        self._com_historico([(FIM - 30 * H, 0.10), (FIM - 25 * H, 0.15),
                             (FIM - 23 * H, 0.20), (FIM - 2 * H, 0.80)])
        r = fetch.precos_nos_leads("t", FIM, leads=(6, 24), min_pontos=2,
                                   max_defasagem_h=6)
        self.assertIn(24, r, "lead de 24h deveria existir (negocio 1h antes)")
        self.assertNotIn(6, r, "lead de 6h deveria cair por defasagem de 17h")


if __name__ == "__main__":
    unittest.main(verbosity=2)
