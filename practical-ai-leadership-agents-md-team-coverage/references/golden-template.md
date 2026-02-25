# AGENTS.md Golden Template

Complete reference template for creating or improving AGENTS.md files.

## Template Structure

```markdown
# {Domain/Package Name} — AGENTS.md

## Purpose

{Brief description of what this project/module does. 1-2 sentences.}

For repository setup and general architecture, see [root AGENTS.md](../../AGENTS.md).

## Commands

```bash
# Navigate to domain/package
cd path/to/domain

# Install dependencies
yarn  # or npm install, flutter pub get, etc.

# Lint and format
yarn fix  # or npm run lint, flutter analyze

# Type check
yarn compile  # or npm run typecheck, flutter analyze

# Run tests
yarn test  # or npm test, flutter test

# Run specific test
yarn test --testPathPattern="<pattern>"
```

## Project Structure

- `src/entrypoints/` — API routes and controllers
- `src/useCases/` — Business logic operations
- `src/services/` — Domain services
- `src/dataSources/` — Database and external API access
- `src/dtos/` — Data transfer objects
- `src/exceptions/` — Domain-specific errors
- `src/types/` — TypeScript type definitions

## Agent Permissions

### Allowed (Do Without Asking)
- Add or update DTOs and entities
- Add or improve tests
- Fix type errors and lint issues
- Add logging for debugging

### Ask First
- Change core business logic
- Modify external integrations
- Alter data models
- Change API contracts

### Never
- Log sensitive data (credentials, PII)
- Hardcode environment-specific values
- Bypass validation or security checks
- Remove existing functionality without discussion

## Performance

- Batch database queries (avoid N+1)
- Use pagination for large result sets
- Cache expensive computations where appropriate
- Implement proper error handling with timeouts

## Domain Rules

- {Business constraint 1}
- {Business constraint 2}
- {State machine rules if applicable}

## Security

- Never log credentials or tokens
- Validate all external input
- Use parameterized queries
- Follow least privilege principle

## Testing

- Unit tests: `test/`
- Test patterns: {describe testing approach}
- Run specific tests: `yarn test --testPathPattern="<pattern>"`

## References

- [README.md](./README.md) — Domain documentation
- [Root AGENTS.md](../../AGENTS.md) — Repository-wide guidelines
```

## Section Weights

| Section | Weight | AI Error Multiplier |
|---------|--------|---------------------|
| Commands | 21% | — |
| Agent Permissions | 17% | — |
| Project Structure | 12% | — |
| Performance | 8% | 7.9x |
| Error Handling | 8% | 1.97x |
| Domain Rules | 7% | 2.25x |
| Security | 6% | 1.5-2x |
| Concurrency | 6% | 2.29x |
| Null Safety | 5% | 2.27x |
| Testing | 8% | — |
| Conventions | 9% | — |

## Optimal Length

| Lines | Assessment |
|-------|------------|
| 0-19 | Too short |
| **20-50** | **Ideal** |
| 51-150 | Acceptable |
| 151-300 | Verbose |
| 300+ | Too long (split) |

## Anti-Patterns

| Pattern | Penalty |
|---------|---------|
| Vague filler ("You are helpful...") | -10 pts |
| Long prose (>10 lines without structure) | -5 pts |
| No code blocks | -15 pts |
| Exceeds 32KB | -20 pts |
| Outdated references (Python 2, TSLint) | -20 pts |
| Self-conflicting rules | -3 pts each |
