# Metrics Definitions Reference

Detailed definitions, formulas, and interpretation guidance for DevEx baseline metrics M1-M9.

## PR Metrics (M1-M6)

These metrics are extracted from the GitHub API and measure PR workflow efficiency.

---

### M1: PR Cycle Time

**Definition:** Time from PR creation to merge.

**Formula:**
```
cycle_time_hours = (merged_at - created_at) / 3600
```

**Data source:** GitHub REST API `/repos/{owner}/{repo}/pulls`

**Fields used:**
- `created_at` - ISO 8601 timestamp when PR was opened
- `merged_at` - ISO 8601 timestamp when PR was merged

**Interpretation:**
| Range | Assessment |
|-------|------------|
| < 4 hours | Excellent - fast iteration |
| 4-24 hours | Good - healthy review cycle |
| 24-72 hours | Moderate - potential bottlenecks |
| > 72 hours | Slow - investigate blockers |

**Exclusions:**
- Draft PRs (not ready for review)
- Bot-authored PRs (automated dependency updates)
- Rejected PRs (closed without merge)

**Aggregations:**
- `median_hours` - Typical PR cycle time (preferred over mean)
- `p90_hours` - 90th percentile, identifies outliers
- `mean_hours` - Average (can be skewed by outliers)

---

### M2: PR Size

**Definition:** Volume of code changes in a PR.

**Formula:**
```
total_changes = additions + deletions
```

**Data source:** GitHub REST API `/repos/{owner}/{repo}/pulls/{pull_number}`

**Fields used:**
- `additions` - Lines added
- `deletions` - Lines removed
- `changed_files` - Number of files modified

**Interpretation:**
| Additions | Assessment |
|-----------|------------|
| < 100 | Small - easy to review |
| 100-400 | Medium - reasonable scope |
| 400-1000 | Large - consider splitting |
| > 1000 | Very large - hard to review thoroughly |

**Why it matters:**
- Larger PRs correlate with longer review times
- Smaller PRs get more thorough reviews
- Large PRs increase risk of bugs slipping through

**Aggregations:**
- `median_additions` - Typical PR size
- `p90_additions` - Identifies large outliers
- `total_additions/deletions` - Overall code churn

---

### M3: Time to First Review

**Definition:** Time from PR creation until first review is submitted.

**Formula:**
```
time_to_first_review = (first_review_submitted_at - created_at) / 3600
```

**Data source:** GitHub REST API `/repos/{owner}/{repo}/pulls/{pull_number}/reviews`

**Fields used:**
- `submitted_at` - When review was submitted
- Sorted by `submitted_at` ascending, take first

**Special values:**
- `"no_review"` - PR was merged without any reviews

**Interpretation:**
| Range | Assessment |
|-------|------------|
| < 2 hours | Excellent - responsive team |
| 2-8 hours | Good - same-day review |
| 8-24 hours | Moderate - next-day review |
| > 24 hours | Slow - review bottleneck |

**Why it matters:**
- Long wait times block developers
- Indicates team availability for reviews
- High "no_review" percentage may indicate process gaps

---

### M4: Review Comments per PR

**Definition:** Number of review comments on a PR.

**Data source:** GitHub REST API `/repos/{owner}/{repo}/pulls/{pull_number}/comments`

**Interpretation:**
| Count | Assessment |
|-------|------------|
| 0 | No inline feedback (may be fine for small PRs) |
| 1-5 | Normal review engagement |
| 5-15 | Thorough review or complex changes |
| > 15 | Extensive discussion - may indicate unclear code |

**Why it matters:**
- Too few comments may indicate rubber-stamping
- Too many may indicate unclear requirements or code
- Useful for identifying PRs that needed significant rework

---

### M5: Commits per PR

**Definition:** Number of commits in a PR.

**Data source:** GitHub REST API `/repos/{owner}/{repo}/pulls/{pull_number}`

**Field used:** `commits`

**Interpretation:**
| Count | Assessment |
|-------|------------|
| 1-3 | Clean - well-organized changes |
| 4-10 | Normal - iterative development |
| > 10 | High - may indicate scope creep or messy history |

**Why it matters:**
- Many commits may indicate iteration during review
- Single commit may indicate squash-merge workflow
- Correlates with PR complexity

---

### M6: PR Rejection Rate

**Definition:** Percentage of PRs closed without being merged.

**Formula:**
```
rejection_rate = rejected_prs / total_prs
```

**Data source:** GitHub REST API - PRs with `state=closed` and `merged_at=null`

**Interpretation:**
| Rate | Assessment |
|------|------------|
| < 5% | Low - most PRs get merged |
| 5-15% | Moderate - some PRs abandoned |
| > 15% | High - investigate reasons |

