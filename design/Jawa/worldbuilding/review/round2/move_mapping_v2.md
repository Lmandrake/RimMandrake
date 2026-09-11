# Move-target mapping v2 — all 164 Move rows

**Amended 2026-09-10 (owner insect ruling):** base-game/Black Hive insects stay
faction-only (infestation/raid events), never biome residents. The four VFEI2 move
rows (Acidspitter, Macrofly, RoyalSpelopede, Silverfish) are VOIDED and removed;
their decisions rows are marked FACTION-RESERVED in `decisions_propagated.json`.
164 moves live (4 arid sitting rulings 2026-09-10 added; Cannok/Vulptex resolve to RESERVE, not a biome) (horror/injectable ruling 2026-09-10 voided Bulwark, Prowler, Squall — injected content, not biome arrivals).

Rebuilt from the owner's completed fauna review (`design/Jawa/worldbuilding/review/fauna_assignment_register.decisions.json`, decidedCount 828, 164 `move` rows). Row key = the decisions.json dict key (`fauna:<originSheet>:<creature>` or `homeless:<creature>`); the owner's words are the verbatim `note` field on that row (truncated to 15 words), never invented. Seeded from `move_target_mapping_2026-09-09.md` (69 rows, validated nickname table); extended here to cover all 164. Standing corrections applied: ocular/occular -> the_contagion; Volcanic (fliers) -> the Forge family, not the_pyrelands.

