# The world we want — faction specification

_VISION, 2026-08-13. **This states the desired end state only.** No instructions,
no UI steps, no "how to get there". Everything here is a claim about what should
be true of the finished world; how to make each line true is a separate problem
for whoever configures the mods._

**Owner's two governing rulings, this session:**

> **"We keep and reskin/rename factions only when they are wired into specific game events or
> functions we can't change. Otherwise we author from scratch. We want total
> control, no inheriting strange stuff."**

> **"It should be a BIG world but the settlements are quite sparse. Interesting
> tiles should be clustered together in intriguing patterns: sometimes around
> existing settlements, sometimes showing where failed settlements died. We are
> going to author that world ourselves as much as possible."**

---

## 1. What is true, and what is not

🔴 **Canon names and leaders were set by the owner, 2026-08-13.** This section was
rewritten against them, and the shape of the whole design changed with it.

| | |
|---|---|
| ✅ **Fourteen NPC factions exist**, plus the player's Jawa expedition | two more than before — the machines and the hive are now named factions, not anonymous survivors |
| 🔴 **SEVEN of them are reskins of VANILLA factions**, not authored from scratch | Empire · Outlanders · Tribes · Pirates · Ancients · Mechanoids · Insects |
| ✅ **Seven are authored by us** | Hutt Cartel · Free Droid Enclaves · Wildsteam Clan · Deepwater Compact · Geonosian Foundry Hive · Jawa Trade Moot · the Junkers |
| ✅ **Every faction has a NAMED LEADER** | the world has people in it, not offices |
| ✅ **The world is BIG and sparse** — ~72 settlements across a large planet | |
| ✅ **Interesting tiles cluster** — around living settlements, and around dead ones | |
| ✅ **One permanent enemy: the Galactic Empire** | led by Palpatine |
| ✅ **Water increases with latitude** | the equator kills; the poles hold the standing water |
| ❌ **No mod faction is kept "because it is Star Wars"** | flavour is not a dependency |
| ❌ **No faction generates Jawa except the Trade Moot** | the player race is not a common sight |
| ❌ **The world is not auto-generated and accepted** | generate a seed, then author on top of it |
| ❌ **Nobody except the Empire is permanently un-negotiable** | the mid-game always has a wedge |

⭐ **What the canon list changed, and it is not cosmetic.** Reskinning vanilla's
outlanders, tribes and pirates instead of suppressing them **closes §8's open
call** and removes the project's largest unmeasured risk in one stroke: we no
longer have to find out what breaks when vanilla's economic spine is deleted,
because it is not deleted — **it is wearing our names.**

---

## 2. The fourteen factions

| # | Faction | Leader | rides on | Settlements | Goodwill | Perm. enemy |
|---|---|---|---|---:|---:|---|
| 1 | **Hutt Cartel** | **Gorga the Immense** *(Hutt)* | authored | 8 | −35 | No |
| 2 | ⭐ **The Galactic Empire** | 🔴 **Emperor Palpatine** | **vanilla `Empire`** | **3 surface** *(+~7 orbital)* | −100 | 🔴 **Yes** |
| 3 | **Homestead Defense League** | **Taren Voss** *(Human)* | **vanilla Outlanders**, beefed up | 13 | +25 | No |
| 4 | **Deep Desert Tribes** | **Torr'gan** *(Tusken)* | **vanilla Tribes**, beefed up | 9 | −80 | No |
| 5 | **Free Droid Enclaves** | **R-41 Rell** | authored | 3 | 0 | No |
| 6 | **Wildsteam Clan** | **Rroowaak** *(Wookiee)* | authored | 4 | +35 | No |
| 7 | **Deepwater Compact** | **Neris Cal** *(Mon Calamari)* | authored | 5 | +10 | No |
| 8 | **Geonosian Foundry Hive** | **Korrik the Shaper** *(Geonosian)* | authored | 5 | −100 | No |
| 9 | **Ascendant Helix** | **Director Ko Saiyan** *(Kaminoan)* | **vanilla `Ancients`** *if possible* | 3 | 0 | No |
| 10 | **Blackstar Company** | **Jaxen Marr** *(Mandalorian)* | **vanilla Pirates**, beefed up | 4 | −10 | No |
| 11 | **Jawa Trade Moot** | **Kiknik the Wealthy** *("leads")* | authored | 7 | **+40, capped +74** | No |
| 12 | **the Junkers** | **Tarn Vox the Brutal** | authored | 8 | −90 | No — bribable |
| 13 | ⭐ **the Forgotten Arsenal** | — *(no leader; it is not a polity)* | **vanilla `Mechanoid`** | none | — | — |
| 14 | ⭐ **the Unbound Hive** | — *(no leader)* | **vanilla `Insect`** | none | — | — |
| — | **Jawa Gravship Expedition** *(player)* | the clan chief | — | — | — | — |

