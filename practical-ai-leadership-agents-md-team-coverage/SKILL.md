---
name: dev-agents-md-team-coverage
description: This skill should be used when the user asks to "improve AGENTS.md for team", "review AGENTS.md coverage gaps", "create AGENTS.md for team areas", "AGENTS.md team coverage audit", "audit AGENTS.md for team codebase", "map team repositories to AGENTS.md", or wants to systematically improve AI coding assistant context for a specific team's codebase areas.
version: 0.1.0
---

# AGENTS.md Team Coverage Audit

Systematically review, improve, and create AGENTS.md files for a team's active codebase areas. Score existing files against the golden template, propose individual changes, and create draft PRs with domain-appropriate reviewers.

## Reference Files

For detailed information:
- **`references/golden-template.md`** — Complete AGENTS.md template structure and section weights
- **`references/scoring-guide.md`** — How to evaluate and score existing files
- **`references/pr-template.md`** — PR descriptions, commit messages, reviewer assignment

## Prerequisites

Before running this skill, ensure you have:

1. **Team mapping** with members, roles, and GitHub usernames
2. **Repository paths** for repos the team works in
3. **Git access** to query commit history
4. **GitHub CLI** (`gh`) authenticated for PR creation

## Workflow Overview

```
1. Identify Team → 2. Map Git Activity → 3. Find AGENTS.md Files → 4. Score & Review → 5. Propose Changes → 6. Implement → 7. Create PRs
```

## Step 1: Gather Team Information

Ask the user for:

| Input | Example |
|-------|---------|
| Team name | "Team A" |
| Team mapping file path | `docs/concept/team_mapping.md` |
| Repository paths | `/path/to/backend`, `/path/to/flutter` |
| Time window for git analysis | 3 months |

Read the team mapping to get:
- Member names
- Git author names/emails
- GitHub usernames
- Roles (Backend, Frontend, Product)

## Step 2: Analyze Git Activity

For each team member, query git history in each repository:

```bash
git log --author="<name>" --since="<date>" --name-only --pretty=format: | sort | uniq -c | sort -rn
```

Build a mapping of:
- Team member → Codebase areas (directories with high activity)
- Aggregate file change counts per area

Focus on areas with 10+ file changes.

## Step 3: Map to AGENTS.md Files

For each high-activity codebase area:

1. Check if `AGENTS.md` exists in that directory
2. Classify as:
   - **Missing** — Needs to be created
   - **Exists** — Needs review and potential improvement

Create a coverage table:

| Repository | Path | Status | Team Members | Activity |
|------------|------|--------|--------------|----------|
| backend | `domains/payment/` | Exists | Alex | 19 files |
| backend | `domains/user/` | Missing | Alex | 30 files |

## Step 4: Score Existing Files

For each existing AGENTS.md, score against the golden template criteria.

### Scoring Criteria (100 points total)

| Section | Weight | Check |
|---------|--------|-------|
| Commands (first 50 lines) | 21% | Build, test, lint commands present? |
| Agent Permissions | 17% | Allowed/Ask First/Never sections? |
| Project Structure | 12% | 5-15 directory entries? |
| Performance | 8% | N+1 prevention, optimization guidance? |
| Domain Rules | 7% | Business logic constraints? |
| Error Handling | 8% | Patterns with examples? |
| Security | 6% | Secrets, auth, input validation? |
| Testing | 8% | Test commands and patterns? |
| Other sections | 13% | Conventions, commits, docs |

### Score Interpretation

| Score | Grade | Action |
|-------|-------|--------|
| 80-100 | Excellent | No changes needed |
| 60-79 | Good | Minor improvements |
| 40-59 | Fair | Add missing sections |
| 0-39 | Poor | Significant rewrite |

## Step 5: Propose Changes

For each file, create an individual proposal:

### For Missing Files

Propose content following the golden template with:
- Purpose section
- Commands (domain-specific)
- Project Structure
- Agent Permissions
- Performance guidance
- Domain Rules
- Testing section

### For Existing Files (Score < 80)

Identify specific gaps and propose additions:
- Add missing sections at appropriate locations
- Preserve existing valuable content
- Don't overwrite domain-specific knowledge

**Present all proposals to user for approval before implementing.**

## Step 6: Implement Changes

After user approval:

1. Create feature branch in each repository:
   ```bash
   git checkout main && git pull
   git checkout -b feat/improve-<team>-agents-md
   ```

2. Apply changes to files

3. Commit with descriptive message:
   ```
   docs: improve AGENTS.md files for <Team> areas

   [List of changes]
   ```

## Step 7: Create Draft PRs

For each repository with changes:

1. Push branch:
   ```bash
   git push -u origin <branch>
   ```

2. Create draft PR:
   ```bash
   gh pr create --draft --title "<title>" --body "<body>"
   ```

3. Add reviewers paired by domain:
   - Backend changes → Backend team members
   - Frontend changes → Frontend team members

4. Report PR links to user

## Templates

For PR descriptions, commit messages, and reviewer assignment, see `references/pr-template.md`.

For the complete AGENTS.md structure, see `references/golden-template.md`.

## Output Summary

At completion, provide:

| Metric | Value |
|--------|-------|
| Files reviewed | X |
| Files improved | X |
| Files created | X |
| PRs created | X |
| Reviewers assigned | [list] |

With links to all created PRs.
