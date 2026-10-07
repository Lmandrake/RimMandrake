# WARSCAR_AEROSOL_SCREEN_1 — the projectors still hum: live rings, the aerosol screen, salvageable generators, glower shielding

From `WARSCAR_BEDAZZLE_SITTING_1`. Design source:
`design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` §2.2 and §4 #2, with the
turn-4 rulings in `warscar_bedazzle_cast_2026-09-30.md` §0.
Owner, typed: *"I like powerful tech. Don't be afraid of making good ideas broadly useful and powerful
(like the aerosol shield). There are many other ways to normalize it."* and *"We're going to have to
evaluate those shield generators if they're present and working. That's salvage man!"* ⇒ **broad in
scope, balanced by cost and gating; never narrowed.**

## spec

1. **Lift the core to RM.** The particulate effect in `src/RimUtinni/ShipShields/`
   (`CompShieldParticulateScreen`, `ShieldHazardUtility.HasParticulateHazard`, the Harmony prefixes on
   `ToxicUtility.DoAirbornePawnToxicDamage` and `GameCondition_ToxicFallout.DoCellSteadyEffects`)
   moves into an RM comp **`RM_CompAerosolScreen`** (EnvironmentalHazards or a new small RM assembly).
   The RUT shield module then calls the RM comp: one patch, two consumers, no franchise in the free tier.
2. **`RM_PollutionSense.IsPollutedHere(Map)`**: tile pollution ≥ Light, OR any active toxic-air
   condition/weather (the two vanilla callers plus `RM_Settling`), OR the biome carries
   **`RM_PollutedBiomeExtension`** (Warscar, Wasteland, Cauldron, Contagion). ShipShields'
   toxic half calls it too.
3. **What the screen blocks (broad, ruled):** all airborne toxic exposure; fallout cell effects; the
   Settling film and its lift front; Wasteland ash-fall pollution writes (in-radius check in
   `RM_MapComponent_WastelandStorms`' fall loop); noxious-haze mood and plant factors in radius;
   **calibrated:** scrubs `GasType.ToxGas` and slowly un-pollutes ground in radius. Never bullets,
   heat or cold. Works in **every polluted biome** (ruled turn 2).
4. **Balanced by cost:** 400 W (900 W calibrated); a `CompRefuelable` burning **dielectric gel**
   (`WARSCAR_RAINBOW_POOLS_1`) ~1 per 3 days, half radius without it; materials plasteel + components +
   one **`RM_ProjectorCore`**; research needs an analysed live ring; calibration needs the old tongue's
   projector reading (`WARSCAR_OLD_TONGUE_1`).
5. **`RM_AerosolScreen`**: radius 7.9, `CompPowerTrader`, `CompFlickable`, **gravship-placeable**, dome
   drawn with the interceptor bubble material as a visual only (⛔ never subclass the interceptor:
   projectiles pass). Add the Warscar row to `BIOME_SHIP_CONTRIBUTIONS_1`: *the aerosol screen*.
6. **The rings:** `RM_WarscarProjector` dead and live variants, placed by a genstep along the Odyssey
   ruins' outer edge. Live = self-powered `RM_CompAerosolScreen`; analysable via Biotech
   `CompProperties_CompAnalyzableUnlockResearch` + `ResearchProjectDef.requiredAnalyzed`; analysis must
   not consume the ring (verify).
7. **Salvage, ruled by the owner:** every ring carries a **condition** (rolled at generation, shown on
   inspect: *dead / failing / working*), read by an **evaluate** job (Crafting 6, minutes). A
   **working** generator can be **uninstalled and hauled home** (`Minifiable`) and reinstalled as a
   working screen with no research — the prize of the biome, rarer than cores. A failing one
   uninstalls into a repair job (WreckedMachines' WRECKED → KLUDGED → REPAIRED ladder is the shipped
   precedent; reuse it if its code is a comp). A dead one deconstructs for a `RM_ProjectorCore` (chance)
   plus steel and components. Uninstalling a live ring ends its dome on that map; that is the trade.
8. **The ship wakes the line** (turn-4 IN): while a landed gravship's `GravEngine` is within ~40
   cells, dead rings in range re-power (live dome, analysable) until it lifts. A check in the ring comp.
9. **Glower shielding** (turn-4, owner typed *"1+2"*, half 2): `RM_GlowerCrust` becomes radiation/toxic
   shielding. **`RM_GlowerShieldPanel`** (a wall-adjacent building) gives `ToxicEnvironmentResistance`
   to pawns in its room and halves room toxic-gas damage; **`RM_GlowerPlate`** (utility-slot apparel)
   gives `ToxicEnvironmentResistance` +0.5 and `ToxicResistance` +0.2. Both cost glower crust in bulk;
   balanced by weight and crust supply. (Half 1, the pool catalyst, is `WARSCAR_RAINBOW_POOLS_1`.)
10. **Readable signs:** the film's hard edge at the dome; a "screened" inspect line on pawns; the ring's
    condition on inspect; the hum (`WARSCAR_GEIGER_CHOIR_1`).
11. **Mod Settings:** screen radius · power · gel burn · calibration on/off · humming rings per map
    (0–3) · ring salvage on/off · ship-wakes-line on/off · glower shielding on/off.

## criteria

- RUT shield particulate mode and `RM_AerosolScreen` share one prefix set (grep: one patch class).
- Inside a dome: no toxic buildup in fallout, ToxRain, `RM_Settling` or Wasteland ash; calibrated, tox
  gas clears.
- A working ring evaluates "working", uninstalls, and runs at home with no research.
- A gravship landed beside dead rings lights them; lifting off darkens them.
- Built on a gravship, the screen flies and works on the next polluted tile.

## progress

- 2026-10-06 (parts 1-2, offline, uncommitted by the worker): `src/RimMandrake/Scarlands/Source/RM_AerosolScreen.cs`
  holds `RM_PollutedBiomeExtension`, `RM_PollutionSense` (tile >= Light, ToxicFallout / `doToxicBuildup`
  weather / `RM_Settling`, or the extension), `RM_CompProperties_AerosolScreen` + `RM_CompAerosolScreen`
  (virtual `IsScreenLive`/`Radius` for the RUT module to derive from; empty `CompRefuelable` halves radius)
  and the prefix pair on `ToxicUtility.DoAirbornePawnToxicDamage` and
  `GameCondition_ToxicFallout.DoCellSteadyEffects`. The Settling film skips screened cells; the choir's
  pollution stand-in forwards to `RM_PollutionSense`; `RM_Warscar` carries the extension; settings gained
  "Aerosol screens" on/off + radius factor. Builds clean.
- Still owed: ShipShields deriving from `RM_CompAerosolScreen` and dropping its own two prefixes (criterion
  "one patch class"); the extension on Wasteland/Cauldron/Contagion; parts 3-11 (no `RM_AerosolScreen`
  building def yet, so nothing in game carries the comp).
