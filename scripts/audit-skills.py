#!/usr/bin/env python3
"""
audit-skills.py — Sprint-style Review phase for all qstack skills.

Validates structural integrity, cross-reference accuracy, Perplexity compatibility,
and produces a scored report with per-skill grades and an overall health score.

This is the foundation of the qstack-validate skill and version benchmark.
"""

import re
import json
import yaml
from pathlib import Path
from datetime import datetime

SKILLS_DIR = Path(__file__).parent.parent / "skills"
REPORT_DIR = Path(__file__).parent.parent / "benchmarks"

# All valid skill names for cross-reference checking
VALID_SKILLS = set()

# ── CHECK FUNCTIONS ────────────────────────────────────────────

def check_frontmatter(content: str, name: str) -> list[dict]:
    """Validate YAML frontmatter structure."""
    issues = []
    
    if not content.startswith("---"):
        issues.append({"severity": "critical", "check": "frontmatter", "msg": "Missing YAML frontmatter"})
        return issues
    
    try:
        end = content.index("---", 3)
        fm_str = content[3:end].strip()
        fm = yaml.safe_load(fm_str)
    except (ValueError, yaml.YAMLError) as e:
        issues.append({"severity": "critical", "check": "frontmatter", "msg": f"Invalid YAML: {e}"})
        return issues
    
    if not fm:
        issues.append({"severity": "critical", "check": "frontmatter", "msg": "Empty frontmatter"})
        return issues
    
    if "name" not in fm:
        issues.append({"severity": "critical", "check": "frontmatter", "msg": "Missing 'name' field"})
    elif not isinstance(fm["name"], str) or not re.match(r'^[a-z0-9][a-z0-9-]{0,63}$', fm["name"]):
        issues.append({"severity": "high", "check": "frontmatter", "msg": f"Name '{fm.get('name')}' may not match Perplexity requirements (lowercase, hyphens, 1-64 chars)"})
    
    if "description" not in fm:
        issues.append({"severity": "critical", "check": "frontmatter", "msg": "Missing 'description' field"})
    elif isinstance(fm["description"], str):
        desc = fm["description"]
        if len(desc) < 50:
            issues.append({"severity": "medium", "check": "frontmatter", "msg": f"Description too short ({len(desc)} chars) — may not auto-activate reliably"})
        # Check for trigger phrases
        triggers = ["use when", "activate when", "proactively suggest", "invoke"]
        if not any(t in desc.lower() for t in triggers):
            issues.append({"severity": "medium", "check": "frontmatter", "msg": "Description lacks trigger phrases (Use when..., Proactively suggest...)"})
    
    # Check for gstack-only fields that should have been stripped
    gstack_fields = ["allowed-tools", "preamble-tier", "version"]
    for field in gstack_fields:
        if field in fm:
            issues.append({"severity": "low", "check": "frontmatter", "msg": f"Contains gstack-only field '{field}' (harmless but unnecessary)"})
    
    return issues


# Skills that are natively Perplexity-aware (don't need a preamble heading)
PERPLEXITY_NATIVE_SKILLS = {"qstack-sprint", "qstack-memory", "qstack-scheduled-ops", "qstack-connectors", "qstack-validate", "qstack-package"}

def check_perplexity_preamble(content: str, name: str) -> list[dict]:
    """Check for Perplexity Computer environment section."""
    issues = []
    
    # Perplexity-native skills don't need a separate preamble heading
    if name in PERPLEXITY_NATIVE_SKILLS:
        # Instead, verify they reference enough Perplexity tools in their body
        perplexity_tools = ["bash", "browser_task", "screenshot_page", "memory_search",
                           "memory_update", "run_subagent", "api_credentials", "search_web",
                           "fetch_url", "deploy_website", "share_file", "js_repl",
                           "ask_user_question", "schedule_cron", "list_external_tools"]
        found = [t for t in perplexity_tools if t in content]
        if len(found) < 3:
            issues.append({"severity": "medium", "check": "preamble", "msg": f"Perplexity-native skill only references {len(found)} tools — expected 3+"})
        return issues
    
    if "## Perplexity Computer Environment" not in content:
        issues.append({"severity": "high", "check": "preamble", "msg": "Missing '## Perplexity Computer Environment' section"})
    else:
        # Check preamble quality
        preamble_start = content.index("## Perplexity Computer Environment")
        # Find end (next ## heading or EOF)
        next_heading = re.search(r'\n## [^P]', content[preamble_start + 10:])
        if next_heading:
            preamble_text = content[preamble_start:preamble_start + 10 + next_heading.start()]
        else:
            preamble_text = content[preamble_start:]
        
        # Check for key Perplexity tool references
        perplexity_tools = ["bash", "browser_task", "screenshot_page", "memory_search", 
                           "memory_update", "run_subagent", "api_credentials", "search_web",
                           "fetch_url", "deploy_website", "share_file", "js_repl",
                           "ask_user_question", "schedule_cron", "list_external_tools"]
        found_tools = [t for t in perplexity_tools if t in preamble_text]
        if len(found_tools) < 2:
            issues.append({"severity": "medium", "check": "preamble", "msg": f"Preamble references only {len(found_tools)} Perplexity tools — may need more specific guidance"})
    
    return issues


