# The world we want — faction specification

_VISION, 2026-08-13. **This states the desired end state only.** No instructions,
no UI steps, no "how to get there". Everything here is a claim about what should
be true of the finished world; how to make each line true is a separate problem
for whoever configures the mods._

**Owner's two governing rulings, this session:**

> **"We keep factions only when they are wired into specific game events or
> functions we can't change. Otherwise we author from scratch. We want total
> control, no inheriting strange stuff."**

> **"It should be a BIG world but the settlements are quite sparse. Interesting
> tiles should be clustered together in intriguing patterns: sometimes around
> existing settlements, sometimes showing where failed settlements died. We are
> going to author that world ourselves as much as possible."**

---

## 1. What is true, and what is not

| | |
|---|---|
| ✅ **Twelve NPC factions exist**, plus the player's Jawa expedition | |
| ✅ **All twelve are authored by us from scratch.** Own `FactionDef`, own name, own pawn kinds, own xenotype mix | |
| ✅ **Mod factions survive ONLY where something we cannot change is wired to them** — an incident's antagonist, a scenario part, a quest chain | |
| ✅ **The world is BIG and sparse.** ~72 settlements across a large planet | |
| ✅ **Interesting tiles cluster.** Around living settlements, and around dead ones | |
| ✅ **One permanent enemy: the Imperial Desert Directorate** | |
| ✅ **Water increases with latitude.** The equator is the killing ground; the poles hold the only standing water | |
| ❌ **No mod faction is kept "because it is Star Wars"** | flavour is not a dependency |
| ❌ **No faction is a reskin of a mod faction** | the v1 Directorate label-patch is a temporary stand-in, not the design |
| ❌ **No faction generates Jawa except faction 11** | the player race is not a common sight |
| ❌ **The world is not auto-generated and accepted** | generate a seed, then author on top of it |
| ❌ **Nobody except the Empire is permanently un-negotiable** | the mid-game always has a wedge |

---

## 2. The factions we author — twelve

| # | Faction | Settlements | Tech | Goodwill | Perm. enemy | Raids |
|---|---|---:|---|---:|---|---|
| 1 | **Hutt Cartel Confederacy** | 8 | Industrial | −35 | No | Medium, distance-scaled |
| 2 | **Imperial Desert Directorate** | **3 surface** *(+~7 orbital, not world tiles)* | Spacer | −100 | 🔴 **Yes** | High |
| 3 | **Outer-Rim Homestead Compact** | 13 | Industrial | +25 | No | **None random — event-driven only** |
| 4 | **Tusken Sand Clans** | 9 | Industrial, gear-restricted | −80 | No | High near their territory; very short, no siege |
| 5 | **Free Droid Enclaves** | 3 | Spacer | 0 | No | Disabled — quests and incidents only |
| 6 | **Wookiee Freeholds** | 4 | Industrial | +35 | No | Very low |
| 7 | **Aquifer League** | 5 | Industrial | +10 | No | **None** — cannot operate away from water |
| 8 | **Geonosian Foundry Hive** | 5 | Spacer | −100 | No | High; **longest reach on the map**; sieges common |
| 9 | **Arkanian–Kaminoan Gene Consortium** | 3 | Spacer | 0 | No | Low — retrieval operations only |
| 10 | **Bounty Hunters' Compact** | 4 | Industrial | −10 | No | Very low; **targeted hunts, not raids** |
| 11 | **Indigenous Jawa Clans — "the Duneborn"** | 7 | Industrial, salvage-grade | **+40, capped +75, never allied** | No | Very low — only after a claim dispute |
| 12 | **Junker Scrap-Warrens** | 8 | Industrial, degraded | −90 | No — **hostile but bribable** | High; long duration |
| — | **Jawa Gravship Expedition** *(player)* | — | Salvage-dependent | — | — | — |

**Total: 72 world settlements.** Sparse across a big planet, which is the point.

### Leader titles

| faction | title |
|---|---|
| Hutt Cartel | Kajidic patriarch / matriarch |
| Imperial Directorate | **Sector Director** |
| Homestead Compact | Elected well-keeper |
| Tusken Sand Clans | Clan speaker |
| Free Droid Enclaves | Coordinator |
| Wookiee Freeholds | Elder of the freehold |
| Aquifer League | First custodian |
| Geonosian Foundry Hive | Arch-overseer *(the Queen is immobile and is the settlement objective, not the diplomatic leader)* |
| Gene Consortium | Chief curator |
| Bounty Compact | Guild adjudicator |
| Duneborn | Scrap-Singer *(elder; quest-giver)* |
| Junker Scrap-Warrens | Warren Boss |

