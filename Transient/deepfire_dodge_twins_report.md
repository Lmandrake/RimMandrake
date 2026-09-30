# DEEPFIRE_DODGE_PROOF_TWINS_1 — twin-construction fix

## Status
DONE (offline fix + clean build; live proof re-run left for the bridge holder)

## Problem
`src/RimMandrake/bridgetools/prove_deepfire_worn_glow.py` round2clean run: 14/15 pass.
FAIL: "pairs: coated MeleeDodgeChance lower (or both floored at 0) in all 20" — the 20
"twin" pairs spawned by the debug action are not skill-matched, so in 1/20 pairs the
coated pawn's base MeleeDodge was higher than the plain pawn's (independent of the coat).
The -0.08 dodge penalty itself is real and explained in 20/20 pairs; this is a proof
construction flaw, not a mechanism defect.

## Investigation
`HitPairsAtCell` (`src/RimMandrake/LuminousPigment/Source/DeepfireWornGlowDebugActions.cs`)
spawns two independent `PawnGenerator`-random colonists per pair ("coated", "plain") and
compared `MeleeDodgeChance` between them. Body size was already matched (a prior fix,
`DEEPFIRE_LIVE_FAILURES_1`), but Melee skill level/passion and dodge-affecting traits
(Nimble etc.) were not — so the "plain" twin's base dodge could sit above the coated
twin's independent of the coat's -0.08 StatPart penalty
(`RM_StatPart_GlowingTarget.TransformValue`, `DeepfireCombatPatches.cs`).

## Fix
Compare the SAME pawn's `MeleeDodgeChance` coated vs stripped, instead of two twins:
read `dodgeC` while `coated` still wears its 3-coat parka, then
`ParkaOf(coated)?.GetComp<CompDeepfire>()?.RemoveAllCoats()`, clear the per-thing stat
cache (`StatDefOf.MeleeDodgeChance.Worker.ClearCacheForThing(coated)` — `GetStatValue` is
cached per-thing and nothing else dirties it mid-tick), then re-read as `dodgeStripped`.
Every other factor (skill, passion, traits, body size, apparel, health) is now identical
by construction since it is literally the same `Pawn`. The ranged aim/size comparison
(twins, size-normalized) was already correct and is unchanged. JSON row field renamed
`dodgePlain` -> `dodgeStripped` to describe what it now is. Also corrected the stale
step-4 docstring in `prove_deepfire_worn_glow.py` (still said "the twin's").

## Build / verify
`dotnet build src/RimMandrake/LuminousPigment/Source/RM_LuminousPigment.csproj -c Release`
— clean, 0 warnings/errors. DLL + `.srchash` sidecar updated together via
`Directory.Build.targets`. `run_selftests.py` run in foreground: 77/79 passed, 1
unmeasured (`selftest_tool_metadata.py` — no local Windows JawaBench build here, expected),
1 failed (`selftest_deployed_biome_refs.py`, pre-existing/unrelated — RUT_TheRot mushroom
biome-def references, nothing to do with LuminousPigment/Deepfire; confirmed no mention of
either in that selftest).

## Proof result
Offline change only — bridge not touched per task scope. The live proof
(`python.exe src\RimMandrake\bridgetools\prove_deepfire_worn_glow.py`) needs a fresh
Windows quicktest map to re-run and is left for whoever next holds the bridge; this
item's fix is the twin-construction/stat-cache correction plus a clean rebuild.
