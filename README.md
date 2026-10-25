# SchemaBounce agent kit

One source of SchemaBounce's working rules for agents: Claude Code on a
developer's machine, OpenAI Codex and other agents, SchemaBounce's hosted
Code Mode sessions, and the agents that run on SchemaBounce itself.

The kit carries **one skill, `schemabounce`**, in the open Agent Skills
format: the manual for the whole platform. Its `SKILL.md` is a short index;
each area (agents and tasks, records and memory, files, workflows, pipelines,
approvals and secrets, code sessions, goals, decisions, billing, the hosted
MCP, administration) is a file under `references/` that an agent loads only
when it works in that area. Install it anywhere skills load:

```
npx skills add SchemaBounce/schemabounce-agent-kit
```

Agents running on SchemaBounce get it from this repository automatically
(decision dec-202). Two parts of it matter most to coding agents.

The first part is **decision records**. SchemaBounce records its rulings
(architecture, pricing, security, product) as `dec-NNN` records. This kit
helps an agent find the rulings that govern the change in front of it, cite
them, stop when a change contradicts one, and propose new ones without
ratifying them.

The second part is **goals and outcome metrics**. It teaches an agent that a
SchemaBounce goal moves only through key results on declared outcome metrics
and tasks linked to it, how to declare, capture and attach a metric through
the MCP, and to read the goal back before saying a number shows anywhere.

Development status: **version 0.5.0**. The public catalog remains on 0.4.2
until this version is released. Version 0.5.0 folds the separate decisions
and goals skills into the one `schemabounce` skill. The decision guidance
works with today's hosted SchemaBounce MCP tools. The pre-edit hook asks the MCP which decisions govern
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

No GitHub SSH key is needed: the marketplace entry points at this repository
by HTTPS URL. On a machine without an SSH key, add the marketplace by URL too:
`claude plugin marketplace add https://github.com/SchemaBounce/claude-plugins.git`.

The marketplace at [SchemaBounce/claude-plugins](https://github.com/SchemaBounce/claude-plugins)
pins a release tag of this repository, so an install is a reviewed release.
This repository is also its own marketplace (`schemabounce@schemabounce-agent-kit`),
which tracks the default branch, `main` (the released state). To work on the
kit, add your local checkout as a marketplace instead:
`/plugin marketplace add /path/to/schemabounce-agent-kit`.

### Enable for everyone in a repository

Check this into the repository's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "schemabounce": {
      "source": { "source": "github", "repo": "SchemaBounce/claude-plugins" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "schemabounce@schemabounce": true
  }
}
```

`autoUpdate: true` makes Claude Code refresh the marketplace after the first
message of a session and fetch a new release in the background; the new version
loads on the next launch, or right away with `/reload-plugins`.

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

The checked-in settings register the marketplace for everyone who trusts the
folder. Because the entry points at the plugin's own repository, each
contributor installs it once per machine, which Claude Code also prompts for:

```
claude plugin install schemabounce@schemabounce --scope project
```

Then sign in to the SchemaBounce MCP once with `/mcp`. Hosted and cloud
sessions never load a repository's plugins; SchemaBounce's hosted Code Mode
loads the kit from a platform pin instead.

## Install in Codex

After the `schemabounce--v0.5.0` release is published, add the SchemaBounce
Codex marketplace and install its pinned release:

```
codex plugin marketplace add SchemaBounce/claude-plugins
codex plugin add schemabounce@schemabounce
```

Sign in to the hosted SchemaBounce MCP when Codex prompts you. The plugin
includes both Agent Skills and an OAuth-configured connection to
`https://mcp.schemabounce.com/mcp`; it never contains your credentials. Codex
does not run the Claude-only pre-edit hook. The skill's decisions guidance calls
`sb_decision` with the repository and paths before a governed change.

For kit development, add this checkout as a local marketplace with
`codex plugin marketplace add /path/to/schemabounce-agent-kit` and install
`schemabounce@schemabounce-agent-kit`. This local entry tracks your checkout;
the public marketplace pins a release tag.

To make the kit's decision rules persistent in a repository, render
[templates/AGENTS.decisions.md](templates/AGENTS.decisions.md) into its
`AGENTS.md` with the script above. Other agents can still copy
`skills/schemabounce/` and configure the hosted MCP manually.

