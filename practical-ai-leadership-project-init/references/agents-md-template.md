# AGENTS.md Template

## Table of Contents

- [Template](#template)
- [Traceability Rules](#traceability-rules)
- [README.md Update](#readmemd-update)

## Template

Create `AGENTS.md` at the project root with this structure:

```markdown
Parent context: [README.md](README.md).

---

## {PROJECT_NAME} Agent Guide

**Problem:** {PROBLEM_STATEMENT}
**Success looks like:** {SUCCESS_CRITERIA}

### Before any change

1. Read this project's `README.md` and `docs` context
2. Understand existing patterns and conventions

### After any change

1. Run linting/formatting on changed files
2. Run static analysis if configured
3. Run pre-commit hooks if configured
4. Run relevant tests
5. Verify changes work locally

### Key architectural notes

- **Architecture pattern:** {ARCHITECTURE_PATTERN}
- **Tech stack:** {TECH_STACK}
- [Add project-specific concepts as they emerge]

### Version bumping rules

- Bump **PATCH** for small fixes with no metric change
- Bump **MINOR** for core functionality changes that affect evaluation
- Bump **MAJOR** for breaking API changes
```

## Traceability Rules

The AGENTS.md must always:
1. Start with `Parent context: [README.md](README.md).` as the very first line
2. Use clickable markdown links (not backticks) for all file references
3. Be linked FROM the project README.md

## README.md Update

After creating AGENTS.md, add this line to README.md (after the first paragraph):

```markdown
Agent quickstart: see [AGENTS.md](AGENTS.md) for the minimal checklist before editing.
```
