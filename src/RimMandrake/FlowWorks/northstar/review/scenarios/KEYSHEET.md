# FlowWorks composite review scenarios - key sheet

Load **RM_fw_walkthrough_20261022** (map C) and **RM_fw_scenarios_rivers_20261021 (not saved yet)** (map R: C1, C11). Paused at 10:00, god mode on, clear weather, Peaceful, Mod Settings at shipped defaults. **Every plot is still until your first poke: its START.** Reload the save to reset. Raids live in **RM_fw_composite_raid**, rain in **RM_fw_composite_rain** (load the branch, never the main save, for those pokes).

Each scenario has a gold title label (number, name, START, what to look for), its try lines under the plot, small rust labels on every part a poke touches, violet **DEFERRED** labels on every piece not built yet, and in-save sign books (a Novel; mouse over it, press i) at its north-west corner and at each DEFERRED piece - the books survive a plain load with no agent.

Tonight's rulings carried: colonists dig to 2 m; deeper holes are machine-dug (mechanoids and droids dig to 20 m, built 2026-10-21; the ridable digging rig is not built: DEFERRED); pipes half as thick and hoses twice the 10-21 girth (owner 2026-10-22 00:00), both built; a FLOWING hose still draws too thin (HOSE_PLUMP_FIX_SKINNIER_WHEN_FULL); canal overflow ships in 1.0 but only Stage 0 (offline kernel) exists: DEFERRED; reachability option 3 is being built separately (REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE); a fallen cord lands walkable (fix built).

| # | scenario | map | plot (x,z,w,h) | look | staged / DEFERRED | goto |
|---|---|---|---|---|---|---|
| C1 | The Thirsty Terraces | R | river-anchored (live) | all four | 15 / 3 | `--goto C1` (map R: framed by `--river --build`; goto on map R owed) |
| C2 | The Drowned Keep | C | (62, 62, 44, 44) | Industrial | 19 / 5 | `--goto C2` |
| C3 | The Labyrinth Rescue | C | (12, 12, 40, 40) | Scrapper | 20 / 3 | `--goto C3` |
| C4 | The Wet Quarry | C | (12, 62, 40, 40) | Industrial | 14 / 2 | `--goto C4` |
| C5 | The Fuel Depot | C | (112, 12, 40, 36) | Industrial | 13 / 3 | `--goto C5` |
| C6 | The Tar Seep | C | (162, 12, 40, 36) | Scrapper | 9 / 2 | `--goto C6` |
| C7 | The Bathhouse and Water Tower | C | (12, 112, 40, 40) | Modern | 13 / 2 | `--goto C7` |
| C8 | The Canal Lock | C | (112, 62, 44, 24) | Futuristic | 11 / 3 | `--goto C8` |
| C9 | The Trench Line | C | (162, 62, 44, 32) | earthworks | 9 / 3 | `--goto C9` |
| C10 | The Rain Basin | C | (196, 112, 44, 40) | land and water bodies | 11 / 3 | `--goto C10` |
| C11 | Prospector's Creek | R | river-anchored (live) | Scrapper | 9 / 2 | `--goto C11` (map R: framed by `--river --build`; goto on map R owed) |
| C12 | The Oubliette and the Kennel | C | (62, 12, 40, 36) | Modern | 15 / 2 | `--goto C12` |

Specials: **S0** status board (12, 170, 40, 20), **F** free area (110, 112, 40, 24), **Z0** Stage 0 swim site (62, 140, 8, 12).

## C1 - The Thirsty Terraces (map R, look all four)

Grow a crop on dry ground three steps above a river: caught, lifted, carried over a ditch, stored, let down terrace by terrace, and sprayed. The field greens only if every link works.

**START:** open sluice S1 (terrace 1's tail)

**Try:**

1. START: open S1: terrace 2's front runs along it
2. unpause an in-game hour: every sprinkler in all four rows sprays (the spray mote centred on its pipe); sprayed cells stay wet till the next spray - read the inspect pane and the crop's yield, NOT a ground tint (ruling 36: no irrigation line)
3. open S2: the front runs along terrace 3; after days (branch save _days) the sand by the swale turns to soil
4. switch the bank pump to Pour, OR (separately) cut its power: the sprinklers stop on the next hour; the remote hose goes flat
5. select the meter on terrace 1: squares, levels held, net in/out per day; shut S1 and watch it turn
6. deconstruct one pipe pole: the overhead span is gone and the pipe can no longer cross the ditch
7. watch the labelled WITNESS sprinkler: the canal feed and the sprinkler circuit are separate nets

**Look for:** sprinklers centred on their pipe; pipes meet the tank at its centre; the span sags over the ditch, not on its floor; the four looks working side by side

**Broken looks like:** a sprinkler off its pipe's centre; spraying with no pump on the net; a pipe drawn through the tank; the overhead pipe on the ditch floor or without sag; terrace 3 wet with S2 shut; a hose crossing that is not clean over/under

**Still until poked:** S0 shut (terrace 1 full), S1 and S2 shut (terraces 2 and 3 dry); the pump fills the tall tank in Fill mode and the heads spray on the hour (that IS the scenario; the soak reads dug cells and buildings)

**Branch saves:** RM_fw_composite_rivers_days: sand to soil by the swale

| piece | status | tag | note |
|---|---|---|---|
| weir on the bank (Scrapper) | staged | look |  |
| intake channel behind S0 | staged | demonstrated |  |
| terrace 1 canal, full | staged | demonstrated |  |
| S1 at terrace 1's tail, shut | staged | poked |  |
| terrace 2 canal, dry | staged | poked |  |
| S2, shut; terrace 3 dry | staged | poked |  |
| crop rows between the terraces | staged | look |  |
| bank pump Drawing, powered | staged | poked |  |
| pipe poles + overhead span over the dry ditch | staged | poked |  |
| tall tank, Fill, about 40 % | staged | demonstrated |  |
| four sprinkler rows, one per look | staged | look |  |
| flow meter on terrace 1 | staged | poked |  |
| sand + swale strip on terrace 3 | staged | poked |  |
| remote field hose (Industrial), Plump | staged | look |  |
| a second hose crossing it at right angles | staged | look |  |
| overflow onto the field (D2/D3) | DEFERRED | DEFERRED | Stage 1+ unbuilt; terrace 1's brim is one notch from spilling, so leaving S1 shut with the pump on will spill once it lands - builds under `CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED` |
| flowing hose girth, joint flanges | DEFERRED | DEFERRED | pipes are half-girth and hoses twice the 10-21 girth (both built 2026-10-22); a flowing (plump) hose still draws thinner than an empty one, and pipe/hose joints have no flanges yet (HOSE_PLUMP_FIX_SKINNIER_WHEN_FULL, PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID) - builds under `HOSE_PLUMP_FIX_SKINNIER_WHEN_FULL` |
| terrace 2's front frozen half way | DEFERRED | DEFERRED | a canal levels itself: no frozen half front survives the soak; staged dry, opening S1 shows the front - builds under `design §3 C1 (deviation)` |

Exercises (17 ids): 5 poked, 12 look.

Goal read: live: ProofLinkPoles reads strung=True; the tall tank's stock rises over the soak (the pump is on the net)

## C2 - The Drowned Keep (map C, look Industrial)

A walled keep inside a water moat: the classic defence, built only from FlowWorks parts, with a nasty gatehouse.

**START:** (raid branch save RM_fw_composite_raid) open the raiders' pen grate and unpause

**Try:**

1. main save: walk a colonist over the grated suspension bridge across the west moat arm and out the jetty; swim under the deck (live 2026-10-21: a span must cross dug ground only, so it cannot also span the dry ditch)
2. RAID BRANCH START: open the pen grate, unpause: raiders reach the ditch and moat, lay the plank or swim (2 m: heads and shoulders up), climb, and try the gate (it stays shut to hostiles)
3. lower the drawbridge (its winch) mid-raid: the leaf drops; the gate still refuses unless held open; let one raider onto the gatehouse concealed pit: he drops onto the spikes
4. open the gatehouse grate and sluice: the trapped raider's pit floods from the moat; read swim vs drown in the inspect pane
5. light the chemfuel arm (dev fire at 'light here'): it goes up like gasoline; the grated deck lets the heat up
6. cut the winch's power (ProofWinchPower off; the GSS cord is DEFERRED): the leaf holds where it is

**Look for:** the concealed pit invisible at play zoom with a slight seam at max zoom; the bridge reads HUNG, not a pier; raiders swim, never walk the moat floor

**Broken looks like:** the concealed pit visible at play zoom, or NO seam at max zoom; the concealed pit reading like a bridge; raiders walking on the moat floor; the gate opening for raiders while the leaf is up; a raider unhurt on the spikes; the bridge drawn as a pier-on-pylons; the sluice open but the pit dry

**Still until poked:** main save: no hostiles; the moat brim-full and closed; the leaf raised and held by a powered winch; every sluice and grate shut; nothing lit; the two defenders drafted

**Branch saves:** RM_fw_composite_raid: four raiders in the north pen, grate shut

| piece | status | tag | note |
|---|---|---|---|
| dry outer ditch | staged | look |  |
| 2 m water moat ring | staged | demonstrated |  |
| keep walls | staged | look |  |
| drawbridge gate in the wall | staged | poked |  |
| drawbridge leaf + winch over the east arm | staged | poked |  |
| winch powered | staged | demonstrated |  |
| leaf raised | staged | poked |  |
| gatehouse pit 3x3, 4 m, spikes | staged | poked |  |
| concealed pit (planks) over it | staged | poked |  |
| channel from the moat: grate + sluice | staged | poked |  |
| guardrail on the gatehouse lip | staged | look |  |
| rail ladder in the gatehouse pit, raised | staged | poked |  |
| south drain grate | staged | look |  |
| chemfuel north arm behind two sluices | staged | poked |  |
| grated suspension bridge over the west arm | staged | poked |  |
| jetty over the west arm | staged | poked |  |
| two defenders, drafted | staged | demonstrated |  |
| raiders in a pen behind a shut grate (raid branch) | staged | poked |  |
| a raid plank in the pen | staged | poked |  |
| doors leaking slowly under water (D4): the postern | DEFERRED | DEFERRED | overflow Stage 1+ unbuilt; the postern sits by the moat so it shows once it lands - builds under `CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED` |
| the winch's GSS power cord (cut it) | DEFERRED | DEFERRED | ProofWinchPower forces power; no script lays an RM_PowerCord - builds under `POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS` |
| machine digging the 4 m gatehouse pit | DEFERRED | DEFERRED | past the 2 m colonist cap - builds under `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL` |
| guardrail art | DEFERRED | DEFERRED | a borrowed fence look; a cosmetic change needs his permission - builds under `GUARDRAIL_ART_RESKIN_BORROWED_FENCE` |
| defenders holding fire until drafted (raid branch) | DEFERRED | DEFERRED | no bridge surface: owed - builds under `owed C#` |

Exercises (19 ids): 10 look, 9 poked.

Goal read: live: ProofLeaf on (39,18) reads raised=..., powered=True; ProofSpan on the west bridge reads hung

Owed C#: a fire-at-will/hold-fire bridge surface (raid-branch defenders hold fire until drafted)

## C3 - The Labyrinth Rescue (map C, look Scrapper)

Hobb is in a 4 m sheer pit in the middle of a maze. Float him out: pond water, by hose, through the maze.

**START:** press reel o1's 'Free end' button until it reads Outflow, then unpause

**Try:**

1. START: reel o1 > Free end: Outflow; unpause: the pond shrinks, Hobb's pit fills; at 2 m he swims but is still 2 m below the lip; only near the BRIM (4 m of water) can he swim out (Stage 0 live, 2026-10-21: PASS_AT_BRIM). Select the meter on the pit floor: litres in.
2. BEFORE that: wall the gap d1 (the short way): the hose must re-route the long way (over 40 cells): it reels in with a message naming the cells needed; fix it by laying onto relay reel o2
3. lay o2's hose back onto o1: refused (a relay chain may not loop)
4. try a portable ladder into Hobb's pit: refused, too deep (3 m reach) - that is why the maze exists
5. move o1's hose end to the boar's pit instead: the boar starts drowning (a non-swimmer); draft and cancel
6. cut the pump's power: the hose goes flat; rotate the pump: the hose follows the port
7. reel park (west): choose a style, undraft the colonist to deploy one by hand, retract one

**Look for:** the hose takes the SHORT way through d1 and passes UNDER the wire span; litres out of the pond = litres into the pit; Hobb rises with the water and leaves only when it nears the brim

**Broken looks like:** the hose through a wall, over the chasm or on top of the wire span; the long way chosen while d1 is open; a hose that never plumps; Hobb standing on the floor under 2 m of water; the boar swimming; a relay loop accepted

**Still until poked:** pump on and Drawing into a tank, hose Plump, but o1's free end is Capped: nothing leaves the hose until he sets Outflow; Hobb and the walker are drafted; the boar is penned by its pit

| piece | status | tag | note |
|---|---|---|---|
| pond (limited) | staged | demonstrated |  |
| pump on the pond edge, Drawing | staged | demonstrated |  |
| small tank beside the pump | staged | demonstrated |  |
| battery, charged | staged | demonstrated |  |
| reel o1 laid the short way, Plump, end Capped | staged | poked |  |
| maze walls (Steel) | staged | look |  |
| door gap d1 (short way) | staged | poked | the gap is the cell east of this wall |
| misleading dead end | staged | look |  |
| Hobb's pit 2x2, 4 m sheer | staged | demonstrated |  |
| Hobb, drafted, in his pit | staged | poked |  |
| boar's pit 2x2, 4 m | staged | demonstrated |  |
| boar (non-swimmer) | staged | poked |  |
| chasm (impassable, 6 m) | staged | look |  |
| GSS wire span on two masts (auto-linked by GSS) | staged | look |  |
| relay reel o2, wound | staged | poked |  |
| destination gauge (flow meter) in Hobb's pit | staged | demonstrated |  |
| reel park: four looks | staged | look |  |
| reel park: deploy order + walker | staged | poked |  |
| reel park: dropped carry | staged | look |  |
| pump power as a GSS power cord | DEFERRED | DEFERRED | a vanilla conduit stands in: no staging surface lays an RM_PowerCord from a script yet - builds under `POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS` |
| swim-out of a flooded sheer pit (Stage 0 live: out only at the brim) | staged | poked | Transient/scenarios_stage0_20261021T220318.json: 2 m FAIL, brim PASS |
| machine digging Hobb's pit | DEFERRED | DEFERRED | 4 m is past the 2 m colonist cap (owner 2026-10-21); the pit is staged, a machine dig order is not built - builds under `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL` |
| flowing hose girth | DEFERRED | DEFERRED | pipes are half-girth and hoses twice the 10-21 girth (both built 2026-10-22); a flowing (plump) hose still draws thinner than an empty one, and pipe/hose joints have no flanges yet (HOSE_PLUMP_FIX_SKINNIER_WHEN_FULL, PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID) - builds under `HOSE_PLUMP_FIX_SKINNIER_WHEN_FULL` |

Exercises (32 ids): 16 poked, 16 look.

Goal read: route lengths: short way (d1 open) <= 40 cells, long way (d1 walled) > 40 and <= 80; live: ProofReadout on Hobb's pit for litres-to-2 m, never typed

**Prove first:** `stage0_swim_pit` (Stage 0, live owed).

## C4 - The Wet Quarry (map C, look Industrial)

A quarry dug below the water table: the deeper it goes the more it floods; a pump rig keeps it workable. The dig ladder, rock vs soil, ways in and out, and pumping water up and away.

**START:** mark the drain-canal extension (Architect > Orders > Dig canal along the labelled strip) and unpause

**Try:**

1. START: designate the labelled 70-cell strip, unpause: a colonist digs it; about 1 in 70 dug tiles leaves a lump (a letter the first time); soil digs faster than rock and rock drops chunks
2. the sump floor (3 m) carries a 'Dig canal' order: an undrafted colonist will not take it (2 m colonist cap, owner 2026-10-21; right-click says it needs machine labour) and the order stays for a machine
3. stop the pump (the deliberate flood): the sump rises half a metre at a time from LOW toward HIGH and the workbench; the miner wades, then swims; restart it and the level falls
4. raise the rail ladder from below, lower it from above (only from above); the geared miner climbs a sheer wall anyway
5. walk a colonist down the ramp and the benches: lower with each step, never trapped

**Look for:** dug ground never reads as a gravel path; dirt and rock walls drawn differently; the sump has visible depth; 0.5 m water reads as silt

**Broken looks like:** a dug tile reading as gravel path; dirt and stone walls alike; the sump a flat blue square; the miner standing ON water at 2 m; the ladder lowered from below

**Still until poked:** the pump draws the sump through the hose to the drain canal, which runs off the map edge, against the bleed well's groundwater: the sump stays near LOW (the soak MEASURES whether this balance holds; the build fails if not); the miner is drafted; no dig is designated until he does it

| piece | status | tag | note |
|---|---|---|---|
| stepped benches D1 > D2 > D3 | staged | demonstrated |  |
| rock east / soil west | staged | look |  |
| machine-dug sump, 3 m, water at LOW | staged | demonstrated |  |
| groundwater bleed well into the sump | staged | demonstrated |  |
| pump Drawing on the sump rim | staged | poked |  |
| hose up and away, free end Outflow | staged | poked |  |
| drain canal off the west edge | staged | demonstrated |  |
| three flow meters | staged | demonstrated |  |
| workbench just above HIGH | staged | look |  |
| miner in climbing gear, drafted | staged | poked |  |
| rail ladder on the sump's west wall, lowered | staged | poked |  |
| ramp from the D1 bench to the rim | staged | poked |  |
| wrecked pumping station on the rim | staged | look |  |
| a colonist refusing a dig past 2 m (the sump floor's order waits for a machine) | staged | poked |  |
| machine digging past 2 m (the sump) | DEFERRED | DEFERRED | machine labour digs to 20 m (built 2026-10-21, design/RimMandrake/machine_dig_2026-10-21.md); a colony Tunneler under a mechanitor is not staged here yet, and the ridable digging rig is not built - builds under `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL` |
| deepstone stratum finds | DEFERRED | DEFERRED | unbuilt - builds under `PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS` |

Exercises (21 ids): 10 poked, 10 look, 1 demonstrated.

Goal read: live: the sump's fill after the two-hour soak within one level of LOW (the pump and bleed well balance)

## C5 - The Fuel Depot (map C, look Industrial)

A caravan fuel stop: cargo tanks, a filling bay, a tapped neighbour's tank, a bunded canal and a fire plan - the place that must not burn shows every fire rule by being dangerous.

**START:** set the bay tanks' Job buttons: Store / Fill / Empty (west to east) and the tank by the pump to Dump

**Try:**

1. START: bay jobs Store, Fill, Empty; the pump-side tank Dump; unpause: colonists fill barrels from Empty and pour only into Fill; the Dump tank empties into the containment canal through the pump
2. cycle the adapter Send > Take > Shut and watch the run's stock (needs Vanilla Chemfuel Expanded)
3. select our hose on THEIR tank: tinted chemfuel; its inspect names nobody's faction
4. light the containment canal (dev fire at 'light here'): burns like gasoline, keeps burning, reaches the tank end, leaves the canal spent; pop the firefoam: foamed cells stay out while foam lies
5. light the astrofuel bund: it detonates, not burns
6. dig the marked cell in the earth wall between the water and chemfuel canals: they meet and do NOT mix

**Look for:** chemfuel, propane and water each their own colour; pipes meet tanks at their centre; the Fill tank is never emptied by colonists

**Broken looks like:** chemfuel, propane and water hoses all one colour; a tank drawn bridging two pipe runs; the Fill tank emptied; water and chemfuel mixing; a burnt canal that looks fresh; foamed cells relighting under foam; litres from nowhere

**Still until poked:** every bay tank in Store; the pump is set to Pour but its Dump-side tank is in Store, so nothing flows; the hose to their tank is Plump with its free end Capped; nothing is lit

| piece | status | tag | note |
|---|---|---|---|
| cargo tanks (Futuristic): chemfuel, propane, XTall chemfuel | staged | look |  |
| Industrial pipe run | staged | look |  |
| chemfuel adapter on the run (VCHE) | staged | poked | built only when Vanilla Chemfuel Expanded's def is loaded (live get_defs) |
| filling bay: four tanks | staged | poked |  |
| empty barrels and bottles | staged | look |  |
| containment canal, chemfuel a quarter | staged | demonstrated |  |
| pump set to Pour | staged | poked |  |
| our hose on THEIR tank, Plump | staged | look |  |
| their tank (hostile faction) | staged | look |  |
| astrofuel bund, walled | staged | poked |  |
| firefoam popper by the canal | staged | poked |  |
| water canal one wall from the chemfuel | staged | poked |  |
| spill pad: liquid spill + tracked tar | staged | look |  |
| fuel overflow spreads and burns (D5) | DEFERRED | DEFERRED | overflow Stage 1+ is unbuilt (only the Stage 0 offline kernel exists); the canal stands below its brim so a second Dump will spill once it lands - builds under `CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED` |
| an acid canal beside the chemfuel | DEFERRED | DEFERRED | moved to C6 (where corrosion lives); the no-mix poke needs only water against chemfuel - builds under `design §3 C5 layout` |
| pipe-to-tank flanges | DEFERRED | DEFERRED | pipes are half-girth and hoses twice the 10-21 girth (both built 2026-10-22); a flowing (plump) hose still draws thinner than an empty one, and pipe/hose joints have no flanges yet (HOSE_PLUMP_FIX_SKINNIER_WHEN_FULL, PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID) - builds under `PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID` |

Exercises (24 ids): 14 poked, 10 look.

Goal read: live: the containment canal's chemfuel litres (ProofReadout) and the Dump tank's stock read; their sum is the canal's brim minus one notch

## C6 - The Tar Seep (map C, look Scrapper)

Tar bleeds up, crawls down a ditch, is tracked in on boots, refined, and burns; slime and acid share the yard; water runs beside the tar so you can compare.

**START:** open both race sluices (the tar one and the water one, at the ditches' west ends), then unpause

**Try:**

1. START: open both sluices, unpause: the water front runs, the tar front crawls behind it (watch both)
2. walk a colonist across the slime pit's edge: slow, nearly uncrossable; the muffalo sits below the surface; the earth plank (x middle) is the dry way over
3. light the tar ditch: it burns for days; the refinery stops if its feed burns; dev weather Rain puts it out
4. start the vat: 400 L tar + 200 L acid water per batch meter in; 200 L of product to a third tank if one is on its line, else 40 gas vented (RM_Reaction_TarAcid; the product thing is owed under SUMP_GASLIGHT_1: judge the metering and the vent)
5. watch the acid canal: what lies in it loses health over hours (Mod Settings: Liquid corrosion, ships ON)
6. colonists clean the tracked tar

**Look for:** tar thick and slow beside water; slime reads viscous, the muffalo below its surface; the three refinery stages easy to tell apart

**Broken looks like:** the tar front level with the water's; slime that looks like coloured water; a muffalo standing on top of slime; tar filth with no art; a burning tar ditch out within an hour; corrosion while the switch is off

**Still until poked:** both race ditches are dry behind shut sluices; the vat is not started; corrosion and the tracked tar DO change over two hours (the soak reads dug cells and buildings, not item health or filth)

**Branch saves:** RM_fw_composite_days: the burning ditch a day later

| piece | status | tag | note |
|---|---|---|---|
| tar seep (pond) + drill | staged | look |  |
| tar ditch behind a shut sluice | staged | poked |  |
| water ditch behind a shut sluice (the race) | staged | poked |  |
| tar refinery Wrecked | Kludged | Repaired | staged | look |  |
| green slime pit with a muffalo | staged | demonstrated |  |
| one-cell earth plank across | staged | poked | x 28 is left undug |
| reaction vat between tar and acid tanks | staged | poked |  |
| acid canal with steel and wood | staged | demonstrated |  |
| tracked tar footpath | staged | look |  |
| the vat's product thing | DEFERRED | DEFERRED | owed under SUMP_GASLIGHT_1: judge metering and vent only - builds under `SUMP_GASLIGHT_1` |
| the drill on a survey hit | DEFERRED | DEFERRED | no survey staging surface: the drill sits on the seep pond - builds under `FLOWWORKS_QUARRY_DIGGING_1` |

Exercises (19 ids): 10 poked, 8 look, 1 demonstrated.

Goal read: live: both ditches dry at the start (excavation read f=0 east of the sluices); the slime pit's fill reads 2

## C7 - The Bathhouse and Water Tower (map C, look Modern)

A desert colony's water: a tower tank, gravity down to the ground tanks, a bathhouse, stills for bad water, thirsty colonists - and communicating vessels in plain sight.

**START:** undraft the four thirsty colonists and unpause

**Try:**

1. START: undraft the four, unpause: they drink at the tanks and from bottles; the warden carries water to the prisoner
2. let them build the two missing pipe cells (or place them: Architect > FlowWorks > pipe on the marked gap): the three ground tanks move to ONE level, in decilitre steps
3. set the tower reel's Free end to Outflow: the hose flows to the garden with no pump (gravity) and stops when the tower's level drops below the end
4. run the stills: the fuelled one works day and night; the sun-pan stops at dusk and under a roof
5. pour poisoned water into the drip filter: a slow, small clean drip

**Look for:** pipes end at a tank's CENTRE; tanks on one net hold one level at rest; the bath reads as a bath, not a hole

**Broken looks like:** tanks on one net at different levels at rest; a gravity hose flowing uphill; brine drunk as water; the sun-pan working at night; pipes ending at a tank's edge; the bath pit reading as a hole

**Still until poked:** the four colonists are drafted (drafted pawns do not drink); the ground tanks are not joined; the tower hose's end is Capped; the well pump draws the pond into the tower (the pond is limited, so it slows; the soak reads dug cells and buildings)

| piece | status | tag | note |
|---|---|---|---|
| well pump, Drawing, powered | staged | demonstrated |  |
| tower: XTall cargo tank, half full | staged | demonstrated |  |
| three ground tanks, one per size, NOT joined | staged | poked |  |
| roofed bathhouse, bath pit filled | staged | look |  |
| liquid thermostat keeps the bath warm | staged | demonstrated |  |
| three bleed wells (ground wells, not on the pipe) | staged | poked |  |
| Empty-mode tank + bottles on a shelf | staged | poked |  |
| brine tank > fuelled still > clean tank | staged | poked |  |
| salt tank > sun-pan still | staged | poked |  |
| poisoned barrel + drip filter | staged | poked |  |
| gravity hose from the tower, end Capped | staged | poked |  |
| four thirsty colonists (drafted) | staged | poked |  |
| prisoner in his own cell | staged | demonstrated |  |
| a blueprint for the two missing pipe cells | DEFERRED | DEFERRED | no script surface places a blueprint; the gap is labelled and the pipe is his to place - builds under `TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH` |
| the overflowing bath (D2/D4: leaking under the door) | DEFERRED | DEFERRED | overflow Stage 1+ is unbuilt - builds under `CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED` |

Exercises (15 ids): 6 poked, 8 look, 1 demonstrated.

Goal read: live: the three ground tanks read three different stocks before the gap is closed (ProofTank read)

## C8 - The Canal Lock (map C, look Futuristic)

Two canals at different water levels, a lock chamber between two timed sluices, and a swimmer riding the lock up: one still surface per body, levels equalising only through open gates.

**START:** order the swimmer down the chamber ladder into the water, then unpause and wait for 13:00

**Try:**

1. START: order the swimmer (on the bank) into the chamber; unpause: at 13:00 the S1 timer opens S1; the chamber rises to the upper level and the swimmer rises with it; at 14:30 S1 shuts; at 15:30 S2 opens and the chamber falls to the lower level
2. read the three meters as it happens: net in/out per day, levels held
3. Mode A (closed): open both sluices by hand: the run settles to ONE surface
4. Mode B (through-flow): DEFERRED (no switched-off holder/sink can be staged yet)
5. the separate spur north of the lower canal: 0.5 m reads as silt-coloured shallows, not blue water

**Look for:** gate state legible without selecting; one surface per body; the swimmer rises and falls with the chamber

**Broken looks like:** two levels on one side of an open gate; a gate drawn open while shut (or turning unlike a door); the swimmer standing on the floor; the timer firing at the wrong hours; meters disagreeing with what is drawn

**Still until poked:** both sluices shut; timers first fire at 13:00 (after the 10:00-12:00 soak); the swimmer waits drafted on the BANK (two hours of swimming would tire him: swim exhaustion); a closed system

| piece | status | tag | note |
|---|---|---|---|
| upper canal, 3 m machine-dug, brim-full | staged | demonstrated |  |
| lock chamber, 2 m water | staged | demonstrated |  |
| lower canal, 2 m water | staged | demonstrated |  |
| sluice S1 | staged | poked |  |
| sluice S2 | staged | poked |  |
| timer on S1 | staged | demonstrated |  |
| timer on S2 | staged | demonstrated |  |
| three meters | staged | demonstrated |  |
| swimmer on the chamber bank, drafted | staged | poked |  |
| chamber ladder (the swimmer's exit) | staged | poked |  |
| 0.5 m silt spur | staged | look |  |
| Mode B: level holder + sink switched off | DEFERRED | DEFERRED | Place* builds them ON; an OFF-staged holder/sink needs a toggle proof surface (owed C#) - builds under `FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS` |
| a boat | DEFERRED | DEFERRED | FlowWorks has none: the swimmer is the boat - builds under `design §3 C8` |
| machine-dug 3 m reaches | DEFERRED | DEFERRED | past the 2 m colonist cap; staged by the dig tool - builds under `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL` |

Exercises (12 ids): 3 poked, 7 look, 2 demonstrated.

Goal read: live: the timers read back 13-14.5 and 15.5-17 (static read); upper fill 6, chamber and lower fill 4

Owed C#: a Place* 'off' flag (or a toggle proof) so a level holder and a sink can be staged switched OFF (C8 Mode B, idle-stable)

## C9 - The Trench Line (map C, look earthworks)

A dry trench line facing an open field, the way a desert colony fights: cover, movement cost, shooting from holes, and what raiders do about trenches.

**START:** (raid branch save RM_fw_composite_raid) open the pen's grate and unpause

**Try:**

1. main save: hover a lane: walk cost climbs with depth; the wet bay is slower than a dry chest bay
2. RAID BRANCH: hover a raider's shot at a colonist: the hit chance lists a 'trench wall' cover line, bigger for the chest-deep man
3. RAID BRANCH START: open the pen grate, unpause: raiders cross the tar ditch (slow), hit the trench line, set a ladder or fill a cell to cross, and never shelter in a sheer pocket; the geared raider goes over the north rampart
4. RAID BRANCH: light the tar ditch as they cross
5. the large mechanoid must not step across the 4-wide titan gap

**Look for:** a cover line on the hit chance, larger for chest than waist; raiders never trapped in a pocket

**Broken looks like:** no cover line, or the same for waist and chest; a raider stuck in a pocket; raiders walking over a trench as if flat; the large pawn stepping across the 4-wide gap; the wet bay no slower

**Still until poked:** main save: no hostiles; colonists drafted in the bays; the tar unlit. Raid branch: the pen's shut grate is proven by the build's two-hour soak with the raiders inside

**Branch saves:** RM_fw_composite_raid: the six raiders and the mechanoid in the pen, grate shut

| piece | status | tag | note |
|---|---|---|---|
| zig-zag trench, waist and chest bays | staged | demonstrated |  |
| three colonists in the chest bays, drafted | staged | demonstrated |  |
| wet foxhole bay at 0.5 m | staged | look |  |
| tar ditch, 2 wide, unlit | staged | poked |  |
| 4-wide titan gap | staged | poked |  |
| stone rampart behind the north end | staged | poked |  |
| raider pen behind a shut security grate | staged | poked |  |
| six raiders incl. one with climbing gear (raid branch) | staged | poked |  |
| a large mechanoid (raid branch) | staged | poked | a vanilla centipede stands in for titan size |
| wet foxhole: cold feet, shaky aim | DEFERRED | DEFERRED | unbuilt; the wet bay is placed so it shows once built - builds under `WET_FOXHOLE_BUILD_COLD_FEET_SHAKY_AIM` |
| defenders holding fire until drafted | DEFERRED | DEFERRED | no bridge surface sets fire-at-will off: owed - builds under `owed C#` |
| raider ladder / fill-in rows proven live | DEFERRED | DEFERRED | raid_trench_proof A2-A7 L2 rows must pass first, else he sees known failures (design §5.3) - builds under `RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP` |

Exercises (11 ids): 8 poked, 3 look.

Goal read: live (raid branch): ProofTrenchCover on a chest-bay colonist vs a penned raider returns trench > 0

Owed C#: a fire-at-will/hold-fire bridge surface so raid-branch defenders hold fire until drafted (C2, C9)

## C10 - The Rain Basin (map C, look land and water bodies)

A dry wash that floods: a limited pond, a limitless spring, a canyon-flood channel, rain trenches, a fill-in job and a drain off the map edge - every litre accounted.

**START:** open sluice A (the pond's canal), then sluice B; unpause

**Try:**

1. START: open sluice A, then B; unpause: the pond's shoreline recedes as canal A draws; B runs off the east edge; the spring's canal C never drops (a source)
2. set the pump to Draw: the tank fills from the pond through the hose Intake end; then Pour: back into the pond
3. designate Fill in canal on canal A's far 4 cells: the filled cells' water goes back to the pond
4. select the canyon trigger at canal D's head > Flood now: the flood runs IN canal D, not over the land
5. select the edge setter: set the east edge sealed: B stops draining and fills
6. closed ledger (fenced, south-east): set the reel's Free end to Outflow: the two tanks' sum stays equal to the litre while litres move
7. RAIN BRANCH (RM_fw_composite_rain): trench E fills, roofed F stays dry; the drawn-down pond refills around the muffalo, never over it

**Look for:** the pond's edge recedes, the spring's never; no water on open ground beside a full canal; the ledger sum constant

**Broken looks like:** the pond full after heavy draw; the spring's readout not saying it is a source; water on open ground beside a full canal (today; not after Stage 1); water poured onto the muffalo; the flood wiping the canal flat; a sealed edge still draining; any litre unaccounted

**Still until poked:** sluices A and B shut; the pump Pours from an empty tank; the ledger hose is Capped; canal D and the trenches dry; the edge setter automatic

**Branch saves:** RM_fw_composite_rain: weather Rain locked; RM_fw_composite_days

| piece | status | tag | note |
|---|---|---|---|
| limited pond 12x8 | staged | demonstrated |  |
| canal A behind a shut sluice | staged | poked |  |
| canal B to the east map edge behind a shut sluice | staged | poked |  |
| spring = flow source, canal C full | staged | demonstrated |  |
| canyon flood trigger at canal D's head | staged | poked |  |
| rain trench E open | staged | poked |  |
| rain trench F roofed | staged | poked |  |
| small pond drawn down, muffalo in the bed | staged | look |  |
| pump (Pour) + empty tank + hose Intake end in the pond | staged | poked |  |
| map-edge setter | staged | poked |  |
| closed ledger: two tanks, one hose, fenced | staged | poked |  |
| overflow Stage 1+ (D1, D2, D6) | DEFERRED | DEFERRED | only the offline Stage 0 kernel exists; canal B is sized so sealing the edge with the pump pouring overfills it once Stage 1 lands - builds under `CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED` |
| a limitless BODY marker on a natural pond | DEFERRED | DEFERRED | the spring is a flow source; a body flagged limitless (and its readout) has no staging surface here - builds under `FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS` |
| rain (global weather) | DEFERRED | DEFERRED | lives in the branch save RM_fw_composite_rain, never the main save - builds under `design §2 GPT #11` |

Exercises (20 ids): 15 poked, 4 look, 1 DEFERRED.

Goal read: live: the closed ledger's two tank stocks sum to 8000 L before and after the soak

## C11 - Prospector's Creek (map R, look Scrapper)

A working creek: ford stones, a stake levee and silt trap, a weir a flood wears through, a ferry rope across the deep run, panning and a sluice box - on a real river with real current.

**START:** unpause

**Try:**

1. START: unpause: the control colonist in the water is carried; the one on the ford stones is not; logs drift
2. ferry a colonist across the deep run (the rope); the stones carry him dry
3. watch the weir pool; dev: Incidents > seasonal flood: the worn weir breaches, the stakes hold the bank (water leaks only through the gap), the silt trap's neighbours richen
4. panners and the sluice box draw from the shared stock; setting off washes nothing
5. stand a throwaway colonist in moving water at the map edge: swept off the map; he walks home

**Look for:** the push follows the river's bend; stones read as stones, not dry ground; the rope drawn above the water

**Broken looks like:** nobody carried; the stones carrying; the ferry ignored; a weir that never pools or never breaks; wash drawn from nothing

**Still until poked:** nothing staged moves by itself except the river: the carried muffalo and logs ARE the demonstration (the soak reads buildings, not those)

| piece | status | tag | note |
|---|---|---|---|
| R station r_current on a real crossing | staged | demonstrated |  |
| R station r_ford on a real crossing | staged | demonstrated |  |
| R station r_weir on a real crossing | staged | demonstrated |  |
| R station r_breach on a real crossing | staged | demonstrated |  |
| R station r_stakes on a real crossing | staged | demonstrated |  |
| R station r_silt on a real crossing | staged | demonstrated |  |
| R station r_ferry on a real crossing | staged | demonstrated |  |
| R station r_placer on a real crossing | staged | demonstrated |  |
| control colonist in moving water beside the ford | staged | poked |  |
| a rope suspension bridge over the deep run | DEFERRED | DEFERRED | suspension over water is in review (SUSPENSION_WATERS_BUILD_MAY_BACKTRACK); the ferry rope carries the crossing - builds under `SUSPENSION_WATERS_BUILD_MAY_BACKTRACK` |
| panners assigned | DEFERRED | DEFERRED | work assignment is his (Work tab); the panning spot is placed - builds under `RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED` |

Exercises (13 ids): 3 demonstrated, 7 poked, 3 look.

Goal read: live: river_anchors places all eight stations (unplaced ones are reported, never faked)

## C12 - The Oubliette and the Kennel (map C, look Modern)

What a pit holds, what climbs out, how wardens work from the lip, and every way in and out of a pit.

**START:** unpause: wardens go to the prisoner from the lip; the kennel beasts start testing the ring

**Try:**

1. START: unpause: wardens feed and water the prisoner from the lip; nobody climbs down
2. oubliette: lower the rail ladder from ABOVE (only from above); raise it from below with the prisoner on it: stranded
3. kennel: just watch: the chicken stays in the ring, the husky climbs out slowly, the muffalo steps across; the thrumbo walks round the 1x1 shaft
4. order the colonist beside the concealed pit onto it: falls through, hurt
5. jump the jump-pack colonist into the third pit: lands unhurt; undraft the geared one: climbs out of 5 m; undraft the ladder-pit one: climbs the portable ladder
6. inspect a pit cell at noon and at midnight (dev advance; branch save _days): its temperature differs from the ground's (vanilla temperature only, no extra sun)

**Look for:** a pit reads as a dark hole at its size; occupants drawn below the floor; raised vs lowered ladder legible; the guardrail keeps people off the lip

**Broken looks like:** a warden climbing down; the room not a prison; all three kennel beasts held, or all out; the thrumbo in the 1x1; the concealed pit visible at play zoom; a ladder lowered from below; the guardrail letting someone walk off

**Still until poked:** every colonist drafted; the prisoner is in a sealed 4 m pit; the beasts are wild and roam INSIDE the ring (climbing out is the test, so the soak reads their KIND per plot, not their cell)

**Branch saves:** RM_fw_composite_days: midnight for the pit-temperature read

| piece | status | tag | note |
|---|---|---|---|
| oubliette 3x4, 4 m, prisoner bed | staged | demonstrated |  |
| prisoner, hungry-ish and thirsty | staged | demonstrated |  |
| rail ladder on the north wall, RAISED | staged | poked |  |
| guardrail round the lip | staged | look |  |
| sluice (wood) in the east wall | staged | poked |  |
| security grate (steel) in the east wall | staged | poked |  |
| dry drain canals behind the doors | staged | look |  |
| concealed pit 3x3 (planks) | staged | poked | plank lattice, not the design's reinforced frame: the frame should HOLD one colonist (review_map pit_cover_drop), and this poke wants a fall |
| kennel ring, 2 m trench, 2 wide | staged | demonstrated |  |
| chicken, husky, muffalo in the yard | staged | demonstrated |  |
| drafted handler at the ring | staged | demonstrated |  |
| thrumbo beside a 1x1 sheer shaft | staged | demonstrated |  |
| portable ladder in a 3 m pit | staged | poked |  |
| climbing gear colonist in a 5 m pit | staged | poked |  |
| jump-pack colonist at a lip | staged | poked |  |
| flyers and floaters (pit travel) | DEFERRED | DEFERRED | never live-tested without the owner (ruling 2026-09-19): added only when he is at the keyboard - builds under `FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT` |
| machine-digging the 3-5 m pits | DEFERRED | DEFERRED | past the 2 m colonist cap; the pits are staged, a machine dig order is not built - builds under `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL` |

Exercises (26 ids): 4 demonstrated, 10 poked, 12 look.

Goal read: live: ProofLadder read on the oubliette ladder says raised; the prisoner's room reads as a prison

## Stage 0 - swim out of a flooded sheer pit (C3's bet)

stage0_swim_pit.py -- Stage 0 proof #3 of the composite design (§5.2 step 0; GPT #2, taken): a swimmer in a flooded
SHEER pit of C3's exact geometry rises and leaves.

