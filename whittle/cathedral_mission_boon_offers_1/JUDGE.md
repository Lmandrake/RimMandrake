# Judge: CATHEDRAL_MISSION_BOON_OFFERS_1

Blind judge, 2026-11-11, clone claude-archmagi-offline3 at 2e1dae4dd7 (the only dirty files are under whittle/ and conversations/; no src file is dirty).
I did not read DONE.md or BROADEN.md. I re-ran the work into /tmp:
- `selftest_rustcathedral_offers.py`: 87/87 ok, exit 0 (/tmp/judge_selftest.txt). It matches evidence/selftest_offers.txt.
- the ordinary-play fixture shadow run (fresh log /tmp/judge_shadow2.jsonl): exit 0, and all 300 records are identical to evidence/shadow_log_ordinary_play.jsonl.
- `cathedral_arc_lint.py --xml` on both shipped def files at stages -1, 1 and 2: 38 strings, PASS, exit 0. The planted "The Cathedral asks..." line gives FAIL with exit 1.
- my own tally of the evidence log by posture, and a read of the gate code (`compute_cathedral_offer_gate`) and the Heat update (gm_blackboard_shadow.py:982).

## Lines

1. **Offer appears only at the correct stage: TRUE.** The selftest's [1] rows run the fixture WARY -> TOLERATED (poll 50) -> VOUCHED (poll 168). My own tally of all 300 logged polls:
   - WARY: missions_open is False on all 54 polls, and both boons are closed_stage or closed_go_dark.
   - TOLERATED: both boons are closed_stage on 118 polls. All 5 mission postings fall at TOLERATED or VOUCHED.
   - All 3 gifts (polls 176, 229, 280) come at VOUCHED.
   The gate reads conduct posture: missions need TOLERATED or higher, boons need VOUCHED or higher.
2. **Never attributed to the Cathedral before stage 3: TRUE.** The lint passes at stages -1, 1 and 2 on both shipped files: RUT_CathedralAssailantMissions.xml and RUT_CathedralFavours.xml. I re-ran it.
   - My own count of player-facing fields gives 38, the same as the linter's count, so it sees every def string.
   - The only player string in the C# (CathedralFavours.cs:124, "Animals gone wrong not yet down: ") is linted in selftest row R.
   - Four planted lines are refused with exit 1: names-the-place, agency, `someone`, and §GM-truth/assailant.
3. **Boon availability flips with a shadow-mode Heat change: TRUE.** In paired runs at the same stage:
   - On poll 18 the gravcore is open in the calm run at Heat 0 (ceiling 5). In the hot run it is withheld_heat at Heat 10.11. It reopens at 4.91.
   - A synthetic Heat of 45 (at or above HEAT_HIGH_BAND) withholds both boons.
   - In the code, the boon state is withheld_heat whenever heat > the def's heatCeiling.
   - Mild flattery: the natural flip is only on the gravcore, at a Heat just past LOW_BAND, and the panels (ceiling 15) do not flip in the hot run. The "high Heat closes both" case is synthetic. It still meets the line as written.
4. **The dark flip closes both: TRUE.** In selftest [4], on go-dark poll 10, missions are closed for the reason go_dark, the posted request is withdrawn, and both boons read closed_go_dark. They stay closed through a 39-poll hold, even after posture climbs back to VOUCHED.
5. **Every beat completes Oracle-absent: TRUE (offline sense).**
   - evidence/oracle_absent_run.txt runs the fixture on a PATH with no `claude`: exit 0, and all 11 of 11 offers carry their full def text.
   - A grep finds no subprocess, Popen or claude call in the blackboard or in CathedralFavours.cs. The text ships as defs.
   - That an in-game beat completes is a live question (see line 8).
6. **K2 anti-laundering: TRUE.**
   - Selftest [6] compares a run that completes every mission with one that ignores them: Heat is identical poll for poll across 6 completions, including during a Heat-carrying sale on poll 100.
   - In the code, Heat changes only by `-HEAT_DECAY_PER_POLL + sale_heat`, and no mission term touches it.
   - In the ordinary log, all 5 completion polls have heat_bump 0. Poll 194 goes 7.714 -> 7.314, which is the decay alone.
7. **Regard feedback observed in shadow logs: TRUE.** The evidence log records at polls 56, 116, 168, 194 and 286 carry mission_completions_this_poll=1 and mission_completion_regard_gain_this_poll=4.0. The selftest pins the gain to exactly 4.0 over the run that ignores missions.
8. **>=1 mission + boon gate live on a quicktest: TRUE for what this lane owes. The live part itself: CANNOT TELL.**
   - What this lane owes is in place. winbuild of CathedralPass: 0 warnings, 0 errors, DLL built. validate_patch: 0 errors over 3 def files. validation.py static PASS. The classes the defs name exist and are public in the right namespace. The exact live recipe is written (evidence/live_run_recipe.txt, steps 0-7). The item is set needs=bridge and reassigned to a live loop.
   - Not proven offline (the recipe says so itself): the pack spawning with the quest tag, RUT_QuestPart_PackDown reaching EndedSuccess, and the gift landing at TradeDropSpot. Only the BENCH/RELENTLESS live run of the recipe settles them.
   - Two small things:
     - The JawaBench `root` field build wrote no DLL ("nothing copied back"). The blackboard falls back to matching on the quest name.
     - The handoff went to RELENTLESS, not "BENCH" as the line words it, though `rimflow show` still lists the owner as BENCH. Standing rulings route live building to Relentless, so this is not a defect of the work.

## Staging / flattery
- All of the offline proof runs on a fixture the builder wrote ("ordinary play") plus synthetic pokes: Heat set to 45, and planted pursuit events. Nothing comes from a real save or a real game.
- The fixture reproduces exactly, and the paired-run design (calm vs hot, completing vs ignoring) is a fair control, not a tidy best case.
- No images ship. None are needed: everything here is a state machine or text.
- The shipped prose reads as deniable, not attributed. One line comes close to a hidden asker: "The runner would not say who asked the enclaves." It is by design and passes the linter.

## Weakest line
Line 8: the whole live path is unproven. The quest-tagged pack, PackDown success and the gift landing all rest on a recipe nobody has run yet. The line assigns that work to the live loop, so it does not block this offline item.

would show: yes
