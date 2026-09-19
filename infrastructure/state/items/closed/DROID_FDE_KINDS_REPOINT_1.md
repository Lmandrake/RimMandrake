# DROID_FDE_KINDS_REPOINT_1

## Spec
Repoint the 4 `Jawa_Droid_*` FDE (Free Droid Enclaves) PawnKindDefs, and any FDE
droid backstories keyed on the old donor races, onto Droidworks races — per
`design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §5 row C2. Fix the
GENERATOR (`src/RimMandrake/Utils/gen_pawnkind_roster.py`), never the emitted
`JawaFactionRoster.xml` by hand.

## What was wrong about the earlier block
Blocked 2026-09-07 08:44 with reason "no instantiable derived race anywhere in
`src/RimStarWars/Droidworks/`" — false. That check only read `Races_Base.xml`
and `Races_Families.xml` (the `Abstract="True"` scaffolding) and missed the
three files holding 57 concrete races: `Races_OuterRim.xml` (19), `Races_KotOR.xml`
(22), `Races_JDS.xml` (16). Unblocked 2026-09-08 19:14 after verifying `grep -c
'Abstract="True"'` on those three files returns 0, and after spawning/live-testing
several of these exact races this session (`RSW_DW_Race_OuterRim_ProtocolDroid`,
`RSW_DW_Race_OuterRim_BattleDroid`, `RSW_DW_Race_OuterRim_GNKDroid`).

## Built
`src/RimMandrake/Utils/gen_pawnkind_roster.py` — the `RACES` dict (was `DROID_RACES
_APPLIED_TO_KINDS_1`'s table) repointed from the OuterRim Droid Depot donor races
to Droidworks' 1:1 absorbed equivalents:

| kind | old race | new race |
|---|---|---|
| `Jawa_Droid_Grunt` | `OuterRim_ImperialLaborDroid` | `RSW_DW_Race_OuterRim_ImperialLaborDroid` |
| `Jawa_Droid_Heavy` | `OuterRim_KXSecurityDroid` | `RSW_DW_Race_OuterRim_KXSecurityDroid` |
| `Jawa_Droid_Specialist` | `OuterRim_ProtocolDroid` | `RSW_DW_Race_OuterRim_ProtocolDroid` |
| `Jawa_Droid_Leader` | `OuterRim_SuperTacticalDroid` | `RSW_DW_Race_OuterRim_SuperTacticalDroid` |

Each new race was confirmed present and non-Abstract in `Races_OuterRim.xml`
before use (`grep -n "<defName>RSW_DW_Race_OuterRim_<X></defName>"`, all 4 hit).

`MayRequire="Neronix17.OuterRim.DroidDepot"` was left UNCHANGED on all 4
`PawnKindDef`s and on the matching guard in `JawaFreeDroidEnclaves.xml` — the
Droidworks absorbed races still ship their texture set under
`Textures/OuterRim/Droid/...` and the design doc's own verify line for this item
is "generator diff = 4 race lines"; retiring the Depot dependency is
`DROID_RETIRE_DEPOT_ASIMOV_1` (D4)'s job, downstream of this one, not this
item's.

Then re-ran the generator and diffed:
```
python3 src/RimMandrake/Utils/gen_pawnkind_roster.py
git diff --stat src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/JawaFactionRoster.xml
```
`1 file changed, 4 insertions(+), 4 deletions(-)` — exactly the 4 `<race>` lines,
nothing else moved (no reordering, no whitespace drift).

## Backstories — second half of the title
Searched `src/RimUtinni/PawnFlavor/` (`Backstories_FDE_Droids.xml`,
`FactionBackstoryWiring.xml`) and grepped the whole `src/RimUtinni/` tree for the
4 donor race defNames. **Nothing needed changing**: every FDE droid backstory
(`RUT_Jawa_CongregationConsecrated`, `RUT_Jawa_CathedralWhispered`,
`RUT_Jawa_CathedralMason`, `RUT_Jawa_ColdForged`, `RUT_Jawa_PipeKeeper`,
`RUT_Jawa_DirtyBurner`) keys exclusively on `spawnCategories`
(`JawaBSC_FDECathedral` / `JawaBSC_FDENightside`), wired onto the 4
`Jawa_Droid_*` kinds via `backstoryFilters` in `JawaFactionRoster.xml` and onto
`Jawa_FreeDroidEnclaves`'s `FactionDef` in `FactionBackstoryWiring.xml`. None of
it names a race defName anywhere, so nothing needed repointing.

**Adjacent, explicitly out of scope, left untouched**: `JawaFreeDroidEnclaves.xml`
lines 184/187 name `OuterRim_ProtocolDroid`/`OuterRim_KXSecurityDroid` directly —
these are Outer Rim's OWN `Trader`-group `traders`/`guards` `PawnKindDef` entries
(not our 4 `Jawa_Droid_*` kinds, not a race, not a backstory), unrelated to this
item's title. Flagging for whoever picks up the design doc's D4/D2 rows rather
than guessing a Droidworks substitute here.

## Verify
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/JawaFactionRoster.xml')"` — well-formed.
- `validate_patch.py` against the live def dump (2026-09-08T16:42:55Z capture,
  600 mods, `mandrake.rsw.droidworks` and `neronix17.outerrim.droiddepot` both
  active) both with `--live` alone and with `--defs <Mods dir + Workshop> --live
  <dump>`: **`OK - 0 errors, 0 warning(s)`** both times, matching the design
  doc's own verify line ("validate 0/0").
- **Offline-only.** Did not deploy or take the bridge — another FOUNDRY window is
  driving a full-list cold-load restart this session. Live coexistence check
  (do the 4 kinds actually spawn wearing the DW race in a running FDE faction,
  raid, or settlement) is a follow-up for whoever next drives the bridge with
  Droidworks + the FDE faction active — not blocking this close, since the
  design doc's stated verify criterion is generator-diff-shape + validate 0/0,
  both offline checks, both satisfied.

## Assumptions recorded
- `MayRequire` stays on `Neronix17.OuterRim.DroidDepot` for now (see Built,
  above) — a deliberate reading of "generator diff = 4 race lines", not an
  oversight.
- The Outer Rim `Trader`/`guards` entries in `JawaFreeDroidEnclaves.xml` are
  out of scope for this item (see Backstories section).
