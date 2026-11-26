# FlowWorks walk of 2026-11-25 (version 0.1.0, NOT PASSED)

Item: `RIMMANDRAKE_ROUTE_FLOWWORKS_WALK_FINDINGS_OF_NOV_TWENTY_FIVE`. Format: `README.md` here and `gss_walk_20261124.md`.

- **When and where:** about 5:40 PM to 6:50 PM PST, ArchBig, the mod's small list
  (`design/concepts/FlowWorks/version/small_list.json`), save `FLOWWORKS_OWNER_REVIEW_VISIT13_SMALL_20261125_0957`, walk
  brief `design/concepts/FlowWorks/version/walk_brief/arrival_4.md`.
- **Build:** FlowWorks `033392ed2d` (the last change to the DLL, defs or textures before the walk; arrival 4 measured
  ArchBig in sync with source at 12:18 PM PST).
- **Result:** not passed; road back to Offline build (Stage 3):
  `design/concepts/FlowWorks/version/walk_brief/walk_4_result.md`. His event ending the walk: `OWNER:1795661493888672544`.
- **His words, whole:** `D:\ClaudeWork\rimmandrake\showings\FLOWWORKS_WALK3_20261125\his_words.md` (not in the repo) and the
  route item's prose. **His pictures:** `1.png` to `15.png` in the same folder (not in the repo).

## The defects

One row per statement. "Check" says what a check would assert and its candidate kind. No proof hook is needed unless the
row says so.

