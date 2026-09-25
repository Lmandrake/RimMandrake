# TWILEK_TROPE_GENES_MOVE_1

Move the Twi'lek submissive-aggression, high-libido and beautiful genes off
the xenotype and onto individual pawns as a background or trait, so a
stereotype is a fact about a person rather than about a race — a mechanism
change, not a gene-list edit.

Owner ruling, 2026-09-15 (relayed via `--owner-said`): "Move them off the
species." Caused by `XENOTYPE_CANON_CORRECTION_1` <- `SPECIES_CANON_LIBRARY_1`.

## spec

Three genes on `RSW_RimMandrakeTwilek` (`src/RimStarWars/StarWarsRaces/Defs/
XenotypeDefs/RimMandrakeXenotypes.xml`) made a slavery-trope stereotype a
species-wide guarantee for every Twi'lek pawn generated:

- `Turn_Gene_AgressionSubmissive` (donor: Integrated Genes,
  `turnovus.biotech.integratedgenes`) — mood bonus while enslaved, mood
  penalty while free, `socialFightChanceFactor 0.25`,
  `SlaveSuppressionFallRate` factor `0.5`, plus several gene-only fields
  (`aggroMentalBreakSelectionChanceFactor`, `prisonBreakMTBFactor`) that have
  no TraitDegreeData equivalent.
- `Libido_High` (vanilla Biotech) — `lovinMTBFactor 0.5`, nothing else.
- `Beauty_Beautiful` (vanilla Biotech) — `statOffsets: PawnBeauty +2`,
  nothing else.

Two waves:

**Wave 1** (`fc16d5507`, 2026-09-17): removed all three genes from the
xenotype's `<genes>` list. Verified only the Twi'lek block was touched;
Chagrian/Zeltron carry their own separate `Libido_High`/`Beauty_Beautiful`
rows and were left alone. Survives a future `gen_races_mod.py` regeneration
because that generator's shipped-metadata-wins path reads the current file
as its floor.

**Wave 2** (this wave, 2026-09-24): the "onto individual pawns" half.
Checked each gene's real mechanism against the live GeneDef/TraitDef XML via
RimSage (`mcp__rimsage__get_def_details`, `search_source`,
`read_csharp_symbol` against `TraitDegreeData` and `BackstoryDef`) before
writing anything, per-gene disposition:

- **Beauty_Beautiful — nothing built.** Vanilla Core already ships a
  `Beauty` TraitDef whose degree 2 ("beautiful") carries the identical
  `<statOffsets><PawnBeauty>2</PawnBeauty></statOffsets>` the gene gave,
  rolled individually for any pawn of any race by the ordinary trait
  generator. The architecture goal — "a fact about a person, not a race" —
  is already satisfied for this gene by a system that predates this item.
  Building a second beauty mechanism would be a duplicate.

- **Turn_Gene_AgressionSubmissive → `RM_Submissive`** (new TraitDef,
  `src/RimStarWars/StarWarsRaces/Defs/TraitDefs/RM_TwilekTropeTraits.xml`).
  `TraitDegreeData` (confirmed via `read_csharp_symbol`) supports
  `socialFightChanceFactor` and `statFactors` directly, so this is a
  faithful port of the gene's two behavioural stat effects — not an
  approximation — just individually rolled (`commonality 3`) instead of
  racially guaranteed. `conflictingTraits: Bloodlust` for thematic
  coherence (verified `Bloodlust` is a real vanilla TraitDef).

