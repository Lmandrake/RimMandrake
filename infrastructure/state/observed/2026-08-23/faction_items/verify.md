# Faction item kits — first approximation, BUILD, 2026-08-23

Owner: *"We're not looking to be overly prescriptive, we're just trying to add some flavor
to the faction pawns based on their wealth, species makeup, and lifestyle. So just take a
wild shot at it."* v1, deliberately a first pass.

Implements PART 3 item 4 of `faction_equipment_clusters.md` — `inventoryOptions`, the last
of the four "dead levers" and the only one now built.

## shape, measured from vanilla rather than guessed
166 of 1737 PawnKindDefs already use `inventoryOptions`; `Grenadier_Destructive` is the
Core model. One `subOptionsChooseOne` per kind, so a pawn carries exactly ONE characteristic
thing, with a high `skipChance` so most pawns carry nothing and the item reads as flavour
rather than issued kit.

52 kinds across 13 faction families. Every `thingDef` verified present in capture
`2026-08-23T07-12-04Z` — 0 dangling. validate_patch.py 0 errors 0 warnings. Deployed.

## the reasoning, per faction

| faction | carries | why |
|---|---|---|
| **Trade Moot** (Jawa) | components, steel, durasteel, silver, herbal | the clan trades in salvage: a Jawa carries STOCK, not supplies. Leader adds a spacer component — the prize piece |
| **Deep Desert** (Tusken) | herbal medicine, pemmican, jade | no industry at all. Jade is portable wealth for people with no banks |
| **Hutt Cartel** | smokeleaf, yayo, flake, ambrosia, silver, gold | vice and portable wealth — the richest and least disciplined roster. Leader adds luciferium |
| **Ascendant Helix** | glitterworld medicine, neutroamine, spacer components, gold | Arkanian geneticists carry LAB stock and never street drugs. The contrast with the Hutts is the point |
| **Deepwater Compact** | industrial medicine, neutroamine, survival meals | sealed-suit divers carry rations and real medicine, not herbs |
| **Geonosian Hive** | insect jelly, components, steel | insect jelly is food AND identity; foundry stock beside it |
| **Free Droid Enclaves** | components, spacer components, chemfuel, hypertech | droids need PARTS and FUEL. No food, no medicine — that absence is the characterisation |
| **Wildsteam Clan** | herbal medicine, pemmican, chemfuel, wood | tribal steam-tech: herbs and hides, plus fuel for the boilers |
| **Junkers** | chemfuel, components, durasteel, steel | warcasket scrappers run on chemfuel and carry what they stripped |
| **Blackstar Company** | industrial medicine, go-juice, survival meals, silver | professionals: combat drugs, real medicine, paid in silver. Leader carries 150-400 silver |
| **Homestead League** | herbal medicine, pemmican, components, a little silver | settlers and salvagers — modest and practical |
| **Empire** | industrial medicine, survival meals | issued kit ONLY. A trooper carries what the quartermaster gave him, and nothing personal |

## where this helps realism, and where it will not

✅ **Looting a corpse becomes characterisation.** The strongest effect is not on the pawn but
on the PLAYER: a dead Hutt goon with flake and gold in his pockets tells you what the cartel
is, and a dead droid with a hypertech component tells you what is worth taking. Right now
every corpse yields the same nothing.

✅ **The absences say as much as the contents.** Droids carrying no food, Empire carrying
nothing personal, Tuskens carrying no manufactured goods — three different societies, read
off inventory alone.

✅ **It makes raids economically distinct.** A Blackstar raid is worth robbing; a Deep Desert
raid is not. That changes which raids the player chooses to fight rather than flee.

⚠️ **It is worth very little on its own.** `skipChance` 0.25-0.40 means most pawns carry
nothing, deliberately — but the flip side is that a player may fight three raids before
noticing. This is texture, not a system.

⚠️ **Drugs on the Hutts have a gameplay tail I did not model.** Captured cartel pawns arrive
as addicts, and luciferium on a Hutt leader means a prisoner who will die without a supply
the player does not have. That is arguably correct characterisation and arguably a cruelty
trap; it is a DECIDE call, not mine.

⚠️ **Silver in inventory is free money.** 40-120 on a Hutt goon and 150-400 on a Blackstar
leader is real early-game income. If raids feel too lucrative, this is the first dial to
turn down.

🔑 **What I would do next, and did NOT do:** the other three dead levers.
`apparelDisallowTags` for the taboos would stop a Tusken ever wearing Imperial plate;
`forceWeaponQuality` clamps are already specified per faction in the design and would make a
Helix agent's gear visibly better than a Junker's; `apparelColor` would give each faction a
palette. Those three do more for legibility than inventory does, and inventory was simply
the one that could be finished tonight.
