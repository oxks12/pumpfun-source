import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rules_copy", ROOT / "scripts/extract-competition-rules-copy.py")
COPY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COPY)


class RulesCopy(unittest.TestCase):
    def test_authenticated_output_matches(self):
        self.assertEqual(COPY.generate(ROOT), (ROOT / COPY.OUTPUT).read_text(encoding="utf-8"))

    def test_selects_web_namespace_not_conflicting_mobile_copy(self):
        labels = COPY.extract((ROOT / COPY.SOURCE).read_text(encoding="utf-8"))
        self.assertEqual(len(labels), 32)
        self.assertIn("registration closes", labels["rule_join_solo"])
        self.assertIn("every position you hold at the start", labels["scoring_default"])
        self.assertEqual(labels["close"], "Close")

    def test_rejects_incomplete_or_duplicate_locale_records(self):
        row = {"locale": "en", "resources": {}}
        def script(value):
            return "<script>self.__next_f.push(" + json.dumps([1, value]) + ")</script>"
        with self.assertRaises(ValueError):
            COPY.extract(script("c1:" + json.dumps(row) + "\n"))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            COPY.extract(script("c1:" + json.dumps(row) + "\nc1:" + json.dumps(row) + "\n"))

    def test_rejects_non_json_flight_without_execution(self):
        with self.assertRaises(json.JSONDecodeError):
            COPY.extract('<script>self.__next_f.push([1, globalThis.neverExecute()])</script>')


if __name__ == "__main__":
    unittest.main()
