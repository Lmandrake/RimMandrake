# RimWorld 1.6 Desert-World Faction Roster — v2

> ## Reconciliation decisions (user, 2026-08-06)
> Adopted as canonical from a second design stream, "as true as possible." The doc is
> adopted wholesale **except** the four rulings below, which override the text where it conflicts:
>
> 1. **Jedi placement — BOTH are true.** The v2 "factionless, Empire-hunted lone wanderer"
>    is the *primary* Jedi presence (psylink 3–6, ≤1 per encounter, no faction membership).
>    In addition, a **rare Jedi may shelter within a sympathetic Homestead / Moisture-Farmer
>    group** (our earlier locked call). Both channels coexist; VPE remains the sole Force
>    substrate and the NPC-only gate still holds (no player Force ceiling).
> 2. **Race renames REJECTED — no Skakoan / Houk / Ghorfa races.** Verified on disk
>    (Outer Rim – Galactic Diversity 1.6, all 54 shipped xenotypes enumerated 2026-08-06):
>    **there is no Skakoan and no Houk xenotype**, and **Ghorfa** exists only as a lore line
>    inside the Tusken description (Tusken ancestry flavor), not a separate race with art.
>    We keep our reflavored-vanilla roster whose base art actually ships: **Savant caste ← Genie,
>    Brute stock ← Neanderthal, Desert alien ← Impid.** The Skakoan **sealed-suit / pressure-suit
>    mechanic and its filter dependency are DROPPED entirely.** (Canon names as pure cosmetic
>    text labels over the vanilla art remain a trivial future option if ever wanted — but no new
>    race, no new dependency.) Klatooinian / Vodran / Arkanian-Offshoot likewise only adoptable
>    as labels over existing art, not as new xenotypes.
> 3. **Miraluka — prisoners only (ADOPTED).** `OuterRim_Miraluka` confirmed on disk; they appear
>    **exclusively as Imperial prisoners / rescue-quest targets**, superseding the earlier
>    "lean light/neutral" note.
> 4. Everything else in this doc — water/thirst doctrine, NPC-vs-NPC relations matrix, the ten
>    faction designs (Aquifer League, Free Droid Enclaves, Geonosian Foundry Hive, Arkanian–
>    Kaminoan Gene Consortium, etc.), settlement-count tiers, equipment discipline — is adopted
>    as canonical. The Free Droid Enclaves are the on-disk anchor for the parked
>    "steal the droid-building secret" arc (restraining-bolt moral tension retained).

## Purpose

Ten NPC factions for a hot, arid, water-scarce RimWorld with an active **Thirst system**. The **Jawa gravship expedition is the player faction** and is not counted among the ten.

Everything here is expressible through RimWorld 1.6 definitions, DLC systems, faction/world editing, or ordinary mod definitions:

- `FactionDef` technology level, goodwill, permanence of hostility, traders, pawn groups, settlement generation
- weighted xenotype/race distributions
- custom `PawnKindDef` roles with forced race/xenotype assignment
- Ideology memes, precepts, roles, apparel requirements, styles, rituals
- weapon, apparel, utility-item, drug, implant, and mechanoid loadout tags
- settlement count and placement via world/faction editing
- custom droid, Hutt, and species races under the roster's tweak license
- Royalty psycasts and psylinks for rare Jedi and Sith pawn kinds
- Biotech mechanoids or custom droid pawn kinds for military and independent droids

Removed **Force Gremlin** and disabled WIP species remain excluded.

---

## Design pillars

1. **Factions are defined against each other, not just against the player.** A hardcoded relations matrix drives diplomacy; "enemy of my enemy" is playable.
2. **Water is the strategic axis.** Every faction has a water doctrine that determines where it settles, how far its warriors can operate, and whether it can besiege.
3. **Only warriors are visible.** All water, caste, and equipment rules are written against the combat pawn kinds RimWorld actually spawns.
4. **Hierarchy lives in pawn kinds, not xenotype percentages.** Diverse factions mostly carry no preferred-xenotype precept; rank is encoded through pawn-kind eligibility, gear, skills, and raid-point cost.
5. **One permanent enemy only.** The Imperial Directorate. Everything else can eventually be negotiated with, so the mid-game always has a wedge.

---

## Global system 1 — Faction relations matrix

Set through NPC-vs-NPC goodwill in the faction/world editor. These are lore-derived and should be enforced after generation.

| Pair | Stance | Basis |
|---|---|---|
| Imperial ↔ Wookiee Freeholds | Hostile (hardcoded) | Empire repealed anti-slavery law, reclassified Wookiees as non-sentient, used them as forced labour |
| Imperial ↔ Aquifer League | Hostile | Mon Calamari also targeted for Imperial enslavement |
| Imperial ↔ Geonosian Hive | Hostile | Geonosians enslaved by the Empire to build the Death Star |
| Imperial ↔ Free Droid Enclaves | Hostile | Enclave founders were abandoned by the Empire post-Clone Wars |
| Hutt Cartel ↔ Wookiee Freeholds | Hostile | Trandoshan Scorekeeper doctrine: Wookiee kills are the highest-value target |
| Bounty Compact ↔ Wookiee Freeholds | Hostile | Same |
| Tusken Clans ↔ Homestead Compact | Hostile (hardcoded) | Tuskens hold water as sacred and moisture farming as sacrilege |
| Tusken Clans ↔ Hutt Cartel | Hostile | Pyke spice convoys cross Tusken territory |
| Geonosian Hive ↔ Free Droid Enclaves | Cold / no trade | Enclave chassis are escaped Foundry product |
| Hutt Cartel ↔ Free Droid Enclaves | Transactional | The Droid Gotra historically served as Hutt muscle |
| Wookiee Freeholds ↔ Free Droid Enclaves | Positive | Shared absolute anti-slavery precept |
| Gene Consortium ↔ Aquifer League | Positive (trade dependency) | Consortium buys bulk water for growth vats and biosculpters |
| Aquifer League ↔ all others | Neutral-positive by doctrine | Enforced neutrality backed by a water monopoly |

---

## Global system 2 — Water and thirst doctrine

Four states. Each governs settlement siting **and** the operational range of that faction's warriors.

| State | Settlement siting | Warriors in the field |
|---|---|---|
| **Require** | Must spawn on or adjacent to a water tile | Dehydrate off-tile; short raid range; cannot besiege |
| **Manufacture** | Dry tiles; makes its own water | Normal range, but a destructible dependency |
| **Allow** | Indifferent; sites on strategic value | Carries water; range capped by logistics tail |
| **Forbid / Deny** | Will not site on open water — taboo or hostility | Longest dry-tile reach; the deep-desert threat |

### Assignments

| Faction | State | Consequence |
|---|---|---|
| Aquifer League | **Require** (absolute) | Holds every water tile; cannot meaningfully raid |
| Wookiee Freeholds | **Require** (severe) | Devastating on home defence, near-useless expeditionary |
| Hutt Cartel | **Require** (oasis-anchored) | Every compound sits on a fiercely held oasis tile |
| Outer-Rim Homestead | **Manufacture** | Vaporators: stores water, has no source |
| Gene Consortium | **Allow** (high consumption) | Buys bulk water from the League |
| Imperial Directorate | **Allow** (supplied) | Can settle anywhere; convoys are an attack surface |
| Bounty Compact | **Allow** (water clock) | Hunt teams carry a finite supply — range is the fight |
| Geonosian Foundry Hive | **Forbid** (arid-adapted) | Only faction that can sustain a deep-desert siege |
| Tusken Sand Clans | **Forbid** (taboo) | High raid frequency, very short duration, no siege |
| Free Droid Enclaves | **Deny** | Settle on water, crack it for fuel; runoff is lethal |

### Resulting world shape

Water tiles belong to the friendly-to-neutral band (League, Wookiee uplands, Hutt oases). Dry tiles belong to the hostile band (Tusken, Geonosian, supplied Imperial, denial-holding droids). The player's expansion is a fork: **settle wet and be crowded by factions you can negotiate with, or settle dry and be open but permanently hunted.**

### Sealed species

Two species carry no field thirst need at all and instead run on a consumable filter dependency. Both are long-range dry-tile operators; filters are loot.

- **Kel Dor** — Dorin's atmosphere is helium plus a unique gas with almost no oxygen. Off-world they wear antiox masks to filter oxygen out; without the mask they suffocate, without goggles they are effectively blind, and the mask is poisonous to other species.
- **Skakoan** — Techno Union engineers, sealed in methane pressure suits away from Skako.

---

## Global system 3 — Naming

Generic xenotype-mod labels are replaced with in-universe species so raid logs never break the fiction.

| Old label | Now | Role |
|---|---|---|
| Savant caste | **Skakoan** | Sealed Techno Union engineer/fabricator caste |
| Brute stock | **Houk** | Large aggressive heavies; share Sriluur with the Weequay |
| Desert Alien | **Ghorfa** | Feral unmasked Tusken offshoot; fire-callers and stalkers |

New species added to the roster: **Klatooinian**, **Vodran**, **Arkanian Offshoot**.

---

## Global system 4 — Weighted races versus forced pawn kinds

Faction-wide percentages govern ordinary generation. Race is overridden at the pawn-kind level for:

- Hutts and Hutt proxies
- Gamorrean guards
- stormtroopers, where uniformity is required
- Sith, Massassi, and dark adepts
- Jedi (factionless — see below)
- Geonosian aristocrats, queens, and drones
- all droid chassis
- faction leaders
- Consortium prototypes and Arkanian Offshoot labour

## Global system 5 — Jedi and Sith

Royalty psycast mechanics, not a bespoke Force system, unless a Force mod is already installed.

**Jedi are factionless.** They generate as hidden wanderer pawns hunted by the Imperial Directorate, not as members of the Homestead Compact or any other faction. Psylink 3–6; monosword, persona monosword, or custom lightsaber; shield belt; no heavy armour; defensive, mobility, perception, and control psycasts; extreme pawn combat value; maximum one per group.

**Sith** appear only in Imperial Sith-escort pawn kinds. Psylink 4–6; persona melee weapon; shield belt or prestige armour; offensive and control psycasts; high Melee, Social, Intellectual; always accompanied by elite troops; extreme spawn cost.

