# FORSAKEN_CRAGS_PREDATORS_BUILD_1 — Cindermare + Skarnix, wild threat pair

Owner-approved design rows from `FORSAKEN_CRAGS_FAUNA_1` (closed) — both `approve`,
no edits requested. Full design content: `infrastructure/state/items/FORSAKEN_CRAGS_FAUNA_1.md`
and the ruled sheet `design/Jawa/worldbuilding/review/forsaken_crags_fauna_sheet.decisions.json`
(`decidedBy: owner-said`, frozen 2026-09-02).

Bundled as one build item (not split) because both are the same shape: wild
(untameable) `AB_RockyCrags` threats sharing an art context (the two promoted
`moornak_opt1`/`moornak_opt2` mockups) and a design register (environmental
valve rather than combat stats) — same pattern `LIVESTOCK_STARTER_TRIO_1` used
to batch onnik/karrask/moornak.

## spec

1. **Cindermare** (`moornak_opt1.png`) — wild threat, `AB_RockyCrags`. No mouth
   in the art, so its kill mechanic is a cold-drain grip (saps body heat on
   contact) rather than a bite. Solitary, untameable. Mane/hide harvested only
   from a kill (no live-shear/farm loop — this is a predator, not livestock).
2. **Skarnix** (`moornak_opt2.png`) — wild threat, `AB_RockyCrags`. Cat-large
   ambush stalker. Valve is behavioral, not combat: will not cross firelight
   or a heated space, so a lit camp neutralizes it without requiring fight
   stats. Untameable.

Both: RimStarWars tier (world/planet fauna, not campaign-specific), sprites
via `generating-rimworld-sprites` contract (128 px/cell, chroma-key alpha,
silhouette-first matching the promoted mockup art), beast-normalization
spirit (born normalized, no retrofit).

Invented premises carried over from the design pass (all declared, none
snuck in): the two names, Cindermare's cold-drain-grip mechanic (the art has
no mouth, so a bite kill was never on the table), Skarnix's firelight valve.

## verify

- Def compiles/loads clean, `validate_patch.py` 0 errors.
- Live quicktest: both spawn as wild `AB_RockyCrags` fauna, Cindermare's
  cold-drain attack registers a hypothermia-flavored damage/hediff on
  contact (not a bite wound), Skarnix demonstrably avoids a lit tile
  (`GlowGrid` check or observed pathing away from a heat/light source).
- Art matches the promoted mockups' silhouette (side-by-side check against
  `moornak_opt1.png`/`moornak_opt2.png`).

## criteria

Both creatures spawn on `AB_RockyCrags`, both untameable, Cindermare's
cold-drain and Skarnix's firelight valve are live-proven mechanics (not just
flavor text), art traced to the promoted mockups.

## 2026-09-02 (FOUNDRY) — offline build, both creatures, not live-verified

Built entirely offline (a sibling fork held the bridge for an unrelated
restart) — `validate_patch.py` clean and `dotnet build` clean, but **nothing
below has been observed running**, per this item's own honesty bar.

- **Both creatures**: `ThingDef`/`PawnKindDef` structurally patterned off
  vanilla `Wolf_Timber` (RimSage `get_def_details`, not guessed) —
  `QuadrupedAnimalWithPawsAndTail` body, `wildness=1.0` (zeroes
  `TameUtility`'s tame chance outright, a real mechanism rather than an
  unenforced "untameable" flavor claim), `trainability=None`, `petness=0`,
  no shear/harvest comp (hide/meat only from a kill, matching the design
  row). `mandrake.rsw.livestock`, deployed, **not yet added to
  `ModsConfig.xml`**.
- **Art**: both textures are the owner-approved mockups themselves
  (`moornak_opt1.png`/`moornak_opt2.png`), chroma-keyed to real alpha and
  conformed onto a transparent canvas (Cindermare 512x512, Skarnix 256x256)
  — not freshly generated art. `validate_sprite.py --describe`: real alpha,
  0 chroma-key corner spill, fringe well under threshold on both (0.18%/
  0.39%). **Scope simplification, stated plainly**: `graphicClass =
  Graphic_Single` (one non-rotating texture) rather than a full 4-facing
  `Graphic_Multi` set — the creature looks identical from every rotation.
  A full facing set is a real follow-on if the owner wants true rotation,
  not done here.
