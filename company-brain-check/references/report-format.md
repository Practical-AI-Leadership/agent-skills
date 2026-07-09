# Report Format

Step 6 of the check. The report ships in **two tiers**: a full report saved to a file (6a), and a short, plain-language chat summary that links to it (6b). Read `references/output-style.md` alongside this file — that governs voice (jargon, word choice, the verifiable-action bar); this file governs structure, save location, and the section contracts.

## 6a — Write the full report to a file

Assemble the full report using the mode-1 or mode-2 contract below, then save it to a file the user can reliably open.

### Where to save

The report must never land inside the graded tree, and never in an ephemeral spot the user can't open. In the usual run the graded root **is** the session's working directory, so writing `./…` would drop the file into the very brain being graded — which breaks the read-only guarantee and pollutes the next scan. So:

- **Default: ask the user where to save**, naming a folder they have open (e.g. a `reports/` folder in a different project they are working from). One short question beats a wrong guess. If the folder they name is inside the brain being graded, keep the report out of it and say why — it would otherwise show up in the next scan as if it were part of the brain.
- **If you must choose without asking:** save to the parent of the graded root, or to the session's working directory only when it is genuinely *different* from the graded root (the user pointed the check at another path). State the chosen location in plain words in the chat summary, not just as a link.
- **Never** save to the session scratchpad or any `/tmp` / `/private/tmp` path — those are ephemeral and usually outside the user's open workspace, so the link dies.

### Mode 1 output contract

```
# Company Brain Check — <root name> — <date>

Mode 1 · Graded <sample statement>

**Headline: <N>/6 core dimensions Solid · <M> additional checks flagged**

| # | Dimension | Why it matters | Verdict | Evidence |
|---|-----------|----------------|---------|----------|

## What already looks strong
## What needs attention
(top 3 gaps, each: the gap → why it matters → the first move, stated as a concrete verifiable action)
## Additional checks
## What this check does not cover
```

The **"Why it matters"** column is the fixed one-line plain-language reason carried by each dimension in `references/check-rubric.md` — the same wording every run, not per-workspace evidence. The **Evidence** column leads with the finding in plain language a non-technical reader can act on, then cites **one** supporting path or count — the citation the Ground Rules require — not a pile of field names, IDs, or hashes; if several paths matter, name one here and put the rest in the prose sections. (The stricter no-path rule applies to the chat summary, not this file — see `references/output-style.md`.)

### Mode 2 output contract

```
# Company Brain Check — <root name> — <date>

Mode 2 · <what the scan found, one line>

## Starter structure, adapted to your projects
(the tree, project slots renamed to real concerns)
## Why each element exists
## Growth rule
## Scaffold?
(explicit question — created only on the user's yes)
```

"What this check does not cover" is part of the honesty of the report: structure grading says nothing about whether the content is *good*, and a sampled scan says nothing about unsampled folders. State both.

## 6b — Present the chat summary

After saving the file, present a short summary in chat — the part the user reads at a glance. It must let them see, in one screen, three things: what is strong, what needs attention, and what to do next. Follow `references/output-style.md` strictly: no internal jargon (see its banned-token list), plain words, and an additional check that found nothing does not appear at all.

Chat summary shape (mode 1):

```
Checked <root name>. <N> of 6 core areas solid.

**What looks strong**
- <2-3 plain-language bullets>

**What needs attention**
1. <plain-language gap> → <concrete, checkable action>
2. ...
3. ...

Full report saved in <plain-words location> — <link to the saved file>
```

Mode 2's output is short and interactive already (it ends by asking whether to scaffold) — present it directly in chat under the same plain-language rules; no separate file is needed unless the user asks for one.
