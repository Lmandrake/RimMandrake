# Faction equipment guidance — tech, money and flavour

_VISION, 2026-08-14. **The guidance document the owner required before CREATE
assigns any inventory.**_

---

## 🔴 The question was answered from the defs, and it was the wrong question

**Owner asked: per xenotype, per faction, or both? CREATE's answer, read from
`Assembly-CSharp` metadata: NEITHER, as posed.**

> **Equipment lives entirely on `PawnKindDef`.**

- **`PawnKindDef`** carries all of it — `weaponTags`, `weaponMoney`,
  `forceWeaponQuality`, `apparelTags`, `apparelRequired`, `apparelMoney`,
  `apparelColor`, `specificApparelRequirements`.
- **`FactionDef` carries no equipment fields at all.** A faction "has" gear only
  by fielding kinds that have it.
- **`XenotypeDef` carries none.** A xenotype is genes; it never touches a loadout.

⭐ **And `PawnKindDef.useFactionXenotypes` is the field that makes this cheap.**
With it true, a kind draws its species from the faction's own `xenotypeSet` — so
**one kind spawns the faction's whole species mix, wearing that faction's gear.**

> **⇒ PER FACTION, BY ROLE. Species ride free.**
> **~4 kinds × 12 factions ≈ 48 kinds, not 80 × 12 = 960.**

**And a Weequay in the Cartel automatically carries different gear from a Weequay
in Blackstar**, because they are different kinds — which is the outcome we wanted,
arrived at by the cheap route.

⚠️ **Per-species exceptions stay possible and must stay RARE.** One extra kind
plus a group-maker entry each. **Reserve them for where the species genuinely
changes the loadout** — a Wookiee with a bowcaster, a Jawa with an ion weapon —
**never for flavour.**

## The four roles, every faction

| role | what it is |
|---|---|
| **grunt** | the body count. What the player sees most, so it defines the faction |
| **heavy** | the one that changes how a fight goes |
| **specialist** | the faction's *idea* made into a pawn — the thing only they field |
| **leader** | rare, better-equipped, and carries the faction's title |

---

## ⭐ Tech and money are DIFFERENT AXES, and the interesting factions sit off the diagonal

**A rich faction with poor tech buys good gear. A poor faction with high tech
makes strange gear. Neither is "better equipped" — and a roster where money and
tech move together is a roster with one axis.**

| faction | tech tier | money | what the gear SAYS |
|---|---|---|---|
| **Galactic Empire** | spacer | rich | **uniform.** Mass-produced, identical, no personality. You are fighting a supply chain |
| **Hutt Cartel** | industrial, with **bought** spacer pieces | **very rich, unevenly spent** | ostentation. Gold on a shotgun. The boss's guard outguns the army |
| **Homestead Defense League** | industrial | **poor** | repaired, not bought. Farm tools that became weapons |
| **Deep Desert Tribes** | neolithic → industrial, gear-restricted | poor | ⭐ **nothing they made themselves.** Scavenged rifles, ritual blades. The gear is *taken* |
| **Free Droid Enclaves** | spacer | modest, **self-manufacturing** | integral. No armour because no flesh; the weapon is part of the body |
| **Wildsteam Clan** | low-industrial | poor | ⭐ **hand-made and heirloom.** Few weapons, each old and good. Bowcasters |
| **Deepwater Compact** | industrial | **wealthy — water monopoly** | defensive and aquatic. Harpoons, pressure weapons, nothing built to march |
| **Geonosian Foundry Hive** | industrial **manufacturer** | ⭐ **rich in materiel, poor in everything else** | sonic weapons, and droids doing the dying. They do not spend on their own |
| **Ascendant Helix** | **ultratech** | very rich | ⭐ **few, and excellent.** No waste, no spares, nothing improvised |
| **Blackstar Company** | industrial → spacer, **mixed** | money-rich per head | ⭐ **personal and mismatched.** A mercenary buys their own; no two look alike |
| **Jawa Trade Moot** | industrial, **salvage-grade** | ⭐ **poor in money, rich in STUFF** | everything works, nothing matches. The most equipment, the least value |
| **the Junkers** | **degraded** industrial | poorest | ⭐ **cut off bodies.** Warcaskets are biographies. Nothing works properly and it shows |

⭐ **The four off-diagonal entries are where the roster earns its keep:** the
**Jawa** (no money, enormous inventory), the **Geonosians** (war materiel without
wealth), the **Deepwater Compact** (wealthy but with nothing built for
offence), and the **Junkers** (armour that is worth more than the people in it).

## Reading the table as loadouts

- **Money buys QUALITY and QUANTITY** → `weaponMoney`, `apparelMoney`,
  `forceWeaponQuality`.
- **Tech buys the WEAPON CLASS** → `weaponTags`.
- ⭐ **Flavour is the mismatch between them**, and it is the column that makes a
  faction recognisable at a glance. **A Junker in an expensive warcasket holding a
  broken pipe is a whole culture in one pawn.**

## What is still blank, and why that is fine

⚠️ **Species names are deliberately absent.** `useFactionXenotypes` reads the
faction's `xenotypeSet`, so **whichever of the three overlapping Star Wars
xenotype mods generation actually honours is the one that must be named there.**
OPS is testing it live.

⭐ **The role skeleton does not depend on that answer**, so nothing here is
blocked. **Build the roles; fill the species names when the test lands.**
