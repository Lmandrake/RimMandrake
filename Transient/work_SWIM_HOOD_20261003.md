# JAWA_SWIM_HOOD_KEEP_1 work log 2026-10-03 (FOUNDRY)

## Mechanism (RimSage, decompiled 1.6)
- `PawnRenderer.ParallelGetPreRenderResults`: if `pawn.Swimming`, flags &= 0xFFFFFF1F (clears Headgear 0x20, Clothes 0x40, NeverAimWeapon 0x80) and |= NoBody.
- `PawnRenderNodeWorker_Apparel_Head.CanDrawNow` (worker given to every Overhead apparel node by `DynamicPawnRenderNodeSetup_Apparel.ProcessApparel`) returns false without Clothes+Headgear, so the worn hood (guy762_JawaHood, Overhead, layer 71/90) is dropped.
- The head is NOT culled: `PawnRenderNodeWorker_Head.OffsetFor` only lowers it z-0.5 when `parms.swimming`. The 2026-09-26 note's "Head culls in swim" hypothesis is FALSE.
- `PawnRenderNodeWorker_Body.CanDrawNow` returns false on NoBody (body hidden, head kept).

## Why the 2026-09-26 live test looked hoodless (inference from Transient/jawa_swim_synced_20260926.png)
The gene fallback node did draw: Mila's 0.75-size pointed silhouette matches hood_south.png. That texture is a greyscale stuff mask (avg RGB ~183) and the fallback node has no colour (colorType default -> white), so it renders pale and reads as a "pale-blue blob" under water lighting. NOT changed (cosmetic; owner decides a tint).

## Fix (JawaRules)
- `Source/Patch_JawaHoodSwimming.cs` (new): `RSW_KeepHoodWhileSwimming` DefModExtension; `JawaHoodRender` helpers; Harmony postfix on `PawnRenderNodeWorker_Apparel_Head.CanDrawNow`: only when vanilla said no, swimming, not portrait, toggle on, apparel def has the extension, re-asks the same worker with Clothes|Headgear restored ([ThreadStatic] re-entry guard; render is parallel). All other vanilla gates still apply.
- `Patches/RSW_JawaHood.xml`: Conditional AddModExtension on guy762_JawaHood.
- `Source/PawnRenderNodeWorker_JawaHoodFallback.cs`: real-hood test now uses vanilla `HeadgearVisible` on the effective parms. Also fixes a latent bug: in a no-body bed the old raw-flag check suppressed the fallback while vanilla hid the real hood (bare-headed sleeper).
- `Source/RSW_JawaRulesSettings.cs`: `swimHoodEnabled` (default ON), Scribe'd, checkbox.
- `Source/JawaRules.cs`: armed via Apply() as rule "swim-hood" (named arm line).
- `Source/JawaRules.csproj`: Compile Include added.
- `validation.py`: arm line, toggle, flip, chain `swim_hood_kept` (offline wiring check + UNMEASURED live component).

## Build / validation
- winbuild JawaRules: 0 warnings, 0 errors; DLL + .srchash refreshed.
- validate_patch.py: 0 errors (1 intentional add-if-missing warning). Offline needles all present.

## Remaining (live, not done: no bridge/deploy this pass)
- Deploy JawaRules at game-down. Live STATE read: hooded Jawa on GoSwimming, read hood node `Worker.CanDrawNow` on this frame's parms -> true; toggle off -> false while the gene fallback node -> true. No bridge tool exposes that yet.
- Hair is not skip-flagged while swimming (`PawnRenderTree.AdjustParms` gates renderSkipFlags on HeadgearVisible); hood layer 71 > hair 62 covers it, edge poke-out UNMEASURED.
- Fallback hood is untinted white: owner call.
