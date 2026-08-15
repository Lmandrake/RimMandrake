# hydrology_and_fire_ecology.md — where the water goes, and what burns

DECIDE owns this. **Owner's session, 2026-08-15.** This is a planetary-physics
document: it states how water moves on this world and what that does to the
living things. It exists because a single gameplay question — *why would anyone
land anywhere but the savanna?* — turned out to have a physical answer rather
than a balance answer.

Companion documents: `tidally_locked_world.md` (geography), `water_doctrine.md`
(water as the master resource), `desert_world_design.md` (risk/reward per
terrain), `setting_physics.md` (the laws of harm).

---

## The problem this solves

The biome roster runs a real-world wet→dry gradient, and **savanna sits at the
comfortable middle of it**: grass to burn, game to hunt, soil to farm, and none
of the desert's lethality. On a harsh planet that makes it the obvious landing
site every single time, which quietly deletes the consequential-landing design
that `desert_world_design.md` is built on.

**The fix is not a nerf.** Making savanna merely worse is a balance patch, and
players read balance patches as arbitrary. The fix is to give the savanna a
physical reason to be the most dangerous productive place on the planet — so the
player who lands there is *right* about the reward and *right* to be afraid.

⇒ **Savanna is the high-risk, high-reward tile.** Everything below is the
machinery that makes that true.

---

## R-H0 · The mountains are VOLCANIC, and there are many of them

**Owner's ruling, 2026-08-15, and it is causally first — everything below depends
on it.** The mountain ranges are highly volcanic. **That is why they exist.**

This answers a question the water cycle would otherwise beg. A dead world erodes
flat, and a flat world has no cold high ground, and no cold high ground means no
water anywhere. **Active volcanism is what keeps building peaks faster than this
climate can tear them down** — so the planet keeps its condensers, and therefore
keeps its water, and therefore keeps its life. The hydrology in R-H1 is downstream
of a geology that has not finished.

**And there should be MANY ranges, dotted with volcanoes.** Not one spine. The
deep desert is monotonous by design and monotony is the enemy of a world you have
to cross — ranges break it up, give the map a skyline, and put a reason to
navigate into every direction of travel.

**What volcanism pays for, beyond the peaks themselves:**

- 🔴 **It explains the nutrient load.** R-H2's overcharged seas need a mineral
  source, and "flash floods off raw volcanic rock" is exactly that source — fresh,
  unweathered, mineral-rich stone, delivered all at once. Volcanic soil is the
  most fertile on Earth for the same reason. **The gigantism traces back to the
  volcanoes.**
- **It explains the fires having somewhere to start** other than lightning alone.
- **It puts geothermal on the map** as a real, sited resource rather than a
  building you unlock — and gives `Primordial Geysers` a job on this world.
- **It fits what is already adopted.** `desert_world_design.md` §3B(5) already
  places **helixien gas pockets** on volcanic and deep-desert tiles, and §3B(6)
  puts Star Wars ore deposits on rocky tiles. Both now have a planetary reason
  rather than a placement rule.
- **It is a hazard tier the roster lacks.** Volcanic tiles are the one terrain
  that is dangerous without being *empty* — the opposite failure mode from deep
  desert.

⚠️ **The world is BUILT BY HAND — owner, 2026-08-15.** So this is a placement
instruction, not a generator constraint: **many ranges, dotted with volcanoes,
distributed to break the deep desert up rather than gathered into one spine.** A
world that comes out flat silently invalidates R-H1, R-H2 and the entire water
economy, and there is no patch for it afterwards. See "How this world gets made"
at the end of this document.

## R-H1 · The water cycle: it rains ONLY on the high peaks

**Owner's ruling, 2026-08-15.** There is no ordinary precipitation on this world.
Rain falls **only at the greatest altitudes** — the tallest mountaintops, which
are also the tiles a gravship cannot land on.

The cycle, start to finish:

1. **Condensation happens only where it is cold enough**, and on a tidally locked
   world baked by a fixed sun that means *height*, not latitude. The peaks are the
   only cold surface in the habitable band.
2. **The water comes down violently** — steaming, near-boiling, carrying the
   mountain with it. Not rivers in the gentle sense. Floods with a schedule.
3. **Where it lands it makes brief wetlands, jungle and river** — a narrow, fierce,
   temporary green.
