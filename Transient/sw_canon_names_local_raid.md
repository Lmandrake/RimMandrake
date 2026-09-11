# Star Wars canon name list — LOCAL DISK RAID (2026-09-11)

Owner ruling, verbatim: *"Right now start making a canon Star Wars name list.
Raid the past mods to build it even the donors we've retired. Additional web
searches can add to it easily especially those on wookiepedia. Star Wars name
list."*

This file is the **LOCAL/DISK half only** — four parallel sub-agents raided
this machine (no web access). A separate agent covered live web research
(Wookieepedia etc.) in parallel; that output is a different file. **This is
Transient staging** per repo convention — a follow-up merge pass combines this
with the web-research file into a real `design/` canonical reference. Do not
treat this file itself as the canonical doc.

Sources raided (see full detail files, kept alongside this one in `Transient/`
for the merge pass to consult if needed):
- **A** = `_raid_tmp_A_firstparty.md` — deployed first-party "mandrake" mods at
  `/mnt/c/.../RimWorld/Mods/` (Armoury, Droidworks, SWBestiary, StarWarsRaces,
  StarWarsPatches, all the `*ArtOverride` creature-reskin mods, UtinniPatches, etc.)
- **B** = `_raid_tmp_B_workshop.md` — 29 currently-active third-party Workshop
  mods checked; 8 confirmed genuinely Star Wars themed (Star Wars Animal
  Collection, The Force: Lightsabers, KotOR Core, KotOR Gravship pack, Outer
  Rim Core/Empire/Rebel Alliance/Furniture); 21 ruled NOT Star Wars themed
  despite evocative names/packageIds (see "Traps" section below).
- **C** = `_raid_tmp_C_retired.md` — 12 retired/donor Star-Wars-themed
  packageIds (once active, now removed from the live mod list), 10 of which
  still have cached Workshop content on disk.
- **D** = `_raid_tmp_D_repodocs.md` — this repo's own worldbuilding docs,
  `donor_proper_noun_backlog.md`, the `ART_REGEN_WAVE1-5` item files, and git
  log — i.e. judgment calls this campaign has ALREADY made about canon-vs-reimagined.

**Total raw name volume**: several hundred proper nouns across ~50 mods/docs.
No attempt was made at perfect global deduplication — a name appearing in two
sources is listed with both, since the merge step needs the provenance more
than it needs a single row. Spelling is taken from the most authoritative
source available (a live ThingDef/XenotypeDef defName beats a folder name
beats a prose reference).

---

## ⚠️ Flagged findings — read before using this list

These are bugs/traps/rulings this raid surfaced, not just names. A later
canon-doc merge should carry these forward as warnings, not just data:

1. **The live lightsaber-name generator is NOT Star Wars.**
   `Armoury/Defs/Absorbed_KotorWeapons/ThingDefs_Weapons/Absorbed_KotorWeapons_lightsabernames.xml`
   (RulePackDef `NamerWeaponLightsaber`) — its entire name table is **Final
   Fantasy VI** character/esper names (Terra, Kefka, Shiva, Bahamut, Cait
   Sith, Ragnarok, Bismarck, etc.), a leftover donor template currently wired
   to generate in-game lightsaber names for this campaign. [A]

2. **Several "ArtOverride" mods are NOT Star Wars** despite living in a
   creature-reskin pipeline alongside genuine SW creatures: **Grithe**
   (donor `GR_ParagonRat`), **Grutt** (`GR_Molebear`), **Kroffa**
   (`BMT_Maligoat`), **Puffmite** (`BMT_FleeceSpider`), **Spidercat**
   (`GR_Spidercat`, art-only, donor name untouched), **Lockjaw**
   (`AA_Lockjaw`, Alpha Animals donor, untouched) — these are campaign-original
   relabels of non-SW donor creatures. Do not add them to a "real SW creature"
   canon doc. [A, D confirms via ART_REGEN_WAVE4/5]

3. **`SWBestiary` (first-party mod) contains non-SW content under an SW name**:
   absorbed "Jurassic Rimworld" dinosaurs (Diplocaulus, Segnosaurus,
   Platyhystrix, Protovermes, Protosolpuga, Baseopsis, Termitotron,
   Holcorobeus — flavor text literally styled "INGEN INTERNAL CASE FILE" /
   "BIOSYN"), plus ~70 absorbed BiomesTeam cave/biome creatures (Pod Worm,
   Royal Rhino Beetle, Yooka, Maligoat, Fleece Spider, Basilisk, etc.) — zero
   Star Wars content despite the mod's name. [A]

