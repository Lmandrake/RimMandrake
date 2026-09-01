# What this project is

*A statement of the goal, the subject matter and the constraints. Deliberately says
nothing about how the work is organised, tooled or divided — that is the question this
document exists to be asked about, not something it should presuppose.*

Written 2026-08-21.

---

## 1. In one paragraph

A single person is hand-authoring one large, bespoke **RimWorld** campaign and shipping
it to other players as a finished artifact. It is simultaneously a **creative writing and
worldbuilding project** (a planet, thirteen factions, twelve religions, a cast of named
inhabitants, a tonal premise) and a **software project** (twenty-two mod folders, ~65,000
lines of game-definition XML, ~20,000 lines of C#, ~950 art assets, and a data pipeline
that stamps a hand-made planet into the game engine). The two halves are not separable:
almost every creative decision has to be expressed as data the game engine will accept,
and almost every technical constraint pushes back on the fiction.

## 2. The game, for someone who does not know it

**RimWorld** is a colony-simulation game. The player manages a handful of characters on a
procedurally generated planet, and an AI "storyteller" throws events at them. It is
extraordinarily moddable: nearly all content — creatures, items, weapons, factions,
biomes, religions, ideologies, quests — is declared in XML "definitions" (*defs*) that
mods add or patch, with C# and the Harmony library available for behaviour that data
cannot express.

Facts about the platform that shape everything here:

- **Mods are loaded once, at game start.** A load of the full mod list takes about
  **25 minutes**. Iterating therefore has a brutal cost unless you can answer a question
  without loading.
- **The active mod list is large: 578 mods.** Mod *count* is not itself a problem; what
  matters is whether a mod raises the player's power ceiling.
- **Several things are fixed permanently at world creation** and cannot be retrofitted —
  most importantly the set of factions that exist and the religions they hold. If
  something is absent at the moment the world is made, it is absent from every player's
  game forever.
- Definitions inherit and are patched across mods, and **a patch that matches nothing
  fails silently**. There is no compiler and no type checker; a mistake usually surfaces
  as content that quietly does not exist.

## 3. What the player actually receives

**A savegame.** Not a world seed, not a scenario the player runs, not a generator — a
fixed save file containing the finished planet, the starting map, the player's ship and
its crew, plus the mod list that save depends on. The player loads it and plays.

This is the single most consequential decision in the project, and it cascades:

- **Nothing is generated at the player's end.** There is exactly one planet, made by
  hand, once, and frozen.
- **There is no worldgen feature in any version of this project** — not deferred, not a
  "version 2" item. Automated or programmatic world generation is permanently out of
  scope. The world is authored the way a level designer authors a level.
- Consequently, **the act of creating the world is irreversible and happens once.**
  Everything that must be present at that moment has to be finished and correct
  beforehand.
- Correctness of the world is judged **visually first** — does it read as a photograph of
  a real planet? — rather than by any numeric score.

## 4. The creative premise

A clan of **Jawa scavengers** — small, hooded desert scavengers, in the Star Wars
tradition — have boarded and are repairing somebody else's crashed industrial
**gravship**. The ship carries a damaged but working production line, which is the
diegetic reason it was worth taking.

The campaign loop: land somewhere → pick objectives → make a temporary camp → explore and
scavenge → improve the ship → enemy pressure rises → **decide what to leave behind** →
launch → do it again somewhere else.

Design pillars: **mobility · scarcity · exploration · hard logistical choices.** The
permanent home is the ship; every planetary camp is disposable. Crew is small, around four
to eight.

There is a governing rule the whole design defends, worth stating because it is the thing
most mod content threatens: **the ship and its onboard factory are the only sanctioned
routes to growing more powerful.** Every other exponential progression the game offers —
psychic powers, genetic engineering, robot armies, escalating royal titles — is
deliberately switched off as a player system. Enemy threat is meant to escalate in
*capability and character*, never in raw numbers.

Tonal reference points the author has named: *Firefly*, *Battlestar Galactica*, the
Oregon Trail, and a scientific expedition crossing an unmapped world.

## 5. The planet

**Ash'karr, "The Sundered"** — a **tidally locked** desert world. One face permanently
faces its star, one face never does. This is not a stylistic label; it is the organising
physical fact, and temperature is driven by angular distance from the hot point rather
than by latitude:

| | |
|---|---|
| substellar (hot) point | **+70 °C** |
| the terminator — the ring of permanent twilight | **+14 °C** |
| antistellar (dark) point | **−80 °C** |

Life is therefore concentrated in a **habitable ring** around the terminator. Surface
water is **8.14 %** — 1,780 of **21,872** tiles — in exactly three bodies: **The Scald**
(a raised crater lake), **The Twilight Sea** and **The Grey Sea**. A fourth basin, **The
Umbra Trap**, holds ammonia rather than water.

