// JawaBenchPatchSwitch.cs - the live switch of one of our Harmony patches, off and on, with call counters that prove it.
//
// Bridge v2 mutants (design/specs/2026-11-23-bridge-v2/05_build_design.md, decision 13; 04_live_tuning.md E9).
// "off" takes ONE patch method off ONE original (Harmony Unpatch of that method only). It is an overlay entry of
// class PUT BACK in the deviation record, so the process is tainted until restart. "on" repays that one entry:
// the same method goes back with its own owner, kind, priority, before and after, and Harmony's patch info is read
// back. The pure part (names, choice, refusals, counters) is JawaBenchPatchSwitchCore.cs.
//
// The counters are the witness. A JawaBench prefix on the PATCH METHOD counts its calls; a JawaBench prefix on the
// ORIGINAL counts the original's calls. arm_count puts the patch counter on first and then rebuilds the original's
// counter, so Harmony builds the original's replacement again AFTER the patch method is detoured. A caller that was
// compiled with the patch method inlined into it would count nothing (E9); the rebuild removes that caller.
//
// Each Harmony call is in its own try/catch and reports a failure as data (the discipline of JawaBenchArgGuard.cs).
// NO jawa/ prefix in prose here other than this file's one real tool name: build.py reads such literals as tools.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using Verse;
using D = JawaBench.BridgeTools.JawaBenchDeviationCore;
using P = JawaBench.BridgeTools.JawaBenchPatchSwitchCore;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchPatchSwitch
    {
        internal const string CounterOwner = "mandrake.jawabench.patchswitch";
        internal static readonly P.Counters Calls = new P.Counters();

        // One patch as Harmony holds it, with what "on" needs to put it back as it was.
        internal sealed class Spec
        {
            internal P.Row Row;
            internal MethodBase Original;
            internal MethodInfo Method;
            internal List<string> OrderBefore;
        }

        // Patches this switch took off, by id. Harmony forgets a removed patch, so this is where "list" finds it.
        private static readonly Dictionary<string, Spec> OffStore = new Dictionary<string, Spec>(StringComparer.Ordinal);
        private static readonly HashSet<long> PatchCounted = new HashSet<long>();

        internal static long Key(MethodBase m) => m.MethodHandle.Value.ToInt64();

        private static Patch[] Slot(Patches info, string kind)
        {
            if (info == null) return new Patch[0];
            switch (kind)
            {
                case "prefix": return info.Prefixes.ToArray();
                case "postfix": return info.Postfixes.ToArray();
                case "transpiler": return info.Transpilers.ToArray();
                default: return info.Finalizers.ToArray();
            }
        }

        private static string Params(MethodBase m) => string.Join(",", m.GetParameters().Select(p => p.ParameterType.Name));

        private static string Signature(MethodBase m) =>
            (m is MethodInfo mi ? mi.ReturnType.Name + " " : "") + m.Name + "(" +
            string.Join(", ", m.GetParameters().Select(p => p.ParameterType.FullName ?? p.ParameterType.Name)) + ")";

        // Harmony runs a slot in its own sorted order (priority, before, after, index), not in the order of the list.
        private static List<MethodInfo> Sorted(MethodBase original, Patch[] patches) =>
            PatchProcessor.GetSortedPatchMethods(original, patches);

        internal static List<string> Order(MethodBase original, string kind)
        {
            var patches = Slot(Harmony.GetPatchInfo(original), kind);
            List<MethodInfo> sorted;
            try { sorted = Sorted(original, patches); }
            catch (Exception) { sorted = patches.OrderByDescending(p => p.priority).ThenBy(p => p.index).Select(p => p.PatchMethod).ToList(); }
            return sorted.Select(m => m.DeclaringType?.FullName + "." + m.Name).ToList();
        }

        // Every patch in the process, ours or not, so that "off" refuses a foreign or a JawaBench patch by name.
        internal static List<Spec> ReadAll()
        {
            var mods = new Dictionary<Assembly, List<string>>();
            foreach (var mod in LoadedModManager.RunningMods)
                foreach (var asm in mod.assemblies?.loadedAssemblies ?? new List<Assembly>())
                {
                    if (!mods.TryGetValue(asm, out var ids)) mods[asm] = ids = new List<string>();
                    ids.Add(mod.PackageId);
                }
            var self = typeof(JawaBenchPatchSwitch).Assembly;
            var all = new List<Spec>();
            var originalsOf = new Dictionary<MethodInfo, HashSet<MethodBase>>();
            foreach (var original in Harmony.GetAllPatchedMethods().ToList())
            {
                var info = Harmony.GetPatchInfo(original);
                if (info == null || original.DeclaringType == null) continue;
                var here = P.Kinds.SelectMany(k => Slot(info, k)).Select(p => p.PatchMethod).Where(m => m != null).ToList();
                foreach (var kind in P.Kinds)
                    foreach (var patch in Slot(info, kind))
                    {
                        var method = patch.PatchMethod;
                        if (method?.DeclaringType == null) continue;
                        mods.TryGetValue(method.DeclaringType.Assembly, out var ids);
                        if (!originalsOf.TryGetValue(method, out var set)) originalsOf[method] = set = new HashSet<MethodBase>();
                        set.Add(original);
                        all.Add(new Spec
                        {
                            Original = original, Method = method,
                            Row = new P.Row
                            {
                                Kind = kind, PatchType = method.DeclaringType.FullName, PatchMethod = method.Name,
                                OrigType = original.DeclaringType.FullName, OrigMethod = original.Name, OrigParams = Params(original),
                                Owner = patch.owner, Mod = ids?.FirstOrDefault(), Priority = patch.priority, Index = patch.index,
                                Before = patch.before ?? new string[0], After = patch.after ?? new string[0],
                                Ours = P.IsOurs(ids), SelfAssembly = method.DeclaringType.Assembly == self,
                                Slots = here.Count(m => m == method)
                            }
                        });
                    }
            }
            foreach (var spec in all) spec.Row.Originals = originalsOf[spec.Method].Count;
            var live = new HashSet<string>(all.Select(s => s.Row.Id), StringComparer.Ordinal);
            foreach (var off in OffStore.Values)
                if (!live.Contains(off.Row.Id)) all.Add(off);
            return all;
        }

        internal static string State(Spec spec) =>
            Slot(Harmony.GetPatchInfo(spec.Original), spec.Row.Kind).Any(p => p.PatchMethod == spec.Method) ? "on" : "off";

        // The entry's write. "off": Unpatch this method from this original only. "on": patch it again as it was.
        internal static void Switch(Spec spec, object value)
        {
            var row = spec.Row;
            if (Equals(value, "off"))
            {
                new Harmony(row.Owner).Unpatch(spec.Original, spec.Method);
                row.Off = true;
                OffStore[row.Id] = spec;
                return;
            }
            var again = new HarmonyMethod(spec.Method) { priority = row.Priority, before = row.Before, after = row.After };
            new Harmony(row.Owner).Patch(spec.Original,
                prefix: row.Kind == "prefix" ? again : null, postfix: row.Kind == "postfix" ? again : null,
                transpiler: row.Kind == "transpiler" ? again : null, finalizer: row.Kind == "finalizer" ? again : null);
            row.Off = false;
            OffStore.Remove(row.Id);
        }

        internal static string SaveRefusal()
        {
            if (JawaBenchCompanionSafety.Effective(out string why, out _) == JawaBenchSafetyCore.Test)
                return JawaBenchDeviations.CanonicalRefusal();
            return "CAMPAIGN: off is refused under the CAMPAIGN profile (" + why + ")";
        }

        internal static string Off(Spec spec, string driver, string overlayName)
        {
            var row = spec.Row;
            spec.OrderBefore = Order(spec.Original, row.Kind);
            var entry = new D.Entry("overlay", "PUT BACK", "process", row.Id, null, "off", () => State(spec), v => Switch(spec, v));
            bool empty = ((System.Collections.ICollection)JawaBenchDeviations.Record.Receipt()["entries"]).Count == 0;
            string error = JawaBenchDeviations.ApplySettings(driver, overlayName ?? (empty ? "patch_switch" : null), entry);
            return error;
        }

        internal static string On(Spec spec, string driver)
            => JawaBenchDeviations.Record.Repay(JawaBenchHands.SettingsSessionOpen ? driver : null, spec.Row.Id);

        internal static string Arm(Spec spec)
        {
            var counter = new Harmony(CounterOwner);
            long pk = Key(spec.Method), ok = Key(spec.Original);
            if (PatchCounted.Add(pk))
            {
                Calls.Arm(pk);
                counter.Patch(spec.Method, prefix: new HarmonyMethod(typeof(JawaBenchPatchSwitch), nameof(CountPatchPre)) { priority = Priority.First });
            }
            // Off and on again, so Harmony builds the original's replacement once more after the patch method's detour.
            var original = new HarmonyMethod(typeof(JawaBenchPatchSwitch), nameof(CountOriginalPre)) { priority = Priority.First };
            Calls.Arm(ok);
            counter.Unpatch(spec.Original, original.method);
            counter.Patch(spec.Original, prefix: original);
            return null;
        }

        // Contained, void and Interlocked: a fault is counted and the patched method runs on unchanged.
        private static void CountPatchPre(MethodBase __originalMethod)
        {
            try { Calls.Hit(Key(__originalMethod)); }
            catch (Exception) { Calls.Fault(); }
        }

        private static void CountOriginalPre(MethodBase __originalMethod)
        {
            try { Calls.Hit(Key(__originalMethod)); }
            catch (Exception) { Calls.Fault(); }
        }

        internal static Dictionary<string, object> Wire(Spec spec, bool counts = false)
        {
            var r = spec.Row;
            var row = new Dictionary<string, object>
            {
                ["id"] = r.Id, ["kind"] = r.Kind, ["state"] = r.Off ? "off" : "on",
                ["original"] = new Dictionary<string, object> { ["declaringType"] = r.OrigType, ["method"] = r.OrigMethod, ["signature"] = Signature(spec.Original) },
                ["patchMethod"] = r.PatchName, ["owner"] = r.Owner, ["mod"] = r.Mod, ["priority"] = r.Priority,
                ["before"] = r.Before, ["after"] = r.After, ["originalsOfPatchMethod"] = r.Originals,
                ["offRefusal"] = P.OffRefusal(r, null)
            };
            if (counts)
            {
                row["patchCalls"] = Calls.Read(Key(spec.Method));
                row["originalCalls"] = Calls.Read(Key(spec.Original));
                row["counterFaults"] = Calls.Faults;
            }
            return row;
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/patch_switch",
            Description =
                "Take ONE of our own Harmony patches off and put it back, live, with call counters that prove it. " +
                "action=list: every prefix, postfix, transpiler and finalizer whose patch method is in the assembly of a " +
                "running mandrake.* mod, with its id, original, patch method, kind, owner, priority and state. " +
                "action=off patch=<id>: Harmony Unpatch of that one patch method on that one original. It is an overlay " +
                "entry of class PUT BACK in the deviation record and taints the process until restart. It refuses by name " +
                "UNKNOWN_PATCH, AMBIGUOUS, NOT_OURS, JAWABENCH, CANONICAL_SAVE or COULD_NOT_LOOK (the loaded save), " +
                "CAMPAIGN (the profile) and ALREADY_OFF. action=on patch=<id>: the same patch method goes back with its " +
                "owner, kind, priority, before and after, read back in Harmony's patch info; the entry is repaid and the " +
                "taint stays (ALREADY_ON, NOT_IN_RECORD). action=arm_count patch=<id>: a call counter on the patch method " +
                "and one on the original (TRANSPILER_NOT_COUNTABLE). action=count patch=<id>: read both counters; -1 is " +
                "not armed. A patch counter that stays still while the patch is on and the original counter rises means " +
                "an inlined or cached caller: the switch cannot prove that patch.",
            ResultDescription =
                "success, action, ticksGame; list: patches[] {id, kind, state, original{declaringType, method, signature}, " +
                "patchMethod, owner, mod, priority, before, after, originalsOfPatchMethod, offRefusal}, jawaBenchPatches, " +
                "otherPatches; off/on: patch, state, orderBefore, orderAfter, orderKept, deviation; arm_count/count: patch " +
                "with patchCalls, originalCalls, counterFaults. A refusal is success=false with its NAME first in message.")]
        public static async Task<object> PatchSwitch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'list' (default), 'off', 'on', 'arm_count' or 'count'.")]
            string action = "list",
            [ToolParameter(Description = "off/on/arm_count/count: a patch id from action=list, or a patch method 'Type.Method' or bare method name that names one patch.")]
            string patch = null,
            [ToolParameter(Description = "list: keep only patches whose mod packageId contains this text (case-insensitive).")]
            string mod = null,
            [ToolParameter(Description = "off: the overlay name in the deviation record; default 'patch_switch' when the record is empty.")]
            string overlayName = null,
            [ToolParameter(Description = "Session driver for off and on while a session is open.")]
            string driver = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string a = (action ?? "list").Trim().ToLowerInvariant();
                if (a != "list" && a != "off" && a != "on" && a != "arm_count" && a != "count")
                    return Fail("BAD_ACTION: action must be 'list', 'off', 'on', 'arm_count' or 'count'.");
                if (a == "off" || a == "on")
                {
                    string driverRefusal = JawaBenchHands.SettingsDriver(driver);
                    if (driverRefusal != null) return Fail(driverRefusal);
                }
                List<JawaBenchPatchSwitch.Spec> all;
                try { all = JawaBenchPatchSwitch.ReadAll(); }
                catch (Exception e)
                {
                    return Fail("COULD_NOT_LOOK: Harmony's patch info could not be read: " + e.GetType().Name + ": " + e.Message, new { harmonyError = true });
                }
                if (a == "list")
                {
                    string want = (mod ?? "").Trim().ToLowerInvariant();
                    var ours = all.Where(s => s.Row.Ours && !P.IsJawaBench(s.Row.Owner, s.Row.SelfAssembly) &&
                                              (want.Length == 0 || (s.Row.Mod ?? "").ToLowerInvariant().Contains(want)))
                                  .OrderBy(s => s.Row.Id, StringComparer.Ordinal).Select(s => JawaBenchPatchSwitch.Wire(s)).ToList();
                    return new
                    {
                        success = true, action = a, patches = ours, patchCount = ours.Count,
                        jawaBenchPatches = all.Count(s => P.IsJawaBench(s.Row.Owner, s.Row.SelfAssembly)),
                        otherPatches = all.Count(s => !s.Row.Ours && !P.IsJawaBench(s.Row.Owner, s.Row.SelfAssembly)),
                        ticksGame = TicksGameSafe()
                    };
                }
                var picked = P.Select(all.Select(s => s.Row).ToList(), patch, out string refusal);
                if (picked == null) return Fail(refusal);
                var spec = all.First(s => ReferenceEquals(s.Row, picked));
                try
                {
                    if (a == "arm_count" || a == "count")
                    {
                        string no = P.CountRefusal(picked);
                        if (no != null) return Fail(no);
                        if (a == "arm_count") JawaBenchPatchSwitch.Arm(spec);
                        return new { success = true, action = a, patch = JawaBenchPatchSwitch.Wire(spec, counts: true), ticksGame = TicksGameSafe() };
                    }
                    string error = a == "off"
                        ? P.OffRefusal(picked, JawaBenchPatchSwitch.SaveRefusal) ?? JawaBenchPatchSwitch.Off(spec, driver, overlayName)
                        : P.OnRefusal(picked) ?? JawaBenchPatchSwitch.On(spec, driver);
                    if (error != null) return Fail(error, new { patch = JawaBenchPatchSwitch.Wire(spec), deviation = JawaBenchDeviations.Record.Receipt() });
                    var after = JawaBenchPatchSwitch.Order(spec.Original, picked.Kind);
                    return new
                    {
                        success = true, action = a, patch = JawaBenchPatchSwitch.Wire(spec, counts: true),
                        state = JawaBenchPatchSwitch.State(spec), orderBefore = spec.OrderBefore, orderAfter = after,
                        orderKept = a == "on" ? (bool?)P.OrderKept(spec.OrderBefore, after) : null,
                        deviation = JawaBenchDeviations.Record.Receipt(), ticksGame = TicksGameSafe()
                    };
                }
                catch (Exception e)
                {
                    return Fail("COULD_NOT_LOOK: " + a + " failed in Harmony: " + e.GetType().Name + ": " + e.Message,
                        new { patch = JawaBenchPatchSwitch.Wire(spec), deviation = JawaBenchDeviations.Record.Receipt() });
                }
            }).ConfigureAwait(false);
        }
    }
}
