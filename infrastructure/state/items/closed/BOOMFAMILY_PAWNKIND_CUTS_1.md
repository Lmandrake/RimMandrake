## spec
`BOOM_FAMILY_CUT_1` (2026-09-10) Cherry-Picker-cut ThingDefs for the 15-creature
boom family but left the matching PawnKindDef cuts unadded — discovered by
`BOOMALOPE_CUT_EVERYWHERE_1` (2026-09-14), which added the missing
`PawnKindDef/Boomalope` itself and flagged the other 14 as "a different
creature set under a closed item." This item closes that gap for the
remaining creatures, offline only.

## done
Added `PawnKindDef/<name>` as a typed Cherry Picker cut, immediately after
each creature's existing `ThingDef/<name>` line, to both files —
`deployed/config/v1_freeze/Mod_3521312241_Mod_CherryPicker.xml` (ratified
anchor) and `infrastructure/state/cherrypicker/CherryPicker.SHIP.xml` (ship
profile) — exact same format as the Boomalope entry added in commit
5087c0f19. 13 creatures cut:

`Boomrat`, `VFEI2_Boomtick`, `GR_Bearalope`, `GR_Boomabear`, `GR_Boomalisk`,
`GR_Boombeetle`, `GR_Boomcat`, `GR_Boomffalo`, `GR_Boomsquirrel`,
`GR_Chickenlope`, `GR_Manalope`, `GR_ParagonBoomalope`, `GR_Squirralope`.

Each PawnKindDef defName verified to match its ThingDef defName exactly, off
the same donor mod source used by `BOOM_FAMILY_CUT_1`: `Boomrat` (Core,
vanilla convention), `VFEI2_Boomtick` (VFE Insectoids 2 — `vendor/mod_sources/
VFE-Insectoids2-main/1.6/Defs/ThingDefs_Races/Races_Boomtick.xml:5,80`), the
11 `GR_*` names (Vanilla Genetics Expanded — `vendor/mod_sources/
VanillaGeneticsExpanded_src/1.6/...`, each defName appearing exactly twice,
ThingDef then PawnKindDef, same pattern already documented for `GR_Boomsnake`/
`GR_Mantistanis` in `WildAnimals_Pyrelands.xml`'s own header).

**EXCLUDED: `GR_Boomsnake`** — per the owner's task brief, no new cut added
for it while its disposition is under investigation (see
`BOOMSNAKE_CUT_CONFLICT_1`). Its `ThingDef/GR_Boomsnake` cut (already present
from `BOOM_FAMILY_CUT_1`) is untouched by this item.

Both files verified identical at the touched region, well-formed XML
(`xml.etree.ElementTree` parse, no errors).

## fallout check (rimworld-content-moderation, post-cut)
Grepped `src/` and `design/` for each of the 13 names. All `src/` XML hits are
either (a) Core `SoundDef` reuse (`Pawn_Boomrat_Wounded` etc. — a different,
uncut def, common modding reuse) or (b) Boomrat texture-folder reuse in
`RSW_Absorbed_Protovermes.xml`/`RSW_Borcatu.xml` (art asset path, not the
ThingDef/PawnKindDef itself) — both already assessed as fine by
`BOOM_FAMILY_CUT_1`'s own pass, unaffected by adding the PawnKindDef cut. No
live `PawnGroupMaker`, scenario, or quest reference found for any of the 13.

All `design/Jawa/worldbuilding/biomes/rosters/*.json` hits for the 13 names
are `"disposition": "homeless-reserve"` (already evicted) — **except one real
fallout hit, fixed**: `the_scarlands.json` still carried `VFEI2_Boomtick` as
an active `"action": "keep"` fauna row (commonality 0.4) four days after its
ThingDef cut and its live `RUT_Scarlands.xml`/`BiomeCast_Ashkarr.xml` removal
— the identical stale-roster-row landmine already fixed for Boomalope and
Boomsnake this session. Moved to `evictions` with
`"disposition": "cut:BOOM_FAMILY_CUT_1 (BOOMFAMILY_PAWNKIND_CUTS_1,
2026-09-14)"`; no live XML referenced it (confirmed clean before the fix), so
no game-facing regression, just a stale design doc corrected.

`_global.json`'s derived home-index (`"derived": "2026-09-10"`, e.g.
`"Boomrat": ["the_contagion"]`) still lists several of these names against
biomes where the live roster already shows them `homeless-reserve` — a stale
snapshot frozen at 2026-09-10, same class as the already-noted stale
`UBIQUITY_25` `Boomalope` entry (`BOOMALOPE_CUT_EVERYWHERE_1`'s "checked, no
action needed"); not touched, consistent with that precedent.

## verify
`python3 -c "import xml.etree.ElementTree as ET; ET.parse(...)"` on both
Cherry Picker files → both parse. `grep` diff of the touched region in both
files → identical. A `cherrypicker.py --source live --is-cut PawnKindDef/<name>`
readback is owed on the next deploy-authorized/bridge session (offline this
pass, per FOUNDRY scope) — same as `BOOMALOPE_CUT_EVERYWHERE_1`'s own open
verify line.