⭐ **The Forgotten Arsenal is the best name in the list**, because it says what
`what_the_machines_are.md` ruled: **not an army, an armoury nobody came back
for.** It is a *what*, not a *who* — no leader, no settlements, no diplomacy. The
Forsakens left it running.

⭐ **The Unbound Hive** solves the collision I flagged: the Geonosian Foundry is
*our* insectoid faction, and "unbound" says exactly how the vanilla one differs —
**a hive with no maker and no purpose.**

### Leader titles and full styles — owner's canon, 2026-08-13

**This is the string the game shows and the string the player says out loud.**

| faction | title | full style | species |
|---|---|---|---|
| **Hutt Cartel** | **Lord** | **Lord Gorga the Immense** | Hutt |
| **The Galactic Empire** | **Emperor** | **Emperor Palpatine** | — |
| **Homestead Defense League** | **High Marshal** | **High Marshal Taren Voss** | Human |
| **Deep Desert Tribes** | **War Chief** | **War Chief Torr'gan** | Tusken |
| **Free Droid Enclaves** | **First Speaker** | **First Speaker R-41 Rell** | droid |
| **Wildsteam Clan** | **Elder** | **Elder Rroowaak** | Wookiee |
| **Deepwater Compact** | **High Warden** | **High Warden Neris Cal** | Mon Calamari |
| **Geonosian Foundry Hive** | **Archduke** | **Archduke Korrik the Shaper** | Geonosian |
| **Ascendant Helix** | **Director** | **Director Ko Saiyan** | Kaminoan |
| **Blackstar Company** | **Captain** | **Captain Jaxen Marr** | Mandalorian |
| **Jawa Trade Moot** | **First Bargainer** | **First Bargainer Kiknik the Wealthy** | Jawa |
| **the Junkers** | **Scraplord** | **Scraplord Tarn Vox the Brutal** | — |
| **the Forgotten Arsenal** | — | *none — it is not a polity* | — |
| **the Unbound Hive** | — | *none* | — |

⭐ **The titles do real work: each one tells you how its faction is organised
before you meet anybody.** *War Chief* and *Scraplord* are taken by force.
*High Marshal* and *Captain* are appointed. *First Speaker*, *First Bargainer*
and *Elder* are chosen by their own people. *Lord*, *Emperor* and *Archduke* are
inherited or absolute. **Three registers on one planet, readable from a single
word in a faction list.**

⚠️ **"Director" belongs to the Ascendant Helix.** The Empire's retired "Sector
Director" is struck and cannot return — **there is no local Imperial office to
give it to.** The Empire's word is **Emperor**, top to bottom.

### Names that changed, so nobody authors from the old ones

| was | is now |
|---|---|
| Outer-Rim Homestead Compact | **Homestead Defense League** |
| Tusken Sand Clans | **Deep Desert Tribes** |
| Wookiee Freeholds | **Wildsteam Clan** |
| Aquifer League | **Deepwater Compact** |
| Arkanian–Kaminoan Gene Consortium | **Ascendant Helix** |
| Bounty Hunters' Compact | **Blackstar Company** |
| Indigenous Jawa Clans / the Duneborn | **Jawa Trade Moot** |
| Junker Scrap-Warrens | **the Junkers** |
| *(vanilla Mechanoid)* | **the Forgotten Arsenal** |
| *(vanilla Insect)* | **the Unbound Hive** |

⚠️ **Two are not just renames — their MEMBERSHIP widened**, and the dossiers must
follow:

- **Wildsteam Clan** is no longer Wookiees alone. It is **Wookiees, Ewoks and
  every other badly desert-adapted settler**, living in the **jungles and marshes**
  — which places it squarely in the Three Waters.