def check_crossrefs(content: str, name: str) -> list[dict]:
    """Validate skill graph cross-references."""
    issues = []
    
    if "## Skill Graph" not in content:
        issues.append({"severity": "high", "check": "crossref", "msg": "Missing '## Skill Graph' section"})
        return issues
    
    # Extract referenced skill names from crossref section
    crossref_start = content.index("## Skill Graph")
    crossref_text = content[crossref_start:]
    
    referenced = re.findall(r'`([a-z0-9-]+)`', crossref_text)
    for ref in referenced:
        if ref in VALID_SKILLS and ref != name:
            continue  # valid reference
        elif ref in VALID_SKILLS and ref == name:
            issues.append({"severity": "low", "check": "crossref", "msg": f"Self-reference to `{ref}` in skill graph"})
        elif ref not in VALID_SKILLS and ref not in [
            "github", "python", "bash", "node", "bun", "npm",  # not skill names
            "memory_search", "memory_update", "browser_task",  # tool names
            "run_subagent", "api_credentials", "schedule_cron",
            "screenshot_page", "fetch_url", "deploy_website",
            "share_file", "js_repl", "ask_user_question",
            "list_external_tools", "confirm_action", "search_web",
        ]:
            issues.append({"severity": "medium", "check": "crossref", "msg": f"References unknown skill `{ref}`"})
    
    return issues


# Skills that document gstack patterns (references are intentional, not residue)
DOCUMENTATION_SKILLS = {"qstack-validate", "qstack-package"}

def check_gstack_residue(content: str, name: str) -> list[dict]:
    """Check for remaining gstack-specific patterns that shouldn't be there."""
    issues = []
    
    # Skills that document gstack patterns are exempt from residue checks
    if name in DOCUMENTATION_SKILLS:
        return issues
    
    # $B browse daemon commands (should be converted)
    b_commands = re.findall(r'\$B\s+\w+', content)
    for cmd in b_commands:
        if "browser_task" not in content[max(0, content.index(cmd)-100):content.index(cmd)]:
            issues.append({"severity": "high", "check": "gstack_residue", "msg": f"Unconverted browse command: {cmd}"})
    
    # gstack binary references
    gstack_bins = re.findall(r'gstack-(?:learnings|config|telemetry|timeline|slug|review|analytics|upgrade)\S*', content)
    for ref in gstack_bins:
        issues.append({"severity": "high", "check": "gstack_residue", "msg": f"Remaining gstack binary reference: {ref}"})
    
    # ~/.gstack/ paths (should be converted to memory or removed)
    if "~/.gstack/" in content:
        issues.append({"severity": "medium", "check": "gstack_residue", "msg": "Contains ~/.gstack/ path reference"})
    
    # CLAUDE.md references that aren't in the "ignore these files" context
    claude_md_refs = [m.start() for m in re.finditer(r'CLAUDE\.md', content)]
    for pos in claude_md_refs:
        context = content[max(0, pos-200):pos+200]
        if "Do NOT read" not in context and "ignore" not in context.lower() and "custom instructions" not in context.lower():
            issues.append({"severity": "low", "check": "gstack_residue", "msg": "CLAUDE.md reference outside of ignore-instructions context"})
    
    # Preamble bash blocks (should have been stripped)
    if "gstack-update-check" in content or "gstack-config get" in content:
        issues.append({"severity": "high", "check": "gstack_residue", "msg": "Contains gstack preamble bash commands"})
    
    return issues


def check_content_quality(content: str, name: str) -> list[dict]:
    """Check for content quality issues."""
    issues = []
    
    lines = content.split("\n")
    total_lines = len(lines)
    
    # Check for reasonable size
    if total_lines < 20:
        issues.append({"severity": "medium", "check": "quality", "msg": f"Very short skill ({total_lines} lines) — may lack sufficient guidance"})
    
    # Check for 4+ consecutive blank lines (formatting issue)
    blank_streak = 0
    for i, line in enumerate(lines):
        if line.strip() == "":
            blank_streak += 1
            if blank_streak >= 4:
                issues.append({"severity": "low", "check": "quality", "msg": f"4+ consecutive blank lines at line {i+1}"})
                break
        else:
            blank_streak = 0
    
    # Check file size (Perplexity max 10MB)
    size_bytes = len(content.encode('utf-8'))
    if size_bytes > 10_000_000:
        issues.append({"severity": "critical", "check": "quality", "msg": f"File exceeds Perplexity 10MB limit ({size_bytes} bytes)"})
    elif size_bytes > 5_000_000:
        issues.append({"severity": "medium", "check": "quality", "msg": f"File approaching Perplexity 10MB limit ({size_bytes} bytes)"})
    
    # Check for markdown structure (should have at least a few ## headings)
    headings = [l for l in lines if l.startswith("## ")]
    if len(headings) < 2:
        issues.append({"severity": "medium", "check": "quality", "msg": f"Only {len(headings)} section headings — may lack structure"})
    
    return issues


