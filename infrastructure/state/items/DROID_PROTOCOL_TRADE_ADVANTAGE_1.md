# DROID_PROTOCOL_TRADE_ADVANTAGE_1 — the protocol droid pays for itself

Packet **C4** of `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` (§5).
Governed by owner **ruling 2**, 2026-09-06 (§0 of that doc), whose load-bearing
sentence is: *"Many traders will come with protocol droids to help them with
communication and trade advantage (**there should be real trade advantage to
having a protocol droid with you, dangerous not to**)."* Predecessor
`DROID_FACTION_LOADOUTS_1` (C1) put a Protocol-family droid into six factions'
Trader-group `guards` — presence only, no mechanic. The mechanic is this packet.

## spec

§3.2's row: *"C4: `StatDef` factor on trade prices/negotiation when a
Protocol-family pawn is in the trade party; a penalty without one — both sides,
so traders without one are cheaper to fleece."* §6's anti-exponential guardrail
constrains it: *"symmetric: traders' droids work against you; the player's droid
is a salvaged, brain-imported asset, not a build."*

## Built

`src/RimStarWars/Droidworks/Source/Droidworks/Patch_ProtocolTradeAdvantage.cs`
(Droidworks assembly, RSW tier — the rule is about any Protocol droid anywhere,
not about this campaign's factions, so it belongs on the platform beside the
`chassisClass` it reads. C1's faction loadouts stayed RimUtinni for the opposite
reason: those name *our* factions.)

### The targets, and why a Postfix

RimWorld computes a trade price in exactly two places:
`TradeUtility.GetPricePlayerBuy` and `TradeUtility.GetPricePlayerSell`, both
`public static float`, both called once per `Tradeable` from the private
`Tradeable.InitPriceDataIfNeeded`, which caches the result into
`pricePlayerBuy`/`pricePlayerSell`. Postfixing those two catches every route to
a price — dialog, deal total, caravan trade, orbital trade — and multiplies the
vanilla result, so the effect **composes** with the negotiator's Social skill,
the faction-base offset, trader price type, difficulty and `SellPriceFactor`
instead of replacing any of them. A prefix would have had to reimplement all of
that and was never a candidate.