4. **It pools into small seas that are always on the edge of failing.** They
   evaporate under a sun that never sets.

⇒ **Every drop of fresh water on this planet is stolen from a mountain.** That is
why the Empire holds high ground, why the Hutts sit *beside* the oasis and never
on it, and why a water bottle is currency.

🔴 **Design consequence, and it is large: rain must be removed from the weather
tables of essentially every biome.** A biome whose `baseWeatherCommonalities`
include ordinary rain is contradicting the planet. The exceptions are the peaks
and the river margin. See "What this makes buildable" below.

## R-H2 · The seas are impossibly salty, and violently alive

Because the seas are fed by flash floods off raw mountain rock and then boiled
down by a sun that never sets, they concentrate twice over:

- **Salinity far past anything Earth offers.** Comparatively unnatural — this is
  not the Dead Sea, it is what the Dead Sea becomes.
- **Nutrient load to match.** The floods strip minerals off the peaks and deliver
  them all at once, and evaporation concentrates what the water leaves behind.

⇒ **The result is not a dead sea but an overcharged one.** Biology in and around
the water runs hot: algal blooms, explosive growth, and — the payoff —
**animals that grow very large**. Gigantism on this world is not a fantasy
conceit, it is a nutrient budget.

This retro-fits the existing fauna decisions rather than contradicting them:
`fauna_placement.md` already puts ten creatures on the water margin because the
owner wanted the wet edge to look inhabited. **Now there is a reason it is
inhabited by big things.**

⚠️ Salinity is also why the water is *not* a free win — see `water_doctrine.md`
ruling 3, most desert water is saline or contaminated. The sea is food and mass,
not drink.

## R-H2b · The poison forest grows on the terminator, and it is the SECOND water

**Owner's ruling, 2026-08-15.** The poison forest is not scattered. It grows in a
band on the **shade side of the terminator** — the twilight seam where the
dayside's dwindling desert air meets the eternal dark of the nightside.

**This is the only other place on the planet where water leaves the air**, and it
does it differently from the peaks: not rain, but **condensation** — fog, dew,
frost at the cold edge. Air that has crossed a scorched dayside carrying almost
nothing finally gives that nothing up when it hits the dark.

⇒ **Two water mechanisms, and they produce opposite ecologies.** The peaks deliver
water violently and all at once, and the result is the overcharged sea of R-H2 —
big, fast, fat. The terminator delivers water constantly and in trace amounts,
and the result is the reverse: **weird, stunted, struggling growth.** Nothing on
the terminator is large. Everything on it is persistent.

**Why it is poisonous follows from the same physics.** Condensation deposits what
the air was carrying — dayside dust, salt, whatever the fires put up. Nothing
washes it away, because it never rains there. **The forest concentrates the
planet's airborne filth in its own tissue** over a very long time, because
nothing on the terminator grows fast enough to dilute it.

⚠️ **This is the one place the freakish-growth planetary fact does NOT apply**, and
that exception is what makes the biome legible: everywhere else on this world
grows too fast, and here alone growth has stalled. Do not let a global growth
multiplier flatten it — the terminator's stunting has to survive the lever.

⇒ It also gives the nightside a doorway. `fauna_placement.md` already confines the
18 cold-named creatures to the frozen nightside; the poison forest is the
**threshold** between that roster and the dayside one, and creatures that belong
to neither list belong here.

## R-H3 · The plants grow freakishly fast — already decided, now it has a cost

The planetary fact was already settled: **all plants grow at a rate that reads as
obtrusive, aggressive, wrong.** Vegetation is meant to feel powerful.

In a jungle that is atmosphere. **In a grassland it is fuel**, and this is the
hinge of the whole document:

```
freakish growth  ->  standing dry grass, constantly renewed
no rain          ->  it never gets wet
lightning        ->  it lights
fire             ->  more lightning
```

## R-H4 · Fire makes its own weather, and on this world that weather is DRY

Large fires generate their own convection. On Earth that can produce
pyrocumulonimbus and, sometimes, rain that ends the fire.

**Here it never rains.** The convection column still forms, still charges, still
discharges — and delivers **dry thunderstorms**: lightning with no water behind
it, striking ground that has just been pre-heated and surrounded by grass that
regrows freakishly fast.

⇒ **The fire lights the storm, and the storm lights the fire.** The savanna does
not burn once. It runs a standing burn that migrates across itself forever.

