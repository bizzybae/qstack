---
description: 'Manage project learnings. Review, search, prune, and export what gstack
  has learned across sessions. Use when asked to "what have we learned",
  "show learnings", "prune stale learnings", or "export learnings".
  Proactively suggest when the user asks about past patterns or wonders
  "didn''t we fix this before?"'
name: learn
---

# learn

> Adapted from [gstack](https://github.com/garrytan/gstack) by Garry Tan (MIT License) for use with Perplexity Computer.

## Perplexity Computer Environment

In Perplexity Computer, learnings are stored in the platform's native memory system:

1. **Store:** `memory_update(content="Remember: [category]:[project] — [learning]")`
2. **Search:** `memory_search(queries=["project learnings for [project]"])`
3. **Categories:** project, pattern, pitfall, preference, decision, codebase, review, sprint
4. **See `qstack-memory`** for the full taxonomy and retrieval strategies


## Detect command

Parse the user's input to determine which command to run:

- `/learn` (no arguments) → **Show recent**
- `/learn search <query>` → **Search**
- `/learn prune` → **Prune**
- `/learn export` → **Export**
- `/learn stats` → **Stats**
- `/learn add` → **Manual add**

---

## Show recent (default)

Show the most recent 20 learnings, grouped by type.


Present the output in a readable format. If no learnings exist, tell the user:
"No learnings recorded yet. As you use /review, /ship, /investigate, and other skills,
qstack will automatically capture patterns, pitfalls, and insights it discovers."

---

## Search


Replace USER_QUERY with the user's search terms. Present results clearly.

---

## Prune

Check learnings for staleness and contradictions.


For each learning in the output:

1. **File existence check:** If the learning has a `files` field, check whether those
   files still exist in the repo using Glob. If any referenced files are deleted, flag:
   "STALE: [key] references deleted file [path]"

2. **Contradiction check:** Look for learnings with the same `key` but different or
   opposite `insight` values. Flag: "CONFLICT: [key] has contradicting entries —
   [insight A] vs [insight B]"

Present each flagged entry via AskUserQuestion:
- A) Remove this learning
- B) Keep it
- C) Update it (I'll tell you what to change)

For removals, read the learnings.jsonl file and remove the matching line, then write
back. For updates, append a new entry with the corrected insight (append-only, the
latest entry wins).

---

## Export

Export learnings as markdown suitable for adding to project custom instructions or project documentation.


Format the output as a markdown section:

```markdown
## Project Learnings

### Patterns
- **[key]**: [insight] (confidence: N/10)

### Pitfalls
- **[key]**: [insight] (confidence: N/10)

### Preferences
- **[key]**: [insight]

### Architecture
- **[key]**: [insight] (confidence: N/10)
```

Present the formatted output to the user. Ask if they want to append it to project custom instructions
or save it as a separate file.

---

## Stats

Show summary statistics about the project's learnings.


Present the stats in a readable table format.

---

## Manual add

The user wants to manually add a learning. Use AskUserQuestion to gather:
1. Type (pattern / pitfall / preference / architecture / tool)
2. A short key (2-5 words, kebab-case)
3. The insight (one sentence)
4. Confidence (1-10)
5. Related files (optional)

Then log it:

## Skill Graph — What to Use Next

`qstack-memory` provides structured naming conventions for Perplexity's built-in memory system.

**See also:** `qstack-memory`

