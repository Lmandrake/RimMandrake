# GPT enrichment consult: The Leaning Scrub

Asked 2026-09-30 via codex exec (gpt-5.6-sol, xhigh). Advice only: nothing here is ruled.

> Deliberate constraint: none of these restores a gravship mechanic. Mark 6 remains the owner-approved miss.

## 1. The Fogwright’s Lessons

*Ruined moisture farms teach the player how to turn fog into water—and what that extraction does to the land.*

- **Experience:** Pawns uncover tilted condensers, ceramic dew-combs and journals charting pale V-shaped scars. Repairing three distinct mechanisms unlocks vaporators; the final lesson reveals how to heal their wakes.
- **Marks:** Discoverable technology, unique mechanic, unique resources.
- **Build:** **Small C# + XML.** Three `ThingDef` study targets, study jobs/comps, a research-project unlock and incident/map-scatter variants. Persist discoveries in a `GameComponent`.
- **Why here:** The Scrub receives moisture horizontally from windblown fog. Its technology should be read from wind, not wells or rainfall.

## 2. The Calling-Pyre

*An Ideology rite deliberately burns a precious patch of fuzz and invites the walking gods to judge everyone present.*

- **Experience:** Worshippers build a low wool-and-venomvine pyre. Its smoke leans sunward; distant footfalls join the ritual music; thundersteps enter from a marked map edge and stamp through fire, enemies and careless celebrants alike. Tracks, dung and crushed lanes remain afterward.
- **Marks:** Relationship to the gods, GIANT beast, unique mechanic.
- **Build:** **Large C#.** `RitualBehaviorDef`, pyre building, map-edge arrival incident and fire-targeting lord/mental state. Herds physically enter and leave at an edge—never disappear.
- **Why here:** These gods are indifferent ecology, not supernatural visitors. Prayer means placing yourself beneath their feet.

## 3. The Wind Calendar

*The Stall and the Gale become two genuinely different ecological seasons measured in hours.*

- **Experience:** Ordinary wind carries layered tikkit clicks, bird phrases and flutterer wing-rushes. During the Stall the wind bed falls away—but nearby creatures remain richly audible; fuzzrunners lock still and zelliks launch. During the Gale the canopy roars, shirrels glide and calls stretch or vanish beneath gusts.
- **Marks:** Interesting weather, soundscape, unique mechanic.
- **Build:** **Large C# + XML.** Two `WeatherDef`s, a `MapComponent` holding wind state and fixed lean vector, weather-weight controller, animal state comps, overlays and keyed `SoundDef` sustainers.
- **Why here:** Wind is simultaneously climate, ceiling, road and hunting medium. No other biome should run on this calendar.

## 4. The Inhabited Quincunx

*Every map contains a layered handful of lives: abandoned, seasonal and currently occupied.*

- **Experience:** Players find collapsed fog farms, hollow-vine crawl settlements, smotherer banks, sweetline pilgrim camps, thornhold trappers and active scavenger yards. Occupants return, trade, feud or migrate; old fires, graves, feed piles and repaired walls reveal continuity.
- **Marks:** Discoverable technology, unique resources, relationship to the gods, soundscape.
- **Build:** **Large C#.** Biome-specific `GenStep_Scatterer`s and `SymbolResolver`s plus incidents that occupy or revisit existing injections. Keep generic `RM_` inhabitants separate from `RSW_/RUT_` Jawa dressing; Jawa caravans may bring tamed-only Blurrgs.
- **Why here:** The endless low canopy should feel densely lived in despite rarely exposing its inhabitants.

## 5. Venomvine Fivefold

*Each venomvine form becomes a recognizable ecological room rather than a recolored plant.*

- **Experience:** Dripping stands bead harvestable amber venom; Twitchers lash once, then visibly droop; Hollow stands contain traversable small-body galleries; Crown stands draw airborne dustflutter clouds during a Stall; base thickets form man-high black fortress walls.
- **Marks:** Unique mechanic, unique resources, surprising creatures.
- **Build:** **Small C# + XML.** Separate plant defs and textures, a map-level proximity sweep for Twitchers, timed venom harvesting, body-size path rules and wind-keyed flock jobs. Use overlays/inspect strings for recovery and yield.
- **Why here:** Venomvine is the biome’s sole violation of the knee-high horizon—the intended showpiece deserves mechanical as well as visual variety.

