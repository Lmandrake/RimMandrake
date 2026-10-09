# Leaning Scrub venomvine sitting: run-sheet (prepared offline 2026-10-09, BENCH helper)

Item `LEANINGSCRUB_VENOMVINE_SITTING_1`. Sitting deferred to next session by card 2026-10-08 21:55. Needs: owner present, bridge held (`rimflow bridge take --for "venomvine sitting"`), game up.
Nothing here was tested live. Every tool name below comes from `skills/rimbridge/SKILL.md` and `stage_review.py`; confirm param names with `rimbridge_client`'s guard (run under `python.exe`).

## 0. Things to know before you start

1. **Seven forms render the SAME picture right now.** Rearing, Quench, Walking, Hoard, Sworn, Shedding and the Thicket all have one deployed texture with identical md5 `9dfff4bfcf63` (a black thorny cane block with pale curved thorns). In game he cannot tell them apart by art. Twitcher has its own file (`0b67d2c716f9`). Crown, Dripping and Hollow have four variants `_a.._d` each.
2. **The Thicket's sheet pick (B, `ls_regen_RM_Venomvine_v1`) and Hoard's pick (J, `0vv_hoard_venomvine_v2`) are NOT what is deployed.** Both pick columns are renders not yet installed (Thicket texture is the shared one above). Nothing installs until he rules in the sitting.
3. **"11 forms" = 8 sheet rows + Walking, Sworn, Shedding.** The roster (`RM_LeaningScrub_Biome.xml` lines 199-218) also carries Sleeper (0.01) as a 12th, plus Strangler/Weeper/Lure that are NOT in the roster. Sleeper is outside the 11; ask in passing only if he wants it.
4. **"Patch growth" is not a named thing in the code.** I read it as the group of mechanics where a stand changes or spreads over time: Walking (runners, tail dies back), Dripping (regrows venom), Hoard (grows items in), plus Smother-craft. See section 3. If he meant something else, ask him first.

## 1. The 11 forms

Roster weight is the `wildPlants` commonality. Defs: `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/` (`RM_LeaningScrubVenomvineForms.xml`, `RM_VenomvineSixForms.xml`; Thicket is `src/RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Plants/RM_Venomvine.xml`). Renders: `D:\Luke\dev\_artpipe\done\0vv_<form>_venomvine_vN.json` (artpipe_state `find venomvine`: 241 hits, none pending).

