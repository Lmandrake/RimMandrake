# History of the content-moderation skill

This file holds evidence and corrected text. The lessons are in `../SKILL.md`. Do not read a count here as a count of
today.

## Dates and counts

- The skill was first written for a 500+ mod stack. On 2026-11-23, `ModsConfig.xml` listed 315 active mods.
- The `About.xml` lesson (Utility Columns): 2026-09-13.
- The donor-of-donor lesson (4 cross-reference errors): 2026-09-08.
- The `RSW_` port-rename lesson: 2026-09-21. The remaining-rows lesson of a fauna roster: 2026-09-22.
- Biome-cast measurements (399 failures): the bench tier, 2026-09-02.
- `BIOME_CAST_REFS_BREAK_MAPGEN_1` (2026-09-02): found by the retired seat FOUNDRY.
- The `FactionDef` lesson: 2026-09-11. The skill said that the cuts were "silently NO-OPS", in `Mod_CherryPicker.xml`,
  "verified live via a fresh DefDump capture".
- `weaponTags` in the dump: **696 ThingDefs and 414 PawnKindDefs** when the skill was written; 388 and 296 in the
  2026-11-23 capture (314 mods).
- The ikwa cut: the only other carrier of `NeolithicMeleeDecent` belonged to an inactive mod. On 2026-11-23, eleven
  ThingDefs carry the tag.
- The vanilla animals are about 40% of the animals. The old text said that vanilla art cannot be rendered offline.
  `extract_bundle_textures.py` now extracts it.
- The old text said that the vanilla animals are "the vanilla ones you already know by sight".

## Where the dump sits against Cherry Picker: three explanations, two of them wrong

1. **First text, wrong.** Nobody measured it. Its author reasoned from how Cherry Picker works and assumed the capture
   order:

   > *"Cherry Picker removes defs at load, so the def dump is the post-removal state. A cut that worked is ABSENT from
   > the dump."*

   The text concluded:
   - **does not resolve** → the cut is already in effect. Correct, not broken.
   - **resolves** → it has NOT taken effect yet. Either it was added since the game started, or it is not working.

   A correction then quoted it as *"a cut that worked is ABSENT from the dump."*
2. **Second text, CORRECTED 2026-08-23, mechanism wrong.** It said that the dump is captured BEFORE Cherry Picker removes
   anything. Its measurements were right, against the running game:
   - the kill list held **1,289 `ThingDef` entries**. **1,162 of them were STILL PRESENT in `defs.sqlite`** — 90%;
   - `Player.log` reported **1,209 defs removed**, including `ThingDef/Cat`, `ThingDef/BlackBear` and every
     other spot-checked entry;
   - the owner reviewed an animal art sheet on 2026-08-23 and asked why animals he had already removed were still there.
     The old text said that they were not still there: the sheet showed 1,162 defs that no longer exist in his game.
3. **Measured 2026-11-23, the current text.** In one `Player.log`, the Cherry Picker block is at line 1279 and the dump
   starts at line 2817. So Cherry Picker runs first. Of the defs that this log reports removed, the capture
   `2026-11-23T19-47-11Z` still holds 397 of 397 `ThingDef`, 19 of 19 `PawnKindDef`, 11 of 11 `BiomeDef`, 9 of 9
   `IncidentDef`, 3 of 3 `HediffDef` and 2 of 2 `AbilityDef`. It holds 0 of 109 `ResearchProjectDef`, 0 of 13
   `XenotypeDef`, 0 of 9 `GeneDef` and 0 of 2 `RecipeDef`. `RemoveDef` in the 1.6 `CherryPicker.dll` (decompiled with
   `ilspycmd`) gives the reason: it calls `DefDatabase<T>.Remove` for 13 types, and it changes fields for the others.

## Biome refs of a cut animal

The skill said that a Cherry Picker cut of an animal leaves a `wildAnimals` entry that throws on the next mapgen. That is
true only when the def leaves the load. In the 2026-11-23 capture, 178 `wildAnimals` entries name cut animals. All have
commonality 0, and the dump log line says `biomes=61 (0 threw and produced no rows)`.

The skill also said that `BiomeDef.ConfigErrors()` throws on one unresolved animal or plant record and breaks map
generation. The 1.6 source reads the animal lists only, in dev mode, and dereferences a null only for a duplicate record.
