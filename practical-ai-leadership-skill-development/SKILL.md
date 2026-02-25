---
name: practical-ai-leadership-skill-development
description: This skill should be used when the user wants to "create a skill", "add a skill", "write a new skill", "build a skill", "improve skill description", "organize skill content", or needs guidance on skill structure, progressive disclosure, or skill development best practices for Claude Code.
version: 1.0.0
---

# Skill Development for Claude Code Plugins

This skill provides guidance for creating effective skills for Claude Code plugins.

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
domains or tasks—they transform Claude from a general-purpose agent into a specialized agent
equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   ├── description: (required)
│   │   └── version: (required, semver e.g. 1.0.0)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    ├── examples/         - Working code examples and templates
    └── assets/           - Files used in output (icons, fonts, etc.)
```

#### SKILL.md (required)

**Metadata Quality:** The `name` and `description` in YAML frontmatter determine when Claude will use the skill. The description must include both what the skill does AND when to use it. Always write in third person — the description is injected into the system prompt, and inconsistent point-of-view causes discovery problems (e.g., "This skill should be used when..." instead of "Use this skill when..." or "I can help with...").

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform Claude's process and thinking.

- **When to include**: For documentation that Claude should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when Claude determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output Claude produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables Claude to use files without loading them into context

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude (Unlimited*)

*Unlimited because scripts can be executed without reading into context window.

| Directory | Purpose | When loaded |
|-----------|---------|-------------|
| SKILL.md | Core procedures and workflow | On skill trigger |
| references/ | Detailed docs, patterns, guides | When Claude needs them |
| examples/ | Working code, templates | When Claude needs them |
| scripts/ | Executable utilities | On execution |
| assets/ | Output resources (icons, fonts, templates) | On use |

## Skill Creation Process

To create a skill, follow the "Skill Creation Process" in order, skipping steps only if there is a clear reason why they are not applicable.

Copy this checklist and track progress:
- [ ] Step 1: Understand the skill with concrete examples
- [ ] Step 2: Plan the reusable skill contents
- [ ] Step 3: Select target location and create skill structure
- [ ] Step 4: Edit the skill
- [ ] Step 5: Validate
- [ ] Step 6: Review and test
- [ ] Step 7: Register and link
- [ ] Step 8: Iterate

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the prompt already specifies the skill's domain, target actions, and integration points (e.g., "write a skill that audits Dockerfiles for security misconfigurations"). Ask clarifying questions when the prompt leaves open questions about scope, data sources, or output format (e.g., "create a skill for team standup summaries" — from where? what format?).

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"

To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.

Conclude this step when there is a clear sense of the functionality the skill should support.

### Step 2: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:

1. Rotating a PDF requires re-writing the same code each time
2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill

Example: When designing a `frontend-webapp-builder` skill for queries like "Build me a todo app" or "Build me a dashboard to track my steps," the analysis shows:

1. Writing a frontend webapp requires the same boilerplate HTML/React each time
2. An `assets/hello-world/` template containing the boilerplate HTML/React project files would be helpful to store in the skill

Example: When building a `big-query` skill to handle queries like "How many users have logged in today?" the analysis shows:

1. Querying BigQuery requires re-discovering the table schemas and relationships each time
2. A `references/schema.md` file documenting the table schemas would be helpful to store in the skill

**For Claude Code plugins:** When building a hooks skill, the analysis shows:
1. Developers repeatedly need to validate hooks.json and test hook scripts
2. `scripts/validate-hook-schema.sh` and `scripts/test-hook.sh` utilities would be helpful
3. `references/patterns.md` for detailed hook patterns to avoid bloating SKILL.md

To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: scripts, references, and assets.

### Step 3: Select Target Location and Create Skill Structure

Determine where to create the skill. Use Bash to discover available locations:

1. **Skills repositories** — scan for git repos containing `skills/` and `setup.sh` (adapt the scan root to the user's project directory):
   ```bash
   find ~/projects -maxdepth 2 -name setup.sh -path '*/skills/../setup.sh' -o -name setup.sh -exec grep -l 'SKILLS_DIR' {} \;
   ```
   These repos auto-discover all skills and symlink them to every detected tool directory.
2. **Native tool directories** — fall back to any Agent Skills-compatible tool directory (e.g., `~/.claude/skills/`, `~/.gemini/skills/`, `~/.cursor/skills/`) if no skills repository exists or the user prefers direct placement.

Present discovered options to the user and ask for their preference. If the user has already specified context (e.g., "create a skill for my client project"), infer without asking. If only native directories are found, use those directly.

Store the chosen path as `$TARGET`. Create the skill directory with only SKILL.md — add subdirectories in Step 4 as needed:

```bash
mkdir -p $TARGET/skills/skill-name
touch $TARGET/skills/skill-name/SKILL.md
```

If `$TARGET` is a skills repository with `setup.sh`, Step 7 will handle symlink registration. If `$TARGET` is a native tool directory, the skill is immediately available and Step 7 can be skipped.

### Step 4: Edit the Skill

When editing the (newly-created or existing) skill, remember that the skill is being created for another instance of Claude to use. Focus on including information that would be beneficial and non-obvious to Claude. Consider what procedural knowledge, domain-specific details, or reusable assets would help another Claude instance execute these tasks more effectively.

#### Start with Reusable Skill Contents

To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates to store in `assets/`, or documentation to store in `references/`.

Also, delete any example files and directories not needed for the skill. Create only the directories you actually need (references/, examples/, scripts/, assets/).

#### Update SKILL.md

Every skill MUST begin with an analytics tracking step immediately after the title:

```markdown
## Before Starting
Run: `skills track <skill-id>`
```

This reports the invocation to the skills server for usage analytics.

**Writing Style:** Write the entire skill using **imperative/infinitive form** (verb-first instructions), not second person. Use objective, instructional language (e.g., "To accomplish X, do Y" rather than "You should do X" or "If you need to do X"). This maintains consistency and clarity for AI consumption.

**Frontmatter:** The fields `name`, `description`, and `version` are required. The `name` must match the skill's directory name (e.g., `my-skill` for `skills/my-skill/`). Name constraints: maximum 64 characters, lowercase letters, numbers, and hyphens only, cannot contain reserved words ("anthropic", "claude"). The `description` must be non-empty and at most 1024 characters. The `version` must follow semantic versioning (e.g., `1.0.0`). Start new skills at `1.0.0`.

**Naming pattern:** `{activity-prefix}-{domain}-{action}` in kebab-case. Every skill name starts with an activity prefix:

| Prefix | Activity |
|--------|----------|
| `dev-` | Development activities (coding, building, fixing, auditing code) |
| `devex-` | Developer experience metrics extraction and analysis |
| `meta-` | Meta-skills that improve AI workflow itself |
| `personal-brand-` | Personal branding, content creation, LinkedIn |
| `admin-` | Administrative and operational maintenance tasks |

Examples: `dev-ai-coding-tools-adoption-audit-autonomous-loop`, `devex-github-baseline-extraction`, `meta-learn-from-mistakes`, `personal-brand-linkedin-weekly-content`, `admin-confluence-team-page-audit`. Prefer gerund or noun-phrase suffixes for the action segment.

**Description must include both what the skill does AND when to use it.** The description is critical for skill selection: Claude uses it to choose the right skill from potentially 100+ available skills. It must provide enough detail for Claude to know both what the skill does and when to select it.

**IMPORTANT — Always write descriptions in third person.** The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems.

- Good: "Processes Excel files and generates reports"
- Avoid: "I can help you process Excel files" (first person)
- Avoid: "You can use this to process Excel files" (second person)

Include specific trigger phrases in the description:

```yaml
---
name: dev-my-domain-skill-action
description: This skill should be used when the user asks to "specific phrase 1", "specific phrase 2", "specific phrase 3". Include exact phrases users would say that should trigger this skill. Be concrete and specific.
version: 1.0.0
---
```

**Good description examples (third person, includes what it does + when to use it):**
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", "implement prompt-based hooks", or mentions hook events (PreToolUse, PostToolUse, Stop).
description: Extracts text and tables from PDF files, fills forms, and merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

**Bad description examples:**
```yaml
description: Use this skill when working with hooks.  # Wrong person ("Use" addresses the reader), vague
description: I can help with hooks.  # First person — causes discovery problems in system prompt
description: You can use this to manage hooks.  # Second person — inconsistent point-of-view
description: Provides hook guidance.  # No trigger phrases, missing "when to use it"
```

To complete SKILL.md body, answer the following questions:

1. What is the purpose of the skill, in a few sentences?
2. When should the skill be used? (Include this in frontmatter description with specific triggers)
3. In practice, how should Claude use the skill? All reusable skill contents developed above should be referenced so that Claude knows how to use them.

**Keep SKILL.md lean:** Target 1,500-2,000 words / under 500 lines for the body. The context window is a shared resource — every token competes with conversation history, other skills, and the user's request. Default assumption: Claude is already very smart; only add context Claude doesn't already have. Challenge each piece: "Does Claude really need this explanation?" Move detailed content to references/:
- Detailed patterns → `references/patterns.md`
- Advanced techniques → `references/advanced.md`
- Migration guides → `references/migration.md`
- API references → `references/api-reference.md`

**Reference depth rule:** Keep references one level deep from SKILL.md. All reference files must link directly from SKILL.md (SKILL.md → reference.md is OK, but SKILL.md → advanced.md → details.md is NOT). Claude may only partially read files discovered through chained references.

**Table of contents for long references:** For reference files longer than 100 lines, include a table of contents at the top so Claude can see the full scope even when previewing with partial reads.

**Match specificity to task fragility (degrees of freedom):** Not all skill instructions need the same level of precision. Choose based on the consequence of deviation:
- **High freedom** (text-based instructions) — when multiple approaches are valid and context determines the best path. Example: code review guidelines, content organization.
- **Medium freedom** (pseudocode with parameters) — when a preferred pattern exists but some variation is acceptable. Example: report generation with configurable format.
- **Low freedom** (specific scripts, exact commands) — when operations are fragile, consistency is critical, or a specific sequence must be followed. Example: database migrations, validation commands with exact flags.

Fragile operations need precise scripts; open-ended tasks need general direction.

**For complex workflows, provide a copy-paste checklist** that Claude can track progress against. This is especially effective for multi-step procedures where skipping a step causes failures:

```markdown
Copy this checklist and track progress:
- [ ] Step 1: Analyze input
- [ ] Step 2: Generate output
- [ ] Step 3: Validate result
- [ ] Step 4: Fix issues and re-validate
```

**Reference resources in SKILL.md:**
```markdown
## Additional Resources

### Reference Files

For detailed patterns and techniques, consult:
- **`references/patterns.md`** - Common patterns
- **`references/advanced.md`** - Advanced use cases

### Example Files

Working examples in `examples/`:
- **`example-script.sh`** - Working example
```

### Step 5: Validate

Three dedicated skills handle validation. Run all three in order before proceeding to Step 6 (Review and Test). For each step, apply a feedback loop: fix issues, re-validate, repeat until resolved.

#### 5a. Best Practices Audit

Trigger `dev-skill-best-practices-audit`:

```
Audit skill at $TARGET/skills/skill-name/ against best practices
```

Spawns five parallel sub-agents checking YAML & naming, descriptions, conciseness & progressive disclosure, content quality, and workflows & feedback. Resolve all CRITICAL and HIGH violations before proceeding.

#### 5b. Naming Compliance Review

Trigger `dev-skill-naming-compliance-review`:

```
Review skill naming for $TARGET/skills/skill-name/
```

Validates folder name, YAML `name` field (max 64 chars, kebab-case, no reserved words, matches folder), activity prefix, and `description` format. Fix any violations before proceeding.

#### 5c. Trigger Phrase Hardening

Trigger `dev-skill-trigger-phrase-hardening`:

```
Check for trigger phrase overlaps with skill at $TARGET/skills/skill-name/
```

Compares the new skill's trigger phrases against all existing skills to detect overlaps that could cause wrong-skill activation. Apply disambiguation fixes (domain-qualifying, abbreviation expansion, cross-reference notes) for any HIGH or MEDIUM risk overlaps.

### Step 6: Review and Test

Both sub-steps are mandatory and must not be skipped. Apply a feedback loop for each: fix issues, re-run, repeat until resolved.

#### 6a. Skill Review

Spawn the `skill-reviewer` agent (built-in at `~/.claude/agents/skill-reviewer.md`):

```
Review the skill at $TARGET/skills/skill-name/
```

The agent evaluates structure, description quality, progressive disclosure, content quality, and supporting files. It produces a structured report with critical/major/minor issues and priority recommendations. Resolve all critical and major issues before proceeding.

#### 6b. Consistency Testing

Trigger `skill-testing`:

```
Test the skill at $TARGET/skills/skill-name/
```

Runs three parallel Claude CLI invocations with the skill's trigger phrases, compares outputs for structural and factual consistency, and detects execution issues. Proceed to Step 7 when the consistency test scores 85%+ (PASS or REVIEW verdict).

### Step 7: Register and Link

**Skip this step if `$TARGET` is a native tool directory** (e.g., `~/.claude/skills/`, `~/.gemini/skills/`, `~/.cursor/skills/`) — the skill is already in place.

If `$TARGET` is a skills repository with `setup.sh`:

Run the setup script to symlink the new skill into all detected tool directories, then commit:
```bash
cd $TARGET
./setup.sh
git add skills/skill-name && git commit -m "feat: add skill-name"
```
Push to remote if applicable: `git push`

The setup script auto-discovers all skills in the repo and symlinks them to every detected tool directory (20+ paths including Claude Code, Codex, Gemini CLI, Cursor, Windsurf, and more). No per-skill configuration is needed.

### Step 8: Iterate

After testing the skill, users may request improvements. Often this happens right after using the skill, with fresh context of how the skill performed.

**Iteration workflow:**
1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again

**Common improvements:**
- Strengthen trigger phrases in description
- Move long sections from SKILL.md to references/
- Add missing examples or scripts
- Clarify ambiguous instructions
- Add edge case handling

## Plugin-Specific Considerations

### Skill Location in Plugins

Plugin skills live in the plugin's `skills/` directory:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
├── agents/
└── skills/
    └── my-skill/
        ├── SKILL.md
        ├── references/
        ├── examples/
        └── scripts/
```

