# Star Wars Naming Layer for the VGE 1.6 Bestiary — v1

_Companion to `desert_world_design.md`, `faction_roster_v2.md`. Created 2026-08-06 (originally `VGE_1_6_Alien_World_Bestiary.md`, renamed to `Alien_Bestiary.md` as scope broadened toward all creature mods). The left-column names in §3 are the literal VGE ThingDef in-game labels._

**Scope decision:** this file names **all 104** VGE creatures plus the four special outputs. Nothing is left as an Earth portmanteau, because a half-renamed bestiary is worse than an unrenamed one — one stray "bearchicken" in a spawn log breaks the whole illusion.

**Every entry gets two names:** a **vernacular** name (what Jawas, homesteaders and Tuskens call it — this is the one that appears in-game) and a **registry/faction** name (what the Consortium, Imperial Directorate or Foundry Hive calls the same organism). The second name is not decoration: it is how a C- or D-grade creature earns its place in the world. A "bearman" is nonsense as wildlife; **Consortium Model UR-7 "Vhek," an abandoned labour-line prototype**, is exactly the kind of thing your Gene Consortium leaves lying around.

---

## 1. The naming system (so you can coin more without me)

Star Wars creature names are short, consonant-heavy, and almost never descriptive in Basic. They sound like a word borrowed from a local language and worn smooth by traders. Four rules reproduce that:

1. **One or two syllables, hard stop at the end.** krayt, bantha, nexu, reek, acklay, ronto, worrt, massiff. Avoid English compounds ("sandstalker") except as *nicknames* — those read as spacer slang, which is a different register and useful for contrast.
2. **Doubled consonants and terminal -k / -ak / -ik / -rr.** This is the single biggest tell. `karrak`, `sissik`, `grondar`, `vhaggan`.
3. **Apostrophes are rare and load-bearing.** Reserve them for Sith/ancient things (`tuk'ata`, `kor'dak`). If everything has one, none of them mean anything.
4. **Don't describe the mechanic in the name.** No "venomhound," no "fuelbeast." The name is opaque; the *nickname* carries the warning ("they call it a venom-mount because that's what it does to you").

**Clade roots — shared morphemes make the ecosystem read as evolved rather than assembled.** This is the part that does real work: a player who meets a `grondar` in a cavern and later meets a `grondrak` under the dunes immediately understands they're related, without a codex entry.

| Root / ending | Clade | Reads as |
|---|---|---|
| `-ak`, `-rak`, `-dar` | ursine heavies | big, slow, dangerous |
| `-ik`, `-ek`, `-ka` | small quick things | vermin, prey, camp animals |
| `-bantha`, `-ba` | muffalo line | domesticable, herd, wool/milk |
| `ss-`, `-ssh`, `-zh` | reptiles | venom, heat tolerance, sibilant |
| `karr-`, `-rrik` | insectoid / Foundry | chitin, hive-made, sterile |
| `-kir`, `-bak`, `-ak` (mounts) | equines | ridden, nomad, migratory |
| `dh-`, `vh-`, `kr-` (initial) | apex predators | the ones with names people whisper |

**The elder-form rule (my strongest structural suggestion).** Every Colossal-dominant creature is named as the **grown or ancient form of a lesser species in the same clade**, not as a separate animal:

- `skarn` (bearcat) → **`skarnath`** (thrumbocat)
- `karrak` (bearscarab) → **`karrakoth`** (thrumbospider)
- `grondar` (bearmole) → **`grondrak`** (thrumborat)
- `dhak` (wolfbear) → **`dhakmaw`** (thrumwolf)
- `obbak` (muffalohorse) → **`obbakar`** (thrumhorse)

This solves the source doc's hardest problem — colossals are "encounter-scale, not population fauna" — *diegetically*. They aren't a separate boss species that inexplicably has no population; they're what happens to one of these animals if nothing kills it for eighty years. Homesteaders will tell you every skarn is a skarnath that got unlucky. That also gives you a free quest hook: killing the local elder form is a service the Homestead Compact will pay for.

