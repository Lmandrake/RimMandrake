using System;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using Verse;

namespace RimMandrake.Watchers
{
    /// <summary>
    /// WATCHER_CREATURES_MOD_1, owner ruling 2026-10-08 ("Full set"): the optional non-body flinch cues, built once for every member.
    /// A member lists only the cues it has, under RM_WatcherExtension.cues; an absent node = it ignores that cue. Each kind has its own
    /// Mod Settings toggle. While any cue holds it goes under and stays under (the geophone rule). Example:
    ///   <cues>
    ///     <gas><gasTypes><li>ToxGas</li></gasTypes><minPercent>0.1</minPercent></gas>
    ///     <heat><aboveC>-120</aboveC></heat>
    ///     <fire><radius>8</radius></fire>
    ///     <steam><things><li MayRequire="mandrake.rm.terminalbiomes">RM_SteamDevil</li></things><radius>10</radius></steam>
    ///     <shade><minShade>0.5</minShade></shade>
    ///     <buried><hediffs><li MayRequire="mandrake.rm.bluedesert">RM_MurrekBuried</li></hediffs><radius>10</radius></buried>
    ///     <light><minGlow>0.5</minGlow></light>
    ///   </cues>
    /// Reused detection: vanilla GasGrid.DensityPercentAt, GridsUtility.GetTemperature, the Fire lister, GlowGrid.GroundGlowAt;
    /// CreatureBehaviors' RM_MapComponent_ShadeGrid.ShadeAt (by reflection, the geophone pattern: this mod is standalone);
    /// the murrek's own RM_MurrekBuried hediff (BlueDesert's RM_MurrekDrift.Bury) named as data, so no assembly reference.
    /// </summary>
    public class RM_WatcherCues
    {
        public GasCue gas;
        public HeatCue heat;
        public FireCue fire;
        public SteamCue steam;
        public ShadeCue shade;
        public BuriedCue buried;
        public LightCue light;

        public class GasCue
        {
            public List<GasType> gasTypes = new List<GasType>();
            public float minPercent = 0.1f;
        }

        /// <summary>Its own cell at or above this temperature (the Chill's pralq: warmth melts its crust).</summary>
        public class HeatCue
        {
            public float aboveC = 40f;
        }

        public class FireCue
        {
            public float radius = 8f;
        }

        /// <summary>A listed Thing (a steam devil; any vent-type thing) within radius.</summary>
        public class SteamCue
        {
            public List<ThingDef> things = new List<ThingDef>();
            public float radius = 10f;
        }

        /// <summary>A shade-dweller: out only where shade is at least minShade (Long Shade's ennuk).</summary>
        public class ShadeCue
        {
            public float minShade = 0.5f;
        }

        /// <summary>A pawn carrying one of these hediffs (a buried murrek) within radius.</summary>
        public class BuriedCue
        {
            public List<HediffDef> hediffs = new List<HediffDef>();
            public float radius = 10f;
        }

        /// <summary>Its cell lit at or above minGlow (carried light; the ikee "dives when the light comes").</summary>
        public class LightCue
        {
            public float minGlow = 0.5f;
        }

        public IEnumerable<string> ConfigErrors()
        {
            return RM_WatcherKernel.CueConfigErrors(gas != null, gas?.gasTypes?.Count ?? 0, gas?.minPercent ?? 0f,
                heat != null, heat?.aboveC ?? 0f, fire != null, fire?.radius ?? 0f,
                steam != null, steam?.things?.Count ?? 0, steam?.radius ?? 0f, shade != null, shade?.minShade ?? 0f,
                buried != null, buried?.hediffs?.Count ?? 0, buried?.radius ?? 0f, light != null, light?.minGlow ?? 0f);
        }
    }

