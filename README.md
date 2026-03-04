# Agent Skills

**Open-format extensions that give AI coding agents specialized knowledge and workflows.**

Your AI coding tools are only as good as the context they operate in. Agent Skills are portable, vendor-agnostic skill files that any AI coding agent can load to perform complex tasks — code analysis, documentation generation, pattern detection — without custom tooling or integrations.

## Available Skills

| Skill | What it does |
|-------|-------------|
| [Negative Coding Patterns Detection](practical-ai-leadership-negative-coding-patterns-detection/) | Scans your codebase for the 10 most dangerous anti-patterns that AI tools copy and amplify at scale. Generates ready-to-use fix prompts. |
| [AGENTS.md Team Coverage](practical-ai-leadership-agents-md-team-coverage/) | Audits and improves AGENTS.md coverage across team-owned repositories so AI agents understand your architecture. |
| [Skill Development](practical-ai-leadership-skill-development/) | A meta-skill for creating new skills — structure, progressive disclosure, and best practices baked in. |
| [Skill from Conversation](practical-ai-leadership-skill-from-conversation-development/) | Extracts a reusable skill from work you've already done in a conversation. Turn any workflow into a repeatable automation. |
| [Skill Testing](practical-ai-leadership-skill-testing/) | Validates that skills produce consistent, deterministic results across runs using parallel CLI testing. |

## How to Use

Each skill is a self-contained directory with a `SKILL.md` file. Point your AI coding agent at it:

**Claude Code:**
```bash
# Install a skill directly
claude mcp add-skill ./practical-ai-leadership-negative-coding-patterns-detection
```

**Any agent:** Copy the `SKILL.md` content into your agent's context or system prompt.

## Why This Exists

Most teams already use AI coding tools. Few get real ROI from them. The gap isn't the tools — it's missing context, unchecked anti-patterns, and no feedback loops.

These skills are extracted from real-world adoption work. They address the patterns we see repeatedly when auditing how engineering teams use AI coding tools.

## Want the Full Picture?

These skills scratch the surface. If your team is struggling with AI coding tool adoption — quality issues, review bottlenecks, the "junior dev" feeling — we run a **24-hour AI Coding Tools Adoption Audit** that identifies exactly what's blocking your ROI.

**[Learn more at practical-ai-leadership.com](https://practical-ai-leadership.com)**

## License

[Custom open-source license](LICENSE.md) — free to use, modify, and distribute. No selling or relicensing.
