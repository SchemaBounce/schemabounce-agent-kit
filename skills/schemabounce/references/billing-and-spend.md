# Budgets, spend limits, credits and model rates

Every cost figure comes from the platform. Never quote a price, a model rate
or a plan limit from memory, and never compute a limit yourself.

## What controls spend

- **Workspace spend limit**: a soft limit sends an alert, a hard limit stops
  further agent spend for the period. Buying credits never raises a limit.
- **Budgets**: policies on a workspace, environment, domain, agent, group of
  agents or goal, measured in dollars, credits or pipeline events, over a
  daily, weekly, monthly, rolling 30 day or lifetime window, with warning
  levels and an optional hard stop. A budget with a hard stop refuses new
  runs at its limit.
- **Per-run cap and wake cap**: limits on a single run and on how often
  agents are woken. Agents and most members cannot change them.
- **Code sessions** have their own budget per session (see
  [references/code-sessions.md](references/code-sessions.md)).

When a run stops on a budget, its failure class says `budget_exceeded`.
Report which budget and its limit as returned; lifting it is a person's
decision.

## Reading costs

- Outside: `sb_billing` `rate_card` returns what each model costs right now
  and which model each `*_latest` alias resolves to. When a model has no rate,
  report tokens, not a guessed dollar figure.
- `credits_usage` aggregates model usage (by model by default);
  `credits_ledger` lists credit movements.
- Inside: `adl_get_agent_metrics` returns runs, tokens and estimated cost per
  agent or for the workspace.

## Changing plans and limits (outside, people only)

`sb_billing`: `inspect`, `plans`, `change_plan`, `add_addon` /
`remove_addon`, `checkout_url`, `portal_url`, `spend_limits_get` /
`spend_limits_set`, `budgets_*`. Every change that can cost money or stop
spend asks for confirmation.

Model provider keys and which model an agent runs on: `sb_automation`
`llm_*`, and `sb_agent` for the agent's own model settings.
