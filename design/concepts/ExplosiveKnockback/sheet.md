# Explosive Knockback: every blast in RimWorld now throws what it hits

## his words
- 2026-09-17: a pawn blasted into a covered pit falls in.
- 2026-10-06, by card: everywhere; explosions only, melee already has blowback; thrown over sandbags; everything light, items and corpses; a blast breaks a pit cover; 3 cells for a mortar beside a human; goods in a pit stay retrievable.
- 2026-11-10: goods visibly fly, rotate and rebound off walls losing energy; no exemption for ordinary shelves; gas goes off clump by clump, each clump scattering goods in its own radius, never one centroid blast.
- 2026-11-11, by card: "Is this the mod? -> Approve as written". OWNER:1794468835221748501
- 2026-11-11, by card: which blasts throw -> all harmful explosions, fire at half, other mods too. OWNER:1794468840281537479
- 2026-11-11, safe storage: "(1) but the closed containers may themselves get shoved a bit" OWNER:1794468845275647261
- 2026-11-11, by card: shield belt -> yes, costs extra charge. OWNER:1794468850306726165
- 2026-11-11, by card: scatter -> C, wild. OWNER:1794468855146168085
- 2026-11-11, by card: gas clump against people -> B, shove 1 cell, no damage. OWNER:1794468860062036002
- 2026-11-11, by card: goods beyond the smooth cap -> all of them fly. OWNER:1794468864684141079
- 2026-11-11, by card: thrown goods hitting people -> light knock, heavy only. OWNER:1794468869384727517
- 2026-11-11, gas source: "2 and remember the gas in the Cauldron" OWNER:1794468874358971350
- 2026-11-12, flagship: "Just put a bomb into a storeroom with people in it beside a pit. Shows some items falling into the pit and some people as well." OWNER:1794470697182934051
- 2026-11-12, by card: the 16 north-star bars -> Approve as written. OWNER:1794470702467936205
- 2026-11-12, the 4 coverage gaps: "1: Anything that draws its contents is open. 2: Search our modlist for explosion. There is at least one that makes them bigger and more impressive, we should have characterized them first I now see. 3: I'm sure they'll work, no need for more testing here, change the word. 4: I am confused. Items should be blown off a shelf, and a shelf should be ruled as open, period. So the scene is staged misleadingly. No blockers." OWNER:1794529787425697771
- 2026-11-13, by card: "We really shouldn't blow back creatures beyond a certain mass, and the heavier something is, the less it should fly. That should also be a function of the explosive damage itself as well." "with a single scene we can check ALL these things together" OWNER:1794592220102307459
- 2026-11-13, by card: Cutoff -> a mass limit; Blast power -> type x damage; "Melee shove is a great idea, but it belongs in FlowWorks, not here." OWNER:1794592407312114138

