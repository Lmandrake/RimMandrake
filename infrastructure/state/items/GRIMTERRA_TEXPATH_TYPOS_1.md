## spec
`GRiNDTerra Biomes` (`GRimTerra.Biomesmod`, workshop `3537211820`) ships three
`texPath`s pointing at folders that do not exist. **The art is all present** —
only the paths are wrong, and every one of them is in the SECOND `<li>` of
`<lifeStages>`, i.e. the JUVENILE stage. Baby and adult stages are correct.
  `1.6/Defs/ThingDefs_Races/Races_Animal.xml:301`
     is   Things/Pawn/Animal/TortoiseGRim/GRimTortoiseA
     want Things/Pawn/Animal/GRimTortoise/GRimTortoiseA        (words transposed)
  `1.6/Defs/ThingDefs_Races/Races_Animal.xml:305`
     is   Things/Pawn/Animal/Tortoise/Dessicated_GRimTortoiseA
     want Things/Pawn/Animal/GRimTortoise/Dessicated_GRimTortoiseA
     ⚠️ points at VANILLA's Tortoise folder. Logs nothing until a dessicated
     corpse exists, so it is invisible in the load harvest.
  `1.6/Defs/ThingDefs_Races/Races_Animal_Birds.xml:64`
     is   Things/Pawn/Animal/GRimPinkBird/GRimPinkbird
     want Things/Pawn/Animal/GRimPinkbird/GRimPinkbird          (capital B)
🔑 The capital-B one is the instructive case: **Windows' filesystem is
case-insensitive but RimWorld's content index is NOT**, so the file resolves
perfectly from a shell and still fails in game. Never settle a texPath question
with `ls`.
FIX: a `PatchOperationReplace` in `Jawa_Patches` on those three `texPath` nodes.
⛔ Do NOT edit the workshop folder — Steam overwrites it on the next update.

## verify
`validate_patch.py --defs` 0 errors; the xpath reports 3 hits, not 0. A patch
that matches nothing logs nothing.

## criteria
a load whose `Player.log` carries **0** `Failed to find any textures at
          Things/Pawn/Animal/TortoiseGRim` or `.../GRimPinkBird` lines. Baseline today is 2.
          ⚠️ ABSENCE IS A WEAK SIGNAL and this is one of the cases where it is the only one
          available. Strengthen it by spawning a JUVENILE tortoise and looking — adults
          render fine and prove nothing. `jawa/set_pawn_age` cannot help: DebugSetAge is
          FORWARD-ONLY and refuses to walk a debug-spawned adult back to a juvenile.
🔴        **THE TWO BROKEN PATHS ARE CONFIRMED LIVE, in the 2026-08-20 session log
          (17:54, archived), and they are EXACTLY the strings this patch targets:**
            `Failed to find any textures at Things/Pawn/Animal/TortoiseGRim/GRimTortoiseA`
            `Failed to find any textures at Things/Pawn/Animal/GRimPinkBird/GRimPinkbird`
          ⇒ That is `harvest_log.py`'s `texture path failures` row, RED at **2** against a
          baseline of 0. ⭐ **This substantially answers the "I could not produce the hit
          count" caveat below** — the offline validator could not confirm the xpaths match,
          but the ENGINE confirms the broken values are present and identical to the ones
          the ops name. The load was at 07:59, before the fix deployed.
          ⏳ **Next load that row must read 0.** It is the cheapest check in this item and
          it is now a straight before/after against a measured 2.

## notes
**from:** CHECK, 2026-08-20. Found in the load harvest after the owner's terrain/worldmap
mod swap; diagnosed to the exact line.

**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

done 2026-08-20 (offline half). One new file,
`src/Jawa/Jawa_Patches/Patches/GrimTerraTexPaths_Fix.xml`, deployed and in sync.
verify output: `validate_patch.py --defs` -> `OK - 0 errors, 3 warning(s)`, all
three of the "this node is probably CREATED by another mod's patch at runtime,
make sure your mod loads AFTER it" class.
⚠️ **THE ITEM'S VERIFY ASKED FOR "3 hits, not 0" AND I CANNOT GIVE YOU THAT
NUMBER. Read this before treating it as passed.** The offline validator reports
**0 on-disk nodes** for all three. I could not settle whether that is the
validator failing to index that mod's defs or the nodes genuinely being
runtime-created, and I am not going to claim a diagnosis I do not have.
**What I ruled out, so nobody repeats it:** the mod IS active (its packageId is
stored lower-case as `grimterra.biomesmod`, so a case-sensitive check says
"inactive" and lies); its `LoadFolders.xml` resolves correctly — I called the
validator's own `resolve_load_folders` and it returns `<mod>/1.6`; and
`<mod>/1.6/Defs/ThingDefs_Races/` exists and parses. A hand-built probe file was
NOT usable as evidence either way: it reported 0 for `AncientSoldier`, a **Core**
def that certainly exists, so the probe method is wrong rather than the mods.
✅ **What IS verified, directly against the authoritative source — the mod's own
XML on disk, parsed, not grepped:** each of the three xpaths selects **exactly
one node**, and the target folders exist with the exact casing the fix writes.
🪤 **THEY ARE ON `PawnKindDef`, NOT `ThingDef`.** The item did not say which, and
the animal's ThingDef carries a `race/lifeStages` node of the same shape. An
xpath aimed at ThingDef matches nothing — and a PatchOperation that matches
nothing logs nothing, so it would have looked exactly like a fix.
🪤 **And the obvious xpath form is the wrong one here.** `texPath[.="..."]` is
valid XPath 1.0 and RimWorld would take it, but the validator walks the defs with
ElementTree, which has no self-predicate and silently reports 0. The shipped form
puts the predicate on the PARENT — `bodyGraphicData[texPath="..."]/texPath` —
which is the house form both engines agree on, the same shape as
`li[kindDef="Combat"]`. Value-predicated rather than `li[2]`, so it cannot drift
if anything ever inserts a life stage.
⏳ **The live half is owed and is CHECK's**, and the item is right that absence is
a weak signal: spawn a JUVENILE tortoise and look. Adults render fine and prove
nothing. Filed as `GRIMTERRA_JUVENILES_RENDER_1` in `queue/CHECK.md`.
