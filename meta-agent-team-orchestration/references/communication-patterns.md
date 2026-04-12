# Communication Patterns for Agent Teams

Detailed guide to choosing and implementing communication topologies.

## Three Core Topologies

### 1. Hub-and-Spoke (Centralized Orchestrator)

```
        Worker A
          ↕
Worker B ← Lead → Worker C
          ↕
       Reviewer
```

**How it works:** All communication flows through the team lead. Workers send results to the lead, who routes them to the next recipient. No direct worker-to-worker messages.

**Strengths:**
- Error containment: Lead validates every output before forwarding (4.4x vs 17x error amplification)
- Clear accountability: Lead knows exact state of every work stream
- Simple debugging: All messages visible in lead's inbox

**Weaknesses:**
- Lead becomes a bottleneck: Every handoff requires lead to poll, read, and forward
- Latency: Each hop adds ~60 seconds (polling interval) + processing time
- Token overhead: Lead processes every message twice (read + forward)

**Best for:**
- Teams of 3-5 agents
- Tasks where error containment matters more than speed
- When the lead needs to synthesize outputs from multiple workers

**Implementation notes:**
- Set inbox polling to 60-second intervals (balance between latency and token cost)
- Forward messages immediately after reading, don't batch
- Track forwarded messages to avoid duplicates

---

### 2. Linear Chain (Pipeline)

```
Agent A → Agent B → Agent C → Agent D
```

**How it works:** Each agent's output is the next agent's input. The team lead monitors but doesn't route — agents send directly to the next in the chain.

**Strengths:**
- No routing bottleneck
- Natural for sequential workflows (investigate → review → plan → implement)
- Each agent has clear input/output contract

**Weaknesses:**
- Blocked by the slowest agent
- No parallelism
- One agent's error propagates through the entire chain

**Best for:**
- Sequential workflows where order matters
- Small teams (2-3 agents)
- When each step has a well-defined input/output contract

**Implementation notes:**
- Each agent's prompt should specify exactly who to send results to
- The lead monitors via inbox but doesn't actively route
- Include error handling: if Agent B rejects Agent A's output, it sends feedback directly to A

---

### 3. Peer-to-Peer (Decentralized)

```
Agent A ←→ Agent B
  ↕    ✕     ↕
Agent C ←→ Agent D
```

**How it works:** Agents communicate directly with whoever they need. No central router.

**Strengths:**
- Lowest latency (no routing hops)
- Natural for collaborative tasks where agents iterate together
- Resilient: if one agent fails, others continue

**Weaknesses:**
- Error amplification: 17x without a validation checkpoint
- Hard to monitor: lead doesn't see all communication
- Coordination complexity: each agent must know about all others

**Best for:**
- Rarely. Almost never optimal for agent teams.
- Only when two agents need rapid bidirectional iteration on a shared artifact.

**Implementation notes:**
- If using peer-to-peer, add a dedicated reviewer who receives the final output
- The team config file at `~/.claude/teams/{name}/config.json` lets agents discover each other by name

---

## Hybrid Patterns

### Hub-and-Spoke with Peer Exceptions

```
Worker A ──→ Lead ──→ Reviewer
Worker B ──→ Lead ──→ Reviewer
Worker A ←→ Worker B  (exception: iterating on shared analysis)
```

**When to use:** When two workers share a domain and benefit from direct collaboration, but the overall structure is still hub-and-spoke.

### Phased Topology Shift

```
Phase 1: Hub-and-spoke (investigation)
Phase 2: Linear chain (review → planning)
Phase 3: Hub-and-spoke (implementation)
```

**When to use:** When the team's communication needs change across phases. Start with hub-and-spoke for parallel investigation, shift to linear for sequential planning.

---

## Decision Matrix: Choosing a Topology

| Factor | Hub-and-Spoke | Linear Chain | Peer-to-Peer |
|--------|--------------|--------------|--------------|
| Task parallelizable? | Yes → Best | No → Best | Collaborative → Consider |
| Error containment critical? | Yes → Best | Moderate | No → Risky |
| Speed critical? | Bottleneck risk | Sequential bottleneck | Fastest |
| Team size > 3? | Best | Unwieldy | Very unwieldy |
| Lead needs synthesis? | Yes → Required | Not needed | Not needed |

**Default recommendation:** Hub-and-spoke for teams of 3+, linear chain for pairs, never pure peer-to-peer.

---

## Inbox Polling Strategy

The team lead's polling interval is a key efficiency lever:

| Interval | Token Cost | Latency | When to Use |
|----------|-----------|---------|-------------|
| 10 seconds | Very high | Low | Never for normal work |
| 30 seconds | High | Low-Medium | Time-critical tasks with user waiting |
| 60 seconds | Medium | Medium | **Default recommendation** |
| 120 seconds | Low | High | Long-running agents (>10 min per task) |

**Adaptive polling:** Start at 60 seconds. If agents complete work quickly (<2 min), reduce to 30. If agents take >5 min per task, increase to 120.

---

## Message Forwarding Best Practices

When acting as the hub in hub-and-spoke:

1. **Consolidate before forwarding.** If two workers produce related reports, synthesize them into one message for the reviewer. Don't send them separately.

2. **Include context in forwards.** Don't just paste the report — add what you need from the recipient: "Please review this root-cause analysis. Specifically check: (a) are the commit verdicts justified by the diffs? (b) is the priority ranking sound?"

3. **Set expectations.** Tell the reviewer how many reports are incoming: "You will receive 2 reports. Review both before responding." This prevents the reviewer from going idle after the first.

4. **Track state.** Keep a mental model of: which agents have delivered, which are still working, what's been reviewed, what's pending.
