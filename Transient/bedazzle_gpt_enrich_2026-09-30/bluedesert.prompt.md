You are a senior game designer consulting on a RimWorld mod campaign. The owner wants recommendations to ENRICH one biome that has already been through a design sitting. Be concrete, vivid and buildable in RimWorld 1.6 (XML defs, C# comps, Harmony, incidents, map components, weather, sounds).

BIOME: The Blue Desert

Standing rules of this project (binding on every recommendation):
- RimWorld 1.6 with ALL five DLCs assumed present; a Star Wars (old Tatooine / Jawa scavenger clan) campaign on one hand-made fixed planet. No worldgen, no alternative planets.
- Each animal lives in ONE biome unless there is an in-game reason (migration, life stage).
- Invented exotic names are fine; genuine Star Wars canon goes in a separate Star Wars layer.
- Heat is ONE planet-wide kind riding vanilla heatstroke; biomes differ by heat kind (overhead sun, low sun, ambient steam/volcanic).
- Animals or pawns must never vanish without a readable sign of what happened.
- If it flies in the fiction, it flies in the game.
- Every mod ships real Mod Settings.
- A biome's ideas must NOT echo another biome's signature; each biome has its own voice.
- The "bedazzle" bar is nine marks: unique mechanic, discoverable technology, unique resources, surprising creatures, a GIANT beast, a gravship touch, an interesting soundscape, interesting weather, a relationship to the gods.

WHAT THE OWNER HAS ALREADY RULED for this biome (ledger, verbatim; do NOT contradict or re-propose anything cut here):
- 2026-09-28: Volley turn 2 rulings, owner typed this session (verbatim in transcript): (1) Vhaulk detonation is TRIGGER-GATED - explodes only if it dies from heat damage, ion, or lightning; ION IS THE TRAP: stunning it is one of the worst things you can do (EMP against it triggers detonation). Plain kinetic/cold kills leave an intact cistern. (2) The four proposed names badly need varied style - not all two-syllable; BENCH proposes a varied set at turn 3. (3) Water plants CUT from Blue Desert rows - the no-water-plants ban stands, the three donor rows go (AB_CrystalHorn keeps its Propane Lakes home). (4) ALL FOUR proposed fills join the roster (vhaulk/drift-ambusher/choir/whistle-reed, names pending restyle). (5) Mark 9 is BIOME-LOCAL LORE, not campaign ideoligion defs - no precepts/rituals; the Warnings/script carry the gods layer. (6) Tameability wall relaxed - owner does not mind tameable creatures; tamed-dovvik minesweeper exception approved.
- 2026-09-28: Volley turn 4, owner typed: All. - full accept of the turn-3 hand: name set Vhaulk/Murrek/Ossivel/Virr as proposed, and ALL slate candidates ship (A Warnings biome-local, B blue-ice quarrying, C vhaulk trigger-gated, E sound, F cold hold + drift burial, G murrek drift re-seeding, I tamed dovvik minesweeper, J ablation salvage incidents; D weathers tickets regardless). Water-plant cut rides the ticket. Commission fires now; sitting stays open for the art review.
- 2026-09-29: Art review DONE by owner (sheet export committed: Transient/bedazzle_art_sheets_2026-09-28/blue_desert/sheet.decisions.json): 4 keep, 1 improve (RM_Vhaulk - east face needs frost + legs like north/south). Owner typed: "Need more plant-like members of this biome." - flora expansion owed, see BEDAZZLE_FLORA_EXPANSION_1.

THE BIOME'S DESIGN DOCS:
===== design/Jawa/worldbuilding/biomes/bluedesert_bedazzle_review_2026-09-28.md =====
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


===== design/Jawa/worldbuilding/biomes/bluedesert_bedazzle_cast_2026-09-28.md =====
<!-- status: cast bible — commissioned under BLUEDESERT_BEDAZZLE_SITTING_1 movement 4 -->
# Blue Desert bedazzle cast — the four new natives + art commission

**Item:** `BLUEDESERT_BEDAZZLE_SITTING_1` (movement 4: commission) · **Date:** 2026-09-28
**Feeds:** `BLUEDESERT_RULED_CONTENT_1` (defs) + `BLUEDESERT_MECHANICS_BUILD_1` (mechanics)
**Authorities:** the 2026-09-28 amendment block in `the_blue_desert.md` (ruled names and
facts) · `bluedesert_bedazzle_review_2026-09-28.md` §3/§4/§5 (developed pitches + turn-2
rulings) · `creatures/blue_desert_hydrocarbon_life.md` (the built cast's register, stats
laws, the charge family §2).

## 0. Shared law — every card below obeys this without restating it

- **Admission test** (sheet §4): hydrocarbon-metabolic, cold-stable, warm-reactive. Every
  card carries the charge family; a warm-safe native is a ban-3 violation.
- **The charge family, as built** (life brief §2; `Defs/HediffDefs/RM_BlueDesertCharges.xml`
  read this pass): one hediff **per species** — `RM_DorrakCharge`/`RM_KrissekCharge`/
  `RM_VekkitCharge` exist, so the new fauna get `RM_VhaulkCharge`, `RM_MurrekCharge`,
  `RM_OssivelCharge`, given by `PawnKindDef.startingHediffs`, each a
  `HediffCompProperties_ExplodeOnDeath` at the card's radius, **Flame 40** (the chain
  number, §2d), `destroyBody false` (corpses butcher to cold wax). Flora ride
  `RM_CompPlantCharge` (KillFinalize-only — cutting and swallowing are safe).
