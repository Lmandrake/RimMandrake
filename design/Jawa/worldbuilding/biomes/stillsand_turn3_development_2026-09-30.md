# The Stillsand — volley turn 3: developing what the owner ruled

**Item:** `STILLSAND_BEDAZZLE_SITTING_1` · BENCH design agent · 2026-09-30
**Reads:** `stillsand_bedazzle_review_2026-09-29.md`, `stillsand_bedazzle_2026-09-27.md`,
`stillsand_roster_fillout_2026-09-27.md`, `dune_sea.md`, `deep_desert.md`,
`SOLAR_HEAT_EXPOSURE_1`, `SHADE_GEAR_FAMILY_1`, `longshade_shade_ideation_2026-09-29.md`.

## 0. The owner's words

Volley turn 2, typed (ledger note on `STILLSAND_BEDAZZLE_SITTING_1`, 2026-09-30T07:05Z), plus one
line relayed mid-turn. Nothing below re-argues any of it.

- *"The listening should focus on wind and sand Noises and then ominous rumbling as things swim
  through the sand or bury their way to the surface. The sand swimmer mod is. Major player here."*
- *"Stillsyork makes no sense as a name. Call it a dune gale."*
- *"I like your religious implication of a ritual here."*
- *"So it would be that the very fine sand of this region is extremely high quality and can be
  smelted into a fine glass fit for lenses. The lenses can be made into high performance solar
  stills and ovens."*
- *"The biome takes its sun angle from its latitude ok the planet not a region description."*
- *"This biome needs event level creatures. Attacks by the mighty krayt dragon. And others."*
- *"The rare rock should be celebrated and almost always featuring a precious cave."*
- *"Overheating here should be trivial and difficult to avoid."*
- *"Take all these ideas and beef them up. Expand them ronustify them and then suggest yet more.
  This is THE poster biome of the old tattoine. Huge skeletons on the sand. Barren tracks of
  apparent nothingness."*
- Relayed during this turn: *"And make sure to read the moving dune mod and the sand swimmer mod.
  This is where they shine."*

