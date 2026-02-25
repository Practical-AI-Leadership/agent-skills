# Comparison Methodology

Detailed guide for comparing skill outputs across multiple real Claude CLI runs.

## Comparison Dimensions

### Structural Comparison (60% weight)

Structural elements must be consistent across runs:

| Element | Tolerance | Why |
|---------|-----------|-----|
| Headings | Must match | Defines output structure |
| Sections | Must match | User expects same format |
| File references | Must match | Same files should be mentioned |
| Code blocks | Should match | Deterministic code output |

**How to compare:**
1. Extract all markdown headings (# ## ###)
2. Normalize to lowercase
3. Compare across all 3 outputs
4. Flag deviations where structure differs

### Factual Comparison (40% weight)

Key facts should be consistent:

| Element | Tolerance | Why |
|---------|-----------|-----|
| Numbers | High | Same data = same numbers |
| Percentages | High | Metrics should be stable |
| Recommendations | Medium | Core conclusions should align |
| Examples | Low | LLM may pick different examples |

**How to compare:**
1. Extract all numbers and percentages
2. Extract bullet points and conclusions
3. Calculate overlap between runs
4. Allow some variance for examples/wording

### Wording (Not scored)

LLM outputs naturally vary in phrasing. This is expected and acceptable:

**Acceptable variance:**
- "The skill analyzes..." vs "Analysis is performed..."
- Different transition words
- Slightly different sentence structure

**Not acceptable:**
- Different conclusions
- Missing sections
- Different file references

## Promise Verification (Vibe Check)

High-level check that output relates to skill description.

### Process

1. **Parse SKILL.md frontmatter**
   - Extract `description` field
   - Identify key verbs (create, analyze, generate)
   - Identify key nouns (rules, reports, configurations)

2. **Check output for evidence**
   - Does output mention the key nouns?
   - Does output show the action was performed?
   - Does format match what was promised?

### Example

```yaml
# SKILL.md frontmatter
description: This skill generates rules for AGENTS.md based on user corrections
```

**Vibe check questions:**
- Does output mention "rules" or "AGENTS.md"? YES/NO
- Does output contain rule-like content (bullet points, guidelines)? YES/NO
- Does output reference corrections or patterns? YES/NO

**Score: PASS** - Output vibes with description

### Scoring

| Match Level | Score |
|-------------|-------|
| Strong match | 100% |
| Partial match | 70% |
| Weak match | 40% |
| No match | 0% |

## Tmux Execution Strategy

### Why Tmux?

1. **True parallel PTYs** - Each test runs in separate terminal
2. **Better isolation** - Independent shell environments
3. **Visibility** - Can attach to watch progress
4. **Reliability** - No background job quirks
5. **Control** - Can kill individual tests if hung

### Execution Pattern

**Setup:**
```bash
mkdir -p /tmp/skill-test
tmux kill-session -t skill-test 2>/dev/null || true
```

**Run 3 parallel tests:**
```bash
tmux new-session -d -s skill-test -n test1 \
  'claude -p --dangerously-skip-permissions "[t1]" > /tmp/skill-test/t1.txt 2>&1; echo DONE > /tmp/skill-test/t1.done'

tmux new-window -t skill-test -n test2 \
  'claude -p --dangerously-skip-permissions "[t2]" > /tmp/skill-test/t2.txt 2>&1; echo DONE > /tmp/skill-test/t2.done'

tmux new-window -t skill-test -n test3 \
  'claude -p --dangerously-skip-permissions "[t3]" > /tmp/skill-test/t3.txt 2>&1; echo DONE > /tmp/skill-test/t3.done'
```

**Wait for completion:**
```bash
while [ ! -f /tmp/skill-test/t1.done ] || [ ! -f /tmp/skill-test/t2.done ] || [ ! -f /tmp/skill-test/t3.done ]; do
  sleep 5
done
```

### Why Tmux Over Other Approaches?

| Approach | Issue |
|----------|-------|
| Task agents | Polling loops, retries, triple nesting |
| Background `&` | May not parallelize in Claude Code |
| **Tmux** | True parallel PTYs, reliable |

### Selecting Trigger Phrases

From the skill's SKILL.md description, extract phrases in quotes:

```yaml
description: This skill should be used when the user asks to "test skill",
"verify consistency", "run skill test"...
```

Pick 3 different phrases to test that all trigger paths work.

## Interpreting Results

### High Consistency (95%+)

Skill is deterministic. Safe to release.

**What this means:**
- All runs produce same structure
- Key facts align
- Minor wording variance only
- All trigger phrases work

### Medium Consistency (85-94%)

Review deviations before release.

**Common causes:**
- Optional sections sometimes included
- Different example selection
- Minor structural variance
- One trigger phrase behaves differently

**Action:** Check if deviations affect user experience

### Low Consistency (70-84%)

Structural issues need fixing.

**Common causes:**
- Conditional logic in skill
- Ambiguous instructions
- Random data sources
- Trigger phrases invoke different behaviors

**Action:** Revise SKILL.md for clearer instructions

### Poor Consistency (<70%)

Skill is non-deterministic. Do not release.

**Common causes:**
- External dependencies with variance
- Underspecified workflow
- Multiple valid interpretations
- Trigger phrases not properly defined

**Action:** Redesign skill for determinism

## Improving Determinism

### Make Instructions Explicit

BAD (Vague):
```
Analyze the code and provide feedback
```

GOOD (Explicit):
```
1. Read all .py files in the directory
2. Check for these specific issues: [list]
3. Generate report with these sections: [list]
```

### Specify Output Format

BAD (Unspecified):
```
Provide a summary
```

GOOD (Specified):
```
Provide summary in this format:
## Summary
- Key finding 1
- Key finding 2

## Recommendations
[numbered list]
```

### Consistent Trigger Behavior

Ensure all trigger phrases in description lead to same workflow:

BAD (Ambiguous):
```
description: "analyze code" or "review code" or "audit code"
```
(If these invoke different behaviors, tests will fail)

GOOD (Consistent):
```
description: "analyze code", "review code", "audit code"
```
(All synonyms that invoke identical workflow)

## Edge Cases

### Empty Outputs

If a run produces empty output:
- Score as 0% similarity
- Flag as major deviation
- Indicates skill failure or trigger not recognized

### Partial Outputs

If a run stops mid-way:
- Compare only completed sections
- Flag incomplete sections as deviations
- May indicate timeout or error

### Trigger Not Matched

If CLI doesn't invoke the skill:
- Output will be generic response, not skill output
- Score as 0% for that trigger phrase
- Indicates trigger phrase needs adjustment in description
