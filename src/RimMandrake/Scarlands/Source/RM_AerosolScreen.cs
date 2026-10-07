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

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!ActiveScreens.Contains(this)) ActiveScreens.Add(this);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            ActiveScreens.Remove(this);
            base.PostDeSpawn(map, mode);
        }

        // Read by the prefixes below and by the Settling film. A colony carries a handful of
        // screens at most; this is never a whole-map scan.
        public static bool IsPositionScreened(IntVec3 c, Map map)
        {
            if (!RM_WarscarSettings.aerosolScreenEnabled || map == null) return false;
            for (int i = 0; i < ActiveScreens.Count; i++)
            {
                RM_CompAerosolScreen s = ActiveScreens[i];
                if (s?.parent == null || s.parent.Map != map || !s.IsScreenLive) continue;
                float r = s.Radius;
                if (c.DistanceToSquared(s.parent.Position) <= r * r) return true;
            }
            return false;
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

    // One prefix set for every aerosol screen. Applied by this assembly's PatchAll (RM_ChotrixPatches /
    // RM_TotchakPatches run PatchAll over the whole assembly), like RM_WarscarPatches.
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
}