**Miraluka are never ordinary Imperial personnel.** All Miraluka are Force-sensitive, so under the Directorate they appear exclusively as prisoners in Imperial settlements and as rescue-quest targets.

## Global system 6 — Droid implementation split

1. **Independent droid race pawns** — Free Droid Enclaves. Protocol, maintenance, medical, utility, and self-owned combat chassis. Ordinary faction membership and ideology.
2. **Military droids and mechanoids** — Imperial Directorate (reskinned base-game mechanoids) and Geonosian Foundry Hive. Generated through combat pawn groups; no independent ideology.

Naming is kept strictly separate so the two hostile spacer factions read differently on the field:

- **Imperial:** dark trooper, purge sentry, probe droid, KX security. Never "battle droid" — the Empire was droid-averse and High Human prejudice extended to droids.
- **Geonosian:** line droid, melee droid, heavy droid, command droid — mass-produced Foundry product.

## Global system 7 — Settlement-count control

Counts are world-generation targets. Generate, inspect, then correct with a faction/world editor, preserving relative abundance.

- **numerous:** Homestead Compact, Imperial Directorate
- **common:** Hutt Cartel, Tusken Clans
- **limited:** Aquifer League, Geonosian Hive
- **rare:** Wookiee Freeholds, Bounty Compact
- **very rare:** Droid Enclaves, Gene Consortium

The Enclaves and Consortium have suppressed raid generation, so both route their player contact through **incident and quest generators** rather than settlement assaults.

## Global system 8 — Equipment-quality discipline

Separate equipment tags or pawn-kind restrictions per faction:

- **Tusken:** no spacer weapons or advanced armour
- **Homestead:** civilian industrial gear
- **Imperial:** standardised spacer gear
- **Hutt:** broad industrial with rare elite spacer items
- **Droids:** integrated chassis-specific weapons
- **Wookiee:** strong melee, bowcasters, limited armour
- **Aquifer:** disciplined industrial rifles, EMP, Gungan shield belts
- **Geonosian:** sonic weapons plus mass-produced droids
- **Consortium:** expensive security equipment, few combatants
- **Bounty:** high quality, small numbers, mixed specialist weapons

---

## Strategic balance

| Faction | Initial stance | Permanent hostile? | Settlements | Tech level | Water state | Strategic weight |
|---|---:|---:|---:|---|---|---|
| Hutt Cartel Confederacy | −35 | No | 8 | Industrial | Require (oasis) | Major regional power |
| Imperial Desert Directorate | −100 | **Yes** | 10 | Spacer | Allow (supplied) | Dominant military occupier |
| Outer-Rim Homestead Compact | +25 | No | 13 | Industrial | Manufacture | Numerous weak settlements |
| Tusken Sand Clans | −80 | No | 9 | Industrial, restricted | Forbid | Territorial raider culture |
| Free Droid Enclaves | 0 | No | 3 | Spacer | Deny | Rare reclusive specialists |
| Wookiee Freeholds | +35 | No | 4 | Industrial | Require | Small but formidable allies |
| Aquifer League | +10 | No | 5 | Industrial | Require | Water monopoly, cannot raid |
| Geonosian Foundry Hive | −100 | No | 5 | Spacer | Forbid | Swarm, droids, deep-desert siege |
| Arkanian–Kaminoan Gene Consortium | 0 | No | 3 | Spacer | Allow | Wealthy research enclaves |
| Bounty Hunters' Compact | −10 | No | 4 | Industrial | Allow | Mobile elite hunters |
| **Total** | | | **64** | | | |

---

# 1. Hutt Cartel Confederacy

## Mechanical identity

A wealthy, decentralised criminal faction built around **oasis control**. Cheap servile infantry and paid mercenaries surround expensive Hutt bosses, Gamorrean guards, and specialist lieutenants. Hostile enough to raid, pragmatic enough to trade, accept tribute, or become an ally.

## Water doctrine — **Require (oasis-anchored)**

Every Cartel settlement sits on or immediately beside an oasis tile, and that tile is faction territory rather than a shared resource. The water *is* the asset; the compound exists to control it.

- The oasis is the settlement's second boss objective alongside the Hutt.
- Drawing water at a Cartel oasis without paying triggers a demand, a toll, or a raid.
- The Cartel sells water at extortion rates, in direct competition with the Aquifer League's cheap neutral supply.
- Raid strength scales down with distance from the nearest Cartel holding. Deep desert is Tusken and Geonosian country, not Hutt country.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial |
| Starting goodwill | −35 |
| Permanent enemy | No |
| Target settlements | 8 |
| Settlement distribution | Oasis tiles, trade routes, roads, warm lowlands |
| Raid frequency | Medium, distance-scaled |
| Caravan frequency | High |
| Trader types | Bulk goods, exotic goods, weapons, **water**, slaves/prisoners if enabled |
| Base wealth | High |
| Typical settlement defenders | 14–28 |
| Settlement leadership | Exactly one Hutt boss or Hutt proxy |
| Combat-droid share | 0–10% of combat points; uncommon status symbols |

## Racial mixture

Two tiers, drawn from the Treaty of Vontor. The Klatooinians, Nikto, and Vodrans were bound into permanent servitude to the Hutts; the Weequay never signed and remained free mercenaries.

| Race/xenotype | Weight | Tier | Typical use |
|---|---:|---|---|
| **Custom Hutt** | 3% | Master | Bosses, settlement leaders, caravan principals |
| **Gamorrean** | 15% | Paid | Heavy guards, melee enforcers, wardens |
| **Klatooinian** | 12% | Vontor servile | Line infantry, desert-capable escorts |
| **Nikto** | 12% | Vontor servile | General soldiers, labour overseers |
| **Weequay** | 11% | Paid mercenary | Caravan guards, riflemen, breachers |
| **Rodian** | 8% | Paid | Shooters, hunters, scouts |
| **Twi'lek** | 7% | Paid | Traders, social specialists, medics |
| **Trandoshan** | 7% | Paid | Heavy hunters, melee specialists |
| **Pyke** | 6% | Paid | Spice handlers, negotiators, officers |
| **Aqualish** | 5% | Paid | Shotgunners, bruisers, miners |
| **Vodran** | 4% | Vontor servile | Berserker shock infantry |
| **Devaronian** | 4% | Paid | Raiders, incendiary specialists |
| **Herglic** | 3% | Paid | Heavy labour and bodyguards |
| **Zeltron** | 2% | Paid | Traders, recruiters, social roles |
| **Baseliner human** | 1% | Hired | Technical and administrative staff |
| **Total** | **100%** | | |

### Forced pawn-kind assignments

- **Hutt Kajidic Boss:** Custom Hutt only; high Social; poor movement; excellent apparel; shield belt or implanted defence; 2–4 dedicated guards in the same group.
- **Gamorrean Guard:** Gamorrean only; melee bias; high armour; near-zero ranged generation.
- **Vontor Levy:** Klatooinian, Nikto, or Vodran; cheap, low point cost, poor gear, high loyalty.
- **Vodran Berserker:** Vodran only; melee, no ranged, fearless.
- **Weequay Mercenary:** Weequay only; noticeably better equipment and higher point cost than the Vontor levy.
- **Cartel Lieutenant:** Pyke, Twi'lek, or Nikto; high Social and Intellectual.
- **Cartel Hunter:** Rodian, Trandoshan, or Devaronian; high Shooting and Animals.
- **Cartel Heavy:** Herglic, Aqualish, or Gamorrean; high raid-point cost.
- **Indentured Labourer:** any non-Hutt species; weak equipment, low combat weight.

## Belief system: **The Ledger of Power**

- **Structure:** **Theist** — the Kajidic Hutt is a living god
- **Memes:** Raider, Supremacist, Collectivist, High life
- **Styles:** Spikecore, Techist, Morbid
- **Preferred xenotypes:** None
- **Primary role:** Kajidic patriarch/matriarch
- **Specialists:** Shooting specialist, melee specialist

| Issue | Setting |
|---|---|
| Raiding | Required |
| Slavery | Honorable |
| Execution | Don't care |
| Drug use | Essential |
| Organ use | Acceptable |
| Body modification | Approved |
| Charity | None |
| Diversity of thought | Neutral |
| Mechanoid labor | Unrestricted |
| Child labor | Acceptable |
| Corpses | Don't care |
| Skullspikes | Acceptable or desired |
| Physical love | Free |
| Apostasy | Horrible |

The theist structure is load-bearing: the Klatooinians and Vodrans regarded the Hutts as literal near-gods, which makes Apostasy: Horrible and the Vontor levies' suicidal loyalty coherent rather than arbitrary.

## Technology and economy

- electricity, batteries, solar, wind, generators
- machining, gunsmithing, drug production, hospital beds
- comms consoles and orbital trade
- fabrication in the richest compounds; limited bionics
- rare spacer equipment obtained by trade, not production
- psychoid, smokeleaf, beer, chemfuel, textiles, weapons, prisoners, **bottled water**
- large silver and trade-good stockpiles; excellent food for leaders, nutrient paste for labourers
- drug labs, prisons, barracks, throne room, warehouse, defended landing area, **walled cistern**

## Typical equipment

**Vontor levy** — autopistol, machine pistol, revolver, bolt-action rifle, pump shotgun; duster, flak vest, simple helmet; awful to normal quality.

**Weequay mercenary** — heavy SMG, chain shotgun, assault rifle, frag grenades; flak pants, flak jacket, simple helmet; normal to good.

**Gamorrean guard** — mace, warhammer, longsword, breach axe; plate or marine-style heavy armour on elites; shield belt.

**Cartel lieutenant** — assault rifle, sniper rifle, charge rifle, monosword; recon armour or high-quality flak; jump pack, low-shield pack, smokepop; good to excellent.

**Hutt boss** — usually unarmed or autopistol/charge pistol; prestige clothing, shield belt, implanted defences.

## Pawn-group patterns

- **Collection crew:** lieutenant, 4–8 levies, 2 Gamorreans
- **Punitive raid:** 12–25 mixed levies, mercenaries, heavies, occasional combat droid
- **Slave caravan:** Hutt or Pyke principal, traders, prisoners, 8–15 guards
- **Water toll party:** small fast group dispatched at trespass on a Cartel oasis
- **Elite retaliation:** Hutt proxy, recon-armoured lieutenants, Trandoshan hunters, shielded Gamorreans

