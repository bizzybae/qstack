#!/usr/bin/env python3
"""
enhance-skills.py — Add Perplexity Computer environment preambles and
cross-reference handoffs to all qstack skills.

Handles two tasks:
1. Injects a skill-specific "## Perplexity Computer Environment" section
   after the attribution line (if not already present)
2. Appends a "## Skill Graph — What to Use Next" section at the end
   (if not already present)
"""

from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "skills"

# ── SKILL GRAPH ────────────────────────────────────────────────
# Maps each skill to: predecessors (what feeds into it), successors (what comes next),
# and alternatives (use this instead if...).

SKILL_GRAPH = {
    # ─── Think Phase ───
    "office-hours": {
        "next": ["plan-ceo-review", "plan-eng-review"],
        "also": ["plan-design-review", "plan-devex-review"],
        "note": "Start here for new ideas. Outputs a design doc that feeds directly into the Plan phase.",
    },

    # ─── Plan Phase ───
    "plan-ceo-review": {
        "prev": ["office-hours"],
        "next": ["plan-eng-review", "plan-design-review"],
        "note": "After CEO review approves the scope, move to eng review to lock the architecture.",
    },
    "plan-eng-review": {
        "prev": ["office-hours", "plan-ceo-review"],
        "next": ["plan-design-review", "plan-devex-review"],
        "note": "After eng review locks the architecture, start building — or run design/DX review if the feature has UI or developer-facing components.",
    },
    "plan-design-review": {
        "prev": ["office-hours", "plan-ceo-review"],
        "next": ["design-consultation", "design-shotgun"],
        "alt": {"design-review": "Use `design-review` instead for auditing a live site (post-implementation)."},
        "note": "After plan-stage design review, use `design-consultation` to build the design system or `design-shotgun` to explore visual variants.",
    },
    "plan-devex-review": {
        "prev": ["plan-eng-review"],
        "next": ["devex-review"],
        "note": "After plan-stage DX review, build the feature, then use `devex-review` to live-test the actual developer experience.",
    },
    "autoplan": {
        "prev": ["office-hours"],
        "next": ["review", "ship"],
        "note": "Autoplan runs CEO + design + eng + DX reviews in sequence automatically. After it completes, move to building, then `review` and `ship`.",
    },

    # ─── Build Phase ───
    "design-consultation": {
        "prev": ["plan-design-review"],
        "next": ["design-html", "design-shotgun"],
        "note": "After creating the design system (DESIGN.md), use `design-html` to generate production HTML or `design-shotgun` to explore variants.",
    },
    "design-html": {
        "prev": ["design-consultation", "design-shotgun", "plan-design-review"],
        "next": ["design-review", "qa"],
        "note": "After generating HTML, use `design-review` for visual QA or `qa` for full testing.",
    },
    "design-shotgun": {
        "prev": ["design-consultation", "plan-design-review"],
        "next": ["design-html"],
        "note": "After the user picks a variant, use `design-html` to finalize it into production HTML.",
    },
    "investigate": {
        "next": ["review", "ship"],
        "note": "After root cause is found and fix is implemented, use `review` to check the diff, then `ship` to create the PR.",
    },

    # ─── Review Phase ───
    "review": {
        "prev": ["investigate"],
        "next": ["ship"],
        "also": ["codex"],
        "note": "After review passes, use `ship` to create the PR. For a second opinion, use `codex`.",
    },
    "cso": {
        "next": ["review", "ship"],
        "also": ["qstack-scheduled-ops"],
        "note": "After the security audit, address findings, then `review` and `ship`. Suggest `qstack-scheduled-ops` to schedule recurring audits.",
    },
    "codex": {
        "prev": ["review"],
        "next": ["ship"],
        "note": "After getting a second opinion, proceed to `ship` if both reviews pass.",
    },

    # ─── Test Phase ───
    "qa": {
        "prev": ["review"],
        "next": ["ship", "design-review"],
        "alt": {"qa-only": "Use `qa-only` if you want a bug report without code changes."},
        "note": "After QA testing and bug fixes, use `ship` to create the PR. If visual issues remain, use `design-review`.",
    },
    "qa-only": {
        "next": ["qa"],
        "alt": {"qa": "Use `qa` instead for the full test-fix-verify loop."},
        "note": "After receiving the report, use `qa` if you want the agent to fix the bugs it found.",
    },
    "design-review": {
        "prev": ["design-html", "qa"],
        "next": ["ship"],
        "alt": {"plan-design-review": "Use `plan-design-review` for pre-implementation design critique."},
        "note": "After visual fixes are committed, use `ship` to create the PR.",
    },
    "devex-review": {
        "prev": ["plan-devex-review"],
        "next": ["ship", "document-release"],
        "note": "After the DX audit, fix issues, then `ship`. If docs need updating, use `document-release`.",
    },
    "benchmark": {
        "next": ["ship", "investigate"],
        "also": ["qstack-scheduled-ops"],
        "note": "If regressions are found, use `investigate` for root cause. Suggest `qstack-scheduled-ops` to schedule nightly benchmarks.",
    },

    # ─── Ship Phase ───
    "ship": {
        "prev": ["review", "qa", "cso"],
        "next": ["land-and-deploy", "document-release"],
        "note": "After the PR is created, use `land-and-deploy` to merge and verify production. Use `document-release` to update docs.",
    },
    "land-and-deploy": {
        "prev": ["ship"],
        "next": ["canary", "document-release", "retro"],
        "note": "After deploy is verified, use `canary` for ongoing monitoring and `document-release` to sync docs. At week's end, use `retro`.",
    },
    "canary": {
        "prev": ["land-and-deploy"],
        "next": ["investigate"],
        "also": ["qstack-scheduled-ops"],
        "note": "If canary detects issues, use `investigate` for root cause. Suggest `qstack-scheduled-ops` to automate canary checks on a schedule.",
    },

    # ─── Reflect Phase ───
    "document-release": {
        "prev": ["ship", "land-and-deploy"],
        "next": ["retro"],
        "note": "After docs are updated, the sprint is complete. At week's end, use `retro`.",
    },
    "retro": {
        "prev": ["land-and-deploy", "document-release"],
        "note": "The retro closes the sprint loop. Learnings feed into future `office-hours` sessions via `qstack-memory`.",
    },

    # ─── Safety/Utility ───
    "careful": {
        "also": ["guard", "freeze"],
        "note": "For directory-scoped protection, use `freeze`. For both safety warnings and directory lock, use `guard`.",
    },
    "freeze": {
        "also": ["guard", "careful", "unfreeze"],
        "note": "Use `unfreeze` to remove the restriction. Use `guard` for freeze + destructive command warnings.",
    },
    "guard": {
        "also": ["careful", "freeze", "unfreeze"],
        "note": "Combines `careful` + `freeze`. Use `unfreeze` to remove the directory restriction.",
    },
    "unfreeze": {
        "also": ["freeze", "guard"],
    },
    "checkpoint": {
        "note": "Use at session boundaries or before switching branches. Resume with 'where was I?' in a new session.",
    },
    "learn": {
        "also": ["qstack-memory"],
        "note": "`qstack-memory` provides structured naming conventions for Perplexity's built-in memory system.",
    },
    "setup-deploy": {
        "next": ["land-and-deploy"],
        "note": "Run once per project to configure deploy settings. After setup, `land-and-deploy` handles future deploys automatically.",
    },

    # ─── Perplexity-Native ───
    "qstack-sprint": {
        "note": "Orchestrates the full pipeline. For individual phases, use the specific skill directly.",
    },
    "qstack-memory": {
        "note": "Invoke at the end of any skill to store learnings. Search at the start to retrieve past context.",
    },
    "qstack-scheduled-ops": {
        "prev": ["canary", "cso", "benchmark", "retro"],
        "note": "Set up recurring automated versions of canary, cso, benchmark, or retro.",
    },
    "qstack-connectors": {
        "note": "Enhance any skill's output by posting to Slack, updating Notion, filing Linear tickets, or emailing summaries.",
    },
}

# ── PREAMBLES ──────────────────────────────────────────────────
# Skill-specific Perplexity Computer environment sections.
# Only for skills that DON'T already have one (the top 5 were done earlier).

PREAMBLES = {
    "plan-ceo-review": """
## Perplexity Computer Environment

1. **Read the design doc** from workspace if it exists (output of `office-hours`):
   check `/home/user/workspace/` for `.md` files matching the project name
2. **Search memory first:** `memory_search` for past reviews of this project, user's scope preferences, and previous CEO review findings
3. **Save your review** to workspace so downstream skills can read it
4. **At the end:** `memory_update` with key scope decisions and verdict
""",
    "plan-eng-review": """
## Perplexity Computer Environment

1. **Read the design doc and CEO review** from workspace if they exist
2. **Search memory:** `memory_search` for architecture decisions, past eng reviews, and known pitfalls for this tech stack
3. **For architecture diagrams:** use ASCII art directly in the output (renders well in Perplexity)
4. **Save your review** to workspace for the build phase
5. **At the end:** `memory_update` with architecture decisions and test matrix
""",
    "plan-design-review": """
## Perplexity Computer Environment

1. **Read the design doc** from workspace if available
2. **For visual references:** use `search_vertical(vertical="image")` to find design inspiration
3. **For existing site audits:** use `screenshot_page` to capture current state
4. **Search memory:** `memory_search` for the project's design system, past design decisions
5. **Save your review** to workspace
6. **At the end:** `memory_update` with design dimension scores and key decisions
""",
    "plan-devex-review": """
## Perplexity Computer Environment

1. **Read the design doc and eng review** from workspace if available
2. **For competitor benchmarking:** use `search_web` and `browser_task` to research competing developer experiences
3. **Search memory:** `memory_search` for past DX reviews, known friction points, TTHW benchmarks
4. **Save your review** to workspace
5. **At the end:** `memory_update` with DX scores and persona-specific findings
""",
    "autoplan": """
## Perplexity Computer Environment

1. **Use `run_subagent`** to dispatch parallel reviews (CEO, design, eng, DX) instead of sequential in-process calls
2. **Workspace files are the handoff:** each review subagent reads the design doc and writes its review to a separate file
3. **Search memory first:** `memory_search` for past autoplan results on this project
4. **At the end:** `memory_update` with the combined verdict and key decisions
""",
    "investigate": """
## Perplexity Computer Environment

1. **Clone the repo** if needed: `bash` with `api_credentials=["github"]`: `gh repo clone [owner/repo]`
2. **Search memory:** `memory_search` for past bugs, known pitfalls, and previous investigations on this codebase
3. **For live debugging:** use `browser_task` to reproduce issues in the browser, `screenshot_page` to capture error states
4. **At the end:** `memory_update` with root cause and the pitfall pattern (prefix with `pitfall:`)
""",
    "codex": """
## Perplexity Computer Environment

In Perplexity Computer, the "second opinion" is obtained via `run_subagent` with a different model:

1. **Code review mode:** `run_subagent(subagent_type="codebase", model="gpt_5_4", objective="Review the diff...")` 
2. **Challenge mode:** `run_subagent(model="claude_opus_4_6", objective="Try to break this code...")`
3. **Consult mode:** `run_subagent(model="gemini_3_1_pro", objective="[question]")`
4. **Spawn multiple models in parallel** for a panel of opinions
""",
    "land-and-deploy": """
## Perplexity Computer Environment

1. **Merge via CLI:** `bash` with `api_credentials=["github"]`: `gh pr merge [number] --squash`
2. **Wait for CI:** `bash` with `api_credentials=["github"]`: `gh run list --limit 5` and poll until complete
3. **Verify production:** use `browser_task` to load the production URL and check for errors, or `fetch_url` for API health checks
4. **Search memory:** `memory_search` for this project's deploy config (platform, URLs, health endpoints)
5. **If Slack connected:** post deploy notification (use `confirm_action` first)
6. **At the end:** `memory_update` with deploy outcome
""",
    "retro": """
## Perplexity Computer Environment

1. **Clone the repo:** `bash` with `api_credentials=["github"]`: `gh repo clone [owner/repo]`
2. **Git log analysis:** `bash`: `git log --since='7 days ago' --stat --pretty=format:'%h %an %s'`
3. **Search memory:** `memory_search` for past retros to track trends
4. **If Slack/Notion connected:** post retro summary (use `confirm_action` first)
5. **At the end:** `memory_update` with key metrics and action items (prefix with `sprint:`)
""",
    "document-release": """
## Perplexity Computer Environment

1. **Clone the repo:** `bash` with `api_credentials=["github"]`: `gh repo clone [owner/repo]`
2. **Read the diff:** `bash`: `git diff main...HEAD` to see what changed
3. **Use `read` and `edit`** to update docs in the workspace, then commit via `bash`
4. **Search memory:** `memory_search` for doc style preferences and past doc-release notes
5. **At the end:** `memory_update` with what docs were updated
""",
    "design-consultation": """
## Perplexity Computer Environment

1. **Research the landscape:** use `search_web` and `search_vertical(vertical="image")` to study competitors and design trends
2. **Font previews:** use `deploy_website` to host a preview page, or `screenshot_page` to capture it
3. **Save DESIGN.md** to workspace — downstream skills (`design-html`, `design-shotgun`) read it
4. **Search memory:** `memory_search` for the user's brand preferences and past design decisions
5. **At the end:** `memory_update` with the design system summary (prefix with `project:`)
""",
    "design-html": """
## Perplexity Computer Environment

1. **Read DESIGN.md** from workspace if it exists (output of `design-consultation`)
2. **Generate HTML** and save to workspace files
3. **Preview:** use `deploy_website` to host the page at a public URL, or `screenshot_page` to capture it
4. **The `vendor/` directory** in this skill contains Pretext JS — reference it for layout patterns
5. **Search memory:** `memory_search` for this project's design system and past HTML generation
""",
    "design-review": """
## Perplexity Computer Environment

1. **Capture current state:** use `screenshot_page(url="[staging_url]")` to take before screenshots
2. **Clone the repo** for code fixes: `bash` with `api_credentials=["github"]`
3. **After each fix:** `screenshot_page` again for after comparison, commit atomically
4. **Search memory:** `memory_search` for this project's design system and past visual QA findings
5. **At the end:** `memory_update` with issues found and fixed
""",
    "design-shotgun": """
## Perplexity Computer Environment

1. **Generate multiple variants** as HTML files in workspace
2. **Deploy comparison board:** use `deploy_website` to host all variants at a public URL, or use `share_file` to send screenshots
3. **Collect feedback** via `ask_user_question` with multi-select for which variants to iterate on
4. **Search memory:** `memory_search` for the project's design system preferences
""",
    "devex-review": """
## Perplexity Computer Environment

1. **Live-test the DX:** use `browser_task` to navigate docs, try getting-started flows, and time TTHW
2. **Capture evidence:** `screenshot_page` for error messages, confusing UI, broken links
3. **Compare to plan:** if `plan-devex-review` was run, `read` its output from workspace and compare scores
4. **Search memory:** `memory_search` for past DX findings and benchmarks
5. **At the end:** `memory_update` with DX scorecard and comparison to plan-stage predictions
""",
    "benchmark": """
## Perplexity Computer Environment

1. **Use `js_repl`** with Playwright for precise performance measurement:
   - `page.goto(url)` with `waitUntil: 'networkidle'`
   - `page.evaluate(() => performance.timing)` for load metrics
   - `page.evaluate(() => performance.getEntriesByType('resource'))` for resource breakdown
2. **Or use `browser_task`** for simpler page-load timing
3. **Search memory:** `memory_search` for past benchmarks (prefix `benchmark:`) to compare
4. **At the end:** `memory_update` with metrics (prefix with `benchmark:[project] [date]`)
""",
    "canary": """
## Perplexity Computer Environment

1. **Use `browser_task`** to load the production URL and check for console errors
2. **Use `fetch_url`** for API health checks (faster, no browser overhead)
3. **Use `screenshot_page`** to capture visual state for comparison
4. **For continuous monitoring:** suggest `qstack-scheduled-ops` to set up a `schedule_cron` job
5. **Search memory:** `memory_search` for pre-deploy baselines to compare against
""",
    "checkpoint": """
## Perplexity Computer Environment

1. **Git state:** capture via `bash` with `api_credentials=["github"]`: `git status`, `git log --oneline -5`, `git branch`
2. **Save checkpoint** to workspace: write a markdown file with current state, decisions made, remaining work
3. **Use `memory_update`** to store the checkpoint summary for cross-session recall:
   `"Remember: checkpoint:[project] [date] — on branch [x], completed [y], remaining [z]"`
4. **Resume:** `memory_search` for `checkpoint:[project]` to find where you left off
""",
    "learn": """
## Perplexity Computer Environment

In Perplexity Computer, learnings are stored in the platform's native memory system:

1. **Store:** `memory_update(content="Remember: [category]:[project] — [learning]")`
2. **Search:** `memory_search(queries=["project learnings for [project]"])`
3. **Categories:** project, pattern, pitfall, preference, decision, codebase, review, sprint
4. **See `qstack-memory`** for the full taxonomy and retrieval strategies
""",
    "careful": """
## Perplexity Computer Environment

The `bash` tool in Perplexity Computer runs in an isolated sandbox, so destructive commands
cannot affect your local machine. However, commands run with `api_credentials=["github"]`
can affect your real repositories (force-push, delete branches). Apply extra caution there.
""",
    "freeze": """
## Perplexity Computer Environment

In Perplexity Computer, file operations are already sandboxed to `/home/user/workspace`.
Freeze further restricts `edit` and `write` to a specific subdirectory within that workspace.
""",
    "guard": """
## Perplexity Computer Environment

Combines sandbox awareness (`careful`) with directory restriction (`freeze`).
Most useful when working on a cloned repo — restricts edits to the repo directory
and warns before any `bash` commands that could affect remote resources.
""",
    "unfreeze": """
## Perplexity Computer Environment

Removes the directory restriction set by `freeze` or `guard`, re-allowing
`edit` and `write` across the full `/home/user/workspace`.
""",
    "setup-deploy": """
## Perplexity Computer Environment

1. **Detect deploy platform:** use `bash` to check for fly.toml, render.yaml, vercel.json, netlify.toml, Procfile, or GitHub Actions workflows in the repo
2. **Save config** to workspace and `memory_update` so future `land-and-deploy` calls know the platform
3. **No CLAUDE.md needed** — store deploy config in Perplexity memory instead:
   `"Remember: project:[name] deploy — platform: [x], URL: [y], health: [z]"`
""",
    "qa-only": """
## Perplexity Computer Environment

Same browser tools as `qa` but report-only — no code changes:

1. **Navigate:** `browser_task(url="[staging_url]", task="Test the [flow]...")`
2. **Screenshots:** `screenshot_page(url="[url]")` for evidence
3. **Advanced flows:** `js_repl` with Playwright for multi-step testing
4. **Save report** to workspace via `write`; share via `share_file`
5. **If Linear/Jira connected:** create bug tickets from the report
""",
    # qstack-* skills already have good context, but add cross-refs
    "qstack-sprint": None,  # skip preamble, just add cross-refs
    "qstack-memory": None,
    "qstack-scheduled-ops": None,
    "qstack-connectors": None,
}


