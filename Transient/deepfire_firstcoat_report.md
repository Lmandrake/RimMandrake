# DEEPFIRE_FIRSTCOAT_BONUS_1 — build report

Status: Built, compiled clean, NOT deployed, NOT live-tested. The coordinator runs the proof.

## Task
Build the first-coat bonus for Deepfire luminous pigment (item §10 step 7):
- Scribed `bonusApplied` flag on CompDeepfire
- Art items: one quality bump on first coat (capped Legendary), stacks split before bump
- Everything else: RM_StatPart_Deepfire on Beauty per spec
- Removal-and-reapply cannot farm the bonus
- Quicktest proof script (NOT run): src/RimMandrake/bridgetools/prove_deepfire_firstcoat.py

## Reading
- [x] item file (DEEPFIRE_FIRSTCOAT_BONUS_1.md)
- [x] spec §3.5 (design/RimMandrake/deepfire_luminous_pigment_spec.md) + §10 row 7
- [x] DEEPFIRE_FLOOR_PAINT_1 report + prove_deepfire_floor.py (style reference)
- [x] CompDeepfire.cs, DeepfirePaintUtility.cs, JobDriver_ApplyDeepfire.cs,
      DeepfireFloorDebugActions.cs, CompInjector_Deepfire.cs (what already exists)