Around two dozen named regions carry the fiction: The Anvil · The Dune Sea · **The Rust
Cathedral** (machine-held, permanently hostile) · The Scorch · The Pyrelands · The
Nightspill · The Sunreach · The Ash Verge · The Long Dark · The Umbra · The Ammonia Flats
· The Salt Gate. Mountain ranges, likewise: The Scald Spine, The Ashteeth, The Fall Line,
The Dew Horn, The Ashfall Range.

Terrain is designed on a deliberate four-axis schema — **abundant / scarce / exotic /
threat** — so that **no location is self-sufficient.** The campaign only functions if the
player keeps moving. **Water is the master resource:** a tile with no water cannot be
camped at all, which turns the water supply into the timer that forces the next launch.

## 6. The inhabitants

**Thirteen factions**, of which eight are authored from scratch and five are existing
factions reskinned: the Hutt Cartel · Free Droid Enclaves · Wildsteam Clan · Deepwater
Compact · Geonosian Foundry Hive · Ascendant Helix · Jawa Trade Moot · the Junkers ·
the **Galactic Empire** (the single escalating military pursuer) · Homestead Defense
League · Deep Desert Tribes · Blackstar Company (pirates) · the Forgotten Arsenal
(machines, hidden, no settlements). Twelve of them hold territory: **72 settlements**
placed on the map.

**Twelve distinct religions** are authored, one per culture, and they are meant to
*disagree with each other about the same world* — water politics, debt, machine
personhood, genetic ascent. The player's own faith, **The Salvation**, is a secular
animist scrapper culture built on scavenging, trade and nomadism — explicitly *not* a
mystical Force faith.

Slavery is present and deliberately morally uncomfortable rather than absent: the Jawa
*trade* slaves, the Hutts *keep* them, and the design separates the two without making
either admirable.

A further ambition, partly built: making the world's locations **somebody's home rather
than scenery** — persistent named inhabitants with routes, fates and histories, including
a decay parameter that turns any settlement archetype into its ruined variant.

## 7. Scale of the material

| | |
|---|---|
| Mod folders authored | **22** |
| Game-definition XML | ~145 files, **~65,000 lines** |
| C# | 51 files, **~19,800 lines**, four shipped assemblies plus authoring tools |
| Art | **~950** PNG assets |
| The planet, as data | **21,872** tiles, plus rivers, roads, settlements, landmarks |
| Design and worldbuilding documents | **~123** in the design tier (~795 markdown files repo-wide), ~30,000 lines |
| Largest single documents | a 1,863-line deferred-ideas file; a 2,785-line faction roster |
| Authored creature/character definitions | 152 character types, 71 sub-species, 118 genes |

A separate arbitration file — around 900 lines — exists purely to hold **one authoritative
value for every number the documents have ever disagreed about.** Its existence is itself
a fact about the project: the material is large enough that different documents drifted
apart, and drift had to be actively fought.

## 8. What is done and what is not

**Settled:** the planet's shape — terrain, climate, water, biomes, the 72 settlements, the
named regions. The ship itself, built and exported. Item curation (roughly 1,300
keep-or-cut judgements). Weapons and gear. Terrain overrides. The player's religion and
sub-species.

**Outstanding:** normalising equipment and giving every character type something
appropriate to carry; the droid characters; converting eleven written religions into game
data; the scenario definition; populating the world with landmarks and named inhabitants;
and finally the **single irreversible act of creating the world** and saving it.

A bestiary of **108 creatures is written and none is built** — currently marked
aspirational rather than committed.

## 9. The constraints that bite

1. **One irreversible shot at world creation**, with faction and religion data required to
   be complete and correct beforehand.
2. **~25 minutes to test anything** that genuinely requires the full game to load.
3. **No compiler.** Errors in game data usually manifest as silent absence, not as a
   failure message.
4. **Large surface area, single author.** Roughly 800 documents and 85,000 lines of code
   and data, all of which must stay consistent with each other and with decisions the
   author makes conversationally as he goes.
5. **Decisions are made verbally, continuously, and must propagate.** The author
   frequently rules on something in passing — keep this mod, cut that faction, freeze this
   file — and every document and work item that assumed otherwise must be brought into
   line, or the project will act on a belief he has already overturned.
6. **Realism is judged by eye, not by metric.** There is no test that can tell you the
   planet looks right.

## 10. What "done" means

The author can hand another person a savegame and a mod list; that person loads it and
plays a coherent, hand-made campaign on Ash'karr, with factions who believe different
things, a scavenged ship to rebuild, and a desert that will not let them stay anywhere for
long.
