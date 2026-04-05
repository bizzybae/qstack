#!/usr/bin/env python3
"""
post-clean.py — Second pass to clean remaining desktop-specific patterns
from converted qstack skills.
"""

import re
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "qstack-skills"

# Bash blocks that reference the browse daemon setup should be replaced
# with a Perplexity Computer browser note
BROWSE_SETUP_REPLACEMENT = """> **Browser access in Perplexity Computer:** Use `browser_task` to navigate and interact with web pages,
> `screenshot_page` to capture screenshots, and `js_repl` with Playwright for advanced browser automation.
> For local browser access, use `browser_task` with `use_local_browser`."""

DESIGN_SETUP_REPLACEMENT = """> **Design tools in Perplexity Computer:** Use `browser_task` to preview designs,
> `screenshot_page` to capture visual comparisons, and `deploy_website` to host comparison boards."""


def clean_browse_setup_blocks(content: str) -> str:
    """Replace bash blocks that set up the browse daemon with Perplexity instructions."""
    # Pattern: ## SETUP block with browse/dist/browse references
    content = re.sub(
        r'## SETUP \(run this check BEFORE any browse command\)\s*\n```bash\n.*?```\s*\n(.*?(?=\n##|\Z))',
        BROWSE_SETUP_REPLACEMENT + '\n',
        content,
        flags=re.DOTALL
    )
    
    # Pattern: standalone bash blocks that set up $B variable
    content = re.sub(
        r'```bash\n_ROOT=\$\(git rev-parse.*?browse/dist/browse.*?```',
        BROWSE_SETUP_REPLACEMENT,
        content,
        flags=re.DOTALL
    )
    
    # Pattern: bash blocks setting up design binary
    content = re.sub(
        r'```bash\n_ROOT=\$\(git rev-parse.*?design/dist/design.*?```',
        DESIGN_SETUP_REPLACEMENT,
        content,
        flags=re.DOTALL
    )
    
    return content


def clean_claude_paths(content: str) -> str:
    """Remove or replace remaining .claude/ path references."""
    # ~/.claude/plans/ → workspace files
    content = re.sub(
        r'~/.claude/plans/\S+',
        '/home/user/workspace/ (project files)',
        content
    )
    content = content.replace('~/.claude/plans/', '/home/user/workspace/')
    
    # .claude/skills/qstack/ paths
    content = re.sub(
        r'(?:\$_ROOT/)?\.claude/skills/qstack/\S+',
        '(qstack skill reference)',
        content
    )
    content = re.sub(
        r'~/.claude/skills/\S*',
        '(skill directory)',
        content
    )
    content = content.replace('.claude/skills/', '')
    
    return content


def clean_analytics_refs(content: str) -> str:
    """Remove analytics/telemetry bash commands that remain in tiny skills."""
    # Remove lines that write to skill-usage.jsonl
    content = re.sub(
        r"echo '\{\"skill\":.*?skill-usage\.jsonl.*?\n",
        '',
        content
    )
    # Remove (qstack memory) analytics references
    content = re.sub(
        r'\(qstack memory\)\s*analytics/skill-usage\.jsonl',
        'Perplexity memory (via memory_update)',
        content
    )
    return content


def clean_qstack_dev_refs(content: str) -> str:
    """Replace ~/.qstack-dev/ references."""
    content = content.replace('~/.qstack-dev/', '/home/user/workspace/.qstack/')
    content = content.replace('~/.gstack-dev/', '/home/user/workspace/.qstack/')
    return content


def clean_codex_skill(content: str) -> str:
    """Special handling for the codex skill — references to Codex CLI are intentional."""
    # The codex skill is about getting a second opinion from OpenAI's Codex.
    # In Perplexity Computer, this maps to run_subagent with a different model.
    # But the ~/.claude/ warnings inside codex commands are meta-instructions, keep but clean.
    return content


def fix_yaml_description(content: str) -> str:
    """Fix double-newlines in YAML multiline descriptions."""
    # The YAML dumper produces extra newlines in literal block scalars
    lines = content.split('\n')
    in_frontmatter = False
    in_description = False
    result = []
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                in_frontmatter = False
                in_description = False
            result.append(line)
            continue
        
        if in_frontmatter and line.startswith('description:'):
            in_description = True
            result.append(line)
            continue
        
        if in_frontmatter and in_description:
            # Skip blank lines within the description
            if line.strip() == '':
                continue
            # If this line isn't indented, description is done
            if not line.startswith(' ') and not line.startswith('\t'):
                in_description = False
            result.append(line)
            continue
        
        result.append(line)
    
    return '\n'.join(result)


def clean_file(path: Path) -> bool:
    """Clean a single SKILL.md file. Returns True if modified."""
    content = path.read_text()
    original = content
    
    content = fix_yaml_description(content)
    content = clean_browse_setup_blocks(content)
    content = clean_claude_paths(content)
    content = clean_analytics_refs(content)
    content = clean_qstack_dev_refs(content)
    
    # Collapse excessive blank lines
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    if content != original:
        path.write_text(content)
        return True
    return False


def main():
    skill_files = list(SKILLS_DIR.rglob("SKILL.md"))
    modified = 0
    
    for f in sorted(skill_files):
        skill_name = f.parent.name
        if clean_file(f):
            modified += 1
            print(f"  CLEANED  {skill_name}")
        else:
            print(f"  OK       {skill_name}")
    
    print(f"\n{modified}/{len(skill_files)} files cleaned.")


if __name__ == "__main__":
    main()
