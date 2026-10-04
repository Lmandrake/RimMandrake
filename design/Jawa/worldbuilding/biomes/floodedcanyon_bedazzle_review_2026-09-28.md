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
| `AA_Murkling` | 0.2 | Spenders | donor | eats the flood's drowned dead; **multi-homed**: also Forsaken/Abyss (annotate, that sitting's call) |
| `RSW_SandLeaper` | 0.2 | Spenders | RSW_ port | draft *qetta* |
| `RSW_Gornt` | 0.3 | Patient | RSW_ port | seep-edge pouncer |
| `RSW_Eopie` | 0.25 | Patient | RSW_ port | ⚠️ **5 homes** (Desert, Leaning Scrub, Long Shade, Weeping Stones, here — MEASURED sweep). SW canon icon carve-out; annotate for the one-home law, do not evict here |
| `RSW_Creature_Mantrap` | 0.15 | Patient | RSW_ port | lure predator at the hidden water; draft *saqqat* |
| `RUT_EmperorVulture` | 0.15 | Patient (sky) | ours | real flight (`MaxFlightTime 60`); 🔴 **frozen twin only — missing from the RM_ patch** |
| `RSW_CanCell` / `RSW_Convor` | 0.2/0.2 | flier-commuters | RSW_ ports | nest in the Desert (ban 4). Convor also Fever Wood/Greentide/Leaning Scrub — flier-migrant carve-out plausibly applies, annotate |
| `RSW_Woolamander` | 0.15 | walking resident | RSW_ port | canon arboreal, no flight (owner, 2026-10-03) |
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
