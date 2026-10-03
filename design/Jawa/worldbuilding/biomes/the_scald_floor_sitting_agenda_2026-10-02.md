# The Scald — floor-pass sitting agenda (draft, 2026-10-02)

Track (b) of `BEDAZZLE_TOP_SHAPE_PROGRAM_1` ("finish the two seas' floor passes"), the Scald's
half. Shape copied from the Grey Sea pass (`GREYSEA_FLOOR_PASS_1`,
`grey_deep_sitting_agenda_2026-09-27.md`). **Draft for a sitting: nothing is filed, no code is
touched.** Read from the bench clone at `e7490dd79`. Rosters were parsed as XML elements (node
name = animal, text = commonality); the cast was judged from descriptions, not defNames. Tile
counts were not consulted.

Sources: the frozen sheet `the_scald.md`; `the_scald_underwater_flora_pass_2026-09-27.md`;
`terminal_seas_cast_proposal_2026-09-25.md` (Scald gap check); items `SCALD_MECHANICS_1`,
`SCALD_WATER_AGITATION_FLECKS_1`, `SEA_FLOOR_AND_CATCH_PASS_1`, `closed/SEABED_PLANET_LAYER_1`;
and the defs under `src/RimMandrake/TerminalBiomes/`, `src/RimMandrake/DivingInteraction/`,
`src/RimUtinni/UtinniPatches/`.

## 1. What is built (measured)

**The cast and the catch are in much better shape than the older items say.** The
`SEA_FLOOR_AND_CATCH_PASS_1` table (2026-09-22: "4 floor animals, zero overlap with the catch")
is stale. The 2026-09-26 pass `SEA_FISHABLES_ALIVE_IN_DEPTHS_1` closed that gap.

### 1.1 The biome def (`RM_TheScald`, `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheScald.xml`)

| field | value | note |
|---|---|---|
| `animalDensity` | 0.15 | non-zero, so the roster can spawn (the Propane Lake trap does not apply) |
| `plantDensity` | 0.30 | the flora pass's proposed number is **already in the def**, though its Q2 is still listed open |
| `wildPlants` | `RM_Crowncarpet` 0.4 | the only plant; none of the flora pass's nine are built |
| `wildAnimals` (inline) | 10 rows | `RM_Eesh` 1.2, `RM_Doss` 1.0, `RM_Shulla` 0.9, `RM_Muddal` 0.7, `RM_Bladderboil` 0.6, `RM_Thuum` 0.5, `RM_Karrash` 0.45, `RM_Noohm` 0.4, `RM_Ekkel` 0.3, `RM_ElderSando` 0.005 |
| `wildAnimals` (campaign patch) | +3 rows | `WildAnimals_TheScald.xml`: `RSW_SandoAquaMonster` 0.03, `RSW_Faa` 0.5, `RSW_Mee` 0.5 (canon Star Wars, Utinni layer) |
| `fishTypes` | 9 + rare table | common: eesh, muddal, doss, thuum, shulla catches; uncommon: karrash, saal, bladderboil, ekkel; rare: `RM_RareScaldCatches` |
| `maxFishPopulation` | 40 | Grey Sea is 120 |
| modExtensions | `RM_SeaShoreExtension`, `RM_SunHeatExtension` (heat kind **ambient**, +15 °C) | no `RM_SeabedAccessExtension` (see 1.4) |

The frozen `RUT_TheScald` twin still carries the old 4-row roster and no plants. Expected: it
holds today's world until the one repaint, and nothing here asks to change it.

### 1.2 The cast, read from descriptions

Every catch has a living floor creature, written from its own catch description:

- **eesh**: finger-long finless mirror-skinned sliver; lives in the boiling column itself; moves as one cloud.
- **doss**: hunch-backed shrimp-thing, pink from birth; works the dung-fall from below.
- **shulla**: hot-white sliver; darts in shoals between vent plumes on the dung-fall.
- **muddal**: hand-long armored grazer of the crowncarpet bands; "the bottom-walkers' small cousin".
- **thuum**: eel living in the hot film *under* the mats; banded in the mats' colours.
- **karrash**: crab that "looks like a piece of the vent walked off"; lives on the chimneys.
- **ekkel**: fist-sized tumbling knot of heat-mirror filaments; travels by letting go down the chimney.
- **bladderboil**: head-sized golden gas-sac that gulps itself taut in the roar and sighs out in quiet pools.
- **noohm**: the bubble-sailor; a translucent bell heeled over on a bubble-line, sail-membrane up. Its catch is named **saal** (`RM_Saal`), different on purpose per `RM_ScaldFloorFauna.xml`'s header.
- **elder sando**: invented leviathan (bs 20), "one per sea, if that". Floor-only, no catch, by the pairing rule.

