# The kyber trade — heat, Hutts, the alleged Jedi, and the smuggle

**Item:** `KYBER_TRADE_PLOT_1`. **Source of intent:** owner, 2026-09-06, captured in
`design/Jawa/worldbuilding/biomes/the_lantern_deeps.md` §8 ("The kyber trade").

## 🔴 The law (owner, verbatim in intent)

Selling kyber crystal is **extremely illegal to the Empire** — the player's heat rises
substantially every time — and **the Hutts' positive interest rises** alongside. It may
bring **"alleged" Jedi calling from the Moisture Farmers** wanting to ask how it was
obtained, and a small plot in which some kyber is **"donated to the cause" and smuggled
offworld at a rendezvous** to help the Rebellion elsewhere. 🔴 **Still no way to help it
here: they lost, that's it.**

Standing gates this spec lives under:
- 🔴 Kyber is **crafting material only** (`FORCE_POWERS_ARE_V2_1`) — nothing here grants
  a power, a psycast, or a Force route. The trade plot is about *money, heat, and story*.
- The two laws of the LLM wiring spec apply to any Oracle-voiced beat: text/menu
  authority only, and the game is whole with the LLM absent.
- No worldgen, ever. Every site named here is a quest site on the fixed world.

## 1. The goods

| Thing | defName | Source | Verified |
|---|---|---|---|
| Kyber crystal (item) | `Force_KyberCrystal` | `lee.theforce.lightsaber` (active donor, not yet absorbed) | `crystal_mods_inventory.md` §2, 2026-09-09 |
| Kyber formations (mineable) | `Force_CrystalFormation_{Small,Medium,Large}` | same | same |
| Mindstone | `RUT_Mindstone` | `RUT_mechanoid_origin_canon.md` §1 (name ruled 2026-09-11) | ruled |

**The mindstone is kyber-family and carries this law in full** (mechanoid canon §1):
selling one raises the same Imperial heat as kyber, *plus* the wild cousins' permanent
text-register grudge. That grudge is the mechanoid canon's charge, not this spec's.

Absorption of the kyber family into our tier (`RUT_` names, Deeps genstep gate) is
`crystal_mods_inventory.md` §4's owed pass, separate from this plot spec — ordinary
owed work, not gated on anything (`NAMING_SCHEME_EXECUTION_1` closed 2026-08-31). Until
that absorption lands, all wiring below binds to the donor defNames above and migrates
with it.

## 2. What "a sale" is, and who can see it

A **sale** is any transfer of `Force_KyberCrystal` (or `RUT_Mindstone`) out of the
colony for value: caravan trade, orbital/settlement trade, trade-shuttle sessions
(the reskinned MiningCo Hutt shuttles included). A **gift** to the smuggle plot (§5)
is explicitly *not* a sale — that is the plot's hinge.

**Detection is in-game, at the trade session** (built 2026-11-11, `src/RimUtinni/KyberTradePlot/Source/KyberTrade.cs`):
a Harmony prefix on `TradeDeal.TryExecute` counts the kyber-family rows the colony sells before the deal resolves.
Every trade window goes through it (caravans, settlements, orbital traders, trade shuttles), so crafting, theft,
gifts (`TradeSession.giftMode`) and the donation's delivery (`TradeRequestComp`, not a trade deal) are never sales.
**Heat is the one Empire attention meter already built, Colony Visibility** (`mandrake.rm.visibility`), per
`design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md` §2 ("No Imperial heat variable is added"): it
paces the pursuit ladder and scales its raids, so a sale rides the existing pursuit spine. No new "wanted" system.

## 3. Heat wiring (the Empire side)

- **Per-sale bump: substantial.** Register: a single kyber sale should move Heat more
  than a season of open-sky loitering — the owner's word is "extremely illegal," and
  the gauge's other inputs (orbital timer, Hutt trade generally) are slow burns.
  Scale with quantity, sublinearly (the crime is *selling kyber*, not the invoice
  total). Shipped: 15 Visibility × √crystals, at most 40 per sale (bands are 20 wide), Mod Settings sliders.
