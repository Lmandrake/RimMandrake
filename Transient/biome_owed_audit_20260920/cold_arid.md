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

Owed section (4 bullets) plus one inline 🔑 line from §10 (not under the Owed heading,
but explicitly unbuilt work per the brief's instruction to check inline 🔴/⚠️/🔑 lines) —
6 work items total.

1. 🔴 **THE HEADLINE FINDING, not from the Owed section at all.** §10's own text: *"🔑 The
   shade grid is the keystone and we must build it. One `MapComponent` computing
   `ShadeAt(IntVec3)`; shade-seeking AI, the burst hediff, crossing heat load and
   megafauna thermal mass all read from that one grid."* This is the single mechanic the
   whole biome's design depends on (§9's "sudden committed sprint across the light,
   deciding" signature moment, shade-seeking fauna, the burst-then-recover hediff,
   megafauna heat, filter-feeding sand — the §10 table's five behaviour rows all cite
   `ShadeAt` or sit downstream of it). **UNFILED (CONFIRMED)** — no ledger item, no C#.
   Searched: `ShadeAt`, `shade grid`, `MapComponent.*shade`/`ShadeSeek`/`ShadeComp`/
   `DesertShade`, `burst hediff`, `megafauna heat`, `filter-feeding sand` — zero hits in
   `infrastructure/state/items/`, `.../closed/`, or `src/`. Ranking this worst on the
   sheet: **Desert is one of the two largest land biomes and the starting biome** (see
   item #3 below — 2,390 tiles), and without `ShadeAt` every one of its headline gameplay
   behaviours (shade-seeking, the burst sprint, megafauna heat, filter-feeding) simply
   does not exist — it plays as reskinned flat terrain with no distinct mechanic, the
   same shape of gap the Blue Desert had, just for the *core* desert rather than a rare
   variant.
2. **Names** (cycle plant/staggerseed?, the prepared seed dish, the glitter-birds;
   Ultracactus already named and stands) — cosmetic naming placeholders, not build work.
   Searched `staggerseed`, `prepared seed dish`, `glitter-bird` — zero ledger hits. Not
   ranking as a finding; too small to matter next to #1.
3. **`WORLDMAP_DESERT_BAND_REPAIR_1`** — **FILED, DONE.** `show`: state `done`, closed
   `d2f0e37d8`. Retyped the mislabelled bands (arc <60 → `ExtremeDesert`, arc >88 →
   `Wasteland`); current Desert tile count is 2,390 per the enrichment item's fresh
   re-measure (item #4).
4. **Wide gaps as named world features + patch-chain connectivity** — **FILED**, rides
   `BIOME_ENRICHMENT_DESERT_WASTELAND_1` (state `doing`, **BLOCKED**). That item's own
   note explains why nothing has been placed yet: `desert.md` "names zero RimWorld
   defNames" for its wide-gap/toll-point/shade-patch kit — it's narrative description,
   not a placeable mutator/landmark list — so the item is correctly blocked on an owner
   naming pass rather than silently stalled. Not counting this as unfiled; it is filed
   and honestly blocked, but flagging it as a second thing worth the owner's eye given
   today's question — it is a live example of the same failure mode (a sheet's Owed
   prose with no def-level follow-through) almost slipping through, caught only because
   FOUNDRY refused to guess defNames.
5. *(Sheet-internal note, not a work item)*: the shade table's wording that "an earlier
   draft modelled the shade as a connected network... superseded by the patch-and-dash
   model" is itself an amendment record, not owed work — no action needed.

## deep_desert.md

Owed section (5 bullets) — 5 work items, one split further by cross-reference.

1. **Sarlacc** ("its own item... three life-cycle stages, a dungeon-like module") —
   **FILED**, `SARLACC_HABITAT_BUILD_1` (state `ready`, BLOCKED). `show` confirms
   substantial work landed (swimmer/rooting/anchored/7 hediffs/settings/v1 breach) with
   named remaining gaps (pocket-map dungeon interior not built, DBH water wiring, real
   art, a RUT Sun-Debt patch) and world placement correctly split off to
   `SARLACC_WORLDMAP_RELOCATE_1` (closed). Properly tracked, not a silent gap.
2. **Silverbole's final name** — owner's-pick placeholder, not build work. Searched
   `silverbole`, one unrelated hit (`INHABITED_AUGMENTATION_BUILD_1`). Not ranking.
3. **Cavern authoring** ("Caverns and permanently shaded canyons — the real ecosystems...
   Serious authoring effort belongs here — reference the Mandalorian cave-beast") —
   **UNFILED (CONFIRMED)**. 🔴 Important disambiguation: this is **not** the Lantern
   Deeps/crystal-caverns work (`CAVERNS_PARITY_BUILD_1`, closed — that's a different
   named biome, `the_lantern_deeps.md`, donor-parity XML work, not mine to report). §8 of
   *this* sheet describes a distinct mini-ecosystem local to the deep desert: brine-seep
   upwellings, trap-striking plants/animals in a few-metres territory, and a named
   reference creature (the Mandalorian cave-beast analog, "massive eggs a Jawa would
   cross a desert for"). Searched: `mandalorian cave-beast`, `deep.desert.*cavern` /
   `cavern.*deep.desert`, `cavern` inside the two Sarlacc closed items (checking it
   wasn't folded into that build) — zero hits anywhere in items, closed items, or `src/`
   (only `DeepDesertTribes.xml`/`.png`, faction art, exists under a DeepDesert name).
   Nothing about brine ecosystems, trap-plants or a cave-beast creature is built or
   ticketed. This is real, sheet-flagged ⭐ "serious authoring effort" with zero ledger
   trace.
4. **Wind-grain / yardang generation in the map-modification routine** — **UNFILED, but
   with a caveat**: two open design docs exist —
   `design/RimMandrake/map_generator_round4_options.md` and
   `.../map_generator_chooser_spec.md` — that discuss yardang/wind-grain generation for
   deep desert AND dune sea together, but the round4 doc's own text flags the underlying
   rule as an **open call, not yet ruled** ("This reverses rule 11 as written: open
   call"). Searched `yardang`, `wind-grain`/`wind grain`, `windgrain`, `MAP_GENERATOR` /
   `map_generator_round4` / `map_generator_chooser` as item names — zero ledger items at
   all, filed or closed, for this generator work on either biome. Ranking this below the
   cavern ecosystem because the design itself isn't finished (nothing to build yet
   without the ruling), but noting it here since the owner's underlying question was
   "was this ever filed" and the honest answer is no, at any stage.
5. **§0 per-region table stale against V23** — a documentation/measurement fix (re-run
   `biome_sheet_stats.py` per-region), not a gameplay gap. Did not chase a ledger ID;
   low-stakes doc accuracy issue, not ranking it.

## arid_shrubland.md

Owed section (6 bullets) — split into 8 work items (the engine-feasibility bullet lists
seven distinct mechanics).

1. **The band mend** (248 sunward-tail tiles → Desert/ExtremeDesert; Ashfall Range/Dew
   Horn judged individually; keep arc 95–100 fog margin; cull past arc 100; paint by
   plumes) — **FILED but EXECUTION UNCONFIRMED (flag, not a clean UNFILED)**. It rode
   `WORLDMAP_DESERT_BAND_REPAIR_1` (closed, `d2f0e37d8`) under a "AridShrubland folds
   in" section, ratified same session as the Desert band repair. ⚠️ **But that item's own
   closing note (2026-09-09T19:06:21Z) names only the Desert side as landed** — *"bands
   A(797 tiles)->ExtremeDesert and D(745)->Wasteland landed live+frozen... Band C
   intentionally left untouched."* It says nothing about the 248-tile AridShrubland cut
   or the 19-tile Wasteland tail that were ratified in the same document. I did not
   re-measure the live tile CSV myself (would need the offline dump/measure tooling, out
   of scope for a report-only pass) so I am not calling this UNFILED — but the item's own
   closing note does not evidence the shrubland-specific work happened, which is exactly
   the failure shape the owner is asking about: work ratified inside a ticket, ticket
   closed, and the specific line item silently dropped. Recommend a live re-measure
   before trusting this line closed.
2. **Tiles CSV frozen-stamp staleness** → `TILES_STAMP_VERIFY_1` — **FILED, DONE**
   (`show`: closed).
3. **`TREE_GRAPHICS_OWNERSHIP_1`** (own sweetline-tree art/scale, drop tree-mod
   rescaling) — **FILED**, state `doing`, BLOCKED on an owner art pick (14 recovered
   candidates awaiting selection per the item's blocker note). Filed and actively
   blocked, not silently dropped.
4. **Names** (giants, snake-analogs, bird-analogs, sweetline trees, the fuzz, venomvine,
   the Stall, the Gale) — owner-pick placeholders, not build work. Not ranking.
5. **Engine feasibility pass** — seven distinct mechanics, checked individually:
   - Stall/Gale wind-driven weather events + AI hooks — **UNFILED (CONFIRMED)**.
   - Parental enrage on approach — **UNFILED (CONFIRMED)**.
   - Canopy-concealment vs the colony-visibility stat — **UNFILED (CONFIRMED)**. The
     general dial exists and is built (`COLONY_VISIBILITY_BUILD_1`, closed/done — a
     threat-scoped raid-point Postfix), but neither it nor its predecessor
     (`COLONY_VISIBILITY_STAT_1`) mentions canopy, cover or shrubland as an input; the
     specific "shrubland canopy feeds the visibility stat" wiring this bullet asks for is
     not there.
   - Venomvine passability by body size — **UNFILED (CONFIRMED)**.
   - Nest-theft behaviour — **UNFILED (CONFIRMED)**.
   - Giants' wall-indifference and fire-stamping — **UNFILED (CONFIRMED)**.
   - Vaporator desertification (V-blight) as a map effect — **UNFILED (CONFIRMED)**; the
     only vaporator items found (`MOISTURE_VAPORATOR_WALL_CLIP_1`,
     `MOISTURE_FARM_TEMPLATES_1`, both closed) are about moisture-farm building
     templates and a wall-clip render bug, not an ecological desertification effect.
   Searched across all seven: `the Stall`, `the Gale`, `parental enrage`, `venomvine`,
   `nest-theft`/`nest theft`, `vaporator`, `V-blight`, `colony_visibility_stat` — in
   `infrastructure/state/items/`, `.../closed/`, and (for the visibility items) their
   full text. Zero build items and zero matching C# for any of the seven.
6. **Candidates not yet ruled** (tree-guardian animals; birds stealing from player bases)
   — explicitly not-yet-ruled by the sheet's own wording, so not owed work until the
   owner picks; not ranking.

## wasteland.md

Owed section (4 bullets) — split into 6 work items, cross-checked against
`RUT_Wasteland.xml`'s own header comment, which independently lists its own unbuilt
scope and matches the sheet closely.

1. **Names** (the Throat's true name; radiotroph flora/excretors/radiothermal
   solitaries/brine-battery creatures; halo-storm/plasma-storm player-facing names) —
   placeholders, not ranking, except see item 5 below on "the Throat" itself.
2. **Engine feasibility pass** (radiation/pollution spine → dose/geiger layer; three
   storm WeatherDefs — ash, halo, plasma; storm map-reshuffle/mutator-churn tooling) —
   **UNFILED (CONFIRMED)**, doubly so: searched `geiger`, `dose layer`, `halo-storm`,
   `plasma-storm`, `storm map-reshuffle`, `radiotroph` — zero ledger hits either live or
   closed — AND `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Wasteland.xml`'s own
   authoring comment independently confirms it, verbatim: *"NOT this pass's scope: the
   dose/geiger layer; the three storm WeatherDefs (ash, halo, plasma); the
   mutator/injection palette per family... the Junkers' tipping-fee economy."* Currently
   `ToxRain`/`GrayPall` (Anomaly) stand in as reflavored placeholders; the biome's actual
   named weather (ash storms, radiation-halo storms, plasma storms) does not exist as
   WeatherDefs, and the radiological disease register the sheet's ban 4 requires
   ("every resident visibly shaped by the contamination") was explicitly left un-authored
   for the same reason ("SS Owed 'needs a dose/geiger layer'").
3. **Def tails — 19 tiles at arc < 60** — **SAME UNCONFIRMED-EXECUTION FLAG as
   `arid_shrubland.md`'s band mend** (see that section, item 1): both were ratified in
   the same `WORLDMAP_DESERT_BAND_REPAIR_1` document under a "Wasteland tail" heading,
   and that item's closing note names only the Desert bands (A/D) as landed, not this
   19-tile Wasteland correction. Not calling it UNFILED outright (didn't re-measure the
   live tiles), but the same gap applies here.
4. **Tipping-fee economy / waste-caravan traffic faction-spec wiring** (Junkers,
   Wildsteam, Deepwater) — **UNFILED (CONFIRMED)**. Searched `tipping-fee`, `tipping fee`,
   `waste-caravan`, `waste caravan` — zero hits in items or closed items; and the same
   def-header line above names "the Junkers' tipping-fee economy" as explicitly out of
   this pass's scope.
5. **"The Throat"** — **DONE, but with a naming/identity ambiguity worth flagging.** The
   sheet describes the Throat as "the environmental doomsday clock," a place you could
   "pour [the Slime] down," with a faction triangle and world-threatening buildup around
   it (§ Owed's "Slime experiment" option). That description matches `GAPING_DOOM_SITE_1`
   (closed, done) almost exactly: a dead-sarlacc toxic-waste pit, world-threatening
   chemical/nuclear/exotic buildup ruled as "a plot element, not set dressing" (owner,
   2026-09-08), Junker-operated dumping-rights economy. CONFIDENCE: high but not
   certain — `GAPING_DOOM_SITE_1` places it at tile 2403 in `ZBiome_Badlands` (the
   Cracked Lands)/"Junker territory," not explicitly tagged `Wasteland`, and the item's
   own CSV note flags a region-bookkeeping mismatch at that tile ("Grey Sea" vs the
   biome). `RUT_Wasteland.xml`'s header (authored 2026-09-09, same day
   `GAPING_DOOM_SITE_1` was filed) still lists "the Throat" among things NOT in its
   scope — plausibly just written before/independent of that landmark landing, or "the
   Throat" and "the Gaping Doom" could be two names circling the same idea that never
   got reconciled. Did not chase further; flagging the ambiguity rather than resolving
   it under a read-only brief.

## the_cracked_lands.md

Owed section (10 bullets) — this sheet is the best-tracked of the ten: most bullets carry
their own named ledger ID already, and `RUT_CrackedLands.xml`'s own header comment gives
an independent NOT-in-scope list that cross-checks cleanly against the sheet. Split into
12 work items.

**FILED and DONE** (verified via `show`, all `closed`/`done`):
- `CONTAGION_BIOME_PLACEMENT_1` — Contagion peaks placement. Done.
- `WORLD_RIVER_COLORS_1` — river gradient colouring. Done.
- `SAND_SWIMMERS_MOD_1` — sand fishing. Done.
- `FISH_BY_BIOME_1` → superseded by **`FISH_TYPES_PATCH_BUILD_1`** — done, fills the
  Cracked Lands' `SandFishing_CrackedLands.xml` fishTypes explicitly.
- `FLOOD_CANYON_BIOME_1` — the flood-as-engine-event (warning chimes, wall of water,
  explosive growth) — done, closed 2026-09-12. This also satisfies the Owed bullet's
  "water chimes" (its spec generalizes "the Cracked Lands chime mechanic").
- **Def label rename** — done: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/
  RUT_CrackedLands.xml` exists, `<label>the Cracked Lands</label>`.
- **Def-tails check on 985 tiles** — folded into `BIOME_OWNERSHIP_WAVE_1`'s own
  authoring measurement: the def's header states 985 tiles as its MEASURED count at
  authoring time (2026-09-09), matching the sheet's own SS0 figure post-Contagion-cut.
  Treating as satisfied rather than a separate open check.

**FILED, in progress:**
- `EXPLOSIVE_PLANT_GROWTH_1` — state `doing`.
- `FLOOD_WITNESS_EVENT_1` — state `doing`, BLOCKED on `FLOOD_CANYON_BIOME_1`'s
  production arm (which is itself now closed per above — worth a fresh look at whether
  this unblocks; not chasing further under a read-only brief).
- `TREE_GRAPHICS_OWNERSHIP_1` — covers the "twisted trees" part of flora authoring
  (same item already discussed under `arid_shrubland.md`), state `doing`, BLOCKED.

**UNFILED (CONFIRMED):**
- **Grasses and mosses** (the other two-thirds of "Flora authoring") — no ledger item
  covers non-tree flora for this biome specifically. Searched `cracked lands grass`,
  `cracked lands moss` — zero hits; only the tree piece is tracked.
- **Discovery surveys and crack-wax as item defs** — searched `discovery survey`,
  `crack-wax`, `crackwax` — zero hits anywhere in items, closed items, or `src/`.
- **The bloom as item defs** (§10b's boom-bust crop economy) — searched `the bloom`
  (in items/closed) — zero hits; only descriptive sheet text exists, no item-def build.
- **The flier-commute vector line to the Desert sheet** ("where they nest") — searched
  `flier-commute`, `vector line` — zero hits. `RUT_CrackedLands.xml`'s own header
  independently lists this exact phrase ("the flier-commute vector line to the Desert
  sheet") among its NOT-in-scope items, corroborating the ledger search.
Ranking these below the desert/nightside/crags findings above: the biome's core
identity (terrain, weather, fauna roster, the flood mechanism, fish, sand-fishing) is
built and playable; what's missing is flavour/economy dressing (crack-wax, the bloom,
discovery surveys) and one cross-biome connective detail (flier nesting), not a
load-bearing mechanic.

## fall_line.md

This sheet has **no `## Owed` heading at all** — only `## Open, not ruled` (2 bullets,
genuinely pre-ratification design questions, not commissioned work) — so I read the
whole sheet for inline 🔴/⚠️ lines naming ratified-but-unbuilt work, per the brief's
instruction. Found one, and it's a big one.

1. 🔴 **§8b, "The ferals" — a complete, owner-ratified mechanic, fully specced, zero
   trace anywhere in the ledger or the code.** Owner's verbatim ruling (2026-09-05):
   crash survivors gone feral — sentient races AND droids — capturable and turned into
   **slaves** (races, with a **permanent mental-problem penalty** that makes them "much
   less valuable") or **memwiped and restored** (droids, "clean" restoration, and
   killing them explicitly **does not anger neutral droids**); no faction affiliation;
   wily/flee-prone behaviour. The sheet's own table spells out every stat needed to
   build it, and explicitly scopes a mental-treatment payoff to v2 ("v2 only, do not
   build now") while leaving the capture/slave/memwipe core as v1, buildable now.
   **UNFILED (CONFIRMED).** Searched: `feral droid`, `feral pawn`, `memwipe`, `feral
   race` — zero hits in `infrastructure/state/items/`, `.../closed/`. Also searched
   `feralpawn`, `feraldroid`, `FallLineFeral`, `RUT_Feral` in `src/` — zero defs, zero
   C#. (A loose `grep -li feral` across `src/` returns only unrelated substring hits —
   `Feralisk` creature names etc. — confirmed by inspection, not a real match.)
   Ranking this alongside the desert `ShadeAt` and nightside-fauna findings: it is a
   named, fully-detailed mechanic the owner personally dictated, with a whole gameplay
   loop (capture → choose slave-or-memwipe → live with the consequence) that currently
   does not exist in the game at all — the Fall Line's one named population (crash
   survivors) is simply absent from play.
2. **Ridge line treatment** and **which donor mod supplies §8b vs custom C#** — both
   explicitly `## Open, not ruled`; the sheet itself says these await a ruling, so they
   are not "owed" work in the sense this audit is chasing (nothing was commissioned
   yet). Not ranking.

## weeping_stones.md

The best-tracked sheet of the ten — every named item checks out FILED, most DONE. Owed
section (7 bullets) split into 8 work items.

**FILED and DONE:**
- `OASIS_LANDMARK_PLACEMENT_1` — done, closed `43172ff44`.
- `OASIS_MUTATOR_PATCH_1` — done, closed `c9af67d3e`.
- `WEEPING_STONES_ROSTER_1` — done, closed `5851917a`.
- `VAPOR_EMITTER_PLACEMENT_1` (the seep-oasis siting dependency) — done, closed
  `ce76906fb`.
- `HUTT_LORDS_AND_POSTS_1` (the cross-flow ledger's Hutt-palace note) — done.
- **Grammar backfill** — done via `CRACKED_LANDS_ENRICHMENT_1` (closed), which filed
  both the README step AND the Cracked Lands' own backfill in one item; this also
  retroactively confirms my `the_cracked_lands.md` section above.

**Not owed yet (correctly gated, not a gap):**
- **The owner's pass on §10–12** — explicitly unratified by the sheet's own words; the
  beasts, dewback reassignment, droid dying-oases and Imperial metering wait on him. Not
  ranking — this is the sheet correctly declining to file work nobody has approved yet,
  which is the opposite of the failure the owner is asking about.

**UNFILED (CONFIRMED):**
- **Engine feasibility pass** — fog-at-wind-hour weather, the condenser fin as a
  buildable water-source structure, the servo-vent enclosure, aeolian ambient sound per
  oasis state, and the truce mechanism (owner-ruled cheap-for-v1: spawn/flavor
  suppression of predator hunts near water, with "the honest behavior mod" deferred to
  v2). Searched: `condenser fin`, `servo-vent`, `fog-at-wind-hour`, `aeolian ambient`,
  `the truce`, `predator hunts near water` — zero hits in items, closed items, or
  `src/`. The v1-scoped truce mechanism in particular is a specific, cheap, owner-ruled
  ask ("spawn/flavor suppression") with no build trace at all.
  Ranking below the desert/nightside/fall-line findings: Weeping Stones' core (terrain,
  oases, roster, mutators) is fully built and this sheet is otherwise the model of good
  tracking — the gap is purely the ambient/mechanical polish layer, not a missing
  ecosystem or missing gameplay loop.

## dune_sea.md
(pending)
