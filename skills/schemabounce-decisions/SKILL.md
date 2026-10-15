---
name: schemabounce-decisions
description: Use before changing anything a SchemaBounce decision may govern (architecture, pricing, security, licensing, infrastructure, product behaviour, agent and code-session rules), and whenever you report, cite, rely on or propose a decision. Finds the accepted decisions that apply to the change, ignores superseded ones, cites their dec-NNN ids, and proposes new decisions without ever ratifying them.
compatibility: Needs the hosted SchemaBounce MCP (https://mcp.schemabounce.com/mcp) signed in to the workspace that holds the decisions. Hosted Code Mode sessions have it read-only.
metadata:
  kit: schemabounce-agent-kit
  version: 0.4.0
---

# SchemaBounce decisions

SchemaBounce records its rulings as **decision records** (`dec-NNN`) in the
Context Engine of its decision workspace. An **accepted** decision is the
authority for its subject. When a document, a comment or your own memory
disagrees with an accepted decision, the decision wins and the other text is
the bug.

## The rules

1. **Look before you change governed things.** Before you change code,
   configuration, pricing, copy or infrastructure that a decision may govern,
   find the accepted decisions that apply and follow them.
2. **Current authority only.** Use decisions whose `status` is `accepted`.
   Ignore `superseded` and `rejected` ones. When decision A lists B in
   `supersedes`, only A counts. A `proposed` decision is not binding yet.
3. **Cite.** Name the ids you relied on (`dec-048`) in your plan, your report
   and your commit message.
4. **Conflict means stop.** If the change you are asked to make contradicts an
   accepted decision, do not code around it. Say which decision and why, and
   offer to record a proposal that would supersede it.
5. **Read status, never remember it.** A person accepts or rejects a proposal
   whenever they like and nothing tells you. Read the record in the same turn
   before you state its status or ask anyone to ratify it.
6. **Propose, never ratify.** You may record a proposal (with the `sb_decision`
   propose action, which assigns the id; see
   [references/proposing.md](references/proposing.md)). Only a person with
   ratification authority accepts or rejects one. Never write `accepted`,
   `rejected` or `superseded` yourself; the server refuses it anyway.
7. **Accepted decisions never change.** A correction is a new proposal whose
   `supersedes` lists the old id. Merging several similar decisions works the
   same way: one proposal that supersedes all of them.

## The edit hook, and when to call `context` yourself

This plugin ships a `PreToolUse` hook on `Edit`, `Write` and `MultiEdit`. Before
each edit it asks the SchemaBounce MCP which accepted decisions govern the file
and adds them to your context, with their ids. When you see them, follow and
cite them. When nothing appears, the file has no classified decision, or the
MCP is signed out or unreachable: the hook fails quietly, so silence is not
proof that nothing applies.

The hook does not run at session start, and it sees one file at a time. Call
`sb_decision` `context` yourself (`repository`, `paths`, optional `topics`
and `query`) at **task start** with the files you expect to touch, and again
**before you write a plan** that changes governed things. Use `budget_tokens`
to cap the answer and `cursor` to page when `more` is set.

## Finding the decisions that apply (version 0)

The `context`, `search`, `get` and `lineage` actions of `sb_decision` are built
but may not be in production yet. If the tool or action is missing, for lookups, use the hosted MCP's `sb_adl` tool and keep results
small:

1. **Known ids**: `sb_adl` `records_get` with `entity_type: "decision"` and
   `entity_id: "dec-NNN"`. Exact and cheap. Use it to read status.
2. **By subject**: `sb_adl` `search` with `entity_types: ["decision"]`, a
   precise query naming the subject (for example "personal Claude
   subscription in hosted code sessions"), and `limit` 5. Results are full
   records and can be large; read title, status, statement and supersedes,
   and drop anything not accepted.
3. Do not filter on `domains` with `records_query`: list fields do not filter
   today (it returns nothing), and `domains` is too broad to narrow anyway.

What a record holds, and how to write a proposal: see
[references/record-fields.md](references/record-fields.md) and
[references/proposing.md](references/proposing.md).

## In a hosted Code Mode session

Your SchemaBounce MCP access is read-only. You can read and cite decisions but
not record one. If your work needs a new decision, write the proposed
statement in your final message, marked as a proposal, so the person can
record it.
