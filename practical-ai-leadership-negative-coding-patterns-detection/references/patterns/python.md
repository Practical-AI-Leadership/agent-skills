# Python Pattern Definitions

File filter: `*.py`

---

## Pattern 1: Broad Exception Handling

**Pattern ID:** broad-exception-handling
**Risk:** High
**Why bad:** Catches all exceptions including system exits and keyboard interrupts. Hides real bugs, makes debugging painful. AI sees broad catches as the standard pattern and replicates across every new function.

### Regex Patterns

```
Pattern: except Exception
Regex: except\s+Exception(\s+as\s+\w+)?:
Multiline: false

Pattern: bare except
Regex: ^\s*except\s*:
Multiline: false
```

### False Positives

- Skip if followed by `raise` on the next line (re-raise pattern is acceptable)
- Skip if inside a test file (`test_*.py`, `*_test.py`)
- Skip if the except block only contains logging + raise

### Before

```python
try:
    result = await api_call()
except Exception as e:
    logger.error(f"Failed: {e}")
```

### After

```python
try:
    result = await api_call()
except HTTPError as e:
    logger.error(f"API error: {e.status_code}")
    raise
except TimeoutError as e:
    logger.warning("Request timed out, retrying")
    result = await api_call()
except Exception as e:
    logger.exception("Unexpected error in api_call")
    raise
```

### AGENTS.md Rule

> Always catch specific exception types. Never use bare `except:` or `except Exception` without re-raising. Log with context. If a catch-all is needed as a last resort, always re-raise after logging.

---

## Pattern 2: Hardcoded Secrets

**Pattern ID:** hardcoded-secrets
**Risk:** Critical
**Why bad:** Credentials leak via version control. Hard to rotate. AI copies the pattern of embedding secrets directly into source, not just the specific value.

### Regex Patterns

```
Pattern: hardcoded password
Regex: (password|passwd|pwd)\s*=\s*['"][^'"]{4,}['"]
Multiline: false

Pattern: hardcoded API key
Regex: (api_key|apikey|api_secret|secret_key)\s*=\s*['"][a-zA-Z0-9_\-]{8,}['"]
Multiline: false

Pattern: AWS access key
Regex: AKIA[0-9A-Z]{16}
Multiline: false

Pattern: generic secret assignment
Regex: (secret|token|jwt_secret)\s*=\s*['"][^'"]{8,}['"]
Multiline: false

Pattern: OpenAI key
Regex: sk-[a-zA-Z0-9]{20,}
Multiline: false

Pattern: private key
Regex: -----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----
Multiline: false
```

### False Positives

- Skip if value references `os.environ`, `os.getenv`, `settings.`, `config.`
- Skip if inside a test file or fixture
- Skip if the variable name contains `example`, `placeholder`, `dummy`, `test`, `fake`, `mock`
- Skip if the value is clearly a placeholder: `xxx`, `changeme`, `TODO`, `your_key_here`
- Skip `.env.example` files

### Before

```python
API_KEY = "sk_live_1234567890abcdef"
AWS_ACCESS_KEY_ID = "AKIAEXAMPLE12345678"
DB_PASSWORD = "super-secret-password"
```

### After

```python
import os

API_KEY = os.environ["API_KEY"]
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
```

### AGENTS.md Rule

> Never hardcode credentials, API keys, tokens, or passwords in source code. Always use environment variables via `os.environ["KEY"]` or a secrets manager. Keep `.env` files in `.gitignore`.

---

## Pattern 3: SQL Injection

**Pattern ID:** sql-injection
**Risk:** Critical
**Why bad:** String interpolation in SQL enables data exposure and manipulation. AI generates new queries using the same unsafe interpolation pattern it found in existing code.

### Regex Patterns