---

## 2. Faction ownership of the "unnatural" grades

The source doc treats C and D as exclusion categories. In this setting they're **faction signatures** — which is exactly what you asked for. Four registries, each mapped to a faction already in `faction_roster_v2.md`:

| Registry | Owner | Naming pattern | Covers |
|---|---|---|---|
| **Labour-line** | Arkanian–Kaminoan Gene Consortium | `Model XX-N "Rolename"` | Every humanoid-dominant hybrid. The Consortium's *Ascendant Genome* doctrine already builds a "labour-line"; these are its discarded iterations. They talk because they were **designed to take instruction**, which is a Kaminoan design decision, not a joke. |
| **Purge catalog** | Imperial Desert Directorate | `XX-N "Codename"` + field nickname | Every mechanoid-dominant hybrid. Directorate doctrine is droid-averse per the roster — so these are filed as *ordnance*, never as droids. That prejudice is itself the flavor. |
| **Foundry caste** | Geonosian Foundry Hive | caste-noun (`unmaker`, `silk`, `hauler`) | Insectoid-dominant hybrids. Sterility is not a defect here; it's caste discipline. Every one you meet was *made*, which the Hive considers the only respectable way to exist. |
| **Alchemical / relic** | Sith remnant, Rakatan ruin, Anomaly | `tuk'ata`-style names, apostrophes allowed | Colossal apexes with no ecological story, plus the archotech line. |

**Rule of thumb for placement:** a creature keeps its vernacular name in the wild and its registry name on a datapad you loot. If the player finds a manifest listing "Model HK-0 'Provision' — 40 units" in a Consortium ruin and later meets one wandering the salt flats, that's the setting doing its own storytelling.

---

## 3. The bestiary

Terrain codes match `desert_world_design.md` §3E: DD deep desert · AR arid shrubland · FC forsaken crags · SF salt flat · OA oasis · RV river · VO volcanic · TP tar pits · CO coast · FJ feralisk jungle · MJ mycotic jungle · GF glowforest · OC ocular forest · WA wasteland/android · SH shipyards.

### 3.1 Ursine-dominant — the heavies

| VGE | Vernacular | Registry / alt | Terrain | Hook |
|---|---|---|---|---|
| Bearalope | **cinderak** | *"walking mine"* (Cartel) | TP, VO | Tibanna bladders under the shoulder hump. Tuskens won't hunt them; the Cartel pays for the intact sacs. |
| Bearchicken | **kor'dak** | *dune-owl* | DD, FC | Broad membranous wing-cases let it cross soft sand no other heavy can. Nests in wreck hulls. |
| Bearffalo | **ghorn** | *high bantha* | DD, AR, SF | The bantha's larger cousin. Jawa clans measure wealth in ghorn. Wool, milk, and it will kill a raider. |
| Bearwolf | **kraddak** | *the long hunger* | AR, FC | Apex pursuit predator. Homesteads bell their livestock for it. One per region, never more. |
| Bearmole | **grondar** | *deep-digger* | GF, FC, WA | Feels no pain, which is why it walks off things that should stop it. Cavern megafauna; elder form `grondrak`. |
| Bearcat | **skarn** | *hide-beast* | FC, AR | Prized pelt — a skarn hide is a legitimate trade good. Elder form `skarnath`. |
| Bearman | *"the porter"* | **Consortium Model UR-7 "Vhek"** | WA, ruins | Built to carry and converse; goes feral politely. Found alone near abandoned Consortium outstations, still trying to be useful. |

### 3.2 Avian-dominant — prey, vermin and the fowl trade

