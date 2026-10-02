# Phase 7 — production subagent worktree pool (2026-10-02)

Implements §2.2 of `git_workflow_plan_2026-10-01.md`. Owner (by card): each seat lands its own
helpers' work; helpers push `submit/<seat>/<name>` and never push `main`.

Status: SHIPPED, hook wired in `.claude/settings.json`. Rollback = delete the `WorktreeCreate` and
`WorktreeRemove` entries there (the pool dirs and refs are inert without them).

## Shipped
- `src/RimMandrake/Utils/worktree_pool.py` — `create` / `remove` (the hooks), `status`, `rescue-list`,
  and `submit` (run inside a slot: rebase on origin/main, refuse DLLs, push `submit/<seat>/<name>`).
  Seat = the hook's `cwd` under `/home/mandrake/rm/<seat>` (or under the pool), else `AGENT_SEAT`;
  neither → exit 1 with a message naming both. Pool `/home/mandrake/rm/pool/<seat>/slot{0,1}`
  (`RM_POOL_SLOTS`), linked worktrees of the seat clone, so slot refs ARE the seat's refs.
- `src/RimMandrake/Utils/land_submissions.py` — the seat lands `submit/<seat>/*`: fetch → rebase via
  `git replay --ref-action=print` on a throwaway `refs/heads/land-tmp/…` (no checkout; the seat's own
  tree is never touched) → `push --atomic <new>:main` + leased deletion of the submit ref →
  `refs/landed/<seat>/<name>` = submitted sha (so the rebased slot recycles as landed). Push failure or
  timeout → fetch + `merge-base --is-ancestor <new> origin/main` before any retry. Conflict → submit
  ref left, exit 1. Never `--force`.
- `src/RimMandrake/Utils/selftest_worktree_pool.py` — 41 checks in a throwaway repo under
  `/home/mandrake/wt/p7test`.

### Decisions worth knowing
- **Rescue events go to `/home/mandrake/rm/pool/rescues.jsonl`, not the rimflow ledger** — rimflow has
  no `rescue` verb (`VERBS` in `rimflow/model.py`), and rimflow/ledger was under concurrent edit. Owed:
  a rimflow `rescue` verb + `rimflow next` listing open rescues (§2.2), reading this jsonl.
- Rescue = a two-parent commit like `git stash`: parent 1 = slot HEAD (keeps unpushed commits
  reachable), parent 2 = the real index (staged state); tree = working tree incl. untracked
  non-ignored ≤5 MB. >5 MB and ignored paths are listed in the message. The snapshot is **verified**
  (`git diff` of the snapshot index vs the working tree must be empty) before the slot is reset; a
  failed verify leaves the slot untouched and unusable. Refs are local only.
- Reset is `checkout -f -B agent/<name> origin/main` + `clean -fd` (ignored `bin/`/`obj/` stay warm).

## 🔴 New measured finding — WorktreeRemove never fires, so pid-ownership alone clogs a live seat
MEASURED 2026-10-02, CC 2.1.285, real `claude -p`: one session launching three **sequential**
isolated subagents (each finished, changed nothing) got slot0, slot1, then **`pool full`** — the
subagent runs inside the parent `claude` process, WorktreeRemove never fired (0 calls in all runs),
so a long-lived seat session would hold every slot it ever used until it exits.
Fix shipped: the parent transcript (`transcript_path` from the hook stdin) records
`toolUseResult: {status: "completed", agentId, worktreePath}`, and the hook's `name` is
`agent-<agentId>`. A slot whose subagent has a terminal status is free **if clean and landed**;
if it holds unlanded work it stays held (its session may still harvest it) and the pool-full message
says so. Re-run after the fix: three sequential subagents → slot0, slot0, slot0. Background
(async) agents never match, so they stay held until their session exits — conservative.

## Real hook JSON contract (re-confirmed)
WorktreeCreate stdin keys, MEASURED: `cwd, hook_event_name, name, prompt_id, session_id,
transcript_path` — no `base_path`/`worktree_name` (docs are wrong, as X1 found). Stdout line 1 = path
(subagent `pwd` was the slot). Exit 1 + stderr surfaces verbatim to the parent as
`WorktreeCreate hook failed: <cmd>: <stderr>`. WorktreeRemove: 0 firings in 6 runs.

## Gate: kill-mid-edit rescue test — PASS
Real `claude -p` (throwaway repo `/home/mandrake/wt/p7test/e2e`): a worktree subagent in slot0
committed `c1.txt` (unpushed), appended to tracked `a.txt`, created untracked `src/new.cs`, staged a
new `st.txt`, touched `READY`, then slept; the owning `claude` process (pid 2356710, from the lock)
was `kill -9`ed. `status` then showed slot0 `NEEDS-RESCUE dirty=4`. The next real `claude -p`
allocation got slot0 and produced `refs/rescue/bench/agent-af068cc1eecad7409-20261002T073336Z`:
`a.txt`=`hello|EDITED`, `c1.txt`=`committed`, `src/new.cs`=`class-Y`, `st.txt`=`staged`, `READY`
present, `^2:st.txt`=`staged` (index), history `rescue → rescue index → unpushed-work → seed`;
classes `{doc: 3, source: 2}`, `pushed: false`, 0 rescue refs on the remote; slot0 `git status`
empty and the new subagent saw a clean tree. The selftest repeats this with a Python writer
SIGKILLed mid-write (also a >5 MB file, an ignored `obj/`, a fake private key → `suspect-secret`).

## Gate: X1 end-to-end re-run with real `claude -p` — PASS
Three parallel isolated subagents, 2 slots: slot0, slot1, third failed cleanly with
`WorktreeCreate hook failed: … pool full: seat bench, all 2 slots unavailable — held: slot0: owner
pid … alive (agent-…); slot1: …`. Telemetry wrote `alloc, alloc, full` with `MemAvailable_kib`
(~31.9 GB) and `wait_s` 0.01–0.04 s (local bare remote; production fetches GitHub inside the mutex).

## Not done here
- rimflow `rescue` verb / `rimflow next` listing (above); weekly >30-day sweep is `rescue-list`
  flagging, not a timer.
- Nothing stops a helper from pushing `main` by hand; `submit` is the documented path.
- Sessions still started in `D:\Luke\dev\RimMandrake` with no `AGENT_SEAT` get a clear hook error
  for `isolation: worktree` subagents (by design: no `.claude/worktrees/` fallback).
