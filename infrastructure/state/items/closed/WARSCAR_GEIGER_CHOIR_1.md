# WARSCAR_GEIGER_CHOIR_1 — the Geiger choir: tick, wind on metal, the silence, the hum; the tetchik in a jar

From `WARSCAR_BEDAZZLE_SITTING_1`. Design source:
`design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` §2.4 and §4 #7 (turn-4 IN).

## spec

1. **Layers**, on the shipped `RM_ProximitySoundscapeExtension` + `RM_MapComponent_ProximitySoundscape`:
   the **tetchik tick** (group `WarscarTick`: `RM_Tetchik` and `RM_Glower` plants, tempo from tagged
   density so crust ticks even when the beetles hide); **wind on metal** (group `WarscarWind`: ancient
   fortified walls, broken turrets, crane parts); **the silence** (wind layer 0 during `RM_Settling`);
   **the hum** (a sustainer on live rings and the aerosol screen); **the pools' boil** (a sustainer on
   reaction-liquor terrain, once `WARSCAR_RAINBOW_POOLS_1` lands); campaign **hole in the sound**
   inside Sentinel ground (RUT data only).
2. **Small additions to the soundscape component:** an optional `volumeFromWind` curve, a hard 0 during a
   named condition, and a `suppressInRadiusOf` thing list. Verify it can tag a **pawn** (built for trees).
3. **Placeholder grains** until real audio; one global volume slider.
4. **A tetchik in a jar** (turn-4 IN): **`RM_TetchikJar`**, made from a captured tetchik and glass. A
   living pollution counter: on the map it ticks with the glower under it; carried by a caravan it
   ticks faster on polluted world tiles and in toxic weather (rate from `RM_PollutionSense`,
   `WARSCAR_AEROSOL_SCREEN_1`), with a caravan message before arrival on a polluted tile.
5. **Mod Settings:** choir on/off · tick volume ceiling · tick density · wind layer on/off ·
   reduced-repetition mode · jar warnings on/off.

## criteria

- Standing over thick glower ticks faster than bare slag (sustainer volume/rate read).
- The wind layer goes silent when `RM_Settling` starts and returns when it ends.
- A caravan carrying a tetchik jar gets the warning approaching a polluted tile.