| VGE | Vernacular | Registry / alt | Terrain | Hook |
|---|---|---|---|---|
| Chickenbear | **shessa-fowl** | *smokedown* (Cartel product) | Cartel oases | Cured down burns sweet. A Hutt product animal, penned, never wild. |
| Chickenlope | **grennik** | *poppers* | Cartel/Foundry pens | Lays gas-eggs. Nobody keeps them near anything flammable twice. |
| Chickenffalo | **kiba-fowl** | *homestead kiba* | AR, OA | The Compact's all-purpose smallholding bird. Unglamorous, everywhere, four products. |
| Chickenwolf | **vekt** | *the flock* | AR, DD, RV | Runs down anything wounded. Invasive along the river corridor — they follow traffic. |
| Chickenrabbit | **gorrel** | *the plague of small mouths* | AR, OA, RV | Womp-rat-tier vermin with a womp-rat-tier reputation. Population control is a standing Compact quest. |
| Chickencat | **pikka** | *camp pikka* | everywhere settled | The animal that's just *around*. Kills gorrels, tolerates people, follows caravans. Your ambient life-signal. |
| Turkeyman | *"switchbird"* | **Consortium Model AV-3 "Steward"** | WA, ruins | Operates switches. Found in dead facilities, still cycling the lights of an empty room. |

### 3.3 Boomalope-dominant — the tibanna line

Reframe the whole clade as **gas-bladder fauna**: they metabolize volatiles and store them. That single move takes the family from "refinery joke" to "the reason this planet has a fuel economy."

| VGE | Vernacular | Registry / alt | Terrain | Hook |
|---|---|---|---|---|
| Boomabear | **tibbak** | *bladderback* | TP, VO | Walks the tar margins eating what it shouldn't. Cartel tappers follow herds and milk them. |
| Boomachicken | **k'krri** | *fragfowl* | Foundry pens | Foundry ordnance stock. Lays a shell or an egg and doesn't distinguish. |
| Boomffalo | **vaporjerba** | *gas-jerba* | Cartel ranches | Milk is mildly intoxicating and sells better than the wool. Very Hutt. |
| Boomwolf | **chilvek** | *frostspit* | GF, OC, SF nights | Vents supercooled gas. Reads as a genuine evolved adaptation to lethal daytime heat — it *cools itself* and weaponizes the exhaust. Best B-grade in the set. |
| Boomsquirrel | **sizzik** | *sparkmite* | TP, WA | Detonates a light-flash to escape. Swarms are how the tar pits stay dangerous. |
| Boomcat | **murrik** | *gland-cat* | Cartel compounds | Kept for the gland. Escaped ones are a fire risk and everyone knows it. |
| Booman | *"the tapper"* | **Consortium Model BX-2 "Tapper"** | WA, VO ruins | Refuels machinery it no longer has orders about. Found servicing generators that stopped mattering decades ago. |

### 3.4 Canine-dominant — pursuit

| VGE | Vernacular | Registry / alt | Terrain | Hook |
|---|---|---|---|---|
| Wolfbear | **dhak** | *the taker* | FC, DD | Strikes high. Tusken clans count dhak scars as status. Elder form `dhakmaw`. |
| Wolfalope | **kessik** | *emberhound* | VO, TP | Spits burning bladder-gas. The volcanic tile's mobile threat — pairs with the eruption timer. |
| Wolfchicken | **tikkra** | *frenzy-runner* | AR, RV | Herbivore built like a predator. Unsettling and entirely plausible. |
| Wolffalo | **vhaggan** | *nightgrazer* | DD, SF | Grazes the cold desert night, shelters by day. Coat is genuinely valuable. Caravan stock. |
| Wolfbeaver | **chirrik** | *grovegnaw* | FJ, MJ, RV | Eats standing timber. The reason the river valley's tree line moves. Compact hates them. |
| Wolfcat | **nazhk** | *twinfang* | AR, FC | Strikes twice in the time anything else strikes once. The good hunting companion. |
| Dogman | *"the smiling hound"* | **Consortium Model CN-4 "Culler"** | WA, ruins | Was built to cull stock. Still culls stock. Do not put it in a pen with your animals. |

### 3.5 Feline-dominant — ambush and companion

