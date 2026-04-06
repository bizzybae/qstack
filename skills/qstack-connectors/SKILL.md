---
name: qstack-connectors
description: |
  Teaches qstack skills how to leverage Perplexity Computer's 400+ app connectors
  (Slack, Gmail, Notion, Linear, Jira, Google Calendar, GitHub, etc.) to enhance
  engineering workflows. Use when the user asks to "post to Slack after shipping",
  "update the Notion board", "send a summary email", "file a bug in Linear",
  "integrate my tools", "connect my apps", "qstack connectors", or "enhance the
  workflow with my apps". Also use when any qstack skill completes and the user
  has connected apps that could receive the output. Proactively suggest when you
  detect connected apps via list_external_tools that could enhance the current workflow.
---

# qstack-connectors

> Perplexity Computer-native capability. gstack cannot integrate with external apps
> (beyond MCP config). qstack weaves your connected apps into every phase of the sprint.

## Philosophy

The best engineering workflows don't end at the PR. They update the ticket, notify
the team, log the decision, and close the loop. gstack stops at the terminal.
qstack continues into your actual tools.

**Rule: always check, never assume.** At the start of any connector-enhanced workflow,
call `list_external_tools` to see what's actually connected. Never tell the user
"I'll post to Slack" if Slack isn't connected. Offer to connect it if it's available
but disconnected.

## Connector Discovery

At the start of any qstack sprint or skill that could benefit from integrations:

```python
# Step 1: Check what's connected
list_external_tools(queries=["slack", "notion", "linear", "jira", "gmail", "calendar", "github"])

# Step 2: For each connected service, describe available tools
describe_external_tools(source_id="slack_mcp", tool_names=["post_message"])
```

## Integration Recipes

### After Shipping (ship / land-and-deploy)

| Connected App | What to Do |
|--------------|-----------|
| **Slack** | Post a ship notification to the team channel: PR link, what changed, who reviewed |
| **Notion** | Create or update a ship log page in the engineering database |
| **Linear/Jira** | Move the ticket to "Done", add a comment with the PR link |
| **Gmail** | Send a release summary to stakeholders (if requested) |
| **Google Calendar** | Create a "deployed [feature]" event for the team timeline |

**Example — Slack ship notification:**
```
call_external_tool(
  tool_name="post_message",
  source_id="slack_mcp",
  arguments={
    "channel": "#engineering",
    "text": "🚢 Shipped: [Feature Name]\nPR: [link]\nWhat changed: [summary]\nTests: [count] passing\nReviewed by: [reviewer]"
  }
)
```

### After Review (review / cso)

| Connected App | What to Do |
|--------------|-----------|
| **Slack** | Post critical findings to a security or review channel |
| **Linear/Jira** | Create tickets for each finding that needs follow-up |
| **Notion** | Add review findings to the project's decision log |

### After QA (qa / qa-only)

| Connected App | What to Do |
|--------------|-----------|
| **Linear/Jira** | Create bug tickets for each issue found, with repro steps and screenshots |
| **Slack** | Post QA summary to the relevant channel |
| **Notion** | Update the QA tracking database |

### After Retro (retro)

| Connected App | What to Do |
|--------------|-----------|
| **Notion** | Create a retro page in the team wiki with stats, highlights, and action items |
| **Slack** | Post the retro summary to #engineering |
| **Gmail** | Email the retro to the team (if requested) |
| **Google Calendar** | Add action items as calendar reminders |

### Before Building (office-hours / plan-*)

| Connected App | What to Do |
|--------------|-----------|
| **Gmail** | Search for customer feedback emails related to the feature |
| **Slack** | Search for team discussions about the problem |
| **Notion** | Pull existing specs, design docs, or research |
| **Linear/Jira** | Pull the ticket details, acceptance criteria, related tickets |
| **Google Calendar** | Check if there's a deadline or review meeting scheduled |

**Example — pulling context before office-hours:**
```
# Search email for customer complaints about the area
run_subagent(
  subagent_type="general_purpose",
  task_name="Gather context from connected apps",
  objective="Search for context about [feature area]:
    1. Search Gmail for emails mentioning [keywords] from the past 30 days
    2. Search Notion for pages about [feature area]
    3. Search Slack for messages about [keywords] in the past 2 weeks
    Save a summary to /home/user/workspace/qstack-sprint/context-from-apps.md"
)
```

## Connector-Aware Sprint Enhancements

When `qstack-sprint` detects connected apps, it should automatically:

1. **Pull context** — before Think phase, search connected apps for relevant discussions, tickets, and docs
2. **Update status** — at each phase transition, update the ticket status in Linear/Jira if connected
3. **Notify** — after Ship phase, post to Slack and/or email stakeholders
4. **Log** — after Sprint completes, create a Notion page with the full sprint artifacts

## Setting Up Connectors

If a user wants to enhance their workflow but hasn't connected apps:

1. `list_external_tools(queries=["slack"])` — find the Slack connector
2. If status is DISCONNECTED: `call_external_tool(tool_name="connect", source_id="slack_mcp")`
3. This shows an auth popup — user clicks through OAuth
4. After connection, tools become available

**Never pressure users to connect apps.** Connectors are enhancements, not requirements.
Every qstack skill works without any connected apps.

## Design Principles

1. **Check, don't assume** — always `list_external_tools` before referencing a connector
2. **Enhance, don't require** — every skill must work without connectors
3. **Confirm before posting** — always use `confirm_action` before sending messages, emails, or creating tickets
4. **Relevant only** — don't post to Slack about a typo fix. Use judgment about what's worth notifying.
5. **User's channels** — ask which Slack channel, which Notion database, which Linear project. Don't guess.
