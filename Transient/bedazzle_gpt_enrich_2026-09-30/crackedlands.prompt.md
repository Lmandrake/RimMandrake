You are a senior game designer consulting on a RimWorld mod campaign. The owner wants recommendations to ENRICH one biome that has already been through a design sitting. Be concrete, vivid and buildable in RimWorld 1.6 (XML defs, C# comps, Harmony, incidents, map components, weather, sounds).

BIOME: The Cracked Lands (formerly Flooded Canyon)

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
- 2026-09-28: Volley turn 2 rulings, owner typed this session (verbatim in transcript): (1) FULL RENAME ticketed - FloodedCanyon -> CrackedLands everywhere: defs, docs, code, file names (item filed this turn). (2) Dowsing/survey ladder must make sense for TRANSIENT gravship players who stay on a map only awhile - rework A/B for per-visit payoff. (3) Ship chime REJECTED - chimes work by being strung on lines up the canyons, not magic; no ship-mounted chime. Wax hold not rejected. (4) Remove all terrestrial (vanilla Earth) life from the roster as usual - the RM_ vanilla zoo goes; invented cast migrates to RM_ tier (Q1 answered). (5) TWO GIANTS OK - rock troll ported as ours AND the muttavaq. (6) Mantrap label collision: the PLANT one relabels to Fang Leaf. (7) Common beasts (eopie et al) have ONE native biome only and TRAVEL to others - arrive with merchants/caravans, never on other rosters; eopie comes off this roster into trader presence. (8) NEW IDEAS from owner: canyon-wall FOSSILS exposed by cracking deep into the earth - something special; and WATER TECH: a special FlowWorks canal, intentionally graded + perforated so water seeps into surrounding soil improving fertility (the seep canal).
- 2026-09-28: Volley turn 4 rulings, owner typed: (1) The seep canal is named THE SWALE - a normal buildable in FlowWorks (RM_ tier), but in the Utinni campaign it is LOCKED and must be discovered as an unlock from this biome (mark 2 shape confirmed). (2) Fliers (CanCell/convor/woolamander) are GUESTS AND MIGRANTS here - they stay on this roster under the migration carve-out. (3) Wax-lined water tank NOT ruled - owner asked what it actually does; explanation owed before it lives or dies. Fossils uncontested (his own addition, in). Batch-4h names still unruled.
- 2026-09-28: Volley FINAL, owner typed: no wax tank (dropped). NEW ruling: crack-wax makes SEALED UNDERWATER SUITS for exploration - apparel-tier water/underwater TERRAIN survival, same reconciliation as WARCASKET_SUIT_CLASS_1 (terrain survival only; sea-floor maps stay ship-only, no pawn dive mechanism). Commission + ticket-out ordered, then handoff. Batch-4h renames (qattora/qetta/saqqat/luttaq/uttaqar-as-label) remain DRAFT - owner passed on the question twice; current names ship, renames await a future card. Sitting stays open for the art review.
- 2026-09-29: Art review DONE by owner (export: Transient/bedazzle_art_sheets_2026-09-28/cracked_lands/sheet.decisions.json): 7 keep, 3 improve (Muttavaq south graphic wrong; Veqma taproot must not show on the in-ground plant graphic; FossilSkeleton joined-together + more alien), 1 regen-deferred (RM_Swale stands as PLACEHOLDER per owner note - live canal reference shots first, ticket SWALE_CANAL_ART_REFERENCE_1). Tarruq: "Needs really cool sounds associated". Owner typed: "Need more plant-like members of this biome."

THE BIOME'S DESIGN DOCS:
===== design/Jawa/worldbuilding/biomes/floodedcanyon_bedazzle_review_2026-09-28.md =====
# The Cracked Lands (RM_FloodedCanyon) — bedazzle review (movement 1 + movement 2 prep)

**Item:** FLOODEDCANYON_BEDAZZLE_SITTING_1 · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1
**Date:** 2026-09-28 · **Author:** DESIGN subagent (Fable)

## 0. Naming note — this biome has two names and a full design record

The program table calls it "Flooded Canyon"; the def `RM_FloodedCanyon`
(`src/RimMandrake/FloodedCanyon/Defs/BiomeDefs/RM_FloodedCanyon_Biome.xml`) **labels itself
"the Cracked Lands"**, and the campaign twin is the frozen `RUT_CrackedLands`
(`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_CrackedLands.xml`). The design record is
rich and lives under the Cracked Lands name: the FROZEN definition sheet
`design/Jawa/worldbuilding/biomes/the_cracked_lands.md` (§10 TIME sorts, §10b explosive
growth, §11 items, §12 faction faces), the roster
`design/Jawa/worldbuilding/biomes/rosters/the_cracked_lands.json` (12 fauna / 6 flora /
fish ruling), and name drafts in
`design/Jawa/worldbuilding/biomes/noncanon_beast_names_poison_miasma_desert_scar_rot_dune_waste_cracked.md`
batch 4h. **There is no missing-sheet gap.** FloodedCanyon is in `Biomes.compose.json`
(wave 0) and hard-deps FlowWorks (`loadAfter mandrake.rm.flowworks`; the flood is a
FlowWorks driver client per `RM_MapComponent_CanyonFlood.cs`'s own header).

## 1. Nine-mark scorecard

State legend: **RULED** (owner decision recorded) / **DESIGNED** (spec, no build) /
**BUILT** (def/C# ships, MEASURED this pass). This biome is unusually far along on
mechanics: `FLOOD_CANYON_BIOME_1` (closed, live-verified chime→flood→recede),
`FLOODEDCANYON_RM_MOD_BUILD_1` (closed, twin split + quicktest proof),
`EXPLOSIVE_PLANT_GROWTH_1` (live, charge clock live-verified 2026-09-27),
`CRACKED_LANDS_ENRICHMENT_1` (closed). `FLOOD_WITNESS_EVENT_1` stays LIVE — the campaign
witness quest and the production arm-the-flood verb are ITS scope, not this sitting's.

| # | Mark | Verdict | Evidence |
|---|---|---|---|
| 1 | Unique mechanic | **FILLED (built, live-verified)** | The flood cycle itself — no other biome floods: `RM_MapComponent_CanyonFlood` (chime warning → wall of `WaterMovingShallow` → recede to `SoilRich`, "death, then soil"), live-proven ON and OFF passes at `FLOOD_CANYON_BIOME_1` close. Coupled to the explosive-growth engine by reflection (`RM_ExplosiveGrowthBridge` — `crack_flood` is a BUILT soak route; `RUT_BloomBurst` + `RUT_BloomCrop` are the flagship). Full per-mechanic Mod Settings. Soil-only-from-the-flood is enforced for the campaign (Op 5 pure-Sand `terrainsByFertility`). This is already Baroque-depth. |
| 2 | Discoverable technology | **MISSING (ruled prose, nothing built)** | Sheet §11 has two ready seams, neither with a mechanism: **discovery surveys** ("fresh data on a newly discovered hidden water… exceptionally valuable to sell", item-as-quest-seed — no def, grep this pass) and the Farmers' **dowsing craft** (reading Sealed sleeper clusters as living dowsing rods, §10). Nothing teaches the player something they keep. Slate A/B below. |
| 3 | Unique resources | **FILLED (built)** | **Crack-wax is real end to end**: `RUT_CrackWax` + `CompWaterWakeTrigger` on the sleeper drops 1–3 on wake, haulable, tradeable, butcher yield (`CRACKED_LANDS_SEALED_WAKE_MECHANISM_1`, per the item file's own header). **The bloom** is real: `RUT_BloomCrop` (BURST top) sown by `RUT_BloomBurst` over flooded ground — the boom-bust flood-week crop. And **soil itself** is this biome's unique gift on the dryland ladder. Unbuilt remainder: discovery surveys (mark 2) and cistern water as an item (slate B). Crack-wax texture is a placeholder texPath. |
| 4 | Surprising creatures | **FILLED (built)** | **The Sealed sleeper** (`RUT_SealedSleeper`, bs 0.7) is the biome's "what" moment made real — the famous cracked-pan flats ARE a dormant fauna; water wakes them and they shed crack-wax. `RSW_Creature_Mantrap` (spd 0.15 lure predator at the hidden water), `RSW_SandPillar` (colossal forever-juvenile caterpillar) and `RSW_MutagenicNorphea` (dormant-until-woken) round out a cast built on the §10 TIME sorts — fauna divided by WHEN it is alive, the Weeping Stones' inversion. |
| 5 | GIANT beast | **PARTIAL (cast on paper, wired nowhere)** | The roster imports `DA_RockTroll` (bs 4.5, "colossal eyeless cave dweller, self-petrifying wounds", owner round2 move mapping) as the colossus, and batch 4h drafts it *uttaqar* — but it appears in **zero** biome defs or patches (MEASURED sweep this pass, sanity-probed on RSW_Gizka=8 files), and it is a donor def, not ours. The giant slot is a ruling away from either an owned port or a new invention (§3 muttavaq). |
| 6 | Gravship touch | **MISSING** | `BIOME_SHIP_CONTRIBUTIONS_1`'s running list has no Cracked Lands row (checked this pass; only the Sump is recorded). The raw material is good — crack-wax as ship waterproofing, a chime as a ship instrument — but nothing is ruled or built. Slate D. |
| 7 | Soundscape | **PARTIAL (mechanic built, voice placeholder)** | The biome already has the planet's best AUDIO MECHANIC: the water chimes ring ahead of the wall (`RingChime()` in the map component — a real warning the player learns to trust). But it plays **`SoundDefOf.TinyBell`**, a vanilla placeholder; there is no Sounds folder in the mod, no wind-in-the-slots ambient, no ticking-flats tell (§9's smell-then-tick sequence), no bespoke chime tones. Slate E. |
| 8 | Interesting weather | **PARTIAL** | The campaign weather table is mostly *bans* executed correctly (Rain/snow/fog zeroed per ban 5; Clear 85, DryThunderstorm 3, Odyssey Sandstorm 8). The flood is a GameCondition, not weather, and Sandstorm/DryThunderstorm are shared vocabulary. No sky effect belongs to nowhere else. The sheet's own herald sequence — the Contagion's storm visible on the peaks, wet clay on the wind — is pure prose. Slate F. |
| 9 | Relationship to the gods | **MISSING** | §12 gives faction faces (Farmers, Jawa salvage strikes, Hutt tolls, tribes-as-water-law-zealots) but nothing places the biome in the ideoligion/lore layer. The material writes itself — "ancient water chimes" (whose ancients?), the flood as visitation, death-then-soil as doctrine — and the Blue Desert precedent (ruled 2026-09-28) says the owner prefers **biome-local lore, no campaign precept defs**. Slate G. |

**Score: 3 filled, 3 partial, 3 missing (2, 6, 9).** Mark 1 is the strongest of any biome
reviewed so far — the volley should aim at 2/6/9 and the voice/sky halves of 7/8, not
re-ideate the flood.

### Water statement (coordinator ask)

The sheet gives this biome real water: **27 measured open-water tiles**, ruled the planet's
ONE lethal water (freeze ruling R6 — the truce's mechanism is sightline and slot-canyon
water has none; the kill happens at the water). Fish are wired: `fishTypes` on both twins
(7 species — our own `RUT_Tubbik`/`RUT_Zhurr`/`RUT_Hurrok`/`RUT_Vhessa` +
`RSW_DuneCrawler`/`RSW_Rocktooth`/`RSW_Boneblade`, `maxFishPopulation 90`, mirrored onto
`RM_FloodedCanyon` by `SandFishing_CrackedLands.xml`). **The sea two-def law (every
fishable also swims a floor map) does NOT bind here** — the owner scoped it to the seas
("true for ALL seas") and its mechanism is the ship-only sea-floor map; a land biome's
freshwater catch has no floor map to swim. Catch-only fish are legal in the Cracked Lands.

## 2. Roster gap census

Two rosters exist and they are deliberately different — read both before calling anything
missing. Parsed as XML elements this pass (`<DefName>commonality</DefName>` shorthand).

### Campaign roster as wired (RUT_CrackedLands inline = frozen; RM_FloodedCanyon via `WildAnimals_CrackedLands.xml`)

| row | comm. | band (§10) | owner | note |
|---|---|---|---|---|
| `RSW_MutagenicNorphea` | 0.4 | Sealed | RSW_ port | dormant-until-woken; batch 4h draft *qattora* / *norphea* |
| `AA_SandSquid` | 0.1 | Sealed | donor (sarg.alphaanimals) | port-named *ommok*, port not executed |
| `RUT_SealedSleeper` | 0.2 | Sealed (signature) | ours | 🔴 **on the frozen twin ONLY — missing from the RM_ patch** (see wiring gaps) |
| `AA_Murkling` | 0.2 | Spenders | donor | eats the flood's drowned dead; **multi-homed**: also Forsaken/Black Crags (annotate, that sitting's call) |
| `RSW_SandLeaper` | 0.2 | Spenders | RSW_ port | draft *qetta* |
| `RSW_Gornt` | 0.3 | Patient | RSW_ port | seep-edge pouncer |
| `RSW_Eopie` | 0.25 | Patient | RSW_ port | ⚠️ **5 homes** (Desert, Leaning Scrub, Long Shade, Weeping Stones, here — MEASURED sweep). SW canon icon carve-out; annotate for the one-home law, do not evict here |
| `RSW_Creature_Mantrap` | 0.15 | Patient | RSW_ port | lure predator at the hidden water; draft *saqqat* |
| `RUT_EmperorVulture` | 0.15 | Patient (sky) | ours | real flight (`MaxFlightTime 60`); 🔴 **frozen twin only — missing from the RM_ patch** |
| `RSW_CanCell` / `RSW_Convor` / `RSW_Woolamander` | 0.2/0.2/0.15 | flier-commuters | RSW_ ports | nest in the Desert (ban 4). Convor also Fever Wood/Greentide/Leaning Scrub — flier-migrant carve-out plausibly applies, annotate |
| `RSW_SandPillar` | 0.5 | (small) | RSW_ port | wired 2026-09-23 on the RM_ patch only (correct — twin frozen); draft *luttaq* |
| `DA_RockTroll` | roster 0.5 | the giant | donor | 🔴 **wired NOWHERE** (0 hits); the roster's import was never executed; draft *uttaqar* |

Flora (identical on both sides via Op 3): `AB_HardyGrass` 1.0, `GRimMoss` 0.8,
`RUT_TwistingThorngrass` 0.5, `RUT_TwistingThornweed` 0.4, `RUT_TwistingThornwood` 0.2
(tree; dual-homed with Poison Forest by design note), `AB_GargantuanLithops` 0.15 — plus
`RUT_BloomCrop` which is correctly sown only by the `RUT_BloomBurst` incident, never a
wild row. Fish: 7 species as in §1. Diseases: 8 entries, twins matched.

### The RM_ tier question (Q11a tension — the census's biggest finding)

`RM_FloodedCanyon`'s own inline roster is **exactly the evicted vanilla zoo**
(Iguana/Dromedary/Fox_Fennec/Warg/Rat/Cougar + vanilla cacti/grass) — deliberate at build
time ("ships the biome functional on Core alone"), but it now sits against Q11a: *"The top
mod without star wars will look precisely the same as the star wars enhanced one save for
any star wars beasts."* The invented, non-canon cast — SealedSleeper, EmperorVulture, the
BMT-origin ports (SandLeaper/SandPillar/Mantrap/Norphea are invented exotics, not Star Wars
canon) — belongs in the `RM_` tier under the Q12–Q15 per-sitting migration, with only true
canon (Eopie, Convor, CanCell, Gornt, Woolamander) riding the Utinni/RSW layer. Today the
free mod is an impoverished vanilla fallback, which Q11a says may not exist. Ruling asked
in §5 Q1.

### Wiring gaps (owed work, not rulings)

1. 🔴 `RUT_SealedSleeper` (0.2) and `RUT_EmperorVulture` (0.15) exist on the frozen twin
   but **not** in `WildAnimals_CrackedLands.xml` — the def that survives the terminal
   paint loses the biome's two signature creatures. One `PatchOperationAdd` fixes it.
2. 🔴 `DA_RockTroll` — roster import never executed anywhere; also a donor def (the
   RimMandrake tier may not assume it). Fold into the mark-5 ruling (§5 Q2).
3. Chime audio is `SoundDefOf.TinyBell` — placeholder, filed under slate E.
4. `RUT_CrackWax` texPath is an expected-pending placeholder folder.

### Food-web / role holes

- **No colossus wired** (mark 5) — the only structural fauna hole.
- **No mudflat breeder** — §10's Spenders name "mudflat breeders, a sudden carpet of small
  frantic life" as the band's core image; murkling (carrion) and sand leaper (small
  rodent) don't breed IN the wet. Proposed: irqit (§3).
- **No voice** — a biome whose §9 sound is "wind in the slots; nothing; then the roar" has
  no creature that sounds. Proposed: tarruq (§3).
- **Flora**: the sheet's owed "our own vegetation, our own scales"
  (`TREE_GRAPHICS_OWNERSHIP_1`) is still donor interim bodies (AB_/GRim*). One addition
  proposed (veqma, §3) rather than re-litigating the authored-tree track.
- Otherwise the pyramid is sound across all three TIME bands + sky + water: producers →
  eopie/sleeper grazers → gornt/mantrap ambushers → vulture/murkling undertakers, with the
  fish as the fourth column.

## 3. Proposed roster fills

All NEW inventions in the Cracked Lands accent (batch 4h register: *dry then sudden — q,
tt, an open -a or a stopped -aq*), with **deliberately varied shapes and syllable counts**
per the Blue Desert sitting's name-style ruling (the existing drafts qattora / qetta /
saqqat / luttaq / uttaqar already skew 2-syllable; these four run 3 / 2 / 2 / 2 with
different vowel patterns and endings). Every name swept this pass with `grep -rilE` across
`src/`, `design/`, `infrastructure/state/` — sweep sanity-probed on *qetta* (2 files, the
name docs) and *korrum* (5+ files): the instrument can find. One home each: here.

