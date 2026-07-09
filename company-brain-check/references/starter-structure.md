# Starter Structure — Mode 2 Recommendation

## Table of Contents

- [The starter tree](#the-starter-tree)
- [Why each element exists](#why-each-element-exists)
- [Seeding rules](#seeding-rules)
- [The growth rule](#the-growth-rule)
- [Adapting without breaking the principles](#adapting-without-breaking-the-principles)

## The starter tree

```
<workspace-root>/
├── README.md                  # what this workspace is + map of its areas
├── AGENTS.md                  # how AI agents navigate and behave here
└── projects/
    ├── <project-name>/        # one folder, one concern — kebab-case name
    │   ├── README.md          # purpose, current status, where details live
    │   └── docs/
    │       ├── README.md      # doc map for this project
    │       ├── concept/       # the ideas the project is built on, interlinked
    │       └── decisions/     # dated decisions with their context
    └── _archive/              # finished projects move here, whole
```

Present the tree with the `<project-name>` slots replaced by the user's real concerns (one or two current projects), so the recommendation reads as *their* structure, not a template.

## Why each element exists

Deliver these reasons with the tree — a structure adopted without its reasons decays into empty folders:

- **Root `README.md`** — the single place a human starts. States what the workspace is and links every top-level area. Without it, orientation cost is paid by every reader, every time.
- **Root `AGENTS.md`** — the single place an agent starts: navigation directions ("client work lives under `projects/`, one folder per concern") plus the ground rules agents must follow. One file at the root serves every AI tool that reads agent instructions; project-level agent files are added only when a project develops rules of its own.
- **`projects/` with one folder per concern** — the unit of the whole system. One concern = one folder means one place to look, one place to archive, one shape for automations to rely on.
- **Per-project `README.md`** — purpose, current status, and links into `docs/`. The project is legible without opening its internals.
- **`docs/concept/`** — the ideas the project is built on: the offer, the architecture, the method. Interlinked, so dependent concepts point at their foundations instead of re-explaining them.
- **`docs/decisions/`** — dated decisions with the context that produced them. Keeps "why is it like this?" answerable a year later without archaeology.
- **`projects/_archive/`** — finished work moves here whole. Separation keeps dead projects out of live context — for readers and for agents that would otherwise treat a 2-year-old plan as current truth.

Two conventions travel with the tree:

- **Every doc links to its parent** — a first line like `Parent: [README.md](../README.md)` makes the tree navigable in both directions: READMEs' downward links are what the navigation probe (mode 1, dimension 6) follows, and parent links are the way back up from any doc an agent lands in.
- **Docs describe current state** — plans live in clearly named planning docs; everything else reads as what *is*. This is dimension 5 of the check, built in from day one.

## Seeding rules

When the user confirms scaffolding:

- Create the folders and seed `README.md` / `AGENTS.md` with **real content gathered from the user**: workspace purpose in one sentence, the first project's name and one-line purpose, its current status. Ask for what is missing.
- Never seed placeholder text ("TODO: describe project"). A brain born with placeholder rot fails dimension 5 before it holds a single idea.
- Seed only the folders the first real project needs. `concept/` and `decisions/` may start empty of files but must not start with stub files.

## The growth rule

Recommend starting with **one project folder done properly** — real README, one real concept doc, links wired — rather than scaffolding the full tree for everything the user might ever do. Structure earns trust by being used, and twenty empty folders are aspiration, not structure. The second project copies the first one's shape; that is the moment the repeating-structure dimension starts existing.

## Adapting without breaking the principles

The tree is a default, not a doctrine. Folder names may change (`clients/` instead of `projects/`, a German-named tree, an Obsidian vault where folders are sections); what must survive any adaptation:

1. One folder, one concern.
2. An entry point at every root (human + agent).
3. Docs that link to each other and to their parents.
4. The same shape repeated across concerns.
5. Current-state writing, plans quarantined in planning docs.
6. A fresh agent can navigate from the root entry point to any doc by links alone.

Those six survive because they are the six dimensions mode 1 grades — the starter structure is simply the smallest layout that passes its own check.
