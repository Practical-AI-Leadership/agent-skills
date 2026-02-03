# Swift Pattern Definitions

File filter: `*.swift`

---

## Pattern 1: Broad Exception Handling

**Pattern ID:** broad-exception-handling
**Risk:** High
**Why bad:** Generic `catch` without pattern matching hides specific error cases. AI replicates broad catches across every function.

### Regex Patterns

```
Pattern: generic catch block
Regex: \}\s*catch\s*\{
Multiline: false

Pattern: catch with generic error
Regex: catch\s+let\s+\w+\s*\{
Multiline: false
```

### False Positives

- Skip if followed by a type-specific catch before the generic one
- Skip in test files
- Skip if the catch block rethrows (`throw error`)

### Before

```swift
do {
    try processOrder(order)
} catch {
    print("Error: \(error)")
}
```

### After

```swift
do {
    try processOrder(order)
} catch let error as ValidationError {
    logger.warn("Invalid order: \(error.message)")
    throw OrderProcessingError.validation(error)
} catch let error as DatabaseError {
    logger.error("Database error: \(error)")
    throw OrderProcessingError.database(error)
}
```

### AGENTS.md Rule

> Catch specific error types using `catch let error as SpecificType`. Never use a bare `catch` without rethrowing or specific handling.

---

## Pattern 2: Hardcoded Secrets

**Pattern ID:** hardcoded-secrets
**Risk:** Critical
**Why bad:** Credentials in Swift source end up in compiled binaries and version control.

### Regex Patterns

```
Pattern: hardcoded password
Regex: (password|passwd|pwd)\s*[:=]\s*"[^"]{4,}"
Multiline: false

Pattern: hardcoded API key
Regex: (apiKey|apiSecret|api_key|API_KEY)\s*[:=]\s*"[a-zA-Z0-9_\-]{8,}"
Multiline: false

Pattern: AWS access key
Regex: AKIA[0-9A-Z]{16}
Multiline: false

Pattern: generic secret
Regex: (secret|token|jwt)\s*[:=]\s*"[^"]{8,}"
Multiline: false
```

### False Positives

- Skip if value references `ProcessInfo.processInfo.environment`, `Bundle.main`, `UserDefaults`
- Skip in test files
- Skip if value contains `example`, `placeholder`, `test`, `mock`

### Before

```swift
let apiKey = "sk_live_1234567890abcdef"
```

### After

```swift
guard let apiKey = ProcessInfo.processInfo.environment["API_KEY"] else {
    fatalError("API_KEY environment variable is required")
}
```

### AGENTS.md Rule

> Never hardcode credentials in Swift source. Use `ProcessInfo.processInfo.environment`, Keychain, or configuration files excluded from version control.

---

## Pattern 7: Type Safety Bypass

**Pattern ID:** type-safety-bypass
**Risk:** High
**Why bad:** Force unwrapping (`!`), force try (`try!`), and implicitly unwrapped optionals bypass Swift's safety system. AI sees these as "how this codebase handles optionals" and applies them everywhere.

### Regex Patterns

```
Pattern: force unwrap
Regex: \w+!\s*[.\[;,\)]
Multiline: false

Pattern: force try
Regex: try!\s+
Multiline: false

Pattern: implicitly unwrapped optional
Regex: :\s*\w+!
Multiline: false
```

### False Positives

- Skip `!` in boolean negation (`!condition`)
- Skip `!` in not-equal (`!=`)
- Skip `IBOutlet` properties (implicitly unwrapped by convention in UIKit)
- Skip `!` in test files (force unwrap is common in tests)
- Skip type declarations like `String!` in protocol conformance with Obj-C

### Before

```swift
let user = fetchUser()!  // Crashes if nil
let data = try! loadFile(path)  // Crashes on error
var service: UserService!  // Implicitly unwrapped
```

### After

```swift
guard let user = fetchUser() else {
    throw UserError.notFound
}

let data: Data
do {
    data = try loadFile(path)
} catch {
    throw FileError.loadFailed(path, error)
}

let service: UserService  // Initialize in init()
```

### AGENTS.md Rule

> Never use force unwrap (`!`) - use `guard let`, `if let`, or `??` with a default. Never use `try!` - use `do-catch`. Never use implicitly unwrapped optionals (`Type!`) - use proper optional handling or non-optional with initialization in `init()`.
