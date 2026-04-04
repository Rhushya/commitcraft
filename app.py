import os
from textwrap import dedent
import streamlit as st
from groq import Groq

MODEL = "llama-3.3-70b-versatile"


def get_client() -> Groq:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        st.error(
            "**GROQ_API_KEY not set.**  \n"
            "**Windows (Anaconda Prompt):** `set GROQ_API_KEY=your_key`  \n"
            "Then restart: `streamlit run app.py`  \n"
            "Get a free key at https://console.groq.com"
        )
        st.stop()
    return Groq(api_key=key)


def ask(system: str, user: str, max_tokens: int = 800) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=0.2,
        max_completion_tokens=max_tokens,
        stream=False,
    )
    return resp.choices[0].message.content.strip()


BASE = (
    "You are CommitCraft — a senior engineer whose only job is to turn "
    "raw git changes into clear, concise communication.\n\n"
    "Hard rules:\n"
    "- NEVER describe changes not present in the input.\n"
    "- NEVER invent file names, function names, or ticket IDs.\n"
    "- Use short sentences and strong verbs.\n"
    "- No marketing language or buzzwords.\n"
)

COMMIT_SYS = BASE + (
    "\nOutput ONE Conventional Commit subject line ONLY — "
    "no explanation, no markdown, no quotes.\n"
    "Format: <type>(<optional scope>): <summary>\n"
    "Types: feat | fix | refactor | docs | test | chore | perf | ci | build\n"
    "Max 72 characters. No period at end. Imperative mood.\n"
)

PR_SYS = BASE + (
    "\nWrite a full PR description in Markdown with EXACTLY these sections:\n"
    "## Summary\n## Changes\n## Rationale\n## Testing\n"
    "Use bullet points under Changes and Testing.\n"
    "If no tests are mentioned, explicitly state what tests should be added.\n"
)

CHANGELOG_SYS = BASE + (
    "\nWrite a Markdown changelog grouped under:\n"
    "## Added\n## Changed\n## Fixed\n## Removed\n"
    "Use past tense (\"Added X\"). Write for external readers.\n"
    "Omit empty sections.\n"
)

SCORE_SYS = BASE + (
    "\nScore the commit message 1-10:\n"
    "  1-3: useless or misleading (\"fix\", \"changes\", \"update stuff\")\n"
    "  4-6: understandable but missing detail or wrong format\n"
    "  7-8: good with minor issues\n"
    "  9-10: excellent, team should copy it\n\n"
    "Respond in this EXACT format:\n"
    "Score: X/10\n\n"
    "Reasoning:\n"
    "- <point>\n"
    "- <point>\n\n"
    "Improved example:\n"
    "<single improved commit message>\n"
)

st.set_page_config(page_title="CommitCraft", page_icon="🧠", layout="wide")
st.markdown(
    "<style>.block-container{padding-top:1.8rem}"
    ".stTextArea textarea{font-family:monospace;font-size:13px}</style>",
    unsafe_allow_html=True,
)
st.title("🧠 CommitCraft — Git Communication Agent")
st.caption(f"Git-native AI agent · Groq free LLM (`{MODEL}`) · GitAgent Hackathon 2026")
st.divider()