def check_perplexity_tool_awareness(content: str, name: str) -> list[dict]:
    """Check if the skill references Perplexity-specific tools where appropriate."""
    issues = []
    
    # Skills that should reference git tools
    git_skills = {"review", "ship", "retro", "document-release", "land-and-deploy", 
                  "checkpoint", "cso", "investigate"}
    if name in git_skills and 'api_credentials=["github"]' not in content and "api_credentials" not in content:
        issues.append({"severity": "medium", "check": "tool_awareness", "msg": "Git-dependent skill doesn't mention api_credentials=[\"github\"]"})
    
    # Skills that should reference browser tools
    browser_skills = {"qa", "qa-only", "design-review", "devex-review", "benchmark", 
                      "canary", "design-shotgun"}
    if name in browser_skills:
        browser_refs = ["browser_task", "screenshot_page", "js_repl"]
        found = [t for t in browser_refs if t in content]
        if not found:
            issues.append({"severity": "high", "check": "tool_awareness", "msg": "Browser-dependent skill doesn't reference any Perplexity browser tools"})
    
    # Skills that should reference memory
    memory_skills = {"learn", "retro", "review", "ship", "cso", "investigate", 
                     "office-hours", "checkpoint"}
    if name in memory_skills:
        if "memory_search" not in content and "memory_update" not in content:
            issues.append({"severity": "medium", "check": "tool_awareness", "msg": "Should reference memory_search/memory_update for cross-session continuity"})
    
    return issues


# ── SCORING ────────────────────────────────────────────────────

SEVERITY_WEIGHTS = {
    "critical": 25,
    "high": 10,
    "medium": 3,
    "low": 1,
}

def score_skill(issues: list[dict], total_lines: int) -> dict:
    """Calculate a health score for a skill. 100 = perfect, 0 = broken."""
    penalty = sum(SEVERITY_WEIGHTS.get(i["severity"], 0) for i in issues)
    # Scale penalty relative to skill size (larger skills get more leeway)
    size_factor = max(1, total_lines / 200)
    adjusted_penalty = penalty / size_factor
    score = max(0, round(100 - adjusted_penalty))
    
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"
    
    return {"score": score, "grade": grade, "penalty": penalty, "issue_count": len(issues)}


# ── MAIN ───────────────────────────────────────────────────────

def audit_all_skills() -> dict:
    """Run the full audit and return structured results."""
    
    # First pass: collect all valid skill names
    for d in SKILLS_DIR.iterdir():
        if d.is_dir() and (d / "SKILL.md").exists():
            VALID_SKILLS.add(d.name)
    
    results = {}
    
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
            continue
        
        name = skill_dir.name
        content = (skill_dir / "SKILL.md").read_text()
        total_lines = len(content.split("\n"))
        
        # Run all checks
        issues = []
        issues.extend(check_frontmatter(content, name))
        issues.extend(check_perplexity_preamble(content, name))
        issues.extend(check_crossrefs(content, name))
        issues.extend(check_gstack_residue(content, name))
        issues.extend(check_content_quality(content, name))
        issues.extend(check_perplexity_tool_awareness(content, name))
        
        scoring = score_skill(issues, total_lines)
        
        results[name] = {
            "lines": total_lines,
            "size_bytes": len(content.encode('utf-8')),
            "issues": issues,
            **scoring,
        }
    
    return results


