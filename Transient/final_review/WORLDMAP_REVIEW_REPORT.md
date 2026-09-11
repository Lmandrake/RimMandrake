# WORLDMAP_FINAL_REVIEW_1 — Phase 4 Synthesis: Is this map going to be THE map?

**Written 2026-09-11 (BENCH synthesis lane).** A serious game-dev-company-style review of
Ash'karr as it stands live, from the three Phase-1 measured audits
(`findings_rivers_roads.md`, `findings_mutators_landmarks.md`,
`findings_settlements_biomes.md`), the in-engine audits (`world_lint.json`,
`world_mutators_audit.json`), the Phase-0 export (`MANIFEST.json`, all fresh 2026-09-11),
the offline STARE (`stare_notes_offline.md`), and my own look at
`Transient/final_review/biome_map_render.png/ASHKARR_WORLDMAP.biome.equirect.png`.

Every claim is tagged: **MEASURED** (traces to a findings file or export), **SEEN** (names
its image), or **JUDGED** (my call, said so). Every critique carries a corrective with a
rough cost (S = under an hour / one script pass; M = a working session, possibly a bridge
window; L = multi-session or a repaint). Every compliment carries a leverage brainstorm.

---

## Executive summary

The map is structurally sound and materially finished. The big machinery — faction
roster, biome zonation, temperature physics, river topology, the road trunk network —
audits clean or clean-with-named-exceptions. What remains is a **finishing-pass problem,
not a design problem**: ~130 stale mutators surviving old repaints, ~150 mutators sitting
on terrain that contradicts their own def gates, 14 landmarks stacked under settlements,
a handful of duplicate names, one river arm still flowing the wrong way at the Scald, and
one doctrine sentence in `the_one_map.md` that no longer describes the planet that got
built. None of it requires re-authoring anything the owner has already judged. The
provisional verdict is at the end.

---

## 1. Rivers

### What's right

- **The river graph is real, connected, and internally consistent.** 326 edges, 335
  tiles, 11 components, zero orphan components — every component reaches a named sea or
  a legitimate endorheic terminus. `riverDist` is monotonic along 98.8% of edges, with
  the only exceptions at a single confluence showing the exact expected `max()`-merge
  signature. MEASURED (`findings_rivers_roads.md` §§1,3,4). This retires the standing
  worry that the frozen world's rivers never got `riverDist` set — they did, and it holds.
  - **Leverage:** a trustworthy flow direction on every river tile makes downstream
    mechanics nearly free — caravan drift bonuses travelling downstream, a "follow the
    water down" survival quest, trade-route generation that rides the river graph,
    flavor text that correctly says which way the water runs at any settle site. Nobody
    has built any of these because nobody trusted the field. Now it's load-bearing.
- **The R1 Scald ruling is 8/9 delivered.** Eight of nine Scald-boundary edges read as
  OUTFLOW by `riverDist` — the crater ocean reads as the water SOURCE, exactly the lore
  ruling, and a full reversal of the 2026-09-07 all-inflow measurement. MEASURED (§6).
  - **Leverage:** the Scald-spills-through-the-notch story is now mechanically true in
    the data, not just the prose. That makes the Scald Spine notch a legitimate strategic
    chokepoint for scenario/quest placement — the one place the planet's biggest river
    exits — cheap to exploit because the geometry already agrees with the lore.

### What's wrong

- **One arm at tile 11943 still reads INFLOW into the Scald** (the →777 branch,
  `riverDist` 2 vs 3, while its sibling branch is already flipped). MEASURED (§6).
  **Corrective:** renumber the 777 arm's `riverDist` upward — renumber riverDist, never
  links or elevation (standing memory). **Cost: S.**
- **One LargeRiver TRUNK system (118 tiles) reaches no sea.** The in-engine lint is
  explicit that low-accumulation rivers may die in playas by owner's ruling but trunk
  systems are defects — and it finds exactly one, sample tile 256. MEASURED
  (`world_lint.json` riverSystems). **Corrective:** either extend that trunk to a sea /
  the Scald system, or downgrade its river class so it's legally endorheic. Needs one
  LOOK at where it dies before choosing. **Cost: M.**