### 1.3 Mechanics (`SCALD_MECHANICS_1`, kit S1–S6)

- **S1 steam sky**: `RUT_ScaldSteam` weather, forced by `RUT_ScaldSteamLock` with "still day" clear spells via the Forge's weather-pulse class.
- **S2 steam-catch**: `RUT_SteamCatch` condenser on a vent. Its water output item is still unset; no item-water def exists.
- **S3 margin fishing and baths**: **blocked.** Fishing needs shore cells. `RUT_ScaldMargin` (cool ring, burn 0) exists but must be hand-placed as a sealed cove, and never was.
- **S4 geyser fields**: `RUT_ScaldVent`. It is placed by the bridge only, so a generated map has **no vents**.
- **S5 set-pieces**: the sail scatterer (`RUT_ScaldSailScatterer`) is keyed to vents and spawns a **vanilla Penguin placeholder**, not the noohm. The walker surfacing (`RUT_WalkerSurfacing`) is a **message only**: no walker creature exists.
- **S6 wreck salvage**: three wrecks (`RUT_ScaldWreck*`) scattered on the surface biome; shadows fixed (`SCALD_WATER_AGITATION_FLECKS_1`).
- **Water agitation**: `RM_MapComponent_WaterAgitation`. Margin calm, shallow lightly agitated, deep always agitated.
- **Gear and research**: `RM_ScaldWorking` research unlocks the boil-suit (`RM_Apparel_BoilSuit`); also the scald wrap. Scald damage, exposure hediff and a scald armor stat exist.
- **Floor-derived item**: `RM_ScaldWalkerChitin` (curved plate from a bottom-walker). This is a walker part with no walker.

### 1.4 The floor itself: two routes, and the live one is empty

- **The old hatch route** (`RM_SeaDiveGenerator_TheScald`, `DivingInteraction`): a pocket map with biome `RM_TheScald`, 55 °C. The base is a sediment floor with nested hot-spring patches: a boiling shallow core (5%) ringed by cool margin (12%). Gensteps include Animals and Plants, so the full 10-creature roster and the crowncarpet spawn here. 🔴 CLAUDE.md (owner, 2026-10-01): **the hatch is a leftover** (`SEA_DIVE_HATCH_RETIRE_1`); the ship now *flies* to the sea-floor planet layer.
- **The live route** (`RM_SeabedLayer`, `closed/SEABED_PLANET_LAYER_1`): Phase 1 only. Every floor tile is either `RM_SeabedFloor` (one generic placeholder, `animalDensity 0`, `plantDensity 0`, `maxFishPopulation 0`) or `RM_SeabedUnavailable`. **Phase 4, "biomes and content per sea", which replaces the placeholder and gives each sea's surface biome `RM_SeabedAccessExtension`, is unbuilt for every sea.** Phase 3 (plants on the floor; it must first guard a known `FinalizeInit` crash) is also unbuilt.
- ⇒ **Today a ship that flies to the Scald's floor lands on an empty generic floor.** Everything in 1.1–1.3 lives on the retiring hatch map or the surface biome. Whether the Scald's crater tile counts as water-covered for the layer (`SurfaceTile.WaterCovered`) is **UNMEASURED**: a live read is owed, not a guess.

## 2. Gaps against the Grey Sea checklist

The Grey pass made the floor a **place**: getting there; a floor you walk with landmarks; two
flora layers; a cast where every catch swims; danger in layers; the ship touched in the sea's
own voice; an economy. Its sitting settled everything. Against that, plus the nine bedazzle marks:

