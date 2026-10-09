# CANON_MATERIALS_DESIGN_1 — canon Star Wars materials: what they are for and where they come from

2026-10-09, FOUNDRY. **Draft for the owner's review.** Nothing here is ruled except the lines marked RULED.
Item: `CANON_MATERIALS_DESIGN_1` (parent `MINERALS_WHERE_THEY_BELONG_1`). Placement numbers live in
`design/RimMandrake/mineral_abundance_registry_2026-10-03.csv`; this doc decides *roles* and *channels*,
the registry carries the amounts.

## 0. What is already ruled (do not reopen)

- RULED 2026-10-03 and 2026-10-09 (cards): precious metals and gems only in their home biomes; vanilla
  plasteel becomes **durasteel** and the three donor durasteels retire into it; deep drilling = iron
  everywhere, everything else by home biome.
- RULED, owner typed 2026-10-09: *"I've ruled this before. All three will exist. Duranium and Doonium are
  mostly salvage and possibly rare trade."* (2026-10-03 typed: both made offworld, pretty rare, REQUIRED to
  build large ship and machine types such as factories.)
- RULED 2026-09-25 typed: components and plasteel are never mined from rock; salvage is a major source of
  advanced materials.

## 1. Inventory — canon materials the game supports today

Method: a parse of every `Defs/**/*.xml` under `src/` for top-level defs whose defName or label names a canon
material (sanity probe: beskar returns 6 defs; durasteel 13), joined with the 2026-10-03 registry inventory
(26,589 ThingDefs from the live-set def dump, 73 mineral materials). `S` = has `stuffProps`.