| VGE | Vernacular | Registry / alt | Terrain | Hook |
|---|---|---|---|---|
| Catbear | **morrik** | *bone-digger* | FC, WA, ruins | Digs up what's buried. Follows battles. Grim and completely believable. |
| Catalope | **ashka** | *cinderling* | VO, TP | Small, evasive, sets things alight. Foundry uses them for pest clearance. |
| Catchicken | **vissik** | *eye-taker* | FJ, FC | Goes for the eyes. Nobody in this world thinks that's unusual; they just wear visors. |
| Catffalo | **jaddal** | *browser* | AR, RV, OA | Finds forage nothing else can. Caravans keep two or three and eat better for it. |
| Catrabbit | **sookal** | *balm-cat* | **OA (Chromatic Oasis)** | Pheromonal calm — reclassify to A-grade and make it *the* signature oasis animal. The oasis feels safe partly because the sookal are making you feel that way. Quietly sinister; leave it unexplained. |
| Catwolf | **veska** | *hearth-veska* | settled, all | Fast, trainable, leaves no mess. The best domestic animal on the planet and everyone wants one. |
| Catman | *"the attendant"* | **Consortium Model FL-6 "Attendant"** | WA, ruins | Feeds the incapacitated. Found in medical wings beside long-dead patients. |

### 3.6 Muffalo-dominant — the bantha-kin

Your caravan spine. Name them all as bantha relatives so the Jawa fiction holds.

| VGE | Vernacular | Registry / alt | Terrain | Hook |
|---|---|---|---|---|
| Muffalobear | **vorrbantha** | *irontusk* | DD, SF | Carries a third more than a bantha and defends the line. Premium caravan stock. |
| Muffalope | **tibbantha** | *gas-bantha* | Cartel ranches | Leaks. Caravans that use them do so because the Cartel gave them no choice. |
| Muffalochicken | **korrbal** | *last-stander* | Compact holdings | Fights harder as it's dying. Homesteads breed them as herd defenders and speak of them fondly. |
| Muffalowolf | **drovak** | *herd-guard* | AR, DD | Fights better in numbers. A drovak string is a genuine deterrent — this is your top-tier native herd animal. |
| Muffalocat | **soffa** | *shed-bantha* | AR, OA | Sheds usable fiber without shearing. Low-effort, high-value, beloved. |
| Muffalorat | **grezz** | *scrub-bantha* | DD, WA | Small, cheap, breeds fast. What poor clans move cargo with. Prone to becoming a problem. |
| Muffaloman | *"the porter-clean"* | **Consortium Model MF-8 "Porter"** | WA | Hauls and sanitizes. The Consortium's most successful failure. |

### 3.7 Rodent-dominant — vermin, burrowers, plague

| VGE | Vernacular | Registry / alt | Terrain | Hook |
|---|---|---|---|---|
| Molebear | **durrag** | *oreseeker* | VO, FC, GF | Surfaces with metal in its claws. Prospectors follow durrag sign. Ties directly to your terrain-treasure layer. |
| Squirralope | **fizzik** | *tib-gnat* | TP, ranches | Tiny volatile pest. Infestations in fuel stores are a running disaster. |
| Rabbitchicken | **skitt** | *needleteeth* | WA, anomaly | Occasionally kills something enormously larger than itself. Nobody can explain it. Keep it rare and unexplained. |
| Ratffalo | **rothrik** | *plague-bantha* | WA, MJ | Disease reservoir. The reason quarantine exists. Forbidden as caravan stock by every faction that has learned. |
| Beaverwolf | **brakka** | *resin-gnaw* | FJ, MJ, RV | Yields harvestable resin. Manageable, farmable, useful — the domesticable counterpart to the chirrik. |
| Rabbitcat | **sivvik** | *knitflesh* | OA, FJ | Closes its own wounds. Invasive where predators are scarce; the oasis has a sivvik problem. |
| Moleman | *"the digger"* | **Consortium Model RD-5 "Delver"** | WA, VO ruins | Obeys mining orders. Jawas find these and argue about whether taking one is salvage or slavery. **Good ethics hook for your player faction.** |

