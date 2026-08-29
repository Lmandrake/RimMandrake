# EMPIRE_WHITELIST_OVERRIDDEN_1 — Empire's permanentEnemyToEveryoneExcept still whitelists the player

Split from `EMPIRE_RAID_QUICKTEST_1`, 2026-08-29. Full evidence there; summary here.

## spec
`GalacticEmpire.xml`'s `PatchOperationReplace` on
`/Defs/FactionDef[defName="Empire"]/permanentEnemyToEveryoneExcept` deliberately DROPS
`PlayerColony`/`PlayerTribe` from the exception list (the comment names this as the entire
mechanism that keeps Empire hostile). Live, `jawa/get_defs FactionDef/Empire
permanentEnemyToEveryoneExcept` (584-mod set, `OFFICIAL-2026-08-29`) returns 24 entries
INCLUDING `PlayerColony` and `PlayerTribe`, plus a dozen other mods' player-faction defNames
never mentioned in our patch. `validate_patch.py --live` confirms our own patch's xpath
matches correctly (every operation: `1 match(es)`), so this is not our patch failing to fire —
something else, loading after `mandrake.jawa.patches` (ModsConfig line 585), re-adds the
excluded entries.

## verify
The mechanism (which mod's patch runs last and wins) has never been observed — this needs a
live read, not an offline guess: either bisect the mod list, or (cheaper) read the exact
in-memory patch application order the game logs for this xpath, or grep the full Workshop
folder for `permanentEnemyToEveryoneExcept` patches that explicitly touch `Empire` (the initial
grep found 30+ mods touching the FIELD generically across many factions — narrow to the ones
naming Empire specifically).

## criteria
- [ ] The interloping mod/patch named.
- [ ] A fix decided: reorder load (About.xml loadAfter), patch the interloper's own operation,
      or convert our operation to run later/win explicitly — owner's call once the mod is named.
- [ ] Live re-check: `jawa/get_defs FactionDef/Empire permanentEnemyToEveryoneExcept` excludes
      PlayerColony/PlayerTribe, and a fresh relation seed shows Empire Hostile to the player.