- [x] RimSage: CompQuality, CompArt, Thing.SplitOff/ThingWithComps.SplitOff (PostSplitOff
      fan-out), StatPart base, StatPart_Quality_Offset (reference), StatWorker.FinalizeValue
      (confirms stat.parts run in list order — a PatchOperationAdd-appended part runs LAST,
      after vanilla's own StatPart_Quality/StatPart_ContentsBeauty on Beauty),
      GetAdditionalOffsetsAndFactorsExplanation (confirms ExplanationPart gets no running
      `val` — hence the ConditionalWeakTable cache in RM_StatPart_Deepfire), GenPlace.TryPlaceThing,
      ThingComp base (parent field), DiningChair/Bed/SculptureSmall merged defs.

## Finding: the spec's own worked examples disagree on "art item" scope
Spec §3.5 bullet 1 lists "art-bearing furniture" under the CompArt/quality-bump bucket, but
its OWN "everything else" worked example is "a Good-quality steel bed... gets +3 + 1.5" — and
`Bed`/`DiningChair` BOTH carry `CompProperties_Art` in vanilla (ArtableFurnitureBase, art only
activates at Excellent+ quality). The item's own Build section resolves this cleanly: "Art
items (CompArt present)" with no furniture carve-out. Implemented literally: CompArt present
→ quality bump, absent → Beauty StatPart. No code depends on `minQualityForArtistic`/`Active`.
For the proof script this means a real DiningChair/Bed would take the quality-bump path, not
Beauty — so the proof uses a Wall (unambiguously non-art, and the spec's own "+3" example) for
the Beauty-StatPart half instead of a chair, with a comment explaining why.

## Build (all under src/RimMandrake/LuminousPigment/)
- `Source/CompDeepfire.cs`: added Scribed `bonusApplied` (never reset by RemoveAllCoats —
  the one Farming guard the spec asks for). `AddCoat()` now detects "first coat" (coats==0 &&
  !bonusApplied), calls `DeepfireFirstCoatBonus.Apply(parent)` and sets bonusApplied=true.
  Stack-split guard: if the parent is a stacked (>1) art item, `Thing.SplitOff(1)` is placed
  near the original FIRST (so PostSpawnSetup can light it), then the split's own fresh
  CompDeepfire (stackCount 1) takes the coat via a single recursive `AddCoat()` call — the
  rest of the original stack is untouched. Defensive: every CompArt/CompQuality def this
  mod's injector targets ships stackLimit 1 in practice.
- `Source/DeepfireFirstCoatBonus.cs` (new): `IsArtItem`/`Apply` — `CompQuality.SetQuality(q+1,
  ArtGenerationContext.Colony)` capped at Legendary; no-op (by design) for non-art things,
  since the Beauty bonus is entirely the StatPart's job and needs no bonusApplied gate (it's
  stateless, cannot double-fire).
- `Source/RM_StatPart_Deepfire.cs` (new): `beautyFlat*sizeFactor + beautyPct*baseBeauty`,
  `sizeFactor = min(area,4)`, gated on `CompDeepfire.coats>0 && !IsArtItem`. Appended (via
  PatchOperationAdd) after StatDef Beauty's existing parts, so `val` at TransformValue entry
  already has StatPart_Quality's factor folded in — matches the spec's bed example exactly.
  `ExplanationPart` has no running `val` (confirmed via RimSage), so a small
  `ConditionalWeakTable<Thing,object>` caches the last TransformValue-seen baseBeauty per
  Thing for the stat-card explanation line, populated moments earlier in the same GetValue
  call the stat card always makes before asking for the explanation.
- `Source/DeepfirePaintUtility.cs`: added `FirstCoatBeautyFlat=3`, `FirstCoatBeautyPct=0.25`,
  `FirstCoatBeautySizeCap=4` to `DeepfirePaintDefaults` (plain constants, matching step 5/6's
  own precedent — Mod Settings wiring is DEEPFIRE_MOD_SETTINGS_1's).
- `Patches/DeepfireBeautyStatPart.xml` (new): PatchOperationAdd onto
  `StatDef[defName="Beauty"]/parts`, adding `RM_StatPart_Deepfire` with flat=3/pct=0.25.
- `Source/DeepfireFirstCoatDebugActions.cs` (new): dev actions under Actions\FirstCoat: ...
  (spawn art Normal/Legendary, spawn wall, coat/remove/report/destroy thing at cell) — each
  writes one `[DeepfireFirstCoat] {json}` log line, coat/remove go through
  `CompDeepfire.AddCoat()`/`RemoveAllCoats()` directly (same entry points the real
  WorkGiver/JobDriver path ends in).
- csproj: added the three new .cs files to `<Compile Include>` (EnableDefaultCompileItems
  false — verified all three compile).

## Proof script (written, NOT run)
`python.exe src\RimMandrake\bridgetools\prove_deepfire_firstcoat.py [--start] [--x --z]` —
spawns a Normal SculptureSmall, coats once (→ Good, bonusApplied true), coats again (→ still
Good, no re-bump), then a fresh Legendary sculpture coated once (stays Legendary, coat still
charged); spawns a Wall, coats it (Beauty rises by exactly flat*1 + pct*baseBeauty), strips
(Beauty back to baseline), reapplies (same rise, not double); asserts no new Deepfire/FirstCoat
log errors. Exit 0/1/2 same convention as prove_deepfire_floor.py.

## Verification
- dotnet build (`/mnt/c/Users/Mandrake/.dotnet/dotnet.exe build ... -c Release`): 0 errors, 0
  warnings, both before and after the XML fix below.
- XML parse: all 22 XML files under the mod (Defs/Patches/About) parse clean, including the
  new patch (first draft used `--` inside an XML comment, illegal per spec — column-precise
  ParseError caught it; fixed by removing the double-hyphens).
- `run_selftests.py`: 77/79 passed, 1 unmeasured (selftest_tool_metadata.py — needs a Windows
  JawaBench build, pre-existing/expected), 1 FAILED — `selftest_deployed_biome_refs.py`, 19
  dangling RUT_TheRot/RUT_WeepingStones refs, identical to DEEPFIRE_FLOOR_PAINT_1's own report
  from the same session — pre-existing, unrelated to this mod, not introduced by this change.
- DLL + `.srchash` both rebuilt and staged together (Directory.Build.targets stamps the hash
  automatically on build).

## Land
- [ ] commit(s)
- [ ] rebase onto origin/main
- [ ] push
- [ ] ancestry confirmed

## Result
(fill at end: sha)
