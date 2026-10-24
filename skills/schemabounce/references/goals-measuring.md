# Measuring a goal through the hosted MCP

Every call below is an action of a hosted SchemaBounce MCP tool as it works
today. Steps 4, 5 and 6 are writes (`outcome_declare`, `outcome_snapshot`,
`goal_update`, and any `goal_create`): make them only when the person you work
for asks or agrees.

## Two meanings of "domain"

- An **org-chart domain** is a group of agents and people (ids start with
  `dom_`). A domain goal is owned by one: `ownerDomainId`.
- An **outcome domain** is one of the ten areas in the metric catalog
  (`marketing_growth`, `revenue_sales`, `support_success`, ...). A metric
  declares one: `metric_domain`.

They are unrelated fields. Do not put a `dom_` id in `metric_domain`.

## 1. Find the goal and what measures it now

- `sb_metrics` `goals_list` (filters `goal_level`, `goal_owner`,
  `goal_status`), or `goals_tree` for the whole tree under a goal.
- `sb_metrics` `goal_get` with `goal_id`. Read `keyResults` and
  `progress.keyResultProgress`. An empty `keyResults` list with no linked
  tasks means the goal is not measured.
- `sb_agent` `domain_list` names the org-chart domains, their members
  (`agentOrder`) and parents (`parentDomainId`).

## 2. Pick the outcome domain and look for an existing metric

- `sb_metrics` `outcome_catalog` lists the ten outcome domains and the
  canonical metrics in each, with their usual direction and caveat class.
- `sb_metrics` `outcome_list` lists every metric this workspace has declared,
  with its baseline, latest value and change. Reuse a metric that already
  measures the number.

## 3. Choose records that hold the number

A `records_query` metric aggregates one record type the workspace already
holds. The cleanest source is **one summary record per run** that carries
the number itself, read with aggregate `latest`. Counting raw rows over the
attribution window counts every repeated run again.

Filters use these keys:

| Key | Meaning |
|---|---|
| `field` | equals the value |
| `field__gte`, `field__lte`, `field__gt`, `field__lt` | numeric comparison |
| `field_in` | equals any value in a list |
| `field` set to `null` | the field is missing or null |

At most ten filters. Record fields are matched by their exact names.

## 4. Declare the metric (write)

`sb_metrics` `outcome_declare`. It is an upsert keyed by `metric_key`, so
declaring the same key again updates it.

| Argument | Required | Notes |
|---|---|---|
| `metric_key` | yes | Stable, lowercase, underscores. Key results point at it. |
| `metric_domain` | yes | An outcome domain id from `outcome_catalog`. |
| `metric_source` | yes | `records_query`. (`connector` is accepted but does not run yet.) |
| `metric_source_query` | yes for records_query | `entity_type`, `aggregate` (`count`, `sum`, `avg`, `min`, `max`, `latest`; default `count`), `field` (every aggregate but `count`), `filters`, `time_field`. |
| `metric_direction` | yes | `up` or `down`: which way is good. |
| `metric_attribution_caveat_class` | yes | `direct_sla`, `confounded_market` or `mixed`: how strongly the work can be said to have caused a change. |
| `metric_label`, `metric_unit`, `metric_description` | no | What people read. |
| `metric_attribution_window` | no | `<n>h`, `<n>d` or `<n>w`. Default `30d`. The query only reads records created within this window (at most 90 days), so the latest summary record must fall inside it. |
| `metric_agent_refs`, `metric_workflow_refs` | no | Who the metric is declared for. Empty means workspace level. |
| `metric_target` | no | A default only; the key result owns the target. |

## 5. Capture a baseline (write)

`sb_metrics` `outcome_snapshot` with `metric_key`. It reads the source now
and stores the value with a timestamp. Until a metric has a snapshot, a key
result on it reads `unresolved`.

## 6. Attach it to the goal (write)

`sb_metrics` `goal_update` with `goal_id` and
`goal: {"keyResults": [...]}`. The list **replaces** the goal's key results:
first `goal_get`, copy every existing entry from `keyResults`, append the new
one, and send the full list. Sending only the new entry deletes the others.
Each entry:

```json
{"metricDeclarationId": "<metric_key>", "targetValue": 10, "direction": "up"}
```

`metricDeclarationId` is the metric's `metric_key`. For a new goal, pass the
same list as `keyResults` to `goal_create`.

## 7. Read it back, then report

`sb_metrics` `goal_get` again. Report what it shows: the key result, its
metric, and the progress or `unresolved` reason the server returned. If the
key result is missing, say the attach failed. Never report a number the read
did not return.

## Worked example (illustrative only)

Use your own record types and keys; nothing here is required wording. A domain
tracks search rankings for twelve keywords. Each weekly run already
writes one record per keyword. To measure "keywords in the top 20":

1. Have each run also write one `rank_summary` record with
   `keywords_in_top_20` and `run_at`.
2. Declare `metric_key: "keywords_in_top_20"`, `metric_domain:
   "marketing_growth"`, `metric_source: "records_query"`,
   `metric_source_query: {"entity_type": "rank_summary", "aggregate":
   "latest", "field": "keywords_in_top_20", "time_field": "run_at"}`,
   `metric_direction: "up"`, `metric_attribution_caveat_class:
   "confounded_market"`, `metric_unit: "count"`.
3. Snapshot it for the baseline.
4. Attach `{"metricDeclarationId": "keywords_in_top_20", "targetValue": 6,
   "direction": "up"}` to the domain goal, then read the goal back.