```
Pattern: f-string SQL
Regex: f['"].*\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)\b
Multiline: false

Pattern: format string SQL
Regex: ['"].*\b(SELECT|INSERT|UPDATE|DELETE)\b.*['"]\.format\s*\(
Multiline: false

Pattern: percent format SQL
Regex: ['"].*\b(SELECT|INSERT|UPDATE|DELETE)\b.*['"].*%\s*\(
Multiline: false

Pattern: Django cursor.execute raw
Regex: cursor\.execute\s*\(\s*f['"]
Multiline: false

Pattern: Django QuerySet.extra
Regex: \.extra\s*\(
Multiline: false

Pattern: Django RawSQL
Regex: RawSQL\s*\(\s*f['"]
Multiline: false

Pattern: SQLAlchemy execute raw
Regex: \.execute\s*\(\s*f['"].*\b(SELECT|INSERT|UPDATE|DELETE)\b
Multiline: false

Pattern: SQLAlchemy text raw
Regex: (sqlalchemy\.)?text\s*\(\s*f['"]
Multiline: false
```

### False Positives

- Skip if the query uses only literal strings without variable interpolation
- Skip if parameterized placeholders (%s, :name) are used correctly
- Skip if inside an ORM migration file
- Skip `.extra()` if used without `where` parameter

### Before

```python
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```

### After

```python
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

### Before (SQLAlchemy)

```python
conn.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### After (SQLAlchemy)

```python
from sqlalchemy import text
conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})
```

### AGENTS.md Rule

> Always use parameterized queries. Never interpolate variables into SQL strings with f-strings, .format(), or % formatting. Use %s placeholders (psycopg2), :name placeholders (SQLAlchemy), or ORM methods.

---

## Pattern 4: Sequential Async Operations

**Pattern ID:** sequential-async
**Risk:** High
**Why bad:** Awaiting inside loops serializes I/O operations, creating N+1 latency. AI defaults to sequential awaits because it's the simplest pattern.

### Regex Patterns

```
Pattern: await in for loop
Regex: for\s+\w+\s+in\s+.*:[\s\S]*?await\s+
Multiline: true

Pattern: await in async for
Regex: async\s+for\s+\w+\s+in\s+.*:[\s\S]*?await\s+
Multiline: true
```

### False Positives

- Skip if there's only one iteration (e.g., `for item in [single_item]:`)
- Skip if the await result is used as input for the next iteration (genuine dependency)
- Skip if `asyncio.gather` or `asyncio.wait` is used nearby

### Before

```python
results = []
for user_id in user_ids:
    user = await fetch_user(user_id)
    results.append(user)
```

### After

```python
import asyncio

tasks = [fetch_user(user_id) for user_id in user_ids]
results = await asyncio.gather(*tasks)
```

### AGENTS.md Rule

> Never await inside loops when iterations are independent. Use `asyncio.gather()` for parallel execution. Only use sequential awaits when each iteration depends on the previous result.

---

## Pattern 5: N+1 Database Queries

**Pattern ID:** n-plus-one-queries
**Risk:** High
**Why bad:** Database queries inside loops execute one query per item instead of a single batch query. AI copies the "query per item" pattern into every data-fetching function.

### Regex Patterns

```
Pattern: Django ORM in loop
Regex: for\s+\w+\s+in\s+.*:[\s\S]*?\.objects\.(get|filter|exclude)\s*\(
Multiline: true

Pattern: SQLAlchemy query in loop
Regex: for\s+\w+\s+in\s+.*:[\s\S]*?session\.query\s*\(
Multiline: true

Pattern: Generic query in loop
Regex: for\s+\w+\s+in\s+.*:[\s\S]*?\.(query|execute|fetchone|fetchall)\s*\(
Multiline: true
```

### False Positives

- Skip if `select_related` or `prefetch_related` is used on the queryset
- Skip if `joinedload` or `subqueryload` is used in SQLAlchemy
- Skip if the loop variable is not used in the query

### Before (Django)

```python
for order in orders:
    customer = order.customer  # DB query each iteration
    print(f"{customer.name}: {order.total}")
```

### After (Django)

```python
orders = Order.objects.select_related('customer').all()
for order in orders:
    print(f"{order.customer.name}: {order.total}")
```

### Before (SQLAlchemy)

```python
for user in users:
    profile = session.query(Profile).filter_by(user_id=user.id).first()
```

### After (SQLAlchemy)

