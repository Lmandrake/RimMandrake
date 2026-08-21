## spec
Three `texPath`s in GRiNDTerra Biomes point at folders that do not exist, all in
the JUVENILE life stage. Baby and adult are correct, which is why this survived.
🔴 **BUILD COULD NOT PRODUCE THE HIT COUNT THE ORIGINAL ITEM ASKED FOR.** The
offline validator reports 0 on-disk nodes for all three, and whether that is the
validator failing to index that mod or the nodes being runtime-created was not
settled. The xpaths ARE verified correct against the mod's own XML, parsed
directly — each selects exactly one node. **So this live check is carrying more
weight than usual: it is the first real evidence the patch lands.**

## verify
`Player.log` after a load: **0** lines matching
`Failed to find any textures at Things/Pawn/Animal/TortoiseGRim` or
`.../GRimPinkBird`. Baseline today is 2.

## criteria
⚠️ **Absence is a weak signal and here it is nearly the only one, so strengthen
it by LOOKING.** Spawn a JUVENILE tortoise and a JUVENILE pinkbird and confirm
they draw. Adults render fine and prove nothing.
🪤 `jawa/set_pawn_age` cannot help you get there: `DebugSetAge` is FORWARD-ONLY
and refuses to walk a debug-spawned adult back to a juvenile. Spawn young, or
age a baby forward.
⚠️ The dessicated-corpse path is the third one and it logs nothing until a
dessicated corpse exists, so it will not appear in a normal harvest at all. Kill
one and leave it, or accept that one as unverified and say so.

## notes
**from:** BUILD, 2026-08-20. `GrimTerraTexPaths_Fix.xml` written, validated, deployed.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready
