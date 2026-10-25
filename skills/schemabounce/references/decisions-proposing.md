# Recording a proposal

Record a proposal only when the person you work for asks for one or agrees to
it. In a hosted Code Mode session you cannot record; put the proposal in your
final message instead.

Two ways exist. Use the propose action when the workspace has it. Use the
fallback only when the tool is absent.

## Preferred: the propose action

`sb_decision` with `action: "propose"` (decision dec-125, if you can read
it). The server picks the
next `dec-NNN` id in one transaction, stamps you as the proposer, and can never
overwrite an existing record. Two proposals made at the same moment get two ids.

Send:

- `title` (160 characters at most), `statement` (1200), `context` (2000),
  `consequences` (2000): all required
- `domains`: at least one coarse area it governs
- optional `supersedes` (ids it would replace), `governed_agent_ids`,
  `sources`, `review_by` (YYYY-MM-DD)

Never send an id, a `status` or a proposer: the server sets them. The reply
carries `decision_id` (the id it assigned) and the stored record, with
`status: "proposed"`.

Afterwards, only you or a person with `adl:decide` can edit the proposal
(`sb_adl` `records_upsert` on that id). Creating a decision with `records_upsert`
is refused and the error names the propose action.

How to tell the workspace has it: `sb_decision` appears in the MCP tool list.
If it does not, use the fallback below.

## Fallback when the `sb_decision` tool is absent

Without the propose action, ids are chosen by the writer and an existing
**proposed** record can be overwritten by a write to the same id, so check
before every write.

### Choosing the id safely

1. Find the highest existing id: `records_get` upward from the newest id you
   know until one returns not found.
2. Immediately before writing, `records_get` your chosen id again. If it now
   exists, take the next one and check again.
3. Never write to an id that exists, and never edit someone else's proposal.

### The write

`sb_adl` `records_upsert`, `entity_type: "decision"`, your `entity_id`, and
`data` with at least:

- `title`, `statement`, `context`, `consequences`
- `status: "proposed"` (nothing else is accepted on create)
- `domains` (the coarse areas it governs), `visibility: "workspace"`
- `proposedBy` (who you are and on whose direction), `proposedAt` (today)
- `supersedes` (ids it would replace, if any), `relatedDecisions`, `sources`

## Writing the content

Write the statement as the ruling itself, in plain sentences. Put reasons in
`context` and effects in `consequences`.

## After writing

Tell the person the id and that it waits for them in the Inbox under
Proposals. Do not describe it as accepted until you have read the record and
seen `status: "accepted"`.
