# JUDGE — CATHEDRAL_MISSION_BOON_OFFERS_1 (blind, 2026-11-11)

Read: STATEMENT.md, NOTES.md, every file in evidence/ (no images exist), the two shipped def files
(src/RimUtinni/CathedralPass/Defs/QuestScriptDefs/RUT_CathedralAssailantMissions.xml,
.../IncidentDefs/RUT_CathedralFavours.xml), the offer gate in gm_blackboard_shadow.py (compute_cathedral_offer_gate,
advance_cathedral_offers) and the C# string literals in CathedralFavours.cs. DONE.md / BROADEN.md not read.

Reruns at 12b1764649 (logs in /tmp):
- selftest_rustcathedral_offers.py: 87/87, exit 0. Matches evidence/selftest_offers.txt line for line (only tmp paths differ).
- gm_blackboard_shadow.py on the ordinary-play fixture: exit 0, 300 polls, same final line as the evidence (Regard 86.15,
  8 requests, 5 completed, 3 gifts). cathedral_offer_letters.py on it: identical to evidence/letters_ordinary_play.txt.
- cathedral_arc_lint.py --xml (both def files) at --stage 1 and --stage 2: 38 strings, PASS, exit 0.
- validation.py (static, offline): STATIC PASS, exit 0.
- My own read of the 300-record log: would_fire types by stage show no cathedral_mission_offer at WARY and no
  cathedral_boon_offer at TOLERATED (the counter does see these types: 5 mission offers at TOLERATED, 3 boon offers at VOUCHED).

## Lines

1. Offer appears only at the correct stage — TRUE. Selftest [1] drives the fixture WARY -> TOLERATED -> VOUCHED and prints
   each poll's offer set: WARY polls are missions False (stage_below_TOLERATED) with both boons closed_stage; TOLERATED offers
   missions with boons closed_stage on every poll; boons open from VOUCHED (poll 168). My log census agrees. The gate
   reads conduct_posture >= TOLERATED / >= VOUCHED; a reveal flag alone opens nothing (pinned).
2. Never attributed to the Cathedral before stage 3 — TRUE. Lint on the shipped files exits 0 at stages -1, 1 and 2 (rerun
   by me at 1 and 2); planted lines are refused with exit 1 (names-the-place, agency, §GM truth). The selftest lints the
   inherited, resolved strings (46) and the C# progress line. I also read every string: none names the place, an asker
   behind the enclaves, or the Assailant. Note: the linter is word-pattern only (a paraphrase walks past it, filed as
   RIMMANDRAKE_HARDEN_ARC_LINT_PARAPHRASE_WALKS_PAST); the criterion is the linter, and my own read found no paraphrased
   attribution either.
3. Boon availability flips with a shadow Heat change — TRUE. Selftest [3] paired runs: poll 18, VOUCHED in both; calm run
   Heat 0 -> gravcore offered; hot run (two kyber sold poll 16) Heat 10.11 > ceiling 5 -> withheld_heat, stage never leaves
   VOUCHED, and the gravcore reopens when Heat cools (poll 31). Synthetic Heat 45 withholds both boons. Ceiling edge
   (== open, +1e-6 withheld) pinned.
4. The dark flip closes both — TRUE. Selftest [4] poll 10: go_dark fired, missions closed (go_dark), the posted request
   withdrawn, both boons closed_go_dark, nothing offered; 10-day hold with no offer though posture re-climbs.
5. Every beat completes Oracle-absent — TRUE (offline scope). oracle_absent_run.txt: PATH resolves no `claude`, fixture run
   exits 0, 11/11 offers carry full def text; no subprocess/Popen/claude in the blackboard or CathedralFavours.cs. All
   text ships in the defs. The in-game quest run itself is part of line 8's live step.
6. K2: completions scrub zero Heat — TRUE. Selftest [6]: 6 completions, Heat identical poll for poll to the ignoring run,
   including one completion at Heat 10.66 (moves only by the 0.4/poll decay both runs share). The only Heat write in the
   blackboard is decay + sale heat (gm_blackboard_shadow.py:982).
7. Regard feedback in shadow logs — TRUE. My rerun's log, poll 56: mission_completions_this_poll=1,
   mission_completion_regard_gain_this_poll=4.0, Regard delta 4.3 vs 0.3 on the polls either side, Heat 0 unchanged.
8. Live end to end on a quicktest — TRUE for what this lane owes; the live run itself has not happened and is owed.
   Offline owed: winbuild of CathedralPass succeeded (0 warnings/errors); validate_patch.py against the game's def set
   0 errors; validation.py static PASS (rerun); the exact recipe is in validation.py and quoted in live_run_recipe.txt,
   with what it does not prove named. Ledger: CLAUDE_ARCHMAGI_OFFLINE3 noted the handoff (04:44:21Z) and set needs=bridge
   (04:44:26Z). Factual correction to the brief: the last event is an OWNER reassign to RELENTLESS (04:48:06Z, per-ruling
   CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM), not BENCH. That follows the standing ruling (Relentless builds; BENCH takes
   only needs=owner looks), so the statement's "BENCH" is out of date. It is not a defect in the work.
   infrastructure/state/queue/BENCH.md (last committed 2026-10-02) is a stale projection; I did not rely on it.

## Staging / flattery notes
- All evidence comes from offline, fixture-driven shadow runs. No screenshot exists and none is claimed. The quest tab look,
  pack spawn on accept, PackDown reaching EndedSuccess, and the gift landing on a gravship map are explicitly owed to the
  live run (the recipe's NOT PROVEN list says so).
- The Heat flip uses a scripted two-kyber sale. It is not cherry-picked: the paired runs share every other input, and a
  separate test checks the live 2000-tick cadence (the 3-day quiet window keeps the gravcore from coming back hours after a sale).
- Oracle-absent is close to true by construction (the path has no LLM call). The PATH test plus the source grep is enough.
- Hygiene, not substance: the working tree holds an uncommitted rebuilt CathedralPass DLL + .srchash. The source hashes
  are identical to the committed stamp; only the DLL hash differs (the build is not deterministic).

would show: yes
