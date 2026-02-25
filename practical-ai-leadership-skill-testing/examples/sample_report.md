# Skill Test Report: learn-from-mistakes

## Summary

| Metric | Result |
|--------|--------|
| Consistency | 72% |
| Promise Alignment | 85% |
| Triggers | 3/3 |
| **Verdict** | **WARN** |

## Test Results

| # | Trigger | Status |
|---|---------|--------|
| 1 | "learn from mistakes - analyze last 10" | OK |
| 2 | "analyze corrections and generate rules" | OK |
| 3 | "generate rules for AGENTS.md" | OK |

## Consistency Analysis

### Data

| Metric | T1 | T2 | T3 | Match |
|--------|----|----|----| ------|
| Patterns | 60 | 286 | 286 | Partial |
| Critical | 13 | 40 | 40 | Partial |

*Note: T1 used "last 10" scope, T2-T3 analyzed all.*

### Structure

| Section | T1 | T2 | T3 |
|---------|----|----|---- |
| Summary | Y | Y | Y |
| Patterns | Y | Y | Y |
| Rules | Y | Y | Y |
| Observations | Y | N | N |
| Next steps | Y | Y | N |

## Issues Found

| # | Severity | Issue |
|---|----------|-------|
| 1 | CRITICAL | Unprompted file creation |
| 2 | HIGH | Inconsistent sections |
| 3 | MEDIUM | Scope variance |

---

## Fix Prompts

### Issue 1

```markdown
## Fix: Unprompted File Creation

**Severity:** CRITICAL
**File:** ~/.claude/skills/learn-from-mistakes/SKILL.md
**Section:** Phase 4: Output

**Problem:** T3 created AGENTS.md without asking permission.

**Current:** No explicit permission check before file writes.

**Fix:** Add to Phase 4:
> NEVER write files without explicit user confirmation.
> Always ask: "Would you like me to create [filename]?" and wait for YES.
```

### Issue 2

```markdown
## Fix: Inconsistent Output Sections

**Severity:** HIGH
**File:** ~/.claude/skills/learn-from-mistakes/SKILL.md
**Section:** Output Format

**Problem:** "Observations" and "Next steps" appear inconsistently across runs.

**Current:** No explicit list of required sections.

**Fix:** Add Required Sections list:
> ## Required Output Sections
> 1. Summary table - ALWAYS
> 2. Top patterns - ALWAYS
> 3. Generated rules - ALWAYS
> 4. Observations - ALWAYS (say "None" if empty)
> 5. Next steps offer - ALWAYS
```

### Issue 3

```markdown
## Fix: Trigger Phrase Scope Variance

**Severity:** MEDIUM
**File:** ~/.claude/skills/learn-from-mistakes/SKILL.md
**Section:** Workflow

**Problem:** "last 10" vs no scope produces different data volumes.

**Current:** No default scope documented.

**Fix:** Add to Workflow:
> ## Default Scope
> If user doesn't specify: analyze last 50 conversations.
> If user says "all": analyze all available.
> If user says "last N": analyze exactly N.
```
