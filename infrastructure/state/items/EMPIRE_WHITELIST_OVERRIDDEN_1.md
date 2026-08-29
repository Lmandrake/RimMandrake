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

## 2026-08-29 (FOUNDRY): correction to my own earlier reasoning, and 69 candidates cleared

🔴 **`validate_patch.py`'s "1 match(es)" does NOT prove our patch wins — corrected.** It
confirms the xpath is well-formed and matches a real node in the RAW, unpatched
`Royalty: Faction_Empire.xml` (an xpath-validity check), not that our `Replace` is the LAST
write in the full 584-mod patch application order. I read this as "our patch fires and is
final" earlier; it only proves the first half. Deployment was also checked and is not the
answer: `diff` between `src/Jawa/Jawa_Patches/Patches/GalacticEmpire.xml` and the deployed
copy under `Mods/Jawa_Patches/Patches/` is byte-identical.

**Exhaustively grepped 101 mods touching `permanentEnemyToEveryoneExcept` anywhere in the
1256-mod Workshop folder** → 69 of those also mention "Empire" → **zero of the 69 contain the
literal string `PlayerColony` or `PlayerTribe`.** The two most plausibly-named suspects by
filename (`empirehostileptach.xml`, `Patch_EmpireGoodwill.xml`) were read in full: both only
`PatchOperationAdd` a SINGLE unrelated defName each (`pphhyy_Demigryph_DemigryphKnights` and
`PlayerColonyBoS`/`PlayerColonyEnc` respectively) — neither touches vanilla `PlayerColony`/
`PlayerTribe` at all, and an Add cannot un-remove what a later Replace removed regardless.

**No XML file in any active mod contains the two specific strings that are reappearing.** This
rules out a straightforward "mod B's patch runs after mod A's and wins" explanation entirely.
The remaining live entries — `BS_PlayerColonyXenoPlus`, `VFEI2_PlayerOutpost`, `AM_PlayerColony`,
`VFEP_PlayerPirate`, `OuterRim_RogueDroidColony`, `OuterRim_EmpirePlayerFaction`,
`OuterRim_RebelPlayerFaction`, etc. — have the SHAPE of a compatibility FRAMEWORK
programmatically appending every active alternate-start mod's player-faction def to every
`permanentEnemy`/`permanentEnemyToEveryoneExcept`-carrying `FactionDef` via C# (likely a
`[StaticConstructorOnStartup]` pass, not XML), which would also explain vanilla `PlayerColony`/
`PlayerTribe` being restored if that same pass treats "the vanilla player factions" as always-
implied rather than reading them off our patched list. **Not confirmed — hypothesis only.**

## verify
Needs either (a) a live Harmony patch inventory naming what runs on `FactionDef`/`Faction`
post-load (the same capability gap `WILD_ANIMALS_PADDED_LISTS_1` needs — no bridge tool exists
for this yet, and building one needs a game-down deploy window), or (b) a bisect: swap to the
13-mod minimal list plus Jawa_Patches plus Outer Rim only, re-check
`permanentEnemyToEveryoneExcept`, then add back mod groups until it reappears.

## criteria
- [ ] The interloping mechanism named — narrowed to "likely a C# compatibility framework, not
      an XML patch" but not confirmed or named.
- [ ] A fix decided: reorder load, patch the interloper, or make Jawa's own hostility check
      NOT rely on `permanentEnemyToEveryoneExcept` at all (e.g. seed the relation directly via
      a companion tool or scenario part at world-gen) — owner's call once the mechanism is named.
- [ ] Live re-check: `jawa/get_defs FactionDef/Empire permanentEnemyToEveryoneExcept` excludes
      PlayerColony/PlayerTribe, and a fresh relation seed shows Empire Hostile to the player.
