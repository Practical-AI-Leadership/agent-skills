# Go Pattern Definitions

File filter: `*.go`

---

## Pattern 1: Broad Exception Handling

**Pattern ID:** broad-exception-handling
**Risk:** High
**Why bad:** Untyped recover() catches all panics without distinguishing between recoverable and fatal errors. AI sees blanket recover as standard practice.

### Regex Patterns

```
Pattern: recover without type check
Regex: recover\s*\(\s*\)
Multiline: false
```

### False Positives

- Skip if followed by type assertion or type switch on the recovered value
- Skip if inside a top-level HTTP middleware (acceptable location)

### Before

```go
defer func() {
    if r := recover(); r != nil {
        log.Println("Recovered:", r)
    }
}()
```

### After

```go
defer func() {
    if r := recover(); r != nil {
        switch err := r.(type) {
        case *CustomError:
            handleCustom(err)
        default:
            log.Printf("Unexpected panic: %v", r)
            panic(r) // re-panic for unknown errors
        }
    }
}()
```

### AGENTS.md Rule

> When using `recover()`, always type-check the recovered value. Re-panic for unexpected error types. Only use recover in top-level middleware or goroutine wrappers.

---

## Pattern 2: Hardcoded Secrets

**Pattern ID:** hardcoded-secrets
**Risk:** Critical
**Why bad:** Credentials leak via version control. AI copies the pattern of embedding secrets directly into Go source.

### Regex Patterns

```
Pattern: hardcoded password
Regex: (password|passwd|pwd)\s*[:=]\s*"[^"]{4,}"
Multiline: false

Pattern: hardcoded API key
Regex: (apiKey|apiSecret|api_key|api_secret)\s*[:=]\s*"[a-zA-Z0-9_\-]{8,}"
Multiline: false

Pattern: AWS access key
Regex: AKIA[0-9A-Z]{16}
Multiline: false

Pattern: generic secret
Regex: (secret|token|jwt)\s*[:=]\s*"[^"]{8,}"
Multiline: false

Pattern: private key
Regex: -----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----
Multiline: false
```

### False Positives

- Skip if value references `os.Getenv`, `viper.Get`, `config.`
- Skip if inside test files (`_test.go`)
- Skip if value contains `example`, `placeholder`, `test`, `mock`, `dummy`

### Before

```go
const APIKey = "sk_live_1234567890abcdef"
```

### After

```go
apiKey := os.Getenv("API_KEY")
if apiKey == "" {
    log.Fatal("API_KEY environment variable is required")
}
```

### AGENTS.md Rule

> Never hardcode credentials in Go source. Use `os.Getenv()`, viper, or a secrets manager. Validate required env vars at startup.

---

## Pattern 3: SQL Injection

**Pattern ID:** sql-injection
**Risk:** Critical
**Why bad:** fmt.Sprintf with SQL enables injection. AI generates new queries using the same unsafe Sprintf pattern.

### Regex Patterns

```
Pattern: fmt.Sprintf SQL
Regex: fmt\.Sprintf\s*\(\s*"[^"]*\b(SELECT|INSERT|UPDATE|DELETE)\b
Multiline: false

Pattern: string concat SQL
Regex: \.(Exec|Query|QueryRow)\s*\(\s*"[^"]*\b(SELECT|INSERT|UPDATE|DELETE)\b[^"]*"\s*\+
Multiline: false

Pattern: Exec/Query with Sprintf
Regex: \.(Exec|Query|QueryRow)\s*\(\s*fmt\.Sprintf
Multiline: false
```

### False Positives

- Skip if using `$1`, `?` placeholders
- Skip if inside migration files
- Skip if the query is a static string with no variable interpolation

### Before

```go
query := fmt.Sprintf("SELECT * FROM users WHERE id = %d", userID)
db.Query(query)
```

### After

```go
db.Query("SELECT * FROM users WHERE id = $1", userID)
```

### AGENTS.md Rule

> Always use parameterized queries with `$1`, `$2` placeholders. Never use `fmt.Sprintf` to build SQL strings.

---

## Pattern 5: N+1 Database Queries

**Pattern ID:** n-plus-one-queries
**Risk:** High
**Why bad:** Database queries inside range loops execute one query per item.

### Regex Patterns

```
Pattern: query in range loop
Regex: for\s+.*range\s+[\s\S]*?\.(Query|QueryRow|Exec|Get|Select)\s*\(
Multiline: true
```

### False Positives

- Skip if the loop is iterating over query results (not making new queries)
- Skip if batch operations are used nearby

### Before

```go
for _, userID := range userIDs {
    var user User
    db.QueryRow("SELECT * FROM users WHERE id = $1", userID).Scan(&user)
    users = append(users, user)
}
```

### After

```go
query, args, _ := sqlx.In("SELECT * FROM users WHERE id IN (?)", userIDs)
query = db.Rebind(query)
var users []User
db.Select(&users, query, args...)
```

### AGENTS.md Rule

> Never execute database queries inside range loops. Use `WHERE IN` with `sqlx.In()` or batch operations.

---

## Pattern 8: Error Suppression

**Pattern ID:** error-suppression
**Risk:** High
**Why bad:** Assigning errors to `_` silently ignores failures. AI learns to suppress errors as the default Go style.

### Regex Patterns

```
Pattern: error assigned to blank identifier
Regex: _\s*=\s*\w+\.\w+\s*\(
Multiline: false

Pattern: error ignored (no assignment)
Regex: ^\s+\w+\.\w+\s*\([^)]*\)\s*$
Multiline: false

Pattern: nolint comment
Regex: //\s*nolint
Multiline: false
```

### False Positives

- Skip `_ = f.Close()` in defer (common acceptable pattern)
- Skip `_ = fmt.Fprintf` (write to known-good writer)
- Skip if the function is documented as never returning errors

### Before

```go
result, _ := doWork()
_ = file.Close()
json.Unmarshal(data, &obj)  // error ignored
```

### After

```go
result, err := doWork()
if err != nil {
    return fmt.Errorf("doWork failed: %w", err)
}

if err := file.Close(); err != nil {
    log.Printf("failed to close file: %v", err)
}

if err := json.Unmarshal(data, &obj); err != nil {
    return fmt.Errorf("unmarshal failed: %w", err)
}
```

### AGENTS.md Rule

> Never assign errors to `_` except for `defer f.Close()` and known infallible writes. Always check and wrap errors with `fmt.Errorf("context: %w", err)`.

---

## Pattern 9: Command Injection

**Pattern ID:** command-injection
**Risk:** Critical
**Why bad:** exec.Command with shell invocation allows injection. AI copies the `/bin/sh -c` pattern.

### Regex Patterns

```
Pattern: shell command via sh -c
Regex: exec\.Command\s*\(\s*"(/bin/)?(sh|bash)"\s*,\s*"-c"
Multiline: false

Pattern: fmt.Sprintf in exec.Command
Regex: exec\.Command\s*\([^)]*fmt\.Sprintf
Multiline: false
```

### False Positives

- Skip if the command string is a hardcoded literal with no variable interpolation
- Skip if inside test files

### Before

```go
cmd := exec.Command("sh", "-c", fmt.Sprintf("tar -czf %s %s", archive, target))
```

### After

```go
cmd := exec.Command("tar", "-czf", archive, target)
```

### AGENTS.md Rule

> Never use `exec.Command("sh", "-c", ...)` with interpolated strings. Always pass the binary and arguments separately: `exec.Command("binary", "arg1", "arg2")`.
