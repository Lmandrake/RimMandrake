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

### Exact checks 2026-10-09 (acceptance sitting)
- A1 CHECK: `jawa/get_defs defs="ThingDef/RM_PriceAlmanac;ThingDef/RM_HagglerModule;ThingDef/RM_ManifestDecoder;ThingDef/RM_TransponderScanner;HediffDef/RM_PriceAlmanacFitted;HediffDef/RM_HagglerModuleFitted;HediffDef/RM_ManifestDecoderFitted;HediffDef/RM_TransponderScannerFitted;RM_BazaarSeedRuleDef/RM_BazaarSeed_DesertWater;RM_BazaarSeedRuleDef/RM_BazaarSeed_BrineSalt;RM_BazaarSeedRuleDef/RM_BazaarSeed_PropaneFuel;RM_BazaarSeedRuleDef/RM_BazaarSeed_BoilingSeaStill" fields="defName"` (seed rules are `RimMandrake.Bazaar.RM_BazaarSeedRuleDef` in TheBazaar/Defs/Economy/RM_BazaarSeedRules.xml; if get_defs rejects the short type name use the full class name). Price store: `jawa/type_probe typeName="RimMandrake.Bazaar.RM_BazaarEconomy"` resolved=true. Settings: `jawa/mod_settings_field typeName="RimMandrake.Bazaar.RM_BazaarSettings" action=list` returns the 7 booleans/fields (economyEnabled, proceduralLocality, intelPriceContext, intelGoodDeals, intelLocalEconomy, intelScarcity, intelModules). `jawa/drain_log limit=400 errorsOnly=True` (or Player.log) filtered for `Bazaar|RM_Bazaar` PASS: success=true, foundCount=12, notFound empty; type_probe resolved=true; list shows all 7 named fields; zero error lines naming the Bazaar. FAIL: success=false (UNMEASURED, not absent), notFound non-empty, or foundCount short, resolved=false (DLL not loaded), fewer than 7 fields, or any error line naming RM_Bazaar*.

## Watch out

- Depends on BAZAAR_WINDOW_GRID_1; seeding reads WORLDMAP_LIQUID_TAGS_1's
  store when it exists — design a null-tolerant seam, do not block on it.
- Never hook MarketValue/StatWorker — that is the rejected VTE blast radius.
- The dump has no statBases (def-dump blind spot): calibrate "typical price"
  baselines from live values, not the offline dump.

## built offline (2026-10-06, uncommitted at time of writing)

In `src/RimMandrake/TheBazaar`: `Source/Economy/` (RM_BazaarEconomy WorldComponent — lazy per-tile seeding,
32-entry history ring, trader-visit log, daily drift with ±10%/day step clamp and ×0.25–×4.0 band;
RM_BazaarSeedRuleDef; RM_BazaarTags with a null-tolerant FlowWorks liquid-tag seam by reflection and a
provider registry for RimUtinni settlement tags; RM_Patch_GetPriceFor postfix guarded on
`RM_BazaarSession.Current`), `Source/Intel/` (gate evaluation reusing Droidworks'
`IsAvailableProtocolDroid` by reflection; L1–L4 column/badge workers), `Defs/` (4 seed rules, 8 intel
layers, 2 columns, 2 badges, 4 module items + fitted hediffs), 7 settings toggles. Builds clean.

Deviations from this item's 2026-09-13 text, following the later owner ruling in the design (§4, 2026-09-20):
the "three artifacts" are FOUR protocol-droid MODULES (adds `RM_TransponderScanner`), gated on a fitted hediff,
not on a carried item.

Still owed: (1) the module install RecipeDef — design routes it through Droidworks' `Recipe_InstallDroidPart`
(RSW tier), so it belongs in the Droidworks layer, not here; (2) L0 colony-needs badges (not built);
(3) everything in `## verify` — the postfix cannot act until the WindowStack.Add intercept
(BAZAAR_WINDOW_GRID_1) constructs `RM_Window_Bazaar`, which raises the session guard.