### 3.8 Reptile-dominant — the desert's own clade

The strongest family for this world. Anchor it to canonical desert reptiles (dewback, massiff, krayt) so it feels native to Tatooine-analog ground.

| VGE | Vernacular | Registry / alt | Terrain | Hook |
|---|---|---|---|---|
| Bearodile | **kraddon** | *lesser krayt* | DD, FC | Venom plus stunning mass. The apex the Tuskens actually fear, and the one most often mistaken for a juvenile krayt. |
| Boomsnake | **sslarn** | *spitter* | SF, TP | Ruptures toxin sacs at range. Salt flats have no cover and an sslarn knows it. |
| Chickenlizard | **sissik** | *scurrier-kin* | DD, AR, SF | Fast-breeding spitter. Your ubiquitous small desert reptile — the one in every landing's first ten minutes. |
| Muffalokomodo | **kollback** | *fanged dewback* | DD, AR | Venomous pack reptile. Milked for coagulant; a kollback string will deter a raid by existing. |
| Spidersnake | **zhakk** | *chitin-serpent* | FC, GF | Armored, venomous, and the Consortium's preferred venom-enzyme source. Untameable, which is why they pay so well for the flasks. |
| Wolfsnake | **vasshk** | *sand-runner* | DD, AR | Sheds valuable scale-plate seasonally — a *renewable found resource* rather than a hunted one. Fearless to the point of suicide. |
| Snakecat | **nirrik** | *scale-cat* | FC, OA | Furred and venomous. Exotic companion; Cartel bosses keep them to signal that they can. |
| Lizardman | *"the culler"* | **hssiss-kin thrall** (Sith/cult) | Sith ruins, cult sites | Reframed as Sith-alchemy stock rather than a lab animal: it was *made* to execute, and it grows stronger for it. Belongs to a dark-side site, not a biosphere. |

### 3.9 Insectoid-dominant — Foundry castes

Sterility is the story. Every one of these was made by the Geonosian Foundry Hive, which is why none of them breed and why they're all *good at exactly one thing*.

| VGE | Vernacular | Registry / alt | Terrain | Hook |
|---|---|---|---|---|
| Bearscarab | **karrak** | *war caste* | Foundry, FC, WA | Armored, calm, trainable. The best domesticable heavy in the game and the Hive's signature export. Elder form `karrakoth`. |
| Boombeetle | **azzik** | *bombardier caste* | TP, VO, Foundry | Fires acid sacs. Bombardier-beetle logic is real biology — this one needs no excuse at all. |
| Chickenspider | **thessik** | *silk caste* | Foundry, FJ | Spins caste-silk and lays sterile product-eggs. Foundry husbandry, escaped populations in the jungle. |
| Muffalopede | **grallik** | *hauler caste* | Foundry, GF | Hive mast and shearable chitin. The Hive's freight animal. |
| Wolfscarab | **skirrak** | *runner caste* | DD, Foundry | Extremely fast armored pursuit. Original lore is slave-hunting — **keep that**, and give it to the Hive and the Directorate both. |
| Spidercat | **nettik** | *binder caste* | FJ, Foundry | Spits adhesive silk to blind and hold. Not a hairball — a capture caste. |
| Manscarab | *"the unmaker"* | **Foundry unmaker caste** | Foundry, SH | Deconstructs structures on command. Perfectly coherent for a hive that builds things: something has to take the scaffolding down. **Promote this one out of C-grade** — it's the least ridiculous humanoid hybrid in the set once the Hive owns it. |

### 3.10 Equine-dominant — mounts and the nomad economy

Your Tusken/Jawa mobility layer. Anchor names to canon riding beasts (dewback, luggabeast, blurrg, fathier).