| # | defName | what it is (from its description) | live art | renders available | his sheet ruling | open question |
|---|---|---|---|---|---|---|
| 1 | `RM_VenomvineThicket` | shrubland thicket, chest-high mass, lightless inside; body-size barrier (blocks big creatures) | shared placeholder (`...\EnvironmentalHazards\Textures\Things\Plant\RM_VenomvineThicket\`) | thicket v1-v3, `ls_regen_RM_Venomvine_v1` | B (ls_regen v1), note "variations" | Install B? Does he want more variations? |
| 2 | `RM_DrippingVenomvine` | amber beads of venom on every cane; harvest gives RM_RawVenom x3, regrows (`harvestAfterGrowth` 0.3) | 4 variants a-d | dripping v1-v2, `gapfin_RM_DrippingVenomvine_v1` | B (gapfin v1), no note | Install B? Does the regrow harvest read right? |
| 3 | `RM_TwitcherVenomvine` | one whip-crack lash at whatever comes close, then droops about an hour | 1 file (own art) | twitcher v1-v2 | A (keep deployed), note "variations" | Keep art; does he want variants? Does the droop show? |
| 4 | `RM_HollowVenomvine` | dead grey cane tubes; Jawa-sized pawns can crawl inside; no venom comp | 4 variants a-d | hollow v1-v2 | A (keep deployed) | Done on art? Can a pawn crawl in (barrier only)? |
| 5 | `RM_CrownVenomvine` | tall single black column with a flower on top; dustflutters mob it when wind drops (stall cloud); rarest, weight 0.002 | 4 variants a-d | crown v1-v2, `gapfin_RM_CrownVenomvine_v1` | B (gapfin v1), no note | Install B? Is 0.002 too rare to ever be seen? |
| 6 | `RM_RearingVenomvine` | canes lie low; a body that pushes in snaps it upright and it "tells" (message); Gale masks it | shared placeholder | rearing v1-v4 | redo: "STOP USING THIS GRAPHIC AND MAKE VENOMVINE!" | Art redo confirmed? Does rearing look different from resting? |
| 7 | `RM_WalkingVenomvine` | wedge with rust-ochre runners; each Gale lays runners downwind, old tail dies back | shared placeholder | walking v1-v4 | none (no sheet row) | Art pick; is the creeping speed right? (section 3) |
| 8 | `RM_HoardVenomvine` | squat coiled knot; grows in loose items and dead gear; cutting it gives all back | shared placeholder | hoard v1-v4 (J = v2) | J, "Keep all of these for now, Venomvine is a mechanic as well as graphics, so we will need to reason about this during Bench settings." | Art; is 4 h grow-in right; keep dead-gear hoarding? |
| 9 | `RM_QuenchVenomvine` | knuckled cane with slate-blue sheen; bursts firefoam once when fire is near, then spent for days | shared placeholder | quench v1-v4 | redo: "STOP USING THIS GRAPHIC AND MAKE VENOMVINE!" | Art redo confirmed? Does the burst stop a fire? |
| 10 | `RM_SwornVenomvine` | trained, flat-topped hedge with fibre knots; thorns spare sap-marked pawns; the only sowable form (sowWork 600) | shared placeholder | sworn v1-v4 | none (no sheet row) | Art pick; does the mark pass-through read clearly? |
| 11 | `RM_SheddingVenomvine` | ragged stand, sunward face stripped; each Gale throws a V of thorn litter downwind (`sheddingLength` 8) | shared placeholder | shedding v1-v4 | none (no sheet row) | Art pick; V length 8 right? |

Per-form art decisions already in the ledger: `infrastructure/state/art/events/BENCH.jsonl` (the 2026-10-08 rulings) and `infrastructure/state/art_rulings/2026-10-08_leaningscrub_sheet_2026-10-05.decisions.json`. Per-form variant letters on the sheet: Crown/Dripping A-D, Hollow A-F, Hoard I (one). Purges for Hoard were NOT executed.

Where to look at renders before the sitting (so he is not seeing them cold): `D:\Luke\dev\_artpipe\_artsrc\0vv_<form>_venomvine_vN\` (check the file names with `artpipe_state.py find <term>` first).

## 2. Tunables (Mod Settings, `RM_LeaningScrubSettings` in `src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs`)

Master `modEnabled`. Per form:
- Thicket: `venomvinePassabilityEnabled`.
- Twitcher: `twitcherLashEnabled`, `twitcherLashDamageFactor` 1, `twitcherLashRecoveryFactor` 1.
- Dripping: `drippingRegrowEnabled`.
- Crown: `crownMobEnabled`.
- Rearing: `rearingEnabled`, `rearingHours` 2.
- Walking: `walkingEnabled`, `walkingMaxCellsPerMap` 120 (slider 10-400).
- Hoard: `hoardEnabled`, `hoardGrowInHours` 4, `hoardKeepsDeadGear`.
- Quench: `quenchEnabled`, `quenchRecoveryDays` 3.
- Sworn: `swornSparesMarkedEnabled`.
- Shedding: `sheddingEnabled`, `sheddingLength` 8.
- All forms: `smotherCraftEnabled`, `smotherDays` 30, `smotherYieldFactor` 1 (smothering a stand yields 30-40 items per def's `yieldCount`).
Per-def tunables in XML: Walking `runnerGrowth` 0.05, `maxStep` 2, `tailDieChance` 0.5, `tailYield` 10 (all marked PROVISIONAL); Rearing `minBodySize` 0.8, `minGrowth` 0.5; barrier `passFreelyBodySize` 0.8, `blockBodySize` 1.5.

## 3. The growth mechanics: where they live and what he must see

Source: `src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs` (six forms, one MapComponent doing the work; plants only tick every ~33 s, so changes are slow), `RM_VenomvineRooms.cs` (Dripping regrow: `RM_RegrowingHarvestExtension`), `RM_SmotherCraft.cs`, `RM_TwitcherLash.cs`, `RM_TheLean.cs` (the wind heading).
Downwind comes from `RM_MapComponent_Lean`'s locked heading. **On a map that does not lean, Walking and Shedding stay put.** Confirm the map leans before judging them.

| mechanic | trigger | what he must SEE | how to provoke it |
|---|---|---|---|
| Walking | each Gale onset | new thin runners 1-2 cells downwind of the front; oldest tail cell dies back into "dead venomvine" (10 items) | force `RM_Gale` weather (below), step a few hundred ticks, count cells before/after; repeat 3 Gales |
| Shedding | each Gale onset | rust-coloured V of thorn litter (8 long) downwind; litter scratches a pawn | same Gale |
| Dripping regrow | harvest | after harvest the stand stays and regrows to 0.3 before it can be harvested again | draft a colonist, designate harvest; or step 1 day |
| Hoard | items lying in or beside it | item vanishes into the stand after 4 h; cutting the stand drops everything | drop 2 items + a corpse next to it, step 4+ h |
| Rearing | pawn with body size >= 0.8 pushing in | stand snaps upright, message appears; masked during Gale | walk a large animal or colonist through |
| Quench | fire within reach | firefoam burst, then spent for 3 days | light a fire cell next to it (`jawa/spawn_thing` Fire or dev tool) |
| Twitcher | anything close | single lash then droop about an hour | walk a colonist next to it |
| Smother-craft | player smother job | stand converts after 30 days, yield | optional, skip unless he asks |
Test pawns: one small (Jawa-size, <0.8), one large animal (>= 1.5, blocked by a thicket-style barrier).

## 4. Staging plan (one map, grid, daylight, clean)

Skill: `.claude/skills/rimworld-live-review/SKILL.md`. Python under `python.exe` from WSL. `stage_review.py` spawns pawns, not plants, so plants go via `rimworld/spawn_thing` in a small script (add a `--plants` flag to `stage_review.py` rather than hand-driving; the skill authorizes it).

**Map.** Start a quicktest map on the LeaningScrub biome (`rimworld/start_debug_game_ready`, or `jawa/world_tile_map_generate` on an `RM_LeaningScrub` tile, then `jawa/map_commit`). Settlement maps are culled when time steps unless colonists live on it: spawn 2-3 living `PlayerColony` colonists first (also the test pawns). Mod list: trimmed review list that includes `mandrake.rm.leaningscrub` and `mandrake.rm.environmentalhazards` (the Thicket depends on it), all five DLCs. Confirm the deployed LeaningScrub DLL and textures match the repo (`deploy_custom_mods.py --mod LeaningScrub`) and that `ModsConfig.xml` is parsed, not grepped.

**Grid key.** Anchor `A = (X0, Z0)`, a verified-open lush-soil cell (check with `rimworld/get_cells_info` over the whole 48 x 36 block). Cell for form `f` is `(X0 + 12*col, Z0 + 12*row)`. Pitch 12 leaves room for Walking and Shedding to travel and Shedding's V of 8.

| | col 0 | col 1 | col 2 | col 3 |
|---|---|---|---|---|
| row 0 | 1 Thicket `(X0, Z0)` | 2 Dripping `(X0+12, Z0)` | 3 Twitcher `(X0+24, Z0)` | 4 Hollow `(X0+36, Z0)` |
| row 1 | 5 Crown `(X0, Z0+12)` | 6 Rearing `(X0+12, Z0+12)` | 7 Walking `(X0+24, Z0+12)` | 8 Hoard `(X0+36, Z0+12)` |
| row 2 | 9 Quench `(X0, Z0+24)` | 10 Sworn `(X0+12, Z0+24)` | 11 Shedding `(X0+24, Z0+24)` | test pawns/items `(X0+36, Z0+24)` |

Put Walking and Shedding on the downwind-free side (read the Lean heading from the map first and mirror the row so the V and runners have open ground). Spawn each plant at full growth (growth param to be confirmed against `rimworld/spawn_thing`; if absent, `jawa/spawn_batch` with a growth field, or step time). For Dripping also spawn a second copy at low growth to show the regrow.
For art, spawn **all variants side by side** for Crown, Dripping, Hollow (a-d) in a short strip in front of each cell (4 cells apart), and one cell per candidate render for forms whose pick is not deployed (install candidates to a scratch copy first, never the repo).

**Order of bridge calls** (all in one `python.exe` script, then read the screenshot):
1. `rimflow bridge who`, `take --for "venomvine sitting"`; `./game` measure; `game_focus.preflight()` (Run in background).
2. `jawa/set_current_map`; `jawa/map_info` (biome must be RM_LeaningScrub); `set_time_speed 0` and verify `ticksGame` holds.
3. `jawa/damage` Bomb 9999 on every `hostile` pawn and turret, loop to 0; then `jawa/clear_area dryRun=false` over the block (chunks, filth, plants, items) so only the grid is there.
4. `jawa/set_terrain` to a soil terrain under the grid if the cells are rock/sand; verify with `rimworld/get_cells_info`.
5. Spawn colonists (living, fed, healed), then plants per the key; read back with `jawa/list_things` that all 11 defs (and variants) exist, count them.
6. Daylight: `jawa/time_set_ticks` to about hour 12 (2500 ticks = 1 h; read the hour off a test shot). `jawa/weather_set` clear.
7. `jawa/set_fog` `action=unfog rect="X0-4,Z0-4,52,40"`; `jawa/clear_ui`; `jawa/window_list_close typeName=EditWindow_Log`.
8. Frame: `jump_camera_to_cell` to the block centre, `rimworld/frame_cell_rect`; keep `rootSize` 14-18; `get_camera_state` read-back (right map, not world view). `jawa/take_screenshot fileName=venomvine_grid` (no `.png`). **Look at it yourself first.** Per-form close-ups after that, one per cell.
9. Mechanic pass (section 3), in this order so nothing contaminates the next: Rearing, Twitcher, Hoard (drop items), Dripping harvest, Quench (fire last in its own corner), then **Gale last**: `jawa/weather_set RM_Gale lockWeather:true`, `step_game_ticks` in chunks of <= 2000, re-pause, count Walking cells and screenshot the Shedding V.
10. Save the keeper only after step 8 and before step 9 (clean grid), then a second save after step 9 if he wants it.

**Keeper save names:** `LEANINGSCRUB_VENOMVINE_GRID` (clean grid) and `LEANINGSCRUB_VENOMVINE_MECH` (after mechanics). Back up the Saves folder's keepers first; afterwards stat `Saves/<name>.rws` and confirm a NEW file appeared and no existing file changed size (`save_game` has written the current slot instead). Never fullscreen or steal focus; no flyer tests apply here.

## 5. Card draft (plain language; use `question-card`, headers <= 12 chars)

1. **Art, forms with no row** — "Walking, Sworn and Shedding look the same right now. Which look do you want for each?" Options: pick from the four renders each (v1-v4), ask for new ones, keep the shared one for now.
2. **Redo** — "Rearing and Quench: make fresh venomvine art, or keep what is in the game?" Options: make new art (note kept word for word), keep current, fold into another form.
3. **Install picks** — "Thicket, Dripping, Crown and Hoard have a picked render that is not in the game yet. Install now?" Options: install all four, install after you've looked in game, leave for now.
4. **Walking speed** — "Walking venomvine creeps one or two cells each Gale and its tail dies back. Too fast, too slow, right?" Options: slower, as is, faster/more cells.
5. **Hoard** — "Hoard keeps dropped items and dead gear after 4 hours. Keep both, items only, or longer?"
6. **Rarity** — "Crown is 1 in about 500 of the plants. Make it findable, or leave it a rare sight?"
7. **Forms to keep** — "Any of the 11 you want cut, merged or turned into a different mechanic?" (free text open.) Also the `LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1` question: do you want more forms pitched?
Record clicks as "decision taken by question card" (no quote flag); only text he types is his words.

## 6. After the sitting

Write his rulings to `infrastructure/state/art_rulings/` and the item; file new artpipe jobs for any redo only after he confirms the form stays (note verbatim); install through `art.py install`; write what the live pass taught (including false theories) into `src/RimMandrake/LeaningScrub/validation.py` and the walk `design/validation_walks/RimMandrake/LeaningScrub.md`; then `rimflow bridge release`.
