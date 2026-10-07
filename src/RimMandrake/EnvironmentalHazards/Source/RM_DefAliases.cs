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
    // Data, not code: any mod adds an RM_DefAliasDef listing from -> to. An alias
    // applies only when the old name resolves to nothing in that def type and the
    // new one does, so it can never shadow a live def.
    public class RM_DefAlias
    {
        public string from;
        public string to;
    }

    public class RM_DefAliasDef : Def
    {
        public List<RM_DefAlias> aliases = new List<RM_DefAlias>();
    }

    public static class RM_DefAliasPatches
    {
        private static Dictionary<string, string> byName;
        private static Dictionary<ushort, string> terrainByHash;

        private static void EnsureBuilt()
        {
            if (byName != null)
            {
                return;
            }
            byName = new Dictionary<string, string>();
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
                    byName[a.from] = a.to;
                    if (DefDatabase<TerrainDef>.GetNamedSilentFail(a.to) != null)
                    {
                        terrainByHash[(ushort)(GenText.StableStringHash(a.from) % 65535)] = a.to;
                    }
                }
            }
        }

        // Pure lookup, shared by the postfix and the proof.
        public static string Resolve(Type defType, string name)
        {
            EnsureBuilt();
            if (name == null || !byName.TryGetValue(name, out string to))
            {
                return null;
            }
            if (GenDefDatabase.GetDefSilentFail(defType, name, false) != null)
            {
                return null;
            }
            return GenDefDatabase.GetDefSilentFail(defType, to, false) != null ? to : null;
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
            if (terrainByHash.TryGetValue(hash, out string to))
            {
                __result = DefDatabase<TerrainDef>.GetNamedSilentFail(to);
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
                    foreach (Type t in new[] { typeof(ThingDef), typeof(HediffDef), typeof(ThoughtDef), typeof(TerrainDef), typeof(ResearchProjectDef), typeof(RecipeDef), typeof(WeatherDef), typeof(GameConditionDef), typeof(IncidentDef) })
                    {
                        target = GenDefDatabase.GetDefSilentFail(t, a.to, false);
                        if (target != null)
                        {
                            type = t;
                            break;
                        }
                    }
                    string got = type == null ? null : BackCompatibility.BackCompatibleDefName(type, a.from);
                    bool pass = type != null && got == a.to;
                    if (type == typeof(TerrainDef))
                    {
                        TerrainDef viaHash = BackCompatibility.BackCompatibleTerrainWithShortHash((ushort)(GenText.StableStringHash(a.from) % 65535));
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
