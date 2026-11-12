"""Non-invasive recovered LinkStack anonymous browser page and asset parity."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/observe-linkstack-recovered-browser-surface.py"
PLAYBOOK = ROOT / "ansible/linkstack-recovered-public-surface.yml"
spec = importlib.util.spec_from_file_location("browser_surface", SCRIPT)
observer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)
SECRET = "PRIVATE_DASHBOARD_SECRET_SHOULD_NOT_APPEAR"


def response(content=b"", status=200, mime="html", location=""):
    return {"outcome": "http", "status": status, "media": mime,
            "content": content, "complete": True, "location": location}


class LinkStackBrowserSurface(unittest.TestCase):
    def test_strict_no_external_urls_queries_tokens_or_admin_pages_discovery_by_guess(self):
        allowed = ("/css/app.css", "css/app.css", "/js/site.js",
                   "http://dir.nexus.sanctum/css/a.css")
        for value in allowed:
            self.assertIsNotNone(observer.safe_path(value), value)
        denied = ("https://outside.org/x.css", "//outside.org/x.js",
                  "http://dir.nexus.sanctum:1234/x.js",
                  "https://dir.nexus.sanctum/x.js",
                  "/admin?token=" + SECRET, "/static/a.css?session=" + SECRET,
                  "/a/../private", "/a/%2e%2e/b", "/file%2Fsecret",
                  "/file#secret", "javascript:alert(1)", "/x\r\nHost:evil",
                  "\\\\evil.example\\private", "")
        for value in denied:
            self.assertIsNone(observer.safe_path(value), value)

    def test_html_parser_only_selects_same_site_css_js_and_discovered_login(self):
        payload = ("""
