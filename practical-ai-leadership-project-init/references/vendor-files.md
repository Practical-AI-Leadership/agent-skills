# Vendor-Specific AI Agent Files

## Table of Contents

- [Agents That Read AGENTS.md Natively](#agents-that-read-agentsmd-natively)
- [Vendor-Specific Entry Points](#vendor-specific-entry-points)
- [File Content Pattern](#file-content-pattern)
- [Traceability Chain](#traceability-chain)

## Agents That Read AGENTS.md Natively

These agents read `AGENTS.md` from the project root automatically. No vendor-specific file is needed:

- **Codex** — Reads `AGENTS.md` from the Git root and walks down to the current directory.
- **Amp** — Reads `AGENTS.md` from the current directory and parent directories up to `$HOME`.

## Vendor-Specific Entry Points

Each vendor file points to AGENTS.md with the correct relative path:

| Agent | File Path | Content |
|-------|-----------|---------|
| Claude Code | `CLAUDE.md` | `See [AGENTS.md](AGENTS.md).` |
| Cursor | `.cursor/rules/AGENTS.md` | `See [../../AGENTS.md](../../AGENTS.md).` |
| GitHub Copilot | `.github/copilot-instructions.md` | `See [../AGENTS.md](../AGENTS.md).` |
| Windsurf | `.windsurf/rules/AGENTS.md` | `See [../../AGENTS.md](../../AGENTS.md).` |
| Gemini CLI | `GEMINI.md` | `See [AGENTS.md](AGENTS.md).` |
| RooCode | `.roo/rules/AGENTS.md` | `See [../../AGENTS.md](../../AGENTS.md).` |
| Continue | `.continue/rules/AGENTS.md` | `See [../../AGENTS.md](../../AGENTS.md).` |
| Amazon Q | `.amazonq/rules/AGENTS.md` | `See [../../AGENTS.md](../../AGENTS.md).` |
| Tabnine | `.tabnine/guidelines/AGENTS.md` | `See [../../AGENTS.md](../../AGENTS.md).` |
| Augment Code | `.augment/rules/AGENTS.md` | `See [../../AGENTS.md](../../AGENTS.md).` |

## File Content Pattern

Every vendor file follows the same pattern — a single line referencing AGENTS.md:

```markdown
See [AGENTS.md]({relative-path-to-agents-md}).
```

The relative path depends on the vendor file's depth relative to the project root:
- Depth 1 (e.g., `CLAUDE.md`, `GEMINI.md`): `AGENTS.md`
- Depth 2 (e.g., `.github/copilot-instructions.md`): `../AGENTS.md`
- Depth 3 (e.g., `.cursor/rules/AGENTS.md`): `../../AGENTS.md`

## Traceability Chain

```
README.md <-> AGENTS.md <- [Vendor Files]
```

- `README.md` links to `AGENTS.md` (bidirectional)
- Each vendor file links to `AGENTS.md` (one-directional)
- `AGENTS.md` is the single source of truth for AI agent instructions
- Vendor files exist only as entry points that redirect to AGENTS.md
