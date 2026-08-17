# Star Wars RimWorld Xenohusbandry Buildings
## Sprite briefs, KOTOR-material costs, vanilla fallbacks, footprints, and placement rules

**Design status:** Art/build-def proposal; intentionally broad  
**Target:** RimWorld 1.6, Star Wars desert-world culinary/xenohusbandry expansion  
**Companion files:**  
- `star_wars_rimworld_cuisine_brewing_overcomplete_design.md`
- `star_wars_rimworld_xenohusbandry_aquaculture_event_design.md`

---

# 1. Important assumptions

The costs below are **proposed balance costs**, not costs copied from an existing mod.

The current **Star Wars KotOR Resources and Materials** mod supplies useful building materials including **Durasteel, Bronzium, Cortosis, Mandalorian Iron/Beskar, Rhydonium, Stygium crystals, Armorweave, Duracrete, Ultra Components**, and related resources. It also optionally changes the availability/stats of vanilla plasteel.

Reference:  
https://steamcommunity.com/sharedfiles/filedetails/?id=3254370945

## Material vocabulary used here

### Routine construction

- **Duracrete** — foundations, basins, retaining walls, pits, troughs, thermal mass.
- **Durasteel** — frames, gates, machinery housings, tank bands, rails.
- **Bronzium** — valves, pipes, corrosion-resistant fittings, decorative KOTOR-looking machinery.
- **Armorweave** — shade sails, nets, flexible containment, straps.
- **Components** — ordinary pumps, motors, sensors, refrigeration.
- **Ultra Components** — reserved for late-game automated/pressure/vacuum/biotech systems.

### Rare strategic materials

These should **not** disappear into routine livestock construction:

- **Cortosis** — optional upgrade where special energy resistance is mechanically meaningful.
- **Mandalorian Iron / Beskar** — optional extreme-containment gate/liner, not baseline husbandry.
- **Stygium** — no ordinary husbandry use.
- **Rhydonium** — fuel/process resource, not structural metal.
- **Tibanna** — process/gas resource, not routine construction.

That keeps rare Star Wars strategic resources exciting.

## Vanilla fallback language

When the KOTOR resource mod is absent:

- Duracrete → **stone blocks** (usually sandstone/limestone/granite) or steel where appropriate.
- Durasteel → **steel**.
- Bronzium → **steel** or **plasteel** for corrosion/high pressure.
- Armorweave → **cloth** or **devilstrand**.
- Ultra Components → **advanced components**.
- Extreme reinforced KOTOR upgrade → **plasteel + uranium**.

---

# 2. RimWorld art direction

## Overall rendering

Each sprite should read correctly at normal game zoom before it looks pretty when enlarged.

- Top-down/orthographic silhouette.
- Broad forms; avoid tiny photorealistic piping.
- One strong identifying motif per building.
- Dark outline/shadow under major forms.
- Visible grime, patch plates, scorch marks, mineral crust, fabric repairs.
- Small Star Wars control panels and indicator lights, but never enough to turn the sprite into visual noise.
- Working machinery should feel **used**, not Naboo-clean.
- Prefer asymmetry: one patched tank, mismatched valve, crooked shade cloth, replacement panel.
- Integrate local desert color: pale dust, rusty iron oxide, salt white, faded canvas, occasional saturated blue/green liquid.
- KOTOR industrial shapes: ribbed cylinders, bronze/copper fittings, heavy geometric housings, small luminous readouts.

## Animation overlays

Do not redraw entire animated buildings where a small overlay will suffice.

Useful overlays:
- water shimmer;
- bubbles;
- rotating fan/pump;
- blinking status lamps;
- pulsing heat coil;
- small moving silhouettes inside tanks;
- steam/frost;
- dangling shade cloth;
- insects around lamps;
- elastic tether movement;
- moving cable/current in mynock systems.

## Damage state

At 50% HP, favor:
- bent rails;
- cracked Duracrete;
- leaking pipe;
- torn net;
- dead indicator lights;
- temporary clamps/patch plates.

At very low HP:
- exposed wiring;
- water leak;
- broken containment warning stripe;
- animal-escape chance may increase if mechanically appropriate.

## Footprints

The dimensions below are gameplay proposals, not art mandates.

For large husbandry systems, use:
- **small anchor building + animal zone/terrain requirement**
rather than painting an entire corral into one sprite.

---

# 3. Conventional ranch infrastructure

