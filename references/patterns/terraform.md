# Terraform Pattern Definitions

File filter: `*.tf`

---

## Pattern 2: Hardcoded Secrets

**Pattern ID:** hardcoded-secrets
**Risk:** Critical
**Why bad:** Credentials in Terraform files leak via version control and state files. AI copies the pattern of embedding secrets directly into infrastructure code, making every new resource definition a potential credential leak.

### Regex Patterns

```
Pattern: hardcoded password in resource
Regex: (password|master_password|admin_password)\s*=\s*"[^"]{4,}"
Multiline: false

Pattern: hardcoded access key
Regex: (access_key|secret_key)\s*=\s*"[a-zA-Z0-9/+]{16,}"
Multiline: false

Pattern: AWS access key ID
Regex: AKIA[0-9A-Z]{16}
Multiline: false

Pattern: hardcoded token
Regex: (token|api_key|api_secret)\s*=\s*"[^"]{8,}"
Multiline: false

Pattern: hardcoded secret in provider
Regex: (secret_key|client_secret|subscription_id)\s*=\s*"[^"]{8,}"
Multiline: false

Pattern: Vault token
Regex: (vault_token|VAULT_TOKEN)\s*=\s*"[^"]{8,}"
Multiline: false

Pattern: connection string
Regex: (connection_string|connection_url)\s*=\s*"[^"]*password[^"]*"
Multiline: false

Pattern: private key inline
Regex: -----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----
Multiline: false
```

### False Positives

- Skip if value references `var.`, `data.`, `local.`, `module.`
- Skip if value uses `sensitive = true` variable
- Skip if inside `.tfvars.example` files
- Skip if value contains `CHANGE_ME`, `TODO`, `example`, `placeholder`
- Skip if using `aws_secretsmanager_secret_version` data source

### Before

```hcl
provider "aws" {
  access_key = "AKIAEXAMPLE12345678"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  region     = "us-east-1"
}

resource "aws_db_instance" "default" {
  engine              = "mysql"
  instance_class      = "db.t3.micro"
  username            = "admin"
  password            = "super-secret-password"
}

resource "vault_generic_secret" "example" {
  path = "secret/foo"
  data_json = jsonencode({
    token = "hvs.CAESICjt8..."
  })
}
```

### After

```hcl
provider "aws" {
  # Credentials from environment: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
  # Or use AWS profiles / IAM roles
  region = "us-east-1"
}

variable "db_password" {
  type      = string
  sensitive = true
}

resource "aws_db_instance" "default" {
  engine              = "mysql"
  instance_class      = "db.t3.micro"
  username            = "admin"
  password            = var.db_password
}

data "aws_secretsmanager_secret_version" "vault_token" {
  secret_id = "vault-token"
}

resource "vault_generic_secret" "example" {
  path = "secret/foo"
  data_json = jsonencode({
    token = data.aws_secretsmanager_secret_version.vault_token.secret_string
  })
}
```

### AGENTS.md Rule

> Never hardcode credentials in Terraform files. Use `variable` blocks with `sensitive = true`, environment variables for provider auth, or data sources for secrets (`aws_secretsmanager_secret_version`, `vault_generic_secret`). Never commit `.tfvars` files with real credentials - add to `.gitignore`.
