---
name: qstack-validate
description: |
  Automated quality checker for qstack skills. Validates structural integrity,
  Perplexity Computer compatibility, cross-reference accuracy, gstack residue,
  and content quality across all installed skills. Produces a scored audit report
  with per-skill grades and an overall health score. Tracks quality across versions
  via benchmark history. Use when the user asks to "validate skills", "check skill
  quality", "audit qstack", "run qstack tests", "skill health check", "benchmark
  skills", "compare versions", or "are my skills working correctly". Proactively
  suggest after re-running the conversion scripts or uploading new skill versions.
---

# qstack-validate

> Automated quality assurance for the qstack skill library. Catches regressions,
> broken references, and compatibility issues before they affect real workflows.

## Perplexity Computer Environment

1. **Clone the qstack repo** if not already in workspace:
   `bash` with `api_credentials=["github"]`: `gh repo clone bizzybae/qstack /home/user/workspace/qstack`
2. **Run the audit script:** `bash`: `cd /home/user/workspace/qstack && python3 scripts/audit-skills.py`
3. **Read the report:** `read` the latest file in `/home/user/workspace/qstack/benchmarks/`
4. **Share with user:** `share_file` the audit report
5. **Compare versions:** `read` the benchmark history JSON to show trends

## What It Checks

### 1. Frontmatter Validation
- `name` field exists, matches Perplexity format (lowercase, hyphens, 1-64 chars)
- `description` field exists, is long enough (50+ chars), contains trigger phrases
- No gstack-only fields (`allowed-tools`, `preamble-tier`, `version`)

### 2. Perplexity Computer Preamble
- `## Perplexity Computer Environment` section exists (or skill is Perplexity-native)
- Preamble references at least 2 relevant Perplexity tools
- Perplexity-native skills (`qstack-*`) reference 3+ tools in their body

### 3. Cross-Reference Accuracy
- `## Skill Graph` section exists
- All referenced skill names are valid (exist in the library)
- No self-references
- No references to unknown skills

### 4. gstack Residue Detection
- No `$B` browse daemon commands (should be `browser_task`/`screenshot_page`)
- No `gstack-` binary references (learnings, config, telemetry, etc.)
- No `~/.gstack/` paths
- No unconverted `CLAUDE.md` references
- No preamble bash blocks

### 5. Content Quality
- Reasonable skill size (not too short, not over Perplexity's 10MB limit)
- Proper markdown structure (2+ section headings)
- No excessive blank lines (4+ consecutive)

### 6. Perplexity Tool Awareness
- Git-dependent skills reference `api_credentials=["github"]`
- Browser-dependent skills reference `browser_task`/`screenshot_page`/`js_repl`
- Memory-worthy skills reference `memory_search`/`memory_update`

## Scoring

Each issue carries a severity weight:
- **Critical** (25 pts): broken frontmatter, exceeds file size limit
- **High** (10 pts): missing preamble, unconverted browse commands, gstack binaries
- **Medium** (3 pts): missing tool references, short description, minimal preamble
- **Low** (1 pt): unnecessary fields, CLAUDE.md mentions, cosmetic issues

Score = 100 - (weighted_penalty / size_factor), where size_factor scales with skill length.

Grades: A (90+), B (75+), C (60+), D (40+), F (<40)

## Version Benchmarking

Every audit run appends to `benchmarks/benchmark-history.json`. This tracks:

```json
{
  "timestamp": "2026-04-07T00:15:11",
  "version": "v3",
  "summary": {
    "total_skills": 34,
    "total_lines": 19602,
    "avg_score": 99.6,
    "total_issues": 6,
    "by_severity": {"critical": 0, "high": 0, "medium": 5, "low": 1},
    "grade_distribution": {"A": 34}
  },
  "skills": {
    "office-hours": {"score": 100, "grade": "A", "lines": 1111, "issues": 0},
    ...
  }
}
```

To compare versions:
1. Run `read` on `benchmarks/benchmark-history.json`
2. Compare `avg_score`, `total_issues`, and `grade_distribution` across entries
3. Flag any skill whose score dropped between versions

## Workflow

1. **Full audit:** `python3 scripts/audit-skills.py` — checks all 34 skills, produces report + benchmark entry
2. **Quick check after changes:** Run audit, compare latest benchmark to previous entry
3. **After re-running converter:** Run audit to verify no regressions from upstream gstack changes
4. **After uploading new skills:** Run audit to verify new skills meet quality standards

## Skill Graph — What to Use Next

Run after modifying skills, re-running conversion scripts, or uploading new versions.

**See also:** `qstack-memory` (store audit findings), `qstack-scheduled-ops` (schedule periodic audits)
