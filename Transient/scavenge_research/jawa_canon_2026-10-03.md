# Jawa canon + repo-lore research for the scavenger's nest / workshop (2026-10-03)

Tags: **[Canon]** current Wookieepedia canon page; **[Legends]** Wookieepedia /Legends page; **[Repo]** our own lore. Pulled via the Wookieepedia parse API (Jawa, Sandcrawler, Jawa/Legends, Sandcrawler/Legends, Jawaese, Jawa Trade Talk, Ion blaster, Jawa ionization blaster, Restraining bolt, Hydrospanner, Monster droid, "Life in a Jawa Sandcrawler"). `Utinni` resolves to a song page only.

## 0. Headline finding
**Canon and Legends give no real picture of a Jawa workshop.** What exists is: a sandcrawler holds "cargo holds, scrap-processing facilities, and quarters" [Canon, Sandcrawler]; Legends adds "magnetic cranes, energy furnaces, workshops" [Legends, Sandcrawler/Legends]; and ground-based Jawa "fortresses" with walls built from wrecked-ship chunks [Legends, Jawa/Legends]. Everything about shape (round, nest-like) is our invention. Anchor it on: the **fortress wall of wreck chunks**, the **hoard of wares** stored there, the **scent/odor** communal life, and the **monster droid** cobbling tradition.

## 1. Concepts (shape / footprint / top-down look / jobs)

### 1. The Wreck-Ring Fortress Nest  (best canon anchor)
- Source: Jawa/Legends: fortresses "nestled deep in the desert where their collected wares were stored", "high walls made from large chunks of old wrecked spacecraft" against Sand People, krayt, storms; scavengers return before storm season. [Legends]
- Shape: roughly circular ring 9-13 cells across; the wall is the build: hull plates, engine bells, tread links set on end. One low gate gap. Open or half-roofed centre.
- Top-down: dark scrap wall, ragged rim, central floor of sand-and-oil terrain, lamp glow from the gap.
- Jobs: storage hoard, sort floor, repair benches ringed against the inner wall, kid/egg safety (ties to Cold Nursery, [Repo] 05_the_clan: eggs ruin above 32 C, so a half-buried ring suits it).

### 2. The Sorting Wheel (spoke-and-bin)
- Source: Jawa motto "not to look for uses in a salvaged item, but to imagine someone else who might find a use for it" [Legends]; **27 Jawaese words for "junk"** [Canon, Jawaese]; repo rite "nothing taken from the sand is junk until the clan says so" (`RUT_Rites_ScrapShrine`) [Repo].
- Shape: circular 7x7: a central appraiser's stool/stand, ~8 radiating bins or tarps, each a different "kind of junk". The wheel IS the 27-words idea: sort into many kinds, appraise by who might want it.
- Jobs: sort lots (pitch option B), identify hidden-value parts (option C). Natural home of the Scrap Shrine rite ("spoken over").

### 3. The Hung Hoard (vertical rafters, hanging parts)
- Source: sandcrawler magnet crane / extendable suction tube dumping into holds [Canon]; QT-3PO's "incarceration" narrative notes servomotors and ion blasters [Legends, Life in a Jawa Sandcrawler].
- Shape: oval 5x9 under a lean-to; parts hung from a ridge line (cables, arms, pipe-lengths), shelves of motivators.
- Top-down: dangling-part sprites read as scattered dots with a drop shadow; the "mess" is the identity.
- Jobs: parts storage, quick-grab repair station, droid-part harvest (Droidworks drops).

### 4. The Droid Corral Workshop (pen + bench)
- Source: holds fit 1,500 droids [Canon]; ion blasters stun droids, restraining bolts control them [Canon]; monster/junk droids "at the request of customers" [Canon, Monster droid]; Jawas carry "various tools for repairing droids" [Legends].
- Shape: a half-circle pen of bolted-down droids (restraining-bolted, standing in rows) opening onto a curved repair bench. Salvaged-shell fencing.
- Jobs: Droid Repair Jobs (built, [Repo] src/RimUtinni/DroidRepairJobs), monster-droid cobbling, bolt-fitting; the droid pen is also the "stock to sell".

### 5. The Furnace Nook (unholy corner)  see section 3
- Source: Legends: sandcrawler "energy furnaces"; Canon: "Jawas typically utilized the reactor to melt down scrap metal and droids" (Sandcrawler). Original Corellia Mining crawler was a "mining and smelting facility". [Canon/Legends]
- Shape: small alcove 3x4 apart from the nest, sealed off or hidden; spoken-over before use. Clan taboo (Rekko, [Repo]).
- Jobs: the *last-resort* smelter; heavier mood/ritual cost.

### 6. The Annual Meet Market (temporary open nest)
- Source: all clans gather in the Dune Sea basin before storm season for the annual swap meet: exchange salvage, compare navigational data, arrange marriages ("marriage merchandise"). [Legends, Jawa/Legends]; "one of the most important days... the annual meeting of all sandcrawlers" [Legends, Sandcrawler/Legends].
- Shape: loose circle of tarp stalls around a central bargaining spot; no walls.
- Jobs: trade, haggle (Bazaar window, [Repo]), cross-clan appraisal.

## 2. Salvage process, tools, droids, appraisal

**Collect**
- Jawas comb deserts for droids or scrap to sell and trade to locals [Canon, Jawa]; stripped, not destroyed ("Stripped. Not destroyed. The Jawas steal. They don't destroy." Kuiil, Mandalorian) [Canon].
- First on the scene of crashed starships and podracer wrecks, hauling "smoking debris" [Canon, Jawa]. Sandcrawler magnet crane + extendable repulsorlift/magnetic suction tube pull droids and scrap into holds [Canon, Sandcrawler].
- Whole salvage expeditions off-world (Endor, Raxus Prime, Skip 5 repairs) [Legends].

**Capture and control droids**
- Ion blasters stun droids; restraining bolts control them [Canon, Jawa]. Ion blaster: handcrafted from salvage; stripped blaster power pack + accu-accelerator from a starship ion engine + a **restraining bolt** in the firing mechanism; 12 m accurate range; safety button above trigger; stuns living creatures [Canon, Ion blaster]. Jawas fire in volleys (stunned Din Djarin) [Canon].
- Restraining bolt: cylindrical; restricts movement and forces response to a hand-held "caller"; commands Come / Halt / Orders; droids cannot remove their own [Canon].

**Repair / refurbish / sell**
- "Instinctive feel for machinery"; knows how to get equipment working "just well enough to sell" [Legends]. Reputation for swindling, hastily refurbished gear and faulty droids; farmers still buy, no better selection [Canon].
- Hydrospanner is a ship-repair tool, appears in Jawa-adjacent repair (Anakin on the *Twilight*; Han/Chewie) [Canon, Hydrospanner]; usable as the nest's bench tool, not a Jawa-specific item.
- **Monster / junk droids**: custom droids recombined from spare parts to a customer's specification [Canon, Monster droid].
- Bargaining: a Mandalorian parts trade at a mudhorn egg; Arvala-7 Jawas prized mudhorn eggs "a large pile of parts for a single egg" [Canon, Jawa].

**Appraisal**
- No canon appraisal procedure exists. Closest: "imagine someone else who might find a use for it" [Legends] and "Mob un loo?" (How much?) [Canon, Jawaese]. Repo hooks: Antiquities examine job + Bazaar `RM_PriceAlmanac` [Repo, pitch 1b].

**Sandcrawler interior**
- ~20 m tall tracked box, triangular front with cockpit; reactor; "cargo holds, scrap-processing facilities, quarters" for a whole clan [Canon]; 1,500-droid hold [Canon]. Legends: "magnetic cranes, energy furnaces, workshops" [Legends]. Shaman stays in the ground fortress, not on the crawler [Legends].

