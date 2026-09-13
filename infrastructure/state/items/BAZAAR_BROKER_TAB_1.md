# BAZAAR_BROKER_TAB_1 — the bulk-liquid Broker tab (slice 4)

Filed by BENCH, 2026-09-13. Spec: `design/RimMandrake/bazaar_trade_window_design.md`
§2 (Broker tab) — this is the merge target of the liquids framework's broker
ruling (LIQUID_LOGISTICS_MOD_1 step 5 renders here; Logistics owns the
hardware and data API, this tab owns the UI).

## spec

`RM_BazaarTabDef` Broker: rows of (LiquidDef, amount in reachable universal
tanks / trader capacity), BOTH directions (pump-to-sell, pay-to-fill), price =
row marketValue × amount × settlement multiplier from RM_BazaarEconomy. Tab
greys with a one-line reason when no tank/manifold in range or Liquid
Logistics absent; The Bazaar never hard-requires Liquid Logistics.

## verify

Quicktest: tank holding water + trader in range → sell 100 units, silver =
value × amount × multiplier exactly; buy direction fills the tank and debits
silver; tab hidden without a tank; The Bazaar loads clean with Liquid
Logistics absent.

## Watch out

- Depends on BAZAAR_WINDOW_GRID_1, BAZAAR_PRICE_ENGINE_1, and
  LIQUID_LOGISTICS_MOD_1's tank + API existing.
- Cross-mod seam: reference Logistics types via its API/defNames only —
  MayRequire-soft, no assembly hard-reference unless the API forces it.