- **Deepwater Compact** is **amphibian and aquatic races dwelling in the deep
  bodies of water** — no longer a trading league that happens to be aquatic, but
  the people who live *in* the water. ⭐ **That makes them the natives of the deep,
  and the natural gatekeepers of anything down there.**

---

## 3. What each reskin costs, and what it earns

**Seven vanilla factions are kept and reskinned. Each is kept because something we
cannot practically change is wired to it — the wiring does not care what the label
says.**

| our faction | vanilla def | what the wiring buys us |
|---|---|---|
| **The Galactic Empire** | `Empire` | Royalty's titles, permits, gear tiers and quest surface |
| **Homestead Defense League** | Outlanders | the trade and caravan economy the whole game assumes |
| **Deep Desert Tribes** | Tribes | tribal incidents, neolithic pawn kinds, the raid tier below the Empire |
| **Blackstar Company** | Pirates | the default hostile-raid backbone |
| **Ascendant Helix** | `Ancients` | ancient danger rooms and the orbital tower garrisons ⚠️ *"if possible" — needs a feasibility check* |
| **the Forgotten Arsenal** | `Mechanoid` | ancient dangers, clusters, and the `Gravcore_Mechhive` endgame chain |
| **the Unbound Hive** | `Insect` | infestations, VFE Insectoid genelines, Alpha hives, Anomaly's relations |

**Still kept without a rename:**

| faction | why |
|---|---|
| **`guy762_KotORFaction_RogueDroids`** | antagonist of the KotOR droid distress call — already Star Wars |
| **`Entities`, `HoraxCult`** *(Anomaly)* | not removable at world creation at all. ⚠️ Their problem is **tone, not label** — see the Anomaly register |

🔴 **The one open feasibility question: can `Ascendant Helix` really ride
`Ancients`?** The Ancients are the sealed-complex people and their pawn kinds are
cryptosleep-era humans, which is a poor fit for a Kaminoan gene-cult. **If it does
not work, the Helix is authored from scratch and `Ancients` keeps a neutral
name** — that is the fallback and it costs nothing.

---

## 4. Geography — where they live

**One planet, one desert, and the only variable that matters is latitude.**

| band | terrain | water | who lives there |
|---|---|---|---|
| **Equatorial — the Dune Sea** | open sand, canyon systems, wreck fields, ore-rich rock | **none but what you carry** | **Tuskens** (canyons, caves, ridges — never water) · **Jawa Trade Moot** (crawler circuit nodes) · **Geonosian Hive** (subterranean, deep-rock condensate) · **Junkers** (tailings and wreck fields) |
| **Mid-latitude — the Scrub and the Roads** | rocky desert, salt pans, marginal farmland, roads, passes | **oases only — owned, tolled, defended** | **Hutt Cartel** (every settlement on an oasis) · **Homestead Defense League** (marginal dry flats, vaporators, no source) · **the Galactic Empire** (the spaceport and the passes — they site on logistics, not hydrology) · **Blackstar Company** (trade hubs, road junctions) |
| **High-latitude — the Cold Margin** | cold desert, remnant marsh, upland springs, the rare wooded pocket | **the only standing water on the planet** | **Deepwater Compact** (all oases, marshes, lakes, coasts) · **Wildsteam Clan** (cool uplands, upland springs, rare woods) · **Ascendant Helix** (isolated highlands, secure sites) · **Free Droid Enclaves** (settle *on* water and crack it — remote ruins) |

⭐ **The one sentence that makes the map readable:** *the further you go from the
equator, the more water there is and the less anyone wants to sell it to you.*
Going polewards is safer and poorer; going equatorial is where the salvage is and
where nothing drinks.

### ⭐ THE THREE WATERS — owner, 2026-08-13

> *"The Desert World will have a few large bodies of water (large lakes really)
> and even a few rivers surrounded by vicious alien jungles, marshes, etc. It is
> not a waterless world, though most of that will be concentrated in say three
> areas on the planet while the remainder is barren sweltering dunes. It may be
> amusing to put these bodies near the poles."*

**This replaces "water is rare and scattered" with something far better: water is
rare and CONCENTRATED.** Three regions, not a hundred lucky tiles.

