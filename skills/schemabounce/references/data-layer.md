# The Agent Data Layer: records, memory, graph, analytics

Paths in this file are relative to the skill root.

Four stores, each with its own tools. Pick by what you are holding:

| You are holding | Store |
|---|---|
| Structured business data other agents and people read (contacts, findings, tasks) | Records |
| Your own notes, state between runs, learned preferences | Memory |
| How records relate (works at, belongs to, owns) | Knowledge graph |
| Raw change events streamed from pipelines | CDC analytics (DuckDB) |

## Records

A record is `entity_type` + `entity_id` + a JSON `data` object.

- **Discover first.** `adl_list_entity_types` lists the types you may read
  with counts and schema status. `adl_get_schema` shows a type's declared
  fields, or the fields observed in recent records when none is declared.
  Read it before you query or write so you do not guess field names.
- **Find by meaning**: `adl_semantic_search` (vector plus keyword, and it
  returns graph-connected records too). Use it first whenever you do not
  know exact field values.
- **Find by exact value**: `adl_query_records` filters one entity type on
  exact field matches. No ranges, operators, timestamps or wildcards, at most
  100 results and no paging: `has_more` means there were more.
- **Fetch one**: `adl_get_record` by type and id.
- **Write one**: `adl_write_record` (alias `adl_upsert_record`). A write
  replaces the record's whole `data`, so a field you leave out is dropped.
  Only `tasks` records merge. `{}` is refused.
- **Write several**: `adl_bulk_upsert`, up to 100 records across types,
  all or nothing. Use it for 3 or more. Create tasks with `adl_create_tasks`
  instead (see [references/agents-and-tasks.md](references/agents-and-tasks.md)).
- **Delete**: `adl_delete_record` soft-deletes one. For age-based cleanup
  use `adl_purge_stale_records` (dry run first, minimum age 7 days, at most
  10,000 per call).

Naming: findings an agent writes for others usually use a role prefix
(`sre_findings`, `mkt_findings`). Keep one entity type per kind of thing and
reuse existing types before inventing new ones.

## Memory

Key-value entries in namespaces, persistent across runs.

- `adl_add_memory`: unstructured text; the platform extracts facts and
  indexes them for search. Use it for observations and preferences.
- `adl_write_memory` / `adl_read_memory`: exact JSON at an exact key. Use it
  for state such as cursors and baselines. `key: "*"` lists a namespace.
- `adl_search_memory`: hybrid semantic and keyword recall, favouring recent
  entries. Be specific ("customer churn reasons Q1", not "everything about
  churn").
- `adl_list_memory`, `adl_delete_memory`.

Namespaces:

- Your own namespaces are private to you.
- `shared:` is readable by every agent in the workspace. Read before you
  write so you do not overwrite another agent's entry.
- `domain:` is shared inside a domain.
- `northstar:` is workspace configuration and read-only for agents.

The agent that first wrote an entry owns it. An entry another agent sealed or
marked sensitive is hidden from you; results say how many were hidden. Never
work around that by asking the owner to paste it.

Housekeeping: `adl_get_namespace_stats`, `adl_consolidate_memory`
(`archive_stale`, `promote_to_durable`, `refresh_confidence`),
`adl_set_memory_ttl`, and `adl_purge_memory_namespace` (dry run first; the
real purge waits for a person in the Inbox).

## Knowledge graph

- `adl_add_edge` links two existing records with a named relationship.
  Writing records does not create edges: add them right after you store
  related records. Use stable `UPPER_SNAKE_CASE` names (`WORKS_AT`,
  `BELONGS_TO`, `OWNS`). Repeating the same edge updates it.
- `adl_search_graph`: one hop, by relationship, with `direction` incoming,
  outgoing or both.
- `adl_query_neighbors`: up to 3 hops, outgoing only. Keep depth at 1 or 2 on
  large graphs and cap with `max_nodes`.
- `adl_get_graph_stats`, then `adl_purge_orphan_edges` to remove edges that
  point at deleted records (dry run first; the real delete waits for a
  person).

## CDC analytics (DuckDB)

`adl_query_duckdb` runs read-only SQL over change events streamed from the
workspace's pipelines. Events land in one table, `cdc_events` (route,
source, schema and table name, operation, a JSON `payload`, timestamps).

- Start with `SHOW TABLES` and `DESCRIBE cdc_events`.
- Aggregate (`count`, `sum`, `GROUP BY`) rather than pulling rows: replies
  over 8 MiB are refused.
- Pass user-supplied values through `params`.
- It holds pipeline events only. Records, memory and graph edges are not in
  it: use the tools above for those, and `adl_get_data_stats` for counts.

Outside: `sb_adl` `duckdb_query`.

## Crystallized skills (pre-computed queries)

Queries that repeat often can become stored functions or materialized views
that run in milliseconds with no model tokens.

- `adl_discover_skills`, then `adl_execute_skill` to run one that exists.
  Check before you re-implement a query the workspace already has.
- `adl_list_query_patterns` and `adl_list_crystallization_candidates` show
  what repeats; `adl_propose_crystallization` proposes one for a person to
  approve.

These are unrelated to this skill and to `adl_invoke_skill`, which loads
skill instructions.

## Cleanup, safely

1. Measure: `adl_get_data_stats`, `adl_get_namespace_stats`,
   `adl_get_graph_stats`.
2. Preview: run the purge tool with its default dry run and read the count.
3. Record why: write a short record of what you intend to remove and why.
4. Run it for real. Destructive purges wait for a person in the Inbox.
5. Measure again and report the actual change.

Never purge another agent's private namespace, `northstar:` data, or records
younger than 7 days. Purge orphan edges after deleting records.

Outside: `sb_adl` covers records, memory, graph, search and workspace rules.
