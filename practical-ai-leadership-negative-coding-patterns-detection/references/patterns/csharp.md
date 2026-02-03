# C# Pattern Definitions

File filter: `*.cs`

---

## Pattern 1: Broad Exception Handling

**Pattern ID:** broad-exception-handling
**Risk:** High
**Why bad:** Catching generic `Exception` hides specific error cases. AI replicates broad catches across every method.

### Regex Patterns

```
Pattern: catch Exception
Regex: catch\s*\(\s*Exception\s+\w+\s*\)
Multiline: false

Pattern: bare catch
Regex: \}\s*catch\s*\{
Multiline: false

Pattern: catch with when (too broad)
Regex: catch\s*\(\s*Exception\s+\w+\s*\)\s*when
Multiline: false
```

### False Positives

- Skip if followed by `throw;` (re-throw)
- Skip in top-level middleware (`ExceptionHandler`, `ExceptionFilter`)
- Skip in test files

### Before

```csharp
try
{
    ProcessOrder(order);
}
catch (Exception ex)
{
    _logger.LogError(ex, "Failed");
}
```

### After

```csharp
try
{
    ProcessOrder(order);
}
catch (ValidationException ex)
{
    _logger.LogWarning("Invalid order: {Message}", ex.Message);
    throw new OrderProcessingException("Validation failed", ex);
}
catch (DbException ex)
{
    _logger.LogError(ex, "Database error processing order");
    throw new OrderProcessingException("Database error", ex);
}
```

### AGENTS.md Rule

> Catch specific exception types. Never catch `Exception` without re-throwing. Use exception filters (`when`) for conditional handling, not for catching all exceptions.

---

## Pattern 2: Hardcoded Secrets

**Pattern ID:** hardcoded-secrets
**Risk:** Critical
**Why bad:** Credentials in C# source leak via version control and decompilation.

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
Regex: (secret|token|jwt|connectionString)\s*=\s*"[^"]{8,}"
Multiline: false

Pattern: connection string with password
Regex: (Password|Pwd)\s*=\s*[^;]+;
Multiline: false
```

### False Positives

- Skip if value references `Environment.GetEnvironmentVariable`, `Configuration[`, `IConfiguration`
- Skip in test files and `appsettings.Development.json`
- Skip if value contains `example`, `placeholder`, `test`, `mock`

### Before

```csharp
private const string ApiKey = "sk_live_1234567890abcdef";
private const string ConnectionString = "Server=db;Password=secret123;";
```

### After

```csharp
private readonly string _apiKey = Environment.GetEnvironmentVariable("API_KEY")
    ?? throw new InvalidOperationException("API_KEY is required");

private readonly string _connectionString = configuration.GetConnectionString("Default")
    ?? throw new InvalidOperationException("ConnectionString is required");
```

### AGENTS.md Rule

> Never hardcode credentials or connection strings. Use `Environment.GetEnvironmentVariable()`, `IConfiguration`, or Azure Key Vault / AWS Secrets Manager.

---

## Pattern 3: SQL Injection

**Pattern ID:** sql-injection
**Risk:** Critical
**Why bad:** String interpolation in SQL enables injection. AI generates new queries using the same unsafe pattern.

### Regex Patterns

```
Pattern: string concat SQL
Regex: ".*\b(SELECT|INSERT|UPDATE|DELETE)\b.*"\s*\+
Multiline: false

Pattern: string interpolation SQL
Regex: \$".*\b(SELECT|INSERT|UPDATE|DELETE)\b.*\{
Multiline: false

Pattern: String.Format SQL
Regex: String\.Format\s*\(\s*"[^"]*\b(SELECT|INSERT|UPDATE|DELETE)\b
Multiline: false

Pattern: ExecuteSqlRaw with interpolation
Regex: ExecuteSqlRaw\s*\(\s*\$"
Multiline: false
```

### False Positives

- Skip if using parameterized placeholders (`@param`, `{0}` with SqlCommand)
- Skip if using Entity Framework LINQ (no raw SQL)
- Skip `ExecuteSqlInterpolated` (EF Core safe interpolation)

### Before

```csharp
var query = $"SELECT * FROM Users WHERE Id = {userId}";
command.CommandText = query;
```

### After

```csharp
command.CommandText = "SELECT * FROM Users WHERE Id = @userId";
command.Parameters.AddWithValue("@userId", userId);
```

### Before (EF Core)

```csharp
context.Database.ExecuteSqlRaw($"DELETE FROM Users WHERE Id = {userId}");
```

### After (EF Core)

```csharp
context.Database.ExecuteSqlInterpolated($"DELETE FROM Users WHERE Id = {userId}");
// Or use LINQ:
context.Users.Where(u => u.Id == userId).ExecuteDelete();
```

### AGENTS.md Rule

> Always use parameterized queries with `@param` placeholders. Use `ExecuteSqlInterpolated` instead of `ExecuteSqlRaw` in EF Core. Prefer LINQ over raw SQL.

---

## Pattern 5: N+1 Database Queries

**Pattern ID:** n-plus-one-queries
**Risk:** High
**Why bad:** Database queries inside loops execute one query per item.

### Regex Patterns

```
Pattern: query in foreach
Regex: foreach\s*\([^)]*\)\s*\{[\s\S]*?\.(Find|FirstOrDefault|SingleOrDefault|Where)\s*\(
Multiline: true

Pattern: query in for
Regex: for\s*\([^)]*\)\s*\{[\s\S]*?\.(Find|FirstOrDefault|SingleOrDefault|Where)\s*\(
Multiline: true
```

### False Positives

- Skip if `.Include()` or `.ThenInclude()` is used on the query
- Skip if the loop iterates over in-memory collections
- Skip if the query is against a different DbContext/repository

### Before

```csharp
foreach (var orderId in orderIds)
{
    var order = await context.Orders.FindAsync(orderId);
    orders.Add(order);
}
```

### After

```csharp
var orders = await context.Orders
    .Where(o => orderIds.Contains(o.Id))
    .Include(o => o.Customer)
    .ToListAsync();
```

### AGENTS.md Rule

> Never execute EF Core queries inside loops. Use `.Where(x => ids.Contains(x.Id))` with `.Include()` for eager loading.
