# Canon metal fabrication — what the factory ship can forge (2026-10-09)

Canon research; no defs changed. The owner ruled on it 2026-10-09; the rulings and the resulting routes live in
`design/RimMandrake/canon_materials_design_2026-10-09.md` (§0, §3), which is the single source of truth. Companion
also to and `design/RimMandrake/mineral_abundance_registry_design_2026-10-03.md` (amounts).

Owner's request, typed 2026-10-09: *"look at how the factory ship is likely able to forge some of this stuff.
Look up the canon requirements for making some of those metals, for example (other ores that might be added
to the world or asteroids... look for the canon sources to check viability here)"*. Then, same day:
*"I'm ok having some things just be import only"*. So verdict (a) is a full answer, not a fallback, and
nothing below stretches canon to make a material forgeable.

**Verdicts:** (a) salvage/trade/import only · (b) re-forgeable from salvage on the factory ship (melt and
reshape existing stock; nothing new is created) · (c) forgeable on the factory ship from named inputs, which
then need a world or asteroid source · (d) needs a facility we do not have (later-game unlock).

**Method.** Wookieepedia API, pulled 2026-10-09: `list=search` to resolve every title, then
`action=parse&prop=wikitext`, 48 pages. **Canon** = the page without `/Legends`; **Legends** = the `/Legends`
page, or a page carrying `{{Top|leg}}` (Carvanium, Ferrocarbon, Phrikite, Phrik metal mine, Quadanium
Refinery, Fusion smelter are Legends-only). Each claim names the Wookieepedia page and the source that page
cites.

## Summary

| material | canon inputs | canon process / facility | ruled route (design §3) | new ores |
|---|---|---|---|---|
| durasteel | **zersium** ore (Canon). Legends: iron, carbon, carvanium, lommite, meleenium, neutronium, zersium | Legends: metallurgical plants, durasteel foundries, fusion smelters | salvage re-melt; steel + zersium on the ship smelter or early alloy forge (TO CONFIRM) | zersium (source TO CONFIRM) |
| plasteel | none named in Canon. Legends: "acrylic polymers and metal alloys" | none in Canon | salvage re-melt; trade; late alloy-forge recipe. Other craft routes removed | none |
| plastoid | none named | none named | **(c)** from chemfuel, as built. A plastic, not a metal | none (oil/biofuel) |
| duranium | none named in either | Legends: "very high melting point, making it difficult to shape" | **(a)**: salvage and rare trade; repair with it, never re-forge it | none |
| doonium | Canon: an ore, mined on planets **and asteroid fields** | Canon: an Imperial mine plus refinery (Ryloth) | salvage, rare trade, asteroid ore smelted aboard with glower crust | doonium ore (asteroids) |
| beskar | Canon: found only on Mandalorian worlds | Canon: the Armorer's cryo-furnace, magnetic tongs, gravity hammer; a guarded Mandalorian secret | used as found; smelting destroys it; only a Mandalorian armorer (Blackstar quest) reforges | none |
| cortosis | Canon: a metal found on Dinzo, Mokivj, Bal'demnic | Canon: useless raw ("soft and frangible"); must be woven into a protective matrix | **(a)** | none |
| transparisteel | **lommite** ore (Canon) | Canon: lommite processing plants (Eriadu). Legends: press-formed into sheets | sifted from extreme-desert fine sand; replaces all glass; also traded | none (fine sand, built) |
| phrik | **phrikite** ore (Legends); Canon names no ore but mines phrik **on Tatooine** | Legends: refined and purified at the mine; alloyed with tydirium | trade and a rare desert phrikite deposit smelted aboard | phrikite (desert) |
| bronzium | none named | none named | dropped from the game | none |
| quadanium | none named | Legends: SoroSuub Quadanium Refinery (Sullust) | folded into durasteel (no def) | none |
| alusteel | none named | none named | folded into durasteel (no def) | none |
| ferrocarbon | Legends-only: iron + carbon | none named | is steel in all but name (no def) | none |

**Bottom line.** Canon gives the sandcrawler a **reactor that melts scrap** and calls it a **mobile mining and
smelting facility**. That supports re-melting ordinary alloys (durasteel, plasteel) aboard and smelting simple
ores (doonium, phrikite). Duranium and cortosis stay salvage and trade; beskar is reforged only by a Mandalorian
smith. The routes the owner chose from this research are in the design doc, §3.

## 1. What the factory ship can do in game today

