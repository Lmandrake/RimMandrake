# BENCH_REBOOT_HANDOFF_202610090437 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610081427`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Ruled art sheets are carried out by ONE command now: `python3 src/RimMandrake/Utils/art/art.py enact <decisions.json>` (preview), then `--apply`. Today the owner found rulings sitting unused for days (Canopy Swinger -> Ookala hidden by a rename; 62 failed redraws silently counted as done). Sheets now show per-row freshness and a banner — before telling him a sheet is current, run enact's preview on it and read the banner; never claim "all incorporated" without that.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Floating dashboard widget is live (concept C look, scheduled task `RimFlow Pulse`, server rm-pulse.service); it froze twice and was fixed (0d93c27be) and made draggable (163c36d8); the drop-position save is unconfirmed. `./pulse back` / "I'm back [3h|since 5pm]" digest installed (new windows only).
- Magenta in game until replacements are picked/installed (his choice, card 20:43): Swarmling, Eopie (all 15 A-E files), Lothcat female S/N, Scurrier male. Nothing deployed since the 19:30 restart — every touched mod composes a DLL, so deploy waits for the next restart.
- Sketto east in-flight master v3 (`D:\Luke\dev\_artpipe\_artsrc\sketto_fly_master_v3_east\sketto_fly_master_v3_east.png`) awaits his OK before stage 2 (wing poses + lock).
- Great Devourer is now `RM_Gulloth` ("gulloth") in LongShade; RSW twin deleted (07ff006d0).
- Canon library swept to realistic references: 95 entries changed, 43 animation-only (Transient/canon_realism_sweep_2026-10-08.md).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `GREYSEA_FLOOR_PASS_1` — offline checks done; live floor staged once but grows no flora and lacked the 4 rarest species; released; NEXT: after GREYSEA_FLOOR_FLORA_ZERO_1 closes, restage per Transient/greysea_floor_sitting_2026-10-08.md and hold his sitting.
- `SEAT_MEMORY_CLONES_DRIVES_1` — phases 0-2 landed (tool cap verified live, memwatch + host sampling, harness slice, object store on trial with telemetry); host sampling is OFF (--no-host) because powershell from a service may steal focus; NEXT: on 2026-10-15 run `python3 src/RimMandrake/Utils/scratch_clone.py report` and put the store verdict to the owner.
- `AWAY_DASHBOARD_BUILD_1` — built and running; gaps: drop-position save unconfirmed, phone push disabled (not ruled), crash vs deliberate kill indistinguishable; NEXT: ask the owner after a day of use whether the widget held position and whether alerts were worth acting on (metrics in ~/.local/state/rm-dashboard/metrics.jsonl).
- `FLYER_STABLE_BODY_GATE_1` — Sketto pilot master v3 east passed canon 5/5, south/north v3 queued; 11 PekoPeko flight jobs held in D:\Luke\dev\_artpipe\_withdrawn\flyer_unlocked_recipe_2026-10-08\; NEXT: get the owner's OK on the v3 east master, then file stage 2 per Transient/sketto_design_2026-10-08.md §8.
- `CANON_REALISTIC_REFERENCE_SWEEP_1` — sweep finished (212 entries); NEXT: close it with the last sweep sha after spot-checking 3 more entries' images.
- `ART_SHEETS_TAIL_1` — all six ruled sheets rebuilt with freshness banners (63ef9f330, 07ff006d0); Greentide fully drawn, he was about to review it; NEXT: when he finishes a sheet, run `art.py enact <its decisions> --apply` and put any CONFLICTS to him in one card.
- `LEANINGSCRUB_VENOMVINE_SITTING_1` — filed, 8 sheet rows + 3 unsheeted forms; NEXT: schedule the in-game sitting with him.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A redo+rename ruling hid its redraws from the sheet (joined by old name) and enact counted old jobs as done (filed: lessons 3cd991a8d).
- Player.log silence + busy CPU was reported as a hung game; it was not (filed: lessons 1f0c08612).
- art ingest keyed on the path string: an absolute path duplicated 231 ledger events (filed: lessons ba9a38195).
- memwatch "35 OOM kills" were 37 planted 128 MiB pen kills from selftest_run_selftests.py (see: Transient/away_dashboard_build_2026-10-08.md).
- pywebview scans public js_api attributes; a window handle there froze the widget (see: Transient/away_dashboard_fix_2026-10-08.md).
- selftest_enact.py writes Transient/enact_test_sheet_*_jobs.json into the real repo on every run (see: this handoff; deleted by hand 2026-10-08).

## Closed since the last handoff (3)

- `JAWABENCH_DLL_REDEPLOY_1` — 0f2f76dc0
- `DONOR_PLANT_OVERRIDE_VERIFY_1` — 5cb5cc22e
- `MIRROR_REPACK_LEAK_FIX_1` — 0b43abbe0

## Filed and still open (12) — the next seat's queue

