# Biome Owed-Work Audit — 2026-09-20

Sheets audited (10): nightside_ice, forsaken_crags, desert, deep_desert, arid_shrubland,
wasteland, the_cracked_lands, fall_line, weeping_stones, dune_sea.

Method: per CLAUDE.md instructions in the task brief. Status: IN PROGRESS — filling in one
sheet at a time, writing after every sheet.

## nightside_ice.md

Owed section (5 bullets) split into 7 work items:

1. **`NIGHTSIDE_ICE_DEF_1`** (author `RUT_NightsideIce`, paint tiles, register in world
   tools) — **FILED, closed/done** (`show NIGHTSIDE_ICE_DEF_1`: state `done`, closed
   `064d8c99d`). Both halves (def + paint) landed. ⚠️ **STALE-ITEM FLAG (CONFIRMED)**: the
   item's spec and closing note say it painted **802 tiles**; the sheet's own §0 says
   **MEASURED live on V26 (2026-09-08): 1,506 tiles**, an amendment on top of an "old
   1,406" baseline — both numbers already above the item's 802. The sheet and the item
   disagree by ~700 tiles and neither says which is authoritative; did not re-measure the
   live def myself (would need the offline dump, out of scope for a report-only audit) —
   flagging the disagreement per the brief's instruction, not resolving it.
2. **Name for the dirty-ice plateau** — owner's-pick placeholder, not a build item.
   UNCERTAIN whether this needs its own ledger entry at all (it's a one-word decision, not
   authored work); not ranking it as a finding.
3. **Tunnelers and icy insects, authoring** — **UNFILED (CONFIRMED)**. This is further
   along than a bare Owed bullet: `BIOME_FAUNA_ASSIGNMENT_SITTING_1` (closed item, sitting
   2026-09-10) COMMISSIONED "tunneler warren creature, inclusion-insect swarm,
   aurora-current feeder" for nightside_ice by name, and
   `design/Jawa/worldbuilding/creatures/RUT_ruled_commissions_wave2.md` (2026-09-10, Fable
   design brief) fully specced all three as **vhorr** (`RUT_Vhorr`, the tunneler warren
   creature), **chittik** (`RUT_Chittik`, the inclusion-insect swarm) and **ilverr**
   (`RUT_Ilverr`, the aurora-current feeder) with full mechanic briefs (§2–§4). That doc's
   own header states: *"status: design brief — nothing here is built except where a row
   says so"* — and no row says so. No ledger item names vhorr/chittik/ilverr or "nightside
   commissions wave 2." No defs exist in `src/`.
   Searched: `vhorr`, `RUT_Vhorr`, `chittik`, `RUT_Chittik`, `ilverr`, `RUT_Ilverr`,
   `tunneler warren`, `inclusion-insect`, `aurora-current`, `nightside_ice` fauna build,
   `commissions_wave2` — across both `infrastructure/state/items/` and `.../closed/` and
   `src/`. Only the commissioning sitting and the design brief itself turn up; zero build
   item, zero def.
   **Net effect: `RUT_NightsideIce`'s `wildAnimals` list is deliberately empty by design
   (per `NIGHTSIDE_ICE_DEF_1`'s own spec — "no wildAnimals, the arctic zoo is evicted")
   and nothing has filled it since** — the biome ships with zero native fauna today,
   same shape of gap as the Blue Desert, just not yet noticed because the def itself
   "closed."
4. **Events as incident defs** (thaw pulse, calving delivery, the lost soul,
   rime-fall/ablation, the Dark drifting over — 5 items from the §4b equivalence table)
   — **UNFILED (CONFIRMED)**. No ledger item and no defs.
   Searched: `thaw pulse`, `calving delivery`, `lost soul`, `rime-fall`, `ThawPulse`/
   `CalvingDelivery`/`LostSoul` (defName-style) — none found in items, closed items, or
   `src/`.
5. **Engine feasibility pass** (crevasse/collapse hazard with warning tells, thaw pulse as
   a temperature-driven map event, inclusions as a calving spawner) — **UNFILED
   (CONFIRMED)**, same search as #4 (crevasse/collapse mechanics are the same missing
   incident-def work, just the "is this buildable" half of it).
6. **Cross-flow ledger** (documenting the katabatic-wind/aurora/Dark/emergence links to
   neighbour sheets) — this is a documentation cross-reference, not a build item; did not
   chase a ledger ID for it, UNCERTAIN whether it needs one.

## forsaken_crags.md
(pending)

## desert.md
(pending)

## deep_desert.md
(pending)

## arid_shrubland.md
(pending)

## wasteland.md
(pending)

## the_cracked_lands.md
(pending)

## fall_line.md
(pending)

## weeping_stones.md
(pending)

## dune_sea.md
(pending)