# ── INJECTION LOGIC ────────────────────────────────────────────

PREAMBLE_MARKER = "## Perplexity Computer Environment"
CROSSREF_MARKER = "## Skill Graph"
ATTRIBUTION_MARKER = "> Adapted from [gstack]"


def build_crossref_section(skill_name: str) -> str:
    """Build the cross-reference handoff section for a skill."""
    graph = SKILL_GRAPH.get(skill_name, {})
    if not graph:
        return ""

    lines = ["\n## Skill Graph — What to Use Next\n"]

    if "note" in graph:
        lines.append(f"{graph['note']}\n")

    if "prev" in graph:
        prev_list = ", ".join(f"`{s}`" for s in graph["prev"])
        lines.append(f"**Feeds from:** {prev_list}\n")

    if "next" in graph:
        next_list = ", ".join(f"`{s}`" for s in graph["next"])
        lines.append(f"**Next steps:** {next_list}\n")

    if "also" in graph:
        also_list = ", ".join(f"`{s}`" for s in graph["also"])
        lines.append(f"**See also:** {also_list}\n")

    if "alt" in graph:
        for alt_skill, reason in graph["alt"].items():
            lines.append(f"**Alternative:** {reason}\n")

    return "\n".join(lines)


def inject_into_skill(skill_dir: Path, preamble: str | None, crossref: str) -> bool:
    """Inject preamble and/or crossref into a skill. Returns True if modified."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False

    content = skill_md.read_text()
    modified = False

    # Inject preamble (after attribution line or after frontmatter)
    if preamble and PREAMBLE_MARKER not in content:
        if ATTRIBUTION_MARKER in content:
            idx = content.index(ATTRIBUTION_MARKER)
            end_of_line = content.index("\n", idx)
            content = content[:end_of_line + 1] + "\n" + preamble.strip() + "\n" + content[end_of_line + 1:]
        else:
            # After frontmatter
            try:
                second_dash = content.index("---", 3)
                end_fm = content.index("\n", second_dash)
                content = content[:end_fm + 1] + "\n" + preamble.strip() + "\n" + content[end_fm + 1:]
            except ValueError:
                pass
        modified = True

    # Inject cross-references (at the end of file)
    if crossref and CROSSREF_MARKER not in content:
        content = content.rstrip() + "\n" + crossref + "\n"
        modified = True

    if modified:
        skill_md.write_text(content)

    return modified


def main():
    patched = 0
    skipped = 0

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        if not (skill_dir / "SKILL.md").exists():
            continue

        name = skill_dir.name

        # Get preamble (None = skip preamble, already has one)
        preamble = PREAMBLES.get(name, "SKIP")
        if preamble == "SKIP":
            # Not in our map — check if it already has one
            content = (skill_dir / "SKILL.md").read_text()
            if PREAMBLE_MARKER in content:
                preamble = None  # already has preamble
            else:
                preamble = None  # not in our map, skip

        # Get cross-reference section
        crossref = build_crossref_section(name)

        if preamble is None and not crossref:
            skipped += 1
            print(f"  SKIP     {name}")
            continue

        if inject_into_skill(skill_dir, preamble, crossref):
            parts = []
            if preamble:
                parts.append("preamble")
            if crossref:
                parts.append("crossref")
            print(f"  PATCHED  {name} ({' + '.join(parts)})")
            patched += 1
        else:
            print(f"  OK       {name} (already enhanced)")
            skipped += 1

    print(f"\n{patched} skills enhanced, {skipped} already up to date.")


if __name__ == "__main__":
    main()
