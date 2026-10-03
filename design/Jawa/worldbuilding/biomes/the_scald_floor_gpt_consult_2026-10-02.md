# The Scald floor: GPT consult, five ideas (2026-10-02)

Raw output of the required bedazzle consult (`BEDAZZLE_TOP_SHAPE_PROGRAM_1` ruling 2026-10-01). Ran via `src/RimMandrake/Utils/gpt_consult.py`, model `gpt-6.1-sol`, effort high, job `consult-20261002-192918-3177139`, 533 s. Inlined: `the_scald.md`, `the_scald_underwater_flora_pass_2026-09-27.md`, the agenda draft (sections 1 to 3), the Grey Sea place summary, the Twilight danger-pass header, `the_propane_lakes.md`, `grandfathered_bedazzle_scores_2026-10-01.md`, and `design/Jawa/salvation_rites_2026-10-01.md`. The first run hit the 10-minute limit after 31 web searches, and its notes were passed to this run. A second run, made at the same moment as the Chill consult, returned an answer about **the Chill** and was discarded (see the agenda, section 4). Agenda: `the_scald_floor_sitting_agenda_2026-10-02.md`.

---

# The Scald: design basis

**This consult is for the Scald only.** I apply its hot, mineral-fouled water, submerged pastures, volcanic vents and hidden coolant works; the copied propane, cryogenic and aurora requirements belong to the exclusion reference.

At −350 m, pressure suppresses boiling: the floor can be merely hot while vent fluids rise toward the roiling surface. That gives the floor a stronger identity than another exposure countdown: **a submerged pastoral landscape beneath the planet’s distillery**.

The agenda also changes the implementation baseline: the live seabed layer is empty. Costs below **exclude the shared Phase 3/4 seabed work**, and distinguish proposed gameplay from already ruled ecology.

# Research: what to borrow and avoid

Six searches, followed by direct source checks. These are design precedents, not claims of current mod compatibility.

