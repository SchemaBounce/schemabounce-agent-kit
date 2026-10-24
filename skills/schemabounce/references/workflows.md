# Workflows, triggers and schedules

Three ways to automate, from simplest to richest:

| Need | Use |
|---|---|
| Run an agent when a record is created, updated or deleted | a trigger (`adl_create_trigger`) |
| Run an agent or a workflow on a cron | a schedule (outside: `sb_automation` `schedule_*`) |
| Several steps, branches, approvals, transforms | a workflow (`adl_create_workflow`) |

Check what exists first (`adl_list_triggers`, `adl_list_workflows`):
duplicates fire duplicate actions.

## The workflow graph contract

A workflow is `nodes` plus `edges`. Get these right or the workflow saves,
deploys, fires and does nothing.

1. **Edges reference node `id`, never `label`.** Give every node an `id`
   (or let the server assign `node_1`, `node_2`). A label in an edge matches
   nothing.
2. **Every `agent_action` needs `agent_id` and `prompt_template`.** The
   label is a caption for people. Without a prompt the agent runs a
   placeholder.
3. **`source_handle` (`"true"` or `"false"`) belongs only on edges leaving a
   `condition` node.**
4. **Every workflow needs a trigger node.**
5. Give nodes distinct `position` values, or omit them and the server lays
   them out top to bottom.

The graph is validated when you save it. If the call fails, the message names
each problem: fix them and call again.

Minimum shape that runs:

```json
{
  "nodes": [
    {"id": "trigger", "type": "schedule_trigger", "label": "Monthly on the 1st",
     "config": {"cron": "0 9 1 * *"}},
    {"id": "write", "type": "agent_action", "label": "Draft the recap",
     "config": {"agent_id": "blog-writer",
                "prompt_template": "Summarise last month's published posts in 200 words."}}
  ],
  "edges": [{"source": "trigger", "target": "write"}]
}
```

## Node types

- **Triggers**: `schedule_trigger` (`cron`), `data_trigger` (`entity_type`,
  `event_type`), `webhook_trigger`, `pipeline_source` (only a person deploys a
  workflow that has one).
- **Agent and model steps**: `agent_action`, `llm_prompt`, `code_job`.
- **Control flow**: `condition` (`expression`), `for_each`, `sub_workflow`,
  `merge`, `delay` (`delay_seconds`; it only waits time), `escalation` (the
  approval checkpoint: the run pauses until a person responds; `targetMode`
  supervisor, position or domain).
- **Data steps**: `upsert_record`, `delete_record`, `http_request`,
  `send_notification`, `webhook_response`, `javascript`, `html_extract`.
- **Transforms**: `transform_map`, `transform_filter`, `transform_mask`,
  `transform_enrich`, `transform_script`, `transform_lookup`,
  `transform_sort`, `transform_dedupe`, `transform_split`,
  `transform_aggregate`, `transform_limit`.

An `agent_action` may carry `modelOverride` (`provider`, `preferred`,
`thinkLevel`, `maxTokensPerCall`, `maxTokenBudget`; blank fields inherit) to
run that one step on a different model.

## Lifecycle

`draft` -> (a person approves the deploy) -> `deployed` -> `paused`.

1. `adl_create_workflow` saves a draft.
2. `adl_get_workflow` to check the structure.
3. `adl_deploy_workflow` requests deployment. **Every deploy waits for a
   person's approval.** Until then the workflow is a draft that has never
   run. Never report it as deployed or live.
4. `adl_trigger_workflow` runs a deployed workflow on demand, also after a
   person approves.
5. `adl_list_workflow_runs`, `adl_get_workflow_run` to check what happened.

Editing a deployed workflow: `adl_update_workflow` with the **full** `nodes`
and `edges` arrays (a partial array deletes what you left out). The edit is
saved as a draft version and the deployed version keeps running until you
deploy again (`has_undeployed_changes`). Do not pause a workflow just to edit
it: pausing removes its schedule. `adl_pause_workflow` is for retracting one
that misbehaves.

## When a run fails

Do not ask anyone for logs. In order:

1. `adl_get_workflow` for the definition.
2. `adl_list_workflow_runs` to find the failed run.
3. `adl_get_workflow_run`: each failed step carries `failure` with `class`,
   `code`, `message` and `fix`. Diagnose from `failure.code` first.
4. Fix with `adl_update_workflow`, then `adl_deploy_workflow` (and say it is
   waiting for approval).

Common codes:

- `model_not_priced`: the agent's model has no price on file. Set
  `modelOverride` on the step, or propose a model change for the agent with
  `adl_propose_agent_model`. Read the agent first with `adl_get_agent_model`.
- `provider_out_of_credits`: that provider's key hit its cap. Override the
  step to a provider the workspace has another key for.
- `provider_error`: retry once; if it repeats, override the step's model and
  report it.
- `unresolved_tool_error`: the step result names the tool; fix the prompt's
  arguments against that tool's schema.

## Triggers

`adl_create_trigger` runs an agent with a prompt template when an entity
event matches a condition. Creating, updating (`adl_update_trigger`) and
deleting (`adl_delete_trigger`) all wait for a person's approval, and you can
change only triggers you created. Prefer `enabled: false` over deleting when
the pause is temporary.

## Outside

`sb_automation`: `workflow_*` (create, update, deploy, undeploy, trigger,
runs, cancel, retry), `workflow_import_analyze` / `workflow_import` (convert
an exported n8n workflow into a draft; credentials are stripped and listed as
connections to add), `schedule_*` (cron schedules that run a workflow or chat
with an agent), and `llm_*` (provider keys and models).
