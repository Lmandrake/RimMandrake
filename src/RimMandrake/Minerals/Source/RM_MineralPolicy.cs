using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Minerals
{
    /// <summary>The mineral policy service (MINERAL_POLICY_CODE_STARTUP_ZEROING; registry design §6.2). At startup, for every def the
    /// registry governs, it writes the target mineableScatterCommonality / deepCommonality the kernel decides, so no vanilla or donor
    /// path places it any more; unregistered bearing defs are reported (and zeroed only when the player turns suppression on).
    /// Every write is computed from a snapshot of the original values, so the master toggle off restores them exactly.
    /// Channel adapters (R3 surface, R4 quarry, R5 framework/meteorite/mutator/scanner/outpost) read rows and effective values here.</summary>
    [StaticConstructorOnStartup]
    public static class RM_MineralPolicy
    {
        private static readonly Dictionary<string, MineralDefInfo> originals = new Dictionary<string, MineralDefInfo>();
        private static readonly Dictionary<string, float[]> lastApplied = new Dictionary<string, float[]>();
        private static List<MineralRow> rows;
        private static Dictionary<string, MineralRow> byMaterial;
        private static readonly HashSet<string> surfacePlacers = new HashSet<string>();

        public static List<PolicyDecision> LastDecisions { get; private set; } = new List<PolicyDecision>();
        public static int Revision { get; private set; }    // bumps on every Apply; adapters key their pool caches on it
        public static string LastReason { get; private set; } = "";
        public static bool SurfacePlacerActive => surfacePlacers.Count > 0;

        static RM_MineralPolicy()
        {
            Apply("startup");
        }

        public static List<MineralRow> Rows
        {
            get
            {
                if (rows == null)
                {
                    rows = new List<MineralRow>();
                    byMaterial = new Dictionary<string, MineralRow>();
                    foreach (RM_MineralRegistryDef d in DefDatabase<RM_MineralRegistryDef>.AllDefsListForReading)
                    {
                        MineralRow r = d.ToRow();
                        if (r.MaterialId.NullOrEmpty()) continue;
                        if (byMaterial.ContainsKey(r.MaterialId))
                        {
                            Log.Error("[RM Minerals] two registry defs share materialId '" + r.MaterialId + "'; " + d.defName + " ignored");
                            continue;
                        }
                        byMaterial[r.MaterialId] = r;
                        rows.Add(r);
                    }
                }
                return rows;
            }
        }

        public static MineralRow Row(string materialId)
        {
            _ = Rows;
            return materialId != null && byMaterial.TryGetValue(materialId, out MineralRow r) ? r : null;
        }

        /// <summary>The value an adapter uses for a material in a biome: override, else registry, times the global multiplier.</summary>
        public static float? EffectiveValue(string materialId, string biomeDefName, float globalMultiplier)
        {
            return RM_MineralPolicyKernel.EffectiveValue(Row(materialId), biomeDefName, RM_MineralsSettings.overrides, globalMultiplier);
        }

        /// <summary>The snapshot value of a def before the policy wrote it (a copy), or null when the policy never saw it.</summary>
        public static MineralDefInfo Original(string defName)
        {
            return defName != null && originals.TryGetValue(defName, out MineralDefInfo o) ? RM_MineralPolicyKernel.Copy(o) : null;
        }

        /// <summary>Copies of every snapshot value, keyed by defName (the surface adapter caches its targets on Revision).</summary>
        public static Dictionary<string, MineralDefInfo> OriginalsCopy()
        {
            return originals.ToDictionary(kv => kv.Key, kv => RM_MineralPolicyKernel.Copy(kv.Value));
        }

        /// <summary>Called by a surface placer (wave R3) once it is ready to place governed veins per biome: from then on governed
        /// mineables with a surface source are zeroed for vanilla scatter, because the placer scatters them itself.</summary>
        public static void RegisterSurfacePlacer(string owner)
        {
            if (owner.NullOrEmpty() || !surfacePlacers.Add(owner)) return;
            Apply("surface placer registered: " + owner);
        }

        private static MineralDefInfo Read(ThingDef t)
        {
            BuildingProperties b = t.building;
            return new MineralDefInfo(t.defName, b != null ? b.mineableScatterCommonality : 0f, t.deepCommonality,
                                      b?.mineableThing?.defName, b != null);
        }

        private static IEnumerable<ThingDef> Candidates(HashSet<string> named)
        {
            foreach (ThingDef t in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (t == null) continue;
                // originals: a def we zeroed earlier must stay reachable, or turning a setting off could never restore it
                if (named.Contains(t.defName) || originals.ContainsKey(t.defName) || t.deepCommonality > 0f
                    || (t.building != null && (t.building.mineableScatterCommonality > 0f || t.building.mineableThing != null)))
                    yield return t;
            }
        }

        /// <summary>Snapshot (first call) or re-adopt (later calls: another mod wrote after us), decide, write. Idempotent.</summary>
        public static void Apply(string why)
        {
            List<MineralRow> rs = Rows;
            var named = new HashSet<string>();
            foreach (MineralRow r in rs)
            {
                named.UnionWith(r.Items); named.UnionWith(r.Mineables); named.UnionWith(r.Producers);
                named.UnionWith(r.ZeroProducers); named.UnionWith(r.RetiredItems);
            }
            var current = new List<ThingDef>(Candidates(named));
            var adopted = RM_MineralPolicyKernel.Readopt(originals, lastApplied, current.Select(Read));
            if (Revision > 0 && adopted.Count > 0)
                Log.Message("[RM Minerals] re-assert (" + why + "): " + adopted.Count + " values changed by another mod since the last write, "
                          + "adopted as originals: " + string.Join(", ", adopted.Take(20)) + (adopted.Count > 20 ? ", ..." : ""));

            var opts = new PolicyOptions
            {
                Enabled = RM_MineralsSettings.enabled,
                SuppressUnregistered = RM_MineralsSettings.suppressUnregistered,
                SurfacePlacerActive = SurfacePlacerActive,
            };
            List<PolicyDecision> decisions = RM_MineralPolicyKernel.Decide(rs, originals.Values.ToList(), opts);
            var byName = current.ToDictionary(t => t.defName);
            int zeroed = 0;
            foreach (PolicyDecision p in decisions)
            {
                if (!byName.TryGetValue(p.DefName, out ThingDef t)) continue;
                if (t.building != null) t.building.mineableScatterCommonality = p.Scatter;
                t.deepCommonality = p.Deep;
                lastApplied[p.DefName] = new[] { t.building != null ? t.building.mineableScatterCommonality : 0f, t.deepCommonality };
                MineralDefInfo o = originals[p.DefName];
                if ((o.Scatter > 0f && p.Scatter == 0f) || (o.Deep > 0f && p.Deep == 0f)) zeroed++;
            }
            LastDecisions = decisions;
            LastReason = why;
            Revision++;

            List<PolicyDecision> unreg = decisions.Where(p => p.Unregistered).ToList();
            Log.Message("[RM Minerals] policy applied (" + why + "): " + rs.Count + " registry materials, " + decisions.Count
                      + " defs decided, " + zeroed + " zeroed, " + unreg.Count + " unregistered"
                      + (opts.Enabled ? "" : " - master toggle OFF, every original value restored")
                      + (opts.SurfacePlacerActive ? "" : "; surface placer not active, governed veins with a surface source keep vanilla scatter"));
            if (opts.Enabled && opts.SuppressUnregistered && unreg.Count > 0 && why == "startup")
                Log.Warning("[RM Minerals] suppressed " + unreg.Count + " minerals the registry has no row for (setting 'Suppress unregistered "
                          + "minerals' is on): " + string.Join(", ", unreg.Select(p => p.DefName)));
            // the meteorite whitelist follows the same master toggle and the same re-assert points (settings change, FinalizeInit)
            try { RM_MineralMeteorite.Refresh(why); }
            catch (System.Exception e) { Log.Error("[RM Minerals] meteorite filter refresh failed (" + why + "): " + e); }
        }
    }

    /// <summary>Bridge proof hooks for Minerals/validation.py (jawa/static_call). Reads and re-applies; never invents state.</summary>
    public static class RM_MineralPolicyProof
    {
        /// <summary>"rev=N;rows=N;decided=N;unreg=N;placer=0|1;Def=scatter/deep/role;..." for each ';'-separated defName (absent = "missing").</summary>
        public static string ProofState(string defs)
        {
            var sb = new System.Text.StringBuilder();
            List<PolicyDecision> d = RM_MineralPolicy.LastDecisions;
            sb.Append("rev=").Append(RM_MineralPolicy.Revision).Append(";rows=").Append(RM_MineralPolicy.Rows.Count)
              .Append(";decided=").Append(d.Count).Append(";unreg=").Append(d.Count(p => p.Unregistered))
              .Append(";placer=").Append(RM_MineralPolicy.SurfacePlacerActive ? 1 : 0).Append(";reason=").Append(RM_MineralPolicy.LastReason);
            foreach (string n in (defs ?? "").Split(';'))
            {
                if (n.Length == 0) continue;
                ThingDef t = DefDatabase<ThingDef>.GetNamedSilentFail(n);
                PolicyDecision p = d.FirstOrDefault(x => x.DefName == n);
                sb.Append(';').Append(n).Append('=');
                if (t == null) { sb.Append("missing"); continue; }
                sb.Append((t.building != null ? t.building.mineableScatterCommonality : 0f).ToString(System.Globalization.CultureInfo.InvariantCulture))
                  .Append('/').Append(t.deepCommonality.ToString(System.Globalization.CultureInfo.InvariantCulture))
                  .Append('/').Append(p == null ? "undecided" : p.Unregistered ? "unregistered" : p.MaterialId);
            }
            return sb.ToString();
        }

        /// <summary>Re-applies the policy as a settings change would (WriteSettings is not called by jawa/mod_settings_field).</summary>
        public static string ProofApply(string why)
        {
            RM_MineralPolicy.Apply("proof: " + why);
            return ProofState("");
        }
    }

    // Ordering against other mods' static constructors is not guaranteed (design §6.2), so the policy re-asserts on every game init.
    [HarmonyPatch(typeof(Game), nameof(Game.FinalizeInit))]
    [RimMandrake.Shared.PatchFeature("Re-assert the mineral policy when a game starts")]
    public static class Patch_MineralPolicyReassert
    {
        public static void Postfix()
        {
            RM_MineralPolicy.Apply("Game.FinalizeInit");
        }
    }
}
