# Shared biome machinery, seen from the ship

**A first draft from a light read.** Three biomes were read deeply for this (the Fever Wood, the Greentide, the
Abyss; their designs are in `design/concepts/<Biome>/design.md`). The other twenty were read only as page one of
their two-page cleanse summaries (`design/concepts/*/cleanse/owner_pages.md`); Pyrelands has no such page and was
read from its mod description. "In `src/`" means a file of that name was found by listing or search on 2026-11-18;
it does not mean the code was read or works. Anything marked *(not verified)* is an inference from names.

**Revised later the same day**, after his card of 2026-11-18, 3:10 PM PST. That card answered the two questions
this file ended on (cover from orbit, fuel) and a third (hull wear). The section "Three ship systems, built once"
is new and is the consolidation of what the revised designs found. It draws on the three pilot designs, read
whole, and on four more that had landed when it was written (the Blue Desert, the Lantern Deeps, the Sleeping Ice,
the Sump), read only by searching them for cover, hull and fuel. The other sixteen biomes are not in its tables
yet.

The owner's framing, 2026-11-18: *"there IS a lot of shared machinery, and a lot of machinery one builds will
actually be active everywhere (just featured and vital in one by design, while more incidental in others... like
wind effect on fire for example)."*

## Built once, active everywhere

