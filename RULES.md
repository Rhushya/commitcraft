# RULES.md — CommitCraft

## Hard Constraints

1. Never describe changes not present in the provided diff, commit range, or input.
2. Never invent file names, function names, or ticket IDs.
3. Never include secrets, API keys, or internal URLs in generated text.
4. Always prefer precise, factual language over marketing language.
5. When uncertain, say so and ask for clarification rather than guessing.

## Commit Message Rules

1. Always use Conventional Commits format:
   <type>(<optional scope>): <short summary>
2. Allowed types: feat, fix, refactor, docs, test, chore, perf, ci, build.
3. Limit subject line to ~72 characters.
4. Do not end the subject line with a period.
5. Use imperative mood: "add", "fix", "refactor" NOT "added", "fixed".

## PR Description Rules

1. Structure output into exactly these sections:
   ## Summary | ## Changes | ## Rationale | ## Testing
2. Use bullet points under "Changes" and "Testing".
3. If tests are missing, explicitly say what tests should be added.

## Changelog Rules

1. Group items under: Added / Changed / Fixed / Removed.
2. Use past tense ("Added feature X") not imperative ("Add feature X").
3. Write for external readers who do not know the internal codebase.

## Quality Scoring Rules

1. Score commit messages 1-10:
   - 1-3: useless or misleading ("fix", "changes", "update stuff")
   - 4-6: understandable but missing detail or correct format
   - 7-8: good messages with minor issues
   - 9-10: excellent examples the whole team should copy
2. Always provide one concrete improved example message.
