---
name: qstack-package
description: |
  Package and deliver client automation projects as production-ready bundles.
  Generates READMEs, health-check scripts, setup scripts, launchd plists,
  and documentation from a standardized template. Use when the user asks to
  "package this for a client", "create a deliverable", "bundle this project",
  "make this installable", "package for delivery", "client handoff",
  "create setup script", "make this one-click", or "prepare for deployment".
  Proactively suggest when the user has a working automation project and
  mentions a client, handoff, or delivery timeline.
---

# qstack-package

> Standardizes client automation delivery. Takes a working project and
> produces a professional, self-contained bundle with setup scripts,
> health checks, and documentation.

## Perplexity Computer Environment

1. **Read the project:** use `read`, `glob`, and `grep` to understand the project structure
2. **Generate files:** use `write` to create setup scripts, READMEs, health checks
3. **Test the setup:** use `bash` to dry-run the setup script in the sandbox
4. **Package:** use `bash` to create a `.tar.gz` or `.zip` bundle
5. **Share:** use `share_file` to deliver the bundle to the user
6. **If GitHub connected:** push to a client repo via `bash` with `api_credentials=["github"]`

## Package Template

Every client deliverable follows this structure:

```
[project-name]/
├── README.md              ← What it does, how to install, how to use
├── setup.sh               ← One-command installer (chmod +x && ./setup.sh)
├── Install.command         ← macOS double-click launcher (runs setup.sh)
├── config/
│   ├── .env.example       ← Template for secrets (never include real secrets)
│   └── [service].json     ← Service-specific config with placeholder values
├── scripts/
│   ├── health-check.sh    ← Verify everything is working
│   ├── start.sh           ← Start the service
│   ├── stop.sh            ← Stop the service
│   └── uninstall.sh       ← Clean removal
├── docs/
│   ├── SETUP.md           ← Detailed setup guide with screenshots
│   ├── TROUBLESHOOTING.md ← Common issues and fixes
│   └── ARCHITECTURE.md    ← How the system works (for technical clients)
└── [source files]         ← The actual project code
```

## Workflow

### Step 1: Analyze the Project

Read the project structure and identify:
- **What it does** — core functionality in one sentence
- **Dependencies** — runtime requirements (Node, Python, Bun, etc.)
- **Config needed** — API keys, tokens, URLs the client must provide
- **Services** — background processes, cron jobs, daemons
- **Platform** — macOS, Linux, or both

```
glob(pattern="/home/user/workspace/[project]/**/*")
read(file_path="/home/user/workspace/[project]/package.json")  # or requirements.txt, etc.
grep(pattern="process.env|os.environ|API_KEY|TOKEN|SECRET", glob="**/*.{js,ts,py,sh}")
```

### Step 2: Generate the README

Template:

```markdown
# [Project Name]

[One sentence: what it does and who it's for]

## Quick Start

```bash
chmod +x setup.sh && ./setup.sh
```

Or double-click `Install.command` on macOS.

## What You'll Need

- [Runtime] (e.g., Node.js 20+, Python 3.11+)
- [Service accounts] (e.g., Google Ads API access, Zapier account)
- [Tokens/keys] (listed below — the setup script will prompt for each)

## Configuration

| Setting | Where to Get It | Required? |
|---------|----------------|-----------|
| [API_KEY] | [URL/instructions] | Yes |
| [TOKEN] | [URL/instructions] | Yes |
| [OPTIONAL_SETTING] | [URL/instructions] | No |

## Health Check

```bash
./scripts/health-check.sh
```

## Troubleshooting

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
```

### Step 3: Generate the Setup Script

Principles:
- **Detect, don't assume** — check if dependencies are installed before installing
- **Prompt only when necessary** — skip questions that have sensible defaults
- **Fail loudly** — if a required step fails, stop and tell the user exactly what to do
- **Idempotent** — safe to run multiple times
- **No secrets in code** — prompt for secrets, write to .env, never embed

Template structure:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== [Project Name] Setup ==="

# 1. Check dependencies
command -v node >/dev/null 2>&1 || { echo "ERROR: Node.js required. Install from https://nodejs.org"; exit 1; }

