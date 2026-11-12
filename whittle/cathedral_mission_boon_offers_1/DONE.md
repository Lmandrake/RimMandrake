# Done claim

- true: **Offer appears only at the correct stage.** Assailant mission offers appear at TOLERATED (stage 1) | evidence: `whittle/cathedral_mission_boon_offers_1/evidence/selftest_offers.txt` `whittle/cathedral_mission_boon_offers_1/evidence/shadow_log_ordinary_play.jsonl` `whittle/cathedral_mission_boon_offers_1/evidence/letters_ordinary_play.txt`
- true: **Never attributed to the Cathedral before stage 3.** Every quest-giver / letter string for the | evidence: `whittle/cathedral_mission_boon_offers_1/evidence/lint_runs.txt` `whittle/cathedral_mission_boon_offers_1/evidence/selftest_offers.txt`
- true: **Boon availability flips with a shadow-mode Heat change.** At VOUCHED, a boon is offered when | evidence: `whittle/cathedral_mission_boon_offers_1/evidence/selftest_offers.txt` `whittle/cathedral_mission_boon_offers_1/evidence/letters_ordinary_play.txt`
- true: **The dark flip closes both.** A go-dark flip (§6.1) closes missions and boons. Evidence: selftest | evidence: `whittle/cathedral_mission_boon_offers_1/evidence/selftest_offers.txt`
- true: **Every beat completes Oracle-absent.** Fallback (prescribed) text ships for every mission and boon | evidence: `whittle/cathedral_mission_boon_offers_1/evidence/oracle_absent_run.txt` `whittle/cathedral_mission_boon_offers_1/evidence/selftest_offers.txt` `whittle/cathedral_mission_boon_offers_1/evidence/build_and_validate.txt`
- true: **K2 anti-laundering: completing missions scrubs zero Heat.** Evidence: selftest row, Heat before and | evidence: `whittle/cathedral_mission_boon_offers_1/evidence/selftest_offers.txt`
- true: **Regard feedback observed in shadow logs.** A completed mission feeds Regard (item 1 input). | evidence: `whittle/cathedral_mission_boon_offers_1/evidence/shadow_log_ordinary_play.jsonl` `whittle/cathedral_mission_boon_offers_1/evidence/selftest_offers.txt` `whittle/cathedral_mission_boon_offers_1/evidence/letters_ordinary_play.txt`
- true: **≥1 Assailant mission shape + the boon-offer gate live end to end on a quicktest.** LIVE step, not | evidence: `whittle/cathedral_mission_boon_offers_1/evidence/build_and_validate.txt` `whittle/cathedral_mission_boon_offers_1/evidence/live_run_recipe.txt`

## What I'm least sure about
- **The quest mechanics have never run in a game.** `RUT_QuestPart_PackDown` (C#) replaces vanilla `QuestNode_PawnsKilled`
  to close a real exploit (a killed tame animal of the pack's race would have finished the mission). It is built and
  reviewed against the decompiled 1.6 source, but no game has loaded it. The live recipe's first check is exactly that
  exploit (`whittle/cathedral_mission_boon_offers_1/evidence/live_run_recipe.txt`, step 3).
- **The last bullet's verdict covers the offline half only.** By the statement's own wording, the live quicktest
  belongs to a live loop. What is true here: the defs and C# are built and validated, the recipe is written, and the
  item is noted and set needs=bridge. It is still claimed by this seat until the wrap-up hands it to BENCH.
- **Ordinary play is a fixture with a simulated player** (`src/RimMandrake/Utils/fixtures/cathedral_offers_ordinary_play.json`).
  Its quest rows are marked `simulated`, and it stands in for a live firer that does not exist yet. Its go-dark uses
  the existing demo hooks (a pursuit event and a lowered threshold), because no live pursuit signal exists. Heat in
  the high band (40 or more) at VOUCHED is shown with a heat value set directly on the board; that row is labelled
  SYNTHETIC. A kyber sale large enough to reach it would cost more Regard than VOUCHED holds.
- **Tuning numbers are mine** (GM tuning, not owner-ruled): heat ceilings 15/5, re-offer intervals of 15/45 days, a
  5-day gap between requests, a 10-day hold after go-dark, and no gift within 2 days of a completion. The dark hold
  is my reading of §6.1 ("it hides from the player again"). Without it, item 1's stage machine re-climbs and reopens
  the favours within about 1.5 days of a go-dark.
- **The success letters repeat word for word.** There is one per channel. Inline variants are not possible through
  `QuestNode_Letter`'s `SlateRef<RulePack>`. The six request descriptions are distinct and cycle before any repeats.
- **The Utinni is named as a channel.** The spec itself says "the Utinni insists"; she is the player's ship, not the
  patron. The patron is never named.

## What I did not test
- Nothing in a live game. That covers: the quest window (does it show any giver?), the manhunter pack spawning on
  accept, PackDown completing or failing, the gift landing at TradeDropSpot on a gravship map,
  `storyteller_fire`'s refusal on the old World target (I read that in source, I did not see it), and Player.log after
  a load.
- Save/reload, and restarting the blackboard mid-campaign. I reasoned about these in BROADEN.md but did not run them.
  A restart resets gift cooldowns.
- Two colonies, or the ship away from home.
- The JawaBench `root` field built cleanly but was not deployed. Without it, the blackboard falls back to
  case-insensitive name matching; the selftest covers that fallback offline.
