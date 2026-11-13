"""Offline tests for scripts/mcp-headers.sh (no network, no real credentials).

Run: python3 -m unittest scripts/test_mcp_headers.py
"""
import json
import os
import subprocess
import tempfile
import unittest

HELPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp-headers.sh")


class McpHeadersTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.TemporaryDirectory()
        self.addCleanup(self.home.cleanup)
        self.creds = os.path.join(self.home.name, ".config", "schemabounce", "credentials.json")

    def run_helper(self):
        env = {"HOME": self.home.name, "PATH": os.environ.get("PATH", "/usr/bin:/bin")}
        return subprocess.run(["sh", HELPER], env=env, capture_output=True, text=True, timeout=20)

    def write(self, text):
        os.makedirs(os.path.dirname(self.creds), exist_ok=True)
        with open(self.creds, "w") as fh:
            fh.write(text)

    def test_no_file_prints_empty_headers_so_oauth_is_used(self):
        r = self.run_helper()
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {})

    def test_other_api_url_is_refused_before_any_request(self):
        self.write(json.dumps({"SCHEMABOUNCE_CLIENT_ID": "sa_x", "SCHEMABOUNCE_CLIENT_SECRET": "s3cret",
                               "SCHEMABOUNCE_API_URL": "http://localhost:8080"}))
        r = self.run_helper()
        self.assertEqual(r.returncode, 1)
        self.assertIn("only accepts https://api.schemabounce.com", r.stderr)
        self.assertEqual(r.stdout, "")

    def test_missing_secret_is_refused(self):
        self.write(json.dumps({"SCHEMABOUNCE_CLIENT_ID": "pat_x"}))
        r = self.run_helper()
        self.assertEqual(r.returncode, 1)
        self.assertIn("needs SCHEMABOUNCE_CLIENT_ID and SCHEMABOUNCE_CLIENT_SECRET", r.stderr)

    def test_unreadable_json_is_refused(self):
        self.write("not json")
        r = self.run_helper()
        self.assertEqual(r.returncode, 1)
        self.assertIn("cannot read", r.stderr)

    def test_errors_never_echo_the_secret(self):
        self.write(json.dumps({"SCHEMABOUNCE_CLIENT_ID": "sa_x", "SCHEMABOUNCE_CLIENT_SECRET": "s3cret",
                               "SCHEMABOUNCE_API_URL": "https://example.invalid"}))
        r = self.run_helper()
        self.assertNotIn("s3cret", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
