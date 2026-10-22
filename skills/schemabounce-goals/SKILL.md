---
name: schemabounce-goals
description: Use when you create, change, measure or report on a SchemaBounce goal, key result, outcome metric, North Star or org-chart domain goal, or when someone asks whether a number shows on a goal or domain page. Covers how a goal is measured and how to read it back before saying it is done.
compatibility: Needs the hosted SchemaBounce MCP (https://mcp.schemabounce.com/mcp) signed in to the workspace that owns the goals. Reading needs view access. Declaring a metric, capturing a snapshot and creating or changing a goal are writes and need write access. Hosted Code Mode sessions have it read-only.
metadata:
  kit: schemabounce-agent-kit
  version: 0.4.2
---

# SchemaBounce goals and outcome metrics

SchemaBounce goals say what a workspace, a domain or an agent is trying to
achieve, and prove progress with numbers the platform measures itself. The
rulings behind this are decision records dec-059 and dec-042 in your
workspace, if you can read them (see the `schemabounce-decisions` skill).

## The pieces

- **North Star**: the workspace's one standing goal with no parent. Every
  other goal sits under it.
- **Goal**: level `workspace`, `domain` or `agent`. A **domain** is an
  org-chart group of agents and people, shown on the Domains page.
  Horizon `deliverable` (it finishes) or `standing` (it never finishes and
  carries an on track or off track verdict).
- **Key result**: a target on one declared outcome metric. It names the
  metric by its key, plus a target value and a direction.
- **Outcome metric**: a declared number with a source, a direction (`up` or
  `down` is good), an attribution window and a caveat class. Today the
  source is a query over records the workspace already holds. Snapshots
  capture its value with a timestamp; progress reads them.

## The rules

1. **Only two things move a goal.** Key results that use a declared outcome
   metric, and tasks linked to the goal. A goal with neither has no
   progress. It is not measured, and you say so.
2. **Only those two feed progress.** Memory notes, files, messages and the
   goal's own description text do not. Never tell anyone a number appears on
   a goal because you wrote it somewhere; read the goal back.
3. **Measure what is already recorded.** Declare the metric over records
   that are written anyway, capture a first snapshot as the baseline, then
   attach it as a key result. The call sequence and a worked example are in
   [references/measuring-a-goal.md](references/measuring-a-goal.md).
4. **Read back before you report.** After you attach a key result, read the
   goal again and report what the read shows: the key result, its metric and
   the progress the server resolved. A key result reads `unresolved` until
   its metric has a snapshot.
5. **The server computes progress.** Never calculate or round your own
   percentage or verdict, and never present one as the platform's. If the
   server returns no progress or `unresolved`, report that as the result.
6. **Writes need a yes.** Declaring a metric, capturing a snapshot and
   creating or changing a goal (`goal_create`, `goal_update`) change the
   workspace. Do them only when the person you work for asks or agrees.
7. **Signed out is not silence.** If the MCP is signed out or unreachable, say
   so and do not guess a goal's progress.

## Where people see it today

- The **Goals** page shows each goal with its key results and progress, and
  lets a person declare a metric or link one.
- A domain's page has a **Health** tab with the domain's runs, tasks
  and agents. Ask the person what they expect to see there before you
  promise it.

## In a hosted Code Mode session

Your SchemaBounce MCP access is read-only. You can read goals and metrics but
not declare, snapshot or change one. Put the metric and key result you would
add in your final message, marked as a proposal, so the person can do it.
