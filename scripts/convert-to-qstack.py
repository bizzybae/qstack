#!/usr/bin/env python3
"""
convert-to-qstack.py — Convert gstack SKILL.md files to Perplexity Computer-compatible qstack skills.

Strategy:
1. Keep frontmatter (name + description), strip gstack-only fields
2. Strip the shared boilerplate (~500 lines: preamble, telemetry, routing, etc.)
3. Remap tool references for Perplexity Computer
4. Rebrand gstack → qstack
5. Output clean SKILL.md files ready for Perplexity upload
"""

import os
import re
import sys
import yaml
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
SKILLS_INPUT_DIR = REPO_ROOT  # gstack skills are at root level
SKILLS_OUTPUT_DIR = REPO_ROOT / "qstack-skills"

# Shared boilerplate section headers to strip (in order they appear)
BOILERPLATE_SECTIONS = [
    "## Preamble (run first)",
    "## Skill routing",
    "## Voice",
    "## Context Recovery",
    "## AskUserQuestion Format",
    "## Completeness Principle — Boil the Lake",
    "## Repo Ownership — See Something, Say Something",
    "## Search Before Building",
    "## Completion Status Protocol",
    "## Operational Self-Improvement",
    "## Telemetry (run last)",
    "## Plan Mode Safe Operations",
    "## Skill Invocation During Plan Mode",
    "## Plan Status Footer",
    "## GSTACK REVIEW REPORT",
]

# Skills to skip (desktop-only, not applicable to Perplexity Computer)
SKIP_SKILLS = {
    "open-gstack-browser",   # Launches headed Chromium — desktop only
    "setup-browser-cookies", # Imports cookies from Chrome/Arc/Brave — desktop only
    "connect-chrome",        # Chrome DevTools Protocol — desktop only
    "gstack-upgrade",        # Self-updater via git — not applicable
    "health",                # gstack installation health dashboard — not applicable
}

# Skills that are too small/simple to need boilerplate stripping
TINY_SKILLS = {"careful", "freeze", "unfreeze", "guard"}

# Frontmatter fields to keep
KEEP_FRONTMATTER = {"name", "description"}

# ── Tool / reference remapping ─────────────────────────────────

REPLACEMENTS = [
    # Branding
    (r'\bGStack\b', 'QStack'),
    (r'\bgstack\b', 'qstack'),
    (r'\bGSTACK\b', 'QSTACK'),
    
    # Browse daemon commands → Perplexity browser tools
    (r'\$B\s+goto\s+', 'Use browser_task to navigate to '),
    (r'\$B\s+snapshot\s+-i', 'Use screenshot_page to capture the page'),
    (r'\$B\s+snapshot', 'Use screenshot_page to capture the page'),
    (r'\$B\s+click\s+', 'Use browser_task to click on '),
    (r'\$B\s+fill\s+', 'Use browser_task to fill in '),
    (r'\$B\s+type\s+', 'Use browser_task to type '),
    (r'\$B\s+scroll', 'Use browser_task to scroll'),
    (r'\$B\s+wait', 'Wait for the page to load'),
    (r'\$B\s+tabs', 'Use browser_task to manage tabs'),
    (r'\$B\s+disconnect', '(end browser session)'),
    (r'\$B\s+handoff', '(browser handoff not available — use browser_task directly)'),
    (r'\$B\s+', 'Use browser_task: '),
    
    # Agent sub-agent → run_subagent
    (r'(?i)dispatch.*?Agent\s+tool', 'dispatch via run_subagent'),
    (r'(?i)spawn.*?sub-?agent', 'spawn via run_subagent'),
    (r'(?i)use the Agent tool', 'use run_subagent'),
    
    # File paths
    (r'~/.claude/skills/qstack/', ''),
    (r'~/.claude/skills/gstack/', ''),
    (r'~/.claude/skills/', ''),
    (r'~/.qstack/', '(qstack memory) '),
    (r'~/.gstack/', '(qstack memory) '),
    
    # CLAUDE.md → custom instructions
    (r'CLAUDE\.md', 'project custom instructions'),
    
    # Learnings system → Perplexity memory
    (r'qstack-learnings-search[^)]*', 'memory_search (Perplexity built-in memory)'),
    (r'qstack-learnings-log[^)]*', 'memory_update (Perplexity built-in memory)'),
    (r'gstack-learnings-search[^)]*', 'memory_search (Perplexity built-in memory)'),
    (r'gstack-learnings-log[^)]*', 'memory_update (Perplexity built-in memory)'),
    
    # Config system → Perplexity memory  
    (r'qstack-config\s+(?:get|set)\s+\S+', 'memory_search/memory_update'),
    (r'gstack-config\s+(?:get|set)\s+\S+', 'memory_search/memory_update'),
    
    # Telemetry references → remove
    (r'qstack-telemetry-\S+', ''),
    (r'gstack-telemetry-\S+', ''),
    
    # Timeline references → remove
    (r'qstack-timeline-\S+', ''),
    (r'gstack-timeline-\S+', ''),
    
    # Other binary references
    (r'qstack-slug', ''),
    (r'gstack-slug', ''),
    (r'qstack-review-log', 'memory_update'),
    (r'gstack-review-log', 'memory_update'),
    (r'qstack-review-read', 'memory_search'),
    (r'gstack-review-read', 'memory_search'),
    
    # Claude Code specific
    (r'Claude Code', 'Perplexity Computer'),
    (r'claude code', 'Perplexity Computer'),
    
    # Conductor → parallel subagents
    (r'\bConductor\b', 'parallel run_subagent calls'),
    
    # OpenClaw references
    (r'OpenClaw', 'Perplexity Computer'),
    (r'openclaw', 'perplexity-computer'),
    
    # Garry Tan attribution (keep but contextualize)
    (r"Garry Tan's", "Garry Tan's (via gstack)"),
]