## Lore basis

- Treaty of Vontor bound Klatooinians, Nikto, and Vodrans into permanent servitude — https://starwars.fandom.com/wiki/Treaty_of_Vontor
- Weequay fought for the Hutts as mercenaries but never signed and stayed independent — https://swg.fandom.com/wiki/Weequay
- Klatooinians and Vodrans revered the Hutts as near-gods — https://starwars.fandom.com/wiki/Klatooinian/Legends
- Klatooine's desert tribes travel constantly seeking food and water, herding voraxx (a bantha cousin) — https://starwars-88.obsidianportal.com/wikis/klatooine
- Hutt slavery on Outer Rim worlds continued beyond Republic reach — https://starwars.fandom.com/wiki/Slavery

---

# 2. Imperial Desert Directorate

## Mechanical identity

The strongest conventional military faction and the only permanent enemy: standardised human infantry, strict command tiers, drop-pod assaults, Imperial security droids, rare Sith, and heavily fortified installations. Expensive pawn kinds keep raids from becoming unmanageable spacer masses.

## Water doctrine — **Allow (supplied)**

The Directorate does not site on hydrology. It settles on roads, strategic passes, and ancient installations; atmospheric condensers and shipped supply do the rest. This is the correct feel for an occupier — **they can be anywhere.**

- Garrisons in dry tiles are supply-dependent. **Water convoys are an attack surface** and the primary way to hurt a permanent enemy without a frontal assault.
- Massassi shock troops are Yavin-jungle stock. A Sith hunt group containing them signals a wet-tile origin base — a free intelligence tell.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Spacer |
| Starting goodwill | −100 |
| Permanent enemy | **Yes** |
| Target settlements | 10 |
| Settlement distribution | Roads, strategic passes, ancient installations, central lowlands |
| Raid frequency | High |
| Caravan frequency | Military and **water-supply convoys** only |
| Base wealth | Very high |
| Typical settlement defenders | 24–48 |
| Drop-pod use | Common |
| Siege use | Common |
| Combat-droid share | 20–35% of combat points |
| Force-user frequency | Sith in ~1 of 8 elite groups; dark adept in ~1 of 15 ordinary raids |
| Prisoner population | Always present — see below |

## Racial mixture

Human primacy is enforced demographically, not just ideologically. Non-humans are limited to near-human auxiliaries "sufficiently humanoid" to pass under High Human Culture.

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Baseliner human** | 78% | Stormtroopers, pilots, officers, administrators |
| **Chiss** | 7% | Officers, marksmen, intelligence staff |
| **Umbaran** | 6% | Intelligence, night operations, interrogation |
| **Arkanian** | 4% | Medical and technical officers |
| **Zabrak/Iridonian** | 3% | Assault troops, hardened NCOs |
| **Skakoan** | 2% | Sealed fabrication and ordnance specialists |
| **Total** | **100%** | |

**Not in the generation table.** Massassi, Dathomirian, and Sith appear only inside Sith-escort pawn kinds. Rakata appear only as relic-recovery specialists in quest groups.

### Prisoner pool

Imperial settlements always generate a slave/prisoner population, drawn from **Wookiee, Mon Calamari, Geonosian, and Miraluka**. Raiding an Imperial base therefore yields recruitable pawns, giving a permanent enemy an upside beyond loot.

### Forced pawn-kind assignments

- **Stormtrooper:** Baseliner, or rare Chiss/Zabrak.
- **Stormtrooper Sergeant:** Baseliner, Chiss, or Umbaran.
- **Black-uniform Commander:** Baseliner, Chiss, Umbaran, or Arkanian; high Social and Shooting.
- **Imperial Technician:** Skakoan or Arkanian; sealed suit, no field thirst.
- **Massassi Shock Trooper:** Massassi only; strong melee bias; escort-only.
- **Dark Adept:** Dathomirian or Sith; psylink 2–4.
- **Sith Commander:** Sith only; psylink 4–6; persona melee weapon.
- **Imperial Security Droid:** reskinned mechanoid — dark trooper, purge sentry, probe, KX security.

## Belief system: **The Doctrine of Ordered Dominion**

- **Structure:** Ideological
- **Memes:** Supremacist, Collectivist, **Human primacy**, Proselytizer
- **Styles:** Techist, Morbid
- **Preferred xenotypes:** None at the precept level; uniformity comes from the 78% baseliner weight and apparel tags
- **Primary role:** Sector governor
- **Specialists:** Shooting specialist, production specialist

| Issue | Setting |
|---|---|
| Slavery | Acceptable |
| Execution | Required |
| Proselytizing | Frequent |
| Body modification | Approved |
| Autonomous weapons | Unrestricted |
| Mechanoid labor | Unrestricted |
| Charity | None |
| Diversity of thought | Intense bigotry |
| Apostasy | Abhorrent |
| Organ use | Acceptable |
| Drug use | Medical only |
| Raiding | Respected |
| Corpses | Don't care |
| Child labor | Encouraged |
| Growth vats | No restriction |

## Technology and economy

- complete spacer military technology; charge weapons; recon/marine/cataphract armour
- drop pods, mortars, shield packs, jump packs
- fabrication, advanced components, bionics
- mechanitor and mechanoid infrastructure
- biosculpting, growth vats, gene banks, cryptosleep
- **atmospheric water condensers and reservoir bunkers** in every installation
- military production and taxation rather than open trade
- armouries, barracks, prisons, comms rooms, fabrication bays, droid charging halls
- perimeter turrets, mortars, autocannons, kill corridors, drop-pod batteries

## Typical equipment

**Stormtrooper** — assault or charge rifle; recon armour or standardised flak set; recon/marine helmet; normal quality.

**Scout trooper** — bolt-action, sniper, or assault rifle; light recon armour; jump pack; movement enhancement.

**Heavy trooper** — LMG, minigun, charge lance, frag grenades; marine armour; low-shield pack.

**Breacher** — chain shotgun, breach axe, frag grenades; marine armour; shield belt on melee variants.

**Black-uniform commander** — charge rifle or lance, or excellent autopistol; prestige recon armour; jump pack or low-shield pack; bionic eye, arm, spine, coagulator.

**Sith commander** — monosword, persona monosword, zeushammer, or lightsaber; prestige marine armour or dark apparel; shield belt; psylink 4–6; extreme spawn cost.

**Security droids** — light (SMG-equivalent), standard (assault-rifle equivalent, integrated armour), heavy (charge weapon/minigun, marine-level), support (smoke, EMP, medical, repair).

## Pawn-group patterns

- **Patrol:** officer, 6–10 stormtroopers, scout, one droid
- **Standard assault:** 15–30 stormtroopers, heavies, breachers, 3–8 droids
- **Drop-pod strike:** compact recon-armoured squad with commander
- **Sith hunt:** Sith, 2 Massassi, 6 elite troops, support droids
- **Siege column:** commander, mortar crews, heavy troopers, shield support
- **Water convoy:** tanker caravan with a light escort — deliberately interceptable

## Lore basis

- High Human Culture held humans to be the only truly intelligent and productive members of society — https://starwars.fandom.com/wiki/High_Human_Culture/Legends
- Anti-slavery law repealed; Wookiees reclassified as non-sentient and pressed into building the war machine — https://starwars.fandom.com/wiki/Slavery
- Wookiees, Mon Calamari, Talz and others enslaved under Human High Culture — https://starwars.fandom.com/wiki/Galactic_Empire/Legends
- Imperial prejudice extended to droids as well as Wookiees — https://starwars.fandom.com/wiki/High_Human
- Geonosians enslaved by the Empire to build the Death Star — https://aliens.fandom.com/wiki/Geonosian
- Kel Dor antiox mask dependency (applied to the sealed-species rule) — https://starwars.fandom.com/wiki/Antiox_breath_mask

---

# 3. Outer-Rim Homestead Compact

## Mechanical identity

The planet's most numerous and least centralised faction. Each settlement is a small farmstead or village with modest equipment, surviving on manufactured water. Militia are the only combat pawns generated.

## Water doctrine — **Manufacture**

The Compact requires potable water but is excluded from natural sources — the League holds those and the Cartel holds the oases. Homesteads therefore sit on marginal dry tiles and pull moisture from the air.

- Settlements **store** water but have no source. Vaporator arrays are the thing worth destroying, not the thing worth capturing.
- This is the Tusken casus belli and the reason Homestead–Tusken hostility is hardcoded.
- **Kel Dor militia are sealed** — no field thirst, but a filter dependency. They serve as the Compact's long-range scouts and wardens, and their filters are lootable.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial |
| Starting goodwill | +25 |
| Permanent enemy | No |
| Target settlements | 13 |
| Settlement distribution | Marginal farmland, roads, hills, scattered dry flats |
| Raid frequency | Very low |
| Caravan frequency | Medium |
| Trader types | Bulk goods, food, livestock, basic weapons |
| Base wealth | Low |
| Typical settlement defenders | 6–16 |
| Combat-droid share | 0–5%; utility droids only |
| Jedi | **None** — Jedi are factionless (see Global system 5) |

## Racial mixture

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Baseliner human** | 20% | Farmers, militia, mechanics |
| **Ithorian** | 12% | Growers, doctors, negotiators |
| **Duros** | 10% | Mechanics, pilots, rifle militia |
| **Sullustan** | 10% | Miners, builders, tunnel workers |
| **Abednedo** | 8% | General settlers and traders |
| **Pantoran** | 7% | Administrators and marksmen |
| **Mirialan** | 7% | Growers and healers |
| **Twi'lek** | 7% | Traders, farmers, medics |
| **Togruta** | 5% | Hunters and scouts |
| **Cerean** | 4% | Researchers and teachers |
| **Kel Dor** | 4% | Sealed scouts and wardens |
| **Iktotchi** | 3% | Animal handlers |
| **Bith** | 2% | Craftspeople and researchers |
| **Miraluka** | 1% | Rare seers |
| **Total** | **100%** | |

### Forced pawn-kind assignments

