# SchemaBounce agent kit

One source of SchemaBounce's working rules for coding agents: Claude Code on a
developer's machine, OpenAI Codex and other agents, and SchemaBounce's hosted
Code Mode sessions.

The first part is **decision records**. SchemaBounce records its rulings
(architecture, pricing, security, product) as `dec-NNN` records. This kit
helps an agent find the rulings that govern the change in front of it, cite
them, stop when a change contradicts one, and propose new ones without
ratifying them.

Status: **version 0.2.1**. The decisions skill works with today's hosted
SchemaBounce MCP tools. The just-in-time retrieval, hooks and Code Mode
loading described in [docs/DESIGN.md](docs/DESIGN.md) come in later phases.

## Install in Claude Code

```
/plugin marketplace add SchemaBounce/schemabounce-agent-kit
/plugin install schemabounce@schemabounce-agent-kit
```

Then sign in to the SchemaBounce MCP with `/mcp`.

To enable it for everyone working in a repository, check this into the
repository's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "schemabounce-agent-kit": {
      "source": { "source": "github", "repo": "SchemaBounce/schemabounce-agent-kit" }
    }
  },
  "enabledPlugins": {
    "schemabounce@schemabounce-agent-kit": true
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

Planned for phase 2: SchemaBounce loads this kit, pinned to a release, into
every hosted code session, and adds the decisions that apply to the
repository to the session's starting context.

## What is inside

| Path | What it is |
|---|---|
| `.claude-plugin/` | Plugin manifest and the marketplace entry |
| `hooks/hooks.json` | Before an edit, asks the MCP which decisions govern the file (see DESIGN.md, "The edit hook") |
| `.mcp.json` | The hosted SchemaBounce MCP |
| `skills/schemabounce-decisions/` | When and how to use decisions (Agent Skills format) |
| `templates/` | Text other agents' instruction files include |
| `scripts/agents_md.py` | Renders `templates/` into a repository's instruction file and checks it stayed intact |
| `docs/DESIGN.md` | Just-in-time decision retrieval, consolidation, and where the kit runs |

## Security

This repository is public. It contains instructions and configuration only:
no credentials, no customer data. Access to decision records goes through
the hosted SchemaBounce MCP with each person's own sign-in.
