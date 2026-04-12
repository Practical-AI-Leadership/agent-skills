# Derive Evaluators from LLM Feature Prompt

Systematically derive code/rule-based and LLM-as-Judge evaluators from any LLM feature's system prompt. Walks the prompt instruction by instruction, applies a three-tier pattern hierarchy, and produces copy-paste-ready evaluator blocks.

**License:** [See LICENSE.md](../LICENSE.md) — free to use, modify, and share. Commercial repurposing prohibited.

## Pain Point

**ENG-04 / ENG-06: AI feature quality measurement**

Teams ship AI features without evaluators and keep rediscovering the same code-checkable vs. semantic distinction for every new feature. This skill codifies the analysis pattern so any engineer can produce a complete evaluator set from a prompt in one session.

## How to Use

1. Copy this directory to `~/.claude/skills/dev-prompt-to-evaluators/`
2. Invoke with a trigger phrase like "derive evaluators from prompt", "extract evaluators", "prompt to evaluators"
3. Provide the full system prompt when asked
4. Answer the three clarifying questions (tool call visibility, existing evaluators scope, dataset metadata availability)

## Origin Story

A team sync surfaced a systemic gap: multiple AI features had been shipped without evaluators, and when evaluators were eventually discussed, the team kept rediscovering the same code-checkable vs. semantic distinction from scratch for each feature. The skill codified the analysis pattern so the categorization logic does not have to be reinvented per feature.

## Customize for Your Org

- [ ] Populate `references/org-patterns.md` with your team's recurring Tier 2 patterns (brand spelling rules, required contact info, prohibited phrases)
- [ ] Adjust tier assignments based on your domain
