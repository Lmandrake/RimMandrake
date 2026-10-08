# JawaRules validation (Approach B), 2026-10-07 - DONE, nothing committed

JAWA_SWIM_HOOD_KEEP_1 (hood keep on swim, apparel render flags) is the centre of this pass.

## Kernel (Verse-free, Harmony-free, called by the mod with the same expressions)
`src/RimStarWars/JawaRules/Source/Kernel/RSW_JawaRulesKernel.cs` (1 Compile line in `JawaRules.csproj`)
- `RSW_HoodKernel`: render flags as plain ints (`Headgear` 0x20, `Clothes` 0x40, the bits the source comment cites from the decompiled engine), `SwimForceApplies`, `EffectiveFlags`, `Postfix` (the CanDrawNow postfix: only when vanilla said no, not inside its own re-ask, rule applies, node is a kept hood; re-asks the SAME worker with the flags restored), `RealHoodIsDrawing` (lazy: def resolved, headgear visible under the effective flags, apparel tracker, hood worn), `FallbackDraws` (fails OPEN). Call sites `Patch_JawaHoodSwimming.cs` (the engine still owns the `[ThreadStatic]` re-entry flag and the `PawnDrawParms` copy), `PawnRenderNodeWorker_JawaHoodFallback.cs`.
- `RSW_RulesKernel`: `IsJawa`, `SowResult`, `NeedsRelationsTracker`, `NeedsPetName`, `ForceKind`, `ForceXenotype`, `Current` (world-label alpha / lift). Call sites `JawaRules.cs`, `RSW_JawaRulesSettings.cs`.
- Not extracted: the two IL transpilers (their own hit-count guards stay), the null-race guard, Harmony registration, the settings window.

## Defects
- None in the kernel: no fuzz case failed on the extracted production code and nothing read while extracting was wrong.
- MEASURED GAP, unchanged (cannot be closed offline): `RealHoodIsDrawing` decides "the real hood will draw" from headgear VISIBILITY, worn and tracker only. The real hood's own worker has further gates (rot draw mode, skip flags) that the fallback node cannot see. When one of them refuses a worn, visible hood, the fallback hides AND the hood does not draw, so the head is bare. The fuzz models that as "the real hood's other gates" and counts it (235,981 of 3.1M fallback decisions at scale 20); with those gates passing, real hood XOR fallback holds on every one of 7.9M steps. Whether any shipped state hits it (the apparel node's default `rotDrawMode` against a desiccated Jawa) needs the engine, not this tool.
- UNMEASURED offline: the flag bit values and the ten Harmony targets (printed by the lint as a game-update checklist).

## Fuzz
`python3 src/RimMandrake/Utils/selftest_jawarules_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only hood|rules]`; project `Source/SelfTest/RimStarWarsJawaRules.SelfTest.csproj` (net8.0, the one kernel). Default seeds 5000 / 5000 (10k cases, 0.8M steps, 1.1 s). `--fuzz-scale 20`: 200,000 cases, 15.9M steps, 21 s, 0 failures; swim re-asks 1.41M (hood kept 804k), fallback draws 3.10M, fail-open checks 4.77M, pets named 134k, pawns re-kinded 402k, Jawa sowing refused 448k (blind guards).
- hood: draw / settings / wardrobe / bed-and-map sequences against a fake render engine (swim masks Headgear, Clothes and NeverAimWeapon BEFORE the worker is asked; headgear visibility = both flags, no hiding bed, hats-only-on-map; an "other gates" bit): a non-kept apparel is never changed, the worker is asked at most once and never inside its own re-ask, never after vanilla said yes (also checked at kernel level), re-asked with exactly the restored flags; a swimming Jawa keeps a worn kept hood whenever every other gate lets it; nothing changes outside swimming, with the setting off or on a portrait; fallback = base gates AND NOT real hood drawing; a throwing guard fails open; fallback shows whenever there is no real hood to stand in for.
- rules: sow / tame / redress / settings sequences: only a Jawa loses sowing (xenotype read only when it can matter), a chosen name is never replaced and a named pet never needs a name again, wild and faction-less animals are never named, a corrected pawn is not corrected twice, `IsJawa` exact and case-sensitive.

## Mutation (48 planted, 48 caught, kernel restored byte-identical)
`python3 src/RimMandrake/Utils/mutate_jawarules_fuzz.py [substring]`: swim-rule gates, flag bits and flag combination, every postfix gate, re-ask with old flags / without asking / ignoring the answer, real-hood visibility / worn / tracker / def, fallback base gates / inversion / fail-closed / throwing guard, Jawa matching, sow ban, tracker, pet-name and redress gates, world-label value. Three first-run misses: two closed with kernel-level checks (a vanilla yes is never re-asked; a faction-less animal is never named; both are unreachable through consistent engine inputs, so only a direct kernel call can see them), one equivalent mutant replaced (swapping the two flag bits changes nothing because they are always OR'd; now `wrong clothes bit`). A harness slip found at scale 20 (two player-chosen pet names could collide) was fixed in the harness, not the kernel.

## Lint
`python3 src/RimMandrake/Utils/lint_jawarules_defs.py [--quiet] [--src-root D] [--plant-check]`: `jr-hood` (patch classes resolve, the gene and hood defs exist, fallback baseLayer 65 under headgear 71, fallback texture exists on disk), `jr-flags`, `jr-xenotype`, `jr-labels` (0.3 / 0.6 and 0.4 / 1.5 against the slider defaults, four lift hits), `jr-settings`, `jr-guard`, `jr-patches` (the Harmony target checklist), `jr-kernel`. 0 ERROR, 0 WARN. `--plant-check`: 13 planted defects all caught.

## Build
`winbuild.py src/RimStarWars/JawaRules/Source/JawaRules.csproj` -> 0 warnings 0 errors; `Assemblies/JawaRules.dll` + `.srchash` rebuilt, UNCOMMITTED.

## Regressions
`run_selftests.py` final sweep after all four mods: 282/282 passed; `selftest_jawarules_fuzz.py` auto-discovered and green; no existing selftest pinned source text that moved.