- **Consequences ride the existing pursuit spine** — Act I bounties → Act II targeted
  raids → Act III blockade (`required_mods.md` CQF sections; `faction_roster_v2.md`
  §"Two dynamic hooks"). Kyber sales are an *accelerant* on that arc, not a parallel
  arc: no new Imperial incident types are authored for v1.
- **Blackstar Company is Heat-scaled already** (roster, ruled) — kyber money therefore
  buys the player better-equipped hunters without any extra wiring. Say so in flavor
  text; build nothing.
- **Who buys at all:** the Empire's own traders never buy kyber (they are the law being
  broken). The natural buyers are the Hutt Cartel and grey/neutral traders. The
  existing Jawa_Patches trader buy-filter lane (`build_plan.md` tier ①) is the
  mechanism if any trader kind must be excluded from carrying/buying it.

## 4. Hutt interest (the mirror)

Canon already holds the devil's-bargain coupling: **Hutt trade raises Imperial Heat**
(`faction_roster_v2.md`, Cartel appendix). Kyber is its sharpest case.

- **In-game half:** each kyber sale *to the Cartel* grants a modest goodwill bump with
  `RUT_Jawa_HuttCartel` (verified defName, `src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaHuttCartel.xml`)
  — the Hutts like a supplier with nerve. Goodwill is the in-game representation;
  no new stat.
- **Hutt Interest:** a counter kept in the save (`GameComponent_KyberTrade`), fed by kyber
  sales to *any* buyer (word gets around), 3 per crystal. Thresholds unlock, in
  order: (a) a Hutt trade shuttle "requested" visit that pays a kyber premium;
  (b) a named Cartel fixer beat (text/menu) who becomes the standing kyber buyer;
  (c) the fixer is the discovery channel for the smuggle plot's contact (§5) — the
  Rebellion's agent hides inside the Hutt smuggling lane, which is exactly where
  such a person would be.
- **Interest is not friendship.** It never moves the endgame thresholds (alliance or
  debt-bondage routes, Cartel dossier) — it moves *access*: better prices, more
  visits, one more door. The relationship stays bought and conditional, per the
  dossier's law.

## 5. The alleged Jedi (the Homestead visit)

- **Faction:** Homestead Defense League — vanilla `OutlanderCivil` reskinned
  (`faction_roster_v2.md` §3; patch at
  `src/RimUtinni/UtinniPatches/Patches/HomesteadDefenseLeague.xml`). This is the
  roster's *secondary sheltered-Jedi channel* (roster, Global system 5): a rare Jedi
  may shelter within a sympathetic Homestead group.
- **Trigger:** fires **once per campaign**, a day after the second sale (the first is
  deniable, the second is a pattern; Mod Settings slider).
- **Shape (v1):** a visitor group event/quest — two or three Homestead pawns, one of
  whom is the "alleged" Jedi: light kit, plain clothes, **no powers, no psylink,
  nothing on the pawn that confirms anything** (`FORCE_POWERS_ARE_V2_1`; in v1 they
  arrive as people asking questions). The word "Jedi" appears only in *other*
  pawns'/the player's speculation — the visitor never claims it.
- **The conversation (text/menu authority only):** they ask *how the kyber was
  obtained* — mined free, taken from the dead, bought, stolen. Player chooses an
  answer (truthful or not; the quest cannot read minds and does not try). Outcomes:
  - *Forthright* (any honest answer): small Homestead goodwill bump; the visitor
    leaves a quiet warning that others watch the same trades; **flags the player as
    approachable for §6's donation plot** — this visit is that plot's front door.
  - *Evasive/hostile:* no goodwill change, visitors leave; the donation plot must
    then find the player through the Hutt fixer lane (§4c) instead. No punishment —
    suspicion is not a crime even to Jedi.
- **What it is not:** not a recruitment (no Jedi joins), not a Force gate opener, not
  repeatable. One visit, one scene, a door flagged open or not.

## 6. The donation and the smuggle

The small plot, owner-shaped end to end:

1. **The ask.** Through whichever door opened (§5 forthright, or §4c fixer), a
   contact asks that some kyber be **"donated to the cause"** — given, not sold.
   A real quantity (register: it should sting; several sales' worth), player's
   choice to accept.
2. **The rendezvous.** Accepting spawns a **site quest on the fixed world** — a
   rendezvous point a caravan must reach with the kyber within a time window.
   Deep-desert register; site template from the existing curated-ruin/site lane
   (`smuggler's cache` is already in the vetted-template library,
   `desert_world_design.md`). Standard site-quest risk (ambush roll rides the
   normal system; if anyone authored it, Blackstar or Imperial patrol — they are
   the ones sniffing heat).
3. **The handoff.** At the site, the kyber leaves with the smugglers **offworld** —
   narratively past the blockade the player cannot pass (they use the same Hutt
   lanes; a line of flavor, not a mechanic). Quest completes on delivery.
4. **The reward that is not victory.** 🔴 The ruled non-outcome, verbatim: **still no
   way to help it here: they lost, that's it.** No Rebellion faction appears, no
   local uprising, no ally arrives, ever — in this campaign or any later act. What
   the player gets: a letter of thanks from a cause that will spend the crystals
   somewhere the war is still alive; a modest Homestead goodwill bump (the
   sympathizers know); **zero Heat change** (RULED 2026-09-11 — the donation is quiet, but
   scrubbing heat would make donation a laundering exploit); and the
   knowledge, priced exactly at the donated kyber, that the player chose a side no
   one here will ever reward. The reward *is* the register.
5. **Refusing or failing** closes this plot for good (one Rebellion cell, one
   chance); the kyber from a failed run is lost with the caravan's normal fate. No
   revenge, no grudge — the cause simply stops calling.

## 7. Build surfaces (for the eventual implementation item)

| Piece | Surface | Owner of the number |
|---|---|---|
| Heat bump per sale, Hutt Interest, fixer threshold | `GameComponent_KyberTrade` + `KyberTradeKernel.cs` (in-game; Colony Visibility is the meter) | Mod Settings |
| Hutt goodwill on Cartel sales | the same sale hook, `TryAffectGoodwillWith` | Mod Settings |
| Homestead visit + conversation | `IncidentWorker_KyberHomesteadVisit` (a visitor group) + `ChoiceLetter_KyberHomesteadQuestion` | quest authoring |
| Rendezvous | `RUT_KyberDonationSmuggle`: a trade request at a Homestead or Cartel settlement (`QuestNode_GetKyberRendezvous`); no "smuggler's cache" SitePartDef exists | quest authoring |
| Trader buy-filter (if any) | Jawa_Patches tier ① | config |

Neither piece uses CQF: the visit is a vanilla-shaped visitor incident with its own letter, and the donation is a
vanilla QuestScriptDef, so `build_plan.md` §6.1's CQF question does not touch this plot.

## 8. Verify (mirrors the item)

- A sale of `Force_KyberCrystal` raises Heat and Hutt Interest in a test; a crafting
  consumption of the same quantity raises neither (`python3 src/RimMandrake/Utils/selftest_kyber_trade_plot.py`).
- The Homestead visit fires exactly once, and never grants a power or a recruit.
- The smuggle quest completes with the ruled non-outcome: no Rebellion presence
  exists on the world after completion, and the reward matches §6.4.

## Cards — RULED 2026-09-11

- **K1 RULED.** Owner, verbatim: *"It was supposed to be quite a long time ago,
  empires rising and falling. But a Helix expedition vessel could easily have
  explored it, and certainly the Empire is aware of it and could have mined
  some on an expedition. A rare Junker expedition might actually survive
  too."* So the mines are DEEP-TIME — worked and abandoned across rising and
  falling empires, no single later party — and the evidence layers a delver
  can find include a Helix expedition's traces, an Imperial expedition's
  mining scars (which is also how the Empire knows kyber is here), and, rarely,
  a Junker expedition that actually made it back. Feeds the Deeps' gallery
  dressing and the Junkers' fragments of the Deeps stories.
- **K2 RULED: Heat unchanged.** The smuggle scrubs nothing — donation is pure
  cost, never laundering. §6.4's zero-Heat proposal is now the rule.
