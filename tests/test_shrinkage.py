import unittest

from models.shrinkage import beta_posterior, dirichlet_posterior


class ShrinkageTests(unittest.TestCase):
    def test_beta_strength_pulls_estimate_toward_prior(self) -> None:
        raw, raw_sd = beta_posterior(8, 10, 0.5, 0)
        pooled, pooled_sd = beta_posterior(8, 10, 0.5, 100)
        self.assertGreater(raw, pooled)
        self.assertGreater(pooled, 0.5)
        self.assertLess(pooled_sd, raw_sd)

    def test_beta_rejects_invalid_counts(self) -> None:
        with self.assertRaises(ValueError):
            beta_posterior(11, 10, 0.5, 10)

    def test_dirichlet_strength_pulls_each_component_toward_prior(self) -> None:
        raw, raw_sd = dirichlet_posterior((8, 1, 1), (1 / 3,) * 3, 0)
        pooled, pooled_sd = dirichlet_posterior((8, 1, 1), (1 / 3,) * 3, 100)
        self.assertGreater(raw[0], pooled[0])
        self.assertGreater(pooled[0], 1 / 3)
        self.assertLess(pooled_sd[0], raw_sd[0])
        self.assertAlmostEqual(sum(pooled), 1.0)

    def test_dirichlet_rejects_invalid_prior(self) -> None:
        with self.assertRaises(ValueError):
            dirichlet_posterior((1, 1, 1), (0.2, 0.2, 0.2), 10)


if __name__ == "__main__":
    unittest.main()
