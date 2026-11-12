# JUDGE — CATHEDRAL_MISSION_BOON_OFFERS_1 (blind, CLAUDE_ARCHMAGI_OFFLINE3 judge seat, 2026-11-11)

Read: STATEMENT.md, NOTES.md, every file in evidence/. Not read: DONE.md, BROADEN.md, the earlier JUDGE.md.
Re-ran at clean HEAD 4de5e82144 (src tree clean; the evidence headers say "2 dirty src file(s)", so I re-ran rather than trust them):
- `selftest_rustcathedral_offers.py`: exit 0, 87/87. The `ok` lines are identical to evidence/selftest_offers.txt.
- `gm_blackboard_shadow.py --fixture cathedral_offers_ordinary_play.json --log /tmp/judge_shadow.jsonl`: exit 0. The 300 records match
  evidence/shadow_log_ordinary_play.jsonl exactly, timestamps excepted (0 rows differ).
- `cathedral_arc_lint.py --xml <both shipped def files> --stage 1` and `--stage 2`: 38 strings, PASS, exit 0. Instrument probe (temp copies
  in /tmp): "Cathedral" planted in a mission `<customLetterText>` and in the gravcore `<letterText>` were both refused, exit 1, at stage 2
  (and at 3 for the letter). So the --xml path reads the letter fields, not just the labels. 38 = 8 parent letter strings + 12 child
  name/description + 12 GiveQuest label/letterLabel + 6 boon strings, which accounts for every player-facing string in the two files.
- Vanilla check: QuestNode_ManhunterPack takes `tag`, `customLetterLabel` and `customLetterText` in Royalty's own QuestScriptDefs
  (Scripts_ItemPodThreat.xml, Script_Intro_Wimp.xml). validate_patch.py does not scan field names, so I checked these myself.
- code_review_status: CathedralFavours.cs, gm_blackboard_shadow.py, the selftest, both def files and validation.py are all CLEAN.
- Ledger: `rimflow show` reads `ready, needs bridge, owner BENCH`, with an offline-landed note naming the recipe (2026-11-12T04:44Z).

## Lines

1. **Offer appears only at the correct stage: TRUE.** Selftest [1] drives the real `ShadowBlackboard.poll` with the ordinary-play
   fixture. It goes from WARY (missions False, stage_below_TOLERATED, both boons closed_stage) to TOLERATED at day 12.25 (mission_offer,
   boons still closed_stage) to VOUCHED at day 41.75 (panels/gravcore open, boon_offer at day 43.75). The checks hold on every poll:
   no offer on any WARY poll, no boon on any TOLERATED poll. The gate is `compute_cathedral_offer_gate` (posture >= TOLERATED for missions,
   >= VOUCHED for boons). Both the defs and the incidents are baseChance 0 / rootSelectionWeight 0, so nothing else can roll them.
2. **Never attributed to the Cathedral before stage 3: TRUE.** The CLI lint on both shipped files exits 0 at stages -1, 1 and 2 (my rerun
   at 1 and 2). The planted lines are refused with exit 1 (names-the-place, agency, §GM-truth "assailant"), and my own plants are refused
   too. When I read the strings myself, none names the place, an asker or the Assailant. The nearest to a hint is the gravcore letter's
   "fits the Utinni's sockets as if it had been cut for them", which is deniable and passes the linter.
3. **Boon availability flips with a shadow-mode Heat change: TRUE.** In the selftest [3] paired runs, the calm run offers the gravcore on
   poll 18 at Heat 0. The hot run (two kyber sold on poll 16, nothing else changed) withholds it on the same poll at Heat 10.11
   (`withheld_heat`). Stage is VOUCHED throughout, and the gravcore reopens at Heat 4.91. Note: this organic flip uses the gravcore's own
   ceiling of 5, so the "high" Heat here is 10.11, barely above the board's HEAT_LOW_BAND of 10. The case at or above HEAT_HIGH_BAND
   (both boons withheld) uses a synthetic `board.heat = 45`. The line's own evidence clause (open at low, closed after a rise, same
   stage) is met.
4. **The dark flip closes both: TRUE.** Selftest [4], go-dark poll 10: missions closed with reason `go_dark`, the posted request withdrawn
   (`mission_offer_withdrawn`), and both boons `closed_go_dark`. The hold lasts 39 polls even after posture climbs back to VOUCHED, so the
   closing is the dark flip and not just the stage drop. The pursuit trigger is staged: the go-dark threshold is lowered to 15 so that one
   pursuit fires it.
5. **Every beat completes Oracle-absent: TRUE.** All 46 offer/letter strings ship as def text (the two def files). evidence/oracle_absent_run.txt
   runs the fixture with a PATH holding no `claude`: exit 0, and 11 of 11 offers carry the full def text. The grep finds no
   subprocess/Popen/os.system/claude in the blackboard or in CathedralFavours.cs. Selftest [5] repeats this on its own scratch PATH.
6. **K2 anti-laundering, zero Heat scrubbed: TRUE.** Selftest [6] compares a run that completes 6 missions with one that ignores them all.
   Heat is identical poll for poll, including poll 108, where Heat is non-zero (10.656 to 10.256, the shared 0.4 decay). Regard ends
   24.0 higher in the completing run. The only Heat write in the code is `max(0, heat - decay + sale_heat)`.
7. **Regard feedback observed in shadow logs: TRUE.** In the committed shadow log, and in my independent rerun, poll 56 records
   `mission_completions_this_poll=1`, `mission_completion_regard_gain_this_poll=4.0` and `cathedral_regard_delta_this_poll=4.3`. The same
   record appears at polls 116, 168, 194 and 286.
8. **≥1 mission + boon gate live on a quicktest: TRUE for what this lane owes; the live proof is still owed.** The statement takes the
   live run out of this lane. What the offline lane owes is all present: the CathedralPass DLL is built (0 warnings, 0 errors, source
   4de5e82144, and the committed DLL is not dirty after the build); validate_patch.py passes 3 files with 0 errors (the `info` lines are
   the mod's own C# classes); static validation.py PASS; the exact recipe is in validation.py, and its "NOT PROVEN offline" section is
   honest. The item is noted, set needs=bridge and owned by BENCH. Weak point: the JawaBench build "wrote no DLL ... nothing copied
   back", so the quest_lifecycle `root` field is not shown landing anywhere deployable. The recipe covers this (the name-match fallback).

## Where the evidence is staged or flattering
- Everything is fixture or shadow. The "offers" are `would_fire` records, and letters_ordinary_play.txt is the builder's rendering of the
  log, not game letters. The builder wrote the "ordinary play" fixture, and it is a tidy arc that climbs to VOUCHED in 42 days.
- The high-band Heat case is set by hand (heat=45). The go-dark case lowers the threshold to 15.
- Nothing shows the in-game half: the manhunter pack spawning tagged on accept, RUT_QuestNode_PackDown reaching EndedSuccess, the boon
  landing at TradeDropSpot. This is said openly and owed to the BENCH live loop.

## Verdict
Each statement line holds on evidence I re-ran myself, and the one live line is scoped out and correctly handed to BENCH (needs=bridge).
I would show it to the owner as finished for this offline lane.

would show: yes
