// The process lists and the work speed of a level (DESIGN.md "What the game's files cannot give").
// Process lists: set at startup and whenever settings are applied, from the donor def as loaded, never from a copy. The factory
// mod adds the autoloom's, the machining bay's and the fish farm's processes in a prefix on DefGenerator.GenerateImpliedDefs_PreResolve
// (read from its 1.6 assembly), which runs before any static constructor, so Capture() sees the full donor lists.
// Work speed: PipeSystem's Process constructor divides a process's ticks by CompAdvancedResourceProcessor.GetNotInRoomRoleFactor
// (read from the live 1.6 PipeSystem.dll), so one postfix on it scales the process time of a Kludged or Refurbished machine.
// The same method also gates PipeSystem's "not in room role" inspect line, which dereferences def.building.workTableRoomRole.label
// without a null check; the postfix is suppressed while that line and the matching stat entry are built.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using PipeSystem;
using RimWorld;
using Verse;

namespace RimMandrake.WreckedMachines
{
    public static class RM_ProcessLists
    {
        private class Captured
        {
            public List<ProcessDef> donor = new List<ProcessDef>();
            public List<ProcessDef> kludgedAsLoaded = new List<ProcessDef>();
            public List<ProcessDef> kludgedExtras = new List<ProcessDef>();
            public List<ProcessDef> refurbishedExtras = new List<ProcessDef>();
        }

        private static readonly Dictionary<RM_MachineLineDef, Captured> captured = new Dictionary<RM_MachineLineDef, Captured>();

        /// <summary>Per thing id: the factor PipeSystem computed and the one our postfix returned, last time it ran.</summary>
        private static readonly Dictionary<int, KeyValuePair<float, float>> seen = new Dictionary<int, KeyValuePair<float, float>>();

        /// <summary>Above 0 while PipeSystem builds its "not in room role" inspect line or stat entry: the postfix then leaves the
        /// factor alone, so that line neither shows our ratio as a room penalty nor reaches the unguarded room-role label.</summary>
        public static int suppress;

        private static List<ProcessDef> ListOf(ThingDef d) => d?.GetCompProperties<CompProperties_AdvancedResourceProcessor>()?.processes;

        public static void Capture()
        {
            captured.Clear();
            foreach (RM_MachineLineDef l in RM_MachineLines.All)
            {
                List<ProcessDef> donor = ListOf(l.original);
                if (donor == null) continue;
                var c = new Captured { donor = donor.Where(p => p != null).Distinct().ToList() };
                List<ProcessDef> k = ListOf(l.kludged);
                if (k != null)
                {
                    c.kludgedAsLoaded = k.Where(p => p != null).Distinct().ToList();
                    c.kludgedExtras = c.kludgedAsLoaded.Where(p => !c.donor.Contains(p)).ToList();
                }
                List<ProcessDef> r = ListOf(l.refurbished);
                if (r != null) c.refurbishedExtras = r.Where(p => p != null && !c.donor.Contains(p)).Distinct().ToList();
                captured[l] = c;
            }
        }

        public static void Apply()
        {
            foreach (KeyValuePair<RM_MachineLineDef, Captured> e in captured)
            {
                RM_MachineLineDef l = e.Key;
                Captured c = e.Value;

                List<ProcessDef> r = ListOf(l.refurbished);
                if (r != null) Set(r, c.donor.Concat(c.refurbishedExtras));

                List<ProcessDef> k = ListOf(l.kludged);
                if (k == null) continue;
                List<ProcessDef> part = l.kludgedProcessDefs != null && l.kludgedProcessDefs.Count > 0
                    ? l.kludgedProcessDefs.ToList()
                    : l.kludgedProcessCount > 0 ? c.donor.Take(l.kludgedProcessCount).ToList()
                    : c.kludgedAsLoaded.Where(p => c.donor.Contains(p)).ToList();
                List<ProcessDef> want = part.Concat(c.kludgedExtras).Distinct().ToList();
                if (want.Count == 0 && c.donor.Count > 0) want.Add(c.donor[0]);
                Set(k, want);
            }
        }