## Hosted Code Mode

SchemaBounce loads this kit, pinned to a release, into every hosted code
session, and adds the decisions that apply to the repository to the session's
starting context. See [docs/DESIGN.md](docs/DESIGN.md), "Where it runs".

## Code sessions started from Linear

A workspace admin can let the SchemaBounce Linear app start code sessions from
Linear issues. If you work in such a workspace through the hosted MCP
(`sb_code_session`), you will see them in the session list:

- **Recognise them.** The branch is `sb-code/<issue id>-<session>` (for
  example `sb-code/eng-123-4f9a`), and the approval card in the Inbox reads
  "Requested from Linear, issue ENG-123".
- **Whose plan pays.** The platform matches the Linear requester to a workspace
  member by verified email. A match runs on that member's own coding plan and
  only that member approves. With no match, the session waits on a hold that
  states its cost, and a person approves it in the Inbox.
- **Approvals stay in SchemaBounce.** Nothing in Linear text approves a start,
  a continue or a push. Do not try to approve for someone else through the MCP:
  `approvals_respond` decides only as the signed-in person, after the typed
  confirmation.
- **Repository.** The repository comes from the Linear team's mapping. A
  session for that issue cannot target another one.
- **Stop.** Only the person who started the work can stop it from Linear.
  The session can also be cancelled in SchemaBounce.
- **Continue.** A session started from an issue can be continued from that same
  issue only. Continue it from the MCP with `sb_code_session` `continue`.

Public overview: <https://schemabounce.com/linear-app>.

## Where each part loads

| Part | Claude Code | Codex | Cowork | claude.ai chat |
|---|---|---|---|---|
| Skill `schemabounce` | Loads | Loads | Loads | Loads |
| Pre-edit hook | Loads | Not loaded | Loads | Not loaded (chat has no hooks) |
| Hosted SchemaBounce MCP | Loads | Connect with OAuth | Connect it from the plugin's Connectors tab | Connect it from the plugin's Connectors tab |

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
- **Platforms:** any system Claude Code runs on. `scripts/agents_md.py` is
  optional and needs Python 3, nothing else.

## What is inside

| Path | What it is |
|---|---|
| `.claude-plugin/` | Plugin manifest and this repository's own (development) marketplace entry |
| `plugin.json` | Portable plugin manifest for Codex and other Agent Plugins hosts; explicitly disables Claude hook discovery in Codex |
| `mcp.json` | Portable hosted MCP connection with OAuth client registration |
| `.agents/plugins/marketplace.json` | Codex development marketplace for this checkout |
| `hooks/hooks.json` | Before an edit, asks the MCP which decisions govern the file (see DESIGN.md, "The edit hook") |
| `.mcp.json` | The hosted SchemaBounce MCP |
| `skills/schemabounce/` | The one SchemaBounce skill (Agent Skills format): `SKILL.md` index plus `references/` per area, including decisions (`references/decisions*.md`) and goals (`references/goals*.md`) |
| `templates/` | Text other agents' instruction files include. `AGENTS.goals.md` is the goals rules for agents that do not load skills; `scripts/agents_md.py` renders only the decisions text today |
| `scripts/agents_md.py` | Renders `templates/` into a repository's instruction file and checks it stayed intact |
| `docs/DESIGN.md` | Just-in-time decision retrieval, consolidation, and where the kit runs |
| `LICENSE` | Apache-2.0 |

## Releases

A release is a version bump in `.claude-plugin/plugin.json` and the
marketplace entry, an immutable tag `schemabounce--v<version>`, and a GitHub
release with two `git archive` assets of this folder under one top-level
directory, each with its sha256: a `.tar.gz`, which hosted Code Mode pins and
verifies before it extracts, and a `.zip` for people. The SchemaBounce
marketplace points at the tag, and `main` holds the released state: a person
merges `development` into `main` at each release (a pull request from
`development` to `main`, which GitHub titles "Development" since `main` is the
default branch), so `main` and the newest tag
match. To update: `claude plugin update schemabounce@schemabounce`.

## Security

This repository is public. It contains instructions and configuration only:
no credentials, no customer data. Access to decision records goes through
the hosted SchemaBounce MCP with each person's own sign-in.

## License

Apache-2.0. See [LICENSE](LICENSE).