---

## 3. The factions we KEEP, and the exact dependency that earns it

**These are the only survivors.** Each is kept because something we cannot
practically change points at it. **Nothing on this list is kept for flavour.**

| faction | what is wired to it | consequence of removing it |
|---|---|---|
| **`Mechanoid`** *(vanilla)* | `ScenPart_PursuingMechanoids` — the gravship pursuit; mech clusters; ancient dangers; **and the `Gravcore_Mechhive` endgame chain, which needs 7 of its 9 subquests** | 🔴 **Permanently locks the Odyssey gravship endgame.** Disqualifying on its own |
| **`Empire`** *(vanilla Royalty)* | Royalty's entire title, permit and quest surface — **and it is now the Fallen Dominion** (§5) | loses both the DLC's content and our second empire |
| **`guy762_KotORFaction_RogueDroids`** | `hostileFactionDef` of the droid distress-call incident in [BTD] Ship Pack: KotOR Ships | a distress call with no antagonist — **a quest the player accepts and cannot finish** |
| **`Insect`** *(vanilla)* | infestations, VFE Insectoids genelines, Alpha Animals hives, and Anomaly's `Entities` relations | removing the faction does not remove the bugs; it orphans them |
| **`Entities`, `HoraxCult`** *(Anomaly)* | not removable at world creation at all — no lever short of disabling the DLC | n/a — kept by force, not by choice |
| **`Ancients` / `AncientsHostile`** | ancient danger rooms, and the orbital tower dungeons | the towers lose their garrison |
| ⚠️ **Outlanders · Pirates · Tribes** *(vanilla)* | an enormous volume of vanilla incident, trade and quest content assumes they exist | **OPEN CALL — see §8.** My recommendation is keep-as-structure |

### Renames — deliberately almost none

**Because we author our own, there is nothing to rename.** Two exceptions:

| faction | rename to | why |
|---|---|---|
| **`Empire`** *(vanilla)* | **The Fallen Dominion** | it becomes ours in fiction without becoming ours in code — see §5 |
| **`Mechanoid`** | a Star Wars reading — *the Derelict Automata*, or similar | it cannot be removed, so it should at least stop saying "mechanoid" on a Star Wars world. **Label only. One operation. Zero risk** |

**Everything else on the keep list stays exactly as it is**, because it is kept for
its wiring, not its identity, and a rename buys nothing.

---

## 4. Geography — where they live

**One planet, one desert, and the only variable that matters is latitude.**

| band | terrain | water | who lives there |
|---|---|---|---|
| **Equatorial — the Dune Sea** | open sand, canyon systems, wreck fields, ore-rich rock | **none but what you carry** | **Tuskens** (canyons, caves, ridges — never water) · **Duneborn** (crawler circuit nodes) · **Geonosian Hive** (subterranean, deep-rock condensate) · **Junkers** (tailings and wreck fields) |
| **Mid-latitude — the Scrub and the Roads** | rocky desert, salt pans, marginal farmland, roads, passes | **oases only — owned, tolled, defended** | **Hutt Cartel** (every settlement on an oasis) · **Homestead Compact** (marginal dry flats, vaporators, no source) · **Imperial Directorate** (the spaceport and the passes — they site on logistics, not hydrology) · **Bounty Compact** (trade hubs, road junctions) |
| **High-latitude — the Cold Margin** | cold desert, remnant marsh, upland springs, the rare wooded pocket | **the only standing water on the planet** | **Aquifer League** (all oases, marshes, lakes, coasts) · **Wookiee Freeholds** (cool uplands, upland springs, rare woods) · **Gene Consortium** (isolated highlands, secure sites) · **Free Droid Enclaves** (settle *on* water and crack it — remote ruins) |

⭐ **The one sentence that makes the map readable:** *the further you go from the
equator, the more water there is and the less anyone wants to sell it to you.*
Going polewards is safer and poorer; going equatorial is where the salvage is and
where nothing drinks.

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
   the reason Junkers and Duneborn both have circuits.

⛔ **The desert between clusters should be genuinely empty.** Sparse is not a
budget constraint; it is what makes a cluster worth crossing to.

---

## 5. The two Empires

**They are not a duplicate. They are the design.**

