<!-- status: draft -->
# Faction equipment clusters — the palette, and who draws from it

_CHECK, 2026-08-22. Owner's instruction, 01:17: cluster the weapon technologies, apparel
types and special items, associate factions with the clusters, and make different factions
want strongly different things._

> 🔑 **This is the layer BELOW `faction_equipment_guidance.md`, not a replacement for it.**
> That document settled the model — equipment lives on `PawnKindDef`, per faction by role,
> tech and money as independent axes — and gave each faction a sentence saying what its gear
> should SAY. **It never named a single def or tag.** This file is the bridge from that
> prose to defs that exist in the loaded game.

---

## PART 0 — the diagnostic, before any design

Measured 2026-08-22 against the 2026-08-21 def dump and the live Cherry Picker kill list.
**"Usable" excludes cut defs**, because Cherry Picker empties `weaponTags` at load and a cut
weapon can never be equipped by generation.

    weapon ThingDefs      771     cut 186     usable 585
    distinct weaponTags with a usable weapon behind them        389
    distinct apparel tags with usable apparel behind them       823

### 🔴 Finding 1 — the WEAPON axis is already differentiated, and it is good

The 68 authored `Jawa_*` kinds request **37 distinct `weaponTags`**, and the split by
faction reads as deliberate design rather than defaults:

| faction group | tags it asks for | what that says |
|---|---|---|
| DeepDesert | `ORTuskenMelee` · `ORMeleeBlunt` · `NeolithicMeleeAdvanced` · `SaV_tusken` | gaderffii sticks and the Tusken Cycler |
| TradeMoot | `Jawa_IonWeapon` · `Jawa_IonWeaponLight` · `KotORRanged_ion` · `SaV_jawaheavy` | the ion signature, exactly as canon has it |
| Empire | `ORImperialStandard` · `ORImperialLight` · `ORImperialHeavy` · `ORImperialSniper` · `ORHeavyWeapon` | one supply chain, four grades |
| Geonosian | `KotORRanged_sonic` + rare/legendary | sonic, as specified |
| Wildsteam | `KotORBowcaster` · `ORVibroweapon` · `ORMeleeSharp` | bowcasters and good blades |
| Junkers | `NeolithicMeleeBasic` · `ORMeleeBlunt` · `KotORRanged_weak` · `SimpleGun` | scrap |
| Blackstar | `KotORRanged_rare/strong/legendary` · `ORPistol` · `ORSniper` | bought, personal, expensive |
| Hutt | `KotORRanged_weak` **through** `legendary` | ostentation, unevenly spent |
| Droid | `ORDroidWeapon` | integral |

**No empty pools among them.** ⇒ Nobody needs to redo the weapon layer. It works.

### 🔴 Finding 2 — the APPAREL axis is essentially unbuilt

**823 apparel tags have usable gear behind them. The 68 authored kinds ask for FIVE.**

    IndustrialBasic          supply  20   asked by 14 kinds
    WarcasketAll             supply  51   asked by  4 kinds
    Neolithic                supply  12   asked by  3 kinds
    SaV_outfit_gamorrean     supply   3   asked by  2 kinds
    SaV_apparel_huttgoon     supply   5   asked by  1 kind

⇒ **Fourteen kinds across many factions all wear generic vanilla `IndustrialBasic`.** The
Empire, the Compact, the Helix and the Homestead are, on screen, the same people.
Meanwhile the pools that would separate them are sitting unused: `ImperialApparel` (21),
`KotORArmor_light` (16) / `_mid` (20) / `_heavy` (16), `EVA` (25), `Royal` (20),
`Warcasket` (15), `PrestigeCombatGear` (22).

🔑 **This is where the owner's wish lives.** Weapons already differ; silhouettes do not.

### 🔴 Finding 3 — every "flavour" lever the guidance doc specifies is at zero

`faction_equipment_guidance.md` assigns a quality clamp to each of the twelve factions —
`forceNormalGearQuality` for the Empire, *min Excellent* for the Helix, *max Poor→Normal*
for the Jawa, *armour unclamped* for the Junkers. Measured across the 68 authored kinds:

| lever | kinds using it |
|---|---|
| `apparelMoney` | **68 / 68** ✅ |
| `techHediffsMoney` | **68 / 68** ✅ |
| `apparelRequired` | 12 / 68 |
| `specificApparelRequirements` | 5 / 68 |
| `techHediffsTags` | 15 / 68 |
| **`forceWeaponQuality`** | **0 / 68** 🔴 |
| **`apparelColor`** | **0 / 68** 🔴 |
| **`apparelDisallowTags`** | **0 / 68** 🔴 |
| **`inventoryOptions`** | **0 / 68** 🔴 |