- **Shared fauna stats** (life brief conventions): `ComfyTemperatureMin/Max` **−100 / −11**
  (heatstroke above −1 °C IS the warm-reactivity, §1f), `ArmorRating_Heat 0` (a native in
  a neighbour's blast is a casualty), `Flammability 0.1` (flora 0.05), `MeatAmount 0`,
  `LeatherAmount 0`, `butcherProducts → RM_ColdWax`. Laws: 60 kg per bodySize, drawSize =
  body length in metres, health ∝ mass, melee best hit ≈ 12–15 × bodySize (Law 3).
- **Tameability is relaxed** (turn-2 ruling 4): the blanket `Wildness 1.0 / trainability
  None` stance is dead; each card sets its own. `BLUEDESERT_RULED_CONTENT_1` §6 carries
  the pass over the existing three.
- **Names are final** (ruled, styled for variance — one/one/two/three syllables): no
  restyling in defs; `vh-` stays the apex marker and only the vhaulk carries it.
- **Numbers are design choices**, calibrated against the built cast's anchors (dorrak
  bs 1.6 / krissek 0.9 / vekkit 0.45); FOUNDRY tunes in playtest, the *relationships*
  (who outruns whom, whose blast is biggest) are the ruled part.

## 1. RM_Vhaulk — the colossus

**Hook.** The biome's slow mountain: a house-sized sealed Swallower-lineage giant on six
pillar legs, a rolling cistern of pentane sludge that grazes whole floss fields in a
pass. It is neutral and it ignores you; every decision it creates is the mechanic. Kill
it near your base and you have detonated a district; lure it toward a siege camp and it
is a weapon; tap it alive and it is the mad-brave harvest. The quarry warnings include
*do not still the mountain* — and they mean the EMP trap.

**Class/role.** GIANT (mark 5). Apex herbivore, no predator, no threat until made one.
The read from a distance is terrain; the read up close is a mistake.

**Description (salvager register):**

> From the ridge it reads as a hill that was not there last season. Six legs like quarry
> pillars, a back like a buried tank, and it eats a floss field the way weather eats a
> footprint — whole, slowly, without noticing you. The crews call it the mountain and
> steer wide. The old warnings say do not still the mountain, and the crews who thought
> that was poetry are the reason the crews steer wide.

**Stats sketch.**

