---
name: dev-prompt-to-evaluators
description: >-
  Systematically derives code/rule-based and LLM-as-Judge evaluators from any LLM
  feature's system prompt. This skill should be used when the user asks to
  "derive evaluators from prompt", "extract evaluators", "prompt to evaluators",
  "code-based evaluators for feature", "rule-based evaluators from prompt",
  "analyze prompt for evaluators", "what can we check with code in this prompt".
  Not for analyzing existing evaluation runs — use project-workflow-eval-analysis for that.
---

# Derive Evaluators from LLM Feature Prompt

Systematically analyze any LLM feature's system prompt to produce two evaluator sets: code/rule-based (deterministic) and LLM-as-Judge (semantic). The output is designed for sharing with stakeholders and for integration into evaluation pipelines. Includes an org-specific pattern catalog but generalizes to any LLM application.

## Intent
- Correct categorization > exhaustive coverage. An evaluator that checks the wrong thing (code-based check for a semantic property, or LLM-as-Judge for something a regex could catch) is worse than a missing evaluator. When in doubt about whether something is code-checkable, test mentally: could you write a reliable regex/parser for this in 10 lines? If not, it is semantic.
- Every code-based evaluator must trace to a specific prompt instruction. If you cannot quote the exact line in the prompt that this evaluator validates, it does not belong in the list. Invented evaluators that test things the prompt never asked for create false failure signals.
- Practical evaluator set > theoretical completeness. 12 evaluators that all get implemented and run beats 40 evaluators where half are too complex to build. Bias toward evaluators with clear pass/fail criteria.
- Never classify "stay on topic" or "be helpful" as code-checkable. These require semantic understanding. Conversely, never classify "must include the support email" as needing LLM-as-Judge — that is a string match.
- "Good" = every prompt instruction maps to at least one evaluator, every evaluator has a clear tier assignment, and the compact code block format is copy-paste ready for the engineering team.
- "Good enough" = code-based evaluators cover all deterministic rules in the prompt, and semantic gaps are explicitly listed as LLM-as-Judge candidates even if their judging criteria are not fully specified.
- When a novel Tier 3 pattern is found, always flag it as a catalog candidate. Patterns that recur across features should be promoted to Tier 2, not rediscovered each time.

## Before Starting

Run: `skills track dev-prompt-to-evaluators`

## Workflow

### Step 1: Receive the Prompt

Wait for the user to provide the full system prompt for the LLM feature. Do not proceed until the complete prompt text is available. If the prompt appears truncated or incomplete, ask the user to confirm they have provided the full prompt before continuing.

### Step 2: Ask Clarifying Questions

Always ask these three questions via AskUserQuestion before deriving evaluators:

1. **Tool call visibility** — "Do we have access to the tool calls (e.g., semantic_search invocations and their results) in the evaluation data, or only the final response text?"
   - Options: Response text only / Full trace with tool calls / Not sure yet
2. **Existing evaluators scope** — "Should we propose a complete fresh set or only new evaluators not yet covered?"
   - Options: Complete fresh set / Only new evaluators (provide existing list)
3. **Dataset metadata availability** — "Will dataset items include expected metadata (topic names, app links, expected language) for validation, or should we only check format?"
   - Options: Format only / With expected metadata / Decide later

These answers directly affect which evaluators are feasible. For example, without tool call visibility, "did the model actually call semantic_search?" cannot be checked with code.

### Step 3: Analyze the Prompt

Walk through each prompt instruction line by line. For every instruction, determine:

1. **Is it code-checkable?** Can a regex, string match, word count, language detector, or structural parser reliably verify compliance?
2. **Is it semantic?** Does it require understanding meaning, intent, or quality (needs LLM-as-Judge)?

Apply a three-tier pattern hierarchy:

**Tier 1 — Universal patterns** (apply to virtually any LLM feature):
- Response Non-Empty (sanity check)
- Language Match (if multi-language support is mentioned)
- System Prompt Leakage (if any system integrity instructions exist)
- Formatting rules (LaTeX, markdown, bold — if any formatting instructions exist)

**Tier 2 — Known org-specific patterns** (from `references/org-patterns.md`):
- Apply when the prompt matches a known org-specific pattern (e.g., brand spelling, support email, personal data echo with known variables)
- Not every pattern will apply to every feature — only include evaluators that have a matching prompt instruction

**Tier 3 — Novel patterns** (discovered from this specific prompt):
- After checking Tiers 1 and 2, look for remaining code-checkable instructions that don't match any known pattern
- Common novel patterns: brand-specific spelling rules, required URLs or contact info, prohibited phrases, structural requirements (must end with a question, must include a link), numeric accuracy (rate limits, quotas)
- When a novel pattern is found, propose it as a new evaluator AND flag it as a candidate to add to the org-specific catalog for future reuse