## 6. Smotherbanks

*Players cultivate valuable dead venomvine by burying living thickets beneath specially woven blankets.*

- **Experience:** A worker spreads a heavy fuzz-fiber and giant-wool blanket over a marked stand. It darkens and settles over seasons, with a readable countdown, before yielding dense, exceptionally clean-burning dead cane.
- **Marks:** Discoverable technology, unique resources.
- **Build:** **Small C#.** Blanket item and recipe, `JobDriver`, plant-state component with scribed completion tick, inspect string, alternate graphic and harvest products.
- **Why here:** The biome’s finest fuel comes from patiently killing the one plant that refuses to burn alive—an economy built from its central contradiction.

## 7. The Pale V-Wake

*Every vaporator creates a useful but damaging downwind wedge in the root-bound crust.*

- **Experience:** Soil pales behind operating machines, fuzz thins, insects relocate and animals nose toward the condenser. The wake becomes a firebreak and sightline, but overuse produces sterile branching scars; dismantling the machine lets pillowmoss begin slow recovery.
- **Marks:** Unique mechanic, unique resources, discoverable technology.
- **Build:** **Small C# + XML.** Owned crust/barrens terrains and a capped `MapComponent` cone sweep using the fixed lean vector. Store original terrain for staged restoration.
- **Why here:** Directional fog harvesting creates directional damage. It also finally removes inappropriate open sand from the biome’s core terrain.

## 8. The Runway Bloom

*Disturbing the canopy produces a visible succession of creatures across its three ecological floors.*

- **Experience:** Crustweevils scatter below, fuzzrunners bolt through stem tunnels, ribbonwhips sway across the crown and dustflutters erupt, fly forty cells and visibly land. Visslers shed twitching arms that attract real scavengers rather than acting as abstract bait.
- **Marks:** Surprising creatures, soundscape, unique resources.
- **Build:** **Large C#.** Shared disturbance propagation, jobs for runway movement, harvestable `RM_VisslerArm`, and RimWorld 1.6 animal flight for dustflutters and zelliks. No teleporting or despawning; burrowing leaves moving crust and exit holes.
- **Why here:** The Scrub’s signature is not merely many animals, but several inhabited floors occupying the same knee-high space.

## 9. Fire-Stamping Thundersteps

*Large exposed fires pull nearby thundersteps into a destructive, comprehensible suppression run.*

- **Experience:** Giants turn visibly toward smoke, gather, then advance in a widening line. Their feet extinguish flames, flatten vegetation and may crush the fire’s makers. Roofed stoves and tiny campfires do not qualify.
- **Marks:** GIANT beast, unique mechanic, relationship to the gods.
- **Build:** **Small C#.** Periodic map fire census, exposed-fire threshold, targeted mental state/lord job and stamped-terrain filth. Reuse the parental-enrage architecture.
- **Why here:** The giants treat fire as damage to their grazing floor; this grounds both their divinity and the calling-pyre in one ecology.

## 10. Named Sweetline Stations

*Every sweetline tree is a named landmark around which routes, wool harvests and local stories accumulate.*

- **Experience:** A tree receives a generated name, snagged thunderstep wool and a small history panel. Travelers camp beneath it; pilgrims leave tokens; harming it may provoke its resident guardian rather than a generic faction penalty.
- **Marks:** Unique resources, relationship to the gods, inhabited richness.
- **Build:** **Small C# + XML.** Tree comp for names, wool timer and tale records; several scatter layouts; guardian awakening through a dormant pawn or incident.
- **Why here:** On a horizon where everything is knee-high and leaning, one fixed tree naturally becomes address, shrine and public memory.

## Top 3

1. **The Wind Calendar** — makes weather, animals and sound express one unmistakable biome-wide rhythm.
2. **The Inhabited Quincunx** — directly fulfills the demand for ruins-to-living-denizens density while delivering technology through play.
3. **Venomvine Fivefold** — turns the owner’s chosen showpiece into five memorable encounters instead of five art variants.
