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

## Built 2026-11-11 (CLAUDE_ARCHMAGI_OFFLINE1, Whittle) — the whole plot runs in-game

The 2026-09-11/09-26 notes that stood here said the plot was blocked on a GM blackboard's "live injection flip".
That premise is gone: `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md` §2 made **Colony
Visibility the one Empire attention meter** ("No Imperial heat variable is added"), and the GM blackboard
(`gm_blackboard_shadow.py`) stays shadow-only. So the plot is wired in the game, mod `src/RimUtinni/KyberTradePlot/`:
- **Sale** = a kyber-family row (`Force_KyberCrystal`, `RUT_Mindstone`) the colony sells in an executed trade deal
  (Harmony on `TradeDeal.TryExecute`). Gifts, crafting, theft and the donation's delivery are never sales.
- **Heat**: Colony Visibility +15 × √crystals (cap 40); **Hutt interest** +3 per crystal from any buyer; **Cartel
  goodwill** +4 when the Cartel buys. First sale: a letter; later sales: a message with the numbers.
- **Alleged Jedi**: a day after the second sale, once per campaign, three Homestead moisture farmers walk in (one
  unarmed, no psylink); a choice letter asks how the kyber was obtained. Any answer = forthright (+8 Homestead
  goodwill, a warning, the door); nothing / leaving unanswered = evasive.
- **Donation**: once, 2.5 days after a door opens (the straight answer, or the Cartel fixer at Hutt interest 15 when
  the visit went nowhere): `RUT_KyberDonationSmuggle`, a trade request for 6–12 kyber at a Homestead or Cartel
  settlement. Delivery pays +5 Homestead goodwill and the letter of thanks: no reward, no Heat, no Rebellion.
- Mod Settings: one switch per feature and the numbers. Spec updated to match.
- Offline proof: `python3 src/RimMandrake/Utils/selftest_kyber_trade_plot.py`. Not yet seen live: a real trade
  window sale, the visitors spawning, the quest generating and completing (`validation.py` lists the first pokes).
