# SLIME_GENE_ARCHIVE_BUILD_1 — the gene machine serves placeholder content

## ✅ BUILT AND LIVE-VERIFIED, 2026-09-21

Built the full content the sheet specifies and shipped it as the campaign
archive. **The FROZEN sheet has 33 target genes, not 22** — the task briefing
that started this build undercounted by omitting the "local denizens" table
(A24-A34); the sheet itself (visitors A1-A22 + denizens A24-A34, A23 struck)
is authoritative and that is what got built. Per this repo's "a number you
brief a subagent with comes back to you" lesson, re-measured rather than
trusted.

- **32 new A-list GeneDefs** (A1-A22, A24-A33) in
  `src/RimMandrake/GelatinousSlime/Defs/GeneDefs/SlimeGenes_AList.xml`. A34
  "Slime-resistant" reuses the mod's pre-existing `RM_Gene_SlimeResistance`
  rather than duplicating it, per the sheet's own framing of that entry.
- **25 new B-list rider GeneDefs** (B1-B25) in `SlimeGenes_BList.xml`,
  including B25 "The Reek" — a real animated stink cloud via
  `Gene_TheReek` (new C#, `Source/GeneConditions.cs`), which reuses vanilla's
  own `GasType.RotStink` (the same gas a rotting corpse emits,
  `CompRottable.cs`) rather than inventing a visual system.
- **Every gene moves a real, RimSage-verified field** — `statOffsets`/
  `statFactors` on real StatDefs, `capMods`, `aptitudes` (skill nudges),
  `disabledWorkTags`, the various `*ChanceFactor` fields, or (for the
  hunger-rate/rest-rate/social-opinion costs GeneDef has no field for) a new
  small generic mechanism, `Gene_ForcesHediff` + `RM_ForcedConditionExtension`
  (`Source/GeneConditions.cs`), that adds/removes a small permanent
  `HediffDef` alongside the gene — the same shape vanilla's own
  `Gene_ChemicalDependency`/`Gene_Bloodfeeder`/`Gene_Clotting` use. 17 such
  conditions in `Defs/HediffDefs/SlimeGeneConditions.xml`, 8 of them also
  carrying a mood via `ThoughtWorker_Hediff` in
  `Defs/ThoughtDefs/SlimeGeneConditionThoughts.xml`. A3 reuses vanilla's own
  `Gene_Healing` (periodic permanent-wound healing) folded into the same
  mechanism via an `alsoHealsPermanentWounds` flag, since `geneClass` is
  exclusive; A25 reuses vanilla's `Gene_Clotting` directly (no detour needed,
  its cost is native fields only). A handful of sheet costs describe
  something no GeneDef/HediffStage field can express at all (a per-hour
  distraction window, "near a corpse", a scheduled monthly binge) and are
  narrowed to the closest always-on real stat — each flagged `[SIMPLIFIED]`
  inline in the XML rather than silently invented.
- **B-list hiding is two existing mechanisms, no new UI code**:
  `Dialog_GeneArchive` only ever reads `archive.targetGenes`, and every
  rider sets `canGenerateInGeneSet=false` (the real vanilla field that keeps
  a GeneDef out of any randomly-generated GeneSet/genepack).
- **P7's two named exceptions are real**: `CompTargetEffect_InjectSlimeGenes`
  (`Source/GeneSeeker.cs`) now doubles the Slime-marked increment when the
  rider is B25 "The Reek", and halves it (to zero) when the patient already
  carries A16 "Pheromone charm" — both per the sheet's own curation
  principles text, not invented.
- **Campaign archive**: `RUT_SlimeGeneArchive`
  (`src/RimUtinni/UtinniPatches/Defs/GeneArchiveDefs/RUT_SlimeGeneArchive.xml`),
  `priority=100` against the universal mod's `priority=0`. `DefaultArchive.xml`
  is untouched.
- **Priority mechanism verified before authoring, then live-verified after**:
  read `GeneArchiveDef.Active` and `Dialog_GeneArchive` (`Source/GeneArchive.cs`)
  — it really does pick the highest-priority archive with a non-empty
  `targetGenes`, exactly as the placeholder's header claims. Confirmed live in
  a quicktest (11-mod `modset_builder.py --tier slime`, new tier added):
  spawned an `RM_GeneSeeker`, fired its "Ask the archive" gizmo over the real
  bridge (`rimworld/execute_gizmo`), and screenshotted the actual
  `Dialog_GeneArchive` window showing "Amphibious lungs", "Kolto glands",
  "Limb regrowth", "Great frame"... — the campaign's list, not vanilla's 17
  placeholders.
- **Mod Settings**: `SlimeSettings.preferHigherPriorityArchive` (default
  `true` = shipped behaviour), consulted by `GeneArchiveDef.Active` and
  invalidated on `WriteSettings()` so the toggle takes effect without a
  restart.