| machinery | what it is | featured in | incidental in | in `src/`? |
|---|---|---|---|---|
| **The Empire's clock** | The search that restarts at every landing (probe, spotter, strike, cordon, breach, bombardment), slowed fourfold on listed biomes and sped or slowed by how visible the crew is. Since his card of 2026-11-18 it also has a partial kind of cover (below). | **The Abyss** (the hide is the biome) | Every biome: it sets how long a stop lasts and what a fight there looks like. | Yes: `src/RimUtinni/EmpirePursuit/`, `src/RimMandrake/Visibility/`. Ladder numbers are marked provisional. |
| **Line of sight as cover** | Plants, trunks and Dark that block sight, so the probe and the spotter (who must *see* the ship) fail. | **The Greentide** (sight-blocking understory) | Fever Wood (solid trunks), Abyss (the Dark), Webwork, Leaning Scrub's vine islands *(not verified)* | Yes: `RM_CompSightBlocker`, `RM_MapComponent_SightBlockGrid` in `CreatureBehaviors`. Whether the probe's sighting honours it: not verified. |
| **One sun, and shade** | Heat from the sun's angle at the tile; roofs, parasols and trees as shade. No biome has its own heat. | **Long Shade**, Stillsand | Every dayside map. Nothing on the night side. | Yes: `RM_SunHeat*`, `RM_PlanetSunGeometry`, `RM_MapComponent_ShadeGrid` in `CreatureBehaviors`. |
| **Wind on fire** | Fire that walks with the wind. | **Pyrelands** | Anywhere something burns: the Fever Wood's oil haze, a blaster fight in dry scrub. | **Only inside Pyrelands today** (`MapComponent_BurnLine`, `PyrelandsFireFront`). Not yet a shared engine. |
| **Wind as an event** | Gusts, stalls and gales that creatures, sound and machines read. | Leaning Scrub (wind power, Stall and Gale), **Abyss** (gusts), Stillsand (the dune gale) | Any map with weather. | Three readers found: `RM_GustController` (Abyss), the Scrub's own calendar, `MovingDunes`. Whether they share one reading: not verified. |
| **Growth as pressure** | Wet natives growing fast; a grid that blowers, grazing and paving write to. | **The Greentide** | Fever Wood, Miasma, Webwork (*"the canopy returns"*), Contagion, Leaning Scrub's venomvine, the Cracked Lands' bloom after a flood | Yes: `ExplosiveGrowth`; blower and grazing hooks in `EnvironmentalHazards`. |
| **Ground that holds you, and the rescue** | A pawn trapped by terrain or taken by water, on a clock, freed by a companion onto firm ground. He ruled the rescue rule general on 2026-11-10: it applies *"wherever it occurs"*. | **The Fever Wood** (seized at the pools), **the Greentide** (mired) | The Twilight sea floor (carried to a sink), the Sump (tar), the Slime (swallowed) | Several: `RM_MapComponent_TheTenant`, the Greentide's mire and burial components, tar coating. One shared rescue rule in code: not verified. |
| **A sign, then the event, then a window** | A readable warning, a timed hazard, and a short harvest after it. | Cracked Lands (chimes, flood, mud), Cauldron (vents quiet, bloom), the Forge (fire and rain, crust), Pyrelands (the burn, ash) | Contagion (clear-sky window), Wastes (ash storms), Greentide (Breaklight), Abyss (the Unveiling) | Yes, as parts: `GameCondition_EnvironmentalWeather`, `RM_GameCondition_WeatherPulse`, `RM_GameCondition_GradientSurge`. |
| **Sound that means something** | A chorus that one event silences; a hum that changes; air that muffles. | **The Fever Wood** (silence means the water) | Greentide (silence means a predator), Rust Cathedral (the hum), Abyss (muffling), Webwork (it is the quiet one) | Yes: `RM_MapComponent_SilenceCue`, `RM_MapComponent_ProximitySoundscape`. |
| **Scenery that is an animal** | Ambushers that read as water, bank, bark, shade, sand or ice until weight or nearness wakes them. | Long Shade (the false shade), Greentide (the water three) | Fever Wood (the bark), Stillsand (buried predators), Sleeping Ice (things in the ice) | Yes: `RM_CompAquaticAmbusher`, `RM_CompFalseShadeAmbusher`, `RM_CompSandSwim`; the `Watchers` and `HostileFlora` kits. |
| **You were noticed** | The place answers what the crew does: light, warmth, noise, taking. | Lantern Deeps (light draws the minds), Rust Cathedral (extraction provokes), Webwork (robbing the web brings hunters) | Abyss (light), Sleeping Ice (warmth), Fever Wood (noise) | No shared engine found. Each biome has its own. The visibility dial is the Empire's version of the same idea. |
| **Light as a resource** | Light that grows crops, that things eat, that gives you away. | **The Abyss** | Lantern Deeps, the Rot, the Twilight sea floor | A shared light ledger exists (named in the Abyss census); who else uses it: not verified. |
| **Wrecks and salvage** | What the crew steps outside for in every biome. | Wastes, Sleeping Ice, Rust Cathedral, Blue Desert | Everywhere | Yes: `Wreckage`. Also the ship's own parts: the acoustic sounder (a reading per biome) and the keel hoist. |
| **Natives belong here** | Natives are never trapped, seized or left thirsty by their own home. | — | Every biome | Yes: `RM_HazardNativeExtension`; thirst through `FlowWorks`. |
| **The landing itself** | What the game does when a gravship arrives. | — | Every biome | Yes, by filename, not read: `GravshipLanding` (unfogs outdoor ground so the landing is not blind), `RM_Patch_GravshipArrivalLetter`, `RM_Patch_LaunchHeldColonistWarning` (a launch warns when someone is still held). These are where "the first minutes" of every design would hook in. |

Also everywhere, and nobody's feature: real flight for anything that flies, bone from butchery, calm-gated
gathering, a settings switch per feature.

## Three ship systems, built once (his rulings of 2026-11-18)

Every biome design now states three things about the landed ship: what cover it has from orbit, how the place wears
the hull, and where fuel comes from. Each is one system built once and read by every biome. A fourth ruling from
the same card is a test, not a system: *"you should always look for solutions that make you say Very Jawa"*
(scavenging, haggling, trading constantly, improvising with junk, a small skittish crew in over its head). Where a
design below had two ways to answer a wear or a shortage, it took the one made of scrap and argument.

### Hull wear

**His words.** *"Yes in 0.1.0. It's easy, and most of the biome already talk about this. Heat. Acid. Rough weather
turbulence in the approach. Heat or cold. Different kinds of shields or armor. It's in there."*