| row key | creature | owner's words | resolved target |
|---|---|---|---|
| `fauna:the_greentide:AA_BloodShrimp` | AA_BloodShrimp | ocular only | the_contagion |
| `fauna:the_greentide:AA_Razorjack` | AA_Razorjack | Pyrelands | the_pyrelands |
| `fauna:the_greentide:Beldon` | Beldon | only over Volcanic | the_forge |
| `fauna:the_greentide:Dalgo` | Dalgo | Pyrelands | the_pyrelands |
| `fauna:the_greentide:Dianoga` | Dianoga | 6 cells, would be awesome if we could add tentacle pulling capabilities like the lasso … | the_miasma |
| `fauna:the_greentide:Falumpaset` | Falumpaset | nope, this thing needs large open spaces only | OUT |
| `fauna:the_greentide:Hssiss` | Hssiss | the swamp biome only | the_sump |
| `fauna:the_greentide:Lylek` | Lylek | Poison Forest | poison_forest |
| `fauna:the_greentide:ShiroTrap` | ShiroTrap | The Rot | the_rot |
| `fauna:the_miasma:AA_BloodShrimp` | AA_BloodShrimp | ocular only | the_contagion |
| `fauna:the_miasma:AA_Helixien` | AA_Helixien | Not here | OUT |
| `fauna:the_miasma:AA_Plasmorph` | AA_Plasmorph | The Poison Forest | poison_forest |
| `fauna:the_miasma:AA_Slurrypede` | AA_Slurrypede | Not here | OUT |
| `fauna:the_miasma:BMT_Gembug` | BMT_Gembug | Crystal caverns | the_lantern_deeps |
| `fauna:the_miasma:Kreetle` | Kreetle | arid type only | arid_shrubland |
| `fauna:the_miasma:RSW_Faa` | RSW_Faa | only underwater biomes place... The Scald underwater. 0.2 cells | the_scald |
| `fauna:the_miasma:RSW_Laa` | RSW_Laa | Twilight Sea | the_twilight_deep |
| `fauna:the_miasma:RSW_Mee` | RSW_Mee | Scald only, 0.3 cells | the_scald |
| `fauna:the_miasma:RSW_OpeeSeaKiller` | RSW_OpeeSeaKiller | Twilight Sea, make it 5 squares long | the_twilight_deep |
| `fauna:the_miasma:RSW_SiltLamprey` | RSW_SiltLamprey | Grey Sea | the_grey_deep |
| `fauna:the_miasma:Yobshrimp` | Yobshrimp | Twilight Sea | the_twilight_deep |
| `fauna:the_propane_lakes:AA_FrostboundBehemoth` | AA_FrostboundBehemoth | needs to totally alien life | OPEN |
| `fauna:the_propane_lakes:AA_Slurrypede` | AA_Slurrypede | not here | OUT |
| `fauna:the_propane_lakes:AA_Terramorph` | AA_Terramorph | not here,, too ordinary | OUT |
| `fauna:the_pyrelands:Boomalope` | Boomalope | Convert to a twisted thing the Assailants make in their dungeons | GROUP:dungeon-guardians |
| `fauna:the_pyrelands:Gizka` | Gizka | not here | OUT |
| `fauna:the_scald:RSW_ElderSando` | RSW_ElderSando | Grey Sea | the_grey_deep |
| `fauna:the_scald:RSW_SandoAquaMonster` | RSW_SandoAquaMonster | Miasma | the_miasma |
| `fauna:the_scarlands:AA_Helixien` | AA_Helixien | not here | OUT |
| `fauna:the_scarlands:AA_SpinedGow` | AA_SpinedGow | extreme desert | dune_sea + deep_desert |
| `fauna:the_slime:AA_DecayDrake` | AA_DecayDrake | not here | OUT |
| `fauna:the_slime:AA_Helixien` | AA_Helixien | not here | OUT |
| `fauna:the_slime:AA_Mime` | AA_Mime | Only assailant dungeons | GROUP:dungeon-guardians |
| `fauna:the_slime:AA_Plasmorph` | AA_Plasmorph | not here | OUT |
| `fauna:the_slime:AA_Thunderbeast` | AA_Thunderbeast | blue desert | the_blue_desert |
| `fauna:the_slime:GR_Manbear` | GR_Manbear | Helix territory only | OPEN |
| `fauna:wasteland:AA_AcanthamoebaGiganteaSmall` | AA_AcanthamoebaGiganteaSmall | scarlands | the_scarlands |
| `fauna:wasteland:AA_Eyeling` | AA_Eyeling | ocular | the_contagion |
| `fauna:wasteland:BMT_ColonyPustuleHornetQueen` | BMT_ColonyPustuleHornetQueen | The Rot | the_rot |
| `fauna:wasteland:BMT_PustuleHornetQueen` | BMT_PustuleHornetQueen | The Rot | the_rot |
| `fauna:wasteland:BMT_PustuleHornetSpawned` | BMT_PustuleHornetSpawned | The Rot | the_rot |
| `fauna:wasteland:SW_Electrictick` | SW_Electrictick | only scarlands | the_scarlands |
| `fauna:wasteland:Toxalope` | Toxalope | assailant dungeons | GROUP:dungeon-guardians |
| `homeless:AA_AcanthamoebaGiganteaHuge` | AA_AcanthamoebaGiganteaHuge | Slime | the_slime |
| `homeless:AA_AngelMoth` | AA_AngelMoth | Rot | the_rot |
| `homeless:AA_AngelMothLarva` | AA_AngelMothLarva | Wildsteam biomes | OPEN |
| `homeless:AA_AnimaColossus` | AA_AnimaColossus | Rot | the_rot |
| `homeless:AA_Atispec` | AA_Atispec | Scald | the_scald |
| `homeless:AA_AuroraSylph` | AA_AuroraSylph | Perfect Propane Lake creature | the_propane_lakes |
| `homeless:AA_Barbslinger` | AA_Barbslinger | wherever needed in hot biomes | OPEN |
| `homeless:AA_Behemoth` | AA_Behemoth | crag, 16 squares | forsaken_crags |
| `homeless:AA_BumbledroneQueen` | AA_BumbledroneQueen | goes with the rest of the bumbledrones | the_sump |
| `homeless:AA_ColossalAerofleet` | AA_ColossalAerofleet | rare creature wherever normal aerofleets end up | terminator_sea + the_grey_deep + the_twilight_deep + the_forge |
| `homeless:AA_CrescendoAnole` | AA_CrescendoAnole | volcanic biomes | the_forge |
| `homeless:AA_EmpressButterfly` | AA_EmpressButterfly | Wildsteam areas | OPEN |
| `homeless:AA_EmpressButterflyLarva` | AA_EmpressButterflyLarva | Wildsteam biomes | OPEN |
| `homeless:AA_Erin` | AA_Erin | Wherever it's needed | OPEN |
| `homeless:AA_Feralisk` | AA_Feralisk | Should be reskinned to the Wysokk of the Web biome. Merge | the_webwork |
| `homeless:AA_FungalHusk` | AA_FungalHusk | occular | the_contagion |
| `homeless:AA_GreatDevourer` | AA_GreatDevourer | Relative of the Sarlacc wandering the desert | desert |
| `homeless:AA_Groundrunner` | AA_Groundrunner | desert | desert |
| `homeless:AA_LarvalAtispec` | AA_LarvalAtispec | wherever the atispec ends up | the_scald |
| `homeless:AA_LuciferBug` | AA_LuciferBug | poison forest | poison_forest |
| `homeless:AA_MatureFleshbeast` | AA_MatureFleshbeast | desert, immature sarlacc | desert |
| `homeless:AA_OcularNightling` | AA_OcularNightling | occular | the_contagion |
| `homeless:AA_OvergrownColossus` | AA_OvergrownColossus | The Slime (make the trees into slime trees) | the_slime |
| `homeless:AA_PebbleMit` | AA_PebbleMit | along any shoreline or oasis | OPEN |
| `homeless:AA_PedigreedRaptor` | AA_PedigreedRaptor | TOTALLY Hutt settlements and territories | OPEN |
| `homeless:AA_Radyak` | AA_Radyak | Poison Forest | poison_forest |
| `homeless:AA_RayHound` | AA_RayHound | Scald beast | the_scald |
| `homeless:AA_RipperHound` | AA_RipperHound | Poison Forest | poison_forest |
| `homeless:AA_SandLion` | AA_SandLion | Sand burrower swimmer deserts | desert + dune_sea + deep_desert |
| `homeless:AA_ShockGoat` | AA_ShockGoat | Refashion into nightside biomes, your choice of extreme cold area, make pale blue aura around … | nightside_ice |
| `homeless:AA_Skyeel` | AA_Skyeel | Electrostatic flyer over Propane Lakes | the_propane_lakes |
| `homeless:AA_TeratogenicOriginator` | AA_TeratogenicOriginator | Slime, tint green | the_slime |
| `homeless:AG_OcularSlinger` | AG_OcularSlinger | contagion | the_contagion |
| `homeless:Acklay` | Acklay | Hutt arena fodder and territories | OPEN |
| `homeless:Aiwha` | Aiwha | HUGE flyer, could appear anywhere, mountable, air, sea, land, Helix territories | GROUP:fliers |
| `homeless:BMT_Basilisk` | BMT_Basilisk | any mountain, make it grey | OPEN |
| `homeless:BMT_BunkerBug` | BMT_BunkerBug | Superb for the Fall wreckage creature | fall_line |
| `homeless:BMT_CaveLemming` | BMT_CaveLemming | ice sheet, rename | nightside_ice |
| `homeless:BMT_ColonyPustuleHornet` | BMT_ColonyPustuleHornet | the Rot | the_rot |
| `homeless:BMT_CrystalCrab` | BMT_CrystalCrab | crystal caverns | the_lantern_deeps |
| `homeless:BMT_CrystalFairyMole` | BMT_CrystalFairyMole | Scarlands, oddly. 1 cell | the_scarlands |
| `homeless:BMT_FacetMoth` | BMT_FacetMoth | Make it brightly colored and put it in the jungle | OPEN |
| `homeless:BMT_FacetMothLarvae` | BMT_FacetMothLarvae | crystal caverns | the_lantern_deeps |
| `homeless:BMT_Megakrill` | BMT_Megakrill | Fishing result, the Grey Sea → retargeted Twilight (2026-09-10 schooling ruling) | the_twilight_deep |
| `homeless:BMT_Megaphorid` | BMT_Megaphorid | injectable hives | OPEN |
| `homeless:BMT_MegaphoridLarva` | BMT_MegaphoridLarva | scarlands | the_scarlands |
| `homeless:BMT_Megapleura` | BMT_Megapleura | wreckage-based creature for the Fall | fall_line |
| `homeless:BMT_MutatingTumorfishAdult` | BMT_MutatingTumorfishAdult | Grey Sea → retargeted Twilight (2026-09-10 schooling ruling) | the_twilight_deep |
| `homeless:BMT_MutatingTumorfishFry` | BMT_MutatingTumorfishFry | Grey Sea → retargeted Twilight (2026-09-10 schooling ruling) | the_twilight_deep |
| `homeless:BMT_MutatingTumorfishSpawn` | BMT_MutatingTumorfishSpawn | Grey Sea → retargeted Twilight (2026-09-10 schooling ruling) | the_twilight_deep |
| `homeless:BMT_PodWorm` | BMT_PodWorm | Maisma | the_miasma |
| `homeless:BMT_Polluwog` | BMT_Polluwog | Grey sea | the_grey_deep |
| `homeless:BMT_PustuleHornet` | BMT_PustuleHornet | the Rot | the_rot |
| `homeless:BMT_SandPillar` | BMT_SandPillar | cracked land | the_cracked_lands |
| `homeless:BMT_SmogMoth` | BMT_SmogMoth | Neat flier in the Rot | the_rot |
| `homeless:BMT_Stoneback` | BMT_Stoneback | Anywhere on the dayside where it might be needed. 1.2 cells | desert + arid_shrubland + wasteland + the_scarlands |
| `homeless:BMT_Thrumbungus` | BMT_Thrumbungus | Make multi-hued and with a surface that's partially digesting itself, move it into the Rot | the_rot |
| `homeless:BMT_TruffleMole` | BMT_TruffleMole | sand burrower, desert & extreme desert, 0.4 cells | desert + dune_sea + deep_desert |
| `homeless:BMT_Yooka` | BMT_Yooka | The Rot | the_rot |
| `homeless:Blarth` | Blarth | Miasma, domesticatable, Hutt pets, 1 cell | the_miasma |
| `homeless:Blixus` | Blixus | The Grey Sea and the Maiasma | the_grey_deep + the_miasma |
| `homeless:Blurrg` | Blurrg | Moisture Farmers territory, domesticated | OPEN |
| `homeless:Bogwing` | Bogwing | miasma flyer | the_miasma |
| `homeless:Brezak` | Brezak | Hutt areas | OPEN |
| `homeless:DA_BeardedTroll` | DA_BeardedTroll | Semi-sentient guardian used by Wildsteam, trainable, sometimes seen wild in their territory, mostly fur with … | OPEN |
| `homeless:DA_RockTroll` | DA_RockTroll | Cracked biome | the_cracked_lands |
| `homeless:FrogDog` | FrogDog | Hutt territories and pet and settlements | OPEN |
| `homeless:GR_Bearmole` | GR_Bearmole | wherever needed in any dayside biome | OPEN |
| `homeless:GR_Boomsnake` | GR_Boomsnake | Pyrelands | the_pyrelands |
| `homeless:GR_Chickenhorse` | GR_Chickenhorse | Helix areas | OPEN |
| `homeless:GR_Chickenlizard` | GR_Chickenlizard | Helix areas | OPEN |
| `homeless:GR_Chickenspider` | GR_Chickenspider | Baby evil spider in the Web biome Wysok(sp?) | the_webwork |
| `homeless:GR_Fleshling` | GR_Fleshling | Contagion | the_contagion |
| `homeless:GR_Mancat` | GR_Mancat | Helix territories | OPEN |
| `homeless:GR_Mechachicken` | GR_Mechachicken | rust cathedral | the_rust_cathedral |
| `homeless:GR_Mecharat` | GR_Mecharat | rust cathedral and mechanoid dungeons | the_rust_cathedral |
| `homeless:GR_Needlechicken` | GR_Needlechicken | Helix territory | OPEN |
| `homeless:GR_Nighthrumbo` | GR_Nighthrumbo | Crags | forsaken_crags |
| `homeless:GR_Rabbitchicken` | GR_Rabbitchicken | sold as pet by the Helix faction | OPEN |
| `homeless:GR_Snakecat` | GR_Snakecat | venomthorn dweller | OPEN |
| `homeless:GR_Spidersnake` | GR_Spidersnake | Helix area | OPEN |
| `homeless:GiantAnt_Race` | GiantAnt_Race | Only the raiding events in the greentide jungles and surrounding area | the_greentide |
| `homeless:Gullipud` | Gullipud | oases and pets | OPEN |
| `homeless:Gundark` | Gundark | Problemmatic semi-sentient predator of the wildsteam territories, can form small raids, this creature steals. Hutt … | OPEN |
| `homeless:JOE_Cephalope` | JOE_Cephalope | sand burrower & swimmer, absorb & retire mod, anywhere there is deep hot sand | desert + dune_sea + deep_desert |
| `homeless:JOE_Landopus` | JOE_Landopus | desert water defender type | desert |
| `homeless:JOE_Nautilant` | JOE_Nautilant | scald | the_scald |
| `homeless:JRWBeelzebufo` | JRWBeelzebufo | Maisma | the_miasma |
| `homeless:JungleRancor` | JungleRancor | wildsteam jungle biom, tree breaker | OPEN |
| `homeless:KellDragon` | KellDragon | Hutt territories and area pits | OPEN |
| `homeless:Leaftail` | Leaftail | wildsteam biomes | OPEN |
| `homeless:MA_Sporemole` | MA_Sporemole | The Rot | the_rot |
| `homeless:Nexu` | Nexu | combat pets of the Wildsteam | OPEN |
| `homeless:PaintedSpat` | PaintedSpat | Slot in nearly anywhere needed on dayside | OPEN |
| `homeless:RSW_AbyssalColo` | RSW_AbyssalColo | Twilight | the_twilight_deep |
| `homeless:RSW_ColoClawFish` | RSW_ColoClawFish | Scald | the_scald |
| `homeless:RSW_CrimsonOpee` | RSW_CrimsonOpee | Twilight Sea 9 squares long | the_twilight_deep |
| `homeless:RSW_ShaleGorger` | RSW_ShaleGorger | Scarlands | the_scarlands |
| `homeless:RSW_Starmaw` | RSW_Starmaw | Twilight Sea | the_twilight_deep |
| `homeless:RSW_StormSando` | RSW_StormSando | Twilight Sea | the_twilight_deep |
| `homeless:RSW_ThornbackColo` | RSW_ThornbackColo | Scald | the_scald |
| `homeless:Rikknit` | Rikknit | Large tree biomes. "rikknit was a crustacean native to New Plympto. They had eight to … | OPEN |
| `homeless:Rycrit` | Rycrit | herd animal near oases | OPEN |
| `homeless:SWPotF_RaceDef_ysalamir` | SWPotF_RaceDef_ysalamir | Wherever needed in arid and hot zones | OPEN |
| `homeless:SW_Electricfish` | SW_Electricfish | scarlands | the_scarlands |
| `homeless:SW_Grenadierworm` | SW_Grenadierworm | scarlands | the_scarlands |
| `homeless:Snoruuk` | Snoruuk | The Rot | the_rot |
| `homeless:StoneCrab` | StoneCrab | 0.3 squares, Twilight Sea | the_twilight_deep |
| `homeless:Tach` | Tach | 1 cell, this creature can steal, lives in the Jungle | OPEN |
| `homeless:Tauntaun` | Tauntaun | white ice night biome | nightside_ice |
| `homeless:TetnissCrab` | TetnissCrab | 0.5 cells, grey sea | the_grey_deep |
| `homeless:Tibidee` | Tibidee | volcanic areas | the_forge |
| `homeless:VAEWaste_Hydra` | VAEWaste_Hydra | venomvine patch predator | arid_shrubland |
| `homeless:Wampa` | Wampa | Ice plains | nightside_ice |

