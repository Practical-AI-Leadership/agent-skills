# Vendor-Specific AI Agent Files

## Table of Contents

- [Available Agents](#available-agents)
- [File Content Pattern](#file-content-pattern)
- [Traceability Chain](#traceability-chain)

## Available Agents

Each vendor file points to AGENTS.md with the correct relative path:

| Agent | File Path | Content |
|-------|-----------|---------|
| Claude Code | `CLAUDE.md` | `See [AGENTS.md](AGENTS.md).` |
| Cursor | `.cursor/rules/AGENTS.md` | `See [../../AGENTS.md](../../AGENTS.md).` |
| GitHub Copilot | `.github/copilot-instructions.md` | `See [../AGENTS.md](../AGENTS.md).` |
| Windsurf | `.windsurf/rules/AGENTS.md` | `See [../../AGENTS.md](../../AGENTS.md).` |
| Codex | `.codex/AGENTS.md` | `See [../AGENTS.md](../AGENTS.md).` |
| Gemini CLI | `.gemini/AGENTS.md` | `See [../AGENTS.md](../AGENTS.md).` |
| Amp | `.amp/AGENTS.md` | `See [../AGENTS.md](../AGENTS.md).` |
| RooCode | `.roo/rules/AGENTS.md` | `See [../../AGENTS.md](../../AGENTS.md).` |
| Continue | `.continue/rules/AGENTS.md` | `See [../../AGENTS.md](../../AGENTS.md).` |
| Amazon Q | `.amazonq/rules/AGENTS.md` | `See [../../AGENTS.md](../../AGENTS.md).` |
| Tabnine | `.tabnine/guidelines/AGENTS.md` | `See [../../AGENTS.md](../../AGENTS.md).` |
| Augment Code | `.augment/AGENTS.md` | `See [../AGENTS.md](../AGENTS.md).` |

## File Content Pattern

Every vendor file follows the same pattern — a single line referencing AGENTS.md:

```markdown
See [AGENTS.md]({relative-path-to-agents-md}).
```

The relative path depends on the vendor file's depth relative to the project root:
- Depth 1 (e.g., `CLAUDE.md`): `AGENTS.md`
- Depth 2 (e.g., `.codex/AGENTS.md`): `../AGENTS.md`
- Depth 3 (e.g., `.cursor/rules/AGENTS.md`): `../../AGENTS.md`

## Traceability Chain

```
README.md <-> AGENTS.md <- [Vendor Files]
```

- `README.md` links to `AGENTS.md` (bidirectional)
- Each vendor file links to `AGENTS.md` (one-directional)
- `AGENTS.md` is the single source of truth for AI agent instructions
- Vendor files exist only as entry points that redirect to AGENTS.md
