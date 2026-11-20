#!/bin/sh
# headersHelper for the plugin's hosted SchemaBounce MCP server.
#
# Claude Code runs this before it connects to the server and again after a
# tool call returns 401 or 403. It prints a JSON object of HTTP headers.
#
# - No credentials file: prints {} and exits 0. Claude Code then signs in with
#   browser OAuth exactly as before, so nothing changes for people who use it.
# - ~/.config/schemabounce/credentials.json present: exchanges it for an
#   access token and prints {"Authorization": "Bearer ..."}. Claude Code skips
#   browser OAuth for the server. This is the path for SSH sessions and
#   headless machines, where the OAuth callback on localhost cannot be reached.
#
# The file is read from a fixed path, not an environment variable, because
# Claude Code strips credential-named variables from a plugin server's
# environment.
f="${HOME}/.config/schemabounce/credentials.json"
if [ ! -f "$f" ]; then
  printf '{}\n'
  exit 0
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "schemabounce: python3 is needed to read $f (remove the file to use browser sign-in)" >&2
  exit 1
fi
exec python3 -I "$(dirname "$0")/mcp_headers.py" "$f"