- **Fixed along the way, live-caught**: `RimWorld.Aptitude` has a CUSTOM XML
  loader (`LoadDataFromXmlCustom`) that is NOT the `<li><skill>X</skill>
  <level>Y</level></li>` shape every other list field uses — the list item
  itself must be renamed to the SkillDef's defName
  (`<aptitudes><Crafting>-1</Crafting></aptitudes>`, no `<li>` wrapper at
  all). Got this wrong twice before a live load surfaced the actual
  `Could not resolve cross-reference` failures; 8 GeneDefs were silently
  discarded from the DefDatabase each time. Also found and fixed:
  `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` was stale by one
  mod (missing `mandrake.rm.gelatinousslime`, which was live) — recaptured
  it from the actual pre-swap live list rather than leave the doctrinal full
  list wrong for the next restore.
- **Verify**: `validate_patch.py` 0 errors on every touched file; the
  `RM_GelatinousSlime.csproj` build (`dotnet build`, Windows-native) is 0
  warnings/0 errors; `run_selftests.py` 72/72 passed; live load on the new
  `slime` modset_builder tier clean (no config errors, no cross-ref failures,
  no exceptions naming anything in this build) after the Aptitude fix.

## the gap, MEASURED 2026-09-20 (superseded above, kept for history)

The Slime's headline mechanic is the gene machine. The owner **ACCEPTED** its
content lists on **2026-09-06** and they were frozen the next day
(`BIOME_FREEZE_FABLE_REVIEW_1`): `design/Jawa/worldbuilding/biomes/the_slime_gene_lists.md`,
an **A-list of targets** (A1–A23, with A23 "battle premonition" STRUCK on his
ruling — too Force-adjacent, P2 wins) and a **B-list of riders** (B1–B25, the
hidden price, including the owner-commissioned **B25 "The Reek"**).

None of it was ever built, and nothing tracked that. VERIFIED this window:

- `src/RimMandrake/GelatinousSlime/Defs/GeneDefs/SlimeGenes.xml` contains
  **exactly 1 GeneDef** — `RM_Gene_SlimeResistance`.
- The only `GeneArchiveDef` anywhere in `src/` is
  `src/RimMandrake/GelatinousSlime/Defs/GeneArchiveDefs/DefaultArchive.xml`,
  the **universal-mod placeholder**. There is no `RUT_`/campaign archive.

🔴 **The placeholder's own header says it is supposed to be overridden:**

> *"THIS IS A DEF, NOT A LIST IN CODE, AND THAT IS THE WHOLE POINT. The RUT
> layer swaps the campaign's frozen SW gene lists in by shipping its own
> `RM_GeneArchiveDef` with a HIGHER `priority`; `Dialog_GeneArchive` reads
> whichever archive wins. Nothing in this mod's C# names a single gene."*

So the machine works, the dialog opens, the player gets genes — **the wrong
ones**. This is the worst shape a gap can take: it does not look like a gap in
game. Nothing errors, nothing is missing on screen, and the biome's signature
economy is quietly fake.

## why it was invisible

Found by a sweep the owner asked for on 2026-09-20, after `RUT_BlueDesert` was
caught shipping 1,029 tiles with no life for the same reason: **work ratified in
a FROZEN sheet's "Owed" list never became a ledger item.** See
`BLUE_DESERT_LIFE_AUTHORING_1`. The sheets are design authority; they are not a
queue, and nothing reconciles the two.

## spec

1. **Author the GeneDefs** for the accepted A-list and B-list. Read
   `the_slime_gene_lists.md` — it is FROZEN and it is the target, not a draft.
   Each target is priced; each rider bites. ⛔ A23 is STRUCK — do not build it.
2. **Ship the campaign archive**: a `GeneArchiveDef` in the RUT layer with a
   **higher `priority`** than `DefaultArchive.xml`, per the mechanism the
   placeholder's own header documents. ⛔ Do not delete or edit the default —
   it is the universal-mod fallback and is meant to lose on priority.
3. **Honour the P-laws** as the sheet states them — they are owner rulings, not
   guidance: P4 every gene is a trade, never pure upside · P5 riders are visible
   AND felt (each shows on the body or in behaviour and moves at least one stat)
   · P6 costs land where Jawas live · P7 the marked are hard to love · P8 machine
   genes are heritable.
4. **Knobs K1/K2 are already ruled** — K1 unlimited visits, riders accumulate;
   K2 riders permanent. K3 (animals) and K4 are not; do not invent them.
5. **Mod Settings**, per the standing rule.

## Watch out

- 🔴 **Never guess a GeneDef name or field.** The placeholder's header records
  that every defName in it was read out of the live GeneDef index via RimSage,
  not guessed — hold the new work to that bar.
- ⚠️ **B25 "The Reek" needs a real gas-emission visual**, not a description. The
  sheet specifies an animated stink cloud (Biotech gas-emission gene visual). A
  rider that only exists in tooltip text fails P5 outright.
- ⚠️ The riders are deliberately hidden from the player's list. Do not surface
  the B-list in any UI.
- Check whether `Dialog_GeneArchive` and `GeneSeeker.cs` actually resolve the
  higher-priority archive as the header claims **before** authoring 50+ defs
  against that assumption — read the C#, don't trust the comment.

## verify

In game: open the gene machine and see the campaign's accepted targets, not the
17 vanilla placeholders. Then a post-load def dump confirming the campaign
archive won on priority — not the XML, which proves nothing about which archive
the dialog picked.

## criteria

The gene machine offers the owner's accepted list, every gift is priced, every
rider is visible and felt, and no placeholder content reaches the player.
