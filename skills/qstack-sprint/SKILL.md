---
name: qstack-sprint
description: |
  Full sprint pipeline orchestrator for qstack. Chains Think → Plan → Build → Review → Test → Ship
  using subagents and workspace files as handoff. Use when the user asks to "run the full sprint",
  "autoplan and build", "end to end", "think plan build ship", "full pipeline", "run qstack",
  "sprint this feature", or wants to go from idea to shipped PR in one conversation. Also use when
  the user says "build this feature end to end" or "take this from idea to PR". Proactively suggest
  when the user has described a feature and seems ready to go from zero to shipped.
---

# qstack-sprint

> Perplexity Computer-native sprint orchestrator. Takes a feature from idea to shipped PR
> using the full qstack skill pipeline with subagent parallelism and workspace file handoff.

## Philosophy

gstack's power is the sprint: Think → Plan → Build → Review → Test → Ship. Each step feeds
the next. This skill replicates that pipeline natively in Perplexity Computer using `run_subagent`
for parallelism and `/home/user/workspace/qstack-sprint/` as the shared handoff directory.

The key insight: **not every feature needs every step.** A bug fix skips Think and Plan. A
greenfield feature needs all six. A design change skips Build. This skill adapts the pipeline
to the work.

## Sprint Directory

All sprint artifacts live in `/home/user/workspace/qstack-sprint/`. Each run creates a
timestamped subdirectory:

```
/home/user/workspace/qstack-sprint/
└── 2026-04-06-patient-intake/
    ├── 00-brief.md              ← User's original request + clarifications
    ├── 01-design-doc.md         ← Output of Think phase (office-hours)
    ├── 02-ceo-review.md         ← Output of Plan phase (plan-ceo-review)
    ├── 03-eng-review.md         ← Output of Plan phase (plan-eng-review)
    ├── 04-design-review.md      ← Output of Plan phase (plan-design-review) [if UI work]
    ├── 05-build-log.md          ← What was implemented, files changed
    ├── 06-review-report.md      ← Output of Review phase (review)
    ├── 07-security-report.md    ← Output of Review phase (cso) [if security-sensitive]
    ├── 08-qa-report.md          ← Output of Test phase (qa or qa-only)
    ├── 09-ship-summary.md       ← PR link, test results, changelog entry
    └── sprint-status.md         ← Live status tracker updated after each phase
```

## Workflow

### Step 1: Classify the Work

Ask the user (via `ask_user_question`) what type of work this is:

| Type | Pipeline | Phases |
|------|----------|--------|
| **Greenfield feature** | Full pipeline | Think → Plan → Build → Review → Test → Ship |
| **Enhancement** | Skip Think | Plan → Build → Review → Test → Ship |
| **Bug fix** | Investigate-first | Investigate → Build → Review → Test → Ship |
| **Design change** | Design-focused | Think → Plan (design-heavy) → Build → Design Review → Ship |
| **Security fix** | Security-focused | Investigate → Build → CSO audit → Review → Ship |

Also ask:
- **What repo?** (needed for `bash` with `api_credentials=["github"]` to clone)
- **Staging URL?** (needed for QA phase — skip QA if no URL)
- **Skip any phases?** (user may want to skip Think if they already know what to build)

### Step 2: Think Phase

Load the `office-hours` skill methodology. Run it conversationally — this phase is interactive,
not delegated to a subagent, because it requires real-time user input on the 6 forcing questions.

Save the design doc to `01-design-doc.md`.

If the user already has a design doc or clear spec, skip this phase and save their input as
`00-brief.md`.

### Step 3: Plan Phase (Parallel Reviews)

This is where subagent parallelism shines. Spawn reviews in parallel:

```
run_subagent(
  subagent_type="general_purpose",
  task_name="CEO Review",
  objective="Read /home/user/workspace/qstack-sprint/[dir]/01-design-doc.md.
    Run a CEO/founder-mode plan review using HOLD SCOPE mode (maximum rigor).
    Challenge premises, check ambition level, identify the 10-star version.
    Write your full review to /home/user/workspace/qstack-sprint/[dir]/02-ceo-review.md.
    Use markdown with clear sections: Scope Assessment, Premise Challenges,
    10-Star Vision, Recommendations, Final Verdict (APPROVED / NEEDS REVISION / RETHINK)."
)

run_subagent(
  subagent_type="general_purpose",
  task_name="Eng Review",
  objective="Read /home/user/workspace/qstack-sprint/[dir]/01-design-doc.md.
    Run an engineering manager plan review. Produce: ASCII architecture diagram,
    data flow analysis, edge case enumeration, test matrix, failure modes,
    performance concerns. Write to /home/user/workspace/qstack-sprint/[dir]/03-eng-review.md.
    End with: APPROVED / NEEDS REVISION / BLOCKING CONCERNS."
)
```

