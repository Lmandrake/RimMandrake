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

## Naming — candidates, not yet decided

### The savanna

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

**Recommendation: `The Cinderveldt`** as the biome's proper name, with *burning
savanna* surviving as what people call it. A world reads better when the formal
name and the common name differ.

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
