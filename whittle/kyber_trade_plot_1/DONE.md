<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- unseen: Selling kyber: Empire heat rises per sale, Hutt interest rises, alleged Jedi from the Moisture Farmers, the donate-and-smuggle plot (no helping the Rebellion here) is done as `infrastructure/state/items/KYBER_TRADE_PLOT_1.md` says, shown by fresh evidence. | evidence: `whittle/kyber_trade_plot_1/evidence/selftest_kyber_trade_plot.log` `whittle/kyber_trade_plot_1/evidence/build.log` `whittle/kyber_trade_plot_1/evidence/static_validators.log` `whittle/kyber_trade_plot_1/evidence/dll_types.log`

**Verdict "unseen", not "true":** the fresh judge (`whittle/kyber_trade_plot_1/JUDGE.md`, would show: no) is right that
two of the item's three verify clauses were never run in a game: the visit spawning and its letter, and the donation
quest generating and completing. This lane drives no game, so the item is parked needs=bridge for a live lane
(`whittle/kyber_trade_plot_1/BLOCKED.md`). What the offline evidence does show, clause by clause, against
`selftest_kyber_trade_plot.log` (HEAD 7fd2d784d9, 58 ok, 0 failed):
- **"A sale raises heat and Hutt interest in a test."** Section "a run of sales...": a 2-crystal sale to a grey
  trader moves the real Colony Visibility component 10.0 -> 31.2 (Hidden -> Discreet) and Hutt interest 0 -> 6; a
  1-crystal sale to the Cartel 31.2 -> 46.2, interest 9, Cartel goodwill +4. "What counts as a sale": real
  Tradeable/TradeDeal rows; selling 3 kyber + 1 mindstone beside steel and a lightsaber counts 4; buying, a zero row
  and a gift count 0; crafting never enters a trade deal. Heat is Colony Visibility because the escalation-ladder
  design made it the one Empire meter ("No Imperial heat variable is added").
- **"The visit fires once."** Over 120 game days with four sales, one visit (every story checks the count); it never
  comes again after a dev-mode fire, a straight answer, silence or an unanswered departure; with no friendly
  Homestead it never fires and the fixer door takes over.
- **"The smuggle quest completes with the ruled non-outcome for the local Rebellion."** The donation is asked once
  through either door; on `settlement.TradeRequestFulfilled` the quest does exactly four things (Homestead goodwill
  +5, a memory, the letter "There is still no way to help it here...", Success); it holds no reward node and no node
  that creates a faction, pawn or site; the delivery (`TradeRequestComp.Fulfill`, IL read) never runs a trade deal,
  so it raises no heat (K2).

## What I'm least sure about
- **The game-side glue has never run in a game.** `GameComponent_KyberTrade` (Find.*, letters, goodwill calls),
  `IncidentWorker_KyberHomesteadVisit` (spawning three Peaceful-group pawns, the visit lord),
  `ChoiceLetter_KyberHomesteadQuestion` (its five answers) and `QuestNode_GetKyberRendezvous` (TestRun/Run in a
  real slate). They compile against the real 1.6 assemblies and every class the XML names is in the DLL
  (`dll_types.log`); the decisions they act on are the tested kernel. A fresh Opus review of that glue, against the
  decompiled 1.6 source, found 10 issues and all the code ones are fixed in `449116ac5a` (the visit landing on an
  orbital map or a colonist-less home, a null Homestead crashing the donation every tick, arrested or recruited
  visitors stalling the plot, dev-mode fires bypassing the once/off gates, an exception in the sale hook breaking
  the trade window, a child as the quiet one, a flat 350 market value). None of those fixes can be exercised
  offline either.
- **Harmony's application of the patch** is checked by shape only (target, injected parameter names/types): Harmony
  cannot detour Unity-compiled IL in a bare .NET process. `validation.py`'s `jawa/harmony_patches` chain is the live
  proof.
- **Numbers**: 15 x sqrt(crystals), cap 40, on a 0-100 meter. Four sales took a colony from Hidden to Exposed in 20
  days. That is "extremely illegal" by design, and all are Mod Settings sliders, but nobody has played it.
- The spec's "smuggler's cache" rendezvous site does not exist as a SitePartDef; the rendezvous is a trade request
  at a Homestead or Cartel settlement (never an Imperial one).

## What I did not test
- A sale in a real trade window (caravan, settlement, orbital, shuttle) and the first-sale letter/messages on screen.
- The visitors spawning and walking in, the letter opening, an answer applied, save/reload with the letter pending.
- The donation quest generating at a real settlement, being accepted, delivered and completing, or failing on
  map loss/hostility. Vanilla `TradeRequestComp.Fulfill` also gives the settlement's faction +12 goodwill.
- Spec §3's "the Empire's own traders never buy kyber" filter: not built (selling to an Imperial trader would raise
  heat like any other sale).
- This lane drives no game; the live pass is noted on the item for a live lane (`validation.py` lists its pokes).