| station | his words (2026-11-25, about 6:35 PM PST unless marked) | picture | item | check, and its kind |
|---|---|---|---|---|
| 6 | "Station 6 still shows odd pit walls under water. Come on! You can see this yourself!" "Look at the difference between wet and dry. Look at the corners." | 1.png, 2.png | `RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE` | the wet pit's walls and corners draw as the dry pit's (station 5) under one water layer; a capture judged against the dry pit, plus a state read of the draw layers on one cell (fast in-game state read + look) |
| 7, 8 | "I then drained the Eastern side manually, and this known issue remained: [Image #3]. That cannot stand. Please fix!" | 3.png | same drill item | a drained side of a shut E/W sluice draws no water look (fast in-game state read) |
| 9, 10 | "N/S had similar issues remaining that need fixing." | 4.png | same drill item | the same for a N/S sluice (fast in-game state read) |
| 17 to 22 | "And look at all the stacks of "layered" blue on the edge of station 22. We REALLY need to figure out why the water looks so bad like this. I suspect you're applying multiple layers over each other instead of calculating a single one, and each one extends E/W to different regions, hence the layered effect that looks awful." | 5.png | same drill item | one computed water layer per cell; no stacked bands at a pit's edge (state read of layer count + look) |
| 17 to 22 | "Water look opacity is still a bit too blue, but that's polish." | 4.png | polish line, `design/concepts/FlowWorks/version/polish.md` | look only; not part of passing 0.1.0 |
| 17 to 22 | "No ripple effects were visible unfortunately, that would have helped." | 5.png | note on `RIMMANDRAKE_DESIGN_FLOWWORKS_WATER_WAVES_FOR_THE_NEXT_VERSION` (0.2.0) | look only, next version |
| 24 to 27 | "Station 24-27, there is only "change the style of the whole line." This should be upgraded to have all the options like we did in GSS immediately." | none | `RIMMANDRAKE_OFFER_FLOWWORKS_STYLE_REACHES_AS_SLACK_DOES` | the Choose style button asks the reach (this item, all connected, all on map) then the look, on every FlowWorks styled part (offline selftest + fast in-game state read) |
| 30, 33 | "Station 30 and 33, body under water looks good (but is drawn too far to the east onto the wall)." | 6.png | `RIMMANDRAKE_SHIFT_SUNK_BODY_OFF_THE_EAST_PIT_WALL` | every drawn pixel of a lying pawn lies inside the pit's water cells (fast in-game state read + look) |
| 69 | "I'm not sure what the fire under deck station was supposed to show ... the WHOLE THING went up in a whoosh and lit the bridge above it completely. I'm not sure what it was supposed to test." | 7.png, 9.png | note on `RIMMANDRAKE_REBUILD_FLOWWORKS_WALK_MAP_OLD_CODED_AND_STRANGE` | the station states one explicit thing it shows (map, look only) |
| 69, 75 | "And Tar is clearly WAY too flammable. Tar burns slowly, catches slowly, like dry grass. This is CRAZY fast, too fast, and solid." | 7.png, 9.png | `RIMMANDRAKE_SLOW_TAR_FIRE_IT_WENT_UP_IN_A_WHOOSH` | a tar strip's front reaches its far end no sooner than a dry-grass strip's, and tar beside a fire catches no sooner than grass (in-game scene, kind B) |
| 75 | "But I can't seen to Attach Fire to the tar. How do you light Tar? I actually don't know how to do this in the game." | 8.png | `RIMMANDRAKE_SHOW_TAR_LIGHT_ORDER_HE_FOUND_NONE` | a visible button lights burnable liquid; a fresh agent with no hint finds it (offline selftest + look) |
| 75 | "poured too much tar... it started spreading over the ground as misty grey squares (not tar-like at all). NEXT VERSION we need to do a LOT of work on what all the differnt fluids look like as thin sheets on the ground, how they flow, etc." | 8.png | `RIMMANDRAKE_DESIGN_FLUID_THIN_SHEETS_TAR_SHOWED_MISTY_GREY` (0.2.0) | look only, next version |
| 69 | "It should also make horrible smoke (burning tar produces choking smoke that should blow with the wind)." | 9.png | `RIMMANDRAKE_DESIGN_TAR_SMOKE_AND_GAS_ON_THE_WIND` (0.2.0) | design, next version |
| 69 | "RULING: Lighting Chemfuel like that is an Explosion that should work with Explosive Knockback. We should verify they play nice together and that it would blow everyone back." | 9.png | `RIMMANDRAKE_PROVE_LIT_CHEMFUEL_BLAST_THROWS_WITH_KNOCKBACK` (Explosive Knockback 0.2.0) | a lit chemfuel pit throws each colonist inside the blast (in-game scene, kind A) |
| 69 | "The "blowback" range of setting a whole moat of chemfuel on fire should be bigger than the squares of the moat itself (expanding air) ..." | none | `RIMMANDRAKE_DESIGN_KNOCKBACK_WHOOSH_FOR_BLASTS_OVER_ONE_CELL` (Explosive Knockback, next version) | design |
| 78, 79 | "Station 78/79 jetty's still look like two blocks stuck together rather than a seamless whole, FIX." | none | `RIMMANDRAKE_JOIN_JETTY_SQUARES_SEAMLESS_STILL_TWO_BLOCKS` | look only (art judge) |
| 48, 49, 70 | "Rope bridge should look like Ropes along the sides with planks laid upon the ropes. The rails should also be of ropes and cast shadows. The ropes coming from the ground should be aligned with the sides of the bridge, not sit in the middle of the walkway and connect to nothing." "Rope bridge "rails" should look like rope netting, and Rope bridge "no rails" should still have hand-guide rails as part of its construction." "There should be sparse wood slats on a rope bridge, that's it." | 10.png; reference 12.png | `RIMMANDRAKE_REDRAW_ROPE_BRIDGE_AS_ROPES_AND_SPARSE_SLATS` | look only (art judge against 12.png) |
| timber bridge | "For the Timber bridge, it's just all wrong." "No ropes tied to the ground for the wood bridge." | references 13.png, 14.png, 15.png | `RIMMANDRAKE_REDRAW_TIMBER_BRIDGE_FROM_HIS_THREE_PHOTOS` | look only (art judge against 13 to 15) |
| 56 | "Please decide what 56 station planks is for or remove it." (about 6:40 PM PST) | none | `RIMMANDRAKE_REBUILD_FLOWWORKS_WALK_MAP_OLD_CODED_AND_STRANGE` | the station states one explicit thing it shows, or is gone (map) |
| map | "We need you to add a new area with many complex surface deformations within a very large pit ... Please set up proper testing for walking under covered pits and plank-covered pits. ... Please work to significantly enhance this test map to expose as many explicit testing principles as FlowWorks really needs... many of them are old, coded, and strange." (6:50 PM PST) | none | `RIMMANDRAKE_REBUILD_FLOWWORKS_WALK_MAP_OLD_CODED_AND_STRANGE` | the map's coverage check names a station per lookable bar (map) |

## Passes he named (kept as bars, not defects)

Sluice gates half-covered when N/S and not when E/W (stations 7 to 10) · the water's transparency · tank graphics ·
sprinklers while working · a body under water, apart from its offset (30, 33) · Wanda standing in water at the correct
level (30) · new bridge art everywhere, with shadows from the elevated cables · pits at stations 34 to 39 · grate doors
· ladders and climbing gear · tar is flammable and does not instantly go away.

## Orders that are not the mod's

- "Please add Character Editor to all smallmod lists, beside the Zoom requirement.": done (`small_list.py check`
  requires `void.charactereditor`; the five walk tiers want it).
- "this should be a generic capability all colonists have for anything flammable, at the RimMandrake level, please pick
  the mod and file that ticket now": `RIMMANDRAKE_ADD_LIGHT_ANYTHING_FLAMMABLE_ORDER_TO_ALL_COLONISTS`, home RimMandrake
  Patches.
