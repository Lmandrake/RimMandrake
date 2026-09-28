# STRANDED_DEFORMATION_DEFNAME_CLASH_1 — RUT_StrandedDeformation exists twice

Found by `BAROQUE_BIOMES_COMPOSE_1`'s §4 collision sweep (defName + abstract
`Name=` sweep, scoped to the wave-0 12-biome compose): `HediffDef`
`RUT_StrandedDeformation` is defined in both `src/RimMandrake/Miasma/` and
`src/RimUtinni/UtinniPatches/`, as two DIFFERENT defs (not a copy-paste
duplicate — the sweep diffed them).

## Why this is a decision, not a fix
Both mods are on the owner's live 630-mod list today, standalone, so this
clash is ALREADY LIVE — whichever def RimWorld's def loader resolves last for
that defName silently wins and the other is discarded with no warning
(RimWorld's own def-loading behavior on a duplicate defName). Baroque Biomes
Wave 1 does not create this problem; it just makes it visible via the sweep.
Someone needs to look at both versions and decide: rename one (which
consumers reference it, and by name, per Ash'karr's shortHash-in-save rule —
check `biome-defname-deletion-must-check-live-tiles` before renaming anything
already placed on the frozen world), or retire one outright if it is dead.

## What is wrong today
- `src/RimMandrake/Miasma/` — a `RUT_StrandedDeformation` HediffDef (find and read it).
- `src/RimUtinni/UtinniPatches/` — a different `RUT_StrandedDeformation` HediffDef.
- Miasma is currently OFF the live mod list (per the corrected
  `design/RimMandrake/biome_mod_unification_spec.md` §1 table); UtinniPatches
  IS on the live list. So today the UtinniPatches version is very likely the
  one actually in play on the shipped save — but this has not been confirmed,
  only inferred from mod-list membership, not from a live def-dump read.

## Watch out
- Check `MIASMA_SHIPPING_NAMES_1` (the owner's working-name card for the
  Miasma) before renaming the Miasma-side def — "stranded deformation" is
  named directly in that card's working-name list, so it may be load-bearing
  design vocabulary, not an arbitrary label.
- Whichever def is retired, grep every XML/C# reference to
  `RUT_StrandedDeformation` first (hediff-granting effects, tooltips, any
  `HediffDef.Named(...)` C# lookup) — a rename or delete that misses a
  reference either dangles a cross-reference or silently no-ops a mechanic.
- This blocks Baroque Biomes Wave 1 (the unified mod joining the owner's full
  list) per that item's own sweep results — Wave 1 should not proceed with
  this clash unresolved, since composing puts both versions in the SAME mod
  where "last loader wins" becomes "same load-root order every time," which
  may be a different (and equally silent) resolution than today's.

## verify
Exactly one `RUT_StrandedDeformation` HediffDef exists across the whole repo,
or the collision is deliberately resolved with the two defs renamed apart and
every consumer repointed.
