# FlowWorks Mod Settings audit (F2, 2026-10-18)

Board row F2 of `design/RimMandrake/flowworks_finish_board_2026-10-18.md`. Standard: `design/RimMandrake/standing_rulings.md`
§"Every mod ships superb Mod Settings" (on/off per feature, defaults = shipped, tuning where a number is the experience,
all-off degrades gracefully, worldgen-affecting toggles labelled, biome mechanics promised inside our biomes only).
Offline only: read the C# screen (`src/RimMandrake/FlowWorks/Source/RimMandrakeFlowWorksMod.cs` lines 880-1906 plus the 14
section files it calls) and ran the instruments below. Nothing here was checked in a running game.

## Instruments run (MEASURED, this clone, 2026-10-18)

| instrument | result |
|---|---|
| `python3 src/RimMandrake/Utils/selftest_settings_screens.py` | 819/823 ok; the 4 FAILs are other mods (LeaningScrub, TheForge, ExplosiveGrowth, SWBestiary). FlowWorks: 12/12 ok, but **only the Hose section is covered** (`FlowWorks#Hose`); the main FlowWorks screen and its other 13 sections have no row |
| `python3 src/RimMandrake/Utils/settings_audit.py` | FlowWorks FAIL on one line: `burnDaysPerNotch` initialiser 1 vs Scribe default -1. **Not a defect**: -1 is the migration sentinel (`ExposeData` reads the old `canalBurnDaysPerLevel` key when it sees -1, else 1). The tool has no way to be told so |
| `northstar/selftest_flowworks_northstar.py` | was FAIL 2: 11 FlowWorks fields and 1 Machinery field ship in C# but were missing from the harness registry. **Fixed** (below); now PASS |
| `northstar/selftest_extensions.py` | was FAIL: the same 8 new switches were on neither the toggle floor nor the owed list, and one walk `## must be true` line had an ASCII `->` instead of the coverage arrow. **Fixed**; now PASS |
| `northstar/selftest_settings_registry.py` | PASS (now 284 rows, 168 toggles) |

Two other FlowWorks selftests fail on **a peer's uncommitted suspension-bridge work**, not on settings:
`selftest_flowworks_cover_breaks.py` (`Pits/Suspension/RM_MapComponent_SuspensionBridges.cs:366` and `:846` drop a pawn
without requiring an open pit) and `selftest_review_map.py` (5 new defs, wall climb / portable ladder / climbing gear /
suspension deck, have no review-map station). Left to their owners.

## Findings against the standard

**1. On/off per feature: met.** 183 settings fields in the main class (102 switches) plus 14 section classes. Every
feature built today has its switch: trench cover (`trenchCoverEnabled`, strength, cap, `trenchAiAvoidsCages`), pit
access (`portableLadderEnabled`, reach, `climbingGearEnabled`, slowness, safe jumps, safe skips, `pitRescueLadderEnabled`),
wall scaling (`RM_WallClimbSettings`: on, speed, raiders), suspension bridges (`RM_SuspensionSettings`, peer's, untracked),
pipes to centre (`pipesUnderToCentre`), deep swimming (`RM_SwimSettings`). Rail ladders, pump ports and hose/pipe girth
are art with no mechanic, so no switch is owed.

**2. Defaults = shipped behaviour: met where checked.** Field initialisers match the rulings: dig cap 16 notches = 8 m
(range 2-20 m), beach shelf off (drained means dry, 2026-10-18), pit room 3 m, fall death on from 6 m, sink clamp on,
own-faction capture off, open-water swimming off. `site_spec.SETTINGS` re-reads every registered initialiser, so a
drifted default fails a selftest; the four unregistered classes (finding 6) are not guarded that way.

**3. Tuning where a number is the experience: met.** Dig depth, dig cost curve, fall damage per metre and cap, fall
death range, drowning head fractions, trench cover, climb and ladder slowness, lake depth/roughness, burn rate, fuel
fires, thirst rate, sprinkler litres, swim endurance all have sliders with the shipped value named.

**4. All-off degrades gracefully: the check was too narrow; fixed in the harness, live proof still owed.** The
`all_off_still_digs` chain (`src/RimMandrake/FlowWorks/northstar/extensions.py`) turned off only the 50 names in
`FW_TOGGLES + PITS_TOGGLES`, so 52 main-class switches (trench cover, pit access, ramps, guardrails, every look switch,
level-exact water, deep beds ...) and every section switch (rivers, machinery, hose, thirst, sprinklers, kits) stayed
ON during "all off". It now turns off the registry's every-switch fixture, `settings_registry.all_off()` (168 switches),
and restores each to its shipped default. Checked offline with a fake bridge (168 set, 168 restored); it has not been
run live. Two limits remain: the four unregistered classes (finding 6) are still not in the fixture, and the chain digs
with `_dig_run` through the bridge, so it shows the depth grid still takes a dig, not that a colonist's dig order
still works with everything off.

**5. Worldgen and map-generation labels: partly met.** Labelled: "Landing repaints typed water (affects newly generated
maps)", "Ruined liquid works appear on new maps (map generation)", river colours (the planet layer redraws at load),
drill odds (in the body text: "new maps only"). **Not labelled in the switch's own label:** "Lakes have their own
floors" (decided when the map is made) and "Largest drainable lake" (lakes found from now on). Both say so only in the
tooltip or body. Filed.

