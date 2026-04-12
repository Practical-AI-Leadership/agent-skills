# Anti-Patterns in Agent Team Orchestration

Common mistakes observed in real agent team sessions, with causes and fixes.

## Anti-Pattern 1: Premature Spawning

**Symptom:** Agents spawn, complete onboarding in 2 minutes, then sit idle for 15+ minutes waiting for input.

**Cause:** All agents spawned at team creation time, regardless of when their input would be ready.

**Example:** Spawning a reviewer and planner simultaneously with investigators. The investigators need 10-15 minutes to produce reports, during which the reviewer and planner burn tokens on onboarding then idle.

**Fix: Lazy Spawning**
```
Phase 1: Spawn only agents whose input is immediately available
Phase 2: Spawn the reviewer when the first report arrives in your inbox
Phase 3: Spawn the planner when the reviewer approves the findings
```

**Token savings:** ~40% reduction in idle-agent token waste.

---

## Anti-Pattern 2: Hub Bottleneck

**Symptom:** Total wall-clock time dominated by the lead's polling and forwarding, not by agent work.

**Cause:** Hub-and-spoke topology where every message requires the lead to: sleep (60s) → poll inbox → read message → compose forward → send → sleep (60s) → poll for response.

**Example:** A 4-agent team where each handoff adds 2 minutes of routing latency. With 6 handoffs in a workflow, that's 12 minutes of pure routing overhead.

**Impact calculation:**
```
Routing latency per hop = polling_interval + read_time + compose_time
                        ≈ 60s + 15s + 30s = ~105 seconds per hop
Total routing overhead  = num_hops × 105 seconds
```

**Fix options:**
1. **Batch communication.** Consolidate multiple reports into one forwarding message instead of routing them individually.
2. **Direct peer messaging for linear chains.** If A's output goes to B and only B, let A send directly.
3. **Reduce polling interval** for time-critical phases (30s instead of 60s).
4. **Pre-instruct the reviewer** to expect N reports: "You will receive 2 reports. Review both before responding with a combined verdict." This eliminates the "reviewed one, went idle, had to nudge" pattern.

---

## Anti-Pattern 3: Redundant Onboarding

**Symptom:** Every agent independently reads the same 7-10 onboarding documents, multiplying token cost.

**Cause:** Each agent's prompt includes "read these documents to understand the project." Since agents don't share context, each reads them independently.

**Example:** 4 agents × 7 documents = 28 document reads. At ~2,000 tokens per document, that's 56,000 tokens just for onboarding.

**Fix options:**
1. **Embed key context in prompts.** Instead of "read business_context.md," include the 3-sentence summary directly in the agent's prompt.
2. **Differentiate onboarding per role.** The verifier doesn't need the value proposition doc. The planner doesn't need the evidence catalog spec. Only include documents each role actually needs.
3. **Use a shared context brief.** Create a 500-word "team briefing" that covers the essentials, and have agents read only role-specific docs beyond that.

---

## Anti-Pattern 4: Missing Batch Instructions for Reviewers

**Symptom:** Reviewer processes one report, goes idle, and the lead has to send a follow-up message asking them to review the second report.

**Cause:** The reviewer's initial instruction said "review the team's outputs" but didn't specify how many outputs to expect or when to consider their work complete.

**Fix:** Always tell the reviewer upfront:
```
"You will receive [N] reports for review. Review ALL of them before sending
your combined verdict. Do not go idle after the first review."
```

---

## Anti-Pattern 5: Revision Cycles from Insufficient Spec

**Symptom:** Agent submits work, it's rejected, agent revises, resubmits. Multiple rounds.

**Cause:** The initial task prompt was ambiguous about output format, acceptance criteria, or scope.

**Example:** A planner was told "design work packages" but wasn't given the exact WP template format used by the project. First submission was a summary, not the template. Required a full revision cycle (10+ minutes).

**Fix:** Include in every task prompt:
1. **Explicit output format** (e.g., "Use the WP template with Parent/Children/Steps/Exit Criteria/Dependencies/Complexity")
2. **Example of acceptable output** (e.g., "See p13_wp_05 for the expected format")
3. **Specific acceptance criteria** (e.g., "Each WP must have numbered exit criteria and a files-to-modify table")

---

## Anti-Pattern 6: Team Too Large for the Task

**Symptom:** Coordination cost exceeds the benefit of parallelization. More time spent routing messages than doing work.

**Cause:** Defaulting to "more agents = more throughput" without assessing whether the task benefits from parallelism.

**Decision rule:**
```
If task_subtasks < 3:           → Single agent
If task_subtasks == 3:          → 2 agents (one does 2 subtasks)
If task_subtasks >= 4:          → 3-4 agents (but justify each)
If task needs independent check: → +1 verifier
If outputs are critical:         → +1 reviewer
```

**Maximum useful team size for Claude Code agent teams: 5.** Beyond 5, Brooks' communication overhead formula (n*(n-1)/2 = 10+ paths) makes coordination impractical.

---

## Anti-Pattern 7: No Post-Mortem

**Symptom:** Same inefficiencies repeat across sessions because nobody analyzed what went wrong.

**Cause:** Team is shut down immediately after deliverables are complete, without analyzing the process.

**Fix:** Mandatory post-mortem (see SKILL.md Phase 6). Track:
- Idle time per agent
- Revision cycles
- Communication hops
- Novel findings vs confirmatory findings

---

## Summary: Prevention Checklist

Before spawning any team, verify:

- [ ] Each agent has input ready at spawn time (no premature spawning)
- [ ] Reviewer knows exactly how many outputs to expect
- [ ] Every task prompt includes output format and acceptance criteria
- [ ] Team size is justified (each agent adds unique capability, not just throughput)
- [ ] Communication topology is explicit (hub-and-spoke by default)
- [ ] Post-mortem is planned
