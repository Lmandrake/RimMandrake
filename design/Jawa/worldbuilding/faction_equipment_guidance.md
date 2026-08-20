# Faction equipment guidance — tech, money and flavour

_A retired seat, 2026-08-14. **The guidance document the owner required before another retired seat
assigns any inventory.**_

---

## 🔴 The question was answered from the defs, and it was the wrong question

**Owner asked: per xenotype, per faction, or both? A retired seat's answer, read from
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
A retired seat was testing it live.

⭐ **The role skeleton does not depend on that answer**, so nothing here is
blocked. **Build the roles; fill the species names when the test lands.**

---

# The canon research, and the numbers it produces

_Research: 70 species read from Wookieepedia wikitext, continuity marked per claim.
**Full findings in the commit; the load-bearing conclusions are here.**_

## ⭐ The finding that validates the whole approach

> **"Equipment quality follows money; industrial capacity does not."**

**The four richest species in Star Wars manufacture nothing.** Hutts own
production and commission fleets. Neimoidians *mortgaged their homeworld to the
Banking Clan for a loan to buy equity in someone else's factory* — and financed
the entire droid army without building one bolt of it. Muuns extract metal,
underwrite credit, then **purchase** their defences and **rent** their armies.
Pykes refine a drug and buy every gun they carry.

**Meanwhile the Geonosians — the densest industrial base in the galaxy, 100
billion strong, whose literal export line is "battle droids" — score only
`mixed`**, because they are a contract manufacturer whose wealth pools in the
aristocracy while drones are expendable.

⇒ **The two-axis model was right, and canon is more extreme than I made it.**

## The three bands that matter for us

| band | who | what it means for a loadout |
|---|---|---|
| ⭐ **"Spacer passengers"** — **the largest group by far** | Jawa · Nikto · Klatooinian · Hutt · Pyke · Muun · Neimoidian · Twi'lek · Kaleesh · Lasat · Aqualish · Feeorin · Zabrak · Togruta · Kel Dor · Chadra-Fan | **Fly, shoot and trade at galactic baseline while manufacturing NOTHING.** Their gear is bought, stolen or inherited — so **quality tracks their money, not their tier**, and nothing they carry needs to match |
| **producers** | Mon Calamari · Quarren · Geonosian · Sullustan · Wookiee · Ithorian · Mandalorian · Trandoshan · Rodian · Weequay · Zygerrian · Ugnaught | Named firms, named products. **Their kit should look deliberate and repeated** |
| **ultratech, one domain only** | Rakata *(Force-hyperdrive)* · Kaminoan *(cloning)* · Arkanian *(genetics)* · Umbaran *(war in darkness)* · **Mandalorian *(beskar metallurgy ONLY)*** | ⭐ **Every one is baseline outside its domain.** Umbaran fighters have no hyperdrive; Kaminoans buy the clones' guns; a Mandalorian off the forge is an ordinary spacer |

## 🔴 Four canon facts that change our factions

1. ⭐ **Jawas DO manufacture one thing: ion blasters, hand-built from scrap** — a
   power pack, a starship ion-engine accelerator and a restraining bolt, with
   **canon naming Jawas as the creators.** **That is the player faction's
   signature weapon and it was already in our stack as a mod.** Everything else
   they carry is someone else's.
2. **Tuskens are a REFUSAL, not a primitive people.** Descended from the
   spacefaring Kumumgah; offworld technology is sacrilege. **Their gaderffii is
   individually forged.** So "gear-restricted" is a doctrine, not a ceiling —
   and it means captured tech should be *destroyed*, not used.
3. ⭐ **Quarren built the CIS navy** — *Providence*, *Recusant*, *Subjugator* —
   through the Free Dac Volunteers Engineering Corps, and built the Mon
   Calamari's floating cities too. **The Deepwater Compact's labour caste are the
   best shipwrights on the planet and resent their own leadership.** That is a
   faction with an internal fracture, free.
4. ⚠️ **"Yoder" is not a canonical name.** Yoda's species has **no name, no
   homeworld and no technology** in either continuity — the mod invented it.
   Fine to keep as our label, but **do not let it into player-facing lore as
   canon.**

---

# The numbers — per faction, per role

**`weaponMoney` and `apparelMoney` are silver budgets. Quality clamps do the rest.
These are starting values to be tuned, not measurements.**

| faction | weapon money | apparel money | quality clamp | weapon classes |
|---|---|---|---|---|
| **Galactic Empire** | grunt 350 · heavy 700 · spec 900 · leader 1600 | 500 / 700 / 700 / 1200 | `forceNormalGearQuality` — **uniformity is the point** | blasters, mass-produced only |
| **Hutt Cartel** | 200 · 550 · 800 · **2500** | 250 / 400 / 600 / **2000** | none — **wildly uneven by design** | anything purchasable |
| **Homestead Defense League** | 130 · 300 · 450 · 700 | 180 / 250 / 300 / 500 | max **Good** | industrial firearms, farm tools |
| **Deep Desert Tribes** | 90 · 200 · 300 · 500 | 100 / 150 / 200 / 350 | max **Normal** | ⭐ **melee + scavenged rifles only.** Nothing they made |
| **Free Droid Enclaves** | integral — n/a | **0** | n/a | built-in weapons; **no apparel at all** |
| **Wildsteam Clan** | 200 · 400 · 500 · 800 | 150 / 200 / 250 / 400 | ⭐ **min Good** — few weapons, each old and well-made | bowcasters, melee |
| **Deepwater Compact** | 300 · 600 · 750 · 1400 | 400 / 550 / 650 / 1100 | min Good | ⭐ **defensive and aquatic** — harpoons, pressure arms |
| **Geonosian Foundry Hive** | 400 · 800 · 1000 · 1500 | ⭐ **60 / 80 / 100 / 200** | normal | sonic weapons; **droids do the dying** |
| **Ascendant Helix** | 600 · 1100 · 1400 · 2200 | 700 / 900 / 1100 / 1800 | ⭐ **min Excellent** — few and perfect | ultratech, no improvisation |
| **Blackstar Company** | 400 · 700 · 1100 · 1800 | 350 / 500 / 800 / 1500 | ⭐ **none — mismatched on purpose** | anything; no two alike |
| **Jawa Trade Moot** | ⭐ **120 · 200 · 300 · 450** | 100 / 130 / 160 / 250 | ⭐ **max Poor→Normal** | ⭐ **ion weapons** + everything salvaged |
| **the Junkers** | ⭐ **60 · 140 · 200 · 350** | ⭐ **400 / 700 / 900 / 1400** | max **Awful→Poor** on weapons; **armour unclamped** | scrap melee, stolen guns |

⭐ **Read the Junker row and the Geonosian row together — they are mirror
images, and each is a culture in two numbers.** The Junker spends nothing on
weapons and everything on armour, because **the armour was cut off a body and the
gun was not.** The Geonosian spends nothing on apparel and everything on
armament, because **the drone is the expendable part.**

⭐ **And the Jawa row is the campaign's thesis as arithmetic:** the lowest weapon
budget of any faction, the tightest quality clamp — **and the widest variety**,
because everything they carry came off something else.
