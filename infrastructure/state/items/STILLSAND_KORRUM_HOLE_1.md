# STILLSAND_KORRUM_HOLE_1 — the deep desert lost its only giant

## why this exists at all

`BIOME_SPECIFIC_FAUNA_LAW_1` gave each animal one home, so `RSW_Korrum` (the boulder-shelled
giant crab, bodySize 4.00) moved to the Scarlands — *"excellent for scarlands"*, owner
2026-09-22 — and its `RUT_ExtremeDesert` wiring at **0.025 was removed**. That was a real,
wired row, not a withdrawn admission, so the deep desert is genuinely one animal thinner.

This is filed because the deep desert is one of the five biomes he named for filling:

> *"We will fill rosters as per-biome work continues. Only fill the mostly finished biomes as
> needed: deep desert, desert, rot, pyrelands, lantern deeps. Others we will work
> individually."*

⛔ The other two roster holes opened the same day (Arid Shrubland, Wasteland) are **not**
filed, deliberately — both were unwired admissions, nothing changed in game, and neither
biome is in that list of five.

## what the roster looks like now — MEASURED 2026-09-22

`RUT_ExtremeDesert`: **14 wired species**, total commonality ~2.76 after the removal, and it
passes the food-pyramid law comfortably (77.0% small as of `ECOSYSTEM_PYRAMID_LAW_1`'s
2026-09-20 sweep — removing a *large* animal moved that the right way).

⇒ 🔑 **The hole is a CHARACTER hole, not a ratio hole.** The pyramid is fine; what the dune
sea lost is its one big silhouette. Do not fill this with more small fauna to satisfy a
number — nothing is failing.

## spec

1. **Check for existing cast first** — the standing rule, and `BIOME_SPECIFIC_FAUNA_LAW_1`'s
   own second half says a hole is filled with a **new** creature rather than a borrowed one.
   But "new to this biome" may already exist unplaced: search the homeless/unplaced creatures
   and the Star Wars canon library (`design/RimStarWars/canon_references/`, 45 creatures)
   before designing anything. A canon desert giant would be far better than an invention.
2. If nothing fits, design one: a large dune-sea animal that is **not** another armoured
   plodder — the korrum's niche (placid, ignores everything, armour as its whole defence) is
   now the Scarlands', and repeating it here would make the two deserts read the same.
   `dune_sea.md` / `deep_desert.md` (merged roster, R22) is the sheet to write against.
3. Wire it at a giant's commonality (the korrum sat at 0.025 here; `KraytDragon` 0.15 and
   `GreaterKraytDragon` 0.001 are the existing scale references in that roster), and check
   the pyramid after.

## verify

The deep desert has at least one large animal again, it is not a re-skin of the korrum, and
`RUT_ExtremeDesert` still passes `ECOSYSTEM_PYRAMID_LAW_1`.

## criteria

Standing in the dune sea and standing in the Scarlands do not show you the same big animal.

## Watch out

- ⛔ **Do not re-add `RSW_Korrum` here.** `RUT_ExtremeDesert`'s `wildAnimals` block carries a
  comment saying so; the owner corrected exactly this ("I meant pick one arid home") and a
  shared habitat class is not an in-game reason to multi-home.
- ⚠️ `RUT_ExtremeDesert` is becoming `RM_Stillsand` (`STILLSAND_RM_MOD_BUILD_1`, open). If that
  build lands first, this creature belongs in the new mod, not in `UtinniPatches` — unless it
  is Star Wars cast, which rides a Utinni-layer patch.
