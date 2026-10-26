using System;
using HarmonyLib;
using RimMandrake.CreatureBehaviors;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // FOOTPRINT_TRACK_GRID_1 item 5/7, the Stillsand's eraser: "each biome brings its own eraser ... the
    // Stillsand's dunes engine (a cell whose sand depth changes past a threshold clears)". The Warscar's
    // eraser is the Settling's downwind sweep (Scarlands RM_Settling.cs); this is the other half.
    //
    // Hook: every Verse.SandGrid depth writer (RM_DuneTrackKernel.SandWriters): SetDepth, which the
    // MovingDunes engine writes every cell move through (MapComponent_DuneField.SetDepthHysteretic), and
    // AddDepth, which weather writes through (sand piling under a sandy weather, wearing away otherwise;
    // DUNETRACK_ERASE_WIDEN_WEATHER_SAND). A prefix keeps the old depth; the postfix clears the track-grid
    // print on that cell once the sand moved over it adds up to ChangeThreshold on an RM_Stillsand map. Any
    // sand that moved buries prints, whoever moved it.
    // ClearCell is safe during map load (the grid skips a section that is not built yet).
    // Setting: duneErasesTracks (off = prints stay until the grid's cap evicts them, the old behaviour).
    // ════════════════════════════════════════════════════════════════════
    public static class RM_DuneTrackEraserSettings
    {
        public static bool duneErasesTracks = true;

        public static void Expose()
        {
            Scribe_Values.Look(ref duneErasesTracks, "duneErasesTracks", true);
        }

    }

    [StaticConstructorOnStartup]
    public static class RM_DuneTrackEraser
    {
        public const float ChangeThreshold = RM_DuneTrackKernel.ChangeThreshold;

        // Resolved inside the guarded static constructor, so a renamed field logs our own
        // diagnostic instead of failing type initialisation.
        private static AccessTools.FieldRef<SandGrid, Map> MapRef;

        /// <summary>Session counter for the bridge (jawa/mod_settings_field list / static read). Never saved.</summary>
        public static int Erased;

        static RM_DuneTrackEraser()
        {
            const string rule = "[RimMandrake.Stillsand] dune track eraser: ";
            try
            {
                MapRef = AccessTools.FieldRefAccess<SandGrid, Map>("map");
            }
            catch (Exception e)
            {
                Log.Error(rule + "SandGrid.map NOT FOUND, moving sand will not bury tracks: " + e.Message);
                return;
            }
            var harmony = new Harmony("mandrake.rm.stillsand.dunetrackeraser");
            // Each writer on its own: one renamed method costs its own sand source, not the other's.
            foreach (string writer in RM_DuneTrackKernel.SandWriters)
            {
                try
                {
                    var target = AccessTools.Method(typeof(SandGrid), writer);
                    if (target == null)
                    {
                        Log.Error(rule + "SandGrid." + writer + " NOT FOUND, sand it writes will not bury tracks.");
                        continue;
                    }
                    harmony.Patch(target,
                        prefix: new HarmonyMethod(typeof(RM_DuneTrackEraser), nameof(Prefix)),
                        postfix: new HarmonyMethod(typeof(RM_DuneTrackEraser), nameof(Postfix)));
                }
                catch (Exception e)
                {
                    Log.Error(rule + "patch of SandGrid." + writer + " FAILED, sand it writes will not bury tracks: " + e.Message);
                }
            }
        }

        public static void Prefix(SandGrid __instance, IntVec3 c, out float __state)
        {
            __state = __instance.GetDepth(c);
        }

        // DUNE_TRACK_ERASE_ACCUMULATE_1: sand moved over a printed cell since its print, per cell (RM_SandMoveTally in
        // Kernel/RM_DuneTrackKernel.cs). A dune engine stepping in slabs smaller than ChangeThreshold, or weather adding
        // 0.023..0.046 a pass, adds up instead of never erasing.
        // PROVISIONAL (auto-decided 2026-10-09, DUNE_TRACK_ERASE_ACCUMULATE_1): session-only (not saved); a reload
        // restarts a part-buried print's count.
        private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<SandGrid, RM_SandMoveTally>
            moved = new System.Runtime.CompilerServices.ConditionalWeakTable<SandGrid, RM_SandMoveTally>();

        public static void Postfix(SandGrid __instance, IntVec3 c, float __state)
        {
            if (!RM_DuneTrackEraserSettings.duneErasesTracks) return;
            float delta = Mathf.Abs(__instance.GetDepth(c) - __state);
            if (delta <= 0f) return;
            Map map = MapRef != null ? MapRef(__instance) : null;
            if (map == null || map.Biome == null || map.Biome.defName != "RM_Stillsand") return;
            RM_MapComponent_TrackGrid grid = RM_MapComponent_TrackGrid.For(map);
            if (grid == null) return;
            bool buried = moved.GetOrCreateValue(__instance)
                .Note(map.cellIndices.CellToIndex(c), grid.TryGetPrint(c, out _), delta);
            if (buried && grid.ClearCell(c)) Erased++;
        }

        /// <summary>
        /// Bridge proof (jawa/static_call): on `map`, lay a print on a sand cell via the grid's own
        /// RecordPrint, then move that cell's sand by `delta` through SandGrid.SetDepth. Returns
        /// "printed=<bool> erased=<bool>" (erased = the print is gone afterwards).
        /// </summary>
        public static string ProofErase(Map map, float delta)
        {
            if (map == null) return "REFUSED: no map";
            RM_MapComponent_TrackGrid grid = RM_MapComponent_TrackGrid.For(map);
            if (grid == null) return "REFUSED: no track grid";
            if (map.sandGrid == null) return "REFUSED: no sand grid";
            Pawn walker = map.mapPawns.FreeColonistsSpawned.FirstOrFallback();
            if (walker == null) return "REFUSED: no colonist to print with";
            RM_TrackSurfaceExtension surface = null;
            IntVec3 cell = IntVec3.Invalid;
            foreach (IntVec3 c in map.AllCells)
            {
                surface = c.GetTerrain(map).GetModExtension<RM_TrackSurfaceExtension>();
                if (surface != null && c.Standable(map)) { cell = c; break; }
            }
            if (!cell.IsValid) return "REFUSED: no track surface cell";
            bool printed = grid.RecordPrint(cell, walker, surface);
            float d = map.sandGrid.GetDepth(cell);
            map.sandGrid.SetDepth(cell, Mathf.Clamp01(d + (d + delta > 1f ? -delta : delta)));
            bool erased = !grid.TryGetPrint(cell, out _);
            return "printed=" + printed + " erased=" + erased;
        }

        /// <summary>
        /// Bridge proof of the weather path (jawa/static_call, DUNETRACK_ERASE_WIDEN_WEATHER_SAND): lay a print as
        /// ProofErase does, then write that cell's sand through SandGrid.AddDepth, the weather writer, in steps of
        /// `step` (piling up, or wearing down when the cell is too full to pile) until the print is gone or 20 steps ran. Returns
        /// "printed=<bool> erased=<bool> steps=<n>"; a step of 0.03 buries it on step 3 (0.09 >= ChangeThreshold).
        /// </summary>
        public static string ProofEraseByWeather(Map map, float step)
        {
            if (map == null) return "REFUSED: no map";
            if (!(step > 0f) || step > 0.25f) return "REFUSED: step must be in (0, 0.25]";
            RM_MapComponent_TrackGrid grid = RM_MapComponent_TrackGrid.For(map);
            if (grid == null) return "REFUSED: no track grid";
            if (map.sandGrid == null) return "REFUSED: no sand grid";
            Pawn walker = map.mapPawns.FreeColonistsSpawned.FirstOrFallback();
            if (walker == null) return "REFUSED: no colonist to print with";
            RM_TrackSurfaceExtension surface = null;
            IntVec3 cell = IntVec3.Invalid;
            foreach (IntVec3 c in map.AllCells)
            {
                surface = c.GetTerrain(map).GetModExtension<RM_TrackSurfaceExtension>();
                if (surface != null && c.Standable(map)) { cell = c; break; }
            }
            if (!cell.IsValid) return "REFUSED: no track surface cell";
            bool printed = grid.RecordPrint(cell, walker, surface);
            // Room to pile threshold + one step, else wear down: with step <= 0.25 either way has the room.
            float sign = map.sandGrid.GetDepth(cell) + ChangeThreshold + step > 1f ? -1f : 1f;
            int steps = 0;
            while (steps < 20 && grid.TryGetPrint(cell, out _))
            {
                map.sandGrid.AddDepth(cell, sign * step);
                steps++;
            }
            bool erased = !grid.TryGetPrint(cell, out _);
            return "printed=" + printed + " erased=" + erased + " steps=" + steps;
        }
    }
}
