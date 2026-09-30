# CAULDRON_GPT_ENRICHMENT_1 — five GPT-suggested enrichments the owner picked

Source: a GPT enrichment consult (codex exec, gpt-5.6-sol xhigh, 2026-09-30) on the Cauldron. The owner
picked these five by question card.

Out: he declined the whole ship/vents/tech group (*"None of these thanks"*: Scabweight, Pressure
Lattice, ruin-learned filtercraft, Oomo's courtesy), and The Engine Below was not picked. The ruled
versions of those features still stand in `CAULDRON_MECHANICS_BUILD_1`; only GPT's extensions are out.

Every item here deepens something already ruled, so build it as an extension of
`CAULDRON_RULED_CONTENT_1` / `CAULDRON_MECHANICS_BUILD_1`, never as a parallel system. If
`CAULDRON_FULL_RENAME_1` lands first, use its names.

## spec

1. **Four-stroke weather cycle.** The four ratified weathers become recognizable phases of one engine:
   - scatter-dusk: the restless baseline;
   - vapour banks: shorter sightlines, and nearby hisses become directional;
   - dewfall: surfaces bead in brilliant chemical colour;
   - vent bloom: raises local vent output after a conspicuous pre-bloom falter.

   Exposure is strongest near vents, not a whole-map toxin tax. Build: the four WeatherDefs, sky and
   mote workers, weather-linked vent multipliers, chemical-dew filth or overlays, and local exposure.
   Small C# plus XML. **Model: sonnet.**
2. **Vexxiss, warden of the breath.** This deepens the ruled vexxiss behaviour (it inhales a vent to
   pause it, attacks those who ignite fires, puts fires out, and transforms the water it touches). It
   follows high-pressure groans, braces over a vent and inhales until the vent falls silent for several
   days. It leaves wet, mineral-ringed footprints and visibly poisons the water it crosses, with a
   warning letter. When fire starts nearby, it bellows, attacks the recorded igniter, and smothers flames
   under its plates. Build: vent-drinking and fire-response job givers, a vent-suppression state,
   ignition-instigator tracking, extinguish jobs, and toxic-water terrain conversion. Large C#.
   **Model: opus.**
3. **Vexxith closed loop.** The ruled rare shear material (acid- and temperature-immune) makes durable
   filter vessels, vent-cap liners, fireproof doors and gravship scab-scrapers. It makes poor weapons and
   ordinary structural walls, which keeps the living vexxiss worth more than a dead one. Build: a
   StuffDef with zero flammability and focused durability, an extension that acid/corrosion damage
   recognizes, and specialized recipes that require plates. Small C# plus XML. **Model: sonnet.**
   `DESIGN_MATERIALS_REVIEW_1` will later normalize its numbers.
4. **Assay forestry.** This deepens the ruled "metal-infused trees are slow to harvest". Mature
   thornwood and martyr trees grow brighter metallic flecks and show an assay grade in their inspect
   pane. Harvesting is slow and noisy, and the yield adds growth-scaled metal concentrate, so premature
   cutting gives little and old stands become valuable but flammable capital. Build: higher harvest work,
   a plant comp recording the assay tier, visual accents, and a harvest postfix for the secondary yield.
   Small C#. **Model: sonnet.**
5. **Condensate Gardens**, which answers the owner's art-review note *"Needs more color in palette and
   more plants."* The owned Cauldron plants form distinct chemistry microhabitats:
   - crystal flowers ring stable taps;
   - blood-dark bouquets mark chronic leaks;
   - nettles colonize poisoned shorelines;
   - towering toxic flowers favour recent blowouts.

   Dewfall briefly saturates their purple, red, glass-white and green-amber accents. Build: owned
   Cauldron-only plant defs on the seven validated flora assets, habitat extensions, and a map scatterer
   keyed to vents, water and ruins. Small C# plus XML. **Model: sonnet.** Coordinate with
   `BEDAZZLE_FLORA_EXPANSION_1`.

Each ships a Mod Settings toggle.

## criteria

- Each of the five is quicktest-proven on a Cauldron map.
- A vent the vexxiss has silenced visibly recovers.
- Water the vexxiss poisons is announced, never silent.
