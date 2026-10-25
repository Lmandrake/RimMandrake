// Verse-free kernel of the mineral policy service (MINERAL_POLICY_CODE_STARTUP_ZEROING, minerals registry design §6.2).
// RM_MineralPolicy feeds it the registry rows and a snapshot of every mineral-bearing ThingDef, then writes back the target
// values it returns. SelfTest compiles this file alone: keep it free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;
using System.Globalization;

namespace RimMandrake.Minerals
{
    /// <summary>One registry material (one RM_MineralRegistryDef), reduced to what the policy needs.</summary>
    public sealed class MineralRow
    {
        public string MaterialId;
        public string Unit = "EPM";
        public float UnitsPerCellOrFind;
        public float DeepWeight;
        public float OtherBiomes;                       // OTHER_vanilla_biomes: every biome that is not ours
        public readonly HashSet<string> Items = new HashSet<string>();
        public readonly HashSet<string> Mineables = new HashSet<string>();
        public readonly HashSet<string> Producers = new HashSet<string>();
        public readonly HashSet<string> ZeroProducers = new HashSet<string>();
        public readonly HashSet<string> RetiredItems = new HashSet<string>();
        public readonly Dictionary<string, float> Cells = new Dictionary<string, float>();   // biome -> number in Unit
        public readonly Dictionary<string, string> Tokens = new Dictionary<string, string>(); // biome -> deep-only / herd / unbounded

        /// <summary>A surface source exists somewhere: a positive cell, a positive OTHER_vanilla_biomes, or a not-deposit-limited token.
        /// "deep-only" says there is no surface form.</summary>
        public bool HasSurfacePresence
        {
            get
            {
                if (OtherBiomes > 0f) return true;
                foreach (float v in Cells.Values) if (v > 0f) return true;
                foreach (string t in Tokens.Values) if (t == "herd" || t == "unbounded") return true;
                return false;
            }
        }

        /// <summary>Same rule as gen_mineral_registry.deep_homes (which writes DeepDrill's RM_DeepHomeTable): deep_weight > 0 and some
        /// biome column > 0 or deep-only. OTHER_vanilla_biomes is not a home column there, so it is not one here.</summary>
        public bool HasDeepHome
        {
            get
            {
                if (!(DeepWeight > 0f)) return false;
                foreach (float v in Cells.Values) if (v > 0f) return true;
                foreach (string t in Tokens.Values) if (t == "deep-only") return true;
                return false;
            }
        }
    }

    /// <summary>A ThingDef the policy may touch: its current scatter/deep weights and, for a mineable, the item it yields.</summary>
    public sealed class MineralDefInfo
    {
        public string DefName;
        public float Scatter;      // building.mineableScatterCommonality (0 when not a building)
        public float Deep;         // deepCommonality
        public string MinedItem;   // building.mineableThing defName, or null
        public bool IsBuilding;

        public MineralDefInfo() { }
        public MineralDefInfo(string defName, float scatter, float deep, string minedItem, bool isBuilding)
        {
            DefName = defName; Scatter = scatter; Deep = deep; MinedItem = minedItem; IsBuilding = isBuilding;
        }
    }

    public sealed class PolicyOptions
    {
        public bool Enabled = true;                 // "Minerals follow the registry"; off = every original value
        public bool SuppressUnregistered = false;   // owner card 2026-10-03: an unknown ore behaves as its mod intended
        public bool SurfacePlacerActive = false;    // set by the surface adapter (wave R3) once it places governed veins per biome
    }

    public sealed class PolicyDecision
    {
        public string DefName;
        public string MaterialId;   // null = unregistered
        public float Scatter;       // target value
        public float Deep;          // target value
        public string ScatterReason;
        public string DeepReason;
        public bool Unregistered => MaterialId == null;
    }

    public static class RM_MineralPolicyKernel
    {
        public const float MeanLumpCells = 30f;      // mineableScatterLumpSizeRange default 20-40 (design §4)
        public const string Kept = "kept";

        private enum Role { None, Item, Mineable, Inferred, Zero }

        /// <summary>True when a def carries any weight a placement channel reads.</summary>
        public static bool Bearing(MineralDefInfo d) { return d != null && (d.Scatter > 0f || d.Deep > 0f); }

