# Workshop Star Wars proper-noun raid — Batch B

Disk raid of Steam Workshop mod folders at
`/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/<id>/`.
All 29 target packageIds were located on disk. Ten of them were not found by their
own packageId string in the mega-regex sweep because they turned out to belong to
**separate workshop items with their own numeric folder** (not bundled inside a
sibling mod's About.xml) — a second, broader keyword sweep found all ten.

## PackageId -> folder map (all 29 located)

| packageId | Workshop folder | Mod name | Verdict |
|---|---|---|---|
| mlie.starwarsanimalcollection | 3497316713 | Star Wars Animal Collection (Continued) | **SW-themed** |
| lee.theforce.lightsaber | 3466124712 | (The Force: Lightsabers) | **SW-themed** |
| guy762.mm.kotorcore | 3254370945 | (KotOR Core, "Modern Mando"?) | **SW-themed** |
| btd.gbp.shippack.kotor.vge | 3614012898 | KotOR Gravship Blueprint pack | **SW-themed** |
| neronix17.outerrim.core | 2919227155 | Outer Rim - Core | **SW-themed** |
| neronix17.outerrim.galacticempire | 2919248699 | Outer Rim - Galactic Empire | **SW-themed** |
| neronix17.outerrim.rebelalliance | 2919249903 | Outer Rim - Rebel Alliance | **SW-themed** |
| neronix17.outerrim.furnitureanddecor | 2919553599 | Outer Rim - Furniture and Decor | **SW-themed** |
| neronix17.outland.genetics | 2910172297 | Outland Genetics | NOT SW-themed (generic alien-gene framework; see note) |
| neronix17.shieldgenerators | 2540563802 | Shield Generators | NOT meaningfully SW-themed (see note) |
| neronix17.retexture.charactereditor | 2855844396 | Character Editor Retextured | NOT SW-themed (UI retexture utility) |
| neronix17.toolbox | 1660622094 | Tabula Rasa (neronix17 Toolbox) | NOT SW-themed (shared dependency framework) |
| xylthixlm.races.core | 3521814323 | Posthuman Drift Core Mod | NOT SW-themed (generic posthuman xenotype series) |
| xylthixlm.races.titan | 3540820354 | Posthuman Drift Titan Xenotype | NOT SW-themed |
| det.avaloi | 3199692643 | Det's Xenotypes - Avaloi | NOT SW-themed (author initials "Det", invented fantasy name) |
| det.boglegs | 3146564944 | Det's Xenotypes - Boglegs | NOT SW-themed |
| det.brawnum | 3429572581 | Det's Xenotypes - Brawnum | NOT SW-themed |
| det.buzzers | 3545293786 | Det's Xenotypes - Buzzers | NOT SW-themed |
| det.keshig | 3376864722 | Det's Xenotypes - Keshig | NOT SW-themed |
| det.venators | 3140248688 | Det's Xenotypes - Venators | Borderline — name only (see note) |
| det.epochsincense | 3072579620 | Epochs - Incense | NOT SW-themed (decorative building mod) |
| det.epochspyrinth | 3336544632 | Epochs - Pyrinth | NOT SW-themed |
| teiwaz.gtgtradercore | 3682209120 | GTG Trader Core | NOT SW-themed (generic trader framework) |
| teiwaz.taajg | 3729570505 | [GTG]Traders Accept All Junk Gear | NOT SW-themed |
| teiwaz.tacac | 3756658373 | [GTG]Traders Accept Chunks & Corpses | NOT SW-themed |
| chezhou.creature.sandworm | 3713982815 | LEVIATHANS:SANDWORM | NOT SW-themed (Dune/generic desert-monster hunt) |
| karew.orcclan | 3232348025 | Orc Clan + Xenotype | NOT SW-themed (fantasy orcs) |
| gravtide.mod | 3779600989 | GravTide | NOT SW-themed (Odyssey gravship ocean-diving mod) |
| vanillaracesexpanded.starjack | 3531912428 | Vanilla Races Expanded - Starjack | NOT SW-themed (generic VRE zero-g xenotype) |

**Confirmed genuinely Star Wars: 8 of 29** (animal collection, lightsaber, KotOR
core, KotOR ship pack, Outer Rim Core/Empire/Rebel Alliance/Furniture). The
remaining 21 are either non-SW despite evocative names (confirming the task's
warning about `det.*` being author initials) or are generic
frameworks/dependencies that other SW mods build on top of but carry no SW
content themselves.

---

## Creature / species

Source: `mlie.starwarsanimalcollection` (3497316713),
`.../1.6/Defs/ThingDefs_Races/*.xml`. ~160 canonical Star Wars creature
species, one ThingDef each (defName = species name, verified from XML). Full
list (defNames, alphabetical):

Acklay, Aiwha, Akk (dog), Anooba, Bantha, Behemoth, Beldon, Blarth, Blixus,
Blurrg, Boarwolf, Bogwing, Bolotaur, Boma, Borcatu, Bordok, Brezak, Bursa,
Can-cell, Cannok, Chrysalide Rancor, Clodhopper, Convor, Corellian Hound,
Corinathoth, Dactillion, Dalgo, Devourers, Dewback, Dianoga, Dragonsnake,
Drexl, Energy Spider, Eopie, Falumpaset, Fambaa, Fanback, Feral Grazer, Feral
Nerf, Frilled Gorg, Frog-dog, Gelagrub, Gizka, Gorg, Gornt, Granite Slug,
Grank, Grazer, Greater Krayt Dragon, Gualaar, Gullipud, Gundark, Gutkurr,
Harvester Beetle, Hawk-bat, Horax, Hrumph, Hssiss, Igitz, Insectomorph, Iriaz,
Iridonian Reek, Ithorian Reek, Jakobeast, Jamel, Jimvu, Jungle Rancor, Kaadu,
Katarn, Kell Dragon, Kinrath, Klorslug, Kowakian Monkey-Lizard, Krayt Dragon,
Kreetle, Krykna, Kwazel Maw, Kwi, Kybuck, Lava Flea, Leaftail, Longtail Gorg,
Loth-Wolf, Lothcat, Lylek, Maalraas, Manka (cat), Marsh Haunt, Massiff, Mastiff
Phalone, Mastmot, Mawvorr, Mott, Mudhorn, Mynock, Narglatch, Neebray, Nerf,
Nexu, Nuna, Ollopom, Orray, Painted Spat, Peko-peko, Pikobis, Porg,
Pufferpig, Qormot, Rancor, Raxshir, Reek, Rikknit, Roggwart, Ronto, Runyip,
Rycrit, Scavrat, Scurrier, Shaak, Shiro (+ ShiroTrap), Shyrack, Silooth,
Skalder, Sketto, Snoruuk, Squall, Stintaril, Strill, Tach, Taozin, Tauntaun,
Tee-muss, Tetniss Crab, Thranta, Tibidee, Tooke, Torton, Tukata, Tusk-cat,
Urusai, Uvak, Vapaad, Varactyl, Veermok, Voorpak, Vornskyr, Vulptex, Wampa,
War Wyrm, Warbird, Whisperbird, Womp Rat, Woolamander, Worrt, Wraid,
Wyyyschokk, Yobshrimp, Zakkeg, Zeer.

Note: all canon SW creature names, faithfully spelled per the mod's own
defNames; no invented species found in this list.

---

## Characters

Source: `lee.theforce.lightsaber` (3466124712), `.../1.6/Defs/ThingDefs_Misc/HiltDefs/*.xml`
(defName pattern `Force_LightsaberHilt_<Character>`) and `Force_LightsaberIgniton_*`
(saber-color-per-character ignition effects). Each is a purchasable/craftable hilt
styled after a canon character's lightsaber — not a pawn or def *of* the
character, just an item named for them.

| Character | Note |
|---|---|
| Aayla (Secura) | hilt |
| Ahsoka Tano (+ "Ahsoka2", "AhsokaShoto") | hilt, incl. shoto variant |
| Anakin (Skywalker) (Anakin1, Anakin2, BlueAnakinEPII ignition) | hilt |
| Asajj (Ventress) | hilt |
| Bastila Shan | KOTOR hilt |
| Cal Kestis (BlueCalKestis ignition) | Jedi: Fallen Order |
| Count Dooku | hilt + Red Dooku ignition |
| Darth Bane | hilt |
| Darth Malgus | hilt |
| Darth Maul (+ Red Maul ignition) | hilt |
| Darth Nihilus | KOTOR2 hilt |
| Darth Vader (+ Red D. Vader ignition) | hilt |
| Desann | Jedi Outcast villain hilt |
| Even Piell | hilt |
| Exar Kun | KOTOR-era hilt |
| Ezra (Bridger) (Ezra2, EzraBlaster, GreenEzra/BlueEzraBlaster ignition) | incl. his blaster-lightsaber |
| Galen Marek ("GalenMalek") | Force Unleashed hilt |
| Gungi | Wookiee Jedi hilt |
| Jaden Korr | Jedi Academy hilt |
| Jaro Tapal | hilt |
| Kanan Jarrus (+ BlueKananJarrus ignition) | hilt |
| Karness Muur | Old Republic hilt |
| Ki-Adi-Mundi ("KiAudi") | hilt |
| Kirak Infila | hilt |
| Kit Fisto | hilt |
| Kyle Katarn | Jedi Knight series hilt |
| Kylo Ren (RedKRen ignition) | hilt |
| Luke (Skywalker) (+ GreenLuke ignition) | hilt |
| Mace (Windu) | hilt |
| Mara Jade | hilt |
| Obi-Wan (Kenobi) (ObiWan1, ObiWan2, BlueObi-Wan ignition) | hilt |
| Oppo Rancisis | hilt |
| Ploo Koon ("PloKoon") | hilt |
| Pong Krell | hilt |
| Qui-Gon (Jinn) (+ GreenQuiGon ignition) | hilt |
| Quinlan Vos | hilt |
| Revan (Revan2) | KOTOR hilt |
| Saesee (Tiin) | hilt |
| Satele Shan | Old Republic hilt |
| Shaak Ti | hilt |
| Sharad Hett | hilt |
| Sidious (Palpatine) (+ RedSidious ignition) | hilt |
| Sion | KOTOR2 hilt |
| Tenel Ka Djo | Legends-era hilt |
| Ulic Qel-Droma | hilt |
| Ven Zallow | hilt |
| Vernestra Rwoh | High Republic hilt |
| Yoda (+ GreenYoda ignition) | hilt |
| Arn Peralun, Jinsu Razor, Karkko | minor/EU character hilts (not independently verified) |

Note: this is the single largest character roster of any mod in this batch —
Jedi Academy/Jedi Knight game characters (Desann, Kyle Katarn, Jaden Korr,
Rosh Penin-adjacent) sit alongside prequel/OT/sequel-trilogy and KOTOR
characters, confirming the mod draws from the full breadth of SW media, not
just the films.

Also from `guy762.mm.kotorcore` (3254370945), `AdditionalMods/_FactionsBase`:
named NPC-type namers/titles reference **Jerec** (Dark Jedi, *Jedi Knight*),
**Xim** (Xim the Despot, ancient pre-Republic conqueror), and **Thrawn**
(`guy762_IdeoIcon_thrawn7th` — Thrawn's 7th Fleet).

Also `neronix17.outerrim.furnitureanddecor` (2919553599),
`ThingDefs_Buildings`: four original (non-canon) NPC statue names —
`OuterRim_SageOfDwartii_BraataDanlos`, `_FayaRodemos`, `_SistrosNevet`,
`_YanjonZelmar` — decorative "Sage of Dwartii" statues; **Dwartii** and the
"Sages of Dwartii" title are canon (Old Republic-era Coruscant statuary from
KOTOR); the four individual sage names appear to be original additions, not
verified as canon.

---

## Factions / organizations

Source: `neronix17.outerrim.core` (2919227155) `FactionDefs`,
`neronix17.outerrim.galacticempire` (2919248699) `FactionDefs`,
`neronix17.outerrim.rebelalliance` (2919249903) `FactionDefs`:

| Faction | defName | Note |
|---|---|---|
| Binary Star Raiders | OuterRim_BinaryStarRaiders | original raider faction, Tatooine-flavored name |
| Moisture Farmers | OuterRim_MoistureFarmers | original settler faction |
| Galactic Empire | OuterRim_GalacticEmpire (+ OuterRim_EmpirePlayerFaction) | canon; see also `MEMORY: galactic-empire-is-reskinned-vanilla.md` |
| Rebel Alliance | OuterRim_RebelAlliance (+ OuterRim_RebelPlayerFaction) | canon |

Source: `neronix17.outerrim.furnitureanddecor` (2919553599),
`ThingDefs_Buildings` — ~170 `OuterRim_Decal_*` wall-decal defs, each a
faction/company/organization logo. This is the single richest canon-name
trove in the batch. Representative list (all are canon Star Wars
organizations unless noted):

Alphabet Squadron, Ashla / Bogan (Force light/dark-side terms, old-canon),
Baktoid Armor Workshop, Balmorran Arms, BlasTech Industries, Black Squadron,
Black Sun, Blade Squadron, Broken Horn Syndicate, Cestus Cybernetics, Chiss
Ascendancy, Cobalt Squadron, Coloacid Creation Nest, Commerce Guild,
Confederacy of Independent Systems, Corellian Engineering Corporation,
Coruscant Health Administration, Coruscant Security Force, Crimson Dawn,
Czerka Corp, Damorian Manufacturing Corp, Dark Lord of the Sith, Durand Crime
Family, Dynamic Automata, First Order, Fromm Gang, Fulcrum (Ahsoka Tano's
codename), Galactic Empire, Galactic Republic (+ Clone Wars-era variant),
Galactic Senate, Gallofree Yards Inc, Garbis Family, Genetech Corp, Golan
Arms, Gold Squadron, Grievous, Guavian Death Gang, Gungans, Hapes Consortium,
Havoc Squad, Haxion Brood, Hutt Clan, Imperial Cloning, Imperial Department of
Military Research, Imperial Information Office, Imperial Munitions, Imperial
Press Corps, Incom Corp, Inferno Squad, Infinite Empire (Rakatan), Ivax
Syndicate, Jedi Order, Jedi Younglings, Kajidic (Hutt crime family/business
structure), Kamino Cloning, Kamino Security, Kanjiklub, Kintan Striders,
Koensayr Manufacturing, KotOR Republic, Kouhun, Kuat Drive Yards, Leisure Mech
Enterprises, Lok Revenants, Loronar Corporation, MandalMotors, Medtech
Industries, Merr-Sonn Munitions Inc, Mon Calamari Shipyards, Naboo Royals, New
Republic, Nihil Raiders, Noble Court, Ohnaka Gang, Old Republic, Onderon
Rebels, Oriolanis Defense Systems, Pantolomin Shipwrights, Partisans, Pyke
Syndicate, Ranc Gang, Rebaxan Columni, Rebel Alliance (+ Rebel Alliance
Intelligence), Rebel Squadron, Regallis Engineering, Rendili StarDrive,
Republic Navy, Resistance, Revan's Sith Empire, Roche Hive, Sienar Fleet
Systems, Sith, Sith Empire, Sith Eternal, Skystrike Academy, Slayn & Korpil,
SoroSuub Corp, Starbird (Rebel emblem), Starlight Squadron, Sublight Products
Corp, Tarkin Initiative, Techno Union, Telgorn Corp, Tendrando Arms, The
Exchange, Theed Palace Engineering Corps, Trade Federation, Trade Spine
League, Twilight Company, Udrane Galactic Electronics, Vanguard Squadron,
Vong (Yuuzhan Vong), Warbird Gang, Xisor Transport Systems, Zann Consortium.

(Plus one non-Star-Wars outlier decal in the same folder: `AccuTronics` — not
independently verified as canon.)

Source: `guy762.mm.kotorcore` (3254370945),
`AdditionalMods/_FactionsBase` (`guy762_IdeoIcon_*`, `guy762_FactionColor_*`,
`guy762_culture_*`): Mandalorians (+ Neo-Crusaders), Sith, Jedi, Hutts (2
icon variants), Czerka, Eriadu, Old/New Republic, Rebels, Empire (+ "Dark
Empire"), Imperial Remnant, Pentastar Alignment, Zsinj (Warlord Zsinj's
faction), Maldrood (Moff Kaine's Maldrood), Trandoshans ("trando"), Khoonda
(KOTOR2 Onderon-region settlement), core worlds / outer rim / mando / sith /
exchange cultures.

---

## Planets / locations

| Planet | Source | Note |
|---|---|---|
| Tatooine | guy762.mm.kotorcore, `AdditionalMods/LayeredAtmosphereOrbit/Defs/Planets_Tatooine` | full planet layer, orbit layer, biomes (Extreme Desert, Highland), granite/sandstone stone types |
| Coruscant | neronix17.outerrim.furnitureanddecor (furniture set: bed/table/dresser line); guy762 (Coruscant Health Administration/Security Force decals) | furniture line named for the planet |
| Corellia | neronix17.outerrim.furnitureanddecor (furniture set) | furniture line |
| Dathomir | neronix17.outerrim.furnitureanddecor (`DathomirOrbLamp`, `DathomirSunLamp`) | lamp line |
| Onderon | guy762.mm.kotorcore (`guy762_Hat_onderon`, `guy762_Robes_onderon`, "Onderon Rebels" decal) | apparel + faction decal |
| Ilum, Jedha, Christophsis, Dantari (likely Dantooine), Kimber (Kimber Station) | lee.theforce.lightsaber (kyber-crystal-source hilt-part names: `IlumCrystalHiltPart`, `JedhaCrystalHiltPart`, `ChristophsisCrystalHiltPart`, `DantariCrystalHiltPart`, `KimberStoneHiltPart`) | named as crystal-source worlds, not built as locations |
| Eriadu | guy762.mm.kotorcore (`guy762_FactionColor_EriaduMint`, `guy762_glove_eriadu`, `guy762_stealthbelt_eriadu`, "Eriadu" decal) | referenced only via item/decal naming |
| Kamino, Naboo, Endor | neronix17 mods (Kamino Cloning/Security decals; Naboo Royals decal; `OuterRim_RebelEndorTrooper` pawnkind) | referenced via decal/pawnkind naming only, no built terrain |

---

## Ships / vehicles

Source: `btd.gbp.shippack.kotor.vge` (3614012898),
`Gravship Blueprints/KotOR/*.btd`: two gravship blueprints —

- **Dynamic-class Freighter** (`Dynamic_Class_Freighter.btd`) — canon KOTOR-era
  ship class (the *Ebon Hawk* is a modified Dynamic-class light freighter).
- **KT-400 Freighter** (`KT_400_Freighter.btd`) — not independently verified as
  a canon ship designation; likely an original/expanded-universe-adjacent name
  used for this blueprint.

Same mod ships an incident (`BTD_DroidDistressCall`) with quest names "Crashed
Freighter Signal" and "Droid Rescue Mission", and references droid colonist
pawnkinds (`KotORDroidColonist_GOTO`, `_T3UD`, etc. — GOTO and the T3 astromech
line are canon KOTOR II droids) that are actually *defined* in a sibling
workshop item (`guy762.KotORDroids`, not one of the 29 targeted packageIds) —
noted for completeness, not extracted in depth since it is out of scope.

---

## Items / materials / weapons

**Lightsaber crystals & hilt parts** (lee.theforce.lightsaber, 3466124712):
Kyber Crystal, Adegan Crystal, Bled Crystal / Cleansed Crystal (Sith-corrupted
vs. purified kyber), Synthetic Crystal, Barab Ingot, Dantari Crystal, Dragite
Crystal, Ghostfire Crystal, Ilum Crystal, Jedha Crystal, Kaiburr Crystal
(canon — the powerful Force-crystal from *Kaiburr* on Mimban), Kimber Stone,
Krayt Dragon Pearl, Lorrdian Gemstone, Mephite Crystal, Nishalorite Stone,
Pontite Crystal, Solari Crystal, Sorian Crystal, Thontiin Crystal, Varpeline
Crystal, Zophis Crystal, Christophsis Crystal. Named lightsaber types: the
**Darksaber**, **Broadsaber**, **Protosaber**, **Soul Saber**. Lightsaber
combat forms (all seven canon forms): Form I Shii-Cho, Form II Makashi, Form
III Soresu, Form IV Ataru, Form V Shien/Djem So, Form VI Niman, Form VII
Juyo/Vaapad.

**Materials/resources** (guy762.mm.kotorcore, 3254370945): Beskar (Mandalorian
iron), Cortosis, Durasteel, Bronzium, Rhydonium (fuel), Tibanna (gas), Kolto
(bacta-analog healing fluid), Stygium Crystal (cloaking-device crystal),
Plastoid, Duracrete, Spice (canon SW drug/currency good), Armorweave,
Synthread; **Czerka Corporation** and **Aratech** referenced as
gear-brand-name prefixes (`guy762_belt_czerka`, `guy762_belt_aratechcr`);
in-game currency named **Credits** (`guy762_KotORcredits`).

**Weapons** (neronix17 Outer Rim Core/Empire/Rebel Alliance, and
guy762.mm.kotorcore): named after canon SW blaster/weapon model designations —
E-11 Blaster Rifle, E-11D, DLT-19 Heavy Blaster Rifle, DLT-19X Targeting
Blaster, DLT-20A, SE-14R, EC-17, D-72 Oppressor, TL-50 Heavy Repeater, A180 /
A280 Blaster, DH-17 Pistol/Rifle, HH-12 Rocket Launcher, K-16 Bryar Blaster
(canon "Bryar pistol" model), T-21 Repeating Blaster, Gaderffii Stick (canon
Tusken Raider "gaffi stick"), Vibroblade/Vibroaxe/Vibrocleaver/Vibrodagger/
Vibro-double-blade/Vibroglaive (canon vibroweapon family), Thermal Detonator,
Aurebesh (the Star Wars writing script — reproduced as decorative decal
letters and whole words, e.g. "Armory", "Hangar", "Reactor").

---

## Not Star Wars themed — verified and set aside

- **det.avaloi / det.boglegs / det.brawnum / det.buzzers / det.keshig** —
  DetVisor's "Det's Xenotypes" series; invented fantasy-flavored xenotype
  names (poets/artists, traders, laborers, waste-eaters, warriors) with no SW
  connection. `det.` = author initials, confirming the task's warning.
- **det.epochsincense / det.epochspyrinth** — DetVisor's "Epochs" decorative
  building series (incense, non-refuelable torches/heaters); unrelated theme.
- **det.venators** — borderline: the name "Venators" echoes the canon
  Venator-class Star Destroyer, but the mod itself is a generic
  paralysis-focused human xenotype with no other SW content; likely a naming
  homage only, not treated as substantive SW content.
- **teiwaz.gtgtradercore / teiwaz.taajg / teiwaz.tacac** — "GTG" trader-utility
  framework (junk/corpse buyback patches); no SW content.
- **xylthixlm.races.core / xylthixlm.races.titan** — "Posthuman Drift" is a
  generic sci-fi xenotype series (space-adapted humans); no SW naming or lore.
- **karew.orcclan** — fantasy orc-clan faction/xenotype; unrelated genre.
- **gravtide.mod** — Odyssey-DLC gravship ocean-diving mod; no SW content.
- **chezhou.creature.sandworm** — "LEVIATHANS: SANDWORM", a Syndicate-contract
  sandworm hunt (Chinese-language description); reads as Dune-esque/generic
  desert monster, not Star Wars.
- **vanillaracesexpanded.starjack** — part of the generic "Vanilla Races
  Expanded" series; a zero-gravity/space-adapted xenotype unconnected to Star
  Wars despite the "Starjack" name.
- **neronix17.outland.genetics** — a generic alien-gene/xenotype **framework**
  (arachnid/bovine/canid head types, body-scale genes, aura systems) used as a
  shared dependency by neronix17's actual SW mods; contains no SW-specific
  gene or species names itself (checked for Wookiee/Twi'lek/Rodian/Zabrak/
  Trandoshan/Mon Calamari/Sullustan/Ewok/Jawa/Hutt/Gungan/Nautolan/Togruta/
  Chiss/Duros/Bothan — zero hits).
- **neronix17.shieldgenerators** — generic personal/base shield-generator tech;
  its three named shield-tier defNames are joke names (`Shield_Astroglide`,
  `Shield_Durex`, `Shield_Trojan` — condom brands), not SW terms.
- **neronix17.retexture.charactereditor** — a pure UI-texture reskin of the
  vanilla Character Editor mod; no thematic content to extract.
- **neronix17.toolbox** — shared code/dependency framework ("Tabula Rasa")
  underlying multiple neronix17 mods; no thematic content.
