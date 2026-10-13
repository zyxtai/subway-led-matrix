---
name: learn
description: Update a repository work log with completed changes, validation, and lessons learned. Use when asked to record project learning or before opening a pull request when repository instructions require it.
---

# Learn

Record the work and useful lessons from the current change in the repository's work log.

1. Read the repository instructions and existing log. Use the path specified by the repository; otherwise use an existing work log or `docs/progress.md` if none exists.
2. Review the current diff and available validation results. Record only work actually completed and checks actually performed; distinguish pending work and unverified assumptions.
3. Add a concise dated entry describing what changed and why, validation results, and any useful lessons, decisions, or remaining issues. Use the user's local date when available. Preserve the existing format and history, and update an entry for the same change instead of duplicating it on retries. Keep each Markdown paragraph and list item on a single source line, except code blocks and diagrams.
4. Review the entry against the final changes. Include the log update in the PR branch before opening the PR. If the change materially evolves after logging, refresh the entry before opening it.

When repository instructions require this skill before PR creation, apply it before any PR-creation command or API call, including draft PRs. If the log cannot be updated or included in the branch, stop PR creation and explain the blocker. Running this skill does not itself authorize committing, pushing, or opening a PR.
