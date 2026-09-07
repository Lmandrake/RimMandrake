# DROID_FACTIONS_IN_FROZEN_SAVE_1 — census

Filed with no spec/criteria. Scope decided by FOUNDRY, 2026-09-07: census the ONE
save that is actually "the frozen world" — `Saves\WORLDMAP_V1_original_e.rws`
(598 mods, matches `ModsConfig.FULL.LATEST.xml`'s modCount). The other candidate,
`Autosave-9.rws`, is a 25-mod minimal-list quicktest scratch save (its own
`<modIds>` header says so), not a campaign save — the exact
"25-mod quicktest autosave mislabeled as the campaign" trap the 2026-09-07 BENCH
handoff doc already names. No other save on disk claims to be a campaign in
progress, so this census covers the frozen world only.

## method

`xml.etree.ElementTree` over the save's plain XML (not the binary map grids —
factions/pawns/needs are ordinary legible XML, per `rimworld-savegame` skill §1/§3).
Built a parent map (ElementTree has no `.getparent()`), searched every `<def>`
element for droid-adjacent keywords (droid/asimov/mse/kotor/kx/astromech/mech),
then classified each hit by its real ancestor kind — `factionManager/allFactions`
for factions, the nearest enclosing `<thing Class="...Pawn">` OR `<li Class="...Pawn">`
for pawn-borne needs (the second form matters: a naive "nearest `<thing>`"
walk misattributes a caravan/cryptosleep-casket-contained pawn's need to the
CONTAINER instead of the pawn inside it — caught and fixed before reporting;
6 `Asimov_EnergyNeed` hits initially misread as belonging to
`Building_AncientCryptosleepCasket` were actually its imprisoned `Megascarab`
pawns).

## findings

**FactionDefs**: exactly one droid-specific faction exists on the world:
`Jawa_FreeDroidEnclaves` (1 instance, `factionManager/allFactions`). Vanilla
`Mechanoid` also present (1) — not droid lore in this campaign's design
(mechanoids are their own separate canon, see `MECHANOID_ORIGIN_CANON_1`), listed
here only because it matched the "mech" keyword.

**PawnKindDefs**: **zero** droid-lore pawnkinds (no `Jawa_Droid_*`, no MSE, no KX,
no Astromech, no Protocol droid, no KotOR droid) appear as spawned `<thing>`/`<li>`
Pawns anywhere on the frozen world. The only "mech" keyword hits among spawned
pawns are vanilla Mechanoids: `Mech_Militor`, `Mech_CentipedeGunner`,
`Mech_Pikeman` (1 each). The droid program's own kinds are not yet on the map —
consistent with `DROID_SYSTEM_BUILD_1`/`DROID_FDE_KINDS_REPOINT_1` still being
build-stage work, not campaign content yet.

**Need classes — the real finding**: `Asimov_EnergyNeed` is scribed on **61 of the
77 total pawns** carrying basic Food/Rest needs (i.e. nearly every creature on the
map), and NONE of the 61 are a droid-lore pawnkind:

```
  11  Eopie            7  Bantha           6  Megascarab       5  Corinathoth
   5  AA_Behemoth      4  Human            3  Qormot           3  Bolotaur
   3  IridonianReek    2  Uvak             2  Manka            1  Mech_Militor
   1  Mech_CentipedeGunner  1  Mech_Pikeman     1  AM_Daggersnout  1  AM_Siegebreaker
   1  Lothcat          1  JRWGeralinura    1  BMT_FungalFerret  1  BMT_FacetMothLarvae
   1  Behemoth
```

Overwhelmingly wildlife/livestock, plus 4 Humans and 3 vanilla Mechanoids — the
Asimov mod's droid-only "energy need" is being attached almost universally
(a Harmony patch too broad for its own gate, not a per-pawnkind grant), not to
any droid at all. This is hard, counted evidence for the already-queued
`DROID_RETIRE_DEPOT_ASIMOV_1` (Asimov named there for retirement); noted on that
item rather than duplicated as a new bug filing.

## verify

```
PROVE   the counts above, reproducible by re-running the census script's method
        against WORLDMAP_V1_original_e.rws (or whichever supersedes it)
EXPECT  a droid FactionDef (Jawa_FreeDroidEnclaves) exists; no droid PawnKindDef
        spawned yet; Asimov_EnergyNeed present far outside any droid population
LIES    trusting a naive "nearest <thing> ancestor" walk for a need's owner --
        misattributes anything inside a container (caravan, cryptosleep casket,
        transport pod) to the container itself, not the pawn inside it
```
