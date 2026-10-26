"""Regression tests for large typed-pair schema validation."""
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fast_jsonschema import FastDraft202012Validator


class FastUniqueItemsTests(unittest.TestCase):
    def check_parity(self, values):
        schema = {"type": "array", "uniqueItems": True}
        baseline = list(Draft202012Validator(schema).iter_errors(values))
        optimized = list(FastDraft202012Validator(schema).iter_errors(values))
        self.assertEqual(bool(optimized), bool(baseline))

    def test_nested_typed_pairs(self):
        values = [
            {"source": {"kind": "element", "id": "a"},
             "target": {"kind": "junction", "id": "andjunction"}},
            {"source": {"kind": "element", "id": "b"},
             "target": {"kind": "junction", "id": "orjunction"}},
        ]
        self.check_parity(values)
        self.check_parity(values + [values[0]])

    def test_dict_order_does_not_hide_duplicates(self):
        self.check_parity([{"source": "x", "target": "y"},
                           {"target": "y", "source": "x"}])

    def test_fallback_for_numbers_and_booleans(self):
        for values in ([1, 1.0], [True, 1], [None, None],
                       [{"n": 1}, {"n": 1.0}],
                       [{"a": "x"}, {"a": "x", "b": None}]):
            with self.subTest(values=values):
                self.check_parity(values)

    def test_large_string_tree(self):
        values = [
            {"source": {"kind": "element", "id": f"source-{i}"},
             "target": {"kind": "element", "id": f"target-{i}"}}
            for i in range(14000)
        ]
        self.assertEqual(list(FastDraft202012Validator(
            {"type": "array", "uniqueItems": True}
        ).iter_errors(values)), [])
        self.assertEqual(len(list(FastDraft202012Validator(
            {"type": "array", "uniqueItems": True}
        ).iter_errors(values + [values[-1]]))), 1)


if __name__ == "__main__":
    unittest.main()
