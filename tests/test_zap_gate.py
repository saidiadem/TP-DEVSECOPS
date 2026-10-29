import unittest
from scripts.zap_gate import evaluate


class ZapGateTests(unittest.TestCase):
    def test_high_is_blocked(self):
        self.assertEqual(evaluate({"site": [{"alerts": [
            {"riskcode": "3", "name": "XSS"}
        ]}]}), ["XSS"])

    def test_medium_is_allowed(self):
        self.assertEqual(evaluate({"site": [{"alerts": [
            {"riskcode": "2", "name": "Medium"}
        ]}]}), [])

    def test_clean_target_is_allowed(self):
        self.assertEqual(evaluate({"site": [{"alerts": []}]}), [])

    def test_missing_target_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({"site": []})

    def test_missing_alerts_is_rejected(self):
        with self.assertRaises(KeyError):
            evaluate({"site": [{}]})
