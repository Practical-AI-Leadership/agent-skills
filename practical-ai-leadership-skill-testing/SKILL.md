---
name: practical-ai-leadership-skill-testing
description: This skill should be used when the user asks to "test skill", "test skill determinism", "verify skill consistency", "check skill outputs", "run skill test", "compare skill runs", "validate skill before release", "check for execution issues", or wants to ensure a skill produces consistent results. Uses tmux for true parallel CLI testing. Not for integration-testing the simpleclub-skills CLI tool — use dev-simpleclub-skills-integration-test for that.
version: 1.0.0
---

# Skill Testing

Test skill consistency using real Claude CLI invocations with tmux parallelism.

## Workflow

### Phase 1: Parse Target Skill

From target SKILL.md extract:
- Trigger phrases (from description)
- Test scenarios (from examples)
- Key promises (what it claims to deliver)

### Phase 2: Run Parallel Tests

Use `${CLAUDE_PLUGIN_ROOT}/scripts/run-parallel-tests.sh`:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/run-parallel-tests.sh \
  "[trigger-1] [skill-path]" \
  "[trigger-2] [skill-path]" \
  "[trigger-3] [skill-path]"
```

Script handles:
- tmux installation (brew/apt/yum)
- Session setup and cleanup
- Parallel execution in 3 tmux windows
- Completion tracking via `.done` files
- 10-minute timeout
- 2s delay between launches (rate limiting)
- Debug log at `/tmp/skill-test/debug.log`

**Commands:**
| Command | Action |
|---------|--------|
| `./run-parallel-tests.sh t1 t2 t3` | Run tests |
| `./run-parallel-tests.sh attach` | Watch progress |
| `./run-parallel-tests.sh results` | Show outputs |
| `./run-parallel-tests.sh cleanup` | Kill session |

### Phase 3: Execution Issue Detection

Scan each output file for execution problems. Report all findings regardless of severity.

**Exit Code Patterns** (from debug.log):
```
grep "exit [1-9]" /tmp/skill-test/debug.log
grep "Exit code [1-9]" /tmp/skill-test/t*.txt
```

**Error Indicators** (scan output files):

*Exit/Status:*
| Pattern | Indicates |
|---------|-----------|
| `Exit code [1-9]` | Tool/script failure |
| `exit_code_[1-9]` | JSON-reported failure |
| `"status": "failed"` | Skill step failure |
| `"status": "partial"` | Degraded execution |
| `"status": "skipped"` | Step was skipped |
| `error:` (case-insensitive) | Error message |
| `[ERROR]` or `[WARN]` | Logged issues |
| `FAILED` | Explicit failure marker |

*Argument/Usage:*
| Pattern | Indicates |
|---------|-----------|
| `the following arguments are required` | Missing CLI args |
| `Usage:` followed by exit | Script called incorrectly |
| `Missing required argument` | Skill caller bug |
| `unrecognized arguments` | Wrong args passed |

*JSON/Parsing:*
| Pattern | Indicates |
|---------|-----------|
| `invalid JSON` | JSON parsing failure |
| `JSONDecodeError` | Python JSON parse error |
| `jq: invalid` | jq command failed |
| `Could not load` | File load failure |
| `Warning: Could not` | Non-fatal load issue |

*Dependencies:*
| Pattern | Indicates |
|---------|-----------|
| `command not found` | Missing CLI tool |
| `Required command not found` | Skill dependency missing |
| `ModuleNotFoundError` | Python module missing |
| `ImportError` | Python import failed |
| `Required dependencies not installed` | Skill setup incomplete |
| `pip install` in error context | Dependency hint |
| `brew install` in error context | Dependency hint |

*File/Path:*
| Pattern | Indicates |
|---------|-----------|
| `No such file or directory` | Path resolution failure |
| `Permission denied` | Access issue |
| `Directory does not exist` | Invalid path passed |
| `Results directory does not exist` | Output dir missing |
| `File not found` | Expected file missing |

*API/Network:*
| Pattern | Indicates |
|---------|-----------|
| `rate limit` | API throttling |
| `API error` | External API failure |
| `gh CLI is not authenticated` | GitHub auth missing |
| `gh auth` in error context | Auth setup needed |
| `Max retries exceeded` | Network/API exhaustion |

*Timeout:*
| Pattern | Indicates |
|---------|-----------|
| `timeout` (case-insensitive) | Operation timed out |
| `timed out` | Process killed |
| `exceeded_\d+s` | Semgrep timeout |
| `Scan timed out` | Tool timeout |

*Git/Repository:*
| Pattern | Indicates |
|---------|-----------|
| `Invalid git repository` | Not a git repo |
| `not a git repository` | Git command failed |
| `Shallow clone detected` | Incomplete git history |
| `unbound variable` | Bash strict mode failure |

**Partial Execution Detection:**
- JSON output with `categories.failed > 0`
- JSON output with `categories.timeout > 0`
- JSON output with `categories.skipped > 0`
- Status fields containing "partial", "failed", "error", "skipped"
- Semgrep summary showing failed/timeout categories

**Report Format:** For each finding, record:
- Test number (t1/t2/t3)
- Pattern matched
- Line content (truncated to 200 chars)
- File or context where it occurred

### Phase 4: Compare Outputs

Read results from `/tmp/skill-test/t[1-3].txt`.

| Check | Tolerance |
|-------|-----------|
| Structure (headings, sections) | Must match |
| Facts (numbers, conclusions) | Must match |
| Wording | Can vary |

### Phase 5: Promise Verification

Vibe check: Does output deliver what description promises?

### Phase 6: Report

| Component | Content |
|-----------|---------|
| Summary | Scores + verdict |
| Tests | Trigger results table |
| **Execution Issues** | All detected problems from Phase 3 |
| Analysis | Structural/factual comparison |
| Issues | Numbered list with severity |
| **Fix Prompts** | Copy-paste ready fixes |

**Execution Issues Section Format:**
```
## Execution Issues