Standing law carried in: the admission test (*"if it makes the map busier it is wrong —
everything admitted is buried, dormant, giant, or a line"*, `stillsand_bedazzle_2026-09-27.md`
§1), and the Long Shade condition that **every loss of an animal or pawn leaves a readable sign**
(*"we can't have animals "disappear spontaneously." There needs to be SOME kind of indication of
what happened to them."*).

## 1. The Stillsand, one paragraph

You land on a plain that runs flat to every horizon, the colour of old bone under a white sky. The
sun has not moved since the world began. The only sound is the wind: one hiss, from one bearing,
that has never turned. Every dune crest runs the same way and every shadow points the same way,
so the whole landscape is a compass pointing at the star. A kilometre off, the ribcage of
something that died before your clan had a name stands out of a dune, and the wind moans through
it. There is a track across the flat, a trough in the sand that runs straight for a hundred cells
and then simply stops, at a patch of sand that is darker than the rest. Your colonists start
cooking the moment they step off the ramp. The nearest rock is a single outcrop on the horizon,
and everyone who has ever lived here knows there is a cave in it and something precious in the
cave. Then, under the hiss, a sound you feel in your teeth before you hear it: a long, low
rumble, moving. A line of sand lifts and falls, far out, travelling. **This is old Tatooine: the
place Jawas were made for, and the place that made the krayt.** It looks like nothing. It is
full, and all of it is underneath you.

## 2. The ruled ideas, developed

### 2.0 What the two sand mods actually are (the owner: "This is where they shine")

Everything here was MEASURED this turn (2026-09-30). I read the source, the About files and the
live `ModsConfig.xml`, and swept every installed About.xml by `<name>` AND `<description>` across
both roots, `...\common\RimWorld\Mods` and `...\workshop\content\294100` (2,818 About files).
**Sanity probe:** "gravship" found 41 mods. Neither mod has "dune" or "swimmer" in a way that
identifies it by name, and neither turned up under those words. Both are **our own**, and both
were found by their item ids inside other mods' descriptions.

#### The moving dune mod: `mandrake.rm.movingdunes`

- **Source:** `D:\Luke\dev\Rimworld\src\RimMandrake\MovingDunes\`. Spec:
  `D:\Luke\dev\Rimworld\design\MOVING_DUNES_DESIGN.md` (v2). Open item: `MOVING_DUNES_BUILD_1`.
- **Installed:** not as its own folder. It ships inside the unified biome mod, at
  `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\RimMandrake.Biomes\Biomes\MovingDunes`.
  That mod's `LoadFolders.xml` lists `Biomes/MovingDunes` beside `Biomes/Stillsand` and
  `Biomes/_Kits/CreatureBehaviors`, and `mandrake.rm.biomes` is **active** (612 active mods).
- **What it does:** real wind-driven sand on Odyssey's `Map.sandGrid`, using Werner slab
  transport. It erodes, hops 2–6 cells downwind, and prefers to deposit in low and sheltered
  cells. The upshot:
  - drifts bank behind walls and scour the lee;
  - dug pits refill;
  - a crest creeps about one cell per 2.5 days, and 4× that in a sandstorm;
  - the map edges work as source and sink, with an influx budget and a mass cap.

  It also ships:
  - `RM_Dunes_BuriedCache`, plus a public `BuryThingsAt(cell, things, depth)` API. Wild items
    under deep drift become sealed caches that do not deteriorate, and they come back out when
    erosion drops the cell below 0.25;
  - **plant choke**, which slowly kills plants on an advancing front;
  - a per-map tinted sand layer;
  - `RM_DuneMaterialDef` (every number is data);
  - `DuneFieldExtension`: biome opt-in, plus a per-weather storm-transport override.

  `RM_Stillsand` is bound (Q12, done).
- **What it cannot do (its own ruled cut):** bury pawns, corpses or turrets; turn sand into a
  haulable item ("dig vanishes", RULED); grow drifts taller than depth 1.0.
- **Honest state:** per its open item, transport, burial and reveal are *"built, not yet observed
  live"*, and the shader-tint gate is still owed. ⚠️ **One conflict with the sheet.** The engine's
  wind direction random-walks over days, while dune_sea §2 says the wind *"has never once changed
  its mind."* §2.7 below shows the sun-angle ruling settles this: pin the wind to the same bearing
  as the sun.

#### The sand swimmer mod: `SAND_SWIMMERS_MOD_1`

The owner named it himself on 2026-09-06: *"Part of the 'sand swimmers' mod we are going to
make."* It was never shipped as one package. It was built into three homes:

| piece | where it lives | installed at | what it is |
|---|---|---|---|
| `RM_DeepSand` terrain | FlowWorks (`src\RimMandrake\FlowWorks\Defs\ManyWaters\TerrainDefs\RM_DeepSand.xml`) | `...\Mods\FlowWorks` (active) | Walkable at pathCost 300, per the 2026-09-27 ruling. Tagged `Water`, which is the load-bearing trick: vanilla fishing works on it with no patch. Recreational swimming is blocked by `RM_NoRecreationalSwimExtension`. The Stillsand paints it "Muchly" (threshold 0.2, perlin 0.03, minSize 60) |
| the catch, the hunter, the prize | SWBestiary (`src\RimStarWars\SWBestiary\Defs\...`) | `...\Mods\SWBestiary` (active) | `RSW_DuneCrawler` is the fish-category catch, a many-legged sand filter-feeder. `RSW_SandStalker` (bs 1.1) waits under a pool for "the vibration of a dune crawler, or a boot" and spends its whole strike on one lunge. `RSW_GlassPearl` is the rare prize, *"a lens that grew a skin"*. `RSW_RareSandCatches` is parented on vanilla's `RareFishingCatchesBase` |
| the fishing hookup | UtinniPatches `SandFishing_CrackedLands.xml` | `...\Mods\UtinniPatches` (active) | `fishTypes` only on `RM_FloodedCanyon` (the Cracked Lands twin) |

🔴 **The sand swimmers are not wired into the Stillsand at all.** `RM_Stillsand` paints deep sand
across most of the map, but **carries no `fishTypes`** (grep of the def, this turn). A fishing
zone on it catches nothing, and the dune crawler, sand stalker and glass pearl never appear in the
biome the owner calls their major stage. Two more gaps:

- **Nothing actually swims.** No shared sub-sand movement exists anywhere in `src/`. The swimmers
  run on stock AI, with bodies walking in plain view on the surface: the vekka, the qorrax, the
  drazzik, the sarlacc swimmer (`CompSarlaccSwimmer` is a water-budget and rooting comp, not a
  swim), the stalker and the krayts. That covers the sheet's *"things swim beneath it"*, the canon
  greater krayt that *"literally swam through the shifting sands"*, and the owner's
  *"things swim through the sand"*.
- **Tier drift:** the crawler and the pearl are invented, so under Q11a they belong at `RM_`.

#### Related content that is also in play

| thing | where | state | what it gives the Stillsand |
|---|---|---|---|
| **LEVIATHANS:SANDWORM** (`chezhou.creature.sandworm`) | `...\workshop\content\294100\3713982815` | **active** | A third-party Dune worm, built as a 50,000-HP building-class entity with a 5×5 hit proxy. It crushes, shoves and head-kills; destroys buildings, removes roofs and converts terrain to sand (a toggle); brings an "abnormal sandstorm" weather and its own music. It is summoned by a **sand hammer**: 10 h of accumulated vibration at a quest site. Its C# (`SandWormLib.dll`) is closed. Our repo already names it the *architecture reference* for VAST creatures (`setting_physics.md` Part 5), never a dependency |
| **The Long Hunger** (`mandrake.rut.longhunger`) | `src\RimUtinni\LongHunger\`, `...\Mods\LongHunger` | **active**, never live-fired (per its item) | Our own original-code VAST dune leviathan: erupts, pulses tremor damage, submerges dropping salvage. It comes with the `RUT_Groundcaller` prop (flavour only in v1), a contract quest, and an unwired `RUT_DuneHaze` weather. Its v2 list names the build-then-activate vibration loop, which is §2.1's thumper |
| **The krayts** (`RSW_KraytDragon` bs 12 / `RSW_GreaterKraytDragon` bs 15) | SWBestiary, ported from `mlie.starwarsanimalcollection` | wired **as ordinary wild animals**: 0.15 / 0.001 in `WildAnimals_Stillsand.xml` | Canon egg layers with combatPower 750 / 2000. No incident, no approach and no swim. Around them, in the stack: `RSW_KraytDragonSkull` + `ProcessKraytDragonSkull`, `RSW_KraytPearl` (and the lightsaber-crystal parts built on it), krayt call/angry/death `SoundDef`s, and the **`RSW_KraytGraveyard` mutator**. That mutator is a 20×20 scatter of skulls, horns and pearls; it is whitelisted to vanilla `ExtremeDesert`, not `RM_Stillsand`, and is unplaced |
| **The sarlacc** (`mandrake.rsw.sarlacc`) | `src\RimStarWars\Sarlacc\` | built | The swimmer → anchored → cistern → throat stages. Its seep marker (`RSW_DeepDesertSeep`) and the kill-sign filths `RM_Filth_DisturbedSand` / `RM_Filth_DragMark` (CreatureBehaviors) are the ready-made "readable sign" vocabulary |

⇒ **"Where they shine" in one line:** the dunes engine is the Stillsand's **surface memory** (what
the wind hides and gives back), and the sand swimmers are its **subsurface life** (what moves
under the hiss). The package below gives each of them a job in every ruled idea. It starts with
the two things they lack: swimmers that actually swim, and a dune wind that keeps one bearing.

### 2.1 The Listening — wind, sand, then the rumble

**This is the owner's correction to the review.** The review put everything in the ground and
left the air near-silent. He wants the opposite order. The **bed** is wind and sand, always there,
so the biome is never silent. The **event** is the rumble, which you learn to dread because the
bed never stops.

**What the player hears, layer by layer:**

1. **The hiss.** A dry, steady wind from one bearing that never turns. It is louder on crests and
   quieter in a lee. This is the Stillsand's room tone, and it is never switched off.
2. **The saltation.** Grains streaming along the surface, a fine seething that rises and falls
   with wind speed. You hear it before you see the sand move.
3. **The singing dunes.** When the dunes engine moves a slab off a slip face, the dune *booms*: a
   long, low drone, as real booming dunes do when an avalanche runs down the lee. The dunes are
   audibly alive. A quiet map is still singing, far off.
4. **The bone harps.** Wind through a giant's ribcage (§3) gives a hollow, pitched moan that sets
   each skeleton apart as a place you can find by ear.
5. **The rumble.** Something is moving under the sand. It is low, felt more than heard, and its
   loudness scales with the swimmer's body size. A vekka is a mutter. A krayt is a freight train
   one dune over, and it grows for a full minute before anything shows.
6. **The breach.** The sound of a thing burying its way *up*: the grinding, sliding roar of a
   sand-buster tunnel or a krayt surfacing, just before the dust column.
7. **The liars** (kept from the review): the drazzik's *"fat and wounded"* drum
   (`RM_CompDrumLure`, shipped), and the duumma's dry-husk drum (fill-out).

**What the player sees.** The rumble has a picture: the **sand wake**. While a swimmer is under,
the surface above it lifts into a low travelling ridge with a spray of grains off its crest. That
is the only visible sign, and it is **a line** (admission test: passes). The wake leaves a
**trough** that the wind fills over hours (§3, tracks). If the piinnok is admitted (review §6,
unruled), its lenses all sink when a big wake passes, so the player has a free visual warning to
go with the sound.

**What the player feels.** The Stillsand's specific dread is that **a quiet map is not a safe
map, and a loud one is not a warning**. The bed noise is always there. The rumble is the one
sound you learn to pick out of it. Because the bed is wind, a dune gale (§2.2) drowns the rumble
too, and that becomes a real trade.

**The mechanism: the sand-swim kit, which is "the sand swimmer mod" made real.**

- **`RM_SandSwimExtension` + `RM_CompSandSwim` (RM tier, CreatureBehaviors kit).** On a race, it
  sets:
  - which terrains it swims in: `Sand`, `SoftSand`, `RM_DeepSand` (and drift depth ≥ 0.3 from the
    dunes engine);
  - its rumble `SoundDef`;
  - its surface and dive rules.

  While the pawn is on swim terrain and not in melee, it is **submerged**:
  - it carries a hediff with vanilla's `HediffComp_Invisibility` (Anomaly's, and all DLCs are
    assumed), so it cannot be seen or targeted;
  - it emits the wake flecks and a rumble sustainer scaled by body size;
  - it leaves `RM_Filth_SandWake` trough filth that the dunes engine erases over time.

  It **surfaces** (hediff off, breach burst of dust flecks plus the breach sound, a short stagger
  on anything within one cell) when it strikes, when it crosses non-swim ground such as rock or a
  floor, or when it is hit. Hard ground is therefore a moat, which is exactly what the deep
  desert's *"the ground lies to you"* needs.
- **Signs, never vanishing.** A swimmer's take lays the shipped `RM_Filth_DisturbedSand` funnel
  at the end of a wake, plus a letter naming the victim. This is the Long Shade swimmer's-road
  shape, reused. A drag gets `RM_Filth_DragMark`.
- **Consumers, day one:**
  - `RM_Vekka`, `RM_Qorrax`, `RM_Drazzik` (it lies under already; the kit gives it a wake when it
    moves) and the fill-out's `RM_Duumma`, all RM tier;
  - `RSW_SandStalker` and `RSW_SarlaccSwimmer` (RSW);
  - the krayts (§2.5).

  Each consumer is one XML extension.
- **Sand fishing, wired here at last.** `fishTypes` on `RM_Stillsand` (RM tier) points at the
  catch family. The line and the wake meet: a sand-fishing pawn on deep sand is **drumming**. Each
  fishing session has a small chance to draw a stalker wake toward the fisher (the stalker's own
  description: *"it waits under a pool for the vibration of a dune crawler, or a boot"*). You fish
  with one ear on the rumble. ⚠️ Tier fix owed with it: the dune crawler and glass pearl are
  invented, so they move to `RM_` (Q11a), and the stalker stays wherever the owner rules.
- **The sound bed.** Layers 1–4 ride the shipped `RM_MapComponent_ProximitySoundscape` +
  `RM_ProximitySoundscapeExtension` (Greentide):
  - the hiss and saltation scale with `WindManager` speed;
  - the singing dunes are a one-shot fired from the dunes engine's transport batch, sampled to
    one or two per batch near the camera. This is a small hook in `MapComponent_DuneField`;
  - the bone harps are a sustainer on each skeleton building, louder in a gale.

  Audio assets follow the placeholder-grain convention. LEVIATHANS' `SandWorm_LeviathanRockMove` /
  `RockCharge` may be used as a **prototyping stand-in only** (MayRequire, never shipped as a
  dependency).
- **The geophone (the review's discoverable tech, kept).** It becomes the lens chain's first
  instrument (§2.4): a biosilica resonator staked in the sand that turns rumbles within its radius
  into coarse direction-and-size markers. It still cannot tell a drazzik's lie from a real drum.

**Reuses:** HediffComp_Invisibility (vanilla), ProximitySoundscape (Greentide), DrumLure, the
kill-sign filths, `RM_DeepSand`, SWBestiary's catch family, and the dunes engine's batch loop.
**Build:** the sand-swim kit is **medium C#** (comp + hediff + filth + surfacing rules, about
400 lines); the sound bed and fishing are **XML** plus one small hook; the geophone is **small
C#**. **Tier:** the kit, bed and fishing are RM; the canon consumers are RSW.
**Admission test:** it adds no residents. The wake is a line, the swimmers are buried, and the
sound adds no pixels.

### 2.2 The dune gale (renamed from Stillstorm)

**The one weather that is this biome's own.** It is rare (a few a year) and long (one to two
days), and it is what the dunes engine was built for.

**What the player sees.**
- **The herald:** the horizon on the windward bearing turns ochre, and dust sheets start to lift
  off every crest at once.
- **The gale:** the sky goes brown-gold and dim, sight shortens, and **the dunes march in hours**.
  Drifts climb your windward walls, a crest crosses the colony yard, your stockpile vanishes under
  sand and a caravan you have never seen before surfaces out of the next dune.
- **The aftermath:** a map you do not recognise. Every track is wiped (§3), and **one emergence**
  stands where nothing was.

**What the player hears.** The hiss becomes a roar (layer 1 swells), the singing dunes boom
everywhere at once, the bone harps howl, and **the rumble layer is drowned**.

**What the player feels.** A real choice, because the gale is dangerous and also the best time to
move:
- **The gale takes the sun off you.** The dim sky lowers sun exposure to near zero (§2.7). This is
  the one natural relief from the heat in a biome without night.
- **The gale blinds the swimmers.** Their appraisal is by vibration, and the storm is all
  vibration, so swimmers stay down and strike rates collapse.
- **But the gale hurts.** Exposed pawns take a slow abrasion, and light pawns and animals get
  **carried**.

A player who learns this crosses the Stillsand *in* the gale. The review's "the one time the giant
stops" is kept: the oommok hunkers, and its shadow stops moving.

**The mechanism.**

| piece | how | size |
|---|---|---|
| `RM_DuneGale` WeatherDef (+ a GameConditionDef for the duration) | sky colours in the sheet's palette (bleached ochre to dim gold, black shadow kept), `windSpeedFactor` high, accuracy and move penalties. LEVIATHANS' "abnormal sandstorm" is a colour reference only | XML |
| dunes march | the dunes engine **already supports** a per-weather override through `DuneFieldExtension` (the design's `stormTransportFactor`, with a violent-storm modExtension). The gale sets it to about 20× and raises `influxPerDay`, and the mass cap stays binding | XML |
| sun off | the gale's sky state feeds `RM_SunHeatExtension` as an exposure multiplier (about 0.2) | small C# |
| abrasion | exposed outdoor pawns get a slow scratch-damage tick (a vanilla `HediffGiver`-style condition worker). Thin roofs and walls under a mass threshold take structural damage | small C# |
| carry | a pawn or animal under a body-size threshold, in the open and on a crest, can be **dragged** 3–10 cells downwind. It lands bruised and leaves an `RM_Filth_DragMark` line. A pawn carried off the map edge gets a letter naming them and the bearing, and it **comes back**: the next gale or dune pass drops the body, or the living pawn as a wanderer, somewhere downwind. Never a silent loss | small C# |
| emergence | at gale end, **one** reveal is chosen and placed with `BuryThingsAt` in reverse (the cache's contents at depth 0 near a fresh erosion face): a mummified caravan, a hull, a sealed Jawa cache, a giant skeleton (§3), or a **cave mouth** in the nearest rock (§2.6, the sheet's *"uncovering new rock, a cavern mouth, a ruin, or something older"*). A letter says what the wind uncovered | small C# |
| seeding | dormant siidda woken nearby, a glasscrust sheet, and an hourbloom if water is present (the shipped `RM_IncidentWorker_BloomBurst`) | XML |
| gale static *(new, §4)* | the dust carries charge. Turrets and droids suffer brief EMP-like stun ticks, so the droid crossing (§4) has its weather | small C# |

**Reuses:** the dunes engine (the gale is its showcase), BuryThingsAt, BloomBurst, dormancy
comps, the kill-sign filths, the heat extension. **Build:** medium overall (several small C#
pieces on an XML spine). **Tier:** RM. **Admission test:** it makes the map *emptier* and then
places exactly one thing. **Distinct from** the Leaning Scrub's gale, which is a calendar that
bends fire and plants: this is a single storm that digs and reburies. ⚠️ **Depends on** the dunes
engine being seen live (`MOVING_DUNES_BUILD_1`'s owed run sheet); the gale is the natural test
of it.

### 2.3 The Return — the ritual

**The Sun-Debt, given its place.** The built ideoligion says *"The sun lends and the sand
collects… We take back what was drawn."* Its holders live here, and the Return is how they pay.

**What the player sees.** A **debt stone** stands on open sand, in full sun, never in shade.
Believers carry water out to it in eggs, skins and still-flasks and pour it into the sand in a
line toward the star. Within hours the sand answers: a ring of pale rose-and-bone hourbloom opens
around the stone. It is the only time dead land flowers on command, and it is dust again in days.

**What the player hears.** The hiss, a low chant, the pour. Then, a day later, the faint crackle
of the bloom opening.

**What the player feels.** That water has a **ledger** here. Every drop you draw is noticed, and
the ritual is where you settle up.

**Robustified: the ledger is mechanical, not only flavour.**

- **The Debt (Utinni tier).** A colony counter of water **drawn** on Stillsand maps. It rises
  from every solar-still litre (§2.4), every canteen egg drunk, every duumma sac and every
  wringing. Sun-Debt believers feel it as a mood line that worsens as debt rises (*"We have taken
  too much"*), and the Deep Desert Tribes' goodwill follows it.
- **The sand collects.** Unpaid debt raises the weight of the Stillsand's own event incidents:
  the krayt, the busters and the muurrok (§2.5). The tribes say the krayt is the debt collector,
  and the storyteller agrees. **The ritual is a pressure valve on the biome's danger**, not a buff.
- **The Return (Ideology `RitualDef` on the Sun-Debt).**
  - **Trigger:** event-driven, never by clock (ban: no circadian anything). It opens after a
    dune gale, after a krayt kill, or when debt passes a threshold.
  - **Cost:** a real quantity of water, which is the one thing the biome lacks.
  - **Outcomes by quality:**
    - the bloom at the stone (shipped `RM_IncidentWorker_BloomBurst`);
    - debt reduced;
    - on a great outcome, **the sand gives back**: the dunes engine reveals one buried cache near
      the stone;
    - on a bad one, the pour wakes what sleeps: a siidda or zuurrik bloom, which the tribes read
      as a debt refused.
- **The sign that stays.** The pour leaves a darker "Return line" terrain stain on the sand that
  lasts until the next gale. Returns you made are readable on the map, and old tribal debt
  stones, found in caves (§2.6), have lines worn into the rock.
- **RM tier, no theology.** Water poured onto Stillsand sand blooms (the physics stands alone),
  and the "sand remembers water" rule simply makes wet sand attract swimmers for a while (the
  rumble comes to the pour). No debt meter.

**Reuses:** DeepDesertTribes' Sun-Debt ideo (built), BloomBurst + the ruled hourbloom plant defs,
the dunes engine's reveal, the dormancy comps, and the sarlacc's Sun-Debt stage labels
(Seeker / Debtor / Collector / Paid), which the Return's letters can speak in. **Build:** the
ritual is XML plus a small C# outcome worker; the debt counter plus incident weighting is small
C#; the RM bloom-on-pour is small C#. **Tier:** the ritual and debt are Utinni; bloom-on-pour is
RM. **Admission test:** a line of poured water, and a bloom that dies. The map ends no busier than
it began. **Distinct from** Sh'kaar (the evil sun, parked at the Long Shade): this god is
*owed*, not feared.

### 2.4 Sand → glass → lens → solar still and solar oven

pending

### 2.5 The krayt dragon and the other event creatures

pending

### 2.6 The rare rock, and the precious cave under almost every one

pending

### 2.7 The heat: trivial to catch, hard to escape

pending

## 3. Huge skeletons and barren tracks

pending

## 4. More ideas

pending

## 5. Recommended package, ranked

pending
