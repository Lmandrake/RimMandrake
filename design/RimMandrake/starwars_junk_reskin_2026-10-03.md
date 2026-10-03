# Star Wars junk reskin — vanilla ancient junk, many variants (2026-10-03)

Item: `STARWARS_JUNK_RESKIN_1` (FOUNDRY), caused by `SALVAGE_WRECKAGE_EVERYWHERE_1`.
Art list (fill_queue input, the provenance of every job): `design/RimMandrake/starwars_junk_reskin_artlist_2026-10-03.json`.

## 1. Owner ruling

Owner, typed, 2026-10-03, on `SALVAGE_WRECKAGE_EVERYWHERE_1`: *"Reskin as Star-Wars-adjacent junk. Things from
a 'world like that.' Doesn't have to be exact canon replicas of movie set examples, but try for it anyway because
we always land 'close but no cigar' and that's actually useful here. Do this right away, because we have ample art
generation capability and it really helps set the mood. And diversity that junk! Lots of different images to choose
from. Vanilla game has a depressingly small range."*

So: every prompt names a real canon design and asks for its silhouette; a near miss is acceptable output. Variety
is the goal, so every def becomes a `Graphic_Random` folder of 6-12 images.

## 2. Vanilla junk defs

**Placement.** `AncientJunkClusters` (`GenStepDef`, `Defs/Ideology/MapGeneration/CommonMapGenerator.xml`,
order 960) is a `GenStep_ScatterGroup` wired into every ordinary outdoor map through Core's
`CommonMapGenerator` (Ideology is a hard prerequisite per the all-DLC ruling, so: every map).
`countPer10kCellsRange 0.2~0.5`, `minSpacing 85`, `isJunk true`, Heavy-affordance validator, not in water,
not roofed. 9 weighted groups; the vehicle/war-machine content is groups 4 (cars), 5 (war machines),
6 (wheels) and 9 (mega-cannon). Groups 1-3, 7-8 are crates, barrels and household junk, out of scope
for this pass. (Measured from RimSage, decompiled 1.6, 2026-10-03.)

Every row below is MEASURED from `get_def_details` (raw). "Random?" says whether a `Graphic_Random`
folder can carry variants: **yes for all of them.** Graphic_Random loads each PNG in the folder as a
`Graphic_Single`, and a rotatable building draws its Single rotated, which is exactly how vanilla's own
`AncientRustedCar` (2x4, rotatable, Graphic_Random) works. So a `Graphic_Multi` def converts to
`Graphic_Random` with ONE top-down image per variant drawn in its north orientation (long axis
vertical); the game rotates it. Non-rotatable Singles just become Random.