⇒ The money numbers landed. **The quality clamps, the faction colours, the taboos and the
carried items were specified and never built** — and those are exactly the four fields that
turn "different budget" into "visibly different culture".

### ⚠️ Finding 4 — one faction's stated identity has no defs behind it

`faction_equipment_guidance.md` gives the **Deepwater Compact** *"defensive and aquatic —
harpoons, pressure weapons, nothing built to march"*. Searched the whole usable set for
harpoon / speargun / trident / net / pressure / dive / aquatic: **zero**. The only
spear-shaped ranged weapons in the game, `AM_Spear68A` and `AM_Spear68C` (6.8 spear rifle),
are **on the Cherry Picker kill list**.

⇒ Three routes, and the cheapest is the first: **un-cut the two spear rifles** and give them
a Compact-only tag; or re-found the Compact's identity on something that exists (they
currently draw `ORVibroweapon` + KotOR mid-tier, which reads as generic); or author new
weapons, which is a mod-build, not a patch.

### ⚠️ Finding 5 — nine authored kinds are fielded by nothing
All four `Jawa_DeepDesert_*`, all four `Jawa_Blackstar_*`, and `Jawa_Empire_Leader` appear
in no `FactionDef`'s `pawnGroupMakers`. Filed as `ORPHANED_ROLE_KINDS_UNFIELDED_1`.
**A cluster assignment for those factions changes nothing until they are wired in.**

---

_Parts 1–3 (the weapon clusters, the apparel clusters, and the faction↔cluster matrix with
taboos) follow once the palette survey and the independent critique return._

### 🔴 Finding 6 — the roster's most-used armour assignment points at a CUT def

Measured against the live kill list:

| vanilla armour | state |
|---|---|
| `Apparel_ArmorRecon` · `Apparel_ArmorHelmetRecon` | 🔴 **CUT** |
| `Apparel_ArmorCataphract` · helmet | 🔴 **CUT** |
| `Apparel_PowerArmor` · helmet | 🔴 **CUT** |
| all three **Prestige** variants | 🔴 **CUT** |
| `Apparel_TribalA` · `Apparel_GasMask` | 🔴 **CUT** |
| `Apparel_ArmorMarine` · helmet | ✅ usable |
| flak vest / jacket / pants, simple + advanced helmet, duster, plate, shield belt | ✅ usable |

⚠️ **`faction_roster_v2.md` assigns "recon armour" to at least seven factions** — Empire
grunt, Hutt lieutenant, Wildsteam Liberator, Compact warden, Geonosian aristocrat, Helix
containment officer, Blackstar tracker. **Every one of those points at a def that generation
can no longer equip.** Marine armour, which the roster also uses, survives.

⇒ The armour ladder on this planet is **flak → marine → Warcasket / KotOR composite**, with
no recon tier and no cataphract tier. Any loadout written against vanilla's ladder is
written against a game that is not installed.

### ⚠️ Finding 7 — 25 apparel tags are requested by kinds and carried by nothing
Of 140 distinct `apparelTags` requested across 1730 usable `PawnKindDef`s, **25 resolve to
zero usable apparel.** Campaign-relevant: **`Medieval` (6 kinds)** — and those six are ours:
`RimMandrake_JawaTribal`, `_ArkanianTribal`, `_GeonosianTribal`, `_NiktoTribal`,
`_QuarrenTribal`, `_WookieeTribal` all ask for `["Neolithic", "Medieval"]`. `Neolithic`
resolves to 11 defs; `Medieval` resolves to nothing, so they draw from **half the palette
they were written for**. Also dead: `RebelApparel` (3 kinds), `ORImperialLight` (1),
`ORRISArmour` (2).

---

# PART 1 — the clustering principle

⛔ **Not by aesthetic, and not by mod.** A palette cut by "looks Star Wars" produces
factions that differ in skin and play identically. `setting_physics.md` already contains a
closed counter-system, so **cluster by HARM FORM — what a thing does and what defeats it —
and cross it with CULTURAL IDIOM — how the faction came to be holding it.** A faction is
then a *cell*, not a shopping list, and its preferences are legible in a firefight rather
than only in a screenshot.

## Axis A — harm form (from `setting_physics.md` L1–L18)

