import json
import unittest

from research.experiments.first_serve_direction_process_uncertainty import (
    CalibrationCase,
    ProcessEstimate,
    estimate_process_variances,
    finite_sample_quantile,
    required_process_variance,
    score_process_histories,
    summarize,
)
from research.experiments.first_serve_direction_robustness import (
    COMPONENTS,
    ComponentEstimate,
    build_histories,
)
from tests.test_first_serve_direction_robustness import record


class FirstServeDirectionProcessUncertaintyTests(unittest.TestCase):
    def test_required_variance_is_zero_when_base_interval_covers(self) -> None:
        history = ComponentEstimate(0.5, 0.5, 0.1, 0.1)
        future = ComponentEstimate(0.55, 0.55, 0.1, 0.1)
        self.assertEqual(required_process_variance(history, future), 0)

    def test_finite_sample_quantile_uses_conservative_rank(self) -> None:
        values = list(range(100))
        self.assertEqual(finite_sample_quantile(values, 0.95), 95)
        with self.assertRaises(ValueError):
            finite_sample_quantile([], 0.95)

    def test_process_estimator_backs_off_from_sparse_tour_component(self) -> None:
        cases = [
            CalibrationCase("ATP", component, float(index))
            for component in COMPONENTS
            for index in range(5)
        ] + [
            CalibrationCase("WTA", component, float(index))
            for component in COMPONENTS
            for index in range(5)
        ]
        estimates = estimate_process_variances(cases)
        self.assertEqual(estimates[("ATP", "deuce_wide")].source, "global")
        self.assertEqual(estimates[("WTA", "ad_t")].calibration_cases, 60)

    def test_process_radius_never_narrows_base_radius(self) -> None:
        history_records = [record("Alice", 2018, 1), record("Alice", 2019, 2)]
        test_records = [record("Alice", 2020, 3), record("Alice", 2020, 4)]
        history = next(iter(build_histories(history_records, 2018, 2020).values()))
        test = next(iter(build_histories(test_records, 2020, 2021).values()))
        estimates = {
            ("ATP", component): ProcessEstimate(0.01, "fixture", 30)
            for component in COMPONENTS
        }
        row = score_process_histories(history, test, 2020, estimates)
        self.assertTrue(
            all(
                process >= base
                for base, process in zip(row.base_radii, row.process_radii)
            )
        )

    def test_summary_does_not_expose_identity(self) -> None:
        history_records = [record("Alice", 2018, 1), record("Alice", 2019, 2)]
        test_records = [record("Alice", 2020, 3), record("Alice", 2020, 4)]
        history = next(iter(build_histories(history_records, 2018, 2020).values()))
        test = next(iter(build_histories(test_records, 2020, 2021).values()))
        estimates = estimate_process_variances(
            [
                CalibrationCase("ATP", component, 0.01)
                for component in COMPONENTS
                for _ in range(30)
            ]
        )
        row = score_process_histories(history, test, 2020, estimates)
        serialized = json.dumps(summarize([row]))
        self.assertNotIn("Alice", serialized)
        self.assertNotIn("alice", serialized)


if __name__ == "__main__":
    unittest.main()
