---
name: devex-github-baseline-extraction
description: This skill should be used when the user asks to "extract devex baseline metrics", "collect PR cycle time metrics", "analyze repository PR health", "devex baseline", "developer experience baseline", "PR cycle time analysis", "engineering velocity metrics", "tier 1 metrics", "extract M1-M9 metrics", or wants to measure developer productivity baseline (M1-M9) from GitHub PR data. For CI/CD metrics use devex-github-ci-infrastructure-extraction, for review/workflow metrics use devex-github-workflow-quality-extraction, for codebase health use devex-github-codebase-health-extraction.
---

# GitHub DevEx Baseline Extraction

Extract baseline developer experience metrics (M1-M9) from GitHub repositories to measure engineering velocity, code review efficiency, and stability.

## Required Input

Always ask user for:
1. **Repository** - GitHub URL (e.g., `https://github.com/org/repo`) or local clone path
2. **Output directory** - Where to save extraction results

Do not proceed without both inputs.

## Rules

- Use tools. Do not describe commands in markdown blocks.
- Use `generate_devex_summary.py` to create devex_summary.json. Do not generate this file via LLM output.
- Execute scripts in order: collect_tier1_metrics.py → generate_devex_summary.py
- If GitHub auth fails, still run generate_devex_summary.py (it handles missing data)
- Default period is 180 days.

## Purpose

Collect quantitative baseline metrics from GitHub to:
- Identify friction hotspots in development workflows
- Measure improvement over time
- Correlate with qualitative developer interview findings
- Establish engineering health benchmarks

## Intent

- Accuracy of reported metrics > speed of collection. If a GitHub API call fails or returns partial data, report the gap explicitly in the output rather than estimating or interpolating values.
- Always use the provided Python scripts to generate output files (especially `devex_summary.json`). Never produce metric values via LLM generation — every number must trace back to an API response or git log entry.
- "Good" = all M1-M9 metrics sourced from actual data, validation spot-checks pass, and any missing metrics are clearly marked as unavailable with the reason.

## Metrics Overview

| ID | Metric | Category | Source |
|----|--------|----------|--------|
| M1 | PR Cycle Time | Velocity | GitHub API |
| M2 | PR Size | Complexity | GitHub API |
| M3 | Time to First Review | Review Efficiency | GitHub API |
| M4 | Review Comments per PR | Review Depth | GitHub API |
| M5 | Commits per PR | Change Scope | GitHub API |
| M6 | PR Rejection Rate | Quality Gate | GitHub API |
| M7 | Revert Rate | Stability | Git Log |
| M8 | Hotfix Frequency | Stability | Git Log |
| M9 | Commit Frequency by Author | Distribution | Git Log |

### M7 Revert Detection Patterns

Detects reverts using multiple keywords (case-insensitive):
- `revert`, `rollback`, `roll back`, `undo`, `backing out`

### M8 Hotfix Detection Patterns

Detects hotfixes using:
- **Commit messages**: `hotfix`, `hot-fix`, `critical fix`, `emergency`, `urgent`, `prod fix`, `production fix`, `[p0]`, `[p1]`, `[sev0]`, `[sev1]`
- **Branch patterns**: `hotfix/`, `hot-fix/`, `emergency/`

For detailed metric definitions and interpretation guidance, see `references/metrics-definitions.md`.

## Prerequisites

Before running extraction:

1. **gh CLI** - Install and authenticate with organization access
   ```bash
   gh auth login
   gh auth status  # Verify access
   ```

2. **jq** - JSON processor for parsing API responses
   ```bash
   brew install jq  # macOS
   ```

3. **Python 3.8+** - For aggregation script
   ```bash
   python3 --version
   ```

4. **Local git clone** - Required for stability metrics (M7-M9)
   ```bash
   git clone https://github.com/org/repo /path/to/repo
   ```

## Extraction Workflow

### Step 1: Run Collection Script

Execute the extraction script with required parameters:

```bash
python3 ${CLAUDE_SKILL_ROOT}/scripts/collect_tier1_metrics.py <org/repo> <output_dir> [since_date] [git_clone_path]
```

**Parameters:**
- `org/repo` - GitHub repository (e.g., `myorg/backend`)
- `output_dir` - Directory for output files
- `since_date` - Start date (optional, default: 180 days ago, format: YYYY-MM-DD)
- `git_clone_path` - Local clone path (optional, required for M7-M9 stability metrics)

**Example:**
```bash
python3 ${CLAUDE_SKILL_ROOT}/scripts/collect_tier1_metrics.py myorg/backend ./output 2025-01-01 /path/to/backend
```

**Output structure:**
```
output/
└── backend/
    ├── tier1/
    │   ├── prs.jsonl          # Per-PR metrics in JSON Lines format
    │   └── stability.json     # Stability metrics (M7-M9)
    ├── backend_tier1_summary.json
    └── backend_tier1_summary.csv
```

### Step 2: Generate DevEx Summary (Required)

Generate validated `devex_summary.json` using Pydantic schema. **This step is mandatory.**

Run from the skill's scripts directory:

```bash
python3 ${CLAUDE_SKILL_ROOT}/scripts/generate_devex_summary.py \
  {output_dir}/{repo_name}/tier1 \
  {final_output_path}/devex_summary.json \
  --period-days 180 \
  --repository "{org/repo}"
```

**Parameters:**
- `tier1_dir` - Directory containing stability.json and prs.jsonl (from Step 1)
- `output_path` - Path to write devex_summary.json
- `--period-days` - Time period in days (default: 180)
- `--repository` - Repository name (e.g., "myorg/backend")