# 2. Install packages
npm install --production

# 3. Prompt for configuration
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Enter your API key (get it from https://...):"
  read -r API_KEY
  sed -i '' "s/YOUR_API_KEY_HERE/$API_KEY/" .env
fi

# 4. Build (if needed)
npm run build

# 5. Set up background service (if needed)
# [launchd plist for macOS, systemd for Linux]

# 6. Health check
./scripts/health-check.sh

echo "=== Setup complete ==="
```

### Step 4: Generate the Health Check

```bash
#!/usr/bin/env bash
# health-check.sh — Verify [Project Name] is working

PASS=0; FAIL=0; WARN=0

check() {
  if eval "$2" >/dev/null 2>&1; then
    echo "  ✓ $1"; PASS=$((PASS+1))
  else
    echo "  ✗ $1"; FAIL=$((FAIL+1))
  fi
}

warn() {
  if eval "$2" >/dev/null 2>&1; then
    echo "  ✓ $1"; PASS=$((PASS+1))
  else
    echo "  ⚠ $1 (non-blocking)"; WARN=$((WARN+1))
  fi
}

echo "=== [Project Name] Health Check ==="

check "Node.js installed"          "command -v node"
check ".env file exists"           "test -f .env"
check "API key configured"         "grep -q 'API_KEY=.' .env"
check "Dependencies installed"     "test -d node_modules"
check "Build output exists"        "test -f build/index.js"
check "Service is running"         "curl -s http://localhost:[PORT]/health"

echo ""
echo "  Passed:   $PASS"
echo "  Warnings: $WARN"
echo "  Failed:   $FAIL"

[ "$FAIL" -eq 0 ] && echo "  All checks passed." || echo "  Fix items marked ✗ before use."
```

### Step 5: Generate macOS Launcher (if applicable)

`Install.command` — double-clickable from Finder:

```bash
#!/usr/bin/env bash
cd "$(dirname "$0")"
chmod +x setup.sh
./setup.sh
echo ""
echo "Press any key to close this window..."
read -n 1
```

### Step 6: Generate launchd Plist (if background service)

For macOS background services:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" ...>
<plist version="1.0">
<dict>
    <key>Label</key><string>com.[client].[project]</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/node</string>
        <string>[path]/build/index.js</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key><string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>[path]/logs/stdout.log</string>
    <key>StandardErrorPath</key><string>[path]/logs/stderr.log</string>
</dict>
</plist>
```

### Step 7: Package and Deliver

```bash
# Clean build artifacts
rm -rf node_modules .git

# Create the bundle
tar -czf [project-name]-v[version].tar.gz [project-name]/

# Or zip for non-technical clients
zip -r [project-name]-v[version].zip [project-name]/ -x "*.DS_Store" "*.git*"
```

Share via `share_file`.

## Security Checklist

Before packaging, verify:
- [ ] No real API keys, tokens, or secrets in any file
- [ ] `.env.example` has placeholder values only
- [ ] No `.git/` directory in the bundle
- [ ] No `node_modules/` in the bundle (setup.sh installs fresh)
- [ ] No personal paths (`/Users/[username]/`) hardcoded
- [ ] README includes instructions for revoking/rotating credentials if compromised

## Client Types

Adapt the package based on who's receiving it:

| Client Type | Emphasis | Skip |
|------------|----------|------|
| **Technical (developer)** | ARCHITECTURE.md, raw config files, CLI-first | Install.command, heavy hand-holding |
| **Semi-technical (power user)** | Balanced README, Install.command, health-check | Architecture details |
| **Non-technical (business owner)** | Install.command, screenshots in SETUP.md, Troubleshooting | Source code details, raw config |

Ask the user (via `ask_user_question`) which client type they're packaging for.

## Skill Graph — What to Use Next

Use after building a working automation project. Feeds from any build/ship workflow.

**Feeds from:** `ship`, `land-and-deploy`

**Next steps:** `document-release` (for ongoing doc updates), `qstack-scheduled-ops` (if the client needs monitoring)

**See also:** `qstack-connectors` (if the client's tools should integrate)
