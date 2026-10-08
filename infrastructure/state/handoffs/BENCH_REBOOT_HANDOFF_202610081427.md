# BENCH_REBOOT_HANDOFF_202610081427 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610081345`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
This window is the FIRST BENCH launch on the new claude_bounded.sh (8807aaa41): the memory fixes are proven only on throwaway TEST seats, so the first real thing to do is confirm this seat is protected — `claude --debug` (or the launch output) must show a `tool cgroup:` path under `claude-seat-BENCH-*.scope`, no red tool-cap warning, and `echo $TMPDIR` = /home/mandrake/.seat-tmp/BENCH. If any of that fails, the owner's standing fallback is SEAT_MEMORY_STANDARD_FALLBACK_1 (design §9).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- The memory work's home-made pieces (clone hook, seat sub-cgroup, harness admission) run on trial; the owner was uneasy about original solutions, and the standard fallback (mask tmp.mount, needs his sudo + WSL restart) is recorded: `D:\Luke\dev\RimMandrake\design\RimMandrake\memory_clones_drives_2026-10-08.md` §9.
- Quarantine `/home/mandrake/rm/_quarantine/2026-10-08/` (~117 GB incl. wt/gitlab) is deleted on/after 10-15 (QUARANTINE_PURGE_WEEK_1); `fstrim` afterwards needs his sudo.
- Ruled biome sheets: Miasma/FeverWood/Webwork/LeaningScrub are reviewable now; Greentide (177) and LongShade (68) still drawing — `D:\Luke\dev\RimMandrake\Transient\biome_art_refresh_2026-10-07\MORNING_SHEETS.md`.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `SEAT_MEMORY_CLONES_DRIVES_1` — Phase 0 + test pen + temp move + disk landed (8807aaa41, 93ae58050, 139775499, 882696f61); remaining: memory.events watcher, shared object store, northstar/judge drivers onto rm-harness.slice, live-seat verification; NEXT: verify this seat's tool cgroup + TMPDIR on launch, then build the memory.events/shmem watcher (design §7 phase 1).
- `ART_SHEETS_TAIL_1` — Greentide/LongShade renders pending, Iriaz H/I + Vaalok south queued; NEXT: rerun Transient/biome_art_refresh_2026-10-07/refresh_ruled_sheets.sh when renders land and put NEW rows to the owner.
- `WEATHER_STONES_OWN_ART_1` — 3 jobs queued (wsart_RM_*); NEXT: put the renders on a sheet for the owner when they land, install only what he rules.
- `MIRROR_REPACK_LEAK_FIX_1` — cause inferred (auto-gc detach killed at unit exit); NEXT: add -c gc.autoDetach=false to mirror.py and prove no tmp_pack_* after 10 timer runs.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- CLAUDE_CODE_TOOL_MEMORY_LIMIT alone never worked under our old launcher: 2.1.286 creates the tool cgroup as a SIBLING of its own cgroup and sets no swap.max, so a bomb survived by swapping (see: Transient/seat_memory_2026-10-08/launcher.md, design §9).
- In the shared bench clone, `git rebase` refuses while any helper has dirty files; `./publish` (private index) lands named paths regardless (see: GIT_WORKFLOW.md).
- Seat OOM enforcement and its upgrade check (filed: lessons 20261008T142604Z).

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (9) — the next seat's queue

