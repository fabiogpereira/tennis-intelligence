import unittest

from pipelines.processing.mcp_notation import parse_notation


class McpNotationTests(unittest.TestCase):
    def test_parses_ace_and_unreturnable(self) -> None:
        ace = parse_notation("5*", "1st")
        unreturnable = parse_notation("6#", "1st")
        self.assertTrue(ace.valid)
        self.assertEqual(ace.outcome, "ace")
        self.assertEqual(ace.serve_direction, "5")
        self.assertEqual(unreturnable.outcome, "unreturnable")

    def test_parses_first_serve_fault_with_lets(self) -> None:
        parsed = parse_notation("cc4e", "1st")
        self.assertTrue(parsed.valid)
        self.assertEqual(parsed.let_count, 2)
        self.assertEqual(parsed.serve_fault, "e")
        self.assertEqual(parsed.outcome, "serve_fault")

    def test_parses_serve_and_volley_fault(self) -> None:
        parsed = parse_notation("4+w", "1st")
        self.assertTrue(parsed.valid)
        self.assertTrue(parsed.serve_and_volley)
        self.assertEqual(parsed.serve_fault, "w")

    def test_parses_rally_winner_and_error(self) -> None:
        winner = parse_notation("5f2f1f1v2n@", "1st")
        self.assertTrue(winner.valid)
        self.assertEqual(len(winner.shots), 4)
        self.assertEqual(winner.shots[-1].shot_type, "v")
        self.assertEqual(winner.shots[-1].error_detail, "n")
        self.assertEqual(winner.outcome, "unforced_error")

    def test_parses_serve_and_volley_return_depth_and_winner(self) -> None:
        parsed = parse_notation("4+b27v1*", "1st")
        self.assertTrue(parsed.valid)
        self.assertTrue(parsed.serve_and_volley)
        self.assertEqual(parsed.shots[0].direction, "2")
        self.assertEqual(parsed.shots[0].return_depth, "7")
        self.assertEqual(parsed.shots[-1].ending, "*")

    def test_parses_second_serve_rally_from_official_example(self) -> None:
        parsed = parse_notation("4s39b3b1w@", "2nd")
        self.assertTrue(parsed.valid)
        self.assertEqual(parsed.shots[0].shot_type, "s")
        self.assertEqual(parsed.shots[0].return_depth, "9")
        self.assertEqual(parsed.outcome, "unforced_error")

    def test_parses_shot_position_and_net_cord_modifiers(self) -> None:
        parsed = parse_notation("6f;1b-2z^2*", "1st")
        self.assertTrue(parsed.valid)
        self.assertEqual(parsed.shots[0].modifiers, (";",))
        self.assertEqual(parsed.shots[1].modifiers, ("-",))
        self.assertEqual(parsed.shots[2].modifiers, ("^",))

    def test_parses_challenge_ending(self) -> None:
        parsed = parse_notation("6b29C", "1st")
        self.assertTrue(parsed.valid)
        self.assertEqual(parsed.shots[0].return_depth, "9")
        self.assertEqual(parsed.outcome, "incorrect_challenge")

    def test_preserves_optional_direction_as_missing(self) -> None:
        parsed = parse_notation("6fb#", "1st")
        self.assertTrue(parsed.valid)
        self.assertIsNone(parsed.shots[0].direction)
        self.assertIsNone(parsed.shots[1].direction)

    def test_parses_exceptional_point_without_inventing_shots(self) -> None:
        parsed = parse_notation("S", "1st")
        self.assertTrue(parsed.valid)
        self.assertEqual(parsed.exceptional, "server_awarded_unobserved")
        self.assertEqual(parsed.shots, ())
        self.assertEqual(parsed.serve_direction_state, "not_applicable")

    def test_rejects_whitespace_and_undocumented_characters(self) -> None:
        parsed = parse_notation(" 6f2*", "1st")
        self.assertFalse(parsed.valid)
        self.assertEqual(parsed.issues[0].code, "expected_serve_direction")

    def test_rejects_rally_without_point_ending(self) -> None:
        parsed = parse_notation("6f2b1", "1st")
        self.assertFalse(parsed.valid)
        self.assertEqual(parsed.issues[0].code, "missing_point_ending")
        self.assertEqual(parsed.serve_direction_state, "observed")
        self.assertEqual(parsed.rally_state, "observed")
        self.assertEqual(parsed.outcome_state, "absent")
        self.assertEqual(len(parsed.shots), 2)

    def test_preserves_safe_prefix_when_later_rally_token_is_unsupported(self) -> None:
        parsed = parse_notation("6b39f28*", "1st")
        self.assertFalse(parsed.valid)
        self.assertEqual(parsed.issues[0].code, "expected_shot_type")
        self.assertEqual(parsed.serve_direction, "6")
        self.assertEqual(parsed.serve_direction_state, "observed")
        self.assertEqual(parsed.rally_state, "partial")
        self.assertEqual([shot.shot_type for shot in parsed.shots], ["b", "f"])
        self.assertEqual(parsed.outcome_state, "invalid")

    def test_preserves_fault_and_serve_fields_before_trailing_extension(self) -> None:
        parsed = parse_notation("4n;", "1st")
        self.assertFalse(parsed.valid)
        self.assertEqual(parsed.serve_direction, "4")
        self.assertEqual(parsed.serve_fault, "n")
        self.assertEqual(parsed.outcome, "serve_fault")
        self.assertEqual(parsed.rally_state, "not_applicable")
        self.assertEqual(parsed.outcome_state, "observed")

    def test_invalid_serve_prefix_does_not_expose_partial_fields(self) -> None:
        parsed = parse_notation("n", "1st")
        self.assertFalse(parsed.valid)
        self.assertIsNone(parsed.serve_direction)
        self.assertEqual(parsed.serve_direction_state, "invalid")
        self.assertEqual(parsed.rally_state, "invalid")


if __name__ == "__main__":
    unittest.main()
