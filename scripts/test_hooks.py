"""Offline checks for hooks/hooks.json (no network, no MCP).

Run: python3 -m unittest scripts/test_hooks.py

The decision hook must fire for every way an agent changes a file. Prod
cs_bepp438j (core-api #1765) wrote every file through Bash heredocs and python,
so a hook on Edit, Write and MultiEdit alone delivered no decision. The hosted
runner renders the repository into each hook that calls sb_decision with
format claude_code_hook (code-sandbox-runner renderKitHooks), so every such
hook must keep that exact shape.
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load():
    with open(os.path.join(ROOT, "hooks", "hooks.json")) as fh:
        return json.load(fh)["hooks"]


def entry(event, matcher):
    for group in load().get(event, []):
        if group.get("matcher") == matcher:
            return group["hooks"]
    return None


class DecisionHooksTest(unittest.TestCase):
    def test_file_tools_keep_the_pre_edit_hook(self):
        hooks = entry("PreToolUse", "Edit|Write|MultiEdit")
        self.assertIsNotNone(hooks)
        inp = hooks[0]["input"]
        self.assertEqual(inp["file_path"], "${tool_input.file_path}")
        self.assertNotIn("command", inp)

    def test_bash_fires_the_hook_after_the_command_ran(self):
        hooks = entry("PostToolUse", "Bash")
        self.assertIsNotNone(hooks, "files written through a shell must reach the hook too")
        self.assertEqual(len(hooks), 1)
        self.assertEqual(hooks[0]["input"]["command"], "${tool_input.command}")
        self.assertNotIn("file_path", hooks[0]["input"])

    def test_every_hook_is_one_shape_the_runner_can_render(self):
        count = 0
        for event, groups in load().items():
            for group in groups:
                for hook in group["hooks"]:
                    count += 1
                    self.assertEqual(hook["type"], "mcp_tool", event)
                    self.assertEqual(hook["server"], "plugin:schemabounce:schemabounce")
                    self.assertEqual(hook["tool"], "sb_decision")
                    inp = hook["input"]
                    self.assertEqual(inp["action"], "context")
                    self.assertEqual(inp["format"], "claude_code_hook")
                    self.assertEqual(inp["cwd"], "${cwd}")
                    # The engine session, so the server can record which decisions
                    # the hook delivered in which session (audit decision.delivered).
                    self.assertEqual(inp["session_id"], "${session_id}")
                    self.assertLessEqual(hook["timeout"], 10, "a slow hook must not stall a tool call")
        self.assertEqual(count, 2)

    def test_hooks_never_name_a_secret_or_a_repository(self):
        raw = json.dumps(load())
        for word in ("token", "secret", "password", "Authorization"):
            self.assertNotIn(word, raw)
        self.assertNotIn('"repository"', raw, "the platform or the server finds the repository, not the kit")


if __name__ == "__main__":
    unittest.main()
