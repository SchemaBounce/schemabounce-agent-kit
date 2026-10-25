# Console pages, docs, attention and platform bugs

## Pointing someone at a console page

Console navigation changes; a path you remember is probably wrong.

- `adl_find_ui_path("api token")`: matches for one question, each with the
  breadcrumb, a ready URL for this workspace, the permission it needs, and
  whether it is enabled. An empty result is a real answer: say you could not
  find it and offer `adl_get_ui_map`.
- `adl_get_ui_map()` (or `adl_get_ui_map("Settings")`): the whole tree or one
  section.

When you answer:

1. Give the breadcrumb and the link, with the workspace id filled in. Never
   leave a placeholder and never invent an id.
2. Name the permission a gated page needs. A member without it sees nothing
   there.
3. Never send anyone to a destination the lookup reports as disabled; say
   why it is unavailable.
4. Prefer a deep link (only the query parameters the result lists) over a
   click-by-click walkthrough.
5. If a tool result carries `url` for the object you touched (a file, a
   workflow, a task, a memory entry), hand that link over instead.

## Citing documentation

`adl_search_docs` searches the published SchemaBounce docs and returns real
titles and URLs. Call it before you answer "how does X work" or paste any
docs link. If it finds nothing, say the docs do not appear to cover it; never
fall back to a guessed URL.

## What needs attention

`adl_workspace_attention` (outside: `sb_workspace` `attention`) lists what
needs a person right now: failed runs grouped by failure class, approvals
waiting, schedules the runtime paused, agents blocked in setup, connections
that need attention. Each item has a severity, the subject id and the console
link for whoever must act. If it says `partial`, a source could not be read:
never report all clear from it.

For one failed run, outside: `sb_agent` `runs_get` returns `failure` with a
class, code, message and a `fix` (label, link and the MCP action that fixes
it). `runs_evidence` gives the run's step timeline.

## Reporting a SchemaBounce bug

`adl_report_schemabounce_bug` is only for a tool result that says
`PLATFORM_FAULT` and gives a `report_ref`: one of SchemaBounce's own services
failed. Pass the `report_ref`; the platform sends the facts it recorded (ids,
names, codes, never conversation content). Refusals, approvals, limits,
missing connections and a tool's own errors are not platform bugs.
