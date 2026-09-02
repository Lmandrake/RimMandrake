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
