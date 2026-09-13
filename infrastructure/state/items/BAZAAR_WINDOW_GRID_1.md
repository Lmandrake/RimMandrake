# BAZAAR_WINDOW_GRID_1 — The Bazaar window + grid parity (slice 1)

Filed by BENCH, 2026-09-13. The Bazaar is ruled:
`design/RimMandrake/bazaar_trade_window_design.md` — read §2 (architecture)
before anything. model: opus (the Harmony seam and IMGUI grid are the whole
risk surface).

## spec

New mod `src/RimMandrake/TheBazaar/` (`mandrake.rm.bazaar`). `RM_Window_Bazaar`
subclasses `Dialog_Trade`; ONE Harmony prefix on `Find.WindowStack.Add`
substitutes it for any vanilla `Dialog_Trade` (catches all eight vanilla spawn
sites + modded callers). Vanilla TradeSession/TradeDeal/Tradeable untouched.
Virtualized, searchable, sortable, column-configurable grid over
`TradeDeal.AllTradeables` with save/load presets and inline wishlist stars;
gift mode = same window, haggle area absent/greyed. Plugin def types ship now:
`RM_BazaarColumnDef`/`BadgeDef`/`TabDef`/`IntelLayerDef` + workers. Mod
Settings skeleton. NO pricing changes in this slice — silver math must be
byte-identical to vanilla.

## verify

Quicktest: open orbital (comms), visiting-pawn, and caravan-settlement trades;
execute a buy and a sell; totals identical to vanilla for the same basket.
Confirm the five kept trade mods still function (TraderGen, Better Traders,
GTG junk stock appears in grid, MultipleTraders picker ends in our window,
Trader Ships trade action opens it). Gift flow opens greyed.

## Watch out

- VERIFY at quicktest that MultipleTraders and Trader Ships construct vanilla
  `Dialog_Trade` (the intercept assumes it).
- VERIFY whether `TransferableUIUtility` counter arrows are reusable or need
  reimplementing.
- Trade UI Revised is ACTIVE in the campaign list and patches the same dialog —
  during dev, test on a minimal list WITHOUT it; the displacement pass
  (BAZAAR_DISPLACEMENT_PASS_1) handles the campaign list.