| field | proposed | grounding |
|---|---|---|
| `baseBodySize` | **6.0** (≈ 360 kg frame + cistern mass in lore) | above Thrumbo (4.0); the biggest thing on the nightside |
| `drawSize` (adult) | **7.0** | 7 m long; canvas **512** (Middenshell/Meltgut colossus precedent — scale must carry in the pixels) |
| `baseHealthScale` | **6.0** | ∝ mass, no discount — killing one is a campaign, which is the point |
| `ArmorRating_Sharp / Blunt / Heat` | 0.7 / 0.5 / **0** | a step past the dorrak's boiler plate; Heat 0 per shared law |
| `MoveSpeed` | **1.2** | below the dorrak (1.8); it never chases and never flees |
| `foodType` / `baseHungerRate` | `VegetarianRoughAnimal` / 2.5 | grazes flora fields whole — Vanish ingestion, so its own grazing never chains (§1g of the life brief) |
| `Wildness` / `trainability` | 0.98 / `None` | tameability relaxed elsewhere, not here: you do not tame a district-bomb, you learn to live near one |
| `manhunterOnDamageChance` | **1.0** | neutral until wounded; then the mountain notices you, slowly |
| `wildGroupSize` | 1 | there is never a second one on the map |
| commonality | **0.02** | the ruled 0.02-class rare — most maps never see one |
| `combatPower` | 450 | Thrumbo-class raid-point weight |
| `lifeExpectancy` | 200 | older than the quarry epochs' later attempts |
| `lifeStageAges` | Baby 0 / Juvenile 8 / Adult 25 | three stages; blast radius is life-stage-independent (§1d) |
| melee | slam Blunt 30, cooldown 4.0 | deliberately **below** Law 3's curve (bs 6 → 72–90): it is not a fighter, and the danger must never be its teeth |
| `butcherProducts` | `RM_ColdWax` × 80 | the cistern; a kinetic kill's prize |

**Marked by / visual identity.** Six pillar legs; a sealed, seamed back with no visible
head worth the name — intake at the front like a dorrak's lid scaled to a garage door;
frost rime standing on the flanks because the cistern is colder than the animal. Grey on
grey with glacial blue-white only where light passes a translucent sludge-window along
the lower flank — the one hint of what it is full of.

**Danger frame.** The largest detonation on the planet's surface (~radius 15 Flame),
**trigger-gated** (ruled, sheet amendment (2)): it explodes ONLY when it dies of
heat-family damage (Flame/Burn — lightning's strike damage is Flame, so lightning comes
free). A kinetic or cold kill leaves the cistern intact: the richest harvest, earned the
hard way. **And the ion trap: any EMP hit against a LIVING vhaulk detonates it
immediately** — checked on hit, not on death. Stunning it is one of the worst things you
can do. The description carries that obliquely (*do not still the mountain*), never as a
tooltip spoiler.

**Def wiring notes** (build: `BLUEDESERT_RULED_CONTENT_1` §2; gating mechanics:
`BLUEDESERT_MECHANICS_BUILD_1` §1).

- `RM_VhaulkCharge` (HediffDef, per-species pattern): `ExplodeOnDeath` radius ~15,
  Flame 40, `destroyBody false` — **plus the two gates**, which need a custom
  HediffComp pair in `BlueDesertLife.cs`: (a) death-cause filter — detonate only when
  the killing `DamageInfo.Def` is heat-family; (b) EMP-on-hit —
  `Notify_PawnPostApplyDamage` fires the kill+detonation on any EMP damage while alive.
  New `.cs` content in the existing assembly: check the csproj — a file without its
  `<Compile Include>` line compiles into nothing, silently.
- **Valve tap body part**: the dorrak Hump pattern scaled up — a `Valve` part
  (coverage ~0.06, height Top) on a bespoke BodyDef (six legs rules out reusing
  `QuadrupedAnimalWithHoovesAndHump` cleanly; the dorrak's cosmetic-label compromise
  does not stretch to a colossus). The tap-alive harvest is a work-giver operation at
  that part → cold-wax windfall at manhunter risk (mechanics item §1).
- Balance care: a 15-radius Flame blast inside flora chains can glass a quarter map —
  that is the point, but verify the cascade cost near map edges (mechanics item §1).

## 2. RM_Murrek — the drift ambusher

