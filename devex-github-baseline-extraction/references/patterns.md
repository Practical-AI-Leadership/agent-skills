# Bash and API Patterns Reference

Patterns and solutions learned from implementing GitHub DevEx baseline extraction.

## GitHub API Patterns

### REST API vs GraphQL

**Problem:** GraphQL queries can exceed node limits (500,000 nodes) for large repositories.

**Solution:** Use REST API with pagination instead:

```bash
# Instead of:
gh pr list --state merged --json number,title,createdAt,mergedAt

# Use:
gh api "repos/$REPO/pulls?state=closed&sort=updated&direction=desc&per_page=100" --paginate
```

### Pagination with jq Flattening

**Problem:** `gh api --paginate` returns multiple JSON arrays that need to be flattened.

**Solution:** Pipe through `jq -s 'add'`:

```bash
gh api "repos/$REPO/pulls?state=closed&per_page=100" \
    --paginate \
    --jq "[.[] | select(.merged_at != null)]" | jq -s 'add'
```

**Explanation:**
- `--paginate` fetches all pages
- `--jq` filters each page
- `jq -s 'add'` slurps all arrays and concatenates them

### Date Filtering in API Queries

**Problem:** GitHub REST API doesn't support `since` parameter for PR queries.

**Solution:** Filter in jq after fetching:

```bash
gh api "repos/$REPO/pulls?state=closed&per_page=100" \
    --paginate \
    --jq "[.[] | select(.merged_at >= \"${SINCE_DATE}T00:00:00Z\")]"
```

### Rate Limit Handling

**Pattern:** Exponential backoff with retry:

```bash
gh_api_with_retry() {
    local endpoint="$1"
    local retries=0
    local sleep_time=60

    while [[ $retries -lt 3 ]]; do
        if response=$(gh api "$endpoint" 2>&1); then
            echo "$response"
            return 0
        else
            if echo "$response" | grep -qi "rate limit"; then
                echo "Rate limit hit, sleeping ${sleep_time}s" >&2
                sleep "$sleep_time"
                sleep_time=$((sleep_time * 2))  # Exponential backoff
                retries=$((retries + 1))
            else
                return 1
            fi
        fi
    done
    return 1
}
```

---

## JSONL Output Patterns

### Compact JSON Output

**Problem:** `jq -n` outputs pretty-printed JSON, not JSONL.

**Solution:** Use `jq -cn` for compact output:

```bash
# Wrong - pretty printed
jq -n '{key: "value"}'

# Correct - single line
jq -cn '{key: "value"}'
```

### Building JSONL Records

**Pattern:** Use `jq -cn` with `--arg` and `--argjson`:

```bash
jq -cn \
    --arg repo "$REPO" \
    --argjson number "$PR_NUMBER" \
    --argjson is_bot "$IS_BOT" \
    '{
        repository: $repo,
        pr_number: $number,
        is_bot: $is_bot
    }' >> "$OUTPUT_FILE"
```

**Key distinction:**
- `--arg` - Pass as string
- `--argjson` - Pass as JSON (numbers, booleans, null)

---

## Parallel Processing Patterns

### Problem: Sequential API Calls Too Slow

Processing 287 PRs sequentially took ~15 minutes (3+ seconds per PR).

### Solution: xargs with Worker Script

**Pattern:** Write PR numbers to file, process with xargs:

```bash
# Create temp directory
tmp_dir=$(mktemp -d)

# Write PR numbers to file
echo "$prs" | jq -r '.[] | .number' > "$tmp_dir/pr_numbers.txt"

# Save full PR data for lookup
echo "$prs" > "$tmp_dir/prs.json"

# Create worker script
cat > "$tmp_dir/process_pr.sh" << 'WORKER_EOF'
#!/bin/bash
pr_number=$1
repo=$2
output_file=$3
prs_json=$4

# Process single PR...
pr=$(jq -c ".[] | select(.number == $pr_number)" "$prs_json")
# ... API calls and output ...
WORKER_EOF

chmod +x "$tmp_dir/process_pr.sh"

# Run in parallel (10 workers)
cat "$tmp_dir/pr_numbers.txt" | xargs -P 10 -I {} \
    "$tmp_dir/process_pr.sh" {} "$REPO" "$OUTPUT_FILE" "$tmp_dir/prs.json"

# Cleanup
rm -rf "$tmp_dir"
```

**Why this approach:**
- Avoids "argument list too long" error
- Each worker gets minimal arguments
- Shared data accessed via temp files
- 10x+ speedup (15 min → 1 min)

### Alternative: GNU Parallel

For more complex parallel processing:

```bash
parallel -j 10 process_pr {} "$REPO" ::: $(echo "$pr_numbers")
```

---

## Bash Safety Patterns

### Strict Mode

Always start scripts with:

```bash
set -euo pipefail
```

