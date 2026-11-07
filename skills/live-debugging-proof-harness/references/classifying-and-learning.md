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
- **A live proof that ticks the game between its own dev-surface steps hands its body to whatever model the live pulse runs.** `deep_lake_proof` drives Recede/Restore by static call, but with `pondDepthEnabled` ON the pulses during its colonist rows StagePond the lake, which the LIFO refill cannot undo. A row that starts PASSing or FAILing right after an earlier row became reachable is a harness-ordering suspect before a mod regression.
- **A fixture class for a warning must be one the game warns about.** Flooded-sheer-pit warnings ('is tiring in deep water' at the `swimWarnAt` crossing) are emitted only for Ours pawns (player or a player prisoner), so a hostile or wild fixture can never see one. `pit_superdeep_walk.py` `PSW_flood_warned_before_under` asserts it with compressed `swimEnduranceHours` and `list_messages`; a risk with no row asserting its warning is unproven.

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
- **Before a walk card asks the owner about a behaviour, find the code path that produces it (or a proof row that saw it).** A walk stop expected three Store tanks joined by pipe to move to one level, but `RM_LiquidNetKernel.SettlePlan` says Store tanks only buffer and `RM_Levelling` links only open hose ends.

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
- **Per-call review of proof scripts does not converge.** Three fresh reviews in a row each found NEW site-scored-as-FAIL call sites. Fix structurally (`modcheck/preconditions.py` scopes withhold PASS/FAIL after any refused or non-taking call), then review once; stop a review loop that finds the same bug class twice.
- **A whole-sheet predicate (all rows UNMEASURED = red canary) must run on the instrument's own rows BEFORE any bookkeeping rows are appended.** The testq worker appended NOT_RUN rows for every requested `--rows` row first, so a red canary on a targeted job read DONE and ingested as a partial verify. Write the canary selftest red-first.
- **A modcheck chain function is CALLED offline before any live run.** `targeting.catalogue()`, the visual floor, `required_checks`, `runsheet` and `extension_proof` all walk every chain with a session-less `_DeclarationProbe`, so any side effect in a chain wrapper fires there too (the FlowWorks river wrapper ran `river_site.py` and replaced the map in a job that selected only core/hose chains). Guard side effects with `getattr(t, 'session', None) is None` and just call the chain.
- **A `static_call` proof scene that pokes a def or setting must register its restore BEFORE the poke**, and Stage (INVALID/ERROR/re-stage) plus a `finally` in Verdict must run it. KineticArms and ExplosiveKnockback undid pokes only inside Verdict, so a Build throw leaked a vanilla Bullet_Revolver extension, `kineticStrength=0` or `enabled=false` into the session, and Knockback restored hard-coded values instead of the prior ones. `validation.py` `proof_restore_wiring` pins it; grep other mods' `*Proof.cs` for `Settings.X = ` outside try/restore.
- **Every modcheck chain restores each Mod Settings field it set** (`set_setting`, `t.bridge_call` or `t.session.call` of `jawa/mod_settings_field`) to its pre-chain value, in the chain's `finally`. A chain that flips a setting for LATER chains to rely on no longer works: set it in each chain that needs it. Before a proof's `Settings("reset")` static call, call `t.remember_settings(type, fields)`. Static check: `src/RimMandrake/Utils/proof_restore_check.py` (REQUIRED selftest).
- **A validation helper that resets `t.upstream_failed` after an UNMEASURED row ('chain not poisoned') is only safe when no later row builds on that row's state.** In a stateful chain (site -> refuel -> enter -> heal) the next row runs on an unbuilt fixture and FAILs the mod for a harness reason (Bacta: refused Refuel -> 'pawn still on map after EnterBuilding'). Keep the reset opt-in per row (`independent=True`) and set `t.upstream_reason` so downstream UNMEASURED rows say why. Other `validation.py` files carry the copied helper.
- **A `return` inside a `with t.component(...)` row in a modcheck chain does not end the row; it ends the whole CHAIN.** Every later row is never entered: absent from the run record and from `required_checks.json`, because the offline probe walks the same code (TrophyCraft's crafting returned on PASS and its layer and pendant rows had never run). Put a row's early exits in a helper function called inside the `with` block. When you lift a declared UNMEASURED latch, restore the PRIOR `upstream_reason`, never None, because a later plain FAIL latches without setting one.

## Bridge calls that report success and do nothing
- **A harness hit must DEAL damage.** `jawa/damage` Blunt 3 on a 0.25-Blunt-armor hide returned success with `totalDamageDealt` 0.0, so a damage-only trigger never fired and the chain read "one hit did not swell it" as a mod FAIL. Read `results[].totalDamageDealt` and treat a never-landing hit as UNMEASURED. An arm whose OWN product is a manhunter must also declare `clockgate.expected_disturbance`, or `safe_advance` stops on 'turned hostile'.
- **`jawa/set_draft(pawnId=...)` without `drafted=True` changes nothing** (`JawaBenchJobTools.cs` SetDraft). Undrafted test pawns, and any undrafted spawned colonist, wander off decks, covers and corner cells during `step_game_ticks`, so a 'held' verdict is a harness artefact. Always pass `drafted=True` and read the draft back; hold a colonist with `order_pawn` to its own cell. Give a pump corner case its own pump so no neighbouring reel body is edge-adjacent to the corner cell.
- **`jawa/pawn_health action=restore` with no body part is always refused**, so scripts that 'healed' colonists that way healed nobody (`live_session` `heal_colonists`, `northstar_driver/site.py`). Check the reply of every heal call.
- **A live proof needs no new C# to read a mod's public statics.** `jawa/mod_settings_field action=get/set` resolves ANY public static field by type FullName (it tries STATIC first), and `jawa/static_call` takes typed args (`|`-separated: Map as `current`, IntVec3 as `x,z`, Pawn by bare thingIDNumber) for any public static method. Before listing a reader as owed C#, check whether the mod already exposes the value as a public static field or a static method with coercible parameters (drawbridge: `RM_Drawbridges.TippedCount/FellCount/CrashCount/RepathCount`, `RaisedAt`, `FreeHostileCount`, `Locked` and `RM_SuperdeepTrap.IsTrapped` were all reachable; only staging and per-leaf state needed a proof class).
- **`jawa/static_call` splits its args string on `|` into PARAMETERS and matches by count.** `args=""` means ZERO params, `a|b|c` means three. A proof method taking ONE string that it splits on `|` is unreachable: pass a non-empty dummy (`-`) or `;`-joined args, and have the C# split on `;` too. Cost: every `lines_proof` and Webwork `web_terrain_weather` row read UNMEASURED/HARNESS on their first live run.
- **`jawa/damage_log` events carry NO hit-part field** (keys: amount, damageDef, deflected, hediffsAdded, totalDealt, victim*, x, z, tick) despite the tool description promising 'hit part'. A runner that classifies wounds by `e.get('hitPart')` silently reads every hit as part ''. Read body parts from `jawa/pawn_get` hediffs (def + part + severity).
- **`governor.judge` on an EMPTY trigger list returns PASS CLEAN**, and `jawa/vitals` events returns only the newest `limit` triggers (the latch caps at 512; check `truncated`/overflow). A proof that a vitals trigger fired must require a non-empty list and match by `subjectId` (int) before trusting the verdict.
- **Under `python.exe` (bridge-side scripts), `os.path.relpath(p, REPO)` raises ValueError when `p` is on `D:` and REPO is `\\wsl.localhost\...`.** A try/except around a copy turns it into a silent 'screenshot copy failed' and a walk loses every labelled capture. Show a path with a relpath-or-absolute fallback (`water_scenes_walk.show_path`), never bare relpath, in anything `python.exe` runs. Still bare: `FlowWorks/northstar/live_session.py` (3), `scenarios_map.py` (2), `HugeThings/northstar/walls_slots_live.py` (3); most of the 59 repo sites are WSL-only tools and safe.
- **Never call `jawa/do_bill_now` inside a wait loop.** Each call re-issues the DoBill job (beforeJobDef DoBill -> restart) and cost 17 s on the 325 map, so `do_bill_now` + `ticks(300)` made zero progress for 520 s. Call it once, then tick in 500-tick chunks polling `list_things` for the product (`pwait.py`); a single call finished the pack in ~2000 ticks. On a just-spawned powered bench (press + conduits + `VanometricPowerCell` in one `spawn_batch`, no tick between) it returns 'JobOnThing(forced:true) returned null' and the pawn wanders off: advance a few ticks, check the bench reads powered, and treat a null as HARNESS until a retry also fails. Ingredient pick is nearest-to-bench first, so place the stack you need carried nearest the interaction cell. Run bridge scripts with `python -u`, or a killed run prints nothing and its `finally` never restores the setting it changed.
- **`jawa/research_finish_project` opens `Window_ResearchComplete`, which absorbs all input and force-pauses.** A later `rimworld/click_cell` selects nothing and `list_selected_gizmos` returns 0 gizmos with success true. Close it with `rimworld/close_window windowType=...` (check `get_ui_state` `anyWindowAbsorbingAllInput`) before any click or gizmo step.
- **`DebugSettings unlimitedPower` does not power a ColdStorage unit that has no power net:** `RSW_CoolingUnit_Wall` read 'Not connected to power ... not running' for 2000 ticks with it true. Stage a `PowerConduit` + `VanometricPowerCell` next to each cold unit.
