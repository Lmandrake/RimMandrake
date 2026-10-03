// JawaBenchCompanionProbeTools.cs - BELT_COMPANION_PROBE_TOOLS_1.
//
// Three read/drive tools that exist so a mod's first script can observe state the
// stock bridge cannot reach (round 6 of the 2026-10-03 belt left these checks
// UNMEASURED): a private/inner comp field (RM_CompKethrelShell.stage / LoadKg), a
// pure static helper (RM_ZennaqLightning.Redirect), and Thing.AmbientTemperature
// on a pawn (the Pyrelands furnace-warmth postfix is invisible to cell_temperature
// because it patches the PAWN-level getter).
//
// Mod settings: jawa/mod_settings_field (JawaBenchModSettingsFieldTools.cs) already
// gets and sets any static OR instance settings field by type name. Not duplicated.
//
// THREAD AFFINITY: everything touching a Map/Thing runs inside ctx.MainThread.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private static Thing ProbeFindThing(string idOrDef, out string how)
        {
            how = null;
            if (string.IsNullOrEmpty(idOrDef)) return null;
            foreach (Map m in Find.Maps)
            {
                List<Thing> all = m.listerThings.AllThings;
                for (int i = 0; i < all.Count; i++)
                {
                    if (all[i].ThingID == idOrDef) { how = "ThingID"; return all[i]; }
                }
            }
            foreach (Map m in Find.Maps)
            {
                // a pawn of that kind/def, first spawned one (colonists are not preferred)
                foreach (Pawn p in m.mapPawns.AllPawnsSpawned)
                {
                    if (p.def.defName == idOrDef || (p.kindDef != null && p.kindDef.defName == idOrDef))
                    { how = "first pawn of def/kind"; return p; }
                }
                ThingDef td = DefDatabase<ThingDef>.GetNamedSilentFail(idOrDef);
                if (td != null)
                {
                    List<Thing> l = m.listerThings.ThingsOfDef(td);
                    if (l.Count > 0) { how = "first thing of def"; return l[0]; }
                }
            }
            return null;
        }

        private static string ProbeRender(object v, int depth = 0)
        {
            if (v == null) return "null";
            if (v is string s) return s;
            Type t = v.GetType();
            if (t.IsPrimitive || t.IsEnum || v is decimal) return Convert.ToString(v, CultureInfo.InvariantCulture);
            if (v is Def d) return t.Name + ":" + d.defName;
            if (v is Thing th) return th.ThingID;
            if (v is IntVec3 c) return c.ToString();
            if (v is IEnumerable en && depth < 1)
            {
                var parts = new List<string>();
                int n = 0;
                foreach (object o in en) { if (n++ < 12) parts.Add(ProbeRender(o, depth + 1)); }
                return "[" + string.Join(", ", parts) + "]" + (n > 12 ? " (" + n + " total)" : "");
            }
            return v.ToString();
        }

        [Tool(
            "jawa/comp_read",
            Description =
                "Reflectively read a ThingComp on a live thing, INCLUDING private fields and non-indexer " +
                "properties. thing = a ThingID (e.g. 'Kethrel123') or a ThingDef/PawnKindDef defName " +
                "(first spawned match on any map). comp = a substring of the comp's type name (e.g. " +
                "'KethrelShell'); an ambiguous substring is refused with the candidates. members = " +
                "comma list of field/property names to read; blank reads EVERY instance field. " +
                "Collections render as a count plus the first 12 entries (ThingOwner counts its held " +
                "things). READ-ONLY. A member that does not exist is reported under missing[], never " +
                "silently dropped.",
            ResultDescription = "success, thing, resolvedBy, compType, values{name:text}, missing[], ticksGame.")]
        public static async Task<object> CompRead(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID or defName.")] string thing,
            [ToolParameter(Description = "Substring of the comp type name.")] string comp,
            [ToolParameter(Description = "Comma list of members; blank = all instance fields.")] string members = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.ProgramState != ProgramState.Playing) return Fail("Not in a loaded game.");
                Thing t = ProbeFindThing(thing, out string how);
                if (t == null) return Fail("No thing matched '" + thing + "'.");
                if (!(t is ThingWithComps twc)) return Fail(t.ThingID + " is not ThingWithComps.");
                var hits = twc.AllComps.Where(x => x.GetType().Name.IndexOf(comp ?? "", StringComparison.OrdinalIgnoreCase) >= 0).ToList();
                if (hits.Count == 0) return Fail("No comp matches '" + comp + "'.", new { comps = twc.AllComps.Select(x => x.GetType().Name).ToList() });
                if (hits.Count > 1) return Fail("Ambiguous comp substring.", new { candidates = hits.Select(x => x.GetType().Name).ToList() });
                object c = hits[0];
                Type ct = c.GetType();
                const BindingFlags F = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.FlattenHierarchy;
                var values = new Dictionary<string, string>();
                var missing = new List<string>();
                if (string.IsNullOrWhiteSpace(members))
                {
                    for (Type tt = ct; tt != null && tt != typeof(ThingComp) && tt != typeof(object); tt = tt.BaseType)
                        foreach (FieldInfo fi in tt.GetFields(F | BindingFlags.DeclaredOnly))
                            if (!values.ContainsKey(fi.Name))
                            {
                                try { values[fi.Name] = ProbeRenderOwner(fi.GetValue(c)); }
                                catch (Exception e) { values[fi.Name] = "ERR " + e.GetType().Name; }
                            }
                }
                else
                {
                    foreach (string raw in members.Split(','))
                    {
                        string name = raw.Trim();
                        if (name.Length == 0) continue;
                        FieldInfo fi = null;
                        for (Type tt = ct; tt != null && fi == null; tt = tt.BaseType) fi = tt.GetField(name, F | BindingFlags.DeclaredOnly);
                        PropertyInfo pi = fi == null ? ct.GetProperty(name, F) : null;
                        try
                        {
                            if (fi != null) values[name] = ProbeRenderOwner(fi.GetValue(c));
                            else if (pi != null && pi.GetIndexParameters().Length == 0 && pi.CanRead) values[name] = ProbeRenderOwner(pi.GetValue(c));
                            else missing.Add(name);
                        }
                        catch (Exception e) { values[name] = "ERR " + (e.InnerException ?? e).GetType().Name + ": " + (e.InnerException ?? e).Message; }
                    }
                }
                return (object)new { success = true, thing = t.ThingID, resolvedBy = how, compType = ct.FullName, values, missing, ticksGame = TicksGameSafe() };
            });
        }

        private static string ProbeRenderOwner(object v)
        {
            if (v is ThingOwner o) return "ThingOwner count=" + o.Count + " [" + string.Join(", ", o.Take(12).Select(x => x.ThingID + "x" + x.stackCount)) + "]";
            return ProbeRender(v);
        }

        [Tool(
            "jawa/thing_ambient_temp",
            Description =
                "Read Thing.AmbientTemperature (the PAWN-level getter that postfix mods patch - " +
                "jawa/cell_temperature reads the map grid and cannot see such a patch) beside the raw " +
                "grid values it is derived from: the cell's room/grid temperature and the map outdoor " +
                "temperature. A difference between ambient and cellTemp IS the patched contribution. " +
                "thing = ThingID or defName (first spawned match). READ-ONLY.",
            ResultDescription = "success, thing, cell, ambient, cellTemp, cellTempOk, outdoor, delta (ambient - cellTemp), ticksGame.")]
        public static async Task<object> ThingAmbientTemp(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID or defName.")] string thing)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.ProgramState != ProgramState.Playing) return Fail("Not in a loaded game.");
                Thing t = ProbeFindThing(thing, out string how);
                if (t == null) return Fail("No thing matched '" + thing + "'.");
                if (!t.Spawned || t.Map == null) return Fail(t.ThingID + " is not spawned.");
                float ambient = t.AmbientTemperature;
                bool ok = GenTemperature.TryGetTemperatureForCell(t.Position, t.Map, out float cellTemp);
                float outdoor = t.Map.mapTemperature.OutdoorTemp;
                return (object)new
                {
                    success = true, thing = t.ThingID, resolvedBy = how, cell = t.Position.ToString(),
                    ambient, cellTemp, cellTempOk = ok, outdoor, delta = ambient - cellTemp, ticksGame = TicksGameSafe(),
                };
            });
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/static_call",
            Description =
                "Invoke a PUBLIC STATIC method by type FullName + method name, for pure helpers a mod " +
                "script needs to exercise (e.g. RM_ZennaqLightning.Redirect). args = '|'-separated, " +
                "coerced by the parameter type: int/float/bool/string, IntVec3 as 'x,y,z' (or 'x,z'), " +
                "Map as 'current' or a map index, ThingDef/any Def by defName. Instance methods and " +
                "overload ambiguity are REFUSED with the candidate signatures. The return value is " +
                "rendered as text. Runs on the main thread. GM-gated: it can call anything public.",
            ResultDescription = "success, method (signature), result, ticksGame.")]
        public static async Task<object> StaticCall(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Type.FullName, exact.")] string type,
            [ToolParameter(Description = "Method name.")] string method,
            [ToolParameter(Description = "'|'-separated arguments.")] string args = "")
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Type ty = AppDomain.CurrentDomain.GetAssemblies()
                    .Select(a => { try { return a.GetType(type, false); } catch { return null; } })
                    .FirstOrDefault(x => x != null);
                if (ty == null) return Fail("Type not found: " + type);
                string[] raw = string.IsNullOrEmpty(args) ? new string[0] : args.Split('|');
                var cands = ty.GetMethods(BindingFlags.Public | BindingFlags.Static)
                    .Where(m => m.Name == method && m.GetParameters().Length == raw.Length).ToList();
                if (cands.Count == 0) return Fail("No public static " + method + " with " + raw.Length + " params.",
                    new { available = ty.GetMethods(BindingFlags.Public | BindingFlags.Static).Where(m => m.Name == method).Select(m => m.ToString()).ToList() });
                if (cands.Count > 1) return Fail("Ambiguous overloads.", new { candidates = cands.Select(m => m.ToString()).ToList() });
                MethodInfo mi = cands[0];
                var ps = mi.GetParameters();
                var vals = new object[ps.Length];
                for (int i = 0; i < ps.Length; i++)
                {
                    string a = raw[i].Trim();
                    Type pt = ps[i].ParameterType;
                    try
                    {
                        if (pt == typeof(int)) vals[i] = int.Parse(a, CultureInfo.InvariantCulture);
                        else if (pt == typeof(float)) vals[i] = float.Parse(a, CultureInfo.InvariantCulture);
                        else if (pt == typeof(bool)) vals[i] = bool.Parse(a);
                        else if (pt == typeof(string)) vals[i] = a;
                        else if (pt == typeof(IntVec3))
                        {
                            string[] z = a.Split(',');
                            vals[i] = z.Length == 2 ? new IntVec3(int.Parse(z[0]), 0, int.Parse(z[1])) : new IntVec3(int.Parse(z[0]), int.Parse(z[1]), int.Parse(z[2]));
                        }
                        else if (pt == typeof(Map))
                        {
                            vals[i] = a == "current" ? Find.CurrentMap : Find.Maps[int.Parse(a)];
                            if (vals[i] == null) return Fail("No map for argument " + i);
                        }
                        else if (typeof(Def).IsAssignableFrom(pt))
                        {
                            if (a.Length == 0 || a == "null") { vals[i] = null; }
                            else
                            {
                                vals[i] = GenDefDatabase.GetDef(pt, a, false);
                                if (vals[i] == null) return Fail("No " + pt.Name + " named '" + a + "'.");
                            }
                        }
                        else return Fail("Unsupported parameter type " + pt.Name + " (arg " + i + ").");
                    }
                    catch (Exception e) { return Fail("Cannot coerce arg " + i + " '" + a + "' to " + pt.Name + ": " + e.Message); }
                }
                try
                {
                    object r = mi.Invoke(null, vals);
                    return (object)new { success = true, method = mi.ToString(), result = ProbeRender(r), ticksGame = TicksGameSafe() };
                }
                catch (Exception e)
                {
                    Exception inner = e.InnerException ?? e;
                    return Fail("Invoke threw " + inner.GetType().Name + ": " + inner.Message);
                }
            });
        }
#endif
    }
}
