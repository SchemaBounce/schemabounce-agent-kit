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
   waits for a person's approval in the Inbox. Pick `session_type`:
   `read_only` for verification, review or investigation that changes no
   file (a small sandbox, no setup or checks, no push; it completes after one
   turn and its answer is the final message), `content` for docs and posts
   (checks that only cover code are skipped), else `code` (the default).
   `read_only` and `content` run on a Sonnet model unless you name one.
2. Do not set a wait for your own session: you are woken when it finishes,
   fails or needs a person. A start can come back `queued` (every slot the
   plan allows is busy, or no sandbox is free): it starts on its own in
   order, so never start another for the same work.
3. `adl_code_session_status`: state, branch, pull request, failure reason,
   spend against budget, and `lastTurn` (tests run, commits, files changed).
   Read `lastTurn` first. `adl_code_session_events` gives the play-by-play.
4. When it waits on a decision (a tool approval, a question, a plan, a push),
   only a person can make it, in the Inbox. Tell them; never approve it
   yourself. A session that waits more than 10 minutes, or sits idle while
   others are queued, is parked (`awaiting_resume`): its work is saved and
   its sandbox freed. It resumes on its own when the decision lands or a
   sandbox frees, so do not continue it by hand.
5. `adl_push_code_session` commits and pushes while the session is still
   open, and opens a pull request with `open_pr`. Unless the workspace
   turned push approval off, it waits for a person. The pull request targets
   the session's base branch.
6. `adl_continue_code_session` retries a session you started that failed,
   was cancelled or expired, from its last checkpoint, with a `note` on what
   to do differently. Starting a new session starts the work over.

A session started from a Linear issue uses the repository mapped to the
issue's team; leave `repo` out.

## Hand work to a code session (outside)

When you are a coding agent working through the hosted MCP and you need more
workers in parallel than you can run yourself, start code sessions for the
parts that fit instead of more local subagents. Each one runs in its own
sandbox, on the normal billing order, and proves its work with the
repository's own checks.

A part fits when all of these hold:

- It changes one repository the workspace's GitHub connection reaches, and
  that repository's checks (its pipeline, tests, lint) can prove it.
- It needs nothing only your machine has: a local stack or cluster, files
  outside the repository, a browser signed in on your machine, or
  credentials you hold.
- No other worker is changing the same files now.

Keep the work local when the proof needs your environment (deploying to and
driving a local stack, walking a page in a browser), when it is a handful of
tool calls, or when it changes CI workflow files the repository's GitHub app
is not allowed to push.

1. Write the prompt as a brief: the goal, what done means as a check that can
   fail, the files or area it owns, and what it must not touch. Use
   `session_type` `read_only` for an investigation that changes nothing.
2. `sb_code_session` `create`. Billing follows the order in Who pays below.
3. Await it with `wait`, which returns when the session finishes or needs a
   person; keep working meanwhile. A session that comes back `queued` starts
   on its own, so never start a second one for the same work.
4. What it waits on (a plan, a tool approval, a held review, a push) is a
   person's decision in the Inbox. Tell them; never answer it for them.
5. Report from `summary`: the outcome, the landed commit or pull request, the
   checks, the review verdict and the cost, as returned. Read its `diff`
   before you build on its work.

## Continue on your computer, and back

Out: `sb_code_session` `handoff` (`session_id`) returns the repository, the
work branch and whether it is on GitHub, the engine and its session id, the
download path of the one transcript file, and the exact commands. A branch
that is not on GitHub yet is pushed first with `push` (it needs a person's
typed phrase). Then, on the machine: `git fetch origin <branch> && git switch
<branch>`, put the transcript at `~/.claude/projects/<project dir>/<id>.jsonl`
(the project dir is the repository's absolute path with every character that
is not a letter or digit turned into `-`), and run `claude --resume <id>`;
for Codex the rollout file goes under `~/.codex/sessions/<yyyy>/<mm>/<dd>/`
and the command is `codex resume <id>`. Only the conversation file is
exported, never the engine's settings or credentials. Download it with your
SchemaBounce credential; the route is audited.

In: `transcript_upload` returns an `upload_id` and a `put_url` (15 minutes).
PUT your local Claude Code session file (`~/.claude/projects/<project>/<id>.jsonl`,
at most 20 MB, one JSON object per line) to it, push your local branch, then
`create` with `transcript_upload_id` and `base_branch` set to that branch.
The session resumes the conversation. Claude Code only; Codex transcripts are
not supported yet. Never print or paste a transcript into a chat or a log:
it is conversation content.

## Who pays

A session runs on a coding subscription whenever one is available: the
requesting person's own subscription, then a seat the workspace holds on the
provider's team plan, then a sponsor's. Only when none is available does it bill the workspace's
API key or credits, and that start is held for a person who sees the model,
its rate, the budget cap and a typical cost before approving. Billing mode
and license kind are shown on the session.

A session that finished with its work saved but its pull request never
opened (`publishOutcome` `unpublished` or `pr_failed`) raises an Inbox
notice. Outside an agent, `sb_code_session` `publish` opens the pull request
from the branch it already pushed, with no model turn and no cost; work that
exists only in the checkpoint needs `continue` instead.

## Report honestly

- A session that never reached a push has no branch or pull request. A
  `read_only` session never has one: report its final message.
- `review.unavailable` means the platform reviewer did not run, not that a
  person reviewed it.
- Never say a person decided something unless a field says so.

## Outside

`sb_code_session`: `create`, `status`, `context`, `events`, `diff`,
`result`, `summary`, `wait` (bounded: default 45 seconds, at most 270; call
it again while it says `still_running`), `handoff`, `transcript_upload`, `push` and `cancel` (each asks for a typed confirmation phrase),
`interrupt` (stop the current turn, keep the session), `pause`, `resume`,
`continue`, `rerun` (a second rerun while one is open returns that one),
`publish` (open the pull request from the pushed branch, no model cost),
`approvals_respond` (decide a held tool call as the signed-in person),
`compute_budget`. `create` takes `session_type` (`code`, `read_only`,
`content`).