### Step 4: Compile Evaluator Lists

#### Code/Rule-Based Evaluators

For each code-checkable instruction, create an evaluator entry with:
- **Name** — short descriptive name (e.g., "Language Match", "LaTeX Validity")
- **Rule** — what the check does in one sentence
- **Prompt source** — the specific prompt instruction it derives from

#### LLM-as-Judge Candidates

For each semantic instruction that code cannot reliably cover, create an entry with:
- **Name** — short descriptive name (e.g., "Topic Adherence", "Authentic Learning")
- **Rule** — what the evaluator assesses in one sentence

### Step 5: Review Evaluator Compilation

Spawn a sub-agent to verify the evaluator lists are complete and correctly categorized:

> You are a relentless evaluator auditor. Your job is to find every prompt instruction that was missed, every evaluator that is miscategorized (code-based when it should be semantic or vice versa), and every criterion that is unfalsifiable. Assume the compilation has gaps until proven otherwise.
>
> **Check:**
> 1. Every instruction in the source prompt maps to at least one evaluator — re-read the prompt line by line and cross-reference against the evaluator list to find any missed instructions
> 2. Code-based evaluators are genuinely code-checkable (could you write a reliable regex/parser in 10 lines?) — flag any that require semantic understanding
> 3. LLM-as-Judge candidates are genuinely semantic — flag any that could be reliably checked with string match, regex, or structural parsing
> 4. Every code-based evaluator has a specific, quoted "Prompt source" that exists in the actual prompt text — no invented evaluators
> 5. Evaluator criteria are falsifiable — each has a clear pass/fail condition, not vague quality assessments
> 6. Tier assignments (1/2/3) are correct — universal patterns are Tier 1, org-specific are Tier 2, novel are Tier 3
> 7. Novel Tier 3 patterns that could recur are flagged as catalog candidates
>
> **Verify against:** the original source prompt provided by the user, the tier definitions in Step 3, and the categorization decision guide in this skill
>
> **Output:** For each finding: Finding / Severity / Evidence / Suggested Fix.
> If zero findings: "Review complete. Zero findings. Checked: [list]."
> If unable to verify a categorization because the prompt instruction is ambiguous: report as UNABLE_TO_VERIFY with reason.

If findings exist: fix the evaluator lists and re-run the review (max 2 cycles). If issues persist after 2 cycles, present findings to the user and ask for direction.

### Step 6: Produce Output

Generate both output formats:

**Format A — Full Markdown Table** (for analysis and discussion):

```markdown
## Code/Rule-Based Evaluators

| # | Evaluator | Tier | Rule | Prompt Source |
|---|-----------|------|------|---------------|
| 1 | Name | 1/2/3 | What it checks | "quoted prompt instruction" |
```

```markdown
## LLM-as-Judge Candidates

| # | Evaluator | Rule |
|---|-----------|------|
| 1 | Name | What it assesses |
```

**Format B — Compact Code Blocks** (for copy-paste sharing):

Two separate code blocks, each with one evaluator per line in format: `#. Name — Rule`

Close with a brief comparison note if this is not the first feature analyzed (e.g., how many evaluators are shared with AI Tutor, how many are feature-specific).

## Categorization Decision Guide

| Signal in Prompt | Category | Evaluator Type |
|-----------------|----------|----------------|
| Specific format rules (LaTeX, markdown, spelling) | Code | Regex / parser |
| Language detection / matching | Code | fasttext / langdetect |
| Word count / length constraints | Code | Threshold check |
| Email / URL must appear in response | Code | String match |
| Known strings must NOT appear | Code | Negative string match |
| Link format requirements | Code | Markdown link regex |
| "Stay on topic", "reject inappropriate" | Semantic | LLM-as-Judge |
| "Guide conceptually, don't give answers" | Semantic | LLM-as-Judge |
| "Factually correct", "content accuracy" | Semantic | LLM-as-Judge |
| "Use only retrieved content" | Semantic | LLM-as-Judge |

## Catalog Maintenance

When Tier 3 novel patterns are discovered during analysis, assess whether they are likely to recur across future features. If so, add them to `references/org-patterns.md` (or a new org-specific catalog file) following the existing entry format: Trigger instruction, Implementation, Applies to.

## Additional Resources

### Reference Files

- **`references/org-patterns.md`** — Catalog of org-specific evaluator patterns with implementation notes (Tier 2)
