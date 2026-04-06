# qstack

> A fork of [garrytan/gstack](https://github.com/garrytan/gstack) (MIT License), adapted for **Perplexity Computer**.

gstack turns Claude Code into a virtual engineering team. **qstack does the same for Perplexity Computer** — no terminal, no install, no compiled binaries, no daemon processes. Just upload a skill file and go.

---

## Why Perplexity Computer Instead of Claude Code

gstack is brilliant engineering — 23+ workflow skills that turn an AI agent into a CEO, eng manager, designer, QA lead, security officer, and release engineer. But it was built for Claude Code on Desktop, which means:

| gstack requirement | What that actually means |
|--------------------|------------------------|
| Claude Code CLI | macOS/Linux/WSL terminal app, $20/mo Anthropic subscription |
| Bun v1.0+ runtime | Install Bun, compile binaries, manage `node_modules` |
| Persistent Chromium daemon | Background process, localhost HTTP, Chrome DevTools Protocol |
| `~/.claude/skills/gstack/` | Clone repo into hidden directory, run `./setup`, manage updates |
| Cookie import from Chrome/Arc/Brave | Keychain access, SQLite decryption, per-browser config |
| CLAUDE.md routing | Manual config file in every project repo |
| Conductor for parallelism | Separate tool for running multiple Claude Code sessions |

**Perplexity Computer replaces all of that with a browser tab:**

| qstack equivalent | What that actually means |
|-------------------|------------------------|
| Perplexity Computer | Open perplexity.ai — it runs in your browser, any OS |
| No runtime needed | Cloud sandbox with Python, Node, bash, git, gh CLI pre-installed |
| `browser_task` / `screenshot_page` | Built-in browser automation, no daemon, no process management |
| Skills UI → Upload | Drag-and-drop a `.md` file, skill activates automatically |
| Comet local browser | Uses your existing logged-in sessions — no cookie import needed |
| Auto-activation by description | No config files — skills fire when your prompt matches |
| `run_subagent` | Built-in parallel agents, typed by task (research, code, asset, website) |

**The bottom line:** gstack requires 30 minutes of terminal setup across 4 dependencies, runs only on macOS/Linux, and needs a background Chromium daemon. qstack requires dragging 30 files into a web UI and works from any device with a browser.

### What Perplexity Computer Adds That Claude Code Doesn't Have

| Capability | Details |
|-----------|---------|
| **400+ app connectors** | Gmail, Slack, Notion, GitHub, Google Calendar, Jira, Linear, HubSpot, Salesforce — all pre-built, OAuth in one click |
| **Cross-session memory** | `memory_update` / `memory_search` — the agent remembers your preferences, projects, and patterns across conversations without JSONL files |
| **Scheduled tasks** | `schedule_cron` — run security audits daily, deploy checks hourly, retros weekly. No external cron needed |
| **Website deployment** | `deploy_website` — ship a static site to a public URL in one command |
| **Typed sub-agents** | `run_subagent` with types: `research` (web search), `codebase` (repo work), `asset` (PDF/DOCX/PPTX), `website` (build sites), `general_purpose` |
| **File sharing** | `share_file` — send any generated file (charts, reports, zips) directly to the user |
| **Multi-model access** | Switch between Claude, GPT, Gemini, and Grok within the same conversation |
| **No local state** | Nothing to corrupt, nothing to back up, nothing to lose when you reformat your machine |

---

## The Sprint — Real-World Use Cases

qstack preserves gstack's core philosophy: **Think → Plan → Build → Review → Test → Ship → Reflect**. Each skill feeds into the next. Here's when and how to use each one.

### Think Phase

| Skill | Your Specialist | When to Use | Real-World Example |
|-------|----------------|-------------|-------------------|
| `office-hours` | **YC Office Hours** | You have an idea and want to stress-test it before writing code | "I want to build a daily briefing app for my calendar." → The agent reframes it: "You're not building a briefing app — you're building a personal chief of staff AI." Asks 6 forcing questions about demand reality, status quo, desperation, narrowest wedge, observation, and future-fit. Outputs a design doc. |

**Example conversation:**

```
You:    I want to build a patient intake automation tool for my clinic.
Agent:  [Activates office-hours methodology]
        Let me push back on "intake automation." You described three things:
        insurance verification that takes 20 minutes per patient, forms that
        patients fill out wrong, and no-shows you can't backfill. Those are
        three different products. Which one makes you most desperate?
You:    The insurance verification. It's killing our front desk.
Agent:  Who is doing this today, and what do they actually do for those 20 minutes?
        [... 4 more forcing questions ...]
        RECOMMENDATION: Build the narrowest wedge — a single API call that
        returns eligibility + copay for the top 5 payers (80% of your volume).
        Ship it in 48 hours. The full intake suite is a 3-month project.
        [Saves design doc to workspace]
```

### Plan Phase

| Skill | Your Specialist | When to Use | Real-World Example |
|-------|----------------|-------------|-------------------|
| `plan-ceo-review` | **CEO / Founder** | Challenge scope and ambition — is this thinking big enough? | Review a feature plan in 4 modes: SCOPE EXPANSION (dream big — "what if this replaced the entire workflow?"), SELECTIVE EXPANSION (hold scope + cherry-pick), HOLD SCOPE (maximum rigor on what's there), SCOPE REDUCTION (strip to essentials). |
| `plan-eng-review` | **Eng Manager** | Lock architecture before writing code | ASCII data flow diagrams, state machine definitions, edge case enumeration, test matrix planning. Catches hidden assumptions — "What happens when the API returns a 429 during the webhook retry?" |
| `plan-design-review` | **Senior Designer** | Evaluate UI/UX design decisions in the plan | Rates each design dimension 0-10 (hierarchy, typography, motion, spacing, accessibility), explains what a 10 looks like, and rewrites the plan to get there. Detects "AI slop" patterns. |
| `plan-devex-review` | **DX Lead** | Review developer-facing products (APIs, CLIs, SDKs) | Explores developer personas, benchmarks Time-To-Hello-World against competitors, designs the "magical moment," traces friction point by point. |
| `autoplan` | **Review Pipeline** | Run all reviews automatically in one command | Chains CEO → design → eng → DX review with encoded decision principles. Surfaces only the close-call "taste decisions" for your approval. |

**Example — `plan-eng-review`:**

```
You:    Review this plan for a webhook processing system.
Agent:  [Draws ASCII architecture diagram]

        ┌──────────┐    ┌──────────────┐    ┌──────────┐
        │ Webhook  │───→│  Queue       │───→│ Processor│
        │ Receiver │    │ (Redis)      │    │ Workers  │
        └──────────┘    └──────────────┘    └──────────┘

        Three concerns:
        1. ORDERING: Your plan assumes FIFO, but Redis lists don't guarantee
           ordering under concurrent LPUSH. Do you need strict ordering per
           source, or is best-effort fine?
        2. RETRY: What's the dead-letter strategy? After 3 failures, where
           do events go? Your plan says "retry" but never says "give up."
        3. IDEMPOTENCY: The processor has no dedup key. If a webhook fires
           twice (common with Stripe), you'll process the same event twice.

        [Asks you to decide on each, then updates the plan]
```

### Build Phase

| Skill | Your Specialist | When to Use | Real-World Example |
|-------|----------------|-------------|-------------------|
| `design-consultation` | **Design Partner** | Create a design system from scratch for a new project | Researches the competitive landscape, proposes typography + color + spacing + motion system, generates preview pages. Writes `DESIGN.md` as the project's source of truth. |
| `design-html` | **Design Engineer** | Turn an approved design into production HTML | Uses Pretext for computed text layout — text actually reflows on resize instead of breaking with hardcoded heights. 30KB overhead, zero deps. |
| `design-shotgun` | **Design Explorer** | See multiple visual options before committing | Generates 3-5 design variants, deploys a comparison board (via `deploy_website`), collects structured feedback, iterates. |
| `investigate` | **Debugger** | Find root cause of a bug before fixing it | Iron Law: no fixes without root cause. Four phases: investigate → analyze → hypothesize → implement. Stops after 3 failed hypotheses and escalates. |

**Example — `investigate`:**

```
You:    Users are seeing blank pages on the dashboard after login.
Agent:  [Phase 1: INVESTIGATE — gathering evidence]
        Checking: network requests, console errors, auth token flow...
        Found: 401 response on /api/user/preferences 200ms after login.
        The token is present but expired — it's a cached token from the
        previous session.

        [Phase 2: ANALYZE — root cause]
        The auth middleware validates the token's `exp` claim, but the
        frontend stores the token in localStorage and only refreshes it
        on explicit login. A user who was logged in yesterday, closes the
        tab, and returns today hits the stale token.

        [Phase 3: HYPOTHESIZE]
        Fix: Add a token freshness check on app mount — if exp < now,
        trigger a silent refresh before the first API call.

        [Phase 4: IMPLEMENT — with your approval]
```

### Review Phase

| Skill | Your Specialist | When to Use | Real-World Example |
|-------|----------------|-------------|-------------------|
| `review` | **Staff Engineer** | Pre-landing code review on any branch with changes | Reads the diff against base branch. Checks for: SQL injection, LLM trust boundary violations, conditional side effects, incomplete migrations, missing error handling. Auto-fixes obvious issues, flags ambiguous ones for your decision. |
| `cso` | **Chief Security Officer** | Security audit before shipping | OWASP Top 10 + STRIDE threat model. Infrastructure-first: secrets archaeology, dependency supply chain, CI/CD pipeline security. Zero-noise mode with 8/10 confidence gate — only reports findings it can verify. Each finding includes a concrete exploit scenario. |
| `codex` | **Second Opinion** | Get a different AI model's perspective | Dispatches via `run_subagent` with a different model (GPT, Gemini, etc.) for independent review. Three modes: code review (pass/fail gate), adversarial challenge (actively tries to break your code), and open consultation. |

### Test Phase

| Skill | Your Specialist | When to Use | Real-World Example |
|-------|----------------|-------------|-------------------|
| `qa` | **QA Lead** | Test a live web app, find bugs, and fix them | Opens the app via `browser_task`, systematically clicks through flows, checks for console errors, takes screenshots. Three tiers: Quick (critical only), Standard (+ medium), Exhaustive (+ cosmetic). Fixes bugs with atomic commits and re-verifies each fix. |
| `qa-only` | **QA Reporter** | Same testing, but report-only — no code changes | Produces a structured bug report with health score, screenshots, and repro steps. Use when you want a report for a team handoff without the agent touching code. |
| `design-review` | **Designer Who Codes** | Visual QA — find and fix spacing, hierarchy, and AI slop issues | Iterative audit + fix loop. Takes before/after screenshots, commits each fix atomically. For plan-stage review (before code), use `plan-design-review` instead. |
| `devex-review` | **DX Tester** | Live-test your developer onboarding | Actually navigates docs, tries the getting-started flow, times how long it takes to reach "hello world," screenshots error messages. Compares against `plan-devex-review` scores. |
| `benchmark` | **Performance Engineer** | Catch performance regressions before they ship | Baselines page load times, Core Web Vitals, resource sizes. Compares before/after on every PR. |

### Ship Phase

| Skill | Your Specialist | When to Use | Real-World Example |
|-------|----------------|-------------|-------------------|
| `ship` | **Release Engineer** | The full shipping workflow | Syncs with base branch, runs tests, audits coverage, bumps VERSION, updates CHANGELOG, pushes, creates PR. Bootstraps a test framework from scratch if your project doesn't have one. |
| `land-and-deploy` | **Release Engineer** | Merge PR → deploy → verify production | Merges the PR (created by `ship`), waits for CI, monitors the deploy, runs canary health checks via `browser_task` and `fetch_url`. |
| `canary` | **SRE** | Post-deploy production monitoring | Periodic checks for console errors, performance regressions, and page failures. In qstack, this can be automated with `schedule_cron` for continuous monitoring. |
| `document-release` | **Technical Writer** | Update docs to match what shipped | Reads all project docs, cross-references the diff, updates README/ARCHITECTURE/CONTRIBUTING to match the new code. Catches stale documentation automatically. |

### Reflect Phase

| Skill | Your Specialist | When to Use | Real-World Example |
|-------|----------------|-------------|-------------------|
| `retro` | **Eng Manager** | Weekly or sprint retrospective | Analyzes commit history, work patterns, code quality. Team-aware: per-person breakdowns with praise and growth areas. Tracks trends over time. |
| `learn` | **Memory** | Review what the agent has learned about your codebase | In qstack, this maps to Perplexity's built-in `memory_search` / `memory_update`. Learnings compound across sessions automatically. |

### Safety and Utilities

| Skill | When to Use |
|-------|-------------|
| `careful` | Activate safety warnings before destructive commands (rm -rf, DROP TABLE, force-push) |
| `freeze` | Lock edits to a specific directory — prevents accidental changes while debugging |
| `guard` | `careful` + `freeze` combined — maximum safety for production work |
| `unfreeze` | Remove the freeze boundary |
| `checkpoint` | Save working state so you can resume later |
| `setup-deploy` | One-time deploy platform configuration |

---

## Install — 2 Minutes

### Option 1: Upload Skills Individually

1. Download any skill's `SKILL.md` from the `skills/` directory in this repo
2. In Perplexity Computer: **Skills → + Create skill → Upload a skill**
3. Drop the `.md` file
4. The skill auto-activates when your prompt matches its description

### Option 2: Bulk Upload

1. Download the `skills/` directory from this repo
2. Upload each `skills/[name]/SKILL.md` through the Skills UI
3. Or zip individual skill folders and upload the `.zip` files

No terminal. No dependencies. No setup script. No CLAUDE.md. No PATH configuration.

---

## How the Conversion Was Done

Two Python scripts process gstack's 30 skill files in a single pass:

1. **`scripts/convert-to-qstack.py`** — Strips ~445 lines of shared boilerplate per skill (bash preamble, telemetry, session tracking, CLAUDE.md routing), remaps tool references (`$B` → `browser_task`, `Agent` → `run_subagent`, learnings → Perplexity memory), rebrands gstack → qstack
2. **`scripts/post-clean.py`** — Second pass to clean browse daemon setup blocks, desktop-only paths, and analytics references

**Result: 32,315 → 18,317 lines (43% reduction) across 30 skills.** The methodology is preserved; the desktop plumbing is removed.

To re-run after upstream gstack updates:

```bash
python3 scripts/convert-to-qstack.py
python3 scripts/post-clean.py
```

---

## Tool Mapping Reference

| gstack (Claude Code Desktop) | qstack (Perplexity Computer) |
|------------------------------|------------------------------|
| `$B goto URL` | `browser_task(url=..., task="Navigate to...")` |
| `$B snapshot` | `screenshot_page(url=...)` |
| `$B click` / `$B fill` | `browser_task(task="Click..." / "Fill...")` |
| `Agent` sub-agent | `run_subagent(subagent_type="general_purpose")` |
| `AskUserQuestion` | `ask_user_question` |
| `WebSearch` | `search_web` / `fetch_url` |
| `Bash` with `git` / `gh` | `bash` with `api_credentials=["github"]` |
| `~/.gstack/learnings` | `memory_search` / `memory_update` |
| `CLAUDE.md` routing | Automatic skill activation by description match |
| `Conductor` (parallel sessions) | Multiple `run_subagent` calls |
| Local Chromium daemon | `browser_task` (cloud) or Comet local browser |
| `gstack-analytics` | Perplexity activity timeline (built-in) |
| No scheduling | `schedule_cron` for recurring tasks |
| No app integrations (beyond MCP) | 400+ OAuth connectors (Gmail, Slack, Notion, etc.) |

---

## File Structure

```
qstack/
├── README.md                    ← You are here
├── QSTACK-PLAN.md               ← Detailed conversion plan and architecture comparison
├── skills/                      ← Upload-ready qstack skills for Perplexity Computer
│   ├── office-hours/SKILL.md
│   ├── plan-ceo-review/SKILL.md
│   ├── plan-eng-review/SKILL.md
│   ├── plan-design-review/SKILL.md
│   ├── plan-devex-review/SKILL.md
│   ├── review/SKILL.md
│   ├── ship/SKILL.md
│   ├── qa/SKILL.md
│   ├── qa-only/SKILL.md
│   ├── cso/SKILL.md
│   ├── investigate/SKILL.md
│   ├── autoplan/SKILL.md
│   ├── ... (30 skills total)
│   └── unfreeze/SKILL.md
├── scripts/
│   ├── convert-to-qstack.py     ← Main conversion script
│   └── post-clean.py            ← Post-processing cleanup
└── gstack-original/             ← Original gstack source (archived for reference)
```

---

## Credits

- **[gstack](https://github.com/garrytan/gstack)** by [Garry Tan](https://x.com/garrytan) — the original toolkit, MIT License. All methodology, skill design, workflow philosophy, and the "virtual engineering team" concept are Garry's work.
- **qstack** adapts that work for [Perplexity Computer](https://www.perplexity.ai/), making it accessible from any browser without terminal setup.

## License

MIT — same as gstack. Free forever.
