# Kotlin Pattern Definitions

File filter: `*.kt`

---

## Pattern 1: Broad Exception Handling

**Pattern ID:** broad-exception-handling
**Risk:** High
**Why bad:** Catching generic `Exception` hides specific error cases. AI replicates broad catches across every function.

### Regex Patterns

```
Pattern: catch Exception
Regex: catch\s*\(\s*e\s*:\s*Exception\s*\)
Multiline: false

Pattern: catch Throwable
Regex: catch\s*\(\s*e\s*:\s*Throwable\s*\)
Multiline: false
```

### False Positives

- Skip if followed by `throw` (re-throw)
- Skip in test files
- Skip in top-level coroutine exception handlers

### Before

```kotlin
try {
    processOrder(order)
} catch (e: Exception) {
    logger.error("Failed", e)
}
```

### After

```kotlin
try {
    processOrder(order)
} catch (e: ValidationException) {
    logger.warn("Invalid order: ${e.message}")
    throw OrderProcessingException("Validation failed", e)
} catch (e: DatabaseException) {
    logger.error("Database error", e)
    throw OrderProcessingException("Database error", e)
}
```

### AGENTS.md Rule

> Catch specific exception types. Never catch `Exception` or `Throwable` without re-throwing. Use sealed classes for typed error handling.

---

## Pattern 2: Hardcoded Secrets

**Pattern ID:** hardcoded-secrets
**Risk:** Critical
**Why bad:** Credentials in Kotlin source leak via version control and decompilation.

### Regex Patterns

```
Pattern: hardcoded password
Regex: (password|passwd|pwd)\s*=\s*"[^"]{4,}"
Multiline: false

Pattern: hardcoded API key
Regex: (apiKey|apiSecret|api_key|API_KEY)\s*=\s*"[a-zA-Z0-9_\-]{8,}"
Multiline: false

Pattern: AWS access key
Regex: AKIA[0-9A-Z]{16}
Multiline: false

Pattern: generic secret
Regex: (secret|token|jwt)\s*=\s*"[^"]{8,}"
Multiline: false
```

### False Positives

- Skip if value references `System.getenv`, `BuildConfig.`, `config.`
- Skip in test files
- Skip if value contains `example`, `placeholder`, `test`, `mock`

### Before

```kotlin
const val API_KEY = "sk_live_1234567890"
```

### After

```kotlin
val apiKey = System.getenv("API_KEY")
    ?: throw IllegalStateException("API_KEY is required")
```

### AGENTS.md Rule

> Never hardcode credentials. Use `System.getenv()`, `BuildConfig` fields, or a secrets manager.

---

## Pattern 4: Sequential Async Operations

**Pattern ID:** sequential-async
**Risk:** High
**Why bad:** Sequential suspend calls inside loops serialize independent I/O. AI defaults to sequential coroutine execution.

### Regex Patterns

```
Pattern: await in for loop (coroutines)
Regex: for\s*\([^)]*\)\s*\{[\s\S]*?\bawait\b
Multiline: true

Pattern: suspend in forEach
Regex: \.forEach\s*\{[\s\S]*?(suspend|\.await\(\))
Multiline: true
```

### False Positives

- Skip if each iteration depends on the previous result
- Skip if `async`/`awaitAll` is used in the same scope

### Before

```kotlin
val results = mutableListOf<User>()
for (userId in userIds) {
    val user = fetchUser(userId) // suspend function
    results.add(user)
}
```

### After

```kotlin
val results = coroutineScope {
    userIds.map { userId ->
        async { fetchUser(userId) }
    }.awaitAll()
}
```

### AGENTS.md Rule

> Never call suspend functions sequentially in loops when iterations are independent. Use `coroutineScope { list.map { async { ... } }.awaitAll() }`.

---

## Pattern 7: Type Safety Bypass

**Pattern ID:** type-safety-bypass
**Risk:** High
**Why bad:** Non-null assertions (`!!`) and unsafe `lateinit` bypass Kotlin's null safety system. AI sees `!!` as "how this codebase handles nullability" and applies it everywhere.

### Regex Patterns

```
Pattern: non-null assertion (!!)
Regex: \w+!!
Multiline: false

Pattern: lateinit without checks
Regex: lateinit\s+var\s+
Multiline: false

Pattern: unchecked cast
Regex: as\s+(?![\?\s])\w+
Multiline: false
```

### False Positives

- Skip `!!` in test files (common in assertions)
- Skip `lateinit` for dependency injection frameworks (Dagger, Hilt) with `@Inject`
- Skip `as` in safe casts (`as?`)

### Before

```kotlin
val name = user!!.name
lateinit var service: UserService  // no @Inject

val result = data as List<String>
```

### After

```kotlin
val name = user?.name
    ?: throw IllegalStateException("User is required")

val service: UserService by lazy { createService() }

val result = data as? List<*>
    ?: throw IllegalArgumentException("Expected List")
```

### AGENTS.md Rule

> Never use `!!` - use `?.`, `?:`, or explicit null checks with meaningful errors. Use `lateinit` only with dependency injection (`@Inject`). Use `as?` (safe cast) instead of `as`.
