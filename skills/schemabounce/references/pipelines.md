# Data pipelines

A pipeline **route** moves data from a **source** to one or more **sinks**
inside an **environment**. Sources include database change data capture
(CDC), outbox tables, webhooks, SaaS connectors and scheduled direct pulls.
Sinks include warehouses, streams, object storage, webhooks, databases and
the workspace's own records (`agent_datastore`). On a paid plan,
pipeline data also lands as typed tables in the workspace warehouse's
`sb_pipelines` schema, where SQL can read it (see
[references/data-layer.md](references/data-layer.md)).

## Inside an agent: look, then propose

Agents read pipeline state and propose routes. A person approves every new
route.

- `adl_list_pipeline_routes`: existing routes with source, status, sinks and
  event counts. Check it first: duplicate routes cause conflicting data.
- `adl_list_workspace_sources`: configured connector and webhook sources
  (CDC and outbox sources are configured through routes and are not listed
  here).
- `adl_list_connectors`: the SaaS connector catalog, filter by category or
  name.
- `adl_list_sink_types` and `adl_list_workspace_sinks`: destinations the
  workspace can use and the ones it already has (with retry and dead-letter
  settings).
- `adl_propose_pipeline_route`: proposes a route with `source_type`,
  `connector_id` and the objects to sync for SaaS, the sink, and a `reason`
  that states the business value. Nothing is created until a person approves
  it; approval fails, and says so, if the named source, sink or environment
  does not exist.
- `adl_get_route_status`: health of one route.
- `adl_get_route_metrics`: per-window event counts, failures, retries, bytes
  and latency.
- `adl_get_agent_metrics`: per-agent runs, tokens, estimated cost and
  failure rate.

### Finding data you are missing

1. Compare the entity types you are meant to read against
   `adl_list_entity_types`.
2. For a type that is missing or empty (`adl_query_records` with a limit of
   1), check whether a route already feeds it.
3. If none does, find the matching connector and propose a route with a
   reason tied to your job. A type that has records but no route may be
   filled by people or another agent: that is healthy.

### Watching route health

Keep baselines in memory and compare each run against them: throughput
falling by more than half, latency several times its baseline, error rate
above a few percent, or a growing dead-letter queue. A growing dead-letter
queue means data is not arriving: never dismiss it. Ignore a single short
spike, update baselines gradually, and write deviations as findings with a
severity (see [references/reporting.md](references/reporting.md)).

## Outside: build and run pipelines

| Tool | Covers |
|---|---|
| `sb_env` | environments: list, create, update, delete, promote routes, sinks, sources and secrets from one environment to another |
| `sb_source` | sources: catalog, create, test, webhook config and replay, CDC resync, SaaS sync, direct pull and backfills, public CAPTCHA forms |
| `sb_sink` | sinks: create, test, pause, transforms (mask, filter, rename, add field) |
| `sb_route` | routes: create, update, pause, resume, sync, archive; and the environment's pipeline workers: enable, scale, pause, disable |
| `sb_inbox` | `pipeline_proposal_approve` / `reject` for routes agents proposed |
| `sb_schema` | Kolumn schema state, drift, applies, catalog search, read-only SQL through an analytics connection |

Changes to production, enabling or scaling workers (which costs money),
resyncs and deletes ask for confirmation. Schema changes go through Kolumn,
never raw SQL DDL.
