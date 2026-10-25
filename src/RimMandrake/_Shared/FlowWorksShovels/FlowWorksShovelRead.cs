using System;
using System.Reflection;
using HarmonyLib;
using Verse;
using Verse.AI;

namespace RimMandrake.Shared
{
    // ════════════════════════════════════════════════════════════════════
    // SHOVELS_BUILD_NO_DIGGING_BARE_HANDED, read reflection-soft from FlowWorks (source-linked into each mod that shovels
    // without depending on FlowWorks: Pyrelands' sand, Moving Dunes' drift). Owner 2026-10-25 (Q2): "yes" -- sand and drift
    // shovelling need a shovel too. FlowWorks owns the rule (RM_Shovels: the setting, the shovel defs, machine labour, the
    // search); this file only calls RM_Shovels.Ready, RM_Shovels.FetchJobFor and reads RM_Shovels.NoShovelReason.
    //
    // FlowWorks is never a dependency: with it absent (or an older FlowWorks without RM_Shovels) Available is false, Ready is
    // always true and nobody needs a shovel.
    // ════════════════════════════════════════════════════════════════════
    public static class FlowWorksShovelRead
    {
        private static bool resolved;
        private static Func<Pawn, bool> ready;
        private static Func<Pawn, bool, Job> fetch;
        private static string reason = "Needs a shovel (none free on the map).";

        public static bool Available
        {
            get { Resolve(); return ready != null && fetch != null; }
        }

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            try
            {
                Type t = AccessTools.TypeByName("RimMandrake.FlowWorks.RM_Shovels");
                if (t == null) return;
                MethodInfo r = AccessTools.Method(t, "Ready", new[] { typeof(Pawn) });
                MethodInfo f = AccessTools.Method(t, "FetchJobFor", new[] { typeof(Pawn), typeof(bool) });
                if (r == null || f == null) return;
                ready = (Func<Pawn, bool>)Delegate.CreateDelegate(typeof(Func<Pawn, bool>), r);
                fetch = (Func<Pawn, bool, Job>)Delegate.CreateDelegate(typeof(Func<Pawn, bool, Job>), f);
                FieldInfo why = AccessTools.Field(t, "NoShovelReason");
                if (why?.GetValue(null) is string s) reason = s;
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake] FlowWorks shovel reflection failed; shovels not required here: " + e.Message);
                ready = null;
                fetch = null;
            }
        }

        /// <summary>May dig now: FlowWorks absent, the pawn needs no shovel, or has one in its pack.</summary>
        public static bool Ready(Pawn pawn)
        {
            Resolve();
            return ready == null || fetch == null || ready(pawn);
        }

        /// <summary>The job that puts the nearest free shovel in the pawn's pack, or null (none free, or FlowWorks absent).</summary>
        public static Job FetchJobFor(Pawn pawn, bool forced)
        {
            Resolve();
            return fetch == null ? null : fetch(pawn, forced);
        }

        /// <summary>The scanner gate: true when the pawn may be offered the cell (Ready, or a free shovel to fetch first).
        /// False sets the work tab's reason.</summary>
        public static bool CanWorkOrFetch(Pawn pawn, bool forced)
        {
            if (Ready(pawn)) return true;
            if (FetchJobFor(pawn, forced) != null) return true;
            JobFailReason.Is(reason);
            return false;
        }
    }
}