| # | form | defeats | defeated by | the law it comes from |
|---|---|---|---|---|
| **A1** | **kinetic** — slugthrowers, cyclers, bows, thrown | energy-optimised armour; droid frames | mass plate; sand fouling (L12) | L2 |
| **A2** | **thermal-plasma** — blaster bolts | flesh, 1–2 shots; light armour | ablative/refractory; **desert megafauna** (L11) | L1 |
| **A3** | **cutting-plasma** — lightsabers | *anything a person can wear*, instantly | vehicle plate; cortosis (rare); its own detonation (L17a) | L3 |
| **A4** | **ionic** — ion, EMP, Force lightning | droids, vehicles, turrets, **powered armour, shields** | flesh — **zero damage** | L4, L15 |
| **A5** | **neural** — stun | organics | machines — **completely inert** | L5 |
| **A6** | **shear** — vibro | ablative armour; parts shields fastest | mass plate | L14 |
| **A7** | **mass/blunt** — clubs, mauls, **sonic** | armour built against Sharp and Heat | — | L7, roster `:1612` |
| **A8** | **explosive** | everything; armour barely helps | scarcity alone | L13 |

🔑 **The loop closes:** blaster → beaten by ablative → beaten by vibro → beaten by mass
plate → beaten by blaster heat. **Ion and stun are exact mirrors of each other** (L4/L5), so
a force meeting droids *and* people needs two tools and cannot economise.

⭐ **And one consequence is the whole campaign in a sentence: the Jawa's own manufactured
weapon, the ion blaster, does ZERO damage to flesh.** The player faction's signature arm
cannot kill a person. It captures machines. Everything else they carry came off somebody
else. That is not a balance problem to fix — it is the thesis, and it should be protected.

## Axis B — cultural idiom (how they came to hold it)

| # | idiom | reads as | levers that express it |
|---|---|---|---|
| **B1** | **forged** — they made it by hand, one at a time | few, personal, old | `min Good` quality, low `weaponMoney`, narrow tags |
| **B2** | **salvaged** | everything works, nothing matches | widest tag list, `max Poor`, high variety |
| **B3** | **manufactured signature** — they make ONE thing well | repeated, deliberate | one dominant tag + filler |
| **B4** | **bought premium** | expensive, mismatched | high money, **no** quality clamp |
| **B5** | **issued uniform** | identical, impersonal | `forceNormalGearQuality`, one tag family |
| **B6** | **integral** — the weapon is the body | no apparel, no variety | `apparelMoney 0` |
| **B7** | **taken** — off a corpse or a wreck | armour worth more than the wearer | armour money ≫ weapon money |

---

# PART 2 — the faction × cluster matrix

**Primary / secondary is what they field. TABOO is the half nobody has built** —
`apparelDisallowTags` is `0 / 68` today, and it is the field that makes a preference *strong*
rather than merely statistical.

| faction | idiom | primary harm | secondary | 🔴 TABOO — must never appear | the vulnerability that makes it fair |
|---|---|---|---|---|---|
| **Galactic Empire** | B5 issued | A2 blaster | A8 mortars, drop pods | improvised, personalised or salvaged anything | all-blaster ⇒ **helpless against ablative desert fauna** (L11), and ion strips their powered kit (L4) |
| **Hutt Cartel** | B4 bought | A2 at every price tier | chemical (drugs, slaves) | nothing they manufactured — it is all purchased | no doctrine and no drill; the best and worst armed pawn on the map stand together |
| **Homestead Defense League** | B1/B2 repaired | A1 kinetic | A7 farm tools | spacer armour, charge weapons | poorest ranged reach; `raidsForbidden` means they never choose the ground |
| **Deep Desert Tribes** | B1 forged + "taken" | A1 cycler + **A7 gaderffii** | chemical — **sandbat venom** | 🔴 **energy weapons are SACRILEGE.** Captured tech is destroyed, not used | cyclers are slugthrowers and **sand fouls mechanisms** (L12) — their own world jams their guns |
| **Free Droid Enclaves** | B6 integral | A4 ionic + A2 charge | — | **no apparel at all**; no food, no water, no prisoners | ionic weapons and **ionic storms** (L12) shut them down; A5 stun is inert on them |
| **Wildsteam Clan** | B1 heirloom | A1 bowcaster | A6 vibro, melee 45–60% | charge weapons; turrets are ideologically forbidden | furred on a desert world — **the thirstiest fighters in the game**, near-useless expeditionary |
| **Deepwater Compact** | B3 manufactured | **A4 EMP** | A1 rifles | 🔴 **nothing built to march** — no drop pods, no offensive production | amphibian physiology; `raidsForbidden` is enforced by dehydration, not by policy |
| **Geonosian Foundry Hive** | B3 manufactured | **A7 sonic (Blunt)** | droids at 35–55% of points | spend nothing on the drone — `apparelMoney` 60 | sonic is **8 damage / 3-round burst**; armour-indifferent, not armour-piercing |
| **Ascendant Helix** | B4 few-and-perfect | A2 charge + A4 EMP | A3 on the Prototype Guardian | improvisation of any kind; no spares | tiny numbers; a lost specialist is not replaced |
| **Blackstar Company** | B4 personal | **all of them** | A3 rarely, beskar rarer | 🔴 **no two alike** — uniformity is the taboo | no fabrication off-site; a hunt is a **water clock** |
| **Jawa Trade Moot** | B2 salvage | ⭐ **A4 ion — the one thing they make** | A1 salvaged rifles | spacer equipment; **proud** to run junk | ⭐ **ion does zero damage to flesh.** Their signature weapon cannot kill a person |
| **the Junkers** | B7 taken | A7 scrap blunt | A1 stolen guns | nothing manufactured, no doctrine at all | welded steel on a desert world; **mass plate is beaten by blaster heat** (L14) |

