# Nightside Ice: bedazzle review (grandfathered sitting, movements 1-2)

Item: `NIGHTSIDEICE_BEDAZZLE_SITTING_1` (BENCH). Program: `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, track (a), worst-first, sitting 1.

_BENCH design pass, 2026-10-01. First sitting of the grandfathered track, chosen worst-first by
`grandfathered_bedazzle_scores_2026-10-01.md` (§ Nightside Ice, and its sitting order row 1). The
sheet `nightside_ice.md` is frozen and owner-ratified, with the §4c tunneler slate ratified
2026-09-24 (`NIGHTSIDE_ICE_DESIGN_SITTING_1`). **Nothing ruled there is re-argued here.** This
sitting is mostly turning ratified words into tickets, plus the three marks nobody ruled (6, 7, 9)._

Sources read, all on `origin/main`: `src/RimMandrake/NightsideIce/` (whole tree),
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_NightsideIce.xml`,
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_NightsideIce.xml` and `NightsideIce_Rename.xml`,
`design/Jawa/worldbuilding/biomes/rosters/nightside_ice.json`, `infrastructure/artpipe/registry.jsonl`
and `done/`. No tile counts are reported (the planet is painted once, at the end).

## 1. What is there: ruled vs built

### The mod is one BiomeDef and a settings stub

`src/RimMandrake/NightsideIce/` holds `About.xml`, `RM_NightsideIce.xml` (label *"the Sleeping
Ice"*), `RM_NightsideIceMod.cs` and its DLL. Nothing else: no ThingDef, no IncidentDef, no
WeatherDef, no SoundDef, no comp. The frozen twin `RUT_NightsideIce` carries the world until the
repaint and is not edited.

What the def does carry, correctly per §6: terrain `Ice` only, no ponds (the vanilla
`terrainPatchMakers` block is dropped), no fish, no plants, `Clear` 100 and every precipitation
weather at 0, `soundsAmbient` dropped (no wind on the interior), `animalDensity` 0.2.

### Fauna, merged (inline + patch-added), read as XML elements

| def | label as shipped | tier | wired? | ruling | state |
|---|---|---|---|---|---|
| `AA_BoulderMit` | boulder mit (donor) | free inline, 0.004 | yes | **EVICTED** 2026-09-24 | 🔴 still shipping |
| `AA_SummitCrab` | summit crab (donor) | free inline, 0.004 | yes | **EVICTED**, moves to Weeping Stones | 🔴 still shipping |
| `AA_RedGoo` | red goo (donor) | free inline, 0.003 | yes | **EVICTED** | 🔴 still shipping |
| `AA_Terramorph` | terramorph (donor) | free inline, 0.003 | yes | **EVICTED** | 🔴 still shipping |
| `AA_Slurrypede` | slurrypede (donor) | free inline, 0.002 | yes | **EVICTED** | 🔴 still shipping |
| `AA_TetraSlug` | tetra slug (donor) | free inline, 0.002 | yes | **EVICTED** | 🔴 still shipping |
| `AA_ShockGoat` | **zhissa** (renamed by `NightsideIce_Rename.xml`) | free inline, 0.03 | yes | visitor, kept | donor body, campaign-only rename |
| `RSW_CaveLemming` | **mahllik** | campaign patch, 0.03 | yes | visitor, kept | built (ported) |
| `Tauntaun` | tauntaun | campaign | **no** | visitor-dying, kept | unwired |
| `Wampa` | wampa | campaign | **no** | visitor-dying, kept | unwired |

Census by description, not defName: the zhissa's patched description (*"Six eyes see nothing on
the nightside; the zhissa reads the world entirely by heat instead"*) is the only shipped text that
speaks the biome's thermal law. The rename lives in a **Utinni** patch, so the free tier ships the
donor's own label and description for its one remaining animal.

🔴 **Finding: the 2026-09-24 eviction was never executed.** The roster JSON records all six donor
residents as evicted, but `RM_NightsideIce.xml` still lists all six inline. After the eviction the
free tier's whole cast is one donor visitor (`AA_ShockGoat`) with a donor label. Q11a (*"rich
enough to stand alone"*) fails outright.

### Ruled natives: all unbuilt

`git grep` over `origin/main -- src` for shivven, frissim, dhorrumak, sohl and wyrmlet returns
**0 files** (sanity probe: the same search finds the names in `design/`).

| ruled | what it is | mechanism owed | art |
|---|---|---|---|
| **sohl** | the one-move animal: terrain until it commits, once, then inert forever | C#: century accumulation, one commit, inert-alive corpse | none |
| **shivven** | the tunnelers: blind, thermal, within the ice, colonial | C#: sub-surface movement with a surface tell, thaw surfacing | none |
| **frissim** | icy insects of the inclusions, dormant until a thaw | dormant-until-thaw comp | none |
| **dhorrumak** | the apex ice wyrm, surfaces only under sustained heat | C#: sustained-heat trigger | none |
| **wyrmlets** | juvenile dhorrumak, feed on frissim | surface at thaws and slab-falls | none |
| *(unnamed)* | hectare-scale sessile catalytic sheets: *"a ridge is an organism"* | C# or building hybrid | none |
| *(terrain)* | chemical frosts ambiguously alive; the hoarfrost forms (§4c.7) | scatter terrain features | none |

### Ruled mechanics: all unbuilt

From §3, §4, §4b and §4c: thermal sensing (your heat is the threat generator) · the thaw pulse ·
calving delivery (inclusions: machine parts, cocoons, the well-provisioned dead) · the lost soul ·
rime-fall and ablation at the margins · the reconnection storm · the crags' Dark drifting over ·
the rumble-tell · the insect-fall · heat-drawn assailant incidents · the breach loop with its
continuous heat dial · the hull rule (no burst through floor or hull) · the larder and cut-down
recovery · the apex ladder (frissim → wyrmlets → nest → dhorrumak) · dirty ice (melt and filter) ·
cold as a resource · the electrojet tap · buried, bermed structures.

### Mechanisms already in `src/` that the slate can reuse (searched before proposing)

- **`RM_CompSandSwim`** (`CreatureBehaviors`, `STILLSAND_SAND_SWIM_KIT_1`): a submerged-moving
  pawn with a per-tick **rumble** sustainer, breach-to-strike and resurface. It is most of the
  shivven's rumble-tell already. It is the Stillsand's *package*, so the shivven must keep their own
  voice: they track **heat**, never footfall, and travel inside ice, not sand.
- **`RM_MapComponent_ChillAuroraSurge`** + `RM_CompPowerPlantAuroraSurge` (`DivingInteraction`):
  an aurora-surge power hook built for the Chill Sea. It is the electrojet tap's mechanism, and it
  is reusable for the reconnection storm's *"circuits surge"*.
- **`BlueDesert`'s buried-pawn hediff and jobs** (`RM_MurrekBuried`): a pawn hidden under terrain.
  Prior art for the larder.
- Vanilla/DLC shapes the sheet already names: VFE siege-burrow (breach staging object), Anomaly
  pit-gate warning tiers, Anomaly's open-ground placement rule (the hull rule).

### Art state

Done and unwired-or-wired: `nightside_zhissa_*` and `nightside_mahllik_*` (3 facings each),
`canon_wampa_v1_*`. **Nothing** for sohl, shivven, frissim, dhorrumak, wyrmlets, the ridge
organism or the hoarfrost forms. No review-sheet ruling on any of these was found
(`Transient/*decisions.json`, searched).

### Weather, sound, ship, gods

- **Weather:** `Clear` 100. The aurora is prose only; no WeatherDef exists.
- **Sound:** none. The ambient was deliberately dropped.
- **Ship:** nothing.
- **Gods:** nothing. `AncientDangerGenSteps_AmbientDoctrine.xml` *prevents* shrines on both defs.


## 2. Scorecard

Ruled counts as HIT; built is reported beside it. Mark sources are the scores doc, re-read against
the sheet.

| # | Mark | Free (ruled) | Campaign (ruled) | Built today | Note |
|---|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | 0 | the heat dial and the shivven breach loop |
| 2 | Discoverable technology | PARTIAL | PARTIAL | 0 | cold as a resource and the electrojet tap are uses, nothing is *learned* |
| 3 | Unique resources | **HIT** | **HIT** | 0 | dirty ice; calving inclusions |
| 4 | Surprising creatures | **HIT** | **HIT** | 0 (donor rows evicted on paper) | the sohl |
| 5 | GIANT beast | **HIT** | **HIT** | 0 | the ridge organism has no def and no name |
| 6 | Gravship touch | MISS | MISS | 0 | the hottest thing on the hemisphere is unclaimed |
| 7 | Soundscape | MISS | MISS | 0 | *"tunnels that make the wind sing"* is cited, not ruled as sound |
| 8 | Interesting weather | **HIT** | **HIT** | `Clear` 100 | thaw pulse, rime-fall, reconnection storm, aurora-clear |
| 9 | Relationship to the gods | MISS | MISS | 0 | shrines prevented; no rite |

**Free 6 / 1 / 2 ruled, 0 built. Campaign the same, plus one ported visitor (mahllik) built.**

Two marks that read HIT are thinner than they look:
- **Mark 5** is the best-argued giant on the planet with no name. Naming it is a §3 fill.
- **Mark 4**'s free tier, once the eviction is executed, is one donor goat until the natives land.


## 3. Roster fill

### The gaps, read from the sheet only

The sheet is the hardest admission test on the planet (*"very short, very strange, and mostly not
obviously fauna at all"*), so the fill is small on purpose. The ruled cast covers small life
(frissim), the mid-tier threat (shivven), the surprise (sohl) and the apex ladder (wyrmlets →
dhorrumak). Three holes remain:

| hole | why it is a hole | fill |
|---|---|---|
| The giant has no name or def | mark 5 rests on one sentence: *"a ridge is an organism"* | **hessarund** |
| Nothing alive touches the ship | mark 6 MISS; a landed hull is the warmest interface on the hemisphere | **kesshet** |
| The free tier's only surface animal is donor | after the ruled eviction, `AA_ShockGoat` is the whole free cast, with a donor label | **zhissa, ported to `RM_`** |

### Proposed fills: 2 new creatures + 1 port, all `RM_` tier, one home each

Names follow the ruled accent (shivven, frissim, sohl, dhorrumak: soft sibilants, *dh*, doubled
consonants). `git grep` over `origin/main -- design src` returns 0 hits for each proposed name
(sanity probe: `shivven` hits).

1. **hessarund** (`RM_Hessarund`), the ridge organism. *Mark 5.* A ridge, several hundred cells
   long, that is one catalytic body lying on a seam where two frosts should react and cannot. It
   looks exactly like a ridge. Told apart only by its tells: frost that sublimates off it in slow
   patterns, a seam-line that is faintly warmer than the ice, and mining it yields catalyst crust
   instead of stone. Behaviour is the card's question (§7 Q2): GPT's bargaining ridge, a slow creep
   toward waste heat, or a quiet landform. Build shape: a `MapComponent` that owns a set of
   mineable `ThingDef` plates (Fever Wood's six-limb `RM_CompTentacleLimb` is the precedent for one
   body met as many parts). Alternates: thessul, olvesh, ossuvel; GPT's own name is *Vhal*.
2. **kesshet** (`RM_Kesshet`), the hull crust. *Mark 6, creature side.* A sessile crust that
   settles on a landed gravship's hull where waste heat meets −40 °C, the steepest gradient on the
   hemisphere, and catalyses there. It grows in a visible rime-ring around the hull footprint over
   days; it cannot breach (the hull rule), but it raises the ship's heat signature (it radiates
   what it feeds on) and it must be scraped before launch or it tears free as a crusted debris
   field and a mood hit. Scraped, it yields a superconducting film (cold as a resource, made
   learnable). Readable from the first day: a frost halo on the hull edge with a hover label.
   Not a pawn: a `ThingDef` scatter attached to hull-edge cells by a `MapComponent`, 1.6
   `Building_GravEngine` presence as the gate (the `PlaceWorker_NeedsGravEngine` precedent).
3. **zhissa, ported** (`RM_Zhissa`, absorbing `AA_ShockGoat`). The owner already asked for it
   (*"Refashion into nightside biomes ... make pale blue aura around it"*, roster JSON). The
   thermal-reading description moves from the Utinni rename patch into our own def, so the free
   tier speaks the biome's law. Its static discharge is a visitor's trait, not resident glow
   (§6's glow ban binds residents). Art exists (`nightside_zhissa_*`, 3 facings, built from the
   donor body); whether it counts is an art-review question, not this card's.

Not filled: a free-tier dying-visitor herd. The zhissa is it, and the tauntaun and wampa carry the
campaign. Flora stays empty by law.


## 4. The slate

The sheet is ratified, so the slate is an **order of build**, not a menu of designs. Every row
below is ruled; only the order and the new marks (§5, §6) need the owner.

**0. Housekeeping (ruled, no card needed).** Execute the 2026-09-24 eviction: remove the six
`AA_` rows from `RM_NightsideIce.xml` (summit crab goes to the Weeping Stones under its own
sitting). Wire `Tauntaun` and `Wampa` onto `RM_NightsideIce` through `WildAnimals_NightsideIce.xml`
at the roster's 0.03. Size S.

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The heat dial and the shivven breach loop.** A `MapComponent` that totals colony heat output (heaters, fires, powered buildings, warm rooms against outdoor) into one continuous dial; breach staging cracks (attackable, VFE siege-burrow shape) open only in open ice at the base's edge (the hull rule); the first breach is timed and taught, later ones vaguely warned; the shivven ride a heat-seeking retune of the sand-swim kit with the rumble-tell. | 1, 4 | `RM_CompSandSwim`, Anomaly pit-gate warning tiers | L |
| 2 | **Thaw pulse, calving delivery and the lost soul.** A `GameCondition` that softens ice near any heat source above a threshold; slumps and calves along crevasse lines; a `ThingSetMakerDef` of inclusions (machine parts, cocoons, the well-provisioned dead); the lost-soul incident with the shivven already coming. | 3, 8 | vanilla incident and quest shapes | M |
| 3 | **The sky.** An aurora-clear `WeatherDef` (cold overhead light, no warm tint), the reconnection storm as a `GameCondition` (radiation, circuit surge, the shivven stir), rime-fall and ablation drift at the margins only. | 8 | `RM_MapComponent_ChillAuroraSurge` | M |
| 4 | **The sohl.** Terrain until it commits, once, then an inert-alive body forever. | 4 | the dormancy comps (roster `new_defs` names a 107-row donor dormancy comp) | M |
| 5 | **The larder.** Downed pawns dragged under (a visible drag trail into the crack, a letter naming who); cut-down recovery into warren territory. | 1 | `RM_MurrekBuried` (Blue Desert) | M |
| 6 | **The apex ladder.** Frissim (dormant until a thaw), wyrmlets (surface where frissim stir), the nest eruption, the dhorrumak under sustained heat. | 4, 5 | build 1's dial | L |
| 7 | **The ice forms.** Hoarfrost scatter features across the interior, chemical frosts; real hoarfrost photography as the art target. | look | terrain scatter | S, art-heavy |
| 8 | **Art commission.** sohl, shivven (the tell graphic matters more than the body), frissim, wyrmlet, dhorrumak, hessarund plates, kesshet, the hoarfrost family. None exists (§1). | all | artpipe | — |

Recommended: **0 and 1 together first.** The heat dial is the biome's law and every later package
reads it. Thaw pulse (2) is the cheapest second because it makes the dial bite without new
creatures.

Then the three unruled marks (6, 7, 9) and the PARTIAL (2) come from §5 and §6.


## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-01/nightsideice.md` (prompt beside it), run
2026-10-01 under the owner's new standing rule: exactly five ideas, each different from the others
and from every other biome's signature (the prompt lists all of them, one line each), with research
on other games and RimWorld mods cited. Model `gpt-5.6-sol`, via `codex exec`.

GPT's own check lines: verbs *tune, bargain, ballast, compare, reconcile*; systems *audio and
recreation, living-terrain morphology, gravship cargo and stress, research and reverse-engineering,
Ideology and faction obligations.*

| # | GPT's idea (faithful summary) | marks | GPT cites | BENCH judgement on uniqueness |
|---|---|---|---|---|
| 1 | **The Kharu Breath-Choir.** Mining opens sealed air bores squeezed by the creeping ice. Colonists fit stops and tune notes by routing ordinary heated air through the gallery; the outside stays windless. Recreation and a small sleep bonus, but playing it raises the heat dial. *"Making this dead place sing means announcing yourself to it."* Free tier, M. | 7 | Dwarf Fortress instruments, ONI thermo sensors, Dubs Bad Hygiene heating | **Unique, and the best answer to mark 7.** It is the canon anchor (*"tunnels that make the wind sing"*) made playable, and it pays in the biome's own currency, heat. Not the Stillsand's Listening (that detects); this is played. |
| 2 | **Vhal, the Ridge That Bargains.** A whole ridge is one organism with an inspectable chemical reserve. Offer minerals at one mouth, lay a warm-and-cold pattern at another, and it may spend centuries of savings to retract one lane and raise a defensive ridge elsewhere. Never into occupied cells; each request costs more. *"Uneasy reciprocity."* Free, L. | 5 | Anomaly fleshmass heart, Timberborn terrain blocks | **Unique on the planet** (no other giant is topology with agency), and it fits *"motion is paid for out of savings"*. Risk: it is a trade with the land, close to Mob'Unloo's register, and it is the largest build here. Card Q2. |
| 3 | **The Keel-Press.** A landed gravship deploys four press gauges. Ballast its quadrants with cargo; the shifting centre of mass loads one arc of deep ice until a stress fan calves up a seam of preserved wreckage, while the powered ship stays the brightest target. Free, L. | 6, 3 | Odyssey gravship, DF cave-ins, Below Zero Seatruck | **Unique mechanism, weakest fiction.** No other biome uses ship mass, but a ship pressing ice by cargo placement strains belief, and it competes with calving, which is already ruled. BENCH prefers the kesshet (§3) for mark 6, which uses the ship's heat, the biome's own law. |
| 4 | **The Sevren Witness Method.** Calving returns pristine manufactured objects tagged by function and era. At a comparison frame, set two ancient versions of a mechanism beside a colony-made one; an intellectual pawn works out what changed. The first valid trio reveals a hidden research row; mastered, comparative reverse-engineering works on any map. Free, M. | 2 | Caves of Qud tinkering, Royalty techprints, VFE Ancients vaults | **Unique, and the cleanest mark 2 on the planet**: it turns *"perfect preservation"* into something *learned*, and it travels. Not the Cracked Lands' read-the-land (that reads ground; this reads lineages). |
| 5 | **Mob'Unloo's Ninth Account.** Some calved dead carry a ledger tablet: what they owed, to whom, why death did not close it. Loot and disclaim, leave it, or inherit the debt as a concrete quest (deliver goods, repair a machine, ransom someone, aid the creditor). Closing it turns a frozen corpse into remembered history. Campaign, M. | 9 | Ideology beliefs, Against the Storm orders | **Unique, and it feeds the starved god.** Not the Abyss's Blind Offering (an item left in the dark) nor the Wasteland's Storm's Receipt (counting finds). §6's Cold Ledger is its rite form. |

GPT's own build-first ranking: the Sevren method, then the Breath-Choir. BENCH agrees on both, and
adds the kesshet for mark 6 because it costs less than the Keel-Press and speaks the heat law.


## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): each rite is found at a site with a reason to
be there, learned through the Rites tab's found-rites row (`mandrake.rut.rites`), and performable
anywhere afterwards. Campaign tier. God balance (`biome_rites_pass_2026-10-01.md`, coverage table):
Oomo is overfed at 4 and gets nothing here; **Mob'Unloo is starved at 2** and gets two; Ishko has
only ever been *fed*, so his rite here is a new kind for him. No kind repeats inside this biome.

**Not taken: a burial in the ice for Rekko** (the scores doc's seed). The Abyss's Lightless Burial
already lays the dead down in the deep dark, so a second burial rite would be the same act.

### R1. The Cold Ledger, for Mob'Unloo: consolation

- **Grounding:** *"an unpaid debt follows you past death"*; a settled ghost is *"a balanced
  ledger"* (§2.0b ④). The dead here are perfectly kept, so their debts are too.
- **Found:** a ledger tablet on a calved expedition corpse (GPT idea 5's tablet is the inscription).
- **Asks:** the colony keeps the dead one's goods and names the debt. An organiser cuts a niche
  into open ice at the find-site and seals an equal-value counter-gift inside. The ice keeps it, in
  sight, forever.
- **Outcomes:** Poor, the ice heaves the gift back out at the next thaw (the debt stands, the
  tablet says so). Fair, the debt is closed: the goods carry no dead-man's-goods thought. Good, plus
  a consolation entry for Mob'Unloo sized by value. Excellent, plus the tablet names the next
  inclusion on this map, and it calves where it said.
- **Readable sign:** the gift stays visible in a clear ice block; its hover names the debt and
  the dead.
- **Collision check:** the Blind Offering (Abyss) is an item taken in the dark by an unseen hand;
  here nothing is taken, and the payment is on display. New kind for Mob'Unloo.

### R2. The Exchange at the Crack, for Mob'Unloo: feeding

- **Grounding:** *"Enemies are just another commodity"*; *"captured body = captured value"*
  (§2.0b ④). The larder is a store, and stores can trade.
- **Found:** tally marks scratched beside an old, frozen breach crack, where a Junker expedition
  traded its dead for its living.
- **Asks:** a colonist has been dragged into the larder (§4c.5). The organiser lays an enemy's
  corpse, or a downed prisoner, at an open breach crack, and everyone steps back past the floor
  line (the hull rule: the crack is in open ice).
- **Outcomes:** Poor, the offering is taken and nothing returns (the crack shows the drag
  trail). Fair, the stored colonist is pushed back up at the crack, frozen and alive if downed
  within the wampa rule's window. Good, plus the warren's next breach comes later. Excellent, plus
  Mob'Unloo feeding sized by the offering's value. The alternative stays open: cut down and fetch
  them by force.
- **Readable sign:** drag trail in, a returned body at the lip, a letter naming both.
- **Collision check:** the Storm's Receipt (Wasteland) is counting finds; this is a trade with
  beasts. Same god and kind, a different act.

### R3. The Cold Hearth, for Ishko: warding

- **Grounding:** stillness and *"the prepared dark"*; attrition defence; to stay unseen (§2.0b ①).
  On this hemisphere, unseen means **cold**.
- **Found:** carved inside one bermed refuge whose occupants are absent, the one shelter on the ice
  whose people lived.
- **Asks:** for one night every heater, fire and powered heat source is put out, and every
  colonist lies still, wrapped. Quality from how low the colony's heat dial falls and how long it
  holds. Real vanilla cold applies: hypothermia is the price.
- **Outcomes:** Poor, someone's frostbite and nothing gained. Fair, "we lay cold" (shared memory).
  Good, the heat dial's breach pressure drops a step for a season. Excellent, plus Ishko's mark on
  the refuge wall (`RM_Ishko_RitualOutcome_PlaceSacredMark`, built and waiting).
- **Collision check:** the Snuffing (Abyss) puts out *lights* to starve Sh'kaar; this puts out
  *heat* to hide from beasts. Abyss rites need darkness; this needs cold. First warding rite for
  Ishko.

Tally if all three are admitted: Mob'Unloo 2 → 4, Ishko 3 → 4 (now two kinds). No god above four.


## 7. Owner turn-1 card

Four questions, plain words. Headers are 12 characters or fewer, for `AskUserQuestion`.

**Q1 · header "Build first" · What should FOUNDRY build first for the Nightside Ice?**
- **The heat dial and the tunnelers (recommended).** Your heating draws the shivven; cracks open
  at the edge of your base; the first one is taught. Big build. *Why: it is the biome's law, and
  every later piece reads it.*
- **The thaw and the calving first.** Warmth softens the ice, it slumps and gives up what it
  held. Medium build, and the ice feels alive before any creature exists.
- **The sohl first.** The one-move animal alone. Medium build, one great surprise, but nothing
  else moves yet.
- **Commission everything at once.** Every ruled piece in one order. Largest and slowest to see.

(Either way, the six evicted donor animals come out now, and the tauntaun and wampa go in. That
was already ruled.)

**Q2 · header "The giant" · What should the living ridge do?**
- **It bargains (GPT's idea, recommended).** Pay it minerals and a warm-and-cold pattern, and it
  slowly moves a ridge for you. Each favour costs more; it never moves onto anything. *Why: no other
  giant on the planet is the map itself, and it fits "motion is paid from savings".* Large build.
- **It creeps toward your heat.** Over seasons the ridge grows toward a warm base, a siege by
  landform. Medium build, more threat, less wonder.
- **It is only a landform.** You can tell it is alive and mine catalyst from it. Small build,
  quiet.

Name: **hessarund**, or GPT's **vhal**?

**Q3 · header "New marks" · Which of these new pieces do you want? (pick any)**
- **The Breath-Choir (sound, recommended).** Tune sealed ice bores into a choir with heated air.
  Lovely recreation, but playing it raises your heat. *Why: it gives a silent biome its voice and
  costs the right thing.*
- **The Witness Method (learned tech, recommended).** Compare old machines the ice gave back with
  your own; learn a research method that works anywhere. *Why: the cleanest "discovered tech" on
  the planet.*
- **The kesshet (ship).** A crust that grows on your landed ship's warm hull; it makes the ship
  hotter, must be scraped before launch, and gives a superconducting film.
- **The Keel-Press (ship).** Shift cargo in your landed ship to press the ice until it cracks open
  a seam of wreckage. Large build; GPT's pick for the ship, BENCH's second.

**Q4 · header "Rites" · Which rites should the ice teach the Salvation? (pick any)**
- **The Cold Ledger (Mob'Unloo, recommended).** Pay a frozen dead man's debt by sealing a gift in
  the ice, where it stays in sight forever. *Why: feeds the god with the fewest rites.*
- **The Exchange at the Crack (Mob'Unloo).** Trade an enemy's body at a tunnel crack for your own
  colonist the tunnelers took.
- **The Cold Hearth (Ishko).** Put out every heater for one night and lie still; the tunnelers lose
  you for a season. Hypothermia is the price.
- **None for now.**

