# 🧠 CommitCraft — Git Communication Agent

> A **GitAgent-compliant** AI agent that turns raw git diffs into clear commit messages,
> PR descriptions, and changelogs. Built for the **GitAgent Hackathon 2026**.

---

## What it does

| Feature | Input | Output |
|---|---|---|
| **Commit Message** | `git diff` | Perfect Conventional Commit subject line |
| **PR Description** | `git diff` | Full structured PR body (Summary / Changes / Rationale / Testing) |
| **Changelog** | `git log --oneline` | Clean CHANGELOG.md entry (Added / Changed / Fixed / Removed) |
| **Score Commit** | Any commit message | Score 1-10 + improved example |

## GitAgent Structure

This agent follows the [open GitAgent standard](https://gitagent.sh):

```
commitcraft/
├── agent.yaml                      <- manifest: name, model, entrypoint, skills
├── SOUL.md                         <- agent identity, personality, mission
├── RULES.md                        <- hard constraints & formatting rules
├── app.py                          <- Streamlit + Groq frontend
├── requirements.txt
└── skills/
    ├── analyze-diff.yaml
    ├── generate-commit-msg.yaml
    ├── write-pr-description.yaml
    ├── generate-changelog.yaml
    └── score-commit-quality.yaml
```

## Quick Start — Windows with Conda

```bash
# 1. Clone this repo
git clone https://github.com/YOUR_USERNAME/commitcraft.git
cd commitcraft

# 2. Create conda environment
conda create -n commitcraft python=3.11 -y
conda activate commitcraft

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your free Groq API key (get one at https://console.groq.com — no card needed)
set GROQ_API_KEY=gsk_your_key_here

# 5. Run
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Demo

Score `"fix: update stuff"` in the Score tab.
CommitCraft gives it **2/10** and suggests `"fix(auth): handle null token on session expiry"` instead.

## Tech Stack

- **LLM:** Llama-3.3-70b-versatile via [Groq](https://console.groq.com) *(free tier)*
- **Frontend:** [Streamlit](https://streamlit.io)
- **Agent standard:** [open-gitagent spec](https://gitagent.sh)
- **Language:** Python 3.11
