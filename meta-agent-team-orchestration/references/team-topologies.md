# Team Organization Frameworks

Literature-backed frameworks for deciding how to structure agent teams.

## Brooks' Surgical Team Model (The Mythical Man-Month, 1975)

Fred Brooks proposed the "surgical team" based on Harlan Mills's model. Key insight: **a team of 10 should have only 3 doing core work**, with the remaining 7 in supporting roles.

### Application to Agent Teams

The surgical team maps directly to agent team design:

| Surgical Team Role | Agent Team Equivalent | Purpose |
|---|---|---|
| Surgeon | Lead analyst / primary worker | Does the core intellectual work |
| Copilot | Verifier / secondary analyst | Independently checks the surgeon's work |
| Administrator | Team lead (the orchestrator) | Coordinates, routes messages, manages lifecycle |
| Editor | Reviewer | Reviews outputs before they advance |
| Toolsmith | Utility agent | Handles mechanical tasks (data collection, formatting) |

**Key takeaway:** Not every agent should be doing "the hard work." Having a dedicated verifier and reviewer adds more value than adding a third analyst.

### Brooks' Law: Communication Overhead

```
Communication paths = n * (n-1) / 2
```

| n | Paths | Implication |
|---|---|---|
| 2 | 1 | Trivial coordination |
| 3 | 3 | Manageable |
| 4 | 6 | Getting expensive |
| 5 | 10 | Each new agent adds 4 paths |
| 6 | 15 | Almost never justified |

For agent teams, communication overhead manifests as:
- Token cost per message sent/received
- Latency per hop (inbox polling intervals)
- Context window consumption (each agent reads shared docs independently)

**Rule of thumb:** Never exceed 5 agents. Prefer 2-3 for most tasks.

---

## Team Topologies Framework (Skelton & Pais, 2019)

Team Topologies defines four fundamental team types:

| Type | Purpose | Agent Team Mapping |
|------|---------|-------------------|
| **Stream-aligned** | End-to-end responsibility for a value stream | Primary worker agents (analyst, implementer) |
| **Enabling** | Temporarily helps other teams upskill | Reviewer agent (provides feedback that improves outputs) |
| **Complicated subsystem** | Wraps specialized expertise | Domain-expert agent (security, performance, etc.) |
| **Platform** | Provides infrastructure/services to others | Team lead (provides coordination infrastructure) |

### Interaction Modes

Team Topologies defines three interaction modes between teams:

| Mode | Description | Agent Team Application |
|------|-------------|----------------------|
| **Collaboration** | Close, bidirectional work | Peer-to-peer agent messaging (expensive, use sparingly) |
| **X-as-a-Service** | One team provides, another consumes | Hub-and-spoke: workers produce, lead consumes and routes |
| **Facilitating** | One team coaches another temporarily | Reviewer providing feedback to workers |

**Key takeaway:** Default to X-as-a-Service (hub-and-spoke) for agent teams. Use Collaboration only when two agents need iterative back-and-forth on a shared problem.

---

## Google Research: Scaling Agent Systems (2025)

Google's research paper "Towards a Science of Scaling Agent Systems" evaluated 180 agent configurations. Key findings:

### Performance by Task Type

| Task Type | Multi-agent Impact | Recommendation |
|-----------|-------------------|----------------|
| Parallelizable tasks | **+81% improvement** | Use teams |
| Sequential tasks | **-70% degradation** | Use single agent |
| Tasks requiring 16+ tools | Coordination tax increases disproportionately | Keep agents specialized (fewer tools each) |

### Error Amplification

| Architecture | Error Amplification Factor |
|---|---|
| Single agent | 1x (baseline) |
| Hub-and-spoke (orchestrator) | **4.4x** (orchestrator catches errors) |
| Peer-to-peer (no orchestrator) | **17x** (errors propagate unchecked) |

**Key takeaway:** Always have a central orchestrator (team lead or reviewer) that validates outputs before they propagate. The hub-and-spoke pattern contains errors 4x better than peer-to-peer.

### When Multi-Agent Outperforms Single-Agent

Multi-agent systems outperform when ALL of these are true:
1. Task can be decomposed into independent subtasks
2. Subtasks benefit from different expertise/focus
3. The coordination cost is less than the parallelization gain
4. A validation mechanism exists (reviewer, orchestrator)

---

## Synthesis: Decision Framework for Agent Teams

Combining all three frameworks:

| Decision Factor | Brooks | Team Topologies | Google Research |
|---|---|---|---|
| Max team size | 3 core workers | N/A (organizational) | Fewer is better for agents |
| Communication pattern | Minimize paths | X-as-a-Service default | Hub-and-spoke (4.4x vs 17x) |
| Specialization | Surgical roles | Four team types | Specialized > generalist |
| When to avoid teams | Always (prefer small) | When collaboration overhead exceeds value | Sequential tasks (-70%) |

### The Combined Rule

> **Start with the smallest team that covers the required expertise domains. Default to hub-and-spoke communication. Add agents only when they bring a capability the existing team lacks, not when they duplicate existing capability.**

---

## Sources

- Brooks, F. P. (1975). *The Mythical Man-Month: Essays on Software Engineering*. Addison-Wesley.
- Skelton, M. & Pais, M. (2019). *Team Topologies: Organizing Business and Technology Teams for Fast Flow*. IT Revolution Press.
- Google Research (2025). "Towards a Science of Scaling Agent Systems: When and Why Agent Systems Work." https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/
- Deloitte (2026). "Unlocking Exponential Value with AI Agent Orchestration." Technology, Media & Telecom Predictions.
