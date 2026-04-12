# DevEx Baseline Metrics Extraction — Implementation Plan Template

## Parent Work Package

[Link to parent work package]

---

## Context

**Project:** [Project name]

**Goal:** Collect baseline metrics across [N] repositories to understand development workflow health and identify friction hotspots.

**Target repositories:**
- [ ] org/repo-1
- [ ] org/repo-2
- [ ] org/repo-3

**Current state:**
- [ ] `gh` CLI is available and authenticated with org access
- [ ] Local clones exist for stability metrics (M7-M9)
- [ ] Output directory created

---

## Acceptance Criteria

- [ ] `collect_tier1_metrics.py` script accepts `org/repo` and output directory as arguments
- [ ] Script extracts all 9 metrics (M1-M9) for target repositories
- [ ] Output is valid JSONL that can be parsed by downstream tools
- [ ] Script handles API rate limiting gracefully (exponential backoff)
- [ ] Bot-authored PRs are flagged separately in output
- [ ] Validation: Cycle time calculation matches manual spot-check

---

## Files to Create/Use

| File | Purpose |
|------|---------|
| `scripts/metrics/github/collect_tier1_metrics.py` | Main extraction script for M1-M9 |
| `scripts/metrics/github/parse_tier1_metrics.py` | JSON aggregation and CSV output |
| `output/{repo}_prs.jsonl` | Per-PR metrics output |
| `output/{repo}_stability.json` | Stability metrics output |
| `output/{repo}_summary.json` | Aggregated statistics |
| `output/{repo}_summary.csv` | Spreadsheet-friendly format |

---

## Implementation Steps

### Step 1: Environment Setup

**What:** Verify prerequisites and prepare environment

**Tasks:**
1. Verify `gh` CLI authentication: `gh auth status`
2. Verify `jq` is installed: `jq --version`
3. Verify Python 3.8+: `python3 --version`
4. Create output directory: `mkdir -p ./output`
5. Clone repositories if needed for stability metrics

**Validation:**
- [ ] All tools available
- [ ] Auth has access to target repositories

---

### Step 2: Extract Metrics for Each Repository

**What:** Run extraction script on each target repository

**Command template:**
```bash
python3 ${CLAUDE_SKILL_ROOT}/scripts/collect_tier1_metrics.py <org/repo> ./output <date> <clone_path>
```

**Execution plan:**

| Repository | Clone Path | Command |
|------------|------------|---------|
| org/repo-1 | /path/to/repo-1 | `python3 ${CLAUDE_SKILL_ROOT}/scripts/collect_tier1_metrics.py org/repo-1 ./output 2025-01-01 /path/to/repo-1` |
| org/repo-2 | /path/to/repo-2 | `python3 ${CLAUDE_SKILL_ROOT}/scripts/collect_tier1_metrics.py org/repo-2 ./output 2025-01-01 /path/to/repo-2` |
| org/repo-3 | /path/to/repo-3 | `python3 ${CLAUDE_SKILL_ROOT}/scripts/collect_tier1_metrics.py org/repo-3 ./output 2025-01-01 /path/to/repo-3` |

**Expected output per repository:**
- `{repo}_prs.jsonl` - One JSON object per PR
- `{repo}_stability.json` - Revert rate, hotfix count, author distribution

**Validation:**
- [ ] No API errors during extraction
- [ ] Output files are valid JSON/JSONL

---

### Step 3: Generate Aggregated Statistics

**What:** Run aggregation script to generate summaries

**Command:**
```bash
python3 ${CLAUDE_SKILL_ROOT}/scripts/parse_tier1_metrics.py ./output ./output
```

**Expected output per repository:**
- `{repo}_summary.json` - Aggregated statistics
- `{repo}_summary.csv` - Flat CSV format

**Validation:**
- [ ] Summary files generated for all repositories
- [ ] Key metrics are non-null

---

### Step 4: Validate Results

**What:** Spot-check metrics accuracy

**Validation tasks:**

1. **Cycle time validation:**
   ```bash
   # Pick a random merged PR
   gh pr view <number> --json createdAt,mergedAt
   # Manually calculate hours between timestamps
   # Compare with script output
   ```

2. **Revert count validation:**
   ```bash
   # Compare with git log
   cd /path/to/clone
   git log --oneline --grep="revert" -i --since="<since_date>" | wc -l
   # Compare with script output
   ```

3. **PR count validation:**
   ```bash
   # Compare total PRs with GitHub UI
   # Filter by merged date range
   ```

**Validation checklist:**
- [ ] Cycle time matches manual calculation (within 0.1h)
- [ ] Revert count matches git log output
- [ ] Total PR count matches GitHub UI

---

### Step 5: Document Findings

**What:** Record key metrics and observations

**Summary template:**

| Repository | Merged PRs | Median Cycle Time | Rejection Rate | Revert Rate |
|------------|------------|-------------------|----------------|-------------|
| org/repo-1 | X | Y hours | Z% | W% |
| org/repo-2 | X | Y hours | Z% | W% |
| org/repo-3 | X | Y hours | Z% | W% |

**Observations:**
- [Notable patterns or outliers]
- [Potential friction hotspots identified]
- [Comparison with industry benchmarks]

---

## Dependencies

- `gh` CLI authenticated with org access
- `jq` for JSON processing
- Python 3.8+ for aggregation script
- Local git clones for stability metrics (M7-M9)

---

## Estimated Effort

| Step | Effort |
|------|--------|
| Environment setup | 15 min |
| Extraction (per repo) | 2-5 min |
| Aggregation | 1 min |
| Validation | 15 min |
| Documentation | 15 min |

**Total per repository:** ~35-45 minutes

---

## Troubleshooting

### gh auth expired

```bash
gh auth login
gh auth status
```

### Rate limit hit

Script implements exponential backoff. If persistent:
- Wait 1 hour for reset
- Run during off-peak hours

### Shallow clone warning

```bash
cd /path/to/clone
git fetch --unshallow
```

### Large repository (>500 PRs)

- Narrow date range
- Expect 1-2 minutes extraction time

---

## Next Steps

After baseline extraction:
1. [ ] Compare metrics across repositories
2. [ ] Identify top friction hotspots
3. [ ] Correlate with developer interview findings
4. [ ] Set improvement targets
5. [ ] Schedule re-measurement (monthly/quarterly)
