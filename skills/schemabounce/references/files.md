# Files

The workspace has a file store that people and agents share. Files are
versioned, quota-checked and text-indexed.

## Reading

- `adl_list_files`: what you can read, filtered by scope (`northstar`,
  `workspace`, `domain`, `private`) or path prefix. Each row has a `url` for
  people.
- `adl_read_file`: the extracted text of a document or PDF. If it says
  `extraction_pending`, read again later (at most 3 times in a run).
  `extraction_failed`, `extraction_unsupported` and `quarantined` are final.
- `adl_view_image_file`: look at an image (receipt, screenshot, diagram,
  form) with a vision model.
- A file you cannot see answers `not_found`. That is access, not a bug: ask
  with `adl_request_file_access` and a specific reason. A person decides in
  the Inbox. Never ask another agent to paste a file you were refused.

## Writing

| You have | Use |
|---|---|
| A document a person will read (report, summary, draft) | `adl_write_file` as Markdown or plain text |
| A PDF or Word document to deliver | `adl_write_file` the Markdown, then `adl_render_file` |
| Many records a person wants as a spreadsheet or data file | `adl_export_records` (CSV, XLSX, JSON, NDJSON) |
| An uploaded data file whose rows belong in records | `adl_import_records` |
| Findings another agent should act on | a record, not a file |

- **Ownership**: a file you write belongs to you and the people who supervise
  you. Pass `scope: workspace` only when every member and every agent should
  read it.
- **Versions**: writing the same name into the same folder adds a version.
  Pass `file_id` to version a specific file, or `on_conflict: fail` to refuse.
- **Rendering** is asynchronous. The result is the target file with status
  `uploading`; it is usable only when `adl_list_files` (use `path_prefix`)
  shows it `ready`. You cannot write a PDF or Word file directly: text with
  a `.pdf` or `.doc` name is rejected.
- **Export and import** run on the server, so rows never pass through your
  context. Always run `adl_import_records` with `dry_run: true` first, check
  the detected columns, then import with a `mapping` if needed. Set
  `entity_id_column` when the file has a natural key so a re-import updates
  instead of duplicating.

## Delivering

- People in the workspace open files in the Files browser. Give them the
  file's `url`.
- `adl_share_file` makes a time-limited public link (default 72 hours, at
  most 7 days) for someone outside the workspace. Creating it waits for a
  person's approval; sending it anywhere is a separate approved action. The
  link is a secret: put it in the delivery message only.
- To give a file to a connected tool, pass `{"$file": "<file id>"}` as the
  argument. Never make a public link for that.
- `adl_send_slack_file` sends a file into the Slack thread that started the
  conversation, after a person approves it.

## Deleting

`adl_delete_file` erases the file and its encryption key permanently. It
waits for a person's approval; report each id's outcome exactly as returned
(`deleted`, `not_found`, `forbidden`, `failed`).

Outside: `sb_ops` `files_*` (list, get, text, upload as base64 up to 12 MiB,
render, delete, grants, search, quota).