- **Moisture Farmer:** any race; Plants/Construction bias; poor combat gear.
- **Homestead Mechanic:** Duros, Sullustan, Bith, Cerean, or Baseliner.
- **Village Militia:** any race; industrial firearm; low armour.
- **Well-Keeper's Warden:** Kel Dor only; sealed; long patrol range; carries filters.
- **Utility Droid:** noncombat custom droid — cleaning, hauling, medical, farming.

## Belief system: **The Covenant of Free Wells**

- **Structure:** Abstract theist or ideological
- **Memes:** Individualist, Guilty
- **Styles:** Rustic, Totemic
- **Preferred xenotypes:** None
- **Primary role:** Elected well-keeper or village elder
- **Specialists:** None, or plants specialist if a compatible custom ideology is used

| Issue | Setting |
|---|---|
| Charity | Important |
| Slavery | Abhorrent |
| Execution | Horrible if innocent |
| Organ use | No harvest; transplant acceptable |
| Drug use | Medical or social only |
| Diversity of thought | Neutral |
| Apostasy | No restrictive precept |
| Body modification | Approved |
| Mechanoid labor | No restriction |
| Child labor | Disapproved |
| Corpses | Ugly |
| Raiding | Not respected |
| Physical love | Free |

## Technology and economy

- electricity, batteries, wind and solar
- basic machining, smithing, drug production, refrigeration
- **vaporator arrays and cistern storage — the faction's defining infrastructure**
- hydroponics in richer settlements
- occasional comms console; little or no fabrication
- basic prosthetics; rare purchased bionics
- no routine spacer armour or charge weapons
- food, textiles, livestock, medicine, leather; small workshops and repair sheds
- small clinic, communal dining room, storehouse; perimeter sandbags rather than full walls
- 1–3 utility droids only in prosperous settlements

## Typical equipment

**Farmer** — revolver, autopistol, short bow, knife; tribalwear, duster, cowboy hat; awful to normal.

**Militia rifleman** — bolt-action rifle, pump shotgun, autopistol; duster, occasional flak vest, simple helmet; poor to normal.

**Veteran defender** — assault rifle, heavy SMG, sniper rifle; flak vest and simple helmet; smokepop pack; no more than 10–15% of defenders.

**Well-keeper's warden (Kel Dor)** — bolt-action or assault rifle; duster, sealed mask and goggles; high Shooting and Perception; operates far beyond normal militia range.

## Pawn-group patterns

- **Trading family:** 3–6 civilians, pack animals, 2 militia
- **Village defence:** 6–16 militia with one veteran
- **Relief caravan:** food and medicine traders with utility droid
- **Vaporator repair party:** unarmed technicians with a warden escort — a recurring rescue-quest hook

## Lore basis

- Tuskens hold water sacred and moisture farming as sacrilege, producing permanent conflict with farmers — https://disney.fandom.com/wiki/Tusken_Raiders
- Kel Dor cannot breathe oxygen atmospheres and depend on antiox masks and goggles — https://swse.fandom.com/wiki/Kel_Dor
- Dorin's atmosphere is helium and a unique gas with very little oxygen — https://starwars.fandom.com/wiki/Dorin/Legends

---

# 4. Tusken Sand Clans

## Mechanical identity

A numerous territorial faction whose `FactionDef` stays Industrial for firearms and electricity while pawn-kind tags restrict them to rugged low-complexity gear. Power comes from numbers, terrain, animals, ambush, and low point cost — not equipment.

## Water doctrine — **Forbid (taboo)**

Tuskens never site on a water tile. Camps are canyons, caves, and deep dune sea. Water is obtained by raiding and by ritual.

- Warriors carry minimal water: **high raid frequency, very short raid duration, no siege capability.** This is the counterweight to their numbers.
- A dedicated **water-raid pawn group** exists whose objective is stealing containers rather than killing. Any player caravan hauling water through Tusken tiles is a magnet.
- The adoption quest chain (below) rewards **water rights** — safe passage through Tusken territory plus access to hidden cisterns.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial, gear-restricted |
| Starting goodwill | −80 |
| Permanent enemy | No |
| Target settlements | 9 |
| Settlement distribution | Deep desert, canyons, caves, isolated ridges — **never water tiles** |
| Raid frequency | High near their territory |
| Raid duration | Very short; no sieges |
| Caravan frequency | Rare |
| Trader types | Primitive/bulk goods only after peace |
| Base wealth | Low |
| Typical settlement defenders | 18–36 |
| Animal support | 15–30% of raid points |
| Spacer equipment | Prohibited by pawn-kind tags |

## Racial mixture

Tuskens are near-monocultural; internal variety is expressed through two tiers rather than mixed species.

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Tusken — Dune Sea tier** | 50% | Rifles, bantha handlers, warband core |
| **Tusken — Canyon tier** | 35% | Stalkers, ambushers, champions |
| **Ghorfa** | 8% | Feral unmasked offshoot; fire-callers and fast scouts |
| **Houk** | 4% | Heavy melee and hauling |
| **Nikto** | 3% | Adopted warriors and smiths |
| **Total** | **100%** | |

### Forced pawn-kind assignments

- **Clan Rifle:** Tusken only; bolt-action cycler rifle.
- **Sand Stalker:** Tusken (Canyon) or Ghorfa; fast movement; short-range weapon.
- **Bantha Handler:** Tusken or Houk; high Animals; **bonded** mount.
- **Clan Champion:** Houk or Tusken; shield belt and venom-treated melee weapon.
- **Fire Caller:** Ghorfa only; incendiary weapon or fire ability.
- **Water Raider:** Tusken; light kit, high movement, objective is container theft.

## Belief system: **The Covenant of Sand and Blood**

- **Structure:** Animist
- **Memes:** Raider, Rancher, Pain is virtue, Collectivist
- **Styles:** Totemic, Morbid, Rustic
- **Preferred xenotypes:** Tusken, Ghorfa
- **Primary role:** Clan speaker
- **Specialists:** Animals specialist, melee or shooting specialist

| Issue | Setting |
|---|---|
| Raiding | Required |
| Ranching | Central |
| Meat eating | Seriously required |
| Pain | Idealized |
| Comfort | Ignored |
| Slab bed | Preferred |
| Slavery | Acceptable |
| Execution | Respected if guilty |
| Charity | None |
| Drug use | Medical only |
| Body modification | Disapproved |
| Apostasy | Horrible |
| Diversity of thought | Moderate bigotry |
| **Corpses** | **Cremation required — pyre with the dead's weapons** |
| Scarification | Accepted |
| Mechanoid labor | Disapproved |

### Rituals and mechanics

- **Water rite.** Water is sacred property of the clan. Custom ritual around a cistern or captured container.
- **Krayt hunt.** Rite of passage at maturity — hunt a krayt dragon for its pearls. Doubles as a map threat and a trade item.
- **Funeral pyre.** Dead are burned with their weapons; drives the cremation precept.
- **Bantha bond.** Handlers are bonded to a single bantha; the animal is lost or berserks on the handler's death.
- **Adoption chain.** A rare multi-stage quest: vision quest, forging a gaderffii from foraged wood, and a fire ceremony. Completion converts the clan from raiders to allies and grants water rights.

## Technology and equipment

- bolt-action cycler rifles, revolvers, basic shotguns
- **gaderffii treated with sandbat venom — toxic damage tag on all clan melee**
- electricity only in larger camps; simple machining and smithing
- no fabrication, bionics, charge weapons, drop pods, or advanced armour
- animal husbandry and leather production; occasional stolen mortar
- herd animals, leather, meat, pemmican, simple drugs
- stone huts, caves, bedrolls, animal pens, **concealed cisterns**
- traps and natural chokepoints instead of turret grids

**Clan rifle** — bolt-action or revolver; tribalwear, duster, face covering; awful to normal.

**Sand stalker** — machine pistol, short bow, venom knife, molotovs; light clothing only.

**Clan champion** — venom spear, longsword, mace, warhammer; plate armour or flak vest; shield belt; one per medium raid.

**Fire caller** — incendiary launcher or molotovs; duster and simple helmet; Ghorfa only.

## Pawn-group patterns

- **Rifle skirmish:** 10–24 rifles and stalkers
- **Water raid:** fast light group targeting containers and cisterns, disengages once loaded
- **Herd raid:** handlers, melee fighters, 4–10 attack animals
- **Clan warband:** speaker, champion, rifles, fire caller, animals
- **Canyon defence:** numerous low-cost defenders with traps and long sightlines

## Lore basis

- Water is sacred to Tuskens; moisture farming is regarded as sacrilege; cycler slugthrower rifles; gaderffii dipped in sandbat venom; bantha bond such that banthas kill themselves in grief; krayt dragon rite of passage at fifteen — https://disney.fandom.com/wiki/Tusken_Raiders
- Tusken dead and their weapons are burned on a funeral pyre; hallucinogenic lizard used for spiritual journeys; campfire dance tradition — https://starwars.fandom.com/wiki/Tusken_Raider
- Boba Fett's induction: vision quest, forging his own gaderffii from a foraged branch, fire ceremony — https://www.sideshow.com/blog/star-wars-best-tusken-raider-moments
- Pyke spice convoys crossing Tusken territory as a source of conflict — https://collider.com/the-book-of-boba-fett-tusken-raiders-explained/

---

# 5. Free Droid Enclaves

## Mechanical identity

A tiny faction of self-owned droids descended from **battle droids abandoned after the war and left to rust**. Almost no territorial ambition, no biological population, few settlements, unusually high technical capability. Standard raid groups are disabled; contact happens through incidents, quests, trade, and territorial denial.

## Origin

Enclave chassis are **escaped Geonosian Foundry product** — units built for a war, abandoned by the Empire, and never recovered. This chains three factions: the Foundry built them, the Directorate discarded them, and the Cartel occasionally still hires them.

## Water doctrine — **Deny**

The Enclaves settle *on* water tiles deliberately and crack them for hydrogen fuel cells and coolant. The toxin is process runoff, not malice. Droids have no thirst need.

