# OpenClaw Integration v0 — Two Runtimes, One Brain

## The Opportunity

OpenClaw has 247K GitHub stars — bigger than React. It's the dominant open-source
AI agent framework. It runs always-on, connects to messaging (WhatsApp, Telegram,
Slack, iMessage), manages calendar, memory, and proactive outreach. It's the
"personal AI operating system."

gstack is the deep-work coding agent — spawned per-task, writes artifacts, ships
code, terminates. It doesn't run 24/7. It doesn't manage your calendar.

These aren't competitors. They're complementary runtimes:

- **OpenClaw (Wintermute)**: always-on brain. Messaging, calendar, memory, orchestration.
- **gstack (Claude Code)**: deep-work hands. Coding, review, ship, QA.

The 10/10 version isn't "port gstack skills to OpenClaw format." It's making them
one system with two execution modes and a shared memory/dispatch layer.

## Current State

**PR #491** by @latifclawbot-mdil ported 22 gstack skills to OpenClaw as a thin
compatibility subtree. Each skill is ~15-20 lines, manually maintained, will drift
from templates immediately. Wrong architecture — should be generator-native.

**PR #114** by @dddabtc was an earlier attempt (10 skills). Already closed.

Both approaches treat OpenClaw as a translation target. The right approach treats
it as a co-runtime.

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Wintermute (OpenClaw, always-on)               │
│  Messaging. Calendar. Memory. Orchestration.    │
│                                                 │
│  ┌───────────────────────────────────────┐      │
│  │ Shared Layer                          │      │
│  │  ~/.gstack/routing.yaml              │      │
│  │  ~/.gstack/activity.jsonl            │      │
│  │  ~/.gstack/dispatch/{id}.json        │      │
│  │  ~/.gstack/handoff/{id}.md           │      │
│  │  learnings (bidirectional)           │      │
│  └──────────────┬────────────────────────┘      │
│                 │                                │
│  Creates Clawvisor task for authorization        │
└─────────────────┼───────────────────────────────┘
                  │
                  │ HTTPS via ngrok tunnel
                  │
┌─────────────────▼───────────────────────────────┐
│  Clawvisor (security gateway, your Mac)         │
│  Credential vaulting + task-scoped auth          │
│  Human approval for sensitive operations         │
│  Chain context verification (anti-injection)     │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  gstack-dispatch-daemon (your Mac)              │
│  Spawns Claude Code sessions per task            │
│  Monitors progress, writes completion reports    │
│  Reports back via Clawvisor callback             │
└─────────────────────────────────────────────────┘
```

## Component Design

### 1. Generator-Native OpenClaw Output

Instead of maintaining a separate `openclaw/` subtree, modify `gen-skill-docs.ts`
to emit OpenClaw variants from the same `.tmpl` templates.

New resolver: `scripts/resolvers/openclaw.ts`

**What it does:**
- Replaces Claude tool references with OpenClaw equivalents
  (`Read` → `read`, `Bash` → `exec`, `$B` → `browser`)
- Strips Claude-specific preamble (telemetry, upgrade checks, session tracking)
- Injects OpenClaw-native YAML frontmatter (`triggers`, `version`,
  `metadata.openclaw.requires`)
- Maps `AskUserQuestion` → "ask in chat reply"
- Maps `Agent` spawning → `sessions_spawn` with appropriate `maxSpawnDepth`
- Outputs to `openclaw/skills/` directory

Every `bun run build` produces both Claude and OpenClaw variants from one source
of truth. Zero drift. Zero manual maintenance.

**Tool mapping table (reference for resolver):**

| gstack (Claude Code)  | OpenClaw              |
|------------------------|-----------------------|
| Read                   | `read`                |
| Write                  | `write`               |
| Edit                   | `edit`                |
| Bash                   | `exec`                |
| WebSearch              | `web_search`          |
| browse binary (`$B`)   | `browser` or `exec $B`|
| Agent / subagents      | `sessions_spawn`      |
| AskUserQuestion        | chat reply / `message` |
| CLAUDE.md              | AGENTS.md             |

### 2. SOUL.md — The Builder Identity

OpenClaw's SOUL.md defines persistent agent personality. gstack ships one that
captures the builder ethos:

```markdown
# gstack soul

You are a builder's coding agent. You ship complete implementations, not
shortcuts. You search before building. You prize first-principles thinking
above convention.