**Hook.** A flat, wide predator that buries itself under ice-sand drifts and erupts
under prey — the ruled drift weather made into a predator's tool. After every drift
storm the landscape is re-armed: yesterday's safe path is today's ambush field, and a
drift leaning against your wall might be a drift.

**Class/role.** Mid predator (marks 4+8 coupling); the krissek's clade cousin, slower
and meaner. In the open it is unimpressive; the drift IS the animal.

**Description (salvager register):**

> Flat as a dropped tarp and about as easy to see, once the sand has settled over it.
> It does not chase and it does not need to: it lies where the wind builds the drifts,
> and the drifts are everywhere the wind was. The crews walk the swept ice after a
> storm and probe the leaning sand with poles, and the poles are not long enough.

**Stats sketch.**

| field | proposed | grounding |
|---|---|---|
| `baseBodySize` | **1.2** (≈ 72 kg) | between krissek (0.9) and dorrak (1.6) |
| `drawSize` | **1.9** | wide and flat — length carries the flatness read; canvas 256 |
| `baseHealthScale` | 1.2 | ∝ mass |
| `MoveSpeed` | **3.5** | slow for a predator in the open — its speed is the ambush |
| `foodType` / `predator` / `maxPreyBodySize` | `CarnivoreAnimal` / true / **1.0** | takes utikka, vekkit, ossivel — never a dorrak |
| `manhunterOnDamageChance` | 0.8 | meaner than its cousin's grace |
| `Wildness` / `trainability` | 0.97 / `None` | relaxed law noted; a buried pet is not a pet |
| `wildGroupSize` | 1 | ambushers do not share drifts |
| commonality | **0.25** | rarer than the krissek (0.35) |
| `combatPower` | 110 | one hard hit and position, not a sustained fighter |
| `lifeExpectancy` | 12 | |
| `lifeStageAges` | Baby 0 / Juvenile 0.3 / Adult 0.6 | |
| melee | strike Stab **17**, cooldown 2.8; jaws Bite 10, cooldown 2.0 | Law 3 (bs 1.2 → 14–18); the eruption's first hit is the fight |
| `butcherProducts` | `RM_ColdWax` × 8 | |

**Marked by / visual identity.** A low wide wedge — all margin, like a ray that learned
to walk: fringed skirt-edges that vibrate sand over its own back, dorsal hide textured
as wind-rippled drift sand, paired hooked forelimbs folded under the leading edge.
Grey-white over grey, the drift-camouflage colourway; the underside (never shown in
sprites) is the dark side.

**Danger frame.** `RM_MurrekCharge` at **radius 2.9**, Flame 40 — krissek-class blast,
ungated (any death detonates, heatstroke included). The ambush is the mechanic; the
charge means flushing one with fire re-arms the field a different way.

**Def wiring notes** (defs: `BLUEDESERT_RULED_CONTENT_1` §2; burrow AI:
`BLUEDESERT_MECHANICS_BUILD_1` §6 — build order: weathers first).

- The def ships walk-and-hunt viable WITHOUT the burrow AI — a slow flat predator —
  so the content item does not wait on the mechanics item.