**It is in there.** The frame exists in the campaign tier: `src/RimUtinni/ShipShields/` (found by search on
2026-11-18; header comments and the hazard tests read, the rest not; nothing here says it has passed anything). It
was built from his eight shield rulings of 2026-09-02, recorded in
`design/Jawa/proposals/ship_shields_deep_design.md`. The first draft of this file missed it. What it does today:

- `ShieldHazardExposureTracker` wears the ship's own structures while the map holds a hazard the ship's shield
  does not cover. The per-hit strength is flat; the rate doubles after a long unshielded spell.
- `ShieldLandingAdvisory` sends one letter on landing and never refuses a landing. His ruling: *"The environment
  is hostile and immediately goes to work on the ship. The ship will know what's visibly dangerous and will advise
  course of action, but no more than that. Its hull is thick and can take a lot of damage in most situations, so no
  environment is immediately lethal. Landing on lava should be the worst case causing immediate severe damage
  (don't do that)."*
- One shield generator holds one field at a time, changed by installing modules: a heavy field (*"impactors,
  blaster fire, and large animal assault"*), a thermal veil, a cryo envelope, and a light screen that by his words
  handles *"wind, ash, vapor, bio contamination, spores, smoke, sand, and rain damage completely as well as repels
  small animals"*.
- No field stops slow things: *"Slow pressing things move through all shields... This is why nothing 'holds out
  water,' it just doesn't work that way."*
- The hazards it can see are three, each from a base-game signal: extreme outdoor heat, extreme outdoor cold
  (forty below, or a cold snap), and blown sand or dust in the weather. Lava at landing is a one-time burst.

**What is missing, and is the build.** A biome cannot yet declare a wear of its own. The designs need four kinds
the tracker does not know:

1. *Weather that falls on the hull* (the Abyss's etchfall). Nearest to what exists.
2. *A living thing on the hull* (the Greentide's rasp).
3. *The ground under the hull* (the Fever Wood's marsh; the Blue Desert's drift against it; the Sump's tar on it).
4. *A reach or an event that hits the hull* (the Fever Wood's limbs; a knock on arrival through the Abyss's gusts).

And it counts only a shield as an answer. The designs also answer wear by hand and with junk: scraping, patching,
stilt footings, a roofed lean-to, a dry-air blower, shovels. The shared system has to let a biome name those as
cover against its own wear. Proposed rules for every biome's wear, taken from his rulings above: it shows a sign
before it costs; it is a bill that grows, never a wall; launching always ends it; no bar pins its rate.

**Tier.** A ship touch is campaign layer (his card of 2026-10-01 for the Abyss: the free tier gets no ship touch),
and `ShipShields` is already there. Wear on what the crew builds outside the ship stays in each free biome.

| biome | how it wears the hull | what answers it | version | source of the wear |
|---|---|---|---|---|
| **The Abyss** (featured: weather on the hull) | Etchfall grain on the outside of the ship. A knock on arrival through gust shear. | A roofed lean-to of scrap against the hull; patching; the light screen. | Grain 0.1.0; the knock 0.2.0. | Sheet (*"breakage and cold"*; the wind section); the hiding note. |
| **The Greentide** (featured: a living wear) | The hull rasp on all outside metal. Falling trees. | Scraping by hand; a dry-air blower; the light screen for the rasp, the heavy field for a tree. | 0.1.0. | The review of 2026-10-02 (not chosen then; asked by name on the card of 2026-11-18). |
| **The Fever Wood** (featured: the ground) | The marsh under the hull; limbs lashing a hull edge in a pool's reach. | Where the ship is set down; stilt footings; patching; quieting the pool. No field stops the marsh. | 0.1.0; the snare and torn-off section 0.2.0. | The review of 2026-10-02 (the Mooring). |
| The Blue Desert *(read by search only)* | Ice sand drifting against the grounded hull. | Shovels. | As its design states. | Its design cites a 2026-09-28 ruling. |
| The Sump *(read by search only)* | Tar fouling the hull, and tar burns. | As its design states; it marks the hull skin as owed. | As its design states. | Its design. |
| The Sleeping Ice *(read by search only)* | Cold, as a standing cost in power and fuel to keep the ship habitable. | Insulation and discipline: closed doors, cold outer compartments. | 0.1.0, per its design. | Its design. |
| The Lantern Deeps *(read by search only)* | Its design says the cave never touches the hull; the ship sits on a surface host at forty below, which is the tracker's built cold case. | | | |

### Fuel

**His words.** *"Every biome has a fuel source, but for most its the hideously slow route of rendering biomass into
chemfuel. Uselessly slow, only for emergencies. A few biomes have richer sources. You can also buy it (the intended
motivation to have to trade constantly, very Jawa)... One or two are REPLETE with fuel (the frozen Chill beach for
example)."* And his older ruling, 2026-08-15 (`design/Jawa/reconciled_lore/01_campaign.md`, "Fuel is life"):
*"Many paths to fuel, or the ship starves"*; the paths *"differ in ACCESS COST, never in viability; no quest or
faction may ever gate the last remaining path."*

**What it is, built once.** Three tiers and a shop:

1. *The emergency route, everywhere:* biomass rendered to chemfuel. The base game's refining does this already.
   Nothing to build unless the rate needs slowing to earn "uselessly slow" (not checked).
2. *A richer source, in a few biomes:* one local stuff and one recipe each.
3. *Replete, in one or two:* fuel for the taking.
4. *Buying:* traders who stock fuel, and something local to pay them with. This is the part meant to be used
   most. No shared fuel-trader stock was looked for in `src/`; *(not verified)*.

`design/Jawa/concept.md` says the ship's fuel is refined from chemfuel at two for one, as *"the built-in fuel
leash"*; whether that is still the ship layer in use was not checked.

| biome | class | the source | who sells | built? |
|---|---|---|---|---|
| **The Abyss** | richer, and the hide burns it | tholin swept after etchfall | nobody (*"No salvage. No sun. No trade."*) | Yes: the refining recipe is in `src/RimMandrake/Abyss/`. |
| **The Greentide** | richer (the sheet's *"the dayside's fuel economy"* could carry replete; his word) | resin; and greenwood for the slow route | Jawa crawlers at the band's edge; the Wildsteam's seats (campaign) | Harvests yes; recipe and sellers no. Its blower burns chemfuel (built). |
| **The Fever Wood** | richer | seep-oil, standing inside a pool's reach | Sporefall's Wildsteam traders (campaign) | Harvest yes; recipe and sellers no. |
| The Blue Desert *(search only)* | richer; its design says the propane lakes, *"one step colder"*, are the replete source | cold wax from every plant and carcass, refined cold | nobody | Per its design. |
| The Lantern Deeps *(search only)* | richer | the candler's cold wax, *"burns like chemfuel and needs no refinery"* | nobody, per its design | Per its design. |
| The Sump *(search only)* | richer | tar | per its design | Its design says rendering tar to ship fuel is not built. |
| The Sleeping Ice *(search only)* | emergency route only, *"and barely that"* | carcasses and what was carried in; a few salvaged cylinders | `UNSETTLED` in its design | Per its design. |

Two cautions for whoever builds this. A biome is written as rich only where a source line supports it (his
instruction in the brief for these rewrites). And the two wax biomes above describe what reads like the same stuff:
check they share one item before either builds its own.

### Cover from orbit

**His card, word for word.** *"Why: makes where you land a real choice without making any biome a free hideout.
Canopy, steam and fog slow the search by one step; full dark still pauses it. Costs a small build per covered biome
and one more thing each design must state. Recommended: it answers your 'what helps them stay and hide' question in
every biome."* On how long a stop then lasts: *"The numbers you're generating are likely the outer edge allowable
for each biome, and that's just fine. Go with that."*

**What exists.** The pursuit (`src/RimUtinni/EmpirePursuit/`) has one list, `surveyShadowBiomes`, with one biome on
it (`RM_Abyss`), and one multiplier for it (four). The crew's visibility (`src/RimMandrake/Visibility/`) sets the
pace in five bands: hidden, discreet, noticed, marked, exposed, with each wait multiplied by 2, 1.4, 1, 0.7 and 0.5
(`EmpireLadderMath.cs`, whose header marks every number provisional). The Abyss adds a ship that gathers cover
while quiet, dark and cold-engined (`RM_MapComponentShipCover`).

**What is missing, and is the build.** A second, weaker list: biomes with partial cover. The three pilot designs
read "one step" as one visibility band quieter, because bands are the only steps the search has; that is a reading
and is flagged on each choices page. On today's numbers it turns a stop of about a month at the outside into one of
about six weeks. A loud crew loses the step.

| biome | cover | why | outer edge of a stop, as its design states |
|---|---|---|---|
| **The Abyss** (featured) | full | permanent Dark; on the built list | about two months before first contact; longer while the ship's own cover holds |
| **The Greentide** | partial | canopy and steam, together one step | about six weeks |
| **The Fever Wood** | partial | closed crown | about six weeks |
| The Sump *(search only)* | partial | deep dusk, not full dark | per its design |
| The Sleeping Ice *(search only)* | partial, for a ship run cold; asks whether its sunless night is full dark | | 28 to 45 days one step quieter |
| The Blue Desert *(search only)* | its design claims full dark | never sees the sun | per its design |
| The Lantern Deeps *(search only)* | the surface host's; asks whether that dark pauses the search as built | | per its design |

## Questions left that are one question across all the biomes

The two this file used to end on are answered above. These came out of applying the answers.

1. **Which sunless places are "full dark"?** Only the Abyss is on the built list, and its Dark is a substance. The
   Blue Desert's design claims full dark, the Sump's takes one step, the Sleeping Ice's and the Lantern Deeps' each
   ask. One ruling settles four designs: is the plain night side full dark, or only the Abyss?
2. **Is "one step" one visibility band?** All three pilot designs assume so.
3. **Which version are the richer sources' recipes in?** His words give none. The pilot designs put an unbuilt
   recipe in 0.2.0 and leave a built one (tholin) where it is.
4. **Does a running shield give the ship away?** Asked by the Abyss's design, where light is what breaks cover.
   Assumed not.

## Biomes that read alike under the lens

A crew that lands at two of these in a row may feel it has seen the second one already. Each group needs its
members told apart by what the *crew does*, not by palette.

- **The wet green ones:** Fever Wood, Greentide, Webwork, Miasma. Trapping ground, a punishment for touching, giant
  plants. Told apart today by sound (loud, loudest, silent) and by what moves (nothing, everything, the spiders).
- **The dark ones lit by what grows:** Abyss, Lantern Deeps, the Rot, the Twilight sea floor. In all four, light
  matters and something answers it.
- **The salvage fields with a tax:** Wastes (poison), Warscar (what it does to the mind), Rust Cathedral (the
  machines), Sleeping Ice (cold and what warmth wakes), Blue Desert (fuel that blasts).
- **The warned cycles:** Cracked Lands, Cauldron, the Forge, Contagion, Pyrelands. Sign, event, window.
- **The open crossings:** Long Shade, Stillsand, Leaning Scrub. These are closest to the crew's home desert. His
  lens says the Jawa are *"adapted only to their parent desert biomes"*, so here the joke cannot be that they are
  out of their depth. These three need a different source of "did you see that".

## Build order, in one line

The Empire's clock comes first because every design leans on how long a stop lasts and what a probe can see; then
the general rescue rule; then growth and its suppression. The Fever Wood and the Greentide share the most groundwork
(painted root routes, mineable living trunks, the silence cue, ground that holds you) and should be built as a
pair; the Abyss shares almost nothing with them and pairs with the Lantern Deeps. Of the three ship systems, the
partial-cover list is the smallest and goes in with the clock; hull wear is next, because he placed it in 0.1.0 and
its frame exists; fuel recipes follow biome by biome, with the shop built once.
