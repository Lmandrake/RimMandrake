# Ash'karr — the studio review (2026-09-08)

*WORLDMAP_FINAL_REVIEW_1 · BENCH/Fable, one sitting, owner present. Baseline
**V27** (`WORLDMAP_V27_cs_icons_scoped_2026-09-09`), canon CSV drift zero. Every claim
below is tagged **MEASURED** (a number from tonight's live exports or an in-engine
audit), **SEEN** (a named screenshot), or **JUDGED** (Fable's call on evidence shown).
Evidence root: `D:\Luke\dev\Rimworld\Transient\final_review\` — exports, four audit
lanes' findings files, and 30 screenshots.*

---

## Verdict

**Yes — this is THE map, pending an eleven-item punch list, none of which is
structural.** The planet has a real thesis (one sun that never moves, and everything —
temperature, water, biome, faction, road — arranged as an argument about distance from
it), and the thesis survives measurement: the dryland ladder is strictly monotonic
across all eighteen 5° arc bands (MEASURED, 63.6 °C → 15.2 °C with no break over 3 °C).
It survives the eye: from orbit the planet reads day-face / terminator / night-face as
three acts with different color languages, and every named site I flew to reads as a
place, not a paint job. The defects found are finish-work: a broken bookkeeping field
on rivers, seven misplaced mutators, some barren patches, doc drift, and a handful of
aesthetic calls that are yours to make. Nothing found tonight argues for repainting
anything large.

---

## Part I — What is genuinely excellent (each with how to push it further)

**1. The Scald is the best single composition on the planet.** (SEEN: `C01_Scald.png`,
`C05_GreentideDelta.png`) The crater sea ringed by green gallery jungle, the banded
brown Scald Spine, rivers visibly radiating outward into the Hollow Verge — the R1
"perched ocean that spills the world's rivers" ruling is *visible from orbit without
being told*. MEASURED support: 4 of 5 river components touching the Scald run cleanly
terminator-ward; the rim's 79 tiles average 561 m.
→ **Leverage:** this is the box-art shot. Make the Scald the campaign's cartographic
identity — loading screen, scenario map pin, the first place a tutorial caravan is sent.
And the rim's one 1 m tile (MEASURED) may be your natural "gate" — if it's where a
river exits, name it and put a settlement or toll on it instead of repairing it.

**2. The antistellar cap lands its metaphor.** (SEEN: `N1_night_b0.png`,
`S17_antistellar.png`, `C03_UmbraLake.png`) The near-black disc with the ice ring
around it reads exactly as "the exhaust port of a machine"; the lake is a true black
mirror; the two droid icons sitting on the cap are legible plot seeds. The lobed
(ruled, anti-bullseye) ring structure shows clearly at S17.
→ **Leverage:** the cap is your poster for the *second* act. Consider one faint
light-detail on the lake tile group at high zoom (aurora tint) so the "brightest sky on
the planet" claim reads in orbit view too — right now the cap's darkness says fuel but
not aurora.

**3. The terminator is a planet-scale gradient that no vanilla world has.** (SEEN: T1,
T2, T3, T5) Cream → gold → purple PoisonForest band → charcoal Crags → ice blues, in
one sweep. This is the profile shot that says "tidally locked" with zero UI.
→ **Leverage:** the two seas sit right in this transition and are underused as views —
a "Terminator" orbit-view camera bookmark (or the scenario's opening camera) would sell
the setting in the first five seconds.

**4. The Rust Cathedral + Ancient Asphalt is environmental storytelling done with two
assets.** (SEEN: `C02_RustCathedral.png`) The dark plateau carpeted in structure
debris, with the white highway hugging its edge and the complex-structures icons now
exclusive to machine country (after tonight's ruling), reads as "the works" instantly.
MEASURED: 5.78 mutators/tile, 65.7 landmarks/100 tiles — the densest ground on the
planet, and the icon layer now honestly says so.
→ **Leverage:** the asphalt's whiteness against dark ground is your strongest road
contrast anywhere — consider extending the asphalt class along the whole
dynamo-conduit story line (Cathedral → Fall Line → cap), so the ancient network is
traceable by color the way the dirt-road network traces the living one.

**5. The naming layer is publication-grade.** (JUDGED, full harvest in
`player_strings.md`) The Homestead Defense League's 28 settlements are *all* named in
one water-obsessed farm dialect (Whistledew, Cloudtrap, Reservoir 7, The Vaporworks) —
that is a culture told entirely through a name list. The Hutt possessive grammar
(Gorga the Immense's Palace, Zeddo's Toll), the Free Droids' abstractions (Unbound
Exception, Second Speaker, The Fair Copy), the Helix's clinical menace (Specimen Hall,
The Revision) — each faction is identifiable from names alone. Faction descriptions
carry real voice ("hostile the way a creditor is hostile"; "a memory of being property
that they intend never to repeat").
→ **Leverage:** these registers are strong enough to drive *systems*: name-generator
rule packs per faction for new sites/caravans/pawns would keep every future object
on-voice for free. The one gap is below in Part II (landmark name reuse).

**6. The region layer works at the player's altitude.** (SEEN: closeups) 71 features,
no orphan biomes (MEASURED), and the labels — Sootreach, Fuelmere, Tallow Ground,
Hollow Verge — consistently land on-theme. Weeping-stones' hilliness matches its sheet
to 0.0pp (MEASURED); the seas' raggedness numbers separate the crater (76) from the
true seas (365–404) exactly as doctrine says.

---

## Part II — Findings (each with corrective and cost)

### A. Mechanical (MEASURED)

**A1 · riverDist is broken planet-wide.** 6 of 11 river components (295/335 tiles)
have multiple riverDist minima; 33 tiles carry riverDist 0 while holding rivers; 13.5%
of edges jump by >1 (worst 18). Flow *topology* is fine (0 asymmetric, 0 orphan links,
def ladder grows toward mouths); the direction *bookkeeping* is what's wrong, and
anything downstream that reads riverDist (map-gen river width, our own tools) will
misbehave. → **Corrective:** a renumbering pass — BFS from each component's true mouth
(pick per component, the Scald components' mouths are their rim exits), write
riverDist, verify single-minimum per component. One scripted bridge pass + save.
**Cost: ~1 evening, no repaint.**

**A2 · Seven coastal mutators on dry tiles.** CoastalIsland ×4 (tiles 239, 361, 3507,
4569), Archipelago ×2 (2249, 13203), Peninsula ×1 (11851) — none within one ring of
water; the engine's own audit misses them because it only checks `Coast`. →
**Corrective:** remove the seven (they generate coast content on maps with no coast).
**Cost: minutes.**

**A3 · 34 tiles of Ancient Asphalt Highway are invisible under the propane cap.**
`AB_PropaneLakes.allowRoads=false` hides real stored links — the only biome/def pair
hiding roads on the planet. Lore-reading: buried conduit roads to the works is *good*;
invisible-by-accident is not. → **Corrective (recommended):** patch
`allowRoads=true` onto AB_PropaneLakes (matches your "all our biomes allow roads"
ruling and makes the dynamo's old network traceable); alternatively delete the links.
**Cost: one patch line + restart to see it.**

**A4 · Road litter: 46 isolated fragments (2–9 tiles) + 17 dead-end stubs.** The main
network is one healthy 1,126-tile component holding 78 of 95 NPC settlements (all 18
off-road settlements match their factions' own isolation lore — Deep Desert Tribes 9/9
off-road is the doc working). The fragments mostly read as erosion relics — fine as
ruins *if intended*. → **Corrective:** one pass sorting the 46 into "keep as ruin"
(rename nothing, they're fine) vs "connect" vs "delete"; the 17 junction stubs are
likelier candidates for deletion. **Cost: ~1 hour with the list already written.**

**A5 · landBiomeSubmerged = 181, decomposed.** 54 are the Rot's ruled Twilight-shore
tiles (its sheet claims exactly 54 — owned). The other 127 hug sea shores across seven
land biomes and are almost certainly the waterline ribbon working as designed — but no
document *owns* them the way the Rot's sheet owns its 54. → **Corrective:** one
paragraph in `water_doctrine.md` claiming the ribbon (count + why), or a repaint if
they're actually spill. **Cost: a doc paragraph after a one-hour look.**

### B. Content richness (MEASURED)

**B1 · Four biomes are mutator-barren; the Grey Sea is *empty*.** PoisonForest (74%
of tiles carry zero mutators), RUT_TwilightSea (80%), Desert (53%), Wasteland (63%) —
and RUT_GreySea has **zero landmarks in 429 tiles**. The two largest land biomes and
the terminator band read thin at closeup exactly where the player will caravan most.
Meanwhile ~38% of all mutator placements are two solar-power defs (VEE_More/Less
SolarPower — invisible texture, real gameplay, no *read*). → **Corrective:** a
placement wave for these five, from each sheet's own §7 uniquely-available list
(Poison Forest: vent fields, metal-plated groves; Desert: shade-line features; the
seas: seamounts/wreck moorings/mat features for the diving arc). Keep the dune sea
barren — its emptiness is ruled. **Cost: one FOUNDRY item per biome, bridge work,
no restart.**

**B2 · Landmark name reuse.** 32 names appear on 2+ landmarks; "Dead Sarlacc" ×7 is
the worst — and one of those seven is about to become The Gaping Doom. →
**Corrective:** hand-name the ~15 that matter (every sarlacc deserves what
GAPING_DOOM_SITE_1 is getting), let a namer variety pass cover the rest. **Cost: an
hour of naming, the fun kind.**

**B3 · 14 settlements share a tile with a landmark.** AddLandmark never validates
(known engine gap). Some stacks are surely deliberate (a palace ON the oasis). →
**Corrective:** eyeball the 14 (list in findings file), keep the good ones, nudge the
accidents one tile. **Cost: minutes each.**

### C. Docs vs world (MEASURED, all doc-side)

**C1 ·** `ASHKARR_WORLD_DEFINITION.md` §7 settlement targets disagree with the live
roster: Jawa Trade Moot 2 vs 4 documented, Hutt Cartel 12 vs 17, Homestead 27 vs 33.
You adopted the rejigger, so the *world* is canon and the *doc* is stale — but
confirm those three shortfalls were rejigger decisions, not losses. **C2 ·**
`the_one_map.md`'s water-body figure ("three bodies ≥8") predates the lake — now four,
12 puddles. **C3 ·** README grammar table's crags count (fixed tonight) had a sibling:
`forsaken_crags.md` self-flags its hilliness split as stale (9.2pp off). **C4 ·** the
`unused_mutators_census.md` counts are from a superseded CSV (6,710 vs tonight's
14,290 mutator-bearing tiles) — mark it superseded in place. → **Corrective:** one
doc-sync pass, ~30 minutes, cite tonight's exports.

### D. The eye (SEEN — aesthetic, each your call)

**D1 · The Hollow Verge river comb.** (C01, C05, C09, C10) The Scald's southern
drainage runs as many straight, parallel, same-angle tributaries — at closeup it reads
as a rake, not a watershed. It is the one place the hand shows. → **Corrective
options:** stagger/branch ~⅓ of the parallel runs (respecting the uphill-water
lesson), or thin them and let the survivors meander. Medium-cost repaint of ~40 link
rows; the region is gorgeous otherwise.

**D2 · The ring's eclipse shadow is a hard-edged black slab.** (D2, T2, T4, T7, T8)
The planet's shadow on the ring is physically right and dramatically good — but it
renders as a crisp rectangle that reads as a missing mesh chunk, not a shadow. →
**Corrective:** check the Atmosphere mod for a shadow-softness setting; if none,
accept (it genuinely is an eclipse) or ask the mod. Note the ring *bands* themselves
now render clean at every zoom I flew (SEEN, D2/D4/T3 vs your 21:07 artifact
screenshot) — tonight's band-limited texture appears live already.

**D3 · Label collisions at the Scald.** "Scald" and "Scald Spine" overprint each
other at most zooms (C01, C05, C09). WORLD_FEATURE_LABELS_OVERSIZED_1 already tracks
the family; add these two as the worst pair. → **Corrective:** shrink Scald Spine's
maxDrawSize or bend its drawAngle along the ridge.

**D4 · Hex-crisp shallows.** (C06, C08, C12) The waterline ribbon's pale hexes have
sharp edges against deep water — charming board-game read at closeup, slightly
artificial at globals. Judged acceptable; if it ever bothers you, the fix is texture
feathering in the waterline mod, not the map.

**D5 · The Rot's world-tint runs cold.** (C10, C12) Its lavender-grey reads
nightside-ish, so Sweatwood/Tallow Ground — *dayside* woods at +12..24 °C — look
chilly beside the desert. One-line world-color warm-shift on AB_MycoticJungle would
fix it; or keep it as "the gut looks wrong on purpose." Your call.

**D6 · The pale dayside is vast and empty — and right.** (D1, D4, C04) At global zoom
the day face is two-thirds cream. That *is* the Dune Sea argument, and the golden
stipple + Cathedral anchor + road web keep it from being dead screen. No corrective —
noted so nobody "fixes" it later.

### E. Text & leak check (JUDGED — three items are yours)

The harvest (`player_strings.md`) is clean of past-cause and future-plot leakage with
three exceptions to rule on:

**E1 ·** `RUT_PropaneLake`: "*Nothing hot has touched it since the war.*" Present-tense
fact, but it's a gun on the wall aimed at the crater ending. I read it as legitimate
in-world survey knowledge (the war is public history — the Free Droids' own blurb
references it). **Keep / soften — your call.**

**E2 ·** The scenario crawl names the hull **Rakatan** openly, while
Forsakens=Rakatans=Ancients is §P/GM reveal-gated lore. A sharp player holding
"Rakatan hull, older than the Cartel's name for the sand" + the Cathedral will
pre-connect the reveal. If the crawl's word is doing deliberate foreshadowing, keep;
if the gate matters, "a hull with no maker's name" preserves the mystery at zero cost.
**Your call — this is the only true leak candidate found.**

**E3 ·** Label-case register is mixed: the rename patch title-cases ("the Rot", "the
Propane Lakes") while our own defs go vanilla-lowercase ("the poison forest",
"nightside ice", "pyrelands"). Pick one register; title-case-as-proper-noun fits a
named world better. **Minutes to fix once ruled.**

### F. One curiosity, not a defect

**F1 · Tile 5873.** A single 1,042 m island — with Caves — surrounded on all six
sides by the propane lake (the lint's `singleTileIslands=1`). Nobody's sheet mentions
an island in the black mirror. Accident of the elevation pass, or the single best
unbuilt landmark site on the nightside (the lab's access shaft above the fuel?).
**Ruled, not repaired — I didn't touch it.**

---

## Part III — The punch list (gating, in recommended order)

| # | item | type | cost |
|---|------|------|------|
| 1 | A2 seven coastal mutators removed | mechanical | minutes |
| 2 | A1 riverDist renumbering pass | mechanical | evening |
| 3 | A3 allowRoads on the cap (or delete 34 links) | ruling + patch | minutes + restart |
| 4 | E1/E2/E3 text rulings | owner | minutes |
| 5 | A4 road-litter sort (46 fragments, 17 stubs) | curation | hour |
| 6 | B1 enrichment wave: Poison Forest, Desert, Wasteland, two seas | content | per-biome items |
| 7 | B2 landmark naming pass | content | hour |
| 8 | B3 the 14 landmark/settlement stacks | curation | hour |
| 9 | A5 waterline ribbon owned in water_doctrine.md | doc | paragraph |
| 10 | C1–C4 doc sync | doc | 30 min |
| 11 | D1 river comb + D3 labels + D5 Rot tint + F1 island | owner aesthetics | per call |

Items 1–3 are the only ones I'd hold the freeze for: they are the map disagreeing with
itself. 4–11 are polish the freeze can carry as known work.

---

## Appendix — method & evidence

Fresh live exports of all seven layers (manifest in `Transient/final_review/MANIFEST.json`:
21,872 tiles · 1,566 link tiles · 21,872 mutator rows · 2,821 landmarks · 196 objects ·
71 features), in-engine `world_lint` (309 findings, decomposed above) and
`world_mutators_audit` (104 stale-Coast, superseded by A2's stricter check). Four
parallel audit lanes with calibration anchors, findings in
`Transient/final_review/findings/` (rivers · roads_settlements · mutators_landmarks ·
seams_landforms — note: the seams lane's Webwork–Greentide "unowned seam" headline was
disproved on verification, 11 cross-mentions; its Desert–PoisonForest silence and
Weeping-Stones–Pyrelands silence verified true and stand in B1's neighborhood). Thirty
screenshots (18 global arc/bearing grid + 12 site closeups) in
`Transient/final_review/shots/`; two same-second filename collisions caught by md5sum
and reshot. Seam verification, the 181-tile decomposition, and tile 5873's inspection
were re-measured in-window before reporting. Sheets-vs-map numeric harmony was
established earlier tonight (20 sheets exact + 5 amended) and is not re-argued here.
