using System;
using System.Collections.Generic;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_FREE_TIER_MOVE_BUILD_1, the frozen-world back-compat. A def that moves
    // between our mods under a new defName orphans every saved reference to the
    // old name (a placed building, a pawn's hediff, a thought, a research row).
    //
    // MEASURED from decompiled 1.6 (RimSage, 2026-10-03), why this is a Harmony
    // postfix and not a BackCompatibilityConverter:
    //  * Scribe resolves a saved def name through
    //    BackCompatibility.BackCompatibleDefName(defType, defName, ...)
    //    (ScribeExtractor, Scribe_Defs). It RETURNS EARLY, before consulting the
    //    private conversionChain, when CheckSaveIdenticalToCurrentEnvironment()
    //    is true: same game build and !ScribeMetaHeaderUtility.modListChanged.
    //    A rename between two mods that both stay active leaves the mod list
    //    unchanged, so a converter would never be asked. A postfix runs after
    //    every return path.
    //  * Terrain is saved as a ushort shortHash per cell; an unknown hash goes to
    //    BackCompatibility.BackCompatibleTerrainWithShortHash(hash), which knows one
    //    vanilla hash. ShortHashGiver assigns StableStringHash(defName) % 65535 and
    //    only probes upward on a collision, so the old name's base hash is what a
    //    save almost always holds; the postfix maps that hash to the new def.
    //  * Thing cross-references survive a rename by themselves:
    //    LoadedObjectDirectory looks Things up by Thing.IDNumberFromThingID, the
    //    number, not the "<defName><number>" string.
    //
    // Data, not code: any mod adds an RM_DefAliasDef listing from -> to (optionally
    // defType and fromHash). An alias applies only when the old name resolves to
    // nothing in that def type and the chain's end does, so it can never shadow a
    // live def. Chains (A -> B -> C) are followed with a cycle check, conflicting
    // declarations are logged, and fromHash covers a terrain whose saved shortHash
    // was probed off its base value (DEF_ALIAS_CHAIN_HASH_1).
    public class RM_DefAlias
    {
        public string from;
        public string to;
        // DEF_ALIAS_CHAIN_HASH_1: optional def-type key ("ThingDef", "TerrainDef" ...; short or full type name).
        // Empty = any def type, as before.
        public string defType;
        // DEF_ALIAS_CHAIN_HASH_1: the old terrain's saved shortHash when it is NOT the base
        // StableStringHash(from) % 65535 (ShortHashGiver probed upward on a collision). -1 = use the base hash.
        public int fromHash = -1;

        public bool AppliesTo(Type t)
        {
            return defType.NullOrEmpty() || t == null || defType == t.Name || defType == t.FullName;
        }

        public ushort SavedTerrainHash => fromHash >= 0 ? (ushort)fromHash : (ushort)(GenText.StableStringHash(from) % 65535);
    }

    public class RM_DefAliasDef : Def
    {
        public List<RM_DefAlias> aliases = new List<RM_DefAlias>();
    }

    public static class RM_DefAliasPatches
    {
        private const int MaxHops = 16;

        private static Dictionary<string, List<RM_DefAlias>> byName;
        private static Dictionary<ushort, string> terrainByHash;

        private static void EnsureBuilt()
        {
            if (byName != null)
            {
                return;
            }
            byName = new Dictionary<string, List<RM_DefAlias>>();
            terrainByHash = new Dictionary<ushort, string>();
            foreach (RM_DefAliasDef def in DefDatabase<RM_DefAliasDef>.AllDefsListForReading)
            {
                if (def.aliases == null)
                {
                    continue;
                }
                foreach (RM_DefAlias a in def.aliases)
                {
                    if (a == null || a.from.NullOrEmpty() || a.to.NullOrEmpty())
                    {
                        continue;
                    }
                    if (!byName.TryGetValue(a.from, out List<RM_DefAlias> list))
                    {
                        list = new List<RM_DefAlias>();
                        byName[a.from] = list;
                    }
                    // DEF_ALIAS_CHAIN_HASH_1: two aliases for the same old name and overlapping def types that point
                    // at different new names are a data conflict; the first one loaded wins and the rest are named.
                    RM_DefAlias clash = list.Find(o => o.to != a.to
                        && (o.defType.NullOrEmpty() || a.defType.NullOrEmpty() || o.defType == a.defType));
                    if (clash != null)
                    {
                        Log.Warning("[RM EnvironmentalHazards] def alias conflict in " + def.defName + ": " + a.from + " -> "
                            + a.to + " ignored; " + a.from + " -> " + clash.to + " was declared first.");
                        continue;
                    }
                    list.Add(a);
                    if (!a.AppliesTo(typeof(TerrainDef)))
                    {
                        continue;
                    }
                    // Terrain is keyed by the saved hash; what it resolves to is decided at lookup, through the chain.
                    ushort h = a.SavedTerrainHash;
                    if (terrainByHash.TryGetValue(h, out string prior) && prior != a.from)
                    {
                        Log.Warning("[RM EnvironmentalHazards] def alias terrain-hash conflict: " + a.from + " and " + prior
                            + " both claim saved hash " + h + "; give one an explicit fromHash.");
                        continue;
                    }
                    terrainByHash[h] = a.from;
                }
            }
        }

        private static RM_DefAlias Find(Type defType, string name)
        {
            if (name == null || !byName.TryGetValue(name, out List<RM_DefAlias> list))
            {
                return null;
            }
            for (int i = 0; i < list.Count; i++)
            {
                if (list[i].AppliesTo(defType))
                {
                    return list[i];
                }
            }
            return null;
        }

        // Pure lookup, shared by the postfix and the proof. DEF_ALIAS_CHAIN_HASH_1: follows A -> B -> C until a name
        // resolves to a live def of this type, so an alias still works after its intermediate def is gone too; a
        // cycle stops the walk and is named once.
        public static string Resolve(Type defType, string name)
        {
            EnsureBuilt();
            if (name == null || GenDefDatabase.GetDefSilentFail(defType, name, false) != null)
            {
                return null;
            }
            string cur = name;
            HashSet<string> seen = null;
            for (int hop = 0; hop < MaxHops; hop++)
            {
                RM_DefAlias a = Find(defType, cur);
                if (a == null)
                {
                    return null;
                }
                if (GenDefDatabase.GetDefSilentFail(defType, a.to, false) != null)
                {
                    return a.to;
                }
                seen ??= new HashSet<string> { name };
                if (!seen.Add(a.to))
                {
                    Log.WarningOnce("[RM EnvironmentalHazards] def alias cycle at " + a.to + " (from " + name + ").",
                        ("RM_DefAliasCycle" + name).GetHashCode());
                    return null;
                }
                cur = a.to;
            }
            return null;
        }

        public static void BackCompatibleDefName_Postfix(Type defType, ref string __result)
        {
            if (__result == null || DefDatabase<RM_DefAliasDef>.DefCount == 0)
            {
                return;
            }
            string to = Resolve(defType, __result);
            if (to != null)
            {
                __result = to;
            }
        }

        public static void BackCompatibleTerrainWithShortHash_Postfix(ushort hash, ref TerrainDef __result)
        {
            if (__result != null || DefDatabase<RM_DefAliasDef>.DefCount == 0)
            {
                return;
            }
            EnsureBuilt();
            if (terrainByHash.TryGetValue(hash, out string from))
            {
                string to = Resolve(typeof(TerrainDef), from);
                if (to != null)
                {
                    __result = DefDatabase<TerrainDef>.GetNamedSilentFail(to);
                }
            }
        }
    }

    // jawa/static_call proof: for every alias, what a save naming the old def
    // resolves to through the real engine entry points (the patched methods).
    public static class RM_DefAliasProof
    {
        public static string ProofAliases(string unused)
        {
            StringBuilder sb = new StringBuilder();
            int ok = 0, bad = 0;
            foreach (RM_DefAliasDef def in DefDatabase<RM_DefAliasDef>.AllDefsListForReading)
            {
                foreach (RM_DefAlias a in def.aliases)
                {
                    Def target = null;
                    Type type = null;
                    string want = null;
                    foreach (Type t in new[] { typeof(ThingDef), typeof(HediffDef), typeof(ThoughtDef), typeof(TerrainDef), typeof(ResearchProjectDef), typeof(RecipeDef), typeof(WeatherDef), typeof(GameConditionDef), typeof(IncidentDef) })
                    {
                        if (!a.AppliesTo(t))
                        {
                            continue;
                        }
                        // the chain's end, not just the first hop (DEF_ALIAS_CHAIN_HASH_1)
                        want = GenDefDatabase.GetDefSilentFail(t, a.to, false) != null ? a.to : RM_DefAliasPatches.Resolve(t, a.to);
                        target = want == null ? null : GenDefDatabase.GetDefSilentFail(t, want, false);
                        if (target != null)
                        {
                            type = t;
                            break;
                        }
                    }
                    string got = type == null ? null : BackCompatibility.BackCompatibleDefName(type, a.from);
                    bool pass = type != null && got == want;
                    if (type == typeof(TerrainDef))
                    {
                        TerrainDef viaHash = BackCompatibility.BackCompatibleTerrainWithShortHash(a.SavedTerrainHash);
                        pass = pass && viaHash == target;
                    }
                    if (pass) ok++; else bad++;
                    sb.Append(pass ? "PASS " : "FAIL ").Append(a.from).Append("->").Append(got ?? "null").Append("; ");
                }
            }
            return (bad == 0 && ok > 0 ? "PASS " : "FAIL ") + ok + " ok, " + bad + " bad: " + sb;
        }
    }
}
