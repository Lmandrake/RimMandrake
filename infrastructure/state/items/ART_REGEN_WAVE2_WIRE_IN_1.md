## spec
Second artpipe batch: 4 creatures, 3 facings each (south/east/north), sitting
generated in `infrastructure/artpipe/done/` (validator-skipped — no reference
to compare against, not a pass/fail): `aa_frostmite_v1_*` (AA_Frostmite),
`gr_spidercat_v1_*` (GR_Spidercat), `insectomorph_v1_*` (Insectomorph),
`vaewaste_megatardi_v1_*` (VAEWaste_Megatardi). All 4 are "redo" rows from
`design/Jawa/worldbuilding/review/round2/decisions_propagated.json`
(owner-ruled full art replacement, not a missing-texture fix). Same wiring
step ART_REGEN_WAVE1_WIRE_IN_1 did for Kreetle/Horax/Fambaa/Dragonsnake/Zakkeg.

Donors identified by reading each ThingDef/PawnKindDef's texPath directly
(the offline def dump doesn't have these; the dump note said as much going
in):
- AA_Frostmite: `sarg.alphaanimals` (Alpha Animals), texPath
  `Things/Pawn/Animal/AA_FrostMite/AA_FrostMite`.
- GR_Spidercat: `vanillaexpanded.vgeneticse` (Vanilla Genetics Expanded),
  texPath `Things/Pawn/Animal/Insectoid/Spidercat/GR_Spidercat`.
- Insectomorph: `mlie.starwarsanimalcollection` — same donor as wave 1,
  texPath `swanimals/Insectomorph/Insectomorph`.
- VAEWaste_Megatardi: no donor — the def was absorbed wholesale into our OWN
  mod (`src/RimUtinni/UtinniPatches/Defs/Absorbed_VAEWasteMegatardi/`,
  STAT_NORM_WAVE2_RETIRE_1) when `vanillaexpanded.vaewaste` retired. texPath
  `Things/Pawn/Animal/Megatardi/Megatardi`. Fix goes straight into that mod's
  own Textures/ tree, no override mod.

## verify
Each creature's new art replaces the old at the correct texPath (dessicated
corpse and, for AA_Frostmite, the AA_FrostMite2/AA_FrostMite3 alternate-look
variants and, for GR_Spidercat, the AA_Dessicated_Spidercat corpse texture,
stay on donor art — same "primary look only" scope wave 1 used for Kreetle's
maggot stage), `validate_patch.py` stays clean, and each renders live (not a
magenta placeholder, not the old donor texture) confirmed by spawn +
screenshot, not inferred from a clean manifest.

## criteria
All 4 creatures render the new art in-game, confirmed by looking.

## Watch out
Two different mechanisms in play: AA_Frostmite and GR_Spidercat's donors ship
LOOSE PNGs at these texPaths already (not AssetBundle-packed), so this is a
plain file overwrite via mod load order — no need to re-prove the
loose-PNG-over-AssetBundle mechanism for those two. Insectomorph's donor
(mlie.starwarsanimalcollection) IS AssetBundle-packed and the loose-PNG-wins
mechanism was already proven live for this exact donor in
ART_REGEN_WAVE1_WIRE_IN_1 (2026-09-11, RimWorld 1.6.4871) — no need to
re-prove it, just wire and spot-check.

## Live verification result (2026-09-11)
Deployed all 4, then a temp-list restart (repo MINIMAL + the 3 donors + all 4
new mods) collided mid-session with a concurrent FOUNDRY window's OWN temp-list
restart for LOCKJAW_ART_WIRE_IN_1 — both write the same live ModsConfig.xml
with no cross-window signal beyond the bridge ledger, and the two lists merged
rather than either replacing the other (see `mandrake-rut-frostmiteartoverride`
etc. sitting alongside `mandrake.rsw.lockjawartoverride` in the same launch's
Player.log). The merged load came up fine both times regardless.

- **GR_Spidercat**: spawned + screenshotted, renders the new spindly-alien art
  clean. CONFIRMED.
- **Insectomorph**: spawned + screenshotted, renders the new art clean.
  CONFIRMED.
- **VAEWaste_Megatardi**: spawned + screenshotted, renders the new art clean.
  CONFIRMED.
- **AA_Frostmite**: first spawn's screenshot/portrait showed the OLD donor
  icy-chevron look, not our new art. Traced, not guessed: the PawnKindDef has
  `alternateGraphicChance=1` over THREE `alternateGraphics` texPaths
  (AA_FrostMite / AA_FrostMite2 / AA_FrostMite3) — every spawn randomly picks
  one, and we only overrode the first (matching the "primary look only" scope
  used for Kreetle's maggot stage in wave 1). Pixel-matched the portrait
  against the donor's own `AA_FrostMite2_south.png` on disk — exact match, so
  this spawn just rolled one of the two un-touched alternates (2-in-3 odds).
  Override file confirmed valid (real alpha, matches source bbox), correctly
  deployed (`deploy_custom_mods.py` VERIFIED in sync), and correctly ordered in
  the actual loaded mod list (`sarg.alphaanimals` then
  `mandrake.rut.frostmiteartoverride` immediately after, both in the crash log
  and the merged live list) — same load-order shape that worked for Spidercat.
  A second restart to force a lucky roll and catch the primary look on camera
  hung past the ~30s a MINIMAL-based restart normally takes (9+ min, no bridge
  token, high sustained CPU) and was killed rather than chased further.
  **NOT independently eyeballed on the primary look; wiring evidence is
  strong but not a sighting.** If this needs closing out to "seen", it wants
  its own bridge session with `count` high enough (8-10) on `jawa/spawn_pawn`
  to force a >95% chance of landing the primary variant, spawned somewhere
  cold enough camera-wise that a stuck restart doesn't collide with another
  window's test again.

Live state restored: `ModsConfig.FULL.LATEST.xml` and the live
`ModsConfig.xml` both carry the 3 new override packageIds (Insectomorph's
alongside wave 1's cluster after `mlie.starwarsanimalcollection`; Frostmite's
and Spidercat's each directly after their own donor). `modlist_swap.py
--status` reads `live currently matches: FULL` after restore. Bridge released.
