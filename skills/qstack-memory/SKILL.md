---
name: qstack-memory
description: |
  Structured cross-session project knowledge for qstack. Establishes naming conventions
  for Perplexity memory so project learnings, preferences, and patterns compound over time.
  Use when the user asks "what have we learned", "project learnings", "save this pattern",
  "remember this for next time", "what do we know about this codebase", "qstack memory",
  "show learnings", or "export learnings". Also auto-invoke at the END of any qstack skill
  to store what was learned. Proactively suggest when the user asks "didn't we fix this before?"
  or "what was that pattern we used?"
---

# qstack-memory

> Replaces gstack's local JSONL learnings system with Perplexity's native cross-session memory.
> Structured tagging makes learnings searchable and compounding.

## Why This Exists

gstack stores learnings in `~/.gstack/projects/<slug>/learnings.jsonl` — a local file that
only works on one machine, in one tool. Perplexity's `memory_update` / `memory_search` is
cross-session, cross-device, and searchable by natural language. But without structure,
memory becomes a junk drawer. This skill imposes structure.

## Memory Taxonomy

Every `memory_update` call should follow this format:

```
memory_update(content="Remember: [category] [project] — [learning]")
```

### Categories

| Prefix | When to Store | Example |
|--------|--------------|---------|
| `project:` | Project-specific facts | "Remember: project:qstack uses Python for conversion scripts and SKILL.md format for skills" |
| `pattern:` | Reusable code/architecture patterns | "Remember: pattern:webhook-retry — always include idempotency key and dead-letter queue" |
| `pitfall:` | Mistakes to avoid | "Remember: pitfall:react-hydration — never inject data-attributes into SSR HTML, use Playwright locators instead" |
| `preference:` | User's style/tool preferences | "Remember: preference:pr-style — user wants PR descriptions with a 'What Changed' and 'Why' section" |
| `decision:` | Architecture or design decisions with rationale | "Remember: decision:qstack-auth — chose API key auth over OAuth for MCP server because simpler for self-hosted" |
| `codebase:` | Codebase-specific knowledge | "Remember: codebase:qstack — the skills/ directory contains upload-ready SKILL.md files, gstack-original/ has the archived source" |
| `review:` | Findings from code reviews | "Remember: review:qstack 2026-04-06 — review of sprint skill found missing error handling in subagent failure path" |
| `sprint:` | Sprint outcomes | "Remember: sprint:patient-intake 2026-04-06 — shipped PR #42, key decision was to start with top-5 payers only" |
| `connector:` | Which apps the user has connected and how they use them | "Remember: connector:github — user is bizzybae, uses api_credentials=['github'] for all gh/git commands" |

### Retrieval Patterns

When starting any qstack skill, search memory first:

```
memory_search(queries=[
  "project learnings for [project name]",
  "pitfalls and patterns for [technology/framework]",
  "user preferences for [skill type]"
])
```

This surfaces past mistakes, established patterns, and user preferences before doing any work.

## Workflows

### 1. Store a Learning (Explicit)

User says: "Remember that our API uses rate limiting with a 60-second window"

```
memory_update(content="Remember: codebase:myapp — API rate limiting uses 60-second sliding window, 100 requests per window, returns 429 with Retry-After header")
```

### 2. Store a Learning (Automatic — Post-Skill)

After any qstack skill completes, store what was learned:

**After a review:**
```
memory_update(content="Remember: review:myapp 2026-04-06 — found missing null check in webhook handler, SQL query without parameterization in search endpoint, 3 auto-fixed issues")
```

**After a sprint:**
```
memory_update(content="Remember: sprint:notifications 2026-04-06 — shipped PR #15, used WebSocket for real-time updates, Redis pub/sub for multi-server, 47 tests added")
```

**After debugging:**
```
memory_update(content="Remember: pitfall:myapp-auth — stale JWT tokens cause blank dashboard after 24h idle, fix is silent refresh on app mount before first API call")
```

### 3. Search Before Building

Before any implementation work, always run:

```
memory_search(queries=[
  "pitfalls for [this technology/pattern]",
  "past decisions about [this area of the codebase]",
  "project [name] architecture and conventions"
])
```

This prevents re-discovering known pitfalls and ensures consistency with past decisions.

### 4. Review All Learnings

User says: "What have we learned about this project?"

```
memory_search(queries=[
  "project learnings for [project]",
  "patterns and pitfalls for [project]",
  "reviews and sprints for [project]"
])
```

Present results organized by category with dates.

### 5. Prune Stale Learnings

If a learning is outdated (e.g., "we use Express" but the project migrated to Hono),
store a correction:

```
memory_update(content="Remember: project:myapp — CORRECTION: migrated from Express to Hono in April 2026, previous Express learnings are outdated")
```

Perplexity memory doesn't support deletion, so corrections override stale entries.

## Integration with Other qstack Skills

Every qstack skill should:

1. **Start** with `memory_search` for relevant project/pattern knowledge
2. **End** with `memory_update` to store what was learned
3. **Reference** past learnings when making recommendations

This creates a compounding knowledge loop: the more you use qstack, the smarter it gets
about your specific codebase, patterns, and preferences.

## Skill Graph — What to Use Next

Invoke at the end of any skill to store learnings. Search at the start to retrieve past context.