- `-e` - Exit on error
- `-u` - Error on undefined variables
- `-o pipefail` - Fail on pipe errors

### grep with pipefail

**Problem:** `grep` returns exit code 1 when no matches found, triggering `pipefail`.

**Solution:** Wrap with `|| true`:

```bash
# Wrong - exits script if no matches
git log --oneline | grep -iE "hotfix" | wc -l

# Correct - returns 0 even with no matches
git log --oneline | { grep -iE "hotfix" || true; } | wc -l
```

### Cross-Platform Date Handling

**Problem:** macOS (BSD) and Linux (GNU) have different date syntax.

**Solution:** Detect and use appropriate format:

```bash
calc_hours_diff() {
    local start="$1"
    local end="$2"

    if date --version >/dev/null 2>&1; then
        # GNU date (Linux)
        start_epoch=$(date -d "$start" +%s)
        end_epoch=$(date -d "$end" +%s)
    else
        # BSD date (macOS)
        start_epoch=$(date -jf "%Y-%m-%dT%H:%M:%SZ" "$start" +%s)
        end_epoch=$(date -jf "%Y-%m-%dT%H:%M:%SZ" "$end" +%s)
    fi

    diff_seconds=$((end_epoch - start_epoch))
    echo "scale=2; $diff_seconds / 3600" | bc
}
```

### Default Date Calculation

```bash
# 90 days ago - cross-platform
SINCE_DATE="${3:-$(date -v-90d +%Y-%m-%d 2>/dev/null || date -d '90 days ago' +%Y-%m-%d)}"
```

---

## Git Patterns

### Commit Count with Date Filter

**Problem:** `git shortlog --since` doesn't work reliably in all git versions.

**Solution:** Use `git log` with sort/uniq:

```bash
git log --since="$SINCE_DATE" --no-merges --pretty=format:"%an" | \
    sort | uniq -c | sort -rn
```

### Case-Insensitive Grep in Git

```bash
git log --oneline --grep="revert" -i --since="$SINCE_DATE"
```

The `-i` flag makes `--grep` case-insensitive.

### Exclude Merge Commits

Always use `--no-merges` for commit frequency metrics:

```bash
git log --oneline --since="$SINCE_DATE" --no-merges | wc -l
```

### Shallow Clone Detection

```bash
if [[ -f ".git/shallow" ]]; then
    echo "Warning: Shallow clone detected. Metrics may be incomplete." >&2
fi
```

To fix:
```bash
git fetch --unshallow
```

---

## Error Handling Patterns

### Logging Functions

```bash
log_info() {
    echo "[INFO] $*" >&2
}

log_error() {
    echo "[ERROR] $*" >&2
}

log_progress() {
    echo "[PROGRESS] $*" >&2
}
```

### Prerequisite Checks

```bash
# Check gh CLI authentication
if ! gh auth status >/dev/null 2>&1; then
    log_error "gh CLI is not authenticated. Run 'gh auth login' first."
    exit 1
fi

# Check required tools
if ! command -v jq >/dev/null 2>&1; then
    log_error "jq is required but not installed."
    exit 1
fi
```

### Directory Setup

```bash
mkdir -p "$OUTPUT_DIR"
> "$PR_OUTPUT"  # Clear previous output
```

---

## Bot Detection Pattern

```bash
BOT_PATTERNS=("dependabot" "renovate" "github-actions" "bot")

is_bot_author() {
    local author="$1"
    author_lower=$(echo "$author" | tr '[:upper:]' '[:lower:]')
    for pattern in "${BOT_PATTERNS[@]}"; do
        if [[ "$author_lower" == *"$pattern"* ]]; then
            return 0
        fi
    done
    return 1
}

# Usage
if is_bot_author "$author"; then
    is_bot="true"
else
    is_bot="false"
fi
```

---

## bc Arithmetic Pattern

### Leading Zero Fix

**Problem:** `bc` outputs `.5` instead of `0.5`.

**Solution:** Use sed to add leading zero:

```bash
echo "scale=2; 30 / 60" | bc | sed 's/^\./0./'
# Output: 0.50 (not .50)
```

---

## Temp File Cleanup Pattern

Always clean up temp files, even on error:

```bash
tmp_dir=$(mktemp -d)
trap "rm -rf $tmp_dir" EXIT

# ... use temp files ...

# Cleanup happens automatically on exit
```

Or manually:

```bash
tmp_dir=$(mktemp -d)
# ... work ...
rm -rf "$tmp_dir"
```

---

## Progress Indicator Pattern

For parallel processing, show dots:

```bash
# In worker script
echo -n "." >&2

# After xargs completes
echo "" >&2  # newline
log_info "Processing complete"
```

Output:
```
[INFO] Processing PRs with 10 parallel jobs...
..................................................
[INFO] Processing complete
```
