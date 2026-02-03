# Dart Pattern Definitions

File filter: `*.dart`

---

## Pattern 1: Broad Exception Handling

**Pattern ID:** broad-exception-handling
**Risk:** High
**Why bad:** Catching generic `Exception` or bare `catch` hides specific error cases. AI replicates broad catches across every function.

### Regex Patterns

```
Pattern: catch Exception
Regex: catch\s*\(\s*Exception\s+\w+
Multiline: false

Pattern: bare on/catch
Regex: \}\s*catch\s*\(\s*\w+\s*\)\s*\{
Multiline: false

Pattern: on Exception catch
Regex: on\s+Exception\s+catch
Multiline: false
```

### False Positives

- Skip if followed by `rethrow`
- Skip in test files (`_test.dart`)
- Skip if the catch block is specific (`on SpecificException`)

### Before

```dart
try {
  await processOrder(order);
} catch (e) {
  print('Error: $e');
}
```

### After

```dart
try {
  await processOrder(order);
} on ValidationException catch (e) {
  logger.warn('Invalid order: ${e.message}');
  rethrow;
} on DatabaseException catch (e) {
  logger.error('Database error', e);
  rethrow;
}
```

### AGENTS.md Rule

> Use `on SpecificException catch (e)` instead of bare `catch (e)`. Never catch generic `Exception` without rethrowing. Use `rethrow` for unhandled errors.

---

## Pattern 2: Hardcoded Secrets

**Pattern ID:** hardcoded-secrets
**Risk:** Critical
**Why bad:** Credentials in Dart source end up in compiled apps and version control.

### Regex Patterns

```
Pattern: hardcoded password
Regex: (password|passwd|pwd)\s*=\s*['"][^'"]{4,}['"]
Multiline: false

Pattern: hardcoded API key
Regex: (apiKey|apiSecret|api_key|API_KEY)\s*=\s*['"][a-zA-Z0-9_\-]{8,}['"]
Multiline: false

Pattern: AWS access key
Regex: AKIA[0-9A-Z]{16}
Multiline: false

Pattern: generic secret
Regex: (secret|token|jwt)\s*=\s*['"][^'"]{8,}['"]
Multiline: false
```

### False Positives

- Skip if value references `Platform.environment`, `dotenv`, `--dart-define`
- Skip in test files
- Skip if value contains `example`, `placeholder`, `test`, `mock`

### Before

```dart
const apiKey = 'sk_live_1234567890abcdef';
```

### After

```dart
final apiKey = Platform.environment['API_KEY']
    ?? (throw StateError('API_KEY is required'));
```

### AGENTS.md Rule

> Never hardcode credentials in Dart source. Use `Platform.environment`, `--dart-define`, or `flutter_dotenv` for configuration.

---

## Pattern 4: Sequential Async Operations

**Pattern ID:** sequential-async
**Risk:** High
**Why bad:** Awaiting inside loops serializes independent I/O. AI defaults to sequential awaits.

### Regex Patterns

```
Pattern: await in for loop
Regex: for\s*\([^)]*\)\s*\{[\s\S]*?\bawait\b
Multiline: true

Pattern: await in for-in
Regex: for\s*\(\s*(final|var)?\s*\w+\s+in\s+[\s\S]*?\bawait\b
Multiline: true
```

### False Positives

- Skip if each iteration depends on the previous result
- Skip if `Future.wait` is used in the same function
- Skip `await for` over streams (correct usage)

### Before

```dart
final results = <User>[];
for (final userId in userIds) {
  final user = await fetchUser(userId);
  results.add(user);
}
```

### After

```dart
final results = await Future.wait(
  userIds.map((userId) => fetchUser(userId)),
);
```

### AGENTS.md Rule

> Never await inside loops when iterations are independent. Use `Future.wait()` for parallel execution.

---

## Pattern 7: Type Safety Bypass

**Pattern ID:** type-safety-bypass
**Risk:** High
**Why bad:** Unsafe `late` keyword and forced casts bypass Dart's null safety. AI sees `late` as "how this codebase handles initialization."

### Regex Patterns

```
Pattern: late keyword
Regex: \blate\s+(final\s+)?(?!override)\w+
Multiline: false

Pattern: forced cast (as)
Regex: \bas\s+\w+[^?]
Multiline: false

Pattern: null assertion operator
Regex: \w+!\s*[.\[;,\)]
Multiline: false
```

### False Positives

- Skip `late` in Flutter widget state initialized in `initState()` (acceptable pattern)
- Skip `late` with immediate initializer (`late final x = computeValue()`)
- Skip `!` in boolean negation
- Skip `!` in `!=`
- Skip `as` in `as?` (conditional cast)

### Before

```dart
late UserService service;  // No guarantee it's initialized
final data = json as Map<String, dynamic>;  // Crashes if wrong type
final name = user!.name;  // Crashes if null
```

### After

```dart
late final UserService service = UserService();  // Immediate init

final data = json is Map<String, dynamic>
    ? json
    : throw FormatException('Expected Map');

final name = user?.name ?? 'Unknown';
```

### AGENTS.md Rule

> Use `late` only with immediate initializers or in `initState()`. Never use forced casts (`as Type`) - use `is` type checks. Use `?.` and `??` instead of null assertion `!`.
