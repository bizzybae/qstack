# CLAUDE.md

Guidance for AI assistants (Claude Code and others) working in this repository.

## What this repo is

**qstack** is a port of [garrytan/gstack](https://github.com/garrytan/gstack) (MIT)
from **Claude Code on Desktop** to **Perplexity Computer** (a cloud, browser-based AI
agent platform). gstack is a toolkit of opinionated *workflow skills* that turn an AI
agent into a virtual engineering team — CEO, eng manager, designer, QA lead, security
officer, release engineer. qstack delivers the same methodology as plain Markdown
skill files that upload into Perplexity Computer, with no terminal, no compiled
binaries, and no persistent browser daemon.

The product of this repo is **a set of `SKILL.md` files** plus the Python tooling that
generates and validates them. There is no application to build or run here — the
"code" is documentation/prompt engineering, and the deliverables are the skill files.

## Repository layout

```
skills/                 ← THE DELIVERABLE: 36 qstack SKILL.md files (canonical source)
gstack-original/        ← Upstream gstack, vendored as the conversion SOURCE + reference
scripts/                ← Conversion / enhancement / audit pipeline (Python) + inherited gstack tooling (TS)
benchmarks/             ← Audit reports (audit-*.md) + benchmark-history.json
README.md               ← User-facing: why Perplexity, the security argument, per-skill use cases
QSTACK-PLAN.md          ← The conversion roadmap, tool-mapping table, skill inventory
LICENSE                 ← MIT (attribution to Garry Tan / gstack)
```

### `skills/` — the canonical skill set
Each skill is a directory containing a single `SKILL.md` with YAML frontmatter
(`name`, `description`) and a Markdown body. Two kinds live here:

- **Converted skills** (~30): adapted from gstack — `office-hours`, `plan-ceo-review`,
  `plan-eng-review`, `plan-design-review`, `plan-devex-review`, `review`, `ship`,
  `qa`, `qa-only`, `cso`, `investigate`, `autoplan`, `retro`, `document-release`,
  `design-*`, `devex-review`, `land-and-deploy`, `codex`, `canary`, `benchmark`,
  `careful`, `freeze`, `guard`, `unfreeze`, `checkpoint`, `learn`, `setup-deploy`.
- **Perplexity-native skills** (`qstack-*`): net-new, built for Perplexity's surface —
  `qstack-sprint` (Think→Plan→Build→Review→Test→Ship orchestrator), `qstack-validate`
  (skill quality auditor), `qstack-connectors` (400+ app connectors), `qstack-memory`
  (cross-session memory conventions), `qstack-package` (client deliverable bundles),
  `qstack-scheduled-ops` (cron monitoring).

The philosophy maps the gstack sprint: **Think → Plan → Build → Review → Test → Ship →
Reflect**, each skill feeding the next. See README.md for the per-phase skill table.

### `gstack-original/` — vendored upstream
A full copy of upstream gstack (Bun project, `package.json` v0.15.8.0, headless browser,
`browse/`, `design/`, TS tests). It is the **input** to the conversion scripts and the
reference for methodology. Do **not** treat it as buildable project code for qstack —
it's a snapshot. Pull upstream changes here, then re-run the conversion.

### `scripts/` — tooling
The **active qstack pipeline is Python**:

| Script | Role |
|--------|------|
| `convert-to-qstack.py` | Main conversion: strips ~500 lines of gstack boilerplate, remaps tool refs (`$B goto`→`browser_task`, `Agent`→`run_subagent`, etc.), rebrands gstack→qstack, keeps `name`+`description` frontmatter. |
| `post-clean.py` | Second pass: removes browse-daemon setup blocks and desktop paths, inserts Perplexity browser notes. |
| `enhance-skills.py` | Injects the "Perplexity Computer Environment" preamble and a "Skill Graph — What to Use Next" cross-reference section into each skill (operates on `skills/`). |
| `audit-skills.py` | Validates frontmatter, cross-references, gstack residue, Perplexity compatibility, content quality; writes a scored report to `benchmarks/`. Foundation of the `qstack-validate` skill. |
| `inject-preamble.py` | Helper for preamble injection. |

The `.ts` files and `resolvers/` under `scripts/` are **inherited gstack tooling** (Bun,
skill-doc generation, evals, host adapters). They depend on gstack's `package.json` and
are not part of the qstack Python pipeline — leave them unless a task explicitly targets
upstream tooling.

> ⚠️ **Path note:** `convert-to-qstack.py` reads gstack skills from `REPO_ROOT` and
> writes to `qstack-skills/`, reflecting the original flat layout. The current canonical
> location is **`skills/`**, and `enhance-skills.py` / `audit-skills.py` already operate
> on `skills/`. When editing skills, **edit `skills/` directly** — that is the source of
> truth that ships. The conversion scripts are primarily for re-importing upstream gstack.

## Working conventions

### Editing skills
- A skill is just `skills/<name>/SKILL.md`. Frontmatter must start with `---` and carry
  a `name` (matching the directory) and a `description`. The `description` is what drives
  Perplexity's auto-activation — keep its trigger phrases ("Use when…", "Proactively…")
  precise and intact.
- Preserve the **methodology** (forcing questions, review frameworks, QA steps, shipping
  workflow). That is the value; everything else is plumbing.
- Use **Perplexity tool names**, never Claude Code / desktop ones. The mapping:

  | gstack (Claude Code) | qstack (Perplexity) |
  |----------------------|---------------------|
  | `$B goto` / `$B snapshot` | `browser_task` / `screenshot_page` |
  | `Agent` sub-agent | `run_subagent` (typed: research, codebase, asset, website, general_purpose) |
  | `AskUserQuestion` | `ask_user_question` |
  | `WebSearch` | `search_web` / `fetch_url` |
  | `~/.gstack/learnings` | `memory_search` / `memory_update` |
  | `CLAUDE.md` routing | Perplexity custom instructions |
  | cron / scheduling | `schedule_cron` |

- The agent runtime is a sandboxed cloud VM; the working directory referenced inside
  skills is `/home/user/workspace/` (handoff files between skills live there). Do not
  reintroduce `~/.claude/...`, headless-browser daemon setup, or compiled-binary steps.
- Keep the attribution line near the top of each skill
  (*"Adapted from gstack by Garry Tan (MIT License)…"*).

### Re-importing upstream gstack
```bash
# 1. Update gstack-original/ to the new upstream snapshot
# 2. Regenerate converted skills
python3 scripts/convert-to-qstack.py
python3 scripts/post-clean.py
python3 scripts/enhance-skills.py
# 3. Audit before committing
python3 scripts/audit-skills.py      # writes benchmarks/audit-<timestamp>.md
```
Then reconcile output into `skills/` and review diffs by hand — do not blindly overwrite
hand-tuned skills.

### Validating skill quality
Run `python3 scripts/audit-skills.py` (or the `qstack-validate` skill). It scores
structural integrity, cross-references, Perplexity compatibility, and gstack residue,
appending to `benchmarks/benchmark-history.json`. Aim to keep the health score from
regressing across versions.

### Tooling requirements
- Python 3 with `PyYAML` for the pipeline scripts (they `import yaml`).
- Bun is only needed for the inherited `gstack-original/` TS tooling, not for normal
  skill work.

## Git workflow

- Develop on the designated feature branch; commit with clear messages and push with
  `git push -u origin <branch>`.
- Commit messages in this repo follow a concise, imperative style and often note the
  scope (e.g. *"Enhance all 34 skills: Perplexity preambles + skill graph cross-refs"*).
- `qstack-zips/` and `qstack-upload/` are build artifacts and gitignored — never commit
  them.
- Do **not** open a pull request unless explicitly asked.

## Quick reference: where to look

- *"How do skills get converted?"* → `scripts/convert-to-qstack.py` + `QSTACK-PLAN.md`
- *"What does skill X do / when does it fire?"* → frontmatter `description` in
  `skills/<x>/SKILL.md`, and the use-case tables in `README.md`
- *"Why Perplexity over Claude Code?"* → README.md (security argument + capability tables)
- *"Is skill quality regressing?"* → `benchmarks/` reports + `qstack-validate`
