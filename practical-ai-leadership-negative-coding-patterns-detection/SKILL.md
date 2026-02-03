---
name: "Practical AI Leadership: Negative Coding Patterns Detection"
description: This skill should be used when the user asks to "scan for anti-patterns", "check AI amplification risk", "find patterns AI copies", "detect bad patterns in codebase", "run amplification scan", "check what AI is copying", "detect negative coding patterns", "find coding anti-patterns", "scan for negative patterns", or wants to identify coding anti-patterns that AI tools replicate at scale.
version: 0.1.0
---

# Negative Coding Patterns Detection

Scan a codebase for the 10 most dangerous cross-language anti-patterns that AI coding tools copy and amplify. Auto-detect the technical stack, search for pattern instances using regex-based code search, and generate a single comprehensive mitigation prompt.

## Workflow

### Step 1: Tech Stack Detection

Detect programming languages present in the codebase:

1. Search for files by extension: `*.py`, `*.ts`, `*.js`, `*.tsx`, `*.jsx`, `*.go`, `*.java`, `*.kt`, `*.swift`, `*.dart`, `*.cs`, `*.tf`
2. Confirm with config files: `package.json`, `tsconfig.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `build.gradle`, `pom.xml`, `Podfile`, `pubspec.yaml`, `*.csproj`, `*.sln`
3. Count files per language

### Step 2: Language Selection

Select the language with the highest file count. Report the selection:

```
Detected languages in the codebase:
- Python (42 files)
- TypeScript (128 files)
- Go (15 files)

Scanning: TypeScript (highest file count)
```

### Step 3: Pattern Analysis

For the selected language, load the corresponding pattern definitions from `references/patterns/{language}.md`.

**Analysis approach per pattern:**

1. Search the codebase with each regex pattern from the language reference file, filtering to the appropriate file extensions (e.g. `*.py` for Python)
2. For each match, read 5-10 lines of surrounding context
3. Check against false positive indicators listed in the reference file - skip matches that are false positives
4. Record: file path, line number, offending code snippet, pattern ID, pattern name

**Run patterns in parallel where possible.** Search for independent patterns concurrently.

**Important:** Some patterns span multiple lines (e.g. await inside loops, queries inside loops). Enable multiline/cross-line matching for these patterns. The reference files mark which patterns need multiline matching.

### Step 4: Findings Report

After scanning, present a findings summary to the user. Structure:

```
## Scan Results

### Summary
- Language scanned: [name]
- Total anti-patterns found: [count]
- Files affected: [count]

### Findings by Pattern

#### 1. [Pattern Name] - [count] instances
**AI Amplification Risk:** [explanation from reference file]
**Files affected:**
- `path/to/file.py:42` - [brief code snippet]
- `path/to/file.py:87` - [brief code snippet]
...

[Repeat for each pattern found]

### Patterns Not Found
- [list of patterns that had zero matches - this is good news]
```

### Step 5: Mitigation Prompt Generation

Generate ONE comprehensive mitigation prompt. Read `references/mitigation_prompt_template.md` for the prompt structure and follow it exactly.

The mitigation prompt must contain:
- All patterns found with their exact file locations and code snippets
- For each pattern: what it is, why AI amplifies it, the correct replacement pattern (before/after code from the language reference files)
- AGENTS.md rules to add that prevent AI from learning the bad patterns
- Instructions to apply fixes systematically (highest-risk patterns first)

Write the mitigation prompt to a file in the user's project root: `NEGATIVE_PATTERNS_MITIGATION.md`

### Step 6: Review

After generating the mitigation prompt, perform a self-review (or delegate to a sub-agent if available) to verify the prompt for:

1. **Completeness** - Every pattern found in Step 4 has a corresponding fix section in the prompt
2. **Correctness** - Before/after code examples match the actual language and framework used in the codebase
3. **Accuracy** - File paths and line numbers referenced in the prompt match the actual findings
4. **Actionability** - Instructions are clear enough for an AI coding tool to execute without ambiguity

Report any issues found. Fix them before presenting the final output to the user.

## The 10 Patterns

| # | Pattern | Risk | Languages |
|---|---------|------|-----------|
| 1 | Broad Exception Handling | High | Python, JS/TS, Java, C#, Go, Kotlin, Swift, Dart |
| 2 | Hardcoded Secrets | Critical | All |
| 3 | SQL Injection | Critical | Python, JS/TS, Go, Java, C# |
| 4 | Sequential Async Operations | High | JS/TS, Python, Dart, Kotlin |
| 5 | N+1 Database Queries | High | Python, JS/TS, Go, Java, C# |
| 6 | Dynamic Code Execution | Critical | Python, JS/TS |
| 7 | Type Safety Bypass | High | TypeScript, Swift, Kotlin, Dart |
| 8 | Error Suppression | High | Go, Python, JS/TS |
| 9 | Command Injection | Critical | Python, JS/TS, Go |
| 10 | DOM Injection (XSS) | Critical | JS/TS |

## Reference Files

### Pattern Definitions (per language)

Each file contains all applicable patterns for that language with: regex patterns, file filters, multiline flag, false positive indicators, before/after code examples, and AGENTS.md rule text.

- **`references/patterns/python.md`** - Patterns 1-6, 8-9 (8 patterns)
- **`references/patterns/javascript_typescript.md`** - All 10 patterns
- **`references/patterns/go.md`** - Patterns 1-3, 5, 8-9 (6 patterns)
- **`references/patterns/java.md`** - Patterns 1-3, 5 (4 patterns)
- **`references/patterns/kotlin.md`** - Patterns 1-2, 4, 7 (4 patterns)
- **`references/patterns/swift.md`** - Patterns 1-2, 7 (3 patterns)
- **`references/patterns/dart.md`** - Patterns 1-2, 4, 7 (4 patterns)
- **`references/patterns/csharp.md`** - Patterns 1-3, 5 (4 patterns)
- **`references/patterns/terraform.md`** - Pattern 2 (1 pattern)

### Mitigation Prompt Template

- **`references/mitigation_prompt_template.md`** - Structure and sections for the generated mitigation prompt

## Important Notes

- Never report a pattern without reading surrounding code context first. Regex matches need verification by reading the actual code.
- For multiline patterns (await-in-loop, query-in-loop), enable cross-line matching. These patterns span multiple lines.
- False positives are common. The reference files list specific exclusions per pattern. Apply them.
- The mitigation prompt targets AI coding tools. Write it as instructions an AI agent can execute, not as human documentation.
- Terraform patterns are infrastructure-specific (hardcoded secrets in IaC). They follow different grep patterns than application code.