- **63 non-Scald uphill-flow edges (20% of directed edges)**, worst gaining +627 m
  "downstream." Consistent with the known noisy coarse DEM; the 8 Scald-touching ones
  are the accepted −350 m artifact and need nothing. MEASURED (§2). **Corrective:**
  regrade elevation along the 15 worst reaches only — the tail is noise a player will
  never perceive; the +300 m-plus reaches are the ones a hillshade render would show as
  rivers climbing walls. **Cost: M.**
- **3 river links are silently hidden by `AB_PyroclasticConflagration`** (tiles 11090,
  11092, 21311) — not mouths, not the Scald; a volcanic biome eating river renders.
  MEASURED (§7). **Corrective:** confirm intentional (lava hiding a river is plausible)
  or shift the links one tile; a one-line owner call. **Cost: S.**

## 2. Roads

### What's right

- **One genuine trunk network of 1,122 tiles**, and zero mechanical violations: 0 road
  edges on `allowRoads: false` tiles, 0 on open sea, 0 on Impassable hilliness.
  MEASURED (§§1,4). The main network is a real artery system, not fragments.
  - **Leverage:** a single connected majority network means caravan travel-time tables,
    patrol/ambush event placement "on the road," and a courier-quest economy all work
    off one graph with no special-casing. Also cheap: a "days from the Ore Moot" metric
    for every settlement as a difficulty/remoteness stat.
- **74/96 settlements sit directly on the road graph.** MEASURED (§2).

### What's wrong

- **46 disconnected road fragments (124 tiles), mostly 2–3 tile crumbs**, and **90 of
  154 dead-end stubs have no settlement within ~3 hexes** — with the worst offenders on
  `RUT_NightsideIce` and the mycotic terminator, reading as leftover decoration serving
  nothing. MEASURED (§§1,3; distance metric approximate, calibrated great-circle).
  JUDGED: nightside ice roads also cut against the map's own story — nothing lives out
  there to build them. **Corrective:** a cull-or-connect pass: delete the crumbs that
  serve no settlement or landmark, spur-connect the few that do. **Cost: M.**