- `LEANINGSCRUB_VENOMVINE_SITTING_1` — Settle all 11 Leaning Scrub venomvine forms (art + patch-growth mechanic) in one in-game BENCH sitting with the owner, game up
- `FLYER_STABLE_BODY_GATE_1` — Flyer-ready static gate + stable-body flip-book regeneration for every flyer
- `SKETTO_FLIGHT_DRAWSIZE_FIX_1` — Sketto flying sprite draws at flyingAnimationDrawSize 1.0 vs 1.25 grounded, so it shrinks 20% at take-off; set it so flight matches or exceeds ground 
- `BIOME_GROUP_SIZE_WALK_1` — Per biome, on its review sheet, walk every custom creature with the owner and set the typical group size it appears in (wildGroupSize/herd); part of t
- `EXTRA_ART_PER_BIOME_COMMISSION_1` — Once a biome's group sizes and herd/pack/domestic lore are settled, commission its gender art (every herd animal) and juvenile art per the guidelines 
- `DESICCATED_LOOKALIKE_FAMILIES_1` — Dried-out corpse art shared by look-alike family (~450 jobs; 308 races draw no desiccated corpse today). Blocked until per-biome creature art is final
- `CANON_HERD_LORE_ARBITRATION_1` — Arbitrate 45 canon creatures whose herd/pack status canon leaves UNCLEAR - Transient/canon_herd_lore_2026-10-08.md
- `LOAD_RED_BASELINE_DRIFT_1` — 2026-10-08 19:30 full-list load vs baseline: patch ops failed 6 vs 5 (new: UtinniPatches ops on BMT_GreyLady, BMT_Thrumbungus — likely caverns cut), C
- `CANON_REALISTIC_REFERENCE_SWEEP_1` — Replace cartoon/animated reference images in all 137 canon_references entries with realistic ones (live-action, film, realistic art) wherever they exi
- `GREYSEA_FLOOR_FLORA_ZERO_1` — Grey Sea floor grows ZERO flora: plants above the lowest wildOrder need lower-order neighbours and the lowest-order plants need a terrain the floor ge
- `BRIDGE_STALL_DIAGNOSTIC_1` — When a bridge call blocks past ~60 s, record what the game's main thread is doing (managed stack dump / current tick phase / top job) to a file, so a 
- `AWAY_DASHBOARD_BUILD_1` — Build the beautiful floating 'what is happening / while you were away' dashboard widget with red (OOM, stopped window) and amber (idle-and-done, no su

## Commits

```
f06e97149 BENCH ledger: close MIRROR_REPACK_LEAK_FIX_1, release GREYSEA_FLOOR_PASS_1 with next step
a583da175 scene harness: handoff notes, nothing built yet
32d66ab3f live checks 2026-10-08: progress log, probe scripts, results
38d3bc308 ledger: live checks 2026-10-08 verify events (Watchers W1-W3, fallen wire A1-A4, ticker, scald, warscar, liquid heat, chill pump, dishes)
163c36d80 Pulse widget: manual no-activate title-bar drag (pywebview drag region fails on a NOACTIVATE window)
07ba5826c Away dashboard hang: debugging notes
579d7a824 Watchers: fix three live-found defects (sign TickRare threw NotImplementedException so orphan signs never cleared; RM_Watcher body had no Moving limb so it could not be generated; remains config error); live tier live_20261008b
281d1b91d Pulse autostart task: MultipleInstances Parallel (IgnoreNew refused every re-run while the widget lived)
0d93c27be Pulse widget: fix GUI hang (pywebview walked Api.window into .NET); startup stages, hang watchdog, async SetWindowPos
9b17744c3 Install I'm back digest hook; digest window settable (3h, 90m, 2d, 17:30, 'since 5pm', 'last 6 hours')
07ff006d0 Enact 2026-10-08 card decisions: FeverWood seven redraws, live x'd art deleted (Swarmling, Eopie, Lothcat, Scurrier), Nerf E installed, Great Devourer -> RM_Gulloth
294cac7a1 Away dashboard build log: final state
69c85b19f Pulse: classify OOM kills from the kernel log (planted pen test is not an alarm); widget never resizes on data
d4b968909 ledger: BLOWER_ROOM_COOLER_1 + LAUNCH_HELD_COLONIST_WARNING_1 implemented
d2454e533 Dry-air blower is a room cooler that never heats (BLOWER_ROOM_COOLER_1); launch dialog names held colonists (LAUNCH_HELD_COLONIST_WARNING_1)
68bde2c78 Pulse widget: fit to content, self-reload, autostart task, I'm-back hook (prepared)
593156f3a Pulse spine + floating widget for the away dashboard (AWAY_DASHBOARD_BUILD_1)
29a03f481 Canon realism sweep: progress log, regenerated INDEX, mon_calamari note on deleted rakata image
a569e6663 Canon realism sweep: gungan
bdb00e232 Canon realism sweep: neimoidian, nelvaanian, nikto, ortolan, pantoran
... 199 more: git log --oneline bea86861e..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     FOUNDRY: Watchers lifecycle + L1 reads + new DLL load checks

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

