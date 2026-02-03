# Java Pattern Definitions

File filter: `*.java`

---

## Pattern 1: Broad Exception Handling

**Pattern ID:** broad-exception-handling
**Risk:** High
**Why bad:** Catching `Exception` or `Throwable` hides specific error cases. AI replicates broad catches across every method.

### Regex Patterns

```
Pattern: catch Exception
Regex: catch\s*\(\s*Exception\s+\w+\s*\)
Multiline: false

Pattern: catch Throwable
Regex: catch\s*\(\s*Throwable\s+\w+\s*\)
Multiline: false
```

### False Positives

- Skip if followed by `throw` on next line (re-throw)
- Skip if in a top-level error handler (main method, servlet filter)
- Skip in test files

### Before

```java
try {
    processOrder(order);
} catch (Exception e) {
    logger.error("Failed", e);
}
```

### After

```java
try {
    processOrder(order);
} catch (ValidationException e) {
    logger.warn("Invalid order: {}", e.getMessage());
    throw new OrderProcessingException("Validation failed", e);
} catch (DatabaseException e) {
    logger.error("Database error processing order", e);
    throw new OrderProcessingException("Database error", e);
}
```

### AGENTS.md Rule

> Catch specific exception types. Never catch `Exception` or `Throwable` without re-throwing. Use multi-catch (`catch (TypeA | TypeB e)`) when handling is identical.

---

## Pattern 2: Hardcoded Secrets

**Pattern ID:** hardcoded-secrets
**Risk:** Critical
**Why bad:** Credentials in Java source leak via JARs, decompilers, and version control.

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

Pattern: private key
Regex: -----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----
Multiline: false
```

### False Positives

- Skip if value references `System.getenv`, `System.getProperty`, `@Value`, `config.get`
- Skip in test files
- Skip if value contains `example`, `placeholder`, `test`, `mock`, `dummy`

### Before

```java
private static final String API_KEY = "sk_live_1234567890";
private static final String DB_PASSWORD = "super-secret";
```

### After

```java
private static final String API_KEY = System.getenv("API_KEY");
private static final String DB_PASSWORD = System.getenv("DB_PASSWORD");
```

### AGENTS.md Rule

> Never hardcode credentials in Java source. Use `System.getenv()`, Spring `@Value`, or a secrets manager (Vault, AWS Secrets Manager).

---

## Pattern 3: SQL Injection

**Pattern ID:** sql-injection
**Risk:** Critical
**Why bad:** String concatenation in SQL enables injection. AI generates new queries using the same unsafe concatenation.

### Regex Patterns

```
Pattern: string concat SQL
Regex: ".*\b(SELECT|INSERT|UPDATE|DELETE)\b.*"\s*\+
Multiline: false

Pattern: String.format SQL
Regex: String\.format\s*\(\s*"[^"]*\b(SELECT|INSERT|UPDATE|DELETE)\b
Multiline: false

Pattern: Statement.execute with concat
Regex: \.(execute|executeQuery|executeUpdate)\s*\(\s*"[^"]*\b(SELECT|INSERT|UPDATE|DELETE)\b[^"]*"\s*\+
Multiline: false
```

### False Positives

- Skip if using `PreparedStatement` with `?` placeholders
- Skip if inside migration/flyway files
- Skip if using JPA `@Query` with `:param` notation

### Before

```java
String query = "SELECT * FROM users WHERE id = " + userId;
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(query);
```

### After

```java
String query = "SELECT * FROM users WHERE id = ?";
PreparedStatement stmt = conn.prepareStatement(query);
stmt.setInt(1, userId);
ResultSet rs = stmt.executeQuery();
```

### AGENTS.md Rule

> Always use `PreparedStatement` with `?` placeholders. Never concatenate user input into SQL strings. Use JPA `@Query` with named parameters for Spring Data.

---

## Pattern 5: N+1 Database Queries

**Pattern ID:** n-plus-one-queries
**Risk:** High
**Why bad:** Database queries inside loops execute one query per item.

### Regex Patterns

```
Pattern: query in for loop
Regex: for\s*\([^)]*\)\s*\{[\s\S]*?\.(find|query|execute|getReference|getOne)\s*\(
Multiline: true

Pattern: query in enhanced for
Regex: for\s*\(\s*\w+\s+\w+\s*:\s*[\s\S]*?\.(find|query|execute)\s*\(
Multiline: true
```

### False Positives

- Skip if `@EntityGraph` or `JOIN FETCH` is used
- Skip if `@BatchSize` annotation is present on entity
- Skip if loop body performs writes, not reads

### Before

```java
for (Long orderId : orderIds) {
    Order order = orderRepository.findById(orderId).orElseThrow();
    orders.add(order);
}
```

### After

```java
List<Order> orders = orderRepository.findAllById(orderIds);
```

### AGENTS.md Rule

> Never execute JPA/JDBC queries inside loops. Use `findAllById()`, `WHERE IN` queries, or `@EntityGraph`/`JOIN FETCH` for eager loading.