- `SEAT_MEMORY_CLONES_DRIVES_1` — Stop seats dying from memory: tmpfs residue, test fan-out, clones, drives (design a98c434cb)
- `ART_SHEETS_TAIL_1` — Ruled biome sheets tail: rerun refresh_ruled_sheets.sh as Greentide (177) and LongShade (68) renders land; put Iriaz H/I redraws and every NEW-flagged
- `DONOR_PLANT_OVERRIDE_VERIFY_1` — Verify in game that the loose-PNG override in UtinniPatches (Brambles, CreepStern, CrimsonCushion/RG_TundraScrubsRed, Dervish; 5cb5cc22e) actually bea
- `WEATHER_STONES_OWN_ART_1` — RM_CondenserWater, RM_KarrekPaste, RM_SeepStone wear vanilla chemfuel/pemmican/jade art: queue our own item art at priority 0, install after owner rul
- `JAWABENCH_DLL_REDEPLOY_1` — JawaBench DLL rebuilt in repo with 3 new tools but the game copy is stale: with the game closed run build.py --gm --apply (rimbridge-companion skill)
- `QUARANTINE_PURGE_WEEK_1` — On/after 2026-10-15 delete /home/mandrake/rm/_quarantine/2026-10-08/ (~117 GB: stale clones + wt/gitlab, all checked no unpushed work; decision taken 
- `HELD_CLONE_WORK_TRIAGE_1` — Land or drop work stranded in side clones: _fwY_gate (uncommitted RM_SluiceGate.cs, RM_SluiceGateMath.cs, settings), _fwY_blood/quarry/tanker (one unt
- `MIRROR_REPACK_LEAK_FIX_1` — mirror.git leaked 42 tmp_pack_* (71 GB): likely auto-gc repack detached by git fetch and killed when rm-mirror.service exits (inferred). Fix: -c gc.au
- `SEAT_MEMORY_STANDARD_FALLBACK_1` — If the home-made seat-memory pieces misbehave (hook, seat sub-cgroup, harness admission), switch to the standard route: mask tmp.mount (owner sudo + W

## Commits

```
905266c35 Seat memory: lesson pointing at the enforcement; progress note on SEAT_MEMORY_CLONES_DRIVES_1
139775499 Selftests run in rm-harness.slice, not the seat (SEAT_MEMORY_CLONES_DRIVES_1)
f9cefa560 Record owner's concern about home-made seat-memory pieces and the standard fallback (mask tmp.mount)
d8b371cae HELD_CLONE_WORK_TRIAGE_1: decision table
6cdda1140 FlowWorks: land stranded sluice gate draft (Building_RM_SluiceGate, math, settings)
8807aaa41 claude_bounded: delegated tool cgroup (6G, swap 0), seat temp on ext4, terminal reset on any exit
c998ed183 File quarantine purge (10-15), held clone work triage, mirror repack leak; web research on Claude Code memory
b04e16755 Queue own-art jobs for condenser water, karrek paste, seep stone
1a13d2c17 File the art and DLL tails from the 10-08 handoff as ledger items so none lingers unowned
93ae58050 Add block_tmpfs_clone PreToolUse hook; merge hook points at ext4 scratch, not /tmp worktree
a46ffeffd Stale clones exam 2026-10-08: unpushed/alternates check, verdicts, proposed removal order
7a9793fff HugeThings validation: settings set triggers RefreshAllMaps; wake failure is a mod bug (Titanic cctor throws)
882696f61 Disk clean-up 2026-10-08: quarantine list, held-back clones, mirror tmp_pack cause
3e3608b67 SolarMirrors validation pass 4: fresh full read, no new kind of problem
6ebf956e6 Pyrinth validation: get_defs '(no such field)' for mineableThing is UNMEASURED, not FAIL
18816252b OasisMaker validation: fast_settings tick budget 4000; acc_green rerun notes
76372908b ShipVermin validation: debug actions live under Actions\T: (nest chain now measures)
5cb5cc22e Morning art rulings enacted (decision taken by question card 2026-10-08)
08a1e0fde File SEAT_MEMORY_CLONES_DRIVES_1 for BENCH: seat OOM deaths from tmpfs residue + test fan-out; executes design a98c434cb
15379fc73 FOUNDRY ledger shard sync
... 7 more: git log --oneline 4416fd0be..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     FOUNDRY acc_green_min sitting

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
?? conversations/   earlier BENCH windows' conversation exports (not this window)
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   earlier BENCH windows (unchanged since the 10-08 morning handoff, which attributes them)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   earlier BENCH windows (unchanged since the 10-08 morning handoff, which attributes them)
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   earlier BENCH windows (unchanged since the 10-08 morning handoff, which attributes them)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/   earlier BENCH windows (unchanged since the 10-08 morning handoff, which attributes them)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/   earlier BENCH windows (unchanged since the 10-08 morning handoff, which attributes them)
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   earlier BENCH windows (unchanged since the 10-08 morning handoff, which attributes them)
```

