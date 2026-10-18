import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import pdx  # noqa: E402


class ParseTests(unittest.TestCase):
    def test_key_values_blocks_and_bare_values(self):
        entries = pdx.parse('a = 1\nb = { c = "x y"  d >= 2 }\nlist = { "one" two }\n')
        self.assertEqual([e.key for e in entries], ["a", "b", "list"])
        self.assertEqual(entries[0].value, "1")
        self.assertEqual(pdx.first(entries[1].value, "c").value, "x y")
        self.assertEqual(pdx.first(entries[1].value, "d").op, ">=")
        self.assertEqual(pdx.bare_values(entries[2].value), ["one", "two"])

    def test_comments_bom_and_line_numbers(self):
        entries = pdx.parse('﻿# header\nfoo = { # trailing { brace in comment\n\tbar = "a # not a comment"\n}\n')
        self.assertEqual(len(entries), 1)
        bar = pdx.first(entries[0].value, "bar")
        self.assertEqual(bar.value, "a # not a comment")
        self.assertEqual(bar.line, 3)

    def test_unbalanced_braces_raise(self):
        for bad in ("a = { b = 1", "a = 1 }", "a = ", "a = = 1"):
            with self.subTest(bad=bad), self.assertRaises(pdx.ParseError):
                pdx.parse(bad)

    def test_walk_visits_nested_entries(self):
        entries = pdx.parse("a = { b = { c = 1 } d = 2 }")
        self.assertEqual([e.key for e in pdx.walk(entries)], ["a", "b", "c", "d"])

    def test_variables_and_value_references(self):
        entries = pdx.parse("x = { base = @civic_rare_random_weight add = value:foo|A|b| mult = trigger:years_passed }")
        vals = {e.key: e.value for e in entries[0].value}
        self.assertEqual(vals["base"], "@civic_rare_random_weight")
        self.assertEqual(vals["add"], "value:foo|A|b|")
        self.assertEqual(vals["mult"], "trigger:years_passed")


if __name__ == "__main__":
    unittest.main()