**The ship as exported** (`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\GravshipExport\The_Utinni.xml`,
`ShipLayoutDefV2`; `Gravship.xml` is the same set) carries exactly these production buildings:
`VFEFactory_AutomatedSmelter`, `VFEFactory_AutomatedMachiningBay`, `VFEFactory_MedicineGranulator`,
`VFEFactory_Booster`, 2× `VFEFactory_Heatsink`, 14× `VFEFactory_FactoryHopper`. **No alloy forge, assembler,
grav forge, plasma furnace or electric smelter is aboard.** (Bronzium appears only as the stuff of 4 placed
things.)

**Planned, not built** (`D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\ship_deck_plan.md` §2, phase table):
Wing B smelter first (phase 2, "salvage → metal; the engine of everything"); Wing E assembler + **alloy
forge** + neutroamine at phase 5, "Fabricate: components, plasteel, gravlite". The 7 rim pods of
`D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\ship_distinctive_features.md` §6 include a forge pod and
a raw-extraction pod.

**Buildable in the live mod set (622 active) that touch these materials** — measured from `src/` RecipeDefs
and VFE Factory's `1.6/Defs/ProcessDefs/ProcessDefs_AlloyForge.xml` (workshop 3686924415):

| route | building | inputs → output | under the ruled design |
|---|---|---|---|
| `VFEFactory_AlloyPlasteel` | VFE Automated Alloy Forge (5×5) | Steel + Chemfuel + Gold → 5 Plasteel | kept: the late alloy-forge plasteel recipe |
| `Make_PlasteelGF` | `GravForge` (ours, ported, `src/RimUtinni/ResearchRetag/Defs/ThingDefs_Buildings/RUT_Ported_GravForge.xml`) | 50 Steel + 50 Chemfuel + 3.5 Silver → Plasteel | removed |
| `kotor_Plasteel_recipe` (+10×) | `kotor_PlasmaFurnace` (Armoury) | 5 Plastoid + 5 Steel → Plasteel | removed |
| `kotor_IngotDurasteel_recipe` (+10×) | `kotor_PlasmaFurnace` | 5 Steel + 2 Uranium → durasteel | removed (steel + zersium replaces it) |
| `KotORRecipe_PlasteelFromSlag` / `…DurasteelFromSlag` / `…BronziumFromSlag` | `ElectricSmelter`, `kotor_PlasmaFurnace` | one salvage slag chunk → the metal | kept (salvage re-melt); bronzium's removed |
| `kotor_IngotBeskar_recipe` (+10×) | `kotor_PlasmaFurnace` | 3 raw beskar → beskar ingot | removed: the colony never reforges beskar |
| `KOTOR_Plastoid_recipe` (+10×) | `ElectricSmelter`, `kotor_PlasmaFurnace` | 20 Chemfuel → plastoid | consistent (design channel F) |

Not traced here: Rimefeller's `UncuredPlasteel` (listed in the registry's donor oddities) may be a fourth
plasteel route; and whether the VFE Automated Smelter accepts `KotORChunk_*` slag (UNMEASURED: its
`ProcessDefs_AutomatedSmelter.xml` was not read).

Under the ruled design (§3.3, §3.4 there), the alloy forge's plasteel recipe is kept as a late unlock and the
GravForge and plasma-furnace plasteel routes and the steel + uranium durasteel recipe are removed; bronzium is
dropped with its slag recipe.

## 2. Canon Jawa / sandcrawler fabrication capability

- **Sandcrawler (Canon page):** "Built by the Corellia Mining Corporation as massive mobile mining and smelting
  facilities … intended … to serve as semi-autonomous mining operations in rough frontier worlds", powered by
  "primitive but reliable nuclear fusion steam reactors" — cites *Star Wars: The Galactic Explorer's Guide*
  and the StarWars.com Databank. They hold "scrap-processing facilities", a magnetic suction tube for droids
  and scrap, and holds for 1,500 droids. **"Inside the sandcrawler, Jawas typically utilized the reactor to
  melt down scrap metal and droids"** — cites *Star Wars Encyclopedia: The Comprehensive Guide* and
  *Episode IV*. The mining boom ended when "the most valuable minerals were found on the surface, making
  sandcrawlers unnecessary" (*Attack of the Clones* era).
- **Sandcrawler/Legends:** Czerka and Corellia Mining Corporation left them on Tatooine because "the ore was of
  very poor quality, corroding very fast"; equipped with "magnetic cranes, energy furnaces, workshops".
- **Jawa (Canon):** scavengers who sell "hastily refurbished equipment"; ion blasters and restraining bolts for
  droids. In *The Mandalorian* Chapter 9 a Jawa band holds Boba Fett's **beskar armour** and trades it to Cobb
  Vanth — Jawas handling beskar as salvage is canon. **Jawa/Legends:** "an instinctive feel for machinery …
  getting a piece of equipment functioning just well enough to sell".
