using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GEOSTONE_BUILD_SIX_LABELS_AWAIT_STAMP: the hand-placed geological landmarks (design/RimMandrake/world_remake_2026-10-19/
    // 16_geo_landmarks.md). Decompiled 1.6 gives neither TileMutatorDef nor LandmarkDef a stone field, so each landmark is a
    // TileMutatorDef RM_Geo_<Name> carrying this extension, and a postfix on World.NaturalRockTypesIn returns its stones on a
    // tile that carries it. Geology crosses biome lines: that is the point, so the postfix replaces the biome's own pick.
    // It touches only maps generated afterwards: the rock list is computed fresh at map generation and never saved.
    // Defs: Defs/GeoLandmarks/RM_GeoLandmarks.xml. Proof: src/RimMandrake/Utils/remake/selftest_geostones.py.
    public class RM_GeoStonesExtension : DefModExtension
    {
        /// <summary>The walls of a map on this tile, in place of the biome's pick. At least one must be a plain natural
        /// rock: RM_PreciousCaves picks one of the list's non-resource rocks.</summary>
        public List<ThingDef> stones;

        /// <summary>The bool field of RM_EnvironmentalHazardsSettings that switches this landmark (default on).</summary>
        public string setting;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (stones == null || stones.Count == 0) yield return "RM_GeoStonesExtension has no stones";
            else if (!stones.Any(s => s != null && s.IsNonResourceNaturalRock))
                yield return "RM_GeoStonesExtension lists no plain natural rock (a map's walls need one)";
            if (RM_GeoStones.SettingField(setting) == null)
                yield return "RM_GeoStonesExtension setting '" + setting + "' is not a bool of RM_EnvironmentalHazardsSettings";
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_GeoStones
    {
        static RM_GeoStones()
        {
            MethodInfo target = AccessTools.Method(typeof(World), nameof(World.NaturalRockTypesIn), new[] { typeof(PlanetTile) });
            if (target == null)
            {
                Log.Error("[RM EnvironmentalHazards] geological landmarks: World.NaturalRockTypesIn(PlanetTile) not found; "
                    + "the six landmarks keep their biomes' stones.");
                return;
            }
            try
            {
                new Harmony("mandrake.rm.environmentalhazards").Patch(target,
                    postfix: new HarmonyMethod(typeof(RM_GeoStones), nameof(Postfix_NaturalRockTypesIn)));
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] geological landmarks: patch failed; the landmarks keep their biomes' stones. " + e);
            }
        }

        public static FieldInfo SettingField(string name)
        {
            if (string.IsNullOrEmpty(name)) return null;
            FieldInfo f = typeof(RM_EnvironmentalHazardsSettings).GetField(name, BindingFlags.Public | BindingFlags.Static);
            return f != null && f.FieldType == typeof(bool) ? f : null;
        }

        static bool On(RM_GeoStonesExtension ext)
        {
            FieldInfo f = SettingField(ext.setting);
            return f == null || (bool)f.GetValue(null);
        }

        /// <summary>The decision: the stones of the first geological mutator on the tile whose landmark is switched on, or
        /// null (keep the biome's pick). A biome that forces its own rock (forceRockTypes, the Rust Cathedral) keeps it.</summary>
        public static List<ThingDef> StonesOf(IList<TileMutatorDef> mutators, bool biomeForcesRock, Func<RM_GeoStonesExtension, bool> on)
        {
            if (biomeForcesRock || mutators == null) return null;
            for (int i = 0; i < mutators.Count; i++)
            {
                RM_GeoStonesExtension ext = mutators[i]?.GetModExtension<RM_GeoStonesExtension>();
                if (ext == null || ext.stones == null || ext.stones.Count == 0) continue;
                if (on(ext)) return ext.stones;
            }
            return null;
        }

        public static void Postfix_NaturalRockTypesIn(PlanetTile tile, ref IEnumerable<ThingDef> __result)
        {
            if (!tile.Valid) return;
            Tile t = tile.Tile;
            if (t == null) return;
            List<ThingDef> stones = StonesOf(t.Mutators, t.PrimaryBiome?.forceRockTypes != null, On);
            if (stones != null) __result = stones;
        }
    }
}
