# WORLD_PORT_SURVIVES_BRIDGE_1 — the read half is PROVEN; the write half is deliberately not run

2026-08-26, seat CHECK, live Ash'karr, full 582-mod list. **Nothing was written to the world.**

## The instrument, and why it cannot be fooled

`jawa/world_tile_validate` compares the live world against a CSV and **reads RAW tile fields**
(`readRawFields: true`), never `HillinessLabel` / `Min-MaxTemperature` / cached `Biomes` — the
lazily-cached properties that have no reset anywhere in RimWorld and would confirm writes that
never landed. That is exactly the trap this item warns about, and the tool is built against it.

## CONTROL — export → validate is lossless

```
world/_lf/live_tiles.csv (exported minutes earlier)
rows 21872   matched 21872   mismatched 0   matchPct 100.0   tolerance 0.5   readRawFields true
```

⇒ **21,872 of 21,872, zero drift.** The per-tile scalar path out of the game and back into a
comparison is exact. A count that merely matches is not the criterion, and this is not a count —
it is a per-tile field comparison over the whole planet.

## The authored bundles differ, and every difference is EXPLAINED

```
_final    2026-08-25 08:25   matched 14472  mismatched 7400   byField {hilliness 7303, biome 140}
VIVIFIED  2026-08-24 08:38   matched 14364  mismatched 7508   byField {hilliness 7303, biome 278}
DRAFT     2026-08-24 01:23   matched 14362  mismatched 7510   byField {hilliness 7305, biome 284, elevation 6}
```

🔑 **The hilliness column is the 2026-08-26 hilliness pass**, which `world/audit_2026-08-26/README.md`
records as **7,315 tiles changed** — 7,303 of them present in these bundles. Sample diffs are
`hilliness: Flat!=SmallHills`, `LargeHills!=SmallHills` — one class, one cause. The biome deltas
shrink monotonically with bundle age (284 → 278 → 140), which is what an accumulating authoring
history looks like. ⇒ Differences accounted for; no unexplained drift.

## The live world is internally sound — the faults that only appear after a save/load

```
world_links_validate     21872 scanned | river 652 / road 2798 entries | 335 river tiles
                         asymmetric 0   nonAdjacent 0   hiddenByBiome 15
                         landlocked river tiles 309 - ruled acceptable (low-accumulation rivers
                         MAY die in playas; only high-accumulation trunks must reach a sea)
world_objects_validate   196 objects | 96 settlements | nullFactionSettlements 0
                         badTile 0 | onWater 0 | onImpassable 0 | stacked 0
world_cache_audit        staleTotal 0        tile_cache_audit  unexplainedStale 0
world_mutators_audit     13,569 tiles with mutators | offenderCount 0
world_lint               22 findings (unchanged from the 2026-08-26 authoring session)
```

🔑 **`nullFactionSettlements: 0` is the important zero.** A Settlement with a null faction is
destroyed by Scribe on load with only a warning — the one fault that is invisible until it is too
late. All 96 are clean.

## ⛔ The WRITE half was NOT run, and that is a decision, not an omission

`jawa/world_tile_import` dry run against the VIVIFIED bundle:
`{"dryRun": true, "rows": 21872, "applied": 21872, "skipped": 0}` — a port would address every
tile and skip none.

I did not run it with `apply: true`. **`ASHKARR_WORLD_DEFINITION.md` §12.4 rule 3 forbids the
importer to write while a map is instantiated**, because painting a planet under an instantiated
map is what destroyed the save twice — and `rimworld/get_game_info` reports `mapCount: 1`. Running
it anyway on the owner's authored planet, while he is away, to gain one criterion, is the wrong
trade: a corrupted Ash'karr costs many sessions of hand authoring.

## What would finish this item

The import half must run **at the world screen with no map instantiated**. ⚠️ Per this item's own
note of 2026-08-23, **the bridge cannot reach the world-creation page at all**
(`BRIDGE_CANNOT_MAKE_A_WORLD_1`) — `Page_CreateWorldParams` needs a Game object that does not exist
in the Entry scene, and the main menu's buttons are immediate-mode GUI that nothing enumerates.
⇒ It needs the owner's hands, or a save loaded to the world screen with the map discarded.

## ⚠️ And a premise of this item has gone stale

The item says *"the map is being authored OUT OF GAME with DECIDE"*. It is not, any more.
`world/ASHKARR_VIVIFIED_provenance.json` names its own source as *"live bridge harvest of Ash'karr
(seed raven)"* — the bundles are **exports of the live world**, not an independently authored
source. So a bundle-vs-live diff is partly circular by construction, and the CONTROL above is the
honest form of it. Whether an out-of-game source still exists is a question for DECIDE.
