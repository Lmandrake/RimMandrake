# LIGHTSABER_RECIPE_GATE_1 — cutting the saber research does not stop saber crafting

The owner ruled lightsaber construction out of the scenario. Cutting the research
rows does not deliver that ruling: a different mod crafts sabers off a vanilla
research row. This closes the hole.

## spec

Owner, 2026-09-03: *"they won't be teaching how to make lightsabers. Nobody will.
That's not tech in this scenario."* v4 accordingly cuts `guy762_ResearchKotOR_lightsabers`,
`_advsabers`, `_saberparts` and `_jedi`.

🔴 **MEASURED by BENCH, and it defeats the ruling as it stands.** The lightsaber
mod (`lee.theforce.lightsaber`, workshop `3466124712`) ships its own crafting
recipes that do not reference any KotOR research row:

- `LightsaberRecipe.xml` declares one **abstract** `RecipeDef Name="Lightsaber_Crafting"`
  carrying `<researchPrerequisite>MicroelectronicsBasics</researchPrerequisite>`
  and `recipeUsers` = `ElectricSmithy`, `FueledSmithy`, `TableMachining`.
- **Eight** concrete recipes inherit it by `ParentName="Lightsaber_Crafting"`:
  `Force_CraftLightsaberSingle` · `_Curved` · `_Shoto` · `_Dual` · `_Crossguard`
  · `_Broadsaber` · `_BuildYourOwn` · `_Blaster` (the last two
  `MayRequire="oskarpotocki.vanillafactionsexpanded.core"`).

So after the v4 cuts a Jawa colony still builds any of eight lightsabers at a
**fueled smithy** — no electricity, no KotOR research — as soon as it has
`MicroelectronicsBasics`, which every colony researches. Identical text in the
mod's 1.5 and 1.6 folders.

The v4 pass independently flagged the same shape as `saberleak: 2 surviving
COMMON rows still unlock Force_ recipes -> ['Smithing', 'MicroelectronicsBasics']`.

## verify

In a game with the v4 cuts applied, no player-buildable bench offers any
`Force_CraftLightsaber*` recipe, and `Lightsaber_Crafting`'s children resolve to
no reachable `recipeUsers` — checked against the RESOLVED post-RR dump, whose
fingerprint matches the live mod set, not against raw mod XML.

## criteria

1. **The items are untouched.** Migration rule 5 governs: a lightsaber still
   exists, still drops from a body, still trades. Only *making* one goes away.
2. The fix is an XML patch on the abstract parent (patches resolve before
   inheritance, so patching the parent reaches all eight children — verify that
   assumption rather than assuming it).
3. It survives the mod's own updates — a patch that silently matches nothing
   logs nothing (`PatchOperationConditional` and `PatchOperationFindMod` both
   return true on no match), so the patch must be validated with
   `validate_patch.py` using both `--live` and `--defs`.
4. Check for a SECOND crafting path before closing: the KotOR mod has its own
   saber items and may carry its own recipes; this item verified only
   `lee.theforce.lightsaber`.