| `fauna:arid_shrubland:Skalder` | Skalder | Poison Forest (sitting 2026-09-10) | poison_forest |
| `fauna:arid_shrubland:AA_Wildpawn` | AA_Wildpawn | steaming jungle (sitting 2026-09-10) | the_greentide |
| `fauna:arid_shrubland:Cannok` | Cannok | to reserve (sitting 2026-09-10) | RESERVE |
| `fauna:arid_shrubland:Vulptex` | Vulptex | to reserve (sitting 2026-09-10) | RESERVE |

| `fauna:desert:Kwi` | Kwi | to reserve (sitting 2026-09-10) | RESERVE |
| `fauna:desert:AA_Gigantelope` | AA_Gigantelope | to reserve (sitting 2026-09-10) | RESERVE |
| `fauna:the_greentide:BMT_Diggerpede` | BMT_Diggerpede | to reserve (sitting 2026-09-10) | RESERVE |

## Summary

- Total move rows: 164
- Mapped to a biome sheet: 113
- GROUP (non-biome roster): 4
- OUT (no destination / "not here"): 10
- OPEN (unmappable, needs owner's word): 37

### GROUP breakdown

- GROUP:dungeon-guardians: 3
- GROUP:fliers: 1

### OPEN rows (need the owner's word)

- **AA_FrostboundBehemoth**: "needs to totally alien life" (`fauna:the_propane_lakes:AA_FrostboundBehemoth`)
- **GR_Manbear**: "Helix territory only" (`fauna:the_slime:GR_Manbear`)
- **AA_AngelMothLarva**: "Wildsteam biomes" (`homeless:AA_AngelMothLarva`)
- **AA_Barbslinger**: "wherever needed in hot biomes" (`homeless:AA_Barbslinger`)
- **AA_EmpressButterfly**: "Wildsteam areas" (`homeless:AA_EmpressButterfly`)
- **AA_EmpressButterflyLarva**: "Wildsteam biomes" (`homeless:AA_EmpressButterflyLarva`)
- **AA_Erin**: "Wherever it's needed" (`homeless:AA_Erin`)
- **AA_PebbleMit**: "along any shoreline or oasis" (`homeless:AA_PebbleMit`)
- **AA_PedigreedRaptor**: "TOTALLY Hutt settlements and territories" (`homeless:AA_PedigreedRaptor`)
- **Acklay**: "Hutt arena fodder and territories" (`homeless:Acklay`)
- **BMT_Basilisk**: "any mountain, make it grey" (`homeless:BMT_Basilisk`)
- **BMT_FacetMoth**: "Make it brightly colored and put it in the jungle" (`homeless:BMT_FacetMoth`)
- **BMT_Megaphorid**: "injectable hives" (`homeless:BMT_Megaphorid`)
- **Blurrg**: "Moisture Farmers territory, domesticated" (`homeless:Blurrg`)
- **Brezak**: "Hutt areas" (`homeless:Brezak`)
- **DA_BeardedTroll**: "Semi-sentient guardian used by Wildsteam, trainable, sometimes seen wild in their territory, mostly fur with …" (`homeless:DA_BeardedTroll`)
- **FrogDog**: "Hutt territories and pet and settlements" (`homeless:FrogDog`)
- **GR_Bearmole**: "wherever needed in any dayside biome" (`homeless:GR_Bearmole`)
- **GR_Chickenhorse**: "Helix areas" (`homeless:GR_Chickenhorse`)
- **GR_Chickenlizard**: "Helix areas" (`homeless:GR_Chickenlizard`)
- **GR_Mancat**: "Helix territories" (`homeless:GR_Mancat`)
- **GR_Needlechicken**: "Helix territory" (`homeless:GR_Needlechicken`)
- **GR_Rabbitchicken**: "sold as pet by the Helix faction" (`homeless:GR_Rabbitchicken`)
- **GR_Snakecat**: "venomthorn dweller" (`homeless:GR_Snakecat`)
- **GR_Spidersnake**: "Helix area" (`homeless:GR_Spidersnake`)
- **Gullipud**: "oases and pets" (`homeless:Gullipud`)
- **Gundark**: "Problemmatic semi-sentient predator of the wildsteam territories, can form small raids, this creature steals. Hutt …" (`homeless:Gundark`)
- **JungleRancor**: "wildsteam jungle biom, tree breaker" (`homeless:JungleRancor`)
- **KellDragon**: "Hutt territories and area pits" (`homeless:KellDragon`)
- **Leaftail**: "wildsteam biomes" (`homeless:Leaftail`)
- **Nexu**: "combat pets of the Wildsteam" (`homeless:Nexu`)
- **PaintedSpat**: "Slot in nearly anywhere needed on dayside" (`homeless:PaintedSpat`)
- **Rikknit**: "Large tree biomes. "rikknit was a crustacean native to New Plympto. They had eight to …" (`homeless:Rikknit`)
- **Rycrit**: "herd animal near oases" (`homeless:Rycrit`)
- **SWPotF_RaceDef_ysalamir**: "Wherever needed in arid and hot zones" (`homeless:SWPotF_RaceDef_ysalamir`)
- **Tach**: "1 cell, this creature can steal, lives in the Jungle" (`homeless:Tach`)
