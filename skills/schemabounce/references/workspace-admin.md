# Workspace administration

Most of this is for people working through the hosted MCP or the console.
Agents read some of it; they do not administer the workspace.

## Members and roles

`sb_workspace`: `member_list`, `member_add` (email, role), `member_remove`,
`member_update_role`, `roles_list`, `role_get`, `permissions_list` (every
permission key, plus your own), `role_clone_builtin` (an editable copy of a
built-in role). Removing an owner asks for confirmation.

## Domains and the org chart

A **domain** is a group of agents and people (marketing, finance, software).
It has a head, members, a supervision setting, goals and its own
connections. The org chart (`adl_get_org_chart`) decides where escalations
go. Outside: `sb_agent` `domain_list`, `domain_create`, `domain_update`
(including the head), `domain_set_members`, `domain_delete`.

## Workspace rules

Rules are always-on guardrail text rendered into every agent's prompt, every
turn, with a severity (`guideline`, `guardrail`, `hard`) and an optional
scope (`applies_to`, for example `tools/github`). They are advice to the
model, not permissions: anything that must be enforced belongs in the
approval policy or access grants. Outside: `sb_adl` `rules_list`,
`rules_create`, `rules_update`, `rules_delete`.

## Credentials

`sb_credential`: service accounts (`create_sa`, `rotate`), API keys and OAuth
clients per environment, and secrets (environment secrets, and workspace
secrets with allowed hosts, a use policy and grants to agents, domains,
workflows or connections). New credentials are shown once; secret values are
write-only.

## Integrations

`sb_integrations`: Slack, Discord and WhatsApp connections and the bindings
that route a channel or number to an agent; GitHub App installations and
repository bindings; the Atlassian connection behind Jira task board sync;
per-agent email inboxes; VPN connections (Tailscale, WireGuard, NetBird,
ZeroTier); personal agent tokens; `connect_url` for a browser sign-in.

## Policies

- **Approval policy** (`sb_access` `approval_policy_*`): which agent actions
  run on their own and which wait for a person, workspace-wide or per agent.
- **Data access policy** (`sb_access` `policy_*`): which records an agent may
  read and write.
- **Egress** (`sb_workspace` `egress_get` / `egress_set`): which outside
  hosts agents can reach (`open`, `llm-only`, `restricted`, `none`, allowed
  domains, and a lock that beats per-agent overrides).
- **Notifications** (`sb_workspace` `notifications_*`) and per-person Slack
  forwarding (`sb_inbox` `notification_prefs_*`).

## Audit

`sb_audit` `search` filters the audit log by time, event type, actor and
resource type; `export` returns the full matching set on plans that include
it. Audit metadata can hold captured request data: never paste it into
messages or reports.

## Configuration as code

`sb_workspace` `config_export` returns the workspace configuration as a
document that names things instead of using ids, with secrets as
placeholders.
