#!/bin/bash
# Skill Testing - Parallel Test Runner
# Runs 3 Claude CLI instances in parallel using tmux

set -e

# --- Configuration ---
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/skill-test}"
SESSION_NAME="skill-test"
# Find claude binary - check common locations
find_claude() {
  local paths=(
    "$HOME/.claude/local/claude"
    "/usr/local/bin/claude"
    "/opt/homebrew/bin/claude"
    "$HOME/.local/bin/claude"
  )
  for p in "${paths[@]}"; do
    [ -x "$p" ] && echo "$p" && return
  done
  # Fallback to PATH
  command -v claude 2>/dev/null
}
CLAUDE_BIN="${CLAUDE_BIN:-$(find_claude)}"

validate_claude() {
  if [ -z "$CLAUDE_BIN" ] || [ ! -x "$CLAUDE_BIN" ]; then
    echo "ERROR: Claude CLI not found"
    echo "Checked: ~/.claude/local/claude, /usr/local/bin, /opt/homebrew/bin"
    echo "Set CLAUDE_BIN env var to override"
    exit 1
  fi
  echo "Using: $CLAUDE_BIN"
}

# --- Functions ---
ensure_tmux() {
  if command -v tmux &> /dev/null; then
    return 0
  fi

  echo "tmux not found, installing..."

  if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install tmux
  elif command -v apt-get &> /dev/null; then
    sudo apt-get update && sudo apt-get install -y tmux
  elif command -v yum &> /dev/null; then
    sudo yum install -y tmux
  else
    echo "ERROR: Cannot install tmux automatically."
    echo "Please install tmux manually and retry."
    exit 1
  fi
}

cleanup() {
  tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
  rm -rf "$OUTPUT_DIR"
}

setup() {
  # Clean up old output files to prevent false completion detection
  rm -rf "$OUTPUT_DIR"
  mkdir -p "$OUTPUT_DIR"
  tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
}

run_tests() {
  local t1="$1"
  local t2="$2"
  local t3="$3"

  # Create tmux session with first test
  tmux new-session -d -s "$SESSION_NAME" -n test1 \
    "echo \"\$(date +%H:%M:%S) [T1] Start: $t1\" >> \"$OUTPUT_DIR/debug.log\"; \
     $CLAUDE_BIN -p --dangerously-skip-permissions \"$t1\" > \"$OUTPUT_DIR/t1.txt\" 2>&1; \
     echo \"\$(date +%H:%M:%S) [T1] Done (exit \$?)\" >> \"$OUTPUT_DIR/debug.log\"; \
     echo DONE > \"$OUTPUT_DIR/t1.done\""

  sleep 2  # Brief rate limit buffer

  tmux new-window -t "$SESSION_NAME" -n test2 \
    "echo \"\$(date +%H:%M:%S) [T2] Start: $t2\" >> \"$OUTPUT_DIR/debug.log\"; \
     $CLAUDE_BIN -p --dangerously-skip-permissions \"$t2\" > \"$OUTPUT_DIR/t2.txt\" 2>&1; \
     echo \"\$(date +%H:%M:%S) [T2] Done (exit \$?)\" >> \"$OUTPUT_DIR/debug.log\"; \
     echo DONE > \"$OUTPUT_DIR/t2.done\""

  sleep 2  # Brief rate limit buffer

  tmux new-window -t "$SESSION_NAME" -n test3 \
    "echo \"\$(date +%H:%M:%S) [T3] Start: $t3\" >> \"$OUTPUT_DIR/debug.log\"; \
     $CLAUDE_BIN -p --dangerously-skip-permissions \"$t3\" > \"$OUTPUT_DIR/t3.txt\" 2>&1; \
     echo \"\$(date +%H:%M:%S) [T3] Done (exit \$?)\" >> \"$OUTPUT_DIR/debug.log\"; \
     echo DONE > \"$OUTPUT_DIR/t3.done\""

  echo "Tests started in tmux session '$SESSION_NAME'"
  echo "Attach with: tmux attach -t $SESSION_NAME"
  echo "Debug log: $OUTPUT_DIR/debug.log"
}

wait_for_completion() {
  local timeout="${1:-600}"  # 10 min default
  local elapsed=0

  while [ ! -f "$OUTPUT_DIR/t1.done" ] || [ ! -f "$OUTPUT_DIR/t2.done" ] || [ ! -f "$OUTPUT_DIR/t3.done" ]; do
    sleep 5
    elapsed=$((elapsed + 5))
    local done_count=$(ls "$OUTPUT_DIR"/*.done 2>/dev/null | wc -l | tr -d ' ')
    echo "Waiting... ${done_count}/3 complete (${elapsed}s)"

    if [ "$elapsed" -ge "$timeout" ]; then
      echo "ERROR: Timeout after ${timeout}s"
      return 1
    fi
  done

  echo "All tests complete"
}

show_results() {
  echo ""
  echo "=== Test 1 Output ==="
  cat "$OUTPUT_DIR/t1.txt"
  echo ""
  echo "=== Test 2 Output ==="
  cat "$OUTPUT_DIR/t2.txt"
  echo ""
  echo "=== Test 3 Output ==="
  cat "$OUTPUT_DIR/t3.txt"
}

# --- Main ---
usage() {
  echo "Usage: $0 <trigger1> <trigger2> <trigger3>"
  echo ""
  echo "Example:"
  echo "  $0 'test skill at ~/.claude/skills/foo' \\"
  echo "     'verify skill consistency ~/.claude/skills/foo' \\"
  echo "     'run skill test ~/.claude/skills/foo'"
  echo ""
  echo "Commands:"
  echo "  $0 cleanup    - Kill session and remove output files"
  echo "  $0 results    - Show results from last run"
  echo "  $0 attach     - Attach to running tmux session"
}

case "${1:-}" in
  cleanup)
    cleanup
    echo "Cleaned up"
    ;;
  results)
    show_results
    ;;
  attach)
    tmux attach -t "$SESSION_NAME"
    ;;
  -h|--help|"")
    usage
    exit 0
    ;;
  *)
    if [ $# -lt 3 ]; then
      echo "ERROR: Need 3 trigger phrases"
      usage
      exit 1
    fi

    validate_claude
    ensure_tmux
    setup
    run_tests "$1" "$2" "$3"
    wait_for_completion
    show_results
    ;;
esac