## does
- [leaf:people_thrown_three_cells] A mortar shell beside a colonist throws them about three cells straight away, over sandbags and barricades, alive and briefly stunned
- [leaf:pawn_flight_arc] A thrown pawn is carried through the air to the cell chosen at the blast, never re-targeted, and goes back to work when the stun ends
- [leaf:the_spared] Never thrown: a living creature heavier than 150 kg (the creature mass limit, a Mod Setting, which weighs living pawns only; a weapon with its own creature limit, like the grav-ram's 216 kg, throws pawns under that instead), a pawn already in a pit, a pawn carrying a pawn, a pawn already airborne, a pawn in bed, goods or corpses heavier than 75 kg (the goods mass limit, which weighs goods and corpses only, never a living pawn), goods and corpses already on a pit floor, a thing at the rim whose throw is under one cell; no body-size rule remains
- [leaf:heavier_flies_less] Heavier flies less and a bigger blast throws farther: one blast throws a rat farther than a colonist, a colonist farther than a muffalo, and a thrumbo over 150 kg not at all; at twice the damage each goes farther, since force is the damage type's force times this blast's damage over that type's normal damage. OWNER:1794592220102307459 OWNER:1794592407312114138, owed
- [leaf:recovery_immunity] A pawn just thrown is spared a second throw until its stun and a short recovery end, also across a save
- [leaf:hose_drops_at_takeoff] A thrown colonist carrying a hose end drops it where they stood, owed a proof
- [leaf:wall_stops_dead] A thrown person stops dead at a wall and takes an impact hit; people never rebound, not even half a step back
- [leaf:pawn_hits_pawn_stops] A thrown person stops at another pawn in the way and takes an impact hit, as at a wall
- [leaf:doors_and_deep_water_stop] A closed door stops a throw and takes damage (none under an impact factor of 0); deep water stops a throw on the last cell a pawn can stand on
- [leaf:shield_belt_holds] A shield belt that absorbs the blast keeps its wearer in place and pays extra charge (a burning gas clump's one-cell shove is the exception: a belt does not stop it)
- [leaf:goods_arc_spin_rebound] Loose goods and corpses, a pawn the blast kills among them, fly wild: about 1.6 times as far as a person, high arc, fast spin, rebounds off walls and closed doors keeping about 70 percent each, until spent; over sandbags, and never into deep water. OWNER:1794468855146168085, owed
- [leaf:every_good_moves] Every light loose good the blast reaches with a throw of a cell or more moves (bar those spared above); the 40-throw cap and the per-tick drop are removed, nothing is skipped over a cap. OWNER:1794468864684141079, owed
- [leaf:open_shelf_scatters] Open shelves, hoppers and tables protect nothing: anything that draws its contents is open, period. OWNER:1794468845275647261 OWNER:1794529787425697771, owed
- [leaf:closed_container_holds] Closed containers (storage that hides what it holds: sealed crates, modded lockers and safes that do not draw their contents, and another mod's hiding container given the opt-in tag, such as the Armoury's secret floor panels) keep their goods and may themselves be shoved a little: one cell at or under the 250 kg container mass limit, else a jolt, never into a pit, a wall or onto a pawn. OWNER:1794468845275647261 OWNER:1794529787425697771, owed
- [leaf:heavy_stack_knocks] A heavy thrown stack gives a pawn a light knock and a stagger; light goods pass. OWNER:1794468869384727517, owed
- [leaf:every_harmful_blast_throws] Every harmful explosion throws: bombs full, fire at half strength (about half the throw), other mods too (the other-mods percent only for a damage type our patch does not tune, never stacked); harmless bursts nothing. OWNER:1794468840281537479, owed
- [leaf:only_explosions_throw] Only explosions throw; melee and bullets move nobody, by his 2026-10-06 answer
- [leaf:per_weapon_tuning] A weapon's own tuning sets its throw, projectile first, then weapon, then damage type; zero turns it off; its own maximum caps the throw (0 = the global maximum) and the per-weapon cap scale shortens that own maximum; an impact factor of 0 makes its throws hit walls, pawns and doors harmlessly, the door undamaged; its own creature mass limit lets it throw heavier pawns
- [leaf:gas_goes_clump_by_clump] A flammable gas cloud that a fire touches goes off clump by clump, scattering goods and shoving people one cell unhurt, a person at most once every 2 seconds. OWNER:1794468860062036002, owed
- [leaf:our_gases_burn] The Cauldron's gas goes off clump by clump, and so does any other gas source of ours the census finds fitting. OWNER:1794468874358971350, owed
- [leaf:blast_breaks_pit_cover] A damaging or fire blast that reaches a pit cover, landing on it or beside it within its radius, breaks it and whoever is on it falls; a gas burst or an EMP, smoke or stun burst never does (a pawn a gas burst shoves onto a cover stands on it, the cover whole). OWNER:1794468860062036002
- [leaf:thrown_into_pit_falls] Anything thrown toward an open pit falls to its floor, and onto a covered cell falls through and breaks the cover; nothing is thrown across. A gas clump's one-cell shove is not a throw but is force: onto an open pit cell the pawn falls in, onto a cover it stands, the cover whole
- [leaf:pit_goods_fetched] A colonist can fetch thrown goods and corpses back off a pit floor, owed a proof
- [leaf:barrage_frame_budget] A mortar barrage into a full stockpile and a long gas chain stay smooth at normal speed, owed
- [leaf:frame_time_probe] A per-frame time probe, so the frame budget can be measured
- [leaf:walk_storeroom_raid] A raid on a stocked colony on the full list, with a mid-way reload, a repeat and a second order
- [leaf:settings_scale_and_switch] Superb Mod Settings: every line takes effect (the removed cap settings are gone from the page), and every new part switches off cleanly with the rest still working, each to its own off state: goods in the air off, goods unthrown, never the old hop; closed guard off, container goods thrown loose; container shove off, containers stay; sealed crates counted closed off, a crate neither slides nor jolts; heavy knock off, stacks pass; gas chain off, a cloud burns without bursts; fire at half off, fire throws nothing; blast power from damage off, damage is ignored
- [floor:mod_settings] Superb Mod Settings: master switch, strengths and every new part switch off cleanly
- [floor:tick_cost] The thrown-thing carrier's own tick cost, measured on the walk

## does not
- [leaf:no_teleport] Goods never vanish and reappear under a dust puff
- [leaf:no_careless_fall] No colonist walks into a pit by ordinary pathing; an enemy may walk into a pit hidden from it, by his 2026-10-06 answer
- [floor:worldgen] No worldgen of any kind
- [floor:multiplayer] No multiplayer support

## waived

## open

## delegated
- A 1x1 closed container whose own mass plus contents is at or under the 250 kg container mass limit (a Mod Setting, not the 75 kg goods limit) slides one cell if the cell behind it is free, else it jolts in place; never into a pit, a wall or onto a pawn
- Sealed crates count as closed containers is a Mod Setting, on by default; a crate's goods sit in its own holder, out of any blast's reach, so the switch only decides whether the crate is shoved or jolted (off: neither)
- The creature mass limit is 150 kg (60 kg times the old body size 2.5, so a muffalo at 144 flies and a rhino at 180 does not), measured from the game's defs; a corpse is weighed only by the 75 kg goods limit; the grav-ram's own limit is 216 kg
- A damage type's normal damage is its own default (Bomb 50, Flame 10), so fire keeps its half and a mortar still throws a colonist 3 cells; the vanilla grenade, mortar and IED all deal 50 and differ by radius; blast power from damage is a Mod Setting, on; gas clump bursts are not scaled by damage
- A gas shove onto an open pit drops the pawn in, by his 2026-10-06 rule that a pawn forced in falls; the melee shove contest is FlowWorks' item, not this mod's
- Other mods' damaging explosions throw at 100 percent by default; EMP, smoke, stun, extinguish and toxic gas at 0, fire at half; the other-mods percent and the fire-half switch are on Mod Settings (off: fire throws nothing, as shipped), the per-type strengths sit in the def patch and any weapon can be tamed per weapon
- Heavy means a stack of 10 kg or more; the knock is 2 to 5 blunt and about half a second of stagger, then the stack stops; a setting
- The gas census covers every gas source of ours (gas defs, our gas grids, every place our code adds gas); today the one that burns is the Cauldron's vent gas, which opts in by registering its grid; the others add vanilla smoke, tox gas or rot stink, which do not burn; this mod adds no gas of its own
- A gas cloud catches the way it already does in play, from a fire touching it; a fire not touching it lights nothing
- One gas clump bursts at radius 1.9, throws goods at most 2 cells, one burst per clump cell, advancing with the fire front; a shield belt does not stop the shove
- The frame budget is no frame over 50 ms through a 6-shell barrage and a 40-cell chain; advisory until a first measurement calibrates it
- The gas chain and the pit-trap raid stay ordinary scenes (coverage_rest), not showcases, by the greedy showcase rule (his one flagship scene takes the showcase)

## pruning
- people_thrown_three_cells: yes, it is the mod
- pawn_flight_arc: yes, a hop instead of a throw is what he rejected for goods
- the_spared: no alone, but a thrown thrumbo or sleeper reads broken
- heavier_flies_less: yes, his 2026-11-13 card
- recovery_immunity: no alone, it stops juggling
- hose_drops_at_takeoff: no alone, his 2026-10-06 answer
- pawn_hits_pawn_stops: no alone, the same rule as walls
- doors_and_deep_water_stop: no alone, the same rule as walls
- wall_stops_dead: yes, people bouncing like goods would read as a toy
- shield_belt_holds: no alone, but it is his one counter
- goods_arc_spin_rebound: yes, he ruled it twice
- every_good_moves: yes, a stack sitting still reads broken
- open_shelf_scatters: yes, he ruled no exemption for ordinary shelves
- closed_container_holds: yes, his own write-in
- heavy_stack_knocks: no alone, a small added touch
- every_harmful_blast_throws: yes, his word was everywhere
- only_explosions_throw: yes, he ruled explosions only
- per_weapon_tuning: no alone, it keeps weapons tunable
- gas_goes_clump_by_clump: yes, he ruled it
- our_gases_burn: yes, his write-in named the Cauldron
- blast_breaks_pit_cover: yes, ruled twice
- thrown_into_pit_falls: yes, his first ruling
- pit_goods_fetched: yes, he ruled goods stay retrievable
- no_teleport: yes, the hop is what he rejected
- no_careless_fall: yes, a colonist enters a pit only by force; an enemy may still walk into one hidden from it
- barrage_frame_budget: yes, all-fly that stutters fails his pick
- walk_storeroom_raid: yes, the walk is the mod in play
- settings_scale_and_switch: no alone, but a part that cannot be switched off fails the floor

## later
- Thrown people tumbling and rebounding like goods: not asked for, kept out so landings stay predictable