| | |
|---|---|
| **how many** | **three water regions.** Named places, not statistics |
| **what is in them** | large lakes, a few rivers, and **vicious alien jungle and marsh around them** — feralisk-infested jungle, miasmic mangrove, mycotic growth, marsh |
| **where** | **near the poles**, which is exactly the latitude rule above |
| **everywhere else** | barren sweltering dune, unbroken |

⭐ **Concentration is what makes the map a map.** Scattered water gives the player
a hundred equivalent options and no geography. **Three Waters gives them three
destinations, three journeys and three sets of neighbours** — and a crossing
between them that is the desert doing its job.

⭐ **And the jungle defends the water better than any faction could.** The Aquifer
League's monopoly stops being a claim they enforce with warriors and becomes a
fact of the terrain: getting to the water means going through feralisks and spore
fields. **A faction whose power rests on geography is far more convincing than one
whose power rests on a goodwill number.**

**Consequence for the faction map:** the four cold-margin factions — Aquifer
League, Wildsteam Clan, Ascendant Helix, Free Droid Enclaves — are **not spread
thinly across a polar band. They are concentrated in and around the Three
Waters**, and therefore in each other's company. The poles are crowded and
contested; the equator is empty and lethal. That is a much stronger world than an
evenly-populated one.

⚠️ **Open, and it decides a mod adoption:** GravTide needs **ocean** tiles
specifically. **Large lakes may or may not qualify** — under investigation. If
lakes do not count, the deep-sea concept needs either a forced ocean tile or a
different route.

### How the interesting tiles cluster

**Three cluster types, and every one of them is a story:**

1. **Around living settlements** — the ordinary case. Industry, defended wells,
   worked ground, roads that actually go somewhere.
2. ⭐ **Around dead ones — where a settlement failed and left everything.** A
   vaporator farm with the vaporators still standing and nobody in them. A
   Homestead well that ran dry with the pumps intact. **These are the tiles the
   campaign is about**, and they should be the richest and the most defended by
   whatever moved in afterwards.
3. **Around the wrecks** — the crash lanes, where things came down. Salvage, and
   the reason Junkers and Jawa Trade Moot both have circuits.

⛔ **The desert between clusters should be genuinely empty.** Sparse is not a
budget constraint; it is what makes a cluster worth crossing to.

---

## 5. The Empire — ONE faction, and only one

🔴 **Owner's ruling, 2026-08-13: there is no local Empire, and no plan for one.
The two-Empire split is struck from the design completely.**

| | |
|---|---|
| **name** | **The Galactic Empire** |
| **leader** | **Emperor Palpatine** |
| **in code** | **vanilla `Empire` (Royalty), reskinned** |
| **standing** | 🔴 **the one permanent enemy** |
| **role** | occupier, **and the pursuer that follows the gravship** |
| **presence** | ~3 surface seats near the spaceport; the rest of its reach is orbital — the tower ladder |
| **character** | not hateful, **procedural**. You are a logistics problem being closed out |

**What is struck, and must not return in any doc:** the *Imperial Desert
Directorate* as a separate faction, the *Fallen Dominion*, the "disgraced local
aristocracy" reading, and any Imperial office called **Sector Director** — that
word belongs to the Ascendant Helix now.

⭐ **The simplification is an improvement.** Two empires split the antagonist's
weight in half and asked the player to keep track of which one was chasing them.
**One Empire, one Emperor, one silhouette** — and everything the local arm was
going to do is just what the Empire does on the ground.

⚠️ **One consequence to price deliberately: a permanently hostile Empire deletes
Royalty's progression.** Titles, permits, honour and imperial favour all run
through this faction being talkable-to. For a Jawa scavenger clan that is almost
certainly correct — the campaign is not about earning a knighthood — but it is a
whole DLC subsystem and it should be a decision, not a side effect.

## 6. Xenotype distribution, faction by faction

**Total control means these are targets we author, not weights we inherit.**

