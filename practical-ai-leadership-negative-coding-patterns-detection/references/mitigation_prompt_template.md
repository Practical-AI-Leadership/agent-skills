# Mitigation Prompt Template

This file describes the structure of the mitigation prompt to generate after scanning. The output prompt is a single markdown file (`NEGATIVE_PATTERNS_MITIGATION.md`) that an AI coding tool can execute to fix all detected anti-patterns.

## Prompt Structure

The generated mitigation prompt must follow this exact structure, section by section.

---

### Section 1: Header

```markdown
# Negative Coding Patterns Mitigation

## Scan Summary

- **Date:** {scan date}
- **Languages scanned:** {comma-separated list}
- **Total anti-patterns found:** {count}
- **Files affected:** {count}
- **Patterns detected:** {count of distinct pattern types}
```

### Section 2: Fix Instructions (one per pattern found, ordered by risk)

Order patterns by risk level: Critical first, then High, then Medium.

For each pattern found, generate this section:

```markdown
---

## Fix: {Pattern Display Name}

**Risk:** {Critical/High/Medium}
**Occurrences:** {count}
**Top file:** `{file_path}:{line_range}`

### Summary

{Why this pattern is bad - from the language reference file's "why_bad" field. 2-3 sentences.}

### Example from Your Code

```{language}
{Actual offending code snippet extracted during scan, with 3-5 lines of surrounding context}
```

### Correct Pattern

```{language}
{Before/after replacement code from the language reference file}
```

### Apply Instructions

1. Fix the top file first (`{top_file}`).
2. Apply the same transformation to the remaining files listed below.
3. Keep changes minimal - avoid refactors unrelated to this pattern.
4. Run verification after each file: pre-commit hooks, linters, tests.

### AI Amplification Risk

If this pattern exists in the codebase, AI assistants will reproduce it in new code.
Fixing it now prevents the pattern from multiplying.

### Files to Fix

- `{file1}:{lines}`
- `{file2}:{lines}`
- ...
```

### Section 3: AGENTS.md Rules

After all per-pattern fix sections, add a consolidated AGENTS.md rules block:

```markdown
---

## AGENTS.md Rules to Add

Add these rules to your project's AGENTS.md (or CLAUDE.md, .cursorrules, etc.) to prevent AI coding tools from reproducing these patterns:

### Coding Conventions

{For each pattern found, include the AGENTS.md rule text from the language reference file. Format as a bulleted list of do/don't rules.}

Example format:
- **Exception handling:** Always catch specific exception types. Never use bare `except:` or `catch (Exception e)` without re-raising. Log with context.
- **Secrets management:** Never hardcode credentials, API keys, or tokens. Use environment variables or a secrets manager.
- **SQL queries:** Always use parameterized queries. Never interpolate variables into SQL strings.
```

### Section 4: Verification

```markdown
---

## Verification Steps

After applying all fixes:

1. Run the project's test suite
2. Run linters and formatters
3. Run pre-commit hooks if configured
4. Verify CI passes
5. Re-run this skill to confirm patterns are resolved
```

## Important Notes for Generation

- Extract actual code from the scanned codebase for the "Example from Your Code" sections. Never use placeholder or hypothetical code.
- Use the before/after code from the language reference files for the "Correct Pattern" sections.
- Include ALL instances found, not just the first few. If more than 20 files for a single pattern, list the top 20 and note the remainder.
- The AGENTS.md rules section must be comprehensive enough that an AI reading it would avoid generating these patterns in new code.
- The entire prompt must be executable by an AI coding tool - write it as clear instructions, not as documentation for humans.
