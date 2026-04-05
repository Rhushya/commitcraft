# CommitCraft - Git Communication Agent

CommitCraft is a GitAgent-compliant AI assistant that transforms raw git changes into clear engineering communication.
It helps developers generate better commit messages, PR descriptions, changelogs, and commit quality feedback in seconds.

## Demo

- Demo video (Loom): https://www.loom.com/share/cc920094f6b445ef968d372cdb491a2f
- Repository: https://github.com/Rhushya/commitcraft

## Problem

Most developer teams face the same issues every day:

- Commit messages are often vague, like "fix" or "update stuff"
- PR descriptions are inconsistent and miss testing context
- Changelogs are manual and time-consuming to write
- Reviewers spend extra time understanding what changed and why

This reduces code review quality, slows releases, and makes git history less useful over time.

## Solution

CommitCraft converts git diffs and commit history into structured, copy-ready outputs.
Instead of writing from scratch, developers get clear, standards-based content that can be used immediately.

## Core capabilities

| Workflow | Input | Output | Value |
|---|---|---|---|
| Commit Message | git diff | One Conventional Commit subject line | Clean and searchable git history |
| PR Description | git diff | Markdown with Summary, Changes, Rationale, Testing | Faster and clearer reviews |
| Changelog | git log --oneline | Added, Changed, Fixed, Removed release notes | Faster release communication |
| Score Commit | commit message (+ optional diff) | Score 1-10 + reasoning + improved example | Better writing habits for teams |
| Release Pack | git diff (+ optional git log) | Commit + PR + changelog + score in one run | End-to-end workflow acceleration |

## Why this is useful for developers

1. Reduces repetitive writing work.
2. Improves team consistency across commits and PRs.
3. Produces practical outputs that can be pasted directly into git or GitHub.
4. Helps junior developers learn strong commit writing patterns.
5. Improves long-term maintainability of repository history.

## Why this is strong project material

1. Solves a real, daily developer pain point.
2. Demonstrates clear productivity impact in a short demo.
3. Uses an explicit rules layer to reduce hallucinations and vague output.
4. Supports both individual mode usage and one-click Release Pack generation.
5. Uses free-tier inference via Groq for easy reproducibility.

## Architecture and GitAgent alignment

CommitCraft follows the open GitAgent pattern:

```text
commitcraft/
|- agent.yaml
|- SOUL.md
|- RULES.md
|- app.py
|- requirements.txt
|- skills/
|  |- analyze-diff.yaml
|  |- generate-commit-msg.yaml
|  |- write-pr-description.yaml
|  |- generate-changelog.yaml
|  |- score-commit-quality.yaml
```

- agent.yaml: model and skill registration
- SOUL.md: identity and style
- RULES.md: hard constraints and output standards
- skills/*.yaml: modular capability definitions
- app.py: Streamlit frontend + generation orchestration

## Quick start (Windows + Conda)

### Prerequisites

- Conda installed
- Python 3.11 environment
- Free Groq API key from https://console.groq.com

### Setup

```bash
# 1) Clone and enter project
git clone https://github.com/Rhushya/commitcraft.git
cd commitcraft

# 2) Create and activate Conda environment
conda create -n commitcraft python=3.11 -y
conda activate commitcraft

# 3) Install dependencies
pip install -r requirements.txt

# 4) Save API key once in the Conda env
conda env config vars set GROQ_API_KEY=gsk_your_key_here -n commitcraft

# 5) Reactivate to load environment variables
conda deactivate
conda activate commitcraft

# 6) Run app
streamlit run app.py
```

Open: http://localhost:8501

## How to use

### Commit Message mode

- Paste git diff
- Optionally set type and scope
- Generate one Conventional Commit subject line

### PR Description mode

- Paste git diff
- Add ticket/testing notes
- Choose audience, detail level, and focus
- Generate a full PR body with required sections

### Changelog mode

- Paste git log --oneline
- Optionally set release version
- Generate release notes grouped by Added, Changed, Fixed, Removed

### Score Commit mode

- Paste a commit message
- Optionally include diff for deeper scoring
- Get score, reasoning, and improved rewrite

### Release Pack mode

- Paste diff and optional log
- Generate commit message, PR description, changelog, and score together

## Example quick test

1. Open Score Commit.
2. Paste: fix: update stuff
3. Generate score.
4. Observe low score and improved commit suggestion.
5. Move to Commit Message and paste a real diff.
6. Generate a clean Conventional Commit line.

## Guardrails

- Never invent files, function names, or ticket IDs
- Never include secrets in generated output
- Enforce structured output contracts
- Clamp overly large inputs for stable generation
- Maintain concise, factual language

## Tech stack

- Python 3.11
- Streamlit
- Groq Python SDK
- Llama-3.3-70b-versatile

## Roadmap

- VS Code extension integration for one-click generation from staged changes
- GitHub PR auto-draft integration
- Team-level style profiles
- Repo-specific terminology adaptation

## License

MIT (see LICENSE)
