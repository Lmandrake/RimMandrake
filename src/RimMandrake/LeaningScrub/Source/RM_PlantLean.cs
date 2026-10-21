using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // SCRUB_WIND_BUILD_LEAN_ON_PURPOSE part 1 — the visible lean (owner card 2026-10-20, biome_bars_sitting §5.1:
    // "Leaning Scrub maps stop mirroring plants at random and face them with the map's wind heading").
    //
    // Vanilla 1.6 Plant.Print (RimSage, decompiled) mirrors each plant mesh with `bool flipUv = Rand.Bool;` under a
    // Rand state seeded from the cell. One transpiler appends a call after that single Rand.Bool: the coin is still
    // consumed (so the seeded stream, and the Graphic_Random variant pick right after it, are unchanged) and on a
    // leaning map a plant listed in RM_LeanExtension.leanPlants gets RM_LeanKernel.FaceFlip instead of the coin.
    //
    // Cost per mesh (plants print in bulk): three static bool reads, a reference compare against the cached map, an
    // array index by ThingDef.index, and for a Graphic_Random whose variants include a west-leaning one a Rand
    // push/peek/pop plus one dictionary hit. No allocation after the first print of each map and graphic.
    //
    // Variant art leans differently (measured: RM_Fuzz_e leans west, RM_Fuzz_d east), so a flip alone would leave the
    // map mixed. The variant vanilla is about to pick is peeked (Rand.PushState / Range / PopState restores the state
    // exactly) and its own lean comes from RM_LeanExtension.westLeaningTextures.
    //
    // VERIFY BY STATE READ: RM_PlantLeanProof.ProofLean (validation.py, windlean chain). The look itself is the owner's.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_PlantLean
    {
        // Proof counters (int increments, no allocation). Reset whenever the cached map changes.
        public static int SitesPatched;
        public static int FacedEast;
        public static int FacedWest;
        public static int RolledOnLeanMap;

        private static Map cachedMap;
        private static RM_LeanExtension cachedExt;
        private static RM_LeanExtension lastExt;
        private static bool cachedWindWest;
        private static readonly Dictionary<Graphic, bool[]> westByGraphic = new Dictionary<Graphic, bool[]>(new RefEq());
        private static readonly bool[] NoneWest = new bool[0];

        private sealed class RefEq : IEqualityComparer<Graphic>
        {
            public bool Equals(Graphic a, Graphic b) { return ReferenceEquals(a, b); }
            public int GetHashCode(Graphic g) { return RuntimeHelpers.GetHashCode(g); }
        }

        static RM_PlantLean()
        {
            MethodInfo print = AccessTools.Method(typeof(Plant), nameof(Plant.Print));
            if (print == null)
            {
                Log.Error("[RM LeaningScrub] lean-plants: Plant.Print not found — rule NOT armed.");
                return;
            }
            try
            {
                new Harmony("mandrake.rm.leaningscrub").Patch(print,
                    transpiler: new HarmonyMethod(typeof(RM_PlantLean), nameof(Print_Transpiler)));
            }
            catch (System.Exception e)
            {
                Log.Error("[RM LeaningScrub] lean-plants: patch failed, rule NOT armed. " + e);
            }
            if (SitesPatched != 1)
            {
                Log.Error("[RM LeaningScrub] lean-plants: expected exactly one Rand.Bool in Plant.Print, patched "
                    + SitesPatched + " — the lean may be wrong or absent.");
            }
        }

        public static IEnumerable<CodeInstruction> Print_Transpiler(IEnumerable<CodeInstruction> instructions)
        {
            MethodInfo getBool = AccessTools.PropertyGetter(typeof(Rand), nameof(Rand.Bool));
            MethodInfo face = AccessTools.Method(typeof(RM_PlantLean), nameof(Face));
            SitesPatched = 0;
            foreach (CodeInstruction ci in instructions)
            {
                yield return ci;
                if (ci.Calls(getBool))
                {
                    yield return new CodeInstruction(OpCodes.Ldarg_0);
                    yield return new CodeInstruction(OpCodes.Call, face);
                    SitesPatched++;
                }
            }
        }

        // rolled = vanilla's coin. Returns the flip to print.
        public static bool Face(bool rolled, Plant plant)
        {
            if (!RM_LeaningScrubSettings.leanPlantsEnabled || !RM_LeaningScrubSettings.leanEnabled
                || !RM_LeaningScrubSettings.modEnabled)
            {
                return rolled;
            }
            Map map = plant.Map;
            if (map == null)
            {
                return rolled;
            }
            if (!ReferenceEquals(map, cachedMap))
            {
                Refresh(map);
            }
            if (cachedExt == null)
            {
                return rolled;
            }
            if (!cachedExt.Leans(plant.def))
            {
                RolledOnLeanMap++;
                return rolled;
            }
            bool artWest = ArtLeansWest(plant);
            bool flip = RM_LeanKernel.FaceFlip(cachedWindWest, artWest);
            if (RM_LeanKernel.VisibleWest(artWest, flip))
            {
                FacedWest++;
            }
            else
            {
                FacedEast++;
            }
            return flip;
        }

        private static void Refresh(Map map)
        {
            cachedMap = map;
            cachedExt = null;
            FacedEast = FacedWest = RolledOnLeanMap = 0;
            RM_MapComponent_Lean lean = RM_MapComponent_Lean.For(map);
            if (lean == null)
            {
                return;
            }
            // The heading may lock here, inside Print's seeded Rand state: push/pop so the plant's own stream is untouched.
            Rand.PushState();
            Vector2 down = lean.Downwind;
            Rand.PopState();
            cachedWindWest = RM_LeanKernel.WindLeansWest(down.x);
            RM_LeanExtension ext = map.Biome.GetModExtension<RM_LeanExtension>();
            if (!ReferenceEquals(ext, lastExt))
            {
                westByGraphic.Clear();   // the west list is the biome's: a graphic's flags are only valid for one list
                lastExt = ext;
            }
            cachedExt = ext;
        }

        // Forget the cached map (settings changed, proof hook). The next print re-reads it.
        public static void Invalidate()
        {
            cachedMap = null;
            cachedExt = null;
        }

        private static bool ArtLeansWest(Plant plant)
        {
            Graphic g = plant.Graphic;
            if (!westByGraphic.TryGetValue(g, out bool[] west))
            {
                west = BuildWest(g) ?? NoneWest;
                westByGraphic[g] = west;
            }
            if (west.Length == 0)
            {
                return false;
            }
            if (g is Graphic_Random r)
            {
                // Peek the variant Plant.Print picks next (its Rand.Range(0, count) right after the coin), state restored.
                Rand.PushState();
                int idx = Rand.Range(0, r.SubGraphicsCount);
                Rand.PopState();
                return idx < west.Length && west[idx];
            }
            return west[0];
        }

        private static bool[] BuildWest(Graphic g)
        {
            List<string> paths = new List<string>();
            if (g is Graphic_Random r)
            {
                for (int i = 0; i < r.SubGraphicsCount; i++)
                {
                    paths.Add(r.SubGraphicAtIndex(i).path);
                }
            }
            else
            {
                paths.Add(g.path);
            }
            return RM_LeanKernel.WestByVariant(paths, cachedExt.WestSet);
        }

        private static bool lastDrawnOn = true;

        // Settings written: when the effective lean switch changed, redraw the current maps so it shows at once.
        public static void RedrawMaps()
        {
            bool on = RM_LeaningScrubSettings.leanPlantsEnabled && RM_LeaningScrubSettings.leanEnabled
                && RM_LeaningScrubSettings.modEnabled;
            if (on == lastDrawnOn)
            {
                return;
            }
            lastDrawnOn = on;
            Invalidate();
            if (Current.ProgramState != ProgramState.Playing || Find.Maps == null)
            {
                return;
            }
            foreach (Map m in Find.Maps)
            {
                m.mapDrawer.RegenerateEverythingNow();
            }
        }
    }

    // jawa/static_call proof hook (validation.py, windlean chain). Forces a redraw of the current map, then reads the
    // counters Face() kept while every plant printed. "on": PASS when listed plants faced one way only, the way the map's
    // wind leans. "off": with leanPlantsEnabled false, PASS when no plant was faced.
    public static class RM_PlantLeanProof
    {
        public static string ProofLean(string mode)
        {
            Map map = Find.CurrentMap;
            if (map == null)
            {
                return "UNMEASURED no current map";
            }
            if (RM_PlantLean.SitesPatched != 1)
            {
                return "FAIL Plant.Print Rand.Bool sites patched=" + RM_PlantLean.SitesPatched + " (want 1)";
            }
            RM_MapComponent_Lean lean = RM_MapComponent_Lean.For(map);
            RM_LeanExtension ext = map.Biome?.GetModExtension<RM_LeanExtension>();
            if (lean == null || ext == null)
            {
                return "UNMEASURED map biome " + map.Biome?.defName + " does not lean (needs a Leaning Scrub map)";
            }
            bool was = RM_LeaningScrubSettings.leanPlantsEnabled;
            bool off = mode == "off";
            try
            {
                RM_LeaningScrubSettings.leanPlantsEnabled = !off;
                RM_PlantLean.Invalidate();
                map.mapDrawer.RegenerateEverythingNow();
                int east = RM_PlantLean.FacedEast, west = RM_PlantLean.FacedWest;
                bool windWest = RM_LeanKernel.WindLeansWest(lean.Downwind.x);
                string s = " east=" + east + " west=" + west + " rolled=" + RM_PlantLean.RolledOnLeanMap
                    + " windWest=" + windWest + " downwind=" + lean.Downwind.ToString("F2");
                if (off)
                {
                    return (east + west == 0 ? "PASS" : "FAIL faced with the toggle off") + s;
                }
                if (east + west == 0)
                {
                    return "UNMEASURED no listed lean plant printed on this map" + s;
                }
                if (east > 0 && west > 0)
                {
                    return "FAIL mixed lean" + s;
                }
                return ((west > 0) == windWest ? "PASS" : "FAIL plants face against the wind") + s;
            }
            finally
            {
                RM_LeaningScrubSettings.leanPlantsEnabled = was;
                RM_PlantLean.Invalidate();
                map.mapDrawer.RegenerateEverythingNow();
            }
        }
    }
}