| Test | Category | Pattern | Context |
|------|----------|---------|---------|
| t1 | Exit/Status | Exit code 2 | detect_monorepo.sh |
| t2 | Exit/Status | "status": "partial" | semgrep scan |
| t3 | Argument/Usage | the following arguments are required | aggregate_findings.py |
| t1 | JSON/Parsing | jq: invalid | collect_tier1_metrics.sh |
| t2 | API/Network | rate limit | gh api call |

Total: X issues detected across Y tests
Categories affected: [list unique categories]
```

If no execution issues found, output:
```
## Execution Issues
None detected.
```

### Phase 7: Fix Prompts

For each issue, output a **markdown code block** for one-click copy.

**Style rules:**
- Keep suggested fixes concise - match the brevity of existing skill instructions
- No dramatic language ("critical", "extremely important", "must always")
- No exaggeration - state facts plainly
- Fixes should blend into existing SKILL.md tone

````
```markdown
## Fix: [Title]

**Severity:** CRITICAL | HIGH | MEDIUM | LOW
**File:** [path/to/SKILL.md]
**Section:** [section name]

**Problem:** [one sentence]

**Current:** [what's wrong]

**Fix:** Add to [section]:
> [exact text to add/modify]
```
````

## Thresholds

| Score | Verdict |
|-------|---------|
| 95%+ | PASS |
| 85-94% | REVIEW |
| 70-84% | WARN |
| <70% | FAIL |

**Execution Issue Impact:**

*By Category:*
| Category | Action |
|----------|--------|
| Exit/Status | Investigate script failure root cause |
| Argument/Usage | Check skill SKILL.md vs actual invocation |
| JSON/Parsing | Check input data edge cases |
| Dependencies | Document required setup in skill |
| File/Path | Verify path resolution logic |
| API/Network | Add retry/auth handling to skill |
| Timeout | Adjust timeouts or add progress handling |
| Git/Repository | Add repo validation before processing |

*Triage Priority:*
1. Argument/Usage errors - skill caller bugs, fix first
2. Dependencies missing - document in skill prerequisites
3. Exit/Status errors - investigate root cause
4. JSON/Parsing errors - handle edge cases in scripts
5. API/Timeout errors - add resilience to skill

Execution issues do not change the consistency score but must be reported in the Execution Issues section.

## Usage

```
Test the skill at ~/.claude/skills/learn-from-mistakes/
```

## Resources

- `scripts/run-parallel-tests.sh` - Parallel test runner
- `references/comparison-guide.md` - Comparison methodology
- `references/fix-prompt-template.md` - Fix prompt examples
- `examples/sample_report.md` - Report format