4. **`Sov.Sith` (retired mod, "Rimwars:Pureblood Xenotype")** never actually
   says "Sith" anywhere in its own XenotypeDef label/description — it's a
   generic crimson-skinned xenohuman. Don't cite this mod as proof a "Sith
   Pureblood" xenotype was ever explicitly authored on disk; only the flavor
   (crimson skin, bone ridges, psychic sensitivity) matches. [C]

5. **`det.venators`** (active third-party mod) echoes the canon Venator-class
   Star Destroyer in name only — its actual content is a generic
   paralysis-focused human xenotype, unrelated. Same "author-initials, not SW"
   pattern applies to all five `det.*` xenotype mods and the two `det.epochs*`
   decor mods, plus `teiwaz.*`, `xylthixlm.races.*`, `karew.orcclan`,
   `gravtide.mod`, `chezhou.creature.sandworm`, `vanillaracesexpanded.starjack`
   — all checked and ruled NOT Star Wars despite sounding like it. [B]

6. **"Horax"** (this campaign's ART_REGEN_WAVE1 labels it a genuine SW-canon
   "redo" creature) is a **different thing** from **`HoraxCult`**, the vanilla
   RimWorld Anomaly DLC faction — already explicitly ruled out-of-scope/not
   Star Wars by `donor_proper_noun_backlog.md`. Verify "Horax" independently
   before treating it as settled canon; the two names are easy to conflate. [A, D]

7. **`killathon.artificialbeings.syncore`** (retired) has an unresolved
   donor-header mismatch: the repo's dependency chain treats it as a separate
   "SynCore" mod, but the Workshop folder it should own
   (`Killathon.ArtificialBeings`, 3288463094) self-declares packageId
   `Killathon.ArtificialBeings` with no `.syncore` suffix — no folder on disk
   actually declares the `.syncore` packageId. Name recovered from
   `DROID_RETIRE_ABF_SYNCORE_1.md` only. [C]

8. **Already-ruled campaign-canon identity decisions** (full detail in D,
   §Part 1) a merge step must respect, not re-litigate:
   - "Iconic Star Wars status protects completely" — owner, 2026-09-05
     (`creature_recognizability_rule.md`): a bantha that reads as a bantha is
     the campaign working, not failing; SW icons are exempt from the
     Earth-animal-recognizability cut rule.
   - `art: "improve"` semantics (owner, 2026-09-11,
     `infrastructure/artpipe/README.md`): SW-named creatures keep canon
     identity; non-SW names are free to be reimagined.
   - The frozen "Ancients" sleepers **are the Rakata** (endonym), called "the
     Forgotten"/"the Forsaken" by modern people — not a reskin, a canon-identity
     ruling (`ANCIENTS_AS_RAKATA_SPEC.md`, owner 2026-08-20/2026-08-29).
   - The vanilla RimWorld `Empire` FactionDef **is** the Galactic Empire
     (patched, not replaced) — `Empire` defName and its six `Empire_*`
     PawnKind defNames are load-bearing (`EMPIRE_GAP_AUDIT.md`, owner 2026-08-20).
   - `RSW_Yobshrimp` was explicitly **renamed away** from its SW-echoing name
     to the invented **FeatherFeel** (owner-mandated, ART_REGEN_WAVE5) —
     despite "Yobshrimp" itself appearing in `starwars_iconic_creatures.md`'s
     research catalogue, the campaign chose NOT to use the SW-adjacent name.
   - **"The Kindled have never been made"** — an invented (non-SW) mechanoid
     concept, flagged only so it isn't mistaken for a Star Wars proper noun.

---

## Creature / Species

### Master canon bestiary — `mlie.starwarsanimalcollection` (active, ~160 species)
Source: Workshop mod 3497316713, `.../1.6/Defs/ThingDefs_Races/*.xml`, one
ThingDef per name, defName = species name. **This is the single most
authoritative spelling source found in this raid** — a dedicated, faithfully-named
SW creature pack, nothing invented. [B]

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
Nexu, Nuna, Ollopom, Orray, Painted Spat, Peko-peko, Pikobis, Porg, Pufferpig,
Qormot, Rancor, Raxshir, Reek, Rikknit, Roggwart, Ronto, Runyip, Rycrit,
Scavrat, Scurrier, Shaak, Shiro (+ ShiroTrap), Shyrack, Silooth, Skalder,
Sketto, Snoruuk, Squall, Stintaril, Strill, Tach, Taozin, Tauntaun, Tee-muss,
Tetniss Crab, Thranta, Tibidee, Tooke, Torton, Tukata, Tusk-cat, Urusai, Uvak,
Vapaad, Varactyl, Veermok, Voorpak, Vornskyr, Vulptex, Wampa, War Wyrm,
Warbird, Whisperbird, Womp Rat, Woolamander, Worrt, Wraid, Wyyyschokk,
Yobshrimp, Zakkeg, Zeer.