| Building | Footprint | RimWorld-style graphic brief | KOTOR-resource cost | Vanilla fallback | Placement / gameplay restrictions |
|---|---:|---|---|---|---|
| **Bantha Shade Corral** | 3×2 anchor + pen | Four thick Duracrete posts, two bent Durasteel crossbeams, huge faded Armorweave awning with long wool tufts snagged along one rail; blue moisture line feeding a trough edge. | 70 Duracrete, 45 Durasteel, 25 Armorweave, 1 Component | 90 stone blocks, 55 steel, 30 cloth, 1 Component | Outdoors or under constructed canopy only; must touch a valid pen; minimum 25 unroofed pen tiles; provides heat protection rather than full enclosure. |
| **Moisture Trough** | 2×1 | Low oval Duracrete basin, blue mineral residue, tiny condenser pipe and float valve; visibly wet interior. | 25 Duracrete, 10 Bronzium | 30 stone blocks, 12 steel | Must be in/adjacent to pen; cannot freeze solid without reduced function; requires water connection if hydration mod active, otherwise consumes power or periodic hauled water. |
| **Bantha Grooming Frame** | 2×2 | Heavy A-frame with blunt comb teeth, hanging wool catcher bags, one side padded with battered leather/Armorweave. | 35 Durasteel, 15 Armorweave, 1 Component | 45 steel, 20 cloth | Must be accessible from pen; one clear interaction cell on both sides; animals voluntarily use it when comfortable. |
| **Nerf Dairy Stall** | 3×2 | Narrow shaded lane, squat milking machinery, stainless/Durasteel side rails, two pale milk canisters, short refrigerated hose with green lamp. | 55 Durasteel, 20 Duracrete, 10 Bronzium, 2 Components | 70 steel, 25 stone blocks, 2 Components | Indoors or roofed; must remain clean; best 0–25°C; requires pen access and powered refrigeration for bonus yield/shelf life. |
| **Shaak Round Pen Hub** | 2×2 + pen | Central circular feed mound surrounded by low radial rails, orange-brown scuff marks and several horn-height scratches. | 35 Durasteel, 25 Duracrete | 45 steel, 30 stone blocks | Outdoors; must be inside a pen; large clear radius preferred; reduces panic if animals have open space. |
| **Kod'yok Snow Paddock Shelter** | 3×3 anchor + pen | Chunky black insulated shelter with white frost lip, orange heat lamp under roof, wool hanging from rounded windbreak edges; snow-packed entrance. | 65 Durasteel, 60 Duracrete, 20 Armorweave, 2 Components | 80 steel, 70 stone blocks, 25 cloth, 2 Components | Best below 5°C; becomes inefficient above 15°C; must touch pen; windbreak bonus outdoors; refrigeration not required on frostside. |
| **Eopie Lean-To** | 2×2 | Crooked scrap-metal sunroof over hitch rail, tiny feed box, hanging water skin/canister; intentionally homestead-scale. | 25 Durasteel, 15 Duracrete, 10 Armorweave | 30 steel, 20 stone blocks, 15 cloth | Outdoors; within pen; no heavy terrain requirement; low-tech and buildable early. |
| **Ronto High Yard** | 3×3 anchor + large pen | Towering four-post frame whose shadow sells height; enormous overhead awning, high-mounted feed basket, reinforced ankle-height barriers. | 100 Duracrete, 90 Durasteel, 40 Armorweave, 2 Components | 130 stone blocks, 110 steel, 50 cloth, 2 Components | Requires ≥50 connected pen tiles, no roof over central interaction area, 3-tile clear approach; cannot be placed under low cave roof. |
| **Ronto Loading Gantry** | 2×3 | Elevated grated platform with ladder, side crane arm and yellow safety rail; one dangling cargo sling at ronto-back height. | 65 Durasteel, 20 Duracrete, 2 Components | 80 steel, 25 stone blocks, 2 Components | Adjacent to Ronto High Yard or caravan packing spot; 3 clear tiles on animal side; no ceiling/rock overhead. |
| **Dung Fuel Press** | 2×2 | Squat mechanical screw press, dirty hopper, rows of rectangular brown fuel cakes drying on side rack; intentionally ugly. | 40 Durasteel, 15 Bronzium, 2 Components | 50 steel, 2 Components | Roof optional; should create filth/odor; dry environment boosts speed; cannot operate in rain unless roofed. |

---

# 4. Pit, burrow, and trench husbandry

