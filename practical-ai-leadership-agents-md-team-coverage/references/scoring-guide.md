# AGENTS.md Scoring Guide

How to evaluate existing AGENTS.md files against the golden template.

## Quick Scoring Checklist

### Tier 1: Core (Must Have) — 50 points

| Check | Points | How to Verify |
|-------|--------|---------------|
| Commands in first 50 lines | 21 | Grep for code blocks with build/test/lint |
| Agent Permissions section | 17 | Look for Allowed/Ask First/Never headers |
| Project Structure | 12 | Count directory entries (need 5-15) |

### Tier 2: High-Impact — 35 points

| Check | Points | How to Verify |
|-------|--------|---------------|
| Performance guidance | 8 | N+1 prevention, batching patterns |
| Error handling patterns | 8 | Code examples for error handling |
| Domain rules | 7 | Business constraints documented |
| Security section | 6 | Secrets, auth, input validation |
| Concurrency patterns | 6 | If applicable to the domain |

### Tier 3: Workflow — 15 points

| Check | Points | How to Verify |
|-------|--------|---------------|
| Conventions | 5 | Naming patterns documented |
| Testing section | 5 | Test commands and patterns |
| Doc links | 5 | References to README, parent AGENTS.md |

## Scoring Process

### Step 1: Read the File

```bash
cat path/to/AGENTS.md | head -100
```

### Step 2: Check Commands Section

**Pass (21 points):** Commands section exists within first 50 lines with:
- At least one build/compile command
- At least one test command
- Formatted as code block

**Partial (10 points):** Commands exist but buried or incomplete

**Fail (0 points):** No commands section

### Step 3: Check Agent Permissions

**Pass (17 points):** Has all three subsections:
- Allowed / Do Without Asking
- Ask First
- Never

**Partial (8 points):** Has some permission guidance but not structured

**Fail (0 points):** No permission boundaries defined

### Step 4: Check Project Structure

**Pass (12 points):** 5-15 directory entries with descriptions

**Partial (6 points):** Structure exists but incomplete

**Fail (0 points):** No structure section

### Step 5: Check Performance

**Pass (8 points):** Contains:
- N+1 query prevention
- Batching/pagination guidance
- Domain-specific optimizations

**Partial (4 points):** Generic performance advice

**Fail (0 points):** No performance section

### Step 6: Calculate Total

Sum all section scores. Apply penalties:

| Issue | Penalty |
|-------|---------|
| File > 300 lines | -10 |
| No code examples | -5 |
| Outdated tech references | -10 |
| Conflicting rules | -3 each |

## Score Interpretation

| Score | Grade | Recommendation |
|-------|-------|----------------|
| 80-100 | Excellent | No changes needed |
| 60-79 | Good | Add 1-2 missing sections |
| 40-59 | Fair | Add Commands, Permissions, Performance |
| 20-39 | Poor | Significant additions needed |
| 0-19 | Critical | Near-complete rewrite |

## Example Scoring

### File: domains/payment/AGENTS.md (Before)

```markdown
# Payment Domain - AI Agent Guide

**For comprehensive documentation**, see README.md.
**For repository setup**, see main README.
**For general guidelines**, see main AGENTS.md.

## Domain Purpose
The payment domain handles billing...
```

**Score Breakdown:**
- Commands: 0 (missing)
- Permissions: 0 (missing)
- Structure: 0 (missing)
- Performance: 0 (missing)
- Domain rules: 2 (brief mention)
- **Total: ~15 (Critical)**

### File: domains/payment/AGENTS.md (After)

```markdown
# Payment Domain — AGENTS.md

## Purpose
Handles billing, subscription management...

## Commands
[code block with yarn commands]

## Project Structure
[7 directory entries]

## Agent Permissions
### Allowed
### Ask First
### Never

## Performance
[N+1 prevention, batching]

## Domain Rules
[Amounts in cents, state machine]

## Security
[PCI compliance, no logging tokens]
```

**Score Breakdown:**
- Commands: 21
- Permissions: 17
- Structure: 12
- Performance: 8
- Domain rules: 7
- Security: 6
- **Total: ~71 (Good)**