- **Smelter droid (Canon):** built for "ore-extraction facilities" (8D series, Roche). **Legends:** "smelting
  task, such as disintegrating droids, refining metal or forging weapons".
- **Fusion smelter (Legends-only):** "an industrial machine that produced molten durasteel" (*Revenge of the
  Sith* novelization).

**What that licenses.** A sandcrawler-class ship is canonically a **smelter**: it melts scrap and droids
into metal, and was built to smelt ore it mined itself. It is **not** canonically a refinery for exotic ores,
a lommite plant, a Mandalorian forge, or a shipyard. So: melting and recasting ordinary alloys is in
character; creating a rare alloy from raw ore is not, except where the ore and process are simple.

## 3. Per material

### Durasteel
- **Canon** (Durasteel): "a type of metal alloy", "more resistant than standard steel"; "Zersium was an ore
  critical to the making of durasteel" (*Aftermath: Life Debt*). **Zersium** (Canon): the bedrock of Nag
  Ubdur, strip-mined by the Empire (*Aftermath: Life Debt*); the only canon locale.
- **Legends** (Durasteel/Legends): "produced in metallurgical plants or specialised durasteel foundries";
  "composed of iron, carbon and various heavier elements, including carvanium, lommite, meleenium,
  neutronium, and zersium" (*The Complete Star Wars Encyclopedia*); used for "smelting pots for less durable
  metals". Zersium/Legends: Koratas, Dor. Carvanium (Legends-only): Mygeeto; Null-5 sabotaged droid foundries
  by adding 5% extra carvanium. Fusion smelter (Legends): makes molten durasteel.
- **Factory ship:** making new durasteel needs zersium plus a foundry recipe of five exotic elements, which
  the owner already ruled out. Re-smelting durasteel salvage (slag, ship chunks) is what a scrap-melting
  sandcrawler does, and is what `canon_materials_design` §3.2 now also proposes steel + zersium aboard.