- **18–22 settlements have no road within ~1 hex** (18 by the findings' calibrated
  metric, 22 by the engine lint's adjacency — the two instruments bracket the truth).
  Six are Deep Desert Tribes, plausibly roadless-nomad by design; but Wildsteam jungle
  seats, Hollow Hive, Deepwater Hold, Quiet Lab, and The Free Charge look like
  omissions rather than statements. MEASURED (`findings_rivers_roads.md` §2 +
  `world_lint.json` settlementsWithNoRoad). **Corrective:** rule the nomad exemption
  explicitly (S, doc), then spur the non-exempt dozen (M, bridge).

## 3. Mutators

### What's right

- **Density gradient runs the right way.** Exotic destination biomes (MechanoidIntrusion
  5.78/tile, CypreJungle 3.98) are mutator-rich; the vast common deserts sit at the
  bottom (0.63–0.70). MEASURED (density table). JUDGED: that is exactly the exploration
  reward curve you want — emptiness as texture on the dune sheet, payoff where you
  travel to.
  - **Leverage:** the density table doubles as a free points-of-interest heat map —
    quest targets, expedition destinations, and "rumor" content can be sampled straight
    from mutator-dense tiles with no new authoring.

### What's wrong

- **104 stale Coast mutators on non-coastal tiles — the single largest defect count on
  the map.** Confirmed twice independently (in-engine lint + direct recomputation; the
  audit's own offender list was silently truncated at 30, now recovered in full). These
  are repaint survivors: Wasteland 32, AridShrubland 32, Badlands 21… a player
  inspecting a landlocked desert tile reads "Coast." MEASURED (`world_lint.json`
  staleMarineMutators + `findings_mutators_landmarks.md`). **Corrective:** scripted
  strip of the Coast mutator from all 104 tiles (IDs fully recovered), then re-run
  world-lint to confirm zero. **Cost: S–M** (one bridge window, mechanical).
- **153 hilliness-gate violations** — mutators on terrain outside their own def's
  declared range: Cliffs on Flat (43), InsectMegahive on flat swamp (28), Hollow (19),
  etc. Not checked by the engine's own audit at all (it only checks Coast). MEASURED
  (independent cross-check vs 47 gated defs). **Corrective:** per-def sweep — remove
  the mutator or (where the def is one step short, like AncientQuarry all on
  LargeHills) accept with a recorded waiver. **Cost: M.**
- **Duplicate mutator defs on single tiles** (3214, 3678: `VEE_RedDesert` ×2 etc.) — a
  generator bug leaving literal duplicates in the array. MEASURED. **Corrective:**
  dedupe pass over `world_mutators.json` tiles, applied via bridge. **Cost: S.**
- **`isCoastal` is false on all 14,400 exported tiles** — a broken field in the export,
  not the world. MEASURED. **Corrective:** fix or delete the field in the companion
  exporter so no future audit trusts it; `waterCovered` is the working proxy. **Cost: S.**
- **247/409 TileMutatorDefs never placed.** MEASURED, but JUDGED mostly correct: a
  desert world *should* never roll `Fjord` or `Iceberg`. The five RUT-tier authored
  defs that never rolled (`RUT_ColdLavaTube`, `RUT_Lightfall`, `RUT_LightlessSink`,
  `RUT_ShadowedOverhang`, `RUT_Slough_GelatinousBreach`) are the only real question —
  paid-for content sitting unused. **Corrective:** per-def call on the five: hand-place
  a few instances or accept. **Cost: S.**
- River-gate check on 165 River-mutator instances: **UNMEASURED** — the export carries
  no per-tile river flag for it. Needs a dedicated export next bridge window. Honest gap.

## 4. Landmarks

### What's right

- **3,414 landmarks, 100% icon coverage at the def level, 65 defs in play.** MEASURED.
  The world map is genuinely furnished — nearly 1 landmark per 6.4 tiles.
  - **Leverage:** at this density, "nearest landmark" is defined virtually everywhere —
    free flavor for raid arrival text, caravan event sites, and grave/ruin storytelling
    without placing anything new.

### What's wrong

- **14 of 96 settlements share their tile with a landmark** — Vicky's Ruse on Ruins,
  Meoum Cave Network on a Cavern, four Valleys, three TerraformingScars… MEASURED (full
  list in findings). JUDGED: a few are arguably flavor (a town IN a valley), but
  scar/ruins collisions read as placement error, and tile 2607 is a double-hit (also a
  stale Coast tile). **Corrective:** per-pair review — move the landmark one tile or
  delete; 14 rows, one sitting. **Cost: S.**
- **42 duplicate landmark names, "Dead Sarlacc" ×7** (owner-flagged, now confirmed),
  plus the "X's Caves" possessive pattern doing most of the rest. MEASURED.
  **Corrective:** rename pass over the 42 (a hand pass beats fixing the namer — the
  namer never runs again on a frozen world). A Dead Sarlacc ×7 could even be kept ×2–3
  as deliberate lore (JUDGED, offer to owner: sarlaccs die in numbers), but not ×7.
  **Cost: S.**

## 5. Settlements & factions

### What's right

- **Zero delta on every faction.** All 12 NPC factions, 95 NPC settlements + 1 player
  colony, exactly matching the design doc's own declared live-canon roster. Zero
  settlements on water, zero on Impassable, zero stacked, zero null-faction
  settlements — the scary "80 no-faction objects will be destroyed on load" flag is a
  confirmed nothingburger (all asteroids/derelicts, none Settlements). MEASURED
  (`findings_settlements_biomes.md` §§1–2, `world_lint.json`).
  - **Leverage:** a roster this stable can be hard-referenced. Faction quest chains,
    trade specialities per named settlement, a printed gazetteer, and the shipped-save
    onboarding text can all cite settlement names without a compatibility layer. That
    is a luxury procedurally-generated games never get — spend it.
- **Deep Desert Tribes 9/9 on Desert/ExtremeDesert, zero water — exact spec match.**
  MEASURED. Wildsteam all on jungle-family biomes, consistent. MEASURED.

### What's wrong

- **Two Hutt palaces (Gorga's, Hurgo's) sit on tiles whose own biome is
  `ZBiome_DesertOasis`**, against the "beside an oasis, never on it" ruling. Soft flag
  — tile-grain data cannot distinguish on-the-well from beside-it-in-an-oasis-hex.
  MEASURED (§3). **Corrective:** Phase-2 in-game look at those two tiles; move one hex
  if the well is literally under the palace. **Cost: S.**
- **Ascendant Helix's Cold Archive and The Fair Copy stand on placeholder biomes**
  because `HorrorWastes` has 0 tiles on the live planet — a known, admitted gap in the
  doc itself, not a new defect. MEASURED (§3, §5). **Corrective:** paint the
  HorrorWastes patch per the doc's own §6c, or re-spec the two settlements onto biomes
  that exist. This is the last place the planet visibly diverges from its own night-side
  spec ("terminator → poison forest → dark margin (HorrorWastes…)"). **Cost: M.**
- **Spacing: 4 pairs under 3 tiles**, and the two worst involve the player: The Claim
  Jump↔Ore Moot at 1.76 tiles, and **the Ore Moot 1.93 tiles from the player Colony**.
  MEASURED (§4). JUDGED: close NPC pairs at the Junkers/Moot cluster are defensible as
  a mining district; the player-adjacency is a real decision because the shipped save
  fixes the start forever. **Corrective:** owner ruling on the start site (there is no
  canon ruling yet, §7b) before shipping the save. **Cost: S (a decision, not work).**

## 6. Biome distribution & climate

### What's right

- **The dryland ladder is strictly monotonic across all twelve 15° arc bands** —
  63.45 °C at substellar to −75.64 °C antistellar, zero inversions on 21,872 tiles.
  MEASURED (§5). The tidal-lock physics the whole design keys on is simply correct.
  - **Leverage:** arc-from-substellar is now a certified difficulty axis. A landing-site
    advisor ("this tile: arc 78°, mean 17 °C, growing period X"), scenario presets by
    ring, and heat-themed incident scaling can all be driven off one number per tile
    with no further validation.
- **Zero water-biome-on-raised-land, zero submerged land biomes, one single-tile island
  on the whole planet.** MEASURED (`world_lint.json`). The land/water paint is tight.

### What's needing a ruling, not a repaint

- **Vegetated biomes total 15.8% of the planet; `AB_MycoticJungle` alone is 10.08%,
  third most common biome, nearly tying Desert** — against `the_one_map.md`'s "green is
  a narrow, fierce ribbon on the water margin and nowhere else." MEASURED (§5). But the
  offline STARE dispositioned it: the purple mass is the NIGHTSIDE fungal belt carrying
  the authored wood-regions, and the doc's own Scald section explicitly assigns "the
  other green" (Mycotic + PoisonForest) to the meridian — the doctrine sentence and the
  doc's own later ruling disagree with each other. JUDGED: the belt is coherent for a
  tidally-locked world and clearly deliberate (it is named — Blindwood, Ashwood, Venom
  Wood, Hanging Wood). **Corrective:** fix the SENTENCE, not the planet — amend the
  "Green" constraint in `the_one_map.md` to scope "narrow fierce ribbon" to tropical
  jungle (which measures a genuinely narrow 2.4% across four biomes) and name the
  nightside fungal belt as intended. Owner glances at the render to ratify. **Cost: S.**
- **Water is 6.62% vs the ~8.6% stated target** — ~2 points under, consistent with the
  doc's own tracked decline across three measurements; not a new finding. MEASURED
  (§5). **Corrective:** owner call — either restate the target at ~6.6% ("live is
  canon," matching how §7 settlements were handled) or add ~430 water tiles. JUDGED: the
  render does not look water-starved; I'd restate. **Cost: S (doc) or M (paint).**

## 7. The visual read (SEEN — ASHKARR_WORLDMAP.biome.equirect.png, 2026-09-11 bundle render)

- SEEN: **The dayside reads as a place, not a gradient.** The cream ExtremeDesert core
  is broken asymmetrically — the Scald crater complex west of substellar, the grey
  Anvil massif and red Scarlands east, Fall Line Barrens northeast, Chalk Marches
  south. You can tell directions apart at a glance, which is exactly what doctrine
  defect #4 (the bullseye) forbids failing. The concentric temperature ladder is there
  because physics; the *identity* is not concentric. This is the strongest single
  argument the map is done.
  - **Leverage:** the equirect + Mollweide render is genuinely attractive — it is
    already key-art grade for a loading screen, the shipped save's flavor insert, or a
    printed player map; the named-regions layer (Dune Sea, Pyrelands, Hollow Verge,
    Cinderdark…) gives it the Tolkien-map quality for free.
- SEEN: **The Scald composition is the map's centerpiece** — round disc, vivid
  Dew-Belt/oasis halo, the Spine and the palace ring around it. The one ruled-round
  shape reads as intended, crater-not-defect.
- SEEN: **The nightside has structure, not filler** — two teal NightsideIce ovals
  framed by the purple fungal belt, with named regions (Deadstone Umbra, Lantern
  Deeps, Quiet Ground). Night reads different from day and from the terminator.
- SEEN: **Rivers and roads are nearly invisible at global scale** — hairlines. The
  audit says the graphs are sound, but no global render can confirm "winding, acute
  angles, no comb teeth" — that verification is owed to the Phase-2 closeup STARE.
  JUDGED: not a data defect, a review limitation; the jungle ribbons tracing the
  rivers are what actually sells hydrology at this zoom, and they do.
- SEEN: **The magenta `AB_GelatinousSuperorganism` at the top edge (Slough) reads as an
  elongated streak.** Doctrine says "patches only, never a band." Equirect distortion
  exaggerates anything polar, so this may well be a compact patch in reality — but it
  is the one doctrine-shaped thing on the render I could not clear. Flagged for the
  Phase-2 globe/in-game look. (0.4% of tiles, so a small fix if real.)
- SEEN: **The east mid-band settlement cluster (Claim Jump / Ore Moot / Tailings End /
  Slagfield) is visibly crowded** against the empty south — matching the measured
  1.76-tile pair. Defensible as a mining district; the render makes the case it's
  intentional-looking rather than accidental-looking.
- SEEN + MEASURED: **The render's settlement layer is stale** — legend says 121
  settlements and 1,387 road edges vs 96 and 1,235 live; the bundle's tiles layer is
  the trusted part (stare notes, lane 3 concur). Corrective: re-export the bundle's
  settlement/link CSVs from live before this render is shown as evidence of anything
  settlement-shaped. **Cost: S.**

---

## Punch list — ranked by what stands between here and "THE map"

| # | finding | evidence | corrective | cost |
|---|---------|----------|------------|------|
| 1 | 104 stale Coast mutators on landlocked tiles — largest defect count, player-visible in the tile inspector | MEASURED: world_lint.json + findings_mutators (full 104 IDs recovered) | scripted strip of Coast from the 104, re-lint to zero | S–M |
| 2 | 153 mutators violate their own hilliness gates (Cliffs-on-Flat 43, InsectMegahive 28, Hollow 19…) | MEASURED: findings_mutators cross-check vs 47 gated defs | per-def sweep: remove or re-terrain; record waivers for the one-step-short cases | M |
| 3 | Green doctrine contradiction: vegetated 15.8%, Mycotic 10.08% vs "narrow fierce ribbon… nowhere else" | MEASURED: findings_settlements §5; SEEN: nightside belt is authored & named; JUDGED: fix the doc | amend the_one_map.md Green constraint to scope ribbon to tropical jungle + name the fungal belt; owner ratifies off the render | S |
| 4 | 14 settlements share a tile with a landmark; 42 dup landmark names (Dead Sarlacc ×7) | MEASURED: findings_mutators_landmarks | one sitting: move/delete the 14; hand-rename the dupes | S |
| 5 | River finish: 1 inflow arm at Scald tile 11943; 1 orphan LargeRiver trunk (118 tiles, no sea); 15 worst uphill reaches | MEASURED: findings_rivers §§2,6 + world_lint riverSystems | renumber the 777 arm's riverDist; route or downgrade the trunk; regrade 15 reaches | M |
| 6 | Roads: 46 disconnected fragments, 90 far-from-anything dead ends (worst on nightside ice); ~12 non-nomad settlements roadless | MEASURED: findings_rivers roads §§1–3 + lint | cull-or-connect pass; explicit nomad-roadless ruling; spur the rest | M |
| 7 | HorrorWastes = 0 tiles; Cold Archive + The Fair Copy on placeholder biomes | MEASURED: findings_settlements §§3,5 (doc's own admitted gap) | paint the §6c HorrorWastes patch, or re-spec the two settlements | M |
| 8 | Player Colony 1.93 tiles from Ore Moot; no canon start-site ruling; save ships the start forever | MEASURED: findings_settlements §4 | owner ruling on the start site before the save freezes | S |
| 9 | Water 6.62% vs ~8.6% target | MEASURED: world_stats + doc trend | restate target at live figure (recommended) or add ~430 tiles | S / M |
| 10 | Stale bundle: render legend 121 settlements / 1,387 roads vs 96 / 1,235 live; export's isCoastal field always-false; dup mutator array entries | MEASURED + SEEN | refresh bundle CSVs from live; fix/remove isCoastal in exporter; dedupe mutator arrays | S |
| 11 | 2 Hutt palaces on oasis-biome tiles; 3 rivers hidden under PyroclasticConflagration; Gelatinous streak vs "patches only"; 5 authored RUT mutators never rolled | MEASURED / SEEN (each item named above) | Phase-2 eyeball each; each is a one-hex move, a one-line waiver, or a hand-placement | S |

Items 1, 2, 4, 5, 6 are pure finishing labor — no design decisions. Items 3, 8, 9 are
owner rulings that cost minutes. Item 7 is the only place the planet is missing
something its own spec still promises.

---

## PENDING — what this report could not do

**Phase 2 (in-game screenshot STARE) and Phase 3 (text/plot-leak pass) are NOT done** —
both need the next bridge window.

What Phase 2 CAN change: it is the acceptance test the doctrine itself names ("the
picture is the acceptance test" — LOOK, not measure). It can (a) confirm or clear the
river-shape doctrine (winding/acute vs comb — invisible at global render scale), (b)
settle the Gelatinous streak-vs-patch question on the real globe, (c) adjudicate the two
Hutt palaces and the 14 landmark collisions at tile grain, (d) run the river-mutator
gate check this export couldn't. What it CANNOT change: the measured topology, roster,
and gate findings above — those are counted, not seen, and a screenshot will not
un-count them. Phase 2 could still DEMOTE the verdict if closeups reveal shape defects
(comb rivers, ruler roads) that the audits structurally cannot detect — that is the one
genuinely open risk.

What Phase 3 CAN change: naming/lore leaks (vanilla-source names, plot spoilers in
landmark/settlement text) would add rows to the punch list — all S-cost rename work. It
cannot move the structural verdict either way.

Also honestly unmeasured this pass: true hex-adjacency for the road-reachability checks
(great-circle proxy used, two instruments bracket 18–22), and per-file landmark icon
texture existence on disk.

---

## Provisional verdict

**Yes — this is THE map, pending the Phase-2 STARE.** The structural spine — factions at
zero delta, monotonic climate, a connected and directionally-correct river system, a
real road network, a dayside with identity and a nightside with structure — is finished
and audits clean; everything on the punch list above is finishing-pass work (roughly two
to three focused sessions, dominated by mutator hygiene and road pruning) plus three
cheap owner rulings, and nothing found in any lane calls for re-authoring a single thing
the owner has already judged. Ship-blocking risk now lives only in what the audits
cannot see: the closeup shape of rivers and roads, which is exactly what the owed
in-game STARE exists to judge.
