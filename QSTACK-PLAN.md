# qstack — gstack adapted for Perplexity Computer

> Adapted from [garrytan/gstack](https://github.com/garrytan/gstack) (MIT License).
> gstack turns Claude Code into a virtual engineering team. **qstack** does the same for **Perplexity Computer**.

---

## What This Is

gstack is Garry Tan's open-source toolkit of 23+ opinionated workflow skills for Claude Code — turning it into a virtual CEO, eng manager, designer, QA lead, security officer, and release engineer. It's built for Claude Code on Desktop (local terminal, persistent headless Chromium daemon, compiled Bun binaries, macOS/Linux).

**qstack** is the same methodology, converted for **Perplexity Computer** — a cloud-based AI agent platform running in the browser with its own tool surface, sub-agents, 400+ app connectors, and custom skill uploads.

## How the Conversion Works

Each gstack SKILL.md contains ~445 lines of shared boilerplate (bash preamble, telemetry, session tracking, CLAUDE.md routing, config prompts) plus the actual methodology. The conversion script:

1. **Strips shared boilerplate** — preamble bash blocks, telemetry, session tracking, proactive-mode prompts, CLAUDE.md routing, voice triggers, context recovery templates
2. **Remaps tool references** — `$B goto` → `browser_task`, `$B snapshot` → `screenshot_page`, `Agent` → `run_subagent`, `gstack-learnings-*` → `memory_search`/`memory_update`
3. **Replaces desktop paths** — `~/.claude/skills/gstack/` → removed, `~/.gstack/` → Perplexity memory, `CLAUDE.md` → custom instructions
4. **Rebrands** — gstack → qstack throughout
5. **Preserves methodology** — the actual value (forcing questions, review frameworks, QA methodology, shipping workflow) passes through untouched

**Result: 32,315 → 18,317 lines (43% reduction) across 30 skills.**

## Converted Skills

### Ready for Upload (`qstack-skills/`)

| Skill | Lines | What It Does |
|-------|-------|-------------|
| `office-hours` | 1,089 | YC-style product interrogation with 6 forcing questions |
| `plan-ceo-review` | 1,243 | CEO/founder strategic review in 4 scope modes |
| `plan-eng-review` | 833 | Architecture, data flow, edge cases, test matrices |
| `plan-design-review` | 921 | Design dimension scoring, AI slop detection |
| `plan-devex-review` | 1,240 | Developer experience review with TTHW benchmarking |
| `review` | 892 | Pre-landing PR review with auto-fix |
| `ship` | 1,969 | Full shipping workflow: sync, test, audit, PR |
| `qa` | 824 | Systematic QA testing + bug fixing |
| `qa-only` | 406 | QA report without code changes |
| `cso` | 683 | OWASP Top 10 + STRIDE security audit |
| `investigate` | 226 | Root-cause debugging methodology |
| `autoplan` | 916 | Automated CEO → design → eng review pipeline |
| `retro` | 888 | Weekly engineering retrospective |
| `document-release` | 404 | Auto-update docs to match shipped code |
| `design-consultation` | 643 | Build a design system from scratch |
| `design-html` | 596 | Production HTML with Pretext |
| `design-review` | 979 | Design audit + fix loop |
| `design-shotgun` | 399 | Multiple design variant generation |
| `devex-review` | 412 | Live developer experience audit |
| `land-and-deploy` | 994 | Merge PR → deploy → verify production |
| `codex` | 499 | Multi-model second opinion (via run_subagent) |
| `canary` | 244 | Post-deploy monitoring |
| `benchmark` | 219 | Performance regression detection |
| `careful` | 52 | Safety guardrails for destructive commands |
| `freeze` | 69 | Edit lock to one directory |
| `guard` | 63 | careful + freeze combined |
| `unfreeze` | 39 | Remove freeze boundary |
| `checkpoint` | 251 | Git checkpoint/restore |
| `learn` | 119 | Manage cross-session learnings (via Perplexity memory) |
| `setup-deploy` | 205 | One-time deploy platform config |

### Skipped (Desktop-Only)

| Skill | Reason |
|-------|--------|
| `open-gstack-browser` | Launches headed Chromium — desktop only |
| `setup-browser-cookies` | Imports cookies from Chrome/Arc — desktop only |
| `connect-chrome` | Chrome DevTools Protocol — desktop only |
| `gstack-upgrade` | Self-updater via git — managed by Perplexity skill UI |
| `health` | gstack installation dashboard — not applicable |

## How to Install

### Individual Skills

1. Navigate to any skill in `qstack-skills/` (e.g., `qstack-skills/office-hours/`)
2. Download the `SKILL.md` file
3. In Perplexity Computer: Skills → Create Skill → Upload a Skill → drop the `.md` file
4. The skill auto-activates when your prompt matches its description

### Bulk Upload

Each skill directory can be zipped individually:

```bash
cd qstack-skills
for skill in */; do
  (cd "$skill" && zip -r "../${skill%/}.zip" .)
done
```

Then upload each `.zip` via the Skills UI.

## Tool Mapping Reference

| gstack (Claude Code) | qstack (Perplexity Computer) |
|---------------------|------------------------------|
| `$B goto URL` | `browser_task(url=..., task="Navigate to...")` |
| `$B snapshot` | `screenshot_page(url=...)` |
| `$B click` / `$B fill` | `browser_task(task="Click on..." / "Fill in...")` |
| `Agent` sub-agent | `run_subagent(subagent_type="general_purpose")` |
| `AskUserQuestion` | `ask_user_question` |
| `WebSearch` | `search_web` / `fetch_url` |
| `Bash` with `git`/`gh` | `bash` with `api_credentials=["github"]` |
| `~/.gstack/learnings` | `memory_search` / `memory_update` |
| `CLAUDE.md` routing | Perplexity custom instructions |
| `Conductor` parallelism | Multiple `run_subagent` calls |

## Remote MCP Server (Optional, Future)

Perplexity supports [custom remote MCP connectors](https://www.perplexity.ai/help-center/en/articles/13915507-adding-custom-remote-connectors). If you need structured project learnings beyond what Perplexity's built-in memory provides, you could build a lightweight MCP server exposing tools like `qstack_learnings_search` and `qstack_config`. For now, the platform's `memory_update`/`memory_search` covers 80%+ of the use case at zero infrastructure cost.

## Scripts

| Script | What It Does |
|--------|-------------|
| `scripts/convert-to-qstack.py` | Main conversion: strips boilerplate, remaps tools, rebrands |
| `scripts/post-clean.py` | Second pass: cleans browse daemon setup blocks, desktop paths |

To re-run conversion (e.g., after pulling upstream gstack changes):

```bash
python3 scripts/convert-to-qstack.py
python3 scripts/post-clean.py
```

---

*Attribution: qstack is adapted from [gstack](https://github.com/garrytan/gstack) by Garry Tan (MIT License).*
