# WARSCAR_TURRETS_TRACK_1 — the turrets still track; refit an old-line turret

From `WARSCAR_BEDAZZLE_SITTING_1`. Design source:
`design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` §4 #5 (turn-4 IN).

## spec

1. **Tracking without firing:** a turret-aim comp with **no verb** on the Warscar's broken ancient turrets
   (Odyssey's ruin turrets, and our `RUT_BustedShieldedTurret` where the campaign places it): the barrel
   top rotates to follow the nearest moving pawn within range, never fires. In a Settling they are the
   only things moving (a readable, eerie sign).
2. **Refit:** a construction job on a broken turret consuming components, steel and **`RM_Etchant`**
   (`WARSCAR_RAINBOW_POOLS_1`; before the pools exist, advanced components instead, slower) converts it
   into **`RM_OldLineTurret`**: slow-firing, long range, heavy hitting, player-owned, powered. Strong,
   balanced by refit cost and a long cooldown (the owner's principle). Reuse the gun plumbing of
   `RUT_AncientShieldedTurret` (AssailantSalvage) as the reference shape, re-authored on RM.
3. **Mod Settings:** tracking on/off · refit on/off · old-line turret damage and cooldown.

## criteria

- A broken turret on a Warscar quicktest rotates toward a moving pawn and never fires (state read on
  the comp's aim angle).
- The refit job yields a working `RM_OldLineTurret` that fires at hostiles.