```python
from sqlalchemy.orm import joinedload
users = session.query(User).options(joinedload(User.profile)).all()
for user in users:
    profile = user.profile
```

### AGENTS.md Rule

> Never execute database queries inside loops. Use `select_related()`/`prefetch_related()` (Django), `joinedload()`/`subqueryload()` (SQLAlchemy), or batch `WHERE IN` queries.

---

## Pattern 6: Dynamic Code Execution

**Pattern ID:** dynamic-code-execution
**Risk:** Critical
**Why bad:** eval() and exec() enable arbitrary code execution. AI treats eval/exec as a valid approach for dynamic behavior and applies it wherever flexibility is needed.

### Regex Patterns

```
Pattern: eval usage
Regex: \beval\s*\(
Multiline: false

Pattern: exec usage
Regex: \bexec\s*\(
Multiline: false

Pattern: compile with exec
Regex: \bcompile\s*\(.*['"]exec['"]
Multiline: false
```

### False Positives

- Skip if inside a test file testing eval behavior
- Skip if `ast.literal_eval` (this is the safe alternative)
- Skip comments and docstrings

### Before

```python
value = eval(user_input)
```

### After (for data parsing)

```python
import json
value = json.loads(user_input)
```

### After (for Python literals only)

```python
import ast
value = ast.literal_eval(user_input)
```

### Before (exec)

```python
exec(user_code)
```

### After (exec)

```python
handlers = {
    "sum": sum,
    "max": max,
}
result = handlers[action](values)
```

### AGENTS.md Rule

> Never use `eval()` or `exec()`. Use `json.loads()` for data parsing, `ast.literal_eval()` for Python literals, or dispatch tables for dynamic behavior.

---

## Pattern 8: Error Suppression

**Pattern ID:** error-suppression
**Risk:** High
**Why bad:** Bare except clauses catch system exits and keyboard interrupts, masking real bugs. AI learns to suppress errors as the default handling strategy.

### Regex Patterns

```
Pattern: bare except
Regex: ^\s*except\s*:
Multiline: false

Pattern: pass in except
Regex: except.*:[\s\S]*?\bpass\b
Multiline: true

Pattern: nosec comment
Regex: #\s*nosec
Multiline: false
```

### False Positives

- Skip if inside a cleanup/teardown function where suppression is intentional
- Skip if the except block contains logging before pass

### Before

```python
try:
    process_data()
except:
    pass
```

### After

```python
try:
    process_data()
except (ValueError, KeyError) as e:
    logger.warning(f"Data processing issue: {e}")
except Exception as e:
    logger.exception("Unexpected error in process_data")
    raise
```

### AGENTS.md Rule

> Never use bare `except:` or `except: pass`. Always catch specific exceptions. If suppression is intentional, add a comment explaining why and log the error.

---

## Pattern 9: Command Injection

**Pattern ID:** command-injection
**Risk:** Critical
**Why bad:** shell=True and os.system() allow shell injection. AI copies the shell=True pattern for every new system call.

### Regex Patterns

```
Pattern: subprocess shell=True
Regex: subprocess\.(run|call|Popen|check_call|check_output)\s*\([^)]*shell\s*=\s*True
Multiline: false

Pattern: os.system
Regex: \bos\.system\s*\(
Multiline: false

Pattern: os.popen
Regex: \bos\.popen\s*\(
Multiline: false
```

### False Positives

- Skip if the command is a hardcoded string literal with no variable interpolation
- Skip if inside a test file

### Before

```python
subprocess.run(f"tar -czf {archive} {target}", shell=True, check=True)
```

### After

```python
subprocess.run(["tar", "-czf", archive, target], check=True)
```

### Before (os.system)

```python
os.system("rm -rf " + path)
```

### After (os.system)

```python
import shutil
shutil.rmtree(path)
```

### AGENTS.md Rule

> Never use `shell=True` in subprocess calls. Always pass commands as lists: `subprocess.run(["cmd", "arg1", "arg2"])`. Never use `os.system()` or `os.popen()` - use `subprocess.run()` with a list or stdlib alternatives (`shutil`, `pathlib`).