        /// <summary>One decision per def that is either bearing (in <paramref name="originals"/>) or named by a row. Targets are
        /// computed from the ORIGINAL values, so applying twice is the same as applying once.</summary>
        public static List<PolicyDecision> Decide(IList<MineralRow> rows, IEnumerable<MineralDefInfo> originals, PolicyOptions o)
        {
            var named = new Dictionary<string, KeyValuePair<MineralRow, Role>>();
            var itemRow = new Dictionary<string, MineralRow>();
            var retired = new Dictionary<string, MineralRow>();
            foreach (MineralRow r in rows)
            {
                foreach (string n in r.Items) { Name(named, n, r, Role.Item); if (!itemRow.ContainsKey(n)) itemRow[n] = r; }
                foreach (string n in r.Mineables) Name(named, n, r, Role.Mineable);
                foreach (string n in r.Producers) Name(named, n, r, Role.Mineable);
                foreach (string n in r.ZeroProducers) Name(named, n, r, Role.Zero);
                foreach (string n in r.RetiredItems) { Name(named, n, r, Role.Zero); if (!retired.ContainsKey(n)) retired[n] = r; }
            }

            var outList = new List<PolicyDecision>();
            foreach (MineralDefInfo d in originals)
            {
                if (d == null || string.IsNullOrEmpty(d.DefName)) continue;
                MineralRow row = null;
                Role role = Role.None;
                if (named.TryGetValue(d.DefName, out KeyValuePair<MineralRow, Role> kv)) { row = kv.Key; role = kv.Value; }
                else if (d.MinedItem != null && retired.TryGetValue(d.MinedItem, out MineralRow rr)) { row = rr; role = Role.Zero; }
                else if (d.MinedItem != null && itemRow.TryGetValue(d.MinedItem, out MineralRow ir)) { row = ir; role = Role.Inferred; }
                if (row == null && !Bearing(d)) continue;

                var p = new PolicyDecision { DefName = d.DefName, MaterialId = row?.MaterialId, Scatter = d.Scatter, Deep = d.Deep,
                                             ScatterReason = Kept, DeepReason = Kept };
                outList.Add(p);
                if (!o.Enabled)
                {
                    p.ScatterReason = p.DeepReason = "master toggle off: original";
                    continue;
                }
                if (row == null)
                {
                    if (o.SuppressUnregistered)
                    {
                        p.Scatter = 0f; p.Deep = 0f;
                        p.ScatterReason = p.DeepReason = "unregistered: suppressed (setting on)";
                    }
                    else p.ScatterReason = p.DeepReason = "unregistered: behaves as its mod intended";
                    continue;
                }
                switch (role)
                {
                    case Role.Zero:
                        p.Scatter = 0f; p.Deep = 0f;
                        p.ScatterReason = p.DeepReason = "registry disables it (zero/retire)";
                        break;
                    case Role.Mineable:
                    case Role.Inferred:
                        string how = role == Role.Inferred ? " (yields " + d.MinedItem + ")" : "";
                        if (!row.HasSurfacePresence) { p.Scatter = 0f; p.ScatterReason = "no surface source in any biome" + how; }
                        else if (o.SurfacePlacerActive) { p.Scatter = 0f; p.ScatterReason = "placed per biome by the surface adapter" + how; }
                        else p.ScatterReason = "kept until the surface adapter (R3) places it per biome" + how;
                        if (d.Deep > 0f && !row.HasDeepHome) { p.Deep = 0f; p.DeepReason = "no deep home"; }
                        break;
                    case Role.Item:
                        if (!row.HasDeepHome) { p.Deep = 0f; p.DeepReason = "no deep home"; }
                        else p.DeepReason = "kept: the deep drill home filter limits it to its home biomes";
                        if (d.Scatter > 0f && !row.HasSurfacePresence) { p.Scatter = 0f; p.ScatterReason = "no surface source in any biome"; }
                        break;
                }
            }
            outList.Sort((a, b) => string.CompareOrdinal(a.DefName, b.DefName));
            return outList;
        }

        // A def named by several rows: zero beats any other role (the registry disabling a producer wins); otherwise first row wins.
        private static void Name(Dictionary<string, KeyValuePair<MineralRow, Role>> named, string n, MineralRow r, Role role)
        {
            if (string.IsNullOrEmpty(n)) return;
            if (named.TryGetValue(n, out KeyValuePair<MineralRow, Role> old) && !(role == Role.Zero && old.Value != Role.Zero)) return;
            named[n] = new KeyValuePair<MineralRow, Role>(r, role);
        }

        /// <summary>Re-assert support (Game.FinalizeInit; other mods' static constructors may run after ours). A value that differs
        /// from what we last wrote was written by someone else after us: adopt it as the new original. Returns the adopted defNames.</summary>
        public static List<string> Readopt(IDictionary<string, MineralDefInfo> originals, IDictionary<string, float[]> lastApplied,
                                           IEnumerable<MineralDefInfo> current)
        {
            var adopted = new List<string>();
            foreach (MineralDefInfo c in current)
            {
                if (c == null || c.DefName == null) continue;
                if (!originals.TryGetValue(c.DefName, out MineralDefInfo orig))
                {
                    originals[c.DefName] = Copy(c);   // a def that became bearing after the snapshot
                    adopted.Add(c.DefName);
                    continue;
                }
                // never written by us (it was not bearing and not governed at the snapshot): whatever it holds now is someone
                // else's value, so compare against the snapshot itself - or a late static constructor giving an unknown ore weight
                // would never reach the policy (suppression, the unregistered count)
                float[] last = lastApplied.TryGetValue(c.DefName, out float[] la) ? la : new[] { orig.Scatter, orig.Deep };
                bool changed = false;
                if (!Same(c.Scatter, last[0])) { orig.Scatter = c.Scatter; changed = true; }
                if (!Same(c.Deep, last[1])) { orig.Deep = c.Deep; changed = true; }
                if (changed) adopted.Add(c.DefName);
            }
            return adopted;
        }

