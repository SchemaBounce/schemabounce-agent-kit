# SchemaBounce agent kit: design

Status: governed by dec-125, accepted 2026-10-14 21:06Z by the founder (see
"Decision" below). The record is the authority; read it before relying on this.

## What this is for

SchemaBounce records its rulings (architecture, pricing, security, product) as
decision records in the Context Engine (dec-001). Every agent that writes code
for SchemaBounce or for a customer should apply the rulings that bear on the
change in front of it, cite them, and propose new ones instead of coding
around them. Today that depends on each agent reading prose instructions and
running broad searches. It is inconsistent across repos, across Claude Code,
Codex and hosted Code Mode sessions, and it will not survive a corpus of
thousands of decisions.

This kit gives every agent the same behaviour from one source:

- the right decisions arrive **just in time**, scoped to the files and topics
  being changed, inside a fixed context budget;
- only **current authority** comes back: superseded and rejected decisions are
  excluded, a chain of supersessions collapses to its latest decision;
- similar decisions can be **consolidated** into one, through the normal
  ratification path;
- it scales to **thousands of decisions** by walking an index, not by
  returning the corpus.

## Constraints from accepted decisions

| Decision | What it requires here |
|---|---|
| dec-001 | Decisions live in the Context Engine; this kit reads and proposes through the hosted SchemaBounce MCP, never a copy. |
| dec-002 | Accepted decisions are immutable; corrections only by supersession, ratified by someone with authority over every domain of the superseded decision. Agents never ratify. |
| dec-081 | Hosted code sessions load a repository's skills, subagents, rules and commands; repository hooks are refused; mods and plugins only from a workspace library or a pinned marketplace listing. |
| dec-106 | A code session's SchemaBounce MCP access is read-only and belongs to the session owner. |

## Measured problems (2026-10-14)

- Decisions carry only `domains`: 15 values over 115 records, two or three per
  record. `architecture` is on 67, `product` on 55, `security` on 46, so a
  domain filter does not narrow. One-off values (`demand_signal_scout`)
  show the vocabulary is not controlled.
- `records_query` with `{"domains": "pricing"}` returns 0 though 29 records
  carry it: list membership is not filterable. A string range filter returns
  HTTP 500.
- A semantic decision search returned about 700 KB of full records.
- Agents allocate `dec-NNN` by reading the maximum and adding one. Two
  sessions did this on 2026-10-14 and one proposal was overwritten (dec-119,
  restored by hand), because proposed-to-proposed edits are open.
  The `propose` action (task_kit_01_propose_server_id, core-api `development`,
  not promoted) closes this: the server assigns the id and a proposed record
  is editable only by its proposer or a holder of `adl:decide`.

## Model

### Decisions stay immutable; classification lives beside them

A decision record keeps its ratified content (dec-002). Everything used to
find it lives in a separate **classification index** that stewards may edit
with an audit trail, without touching the ratified content hash:

- **Topics**: a controlled tree, for example
  `code-mode/licensing/personal-subscription` or `pricing/tiers`. One registry
  holds the vocabulary; agents cannot invent a topic, they propose one.
- **Applies-to patterns**: repository-scoped path globs, for example
  `core-api:schemabounce-api/internal/services/codesession/**`, attached to a
  topic or directly to a decision.
- **Edges**: `supersedes`, `consolidates`, `refines`, `relates`, kept in the
  Context Engine graph.
- `domains` stays as the coarse grouping used for ratification authority.

### Current authority

A **lineage** is a chain of supersessions. Its **head** is the one decision
in it that is accepted and not superseded. Retrieval returns heads only.
History (`include: "history"`) is opt-in. Proposed decisions are returned only
when asked for, labelled as not binding.

### Consolidation

A consolidated decision is an ordinary proposal whose `supersedes` lists two
or more accepted decisions. When a person with authority over every domain
involved accepts it, the server marks all of them superseded in the same
transaction and the new decision becomes the head of a merged lineage that
inherits the union of their classifications. A steward agent finds candidates
(same topic, high embedding similarity, overlapping applies-to, or explicit
`relatedDecisions`), drafts the consolidated statement, and records it as
proposed. Nothing is merged without ratification.

## Just-in-time retrieval (the central design)

One call answers "which rulings bear on what I am about to do":

```
context(repo, paths[], topics[], query, budget_tokens) -> cards[], more
```

1. **Paths to topics.** Each path is matched against the repo's applies-to
   patterns. Patterns are indexed by repository and first path segment, so a
   lookup touches only the patterns that could match.
2. **Walk the topic tree.** Matched topics expand to their ancestors through a
   closure table: a ruling on `code-mode` also governs
   `code-mode/licensing`. Depth is bounded.
3. **Collapse to heads.** Candidate decisions map to their lineage heads;
   superseded, rejected and (by default) proposed are dropped.
4. **Rank.** Most specific first (a direct path match beats a topic ancestor,
   a deep topic beats a shallow one), then binding strength, then recency. A
   `query`, when given, re-ranks inside the candidate set by embedding
   similarity; it never widens the set to the whole corpus.
5. **Emit cards within the budget.** A card is the id, title, a one-sentence
   statement, status, decided date, topics and why it matched (about 60
   tokens). The response stops at `budget_tokens` and returns a `more` cursor.
   The full record comes from `get(id)` only when the agent needs it.

**Digests.** Each topic node has a precomputed digest of its heads, versioned
by a corpus counter that increments on any decision or classification change.
A session start can inject the digest for the repo's topics in a few hundred
tokens, and clients cache by (topic, version).

**Scale.** Classification, lineage heads and the topic closure live in
dedicated control-plane tables (Kolumn HCL), not in generic JSON record
queries. Thousands of decisions and tens of thousands of patterns stay well
inside indexed lookups; responses are bounded by the budget, not the corpus.

## Server surface (core-api)

A dedicated MCP tool, `sb_decision`, on the hosted SchemaBounce MCP:

| Action | Purpose | Code Mode (read-only) |
|---|---|---|
| `context` | The just-in-time call above | yes |
| `search` | Text and topic search over heads, compact rows | yes |
| `get` | One full record | yes |
| `lineage` | Supersession and consolidation history of a decision | yes |
| `propose` | Create a proposal; the server assigns the id and refuses to overwrite | no |
| `consolidation_candidates` | Clusters a steward can merge | no |
| `classify` | Steward edits to topics and applies-to, audited | no |

Responses are compact JSON with resource links (`schemabounce://decisions/dec-NNN`)
for progressive disclosure. Read actions are marked read-only.

## This repository: the plugin

```
.claude-plugin/plugin.json        plugin manifest (name: schemabounce)
.claude-plugin/marketplace.json   this repo is its own marketplace
.mcp.json                         the hosted SchemaBounce MCP (OAuth login per person)
skills/schemabounce-decisions/    when and how to use decisions (Agent Skills format)
hooks/hooks.json                  phase 2: path-scoped context before edits
agents/                           phase 3: decision steward subagent
AGENTS.md                         the same rules for Codex and other agents
```

Patterns used, verified against the Claude Code documentation on 2026-10-14:

- **Skills** follow the open Agent Skills format (name and description
  frontmatter, body loaded on use, references loaded on demand), so the same
  files serve Claude Code and other agents.
- **Hooks** (phase 2) call the MCP directly with `type: "mcp_tool"` on
  `PreToolUse` for `Edit|Write|MultiEdit`, passing the file path, and return
  the cards as `additionalContext` (10,000-character cap, phrased as facts).
  `mcp_tool` hooks are skipped at session start, so start-of-session context
  comes from the platform (Code Mode) or the skill (local).
- **MCP tool search** keeps tool schemas deferred until used.

## Where it runs

| Surface | How the kit arrives | Just-in-time context |
|---|---|---|
| Local Claude Code | Each repo checks in `.claude/settings.json` with this marketplace and `schemabounce@schemabounce-agent-kit` enabled; the marketplace entry pins the version | Hooks before edits; the skill at task start |
| Hosted Code Mode | The platform fetches this plugin at a pinned digest and loads it into every session as a platform plugin (Agent SDK `plugins: [{type: "local"}]`), outside the repository | Core-api adds the repo digest to the session's start context; hooks before edits; read-only `sb_decision` |
| Codex and other agents | `AGENTS.md` and the Agent Skills files, generated into each repo from this kit; MCP configured in their own config | The skill; `context` called explicitly |
| SchemaBounce agents | Native decision tools in the runtime; the decision rule deployed as a workspace rule | Same `context` call |

Loading the kit into every hosted session without a per-person approval
refines dec-081 clause 5 and needs the decision below.

## Decision

dec-125, accepted 2026-10-14 21:06Z: classification index beside immutable
decisions; current authority and consolidation as above; server-assigned ids;
one public agent kit as the single source for every agent surface; the
platform loads it, pinned, in every hosted code session (refining dec-081
clause 5 for this kit only). Work is tracked as task_kit_00 to task_kit_09 on
the SchemaBounce board.

## Phases

0. **This repo, the design, and a version 0 skill** that works with today's
   tools (`sb_adl` records_get and search), with their limits stated.
1. **Server API**: `sb_decision` context, search, get, lineage, propose with a
   server-assigned id; classification tables and the topic registry; list
   filters fixed.
2. **Hooks and Code Mode**: path-scoped hooks; core-api start-of-session digest;
   the platform loads the pinned kit in hosted sessions.
3. **Backfill and consolidation**: a steward agent proposes topics and
   applies-to for every existing decision for a person to approve in bulk; then
   consolidation candidates.
4. **Every repo and agent**: settings checked into each SchemaBounce repo,
   AGENTS.md and skills generated for Codex, a check that a repo enables the
   expected version.
5. **Customers**: the same kit against a customer's own decision plane.

## Open checks

- Whether an `mcp_tool` hook can target a server that a plugin provides (the
  plugin server registers as `plugin:<plugin>:<server>`).
- How `-p` and Agent SDK sessions treat plugin trust in the hosted sandbox.
- Which directories Codex reads skills from.
