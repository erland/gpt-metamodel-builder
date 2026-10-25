"""Focused CORE-013 preflight and legacy migration safety regression."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mmp_capability_policy import required_capabilities, require_legacy_safe

class CapabilityGateTests(unittest.TestCase):
    def test_legacy_without_extensions(self):
        require_legacy_safe({"id": "old"})
    def test_legacy_unrelated_extensions(self):
        require_legacy_safe({"extensions": {"custom": {"preserved": True}}})
    def test_declared_empty_capabilities(self):
        require_legacy_safe({"extensions": {"mmp_required_capabilities": []}})
    def test_known_or_unknown_critical_is_rejected_until_negotiable(self):
        with self.assertRaisesRegex(ValueError, "not_supported"):
            require_legacy_safe({"extensions": {"mmp_required_capabilities": [
                {"id": "mmp-pairwise-relationships", "version": "1.0.0"}]}})
    def test_invalid_declaration_rejected(self):
        for value in ["anything", [{}], [{"id": "x", "version": ""}],
                      [{"id":"x","version":"1"},{"id":"x","version":"1"}]]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                required_capabilities({"extensions":{"mmp_required_capabilities":value}})

if __name__ == "__main__":
    unittest.main()
