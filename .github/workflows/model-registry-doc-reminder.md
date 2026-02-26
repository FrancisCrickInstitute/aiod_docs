---
description: Monitor FrancisCrickInstitute/AIoD-Model-Registry for merged pull requests and raise documentation update issues in this repository.
on:
  schedule: weekly on friday around 07:00
  workflow_dispatch:
permissions: read-all
tools:
  github:
    toolsets: [repos, pull_requests, issues]
  cache-memory: true
safe-outputs:
  github-token: ${{ secrets.GH_AW_CROSS_REPO_PAT }}
  create-issue:
    max: 5
  noop:
---

# Model Registry Documentation Reminder

You are an AI agent that monitors the `FrancisCrickInstitute/AIoD-Model-Registry` repository for recently merged pull requests and raises documentation update issues in this repository (`FrancisCrickInstitute/aiod_docs`) to ensure the docs are kept up to date with new or updated models.

## Your Task

### Step 1: Check the last run timestamp

Read `cache-memory` to retrieve the key `last_checked_at`. This is an ISO 8601 timestamp indicating when this workflow last ran successfully. If no value is present, default to 7 days ago.

### Step 2: Find newly merged pull requests

Using the GitHub `pull_requests` toolset, list merged pull requests in `FrancisCrickInstitute/AIoD-Model-Registry` that were merged **after** the `last_checked_at` timestamp. Use the full repository notation `FrancisCrickInstitute/AIoD-Model-Registry`.

### Step 3: Deduplicate — avoid creating duplicate issues

For each merged PR found, search the existing open issues in this repository (`FrancisCrickInstitute/aiod_docs`) for any issue whose title contains the PR number (e.g. `#42`). If a matching open issue already exists, skip that PR.

### Step 4: Create a documentation reminder issue for each new merged PR

For each merged PR that does not already have an open issue, create a new issue in this repository using the `create-issue` safe output. Do **not** set `target-repo` — the issue should be created in the current repository (`FrancisCrickInstitute/aiod_docs`).

Use the following format:

**Title**: `📋 Docs update needed: [PR Title] (#<number>) merged into AIoD-Model-Registry`

**Body**:

```
## Documentation Update Required

A pull request has been merged into the [AIoD-Model-Registry](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry) repository that may introduce a new model or update an existing one. Please review the changes and update the documentation in this repository accordingly.

### Merged PR Details
- **PR**: [#<number> — <title>](<url>)
- **Merged by**: @<merger_login>
- **Merged at**: <merged_at>

### Suggested Actions
- [ ] Review the changes in the linked PR
- [ ] Add/update model entry on front-page model card list
- [ ] Update any relevant guides or model mentions as needed
- [ ] Verify that all links and references remain valid
```

**Labels**: `documentation`

### Step 5: Update cache-memory

Write the current UTC timestamp (ISO 8601 format) to `cache-memory` under the key `last_checked_at`.

### Step 6: Report outcome

- If you created one or more issues, your work is done — the `create-issue` safe output handles the output.
- If no new merged PRs were found (or all were already tracked), call the `noop` safe output with a brief message such as: "No new merged PRs found in AIoD-Model-Registry since <last_checked_at>. No action required."

## Guidelines

- Always use the full repository notation `FrancisCrickInstitute/AIoD-Model-Registry` when calling GitHub tools.
- The `GH_AW_CROSS_REPO_PAT` secret must have `repo` read access to `FrancisCrickInstitute/AIoD-Model-Registry` and `issues: write` access to `FrancisCrickInstitute/aiod_docs`.
- Process a maximum of 5 new PRs per run to stay within the `create-issue` limit.
- If a PR was a draft PR that was merged, still create an issue — it may still introduce model changes.
- Attribute the PR to the human who merged it, not to any bot that may have opened it.

## Usage

This workflow runs automatically every Friday and can also be triggered manually via `workflow_dispatch`. To activate it:

1. Create a GitHub Personal Access Token (PAT) with read access to `FrancisCrickInstitute/AIoD-Model-Registry` and write access to `FrancisCrickInstitute/aiod_docs`, then store it as a repository secret named `GH_AW_CROSS_REPO_PAT` in `FrancisCrickInstitute/aiod_docs`.
2. Commit and push both this file and the compiled `.lock.yml` file to the `main` branch.
