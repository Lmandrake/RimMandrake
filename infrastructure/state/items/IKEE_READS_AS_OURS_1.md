## spec
Rename and placement only — the sprite and every stat are untouched, deliberately.
Both the `ThingDef` and the `PawnKindDef` named `AA_Eyeling` were relabelled,
because the mod ships both with `label: eyeling`.

## verify
off the next def dump: `AA_Eyeling` label reads **`ikee`** on BOTH defs, and its
description contains **no** "extradimensional corruption" and no "grotesquely".
Then: `AA_Eyeling` appears in the `wildAnimals` of exactly **three** biomes —
`Wasteland`, `ExtremeDesert`, `ZBiome_DesertOasis` — and no others.

## criteria
a player can find one in the waste, and it reads as belonging to this campaign
rather than to Alpha Animals.
🔴 **NOT ON THE NIGHTSIDE.** Its shipped `ComfyTemperatureRange` is 0-60 °C, so it
freezes there. If one turns up on a nightside tile, something else is placing it
and that is worth knowing.
⏳ The bonded starting ikee is NOT part of this — it rides with `B55`.

## notes
**from:** BUILD, 2026-08-20. `Ikee_Rename.xml` written, validated, deployed.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready
