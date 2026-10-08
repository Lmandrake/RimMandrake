using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_MECHANICS_BUILD_1 part 2 — the Lean (v1).
    //
    // Each map whose biome carries RM_LeanExtension locks one wind heading the
    // first time it is asked for, and keeps it for the life of the map
    // (Scribed on RM_MapComponent_Lean). v1 scope, per the item: two local
    // patches, no hunting-AI rewrite.
    //
    //   Scent  JobGiver_AnimalFlee.TryGiveJob postfix. Vanilla wild animals
    //          flee only fire and alwaysFlee things (RimSage, decompiled
    //          JobGiver_AnimalFlee); here a wild non-predator also bolts from a
    //          humanlike standing UPWIND of it within scent range — its scent
    //          is carried down onto the animal. Approach from downwind and the
    //          prey never knows.
    //   Fire   Fire.TrySpread prefix. Part of the time the spread picks only
    //          among the adjacent cells that lie downwind, then runs vanilla's
    //          own ChanceToStartFireIn / TryStartFireIn; otherwise vanilla's
    //          own omnidirectional roll runs untouched. Net: fire races
    //          downwind and creeps upwind.
    //
    // Not in v1: windbreak calm wakes (microcells for the ripple / fog harvest,
    // neither of which exists yet) and predators hunting by scent.
    // ════════════════════════════════════════════════════════════════════
    public class RM_LeanExtension : DefModExtension
    {
    }

    public class RM_MapComponent_Lean : MapComponent
    {
        private float headingDegrees = -1f;
        private bool? applies;
        private Vector2 cachedDir;

        public RM_MapComponent_Lean(Map map) : base(map)
        {
        }

        public bool Applies
        {
            get
            {
                if (!applies.HasValue)
                {
                    applies = map.Biome?.GetModExtension<RM_LeanExtension>() != null;
                }
                return applies.Value;
            }
        }

        // Unit vector the wind blows TOWARD, in map x/z.
        public Vector2 Downwind
        {
            get
            {
                if (headingDegrees < 0f)
                {
                    headingDegrees = RM_LeanKernel.LockHeading(headingDegrees, Rand.Range(0f, 360f));
                    cachedDir = Vector2.zero;
                }
                if (cachedDir == Vector2.zero)
                {
                    RM_LeanKernel.Direction(headingDegrees, out float dirX, out float dirZ);
                    cachedDir = new Vector2(dirX, dirZ);
                }
                return cachedDir;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref headingDegrees, "rmLeanHeadingDegrees", -1f);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                cachedDir = Vector2.zero;
            }
        }

        public static RM_MapComponent_Lean For(Map map)
        {
            if (map == null || !RM_WindCalendar.On(RM_LeaningScrubSettings.leanEnabled))
            {
                return null;
            }
            RM_MapComponent_Lean lean = map.GetComponent<RM_MapComponent_Lean>();
            return lean != null && lean.Applies ? lean : null;
        }

        // Cosine between "from → to" and the downwind heading: 1 = straight downwind.
        public float Alignment(IntVec3 from, IntVec3 to)
        {
            Vector2 dir = Downwind;
            return RM_LeanKernel.Alignment(to.x - from.x, to.z - from.z, dir.x, dir.y);
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_TheLeanPatches
    {
        private const int FleeDistance = 24;

        static RM_TheLeanPatches()
        {
            Harmony harmony = new Harmony("mandrake.rm.leaningscrub");
            Patch(harmony, "lean-scent", AccessTools.Method(typeof(JobGiver_AnimalFlee), "TryGiveJob"),
                null, nameof(AnimalFlee_Postfix));
            Patch(harmony, "lean-fire", AccessTools.Method(typeof(Fire), "TrySpread"),
                nameof(TrySpread_Prefix), null);
        }

        private static void Patch(Harmony harmony, string rule, System.Reflection.MethodBase target, string prefix, string postfix)
        {
            if (target == null)
            {
                Log.Error("[RM LeaningScrub] " + rule + ": target method not found — rule NOT armed.");
                return;
            }
            try
            {
                harmony.Patch(target,
                    prefix: prefix == null ? null : new HarmonyMethod(typeof(RM_TheLeanPatches), prefix),
                    postfix: postfix == null ? null : new HarmonyMethod(typeof(RM_TheLeanPatches), postfix));
            }
            catch (Exception e)
            {
                Log.Error("[RM LeaningScrub] " + rule + ": patch failed, rule NOT armed. " + e);
            }
        }

        public static void AnimalFlee_Postfix(Pawn pawn, ref Job __result)
        {
            if (__result != null || pawn == null || pawn.Faction != null || !pawn.RaceProps.Animal
                || pawn.RaceProps.predator || pawn.Downed || !pawn.Spawned
                || !RM_LeaningScrubSettings.leanScentEnabled)
            {
                return;
            }
            RM_MapComponent_Lean lean = RM_MapComponent_Lean.For(pawn.Map);
            if (lean == null)
            {
                return;
            }
            float range = RM_LeaningScrubSettings.leanScentRange;
            IReadOnlyList<Pawn> people = pawn.Map.mapPawns.AllHumanlikeSpawned;
            int n = people.Count;
            int[] dx = new int[n], dz = new int[n];
            bool[] gone = new bool[n];
            for (int i = 0; i < n; i++)
            {
                Pawn h = people[i];
                // Scent runs from the person toward the animal along the wind.
                dx[i] = pawn.Position.x - h.Position.x;
                dz[i] = pawn.Position.z - h.Position.z;
                gone[i] = h.Dead || h.Downed;
            }
            Vector2 wind = lean.Downwind;
            Job found = null;
            RM_LeanKernel.FirstScentThreat(n, dx, dz, gone, range, wind.x, wind.y, i =>
            {
                Job flee = FleeUtility.FleeJob(pawn, people[i], FleeDistance);
                if (flee == null)
                {
                    return false;
                }
                found = flee;
                return true;
            });
            if (found != null)
            {
                __result = found;
            }
        }

        public static bool TrySpread_Prefix(Fire __instance)
        {
            if (!RM_LeaningScrubSettings.leanFireEnabled)
            {
                return true;
            }
            Map map = __instance.Map;
            RM_MapComponent_Lean lean = RM_MapComponent_Lean.For(map);
            if (lean == null)
            {
                return true;
            }
            IntVec3 pos = __instance.Position;
            Vector2 wind = lean.Downwind;
            int pick = RM_LeanKernel.FireSpreadPick(true, RM_LeaningScrubSettings.leanFireBias, Rand.Value, wind.x, wind.y, Rand.Value);
            if (pick < 0)
            {
                return true;
            }
            IntVec3 target = new IntVec3(pos.x + RM_LeanKernel.NeighbourDx[pick], 0, pos.z + RM_LeanKernel.NeighbourDz[pick]);
            if (target.InBounds(map) && Rand.Chance(FireUtility.ChanceToStartFireIn(target, map)))
            {
                FireUtility.TryStartFireIn(target, map, 0.1f, __instance.instigator);
            }
            return false;
        }
    }
}
