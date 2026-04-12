# Interview Framework for Team Design

Structured question bank for classifying tasks and designing optimal agent teams.

## Core Interview (4 Questions — Always Ask)

These four questions are mandatory and should be asked using the AskUserQuestion tool in a single call.

### Q1: Task Nature
```
question: "What is the core task you need the team for?"
header: "Task type"
options:
  - label: "Investigation/analysis"
    description: "Research, root-cause analysis, auditing, understanding existing systems"
  - label: "Creation/generation"
    description: "Writing code, designing systems, producing new deliverables"
  - label: "Verification/validation"
    description: "Testing, reviewing, confirming existing findings"
  - label: "Mixed"
    description: "Combination — e.g., investigate then plan fixes"
```

### Q2: Parallelizability
```
question: "Can the work be split into independent streams, or must it flow sequentially?"
header: "Parallelism"
options:
  - label: "Fully parallel"
    description: "Independent subtasks with no dependencies between them"
  - label: "Mostly parallel"
    description: "Some dependencies exist, but multiple streams can start independently"
  - label: "Sequential pipeline"
    description: "Each step's output feeds the next — strict ordering required"
  - label: "Exploratory"
    description: "Unknown structure — need to investigate before knowing the shape"
```

### Q3: Criticality
```
question: "How critical are the outputs? This determines review intensity."
header: "Criticality"
options:
  - label: "Production-impacting"
    description: "Affects real users, deployments, or business decisions"
  - label: "Internal deliverable"
    description: "Work packages, plans, documentation for internal use"
  - label: "Exploratory research"
    description: "Findings inform future decisions, not immediate action"
```

### Q4: Constraints
```
question: "Any specific constraints for this team?"
header: "Constraints"
options:
  - label: "Cost-sensitive"
    description: "Prefer Sonnet/Haiku over Opus where possible"
  - label: "Quality-first"
    description: "Prefer Opus for all reasoning tasks, cost is secondary"
  - label: "Speed-first"
    description: "Maximize parallelism, minimize review cycles"
  - label: "Balanced (Recommended)"
    description: "Opus for reasoning, Sonnet for verification, standard review gates"
```

---

## Follow-Up Questions (Conditional)

Ask these based on core interview answers:

### If Task Nature = "Investigation/analysis"
```
question: "Is there existing data/findings to verify, or is this a fresh investigation?"
header: "Starting point"
options:
  - label: "Verify existing findings"
    description: "Someone already investigated — we need to confirm and build on it"
  - label: "Fresh investigation"
    description: "Starting from scratch with raw data"
```

**Impact on design:**
- Verify existing → Lean pair (verifier + analyst), lower complexity
- Fresh investigation → Full team with independent streams, higher complexity

### If Task Nature = "Mixed"
```
question: "What's the breakdown between investigation and creation?"
header: "Mix ratio"
options:
  - label: "Mostly investigation, then brief planning"
    description: "80% research/analysis, 20% action items"
  - label: "Equal parts"
    description: "50% investigation, 50% design/creation"
  - label: "Brief investigation, then mostly creation"
    description: "20% analysis, 80% building/designing"
```

**Impact on design:**
- Mostly investigation → Design team around investigation, add planner as last-phase lazy spawn
- Equal parts → Balanced team with phased topology shift
- Mostly creation → Design team around creation, add brief investigation phase first

### If Parallelism = "Exploratory"
```
question: "How many domains or areas need exploring?"
header: "Exploration scope"
options:
  - label: "Single domain, deep dive"
    description: "One area to explore thoroughly"
  - label: "Multiple domains, breadth-first"
    description: "2-4 areas to explore in parallel"
  - label: "Unknown scope"
    description: "Start exploring and see what we find"
```

**Impact on design:**
- Single domain → Single agent or lean pair
- Multiple domains → One agent per domain (parallel)
- Unknown scope → Start with 1 explorer, scale based on findings

### If Criticality = "Production-impacting"
```
question: "Should the reviewer be a dedicated teammate or should I (team lead) review?"
header: "Review model"
options:
  - label: "Dedicated reviewer teammate (Recommended)"
    description: "Separate Opus agent focused only on quality. Independent perspective."
  - label: "Team lead reviews"
    description: "You review outputs directly. Faster but less independent."
  - label: "Dedicated reviewer + user approval"
    description: "Both agent reviewer AND user sign-off before advancing. Maximum rigor."
```

---

## Mapping Interview Answers to Team Design

### Task Nature → Primary Roles

| Task Nature | Primary Roles | Notes |
|-------------|--------------|-------|
| Investigation | Analyst + Verifier | Independent streams, cross-check findings |
| Creation | Implementer + Reviewer | Build and review cycle |
| Verification | Verifier (primary) + Spot-checker | Measure, don't analyze |
| Mixed | Analyst + Planner + Reviewer | Phased approach |

### Parallelism → Topology

| Parallelism | Topology | Spawning Strategy |
|-------------|----------|-------------------|
| Fully parallel | Hub-and-spoke | All workers spawn immediately |
| Mostly parallel | Hub-and-spoke with lazy deferred agents | Phase 1 agents immediate, Phase 2 deferred |
| Sequential pipeline | Linear chain | Spawn each agent when previous completes |
| Exploratory | Start with 1, scale | Spawn explorer first, add agents as scope clarifies |

### Criticality → Review Gates

| Criticality | Review Gate | Model for Reviewer |
|-------------|------------|-------------------|
| Production-impacting | Dedicated reviewer (Opus) for every output | Opus |
| Internal deliverable | Team lead reviews, escalate if uncertain | N/A (lead reviews) |
| Exploratory | Spot-check by lead, no formal gate | N/A |

### Constraints → Model Selection

| Constraint | Analyst Model | Verifier Model | Reviewer Model | Planner Model |
|-----------|--------------|----------------|---------------|---------------|
| Cost-sensitive | Sonnet | Sonnet | Sonnet | Sonnet |
| Quality-first | Opus | Opus | Opus | Opus |
| Speed-first | Sonnet | Sonnet | Skip reviewer | Sonnet |
| Balanced | Opus | Sonnet | Opus | Opus |

---

## Edge Cases

### "I just want to try agent teams"
If the user doesn't have a clear task but wants to experiment:
- Suggest a low-risk practice task (e.g., "have 2 agents independently review a file and compare findings")
- Use Sonnet for all roles to minimize cost
- Include post-mortem to learn from the experiment

### "This task is urgent"
If the user emphasizes speed:
- Reduce team size to minimum viable (2 agents)
- Skip formal review gates (lead does spot-checks)
- Use 30-second polling intervals
- Use Sonnet for all roles

### "I want maximum quality"
If the user emphasizes rigor:
- Use Opus for all roles
- Dedicated reviewer for every output
- Plan approval mode for planning agents
- Consider adding user approval gates at key checkpoints

### "I'm not sure how many subtasks there are"
If the task structure is unclear:
- Start with a single Explore agent to map the scope
- Based on their findings, design the full team
- This is a two-phase approach: Phase 0 (scope) → Phase 1+ (execution)
