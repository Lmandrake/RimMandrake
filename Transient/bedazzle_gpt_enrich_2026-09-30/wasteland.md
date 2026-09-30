# GPT enrichment consult: The Wasteland

Asked 2026-09-30 via codex exec (gpt-5.6-sol, xhigh). Advice only: nothing here is ruled.

The weakest marks are the relationship to the gods, discoverable technology, gravship integration, and soundscape. These recommendations address those first, then deepen existing strengths.

### 1. The Unburied Ledger — The gods may forgive, but this ground remembers

- **Experience:** Storms expose name-tags, confession cylinders, grave markers, and sealed evidence. Colonists can perform a “Bearing Witness” ritual: identify the dead, reseal the crime, or sell the evidence. Each choice produces Ideology-dependent thoughts and faction consequences.
- **Marks:** Relationship to the gods; unique mechanic.
- **Build:** PreceptDefs, RitualPatternDef, ThoughtDefs and exhumed relic ThingDefs; small C# ritual outcome worker. Deities remain interpretive—nothing supernatural is confirmed.
- **Why here:** Preservation, buried crimes, and “no outlet” make the Wasteland the one place where sins literally cannot disappear.

### 2. Waste Stratigraphy — Learn the biome by reading successive layers of poison

- **Experience:** Players recover three classes of field knowledge: war dosimeters, Junker sorting ledgers, and brine-voltage records. Studying examples unlocks survey stakes, safer cache excavation, and finally sealed plant-vault extraction.
- **Marks:** Discoverable technology; unique mechanic.
- **Build:** XML research projects and analyzable salvage; small C# `CompAnalyze`, study job and knowledge tracker. Hide each research node until its first associated object is examined.
- **Why here:** Conventional research cannot substitute for learning which particular century of waste lies beneath a particular crust.

### 3. The Sealed Cask Bay — Make the gravship carry a piece of the dump

- **Experience:** A ship-bound bay accepts dangerous casks and clearly displays seal integrity, internal heat, stored dose and launch safety. Powered seals contain pollution; processor animals can convert selected cargo into bricks or bezoars, while compound damage risks a visible leak.
- **Marks:** Gravship touch; unique mechanic; resources.
- **Build:** XML building and cask defs plus a medium C# comp tracking containment. Connect to gravship membership and launch validation; use Harmony only if the normal launch checks offer no extension point. Add real Mod Settings for capacity, leak severity and processing rate.
- **Why here:** Only this biome treats waste simultaneously as cargo, livestock feed, income and an environmental verdict.

### 4. The Glass Choir — Let the empty land sound crowded with buried things

- **Experience:** Salt plates tick as temperatures move; vitrified crust rings under footsteps; half-buried hulls boom in gusts; distant gas pockets groan near the Stenchlands. Geiger-like clicks occur only while a carried or installed instrument is active, intensifying directionally near dose.
- **Marks:** Interesting soundscape.
- **Build:** Mostly SoundDefs and terrain footstep tags; small C# map audio component for dose-aware sustainers and rare one-shots. Expose volume and click-frequency settings.
- **Why here:** The Wasteland’s “population” is preserved wreckage, stressed glass and trapped gas—not insects, rain or howling predators.

### 5. Deadlight Halo and Cinderwire Storm — Give the two unnamed storms unmistakable identities

- **Experience:** A **Deadlight Halo** arrives quietly: shadows double, instrument clicks accelerate and sickly light rims every pawn. A terminator-only **Cinderwire Storm** begins with crawling static, levitating scraps and a deep electrical whine before EMP, plasma and burial effects begin.
- **Marks:** Interesting weather; soundscape.
- **Build:** Extend the already-ruled WeatherDefs with sky colors, overlays, motes and SoundDefs; small C# phase controller supplies readable warnings and hands resolution to the existing storm mechanics.
- **Why here:** These are different expressions of trapped contamination, not generic toxic fallout or another biome’s supernatural storm.