### Plasteel
- **Canon** (Plasteel): "a hard material"; no ingredients or process named anywhere on the page; uses as in
  `canon_materials_design` §2a (B1 droids — *Queen's Peril*; masks, greaves, M3 blast shields).
- **Legends** (Plasteel/Legends): acrylic polymers combined with metal alloys; construction droids extrude
  plasteel girders. Neither names an ore.
- **Factory ship:** canon gives no recipe to build, so a recipe would be invented, not sourced. Re-forming
  plasteel salvage chunks is already built (`KotORRecipe_PlasteelFromSlag`).

### Plastoid
- **Canon** (Plastoid): armour material; stormtrooper "plastoid composite … impervious to chemical warfare"
  (*Thrawn: Alliances* et al.). **Legends:** "plasarmor"; plastoid tubing reinforces Mos Eisley walls.
  No inputs named in either.
- **Factory ship:** a plastic; making it from chemfuel at a smelter is the built route and the design's
  channel F. No world source needed beyond oil/biofuel.

### Duranium
- **Canon** (Duranium): "a tough alloy used in military-grade plating … stronger than titanium but less
  resilient than impervium" (*Star Wars: Galactic Defense*); Grievous's armour, MagnaGuard frames. No source
  world, no inputs.
- **Legends** (Duranium/Legends): high tensile strength; "a very high melting point, making it difficult to
  shape"; prison cells and cages.
- **Factory ship:** nothing to forge it from, and Legends says it resists reshaping. Salvage and rare trade,
  used as found for frames and repairs, exactly as ruled.

### Doonium
- **Canon** (Doonium): "a heavy metal … used primarily for starship construction … found and mined on
  numerous planets and asteroid fields", naming Batonn, Umbara, Samovar, Lothal and the **Socorro asteroid
  belts** (*Catalyst*, *Thrawn*); Ryloth (*The Bad Batch*). Essential with dolovite in shielding the Death
  Star's hypermatter reactor core. **Imperial doonium refinery** (Canon): Ryloth, pipelines "into the depths
  of a large mountain", a garrisoned Imperial installation (*Galactic Atlas*).
- **Legends:** Imperial hull plating; Thrugii Asteroid Belt (Socorro), Dor, Atraken.
- **Factory ship:** doonium is an ore in canon, and asteroid fields are a named home, so Odyssey asteroid maps
  are a canon-true place for it. Smelting a heavy-metal ore is within a mining sandcrawler's job; the canon
  refinery is an Imperial installation, though, and the owner ruled doonium "made offworld".  Dolovite (Canon: Mustafar, Samovar, Burnin
  Konn, all lava worlds) is the canon partner for reactor shielding; it needs no def until a consumer exists.

### Beskar
- **Canon** (Beskar): "Beskar was found only on Mandalorian worlds" (*The Star Wars Book*); Concordia and
  Mandalore. The Armorer "used a cryo-furnace, magnetic tongs, and a gravity hammer" to forge it (*The
  Mandalorian* Chapter 3); "the Mandalorian method for forging beskar was a closely guarded secret" (Databank,
  The Armorer's forge). Din Djarin's Imperial-stamped beskar ingots were melted and reforged (Chapter 3): re-forging
  salvage is canon, **for a Mandalorian smith**.
- **Legends:** only source Mandalore and Concordia; carbon added in the foundry; techniques guarded by
  metalsmiths "who would sooner die than reveal their secrets".
- **Factory ship:** no ore on our world, and the skill is not the Jawas'. The canon Jawa relationship to
  beskar is trading a found suit (Chapter 9). 

### Cortosis
- **Canon** (Cortosis): found on Dinzo (an Imperial secret mine — *Rebels Magazine*), Mokivj (*Thrawn:
  Alliances*), Bal'demnic (*The Acolyte*). Thrawn: "soft and frangible, useless for building into armor …
  they've found a method for weaving the cortosis into a network within a protective matrix".
- **Legends:** "very rare, brittle, fibrous"; "had to be absolutely refined"; raw ore lethal to touch; mining
  wears out hydraulic jacks.
- **Factory ship:** raw cortosis is useless and the weave is specialist tech. **(a)**; the registry's
  "not mined" ruling matches canon.

### Transparisteel
- **Canon** (Transparisteel): windows and canopies; "A major component of transparisteel was lommite ore"
  (*Rise of the Rebels*). **Lommite** (Canon): shipped from Eriadu; mined on Didyma V; "scattered deposits were
  found on the surface of the desert planetoid Arvala-7" (*The Mandalorian Visual Guide*). **Lommite
  processing plants** (Canon): in Eriadu City (*Tarkin*).
- **Legends:** "press-formed into thin, transparent sheets"; Lommite/Legends: Dorvalla, Elom, Ord Thoden;
  also a durasteel constituent.
- **Factory ship:** the ore suits a desert surface, but canon processing is a city's plant. 

### Phrik
- **Canon** (Phrik): "a rare and robust alloy … mined on Gromas … and Tatooine"; "mined at the Mos Algo mine on
  the desert planet Tatooine" (*Star Wars Outlaws*); Baktoid electrostaffs; weaker than cortosis.
- **Legends:** Phrikite (Legends-only): "the source ore for the metal phrik", primary source Gromas 16;
  Phrik/Legends: combined with tydirium; "highly malleable" in its smelting stage; the Empire nationalised
  phrik mining. Phrik metal mine (Legends-only): Tatooine, Jundland Wastes, ore "refined and purified" on site
  with its own furnace.
- **Factory ship:** the one exotic metal canon places on a desert world, smelted at the mine. A deep
  phrikite deposit in a desert biome, smelted aboard, is the least-stretched forge route in this doc.

### Bronzium
- **Canon** (Bronzium): "a bronze-colored alloy" for statues, finishes, lightsabers, armour (*Tarkin*, *The
  Rise of Skywalker: Visual Dictionary*). **Legends:** droid finishes (C-3PO, droidekas); Wookiee bowcasters.
  No inputs named.
- **Factory ship:** only slag makes it; inventing an ore would be unsourced.


### Quadanium, alusteel, ferrocarbon — folded, no def
- **Quadanium steel** (Canon): Death Star hull plates, TIE wing frames, *Supremacy* armour (*Tarkin*, *TIE
  Fighter Owners' Workshop Manual*); sold 30 credits a unit in 3 ABY. Legends: SoroSuub's Quadanium Refinery;
  Despayre a source. **Alusteel** (Canon): Y-wing and *Executor* hulls. **Ferrocarbon** (Legends-only): iron +
  carbon, Coruscant foundations. None names inputs a sandcrawler could use, and all duplicate durasteel or
  steel. Keep them folded, as decided.

## 4. Ores

The ores the rulings add (doonium on asteroid maps, phrikite in a desert, zersium with its source still to
confirm) and their routes are in the design doc, §3.2 and §3.5. Canon homes: doonium — asteroid fields, the
Socorro belts (*Thrawn*, *Catalyst*); phrik — the Mos Algo mine, Tatooine (*Star Wars Outlaws*), phrikite ore
(Legends); zersium — the bedrock of Nag Ubdur (*Aftermath: Life Debt*). Dolovite (Mustafar, Samovar, Burnin
Konn) needs no def until a consumer exists. Not added: lommite (the desert's fine sand is the transparisteel
feedstock), carvanium, meleenium, neutronium, tydirium (Legends-only inputs).