<html><title>""" + SECRET + """</title><head>
<link rel="stylesheet" href="/assets/app.css">
<link rel="stylesheet" href="https://external.example/tracking.css">
<script src="http://dir.nexus.sanctum/assets/app.js"></script>
<script src="/private.js?token=""" + SECRET + """"></script>
</head><body><a href="/login">Log in</a><a href="/target">Target</a>
</body></html>""").encode()
        r = observer.parse_public_root(response(payload))
        self.assertEqual(r.anchors, 2)
        self.assertEqual(r.assets["css"], {"/assets/app.css"})
        self.assertEqual(r.assets["javascript"], {"/assets/app.js"})
        self.assertEqual(r.logins, {"/login"})
        self.assertNotIn(SECRET, str(r.assets) + str(r.logins))

    def test_only_common_public_assets_and_explicit_login_gets(self):
        page = ("""
<html><head><link rel="stylesheet" href="/assets/public.css">
<script src="/assets/public.js"></script></head>
<body><a href="/login">Login</a><a href="https://example.com">Other</a>
<p>""" + SECRET + """</p></body></html>""").encode()
        calls = []
        def get(host, port, path):
            calls.append((host, port, path))
            if path == "/":
                # Non-secret differences in the old/current page are private.
                return response(page + (b" " if port == 18081 else b""))
            if path == "/login":
                return response(b"Private CSRF " + SECRET.encode(), 200)
            if path.endswith(".css"):
                return response(b"body { color: red } " + SECRET.encode(), 200, "css")
            if path.endswith(".js"):
                return response(b"var private = " + SECRET.encode(), 200, "javascript")
            self.fail("Unexpected GET " + repr(path))
        result = observer.observe(get)
        self.assertEqual(result["schema"], "sanctum-linkstack-anonymous-browser-surface/v1")
        self.assertEqual(result["root"]["kvin_recovered"]["status"], 200)
        self.assertTrue(result["public_html_parsed"])
        self.assertFalse(result["public_directory_exact_body_equal"])
        self.assertEqual(result["public_links"]["recovered_anchor_count"], 2)
        self.assertEqual(result["login_surface"]["status"], "anonymous_get_observed")
        self.assertEqual(result["login_surface"]["responses"]["kvin_recovered"]["status"], 200)
        self.assertFalse(result["login_surface"]["path_disclosed"])
        self.assertEqual(result["public_assets"]["css"]["shared_count"], 1)
        self.assertEqual(result["public_assets"]["javascript"]["shared_count"], 1)
        self.assertEqual(len(calls), 12)  # 3 origins x (root + CSS + JS + login)
        self.assertEqual({x[2] for x in calls},
                         {"/", "/assets/public.css", "/assets/public.js", "/login"})
        self.assertNotIn(SECRET, json.dumps(result))
        self.assertNotIn("/assets/public.css", json.dumps(result))
        self.assertNotIn("/login", json.dumps(result))
        for key in ("application_data_or_credentials_exposed",
                    "authenticated_admin_accepted",
                    "real_named_browser_session_accepted",
                    "production_route_switched",
                    "configuration_changed"):
            self.assertFalse(result[key])

    def test_missing_or_oversized_page_degrades_without_asset_followups(self):
        calls = []
        def get(host, port, path):
            calls.append((host, port, path))
            if port == 18081:
                return {"outcome": "http", "status": 200, "media": "html",
                        "content": None, "complete": False, "location": ""}
            return response(b"<a href='/login'>login</a>")
        report = observer.observe(get)
        self.assertEqual(len(calls), 3)
        self.assertEqual(report["root_origin_to_recovered"]["body_equal"], "not_comparable")
        self.assertFalse(report["public_html_parsed"])
        self.assertEqual(report["login_surface"]["status"], "not_discovered_on_both")

    def test_redirect_values_not_exposed_even_when_different(self):
        left = response(b"", 302, "html", "http://kvar.outer.sanctum/secret?" + SECRET)
        right = response(b"", 302, "html", "http://dir.nexus.sanctum/login")
        compared = observer.compare(left, right)
        self.assertFalse(compared["redirect_equal"])
        self.assertNotIn(SECRET, json.dumps(compared))
        self.assertNotIn("dir.nexus", json.dumps(compared))

    def test_ansible_guards_unchanged_pinned_candidate_and_no_web_session_claim(self):
        plays = yaml.safe_load(PLAYBOOK.read_text())
        self.assertEqual(len(plays), 1)
        play = plays[0]
        self.assertEqual(play["hosts"], "kuma")
        self.assertFalse(play["become"])
        self.assertTrue(play["gather_facts"])
        tasks = play["tasks"]
        conditions = str(tasks[0]["ansible.builtin.assert"]["that"])
        for token in ("inventory_hostname == 'kvin.outer.sanctum'",
                      "ansible_facts['architecture'] == 'aarch64'",
                      "sanctum_linkstack_anonymous_surface_observe_approved",
                      "not ansible_check_mode", "sanctum_linkstack_cutover_approved"):
            self.assertIn(token, conditions)
        check = str(tasks[2]["ansible.builtin.assert"]["that"])
        for token in ("State.Running", "Mounts", "sanctum-linkstack-qualified-20261112t105926",
                      "53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65"):
            self.assertIn(token, check)
        self.assertIn("127.0.0.1:18081", str(tasks[4]))
        probe = tasks[5]
        self.assertTrue(probe["no_log"])
        self.assertFalse(probe["changed_when"])
        self.assertIn("observe-linkstack-recovered-browser-surface.py",
                      probe["ansible.builtin.command"]["argv"][2])
        expected = tasks[-1]["ansible.builtin.debug"]["msg"]
        self.assertEqual(expected, "{{ linkstack_browser_surface.stdout | from_json }}")
        text = PLAYBOOK.read_text()
        for forbidden in ("ansible.builtin.systemd_service",
                          "ansible.builtin.template", "ansible.builtin.copy:",
                          "ansible.builtin.uri:", "podman volume rm",
                          "firewall-cmd", "podman pull", "scp"):
            self.assertNotIn(forbidden, text)
        workflow = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_linkstack_recovered_public_surface.py", workflow)
        self.assertIn("ansible/linkstack-recovered-public-surface.yml --syntax-check", workflow)


if __name__ == "__main__":
    unittest.main()
