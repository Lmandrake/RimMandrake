using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §4.1: "any worn apparel / equipped weapon whose CompDeepfire.coats
    // > 0, and any RM_StatusGoodExtension-tagged def (the hook for later
    // goods; Deepfire is detected by comp, not by extension)." A generic,
    // reusable "purple engine": CompDeepfire contributes its live coat count
    // (DEEPFIRE_STATUS_THOUGHTS_1); any other good contributes its tagged
    // statusLevel.
    public class StatusGoodExtension : DefModExtension
    {
        // 0..3, analogous to Deepfire's coat count. A def with this
        // extension always contributes this fixed level; a Deepfire-coated
        // thing contributes its live coat count instead.
        public int statusLevel = 1;
    }

    // DEEPFIRE_STATUS_THOUGHTS_1 (spec §4.1 room thoughts, §7 key
    // goodwillPerImpressedVisit). Settings wiring is DEEPFIRE_MOD_SETTINGS_1's.
    public static class DeepfireStatusDefaults
    {
        public const int WallFloorCellsPerPoint = 10;    // "walls/floors count 1 per 10 cells"
        public const int BedroomScoreLow = 3;            // RM_DeepfireBedroom stage 0 (+4)
        public const int BedroomScoreHigh = 8;           // RM_DeepfireBedroom stage 1 (+6)
        public const int ImpressRoomScore = 8;           // RM_ImpressedByDeepfire: any public room >= this
        public const int GoodwillPerImpressedVisit = 2;
        public const int ImpressCheckInterval = 2500;    // one in-game hour
        public const int RoomScoreCacheTicks = 250;      // situational thoughts re-ask often; rooms change rarely
    }

    public static class SumptuaryUtility
    {
        public static int DisplayScoreFor(Pawn pawn)
        {
            if (pawn == null) return 0;
            int score = 0;
            if (pawn.apparel != null)
            {
                foreach (Apparel a in pawn.apparel.WornApparel)
                {
                    score += GoodLevel(a);
                }
            }
            if (pawn.equipment?.Primary != null)
            {
                score += GoodLevel(pawn.equipment.Primary);
            }
            return UnityEngine.Mathf.Min(score, LuminousPigmentSettings.displayCap);
        }

        // Deepfire by comp first (spec §4.1), then the generic extension.
        public static int GoodLevel(Thing t)
        {
            if (t == null) return 0;
            CompDeepfire comp = t.TryGetComp<CompDeepfire>();
            if (comp != null && comp.coats > 0) return comp.coats;
            StatusGoodExtension ext = t.def.GetModExtension<StatusGoodExtension>();
            return ext?.statusLevel ?? 0;
        }

        // Spec §4.1: "A room's display score = Σ coats of Deepfire-coated
        // furniture in it (walls/floors count 1 per 10 cells)." Furniture =
        // any coated Building in or bordering the room that is not a wall
        // (each Thing counted once; Room.ContainedAndAdjacentThings is
        // de-duplicated, RimSage Verse/Room.cs). Walls and floor cells are
        // pooled and count 1 point per WallFloorCellsPerPoint coated cells.
        public static int RoomDisplayScore(Room room)
        {
            if (room == null || room.Map == null || room.PsychologicallyOutdoors) return 0;
            int furniture = 0, wallCells = 0;
            List<Thing> things = room.ContainedAndAdjacentThings;
            for (int i = 0; i < things.Count; i++)
            {
                Thing t = things[i];
                if (t.def.category != ThingCategory.Building) continue;
                CompDeepfire comp = t.TryGetComp<CompDeepfire>();
                if (comp == null || comp.coats <= 0) continue;
                if (t.def.IsWall) wallCells++;
                else furniture += comp.coats;
            }
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(room.Map);
            int floorCells = mc == null || mc.CoatedFloorCellCount == 0 ? 0 : mc.CountCoatedFloorCells(room.Cells);
            return furniture + (wallCells + floorCells) / DeepfireStatusDefaults.WallFloorCellsPerPoint;
        }

        // Royalty title seniority -> Ideology leader/moral-guide role ->
        // otherwise common (spec §4.1's rank judgement, cheapest first).
        public static bool IsTitled(Pawn pawn)
        {
            if (pawn?.royalty != null && pawn.royalty.AllTitlesInEffectForReading.Count > 0) return true;
            if (pawn?.Ideo != null && pawn.Ideo.GetRole(pawn) != null) return true;
            return false;
        }

        // Spec §4.1: "A colony with neither DLC has no titled pawns;
        // ranklessColoniesEnjoyIt (default on) then lets every pawn take the
        // wearer's pleasure." With the setting off and neither DLC active,
        // there is no "who else" for the engine's status comparison to mean
        // anything, so the wearer's own pleasure thought is suppressed too.
        public static bool RanklessColonyThoughtAllowed()
        {
            if (LuminousPigmentSettings.ranklessColoniesEnjoyIt) return true;
            return ModsConfig.RoyaltyActive || ModsConfig.IdeologyActive;
        }
    }
}
