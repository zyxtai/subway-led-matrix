# Work Log

## 2026-10-10 — Development workflow

- Updated the project plan to make Visual Studio Code the primary development environment while allowing alternatives such as Arduino IDE.
- Removed hard line breaks within project-plan paragraphs and list items; verified the text content and fenced code blocks were preserved.
- Revised the setup status to start fresh and verify the board's current state, treating the earlier bootloader result as a historical observation.
- Renamed the document title to Project Plan and updated its preservation instruction to reference `docs/PROJECT_PLAN.md`.
- Added a repository rule requiring the `learn` skill to update this log before opening any PR, including draft PRs, with the log update included in the PR branch.
- Installed the reusable `learn` skill in `~/.codex/skills/learn` and recorded the preference for natural Markdown wrapping in `AGENTS.md`.
- Validated the skill frontmatter and UI metadata with Ruby YAML parsing. The bundled Python validator could not run because PyYAML is unavailable; no application tests were needed for these documentation changes.
- Before opening the PR, applied the `learn` skill to review this entry against the branch changes and confirmed `git diff --check origin/main...HEAD` passed. The `learn` skill is installed locally; other contributors will need to install it to follow the PR workflow.