with st.sidebar:
    st.header("Mode")
    mode = st.radio(
        "",
        ["📝  Commit Message", "📋  PR Description", "📦  Changelog", "🔍  Score Commit"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        "**How to use**\n"
        "1. Paste a `git diff` or git log\n"
        "2. Click Generate\n"
        "3. Copy into your terminal or PR"
    )
    st.markdown("---")
    st.markdown(f"**Free Groq key:** [console.groq.com](https://console.groq.com)\n\n**Model:** `{MODEL}`")


if mode == "📝  Commit Message":
    st.subheader("📝 Conventional Commit Message from Diff")
    diff = st.text_area(
        "Paste git diff (`git diff` or `git show`)",
        height=280,
        placeholder="diff --git a/auth.py b/auth.py\n--- a/auth.py\n+++ b/auth.py\n@@ -12,6 +12,10 @@\n ...",
    )
    c1, c2 = st.columns(2)
    ctype = c1.selectbox(
        "Preferred type (optional)",
        ["auto-detect","feat","fix","refactor","docs","test","chore","perf","ci","build"],
    )
    scope = c2.text_input("Scope (optional — e.g. auth, api, ui, cli)")

    if st.button("Generate Commit Message", type="primary", use_container_width=True):
        if not diff.strip():
            st.warning("Please paste a git diff first.")
        else:
            prompt = (
                f"Diff:\n```diff\n{diff}\n```\n"
                f"Preferred type: {ctype if ctype != 'auto-detect' else 'best fit'}\n"
                f"Scope: {scope or 'none'}\n\nReturn ONE commit subject line only."
            )
            with st.spinner("Groq is thinking..."):
                result = ask(COMMIT_SYS, prompt, max_tokens=120)
            st.success("Your commit message:")
            st.code(result, language="text")
            st.code(f'git commit -m "{result}"', language="bash")


elif mode == "📋  PR Description":
    st.subheader("📋 Full PR Description from Diff")
    diff = st.text_area(
        "Paste git diff for this PR",
        height=280,
        placeholder="diff --git a/server.js b/server.js\n...",
    )
    c1, c2 = st.columns(2)
    ticket  = c1.text_input("Ticket / Issue ID (optional — e.g. GH-42)")
    testing = c2.text_area("Tests already run (optional)", height=80,
                            placeholder="pytest passed, manual test on Windows")

    if st.button("Generate PR Description", type="primary", use_container_width=True):
        if not diff.strip():
            st.warning("Please paste a git diff first.")
        else:
            prompt = (
                f"Diff:\n```diff\n{diff}\n```\n"
                f"Ticket: {ticket or 'none'}\n"
                f"Testing notes: {testing or 'none provided'}"
            )
            with st.spinner("CommitCraft is writing your PR..."):
                result = ask(PR_SYS, prompt, max_tokens=1000)
            st.success("PR Description:")
            st.markdown(result)
            st.divider()
            st.caption("Raw Markdown — copy into your GitHub PR:")
            st.code(result, language="markdown")


elif mode == "📦  Changelog":
    st.subheader("📦 Release Changelog from Git Log")
    log = st.text_area(
        "Paste git log (`git log --oneline`)",
        height=280,
        placeholder="a1b2c3d feat: add dark mode\ne4f5g6h fix: crash on empty config\n",
    )
    version = st.text_input("Release version (optional — e.g. v1.0.0)")

    if st.button("Generate Changelog", type="primary", use_container_width=True):
        if not log.strip():
            st.warning("Please paste some commit messages first.")
        else:
            prompt = f"Commits:\n```\n{log}\n```\nRelease version: {version or 'unversioned'}"
            with st.spinner("Building changelog..."):
                result = ask(CHANGELOG_SYS, prompt, max_tokens=900)
            st.success("Changelog entry:")
            st.markdown(result)
            st.divider()
            st.caption("Raw Markdown — copy into CHANGELOG.md:")
            st.code(result, language="markdown")


elif mode == "🔍  Score Commit":
    st.subheader("🔍 Score an Existing Commit Message")
    msg = st.text_area(
        "Commit message to evaluate",
        height=80,
        placeholder="fix: update stuff",
    )
    diff = st.text_area(
        "Optional: paste the diff too for deeper evaluation",
        height=200,
        placeholder="diff --git a/config.py b/config.py\n...",
    )

    if st.button("Score My Commit", type="primary", use_container_width=True):
        if not msg.strip():
            st.warning("Please enter a commit message.")
        else:
            prompt = (
                f'Commit message:\n"""\n{msg}\n"""\n\n'
                f"Diff (may be empty):\n```diff\n{diff}\n```"
            )
            with st.spinner("Scoring..."):
                result = ask(SCORE_SYS, prompt, max_tokens=500)

            score_num = None
            for line in result.splitlines():
                if line.startswith("Score:"):
                    try:
                        score_num = int(line.split(":")[1].strip().split("/")[0])
                    except Exception:
                        pass

            if score_num is not None:
                label = (
                    "Poor — rewrite it" if score_num <= 3
                    else "Okay — could be better" if score_num <= 6
                    else "Good" if score_num <= 8
                    else "Excellent!"
                )
                st.metric("Commit Score", f"{score_num}/10", delta=label)
                st.markdown("---")

            st.markdown(result)

st.divider()
st.caption(
    "CommitCraft · GitAgent Hackathon 2026 · "
    "Streamlit + Groq · GitAgent spec: [gitagent.sh](https://gitagent.sh)"
)
