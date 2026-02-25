# Skill Extraction Example

This example demonstrates extracting a skill from a conversation about creating project phase artifacts.

---

## The Original Conversation (Summary)

**User Request:**
"Help me create work packages and implementation plans for my project"

**What Happened:**
1. User asked to create work packages
2. Claude gathered context about the project
3. Created phase overview document
4. Created work package documents
5. Created implementation plan documents
6. User asked to make this reusable

**Key Phrases Used:**
- "work on a project phase"
- "create a work package"
- "create an implementation plan"
- "break down this work"
- "phase planning"

---

## Extraction Analysis

### Step 1: Goal Identification

| Element | Extracted Value |
|---------|-----------------|
| Goal | Create project phase artifacts |
| Outcome | Phase overview, work packages, and implementation plans |
| Trigger | "work on a project phase", "create a work package" |
| Domain | Project management / Phase development |

### Step 2: Process Extraction

**Workflow that emerged:**

1. Detect available project commands
2. If no command exists, guide to `/init-project`
3. Gather context about what to create (detective mode)
4. Confirm artifact type (phase, WP, or plan)
5. Create the artifact with proper structure
6. Update parent artifacts with references
7. Validate cross-references

### Step 3: Component Identification

**References identified:**
- Templates for each artifact type
- Patterns for context gathering
- Naming conventions

**Examples identified:**
- Complete phase overview example
- Complete work package example

**Scripts identified:**
- None needed (all operations via tools)

### Step 4: Scope Definition

**Handles:**
- Phase overviews (P{N})
- Work packages (P{N}-WP-{NN})
- Implementation plans (P{N}-PLAN-{NN})

**Does NOT Handle:**
- Consultations
- Experiments
- Other project artifacts
- Project initialization

---

## Resulting Skill Structure

```
project-phase-development/
├── SKILL.md
├── references/
│   ├── templates.md
│   └── patterns.md
└── examples/
    ├── example-phase-overview.md
    └── example-work-package.md
```

---

## SKILL.md Frontmatter (Extracted)

```yaml
---
name: project-phase-development
description: This skill should be used when the user asks to "work on a project phase", "create a work package", "create an implementation plan", "start phase development", "develop project phase", "define phase overview", "break down this work into packages", "plan the implementation", "scope the phase", "create WP", "create PLAN", "phase planning", or mentions working on phases, work packages, or implementation plans.
version: 0.1.0
---
```

Note how the trigger phrases came directly from user language in the conversation.

---

## Key Patterns Extracted

### Detective Mode Pattern

Before creating any artifact:
1. Ask identity questions (what is this?)
2. Ask purpose questions (why does it exist?)
3. Ask scope questions (what does it cover?)
4. Ask detail questions (how does it work?)
5. Ask connection questions (how does it relate?)

### Naming Convention Pattern

```
Phase:    P{N}
WP:       P{N}-WP-{NN}
Plan:     P{N}-PLAN-{NN}
```

### Cross-Reference Pattern

```
Phase Overview
├── Work Package 01
│   └── Implementation Plan 01
├── Work Package 02
│   └── Implementation Plan 02
```

---

## 3-Step Workflow Execution

### Step A: skill-development

Created skill using skill-development guidance:
- Proper frontmatter with trigger phrases
- Lean SKILL.md (under 2,000 words)
- References for detailed content
- Examples from actual work

### Step B: skill-reviewer

Reviewer findings:
- Description included good trigger phrases ✓
- Content used imperative form ✓
- Progressive disclosure applied ✓
- Resources properly referenced ✓

### Step C: skill-testing

Test triggers used:
- "work on a project phase" → ✓ Triggered
- "create a work package" → ✓ Triggered
- "create an implementation plan" → ✓ Triggered

No overlap with other skills confirmed.

---

## Lessons Learned

1. **Extract actual user phrases** - Don't invent triggers, use what user said
2. **Narrow scope early** - Initial version was too broad, had to narrow
3. **Check for overlap** - One trigger phrase overlapped with another skill
4. **Test promptly** - Testing revealed needed trigger adjustments
5. **Complete all 3 steps** - Each step caught different issues

---

## Before/After Comparison

**Before (no skill):**
- Recreate process each time
- Remember all patterns manually
- No consistent structure
- Risk missing steps

**After (with skill):**
- Process documented and triggered
- Patterns available when needed
- Consistent artifact structure
- Validation built in
