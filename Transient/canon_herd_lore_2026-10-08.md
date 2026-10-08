# Canon herd / pack / domestic lore pass — 2026-10-08

Owner (typed, 2026-10-08 12:15): *"Go ahead and see if you can determine which canon creatures are clearly herd or pack or domesticatable animals in lore and which ones definitely aren't. Then ticket an item for me to go in and arbitrate the rest."* Addition: capture whether canon art already shows gender dimorphism.

**Method.** Every race ThingDef under `src/RimStarWars` and `src/RimUtinni` (237 defs) was resolved against Wookieepedia with the search API (`list=search`), then the canon page and its `/Legends` page were pulled whole (`action=parse`, wikitext, cached in `/home/mandrake/rm/scratch/BENCH/lore_cache/`). Each page was swept for group/solitary/domestication/sex wording; every verdict below was then read and set by hand. **Each non-UNCLEAR verdict quotes the sentence and names the page it came from** (the page column is re-checked by script against the cached text). Canon and Legends are both counted as lore; the page column says which.

**Two independent axes**, because the owner's three words are not exclusive: SOCIAL = HERD (lives in groups for grazing/protection) · PACK (hunts together) · GROUP (school/hive/flock/colony/pairs, no herd-or-pack wording) · SOLITARY (canon says solitary or a territorial loner) · UNCLEAR. DOMESTIC = DOMESTICATED (bred/kept/ridden/livestock/pet in canon) · NOT (canon says domestication fails) · UNCLEAR. Where canon's own word ("packs" of grazing scurriers) differs from the behaviour, the class follows the behaviour and the note says so.

## Summary (MEASURED from the CSV)

- **105 canon subjects** covering 121 of our defs (life stages and our invented morphs folded into their canon parent). 116 defs have no Wookieepedia subject (listed last).
- SOCIAL: GROUP 14 · HERD 26 · PACK 14 · SOLITARY 6 · UNCLEAR 45
- DOMESTIC: DOMESTICATED 49 · NOT 1 · UNCLEAR 55
- DIMORPHISM: NO 2 · UNKNOWN 90 · YES-in-canon-art 2 · YES-text-only 11
- **For the owner to arbitrate: 45 subjects with SOCIAL = UNCLEAR** (23 of them UNCLEAR on both axes).

**Sanity probe.** Bantha → HERD + DOMESTICATED ✔ · Eopie → HERD (20+) + DOMESTICATED ✔ · Dewback → DOMESTICATED ✔, social HERD (2–5) with a canon "reputation for being solitary" caveat. ⚠️ **Krayt dragon did NOT come back SOLITARY** — neither its canon nor its Legends page says anything about grouping; it is in the UNCLEAR list, and the solitary control was met instead by Horax ("solitary creatures"), Zakkeg ("solitary and territorial") and Wampa ("typically solitary hunters"). (No rancor def exists in our tree.)

**GPT consult.** One `gpt_consult.py -m gpt-6.1-sol --effort high` run on 35 hard cases timed out at 540 s with no answer; its one surfaced lead (wraids in groups of two to six) was checked against the cached Wookieepedia page and kept. Nothing else from GPT is used.

## Clear social verdicts

