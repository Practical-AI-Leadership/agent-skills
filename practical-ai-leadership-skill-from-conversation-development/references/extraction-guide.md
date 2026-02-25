# Conversation Extraction Guide

Detailed techniques for analyzing conversations and extracting reusable skills.

---

## Conversation Analysis Techniques

### Reading the Conversation History

When analyzing a conversation, look for:

**User Intent Signals:**
- Initial request phrasing
- Clarification questions asked
- Satisfaction indicators ("that's exactly what I needed")
- Iteration requests ("can you also...")

**Process Markers:**
- Sequential steps taken
- Tools used repeatedly
- Decision points where choices were made
- Validation/verification moments

**Knowledge Patterns:**
- Information gathered before acting
- References consulted
- Patterns applied
- Rules followed

### Identifying Repeatable vs One-Off Tasks

**Repeatable (good for skills):**
- Generic process that applies to multiple instances
- Clear inputs and expected outputs
- Consistent steps regardless of specific content
- Would benefit from captured knowledge

**One-Off (not suitable for skills):**
- Highly specific to one situation
- Requires unique context each time
- No generalizable pattern
- Better solved ad-hoc

### Extraction Questions by Phase

**Phase 1: Goal Identification**

| Question | Purpose |
|----------|---------|
| What did the user ultimately want? | Core goal |
| Why did they want it? | Motivation/context |
| What would trigger this need again? | Activation phrases |
| What domain is this? | Categorization |

**Phase 2: Process Mapping**

| Question | Purpose |
|----------|---------|
| What was the first step? | Entry point |
| What decisions were made? | Branching logic |
| What tools were used? | Technical requirements |
| How was success verified? | Validation criteria |
| Were there iterations? | Refinement patterns |

**Phase 3: Knowledge Extraction**

| Question | Purpose |
|----------|---------|
| What information was needed? | Domain knowledge |
| What patterns were followed? | Best practices |
| What mistakes were avoided? | Anti-patterns |
| What could have gone wrong? | Error handling |

---

## Component Identification

### Determining What Becomes Scripts

Create scripts when:
- Same code written repeatedly
- Deterministic output required
- Parsing/validation needed
- File manipulation involved

**Script Candidates from Conversations:**
- Validation logic that was written
- Parsers that were created
- Generators that were built
- Utilities that were used

### Determining What Becomes References

Create references when:
- Domain knowledge was consulted
- Patterns were explained
- Templates were used
- Standards were followed

**Reference Candidates from Conversations:**
- Explanations given during work
- Patterns that were applied
- Templates that were used
- Best practices followed

### Determining What Becomes Examples

Create examples when:
- Complete working output exists
- Real usage demonstrated
- Copy-and-modify useful
- Structure matters

**Example Candidates from Conversations:**
- Final outputs created
- Working configurations
- Complete implementations
- Templates filled in

---

## Trigger Phrase Extraction

### Mining User Language

Extract phrases the user actually used:

1. **Initial Request:** How did they start?
   - "I want to..."
   - "Can you help me..."
   - "I need to..."

2. **Refinements:** How did they clarify?
   - "I mean..."
   - "What I want is..."
   - "Like this..."

3. **Domain Terms:** What vocabulary?
   - Technical terms used
   - Domain-specific language
   - Abbreviations/acronyms

### Phrase Transformation

Turn user phrases into trigger patterns:

| User Said | Trigger Phrase |
|-----------|---------------|
| "I want to create a hook" | "create a hook" |
| "Help me set up a new phase" | "set up a new phase" |
| "Can you make me a skill" | "make a skill" |
| "I need to validate this" | "validate" |

### Broadening Triggers

Add related phrases:

| Core Trigger | Related Triggers |
|--------------|-----------------|
| "create a hook" | "add a hook", "new hook", "hook setup" |
| "work on phase" | "phase development", "start phase", "create phase" |
| "extract skill" | "make skill", "turn into skill", "save as skill" |

---

## Scope Definition

