# SHOKKWEAVE_SOLE_SOURCE_1 — Shokkweave economy (rename, trader strip, harvest routes)

Queue line: rename hyperweave game-wide, strip it from EVERY trader stock
table (prove against live trader generation), add the three Webwork harvest
routes (web-cutting, butchery, nest raid).

## Ruled input — 2026-09-11 card sitting (the boundary question)

**Border-map creep-web YIELDS, with teeth.** Owner-verbatim: "(2) but it has
a small chance of SPAWNING an emergent Shokk to get you." Cutting creep-web
on a border map is a real in-biome harvest route — supersedes the webwork
kit's no-yield-variant placeholder — and each cut carries a small chance of
spawning an emergent Shokk. The spawn hook lands with `SHOKK_RSW_MOD_1`
(the Shokk is its own RSW-tier mod, same sitting); this item wires the
yield side. Does NOT change the other three harvest routes or the trader
strip.

## spec
(unchanged from the queue line; see `webwork_kit_spec.md` "Owner rulings"
item 4 and the sole-source constraints block for the boundary contract)

## verify
Live trader generation shows zero hyperweave/Shokkweave stock; border-map
creep-web cut yields Shokkweave and can spawn the emergent Shokk.

## 2026-09-11 update — build-order step 1 shipped, live proof PARTIAL

**Built** (`src/RimUtinni/ShokkweaveEconomy/`, deployed, enabled in
`ModsConfig.xml`): rename, tradeability strip, quest-reward tag strip,
`ExoticMisc` tag strip, stuff-commonality 0.1→0.05, Wyyyschokk butcher yield
(15). Every xpath confirmed matching live via `validate_patch.py --live`
before shipping (caught the `tradeability` field-doesn't-exist-in-XML trap:
`PatchOperationAdd`, not `Replace`). All 4 files reviewed and marked CLEAN.

**Live-confirmed this session** (`jawa/get_def` on `Hyperweave`, full
591-mod list, game UP): `label: "shokkweave"`, new `description` text,
`tradeability: "Sellable"`, `tradeTags: []` — all four read back correctly
from the RUNNING game, not just the XML on disk. Five expected "Hyperweave
tradeability doesn't allow traders to sell this thing" config errors also
appeared for exactly the five SingleDef trader kinds the spec predicted
(`AM_AncientLogisticsSystem`, `guy762_BaseTraderKind_Czerka`,
`guy762_TraderKind_Czerka`, `guy762_BaseTraderKind_HuttGalleon`,
`guy762_TraderKind_HuttGalleon`) — this is the mechanism working as
documented, not a bug.

**NOT done this session** (honest gap, not swept under anything): the
spec's own proof standard — bridge/dev-mode generation of all 11 named
trader kinds, N≥20 rolls each, asserting zero stock — was not run. No
bridge tool exists to generate a specific `TraderKindDef`'s stock list
directly (checked `rimbridge/run_lua`'s capability surface; it only
composes existing `jawa/`/`rimworld/` tools, none of which do this), and
building one is its own `rimbridge-companion` cycle, out of scope for
tonight. Also not attempted: quest-reward roll pass, live butchery spawn
test (relying on the def-state read + `validate_patch.py --live` instead),
and steps 3/4 (web-cutting/nest-raid/border-creep-web yields — block on
unbuilt roster ThingDefs, unchanged from the offline build note).

**Criteria status**: the mechanism is verified correct by direct live def
read and by RimSage source analysis of `TradeabilityUtility`/
`StockGeneratorUtility` (done during the build, see the patch file's own
comments) — but the item's own stated verify line ("live trader generation
shows zero stock") is not yet independently exercised end-to-end. Leaving
`doing`, not closing, until either that tool gets built or someone accepts
the def-state + source-analysis proof as sufficient.