**This is the single best mechanical idea in this document**, because RimWorld
already ships dry thunderstorms, lightning strikes, and fire spread. The loop is
not something we simulate — it is something we *allow* by writing the weather
table honestly.

## R-H5 · The savanna's reward, stated plainly

A place is only high-risk-high-reward if the reward is real. The savanna offers,
and should visibly offer:

- **Ash fertility.** Burnt ground is the richest soil on the planet, briefly.
  Farming in the burn scar is genuinely excellent — until the front comes back.
- **Standing biomass.** Fast growth means harvestable plant matter at a rate no
  desert tile can approach.
- **Game.** Grazers follow the regrowth, and the nutrient economy of R-H2 means
  they are worth killing.
- **Open ground.** Easy to build on, easy to see across — and easy to be caught on.

⇒ The bargain: **the most productive soil on the planet, on a tile that will
eventually burn, on a schedule you do not control.**

---

## Who survives a savanna like this — four faction answers

A fire ecology this violent is a filter, and **the way a faction answers it should
be legible from its settlements.** Four strategies, and they are mutually
exclusive enough to characterise four different peoples:

| strategy | who it suits | what it looks like on the map |
|---|---|---|
| **① Burrow — let it pass overhead** | An insectile or subterranean people. Fire moves fast and shallow; a hive two metres down does not care | Surface entrances only. Nothing above ground worth losing. Fits the Geonosian-analogue foundry hive already in the roster |
| **② Move — never be where it is** | Nomads who follow the burn line. The ash is fertile and the front is predictable to those who read it | No permanent structures at all. Camps in the scar *behind* the fire, which is the safest ground on the planet for exactly one season. This is the Tusken answer, and it makes their nomadism a competence rather than a poverty |
| **③ Burn it first — farm the fire** | The most interesting answer. A faction that sets fires deliberately, on their schedule, to control when and where the front arrives and to harvest the regrowth | Blackened bands around green fields. They are not victims of the fire, they are its farmers — and they will treat an unplanned burn as an act of war |
| **④ Wall it out — pay industrially** | The Empire. Firebreaks, cleared ground, ceramite, suppression | Settlements ringed by wide sterile scars visible from orbit. Expensive, ugly, and a statement: *we do not adapt to this world, we exclude it.* |

🔴 **③ is the one to build.** A fire-setting faction is not in the roster and it
would be the most distinctive thing on the map — it explains the burn pattern,
gives the player a reason the savanna looks *managed* in places, and creates an
obvious flashpoint the moment the player's own farm sits downwind. Recorded here
as a proposal; the roster decision belongs with `FACTION_SPEC.md`.

⚠️ **The Jawa themselves are ①-and-②** — a sandcrawler is a wall that moves, and
that is the whole point of a gravship on this world.

---

## What this makes buildable

Stated so the design does not stay prose. None of this is scheduled here.

- **Strip ordinary rain from the weather tables** of every biome except the peaks
  and the river margin. `BiomeDef/baseWeatherCommonalities` — see the review sheet
  from `src/RimMandrake/Utils/biome_review.py` for the current values, which show
  the top three weathers per biome.
- **Raise dry-thunderstorm commonality hard in the savanna**, and raise it further
  in whatever "burnt" variant we end up with.
- **Fast plant growth is a global multiplier**, not a per-plant edit — one lever,
  applied once, per the planetary fact.
- **Ash fertility** wants a terrain: burnt ground that is temporarily richer than
  anything else. Check what the biome mods already ship before authoring one.
- **The peaks are unlandable and that is the point** — do not "fix" it.
- **Large fauna belong to the water margin**, per R-H2 and `fauna_placement.md`.

⚠️ **Order matters.** All of this is chain step 2 (normalize) and step 8 (biomes),
and step 8 is already ratified. Reopening it needs a ruling, not a patch.

---

## Naming

### 🔴 The savanna is `The Pyrelands` — OWNER'S RULING, 2026-08-15

Chosen from the candidates below. *Burning savanna* survives as the common name;
**the Pyrelands** is what the world is called. It reads grand, funereal and
faintly religious — which is the right register for a place that burns forever
and that at least one faction will end up worshipping.

### The savanna — the candidates it was chosen from

