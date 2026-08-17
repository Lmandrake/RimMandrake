# Star Wars RimWorld Xenohusbandry, Aquaculture & Culinary-Fauna Design
## Production mechanisms, facilities, breeding systems, symbionts, failures, and rare events

**Design status:** Intentionally overcomplete brainstorm  
**Companion to:** `star_wars_rimworld_cuisine_brewing_overcomplete_design.md`  
**Target:** RimWorld 1.6 Star Wars culinary/brewing expansion on a tidally locked desert world with a lethally hot dayside, cryogenic nightside, and habitable terminator belts.

---

# 1. Design thesis

The culinary expansion becomes much more distinctive if food animals are **not all implemented as ordinary pen animals**.

The major production classes should be:

1. **Conventional herd ranching** — banthas, shaaks, nerfs, kod'yoks.
2. **Heavy desert stock** — rontos, eopies, mudhorns.
3. **Burrow and pit husbandry** — gorgs, worrts, sandmaggots, scurriers, slugs, worms.
4. **Aviaries / flight lines / balloon yards** — porgs, loralora birds, mykals, hawk-bats, puffer pigs.
5. **Pond and raceway aquaculture** — gorgs, paddy frogs, yobshrimp, fleek eels, small fish.
6. **Deep-pressure aquaculture** — colo claw fish and other large marine predators.
7. **Tree-canopy / vertical husbandry** — rikknit.
8. **Hive husbandry** — sparkbees and other social insects.
9. **Power-fed parasite culture** — mynocks.
10. **Live-food culture** — worms, slugs, glubex, trufflites.
11. **Bioculture / host symbiosis** — deliberately invented RimWorld-style xenobiology where a farmer hosts a harmless or semi-harmless brood organism to harvest eggs, sacs, secretions, or larvae.
12. **Trophy propagation** — acklay, krayt, mudhorn and other dangerous species where the player is not really “farming” so much as maintaining a controlled ecological hazard.

The design goal is that the player should be able to recognize a facility at a glance and think:

> “That is not a cow pen. That is where they grow the terrible food.”

---

# 2. Lore anchors worth building mechanics around

The following are unusually useful because Star Wars provides actual biological/husbandry details rather than only food names.

- **Banthas** are domesticated herd animals used for milk, meat, hide and wool.
- **Rontos** are gentle, strong Tatooine pack animals favored by Jawas.
- **Shaaks** are herd animals actually raised for meat.
- **Kod'yoks** are farmed for meat and milk; their wool, hides and dung are also useful.
- **Puffer pigs** inflate dramatically when frightened and possess extraordinary mineral-smelling ability.
- **Mynocks** are vacuum-adapted energy parasites; Legends additionally describes replication after sufficient feeding and explicit mynock incubation facilities.
- **Colo claw fish** are giant aquatic carnivores that ambush prey from underwater tunnels.
- **Mudhorns** prefer cool, dark caves.
- **Rikknit** in Legends are arboreal crustaceans whose females carry external ovum sacs; harvesting those sacs is the basis of their egg industry.
- **Gorgs** are small edible creatures and can also chew wiring.
- **Kod'yok** husbandry is particularly well developed in lore: ranching, milk, meat, wool, hides and dung fuel all coexist.

**Lore reference links**
- https://www.starwars.com/databank/ronto
- https://www.starwars.com/databank/shaak
- https://www.starwars.com/databank/puffer-pig
- https://www.starwars.com/databank/mudhorn
- https://www.starwars.com/databank/colo-claw-fish
- https://www.starwars.com/databank/gorg
- https://starwars.fandom.com/wiki/Bantha
- https://starwars.fandom.com/wiki/Kod%27yok
- https://starwars.fandom.com/wiki/Mynock/Legends
- https://starwars.fandom.com/wiki/Rikknit/Legends
- https://starwars.fandom.com/wiki/Rikknit_egg
- https://starwars.fandom.com/wiki/Sandmaggot

Everything below that goes beyond these facts is **mod design**, not claimed lore.

---

# 3. Facility language

A strong visual vocabulary helps the whole expansion feel coherent.

## 3.1 Conventional ranch structures

| Building | Appearance | Function |
|---|---|---|
| **Bantha Shade Corral** | Thick sandstone posts, canvas shade sails, moisture troughs, wool caught on rails | General bantha pen; heat mitigation |
| **Moisture Trough** | Condenser-fed trough with blue mineral staining | Low-water livestock drinking |
| **Bantha Grooming Frame** | Heavy timber/metal arch with comb teeth and wool bags | Improves wool yield and animal comfort |
| **Nerf Dairy Stall** | Narrow shaded milking lane, chilled milk hoses | Automated/semi-automated nerf milk collection |
| **Shaak Round Pen** | Low broad fence around grazing patch, feeding mounds | Meat-focused herd |
| **Kod'yok Snow Paddock** | Windbreak walls, frost-coated fencing, covered milk stall | Nightside cold ranching |
| **Eopie Lean-To** | Low sunshade, tether rails, water condenser | Small homestead pack stock |
| **Ronto High Yard** | Extremely tall gate, overhead feed crane, enormous shade canopy | Ronto husbandry and caravan loading |
| **Ronto Loading Gantry** | Elevated platform at neck/back height | Converts rontos between livestock and caravan mount roles |
| **Dung Fuel Press** | Compact brick press with drying racks | Kod'yok/bantha/eopie dung → burnable fuel cakes |

## 3.2 Pit and burrow structures

| Building | Appearance | Function |
|---|---|---|
| **Deep-Beast Pit** | Sunken floor illusion, heavy vertical walls, retractable ladder | Acklay/mudhorn/large dangerous animals |
| **Sandmaggot Dune Bed** | Raised oval sand mound surrounded by buried mesh | Egg and larval production |
| **Worrt Burrow Bank** | Artificial rock/sand mound with many dark holes | Worrt breeding |
| **Scurrier Warren** | Layered scrap-pipe burrow complex | Small desert scavenger production |
| **Gorg Wet Pit** | Shallow lined pit with mud shelves and insect lamps | Gorg ranching |
| **Vel-Slug Run** | Humid trench with glazed ceramic walls | Slug production |
| **White-Worm Cabinet** | Heated glass-front drawers filled with substrate | Ylesian worm production |
| **Trufflite Bed** | Luxury humid terrarium over fungus-rich soil | Slow high-value Hutt delicacy |
| **Keebada Hazard Vat** | Lidded ceramic tank with glove ports and warning lamps | Dangerous small-creature culture |
| **Duraslug Masonry Crib** | Stack of sacrificial duracrete blocks inside a catch basin | Lets slugs “graze” on structural mineral feed |

## 3.3 Aquaculture structures

| Building | Appearance | Function |
|---|---|---|
| **Brine Raceway** | Long shallow channels with pumps and shade cloth | Small fish, shrimp, roe species |
| **Paddy-Frog Rackpond** | Tiered shallow trays with aquatic plants | Frog and spawn production |
| **Yobshrimp Lantern Tank** | Clear glowing tanks filled with swarming tiny shrimp | Live-food/cocktail production |
| **Fleek-Eel Pipe Farm** | Coiled opaque pipes and feeding ports | Eel culture |
| **Mollusk Basket Line** | Suspended baskets in shallow brine pond | Shell/mollusk production |
| **Redfish Net Pen** | Mesh cages inside natural or artificial water | Flesh and roe production |
| **Quekka Conservation Pond** | Low-density naturalistic pond with protected nest zones | Rare fish with ethical/permit mechanic |
| **Deepwater Pressure Tank** | Thick transparent walls, heavy pipes, dim lighting | Large deepwater species |
| **Colo Tunnel Aquarium** | Huge dark tank with artificial rock tunnels and observation slit | Colo claw fish broodstock |
| **Roe Incubation Cabinet** | Refrigerated drawer-wall with labeled egg trays | Keeps culinary roe edible—or intentionally hatches it |
| **Cryo Nursery** | Frosted tanks partially buried in cold ground | Coldwater juveniles and slow maturation |
| **Mobile Fish Net** | Deployable net infrastructure on world-map/coastal tile | Low-tech fish-net aquaculture |

## 3.4 Aerial and tethered structures

| Building | Appearance | Function |
|---|---|---|
| **Balloon Pasture Mast** | Tall central post with rotating tether arms | Semi-buoyant/inflatable livestock |
| **Puffer-Pig Mooring Yard** | Soft net canopy, padded posts, elastic tethers | Prevents frightened inflated pigs from smashing into structures |
| **Porg Rookery** | Cliff-shaped nesting wall with ledges | Eggs/meat/feather production |
| **Loralora Aviary** | Tall mesh tower with flowering perches | Small bird production |
| **Mykal Sky Corral** | Huge net dome with suspended carcass feeders | Dangerous aerial predator ranching |
| **Hawk-Bat Loft** | Roof-mounted roost boxes and egg drawers | Urban egg production |
| **Gwayo Nest Tower** | Tall nesting mast with collection balcony | Egg production |
| **Flight-Line Post** | Two tall poles joined by retractable tether cable | Allows semi-free flight exercise without escape |

## 3.5 Tree/canopy structures

| Building | Appearance | Function |
|---|---|---|
| **Rikknit Climbing Orchard** | Artificial tree trunks, web frames, upper walkways | Arboreal crustacean breeding |
| **Ovum Harvest Gantry** | Elevated narrow catwalk with gentle handling arms | Removes external egg sacs without slaughter |
| **Web Storage Frame** | Mesh panel where rikknit can build nests | Raises fertility and animal comfort |
| **Canopy Feed Lift** | Pulley-fed trays high above ground | Keeps handlers away from aggressive breeders |

## 3.6 Hive / microfauna structures

| Building | Appearance | Function |
|---|---|---|
| **Sparkbee Flare Hive** | Metallic hive boxes with glowing vents | Honey production |
| **Nectar Trough** | Shallow aromatic feeder | Stabilizes honey output when flowers scarce |
| **Brood Heat Plate** | Warm ceramic tile under hive | Increases reproduction, also raises swarm risk |
| **Insect Protein Bin** | Ventilated living-feed box | Feeds gorgs, frogs, predatory bugs |
| **Larval Sorting Table** | Fine trays, brushes and jars | Separates edible larvae/eggs from breeders |

## 3.7 Vacuum / parasite structures

| Building | Appearance | Function |
|---|---|---|
| **Mynock Vacuum Blister** | Black translucent bubble bolted to exterior hull/wall | Maintains low-pressure mynock culture |
| **Sacrificial Power Bus** | Thick exposed cables running through cage | Electricity becomes animal feed |
| **Mynock Incubator** | Suspended cage surrounding energized coils | Encourages replication |
| **Hull-Scrap Feeder** | Rack of metal plates and wreckage | Prevents mynocks from eating useful infrastructure |
| **Quarantine Airlock** | Double door, helium emergency purge canister | Stops escapes |
| **Mynock Harvest Cage** | Fold-out restraint basket | Safe slaughter/capture |

## 3.8 Bioculture / host-symbiont structures — entirely invented for the mod

| Building | Appearance | Function |
|---|---|---|
| **Xenobiotic Clinic** | Small sterile room with creature tanks and surgical couch | Installs/removes culinary symbionts |
| **Brood Implant Cradle** | Soft restraint couch under monitoring arch | Implant surgery |
| **Symbiont Monitor** | Wall display tracking growth cycles | Predicts harvest events |
| **Ovum Collection Chair** | Reclining chair with collection bottles | Nonlethal harvest from host |
| **Brood Recovery Bed** | Medical bed with heat/cooling control | Reduces post-harvest penalties |
| **Emergency Purge Unit** | Medical extractor | Removes rejected/escaped symbiont |
| **Restaurant's Living Pantry** | Decorative back-room bioculture cabinet | Tiny restaurant-scale brood organisms |

---

# 4. Creature-by-creature production systems

## 4.1 Conventional and semi-conventional ranch animals

| Creature | Production facility | Feed / habitat | Products | Signature mechanics | Failure / event hooks |
|---|---|---|---|---|---|
| **Bantha** | Bantha Shade Corral | Desert forage, hay, water; shade | Blue milk, meat, wool, hide, dung | Herd social need; grooming raises wool; can serve as caravan animals | Matriarch dispute, calf defense ring, wool molt, dry-season milk crash, predator panic |
| **Nerf** | Nerf Dairy Stall + pasture | Grass/hay, moderate water | Milk, cheese input, meat, hide | High dairy output; milking schedule; breeding line traits | Mastitis analogue, escaped bull, milk glut, cheese-culture contamination |
| **Shaak** | Shaak Round Pen | Grazing + fodder | Meat, hide; Legends ambergris/perfume input if enabled | Cheap fast-growing meat animal; panics easily | Stampede, bloat, breeding frenzy, “everyone sat on the same fence” breakage |
| **Ronto** | Ronto High Yard | Huge fodder requirement, considerable water | Meat, hide; pack/mount labor | Can alternate between livestock and caravan carrier; skittish | Startled by machinery, knocks down wall, neck stuck in roof, refuses loading |
| **Eopie** | Eopie Lean-To | Sparse desert feed, water | Meat, milk if desired, dung, caravan labor | Very low-input homestead stock; pack animal | Legendary flatulence event fouls dining room; stubborn work refusal |
| **Kod'yok** | Kod'yok Snow Paddock | Frostside grazing/fodder | Meat, milk, wool, hide, dung fuel | Naturally ideal nightside livestock; wool insulation; dung press | Rutting males smash gates; herd thinned if overhunted; blizzard roundup |
| **Puffer pig** | Puffer-Pig Mooring Yard | Herbivore feed; calm enclosure | Meat/bacon; mineral-detection labor | Fear causes enormous inflation; can detect buried ore | Inflates indoors and blocks doorway; wind carries tethered animal; herd “chain inflation” |
| **Mudhorn** | Refrigerated Mudhorn Grotto | Cool dark cave, mud wallow, heavy feed | Rare eggs, meat/hide if slaughtered | Territorial, slow breeding, huge egg value; prefers darkness/cool | Horn charge, cave mating bellow, egg defense rage, mud wallow destroys flooring |
| **Kod'yok milk line** | Snow Milking Shed | Same herd | Specialty cold dairy | Cold-side dairy ages well | Frozen teat equipment, milk freezes in pipes |
| **Droidbreaker** | Mineral Paddock | Scrap/mineral feed | Iron-rich meat | Converts low-value metal scrap into specialty meat | Eats forbidden component stack; metal deficiency rage |
| **Sand lizard** | Warm Rock Pen | Insects/small prey | Steak/game meat | Solar heated pen reduces power use | Escapes into walls; tail-drop event |
| **Heklu** | Bog Pen | Wetland forage | Amphibian meat | Terminator wetland ranching | Breeding chorus causes sleep penalty |
| **Feejay** | Small Exotic Pen | Creature chow | Luxury meat | Slow, high-value breeder | Fragile juvenile die-off |
| **Gargon** | Marsh Paddock | Wet feed | Gumbo meat | Efficient batch food animal | Swamp odor attracts wildlife |

---

## 4.2 Small desert pit fauna

| Creature | Facility | Feed / habitat | Products | Mechanics | Rare failures |
|---|---|---|---|---|---|
| **Gorg** | Gorg Wet Pit | Shallow water/mud, insects | Meat, eggs | Very fast reproduction; good homestead protein | Chews electrical wiring after escape; “Bitey” event; population boom |
| **Worrt** | Worrt Burrow Bank | Sand burrows, insects/small prey | Eggs, meat | Mostly underground; harvest by baiting them out | Bites handler; egg chamber discovered under adjacent room |
| **Klatooine paddy frog** | Paddy-Frog Rackpond | Aquatic trays, insects | Meat, eggs/spawn | Spawn collected repeatedly without killing adults | Spawn tray hatches unexpectedly; frogs leap into dining room |
| **Sandmaggot** | Sandmaggot Dune Bed | Hot sand, organic scraps | Eggs, kidneys/meat | Larval stages invisible underground; egg harvest periodic | Entire dune “boils” with hatchlings; larvae migrate toward fermenters |
| **Scurrier** | Scurrier Warren | Scraps/seeds/insects | Seasonal meat/tips | Seasonal production burst | Warren breaks into pantry; breeding swarm |
| **Vel slug** | Vel-Slug Run | Fungus/vegetable waste | Slugs | Converts waste to luxury Hutt food | Slime coats floor; escapees eat garden |
| **Ylesian white worm** | White-Worm Cabinet | Wet protein mash | Worms | Drawer-based micro-livestock; huge density | Drawer left open: worm carpet |
| **Effrikim worm** | Divided Worm Cabinet | Protein substrate | Two-headed worms | Valuable live service; fragile culture | Heads bite one another during stress; mass die-off |
| **Trufflite** | Trufflite Bed | Fungus-rich substrate | Whole luxury creature | Slow growth, low input, high price | “Trufflite thieves” event; rare spontaneous color morph |
| **Glubex** | Glubex Brine Wheel | Brackish water, microfeed | Whole delicacy | Star-shaped colonies cling to rotating surfaces | Tank stars detach and clog pumps |
| **Keebada** | Keebada Hazard Vat | Unpleasant mash | Processed delicacy | Requires skilled handling and PPE | Venom/irritant exposure; batch ruins gloves |
| **Duraslug** | Duraslug Masonry Crib | Sacrificial duracrete/mineral blocks | Meat | Converts building material into food | Escaped slugs start eating actual walls |
| **Millitile** | Millitile Drawer Farm | Grain/insect feed | Legs / whole small creature | High-density protein culture | Drawer population cannibalism |
| **Robuma** | Small ranch / dry pit | Generic feed | Jerky animal | Primarily preservation commodity | Overpopulation / nuisance herd |

---

## 4.3 Tree, hive, and canopy production

| Creature | Facility | Feed | Products | Mechanics | Failures/events |
|---|---|---|---|---|---|
| **Rikknit** | Rikknit Climbing Orchard | Canopy feed, insects/fruit as mod abstraction | External ovum sacs / eggs, optional web | Egg harvesting can be nonlethal; overharvest reduces fertility | Ovum sac rupture; protected-species inspection; tree-top escape; brood web blocks walkway |
| **Sparkbee** | Sparkbee Flare Hive | Flowers/nectar trough | Honey | Hive population + flower availability determine yield | Defensive swarm; queen replacement; honey flow attracts predators |
| **Hawk-bat** | Hawk-Bat Loft | Insects/small prey | Eggs, meat | Roof-integrated urban farming | Colony becomes feral; nocturnal screeching |
| **Gwayo bird** | Gwayo Nest Tower | Seed/insect feed | Eggs | Tall nesting preference; egg baskets | Birds mob egg collector |
| **Loralora bird** | Loralora Aviary | Seeds/fruit | Wings/meat/eggs if desired | Small attractive bird doubles as ambience animal | Flock escape becomes map-wide recapture mini-event |
| **Porg** | Porg Rookery | Fish/insects | Meat, eggs | Cliff/rock rookery; extremely prolific | Colonists develop “too cute to butcher” thought; porgs invade kitchen |
| **Mykal** | Mykal Sky Corral | Meat/live prey | Meat | Dangerous flying predator; aerial exercise required | Net tear leads to hunting incident; mating flight causes berserk attacks |
| **Pylat bird** | Warm Aviary | Seed/fruit | Rich eggs | High-fat egg line; selective breeding | Broody birds stop laying |
| **Golden pheasant** | Ornamental Aviary | Grain | Meat/eggs/feathers | Beauty + food dual use | Predator raid on aviary |

---

## 4.4 Aquaculture and marine production

| Creature | Facility | Feed / water | Products | Mechanics | Failures/events |
|---|---|---|---|---|---|
| **Fleek eel** | Fleek-Eel Pipe Farm | Fish scraps/live feed | Meat | Eels hide in pipes; harvest by draining a loop | Eels knot filter, escape into plumbing |
| **Yobshrimp** | Yobshrimp Lantern Tank | Algae/microfeed | Live shrimp | Ultra-fast reproduction; live service premium | “Not dead yet” dining escape; swarm in sink drains |
| **Vaoloi mollusc** | Mollusk Basket Line | Filter feeder | Whole mollusk | Low labor, slow growth | Harmful bloom kills basket line |
| **Quekka fish** | Conservation Pond | Fish feed/natural pond | Meat | Very low stocking density; protected status | Poacher event; regulator visit; breeding success jackpot |
| **Redfish** | Redfish Net Pen | Pellets/fish feed | Meat + roe | Sexed broodstock; seasonal roe | Roe theft; fungal gill disease |
| **Frella-fish** | Shallow Roe Raceway | Microfeed | Roe + fish | Optimized for repeated roe stripping | Overharvest causes infertility |
| **Coodler** | Brine Raceway | Small-feed pellets | Roe | Primarily roe species; pickling economy | Refrigeration failure can become hatch event |
| **Colo claw fish** | Colo Tunnel Aquarium | Large live prey/meat | Roe/caviar, meat | Requires darkness, tunnels, enormous tank; breeder pair highly dangerous | Tunnel ambush kills handler; filter failure; cannibalism; tank-wall strike |
| **Hocekureem** | Standard Fish Pen | Pellets | White fish fillet | Reliable restaurant fish | Water-quality crash |
| **Hammerfish** | Heavy Raceway | Crustacean feed | Meat | Strong swimmers need flow | Breaks grate; knocks worker into water |
| **Trask cephalopod** | Cephalopod Maze Tank | Crabs/shrimp | Chowder animal | Enrichment needed; clever escape artist | Unscrews hatch / hides in kitchen; steals tool |
| **Mollusk general stock** | Basket Line | Filter feeding | Meat/jerky/garum | Waste-efficient aquaculture | Biofouling reduces pumps |
| **Slaur** | Swamp Roe Pond | Local swamp ecology | Roe | Low-tech wetland production | Toxic bloom / predator invasion |
| **Ubuuga caviar species** | Premium Caviar Raceway | High-grade feed | Luxury roe | Slow maturity, huge price | Broodstock dies if temperature drifts |
| **Generic gorg-water culture** | Wet Pit/Rackpond | insects | Meat/eggs | Can bridge land/aquatic mechanics | See gorg events |

---

## 4.5 Large dangerous culinary fauna

| Creature | Facility | Feed | Products | Mechanics | Rare events |
|---|---|---|---|---|---|
| **Acklay** | Acklay Deep-Beast Pit | Large quantities of meat | Claws/meat, breeder eggs if invented | Requires pit depth, feeding gantry, very high Handling | Claw reaches over rim; mate kills mate; pit gate sheared |
| **Krayt dragon** | **Do not truly domesticate**; protected nest reserve / baited nesting canyon | Wild ecosystem | Eggs only, perhaps naturally shed material | Colony maintains a dangerous wild nesting site rather than pen | Dragon returns while egg collectors present; nest migration; poachers |
| **Mudhorn** | Refrigerated Grotto | Heavy feed | Eggs | Manage breeding pair, darkness, mud | Breeding season charge frenzy |
| **Orpali dragon** | Orpali Nursery | Small live feed / high-grade meat | Young culinary animals | Ethically dubious high-control breeder; huge Hutt price | Activist/authority raid; juvenile escape; parent refuses brood |
| **Cannok** | Cannok Brush Pen | Omnivorous scraps | Meat | Aggressive scavenger useful for waste conversion | Eats equipment / steals dropped weapon |
| **Terrafin** | Terrafin Rock Yard | Vegetable/meat mix depending adaptation | Loin/meat | Specialty slow breeder | Burrows out |
| **Trakkrrrn** | Spice-Beast Paddock | Plant/meat feed depending mod lore | Naturally spicy meat/fat | Diet influences spice intensity | “Hot” breeding line becomes aggressive / overheating |
| **Yalbec** | Yalbec Stingery | Live prey | Stingers + meat | Harvest stingers nonlethally at high skill | Handler sting; pheromone alarm causes colony rage |
| **Mykal** | Sky Corral | live prey | meat | Flying predator | See above |

---

## 4.6 Weird specialty animals

| Creature | Facility | Products | Signature system |
|---|---|---|---|
| **Mynock** | Mynock Vacuum Blister + Sacrificial Power Bus | Edible flesh, spore/replication material if Legends systems enabled | **Electricity is feed.** Well-fed mynocks replicate; poorly contained mynocks escape and drain colony power |
| **Puffer pig** | Mooring Yard + Mineral Scent Course | Meat/bacon + prospecting labor | Can be trained to reveal nearby ore deposits; fear inflation creates physical chaos |
| **Droidbreaker** | Mineral Paddock | Iron-rich meat | Eats low-grade slag/scrap; converts inorganic waste into biological food |
| **Rikknit** | Climbing Orchard | Eggs/ovum sacs | External egg-sac economy; nonlethal harvest |
| **Sparkbee** | Hive | Honey | Flora-to-luxury sweetener chain |
| **Mynock culture as reactor parasite** | Reactor-collar variant | Biomass | Power grid acts like pasture |
| **Puffer-pig balloon herding** | Tether mast variant | Animal + mining service | Wind and fear turn livestock into semi-buoyant hazards |

---

# 5. Host-symbiont culinary production
## Entirely speculative, intentionally RimWorld-like

This should be a **late research branch**, optional, and ideology/trait-sensitive.

The important design rule: the host is not necessarily being “harmed.” Some symbionts may be no worse than a weird implant or pregnancy. The horror/comedy comes from biological unfamiliarity.

## 5.1 Implant candidates

| Implant | Inspired by | Host requirement | Periodic product | Benefit | Risk |
|---|---|---|---|---|---|
| **Rikknit Ovum Graft** | External rikknit ovum sacs | Adult organic pawn | Small ovum sac | Extremely valuable roe without tree farm | Pain/itch, rejection, accidental hatch |
| **Sandmaggot Brood Pouch** | Fermented sandmaggot eggs | Pawn with warm body temp | Egg cluster | Produces fermentable eggs anywhere | Heat stress, “moving under skin” mood, brood escape |
| **Sparkbee Nectar Symbiont** | Honey production | Pawn consumes sugar regularly | Sweet secretion vial | Portable luxury sweetener | Attracts insects; sweet scent; hypoglycemic-style hunger spike as game effect |
| **Paddy-Frog Spawn Bladder** | Frog spawn | Amphibious-compatible or modified pawn | Egg pearls | Cocktail garnish/roe | Burping/croaking social debuff; accidental spawning in bath |
| **Vel-Slug Mucus Gland** | Slug cuisine | Any organic pawn | Culinary slime concentrate | Sauce thickener / Hutt delicacy | Grossed-out thoughts, dehydration |
| **Coodler Roe Vesicle** | Roe fish | Aquatic xenotype or advanced biotech | Roe packet | High-value roe | Requires hydration; infection on poor harvest |
| **Mynock Power-Leech Harness** | Mynock energy feeding | Mechanoid or cyborg pawn, external rather than implanted | Tiny mynock buds / biomass | Converts pawn battery drain into culinary product | Battery loss; escape attaches to nearby generator |
| **White-Worm Gut Culture** | Ylesian white worms | Organic pawn | Mature worms harvested non-surgically | Extremely compact mobile worm farm | Violent vomiting event; appetite increase |
| **Trufflite Symbiotic Nodule** | Trufflite luxury food | Body-modder-friendly pawn | Slow-growing trufflite | Restaurant owner can literally cultivate house specialty | Movement discomfort; rare rupture |
| **Golden-Lichen Skin Culture** | Botanical/fungal analogue | Exposed skin | Lichen flakes | Non-animal garnish | Cosmetic discoloration, social reactions |

## 5.2 Host psychology

Possible thoughts:
- **Something is growing in me**
- **My little passengers are healthy**
- **Harvested again**
- **I am the pantry**
- **Profitable symbiosis**
- **Disgusting implant**
- **Body-mod cuisine**
- **The chef asked if I'm ready for service**
- **That one hatched early**
- **I can feel them moving**

Traits should matter:
- Body Modder: positive.
- Body Purist: severe negative.
- Gourmand: curious/neutral-positive.
- Ascetic: probably negative toward luxury use.
- Cannibal/creepy ideology traits: perhaps indifferent.
- Xenophile-type ideology: positive.

---

# 6. Husbandry mechanics beyond vanilla pens

## 6.1 Breeding-season states

Animals should have a periodic **mating season** state that modifies behavior rather than merely fertility.

Possible consequences:
- movement speed increases;
- hunger rises;
- social fights among males;
- fences take impact damage;
- handlers become targets of courtship/territorial aggression;
- milk production temporarily drops;
- egg production follows with a boom;
- herd animals attempt to cluster together;
- isolated animals suffer distress;
- flying animals perform mating flights;
- aquatic animals stop eating and begin nest building;
- fermented smells may accidentally trigger mating behavior in unrelated wildlife.

Species-specific examples:
- **Bantha rut:** horn sparring, matriarch-herd reshuffling.
- **Kod'yok rut:** males slam windbreaks.
- **Puffer pig courtship:** constant partial inflation; animals bounce around the enclosure.
- **Gorg spawn season:** every muddy surface receives eggs.
- **Rikknit web season:** entire gantry webbed over.
- **Mynock replication pulse:** power draw spikes before population doubles.
- **Yobshrimp bloom:** tank suddenly turns opaque with larvae.
- **Mykal mating flight:** net dome becomes violently crowded.
- **Acklay pairing:** one bad compatibility roll can kill a breeder.

## 6.2 Feed affects product

A simple dietary-quality system can create interesting culinary outcomes:

- Banthas fed aromatic desert forage produce **Herbed Blue Milk**.
- Nerfs fed saltgrass produce higher-cheese-solids milk.
- Puffer pigs fed mineral-rich forage become better prospectors.
- Colo claw fish fed crustaceans produce richer orange roe.
- Sparkbees fed Cassius nectar produce **Cassius Honey**.
- Trakkrrrn fed boontaspice-rich fodder produce absurdly spicy fat.
- Rikknit fed specific fruit produce differently colored eggs.
- Mudhorns fed mineral supplements produce thicker-shelled eggs.
- Yobshrimp fed luminous algae become glowing live-cocktail garnish.

## 6.3 Animal comfort matters

High-end output should depend on husbandry quality:

- stress reduces roe;
- overcrowding creates disease;
- poor nesting causes egg loss;
- inadequate darkness makes colo fish infertile;
- lack of mud makes mudhorns aggressive;
- puffer pigs kept frightened all the time become sick;
- mynocks starved of energy attack structures;
- overmilked herd animals lose condition;
- badly ventilated worm cabinets create catastrophic odor.

This gives restaurants an incentive to operate *nice* little farms rather than only industrial slaughter pens.

---

# 7. Rare event library

These should be infrequent enough to remain funny/scary rather than becoming chores.

## 7.1 “The food was not actually dead”

1. **Yobshrimp Resurrection** — a plated shrimp suddenly leaps off the table and flees under furniture.
2. **The Second Course Returns** — a crustacean shell discarded in trash begins moving; the animal was in torpor.
3. **Fleek Eel Reflex** — an apparently butchered eel coils around a cook's wrist.
4. **Glubex Reattachment** — two cut pieces fuse back together in the pantry.
5. **Mollusk Closure** — a supposedly dead mollusk clamps onto expensive silverware.
6. **Paddy Frog Pocket Escape** — garnish frog revives when warmed by a diner.
7. **Cryo-Thawed Roe Parent** — frozen egg mass contains a surprisingly developed embryo.
8. **Duraslug Regeneration** — discarded tail tissue grows into a tiny slug.
9. **Trufflite Budding** — uneaten garnish produces a daughter organism overnight.
10. **“The Soup Blinked”** — purely cosmetic rare thought/event after live Hutt cuisine.

## 7.2 Roe and egg catastrophes

11. **Roe Bloom** — unrefrigerated roe does not rot; it hatches.
12. **Coodler Kitchen Swarm** — dozens of finger-length fish flop through the kitchen.
13. **Paddy Spawn Explosion** — sink/drainage system becomes full of tadpoles.
14. **Mudhorn Egg Cracks Early** — extremely valuable egg turns into an extremely inconvenient baby.
15. **Rikknit Ovum Spill** — hundreds of tiny hatchlings climb nearby furniture.
16. **Worrt Nursery Underfloor** — forgotten eggs hatch beneath a bedroom.
17. **Gorg Storm** — warm rain causes every stored fertile egg to hatch at once.
18. **Unplanned Caviar Nursery** — elite dining stock becomes breeding stock; player chooses eat, raise, or sell.
19. **Wrong Incubator Drawer** — culinary roe and breeding roe are swapped.
20. **Cold Snap Saved Them** — a “ruined” clutch becomes viable after an unexpected freeze.

## 7.3 Fermentation and digestion horrors

21. **Ferment Purge** — pawn violently vomits after an unusually potent fermented dish.
22. **Chain Purge** — several diners who shared the same crock become sick in sequence.
23. **Overactive Culture** — bottle keeps fermenting after opening and sprays a room.
24. **Gut Rebellion** — pawn acquires temporary severe hunger and intestinal discomfort after new microbial food.
25. **The Good Batch** — dangerously strong ferment gives an enormous positive buff *and* high vomiting chance.
26. **Gas Pocket** — sealed crock launches its lid across the room.
27. **Blue Cheese Fog** — aging cellar odor gives everyone nearby a mood opinion.
28. **Garum Leak** — concentrated fish ferment spills and contaminates an entire storage room's smell.
29. **House Culture Mutation** — long-lived starter develops a rare beneficial trait.
30. **House Culture Goes Bad** — same starter becomes unusable until kitchen sterilized.

## 7.4 Smell attracts wildlife

31. **Ferment Scent Raid** — desert predators arrive specifically targeting fermenters.
32. **Worm-Scent Frenzy** — insectivores swarm White-Worm Cabinets.
33. **Fish Smoke Migration** — airborne scavengers circle the smoker.
34. **Honey Night** — sparkbee honey attracts huge nocturnal insects.
35. **Bantha-Blood Trail** — blood-processing causes predators to follow caravan home.
36. **Garum Season** — every wild carnivore in range becomes unusually interested in the kitchen.
37. **Trakkrrrn Aroma** — spicy fat draws a specialized beast that considers it mating pheromone.
38. **Fruit Ferment Stampede** — herbivores break fences seeking sweet brewing mash.
39. **Mynock Power Scent** — large powered fermentery attracts wild mynocks to the electrical grid.
40. **The Restaurant Has Fans** — harmless wild gorgs begin living around garbage bins.

## 7.5 Mating season chaos

41. **Bantha Rut** — two males repeatedly ram gates and each other.
42. **Kod'yok Roundup** — herd breaks pasture formation and must be manually rounded up.
43. **Puffer Pig Courtship** — inflated animals bump and bounce through the yard.
44. **Mykal Mating Flight** — aerial predators slam the aviary net.
45. **Gorg Chorus** — endless croaking causes sleep penalty but huge egg production.
46. **Worrt Burrow War** — males fight underground, collapsing tunnels.
47. **Rikknit Web Frenzy** — paths become impassable until webs cleared.
48. **Sparkbee Queen Flight** — hive divides; player may capture new queen or lose half colony.
49. **Colo Territorial Season** — paired fish turn on each other.
50. **Acklay Pairing Disaster** — courtship escalates into a lethal duel.
51. **Yobshrimp Moon Bloom** — population increases tenfold in a day.
52. **Mudhorn Nest Rage** — parents become manhunters if colonists approach the egg.

