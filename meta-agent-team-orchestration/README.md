# Agent Team Orchestration

Design, spawn, coordinate, and retrospect multi-agent teams matched to a task. Handles the full lifecycle: interview the user, classify the task, recommend the right team topology, spawn agents with appropriate roles and models, enforce review gates, and run a post-mortem after shutdown.

**License:** [See LICENSE.md](../LICENSE.md) — free to use, modify, and share. Commercial repurposing prohibited.

## Problem

Agent teams are often spawned with every agent at once, causing idle time on agents waiting for upstream output. The coordination overhead grows quadratically (N agents create N*(N-1)/2 communication paths), and teams frequently exceed the size where parallelism stops paying for itself. This skill enforces lazy spawning, smallest-team-first sizing, and post-mortem retrospectives.

## How to Use

1. Copy this directory to `~/.claude/skills/meta-agent-team-orchestration/`
2. Invoke with a trigger phrase like "create agent team", "design agent team", "orchestrate agents", "coordinate multiple agents"
3. Answer the 4 interview questions (task nature, parallelizability, criticality, constraints)
4. The skill warns if a team is overkill and recommends a single agent instead when appropriate

## Origin Story

Built from accumulated experience running multi-agent teams for complex research, analysis, and implementation tasks. The pattern that triggered codification was the repeated observation that agent teams were being spawned with all agents at once, causing idle time on agents waiting for upstream output. The skill was designed around three hard-won principles: lazy spawning (only spawn an agent when its input is ready), the smallest team that can do the job, and post-mortem retrospectives that capture where coordination broke.

## Customize for Your Org

- [ ] Adjust the model assignment table (Opus/Sonnet/Haiku) based on your cost budget
- [ ] Add your team's common task → topology mappings to the Quick Reference section
- [ ] Extend the review gate prompt with domain-specific correctness checks
