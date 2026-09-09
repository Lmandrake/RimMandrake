using System;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.Inhabited
{
    // INHABITED_INJECTIONS_DECOUPLE_1 / design/CHRONICLE_EVENT_SPINE.md soft-hook
    // law: GenStep_ComposeSettlementDistrict's district-template feature calls
    // into StructureInjections' RimplacePlan.Parse / GenStep_RimplacePlan.ApplyPlan
    // -- a functional library call with a return value, not a fire-and-forget
    // notification, so the static-event Subscribe/Raise pattern
    // CHRONICLE_NINEFOLD_DECOUPLE_1 used for Aftermath->Ninefold does not
    // transfer (see that item's own "Shape difference" note). Bound here via
    // AccessTools.TypeByName + MethodInfo.Invoke instead: no
    // <modDependencies>, no hard csproj <Reference>, no compile-time `using
    // RimMandrake.StructureInjections;` anywhere in Inhabited. If
    // mandrake.rm.injections is not loaded, <see cref="Available"/> is false
    // and the caller's existing "no template wired" fallback path handles it
    // -- the feature no-ops cleanly rather than crashing.
    [StaticConstructorOnStartup]
    internal static class StructureInjectionsBridge
    {
        private static readonly MethodInfo ParseMethod;
        private static readonly MethodInfo ApplyPlanMethod;
        private static readonly FieldInfo HasFootprintField;
        private static readonly FieldInfo FootprintXField;
        private static readonly FieldInfo FootprintZField;
        private static readonly FieldInfo FootprintWField;
        private static readonly FieldInfo FootprintHField;

        internal static bool Available { get; }

        static StructureInjectionsBridge()
        {
            Type planType = AccessTools.TypeByName("RimMandrake.StructureInjections.RimplacePlan");
            Type genStepType = AccessTools.TypeByName("RimMandrake.StructureInjections.GenStep_RimplacePlan");
            if (planType == null || genStepType == null)
            {
                return; // StructureInjections not loaded -- district templates stay OFF.
            }

            ParseMethod = AccessTools.Method(planType, "Parse", new[] { typeof(string) });
            ApplyPlanMethod = AccessTools.Method(genStepType, "ApplyPlan",
                new[] { typeof(Map), planType, typeof(int), typeof(int), typeof(string) });
            HasFootprintField = AccessTools.Field(planType, "HasFootprint");
            FootprintXField = AccessTools.Field(planType, "FootprintX");
            FootprintZField = AccessTools.Field(planType, "FootprintZ");
            FootprintWField = AccessTools.Field(planType, "FootprintW");
            FootprintHField = AccessTools.Field(planType, "FootprintH");

            Available = ParseMethod != null && ApplyPlanMethod != null && HasFootprintField != null
                && FootprintXField != null && FootprintZField != null && FootprintWField != null
                && FootprintHField != null;

            if (!Available)
            {
                Log.Warning("[RimMandrake.Inhabited] found mandrake.rm.injections but " +
                    "RimplacePlan/GenStep_RimplacePlan no longer match the expected shape -- " +
                    "district templates are OFF.");
            }
        }

        // Boxed RimplacePlan, or throws (callers already wrap this call in
        // their own try/catch, matching the pre-decouple direct-call
        // behaviour). TargetInvocationException is unwrapped so a caller's
        // Log.Error(ex) still shows the real parse failure, not the
        // reflection plumbing around it.
        internal static object Parse(string path)
        {
            try
            {
                return ParseMethod.Invoke(null, new object[] { path });
            }
            catch (TargetInvocationException tie) when (tie.InnerException != null)
            {
                throw tie.InnerException;
            }
        }

        internal static bool HasFootprint(object plan) => (bool)HasFootprintField.GetValue(plan);
        internal static int FootprintX(object plan) => (int)FootprintXField.GetValue(plan);
        internal static int FootprintZ(object plan) => (int)FootprintZField.GetValue(plan);
        internal static int FootprintW(object plan) => (int)FootprintWField.GetValue(plan);
        internal static int FootprintH(object plan) => (int)FootprintHField.GetValue(plan);

        internal static void ApplyPlan(Map map, object plan, int dx, int dz, string sourceLabel)
        {
            try
            {
                ApplyPlanMethod.Invoke(null, new object[] { map, plan, dx, dz, sourceLabel });
            }
            catch (TargetInvocationException tie) when (tie.InnerException != null)
            {
                throw tie.InnerException;
            }
        }
    }
}
