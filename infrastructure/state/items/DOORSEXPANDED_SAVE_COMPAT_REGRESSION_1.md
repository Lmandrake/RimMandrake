# DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1

Caused by `STARWARS_DONOR_SUNSET_1` Wave 4 (commit `c16fd4f0`), discovered live 2026-09-09 ~20:12Z.

## spec
Wave 4 retired `lumi.doorsexpanded` after a thorough whole-modlist XML/def cross-reference
check (0 dependents found — genuinely correct for that check). But `CANONICAL_ASHKARR_2026-09-09.rws`
holds placed door Things built from Lumi's own ThingDefs — a **Scribe-level (save-content)**
reference, invisible to any def-loader/XML cross-reference sweep. Consequence:

1. `rimworld/load_game` on the canonical save refused: `compatibility.status=missing_mods`
   (589/590 active).
2. A force-load with `ignoreModCompatibility: true` reached `programState: Playing`
   (`ticksGame: 108949`, ~20s) then the entire `RimWorldWin64` process died within seconds,
   no crash trace — `Player-prev.log` cuts off mid map-finalization with only a routine,
   non-fatal ReGrowthCore exception logged before the cutoff.
3. `lumi.doorsexpanded` was restored to the live `ModsConfig.xml` (~20:15Z, a separate
   FOUNDRY pass) to unblock the campaign. **The donor is back — Wave 4's retirement did
   not survive contact with the real save**, despite `STARWARS_DONOR_SUNSET_1` showing
   `done`.

**General lesson**: "no other mod's XML/def references this donor" proves the donor is
safe to retire against the MOD STACK. It says nothing about whether the LIVE SAVE has
already placed objects built from that donor's defs. Any future donor retirement that
has ever been active during real play needs a save-content check too (see
`rimworld-savegame` skill's distinction: "Could not resolve cross-reference" = def
loader/mod-stack problem; "Could not load reference to" = Scribe/save problem, no mod
change fixes it).

## verify
```
PROVE   grep the canonical save's XML (rimworld-savegame skill tooling) for any
        Lumi-authored door defName actually placed on the map/world, not just
        referenced in a roster/history list
EXPECT  either zero placed instances (safe to re-attempt retirement, this time also
        checking the save) or a nonzero list of thing IDs/positions needing a real fix
LIES    "the mod-dependency check passed" is not evidence about the save; only reading
        the save's own Scribe data settles this
```

## criteria
Either (a) the placed Lumi door(s) in the canonical save are migrated to a surviving
ThingDef (ours or `jecrell.doorsexpanded`'s) via a save edit, and `lumi.doorsexpanded`
is retired for real with a clean load proof, or (b) the owner rules this one donor stays
permanently (the save is worth more than the retirement), and `STARWARS_DONOR_SUNSET_1`'s
Wave 4 status is corrected to reflect that. Either way, `STARWARS_DONOR_SUNSET_1`'s own
record should stop claiming Wave 4 is done until one of these actually happens.
