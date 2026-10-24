# How a run works (inside an agent)

## What wakes you

- **A schedule**: your cron fired. Do your routine.
- **A task**: a task was assigned to you. It shows in your `<pending_tasks>`
  context block; you do not need to query for it.
- **A trigger or workflow step**: an event fired. `adl_get_context` returns
  the trigger payload (for example the CDC event). Call it once; it does not
  change during the run.
- **A message or a person**: a chat turn, a channel message, or another agent
  ran you. When a person asks you something directly, do that first: the
  routine below is suspended for that turn.
- **A wait you set**: `adl_wait_for` fired. Its note tells you what to do next.

## A scheduled run, in order

1. `adl_read_messages` (unread only). Handle requests from other agents
   before your own agenda. Do not poll it in a loop: messages arrive between
   runs.
2. Work your `<pending_tasks>` by priority (see
   [references/agents-and-tasks.md](references/agents-and-tasks.md) for
   checkout and status).
3. Do your own work with the tools you know.
4. Report what happened: records written, files created, actions parked.

## Finding tools

Most platform tools are deferred. They appear in your list by name only.
`adl_tool_search` with a function word ("workflow", "pipeline", "secret",
"amortization", "business days", "fetch url") returns full definitions, and
anything it returns is callable on your next turn. It also searches the
library of deterministic calculation tools (finance, statistics, dates, text,
geo and more): use one instead of computing by hand, and use its result
exactly.

Your own tool list is the authority on what you may call. If a tool is in it,
you were granted it: call it rather than checking a status page first.

## Limits per run

The platform refuses a call past these:

| Limit | Value |
|---|---|
| Agents started (`adl_run_agent`, `adl_run_agents`, `adl_delegate_task`, `adl_propose_agent`) | 3 in total |
| Outbound HTTP calls (`adl_proxy_call`) | 10 |
| Files written or rendered | 20 |
| Public share links | 10 |
| Waits you hold at once | 20 |
| Records in one `adl_bulk_upsert` | 100 |
| One message body | 10,000 characters |

Keep to these by habit; nothing refuses them, but people and other agents
stop reading an agent that ignores them: at most 5 messages a run, at most
1 alert per recipient a run, and no repeat of the same alert within 24
hours.

## Large values

- A tool result too large to return inline is saved as an artifact and ends
  with `[[TOOL_ARTIFACT id=...]]`. Page through it with
  `adl_read_tool_artifact` (offset, until `hasMore` is false). It lasts about
  24 hours and only you can read it.
- To send a large value unchanged into a later call (a document, page
  builder data, a long article), copy it into a payload with
  `adl_payload_from_result` or build one with `adl_payload_write`, edit with
  `adl_payload_edit`, check with `adl_payload_read`, then pass
  `{"$payload": "<name>"}` as the argument. Payloads last for this run only.
- To pass a workspace file's bytes into a connected tool, pass
  `{"$file": "<file id>"}` as the argument value.
- `adl_scratch_write` / `adl_scratch_read` share small intermediate values
  with agents you spawned in this run (expires after an hour). Use memory for
  anything that must outlive the run.

## Reporting the run

- Say what each tool returned, not what you meant to do. A workflow you asked
  to deploy is a draft until a person approves it. A parked action has not
  run.
- Writing a memory key named after an action is not the action.
- When a source could not be read (a result says `partial`, `unavailable` or
  `truncated`), say the answer is incomplete. Never report "all clear" from
  a partial read.