**The "unholy smelting" angle**
- **Canon does not say smelting is unholy.** It says the opposite: Jawas "typically utilized the reactor to melt down scrap metal and droids" [Canon, Sandcrawler]; crawlers were built as smelting facilities.
- So "unholy (literally)" is **[Repo] / owner ruling**: `design/Jawa/wrecked_machines_resurrection.md` ("repair existing broken machinery... about all the Jawa can do"; sacred scrap as clan policy) and Rekko of the Second Hand in `design/Jawa/divine_satiation_engine.md` (TABOOS: S "smelting/scrapping above half condition", M "destroying a repairable machine", L mass destruction; DEEDS +: repairing, restoring, "careful parts-deconstruction where repair is truly impossible (mourned)"). Rite: `RUT_Rites_ScrapShrine`. A usable bridge to canon: Jawas melt only what cannot be mended, and the crawler furnace is the clan's "dirty" machine kept apart.

## 3. Society, roles, trade (canon/legends)
- Each sandcrawler led by a male Clan-Chief; clan overseen by a female Shaman (foretelling, hexes, blessings) who lives in the fortress [Legends].
- Adults work the crawlers; children, eggs and stored wares stay in the fortress [Legends].
- Clans trade sons/daughters as "marriage merchandise" [Legends]. Annual meet before storm season [Legends].
- Robes hemmed to armpit, hem lowered with age; adults 5-6 hems [Canon, "Stories in the Sand"]: a growth-marker unit usable for apprentice ranks ("hems").
- Scent is language: identity, health, clan, mood [Legends, Canon says scent in Jawaese]; faces hidden, glowing eyes; orange gemstones in hood fabric [Legends].
- Tusken relations: tentative peace, avoid them; Tuskens sold some crawlers to Jawas [Legends]; Jawas fear krayt dragons and sandstorms [Canon].
- Diet: hubba gourd [Legends]; squills as delicacy [Legends].

## 4. Terms usable as names
| Term | Meaning | Source |
|---|---|---|
| Utinni | "Come on / Let's go!" (also 'Untinni') | [Canon, Jawaese; Jawa Trade Talk] |
| Mob un loo | "How much does it cost?" (appraisal/haggle) | [Canon] |
| Mombay m'bwa | "It's mine" (claim stamp on salvage) | [Canon] |
| Tandi kwa | "Give it back!" | [Canon] |
| Togo Togu | "Hands off!" (don't-touch tag) | [Canon] |
| Taa baa | "Thank you" | [Canon] |
| Ibana / Nyeta | Yes / No | [Canon] |
| Monasuka | egg (nest, nursery) | [Canon] |
| M'um m'aloo | Hello | [Canon] |
| Omu'sata | Shut up | [Canon] |
| digger crawler | the sandcrawler's original name | [Canon] |
| marriage merchandise | trade in kin | [Legends] |
| monster droid / junk droid | recombined droid | [Canon] |
| hems | robe-hem count = age/rank | [Canon] |
Note: "27 words for junk" is canon but the words themselves are unrecorded; coin them (invented, RM_ tier OK per owner Q11a).

## 5. Repo lore pointers
- `design/RimMandrake/jawa_scavenge_system_pitch_2026-10-03.md`: options A-F; sorting bench = the Scrap Shrine; no appraisal/identify mechanic exists yet.
- `design/Jawa/reconciled_lore/05_the_clan.md` Cold Nursery; `06_the_ship.md` crawlers stolen from collapsed silicax oxalate mines, ship stolen from a Hutt yard.
- `design/Jawa/divine_satiation_engine.md` Rekko of the Second Hand; `design/Jawa/wrecked_machines_resurrection.md`.
- `src/RimUtinni/Rites/Defs/RUT_Rites_Research.xml` scrap shrine (line 34).
- grep for "nest" in design/ found only vermin/creature nests, no workshop concept exists; the scrap shrine is the only named workshop-ish place.

## 6. Caveat
Legends facts are not campaign canon; the fortress-of-wreck-walls and shaman-at-fortress are Legends only. Image reference not fetched.
