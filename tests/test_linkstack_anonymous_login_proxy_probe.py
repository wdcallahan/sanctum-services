"""Source contracts for anonymous LinkStack /login proxy-form validation."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/observe-linkstack-login-proxy-form.py"
PLAY = ROOT / "ansible/linkstack-anonymous-login-proxy-probe.yml"
spec = importlib.util.spec_from_file_location("login_probe", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SECRET = "SENSITIVE_COOKIE_AND_ADMIN_CSRF_DO_NOT_PRINT"


class AnonymousLoginProbe(unittest.TestCase):
    def test_redirects_are_sanitized_and_classified(self):
        test_cases = [
            ("", "absent", "absent", "absent"),
            ("/dashboard?token=" + SECRET, "relative", "relative", "relative"),
            ("http://dir.nexus.sanctum/login", "absolute", "frontend", "http"),
            ("https://dir.nexus.sanctum/dashboard", "absolute", "frontend", "https"),
            ("https://old.example.com/" + SECRET, "absolute", "unexpected_host", "https"),
            ("file:///etc/passwd", "unexpected", "unknown", "unknown"),
        ]
        for value, kind, host, scheme in test_cases:
            o = mod.classify_redirect(value)
            self.assertEqual((o["kind"], o["host"], o["scheme"]),
                             (kind, host, scheme))
            self.assertNotIn(SECRET, json.dumps(o))

    def test_cookie_attributes_are_finite_flags_only(self):
        cookies = [("Set-Cookie", "session=" + SECRET +
                    "; Domain=.dir.nexus.sanctum; Path=/; HttpOnly; SameSite=Lax"),
                   ("set-cookie", "csrf=" + SECRET +
                    "; Path=/; Secure; SameSite=Strict")]
        o = mod.classify_cookies(cookies)
        self.assertTrue(o["set_cookie_present"])
        self.assertTrue(o["domain_attribute_present"])
        self.assertTrue(o["domain_attributes_match_frontend"])
        self.assertTrue(o["secure_attribute_present"])
        self.assertTrue(o["http_only_attribute_present"])
        self.assertEqual(o["samesite_categories"], ["lax", "strict"])
        self.assertNotIn(SECRET, json.dumps(o))
        bad = mod.classify_cookies([("set-cookie", "auth=" + SECRET +
                                    "; Domain=unrelated.example")])
        self.assertFalse(bad["domain_attributes_match_frontend"])
        empty = mod.classify_cookies([])
        self.assertEqual(empty["domain_attributes_match_frontend"], "not_applicable")

    def test_absolute_form_is_the_only_variation_in_http_request(self):
        class FakeResponse:
            status = 200
            def getheader(self, name, default=""):
                return {"Content-Type": "text/html; charset=UTF-8",
                        "Location": ""}.get(name, default)
            def getheaders(self):
                return [("Set-Cookie", "csrf=" + SECRET + "; HttpOnly")]
            def read(self, n):
                return ("<form>private " + SECRET + "</form>").encode()
        recorded = []
        class FakeConnection:
            def __init__(self, host, port, timeout=8):
                recorded.append(("connect", host, port, timeout))
            def putrequest(self, *args, **kwargs):
                recorded.append(("request", args, kwargs))
            def putheader(self, *args):
                recorded.append(("header", args))
            def endheaders(self):
                recorded.append(("send",))
            def getresponse(self):
                return FakeResponse()
            def close(self):
                recorded.append(("close",))
        with patch.object(mod.http.client, "HTTPConnection", FakeConnection):
            d = mod.request("127.0.0.1", 18081)
            a = mod.request("127.0.0.1", 18081, absolute_form=True)
        self.assertTrue(mod.compatible(d, a))
        reqs = [x for x in recorded if x[0] == "request"]
        self.assertEqual(len(reqs), 2)
        self.assertEqual(reqs[0][1][1], "/login")
        self.assertEqual(reqs[1][1][1], "http://dir.nexus.sanctum/login")
        self.assertTrue(all(x[2].get("skip_host") for x in reqs))
        self.assertEqual(sum(x == ("header", ("Host", "dir.nexus.sanctum"))
                             for x in recorded), 2)
        self.assertNotIn(SECRET, json.dumps(d) + json.dumps(a))

    def test_synthetic_four_case_parity_and_no_authentication_claim(self):
        called = []
        def get(host, port, absolute_form=False):
            called.append((host, port, absolute_form))
            return {
                "outcome": "http", "status": 200, "mime_class": "html",
                "redirect": mod.classify_redirect(""),
                "cookie_policy": mod.classify_cookies([]),
                "body_complete_within_bound": True,
            }
        report = mod.observe(get)
        self.assertEqual(len(called), 4)
        self.assertEqual(called, [
            ("kvar.outer.sanctum", 8081, False),
            ("kvar.outer.sanctum", 80, False),
            ("127.0.0.1", 18081, False),
            ("127.0.0.1", 18081, True),
        ])
        self.assertTrue(report["candidate_proxy_request_compatible"])
        self.assertTrue(report["login_status_equal_to_kvar_npm"])
        for key in (
            "raw_urls_headers_cookies_or_html_returned",
            "password_or_form_submitted", "authenticated_admin_accepted",
            "real_named_firefox_session_accepted",
            "firefox_proxy_or_ssh_tunnel_created",
            "production_service_or_dns_modified",
        ):
            self.assertFalse(report[key])

    def test_absolute_form_failure_is_never_misclassified_as_working(self):
        normal = {
            "outcome": "http", "status": 200, "mime_class": "html",
            "redirect": mod.classify_redirect(""),
            "cookie_policy": mod.classify_cookies([]),
            "body_complete_within_bound": True,
        }
        proxy = dict(normal, status=400)
        self.assertFalse(mod.compatible(normal, proxy))
        proxy = dict(normal, redirect=mod.classify_redirect("https://old.example/"))
        self.assertFalse(mod.compatible(normal, proxy))
        proxy = dict(normal, body_complete_within_bound=False)
        self.assertFalse(mod.compatible(normal, proxy))

    def test_strict_kvin_and_loopback_guards_with_sanitized_probe(self):
        plays = yaml.safe_load(PLAY.read_text())
        self.assertEqual(len(plays), 1)
        play = plays[0]
        self.assertEqual(play["hosts"], "kuma")
        self.assertFalse(play["become"])
        self.assertTrue(play["gather_facts"])
        tasks = play["tasks"]
        criteria = str(tasks[0]["ansible.builtin.assert"]["that"])
        for phrase in ("'kvin.outer.sanctum'", "'aarch64'", "'wdc2'",
                       "sanctum_linkstack_anonymous_login_probe_approved",
                       "not ansible_check_mode", "sanctum_linkstack_cutover_approved"):
            self.assertIn(phrase, criteria)
        required = str(tasks[2]["ansible.builtin.assert"]["that"])
        for phrase in ("State.Running", "Mounts",
                       "sanctum-linkstack-qualified-20261112t105926",
                       "53b38579d3768c94c9904593b759aa8c1864cf88ebc435ee264290bd59676c65"):
            self.assertIn(phrase, required)
        self.assertIn("127.0.0.1:18081", str(tasks[4]))
        check = tasks[5]
        self.assertTrue(check["no_log"])
        self.assertFalse(check["changed_when"])
        self.assertIn("observe-linkstack-login-proxy-form.py",
                      check["ansible.builtin.command"]["argv"][2])
        self.assertEqual(tasks[-1]["ansible.builtin.debug"]["msg"],
                         "{{ linkstack_login_wire.stdout | from_json }}")
        yaml_text = PLAY.read_text()
        for forbidden in ("ansible.builtin.systemd_service",
                          "ansible.builtin.copy:", "ansible.builtin.template:",
                          "ansible.builtin.uri:", "firewall-cmd",
                          "podman volume rm", "scp", "podman pull",
                          "ansible.posix.sysctl"):
            self.assertNotIn(forbidden, yaml_text)
        wf = (ROOT / ".github/workflows/yxorp-source-check.yml").read_text()
        self.assertIn("test_linkstack_anonymous_login_proxy_probe.py", wf)
        self.assertIn("ansible/linkstack-anonymous-login-proxy-probe.yml --syntax-check", wf)


if __name__ == "__main__":
    unittest.main()