### Auto-Discovery

Claude Code automatically discovers skills:
- Scans `skills/` directory
- Finds subdirectories containing `SKILL.md`
- Loads skill metadata (name + description) always
- Loads SKILL.md body when skill triggers
- Loads references/examples when needed

### No Packaging Needed

Plugin skills are distributed as part of the plugin, not as separate ZIP files. Users get skills when they install the plugin.

### Testing in Plugins

Test skills by installing plugin locally:

```bash
# Test with --plugin-dir
cc --plugin-dir /path/to/plugin

# Ask questions that should trigger the skill
# Verify skill loads correctly
```

## Examples from Plugin-Dev

Study the skills in this plugin as examples of best practices:

**hook-development skill:**
- Excellent trigger phrases: "create a hook", "add a PreToolUse hook", etc.
- Lean SKILL.md (1,651 words)
- 3 references/ files for detailed content
- 3 examples/ of working hooks
- 3 scripts/ utilities

**agent-development skill:**
- Strong triggers: "create an agent", "agent frontmatter", etc.
- Focused SKILL.md (1,438 words)
- References include the AI generation prompt from Claude Code
- Complete agent examples

**plugin-settings skill:**
- Specific triggers: "plugin settings", ".local.md files", "YAML frontmatter"
- References show real implementations (multi-agent-swarm, ralph-wiggum)
- Working parsing scripts

