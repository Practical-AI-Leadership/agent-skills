---
name: practical-ai-leadership-project-init
description: This skill should be used when the user asks to "initialize a project", "create a new project", "set up project structure", "scaffold a project", "init project", "start a new project in this repo", or wants to create a project with folder structure, documentation, AGENTS.md, and vendor-specific AI agent entry points.
version: 1.0.0
---

# Project Initialization

Initialize new projects with folder structure, documentation, AGENTS.md, and vendor-specific AI agent files. Creates a solid foundation for any software project that uses AI coding assistants.

Extract any user-provided arguments as initial project description context. Pre-fill interview questions with relevant information (project name, purpose) when available.

## Initialization Workflow

Copy this checklist and track progress:

- [ ] Phase 1: Gather project information
- [ ] Phase 2: Gather project context
- [ ] Phase 3: Select AI coding agents
- [ ] Phase 4: Create folder structure
- [ ] Phase 5: Create AGENTS.md and vendor files

### Phase 1: Gather Project Information

**STOP AND ASK if:** path does not exist or answers conflict.

Use AskUserQuestion to collect:

1. **Project path** — Relative to repo root (e.g., `projects/my_project_backend`, or `.` for root).
2. **Project name** — Human-readable (e.g., "My Project Backend").

### Phase 2: Gather Project Context

Collect context for documentation. Accept "TBD" or empty answers — incomplete context is better than blocking.

1. **Problem statement** — What problem does this project solve? (1-2 sentences)
2. **Success criteria** — How to measure success.
3. **Current state** — Greenfield, partial implementation, improving existing system.
4. **Tech stack** — Languages, frameworks, key dependencies.
5. **Stakeholders** — Who is affected or interested.
6. **Constraints** (optional) — Time, budget, tech, team constraints.
7. **Related work** (optional) — Related projects, repos, or documentation.

### Phase 3: Select AI Coding Agents

Use AskUserQuestion with multiSelect. Available agents and their vendor files are listed in `references/vendor-files.md`.

### Phase 4: Create Folder Structure

**Project root is `{PROJECT_PATH}/`** — verify with the user if ambiguous.

Create core folders:

```bash
mkdir -p {PROJECT_ROOT}/docs/project_phases
mkdir -p {PROJECT_ROOT}/docs/concept
mkdir -p {PROJECT_ROOT}/docs/expert_consultations
mkdir -p {PROJECT_ROOT}/docs/work_packages
```

Create `docs/README.md` using the template in `references/folder-templates.md`, populated with Phase 2 context.

**No source code directories** — only create docs/ folders. Never create src/ or tests/.

### Phase 5: Create AGENTS.md and Vendor Files

Create `AGENTS.md` at project root using the template in `references/agents-md-template.md`, populated with Phase 1-2 information.

Create vendor-specific files for each agent selected in Phase 3. Each vendor file references AGENTS.md with the correct relative path. See `references/vendor-files.md` for exact paths and content.

Update `README.md` to link to AGENTS.md:

```markdown
Agent quickstart: see [AGENTS.md](AGENTS.md) for the minimal checklist before editing.
```

## Finalization

After creating all files:

1. Verify: AGENTS.md starts with `Parent context:`. Each vendor file links to AGENTS.md with correct relative path. `docs/README.md` exists and links to `../README.md` and `../AGENTS.md`.
2. List created files and folder structure.
3. Confirm: "Project initialized. Your project foundation is ready."

## Important Rules

1. **Check base path exists** — Create parent directories if needed.
2. **Use clickable markdown links** — `[AGENTS.md](AGENTS.md)`, not backticks.
3. **Traceability everywhere** — Every file links to its parents.
4. **Always use AskUserQuestion** — Gather all information through questions, not assumptions.
5. **Date format** — Always YYYY-MM-DD.
6. **No source code structure** — Only docs/ folders.

## Additional Resources

- **`references/folder-templates.md`** — docs/README.md template with placeholder fields
- **`references/agents-md-template.md`** — AGENTS.md generation template with traceability header
- **`references/vendor-files.md`** — Vendor-specific file paths, content, and relative path patterns