        public static MineralDefInfo Copy(MineralDefInfo d)
        {
            return new MineralDefInfo(d.DefName, d.Scatter, d.Deep, d.MinedItem, d.IsBuilding);
        }

        private static bool Same(float a, float b) { return Math.Abs(a - b) < 1e-6f; }

        public static string OverrideKey(string materialId, string biome) { return materialId + "|" + biome; }

        /// <summary>The registry value of a row in a biome, before overrides and multipliers: the biome's own cell; a RUT_ twin with no
        /// column of its own reads its RM_ column; any biome that is not ours (no RM_/RUT_ prefix) reads OTHER_vanilla_biomes. Null when
        /// the cell is a token (deep-only, herd, unbounded): not a number in the row's unit.</summary>
        public static float? RegistryValue(MineralRow row, string biome)
        {
            if (row == null || string.IsNullOrEmpty(biome)) return null;
            if (row.Tokens.ContainsKey(biome)) return null;
            if (row.Cells.TryGetValue(biome, out float v)) return v;
            if (biome.StartsWith("RUT_", StringComparison.Ordinal))
            {
                string twin = "RM_" + biome.Substring(4);
                if (row.Tokens.ContainsKey(twin)) return null;
                if (row.Cells.TryGetValue(twin, out float tv)) return tv;
                return 0f;
            }
            if (biome.StartsWith("RM_", StringComparison.Ordinal)) return 0f;
            return row.OtherBiomes;
        }

        /// <summary>Effective value a channel adapter uses: a player's sparse absolute override if one exists, else the registry value;
        /// times the channel's global multiplier.</summary>
        public static float? EffectiveValue(MineralRow row, string biome, IDictionary<string, float> overrides, float globalMultiplier)
        {
            if (row == null) return null;
            if (overrides != null && overrides.TryGetValue(OverrideKey(row.MaterialId, biome), out float ov)) return ov * globalMultiplier;
            float? reg = RegistryValue(row, biome);
            if (reg == null) return null;
            return reg.Value * globalMultiplier;
        }

        /// <summary>Attempted lump count an EPM value means on a standard map (design §4): EPM / (units per cell x mean lump cells).</summary>
        public static float LumpsForEpm(float epm, float unitsPerCell)
        {
            if (!(unitsPerCell > 0f) || !(epm > 0f)) return 0f;
            return epm / (unitsPerCell * MeanLumpCells);
        }

        /// <summary>Inverse of LumpsForEpm: the settings screen edits deposits per map (owner card 2026-10-03), the registry and
        /// overrides store EPM.</summary>
        public static float EpmForLumps(float lumps, float unitsPerCell)
        {
            if (!(unitsPerCell > 0f) || !(lumps > 0f)) return 0f;
            return lumps * unitsPerCell * MeanLumpCells;
        }

        /// <summary>How the settings screen's numeric field shows a value (and so what an unfocused field re-parses every frame).</summary>
        public static string ShowNumber(float v) { return v.ToString("0.##", CultureInfo.InvariantCulture); }

        /// <summary>The settings screen's edit rule. <paramref name="shown"/> is the stored value in screen units (deposits for EPM
        /// rows); <paramref name="typed"/>/<paramref name="parsed"/> are the field's buffer and number. Null = the player did not
        /// change it: an unfocused field re-parses its own 2-decimal display, which must not rewrite a stored 1.234 as 1.23 (nor
        /// mint an override at a .xx5 rounding edge) just because the screen was opened. Else the new value to store (EPM for
        /// deposit rows).</summary>
        public static float? SettingsEdit(float shown, string typed, float parsed, bool deposits, float unitsPerCell)
        {
            if (parsed == shown || typed == ShowNumber(shown)) return null;
            return deposits ? EpmForLumps(parsed, unitsPerCell) : parsed;
        }

        /// <summary>True when a typed value is the registry value as the field shows it: store no override, so later registry
        /// updates reach the cell again.</summary>
        public static bool SameAsShown(float parsed, float registryShown) { return ShowNumber(parsed) == ShowNumber(registryShown); }

        /// <summary>The settings-screen translation: "~ 1.3 deposits of ~30 cells".</summary>
        public static string DescribeEpm(float epm, float unitsPerCell)
        {
            float lumps = LumpsForEpm(epm, unitsPerCell);
            if (lumps <= 0f) return "none";
            return "~" + lumps.ToString(lumps < 10f ? "0.0" : "0", CultureInfo.InvariantCulture) + " deposits of ~"
                 + MeanLumpCells.ToString("0", CultureInfo.InvariantCulture) + " cells";
        }
    }
}
