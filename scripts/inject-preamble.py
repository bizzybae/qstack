#!/usr/bin/env python3
"""
inject-preamble.py — Add Perplexity Computer environment context to key skills.
"""

from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "skills"

# Skills to patch and their specific environment setup instructions
SKILL_PREAMBLES = {
    "office-hours": """
## Perplexity Computer Environment

Before starting the office-hours workflow:

1. **Search memory first:** `memory_search` for past brainstorming sessions, project context,
   and user preferences for this domain
2. **Save the design doc** to `/home/user/workspace/` — downstream skills (plan-ceo-review,
   plan-eng-review) can read it from there
3. **At the end:** `memory_update` with key decisions and the design doc location
4. **If connected apps exist** (check via `list_external_tools`): search Slack/Gmail/Notion
   for customer context before asking the forcing questions
""",
    "review": """
## Perplexity Computer Environment

Before starting the review:

1. **Clone the repo** if not already in workspace:
   `bash` with `api_credentials=["github"]`: `gh repo clone [owner/repo] /home/user/workspace/[repo]`
2. **Git operations** use `bash` with `api_credentials=["github"]` — this injects the GitHub token
   automatically. No manual auth needed.
3. **To read the diff:** `bash`: `cd /home/user/workspace/[repo] && git diff main...HEAD`
4. **To create a PR:** `bash` with `api_credentials=["github"]`: `gh pr create --title "..." --body "..."`
5. **Search memory first:** `memory_search` for past review findings on this repo
6. **At the end:** `memory_update` with key findings for future reference
7. **If Linear/Jira connected:** create follow-up tickets for non-blocking findings
""",
    "ship": """
## Perplexity Computer Environment

Before starting the ship workflow:

1. **Clone the repo** if not already in workspace:
   `bash` with `api_credentials=["github"]`: `gh repo clone [owner/repo] /home/user/workspace/[repo]`
2. **All git/gh commands** use `bash` with `api_credentials=["github"]`
3. **Run tests:** `bash`: `cd /home/user/workspace/[repo] && [test command]`
   (detect test runner from package.json, Makefile, pytest.ini, etc.)
4. **Create PR:** `bash` with `api_credentials=["github"]`:
   `cd /home/user/workspace/[repo] && gh pr create --title "..." --body "..."`
5. **Search memory:** `memory_search` for this project's shipping preferences (branch naming,
   PR template, changelog format)
6. **At the end:** `memory_update` with PR link and what shipped
7. **If Slack connected:** post ship notification (use `confirm_action` first)
8. **If Linear/Jira connected:** move ticket to "Done"
""",
    "qa": """
## Perplexity Computer Environment

QA testing in Perplexity Computer uses browser automation instead of gstack's browse daemon:

1. **Navigate to the app:** `browser_task(url="[staging_url]", task="Navigate to the app and verify it loads")`
2. **Take screenshots:** `screenshot_page(url="[url]")` — captures the current visual state
3. **Interactive testing:** `browser_task(task="Click the login button, fill in test credentials, submit the form, and verify the dashboard loads")`
4. **Advanced automation:** `js_repl` with Playwright for complex multi-step flows that need persistent state
5. **For local browser testing:** use `browser_task` with `use_local_browser` to test with the user's real logged-in sessions
6. **Clone the repo** for code fixes: `bash` with `api_credentials=["github"]`: `gh repo clone [owner/repo]`
7. **Search memory:** `memory_search` for known issues and past QA findings on this app
8. **At the end:** `memory_update` with bugs found and fixed
9. **If Linear/Jira connected:** create bug tickets with repro steps and screenshots
""",
    "cso": """
## Perplexity Computer Environment

Before starting the security audit:

1. **Clone the repo:** `bash` with `api_credentials=["github"]`:
   `gh repo clone [owner/repo] /home/user/workspace/[repo]`
2. **Dependency scanning:** `bash`: `cd /home/user/workspace/[repo] && npm audit` (or pip audit, etc.)
3. **Secrets scanning:** `grep` tool to search for API keys, tokens, passwords across the codebase
4. **Search memory:** `memory_search` for past security findings on this repo
5. **At the end:** `memory_update` with findings summary and severity counts
6. **If Slack connected:** post critical findings to a security channel (confirm first)
7. **Schedule recurring audits:** suggest `qstack-scheduled-ops` for weekly automated scans
""",
}

MARKER = "> Adapted from [gstack]"


def inject_preamble(skill_name: str, preamble: str) -> bool:
    skill_md = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_md.exists():
        return False

    content = skill_md.read_text()

    # Don't double-inject
    if "## Perplexity Computer Environment" in content:
        print(f"  SKIP  {skill_name} (already has preamble)")
        return False

    # Find insertion point: after the attribution line, or after the frontmatter
    if MARKER in content:
        # Insert after the attribution line
        idx = content.index(MARKER)
        end_of_line = content.index("\n", idx)
        content = content[:end_of_line + 1] + "\n" + preamble.strip() + "\n" + content[end_of_line + 1:]
    else:
        # Insert after frontmatter
        second_dash = content.index("---", 3)
        end_fm = content.index("\n", second_dash)
        content = content[:end_fm + 1] + "\n" + preamble.strip() + "\n" + content[end_fm + 1:]

    skill_md.write_text(content)
    return True


def main():
    for skill_name, preamble in SKILL_PREAMBLES.items():
        if inject_preamble(skill_name, preamble):
            print(f"  PATCHED  {skill_name}")
        else:
            print(f"  SKIP     {skill_name}")


if __name__ == "__main__":
    main()
