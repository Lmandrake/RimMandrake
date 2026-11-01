// Explicit placement lists adapter (PLASTEEL_AUDIT_EXPLICIT_MINEABLE_LISTS). The policy zeroes a disabled mineable's scatter and
// deep weights, but several defs name mineables in a list of their own and never read those weights: Core GenStepDef PreciousLump
// (GenStep_PreciousLump.mineables), the VGE and Deep Orbit asteroid GenSteps (mineableCounts), their GeneratedLocationDefs
// (preciousResources), Odyssey / Deep Orbit QuestNode_Root_Asteroid.mineables, and GenStep_ScatterGroup things
// (KOTOR_JunkPileClusters). Canon (minerals design, 2026-09-25 / 2026-10-09): components and plasteel are never mined from rock.
// This drops every registry-disabled mineable from those lists, from the list as first seen, so a settings change or the
// master toggle restores them. Found by reflection, so no donor mod is referenced; a list it would empty is kept whole.
// NOT touched here: StructureLayoutDef grids (authored ruins: Ancient mining industry) - RM_MineralLayoutGrids.cs swaps those to steel.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimWorld;
using Verse;

namespace RimMandrake.Minerals
{
    public static class RM_MineralExplicitLists
    {
        private sealed class Target
        {
            public string Where;
            public IList Live;
            public List<object> Original;      // the list as first seen, plus entries another mod added after our last write
            public List<object> LastWritten;
            public ListPrune Last;
        }

        private const BindingFlags Fields = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
        private static readonly Dictionary<Type, FieldInfo[]> fieldCache = new Dictionary<Type, FieldInfo[]>();
        private static readonly Dictionary<Type, FieldInfo[]> thingFieldCache = new Dictionary<Type, FieldInfo[]>();
        private static List<Target> targets;

        public static string LastReason { get; private set; } = "never applied";
        public static int TargetCount => targets?.Count ?? 0;

        public static bool IsMineable(ThingDef t) { return t != null && t.building != null && t.building.mineableThing != null; }

        private static bool IsMineable(string defName) { return IsMineable(DefDatabase<ThingDef>.GetNamedSilentFail(defName)); }

        public static void Refresh(IEnumerable<PolicyDecision> decisions, string why)
        {
            if (targets == null) targets = Scan();
            HashSet<string> disabled = RM_MineralsSettings.enabled ? RM_ExplicitListKernel.Disabled(decisions, IsMineable) : new HashSet<string>();
            int dropped = 0, lists = 0;
            var fell = new List<string>();
            bool changed = false;
            foreach (Target t in targets)
            {
                if (t.LastWritten != null)
                    foreach (object o in t.Live) if (o != null && !t.LastWritten.Contains(o) && !t.Original.Contains(o)) t.Original.Add(o);
                ListPrune p = RM_ExplicitListKernel.Prune(t.Original.Select(Names).ToList(), disabled);
                t.Live.Clear();
                foreach (int k in p.Keep) t.Live.Add(t.Original[k]);
                t.LastWritten = t.Live.Cast<object>().ToList();
                if (t.Last == null || !t.Last.Keep.SequenceEqual(p.Keep)) changed = true;
                t.Last = p;
                if (p.Dropped.Count > 0) { lists++; dropped += p.Dropped.Count; }
                if (p.FellBack) fell.Add(t.Where);
            }
            LastReason = why;
            if (fell.Count > 0)
                Log.Warning("[RM Minerals] explicit mineable lists (" + why + "): " + fell.Count + " list(s) name only disabled mineables and are "
                          + "kept whole so their map or quest still generates: " + string.Join(", ", fell));
            if (changed)
                Log.Message("[RM Minerals] explicit mineable lists (" + why + "): " + targets.Count + " lists seen, "
                          + (RM_MineralsSettings.enabled ? dropped + " entries dropped from " + lists + " (" + string.Join(", ", disabled.OrderBy(x => x)) + ")"
                                                         : "master toggle OFF, every list restored"));
        }

        /// <summary>The defNames one list entry carries: a ThingDef itself, or the ThingDef fields of a config object.</summary>
        private static IList<string> Names(object o)
        {
            if (o is ThingDef td) return new[] { td.defName };
            var outList = new List<string>();
            if (o == null) return outList;
            foreach (FieldInfo f in ThingFields(o.GetType()))
                if (f.GetValue(o) is ThingDef t) outList.Add(t.defName);
            return outList;
        }

        private static FieldInfo[] ThingFields(Type ty)
        {
            if (!thingFieldCache.TryGetValue(ty, out FieldInfo[] fs))
                thingFieldCache[ty] = fs = ty.GetFields(Fields).Where(f => typeof(ThingDef).IsAssignableFrom(f.FieldType)).ToArray();
            return fs;
        }

