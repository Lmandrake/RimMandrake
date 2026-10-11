# Run-start and run-end checklists

Each line names the failure it prevents. Every one of these cost a full-list run
(~15 minutes plus a ~15–19 minute cold load) before it was written down.

## Before the game is up

- [ ] **Hold the bridge** (`rimflow bridge take --for "<proof>"`). One driver at a time.
- [ ] **Record the mod list's identity**: the active count parsed from `ModsConfig.xml`
      (never `grep -c '<li>'`) and its md5. Re-check both at the end. A proof that
      swapped the list must restore it.
- [ ] **Deploy from what you will claim.** If your clone has diverged from origin, or
      carries peers' dirty files, deploy from a `git archive` export of origin/main and
      run *that export's* `deploy_custom_mods.py`. Run the proof from the same export.
      Its DLLs must be byte-identical to the game copy, or `assembly_identity` aborts
      at L2.
- [ ] **A restored C# file keeps its backup's older mtime.** msbuild's incremental
      check then skips it, and the old build stays compiled. `touch` a restored source
      file before rebuilding. This happened with a planted-defect fuzz, 2026-10-11.

## Launch and readiness

- [ ] **Launch via Steam**, not the bare exe.
- [ ] **A cold load of the full list takes ~13–19 minutes** (03:16 → 03:35 on 2026-10-11).
      `launch_and_wait.sh` gives up after ~5 minutes. Its timeout is not a failed launch.
- [ ] **"Bridge token:" in Player.log right after a relaunch can be the PREVIOUS
      session's line.** The new process has not truncated the file yet, so a naive
      grep reads "ready" at 0 s. Before trusting the hit, require a fresh log: a small
      line count, or an mtime newer than the launch with the PID matching the new
      process.
- [ ] **Liveness is a bridge round trip (`./game`), never log mtime.** Player.log silent
      for 17+ minutes with a busy CPU was a healthy game, not a hang.
- [ ] **A game that has run for hours** no longer reaches its startup `[RimBridge]` line
      through `list_logs limit=500`, so a startup-log row goes UNMEASURED. Prefer a
      fresh load before a recorded proof. Since 2026-10-11 a check can also accept the
      `log_revive` sentinel as its journal proof.
- [ ] **JawaBench's test profile can expire mid-session.** `JawaBench/companion_profile.json`
      grants the TEST profile, and once it lapses, test-only tools such as
      `jawa/map_comp_timing` are refused as CAMPAIGN. Renew it with the same keys and
      a new expiry.

## Run start (in the script, not by hand)

- [ ] **`jawa/static_call Verse.Prefs set_RunInBackground true`.** Without it, focus
      loss stops rendering and every bridge call times out at 30 s. A run started with
      another window focused dies at preflight. The setting is in memory only, so
      repeat it after every launch.
- [ ] **`validation_core.log_revive(B)`**: `Log.Clear`, then a sentinel read back. If
      the sentinel is not seen, the run's log rows will be UNMEASURED. Say so at
      the start, not at the end.
- [ ] **`validation_core.tap_start(B)`** before the first tick, so the journal tap
      covers the whole session.
- [ ] **Tier truth: record `len(env.running)` and its sha256** (`jawa/running_mods`).
      A row that checks only "the mod is present" says nothing about the tier. Two runs
      are comparable only when their running lists match.
- [ ] **Control noise**: one save/load and ~600 ticks before any scene exists.
      Open it **before the first tick**, so you catch `Log.ErrorOnce` noise from that
      first tick (see `log-budgets.md`).
- [ ] **Fresh map**: `rimworld/start_debug_game_ready`. Lock the weather clear and set
      noon, clear the incident queue, destroy non-colonists, and pin the site.
- [ ] **No stale modal.** A `Dialog_ModSettings` or colony-naming dialog left open
      taints every later call, and closing the naming dialog can hop the current map.

## Each block

- [ ] Re-calm (`jawa/destroy_bulk filter=nonColonists dryRun=false`). Record
      `matchedCount`. Draft any colonist the block is not using.
- [ ] `clear_huge_plants(B)`, then `prepare_site(B, rect, rows, rid)`. If it returns
      False, the block's rows are UNMEASURED/SITE. Skip the block rather than run
      it on a blocked site.
- [ ] Spawn enough subjects. A block that needs 2 free colonists and gets fewer
      reads UNMEASURED. That is a staging flake: rerun it, and do not file it as a
      defect.

## Hang classes: "is the process alive" sees none of them

1. the run is already dead (died in <1 s on a focus refusal, then polled for minutes as running);
2. a frozen exception loop (Player.log stops, the game shows Not Responding at one full core);
3. a per-frame exception wedge (RealFoW `IndexOutOfRange` every Update once a 2nd map's ruins
   are destroyed: drop `mlie.nwnrealfogofwar` from test lists);
4. a stale modal;
5. a cold-load stall, or a silent subagent.

Watchdog: `python3 src/RimMandrake/Utils/belt_watchdog.py` every 5 minutes. Runbook:
`design/RimMandrake/live_test_hang_runbook.md`.

## Run end, before you report

- [ ] **Z / log budget**: `tap.lost == 0` **and** the `log_alive` sentinel is seen.
      If either fails, the row is UNMEASURED, whatever the error count says.
- [ ] **`certifiable`** is true only for mode `live`, not aborted, not raised. An
      `--only` run is mode `partial`, and `modcheck record` refuses it.
- [ ] **The Saves folder**: exactly the new files appeared, and 0 keepers changed size.
- [ ] **The mod list md5** matches the start value. The game is in the state you say
      it is in.
- [ ] **Every UNMEASURED row has its why** in `detail`. Every non-PASS row has a class.
- [ ] **Release the bridge** the moment you stop.
- [ ] **A full-suite selftest**: an `--only` slice of `run_selftests.py` never includes
      the `Utils/` lints, and a port is not done until the full suite has run. A low
      PASS count with "N SKIPPED as unchanged" on the evidence line means tests were
      skipped from the cache, not that failures are hidden.