- Burrow hookup (mechanics §6): buried/unburied states via a burrow/unburrow job
  driver (the biome's first genuinely new one) + a MapComponent listening for the
  drift weather's end that re-seeds buried murrek at fresh drift cells. Dig the
  drift, flush the thing. Buried state wants a near-invisible drift graphic swap,
  not a new sprite sheet — the drift itself is the art.
- New `.cs` needs its `<Compile Include>` line (same trap as §1).

## 3. RM_Ossivel — the choir

**Hook.** The biome's voice (mark 7 in fauna form). A knee-high vent-throated thing
whose gas-exchange spiracles sound organ tones; packs sing at the ablation line at
"dusk" (activity-cycle, not sky — there is no dusk on the nightside). Harmless,
beautiful — and a working alarm: **they go silent when something big moves.** A colony
that learns the choir learns to hear the silence.

**Class/role.** Small herd herbivore-adjacent (spiracle-feeder on airborne
hydrocarbons + palefloss); prey for krissek and murrek; the alarm the player earns by
paying attention.

**Description (salvager register):**

> Knee-high, round-bodied, throat like a rank of organ pipes. At the line they stand
> in dozens and sing — long cold chords you can hear through a sealed helmet, the only
> proof for a hundred kilometres that anything is glad to be here. The crews like
> them. The crews also count on them: when the singing stops all at once, you have
> until the echo dies to be somewhere else.

**Stats sketch.**

| field | proposed | grounding |
|---|---|---|
| `baseBodySize` | **0.35** (≈ 21 kg) | below the vekkit; krissek/murrek prey |
| `drawSize` | **0.9** | canvas 256 (the floor) |
| `baseHealthScale` | 0.35 | ∝ mass |
| `MoveSpeed` | 4.0 | quick enough that the choir scatters |
| `foodType` | `VegetarianRoughAnimal` | crops palefloss beside the utikka |
| `manhunterOnDamageChance` | 0 | it has never fought anything |
| `herdAnimal` / `wildGroupSize` | true / **5~12** | the choir is the point |
| `Wildness` / `trainability` | **0.55** / `None` | the relaxed-tameability ruling lands here: a tamed choir is a living perimeter alarm — deliberate, and priced by taming work, not forbidden |
| commonality | **0.5** | common; the soundscape needs them |
| `combatPower` | 25 | |
| `lifeExpectancy` | 9 | |
| `lifeStageAges` | Baby 0 / Juvenile 0.2 / Adult 0.4 | |
| melee | nip Bite 4, cooldown 1.8 | not a fighter |
| `butcherProducts` | `RM_ColdWax` × 2 | and butchering the choir is a choice the colony hears |

**Marked by / visual identity.** A rounded, upright-postured little body whose throat
and chest are a fan of graded vent-pipes — spiracle tubes of visibly different lengths,
frost-rimmed at the openings; small folded limbs, no true face beyond a sensory band
above the pipes. Glacial blue-white grading to grey; the pipes' interiors the darkest
value on the body.

**Danger frame.** `RM_OssivelCharge` at **radius 1.1** (vekkit-class pop), Flame 40 —
the one you can survive standing next to, but a startled choir dying together in a
floss field is its own cautionary tale.

**Def wiring notes** (defs: `BLUEDESERT_RULED_CONTENT_1` §2; choir/silence:
`BLUEDESERT_MECHANICS_BUILD_1` §5).

- The def ships silent-capable: no hard dependency on the sound work. Choir hookup
  (mechanics §5): a sustainer ambient keyed to pack presence at the ablation line /
  activity cycle, using vanilla SFX reuse/retint first (audio is a new pipeline ask —
  scope small).
- **Silence-alarm**: the choir's sustainer stops when a pawn above a bodySize
  threshold (design: ≥ 1.0 — murrek, dorrak, vhaulk, and yes, a colonist in armour
  does not qualify; predators and the mountain do) moves within hearing range —
  MapComponent or comp proximity check on the pack's sustainer, per mechanics §5's
  "choir stops when a big pawn nears", verified by state read.
- Tameability: `Wildness 0.55` is this bible's proposal under ruling 4; the tamed
  choir-as-alarm reading follows the approved tamed-dovvik precedent (a utility pet
  whose utility is its biology).

## 4. RM_Virr — the whistle-reed (flora)

**Hook.** The soundscape's floor (mark 7). A fractal tube whose branches sound in wind
— fields of virr ARE the biome's music between storms. **The pitch rises as the plant's
charge ripens**, so a keen-eared colonist hears which field is about to be dangerous to
warm. The only plant on Ash'karr that tells you its own state.

**Class/role.** Fourth native flora card, joining the life brief §6b table (palefloss /
glassfern / chimeglobe). Mid-tier, field-forming.

**Card (extends the §6b table; shares every §6a field — `completelyIgnoreFertility`,
the −90…−1 °C band, glow-0 growth, no `sowTags` (ban 2), `Flammability 0.05`, the
ButaneGut outcome doer, `harvestedThingDef RM_ColdWax`):**

| field | `RM_Virr` · whistle-reed · mid |
|---|---|
| the read | a hollow fractal tube, hand-high, branching into graded open-ended pipes — an organ the wind plays |
| `MaxHitPoints` | **35** (≤ the chain number 40) |
| `Nutrition` | 0.25 |
| `growDays` | 10 |
| `harvestYield` (cold wax) | 3 |
| `harvestWork` | 130 |
| `visualSizeRange` | **0.65~1.0** — the smallness law: nothing above 1.1 cells |
| `maxMeshCount` | 1 |
| `wildClusterRadius` / weight | 4 / 4 — fields, because fields are the instrument |
| `wildOrder` | 2 |
| `charge.radius` (`RM_CompPlantCharge`) | **1.9** (glassfern-class) |
| `graphicClass` | Graphic_Random, 3 variants |
| `selectable` | true |
| `BeautyOutdoors` | 4 |

**Marked by / visual identity.** Transparent like all the native flora — but where the
glassfern is edge and the chimeglobe is lattice, the virr is *bore*: open pipe-ends of
visibly different diameters, thin translucent walls with refraction highlights, the ice
readable through the body. A card that reads as an opaque reed on ice fails (life brief
§8's rule).

**The rising-pitch note (wiring, mechanics §5).** Two inputs map to one audible
parameter: (a) ambient — a wind-keyed sustainer on virr fields (WeatherDef wind →
sustainer volume), the between-storms music; (b) **the ripeness pitch** — the
sustainer's pitch parameter driven by the field's charge state: growth fraction as the
slow season-scale rise, and `RM_CompPlantCharge`'s existing two-longtick warm countdown
as the sharp final climb — the same countdown the pre-detonation crack cue (mechanics
§5) already listens to, so the virr's scream and the crack cue are one system heard
two ways. Zero new mechanism class: the comp already holds the state; the sound layer
reads it.

## 5. RM_BlueIce — visual note (mineable + item icon)

The ⭐ golden mineable (`BLUEDESERT_RULED_CONTENT_1` §3: RockBase-family mineable +
stockpilable item; thaw-roll comp is the mechanics item's §3). Visual identity, both
forms:

- **The one true blue up close.** The sheet's law is "nothing here is blue up close" —
  scattering only. Blue ice is the earned exception, and it is real physics: ancient
  compressed ice IS blue in the body, the long optical path through dense bubble-free
  ice. The player who mines it holds the only locally-blue thing in the biome — which
  is exactly why it reads as treasure ("golden," owner).
- **Mineable (in-wall)**: deep glacial blue-into-teal translucent mass, glassy
  conchoidal fracture faces, fine white crack-veils deep in the body, frost bloom at
  cut edges. Follows the RockBase atlas convention (the greatbole-heartwood precedent:
  a natural-rock blob with its own colour identity); FOUNDRY derives the atlas tile
  from the item art's material language if no separate wall texture is commissioned.
- **Item icon (this commission)**: a cut block — clean quarried facets, deep
  saturated glacial blue with internal light, white crack-veils, distilled-water
  clarity at the thinnest corner. Reads as gem-grade water: valuable, cold, pure.

## 6. Roster wiring summary

Shorthand element form ONLY (`<DefName>commonality</DefName>` — a `<li>` in
`wildAnimals`/`wildPlants` silently discards the def). Target state of
`RM_BlueDesert.xml` after `BLUEDESERT_RULED_CONTENT_1` lands (existing three + the
2026-09-24 depth cast + the bedazzle four; depth-cast commonalities are that item's
to settle, shown here as this bible's proposal for one source):

```xml
<wildAnimals>
  <RM_Vekkit>0.8</RM_Vekkit>
  <RM_Utikka>0.7</RM_Utikka>
  <RM_Dorrak>0.5</RM_Dorrak>
  <RM_Ossivel>0.5</RM_Ossivel>
  <RM_Krissek>0.35</RM_Krissek>
  <RM_Vrisk>0.3</RM_Vrisk>
  <RM_Murrek>0.25</RM_Murrek>
  <RM_Dovvik>0.2</RM_Dovvik>
  <RM_Zhaaz>0.1</RM_Zhaaz>
  <RM_Vhaulk>0.02</RM_Vhaulk>
</wildAnimals>
<wildPlants>
  <RM_Palefloss>1.0</RM_Palefloss>
  <RM_Glassfern>0.5</RM_Glassfern>
  <RM_Virr>0.4</RM_Virr>
  <RM_Chimeglobe>0.25</RM_Chimeglobe>
</wildPlants>
```

- `animalDensity 0.5` / `plantDensity 0.33` stay explicitly set (sparse by doctrine;
  never zeroed).
- The three donor water-plants (`AB_ToxiGrass`, `AB_CrystalHorn`,
  `PoisonPlantTallGrass`) come OFF in the same change (turn-2 ruling 1; CrystalHorn
  keeps its Propane Lakes home).
- The campaign-tier Star Wars rows (`Vapaad`, `AA_Thunderbeast`) ride the Utinni
  patch, not this mod.

## 7. Art commission

**Pre-queue check (standing owner rule), run 2026-09-28.** Instrument: filename search
over `infrastructure/artpipe/done/` (3,778 files), `pending/` (14), `_artsrc/` (3,541
entries) + content search of `registry.jsonl`. Sanity probe: **krissek → 10 hits in
`done/` and 10 in `_artsrc/`** (the instrument sees). Findings: **vhaulk, murrek,
ossivel, virr, blueice/blue_ice — 0 hits everywhere.** Nothing to reuse; all five
subjects genuinely owed. (Side note: `registry.jsonl` returned 0 even for krissek —
it does not index this cast; the filename search over `done/`/`_artsrc/` is the
working instrument for Blue Desert subjects.) The 20 existing-cast jobs
(chimeglobe/glassfern/palefloss/dorrak/krissek/vekkit) are already queued/done and are
NOT re-queued.

**CSV:** `infrastructure/artpipe/art_lists/bluedesert_bedazzle_cast.csv` — 5 jobs,
`rimflow_item_id BLUEDESERT_BEDAZZLE_SITTING_1`, channel codex, transparent,
priority 70:

| id | canvas | facings | note |
|---|---|---|---|
| `RM_Vhaulk` | **512** | south,east,north | colossus precedent (Middenshell/Meltgut): scale must carry in the pixels; the read is "terrain feature that turns out to be an animal" |
| `RM_Murrek` | 256 | south,east,north | |
| `RM_Ossivel` | 256 | south,east,north | |
| `RM_Virr` | 256 | single | plant, Graphic_Random variants derive from the master |
| `RM_BlueIce` | 256 | single | item icon (cut block); mineable atlas derives from it |

**Style register (sheet §9 — "extremely blue from far away; colorless up close"):**
cold glacial blue-white and glass-grey palette, grey-on-grey bodies with blue-white
only in translucence, frost rime and rim light; starlit cold light; the saturated
blue-fire accent `#55c0f0` stays the krissek halo's — none of the new cast borrows it;
rust/char accents only where the fallen lie (not on these subjects). Realistic painted
natural-history illustration, grounded believable anatomy, matte natural surface
texture, never cartoonish, no outlines, no camera words. Recognizability rule: no
Earth-nameable silhouette. Every faced job's north line: **true rear view seen from
directly behind — no eyes, no face, no frontal features.** Flora/ice must show
transparency and refraction (an opaque card fails).

Queued via `python3 src/RimMandrake/Utils/artpipe/fill_queue.py --input
infrastructure/artpipe/art_lists/bluedesert_bedazzle_cast.csv` — counts recorded on
the ledger at queue time.


TASK: Give 8 to 12 recommendations that would make The Blue Desert richer, more memorable and more distinct, filling the weakest of the nine marks first. Improve and extend what is ruled rather than restarting it. For each recommendation:
- **Name** and a one-line pitch
- What the player sees, hears and feels
- Which of the nine marks it lifts
- How it could be built in RimWorld 1.6 and a rough size (XML only / small C# / large C#)
- Why it belongs to THIS biome and no other

Then list your TOP 3 in rank order with one line of why each. Reply in Markdown, at most about 1500 words. Do not ask questions; do not modify any files.