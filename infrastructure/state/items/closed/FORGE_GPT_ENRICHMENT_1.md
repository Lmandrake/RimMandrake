# FORGE_GPT_ENRICHMENT_1 — seven GPT-suggested enrichments the owner picked

Source: a GPT enrichment consult (codex exec, gpt-5.6-sol xhigh, 2026-09-30) on the Forge. The owner
picked these seven by question card. Not picked, so out: The Last Lift, Quench Crossings, and The Anvil
Answer. Builds on `FORGE_RULED_CONTENT_1` and `FORGE_CYCLE_MECHANICS_1`, and must stay inside the Forge
sitting's rulings (Floatstone is the sole growth-phase form; vent machines are cut; vanilla geothermal
suffices).

## spec

1. **Floatstone keelwork.** Pearl-white, spun-sugar floatstone braces threaded through a gravship
   reduce its launch cost or raise its effective payload, and ring glassily at launch. Build: a keel-brace
   ThingDef, a Harmony hook into Odyssey's gravship mass/launch-cost calculation, and an inspect string
   showing the mass saved. Small C# plus XML. **Model: opus** (it touches the gravship calculation).
2. **Spunstone bonding.** Floatstone construction is learned in the Forge: studying mature gardens and
   foundry salvage triggers a breakthrough that reveals a hidden research project. That project unlocks
   keel braces, high-speed doors and advanced structural parts. This is material science, not a vent
   machine. Build: `CompStudiable` on gardens and caches, a knowledge counter, a hidden
   ResearchProjectDef, and an unlock letter. Small C#. **Model: sonnet.**
3. **Four voices of the Forge.** Each cycle phase has its own sound:
   - still heat: a subterranean, turbine-like throb;
   - gas washes: approach with coughing vents;
   - boiling rain: a deafening hiss;
   - cooling basalt: ticks and sings like glass.

   Before remelt, the harmony drops out and a deep cracking pulse begins. Muted players get matching
   visual alerts. Build: layered sustainers chosen by the cycle MapComponent, positional geyser
   one-shots, phase stingers, and a letter fallback. Small C#. **Model: sonnet.**
4. **White plume fronts.** Quench steam rolls out from newly crusted vents as moving fronts. They
   briefly obscure shooters, soak the ground, and heat exposed pawns faster through **vanilla
   heatstroke** (the one-kind-of-heat ruling, `SOLAR_HEAT_EXPOSURE_1`). Vapour-adapted creatures move
   normally inside them. Build: a phase-bound cell front, flecks, a ranged-accuracy modifier, AI
   avoidance, and an adapted-species exemption. Medium C#. **Model: opus.**
5. **Sky pastures.** The existing vapour-column field becomes visible, inhabited aerial terrain. Steam
   columns spiral ash upward; the aerofleets, beldons, fleet fliers and admitted giants congregate
   there; jossurs circle above and make real flying stoops on prey (the flyers-fly rule). Selecting a
   flier highlights the useful columns. Build: render the column grid, add column-aware wander and hunting,
   wire `RM_CompVaporDrifter`, and give jossurs real 1.6 flight. Small–medium C#. **Model: sonnet.**
6. **Dhokkur ways.** Dormant dhokkur resemble outcrops, but converging gutter lines and worn
   depressions give them away. When rain starts, the stone groans, water pours through their plates,
   and they follow old glass-polished tracks. A careful player can site walls off the tracks; walls in
   the way get shoved aside rather than annihilated. Build: a dormant graphic swap, a phase-triggered
   wake comp, a path-memory MapComponent, trail terrain, and shove/damage rules. Medium C#.
   **Model: opus.**
7. **The dhuvvox clock.** Nodules click open after rain, and ember-flecked swarms race across wet rock.
   They slow in the final quarter-hour, and at expiry every survivor visibly curls back into a
   persistent nodule; none vanishes. Build: phase spawning from nodule Things, timed states, swarm
   aggregation for performance, and resealing conversion with countdown inspect strings. Medium C#.
   **Model: sonnet.**

Each ships a Mod Settings toggle.

## criteria

- Each of the seven is quicktest-proven on a Forge map.
- A floatstone brace measurably changes gravship launch cost.
- No dhuvvox or dhokkur disappears without a visible trace.

## built (offline tranche, 2026-10-01)

- §1 keelwork: `RM_FloatstoneKeelBrace`, a vanilla gravship facility (`fuelSavingsPercent`, TUNED 5%, four per
  ship) linked to the grav engine by patch. MEASURED: Odyssey has no gravship mass, so no Harmony hook is needed.
  Remainder: `FORGE_KEELWORK_REMAINDER_1`.
- §2 spunstone: a study comp on mature gardens, a colony knowledge counter, `RM_SpunstoneBonding` hidden until
  revealed, and an unlock letter. Remainder: `FORGE_SPUNSTONE_SOURCES_1`.
- §3 voices: `RM_ForgeVoices` with phase sustainers, positional coughs and ticks, a cracking pulse, stingers and
  visual cues (always on when muted). Placeholder vanilla audio; owed: `FORGE_VOICES_AUDIO_1`.
- §7 dhuvvox clock: countdown, final quarter-hour slowing, nodule click, visible curl. Remainder:
  `FORGE_DHUVVOX_SWARM_REMAINDER_1`.
- Not built, each with its open question: §4 `FORGE_WHITE_PLUME_FRONTS_1`, §5 `FORGE_SKY_PASTURES_1`, §6
  `FORGE_DHOKKUR_WAYS_1`.
- Every built piece has a Mod Settings toggle. Live proof: `FORGE_ENRICHMENT_QUICKTEST_1`.
