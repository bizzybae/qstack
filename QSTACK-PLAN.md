# qstack — Perplexity Computer Adaptation Plan

> Adapted from [garrytan/gstack](https://github.com/garrytan/gstack) (MIT License).
> gstack turns Claude Code into a virtual engineering team. **qstack** does the same for **Perplexity Computer** — a cloud-based AI agent platform running in the browser.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Platform Comparison](#platform-comparison)
3. [Compatibility Matrix](#compatibility-matrix)
4. [Architecture Translation](#architecture-translation)
5. [Skill Conversion Strategy](#skill-conversion-strategy)
6. [Reorganized Skill Tiers](#reorganized-skill-tiers)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Remote MCP Server Strategy](#remote-mcp-server-strategy)
9. [File Structure](#file-structure)

---

## Executive Summary

gstack was built for **Claude Code on Desktop** — a terminal-based AI coding agent with access to the local filesystem, a persistent headless Chromium daemon, compiled Bun binaries, and deep macOS/Linux integration. It uses bash preambles, local state files (`~/.gstack/`), and Playwright browser automation.

Perplexity Computer is a **cloud-based, browser-first AI agent platform**. Every task runs in an isolated compute sandbox (Linux VM with 2 vCPUs, 8 GB RAM, ~20 GB disk). It has:

- A real filesystem at `/home/user/workspace`
- A real browser (via `browser_task`, `screenshot_page`, `js_repl` with Playwright)
- Bash execution (via `bash` tool)
- File I/O (via `read`, `write`, `edit`, `grep`, `glob` tools)
- Web search and URL fetching (via `search_web`, `fetch_url`)
- Sub-agents (via `run_subagent` — research, codebase, asset, website, general purpose)
- 400+ app connectors (Gmail, Slack, Notion, GitHub, Google Calendar, etc.)
- Custom skills (uploaded as `SKILL.md` or `.zip` with `SKILL.md` at root)
- Memory across sessions (via `memory_search`, `memory_update`)
- Scheduled tasks and cron jobs
- Website deployment (via `deploy_website`)
- File sharing (via `share_file`)

**The core insight:** ~60% of gstack's value is in its **methodology and prompt engineering** (the SKILL.md instruction text), which ports directly. ~30% is in **tooling integration** that needs remapping to Perplexity's tool surface. ~10% is **desktop-specific** features (browser daemon, compiled binaries, cookie import, Chrome extension) that need rethinking or dropping.

---

## Platform Comparison

| Dimension | gstack (Claude Code) | qstack (Perplexity Computer) |
|-----------|---------------------|------------------------------|
| **Runtime** | Local terminal (macOS/Linux/WSL) | Cloud sandbox (Linux VM) |
| **Filesystem** | Full local FS (`~/`, project dir) | Isolated `/home/user/workspace` |
| **Browser** | Persistent headless Chromium daemon via Playwright, localhost HTTP, CDP | `browser_task` (cloud Chromium), `js_repl` (Playwright), `screenshot_page`, or local Comet browser |
| **Sub-agents** | Claude `Agent` tool (child process) | `run_subagent` (typed: research, codebase, asset, website, general_purpose) |
| **Git access** | Direct `git` + `gh` CLI | `gh` CLI via `bash` with `api_credentials=["github"]` |
| **Skill format** | `SKILL.md` with YAML frontmatter, `allowed-tools` field, bash preamble blocks | `SKILL.md` with YAML frontmatter (`name`, `description`), max 10 MB, uploaded via UI or created conversationally |
| **Skill activation** | Slash commands (`/review`, `/ship`) | Auto-activated by description matching, or loaded via `load_skill` |
| **Persistent state** | `~/.gstack/` directory tree, `.gstack/browse.json`, learnings JSONL | Perplexity `memory_update`/`memory_search` for cross-session; workspace files for in-session |
| **App integrations** | MCP servers (configured in Claude Desktop config) | 400+ built-in connectors + custom remote MCP connectors (HTTPS, SSE/Streamable HTTP) |
| **Code execution** | Direct terminal (bash, bun, node, python) | `bash` tool (sandboxed), `js_repl` (persistent Node.js REPL) |
| **File output** | Written to local FS, user opens locally | `share_file` to send to user, `deploy_website` for sites |
| **Scheduling** | Not native (use cron externally) | Built-in `schedule_cron` for recurring tasks |
| **Memory** | `.gstack/projects/<slug>/learnings.jsonl` | `memory_update` / `memory_search` — platform-native, cross-session |

---

## Compatibility Matrix

### Skills That Port Directly (Methodology-Heavy, Minimal Tooling)

These skills are 90%+ prompt/methodology. Convert by removing the bash preamble, adapting `allowed-tools` references, and adjusting file paths.

| gstack Skill | Lines | Portable? | Adaptation Notes |
|-------------|-------|-----------|-----------------|
| `/office-hours` | 1,674 | **Direct** | Core methodology (6 forcing questions, design doc output) is pure prompt. Remove preamble bash. Replace `Write` → workspace files. Replace `Agent` sub-agent → `run_subagent`. |
| `/plan-ceo-review` | 1,797 | **Direct** | CEO review methodology is prompt-only. Remove preamble. Adjust `CLAUDE.md` references → custom instructions. |
| `/plan-eng-review` | 1,391 | **Direct** | Architecture review, ASCII diagrams, test matrices — all prompt. |
| `/plan-design-review` | 1,489 | **Direct** | Design dimension scoring, AI slop detection — all prompt. `AskUserQuestion` maps to `ask_user_question`. |
| `/plan-devex-review` | 1,793 | **Direct** | DX review with personas, TTHW benchmarks — all prompt. |
| `/investigate` | 735 | **Direct** | Root-cause debugging methodology. Remove freeze integration. |
| `/retro` | 1,427 | **Mostly** | Git-based retrospective. `gh` CLI works in sandbox. Remove multi-session tracking (use memory instead). |
| `/document-release` | 885 | **Direct** | Doc update methodology. Works with any repo cloned into workspace. |
| `/cso` | 1,185 | **Direct** | OWASP + STRIDE methodology is prompt-only. |
| `/design-consultation` | 1,225 | **Mostly** | Design system creation. Replace `Agent` → `run_subagent`. Replace browse commands → `browser_task`/`screenshot_page`. |
| `/design-html` | 1,140 | **Mostly** | HTML generation methodology. Pretext vendor JS included. Replace browse preview → `deploy_website` or `screenshot_page`. |
| `/careful` | 59 | **Direct** | Safety guardrails — pure prompt instructions. |
| `/freeze` / `/unfreeze` / `/guard` | 40-82 | **Direct** | Edit restrictions — pure prompt instructions. |
| `ETHOS.md` | ~100 | **Direct** | Builder philosophy. Universal. |

### Skills That Need Significant Rework (Tool-Dependent)

| gstack Skill | Lines | Issue | Adaptation Strategy |
|-------------|-------|-------|-------------------|
| `/review` | 1,427 | Reads git diff, auto-fixes code, runs tests — works via `bash` with `gh` CLI. Sub-agent usage (`Agent`) → `run_subagent`. | Remap tool references. Clone repo in sandbox, use `gh` CLI. |
| `/ship` | 2,503 | Largest skill. Git sync, test run, PR creation — all works via `bash`+`gh`. References CLAUDE.md routing. | Remap. PR creation via `gh pr create` works. Remove CLAUDE.md routing references. |
| `/qa` | 1,379 | Uses gstack browse daemon (`$B` commands). Core QA methodology portable, but browser interaction needs full remap. | Replace `$B snapshot`, `$B goto`, `$B click` → `browser_task` or `js_repl` Playwright commands. |
| `/qa-only` | 969 | Same browse dependency as `/qa`. | Same remap as `/qa`. |
| `/browse` | 704 | **Entire skill is the gstack browser daemon.** This is the core infrastructure, not a methodology skill. | **Replace entirely** with instructions for using `browser_task`, `screenshot_page`, `js_repl` (Playwright), and Comet local browser. |
| `/autoplan` | 1,424 | Orchestrates CEO → design → eng reviews in sequence using `Agent`. | Replace `Agent` chaining → `run_subagent` chaining or sequential skill loads. |
| `/benchmark` | 633 | Uses browse daemon for page load timing + Core Web Vitals. | Replace with `js_repl` Playwright performance API, or `browser_task` with Lighthouse. |
| `/canary` | 766 | Post-deploy monitoring loop using browse daemon. | Replace with `schedule_cron` + `browser_task` for periodic checks. |
| `/design-review` | 1,556 | Design audit + fix loop. Uses browse for screenshots. | Replace browse → `screenshot_page`. Code editing works natively. |
| `/design-shotgun` | 914 | Generates design variants, opens comparison board in browser. | Replace with `deploy_website` for comparison board, or `share_file` for screenshots. |
| `/land-and-deploy` | 1,546 | Merge PR, wait for CI, verify production. Uses `gh` CLI + browse. | `gh` CLI works. Replace browse health check → `browser_task` or `fetch_url`. |
| `/codex` | 1,035 | Invokes OpenAI Codex CLI for second opinion. | **Drop or remap** — Perplexity already orchestrates multiple models (Opus 4.6, Gemini, GPT-5.2, Grok). Could replace with `run_subagent` using different model parameter. |
| `/retro` | 1,427 | Git log analysis. `gh` works. `/retro global` scans multiple tool histories. | `gh` works. Drop global multi-tool scan (Codex, Gemini logs are local-only). |

### Skills to Drop or Defer (Desktop-Specific)

| gstack Skill | Reason |
|-------------|--------|
| `/open-gstack-browser` | Launches headed Chromium with extension + sidebar. Desktop-only. |
| `/setup-browser-cookies` | Imports cookies from Chrome/Arc/Brave/Edge. Desktop-only. (Comet browser has its own session management.) |
| `/connect-chrome` | Chrome DevTools Protocol connection. Desktop-only. |
| `/gstack-upgrade` | Self-updater via git pull. Not applicable — skills are managed in Perplexity's skill UI. |
| `/setup-deploy` | One-time deploy platform detection. Can be simplified to a memory-based config. |
| `/learn` | Local learnings JSONL. **Replace with `memory_update`/`memory_search`** — Perplexity's native memory is better (cross-session, searchable, no file management). |
| `/checkpoint` | Git checkpoint/restore. Relies on local git worktrees. |
| `/health` | gstack installation health dashboard. Not applicable. |
| OpenClaw skills | OpenClaw-specific dispatch. Not applicable. |

---

## Architecture Translation

### gstack Architecture (Desktop)

```
User Terminal
    ↓
Claude Code (local process)
    ↓ slash command
SKILL.md loaded → bash preamble runs → methodology executes
    ↓ tool calls
Bash (local) / Read / Write / Edit / Grep / Glob
    ↓ browse commands
gstack daemon (localhost HTTP → Chromium via CDP)
    ↓ sub-agents
Agent tool (child Claude process)
    ↓ state
~/.gstack/ (config, learnings, sessions, analytics)
```

### qstack Architecture (Cloud/Browser)

```
Perplexity Computer (browser UI)
    ↓ skill auto-activated by description match
SKILL.md loaded → methodology executes
    ↓ tool calls
bash (sandboxed VM) / read / write / edit / grep / glob
    ↓ browser interaction
browser_task (cloud Chromium) / js_repl (Playwright) / screenshot_page
    ↓ sub-agents
run_subagent (typed: research, codebase, asset, website, general_purpose)
    ↓ state
memory_update / memory_search (platform-native, cross-session)
    ↓ integrations
400+ connectors (GitHub, Slack, Gmail, Notion, etc.) + custom remote MCP
    ↓ output
share_file / deploy_website / submit_answer
```

### Key Translation Rules

| gstack Pattern | qstack Equivalent |
|---------------|------------------|
| `allowed-tools: [Bash, Read, Write, ...]` | Remove — Perplexity Computer uses all tools automatically |
| Bash preamble (gstack-update-check, sessions, telemetry, learnings) | **Remove entirely.** Replace learnings with `memory_search`/`memory_update` instructions in the skill body. |
| `~/.claude/skills/gstack/` paths | Not applicable — skills are standalone `.md` or `.zip` uploads |
| `CLAUDE.md` references | Replace with "custom instructions" or "project context" references |
| `$B goto https://...` (browse daemon) | `browser_task(url="https://...", task="Navigate and extract...")` |
| `$B snapshot -i` | `screenshot_page(url="https://...")` |
| `$B click [selector]` | `browser_task(task="Click on [element]...")` or `js_repl` Playwright |
| `Agent` sub-agent tool | `run_subagent(subagent_type="general_purpose", ...)` |
| `AskUserQuestion` | `ask_user_question` (same concept, slightly different format) |
| `WebSearch` | `search_web` / `fetch_url` / `search_vertical` |
| `gstack-config get [key]` | `memory_search(queries=["qstack config: [key]"])` |
| `gstack-learnings-search` | `memory_search(queries=["project learnings for..."])` |
| `gstack-learnings-log` | `memory_update(content="Remember: [learning]")` |
| `gstack-telemetry-log` | Drop — no telemetry needed |
| `gstack-timeline-log` | Drop — Perplexity has its own activity timeline |
| `gstack-review-log` | `memory_update(content="Remember: review of [branch] found...")` |
| `gstack-slug` (project identifier) | Derive from repo name in workspace, or ask user |
| `git diff` for review | `bash` with `git diff` works in sandbox (repo must be cloned first) |
| `gh pr create` | `bash` with `gh pr create` and `api_credentials=["github"]` |
| `Conductor` (parallel sessions) | Perplexity already supports parallel `run_subagent` calls |
| Design comparison board (local HTML) | `deploy_website` to host comparison, or `share_file` screenshots |

---

## Skill Conversion Strategy

### SKILL.md Format for Perplexity Computer

Perplexity skills use a simpler format than gstack:

```yaml
---
name: skill-name-here
description: |
  One paragraph describing what this skill does and when to activate it.
  Include trigger phrases: "Use when the user asks to...", "Activate when..."
  The description is critical — Perplexity uses it to decide when to auto-activate.
---

# Skill Name

## Instructions

[Methodology content — the actual value from gstack]

## Workflow

[Step-by-step process]

## Output Format

[What to produce]
```

**Key differences from gstack SKILL.md:**
- No `allowed-tools` field (Perplexity auto-manages tools)
- No `preamble-tier` field
- No `version` field
- No bash preamble blocks
- Description must be rich with trigger phrases for auto-activation
- Name must be lowercase with hyphens, 1-64 chars
- Max file size 10 MB (no issue — largest gstack skill is ~2,500 lines ≈ ~80 KB)

### Conversion Template

For each gstack skill → qstack skill:

1. **Extract the methodology** — everything between the preamble and the tooling-specific sections
2. **Rewrite the description** — add Perplexity-style trigger phrases
3. **Replace tool references:**
   - `Bash` tool calls → `bash` tool (note: use `api_credentials=["github"]` for git/gh commands)
   - `$B [command]` browse calls → `browser_task` / `js_repl` / `screenshot_page` instructions
   - `Agent` calls → `run_subagent` instructions with appropriate `subagent_type`
   - `AskUserQuestion` → `ask_user_question`
   - File reads referencing `~/.claude/skills/gstack/[skill]/SKILL.md` → inline the relevant content or reference "load the [skill-name] skill"
4. **Replace state management:**
   - Learnings → `memory_update` / `memory_search`
   - Config → `memory_search` for preferences
   - Session tracking → drop (Perplexity handles this)
5. **Remove all preamble bash blocks**
6. **Remove gstack-specific infrastructure** (update checks, telemetry, session files, slug generation)
7. **Add qstack branding** and attribution

---

## Reorganized Skill Tiers

### Tier 1 — Foundation (Convert First)

These deliver immediate value with minimal adaptation:

| qstack Skill | From gstack | Priority | Effort |
|-------------|-------------|----------|--------|
| `office-hours` | `/office-hours` | P0 | Low — prompt rewrite only |
| `ceo-review` | `/plan-ceo-review` | P0 | Low |
| `eng-review` | `/plan-eng-review` | P0 | Low |
| `design-review-plan` | `/plan-design-review` | P0 | Low |
| `code-review` | `/review` | P0 | Medium — remap git tooling |
| `security-audit` | `/cso` | P0 | Low |
| `investigate` | `/investigate` | P0 | Low |
| `ethos` | `ETHOS.md` | P0 | Embed as reference in all skills |

### Tier 2 — Shipping Workflow

| qstack Skill | From gstack | Priority | Effort |
|-------------|-------------|----------|--------|
| `ship-pr` | `/ship` | P1 | Medium — largest skill, remap PR workflow |
| `qa-test` | `/qa` | P1 | High — full browse remap to browser_task |
| `qa-report` | `/qa-only` | P1 | High — same browse remap |
| `retro` | `/retro` | P1 | Medium — git analysis works, drop multi-tool |
| `doc-release` | `/document-release` | P1 | Low |
| `autoplan` | `/autoplan` | P1 | Medium — remap Agent chaining |

### Tier 3 — Design System

| qstack Skill | From gstack | Priority | Effort |
|-------------|-------------|----------|--------|
| `design-consult` | `/design-consultation` | P2 | Medium |
| `design-html` | `/design-html` | P2 | Medium — include Pretext vendor JS |
| `design-audit` | `/design-review` | P2 | Medium |
| `design-explore` | `/design-shotgun` | P2 | Medium |
| `devex-review` | `/plan-devex-review` + `/devex-review` | P2 | Low-Medium |

### Tier 4 — DevOps & Monitoring

| qstack Skill | From gstack | Priority | Effort |
|-------------|-------------|----------|--------|
| `deploy` | `/land-and-deploy` | P3 | Medium — gh CLI + browser_task |
| `canary-monitor` | `/canary` | P3 | Medium — use schedule_cron |
| `benchmark` | `/benchmark` | P3 | Medium — js_repl Playwright perf |

### Tier 5 — Utilities (Adapt or New)

| qstack Skill | From gstack | Priority | Effort |
|-------------|-------------|----------|--------|
| `safety-guard` | `/careful` + `/freeze` + `/guard` + `/unfreeze` | P3 | Low |
| `browse-guide` | `/browse` (rewritten) | P1 | Medium — new skill teaching Perplexity's browser tools |

### New Skills (Perplexity-Native)

| qstack Skill | Description | Priority |
|-------------|-------------|----------|
| `connector-setup` | Guide for connecting GitHub, Slack, Notion, etc. via Perplexity's connector system | P1 |
| `mcp-bridge` | Instructions for setting up custom remote MCP servers to extend qstack | P2 |
| `scheduled-ops` | Patterns for using `schedule_cron` for monitoring, reporting, automated checks | P2 |
| `parallel-sprint` | Guide for running multiple `run_subagent` in parallel (Perplexity's version of Conductor) | P2 |

---

## Implementation Roadmap

### Phase 1 — Foundation (Week 1-2)

1. **Create the qstack README.md** — rewritten for Perplexity Computer audience
2. **Convert Tier 1 skills** (office-hours, ceo-review, eng-review, design-review-plan, code-review, security-audit, investigate)
3. **Create `browse-guide`** — new skill teaching Perplexity's browser capabilities
4. **Create `QSTACK-ETHOS.md`** — adapted builder philosophy
5. **Test each skill** by uploading to Perplexity Computer and running through example workflows
6. **Package as `.zip`** with all Tier 1 skills for easy upload

### Phase 2 — Shipping Pipeline (Week 3-4)

1. **Convert Tier 2 skills** (ship-pr, qa-test, qa-report, retro, doc-release, autoplan)
2. **Build the QA skill** — most complex adaptation (gstack browse → browser_task/js_repl)
3. **Build the ship-pr skill** — PR workflow via gh CLI in sandbox
4. **Create `connector-setup` guide skill**
5. **Test end-to-end workflow**: office-hours → ceo-review → eng-review → implement → code-review → qa → ship

### Phase 3 — Design & DevOps (Week 5-6)

1. **Convert Tier 3 skills** (design system)
2. **Convert Tier 4 skills** (deploy, canary, benchmark)
3. **Create `scheduled-ops`** and **`parallel-sprint`** skills
4. **Build the MCP bridge** documentation and example server

### Phase 4 — Polish & Package (Week 7-8)

1. **Create master installer skill** — a meta-skill that helps users install all qstack skills
2. **Write the qstack ARCHITECTURE.md** — adapted for Perplexity Computer
3. **Create video/documentation** for onboarding
4. **Publish to community** (optional — share on r/perplexity_ai, agentskills.io)

---

## Remote MCP Server Strategy

### Why a Custom Remote MCP Server?

Perplexity Computer supports [custom remote MCP connectors](https://www.perplexity.ai/help-center/en/articles/13915507-adding-custom-remote-connectors). This enables qstack to expose its own tools as a remote service that Perplexity can call, extending beyond what SKILL.md files alone can do.

### What an MCP Server Could Provide

| MCP Tool | Purpose | gstack Equivalent |
|----------|---------|------------------|
| `qstack_learnings_search` | Project-specific learnings database (richer than Perplexity memory) | `gstack-learnings-search` |
| `qstack_learnings_log` | Store structured learnings with tags, project slugs | `gstack-learnings-log` |
| `qstack_review_log` | Persistent review history across sessions | `gstack-review-log` |
| `qstack_analytics` | Usage dashboard — which skills run, how often, outcomes | `gstack-analytics` |
| `qstack_config` | Persistent configuration (proactive mode, skill prefix, etc.) | `gstack-config` |

### Architecture

```
Perplexity Computer (browser)
    ↓ tool call via MCP
HTTPS (Streamable HTTP or SSE)
    ↓
qstack MCP Server (your remote server)
    ↓
SQLite/PostgreSQL database
    ↓
Learnings, config, analytics, review history
```

### Implementation Options

| Option | Hosting | Complexity | Cost |
|--------|---------|-----------|------|
| **A) Cloudflare Worker + D1** | Serverless, edge | Low | Free tier covers most usage |
| **B) Railway/Render + SQLite** | Managed container | Medium | ~$5/mo |
| **C) Self-hosted on your Ubuntu server** | Full control, Tailscale VPN | Medium | $0 (existing infra) |
| **D) Skip MCP, use Perplexity memory** | No server needed | Lowest | $0 |

**Recommendation:** Start with **Option D** (Perplexity memory only) for Phase 1-2. The platform's built-in `memory_update`/`memory_search` covers 80% of the use case. Graduate to **Option C** (self-hosted) if you need structured learnings with SQL queries, or **Option A** (Cloudflare) for zero-ops.

### MCP Server Setup in Perplexity

1. Build and deploy the MCP server (HTTPS required)
2. In Perplexity: Account Settings → Connectors → + Custom Connector → Remote
3. Configure:
   - Name: "qstack"
   - MCP Server URL: `https://your-server.com/sse` (or `/mcp` for Streamable HTTP)
   - Auth: API Key (simplest) or OAuth 2.0
   - Transport: SSE or Streamable HTTP
4. Perplexity auto-discovers tools from the MCP server
5. Skills can reference: "Use the qstack connector to search learnings about this project"

---

## File Structure

### Current gstack Structure (to be reorganized)

```
qstack/                          # Root (currently mirrors gstack)
├── QSTACK-PLAN.md              # This document
├── README.md                    # To be rewritten
├── ETHOS.md                     # To be adapted
├── ARCHITECTURE.md              # To be rewritten
├── skills/                      # NEW: all converted skills
│   ├── office-hours/
│   │   └── SKILL.md
│   ├── ceo-review/
│   │   └── SKILL.md
│   ├── eng-review/
│   │   └── SKILL.md
│   ├── design-review-plan/
│   │   └── SKILL.md
│   ├── code-review/
│   │   └── SKILL.md
│   ├── security-audit/
│   │   └── SKILL.md
│   ├── investigate/
│   │   └── SKILL.md
│   ├── ship-pr/
│   │   └── SKILL.md
│   ├── qa-test/
│   │   └── SKILL.md
│   ├── ...
│   └── browse-guide/
│       └── SKILL.md
├── mcp-server/                  # NEW: optional remote MCP server
│   ├── src/
│   ├── package.json
│   └── README.md
├── gstack-original/             # ARCHIVE: original gstack for reference
│   ├── office-hours/
│   ├── plan-ceo-review/
│   ├── review/
│   ├── ship/
│   ├── qa/
│   ├── browse/
│   └── ...
└── docs/
    ├── INSTALLATION.md          # How to upload skills to Perplexity Computer
    ├── WORKFLOW.md              # The sprint: Think → Plan → Build → Review → Test → Ship
    ├── PLATFORM-COMPARISON.md   # gstack vs qstack differences
    └── MCP-SETUP.md             # Remote MCP server setup guide
```

### Packaging for Perplexity Upload

Each skill should be packageable as:

1. **Individual `.md` files** — drag-and-drop upload one skill at a time
2. **Individual `.zip` files** — one skill per zip (SKILL.md at root, plus any reference files)
3. **Bundle `.zip`** — all skills in one zip for bulk upload (SKILL.md files in subdirectories)

---

## Appendix: Perplexity Computer Tool Reference

For skill authors, here are the available tools in Perplexity Computer:

| Tool | Maps to gstack | Notes |
|------|---------------|-------|
| `bash` | `Bash` | Sandboxed Linux VM. Use `api_credentials=["github"]` for gh/git. |
| `read` | `Read` | Read files from workspace |
| `write` | `Write` (file creation) | Create files in workspace |
| `edit` | `Edit` | String replacement in files |
| `grep` | `Grep` | Regex search across files |
| `glob` | `Glob` | File pattern matching |
| `search_web` | `WebSearch` | Web search with multiple parallel queries |
| `fetch_url` | `WebSearch` (URL fetch) | Fetch and optionally extract from URLs |
| `browser_task` | `$B` commands | Cloud or local browser automation |
| `screenshot_page` | `$B snapshot` | Take screenshots of web pages |
| `js_repl` | (no equivalent) | Persistent Playwright Node.js REPL |
| `run_subagent` | `Agent` | Typed sub-agents (research, codebase, asset, website, general_purpose) |
| `ask_user_question` | `AskUserQuestion` | Multi-choice questions to user |
| `share_file` | (no equivalent) | Send files to user |
| `deploy_website` | (no equivalent) | Deploy static sites to S3 |
| `schedule_cron` | (no equivalent) | Recurring scheduled tasks |
| `memory_search` | `gstack-learnings-search` | Search cross-session memory |
| `memory_update` | `gstack-learnings-log` | Store persistent facts |
| `call_external_tool` | MCP server tools | Call connected app APIs |

---

*This plan is a living document. Update as skills are converted and tested.*

*Attribution: qstack is adapted from [gstack](https://github.com/garrytan/gstack) by Garry Tan (MIT License).*
