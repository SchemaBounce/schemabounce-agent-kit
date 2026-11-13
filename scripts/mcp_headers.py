"""Exchange a SchemaBounce credentials file for an MCP Authorization header.

Called by mcp-headers.sh only when the credentials file exists. The file is a
JSON object:

    {
      "SCHEMABOUNCE_CLIENT_ID": "pat_... or sa_...",
      "SCHEMABOUNCE_CLIENT_SECRET": "...",
      "SCHEMABOUNCE_API_URL": "https://api.schemabounce.com"
    }

SCHEMABOUNCE_API_URL is optional. The plugin's server is the production
hosted MCP, so any other value is refused: a token from another platform
would be rejected by it anyway, and refusing first keeps a local test
credential from being sent to production.

Prints {"Authorization": "Bearer <token>"} on success. On failure, prints one
line to stderr naming the file and the HTTP status, never the credential, and
exits 1.
"""
import base64
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

API_URL = "https://api.schemabounce.com"


def fail(msg):
    sys.stderr.write("schemabounce: " + msg + "\n")
    sys.exit(1)


def main(path):
    try:
        with open(path) as fh:
            creds = json.load(fh)
    except (OSError, ValueError) as err:
        fail(f"cannot read {path}: {err.__class__.__name__}")
    if not isinstance(creds, dict):
        fail(f"{path} must hold a JSON object")
    client_id = creds.get("SCHEMABOUNCE_CLIENT_ID") or ""
    secret = creds.get("SCHEMABOUNCE_CLIENT_SECRET") or ""
    if not client_id or not secret:
        fail(f"{path} needs SCHEMABOUNCE_CLIENT_ID and SCHEMABOUNCE_CLIENT_SECRET")
    api = (creds.get("SCHEMABOUNCE_API_URL") or API_URL).rstrip("/")
    if api != API_URL:
        fail(f"{path} points at {api}; this server only accepts {API_URL}")

    basic = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
    req = urllib.request.Request(
        API_URL + "/api/v1/oauth/token",
        data=urllib.parse.urlencode({"grant_type": "client_credentials"}).encode(),
        headers={
            "Authorization": "Basic " + basic,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            # The default Python-urllib User-Agent is refused at the edge.
            "User-Agent": "schemabounce-agent-kit-mcp-headers",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            token = json.load(resp).get("access_token")
    except urllib.error.HTTPError as err:
        fail(f"token exchange for {path} returned HTTP {err.code}")
    except (urllib.error.URLError, OSError, ValueError) as err:
        fail(f"token exchange for {path} failed: {err.__class__.__name__}")
    if not token:
        fail(f"token exchange for {path} returned no access_token")
    print(json.dumps({"Authorization": "Bearer " + token}))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        fail("usage: mcp_headers.py <credentials.json>")
    main(sys.argv[1])