| name | what it leans on |
|---|---|
| **The Burning Savanna** | the owner's own, and the plainest. Hard to beat |
| **The Tinder Veldt** | "veldt" carries grassland without Earth's Africa; tinder says the state it is always in |
| **The Ashfall Steppe** | names the aftermath rather than the event |
| **The Emberplain** | one word, and it implies it never fully goes out |
| **The Pyrelands** | grand, funereal, faintly religious — good if a faction worships the fire |
| **The Thunder Veldt** | names the *storm* instead of the fire, which is the more unusual half |
| **The Quickgrass** | names the growth, not the burning. The quiet menace of a place that grows too fast |
| **The Kindling Reach** | "reach" gives it scale; "kindling" says what the grass is for |
| **The Scorchgrass Sea** | grassland-as-ocean, which suits a tile you cross rather than hold |
| **The Cinderveldt** | contraction of the two strongest halves; reads as a proper place-name |

*(Superseded by the ruling above. Kept so the shortlist is not re-derived.)*

### The planet

| name | why |
|---|---|
| **Kholvast** | hard consonants, vast in the mouth. Reads industrial and Imperial |
| **Ashkarr** | says what it is, twice over, without being English |
| **Vessara** | softer, older — sounds like a name the planet had before anyone burned it |
| **Sekkoth** | dry, hissing; pairs well with Jawa phonetics |
| **Thal Ain** | two-part names read as *inhabited*. "The Ain" as a shortening |
| **Morrovar** | sombre; the *mor-* root does a lot of work |
| **Ilmarra** | vowel-rich, Outer Rim standard — the sort of name a trade lane uses |
| **Kravass** | brutal and short, like the tile roster it names |
| **Ojhad** | reads as a local name rather than a survey designation |
| **Sundering** *(or* **Sunder** *)* | the only English option; names the tidal lock itself — a world split in three |

**Recommendation: `Sekkoth`** — it is pronounceable, it is not English, it shares
its phonetics with the Jawa naming already in `jawa_crew_personas.md` (Sekki
Vosh, Yeku, Nkik), and it sounds like somewhere people live rather than somewhere
a probe once visited.

⚠️ Both recommendations are DECIDE's opinion, not rulings. The owner names the
world.

---

## R-H6 · The nightside is a DECAY GRADIENT, not a biome

**Owner's ruling, 2026-08-15.** Past the terminator the world does not simply get
dark and stop. It runs a **spatial sequence of decay biomes**, each further into
the lightlessness than the last, and the sequence *fades* rather than ending at a
border:

| distance past the terminator | biome | character |
|---|---|---|
| the seam itself | **poison forest** (R-H2b) | stunted, persistent, toxin-concentrating |
| deeper | **mycotic jungle** | fungal, lightless, feeding on what the seam drops |
| deeper still, in **patches only** | **gelatinous superorganism** | the end state — not plants any more |
| **well past** it, in the deep cold | **propane lakes** (R-H6b) · **crystalline caverns** · **glowing landscapes** (R-H6c) | not life at all — the exhaust, condensed; and the last light on the planet |
| **the end of the world** | **the forsaken crags** (R-H6d) | total darkness. A different chemistry, and it does not want us |

**What unifies them is decomposition, not darkness.** Each of these biomes speaks
of decay, of limited-but-available moisture, and of **extremely rapid
breakdown** — the counterpart to the dayside's freakish growth. On the lit side
matter is assembled obscenely fast; on the dark side it is taken apart just as
fast. Same planetary metabolism, opposite sign.

🔴 **The gelatinous superorganism is PATCHES, never a band.** A few of them,
scattered. It is the strangest thing on the map and rarity is what keeps it
strange; a continuous belt of it would read as terrain rather than as a horror.

⚠️ **Both are downstream of the terminator's water, not of rain.** The moisture is
the same trace condensation that feeds the poison forest, thinning as the air
gives up the last of it — which is why the gradient *fades spatially* instead of
ending. Nothing here is fed by a river.

## R-H6b · The propane lakes are the nightside's CONDENSER — a third water cycle

**Owner's ruling, 2026-08-15.** The propane lakes sit **well past the terminator,
deep in the eternal night**, where the temperature drops precipitously.