### 6. Rootglass Vaults — The cleanest-looking ground conceals the dirtiest ore

- **Experience:** Mature sequestration growth occasionally leaves a faintly raised, glass-veined crust. Extracting the buried rootglass yields dense reactor material but immediately repollutes nearby cells, kills the protective growth and releases a dose pulse.
- **Marks:** Unique resources; discoverable technology; unique mechanic.
- **Build:** XML mineable and item defs; small C# plant/vault comp recording accumulated sequestration and revealing a node when surveyed or disturbed. Rootglass can fuel dirty equipment and improve cask-bay shielding.
- **Why here:** It embodies the ruled healing inversion: flora cleans the surface by making something worse underneath.

### 7. Crime Strata — Make every exhumation a tiny preserved story

- **Experience:** Storm finds are authored tableaux rather than loose loot: a survey team facing home, a payroll cask chained to a corpse, a sealed ambulance full of stolen medicine, or a failed warcasket extraction. Inscriptions and item ownership explain what happened.
- **Marks:** Unique mechanic; resources; relationship to the gods.
- **Build:** XML encounter templates and ThingSetMakers atop MovingDunes exhumation; medium C# placement and history stamping. Anything buried receives a visible ash-swelling marker and inspect text—never unexplained disappearance.
- **Why here:** Nowhere else preserves both the evidence and the people who tried to hide it.

### 8. The Middenshell Procession — Turn the giant into a landscape-scale visit

- **Experience:** Hours before arrival, crust trembles and loose metal points toward one map edge. The Middenshell crosses on a slow readable route, grinding buildings and leaving hot footprints, shell flakes and minor bezoars. Waste stockpiles can divert it. If it exits, its trail and edge-scar remain.
- **Marks:** Giant beast; surprising creatures; soundscape; unique mechanic.
- **Build:** Large C# extension to the TitanicCreatures route and destruction-wake system, with XML incident, sounds and footprint filth/terrain. Preserve the owner-ruled twenty-cell width or report an engine ceiling.
- **Why here:** It is the Wasteland’s entire ecology enlarged into geography: contamination eaten, concentrated and worn as armor.

### 9. The Rite of Tipping — Get paid to accept tomorrow’s disaster

- **Experience:** A Junker-supervised waste convoy offers silver and access rights if the colony licenses a marked dumping pad. Wildsteam may ask for evidence; Deepwater may finance proper containment. Accepted casks remain physical objects that can leak, feed processors, enter the cask bay or be illegally reburied.
- **Marks:** Unique mechanic; unique resources; gravship touch.
- **Build:** QuestScriptDefs, IncidentDef, cask items and faction rewards; small C# dump-pad comp for contracts, inventory and breaches.
- **Why here:** The biome’s hazard is the only one with a tipping fee and a faction whose survival depends on denying the cost.

### 10. Star Wars layer: Jawa Black-Glass Auctions — Storm salvage becomes clan theatre

- **Experience:** After major exhumations, the Jawa clan can hold a noisy lantern-lit auction around an exposed hull. Lots may contain droid memory cores, ion-burned machinery or disastrously hot “mystery boxes”; radio chirps and excited Jawa calls contrast with the empty wind.
- **Marks:** Discoverable technology; resources; soundscape.
- **Build:** Conditional `SW_` XML defs, ritual/quest integration and loot tables; small C# auction outcome worker. Keep every canon reference confined to this compatibility layer.
- **Why here:** The storms continually replenish perfectly preserved salvage, making scavenging a renewable cultural institution rather than ordinary ruin-looting.

## Top 3

1. **Waste Stratigraphy** — Converts contamination from a passive penalty into an escalating, discoverable knowledge game.
2. **The Unburied Ledger** — Supplies the missing divine relationship without making the Wasteland supernatural.
3. **The Sealed Cask Bay** — Connects animals, resources, pollution and the campaign’s gravship dilemma in one buildable system.