If the feature has UI work, also spawn:
```
run_subagent(
  subagent_type="general_purpose",
  task_name="Design Review",
  objective="Read /home/user/workspace/qstack-sprint/[dir]/01-design-doc.md.
    Run a design review: rate each dimension 0-10 (hierarchy, typography, spacing,
    motion, accessibility, consistency). Explain what a 10 looks like for each.
    Write to /home/user/workspace/qstack-sprint/[dir]/04-design-review.md."
)
```

Wait for all subagents to complete. Read their outputs. Present a **Review Summary** to the user:
- List any BLOCKING CONCERNS or NEEDS REVISION verdicts
- Highlight agreements across reviewers
- Ask the user to approve the plan or request changes

Update `sprint-status.md`.

### Step 4: Build Phase

Delegate to a codebase subagent:

```
run_subagent(
  subagent_type="codebase",
  task_name="Implement feature",
  metadata='{"repo_url": "https://github.com/[owner]/[repo]"}',
  objective="Implement the feature described in /home/user/workspace/qstack-sprint/[dir]/01-design-doc.md.
    The engineering review is at 03-eng-review.md — follow its architecture recommendations.
    Write tests. Commit with clear messages. Save a build log to
    /home/user/workspace/qstack-sprint/[dir]/05-build-log.md listing: files changed,
    approach taken, tests added, any deviations from the plan."
)
```

### Step 5: Review Phase

After build completes, spawn review subagents in parallel:

```
run_subagent(
  subagent_type="codebase",
  task_name="Code Review",
  metadata='{"repo_url": "https://github.com/[owner]/[repo]"}',
  objective="Load the code-review skill. Review the current branch diff against main.
    Check for: SQL safety, trust boundary violations, conditional side effects,
    missing error handling, incomplete migrations. Auto-fix obvious issues.
    Write report to /home/user/workspace/qstack-sprint/[dir]/06-review-report.md."
)
```

For security-sensitive features, also spawn:
```
run_subagent(
  subagent_type="general_purpose",
  task_name="Security Audit",
  objective="Read the build log at /home/user/workspace/qstack-sprint/[dir]/05-build-log.md.
    Run OWASP Top 10 + STRIDE threat model on the changes. Focus on the new code.
    Write to /home/user/workspace/qstack-sprint/[dir]/07-security-report.md."
)
```

### Step 6: Test Phase

If a staging URL was provided:

```
run_subagent(
  subagent_type="general_purpose",
  task_name="QA Testing",
  objective="Test the web application at [staging_url]. Use browser_task to navigate
    through the key flows affected by this feature. Check for: console errors,
    broken layouts, missing functionality, regression in existing features.
    Take screenshots of any issues found. Write a QA report to
    /home/user/workspace/qstack-sprint/[dir]/08-qa-report.md with health score,
    screenshots, and repro steps."
)
```

If no staging URL, run the test suite via bash in the codebase subagent.

### Step 7: Ship Phase

Delegate to codebase subagent:

```
run_subagent(
  subagent_type="codebase",
  task_name="Ship PR",
  metadata='{"repo_url": "https://github.com/[owner]/[repo]"}',
  objective="Sync with main, run tests, create a PR. PR description should reference
    the design doc and review findings. Save the PR link and summary to
    /home/user/workspace/qstack-sprint/[dir]/09-ship-summary.md."
)
```

### Step 8: Sprint Summary

Read all sprint artifacts. Present to the user:
- **What was built** (from build log)
- **What was reviewed** (from review + security reports)
- **What was tested** (from QA report)
- **PR link** (from ship summary)
- **Total sprint time**

Store a sprint memory entry:
```
memory_update: "Remember: qstack sprint for [feature] completed on [date].
  Repo: [repo]. PR: [link]. Key decisions: [list]. Issues found: [list]."
```

## Adapting the Pipeline

Not every sprint needs every phase. The skill should adapt:

- **If the user says "just ship it"** → skip Think and Plan, go straight to Review → Ship
- **If reviews return all APPROVED** → proceed without user gate
- **If any review says BLOCKING** → stop and present the concern before Build
- **If QA finds critical bugs** → loop back to Build, then re-test
- **If the repo has no tests** → the ship subagent should bootstrap a test framework

## Connector Enhancement

If the user has connected apps, enhance the sprint:

- **GitHub** (always): Clone repo, create PR, check CI status
- **Slack** (if connected): Post sprint summary to a channel after shipping
- **Notion** (if connected): Create a sprint log page
- **Linear/Jira** (if connected): Update ticket status at each phase
- **Gmail** (if connected): Send sprint summary to stakeholders

Check for connectors via `list_external_tools` at the start of the sprint. Don't require
them — just use them if available.

## Skill Graph — What to Use Next

Orchestrates the full pipeline. For individual phases, use the specific skill directly.

