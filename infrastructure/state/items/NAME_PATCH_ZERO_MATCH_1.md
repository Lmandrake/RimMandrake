# NAME_PATCH_ZERO_MATCH_1 — gen_name_patch.py matches 0 of the doc's 41 rows against either cast

## Found while resolving `ROSTERS_TO_CAST_BIOMECAST_DEFS_STALE_1`, 2026-09-20 FOUNDRY

While verifying `cast_assignment.csv`'s downstream consumers before regenerating it for
real, `design/Jawa/fauna/gen_name_patch.py` was run (dry, before any commit) against the
newly-corrected CSV. It reported **0 renames**, 41 of 41
`design/Jawa/worldbuilding/creature_names_ashkarr.md` rows unmatched — a wipe of the
shipped 37-rename patch (`design/Jawa/fauna/CreatureNames_Ashkarr.xml`, last written at
`c4a50c968`, "37 creature renames ship wrapped").

**Not caused by the biome-name fix.** Re-run against the OLD (pre-fix, still
pre-migration-named) `cast_assignment.csv` from `HEAD` — **also 0 matches, 41
unmatched**. The doc's label keys (`Andrewsarchus`, `Castoroides`, `smilodon`,
`woolly mammoth`, …) don't match ANY row in the cast today, old CSV or new. This is a
pre-existing drift between `creature_names_ashkarr.md` and whatever cast content
actually produced the shipped 37-rename patch — unrelated to biome defNames.

The accidental overwrite from testing this was reverted (`git checkout --
design/Jawa/fauna/CreatureNames_Ashkarr.xml`); the shipped 37-rename patch is untouched
on disk and in the deployed mod.

## Resolved 2026-09-20 (FOUNDRY) — not a defect, root cause found

**`gen_name_patch.py`'s matching logic is correct.** All 41 of the doc's rows are
verified to be exclusively Jurassic Rimworld (22 rows: Protovermes…Torosaurus) and
Megafauna (19 rows: castoroides…titanoboa) creatures — no other mod is represented in
`creature_names_ashkarr.md` at all. Both donor mods were **retired from the active mod
list**, per the owner's dinosaur/mod-retirement ruling
(`design/Jawa/worldbuilding/creature_recognizability_rule.md` §6, ruled 2026-09-05):

- `mlie.jurassicrimworlddinosaursonly` — deactivated 2026-09-13, executing that ruling
  (`infrastructure/state/items/MODLIST_RULED_CUTS_1.md`; 5 survivors already absorbed
  into `mandrake.rsw.swbestiary` as `RSW_Absorbed_*`).
- Megafauna — likewise ruled retired 2026-09-05 ("retire, cleanup only" —
  `creature_recognizability_rule.md` §6 correction table).

MEASURED against the live game: neither packageId appears anywhere in the current
617-entry `ModsConfig.xml` (checked by parsing `activeMods`, not a text grep), and
neither mod's creatures appear in `cast_assignment.csv` (419 rows, `rosters_to_cast.py`'s
hand-authored-roster regime since `BIOME_FAUNA_ASSIGNMENT_SITTING_1`). So **0 renames is
the objectively correct output**: there is nothing left in the game to rename. The
41-row doc and the shipped 37-rename `CreatureNames_Ashkarr.xml` describe content that
no longer exists in the mod list — not a stale join, not a broken matching key, not
caused by the biome-name-join fix chain this was found investigating.

No code change needed. `CreatureNames_Ashkarr.xml`'s 37 `PatchOperationConditional`
ops are harmlessly inert now (their defNames' donor mods are gone, so the guard never
matches) — cleanup of that dead patch, if wanted, belongs with the broader Megafauna/
Jurassic retirement cleanup already named in `creature_recognizability_rule.md` §6's
correction table, not this item.

Added a short pointer to `gen_name_patch.py`'s own "NOT missing defs" print (a third,
now-measured cause: the row's donor mod was formally retired) so a future 0-match run
is diagnosed faster.