**6. Biome-only mechanics: nothing to label.** FlowWorks is the engine, not a biome mod. It has no "works in other
biomes" switch, so the 2026-10-15 rule (such switches off and marked "Unsupported: may work outside our biomes, not
tested") has nothing here to apply to. The nearest is `swimOpenWaterEnabled`, which is off and labelled "(not
supported)". It is about the sea and rivers, not biomes. The VFE sprinkler adapter acts "inside this project's own
biomes", which is the design.

## Defects

| # | defect | where | state |
|---|---|---|---|
| D1 | 12 shipped fields (trench cover 4, pit access 7, `pipesUnderToCentre`) missing from the harness registry, so no default guard, no all-off, no floor | `src/RimMandrake/FlowWorks/northstar/site_spec.py` | **fixed** this commit; 8 new switches put on the owed list in `src/RimMandrake/FlowWorks/validation.py` (their live rows are owed on their items) |
| D2 | all-off chain switched off 50 of 168 switches | `src/RimMandrake/FlowWorks/northstar/extensions.py` | **fixed** (registry fixture); live run owed |
| D3 | walk coverage line used `->` not the arrow, so `selftest_extensions` FAILed | `design/validation_walks/RimMandrake/FlowWorks.md` `## must be true` (outside the hash) | **fixed** |
| D4 | four section classes not in the registry: `RM_SwimSettings` (Swimming/RM_Swim.cs), `RM_WaterMendSettings` (RM_WaterBodyMendGame.cs), `RM_WallClimbSettings`, `RM_SuspensionSettings` (peer work in flight). About 25 switches have no default guard, are left out of all-off, and are not on the floor | registry | filed `SETTINGS_REGISTRY_FILL_FOUR_SECTIONS_UNSEEN` |
| D5 | the main FlowWorks screen has no row in the settings-screens selftest (only the hose section does) | `src/RimMandrake/Utils/selftest_settings_screens.py` | same item |
| D6 | `settings_audit.py` reports the `burnDaysPerNotch` migration sentinel as a defaults mismatch (a false FAIL) | `src/RimMandrake/Utils/settings_audit.py` | same item |
| D7 | stale labels: "Superdeep limits who can shoot whom" (the rule is now any cliff edge of the set height); "Superdeep cells trap" and its tooltip speak of the old absolute rule beside "Pits trap by relative height" | main screen | filed `FLOWWORKS_LABELS_POLISH_LEVELS_TO_METRES` |
| D8 | numbers shown in levels rather than metres, against the rewire's "strings in metres": "Levels a ramp spans: N", "Sink per depth level (cells) (superdeep: x4)", slow climb "two levels for a person", fill-in "one level", drained pond "two levels / four", flow per pulse, rain fill "level(s) per pulse", drill "fill-unit(s) per cycle" | main screen | same item |
| D9 | map-generation switches not labelled in their label (finding 5) | main screen | same item |
| D10 | river and machinery checkboxes with no tooltip (carry animals / visitors / items, seasonal and torrential flood counts, silt-traps, breach washes catch, ruin stock, pipe adapters) | `Rivers/RM_RiversSettings.cs`, `Machinery/RM_MachinerySettings.cs` | same item |

D7-D10 are text in `src/RimMandrake/FlowWorks/Source/RimMandrakeFlowWorksMod.cs`, which a peer has uncommitted edits in,
so they were filed, not edited. No C# changed in this audit, so no DLL rebuild was needed.
