# BRAINWORM_MOD_BUILD_1 — Geonosian brain worms, RSW tier

Built to `design/RimStarWars/brain_worm_spec.md`. Mod lives at
`src/RimStarWars/BrainWorms/` — packageId `mandrake.rsw.brainworms`, namespace
`RimMandrake.StarWars.BrainWorms`, every defName `RSW_`.

## 🔴 The owner's permanent ruling, carried into the code

*"Never corpse-walker. Too gross."* (2026-09-11). Living hosts only, forever.
Three places enforce it and all three carry the ruling in a comment:
`CompRSWWormBurrow.IsValidHost` refuses a dead pawn; `HediffComp_BrainWormPuppeteer`
refuses a dead pawn and a hediff stops ticking when its pawn dies anyway; the worm
race sets `canBecomeShambler false` so Anomaly cannot raise a dead worm either.
A dead-host path is not deferred work here. It is banned work.

## What it is

| piece | where |
|---|---|
| the worm + its kind | `Defs/ThingDefs_Races/Races_BrainWorm.xml` |
| staged infection hediff | `Defs/HediffDefs/HediffDefs_BrainWorm.xml` |
| puppet mental state | `Defs/MentalStateDefs/MentalStateDefs_BrainWorm.xml` |
| puppet think tree | `Defs/ThinkTreeDefs/ThinkTreeDefs_BrainWorm.xml` |
| surgery (risky fast path) | `Defs/RecipeDefs/Recipes_BrainWormSurgery.xml` |
| eggs, egg shell, projectile | `Defs/ThingDefs_Items/Items_BrainWormEggs.xml` |
| C# (11 files, no Harmony) | `Source/` |

Ladder: latent (invisible, ~2.5 days) → influenced (whispers, social/work
debuffs, ~3 days) → puppeted. Cold is the cure and the same number with a sign:
`severityPerDay 0.14` while warm, `-3` at or below 0 °C, and
`Thing.AmbientTemperature` answers on a map cell, in a container AND from the
world tile — so carrying an infected friend into the nightside genuinely works
mid-caravan.

**No Harmony.** The puppet think tree rides vanilla's own
`Humanlike_PostMentalState` `insertTag` hook, which sits after both mental-state
subtrees and before queued jobs, drafted orders, lord duties and all work. There
is no patch to collide with.

## The one design question the spec left open, and its answer

The spec fixed the fantasy of vector 3 (*"bring a catapult and hurl eggs at
their ship, then leave"*) and left the delivery mechanism to the build:
catapult/launcher item vs caravan action.

**Ruled here: a mortar shell.** `RSW_Shell_BrainWormEgg` is a craftable
(Mortars research, machining table) non-explosive shell whose
`projectileWhenLoaded` bursts into 2–4 worms where it lands. Minify a mortar,
caravan it onto the hostile settlement's map, shell them, leave — that IS
"bring a catapult", and it needs no new world-map machinery at all. Reversible
if the owner wants the caravan-action version instead; nothing else depends on
this choice.

## Vectors, all three ruled and all three built

1. **Ruin dungeons** — `Patches/BrainWormEggs_RuinLoot.xml` adds egg clusters to
   `MapGen_AncientComplexRoomLoot_Default` (validated: 2 live matches). With
   `mandrake.rm.proximityhatch` active they hatch when you walk up to them.
2. **Salvaged cargo** — `RSW_BrainWormCargoPod`, an ordinary-looking cargo-pod
   crash with a real salvage haul and a brood in it. PositiveEvent letter on
   purpose; the player is never told.
3. **Weaponized eggs** — the mortar shell above.

## State

- `dotnet build -c Release` — 0 warnings, 0 errors.
- `validate_patch.py` over all 9 def/patch files against the live 568-mod set —
  0 errors. The only WARNs are the two vanilla texPaths (bundle-resident, so
  correct and wrong look identical from outside the game) and the standard
  unconditional-PatchOperationAdd advisory on two Core targets that always exist.
- `run_selftests.py` — 45/47; both failures pre-existing and unrelated
  (`selftest_tool_metadata` skips for want of a bridgetools build in this
  worktree; `selftest_handoff` passes standalone, flakes under the parallel runner).

## Owed

- 🔴 **LIVE PROOF. Nothing here has been in the game.** The load-round questions
  worth writing down before the next cold load: does the worm race load without
  a config error (one `AnimalAdult` life stage at minAge 0, hatched at
  `DevelopmentalStage.Newborn` by vanilla `CompHatcher`); does the
  `Humanlike_PostMentalState` insert actually fire for a puppeted pawn; does the
  extract-brain-worm bill appear on a Jawa's operations tab (the recipe is
  attached by patching every race that declares `ExciseCarcinoma`, not by
  `recipeUsers`).
- **Deploy.** `deploy_custom_mods.py --mod BrainWorms` plans clean (11 files) and
  has NOT been applied; the mod is not in `ModsConfig.xml` either.
- **ART.** Every texPath is a vanilla stand-in — megascarab body for the worm,
  small bird egg for the cluster, HE shell for the shell and its projectile.
  Nothing renders magenta; nothing is drawn.
- **Code review.** Every file is DIRTY by default; none marked clean.