### Narrowing Scope

A skill should have focused scope:

**Too Broad:**
```
Handles all project management tasks
```
Problem: Overlaps with many skills

**Too Narrow:**
```
Creates Phase 2 work packages for AIPT project
```
Problem: Too specific, rarely triggered

**Just Right:**
```
Creates phase overviews, work packages, and implementation plans for any project
```
Benefit: Focused but generalizable

### Overlap Detection

Before creating a skill, check for:

1. **Existing Skills:**
   - List skills in `.claude/skills/`
   - Read their descriptions
   - Identify potential overlap

2. **Overlap Patterns:**
   - Same trigger phrases
   - Same domain
   - Same operations

3. **Resolution:**
   - Narrow new skill scope
   - Extend existing skill instead
   - Combine into broader skill

---

## Quality Indicators

### Signs of a Good Skill Candidate

| Indicator | Meaning |
|-----------|---------|
| User said "I do this often" | Repeatable |
| Multiple steps were needed | Substantive |
| Domain knowledge applied | Valuable |
| Clear success criteria | Verifiable |
| Generic process emerged | Transferable |

### Signs of a Poor Skill Candidate

| Indicator | Meaning |
|-----------|---------|
| Highly specific context | Not generalizable |
| Simple single step | Too trivial |
| No clear pattern | Ad-hoc |
| Context-dependent decisions | Hard to capture |
| Rarely needed | Low value |

---

## Extraction Workflow

### Step-by-Step Process

```
1. Summarize conversation goal
   ↓
2. Identify repeatable process
   ↓
3. Extract trigger phrases
   ↓
4. List reusable components
   ↓
5. Define scope boundaries
   ↓
6. Check for overlap
   ↓
7. Plan skill structure
   ↓
8. Execute 3-step workflow
```

### Deliverables at Each Step

| Step | Deliverable |
|------|-------------|
| 1. Goal | One-sentence goal statement |
| 2. Process | Numbered step list |
| 3. Triggers | 5-10 trigger phrases |
| 4. Components | Scripts/references/examples list |
| 5. Scope | What it handles and doesn't |
| 6. Overlap | Confirmed no conflicts |
| 7. Structure | Directory and file plan |
| 8. Creation | Complete skill via 3-step workflow |

---

## Common Extraction Scenarios

### Scenario: Process Automation

User completed a multi-step process successfully.

**Extract:**
- Sequential steps as workflow
- Validation checks as requirements
- Files modified as patterns
- Commands used as scripts

### Scenario: Knowledge Application

User needed domain knowledge to complete task.

**Extract:**
- Knowledge applied as references
- Decisions made as patterns
- Terms explained as glossary
- Standards followed as guidelines

### Scenario: Template Creation

User created something from scratch.

**Extract:**
- Final output as template
- Structure as pattern
- Variations as examples
- Customization points as parameters

---

## Integration with 3-Step Workflow

### Before skill-development

Have ready:
- [ ] Goal statement
- [ ] Process steps
- [ ] Trigger phrases
- [ ] Component list
- [ ] Scope definition

### During skill-development

Apply extraction to:
- Frontmatter: Use trigger phrases
- Body: Document process
- References: Store knowledge
- Examples: Include outputs

### After skill-reviewer

Address feedback on:
- Trigger quality
- Content organization
- Writing style
- Resource references

### During skill-testing

Verify:
- Triggers from conversation activate skill
- Process steps are followable
- Knowledge is accessible
- Examples are useful

---

## Checklist for Extraction

**Conversation Analysis:**
- [ ] Goal clearly identified
- [ ] Process steps documented
- [ ] Trigger phrases extracted
- [ ] Components categorized

**Skill Planning:**
- [ ] Scope defined
- [ ] No overlap confirmed
- [ ] Structure planned
- [ ] Name decided

**3-Step Execution:**
- [ ] skill-development invoked
- [ ] skill-reviewer completed
- [ ] skill-testing validated
- [ ] All issues resolved