### Additional canon creatures confirmed via other sources (not necessarily in the list above, or with useful campaign-status context)

| Name | Source | Note |
|---|---|---|
| Ysalamiri / Ysalamir | A (`Armoury/.../kotorcore/VEF/Absorbed_Kotorcore_VEF_Ysalamiri.xml`) | Force-nullification-field creature; description matches canon lore |
| Colo Claw Fish | A (`SWBestiary/.../SeaBeasts_Colo.xml`) | Naboo underworld creature (Episode I); "Abyssal"/"Thornback" morphs are invented additions |
| Opee Sea Killer | A (`SeaBeasts_Opee.xml`) | Naboo (Episode I); "Crimson"/"Shale gorger" morphs invented |
| Sando Aqua Monster | A (`SeaBeasts_Sando.xml`) | Naboo apex predator (Episode I); "Elder"/"Storm" morphs invented |
| Sarlacc | D (`starwars_iconic_creatures.md`, referenced landmark in A's UtinniPatches) | Canon (ROTJ, Book of Boba Fett). Named a "real gap" — no creature def yet, only referenced as a landmark ("the Gaping Doom" = a sarlacc corpse-pit). Extensive dedicated spec docs exist (`sarlacc_spec.md` family). TOP PRIORITY per D. |
| Luggabeast | D | Canon (Force Awakens/Jakku). Named the top-priority "real gap" — "near-perfect Jawa-clan parallel," not yet built. |
| Steelpecker | D | Canon (Battlefront II, Jakku). "Real gap" recreate-worklist. |
| Rakghoul | D | SWTOR/KOTOR canon-adjacent plague creature, sourced to tunnels beneath Tatooine. "Real gap" recreate-worklist. |
| Firaxan shark | D | Canon-adjacent (KOTOR, Manaan). "Real gap" recreate-worklist. |
| Profogg | D | Legends/games. "Real gap" recreate-worklist. |
| Kath hound | D | FIT-POSSIBLE, KOTOR/SWTOR games, Legends-rooted |
| Sandwhirl | D | UNCERTAIN — possibly a hazard not a lifeform, thin sourcing |
| Oggdo Bogdo | D | Jedi: Fallen Order (Bogano) |
| Rabid Jotaz | D | Jedi: Fallen Order (Zeffo) |
| Thala-siren ("sea sow") | D | Canon (Last Jedi, Ahch-To) |
| Purrgil | D | Canon (Rebels/Ahsoka/Mandalorian); deep-space only |
| Howler / summa-verminoth | D | Canon (Solo); "Howler" as distinct species is uncertain, possible conflation |
| Nekko | D | Jedi: Survivor (Koboh) |
| Voritor lizard | D | Legends (Star Wars Galaxies) |
| Fathier | D | Canon (Last Jedi, Canto Bight) |
| Orbak | D | Canon (Rise of Skywalker, Kef Bir) |
| Tooka cat | D | Legends/canon references, galaxy-wide |
| Roba | D | Legends |
| Binog | D | Jedi: Fallen Order, background-only |
| Gizka | D (also in master list above) | Has a dedicated Tatooine-set arc in KOTOR canon |

### Droid chassis / model lines (treated as "species" for droid pawns)

Real canon KOTOR/Clone Wars-era droid designations, verbatim from disk:
AQ Battle Droid, B1 Battle Droid (+ Commander/Security/A variants), B2 Super
Battle Droid (+ HA variant), BX Commando Droid, DSD1 Dwarf Spider Droid, DUM
Repair Droid, Destroyer Droid, Droideka (+ Sharpshooter variant), IG-100
MagnaGuard, KX Security Droid, MSE Repair Droid, Muckraker Crab Droid,
R-Series Droid (R2, R3, R4, R5), ST/T-series/T1 Tactical Droid, T3 unit
(astromech), FX-7 medical droid, GNK power droid, protocol droid (3PO line),
LR-57 Combat Droid, Pistoeka Sabotage/Saboteur Droid (donor mod misspells it
"Sotage"), KM1-series (mining/excavation), GE3-series (labor/protocol),
IT-series, R-8009 series, K-X12 assassin/utility probe droid, Sentinel-class
war droid, Devastator-class assassin/war droid (Type II), Municipal Patrol
Droid Mk I, Assault Droid Mk I/IV/IV-Type-B, Star Forge Assault Droid, HK-47,
HK-50 series, HK-51 series, G0-T0 (GOTO, KOTOR II unique character
genericized into a droid kind), 3C-series utility droid, Imperial Labor
Droid, Astromech Droid (generic), RA-7 ("Death Star droid"), CLLM2, ASP7,
21B (medical droid), LOM. [A, C]

Droid-brain manufacturer names (real canon): Industrial Automaton, Cybot
Galactica, Arakyd. Droid armor-plating materials: Agrinium, Desh, Quadranium. [A]

### NOT Star Wars — campaign-original reimaginings of donor creatures (do NOT list as canon)

| Name used in campaign | Donor defName it reskins | Note |
|---|---|---|
| Grithe | `GR_ParagonRat` (VE Genetics) | chitin-plated insectoid-rodent, "not a literal rat" |
| Grutt | `GR_Molebear` (VE Genetics) | tusked armor-plated burrower |
| Kroffa | `BMT_Maligoat` (BiomesTeam) | six-legged plated desert grazer |
| Puffmite | `BMT_FleeceSpider` (BiomesTeam) | filament-tufted tiny arachnid |
| Spidercat | `GR_Spidercat` (VE Genetics) | art-only reskin, donor's own name untouched |
| (untouched) | `AA_Lockjaw` (Alpha Animals) | whale-alligator hybrid; not SW at all |
| FeatherFeel | `RSW_Yobshrimp` | owner-mandated rename AWAY from an SW-echoing name |
| Duskram | `Jamel` | frilled ceratopsian grazer, "not a literal camel" |
| Slagmaw | `BMT_FoundryBeetle` | rust/slag-plated grinder |
| (kept as-is, not SW) | `AA_Terramorph` | explicitly exempted from renaming — earned identity in a prior sitting |

Phonetic-style (SW-flavored spelling, NOT SW identity) renaming ladder for
Latin-binomial donor creatures, per `creature_names_ashkarr.md` DECIDE
2026-08-22: Protovermes→ssik, Compsognathus→sskek, Coelophysis→sslek,
Brachiosaurus→ssorrbantha, Castoroides→grondik, Smilodon→dhakar, woolly
mammoth→vhorbantha, Sivatherium→obbakar (reserve), Dinornis→kessik (reserve).
English-compound names kept as "spacer slang," never renamed: dunbear,
duskhorn, manehound, hellboar, sporemole. [D]

### NOT Star Wars — non-droid species names used only as item-name adjectives (retired mod `guy762.KotORWeapons`)

Bothan, Baragwin, Echani, Gand, Geonosian, Kaleesh, Krath, Nagai, Rakatan,
Trandoshan, Tusken (Raider), Verpine, Zabrak, Arkanian, Dashade, Ankarres —
**these ARE real SW species names** (see Species/Peoples section below); listed
here only because their only disk presence in this retired mod is as an
equipment-label prefix, not a spawnable pawn. [C]

---

## Character

| Name | Context | Source |
|---|---|---|
| Darth Malak, Darth Revan, Darth Nihilus, Darth Sion, Darth Traya (Kreia), Exar Kun, Darth Malgus, Darth Bane, Darth Maul, Darth Vader | Sith | A, C, B (lightsaber hilts) |
| Visas Marr, Jolee Bindo, Bastila Shan, Juhani, Cal Kestis, Kanan Jarrus, Ezra Bridger, Ahsoka Tano, Gungi | Jedi/companions | A, B |
| Lando Calrissian | — | A, C ("Calrissian's utility belt") |
| Ulic Qel-Droma, Cay Qel-Droma | Old Republic Sith/Jedi | A, C |
| HK-47 | Droid/assassin | A, C ("HK-47's Assassin Rifle") |
| Mandalore (title), Cassus Fett, Bendak Starkiller, Freedon Nadd, Jurgan Kalta, Jamoh Hogra, Mira, Mission Vao, Sanasiki, Zaalbar, Yusanis, Canderous Ordo, Carth Onasi, Bacca, Luxa | Various KOTOR-era named individuals | A, C (named-weapon labels) |
| G0-T0 (GOTO) | Droid, KOTOR II unique | A |
| Emperor Palpatine | Galactic Empire | A, D (git 78a096733) |
| Jerec | Dark Jedi (Jedi Knight game) | B |
| Xim (the Despot) | Ancient pre-Republic conqueror | B |
| Thrawn | Imperial admiral ("Thrawn's 7th Fleet") | B |
| Aayla Secura, Anakin Skywalker, Asajj Ventress, Count Dooku, Even Piell, Galen Marek, Jaden Korr, Jaro Tapal, Karness Muur, Ki-Adi-Mundi, Kirak Infila, Kit Fisto, Kyle Katarn, Kylo Ren, Luke Skywalker, Mace Windu, Mara Jade, Obi-Wan Kenobi, Oppo Rancisis, Plo Koon, Pong Krell, Qui-Gon Jinn, Quinlan Vos, Saesee Tiin, Satele Shan, Shaak Ti, Sharad Hett, Tenel Ka Djo, Ven Zallow, Vernestra Rwoh, Yoda, Desann | Lightsaber-hilt namesakes (games/EU spanning full media breadth) | B (`lee.theforce.lightsaber`) |
| Boba Fett, Salacious Crumb, Teedo, Grievous, Obi-Wan (steed reference) | Reference-only mentions in creature research doc | D |
| Sage of Dwartii (title, canon) — individual names Braata Danlos/Faya Rodemos/Sistros Nevet/Yanjon Zelmar | Decorative Coruscant statuary | B — the TITLE is canon (KOTOR-era), the four individual names are unverified/likely original |

---

## Faction / Organization

### Real Star Wars canon — confirmed on disk

Jedi Order, Sith (+ Apprentice/Assassin/Warrior/Marauder/Trooper/Commando
ranks), Sith Empire, Sith Eternal, Mandalorian(s) (+ Neo-Crusader,
Supercommando), Galactic Republic (+ Republic Commando, Civic Security/TSF,
Republic Navy), Old Republic, New Republic, Czerka Corporation, Hutt
Cartel/Clan, The Exchange, Rakata/Rakatan (Infinite Empire), GenoHaradan,
Galactic Empire (+ Dark Empire, Imperial Remnant, Pentastar Alignment,
Imperial Cloning/Munitions/Press Corps/Information Office/Dept. of Military
Research), Rebel Alliance (+ Rebel Alliance Intelligence, Rebel Squadron),
Confederacy of Independent Systems (CIS/Separatists), Trade Federation, First
Order, Resistance, Chiss Ascendancy, Hapes Consortium, Nihil Raiders,
Partisans, Twilight Company, Zsinj's faction, Maldrood, Khoonda,
Zann Consortium, Black Sun, Crimson Dawn, Kanjiklub, Ohnaka Gang, Pyke
Syndicate, Guavian Death Gang, Fromm Gang, Durand Crime Family, Broken Horn
Syndicate, Haxion Brood, Kajidic (Hutt business structure), Tenloss
(Syndicated Armaments), Systech, Aratech, arms/shipyard corporations
(BlasTech Industries, Baktoid Armor Workshop, Balmorran Arms, Cestus
Cybernetics, Commerce Guild, Corellian Engineering Corporation, Damorian
Manufacturing Corp, Dynamic Automata, Gallofree Yards Inc, Genetech Corp,
Golan Arms, Incom Corp, Koensayr Manufacturing, Kuat Drive Yards, Leisure Mech
Enterprises, Loronar Corporation, MandalMotors, Medtech Industries, Merr-Sonn
Munitions, Mon Calamari Shipyards, Oriolanis Defense Systems, Pantolomin
Shipwrights, Rebaxan Columni, Regallis Engineering, Rendili StarDrive, Sienar
Fleet Systems, Slayn & Korpil, SoroSuub Corp, Sublight Products Corp, Tarkin
Initiative, Techno Union, Telgorn Corp, Tendrando Arms, Theed Palace
Engineering Corps, Udrane Galactic Electronics, Xisor Transport Systems),
Galactic Senate, Gungans, Coruscant Security Force/Health Administration,
Kamino Cloning/Security, Naboo Royals, Lok Revenants, Onderon Rebels, Roche
Hive, Skystrike Academy, Starlight Squadron, Vanguard Squadron, Cobalt
Squadron, Gold Squadron, Blade Squadron, Black Squadron, Alphabet Squadron,
Inferno Squad, Havoc Squad, Yuuzhan Vong, Ashla/Bogan (old-canon Force
light/dark terms), Fulcrum (Ahsoka Tano's codename), Noble Court, Warbird
Gang, Ranc Gang, Ivax Syndicate, Kintan Striders, Kouhun (species used as
faction-adjacent name), Coloacid Creation Nest. [A, B, C]

### Real Star Wars canon — explicit campaign rulings (this repo already decided these)

- Galactic Empire = the vanilla `Empire` FactionDef, patched not replaced
  (`EMPIRE_GAP_AUDIT.md`). Ideo name "The Rising Order."
- Hutt Cartel (`Jawa_HuttCartel`) — AUTHORED faction built around genuine Hutt
  lore, not a reskin. Ideo "the Reckoning of Debts."
- Rebel Alliance — appears via the Outer Rim donor mod, ruled near-lore/OK, not
  separately authored.
- Geonosian Foundry Hive — campaign faction built on the real species/world;
  owner ruling: "the Empire sterilised their species... every one here is a refugee."
- Separatist remnants / "JDS Separatists" — live droid-economy mechanism.
[D]

### NOT Star Wars — campaign-original factions (listed so they are never mistaken for canon)

Ascendant Helix, Deepwater Compact, Free Droid Enclaves, the Junkers, Jawa
Trade Moot, Wildsteam Clan, Homestead Defense League ("the Withdrawn"), Deep
Desert Tribes, the Forgotten Arsenal, Blackstar Company (vanilla Pirate
faction reskin). Deities: Ishko the Unmaskable, Sh'kaar, Ohm (the
All-Current) — the "Nine gods"/"Nine Voices" pantheon. "The Assailant" —
campaign-original antagonist entity. Also: `HoraxCult` is **vanilla RimWorld
Anomaly DLC**, not a donor or Star Wars name — already ruled out of scope. [A, D]

---

## Planet / Location

### Real Star Wars canon

| Name | Source | Note |
|---|---|---|
| Tatooine | A, B, D | Full planet layer built in `guy762.mm.kotorcore`; the constant design-register comparison target for Ash'karr (not itself in the campaign) |
| Naboo (+ Naboo Abyss) | A, B, D | Source of "shuura" fruit; Sando/Colo/Opee/Gorg/Shaak/Nuna/Veermok creature refs |
| Kessel | A, D | Source of "kessel grain"; Vornskyr/Howler creature refs |
| Mimban | A | Source of "mimbanese cacao/sweet" |
| Gamorr | A | Gamorreans' homeworld |
| Nar Shaddaa | A, C | "Nar Shaddaa Grinder" weapon |
| Onderon | A, B, C | "Onderon Repeating Carbine"; "Onderon Rebels" faction decal |
| Taris | A, C | "Taris survival gloves" |
| Cinnagar / Cinnagaran | A, C | KOTOR-era world (Old Republic corpus, not mainline films) |
| Eriadu | B, C | Item/decal naming only |
| Bonadan | C | "Bonadan Alloy Heavy Suit" |
| Barab | A, C | Source of "Barab Ore Ingot" |
| Balmorra | C | "Balmorran overshield" |
| Coruscant | B | Furniture line; Sage of Dwartii statuary (Old Republic-era) |
| Corellia | B | Furniture line |
| Dathomir | B, D | Lamp line; Rancor/Voritor lizard creature refs |
| Ilum, Jedha, Christophsis, Dantari (likely Dantooine), Kimber Station | B | Named as kyber/crystal-source worlds via lightsaber hilt-parts |
| Kamino | B, D | Decal naming; Aiwha creature ref |
| Endor | B | `OuterRim_RebelEndorTrooper` pawnkind |
| Jakku | D | Steelpecker/Luggabeast refs |
| Geonosis | D | Orray ref |
| Manaan | D | Firaxan shark ref (KOTOR) |
| Ahch-To | D | Thala-siren/Porg refs |
| Crait | D | Vulptex ref |
| Hoth | D | Tauntaun/Wampa refs |
| Dxun | D | Boma beast/Zakkeg refs |
| Utapau | D | Energy spider/Varactyl refs |
| Lothal | D | Loth-cat/Loth-wolf refs |
| Kashyyyk | D | Kybuck/Kinrath refs |
| Cholganna | D | Nexu ref |
| Korriban | D | Sith homeworld (implied by species entry) |

### NOT Star Wars

Ash'karr (this campaign's fixed world). Sophiamunda (campaign's own Empire
homeworld — "techno-feudal culture," not a real SW planet). Numerous
campaign-original sub-locations (Rust Cathedral, the Scorch, the Fall Line,
Deadstone, the Slough, the Umbra vault, the Rot, the Propane Lakes, the Blue
Desert, the Forsaken Crags, the Cracked Lands, the Poison Forest, the Weeping
Stones, the Pyrelands, the Greentide, the Contagion, the Webwork, the Slime,
the Miasma, the Sump, the Fever Wood, the Forge, the Gaping Doom, Lightfall,
the gelatinous breach). [A]

