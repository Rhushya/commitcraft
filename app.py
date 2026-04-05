import os
import re
from datetime import datetime
import streamlit as st
from groq import Groq

MODEL = "llama-3.3-70b-versatile"
MAX_INPUT_CHARS = 22000
CONVENTIONAL_RE = re.compile(
    r"^(feat|fix|refactor|docs|test|chore|perf|ci|build)(\([^)]+\))?: .{1,72}$"
)


def get_client() -> Groq:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        st.error(
            "**GROQ_API_KEY not set.**  \n"
            "Set it once for your Conda env:  \n"
            "`conda env config vars set GROQ_API_KEY=your_key -n commitcraft`  \n"
            "Then reopen terminal and run: `conda activate commitcraft`"
        )
        st.caption("Get a free key at https://console.groq.com")
        st.stop()
    return Groq(api_key=key)


def create_completion(client: Groq, system: str, user: str, max_tokens: int):
    common_args = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "stream": False,
    }

    # Groq SDK versions may use max_tokens or max_completion_tokens.
    for token_arg in ("max_tokens", "max_completion_tokens"):
        try:
            return client.chat.completions.create(
                **common_args,
                **{token_arg: max_tokens},
            )
        except TypeError as err:
            if "unexpected keyword argument" in str(err):
                continue
            raise

    # Final fallback if both token params are unsupported.
    return client.chat.completions.create(**common_args)


def ask(system: str, user: str, max_tokens: int = 800) -> str:
    client = get_client()
    try:
        resp = create_completion(client, system, user, max_tokens)
    except Exception as err:
        st.error("Groq request failed. Please check your API key, model access, and internet connection.")
        with st.expander("Technical details"):
            st.code(str(err))
        st.stop()

    content = resp.choices[0].message.content
    if not content:
        st.warning("Groq returned an empty response. Please try again.")
        st.stop()

    return content.strip()


def clamp_input(text: str, label: str) -> str:
    if len(text) <= MAX_INPUT_CHARS:
        return text
    st.warning(
        f"{label} is long. Using the first {MAX_INPUT_CHARS:,} characters to keep generation stable."
    )
    return text[:MAX_INPUT_CHARS]


def extract_score_num(result: str):
    for line in result.splitlines():
        if line.lower().startswith("score:"):
            try:
                return int(line.split(":")[1].strip().split("/")[0])
            except Exception:
                return None
    return None


def show_download(label: str, content: str, file_name: str, mime: str):
    st.download_button(
        label=label,
        data=content,
        file_name=file_name,
        mime=mime,
        use_container_width=True,
        key=f"dl-{file_name}",
    )


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


SAMPLE_COMMIT_DIFF = """diff --git a/auth.py b/auth.py
--- a/auth.py
+++ b/auth.py
@@ -10,6 +10,9 @@ def login(email, password):
-    token = api_login(email, password)
+    if not email or not password:
+        raise ValueError(\"email and password required\")
+    token = api_login(email, password)
     return token"""

SAMPLE_PR_DIFF = """diff --git a/cache.py b/cache.py
--- a/cache.py
+++ b/cache.py
@@ -1,8 +1,16 @@
+from time import time
 _store = {}
+_ttl = 300

 def set_value(key, value):
-    _store[key] = value
+    _store[key] = (value, time())

 def get_value(key):
-    return _store.get(key)
+    item = _store.get(key)
+    if not item:
+        return None
+    value, created = item
+    if time() - created > _ttl:
+        return None
+    return value"""

SAMPLE_LOG = """a1b2c3d feat: add commit score meter
b2c3d4e fix(api): handle missing GROQ_API_KEY message
c3d4e5f refactor(ui): split mode panels into helpers
d4e5f6a docs: add windows conda setup section"""

SAMPLE_SCORE_MESSAGE = "fix: update stuff"


def rerun_app():
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()


def render_input_toolbar(text_key: str, sample_value: str):
    b1, b2 = st.columns(2)
    if b1.button("Load sample", key=f"load-{text_key}", use_container_width=True):
        st.session_state[text_key] = sample_value
        rerun_app()
    if b2.button("Clear", key=f"clear-{text_key}", use_container_width=True):
        st.session_state[text_key] = ""
        rerun_app()


