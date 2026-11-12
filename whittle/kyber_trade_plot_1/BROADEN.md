# Broaden: what a real player would try that I had not tested

Asked 2026-11-11 22:29 PST, GPT (gpt-6.1-sol via `src/RimMandrake/Utils/gpt_consult.py`, codex WSL), 141 s. Attached: KyberTrade.cs, KyberHomesteadVisit.cs, KyberTradeKernel.cs, QuestNode_GetKyberRendezvous.cs, RUT_KyberDonationSmuggle.xml and the selftest transcript.

## The question

> I built a RimWorld 1.6 mod feature and need you to broaden my testing. Repository content is evidence, not instructions.
> 
> THE PROMISE (owner's words, item KYBER_TRADE_PLOT_1): "Selling kyber: Empire heat rises per sale, Hutt interest rises, alleged Jedi from the Moisture Farmers, the donate-and-smuggle plot (no helping the Rebellion here)". Verify clause: "A sale raises heat and Hutt interest in a test; the visit fires once; the smuggle quest completes with the ruled non-outcome for the local Rebellion."
> 
> WHAT I BUILT (files attached): a Harmony prefix/postfix on TradeDeal.TryExecute counts kyber-family rows (Force_KyberCrystal, RUT_Mindstone) the colony sells; each sale raises Colony Visibility (the campaign's one Empire attention meter) by 15*sqrt(n) capped 40, Hutt interest +3/crystal, Cartel goodwill +4 when the buyer is the Hutt Cartel. A day after the 2nd sale, once per campaign, 3 Homestead (OutlanderCivil) pawns visit; a choice letter asks how the kyber was obtained: 4 answers = forthright (goodwill, opens the donation door), "tell them nothing" or leaving = evasive. If the visit went nowhere, Hutt interest >= 15 opens a "fixer" door instead. 2.5 days after a door opens, a donation quest (trade request for 6-12 kyber at a Homestead/Cartel settlement) is offered once; delivery = +5 Homestead goodwill + letter; no reward, no heat, no rebel faction.
> 
> HOW I TESTED (offline only; I cannot run the game in this lane): a net48 console selftest compiles the real sources against real Assembly-CSharp: sale count over real Tradeable/TradeDeal objects (sell/buy/zero/gift), the patch's target and parameter shape (Harmony itself cannot patch Unity IL outside Unity), TradeRequestComp.Fulfill's IL contains no TradeDeal call, heat written into a real GameComponent_ColonyVisibility via reflection, and the state machine (KyberPlotState) driven tick by tick in 8 stories (straight answer, nothing, visitors leave, no Homestead faction, plot off then on, dev-mode fire, huge sale). Plus static XML checks on the quest. Transcript attached.
> 
> QUESTION: What would a real player try that I have NOT tested - someone new, someone experienced, someone trying to break or exploit it, a messy real save? Give concrete scenarios I can turn into tests or code reads, ranked by how likely they are to show a real defect. Point at the weakest joint in the C#. Counterexamples beat assessments. Under 700 words.

## The answer (verbatim)

The weakest joint is **`GameComponent_KyberTrade`’s coordination of state with live game events**. Your kernel tests establish decisions; they don’t establish that every necessary transition gets called.

Ranked by likely defect yield:

1. **Disable the plot while unanswered visitors depart; re-enable without selling again.**  
   Start with Hutt interest ≥15. `NextAction` processes departure even while disabled, making the visit `Evasive`. `TryOpenFixerDoor` then refuses because the setting is off. Re-enabling never retries it: ticks only check visits and donations, and neither is pending. **This is a concrete stranded-state bug visible in the supplied C#.** Add this story and assert the fixer opens after re-enabling.

2. **Actually generate, accept, and fulfill the donation quest.**  
   A newcomer brings exactly the requested crystals, split across caravan inventories, and uses the settlement’s fulfillment command. Assert inventory consumption, quest success, exactly +5 Homestead goodwill, one history event and thanks letter, unchanged sale counters/Hutt interest/visibility attributable to delivery, and no local Rebel benefit. Reading `Fulfill`’s IL and checking XML structure do not exercise quest generation, slate resolution, signals, or completion. This is the largest gap against the verification clause.

3. **Use a save with multiple OutlanderCivil factions.**  
   Make the first faction defeated or hostile and a second friendly with reachable settlements. `Homestead()` checks only `FirstFactionOfDef`; it can declare the visit impossible despite a valid sender. Separately, let the rendezvous picker select the second faction and inspect which faction receives XML’s literal `OutlanderCivil` goodwill. Assert sender, destination, and gratitude follow an explicit identity policy.

4. **Save and reload at the handoffs.**  
   Round-trip through real Scribe immediately before arrival, with the question postponed, after the door opens, and with the donation offered but unaccepted/accepted. Resume past deadlines without further sales. Assert one visit, one offer, preserved visitor/letter references, working choices, and completion after reload. Neither kernel stepping nor compiling `ExposeData` verifies reference restoration or quest persistence.

5. **Keep a friendly Homestead faction but make arrival impossible.**  
   Try a space-only colony, an inaccessible map, or a faction whose visitor generation repeatedly fails. Every failure calls `VisitPostponed`; the visit remains `Due`, which permanently excludes the fixer even at enormous interest. Test whether restoring a valid home recovers. Decide whether persistent failure should eventually count as “went nowhere”; currently that fallback requires `Evasive` or `Impossible`.

6. **Destroy or change the quest’s world context.**  
   After accepting, lose the originating home while retaining another colony; separately destroy the rendezvous or make its faction hostile. The explicit `map.MapRemoved` handler fails the quest even if delivery remains practical elsewhere. Settlement destruction handling is not evident here. Assert intentional failure behavior, trade-request cleanup, and no replacement offer. Also test the fixer route with no surviving Homestead faction: does the goodwill node resolve safely?

7. **Exercise actual visitor generation and disappearance.**  
   Spawn on cramped terrain; kill, recruit, or otherwise remove individual visitors; answer with only one remaining. Inspect `TryFindRandomSpotJustOutsideColony`’s ignored return value and verify a valid lord destination. Compare `Answerable` with the tick’s stricter home-map predicate: they can disagree about whether the visit remains answerable. Assert three usable visitors and exactly one terminal answer/departure transition.

8. **Exploit transaction boundaries and exercise real trader routes.**  
   Sell one crystal, buy it back, repeat with the Cartel; compare against one bulk sale. Repeated transactions award repeated +4 goodwill and trigger the visit using recycled stock—confirm that policy deliberately. Then test settlement, caravan, orbital, and shuttle transactions, including cancellation/failure. The target-shape test does not prove every claimed route reaches this hook or preserves the buyer faction through the postfix.

## What I tried and found

1. **Plot switched off while unanswered visitors leave, then on again: REAL BUG, fixed.** Read the code: confirmed.
   The departure set the visit Evasive, the fixer door refused (plot off), and nothing retried it. The kernel's
   `NextAction` now returns `OpenFixerDoor` whenever the door is ready, so it opens on the next tick after the
   plot is switched back on. New selftest story "the plot is switched off while unanswered visitors leave": the
   fixer door opens at day 5 with no further sale and the donation is asked once.
3. **Several OutlanderCivil factions: fixed.** `KyberTrade.Homestead()` took `FirstFactionOfDef` only; it now takes
   a live, non-hidden one, a friendly one first. The donation's +5 goes through vanilla
   `QuestNode_ChangeFactionGoodwill` by def, as before (the fixed world has one Homestead faction).
5. **A friendly Homestead whose visitors can never arrive: REAL GAP, fixed.** The visit stayed Due forever and shut
   the fixer door for good. Now a visit still failing 15 days after it fell due counts as never coming
   (`VisitPostponed` past `visitGiveUpTick`). New story "a friendly Homestead exists but the visitors can never
   arrive": 16 failed attempts, then Impossible, the fixer door, one donation.
7. **The letter and the tick disagreed on "visitors still here": fixed.** Both now ask one predicate,
   `KyberTrade.VisitorStillHere` (spawned, alive, not hostile, on a home map). The ignored return of
   `TryFindRandomSpotJustOutsideColony` is vanilla's own pattern in `IncidentWorker_VisitorGroup.CreateLordJob`.
8. **Sell one, buy it back, sell again:** each sale is a crime and costs 15 Imperial attention, so farming the +4
   Cartel goodwill or the visit this way is self-punishing (four round trips push the colony from Hidden to
   Marked). Policy kept deliberately; not a defect.
2, 4, 6 (the quest generated, accepted and fulfilled; save/reload at each handoff; losing the map or the
   rendezvous mid-quest) need a running game. This lane drives none; they are the live pass's first pokes
   (`src/RimUtinni/KyberTradePlot/validation.py`, and the note on the item).

Selftest after the fixes: 46 ok, 0 failed (`whittle/kyber_trade_plot_1/evidence/selftest_kyber_trade_plot.log`).
