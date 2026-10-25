# Repository Instructions

## Work log before pull requests

Before opening any pull request, including a draft PR, use the `learn` skill to update `docs/progress.md` with the completed changes, their purpose, validation results, and any useful lessons or remaining issues.

Use the repository-owned skill at `.agents/skills/learn/SKILL.md`, even if a personal skill with the same name is installed. Read that file directly if it is not already available in the session's skill list. If the file is missing, restore it before proceeding; do not silently skip this requirement.

Include the work log update in the PR branch before running a PR-creation command or API call. Refresh the entry if the change materially evolves, and avoid duplicate entries when retrying. If logging or including the update is blocked, do not open the PR; report the blocker.

## Markdown formatting

Keep each paragraph and list item on a single source line so the editor can wrap it naturally. Preserve intentional line breaks in code blocks and diagrams.

## Shared Codex skills

Keep project-specific Codex skills in `.agents/skills/<skill-name>/` and commit their `SKILL.md`, UI metadata, and any required supporting resources alongside the project changes. The repository copy is the source of truth for this project's workflows.

## Privacy

Use the GitHub handle @zyxtai for contributor references. Use “the selected station” for the home station and keep its name and platform IDs out of tracked files. Store station selection only in ignored local settings.toml; use synthetic station IDs in tests.
