# Findings, reports, briefings and monitoring

Conventions that keep agent output readable by people and by other agents.

## Findings

A finding is a record another agent or a person can act on.

- Write it with `adl_write_record` (or `adl_bulk_upsert` for several) under
  your role's findings type, for example `sre_findings`.
- Include: what was observed, the affected entity (`entity_type` and
  `entity_id`), a `severity` (`critical`, `high`, `medium`, `low`), the
  evidence, and when.
- Tell whoever must act with `adl_send_message`: `alert` for critical and
  high (keep it to one per recipient per run), `finding` for the rest,
  batched into one message per recipient. Send the finding's id, not its
  body.

## Severity

- **critical**: act now; something is broken or losing data.
- **high**: investigate this run or next.
- **medium**: note it for trends.
- **low**: informational.

Compare against a baseline before you call anything abnormal. A single
outlier is logged, not escalated; require a pattern (for example three
consistent shifts) before moving a threshold.

## Incremental reports

Reports that run on a schedule work on what changed since the last run.

`adl_query_records` matches exact values only: it cannot filter by date or
range, returns at most 100 records and has no paging. So give records a
value you can match exactly:

- **A period field**: producers write `period: "2026-10-24"` (or a week or
  month key), and the report queries that one period.
- **A state field**: unreported records carry `reported: false`; after the
  report, set it to `true` on the records you covered.
- **Your own list**: keep the ids you already covered in memory and skip
  them.

Then:

1. Read your state from memory (`adl_read_memory`): the last period covered,
   or the covered ids.
2. Query only the new period or the unreported records. When more than 100
   could match, narrow the filter further, or have the platform build a file
   with `adl_export_records` instead of reading rows yourself.
3. Analyse, then write the report: a short findings record and, when a person
   will read it, a file (`adl_write_file`, or `adl_render_file` for PDF or
   Word).
4. Update your state only after the report is written.
5. Send downstream agents a summary with the report's id.

Never re-analyse what earlier runs covered, and never send a full report
body as a message.

## Briefings

A briefing summarises other agents' findings for a person.

1. Read the last briefing checkpoint from memory.
2. Collect findings and alerts written since then, using the period or state
   fields above (findings types usually share a `severity` field you can
   match, for example `severity: "critical"`).
3. Rank: critical first, then by fit with the workspace's priorities (read
   the North Star goal and `northstar:` memory), then by recency.
4. Group by domain, at most five items each, linking to the full findings.
5. Write the briefing, then move the checkpoint.

## Monitoring records

1. Load the current rules and thresholds from memory before every run.
2. Check every record in scope; log how many you checked and how many failed,
   so coverage can be proven. A query returns at most 100 records: if
   `has_more` is true, split the scope with more exact filters until every
   part fits, and say so if you could not cover it all.
3. Use built-in validation and PII-detection tools
   (`adl_tool_search("validate")`) instead of judging by eye.
4. Write one finding per violation and escalate critical ones.

## Numbers people see

- Report figures as the tools returned them, with their window ("last 7
  days").
- A number that must appear on a goal has to be a declared outcome metric
  (see [references/goals.md](references/goals.md)). Memory notes and files
  never show on a goal.
- Costs come from the platform's rate card and run usage, never from a price
  you remember.