| Building | Footprint | Graphic brief | KOTOR-resource cost | Vanilla fallback | Placement / restrictions |
|---|---:|---|---|---|---|
| **Deep-Beast Pit** | 5×5 anchor/terrain system | Illusion of a sunken black center surrounded by thick cracked Duracrete retaining wall; inner edge lined with inward Durasteel teeth; one retractable feeding bridge. | 220 Duracrete, 100 Durasteel, 4 Components | 260 stone blocks, 130 steel, 4 Components | Heavy/solid terrain only; outdoors or mountain opening; ≥2 tiles from ordinary buildings; only one gate side; dangerous fauna containment. |
| **Sandmaggot Dune Bed** | 4×4 | Raised mound of orange sand with only a few breathing tubes, half-buried mesh perimeter, inspection hatch and egg basket; most livestock invisible. | 45 Durasteel, 25 Armorweave, 20 Duracrete | 55 steel, 30 cloth, 25 stone blocks | Sand/soil terrain only; outdoors; cannot be floored; efficiency improves in high heat; adjacent fermenters increase attraction/escape risks. |
| **Worrt Burrow Bank** | 3×2 | Artificial layered sandstone mound with six black burrow mouths, one bait tray, tiny red capture shutters. | 55 Duracrete, 15 Durasteel | 70 stone blocks, 20 steel | Soil/sand; no constructed floor; roof permitted only if natural cave; burrow mouths require one free tile in front. |
| **Scurrier Warren** | 3×2 | Scrap-pipe maze emerging from sand, tiny doors, seed trays, bits of stolen junk protruding from holes. | 30 Durasteel, 20 Duracrete | 40 steel, 25 stone blocks | Soil/sand; must not be inside sterile room; generates filth; escape chance rises if adjacent to food storage. |
| **Gorg Wet Pit** | 3×3 | Shallow muddy basin with green-brown water, three rock shelves, hanging insect lamp and a crude Jawa-style wire lid. | 40 Duracrete, 20 Durasteel, 1 Component | 50 stone blocks, 25 steel, 1 Component | Requires water supply or regular hauling; 10–40°C; cannot be sterile-floored; electrical equipment within 4 tiles is at risk during escapes. |
| **Vel-Slug Run** | 4×1 | Long glazed ceramic trench, translucent slime sheen, grated feeding slots, high inward-curving walls. | 55 Duracrete, 20 Bronzium | 70 stone blocks, 25 steel | Roofed/humid room preferred; requires ≥5°C; cannot share clean kitchen room without cleanliness penalty. |
| **White-Worm Cabinet** | 2×1 | Upright bank of six glass/metal drawers, warm amber glow, wriggling pale lines visible through windows. | 25 Durasteel, 10 Bronzium, 1 Component | 35 steel, 1 Component | Indoors; powered; 18–32°C ideal; catastrophic escape event if destroyed or left unmaintained. |
| **Trufflite Bed** | 3×2 | Low terrarium of dark rich substrate under domed humidity cover, faint fungus glow, miniature feeding dishes; looks expensive rather than industrial. | 35 Durasteel, 20 Duracrete, 15 Bronzium, 2 Components | 45 steel, 25 stone blocks, 2 Components | Indoors; requires humidity/temperature control; clean-room bonus; cannot tolerate freezing or extreme heat. |
| **Keebada Hazard Vat** | 2×2 | Tall cream ceramic vat with clamped black lid, twin glove ports, warning triangle, red pressure lamp and side drain. | 45 Durasteel, 25 Duracrete, 15 Bronzium, 2 Components | 60 steel, 30 stone blocks, 2 Components | Indoors/roofed; requires Cooking or Animals skill threshold to safely harvest; cannot be adjacent to beds/dining tables without mood penalty. |
| **Duraslug Masonry Crib** | 3×2 | Waist-high containment basin holding stacks of sacrificial Duracrete blocks visibly gnawed into scallops; slime drain at one end. | 70 Duracrete, 25 Durasteel | 85 stone blocks, 35 steel | Must have mineral feed stockpile nearby; never adjacent to structural walls if player values safety; escapees target stone/concrete structures. |

---

# 5. Aquaculture

| Building | Footprint | Graphic brief | KOTOR-resource cost | Vanilla fallback | Placement / restrictions |
|---|---:|---|---|---|---|
| **Brine Raceway** | 5×2 | Two long turquoise channels with central pump spine, white salt crust, narrow Durasteel grates and one bubbling inlet. | 90 Duracrete, 45 Durasteel, 15 Bronzium, 2 Components | 110 stone blocks, 60 steel, 2 Components | Flat terrain; powered; water/brine source; outdoors or roofed; temperature depends species; channels cannot be walked through. |
| **Paddy-Frog Rackpond** | 3×2 | Three shallow stacked trays, bright aquatic weeds, dozens of tiny egg pearls, side ladder and insect lamp. | 35 Durasteel, 25 Duracrete, 10 Bronzium, 1 Component | 45 steel, 30 stone blocks, 1 Component | 12–35°C; needs water; one clear harvest side; benefits from insect feed. |
| **Yobshrimp Lantern Tank** | 2×2 | Tall luminous cyan aquarium, thick rounded corners, visible pink/orange shrimp specks, black base with two blinking buttons. | 40 Durasteel, 20 Bronzium, 20 Duracrete, 2 Components | 50 steel, 20 plasteel, 2 Components | Powered; indoors recommended; guest-facing beauty bonus; must stay within species temperature range; destruction releases live shrimp. |
| **Fleek-Eel Pipe Farm** | 3×2 | Three fat coiled dark pipes mounted horizontally, inspection portholes with eel silhouettes, drain tray and valve wheel. | 50 Durasteel, 30 Bronzium, 2 Components | 65 steel, 2 Components | Powered pump; roof optional; requires water source; one drainage cell kept clear; escape may use plumbing network. |
| **Mollusk Basket Line** | 4×1 | Four submerged mesh baskets hanging from a narrow rail, shell shapes visible through water, tiny winch at end. | 25 Durasteel, 15 Armorweave, 1 Component | 30 steel, 20 cloth, 1 Component | Must overlap shallow water/aquaculture pond or be attached to artificial basin; clean water required. |
| **Redfish Net Pen** | 4×4 zone anchor | Floating square frame with dark mesh below, red/orange fish silhouettes, feed buoy and tiny walkway. | 35 Durasteel, 25 Armorweave, 1 Component | 45 steel, 30 cloth, 1 Component | Natural shallow/deep water or artificial pond; cannot block shore path completely; roe season affected by temperature. |
| **Quekka Conservation Pond** | 5×5 pond anchor | Naturalistic irregular pool edge, reeds, protected nesting shoal, understated blue beacon/permit marker rather than industrial machinery. | 60 Duracrete, 20 Durasteel, 1 Component | 75 stone blocks, 25 steel, 1 Component | Requires soil + water; low stocking density; cannot be packed adjacent to another Quekka pond; protected-species mechanics/permit option. |
| **Deepwater Pressure Tank** | 4×4 | Massive black cylindrical tank viewed from above, four thick pressure ribs, tiny dark viewing window, bronze pipe cluster and safety lights. | 110 Durasteel, 50 Duracrete, 30 Bronzium, 3 Components, 1 Ultra Component | 130 steel, 50 plasteel, 40 stone blocks, 3 Components, 1 Advanced Component | Heavy terrain; powered; indoors/roofed recommended; minimum 2-tile separation from beds; explosive flood/damage risk if destroyed. |
| **Colo Tunnel Aquarium** | 6×5 | Huge dark blue-black pool/tank with artificial stone arches forming tunnels, one ominous orange eye/silhouette occasionally visible, feeder crane on one corner. | 180 Duracrete, 120 Durasteel, 40 Bronzium, 5 Components, 1 Ultra Component | 220 stone blocks, 150 steel, 70 plasteel, 5 Components, 1 Advanced Component | Heavy terrain; powered; ≥3 tiles clearance on feeder side; low light; minimum 10×10 room if indoor; cannot share with ordinary aquaculture. |
| **Roe Incubation Cabinet** | 2×1 | Refrigerated wall cabinet with many translucent trays, little colored labels, frost rim and one tray with obvious embryo dots. | 30 Durasteel, 10 Bronzium, 2 Components | 40 steel, 2 Components | Indoors; powered; can switch **Culinary / Breeding** mode; if above safe temperature, “spoilage” may become hatch event. |
| **Cryo Nursery** | 3×2 | Frost-coated low tanks half-sunk into floor, white vapor, insulated black lid segments, pale blue lights. | 55 Durasteel, 35 Duracrete, 15 Bronzium, 3 Components | 70 steel, 45 stone blocks, 3 Components | Best below 0°C; can exploit natural frostside cold to reduce power; must not exceed species maximum temp. |
| **Mobile Fish Net** | 2×1 packed / deployed zone | Rolled black net bundle when packed; deployed becomes buoy line with triangular floats and hanging mesh. | 20 Durasteel, 25 Armorweave | 25 steel, 30 cloth | Must deploy on natural water edge; temporary structure; can be packed; vulnerable to storms/predators. |

