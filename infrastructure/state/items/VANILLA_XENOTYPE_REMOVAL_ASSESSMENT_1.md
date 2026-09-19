## the ask (owner, 2026-09-19)

Owner spotted `Impid` (vanilla Biotech's horned, fire-spitting xenotype — read as
"fire imp") and ruled: *"Only Star Wars xenotypes are supposed to be here."* Rather
than purge Impid alone, he asked for a proper BENCH assessment of every
non-Star-Wars xenotype for possible removal, weighing: **(a) do our Star Wars-native
xenotypes already cover the same gameplay role/niche this one fills, and (b) what
does removing it actually cost/break.**

## what FOUNDRY found (2026-09-19, def dump 621 mods, captured 2026-09-19T12:48:16Z)

`src/RimUtinni/PawnFlavor/Patches/PawnFlavorPhase2_Xenotype.xml` (2,922 lines) is a
deliberate, already-built system that keeps a long list of vanilla/other-mod
XenotypeDefs ACTIVE and re-flavors their label/description with campaign-appropriate
lore text, rather than cutting them. This is not a stray leftover — someone
purpose-built this file to give every vanilla xenotype a Star-Wars-flavored
description (e.g. Impid: *"Horned and quick as a scared varmint... can spit fire..."*).

**14 non-Star-Wars xenotypes touched by that file** (everything else in it is an
`RSW_RimMandrake*` species, correctly in scope):

```
Baseliner   Dirtmole   Genie   Highmate   Hussar   Impid   Neanderthal
Pigskin   Sanguophage   Starjack   VRESaurids_Saurid   Waster   Yttakin
guy762_debugxenotype_droid
```

`Impid` also carries a vanilla Biotech FactionDef, `TribeSavageImpid` — check whether
that faction (or any other of these 14) is actually placed on the frozen Ash'karr
world (per CLAUDE.md's "there is no worldgen feature... one hand-made, frozen world"
— a faction absent from that hand-made placement is already effectively absent from
every player's game, which changes the removal calculus for that one).

## what to assess, per xenotype

- **Role coverage**: what gameplay niche does it fill (fast/fragile raider, tough
  soldier, cave-dweller, etc.) and is there already an `RSW_RimMandrake*` species (or
  a droid kind) that covers the same niche without it?
- **Removal cost**: what references it — FactionDefs, PawnKindDefs, other genes/
  RulePackDefs sharing its GeneDef pool, any canonical-save pawn already carrying it,
  any quest/incident keyed on it. `guy762_debugxenotype_droid` in particular may be
  load-bearing debug tooling, not player-facing content — check before recommending
  removal.
- **Removal mechanism**: Cherry Picker is the sanctioned cut path (never a bare
  mod uninstall) per `rimworld-content-moderation`; note the post-cut tag/pawnkind
  reattribution check that skill requires.

## Watch out

- `PawnFlavorPhase2_Xenotype.xml` is one large `PatchOperationSequence` per
  xenotype — removing an entry means deleting its whole `<li Class=
  "PatchOperationSequence">` block cleanly, not just its content, or the XML
  structure breaks for the next entry.
- A def dump hit only proves the xenotype LOADS somewhere in the 621-mod set, not
  that it is reachable by a real pawn (faction xenotype chance, quest-only kinds,
  etc.) — verify reachability before recommending against removal on presence alone.
- This is an assessment/recommendation ticket, not an execution order — the actual
  cuts still need an owner ruling per xenotype (or per batch), same as any other
  content-removal decision.
