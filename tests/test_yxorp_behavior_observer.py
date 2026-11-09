"""Offline privacy and scope checks for Kvar's read-only NPM observer."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "tools/observe-yxorp-npm-behavior.py"
spec = importlib.util.spec_from_file_location("npmbehavior", path)
observer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)


class ObserverPrivacyTests(unittest.TestCase):
    def test_no_header_values_or_credentials_exported(self):
        raw = b"""server {
set $server "kvar.outer.sanctum";
set $port 82;
location / {
  proxy_set_header Authorization "Bearer topsecret-CREDENTIAL";
  proxy_set_header Upgrade $http_upgrade;
  proxy_pass http://user:password@backend.example/secret;
  return 302 http://secret.example/opaque;
}
}"""
        result = observer.inspect_proxy_config(raw)
        projection = json.dumps(result)
        for forbidden in ("topsecret-CREDENTIAL", "password", "secret.example",
                          "backend.example", "opaque", "Bearer"):
            self.assertNotIn(forbidden, projection)
        self.assertIn("Authorization", result["header_names_only"])
        self.assertTrue(result["websocket_header_detected"])
        self.assertIn("return", result["redirect_directive_names"])

    def test_nondefault_location_without_path_secrets(self):
        result = observer.inspect_proxy_config(
            b"location /api {\n return 200 secret;\n}\n"
            b"location ~ ^/token-very-sensitive {\n proxy_pass http://secret;\n}\n")
        self.assertEqual(result["location_count"], 2)
        self.assertEqual(result["nondefault_location_count"], 2)
        self.assertEqual(result["locations_redacted_or_unsupported"], 1)
        self.assertTrue(result["needs_manual_behavior_review"])
        self.assertNotIn("token-very-sensitive", json.dumps(result))

    def test_fixtures_restrict_proxy_directory_and_custom_snippets(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            p = base / "nginx" / "proxy_host"
            p.mkdir(parents=True)
            (p / "5.conf").write_text("server {\n location / {\n proxy_pass http://secret;\n }\n }")
            custom = base / "nginx" / "custom"
            custom.mkdir()
            (custom / "server_proxy.conf").write_text("add_header Authorization secret;")
            report = observer.inspect_data_root(base)
            self.assertEqual(report["status"], "observed")
            self.assertEqual(len(report["proxy_hosts"]), 1)
            self.assertEqual(report["proxy_hosts"][0]["file"], "5.conf")
            self.assertEqual(report["nonempty_custom_config_files"][0]["file"],
                             "server_proxy.conf")
            self.assertNotIn("add_header Authorization secret;", json.dumps(report))
            self.assertNotIn("http://secret;", json.dumps(report))

    def test_unsafe_symlink_or_unexpected_file_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            p = root / "nginx" / "proxy_host"
            p.mkdir(parents=True)
            (p / "5.conf").write_text("server {}")
            (p / "not-a-generated-host.conf").write_text("secret")
            with self.assertRaises(ValueError):
                observer.inspect_data_root(root)


if __name__ == "__main__":
    unittest.main()