---

# 6. Aerial, inflatable, and aviary structures

| Building | Footprint | Graphic brief | KOTOR-resource cost | Vanilla fallback | Placement / restrictions |
|---|---:|---|---|---|---|
| **Balloon Pasture Mast** | 2×2 | Tall mast implied by long central shadow, circular swivel head and four elastic tethers spiraling outward; warning pennants. | 45 Durasteel, 20 Armorweave, 1 Component | 55 steel, 25 cloth, 1 Component | Outdoors; no roof in 4-tile radius; best on open terrain; wind affects tethered stock. |
| **Puffer-Pig Mooring Yard** | 3×3 anchor + pen | Padded round corner posts, loose overhead safety net and enormous stretchy tethers; one comically oversized empty harness. | 50 Durasteel, 35 Armorweave, 20 Duracrete | 65 steel, 45 cloth, 25 stone blocks | Outdoors; ≥20 open pen tiles; no sharp traps/turrets inside yard; wind event interaction. |
| **Porg Rookery** | 3×2 | Faux cliff face with many rounded nesting holes and tiny white/orange porg shapes; removable egg drawers along bottom. | 60 Duracrete, 15 Durasteel | 75 stone blocks, 20 steel | Against natural/constructed wall preferred; roof okay; cannot be sterile; benefits from nearby water/fish feed. |
| **Loralora Aviary** | 3×3 | Tall mesh tower, flowering branches and hanging feeders; vivid little birds visible as colored marks. | 35 Durasteel, 35 Armorweave, 1 Component | 45 steel, 45 cloth, 1 Component | Outdoors or high-ceiling room; no trees/buildings inside footprint; requires temperature range. |
| **Mykal Sky Corral** | 5×5 | Heavy black net dome with four towering supports, suspended carcass feeder and red danger lamps; shadows imply significant height. | 90 Durasteel, 70 Armorweave, 40 Duracrete, 3 Components | 120 steel, 90 cloth/devilstrand, 50 stone blocks, 3 Components | Outdoors; 2-tile safety perimeter; cannot overlap power lines/tall structures; damaged net creates escape risk. |
| **Hawk-Bat Loft** | 2×1 | Roof-mounted dark roost boxes, guano stains, little egg drawer, wings painted as simple silhouette on side. | 20 Durasteel, 10 Armorweave | 25 steel, 15 cloth | Must be adjacent to wall or built on roof edge; nocturnal sound radius; cannot be in sterile rooms. |
| **Gwayo Nest Tower** | 2×2 | Central mast with stacked circular nest baskets and tiny service balcony; eggs visible in one basket. | 30 Durasteel, 15 Armorweave | 40 steel, 20 cloth | Outdoors; no roof; 2 clear tiles around; exposed to storms. |
| **Flight-Line Post** | 1×1 each; pair required | Tall tapered Durasteel poles with cable spool, padded tether clip and wind pennant. | 20 Durasteel, 8 Armorweave each | 25 steel, 10 cloth each | Must place in pairs 6–20 tiles apart; clear line between posts; outdoors; no roofs/trees blocking line. |

---

# 7. Arboreal rikknit system

| Building | Footprint | Graphic brief | KOTOR-resource cost | Vanilla fallback | Placement / restrictions |
|---|---:|---|---|---|---|
| **Rikknit Climbing Orchard** | 4×4 | Three artificial pale trunks joined by black web frames, upper feeding dishes, reddish crab silhouettes clinging at different heights. | 70 Duracrete, 50 Durasteel, 25 Armorweave | 85 stone blocks, 65 steel, 30 cloth | Requires open vertical space; indoors only in ≥4-tile-high conceptual greenhouse; 1-tile clear perimeter for handlers. |
| **Ovum Harvest Gantry** | 1×4 | Thin elevated catwalk with handrail and two gentle curved handling arms ending in padded clamps; egg collection basket beneath. | 40 Durasteel, 10 Bronzium, 1 Component | 50 steel, 1 Component | Must run along edge of Rikknit Orchard; clear access from one end; nonlethal harvest only while powered. |
| **Web Storage Frame** | 2×2 | Empty lattice panel deliberately covered in layered translucent webbing; small brood boxes clipped to corners. | 20 Durasteel, 15 Armorweave | 25 steel, 20 cloth | Adjacent to orchard; increases comfort/fertility; if overfilled can create pathing/web-cleaning event. |
| **Canopy Feed Lift** | 1×2 | Tiny floor winch with cable vanishing upward into elevated hanging tray; fruit scraps visible in tray. | 20 Durasteel, 10 Bronzium, 1 Component | 25 steel, 1 Component | Adjacent to orchard/aviary; powered; keeps handlers outside dangerous canopy during feeding. |

---

# 8. Hive and microfauna equipment

| Building | Footprint | Graphic brief | KOTOR-resource cost | Vanilla fallback | Placement / restrictions |
|---|---:|---|---|---|---|
| **Sparkbee Flare Hive** | 2×2 | Three metallic hexagonal hive boxes around a glowing amber central vent; occasional tiny light motes around openings. | 30 Durasteel, 10 Bronzium, 1 Component | 40 steel, 1 Component | Outdoors/greenhouse; needs flowering plants or Nectar Trough; too hot/cold reduces yield; disturbance can provoke swarm. |
| **Nectar Trough** | 1×1 | Shallow bronze dish with glowing syrup, flower-like emitter vanes and a few bee motes. | 8 Bronzium, 5 Durasteel | 15 steel | Within 5 tiles of hive; consumes sugar/fruit syrup; increases honey yield but may attract wild insects. |
| **Brood Heat Plate** | 1×1 | Flat cream ceramic square with red-orange concentric heating lines and a tiny thermostat. | 10 Durasteel, 1 Component | 12 steel, 1 Component | Indoors/under hive; powered; boosts reproduction but raises swarm/overpopulation risk. |
| **Insect Protein Bin** | 2×1 | Ventilated black crate full of crawling silhouettes and vegetable scraps; mesh lid and scoop attached. | 15 Durasteel, 10 Armorweave | 20 steel, 12 cloth | Roofed recommended; creates smell/filth; feed source for gorg/frogs/insectivores. |
| **Larval Sorting Table** | 2×1 | Fine white trays, small brushes/tongs, labeled breeder and kitchen jars; one magnifying lamp. | 20 Durasteel, 1 Component | 25 steel, 1 Component | Indoors; cleanliness improves yield; requires Cooking/Animals work type depending recipe. |

---

# 9. Mynock vacuum/energy husbandry

| Building | Footprint | Graphic brief | KOTOR-resource cost | Vanilla fallback | Placement / restrictions |
|---|---:|---|---|---|---|
| **Mynock Vacuum Blister** | 3×3 | Bulging black-translucent dome bolted to a heavy ring, mynock silhouettes clinging inside, exterior frost and warning strips. | 75 Durasteel, 35 Duracrete, 25 Bronzium, 3 Components, 1 Ultra Component | 90 steel, 40 plasteel, 40 stone blocks, 3 Components, 1 Advanced Component | Must be on exterior wall/ship hull or special vacuum pad; powered; cannot be in ordinary occupied room; breach releases mynocks. |
| **Sacrificial Power Bus** | 1×3 | Ridiculously thick exposed orange/yellow cables between armored terminals, visible arcing inside protective cage. | 30 Durasteel, 20 Bronzium, 2 Components | 40 steel, 2 Components | Must connect to power grid and Mynock Blister; consumes electricity as animal feed; creates short-circuit risk when damaged. |
| **Mynock Incubator** | 2×2 | Suspended circular coil cage with one or two young mynocks wrapped around glowing conductors; clear growth gauge. | 45 Durasteel, 20 Bronzium, 2 Components | 60 steel, 2 Components | Powered; must connect to Vacuum Blister or vacuum room; higher wattage accelerates replication and risk. |
| **Hull-Scrap Feeder** | 2×1 | Rack of bent ship plates, cut cables and burned components; visible bite/scorch marks. | 15 Durasteel | 20 steel | Adjacent to Mynock system; accepts scrap/slag; reduces chance animals attack useful equipment. |
| **Quarantine Airlock** | 2×3 | Compact double-door module with red lamps, tiny purge cylinder and stencil of a mynock crossed out. | 55 Durasteel, 20 Duracrete, 10 Bronzium, 2 Components | 70 steel, 30 stone blocks, 2 Components | Required entrance for staffed vacuum husbandry room; only functional when both doors not open simultaneously; can emergency-purge containment. |
| **Mynock Harvest Cage** | 2×2 | Folding restraint basket with insulated black jaws and bright yellow grab handles; nasty bite marks. | 35 Durasteel, 10 Armorweave, 1 Component | 45 steel, 15 cloth, 1 Component | Adjacent to Vacuum Blister; one clear handler cell; reduces injury during harvest. |

### Optional extreme upgrade: **Beskar Containment Collar**

Not a baseline building. Add-on to Vacuum Blister / Deep-Beast Pit / Acklay Pit.

**Cost:** 8–15 Mandalorian Iron/Beskar + 1 Ultra Component.  
**Fallback:** 40 plasteel + 20 uranium + 1 Advanced Component.

Effect:
- large containment HP bonus;
- greatly reduced catastrophic breach chance;
- absurdly expensive, intentionally so.

---

# 10. Bioculture / host-symbiont facilities

| Building | Footprint | Graphic brief | KOTOR-resource cost | Vanilla fallback | Placement / restrictions |
|---|---:|---|---|---|---|
| **Xenobiotic Clinic** | 3×3 | Rounded sterile surgery pod fused with small glowing creature tanks; pale KOTOR console, articulated surgical arm, drain hoses. | 70 Durasteel, 30 Duracrete, 20 Bronzium, 3 Components, 1 Ultra Component | 90 steel, 40 sterile tile equivalent/stone, 3 Components, 1 Advanced Component | Indoors, roofed, sterile/clean room; power required; same cleanliness logic as hospital surgery. |
| **Brood Implant Cradle** | 2×2 | Reclined padded chair with U-shaped scanner arch, four soft restraints and small vial rack; more clinic than torture device. | 35 Durasteel, 15 Armorweave, 2 Components | 45 steel, 20 cloth, 2 Components | Indoors; adjacent or same room as clinic; requires medicine and skilled operator. |
| **Symbiont Monitor** | 1×1 | Upright console with stylized body silhouette and several colored brood-stage dots; dangling probe cable. | 15 Durasteel, 1 Component | 20 steel, 1 Component | Powered; within clinic/recovery room; reduces surprise-hatch/rejection chance. |
| **Ovum Collection Chair** | 2×2 | Comfortable cantina-like recliner crossed with medical collector; discreet tubing, chilled bottle rack, towel warmer. | 25 Durasteel, 10 Bronzium, 15 Armorweave, 1 Component | 35 steel, 20 cloth, 1 Component | Indoors; clean room preferred; nonlethal harvest; Body Purist/etc. thoughts handled by hediff/ritual logic. |
| **Brood Recovery Bed** | 2×1 | Medical bed with dual heat/cold pads, amber side lamps and soft abdomen-support sling. | 25 Durasteel, 15 Armorweave, 2 Components | 30 steel, 20 cloth, 2 Components | Indoors; powered for best recovery; hospital-like placement. |
| **Emergency Purge Unit** | 2×1 | Brutally functional extractor with sealed transparent specimen jar and bright red lever; deliberately unsettling. | 35 Durasteel, 15 Bronzium, 2 Components | 45 steel, 2 Components | Clinic only; medical skill threshold; emergency extraction can injure host. |
| **Restaurant's Living Pantry** | 2×2 | Beautiful display cabinet with 4 tiny habitat niches, warm colored lamps, ornate Bronzium trim, little handwritten labels. | 25 Durasteel, 25 Bronzium, 1 Component | 35 steel, 15 silver, 1 Component | Indoors; dining/bar room permitted; small species only; provides beauty/restaurant value but containment incident happens in public. |

---

# 11. Specialized dangerous-animal facilities

