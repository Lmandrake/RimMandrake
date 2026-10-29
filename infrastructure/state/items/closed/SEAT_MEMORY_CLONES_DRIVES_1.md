# SEAT_MEMORY_CLONES_DRIVES_1 — stop seats dying from memory: tmpfs, test fan-out, clones, drives

**For BENCH, in RimFlow.** Filed 2026-10-08 by a session in `D:\Luke\dev` (not a RimMandrake
seat) on the owner's instruction: *"Please write this entire topic up as a Bench ticket to take
up in RimFlow. Record the entire context please, it will not be you executing it."*
The owner asked for a deep design, **"not just another small kludge that will get us into yet
more trouble"**. Treat this as a design-led change to the fleet, not a one-line patch.

## The design to execute

`design/RimMandrake/memory_clones_drives_2026-10-08.md` (commit `a98c434cb`) is the authoritative
plan. It holds the full audit, three plans with trade-offs and a memory budget for each, and
GPT's adversarial review (gpt-6.1-sol via `gpt_consult.py`, actually reached). Of GPT's 15
objections, 14 were accepted and 1 partly; the doc records how each changed the plan.
**Read it before doing anything.** This ticket carries the context and the order; the doc
carries the numbers.

## The incident (2026-10-07/08)

- FOUNDRY's seat (`claude-seat-FOUNDRY-683.scope`, launched by
  `src/RimMandrake/Utils/claude_bounded.sh`: `MemoryMax=10G`, `MemorySwapMax=2G`, under
  `claude-seats.slice` 24G) was OOM-killed by the kernel. Kills: **23 processes between 23:08 and
  23:20 PDT** (python test harnesses 0.8–2.1G each, git, and **Claude itself, pid 960, at
  23:16:52**). The terminal printed `bash: line 1: 683 Killed … claude_bounded.sh …`. Nothing ran
  overnight, so the owner lost the night's work and the session's context.
- **Cause 1 — RAM disk.** At 23:08 a FOUNDRY subagent ran `git clone` of RimMandrake into
  `/tmp/claude-1000/pushclone` to push 14 commits from a clean copy. `/tmp` is tmpfs (18G).
  **tmpfs pages are charged as shmem to the writer's memcg and stay charged after the writer
  dies.** The clone reached 12G. After the crash the scope sat at **9.2G of 10G (shmem 9.10G,
  anon 0)** all night, holding only a `sleep` loop. `memory.events`: `max 621177`,
  `oom 6749`, `oom_kill 23`.
- **Cause 2 — test fan-out.** At about 23:05–23:08 the same seat ran the full selftest suite with
  **16 parallel workers** (`Transient/selftest_after_l0_20261008.txt`: 329/336 passed; 4 of the
  7 failures were rc 137 OOM kills, not real failures).
- **Side effect:** the killed Claude left the terminal in SGR mouse-tracking mode, so moving the
  mouse printed `0;34;37M35;…` codes. `reset` clears it.
- Clean-up already done: the dead clone was deleted (the seat dropped to 176M), and the leftover
  scope was stopped. FOUNDRY's stranded work was rescued and pushed (`5438ed5d3`, 14 canon
  commits, handoff `6c097fd51`).

## It is a pattern, not a one-off (from the design audit)

- **Six** seat deaths from tmpfs residue since 10-01 (3.1–9.65 GB each), with Claude itself
  killed in five. **Lessons were filed after 10-06 and 10-07, and it recurred within hours both
  times.** So a written rule alone has failed; enforcement is required.
- 10-04/05: seats died with about 10.1 GB of anon memory and almost no tmpfs. That was test
  fan-out alone. Single harness processes reach 1.2–5.1 GB.
- The per-seat cap works: there has been no host-wide OOM since 08-14, and both FOUNDRY and
  BENCH hit 10G this boot.
- **Host headroom is thin:** RimWorld's measured peak is 20.17 GB, plus the WSL 36 GB cap and an
  *estimated* ~6 GB for Windows, against 63.4 GB physical. That leaves about 1–2 GB of slack,
  and the Windows figure is an estimate, not a measurement.
