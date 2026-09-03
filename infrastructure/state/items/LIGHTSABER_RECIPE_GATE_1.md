# LIGHTSABER_RECIPE_GATE_1 — cutting the saber research does not stop saber crafting

## spec

Owner, 2026-09-03: *"they won't be teaching how to make lightsabers. Nobody will.
That's not tech in this scenario."* v4 accordingly cuts `guy762_ResearchKotOR_lightsabers`,
`_advsabers`, `_saberparts` and `_jedi`.

🔴 **MEASURED by BENCH, and it defeats the ruling as it stands.** The lightsaber
mod (`lee.theforce.lightsaber`, workshop `3466124712`) ships its own crafting
recipes that do not reference any KotOR research row: an abstract
`RecipeDef Name="Lightsaber_Crafting"` and eight concrete recipes inheriting it
by `ParentName`.

## correction (FOUNDRY, 2026-09-03) — the raw donor file is not what's live

BENCH's finding read `LightsaberRecipe.xml` in isolation: `researchPrerequisite=
MicroelectronicsBasics`, `recipeUsers=[ElectricSmithy, FueledSmithy,
TableMachining]`. **That is not what the resolved game actually builds.**
`guy762.KotORWeapons` (absorbed into `mandrake.rsw.armoury`,
`WEAPONS_DONOR_RETIREMENT_1`) shipped its own compatibility patch for this exact
donor
(`Armoury/Patches/Absorbed_AdditionalMods/kotorweapons/TheForceLightsabers/
Absorbed_Kotorweapons_TheForceLightsabers_Patch_KotORLightsaberRecipes.xml`,
`IfModActive="lee.theforce.lightsaber"`, active on the live 589-mod list) that
already overrides the parent's `recipeUsers` to `[FabricationBench,
guy762_KotORWorkbench]` and adds `researchPrerequisite=
guy762_ResearchKotOR_lightsabers` to each of the eight children.

Verified against the RESOLVED dump (per this item's own criteria — not raw mod
XML): `defs/RecipeDef.json`, capture `2026-09-03T07-26-04Z` (589 mods,
fingerprint-matched to the live set). `Force_CraftLightsaberSingle` resolves
with `researchPrerequisite: guy762_ResearchKotOR_lightsabers`, `recipeUsers:
[FabricationBench, guy762_KotORWorkbench]` — not the raw donor's own values at
all.

**This makes the hole worse than filed, not different in kind.**
`guy762_ResearchKotOR_lightsabers` is one of the four rows v4 just cut. Once
that ResearchProjectDef no longer exists, `researchPrerequisite` is a dangling
reference that resolves to **null**, which `RecipeDef` reads as *no
prerequisite at all* — so post-cut, on the live resolved game, these recipes
would need **zero research**, buildable at a `FabricationBench` the moment the
right saber parts exist. Neither of the two research paths (raw donor's
`MicroelectronicsBasics`, or the absorbed compat patch's now-dangling
`guy762_ResearchKotOR_lightsabers`) is what actually gates it once v4 lands —
so the fix targets the one field neither override touches per-child:
`recipeUsers` on the shared abstract parent.

## what shipped

`src/RimStarWars/Armoury/Patches/Armoury_LightsaberCraftingCut.xml` — gated on
`lee.theforce.lightsaber` via `PatchOperationFindMod`, removes
`recipeUsers` from `Defs/RecipeDef[@Name="Lightsaber_Crafting"]`. A recipe
attached to zero benches cannot be queued from any bench, independent of which
research field ends up governing it post-cut — this closes the hole regardless
of the dangling-reference question above, rather than depending on getting
that exactly right. Order relative to the absorbed compat patch's own
`PatchOperationReplace` on the same xpath does not matter (worked through in
the patch file's own header): whichever runs second is the one still standing
when inheritance resolves, and a `Replace` targeting a node this `Remove`
already deleted matches nothing and is a no-op.

Deployed (`deploy_custom_mods.py --mod Armoury --apply`, verified in sync).

## verify

`validate_patch.py` against the live 589-mod set with `--live` on capture
`2026-09-03T07-26-04Z`: **1 match, 0 errors, 0 warnings** — confirms the xpath
hits exactly the one node intended
(`Star Wars : The Force - Lightsaber: LightsaberRecipe.xml`).

Not yet done, needs a live reload with the v4 research cuts actually applied:
confirm no player-buildable bench offers any `Force_CraftLightsaber*` recipe
in the RESOLVED post-cut dump. The dump checked against here (`07-26-04Z`)
predates the v4 pass (made ~21:00 the same day), so it could only verify the
patch's mechanism (the xpath hits, the field is gone), not the final
post-cut-and-repatch resolved state.

## criteria

1. **The items are untouched.** Only `recipeUsers` was removed from the shared
   `RecipeDef` parent — every lightsaber `ThingDef`, its stats, market value
   and lootability are unaffected. Met.
2. The fix is an XML patch on the abstract parent, verified to reach all eight
   children (they inherit `recipeUsers`, none override it). Met.
3. Validated with `validate_patch.py` using `--live` (589-mod dump) — see
   above. `--defs` was also passed (Data + Workshop + Mods roots) alongside
   `--live` in the same run.
4. **Second crafting path**, checked two ways: (a) `guy762.KotORWeapons` and
   `guy762.MM.KotORCore` directly — no other lightsaber `RecipeDef` found;
   (b) scoped grep across all 605 currently-active mod folders (not the full
   ~1300-mod workshop cache) for `Force_CraftLightsaber*`/
   `Force_Lightsaber_Custom` — one incidental hit,
   `guy762.kotordroids`'s `AlienRace_KotORDroidBase.xml` (a `1.5`-only file),
   which only lists `Force_Lightsaber_Custom` in a droid race's allowed-gear
   list — an item reference, not a recipe; droids being permitted to *wield*
   an already-existing lightsaber is unaffected by this fix and consistent
   with criterion 1. A handful of large, name-unrelated mods (furniture,
   wall stuff, face-addon framework, etc.) timed out on the 5s-per-mod cap
   and were not fully swept; judged low-risk given no plausible connection
   to Star Wars/lightsaber content.
