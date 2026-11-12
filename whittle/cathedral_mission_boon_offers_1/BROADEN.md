# Broaden: second-model test pass (CATHEDRAL_MISSION_BOON_OFFERS_1)

Asked 2026-11-11 ~20:30 PST, `gpt_consult.py` (model gpt-6.1-sol, job consult-20261111-203013-2134677-416ea5).
Files given: STATEMENT.md, the selftest output, a player's-eye letter transcript of the ordinary-play fixture,
both favour def files. (The transcript it saw was made before the six request variants landed; see item 6.)

## The question

I built a feature for a RimWorld mod campaign and want you to broaden my testing. Attached: the owner's statement of what must be true (STATEMENT.md), the selftest output (one block per criterion), a player's-eye transcript of a 75-day simulated ordinary playthrough (letters the player would read; lines in [brackets] are hidden mechanics), the defs with the player-facing text, and the blackboard code.

Design in one paragraph: an out-of-game Python "GM blackboard" polls the game read-only each quarter day. It tracks Imperial Heat (raised by kyber crystal sales, decays 0.4/poll), a hidden Regard score and a conduct stage WARY/TOLERATED/VOUCHED. At TOLERATED+ it offers one mission request at a time (6 vanilla quests: cull a manhunter pack of "animals gone wrong"), sourced deniably via droid enclaves or the player's ship (the Utinni), never naming the Cathedral (the hidden patron). At VOUCHED it leaves gravtech gifts (30 gravlite panels, heat ceiling 25, every 15+ days; a gravcore, heat ceiling 10, every 45+ days). A go-dark flip (exposure pressure) closes both and holds them shut 10 days. Completed missions feed Regard (+4) but never touch Heat (anti-laundering rule K2). Offline it runs on a scripted fixture with a simulated player.

Question: what would a real user try that I have not tested -- someone new to the campaign, someone experienced, someone trying to break or exploit it, and a messy real case (save/reload, two colonies, a quest left open for weeks, etc.)? Also: does anything in the transcript read as a quest-giver with a name, or break the "unseen patron grading their manners" feel? Give me the 6-10 most revealing tests, ranked, each with the expected-vs-feared outcome, and say which two you would run first. Be concrete and brief.

## The answer (verbatim)

**Run 1 and 2 first.** The fixture proves useful gate behavior; these tests challenge whether real quests and persistent state agree. The Python blackboard wasn’t included, so persistence concerns below are hypotheses.

1. **Kill the wrong animals — exploiter, live quicktest.** Accept a pack, shelter from it, then slaughter owned animals of the same race. **Expected:** success requires the actual pack’s deaths. **Feared:** the XML’s race/count check awards success and +4 Regard while the attackers remain alive.

2. **Reload across a reward — messy save case.** Save before completion or gift delivery; reload afterward, restart the GM, and repeat a poll. Also interrupt delivery before its acknowledgement. **Expected:** each quest earns credit once per timeline, gifts reconcile, cooldowns survive. **Feared:** duplicate Regard/items, lost gifts, or Heat decay from repeated polling without game time advancing.

3. **Keep an accepted quest open for 30 days, spanning go-dark.** Leave one attacker alive; finish during the hold, then inspect reopening. **Expected:** accepted-quest policy is consistent, completion credits once, no new offers during darkness. **Feared:** permanent blockage, overlapping requests, stale withdrawal, or completion reopening favours early. Existing evidence covers withdrawal of an *unaccepted* request.

4. **Two colonies; move or lose the ship.** Offer at A, select B, accept, then abandon A. **Expected:** pack, quest tracking, gifts, and letters use a coherent location; mission exclusivity holds across colonies. **Feared:** wrong-map attacks, duplicate offers, inaccessible gifts, or “cargo ramp” deliveries where no ship exists.

5. **Cross gates on the exact delivery poll.** At VOUCHED, test Heat just below/at/above 10 and 25; trigger go-dark when a gift’s cooldown expires. **Expected:** final eligibility governs delivery, cooldowns prevent repeats, darkness wins. **Feared:** stale eligibility leaks a gift or repeated threshold crossings reset its cooldown.

6. **Actually cycle all six requests.** Resolve six consecutively, including failures and expirations. **Expected:** all six descriptions appear before repetition. **Feared:** only two cycle—the transcript already repeats “A request from the enclaves” on day 26.75, contradicting the XML comment’s roughly six-week variety claim.

7. **Compare manners, not mission throughput.** Run otherwise matched colonies: considerate conduct, objectionable conduct, and simply ignoring every request. **Expected:** progression follows the intended conduct rules; completions add Regard without changing Heat. **Feared:** passive time or repeated culls overwhelms conduct, making the patron feel like a reputation vending machine.

8. **Blind novice read, including the real quest UI.** Ask who wants this done, what acceptance causes, and whether burning corpses is mandatory. **Expected:** understandable risk, uncertain ultimate sponsor, accurate instructions. **Feared:** a named quest-giver field leaks attribution, or players infer a spreading infection/burning requirement that gameplay never implements.

