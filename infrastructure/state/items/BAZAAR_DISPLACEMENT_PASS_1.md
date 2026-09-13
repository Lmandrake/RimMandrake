# BAZAAR_DISPLACEMENT_PASS_1 — retire Trade UI Revised and VTE from the campaign list

Filed by BENCH, 2026-09-13. Spec: `design/RimMandrake/bazaar_trade_window_design.md`
§8. needs: owner (a campaign mod-list change is his call and his RimSort
session; rimworld-start-prep discipline applies).

## spec

When The Bazaar's slices 1–2 are live-proven AND their useful behaviors are
absorbed (owner: retire only after we absorb what we need and improve it):
deactivate Trade UI Revised (hobtook.tradeui) and Vanilla Trading Expanded
(vanillaexpanded.vanillatradingexpanded). NOT Utility Columns
(nephlite.orbitaltradecolumn) — despite the packageId it is a BUILDING mod
(structural roof-bearing columns), no trade UI at all; leave it. KEEP TraderGen,
Better Traders, GTG framework, MultipleTraders, Trader Ships. TradeHelper
stays inactive.

**VTE unwind rehearsal is the real work**: on a COPY of the current save,
remove VTE, load, and record: (a) the wealth/raid-point step when its global
MarketValue substitution vanishes, (b) the missing-component Scribe warnings
and whether the save is clean afterwards, (c) any third-party mod that turns
out to reference VTE (grep About/loadAfter + Patches across the active list
first). Read VTE's actual component class names from its assembly before
judging — do not hand-edit the save on guesses.

## verify

The rehearsal save loads clean post-removal and plays a day without errors;
wealth step measured and reported to the owner BEFORE the real list changes;
ModsConfig.xml diff shows exactly the three deactivations and nothing else.

## Watch out

- ModsConfig describes the NEXT load; RimSort needs Refresh + Save (closing
  the window writes nothing); Steam may defer while the game runs.
- Do this against the FULL list, not the minimal harness list — the trap that
  produced the modsconfig-stale-list false root cause before.