| Building | Footprint | Graphic brief | KOTOR-resource cost | Vanilla fallback | Placement / restrictions |
|---|---:|---|---|---|---|
| **Refrigerated Mudhorn Grotto** | 5×4 | Artificial cave mouth framed in cracked Duracrete, deep mud pool, shadowed back wall, pale refrigeration coils crusted with frost. | 130 Duracrete, 70 Durasteel, 20 Bronzium, 4 Components | 160 stone blocks, 90 steel, 4 Components | Must be ≤10°C for breeding bonus; requires 2-tile safety setback; mud terrain/wallow required; roof/cave strongly preferred. |
| **Acklay Deep-Beast Pit** | 6×6 | Deeper, more militarized Deep-Beast Pit: black central void, giant claw-scarred rim, feeder crane, triple-latch gate with red lamps. | 280 Duracrete, 150 Durasteel, 6 Components, 1 Ultra Component | 320 stone blocks, 180 steel, 80 plasteel, 6 Components, 1 Advanced Component | Heavy terrain; outdoors; 3-tile safety perimeter; no ordinary doors on inner edge; only high-skill handlers. |
| **Yalbec Stingery** | 4×4 | Low armored insect pen with central carcass hook, curved vertical sting shields and pheromone vent tower. | 85 Durasteel, 60 Duracrete, 25 Armorweave, 3 Components | 110 steel, 75 stone blocks, 35 devilstrand, 3 Components | Outdoors/large enclosure; 2-tile clearance; downwind placement recommended via odor aura, not hard rule. |
| **Spice-Beast Paddock** | 3×3 anchor + pen | Dark red feeding troughs, heat-resistant rails, spice-stained ground and hanging sampler jars; designed for trakkrrrn. | 50 Durasteel, 30 Duracrete, 1 Component | 65 steel, 40 stone blocks, 1 Component | Pen required; feed recipe influences meat potency; high ambient heat increases animal stress. |
| **Mineral Paddock** | 3×3 anchor + pen | Scrap-filled trough, rusted ore chunks, reinforced chewing posts; ideal for droidbreakers. | 45 Durasteel, 25 Duracrete | 60 steel, 30 stone blocks | Requires mineral/scrap feed; should not overlap valuable resource stockpiles; animals may eat dropped metal if hungry. |
| **Cannok Brush Pen** | 3×3 anchor | Messy brush piles, junk toys, slanted containment fence and dangling bait; deliberately chaotic. | 35 Durasteel, 25 Duracrete | 45 steel, 30 stone blocks | Outdoors; omnivore waste feed; loose weapons/items in pen may be consumed/stolen. |
| **Terrafin Rock Yard** | 4×3 | Rock berms and artificial crevices with buried anti-dig mesh visible at edges. | 80 Duracrete, 30 Durasteel | 100 stone blocks, 40 steel | Soil/rock terrain; anti-burrow foundation required; no adjacent unreinforced walls. |
| **Orpali Nursery** | 3×3 | Disturbingly elegant Hutt nursery: warm sand, low heat emitters, gold/bronze feeding bowls, secure translucent cover. | 45 Durasteel, 35 Duracrete, 25 Bronzium, 2 Components | 60 steel, 45 stone blocks, 15 silver, 2 Components | Indoors/roofed; warm; protected/illegal-species events possible; very clean feed. |
| **Heklu Bog Pen** | 4×4 | Shallow muddy bog with raised island, reed clumps and low escape wall; green moisture haze. | 70 Duracrete, 20 Durasteel | 90 stone blocks, 30 steel | Water/mud terrain; 10–35°C; sleep disruption radius during breeding chorus. |
| **Feejay Exotic Pen** | 2×2 | Small ornate shaded enclosure with decorative bronze trim and padded sleeping hollow. | 20 Durasteel, 15 Bronzium, 10 Duracrete | 30 steel, 10 silver, 15 stone blocks | Temperate/controlled environment; fragile juveniles; beauty bonus. |
| **Gargon Marsh Paddock** | 4×4 | Broad wet pen with black water channels, fungus-covered feed mound and tall odor vent. | 65 Duracrete, 30 Durasteel, 1 Component | 85 stone blocks, 40 steel, 1 Component | Wet terrain/water supply; permanent odor aura; predator-attraction events. |
| **Warm Rock Pen** | 3×2 | Sun-heated flat stones between low walls, insect feeder and tiny basking shelters; for sand lizards. | 35 Duracrete, 10 Durasteel | 45 stone blocks, 15 steel | Must receive sunlight or heat-lamp power; cold stops reproduction. |

---

# 12. Protected krayt nesting infrastructure

Krayt dragons should not become cows. The facility should manage a **wild nest**, not own the dragon.

| Building | Footprint | Graphic brief | KOTOR-resource cost | Vanilla fallback | Placement / restrictions |
|---|---:|---|---|---|---|
| **Krayt Nest Beacon** | 1×1 | Tiny sand-colored sensor mast with long-range antenna and huge warning skull stencil around base. | 20 Durasteel, 1 Component | 25 steel, 1 Component | Desert/sand only; must be placed within designated wild krayt nesting zone/event site. |
| **Krayt Bait Winch** | 2×2 | Heavy ground winch dragging bait chain toward canyon edge; partially buried anchor spikes. | 50 Durasteel, 1 Component | 65 steel, 1 Component | Sand/rock, outdoors; ≥8 tiles from colony structures; baiting raises dragon-presence risk. |
| **Egg-Lift Crane** | 2×3 | Low profile telescoping crane, sling cradle shaped for one enormous egg, red emergency release handle. | 60 Durasteel, 20 Bronzium, 2 Components | 75 steel, 2 Components | Only useful at active nest; requires clear route out; harvesting may trigger parent return. |

---

# 13. Variant aquaculture modules

These can reuse Brine Raceway / Net Pen art with colored inserts rather than becoming entirely separate art sets.

| Module | Visual variation | Extra cost | Placement / effect |
|---|---|---|---|
| **Frella Roe Raceway Module** | Soft orange egg-catching screens | 10 Durasteel, 5 Armorweave | Converts raceway toward roe yield; lower meat growth. |
| **Coodler Roe Raceway Module** | Dense white egg trays and refrigeration pipe | 10 Bronzium, 1 Component | Supports culinary/breeding roe modes. |
| **Premium Caviar Raceway Module** | Cleaner black rails, gold/bronze labels, temperature readout | 15 Bronzium, 1 Component | Quality bonus but strict temperature range. |
| **Hammerfish Flow Module** | Larger pump and heavy grate | 20 Durasteel, 1 Component | Higher current; required for strong-swimming fish. |
| **Slaur Swamp Module** | Mud shelf and reed inserts | 20 Duracrete | Converts pond to swamp-style roe habitat. |
| **Cephalopod Enrichment Module** | Maze pipes, colored puzzle doors, hanging shell toys | 20 Durasteel, 1 Component | Reduces intelligent-cephalopod escape chance. |

---

# 14. Restaurant-facing display variants

These are cosmetic/functional upgrades for Gastronomy/Hospitality-style play.