| VGE | Vernacular | Registry / alt | Terrain | Hook |
|---|---|---|---|---|
| Bearhorse | **thorrak** | *luggabeast-kin* | DD, SF | Heavy, omnivorous, sleeps little. The freight mount. |
| Boomhorse | **haskir** | *tapper-steed* | Cartel routes | Produces more gas the further it walks. Cartel long-haul stock; caravans park them downwind. |
| Chickenhorse | **sirrak** | *fathier-kin* | AR, RV | Breeds on the move. Nomad clans time foaling to migration — a genuinely elegant bit of ecology. |
| Cathorse | **vokkir** | *pounce-mount* | Bounty Compact, FC | Carnivorous cavalry that leaps. Bounty Hunters' Compact signature mount — expensive, fed on meat, unmistakable on approach. |
| Molehorse | **dunnik** | *cave-runner* | GF, OC, WA | Small tunnel mount with low upkeep. What the droid enclaves and cavern settlements ride. |
| Wolfhorse | **verrak** | *steppe-hunter* | AR, DD | Fast predatory mount. Straightforward and excellent — Tusken raiding stock. |
| Muffalohorse | **obbak** | *the herd-beast* | DD, AR, SF | Forages while migrating; produces only while moving. **The single most thematically perfect animal in the mod for a nomad culture** — it is literally only productive if you keep travelling. Give this to the Tuskens and make it sacred. Elder form `obbakar`. |
| Crocorse | **sarnak** | *venom-mount* | DD, VO | Toxic breath, extreme heat tolerance, ridable. Deep-desert cavalry; dangerous to friendlies, which is a feature. |
| Spiderhorse | **chakrir** | *hive cavalry* | Foundry, SH | Armored web-throwing mount. Sterile, so every one you see was issued. Geonosian aristocrat mount. |
| Hurseman | *"the outrider"* | **Consortium Model EQ-9 "Outrider"** | WA, routes | Talks to you for the whole journey. Consortium courier stock; found wandering old trade lines. |

### 3.11 Colossal-dominant — elder forms and apexes

One per region, maximum. Each is the grown form of something smaller, except the krayt — which is its own thing, because it should be.

| VGE | Vernacular | Registry / alt | Terrain | Hook |
|---|---|---|---|---|
| Thrumbear | **rannok** | *rancor-kin* | FC, GF | Elder-form heavy. Cartel arenas want one alive; nobody has managed it twice. |
| Thrumbalope | **vaskarr** | *the tibanna colossus* | TP, VO | A walking fuel reservoir with a catastrophic failure mode. One exists. Killing it changes the map. |
| Thrumbochicken | **kessorak** | *the tyrant-ruping* | FC, DD | Fast apex, rideable if you're insane. Whoever rides one is a named NPC by definition. |
| Thrumffalo | **dunemother** | *vhorbantha* | DD, SF | A living terrain feature. Jawa clans navigate by where the dunemother is grazing. **Non-hostile apex** — the encounter is logistical, not martial. |
| Thrumwolf | **dhakmaw** | *elder dhak* | AR, FC | Hunts several times a day and empties a region. Its arrival is a migration event for everything else. |
| Thrumbocat | **skarnath** | *elder skarn* | FC, GF | Suffocation kills. Silent, agile, and the reason cavern settlements post watches. |
| Thrumbospider | **karrakoth** | *the Foundry colossus* | SH, Foundry ruins | Near-unkillable siege caste. Vulnerable to fire — the one usable answer, and worth telegraphing. |
| Thrumbolizard | **krayt dragon** | *greater krayt* | DD, FC | Use the canonical name. This is the mod's dragon and Tatooine's dragon and they are the same animal. Pearl in the gut, obviously. |
| Thrumborat | **grondrak** | *elder grondar* | GF, DD | Burrows and surfaces. Temporarily near-immune underground — you cannot chase it, only survive it. |
| Thrumhorse | **obbakar** | *the Windrunner* | DD, SF | Legendary mount, one per faction at most. Tusken clans that hold one hold territory. |
| Thrumboman | *"the Gardener"* | **Consortium Ascendant Model I "Cultivator"** | WA, OA ruins | The Consortium's masterwork: a colossal, conversant thing that tends plants. Still tending them. Mythic rather than comedic if you never explain it. |

