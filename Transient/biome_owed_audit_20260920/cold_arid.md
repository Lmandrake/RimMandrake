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

Owed section (6 bullets) split into 6 work items (the sitting bullet is one item, not
several):

1. **Frostling joins the roster** — **DONE-BUT-UNRECORDED as an item (CONFIRMED from
   defs)**: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_ForsakenCrags.xml:126`
   carries `<AA_Frostling MayRequire="sarg.alphaanimals">0.05</AA_Frostling>` with a
   comment naming this exact sheet note. No dedicated ledger item names it, but it rode
   in under `BIOME_OWNERSHIP_WAVE_1` (closed, 2026-09-09) alongside the rest of the
   transplanted roster — proven from the def, not inferred.
2. **`LIGHTFALL_CHASM_AUTHORING_1`** — **FILED**, `show`: state `done`, closed
   `89dbfd0a0`. Site + name authored on the Damp chain per spec.
3. **Dusk rat art redo → NEW-ART ledger** — **UNCERTAIN**, leaning DONE-BUT-DECIDED-
   DIFFERENTLY rather than unfiled. Roster uses `AA_DuskRat` (donor Alpha Animals def,
   not the "vanilla `Rat`" the sheet's own bullet 6 describes — a second, smaller
   sheet/roster disagreement worth flagging on its own).
   `design/Jawa/fauna/creature_art_decisions.json:273` records `"AA_DuskRat": {"state":
   "keep", "note": ""}` — donor art kept, not redone, and no redo ledger item exists.
   Cosmetic-only, and the decisions file may simply be where "keep the donor art" was
   ruled, superseding the sheet's redo ask; did not find a rescinding note either way, so
   calling this UNCERTAIN rather than UNFILED. Searched: `dusk rat`, `duskrat`,
   `AA_DuskRat`, `NEW-ART` ledger for a DuskRat row.
4. **Colder/warmer variant mapping** — explicitly marked **unratified** by the sheet
   itself ("BENCH-derived, unratified... to concretize at the assignment sitting"); this
   is a proposal awaiting a ruling, not yet owed build work. Not ranking it — searched
   `tholin-rime`, `daysmoke` anyway, zero hits in items either way.
5. **Engine feasibility pass** (permanent-dark weather-vs-condition; gust-wind
   variability, likely C#; turbine-breakage rates; a rare reveal weather def — the sheet
   calls it "the Unveiling" everywhere except this one Owed bullet, which calls it "the
   Clearing" — **note: sheet-internal naming inconsistency, not a second mechanic**;
   pursuit/raid slowdown wiring) — **UNFILED (CONFIRMED)**. `RUT_ForsakenCrags.xml`'s own
   header states outright: *"NOT this pass's scope: the Unveiling as its own rare
   WeatherDef; the darkbeast, the Dark-folding mechanism, gust-wind variability (all C#,
   SS Owed)"* — and for the wind/geothermal bans: *"are not claimed as satisfied by this
   def alone."* So the def, weather-commonality and fauna are built, but every mechanic
   that makes this biome distinctive in play (the darkbeast's EM sun-block, the
   Unveiling's rare reveal, gust-pattern wind, turbine breakage, raid/pursuit slowdown in
   the Dark) is still missing.
   Searched: `darkbeast`, `dark-folding`, `gust-wind`, `turbine-breakage`, `unveiling`,
   `pursuit/raid slowdown`, `raid slowdown` — the only hits are a cataloguing/research
   item (`ALPHA_FAMILY_SOURCE_REVIEW_1`, which inventories the donor mod's mechanics as
   background research, not a build) and two unrelated docs. Zero build item, zero C#.
6. **Roster admission tests at `BIOME_FAUNA_ASSIGNMENT_SITTING_1`** — **DONE**; that item
   is closed and its notes show the crags' fauna (AA_SandProwler, AA_Frostling, etc.)
   admitted and now present in the def (confirmed above).

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
