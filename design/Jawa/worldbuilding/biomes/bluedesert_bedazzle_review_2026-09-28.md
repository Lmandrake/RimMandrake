# Blue Desert — bedazzle review (movement 1 + movement 2 prep)

**Item:** BLUEDESERT_BEDAZZLE_SITTING_1 · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1
**Date:** 2026-09-28 · **Author:** DESIGN subagent (Fable)

## 1. Nine-mark scorecard

State legend: **RULED** (owner decision recorded) / **DESIGNED** (spec exists, no ruling needed or ruling embedded) /
**BUILT** (def/C# ships in `src/RimMandrake/BlueDesert/`, MEASURED this pass). All Blue Desert
ledger items are CLOSED (`BLUEDESERT_RM_MOD_BUILD_1`, `BLUEDESERT_DESIGN_SITTING_1`,
`BLUE_DESERT_LIFE_AUTHORING_1` — all in `items/closed/`); the mod `mandrake.rm.bluedesert`
exists with BiomeDef, 3 fauna, 3 flora, cold wax, charge hediffs, halo effecter, and
`BlueDesertLife.cs` compiled (`Assemblies/RimMandrake.BlueDesert.dll` + `.srchash`).

| # | Mark | Verdict | Evidence |
|---|---|---|---|
| 1 | Unique mechanic | **FILLED (built)** | The warm-detonation charge family — no other biome has it: `RM_HydrocarbonCharge` (fauna explode on death), `RM_CompPlantCharge` (flora chain-detonate above +5 °C, KillFinalize-only so cutting/grazing is safe), `RM_ColdWax` temperature-ruin→wick, `RM_ButaneGut` for foreign grazers. All shipped in `BlueDesertLife.cs` + `Defs/HediffDefs/RM_BlueDesertCharges.xml`; per-mechanic Mod Settings toggles built (`BLUEDESERT_RM_MOD_BUILD_1` §8, closed). The dorrak Hump-shot trigger and the field-as-fuse chain (life brief §6b) are the "no other biome does this" core. |
| 2 | Discoverable technology | **MISSING** | Nothing teaches the player something they keep. The nearest seam is ruled but inert as lore only: the five quarry epochs (Rakata → war era → Czerka → Empire → player, ruled by card 2026-09-24, sheet §8) with "later epochs left translations of the Rakatan script that trail off" — a ready-made discovery ladder with no mechanism attached. Slate candidates A/B below aim here. |
| 3 | Unique resources | **PARTIAL** | Cold wax is BUILT (`RM_ColdWax`, butchery + harvest product, refines to chemfuel — recipe itself still on the carried-forward list). **Blue ice — the sheet's ⭐ "golden" mineable, the water-taxonomy top row — is not built**: zero hits for any BlueIce def in `src/` (MEASURED grep this pass); `WATER_KINDS_TAXONOMY_1` still open. The fallen (meteoritic metal/wreckage/freeze-dried corpses) are ruled on the sheet (§7) with no injection built. |
| 4 | Surprising creatures | **FILLED (built), enrichment ruled-unbuilt** | The krissek (blue-fire halo at speed, detonates when killed — `RM_KrissekHalo` effecter shipped) and the dorrak (shoot the Hump and it takes you with it) are genuine "what" moments, BUILT in `RM_BlueDesertFauna.xml`. The four depth-cast creatures ruled in at the 2026-09-24 sitting — **zhaaz, vrisk, dovvik, utikka** — exist only in roster/sheet prose: zero hits in `src/` (MEASURED grep). |
| 5 | GIANT beast | **MISSING** | No colossus. Largest native is the dorrak at `baseBodySize 1.6` (life brief §3a). The zhaaz is an engulf-feeder slush lobe with no ruled size. Slate candidate C (the vhaulk) proposed below. |
| 6 | Gravship touch | **PARTIAL (ruled, unbuilt)** | ⭐ THE COLD HOLD ruled by card 2026-09-24 (`BIOME_SHIP_CONTRIBUTIONS_1`, sheet §7): blue-ice blocks as distilled water stock + butane flora/Burner glands as a chemfuel windfall safe only refrigerated — "one cooling failure aboard and the pantry is a bomb." Nothing built (blue ice itself unbuilt, mark 3). The cold-wax half works aboard today for free (`CompTemperatureRuinable` cares only about room temperature), but the ruled ship-facing framing (water stock row, the pantry-bomb story) has no defs. |
| 7 | Soundscape | **MISSING (prose only)** | Sheet §9 has the right sentence — "wind over ice; the hiss of drift; the crack of a thaw; then the boom" — but no SoundDef, no ambient set, nothing in the mod's Defs (no Sounds folder, MEASURED). The detonation chain has default vanilla explosion audio. Slate candidate E. |
| 8 | Interesting weather | **PARTIAL (ruled + engine-proven, unbuilt)** | The strongest ruled-unbuilt gap. Three weathers ruled with engine mechanisms RimSage-measured at the 2026-09-24 sitting (sheet §4b amendment): ice-sand drift on Odyssey's sand grid (owner typed: *"But we need to do testing to make sure it goes deep"* — a live deep-drift test gates done), the Haze with exposure hediff via `EnvironmentalWeatherExtension` (zero new C#), ice fog at BlindFog-verbatim severity + `maxRangeCap`. The shipped def is still `Clear 100`, all else zeroed (`RM_BlueDesert.xml` lines 157–170, read this pass). This is ticket-ready, not volley material. |
| 9 | Relationship to the gods | **MISSING** | Nothing anywhere — sheet, sitting rulings, roster, mod — places the Blue Desert in the ideoligion/lore layer. The raw material is unusually good (the sky gives its dead back; the Rakatan warnings as scripture nobody can read; the field where every civilization's hubris is preserved), but no ruling exists. Slate candidates A/H. |

**Score: 2 filled, 3 partial, 4 missing (2, 5, 7, 9).** The misses cluster exactly where the
volley should aim; marks 1 and 4 are already at Baroque depth and need commissioning
(art) rather than ideation.

## 2. Roster gap census

Land biome — sea/fish rows n/a (roster's own fish ruling: "no fish — zero water, zero rivers").
Q11a binds: the `RM_` tier must be rich enough to stand alone.

### Fauna as wired today (`RM_BlueDesert.xml` `<wildAnimals>`, read this pass)

| row | commonality | state | role |
|---|---|---|---|
| `RM_Vekkit` (picker) | 0.8 | BUILT | scavenger, herd, the harmless one |
| `RM_Dorrak` (swallower) | 0.5 | BUILT | armored grazer, hump-shot bomb |
| `RM_Krissek` (burner) | 0.35 | BUILT | fast predator, halo, detonates |
| `AA_Thunderbeast` | 0.005 | donor import, MayRequire-gated inline | trace-experiment (owner review row) |
| `Vapaad` | 0.5 | canon SW, rides `WildAnimals_BlueDesert.xml` (patch EXISTS, checked) | campaign-tier addition |

### Ruled-in, unbuilt (2026-09-24 sitting, roster `new_defs`) — these ARE the fill, already ruled

**zhaaz** (living propane-slush engulf-feeder) · **vrisk** (kite-thin Haze-skimming flier —
gets real `MaxFlightTime` flight per the standing flyer rule) · **dovvik** (proboscis
defuser draining plant charges) · **utikka** (fist-sized palefloss-cropper, krissek's
staple prey). Building these four is owed FOUNDRY work, not a new ruling.

### Food-web / role holes once the ruled eight exist

- **No colossus** (mark 5) — the only structural fauna hole. Proposed: vhaulk (§3).
- **No creature that uses the weather** — drift and fog are ruled as pure sky effects;
  nothing hunts from them. Proposed: murrek (§3).
- **No voice** — a biome sold on silence-then-boom has nothing that sounds. Proposed:
  sivvet + virrell (§3).
- Otherwise the pyramid is sound: 3–4 flora producers → utikka/dorrak grazers → krissek
  predator → vekkit scavenger → zhaaz engulfer, vrisk aerial, dovvik specialist. Eight
  natives + one flora addition clears the "rich standalone" bar for a sparse-by-doctrine
  biome (donor read `animalDensity 0.5` = "the sparsest def defined" — richness here is
  role diversity, not headcount).

### Multi-homed rows — ANNOTATE for the sitting, do not evict

| row | homes (grep of biome defs, this pass) | note |
|---|---|---|
| `AB_CrystalHorn` (flora) | Blue Desert + Propane Lakes ("propane lakes and blue desert only" — owner review 2026-09-20 move) | deliberate two-home by owner review; also in ban-1 tension below |
| `AB_ToxiGrass` (flora) | Blue Desert (+ Wasteland lineage; appears in `RUT_Wasteland`/`RUT_Umbra`-family defs) | owner review move row, "blue desert rare" |
| `PoisonPlantTallGrass` (flora) | Blue Desert + poison-forest-family defs | owner review move row |
| `AA_Thunderbeast` | Blue Desert trace + other AA_* donor placements | trace-experiment; donor import, not ours to single-home |

⚠️ **Standing ban-1 tension, still the owner's:** all three donor flora are ordinary
water-metabolism plants inside the "no water-based plants" hard ban (sheet §6.1). Both the
`RUT_` twin's comment and `RM_BlueDesert.xml`'s own comment flag it and defer to the owner;
no pass may cut them on its own authority. Carried to §5 as an open question — this sitting
is the natural place to finally rule it.

### Flora census

3 native (palefloss/glassfern/chimeglobe — names REAFFIRMED as pre-law exception, do not
rename) + 3 donor (tension rows). "Plants stay small" is ratified physics, so the flora
hole is not a big anchor plant but **role variety within smallness** — nothing rare, nothing
that does anything but detonate. One addition proposed (§3).

### Art state (check-before-queueing rule applied)

The build item recorded fauna texPaths pointing at vanilla placeholder art and flora PNGs
absent, with **20 art jobs already queued** (`BLUE_DESERT_LIFE_AUTHORING_1` citation) and 9
in `done/`, 11 pending as of 2026-09-24. ⛔ Do not re-queue those subjects at movement 4;
verify the pending set landed before commissioning anything new.

## 3. Proposed roster fills

All NEW inventions in the Blue Desert's own accent (`Alien_Bestiary.md` §1 register as the
built cast uses it: one–two syllables, doubled consonants, hard stops, the name never
describes the mechanic; `vh-` marks apex). Every name collision-swept this pass with
`grep -ri` across `src/`, `design/`, `infrastructure/state/` — sweep sanity-probed on
`korrum` (57 files, instrument proven able to find). One home each: the Blue Desert.

| name | defName | kind | result of sweep | concept + role |
|---|---|---|---|---|
| **vhaulk** | `RM_Vhaulk` | creature (GIANT) | **0 hits — clean** | The colossus (mark 5). A house-sized sealed swallower-lineage giant, six pillar legs, a rolling cistern of pentane sludge that grazes whole floss fields in a pass — the biome's slow mountain. Killing one is a strategic decision: the largest detonation on the planet's surface (it IS the anti-siege weapon the quarry epochs learned to fear). Tapping one alive at a valve part is the mad-brave harvest. `vh-` apex prefix earned. |
| **murrek** | `RM_Murrek` | creature | **0 hits — clean** | Drift ambusher (marks 4+8 coupling). A flat, wide thing that buries itself under ice-sand drifts and erupts under prey — the ruled drift weather made into a predator's tool: after every drift storm the landscape is re-armed. Doubled `rr`, hard `-ek` stop (krissek's clade cousin, slower and meaner). |
| **sivvet** | `RM_Sivvet` | creature | **0 hits — clean** | The choir (mark 7 in fauna form). A knee-high vent-throated thing whose gas-exchange spiracles sound organ tones; packs sing at the ablation line at "dusk" (activity cycle). Harmless, beautiful, and a working alarm: they go silent when something big moves. `-et` small clade, doubled `vv`. |
| **virrell** | `RM_Virrell` | flora | **0 hits — clean** | Whistle-reed (mark 7's floor). A fractal tube whose branches sound in wind — fields of virrell ARE the soundscape between storms; the pitch rises as the plant's charge ripens, so a keen-eared colonist hears which field is about to be dangerous to warm. Same charge comp family, `visualSizeRange` under the smallness law. |

Rejected during sweep: **skovva** (1 hit — already used as a candidate-name column entry
for `AA_RedSpore`/vezzok in `noncanon_beast_names_crags_nightside_contagion_slime.md:170`;
avoided rather than argued). **rukka**-family roots avoided per the life brief's own
recorded collision (Rot's rukka cap).

These four are **pitches for movement 2's ruling**, not filed defs — the owner admits or
strikes at the sitting. None re-homes a neighbour's species; all pass the admission test
(hydrocarbon-metabolic, cold-stable, warm-reactive — each carries the charge family).

## 4. Candidate mechanics slate

Ranked pitches for the four-turn volley, aimed at the unfilled marks (2, 5, 7, 9) and the
two ruled-unbuilt partials (3, 6, 8). All DLCs assumed present. These are pitches the owner
refines, not specs.

**A. The Warnings — reading the Rakatan script** *(marks 2 + 9; rank 1)*
The five quarry epochs are already ruled; this makes them a discovery ladder the player
climbs. Each quarry tableau examined yields a fragment — later epochs' trailing
translations first, the Rakatan original last — and completing tiers grants permanent
knowledge: first the map reveal of buried hazards near quarries, then **cold-cutting**
(mining technique: ice extraction that never crosses the phase line, so crysalises don't
trigger), finally the full reading of what the warnings actually say. *Engine:* Anomaly's
entity-study/monolith shape (study interactable + accumulating knowledge category) or
Royalty techprint-style unlocks; injected tableaus ride the already-ruled KCSG quarry
templates. *Trade-off:* the best candidate for "the biome teaches you something you keep,"
but it couples to `HORRORS_RAIDING_FACTION_1`'s crysalis triggers (cross-item), and the
payoff needs the quarry injections built first.

**B. Blue-ice quarrying, done properly** *(marks 3 + 1 deepened; rank 2)*
Build the ruled ⭐ resource: `RM_BlueIce` mineable blocks (distilled-purity water,
"golden" value) whose extraction *warms the quarry face* — every N blocks cut rolls
against the thaw table: nothing, a fallen-debris find, or a siege-form release. Mining IS
the biome's push-your-luck loop; cold-cutting (candidate A) is its earned counter.
*Engine:* a `RockBase`-family mineable with custom `mineableThing`; the thaw roll is a
small comp on the mineable or a MapComponent watching mined cells — the greatbole
heartwood precedent shows the whole shape works. *Trade-off:* the release half depends on
Horrors content that is another item's; can ship with debris-only rolls first.

**C. The vhaulk — the walking cistern** *(marks 5 + 4; rank 3)*
The colossus (§3). Rare (0.02-class commonality), neutral, ignores you; the decisions it
creates are the mechanic: kill it near your base and you've detonated a district; lure it
toward a siege camp and it's a weapon; tap it alive (a work-giver operation at a valve
body part, dorrak-hump logic scaled up) for a cold-wax windfall at manhunter risk.
*Engine:* big animal + `RM_HydrocarbonCharge` at radius ~15, `startingHediffs`, the
existing hump-part trigger pattern; no new mechanism class. *Trade-off:* a 15-radius Flame
explosion needs balance care near the flora chain (one vhaulk death can glass a quarter
map — arguably the point).

**D. Weather build-out — the three ruled skies** *(mark 8; rank 4 — ticket, not volley)*
Ice-sand drift (Odyssey sand grid + blue-white tint patch, gated on the owner's ruled
"goes deep" live test), the Haze (exposure hediff, zero new C#), ice fog
(BlindFog-severity + `maxRangeCap`). All three mechanisms already RimSage-proven and
ruled 2026-09-24. *Trade-off:* none design-side — this is FOUNDRY work the volley should
simply ticket; listed so the slate is honest about where mark 8 closes.

**E. The sound of the phase line** *(mark 7; rank 5)*
An ambient set that is the sheet's §9 sentence made audible: wind-over-ice base layer,
drift hiss during sand weather, virrell fields whistling, sivvet choirs at the ablation
line — and one designed audio *mechanic*: a sharp cracking cue in the seconds before a
chain detonation propagates, so a player who listens gets a beat to run. *Engine:*
`SoundDef` ambients keyed to WeatherDefs + a sustainer on the charge comp's two-longtick
warm countdown (the delay already exists in `RM_CompPlantCharge`, built). *Trade-off:*
audio assets are a new pipeline ask (artpipe is images); scope the cue to reuse/retint
vanilla SFX first.

**F. The Cold Hold, built** *(mark 6; rank 6)*
Execute the ruled ship contribution: blue-ice blocks as the ship's water stock
(`WATER_KINDS_TAXONOMY_1` row), and a labeled ship-pantry story — a Cold Hold room whose
cooling failure turns stored wax/flora into a countdown the player hears (candidate E's
cue aboard). Plus one new ship touch in the biome's own voice: **drift burial while
landed** — ice-sand accumulates against the grounded gravship's windward hull (sand grid
already does structure-adjacent accumulation), costing a dig-out on departure after a
storm. *Engine:* item defs + the already-shipped `CompTemperatureRuinable`; drift-vs-ship
is the same sand grid the weather rides. *Trade-off:* blue ice (candidate B) is the
prerequisite; burial annoyance needs tuning so it reads as weather, not tax.

**G. The murrek's drifts** *(marks 4 + 8 coupling; rank 7)*
§3's ambusher as a mechanic: after each drift storm, buried murrek re-seed at fresh drift
cells; drifts near the colony are a clearable threat (dig the drift, flush the thing).
*Engine:* a MapComponent listening for the weather's end + burrow/unburrow job pattern
(sand grid cells as spawn candidates). *Trade-off:* needs the drift weather (D) first;
burrow AI is real C# — the biome's first genuinely new job driver.

**H. The Field of the Returned — the gods layer** *(mark 9; rank 8)*
The ideoligion reading: the Blue Desert is where the sky gives back its dead — the one
place on Ash'karr where what is lost returns, incorruptible. Shape options for the owner:
a memes/precept package (a "Returning" precept — orbital dead deserve retrieval and rites;
the ablation line as a pilgrimage site with a ritual), the Rakatan script as sacred text
nobody may read aloud, or the quarry warnings as the gods' own voice ("the ones who dug
are still here"). *Engine:* Ideology precepts + ritual on an injected site piece; all
content-side. *Trade-off:* pure lore-layer work whose right owner-shape (campaign
ideoligion vs biome-local flavor) is genuinely his call — see §5 Q3.

**I. The dovvik defuser economy** *(mark 4 depth; rank 9)*
When the dovvik builds (ruled), give its mechanic a player face: a drained plant is
charge-safe for a day (visible tint), so wild dovvik trails are natural safe-paths through
floss fields — and a tamed dovvik is a living minesweeper. *Engine:* the drain comp is
already the ruled mechanic_load; safe-state is a flag + graphic tint on `RM_CompPlantCharge`.
*Trade-off:* taming contradicts the built cast's all-untameable stance — needs the owner's
word either way.

**J. Ablation-line salvage incidents** *(mark 3 depth; rank 10)*
A biome-local incident family: "the line gave something up" — a small skyfaller-less
surfacing event placing meteoritic metal / wreck pieces / a freeze-dried spacer (with
salvage and a story) at the ablation line, vekkit and sivvet converging as the visible
tell. *Engine:* `IncidentDef` + map-edge-biased placement; the freeze-dried corpse reuses
vanilla corpse gen frozen. *Trade-off:* overlaps the quarry/debris injections — sequence
after A/B so the two don't double-author "the fallen."

## 5. Open questions — RULED at volley turn 2 (owner typed, 2026-09-28; on the sitting's ledger)

1. **The three donor water-plants: CUT.** The ban stands — no water plants make sense
   here. `AB_ToxiGrass`, `AB_CrystalHorn`, `PoisonPlantTallGrass` come off the Blue
   Desert rows (`AB_CrystalHorn` keeps its Propane Lakes home).
2. **Admissions: ALL FOUR join the roster** — subject to (2a) below.
   2a. **Name-style ruling:** the four names badly need varied style, away from
   just two syllables — restyled set proposed at turn 3.
3. **Mark 9: BIOME-LOCAL LORE.** No campaign ideoligion defs — no precepts, no
   rituals. The Warnings/script/tableaus carry the gods layer as prose and content.
   Candidate H's precept shape is dead; candidate A carries marks 2+9 together.
4. **Tameability: relaxed.** The owner does not mind tameable creatures; the tamed
   dovvik minesweeper (candidate I) is approved.

**Plus a candidate-C refinement (ruled same turn): vhaulk detonation is
TRIGGER-GATED.** It explodes only when it dies from heat, ion or lightning damage —
and **ion is the trap: stunning it is one of the worst things you can do.** A plain
kinetic/cold kill leaves the cistern intact (the richest harvest, earned the hard
way).

---

*Movement 2 prep is complete on paper: the ruled-unbuilt fill (zhaaz/vrisk/dovvik/utikka)
is FOUNDRY-ready, §3 carries the new pitches collision-proven, and the slate above is the
movement 3 opening hand. Nothing in this review re-opens a frozen ruling; tile counts are
not cited as evidence of anything (paint is terminal).*