        private static FieldInfo[] WalkFields(Type ty)
        {
            if (!fieldCache.TryGetValue(ty, out FieldInfo[] fs))
                fieldCache[ty] = fs = ty.GetFields(Fields).Where(f => !Skipped(f.FieldType)).ToArray();
            return fs;
        }

        private static bool Skipped(Type ty)
        {
            return ty.IsValueType || ty == typeof(string) || ty.IsArray || typeof(Def).IsAssignableFrom(ty) || typeof(Type).IsAssignableFrom(ty)
                || typeof(Delegate).IsAssignableFrom(ty) || typeof(UnityEngine.Object).IsAssignableFrom(ty) || typeof(IDictionary).IsAssignableFrom(ty);
        }

        // Recurse only into the mod-side object graph: never a mod's own bookkeeping (ModContentPack -> patches -> XmlNodes) or a
        // System type (XmlNode is IEnumerable but no list), which would turn a GenStep scan into a walk of the whole load.
        private static bool Recursable(Type ty)
        {
            return !Skipped(ty) && !typeof(ModContentPack).IsAssignableFrom(ty) && !typeof(IEnumerable).IsAssignableFrom(ty)
                && !(ty.Namespace ?? "").StartsWith("System") && !(ty.Namespace ?? "").StartsWith("UnityEngine");
        }

        private static List<Target> Scan()
        {
            var found = new List<Target>();
            var seen = new HashSet<object>();
            foreach (Type defType in GenDefDatabase.AllDefTypesWithDatabases())
            {
                // GenSteps and quest trees hold their lists a few objects down; every other def type is read one level deep only
                bool deep = typeof(GenStepDef).IsAssignableFrom(defType) || typeof(QuestScriptDef).IsAssignableFrom(defType);
                foreach (Def d in GenDefDatabase.GetAllDefsInDatabaseForDef(defType))
                {
                    if (d == null) continue;
                    try { Walk(d, defType.Name + " " + d.defName, deep ? 6 : 0, seen, found); }
                    catch (Exception e) { Log.Warning("[RM Minerals] explicit mineable lists: could not read " + d.defName + ": " + e.Message); }
                }
            }
            return found;
        }

        private static void Walk(object o, string where, int depthLeft, HashSet<object> seen, List<Target> found)
        {
            if (o == null || !seen.Add(o)) return;
            foreach (FieldInfo f in WalkFields(o.GetType()))
            {
                object v = f.GetValue(o);
                if (v == null) continue;
                string at = where + "." + f.Name;
                if (v is IList list)
                {
                    Type ty = v.GetType();
                    if (!ty.IsGenericType || !seen.Add(v)) continue;
                    Type et = ty.GetGenericArguments()[0];
                    if (typeof(ThingDef).IsAssignableFrom(et) || ThingFields(et).Length > 0)
                    {
                        bool hasMineable = false;
                        foreach (object e in list) if (Names(e).Any(IsMineable)) { hasMineable = true; break; }
                        if (hasMineable) found.Add(new Target { Where = at, Live = list, Original = list.Cast<object>().ToList() });
                    }
                    if (depthLeft > 0 && Recursable(et))
                    {
                        int i = 0;
                        foreach (object e in list) Walk(e, at + "[" + i++ + "]", depthLeft - 1, seen, found);
                    }
                }
                else if (depthLeft > 0 && Recursable(v.GetType())) Walk(v, at, depthLeft - 1, seen, found);
            }
        }

        /// <summary>"lists=N;reason=..;&lt;where&gt;=kept1,kept2|dropped=..;..." for every list whose path contains a ';'-separated filter
        /// term (empty = every list). Bridge proof hook for Minerals/validation.py (jawa/static_call); reads, never writes.</summary>
        public static string ProofState(string filter)
        {
            var terms = (filter ?? "").Split(';').Select(x => x.Trim()).Where(x => x.Length > 0).ToList();
            var sb = new System.Text.StringBuilder();
            sb.Append("lists=").Append(TargetCount).Append(";reason=").Append(LastReason);
            if (targets == null) return sb.ToString();
            foreach (Target t in targets)
            {
                if (terms.Count > 0 && !terms.Any(x => t.Where.Contains(x))) continue;
                sb.Append(';').Append(t.Where).Append('=').Append(string.Join(",", t.Live.Cast<object>().Select(o => string.Join("+", Names(o)))));
                if (t.Last != null && t.Last.Dropped.Count > 0) sb.Append("|dropped=").Append(string.Join(",", t.Last.Dropped));
                if (t.Last != null && t.Last.FellBack) sb.Append("|fellback");
            }
            return sb.ToString();
        }
    }
}