**On the writing:** the Utinni plainly reads as a named quest-giver: “She wants them dead” and “will not stop asking.” That fits a named intermediary, but exceeds the comment’s claim that no asker is named. “Who asked the enclaves” also explicitly announces a hidden client.

The repeated success reassurance, plus gifts arriving on completion days 41.25 and 71.25, can read as payment for culls. The transcript conveys concealed sponsorship more strongly than an unseen patron grading manners.

## What I tried, and what I found

**1. Kill the wrong animals (ran first; REAL BUG, fixed).** Reading the vanilla source confirmed it:
`QuestNode_PawnsKilled` counts any pawn of the pack's *race* killed by the colony
(`QuestPart_PawnsKilled.Notify_PawnKilled`: `pawn.def == race`), so slaughtering your own tame animals of that
race finished the mission (+4 Regard) while the pack still roamed. Replaced with this mod's
`RUT_QuestNode_PackDown` / `RUT_QuestPart_PackDown` (`src/RimUtinni/CathedralPass/Source/CathedralFavours.cs`):
it completes only when every pawn carrying this quest's pack tag is dead (vanilla
`IncidentWorker_AggressiveAnimals` tags each spawned animal with `parms.questTag`, read in source), and fails if
the pack never arrives in 2 days or walks off alive. This is C# that only a live run can exercise; the live recipe
in `src/RimUtinni/CathedralPass/validation.py` now starts step 3 with exactly this exploit check.

**6. Cycle all six requests (ran).** Its worry came from the stale transcript (2 requests). With the six variants
the selftest now asserts the first six offers are six different quests and the seventh is the first again:
order EnclaveRunner, UtinniInsists, EnclaveShrineRoad, UtinniFrequency, EnclaveBeacon, UtinniRestless,
EnclaveRunner. Passes.

**Writing critique (acted on).** (a) Gifts landed on completion days 41.25 and 71.25 and read as payment for
culls: true in the transcript. Added `CATHEDRAL_BOON_AFTER_COMPLETION_GAP_TICKS` (no gift within two days of a
completed mission); the selftest asserts it over the ordinary-play run (4 gifts, 5 completions, none within two
days after). (b) Every request ended with a wink about who was behind it, which turned "unseen patron" into
"announced hidden client". Cut to one hint per channel (the enclave runner "would not say who asked the enclaves";
the Utinni "changes the subject" when asked how she knows); the others now just end. (c) "She wants them dead",
"she will not stop asking" made the Utinni read as the client: rewritten so she tracks and marks and the mark
keeps coming back. She is still named: the spec's own deniable channel is "the Utinni insists...", and she is
the player's ship, not the patron. I did not take that further.

**3. An accepted quest left open across a go-dark (ran).** New selftest block: a request accepted before the
go-dark is not withdrawn, completes during the 10-day hold, is credited exactly once, and no offer of any kind
appears between the go-dark and the hold's end. Passes.

**5. Gates on the exact poll (partly ran).** Pure-gate rows: each boon is open at Heat == its ceiling and
withheld at ceiling + 1e-6. The "go-dark on the poll a cooldown expires" case is covered by the go-dark poll
rows (boons read closed_go_dark, nothing offered, whatever their cooldown).

**2. Reload across a reward (reasoned, not run).** The blackboard keeps no save state by design. A save reload
rewinds the quest list but not the blackboard: a quest id it already credited is in
`mission_completed_quest_ids`, so completing it again after the reload credits nothing; a gift's cooldown runs
from the original tick, so a reload cannot farm gifts. A *restart of the blackboard process* resets Regard to 0
and re-reads every ended mission quest as a completion on its first poll, which rebuilds the mission share of
Regard and the VOUCHED mission count rather than doubling it; but gift cooldowns reset with it, so a restart can
re-offer a gravcore sooner than 45 days. Not fixed here: persisting blackboard state is outside this item.

**4. Two colonies (not run).** The blackboard reads the current map only, and the boon worker gives to the map
it is fired at. Untested.

**7. Manners vs throughput (partly measured).** In the selftest's K2 pair, the run that ignores every request
ends 200 polls still TOLERATED (VOUCHED needs 3 completions), while the run that completes them reaches VOUCHED.
Matched "bad conduct" colonies were not run; the Regard weights are GM tuning, not this item's.

**8. Blind novice read of the real quest UI (owed to the live run).** The quest has no asker node, so vanilla
shows no giver; the live recipe step 2 screenshots the quest tab to confirm.

## After the pass

A player's-eye reread of the fresh transcript (after these fixes) found the gravcore held back under a day after a
two-crystal kyber sale, then arriving with "The sky has been empty of Imperial traffic for days": untrue. Ceilings
lowered from 25/10 (as in the question above) to 15/5: the gravcore now waits about 3.75 days after such a sale
(selftest [3]). The channel success letters still repeat word for word (one per channel); vanilla
`QuestNode_Letter.textRules` is a `SlateRef<RulePack>` and takes no inline variants from XML, so variety there
would mean one full quest per request. Left as is.