## 7.6 Escape events

53. **Mynock Loose** — escapes blister and begins draining random powered buildings.
54. **Mynock in the Gravship** — several escape into ship machinery; power efficiency drops until hunted.
55. **Gorg in the Wiring** — little animal causes random shorts.
56. **Cephalopod in the Pantry** — intelligent tank animal steals food and hides.
57. **Duraslug Wall Breach** — escaped slugs tunnel through a noncritical wall.
58. **Puffer Pig Aloft** — frightened pig becomes effectively airborne in a dust storm while tethered.
59. **Mykal Net Tear** — predator escapes into colony.
60. **White-Worm Carpet** — drawer farm spills thousands of worms.
61. **Vel Slug Trail** — colonists track slime throughout base; movement penalty until cleaned.
62. **Porg Kitchen Occupation** — flock occupies counters and steals ingredients.
63. **Rikknit Ceiling Colony** — escaped crustaceans establish a breeding nest over a room.
64. **Fleek Eel Plumbing Incident** — eel escapes into water system and emerges somewhere absurd.

## 7.7 Environmental husbandry failures

65. **Dayside Heat Surge** — pond oxygen crashes; aquaculture emergency.
66. **Frostside Pipe Freeze** — milking or fish-water pipes freeze solid.
67. **Terminator Storm Shift** — fermentation rooms suddenly too cold/hot.
68. **Salt Pan Dusting** — dust storm contaminates high-grade salt.
69. **Cryo Nursery Power Loss** — stored live cultures begin waking/thawing.
70. **Solar Dryer Flash Char** — extreme sun cooks instead of dries a batch.
71. **Acid Brine Intrusion** — crater-water chemistry changes unexpectedly.
72. **Night Ice Migration** — fish move into colder water and stop feeding.
73. **Mudhorn Cave Collapse** — wallow undermines constructed floor.
74. **Ronto Water Panic** — moisture system fails; herd drinks emergency reserves.

## 7.8 Disease, parasites and symbiont events

75. **Brood Rejection** — implanted symbiont becomes inflamed and must be removed.
76. **Brood Synchronization** — several hosts begin producing on the same day.
77. **Accidental Hatch in Host** — living young must be surgically removed.
78. **Symbiont Transfer** — one species migrates to another pawn during close contact.
79. **Sweet-Scent Host** — sparkbee symbiont causes wild insects to follow pawn.
80. **Worm Purge** — host expels the entire white-worm culture during vomiting.
81. **Ovum Jackpot** — unusually large but harmless egg sac forms.
82. **Host Attachment** — pawn becomes emotionally attached to symbiont and resists removal.
83. **Restaurant Celebrity** — visitors learn the chef grows the house delicacy personally; prestige skyrockets.
84. **Body Purist Scandal** — faction guests react badly to host-grown cuisine.

## 7.9 Trade, law and faction events

85. **Protected Species Inspector** — checks rikknit/Quekka/orpali operation.
86. **Hutt Buyer Arrives** — offers absurd price for live rather than processed specimens.
87. **Geonosian Breeder** — can improve insect fertility genetics.
88. **Mon Cala Aquaculturist** — offers water-quality upgrade.
89. **Tusken Herdmaster** — teaches better bantha breeding but objects to disrespectful slaughter.
90. **Jawa Livestock Swap** — wants to trade a dubious animal plus mystery crate.
91. **Mandalorian Field Chef** — buys shelf-stable premium meats.
92. **Imperial Quarantine** — mynock escape causes temporary trade restriction.
93. **Blackstar Poachers** — attempt to steal rare breeders instead of attacking colonists.
94. **Egg Smuggling Contract** — transport a live fertile egg without customs discovering it.
95. **Restaurant Critic** — evaluates freshness, animal welfare, facility cleanliness and presentation.
96. **Rare Breeding Pair Auction** — colony can gamble huge silver on exotic broodstock.

## 7.10 Restaurant-scale comedy and horror

97. **The Plate Walked Away** — diner receives live food; it escapes before being eaten.
98. **Egg-Hatching Challenge** — cantina bartender encourages customers to finish drink before garnish hatches.
99. **Too Fresh** — diner thought varies from ecstatic to horrified.
100. **Chef's Pet** — kitchen staff refuses to slaughter a named breeder.
101. **Customer Wants It Alive** — special order requires live service.
102. **Customer Wants It Deader** — offended guest demands kitchen kill moving dish properly.
103. **Wrong Table** — Hutt live platter delivered to squeamish Imperial delegation.
104. **Puffer Pig at the Bar** — frightened pig inflates and wedges itself between tables.
105. **Gorg Theft** — live gorg steals garnish from another table.
106. **Caviar Price Spike** — sudden offworld shortage makes stored roe spectacularly valuable.
107. **Legendary Vintage + Legendary Roe** — pairing creates colony-wide dining story.
108. **The Last Egg** — restaurant demand conflicts with preserving breeding stock.

---

# 8. Production-scale tiers

The same animal should support several scales.

## Homestead scale

1–6 creatures or one small culture.

Buildings:
- single gorg pit;
- one paddy rack;
- one worm cabinet;
- two banthas;
- tiny nerf dairy;
- rooftop hawk-bat loft;
- one sparkbee hive.

Purpose:
- family food;
- occasional luxury ingredient;
- small trade surplus.

## Restaurant scale

Enough output to maintain a menu.

Buildings:
- 2–4 specialist cultures;
- aging and refrigeration;
- visible guest-facing aquarium/aviary;
- live pantry.

Purpose:
- signature dishes;
- high-margin rare food;
- “house-grown” prestige.