**They are the decay gradient's exhaust, condensed.** The fungal biomes of R-H6
break matter down extremely fast and anaerobically, and what that produces is
**volatile hydrocarbons** — outgassed continuously, drifting into the dark
because there is nowhere else for them to go. Out there it is cold enough that
they stop being gas.

⇒ **This planet has THREE condensers, and that is the whole of its chemistry:**

| where | what condenses | what it makes |
|---|---|---|
| **the high peaks** (R-H1) | water, violently | floods, rivers, the hypersaline seas — and gigantism |
| **the terminator seam** (R-H2b) | water, as a trace | the stunted poison forest |
| **the deep night** (R-H6b) | **hydrocarbons** | the propane lakes |

**It is also physically honest**, which is why it is worth keeping exactly as
stated: propane liquefies around −42 °C, and the active planet curve already runs
to **−70 °C at latitude 1.3 and −80 °C in deep night**
(`tidally_locked_world.md`). The lakes do not need special pleading. **The world
is simply cold enough**, and the fungal biomes upwind are simply productive
enough.

🔴 **And it makes the nightside the Pyrelands' mirror.** The savanna is
high-risk/high-reward because it is fertile and it burns. The propane lakes are
high-risk/high-reward because they are **a fuel field the size of a sea** in a
place that will kill an unprepared expedition through temperature alone. Two
opposite poles of the same design, at opposite ends of the same world — one where
the danger is fire, one where the fuel *is* the danger.

⚠️ **Standing next to a lake of liquid propane with an ignition source is a story
that tells itself.** Do not over-author it; the player will find it.

⚠️ **See "The hydrocarbon reconciliation" below** — the tar pits of R-H9 made this
a three-way problem rather than a two-way one.

## R-H9 · The tar pits are what the Pyrelands leave behind

**Owner's ruling, 2026-08-15.** The tar pits lie **past the Pyrelands, where the
desert finally takes over** — and are **interspersed with them** at the margin
rather than starting at a clean border.

**The mechanism, and it is the best thing about them:** the burning savanna
produces ash without end. The rivers of R-H1 flood it, frequently and violently.
Over eons that churn — ash, water, ash, water — compresses and transforms into
**gooey, thick, biologically rich tar.**

⇒ 🔴 **The Pyrelands manufacture their own margin.** The fire is not just a hazard
the player survives; given geological time it is a *process with a product*, and
the tar pits are the receipt. Nothing else on this world so plainly says *this has
been burning for a very long time*.

**Three things fall out of that, all free:**

- **Tar preserves.** A tar pit is a trap that keeps what it catches, and on a
  planet whose animals grow very large (R-H2) what it has caught is **enormous**.
  Bones, whole carcasses, and — the part that matters to this campaign — **things
  that are not bones.** A scavenger clan digging intact machinery out of tar is
  the single most on-theme activity available to a Jawa, and it needs no mechanic
  we do not already have.
- **It is a slow hazard, not a fast one.** Deep desert kills by absence and the
  Pyrelands kill by fire; tar kills by holding onto you. That is a third failure
  mode, and the roster is short of hazards that are dangerous without being empty.
- **"Biologically rich" is a resource claim**, and it should be honoured — this is
  organic matter concentrated over geological time, not sludge.

⚠️ **Placement note: interspersed, not banded.** The owner said past the savanna
*or* interspersed with it, and interspersed is the stronger read — a hard border
would imply a process with an edge, and this one does not have one. Pits inside
the burning grassland are older ground that has already been through the cycle.

## 🔴 MANY PATHS TO FUEL — owner's ruling, 2026-08-15

Three separate hydrocarbon sources are now on this planet, each ruled in a
different session for a different reason:

| source | where | reached by | ruling |
|---|---|---|---|
| **helixien gas pockets** | volcanic and deep-desert tiles | holding a hazardous tile | `desert_world_design.md` §3B(5) |
| **propane lakes** | deep night, past the terminator | a lethal cold expedition | R-H6b |
| **tar pits** | the Pyrelands margin | working beside the fire | R-H9 |

**The owner's ruling reframes this, and the reframing is important: redundancy is
the REQUIREMENT, not the problem.** The instinct to collapse three sources into
one "winner" is ordinary resource-design reflex, and here it is actively wrong.

⇒ **This is a gravship campaign. If fuel has a single source, the ship starves —
and a starved ship ends the campaign**, because the whole arc is *keep moving*.
A player cut off from the one fuel path is not facing a setback, they are facing a
dead save. **Every additional path is insurance against that.**

