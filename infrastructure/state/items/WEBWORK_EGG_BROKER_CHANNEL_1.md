## spec

Design: `design/Jawa/worldbuilding/biomes/webwork_egg_blackmarket_2026-09-24.md`
§1b point 2 — the Bazaar's broker tab as the black market's *selling* channel
("the smuggler's jackpot cashes out without waiting for a caravan roll").

**Why this is split out of `WEBWORK_EGG_BLACKMARKET_BUILD_1`:** checked the
actual state of `mandrake.rm.bazaar` before building against it (per
`check-for-existing-generated-art`-style discipline, applied to code): the
Bazaar tab SYSTEM does not exist to extend yet.

- `RM_BazaarTabDef` / `BazaarTabWorker` (`src/RimMandrake/TheBazaar/Source/
  Defs/RM_BazaarTabDef.cs`) is the plugin-def SHAPE only — zero concrete
  `RM_BazaarTabDef` instances and zero `BazaarTabWorker` subclasses exist
  anywhere in the repo (MEASURED via grep, 2026-09-26).
- `RM_Window_Bazaar` (`Source/RM_Window_Bazaar.cs`) is a bare `Dialog_Trade`
  subclass with no `DoWindowContents` override and — its own header says so —
  **is not even wired to `WindowStack.Add` yet**. No tab, grid or haggle UI
  has ever been drawn.
- `RM_BazaarSession` is an intentionally empty marker class; the memory note
  "bazaar-trade-window-ruled" describes the RULING (broker is a Bazaar tab,
  question-card decision 2026-09-13), not built code.
- `BAZAAR_WINDOW_GRID_1` (owner: `mandrake.rm.bazaar` slice 1) is itself still
  `doing` — plugin def scaffolding + the bare window subclass only. Its own
  About.xml says outright: "NOT YET SHIPPED: the WindowStack.Add Harmony
  intercept ... the virtualized grid body, the price engine, the haggle duel."

Building a tab worker against this now would be code with nothing to plug
into and no way to exercise it — `validate_patch.py` cannot check a C# UI
class, and there is no live game surface to click. Per the build item's own
instructions ("don't force a fragile quest/UI implementation you can't
validate offline"), this is deferred rather than forced.

**What this item owes once it is buildable** (i.e. once `BAZAAR_WINDOW_GRID_1`
or a successor ships a working tab-worker slice with at least one real tab
drawing real content):

1. A concrete `RM_BazaarTabDef` instance, e.g. `RUT_BazaarTab_EggBroker`
   (campaign-tier — Hutt/black-market content is IP-gated to `RUT`, same
   Q11/Q11a reasoning as the rest of this design), with a `workerClass`
   subclassing `BazaarTabWorker`.
2. `ShouldShow(RM_BazaarSession)` gates on: campaign layer loaded
   (`mandrake.rut.shokkweaveeconomy` present) AND the current `trader` being
   the Hutt Cartel egg-market kind (`RUT_Caravan_HuttCartel_EggMarket`,
   already built in `WEBWORK_EGG_BLACKMARKET_BUILD_1`) OR a dedicated broker
   context — exact gate depends on what `BAZAAR_WINDOW_GRID_1` ends up
   exposing on `RM_BazaarSession` by then (today it exposes only `negotiator`
   and `trader`).
3. `DoTabContents` draws the sell-your-eggs-for-the-jackpot flow described in
   §1b: a premium payout without waiting for the caravan's `commonality` roll.
   🔴 Re-check the engine-limit note left on `WEBWORK_EGG_BLACKMARKET_BUILD_1`'s
   own patch file (`ShokkweaveEggBlackMarket.xml`) before assuming a price
   premium is free: `TraderKindDef.PriceTypeFor` never returns a non-Normal
   `PriceType` for `TradeAction.PlayerSells` (MEASURED, RimSage, 2026-09-26) —
   a genuine "broker pays more" jackpot needs its own price calculation in the
   tab worker itself (it does not have to run through vanilla `TradeDeal`
   pricing at all, since a Bazaar tab is a custom UI surface, not a
   `Tradeable` row) rather than assuming a `StockGenerator` field will do it.

## verify

No live-game verify is possible until `BAZAAR_WINDOW_GRID_1` (or whatever
supersedes it) has a tab-worker slice to test against. When it does: open the
Bazaar with the Cartel egg-market trader active, confirm the tab appears only
in that context, confirm the payout matches the ruled premium, confirm it
gracefully absent (not crashing) when the campaign layer or that trader isn't
present.