**Example:**
```bash
python3 ${CLAUDE_SKILL_ROOT}/scripts/generate_devex_summary.py \
  ./output/backend/tier1 \
  ./output/devex_summary.json \
  --period-days 180 \
  --repository "myorg/backend"
```

**CRITICAL:**
- Always run this script even if Step 1 fails or produces partial data
- The script handles missing data gracefully and outputs a valid schema
- NEVER generate devex_summary.json via LLM output - always use this script

### Step 3: Run Aggregation Script (Optional)

Generate detailed summary statistics from raw data:

```bash
python3 ${CLAUDE_SKILL_ROOT}/scripts/parse_tier1_metrics.py <tier1_dir> <output_dir>
```

**Example:**
```bash
python3 ${CLAUDE_SKILL_ROOT}/scripts/parse_tier1_metrics.py output/backend/tier1 output/backend
```

**Output files:**
- `{repo}_tier1_summary.json` - Aggregated statistics (median, mean, p90)
- `{repo}_tier1_summary.csv` - Flat format for spreadsheet analysis

### Step 4: Validate Results

Spot-check metrics accuracy:

1. **Cycle time validation** - Pick a random merged PR and manually calculate:
   ```bash
   gh pr view <number> --json createdAt,mergedAt
   # Calculate: (mergedAt - createdAt) in hours
   ```

2. **Revert count validation** - Compare with git log:
   ```bash
   git log --oneline --grep="revert" -i --since="YYYY-MM-DD" | wc -l
   ```

## Performance Optimization

The script uses parallel processing for large repositories:

- **Default:** 10 concurrent API workers
- **Processing rate:** ~280 PRs per minute
- **Adjustable:** Modify `parallelism=10` in script

For repositories with >500 PRs, consider:
- Narrowing the date range
- Running during off-peak hours (API rate limits)

## Output Format

### JSONL Record Structure (per PR)

```json
{
  "repository": "org/repo",
  "pr_number": 123,
  "author": "username",
  "created_at": "2025-01-15T10:00:00Z",
  "merged_at": "2025-01-15T14:30:00Z",
  "status": "merged",
  "is_bot": false,
  "metrics": {
    "m1_cycle_time_hours": 4.5,
    "m2_additions": 150,
    "m2_deletions": 30,
    "m2_changed_files": 5,
    "m3_time_to_first_review_hours": 1.2,
    "m4_review_comments": 3,
    "m5_commits": 2
  }
}
```

### Summary Statistics Structure

```json
{
  "repository": "org/repo",
  "pr_metrics": {
    "m1_cycle_time": {"median_hours": 18.5, "p90_hours": 48.2},
    "m6_rejection_rate": {"rate_pct": 8.0}
  },
  "stability_metrics": {
    "m7_revert_rate": 0.02,
    "m8_hotfix_count": 12,
    "m8_hotfix_per_week": 1.5
  }
}
```

## Common Issues and Solutions

### gh auth expired

Re-authenticate when rate limit or auth errors occur:
```bash
gh auth login
gh auth status
```

### Shallow clone warning

Stability metrics require full git history:
```bash
git fetch --unshallow  # Convert shallow to full clone
```

### API rate limiting

The script implements exponential backoff (60s → 120s → 240s). For persistent issues:
- Wait 1 hour for rate limit reset
- Use a GitHub token with higher limits

### grep returns exit code 1

When using `set -o pipefail`, wrap grep with fallback:
```bash
{ grep -iE "pattern" || true; }
```

For additional patterns and solutions, see `references/patterns.md`.

## Multi-Repository Extraction

To extract metrics across multiple repositories:

```bash
#!/bin/bash
REPOS=("org/repo1" "org/repo2" "org/repo3")
OUTPUT_DIR="./metrics_output"
SINCE="2025-01-01"

for repo in "${REPOS[@]}"; do
  repo_name="${repo##*/}"
  clone_path="/path/to/clones/$repo_name"
  python3 ${CLAUDE_SKILL_ROOT}/scripts/collect_tier1_metrics.py "$repo" "$OUTPUT_DIR" "$SINCE" "$clone_path"
done

# Run aggregation for each repo
for repo in "${REPOS[@]}"; do
  repo_name="${repo##*/}"
  python3 ${CLAUDE_SKILL_ROOT}/scripts/parse_tier1_metrics.py "$OUTPUT_DIR/$repo_name/tier1" "$OUTPUT_DIR/$repo_name"
done
```

## Scripts Reference

### collect_tier1_metrics.py

Main extraction script located in `scripts/`. Features:
- GitHub CLI (gh) API calls via subprocess
- Parallel processing (10 workers via ThreadPoolExecutor)
- Bot detection (dependabot, renovate, github-actions)
- Rate limit handling with exponential backoff (60s → 120s → 240s)
- Zero external dependencies (uses gh CLI and git)

### parse_tier1_metrics.py

Aggregation script located in `scripts/`. Features:
- JSONL parsing
- Statistical calculations (median, mean, p90)
- CSV export for spreadsheet analysis
- Bot/human PR separation

## Additional Resources

### Reference Files

- **`references/metrics-definitions.md`** - Detailed M1-M9 definitions, formulas, and interpretation guidance
- **`references/patterns.md`** - Bash scripting patterns for GitHub API, pagination, parallel processing

### Example Files

- **`examples/implementation-plan-template.md`** - Template for planning metrics extraction projects

### Scripts

- **`scripts/collect_tier1_metrics.py`** - Main extraction script (raw data collection)
- **`scripts/generate_devex_summary.py`** - Generate validated devex_summary.json (Pydantic schema)
- **`scripts/parse_tier1_metrics.py`** - Aggregation and statistics script
- **`scripts/generate_metrics_summary.py`** - Customer-friendly metrics summary