**So the design question is not "which of the three wins".** It is:

- **All three must stay viable.** None may be balanced into irrelevance, because
  each is somebody's only option at some point in the campaign.
- **They should differ in ACCESS COST, not in yield.** A volcanic tile you must
  hold, a cold expedition you must survive, a hazard field beside the best
  farmland on the planet — three prices for the same commodity, so the player
  chooses by circumstance rather than by arithmetic.
- **Each should be reachable from a different kind of situation** — dug in, on the
  move, or desperate.

⚠️ **Values still get set once, together** — the reason is now the opposite of what
it was. Not to pick a winner, but to make sure none of them is accidentally so bad
that it stops counting as a path.

## R-H6c · Crystalline caverns, and landscapes that make their own light

**Owner's ruling, 2026-08-15.** Out on the dark side, past the fungal biomes and
alongside the propane lakes, are **crystalline caverns** — and with them
**glowing landscapes that generate their own meagre light in the eternal night.**

**Meagre is the operative word.** This is not a lit place. It is a place with
*enough* light to move by and no more, which is a far stranger thing to walk into
than either full dark or full day. Everything the player sees out here, they see
because the ground is doing it.

⇒ **This is the last light on the planet**, and its position in the sequence is
what gives it meaning: it comes *after* the decay biomes and *before* the dark.
The glow is the final thing that pushes back, and past it nothing does.

**Two payoffs worth protecting:**

- **The crystal is a reason to come out here** that is not fuel. The propane lakes
  give the deep night an industrial purpose; the caverns give it a *prospecting*
  one, and those attract different play.
- **Bioluminescence and mineral glow read completely differently.** If the glow is
  alive it belongs to the decay gradient; if it is mineral it belongs to the
  crags. Deciding which is worth doing deliberately — DECIDE owes it, and either
  answer is good.

## R-H6d · The forsaken crags — the conjugate of the deep desert

**Owner's ruling, 2026-08-15.** Past the last glow, **total and utter darkness
descends**: the forsaken crags. `AB_RockyCrags` (Alpha Biomes), which already
carries a **hard-coded 0.34 sun-glow multiplier and can never roll clear weather**
(`tidally_locked_world.md` §2).

🔴 **They are the exact conjugate of the deep desert**, and stating it that way is
the design:

| | **deep desert** — dayside terminus | **forsaken crags** — nightside terminus |
|---|---|---|
| what kills you | **absence.** No water, no shade, nothing there | **presence.** Something is there and it is hostile |
| the danger | emptiness | occupancy |
| the fear | you will run out | you are not alone, and you are not welcome |

**And the crags are oddly FULL of life** — built on an **entirely different
chemistry than ours**, and deeply hostile to our presence. Two consequences, both
ruled:

- 🔴 **Most creatures go manhunter on arrival onto the map.** Not provoked.
  Arrived.
- 🔴 **Nothing here is edible.** Not the animals, not the plants. Alien
  biochemistry is not food; it is at best inert and at worst poison.

⭐ **There is a vanilla field that delivers BOTH halves at once:
`BiomeDef.wildAnimalScariaChance`.** Scaria makes animals manhunt and makes their
corpses unusable — so one number produces "everything attacks you and you cannot
eat what you kill." Drive it high and the crags behave as ruled without a line of
C#. **Verify the exact behaviour before relying on it**, but this is the lever.

⇒ **The crags are therefore the one biome where the campaign's core loop fails.**
Everywhere else a Jawa can scavenge, hunt or trade. Here the food chain is not
merely poor, it is *not addressed to us*. That is what makes it the end of the
world rather than just a bad tile.

⚠️ **A temptation to leave alone.** The crags' description already says an ancient
race partly terraformed this world and left — the Forsakens — and R-H8 says the
strange biomes carry an ancient bioweapon's genetics. **Do not weld those two
together yet.** The crags read best as chemistry that was ALWAYS here and was
never ours; the terminator biomes read best as something that was *done* to
ordinary life. Two different alien facts are richer than one explained one, and
R-H8 already rules that the bioweapon's author stays unknown.

## R-H7 · The ocular forests — the mountains have their own horror

**Owner's ruling, 2026-08-15.** High on the mountains, in the valleys where R-H1's
near-perpetual rain actually falls, grow the **ocular forests**.