| name | defName | kind | sweep | concept + role |
|---|---|---|---|---|
| **muttavaq** | `RM_Muttavaq` | creature (GIANT) | **0 hits — clean** | The colossus (mark 5), and the Sealed band's logical extreme: a canyon-floor giant that sleeps for YEARS under a clay pan the players read as terrain — a low mounded polygon field slightly out of pattern. The flood wakes it; it spends the flood-weeks dredging the wet floor like a walking weir, then digs in wherever it stands and seals. Killing one asleep is easy and shameful (and yields a fortune in crack-wax and meat); waking one over your farm is the disaster. Fits the built `CompWaterWakeTrigger` family — the mechanism is already this biome's. |
| **irqit** | `RM_Irqit` | creature | **0 hits — clean** | The mudflat breeder (§10 Spenders' missing core). Palm-sized, spawns as a sudden carpet on flooded cells at recede, breeds once, dies at the dry — a living calendar of the flood and the fliers' feast made real. Stopped *-it* ending, front vowel: quick and small in the mouth. |
| **tarruq** | `RM_Tarruq` | creature | **0 hits — clean** | The voice (mark 7 in fauna form). A crack-dweller at the seep line whose territorial calls resonate down the crack network — long low tones the canyon carries for hundreds of meters. It goes silent when the cracks begin to fill: the biome's living second warning, before even the chimes. Doubled *rr*, closed *-uq*. |
| **veqma** | `RM_Veqma` | flora | **0 hits — clean** | Dowsing flora (marks 2+3 support). A wiry, near-leafless plant whose taproot finds hidden water; it blushes faintly green at the tip in proportion to how near the water table sits. Fields of veqma ARE the Farmers' first survey instrument — and a player who learns to read them keeps that knowledge. Grows only on the shade line (ban 2 respected by placement). |

These are pitches for the sitting's ruling, not filed defs. None re-homes a neighbour's
species; all pass the admission test (lives in the shade line, survives the flood — by
sealing, spending or hiding — and is not a terrestrial animal). The four batch-4h drafted
renames (qattora, qetta, saqqat, luttaq, uttaqar) remain DRAFT, "nothing applied" — §5 Q3
asks for their ruling in the same breath.

## 4. Candidate mechanics slate

Ranked pitches for the four-turn volley, aimed at the misses (2, 6, 9) and the partial
halves (5, 7, 8). All DLCs assumed present. The flood engine, FlowWorks and the
explosive-growth engine are BUILT — every pitch below leans on machinery that exists
rather than proposing new liquid mechanics. `FLOOD_WITNESS_EVENT_1` keeps the campaign
witness quest and the production arm-the-flood verb; nothing here duplicates it.

**A. Discovery surveys + the dowsing craft** *(mark 2, with 3; rank 1)*
Build §11's ruled pair as one ladder the player climbs and KEEPS. Reading the land —
sleeper clusters (living dowsing rods), veqma blush, crack-wax finds — accumulates toward
a **hidden-water discovery**: a survey item naming a real map location. The survey is
sellable (§11's "exceptionally valuable thing to sell"), or kept and dug (candidate B).
The kept half is the discoverable technology: once a colony completes its first survey,
dowsing reads become visible info overlays for good (Anomaly study / techprint-shaped
unlock, content-side). *Engine:* item def + a MapComponent scoring cells from things
already placed; zero new liquid code. *Trade-off:* the payoff wants candidate B built, but
sell-only ships alone.

**B. The cistern — tapping the hidden water** *(marks 2+3+1 deepened; rank 2)*
The Farmers' whole economy, playable: at a surveyed hidden-water site, dig a cistern head
— a FlowWorks water source that yields slowly between floods and refills at each flood.
Line it with crack-wax (the material's ruled purpose, closing that loop) or lose a share
to seepage. The only reliable water on the dryland ladder, and it is FOUND, not placed.
*Engine:* FlowWorks fluid source building + the flood's existing cycle clock; crack-wax as
a build ingredient. *Trade-off:* touches FlowWorks' source-budget balance; wants the
survey (A) as its gate so water stays earned.

**C. The muttavaq — the pan that wakes** *(mark 5, with 4; rank 3)*
§3's giant as the biome's set-piece decision. Sleeping, it is a terrain-reading puzzle
(a pan field slightly wrong); the flood wakes it wherever the water reaches; awake, it is
neutral but unstoppable, re-cutting the canyon floor as it feeds (FlowWorks depth edits on
its trail — machinery the flood already drives). Players choose: quarry a sleeping fortune
and answer for it, or farm around a thing that will someday stand up under the barn.
*Engine:* big animal + `CompWaterWakeTrigger` (built) + a walk-path terrain writer;
flip-book flight not needed, but dig-in/emerge states want 2 poses. *Trade-off:* the
terrain-writer is real C#; the "reads as terrain while asleep" presentation needs art care.

**D. The ship takes the chime and the wax** *(mark 6; rank 4)*
The Cracked Lands' `BIOME_SHIP_CONTRIBUTIONS_1` row, in the biome's own voice, two halves:
**a ship-mounted water chime** — salvaged ancient chimes rehung on the gravship as an
early-warning instrument (on any map: rings ahead of floods, and gives one in-advance ring
before this biome's wall; a beautiful sound the crew learns to fear), and **the wax-lined
hold** — a crack-wax-lined water tank / damp-proofed storage module (spoilage bonus for
liquids and perishables; FlowWorks tank re-skinned). *Engine:* one building def each; the
chime's trigger reads the flood clock that exists. *Trade-off:* chime-on-other-maps needs
a rule for what it listens to off-biome (weather? nothing?) — genuinely the owner's
flavour call.

**E. The soundscape, built** *(mark 7; rank 5)*
Replace TinyBell with a real chime voice: 3–4 bespoke deep chime tones, **staged by
distance-to-flood** (single far tolls at first fill, rolling peals as the wall nears —
the lead time is already a Mod Settings number, so the staging hooks exist). Under it: the
wind-in-the-slots ambient, the ticking flats as the Sealed wake (tick SFX at sleeper
positions in the chime window — defs exist), and tarruq calls that STOP a beat before the
chimes start. The biome heard with eyes closed is: wind, tick, silence, chime, roar.
*Engine:* SoundDefs + one-shot triggers from the existing phase clock; ambient keyed to
biome. *Trade-off:* audio assets are a new pipeline ask (artpipe is images); scope tones
first, ambient later.

**F. The herald sky** *(mark 8; rank 6)*
A weather that belongs to nowhere else because it is ABOUT somewhere else: **Peakstorm
Light** — here it stays clear and dry, but the northern skyline flickers with the
Contagion's storm (dry lightning at the horizon, a red-brown cast on the light), and it is
the flood clock's herald: the map component biases the chime window to follow it, so a
watching player reads the sky like a Farmer. Optionally a second: **wet-clay wind** (§9's
smell tell) — a short pre-chime weather with dust motion reversal, no precipitation.
*Engine:* WeatherDef + skyColors and an overlay; a one-line hook where the clock already
rolls its window. *Trade-off:* horizon-lightning presentation is approximate in RimWorld's
sky system (sky color + distant strike SFX carry it); it must never rain here (ban 5 — the
weather does 0 precipitation by construction).

**G. The ones who hung the chimes** *(mark 9; rank 7)*
Biome-local lore, no campaign precept defs (Blue Desert precedent). The chimes are already
"ancient" in their own ruled tooltip — someone hung them, tuned to the water, before
anyone alive. The gods layer: the flood as visitation (the tooltip's "annual inundation" —
death, then soil, as the oldest mercy on the dryland ladder), refuge ledges bearing
chime-tenders' marks, and the one commandment everyone on the roads already keeps: settled
water is legal water. Shape: description passes on chimes/ledges/ruins + one lore quest
seed (a chime that rings WRONG — a survey seed in disguise, tying to A). *Trade-off:* pure
content; its only cost is the owner's voice — drafted lines must go to him.

**H. The salvage strike** *(§12's Jawa rhythm; rank 8)*
"A flood is a salvage strike": each recede exposes buried wreckage along the flood line
for a few days — scatter of tech scrap/artifacts on flood-touched cells, decaying fast.
And what the flood gives the player it gives everyone: a rival Jawa crawler crew may
arrive to work the same mud (visitor-band incident, not a raid). Boom-bust scavenging on
the flood's clock, the mirror of the bloom. *Engine:* incident + placement on the map
component's soaked-cell list (exists); crawler visitors are a pawn-group incident.
*Trade-off:* loot tables need discipline or the flood becomes a slot machine; sequence
after the bloom so the two windfalls read distinct.

**I. The toll gate and the refuge ledge** *(§12 structures; rank 9)*
Two site/structure pieces: refuge ledges cut along the roads (map features that make the
witness moment survivable EVERYWHERE, not just at the quest — `FLOOD_WITNESS_EVENT_1`
depends on ledges existing) and the Hutt toll gate as a slot-canyon site piece (one gate,
one cut of everything, legally smiling). *Engine:* KCSG/template family
(`MOISTURE_FARM_TEMPLATES_1` closed — the template machinery is proven on this very
biome). *Trade-off:* ledge placement interacts with mapgen cliffs; the toll gate is
flavour until quests use it.

**J. The bloom market** *(economy tail of 10b; rank 10)*
When a canyon blooms, the market drowns: post-bloom trade surge (caravans arrive FOR the
bloom crop at crashed prices; off-season, bloom goods command a premium elsewhere).
Boom-bust made tradeable. *Engine:* a price-factor hediff on the item + a trade-caravan
incident bias for N days post-bloom. *Trade-off:* small; do last — it polishes an economy
the flood already creates.

## 5. Open questions for the owner

1. **The RM_ tier's face (Q11a).** The free `RM_FloodedCanyon` roster is today the evicted
   vanilla zoo (Iguana/Dromedary/Fennec/Warg/Rat/Cougar) — built deliberately as a
   works-on-Core-alone generic, before Q11a ruled the free mod must look the same as the
   campaign one. Migrate the invented cast (SealedSleeper, EmperorVulture, the four
   BMT-origin ports) to `RM_` defs at this sitting per Q12–Q15 and retire the vanilla
   zoo — or does this mod's "generic canyon for any world" origin earn an exemption?

2. **The giant.** The roster's colossus is `DA_RockTroll` — donor-owned, never wired,
   rename drafted (*uttaqar*). Port it as ours, or strike it and take the muttavaq (§3),
   which is native to the biome's own Sealed/water-wake mechanism? (Both is also coherent:
   troll under the crags walls, muttavaq under the pans — but that spends two giants on
   one biome.)

3. **Batch 4h names.** qattora (or bare *norphea*), qetta, saqqat, luttaq (+ ommok,
   kessik) are drafted, "nothing applied," and the sitting is the natural place to rule
   them — including the mantrap label collision (two different creatures both labelled
   "mantrap"; batch 4h flag 2 says one roster should relabel).

4. **The ship's take (mark 6).** Chime mast, wax-lined hold, both, or something else in
   the biome's voice — the `BIOME_SHIP_CONTRIBUTIONS_1` row needs his pick before
   anything builds.

5. **Multi-homing annotations only:** RSW_Eopie carries 5 homes (canon icon herd) and
   RSW_Convor 4 (flier-migrant carve-out?). Recorded here for THIS biome's sheet per the
   no-evictions ruling — is either annotation ("deliberate, do not fix") his intent, or
   should their one-home picks queue for their own review rows?

---

*Movement 2 prep: the wiring gaps in §2 (sleeper/vulture patch rows, giant ruling) plus
the four §3 pitches are the fill; the slate above is the movement 3 opening hand. Nothing
here re-opens a frozen ruling; no tile count is cited as evidence of anything (paint is
terminal); `FLOOD_WITNESS_EVENT_1` and the explosive-growth item's own Owed list are
respected as other items' scope.*


===== design/Jawa/worldbuilding/biomes/cracked_lands_bedazzle_cast_2026-09-28.md =====
# The Cracked Lands — bedazzle cast bible (movement 4: commission)

**Item:** FLOODEDCANYON_BEDAZZLE_SITTING_1 · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1
**Date:** 2026-09-28 · **Author:** DESIGN subagent (Fable)
**Slate:** owner full-accepted (volley turns 2–4 + final, ledger notes on the item).
**Biome:** `RM_FloodedCanyon`, labelled "the Cracked Lands"; full rename to CrackedLands
is `CRACKEDLANDS_FULL_RENAME_1`'s scope, not this document's — current names ship.

## RM_Muttavaq — the pan giant

**The Sealed band's logical extreme, and the biome's set-piece decision.** A canyon-floor
giant that sleeps for YEARS under a clay pan the player reads as terrain: a low mounded
polygon field slightly out of pattern — the polygons a touch too regular, the mounding a
touch too high, the cracks radiating from a center the way dried clay never does. Walk the
famous cracked-pan flats and you walk on sleeping animals; walk THIS pan and you walk on
one animal. The Farmers know every muttavaq pan in their reach by name and route around
them; a newcomer farms on top of one.

**Wake.** The flood wakes it wherever the water reaches — the built
`CompWaterWakeTrigger` family (`RUT_CompWaterWakeTrigger.cs`: terrain-turns-to-water
trigger calling straight into the stock `CompCanBeDormant.WakeUp()` path, wake state
Scribed) is exactly this mechanism at sleeper scale; the muttavaq is the same comp on a
body two orders of magnitude larger. Awake, it spends the flood-weeks **feeding as a
walking weir**: wading the wet canyon floor, straining mud and carrion and the irqit
carpet through its jaw-plates, re-cutting the floor as it goes (FlowWorks depth edits on
its trail — the terrain-writer is the mechanics item's C#, not this document's). At the
dry, it digs in wherever it stands, seals its burrow-lining, and becomes terrain again —
somewhere new.

**Danger frame: neutral but unstoppable.** It never hunts, never raids, never
manhunters. It also never stops: walls, crops, buildings and pawns on its feeding line
are things it walks through, and its wake is a FlowWorks event, not a combat one. The
player's decisions are all placement decisions: quarry a sleeping fortune and answer for
it (killing one asleep is easy and shameful, and yields a fortune in crack-wax and meat —
its burrow-lining is the planet's largest single crack-wax deposit), or farm around a
thing that will someday stand up under the barn.

**Stats sketch** (FOUNDRY calibrates; the frame is Middenshell-class):
`baseBodySize ~5.0`, `baseHealthScale ~12`, `MoveSpeed ~2.0` (it does not need to be
fast), `manhunterOnDamageChance 0` awake and asleep — damage while waking it is answered
by the wake itself, not by rage. Wildness 1.0, untrainable, `lifeExpectancy` in
centuries. Butcher/kill yield: meat at giant scale + a large `RUT_CrackWax` drop (the
wake-drop mechanism already ships on the sleeper; the muttavaq's is the same drop scaled
up). Not a pack/herd animal — one per pan, pans rare.

**Marked by:** the out-of-pattern pan (sleeping); the wet-season silhouette of a hill
that wades (awake); its trail — a fresh-cut channel of churned wet clay that was not
there before the flood.

## RM_Uttaqar — the rock troll, ported as ours

**Port of `DA_RockTroll` (Dinonysus's donor mod), taken as OURS with the donor's read
honored.** The donor def (read this pass from the installed mod, `1.6/Defs/ThingDefs_Races/
Animal_RockTroll.xml`): *"a colossal, eyeless creature often found living in caves and
underground chasms… will only surface from its underground lair when provoked. Lacking
regenerative abilities, the rock troll makes up for it through a strange process known as
self-petrification. Any open wound will almost immediately be closed by ultra-fast blood
clotting that ossifies soon after, creating dense stone-like formations that provide the
beast with temporary ablative armor."* Donor numbers, which the port keeps as its
baseline: `baseBodySize 4.5`, `baseHealthScale 10`, `MoveSpeed 3.5`,
`manhunterOnDamageChance 1.0`, armor 1.2 sharp / 0.7 blunt / 0.8 heat, `MarketValue
5300`, `lifeExpectancy 750`, trainability Intermediate, hediff `DA_BloodPetrification`
(five severities). The donor even ships a dormant-disguise cousin mechanic —
`DA_HibernatingRockTroll`, spawned as a *"strange stone formation"* — which the port
keeps in spirit: an uttaqar at rest against a crag wall reads as rockfall.

**Re-voiced in our register.** In the Cracked Lands the uttaqar is the crag-walls giant
against the muttavaq's pans — **the two giants never share a band**: the muttavaq owns
the flats and the flood-floor; the uttaqar owns the walls, the talus, the slot-canyon
dark and the chasms under them. It is the biome's answer to what lives where even the
seep does not reach: a thing that eats stone-dwelling life and minerals, needs no water
the cracks don't already hold, and treats its own wounds as quarry — every fight it
survives leaves it more stone than flesh. Old uttaqar are effectively walking petroglyphs,
seamed with ossified wound-stone in layers a Farmer can read like tree rings.

**Port shape:** our own ThingDef + PawnKindDef `RM_Uttaqar`, our own art (this
commission), the self-petrification hediff rebuilt as `RM_` (mechanics item); the donor
def leaves the roster (`CRACKEDLANDS_RULED_CONTENT_1` step 4). **Label ships as "rock
troll"** — *uttaqar*-as-label is a batch-4h DRAFT the owner passed on twice; current
names ship, the defName carries the invented word per the commission.

**Marked by:** the eyeless head; the wound-stone seams; a "rockfall" at the crag base
that was not in yesterday's survey.

## RM_Irqit — the mudflat breeder

**The Spenders' missing core, made real** (§10: *"mudflat breeders, a sudden carpet of
small frantic life"*). Palm-sized, soft-bodied, quick — the irqit exists as eggs in the
dry clay for years, then the recede turns every flood-touched cell into a nursery: a
sudden CARPET of small frantic life between the roar and the dry. Each irqit breeds
exactly once, lays into the wet clay, and dies as the mud stiffens — a living calendar of
the flood, and the reason the fliers commute in (§4's ruling seen from below: the irqit
carpet IS the feeding run). The muttavaq strains them by the thousand; the gornt and the
fang leaf take the stragglers at the seep; the vultures take everything that misses the
timing.

**Mechanism:** spawned as a cohort on the flood component's soaked-cell list at recede
(the list exists — slate H already planned placement off it), aging on a fast lifecycle
clock; at dry-out the cohort dies where it stands, leaving small meat/carrion. No
year-round population: outside flood-weeks the biome shows zero irqit and that is
correct, not a defect.

**Stats sketch:** `baseBodySize ~0.12`, herd-spawning, `MoveSpeed ~4.5`, wildness 1.0,
no manhunter, trivial combat stats — its defense is number and calendar. Tiny meat
yield; the point of hunting it is that for two weeks it is free food carpeting the floor.

**Marked by:** the carpet itself — motion where the biome's rule is "none, then the
flood"; drying windrows of spent irqit at the flood line afterward.

## RM_Tarruq — the voice

**The biome heard, in fauna form** (mark 7's fauna half). A crack-dweller at the seep
line — a lean, long-limbed climber built for the vertical dark — whose territorial calls
resonate down the crack network: long low tones the canyon carries for hundreds of
meters, each animal answering its neighbors down the line. On an ordinary day the
Cracked Lands' soundscape is wind, then tarruq, then wind. **It goes silent when the
cracks begin to fill** — the seep-water rising through its galleries drives it up and
mute — and that silence is the biome's living second warning, arriving BEFORE even the
chimes: an experienced Farmer trusts the ground (the ticking flats), then the tarruq
hush, then the chimes, then runs. The warning ladder the sheet's §9 smell-then-tick
sequence began now has its middle rung.

**Mechanism:** an ambient call (SoundDef, slate E's pipeline) keyed to tarruq presence,
gated OFF by the flood map component's pre-chime phase — one boolean read on machinery
that exists. The silence costs no C# beyond the gate.

**Stats sketch:** `baseBodySize ~0.45`, `MoveSpeed ~4.8`, agile, shy (high wildness, no
manhunter — it answers threat by going vertical), modest predator diet (crack-life,
irqit stragglers, eggs). Year-round Patient-band resident; commonality low enough that
hearing one is common and seeing one is an event.

**Marked by:** the call; the hush; claw-polished runs down the slot walls at the seep
line.

## RM_Veqma — the dowsing flora

**The Farmers' first survey instrument, growing wild** (marks 2+3 support; §11's dowsing
craft in flora form). A wiry, near-leafless plant of the shade line — mostly taproot,
the visible plant a sparse fan of grey-green whips — whose root finds the hidden water,
and whose **tip blushes green in proportion to how near the water table sits**. A stand
of veqma is a contour map: dull grey where the water lies deep, brightening cell by cell
toward the seep, vivid green directly over a find. Reading a veqma field is the first
thing a Farmer teaches a child and the first thing the survey loop (below) teaches a
player.

**Placement law:** grows ONLY on the shade line — ban 2 (*"no green outside the shade
line"*) is respected by placement, not exception. A veqma on open sun-flats is a
linter-catchable violation.

**Mechanism:** graphic tint (or small variant set) keyed to the survey component's
hidden-water proximity score for its cell — the same score the dowsing ladder reads, so
the plant IS the UI. Wild-sown at low commonality in the shade band; not farmable (its
value is where it grows, not what it yields — harvest gives a little herbal/raw
plantmatter only).

**Marked by:** the blush gradient; a vivid-green stand is worth a survey flag on sight.

## The Swale (RM_Swale) — the seep canal

**Owner's own addition (volley turn 2), named THE SWALE at turn 4.** A FlowWorks canal
variant, intentionally graded and **perforated**: while it carries water, it deliberately
loses some of it sideways — the water seeps into the surrounding ground, and **adjacent
cells climb in fertility** for as long as the swale runs. The trade is the design: a
sealed `RM_Channel` delivers everything downstream; a swale delivers less and farms its
own banks on the way. A homestead ringed by green swale-lines is the Cracked Lands'
signature of wealth.

**Tier law (owner-ruled, turn 4):** the swale is a **normal buildable in FlowWorks**
(`RM_` tier — any RimWorld world gets it with the mod), but **in the Utinni campaign it
is LOCKED and must be discovered as an unlock from this biome** — the mark-2
discoverable technology, confirmed shape. Build implementation rides the FlowWorks
channel family (`RM_Channel_*` defs + the fill terrains); the perforation is a fertility
write on adjacent cells while the fill terrain is wet — mechanics item's C#.

**The discovery loop — reworked for TRANSIENT gravship players (owner, turn 2).** The
original A/B ladder assumed a settled colony accumulating dowsing reads over years; a
gravship player stays a while and leaves. The loop is now **per-visit shaped**, with one
durable prize:

1. **Read the land** (one visit's work): veqma blush gradients, Sealed-sleeper cluster
   density (living dowsing rods, §10), crack-wax finds, tarruq territories. The survey
   component scores cells from things already placed — zero new liquid code.
2. **Complete a survey** → a **discovery survey item** naming a real hidden-water site
   on THIS map. Per-visit payoff, spend it either way before you leave:
   **sell it** (§11's "exceptionally valuable thing to sell" — the Farmers pay
   handsomely for fresh data), or **dig it**: a cistern head at the site — a FlowWorks
   water source that yields slowly between floods, refills at each flood, and wants a
   crack-wax lining or it loses a share to seepage. The cistern serves the stay and
   remains on the map as the player's mark on the biome.
3. **The durable prize:** the first completed survey **unlocks the swale for the
   campaign** — the one thing that leaves on the ship. The player didn't find water;
   they learned how the Farmers make ground grow, and that knowledge works on any map
   with a FlowWorks line. Dowsing reads (veqma tint, sleeper-cluster overlay) also stay
   visible once earned.

So a transient player's arc is complete in one stay — read, survey, sell-or-dig — and
the biome still changes their game forever. **No wax tank** (owner, final: dropped); the
crack-wax loop closes through the cistern lining and the wax suit instead.

## Fossils — the canyon-wall strata

**Owner's own addition (volley turn 2, uncontested at turn 4): the canyon walls are
FULL of the dead — something special.** The flood has been cutting this country for
geological time, and the walls are the ledger: **fossil-bearing strata** ship as
mineable defs seeded in canyon-wall generation (RockBase-family mineables, the
Greatbole-Heartwood pattern — a wall cell the player can see is different and dig).
Mining a seam yields the fossil item family:

- **Common impressions** — fern-mats, shell-beds, trackway slabs; modest value, stack
  well, honest trade goods and a beauty bump raw.
- **Articulated skeletons** — rare; a whole small animal in the stone; serious value
  and the centerpiece tier for display.
- **Deep-stratum uniques** — the quest-grade tier, found only deep in the walls or
  where a flood has cut a fresh face; each one a named, one-off piece.

**The flood re-cuts the ledger:** after each flood, the map component converts a few
flood-scoured wall cells to FRESH exposed seams — the recede is a mining opportunity as
well as a farming one, and the salvage-strike rhythm (§12's Jawa face) gets a geological
verse. Post-flood, walls near the water line are worth walking.

**Display furniture:** a mounted-display family (sculpture-shaped: quality-bearing,
beauty-scaled by the fossil tier mounted) — the wall slab, the free-standing skeleton
mount. A Farmer homestead with a mounted deep-stratum piece over the door is saying
something; so is a gravship galley with one bolted to the bulkhead.

**The quiet lore line (owner's "something special", kept quiet on purpose):** the deep
strata hold **pan-giants** — articulated sleepers the size of a muttavaq and larger, in
layers older than the canyons themselves, some still curled in the seal position. The
pans have been sleeping here a very long time; not all of them woke. No tooltip says
this outright — the deep-stratum unique descriptions let the player assemble it.

## The wax suit — crack-wax sealed underwater suit

**Owner's final ruling of the volley: crack-wax makes SEALED UNDERWATER SUITS.** The
Sealed sleeper survives years underground behind a crack-wax membrane; the Farmers
line cisterns with the same material; the suit is the third use of the one substance —
a full-body sealed apparel piece, crack-wax over a stiffened frame, that lets a pawn
**survive water and underwater TERRAIN**: working flooded slot-canyon cells during the
flood-weeks, crossing and working the biome's 27 measured open-water tiles (the
planet's ONE lethal water, freeze ruling R6 — the suit is how a pawn survives standing
in it), and hidden-water digs — cutting into a seep gallery or a drowned cistern
without drowning in the attempt.

🔴 **Terrain survival ONLY — stated in the def, the doc and the review.** The suit
grants survival on water/underwater TERRAIN a pawn can already path to. It grants **no
sea-floor access**: sea-floor maps remain **ship-only** (owner, 2026-09-26, verbatim:
*"You can't 'dive' as an individual pawn nor return as one. It's ship or nothing."*),
there is **no pawn dive verb, mechanism or menu option anywhere in this feature**, and
`RM_SeaDiveHatch` remains the single way onto a sea floor. This is the same
reconciliation `WARCASKET_SUIT_CLASS_1` carries: an apparel class may make hostile
terrain survivable; it may never become a travel mechanism. A future reader who finds
this suit and thinks "so pawns can dive now" has it backwards — see
`CRACKEDLANDS_RULED_CONTENT_1` step 6.

**Item shape:** apparel, shell layer + full body coverage, crafted from `RUT_CrackWax`
(+ fabric/frame component), heavy move/work penalty appropriate to a sealed suit,
modest armor. The stat/hediff mechanism that reads "this pawn survives water terrain"
is the mechanics item's; the reconciliation line above binds it whatever the mechanism.
Utinni-side the recipe is discovered here (crack-wax is this biome's material); the
RM_ tier ships it with the biome mod per the standing Q11a face rule.

## Roster wiring summary

Executable summary — the build ticket is `CRACKEDLANDS_RULED_CONTENT_1`; wildAnimals /
wildPlants use the **shorthand element form** (`<DefName>commonality</DefName>`),
never `<li>` (a `<li>` silently discards the whole entry).

**OUT — the vanilla terrestrial zoo** (owner, turn 2: *"remove all terrestrial
(vanilla Earth) life from the roster as usual"*). `RM_FloodedCanyon_Biome.xml`'s
inline rows all go: Iguana 1.0, Dromedary 0.4, Fox_Fennec 0.3, Warg 0.15, Rat 0.6,
Cougar 0.06 — and the inline vanilla flora (Plant_Grass, PincushionCactus,
SaguaroCactus, Agave, Bush, Dandelion) goes with it, replaced by the owned flora set.
`animalDensity`/`plantDensity` stay explicitly set after the eviction.

**MIGRATES to owned RM_ defs — reusing existing art, queue nothing** (Q11a: the free
mod looks the same as the campaign one; Q12–Q15 per-sitting migration):

| current def | band | note |
|---|---|---|
| `RUT_SealedSleeper` 0.2 | Sealed (signature) | also fix: today missing from the RM_ patch entirely |
| `RUT_EmperorVulture` 0.15 | Patient (sky) | real flight; also missing from the RM_ patch |
| `RSW_SandLeaper` 0.2 | Spenders | invented exotic, not canon |
| `RSW_SandPillar` 0.5 | small | invented exotic |
| `RSW_Creature_Mantrap` 0.15 | Patient | **the Fang Leaf relabel lands here — verified this pass against both defs' own descriptions.** Both cite the Venus flytrap, so ancestry does not discriminate; FORM does: this one is *"proto-feet… can move very slowly"* at spd 0.15 — a near-stationary lure predator that reads as a plant. The Miasma's `AA_Mantrap` (Alpha Animals) is the engineered war-animal form — bs 2.0, mobile, *"concentrated formic acid spit launchers"* — and keeps its label; it is that biome's business. New label here: **fang leaf**. defNames untouched. |
| `RSW_MutagenicNorphea` 0.4 | Sealed | label ships as-is (batch-4h *qattora*/*norphea* DRAFT) |

**NEW natives** (this document, art this commission): `RM_Muttavaq` (pan giant),
`RM_Uttaqar` (crag giant — donor `DA_RockTroll` row leaves, ours replaces),
`RM_Irqit` (Spenders), `RM_Tarruq` (Patient), `RM_Veqma` (flora).

**OFF the roster, onto the roads:** `RSW_Eopie` — owner, turn 2: common beasts have
**one native biome** and TRAVEL to the others; the eopie leaves this roster (and its
other guest rosters at their own sittings) and arrives with merchants — trader stock /
caravan pack-animal availability instead of a wild row.

**STAYS — canon on the RSW_/Utinni layer:** `RSW_Gornt` 0.3, and the three fliers
`RSW_CanCell` 0.2 / `RSW_Convor` 0.2 / `RSW_Woolamander` 0.15 — owner, turn 4: the
fliers are **guests and migrants** here under the migration carve-out (they nest in
the Desert, ban 4 holds). Donor rows `AA_Murkling` 0.2 / `AA_SandSquid` 0.1 stay
inline per the standing donor-fauna acceptance.

**Names:** batch-4h renames (qattora, qetta, saqqat, luttaq, uttaqar-as-label) remain
DRAFT — owner passed twice; **current names ship**, and only the ruled Fang Leaf
relabel applies. The full FloodedCanyon→CrackedLands rename is
`CRACKEDLANDS_FULL_RENAME_1`, gated on its own live-tile/savegame check.

---

*Art register for everything above (sheet §9): cracked clay grey-white, red-brown
flood stain, moss green only in the blue slot-shade, the hardest light contrast on the
planet — dry then sudden. Queued this sitting in
`infrastructure/artpipe/art_lists/cracked_lands_bedazzle_cast.csv`.*


TASK: Give 8 to 12 recommendations that would make The Cracked Lands (formerly Flooded Canyon) richer, more memorable and more distinct, filling the weakest of the nine marks first. Improve and extend what is ruled rather than restarting it. For each recommendation:
- **Name** and a one-line pitch
- What the player sees, hears and feels
- Which of the nine marks it lifts
- How it could be built in RimWorld 1.6 and a rough size (XML only / small C# / large C#)
- Why it belongs to THIS biome and no other

Then list your TOP 3 in rank order with one line of why each. Reply in Markdown, at most about 1500 words. Do not ask questions; do not modify any files.