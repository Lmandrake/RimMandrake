# The Bazaar — the scavenger trade window

**Status: RULED (owner, 2026-09-13, bench sitting — same day as the liquids
framework, which this integrates with).** Name canonized by the owner: **The
Bazaar**. Identity per `design/NAMING_SCHEME_PLAN.md`: packageId
`mandrake.rm.bazaar` · display `RimMandrake: The Bazaar` · namespace
`RimMandrake.Bazaar` · defNames `RM_Bazaar*` · folder `src/RimMandrake/TheBazaar/`.
Campaign wiring (Ash'karr settlement tags, droid-module placements) lives in the
RimUtinni layer.

The thesis: **the deal is the gameplay.** Vanilla treats trade as a spreadsheet
checkout; for a Jawa, information is loot, reading the trader is a skill, and
walking away richer than you should have is the fantasy.

Ecosystem facts this rests on (researched 2026-09-13): no shipped mod combines
trade UI + dynamic economy + negotiation — ecosystem "haggling" is a static
random multiplier; Dynamic Trade Interface (not in our list) is the only
extensible trade UI, and we take its *architecture* (typed plugin defs), not its
code; the proven base primitive of every great RimWorld UI (VPE, Numbers, Work
Tab, Mint Menus) is a searchable, sortable, column-configurable grid with
presets. Vanilla Trading Expanded was source-analyzed and REJECTED as a feeder:
one global price per ThingDef (no locality — contradicts our worldTag economy),
a global MarketValue StatWorker substitution (high blast radius), and
pre-blended history no external consumer can baseline against. Its
clamp/mean-reversion pattern is sound and is copied; nothing else is.

## 1. Pillars

1. **The deal is the gameplay** — every screen element either informs a decision
   or is a move in one.
2. **Information is loot** — shallow intel earned with Social, deep intel FOUND
   as protocol-droid modules and fitted to a droid you keep alive.
3. **Deterministic first, voiced second** — every price, crit and rumor is
   seeded C# math before any LLM sees it; banter only narrates what already
   happened (the two Oracle laws, inherited verbatim).
4. **Read-side economy** — the price engine touches nothing global: no
   MarketValue hook, no wealth/raid-point drift; it exists only inside The
   Bazaar's read path.
5. **Ours is the window others extend** — a typed plugin contract so future mods
   (cuisine flags, RimProperty fencing, rumor goods) plug in instead of forking.

## 2. Window architecture

**Replacement seam (VERIFIED against decompiled 1.6 source).** All eight vanilla
trade entry points construct `Dialog_Trade` and push it via
`Find.WindowStack.Add(...)`: `IncidentWorker_CaravanMeeting`,
`JobDriver_TradeWithPawn`, `TradeShip` (comms), `CaravanArrivalAction_Trade` +
`CaravanVisitUtility`, `TransportersArrivalAction_Trade`, and the two gift sites
(`CaravanArrivalAction_OfferGifts`, `FactionGiftUtility`, `giftsOnly: true`).
Replacement: **one Harmony prefix on `WindowStack.Add`** — if the window
`is Dialog_Trade` and not ours, substitute `RM_Window_Bazaar`, a `Dialog_Trade`
SUBCLASS so any mod holding a `Dialog_Trade` reference still type-checks. This
catches all eight sites plus modded callers without touching them. VERIFY at
quicktest: MultipleTraders' picker and Trader Ships' trade action both end in
vanilla `Dialog_Trade`. **Gift mode (owner-ruled): The Bazaar with haggling
greyed** — one window everywhere; gifts show grid + intel, no duel.

**Session plumbing.** Vanilla `TradeSession`/`TradeDeal`/`Tradeable` stay intact
— TraderGen, Better Traders, GTG junk stock and Trader Ships shape
`ITrader.Goods` and vanilla `TradeDeal` consumes it, so their stock arrives
untouched. Our prices apply via a **session-guarded Harmony postfix on the
virtual `Tradeable.GetPriceFor`** (verified virtual): outside our window it is a
no-op boolean check; inside it, price = vanilla × settlement multiplier (§3) ×
haggle delta (§5). Vanilla `ResolveTrade`/`TryExecute` call `GetPriceFor`, so
haggled prices are real at execution with zero rewrite of trade execution.

**Layout — three tabs** (def-driven):

- **Goods** — the grid: searchable, sortable, column-configurable over the live
  `TradeDeal.AllTradeables`, virtualized rows (599-mod stocks are huge), column
  presets save/load, wishlist stars inline (absorbs TradeHelper's UX).
- **Broker** — bulk liquids (the liquids framework's broker interface lives
  HERE; merge target of FlowWorks' hardware step — was Liquid Logistics, absorbed 2026-09-16): rows are (LiquidDef, amount in
  reachable universal tanks / trader capacity), both directions, price = row
  marketValue × amount × settlement multiplier. Greys out with a one-line reason
  when no tank is in range or FlowWorks is absent (was Liquid Logistics, absorbed 2026-09-16).
- **Ledger** — relationship memory: this trader's history with you, watchlist,
  session rumor log, haggle-lockout status.

**Plugin contract** (ours to own):

- `RM_BazaarColumnDef` + `BazaarColumnWorker`: `DrawCell(Rect, Tradeable,
  BazaarSession)`, `Compare`, `GetTooltip`, `VisibleFor(session)` (intel gating
  lives here).
- `RM_BazaarBadgeDef` + `BazaarBadgeWorker`: stacked row icons (good-deal,
  colony-need, scarcity, provenance) — `GetBadge(Tradeable, session)`.
- `RM_BazaarTabDef` + `BazaarTabWorker`: `ShouldShow(session)`,
  `DoTabContents(Rect)`.
- `RM_BazaarIntelLayerDef`: names a gate (Social band or droid module) that columns
  and badges reference — one place to rebalance gating.

**Drawing.** IMGUI throughout; reuse vanilla `Widgets`/`GenUI`/`Text` and the
vanilla confirm/execute path (`TradeSession.deal.TryExecute`). VERIFY whether
`TransferableUIUtility`'s counter arrows are cleanly reusable or need
reimplementing. Custom-drawn: virtualized grid body, patience meter (segmented
bar), badge strip, banter strip, broker rows.

## 3. Price engine — `RM_BazaarEconomy` (read-side only)

- **`WorldComponent RM_BazaarEconomy`**, scribed in the save.
- **Multiplier store**: sparse `settlementTile → (PriceKey → float)`, where
  `PriceKey` is a tradeTag/ThingCategory BUCKET with per-ThingDef overrides only
  where a tag targets a specific def (water, liquids). Buckets keep memory sane
  on a 599-mod item pool. Orbital/roaming traders resolve to their faction's
  nearest settlement tile, else a global bucket.
- **Seeding**: at init, read the liquids framework's authored worldTag store
  plus RimUtinni settlement economy tags; XML rule table
  (`RM_BazaarSeedRuleDef`): desert-tagged settlement seeds water ×1.8–2.6,
  brine-adjacent seeds salt cheap, propane-lake seeds fuel cheap. The world is
  frozen and hand-authored — seeding is stable and story-true.
- **History ring buffer**: per PriceKey, 32 entries (day, effective multiplier,
  observed offer) written on session open and drift ticks — the raw,
  consumable "vs typical" baseline VTE cannot provide.
- **Trader-visit log**: bounded (day, trader kind, notable stock) list feeding
  scarcity intel.
- **Tick**: one pass per in-game day over seeded buckets only — drift toward
  tag-weighted targets, then mean-revert and clamp per step and per absolute
  band (×0.25–×4.0), VTE's clamp pattern. Event nudges (drought condition, big
  broker sale) push targets; reversion pulls back over days. NO banks, stocks,
  contracts, news.
- **Read path — the whole of it**: `MultiplierFor(settlementTileOrTrader,
  ThingDef)`, called from exactly two places: the guarded `GetPriceFor` postfix
  and intel/broker rendering. Vanilla wealth, raid points, caravan valuations:
  untouched.
- **Tag-absent worlds (public release, owner-ruled): procedural locality** —
  seed buckets from a stable hash of (faction, biome, tile ID); mild believable
  locality, zero authored data. Campaign always uses authored tags. Settings
  also offer flat ×1.0 (engine dormant).

## 4. Intel layers

Bands use the negotiator's Social skill (vanilla has no trade skill;
`TradePriceImprovement` remains the price carrier — verified stat).