Each postfix re-applies vanilla's own tail after its factor — `Mathf.Max(…,
MinimumBuyPrice/MinimumSellPrice)` and the `> 99.5f` rounding — which the
multiplication would otherwise step through.

A third postfix on `Tradeable.GetPriceTooltip` appends the explanation. It is
legibility only and the mechanic works without it, but vanilla's tooltip names
every other price factor, so an unexplained 12 % swing reads as a bug.

### ⛔ Why NOT a `StatPart` on `TradePriceImprovement` — the obvious route, and it is dead

§3.2 says "`StatDef` factor", and `Tradeable.InitPriceDataIfNeeded` really does
read `playerNegotiator.GetStatValue(StatDefOf.TradePriceImprovement)` into the
additive gain — a `StatPart` would have been tidier, self-documenting in the
stat card, and additive exactly where vanilla is additive.

**It cannot carry this ruling.** `Stats_Pawns_Social.xml` declares that StatDef
with `<minValue>0</minValue>` and `<maxValue>0.395</maxValue>`, and
`StatWorker.FinalizeValue` ends with `Mathf.Clamp(val, stat.minValue,
stat.maxValue)` whenever `applyPostProcess` is true — which is the default and
what `GetStatValue` passes. So the **penalty half — the entire "dangerous not
to" — would silently clamp to zero**, and a high-Social negotiator's bonus half
would clamp away too. Widening a vanilla stat's clamps in XML would have
un-clamped the Inspired Trade case (0.32 + 0.18 = 0.50, currently cut to 0.395)
for every pawn in the game. Rejected on both counts. Recorded here because the
spec named the route and the next reader will reach for it again.

## The number and the shape — FOUNDRY's, no ruling exists

Ruling 2 gives no percentage. Chosen: **`PerSideAdvantage = 0.06f`**, one term
per side.

| side | has a Protocol droid | lacks one |
|---|---|---|
| player party | **+1** | **−1** |
| trader party | **−1** | **+1** |

`net = playerTerm + traderTerm`, so both-or-neither cancels to exactly zero —
§6's symmetry requirement — and net ranges −2…+2, i.e. **−12 % … +12 %**.
Positive is good for the player: **buy prices × (1 − net), sell prices × (1 +
net)**. Full swing between best case and worst is 24 percentage points on any
price.

Calibrated against vanilla's own scale: a settlement offsets 0.02, a maxed
Social negotiator reaches ~0.30, the Inspired Trade inspiration gives 0.18. At
0.06 per side the effect is well clear of noise and well short of out-earning
the negotiator himself. Because C1 gave six factions' trader guards a protocol
droid, the **default** state for a player without one is net −2: buys 12 %
dearer, sells 12 % cheaper. That is the "dangerous not to".

## Assumptions recorded

1. **"Party" is defined per side, mirroring how the game already groups pawns.**
   Player side: the negotiator's `Caravan` if he is in one, otherwise every
   player-faction pawn spawned on his map. Trader side: the trader pawn's
   `Lord.ownedPawns` (a visiting trade caravan is one Lord), else the trader
   alone; or a world `Caravan`'s pawn list.
2. **The trader term applies only when the trader's party is enumerable.** An
   orbital `TradeShip` and a `Settlement` have no pawns to inspect, so they
   contribute **nothing** rather than scoring as "no droid" and handing the
   player a free +6 % on every orbital trade. The **player** term always
   applies — it is always knowable, and ruling 2 puts the penalty squarely on
   the player's own side.
3. **A droid must be able to talk for you**: dead, downed, powered-down
   (`RSW_DW_PoweredDown`) or imprisoned droids do not count.
4. **Protocol-family test** is `chassisClass == 1` on the race's own
   `DroidworksExtension`, read with the same `OfType<>().LastOrDefault()` pattern
   `CompDWHeadDropper`/`CompDroidDetonation`/`CompDWPartDropper` document — XML
   inheritance APPENDS `modExtensions`, so the race's own copy sorts last.
5. **Gifts are not trades.** `FactionGiftUtility.GetGoodwillChange` calls
   `GetPricePlayerSell` to value a gift; the patch no-ops when
   `TradeSession.giftMode` is set, and when the currency is not Silver (royal
   favor is returned unscaled by vanilla).
6. **The verdict is cached per (trader, negotiator) for 250 ticks.**
   `InitPriceDataIfNeeded` runs once per `Tradeable` and a caravan trade holds
   hundreds, so an uncached party scan would run hundreds of times for an answer
   that cannot change while a dialog is open. Consequence, and it is deliberate:
   changing a party mid-dialog does not move prices until the session is
   reopened.
7. **Own Harmony instance** (`mandrake.rsw.droidworks.tradeadvantage`), not
   `…needgate`'s, so a failure here cannot take the `RSW_DW_Power` need gate
   down with it. Same `[StaticConstructorOnStartup]` + static `Apply(Harmony)`
   shape `Patch_ShouldHaveNeed_Power.cs` documents.

## verify — MEASURED LIVE, both ways

The packet's verify line is *"trade with/without a protocol droid, prices
measured both ways"*. Done, on the 25-mod minimal list (load 30 s), quicktest
map, a real `TraderCaravanArrival` (804 points, `Caravan_Neolithic_ShamanMerchant`,
`TribeCivil`, an **18-pawn Lord roster**), one negotiator (Boots,
`TradePriceImprovement` 0.03), through `jawa/trade_price_probe`.
Script: `src/RimMandrake/bridgetools/prove_trade_price_probe.py`.

| | player party | trader party | net | predicted |
|---|---|---|---|---|
| **before** | 4 pawns, **no** protocol droid | 18 pawns, **no** protocol droid | −1 +1 = **0** | no shift |
| **after** | 5 pawns, protocol droid *Landon* (`chassisClass 1`) | 18 pawns, no protocol droid | +1 +1 = **+2** | buy ×0.88, sell ×1.12 |

Measured ratios, after ÷ before, on the 12 reported tradeables:

```
Monkey        buy 136.00 -> 120.00  x0.8800     sell  61.80 ->  69.22  x1.1200
Chicken(29.65)buy  40.26 ->  35.43  x0.8800     sell  18.32 ->  20.52  x1.1200
Chicken(50.00)buy  67.90 ->  59.75  x0.8800     sell  30.90 ->  34.61  x1.1200
Dromedary     buy 407.00 -> 358.00  x0.8796     sell 185.00 -> 207.00  x1.1189
Gold          buy  13.58 ->  11.95  x0.8800     sell   6.18 ->   6.92  x1.1200
Bioferrite    buy   1.02 ->   0.90  x0.8800     sell   0.46 ->   0.52  x1.1200
Pemmican      buy   1.90 ->   1.67  x0.8800     sell   0.87 ->   0.97  x1.1200
Plasteel      buy  12.22 ->  10.76  x0.8800     sell   5.56 ->   6.23  x1.1200
Tome          buy 421.00 -> 370.00  x0.8789     sell 192.00 -> 215.00  x1.1198
MindNumbSerum buy 109.00 ->  95.92  x0.8800     sell  49.44 ->  55.37  x1.1200
Silver        buy   1.00 ->   1.00  x1.0000     sell   1.00 ->   1.00  x1.0000
```

**×0.8800 / ×1.1200 is exactly the predicted ±12 %.** The four rows reading
0.879x/1.118x are vanilla's own `> 99.5f` rounding of the larger prices, not
drift. **Silver is untouched at ×1.0000** — correct and load-bearing:
`Tradeable.IsCurrency` short-circuits `InitPriceDataIfNeeded` before either
price function is reached, so the currency itself can never be re-priced.

What this pair proves together, and why one run alone would not:

* the patch **applied** (the after run moved) — a Harmony patch that silently
  fails to bind is the failure mode this whole check exists for;
* the **net-0 cancellation is real** (the before run did not move) — with the
  patch demonstrably live, "no shift" is a computed zero, not an absence;
* `TraderParty()` really reads a trader's **Lord** roster: 18 pawns, not the
  one trader pawn;
* the Protocol test agrees with an independent instrument — the probe reports
  `droidChassisClass` read **reflectively** off `DroidworksExtension`, different
  code from the patch's own `OfType<>().LastOrDefault()`.

⚠️ **Not directly measured: the trader-side POSITIVE branch** (a protocol droid
in the *trader's* party → −1). The minimal list carries Droidworks but not the
RimUtinni patches where C1 put protocol droids into trader `guards`, and there
is no way to add a pawn to an existing Lord from the bridge. What IS exercised
is every component of it: `PartyHasProtocolDroid` returning **true** over a
party (player side) and **false** over the 18-pawn trader Lord roster, and the
sign arithmetic, which is one expression. Residual risk: the sign, i.e. that a
trader's droid helps the trader rather than the player. Read the table above
against `CurrentAdvantage()` before assuming otherwise.

⚠️ The run above keyed its DELTA rows by `defName`, so the two distinct
Chicken tradeables collided and it printed a nonsense ratio for one of them —
the raw before/after numbers above are per row and both Chickens are
×0.88/×1.12. Script artifact, not a mechanism discrepancy; the committed script
now keys by position and says so when the row order moves.

## Also built: the instrument

`jawa/trade_price_probe`
(`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTradeProbeTools.cs`).

Nothing on the bridge could open or read a trade. Trade prices are computed in
`TradeUtility`, cached into `Tradeable`, and surfaced only through
`Dialog_Trade` — a **modal**, and nothing on the bridge can answer a modal. So
any claim about a trade price factor was unfalsifiable from here, and this
packet's own verify line ("prices measured both ways") was unreachable.

The tool opens a headless `TradeSession` against a trader pawn on the current
map, reads `Tradeable.GetPriceFor` — the same accessor the dialog uses, so every
mod's price factor is included — and closes the session again exactly as vanilla
does. It refuses when a real `TradeSession` is already active (the static would
be clobbered). It also reports both parties' rosters with each pawn's
`droidChassisClass`, read **reflectively** off any `DroidworksExtension`, so the
signal the patch keys on is confirmed by different code than the patch's own.

Reusable for C5 (`DROID_REPAIR_FOR_PROFIT_EVENTS_1`, payment scaling) and any
future trade work.