A wonderful restaurant mechanic would be **table-visible husbandry**:
- diners can see yobshrimp tanks;
- paddy frogs croak behind the bar;
- pickled mynocks hang in glass jars;
- a sparkbee hive glows through a wall;
- the rare breeder is visible but *not* automatically slaughtered.

## Settlement farm scale

Large output and faction trade.

Buildings:
- multiple corrals;
- large water system;
- dedicated aquaculture;
- hatchery;
- feed production;
- veterinary area;
- slaughter/processing chain.

Purpose:
- exported cheese/jerky/roe;
- faction contracts;
- caravan provisioning.

## Industrial exotic ranch

Potential late game.

Examples:
- huge mynock energy farm;
- deep-pressure colo facility;
- large Hutt live-food complex;
- protected-species breeding center;
- cryogenic kod'yok ranch;
- xenobiotic host farm.

At this scale, breakdowns should become **colony events**, not just lost output.

---

# 9. Visual identity by planetary zone

## Scorchside facilities

Materials:
- pale ceramic;
- rusted shade frames;
- reflective foil;
- buried water pipes;
- solar concentrators;
- deep pits;
- salt crust.

Best animals:
- bantha;
- ronto;
- eopie;
- gorg;
- worrt;
- sandmaggot;
- scurrier;
- puffer pig;
- mynock exterior blisters.

## Frostside facilities

Materials:
- black insulated walls;
- glowing heat lamps;
- frost-coated fences;
- buried warm shelters;
- thick insulated water pipes.

Best animals:
- kod'yok;
- coldwater fish;
- cryo roe broodstock;
- perhaps specialized bantha lines;
- frost-smoked eel facilities.

## Terminator facilities

Materials:
- ordinary agricultural fencing;
- greenhouse-adjacent culture rooms;
- humid fungal tanks;
- fermentation buildings;
- mixed ranch/aquaculture.

Best animals:
- nerf;
- shaak;
- sparkbee;
- rikknit;
- paddy frog;
- general aquaculture;
- restaurant farms.

---

# 10. Research tree

1. **Xenohusbandry** — basic exotic pens, feed, handling.
2. **Desert Stockkeeping** — bantha/ronto/eopie infrastructure.
3. **Microfauna Culture** — worms, gorgs, slugs, small pits.
4. **Aquaculture** — ponds, baskets, raceways.
5. **Roe Husbandry** — broodstock sexing, roe stripping, incubation.
6. **Deepwater Aquaculture** — pressure tanks, colo claw.
7. **Aerial Husbandry** — flight lines and aviaries.
8. **Arboreal Husbandry** — rikknit canopy systems.
9. **Hive Culture** — sparkbee systems.
10. **Vacuum Fauna** — mynock blister and power feeding.
11. **Dangerous Beast Handling** — mudhorn/acklay/large predators.
12. **Protected Species Breeding** — conservation + legal trade.
13. **Culinary Symbiosis** — voluntary host implants.
14. **Advanced Brood Surgery** — rare symbiont production.
15. **Restaurant Husbandry** — guest-visible live pantry and premium freshness bonuses.

---

# 11. Compatibility ideas

## Vanilla animal systems

Use normal pens when they add value:
- bantha;
- nerf;
- shaak;
- kod'yok;
- eopie.

Do **not** force normal pens on:
- mynock;
- aquatic species;
- worms;
- slugs;
- rikknit;
- sparkbees;
- deep predators.

## Biotech

Potential integrations:
- xenotype dietary preferences;
- symbiont implants as Hediffs;
- genes changing tolerance for raw/live/fermented foods;
- insectoid/Geonosian affinity for brood foods;
- sanguophage preference for bantha-blood products.

## Ideology

Precepts:
- Live food: abhorrent / acceptable / revered
- Host-grown food: abhorrent / acceptable / exalted
- Protected species consumption: forbidden / neutral / prestigious
- Slaughter: normal / ritualized
- Hutt excess cuisine: decadent / admired
- Fermentation: ordinary / sacred

## Hospitality / Gastronomy

Guest-facing facilities could add:
- entertainment value;
- restaurant beauty;
- dish markup;
- faction-specific appeal.

---

# 12. A sane implementation slice

The full design is intentionally excessive.

A first husbandry release could focus on **10 systems that are mechanically different**:

1. **Bantha Shade Corral** — conventional desert dairy/wool ranch.
2. **Kod'yok Snow Paddock** — frostside multipurpose livestock.
3. **Puffer-Pig Mooring Yard** — inflatable livestock + mineral prospecting.
4. **Gorg Wet Pit** — tiny fast-breeding restaurant animal that sometimes eats wiring.
5. **Rikknit Climbing Orchard** — vertical crustacean + nonlethal egg-sac harvest.
6. **Sparkbee Flare Hive** — honey culture.
7. **Fleek-Eel Pipe Farm** — compact aquaculture.
8. **Yobshrimp Lantern Tank** — live cocktail seafood + escape comedy.
9. **Mynock Vacuum Blister** — electricity-fed livestock/parasite farm.
10. **Mudhorn Grotto** — rare dangerous egg-producing trophy beast.

Those ten already cover:
- normal ranching;
- hot biome;
- cold biome;
- tiny animal culture;
- vertical husbandry;
- hive management;
- aquaculture;
- live-food handling;
- truly alien power-fed biology;
- dangerous rare breeding.

Everything else can be layered in after those systems prove fun.

---

# 13. Strongest design principle

The player should periodically find themselves saying things like:

> “Don't open that freezer; the caviar is breeding.”

> “We need to shut down the south battery bank because the mynocks got out.”

> “The kod'yoks are in rut, so don't send anyone with Animal 3 into that paddock.”

> “Why are there gorgs in the fabrication bench?”

> “Do not serve the last mudhorn egg. That's our breeder.”

> “Apparently the smell from the sandmaggot ferment has attracted something from the desert.”

> “The puffer pig is on the roof again.”

That is the target tone: **culinary production as ecology, logistics, comedy, danger, and emergent story**, rather than another list of recipes.