def generate_report(results: dict) -> str:
    """Generate a markdown audit report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Overall stats
    total_skills = len(results)
    total_issues = sum(r["issue_count"] for r in results.values())
    avg_score = round(sum(r["score"] for r in results.values()) / total_skills, 1)
    total_lines = sum(r["lines"] for r in results.values())
    
    by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for r in results.values():
        for i in r["issues"]:
            by_severity[i["severity"]] += 1
    
    grade_dist = {}
    for r in results.values():
        g = r["grade"]
        grade_dist[g] = grade_dist.get(g, 0) + 1
    
    lines = [
        f"# qstack Skill Audit Report",
        f"",
        f"**Date:** {timestamp}",
        f"**Version:** v3 (preambles + cross-refs)",
        f"**Skills audited:** {total_skills}",
        f"**Total lines:** {total_lines:,}",
        f"",
        f"## Overall Health",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Average score | **{avg_score}/100** |",
        f"| Total issues | {total_issues} |",
        f"| Critical | {by_severity['critical']} |",
        f"| High | {by_severity['high']} |",
        f"| Medium | {by_severity['medium']} |",
        f"| Low | {by_severity['low']} |",
        f"",
        f"**Grade distribution:** " + ", ".join(f"{g}: {c}" for g, c in sorted(grade_dist.items())),
        f"",
        f"## Per-Skill Scores",
        f"",
        f"| Skill | Lines | Score | Grade | Issues |",
        f"|-------|-------|-------|-------|--------|",
    ]
    
    for name in sorted(results.keys(), key=lambda n: results[n]["score"]):
        r = results[name]
        lines.append(f"| `{name}` | {r['lines']} | {r['score']}/100 | {r['grade']} | {r['issue_count']} |")
    
    lines.append("")
    
    # Detail section for skills with issues
    skills_with_issues = [(n, r) for n, r in sorted(results.items()) if r["issues"]]
    if skills_with_issues:
        lines.append("## Issues by Skill")
        lines.append("")
        
        for name, r in sorted(skills_with_issues, key=lambda x: x[1]["score"]):
            if not r["issues"]:
                continue
            lines.append(f"### `{name}` — {r['score']}/100 ({r['grade']})")
            lines.append("")
            for issue in r["issues"]:
                icon = {"critical": "!!!", "high": "!!", "medium": "!", "low": "~"}[issue["severity"]]
                lines.append(f"- [{icon}] **{issue['severity'].upper()}** ({issue['check']}): {issue['msg']}")
            lines.append("")
    
    return "\n".join(lines)


def generate_benchmark_entry(results: dict) -> dict:
    """Generate a JSON benchmark entry for version tracking."""
    timestamp = datetime.now().isoformat()
    
    total_skills = len(results)
    avg_score = round(sum(r["score"] for r in results.values()) / total_skills, 1)
    total_lines = sum(r["lines"] for r in results.values())
    total_issues = sum(r["issue_count"] for r in results.values())
    
    by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for r in results.values():
        for i in r["issues"]:
            by_severity[i["severity"]] += 1
    
    grade_dist = {}
    for r in results.values():
        g = r["grade"]
        grade_dist[g] = grade_dist.get(g, 0) + 1
    
    per_skill = {}
    for name, r in results.items():
        per_skill[name] = {
            "score": r["score"],
            "grade": r["grade"],
            "lines": r["lines"],
            "issues": r["issue_count"],
        }
    
    return {
        "timestamp": timestamp,
        "version": "v3",
        "summary": {
            "total_skills": total_skills,
            "total_lines": total_lines,
            "avg_score": avg_score,
            "total_issues": total_issues,
            "by_severity": by_severity,
            "grade_distribution": grade_dist,
        },
        "skills": per_skill,
    }


def main():
    REPORT_DIR.mkdir(exist_ok=True)
    
    print("Running qstack skill audit...\n")
    results = audit_all_skills()
    
    # Generate markdown report
    report = generate_report(results)
    report_path = REPORT_DIR / f"audit-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    report_path.write_text(report)
    
    # Generate benchmark JSON entry
    benchmark = generate_benchmark_entry(results)
    
    # Append to benchmark history
    history_path = REPORT_DIR / "benchmark-history.json"
    if history_path.exists():
        history = json.loads(history_path.read_text())
    else:
        history = []
    history.append(benchmark)
    history_path.write_text(json.dumps(history, indent=2))
    
    # Print summary
    s = benchmark["summary"]
    print(f"Skills: {s['total_skills']}")
    print(f"Lines:  {s['total_lines']:,}")
    print(f"Score:  {s['avg_score']}/100")
    print(f"Issues: {s['total_issues']} (C:{s['by_severity']['critical']} H:{s['by_severity']['high']} M:{s['by_severity']['medium']} L:{s['by_severity']['low']})")
    print(f"Grades: {s['grade_distribution']}")
    print(f"\nReport: {report_path}")
    print(f"Benchmark: {history_path}")
    
    # Print per-skill scores sorted worst to best
    print("\n--- Per-Skill Scores ---")
    for name in sorted(results.keys(), key=lambda n: results[n]["score"]):
        r = results[name]
        issues_str = f" ({r['issue_count']} issues)" if r["issues"] else ""
        print(f"  {r['grade']}  {r['score']:3d}  {name}{issues_str}")


if __name__ == "__main__":
    main()
