A headless claude -p judge call cannot use --bare to skip CLAUDE.md and hooks: --bare reads only ANTHROPIC_API_KEY or an apiKeyHelper, never the OAuth login, so on our subscription accounts it cannot authenticate. A no-tool judge call through claude_bounded.sh with --tools '' and the prompt on stdin, run from a folder outside the repo (no project CLAUDE.md or hooks), cost about 178k weighted tokens cold and about 60k warm (Sonnet, measured 2026-11-25 on 50 calls).
item: RIMMANDRAKE_BUILD_TEMPORARY_WORK_BUNDLE_MONITOR_DAILY
home: infrastructure/state/facts/tool_traps.md
