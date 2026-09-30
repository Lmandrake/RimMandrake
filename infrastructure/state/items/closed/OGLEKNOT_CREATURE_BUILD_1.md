# OGLEKNOT_CREATURE_BUILD_1 — build RM_Ogleknot, the Contagion's eye-knot

Supersedes `IKEE_REJECT_SALVAGE_1`. Name and home decided by question card
2026-09-28 (decision taken by question card: home = The Contagion, name =
Ogleknot; both the recommended options). Origin: the owner ruled the rejected
2026-09-28 Ikee render "can still be made into a creature, just a new one."

## spec

- **Art exists and is validated — do not queue any art.** The render is the
  RM_Ikee_* job of 2026-09-28: `infrastructure/artpipe/_artsrc/RM_Ikee_{south,east,north}/`
  and its done/ manifests. Copy the three PNGs to RM_Ogleknot's texPath in the
  Contagion mod; textures bind by texPath. (The prior Ikee art restore is
  separate and already done — leave RM_Ikee alone.)
- **The creature**: a knot of mismatched eyeballs of different sizes walking on
  spider-stilt tendril legs. Small, skittering, Contagion register (Gawpsack /
  Fleshsop / Peeper family). Description written from the render in the biome's
  voice. Wild in the Contagion only (one biome, one home).
- Roster wiring into the Contagion cast (respect the def-vs-patch tier split
  the biome already uses); Mod Settings coverage per the settings law.
- Behavior: base small-critter is acceptable for v1; anything fancier (a
  watcher mechanic) is a future sitting row, not this build.

## criteria

- RM_Ogleknot def collision-proven (name swept 0 files, probe korrum 68,
  2026-09-28), renders from its own texPath in a quicktest, appears in the
  Contagion merged roster read (parse `<wildAnimals>` by node NAME).
