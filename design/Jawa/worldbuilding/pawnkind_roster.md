<!-- status: live -->
# The pawn-kind roster — 48 kinds, and what each one carries

_A retired seat, 2026-08-14. **The buildable half of `faction_equipment_guidance.md`.**
BUILD builds from this; nothing here should require a decision from them._

---

## The shape, in one paragraph

**Twelve factions × four roles = 48 `PawnKindDef`s.**

⚠️ **Name the denominator: the twelve are the factions that HOLD SETTLEMENTS on the
painted map**, which is also the twelve that carry dossiers in `faction_roster_v2.md`.
**The full roster is THIRTEEN** (`factions.count` in
`D:\Luke\dev\Rimworld\infrastructure\state\canon.yml`): the thirteenth is the
Forgotten Arsenal (vanilla `Mechanoid`), which holds no settlement by design, gets a
label patch rather than a dossier, and therefore gets **no kinds here**. So 12 is right
in this arithmetic and 13 is right for the roster; they are different questions.
🔴 The **fourteenth** faction some older docs count — the Unbound Hive — was cut
2026-08-14 and the cut landed on disk.

Every one sets
**`useFactionXenotypes: true`**, so it draws its species from the faction's own
`xenotypeSet` and **one kind spawns the whole species mix wearing that faction's
gear.** Species never appear in a kind's name.

**Naming:** `Jawa_<Faction>_<Role>` — e.g. `Jawa_Empire_Grunt`,
`Jawa_Junkers_Leader`. Our prefix, so nothing collides with a donor mod.

| role | share of a group | what it is |
|---|---|---|
| **Grunt** | ~60% | the body count. **This is the faction, because it is what the player sees** |
| **Heavy** | ~25% | changes how a fight goes |
| **Specialist** | ~12% | the faction's *idea* made into a pawn |
| **Leader** | ~3%, capped 1 | carries the canon title |

⚠️ **`weaponTags` are given as CLASSES, not strings.** I will not invent tag
values — **BUILD resolves each class to the actual tags our weapon mods use**,
and that survey is part of the build.

---

## The 48

**`wM` = `weaponMoney`. `aM` = `apparelMoney`. Quality column is the clamp.**

### 1 · Galactic Empire — *uniformity is the point*
| kind | wM | aM | quality | weapon class |
|---|---:|---:|---|---|
| Grunt — **stormtrooper** | 350 | 500 | `forceNormalGearQuality` | issue blaster rifle |
| Heavy — **heavy trooper** | 700 | 700 | same | support blaster, launcher |
| Specialist — **officer** | 900 | 700 | same | pistol; ⭐ **no armour** — grey uniform |
| Leader — **Emperor Palpatine** *(unique)* | 1600 | 1200 | Excellent | ceremonial |

⭐ **`forceNormalGearQuality` on all four is the design.** Nothing the Empire
fields is remarkable, and that is what makes it frightening.

### 2 · Hutt Cartel — *ostentation, unevenly spent*
| kind | wM | aM | quality | weapon class |
|---|---:|---:|---|---|
| Grunt — **enforcer** | 200 | 250 | none | cheap slugthrowers |
| Heavy — **bodyguard** | 550 | 400 | none | shotguns, heavy pistols |
| Specialist — **factor** *(the human minority)* | 800 | 600 | none | concealed |
| Leader — **Lord Gorga the Immense** | **2500** | **2000** | Masterwork | gilded, absurd |

⭐ **No clamp anywhere.** A Cartel group should contain the best-armed and the
worst-armed pawn on the map at once.

### 3 · Homestead Defense League — *repaired, not bought*
| kind | wM | aM | quality | weapon class |
|---|---:|---:|---|---|
| Grunt — **militia** | 130 | 180 | max **Good** | bolt-action, farm tools |
| Heavy — **well-guard** | 300 | 250 | max Good | industrial rifle |
| Specialist — **warden** *(Iktotchi)* | 450 | 300 | max Good | scoped rifle |
| Leader — **High Marshal Taren Voss** | 700 | 500 | max Excellent | sidearm |

### 4 · Deep Desert Tribes — *nothing they made*
| kind | wM | aM | quality | weapon class |
|---|---:|---:|---|---|
| Grunt — **raider** | 90 | 100 | max **Normal** | ⭐ **melee only** — gaderffii |
| Heavy — **brute** | 200 | 150 | max Normal | heavy melee |
| Specialist — **marksman** | 300 | 200 | max Normal | **one scavenged rifle** |
| Leader — **War Chief Torr'gan** | 500 | 350 | max Good | forged blade |

⭐ **Captured tech is destroyed, not used** — canon: offworld technology is
sacrilege. So the rifle is an exception the fiction has to earn.

### 5 · Free Droid Enclaves — *integral*
| kind | wM | aM | quality | weapon class |
|---|---:|---:|---|---|
| Grunt — **labour droid** | — | **0** | n/a | ⭐ **built-in, no apparel at all** |
| Heavy — **security droid** | — | 0 | n/a | integral heavy |
| Specialist — **medical droid** | — | 0 | n/a | none |
| Leader — **First Speaker R-41 Rell** | — | 0 | n/a | none |

