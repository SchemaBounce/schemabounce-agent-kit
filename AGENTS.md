# Working on the SchemaBounce agent kit

This file is for agents and people changing this repository. The rules the
kit teaches other repositories live in `skills/` and `templates/`.

- **Public repository.** Never commit credentials, tokens, customer data,
  internal hostnames beyond the public MCP URL, or conversation content.
- **Portable skills.** Skills use the open Agent Skills format: frontmatter
  `name` (matches the directory, lowercase, hyphens), `description`, and
  optionally `license`, `compatibility`, `metadata`. Keep `SKILL.md` short and
  move detail into `references/`, which loads only when read.
- **One source.** `templates/` text is the same rules as the skills, written
  for agents that do not load skills. Change both together.
- **Accuracy over intent.** Describe what the hosted SchemaBounce MCP does
  today. Label anything planned as planned, with its phase in
  `docs/DESIGN.md`.
- **Versions.** Bump `version` in `.claude-plugin/plugin.json` and the
  marketplace entry together; consumers update only when it changes.
- **Writing.** Short declarative sentences, no em dashes, no hype words.
- **Branches.** Work goes to `development`; nothing is committed or pushed to
  `main` by an agent.
