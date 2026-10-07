using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Scarlands
{
    // ════════════════════════════════════════════════════════════════════
    // WARSCAR_AEROSOL_SCREEN_1, parts 1-2: the RM aerosol-screen core and RM_PollutionSense.
    //
    //  * RM_CompAerosolScreen is the franchise-free lift of ShipShields' CompShieldParticulateScreen
    //    toxic half: a static registry of live screens and one IsPositionScreened(c, map) test.
    //    IsScreenLive and Radius are virtual so the RUT shield module can derive from this comp
    //    and gate on its own field mode, leaving ONE prefix set (RM_AerosolScreenPatches) for
    //    both consumers. ShipShields still carries its own prefixes until it is rebuilt against
    //    this assembly; while both run they agree (each only ever cancels exposure).
    //  * What it blocks here: every airborne toxic exposure (ToxicUtility.DoAirbornePawnToxicDamage,
    //    whose vanilla callers are GameCondition_ToxicFallout and WeatherWorker for doToxicBuildup
    //    weather, plus the Settling and its lift front), fallout cell effects, and the Settling film
    //    (checked inline in RM_GameCondition_Settling.DoCellSteadyEffects).
    //  * A CompRefuelable on the parent, when present and empty, halves the radius (spec 4: the
    //    dielectric-gel feed). With no refuelable comp the full radius applies.
    // ════════════════════════════════════════════════════════════════════

    // Marker on a BiomeDef: the biome's hazard is ours (Settling, ash fall) and should read polluted
    // even on a clean world tile. Warscar, Wasteland, Cauldron, Contagion.
    public class RM_PollutedBiomeExtension : DefModExtension
    {
    }

    public static class RM_PollutionSense
    {
        // True when the tile is polluted (Biotech PollutionLevel >= Light), the air is toxic now
        // (toxic fallout, a doToxicBuildup weather, or the Settling), or the biome says so.
        public static bool IsPollutedHere(Map map)
        {
            if (map == null) return false;
            if (ToxicAirNow(map)) return true;
            if (TilePolluted(map.Tile)) return true;
            BiomeDef biome = map.Biome;
            return biome != null && biome.HasModExtension<RM_PollutedBiomeExtension>();
        }

        public static bool ToxicAirNow(Map map)
        {
            if (map == null) return false;
            GameConditionManager g = map.gameConditionManager;
            if (g.ConditionIsActive(GameConditionDefOf.ToxicFallout)) return true;
            if (RM_SettlingDefOf.RM_Settling != null && g.ConditionIsActive(RM_SettlingDefOf.RM_Settling)) return true;
            WeatherDef w = map.weatherManager?.curWeather;
            return w != null && w.doToxicBuildup;
        }

        public static bool TilePolluted(PlanetTile tile)
        {
            return tile.Valid && Find.WorldGrid[tile].PollutionLevel() >= PollutionLevel.Light;
        }
    }

    public class RM_CompProperties_AerosolScreen : CompProperties
    {
        public float radius = 7.9f;
        // Self-powered screens (the live rings) set this false and ignore power entirely.
        public bool needsPower = true;
        public bool drawDome = true;
        // Part 3/4: a calibrated screen also scrubs GasType.ToxGas and slowly un-pollutes ground in radius.
        public bool calibrated = false;

        public RM_CompProperties_AerosolScreen()
        {
            compClass = typeof(RM_CompAerosolScreen);
        }
    }

    public class RM_CompAerosolScreen : ThingComp
    {
        private static readonly List<RM_CompAerosolScreen> ActiveScreens = new List<RM_CompAerosolScreen>();

        public RM_CompProperties_AerosolScreen Props => (RM_CompProperties_AerosolScreen)props;

        protected CompPowerTrader PowerTrader => parent.GetComp<CompPowerTrader>();
        protected CompFlickable Flickable => parent.GetComp<CompFlickable>();
        protected CompRefuelable Refuelable => parent.GetComp<CompRefuelable>();

        public virtual bool IsScreenLive
        {
            get
            {
                if (!parent.Spawned) return false;
                if (Flickable != null && !Flickable.SwitchIsOn) return false;
                if (Props.needsPower && PowerTrader != null && !PowerTrader.PowerOn) return false;
                return true;
            }
        }

        public virtual float Radius
        {
            get
            {
                float r = Props.radius * RM_WarscarSettings.aerosolScreenRadiusFactor;
                CompRefuelable fuel = Refuelable;
                if (fuel != null && !fuel.HasFuel) r *= 0.5f;
                return r;
            }
        }

        // The Map object this screen registered on. Thing.Map is Find.Maps[index], so a screen left in the static
        // registry by a previous game (load a save, nothing despawns) would alias onto the new game's map at the
        // same index; comparing the registered Map reference never does, and stale entries are pruned on spawn.
        private Map registeredMap;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            ActiveScreens.RemoveAll(s => s == null || s.registeredMap == null || !Find.Maps.Contains(s.registeredMap)
                || !s.parent.Spawned || s.parent.Map != s.registeredMap);
            registeredMap = parent.Map;
            if (!ActiveScreens.Contains(this)) ActiveScreens.Add(this);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            ActiveScreens.Remove(this);
            registeredMap = null;
            base.PostDeSpawn(map, mode);
        }

        private const int CalibrationIntervalTicks = 250;
        private const int ToxGasScrubPerPass = 12;   // density units (of 255) per cell per pass

        public override void CompTick()
        {
            base.CompTick();
            if (Props.calibrated && parent.IsHashIntervalTick(CalibrationIntervalTicks)) DoCalibrationPass();
        }

        // Rings tick Rare rather than Normal; whichever ticker the def uses, only one of these runs.
        public override void CompTickRare()
        {
            base.CompTickRare();
            if (Props.calibrated) DoCalibrationPass();
        }

        // Scrubs tox gas in radius and un-pollutes one random polluted cell. Slow by design.
        public void DoCalibrationPass()
        {
            if (!Props.calibrated || !RM_WarscarSettings.calibrationEnabled || !RM_WarscarSettings.aerosolScreenEnabled) return;
            if (!IsScreenLive || parent.Map == null) return;
            Map map = parent.Map;
            float r = Radius;
            GasGrid gas = map.gasGrid;
            PollutionGrid pol = map.pollutionGrid;
            List<IntVec3> polluted = null;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(parent.Position, r, true))
            {
                if (!c.InBounds(map)) continue;
                if (gas != null)
                {
                    byte tox = gas.DensityAt(c, GasType.ToxGas);
                    if (tox > 0)
                    {
                        byte nt = (byte)Mathf.Max(0, tox - ToxGasScrubPerPass);
                        gas.SetDirect(c, gas.DensityAt(c, GasType.BlindSmoke), nt,
                            gas.DensityAt(c, GasType.RotStink), gas.DensityAt(c, GasType.DeadlifeDust));
                        map.mapDrawer.MapMeshDirty(c, MapMeshFlagDefOf.Gas);
                    }
                }
                if (ModsConfig.BiotechActive && pol != null && pol.CanUnpollute(c))
                {
                    if (polluted == null) polluted = new List<IntVec3>();
                    polluted.Add(c);
                }
            }
            if (polluted != null) pol.SetPolluted(polluted.RandomElement(), false);
        }

        // Read by the prefixes below and by the Settling film. A colony carries a handful of
        // screens at most; this is never a whole-map scan.
        public static bool IsPositionScreened(IntVec3 c, Map map)
        {
            if (!RM_WarscarSettings.aerosolScreenEnabled || map == null) return false;
            for (int i = 0; i < ActiveScreens.Count; i++)
            {
                RM_CompAerosolScreen s = ActiveScreens[i];
                if (s?.parent == null || s.registeredMap != map || !s.IsScreenLive) continue;
                float r = s.Radius;
                if (c.DistanceToSquared(s.parent.Position) <= r * r) return true;
            }
            return false;
        }

        // Visual only (spec 5): the dome is drawn with the force-field bubble material, never the
        // interceptor class, so projectiles pass.
        private static Material domeMat;

        public override void PostDraw()
        {
            base.PostDraw();
            if (!Props.drawDome || !RM_WarscarSettings.aerosolScreenEnabled || !IsScreenLive) return;
            if (domeMat == null)
                domeMat = MaterialPool.MatFrom("Other/ForceField", ShaderDatabase.MoteGlow, new Color(0.95f, 0.75f, 0.35f, 0.18f));
            float d = Radius * 2f;
            Vector3 pos = parent.DrawPos;
            pos.y = AltitudeLayer.MoteOverhead.AltitudeFor();
            Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(pos, Quaternion.identity, new Vector3(d, 1f, d)), domeMat, 0);
        }

        public override void PostDrawExtraSelectionOverlays()
        {
            base.PostDrawExtraSelectionOverlays();
            if (parent.Spawned) GenDraw.DrawRadiusRing(parent.Position, Radius);
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_WarscarSettings.aerosolScreenEnabled) return "Aerosol screen: disabled in mod settings";
            string state = IsScreenLive ? "screening" : "idle";
            string s = "Aerosol screen: " + state + ", radius " + Radius.ToString("0.0");
            CompRefuelable fuel = Refuelable;
            if (fuel != null && !fuel.HasFuel) s += " (half radius: no gel)";
            return s;
        }
    }

    // One prefix set for every aerosol screen. Applied by this assembly's single PatchAll (RM_ChotrixPatches
    // runs it over the whole assembly), like RM_WarscarPatches.
    // Every airborne toxic exposure: toxic fallout, toxic weather, the Settling and its lift front.
    [HarmonyPatch(typeof(ToxicUtility), nameof(ToxicUtility.DoAirbornePawnToxicDamage))]
    public static class RM_AerosolScreenPatches_AirborneToxic
    {
        [HarmonyPrefix]
        public static bool Prefix(Pawn p)
        {
            if (p?.Spawned != true || p.Map == null) return true;
            return !RM_CompAerosolScreen.IsPositionScreened(p.Position, p.Map);
        }
    }

    // Toxic fallout's per-cell plant kill and item rot.
    [HarmonyPatch(typeof(GameCondition_ToxicFallout), nameof(GameCondition_ToxicFallout.DoCellSteadyEffects))]
    public static class RM_AerosolScreenPatches_FalloutCell
    {
        [HarmonyPrefix]
        public static bool Prefix(IntVec3 c, Map map)
        {
            if (map == null) return true;
            return !RM_CompAerosolScreen.IsPositionScreened(c, map);
        }
    }

    // Readable sign (spec 10): pawns standing in a screened cell say so on inspect.
    [HarmonyPatch(typeof(Pawn), nameof(Pawn.GetInspectString))]
    public static class RM_AerosolScreenPatches_PawnInspect
    {
        public static void Postfix(Pawn __instance, ref string __result)
        {
            if (!RM_WarscarSettings.aerosolScreenEnabled || __instance == null || !__instance.Spawned) return;
            if (!RM_CompAerosolScreen.IsPositionScreened(__instance.Position, __instance.Map)) return;
            string line = "Screened from airborne toxins";
            __result = string.IsNullOrEmpty(__result) ? line : __result + "\n" + line;
        }
    }

    // Noxious haze (Biotech): the thought, the plant growth factor, the stat part and meditation all
    // read NoxiousHazeUtility.IsExposedToNoxiousHaze(thing, cell, map) (the one-arg overload forwards
    // to it), so one prefix suppresses mood and plant factors for anything standing in a screened cell.
    [HarmonyPatch(typeof(NoxiousHazeUtility), nameof(NoxiousHazeUtility.IsExposedToNoxiousHaze), new[] { typeof(Thing), typeof(IntVec3), typeof(Map) })]
    public static class RM_AerosolScreenPatches_NoxiousHaze
    {
        [HarmonyPrefix]
        public static bool Prefix(IntVec3 cell, Map map, ref bool __result)
        {
            if (map == null || !RM_CompAerosolScreen.IsPositionScreened(cell, map)) return true;
            __result = false;
            return false;
        }
    }

    // Wasteland ash fall lives in another assembly that does not reference this one, so it is patched
    // by name at startup: skipped silently when RM_MapComponent_WastelandStorms (or its private DoFall)
    // is absent, so this assembly loads with or without the Wasteland mod. DoFall's finalizer clears the
    // flag even if it throws; PollutionGrid.SetPolluted(true) is refused only while the flag is set and
    // only for screened cells, so no other pollution source is touched.
    [StaticConstructorOnStartup]
    public static class RM_AerosolScreenWastelandBridge
    {
        [System.ThreadStatic] private static Map fallMap;

        static RM_AerosolScreenWastelandBridge()
        {
            try
            {
                System.Type t = AccessTools.TypeByName("RimMandrake.Wasteland.RM_MapComponent_WastelandStorms");
                System.Reflection.MethodInfo doFall = t == null ? null : AccessTools.Method(t, "DoFall");
                System.Reflection.MethodInfo setPolluted = AccessTools.Method(typeof(PollutionGrid), nameof(PollutionGrid.SetPolluted));
                if (doFall == null || setPolluted == null) return;
                Harmony h = new Harmony("mandrake.rm.warscar.aerosolwasteland");
                h.Patch(doFall,
                    prefix: new HarmonyMethod(typeof(RM_AerosolScreenWastelandBridge), nameof(FallPrefix)),
                    finalizer: new HarmonyMethod(typeof(RM_AerosolScreenWastelandBridge), nameof(FallFinalizer)));
                h.Patch(setPolluted, prefix: new HarmonyMethod(typeof(RM_AerosolScreenWastelandBridge), nameof(SetPollutedPrefix)));
            }
            catch (System.Exception e)
            {
                Log.Warning("[RM Warscar] aerosol screen could not bridge Wasteland ash fall: " + e.Message);
            }
        }

        public static void FallPrefix(MapComponent __instance) { fallMap = __instance?.map; }
        public static void FallFinalizer() { fallMap = null; }

        public static bool SetPollutedPrefix(IntVec3 cell, bool isPolluted)
        {
            Map m = fallMap;
            if (m == null || !isPolluted) return true;
            return !RM_CompAerosolScreen.IsPositionScreened(cell, m);
        }
    }
}
