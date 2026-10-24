# Connected services, built-in tools, marketplace and skills

## Connected MCP servers

A workspace connects external services as MCP servers (hosted by the
platform, or remote by URL) and grants them to agents. Their tools appear in
a granted agent's list as `<server>__<tool>`.

- **Your tool list is the authority.** If a tool is in it, you were granted
  it: call it and report what came back.
- `adl_list_mcp_connections` is a diagnostic for after a call failed. A
  connection showing `pending` or `unverified` very often works fine; never
  skip a call or call a service missing because of that status.
- Credentials are handled by the platform. You never see or store a
  service's key. If a service you need is not connected, say so and point
  the person to the connections page (find it with `adl_find_ui_path`).
- Calls that change something on the outside may park for approval (see
  [references/approvals-and-secrets.md](references/approvals-and-secrets.md)).
- A connection can be Personal (one person's account), Domain (shared
  inside one domain) or Workspace (a shared service identity). Which account a call uses is decided by the
  grant, not by you.

Outside: `sb_access` `connection_*` (create, validate, health, reconnect URL,
traces), `grant` / `revoke` / `set_tool_allowlist`. To wire a server to an
agent: `connection_create`, then `grant`. A custom server is submitted as
JSON: a remote server by URL (`streamable-http` or `sse`), or a stdio server
from an npm, PyPI or pinned GitHub release package that the platform's
gateway runs.

## Built-in calculation tools

The platform ships a library of deterministic tools: finance, statistics,
dates and business days, unit conversion, text and document processing,
geospatial, HR, legal, healthcare, e-commerce, marketing, devops, security
and web fetching. They run in milliseconds, cost no model tokens and return
exact results.

Before you calculate, convert, parse or transform anything by hand, search:
`adl_tool_search("amortization")`, `("business days")`, `("parse csv")`,
`("statistics")`. Use the result exactly; do not round or re-interpret it.

## Marketplace

The marketplace lists **bots** (blueprints that deploy as agents), **domain
templates** (a bundle of bots, data kits and an org chart for one domain),
**MCP servers**, **data kits** and managed workflows.

- `adl_search_catalog`, then `adl_get_catalog_detail` for one result.
- An agent never deploys a bot itself: `adl_propose_agent` puts the hire in
  the Inbox.

Outside: `sb_marketplace` (`list_bots`, `list_templates`, `activate_bot`,
`use_template`, managed services). Builders who sell on the marketplace use
`sb_builder`.

## Skills

A skill is instructions an agent loads when a task needs them.

- **This skill** (`schemabounce`) is SchemaBounce's own manual, in the open
  Agent Skills format.
- **Public skills** come from the open Agent Skills ecosystem (found on
  skills.sh, pinned from GitHub by commit). A workspace adds them to agents;
  a skill whose security audit fails is refused. A pinned skill changes only
  when a person updates it.
- Inside an agent, the `# Skills` list shows each attached skill's
  description. `adl_invoke_skill` loads one; its `file` argument loads a
  supporting file. Scripts in a skill are never run in a hosted agent.

Do not confuse these with crystallized skills (`adl_discover_skills`,
pre-computed database queries) or workspace **rules**, which are always-on
guardrail text in every agent's prompt.
