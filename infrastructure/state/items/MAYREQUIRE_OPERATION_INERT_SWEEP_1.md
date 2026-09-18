# MAYREQUIRE_OPERATION_INERT_SWEEP_1 — audit and fix the inert-MayRequire-on-Operation pattern repo-wide

Filed 2026-09-18 (BENCH), descended from the 23:31Z full-list load death:
`MayRequire` on a patch `<Operation>` is INERT (`ModContentPack.LoadPatches`
never reads it; `PatchOperation` has no such field). Two lethal cases
(`RUT_TibannaTap_BeldonWiring.xml`, `RUT_VaporDrifter_AerofleetWiring.xml`)
were already fixed at `01eca070e` before this item was worked further;
~18 more files matched `Operation.*MayRequire` in `src` and needed auditing.

## 2026-09-18 (FOUNDRY, offline/BELT) — swept, 10 more fixed, closing

Grepped every `<Operation ... MayRequire=...>` in `src/**/Patches/**/*.xml`
(minus the two already-fixed files, whose only remaining `MayRequire` hits
are in corrected prose) and classified each by the same test
`PATCH_MAYREQUIRE_OPERATION_SWEEP_1` used: does the xpath fail safely
without the gated mod, or does the operation actually misbehave (a
type-resolution crash, or a dangling reference injected unconditionally)?

**Fixed (10 files, real `PatchOperationFindMod` gate on the mod's display
name, verified via RimSage against `PatchOperationFindMod`/
`ModLister.HasActiveModWithName` — exact-name OR match):**

- `RUT_BeastBulge_DreadRegistration.xml`, `RSW_ProtovermesEgg_ProximityHatch.xml`
  — genuine whole-file killers: an unguarded `<li Class="...">` comp
  injection from a mod that may be absent (same class of bug as the two
  fixed at `01eca070e`).
- `WreckVerminNest_ShipChunk.xml` — same Class= injection pattern, gated on
  TWO mods via comma-`MayRequire`; fixed with nested `PatchOperationFindMod`
  since its own `<mods>` list is OR-only, not AND.
- `RUT_ForgePulse_BiomeWiring.xml`, `RUT_SumpDuskLock_BiomeWiring.xml`,
  `RUT_VentForge_RecipeWiring.xml`, `RUT_VentKiln_RecipeWiring.xml`
  (`PatchOperationAdd`) and `RUT_ScaldSteamLock_BiomeWiring.xml`,
  `RUT_RoilLock_BiomeWiring.xml`, `RUT_GreentideWetBulbLock_BiomeWiring.xml`
  (`PatchOperationConditional`) — no Class= risk, but the xpath targets our
  own always-loaded biome/recipe defs rather than anything gated on
  `mandrake.rm.environmentalhazards`, so the "MayRequire makes this a true
  no-op" comment in every one of these files was false: the patch always
  ran and always injected a dangling `RUT_*` defName reference whenever
  that mod was inactive — true of every load so far per
  `ENVHAZARDS_NEVER_ACTIVATED_1`.

**Audited and left alone (confirmed harmless, bucket (b) from the sibling
sweep — xpath already fails safely without the gated mod, no Class=
injection risk):** the ~100 `PatchOperationConditional MayRequire=`
occurrences in `BiomeCast_Ashkarr.xml` (donor-animal xpaths that only match
when the donor mod is active), the 4 in `FishTypesStrip_NoFishBiomes.xml`
(test the Odyssey-only `fishTypes` field, itself absent without Odyssey),
and the Sequence-wrapped `ThirdPartySignConfigErrors_Fix.xml` /
`ThirdPartyStunBodySize_Squared.xml` (inner `<li Class="PatchOperation...">`
items are core RimWorld classes, not third-party types, and the outer xpath
already depends on the gated mod's own defs existing).

Verified with `skills/rimworld-modding/scripts/validate_patch.py` against
the live minimal-list install (`--defs` on Mods + Data + Workshop content
dirs) — 0 errors across all 10 fixed files, including the nested-FindMod
file reaching its real Odyssey-gated target through both wrapping levels.

## spec
Grep every `<Operation ... MayRequire=...>` in `src/**/Patches/**/*.xml`,
classify each as engine-honored, inert-but-harmless, or inert-and-relied-
upon, and fix the third bucket with a real gate (`PatchOperationFindMod`,
nested where more than one mod is required).

## verify
Every occurrence found this pass is accounted for as fixed or confirmed
harmless; none left in the "relied upon but broken" bucket.

## criteria
No patch file in this repo silently misbehaves (patches something that
doesn't exist, injects a dangling reference, or crashes on a missing type)
due to the `MayRequire`-on-`<Operation>` anti-pattern. Met this pass for
every occurrence found — closing.