- **Libido_High → `RM_Amorous`** (same file). Confirmed via
  `JobDriver_Lovin.GenerateRandomMinTicksToNextLovin` (RimSage
  `read_csharp_symbol`) that lovin'-frequency is multiplied only by
  `Pawn.genes` and by any `Hediff` carrying
  `HediffComp_GiveLovinMTBFactor` — nothing else reaches it.
  `TraitDegreeData` has no field that reaches either path, and
  `BackstoryDef` (also read via RimSage) can only force other TRAITS, never
  a gene or a hediff. **So a TraitDef genuinely cannot replicate the
  lovin'-frequency multiplier itself without a Harmony postfix** on
  `GenerateRandomMinTicksToNextLovin` (or on trait-add, to attach a
  `HediffComp_GiveLovinMTBFactor` hediff) — this is the same C#-against-the-
  Biotech-API gap wave 1 already flagged, now scoped precisely to this one
  mechanic rather than to all three genes. `RM_Amorous` ships instead with
  a real, verifiable, individually-rolled field: `disallowedThoughts` on
  `RebuffedMyRomanceAttempt`/`FailedRomanceAttemptOnMe`/
  `FailedRomanceAttemptOnMeLowOpinionMood` (all three confirmed real
  ThoughtDefs via `search_defs`) — a forward personality that shrugs off
  romantic rejection instead of being stung by it.

Both new TraitDefs are RM_-tier per `design/NAMING_SCHEME_PLAN.md`: nothing
about a "submissive" or "amorous" personality is Star-Wars-specific: tier is
about what the content IS, not which mod folder ships it first. They live in
the StarWarsRaces mod (`mandrake.rsw.starwarsraces`) because that is the mod
performing this specific migration; no owner ruling asked for a shared
RM-tier library mod extraction, so none was speculatively built.

## verify

- `skills/rimworld-modding/scripts/validate_patch.py` against
  `RM_TwilekTropeTraits.xml` with `--defs` pointed at Data, Workshop and
  Mods: **OK, 0 errors, 0 warnings** (fixed one `--` double-hyphen-in-
  comment violation caught on the first pass, per this repo's own XML-
  comment trap).
- Cross-checked every referenced defName against the live def dump
  (`DefDump/defs.sqlite`, 78,489 rows) and RimSage before writing: `Beauty`
  (TraitDef), `Bloodlust` (TraitDef), `RebuffedMyRomanceAttempt`/
  `FailedRomanceAttemptOnMe`/`FailedRomanceAttemptOnMeLowOpinionMood`
  (ThoughtDefs), `SlaveSuppressionFallRate` (StatDef) — all confirmed to
  exist with the exact spelling used. `RM_Submissive`/`RM_Amorous` checked
  against the dump for defName collisions: none.
- `python3 src/RimMandrake/Utils/run_selftests.py`: **75/75 passed** (2
  skipped for unrelated reasons — art-reference and a lupa-dependent
  package test), 0 failed, 0 unmeasured.
- **Not done this wave**: no live quicktest. `./game` reported
  `NOT RUNNING` / `recorded: DOWN` at the start of this wave (owner's
  restart cycle was flapping) — offline-only work per the task brief. The
  new TraitDefs will get their first live confirmation (do they appear in
  the trait pool, does `disallowedThoughts` actually suppress the named
  thoughts) at the next load; nothing here is behaviour that could silently
  no-op the way a patch xpath can, since TraitDef is a plain top-level def
  with no patch/xpath layer to fail quietly.

## criteria

- [x] Twi'lek xenotype no longer guarantees the three trope genes (wave 1).
- [x] Beauty is confirmed already individually-rolled, race-independent, no
      new work required.
- [x] Submissive-aggression trope reachable by any pawn via a real TraitDef
      with faithfully-ported stat effects.
- [x] High-libido trope reachable by any pawn via a real TraitDef, with an
      honest note on the one mechanic (lovin'-frequency multiplier itself)
      that cannot be reached without new C#.
- [ ] **Owed, not this item's scope to force**: a Harmony postfix that lets
      an individual, race-independent condition apply the actual
      `lovinMTBFactor`-equivalent multiplier (via `HediffComp_
      GiveLovinMTBFactor` or a direct postfix on
      `GenerateRandomMinTicksToNextLovin`). File as new work if the owner
      wants full mechanical parity for the libido trope specifically;
      nothing today blocks on it, since `RM_Amorous` already gives that
      trope a real, individual, race-independent expression.
