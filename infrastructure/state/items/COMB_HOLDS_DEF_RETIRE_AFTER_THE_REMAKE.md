# COMB_HOLDS_DEF_RETIRE_AFTER_THE_REMAKE

`RM_Faction_CombHolds` (the "Tallmere Combs") was banned by the owner on 2026-10-20: *"We don't want those"*. The def
is kept only as a tombstone, because it is loadID 9 in every `ASHKARR_DEV_*` save. If the def were deleted while a
save still holds the faction, `FactionManager.ExposeData` would drop it with "Some factions were null after loading",
and every other faction would keep a relation pointing at it.

## spec

**Gate:** delete the def only once `python3 src/RimMandrake/Utils/banned_factions.py check-save <save>` reports
`ABSENT RM_Faction_CombHolds` on every save we keep. That means after the world re-make; old dev saves can be
deleted or kept unloaded.

**Delete** from `src/RimMandrake/LeaningScrub/Defs/FactionDefs/RM_CombHolds.xml`:
- the FactionDef;
- `RM_Comber`, `RM_CombWarden` and `RM_CombTrader`;
- `RM_NamerFaction_CombHolds` and `RM_NamerSettlement_CombHolds`;
- the file itself, if nothing else is left in it.

**Then:**
- In `src/RimMandrake/Utils/factions/banned_factions.json`, set its disposition to `supplier_cut` and remove its
  `own_def_file` and that file's allowlist row.
- Fix the stale camp comment in `src/RimMandrake/LeaningScrub/Source/RM_ScrubInjections.cs`, line 22. Comment
  only: it rebuilds the DLL and its `.srchash`.
- Run `selftest_banned_factions.py` and the LeaningScrub selftests.

Design: `design/RimMandrake/factions_unwanted_and_lingering_2026-10-20.md` §5.
