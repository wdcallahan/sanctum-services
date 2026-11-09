"""No automatic Kuma monitor mutations until the retained instance is qualified."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class KumaDesiredTests(unittest.TestCase):
    def test_joule_wicket_handoff_is_exact_and_unique(self):
        doc = yaml.safe_load((ROOT / "data/kuma-monitors.yml").read_text("utf8"))
        monitors = doc["kuma_monitors"]
        self.assertEqual(len(monitors), len({m["key"] for m in monitors}))
        wicket = next(m for m in monitors if m["key"] == "wicket_ollama")
        self.assertEqual(wicket["name"], "Wicket Ollama")
        self.assertEqual(wicket["type"], "http")
        self.assertEqual(wicket["method"], "GET")
        self.assertEqual(wicket["url"], "http://wicket.arcane.sanctum:11435/healthz")
        self.assertEqual(wicket["intended_state"], "active_after_retained_kuma_acceptance")
        self.assertEqual(wicket["accepted_status_codes"], ["200-299"])


if __name__ == "__main__":
    unittest.main()
