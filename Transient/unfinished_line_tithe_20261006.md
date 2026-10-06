# UNFINISHED_LINE_TITHE_BEAT_1 — beat 4 "The Tithe and the Hands" (2026-10-06, FOUNDRY helper, offline)

## Reading (done)
- Spec §2.4: not a rite. Tithe (plasteel 300 / components 40 / steel 800 / uranium 60 at 1x) + lend one Crafting >= 8 colonist 10 days; death -10 both; 20-day deadline; reward Crafting XP, line assembled -> beat 5.
- Site choice (UNFINISHED_LINE_SITE_CHOICE_1) still blocked: beats 3/5 stand in with "at your colony". Beat 4 follows suit.

## Shape chosen
- ONE Enclave-sent shuttle (vanilla Util_TransportShip_Pickup, Script_PawnLend's pattern) whose requiredItems is the tithe basket and requireColonistCount 1.
- Crafting >= N enforced by a Harmony postfix on CompShuttle.IsAllowed (covers load dialog, float menu, enter job), scoped to this beat's shuttle only.
- Lend via QuestPart_LendColonistsToFaction built by a small node (the vanilla node needs a Pawn asker).

## Built (uncommitted)
- `RUT_UnfinishedLine_4_Tithe` on the spine between 3 and 5; HistoryEventDef `RUT_LineHandsLost`.
- `Source/UnfinishedLineTithe.cs` (+csproj Compile, Harmony ref): TitheSetup, TitheShuttleGate, LineHands (lend part + Crafting XP), CompShuttle.IsAllowed postfix, `UnfinishedLineTitheProof.ProofTitheSetup`.
- Mod Settings: titheScale 1.0 (0.25-3), titheDeadlineDays 20, lendDays 10, lendSkillGateEnabled on, lendMinCrafting 8, lendCraftingXp 6000. All PROVISIONAL.
- About.xml: Harmony dependency; stale "only beats 1-2 built" description corrected.
- validation.py: beat 4 static checks (sanity-probed: a mutated HandsLost End is caught) + live `tithe` chain, toggle lendSkillGateEnabled.
- No art needed (vanilla shuttle).

## Validation
- validate_quest.py: 6 defs, 0 errors (beat-4 warnings are C#-stored slate vars, same class as beat 5's).
- validation.py STATIC PASS; validate_patch.py 0 errors; winbuild.py UnfinishedLine: 0 warnings 0 errors.
- NOT run live.

## Deferred / open
- Site-dependent delivery (caravan TradeRequests A/C/D, monument B) waits on UNFINISHED_LINE_SITE_CHOICE_1.
- Tithe scales by the setting only, not colony wealth (design said "scaled to wealth").
- The shuttle is vanilla's Imperial shuttle graphic, flown under the Enclaves' faction.
- Lend goes to the Hive (Enclaves while the Hive is hostile): a judgement call.

