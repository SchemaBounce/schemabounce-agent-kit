# SchemaBounce decisions

SchemaBounce records its rulings as **decision records** (`dec-NNN`) in the
Context Engine of its decision workspace. An **accepted** decision is the
authority for its subject. When a document, a comment or your own memory
disagrees with an accepted decision, the decision wins and the other text is
the bug.

## The rules

1. **Look before you change governed things.** Before a change to
   architecture, pricing, security, licensing, infrastructure, product
   behaviour or an agent or code-session rule, find the accepted decisions
   that apply and follow them. Skip the lookup for a change that touches none
   of these: a typo, formatting, a test-only change.
2. **Current authority only.** Use decisions whose `status` is `accepted`.
   Ignore `superseded` and `rejected` ones. When decision A lists B in
   `supersedes`, only A counts. A `proposed` decision is not binding yet.
3. **Cite.** Name the ids you relied on (`dec-048`) in your plan, your report
   and your commit message.
4. **Conflict means stop.** Stop only when an accepted decision's statement
   clearly forbids the change or requires the opposite. Do not code around it:
   say which decision and why, and offer a proposal that would supersede it. A
   match that is only topical is not a conflict; say so and continue.
5. **Read status, never remember it.** A person accepts or rejects a proposal
   whenever they like and nothing tells you. Read the record in the same turn
   before you state its status or ask anyone to ratify it.
6. **Propose, never ratify.** Record a proposal only when the person you work
   for asks or agrees, with the `sb_decision` propose action, which assigns the
   id (see [references/decisions-proposing.md](references/decisions-proposing.md)). Only a person
   with ratification authority accepts or rejects one. Never write `accepted`,
   `rejected` or `superseded` yourself; the server refuses it anyway.
7. **Accepted decisions never change.** A correction is a new proposal whose
   `supersedes` lists the old id. Merging several similar decisions works the
   same way: one proposal that supersedes all of them.
8. **Signed out is not silence.** If the MCP is signed out or unreachable, say
   so and do not guess which decisions apply.

## The edit hook, and when to call `context` yourself

In Claude Code and Cowork the SchemaBounce agent kit plugin ships a `PreToolUse` hook on `Edit`,
`Write` and `MultiEdit`. Before each edit it asks the SchemaBounce MCP which
accepted decisions govern the file and adds them to your context, with their
ids. When you see them, follow and cite them. When nothing appears, the file
has no classified decision, or the MCP is signed out or unreachable: the hook
fails quietly, so silence is not proof that nothing applies. claude.ai chat
loads no hooks: there, call `context` yourself.

The hook does not run at session start, and it sees one file at a time. Call
`sb_decision` `context` yourself (`repository`, `paths`, optional `topics`
and `query`) at **task start** with the files you expect to touch, and again
**before you write a plan** that changes governed things. Use `budget_tokens`
to cap the answer and `cursor` to page when `more` is set.

## Finding the decisions that apply

`sb_decision` has `context` (the decisions that govern given files or topics),
`search` (by words in title and statement), `get` (one record) and `lineage`
(what a decision replaced and what replaced it). Prefer them. If the tool or an
action is missing in your workspace, use the hosted MCP's `sb_adl` tool for
lookups and keep results small:

1. **Known ids**: `sb_adl` `records_get` with `entity_type: "decision"` and
   `entity_id: "dec-NNN"`. Exact and cheap. Use it to read status.
2. **By subject**: `sb_adl` `search` with `entity_types: ["decision"]`, a
   precise query naming the subject (for example "personal Claude
   subscription in hosted code sessions"), and `limit` 5. Results are full
   records and can be large; read title, status, statement and supersedes,
   and drop anything not accepted.
3. Search is relevance-ranked and limited. An empty or all-non-accepted
   result is not proof that no decision applies. Say "I found no accepted
   decision for <your query>", never "no decision governs this".

What a record holds, and how to write a proposal: see
[references/decisions-record-fields.md](references/decisions-record-fields.md) and
[references/decisions-proposing.md](references/decisions-proposing.md).

## In a hosted Code Mode session

Your SchemaBounce MCP access is read-only. You can read and cite decisions but
not record one. If your work needs a new decision, write the proposed
statement in your final message, marked as a proposal, so the person can
record it.

## Inside a SchemaBounce agent

The same rules apply with the agent's own tools:

- `adl_decision_context`: the decisions that govern the topics or files you
  are about to touch, as compact cards. Call it before you act in a governed
  area.
- `adl_decision_search`: find decisions by words. Accepted only by default;
  pass `status` to see proposals and history. When its `strategy` says
  `ilike`, an empty answer only means no text matched.
- `adl_decision_propose`: record a proposal (Starter plan and higher). It is
  always created `proposed`; only a person ratifies it in the Inbox.
- A status changes without notice. Search again right before you state one.