### 3.12 Humanoid-dominant — the Consortium labour-line

None of these are wildlife. All of them are **Model numbers on a manifest** and set dressing for the Consortium's *Ascendant Genome* doctrine. Quarantine to WA/ruins/Consortium sites.

| VGE | Field name | Registry | Hook |
|---|---|---|---|
| Manbear | *"the advocate"* | **Model HB-1 "Advocate"** | Talks prisoners into cooperating. Was built for exactly that and is very good at it. |
| Manalope | *"the sapper"* | **Model HL-4 "Sapper"** | Hovers; places charges on a schedule nobody remembers setting. Wasteland approaches are mined by something patient. |
| Manchicken | *"provision"* | **Model HK-0 "Provision"** | Bred to be eaten and content about it. The single darkest thing in your setting — use it **once**, in one Kaminoan facility, and never explain it further. |
| Manffalo | *"the drover"* | **Model HM-7 "Drover"** | Carries more the longer it has served. A loyalty metric expressed as anatomy. |
| Manwolf | *"the tracker"* | **Model HW-2 "Tracker"** | Intelligent, hardy, regenerative. The prototype the Consortium was proudest of; sold to the Bounty Compact. |
| Mancat | *"the companion"* | **Model HC-3 "Companion"** | Built for company. Consortium executives keep them. Deeply unsettling in a way nobody local remarks upon. |
| Mansquirrel | *"the sweeper"* | **Model HS-5 "Sweeper"** | Works at night, clears ground. Harmless. Somehow the saddest one. |

### 3.13 Mechanoid-dominant — the Imperial Purge catalog

Filed as **ordnance**, never as droids, per Directorate doctrine. Field nicknames come from the troops who have to work alongside them.

| VGE | Field name | Imperial designation | Hook |
|---|---|---|---|
| Mechabear | *plasmaback* | **PX-4 "Bulwark"** | Mobile heavy weapon. Assigned to garrison commanders who have annoyed someone. |
| Mechalope | *ashmaker* | **IN-6 "Censer"** | Burns ground. Named for what the Directorate does to noncompliant settlements. |
| Mecha-chicken | *needlebird* | **SR-2 "Quill"** | Recon sniper. Lays electro-eggs as remote sensors — reframe them as *seeded telemetry*, which is genuinely clever. |
| Mechaspider | *the spindle* | **AS-8 "Loomrig"** | Sustained laser fire. The thing that ends a breach attempt. |
| Mecha-muffalo | *smokebeast* | **LG-3 "Draywork"** | Freight plus smoke screen. Directorate convoys are built around these — **and your design doc says convoys are the Empire's attack surface.** This is what you're ambushing. |
| Mecha-rat | *stunmite* | **SW-1 "Tick"** | Disposable swarm. Deployed by the hundred and accounted for by the crate. |
| Mechaturtle | *spitshell* | **BK-7 "Redoubt"** | Static poison turret. Guards the things the Directorate can't afford to move. |
| Mechawolf | *frostrunner* | **CR-5 "Hoarfrost"** | Cryogenic hunter-killer. Used for capture operations — freeze, don't kill. |
| Mechathrumbo | *the siege-beast* | **AG-0 "Doomtoll"** | Mobile antigrain artillery. Strategic asset; its deployment is an Act-III beat, not an encounter. |
| Mechacat | *tailblade* | **BL-9 "Scyther"** | Throws and regrows a blade. Skirmisher; Sith escorts favor them. |
| Mecha-horse | *ventsteed* | **CV-6 "Emberrider"** | Fast mount that scorches what it passes. Directorate outrider cavalry. |
| Mecha-mime | *the Quiet One* | **XN-0 "Silence"** | **Not Imperial-made** — recovered, catalogued, and not understood. Its cannon ignores armor because it ignores *space*. Loses control fast and destroys whatever it was guarding. Perfect Anomaly-tier containment set-piece for the Shipyards or a Rakatan ruin. Never fauna, never twice. |

