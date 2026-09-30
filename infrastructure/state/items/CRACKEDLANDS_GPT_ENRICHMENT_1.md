# CRACKEDLANDS_GPT_ENRICHMENT_1 — six GPT-suggested enrichments the owner picked

Source: a GPT enrichment consult (codex exec, gpt-5.6-sol xhigh, 2026-09-30) on the Cracked Lands. The
owner picked these by question card. The Belly Sounder became the cross-biome
`GRAVSHIP_ACOUSTIC_SCANNER_1`, and its Cracked Lands payload (water, fossil strata, sealed pans) is
authored there. Not picked, so out: the one-stay water survey, fossils remember the map, and muttavaq
never disappears. The ruled versions of those three still stand in `CRACKEDLANDS_MECHANICS_BUILD_1`;
only GPT's extensions of them are out. Builds on `CRACKEDLANDS_RULED_CONTENT_1` and
`CRACKEDLANDS_MECHANICS_BUILD_1`. If `CRACKEDLANDS_FULL_RENAME_1` lands first, use its names.

## spec

1. **Ledges of Mercy.** Map generation places high ledges bearing worn figures, old offerings, and
   chime lines stretched across the canyon below. The inscriptions call the flood *"the mercy that
   kills, then feeds."* During warnings, neutral visitors and trained animals try to reach the nearest
   ledge. Build: ledge prefabs scattered above the flood mask; a flood-phase lord/job that favours them;
   inspectable carvings and one-shot memories; no campaign precepts. Small C#.
2. **Five beats before water.** The flood clock becomes spatially staged sound, in order: wind threads
   the slots; sleeper pans start ticking; tarruq calls stop; chime lines toll from the far canyon to the
   near; the flood becomes a continuous roar. Build: replace the global bell with emitters on
   map-generated chime anchors, pick the stage by flood phase and distance, gate tarruq ambience off
   during the pre-chime, and write bespoke SoundDefs. Small C#.
3. **Peakstorm light.** The map stays rainless, but the northern sky turns bruised red, distant lightning
   silhouettes the peaks, and dust briefly reverses as cool wet-clay air pushes through the slots. It
   raises flood odds without being a perfect timer. Build: a precipitation-free WeatherDef (sky, wind,
   motes, distant thunder) that the flood component weights. XML plus small C#.
4. **Three-height flora.** Red-brown **qirra mats** open only on recently wetted open clay. The Veqma
   (existing) maps hidden water in the blue shade. Pale **talus clasps** root beside fossil-bearing rock
   and slowly pry cracks wider. Only the Veqma shows green, and only inside the shade line. Build: PlantDefs
   with terrain/glow limits, the flood component waking the qirra, and a placement worker keeping talus
   clasps on natural walls; minor harvests only. Coordinate with `BEDAZZLE_FLORA_EXPANSION_1`, which
   also owes this biome flora. New names must be collision-swept, with art to an owner review sheet
   before any def ships.
5. **The recede feast.** Flood-touched mud suddenly moves like fur as irqit hatch in millions, breed
   once, and die into visible windrows as the ground dries. Convor, can-cell and woolamander migrants
   physically fly in, feed, and fly out overhead, never edge-spawning or vanishing. Build: bounded irqit
   cohorts from the soaked-cell list with lifecycle hediffs, and existing flight for the migrants. Small C#.
6. **Floodline salvage claim.** Receding mud exposes half-buried components and wreck silhouettes.
   Claim stakes appear, and a rival crew arrives to negotiate, race the player, or steal once relations
   collapse. Build: loot from the recorded flood cells plus a temporary visitor lord with claim-area jobs.
   The RM layer uses generic scavengers; the Utinni patch substitutes Jawas, crawler props and Star
   Wars dialogue. Small C#.

**Model: sonnet** for all six; each is small and checkable. Escalate the lord/AI pieces if they fight
the engine. Each ships a Mod Settings toggle.

## criteria

Each of the six is quicktest-proven. The migrants arrive and leave by visible flight.
