---
name: practical-ai-leadership-skill-from-conversation-development
description: This skill should be used when the user asks to "create a skill from this conversation", "extract a skill from what we did", "turn this into a skill", "make a skill from this workflow", "capture this process as a skill", "skill from conversation", "save this as a skill", or wants to create a reusable skill based on work accomplished in the current conversation.
version: 0.2.0
---

# Skill from Conversation Development

Extract reusable skills from active conversations where goals have been achieved.

## Purpose

Transform accomplished work in conversations into reusable skills. Analyze the current conversation, present findings to the user, and let them choose which process to capture as a skill.

## Critical Workflow

**DO NOT autonomously decide what to extract.** The workflow is:

1. Analyze conversation → identify potential skill candidates
2. Present findings to user as numbered options
3. Wait for user selection
4. Proceed with selected option only

## Conversation Analysis Process

### Step 1: Analyze and Identify Candidates

Scan the conversation for potential skill candidates. For each candidate, extract:

| Element | What to Find |
|---------|-------------|
| Process Name | Short descriptive name |
| Goal | What was accomplished |
| Workflow | Key steps that emerged |
| Trigger Phrases | User language that initiated this work |
| Repeatability | Is this a one-off or recurring need? |

### Step 2: Present Options to User

**REQUIRED:** Present findings as a numbered table for user selection:

```markdown
Based on this conversation, I found these potential skills to extract:

| # | Candidate | Description | Repeatability |
|---|-----------|-------------|---------------|
| 1 | **[name-1]** | [what it does] | [high/medium/low] |
| 2 | **[name-2]** | [what it does] | [high/medium/low] |
| 3 | **[name-3]** | [what it does] | [high/medium/low] |

Which would you like to turn into a skill? (Enter number, or describe something else)
```

If only one candidate exists, still present it and ask for confirmation.

If no candidates found, explain why and ask what the user had in mind.

### Step 3: Gather Details for Selected Option

After user selects, use the **AskUserQuestion tool** to gather details interactively:

```
Use AskUserQuestion with questions like:
- "What scope should this skill have?" (options: narrow/medium/broad)
- "What output location for generated files?" (options: specific paths)
- "How should the skill handle edge cases?" (options based on context)
```

Tailor questions to the specific skill being created. Use multiSelect where appropriate.

### Step 4: Confirm Before Creating

Present the skill plan and get explicit confirmation:

```markdown
**Skill Plan:**
- Name: [skill-name]
- Triggers: [list of phrases]
- Scope: [what it handles]
- Structure: [files to create]

Proceed with creation? (yes/no)
```

## Mandatory Creation and Validation

After gathering details and confirming the skill plan, invoke the `skill-development` skill which handles the entire creation and validation pipeline:

```
Invoke skill: skill-development
```

The `skill-development` skill owns the entire lifecycle: creation, validation (best practices audit, naming compliance, trigger phrase hardening, consistency testing), registration, and iteration. Do not invoke any of these skills directly.

**GATE: Do not declare "done" or commit until skill-development's full pipeline has passed.**

## Conversation Extraction Checklist

Before creating the skill, verify:

- [ ] Clear goal identified from conversation
- [ ] Repeatable process documented (not one-off task)
- [ ] Trigger phrases extracted from user's language
- [ ] Scope boundaries defined (what it handles/doesn't)
- [ ] No overlap with existing skills identified
- [ ] Components categorized (scripts, references, examples)

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Autonomous selection | User loses control | Always present options, wait for user choice |
| Skipping confirmation | Wrong skill created | Get explicit "yes" before creating |
| One-off task | Not repeatable | Only create skills for recurring processes |
| Too broad | Overlaps everything | Define narrow, specific scope |
| Too narrow | Rarely triggered | Combine related small tasks |
| Missing validation | Quality unknown | Let skill-development run its full Step 5 pipeline |
| Bypassing skill-development | Validation skills called directly, inconsistent | Always go through skill-development which orchestrates all validation |
| Committing before validation | Unreviewed skills in repo | Wait for skill-development to confirm all checks pass |

## Quick Reference

### Extraction Flow
```
Analyze → Present Options → User Selects → Gather Details → Confirm → skill-development (creates + validates)
```

### User Decision Points
1. **Selection** - User chooses which candidate to extract
2. **Scope** - User defines boundaries
3. **Confirmation** - User approves skill plan before creation

### Delegation
All creation and validation is handled by `skill-development` (Steps 1-7), which internally orchestrates best practices audit, naming compliance, trigger phrase hardening, and consistency testing.

### Key Questions (via AskUserQuestion tool)
Use the AskUserQuestion tool for interactive gathering:
- Scope boundaries (narrow/medium/broad)
- Output locations (ask each time vs fixed)
- Behavioral options (auto-execute vs confirm each step)
- Ecosystem support (specific vs general)

## Additional Resources

### Reference Files

For detailed extraction techniques:
- **`references/extraction-guide.md`** - Detailed conversation analysis methods

### Example Files

Working examples:
- **`examples/extraction-example.md`** - Example of skill extracted from a conversation
