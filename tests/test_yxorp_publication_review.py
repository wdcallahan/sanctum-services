"""Verify read-only NPM projection comparison without accessing production."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools/review-yxorp-publication.py"
SPEC = importlib.util.spec_from_file_location("yxorp_review", MODULE)
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


def make_report(name="search.nexus.sanctum", port="8083"):
    return {
        "kvar_rootful": {
            "host": "kvar.outer.sanctum",
            "scope": "rootful",
            "containers": [{
                "name": "nginx-proxman",
                "proxy_routes": {
                    "status": "observed",
                    "routes": [{
                        "file": "1.conf", "status": "projected",
                        "duplicate_fields": False,
                        "sha256": "a" * 64,
                        "default_upstream": {
                            "server_names": [name], "server": "kvin.outer.sanctum",
                            "port": port, "forward_scheme": "http"
                        },
                    }],
                },
            }],
        },
    }


def make_desired():
    return {
        "yxorp_routes": [{
            "hostname": "search.nexus.sanctum",
            "upstream_scheme": "http", "upstream_host": "kvin.outer.sanctum",
            "upstream_port": 8083, "enabled": False,
        }],
    }


class PublicationComparison(unittest.TestCase):
    def test_comparison_keeps_disabled_desired_routes(self):
        result = review.compare(make_report(), make_desired())
        self.assertEqual(result["observed_host_count"], 1)
        self.assertEqual(result["proposed_host_count"], 1)
        self.assertFalse(result["review_required"])
        self.assertEqual(result["observed_default_routes"]["search.nexus.sanctum"]["upstream_port"], 8083)
        self.assertIn("omits custom locations", result["limitations"][0])

    def test_mismatch_does_not_mutate_source(self):
        proposed = make_desired()
        result = review.compare(make_report(port="8089"), proposed)
        self.assertTrue(result["review_required"])
        self.assertEqual(
            result["proposed_upstream_differences"][0]["differences"]["upstream_port"],
            {"observed": 8089, "proposed": 8083},
        )
        self.assertEqual(proposed["yxorp_routes"][0]["upstream_port"], 8083)

    def test_old_yarn_name_is_not_silently_renamed(self):
        result = review.compare(make_report(name="yarn.inner.sanctum"), make_desired())
        self.assertEqual(result["observed_not_in_proposal"], ["yarn.inner.sanctum"])
        self.assertEqual(result["proposal_not_in_observation"], ["search.nexus.sanctum"])

    def test_partial_files_are_reported_not_accepted(self):
        report = make_report()
        row = report["kvar_rootful"]["containers"][0]["proxy_routes"]["routes"][0]
        row["duplicate_fields"] = True
        result = review.compare(report, make_desired())
        self.assertTrue(result["review_required"])
        self.assertEqual(result["partial_or_unsupported_files"], ["1.conf"])
        self.assertEqual(result["observed_host_count"], 0)

    def test_unknown_rootful_identity_refused(self):
        report = make_report()
        report["kvar_rootful"]["host"] = "different.example"
        with self.assertRaises(ValueError):
            review.compare(report, make_desired())


if __name__ == "__main__":
    unittest.main()