# ── Helper functions ───────────────────────────────────────────

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Split SKILL.md into frontmatter dict and body."""
    if not content.startswith('---'):
        return {}, content
    
    end = content.index('---', 3)
    fm_str = content[3:end].strip()
    body = content[end + 3:].strip()
    
    try:
        fm = yaml.safe_load(fm_str)
    except yaml.YAMLError:
        fm = {}
    
    return fm or {}, body


def clean_frontmatter(fm: dict) -> dict:
    """Keep only Perplexity-compatible fields."""
    cleaned = {}
    for key in KEEP_FRONTMATTER:
        if key in fm:
            val = fm[key]
            if key == "description" and isinstance(val, str):
                # Strip "(gstack)" tag from descriptions
                val = val.replace("(gstack)", "").replace("(qstack)", "").strip()
                # Remove voice trigger lines
                val = re.sub(r'\s*Voice triggers.*$', '', val, flags=re.MULTILINE).strip()
            cleaned[key] = val
    return cleaned


def strip_boilerplate(body: str) -> str:
    """Remove shared boilerplate sections, keeping skill-specific content."""
    lines = body.split('\n')
    result = []
    skipping = False
    skip_section = None
    
    # Track which boilerplate sections we've seen
    boilerplate_set = set(BOILERPLATE_SECTIONS)
    
    # Also strip the AUTO-GENERATED comment
    in_auto_gen = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Skip auto-generated comments
        if '<!-- AUTO-GENERATED from SKILL.md.tmpl' in stripped:
            i += 1
            continue
        if '<!-- Regenerate: bun run gen:skill-docs -->' in stripped:
            i += 1
            continue
        
        # Check if this line starts a boilerplate section
        if stripped in boilerplate_set:
            skipping = True
            skip_section = stripped
            i += 1
            continue
        
        # If we're skipping, check if a new ## section starts (that's NOT boilerplate)
        if skipping and stripped.startswith('## ') and stripped not in boilerplate_set:
            skipping = False
            skip_section = None
            # Fall through to add this line
        
        if not skipping:
            result.append(line)
        
        i += 1
    
    return '\n'.join(result)


def strip_bash_blocks_in_boilerplate_context(body: str) -> str:
    """Remove bash code blocks that contain gstack/qstack preamble commands."""
    lines = body.split('\n')
    result = []
    in_bash_block = False
    is_preamble_bash = False
    bash_block_lines = []
    
    for line in lines:
        if line.strip() == '```bash' or line.strip() == '```shell':
            in_bash_block = True
            bash_block_lines = [line]
            continue
        
        if in_bash_block:
            bash_block_lines.append(line)
            if line.strip() == '```':
                # Check if this bash block is preamble-related
                block_content = '\n'.join(bash_block_lines)
                preamble_indicators = [
                    'gstack-update-check', 'qstack-update-check',
                    'gstack-config', 'qstack-config',
                    'gstack-telemetry', 'qstack-telemetry',
                    'gstack-timeline', 'qstack-timeline',
                    'gstack-slug', 'qstack-slug',
                    'gstack-learnings', 'qstack-learnings',
                    '.gstack/sessions', '.qstack/sessions',
                    'PROACTIVE:', 'TEL_PROMPTED:',
                    'SKILL_PREFIX:', 'REPO_MODE:',
                    'skill-usage.jsonl',
                ]
                if any(ind in block_content for ind in preamble_indicators):
                    # Skip this entire bash block
                    pass
                else:
                    result.extend(bash_block_lines)
                in_bash_block = False
                bash_block_lines = []
            continue
        
        result.append(line)
    
    return '\n'.join(result)


def apply_replacements(text: str) -> str:
    """Apply all tool/reference remappings."""
    for pattern, replacement in REPLACEMENTS:
        text = re.sub(pattern, replacement, text)
    return text


def clean_empty_lines(text: str) -> str:
    """Collapse 3+ consecutive empty lines to 2."""
    return re.sub(r'\n{4,}', '\n\n\n', text)


def add_qstack_header(body: str, skill_name: str) -> str:
    """Add a qstack attribution header."""
    header = (
        f"# {skill_name}\n\n"
        f"> Adapted from [gstack](https://github.com/garrytan/gstack) by Garry Tan (MIT License) "
        f"for use with Perplexity Computer.\n\n"
    )
    return header + body


def convert_skill(skill_dir: Path) -> tuple[str, dict]:
    """Convert a single gstack SKILL.md to qstack format. Returns (content, metadata)."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None, {}
    
    content = skill_md.read_text()
    fm, body = parse_frontmatter(content)
    
    skill_name = fm.get('name', skill_dir.name)
    
    # Clean frontmatter
    fm = clean_frontmatter(fm)
    if not fm.get('name') or not fm.get('description'):
        return None, {}
    
    # For tiny skills, just do replacements without boilerplate stripping
    if skill_name in TINY_SKILLS:
        body = apply_replacements(body)
        body = clean_empty_lines(body)
    else:
        # Strip shared boilerplate sections
        body = strip_boilerplate(body)
        # Strip preamble bash blocks
        body = strip_bash_blocks_in_boilerplate_context(body)
        # Apply tool/reference remappings
        body = apply_replacements(body)
        # Clean up
        body = clean_empty_lines(body)
    
    # Add attribution header
    body = add_qstack_header(body, skill_name)
    
    # Reconstruct SKILL.md
    fm_str = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False).strip()
    output = f"---\n{fm_str}\n---\n\n{body}\n"
    
    # Apply final replacements to frontmatter too (but not name field)
    # Only apply branding to description
    desc = fm.get('description', '')
    desc = desc.replace('(gstack)', '').replace('gstack', 'qstack').strip()
    
    metadata = {
        'name': fm['name'],
        'original_lines': len(content.split('\n')),
        'converted_lines': len(output.split('\n')),
        'stripped_lines': len(content.split('\n')) - len(output.split('\n')),
    }
    
    return output, metadata