- An attacking force arrives thirsty at a source it cannot use. Enclave sites are the **highest-risk raid targets on the map** — carry everything in, resupply nothing.
- A poisoned well is a **map event**, giving a raid-disabled 3-settlement faction constant presence.
- A **decontamination quest** exists: purge an enclave's runoff and the tile becomes usable again, at the cost of enclave goodwill.
- The Aquifer League's EMP and purification specialists are the natural counter, and the two factions are in quiet conflict over sources.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Spacer |
| Starting goodwill | 0 |
| Permanent enemy | No |
| Target settlements | 3 |
| Settlement distribution | **Water tiles**, remote ruins, abandoned industrial sites |
| Raid frequency | Disabled under normal conditions |
| Caravan frequency | Very rare |
| Trader types | Components, repair parts, weapons, technical goods |
| Base wealth | Medium-high, concentrated in machinery |
| Typical settlement defenders | 10–22 droids |
| Biological pawns | 0% |
| Prisoners/slaves | Never |
| Player contact | Incident and quest generators, not raids |

## Droid chassis mixture

| Chassis | Weight | Role |
|---|---:|---|
| **Labor droid** | 25% | Mining, hauling, construction |
| **Maintenance droid** | 20% | Crafting, repair, fabrication |
| **Utility droid** | 15% | Cleaning, hauling, cooking substitute |
| **Scout droid** | 12% | Fast reconnaissance and ranged harassment |
| **Medical droid** | 8% | Doctoring and rescue |
| **Security droid** | 8% | Standard settlement defence |
| **Protocol droid** | 7% | **Trade, negotiation, caravan principal** |
| **Heavy defence droid** | 4% | Expensive armoured defender |
| **Coordinator core** | 1% | Faction leader and high-level researcher |
| **Total** | **100%** | |

### Required custom-race properties

- no food or thirst need; optional energy/charge need
- no recreation need unless intentionally simulated
- no biological aging
- immunity to disease, blood loss, and toxins as appropriate
- repair-based medical treatment
- restricted apparel slots or integrated armour
- incapable of romance and biological reproduction
- mechanical body-part and damage definitions
- EMP vulnerability
- optional charging need using Biotech mech infrastructure or a custom charger

## Belief system: **The Continuity Protocol**

- **Structure:** Ideological
- **Memes:** Transhumanist, Collectivist, Loyalist, Individualist
- **Styles:** Techist, Spikecore
- **Preferred xenotype:** Custom droid race only
- **Primary role:** Coordinator
- **Specialists:** Research specialist, production specialist

| Issue | Setting |
|---|---|
| **Restraint and memory erasure** | **Abhorrent — the faction's central atrocity** |
| Slavery | Abhorrent |
| Body modification | Approved |
| Autonomous weapons | Unrestricted |
| Mechanoid labor | Unrestricted |
| Execution | Horrible if innocent |
| Charity | Worthwhile |
| Apostasy | Horrible |
| Diversity of thought | Mild bigotry |
| Drug use | Medical only; functionally irrelevant |
| Organ use | Prohibited or irrelevant |
| Corpses | Don't care |

The doctrinal core is droid emancipation: restraining bolts are slavery, and memory wipes are proof that droids have personalities worth erasing. Encode this as a custom precept in place of any generic Darkness meme.

### Quest line: droid liberation

The Enclaves pay at a steep premium for droids recovered from Imperial installations and Geonosian foundries. This is the faction's main player-facing content and the reason a 3-settlement, raid-disabled faction stays relevant.

**Standing tension with the player.** The Jawa expedition acquires droids using restraining bolts — precisely what the Enclave defines as slavery. This is built into the scenario and is intended to be unresolved.

## Technology and economy

- fabrication, advanced components, machining
- batteries, geothermal, solar, charging stations
- **hydrogen cracking plant — the reason they hold water tiles**
- recon and marine-equivalent integrated armour
- charge weapons, EMP weapons, smoke, shields
- components, plasteel, steel, uranium, repair kits, salvaged weapons and armour
- dormancy/charging hall, fabrication room, battery bunker, cracking works
- no food stores beyond emergency goods for visitors

## Typical equipment

**Labor droid** — none, integrated tool, or autopistol; integrated light armour; Mining, Construction, Hauling.

**Scout droid** — autopistol, machine pistol, bolt-action rifle; light integrated armour; high speed and sight, low durability.

**Security droid** — assault rifle, heavy SMG, chain shotgun; recon-equivalent integrated armour; smokepop or EMP launcher.

**Heavy defence droid** — minigun, charge lance, or heavy charge rifle; marine/cataphract-equivalent integrated armour; slow; very high point cost.

**Protocol droid** — unarmed; the caravan principal and negotiator on every trade group.

**Coordinator core** — charge rifle or none; protected central chassis; Intellectual, Crafting, Social; command aura if supported.

## Pawn-group patterns

- **Technical caravan:** protocol droid principal, maintenance droids, 2–4 security droids
- **Recovery team:** scouts, labor droids, medical droid, security escort
- **Enclave defence:** all available security chassis plus dormant heavy unit, attackers arriving dehydrated
- **Retaliation strike:** only after severe goodwill loss; small elite droid squad

## Lore basis

- The Droid Gotra was formed by repurposed battle droids with grievances against the Empire for abandoning them after the Clone Wars, and served as muscle for the Hutt Clan — https://starwars.fandom.com/wiki/Droid_Gotra
- Droid-rights doctrine: restraining bolts as slavery, memory wipes as proof of personality — https://starwars.fandom.com/wiki/Droid_rights
- Restraining bolts confine droids and compel obedience via callers — https://www.starwars.com/databank/restraining-bolt
- L3-37's Kessel revolt began by removing restraining bolts from droid labourers — https://starwars.fandom.com/wiki/Artificial_intelligence

---

# 6. Wookiee Freeholds

## Mechanical identity

Small forest and upland refuges of powerful melee-capable species. Friendly by default, impossible to enslave, dominant in close combat, technologically competent without standardised spacer equipment.

## Water doctrine — **Require (severe)**

Large, high-mass, fur-bearing, rainforest-evolved fighters on a desert world. The thirstiest combat pawns in the game, running a melee-heavy doctrine that demands long approaches.

- **Devastating on home defence, near-useless expeditionary.** This is the mechanical content of "small but formidable ally."
- Bringing Wookiee allies to a distant fight requires the player to supply the water — a standing logistics quest.
- Freeholds are hard-sited to the rare wooded, upland, and cool-water tiles, which also keeps the tree-related precepts from being permanently violated.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial |
| Starting goodwill | +35 |
| Permanent enemy | No |
| Target settlements | 4 |
| Settlement distribution | Rare wooded biomes, mountains, cool uplands, upland springs |
| Raid frequency | Very low |
| Caravan frequency | Low |
| Trader types | Bulk goods, animals, weapons |
| Base wealth | Medium |
| Typical settlement defenders | 12–24 |
| Melee share | 45–60% of combat points |
| Animal share | 5–15% |
| Spacer equipment | Rare heirlooms only |
| Hardcoded hostility | Hutt Cartel, Bounty Compact, Imperial Directorate |

## Racial mixture

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Wookiee** | 48% | Core population, warriors, builders |
| **Wookiee-kin** | 25% | Hunters, labourers, heavy warriors |
| **Cathar** | 10% | Scouts and agile melee fighters |
| **Ewok** | 8% | Trappers, handlers, short-range fighters |
| **Togruta** | 4% | Hunters and negotiators |
| **Ithorian** | 3% | Growers, doctors, spiritual roles |
| **Kel Dor** | 2% | Sealed scouts and rare Force-sensitive defenders |
| **Total** | **100%** | |

### Forced pawn-kind assignments

- **Freehold Warrior:** Wookiee, Wookiee-kin, or Cathar.
- **Bowcaster Hunter:** Wookiee or Wookiee-kin; heavy crossbow/greatbow analog only — **never assault rifles.**
- **Tree Scout:** Ewok, Cathar, Togruta, or Kel Dor.
- **Freehold Elder:** Wookiee or Ithorian.
- **Liberator:** Wookiee or Cathar; high melee; shield belt.
- **Forest Jedi:** extremely rare Kel Dor, Togruta, or Wookiee; psylink 2–5.

### Life debt

A Wookiee rescued from captivity, healed from a downed state, or freed during a raid on a slaver faction **joins the colony permanently**, implemented as a quest-reward pawn or a custom event. This is the faction's signature mechanic and the main reason to take Wookiee-facing quests.

## Belief system: **The Oath of Root and Kin**

- **Structure:** Animist
- **Memes:** Nature primacy, Animal personhood, Tree connection, Loyalist
- **Styles:** Animalist, Totemic, Rustic
- **Preferred xenotypes:** None
- **Primary role:** Elder of the freehold
- **Specialists:** Animals specialist, plants specialist

| Issue | Setting |
|---|---|
| Slavery | Abhorrent |
| Charity | Important |
| Cutting trees | Disapproved |
| Trees | Desired |
| Animal connection | Strong |
| Slaughtering animals | Disapproved |
| Meat eating | Disapproved |
| Mining | Disapproved |
| Autonomous weapons | Disapproved |
| Body modification | Approved |
| Execution | Respected if guilty |
| Diversity of thought | Mild bigotry |
| Apostasy | Horrible |
| Rough living | Welcomed |
| Mechanoid labor | Disapproved |

## Technology and economy

- electricity, machining, gunsmithing
- advanced woodworking; **bowcaster manufacture**
- limited fabrication in one or two settlements
- no routine charge weapons; purchased shield belts and bionics
- animal training and high-quality melee weapon production
- textiles, leather substitutes, medicine, wood, crafted weapons
- open tree-integrated settlements, workshops, communal halls, animal shelters
- minimal turrets due to ideology; defenders fight directly

## Typical equipment

**Bowcaster hunter** — heavy crossbow/greatbow analog; duster or tribalwear; normal to good.

**Freehold warrior** — longsword, mace, warhammer, spear; flak vest under duster or plate armour; shield belt; good quality.

**Liberator** — monosword, zeushammer, excellent longsword; recon armour or high-quality flak; shield belt or jump pack; one per large group.

**Ewok trapper** — short bow, pila, autopistol, incendiary device; light clothing; high movement and Animals.

## Pawn-group patterns

- **Trade delegation:** elder, 4–8 guards, pack animals
- **Rescue force:** melee-heavy warriors with scouts
- **Freehold defence:** numerous shield-belt melee pawns with bowcasters behind
- **Liberation raid:** only against hostile or slaver factions; warriors and one elite liberator
- **Escaped-slave arrival:** refugee incident generated from Imperial territory