- They **drink the high rain** — they are the only large organisms with unlimited
  water on this planet, and it shows.
- They **excrete red-flowing water**: streams running out of the high valleys
  loaded with **reproductive spores and alien toxins**. Absolutely unsafe to drink.
- ⭐ **The toxins and spores volatilise out of the stream before it reaches the
  formal desert rivers.** By the time the water arrives in the lowlands it is
  potable again.

**That last point is the whole design, and it must not be lost.** It means the
rivers everyone drinks from *begin* as poison, and the planet detoxifies them by
accident, in transit. The player who follows a good river upstream far enough
finds it turning red — and finds out why nobody lives at the top.

**The flavour to hold on to:** *as though life's flesh invested this biome long
ago, and was released from the ordinary constraints of bodily boundaries that
everything else obeys.* These are not trees. They are one organism's tissue that
has forgotten where it is supposed to stop. **Rare and horrible.**

⇒ It also completes the water story. The peaks make the water (R-H1), the ocular
forests **poison** it, distance **cleans** it, the desert rivers **carry** it, and
the hypersaline seas **end** it (R-H2).

## R-H8 · The genetics are wrong on purpose — an ancient bioweapon, still under test

**Owner's ruling, 2026-08-15.** The biology of these biomes — the ocular forests,
the gelatinous superorganism, the mycotic jungle, the poison forest — is
**genetically bizarre in a way ordinary evolution does not explain.** It is the
residue of an **ancient deployed bioweapon**.

🔴 **And it is still a live testing ground for the `Ascendant Helix`**
(`Jawa_AscendantHelix`, `FACTION_SPEC.md` §9) — the gene-cult that "believes the
body is a rough draft and the species a project," which **does not raid, it
retrieves**, and whose standing pawn groups already include **Research caravan**,
**Retrieval raid**, **Acquisition team** and — the one that suddenly means
something — **Containment response**.

**This costs nothing and pays for a great deal.** No new faction, no new mechanic:

- It explains why an obscenely wealthy spacer gene-cult is on a dying desert
  world at all, which the faction spec never answered.
- Their settlement placement gains a rule: **near the strange biomes, not near the
  people.** Isolated and secure was already their brief.
- It makes every encounter with them legible. A Research caravan in the mycotic
  jungle is them *working*. A Containment response is something having got out.
- The player has a reason to go somewhere horrible other than curiosity.

⚠️ **Do not settle who deployed the weapon, or against whom.** An unanswered
question here is worth more than an answer, and the Ascendant Helix not knowing
either — only that the samples are extraordinary — is the better story.

---

## How this world gets made — hand-built, with one honest caveat

**Owner's ruling, 2026-08-15: the world is built BY HAND.** No generator will be
written. The constraint set — three thermal bands, a decay gradient that fades
spatially, volcanic ranges scattered rather than spined, rain only at altitude,
patches of one biome and bands of another — is too tangled to be worth permuting
as free variables, and the result has to be *judged*, not validated.

⚠️ **The one thing DECIDE would say against it, stated once and then dropped:**
this is not all-or-nothing, because `Alien Worlds - Tidally Locked`
(`7f.alienworlds.tidallylocked`, ACTIVE) already exposes most of the *physics* as
XML on a `PlanetTypeDef` — `avgTempByLatitudeCurve` for the day/night gradient,
**`rainfallCurves`** for R-H1, **`elevationRange`** for the mountain share of
R-H0, `biomes`/`biomeBlacklist` for what may appear at all, and `biomeConfigs`
with per-biome `scoreOffset` for pushing a biome toward a latitude band.

⇒ **The distinction worth keeping is zonation versus placement.** Zonation is the
part that must hold *everywhere* — and a human placing hundreds of tiles by hand
will drift, because consistency across a whole globe is exactly what people are
bad at. Placement — a few patches of gelatinous superorganism, one sea near a
pole, where the ocular valleys sit — is the part a generator cannot do well and a
person can do in minutes.

**So the cheap version of "otherwise" is: let the planet type carry the curves and
the mountain dial, and hand-place everything that is rare.** That is still a
hand-built world; it just does not ask the hand to enforce a gradient.

**If the owner declines this, nothing above changes** — every ruling in this
document is a placement instruction either way, and manual remains the ruling.