| defName | label | group | size | drawSize | graphicClass now | texPath now | rotatable |
|---|---|---|---|---|---|---|---|
| `AncientRustedCar` | ancient car | 4 | 2x4 | (2,4) | Graphic_Random | `Things/Building/Ruins/RustedCars` | yes |
| `AncientRustedCarFrame` | ancient car frame | 4 | 2x3 | (2,3) | Graphic_Multi | `Things/Building/Ruins/RustedCarFrame` | yes |
| `AncientPodCar` | ancient pod car | 4 | 3x2 | (3,2) | Graphic_Single | `Things/Building/Ruins/PodCar` | no |
| `AncientRustedEngineBlock` | ancient engine block | 4 | 1x1 | (1,1) | Graphic_Random | `Things/Building/Ruins/RustedEngineBlock` | no |
| `AncientWheel` | ancient wheel | 1,4,6 | 1x1 | (1,1) default | Graphic_Random | `Things/Building/Ruins/Wheel` | default |
| `AncientGiantWheel` | ancient giant wheel | 6 | 2x2 | (2,2) | Graphic_Random | `Things/Building/Ruins/GiantWheel` | default |
| `AncientTankTrap` | ancient tank trap | 5 | 2x2 | (2,2) | Graphic_Random | `Things/Building/Ruins/AncientTankTrap` | no |
| `AncientAPC` | ancient ruined APC | 5 | 5x3 | (5,3) | Graphic_Single | `Things/Building/Ruins/RuinedAPC` | no |
| `AncientTank` | ancient ruined tank | 5 | 5x3 | (5,3) | Graphic_Single | `Things/Building/Ruins/RuinedTank` | no |
| `AncientRustedJeep` | ancient troop carrier | 5 | 3x5 | (3,5) | Graphic_Multi | `Things/Building/Ruins/RustedMilitaryJeep` | yes |
| `AncientLargeRustedEngineBlock` | ancient macro-engine block | 5 | 2x1 | (2,1) | Graphic_Single | `Things/Building/Ruins/LargeEngineBlock` | no |
| `AncientWarwalkerClaw` | ancient warwalker claw | 5 | 1x2 | (1,2) | Graphic_Multi | `Things/Building/Ruins/AncientWarwalkerClaw` | yes |
| `AncientWarwalkerLeg` | ancient warwalker leg | 5 | 2x4 | (2,4) | Graphic_Multi | `Things/Building/Ruins/AncientWarwalkerLeg` | yes |
| `AncientWarwalkerFoot` | ancient warwalker foot | 5 | 2x2 | (2,2) | Graphic_Single | `Things/Building/Ruins/AncientWarwalkerFoot` | no |
| `AncientWarwalkerTorso` | ancient warwalker torso | 5 | 4x6 | (4,6) | Graphic_Multi | `Things/Building/Ruins/AncientWarwalkerTorso` | yes |
| `AncientWarwalkerShell` | ancient warwalker shell | 5 | 5x3 | (5,3) | Graphic_Single | `Things/Building/Ruins/AncientWarwalkerShell` | no |
| `AncientWarspiderRemains` | ancient warspider remains | 5 | 5x5 | (5,5) | Graphic_Single | `Things/Building/Ruins/AncientWarspiderRemains` | no |
| `AncientMiniWarwalkerRemains` | ancient warsprinter remains | 5 | 5x3 | (5,3) | Graphic_Single | `Things/Building/Ruins/AncientWarsprinterRemains` | no |
| `AncientJetEngine` | ancient jet engine | 5 | 3x2 | (3,2) | Graphic_Single | `Things/Building/Ruins/JetEngine` | no |
| `AncientDropshipEngine` | ancient dropship engine | 5 | 3x2 | (3,2) | Graphic_Single | `Things/Building/Ruins/AncientDropshipEngine` | no |
| `AncientRustedDropship` | ancient dropship | 5 | 6x5 | (6,5) | Graphic_Single | `Things/Building/Ruins/AncientRustedDropship` | no |
| `AncientMegaCannonBarrel` | ancient mega-cannon barrel | 9 | 1x2 | (1,2) | Graphic_Multi | `Things/Building/Ruins/AncientMegacannonBarrel` | yes |
| `AncientMegaCannonTripod` | ancient mega-cannon platform | 9 | 3x3 | (3,3) | Graphic_Random | `Things/Building/Ruins/AncientMegacannonTripod` | no |

⚠️ `AncientRustedTruck` (2x4, Graphic_Multi, `Things/Building/Ruins/RustedTruck`) exists but is **not in any
`AncientJunkClusters` group**; it reaches maps through other placers (ruins prefabs, Odyssey mutators). It is
reskinned anyway, because the patch targets the ThingDef and so changes it wherever it appears.

**Labels and descriptions** say "car", "truck", "jet engine", "warwalker". The reskin patches those too
(§6), or a landspeeder hull reads "ancient car" in the inspect pane.
## 3. Existing art

Searched 2026-10-03 with `artpipe_state.py find` (junk, wreck, speeder, landspeeder, sandcrawler, skiff, walker,
atst, podracer, hulk, swoop, scrap, ScaldWreck) and `src/` textures.

- **`AncientPodCar` is already reskinned** as a wrecked landspeeder:
  `src/RimStarWars/StarWarsPatches/Patches/PodCarIsLandspeeder.xml` (owner request 2026-08-24) points texPath at
  `src/RimStarWars/StarWarsPatches/Textures/Things/Building/Ruins/WreckedLandspeeder.png` (512x256, Graphic_Single).
  ⇒ **Reused**: that PNG becomes variant `00` of the PodCar folder, and the existing patch is extended to the
  folder, not duplicated. Its label/description replacements stay.
