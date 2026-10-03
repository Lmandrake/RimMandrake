# RimStarWars: Sarlacc — validation walk
subject: src/RimStarWars/Sarlacc  (packageId `mandrake.rsw.sarlacc`)
deps: Ludeon.RimWorld.Anomaly (Devourer body, render tree, think tree and comp are reused by reference); loadAfter `mandrake.rm.biomes` (soft: the Stillsand cave row and the incident biome gates)
list: no named modset_builder tier yet; the smallest tier is BRIDGE + `mandrake.rsw.sarlacc` + the five DLCs (add `mandrake.rm.biomes` for the Stillsand cave row)
status-hint: SARLACC_FIRST_SCRIPT_1 — three stages of one creature (swimmer, anchored mouth, cistern/throat), seven changed-return hediffs, two once-per-map swimmer incidents; first script drafted, never run live

Sources: `src/RimStarWars/Sarlacc/About/About.xml` description, `Defs/**`, `Source/*.cs`, `Transient/work_STILLSAND_EVENTS_20261003.md`.

## must be true
Agent-owned, not hashed. Chains and components are in `src/RimStarWars/Sarlacc/validation.py`.
- Every def the mod ships loads in the running game (swimmer pawn kind and race, anchored mouth, cistern and throat, buried-seep marker, seven hediffs, two incidents, the road's think tree); a def that fails to load is dropped whole and silently. [About.xml; `Defs/`] → defs_resolve.every_shipped_def_resolves
- The def-probe instrument can say "not found". [method] → defs_resolve.control_probe_can_say_absent
- The Stillsand cave row `RSW_PreciousCave_SarlaccSeep` (a brine pool plus the seep marker) loads when `mandrake.rm.biomes` is present. [`MapGeneration/RSW_PreciousCave_SarlaccSeep.xml`] → defs_resolve.stillsand_cave_row_resolves
- All 11 Mod Settings fields (9 toggles, 2 tuning numbers) write and read back, numbers numerically, and restore; defaults are the shipped behaviour. [`RSW_SarlaccSettings.cs`; CLAUDE.md "superb Mod Settings"] → settings_roundtrip.settings_probe_finds_fields, settings_roundtrip.<field>_round_trips for each field
- A swimmer carries a birth-water reserve and shows it on its inspect pane; a thing without the comp shows no such line. [`CompSarlaccSwimmer.CompInspectStringExtra`; About.xml "Stage I"] → swimmer_reserve.swimmer_reads_a_water_reserve, swimmer_reserve.probe_can_miss_the_line_control
- With `rootingInPlayEnabled` off a swimmer never roots, even with its reserve spent. [`CompSarlaccSwimmer.CompTick`] → rooting.rooting_off_swimmer_stays
- A swimmer whose reserve runs out roots where it stood into `RSW_SarlaccAnchored` and stops being a pawn, and says why in a message when `rootingMessagesEnabled` is on; `reserveDrainMultiplier` is what makes that quick enough to read. [`CompSarlaccSwimmer.RootHere`; About.xml "Fork 1"] → rooting.exhausted_reserve_roots_where_it_stood
- A cistern is a placeable landmark def that loads and spawns. [`ThingDefs_SarlaccCistern.xml`] → cistern.cistern_spawns_and_reads
- Breaching a cistern floods the surrounding sand into shallow water for days, runs the ecosystem-death messages and turns it into the drained throat; it is the only kill. [`CompSarlaccCisternBreach.cs`; About.xml "Fork 5"] → UNCOVERED: the breach is a `CompInteractable` done by a pawn at the wall and no bridge tool presses an interactable comp; a companion `[Tool]` is the missing piece
- A pawn that survives being swallowed and spat free is granted one of the seven changed-return hediffs, occasionally a second. [`CompSarlaccSwimmer.GrantChangedReturn`; About.xml "Fork 8"] → changed_return.changed_return_granted_to_a_survivor (reports UNMEASURED: a swallow cannot be staged to completion with live prey)
- The anchored mouth strikes a pawn standing beside it now and then. [`CompSarlaccAnchoredMouth`; About.xml "tithe"] → UNCOVERED: statistical (mtbStrikeDays 20); the roll cannot be forced (debug_process.md section 4)
- On a Long Shade map one swimmer comes up once per map and swims toward the biggest dew ring; on a Stillsand map one comes up once per map toward the biggest seep; each roots there for good and leaves a take sign (disturbed sand and a message) on every swallow. [`IncidentDefs_SwimmerRoad.xml`, `IncidentDefs_SwimmerSeep.xml`, `RSW_SwimmerRoad.cs`] → incidents.swimmer_road_longshade_only, incidents.swimmer_seep_stillsand_only, incidents.take_signs_leave_sand_and_message, incidents.rooting_evacuates_the_patch (each reports UNMEASURED: biome-gated, needs a generated map and game days)
- The sarlacc's art, the tribal stage labels and the interior are as designed. → UNCOVERED: visual (art is the judge pass's; every texPath is a placeholder reuse of Anomaly art) and the pocket-map interior is owed (`SARLACC_HABITAT_BUILD_1`)

## the walk
1. [D] defs_resolve, settings_roundtrip: pure reads and a write/restore of the settings class
2. [B] swimmer_reserve: clear a 24-cell area, spawn a swimmer (faction none) and read its inspect pane; spawn a seep marker as the absent-line control
3. [B] rooting: spawn a swimmer; rooting OFF plus reserveDrainMultiplier 1e9, 40 ticks, expect no anchored mouth and the pawn still readable; then rooting ON, expect `RSW_SarlaccAnchored` at the cell, the pawn gone and the reserve message; restore both settings
4. [B] cistern: spawn a cistern and read it back
5. [S] incidents and changed_return chains stay UNMEASURED with their reasons

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "reserve exhaustion cannot be forced inside a test" — `reserve -= drainPerDay / 60000 * movingFactor * reserveDrainMultiplier` every CompTick and the first rare check runs at once (`nextRareCheckTick` starts 0), so a x1e9 multiplier roots the swimmer within a tick (`CompSarlaccSwimmer.CompTick`); the check goes red if the toggle is dead.
RULED OUT: "an incident dry-run proves the biome gate" — `fire_incident` dry-run reports success=False with canFireNow=False for any reason, so it cannot tell a gated map from a broken gate; those components say UNMEASURED.
RULED OUT: "a def-count of the cave row proves it ships" — its tag is the namespaced class `RimMandrake.Stillsand.RM_PreciousCaveDef` and it is MayRequire `mandrake.rm.biomes`; absent that mod it is dropped by design, so it is checked on its own and reports UNMEASURED when it does not resolve.
RULED OUT: "the Sarlacc settings class has no Mod Settings screen" — `RSW_SarlaccMod` draws all 11 fields in `DoWindowContents`; the static check reads both the Scribe and the UI side.
