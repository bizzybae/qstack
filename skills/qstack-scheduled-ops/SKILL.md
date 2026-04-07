---
name: qstack-scheduled-ops
description: |
  Automated monitoring and recurring tasks using Perplexity Computer's schedule_cron.
  Set up canary health checks, security audits, retros, performance benchmarks, and
  custom monitoring on a schedule. Use when the user asks to "monitor production",
  "schedule a security audit", "set up canary checks", "automate retros", "recurring
  QA", "watch this site", "alert me if anything breaks", "nightly benchmarks",
  "scheduled ops", or "set up monitoring". Proactively suggest after a deploy
  completes or when the user ships a feature to production.
---

# qstack-scheduled-ops

> Perplexity Computer-native capability. gstack has no scheduling — monitoring is manual.
> qstack uses `schedule_cron` to automate canary checks, security scans, retros, and
> benchmarks on any cadence.

## Available Schedules

### 1. Canary Health Check (Hourly or Custom)

Monitors a production URL for availability, console errors, and performance regressions.
Sends a notification only when something is wrong.

**Setup:**
```
schedule_cron(
  action="create",
  name="Production canary: [app name]",
  cron="0 * * * *",  # Every hour (UTC)
  task="""
    Check the production health of [URL]:
    1. Use fetch_url to verify the page returns 200
    2. Use browser_task to load the page and check for:
       - Console errors (especially uncaught exceptions)
       - Page load time > 3 seconds
       - Missing critical elements (header, nav, main content)
    3. If ANY check fails, send_notification with:
       - Title: "🔴 [app name] canary failure"
       - Body: what failed, the URL, and timestamp
    4. If all checks pass, do NOT send a notification (no noise)
  """,
  background=True,
  exact=False
)
```

**Suggested cadence:**
- Production app: every 1-2 hours
- Staging: every 4-6 hours
- Personal site: daily

### 2. Security Audit (Weekly)

Runs the CSO skill methodology against a repo on a schedule.

**Setup:**
```
schedule_cron(
  action="create",
  name="Weekly security audit: [repo]",
  cron="0 14 * * 1",  # Monday 10am ET (14 UTC)
  task="""
    Run a security audit on [repo]:
    1. Clone the repo: bash with api_credentials=["github"]: gh repo clone [owner/repo] /home/user/workspace/security-audit
    2. Check for:
       - Secrets in code (API keys, tokens, passwords)
       - Dependencies with known CVEs (check package.json / requirements.txt)
       - Exposed environment variables
       - SQL injection vectors
       - Missing auth checks on sensitive endpoints
    3. If ANY critical or high-severity findings, send_notification:
       - Title: "Security audit: [N] findings in [repo]"
       - Body: severity breakdown + top 3 findings
    4. Save full report to /home/user/workspace/security-audits/[date].md
    5. If no findings, do NOT notify (zero noise)
  """,
  background=True,
  exact=True
)
```

### 3. Weekly Retro (Friday Afternoon)

Automatically generates a weekly engineering retrospective.

**Setup:**
```
schedule_cron(
  action="create",
  name="Weekly retro: [repo]",
  cron="0 21 * * 5",  # Friday 5pm ET (21 UTC)
  task="""
    Generate a weekly engineering retro for [repo]:
    1. Clone: bash with api_credentials=["github"]: gh repo clone [owner/repo] /tmp/retro-repo
    2. Analyze the past 7 days: git log --since='7 days ago' --stat
    3. Produce:
       - Commits this week (count, authors)
       - Lines added/removed
       - Key features shipped
       - Test coverage changes
       - Notable patterns (large PRs, revert commits, hotfixes)
    4. Send notification:
       - Title: "Weekly retro: [repo]"
       - Body: key stats + highlights
  """,
  background=True,
  exact=True
)
```

### 4. Performance Benchmark (Nightly)

Tracks performance metrics over time and alerts on regressions.

**Setup:**
```
schedule_cron(
  action="create",
  name="Nightly benchmark: [app name]",
  cron="0 6 * * *",  # 2am ET (6 UTC)
  task="""
    Benchmark [URL]:
    1. Use browser_task to load the page and measure:
       - Time to first contentful paint
       - Total page load time
       - Number of network requests
       - Total transfer size
    2. Compare against previous benchmarks in memory:
       memory_search for "benchmark:[app name]"
    3. Store this run: memory_update with "benchmark:[app name] [date] — FCP: Xms, load: Xms, requests: N, size: X KB"
    4. If load time increased >30% from last run, send_notification:
       - Title: "Performance regression: [app name]"
       - Body: before vs after metrics
    5. If no regression, do NOT notify
  """,
  background=True,
  exact=False
)
```

### 5. Dependency Check (Weekly)

Scans for outdated or vulnerable dependencies.

**Setup:**
```
schedule_cron(
  action="create",
  name="Dependency check: [repo]",
  cron="0 15 * * 3",  # Wednesday 11am ET (15 UTC)
  task="""
    Check dependencies for [repo]:
    1. Clone: bash with api_credentials=["github"]: gh repo clone [owner/repo] /tmp/dep-check
    2. If package.json exists: run npm audit, check for critical/high vulns
    3. If requirements.txt exists: run pip audit or check against known CVE databases
    4. Check for major version updates available
    5. If critical vulnerabilities found, send_notification:
       - Title: "Vulnerable dependencies in [repo]"
       - Body: package names, severity, recommended action
  """,
  background=True,
  exact=False
)
```

## How to Use This Skill

When the user asks to set up monitoring, walk them through:

1. **What to monitor** — production URL, repo, or both?
2. **What cadence** — hourly, daily, weekly? (Remind: each scheduled run uses credits)
3. **What to alert on** — all findings, or critical-only?
4. **Timezone** — always convert to UTC for the cron expression using Python

Then create the cron job(s). Confirm with the user before creating (each run consumes credits).

## Managing Schedules

```
schedule_cron(action="list")     # Show all active schedules
schedule_cron(action="update", cron_id="...", cron="0 */4 * * *")  # Change cadence
schedule_cron(action="delete", cron_id="...")  # Remove a schedule
```

## Design Principles

1. **Zero noise** — never notify when everything is fine. Only alert on actual problems.
2. **Credit awareness** — remind users that each scheduled run consumes credits. Suggest appropriate cadences, not aggressive ones.
3. **Memory integration** — store metrics in Perplexity memory so trends can be tracked across runs.
4. **Idempotent** — each run is self-contained. No state files to corrupt, no daemon to crash.

## Skill Graph — What to Use Next

Set up recurring automated versions of canary, cso, benchmark, or retro.

**Feeds from:** `canary`, `cso`, `benchmark`, `retro`

