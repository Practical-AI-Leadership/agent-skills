---
name: meta-agent-team-orchestration
description: This skill should be used when the user asks to "create agent team", "spawn a team", "design agent team", "team of agents", "multi-agent team", "orchestrate agents", "agent team for this task", "coordinate multiple agents", "parallel agent work", "swarm this task", "use agent teams", or wants to design and execute a multi-agent team for a complex task. Handles full lifecycle from task analysis through post-mortem retrospective. Not for delegating project workflow work packages to agents — use project-workflow-wp-execution-delegation for that. Not for orchestrating a remote OpenClaw/Codex agent to solve a Jira ticket — use meta-openclaw-ticket-orchestration for that.
---

# Agent Team Orchestration

Design, spawn, coordinate, and retrospect multi-agent teams matched to the task at hand.

## Purpose

Transform complex tasks into efficiently coordinated multi-agent workflows. Interview the user, classify the task, recommend the right team topology, spawn agents with appropriate roles and models, enforce review gates, and run a post-mortem after shutdown.

## Intent
- Task completion quality > team size. A single agent that finishes correctly beats a 4-agent team with coordination overhead. Always recommend the smallest team that can do the job, and say so explicitly when a team is overkill.
- Idle agents are wasted money, not "readiness." Never spawn an agent before its input is available. The lazy-spawning rule exists because each spawned agent burns tokens on onboarding whether or not it has work to do.
- Coordination overhead grows quadratically (Brooks' Law). At 4+ agents, justify each additional agent against the communication tax. At 6+, the coordination cost almost always exceeds the parallelism benefit.
- Review gates are mandatory for production-impacting outputs but wasteful for exploratory research. Match review intensity to output criticality — do not apply uniform review to everything.
- "Good" = a team that completes with zero idle time per agent, no revision cycles caused by miscommunication (as opposed to legitimate quality issues), and a post-mortem that identifies at least one reusable insight.
- "Good enough" = the task completes correctly with the right team size, even if coordination was slightly inefficient.
- When the interview reveals ambiguity about parallelizability, default to a smaller team with sequential execution rather than a larger team that might work at cross-purposes.

## Critical Rules

1. **Always interview first.** Never spawn agents without understanding the task.
2. **Warn when a team is overkill.** If the task is simple, recommend a single agent instead.
3. **Lazy-spawn teammates.** Only spawn agents when their input is ready. Never let agents idle.
4. **Review gates are mandatory for critical outputs.** The skill decides which outputs need review based on task criticality.
5. **Post-mortem is mandatory.** After every team shutdown, analyze efficiency and report findings.

## Workflow Overview

```
Interview → Assess Complexity → Design Team → Spawn → Coordinate → Shutdown → Post-Mortem
```

| Phase | What Happens | Tool |
|-------|-------------|------|
| 1. Interview | Classify the task via structured questions | AskUserQuestion |
| 2. Assess | Determine if a team is needed at all | Decision matrix |
| 3. Design | Select topology, roles, models, review gates | Team design framework |
| 4. Spawn | Create team, launch agents with lazy spawning | TeamCreate, Task |
| 5. Coordinate | Route work, enforce review gates, monitor | SendMessage, inbox polling |
| 6. Shutdown | Graceful shutdown of all teammates | SendMessage (shutdown_request) |
| 7. Post-Mortem | Analyze efficiency, friction, improvements | Retrospective framework |

---

## Phase 1: Task Classification Interview

Use AskUserQuestion to gather task characteristics. Ask these questions in order:

### Question 1: Task Nature

```
"What is the core task you need the team for?"
Options:
- Investigation/analysis (research, root-cause analysis, auditing)
- Creation/generation (writing code, designing systems, producing deliverables)
- Verification/validation (testing, reviewing, confirming findings)
- Mixed (combination of the above)
```

### Question 2: Parallelizability

```
"Can the work be split into independent streams, or must it flow sequentially?"
Options:
- Fully parallel (independent subtasks, no dependencies)
- Mostly parallel (some dependencies, but streams can start independently)
- Sequential pipeline (each step's output feeds the next)
- Exploratory (don't know yet — need to investigate first)
```

### Question 3: Criticality

```
"How critical are the outputs? This determines review gate intensity."
Options:
- Production-impacting (affects real users, deployments, or business decisions)
- Internal deliverable (work packages, plans, documentation)
- Exploratory research (findings inform future decisions, not immediate action)
```

### Question 4: Constraints

```
"Any specific constraints?"
Options:
- Cost-sensitive (prefer Sonnet/Haiku over Opus where possible)
- Quality-first (prefer Opus for all reasoning tasks)
- Speed-first (maximize parallelism, minimize review cycles)
- Balanced (default)
```

See `references/interview-framework.md` for the full question bank and follow-up logic.

---

## Phase 2: Complexity Assessment

After the interview, classify the task using this matrix:

| Signal | Single Agent | Lean Pair (2) | Full Team (3-5) |
|--------|-------------|---------------|-----------------|
| Subtask count | 1-2 | 2-3 | 4+ |
| Requires independent verification | No | Yes (one verifies the other) | Yes (dedicated verifier) |
| Multiple expertise domains | No | No | Yes |
| Output criticality | Low | Medium | High |
| Parallelizable work streams | No | Limited | Yes |

**If Single Agent is recommended:** Warn the user explicitly:

> "This task has [N] subtasks with [low/no] parallelization opportunity. A single agent would complete it faster with less overhead. Shall I proceed with a single agent instead, or do you still want a team?"

Only proceed with a team if the user insists or if the initial classification was incorrect.

---

## Phase 3: Team Design

### Step 3.1: Select Topology

Use the task classification to select a communication topology:

| Task Type | Topology | Why |
|-----------|----------|-----|
| Parallel independent work | **Hub-and-spoke** | Workers report to lead, no cross-talk needed |
| Sequential pipeline (A→B→C) | **Linear chain** | Each agent's output feeds the next |
| High-ambiguity exploration | **Parallel + dedicated reviewer** | Independent perspectives prevent groupthink |
| Confirmatory verification | **Lean pair** | One investigates, one verifies |

See `references/communication-patterns.md` for detailed topology diagrams and trade-offs.

### Step 3.2: Define Roles

Map task needs to agent roles. Common role patterns:

| Role | Purpose | Default Model | When to Use |
|------|---------|---------------|-------------|
| Investigator | Research, data gathering, analysis | Opus | Complex reasoning over large inputs |
| Verifier | Independent measurement, spot-checking | Sonnet | Quantitative checks against source data |
| Reviewer | Quality gate, cross-checking outputs | Opus | Critical deliverables needing sign-off |
| Planner | Designing solutions, writing specs | Opus | Architectural decisions, WP design |
| Implementer | Writing code, executing changes | Opus/Sonnet | Depends on change complexity |

**Model selection principle:** Use Opus for reasoning-heavy roles (analyst, reviewer, planner). Use Sonnet for measurement-heavy roles (verifier, data collector). Never use Haiku for roles that produce deliverables.

### Step 3.3: Design Review Gates

Based on criticality from the interview:

| Criticality | Review Approach |
|-------------|----------------|
| Production-impacting | Dedicated Reviewer teammate (Opus) for every output |
| Internal deliverable | Team lead reviews, escalates to user if unsure |
| Exploratory research | Spot-check by lead, no formal review gate |

For dedicated reviewers, include these instructions in their prompt:

> You are a relentless reviewer. Your job is to find every error, inconsistency, and gap in this output. Assume it has problems until proven otherwise.
>
> **Check:**
> 1. Every factual claim is verified against the actual source (code, files, data) — not accepted at face value
> 2. Internal consistency: no contradictions between sections or outputs
> 3. Completeness: no requirements or inputs silently dropped
> 4. Output format matches the specification given to the producing agent
> 5. No placeholder content (TODO, TBD, FIXME, "insert here")
> 6. Recommendations are supported by specific evidence, not generic advice
>
> **Verify against:** The original task brief, source files referenced by the output, and any specification docs provided during onboarding.
>
> **Output:** For each finding:
> - **Finding**: What is wrong
> - **Severity**: CRITICAL / HIGH / MEDIUM / LOW
> - **Evidence**: What you checked and what you found
> - **Suggested Fix**: Specific action to resolve
>
> If zero findings: "Review complete. Zero findings. Checked: [list criteria checked]."
> If you cannot verify a claim because the source data is unavailable or ambiguous, report it as UNABLE_TO_VERIFY. Do not assume correctness. Do not guess.
>
> **Verdict:** APPROVED / APPROVED WITH NOTES / REVISION NEEDED / REJECTED

If the reviewer reports findings: the producing agent fixes issues and the reviewer re-verifies (max 2 cycles). If issues persist after 2 cycles, escalate to user with all findings.

### Step 3.4: Plan Spawning Order (Lazy Spawning)

**Never spawn all agents at once.** Plan which agents start immediately vs which wait:

```
Immediate:  Agents whose input is already available
Deferred:   Agents who need output from immediate agents
Last:       Agents who validate/integrate all prior work
```

Example for an investigation team:
```
Immediate:  verifier + root-cause-analyst (parallel, input is the raw data)
Deferred:   reviewer (spawned when first report arrives)
Last:       planner (spawned after review approves findings)
```

This avoids the **idle agent anti-pattern** where agents burn tokens on onboarding then wait with nothing to do. See `references/anti-patterns.md`.

---

## Phase 4: Spawning and Coordination

### Step 4.1: Create Team

```
TeamCreate with team_name derived from the task (e.g., "p14-regression-investigation")
```

### Step 4.2: Spawn Agents

For each agent, use the Task tool with:
- `subagent_type`: Match to the role (general-purpose for full capability, Explore for read-only research, Plan for plan-mode work)
- `model`: As determined in Step 3.2
- `mode`: Use "plan" for planner roles that need approval before writing
- `name`: Short, descriptive (e.g., "verifier", "root-cause-analyst")
- `team_name`: The team created in Step 4.1

**Prompt structure for every teammate:**
1. Role definition (what they do, what they don't do)
2. Onboarding instructions (which files to read first)
3. Task-specific instructions (what to investigate/produce)
4. Output format (how to structure their deliverable)
5. Communication protocol (send results to team-lead when done)

### Step 4.3: Coordinate Work

During execution:
- **Poll inbox with 60-second intervals** to save tokens
- **Forward outputs to the right recipient** based on the spawning plan
- **Enforce review gates** — do not advance to the next phase until the reviewer approves
- **Handle rejections** — if a reviewer rejects output, send feedback to the original agent for revision
- **Track revision cycles** — if an agent needs >2 revisions, flag it in the post-mortem

---

## Phase 5: Shutdown

1. Send `shutdown_request` to all teammates
2. Wait for all `shutdown_approved` confirmations
3. Call `TeamDelete` to clean up team files
4. Proceed to post-mortem

---

## Phase 6: Post-Mortem Retrospective (Mandatory)

After every team shutdown, analyze and report:

### Metrics to Collect

| Metric | How to Measure |
|--------|---------------|
| Wall-clock time | Team creation to final shutdown |
| Idle time per agent | Time between spawn and first meaningful work |
| Communication hops | Messages routed through lead vs direct peer messages |
| Revision cycles | Times outputs were rejected/revised before approval |
| Novel findings | Insights that weren't in the original input |
| Onboarding overhead | Duplicate document reads across teammates |

### Report Template

```markdown
## Post-Mortem: [Team Name]

### Timeline
- Total wall-clock: [X] minutes
- Phase 1 (investigation): [X] min
- Phase 2 (review): [X] min
- Phase 3 (planning): [X] min

### Efficiency Analysis
- Agents spawned: [N]
- Agents that were idle >2 min: [list]
- Communication hops through lead: [N]
- Revision cycles: [N] (reasons: [...])

### What Worked
- [specific patterns that added value]

### What to Improve
- [specific friction points with suggested fixes]

### Recommendation for Next Time
- Optimal team size for this task type: [N]
- Recommended topology: [type]
- Skip/keep reviewer: [recommendation with justification]
```

Present this to the user after every team run.

---

## Quick Reference

### Task → Team Size

| Task | Team Size | Topology |
|------|-----------|----------|
| Confirm existing findings | 2 (investigator + verifier) | Lean pair |
| Root-cause analysis | 3 (analyst + verifier + reviewer) | Hub-and-spoke |
| Design work packages | 2-3 (planner + reviewer, optional analyst) | Linear chain |
| Full investigation + planning | 3-4 (analyst + verifier + reviewer + planner) | Hub-and-spoke with lazy spawning |
| Parallel implementation | N workers + 1 reviewer | Hub-and-spoke |

### Communication Overhead Formula

```
Hops = n * (n-1) / 2    (Brooks' Law)
```

| Team Size | Communication Paths | Coordination Tax |
|-----------|-------------------|-----------------|
| 2 | 1 | Negligible |
| 3 | 3 | Low |
| 4 | 6 | Medium |
| 5 | 10 | High — justify each additional agent |
| 6+ | 15+ | Very high — almost never justified for agent teams |

### Model Costs (Relative)

| Model | Cost | Best For |
|-------|------|----------|
| Haiku | $ | Never for deliverables. OK for simple data extraction. |
| Sonnet | $$ | Verification, measurement, data collection |
| Opus | $$$$ | Analysis, review, planning, architecture |

## References

- `references/team-topologies.md` — Brooks' Surgical Team, Team Topologies framework, Google Research findings on multi-agent scaling
- `references/communication-patterns.md` — Hub-and-spoke vs peer-to-peer vs hybrid, with decision criteria and trade-offs
- `references/anti-patterns.md` — Common mistakes: idle agents, hub bottleneck, redundant onboarding, premature spawning
- `references/interview-framework.md` — Full question bank with follow-up logic and edge case handling
