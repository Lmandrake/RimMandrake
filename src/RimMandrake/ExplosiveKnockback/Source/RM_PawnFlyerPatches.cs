using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    /// <summary>
    /// GPT #5 (confirmed in decompiled 1.6): PawnFlyer.TickInterval calls private CheckDestination() every 15 ticks
    /// and, when JumpUtility.ValidJumpTarget fails, moves destCell to ANY valid cell within 3.9 — across a wall,
    /// onto the far lip of a pit, out of a pit. Skipped for our def only; vanilla jumps and other mods' flyers
    /// are untouched.
    /// </summary>
    [HarmonyPatch(typeof(PawnFlyer), "CheckDestination")]
    public static class RM_Patch_PawnFlyer_KnockbackNoRedirect
    {
        public static bool Prefix(PawnFlyer __instance)
        {
            return __instance.def != RM_KnockbackDefOf.RM_PawnFlyer_Knockback;
        }
    }

    /// <summary>Our own landing check (GPT #7/#11): if the destination became unusable mid-flight (a wall built, a
    /// door closed, another pawn landed there), walk back along the travelled line toward the takeoff; if nothing
    /// is valid, land at the takeoff. Never across a wall.</summary>
    [HarmonyPatch(typeof(PawnFlyer), "RespawnPawn")]
    public static class RM_Patch_PawnFlyer_KnockbackLanding
    {
        private static readonly AccessTools.FieldRef<PawnFlyer, IntVec3> DestCell = AccessTools.FieldRefAccess<PawnFlyer, IntVec3>("destCell");
        private static readonly AccessTools.FieldRef<PawnFlyer, Vector3> StartVec = AccessTools.FieldRefAccess<PawnFlyer, Vector3>("startVec");

        public static void Prefix(PawnFlyer __instance, out Pawn __state)
        {
            __state = null;
            if (__instance.def != RM_KnockbackDefOf.RM_PawnFlyer_Knockback)
            {
                return;
            }
            Pawn p = __instance.FlyingPawn;
            Map map = __instance.Map;
            __state = p;
            if (p == null || map == null)
            {
                return;
            }
            IntVec3 dest = DestCell(__instance);
            IntVec3 start = StartVec(__instance).ToIntVec3();
            if (LandOk(map, p, dest))
            {
                return;
            }
            IntVec3 chosen = start;
            int n = Mathf.Max(Mathf.Abs(dest.x - start.x), Mathf.Abs(dest.z - start.z));
            for (int i = n - 1; i >= 1; i--)
            {
                var c = new IntVec3(start.x + Mathf.RoundToInt((dest.x - start.x) * i / (float)n), 0,
                    start.z + Mathf.RoundToInt((dest.z - start.z) * i / (float)n));
                if (LandOk(map, p, c))
                {
                    chosen = c;
                    break;
                }
            }
            if (!chosen.InBounds(map) || !chosen.Standable(map))
            {
                chosen = CellFinder.StandableCellNear(start, map, 3f);
            }
            RM_KnockbackJournal.Add("redirect", 0, p, "from", dest, "to", chosen);
            DestCell(__instance) = chosen;
        }

        public static void Postfix(Pawn __state)
        {
            if (__state != null)
            {
                RM_KnockbackJournal.Add("land", 0, __state, "at", __state.Spawned ? __state.Position : IntVec3.Invalid,
                    "spawned", __state.Spawned, "dead", __state.Dead, "downed", __state.Downed,
                    "inPit", __state.Spawned && RM_KnockbackCompat.IsSuperdeep(__state.Map, __state.Position));
            }
        }

        private static bool LandOk(Map map, Pawn p, IntVec3 c)
        {
            if (!c.InBounds(map) || !c.Standable(map))
            {
                return false;
            }
            if (c.GetEdifice(map) is Building_Door door && !door.Open)
            {
                return false;
            }
            foreach (Thing t in c.GetThingList(map))
            {
                if (t is Pawn o && o != p)
                {
                    return false;
                }
            }
            return true;
        }
    }
}
