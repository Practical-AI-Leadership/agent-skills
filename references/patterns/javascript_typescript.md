# JavaScript / TypeScript Pattern Definitions

File filter: `*.{js,jsx,ts,tsx,mjs,cjs}`

---

## Pattern 1: Broad Exception Handling

**Pattern ID:** broad-exception-handling
**Risk:** High
**Why bad:** Generic try/catch blocks hide specific error cases. AI sees broad catches as the standard pattern and replicates across every new function.

### Regex Patterns

```
Pattern: generic catch
Regex: catch\s*\(\s*\w+\s*\)\s*\{
Multiline: false

Pattern: catch with console.log only
Regex: catch\s*\(\s*\w+\s*\)\s*\{[\s\S]*?console\.(log|error|warn)\s*\([\s\S]*?\}
Multiline: true
```

### False Positives

- Skip if the catch block rethrows (`throw err` or `throw new`)
- Skip if inside test files (`*.test.ts`, `*.spec.ts`)
- Skip if the catch block uses `instanceof` to check error types

### Before

```javascript
try {
  doWork();
} catch (err) {
  console.log(err);
}
```

### After

```javascript
try {
  doWork();
} catch (err) {
  if (err instanceof ValidationError) {
    handleValidation(err);
  } else if (err instanceof NetworkError) {
    handleNetwork(err);
  } else {
    throw err;
  }
}
```

### AGENTS.md Rule

> Always check error types in catch blocks using `instanceof`. Never silently log and swallow errors. Rethrow unknown errors.

---

## Pattern 2: Hardcoded Secrets

**Pattern ID:** hardcoded-secrets
**Risk:** Critical
**Why bad:** Credentials leak via version control. AI copies the pattern of embedding secrets directly into source.

### Regex Patterns

```
Pattern: hardcoded API key
Regex: (api_key|apikey|api_secret|API_KEY)\s*[:=]\s*['"][a-zA-Z0-9_\-]{16,}['"]
Multiline: false

Pattern: AWS access key
Regex: AKIA[0-9A-Z]{16}
Multiline: false

Pattern: OpenAI key
Regex: sk-[a-zA-Z0-9]{20,}
Multiline: false

Pattern: generic secret
Regex: (secret|token|password|passwd)\s*[:=]\s*['"][^'"]{8,}['"]
Multiline: false

Pattern: database password
Regex: (mysql|Sequelize|Pool|knex|pg).*password\s*:\s*['"][^'"]+['"]
Multiline: false

Pattern: connection string with creds
Regex: (mongodb|postgres|mysql|redis)://\w+:[^@]+@
Multiline: false

Pattern: private key
Regex: -----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----
Multiline: false
```

### False Positives

- Skip if value references `process.env.`, `config.`, `import.meta.env.`
- Skip if inside `.env.example` or test fixtures
- Skip if value contains `example`, `placeholder`, `dummy`, `test`, `mock`, `xxx`, `changeme`

### Before

```javascript
const API_KEY = "sk_live_1234567890abcdef";
const DB_PASSWORD = "super-secret-password";
```

### After

```javascript
const API_KEY = process.env.API_KEY;
const DB_PASSWORD = process.env.DB_PASSWORD;
```

### AGENTS.md Rule

> Never hardcode credentials, API keys, tokens, or passwords. Use `process.env.KEY` (Node.js) or `import.meta.env.KEY` (Vite). Keep `.env` in `.gitignore`.

---

## Pattern 3: SQL Injection

**Pattern ID:** sql-injection
**Risk:** Critical
**Why bad:** String concatenation in SQL queries enables injection attacks. AI generates new queries using the same unsafe pattern.

### Regex Patterns

