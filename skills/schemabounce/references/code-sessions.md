# Code sessions and repositories

A code session is a coding agent working in a GitHub repository in a hosted
sandbox: it edits, runs checks, commits and pushes a branch, and can open a
pull request. It needs a paid plan, a connected GitHub repository and a free
session slot.

## Read the code first

- `adl_list_repos`: repositories the workspace's GitHub connection reaches,
  with default branches. Call it before you ask anyone which repository.
- `adl_repo_list_files`, `adl_repo_read_file`, `adl_repo_search_code`: browse,
  read and search a repository so the paths and names you put in a prompt
  are real. Read-only.

## Run a session (inside an agent)

1. `adl_start_code_session` with a clear `prompt` (what to change, how to
   check it, what done means). The repository comes from `repo`, else the
   linked task, else the last repository this agent coded in. Every start
   waits for a person's approval in the Inbox.
2. Do not set a wait for your own session: you are woken when it finishes,
   fails or needs a person.
3. `adl_code_session_status`: state, branch, pull request, failure reason,
   spend against budget, and `lastTurn` (tests run, commits, files changed).
   Read `lastTurn` first. `adl_code_session_events` gives the play-by-play.
4. When it waits on a decision (a tool approval, a question, a plan, a push),
   only a person can make it, in the Inbox. Tell them; never approve it
   yourself.
5. `adl_push_code_session` commits and pushes while the session is still
   open, and opens a pull request with `open_pr`. Unless the workspace
   turned push approval off, it waits for a person. The pull request targets
   the session's base branch.
6. `adl_continue_code_session` retries a session you started that failed,
   was cancelled or expired, from its last checkpoint, with a `note` on what
   to do differently. Starting a new session starts the work over.

A session started from a Linear issue uses the repository mapped to the
issue's team; leave `repo` out.

## Who pays

A session runs on a coding subscription whenever one is available: the
requesting person's own subscription, then a seat the workspace holds on the
provider's team plan, then a sponsor's. Only when none is available does it bill the workspace's
API key or credits, and that start is held for a person who sees the model,
its rate, the budget cap and a typical cost before approving. Billing mode
and license kind are shown on the session.

## Report honestly

- A session that never reached a push has no branch or pull request.
- `review.unavailable` means the platform reviewer did not run, not that a
  person reviewed it.
- Never say a person decided something unless a field says so.

## Outside

`sb_code_session`: `create`, `status`, `context`, `events`, `diff`,
`result`, `push` and `cancel` (each asks for a typed confirmation phrase),
`interrupt` (stop the current turn, keep the session), `continue`, `rerun`,
`approvals_respond` (decide a held tool call as the signed-in person),
`compute_budget`.
