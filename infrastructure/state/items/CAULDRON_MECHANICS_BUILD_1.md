# CAULDRON_MECHANICS_BUILD_1 — Build the Cauldron mechanics

From `CAULDRON_BEDAZZLE_SITTING_1` (volley closed 2026-09-28; every ruling is a
ledger note on that item, owner-typed). Analysis source:
`design/Jawa/worldbuilding/biomes/cauldron_bedazzle_review_2026-09-28.md`
(§Candidate mechanics slate carries the engine notes). Mod is
`src/RimMandrake/PoisonForest/` today; coordinate with `CAULDRON_FULL_RENAME_1`.

## spec

Five organs, one machine:

1. **The Engine Underfoot** (soundscape). Owner: "The ground should rush and groan
   and sigh and rumble and gurgle from all the strange chemistry flowing around.
   Hisses and dull slow roars. Like a slow steam engine." Layered BiomeDef ambient
   SoundDefs: low sustainer floor + randomized one-shot groans/gurgles clustering
   near vent cells; per-weather mixes. **The falter tell**: ahead of a vent bloom
   the ambient drops out and native fauna hush (one MapComponent) — silence is the
   alarm because the biome is otherwise never silent. Research-gated seismograph
   building raises a real alert for muted players.
2. **Four ratified weathers** (owner card 2026-09-12, names/behaviors ratified):
   scatter-dusk · vent bloom · vapour bank · dewfall — WeatherDefs at last; retire
   the donor Fog 90 block. Vent bloom carries the stacking metal-load hediff on
   outdoors+unroofed pawns (Blue Desert Haze shape), no double-tax with vanilla
   toxic buildup.
3. **The Gas**. Owner: "The gas is highly flammable with toxic smoke and should be
   stopped. It can also be refined for valuable liquid reagents." Vent ThingDefs
   special-spawned at mapgen leak visible flammable gas; ignition burns with TOXIC
   smoke (Biotech tox-gas pattern + combustion comp). **Gas-tap scaffold** building
   caps a vent: stops the leak AND banks flow for refining — safety and industry as
   one act.
4. **The Filter-Works** (discoverable tech). Owner: "the discoverable tech is about
   conversion of one fluid to another via filtering." One mechanic on the canon
   LiquidDef/FlowWorks registry: filter building + consumable cartridges converts
   input fluid → output fluid. Launch recipes: tapped gas condensate → valuable
   liquid reagents; toxic water → potable water. Taught by studying the corroded
   ruin kit (study-interactable); the ruin set pieces are part of this item.
5. **The Vexxiss behaviors** (def lives in `CAULDRON_RULED_CONTENT_1`):
   - **Inhales a vent deeply** → that vent's production pauses for days; it pries at
     scaffolds to drink (industry's living rival).
   - **Fire warden**: fires/gas ignition → it attacks the igniter and smothers the
     flames out (JobGiver keyed to fire + mental state targeting the fire-starter).
   - **Poisons water on touch**: water cells it wades through become toxic water
     (FlowWorks terrain/liquid swap).
   - NO explosion, alive or dead.
6. **Oomo's Grimace** (gods, biome-local per Blue Desert precedent). Owner: "Oomo
   will dislike it but not refuse to go." Grudging shrine kit in the ruins, sour
   flavor tint on water rites here, no precept defs. Pure content.

## criteria

- Every mechanic feature-gated in Mod Settings, defaults = shipped behavior,
  all-off degrades gracefully (mod-settings law).
- Falter tell verified by state read, not screenshot hunt; no unattended live
  visual hunts (flyer-law shape applies to any animation claim).
- Weathers live in a quicktest read of the biome's weatherCommonalities.
- Nine-mark scorecard re-run at close: marks 1,2,3,5,6,7,8,9 all HAVE
  (6 = gravship touch remains the one deliberate gap this pass — the slate's
  ship-scab candidate E was neither ruled in nor struck; it stays sitting-row
  material, not silently dropped).