- **RimWorld, Odyssey and VE Fishing:** Odyssey supplies the travelling colony and hostile destination maps; its orbital platforms and asteroid expeditions establish the “bring your home, work outside, return aboard” loop. VE Fishing explicitly uses Odyssey’s fishing system when installed. Keep that framework and the existing living-creature/catch pairs. [Odyssey announcement](https://ludeon.com/blog/2025/06/announcing-odyssey-and-update-1-6/), [VE Fishing](https://steamcommunity.com/sharedfiles/filedetails/?id=1914064942)

- **Vanilla Expanded / Outposts:** Outposts turn assigned pawns and skills into remote production. That is precisely the abstraction to avoid here: the Scald should require an expedition’s physical presence. For gravship-era additions, use Odyssey’s ship and outfit it through ordinary buildings/comps; I did not verify a separate VE seabed or pressure framework. [VE Outposts](https://steamcommunity.com/sharedfiles/filedetails/?id=2688941031)

- **Alpha Biomes / Alpha Animals / Biomes! Caverns and Islands:** Alpha Biomes’ Propane Lakes are the literal hydrocarbon precedent, while its resource omissions make unfamiliar ecology affect survival. Alpha Animals supplies the encounter-sized, unusual-creature approach; Caverns and Islands supply bespoke environmental assemblages. Borrow ecological specificity, not cold reskins, generic darkness or another animal roster. [Alpha Biomes](https://steamcommunity.com/sharedfiles/filedetails/?id=1841354677), [Alpha Animals source](https://github.com/juanosarg/AlphaAnimals), [Caverns](https://github.com/biomes-team/BiomesCaverns), [Islands](https://github.com/biomes-team/BiomesIslands)

- **Rimefeller / Dubs Bad Hygiene / SOS2:** Rimefeller’s oil-processing chain is an extraction precedent, but fuel logistics would duplicate the Chill. DBH’s tanks, boilers and hot baths already overlap the Scald’s steam-catch and sacred spa. SOS2’s ship heat management is useful structurally; its separate ship-heat machinery should not become a second planetary temperature system. [Rimefeller](https://github.com/Dubwise56/Rimefeller), [DBH hot water](https://github.com/Dubwise56/Dubs-Bad-Hygiene/wiki/Hot-Water), [SOS2 historical source](https://github.com/SonicTHI/SaveOurShip2Experimental)

- **Oxygen Not Included / Factorio Aquilo:** ONI makes thermoregulation and vehicle-supported expeditions central. Aquilo makes heat distribution a construction problem; importantly, its developers removed actual platform melting because it became frustrating. Borrow readable thermal infrastructure, avoid another survival meter or irreversible floor erosion. Aquilo is an **ammonia ocean**, not a methane/propane simulation. [Klei](https://www.klei.com/games/oxygen-not-included), [Aquilo design account](https://updater.factorio.com/blog/post/fff-432)

- **Subnautica / Below Zero / Barotrauma:** Sea Treaders’ dung trails connect megafauna to an economy; Cyclops silent running connects vessel operation to creature responses. Below Zero’s erupting Thermal Vents and modular Seatruck are close expedition precedents. Barotrauma’s passive/active sonar makes information an operational choice. Borrow ecological tells and the mobile refuge; avoid individual diving, light attraction and submarine flooding simulation. [Sea Treaders](https://unknownworlds.com/en/news/ghost-update-released-steam), [Cyclops](https://unknownworlds.com/en/news/silent-running-update-released), [Below Zero](https://store.steampowered.com/app/848450/Subnautica_Below_Zero/), [Barotrauma sonar](https://barotraumagame.com/wiki/Sonar)

- **Dwarf Fortress / Frostpunk 1&2:** DF’s aquifers reward engineering against a legible environmental process; Frostpunk makes thermal allocation a social choice. Borrow opportunities to plan and prioritize, not full fluid simulation or a duplicate generator economy. [Aquifer development notes](https://www.bay12games.com/dwarves/dev_2019.html), [Frostpunk 2 heat management](https://store.steampowered.com/app/1601580/Frostpunk_2/)

- **Anomaly / Stellaris / Surviving Mars / Outer Wilds:** The useful pattern is studying an unfamiliar process before deciding how to interact. Anomaly’s entity study and rituals are implementation precedents; Stellaris anomaly investigations and Surviving Mars mysteries are narrative comparisons. Outer Wilds provides the stronger spatial model: knowledge reveals opportunities in changing environments. Avoid a random anomaly reward button or another campaign-changing dungeon. [Outer Wilds](https://store.steampowered.com/app/753640/Outer_Wilds/)

- **Dredge / Kenshi / Valheim:** Dredge ties expedition equipment to access, but its fog/night pressure would overlap other seas. Kenshi’s wounded-party extraction is useful for the rite below. Valheim makes journeys meaningful through biome-specific resources and preparation; avoid adding another boss gate. [Dredge](https://store.steampowered.com/app/1562430/DREDGE/), [Kenshi](https://store.steampowered.com/app/233860/Kenshi/), [Valheim](https://store.steampowered.com/app/892970/Valheim/)

None of these needs to supply the Scald’s physics wholesale. Its strongest precedents concern **ecological work, environmental information and the ship as an expedition base**.

# Five ideas

## 1. The Walking Pasture — follow

**Experience.** Three enormous bottom-walkers advance across a rainbow pasture, with silver scavengers working behind them. Their grazing briefly exposes the mat’s normally inaccessible underside: crews follow to collect pigment-rich basal material before the carpet closes again. Mark one herd as your expedition’s worksite; gatherers keep behind it, stop when it turns, and retreat when two grazing lanes converge. Getting closer improves access but risks being swept aside by an animal that scarcely notices people.

**System.** A real walker `PawnKindDef`; `MapComponent` coordinates shared grazing destinations. A `ThingComp` records recently grazed cells; `WorkGiver`/`JobDriver` supplies the following harvest job. Ordinary plants, growth and pigment items remain the economy. Represent bodily danger with a small, telegraphed proximity footprint—not multi-cell pawn pathfinding.

**Nearest neighbours checked.** The Scald already rules herds and dung feeding: the **addition is the moving worksite**, not that ecology. Pyrelands’ herd follows a thermal/fire regime; this one creates temporary access to a substrate. Sump trails indicate thin tar; these routes move with living actors and require coordinating workers.

**Precedents.** Sea Treaders’ ecological trails; expedition preparation from Valheim.

**Cost: L. Risk:** herd AI and automatic workers could become irritating. Start with one slow herd, generous turning tells and explicit disengagement.

## 2. The Sail Forecast — forecast

**Experience.** A vent avenue forks around a basalt saddle. Saal traffic shifts first: bells abandon one branch and gather over another as the feeding flow changes. Players learn to read that movement before approaching exposed vent-wall deposits. A dangerous discharge is localized, pushes loose objects and interrupts work; watching the sails earns a useful warning without a universal countdown. The creatures remain ordinary living residents, including the existing saal catch pairing.

**System.** A vent-network `MapComponent` schedules local discharge states; saal `ThingComp`/jobs visibly respond during a warning phase. Vent comps handle localized damage and bounded displacement. `FleckDef`, `SoundDef` and an inspect description reinforce the same tell. No computational fluid dynamics.

**Nearest neighbours checked.** S4 already supplies geysers; the new system supplies **forecastable relationships between wildlife and individual vents**. Twilight’s current is environmental movement; this is information acquired from animal traffic. It adds no vertical travel, vent-powered lift, map-wide boil-rain or light lure.

**Precedents.** Below Zero’s Thermal Vents; Barotrauma’s environmental information; Outer Wilds’ learned timing.

**Cost: M. Risk:** players may mistake decorative traffic for unreliable signalling. Every dangerous discharge must have the same unmistakable preceding behaviour.

## 3. The Immersion Berth — refrigerate

**Experience.** The gravship arrives comfortable, then the sea starts warming its occupied rooms. A compact hull is easier to refrigerate than a sprawling workshop deck. Fit immersion refrigeration, choose which compartments deserve power, and suspend fabrication while the field crew works. The sea never seals the doors or prevents departure: its pressure is on the ship’s usefulness as a hospital, bedroom and working base.

**System.** Use vanilla `Room` temperature, `CompCooler`/`CompTempControl`, `CompPowerTrader` and `GenTemperature.PushHeat`. A `MapComponent` applies a calibrated additional heat-transfer load to exposed ship compartments. New exchanger defs provide a floor-compatible refrigeration arrangement; all displayed temperatures and pawn effects remain vanilla.

**Nearest neighbours checked.** Grey accretes matter and demands chipping before launch; this accretes nothing and has no launch-work gate. Nightside Ice detects emitted heat; this attracts no creature. The existing Scald exposure system concerns workers outside; this creates a room-layout and electricity decision aboard.

**Precedents.** ONI thermoregulation, SOS2 vessel management, Frostpunk’s allocation choices.

**Cost: M–L. Risk:** excessive heat transfer could force identical ship designs. Tune for a meaningful power burden, not mandatory reconstruction or constant medical emergencies.

## 4. The Return Gallery — trace

**Experience.** A vast broken coolant manifold lies half-buried in the crater floor: an annular gallery with pipes disappearing into sediment. Connect a portable diagnostic pump to its maintenance ports and follow the response through gauges and branch outlets. Dead ends answer differently from intact branches. Correctly tracing the return identifies a service locker containing an immersion-engineering schematic and a record of where the Cathedral has been dumping its heat. You investigate the machine’s plumbing while its history becomes geography.

**System.** `GenStep` builds the gallery and a small, predetermined circuit graph. `ThingComp` ports, `WorkGiver` connection jobs and a `MapComponent` propagate diagnostic signals through that graph. `CompStudiable`, techprints and `ResearchProjectDef` deliver the retained discovery. Actual fluid simulation is unnecessary.

**Nearest neighbours checked.** The hidden Cathedral coolant circuit is already canon; **diagnosing its abandoned maintenance branches** is new gameplay. Cathedral mechanics judge conduct and drilling; this is a spatial inference puzzle. Scald wreck salvage rewards extraction; this rewards understanding. It supplies neither tower command codes nor a third war-lab key, and cannot alter the live cooling trunk or stop the boil.

**Precedents.** Outer Wilds’ infrastructure archaeology; anomaly investigations; Rimefeller’s readable pipe connectivity.

**Cost: M. Risk:** it could become arbitrary switch matching. Every branch needs observable evidence, and a wrong connection should waste work rather than secretly cause catastrophe.

## 5. The Unanswered Wound — refuse retaliation

**Experience.** An old pilgrim relief shows people carrying a wounded companion beneath a walker, their weapons still sheathed. Studying it reveals a Salvation rite for **Sh’kaar: starving escalation**. After a native genuinely injures a colonist, the congregation tends the victim and completes a short procession back to shelter without striking any resident. The injury becomes a reason to protect someone instead of making an enemy. Success gives a shared memory and pre-moves Sh’kaar downward; it grants no heat immunity.

**System.** The supplied found-rite route: `CompStudiable` → rubbing/techprint → `ResearchMod` granting the ritual precept. `RitualObligationTargetFilter`, `LordJob_Ritual` and an outcome worker handle eligibility and completion; a small `MapComponent` records injury provenance and colony retaliation. Call Ninefold’s existing `ApplyDelta`. Content belongs in `mandrake.rut.rites`.

**Nearest neighbours checked.** Snuffing extinguishes light; this remains openly lit. Anvil Gift destroys a weapon; weapons here remain intact. Shade Tithe concerns roofs; Felled Noon concerns felling and exposure. Stranger’s Overhaul repairs an outsider; this ministers to a companion while withholding revenge. It uses Sh’kaar’s fifth found-rite slot, without importing another faith’s bathing rite.

**Precedents.** Kenshi’s extraction of wounded companions; RimWorld’s ritual obligations and Anomaly’s situated ritual framing.

**Cost: M. Risk:** deliberately farming injuries. Require native provenance, reject colony-provoked encounters, and limit credit to once per expedition.

# Ranking for this floor

1. **Walking Pasture:** strongest expression of the Scald’s missing signature giant and pastoral ecology.
2. **Return Gallery:** strongest fixed landmark, discoverable technology and campaign-history connection.
3. **Unanswered Wound:** gives the expedition a belief-practice with a distinct action.
4. **Sail Forecast:** makes the signature silhouette teach useful environmental knowledge.
5. **Immersion Berth:** worthwhile ship interaction, but less distinctive than the ecology and archaeology.

**The Walking Pasture would most make the Scald memorable as a place: a rainbow seabed crossed by enormous, indifferent herds, with your small expedition working in their wake.**