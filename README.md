# CommitCraft - Git Communication Agent

CommitCraft is a GitAgent-compliant AI assistant that turns raw git history into clean engineering communication.
It generates Conventional Commit subjects, full PR descriptions, release changelog entries, and commit quality feedback.

## Why this exists

Teams lose velocity when git history is vague.
CommitCraft fixes that by turning noisy raw diffs into concise, structured outputs that reviewers and future maintainers can trust.

## Core workflows

| Workflow | Input | Output |
|---|---|---|
| Commit Message | git diff | One Conventional Commit subject line |
| PR Description | git diff | Markdown with Summary, Changes, Rationale, Testing |
| Changelog | git log --oneline | Added/Changed/Fixed/Removed release notes |
| Score Commit | commit message (+ optional diff) | Score 1-10, reasoning, improved example |
| Release Pack | git diff (+ optional git log) | All of the above in one click |

## Why this is strong hackathon material

1. Real developer pain solved: git communication quality.
2. Practical outputs that can be pasted directly into Git and GitHub.
3. One-click Release Pack demo path that shows end-to-end value fast.
4. Rules-first design with anti-hallucination constraints in [RULES.md](RULES.md).
5. Free, fast LLM runtime on Groq for easy judging reproduction.

## Quick start (Windows + Conda)

```bash
# 1) Clone and enter folder
git clone https://github.com/Rhushya/commitcraft.git
cd commitcraft

# 2) Create and activate Conda env
conda create -n commitcraft python=3.11 -y
conda activate commitcraft

# 3) Install dependencies
pip install -r requirements.txt

# 4) Save Groq key once (persistent for this Conda env)
conda env config vars set GROQ_API_KEY=gsk_your_key_here -n commitcraft

# 5) Re-activate so env var is loaded
conda deactivate
conda activate commitcraft

# 6) Run app
streamlit run app.py
```

Open http://localhost:8501.

## 2-minute demo flow

1. Open Score Commit and input: fix: update stuff.
2. Show low score and improved example.
3. Open Commit Message and paste any real diff.
4. Show Conventional Commit output.
5. Open Release Pack and generate commit + PR + changelog in one run.

## Project structure

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

## Guardrails

- Never invent files, functions, or ticket IDs.
- Never include secrets in generated output.
- Use structured output formats that teams can review quickly.
- Clamp overly large inputs to keep generation stable.

## Tech stack

- Python 3.11
- Streamlit
- Groq Python SDK
- Llama-3.3-70b-versatile

## License

MIT