| | **Imperial Desert Directorate** | **The Fallen Dominion** |
|---|---|---|
| what it is | the Galactic arm — occupier, spacer tech, orbital seats | the **local aristocracy**, force-welded into the Empire |
| where | 3 surface seats near the spaceport, ~7 orbital holdings | planetside, the settlements it always held |
| standing | the Empire itself | **in disgrace.** It won the local war and got blamed for the peace |
| motive | procedural. You are a logistics problem being closed out | **eager to please.** It hunts "yet more chaotic nonsense" — such as Jawa flying an ancient hulk on a persona core — to earn its way back |
| in code | authored by us | **vanilla `Empire`, renamed** |

⚠️ **Its name is generated at world creation.** Until a `fixedName` is authored,
whatever the world calls it *is* its name.

---

## 6. Xenotype distribution, faction by faction

**Total control means these are targets we author, not weights we inherit.**

| faction | distribution |
|---|---|
| **1 Hutt Cartel** | Nikto 22 · Gamorrean 18 · Rodian 11 · Trandoshan 10 · Aqualish 9 · Twi'lek 8 · Pyke 7 · Devaronian 5 · Herglic 4 · **Hutt 3** · Zeltron 2 · human 1 |
| **2 Imperial Directorate** | **baseliner human 78** · Chiss 7 · Umbaran 6 · Arkanian 4 · Zabrak 3 · Savant 2 — *Sith and Massassi only inside escort pawn kinds* |
| **3 Homestead Compact** | human 20 · Ithorian 12 · Duros 10 · Sullustan 10 · Abednedo 9 · Pantoran 8 · Mirialan 7 · Twi'lek 7 · Iktotchi 5 · Togruta 5 · Cerean 4 · Bith 2 · Miraluka 1 |
| **4 Tusken Sand Clans** | **Tusken (Dune Sea) 50 · Tusken (Canyon) 35** · Desert alien 8 · Brute 4 · Nikto 3 |
| **5 Free Droid Enclaves** | **100% droid chassis, 0% biological** — Labor 25 · Maintenance 20 · Utility 15 · Scout 12 · Medical 8 · Security 8 · Protocol 7 · Heavy defence 4 · Coordinator core 1 |
| **6 Wookiee Freeholds** | Wookiee 48 · Wookiee-kin 25 · Cathar 10 · Ewok 8 · Togruta 6 · Ithorian 3 |
| **7 Aquifer League** | Quarren 23 · Mon Calamari 22 · Selkath 20 · Gungan 14 · Chagrian 8 · Herglic 5 · Aqualish 4 · Ithorian 2 · Duros 2 — **every one aquatic or amphibian** |
| **8 Geonosian Foundry Hive** | **Geonosian 76** · Savant 8 · Bith 6 · Brute 5 · Pyke 3 · Rakata 2 — *plus a 35–55% droid share on top* |
| **9 Gene Consortium** | Arkanian 26 · Kaminoan 20 · **Brute stock 12 (the engineered underclass)** · Cerean 8 · Bith 8 · Savant 8 · Chiss 6 · Rakata 4 · Umbaran 4 · Miraluka 2 · Neimoidian 2 |
| **10 Bounty Compact** | Kaleesh 15 · Zabrak 12 · Trandoshan 12 · Rodian 10 · Bothan 8 · Devaronian 8 · Cathar 8 · Chiss 7 · Umbaran 6 · Zeltron 5 · Iktotchi 3 · Togruta 3 · Duros 3 |
| **11 Duneborn** | **Jawa (clan) 78 · Jawa (shaman/elder) 12** · Ugnaught 6 · vermin-kin 4 |
| **12 Junker Scrap-Warrens** | Gamorrean 26 · Weequay 16 · Nikto (low caste) 14 · Aqualish 12 · Ugnaught 10 · Rodian 8 · Snivvian 7 · Trandoshan (disgraced) 5 · Devaronian 2 |
| **player** | **Jawa.** Other races may join by recruitment |

⚠️ **Thirst is differential and it is set by species, not faction.** Jawa, Tusken,
Desert alien, Geonosian, Nikto, Kaleesh and Iktotchi drink **less**; droids drink
**nothing**; the Aquifer and Wookiee species lists drink **more**. That single
table decides how far every faction can operate.

---

## 7. Who they are — the player-facing read

**One paragraph each. This is the impression the faction should leave after three
encounters, not its history.**

**1 · Hutt Cartel Confederacy.** Oily, transactional, amused by your desperation.
They own the water you need and will sell it at a price that insults you, and
they are also the only door out — your gravship was being scrapped in one of
their yards, and *they never knew it could still fly*. Comedy-adjacent, with
teeth. The best market on the planet is also the one most likely to sell your
position.

