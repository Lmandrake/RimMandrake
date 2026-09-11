# BIOME_TEXT_PORT_1

Port the 27 already-written RUT_ biome descriptions onto the LIVE donor BiomeDefs by
patch, and relabel the 3 never-relabeled biomes (2,571 tiles incl vanilla Scarlands).
Closes all 4 plot leaks named below and the label-over-donor-voice split.

Source finding (now decayed off `Transient/`, per the item's own warning): the
Phase 3 text/plot-leak audit of `WORLDMAP_FINAL_REVIEW_1`,
`Transient/final_review/findings_text_lore.md` (git history still has it — this
section is the load-bearing copy).

## spec

**The structural fact everything hangs on.** `BiomeNames_Ashkarr.xml` is
label-only by design (its own header says so). The live planet runs donor
defNames on ~23 of 29 painted biomes — so the player reads OUR label over the
DONOR's `<description>`. 27 fully-authored `RUT_*` BiomeDefs
(`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_*.xml`) carry campaign-voice
descriptions, but before this item **no patch in any deployed mandrake mod
touched a biome `description`** — only labels were ever patched.

**The 4 plot leaks (all donor-inherited; 0 in anything WE authored):**

1. WORST — `AB_MechanoidIntrusion`, labeled "the Rust Cathedral" (236 tiles).
   Donor text: "A mechanoid hive was dismantling this biome, turning its mass
   into computronium, and hastily left it abandoned for unknown reasons...
   even the trees turned into mechanical contraptions." This is a near-miss on
   the §GM smart-metal/mind-factory truth and violates ban 6.1 ("the mind's
   nature… plot only, gate-kept") from `design/Jawa/worldbuilding/biomes/
   the_rust_cathedral.md`.
2. `Scarlands` (vanilla Odyssey, 90 tiles, **never even relabeled** — showed
   lowercase "scarlands"). Donor text invented a bombed city and "mechanoids
   lurk... waiting to awaken and kill again," contradicting ban 6.6 (the
   Forgotten Sentinels defend only, never pursue) and the sheet's own "every
   ancient danger here has already been opened and destroyed"
   (`the_scarlands.md`). The donor `settleWarning` carried the same
   contradiction ("dangerous insects and rogue mechanoids... waiting to
   awaken").
3. `AB_PropaneLakes`, labeled "the Propane Lakes" (2,531 tiles). Donor text:
   "As propane is a compound that doesn't occur naturally, this is probably
   the remnant of some weird ecological or industrial experiment gone awry" —
   asserts an industrial origin. The Lakes are terramanufacture's far end
   (§GM, `TERRAMANUFACTURE_CANON_1`) — a past-why the player is not cleared
   to read.
4. `AB_RockyCrags`, labeled "the Forsaken Crags" (1,135 tiles). Donor text:
   "In the ancient past it was partly terraformed by a mysterious humanoid
   alien race simply known as Forsakens" — invents a rival ancient race,
   corrupting the campaign's one reveal ladder (players taught wrong ancients
   before the Rakata gates open).

**The 3 never-relabeled biomes (2,571 tiles):** `Scarlands` (90, see leak 2),
`Wasteland` (donor mod BiomesPlus, ~1,126 per `wasteland.md` SS0), and
`AridShrubland` (vanilla Core, ~665 per `arid_shrubland.md` SS0) — none of
these three appeared in `BiomeNames_Ashkarr.xml` at all (not a bug in that
file; they were simply outside its original 30-biome census), so they showed
raw lowercase donor labels ("scarlands", "wasteland", "arid shrubland") on
top of donor description text.

**The "three mods arguing" quality issue (§B, not itself a leak):** under our
labels the player also read donor filler like "the Greentide" → "Overgrown
jungle.", "the Miasma" opening with an Earth mangrove encyclopedia entry, "the
Poison Forest" mentioning Earth poplars, five `AB_*` biomes shipping a
`<color>` "Biome difficulty:" footer. The remediation ports every donor def
that has both (a) an entry in `BiomeNames_Ashkarr.xml` and (b) a matching
already-authored `RUT_*` description — this closes the leaks AND the quality
class in the same pass, per the finding's own corrective note ("that single
pass clears all 4 leaks and the whole three-mods-arguing class").

**Mapping used (donor defName -> RUT_ source, all in the same BiomeDefs
folder), built from `BiomeNames_Ashkarr.xml`'s existing label-defName
correspondence plus each `RUT_*.xml`'s own "Replaces the donor `X`" header
comment where present:**

| donor defName | RUT_ source | note |
|---|---|---|
| AB_MycoticJungle | RUT_TheRot | |
| AB_PropaneLakes | RUT_PropaneLake | judgment call, see below |
| BiomeGRimond | RUT_BlueDesert | donor owns ~1/1030 tiles only |
| AB_RockyCrags | RUT_ForsakenCrags | plot leak 4 |
| ZBiome_Badlands | RUT_CrackedLands | |
| PoisonForest | RUT_PoisonForest | |
| ZBiome_DesertOasis | RUT_WeepingStones | |
| AB_MechanoidIntrusion | RUT_RustCathedral | plot leak 1, worst |
| BiomeCypreJungle | RUT_Greentide | |
| AB_OcularForest | RUT_Contagion | |
| AB_FeraliskInfestedJungle | RUT_Webwork | |
| AB_GelatinousSuperorganism | RUT_Slime | owns 0 tiles today |
| AB_MiasmicMangrove | RUT_Miasma | |
| AB_TarPits | RUT_Sump | |
| COMIGO_GreaterSwamp_Tropical | RUT_FeverWood | |
| AB_PyroclasticConflagration | RUT_TheForge | |
| Desert | RUT_Desert | |
| ExtremeDesert | RUT_ExtremeDesert | label is "the Deep Desert" (R22), description text is RUT_ExtremeDesert's own |
| Scarlands | RUT_Scarlands | plot leak 2, + settleWarning, + first-ever label |
| Wasteland | RUT_Wasteland | first-ever label |
| AridShrubland | RUT_AridShrubland | first-ever label (kept lowercase, matches RUT_'s own) |

**Not ported (deliberately):** `RUT_NightsideIce`, `RUT_TwilightSea`,
`RUT_GreySea`, `RUT_TheScald`, `RUT_Umbra` already run under their own RUT_
defName on (almost) all their tiles — nothing to port onto.
`RUT_Jawa_BackgroundWater` never has a tile (isBackgroundBiome, implemented
false). `ZBiome_Grasslands` ("the Pyrelands" donor "stormy savanna") has no
RUT_ BiomeDef yet — `the_pyrelands.md` is written, the def is not — so it is
NOT one of the 27 and is left alone; a known gap, not silently invented.
That's 21 ported + 5 self-owning + 1 background = 27, matching the item's own
count.

**Judgment call recorded — `AB_PropaneLakes`:** `AB_PropaneLakes` is the LAND
biome (2,531 tiles, `canBuildBase=true`). The only already-authored "propane"
text is `RUT_PropaneLake` — a SEPARATE, not-yet-painted WORLD-TILE WATER
biome for the lake proper (its own header: "NOT painted onto any tile by this
file or this pass... this item does not touch it"). `RUT_PropaneLake`'s
description ("A black mirror of liquid fuel under the brightest sky on the
planet...") is thematically apt and verified SSP-clean against
`the_propane_lakes.md` (no mention of the buried war lab — that's SSGM,
banned from any def field by that sheet's own ban 8). No other
already-written propane text exists, so it was reused verbatim on
`AB_PropaneLakes` rather than composing new prose from the `.md` sheet, which
DOES carry SSGM content. This is the one place a literal "replaces the donor"
header comment does not exist in the RUT_ source; recorded here so a future
reader does not mistake it for an oversight.

## verify

- `git diff --stat` on `src/RimUtinni/UtinniPatches/Patches/BiomeNames_Ashkarr.xml`
  and `BiomeDescriptions_Ashkarr.xml` (new file) shows the label + description +
  settleWarning operations for all defNames in the mapping table above.
- `python3 skills/rimworld-modding/scripts/validate_patch.py` against both files
  with `--mods-config infrastructure/state/modlists/ModsConfig.PRESWAP.20260908_apparel_isflesh_gate.xml`
  (newest full ~606-mod backup; the live `ModsConfig.xml` was a 6-mod spike at
  patch time, per `rimworld-deploy`'s own warning never to validate against a
  small spike) and `--defs` pointed at RimWorld's `Data`, the Workshop content
  folder, and `Mods` — ran clean: **0 errors, 2 advisory warnings** (both
  pre-existing multi-match patterns already accepted in the shipped
  `BiomeNames_Ashkarr.xml`, not introduced by this item: `COMIGO_GreaterSwamp_
  Tropical` resolving twice inside one donor file, and `Desert`/`ExtremeDesert`
  legitimately spanning Core + a GRiNDTerra retexture mod).
- Each of the 4 named plot leaks: confirm the new `<description>` (and, for
  Scarlands, `<settleWarning>`) text no longer contains the flagged phrase
  ("computronium"/"mechanical contraptions", "waiting to awaken and kill
  again", "industrial experiment gone awry", "Forsakens... alien race") —
  true by construction, since each was a full `PatchOperationReplace`, not an
  edit of the donor string.
- Not verified live in-game (no cold load run this pass — out of scope for a
  text-patch item; the deployed mod copy at
  `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\UtinniPatches`
  still needs `deploy_custom_mods.py --apply` before a save reads this text).

## criteria

- [x] All 4 named plot leaks addressed by a description (or settleWarning)
      patch, sourced from the campaign's own already-authored RUT_ text, no
      new lore invented.
- [x] The 3 never-relabeled biomes (Scarlands, Wasteland, AridShrubland) get
      both a label patch (`BiomeNames_Ashkarr.xml`) and a description patch
      (`BiomeDescriptions_Ashkarr.xml`); Scarlands also gets its
      `settleWarning` ported.
- [x] Patches validate clean (0 errors) against the full mod list.
- [ ] NOT done this pass, flagged as owed: deploying the mod copy
      (`deploy_custom_mods.py --apply`) and a cold-load/quicktest confirmation
      that the new text actually renders in the biome tooltip. Whoever next
      touches `UtinniPatches` in-game should fold this deploy in rather than
      restart without it.
