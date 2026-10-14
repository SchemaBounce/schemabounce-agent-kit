# Recording a proposal (version 0)

Record a proposal only when the person you work for asks for one or agrees to
it. In a hosted Code Mode session you cannot record; put the proposal in your
final message instead.

## Choosing the id safely

The server does not assign decision ids yet, and an existing **proposed**
record can be overwritten by a write to the same id. On 2026-10-14 one
session overwrote another's proposal this way. Until the server assigns ids:

1. Find the highest existing id: `records_get` upward from the newest id you
   know until one returns not found.
2. Immediately before writing, `records_get` your chosen id again. If it now
   exists, take the next one and check again.
3. Never write to an id that exists, and never edit someone else's proposal.

## The write

`sb_adl` `records_upsert`, `entity_type: "decision"`, your `entity_id`, and
`data` with at least:

- `title`, `statement`, `context`, `consequences`
- `status: "proposed"` (nothing else is accepted on create)
- `domains` (the coarse areas it governs), `visibility: "workspace"`
- `proposedBy` (who you are and on whose direction), `proposedAt` (today)
- `supersedes` (ids it would replace, if any), `relatedDecisions`, `sources`

Write the statement as the ruling itself, in plain sentences. Put reasons in
`context` and effects in `consequences`.

## After writing

Tell the person the id and that it waits for them in the Inbox under
Proposals. Do not describe it as accepted until you have read the record and
seen `status: "accepted"`.