**2 · Imperial Desert Directorate.** Not hateful — **procedural**. You are a
logistics problem they are closing out. Their doctrine holds that the galaxy
tends toward entropy and only one ordered, human, obedient hierarchy holds the
chaos back; every alien and every independent act is disorder to be corrected.
They are the only permanent enemy, they can be anywhere because they truck their
own water, and their reach is a ladder of orbital towers.

**3 · Outer-Rim Homestead Compact.** Farmers who wrung a living out of dead sand
and never forgot how close they came to dying of thirst. Decent, tired, armed
badly. Their faith carries guilt: they believe survival was bought at someone's
expense — claims jumped, wells that ran dry while a neighbour's held. **They
never raid you unprovoked.** Anger them and it is personal.

**4 · Tusken Sand Clans.** Water is sacred and moisture farming is sacrilege.
They arrive fast, hit hard, and are gone before you can organise — not because
they cannot range further, but because their way of war says they should not.
Near-monocultural, absolutely certain, and the only faction whose hostility is
theological.

**5 · Free Droid Enclaves.** Battle droids abandoned after the war and left to
rust, who woke up and decided they belonged to themselves. They settle on water
and crack it for fuel — an attacker arrives thirsty at a source they cannot
drink. **They call restraining bolts slavery, which makes your entire economy
their central atrocity.** They will still talk to you. That is worse.

**6 · Wookiee Freeholds.** A forest people on the wrong planet, hard-sited to the
handful of cool upland springs, holding a covenant that treats every living thing
around them as kin. Devastating at home and near-useless anywhere else, because
they are the thirstiest fighters alive. **Free one from captivity and they never
leave.**

**7 · Aquifer League.** They hold the water and they sell it to everyone —
including the Empire that is hunting you. Their neutrality is not politeness, it
is a monopoly with teeth. Their warriors physically cannot come after you; they
have never needed to. **Raiding an Imperial water convoy costs you their
goodwill, and that is the central dilemma of the campaign.**

**8 · Geonosian Foundry Hive.** A hive that makes droids in ancient factories
under the rock. Drones take their moisture from food, droids need none, and
between them the Foundry is **the only power on the planet that can sustain a
siege in deep desert**. Their reach is the longest on the map. Their queen never
moves.

**9 · Arkanian–Kaminoan Gene Consortium.** They believe the body is a rough draft
and the species is a project — and they despise their own manufactured underclass
most of all. **The planet's freakish spliced wildlife is theirs**: escaped
experiments, still roaming, still breeding. They do not raid. They *retrieve*.

**10 · Bounty Hunters' Compact.** Not a faction so much as **one dangerous person
with a name who is coming for you.** A hunting party carries no supply train, so
every hunt is a water duel — retreat into dry country and the hunter must break
off or gamble. Shame one and he comes back alone, better equipped, for the
specific pawn who beat him.

**11 · The Duneborn.** Jawa who never left — the same sandcrawler running the same
circuit for two hundred years. Visiting them should make you feel **superior and
homesick at once**: this is the life your expedition lost. Salvage is inheritance,
not property, and cutting another clan's circuit is closer to blasphemy than to
theft. They will help you. **They will not be seen helping you** — the Hutts are
watching.

**12 · Junker Scrap-Warrens.** The bottom of the heap, armed and holding a
grudge. Where the Duneborn scavenge by inherited right, Junkers scavenge by
arriving second and killing whoever arrived first. There is no doctrine, only the
ladder: a Junker's warcasket is his biography, and every plate was cut off a
body. **They can be bought. That is not the same as being trusted.**

**Player · the Jawa Gravship Expedition.** Comedic, greedy, communal, resourceful
— and running. Your advantage on a thirst world is that **your labour force does
not drink**, which makes every droid you bolt an act of water security rather
than technology. The Enclaves call that slavery. The design does not resolve it
for you.

---

## 8. The one open call

⚠️ **Vanilla outlanders, pirates and tribes.** Total control argues for deleting
them; a very large volume of vanilla trade, incident and quest content assumes
they exist, and unlike the Mechanoid case nobody has measured how much.

**My recommendation: keep them as structure**, unlabelled and unloved, until
someone measures what breaks. They are the economy's floor. **If we delete them
we should do it deliberately, having counted the cost — not as a side effect of
wanting a Star Wars world.**

**Everything else in this document is decided.**
