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
    // Hook: Verse.SandGrid.SetDepth, which the MovingDunes engine writes every cell move through
    // (MapComponent_DuneField.SetDepthHysteretic). A prefix keeps the old depth; the postfix clears the
    // track-grid print on that cell when the depth moved by at least ChangeThreshold on an RM_Stillsand
    // map. Vanilla writers of SetDepth are caught too, which is right: any sand that moved buries prints.
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
        public const float ChangeThreshold = 0.08f;

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
                var target = AccessTools.Method(typeof(SandGrid), "SetDepth");
                if (target == null)
                {
                    Log.Error(rule + "SandGrid.SetDepth NOT FOUND, moving sand will not bury tracks.");
                    return;
                }
                new Harmony("mandrake.rm.stillsand.dunetrackeraser").Patch(target,
                    prefix: new HarmonyMethod(typeof(RM_DuneTrackEraser), nameof(Prefix)),
                    postfix: new HarmonyMethod(typeof(RM_DuneTrackEraser), nameof(Postfix)));
            }
            catch (Exception e)
            {
                Log.Error(rule + "patch FAILED, moving sand will not bury tracks: " + e.Message);
            }
        }

        public static void Prefix(SandGrid __instance, IntVec3 c, out float __state)
        {
            __state = __instance.GetDepth(c);
        }

        // DUNE_TRACK_ERASE_ACCUMULATE_1: sand moved over a printed cell since its print, per cell. A dune engine
        // stepping in slabs smaller than ChangeThreshold used to never erase; now the steps add up. Starts counting
        // at the first move that finds a print on the cell (and resets when the cell has none), so sand that moved
        // BEFORE the print never counts against it.
        // PROVISIONAL (auto-decided 2026-10-09, DUNE_TRACK_ERASE_ACCUMULATE_1): session-only (not saved); a reload
        // restarts a part-buried print's count.
        private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<SandGrid, System.Collections.Generic.Dictionary<int, float>>
            moved = new System.Runtime.CompilerServices.ConditionalWeakTable<SandGrid, System.Collections.Generic.Dictionary<int, float>>();

        public static void Postfix(SandGrid __instance, IntVec3 c, float __state)
        {
            if (!RM_DuneTrackEraserSettings.duneErasesTracks) return;
            float delta = Mathf.Abs(__instance.GetDepth(c) - __state);
            if (delta <= 0f) return;
            Map map = MapRef != null ? MapRef(__instance) : null;
            if (map == null || map.Biome == null || map.Biome.defName != "RM_Stillsand") return;
            RM_MapComponent_TrackGrid grid = RM_MapComponent_TrackGrid.For(map);
            if (grid == null) return;
            var acc = moved.GetOrCreateValue(__instance);
            int idx = map.cellIndices.CellToIndex(c);
            if (!grid.TryGetPrint(c, out _))
            {
                acc.Remove(idx);
                return;
            }
            acc.TryGetValue(idx, out float sum);
            sum += delta;
            if (sum < ChangeThreshold)
            {
                acc[idx] = sum;
                return;
            }
            acc.Remove(idx);
            if (grid.ClearCell(c)) Erased++;
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
    }
}
