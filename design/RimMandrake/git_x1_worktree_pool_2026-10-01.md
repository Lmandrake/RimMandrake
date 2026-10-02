# X1: WorktreeCreate/WorktreeRemove pool hook experiment (2026-10-01)

Claude Code 2.1.285. Experiment dir `/home/mandrake/wt/x1` (hook `pool_hook.py`, `hook.log`, `pool/`, test repo `repo/`). No real repo or settings touched.

## Contract (MEASURED, differs from docs)
- Docs say stdin has `base_path` + `worktree_name`. REAL WorktreeCreate stdin: `session_id, transcript_path, cwd, hook_event_name, name` (+ `prompt_id` for subagents). No `base_path`, no `worktree_name`. Use `cwd` and `name` (subagent: `agent-<hex>`; `--worktree x1test`: `x1test`).
- Stdout first line = path: MEASURED works; subagent `pwd` was the pool slot. Non-zero exit + stderr: MEASURED, parent agent sees `WorktreeCreate hook failed: <cmd>: <stderr verbatim>` as the Agent tool error; no subagent starts.
- WorktreeRemove: NEVER fired in any run (4 subagent runs + 1 `--worktree` run, all `claude -p`). UNMEASURED for interactive sessions.
- Claude did not delete the slot dir (MEASURED; no remove call at all).
- `claude --worktree x1test -p` DOES go through the hook (MEASURED).

## Design findings
- flock cannot carry ownership (hook exits). Ownership = JSON in `slotN.lock` {pid of the claude process, name}; slot busy iff that pid is alive; short flock on `alloc.mutex` only serialises allocation. Dead owner = auto-free, so missing WorktreeRemove is harmless.
- TRAP (MEASURED): hook's parent is a short-lived `sh -c`; recording `getppid()` made the slot look free at once and two parallel sessions got the SAME slot. Fix: walk /proc ancestors to the `claude` process.
- After fix: 2 parallel sessions -> slot0 and slot1 (MEASURED). Recycle of a clean pushed slot to fresh origin/main on `agent/<name>` works (MEASURED).
- Pool full (4 hand-written locks held by a live pid): clean fail, message above (MEASURED).
- Recycle refuses dirty/unpushed slots (code path written, not exercised: UNMEASURED).
- Note: recycled slots can race origin (one subagent push was non-FF); agents must rebase.