**Common reasons for rejection:**
- Requirements changed
- Duplicate work
- Approach rejected in review
- Developer left team

**Exclusions:**
- Bot-authored PRs (calculated separately)

---

## Stability Metrics (M7-M9)

These metrics are extracted from git history and measure code stability.

---

### M7: Revert Rate

**Definition:** Percentage of commits that are reverts.

**Formula:**
```
revert_rate = revert_commits / total_commits
```

**Data source:** Git log with `--grep="revert" -i`

**Command:**
```bash
git log --oneline --grep="revert" -i --since="YYYY-MM-DD" | wc -l
```

**Interpretation:**
| Rate | Assessment |
|------|------------|
| < 1% | Excellent - stable codebase |
| 1-3% | Normal - occasional rollbacks |
| > 3% | High - quality or process issues |

**Why it matters:**
- Reverts indicate production issues
- High rate suggests insufficient testing
- Each revert represents developer time lost

---

### M8: Hotfix Frequency

**Definition:** Number of commits tagged as urgent fixes.

**Data source:** Git log with keyword patterns

**Patterns matched (case-insensitive):**
- `hotfix`
- `fix:`
- `urgent`
- `emergency`

**Command:**
```bash
git log --oneline --since="YYYY-MM-DD" --no-merges | grep -iE "(hotfix|fix:|urgent|emergency)" | wc -l
```

**Interpretation:**
| Frequency | Assessment |
|-----------|------------|
| < 5/month | Low - stable releases |
| 5-15/month | Moderate - regular fixes needed |
| > 15/month | High - investigate root causes |

**Why it matters:**
- Hotfixes indicate production issues
- High frequency suggests release quality issues
- Each hotfix disrupts planned work

---

### M9: Commit Frequency by Author

**Definition:** Distribution of commits across team members.

**Data source:** Git shortlog or git log

**Command:**
```bash
git log --since="YYYY-MM-DD" --no-merges --pretty=format:"%an" | sort | uniq -c | sort -rn
```

**Output format:**
```json
[
  {"author": "Alice", "commits": 150},
  {"author": "Bob", "commits": 120},
  {"author": "Charlie", "commits": 80}
]
```

**Interpretation:**
- **Bus factor** - If top 1-2 authors have >80% of commits, knowledge is concentrated
- **Team balance** - Healthy teams have more distributed commits
- **Onboarding** - New team members should show increasing commits over time

**Exclusions:**
- Merge commits (`--no-merges`)

---

## Aggregation Methods

### Median vs Mean

**Prefer median** for most metrics because:
- Resistant to outliers (one 100-hour PR won't skew results)
- Better represents "typical" experience
- More stable over time

**Use mean** when:
- Total throughput matters more than typical
- Outliers are meaningful (e.g., total code churn)

### Percentiles

**p90 (90th percentile):**
- 90% of values are below this
- Useful for identifying "worst case" experiences
- Helps set SLOs (e.g., "90% of PRs merged within 24 hours")

**Calculation:**
```python
def percentile(values, p):
    sorted_values = sorted(values)
    index = (len(sorted_values) - 1) * p / 100
    lower = int(index)
    upper = lower + 1
    weight = index - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight
```

---

## Bot Detection

PRs from automated accounts are flagged separately to avoid skewing human productivity metrics.

**Bot patterns detected:**
- `dependabot`
- `renovate`
- `github-actions`
- `bot` (substring match)

**Why separate:**
- Bot PRs are typically small dependency updates
- Often auto-merged without review
- Don't reflect human development patterns

---

## Data Quality Considerations

### Exclusions

| Exclusion | Reason |
|-----------|--------|
| Draft PRs | Not ready for review |
| Bot PRs | Flagged but not excluded from totals |
| Merge commits | Don't represent actual work |

### Edge Cases

| Case | Handling |
|------|----------|
| PR with no reviews | `m3_time_to_first_review = "no_review"` |
| PR merged same minute as created | Very small cycle time (valid) |
| Empty PR (0 additions) | Included (may be config changes) |

### Date Filtering

All metrics respect the `since_date` parameter:
- PRs: filtered by `merged_at` or `closed_at`
- Commits: filtered by `--since` flag
- Default: 90 days

---

## Benchmarks Reference

Industry benchmarks from DORA and engineering studies:

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| PR Cycle Time | < 1 day | 1-7 days | 1-4 weeks | > 1 month |
| Time to First Review | < 4 hours | < 1 day | < 1 week | > 1 week |
| PR Size (additions) | < 100 | 100-400 | 400-1000 | > 1000 |
| Rejection Rate | < 5% | 5-10% | 10-20% | > 20% |
| Revert Rate | < 1% | 1-3% | 3-5% | > 5% |

*Note: Benchmarks vary by team size, domain, and development methodology.*
