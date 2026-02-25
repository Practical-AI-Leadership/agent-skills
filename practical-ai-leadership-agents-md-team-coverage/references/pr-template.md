# PR Description Templates

Templates for creating pull requests when improving AGENTS.md files.

## Backend Repository Template

```markdown
## Description

Improves AGENTS.md files for {Team}'s high-activity backend domains by adding critical sections required by the AGENTS.md golden template.

**Files improved ({count}):**
{for each improved file}
- `{path}` — {what was added: Commands, Permissions, etc.}
{end for}

**Files created ({count}):**
{for each new file}
- `{path}` — {domain description}
{end for}

**Sections added to each file:**
- **Commands** — yarn fix, compile, test commands (21% weight in scoring)
- **Agent Permissions** — Allowed/Ask First/Never boundaries (17% weight)
- **Performance** — N+1 prevention, batching patterns (7.9x AI error multiplier)
- **Domain Rules** — Business logic constraints
- **Security** — Domain-specific security guidance

These improvements help AI coding assistants (Claude Code, Cursor, Copilot) understand project conventions and constraints before making changes.

## Related issues

- Part of {Team} AI Coding Assistance Adoption initiative

## QA Test Cases

1. Open each modified/created AGENTS.md file and verify:
   - Commands section appears in first 50 lines
   - Agent Permissions has three subsections (Allowed/Ask First/Never)
   - Performance section has actionable guidance
   - Domain Rules reflect actual business constraints
2. For improved files, verify existing valuable content was preserved
3. Confirm markdown formatting is correct and links work
```

## Flutter Repository Template

```markdown
## Description

Improves AGENTS.md files for {Team}'s high-activity feature packages by adding critical sections required by the AGENTS.md golden template.

**Files improved ({count}):**
{for each improved file}
- `{path}` — {what was added}
{end for}

**Sections added to each file:**
- **Commands** — Build, test, and code generation commands (21% weight in scoring)
- **Agent Permissions** — Allowed/Ask First/Never boundaries (17% weight)
- **Performance** — Flutter-specific optimization patterns (7.9x AI error multiplier)

These improvements help AI coding assistants (Claude Code, Cursor, Copilot) understand project conventions and constraints before making changes.

## Related issues

- Part of {Team} AI Coding Assistance Adoption initiative

## How to QA?

1. Open each modified AGENTS.md file and verify:
   - Commands section appears in first 50 lines
   - Agent Permissions has three subsections (Allowed/Ask First/Never)
   - Performance section has actionable guidance
2. Verify existing content was preserved (not overwritten)
3. Confirm markdown formatting is correct

### Affected areas

{for each file}
- `{package path}` — {Package name} documentation
{end for}
```

## Commit Message Template

```
docs: improve AGENTS.md files for {Team} {areas}

{Summary of what was added/improved}

{If improved files}
Improved existing AGENTS.md files:
{list}

{If created files}
Created new AGENTS.md files:
{list}

All files now follow the AGENTS.md golden template with:
- Commands section in first 50 lines
- Agent Permissions (Allowed/Ask First/Never)
- Performance guidance
- Domain-specific rules
```

## PR Title Patterns

| Scenario | Title Pattern |
|----------|---------------|
| Single repo, improvements only | `Improve AGENTS.md files for {Team} {areas}` |
| Single repo, new + improvements | `Improve and add AGENTS.md files for {Team} {areas}` |
| Multiple domains | `Improve AGENTS.md files for {Team} domains` |
| Multiple packages | `Improve AGENTS.md files for {Team} features` |

## Reviewer Assignment

Pair reviewers by domain expertise:

| PR Content | Assign Reviewers |
|------------|------------------|
| Backend domains | Backend team members |
| Frontend packages | Frontend team members |
| Mixed | All technical team members |
| Documentation only | Team lead |
