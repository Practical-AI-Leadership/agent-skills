---
name: company-brain-check
description: This skill should be used when the user asks to "check my company brain", "grade my company brain", "run the company brain completeness check", "how complete is our knowledge base", "assess our knowledge base structure", "audit our knowledge repository structure", "set up a company brain", or "recommend a starter structure for our knowledge base". Grades the structural completeness of a company or personal knowledge repository — the place where projects, concepts, and conventions live — across six dimensions plus additional checks (mode 1), or recommends a generalizable starter structure when no structured knowledge base exists yet (mode 2). Runs at a repository or workspace root in Claude Code or Claude Cowork. Not for reviewing source-code quality, not for writing or editing documentation content, and not for auditing a single document's prose.
version: 1.1.1
---

# Company Brain Check

A company brain (or personal brain) is the repository where projects, concepts, and conventions live — the foundation AI agents, automations, and new teammates read from. This check grades the brain's **structure**, not the quality of its prose: can a fresh agent (or a fresh hire) land at the root and find its way alone?

Two modes, auto-detected:

- **Mode 1 — a brain exists.** Grade its completeness across six core dimensions plus additional checks, with evidence for every finding.
- **Mode 2 — nothing structured exists yet.** Recommend a basic, generalizable starter structure and offer to scaffold it.

## Ground Rules

- **Mode 1 is read-only inside the graded tree.** Never create, modify, move, or delete a file inside the brain being graded. The one file Mode 1 writes is the report, saved *outside* the graded tree (see `references/report-format.md`). Mode 2 scaffolds files only after the user explicitly confirms — a recommendation the user has not seen is not consent to write it.
- **Every finding cites a real path**, relative to the root (never machine-absolute — reports get pasted into chats and tickets, where absolute paths break both portability and privacy). A verdict without a checkable path is an opinion, not a finding. If something cannot be verified (unreadable folder, tool limits), report it as "not checked" rather than guessing either way.
- **Overview depth, not a rewrite.** Name each gap, why it matters, and the first move to close it. Never rewrite the user's documents or prescribe tool choices — the principles apply whether the brain lives in a git repo, Notion, or Obsidian (run wherever the files are readable as a folder tree).

## Workflow

1. **Establish the root and take inventory.** Confirm the root in one line ("Checking: `<root>`"), then inventory three levels deep, skipping machine folders and stating any sample on large workspaces. Mechanics: `references/scanning-and-modes.md`.
2. **Detect the mode.** Apply the rule ladder in `references/scanning-and-modes.md` — including the scope gate: if the root does not read as a knowledge repository, confirm intent with the user before grading. State the detected mode and the rule that fired.
3. **Mode 1 — grade.** Read `references/check-rubric.md` and grade each of the six dimensions **Solid / Partial / Missing** (Projects as units · Entry points · Interlinked concept docs · Repeating structure · Current-not-aspirational · Machine-readability), then the four additional checks. Every verdict needs an evidence line with a real path or a scan-derived count; draw findings only from what the scan observed, never from the rubric's illustrative examples.
4. **Mode 2 — recommend.** Read `references/starter-structure.md` and present the starter tree adapted to the user's real concerns, the one-line "why" per element, and the growth rule. Offer to scaffold; create files only on explicit confirmation, seeded with real content, never placeholders.
5. **Review gate (both modes).** Before presenting anything, run the synchronous adversarial review in `references/review-gate.md` — spawn a fresh sub-agent, wait for its verdict, fix findings (at most 2 cycles).
6. **Present the report.** Two tiers: a full report saved to a file the user can open, and a short plain-language chat summary linking to it. Section contracts and the save-location rule: `references/report-format.md`. Output voice (no jargon, plain words, verifiable actions): `references/output-style.md`.

## Intent

- Evidence over impression: a dimension with mixed signals gets Partial with both signals cited — never rounded up to Solid because the workspace "feels organized" or down to Missing to seem rigorous.
- Read-only trust > proactive helpfulness: in mode 1, never "fix a small thing while at it" — the moment the check edits what it grades, its verdicts stop being trustworthy; and treating an unconfirmed mode-2 scaffold as helpful initiative is the same failure.
- A plausible root is not necessarily the brain: when the workspace reads as a pure source-code repo, a home directory, or anything else that mismatches "knowledge repository", confirm the intended scope with the user before grading — a correct report on the wrong scope is still a wrong report.
- Overview depth > exhaustive depth: three gaps the user will actually act on beat fifteen findings that overwhelm. When the scan surfaces more, cut to the highest-leverage few rather than listing them all.
- Honest sampling > false completeness: a stated sample outranks an implied full scan; "not checked" outranks a guessed verdict.
- Generalizable > prescriptive: recommendations name structural principles (entry points, one-folder-one-concern), never a specific tool, vendor, or company-specific convention.
- "Good" = a report where every verdict survives the Step 5 re-verification untouched and each first move names a concrete next action — a specific file to create or link to fix, not a category of work. "Good enough" = all six dimensions graded with cited evidence and the top-3 attention list actionable, even if additional checks carry "not checked" entries on tool limits.

## Additional Resources

- **`references/scanning-and-modes.md`** — Step 1–2 mechanics: inventory rules, the sampling formula, and the mode-detection rule ladder (incl. the scope gate).
- **`references/check-rubric.md`** — Mode 1 grading: per-dimension signals, Solid/Partial/Missing criteria, the navigation probe, the four additional checks, each dimension's one-line "why it matters", and report wording examples.
- **`references/starter-structure.md`** — Mode 2 starter tree with the why behind each element, seeding rules, and the growth rule.
- **`references/review-gate.md`** — Step 5 adversarial-review prompt and the fix-and-re-run procedure.
- **`references/report-format.md`** — Step 6 two-tier structure, the save-location rule, and the mode-1 / mode-2 output contracts.
- **`references/output-style.md`** — output voice: no internal jargon in the chat summary, plain words, concise-over-complete, and the verifiable-action bar for every recommendation.

---

*Tested on a working knowledge base with 100+ documented project folders (2,000+ Markdown docs) and on an empty workspace.*