        // In place: a comp that already holds the list keeps seeing the live one.
        private static void Set(List<ProcessDef> list, IEnumerable<ProcessDef> want)
        {
            List<ProcessDef> w = want.Where(p => p != null).Distinct().ToList();
            list.Clear();
            list.AddRange(w);
        }

        /// <summary>The defNames of the live Kludged and Refurbished process lists of a line.</summary>
        public static void Row(RM_MachineLineDef line, out List<string> kludged, out List<string> refurbished)
        {
            kludged = (ListOf(line?.kludged) ?? new List<ProcessDef>()).Where(p => p != null).Select(p => p.defName).ToList();
            refurbished = (ListOf(line?.refurbished) ?? new List<ProcessDef>()).Where(p => p != null).Select(p => p.defName).ToList();
        }

        /// <summary>The ratio our postfix applies to this def now, or 1: a Kludged or Refurbished level of a line that is on.</summary>
        public static float RatioOf(ThingDef def)
        {
            RM_MachineLineDef l = RM_MachineLines.LineOf(def, out int level);
            if (l == null || !RM_MachineLines.IsOn(l)) return 1f;
            if (level != RM_WreckedMachinesKernel.Kludged && level != RM_WreckedMachinesKernel.Refurbished) return 1f;
            return RM_WreckedMachinesKernel.RatioFor(level, WreckedMachinesSettings.Ladder);
        }

        /// <summary>The work speed applied to a machine against its Original: after over before, as last seen by the postfix;
        /// a machine it has not seen answers its level's ratio; anything not ours answers 1.</summary>
        public static float SpeedFactor(Thing t)
        {
            if (t == null) return 1f;
            if (seen.TryGetValue(t.thingIDNumber, out KeyValuePair<float, float> ba) && ba.Key > 0f && t.def != null
                && RM_MachineLines.LineOf(t.def, out _) != null)
                return ba.Value / ba.Key;
            return RatioOf(t.def);
        }

        public static void Record(Thing t, float before, float after)
        {
            if (t != null) seen[t.thingIDNumber] = new KeyValuePair<float, float>(before, after);
        }
    }

    [HarmonyLib.HarmonyPatch(typeof(CompAdvancedResourceProcessor), nameof(CompAdvancedResourceProcessor.GetNotInRoomRoleFactor))]
    [RimMandrake.Shared.PatchFeature("A Kludged or Refurbished factory machine works at its level's ratio of the original's speed")]
    public static class Patch_LevelWorkSpeed
    {
        public static void Postfix(ThingWithComps parent, ref float __result)
        {
            if (RM_ProcessLists.suppress > 0 || parent == null) return;
            float ratio = RM_ProcessLists.RatioOf(parent.def);
            float before = __result;
            if (ratio != 1f && ratio > 0f) __result = before * ratio;
            if (RM_MachineLines.LineOf(parent.def, out _) != null) RM_ProcessLists.Record(parent, before, __result);
        }
    }

    [HarmonyLib.HarmonyPatch(typeof(CompAdvancedResourceProcessor), nameof(CompAdvancedResourceProcessor.CompInspectStringExtra))]
    [RimMandrake.Shared.PatchFeature("A machine's work-speed ratio is not shown as a room penalty in its inspect text")]
    public static class Patch_InspectNoRoomPenalty
    {
        public static void Prefix() => RM_ProcessLists.suppress++;

        public static Exception Finalizer(Exception __exception)
        {
            if (RM_ProcessLists.suppress > 0) RM_ProcessLists.suppress--;
            return __exception;
        }
    }

    [HarmonyLib.HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("A machine's work-speed ratio is not shown as a room penalty in its stats")]
    public static class Patch_StatsNoRoomPenalty
    {
        public static MethodBase TargetMethod() =>
            HarmonyLib.AccessTools.EnumeratorMoveNext(HarmonyLib.AccessTools.Method(typeof(CompAdvancedResourceProcessor),
                nameof(CompAdvancedResourceProcessor.SpecialDisplayStats)));

        public static void Prefix() => RM_ProcessLists.suppress++;

        public static Exception Finalizer(Exception __exception)
        {
            if (RM_ProcessLists.suppress > 0) RM_ProcessLists.suppress--;
            return __exception;
        }
    }
}