| material | defs that carry it today | form today | owner |
|---|---|---|---|
| beskar / Mandalorian iron | `KOTOR_RawBeskar`, `KOTOR_IngotBeskar` (S), `KOTOR_MineableBeskar`; Outer Rim `OuterRim_Beskar`, `OuterRim_PureBeskar` (+ floors); LK `LKBeskar_Ore` | ore + ingot + stuff | Armoury (ours), Outer Rim, LK |
| durasteel | `KOTOR_AlloyDurasteel` (S), `KOTOR_MineableDurasteel`, slag + smelt recipes, `ShipChunk_durasteel`, powered durasteel walls; `OuterRim_Durasteel`; `LKDurasteel_Ore` | alloy + ore | Armoury, Outer Rim, LK → **merging into plasteel** |
| plasteel (canon name too) | Core `Plasteel`; KotOR smelt/slag recipes | Core stuff | Core |
| cortosis | `KOTOR_IngotCortosis` (S), `KOTOR_MineableCortosis`, `guy762_armband_cortosis` | ingot | Armoury |
| bronzium | `KOTOR_AlloyBronzium` (S), `KOTOR_MineableBronzium`, slag, bronzium light battle armor | alloy | Armoury |
| plastoid | `KOTOR_Plastoid` (S), smelt recipes | stuff | Armoury |
| kyber | `Force_KyberCrystal`, `Force_CrystalFormation_*` (Lantern Deeps scatter `RUT_LanternDeepKyberScatter`), synthetic/bled/cleansed crystals, kyber quests | crystal | SW The Force, ours |
| stygium | `KOTOR_StygiumCrystal`, `guy762_crystalitem_stygium`, stygium cloaking research | crystal | Armoury |
| tibanna | `KOTOR_Tibanna` + pipe net, `RUT_TibannaGas`, `OuterRim_Tibanna` | gas / item | Armoury, ours (beldon herds, the Forge) |
| rhydonium | `KOTOR_RawRhydonium`, `KOTOR_Rhydonium` fuel, rhydonium reactors, drug chain | fuel + drug | Armoury |
| spice | `KOTOR_Spice`, `KOTOR_MineableSpice`, drug chain | drug | Armoury |
| baradium | `KOTOR_Research_Baradium` only (explosives research) | research | Armoury |
| agrinium | `RSW_DW_Module_DroidArmorLte_agrinium` (droid armor module) | name only | ours |
| zersium | `guy762_brifle_zersium` (a rifle's name) | name only | Armoury |
| bacta | `RSW_Bacta`, patch, spray, tank | medicine | ours — **out of scope** (medicine, not a material) |
| duranium, doonium | none yet; registry rows `RSW_Duranium`, `RSW_Doonium` (RULED to exist) | — | to build |

Not in the game anywhere (checked: 0 defs in `src/`; installed-mod sweep in §1a): phrik, transparisteel,
lommite, aurodium, chromium, quadanium, coaxium, impervium, thorilide, dolovite, corusca, carbonite,
hyperbaride, laminanium, ultrachrome, alusteel, neutronium, ferrocarbon.

### 1a. Beyond `src/`

The active-set picture is the 2026-10-03 registry inventory (def dump of the live mod set): canon materials
from other active mods are Outer Rim - Core (beskar, pure beskar, durasteel, tibanna) and LK mineables
(beskar ore, durasteel ore). A sweep of every *installed* (incl. inactive) mod's Defs for the canon names was
started and did not finish inside this pass over the slow `/mnt/c` mount — **UNMEASURED** for inactive mods.

**Measured leak relevant to the minerals rulings (2026-10-09):** Odyssey's own asteroid generation
(`Data/Odyssey/Defs/MapGeneration/SpaceMapGenerator.xml`, `GeneratedLocations.xml`) names `MineablePlasteel`,
`MineableGold`, `MineableSilver`, `MineableUranium`, `MineableJade` and `MineableComponentsIndustrial`. So
asteroid maps mine plasteel (= durasteel after the rename) and components from rock, which the 2026-09-25
ruling forbids, unless the minerals work patches it. GPT raised the same point independently.

## 2. Canon — what each material is for (Wookieepedia, canon pages, pulled 2026-10-09)

Source: `starwars.fandom.com/api.php` `action=parse&prop=wikitext` on the **canon** page (not `/Legends`),
titles resolved with `list=search`. One line of canon use, then the orthogonal ROLE proposed for the game.

| material | canon (sourced) | proposed game role (one axis each) |
|---|---|---|
| **durasteel** | Galaxy-wide alloy: armor, buildings, crates, stuncuffs, military ship plating; "more resistant than standard steel", protects against kinetic damage; **zersium** ore is critical to making it | the workhorse super-metal (replaces plasteel): structure, armor, advanced crafting |
| **beskar** | Mandalorian iron; armor that withstands blaster fire and repels lightsabers; "found only on Mandalorian worlds"; reforgeable; making weapons of it taboo to the Children of the Watch | apex *personal armor*; heirloom; never mass-produced |
| **cortosis** | extremely rare; absorbs energy (dissipates blaster bolts), can short out a lightsaber; **brittle and porous in its natural state**, useless as armor unalloyed; cortosis helmets hide the wearer's thoughts from Force users | *anti-energy / anti-Force* — shields, dampers, psychic-hiding helmets; never bulk armor |
| **phrik** | rare robust alloy, lightsaber-resistant; mined on Gromas and **Tatooine (Mos Algo mine)**; electrostaffs, Sidious's lightsabers; weaker than cortosis | *lightsaber-proof WEAPONS* (staffs, blades) — the weapon twin of beskar's armor |
| **duranium** | tough military-grade plating, stronger than titanium, less resilient than impervium; Grievous's armor, MagnaGuard frames | *heavy frames*: large machines, war droids, factory structures (owner: required for large ship/machine types) |
| **doonium** | heavy metal used primarily for **starship construction**; Empire stockpiled it for the Death Star, essential (with dolovite) in **shielding the hypermatter reactor core**; mined on many planets and asteroid fields | *reactors and ship cores* — power plants, gravship engines/cores, radiation shielding |
| **transparisteel** | hardy transparent alloy for windows and canopies; can be blaster-proof; **lommite** ore is a major component | *see-through strong wall/window*; cockpit canopies |
| **plastoid** | armor plastic (clone and stormtrooper armor), impervious to chemical warfare, vulnerable to blaster fire | *light sealed armor* — tox/gas/vacuum protection, cheap mass armor |
| **bronzium** | bronze-coloured alloy for statues, decorative finishes, some armor | *art and furniture beauty*, cheap decorative alloy |
| **aurodium** | yellow metal rarer than gold; currency standard (Cantonica), jewellery, a lightsaber hilt | *luxury / currency* metal (the galaxy's gold) |
| **chromium** | rare valuable metal; royal Naboo ship plating; reflects some radiation; chromium–titanium alloy needed in hyperdrives; mined on a Naboo moon | *plating / prestige finish*; hyperdrive alloying |
| **quadanium** | metallic substance for ships and battle stations (Death Star hull plates, TIE wing frames), turbolasers, shields; sold for 30 credits/unit | overlaps duranium/doonium — **candidate to fold in, not add** |
| **kyber** | Force-attuned living crystal; lightsabers; large ones at the heart of superweapons | *Force/energy focus* (already ours: Lantern Deeps only) |
| **stygium** | crystals that power cloaking devices (TIE Phantom, Scimitar) | *stealth* |
| **tibanna** | reactive gas: hyperdrives, repulsorlift coolant, fuel, **supercharges blaster bolts** | *weapon gas / coolant* (RULED: beldon herds) |
| **coaxium** | hyperfuel, rare hypermatter, mined on Kessel; raw form unstable and explodes if not kept cold | *long-range gravship fuel*; volatile cargo |
| **rhydonium** | volatile starship fuel, explosive, toxic fumes, an addictive high | *dirty fuel* + drug (already modelled) |
| **carbonite** | carbon-freezing: preserves goods and people; used to transport tibanna and coaxium | *stasis / preservation* |
| **thorilide** | prized crystal for turbolaser shock absorbers, mined with baradium | *turret component* |
| **zersium** | mineral ore essential to durasteel; Nag Ubdur's bedrock flecked with it | *the local ore of durasteel* |
| **lommite** | ore used to make transparisteel; scattered surface deposits on a desert planetoid | *the local ore of transparisteel* |
| **dolovite** | mined on the lava worlds Mustafar and Samovar; refined to a crimson alloy; with doonium shields reactor cores | *lava-biome mineral* |
| **corusca gem** | extremely rare valuable gemstone (Sarka); smuggler's cargo | *luxury trade gem* |
| **hyperbaride** | valuable mineral on Mimban (a mud world), mined by dangerous energy mining | *swamp-biome mineral* |
| **baradium** | volatile synthetic explosive: thermal detonators, mining charges | *explosives* (research exists) |

Not proposed: impervium, laminanium, ultrachrome, alusteel, neutronium, ferrocarbon, agrinium — canon
stubs of one or two sentences that only duplicate a role above.

## 3. Three candidate designs (kept alive deliberately)

The five origin channels every design draws from: **L** local biome mining (vein, nodule, crystal — via
the registry), **S** salvage (wrecks, Rust Cathedral, Warscar troves, crashed ships, Odyssey orbital
debris and mech-ship chunks), **A** asteroid mining (Odyssey `AsteroidMiningSite` / `Asteroid` space maps,
reached by gravship), **T** offworld trade (Bazaar, orbital traders), **H** herds/creatures (tibanna
beldons — RULED). Each design answers the same two questions — what is it FOR, and where does it COME FROM —
from a different first principle.

### Design 1 — "The ladder" (a material is a TIER)

First principle: materials are a progression; the further up, the further away it comes from.

| tier | material | for | from |
|---|---|---|---|
| 0 | steel | everything basic | L (iron where the biome has it) |
| 1 | durasteel (= plasteel) | advanced structure, armor, weapons, gravship hull | S + T; L only as zersium ore in two or three industrial biomes, smelted |
| 2 | duranium | large machines, war droids, factory buildings (owner rule) | S (crashed capital ships, mech-ship chunks), rare T |
| 3 | doonium | reactors, gravship cores/engines, big power plants | S, rare T, A (asteroid seams) |
| apex | beskar · cortosis · phrik | best armor · anti-energy gear · lightsaber-proof weapons | S only (troves, Mandalorian wrecks), never mined |
| side | kyber · stygium · tibanna · coaxium | lightsabers · cloaking · blaster gas · long-range fuel | L Lantern Deeps · S · H beldons · T/A |

Strength: one glance tells a player what is better; easy to balance; gating is natural (a factory needs
tier 2). Weakness: it collapses toward "bigger numbers" — duranium vs durasteel reads as +20% rather than a
different job, which is exactly the orthogonality the owner asked for. Cortosis, phrik and beskar compete
for the same "apex" slot.

### Design 2 — "One job each" (a material is a FUNCTION)

First principle: no two materials do the same job; every material owns one verb the game cannot do
without it, and is otherwise mediocre.

| material | owns this job | deliberately bad at | from |
|---|---|---|---|
| durasteel | bulk structure, general armor, advanced crafting (vanilla plasteel's whole role) | nothing special — the baseline | S + T; L zersium ore (industrial biomes) |
| duranium | **frames of anything bigger than a pawn**: factories, big droids, turret mounts, ship hull plates | personal gear (too heavy) | S, rare T |
| doonium | **power and shielding**: reactor cores, gravship engine/core, radiation shielding | structure, armor | S, rare T, A |
| beskar | **personal armor** vs blades and bolts; reforgeable heirloom | weapons (taboo), structures | S only |
| phrik | **weapons that survive a lightsaber** (staffs, vibro-blades) | armor | L Stillsand (canon: Tatooine mine) + S |
| cortosis | **energy absorption**: shields, Force-dampening helmets, saber-shorting | anything raw (brittle — must be alloyed into weave) | S + T, never mined |
| transparisteel (from lommite) | **walls you can see through**: windows, canopies, observation domes | cheapness | L lommite in a desert biome, smelted with durasteel |
| plastoid | **sealed light armor**: tox/gas/vacuum protection, cheap mass armor | blaster bolts | crafted from chemfuel/neutroamine (no ore) |
| bronzium | **beauty**: statues, furniture, decorative finishes | combat | crafted alloy (steel + copper-ish salvage) / T |
| aurodium | **money and jewellery** (the galaxy's gold; currency standard) | anything practical | T, home-biome trace (precious ruling) |
| kyber | **focusing the Force/energy**: lightsabers, superweapon cores | — | L Lantern Deeps only (built) |
| stygium | **stealth**: cloaking fields, invisibility gear | — | S + T |
| tibanna | **weapon gas and coolant**: blaster supercharge, repulsor cooling | — | H beldons (RULED) |
| coaxium | **gravship range** (hyperfuel) — volatile, must be kept cold | storage | A + T, never local |
| carbonite | **stasis**: preserve food, prisoners, volatile cargo (coaxium/tibanna) | — | crafted / T |

Strength: every material is wanted for one reason and the reason is canon. Weakness: 15 materials, each
needing a consumer, art and balancing — a material without a consumer is dead content; overlaps with
existing vanilla jobs (plasteel, uranium, gold) must be resolved one by one.

### Design 3 — "Where it comes from IS what it is" (a material is a PROVENANCE)

First principle: the Jawa clan is a scavenger culture; origin is the gameplay, and each origin class gets a
small number of materials with a shared flavour of use.

| origin class | materials | shared use flavour |
|---|---|---|
| **Dug here** (L, per biome, registry) | zersium (→ durasteel), lommite (→ transparisteel), phrik (Stillsand), dolovite (the Forge/Pyrelands), hyperbaride (the Sump/Miasma), kyber (Lantern Deeps) | crafting inputs — the colony *makes* things from its land; each biome's ore makes that biome worth settling |
| **Pulled from wrecks** (S) | beskar, duranium, cortosis, quadanium-as-scrap, plastoid plate, durasteel scrap | reclaim and repurpose — gear and parts you cannot make, only recover and refit; the clan's identity |
| **Brought from orbit** (A, T) | doonium, coaxium, aurodium, corusca, chromium | the endgame — big ship and factory builds, range, wealth; requires a gravship or a trader |
| **Grown / herded** (H) | tibanna | (already ruled) |

Strength: placement and use explain each other; the salvage identity the owner named is front and centre;
every biome gets a reason to exist. Weakness: uses are thinner per material (a "provenance flavour" is not
a mechanical job), and it adds several new local ores that each need a biome sitting.

### What the three share (and so is probably safe whichever wins)

- Durasteel is the one bulk super-metal; no other material competes for plasteel's job.
- Duranium and doonium are salvage-first, rare trade, and gate large machines/ships (owner rule) — the
  designs differ only on whether duranium (frames) and doonium (power/cores) split that gate.
- Beskar is salvage-only and personal-armor-only.
- Kyber stays Lantern Deeps; tibanna stays beldon herds.

## 4. GPT review (gpt-6.1-sol, high effort, 2026-10-09)

Full answer: `design/RimMandrake/canon_materials_gpt_consult_2026-10-09.md`. Its main points:

**Corrections it says apply to every design:**
- Duranium and doonium should **not** come from asteroid seams. Under the owner's "made offworld" ruling they
  are finished material recovered from wrecks, including orbital wrecks, with rare trade second. (Design 1's
  and Design 2's "A" for doonium is withdrawn on this point.)
- No naturally generated precious metals or gems in orbit.
- Renaming plasteel is not enough. Surface veins, deep resources, meteorites, asteroid generation and donor
  mineables must all be patched (see §1a).
- A cheap local zersium → durasteel chain would make salvage irrelevant. Keep it only as a deliberately
  limited alternative.
- Large factories and ships should need **both** duranium (frame) and doonium (containment), with neither
  convertible into the other. Illustrative cost only: factory = 80 durasteel + 20 duranium + 6 doonium + 8
  components.
- **Ground salvage must supply the first construction quantities** before orbit is needed, or progression
  locks itself.

**Its critique of ours:**
- **D1 (ladder):** clearest to learn, but the tiers read as "better metal". Repair: make the tiers about
  access, and use duranium and doonium as fixed recipe ingredients.
- **D2 (one job each):** best base for orthogonal materials, but 15 inventories bring too many shortages and
  dead consumers. Repair: a material is switched on only once a working consumer exists.
- **D3 (provenance):** strongest Jawa identity, but knowing where something comes from does not tell you what
  to build. Repair: give every resource a verb, and put both required alloys in ground wrecks.
- *"The recurring danger is adding a material to justify a biome, then adding a building to justify the
  material."*

**Its three designs:**

| | D4 — fixed recipe functions | D5 — recover and refit (Jawa workshop) | D6 — expedition logistics |
|---|---|---|---|
| idea | advanced alloys are recipe ingredients, not universal stuff | progress = dismantling identifiable wrecks and refitting gear | construction buys capability; renewable supplies set how far the clan can travel |
| roster | durasteel Build, duranium Brace, doonium Contain, beskar Protect, cortosis Disrupt, plastoid Seal, bronzium Decorate, kyber Focus, stygium Conceal, tibanna Charge, baradium Demolish (11) | D4 minus bronzium, plus phrik Parry (Stillsand), carbonite Preserve; origins named by wreck part (machine chassis → duranium, reactor assembly → doonium) (12) | D4 plus transparisteel Observe (lommite), rhydonium Burn, coaxium Extend (optional gravship range booster; chemfuel flight stays), carbonite Preserve (14) |
| best for | delivery and readable recipes | scavenger identity | Odyssey nomad play |
| weakness | little processing or logistics | refitting needs condition/UI work | heaviest chore load |

**Its overlap and roster rulings (advice only):**
- Fold into durasteel: quadanium, alusteel, ferrocarbon.
- Do not add: impervium, laminanium, ultrachrome, neutronium.
- Avoid intermediate ores (zersium, lommite) unless processing is a chosen loop.
- Defer: dolovite, hyperbaride, thorilide, agrinium.
- Aurodium, corusca and chromium only as named valuables (home-biome only). Keep silver as currency and gold's
  vanilla roles.
- Phrik, transparisteel, carbonite and coaxium are conditional, each on a real consumer: saber-parry, sight
  through walls, portable stasis, range booster.
- Beskar's weapon taboo belongs to the Children of the Watch. Armor-only for Jawas is a design choice, not
  universal canon.
- Mechanics: keep the `Plasteel` defName and rename only its label. Avoid giving specialist materials
  `stuffProps` `Metallic`, because that leaks them into every wall and weapon. Cortosis, phrik and stygium
  need real C# effects; armor factors alone cannot short out a lightsaber.

**Its ranking (for review priority, not elimination):** D4, D5, D2, D6, D3, D1. It asks that all six stay
available until the owner chooses which play loop the campaign emphasises.

Unchecked GPT claims: it cites Ludeon's Odyssey blog and a GitHub data mirror. The asteroid point was
re-measured here (§1a) and holds. The gravship fuel-tank `Chemfuel` filter is **UNMEASURED** by us.

## 5. Recommendation and what the owner decides

All six designs stay live. They split along **one question that only the owner can answer: which play loop
should materials serve?**

| if the campaign is mainly about… | pick | consequence |
|---|---|---|
| building a colony that becomes capable | **D4** (or D1 for the gentlest learning curve) | ~11 materials, mostly recipe ingredients; cheapest to build |
| being Jawas: wrecks, scrap, refitted heirlooms | **D5** (or D3 for the biome-exploration flavour) | wreck types become the content; refit system is real C# work |
| travelling: gravship range, volatile cargo, herds | **D6** | most materials and chores; leans hardest on Odyssey |
| a rich specialist crafting map | **D2** | most consumers to build; switch a material on only with its consumer |

**FOUNDRY's recommendation:** use **D5's identity with D4's discipline**. Durasteel, duranium, doonium,
beskar, cortosis, plastoid, kyber, stygium, tibanna and baradium form the core 10. Each is a fixed
ingredient with one verb, and each is sourced the way D5 says: by recognisable wreck part, so a salvaged
machine chassis gives duranium and a reactor assembly gives doonium. Ground wrecks supply the first lots.
Phrik, transparisteel, carbonite and coaxium are a **second wave**, each switched on only when its consumer
(parry, windows that matter, portable stasis, range booster) is built. Aurodium, corusca and chromium are
named valuables only. Fold quadanium into durasteel and drop the rest of §2's stubs.

Decisions for the joint sitting (none are rulings yet):
1. Which play loop (table above), and so which design is the base?
2. Should duranium **and** doonium both be required for large builds (frame + containment), or is one enough?
3. Phrik: worth a saber-parry mechanic (Stillsand, canon Tatooine source), or fold it into durasteel?
4. Should local precursor ores exist (zersium → durasteel, lommite → transparisteel), or stay abstract in
   recipes?
5. Beskar: armor-only for everyone, or weapons allowed outside the Children of the Watch?
6. The Odyssey asteroid leak (§1a): patch it under the minerals work (it mines plasteel and components)?