# ── Main ───────────────────────────────────────────────────────

def main():
    # Find all skill directories
    skill_dirs = []
    for item in sorted(SKILLS_INPUT_DIR.iterdir()):
        if item.is_dir() and (item / "SKILL.md").exists():
            if item.name not in SKIP_SKILLS and item.name != "qstack-skills":
                # Skip non-skill directories
                if item.name not in {'docs', 'bin', 'browse', 'scripts', 'design',
                                     'extension', 'hosts', 'supabase', 'test',
                                     '.github', 'agents', 'openclaw', 'contrib'}:
                    skill_dirs.append(item)
    
    # Also handle root SKILL.md (the browse/gstack root skill) — skip it
    # It's the browse daemon infrastructure, not a methodology skill
    
    # Create output directory
    SKILLS_OUTPUT_DIR.mkdir(exist_ok=True)
    
    print(f"Converting {len(skill_dirs)} skills...\n")
    
    results = []
    for skill_dir in skill_dirs:
        name = skill_dir.name
        
        if name in SKIP_SKILLS:
            print(f"  SKIP  {name} (desktop-only)")
            continue
        
        output, meta = convert_skill(skill_dir)
        
        if output is None:
            print(f"  SKIP  {name} (missing name/description)")
            continue
        
        # Write to output directory
        out_dir = SKILLS_OUTPUT_DIR / name
        out_dir.mkdir(exist_ok=True)
        (out_dir / "SKILL.md").write_text(output)
        
        # Also copy any non-SKILL.md, non-test, non-src supporting files
        # (e.g., vendor JS for design-html)
        for sub in skill_dir.iterdir():
            if sub.name == "SKILL.md" or sub.name == "SKILL.md.tmpl":
                continue
            if sub.name in {'src', 'test', 'bin', 'scripts', 'dist', 'node_modules'}:
                continue
            if sub.is_file() and sub.suffix in {'.js', '.css', '.html', '.json', '.md'}:
                import shutil
                vendor_dir = out_dir / "vendor" if sub.parent.name == "vendor" else out_dir
                vendor_dir.mkdir(exist_ok=True)
                dest = vendor_dir / sub.name
                if not dest.exists():
                    shutil.copy2(sub, dest)
            elif sub.is_dir() and sub.name == "vendor":
                import shutil
                dest_vendor = out_dir / "vendor"
                if not dest_vendor.exists():
                    shutil.copytree(sub, dest_vendor)
        
        pct = round(meta['stripped_lines'] / max(meta['original_lines'], 1) * 100)
        print(f"  OK    {name}: {meta['original_lines']} → {meta['converted_lines']} lines ({pct}% stripped)")
        results.append(meta)
    
    print(f"\nDone. {len(results)} skills converted to {SKILLS_OUTPUT_DIR}/")
    total_orig = sum(r['original_lines'] for r in results)
    total_conv = sum(r['converted_lines'] for r in results)
    print(f"Total: {total_orig} → {total_conv} lines ({round((total_orig-total_conv)/total_orig*100)}% reduction)")


if __name__ == "__main__":
    main()
