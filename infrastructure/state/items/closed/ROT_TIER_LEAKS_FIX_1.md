# ROT_TIER_LEAKS_FIX_1 — regate the fungal-soil trade to the free Rot biome, and take "the Force" off the free pale tree

Caused by `ROT_SCORING_SITTING_1` (turn 1). Two tier leaks, two mods: campaign
`mandrake.rut.fungalsoiltrade` (`src/RimUtinni/FungalSoilTrade/`) and free `mandrake.rm.therot`, plus one
campaign patch. Design: `design/Jawa/worldbuilding/biomes/rot_bedazzle_review_2026-10-02.md` §1 (b) and the
reverse slip, §4 row 0, §8. Ruling: **build first: land the decided work plus the giant** (decision taken by
question card 2026-10-02 10:20 PDT). Law: Q11a (the franchise is campaign-tier IP; invented content is free).

## spec

1. **FungalSoilTrade gates on the donor biome, so it never fires on the Rot.** Both
   `src/RimUtinni/FungalSoilTrade/Source/GenStep_ScatterFungalGround.cs` (line ~20) and
   `src/RimUtinni/FungalSoilTrade/Source/MapComponent_RotFungalDistress.cs` (line ~100) declare
   `RotBiomeDefName = "AB_MycoticJungle"`. Change the gate to a **set** that holds `RM_TheRot` (and
   `RUT_TheRot`, the frozen twin, so a save on the twin keeps working), one shared constant, not two. Update
   the comments in `Defs/MapGeneration/RUT_FungalSoilScatter.xml`, `Patches/RUT_FungalSoilScatter_MapGenPatch.xml`
   and `About/About.xml` so they state the new gate (delete the old statements, do not annotate them). Drop
   `sarg.alphabiomes` from `About.xml`'s dependency list if nothing else in the mod needs it (measure). The
   distress response's named species (`AA_MycoidColossus` and the rest, About.xml line ~18) stay as they
   are; the giant's name changes nothing here.
2. **The pale tree's Force line.** `src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_PaleTree.xml` line ~53
   says *"a faint, tugging sense of the Force"*; the comment above it says *"Wildsteam's Force door"*. Free
   text: rewrite that clause franchise-free (a faint pull toward something living that is larger than you),
   keep the rest; fix the comment. Campaign: a new patch in `src/RimUtinni/UtinniPatches/Patches/`
   (`RUT_PaleTree_ForceText.xml`, `PatchOperationReplace` on `Defs/ThingDef[defName="RM_PaleTree"]/description`)
   restores the Force wording for the campaign.

Depends on: none. `FUNGAL_SOIL_TRADE_FIRST_SCRIPT_1` must be written against this item's state.

## criteria

Deterministic reads, recorded in `FUNGAL_SOIL_TRADE_FIRST_SCRIPT_1`'s and `THE_ROT_FIRST_SCRIPT_1`'s
`validation.py`:
- Offline: no `.cs` or `.xml` under `src/RimUtinni/FungalSoilTrade/` contains `AB_MycoticJungle` (a
  sanity probe on the same walk finds `RM_TheRot` ≥ 1 time).
- On a generated `RM_TheRot` test map with FungalSoilTrade loaded: the count of fungal-knot things placed by
  `GenStep_ScatterFungalGround` is > 0; on a non-Rot map it is 0. Digging a knot raises the distress
  component's state from idle (read before/after).
- Free tier only (no `UtinniPatches`): `RM_PaleTree`'s loaded description contains no `Force`. Campaign
  loaded: it contains `Force`.
</content>
</invoke>
