# FOUNDRY_HANDOFF_202610191447 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610190749`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Every donor-retirement trap this session was in SAVES, not defs: a removed mod leaves CLASS names (`VFEInsectoids.Area_Hive` blanked the screen via AreaManager -> Vehicle Framework NRE) and removed THING defs (1528 `RM_TreeMartyr`, 91 `AB_Mech_Ruined*`) that the def-name census cannot see. Load only the `*_AREAFIX2` copies (never the originals), run `save_class_census.py` and `save_def_census.py` on any save before loading it, and read the FIRST exception. The 536-mod donor-free list (535 + `mandrake.rut.weathersuite`) cold-loads clean: harvest xref 0, ours 0 exceptions, 0 texture misses.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Direct Sun: he ruled ONE geometry-only model (55 C at zenith, no biome kinds), on every sunlit map, sand glare from any natural sand, tree shade = projected crowns, full, overlay + mouseover + one ground-tint experiment; Sun & Shade becomes its own piece inside Baroque Biomes. Code not started (blocked behind the boundary move).
- Three ambiguous plant-sheet readings (bryolux = new Blue Desert plant or move the Rot's? firevine = new Weeping Stones tree or move the Forge's? witches' oyster 'drop, already in Rott' = kept, or remove?) and four icon rows with a bare 'drop' (fang pendant, simple research kit, pilgrim journal, half-extracted core) are still IN the game; under his later rule 'drop means remove the item' they would be removed.
- The dessicated corpses sheet (48 rows) is still unruled; he stopped all sheet servers (no time), review tonight with `art.py review awaiting-pick` (~3.5 min).
- Freezing vents ported, death pall dropped (no zombies in Utinni), gray pall kept. 19 mutators ported (Archonexus dropped, lab = another mutator, temples = design item).
- I invented nothing new in numbers this session; the Contagion Bloom 0.2/10 C is superseded by Direct Sun.
- `D:\Luke\dev\_rm_old_git_2026-10` (4.2 GB old repo .git) holds 14 branches/stashes NOT on origin: salvage first or delete? Needs his word.
- The 12 unratified Cherry Picker cuts (IceSheet, SeaIce, 7 weapons, 3 animals) are a gap, not a decision.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `DONOR_FOUR_RETIRE_JUST_GET_IT_DONE` — deployed, donor-free load clean (xref 0, ours 0); NEXT: close it with the 08:07 harvest evidence.
- `ASHKARR_WEATHER_INSTALL_THE_SLEEPING_STORMS` — mod activated on the 536 list, natural triggering and nightside geothermal zero UNMEASURED; NEXT: run those state reads on a nightside map.
- `DONOR_MUTATORS_MIGRATE_TWENTY_TWO_CAME_HOME` — 19 mutators deployed, IDs in the ported save are PREDICTED; NEXT: get_defs the 19 and check the ported save's IDs against a fresh dump, then live tile check after Bench's biome repair.
- `CONTAGION_MECHANICS_BUILD_1` — A3-A5 pass, A1 (exposed visitor took no Burn dose) and A6 (Coalescence absorbed 6, stayed stage 1) FAIL; NEXT: read the code for A1/A6, fix, rerun on RM_TestSite_contagion_v1_AREAFIX.
- `CAULDRON_MECHANICS_BUILD_1` — never run on a healthy session; NEXT: load RM_TestSite_cauldron_v1_AREAFIX2 and run its owed rows (then Leaning Scrub SCRUB_SETTINGS_WIRE_MASTER_CANNOT_GREY, Pyrelands, SUMP_TAR_LIVING_SYSTEMS_1 A6).
- `WORLDMAP_REPAIR_LOST_BIOMES_ROCKY_TEXTURES` — Bench's; ported-mutator save copy `..._PORTED_MUTATORS_NODEATHPALL.rws` waits in D:\Luke\dev\_rmscratch\ported_mutator_saves; NEXT: Bench runs the biome repair on it.
- `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES` — blocked behind `SUNSHADE_MIGRATE_MOVE_NOT_CHANGE`; NEXT: build the Sun & Shade boundary move keeping every name.
- `DEV_SCRATCH_DIRS_MIGRATE_OFF_LODESTARS_LAWN` — _artpipe, _artstore, _rmscratch, _rmbuild, _obs, _rmdashboard still in D:\Luke\dev; NEXT: after a quiet artpipe, relocate behind one path setting.
- `JAWABENCH_BRIDGETOOLS_DLL_REBUILD_OWED` — build.py would REMOVE jawa/weather_set etc. from the game copy; NEXT: decide the build flags (--gm / --allow-tool-removal) at the next game-down window.
- `DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO` — feeder timer rm-donor-regen-feeder (10 min) and rm-donor-regen-install (hourly) recreated by systemd-run, gated by the fixed eligibility; ~147 eligible failures requeue at 10 per run; NEXT: re-arm both timers if WSL restarted (systemctl --user list-timers).
- `TEMPLE_RUINS_DESIGN_SEVERAL_FAITHS` / `DERELICT_LABS_DESIGN_ONE_MORE_MUTATOR` — filed from the derelict study; NEXT: design pass on vanilla/Odyssey ruin machinery.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- A removed mod's class names persist in saves and break AreaManager then Vehicle Framework (filed: infrastructure/state/lessons/20261019T123616Z-FOUNDRY-retired-donor-mod-leaves-class-names.md).
- Never leave a broken game running; close it at the first error storm (filed: infrastructure/state/lessons/20261019T123616Z-FOUNDRY-never-leave-broken-game-running-owner.md).
- Removed THING defs left in saves throw 'Exception spawning loaded thing null' on load (filed: save_def_census.py doc note and its lesson).
- gate_browser.py stopped draining the test server pipe, so big sheets hung Edge for 600 s; fixed (see: design/RimMandrake/art_sheet_speedup_2026-10-19.md).
- GPT's review of the art automation found 18 real defects (case-twin paths, first-facing-only, whole-file commits); fixed and tested (see: Transient/gpt_review_art_automation_2026-10-19.txt).
- `rimflow close`/`done` is terminal; `drop` is refused on done items (FIREHAWK_FLIGHT_BEHAVIOR_1) (see: using-rimflow skill).
- My own close-out commit swept three of another seat's stale deletions under a guessed 'retired' message; check a peer's tree against its handoff before committing it (see: the Bench handoff 'not BENCH's work' line).

## Commits

```
64db6c8fc Donor art: hourly install of 10 finished dregen_ renders (accepted-for-now)
f26b50ad1 Art enact report 2026-10-19 (178 rows, pinned); icons decisions with followed notes
201b056a7 Restore fang pendant and simple research kit: a bare 'drop' on picks_icons rows reads as drop the renders
9ad0235ba Drop cooked skewer, fang pendant, Pyrinth blade and simple research kit (picks_icons_sheet_2026-10-19)
1bb8d312c Transient: pin proposed rimworld-review-sheets skill patch (art review 2026-10-19)
71d91a918 Retire art of the four items he dropped on picks_icons_sheet_2026-10-19 (defs removed in the next commit)
0b6cc5246 art.py review awaiting-pick: every row waiting on his pick, one gated page, served and opened, no agent
a6065ff12 Enact picks_icons_sheet_2026-10-19: 40 installs, folder retires, 4 notes made random pools, Tolluk cap own icon
3ccea8d6d save_def_census.py: unresolved THING defs in saves (cut-def residue), selftest, doc note, lesson
642ce3baf freshness docs: stale rows labelled on serve (owner card 2026-10-19), no longer whole sheet refused
c4a845c11 ledger: live testing verifies on fixed saves (Contagion A3-A5 pass, A1/A6 fail)
6378053d5 live testing 10-19b: TreeMartyr only in cauldron site
d476ae71e live testing 10-19b: cauldron AREAFIX site load storms on cut RM_TreeMartyr (1528 plants); stopped
8668090c8 art sheet: drop unused controls; stale rows labelled on serve instead of the sheet refused
436e46a14 live testing 10-19b: AREAFIX load clean, VF spawns fixed, weather suite + Contagion suite evidence
7e22dc2de gate req 13: sidecar log to a file, not a pipe (deadlocked big sheets); Edge capped at 90 s, no timeout retry
5abbe0efe donor_regen_jobs: atomic no-replace requeue, per-row cap, backoff re-read, real 429 detection, as_posix (#12-16, #18)
8ebfb63ae donor_regen_install_hourly: commit only its own changes, from a private index; publish only its own commits (#8-11)
02cb50977 regen_eligibility: close gate false-eligibles from the GPT review (#1-7, #17)
670de4036 design: art sheet speed-up analysis + GPT review (Edge gate pipe deadlock found; 5 options)
... 128 more: git log --oneline 3eef4a5f3..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/flowworks_owner_walk_art_sheet_2026-10-11.decisions.json   generated or another window's scratch; not FOUNDRY work
 M Transient/biome_ffar/phase0_remaining_art_sheet_2026-10-16.decisions.json   generated or another window's scratch; not FOUNDRY work
 M Transient/modcheck/fixtures.json   generated or another window's scratch; not FOUNDRY work
 M deployed/config/ModsConfig.before-tier-fw_gss_sitting.xml   generated or another window's scratch; not FOUNDRY work
 M infrastructure/state/ledger/events/OWNER.jsonl   generated or another window's scratch; not FOUNDRY work
?? Transient/biome_ffar/awaiting_pick_sheet_2026-10-19.decisions.json   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S1_20261017T084726.txt   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S1_20261017T084802.txt   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S1_20261017T092155.txt   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S1_20261017T110253.txt   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S1_p00.png   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S1_p03.png   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S1_p10.png   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S1_p14.png   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S2_20261017T084824.txt   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S2_20261017T092355.txt   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S2_20261017T110404.txt   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S2_p00.png   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S2_p10.png   generated or another window's scratch; not FOUNDRY work
?? Transient/fw_scenes/live/S2_p30.png   generated or another window's scratch; not FOUNDRY work
... 136 more uncommitted paths (by top-level dir: Transient 128, deployed 3, src 2, (root) 1, conversations 1, infrastructure 1): git status --short
```