- **Disk debris, about 240 GB of the 337 GB used on the WSL ext4:**
  - `mirror.git` holds 71 GB of leftovers from 42 aborted fetches.
  - 11 stale `/home/mandrake/wt/impl-*` clones take 81 GB.
  - ⚠️ Five `_fwY_*` clones, `reconcile` and a `~/.cache/pyrelands_replay_*` copy **borrow
    objects (alternates) from the live foundry/bench clones**, so naive deletion or a gc there
    can corrupt them.
- Claude Code's own task-output folder under `/tmp/claude-1000` was already 6.2 GB.

## Recommended plan ("B-lite", phased; see the doc for B and C and why they were not chosen)

**Phase 1 — today, cheap, enforce rather than exhort**
1. Default the selftest runner to **1 worker inside a seat** (16 today). GPT rated this the
   cheapest single change.
2. Set `CLAUDE_CODE_TOOL_MEMORY_LIMIT=6G` in the seat environment, so a runaway tool dies before
   Claude does. Nothing sets it today; it is confirmed present in installed Claude Code 2.1.286.
3. Make `claude_bounded.sh` restore the terminal when Claude exits (mouse tracking off, or a
   `reset`).
4. Add a hook that **refuses** `git clone` (and other large writes) into `/tmp` or `/dev/shm`.

**Phase 2 — next, after testing**
5. Move `TMPDIR` / `CLAUDE_CODE_TMPDIR` off tmpfs onto ext4, **only after verifying Claude still
   works** with it moved.
6. Give test workers their own memcg (about 12G), **placed so it truly counts under the seat's
   budget** (GPT's objection 1: as first drafted, per-test caps escaped the seat's limit).
7. Add a watcher on `memory.events` that warns before a seat reaches its cap.

**Phase 3 — later**
8. Quarantine stale clones only after checking each for unpushed work, and **resolve alternates
   first**.
9. Set up a shared object store.
10. Shrink `/tmp` to 8G, only after step 5, because shrinking it could break Claude itself.

**Deferred:** tighter per-seat caps and the central clone/push broker (Plan C). GPT's objection
2: in Plans B and C the seat caps summed past the slice cap, which still lets Claude be killed.

## Constraints whoever executes must respect

- 🔴 **Worktrees are OFF** (owner, 2026-10-02, `block_worktrees.py`). The design doc and any
  "push from a clean copy" helper must not route around that with a full clone in `/tmp`; that
  workaround is exactly what caused this incident. Note: the session that filed this ticket used
  `git worktree` twice on 10-08 for rescue pushes from outside a seat, unaware of the rule. Both
  worktrees are removed.
- Changes to `claude_bounded.sh`, the seat environment and hooks affect **every** seat (FOUNDRY,
  BENCH, EMERGENCY, the RC Server). Roll them out when seats can restart, and verify per seat
  with `systemctl --user status claude-seat-*.scope` (Memory, peak and swap lines).
- A changed cap or limit is verified by an **OOM test that fails before and passes after**, as in
  the 08-14 measurement recorded in `claude_bounded.sh`. Rereading the config does not count.

## Acceptance

- [ ] Phase 1 items 1–4 landed, each with a planted-break check: a clone into `/tmp` is refused;
      a deliberate tool memory bomb dies at 6G with Claude surviving; the terminal is sane after
      `kill -9` of Claude in a seat.
- [ ] Selftest suite run inside a seat completes with no rc 137.
- [ ] Phase 2 items 5–7, each verified on a live seat.
- [ ] Phase 3 debris cleanup with a written list of what was removed and the unpushed or
      alternates check that preceded it.
- [ ] The lesson recorded in the lessons doc (not `CLAUDE.md`), pointing at the enforcement,
      not restating the rule.

NEXT: read `design/RimMandrake/memory_clones_drives_2026-10-08.md`, then land Phase 1 items 1–4 with their planted-break checks.
