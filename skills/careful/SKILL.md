---
description: 'Safety guardrails for destructive commands. Warns before rm -rf, DROP
  TABLE,
  force-push, git reset --hard, kubectl delete, and similar destructive operations.
  User can override each warning. Use when touching prod, debugging live systems,
  or working in a shared environment. Use when asked to "be careful", "safety mode",
  "prod mode", or "careful mode".'
name: careful
---

# careful

> Adapted from [gstack](https://github.com/garrytan/gstack) by Garry Tan (MIT License) for use with Perplexity Computer.

## Perplexity Computer Environment

The `bash` tool in Perplexity Computer runs in an isolated sandbox, so destructive commands
cannot affect your local machine. However, commands run with `api_credentials=["github"]`
can affect your real repositories (force-push, delete branches). Apply extra caution there.

<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

# /careful — Destructive Command Guardrails

Safety mode is now **active**. Every bash command will be checked for destructive
patterns before running. If a destructive command is detected, you'll be warned
and can choose to proceed or cancel.

```bash
mkdir -p (qstack memory) analytics
```

## What's protected

| Pattern | Example | Risk |
|---------|---------|------|
| `rm -rf` / `rm -r` / `rm --recursive` | `rm -rf /var/data` | Recursive delete |
| `DROP TABLE` / `DROP DATABASE` | `DROP TABLE users;` | Data loss |
| `TRUNCATE` | `TRUNCATE orders;` | Data loss |
| `git push --force` / `-f` | `git push -f origin main` | History rewrite |
| `git reset --hard` | `git reset --hard HEAD~3` | Uncommitted work loss |
| `git checkout .` / `git restore .` | `git checkout .` | Uncommitted work loss |
| `kubectl delete` | `kubectl delete pod` | Production impact |
| `docker rm -f` / `docker system prune` | `docker system prune -a` | Container/image loss |

## Safe exceptions

These patterns are allowed without warning:
- `rm -rf node_modules` / `.next` / `dist` / `__pycache__` / `.cache` / `build` / `.turbo` / `coverage`

## How it works

The hook reads the command from the tool input JSON, checks it against the
patterns above, and returns `permissionDecision: "ask"` with a warning message
if a match is found. You can always override the warning and proceed.

To deactivate, end the conversation or start a new one. Hooks are session-scoped.

## Skill Graph — What to Use Next

For directory-scoped protection, use `freeze`. For both safety warnings and directory lock, use `guard`.

**See also:** `guard`, `freeze`