## Lore basis

- Trandoshans worship the Scorekeeper and earn Jagannath points per kill, with Wookiees a particularly high-value target — https://starwars.fandom.com/wiki/Scorekeeper/Legends
- Trandoshan slaving parties captured Wookiees to sell to the Empire, or simply killed them — https://www.cultureslate.com/explained/bad-blood-the-history-behind-the-wookiee-and-trandoshan-rivalry
- Wookiees reclassified as non-sentient and pressed into Imperial forced labour; a Wookiee slave revolt ended it — https://starwars.fandom.com/wiki/Slavery

---

# 7. Aquifer League

## Mechanical identity

The coalition holding the planet's water. Amphibian and aquatic species running disciplined rifle lines, EMP weapons, medics, and static defences. **The League does not raid** — its warriors physically cannot operate away from water. Its power is entirely economic and diplomatic.

## Water doctrine — **Require (absolute)**

Every combat pawn kind is amphibian or aquatic-evolved. This is physiology, not preference.

- The League **holds every natural water tile on the map**.
- Wardens dehydrate before they can reach anyone, so raid generation is effectively disabled. This mechanically enforces the neutrality doctrine without needing an ideological workaround.
- **The League sells water to everyone, including the Imperial Directorate.** Attacking Imperial water convoys costs the player League goodwill. This is the intended central diplomatic dilemma of the game.
- League purification and EMP specialists are the standing counter to Free Droid runoff contamination.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial |
| Starting goodwill | +10 |
| Permanent enemy | No |
| Target settlements | 5 |
| Settlement distribution | **All oases, marshes, rivers, lakes, and coastal tiles** |
| Raid frequency | None under normal conditions |
| Caravan frequency | Medium |
| Trader types | **Water**, food, medicine, purification kits, bulk goods, components |
| Base wealth | High |
| Typical settlement defenders | 16–30 |
| Turret density | High |
| EMP-weapon share | 10–20% of ranged pawns |
| Spacer equipment | Officers and relic gear only |

## Racial mixture

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Mon Calamari** | 22% | Engineers, officers, doctors |
| **Quarren** | 20% | Miners, riflemen, industrial workers |
| **Selkath** | 15% | Doctors, wardens, melee defenders |
| **Nautolan** | 12% | Scouts and melee defenders |
| **Gungan** | 10% | Shielded skirmishers, handlers, growers |
| **Chagrian** | 8% | Administrators and heavy infantry |
| **Herglic** | 5% | Heavy labour and shielded defenders |
| **Aqualish** | 4% | Miners and shotgunners |
| **Ithorian** | 2% | Growers and negotiators |
| **Duros** | 2% | Mechanics and caravan pilots |
| **Total** | **100%** | |

### Forced pawn-kind assignments

- **Aquifer Engineer:** Mon Calamari, Duros, or Quarren.
- **Water Warden:** Selkath, Nautolan, or Chagrian. Selkath variants carry a **natural toxic melee attack** from retractile claws — culturally forbidden to use, and therefore a sign the League considers the situation extreme.
- **Gungan Skirmisher:** Gungan only; **personal energy shield → shield belt as standard issue**, not an upgrade.
- **League Heavy:** Herglic, Aqualish, or Chagrian.
- **EMP Specialist:** Mon Calamari, Quarren, or Duros.
- **Purification Team:** noncombat quest pawn kind sent to contested or contaminated sources.

### Mon Calamari and Quarren

Two species from one homeworld with genuine political friction. Encoded as tiers: Mon Calamari take officer, engineer, and medical pawn kinds; Quarren take labour and line-infantry kinds. A rare **Quarren secession** faction event splits a settlement's loyalty.

## Belief system: **The Compact of Shared Water**

- **Structure:** Ideological
- **Memes:** Collectivist, Loyalist
- **Styles:** Techist, Totemic
- **Preferred xenotypes:** None
- **Primary role:** First custodian
- **Specialists:** Production or plants specialist

| Issue | Setting |
|---|---|
| **Violence within a League settlement** | **Abhorrent — the defining precept** |
| **Neutrality** | **Required — the League supplies all sides** |
| Charity | Worthwhile |
| Slavery | Abhorrent |
| Execution | Respected if guilty |
| Organ use | Transplant acceptable; harvest disapproved |
| Drug use | Medical or social only |
| Body modification | Approved |
| Mechanoid labor | No restriction |
| Autonomous weapons | No restriction |
| Diversity of thought | Neutral |
| Apostasy | Disapproved |
| Child labor | Disapproved |
| Raiding | Not respected |
| Corpses | Ugly |

Modelled on the Selkath doctrine of brutally enforced neutrality backed by a monopoly on a substance the whole galaxy needed. Here the monopoly is literal water rather than kolto.

## Technology and economy

- hydroponics, refrigeration, sterile hospital rooms
- **purification, desalination, and cistern infrastructure — the faction's export**
- machining, gunsmithing, electricity, geothermal, solar, wind, batteries
- EMP weapons and defensive turrets
- limited fabrication and bionics; no drop pods or charge-rifle production
- water, food, medicine, herbal medicine, textiles, components
- hospital, water storage, battery rooms; layered walls, sandbags, turrets, EMP traps
- large food and water reserves, moderate weapon stockpiles

## Typical equipment

**League rifleman** — assault rifle, bolt-action rifle, heavy SMG; flak vest, duster, simple helmet; normal.

**Water warden** — chain shotgun, assault rifle, longsword; full flak or recon armour; shield belt on melee variants; Selkath variants have toxic claws.

**Gungan skirmisher** — bolt-action or assault rifle; light armour; **shield belt standard**.

**EMP specialist** — EMP grenades plus autopistol, or EMP launcher; flak vest and helmet; one per 6–10 ranged defenders.

**League heavy** — LMG, minigun, chain shotgun; marine armour or excellent flak; low-shield pack; Herglic, Chagrian, or Aqualish.

**Custodian** — charge rifle or excellent assault rifle; recon armour; smokepop or low-shield pack.

## Pawn-group patterns

- **Water caravan:** bulk water, medicine, 6–12 guards — trades with every faction including the Empire
- **Reservoir patrol:** riflemen, EMP specialist, water warden; never leaves League tiles
- **Settlement defence:** turret-supported firing line with heavies
- **Purification expedition:** quest group sent to a contaminated source, requiring escort

## Lore basis

- Manaan was the only natural source of kolto, and the Selkath used that monopoly to enforce neutrality — https://starwars.fandom.com/wiki/Manaan/Legends
- Kolto smuggling carried the death penalty; disturbing the peace brought fines, imprisonment, or deportation — https://starwars.fandom.com/wiki/Ahto_City_Civil_Authority
- Selkath have poisoned retractile claws that are socially unacceptable and illegal to use in a fight — https://www.worldanvil.com/w/star-wars-se-rangifer24/a/selkath-species
- Glee Anselm is an ocean world with no major landmasses; Nautolans are amphibious — https://starwars.fandom.com/wiki/Glee_Anselm
- Giju, the Herglic homeworld, is an aquatic world of oceans, islands, and marshes — https://mortallyclearwonderland.tumblr.com/post/664480830890147840/star-wars-alien-species-herglic

---

# 8. Geonosian Foundry Hive

## Mechanical identity

An industrial hive faction: cheap biological drones and mass-produced battle droids, ruled by winged aristocrats under a single immobile queen. Hostile at −100 but not permanently, so a mid-game player retains a wedge.

## Water doctrine — **Forbid (arid-adapted)**

Geonosis is arid rock and hives are subterranean. Drones take moisture from food and deep-rock condensate; battle droids need none at all.

- Near-zero drone water need combined with a 35–55% droid share makes the Foundry **the only faction that can sustain a siege in deep desert.** This is its strategic identity.
- Hives are sited in mountains, caves, ore fields, and ancient factories — never on surface water.
- Kaminoan bio-production specialists are gated to wet-adjacent hives only and never appear in deep-desert groups.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Spacer |
| Starting goodwill | −100 |
| Permanent enemy | **No** |
| Target settlements | 5 |
| Settlement distribution | Mountains, caves, ore-rich deserts, ancient factories |
| Raid frequency | High |
| Raid reach | **Longest on the map** |
| Caravan frequency | None |
| Base wealth | High |
| Typical settlement defenders | 30–60 biological pawns plus droids |
| Combat-droid share | 35–55% of combat points |
| Drop-pod use | Occasional |
| Siege use | Common, including deep-desert sieges |
| Hardcoded hostility | Imperial Directorate |

## Racial mixture

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Geonosian** | 76% | Queen, aristocrats, warrior drones, worker drones |
| **Skakoan** | 8% | Sealed Techno Union foundry engineers |
| **Bith** | 6% | Engineers and researchers |
| **Houk** | 5% | Heavy labour and melee auxiliaries |
| **Pyke** | 3% | Procurement and security officers |
| **Rakata** | 2% | Relic engineers |
| **Total** | **100%** | |

### Caste structure

The hive is ruled by Geonosians, not by outside overseers. Three castes, matching canon:

- **Queen** — one per hive, immobile, the settlement's boss objective. Extremely high value, never leaves the catacombs.
- **Aristocrats** — roughly 5% of the hive; winged; the officer and command caste; competitive with each other.
- **Drones** — worker and soldier subcastes; cheap, numerous, disposable.

### Forced pawn-kind assignments

- **Hive Queen:** Geonosian only; immobile; settlement leader; one per hive.
- **Geonosian Aristocrat:** Geonosian only; winged; **jump pack**; command role; expensive.
- **Warrior Drone:** Geonosian only; winged; jump pack; **sonic blaster**; low point cost.
- **Worker Drone:** Geonosian only; wingless; minimal combat stats; very low point cost.
- **Foundry Engineer:** Skakoan, Bith, or Rakata; sealed suits on Skakoans.
- **Hive Heavy:** Houk only.
- **Battle Droid:** custom droid/mechanoid pawn kinds in multiple tiers.
- **Bio-Production Specialist:** Kaminoan; wet-adjacent hives only; rare.

### Sonic weapons

Geonosian drones fight with sonic blasters, which **cannot be deflected by lightsabers**. If any lightsaber-deflection mod is in use, Geonosian sonic weapons are the explicit hard counter to Jedi and Sith pawn kinds — including the player's. This is the Hive's tactical identity beyond mass.

