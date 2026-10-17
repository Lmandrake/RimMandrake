# Venomvine: the Leaning Scrub grows teeth (design, 2026-10-16)

Item: `VENOMVINE_BUILD_SCRUB_GROWS_TEETH`. Design only: nothing here is built, installed or deployed.

> Owner, 2026-10-16: *"Venomvine was supposed to be integral to the Leaning Scrub... the one plant that grows
> abundantly tall and dangerous. I think we need it in there. And there were many variants to consider too..."*

## 0. The short version

**Venomvine is already built, and it is in the game. You just cannot see it.** (Rulings of 2026-10-16 are in section 10; the sections below are written to them.) Fifteen venomvine plants exist
in code, with their mechanics, their Mod Settings and a deployed copy (Baroque Biomes is active in your mod list).
Four things hide it:

1. **It is rare.** All venomvine together is 8% of the Scrub's wild-plant weight (0.43 of 5.32), on a biome
   whose plant density is 0.35. Most single forms sit at 0.02 to 0.05. The Crown is 0.002.
2. **It is short.** Every form is drawn at about one cell (size 0.9 to 1.3). A person is taller. Your ruling
   says man-height or more.
3. **Ten of the fifteen look identical in game.** Rearing, Walking, Quench, Sworn, Shedding, Strangler, Weeper,
   Sleeper (both states) and Lure all show the same placeholder picture (one file, checksum `9dfff4bf`). Hoard
   shows it for half its variants. Own renders exist for every one of them in
   `D:\Luke\dev\_artpipe\done\`. Your card of 2026-10-09 said to swap them in ("replace all"); it was never
   carried out, because the art ledger would not take a card over a kept picture.
4. **Three forms never grow wild.** Strangler, Weeper and Lure are built but are not on the Scrub's plant list,
   so no map ever gets one.

**The headline of this design:** make venomvine the Scrub's skeleton. Every map gets **near-black islands of
it (about 15% of open ground)**, standing **taller than a person**, that **creep slowly downwind** on their own clock, with the rarer forms
living as **rooms inside the islands**. Its growth is its own number, kept out of Explosive Growth whichever way
that goes.

## 1. What you have said about it (verbatim, dated)

- 2026-09-21 (sheet amendment, `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\arid_shrubland.md`):
  *"'cover everywhere' is interpreted only for smaller things than you. People stand out. Except for the
  venomvine, that should be man-height or more."*
- 2026-09-29 (bedazzle sitting, ruling 6): *"The art for the venomvine should be especially rich, varied,
  interesting... its the strange showpiece here. Maybe one variant of it can be a dripping kind that is
  overproducing the venom and thus can be harvested. Another kind could be a Twitcher, that when you get near
  lashes out and strikes you once."*
- 2026-09-30 (card): *"I really like the different kinds of venom vine. Might need even more."*
- 2026-10-03 (card): build all six further forms; the sworn hedge lets through anyone carrying its sap mark
  (raiders can steal it); hoard stands keep the gear of whatever dies inside.
- 2026-10-08 (finishing the Scrub sheet): *"We will need to settle all that Venomvine in a sitting on Bench in
  the game at some point since it's also a mechanic that grows in patches."* On the Hoard row: *"Keep all of
  these for now, Venomvine is a mechanic as well as graphics, so we will need to reason about this during Bench
  settings."* On the Rearing and Quench rows: *"STOP USING THIS GRAPHIC AND MAKE VENOMVINE!"* On the Twitcher and
  Thicket rows: *"variations"*.
- 2026-10-08 (card): admit Strangler, Weeper, Sleeper and Lure.
- 2026-10-09 (card): the own renders replace the copied thicket picture on the other forms.

The sitting (`LEANINGSCRUB_VENOMVINE_SITTING_1`) was deferred on 2026-10-08 and has not happened. Its run-sheet:
`D:\Luke\dev\RimMandrake\Transient\venomvine_sitting_runsheet_2026-10-09.md`.

## 2. What venomvine is

The Scrub is a knee-high silver-green fuzz plain where everything leans sunward and nothing hides a person.
**Venomvine is the one exception**: black cane thickets, taller than a man, that break sightlines, wall off
ground, poison whatever forces through, and are nearly impossible to burn while alive. It is the dungeon, the
curtain wall, the treasure vault and the fuel bank of the biome, all in one plant.

### What "dangerous" means in play (built today, kept)

- **Contact venom.** Entering a stand scratches you once, then once an in-game hour while you stay. Each
  scratch adds thorn venom: minor at 5%, serious at 30%, grave at 60%, lethal at 100% (lethal can be switched
  off). Venom fades by half a stage a day. Code: `CompContactVenom`, `MapComponent_ContactVenom`
  (EnvironmentalHazards).
- **It blocks big bodies.** Under body size 0.8 passes freely, 0.8 to 1.5 threads slowly, 1.5 and up cannot
  enter. A Jawa slips in, a person forces a way, a giant is stopped.
- **Each form adds one more kind of danger** (section 5).

### What changes in this design

| | today | proposed |
|---|---|---|
| **How much** | scattered single stands, 8% of plant weight | **islands**: a map step lays 8 to 14 near-black islands per map (count PROVISIONAL, scaled up to reach the share), each a body of thicket 40 to 200 cells, about **15% of the map's open ground** in all (RULED Q1, Heavy). The wild list still scatters lone stands between them. |
| **How tall** | drawn about 1 cell | drawn **1.8 to 2.4 cells** (tree height), on a tall canvas, rooted at the cell's base, leaning sunward. It towers over a person at play zoom. |
| **Cover** | none set | **half cover** for anyone inside or behind it (like sandbags), and pawns deep inside an island are hidden from the colony's view the way small creatures are hidden in the fuzz. Full shot-blocking is out: in RimWorld that also blocks walking, which breaks the size gate. |
| **Growth** | vanilla regrowth only (plus Walking's gale runners) | **its own slow creep** (section 3) |
| **The forms** | each scattered alone | **rooms inside islands**: an island is thicket, with one to three rarer forms grown into it (a dripping room, a twitcher gate, a hollow gallery, a crown at the heart of the biggest island) |

## 3. Growth: its own clock, independent of Explosive Growth

You are rethinking Explosive Growth right now
(`D:\Luke\dev\RimMandrake\design\RimMandrake\explosive_growth_deep_dive_2026-10-16.md`). Today venomvine is
inside it: the everyday band speeds its growth ×4, and a soaked stand could go faster again. That ties the
Scrub's backbone to a system that may change shape.

**Proposal: take venomvine out of Explosive Growth completely**, by putting every venomvine defName on
Explosive Growth's two existing exemption lists (the no-soak list and the no-band list, both read by
`RM_ExplosiveGrowthRegistry.cs`). Then whichever direction you pick there (water only, brakes, events, or the
combination), venomvine grows at exactly its own speed.

**Its own speed is a creep, not a burst.** That is what "a mechanic that grows in patches" means here:

- A fully grown stand that has stood for a while (about **10 days**, PROVISIONAL) puts **one runner** into a
  free neighbouring cell.
- The pick favours **downwind** (the map's locked lean heading): about 3 in 4 runners go downwind. Islands
  therefore stretch sunward over a long game, like everything else in the Scrub.
- Runners only go onto natural crust. Never onto floors, under roofs, onto a cell with a building, or into a
  vaporator's dried wake once that wake exists.
- **A map cap** stops it: venomvine never passes a set share of the map (default **22%**, above the 15% laid share). At the cap, creep
  stops until something is cut, burned or smothered.
- A runner is **safe for its first days**: no venom until it reaches half growth. Cutting the front is a cheap
  chore; smothering the body stops the whole island.
- Walking venomvine keeps its own faster, gale-driven walk on top. Sworn venomvine creeps only where it was
  sown (it is a crop, not a weed). Crown never creeps.

The engine is one map-level sweep every few in-game hours (plants only tick every ~33 seconds), the same shape
as the six-form sweep already in `RM_VenomvineForms.cs`.

## 4. How it fits the Scrub mechanics FOUNDRY built

| built mechanic (`LEANINGSCRUB_MECHANICS_BUILD_1` and after) | venomvine's part |
|---|---|
| **The Lean** (one wind heading per map) | creep and Walking go downwind; Shedding throws its thorn V downwind; art leans sunward |
| **Upwind flee** (prey bolt from a person upwind) | a pawn inside an island is masked: the cane's own smell covers theirs (PROPOSED, small: one check added to the scent patch). Hunting from inside the thicket becomes the Jawa ambush. |
| **Downwind fire** (fire races downwind, creeps upwind) | living venomvine barely burns (flammability 0.1), so an island is a **firebreak** the downwind front splits around. **Dead** venomvine (Walking's dead tail, ripened smother claims) burns long and hot, so a fire that meets dead cane **flares**. Quench stands burst firefoam. Pyroculture raiders can reveal scrap nests by burning a dead patch, as the sheet says. |
| **Fire-stamping giants** | giants (body size 1.5 and up) cannot enter a thicket. A fire deep inside an island **cannot be stamped**: they stand at the edge. (Design intent; the stamping code has not been checked against the size gate.) |
| **The Stall and the stallhawk** | small creatures freeze in the Stall; inside an island they are out of the hawk's reach, so islands become the Stall's shelters and the dustflutters mob the Crown there (built). |
| **Vaporators** (the building exists; the dried downwind wake does not yet) | venomvine does not creep into a vaporator's wake once built. A vaporator is the colonist's way to hold an island back without cutting. |
| **Smother-craft** (built) | the main tool against an island: blanket it, wait, collect dead venomvine fuel |
| **Inhabited injections** (built: smother-claimed fields, hedge homesteads) | these already place venomvine; they sit inside or beside the new islands |

## 5. The variants (fifteen defs; fourteen belong to the Scrub)

Weight is the current wild-list weight. "Room?" says where it lives under this design.

| form | what differs | weight today | room? |
|---|---|---|---|
| **Thicket** (`RM_VenomvineThicket`) | the base: man-high black wall, size gate, venom | 0.15 | **the island body** |
| **Dripping** (your idea) | beads amber venom; harvest gives raw venom and the stand regrows | 0.05 | harvest room on an island's edge |
| **Twitcher** (your idea) | lashes once at anything close, then droops spent for an hour | 0.05 | gatekeeper at island mouths |
| **Hollow** | dead grey galleries; small creatures and Jawa crawl through; no venom | 0.04 | the corridors inside an island |
| **Crown** | rare tall black column, the plain's only flower; dustflutters mob it in the Stall | 0.002 | the heart of the biggest island (one per map at most) |
| **Rearing** | snaps upright when pushed into, revealing whoever is inside; the Gale masks it | 0.03 | the island's alarm edge |
| **Walking** | creeps downwind each Gale; the old tail dies back into fuel | 0.02 | an island's sunward tip |
| **Hoard** | grows in loose items and dead gear; cutting it gives everything back | 0.02 | deep room, near scrap nests |
| **Quench** | bursts firefoam when fire touches it, then spent for days | 0.03 | scattered in the body: why islands survive fires |
| **Sworn** | the only sowable form; spares pawns wearing its sap mark | 0.005 | hedge homesteads only, never a wild island |
| **Shedding** | each Gale throws a V of thorn litter downwind | 0.02 | an island's downwind face |
| **Strangler** | wraps a wall or tree and damages it until trimmed | **not on the list** | island edges that touch a tree or ruin |
| **Weeper** | leaves a venom pool that poisons the soil | **not on the list** | a low room; its pool is the island's dead patch |
| **Sleeper** | looks like dead vine until a body passes, then wakes and lashes | 0.01 | among dead cane, where it lies |
| **Lure** | sweet fruit draws animals into the thicket | **not on the list** | the island's bait room |
| *Desert venomvine* (`RM_Venomvine`) | the scattered desert form, EnvironmentalHazards | Desert list | not a Scrub plant |

## 6. Harvest and use

- **Raw venom** (Dripping, regrowing harvest): the sap-mark for Sworn hedges, and a trade good.
- **Dead venomvine**: the region's finest fuel. From smother claims, Walking's dead tail, and cutting a dead
  stand. Burns hot in any wood-fuelled building (built).
- **Living cane** (proposed, small): cutting a grown stand by hand yields a little cane, a spiked building stuff
  for fences and traps. Cutting is slow and the cutter is scratched unless the stand is smothered first.
- **Sworn seed**: the one sowable form, behind the Scrub research step (built).
- **What it guards**: scrap nests and Hoard stands inside islands are the treasure; the venom is the price.

## 7. Readable signs (nothing harmful without one)

| harm | sign |
|---|---|
| venom scratch | the stand is near-black and visibly thorned; the inspect line names the venom; the pawn shows a "thorn venom" condition with its stage |
| size gate | inspect line: "passes freely under 0.8, threads to 1.5, blocks above" |
| creep | fresh runners are a different colour (rust-ochre, thornless); inspect: "spreading, next runner in about N days" |
| Twitcher lash | the drooping, spent pose for an hour after a strike |
| Rearing | the stand stands upright with its pale underside showing |
| Shedding | the rust V of litter on the ground |
| Sleeper | inspect on the "dead vine" says "dormant venomvine" (the sign is the label, not the picture) |
| Strangler | the wrapped wall or tree shows the cane on it and takes visible damage |
| Weeper | the venom pool and the stained soil around it |
| Hoard | metal glints inside; the inspect line lists what it holds |
| Quench | collapsed, cracked knuckles while spent |
| dead-cane flare | dead venomvine looks bleached grey; anything that burns hot looks dead |
| hazard clocks | the filed readout item `ENVHAZARDS_HAZARD_CLOCK_READOUTS_1` (venom contact and next scratch on hover) |

## 8. Mod Settings

**Already there** (`RM_LeaningScrubMod.cs`, EnvironmentalHazards): venom on/off, scratch strength, lethal
venom on/off, size gate on/off, passability, and one switch (plus tuning) for each of Twitcher, Dripping, Crown,
Rearing, Walking, Hoard, Quench, Sworn, Shedding, Strangler, Weeper, Sleeper, Lure and the smother-craft.

**New** (defaults = shipped behaviour):
- **Venomvine islands**: on/off; islands per map (default 8 to 14); share of open ground (default **15%**, RULED Q1).
  Labelled "affects new maps only".
- **Venomvine creep**: on/off; days between runners (default 10); downwind share (default 75%); map cap
  (default **22%**: it must sit above the 15% laid share or creep would be dead on arrival; PROPOSED, owner may change).
- **Cover and concealment inside stands**: on/off.
- **Scent masking inside stands**: on/off.
- All off: venomvine is a scattered, still, poisonous plant as it is today.

## 9. Art brief, per variant

**Laws for every form** (from the frozen sheet and your rulings): near-black cane on silver-green ground;
**taller than a person** (tall canvas, rooted at the bottom, crown leaning sunward); each form owns **one accent
colour**; **no green**; not a briar, bamboo or bramble; posture, never a voice; **at least three random
variants per form** (your "variations"). Renders already exist for every form in `D:\Luke\dev\_artpipe\done\`;
check them first, and regenerate only what fails these laws (the current renders are about one cell tall).

| form | look | accent | extra states |
|---|---|---|---|
| Thicket | a dense man-and-a-half-high wall of black cane, swept sunward, lightless inside | none: the pure black | edge pieces so islands read as one mass |
| Dripping | thicket with amber beads hanging from every cane | amber | harvested (beads gone) |
| Twitcher | a few long whip canes standing above a low body, coiled and tense | dull red at the cane tips | spent: the whips drooping flat |
| Hollow | dead grey cane tubes with dark open galleries a small body fits through | ash grey | none |
| Crown | one tall black column, the tallest venomvine, with a single pale flower at the top | bone-white flower | a dustflutter cloud is creatures, not art |
| Rearing | canes laid low and flat in sunward sweeps | pale bone-grey underside bands | reared: every cane upright against the lean |
| Walking | a long wedge: old black tail, thin rust-ochre runners at the sunward tip | rust-ochre | none |
| Hoard | a squat fist of canes coiled inward | cold metal glints in the interior | none |
| Quench | thick canes with swollen knuckle joints | wet slate-blue sheen | spent: knuckles collapsed and cracked, cane scorched |
| Sworn | trained, bound in lines, flat-topped: plainly grown on purpose | knots of pale undyed fibre | none |
| Shedding | tall and ragged, the sunward face stripped to pale scarred cane | rust thorn litter (a separate ground item) | none |
| Strangler | canes spiralled around something upright, gripping it | sickly ochre at the grip points | wrapped on wall, wrapped on tree |
| Weeper | low drooping canes over a dark wet pool | oily violet-black sheen on the pool | none |
| Sleeper | looks exactly like bleached dead cane | none while asleep | awake: black, thorned, upright, a deep red at the cane joints |
| Lure | thicket with clusters of round pale-gold fruit low on the outer canes | pale gold | picked (fruit gone) |

## 10. Rulings (owner, question cards, 2026-10-16)

- **Q1 RULED (by card): Heavy, islands at about 15% of open ground.** Against the recommendation of 8%. The Scrub becomes a maze: travel, building and pathing get much harder, and the 12% map cap is raised to 22% so creep still has room.
- **Q2 RULED (by card): tree-tall, 1.8 to 2.4 cells.** The tall-canvas re-render is approved.
- **Q3 RULED (by card): its own slow creep downwind, capped, outside Explosive Growth** (section 3).
- **Q4 RULED (by card): all fifteen forms stay, as rooms inside islands; install the existing renders; Strangler, Weeper and Lure go on the wild list** (section 5).

## 11. Build consequences

1. Island map step targets 15% of open ground (not 8%): re-size the island count and body size; check that travel and the base-building area stay possible (keep the start area and colony site clear of islands, PROPOSED) and that pathing and pawn-count stay inside perf bounds.
2. Map cap default 22% (above 15%); every creep-related test and setting default uses the new numbers. Any text still saying 8% share or a 12% cap is wrong.
3. Add every venomvine defName to Explosive Growth's two exemption lists (Q3).
4. Wild list: add Strangler, Weeper, Lure (weights set so rooms, not scatter, place them); install the existing `_artpipe\done` renders on the ten forms that share the placeholder, then commission the tall-canvas re-render of all forms (Q2, art approved).
5. Cover and concealment: at 15% the hidden-from-view rule affects far more of the map; keep its Mod Setting and label it.