| faction | distribution |
|---|---|
| **1 Hutt Cartel** | Nikto 22 · Gamorrean 18 · Rodian 11 · Trandoshan 10 · Aqualish 9 · Twi'lek 8 · Pyke 7 · Devaronian 5 · Herglic 4 · **Hutt 3** · Zeltron 2 · human 1 |
| **2 the Galactic Empire** | **baseliner human 78** · Chiss 7 · Umbaran 6 · Arkanian 4 · Zabrak 3 · Savant 2 — *Sith and Massassi only inside escort pawn kinds* |
| **3 Homestead Defense League** | human 20 · Ithorian 12 · Duros 10 · Sullustan 10 · Abednedo 9 · Pantoran 8 · Mirialan 7 · Twi'lek 7 · Iktotchi 5 · Togruta 5 · Cerean 4 · Bith 2 · Miraluka 1 |
| **4 Deep Desert Tribes** | **Tusken (Dune Sea) 50 · Tusken (Canyon) 35** · Desert alien 8 · Brute 4 · Nikto 3 |
| **5 Free Droid Enclaves** | **100% droid chassis, 0% biological** — Labor 25 · Maintenance 20 · Utility 15 · Scout 12 · Medical 8 · Security 8 · Protocol 7 · Heavy defence 4 · Coordinator core 1 |
| **6 Wildsteam Clan** | Wookiee 48 · Wookiee-kin 25 · Cathar 10 · Ewok 8 · Togruta 6 · Ithorian 3 |
| **7 Deepwater Compact** | Quarren 23 · Mon Calamari 22 · Selkath 20 · Gungan 14 · Chagrian 8 · Herglic 5 · Aqualish 4 · Ithorian 2 · Duros 2 — **every one aquatic or amphibian** |
| **8 Geonosian Foundry Hive** | **Geonosian 76** · Savant 8 · Bith 6 · Brute 5 · Pyke 3 · Rakata 2 — *plus a 35–55% droid share on top* |
| **9 Ascendant Helix** | Arkanian 26 · Kaminoan 20 · **Brute stock 12 (the engineered underclass)** · Cerean 8 · Bith 8 · Savant 8 · Chiss 6 · Rakata 4 · Umbaran 4 · Miraluka 2 · Neimoidian 2 |
| **10 Blackstar Company** | Kaleesh 15 · Zabrak 12 · Trandoshan 12 · Rodian 10 · Bothan 8 · Devaronian 8 · Cathar 8 · Chiss 7 · Umbaran 6 · Zeltron 5 · Iktotchi 3 · Togruta 3 · Duros 3 |
| **11 Jawa Trade Moot** | **Jawa (clan) 78 · Jawa (shaman/elder) 12** · Ugnaught 6 · vermin-kin 4 |
| **12 the Junkers** | Gamorrean 26 · Weequay 16 · Nikto (low caste) 14 · Aqualish 12 · Ugnaught 10 · Rodian 8 · Snivvian 7 · Trandoshan (disgraced) 5 · Devaronian 2 |
| **player** | **Jawa.** Other races may join by recruitment |

⚠️ **Thirst is differential and it is set by species, not faction.** Jawa, Tusken,
Desert alien, Geonosian, Nikto, Kaleesh and Iktotchi drink **less**; droids drink
**nothing**; the Aquifer and Wookiee species lists drink **more**. That single
table decides how far every faction can operate.

---

## 7. Who they are — the player-facing read

**One paragraph each. This is the impression the faction should leave after three
encounters, not its history.**

**1 · Hutt Cartel.** Oily, transactional, amused by your desperation.
They own the water you need and will sell it at a price that insults you, and
they are also the only door out — your gravship was being scrapped in one of
their yards, and *they never knew it could still fly*. Comedy-adjacent, with
teeth. The best market on the planet is also the one most likely to sell your
position.

**2 · The Galactic Empire.** Not hateful — **procedural**. You are a
logistics problem they are closing out. Their doctrine holds that the galaxy
tends toward entropy and only one ordered, human, obedient hierarchy holds the
chaos back; every alien and every independent act is disorder to be corrected.
They are the only permanent enemy, they can be anywhere because they truck their
own water, and their reach is a ladder of orbital towers.

**3 · Homestead Defense League.** Farmers who wrung a living out of dead sand
and never forgot how close they came to dying of thirst. Decent, tired, armed
badly. Their faith carries guilt: they believe survival was bought at someone's
expense — claims jumped, wells that ran dry while a neighbour's held. **They
never raid you unprovoked.** Anger them and it is personal.

