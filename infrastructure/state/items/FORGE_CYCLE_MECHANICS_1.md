# FORGE_CYCLE_MECHANICS_1 — the Forge fire-and-water grand cycle

From `FORGE_BEDAZZLE_SITTING_1`, owner-typed 2026-09-29 (verbatim in that item's
ledger notes): *"This is a biome of fire and water. The open lava is horrible,
hot, deadly. The occasional washes of superheated gas burst ignite much of the
map. Then the torrential rains pour down, causing flooding. There should be
huge plumes of steam and transformation of the lava vents to temporary basalt
shingle and pumice chunk."* Strange forms then grow from the frozen crust;
*"Eventually glowing cracks form on the rock covering, and the whole thing
melts back into lava again, destroying them."*

🔴 **Coordinate with `FORGE_MECHANICS_1` (FOUNDRY, state doing)** — its F1
WeatherPulse/FlashCycle is the substrate this EXTENDS; do not double-author the
pulse. A note pointing here sits on that item.

## spec

The pulse becomes a six-phase grand cycle:

1. **Still heat** — baseline; open lava as deadly as ever.
2. **Gas wash** — superheated burst ignites swathes of flammable map (vanilla
   fire, our trigger off the pulse condition).
3. **Torrential boiling rain + FLOODING** — the existing deluge plus low-cell
   flooding via the canon FlowWorks flood engine (its defects closed at
   `747b0025`).
4. **The freeze** — huge steam plumes; lava-vent/lava-edge cells terrain-swap
   to TEMPORARY basalt shingle + pumice chunk (walkable); the deadliest ground
   becomes the treasure floor.
5. **The growth** — floatstone gardens bloom on the crust (lace-walled globes;
   caught ripe = floatstone material per `FORGE_RULED_CONTENT_1`; unharvested
   globes tear free and drift off-map ahead of the melt — the form the lava
   never gets back). The flash-flora harvest window (wired FlashFlora) runs on
   the same clock.
6. **Glowing cracks → melt-back** — visible warning terrain phase, then
   reversion to lava destroying remaining growths and anyone standing there.
   Things on melting cells: destroy + damage, no silent vanishing.

Plus, folded in at turn 3 unopposed:
- **Soundscape + telegraph** (§9 of the frozen sheet as real SoundDefs;
  a hiss that swells before the burst; a letter/alert fallback for muted
  players). Verify the telegraph via STATE READ, never a screenshot hunt.
- **Dhokkur dormancy** keyed to the rain phase (CanBeDormant precedent);
  path-memory MapComponent kept light.
- **Vapor columns rendered** (`RM_MapComponent_VaporColumns` already computes
  the field) + sky herds congregating in them (`GetWanderRoot` seam).

Feature-gate everything in Mod Settings; defaults = shipped behavior; all-off
degrades gracefully.

## criteria

- Full cycle observable in a quicktest via state reads (phase enum, terrain
  swap counts, flood cells, growth spawns, revert destroys).
- Nine-mark re-score at close: the Forge's remaining deliberate gaps are mark 6
  (gravship touch — B struck) and mark 2 unless the growth forms carry it;
  record both as owner-accepted misses, not silent drops.

## round 36 (2026-10-03): numbers, audio, the dhuvvox swarm

- **Audio:** already shipped with vanilla clips by `FORGE_GPT_ENRICHMENT_1` (`RM_ForgeVoices.xml`: still throb,
  vent cough, rain hiss, basalt tick, glass sing, crack pulse, phase stinger). Owner 2026-10-03: vanilla ships as
  final. Nothing audio-owed remains.
- **PROVISIONAL numbers:** every value in `RM_ForgePulse.xml`'s `RM_ForgeCycleExtension` (phase hours, wave and
  flood counts, radii, chances, melt burn) and every voice interval in `RM_ForgeVoices.cs`.
- **Dhuvvox mass eruption built:** entering the Rain spawns **60 (PROVISIONAL)** extra wild dhuvvox within
  **12 cells (PROVISIONAL)** of resident ones; entering the Freeze burrows every survivor back with a
  `Filth_Ash` scar and one counted message (no silent vanish). Toggle `dhuvvoxSwarmEnabled`. Report tokens
  `swarmLive/swarmErupted/swarmResealed`; suite components `rain_erupts_dhuvvox_swarm` and
  `rain_end_reseals_swarm_with_signs` (mock breaks red).
- Still owed: live re-run of the cycle with the swarm; dhokkur path memory; crust art.