    public static class RM_WatcherCueUtility
    {
        /// <summary>The cues holding for this watcher where it stands. Only the readings of cues that are on are taken.</summary>
        public static CueKind CuesNow(Pawn p, RM_WatcherExtension ext)
        {
            RM_WatcherCues c = ext.cues;
            Map map = p.Map;
            if (c == null || map == null)
            {
                return CueKind.None;
            }
            IntVec3 at = p.Position;
            var r = new CueIn
            {
                gasOn = c.gas != null && RM_WatchersSettings.cueGas,
                heatOn = c.heat != null && RM_WatchersSettings.cueHeat,
                fireOn = c.fire != null && RM_WatchersSettings.cueFire,
                steamOn = c.steam != null && RM_WatchersSettings.cueSteam,
                shadeOn = c.shade != null && RM_WatchersSettings.cueShade,
                buriedOn = c.buried != null && RM_WatchersSettings.cueBuried,
                lightOn = c.light != null && RM_WatchersSettings.cueLight,
                fireDistSq = float.MaxValue, steamDistSq = float.MaxValue, buriedDistSq = float.MaxValue,
            };
            if (r.gasOn)
            {
                r.gasMin = c.gas.minPercent;
                for (int i = 0; i < c.gas.gasTypes.Count; i++)
                {
                    r.gasPercent = Math.Max(r.gasPercent, map.gasGrid.DensityPercentAt(at, c.gas.gasTypes[i]));
                }
            }
            if (r.heatOn)
            {
                r.heatAboveC = c.heat.aboveC;
                r.tempC = at.GetTemperature(map);
            }
            if (r.fireOn)
            {
                r.fireRadius = c.fire.radius;
                r.fireDistSq = NearestThingDistSq(map, at, ThingDefOf.Fire);
            }
            if (r.steamOn)
            {
                r.steamRadius = c.steam.radius;
                for (int i = 0; i < c.steam.things.Count; i++)
                {
                    r.steamDistSq = Math.Min(r.steamDistSq, NearestThingDistSq(map, at, c.steam.things[i]));
                }
            }
            if (r.shadeOn)
            {
                r.shadeMin = c.shade.minShade;
                bool gridActive = TryGridShade(map, at, out float gridShade);
                r.shade = RM_WatcherKernel.ShadeReading(at.Roofed(map), gridActive, gridShade, map.skyManager.CurSkyGlow);
            }
            if (r.buriedOn)
            {
                r.buriedRadius = c.buried.radius;
                r.buriedDistSq = NearestCarrierDistSq(p, c.buried.hediffs);
            }
            if (r.lightOn)
            {
                r.lightAbove = c.light.minGlow;
                r.glow = map.glowGrid.GroundGlowAt(at);
            }
            return RM_WatcherKernel.Cues(r);
        }

        private static float NearestThingDistSq(Map map, IntVec3 at, ThingDef def)
        {
            float best = float.MaxValue;
            if (def == null)
            {
                return best;
            }
            List<Thing> things = map.listerThings.ThingsOfDef(def);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i].Spawned)
                {
                    best = Math.Min(best, (things[i].Position - at).LengthHorizontalSquared);
                }
            }
            return best;
        }

        private static float NearestCarrierDistSq(Pawn watcher, List<HediffDef> hediffs)
        {
            float best = float.MaxValue;
            IReadOnlyList<Pawn> pawns = watcher.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn o = pawns[i];
                if (o == watcher || o.health?.hediffSet == null)
                {
                    continue;
                }
                for (int h = 0; h < hediffs.Count; h++)
                {
                    if (hediffs[h] != null && o.health.hediffSet.HasHediff(hediffs[h]))
                    {
                        best = Math.Min(best, (o.Position - watcher.Position).LengthHorizontalSquared);
                        break;
                    }
                }
            }
            return best;
        }

        // CreatureBehaviors' RM_MapComponent_ShadeGrid (src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs):
        // ShadeAt(IntVec3) 0..1 and SunHeatActive. ShadeAt reads 0 ("no shade anywhere") when the grid is off, so it is used only while
        // SunHeatActive; otherwise the sky and the roof decide (RM_WatcherKernel.ShadeReading).
        private static bool shadeResolved;
        private static Type shadeGridType;
        private static MethodInfo shadeAt;
        private static PropertyInfo shadeActive;

        private static bool TryGridShade(Map map, IntVec3 at, out float shade)
        {
            shade = 0f;
            if (!shadeResolved)
            {
                shadeResolved = true;
                shadeGridType = GenTypes.GetTypeInAnyAssembly("RimMandrake.CreatureBehaviors.RM_MapComponent_ShadeGrid");
                shadeAt = shadeGridType?.GetMethod("ShadeAt", BindingFlags.Public | BindingFlags.Instance, null, new[] { typeof(IntVec3) }, null);
                shadeActive = shadeGridType?.GetProperty("SunHeatActive", BindingFlags.Public | BindingFlags.Instance);
                if (shadeAt == null || shadeAt.ReturnType != typeof(float) || shadeActive == null || shadeActive.PropertyType != typeof(bool))
                {
                    shadeAt = null;
                }
            }
            if (shadeAt == null)
            {
                return false;
            }
            MapComponent grid = map.GetComponent(shadeGridType);
            if (grid == null || !(bool)shadeActive.GetValue(grid))
            {
                return false;
            }
            shade = (float)shadeAt.Invoke(grid, new object[] { at });
            return true;
        }
    }
}