⭐ **Read the Geonosian and Junker rows together, as the guidance doc says — they are
mirrors.** And read the Jawa row against the Empire's: the richest faction fields one weapon
type and is blind to wildlife; the poorest fields everything and cannot kill a man with the
only gun it builds.

## The apparel assignment — the half that does not exist yet

Clusters from the live palette (723 usable apparel defs, 14 clusters). **One cluster per
faction, so a silhouette is readable at a glance:**

| faction | apparel cluster | tags to use | head piece |
|---|---|---|---|
| Empire | **Imperial trooper plate** (57) / **uniform** (64) for officers | `ImperialStormtrooper`, `ImperialArmy`, `ImperialOfficer` | yes — full-face |
| Hutt Cartel | Merc composite + **Noble regalia** on the boss | `SaV_apparel_huttgoon`, `KotORArmor_mid`, `Royal` | mixed |
| Homestead | Salvager junk + Desert robes | `Outlander`, `Western`, `ORScrapper` | hoods |
| Deep Desert Tribes | **Desert robes / veiled faces** (35) | `ORTusken`, `SaV_apparel_tusken`, `GS_SandP_*` | **yes — masks** |
| Free Droid Enclaves | **Droid chassis** (24) + modules (108) | `KotORDroidArmorT1/T2/T3`, `DroidArmor` | n/a |
| Wildsteam | Tribal hides (51) | `Neolithic`, `ORBoneArmour`, `ORChitinArmour` | skull masks |
| Deepwater Compact | **Environmental suits & breathers** (16) | `EVA`, `Vacsuit`, `KotORHeadband_gasmask` | yes |
| Geonosian | chitin (natural) + lab apparel; **`apparelMoney` 60** | `BMT_Apparel_Chitin*` | beetle helm |
| Ascendant Helix | Merc composite, top tier only | `PrestigeCombatGear`, `KotORArmor_heavy` | visored |
| Blackstar | **Merc & composite** (67), deliberately mixed | `SaV_outfit_merc`, `MNCFactionArmor`, `KotORArmor_*` | mixed |
| Jawa Trade Moot | **Desert robes** — `apparelRequired` robe + hood | `ORJawa`, `SaV_apparel_jawa`, `guy762_JawaHood` | **yes, mandatory** |
| Junkers | **Warcasket** (65) | `WarcasketAll`, `WarcasketVeteran` | sealed, three-piece |

⚠️ **Heat is a real constraint and it cuts against two of these.** Measured
`Insulation_Heat`: desert robes 20–25, Tusken/Sandpeople masks 50 — *the correct look, not
the survival answer*. The genuinely heat-proof kit is the **hazard warcasket (333)** and the
environmental/droid tiers (100). ⇒ On a dayside world the Junkers are wearing the best heat
protection on the planet, which contradicts the roster's intent that warcaskets carry a heat
*penalty*. **That contradiction is real and belongs to DECIDE**, not to me.

---

# PART 3 — what to build, in order

1. **Wire the nine orphaned kinds in** (`ORPHANED_ROLE_KINDS_UNFIELDED_1`). Until then the
   Deep Desert and Blackstar rows above change nothing.
2. **Repoint every "recon armour" and "cataphract" assignment.** Both are cut. The ladder is
   flak → marine → Warcasket/KotOR composite.
3. **Give each faction its apparel cluster.** One tag family each, replacing the shared
   `IndustrialBasic`. This is the single highest-visibility change on the list.
4. **Build the four dead levers:** `forceWeaponQuality` (the clamps are already specified per
   faction and unimplemented), `apparelColor`, `apparelDisallowTags` for the taboos,
   `inventoryOptions` for carried signature items.
5. **Fix `Medieval`** — six of our own tribal kinds ask for a tag with no carriers.
6. **Decide the Deepwater Compact's weapon identity.** Harpoons do not exist; the two 6.8
   spear rifles are cut and are the cheapest route to one.
