# KYBER_TRADE_PLOT_1 — selling kyber: heat, Hutts, alleged Jedi, and the smuggle

Owner, 2026-09-06 (`the_lantern_deeps.md` §8, verbatim in intent): selling kyber crystal
is **extremely illegal to the Empire** — the player's heat rises substantially every time
— and **the Hutts' positive interest rises** alongside. It may also bring **"alleged"
Jedi calling from the Moisture Farmers** wanting to ask how it was obtained, and a small
plot in which some kyber is **"donated to the cause" and smuggled offworld at a
rendezvous** to help the Rebellion elsewhere. 🔴 **Still no way to help it here: they
lost, that's it.**

## spec
- Wire the heat mechanic (the Empire's pursuit/attention system — find the existing
  heat/wanted representation before inventing one) to kyber sales; the Hutt interest as
  the mirror stat/relationship.
- The alleged-Jedi visit as a quest/event from the Moisture Farmer / Homestead faction
  (the sheltered-Jedi channel already ruled in the Force gate — NPC-only, light kit, v2
  for powers; in v1 they arrive as people asking questions).
- The donation-and-smuggle plot: rendezvous site, offworld handoff, the reward that is
  not victory here. Quest-authoring skill applies; keep to text/menu authority.
- Ties: `LANTERN_DEEPS_INJECTION_1` (the source), the Force gate in `required_mods.md`,
  the Hutt faction spec.

## verify
A sale raises heat and Hutt interest in a test; the visit fires once; the smuggle quest
completes with the ruled non-outcome for the local Rebellion.

## Progress 2026-09-11 — spec drafted (BENCH fan-out)
Design spec: `design/Jawa/kyber_trade_plot_spec.md` (heat wiring on the GM
blackboard, Hutt Interest mirror, the alleged-Jedi visit powers-free, the
donate-and-smuggle quest). Cards K1 (who were the later parties in the old
mines) and K2 (does the smuggle scrub heat) await the owner; implementation
owed after his rulings.

## Progress 2026-09-11 — quest content built (FOUNDRY); BLOCKED on GM-layer infra

**Built and offline-validated** (`python3 skills/rimworld-quests/scripts/validate_quest.py
--dir src/RimUtinni/KyberTradePlot/Defs/QuestScriptDefs` — 2 QuestScriptDef(s),
0 errors, 0 warnings), new mod `src/RimUtinni/KyberTradePlot/`:
- `RUT_KyberHomesteadVisit` (spec §5) — one-shot conversation quest; Accept =
  Forthright (Homestead/`OutlanderCivil` goodwill +8, `RUT_KyberHomesteadDoorOpened`
  HistoryEventDef, letter), letting it expire = Evasive (nothing fires — no
  punishment, matches spec exactly).
- `RUT_KyberDonationSmuggle` (spec §6) — donation/rendezvous quest built on
  vanilla `TradeRequestComp`/`QuestNode_TradeRequest_*` (the proven mechanism
  already shipped in `RUT_FungalSoilTradeRequest.xml`). Fulfillment: Homestead
  goodwill +5, `RUT_KyberDonatedToCause` HistoryEventDef, letter of thanks — **no
  `QuestNode_GiveRewards` anywhere in the file**, so K2 (zero Heat, never
  laundering) holds trivially. No Rebellion faction or presence is created by
  anything in this file, ever (spec §6.4/§6.5).
- Both fire only through paired `RUT_GiveQuest_*` IncidentDefs (`baseChance 0`,
  `ParentName="GiveQuestBase"`) — the same deterministic dev-mode/bridge trigger
  pattern `VAULT_THAW_QUEST_FAMILY_1` established. Neither is
  `rootSelectionWeight` > 0; neither can be rolled by the storyteller.

**Two named, documented substitutions** (see each file's own header comment for
the full reasoning): (1) the Homestead visit has no live pawn group walking the
map — vanilla has no multi-button mid-scene dialogue node (`QuestPart_Choice` is
a pre-accept reward-picker, not a narrative branch; confirmed by reading
`RimWorld/QuestPart_Choice.cs`), so Forthright/Evasive is the quest's own
Accept/let-expire choice, matching how every other quest in this repo
represents a decision; (2) the rendezvous is a nearby settlement standing in
for "the smuggling lane's fixer," not a new `smuggler's cache` SitePartDef —
no such site template exists yet in this repo (grepped, absent) and authoring
one is materially larger scope than this pass.

**BLOCKED, not closed — the item's own `## verify` first clause cannot be met
today:** "A sale raises heat and Hutt interest in a test." The spec is explicit
that Heat/Hutt-Interest live on an **external GM blackboard** (`build_plan.md`
§2, §M4 "Heat in shadow mode") that **does not exist as buildable
infrastructure** — searched the repo (`grep`, `find`) for any Python state
machine, blackboard file, or trade-session poller and found none; `build_plan.md`
itself lists M4 as unstarted ("fast-follow at M4, not v1") and the CQF-vs-thin-
config question in §6.1 is still open. Building a parallel in-mod Heat/Hutt-
Interest counter would be exactly the "invent a parallel system" this task was
told not to do. **What's owed before this item can close:** (a) the M4 Heat
shadow-mode blackboard itself; (b) whatever polls trade sessions and diffs
kyber/mindstone counts to detect a sale (spec §2's "reconcile against the trade
session, not raw inventory" warning still applies); (c) the wiring that fires
`RUT_GiveQuest_KyberHomesteadVisit` at the second sale and
`RUT_GiveQuest_KyberDonationSmuggle` from either door (§5 forthright or §4c Hutt
fixer) — none of which this item's own build surfaces table (spec §7) claimed
were done already. The in-game Hutt goodwill bump on ordinary Cartel kyber
sales (spec §4 "in-game half") is equally blocked: the spec ties its trigger to
the same GM-layer sale detection, not a standalone Harmony hook, so it rides
the same missing infra rather than being separately buildable.