| Grey checklist row | Grey Sea | The Scald today | gap |
|---|---|---|---|
| Getting there (ship to the floor) | ruled; same layer problem | live layer gives an empty placeholder | **shared**: Phase 4 per-sea seabed biome |
| Floor landmarks / formations | pillars, domes, chimneys, crystals, brine pools, channels (built) | sediment plus two noise patches; **no vents, no rim, no wrecks on the floor** | **big**: no geography to navigate or fight over |
| Flora: monuments + understorey | 7 monuments built + 10 understorey ruled at 0.22 | crowncarpet only; 9 designed (`the_scald_underwater_flora_pass`), none built | ruled roster exists, unbuilt; 4 flora questions still open |
| Cast: every catch swims | yes | **yes, 9 of 9** | none on the pairing |
| Anchor / giant | crusted giant (`RM_Reefback`) + ossuary shrimp | elder sando only; **the bottom-walkers (the sheet's own herds) have no creature def** | **big**: the sheet's signature giant herd is missing |
| Prize catch | rare table + prize items | rare table is just extra karrash/ekkel | small: no prize |
| Danger in layers | pools that crystallise, light economy, the Elders | burn on traversal, scald exposure | **medium**: the floor has no designed danger beyond "it's hot" |
| Ship-touch voice | crystallises hull, salts doors | **unruled**: Q17 deferred it to this pass | **owed this sitting** |
| Economy | 4 salts, crystals, jacket salvage, novelty trade | steam-catch (output item unset), pigment (crowncarpet), walker chitin, boil-suit | medium: steam-catch water item missing |
| Soundscape | — | `RUT_ScaldSteam` weather only, no SoundDef | miss (same as most biomes) |
| Rites | Grey has none listed | **none in the rites register**, though the sheet's two-faith shore and sacred baths are rite-shaped | pitch owed |
| Fishing from the shore | shore question shared | S3 blocked: no margin cove painted on the planet | carried; not this sitting's to solve (map painting is the end pass) |

## 3. Per-species floor + catch table

All `RM_` (invented, franchise-free per Q11a) unless noted. "Floor" = a living creature on the
Scald's `wildAnimals`. "Catch" = an entry in its `fishTypes`.

| species | what it is (from description) | floor def | catch def | status |
|---|---|---|---|---|
| eesh | mirror-skinned sliver in the boiling column; cloud | `RM_Eesh` 1.2 (shoal stand-in) | `RM_EeshCatch` common 1.5 | ✅ pair |
| doss | pink shrimp-thing, under-mat scavenger | `RM_Doss` 1.0 | `RM_DossCatch` common 0.7 | ✅ pair |
| shulla | hot-white plume-darting sliver | `RM_Shulla` 0.9 | `RM_ShullaCatch` common 0.6 | ✅ pair |
| muddal | small armored mat-grazer | `RM_Muddal` 0.7 | `RM_MuddalCatch` common 0.8 | ✅ pair |
| thuum | under-mat banded eel | `RM_Thuum` 0.5 | `RM_ThuumCatch` common 0.5 | ✅ pair |
| karrash | vent-crust crab | `RM_Karrash` 0.45 | `RM_KarrashCatch` uncommon 1.0 + rare | ✅ pair |
| ekkel | tumbling filament knot | `RM_Ekkel` 0.3 | `RM_EkkelCatch` uncommon 0.4 + rare | ✅ pair |
| bladderboil | golden gas-sac | `RM_Bladderboil` 0.6 | `RM_BladderboilCatch` uncommon 0.5 | ✅ pair |
| bubble-sailor | sail-bell riding bubble-lines | `RM_Noohm` 0.4 (bs 0.3) | `RM_Saal` uncommon 0.5 | ⚠️ pair under **two names**. The catch reads as "fist-sized, one stiff vane"; the creature reads as a heeled bell with a membrane. A deliberate choice, but the owner has never seen it side by side (decision 5) |
| elder sando | invented leviathan, one per sea | `RM_ElderSando` 0.005 | — | ✅ floor-only megafauna (pairing rule) |
| **bottom-walker** | the sheet's huge armored herds mowing the mats at −350 m | **none** | — (chitin item exists) | 🔴 **missing**: the sheet's signature giant |
| sando aqua monster | canon apex, campaign layer | `RSW_SandoAquaMonster` 0.03 | — | floor-only megafauna (campaign) |
| mee | canon silver-blue schooling scalefish | `RSW_Mee` 0.5 | `RSW_MeeCatch` exists, **not** in Scald `fishTypes` | ⚠️ campaign half-pair |
| faa | canon gold-olive scalefish | `RSW_Faa` 0.5 | `RSW_FaaCatch` exists, **not** in Scald `fishTypes` | ⚠️ campaign half-pair |

⚠️ **Two cast questions the table raises:**
- The canon mee and faa are Naboo shallows fish. They swim in a boiling sea whose admission test
  is "thrives in heat that kills everything else", and their catch is not wired here. Either wire
  the catch (campaign patch, as the Greentide does) or drop them from the Scald. Dropping is
  scoped to this sea only. Decision 6.
- **Sheet ban 4** ("nothing swims the roiling surface layer but bubbles and sails") versus the
  eesh, which by its own description "lives in the boiling column itself". On a floor map the
  column is not drawn, so it is harmless in play. Flagged for the record, not for a card.

## 4. Five ideas (GPT consult)

Full output: `design/Jawa/worldbuilding/biomes/the_scald_floor_gpt_consult_2026-10-02.md`
(gpt-6.1-sol, high effort). GPT was given the frozen sheet, the flora pass, sections 1–3 above,
the Grey, Twilight and Propane material, the 12 grandfathered biome scorecards and the rites
register. It was asked for five ideas that differ from each other and from every other biome,
each with deep research on other games and mods. Its precedents included Subnautica's sea-treader
dung trails, Below Zero's thermal vents, Barotrauma's sonar, ONI's and Frostpunk's thermal
allocation, Outer Wilds' infrastructure archaeology, VE Fishing riding Odyssey's fishing, SOS2,
DBH, Rimefeller, Alpha Biomes/Animals and Kenshi. It names what it deliberately did not copy.
GPT's costs **exclude** the shared seabed-layer work (1.4).

| # | idea (GPT's name) | in plain words | the verb | nearest existing content, and why different (GPT's check) | cost |
|---|---|---|---|---|---|
| 1 | **The Walking Pasture** | Build the missing bottom-walkers as a real herd. Where they graze, the mat's pigment-rich underside is briefly exposed; your crew works behind the herd, stops when it turns, and backs off when two grazing lanes meet. Too close and you get shoved aside by something that barely notices you. | follow | Pyrelands' herds follow a fire regime; this one opens temporary access to a resource. The sheet already rules the herds and the dung economy; the **moving worksite** is the new part. | L |
| 2 | **The Sail Forecast** | The noohm bubble-sailors shift from one vent branch to another *before* that vent discharges. Players learn to read sail traffic as the warning, then harvest the exposed vent-wall deposits in the safe window. | forecast | The geysers (S4) exist; what is new is wildlife telling you which vent is about to go. Not a map-wide countdown, not the Forge's boiling rain, not a light lure. | M |
| 3 | **The Immersion Berth** | **The Scald's ship-touch voice.** A parked hull slowly heats up: a small, tight ship is easy to keep cool, a sprawling one is not. Fit coolers and choose which rooms get power. The sea never seals doors or blocks launch; it makes the ship worse as a bedroom, hospital and workshop. | refrigerate | Grey grows matter on the hull and demands chipping before launch. This adds nothing to the hull and has no launch gate. Vanilla room temperature and coolers throughout. | M–L |
| 4 | **The Return Gallery** | A half-buried, broken coolant manifold from the Rust Cathedral's circuit lies on the crater floor. Hook a pump to its ports and read the gauges to trace which branches are dead and which still return. Solving it opens a locker with an engineering schematic and a record of where the Cathedral dumps its heat. | trace | The coolant circuit is canon already; diagnosing its abandoned branches is new. It rewards understanding, where wreck salvage rewards extraction. It cannot touch the live trunk or stop the boil. | M |
| 5 | **The Unanswered Wound** | A found rite for **Sh'kaar** (the forge god). After a native creature genuinely injures a colonist, the group tends the wounded and walks them back to shelter **without striking any resident**. The injury becomes a reason to protect, not to retaliate. A shared memory; no heat immunity. | refuse retaliation | Not the Snuffing (light), not the Anvil Gift (destroys a weapon: here weapons stay intact), not the Shade Tithe or Felled Noon. GPT says it uses Sh'kaar's last open found-rite slot. Guarded against injury-farming. | M |

**GPT's ranking:** Walking Pasture, then Return Gallery, then Unanswered Wound, Sail Forecast,
Immersion Berth. **BENCH's read:** the Pasture fills the sheet's biggest hole (the giant herd has
no creature), so it ranks first. The Berth is the only candidate for the ship-touch voice the
Grey sitting deferred here, so it is owed a card whatever its rank. The Forecast needs vents to
exist on the floor map, which they don't today (1.3, S4).

⚠️ **Consult hygiene finding.** A run made at the same moment as the Chill/Propane consult returned
a complete answer **about the Chill**, built on this consult's attached files. Two
`gpt_consult.py` jobs running at once can cross answers, though each has its own job directory.
That answer was discarded, and the run above was repeated with a "Scald only" guard. Whoever
reviews the Chill consult should check that its answer is about the Chill.

## 5. Decisions for the owner

Ranked by how much each one changes what a player meets. The first three matter most.

1. **The bottom-walkers: what are they in play?** The sheet calls them the Scald's signature: huge
   armored herds mowing the rainbow mats on the floor. Today they exist only as a chitin plate you
   can trade and a "walker sighted" message. There is no creature.
   - (a) **A plain grazing herd.** Big, slow, harmless, part of the scenery. *For:* cheapest; fills the hole. *Against:* the giant just stands there; nothing to do with it.
   - (b) **The Walking Pasture** (GPT idea 1). Your crew follows the herd to harvest what its grazing exposes. *For:* the giant becomes the floor's main activity, and no other biome has a moving worksite. *Against:* the largest build here (herd behaviour plus a following job), and herd AI could annoy if tuned badly.
   - (c) **Rare surfacing only.** Keep them as an event, never on the floor. *For:* keeps their mystery. *Against:* the sheet says the floor *has herds*; a diver would never meet one.
   - BENCH leans **(b)**, built as (a) first so the creature exists even if the following job slips.

2. **How does the Scald touch a parked ship?** This was deferred from the Grey sitting (its Q17)
   to this one. The Grey crystallises the hull and salts doors shut; the Twilight drops panes.
   - (a) **The Immersion Berth** (GPT idea 3). The hull's rooms heat up; a compact ship stays cool and a sprawling one costs power to keep livable. Doors never seal and launch is never blocked. *For:* uses the game's own temperature and coolers; a real ship-design choice. *Against:* if tuned too hard, every Scald ship ends up the same shape.
   - (b) **Kettle scale.** Mineral fur on the hull you scrape off. *For:* the obvious picture. *Against:* too close to the Grey's crust-and-chip.
   - (c) **Steam and sound only.** Cosmetic, no mechanic. *For:* free. *Against:* the only sea with no ship voice.
   - BENCH leans **(a)**.

3. **What stands on the floor to give it geography?** Today the floor is plain sediment with a few
   hot-spring patches. Vents are placed by hand on the surface map only, so the floor has none,
   and the bubble-sailor scatterer finds nothing to anchor to (it still spawns a placeholder penguin).
   - (a) **Generate vent fields on the floor map.** This unlocks the sailors, the vent flora (glasskelle, pulsebead) and the Sail Forecast (GPT idea 2). *For:* one change switches on four built or designed things. *Against:* vent geysers then go off near a parked ship.
   - (b) **Add the Return Gallery** (GPT idea 4): a half-buried Cathedral coolant ruin to trace. *For:* a landmark plus discoverable technology plus campaign history. *Against:* a puzzle that needs care to avoid arbitrary switch-matching.
   - (c) **Both.**
   - BENCH leans **(a) now, (b) as a second wave.**

4. **A rite for the Scald?** The rites register has nothing for the Scald, though its two-faith
   shore and sacred baths are rite-shaped by the sheet's own words.
   - (a) **The Unanswered Wound** (GPT idea 5): a Sh'kaar rite of carrying a hurt colonist home without striking back. *For:* a genuinely new act in the register. *Against:* it sits on the floor, away from the sheet's shore faiths.
   - (b) **A bathing rite for the water pilgrims** at the cool margins. *For:* the sheet's own image. *Against:* needs the margin cove, which waits for the end-of-project map painting.
   - (c) **None for now**, recorded as "none". *For:* the program allows it. *Against:* leaves a mark empty.

5. **Bubble-sailor: one creature with two names?** The living sailor is the *noohm*, a heeled
   bell with a membrane. The fish you net is the *saal*, fist-sized with one stiff vane. They were
   paired on purpose, but you have not seen them side by side. Keep the two names (fishermen and
   divers call it different things), or rename one so the creature and its catch match.

6. **The two Naboo fish in a boiling sea.** The campaign layer adds the canon mee and faa (shallows
   scalefish) to the Scald's floor, but their catch items are not wired here. Either wire the catch
   in, or drop them from the Scald only. Dropping matches the sheet's admission test ("thrives in
   heat that kills everything else") and, by the standing ruling, affects no other biome.

7. **Flora leftovers.** The flora pass's density of **0.30 is already in the def**; ratify or
   change it. Its three other open questions (what the kettlewick collar and the seepcandle wax
   yield, and whether simmerlace knots become ekkel as fishermen's lore) still stand. None of the
   nine plants is built yet.

**Housekeeping, not a card:** nothing on this agenda reaches a player until the sea-floor planet
layer gets real per-sea floors (its Phase 4; Phase 3 adds plants and must guard a known crash
first). Today a ship landing under the Scald finds an empty generic floor. Whether that work
starts with the Scald or the Grey is a scheduling call for FOUNDRY's queue, not a design question.