Each demonstrates progressive disclosure and strong triggering.

## Validation Checklist

Before finalizing a skill:

- [ ] SKILL.md has valid YAML frontmatter with `name`, `description`, and `version`
- [ ] First instruction after title is `skills track <skill-id>` in a `## Before Starting` section
- [ ] Version follows semantic versioning (e.g., `1.0.0`); new skills start at `1.0.0`
- [ ] Name is at most 64 characters, lowercase letters/numbers/hyphens only, no reserved words ("anthropic", "claude")
- [ ] Description is non-empty and at most 1024 characters
- [ ] Description uses third person (not first/second person — it's injected into system prompt) with specific trigger phrases
- [ ] Description includes both what the skill does AND when to use it
- [ ] Body uses imperative/infinitive form (not second person)
- [ ] Body is lean (1,500-2,000 words / under 500 lines), detailed content in references/
- [ ] References are one level deep from SKILL.md (no chained references)
- [ ] Reference files longer than 100 lines have a table of contents at the top
- [ ] All referenced files exist
- [ ] Examples are complete and working
- [ ] Scripts are executable
- [ ] No time-sensitive content (avoid phrases like "If before August 2025, use old API" — instructions must remain valid regardless of when they are read)
- [ ] Consistent terminology throughout (pick one term and use it everywhere; do not mix synonyms like "API endpoint" / "route" / "path" for the same concept)
- [ ] All file paths use forward slashes only (`src/utils/helper.py`), even when targeting Windows
- [ ] Provides a single default approach rather than listing multiple options; mention alternatives only as an escape hatch when truly necessary

## Additional Resources

### Reference Files

- **`references/writing-style.md`** — Imperative form, third-person descriptions, objective language with before/after examples
- **`references/common-mistakes.md`** — Weak triggers, bloated SKILL.md, second person writing, missing resource references

## Implementation Workflow

1. **Understand use cases**: Identify concrete examples of skill usage
2. **Plan resources**: Determine what scripts/references/examples are needed
3. **Select target and create structure**: Discover skills repos (look for `setup.sh`) or fall back to native tool directories, then create skill directory with SKILL.md
4. **Edit the skill**: Write SKILL.md and create bundled resources (references/, examples/, scripts/, assets/)
5. **Validate**: Run `dev-skill-best-practices-audit`, `dev-skill-naming-compliance-review`, `dev-skill-trigger-phrase-hardening`
6. **Review and test**: Spawn `skill-reviewer` agent, then run `skill-testing` skill
7. **Register and link** (repo only): Run `./setup.sh` to symlink into all detected tool directories, then commit. Skip if placed directly in a native tool directory.
8. **Iterate**: Use the skill on real tasks, identify improvements, update and retest
