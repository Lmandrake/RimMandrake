# Classifying a run's findings, and making the next run find the mod bug

## Telling MOD, SITE and HARNESS apart

| ask | if yes |
|---|---|
| Does the same row PASS on a different, cleaner staging (a spare plot, the 11-mod list, a second scene of the same geometry)? | SITE or HARNESS, not MOD |
| Did the mod refuse something it is *supposed* to refuse (no room for the lead-out, occupied cell)? | SITE: the staging asked for the impossible |
| Did the window close before the design's contract says the effect is due? | HARNESS |
| Was the instrument able to see? (tap `lost`, sentinel, tier, profile, a `success:false`) | if not, the row is UNMEASURED/HARNESS, not a FAIL |
| Does a hand re-stage reproduce it, traced every 10 ticks, with the quantity the symptom is about? | if it does, and the cause is in the mod's code, MOD |

Write **"presumed, unproven"** for a row you did not trace. On 2026-10-11, RL6 and SL4
vanished once the giants were cleared. They were recorded as presumed SITE, not
folded into R1–R6's proven cause.

## The 2026-10-11 tally: what "mostly ceremony" looked like

| finding | class |
|---|---|
| matrix block: `load_catalog` needs numpy under python.exe; the live mode never ran its offline gate | HARNESS |
| two real-flow rows: flat 260-tick window shorter than the design contract | HARNESS |
| relay chain: hose aimed beside the relay, lead-out onto an unprepared gap | SITE |
| relay chain again: clock started before the pump had power | HARNESS |
| v2 L2: clone DLL ≠ deployed DLL | HARNESS (run location) |
| v2 L2: an internal one-time import flag compared as a player setting (`INTERNAL_FLAGS` ignored) | HARNESS |
| v2 P4: ladder row's pit occupied by the previous row's forced pawn (rows never run live) | HARNESS (staging) |
| E9 and every budget: Verse.Log 10k cap | HARNESS (instrument blind) |
| style_hose R1–R6: giants outside the rect re-blocking the site | SITE |
| E9, L2 and every end-of-run budget: 1,000-entry journal ring | HARNESS (instrument blind) |
| a native crash in a donor mod's background task during world churn | not ours |
| **`RM_MapComponent_Hoses` 3x over budget: per-tick cache defeated by staggered checks** | **MOD (perf)** |

Eleven of twelve were not mod bugs. Three lessons come out of that, and you should act
on all three:

1. **Harness faults come in classes.** Audit the class before the second run. A
   full-list run surfaces 2–4 new harness assumptions per ~15-minute run. One
   fresh-context, read-only audit of the whole fragility class found 8 at once
   (2026-10-11). The class is camera, tick stepping, idle pawns, site margins, fog,
   save/load timing, log budget and tier. Do it before the second full-list run, not
   after the fifth.
2. **A proof only ever run on its small tier carries tier assumptions**: journal start
   line, settings set, pawn staging. Rows that were added and never run live (P3f/P4f)
   are untested code. Expect them to fail on their first full-list run, and budget
   time for that.
3. **The mod bug came from a perf row, not from a functional row.** The functional rows
   had been tuned until they passed. The perf row was the one row that read the real
   hot path on a realistic map.

## Pointing the next run at the mod

After the harness is honest and the run is green, spend part of the time on where the
mod could still be wrong. Each item below becomes a row that can go red, or a filed
lead.

- **Leads noticed while debugging.** For example: `Building_LiquidPump.TryDraw` increments
  `Moved` and has already taken the channel level when `tank.TryAddLiquid` returns false,
  so the level is lost. `TankToFill` should make that unreachable, but nothing asserts
  it. Write the assertion.
- **Conservation.** Units drawn == units delivered + units held, across relays, saves and
  removals.
- **Upgrade paths.** Old saves (pre-port fixtures), imported settings, one-time flags. One
  example: the hose port's `hoseSettingsImported` flag is flipped by the mod on every
  upgraded install. `--reset-settings` would have re-armed the import.
- **Rows never seen red.** For each, plant the defect (or run the old shape) once and
  watch it fail. A planted-defect fuzz needs the restored file `touch`ed before the
  rebuild (see `run-checklists.md`).
- **The full list.** Run on the owner's list, not only the mod's tier. The first full-list
  run of FlowWorks v2 found four faults that no tier run could have shown.
- **Perf on the real hot path** (`perf.md`).

## Recording what the run learned (`debug_process.md` §0, §2.4, §3 rung 3)

- **A check that goes red for the reported reason** before the final fix. It reads the
  same quantity the symptom is about, not a correlate.
- **Each informative dead theory** goes in the walk's `## anti-guessing notes` as
  `RULED OUT: <theory> — <the check or source line that killed it>`, and gets a guard
  component if a machine can watch it. Example from 2026-10-11: "RULED OUT: the relay
  chain drops units — a hand trace every 10 ticks moved 5 units A→B→tank once the pump
  had power".
- **The harness fix is committed beside the check.** The commit names the class and the
  row id. Scratch probes are thrown away. Only checks survive, because scratch files
  vanish (the `ns_probe_*` files did on 2026-10-01).
- **A Transient run log is for the owner to read once.** It is never the only record of
  a finding. If a lesson is about the *harness* in general, fold it into this skill.

## modcheck, walks and recording traps

- **Recording.** `modcheck.status.record_run` is the only record, and it is hash-bound.
  A recorded run goes STALE when any mod-folder file changes, except `validation.py`,
  `human_review.py` and `northstar/`. Even filing a `review/` folder or a helper `.py`
  in the mod did it. Finish mod-folder edits before the run you record.
- **`modcheck run <Mod>` REWRITES the live `ModsConfig.xml`** (it swaps to MINIMAL). It
  is an expensive-list action, not a query.
- **A walk's lines in the wrong format parse as ZERO lines and still exit 0.**
  `modcheck validate` prints "these lines BIND once validated" followed by nothing, so a
  walk validated in that state would bind an empty checklist. The parser wants
  `- [ ] \`snake_case_id\` — text` under bold subheads. Copy the format from a VALIDATED
  walk (Pits). `validate` now refuses a section that parses to zero bars.
- **`### cannot show` ids have the OPPOSITE polarity.** A collector that took every
  checkbox id in a section into one list put a rejection line into the must-show floor.
- **A walk filed under a mod's old name is invisible** to `find_walk`. For example,
  `FluidCanals.md` was not found for FlowWorks. Check that `find_walk` resolves before
  spending a sitting on a checklist.
- **A bar about CHANGE cannot be judged from one frame.** The judge took `shots[-1]`,
  while 10 of AtmosphericBase's 23 bars were about motion. Count how many of a
  checklist's bars the judge can actually see before drafting more.
- **Never hand-edit a result JSON** (it was done once, 2026-10-04, to test how SKIP
  reads). Fix the harness and rerun. Delete the edited file before anything is recorded.
- **Two runs that disagree**: compare `len(env.running)` and its sha256 first. 3 of 15
  FAILs in a run labelled "gimmesomeslack tier" (the B3/B4d/R2 draw counters) PASS on the
  real 11-mod list, because that run was on 550 mods.