```
Pattern: string concat SQL
Regex: ['"`].*\b(SELECT|INSERT|UPDATE|DELETE)\b.*['"`]\s*\+
Multiline: false

Pattern: template literal SQL
Regex: `[^`]*\$\{[^}]+\}[^`]*\b(SELECT|INSERT|UPDATE|DELETE)\b
Multiline: false

Pattern: template literal SQL (reversed)
Regex: `[^`]*\b(SELECT|INSERT|UPDATE|DELETE)\b[^`]*\$\{[^}]+\}
Multiline: false

Pattern: Sequelize raw query
Regex: \.query\s*\(\s*['`"].*\b(SELECT|INSERT|UPDATE|DELETE)\b.*['`"]\s*\+
Multiline: false

Pattern: Knex raw
Regex: \.(raw|whereRaw|havingRaw|orderByRaw)\s*\(\s*['`"].*\$\{
Multiline: false

Pattern: Node SQL driver
Regex: \.(query|execute)\s*\(\s*['`"].*\b(SELECT|INSERT|UPDATE|DELETE)\b.*['`"]\s*\+
Multiline: false

Pattern: MongoDB $where
Regex: \$where\s*[:=]
Multiline: false
```

### False Positives

- Skip if using parameterized placeholders (`?`, `$1`, `:name`)
- Skip if inside ORM model definitions
- Skip if the query is a static string without variable interpolation

### Before

```javascript
await sequelize.query("SELECT * FROM users WHERE id = " + userId);
```

### After

```javascript
await sequelize.query("SELECT * FROM users WHERE id = ?", {
  replacements: [userId],
});
```

### Before (Knex)

```javascript
await knex.raw("SELECT * FROM users WHERE id = " + userId);
```

### After (Knex)

```javascript
await knex.raw("SELECT * FROM users WHERE id = ?", [userId]);
```

### AGENTS.md Rule

> Always use parameterized queries. Never concatenate or interpolate variables into SQL strings. Use `?` placeholders (Sequelize, Knex) or `$1` (pg). Never use MongoDB `$where`.

---

## Pattern 4: Sequential Async Operations

**Pattern ID:** sequential-async
**Risk:** High
**Why bad:** Awaiting inside loops serializes independent I/O operations. AI defaults to sequential awaits.

### Regex Patterns

```
Pattern: await in for loop
Regex: for\s*\([^)]*\)\s*\{[\s\S]*?await\s+
Multiline: true

Pattern: await in for-of loop
Regex: for\s*\(\s*(const|let|var)\s+\w+\s+of\s+[\s\S]*?await\s+
Multiline: true

Pattern: await in forEach
Regex: \.forEach\s*\(\s*async\s*\([^)]*\)\s*=>[\s\S]*?await\s+
Multiline: true
```

### False Positives

- Skip if each iteration depends on the previous result
- Skip if `Promise.all` or `Promise.allSettled` is used in the same function
- Skip `for await...of` over async iterators (this is correct usage)

### Before

```javascript
const results = [];
for (const userId of userIds) {
  const user = await fetchUser(userId);
  results.push(user);
}
```

### After

```javascript
const results = await Promise.all(
  userIds.map(userId => fetchUser(userId))
);
```

### Before (forEach)

```javascript
items.forEach(async item => {
  await processItem(item);
});
```

### After (forEach - parallel)

```javascript
await Promise.all(items.map(item => processItem(item)));
```

### AGENTS.md Rule

> Never await inside loops when iterations are independent. Use `Promise.all()` for parallel execution. Never use `forEach` with async callbacks - use `for...of` for sequential or `Promise.all(arr.map(...))` for parallel.

---

## Pattern 5: N+1 Database Queries

**Pattern ID:** n-plus-one-queries
**Risk:** High
**Why bad:** Database queries inside loops execute one query per item. AI copies the "query per item" pattern.

### Regex Patterns

```
Pattern: query in for loop
Regex: for\s*\([^)]*\)\s*\{[\s\S]*?\.(find|findOne|findById|query|execute)\s*\(
Multiline: true

Pattern: query in for-of
Regex: for\s*\(\s*(const|let|var)\s+\w+\s+of\s+[\s\S]*?\.(find|findOne|findById|query|execute)\s*\(
Multiline: true

Pattern: query in forEach
Regex: \.forEach\s*\([\s\S]*?\.(find|findOne|findById|query|execute)\s*\(
Multiline: true
```

### False Positives

- Skip if using `.populate()` (Mongoose eager loading)
- Skip if the loop body performs writes, not reads
- Skip if `include` option is present (Sequelize eager loading)

### Before

```javascript
for (const orderId of orderIds) {
  const order = await Order.findById(orderId);
  results.push(order);
}
```

### After

```javascript
const orders = await Order.find({ _id: { $in: orderIds } });
```

### AGENTS.md Rule

> Never execute database queries inside loops. Use batch queries (`WHERE IN`, `$in`), eager loading (`.populate()`, `include`), or data loaders.

---

## Pattern 6: Dynamic Code Execution

**Pattern ID:** dynamic-code-execution
**Risk:** Critical
**Why bad:** eval(), new Function(), and similar enable arbitrary code execution. AI treats eval as a valid approach for dynamic behavior.

### Regex Patterns

```
Pattern: eval usage
Regex: \beval\s*\(
Multiline: false

Pattern: Function constructor
Regex: new\s+Function\s*\(
Multiline: false
```

### False Positives

- Skip if inside a test file
- Skip `JSON.parse()` (this is the safe alternative, not eval)
- Skip comments

### Before

```javascript
const result = eval(userExpression);
```

### After

```javascript
const handlers = { sum: (a, b) => a + b, max: Math.max };
const result = handlers[action](a, b);
```

### Before (Function constructor)

```javascript
const fn = new Function(`return ${userExpression}`);
```

### After

```javascript
const allowed = { add: (a, b) => a + b };
const fn = allowed[action];
```

### AGENTS.md Rule

> Never use `eval()` or `new Function()`. Use `JSON.parse()` for data, dispatch tables for dynamic behavior, or structured parsers for expressions.

---

## Pattern 7: Type Safety Bypass

**Pattern ID:** type-safety-bypass
**Risk:** High
**Why bad:** Non-null assertions, `any` type, and similar bypass the type system. AI sees bypass patterns as "how this codebase handles types" and applies them everywhere.

### Regex Patterns

```
Pattern: any type annotation
Regex: :\s*any\b
Multiline: false
File filter: *.{ts,tsx}

Pattern: as any cast
Regex: \bas\s+any\b
Multiline: false
File filter: *.{ts,tsx}

Pattern: non-null assertion
Regex: \w+!\s*[;,\).\[]
Multiline: false
File filter: *.{ts,tsx}

Pattern: ts-ignore
Regex: @ts-ignore|@ts-nocheck
Multiline: false
File filter: *.{ts,tsx}
```

### False Positives

- Skip `!` in boolean negation context (`!variable`, `!==`)
- Skip `any` in comments or string literals
- Skip generic type parameters that happen to contain `any`
- Skip test files for `as any` (common in test mocking)
- Skip `!` at end of line in non-TypeScript files (not assertion)

### Before

```typescript
function processData(data: any) {
    return data.value * 2;
}

const name = user!.name;
```

### After

```typescript
interface DataWithValue {
    value: number;
}

function processData(data: DataWithValue) {
    return data.value * 2;
}

if (!user) {
    throw new Error('User is required');
}
const name = user.name;
```

### AGENTS.md Rule

> Never use `any` type - define proper interfaces. Never use non-null assertions (`!.`) - use type guards or null checks. Never use `@ts-ignore` - fix the type error.

---

## Pattern 8: Error Suppression

**Pattern ID:** error-suppression
**Risk:** High
**Why bad:** Empty catch blocks and ignored promises hide failures. AI learns to suppress errors as the default strategy.

### Regex Patterns

```
Pattern: empty catch block
Regex: catch\s*\(\s*\w*\s*\)\s*\{\s*\}
Multiline: false

Pattern: catch with only comment
Regex: catch\s*\(\s*\w*\s*\)\s*\{[\s\S]*?//[\s\S]*?\}
Multiline: true

Pattern: unhandled promise
Regex: \.catch\s*\(\s*\(\s*\)\s*=>\s*\{\s*\}\s*\)
Multiline: false
```

### False Positives

- Skip if inside cleanup/teardown code
- Skip if the empty catch has a comment explaining why suppression is intentional

### Before

```javascript
try {
  doWork();
} catch (err) {}

promise.catch(() => {});
```

### After

```javascript
try {
  doWork();
} catch (err) {
  if (err instanceof KnownError) {
    handleKnown(err);
  } else {
    throw err;
  }
}

promise.catch(err => {
  logger.error('Unhandled promise rejection:', err);
});
```

### AGENTS.md Rule

> Never use empty catch blocks. Either handle the error, log and rethrow, or remove the try/catch. Never use `.catch(() => {})` - always log or handle.

---

## Pattern 9: Command Injection

**Pattern ID:** command-injection
**Risk:** Critical
**Why bad:** child_process.exec with string concatenation allows shell injection. AI copies this pattern for every new system call.

### Regex Patterns

```
Pattern: child_process.exec with concat
Regex: child_process\.exec\s*\(\s*['"`].*\+
Multiline: false

Pattern: exec with template literal
Regex: child_process\.exec\s*\(\s*`[^`]*\$\{
Multiline: false

Pattern: execSync with concat
Regex: execSync\s*\(\s*['"`].*\+
Multiline: false

Pattern: execSync with template literal
Regex: execSync\s*\(\s*`[^`]*\$\{
Multiline: false
```

### False Positives

- Skip if the command is a hardcoded string with no interpolation
- Skip if inside a test file

### Before

```javascript
const { exec } = require('child_process');
exec(`tar -czf ${archive} ${target}`);
```

### After

```javascript
const { execFile } = require('child_process');
execFile('tar', ['-czf', archive, target]);
```

### AGENTS.md Rule

> Never use `child_process.exec()` with string interpolation. Use `child_process.execFile()` or `child_process.spawn()` with arguments as an array.

---

## Pattern 10: DOM Injection (XSS)

**Pattern ID:** dom-injection-xss
**Risk:** Critical
**Why bad:** innerHTML and document.write inject unescaped content into the DOM. AI uses innerHTML as the default DOM manipulation method.

### Regex Patterns

```
Pattern: innerHTML assignment
Regex: \.innerHTML\s*=
Multiline: false

Pattern: document.write
Regex: document\.write\s*\(
Multiline: false

Pattern: dangerouslySetInnerHTML
Regex: dangerouslySetInnerHTML
Multiline: false

Pattern: v-html directive
Regex: v-html\s*=
Multiline: false
```

### False Positives

- Skip if the value is a sanitized output (using DOMPurify, sanitize-html)
- Skip if assigning empty string (`innerHTML = ''` for clearing)
- Skip if inside a test file
- Skip `dangerouslySetInnerHTML` if wrapped in a sanitizer

### Before

```javascript
container.innerHTML = userInput;
document.write(userContent);
```

### After

```javascript
container.textContent = userInput;

// For rich content, sanitize first:
import DOMPurify from 'dompurify';
container.innerHTML = DOMPurify.sanitize(richContent);
```

### After (React)

```jsx
// Instead of dangerouslySetInnerHTML, use a sanitizer:
<div>{DOMPurify.sanitize(content)}</div>
```

### AGENTS.md Rule

> Never use `innerHTML` with user input. Use `textContent` for plain text. If HTML rendering is needed, always sanitize with DOMPurify or equivalent. Never use `document.write()`. In React, avoid `dangerouslySetInnerHTML` - if unavoidable, always sanitize.
