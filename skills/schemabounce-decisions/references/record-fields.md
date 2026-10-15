# Decision record fields

A decision is a Context Engine record with `entity_type: "decision"` and
`entity_id: "dec-NNN"`. Its fields live in `data` and use camelCase.

| Field | Meaning |
|---|---|
| `title` | Short name of the ruling. |
| `statement` | The decision itself. Numbered clauses when it has several. |
| `status` | `proposed`, `accepted`, `rejected` or `superseded`. Only `accepted` binds. |
| `context` | Why it came up and what was weighed. |
| `consequences` | What it commits to and what it rules out. |
| `domains` | Coarse areas (architecture, pricing, security, product, ...). |
| `visibility` | `workspace`, `domain:<id>` or `private`. |
| `proposedBy`, `proposedAt` | Who raised it and when. |
| `decidedBy`, `decidedAt` | Who ratified it and when. Written by the server only. |
| `ratifiedContentHash` | Hash of the content that was accepted. Written by the server only. |
| `supersedes` | Ids this decision replaces. |
| `supersededBy`, `supersededAt` | Set on a decision that a later one replaced. |
| `relatedDecisions` | Cross-references that do not replace anything. |
| `sources` | Repo paths or URLs of the narrative behind it. |
| `reviewBy` | When it should be looked at again, if set. |

The server enforces the lifecycle: a new record can only be `proposed`;
only the ratification route, used by a person with authority, moves it to
`accepted` or `rejected`, or an accepted one to `superseded`; accepted content
cannot be edited. Treat `decidedBy`, `decidedAt` and `ratifiedContentHash` as
read-only.