- `RSW_WreckedSkiff` and `RSW_CrawlerTreadWreck` (`src/RimStarWars/StructureInjectionsSW/Textures/Things/Building/CrawlerRoad/`)
  and the Scald's `scald2_wreck*` set are **not** reused: they are the signature art of their own defs (the crawler
  road, the Scald shallows), and scattering them on every map would erase that. They are the style register the
  prompts copy.
- No podracer, AT-ST/AT-AT, swoop or crashed-starfighter art exists anywhere in the artpipe state. Everything else
  is new.

## 4. Mod home and naming

**Star Wars IP ⇒ the RimStarWars tier** (CLAUDE.md naming; `biome_mod_architecture.md` §7 Q11: a RimMandrake-tier
mod may never name Star Wars content). The variants are canon designs (X-34, AT-AT, LAAT/i), not invented names,
so Q11a's "Star Wars style is not IP" carve-out does not apply.

**Home: `mandrake.rsw.patches`** (`src/RimStarWars/StarWarsPatches/`, "RimStarWars Patches"). It already owns
the one vanilla-junk reskin (`PodCarIsLandspeeder.xml`), so this extends a precedent rather than founding a mod.
FOUNDRY may split it into its own `mandrake.rsw.ancientjunkreskin` if the Mod Settings retrofit
(`MOD_OPTIONS_RETROFIT_1`: one toggle, "Star Wars junk on/off") is easier there; that is a build call, not a ruling.

- Textures: `Textures/Things/Building/Ruins/RSW_Junk/<VanillaDefName>/RSW_Junk_<VanillaDefName>_<nn>.png`
- Artpipe job ids: `RSW_Junk_<VanillaDefName>_<nn>` (same string, so a job traces to its file by name).
- Patch file: `Patches/AncientJunk_StarWarsReskin.xml`. **No new defs and no defNames** are created; the
  vanilla defNames stay so every GenStep, prefab and ruin layout that places them keeps working.

## 5. Variant subjects per def

Canvas = drawSize x 128, doubled until the long side reaches 512 (generous per `ART_PAINTERLY_RESTORATION_1`).
Rotatable defs are drawn pointing north (long axis vertical); non-rotatable ones in their footprint's own aspect.
Full prompts are in the art-list JSON.