| Layer | Gate | Renders | Source |
|---|---|---|---|
| L0 Grid basics | none | item, qty, quality/hp, price, wishlist star | vanilla Tradeable |
| L0 Colony-needs badges | none (it's YOUR colony) | "missing ingredient for 3 recipes", "only medicine: 4 herbal", "needed: Distillation repair" | colony scan: blocked bills, med inventory, WreckedMachines module wants |
| L1 Price context | Social 3+ | arrow + % vs typical, history sparkline | engine ring buffer |
| L2 Good-deal badges | Social 5+ | outlier flags, both directions | price vs baseline |
| L3 Local economy | Social 7+ | "this settlement pays 2.3× for water", best-sell-here hints | multiplier store + tags |
| L4 Scarcity | Social 9+ | "only source of X in 30 days" | trader-visit log |
| S1 Stolen-goods inkling | Social-scaled, no module | "this may be stolen" hint, confidence ∝ how distinct the item is (art, quality, named/unique, rare def) — generic bulk gives nothing | RimProperty ownership records |
| D1 Trader read | droid module `RM_HagglerModule` | personality tag, patience meter AS NUMBERS, crit-odds hint | deterministic personality (§5) |
| D2 Registry | droid module `RM_ManifestDecoder` | goods-origin flavor; definite stolen/lost flag + which owner notices; fall-salvage provenance reads as unowned (safe) | RimProperty lost-and-stolen registry |
| D3 Transponder scan | droid module `RM_TransponderScanner` | reads the transponders goods radiate: stolen/lost flags on a trader's stock before a word is exchanged, and on a settlement's stock at arrival | live transponder emissions; RimProperty |
| D4 Market analysis | droid module `RM_PriceAlmanac` | full history graphs; lowers every Social gate above by 2 | engine, all stores |

**The deep layers are protocol-droid MODULES — droid parts, found, then
fitted through Droidworks' surgery route (`Recipe_InstallDroidPart`), never
carried items** (owner, 2026-09-20: *"This is why you bother with a flaked JPL
combat droid like C-3PO and gives him a reason to exist."*). All four fit on one
droid, installed as you find them; no slot limit. Campaign placement is
RimUtinni data.

- **Presence gate**: a module renders only when a FUNCTIONAL protocol droid
  carrying it is either **in the trading party at the deal** or **at the colony
  working a comms console** for a remote trade (communicators are assumed
  ubiquitous in this world). Either satisfies it.
- **Functional** is the test `Patch_ProtocolTradeAdvantage.cs` already ships
  (`src/RimStarWars/Droidworks/Source/Droidworks/`): a `DW_Family_Protocol`
  chassis (`DroidworksExtension.chassisClass == 1`) that is not dead, downed,
  powered-down (`RSW_DW_PoweredDown`) or imprisoned. Reuse it; do not write a
  second. Live protocol droids: `RSW_DW_Race_OuterRim_ProtocolDroid`,
  `RSW_DW_Race_guy762_DroidRace_GE3PD`.
- **The droid's shipped ±6% trade advantage stays** (`PerSideAdvantage`,
  symmetric — a trader's droid works against you, both-or-neither cancels; owner
  2026-09-06: *"dangerous not to"*). Modules ADD the intel unlocks on top of it.
- **Why the droid is the reader**: protocol droids "speak" the language of trade
  droids — how Star Wars handles databases and data formats.
- `RM_PriceAlmanac` is a market-data-analysis module; `RM_ManifestDecoder` is a
  registry of known lost and stolen goods; `RM_TransponderScanner` (working name, not
  the owner's — he named no def) is a distinct second scanner (transponders,
  not records). Without `RM_HagglerModule` the
  meter is hidden — you haggle *blind*, which is the point.

**Stolen goods — RULED IN, integrated with RimProperty** (owner, 2026-09-20:
*"The stolen goods angle is brilliant and now must be included as integration
with the property mod."*). Stolen goods are cheaper to buy; buying them *"may
gain the wrath of the owner or even raids."* S1 gives the ungated inkling; D2
and D3 give certainty. The player did not fall from space — the fall's wrecks
are someone else's, and knowing a thing is fall-salvage is what makes it safe to
buy. Owner: *"worth its own awesome design pass to expand"* — that pass is owed
and carried by `BAZAAR_STOLEN_GOODS_PROPERTY_1`; this doc records the rulings,
not the mechanics. Lead, not a commitment here: injected wreckage in the fall
zone can seed quests about lost cargo of interest.

## 5. The haggle duel — WHOLE-DEAL (owner-ruled)

**Owner, 2026-09-13: haggling is over the whole deal, not per item** — "haggling
for the whole deal seems really like the only important thing. Otherwise it's
monotonous to do it on each item." So: assemble the basket in the grid, then the
duel happens at the deal stage — confirm-time IS the dramatic moment.

- One trader session holds one **patience meter P** (4–9: base by trader kind ±
  personality, +1 per 25 goodwill band; numbers visible only with D1, else a
  vague face icon at Social 7+). No regen within the session, except completing
  a deal above a silver threshold restores +1 (spending soothes; nudges players
  to actually close).
- **Push** (on the current deal total): success chance
  `p = 0.45 + 0.025×Social − 0.04×log2(dealValue/250) − 0.10×(pushes won this
  deal) + personalityMod`, clamped 0.10–0.85.
- **Success**: the whole-deal balance moves ~3% in your favor (diminishing
  3/2.5/2...), costs 1 patience.
- **Crit** (top 15% of the success band): free (no patience) plus a spoil —
  a freebie thrown into the deal (drawn from the trader's lowest-value junk
  rows — the GTG junk pool shines here, with no GTG dependency) or a **rumor
  token**: a true intel unlock (one D-layer row for this session, or a world
  fact — "drought upriver, water's dear at Kesh crossing" — which is literally
  the engine's multiplier speaking). 50/50, weighted by personality.
- **Fail**: no move, costs 2 patience, trader claws back your last concession.
- **Critical fail** (bottom 5%): patience floors → **session lockout** (haggle
  controls grey until the trader leaves); concessions won so far survive; small
  stinger −2% on the final balance. Patience reaching 0 by ordinary spending =
  lockout, no stinger.
- **Re-basketing** after pushes is allowed; concessions are a % on the deal, so
  they scale with what's in it — but push count (and its diminishing returns)
  does not reset. No per-item micro-loop exists at all.
- **Determinism / anti-save-scum**: every roll seeded from (world seed, trader
  stock seed, push index) — reload and re-push replays identically, the same
  trick vanilla uses for Tradeable price randomness. Said out loud in Settings.
- **XP**: each push grants Social XP (~150; ×2 crit, ×0.5 fail — you learn from
  being laughed at). Traders become a Social training ground.
- **Personality** (deterministic per trader seed; persisted in the Ledger):
  stingy (+2 P, 2% concessions), desperate (−2 P, 5% concessions, worse base
  prices), gullible (+0.10 p, low-grade rumor crits), volatile (10% crit-fail
  band, 20% crit band — the gambler's trader). Repeat traders remember: lockout
  → −1 P next visit; big purchase → +1 P.

## 6. Banter — the fourth Oracle consumer

Rides the `claude -p` subprocess transport (the ruled CLI-only in-game LLM
access; `src/RimMandrake/Oracle/Source/OracleClient.cs`). Both laws hold: text
authority only (banter is display text, never a number, never a def); the game
is whole with the LLM absent (authored line pools per personality × event type
ship FIRST and are the permanent fallback).

- **Prompt**: system = trader persona (personality, faction, settlement
  character) + hard rules (~160 char cap, no invented game terms, in-voice);
  stdin = the deterministic event that already happened ("pushed on a 2,400
  silver deal, failed, patience 2/6") + up to 3 TRUE world facts (top multiplier
  deviations, one scarcity entry, one recent event) + Ledger memory lines.
- **Real intel**: the facts are read from the engine, so flavor lines carry
  usable information, gated only by listening.
- **Async**: fired on haggle events via the Oracle off-tick Task + main-thread
  queue; fallback line shows immediately; a fresh line (timeout ~8s) is used on
  the NEXT exchange; one outstanding call per session; budget N per session
  (default 5) under the Oracle global budget/kill-switch. CLI missing → detect
  once, disable for the save session, pools carry everything, no log spam.
- **Launch posture (owner-ruled): DORMANT until `ORACLE_EXPERIMENT_SPIKE_1`'s
  live proof lands** — the authored pools are the day-one experience; the LLM
  consumer flips on afterward.

## 7. Mod Settings

Dynamic economy (campaign: authored tags / public default: procedural; flat
kills it) · per-layer intel toggles · colony-needs badges · haggling on/off ·
crit spoils on/off · banter (hard off switch; auto-off without CLI) · broker tab
(auto-hidden without FlowWorks) · wishlist flash · grid presets/density.
**All-off = a plain good trade grid.** Defaults = shipped behavior.

## 8. Displacement & compat

**Deactivate when The Bazaar lands** (a mod-list change scheduled with the
owner, rimworld-start-prep discipline — and only AFTER absorbing what each
does well, per the owner): Trade UI Revised and Vanilla Trading Expanded.
(Utility Columns was wrongly listed here at first — it is a BUILDING mod,
structural roof-bearing columns, despite its `nephlite.orbitaltradecolumn`
packageId; it stays untouched.) **VTE unwind**: it substitutes MarketValue globally
and holds state in its own components — mid-save removal snaps prices to
vanilla (wealth/raid points will step visibly for a few days) and the next load
logs missing-component Scribe warnings — **rehearse on a save copy first**
(UNCERTAIN until rehearsed; read the component class names from the VTE
assembly before judging the save safe). TradeHelper stays inactive (wishlist
absorbed).

**The tier crossing — owner-ruled 2026-09-20: generic concept, Star Wars
body.** The D-layers are not "protocol droid" features at the RimMandrake tier.
The Bazaar owns the ABSTRACT role — *a machine that can negotiate for you*,
carrying module slots and a liveness test — and ships it as a def other mods
register against. The protocol droid is what FILLS that role in this campaign;
another game could fill it with something else entirely, and the generic mod is
not poorer for lacking Star Wars. The role def's name is owed (it does not
exist yet); do not invent one in passing.

- **RimMandrake side** (`mandrake.rm.bazaar`): the role def, the four module
  slots, the presence gate's shape (at the deal OR on a comms console), and the
  D-layer rendering.
- **RimStarWars side** (`mandrake.rsw.droidworks`): registers the
  `DW_Family_Protocol` chassis against the role, supplies the shipped
  functional test and the ±6% advantage, and owns the part surgery. Trade droids
  on the other side of the deal stay Droidworks' concern.
- **RimProperty** (`mandrake.rm.property`) carries S1/D2/D3's ownership records.

With no mod registering the role, the D-layers do not render and Settings says
why; with RimProperty absent the stolen-goods rows do not render. Soft
references (`MayRequire`), never hard dependencies, in both directions.

**Keep**: TraderGen, Better Traders, GTG junk framework, MultipleTraders,
Trader Ships — they shape stock and arrivals, not UI; we consume vanilla
`TradeDeal` from whatever they generate and intercept only at `WindowStack.Add`
plus the session-guarded postfix. We never regenerate stock, never patch
StockGenerators or their incident workers.

## 9. Phasing (each slice lands + quicktests alone)

1. **Window + grid parity** *(opus — the Harmony seam and IMGUI grid are the
   risk surface)*: intercept, subclassed window, virtualized grid,
   sort/search/presets, wishlist, gift mode, Settings skeleton. Test: quicktest
   colony; open orbital + visiting-pawn + caravan-settlement trades; buy and
   sell with silver math identical to vanilla; the five kept trade mods still
   function.
2. **Price engine + intel** *(opus for the engine; column workers sonnet)*:
   `RM_BazaarEconomy`, worldTag seeding, ring buffer, drift tick, guarded
   postfix, L0–L4 columns/badges, the four modules as Droidworks parts with the
   presence gate (placement stub; stolen-goods mechanics wait on
   `BAZAAR_STOLEN_GOODS_PROPERTY_1`). Test: authored-tag fixture — water reads
   ~2× at a desert settlement; save/load round-trips; vanilla wealth readout
   unchanged; a module renders with a functional droid in the caravan or at a
   comms console, and not with the droid downed, powered-down or left home.
3. **Whole-deal haggle duel** *(opus for tuning)*: patience, push resolution,
   crits/freebies/rumor tokens, lockout, XP, personalities, Ledger memory,
   deterministic seeding. Test: scripted push sequences replay identically
   across save/reload; lockout greys; XP ticks.
4. **Broker tab**: merge of FlowWorks' hardware step (gated on the universal
   tank existing). Test: tank of water + trader in range → sell 100 units at
   value × amount × multiplier; tab hidden without a tank.
5. **Banter** *(opus — prompt/validation quality is the product)*: authored
   pools FIRST (complete feature alone), then the dormant Oracle consumer.
   Test: pools fire on every event type with CLI absent; with CLI present, the
   stub-marker discrimination trick proves real delivery vs fallback.

## 10. Rulings log (owner, 2026-09-13)

Haggle = whole-deal only (per-item rejected as monotonous) · banter dormant
until Oracle proof · public seeding = procedural locality · gift mode = Bazaar
with haggle greyed · economy = own engine, VTE rejected and scheduled for
deactivation · intel gating = Social + found deep intel (its carrier reworked
2026-09-20, below) · build order = grid+intel → duel → broker → banter.

**2026-09-20 (bench sitting).** Deep intel = protocol-droid MODULES, not carried
artifacts (*"gives him a reason to exist"*) · fitted via `Recipe_InstallDroidPart`
· gate = functional droid present at the deal OR working a comms console for a
remote trade (communicators ubiquitous) · "functional" = the shipped
`Patch_ProtocolTradeAdvantage` test, no new one · ±6% advantage stays, modules
add on top · all modules on one droid, no slot limit · almanac REPLACED by a
market-data-analysis module, same function (pre-collapse book fiction dead) ·
stolen goods RULED IN with RimProperty: ungated Social inkling ∝ item
distinctiveness, stolen = cheaper, owner wrath up to raids, decoder = registry of
lost/stolen goods, a distinct second scanner reads transponders on traders and
settlements, fall-salvage reads as safe · *"The player didn't fall from space"* ·
stolen-goods design pass owed → `BAZAAR_STOLEN_GOODS_PROPERTY_1` · lead only:
fall-zone injected wreckage → lost-cargo quests · tier crossing = generic
concept, Star Wars body: The Bazaar owns the abstract negotiator role,
Droidworks registers the protocol droid against it (§8).