| Upgrade | Graphic | Cost | Effect |
|---|---|---|---|
| **Guest Viewing Glass** | Clean dark window strip + warm accent light | 15 Bronzium, 15 Durasteel | Beauty/restaurant-value increase for tanks/hives. |
| **Batuuan Hand-Painted Sign** | Rough sign plate with Aurebesh-like markings and creature silhouette | 5 Durasteel or 10 wood | Menu/ambience; negligible mechanical cost. |
| **Hutt Luxury Trim** | Gold-bronze edging, red cushions, dangling lamps | 20 Bronzium, 15 cloth | Hutt guest appeal; beauty. |
| **Jawa Kludge Kit** | Mismatched patch plates, exposed wire, salvaged indicator lamps | 10 Durasteel, 1 Component | Lower rebuild cost after damage; uglier to Core guests, appealing to Jawas. |
| **Mon Cala Wetbar Fascia** | Smooth blue-green ceramic trim, shell motifs | 20 Duracrete, 10 Bronzium | Aquaculture restaurant beauty. |
| **Mandalorian Field Retrofit** | Minimal dark armored panels and tie-downs | 20 Durasteel, 10 Armorweave | Higher HP; lower beauty but faction preference. |

---

# 15. Placement-rule philosophy

Hard restrictions are most fun when players can **see why** they exist.

## Good hard restrictions

- “Must be outdoors.”
- “Must touch shallow water.”
- “Requires sand/soil.”
- “Cannot be roofed.”
- “Requires 2-tile safety clearance.”
- “Must connect to a pen.”
- “Must remain below 10°C.”
- “Must be on a powered grid.”
- “Must be paired with another post.”
- “Must attach to a wall/hull.”
- “Requires natural rock/cave or artificial grotto.”

## Better as soft penalties than hard restrictions

Avoid arbitrary placement bans for:
- odor;
- aesthetics;
- proximity to kitchen;
- proximity to bedrooms;
- faction sensibilities.

Instead:
- odor creates mood radius;
- dirty husbandry lowers room cleanliness;
- animals panic around loud machines;
- predators are attracted by smell;
- guests dislike seeing certain facilities;
- Hutt guests may *prefer* seeing live-food tanks.

That generates stories and player choice.

---

# 16. Suggested art palettes

## Scorchside

- sandstone beige
- bleached Duracrete
- oxide red
- faded ochre canvas
- black solar-baked rubber
- white salt crust
- very small cyan/green indicator lights

## Frostside

- charcoal insulation
- pale steel
- bright frost edge
- dull orange heat lamps
- blue-white vapor
- dark red emergency marks

## Terminator / wet agriculture

- dark wet Duracrete
- bronze plumbing
- muted teal water
- green algae/fungus
- warm amber lamps

## Jawa-built version

- orange/rust brown
- beige scrap
- mismatched dark plates
- exposed cable bundles
- irregular weld seams
- repaired warning paint
- very few pristine surfaces

---

# 17. Suggested graphic-production strategy

To keep the art workload tractable:

## Unique full sprites

Worth bespoke art:
1. Bantha Shade Corral
2. Ronto High Yard
3. Deep-Beast Pit
4. Sandmaggot Dune Bed
5. Gorg Wet Pit
6. Yobshrimp Lantern Tank
7. Fleek-Eel Pipe Farm
8. Colo Tunnel Aquarium
9. Puffer-Pig Mooring Yard
10. Rikknit Climbing Orchard
11. Sparkbee Flare Hive
12. Mynock Vacuum Blister
13. Xenobiotic Clinic
14. Refrigerated Mudhorn Grotto
15. Acklay Deep-Beast Pit
16. Krayt Egg-Lift Crane

## Shared sprite families with overlays

### Raceway family
- Brine Raceway
- Frella
- Coodler
- premium caviar
- hammerfish
- swamp/roe variants

### Small-terrarium family
- White-Worm Cabinet
- Trufflite Bed
- Keebada Vat
- Restaurant Living Pantry

### Aviary family
- Loralora
- Gwayo
- Hawk-bat
- Porg variants

### Pen hub family
- Shaak
- Eopie
- spice beast
- mineral paddock
- Cannok

### Clinic family
- Implant Cradle
- Ovum Chair
- Recovery Bed
- Purge Unit

This could reduce dozens of proposed defs to roughly **20–25 genuinely distinct art assets plus overlays and recolors**.

---

# 18. Best first-wave buildings

If the goal is maximum visual/gameplay diversity with minimum art count, I would start with:

1. **Bantha Shade Corral** — establishes Star Wars ranching.
2. **Kod'yok Snow Paddock Shelter** — makes the frostside culinary.
3. **Puffer-Pig Mooring Yard** — immediately funny and mechanically unique.
4. **Gorg Wet Pit** — tiny restaurant-scale farming.
5. **Rikknit Climbing Orchard** — vertical egg husbandry.
6. **Sparkbee Flare Hive** — high-value sweetener chain.
7. **Fleek-Eel Pipe Farm** — unmistakably non-vanilla aquaculture.
8. **Yobshrimp Lantern Tank** — live restaurant food.
9. **Mynock Vacuum Blister** — electricity-fed animal production.
10. **Refrigerated Mudhorn Grotto** — rare dangerous trophy ranching.
11. **Roe Incubation Cabinet** — supports the “spoiled caviar hatched” event family.
12. **Dung Fuel Press** — closes the ranch economy with a useful waste product.

Those twelve alone would visually communicate that this is a **xenohusbandry mod**, not merely another animal pack.