- **Cindermare's cold-drain grip**: a REAL mechanism, not flavor text —
  `RSW_ColdDrainDamage` (DamageDef) → `RSW_ColdDrain` (HediffDef,
  `ParentName="InjuryBase"`, same shape as vanilla `Bruise`) wired via the
  tool's `extraMeleeDamages`, on a tool replacing the usual bite (no mouth
  in the art). Mechanism cited against this project's own
  `guy762_RangedDamage_sonic`/`additionalHediffs` precedent
  (`src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/DamageDefs/
  Absorbed_KotorCore_BlasterDamages.xml`), not invented from scratch.
- **Skarnix's firelight valve**: a REAL C# mechanism —
  `CompLightAversion` (`src/RimStarWars/Livestock/Source/
  CompLightAversion.cs`), a `ThingComp.CompTickRare` that forces a
  flee-to-darkness `Goto` job whenever `GlowGrid.PsychGlowAt` reads
  not-`Dark` at the pawn's position. Guard shape and the forced-job call
  are copied from vanilla's own `HediffComp_Disorientation.
  CompPostTickInterval` (same Spawned/!Downed/Awake()/CurJob.suspendable
  gates, same `StartJob(..., JobCondition.InterruptForced, ...,
  resumeCurJobAfterwards: true)` shape) — not a novel AI system. `dotnet
  build`: 0 warnings, 0 errors.
- **NOT done, explicitly**: live spawn, live observation of either
  mechanism actually firing, and no `ModsConfig.xml` entry — all three
  "live-proven" criteria bullets above remain open. This item stays
  `doing`.

## 🔴 2026-09-02 (FOUNDRY) — enabled, tested, found a severe defect, DISABLED again

Enabled `mandrake.rsw.livestock` in `ModsConfig.xml` (593 mods), cold-loaded
clean (no Config errors naming this mod). Then:

- **Cindermare's cold-drain grip: PROVEN live.** `jawa/damage` with
  `damageDef=RSW_ColdDrainDamage`, `amount=15` on a wild Iguana produced
  `RSW_ColdDrain` (severity 12.0) confirmed via `jawa/pawn_get`'s raw
  hediff list — the `DamageDef` → `HediffDef` chain genuinely fires. This
  half of the item's criteria is met.
- **🔴 Both creatures are UNPLAYABLE as spawned pawns — engine-level crash,
  not a bridge quirk.** Any attempt to read either creature's label once
  spawned (`jawa/inspect_string`, `jawa/pawn_get`, `jawa/list_pawns` once
  it iterates far enough) throws `System.ArgumentOutOfRangeException` in
  `Verse.Pawn_AgeTracker.get_CurKindLifeStage()` →
  `RimWorld.GenLabel.BestKindLabel` → `Pawn.get_KindLabel`/
  `get_LabelNoCount`/`get_LabelShort`. **100% reproducible**: 2 separate
  Cindermare spawns + 2 separate Skarnix spawns, 4/4 crash identically on
  first read. `Pawn.get_LabelShort` is called by ordinary vanilla UI
  (hover tooltips, colonist/animal bar, any inspect pane) — this is not a
  bridge-only problem, it would misbehave for any player who looks at one
  of these animals.
- **Root cause NOT found this pass.** Ruled out: a naive lifeStages/
  lifeStageAges count mismatch — both defs have exactly 3 `lifeStageAges`
  (race) and exactly 3 `lifeStages` (kind), matching each other AND
  structurally mirroring vanilla `Wolf_Timber`'s own working 3/3 pattern
  exactly (same `ParentName="ThingBaseWolf"`/`"AnimalKindBaseWolf"`
  abstracts, confirmed by reading
  `Data/Core/Defs/ThingDefs_Races/Races_Animal_WildCanines.xml` directly).
  **Unconfirmed hypothesis**: some other active mod may patch
  `race.lifeStageAges` broadly (adding a stage to many/all animal
  `ThingDef`s) while only patching KNOWN vanilla `PawnKindDef`s' matching
  `lifeStages` to keep pace — leaving brand-new custom kinds like ours
  stage-count-mismatched at the RESOLVED (post-patch) level even though
  our own raw XML is internally consistent. **Not verified** — next step
  is comparing `RSW_Skarnix`'s resolved `race.lifeStageAges` count against
  its `PawnKindDef.lifeStages` count via a live def dump (`jawa/get_defs`
  is scalar-only and cannot see list lengths).
- Skarnix's `CompLightAversion` was **never reached** — every read attempt
  crashed before the mechanism could be observed.
- **Disabled `mandrake.rsw.livestock` again** (back to 592 mods,
  `ModsConfig.FULL.LATEST.xml` synced) pending a fix — this content is not
  safe to leave live. Do not re-enable until the label crash is
  root-caused and fixed.

Criteria status: Cindermare's cold-drain mechanism ✅ proven. Everything
else — Skarnix's valve, both creatures spawning safely as playable pawns,
"both untameable" observed rather than assumed — remains open, and the
label crash is now the blocking issue, not a missing observation.

## 🔴 2026-09-02 (FOUNDRY) — root cause found and fixed, still owed a live re-verify

Root-caused via the live def dump (`DefDump/captures/2026-09-02T03-38-43Z/animals.json`,
captured during the session that first found the crash — resolved, post-patch
data, not raw XML): `RSW_Cindermare`'s resolved `race.lifeStageAges` has **6
entries**, not 3 — the first 3 are `ThingBaseWolf`'s own (`AnimalBaby`/
`AnimalJuvenile` minAge 0.2/`AnimalAdult` minAge 0.5, dog sounds,
`Data/Core/Defs/ThingDefs_Races/Races_Animal_WildCanines.xml` line ~35), the
next 3 are our own re-declared block (minAge 0.25/0.6) — genuinely duplicated,
not a scan artifact.

**Mechanism, confirmed against the real decompiled source**
(`Verse/Pawn_AgeTracker.cs`): `ThingDef ParentName="ThingBaseWolf"` already
declares `<race><lifeStageAges>` (3 `<li>`); our own `ThingDefs_ForsakenCrags.xml`
redeclared `<lifeStageAges>` again with our own 3 entries. RimWorld's XML
inheritance **appends** a redeclared `List<T>` field rather than replacing it
unless the tag carries `Inherit="False"` — neither of our two `<lifeStageAges>`
blocks had it, so each resolved to 6.

The **PawnKindDef** side did NOT double the same way: `AnimalKindBaseWolf`
(the abstract `ParentName` both kinds use) declares no `<lifeStages>` of its
own (confirmed: `combatPower`/`ecoSystemWeight` only,
`Races_Animal_WildCanines.xml` line 148) — so our own 3-entry `<lifeStages>`
block had nothing to append to and stayed at exactly 3.

**The actual crash**: `Pawn_AgeTracker.RecalculateLifeStageIndex()` computes
`cachedLifeStageIndex` by walking `pawn.RaceProps.lifeStageAges` (6 entries,
valid indices 0-5) against the pawn's `growth`. `CurKindLifeStage` then does
`pawn.kindDef.lifeStages[CurLifeStageIndex]` — indexing the KIND's 3-entry
list with an index computed against the RACE's 6-entry list. Once growth is
high enough that the walk lands on index 3, 4, or 5 (any of our own
re-declared, duplicate stages), `kindDef.lifeStages[3..5]` throws
`ArgumentOutOfRangeException` on a 3-element list — exactly the observed
`System.ArgumentOutOfRangeException` in `get_CurKindLifeStage()`.

**Fix**: added `Inherit="False"` to both `<lifeStageAges>` tags in
`src/RimStarWars/Livestock/Defs/ThingDefs_Animals/ThingDefs_ForsakenCrags.xml`
(Cindermare and Skarnix) so our own 3-entry block REPLACES `ThingBaseWolf`'s
inherited 3, giving race=3/kind=3 again, matching `Wolf_Timber`'s own working
shape. The `PawnKindDef` side needs no change — it was never doubled.

`validate_patch.py` (594-mod set, both `ThingDefs_ForsakenCrags.xml` and
`PawnKindDefs_ForsakenCrags.xml`): 0 errors, 0 warnings (one expected `info`
note on `CompProperties_LightAversion` resolving to our own compiled class,
unchanged from before). Deployed (`deploy_custom_mods.py --mod Livestock
--apply`), file-copy only — `mandrake.rsw.livestock` stays OUT of
`ModsConfig.xml` on purpose; this fix is reasoned from source and the real
resolved-def evidence, but **not yet observed running** — the next bridge
window should re-enable, spawn both creatures, and confirm `jawa/pawn_get`/
`jawa/inspect_string` no longer throw before this item's remaining criteria
(Skarnix's valve, both-untameable, both-spawn-safely) get checked off.
