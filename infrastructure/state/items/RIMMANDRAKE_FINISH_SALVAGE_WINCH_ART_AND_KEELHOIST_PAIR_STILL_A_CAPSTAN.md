# RIMMANDRAKE_FINISH_SALVAGE_WINCH_ART_AND_KEELHOIST_PAIR_STILL_A_CAPSTAN

Remainder of `SHIP_TOW_LINE_1` (X-13/CB-9 in `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`). The winch
works: on 2026-11-26 the `salvage_winch_reel` chain (CreatureBehaviors) read 2/2 PASS on ArchBig. Two parts of X-13 are
still owed. Its A3 text named both of them.

## spec

1. The salvage winch (`src/RimMandrake/TheSump/Defs/ThingDefs_Buildings/RM_SalvageWinch.xml`) gets its own sprite. Today
   it reuses `Things/Building/CapstanTurret/RM_CapstanTurret_Base` (PROVISIONAL). The art goes in through `art install`,
   and an art judge rules on it (`design/RimMandrake/art_judge_brief.md`).
2. X-13 says the tow line "pairs with KeelHoist's vertical cargo lift". Nothing says what the pairing is. The Designer
   first writes what a player sees (for example, a reeled wreck that arrives beside a KeelHoist is lifted aboard), then
   it is built. If the Designer finds no player value, drop part 2 with that reason.

## criteria

- A1 L0: RM_SalvageWinch.xml names its own texture, not the capstan base (the item's effect check).
- A2 L2: live, a placed winch shows its own sprite; the art judge passed it.

## verify

- A1: `path-lacks:src/RimMandrake/TheSump/Defs/ThingDefs_Buildings/RM_SalvageWinch.xml::CapstanTurret/RM_CapstanTurret_Base`.
- A2: a capture of a placed winch, judged by the art judge; the art ledger records the install.

## refs

file: src/RimMandrake/TheSump/Defs/ThingDefs_Buildings/RM_SalvageWinch.xml
