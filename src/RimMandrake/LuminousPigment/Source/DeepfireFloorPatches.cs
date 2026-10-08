using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_FLOOR_PAINT_1, spec §3.5 floor bullets + §3.6. Every target
    // below was read in the decompiled 1.6 source via RimSage before this
    // was written (signatures quoted in each class comment).

    // Verse/TerrainGrid.cs: public void SetTerrainColor(IntVec3 c, ColorDef color)
    // writes colorGrid then calls DoTerrainChangedEffects(c, same, same).
    // Recolour -> relight; a null ColorDef (vanilla "remove paint") keeps the
    // coats and the glow falls back to the floor def's own colour.
    [HarmonyPatch(typeof(TerrainGrid), nameof(TerrainGrid.SetTerrainColor))]
    public static class Patch_TerrainGrid_SetTerrainColor
    {
        public static void Postfix(IntVec3 c, Map ___map)
        {
            MapComponent_DeepfireLights.Get(___map)?.Notify_FloorColorChanged(c);
        }
    }

    // Verse/TerrainGrid.cs: private void DoTerrainChangedEffects(IntVec3 c,
    // TerrainDef oldTerr, TerrainDef newTerr, TerrainDef oldFoundation = null)
    // -- the one funnel SetTerrain / RemoveTopLayer / SetFoundation /
    // RemoveFoundation / SetTempTerrain / RemoveTempTerrain all end in.
    // Floor removed or replaced -> coats zeroed, no refund. A same-def call
    // (SetTerrainColor's own) is a recolour, handled above. A temporary
    // terrain landing on or lifting off a floor does not remove the floor
    // (TopTerrainAt is unchanged unless the temp def destroysFloors), so the
    // rule is "the top floor is no longer coatable, or its def changed".
    [HarmonyPatch(typeof(TerrainGrid), "DoTerrainChangedEffects")]
    public static class Patch_TerrainGrid_DoTerrainChangedEffects
    {
        public static void Postfix(IntVec3 c, TerrainDef oldTerr, TerrainDef newTerr, Map ___map)
        {
            if (oldTerr == newTerr) return;
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(___map);
            if (mc == null || mc.FloorCoatsAt(c) <= 0) return;

            bool tempOnly = (oldTerr != null && oldTerr.temporary) || (newTerr != null && newTerr.temporary);
            if (tempOnly && MapComponent_DeepfireLights.IsCoatableFloor(___map, c)) return;

            mc.ClearFloorCoats(c);
        }
    }

    // RimWorld/BeautyUtility.cs: public static float CellBeauty(IntVec3 c,
    // Map map, HashSet<Thing> countedThings = null) -- a real ~40-line method
    // with loops, not an inlining candidate, so it is postfixed directly and
    // the spec's AverageBeautyPerceptible fallback is not needed. Vanilla
    // returns ONLY a full-fillage thing's beauty (walls) and skips terrain
    // entirely on such a cell; the bonus follows the terrain, so it is skipped
    // there too. Coated-or-not, never per coat (spec §3.5).
    [HarmonyPatch(typeof(BeautyUtility), nameof(BeautyUtility.CellBeauty))]
    public static class Patch_BeautyUtility_CellBeauty
    {
        public static void Postfix(IntVec3 c, Map map, ref float __result)
        {
            if (map == null) return;
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(map);
            if (mc == null || mc.CoatedFloorCellCount == 0 || mc.FloorCoatsAt(c) <= 0) return;

            Building edifice = c.GetEdifice(map);
            if (edifice != null && edifice.def.Fillage == FillCategory.Full) return;

            __result += LuminousPigmentSettings.floorBeautyPerCell;
        }
    }

    // RM_RoomStatPart_DeepfireFloor (spec §3.5 "per room").
    // RimWorld/RoomStatWorker_Beauty.cs: public override float GetScore(Room room)
    // -- sums CellBeauty over room.Cells (plus adjacent things' cells) and
    // divides by CellCountCurve (0->20, 40->40). The per-cell bonus above is
    // therefore diluted by that divisor like any floor beauty; the room line
    // is added AFTER it, undivided: +FloorRoomBonusPer10 per 10 coated floor
    // cells inside the room, capped at FloorRoomBonusCap.
    [HarmonyPatch(typeof(RoomStatWorker_Beauty), nameof(RoomStatWorker_Beauty.GetScore))]
    public static class RM_RoomStatPart_DeepfireFloor
    {
        public static void Postfix(Room room, ref float __result)
        {
            float bonus = BonusFor(room);
            if (bonus > 0f) __result += bonus;
        }

        public static float BonusFor(Room room)
        {
            if (room?.Map == null) return 0f;
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(room.Map);
            if (mc == null || mc.CoatedFloorCellCount == 0) return 0f;
            int coated = mc.CountCoatedFloorCells(room.Cells);
            return RM_DeepfireRules.FloorRoomBonus(LuminousPigmentSettings.floorRoomBonusPer10, LuminousPigmentSettings.floorRoomBonusCap, coated);
        }
    }
}