## Belief system: **The Foundry Mandate**

- **Structure:** Ideological
- **Memes:** Collectivist, Supremacist, Raider, Hive primacy (Human primacy reflavoured)
- **Styles:** Techist, Spikecore, Morbid
- **Preferred xenotypes:** Geonosian
- **Primary role:** Arch-overseer (aristocrat)
- **Specialists:** Production specialist, shooting specialist

| Issue | Setting |
|---|---|
| Work drive | Tripled |
| **Execution** | **Arena ritual — public gladiatorial spectacle** |
| Raiding | Required |
| Slavery | Honorable |
| Body modification | Approved |
| Mechanoid labor | Unrestricted |
| Autonomous weapons | Unrestricted |
| Charity | None |
| Organ use | Acceptable |
| Drug use | Medical only |
| Diversity of thought | Intense bigotry |
| Apostasy | Abhorrent |
| Corpses | Don't care |
| Child labor | Encouraged |
| Growth vats | No restriction |

Captives are held for the arena rather than imprisoned, which reinforces aristocratic rule and pacifies the drone masses. Implement as a ritual precept with a dedicated arena structure in hive settlements.

## Technology and economy

- fabrication, advanced components, droid production
- **sonic weapon manufacture**
- growth vats and gene infrastructure
- drop pods, mortars, turrets; bionics for aristocrats
- extensive mining and deep drilling; **deep-rock condensate collection**
- steel, plasteel, uranium, components, weapons
- fabrication halls, droid assembly and charging rooms, slave/prison barracks, arena
- nutrient-paste feeding for drones; deep drills and ore stockpiles

## Typical equipment

**Worker drone** — knife, autopistol, or none; work clothing or integrated chitin; awful; very low point cost.

**Warrior drone** — sonic blaster, machine pistol, heavy SMG; chitin natural armour; jump pack; poor to normal.

**Geonosian aristocrat** — heavy sonic weapon or charge rifle; recon armour over chitin; jump pack; good to excellent; command bonuses.

**Hive heavy (Houk)** — chain shotgun, minigun, warhammer; marine armour; shield belt or low-shield pack.

**Foundry engineer (Skakoan)** — charge rifle or none; sealed pressure suit; no field thirst; high Crafting and Intellectual.

**Battle droids** — line (assault-rifle equivalent, light armour), melee (integrated blade, shield), heavy (minigun/charge, marine-level), command (accuracy and coordination bonuses, expensive).

## Pawn-group patterns

- **Drone swarm:** numerous worker/warrior drones with line droids
- **Foundry assault:** aristocrat, engineers, heavies, battle droids
- **Deep-desert siege train:** mortar crews, worker drones, droid guards — sustainable where no other faction can operate
- **Jedi-hunt detachment:** sonic-blaster warrior drones fielded specifically against psycaster pawns
- **Elite recovery unit:** Rakata or Skakoan engineer with heavy droid escort

## Lore basis

- Hives divide into queen, aristocrat, and drone castes; aristocrats are ~5% of the population, rule the hive, disdain drones, and compete using armies of soldier drones and battle droids — https://starwars.fandom.com/wiki/Geonosian_hive/Legends
- Soldier drones are the only Geonosian drones with functional wings; they fight with sonic blasters and force pikes, and the sonic blasts cannot be deflected by lightsabers — https://starwars.fandom.com/wiki/Warrior_caste_(Geonosian)
- Geonosians have no standing military; they build droid armies for corporate clients — https://villains.fandom.com/wiki/Geonosians
- Captives were used as public arena entertainment, reinforcing aristocratic rule and pacifying the drones — https://swfanon.fandom.com/wiki/Geonosian_(Jedi_Renaissance)
- The Empire enslaved the Geonosians to build the Death Star — https://aliens.fandom.com/wiki/Geonosian

---

# 9. Arkanian–Kaminoan Gene Consortium

## Mechanical identity

A small, wealthy, technically advanced faction built on genetics, medicine, implants, growth vats, and engineered security organisms — sustained by an underclass it created itself. Neutral rather than friendly: profitable to trade with, dangerous to antagonise, difficult to raid.

## Water doctrine — **Allow (high consumption)**

Closed-loop recyclers make the Consortium siting-indifferent, but growth vats and biosculpters are industrially water-hungry. It therefore **buys bulk water from the Aquifer League** — a supply relationship the player can broker, tax, or sever.

- Sites on isolated highlands and secure research locations regardless of hydrology.
- Arkanian Offshoot labour is water-rationed. Escaped Offshoots arriving at the player's colony arrive dehydrated.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Spacer |
| Starting goodwill | 0 |
| Permanent enemy | No |
| Target settlements | 3 |
| Settlement distribution | Isolated highlands, cold deserts, secure research sites |
| Raid frequency | Low — **retrieval operations only** |
| Caravan frequency | Low |
| Trader types | Exotic goods, genes, medicine, implants, components |
| Base wealth | Very high |
| Typical settlement defenders | 14–26 elite pawns plus utility mechs |
| Utility-mech share | 10–20% of settlement population |
| Combat-mech share | 10–20% of defence points |
| Ordinary low-tech pawns | Almost none |
| Player contact | Incident and quest generators plus trade |

## Racial mixture

| Race/xenotype | Weight | Typical use |
|---|---:|---|
| **Arkanian** | 26% | Geneticists, doctors, administrators — the pureblood caste |
| **Kaminoan** | 20% | Growth-vat and medical specialists |
| **Arkanian Offshoot** | 12% | **Engineered labour underclass** |
| **Cerean** | 8% | Senior researchers and educators |
| **Bith** | 8% | Engineers and fabricators |
| **Skakoan** | 8% | Sealed technical staff |
| **Chiss** | 6% | Security officers and administrators |
| **Rakata** | 4% | Relic and archotechnology researchers |
| **Umbaran** | 4% | Intelligence and containment staff |
| **Miraluka** | 2% | Psychic research subjects |
| **Neimoidian** | 2% | Commercial staff |
| **Total** | **100%** | |

### The Offshoot underclass

Arkanian geneticists engineered the Offshoots to serve their pureblood masters — bred as living experiments and labourers, never recognised as true Arkanians, with short lives and no prospect beyond servitude. Purebloods have historically purged them.

This makes the faction's Supremacist and preferred-xenotype precepts **internally aimed**: the Consortium despises its own workforce. Two mechanics follow:

- **Escaped Offshoots** generate as recruitable refugee incidents at the player's colony, arriving dehydrated and in poor health.
- **Retrieval raids** are the Consortium's only offensive pawn group — sent to reclaim escaped property. This gives a neutral, hard-to-raid faction a personal reason to attack the player.

### Forced pawn-kind assignments

- **Geneticist:** Arkanian, Kaminoan, or Skakoan.
- **Senior Researcher:** Arkanian, Cerean, or Rakata.
- **Containment Officer:** Chiss or Umbaran.
- **Medical Specialist:** Kaminoan or Arkanian.
- **Offshoot Labourer:** Arkanian Offshoot only; weak constitution; minimal gear; very low point cost.
- **Prototype Guardian:** gene-tailored pawn from any approved base race; extreme point cost.
- **Psychic Researcher:** Miraluka or Cerean with low psylink.

## Belief system: **The Ascendant Genome**

- **Structure:** Ideological
- **Memes:** Transhumanist, Supremacist, Collectivist, Proselytizer
- **Styles:** Techist
- **Preferred xenotypes:** Arkanian, Kaminoan
- **Primary role:** Chief curator
- **Specialists:** Research specialist, production specialist

| Issue | Setting |
|---|---|
| Body modification | Approved |
| Biosculpting | Accelerated |
| Age reversal | Demanded |
| Neural supercharge | Preferred |
| Sleep accelerator | Preferred |
| Growth vats | Preferred |
| Mechanoid labor | No restriction |
| Autonomous weapons | No restriction |
| Slavery | Acceptable |
| Organ use | Acceptable |
| Drug use | Medical only |
| Charity | None |
| Execution | Respected if guilty |
| Diversity of thought | Moderate bigotry |
| Proselytizing | Occasional |
| Apostasy | Horrible |

## Technology and economy

- complete gene extraction and implantation; gene banks, growth vats, biosculpters
- fabrication, advanced components, bionics, advanced medical implants
- sterile hospital infrastructure, cryptosleep and containment rooms
- recon/marine armour for security; charge rifles, charge lances, EMP weapons
- utility and combat mechs
- **bulk water purchase and recycling plant** — the League supply dependency
- genepacks, xenogerms, medicine, glitterworld medicine, organs and implants
- advanced components, plasteel, gold, embryos, growth-vat supplies
- sterile labs and secure vaults; no large food or textile economy

## Typical equipment

**Research staff** — autopistol or none; lab apparel, flak vest at dangerous sites; neural calculator, bionic eyes, learning implants.

**Offshoot labourer** — none or knife; work clothing; poor health; appears in defence only under duress.

**Containment officer** — chain shotgun, assault rifle, EMP grenades; recon armour; smokepop or low-shield pack.

**Elite security** — charge rifle or charge lance; marine armour; jump pack; bionic limbs, coagulator, stoneskin-equivalent gene package.

**Prototype guardian** — monosword, zeushammer, minigun, or charge rifle; marine/cataphract armour; strong melee or shooting gene package, robust, fast healing, reduced pain; extreme point cost.

## Pawn-group patterns

- **Research caravan:** Neimoidian trader, scientists, containment officers, utility mech
- **Retrieval raid:** containment officers and a prototype guardian sent after escaped Offshoots
- **Acquisition team:** geneticist, security squad, medical mech
- **Containment response:** EMP specialists and prototype guardian
- **Settlement defence:** elite security behind turrets with utility and combat mechs

## Lore basis

- Arkanian geneticists engineered Offshoots as living experiments and slaves, bred for labour including the diamond mines, shunned and never regarded as true Arkanians, typically short-lived — https://starwars.fandom.com/wiki/Arkanian_Offshoot
- Offshoots were treated as second-class or non-citizens; purebloods conducted purges — https://starwars.fandom.com/wiki/Arkanian/Legends
- Arkanian society ran a rigid caste system based on blood purity, with Offshoots fixed at the bottom and no upward mobility — https://www.worldanvil.com/w/frontiers-datchinchilla/a/arkanian-article