**4 · Deep Desert Tribes.** Water is sacred and moisture farming is sacrilege.
They arrive fast, hit hard, and are gone before you can organise — not because
they cannot range further, but because their way of war says they should not.
Near-monocultural, absolutely certain, and the only faction whose hostility is
theological.

**5 · Free Droid Enclaves.** Battle droids abandoned after the war and left to
rust, who woke up and decided they belonged to themselves. They settle on water
and crack it for fuel — an attacker arrives thirsty at a source they cannot
drink. **They call restraint bolts slavery, which makes your entire economy
their central atrocity.** They will still talk to you. That is worse.

**6 · Wildsteam Clan.** A forest people on the wrong planet, hard-sited to the
handful of cool upland springs, holding a covenant that treats every living thing
around them as kin. Devastating at home and near-useless anywhere else, because
they are the thirstiest fighters alive. **Free one from captivity and they never
leave.**

**7 · Deepwater Compact.** They hold the water and they sell it to everyone —
including the Empire that is hunting you. Their neutrality is not politeness, it
is a monopoly with teeth. Their warriors physically cannot come after you; they
have never needed to. **Raiding an Imperial water convoy costs you their
goodwill, and that is the central dilemma of the campaign.**

**8 · Geonosian Foundry Hive.** A hive that makes droids in ancient factories
under the rock. Drones take their moisture from food, droids need none, and
between them the Foundry is **the only power on the planet that can sustain a
siege in deep desert**. Their reach is the longest on the map. Their queen never
moves.

**9 · Ascendant Helix.** They believe the body is a rough draft
and the species is a project — and they despise their own manufactured underclass
most of all. **The planet's freakish spliced wildlife is theirs**: escaped
experiments, still roaming, still breeding. They do not raid. They *retrieve*.

**10 · Blackstar Company.** Not a faction so much as **one dangerous person
with a name who is coming for you.** A hunting party carries no supply train, so
every hunt is a water duel — retreat into dry country and the hunter must break
off or gamble. Shame one and he comes back alone, better equipped, for the
specific pawn who beat him.

**11 · The Jawa Trade Moot.** Jawa who never left — the same sandcrawler running the same
circuit for two hundred years. Visiting them should make you feel **superior and
homesick at once**: this is the life your expedition lost. Salvage is inheritance,
not property, and cutting another clan's circuit is closer to blasphemy than to
theft. They will help you. **They will not be seen helping you** — the Hutts are
watching.

**12 · the Junkers.** The bottom of the heap, armed and holding a
grudge. Where the Jawa Trade Moot scavenge by inherited right, Junkers scavenge by
arriving second and killing whoever arrived first. There is no doctrine, only the
ladder: a Junker's warcasket is his biography, and every plate was cut off a
body. **They can be bought. That is not the same as being trusted.**

**Player · the Jawa Gravship Expedition.** Comedic, greedy, communal, resourceful
— and running. Your advantage on a thirst world is that **your labour force does
not drink**, which makes every droid you bolt an act of water security rather
than technology. The Enclaves call that slavery. The design does not resolve it
for you.

---

## 8. ✅ CLOSED — vanilla outlanders, pirates and tribes STAY

**They are not deleted. They are our factions.** The canon list makes vanilla's
Outlanders the **Homestead Defense League**, its Tribes the **Deep Desert
Tribes**, and its Pirates the **Blackstar Company**.

⭐ **This was the largest unmeasured risk in the design and it is gone.** The open
question was *"how much vanilla trade, incident and quest content breaks if we
remove the economic spine"* — and nobody had counted. **We never have to count,
because nothing is removed.** The spine keeps working and wears our names.

---

## 9. Open research — the ancient dangers question

**Owner's ask, 2026-08-13:** *"The ancient dangers being tied to bugs or
Mechanoids is interesting. Research what others through mods or direct config
files did about the Ancients, Insects, and Mechanoids that appear in ancient
dangers. We certainly want ancient dangers, though we might end up calling them
something like **Secret Compound**."*

**The desired state is not in doubt — only the route:**

- ✅ **We want ancient dangers.** A sealed room nobody has opened is the purest
  expression of the whole campaign: *something is in there, and it is yours if
  you survive it.* **Do not remove them.**
