# ABYSS_HIDDEN_SHIP_PROBES_1 work log 2026-10-03
(started; choices below)
## Choices
- Abyss slice only: RM_MapComponent_ShipCover (Source/RM_MapComponentShipCover.cs). Cover 0..1 on a player-home RM_Abyss map holding a GravEngine; grows over ~6 days while QUIET (<=4 lit building lamps; more lamps erode it 2x), "covered" at >=0.6.
- Not permanent: lapses after 15 days covered, 3-day cooldown. Resets when the engine leaves the map (engine start) and on a probe report. The cost is staying dark and cold in a poor place; nothing else stored.
- Probes: every 3-6 days while covered, one scout spawns at an edge, quarters a colonist's position (LordJob_DefendPoint). It reports if a MOVING colonist (14 cells) or lit lamp (22 cells) stays in sight 10 s cumulative; report = cover collapses + cooldown + letter. Avoid by standing still/dark or killing it. Leaves after 1 day.
- Tier: probe kinds come from RM_AbyssProbeExtension on the RM_Abyss BiomeDef (empty = vanilla Mech_Militor, faction mechanoids). No IP in the RM tier.
- Settings: shipCoverEnabled, probesEnabled (defaults on). Build OK; validation cover_check added (offline PASS).
## Blockers / owed (other mods)
- Pursuit slowing and trade-ship blocking need hooks in EmpirePursuit (src/RimUtinni/EmpirePursuit) / trader incidents: read RM_MapComponent_ShipCover.IsCovered(map) (reflection or assembly ref) and multiply raid delay / veto orbital trader. surveyShadowBiomes 4x already static for the biome.
- Campaign patch owed: add RSW_DW_KotORDroidBad_KX12UPD / _KX12APD (+ _sapper) to the RM_Abyss biome's RM_AbyssProbeExtension/probeKinds and probeFaction = Empire from the Utinni layer.
- Live proof (probe report timing, LordJob_DefendPoint behaviour) is a joint session; not deployed.
