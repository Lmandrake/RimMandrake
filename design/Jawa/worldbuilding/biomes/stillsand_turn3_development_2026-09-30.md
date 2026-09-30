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

**What exists already (checked before inventing, per the standing rule).** I read the live def
dump (`measure`, 628 mods, captured 2026-09-26) and `src/`:

- **no glass material or stuff exists** anywhere in the stack;
- **no solar still or solar oven exists**. The stack's "solar" is all power: vanilla
  `SolarGenerator`, VFE's advanced solar, and panel variants;
- vanilla smelting is metal recycling (`ElectricSmelter`, `SmeltWeapon`…), not sand;
- the only water-from-air building is the canon **moisture vaporator** (`KotOR_MoistureVaporator_big`,
  absorbed into our Armoury, RSW). ⛔ The Leaning Scrub owns buildable moisture *farming*, so the
  still must not be a vaporator;
- the raw optics that do exist are **`RM_Biosilica`** (the nub's harvest, built with no use),
  **`RSW_GlassPearl`** (the sand-fishing prize, *"a lens that grew a skin"*), the fill-out's
  **glasscrust grit**, and the canon **`RSW_KraytPearl`**;
- **`RUT_GlassSea`** is an unplaced mutator of fused sand ("Solar output soars; so does
  exposure").

⇒ **The chain is new, and the biome already grows its bootstrap.**

**The chain, robustified: four stages, and the Stillsand grows its own first lens.**

| stage | what | input → output | why it is the Stillsand's |
|---|---|---|---|
| 0. **the bootstrap** | biosilica is a lens the ground grows for you. The **sun furnace** is a mirror-and-lens dish that focuses the fixed sun on a crucible. It is built with biosilica, so it needs **no fuel**, which matters because *"there is no fuel here"* (deep_desert §8) | biosilica + steel → sun furnace | the only way to smelt in a biome with nothing to burn is to use the sun |
| 1. **the fine sand** | the **sand sieve**, a staked screen built on `Sand`/`RM_DeepSand`, sifts the region's ultra-fine grain into **`RM_GlassSand`** over time, like a slow deep drill. ⚠️ It is a *harvested* item, NOT drift sand. The dunes engine's ruled "dig vanishes" stands; see the card below | terrain → glass sand | the owner's line: this sand is the finest on the planet |
| 2. **the glass** | at the sun furnace, glass sand melts to **`RM_SunGlass`**. A small stack is a clear, faintly gold, bubble-free material. **One stuff**, deliberately simple, because `DESIGN_MATERIALS_REVIEW_1` will normalize every material later: it gets one stat line and one market value and waits for that pass | glass sand → sun glass | eternal noon *is* the furnace: output scales with sun elevation (§2.7), so furnaces run hottest in the Dune Sea region and slower in the far ring. The gale stops them |
| 3. **the lens** | a **lens bench** (Crafting) grinds sun glass into **`RM_PrecisionLens`**. Premium lenses come from the grown optics: a glass pearl gives a *pearl lens*, and a krayt pearl gives a *krayt lens*, the apex (canon krayt pearls are focusing crystals) | sun glass → lens; pearl → pearl lens | the prize lenses come out of the sand-fishing line and the krayt kill, so the chain ties to §2.1 and §2.5 |

**What the lenses make: the owner's "high performance solar stills and ovens," plus the kit.**

- **The solar still.** A lens-and-glass condenser, glazed on top and black-bottomed, that
  distils water out of what the Stillsand does have:
  - **brine** from the cavern seeps (§2.6), the steady source that makes a precious cave a water
    source;
  - **wet organics**: fresh kills, drazzik and guzzka eggs, duumma sacs;
  - **the dead**, with a heavy mood penalty unless the colony holds the Sun-Debt, which calls it
    *drawing*.

  Output goes into FlowWorks' water liquid (the ruled LiquidDef registry) or DBH's water item,
  whichever the build finds live. Rate scales with sun elevation. **A pearl lens doubles it.**
  Every litre counts on the Debt (§2.3). ⚠️ Distinct from the vaporator (air) and the Cauldron's
  fluid conversion: this is distillation by lens, from matter.
- **The solar oven.** A glazed box on a mirror skirt that cooks meals with **no fuel and no
  power**, in full sun only. It stops in shade, in the gale, and (Long Shade trivia) at a lower
  sun. It is a stove for a biome with nothing to burn. **A reflector skirt of muurrok crest-plate
  (§2.5)** makes it a *high performance* oven: faster, and able to bake the sun furnace's glass.
- **What else the lens reaches** (each one line of XML once the lens exists):
  - the **geophone** (§2.1);
  - **sun goggles** (§4, the glare-blind counter);
  - a scope component for rifles;
  - the **ship lens array**, the Stillsand's row for `BIOME_SHIP_CONTRIBUTIONS_1` (review #2),
    which is the ship-contribution MISS answered.

**Solar power, answered (MEASURED via RimSage this turn).** Vanilla `CompPowerPlantSolar`
outputs `Lerp(0, max, map.skyManager.CurSkyGlow) × unroofed fraction`. It reads the **sky glow**,
not the clock. So once the Stillsand pins its sun (§2.7), glow is constant and **solar panels
run at 100% forever with zero patches**. The dune gale, which dims the sky, is then the only
thing that ever cuts the colony's power. That is one more reason the gale is an event.

**Card (his call, not assumed):** should shovelling drifted sand off your walls *also* yield glass
sand? It would tie the dunes engine straight into the chain (every drift is stock), but it
reverses the engine's ruled "dig vanishes." The recommendation is **no**: keep the sieve and leave
the ruling alone.

**Reuses:** `RM_Biosilica`, `RSW_GlassPearl`, `RSW_KraytPearl`, glasscrust grit, the heat
extension's sun elevation, FlowWorks liquids, and vanilla deep-drill and workbench shapes.
**Build:** the items, stuff, recipes, bench, sieve and oven are **XML**. The sun furnace and
still's elevation scaling and brine or organics input are **small C#**. The oven's "full sun
only" rule is a small C# power-trader-style check. **Tier:** RM. The pearl-lens and krayt-lens
recipes are RSW patches (their inputs are RSW). **Admission test:** the player's buildings are
compact (one furnace, one bench, a few stills), and nothing is added to the wild map.

### 2.5 The krayt dragon and the other event creatures

**The principle: in the Stillsand the big things are events, not residents.** Today the krayts
are wired as wild animals (0.15 and 0.001), so a krayt can stroll across the map on a quiet day.
That is both the wrong fantasy and the wrong law (giant *and* surface-visible *and* awake).

**Card: take both krayts to 0 in `WildAnimals_Stillsand.xml` and make them incident-only**, as the
sand busters already are. The war wyrm (0.2, canon, ruled a burrower) is the same question; the
recommendation is to do the same.

**The ladder, from most often to once a lifetime:**

| # | creature | tier | how it comes | what it does | the sign it leaves |
|---|---|---|---|---|---|
| 1 | **sand busters** (ruukka + oorrik) | RM | built: eruption under the colony | the planet's only infestation | eruption scar |
| 2 | **the krayt dragon attack** | RSW | incident, weighted up by the Debt (§2.3) and by vibration (drilling, a landing ship, the thumper §4) | see below | a wake trough, a breach crater, drag marks, and its corpse becomes a skeleton (§3) |
| 3 | **the muurrok**, the free tier's own leviathan (NEW, invented, `RM_`) | RM | incident; also the RM mod's answer when the RSW layer is absent, so the free mod still has a mighty event (Q11a: "the same, save for any Star Wars beasts") | see below | a funnel where the victim was, and its shed crest-plates |
| 4 | **the sarlacc swimmer comes to root** | RSW | built creature; a Stillsand incident: a swimmer whose birth-water is running out swims in toward the largest seep, meaning the precious cave (§2.6) | sweeps a lane with the sand-swim kit, then **roots** at the seep. The water in your cave becomes a mouth | letters naming the take, `RM_Filth_DisturbedSand`, and the anchored sarlacc itself |
| 5 | **the greater krayt: the den** | RSW | a **quest**: the Mandalorian beat. A greater krayt has denned in a rock cave (§2.6), and the Deep Desert Tribes and a Jawa crew ask for help | a set-piece hunt at the den: bait (a bantha or eopie), the drumming lure, charges in the tunnels. Canon behaviours: it swims the sand on ten legs and spits acid | the den, cleared, becomes a precious cave in its own right; the greater skull, the pearl, and a skeleton landmark |
| 6 | **the Long Hunger** | RUT (built, active, never live-fired) | its contract quest; v2 wires the **Groundcaller** into the thumper (§4) as the real vibration-accumulation summon | VAST-tier eruption, tremor pulses, submerge with salvage | the torn ridge; its salvage drop |

**The krayt attack, beat by beat:**

1. **The Listening warns first.** A rumble on the windward horizon grows over about a minute of
   game time. Piinnok lenses sink (if admitted). The geophone marks a *very large* size class. A
   letter says *"Something vast is moving under the sand."*
2. **The wake.** A raised ridge crosses the dunes toward whatever is making the most noise or
   carrying the most water (§4's appraisal): a caravan, a drilling rig, a herd.
3. **The breach.** The krayt surfaces with the breach sound, a dust column and a stagger ring, and
   **fights on the surface** (canon krayts are land-fighters once up). It is hard to kill: bs 12,
   health ×10, combatPower 750.
4. **The choice.** Kill it, or make it dive: hard ground, fire (deep_desert §8: *"fire causes
   rout"* and the tribes' treasure), or losing interest once it has fed. **If it feeds, it
   takes the prey down**: a drag mark into a disturbed-sand funnel, and a letter naming what was
   taken. Never a silent vanish.
5. **The payoff.** Meat, leather, the skull (`ProcessKraytDragonSkull` exists), the pearl (the
   apex lens, §2.4), and **a corpse that does not rot** (deep_desert: *"nothing rots"*). Over a
   season it becomes a **skeleton landmark** (§3), so your kills become the map's history.

**The krayt call (canon, a counter).** Obi-Wan's cry, which scared off the Tuskens: a craftable
**krayt horn** (RSW) plays `RSW_Pawn_KraytDragon_Call` (the SoundDef ships). It **routs** smaller
predators and tribal raiders, and **every blow risks an answer**: a small chance of queuing the
real attack. It is a great tool and a terrible habit.

**The muurrok, drafted fresh.** The name was swept this turn: 0 hits in src/design/infrastructure/
skills/research, 0 in the artpipe registry, 0 Wookieepedia (control `bantha` → Bantha),
`check_pseudo_sw_name.py` PASS. Spares, equally clean: *tuullik*, *kaaddok*, *haarrok*.
- **What it is.** A giant sub-sand swimmer, polarised on the sun axis like everything here. Its
  sun-face is a single **mirror crest** that breaks the surface when it cruises, so the only thing
  you ever see is **a line of glare moving across the dunes**, a blade of light cutting the
  corrugation.
- **How it hunts.** By the deep desert's own law: *surfacing spends water*, so it **appraises**.
  It circles a party at the edge of sight and takes **the wettest body**: the best-watered pawn,
  the fattest pack animal, a full water-carrier. Then it ignores everyone else. A party that
  learns this travels lean (§4).
- **Why it is not a krayt echo.** The krayt is a surface fighter that answers noise and water
  debt. The muurrok never fights on the surface: it strikes from under, one take, and is gone.
- **Def sketch.** bs about 14, commonality 0 (incident only). The sand-swim kit. A strike that
  downs and drags. Its corpse yields **crest-plate**, a mirror reflector material that feeds the
  high-performance solar oven (§2.4).

**Reuses:** the sand-swim kit (§2.1); the sand-buster incident shape
(`RM_IncidentWorker_SandBusterEruption` is the biome-gated incident precedent); the Sarlacc's
`RSW_SwimmerRoadExtension.biomes` pattern for gating by defName; the krayt SoundDefs and item
chain; the quest skills' vanilla-node shape (StrandedQuest, LongHunger). **Build:**

- the krayt and muurrok incidents: **small C#** each, on the kit;
- the sarlacc-roots incident: **small C#**;
- the greater-krayt den quest: **medium** (a QuestScriptDef plus a den set piece in §2.6's cave
  genstep);
- the krayt horn: **small**;
- the war wyrm and krayt commonality changes: **XML**.

**Tier:** krayt, greater krayt, horn, war wyrm and sarlacc are RSW/Utinni patches. The muurrok is
RM. The Long Hunger is RUT. **Admission test:** every one of them is **buried or dormant until it
arrives, giant when it does**, and leaves the map as empty as it found it, plus one skeleton.

### 2.6 The rare rock, and the precious cave under almost every one

**The law.** Rock is rare in the Stillsand, so when there is rock it is **the landmark of the
map**. Almost every outcrop hides a cave, and the cave holds something precious. It also answers
the question the review left open: **where do the Stillsand's caverns go?** Into the rock.
`STILLSAND_CAVERN_AUTHORING_1` is filed in the ledger with no item file, and this is its home.

**What the player sees.** Usually there is one outcrop on the whole map, and never more than a
few. Yardang-shaped: long, wind-carved and aligned to the one wind (deep_desert §9's owed "map
grain" lands here, on the rock). On landing, a letter names it and its bearing: *"A rock island
stands to the north-east."* Its **lee is the only real shade on the map** (under the low sun it
throws a long black shadow), so it is where the biome's fauna rest. **The cave mouth opens on the
shade face**, as everything here keeps its openings on the dark side (dune_sea §4). Inside, the
air is cool, the light is gone, and there is water.

**What the player hears.** The hiss drops away at the mouth. Inside is a drip, the one sound of
water in the biome. Deeper, sometimes, is something breathing.

**What the player feels.** Greed, and the knowledge that **the rock is also the best place to
live**. A thick natural roof is full relief from the sun (§2.7), and a brine seep feeds a still.
To settle it, you must take it from whatever already lives in it.

**The precious table (one per cave, weighted):**

| cave | what's inside | ties |
|---|---|---|
| **the seep cave** (most common) | a brine and mineral-salt seep (deep_desert §7's *"a chemistry input available nowhere else"*); a metres-wide cavern food web where things *"strike out of the water like traps"* | `STILLSAND_CAVERN_AUTHORING_1`; the solar still's steady input (§2.4) |
| **the guzzka lair** | the built `RM_Guzzka` (bs 5.5) on a clutch of `RM_GuzzkaEggFertilized`, *"the best drink of water a person could carry"* | **wires the built-but-nowhere guzzka at last** (`DESERT_CAVERN_BEAST_EGGS_1`) |
| **the lens grotto** | walls of grown biosilica, a geode of light-pipe glass where the light is piped *down*; the richest biosilica on the map | the lens chain's bootstrap (§2.4) |
| **the krayt den** | a greater krayt, or its old den with its skull and pearl | §2.5 #5's quest set piece |
| **the debt cave** | an old Sun-Debt shrine: a debt stone with Return lines worn into it (§2.3), a mummified priest, sealed water jars | the Return's first stone |
| **the sealed cache** | a Jawa or old-war cache: dry, pristine, sealed. The buried record in stone, not sand | marquee #3 |
| **the sarlacc seep** | an `RSW_DeepDesertSeep` marker, so this is where a swimmer will come to root (§2.5 #4) | Sarlacc build |
| **nothing, taken** (rare) | the cave was emptied. A tribal mark and a cold hearth say by whom | "almost always" means not always, and the empty one is a sign too |

**Two more cave sources, so "almost always" can be true on flat maps too:**
- **Sand caves (sinkholes).** Some caves are *under the sand*, not in rock. A glasscrust roof over
  a void collapses when a swimmer breaches, an eruption fires or a gale scours it, and **the
  ground opens** onto a pocket cave (§4). They are rarer, and a surprise.
- **Gale-uncovered mouths.** The dune gale's emergence can be a cave mouth in the nearest rock
  (§2.2).

**The mechanism.** A Stillsand `GenStep` runs after terrain. If the map has natural rock, it
takes the largest outcrop and carves one chamber off its **shade face** (the tile's sun bearing,
§2.7), sized to the rock. It rolls the table and places the set piece with the shipped
`RM_GenStep_PlacedSetPieces`. On rockless maps it can seat **one** small tor at low odds (the
"celebrated" rock: rare, never a range). Vanilla and Odyssey's `Caves` / `Cavern` /
`UndergroundCave` tile mutators exist in the dump and are evaluated first. The cavern terrain
(brine seep, permanently shaded floor, the mummified register) is `STILLSAND_CAVERN_AUTHORING_1`'s
own work, and this genstep is its placement.

**Reuses:** PlacedSetPieces, the tile mutators, the guzzka and its eggs, the seep marker, the
Sun-Debt, and the krayt items. **Build:** the genstep and table are **small C#** plus XML; the
cavern terrain and food web are **medium** (the cavern item's own scope); sinkholes are **small
C#**. **Tier:** the genstep, seep cave, guzzka, lens grotto and sealed cache are RM; the krayt den,
debt cave and sarlacc seep are RSW/Utinni entries added to the table by patch. **Admission test:**
**buried** (the whole thing is inside the rock) and **a line** (the yardang). The surface gains
nothing.

### 2.7 The heat: trivial to catch, hard to escape

**The sun angle, from the planet (the ruling worked through).** The shipped shade grid already
computes the sun per tile: bearing and arc from the map's tile to the substellar point, elevation
= 90° − arc (`RM_MapComponent_ShadeGrid.ResolveSun`). The ruling means **no region override**:
"the Dune Sea" never forces an overhead sun by name, and the tile's own arc decides. What follows:

1. **Pin the sky to it.** Add the shipped `RM_PinnedSunExtension` to `RM_Stillsand` with the
   elevation from the tile. The rendered shadows then equal the mechanical shade, and the
   day-night cycle ends. That fixes dune_sea §6's first ban, which is broken as shipped. It also
   gives solar 100% uptime for free (§2.4, measured). The palette is the sheet's: a bleached-white
   sky, black shadow, no penumbra.
2. **Lift the clamp.** `maxElevationDegrees` is 60 today, so even the substellar point gets a
   sun at 60°. Latitude-true means the Stillsand's extension allows about 85°. Near the
   substellar point, shadows shrink to almost nothing. The sheet's "shadeless" Dune Sea emerges
   from physics, not from a label.
3. **Let the heat kind follow the sun.** Protection is set per biome today (`lowSun`, only a lee
   helps), and a latitude-true sun makes that wrong at the top of the range: under a 75° sun, a
   roof *does* shade you. Proposal: a kind resolved from elevation. **Above about 55° the
   `overhead` rules apply** (roofs and parasols count, and lee shadows are short). **Below it,
   `lowSun`** (only a lee or rock counts). This is not a new *kind of heat*, which the owner
   ruled out. It is only which cover counts, and it is set by the sun's angle.
4. **Irradiance by angle.** The heat offset scales with sin(elevation): the substellar region
   roasts hardest, and the far ring a little less, with longer shadows to hide in.
5. **One bearing for everything.** The sun bearing, the lee direction, the dune crests and **the
   dunes engine's wind** all come from the same tile-to-substellar bearing. Pin the engine's wind
   to it (a `DuneFieldExtension` field, `lockBearingToSubstellar`, which is small C#), and the
   sheet's *"a wind that has never once changed its mind"* holds. The whole map becomes the compass
   the tribes navigate by. Reveals still happen, because a migrating dune uncovers what it passes
   over.

**Overheating made trivial and hard to avoid.** These are first values; the owner-watched sitting
tunes them.

| lever | today | proposed | effect |
|---|---|---|---|
| `heatOffsetC` | 35 | **55** × sin(elev) normalised (about 35 in the far ring, 55 at the substellar) | a colonist in the open is feeling heatstroke within the hour anywhere, and in minutes in the Dune Sea region |
| **sand glare** (NEW) | none | exposure on open **sand** cannot drop below **0.35**, even in cast shade: reflected light off the bright ground | a sun shield or a wall's lee on open sand **slows** you cooking; it does not stop it |
| gear | parasol `lowSunFactor` 0.3; shield works | unchanged | the shield is the only carried piece that helps, and only partly (glare) |
| `sunPathCostPerCell` | 20 | 20 | there is so little shade that routing cannot avoid the sun, which is honest |

**The player's real counters, all of which cost something:**

1. **Go into the rock.** A thick natural roof is full relief (`RM_SunHeatMath`: under lowSun,
   thick roof = cover 1). The precious cave (§2.6) is the Stillsand's true home, which is why it
   is contested.
2. **Enclose and cool.** An enclosed room has zero sun exposure, but the ambient air is still
   43–70 °C (sheet temperatures), so the room needs coolers, and the coolers need power. The solar
   panels run forever (§2.4), so the colony is a power plant keeping itself alive.
3. **Pave the lee.** Constructed floors do not glare. A **shade yard**, a paved lee behind a wall
   line, is the one outdoor space where shade fully works. It is a real base-layout decision,
   oriented by the one bearing.
4. **Drink the still.** A drink of still water gives a **cooling draught** hediff (vanilla stat
   offset: ComfyTemperatureMax +8 °C for about 6 h). Water fights the heat directly, and it adds
   to the Debt (§2.3) and makes you a better target (§4, appraisal). Every counter feeds a danger.
5. **Time it.** There is no night, so timing means *events*: move **in the dune gale** (sun near
   zero, swimmers blind, but abrasion and carry), move **in the oommok's moving shadow** (ruled
   marquee #2), or move in the shadow of your own landed ship.
6. **Send droids.** Machines do not heatstroke, and nothing under the sand hunts them (§4). The
   deep desert's campaign-defining line becomes the heat's best answer too.

**Reuses:** all of `SOLAR_HEAT_EXPOSURE_1` and `SHADE_GEAR_FAMILY_1` (built), `RM_PinnedSunExtension`
(built for the Long Shade), and the dunes engine's extension. **Build:** the pinned sun and
retune are **XML**; kind-from-elevation, sin(elev), sand glare and the wind lock are **small
C#**, four short additions to `RM_SunHeatMath` / `ResolveSun` / `DuneFieldExtension`, each
selftestable in the existing SelfTest; the draught hediff is **XML**. **Tier:** RM (CreatureBehaviors
kit + Stillsand def). **Admission test:** it adds nothing to the map, only teeth. ⚠️ **Echo, stated
plainly:** the pinned sun is the Long Shade's mechanism, used for the opposite sky, because the
sheet and the ruling both demand it.

## 3. Huge skeletons and barren tracks

pending

## 4. More ideas

pending

## 5. Recommended package, ranked

pending