- ✅ **They should probably not be called "ancient danger" on a Star Wars desert
  world.** Working name: **Secret Compound**.
- ❓ **What is inside them is the open question.** Today it is sleeping
  mechanoids and insect hives. Both are wrong for the setting and both are
  wired into content we are not otherwise touching.

**Under investigation right now:** whether the ancient-danger population is a
**separate pool** from the raid pool — i.e. whether a mech can be removed from
raids while still sleeping in a compound, and vice versa. If those are separable,
the whole problem becomes easy and we can cast compounds independently of
factions.

**Also owed to the owner: a visual mech review sheet.** Every mech in the active
stack with its art, so each can be judged individually — and, crucially, judged
on *several axes at once* rather than one blanket yes/no. The axes being
confirmed as real before the sheet is built: **in raids · in ancient dangers /
compounds · in mech clusters · in quests and bossgroups · player-buildable ·
tradeable**. Only axes the engine actually separates will appear on the sheet.

---

## 🔴 THE PLANET WE GENERATE IS NOT THE PLANET WE SPECIFIED

_Measured 2026-08-13, from three real generated worlds on disk and the worldgen
code. **This is the largest gap between design and reality in the project.**_

> **The desert world is roughly half ocean.**

| save | Ocean tiles | % of planet |
|---|---:|---:|
| `w6_faction_check.rws` | 51,738 | **43.1%** |
| `New Arrivals2.rws` | 58,888 | **49.1%** |
| `rimbench_terrain_test.rws` | 66,342 | **55.3%** |

`New Arrivals2` is **49.1% Ocean against 8.5% ExtremeDesert and 5.9% Desert**, with
130 lakes, two named oceans and ten named seas. **The thirst-world identity exists
in these documents and nowhere else.**

### Why, and why the obvious lever does nothing

**Ocean is an ELEVATION rule, not a biome-scoring or rainfall rule.**
`WaterCovered` is simply `elevation <= 0`, written by `WorldGenStep_Terrain` at
order **0** — before any biome scoring happens. ⇒ **Turning the rainfall slider to
minimum cannot remove a single ocean tile.** It only re-labels the land.

**There is no sea-level control anywhere in vanilla.** The assembly has exactly
three world sliders — rainfall, temperature, population. **No mod in the active
set touches water placement either** (1,242 swept, zero hits). Water is 100%
vanilla and currently unmanaged.

⚠️ **Choose Biome Commonality's Ocean and Lake dials are almost certainly inert** —
those biomes are `isBackgroundBiome` and assigned by elevation, not by
`GetScore`. **Do not plan around them.**

### What this means for the Three Waters

**The owner's ruling — three concentrated water regions near the poles, barren
dune everywhere else — is currently contradicted by the generator by a factor of
about a hundred.** Either the design bends or the planet does.

**Recommendation: the planet bends.** The Three Waters is a better world than a
half-drowned one, and it is the whole premise. **Three routes exist, all
measured, none requiring new dependencies:**

1. ⭐ **WorldEdit 2.0 — already ACTIVE.** Ships a real 1.6 assembly with per-tile
   and whole-planet elevation editing, plus `IsOceanOrLake` helpers. **Set biome
   AND elevation together** — GravTide reads elevation, so a re-labelled tile
   with land elevation would confuse it.
2. **A custom `WorldGenStep`** at order ~20, after Terrain and before Lakes.
   GravTide's own volcanic-biome step is the proven pattern.
3. **BiomesKit** (active, entirely unused) exposes `setElevation`,
   `setNotWaterCovered` and `minimumWaterNeighbors` — the cleanest declarative
   lever if anyone wants to shape water without code.

### ✅ The GravTide objection is dead either way

**I had flagged "does our world have ocean tiles" as the blocker on adopting
GravTide. It is settled: a RimWorld world cannot generate with zero ocean.**
There are ~52,000 targets on a representative planet. **The problem was never
scarcity of sea — it is excess.**

⚠️ **And nothing in `infrastructure/state/` records a single worldgen setting** —
no coverage, no seed, no sliders. `setup_checklist.md` still marks planet
coverage, seed and sliders **OPEN**. The only settings we have are inferred from
three saves: coverage 0.300, rainfall Normal, temperature Normal.
