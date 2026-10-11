# 20 — global ~/.claude/CLAUDE.md: fix sources, render; link chatgpt-consult

- [x] 1. claudeconf.py read; live file backed up
- [x] 2. live-vs-render diff; hand edits adopted into sources
- [x] 3. stale source lines fixed (worktree advice, wsl-windows-plumbing, model ladder)
- [x] 4. rendered, check clean, Lodestar pushed
- [x] 5. ChatGPTConsult linked + registry + memory updated

## Lodestar — PUBLISHED acc95bbb (pushed origin/main)
- Backup: ~/.claude/backups/weekly_cleaning_2026-10-11/CLAUDE.md.global.bak
- Hand edits adopted: RimMandrake clones line -> machines/archmagi.md; owner's verbatim HANDOFF READY quote (only in 09-29 captures) -> 55-handoff-on-reboot.md. Not adopted (stale/superseded by newer sources): old Sonnet 5.5/haiku-400 ladder, old Placard text, provenance tails, "lessons in CLAUDE.md".
- 50-save-as-you-go: merge only in a checkout no other agent edits (fresh clone, or worktree where allowed; RimMandrake not).
- archmagi.md: wsl-windows-plumbing now linked (skills.md row, windows-wsl), pointer kept and described.
- 45-subagents source already matches Agent_Policy (sonnet, no haiku). Render done; claudemd_drift() = None; adopt queue empty. check still warns 118 auto-memory files unsnapshotted (sweep's job, not done here).

## chatgpt-consult — ChatGPTConsult PUBLISHED cf12822; linked ~/.claude/skills/chatgpt-consult
- Frontmatter was INVALID YAML (unquoted `: ` inside description) and 2,108 chars; now a `>-` block, 850 chars. The dropped detail (thread naming, decline ledger) was already in the body.
- skills.md row widened `mac` -> `mac, windows-wsl` (Lodestar acc95bbb). wsl-windows-plumbing linked too.
- Memory gpt-consult.md now points at the skill instead of saying it isn't wired.

## Lessons folded into ~/dev/ChatGPTConsult/references/windows-wsl-codex.md (originals untouched)
| lesson | source (still in place) | section |
|---|---|---|
| effort floor high, owner quote; gpt-6.1-sol default; art model separate | memory gpt-consult.md; gpt_consult.py; lesson 20261002T081258Z | The call |
| prompt on stdin, read-only sandbox, -o Windows path | gpt_consult.py | The call |
| ext4 cwd breaks sandbox; \\wsl.localhost reads hang; stage on Windows drive; inline all inputs | lesson 20261002T081258Z; GIT_WORKFLOW.md; gpt_consult.py docstring | WSL path traps |
| inline FILE delimiter format + "do not open from disk" | gpt_consult.py build_prompt | WSL path traps |
| PowerShell codepage mojibake, say UTF-8 | debug_process.md §5 | WSL path traps |
| <~700k chars, silent middle truncation, ask "Outside this slice" | lesson 20261011T071444Z | Size |
| slice by manifest, shared context in every slice | hose_port_gpt_review_2026-10-10/build_manifests.py, prompt_common.md | Size |
| 438-970 s at high effort; timeouts 1500/3000 | lesson 20261011T071444Z; run_consult.sh | Size |
| parallel consults cross answers; subject guard | lesson 20261003T023944Z | Size |
| no live process != dead consult | lesson 20261002T230900Z | Size |
| expired auth looks like a session; grade the body | lesson 20260929T062905Z | Failure modes |
| stale codex processes after app update | lesson 20261011T163131Z | Failure modes |
| adversarial review framing + Findings/verified/outside-slice format | prompt_common.md | Framing |
| debug brief contents + "rank hypotheses, cheapest test" | debug_process.md §5 | Framing |
| answer is a hypothesis; verify line-level claims (brace 27/27) | debug_process.md §5; lesson 20261011T071444Z | Reading the answer |
Kept local only: RimMandrake trigger thresholds (20 min / card), Transient retention, D:\Luke\dev\_rmscratch path specifics. Pointer added to debug_process.md §5.
