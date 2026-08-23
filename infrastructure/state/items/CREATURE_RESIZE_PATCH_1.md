## spec

🔴 **APPROVED FOR v1 BY THE OWNER, 2026-08-23:** *"nice job on the animals. I approve for v1.
We'll have to meet them and see how it feels during live play."*

**The list is `design/Jawa/fauna/CREATURE_RESIZE_LIST.md`** — 25 changes out of 621 cast
creatures, each naming the field and the magnitude. Its source of truth is
`design/Jawa/fauna/creature_size_decisions.json` (`savedBy: creature_size_review.html`).

⚠️ **Approved as generated, not row by row** — 0 of 621 rows overridden. That is a real
decision and the list says so. It also means **the eye has not been on every row**, so a
change that looks wrong in game is a correction, not a contradiction.

## the two fields, and they must not be merged

| field | lives at | moves |
|---|---|---|
| `drawSize` | `ThingDef.graphicData.drawSize` | **the picture and nothing else** |
| `bodySize` | `ThingDef.race.baseBodySize` | meat, leather, hunting yield, carrying capacity, food need, melee damage scaling |

- **23 shrinks are `drawSize` ONLY.** ⛔ Do not touch `bodySize` on any of them. Shrinking to
  hide weak art is a rendering decision; taking meat off a creature because its sprite is
  small is a balance change nobody asked for.
- **2 enlarges are BOTH**, because a headliner that is only *drawn* big is a cardboard cutout.

## the magnitudes are derived, not taste

`drawSize` multiplier = `sqrt(px / band median px)`, clamped **0.55 – 0.95**, where `px` is
the sprite's real area from `design/Jawa/fauna/sprite_features.csv`. A creature drawn at a
quarter of its band's pixel budget gets drawn at half. The table carries the number per
creature; do not re-derive it.

The two promotions both target `bodySize` **8.2**, the median of the 24 creatures already
cast SUPER.

## 🔴 the two enlarges are the risky half

`Zakkeg` 5 → 8.2 and `BMT_Thrumbungus` 4 → 8.2 roughly **double** meat, melee scaling and
food need. Both went in because `AB_MiasmicMangrove` and `IceSheet` had **no super-huge at
all** and the alternative was a headliner-less biome. ⭐ These are exactly what *"see how it
feels during live play"* is for — watch them before anything else.

## verify

    python3 skills/rimworld-modding/scripts/validate_patch.py <the new patch> --defs ... --live ...

**PASS =** every one of the 25 defNames resolves and every operation matches. 🔴 **A patch
that matches nothing logs nothing** — `PatchOperationConditional` and `PatchOperationFindMod`
both return true on no match, so a silent no-op reads as success. Count the operations that
applied; do not read the absence of a red error as a pass.

⚠️ **`drawSize` may be ABSENT on a def**, in which case it must be Added rather than
Replaced. Vanilla animals mostly do not declare it. Use the conditional add/replace pattern
already used throughout `WeaponTags_Renormalise.xml`.

## criteria

- [ ] All 25 creatures patched, each with the field and magnitude the list names.
- [ ] ⛔ Zero `bodySize` edits among the 23 shrinks.
- [ ] `Zakkeg` and `BMT_Thrumbungus` carry both fields.
- [ ] Validator run with BOTH `--defs` and `--live`; operation count checked, not just errors.
- [ ] Deployed — writing the file is not deploying it.

## watch out

- ⚠️ **These are OTHER MODS' defs** — Jurassic Rimworld, Star Wars Animal Collection,
  Biomes! Caverns, Alpha Animals, Megafauna. Patch them; never edit a mod folder in place.
- ⚠️ **The cast was built against 26 biomes before 2026-08-23.** `AB_RockyCrags` has since
  lost its 339 tiles above 0 °C to `HorrorWastes`, so the RockyCrags cast describes ground
  that no longer exists in it. Sizes are unaffected; the cast is a separate job.
- 🔑 `design/Jawa/fauna/creature_size_decisions.json` is the owner's file. ⛔ Nothing may
  write it but the sheet. `gen_creature_size_sheet.py` reads it and never writes it, which is
  why no freeze marker was added — there is no generator that could overwrite it.
