# Driving a workspace from outside: the hosted SchemaBounce MCP

Assistants and coding agents (Claude, Codex, Cursor and others) reach a
SchemaBounce workspace through the hosted MCP server at
`https://mcp.schemabounce.com/mcp`. It acts as the signed-in person, through
the same API and permissions as the console: a call that person may not make
fails with the reason.

## Connecting

- **Interactive clients**: add the server and sign in with OAuth (in Claude
  Code, `/mcp`). The SchemaBounce agent kit plugin adds the server for you.
- **Scripts and CI**: a workspace service account issues a client id and
  secret; exchange them at `POST /api/v1/oauth/token` for a bearer token.
  Create one in the console (find the page with the console lookup) or with
  `sb_credential` `create_sa`.
- **Personal agent tokens**: read-only by default and never beyond the
  person's own access (`sb_integrations` `personal_token_create`). The secret
  is shown once.

If the server is signed out or unreachable, say so. Never guess what it would
have returned.

## Start here

1. `sb_workspace` `attention`: what needs a person now, each item with a
   console link and the MCP action that fixes it.
2. `sb_inbox` `pending`: everything waiting for a decision.
3. Then the tool for the area you are working in.

## The tools

| Tool | Area |
|---|---|
| `sb_workspace` | attention, typed faults (`events`), workspace settings, notifications, egress policy, config export, members and roles |
| `sb_agent` | agents, chat, runs and failures (`runs_get`, `runs_evidence`, `runs_scorecard`), setup status, overlays, domains, A2A, improvement proposals |
| `sb_adl` | records, memory, knowledge graph, semantic search, warehouse SQL (`duckdb_query`), workspace rules, embeddings |
| `sb_inbox` | approvals, decision ratification (people only), pipeline proposals, file grants, escalations |
| `sb_decision` | decision context, search, lineage, propose (see [references/decisions.md](references/decisions.md)) |
| `sb_metrics` | goals, North Star, outcome metrics, overview, activity, domain health (see [references/goals.md](references/goals.md)) |
| `sb_automation` | workflows, schedules, n8n import, model provider keys |
| `sb_access` | MCP connections, grants, tool allowlists, data access policy, approval policy |
| `sb_credential` | service accounts, API keys, OAuth clients, environment and workspace secrets |
| `sb_ops` | files and SSO |
| `sb_integrations` | Slack, Discord and WhatsApp bindings, GitHub, Atlassian, agent email inboxes, VPN, personal tokens |
| `sb_code_session` | hosted code sessions (see [references/code-sessions.md](references/code-sessions.md)) |
| `sb_billing` | plan, credits, rate card, spend limits, budgets |
| `sb_marketplace` | bots, domain templates, managed workflows and services |
| `sb_builder` | the builder side of the marketplace |
| `sb_env`, `sb_source`, `sb_sink`, `sb_route` | pipelines (see [references/pipelines.md](references/pipelines.md)) |
| `sb_schema` | Kolumn schema state, drift, applies, catalog, read-only SQL |
| `sb_audit` | the workspace audit log |

Every tool takes an `action`. Paged reads return `next_cursor` while
`has_more` is true; pass it back as `cursor`.

## Confirmations and parked calls

Some changes ask you to confirm (deletes, production changes, anything that
costs money). A client that cannot show a confirmation gets
`status: awaiting_approval` and an `approval_id`: the call waits in the Inbox
for a person for up to 7 days. Check `sb_inbox` `pending`; once a person
approves it, repeat the same call with the same arguments and it runs once.
Approving, rejecting and other Inbox decisions are never parked: a person
makes them directly.

Some lifecycle actions ask the person to type a phrase, for example
`PUSH <session_id>`.

## Agent conversations

Every interaction with a SchemaBounce agent goes through this server: `chat`
to talk to one, `conversations_list` and `sessions_messages` to read a
thread, `runs_*` for what a run did. Never read or replay conversation
content any other way.

## Plans

Some features need a paid plan; decision records need Starter or higher. A
`402 PLAN_FEATURE_REQUIRED` answer means the plan does not include it: say
so, and do not work around it.
