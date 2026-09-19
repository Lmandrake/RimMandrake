# AQUATIC_WATER_BREATHING_GENE_1

Design and build a real water-breathing mechanism for the aquatic xenotypes that
currently have none. Design brief: `design/RimStarWars/aquatic_water_breathing_design.md`
(written 2026-09-18; read it in full before touching this item — it has the exact
mechanism shape, the engine facts it was MEASURED against, and both cards below in
more depth).

## build log — 2026-09-19, FOUNDRY, offline

Built the mechanism the design brief specified, unwired. Everything below was
confirmed against the live def dump (`captures/2026-09-19T04-19-13Z`, 622 mods)
and via RimSage source reads, not guessed.

1. **`RSW_WaterBreathing`** — new `GeneDef`,
   `src/RimStarWars/StarWarsRaces/Defs/GeneDefs/RSW_Aquatic.xml` (hand-authored,
   new file — `SW_Genes.xml` is `gen_races_mod.py` output and not touched).
   `waterCellCost=1`, `makeImmuneTo` a `<li MayRequire="mandrake.rm.flowworks">RM_PitDrowning</li>`,
   `RSW_SWparts_Category`, biostat 1/−2, `customEffectDescriptions` tooltip line.
   Icon path corrected during the build from a guessed `Gene_Fins` to the real
   vanilla `UI/Icons/Genes/Gene_WebbedPhalanges` (confirmed via RimSage against
   the shipped `WebbedPhalanges` GeneDef, which this gene's water-cell-cost
   effect subsumes).
2. **`SoakingWet` patch** — `src/RimStarWars/StarWarsRaces/Patches/RSW_Aquatic_SoakingWet.xml`.
   Corrected during the build: the design brief's own draft xpath
   (`ThoughtDef[defName="SoakingWet"]/nullifyingGenes`) would have matched
   nothing — RimSage's raw read of vanilla `SoakingWet` shows it carries no
   `<nullifyingGenes>` element at all (only `nullifyingPrecepts`), so that
   `PatchOperationAdd` would have silently added nothing on load. Retargeted to
   add the whole `<nullifyingGenes>` element onto the ThoughtDef itself.
3. **FlowWorks `CompPitFitting.CanSwim`** — added one clause ahead of the
   existing swim-art heuristics: `p.health.immunity.AnyGeneMakesFullyImmuneTo(RMPits_HediffDefOf.RM_PitDrowning)`.
   Vanilla public API (`ImmunityHandler.AnyGeneMakesFullyImmuneTo`, confirmed via
   RimSage source read), references no StarWarsRaces def — no cross-mod
   dependency either direction. **`PIT_SUPERDEEP_COLLAPSE_1` (filed 2026-09-17)
   is still `proposed`/unbuilt** — `CompPitFitting.CanSwim` has NOT moved from
   where the design brief described it; this clause landed in today's real
   location. If that item rehouses `CanSwim` later, this clause travels with it
   (flag it in that item's REHOUSE notes when it's picked up).
4. **MayRequire gate** — confirmed generically via RimSage
   (`DirectXmlToObjectNew.ValidateMayRequires` / `DirectXmlCrossRefLoader`):
   `MayRequire` on any `<li>`, in a `Defs` file or a `Patch`, is a load-time
   check independent of PatchOperations — the gene loads fine with FlowWorks
   absent, `makeImmuneTo` on that `<li>` simply drops.
5. Verified: `dotnet build RimMandrake_FlowWorks.csproj -c Release` clean (0
   warnings, 0 errors); `validate_patch.py` on both new XML files with
   `--live` against the current dump — 0 errors, 2 advisory warnings (both
   reviewed and expected: the vanilla icon path can't be told apart from a typo
   by a mod-local texture scan, and the `SoakingWet` patch isn't wrapped in
   `PatchOperationFindMod` because its target is Core, which is always active);
   full `run_selftests.py` — 61/61 passed, including `selftest_pit_logic.py`.

**Deliberately NOT done, and both still genuinely his:**

- **Card 1 — roster.** The gene is built but wired onto **no xenotype**. The
  item's own filing names Mon Calamari/Nautolan/Gungan/Selkath; the canon
  library instead calls Gungan a breath-holder (not a water-breather) and rates
  Quarren "most comfortable underwater" — a species the item never named. Do
  not guess which species get `RSW_WaterBreathing`; wiring it into
  `RimMandrakeXenotypes.xml` (via `gen_races_mod.py`'s shipped-metadata-wins
  path, per the design brief §3) is the next owed step once he rules.
- **Card 2 — deep water.** Still impassable for everyone, including a
  water-breather. Opening it needs a per-pawn pathing context (new engine work,
  wide blast radius) and was explicitly scoped out of this item as its own
  future item, not a field on this gene.

**Also owed, separately:** live-quicktest proof (a water-breather and a
baseliner in a flooded FlowWorks pit; wading path/mood on a drafted
water-breather) — offline build only this pass, no bridge touched.

## status

Left `doing`. Not closeable: the roster card is unresolved and there is no
live-game proof this actually behaves as designed, only an offline build that
compiles, validates, and passes the existing self-test suite.

## 2026-09-19 FOUNDRY (overnight full-621-mod batch) — gene applies cleanly, live-confirmed

`StarWarsRaces` had 2 drifted files (`Defs/GeneDefs/RSW_Aquatic.xml`,
`Patches/RSW_Aquatic_SoakingWet.xml`) — deployed this pass
(`deploy_custom_mods.py --mod StarWarsRaces --apply`). Full 621-mod cold load
confirmed clean via `Bridge token:`. Live test: spawned a colonist, added
`RSW_WaterBreathing` as a xenogene via `jawa/pawn_genes action=add` — **no
exception**, `xenogeneCount` incremented 0→1, gene listed back correctly, and a
follow-up `jawa/pawn_get` on the same pawn read back fine (no crash, appearance/
skills/traits all intact). **Confirms the minimum bar from this item's own recipe**
("at minimum confirm the gene itself applies cleanly with no exceptions").

**Not tested this pass** (time-boxed batch, prioritized elsewhere): rigging an actual
`RM_PitDrowning` immunity test (needs a FlowWorks pit + a flooded cell, more setup
than this pass's slot allowed) and the wading-path/mood behavior. Both remain owed.
Card 1 (roster wiring) and Card 2 (deep water pathing) are unchanged — still explicitly
his to rule on, not touched this pass.
