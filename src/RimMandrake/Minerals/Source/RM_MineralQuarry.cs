// Quarry adapter (MINERAL_QUARRY_WIRE_LOCAL_POOL; minerals registry design §6.4, owner ruling 2026-10-03).
// The Quarry mod (ogliss.thewhitecrayon.quarry) answers a Resources request with OreDictionary.TakeOne(): one planet-wide list of
// every resource-rock mineable plus industrial components, whatever the land under the quarry is. A transpiler on
// Building_Quarry.GiveResources replaces that one call with RM_MineralQuarry.Draw(this, ref singleSpawn): Quarry's unregistered
// entries keep their share with Quarry's weights (owner card: an unknown ore behaves as its mod intended); the governed share
// comes from this biome's registry pool, or local rock chunks (singleSpawn = true) when the biome has none.
// No compile reference to Quarry.dll: every Quarry member is found by name, and each patch class's Prepare() skips it cleanly when
// Quarry is not loaded. A renamed member makes the patch throw inside PatchApplier, which logs it and keeps the rest of the mod.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Minerals
{
    public static class RM_MineralQuarry
    {
        public const string HarmonyId = "mandrake.rm.minerals";

        internal static readonly Type QuarryType = AccessTools.TypeByName("Quarry.Building_Quarry");
        internal static readonly Type DictType = AccessTools.TypeByName("Quarry.OreDictionary");
        internal static readonly Type SettingsType = AccessTools.TypeByName("Quarry.QuarrySettings");
        internal static readonly Type EntryType = AccessTools.TypeByName("Quarry.ThingCountExposable");
        internal static readonly Type DriverType = AccessTools.TypeByName("Quarry.JobDriver_MineQuarry");

        internal static readonly MethodInfo TakeOne = DictType == null ? null : AccessTools.Method(DictType, "TakeOne", Type.EmptyTypes);
        internal static readonly MethodInfo GiveResources = QuarryType == null ? null : AccessTools.Method(QuarryType, "GiveResources");
        internal static readonly FieldInfo ResourceModifer = SettingsType == null ? null : AccessTools.Field(SettingsType, "resourceModifer");
        private static readonly MethodInfo build = DictType == null ? null : AccessTools.Method(DictType, "Build");
        private static readonly FieldInfo oreDictionary = SettingsType == null ? null : AccessTools.Field(SettingsType, "oreDictionary");
        private static readonly FieldInfo entryCount = EntryType == null ? null : AccessTools.Field(EntryType, "count");
        private static readonly PropertyInfo entryThing = EntryType == null ? null : AccessTools.Property(EntryType, "thingDef");
        private static readonly PropertyInfo chunksUnder = QuarryType == null ? null : AccessTools.Property(QuarryType, "ChunksUnder");

        /// <summary>The last Resources draw came from this biome's registry pool: the yield multiplier applies to its stack. Set by Draw,
        /// cleared by every GiveResources call and consumed by the stack-size read, so it can never reach another job's stack.</summary>
        internal static bool lastDrawLocal;

        public static bool QuarryLoaded => QuarryType != null && TakeOne != null && GiveResources != null;

        /// <summary>The Quarry mod's dictionary as it draws from it: (mined item defName, weight). Builds it the way TakeOne would when
        /// Quarry has not yet.</summary>
        public static List<KeyValuePair<string, float>> QuarryDictionary()
        {
            var list = new List<KeyValuePair<string, float>>();
            if (oreDictionary == null || entryCount == null || entryThing == null) return list;
            if (oreDictionary.GetValue(null) == null && build != null)
                build.Invoke(null, build.GetParameters().Length == 1 ? new object[] { true } : null);
            if (!(oreDictionary.GetValue(null) is System.Collections.IEnumerable entries)) return list;
            foreach (object e in entries)
            {
                if (e == null) continue;
                var t = entryThing.GetValue(e, null) as ThingDef;
                if (t == null) continue;
                list.Add(new KeyValuePair<string, float>(t.defName, Convert.ToSingle(entryCount.GetValue(e), CultureInfo.InvariantCulture)));
            }
            return list;
        }

        /// <summary>This biome's quarry plan from the live registry, settings and Quarry dictionary.</summary>
        public static QuarryPlan PlanFor(string biome)
        {
            return RM_QuarryKernel.Plan(RM_MineralPolicy.Rows, biome, RM_MineralsSettings.overrides, QuarryDictionary(),
                                        RM_MineralsSettings.suppressUnregistered);
        }

        /// <summary>Public draw (design §6.4: the API for the other local-material consumers). The item a quarry on this map hands out,
        /// or null = local rock. Callers must check that the policy is on (RM_MineralsSettings.enabled and quarryFollowsLocal).</summary>
        public static QuarryEntry QuarryDraw(Map map)
        {
            if (map?.Biome == null) return null;
            return RM_QuarryKernel.Draw(PlanFor(map.Biome.defName), Rand.Value, Rand.Value);
        }

        private static ThingDef Original()
        {
            return (ThingDef)TakeOne.Invoke(null, null);
        }

        /// <summary>Called in place of OreDictionary.TakeOne() inside Building_Quarry.GiveResources (the Resources branch, which has
        /// just set singleSpawn = false).</summary>
        public static ThingDef Draw(Thing quarry, ref bool singleSpawn)
        {
            lastDrawLocal = false;
            if (!RM_MineralsSettings.enabled || !RM_MineralsSettings.quarryFollowsLocal || quarry?.Map == null) return Original();
            QuarryEntry e = QuarryDraw(quarry.Map);
            if (e != null)
            {
                ThingDef t = DefDatabase<ThingDef>.GetNamedSilentFail(e.Item);
                if (t != null)
                {
                    lastDrawLocal = e.MaterialId != null;
                    return t;
                }
            }
            // governed share with no local row: local rock, one chunk (as Quarry's own chunk branch hands it out)
            if (chunksUnder?.GetValue(quarry, null) is List<ThingDef> chunks && chunks.Count > 0)
            {
                singleSpawn = true;
                return chunks.RandomElement();
            }
            return Original();   // no rock under a quarry cannot happen in Quarry's placement rules; keep its behaviour if it does
        }

        /// <summary>Quarry's stack-size factor (QuarrySettings.resourceModifer) times our quarry yield multiplier when the stack came
        /// from the local pool. Consumes the flag.</summary>
        public static float Yield(float resourceModifer)
        {
            bool local = lastDrawLocal;
            lastDrawLocal = false;
            return local ? resourceModifer * RM_MineralsSettings.quarryMultiplier : resourceModifer;
        }

        /// <summary>The single JobDriver_MineQuarry method (a compiler-generated toil lambda) that calls GiveResources and reads
        /// resourceModifer; null when not exactly one does.</summary>
        internal static MethodBase StackMethod()
        {
            if (DriverType == null || GiveResources == null || ResourceModifer == null) return null;
            var hits = new List<MethodBase>();
            foreach (MethodInfo m in AccessTools.GetDeclaredMethods(DriverType))
            {
                if (m.IsAbstract || m.GetMethodBody() == null) continue;
                bool calls = false, reads = false;
                foreach (KeyValuePair<OpCode, object> ins in PatchProcessor.ReadMethodBody(m))
                {
                    if (ins.Value is MethodInfo mi && mi == GiveResources) calls = true;
                    if (ins.Value is FieldInfo fi && fi == ResourceModifer) reads = true;
                }
                if (calls && reads) hits.Add(m);
            }
            if (hits.Count != 1) Log.Warning("[RM Minerals] quarry yield multiplier: expected one JobDriver_MineQuarry method calling GiveResources "
                                           + "and reading resourceModifer, found " + hits.Count + "; the multiplier is off");
            return hits.Count == 1 ? hits[0] : null;
        }

        internal static bool Owns(MethodBase m, Func<Patches, IEnumerable<Patch>> kind)
        {
            Patches p = m == null ? null : Harmony.GetPatchInfo(m);
            return p != null && kind(p).Any(x => x.owner == HarmonyId);
        }
    }

    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Quarry output follows local minerals", typeof(RM_MineralsSettings), nameof(RM_MineralsSettings.quarryFollowsLocal))]
    public static class Patch_QuarryGiveResources
    {
        public static bool Prepare() { return RM_MineralQuarry.QuarryLoaded; }

        public static MethodBase TargetMethod() { return RM_MineralQuarry.GiveResources; }

        public static void Prefix() { RM_MineralQuarry.lastDrawLocal = false; }

        public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions, MethodBase original)
        {
            List<CodeInstruction> code = instructions.ToList();
            int[] at = code.Select((c, i) => c.Calls(RM_MineralQuarry.TakeOne) ? i : -1).Where(i => i >= 0).ToArray();
            if (at.Length != 1)
                throw new InvalidOperationException("Building_Quarry.GiveResources: expected one OreDictionary.TakeOne() call, found " + at.Length);
            ParameterInfo[] ps = original.GetParameters();
            int single = Array.FindIndex(ps, p => p.Name == "singleSpawn");
            if (single < 0 || !ps[single].ParameterType.IsByRef)
                throw new InvalidOperationException("Building_Quarry.GiveResources: no by-ref parameter named singleSpawn");
            CodeInstruction call = code[at[0]];
            var replacement = new List<CodeInstruction>
            {
                new CodeInstruction(OpCodes.Ldarg_0),
                new CodeInstruction(OpCodes.Ldarg_S, (byte)(single + 1)),   // instance method: arg 0 is this
                new CodeInstruction(OpCodes.Call, AccessTools.Method(typeof(RM_MineralQuarry), nameof(RM_MineralQuarry.Draw))),
            };
            replacement[0].labels.AddRange(call.labels);
            replacement[0].blocks.AddRange(call.blocks);
            code.RemoveAt(at[0]);
            code.InsertRange(at[0], replacement);
            return code;
        }
    }

    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Quarry yield multiplier")]
    public static class Patch_QuarryStackYield
    {
        public static bool Prepare() { return RM_MineralQuarry.QuarryLoaded && RM_MineralQuarry.DriverType != null; }

        public static MethodBase TargetMethod() { return RM_MineralQuarry.StackMethod(); }

        public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
        {
            int n = 0;
            foreach (CodeInstruction c in instructions)
            {
                yield return c;
                if (c.opcode == OpCodes.Ldsfld && c.operand is FieldInfo f && f == RM_MineralQuarry.ResourceModifer)
                {
                    n++;
                    yield return new CodeInstruction(OpCodes.Call, AccessTools.Method(typeof(RM_MineralQuarry), nameof(RM_MineralQuarry.Yield)));
                }
            }
            if (n != 1) throw new InvalidOperationException("JobDriver_MineQuarry stack lambda: expected one resourceModifer read, found " + n);
        }
    }

    /// <summary>Bridge proof hook for Minerals/validation.py (jawa/static_call). Reads only; draws use a private System.Random so the
    /// game's Rand stream is untouched.</summary>
    public static class RM_MineralQuarryProof
    {
        /// <summary>"quarry=0|1;wired=0|1;yield=0|1;on=0|1;biome=B;share=0.87;local=mat:item:w,...;unreg=item:w,...;draws=item:n,...;rock=n"
        /// for <paramref name="args"/> = "biome" or "biome;N" (N kernel draws, default 1000).</summary>
        public static string ProofQuarry(string args)
        {
            string[] a = (args ?? "").Split(';');
            string biome = a[0];
            int n = a.Length > 1 && int.TryParse(a[1], out int k) ? Math.Max(1, Math.Min(k, 100000)) : 1000;
            var sb = new StringBuilder();
            sb.Append("quarry=").Append(RM_MineralQuarry.QuarryLoaded ? 1 : 0)
              .Append(";wired=").Append(RM_MineralQuarry.Owns(RM_MineralQuarry.GiveResources, p => p.Transpilers) ? 1 : 0)
              .Append(";yield=").Append(RM_MineralQuarry.Owns(RM_MineralQuarry.StackMethod(), p => p.Transpilers) ? 1 : 0)
              .Append(";on=").Append(RM_MineralsSettings.enabled && RM_MineralsSettings.quarryFollowsLocal ? 1 : 0)
              .Append(";biome=").Append(biome);
            if (!RM_MineralQuarry.QuarryLoaded || biome.NullOrEmpty()) return sb.ToString();
            QuarryPlan p = RM_MineralQuarry.PlanFor(biome);
            sb.Append(";share=").Append(p.UnregisteredShare.ToString("0.####", CultureInfo.InvariantCulture));
            sb.Append(";local=").Append(string.Join(",", p.Local.Select(e => e.MaterialId + ":" + e.Item + ":" + e.Weight.ToString("0.##", CultureInfo.InvariantCulture))));
            sb.Append(";unreg=").Append(string.Join(",", p.Unregistered.Select(e => e.Item + ":" + e.Weight.ToString("0.##", CultureInfo.InvariantCulture))));
            var rng = new System.Random(12345);
            var counts = new SortedDictionary<string, int>(StringComparer.Ordinal);
            int rock = 0;
            for (int i = 0; i < n; i++)
            {
                QuarryEntry e = RM_QuarryKernel.Draw(p, rng.NextDouble(), rng.NextDouble());
                if (e == null) { rock++; continue; }
                counts[e.Item] = counts.TryGetValue(e.Item, out int c) ? c + 1 : 1;
            }
            sb.Append(";draws=").Append(string.Join(",", counts.Select(kv => kv.Key + ":" + kv.Value))).Append(";rock=").Append(rock);
            return sb.ToString();
        }
    }
}
