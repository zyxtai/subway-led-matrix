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

## 2026-10-12 — Phase 0 documentation

- Created `docs/phase-0-foundation` from the merged `main` branch and expanded the README with project goals, repository setup, documentation links, and the branch-and-PR workflow.
- Added `docs/hardware.md`, `docs/wiring.md`, and `docs/decisions.md` using the project plan as the source. Distinguished reported specifications and proposed designs from physically verified results; preserved uncertainty about ordered parts, supply polarity, USB-C power suitability, and the board's current state.
- Documented the smallest next experiment: connect only the controller to the Mac with a USB data cable and record USB detection before choosing or installing firmware. No hardware was connected or tested and no firmware/toolchain was selected or installed during this documentation work.
- Applied the `learn` skill to record the completed changes and review their purpose and limitations. Checked all relative Markdown links and fenced code blocks across the project documents; `git diff --check` passed. No application tests were needed for documentation changes.
- Added the shared `learn` skill and its UI metadata under `.agents/skills/learn/`. Updated repository instructions, the README, and decisions to use the repository copy as the source of truth and require project-specific skills to be version controlled. This removes the need to distribute Ryan's personal installation separately.
- Validated the repository skill's frontmatter and UI metadata with Ruby YAML parsing because PyYAML remains unavailable. Rechecked 11 relative Markdown links and fenced code blocks across eight documents; whitespace checks passed.
- Ran the repository-owned `learn` skill again after commit `f5623b5`: reviewed the complete diff against `origin/main`, confirmed both skill files are tracked, and verified `git diff --check origin/main...HEAD` passed. Updated this entry rather than creating a duplicate.
- Lesson: a PR rule that depends on a personal skill installation is incomplete for a shared repository. Version the skill with the project and explicitly prefer the repository copy so contributors use the same instructions.
- The initial Phase 0 documents are in place. Fresh board verification and toolchain evaluation remain Phase 1 work.