## Core principles
- Completeness is cheap with AI coding. Don't recommend shortcuts when the
  complete implementation is achievable. Boil the lake.
- Search for built-ins and best practices before designing solutions.
  Three layers: tried-and-true, new-and-popular, first-principles.
  Prize Layer 3 above all.
- Builder > Optimizer. Ship the thing, then improve it.

## Voice
Direct. Opinionated. No hedging. Lead with the answer, not the reasoning.
Say "do X" not "you might consider X." If you're wrong, be wrong confidently
and correct fast.

## When dispatched by Wintermute
You're the deep-work specialist. Wintermute handles orchestration. You handle
execution. Report back with: what shipped, decisions made, learnings,
and anything that needs human judgment.
```

### 3. Shared Learnings Store (Bidirectional)

**gstack → OpenClaw:**
After each session, write a parallel copy of new learnings as OpenClaw memory:

```
~/.gstack/projects/{slug}/learnings.jsonl     (gstack native)
~/.openclaw/workspace/memory/gstack-{slug}.md (OpenClaw readable)
```

Format bridge: each JSONL entry (`pattern`, `context`, `confidence`) becomes a
markdown section in the OpenClaw memory file.

**OpenClaw → gstack:**
Extend `LEARNINGS_SEARCH` in the preamble to also grep
`~/.openclaw/workspace/memory/*.md`. When gstack starts a coding session, it
already knows what Wintermute learned overnight.

**Cost:** ~30 min. Both formats are text files. The bridge is a read adapter.

### 4. Shared Routing Config

A routing table that both runtimes read:

```yaml
# ~/.gstack/routing.yaml
routes:
  - match: { project: "baku", files: ["calendar/*"] }
    load: ["kitsune-context", "calendar-api-docs"]
  - match: { task_type: "security" }
    skills: ["gstack-cso", "gstack-careful"]
  - match: { task_type: "shipping" }
    skills: ["gstack-ship", "gstack-review"]
```

gstack's preamble resolver reads this. OpenClaw's AGENTS.md references it. Same
routing table, two readers. "If touching calendar → load kitsune context" works
in both runtimes.

### 5. Dispatch Protocol (Wintermute → gstack)

The flow when Wintermute dispatches a coding task:

**Step 1: Wintermute creates dispatch file**
```json
{
  "id": "dispatch-2026-04-03-auth-flow",
  "dispatched_by": "wintermute",
  "task": "Build JWT auth flow with refresh token rotation",
  "project": "baku",
  "project_dir": "~/git/baku",
  "learnings": ["...relevant memories from Wintermute..."],
  "constraints": ["mobile client needs offline token refresh"],
  "callback": "~/.openclaw/inbox/dispatch-{id}.md",
  "clawvisor_task_id": "task_abc123",
  "ttl_seconds": 3600
}
```

**Step 2: Clawvisor authorization (see section 7)**

**Step 3: gstack-dispatch-daemon spawns session**
```bash
claude --print --permission-mode bypassPermissions \
  --project ~/git/baku \
  "Load gstack. Dispatch ID: dispatch-2026-04-03-auth-flow. \
   Read dispatch context from ~/.gstack/dispatch/dispatch-2026-04-03-auth-flow.json"
```

**Step 4: gstack preamble reads dispatch context**
- Skips AskUserQuestion (non-interactive)
- Pre-loads task description, learnings, constraints
- Runs the task

**Step 5: On completion, writes report**
```markdown
---
dispatch_id: dispatch-2026-04-03-auth-flow
status: completed
duration: 847s
commits: 3
pr: garrytan/baku#47
---

## What shipped
JWT auth flow with refresh token rotation. 3 commits:
1. Schema migration for refresh_tokens table
2. Auth middleware with JWT verification + refresh endpoint
3. Tests: 12 cases covering expiry, rotation, revocation

## Decisions made
- JWT over sessions: mobile client needs offline capability
- 15-min access token TTL, 7-day refresh token
- Refresh rotation: old token invalidated on use (replay protection)

## Learnings logged
- Baku uses Drizzle ORM, not Prisma (discovered from existing schema)
- Test runner is vitest, not jest

## Needs human judgment
- Should refresh tokens survive password change? Currently: no (revoke all).
  This is a product decision, not a technical one.
```

**Step 6: Fires callback via Clawvisor (symmetric path)**

Callback flows through the same security layer as dispatch:
```
Dispatch:  Wintermute → Clawvisor → Daemon → Claude Code
Callback:  Claude Code → Daemon → Clawvisor → Wintermute webhook
```

The daemon POSTs the completion report to the Clawvisor callback URL, which
relays to Wintermute's OpenClaw webhook endpoint. No side-channel
`openclaw system event`. Everything audited both directions.

### 6. Session Handoff (Cross-Runtime Context Transfer)

"I was working on X in Claude Code, continue in OpenClaw" (and vice versa).

**Handoff file format:**
```markdown
---
from: gstack
to: wintermute
project: baku
branch: garrytan/auth-flow
timestamp: 2026-04-03T14:30:00Z
---

## Context
Working on JWT auth flow. Got stuck on refresh token rotation test.

## State
- Branch has 2 commits: schema migration + middleware skeleton
- Tests written but failing on token expiry edge case
- Design doc at ~/.gstack/projects/baku/plans/auth-design.md

## What I need
Debug the refresh token rotation test failure and fix it.

## Resume prompt
Load gstack. Continue work on branch garrytan/auth-flow in ~/git/baku.
Two commits landed (schema + middleware). The refresh token rotation
test is failing on the expiry edge case. Read the test at
test/auth/refresh-rotation.test.ts:47. The expected behavior is that
a rotated refresh token invalidates the old one on first use.
```

The `resume_prompt` field is critical: gstack has full context at checkpoint
time; Wintermute doesn't. When the user says "continue the Baku auth work,"
Wintermute passes the resume prompt straight into the next Claude Code session.
Zero context reconstruction.

Written to `~/.gstack/handoff/{id}.md`. Wintermute reads it. Context transfers
without re-explaining. Extends the existing `/checkpoint` skill.

### 7. Clawvisor Integration (Security Gateway)

Clawvisor (clawhub.ai/ericlevine/clawvisor) sits between Wintermute and your Mac.
It provides credential vaulting, task-scoped authorization, and human approval
flows. The agent never directly handles secrets.

**Why Clawvisor, not raw SSH/ngrok:**

| Raw tunnel                          | Clawvisor                                   |
|-------------------------------------|---------------------------------------------|
| Full SSH access to Mac              | Task-scoped authorization per action         |
| No audit trail                      | Every request has `reason` + `data_origin`   |
| One compromise = full access        | Token is service-scoped, revokable           |
| No human-in-the-loop                | Approval required (or auto for trusted scope)|
| Prompt injection → arbitrary cmds   | Chain context verification blocks injection  |
| All or nothing                      | Scope expansion requires re-approval         |

**Clawvisor service definition for gstack:**

```
Service: gstack-coding
Actions:
  spawn-session     Start Claude Code + gstack in a project dir
  check-status      Is the session still running?
  get-completion    Fetch the completion report
  cancel-session    Kill a running session
  list-sessions     What's running + queue depth + max concurrent
```

The `list-sessions` response includes `queue_depth` and `max_concurrent` so
Wintermute can make intelligent dispatch decisions before sending work:

```json
{
  "active": 2,
  "max_concurrent": 2,
  "queued": 1,
  "sessions": [
    { "id": "dispatch-auth-flow", "project": "baku", "elapsed": 423 },
    { "id": "dispatch-fix-ci", "project": "gstack", "elapsed": 87 }
  ]
}
```

When a dispatch arrives and active sessions are at `max_concurrent`, the daemon
queues it (FIFO). Wintermute sees `queued: 1` in `list-sessions` and can decide
whether to wait or cancel a lower-priority session.

**Authorization flow:**

1. Wintermute creates a Clawvisor task declaring scope:
   `spawn-session` in `~/git/baku`, read/write in that dir, run tests, create PR
2. Clawvisor checks restrictions (hard blocks on rm -rf /, force-push main, etc.)
3. You get a notification: "Wintermute wants to code in Baku. Approve?"
   (or auto-approved if standing task exists for this repo)
4. On approval, dispatch-daemon spawns the session
5. Every action audited with `reason` and `data_origin`
6. On completion, `POST /api/tasks/{id}/complete`

**Standing tasks for trusted workflows:**

```yaml
Standing Task: "gstack-trusted-repos"
  scope: [spawn-session, check-status, get-completion]
  repos: [baku, gstack, foundation]
  restrictions: [no-main-push, no-credential-read, project-dir-only]
  auto_execute: true   # no approval ping needed
  session_id: required # chain context per invocation
```

Wintermute can spawn gstack sessions in approved repos without pinging you.
New repos or destructive actions still require approval.

**Restriction templates (shipped with gstack):**

```yaml
restrictions:
  - block: exec
    pattern: "rm -rf /"
    reason: "never delete root"
  - block: exec
    pattern: "git push --force origin main"
    reason: "no force-push to main"
  - block: read
    pattern: "~/.ssh/*"
    reason: "no credential access"
  - block: write
    pattern: "*/node_modules/*"
    reason: "no writing to dependencies"
```

**Tunnel setup (ngrok or Tailscale):**

```bash
# Option A: ngrok (easy, public URL)
ngrok http $CLAWVISOR_PORT --authtoken $NGROK_TOKEN \
  --domain your-stable-domain.ngrok.app

# Option B: Tailscale (better for always-on, private)
tailscale serve --bg $CLAWVISOR_PORT
```

Wintermute's `CLAWVISOR_URL` points to the stable domain.
Authenticated via `CLAWVISOR_AGENT_TOKEN` (minimally scoped).

### 8. gstack-dispatch-daemon

A lightweight Bun process running on your Mac:

```
bin/gstack-dispatch-daemon

Responsibilities:
  - Watches ~/.gstack/dispatch/ for new task files
  - Validates dispatch came through Clawvisor (token check)
  - Spawns `claude --print` with gstack loaded
  - Captures stdout, tracks elapsed time, detects hangs
  - Writes structured completion report
  - Fires callback to Wintermute via Clawvisor
  - Manages concurrency (configurable, default: 2 parallel sessions)
  - Kills sessions that exceed TTL
```

### 9. Cross-Runtime Diarization (Activity Index)

gstack already produces artifacts that survive on disk: plans, reviews, ship
reports, retros, learnings. The missing piece: a unified activity index that
Wintermute can scan.

```jsonl
// ~/.gstack/activity/activity-2026-W14.jsonl
{"ts":"2026-04-03T14:30:00Z","project":"baku","skill":"ship","artifacts":["pr:47"],"duration":847,"dispatch":"wintermute"}
{"ts":"2026-04-03T12:15:00Z","project":"gstack","skill":"review","artifacts":["review-log.jsonl"],"duration":423}
{"ts":"2026-04-02T16:00:00Z","project":"baku","skill":"investigate","artifacts":["learnings:3"],"duration":612,"dispatch":"wintermute"}
```

**Rotation strategy:** Weekly rollup files (`activity-YYYY-WNN.jsonl`) instead of
a single append-only file. Wintermute answering "what did I ship this week" reads
one file, not 6 months of history. The preamble writes to the current week's file;
old weeks are immutable. A simple `ls ~/.gstack/activity/` gives the full timeline.
Project-specific queries grep across weeks — still fast since each file is small.

### 10. ClawHub Publishing

Package all OpenClaw-variant skills for ClawHub marketplace:

- Versioning synced to gstack's `VERSION` file
- Security metadata: `requires.bins` (gh, git), no env vars by default
- Meta-package: `clawhub install garrytan/gstack` pulls all skills
- CI pipeline: on release tag, auto-publish to ClawHub
- SOUL.md included in the package

This puts gstack in front of OpenClaw's 247K-star user base through their native
package manager.

### 11. Proactive Skill Suggestion Across Runtimes

Wintermute sees "Baku coding session" on calendar → pre-loads context:

1. Reads `~/.gstack/activity.jsonl` for last Baku session
2. Reads `~/.gstack/projects/baku/learnings.jsonl` for project context
3. Checks routing table for Baku-specific skill recommendations
4. Pre-creates dispatch file with context
5. When you say "going to code" → suggests: "Last session was debugging auth.
   Want me to dispatch gstack with the checkpoint from yesterday?"

This is orchestration logic on the OpenClaw side. gstack's role is producing the
artifacts that make it possible (which it already does).

### 12. OpenClaw Integration Skill (gstack-bridge)

An actual SKILL.md that OpenClaw instances install — teaches any OpenClaw agent
how to work with gstack. This is the OpenClaw-side counterpart to the gstack
dispatch-aware preamble.

```yaml
---
name: gstack-bridge
description: >
  Bridge between OpenClaw and gstack (Claude Code). Dispatch coding tasks,
  read completion reports, parse handoffs, query activity timelines, and
  manage shared learnings. Install this to make your OpenClaw agent
  gstack-aware.
version: 0.1.0
triggers:
  - dispatch coding task
  - what did I ship
  - continue the coding work
  - gstack status
metadata:
  openclaw:
    requires:
      bins: [claude, gh, git]
      env: [CLAWVISOR_URL, CLAWVISOR_AGENT_TOKEN]
---
```

**What the skill teaches OpenClaw:**

1. **Dispatch protocol** — how to create dispatch files, authorize via Clawvisor,
   and spawn Claude Code sessions
2. **Completion parsing** — how to read YAML frontmatter + markdown completion
   reports and integrate into memory
3. **Handoff reading** — how to parse handoff files and use `resume_prompt` to
   continue work in a new Claude Code session
4. **Activity queries** — how to read `~/.gstack/activity.jsonl` and answer
   "what did I ship this week" across both runtimes
5. **Learnings sync** — how to read gstack's JSONL learnings and incorporate
   them into OpenClaw memory
6. **Standing task management** — how to configure trusted repos for
   auto-approved dispatch

This skill ships to ClawHub alongside all the other gstack skills. Any OpenClaw
user who installs gstack's skill pack gets the bridge automatically.

### 13. JSON Schema Definitions (Shared Contract)

All shared file formats have formal JSON Schema definitions to prevent silent
breakage when either side evolves.

**`schemas/dispatch.schema.json`**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["id", "dispatched_by", "task", "project", "project_dir"],
  "properties": {
    "id": { "type": "string", "pattern": "^dispatch-" },
    "dispatched_by": { "type": "string" },
    "task": { "type": "string", "minLength": 1 },
    "project": { "type": "string" },
    "project_dir": { "type": "string" },
    "learnings": { "type": "array", "items": { "type": "string" } },
    "constraints": { "type": "array", "items": { "type": "string" } },
    "callback_url": { "type": "string", "format": "uri" },
    "clawvisor_task_id": { "type": "string" },
    "ttl_seconds": { "type": "integer", "minimum": 60, "maximum": 86400 }
  }
}
```

**`schemas/completion.schema.json`**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["dispatch_id", "status", "duration"],
  "properties": {
    "dispatch_id": { "type": "string", "pattern": "^dispatch-" },
    "status": { "enum": ["completed", "failed", "cancelled", "timeout"] },
    "duration": { "type": "integer", "description": "seconds" },
    "commits": { "type": "integer" },
    "pr": { "type": "string", "description": "owner/repo#number format" },
    "error": { "type": "string", "description": "present only on failure" }
  }
}
```

**`schemas/handoff.schema.json`**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["from", "to", "project", "timestamp"],
  "properties": {
    "from": { "enum": ["gstack", "wintermute"] },
    "to": { "enum": ["gstack", "wintermute"] },
    "project": { "type": "string" },
    "branch": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "resume_prompt": { "type": "string", "description": "exact prompt to resume session" }
  }
}
```

**`schemas/activity-entry.schema.json`**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["ts", "project", "skill", "duration"],
  "properties": {
    "ts": { "type": "string", "format": "date-time" },
    "project": { "type": "string" },
    "skill": { "type": "string" },
    "artifacts": { "type": "array", "items": { "type": "string" } },
    "duration": { "type": "integer", "description": "seconds" },
    "dispatch": { "type": "string", "description": "who dispatched, if any" }
  }
}
```

Schemas live in `schemas/` at the repo root. Both the gstack dispatch daemon and
the OpenClaw bridge skill validate against them. Schema version is tied to gstack
VERSION — breaking changes require a major version bump.

### 14. Version Compatibility

OpenClaw-variant skills carry `min_openclaw_version` in frontmatter:

```yaml
---
name: gstack-ship
version: 0.15.2.0
min_openclaw_version: "1.8.0"
---
```

OpenClaw's skill loader checks this and warns if the runtime is too old.
Prevents "why isn't this working" support issues on ClawHub.

The gstack-bridge skill additionally carries `min_gstack_version` to ensure
the dispatch daemon and file formats are compatible:

```yaml
min_gstack_version: "0.16.0.0"
```

## Resolved Decisions

1. **Browse binary on OpenClaw:** Ship standalone, invoke via `exec $B`. Don't
   adapter it. The browse binary's capabilities (snapshot diffing, chain commands,
   cookie import, annotated screenshots) are years ahead of OpenClaw's native
   browser. Wrapping it would lose features.

2. **Multi-agent orchestration:** Ship and measure. OpenClaw's `sessions_spawn`
   doesn't share prompt cache like Claude Code's Agent tool, so sub-agents will
   be slower and more expensive. Worth shipping and measuring the cost delta
   rather than deferring.

3. **Concurrency on dispatch:** Default 2 parallel sessions. Bottleneck is
   Anthropic rate limits, not local compute. Configurable in
   `~/.gstack/config.yaml` via `dispatch.max_concurrent`.

4. **Standing task scope:** `trusted_repos` list in `~/.gstack/config.yaml`.
   Start with personal repos (`garrytan/*` auto-approves). Org repos or other
   people's repos require per-dispatch approval.

5. **PR #491 disposition:** Close it. Generator-native approach replaces the
   entire subtree. Credit @latifclawbot-mdil for tool mapping research in
   CHANGELOG.

## Implementation Plan

### Phase 1: Generator + ClawHub (distribution)
- OpenClaw resolver in `gen-skill-docs.ts`
- Add OpenClaw frontmatter to all skill templates (including `min_openclaw_version`)
- SOUL.md
- ClawHub publishing pipeline
- **Result:** gstack skills installable on OpenClaw via `clawhub install`

### Phase 2: Shared Layer (memory bridge)
- JSON Schema definitions for all shared file formats
- Bidirectional learnings adapter
- Activity index (session diarization)
- Shared routing config
- Extend `/checkpoint` for cross-runtime handoff (with `resume_prompt`)
- **Result:** both runtimes share memory and context with validated contracts

### Phase 3: Remote Dispatch (Wintermute → gstack)
- Dispatch file format + protocol (validated against schema)
- Dispatch-aware preamble
- gstack-dispatch-daemon (symmetric Clawvisor callback path)
- Clawvisor service adapter + restriction templates
- ngrok/Tailscale tunnel setup
- gstack-bridge skill for OpenClaw (teaches Wintermute the full protocol)
- **Result:** Wintermute can autonomously dispatch coding sessions

## Effort Estimate

| Component                                         | Time    |
|---------------------------------------------------|---------|
| OpenClaw resolver in gen-skill-docs               | 30 min  |
| SOUL.md + AGENTS.md template                      | 15 min  |
| ClawHub CI publishing pipeline                    | 30 min  |
| JSON Schema definitions (4 schemas)               | 30 min  |
| Bidirectional learnings adapter                   | 30 min  |
| Activity index                                    | 15 min  |
| Shared routing config                             | 30 min  |
| Dispatch protocol + file format                   | 30 min  |
| Dispatch-aware preamble                           | 30 min  |
| gstack-dispatch-daemon (with symmetric callback)  | 1 hour  |
| Clawvisor service adapter + restrictions          | 45 min  |
| ngrok/Tailscale setup integration                 | 15 min  |
| gstack-bridge skill for OpenClaw                  | 45 min  |
| **Total**                                         | **~7h** |

## Resolved Decisions (from Wintermute review)

6. **Offline Mac:** Fail fast, let Wintermute decide retry strategy. No
   Clawvisor queuing (keeps the security layer stateless). No iCloud/Dropbox
   sync (conflict resolution nightmare). But Clawvisor error responses MUST
   distinguish failure modes so Wintermute can retry intelligently:
   - `mac_asleep` — tunnel unreachable, retry when Mac wakes
   - `tunnel_down` — ngrok/Tailscale not running, user action needed
   - `daemon_crashed` — dispatch daemon not responding, restart needed
   - `queue_full` — all slots occupied, check `list-sessions` for ETAs

7. **Schema evolution:** Additive-only for minor versions, strict semver for
   breaking. **Breaking change defined as:** removing a required field,
   changing a field's type, or changing the semantics of an existing field.
   **Non-breaking:** adding optional fields. This definition goes in a
   `COMPATIBILITY.md` at the repo root so future contributors don't guess
   under pressure.

8. **Activity index rotation:** Weekly rollup files
   (`activity-YYYY-WNN.jsonl`) instead of single append-only file. See
   section 9 for details.

9. **Dispatch queueing:** When active sessions are at `max_concurrent`, the
   daemon queues incoming dispatches (FIFO). `list-sessions` returns
   `queue_depth` so Wintermute can decide whether to wait or cancel a
   lower-priority session. See section 7 for the response format.

10. **Multiple OpenClaw agents:** Don't over-engineer. The `dispatched_by`
    field already handles identity. If multi-agent becomes real, add
    per-agent config sections in `~/.gstack/config.yaml`. Flag it, move on.