| def | variants | canvas | subjects (canon aim) |
|---|---|---|---|
| `AncientRustedCar` | 10 | 256x512 | an X-34 landspeeder (Luke Skywalker's, A New Hope); a SoroSuub V-35 Courier landspeeder (the Lars homestead's old family speeder); an XP-38 sport landspeeder; a Ubrikkian 9000 Z001 open landspeeder of the Mos Eisley streets; Anakin Skywalker's yellow XJ-6 airspeeder (Attack of the Clones); Zam Wesell's Koro-2 airspeeder (Attack of the Clones); a Coruscant air taxi (Attack of the Clones); a T-47 airspeeder / snowspeeder (Empire Strikes Back) crash-landed; a Mobquet Overracer-style courier landspeeder; an Imperial patrol landspeeder (Mos Eisley sandtrooper speeder, A New Hope) |
| `AncientRustedCarFrame` | 8 | 512x768 | the stripped chassis of an X-34 landspeeder; the skeleton of an Aratech 74-Z speeder bike (Return of the Jedi); the stripped frame of a Mobquet swoop bike; the gutted frame of a Flash speeder (Naboo, The Phantom Menace); the bare chassis of a Jawa ore-hauler repulsor sled; the frame of a BARC speeder (Revenge of the Sith); the stripped spaceframe of a Gian speeder (Naboo security); the skeleton of a farm repulsor cart |
| `AncientPodCar` | 8 | 768x512 | Anakin Skywalker's podracer cockpit pod (The Phantom Menace); Sebulba's podracer cockpit pod; an escape pod from a Corellian corvette (Tantive IV, A New Hope) lying on its side; a Naboo Flash speeder (The Phantom Menace); an Imperial Viper probe droid's hyperspace pod (Empire Strikes Back), cracked open; a Republic-era Gian speeder (The Phantom Menace); a sail barge personal skiff lifeboat; a Bespin cloud car (Empire Strikes Back) crash-landed |
| `AncientRustedTruck` | 8 | 256x512 | an A-A5 speeder truck (Mos Eisley / Jedha); a Trast A-A4B landspeeder truck; an Ubrikkian cargo hauler; an Imperial cargo speeder (Jedha, Rogue One); a moisture-farm utility speeder; a Mining Guild ore hauler speeder; a Jawa salvage-collection speeder; a fuel tanker landspeeder |
| `AncientRustedJeep` | 8 | 384x640 | an Imperial Troop Transport (Star Wars Rebels); the nose section of a Trade Federation MTT (multi-troop transport, The Phantom Menace); the cab section of a HAVw A6 Juggernaut (Revenge of the Sith); an Imperial TX-225 Occupier cargo variant hull (Rogue One, Jedha); a Rebel Hoth personnel speeder / armoured transport; a Republic Clone-era AT-OT carriage fallen off its legs; an Imperial K79-S80 patrol transport; an armed A-A5 'technical' converted into a troop truck |
| `AncientTank` | 8 | 640x384 | a Trade Federation AAT (Armored Assault Tank, The Phantom Menace); an Imperial TX-225 GAVw Occupier combat assault tank (Rogue One); a Republic TX-130 Saber-class fighter tank (Clone Wars); an Imperial 2-M saber hover tank (Star Wars Rebels); a Corporate Alliance NR-N99 Persuader tank droid; an InterGalactic Banking Clan IG-227 Hailfire droid (Revenge of the Sith); a Republic HAVw A6 Juggernaut hull section; a Separatist NR-N99-style droid tank turret ripped off and lying beside its hull |
| `AncientAPC` | 7 | 640x384 | a full Imperial Troop Transport (Star Wars Rebels) lying on its side, troop pods sprung open; the long side of a Trade Federation MTT (The Phantom Menace); a Republic AV-7 antivehicle artillery cannon chassis (Revenge of the Sith), barrel snapped short; an Imperial Juggernaut HAVw A5 hull with its crew tower collapsed; a Rebel shielded armoured transport from Hoth; an Imperial AT-AP-style armoured transport body with its legs gone; a Republic Clone turbo tank (HAVw A6) rear module |
| `AncientWarwalkerFoot` | 7 | 512x512 | an AT-AT foot (Empire Strikes Back); an AT-ST foot (Return of the Jedi); an AT-TE foot (Attack of the Clones); an AT-ACT foot (Rogue One); a Separatist OG-9 homing spider droid foot; an AT-DP foot (Star Wars Rebels); an AT-RT foot |
| `AncientWarwalkerLeg` | 8 | 256x512 | an AT-AT leg (Empire Strikes Back); an AT-ST leg (Return of the Jedi); an AT-TE leg segment (Attack of the Clones); an AT-ACT leg (Rogue One); a Separatist OG-9 homing spider droid leg; an AT-RT leg; an Octuptarra tri-droid leg; an AT-M6 walker forelimb (The Last Jedi) |
| `AncientWarwalkerClaw` | 8 | 256x512 | an AT-ST chin-mounted twin blaster cannon pod torn off its head; an AT-AT heavy laser cannon (chin cannon) barrel; a droideka (destroyer droid) arm with its twin blasters; a B2 super battle droid wrist-blaster arm; an AT-ST side-mounted concussion grenade launcher; a Separatist crab droid (LM-432) pincer leg; an IG-100 MagnaGuard arm with its electrostaff stub; an AT-TE mass-driver cannon barrel segment |
| `AncientWarwalkerTorso` | 7 | 512x768 | a fallen AT-AT body (Battle of Hoth); an AT-ST cockpit head with its hip joint (Battle of Endor), toppled on its back, viewport smashed; an AT-TE hull (Attack of the Clones); an AT-ACT cargo body (Rogue One); a Republic AT-OT troop carrier body (Clone Wars); an AT-M6 walker hull (The Last Jedi); an AT-DP walker cockpit and hip (Star Wars Rebels) |
| `AncientWarwalkerShell` | 7 | 640x384 | an AT-AT head (Empire Strikes Back) lying on its side; an AT-ACT head (Rogue One) torn off at the neck; an AT-ST cockpit pod split open like a nut; an AT-TE top cannon turret blown off its mount; a section of Star Destroyer hull plating fallen from orbit; a HAVw Juggernaut armour flank plate; a Trade Federation Lucrehulk hull fragment |
| `AncientWarspiderRemains` | 7 | 640x640 | a fallen Separatist OG-9 homing spider droid; a cluster of crushed DSD1 dwarf spider droids; an Octuptarra tri-droid; a Separatist LM-432 crab droid (Clone Wars); an Imperial Viper probe droid (Empire Strikes Back), enlarged by the fall; a toppled Corporate Alliance tank droid with its wheel shattered; an AT-AT neck and head assembly lying across its own broken leg |
| `AncientMiniWarwalkerRemains` | 7 | 640x384 | a sprawled AT-RT (Clone Wars recon walker); an AT-DP scout walker (Star Wars Rebels) knocked flat; three crushed droidekas half-unrolled; a BARC speeder wreck with its sidecar torn off; a Kashyyyk swamp speeder (Revenge of the Sith); an Aratech 614-AvA speeder bike (Star Wars Rebels / Andor) broken in two; a pair of crashed 74-Z speeder bikes tangled together (Endor chase) |
| `AncientJetEngine` | 8 | 768x512 | an X-wing Incom 4L4 fusial thrust engine pod (A New Hope), torn off at the S-foil; a TIE fighter hexagonal solar panel wing lying flat, frame bent; a Y-wing engine nacelle with its exposed rear thrust cone; a podracer engine (Anakin's Radon-Ulzer 620C, The Phantom Menace); Sebulba's Collor Pondrat Plug-F Mammoth podracer engine; an A-wing sublight engine pair; a Naboo N-1 starfighter engine pod with its chrome finned tail; a TIE interceptor dagger wing |
| `AncientDropshipEngine` | 7 | 768x512 | a Lambda-class shuttle sublight engine block (Return of the Jedi); a Republic LAAT/i gunship rear engine and tail fin assembly; a YT-1300 freighter sublight drive grille section (Millennium Falcon pattern); a Sentinel-class landing craft engine cluster; a Gozanti cruiser engine nacelle; a Ghtroc 720 freighter thruster pod; a hyperdrive motivator housing from a light freighter |
| `AncientRustedDropship` | 12 | 768x640 | a crashed Republic LAAT/i gunship (Attack of the Clones); a crashed Lambda-class shuttle (Return of the Jedi); a crashed X-wing (A New Hope); a crashed TIE fighter; a crashed BTL Y-wing; a crashed Sentinel-class Imperial landing craft; a crashed Naboo N-1 starfighter; a crashed B-wing; the front cockpit section of a YT-1300 light freighter (Millennium Falcon pattern); a crashed TIE bomber; a crashed Sith Infiltrator-style needle ship (The Phantom Menace) with folded wings; a crashed Gozanti-class cruiser pod section |
| `AncientRustedEngineBlock` | 8 | 512x512 | a GNK power droid (the 'Gonk' droid) toppled over, box body dented; a dome-less R2-series astromech droid body lying on its side; a hyperdrive motivator unit with cables spilling out; a power converter (the kind Luke wanted to pick up at Tosche Station); a repulsorlift coil unit, cracked casing; a protocol droid head (C-3PO pattern), eyes dark; a B1 battle droid torso folded in half; an MSE-6 mouse droid flattened |
| `AncientLargeRustedEngineBlock` | 7 | 512x256 | a fallen Tatooine moisture vaporator lying on its side; a CLL-6 binary load lifter droid lying flat (A New Hope); a long hyperdrive core assembly; a sublight ion thruster stack; a twin landspeeder turbine pair still bolted to a mount; a sandcrawler drive bogie with tread rollers; a dead Imperial probe-droid power core, long and ribbed |
| `AncientWheel` | 8 | 512x512 | a droideka curled into its wheel form, cracked; a B1 battle droid head; an astromech droid leg with its tread foot; a small repulsor disc emitter; a sandcrawler drive sprocket; an MSE-6 mouse droid on its side; a GNK power droid foot; a TIE fighter cockpit hatch |
| `AncientGiantWheel` | 7 | 512x512 | an IG-227 Hailfire droid hoop wheel, broken off; a sandcrawler tread segment curled up; a Republic Juggernaut drive wheel; a Corporate Alliance tank droid central wheel; a big sandcrawler drive sprocket with broken teeth; a repulsor array ring from a cargo skiff; an Imperial Occupier tank track wheel set |
| `AncientTankTrap` | 7 | 512x512 | an Imperial durasteel blast barrier (Jedha, Rogue One); a Rebel Hoth trench barricade post with a dead shield emitter; a Separatist energy shield emitter pylon, dark; an Imperial checkpoint barrier pylon with warning stripes worn away; a Star-Wars-styled durasteel hedgehog of three angled beams; a Clone Wars Republic barricade pylon; a Mos Eisley crowd-control barrier block |
| `AncientMegaCannonBarrel` | 6 | 256x512 | a DF.9 anti-infantry battery barrel (Battle of Hoth); a Republic turbolaser barrel segment; a Rebel P-tower dish-gun emitter mast; an Imperial E-web heavy repeating blaster, oversized and fallen; a Separatist AAT main cannon barrel; an AT-TE mass-driver cannon barrel |
| `AncientMegaCannonTripod` | 6 | 768x768 | a DF.9 anti-infantry battery turret base (Battle of Hoth); a Rebel P-tower dish-gun base; a KDY v-150 Planet Defender ion cannon base fragment (Hoth); an Imperial turbolaser emplacement base; a Separatist anti-air battery tripod; a Republic SPHA-T artillery walker turret base |

## 6. Patch shape

Per def, in `Patches/AncientJunk_StarWarsReskin.xml`, plain `PatchOperationReplace` (vanilla + DLC defs, all
present by the all-DLC ruling, so **no `MayRequire` and no FindMod guard**; and `MayRequire` on an `<Operation>`
is inert anyway):

```xml
<Operation Class="PatchOperationReplace">
  <xpath>/Defs/ThingDef[defName="AncientTank"]/graphicData/texPath</xpath>
  <value><texPath>Things/Building/Ruins/RSW_Junk/AncientTank</texPath></value>
</Operation>
<Operation Class="PatchOperationReplace">
  <xpath>/Defs/ThingDef[defName="AncientTank"]/graphicData/graphicClass</xpath>
  <value><graphicClass>Graphic_Random</graphicClass></value>
</Operation>
```

- **graphicClass**: replace with `Graphic_Random` on the 14 defs that are `Graphic_Single`/`Graphic_Multi` today
  (the 9 already-Random ones need only texPath). Graphic_Multi → Graphic_Random is correct for the rotatable
  defs: each folder PNG loads as a Single and is drawn rotated, as vanilla's own `AncientRustedCar` does.
- **drawSize / size / shadowData / passability / HP / killedLeavings: untouched.** Appearance only, same contract
  as `PodCarIsLandspeeder.xml`.
- **label + description**: replace on every def (an X-wing must not inspect as "ancient jet engine"). Labels go
  generic because one def now shows many designs: "starship wreck", "walker leg", "speeder hulk",
  "droid tank hulk", etc. Descriptions: one paragraph of "looted generations ago" prose in the Star Wars register.
- `AncientWheel` has no explicit `drawSize`/`size` (inherits 1x1); do not add one.
- **Curation before wiring.** The owner asked for "lots of images to choose from", so a review sheet of the
  finished jobs (`review-sheets` skill, keep/cut per image) comes before copying PNGs into the folders. Only kept
  images ship; a folder with zero keeps leaves that def's texPath unpatched.
- Verify offline with `validate_patch.py --defs`, then one quicktest look (no flyers involved, so a solo bridge
  pass is allowed) to confirm rotated Multi→Random defs draw the right way round.

## 7. Art queue

**184 jobs filed 2026-10-03** to `D:\Luke\dev\_artpipe\pending\` by `fill_queue.py` from the art-list JSON,
`rimflow_item_id STARWARS_JUNK_RESKIN_1`, priority 60, channel codex, transparent background, no reference image
(new art, not reskins of the vanilla sprite). Per def: see the variants column in §5 (6-12 each, 12 for the
crashed-starship `AncientRustedDropship`, 10 for `AncientRustedCar`). `AncientRustedTruck` is in the 184 although
the junk GenStep does not place it (§2 note).
