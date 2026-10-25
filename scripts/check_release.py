#!/usr/bin/env python3
"""Release checks for the agent kit, beyond the Agent Skills spec itself.

The spec (frontmatter keys, name, lengths) is checked by the official
validator, `agentskills validate` from skills-ref. This covers what the spec
does not:

1. The version being released matches every manifest that carries one.
2. Every `references/<x>.md` the skill links exists, and every file in
   references/ is linked from SKILL.md (no orphan, no dead link).
3. No em dash anywhere in the skill (house writing rule).
4. No vendor MCP tool name (`server__tool`) in the skill text: the skill names
   only platform tools; the `<server>__<tool>` placeholder is allowed.
5. The Codex package files a release must carry exist.

Usage: python3 scripts/check_release.py <version>
Exits 1 with one line per problem. Standard library only.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "schemabounce"
REF_LINK = re.compile(r"references/[a-z0-9-]+\.md")
VENDOR_TOOL = re.compile(r"\b[a-z0-9][a-z0-9-]*__[a-z][a-z0-9_]*\b")
FILTER_SUFFIX = re.compile(r"__(gte|lte|gt|lt|in)$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$")


def manifest_versions():
    out = {}
    for rel in (".claude-plugin/plugin.json", "plugin.json"):
        out[rel] = json.loads((ROOT / rel).read_text())["version"]
    market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    for p in market.get("plugins", []):
        if p.get("name") == "schemabounce":
            out[".claude-plugin/marketplace.json"] = p.get("version")
    return out


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    version = argv[1].strip()
    problems = []

    if not SEMVER.match(version):
        problems.append(f"version {version!r} is not semver (1.2.3)")
    for path, v in manifest_versions().items():
        if v != version:
            problems.append(f"{path} says version {v!r}, releasing {version!r}")

    texts = {p: p.read_text() for p in SKILL.rglob("*.md")}
    linked = set()
    for path, text in texts.items():
        for link in REF_LINK.findall(text):
            linked.add(link)
            if not (SKILL / link).is_file():
                problems.append(f"{path.relative_to(ROOT)} links {link}, which does not exist")
    index = texts.get(SKILL / "SKILL.md", "")
    for ref in sorted((SKILL / "references").glob("*.md")):
        rel = f"references/{ref.name}"
        if rel not in index:
            problems.append(f"{rel} is not linked from SKILL.md")

    for path, text in texts.items():
        for n, line in enumerate(text.splitlines(), 1):
            where = f"{path.relative_to(ROOT)}:{n}"
            if "—" in line:
                problems.append(f"{where} has an em dash")
            for name in VENDOR_TOOL.findall(line):
                # field__gte etc. is the record filter syntax, not a tool.
                if name != "server__tool" and not FILTER_SUFFIX.search(name):
                    problems.append(f"{where} names a vendor tool {name!r}")

    for rel in ("plugin.json", "mcp.json", ".claude-plugin/plugin.json"):
        if not (ROOT / rel).is_file():
            problems.append(f"{rel} is missing (the release must carry it)")

    for p in problems:
        print(f"FAIL {p}")
    if not problems:
        print(f"OK schemabounce {version}: versions agree, {len(linked)} reference links resolve, no em dash, no vendor tool")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