def mode_help(selected_mode: str) -> str:
    help_map = {
        "Commit Message": "Create one clean Conventional Commit line from a diff.",
        "PR Description": "Generate a full, structured PR body with testing notes.",
        "Changelog": "Build release-ready changelog text from commit history.",
        "Release Pack": "Generate commit, PR, changelog, and quality score in one run.",
        "Score Commit": "Evaluate commit quality and get a stronger rewrite.",
    }
    return help_map.get(selected_mode, "")

st.set_page_config(page_title="CommitCraft", layout="wide")
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1120px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    .stTextArea textarea {
        font-family: Consolas, "Courier New", monospace;
        font-size: 13px;
    }
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 48%, #0ea5e9 100%);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.8rem;
        color: #f8fafc;
    }
    .hero h1 {
        margin: 0;
        font-size: 1.6rem;
        line-height: 1.25;
    }
    .hero p {
        margin: 0.4rem 0 0 0;
        color: #dbeafe;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="hero">
      <h1>CommitCraft - Git Communication Agent</h1>
      <p>Turn raw git changes into clean commit history, PR narratives, and release notes in seconds.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(f"Git-native AI agent · Groq free LLM ({MODEL}) · GitAgent Hackathon 2026")
stat1, stat2, stat3 = st.columns(3)
stat1.metric("Workflows", "5")
stat2.metric("Model", MODEL)
stat3.metric("Output Types", "Commit, PR, Changelog")
st.divider()

with st.sidebar:
    st.header("Mode")
    mode = st.radio(
        "Select mode",
        [
            "Commit Message",
            "PR Description",
            "Changelog",
            "Release Pack",
            "Score Commit",
        ],
        label_visibility="visible",
    )
    st.markdown("---")
    if os.environ.get("GROQ_API_KEY", ""):
        st.success("API key detected in environment")
    else:
        st.warning("GROQ_API_KEY is not loaded")
    st.markdown("---")
    st.caption(mode_help(mode))
    st.markdown("---")
    st.markdown(
        "**How to use**\n"
        "1. Paste a `git diff` or `git log`\n"
        "2. Pick a mode (or use Release Pack)\n"
        "3. Generate, copy, or download output"
    )
    st.markdown("---")
    st.markdown(
        f"**Free Groq key:** [console.groq.com](https://console.groq.com)\n\n"
        f"**Model:** `{MODEL}`\n\n"
        "Tip: activate your Conda env before running Streamlit."
    )


if mode == "Commit Message":
    st.subheader("Conventional Commit Message from Diff")
    st.caption("Best for converting a raw diff into one high-quality commit subject line.")
    diff = st.text_area(
        "Paste git diff (`git diff` or `git show`)",
        height=280,
        placeholder="diff --git a/auth.py b/auth.py\n--- a/auth.py\n+++ b/auth.py\n@@ -12,6 +12,10 @@\n ...",
        key="commit-diff",
    )
    render_input_toolbar("commit-diff", SAMPLE_COMMIT_DIFF)
    st.caption(f"Input size: {len(diff):,} characters")
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
            if "diff --git" not in diff and "@@" not in diff:
                st.info("Tip: this box works best with output from `git diff` or `git show`.")
            diff_input = clamp_input(diff, "Diff")
            prompt = (
                f"Diff:\n```diff\n{diff_input}\n```\n"
                f"Preferred type: {ctype if ctype != 'auto-detect' else 'best fit'}\n"
                f"Scope: {scope or 'none'}\n\nReturn ONE commit subject line only."
            )
            with st.spinner("Groq is thinking..."):
                result = ask(COMMIT_SYS, prompt, max_tokens=120)
            st.success("Your commit message:")
            st.code(result, language="text")
            st.code(f'git commit -m "{result}"', language="bash")
            if not CONVENTIONAL_RE.match(result):
                st.warning("Output may not fully match Conventional Commits. Try again or set type/scope.")
            show_download(
                label="Download commit message",
                content=result + "\n",
                file_name="commit-message.txt",
                mime="text/plain",
            )


elif mode == "PR Description":
    st.subheader("Full PR Description from Diff")
    st.caption("Use this when you want a review-ready PR body with clear rationale and testing details.")
    diff = st.text_area(
        "Paste git diff for this PR",
        height=280,
        placeholder="diff --git a/server.js b/server.js\n...",
        key="pr-diff",
    )
    render_input_toolbar("pr-diff", SAMPLE_PR_DIFF)
    st.caption(f"Input size: {len(diff):,} characters")
    c1, c2 = st.columns(2)
    ticket  = c1.text_input("Ticket / Issue ID (optional — e.g. GH-42)")
    testing = c2.text_area("Tests already run (optional)", height=80,
                            placeholder="pytest passed, manual test on Windows")

    p1, p2, p3 = st.columns(3)
    audience = p1.selectbox(
        "Audience",
        ["Engineering reviewers", "Cross-functional stakeholders"],
    )
    detail_level = p2.selectbox(
        "Detail level",
        ["Concise", "Standard", "Detailed"],
        index=1,
    )
    focus = p3.selectbox(
        "Focus",
        ["Balanced", "Risk-first", "Testing-first"],
    )
    q1, q2 = st.columns(2)
    writing_style = q1.selectbox(
        "PR writing style",
        ["Direct", "Reviewer-friendly", "Executive summary"],
    )
    highlight_risk = q2.checkbox("Highlight potential risks", value=True)
    include_rollout = st.checkbox("Include rollout and rollback note", value=True)
    include_qa_checklist = st.checkbox("Include QA checklist in Testing", value=True)

    if st.button("Generate PR Description", type="primary", use_container_width=True):
        if not diff.strip():
            st.warning("Please paste a git diff first.")
        else:
            if "diff --git" not in diff and "@@" not in diff:
                st.info("Tip: this box works best with output from `git diff` or `git show`.")
            diff_input = clamp_input(diff, "Diff")
            prompt = (
                f"Diff:\n```diff\n{diff_input}\n```\n"
                f"Ticket: {ticket or 'none'}\n"
                f"Testing notes: {testing or 'none provided'}\n"
                f"Audience: {audience}\n"
                f"Detail level: {detail_level}\n"
                f"Focus: {focus}\n"
                f"Writing style: {writing_style}\n"
                f"Highlight risks clearly: {'yes' if highlight_risk else 'no'}\n"
                f"Include rollout/rollback note under Rationale: {'yes' if include_rollout else 'no'}\n"
                f"Include QA checklist bullets under Testing: {'yes' if include_qa_checklist else 'no'}\n"
                "Keep the required sections exactly as Summary, Changes, Rationale, Testing."
            )
            with st.spinner("CommitCraft is writing your PR..."):
                result = ask(PR_SYS, prompt, max_tokens=1000)
            st.success("PR Description:")
            st.markdown(result)
            st.divider()
            st.caption("Raw Markdown — copy into your GitHub PR:")
            st.code(result, language="markdown")
            show_download(
                label="Download PR description",
                content=result + "\n",
                file_name="pr-description.md",
                mime="text/markdown",
            )


elif mode == "Changelog":
    st.subheader("Release Changelog from Git Log")
    st.caption("Use commit history to create release-ready notes grouped by change type.")
    log = st.text_area(
        "Paste git log (`git log --oneline`)",
        height=280,
        placeholder="a1b2c3d feat: add dark mode\ne4f5g6h fix: crash on empty config\n",
        key="changelog-log",
    )
    render_input_toolbar("changelog-log", SAMPLE_LOG)
    st.caption(f"Input size: {len(log):,} characters")
    version = st.text_input("Release version (optional — e.g. v1.0.0)")

    if st.button("Generate Changelog", type="primary", use_container_width=True):
        if not log.strip():
            st.warning("Please paste some commit messages first.")
        else:
            log_input = clamp_input(log, "Commit log")
            prompt = f"Commits:\n```\n{log_input}\n```\nRelease version: {version or 'unversioned'}"
            with st.spinner("Building changelog..."):
                result = ask(CHANGELOG_SYS, prompt, max_tokens=900)
            st.success("Changelog entry:")
            st.markdown(result)
            st.divider()
            st.caption("Raw Markdown — copy into CHANGELOG.md:")
            st.code(result, language="markdown")
            show_download(
                label="Download changelog",
                content=result + "\n",
                file_name="changelog.md",
                mime="text/markdown",
            )


elif mode == "Release Pack":
    st.subheader("One-Click Release Pack")
    st.caption("Generate commit message, PR description, changelog, and score in one run.")

    diff = st.text_area(
        "Paste git diff (`git diff` or `git show`)",
        height=230,
        placeholder="diff --git a/app.py b/app.py\n...",
        key="pack-diff",
    )
    render_input_toolbar("pack-diff", SAMPLE_COMMIT_DIFF)
    st.caption(f"Diff size: {len(diff):,} characters")
    log = st.text_area(
        "Paste git log (`git log --oneline`) for changelog (optional)",
        height=140,
        placeholder="a1b2c3d feat: add feature\nb2c3d4e fix: handle error\n",
        key="pack-log",
    )
    render_input_toolbar("pack-log", SAMPLE_LOG)
    st.caption(f"Log size: {len(log):,} characters")

    c1, c2, c3 = st.columns(3)
    ctype = c1.selectbox(
        "Commit type preference",
        ["auto-detect", "feat", "fix", "refactor", "docs", "test", "chore", "perf", "ci", "build"],
        key="pack-ctype",
    )
    scope = c2.text_input("Commit scope (optional)", key="pack-scope")
    version = c3.text_input("Release version (optional)", key="pack-version")

    c4, c5 = st.columns(2)
    ticket = c4.text_input("Ticket / Issue ID (optional)", key="pack-ticket")
    testing = c5.text_area(
        "Tests already run (optional)",
        height=80,
        placeholder="pytest passed, manual smoke test on Windows",
        key="pack-testing",
    )

    r1, r2, r3 = st.columns(3)
    pack_audience = r1.selectbox(
        "PR audience",
        ["Engineering reviewers", "Cross-functional stakeholders"],
        key="pack-audience",
    )
    pack_detail = r2.selectbox(
        "PR detail level",
        ["Concise", "Standard", "Detailed"],
        index=1,
        key="pack-detail",
    )
    pack_focus = r3.selectbox(
        "PR focus",
        ["Balanced", "Risk-first", "Testing-first"],
        key="pack-focus",
    )
    pack_rollout = st.checkbox(
        "Include rollout and rollback note in PR",
        value=True,
        key="pack-rollout",
    )
    pack_qa = st.checkbox(
        "Include QA checklist in PR Testing",
        value=True,
        key="pack-qa",
    )

    if st.button("Generate Release Pack", type="primary", use_container_width=True):
        if not diff.strip():
            st.warning("Please paste a git diff first.")
        else:
            if "diff --git" not in diff and "@@" not in diff:
                st.info("Tip: this works best with output from `git diff` or `git show`.")

            diff_input = clamp_input(diff, "Diff")
            log_input = clamp_input(log, "Commit log") if log.strip() else ""

            commit_prompt = (
                f"Diff:\n```diff\n{diff_input}\n```\n"
                f"Preferred type: {ctype if ctype != 'auto-detect' else 'best fit'}\n"
                f"Scope: {scope or 'none'}\n\nReturn ONE commit subject line only."
            )
            pr_prompt = (
                f"Diff:\n```diff\n{diff_input}\n```\n"
                f"Ticket: {ticket or 'none'}\n"
                f"Testing notes: {testing or 'none provided'}\n"
                f"Audience: {pack_audience}\n"
                f"Detail level: {pack_detail}\n"
                f"Focus: {pack_focus}\n"
                f"Include rollout/rollback note under Rationale: {'yes' if pack_rollout else 'no'}\n"
                f"Include QA checklist bullets under Testing: {'yes' if pack_qa else 'no'}\n"
                "Keep the required sections exactly as Summary, Changes, Rationale, Testing."
            )
            if log_input:
                changelog_prompt = (
                    f"Commits:\n```\n{log_input}\n```\n"
                    f"Release version: {version or 'unversioned'}"
                )
            else:
                changelog_prompt = (
                    f"Changes:\n```diff\n{diff_input}\n```\n"
                    f"Release version: {version or 'unversioned'}"
                )

            with st.spinner("Building release pack..."):
                commit_message = ask(COMMIT_SYS, commit_prompt, max_tokens=120)
                pr_body = ask(PR_SYS, pr_prompt, max_tokens=1000)
                changelog_md = ask(CHANGELOG_SYS, changelog_prompt, max_tokens=900)
                score_report = ask(
                    SCORE_SYS,
                    (
                        f'Commit message:\n"""\n{commit_message}\n"""\n\n'
                        f"Diff (may be empty):\n```diff\n{diff_input}\n```"
                    ),
                    max_tokens=500,
                )

            ts = datetime.now().strftime("%Y%m%d-%H%M")
            tab_commit, tab_pr, tab_changelog, tab_score = st.tabs(
                ["Commit", "PR", "Changelog", "Score"]
            )

            with tab_commit:
                st.success("Commit message")
                st.code(commit_message, language="text")
                st.code(f'git commit -m "{commit_message}"', language="bash")
                show_download(
                    label="Download commit message",
                    content=commit_message + "\n",
                    file_name=f"commit-message-{ts}.txt",
                    mime="text/plain",
                )

            with tab_pr:
                st.success("PR description")
                st.markdown(pr_body)
                st.code(pr_body, language="markdown")
                show_download(
                    label="Download PR markdown",
                    content=pr_body + "\n",
                    file_name=f"pr-description-{ts}.md",
                    mime="text/markdown",
                )

            with tab_changelog:
                st.success("Changelog")
                st.markdown(changelog_md)
                st.code(changelog_md, language="markdown")
                show_download(
                    label="Download changelog",
                    content=changelog_md + "\n",
                    file_name=f"changelog-{ts}.md",
                    mime="text/markdown",
                )

            with tab_score:
                score_num = extract_score_num(score_report)
                if score_num is not None:
                    label = (
                        "Poor — rewrite it" if score_num <= 3
                        else "Okay — could be better" if score_num <= 6
                        else "Good" if score_num <= 8
                        else "Excellent!"
                    )
                    st.metric("Commit Score", f"{score_num}/10", delta=label)
                    st.markdown("---")
                st.markdown(score_report)
                show_download(
                    label="Download score report",
                    content=score_report + "\n",
                    file_name=f"score-report-{ts}.md",
                    mime="text/markdown",
                )


elif mode == "Score Commit":
    st.subheader("Score an Existing Commit Message")
    st.caption("Get a quality score, reasoning, and a stronger rewritten commit subject.")
    msg = st.text_area(
        "Commit message to evaluate",
        height=80,
        placeholder="fix: update stuff",
        key="score-msg",
    )
    render_input_toolbar("score-msg", SAMPLE_SCORE_MESSAGE)
    diff = st.text_area(
        "Optional: paste the diff too for deeper evaluation",
        height=200,
        placeholder="diff --git a/config.py b/config.py\n...",
        key="score-diff",
    )
    render_input_toolbar("score-diff", SAMPLE_COMMIT_DIFF)
    st.caption(f"Message size: {len(msg):,} characters | Diff size: {len(diff):,} characters")

    if st.button("Score My Commit", type="primary", use_container_width=True):
        if not msg.strip():
            st.warning("Please enter a commit message.")
        else:
            diff_input = clamp_input(diff, "Diff")
            prompt = (
                f'Commit message:\n"""\n{msg}\n"""\n\n'
                f"Diff (may be empty):\n```diff\n{diff_input}\n```"
            )
            with st.spinner("Scoring..."):
                result = ask(SCORE_SYS, prompt, max_tokens=500)

            score_num = extract_score_num(result)

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
            show_download(
                label="Download score report",
                content=result + "\n",
                file_name="score-report.md",
                mime="text/markdown",
            )

st.divider()
st.caption(
    "CommitCraft · GitAgent Hackathon 2026 · "
    "Streamlit + Groq · GitAgent spec: [gitagent.sh](https://gitagent.sh)"
)