| subject | our defs | social | evidence (social) | domestic | evidence (domestic) | group size | dimorphism | note |
|---|---|---|---|---|---|---|---|---|
| Bantha | `RSW_Bantha` | **HERD** | "All banthas were peaceful omnivores and lived in herds." — *Bantha* | **DOMESTICATED** | "They were social herd animals, and were often domesticated" — *Bantha* |  | YES-in-canon-art: Legends image Bantha_Bull_and_Cow.jpg (viewed): bull has larger double-spiral horns and bigger head; cow a single spiral. Text: "bulls were larger than cows" (canon_references/bantha). |  |
| Eopie | `RSW_Eopie` | **HERD** | "They were very social creatures that lived in large herds of 20 or more." — *Eopie/Legends* | **DOMESTICATED** | "were domesticated by the planet's inhabitants" — *Eopie* | 20 or more | UNKNOWN |  |
| Dewback | `RSW_Dewback` | **HERD** | "wild dewbacks were also known to roam the seemingly endless deserts of Tatooine in single-file packs of two to five" — *Dewback/Legends* | **DOMESTICATED** | "where they were used as beasts of burden, as well as mounts" — *Dewback* | 2-5 | YES-text-only: Males display bellies that change to sky-blue when courting (display colouring, not a fixed look). | Same Legends sentence opens "While they had a reputation for being solitary animals"; another source (The Wildlife of Star Wars) says herds. Small-group grazer. |
| Fambaa | `RSW_Fambaa` | **HERD** | "In the wild, fambaas traveled in herds of up to twelve" — *Fambaa/Legends* | **DOMESTICATED** | "The fambaa had been domesticated by Gungans for millennia as beasts of burden" — *Fambaa/Legends* | up to 12 (breeding herds of hundreds) | UNKNOWN |  |
| Falumpaset | `RSW_Falumpaset` | **HERD** | "in large herds (as well as in family groups containing one adult bull and four to seven adult cows and their young)" — *Falumpaset/Legends* | **DOMESTICATED** | "Easily domesticated, falumpasets were popular mounts all over the galaxy." — *Falumpaset/Legends* | family group 1 bull + 4-7 cows | UNKNOWN: Bull/cow named; no stated look difference. |  |
| Shaak | `RSW_Shaak` | **HERD** | "Shaaks were plump quadrupedal herd animals native to the grasslands of Naboo." — *Shaak/Legends* | **DOMESTICATED** | "Gungans farmed shaaks for their meat and hide." — *Shaak* | a herd of fifteen (anecdote) | UNKNOWN |  |
| Nerf | `RSW_Nerf RSW_FeralNerf` | **HERD** | "evolved to tell apart different herds" — *Nerf* | **DOMESTICATED** | "Individuals who herded nerfs for a living were referred to as nerf herders." — *Nerf* |  | YES-text-only: Male nerfs were generally larger and more aggressive than their female counterparts, with more pronounced horns. | RSW_FeralNerf is our sub-variety; inherits nerf lore. |
| Reek | `RSW_IridonianReek` | **HERD** | "Reeks were usually found in herds" — *Reek/Legends* | **DOMESTICATED** | "They could also be found on Tatooine and in ranches on the Codian Moon and Saleucami." — *Reek/Legends* | small herds (Codian Moon) | YES-text-only: The horns of male reeks are usually larger than those of females (also canon_references/iridonianreek). |  |
| Jakobeast | `RSW_Jakobeast` | **HERD** | "Jakobeasts were Force-sensitive arctic herd animals" — *Jakobeast/Legends* | **DOMESTICATED** | "Jakobeasts were domesticated primarily for their meat, milk, and fur." — *Jakobeast/Legends* |  | UNKNOWN: "elder bulls turned outward" - no look difference stated. | Canon: "ill-suited to serve as mounts, guards, or attack animals". |
| Kybuck | `RSW_Kybuck` | **HERD** | "Pav-ti tracked a small herd of kybucks" — *Kybuck* | **DOMESTICATED** | "Some chieftains often domesticated kybucks as a symbol of status." — *Kybuck/Legends* | small herd | YES-text-only: Males had short horns sitting atop their head. |  |
| Uvak | `RSW_Uvak` | **HERD** | "stole an entire herd of uvak from the port town of Eorm" — *Uvak* | **DOMESTICATED** | "tamed and domesticated the uvaks" — *Uvak* |  | UNKNOWN |  |
| Varactyl | `RSW_Varactyl` | **HERD** | "had a brief encounter with a herd of varactyls" — *Varactyl* | **DOMESTICATED** | "incredibly loyal and obedient mounts" — *Varactyl* |  | YES-text-only: While females sported blue-green plumage and skin, males were mostly dull shades of orange and brown. (Legends image shows Boga, a female only.) |  |
| Gornt | `RSW_Gornt` | **HERD** | "Wild gornts traveled in packs of 10 to 30, with half of the pack being young gornts" — *Gornt/Legends* | **DOMESTICATED** | "The gornt was a domesticated, omnivorous creature" — *Gornt/Legends* | 10-30 | UNKNOWN | Canon word is "packs" but grazing livestock with young; caption "A herd of Gornts". |
| Zeer | `RSW_Zeer` | **HERD** | "Zeer traveled in herds" — *Zeer* | **UNCLEAR** |  |  | UNKNOWN | Shown at the Coruscant Livestock Exchange (image caption) and in zoos/circuses; no domestication statement. |
| Beldon | `RSW_Beldon` | **HERD** | "They traveled in free-floating herds numbering anywhere from 500 to 3,000." — *Beldon/Legends* | **UNCLEAR** |  | 500-3000 | UNKNOWN |  |
| Iriaz | `RSW_Iriaz` | **HERD** | "They lived in massive herds" — *Iriaz* | **UNCLEAR** |  | massive | UNKNOWN | "lone iriaz were usually sick, old, or injured, though the occasional rogue male". |
| Kwi | `RSW_Kwi` | **HERD** | "When traveling in herds across the plains" — *Kwi* | **UNCLEAR** |  |  | UNKNOWN |  |
| Hrumph | `RSW_Hrumph` | **HERD** | "Herds defended young from predators like veermoks by encircling them" — *Hrumph/Legends* | **UNCLEAR** |  |  | UNKNOWN |  |
| Corinathoth | `RSW_Corinathoth` | **HERD** | "encountered a herd of Korinatoths crossing the plains of Maridun" — *Corinathoth/Legends* | **UNCLEAR** |  |  | UNKNOWN |  |
| Woolamander | `RSW_Woolamander` | **HERD** | "babies would become members of troops numbering 20 individuals" — *Woolamander/Legends* | **UNCLEAR** |  | troops of ~20 | UNKNOWN |  |
| Mott | `RSW_Mott` | **HERD** | "Communes usually consisted of a dominant male and, perhaps, one lieutenant male that guarded the females and young." — *Mott/Legends* | **DOMESTICATED** | "Gungans found motts to be good pets" — *Mott/Legends* | commune | UNKNOWN: Legends image shows female + young only. |  |
| Scurrier | `RSW_Scurrier` | **HERD** | "Scurriers traveled in packs of around thirty" — *Scurrier/Legends* | **UNCLEAR** |  | ~30 | YES-text-only: Horns: those of a male were thick and curved, while those of a female were thin and straight. (Legends image shows a female only.) | Canon word is "packs" but they scatter from danger - a flee-group, not a hunting pack. |
| Kowakian monkey-lizard | `RSW_KowakianMonkeyLizard` | **HERD** | "rarely leaving the packs they moved around in for protection against predators" — *Kowakian monkey-lizard/Legends* | **DOMESTICATED** | "often used by members of the underworld as pets" — *Kowakian monkey-lizard* |  | UNKNOWN | Canon also: "impossible to train a monkey-lizard". Oldest female leads. |
| Pikobi | `RSW_Pikobis` | **HERD** | "The Pikobi traveled in pairs or groups of five to six." — *Pikobi/Legends* | **UNCLEAR** |  | 5-6 | UNKNOWN | Group-living; canon does not say they hunt together. |
| Clodhopper | `RSW_Clodhopper` | **HERD** | "they fed in swarms, becoming a real menace" — *Clodhopper* | **UNCLEAR** |  | swarm | UNKNOWN | Flightless crop-pest birds. |
| Jerba | `RSW_Jerba` | **HERD** | "a pack of anoobas killed or scattered Corey's entire herd" — *Jerba/Legends* | **DOMESTICATED** | "The jerba was an equine pack animal and beast of burden" — *Jerba/Legends* |  | UNKNOWN | Herd evidence is of a kept herd, not wild. |
| Womp rat | `RSW_WompRat` | **PACK** | "Womp rats were not timid creatures, hunting in packs" — *Womp rat* | **UNCLEAR** |  | up to 20 | UNKNOWN | Canon: "not unheard of for people to have domesticated womp rats as pets" - occasional pet, pest otherwise. |
| Gutkurr | `RSW_Gutkurr` | **PACK** | "Gutkurrs were pack hunters" — *Gutkurr* | **DOMESTICATED** | "for centuries they have been exported by crime lords as pets" — *Gutkurr/Legends* |  | UNKNOWN | "intelligent enough to be trained - but only by those brave enough". |
| Anooba | `RSW_Anooba` | **PACK** | "Anoobas were aggressive pack predators native to Tatooine." — *Anooba/Legends* | **DOMESTICATED** | "Anoobas could be trained to be pets,guards,or hunters." — *Anooba* | 10-12 | YES-text-only: males being larger than females (20-45 kg range). |  |
| Cannok | `RSW_Cannok` | **PACK** | "these packs were usually formed of three or more cannoks" — *Cannok* | **UNCLEAR** |  | 3+ | UNKNOWN |  |
| Marsh haunt | `RSW_MarshHaunt` | **PACK** | "they worked in loose packs of two to eight creatures to ambush prey" — *Marsh haunt* | **UNCLEAR** |  | 2-8 | UNKNOWN |  |
| Massiff | `RSW_Massiff` | **PACK** | "A pack of massiffs on Tatooine" — *Massiff* | **DOMESTICATED** | "Massiffs were often domesticated for sentry and guard tasks" — *Massiff* |  | UNKNOWN |  |
| Vornskr | `RSW_Vornskyr` | **PACK** | "A pack of vornskrs" — *Vornskr* | **DOMESTICATED** | "kept two vornskrs, Sturm and Drang, as pets and guard animals" — *Vornskr* |  | UNKNOWN | Social evidence is an image caption. |
| Vulptex | `RSW_Vulptex` | **PACK** | "They lived in groups referred to as skulks, regrouping three to four families with as many as ten creatures by family." — *Vulptex* | **UNCLEAR** |  | 3-4 families x up to 10 | UNKNOWN |  |
| Kreetle | `RSW_Kreetle` | **PACK** | "They attack in groups of four-to-five" — *Kreetle* | **UNCLEAR** |  | 4-5 | UNKNOWN |  |
| Hawk-bat | `RSW_Hawkbat` | **PACK** | "Flocks of hawk-bats would hunt and attack their prey as if they were one." — *Hawk-bat/Legends* | **UNCLEAR** |  | large flocks | UNKNOWN |  |
| Shyrack | `RSW_Shyrack` | **PACK** | "These winged monstrosities were eyeless beasts that hunted in swarms." — *Shyrack/Legends* | **UNCLEAR** |  | swarm | UNKNOWN | Also "fiercely territorial" (as a cave colony). |
| Sketto | `RSW_Sketto` | **PACK** | "Sketto tended to swarm with others of their kind to suck the blood of sleeping larger animals." — *Sketto/Legends* | **UNCLEAR** |  | swarm | UNKNOWN |  |
| Mynock | `RSW_Mynock` | **PACK** | "tended to flock together in a pack of ten" — *Mynock/Legends* | **UNCLEAR** |  | ~10; large migrating groups | UNKNOWN | Also "extremely territorial". Energy parasites, not hunters - "pack" is canon wording. |
| Hssiss | `RSW_Hssiss` | **PACK** | "When in the lakes on Ambria, they hunted in pairs" — *Hssiss* | **UNCLEAR** |  |  | UNKNOWN | One pet (Ktriss, Great Bogga's). |
| Lylek | `RSW_Lylek` | **GROUP** | "These hordes were led by a lylek queen" — *Lylek* | **UNCLEAR** |  | hundreds (hive) | UNKNOWN: Queen caste exists. | Hive insect. |
| Kinrath | `RSW_Kinrath` | **GROUP** | "a single female kinrath matriarch was the leader of a hive of kinrath" — *Kinrath/Legends* | **UNCLEAR** |  | hive | UNKNOWN: Matriarch caste stated. | Also "territorial". |
| Krykna | `RSW_Krykna` | **GROUP** | "cocooned their prey in underground hives" — *Krykna* | **UNCLEAR** |  | hive | UNKNOWN | Canon: "extremely difficult to tame with the Force". |
| Neebray | `RSW_Neebray` | **GROUP** | "Groups of neebray were called a pod." — *Neebray* | **UNCLEAR** |  | pod/flock | UNKNOWN |  |
| Mee | `RSW_Mee RSW_MeeJuv` | **GROUP** | "Mee were plentiful, traveling in schools of thousands" — *Mee/Legends* | **UNCLEAR** |  | thousands | UNKNOWN |  |
| Faa | `RSW_Faa RSW_FaaJuv` | **GROUP** | "a school of faa—which could include up to thirty fish" — *Faa/Legends* | **DOMESTICATED** | "Faa were sold in pet shops on Coruscant." — *Faa/Legends* | up to 30 | UNKNOWN | Pet-shop trade only. |
| Peko-peko | `RSW_PekoPeko` | **GROUP** | "Peko-pekos congregated in large flocks but generally traveled in pairs and mated for life." — *Peko-peko/Legends* | **DOMESTICATED** | "they were a favorite pet of both Gungans and Naboo" — *Peko-peko/Legends* | large flocks / pairs | NO: Both male and female had beautiful indigo-sapphire plumage, and both were the same size. |  |
| Porg | `RSW_Porg` | **GROUP** | "A group of porgs was called a "murder."" — *Porg* | **DOMESTICATED** | "Both wild and domesticated porgs were unusually smitten by human objects." — *Porg* |  | YES-text-only: Porgs were sexually dimorphic; males were slightly larger than females and had orange plumage around the eyes. |  |
| Voorpak | `RSW_Voorpak` | **GROUP** | "In the wild, they lived in small colonies" — *Voorpak/Legends* | **DOMESTICATED** | "They came from Naboo and were often kept as pets." — *Voorpak* | small colonies | UNKNOWN |  |
| Ronto | `RSW_Ronto` | **GROUP** | "While typically encountered in small groups" — *Ronto/Legends* | **DOMESTICATED** | "Easily domesticated, rontos were utilized by the Jawas as beasts of burden" — *Ronto* | small groups | UNKNOWN: Female in heat gives off musky scent (not visual). | Legends only for the group statement. |
| Convor | `RSW_Convor` | **GROUP** | "in the jungles of Wasskah they worked in pairs to fend off predators" — *Convor* | **DOMESTICATED** | "Convorees were popular as pets throughout the galaxy." — *Convor* |  | UNKNOWN |  |
| Wraid | `RSW_Wraid RSW_WraidAlpha` | **GROUP** | "Wraids were often seen in clusters from two to six members." — *Wraid* | **UNCLEAR** |  | 2-6 | UNKNOWN | WraidAlpha is our invention. |
| Qormot | `RSW_Qormot` | **GROUP** | "rival qormots or predators encroached on the territory of their small prides" — *Qormot* | **UNCLEAR** |  |  | UNKNOWN | Small territorial prides; also wiki category "Herd and pack creatures". |
| Ysalamiri | `SWPotF_RaceDef_ysalamir` | **GROUP** | "Many ysalamiri grouped together would expand their Force-neutral bubble" — *Ysalamiri/Legends* | **UNCLEAR** |  |  | UNKNOWN | "large groups of ysalamiri could extend their collective bubble"; one pet shown at a livestock exchange. |
| Horax | `RSW_Horax` | **SOLITARY** | "The carnivorous horaxes were solitary creatures." — *Horax/Legends* | **UNCLEAR** |  | pairs only to mate | UNKNOWN |  |
| Zakkeg | `RSW_Zakkeg` | **SOLITARY** | "Huge, armored quadrupeds, they were solitary and territorial." — *Zakkeg/Legends* | **UNCLEAR** |  |  | UNKNOWN |  |
| Wampa | `RSW_Wampa` | **SOLITARY** | "Wampas were typically solitary hunters." — *Wampa/Legends* | **UNCLEAR** |  | alone or small family groups | UNKNOWN: Legends image: female and cubs (one sex shown). | Canon: "occasionally hunted in packs". Captive/"trained" wampas exist but no domestication. Captive wampas only; no domestication statement. |
| Mudhorn | `RSW_Mudhorn` | **SOLITARY** | "The mudhorn was an extremely territorial creature by nature" — *Mudhorn/Legends* | **DOMESTICATED** | "By 3626 BBY, mudhorns had been domesticated and used as riding animals and pet companions." — *Mudhorn/Legends* |  | UNKNOWN | "hard to domesticate them; only expert handlers were able to do it". Domestication evidence is Legends (SWTOR mount). |
| Strill | `RSW_Strill` | **SOLITARY** | "Strills were territorial creatures, marking the areas they claimed as their own" — *Strill/Legends* | **DOMESTICATED** | "a number of Mandalorians took to keeping strills" — *Strill/Legends* |  | UNKNOWN |  |
| Bogwing | `RSW_Bogwing` | **SOLITARY** | "It was very territorial and used its talons to pick up victims." — *Bogwing/Legends* | **UNCLEAR** |  |  | UNKNOWN | Juveniles flock under successful hunters for scraps. |

## UNCLEAR — 45 for owner arbitration (what canon does say is in the note / domestic columns)

| subject | our defs | social | evidence (social) | domestic | evidence (domestic) | group size | dimorphism | note |
|---|---|---|---|---|---|---|---|---|
| Gizka | `RSW_Gizka` | **UNCLEAR** |  | **NOT** | "All the attempts at domesticating the gizka ended in disaster" — *Gizka/Legends* |  | UNKNOWN | Fast-breeding colony pest ("a temporary colony of gizka"). |
| Dalgo | `RSW_Dalgo` | **UNCLEAR** |  | **DOMESTICATED** | "Onderon rebels used dalgos as beasts of burden and battle mounts" — *Dalgo* |  | UNKNOWN |  |
| Igitz | `RSW_Igitz` | **UNCLEAR** |  | **DOMESTICATED** | "The igitz were a popular pet in most Gungan civilizations." — *Igitz* |  | UNKNOWN |  |
| Puffer pig | `RSW_Pufferpig` | **UNCLEAR** |  | **DOMESTICATED** | "Puffer pigs were raised as livestock for consumption by residents of the planet Batuu." — *Puffer pig* |  | UNKNOWN |  |
| Bolotaur | `RSW_Bolotaur` | **UNCLEAR** |  | **DOMESTICATED** | "Bolotaurs were sometimes tamed and used as mounts." — *Bolotaur* |  | UNKNOWN |  |
| Gelagrub | `RSW_Gelagrub` | **UNCLEAR** |  | **DOMESTICATED** | "They were easily domesticated creatures whose larval forms were used as mounts" — *Gelagrub/Legends* |  | UNKNOWN |  |
| Worrt | `RSW_Worrt` | **UNCLEAR** |  | **DOMESTICATED** | "Worrts could, with great difficulty, be trained as housepets." — *Worrt/Legends* |  | UNKNOWN |  |
| Saw-toothed grank | `RSW_Grank` | **UNCLEAR** |  | **DOMESTICATED** | "imported saw-toothed granks were sold as pets or zoo animals" — *Saw-toothed grank* |  | UNKNOWN |  |
| Jamel | `RSW_Jamel` | **UNCLEAR** |  | **DOMESTICATED** | "Jamels were used as beasts of burden by the Utapau Amani." — *Jamel* |  | UNKNOWN |  |
| Orray | `RSW_Orray` | **UNCLEAR** |  | **DOMESTICATED** | "Many orrays were tamed and domesticated by the Geonosians" — *Orray* |  | UNKNOWN |  |
| Runyip | `RSW_Runyip` | **UNCLEAR** |  | **DOMESTICATED** | "were still commonly used a pack animals on frontier worlds" — *Runyip/Legends* |  | UNKNOWN |  |
| Tee-muss | `RSW_TeeMuss` | **UNCLEAR** |  | **DOMESTICATED** | "Tee-muss were a species of domesticated farm animals" — *Tee-muss/Legends* |  | UNKNOWN |  |
| Gorg | `RSW_Gorg RSW_LongtailGorg RSW_FrilledGorg` | **UNCLEAR** |  | **DOMESTICATED** | "sewers, where harvesters bred them illegally; and gorgmonger farms" — *Gorg/Legends* |  | UNKNOWN | Longtail/Frilled gorg are donor-mod subspecies with no Wookieepedia page of their own - NOT sourced as canon; inherit gorg only if the owner says so. |
| Blarth | `RSW_Blarth` | **UNCLEAR** |  | **DOMESTICATED** | "Amiable and easily tamed, they were kept as a household pet and watch animal by Gungans" — *Blarth/Legends* |  | UNKNOWN |  |
| Can-cell | `RSW_CanCell` | **UNCLEAR** |  | **DOMESTICATED** | "The Wookiees of Kashyyyk considered the appearance of a can-cell a good omen, and often kept them as pets." — *Can-cell/Legends* |  | UNKNOWN |  |
| Dactillion | `RSW_Dactillion` | **UNCLEAR** |  | **DOMESTICATED** | "They were also used as mounts in battle by the Utapaun Security Forces" — *Dactillion* |  | UNKNOWN |  |
| Lava flea | `RSW_LavaFlea` | **UNCLEAR** |  | **DOMESTICATED** | "The creatures were easily domesticated" — *Lava flea/Legends* |  | UNKNOWN |  |
| Blurrg | `RSW_Blurrg` | **UNCLEAR** |  | **DOMESTICATED** | "two-legged reptilian beast of burden found throughout the galaxy" — *Blurrg* |  | UNKNOWN: Males eaten by females after mating (behaviour, not look). | Only "herd" is a Legends game store price ("a herd of 12"). |
| Nuna | `RSW_Nuna` | **UNCLEAR** |  | **DOMESTICATED** | "made them popular livestock animals" — *Nuna* |  | YES-text-only: the male nunas could inflate when agitated (large anterior body cavity). |  |
| Yobshrimp | `RSW_Yobshrimp RSW_YobshrimpJuv RSW_YobshrimpLand` | **UNCLEAR** |  | **DOMESTICATED** | "fishing families cultivated the foreign yobshrimp for consumption" — *Yobshrimp* |  | UNKNOWN |  |
| Boma | `RSW_Boma` | **UNCLEAR** |  | **DOMESTICATED** | "one Mandalorian clan existing that has bred the vicious bomas for centuries in their breeding pens" — *Boma* |  | UNKNOWN | Legends; bred as war beasts. |
| Loth-cat | `RSW_Lothcat` | **UNCLEAR** | "Loth-cats led solitary lives, coming together only to mate and raise kits." — *Loth-cat* | **DOMESTICATED** | "Although it was very difficult, loth-cats could be domesticated" — *Loth-cat* |  | UNKNOWN | Social contradictory: another reference says family groups. |
| Acklay | `RSW_Acklay` | **UNCLEAR** |  | **UNCLEAR** | "also took to breeding them" — *Acklay/Legends* |  | UNKNOWN | Captive-bred arena beasts, not tame. |
| Krayt dragon | `RSW_KraytDragon` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN | Canon and Legends pages silent on grouping; lone-individual stories only. Sanity probe did NOT return SOLITARY. |
| Greater krayt dragon | `RSW_GreaterKraytDragon` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN |  |
| Dragonsnake | `RSW_Dragonsnake` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN: King of the Dragonsnakes "a large individual male" (one individual). |  |
| Sarlacc | `RSW_SarlaccSwimmer` | **UNCLEAR** |  | **UNCLEAR** |  |  | YES-text-only: Females generally grew much larger than males; male attaches to female like an anglerfish (Legends). | Our def is an invented mobile form. Jabba's "pet" is one captive. |
| Sando aqua monster | `RSW_SandoAquaMonster RSW_ElderSando RSW_StormSando` | **UNCLEAR** |  | **UNCLEAR** |  |  | YES-in-canon-art: canon_references/sandoaquamonster legends_1 shows male and female (female has belly pores); text: males over 200 m, females at least 150 m. | Elder/Storm Sando are our invented morphs. |
| Opee sea killer | `RSW_OpeeSeaKiller RSW_OpeeSeaKillerJuv RSW_CrimsonOpee` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN: Male mouth-broods eggs (behaviour). | Crimson Opee is our invented morph. |
| Colo claw fish | `RSW_ColoClawFish RSW_AbyssalColo RSW_ThornbackColo` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN | Abyssal/Thornback are our invented morphs. |
| Laa | `RSW_Laa RSW_LaaJuv` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN | Only an image caption "A group of laas". |
| Dianoga | `RSW_Dianoga` | **UNCLEAR** |  | **UNCLEAR** |  |  | NO: Hermaphroditic; gender is self-identified, not a body difference. | "A family of dianoga inhabited a pool" (one anecdote). |
| Urusai | `RSW_Urusai` | **UNCLEAR** |  | **UNCLEAR** |  |  | YES-text-only: Females had two wings, while males had four (Legends; images show females only). | Nests in sarlacc maws. |
| Fanback | `RSW_Fanback` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN |  |
| Jimvu | `RSW_Jimvu` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN |  |
| K'lor'slug | `RSW_Klorslug` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN |  |
| Shiro | `RSW_Shiro RSW_ShiroTrap` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN | "very popular with Gungan cooks" - eaten, not kept. |
| Whisper bird | `RSW_Whisperbird` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN |  |
| Granite slug | `RSW_GraniteSlug` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN | Deliberately introduced to Coruscant to eat garbage. |
| Borcatu | `RSW_Borcatu` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN |  |
| Blixus | `RSW_Blixus` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN | One pet (D'Nar's). |
| Ollopom | `RSW_Ollopom` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN | One pet in a tank (Dok-Ondar). |
| Skalder | `RSW_Skalder` | **UNCLEAR** |  | **UNCLEAR** | "They were not normally ridden by sentient beings" — *Skalder* |  | UNKNOWN |  |
| Great Devourer | `RSW_GreatDevourer` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN | One named individual. |
| Brain worm | `RSW_BrainWorm` | **UNCLEAR** |  | **UNCLEAR** |  |  | UNKNOWN | Parasite; herd/pack not applicable. |

## Dimorphism, the positive cases

- **Bantha** — YES-in-canon-art: Legends image Bantha_Bull_and_Cow.jpg (viewed): bull has larger double-spiral horns and bigger head; cow a single spiral. Text: "bulls were larger than cows" (canon_references/bantha).
- **Dewback** — YES-text-only: Males display bellies that change to sky-blue when courting (display colouring, not a fixed look).
- **Nerf** — YES-text-only: Male nerfs were generally larger and more aggressive than their female counterparts, with more pronounced horns.
- **Reek** — YES-text-only: The horns of male reeks are usually larger than those of females (also canon_references/iridonianreek).
- **Kybuck** — YES-text-only: Males had short horns sitting atop their head.
- **Varactyl** — YES-text-only: While females sported blue-green plumage and skin, males were mostly dull shades of orange and brown. (Legends image shows Boga, a female only.)
- **Scurrier** — YES-text-only: Horns: those of a male were thick and curved, while those of a female were thin and straight. (Legends image shows a female only.)
- **Anooba** — YES-text-only: males being larger than females (20-45 kg range).
- **Peko-peko** — NO: Both male and female had beautiful indigo-sapphire plumage, and both were the same size.
- **Porg** — YES-text-only: Porgs were sexually dimorphic; males were slightly larger than females and had orange plumage around the eyes.
- **Nuna** — YES-text-only: the male nunas could inflate when agitated (large anterior body cavity).
- **Sarlacc** — YES-text-only: Females generally grew much larger than males; male attaches to female like an anglerfish (Legends).
- **Sando aqua monster** — YES-in-canon-art: canon_references/sandoaquamonster legends_1 shows male and female (female has belly pores); text: males over 200 m, females at least 150 m.
- **Dianoga** — NO: Hermaphroditic; gender is self-identified, not a body difference.
- **Urusai** — YES-text-only: Females had two wings, while males had four (Legends; images show females only).

YES-in-canon-art needs an image that shows BOTH sexes; an image of one sex beside a text claim is YES-text-only. Images were judged from Wookieepedia captions plus `design/RimStarWars/canon_references/*/description.md`; the bantha image was opened and viewed. UNKNOWN means no sex-difference statement was found, not that the sexes look alike.

## Not sourced as canon

- `RSW_LongtailGorg`, `RSW_FrilledGorg`: descriptions present them as gorg subspecies; no Wookieepedia subject exists for either — the only evidence is the donor mod's defName/description. **NOT sourced.**
- `RSW_Basilisk` (six-legged gaze beast) and `RSW_Screecher` (pollution-mutated corvid): Wookieepedia has pages of the same name (a planet; a Legends Kirtania animal) that describe different things — name collisions, not canon matches.
- Our invented morphs folded under a canon parent, inheriting nothing until the owner says so: `RSW_ElderSando`, `RSW_StormSando`, `RSW_CrimsonOpee`, `RSW_AbyssalColo`, `RSW_ThornbackColo`, `RSW_WraidAlpha`, `RSW_SarlaccSwimmer` (mobile form of a sessile canon animal).

## No Wookieepedia subject (116 defs — out of scope; invented creatures go to BIOME_GROUP_SIZE_WALK_1)

`JOE_Landopus`, `JOE_Nautilant`, `RM_Chikka`, `RM_Durrok`, `RM_Mullgoth`, `RM_Vurra`, `RSW_AaroxisDendoria`, `RSW_AaroxisDendoriaLarvae`, `RSW_AaroxisDendoriaPupa`, `RSW_AcidSlug`, `RSW_Baseopsis`, `RSW_Basilisk`, `RSW_BloodletterPetrel`, `RSW_BloodropLarvae`, `RSW_BloodropPupa`, `RSW_BovineBeetleLarvae`, `RSW_BovineBeetlePupa`, `RSW_BunkerBug`, `RSW_CaveLemming`, `RSW_ColonyPustuleHornet`, `RSW_ColonyPustuleHornetQueen`, `RSW_Creature_Mantrap`, `RSW_CrestedDragon`, `RSW_CrystalCrab`, `RSW_Diggerpede`, `RSW_Diplocaulus`, `RSW_Excretor`, `RSW_FacetMoth`, `RSW_FacetMothPupa`, `RSW_FeralGrazer`, `RSW_FleeceSpider`, `RSW_FoundryBeetle`, `RSW_FoundryBeetleLarvae`, `RSW_FoundryBeetlePupa`, `RSW_FungalMantis`, `RSW_FungalWeevil`, `RSW_GastroToad`, `RSW_Glowtail`, `RSW_Holcorobeus`, `RSW_Ikee`, `RSW_JewelBeetle`, `RSW_JewelBeetleLarvae`, `RSW_JewelBeetlePupa`, `RSW_Karrask`, `RSW_Khorrak`, `RSW_Korrum`, `RSW_Lanternwhale`, `RSW_Maguana`, `RSW_Maligoat`, `RSW_Maxolotl`, `RSW_Megakrill`, `RSW_Megaphorid`, `RSW_MegaphoridLarva`, `RSW_Moornak`, `RSW_MossBeetle`, `RSW_MossBeetlePupa`, `RSW_MutagenicNorphea`, `RSW_MutatingTumorfishAdult`, `RSW_MutatingTumorfishFry`, `RSW_MutatingTumorfishSpawn`, `RSW_Onnik`, `RSW_Platyhystrix`, `RSW_PodWorm`, `RSW_Polluwog`, `RSW_Protosolpuga`, `RSW_Protovermes`, `RSW_PustuleHornet`, `RSW_PustuleHornetQueen`, `RSW_PustuleHornetSpawned`, `RSW_Reefback`, `RSW_RoyalRhino`, `RSW_RoyalRhinoLarvae`, `RSW_RoyalRhinoPupa`, `RSW_RustNipper`, `RSW_RustNipperJuv`, `RSW_Sacapillar`, `RSW_SandLeaper`, `RSW_SandLion`, `RSW_SandPillar`, `RSW_SandStalker`, `RSW_Scavrat`, `RSW_ScrapNestBird`, `RSW_Screecher`, `RSW_Segnosaurus`, `RSW_ShadeWhale`, `RSW_ShaleGorger`, `RSW_ShrublandGiant`, `RSW_SiltLamprey`, `RSW_SiltLampreyJuv`, `RSW_SmogMoth`, `RSW_SmogMothLarvae`, `RSW_SmogPupa`, `RSW_Starmaw`, `RSW_TelluroxRace`, `RSW_Termitotron`, `RSW_Thrumbungus`, `RSW_TunnelSnake`, `RSW_VentStalker`, `RSW_Vozzik`, `RSW_WarWyrm`, `RSW_Yooka`, `RSW_Zakkro`, `RSW_Zhakka`, `RUT_BrineBattery`, `RUT_BurnerAscendant`, `RUT_CathedralRoach`, `RUT_EmperorVulture`, `RUT_FleetFlier`, `RUT_GreentideAntRace`, `RUT_Placeholder_GreentideGnawerRace`, `RUT_Radiothermal`, `RUT_ScarRoach`, `RUT_SealedSleeper`, `RUT_VWake`, `RUT_Vhessk`, `VAEWaste_Megatardi`

A search miss is not proof of non-canon; these got a name search (CamelCase split, life-stage suffix stripped) and the top 8 hits were read.
