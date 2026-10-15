# SchemaBounce agent kit

One source of SchemaBounce's working rules for coding agents: Claude Code on a
developer's machine, OpenAI Codex and other agents, and SchemaBounce's hosted
Code Mode sessions.

The first part is **decision records**. SchemaBounce records its rulings
(architecture, pricing, security, product) as `dec-NNN` records. This kit
helps an agent find the rulings that govern the change in front of it, cite
them, stop when a change contradicts one, and propose new ones without
ratifying them.

Status: **version 0.3.0**. The decisions skill works with today's hosted
SchemaBounce MCP tools. The pre-edit hook asks the MCP which decisions govern
the file being changed; it returns decisions once SchemaBounce has classified
them by repository path, and nothing before that. Code Mode loading is
described in [docs/DESIGN.md](docs/DESIGN.md).

## Install in Claude Code

Add the SchemaBounce marketplace once, then install the plugin:

```
/plugin marketplace add SchemaBounce/claude-plugins
/plugin install schemabounce@schemabounce
```

Then sign in to the SchemaBounce MCP with `/mcp`.

The marketplace at [SchemaBounce/claude-plugins](https://github.com/SchemaBounce/claude-plugins)
pins a release tag of this repository, so an install is a reviewed release.
This repository is also its own marketplace (`schemabounce@schemabounce-agent-kit`),
which tracks the development branch; use it only to work on the kit.

### Enable for everyone in a repository

Check this into the repository's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "schemabounce": {
      "source": { "source": "github", "repo": "SchemaBounce/claude-plugins" }
    }
  },
  "enabledPlugins": {
    "schemabounce@schemabounce": true
  }
}
```

Then render the kit's decisions text into the repository's instruction file
and keep the check in the repository's pre-commit hook, so the text is never
typed in by hand and a commit that drops or edits it fails:

```
python3 scripts/agents_md.py render /path/to/repo/AGENTS.md
python3 scripts/agents_md.py check /path/to/repo/AGENTS.md
python3 scripts/agents_md.py check-settings /path/to/repo/.claude/settings.json
```

`render` writes [templates/AGENTS.decisions.md](templates/AGENTS.decisions.md)
between two marker comments that record the kit version and a hash;
`--before "## Some heading"` places a new block above that heading. A
repository that has no kit checkout beside it keeps a copy of the script as
`scripts/check-agent-kit.py` for the two `check` commands. When a file is
generated from another (a Codex mirror from `CLAUDE.md`), render into the
source and regenerate the mirror.

## Codex and other agents

Render [templates/AGENTS.decisions.md](templates/AGENTS.decisions.md) into the
repository's `AGENTS.md` with the script above, copy
`skills/schemabounce-decisions/` into the directory your agent reads skills
from, and add the hosted MCP (`https://mcp.schemabounce.com/mcp`) to the
agent's MCP configuration.

## Hosted Code Mode

SchemaBounce loads this kit, pinned to a release, into every hosted code
session, and adds the decisions that apply to the repository to the session's
starting context. See [docs/DESIGN.md](docs/DESIGN.md), "Where it runs".

## Where each part loads

| Part | Claude Code | Cowork | claude.ai chat |
|---|---|---|---|
| Skill `schemabounce-decisions` | Loads | Loads | Loads |
| Pre-edit hook | Loads | Loads | Not loaded (chat has no hooks) |
| Hosted SchemaBounce MCP | Loads | Connect it from the plugin's Connectors tab | Connect it from the plugin's Connectors tab |

## What this plugin runs, sends and fetches

- **Runs:** nothing on your machine by itself. The hook is an MCP tool call,
  not a command. `scripts/agents_md.py` runs only when you run it.
- **Sends:** before each Edit, Write or MultiEdit in Claude Code or Cowork,
  the hook calls `sb_decision` (action `context`) on
  `https://mcp.schemabounce.com/mcp` with your session's working directory
  and the absolute path of the file being edited. The server uses the
  directory names to work out which repository you are in and which decisions
  apply; it does not store or log the absolute path. The reply is text added
  to the model's context. Nothing else is sent, and there is no telemetry.
- **Fetches:** nothing. No downloads, no package installs.
- **Signed out or unreachable:** the edit goes ahead with no decision
  context. The hook never blocks an edit.
- **Access:** the MCP server needs each person's own SchemaBounce sign-in and
  returns only what that person may read.

## What is inside

| Path | What it is |
|---|---|
| `.claude-plugin/` | Plugin manifest and this repository's own (development) marketplace entry |
| `hooks/hooks.json` | Before an edit, asks the MCP which decisions govern the file (see DESIGN.md, "The edit hook") |
| `.mcp.json` | The hosted SchemaBounce MCP |
| `skills/schemabounce-decisions/` | When and how to use decisions (Agent Skills format) |
| `templates/` | Text other agents' instruction files include |
| `scripts/agents_md.py` | Renders `templates/` into a repository's instruction file and checks it stayed intact |
| `docs/DESIGN.md` | Just-in-time decision retrieval, consolidation, and where the kit runs |
| `LICENSE` | Apache-2.0 |

## Releases

A release is a version bump in `.claude-plugin/plugin.json` and the
marketplace entry, an immutable tag `schemabounce--v<version>`, and a GitHub
release with two `git archive` assets of this folder under one top-level
directory, each with its sha256: a `.tar.gz`, which hosted Code Mode pins and
verifies before it extracts, and a `.zip` for people. The SchemaBounce
marketplace points at the tag. To update:
`claude plugin update schemabounce@schemabounce`.

## Security

This repository is public. It contains instructions and configuration only:
no credentials, no customer data. Access to decision records goes through
the hosted SchemaBounce MCP with each person's own sign-in.

## License

Apache-2.0. See [LICENSE](LICENSE).
