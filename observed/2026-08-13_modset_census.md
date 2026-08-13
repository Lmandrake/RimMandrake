# Mod set census — listed vs present — 2026-08-13

Seat: OPS. Game DOWN (exited ~10:04). Census run 16:2x PDT, all offline file reads — no game load.

Sources:

- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml` (mtime Aug 13 10:01)
- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\`  ← **added mid-run**; Core and the five expansions live here, not under `Mods\`. Omitting it manufactures six false 'missing' hits.

Script, kept for reproducibility: `D:\Luke\dev\Rimworld\observed\2026-08-13_modset_census.py` — walks each root, reads `About/About.xml`, takes the **root-level** `<packageId>` child of `<ModMetaData>`, lowercases both sides, set-compares against `<activeMods>`.
Raw map committed alongside: `D:\Luke\dev\Rimworld\observed\2026-08-13_modset_map.json`

## Method traps hit, and how they were caught

Both of these produced wrong answers on the first pass. Recording them because the wrong answer looked plausible.

1. **`<packageId>` is not unique inside `About.xml`.** A naive `re.search(r'<packageId>(.*?)</packageId>')` returns the *first* match, which in most modern mods is a **dependency's** id inside `<modDependencies>`, not the mod's own. Caught by `sarg.alphabiomes` reporting as absent while `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1841354677\About\About.xml` plainly contains it — line order there is `brrainz.harmony`, `OskarPotocki.VanillaFactionsExpanded.Core`, *then* `sarg.alphabiomes`. The first pass reported dozens of missing mods (the exact count was lost to output truncation, but the corrected run drops it from that to **1**); every one but a single entry was this bug. Fix: `ET.parse(ax).getroot().find('packageId')` — direct child only.
2. **Core and the DLCs are not under `Mods\`.** They are `...\RimWorld\Data\{Core,Royalty,Ideology,Biotech,Anomaly,Odyssey}`. Caught by `ludeon.rimworld` at index 3 reporting absent.

## Counts, each with its derivation

| quantity | value | how it was produced |
|---|---:|---|
| raw `<li>` in `ModsConfig.xml` | 575 | `len(list(ET.parse(CFG).getroot().iter('li')))` |
| `<activeMods>` entries | **570** | `len(root.find('activeMods').findall('li'))` |
| `<knownExpansions>` entries | 5 | `len(root.find('knownExpansions').findall('li'))` — 570 + 5 = 575 ✓ |
| folders under `workshop/content/294100` | 1238 | `sum(1 for d in os.listdir(r) if os.path.isdir(...))` |
| folders under `common/RimWorld/Mods` | 8 | `sum(1 for d in os.listdir(r) if os.path.isdir(...))` |
| folders under `common/RimWorld/Data` | 6 | `sum(1 for d in os.listdir(r) if os.path.isdir(...))` |
| distinct packageIds on disk | 1252 | `len(present)` after the walk |
| folders with no readable `<packageId>` | 0 | `len(noid)` |
| **LISTED BUT NOT PRESENT** | **1** | `[p for p in active if p.lower() not in present]` |
| **PRESENT BUT NOT LISTED** | **683** | `[k for k in present if k not in {p.lower() for p in active}]` |
| **duplicate packageId across folders** | **0** | `{k for k,v in present.items() if len(v)>1}` |

**Arithmetic check:** 1252 folders scanned = 1252 distinct packageIds (bijection: zero duplicates, zero unreadable). 570 listed − 1 missing = 569 listed-and-present; 569 + 683 inactive = 1252. ✓

**570 held up.** The file's own `<activeMods>` block counts 570, and 575 − 5 `<knownExpansions>` = 570. The docs saying 569 and 573 are stale; do not use them.

## (a) LISTED BUT NOT PRESENT — 1

| load index | packageId | what it is |
|---:|---|---|
| 560 | `lee.theforce.lightsaber` | **Star Wars: The Force — lightsaber module.** Third module of a family by author *Lee*. |

Identification and evidence:

- Two sibling modules ARE on disk, and both name it explicitly:
  - `...\294100\3557220601\About\About.xml` → `<name>Star Wars : The Force Standalone</name>`, `<packageId>lee.theforce.standalone</packageId>`, and **`<loadBefore><li>lee.theforce.lightsaber</li>`**
  - `...\294100\3557220783\About\About.xml` → `<name>Star Wars : The Force Factions</name>`, `<packageId>lee.theforce.factions</packageId>`, and **`<loadAfter>` includes `lee.theforce.lightsaber`**
- `grep -ril "lee.theforce" <workshop root> --include=About.xml` returns **only** those two folders. The lightsaber module is nowhere on this disk.
- Steam has no record of it either: `grep -n "3557220" appworkshop_294100.acf` returns exactly four hits — `3557220601` and `3557220783`, each twice (`WorkshopItemsInstalled` and `WorkshopItemDetails`). There is no third id in the family. `NeedsDownload` = `0` and `NeedsUpdate` = `0`, so **Steam does not think a download is pending** — this is not an interrupted install, it is an item that is not subscribed.
- The listing is not new: `git grep lee.theforce.lightsaber` finds it in every archived `deployed\config\ModsConfig.*.xml` back to `ModsConfig.ORIGINAL-2026-08-10-prerename.xml` line 561. It has been listed-and-absent for at least three days.

**Why RimWorld said nothing:** neither sibling declares it in `<modDependencies>` — only `<loadBefore>` / `<loadAfter>`, which are *ordering hints*. An ordering hint pointing at an id that never loads is silently ignored; only a real `<modDependencies>` entry raises the yellow 'missing dependency' dialog. So the entry is dropped from the load list without a word.

**Twist worth flagging: the two siblings that ARE installed are NOT in `<activeMods>`.** `lee.theforce.standalone`, `lee.theforce.factions` and `lee.theforce.psycast` are all in the inactive list below. Their folders `3557220601` and `3557220783` have mtime **Aug 13 15:43** — five and a half hours *after* the `ModsConfig.xml` write at 10:01, and after the game exited at ~10:04. So the family arrived on disk after the config was last written, and the config still points at the one module that did not arrive. **Directly relevant to the Jedi/Sith force-user build spec (commit `b5796eb`)** — that spec should be checked against what is actually loadable, which today is *neither* module: the lightsaber one is absent, the other two are inactive.

**Recommended action:** decide which of the three you want, then either subscribe to the lightsaber module and activate the siblings, or remove `lee.theforce.lightsaber` from `<activeMods>`. Leaving it costs nothing at runtime (RimWorld drops it silently) but every future census and every load-order tool will keep reporting it, and the build spec is currently written against defs that do not load.

## (b) PRESENT BUT NOT LISTED — 683

Installed and inactive. Derivation: `sorted(k for k in present if k not in {p.lower() for p in active})`. Not a problem in itself — 1252 subscribed mods, 569 activated. Listed in full for completeness; the machine-readable form with folder paths is in the JSON map.

<details><summary>683 inactive packageIds</summary>

| packageId | name | folder |
|---|---|---|
| `4loris4.morelinkables` | More Linkables | `1103809207` |
| `ab.hoffa` | Head Set For [NL]Facial Animation | `2975760383` |
| `adamas.hospital` | Hospital | `2992224079` |
| `adamas.hospitalitycasino` | Hospitality: Casino | `2939292644` |
| `adamas.hospitalityspa` | Hospitality: Spa | `2971831654` |
| `adamas.storefront` | Hospitality: Storefront | `2952321484` |
| `adamas.vendingmachines` | Hospitality: Vending machines | `3014885065` |
| `akaster.ivdruginfuser` | IV Drug Infuser | `3484624947` |
| `al9000.tvc` | Tastier Vanilla Clothes | `2808554143` |
| `alias.doormats` | Doormats | `3239838811` |
| `als.anomalygravship` | Anomaly for Gravship | `3558784993` |
| `als.gravtech` | GravTech | `3545374124` |
| `altushka.boscompendium` | The Brotherhood Compendium 1.6 | `3571412768` |
| `amro.uniqueapparel` | Unique Apparel & Armor | `3545666494` |
| `andromeda.helpmebuild` | Help me build | `3534699220` |
| `andromeda.nicehealthtab` | Nice Health Tab | `3328729902` |
| `andromeda.stackgap` | Stack gap | `3071298014` |
| `annoprofi.outfitbuilderredux2` | Outfit Builder Redux^2 | `3589354596` |
| `anomaly.power.improved` | Anomaly Power Improved | `3263594825` |
| `anthitei.athsstyleableframework.style` | ATH's Styleable Framework | `3016405872` |
| `anthitei.athsstylegothic.style` | ATH's style Gothic and Bloody Gothic | `3136210612` |
| `anthitei.athsstylenorse.style` | ATH's styles Norse | `3292048218` |
| `aoba.fortress.industrial.nucleardawn` | Fortification Industrial -Nuclear Dawn | `2733185331` |
| `aoba.fortress.medieval` | Fortifications - Medieval | `2501486827` |
| `aoba.tent` | Camping Tent | `2407128339` |
| `aoba.tentshelters` | Post-apocalyptic Shelters | `2444147091` |
| `arandomkiwi.rimsaves` | RimSaves | `1713367505` |
| `arandomkiwi.rimthemes` | RimThemes | `1668983184` |
| `aranmaho.rangerclass` | VPE - Ranger | `2927626324` |
| `aranmaho.ravenouseye.wildhunter.psycast` | Wildheart Psycast | `3043229067` |
| `arquebus.medievalpersonaweapons` | Medieval Persona Weapons | `2869057049` |
| `arquebus.morepersonatraits` | More Persona Traits | `2863308112` |
| `arvkus.simplerecycling` | Simple Apparel Recycling | `3239309389` |
| `asf.deepstorage` | LWM's Adaptive Deep Storage | `3373064575` |
| `asmallrabbit.uniformgrowzone` | Uniform Growing Zone Tool | `1898969926` |
| `assassinsbro.medievalbackstoriesnohar` | Medieval Backstories No HAR | `3128454510` |
| `assssssqwww.feelingfilter` | RimTalk-Message Filter | `3697500330` |
| `automatic.autocleaner` | Autocleaner | `2051042827` |
| `automatic.bionicicons` | Bionic icons | `1677616980` |
| `automatic.gradienthair` | Gradient Hair | `1687053679` |
| `automatic.gunplay` | Gunplay | `2034896549` |
| `avilmask.grazinglands` | Grazing Lands | `1770268130` |
| `ayas.passiononlevelupplus` | Passion On Level Up Plus | `3526025445` |
| `azrazalea.dbh.springwater.patch` | Dubs Bad Hygiene - Spring Water Patch | `3531641684` |
| `balistafreak.stopdropandroll` | Stop, Drop, And Roll! [BAL] | `2362707956` |
| `bart.bioformmatrix` | Bioform Matrix | `3535848372` |
| `bdew.fullgunsellprice` | Full Gun Sell Price | `1575464750` |
| `bean.customxenotypes.goblinsoftherim` | Goblins of the Rim | `3237397753` |
| `bionicicons.hd` | [CF] Bionic Icons HD | `3239007545` |
| `biotexpans.core` | Biotech Expansion - Core | `2884018485` |
| `biotexpans.mythic` | Biotech Expansion - Mythic | `2883216840` |
| `bjr1984.dubsskylights.addon` | Dubs Skylights Addon | `2016959026` |
| `blackmarket420.pandoraframework` | Pandora's Framework | `3226701491` |
| `bodilpwnz.animalbiosculpter` | Animal Biosculpter | `2883571601` |
| `bonible.modded.gun.sound.pack` | Modded Weapon Sound Replacement | `2999509683` |
| `botchjob.divineorder` | Divine Order | `3017163907` |
| `botchjob.hthair` | Hard Times: Hair and Beards | `3092175321` |
| `botchjob.medievalfantasyquestrewards` | Medieval Fantasy Themed Quest Rewards | `2955864975` |
| `botchjob.medievalfantasyrareresources` | Medieval Fantasy Themed Rare Resources | `2942661554` |
| `botchjob.medievalfantasythemedrelicquests` | Medieval Fantasy Themed Relic Quests | `3035624471` |
| `botchjob.possessedweapons` | Possessed Weapons | `2982391372` |
| `botchjob.profaned` | The Profaned | `3202008037` |
| `broms.asteroidmineralscanner` | Asteroid Mineral Scanner | `3536585361` |
| `buggy.rimworld.letterpermanentinjury` | Letter Permanent Injury | `2592535960` |
| `bulldog.vanillachemfuelexpandedodysseypatch` | Vanilla Chemfuel Expanded - Odyssey Patch | `3530583255` |
| `caesarv6.damageindicators` | Damage Indicators [1.6] | `2016331497` |
| `canon.nomechsummonergizmo` | No Summon Mech Threat Gizmo | `2889317343` |
| `cedaro.csa` | Change Style Anytime | `3072859227` |
| `cedaro.worldpawncleaner` | World Pawn Cleaner | `3181327333` |
| `cf.anomalyupscaled` | [CF] Anomaly Upscaled | `3239664028` |
| `cgf1.hlrw.thecombines` | HLRW - The Combine | `3536753286` |
| `chaoticenrico.castlewallsexpanded` | Castle Walls Expanded | `3024167916` |
| `chaoticenrico.followtarget` | Follow Target | `3555423377` |
| `chaoticenrico.smoothterrain` | Smooth Terrain | `3502765685` |
| `charlie.muzzle.flash.for.ancientruins` | Wood's Muzzle Flash for Ancient urban ruins | `3442021825` |
| `cj.rimtalk` | RimTalk | `3551203752` |
| `cj.rimtalk.expandmemory` | RimTalk - Expand Memory | `3608181242` |
| `cj.rimtalk.literature` | RimTalk - Expand Literature | `3633249209` |
| `cj.rimtalk.toddlers` | RimTalk - Expand Toddlers | `3659064387` |
| `cn.youaresobeautiful` | You Are So Beautiful | `3576178532` |
| `co.uk.epicguru.disco` | Disco! | `2436747646` |
| `coldcrow.betterorbitaltraders` | Better Orbital Traders | `3009866854` |
| `coldcrow.bettertradableitems` | Better Tradable Items | `3009963773` |
| `colossalfossil.animalsarefuncontinued` | Animals are fun! (Continued) | `3245454244` |
| `com.bymarcin.architecticons` | Architect Icons | `1195427067` |
| `com.er.mod.winstonwavepawncap` | Winston Wave Pawn Cap | `3757637713` |
| `conit.kpdl` | Kidnapped Pawns Die Less | `3308076464` |
| `costel.customroomnames.rimtalkaddon` | Custom Room Names - RimTalk Addon | `3626983869` |
| `cp.uncle.boris.brainwash.chair` | [RH2] Uncle Boris' - Brainwash Chair | `2885223720` |
| `crows.dustbunny` | Dust Bunnies | `3480725900` |
| `ctrlaltfunk.vpeselfcastpluspatch` | VPE Self-Cast This! Plus Temp 1.6 | `3519928832` |
| `cucumpear.azrael.varietycoats` | Animal Variety Coats | `1511926373` |
| `cyanobot.buildfromchunk` | Build From Chunk | `3218639401` |
| `cyber.miniaturization` | Miniaturization (Minify) | `2885885154` |
| `cyberchronicle.rimtalkexperts` | RImtalk Expand : News, Expert and Colony Chronicle | `3714540653` |
| `cyberchronicle.rimtalkstoryteller` | RimTalk Expand: AI Storyteller | `3715752189` |
| `dame.ignorance` | Ignorance Is Bliss | `2554423472` |
| `daniledman.fastregen` | Fast regen 1.6 | `943925765` |
| `daniledman.hardworkinganimals` | Hardworking animals 1.6 | `933324235` |
| `danzen.vpe.biotechintegration` | Vanilla Psycast Expanded - Biotech Integration | `3110971925` |
| `daria40k.biglittlemodpatch` | Big Little Mod Patch | `2710382569` |
| `darknote.bunkbeds` | Bunk Beds | `2961752749` |
| `daysleep.humanpregnancyduration` | Human Pregnancy Duration Settings | `2880967245` |
| `dbh.upscaled` | [CF] Dubs Bad Hygiene Upscaled | `3163175368` |
| `deadmano.rimanoarchitecticons` | Rimano: Architect Icons | `3212495112` |
| `defi.autocutblight` | Auto-Cut Blight - 1.6 | `3520167264` |
| `defi.blueprints.fork` | Blueprints Forked - 1.6 | `3525001145` |
| `defi.generipper` | Gene Ripper | `3524806362` |
| `delmaintweaks.ritualsizeattenuation` | Ritual Size Attenuation | `3262033797` |
| `delmaintweaks.roleapparel` | Delmain Tweaks - Role Apparel | `2980235255` |
| `densevoid.peerpressure` | Peer Pressure (Continued) | `3605155621` |
| `deon.rimtek.stealthbelt` | RimTek StealthBelt | `3501257149` |
| `deon.rimtek.style` | RimTek Style | `3502852790` |
| `desmond.chargestunners.7742` | Charge Stunners | `2994740520` |
| `det.dwarvenstyle` | Stoneborn - Dwarven Style Pack | `3172496453` |
| `det.epochspottery` | Epochs - Pottery | `3092351095` |
| `det.epochstallow` | Epochs - Tallow | `3502180016` |
| `det.halffoot` | Det's Xenotypes - Half-foot | `3530817307` |
| `det.spacerarsenal` | Spacer Arsenal | `3247891820` |
| `det.stoneborn` | Det's Xenotypes - Stoneborn | `2888722722` |
| `det.vanillaarsenal` | Vanilla Arsenal | `3273371966` |
| `dev.tobot.vpe.betterautocast` | Better autocasting for Vanilla Psycasts Expanded | `3199585285` |
| `dhl.seedfish` | Seed Fish Tool | `3549336894` |
| `dhultgren.smarterconstruction` | Smarter Construction | `2202185773` |
| `dimonsever000.animaobelisk.specific` | Cybranian - Anima Obelisk | `2614248835` |
| `dimonsever000.events.specific` | Cybranian - Events | `2599784515` |
| `dimonsever000.weaponproficiency` | Cybranian - Weapon Proficiency | `3523531768` |
| `dingzhen.levelthis` | Level This! (Continued) | `3443626025` |
| `dismarzero.vgp.vgpvegetablegarden` | VGP Vegetable Garden | `2007061826` |
| `dismarzero.vgp.xtratreesandflowers` | VGP Xtra Trees and Flowers | `2007064094` |
| `doll.nevergeneraterelations` | Never Generate Relations | `2891797130` |
| `doug.nojobauthors` | No Job Authors | `2009825774` |
| `dprtf.darkpsychicrituals.sentinel` | Dark Psychic Rituals: The Following | `3596468709` |
| `drati.rimtalkmoodreactions` | RimTalk Mood Reactions | `3755539006` |
| `drilledhead.hybridpoweredgravships` | [DHM]Hybrid-Powered Gravships | `3524491355` |
| `drwalz.contentmodnumberthreeskillbionics` | Skill Bionics | `3228526665` |
| `dubwise.dubsappareltweaks` | Dubs Apparel Tweaks | `2296697286` |
| `dubwise.dubsbadhygiene` | Dubs Bad Hygiene | `836308268` |
| `dubwise.dubsskylights` | Dubs Skylights | `833899765` |
| `dubwise.rimatomics` | Dubs Rimatomics | `1127530465` |
| `el.biotechmechrt` | Biotech Mechanoid Retexture | `3164022710` |
| `elindis.betterhotsprings` | Better Hot Springs | `3532108439` |
| `erin.bg3.hair` | Erin's Baldur's Gate 3 Hairs | `3069933015` |
| `erin.body.texture` | Erin's Body Retexture | `2662457442` |
| `erin.decorations` | Erin's Decorations | `2463358089` |
| `erin.hair2` | Erin's Hairstyles 2 | `2849477421` |
| `erin.hairredux` | Erin's Hairstyles - Redux | `2361911135` |
| `erin.kpdh.hair` | Erin's KPop Demon Hunters Hairs | `3595945875` |
| `escp.morrowrim.birthsignspassive` | MorrowRim - Passive Birthsigns | `3244646911` |
| `escp.morrowrim.dunmerstyles` | MorrowRim - Dunmer Styles | `3244646489` |
| `escp.racetools` | ESCP - Race Tools | `3244642507` |
| `espio.pastelove` | Nutrient Paste Love | `3386437690` |
| `esvn.rpgdialog` | RPG Dialog | `3547971440` |
| `evyatar108.seedspleaseliteredux` | SeedsPlease: Lite Redux | `3523459853` |
| `extts.fl` | Extra Mini-Turrets | `3199145674` |
| `fallen.anomaliesexpectedaddon` | Anomalies Expected Addon | `3251944598` |
| `farxmai2.genebanksexapnded` | [FM] Gene Banks Expanded | `3138968978` |
| `fastergene.recovery` | Faster Gene Recovery | `2882689772` |
| `fed1splay.pawntargetfix` | Pawn Target Fix | `2014789938` |
| `ferny.progressionstorage` | Progression: Storage | `3292746186` |
| `ferny.propscore` | More Prop Categories | `3167021055` |
| `ferny.replacelib` | ReplaceLib | `3417393194` |
| `ferny.vanillaexpandedherobackgrounds` | Vanilla Expanded: Hero Backgrounds | `3313700572` |
| `ferny.worldbuilder` | Worldbuilder | `3522102833` |
| `fip.robco` | FIP - RobCo | `3563825876` |
| `firecat.winstonwaves.bugfix` | Winston Waves Bugfix | `3749719642` |
| `flashpoint55.rpgstylelevelupmod` | RPG Style Level Up Mod | `1995668415` |
| `fleshforge.defilergenerator` | Defiler Generator | `3530838203` |
| `fox.simplelearning` | Simple Learning (Continued) | `3580464748` |
| `frozensnowfox.betterancientcomplexloot` | [FSF] Better Ancient Complex Loot | `2559244124` |
| `frozensnowfox.betteranomalyloot` | [FSF] Better Anomaly Loot | `3229997523` |
| `frozensnowfox.betterexplorationloot` | [FSF] Better Exploration Loot | `3526957922` |
| `frozensnowfox.filthvanisheswithrainandtime` | [FSF] Filth Vanishes With Rain And Time | `1508341791` |
| `frozensnowfox.frozensnowfoxtweaks` | [FSF] FrozenSnowFox Tweaks | `2893432492` |
| `frozensnowfox.indoortreefarms` | [FSF] Indoor Tree Farms | `1515299608` |
| `frozensnowfox.nodefaultshelfstorage` | [FSF] No Default Shelf Storage | `945085502` |
| `futurplanet.disassemblemechanoid` | Disassemble Mechanoid | `3191640281` |
| `ganja.ed.embrasures` | ED-Embrasures (Continued) | `3277482616` |
| `gaon.lowtoolcabinet` | Medieval Tool Cabinet (Continued) | `3326055369` |
| `gerrymon.mco` | Medieval Coastal Outfits | `3483685923` |
| `gerrymon.medievaldbh` | Gerrymon's Medieval DBH Retexture | `3510803927` |
| `gerrymon.uvt` | Gerrymon's Upscaled Vanilla Textures | `3276562906` |
| `ghastly.echoesoftherim` | Echoes of the Rim | `3573196843` |
| `ghastly.visualcybernetics` | Visible Cybernetics | `3262173908` |
| `ghost.tribalicons` | Tribal Ideology Icons | `3083595998` |
| `gideon.castlewalls` | Castle Walls Reborn | `3256542892` |
| `gm.cannibal.style` | Gerrymon's Cannibal Style | `3432956417` |
| `gm.erotic.style` | Gerrymon's Erotic Style | `3273776545` |
| `gm.nautian.style` | Gerrymon's Nautian Style | `3147664706` |
| `goat.anomaly.events` | Anomaly Events Extended | `3307094049` |
| `goat.archean.sunlamps` | Archean Tree Sunlamps | `3536650291` |
| `goat.food.texture.variety.core` | Food Texture Variety Core | `3354455179` |
| `goat.food.texture.variety.vecoffetea` | Food Texture Variety - Vanilla Expanded Coffee and Tea | `3409546023` |
| `goat.food.texture.variety.vecooking` | Food Texture Variety - Vanilla Expanded Cooking | `3388883044` |
| `gogatio.newanomalythreats` | New Anomaly Threats | `3274840013` |
| `goji.thesimstraits` | The Sims Traits | `3604588393` |
| `gold.ultimatestoryteller` | Ultimate Storyteller [1.4-1.6] | `2887952810` |
| `gold.usbasilicuspatch` | Ultimate Storyteller - Basilicus Patch [1.4-1.6] | `2928443788` |
| `gonezzle.pig` | Pigs are smart | `2837154037` |
| `gorlath.ideonature` | Gorlath's Flowery Ideology Addon | `3362432392` |
| `grasstypefire.medieval.backstoriespatch` | Medieval Backstories Patch | `3170653412` |
| `grasstypefire.tribalbackstories.medievalpatch` | Tribal Backstories - Medieval Patch | `3170651153` |
| `grillmaster.integratedcreepjoiners` | Integrated Creep Joiners | `3233429182` |
| `gt.sam.basicdoubledoors` | Basic Double Doors | `3223646936` |
| `gunseeker.repairstation` | Repair Station | `3534893110` |
| `guy762.kotorfactions` | Star Wars KotOR Factions | `3379096669` |
| `hailuan.customquestframework.rimtalk` | Custom Quest Framework-Rimtalk addon | `3684497117` |
| `hailuan.dungeon` | Dungeon Core | `3064597982` |
| `hailuan.spacetower` | Space Tower | `3527936083` |
| `hailuan.voiduniverse` | Dlc collaboration - Void universe | `3587277884` |
| `haplo.miscellaneous.training` | Misc. Training | `717575199` |
| `happycam.conditioncauserretexture` | Mechanoid Cluster Retexture | `3523231836` |
| `harryrobinson.primitivefloorscheap` | Cheaper Primitive Floors | `2833159444` |
| `hatti.qualitybuilder` | QualityBuilder Unofficial 1.6 | `3512466087` |
| `hd2.pelican` | Vehicles - Pelican(Helldivers 2) | `3370607942` |
| `hdz.asteroidsurvival` | 剧本扩展:小行星空岛生存 | `3527737313` |
| `hekmo.chimeravariants` | Anomaly - Chimera Variants | `3482158348` |
| `hg.originals.f3` | F3: Spacer Jumpsuits and More | `2776936670` |
| `hiztaar.essential.uscmcore` | USCM - Core | `726855894` |
| `hiztaar.optionnal.uscmfcm` | USCM - Colonial Marines Corps Faction | `759866027` |
| `hiztaar.optionnal.uscmxenomorphs` | USCM - Xenomorphs Faction | `974867140` |
| `hoboofserenity.thrumbohusbandry` | Thrumbo Husbandry | `2208985736` |
| `hol.stellarisicons` | Stellaris Ideology Icons | `3540888076` |
| `icc.tov.tbc` | Taste of Vanilla - The Brotherhood Compendium | `3008804056` |
| `ih.clean.textures` | Clean Textures | `2865361569` |
| `ingendum.animalarmorbasic` | Animal Apparel: Basic Armor | `3513849448` |
| `ingendum.animalarmoruniversal` | Animal Apparel: Universal Basic Armor | `3524467381` |
| `inglix.fasterbiosculptingpod` | Faster Biosculpter Pod | `2576257954` |
| `inoshishi3.smallvehicleaddons` | Small Vehicle Add-ons | `3420948947` |
| `issaczhuang.muzzleflash` | Muzzle Flash | `2917732219` |
| `jackdeg.fieldadminister` | Field Administer | `2472006801` |
| `jalapenolabs.rimworld.fishingisfun` | Fishing Is Fun | `3538562620` |
| `jamaicancastle.rf.fertilefields` | Fertile Fields 1.6 | `3225843229` |
| `jdalt.nmldt` | No More Lethal Damage Threshold | `2657551690` |
| `jelly.bar0th.closesettlements` | Close Settlements | `2600837512` |
| `jetharius.feedinfishies` | FeedinFishies | `3573713081` |
| `jf.geometricfloors` | [JF] Geometric Floors | `2863525144` |
| `jf.royalcarpets` | [JF] Royal Carpets | `2977701969` |
| `jiopaba.fences` | More Vanilla Fences | `2546954423` |
| `jkluch.haultostack` | Haul to Stack | `949498803` |
| `joe.mo.tweaks` | Joe's Tweaks | `3458506170` |
| `joe.rpgadventureflavour.fork` | RPG Adventure Flavour Pack - Fork | `3342554570` |
| `joe.xenomorphinsectoids` | XenomorphInsectoids | `2873545234` |
| `joeownage.automatic.traderships` | Medieval Trader Airships (Legacy) | `3448488157` |
| `jsin.laglesslamps` | Lagless Lamps - C# | `3467878826` |
| `kathanon.craftwithcolor` | Craft with Color | `2795998250` |
| `kathanon.fixstyledblueprints` | Fix Styled Blueprints | `2957953663` |
| `kathanon.limitquestpawns` | Limit Quest Pawns | `2898408684` |
| `kathanon.nodisabledfactions` | No Disabled Factions In Quests | `2892125637` |
| `katsudon.uiretexture` | UI Retexture | `2978831421` |
| `keepercraft.rimkeeperanimals` | RimKeeper - Wild Animal Procreation | `3259367736` |
| `keshash.layeredwalldestruction` | Layered Wall Destruction | `3024527775` |
| `keyz182.keyzmiscresources` | Keyz Misc Resources | `3355560776` |
| `khamenman.outfitstandsplus` | Outfit Stands Plus | `3545172389` |
| `kilo.odysseusvacset` | Odysseus Vacsuit Set | `3530182181` |
| `kittahkhan.grazeup` | [Kit] Graze up | `2302739121` |
| `kitty.treememepatch` | Gauranlen Supremacy doesn't need Tree Connection! | `3556875187` |
| `koberiddle.milkandwoolpatches` | More Milkable and Shearable Animals | `3453878341` |
| `kongkim.droppodjammer` | Drop Pod Raid Jammer | `3527131849` |
| `konstantynopolitaneczka.disableraidneeds` | Disable Raid Needs | `3568265578` |
| `krafs.levelup` | Level Up! | `1701592470` |
| `krkr.rule56` | [1.6] CAI 5000 - Advanced AI + Fog Of War (continued) | `3673768803` |
| `kyrun.reunion` | Reunion | `1985186461` |
| `lambda.nuclearstove` | Lambda's Nuclear-Powered Stove | `3347342950` |
| `latta.petknowstrueyou` | ANDH - Animals Nuzzling Detects Horrors | `3230195082` |
| `lecht.lockapparel` | Lock apparel | `3507498385` |
| `lee.theforce.factions` | Star Wars : The Force Factions | `3557220783` |
| `lee.theforce.standalone` | Star Wars : The Force Standalone | `3557220601` |
| `lee.xenotypefloattodialogue` | Premade Xenotype Floatmenu to Dialog | `3350991041` |
| `legendaryminuteman.mai` | More Archotech Implants | `2646064233` |
| `leyley.rimtalkideologypatch` | RimTalk Ideology Patch | `3724752618` |
| `linnun.autocastspecialistcommands` | Auto-Cast Specialist Commands | `3459647882` |
| `linnun.kitchensinkfix` | Kitchen Sink Fix for Vanilla Cooking Expanded | `3288756218` |
| `longman.smallerradiusforanimatreesandshrines` | Smaller radius for Anima Trees, Shrines and Animus Stones | `2812513517` |
| `lordkuper.equipmentmanager` | Equipment Manager | `2790435986` |
| `louize.runtimegc.fork` | RuntimeGC [1.6] fork2 | `3528496623` |
| `lts.i` | Integrated Implants | `3223443793` |
| `m00nl1ght.unofficialupdates.hugslogpublisher` | Log Publisher from HugsLib | `2873415404` |
| `m3.jangodsoul.aqw.armorset` | [JDS] AQW Armor Set | `3541935426` |
| `m3.jangodsoul.df.void` | [JDS] Dead Frontier - V.O.I.D | `3543946353` |
| `maaxar.dubsskylights.glasslights.patch` | Dubs Skylights Glass+Lights Patch | `1610803364` |
| `maiya.rimtalkdynamiccolors` | RimTalk DynamicColors 边缘世谭-言出多彩 | `3628773219` |
| `mandrake.wreckedmachines` | Wrecked Machines | `Mods/WreckedMachines` |
| `manulinkraft.waterretextured` | Water retextured | `2782707284` |
| `marek15.keeponlinking` | Keep On Linking | `2717482472` |
| `marvinkosh.sometimesraidsgowrong` | Sometimes Raids Go Wrong | `1551336515` |
| `masstell.geneticdrift16` | Genetic Drift 1.6 | `3522332727` |
| `matathias.ruthlessmechanoids` | Ruthless Faction Pursuit | `3621784437` |
| `mbee.strongerwings` | Stronger Wings | `3185383404` |
| `meltup.beautifuloutdoors` | Beautiful Outdoors | `2011794898` |
| `memegoddess.mealsonwheels` | Meals On Wheels - Continued | `3538082807` |
| `memegoddess.thickarmor` | Thick Armor - Continued | `3531630021` |
| `memer.minigravships` | Mini Gravships | `3527312835` |
| `metalocif.morecreeps` | More Creepjoiners | `3434682604` |
| `mingtuwuxiang.gothicdecorative` | [MUS]哥特式吸血鬼家具 Gothicstyle Vampire Furniture | `3102678787` |
| `misstall.throwingweaponbeltz` | Throwing Weapon Belt | `3238126692` |
| `mitasamodel.outfitted` | Outfitted 1.6 | `3546414006` |
| `mlie.animalharvestingspot` | AnimalHarvestingSpot (Continued) | `1542765654` |
| `mlie.biosculptingplus` | BioSculptingPlus (Continued) | `3272451634` |
| `mlie.blockunwantedminutiae` | Block Unwanted Minutiae (Continued) | `3278213153` |
| `mlie.changestuffproperties` | Change Stuff Properties | `2788278669` |
| `mlie.cleaningpriority` | Cleaning Priority (Continued) | `2018316486` |
| `mlie.colourfulsteriletiles` | Colourful Sterile Tiles | `1619656080` |
| `mlie.combatreadinesscheck` | Combat Readiness Check (Continued) | `2314304057` |
| `mlie.compactworktab` | Compact Work Tab (Continued) | `3250322299` |
| `mlie.cutplantsbeforebuilding` | Cut plants before building (Continued) | `3286376165` |
| `mlie.ducksnolimitsideology` | Ducks' No Limits - Ideology (Continued) | `2916566114` |
| `mlie.durableclothes` | Durable Clothes (Continued) | `2015395963` |
| `mlie.expandedincidents` | Expanded Incidents (Continued) | `2039064466` |
| `mlie.iclearlyhaveenough` | I Clearly Have Enough! (Continued) | `2023661266` |
| `mlie.justignoremepassing` | Just Ignore Me Passing (Continued) | `3503627342` |
| `mlie.jwlatmosphericwaterprocessor` | [JWL] Atmospheric Water Processor (Continued) | `3007838663` |
| `mlie.livewiththepain` | Live With The Pain | `2659985388` |
| `mlie.morepsycasts` | More Psycasts (Continued) | `2036349987` |
| `mlie.newlimbsneedstraining` | New Limbs Needs Training | `2439159828` |
| `mlie.newzonetools` | New Zone Tools (Continued) | `2377860105` |
| `mlie.norandomideologies` | No Random Ideologies | `3337263133` |
| `mlie.nwnrealfogofwar` | (NWN) Real Fog of War (Continued) | `3391128917` |
| `mlie.pawneducation` | Pawn Education (Continued) | `2296533470` |
| `mlie.pawnnamevariety` | Pawn Name Variety (Continued) | `3548290568` |
| `mlie.prostheticnomissingbodyparts` | Prosthetic No Missing Body Parts (Continued) | `2739055353` |
| `mlie.realfactionguest` | Real Faction Guest (Continued) | `2886929245` |
| `mlie.recipeicons` | Recipe icons (Continued) | `2904906618` |
| `mlie.reconanddiscovery` | Recon And Discovery (Continued) | `2035131107` |
| `mlie.sfcomfymeditation` | SF Comfy Meditation (Continued) | `3432727841` |
| `mlie.smarterdeconstructionandmining` | Smarter Deconstruction and Mining (Continued) | `3261302741` |
| `mlie.spreadtheword` | Spread The Word (Continued) | `3287847068` |
| `mlie.stufflist` | Stuff List (Continued) | `2798767227` |
| `mlie.tribalsignalfire` | Tribal Signal Fire (Continued) | `2026582975` |
| `mlie.ultratechshades` | Ultratech Shades (Continued) | `2937778775` |
| `mlie.wehadatrader` | We Had a Trader? (Continued) | `1541408076` |
| `mlie.wzrdcarrycapacity` | [WZRD] Carry Capacity (Continued) | `2237017954` |
| `mlmlmlm.bluearchivefurniture` | Blue Archive Furniture | `3491176484` |
| `mo.decorationsluxury` | Decorations and dishes at Gorgeous banquet | `3027639868` |
| `mo.technicalmapvehicles` | Technical map Vehicles | `3438366909` |
| `mooloh.dndmenagerie` | Mooloh's Dnd Menagerie | `2751849453` |
| `mortstrudel.mortideologyscifai` | Empiricism and Faith - Mort's Ideologies: Memes and Precepts | `2948947009` |
| `mrhydralisk.anomaliesexpected` | Anomalies Expected | `3240752689` |
| `mrhydralisk.vnpereimaginedprogression` | Vanilla Nutrient Paste Expanded: Reimagined Progression | `3530651481` |
| `mrhydralisk.voedeliverylogistics` | Vanilla Outposts Expanded: Delivery Logistics | `3006726393` |
| `mrhydralisk.voepowergrid` | Vanilla Outposts Expanded: Power Grid | `2915686437` |
| `mrhydralisk.voeprisonerpatch` | Vanilla Outposts Expanded: Prisoner Patch | `3002936071` |
| `mrkociak.yetanotherprostheticexpansionmodcore` | Yet another prosthetic expansion mod - Core | `2808872704` |
| `mrsamuelstreamer.rimthemesrecolours` | Basic RimThemes Recolours | `2916014613` |
| `mrwireman.powercell.01` | Practical Powercells | `3524003581` |
| `mrwireman.stealthshuttle` | Stealth Shuttle | `3534488918` |
| `mss.flavourpack` | MSS Tweaks and Fun | `3379574408` |
| `mss.recube` | Recubes Your Cube | `3220139435` |
| `msws.growingzoneicons` | GrowingZoneIcons | `3531165541` |
| `mute.vpesensitivity` | Psychic Sensitivity Affects More (VPE) | `2881380497` |
| `myf.lightseeker` | Ars Mythica - Lightseeker | `3068154233` |
| `myf.vpe.tweaks` | Myf's Vanilla Psycast Expanded Tweaks | `3328399391` |
| `nakomaru.vanillafyfloors` | Vanillafy Floors | `3219321678` |
| `nals.customportraits` | [NL] Custom Portraits | `1569605867` |
| `nalzurin.betterdistresscall` | Better Distress Call | `3305489753` |
| `name.krypt.rimworld.pawntablegrouped` | Grouped Pawns Lists | `2340773428` |
| `name.krypt.rimworld.rwlayout.alpha2` | RWLayout | `2209393954` |
| `nanoce.glasslights` | Glass+Lights | `826153738` |
| `nathanielcwm.beautifulwater` | Beautiful Water (Fork) | `2039480177` |
| `nd.rtpj` | Projectile Bullet Retexture | `2962208832` |
| `neachi.rimtalkdialoguepatch` | RimTalk Dialogue Patch | `3631632728` |
| `nep.getoffmygravship` | Get Off My Gravship! | `3548548674` |
| `neronix17.archotech.genetics` | Archotech Genetics | `2995858859` |
| `neronix17.hd.pawns` | Vanilla Pawns Retextured | `2275310562` |
| `neronix17.retexture.vanillabeards` | Vanilla Beards Retextured | `2777098392` |
| `neronix17.retexture.vanillahair` | Vanilla Hair Retextured | `2748834409` |
| `nibato.autoextractgenes` | AutoExtractGenes | `2882834449` |
| `nightmare.devmodehotkey` | Development Mode Hotkey | `3009274839` |
| `nightmare.museums` | Museums | `3204176859` |
| `nikidigi.resurrectenemymechanoids` | Resurrect Enemy Mechanoids | `2882468335` |
| `nilchei.dynamicdiplomacycontinued` | Dynamic Diplomacy - Continued | `3220299022` |
| `niz.xenomorphtype` | Alien \| Rimworld | `3596077324` |
| `none1637.mechenergysetting` | Mech energy setting | `3238097300` |
| `novatrium.spacewaves` | Winston Waves Odyssey integration | `3603474848` |
| `noxilie.regrow.wmb.morevanillabiomes` | ReGrowth 2 World Map Beautification for More Vanilla Biomes | `3564679624` |
| `nuanki.controlledrituals` | Controlled Rituals - Anomaly | `3328826971` |
| `nuanki.unlimitedreborn` | Un-Limited Reborn | `3295368629` |
| `oblitus.mylittleplanet` | My Little Planet | `1117406550` |
| `obsidiaexpansion.ideology.icons` | Obsidia Expansion - Ideology Icons | `2990607010` |
| `ocarina.hazzor.moon.factions` | Moon Factions | `3561739080` |
| `oceantest5.rimtalk.enhance` | RimTalk.DisplayOptimization | `3629456304` |
| `oceantest6.rimtalk.promptcleaner` | RimTalk-PromptCleaner | `3630607068` |
| `oceantest7.rimtalk.memory` | RimTalk-MemoryDigest | `3726488698` |
| `oddbase.nuclearrevolution` | Nuclear revolution | `3536364597` |
| `oels.nanamefloors` | NANAME Floors | `3293767181` |
| `og.immersive.filter` | [Og] Immersive Filter | `3735827910` |
| `og.repair.your.gear` | [Og] Repair Your Gear | `3513376486` |
| `ok.scraptek` | Oktober's Scrap-Tek | `3122686960` |
| `okagrim.duskwood` | Dusk Wood Biome | `3560499511` |
| `okagrim.necrotexgrav` | [Odyssey] Necrotic Gravship Retextured | `3567591339` |
| `onyxae.dragonsdescent` | Dragons Descent | `2026992161` |
| `oracle.miscellania` | Oracle's Miscellania | `3279582979` |
| `orion.cashregister` | Cash Register (Continued) | `3509487668` |
| `orion.gastronomy` | Gastronomy (Continued) | `3509488152` |
| `orion.hospitality` | Hospitality (Continued) | `3509486825` |
| `oskarpotocki.vanillafactionsexpanded.settlersmodule` | Vanilla Factions Expanded - Settlers | `2052918119` |
| `oskarpotocki.vanillavehiclesexpandedupgrades` | Vanilla Vehicles Expanded - Upgrades | `3302208420` |
| `oskarpotocki.vfe.classical` | Vanilla Factions Expanded - Classical | `2787850474` |
| `oskarpotocki.vfe.deserters` | Vanilla Factions Expanded - Deserters | `3025493377` |
| `oskarpotocki.vfe.empire` | Vanilla Factions Expanded - Empire | `2938820380` |
| `oskarpotocki.vfe.medieval2` | Vanilla Factions Expanded - Medieval 2 | `3444347874` |
| `owlchemist.fridgeutilities` | Simple Utilities: Fridge | `3219883811` |
| `owlchemist.moonlight` | Moonlight | `3261311563` |
| `owlchemist.simplefx.smoke2` | Simple FX: Smoke | `3261314247` |
| `owlchemist.smartfarming` | Smart Farming | `3220129183` |
| `owlchemist.toggleableoverlays` | Toggleable Overlays | `3261316725` |
| `owlchemist.toggleablereadouts` | Toggleable Readouts | `3261317086` |
| `owlchemist.toggleableshields` | Toggleable Shields | `3261317430` |
| `p90forretail.nanomachines` | Luciferium Mood Boost | `2810755290` |
| `paragon.hanul.unlimitedarmor` | UnLimitedArmor | `1695493009` |
| `pershonkey.startdate` | Start Date | `2991015129` |
| `pesky.arcanist.style` | Pesky's Arcanist Ideology Style Pack | `3370539088` |
| `phaneron.basic.storage` | Phaneron's Basic Storage | `3201536200` |
| `phaneron.simplelearningretexture` | Simple Learning Retexture | `3026005966` |
| `phaserrave.deathpallcalypse` | Deathpallcalypse | `3253910772` |
| `phomor.craftingqualityrebalanced` | Crafting Quality Rebalanced | `1542004942` |
| `pixelbirb.dwc` | Dynamic Weapon Cooldown | `3038525914` |
| `pjerri.waveraids` | Wave Raids | `3692439859` |
| `planttreeindoor.serval.patch` | PlantTreeIndoor | `3569744872` |
| `pphhyy.demigryphsmod` | pphhyy's Demigryphs Continued | `3540496928` |
| `pphhyy.guldennew` | Gulden Biome (Continued) | `3607066070` |
| `pphhyy.lightlessempyrean` | Lightless Empyrean Reborn | `3517488959` |
| `prkr.genetools` | Gene Tools - Forked | `3047454700` |
| `proxyer.dismantleancientjunk` | Dismantle Ancient Junk | `2871064871` |
| `proxyer.optionalicons4ai` | Optional Icons for Architect Icons | `1966995052` |
| `puremj.mjrimmods.smartmeditation` | Smart Meditation | `2800676538` |
| `puremj.mjrimmods.vanillafixhaulafterslaughter` | Vanilla Fix: Haul After Slaughter | `2801452324` |
| `qwertaii.substructureanywhere` | Gravship Substructure Anywhere | `3528440892` |
| `rabiosus.vfautoparking` | Automatic Parking | `3365473553` |
| `rah.rbse` | RBSE | `850429707` |
| `rakros.upgradequality` | Upgrade Quality | `3176082972` |
| `rashomcree.odyssey.asteroidgrounds` | Asteroid Grounds | `3527371016` |
| `rashomcree.odyssey.orbitalplatforms` | Orbital Platforms | `3525980713` |
| `ratys.madskills` | Mad Skills | `731111514` |
| `ray1203.simplecamerasetting` | SimpleCameraSetting | `3232415388` |
| `rebuild.cotr.doorsandcorners` | ReBuild: Doors and Corners | `3262718980` |
| `redmattis.betterconversion` | Wololoo - Better Conversion and Recruitment | `3108763487` |
| `redmattis.bsfurniture` | Big and Small Furniture | `3024478368` |
| `redmattis.geneextractor` | Gene Extractor Tiers | `3016454783` |
| `redmattis.genenodes` | Gene Nodes - Genes for Sale | `3264344552` |
| `redmattis.heaven` | Big and Small - Heaven and Hell | `3170117364` |
| `redmattis.morexenos` | Big and Small - More Xenotypes | `3218636337` |
| `redmattis.undead` | Big and Small - Vampires and the Undead | `2926556467` |
| `redmattis.undead.medieval` | Medieval Undead Hordes | `2994387009` |
| `redmattis.vanillagenesrebalanced` | Vanilla Genes Rebalanced | `2905707100` |
| `redtrainer.compactgenebuildings` | Compact Gene Banks/Processors | `3466062158` |
| `redundant.oopsallgenepacks` | Oops All Gene Banks | `2883683444` |
| `reel.expanded.storage` | Reel's Expanded Storage | `3237638097` |
| `reel.hair` | Reel's Galactic Hairs | `2278578765` |
| `reel.hair2` | Reel's Frieren Hairs | `3119772468` |
| `reel.insectorfaction` | Reel's Insector Faction | `3309022698` |
| `regrowth.botr.aspenforest` | ReGrowth 2: Aspen | `2545774148` |
| `reiquard.questexpirationcriticalalert` | Quest Expiration Critical Alert | `2405632805` |
| `reo.rimscent` | RimScent | `3645569466` |
| `resurrectionem.khayrea` | Khayrea Pass Stylepack | `3372728277` |
| `resurrectionem.romascita` | Romascita Style pack | `3277109336` |
| `resurrectionem.rowmart` | RowMart Stylepack | `3503142907` |
| `resurrectionem.swifttools` | Swift Tools Stylepack | `3378901481` |
| `resurrectionem.wartalker` | Wartalker Stylepack | `3569670754` |
| `rh2.faction.utilitarian` | [RH2] Faction: Utilitarian | `2942350062` |
| `rh2.faction.void` | [RH2] Faction: V.O.I.D. | `2883208829` |
| `rh2.void.storyteller` | [RH2] V.O.I.D. Storyteller | `2130957394` |
| `rimeffectrenegade.asarireapers` | Rim-Effect Renegade: Asari and Reapers | `3473370728` |
| `rimeffectrenegade.core` | Rim-Effect Renegade: Core | `3473370247` |
| `rimeffectrenegade.drell` | Rim-Effect Renegade: Drell | `3473371103` |
| `rimeffectrenegade.extendedcut` | Rim-Effect Renegade: Extended Cut | `3473382290` |
| `rimeffectrenegade.n7` | Rim-Effect Renegade: N7 | `3473371554` |
| `rimsenal.federation` | Rimsenal Faction Pack - Federation | `736172213` |
| `rimsenal.spacer` | Rimsenal Faction Pack - Spacer | `3086137468` |
| `rimsenal.techist` | Rimsenal Style Pack - Techist | `2661828028` |
| `rimsenal.urb` | Rimsenal Style Pack - Urbworld | `2908039338` |
| `rimtalk.quests` | RimTalk - Quests | `3642675329` |
| `rimtalk.styleexpand` | RimTalk StyleExpand | `3694936738` |
| `rimworld.randomcoughdrop.geneassistant` | Random's Gene Assistant | `2882497271` |
| `rince.ideo.warframesymbols` | Ideology Warframe Icons | `2937728695` |
| `robtherobotguard.toomanyrewardswinstonwave` | Too Many Rewards - A Winston Wave Addon | `3763619179` |
| `romyashi.bunnyframework` | Bunny Framework | `3015333853` |
| `romyashi.extractanyplant` | Extract Any Plant | `2833838214` |
| `romyashi.scavenging` | Scavenging | `3108829323` |
| `rooboid.hdhair.continued` | Roo's HD Hairstyles (continued) | `3559870636` |
| `rp.rimtalk.personadirector` | RimTalk: Persona Director | `3619548407` |
| `ru.anomalyskilltrainer` | Anomaly Skill Trainer | `3602237032` |
| `runningbugs.landingonasteroid` | Landing On Asteroid 着陆小行星 | `3532991747` |
| `saltgin.rimtalkeventmemory` | RimTalk Event+ | `3612632140` |
| `samael.livestocktraders` | Livestock Traders | `2960610215` |
| `sandy.rpgstyleinventory` | RPG Style Inventory | `1561221991` |
| `sanguo.rimtalk.expandactions` | RimTalk - Expand Actions | `3628755033` |
| `sarg.alphabooks` | Alpha Books | `3403180654` |
| `sarg.alphacrafts` | Alpha Crafts | `3382446150` |
| `sarg.alphapropsparks` | Alpha Props - Parks and Gardens | `3146268928` |
| `sarg.smartodyssey` | Smart Odyssey | `3522762411` |
| `sarg.smartspeed` | Smart Speed | `1504723424` |
| `sbz.neatstorage` | [sbz] Neat Storage | `3416243474` |
| `sc.waterplace` | Artificial Water Place | `2382789361` |
| `scherub.planningextended` | Planning Extended | `2877392159` |
| `scorpio.optimizationleathers` | Optimization: Leathers - C# Edition | `2591816333` |
| `scorpio.staggeredraids` | Staggered Raids | `3531990280` |
| `scorpio.vemedicaldripsdubsbadhygiene` | VE Medical drips - Dubs Bad Hygiene patch | `2940894029` |
| `scrubdaddy.hairstyles` | ScrubDaddy's Hairstyles | `3536769145` |
| `scurvyez.bondedanimalsrng` | Bonded Animals RNG | `3370236256` |
| `scurvyez.steveswalls` | Steve's Walls | `2616538981` |
| `seohyeon.letterstackcleaner` | Letter stack cleaner | `2669779266` |
| `seohyeon.optimizationmeats` | Optimization: Meats - C# Edition | `2542931556` |
| `serek.misctrainingmedievalretexture` | Misc. Training Medieval Retexture | `3271602770` |
| `seti.millitarism` | Millitarism Meme | `3482463633` |
| `setosa.power.tools` | Setosa's Power Tools | `3526160222` |
| `shakeyourbunny.fastspreadinggrass` | Fast Spreading Grass | `3541038010` |
| `shenanigans.tribalbackstories1.4` | Tribal Backstories | `2879649038` |
| `shepirotgamer.slightlyfastermechgestator` | Slightly Faster Mech Gestator | `3546705271` |
| `shinzy.apparello` | Apparello 2 | `728381322` |
| `shira.rgrwthpatch` | ReGrowth: Core Animal Texture Patch | `2985646173` |
| `shunthewitch.termimother` | WM420_Mother | `3248912334` |
| `sielfyr.archeangravship` | Archean Tree in Gravship | `3530307917` |
| `silencer59.timekills` | Time Kills | `2374079539` |
| `sirmashedpotato.bloodmoon` | Mashed's Bloodmoon | `3523186663` |
| `sirmashedpotato.escp.skyshards` | ESCP - Skyshards | `2814453057` |
| `sirmashedpotato.questingmeme` | Questing Meme | `2826539854` |
| `sirrandoo.bettersliders` | BetterSliders | `2218078784` |
| `sirrandoo.mpe` | More Pause Events | `1874708724` |
| `sirrolin.questsgivesgoodwill` | Questing Gives Goodwill (1.6) | `3074941619` |
| `sirvan.mechanitorretexture` | Van's Retexture : Mechanitor | `2943977908` |
| `sirvan.misctrainingretexture` | Van's Retexture : Misc. Training | `2848956469` |
| `sl4vp0wer.sleepmeditation.1.5` | Sleep Meditation | `3238976509` |
| `slaughteringmeme.rince` | Slaughtering Meme | `3151598704` |
| `sm.medievalrepair` | Medieval Repair | `2955709750` |
| `smeir.fastersettlementrestock` | Faster Settlement Restock | `3363826406` |
| `smuffle.harvestorganspostmortem` | Harvest Organs Post Mortem Continued | `1204502413` |
| `sneaks.recycle` | Recycle 1.5 | `1534883539` |
| `son1c.greenworldregrowth` | Greenworld - ReGrowth | `2882040405` |
| `soulretextured.recyclethis` | Retextured! - Recycle This | `2978527594` |
| `souper.anomalyanywhere` | Anomaly Anywhere | `3534053654` |
| `spacemoth.youdriveisleep` | You Drive, I Sleep | `3324430833` |
| `stagz.vsierationaltraitdevelopment` | VSIE - Rational Trait Development | `2916405546` |
| `statistno1.enchantqualityplusunofficial` | EnchantQualityPlus | `3531518926` |
| `statistno1.evolvedorgansredux` | EvolvedOrgansRedux | `3648390934` |
| `steelchicken.devilstrandhydroponics` | Devilstrand Hydroponics | `2008034916` |
| `steve.betterquestrewards` | Better Quest Rewards | `2671237934` |
| `steve.vpe.revertsomenerf` | VPE: Revert Some Nerfs (Continued) | `3484509389` |
| `stevezero.fullarmorhandsfeet` | Full Armor - Hands and Feet [1.6] | `3530977354` |
| `sumghai.medpod` | MedPod | `2153065191` |
| `sumghai.replimat` | Replimat | `1715402900` |
| `sumghai.replimatmeals` | Replimat Meals | `3274344708` |
| `sumika.overflowingflowers` | OverflowingFlowers | `3005103112` |
| `sun.reducer` | Sun Lamp Power | `738063560` |
| `superniquito.modoptionssort` | Mod Options Sort | `2910865748` |
| `superniquito.traiticons` | Trait and Backstory Icons | `2873494547` |
| `superpox.gravshipbiofuelrefineryretexture` | Gravship Biofuel Refinery Retexture | `3553790634` |
| `svcbot.lhm` | Luci heals more! | `965087548` |
| `swwu.mechanitorcommandrange` | Unlimited Mechanitor Command Range | `2878895195` |
| `syrchalis.processor.framework` | [SYR] Processor Framework | `3210544395` |
| `syrus.bpansresize` | Biosculpter Pod and Neural Supercharger Resize | `2710513531` |
| `syrus.caravanmoodbuff` | Caravan Mood Buff | `2680751877` |
| `tac.genetrader` | Gene Trader | `2886375137` |
| `taggerung.configappliedcheck` | Config Applied Check | `3103608609` |
| `taggerung.customuiscales` | CustomUIScales | `2882372932` |
| `taggerung.iaintbuildingthat` | I Aint Building That | `3118060751` |
| `tc.tribalizedarmor` | TC Tribalized Armor | `3338236184` |
| `techmago.bootsnstuff` | Boots and Stuff | `1488970545` |
| `teiwaz.oot` | [GTG]Odyssey Orbital Trader | `3522859265` |
| `teiwaz.uws` | Sellable Odyssey Unique Weapons | `3522909912` |
| `telardo.dragselect` | DragSelect | `2599942235` |
| `telefonmast.graphicssettings` | Graphics Settings+ | `1678847247` |
| `tests.rottable` | Rottable Filter | `2845056427` |
| `thale.medievalerarimtheme` | Medieval Era RimTheme | `3551233435` |
| `thegoosebehindtheslaughter.noforcedslowdown` | No Forced Slowdown | `3223768532` |
| `thereallemon.powermill` | Power mill (1.4-1.6) | `2884054310` |
| `tickleyourpawn.core` | Tickle Your Pawn | `3721622218` |
| `timmyliang.tradehelper` | TradeHelper | `2113372560` |
| `tinda.medieval.tailor.continued` | Medieval Tailor Continued | `3512201406` |
| `tinda.patches.epochstallow` | Epochs Tallow - Butchery Patch | `3508507223` |
| `tixiv.whoshotmylegoff` | Who shot my leg off? | `3491552121` |
| `tk421storm.gardens` | Gardens | `2869260174` |
| `tk421storm.prioritytreatmentressurected` | Priority Treatment Ressurected | `3009738919` |
| `tolgrim.thermalwellexcavation` | Thermal Well Excavation | `3656836896` |
| `tookatee.fungoidnovomit` | Fungoids aren't that ugly! | `3433197206` |
| `tradingcontrol.tad.rimworld.core` | Trading Control | `2007107588` |
| `trickity.conversion.staff` | T's Conversion Staff | `2890481507` |
| `tro.soundscape.enhanced` | Rimworld: Soundscape Enhanced | `3276642170` |
| `turbopickle.gravshuttle` | Grav-Shuttle | `3528998097` |
| `tw.tangs.retexture.apparel` | [TW1.6]堂丸贴图重置~服饰 Tang's~Retexture~Apparel | `3255510656` |
| `tw.tangs.retexture.foods` | [TW1.6]堂丸贴图重置~食物 Tang's~Retexture~Foods | `3050762215` |
| `tw.tangs.retexture.manufactured` | [TW1.6]堂丸贴图重置~制成品 Tang's_Retexture_Manufactured | `3058943402` |
| `tw.tangs.retexture.resource` | [TW1.6]堂丸贴图重置~原材料 Tang's~Retexture~Resource | `3050448166` |
| `tw.tangs.retexture.structure` | [TW1.6]堂丸贴图重置~结构 Tang's~Retexture~Structure | `3168625192` |
| `tw.tangs.retexture.ui` | [TW1.6]堂丸贴图重置~UI Tang's~Retexture~UI | `3141849282` |
| `tw.tangs.retexture.weapons` | [TW1.6]堂丸贴图重置~武器 Tang's~Retexture~Weapons | `3048306872` |
| `tw.tangsbiome.rainbowforest` | [TW1.6]幻彩林地 Rainbow forest | `3532501549` |
| `twistedpacifist.reasonablecomponents` | Reasonable Components | `1542915888` |
| `ucp.invisiblewalls` | Ollie's Invisible Walls | `2857888739` |
| `ucp.starwarsdubshygienestuff` | Star Wars Dub's Hygiene Stuff | `3371695380` |
| `unagi.funiture.build.window` | UNAGI Decorative Furniture | `3379047800` |
| `unclejackhughes.barbarianstylepack` | Barbarian Style Pack | `3551819421` |
| `unknown.forcedxenogermimplantation` | Forced Xenogerm Implantation | `3586850201` |
| `unon.noburnmetal` | No Burn Metal | `1923990111` |
| `usagirei.pocketsand` | Pocket Sand | `2226330302` |
| `ushanka.biologicalwarfare` | Ushankas Biological Warfare | `3221550806` |
| `ushanka.necroaarchovirus` | Ushankas Necroa Archovirus | `3531035748` |
| `uveren.hemogenextractor` | Hemogen Extractor | `3267565839` |
| `van.datools` | Dark Ages : Medieval Tools | `3028566550` |
| `vanillaexpanded.basegeneration` | Vanilla Base Generation Expanded | `3209927822` |
| `vanillaexpanded.ideo.dryads` | Vanilla Ideology Expanded - Dryads | `2720631512` |
| `vanillaexpanded.ideo.iconsandsymbols` | Vanilla Ideology Expanded - Icons and Symbols | `2552609458` |
| `vanillaexpanded.ideo.sophianstyle` | Vanilla Ideology Expanded - Sophian Style | `3194606539` |
| `vanillaexpanded.recycling` | Vanilla Recycling Expanded | `3155781848` |
| `vanillaexpanded.vaeendandext` | Vanilla Animals Expanded — Endangered | `2366589898` |
| `vanillaexpanded.vaeroy` | Vanilla Animals Expanded — Royal Animals | `2858079457` |
| `vanillaexpanded.vanillafoodvarietyexpanded` | Vanilla Food Variety Expanded | `3334272487` |
| `vanillaexpanded.vanillasocialinteractionsexpanded` | Vanilla Social Interactions Expanded | `2439736083` |
| `vanillaexpanded.vbookse` | Vanilla Books Expanded | `2193152410` |
| `vanillaexpanded.vbrewecandt` | Vanilla Brewing Expanded - Coffees and Teas | `2275449762` |
| `vanillaexpanded.vcef` | Vanilla Fishing Expanded | `1914064942` |
| `vanillaexpanded.vcefaddon` | Vanilla Fishing Expanded - Fishing Treasures AddOn | `2468543398` |
| `vanillaexpanded.vhe` | Vanilla Hair Expanded | `1888705256` |
| `vanillaexpanded.vieat` | Vanilla Ideology Expanded - Anima Theme | `2666998627` |
| `vanillaexpanded.vnutriente` | Vanilla Nutrient Paste Expanded | `2920385763` |
| `vanillaexpanded.vpe.hemosage` | Vanilla Psycasts Expanded - Hemosage | `2990596478` |
| `vanillaexpanded.vpe.puppeteer` | Vanilla Psycasts Expanded - Puppeteer | `3033779606` |
| `vanillaexpanded.vpersonaweaponse` | Vanilla Persona Weapons Expanded | `2826922787` |
| `vanillaexpanded.vplantse` | Vanilla Plants Expanded | `2134308522` |
| `vanillaexpanded.vplantsemore` | Vanilla Plants Expanded - More Plants | `2748889667` |
| `vanillaexpanded.vplantsemushrooms` | Vanilla Plants Expanded - Mushrooms | `3006389281` |
| `vanillaexpanded.vpsycastse` | Vanilla Psycasts Expanded | `2842502659` |
| `vanillaexpanded.vtexe` | Vanilla Textures Expanded | `2016436324` |
| `vanillaexpanded.vtexvariations` | Vanilla Textures Expanded - Variations | `2493234474` |
| `vanillaexpanded.vwel` | Vanilla Weapons Expanded - Laser | `1989352844` |
| `vanillaexpanded.vwenl` | Vanilla Weapons Expanded - Non-Lethal | `2454918354` |
| `vanillaquestsexpanded.deadlife` | Vanilla Quests Expanded - Deadlife | `3497226454` |
| `vanillaracesexpanded.customicons` | Vanilla Races Expanded - Custom Icons | `2917311689` |
| `vanillaracesexpanded.highmate` | Vanilla Races Expanded - Highmate | `2995385834` |
| `vanillaracesexpanded.hussar` | Vanilla Races Expanded - Hussar | `2893586390` |
| `vanillaracesexpanded.insector` | Vanilla Races Expanded - Insector | `3260509684` |
| `vanillastorytellersexpanded.winstonwave` | Vanilla Storytellers Expanded - Winston Waves | `3215569151` |
| `veltaris.mechanoidskins` | [AV] Mechanoid Skins | `3667667489` |
| `vesper.notmyfault` | Not My Fault | `2870045856` |
| `victor.genometable` | Vanilla Genetics Expanded - Genome Extracting Table ALL Genomes | `2883081878` |
| `victor.wallsaresolid` | Walls are solid | `2896548513` |
| `vingy.moreagingmulitplier` | MoreAgingMultiplier | `2879214881` |
| `visibleraidpoints.1trickpwnyta` | Visible Raid Points | `2562730174` |
| `void.szatmosphericevents` | SZ_Atmospheric Events | `1874676885` |
| `vortex.customizeweapon` | Customize Weapon | `3550585103` |
| `voult.betterpawncontrol` | Better Pawn Control | `1541460369` |
| `vpe.anima.sentinel` | VPE - Anima | `3462136587` |
| `vpe.horaxian.sentinel` | VPE - Horaxian | `3456508582` |
| `vpe.luminis.sentinel` | VPE - Luminis | `3559834496` |
| `vpe.voidweaver.sentinel` | VPE - Voidweaver | `3467913565` |
| `vr.animaanimalscombined` | Anima Animals Combined (Continued) | `3190798512` |
| `vse.perrypersistent` | Vanilla Storytellers Expanded - Perry Persistent | `2149702069` |
| `waffle.fantasypatches` | Medieval Fantasy Psycaster Raids | `3413747772` |
| `wall.light.relic` | Wall light Relic | `3220394219` |
| `wastelandr.betterroads` | Better Roads | `1489564822` |
| `winglessflight.gene` | Wingless Flight Gene | `3002447909` |
| `wolfcub05.draftableanimals` | Draftable Animals - Releashed | `3534629428` |
| `woolstrand.realruins` | Real Ruins | `1552146295` |
| `wtfomgjohnny.perishable` | Perishable | `2294597530` |
| `wuren.rimtalkcontextupgrade` | RimTalk Context Upgrade | `3641774579` |
| `wvc.sergkart.biotech.moremechanoidsworkmodes` | WVC - Work Modes | `2888380373` |
| `wvc.sergkart.ultraexpansion` | WVC - Ultra Expansion II | `3107443670` |
| `wyr3d.bettercampsites` | [WYD] Better Campsites | `3546818262` |
| `wyr3d.simpleboneblocks` | [WYD] Bone | `3195547844` |
| `wyr3d.worthlessplants` | [WYD] Worthless Plants | `3555545972` |
| `xale86.smallbedroomfurniture` | Small Bedroom Furniture | `3570779724` |
| `xale86.wallsolarpanels` | Wall mounted solar panels | `3545934731` |
| `xelnigma.mechanoidslagtoplasteel` | Mechanoid slag to Plasteel | `3552644190` |
| `xercaine.wallsunlamp` | Wall Sun Lamp | `3234498246` |
| `xmb.ancienthydroponicfarmfacilities.mo` | Ancient hydroponic farm facilities | `3075384838` |
| `xslayer300.ax.aliens.parta` | Aliens: Xenocide (MKI) | `2866528992` |
| `yoann.proselytizingnever` | Proselytizing Never | `3053650876` |
| `zaire82.rgretexpatches` | ReGrowth ReTextures Patches | `3410715318` |
| `zal.chooseyourrecipe` | Choose Your Recipe (Continued) | `3263007587` |
| `zal.fhf` | Friendly Hostile Factions (Continued) | `2812503053` |
| `zal.keptb` | KEP:Toolbox Bionics (Continued) | `2803222245` |
| `zal.primitivefloors` | Primitive Floors (Continued) | `2801265143` |
| `zal.sibtl` | Stranger In Black Techlevel | `3428237149` |
| `zal.zww` | Zalcore Winston Waves Control Panel | `3720234170` |
| `zav.fantasymetalsforked` | [ZAV] Fantasy Metals | `2936850549` |
| `zcubekr.customfonts` | Custom Fonts - Forked | `3231727915` |
| `zoarak.anomalyplat` | Anomaly Research Asteroid | `3527726648` |
| `zoarak.mechplat` | Mechanitor Orbital Platform | `3523146525` |
| `zruic.expand.action` | RimTalk - Expand Actions Core | `3661055729` |
| `zruic.expand.dialogue` | RimTalk - Expand Dialogue | `3662962455` |
| `zruic.expand.relation` | RimTalk - Expand Relation | `3661493651` |
| `zruic.expand.thoughts` | RimTalk - Expand Thoughts | `3661175034` |
| `zylle.morepredators` | More Predators | `2347596617` |

</details>

## (c) Duplicate packageIds across folders — 0

Derivation: `{k: v for k, v in present.items() if len(v) > 1}` → empty.

This is a stronger result than it looks: 1252 folders across three roots produced 1252 **distinct** packageIds, a clean bijection. There is no workshop-copy/local-copy shadowing anywhere — in particular the eight local mods under `...\RimWorld\Mods\` (`Jawa_Armoury`, `Jawa_Doctrine`, `Jawa_Patches`, `JawaIonWeapons`, `JawaVoice`, `MissingArtFixes`, `RimDefDump`, `WreckedMachines`) each own an id no workshop mod claims. The known historical hazard of a hand-copied mod shadowing its workshop original is **not present today**.

## (d) Expansions — 5 listed, 5 installed

`<knownExpansions>` holds 5 entries; each resolves to a folder under `...\RimWorld\Data\`:

| packageId | folder | present |
|---|---|---|
| `ludeon.rimworld` (Core, not an expansion) | `Data\Core` | yes |
| `ludeon.rimworld.royalty` | `Data\Royalty` | yes |
| `ludeon.rimworld.ideology` | `Data\Ideology` | yes |
| `ludeon.rimworld.biotech` | `Data\Biotech` | yes |
| `ludeon.rimworld.anomaly` | `Data\Anomaly` | yes |
| `ludeon.rimworld.odyssey` | `Data\Odyssey` | yes |

All five expansions plus Core are on disk and all six appear in `<activeMods>` at indices 3–8 (`ludeon.rimworld`, `.royalty`, `.ideology`, `.biotech`, `.anomaly`, `.odyssey`). Note `<knownExpansions>` lists the five DLCs only — Core is not in it, which is why 575 − 5 = 570 and not 569.

---

Reproduce: `python3 D:\Luke\dev\Rimworld\observed\2026-08-13_modset_census.py`. Runtime ~11 s wall for 1,252 folders — one `os.listdir` pass per root plus one `About.xml` parse per folder, no per-folder shell calls.
