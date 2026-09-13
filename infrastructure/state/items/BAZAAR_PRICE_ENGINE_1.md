# BAZAAR_PRICE_ENGINE_1 — read-side economy + intel layers (slice 2)

Filed by BENCH, 2026-09-13. Spec: `design/RimMandrake/bazaar_trade_window_design.md`
§3 (engine) + §4 (intel). model: opus for the engine; column workers may be
sonnet.

## spec

`WorldComponent RM_BazaarEconomy`: bucket-keyed multiplier store
(settlementTile → PriceKey → float), seeded from the liquids framework's
authored worldTags + RimUtinni settlement tags via `RM_BazaarSeedRuleDef`;
32-entry history ring per bucket; trader-visit log; daily drift tick with
mean-reversion clamp (×0.25–×4.0 band — VTE's clamp pattern, nothing else of
VTE). READ-SIDE ONLY: a session-guarded postfix on `Tradeable.GetPriceFor`
(no-op outside The Bazaar) and the intel/broker renderers are the only two
consumers — vanilla wealth/raid points must be provably untouched. Intel
layers L0–L4 as columns/badges gated per §4; the three artifacts as items
(`RM_PriceAlmanac`, `RM_HagglerModule`, `RM_ManifestDecoder`) with campaign
placement stubbed (RimUtinni owns placement). Public/tag-absent seeding:
procedural locality hash (owner-ruled).

## verify

Quicktest with an authored-tag fixture: water reads ~2× at a desert-tagged
settlement and normal elsewhere; save/load round-trips the component; the
colony wealth readout is IDENTICAL before/after enabling the engine (the
read-side guarantee, checked, not assumed). Artifact-gated columns appear only
when the artifact is carried.

## Watch out

- Depends on BAZAAR_WINDOW_GRID_1; seeding reads WORLDMAP_LIQUID_TAGS_1's
  store when it exists — design a null-tolerant seam, do not block on it.
- Never hook MarketValue/StatWorker — that is the rejected VTE blast radius.
- The dump has no statBases (def-dump blind spot): calibrate "typical price"
  baselines from live values, not the offline dump.
