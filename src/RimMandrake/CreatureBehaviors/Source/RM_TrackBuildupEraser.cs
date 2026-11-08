using System;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // FOOTPRINT_TRACK_GRID_1 — the eraser of a BUILDUP surface (a biome whose
    // sand-grid buildup takes prints: the Pyrelands' ash, 2026-11-08).
    //
    // Every other surface brings its own eraser from its biome (the Stillsand's
    // moving sand, the Warscar's downwind sweep). A buildup surface IS the sand
    // grid, so the print goes with the grid: when its cell thins below the
    // surface's minSandDepth (black rain washed it, a colonist cleared it, it
    // wore away) the print clears; and every write that moves the cell's sand
    // buries it on the odds, delta / buryDepth, so a print is gone after about
    // buryDepth of fresh fall, or of slow wear (about a day dry on the
    // Pyrelands). The biome sets both numbers in its XML; nothing here decides
    // them. Hooks both SandGrid writers, SetDepth (jobs, buildings, floors) and
    // AddDepth (weather), as the Stillsand's RM_DuneTrackEraser does.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_TrackBuildupEraser
    {
        private static AccessTools.FieldRef<SandGrid, Map> MapRef;

        /// <summary>Session counter for the bridge. Never saved.</summary>
        public static int Erased;

        static RM_TrackBuildupEraser()
        {
            const string rule = "[RM CreatureBehaviors] buildup track eraser: ";
            if (!ModsConfig.OdysseyActive) return;
            try
            {
                MapRef = AccessTools.FieldRefAccess<SandGrid, Map>("map");
            }
            catch (Exception e)
            {
                Log.Error(rule + "SandGrid.map NOT FOUND, prints in a biome's buildup will never clear: " + e.Message);
                return;
            }
            var harmony = new Harmony("mandrake.rm.creaturebehaviors.builduperaser");
            foreach (string writer in new[] { nameof(SandGrid.SetDepth), nameof(SandGrid.AddDepth) })
            {
                try
                {
                    harmony.Patch(AccessTools.Method(typeof(SandGrid), writer),
                        prefix: new HarmonyMethod(typeof(RM_TrackBuildupEraser), nameof(Prefix)),
                        postfix: new HarmonyMethod(typeof(RM_TrackBuildupEraser), nameof(Postfix)));
                }
                catch (Exception e)
                {
                    Log.Error(rule + "patch of SandGrid." + writer + " FAILED, prints in buildup it writes will not clear: " + e.Message);
                }
            }
        }

        public static void Prefix(SandGrid __instance, IntVec3 c, out float __state)
        {
            __state = __instance.GetDepth(c);
        }

        public static void Postfix(SandGrid __instance, IntVec3 c, float __state)
        {
            if (!RM_CreatureBehaviorsSettings.tracksEnabled) return;
            float now = __instance.GetDepth(c);
            float delta = Mathf.Abs(now - __state);
            if (delta <= 0f) return;
            Map map = MapRef != null ? MapRef(__instance) : null;
            RM_TrackSurfaceExtension surface = RM_TrackGridPatches.BuildupSurfaceOf(map);
            if (surface == null) return;
            RM_MapComponent_TrackGrid grid = RM_MapComponent_TrackGrid.For(map);
            if (grid == null || grid.Pool == null || !grid.TryGetPrint(c, out _)) return;
            if (now >= surface.minSandDepth && !Rand.Chance(delta / surface.buryDepth)) return;
            // A terrain's or a filth's own surface on this cell keeps its print: its own biome's eraser owns it.
            if (RM_TrackGridPatches.OwnSurfaceAt(c, map) != null) return;
            if (grid.ClearCell(c)) Erased++;
        }
    }
}
