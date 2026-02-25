# Fix Prompt Template

Reference for generating actionable fix prompts from test results.

## Purpose

Fix prompts are copy-paste-ready instructions that can be sent to another Claude session to fix issues found during skill testing. They should be:

- **Self-contained** - All context needed to understand and fix the issue
- **Actionable** - Clear what needs to change
- **Specific** - References exact file, section, and content
- **Copy-paste ready** - User can literally copy and paste to fix

## Template Structure

```markdown
## Fix: [Concise Issue Title]

**Severity:** [CRITICAL / HIGH / MEDIUM / LOW]

**Problem:** [One sentence explaining the issue]

**File:** [Full path to the file that needs modification]
**Section:** [Section name, heading, or line number reference]

**Current behavior:**
[Quote or describe what's happening now that's wrong]

**Required change:**
[Clear description of what needs to change]

**Suggested fix:**
```
[The actual modified content - what to add, change, or remove]
```

---
Copy the prompt above and send to the agent that maintains this skill.
```

## Severity Guidelines

| Severity | When to Use |
|----------|-------------|
| CRITICAL | Unprompted actions, data loss risk, security issues |
| HIGH | Inconsistent output structure, missing key features |
| MEDIUM | Optional sections vary, minor format differences |
| LOW | Wording variance, cosmetic issues |

## Examples by Issue Type

### Unprompted Actions (CRITICAL)

```markdown
## Fix: Skill Creates Files Without Permission

**Severity:** CRITICAL

**Problem:** Skill writes to user's filesystem without asking for confirmation.

**File:** ~/.claude/skills/example-skill/SKILL.md
**Section:** Phase 3: Output Generation

**Current behavior:**
Skill directly creates/updates files like AGENTS.md or config files without user approval.

**Required change:**
Add explicit instruction requiring user confirmation before any file operations.

**Suggested fix:**
Add to the Output Generation section:
```
## File Operations Safety

NEVER write, create, or modify files without explicit user confirmation.

Before any file operation:
1. Show the user what you intend to write
2. Ask: "Would you like me to create/update [filename]?"
3. Wait for explicit approval before proceeding

If user hasn't confirmed, DO NOT write any files.
```

---
Copy the prompt above and send to the agent that maintains this skill.
```

### Inconsistent Output Structure (HIGH)

```markdown
## Fix: Optional Section Appears Inconsistently

**Severity:** HIGH

**Problem:** "Observations" section appears in some runs but not others.

**File:** ~/.claude/skills/example-skill/SKILL.md
**Section:** Output Format

**Current behavior:**
No explicit instruction about whether Observations section is required or optional.

**Required change:**
Make output structure explicit - either always include or never include.

**Suggested fix:**
Update the Output Format section to include:
```
## Required Output Sections (in order)

1. Summary - Always include
2. Findings - Always include
3. Observations - Always include (even if empty, state "No additional observations")
4. Recommendations - Always include
5. Next Steps - Always include

Do NOT add sections not listed above. Do NOT omit any required section.
```

---
Copy the prompt above and send to the agent that maintains this skill.
```

### Trigger Phrase Behavior Variance (MEDIUM)

```markdown
## Fix: Different Triggers Produce Different Scope

**Severity:** MEDIUM

**Problem:** "analyze last 10" vs "analyze all" triggers different data scope.

**File:** ~/.claude/skills/example-skill/SKILL.md
**Section:** Description / Workflow

**Current behavior:**
Trigger phrase wording affects how much data is analyzed, leading to inconsistent results.

**Required change:**
Document expected behavior or normalize scope handling.

**Suggested fix:**
Add to Workflow section:
```
## Scope Handling

Default scope: Last 50 conversations (unless user specifies otherwise)

If user says:
- "last N conversations" → Analyze exactly N
- "all conversations" → Analyze all available
- No scope specified → Use default (50)

All trigger phrases should respect scope the same way.
```

---
Copy the prompt above and send to the agent that maintains this skill.
```

### Missing Permission Check (HIGH)

```markdown
## Fix: Skill Doesn't Verify Required Files Exist

**Severity:** HIGH

**Problem:** Skill assumes files exist without checking, causing silent failures.

**File:** ~/.claude/skills/example-skill/SKILL.md
**Section:** Phase 1: Setup

**Current behavior:**
Skill proceeds with analysis even when required data files are missing.

**Required change:**
Add pre-flight check for required files.

**Suggested fix:**
Add to Phase 1:
```
## Pre-flight Checks

Before proceeding, verify:
1. Required directories exist
2. Data files are accessible
3. Minimum data threshold is met

If any check fails:
- Report the specific issue to the user
- Do NOT proceed with partial data
- Suggest how to resolve the issue
```

---
Copy the prompt above and send to the agent that maintains this skill.
```

## Best Practices

### DO

- Reference exact file paths
- Quote the problematic behavior when possible
- Provide concrete replacement text
- Keep fixes concise - match existing skill tone
- Make fixes self-contained (don't require reading other docs)

### DON'T

- Write vague instructions like "improve this"
- Use dramatic language ("critical", "extremely important", "must always")
- Exaggerate severity or impact - state facts plainly
- Combine multiple unrelated fixes in one prompt
- Leave the suggested fix ambiguous

## Generating Fix Prompts

When generating fix prompts from test results:

1. **One issue = One prompt** - Don't combine multiple issues
2. **Read the actual skill** - Quote real content, don't guess
3. **Be specific about location** - Section name + what comes before/after
4. **Test your fix mentally** - Would this actually solve the issue?
5. **Consider side effects** - Could the fix break something else?