### 6 · Wildsteam Clan — *few, old, well-made*
| kind | wM | aM | quality | weapon class |
|---|---:|---:|---|---|
| Grunt — **hunter** | 200 | 150 | ⭐ **min Good** | bowcaster |
| Heavy — **pod-warden** | 400 | 200 | min Good | heavy bowcaster |
| Specialist — **beast-handler** | 500 | 250 | min Good | melee + wildpod bond |
| Leader — **Elder Rroowaak** | 800 | 400 | min Excellent | heirloom bowcaster |

### 7 · Deepwater Compact — *wealthy, and nothing built to march*
| kind | wM | aM | quality | weapon class |
|---|---:|---:|---|---|
| Grunt — **shore guard** | 300 | 400 | min Good | harpoon gun |
| Heavy — **pressure trooper** | 600 | 550 | min Good | pressure weapon |
| Specialist — **Quarren shipwright** | 750 | 650 | min Good | tools ⭐ *see below* |
| Leader — **High Warden Neris Cal** | 1400 | 1100 | Excellent | ceremonial trident |

⭐ **The Quarren specialist carries the faction's internal fracture** — canon's
best shipwrights, subordinate to Mon Calamari leadership and resentful of it.

### 8 · Geonosian Foundry Hive — *the drone is the expendable part*
| kind | wM | aM | quality | weapon class |
|---|---:|---:|---|---|
| Grunt — **drone** | 400 | ⭐ **60** | normal | sonic blaster |
| Heavy — **soldier drone** | 800 | 80 | normal | sonic cannon |
| Specialist — **overseer** | 1000 | 100 | normal | sonic + command |
| Leader — **Archduke Korrik the Shaper** | 1500 | 200 | Excellent | ceremonial |

⭐ **Sonic weapons cannot be deflected by a lightsaber** — canon, and it is the
one hard counter to the Sith in the whole roster.

### 9 · Ascendant Helix — *few and perfect*
| kind | wM | aM | quality | weapon class |
|---|---:|---:|---|---|
| Grunt — **retrieval agent** | 600 | 700 | ⭐ **min Excellent** | ultratech sidearm |
| Heavy — **brute-stock labourer** | 1100 | 900 | min Excellent | ⭐ the engineered underclass |
| Specialist — **curator** | 1400 | 1100 | min Excellent | precision |
| Leader — **Director Ko Saiyan** | 2200 | 1800 | Masterwork | none |

### 10 · Blackstar Company — *no two alike*
| kind | wM | aM | quality | weapon class |
|---|---:|---:|---|---|
| Grunt — **hired gun** | 400 | 350 | ⭐ **none** | anything |
| Heavy — **Mandalorian** | 700 | 500 | none | ⭐ beskar-pattern plate |
| Specialist — **hunter** | 1100 | 800 | none | tracker's kit |
| Leader — **Captain Jaxen Marr** | 1800 | 1500 | none | personal |

⭐ **Mandalorian is a CULTURE, not a species** — humans and adoptees in the plate.

### 11 · Jawa Trade Moot — *everything works, nothing matches*
| kind | wM | aM | quality | weapon class |
|---|---:|---:|---|---|
| Grunt — **scavenger** | ⭐ **120** | 100 | ⭐ **max Poor** | ⭐ **ion weapon** |
| Heavy — **crawler guard** | 200 | 130 | max Normal | salvaged rifle |
| Specialist — **Scrap-Singer** | 300 | 160 | max Normal | none — quest-giver |
| Leader — **First Bargainer Kiknik the Wealthy** | 450 | 250 | max Good | ceremonial ion |

⭐ **The ion blaster is the one thing Jawas canonically MANUFACTURE** — a power
pack, a starship ion accelerator and a restraining bolt. **Everything else they
carry came off something else.**

### 12 · the Junkers — *the armour was cut off a body; the gun was not*
| kind | wM | aM | quality | weapon class |
|---|---:|---:|---|---|
| Grunt — **scrapper** | ⭐ **60** | ⭐ **400** | ⭐ weapons max **Awful** | scrap melee |
| Heavy — **warcasket** | 140 | **700** | armour **unclamped** | stolen gun |
| Specialist — **claim-jumper** | 200 | 900 | weapons max Poor | stolen rifle |
| Leader — **Scraplord Tarn Vox the Brutal** | 350 | 1400 | armour Masterwork | broken pipe |

⭐ **Read the Junker and Geonosian grunts side by side.** 60/400 against 400/60.
**Each is a culture in two numbers, and they are exact mirrors.**

---

## Not our kinds

**the Forgotten Arsenal** (vanilla `Mechanoid`) and **the Unbound Hive** (vanilla
`Insect`) field vanilla kinds. **We rename the factions and cherry-pick the
roster; we author no pawn kinds for either.**

## What BUILD resolves, and it is the only open work

1. **`weaponTags` → real tag strings.** Requires a survey of what our weapon mods
   actually tag. **The classes above are the design; the strings are the build.**
2. **`combatPower` per kind.** Should follow the money, not be set independently.
3. **`apparelRequired`** for the four cases where a specific item IS the pawn:
   stormtrooper armour, Mandalorian plate, warcasket, Jawa robe.
4. ⚠️ **`apparelStuffFilter` is a FACTION field, not a kind field** — set it once
   per faction. **The cheapest way to make the Junkers look like Junkers.**