### 3.14 Special outputs

| Source | Name | Hook |
|---|---|---|
| Fleshling | **caulling** | Consortium term: *non-viable*. Friendly, helpless, dies without care. Finding a live one in an abandoned lab is a moral problem with no clean answer. |
| Aberrant fleshbeast | **shudderflesh** | Gene-spill. Bleeds continuously, fights only when struck. Anomaly and Consortium-failure sites only. |
| Paragons | **crown-forms** | Per-clade perfect specimens. Name each as the clade root plus `-ath`/`-oth`/`-ar` (the elder-form pattern). One named individual each; faction prizes, relic hunts, Cartel arena stock. |
| Archotech centipede | **the Infinite** | Rakatan war-form, sleeping under the Shipyards. Ties your §3E "the mechanoids are building something gravship-shaped" reveal to something far older than the Empire. Boss encounter, once, at the end. |

---

## 4. Suggested clade-to-terrain allocation

Your source doc's advice — 3–5 coherent clades per region, not a zoo — applied:

| Terrain | Resident clades | Signature animal |
|---|---|---|
| **Deep desert (DD)** | reptile, equine, bantha-kin | `kraddon`, `obbak`, `krayt dragon` |
| **Arid shrubland (AR)** | avian, canine, bantha-kin | `vekt`, `drovak`, `gorrel` |
| **Forsaken crags (FC)** | ursine, feline, reptile | `skarn`, `dhak`, `nirrik` |
| **Salt flat (SF)** | reptile, bantha-kin (transient) | `sslarn`, `vhaggan` |
| **Oasis (OA)** | feline, rodent, avian | `sookal`, `sivvik`, `pikka` |
| **River (RV)** | canine, rodent, avian | `chirrik`, `brakka`, `vekt` |
| **Volcanic (VO)** | gas-bladder, rodent, reptile | `kessik`, `durrag`, `sarnak` |
| **Tar pits (TP)** | gas-bladder, insectoid | `tibbak`, `azzik`, `sizzik` |
| **Coast (CO)** | (Alpha Biomes native fauna — leave to the mod) | — |
| **Feralisk / Mycotic jungle (FJ/MJ)** | insectoid, canine, rodent | `nettik`, `chirrik`, `rothrik` |
| **Glowforest / Ocular (GF/OC)** | ursine burrowers, gas-bladder cryo, insectoid | `grondar`, `chilvek`, `grallik` |
| **Wasteland (WA)** | *no wild clade* — labour-line remnants only | `Model` designations |
| **Shipyards (SH)** | *no wild clade* — Foundry castes and Purge catalog | `karrakoth`, `chakrir` |

Two terrains deliberately have **no native fauna**: the wasteland and the shipyards. Everything alive there was manufactured. That absence is louder than any creature you could put in it.

---

## 5. Open choices for you

1. **Krayt naming.** I've reserved `krayt dragon` for the thrumbolizard and used `kraddon`/*lesser krayt* for the bearodile. If you'd rather the krayt name stay unique, `kraddon` stands alone fine and I'd rename the thrumbolizard `vhorkrayt`.
2. **The Manchicken.** I've written it as the setting's darkest single artifact. It is entirely reasonable to cut it instead — it is the one entry where "place it in proper context" may not be worth doing.
3. **Sookal (catrabbit).** I promoted it from C to the Chromatic Oasis signature. That depends on whether you want the oasis to feel *actively* seductive rather than just wet. My lean is strongly yes — it makes the oasis's raid-magnet threat axis feel earned.
4. **Moleman / Delver.** Jawas encountering a semi-sapient mining animal built by a slaver-adjacent faction is a good, cheap ethical hook for the player faction. Worth a quest if you're authoring any.