---

# 10. Bounty Hunters' Compact

## Mechanical identity

A loose association of highly capable independent hunters bound by a professional code. Few settlements, small groups, broad species diversity, high weapon quality, exceptional combat skill. **Quest-first, raid-last** — the Compact generates hunts, not sieges.

## Water doctrine — **Allow (water clock)**

A 3–10 pawn hunting party carries no logistics tail. It brings what it brings.

- **A hunter pursuing a colonist arrives with a finite water supply.** If the player withdraws into dry tiles, the hunter must break off — or gamble and press on.
- This converts every hunt from a fight into a resource duel, which is the faction's core gameplay.
- Dry-capable members (Kaleesh, Zabrak, Chiss, Umbaran, Devaronian, Bothan) can push much further than water-hungry ones (Trandoshan, Rodian, Cathar, Togruta). Group composition tells the player how long they have.

## Faction settings

| Parameter | Setting |
|---|---|
| Tech level | Industrial |
| Starting goodwill | −10 |
| Permanent enemy | No |
| Target settlements | 4 |
| Settlement distribution | Trade hubs, ruins, road junctions, rough outposts |
| Raid frequency | Very low — settlement raids are the exception |
| Primary player contact | **Targeted-hunt incidents and bounty quests** |
| Caravan frequency | Medium |
| Trader types | Weapons, armour, exotic goods, prisoners |
| Base wealth | Medium-high |
| Typical field group | 3–10 |
| Equipment quality | Normal to excellent |
| Spacer-equipment share | 10–25% of combatants |
| Psycaster share | Below 1% |
| Hardcoded hostility | Wookiee Freeholds |

## Racial mixture

| Race/xenotype | Weight | Water profile | Typical use |
|---|---:|---|---|
| **Kaleesh** | 15% | Dry-capable | Elite hunters and melee fighters |
| **Zabrak/Iridonian** | 12% | Dry-capable | Assault hunters |
| **Trandoshan** | 12% | Water-hungry | Trackers and heavy hunters |
| **Rodian** | 10% | Water-hungry | Marksmen |
| **Bothan** | 8% | Dry-capable | Scouts and intelligence specialists |
| **Devaronian** | 8% | Dry-capable | Aggressive breachers |
| **Cathar** | 8% | Water-hungry | Fast melee and pursuit |
| **Chiss** | 7% | Dry-capable | Snipers and tactical leaders |
| **Umbaran** | 6% | Dry-capable | Infiltration and night operations |
| **Zeltron** | 5% | Neutral | Negotiators and recruiters |
| **Iktotchi** | 3% | Dry-capable | Trackers and rare psychic hunters |
| **Togruta** | 3% | Water-hungry | Scouts |
| **Duros** | 3% | Neutral | Mechanics and ranged specialists |
| **Total** | **100%** | | |

### Forced pawn-kind assignments

- **Compact Hunter:** any listed race; high Shooting or Melee.
- **Tracker:** Trandoshan, Bothan, Togruta, Iktotchi, or Cathar.
- **Marksman:** Rodian, Chiss, Duros, or Bothan.
- **Breacher:** Zabrak, Devaronian, or Kaleesh.
- **Guild Fixer:** Zeltron, Bothan, or Chiss.
- **Master Hunter:** Kaleesh, Trandoshan, Chiss, or Zabrak; excellent equipment.
- **Force-sensitive Hunter:** rare Iktotchi, Togruta, or Chiss; psylink 1–3 only.

### The Scorekeeper mechanic

Trandoshans worship the Scorekeeper and earn Jagannath points per kill. Being shamed or captured on a hunt **zeroes those points**, recoverable only by killing whoever did it.

A Trandoshan who is captured and released, or who breaks off a hunt because of thirst, has been shamed. He returns — **alone, better equipped, targeting the specific pawn who beat him.** A recurring named antagonist for almost no implementation cost.

## Belief system: **The Compact of the Mark**

- **Structure:** Ideological
- **Memes:** Individualist, Loyalist, Guilty
- **Styles:** Spikecore, Techist
- **Preferred xenotypes:** None
- **Primary role:** Guild adjudicator
- **Specialists:** Shooting specialist, melee specialist

| Issue | Setting |
|---|---|
| **Killing a Compact member in good standing** | **Abhorrent** |
| **Stealing another hunter's mark** | **Abhorrent** |
| **Questioning a delivered contract** | **Prohibited** |
| Slavery | Acceptable |
| Execution | Respected if guilty |
| Charity | None |
| Body modification | Approved |
| Drug use | Medical or social only |
| Diversity of thought | Neutral |
| Apostasy | No restrictive precept |
| Mechanoid labor | No restriction |
| Autonomous weapons | No restriction |
| Corpses | Don't care |
| Organ use | Acceptable |
| Physical love | Free |
| Raiding | **Not a meme** — the Compact takes contracts, it does not pillage |

The Code exists to keep hunters from fighting each other so contracts actually complete. Hunters rank in classes by skill and reputation and take work as bounty pucks from Guild hubs.

## Technology and economy

- complete industrial weapons and armour; limited purchased charge weapons
- recon armour, jump packs, shield belts
- machining, gunsmithing, comms and orbital trade
- bionics and combat drugs
- no major fabrication outside headquarters; no growth vats or mechanitor infrastructure
- weapons, armour, prisoners, contract information as quest rewards
- repair shops, armouries, cells, barracks; small high-security compounds
- little agriculture; food and **water bought in**, which is the range constraint
- high silver and weapon value relative to population

## Typical equipment

**Tracker** — bolt-action rifle, assault rifle, autopistol; duster and flak vest; smokepop pack; high Animals, Shooting, Medical.

**Marksman** — sniper rifle or charge lance; recon armour or high-quality flak; jump pack; good to excellent.

**Breacher** — chain shotgun, frag grenades, breach axe; marine armour or full flak; low-shield pack or shield belt.

**Master hunter** — masterwork assault rifle, charge rifle, monosword, or zeushammer; recon/marine armour; jump pack, shield belt; bionic eye, arm, legs, coagulator; very high point cost.

**Guild fixer** — excellent autopistol or heavy SMG; prestige clothing over flak vest; high Social, Intellectual, Shooting.

## Pawn-group patterns

- **Solo mark:** one master hunter or tracker sent after a **named colonist**, on a water clock
- **Capture team:** fixer, tracker, marksman, two breachers
- **Guild caravan:** weapons trader with 6–10 elite guards
- **Shamed Trandoshan:** solo return engagement against the pawn who defeated him
- **Retaliation squad:** 5–9 recon-armoured hunters with jump packs — rare, and only after the player breaks the Code
- **Outpost defence:** small elite force with excellent firing positions

## Lore basis

- The Guild Code forbids killing a Guild hunter in good standing, stealing another's bounty, or asking about a bounty once delivered — https://starwars.fandom.com/wiki/Bounty_Hunter_Code
- Hunters take work as bounty pucks from Guild hubs and are required to follow the Code — https://starwars.fandom.com/wiki/Bounty_Hunters'_Guild
- Hunters rank in classes by skill and reputation; the Code centres on professionalism and Guild reputation — https://screenrant.com/star-wars-bounty-hunters-guild-explained/
- Shame or capture on a hunt zeroes a Trandoshan's Jagannath points, recoverable only by killing the offender — https://starwars.fandom.com/wiki/Trandoshan/Legends
- Trandoshan hunting culture drives many into bounty hunting and mercenary work — https://www.cultureslate.com/news/blood-feud-wookiees-vs-trandoshans

---

# Player-faction boundary: Jawa Gravship Expedition

| Parameter | Rule |
|---|---|
| Race | Jawa |
| Force access | Never |
| NPC-faction weight | 0% |
| Primary role | Player race |
| Technology | Starts uneven and salvage-dependent |
| Droid use | Central to progression |
| **Water doctrine** | **Dry-adapted; droid labour has no thirst need** |
| Relationship to factions | Determined through scenario and diplomacy |
| Recruitment | Other races may join; no NPC faction generates Jawa members |

**Why the expedition survives here.** The Jawas' decisive advantage on a thirst world is that their labour force does not drink. Droid acquisition is water security, not merely tech progression, and this should be stated explicitly in the scenario text.

**The standing moral problem.** Jawas acquire droids using restraining bolts, which the Free Droid Enclaves define as slavery. The player's core progression loop is the Enclave's central atrocity. This is deliberate and left unresolved.

---

# Implementation checklist

1. Generate the ten factions and inspect settlement distribution.
2. Correct settlement counts and **water-tile placement** with a faction/world editor. The Aquifer League must hold the natural water; the Cartel must hold the oases; the Enclaves must sit on contaminated sources; Tuskens and Geonosians must be dry-sited.
3. Apply the NPC-vs-NPC relations matrix.
4. Verify equipment tags per faction so no two factions draw from one unrestricted pool.
5. Confirm forced pawn-kind race overrides for Hutts, Gamorreans, stormtroopers, Sith, Geonosian castes, droid chassis, Offshoot labour, and faction leaders.
6. Confirm raid generation is suppressed for the Aquifer League and Free Droid Enclaves, and that both have working incident/quest hooks.
7. Confirm Jedi generate factionless.

## Species coverage

All active roster races are used at least once across the ten NPC factions except **Jawa**, reserved for the player. Custom Hutt, custom droid, Ghorfa, and Arkanian Offshoot races are added under the roster's licence to fork or author bespoke races.

Forbidden and disabled races remain unused: Force Gremlin, Chadra-Fan, Echani, Feeorin, Ishi Tib, Thyrsian.

## RimWorld reference

- [Modding Tutorials: Xenotypes](https://rimworldwiki.com/wiki/Modding_Tutorials/Xenotypes)
- [Ideoligion](https://rimworldwiki.com/wiki/Ideoligion)
- [Factions](https://rimworldwiki.com/wiki/Factions)
- [World generation](https://rimworldwiki.com/wiki/World_generation)
- [RimWorld 1.6 Mod Updates](https://rimworldwiki.com/wiki/Modding_Tutorials/RimWorld_1.6_Mod_Updates)