---

## Ship

| Name | Source | Note |
|---|---|---|
| YT-1300 transport | A | Real canon (Millennium Falcon's model); used only for a pilot-console building defName |
| Dynamic-class Freighter | A, B | Real KOTOR-era canon ship class — the *Ebon Hawk* is a modified Dynamic-class light freighter |
| KT-400 Freighter | A, B | NOT verified as canon — likely donor-invented designation |
| Landspeeder | A | Real SW vehicle class name; applied via label/description reskin of a Vanilla Expanded pod-car |
| Star Forge | C, D (filed as "other" — it's a mega-structure/factory, not a ship) | Ancient Rakatan droid-factory station (KOTOR) |
| the *Utinni* | D | Campaign's own gravship — explicitly flagged as ORIGINAL, not a Star Wars proper noun |

**No specific named individual canon starship** (e.g. a Star Destroyer class
name, the Millennium Falcon by name) was found authored anywhere in this
campaign's own content — only referenced via the "Dynamic-class Freighter"
canon ship-class label and the `det.venators` naming-echo trap (that mod is
NOT actually about the Venator-class Star Destroyer). [B, D]

---

## Item / Artifact

### Real Star Wars canon

**Named unique artifacts**: Star Forge (Robes/Mask/Cloak/Shield), Kaiburr
Crystal, Krayt Dragon Pearl, Heart of the Guardian, Mantle of the Force,
Pride of Mandalore, Ultima Pearl, Lorrdian Gemstone, "Whistling Birds"
launcher (Mandalorian wrist-launcher), Arg'garok (Gamorrean axe — bug noted:
no weapon def on disk actually carries the matching tag), M'uhk'gfa
(Gamorrean battle harness/armor). [A, C]

**Lightsaber/power/focusing crystals** (real named SW types): Kyber, Adegan,
Rubat, Ruusan, Velmorite, Sigil, Nextor, Kasha, Eralam, Damind, Sapith, Opila,
Upari, Jenurax, Luxum, Bondar, Dragite, Firkann, Pontite, Stygium, Barab Ore
Ingot, Hurrikaine, Artusian, Qixoni, Solari, Bled Crystal, Cleansed Crystal,
Synthetic Crystal, Dantari, Ghostfire, Ilum, Jedha, Kimber Stone, Mephite,
Nishalorite Stone, Sorian, Thontiin, Varpeline, Zophis, Christophsis,
Ankarres Sapphire, Viridian. Named lightsaber types: Darksaber, Broadsaber,
Protosaber, Soul Saber. All seven canon lightsaber combat forms: Form I
Shii-Cho, Form II Makashi, Form III Soresu, Form IV Ataru, Form V
Shien/Djem So, Form VI Niman, Form VII Juyo/Vaapad. [A, B, C]

**Weapons** (real canon blaster/weapon model designations): Bowcaster,
E-Web, Thermal Detonator, DC-15A/S/x, DC-17/17M/17S, E-5/5C/5S, E-60R, EE-3,
SE-14/14R, Westar-33/34/35/44/M5, Amban sniper rifle, Z6 Rotary Blaster
Cannon, E-11/11D, DLT-19/19X/20A, D-72 Oppressor, TL-50 Heavy Repeater,
A180/A280, DH-17, HH-12, K-16 Bryar Blaster, T-21 Repeating Blaster,
Gaderffii Stick (Tusken "gaffi stick"), Vibroblade/Vibroaxe/Vibrocleaver/
Vibrodagger/Vibro-double-blade/Vibroglaive family. [A, B, C]

**Materials/currency**: Beskar (Mandalorian iron), Cortosis, Durasteel,
Bronzium, Rhydonium, Tibanna, Kolto, Plastoid, Duracrete, Spice, Armorweave,
Synthread, Credits (canon currency name), Aurebesh (SW writing script). [B]

**Food renames** (owner ruling: inspected/traded food gets canon SW plant
names): kessel grain, kibla grain, koyo tuber(s), pallie berry, muja bramble,
ardees, shuura bush, mimbanese sweet, mimbanese cacao, bantha fodder. [A]

**Technology/concepts**: Lightsaber (explicit ruling: do not casually conflate
with the campaign's own "laser sword" item pending a Force-users spec),
Restraining bolt (two dedicated design docs), Astromech droid, Protocol
droid, Podracer/podrace. [D]

### Named weapon model codes, retired mod (`M3...StarWars.BTI`)

DC-15A, DC-15S, DC-15x, DC-17, DC-17M, DC-17S, E-5, E-5C, E-5S, E-60R, EE-3,
SE-14, Westar-33/34/35/44/M5, Z6, Amban. [C — duplicates some of the B list
above; kept separate since it's independently confirmed from a different mod]

### NOT Star Wars

Jawa Ion Blaster, ion bolt (Utinni-original despite the "Jawa" name). Shokk
mouth-loom, web-silk glob (Utinni-original mechanic on the real, third-party
Wyyyschokk species). `RSW_RN2SWGun_EWebMounted_GPMG` is labeled "M60" — a
real-world weapon name, not SW, not fictional. [A]

---

## Other / notable

- **Ben Burtt Jawa-language phrases** (real, used verbatim in About.xml text,
  not XML defs): *Utinni!*, *M'um m'aloo*, *Ibana*, *Nyeta*, *Taa baa*. [A]
- **StarWarsRaces mod** enumerates ~65-69 real SW playable species (About.xml
  claims 69; ~47 directly confirmed via defs): Abednedo, Anzati, Aqualish,
  Arkanian, Bith, Bothan, Cathar, Cerean, Chadra-Fan, Chagrian, Chiss,
  Dathomirian, Defel, Devaronian, Duros, Echani, Ewok, Falleen, Feeorin,
  Gamorrean, Gand, Geonosian, Gungan, Herglic, Hutt, Iktotchi, Iridonian,
  Ithorian, Kaleesh, Kaminoan, Kel Dor, Klatoonian, Kubaz, Lasat, Mimbanese,
  Mirialan, Mon Calamari, Muun, Nagai, Nautolan, Neimoidian, Nelvaanian,
  Nikto, Ortolan, Pantoran, Pyke, Quarren, Rakata, Rodian, Selkath, Sith
  (Kissai/Massassi/Zugurak Pureblood), Snivvian, Sullustan, Taung, Togorian,
  Togruta, Trandoshan, Tusken, Twi'lek, Ugnaught, Umbaran, Weequay, Wookiee,
  "Yoder" (an unnamed canon species nicknamed "force gremlin" by the mod),
  Zeltron, Zygerrian. [A]
- **Species/peoples this campaign has already built factions/rosters around**
  (all real SW canon): Hutt, Nikto, Gamorrean, Rodian, Trandoshan, Aqualish,
  Twi'lek, Pyke, Devaronian, Sith Pureblood, Rakata, Wookiee, Ewok, Tusken
  Raiders/Sand People, Jawa (the campaign's own premise). Weequay is
  explicitly noted as MISSING despite being canonically common Hutt-cartel
  muscle. Nautolan was explicitly ruled OUT of an unrelated slime mod
  ("nothing to do with Star Wars" — i.e. don't misread its mere mention as
  campaign adoption). [D]
- Gand, Geonosian, Kaleesh, Verpine, Arkanian, Gree, Bothan, Trandoshan,
  Zabrak, Nagai, Dashade appear throughout `Armoury`'s weapon files as
  species-flavored item-name adjectives (e.g. "Gand Shockstaff," "Kaleesh
  Battle Rifle") rather than as spawnable pawns. [A]

---

## Mod/source coverage — what was and wasn't checked

**Checked with content found**: Armoury, Droidworks, SWBestiary,
StarWarsRaces, StarWarsPatches, UtinniPatches, StructureInjectionsRUT, most
`*ArtOverride` mods, `mlie.starwarsanimalcollection`, `lee.theforce.lightsaber`,
`guy762.mm.kotorcore`, `btd.gbp.shippack.kotor.vge`, all four active
`neronix17.outerrim.*` mods, 10 of 12 retired SW-themed mods,
`design/Jawa/worldbuilding/` (partial — see below), `donor_proper_noun_backlog.md`,
all 7 `ART_REGEN_WAVE*` items, git log (keyword-filtered).

**Checked, zero SW content**: DroidRepairJobs, ShipShields, RestrainingBolts
(near-zero), StrandedQuest, Oracle, RaidRedesigner, RustChrome,
ProximityHatch, PlanetPresetPrime, StructureInjections, MandrakePatches,
TitanicCreatures, RotSporeKit, AshkarrLandmarkArt, JawaRules; all 21
non-SW-themed active Workshop mods listed in the flagged findings above; 4
retired mods ruled non-SW (`matathias.ruthlessmechanoids`, `titans.fl`,
`mf.jfklanding`, `joe.cephaloids`).

**Not reached — flagged gaps for a follow-up pass**:
`design/Jawa/worldbuilding/faction_roster_v2.md` (189KB), `jawa_society.md`
(62KB), `desert_world_design.md` (155KB), `ASHKARR_WORLD_DEFINITION.md`
(111KB), `Alien_Bestiary.md` (30KB), the remainder of `ANCIENTS_AS_RAKATA_SPEC.md`
and `EMPIRE_GAP_AUDIT.md` beyond their first ~150 lines, and most of the
~150-file `design/Jawa/worldbuilding/` tree beyond what's listed in source D.
Also `guy762.KotORFactions` (workshop 3379096669) has content on disk and is
clearly SW-related but couldn't be classified retired-vs-never-active within
the 5-snapshot sample checked — worth a look in the merge pass.
Beskar and "protocol droid" were expected as canon terms but not independently
confirmed quoted in the docs read this pass (flagged, not concluded absent).
