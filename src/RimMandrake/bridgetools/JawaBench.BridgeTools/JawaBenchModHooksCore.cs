// JawaBenchModHooksCore.cs - the mods' test hooks, found by reflection: the PURE half (no Verse, no Unity, no Harmony).
// Item RIMMANDRAKE_BUILD_MOD_TRACE_AND_RESET_HOOKS_BY_REFLECTION. Page: design/specs/2026-11-23-bridge-v2-mod-hooks/boundary.md.
// The mod side is src/RimMandrake/_Shared/TestHooks/RMTestHooks.cs, compiled into each mod as its own internal copy. This file
// finds that copy by TYPE NAME in every loaded assembly, so neither side references the other.
//
//   discovery  every assembly whose name starts with RimMandrake, or that holds the shared file's types: its build (PROOF |
//              RELEASE), its trace sink, its [RMReset] and [RMDigest] hooks, and each problem by name.
//   the run    Armed: each mod's RMTrace.Sink writes a `mod` record into the run's trace. Ended: every sink is null again. The
//              run's End calls Ended on every end state, a thrown tick included (JawaBenchSceneTickCore.SceneRun.End).
//   digest     accepted only after it was seen to DIFFER between a clean state and a state dirtied on purpose: a digest that
//              answers a constant could never tell a reset from no reset.
//   admit      an acceptance run refuses a hook of a PROOF build, or of a build that does not say which it is.
//
// Compiled into bridgetools/TestHooksSelfTest as well: a `using Verse;` here breaks that build, which is the guard rail.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using T = JawaBench.BridgeTools.JawaBenchSceneTickCore;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchModHooksCore
    {
        internal const string Ns = "RimMandrake.Shared.TestHooks";
        internal const string TraceType = Ns + ".RMTrace", BuildType = Ns + ".RMTestHooksBuild";
        internal const string ResetAttr = "RMResetAttribute", DigestAttr = "RMDigestAttribute";
        internal const string NamePrefix = "RimMandrake";
        internal const int Contract = 1;                      // RMTestHooksBuild.Contract that this file knows
        internal const string Shape = "public static string M(string scope)";

        /// <summary>One loaded mod assembly and what it offers.</summary>
        internal sealed class Mod
        {
            public string Name;                               // the assembly's simple name: the key
            public Assembly Asm;
            public string Build = "none";                     // PROOF | RELEASE | none (no shared file) | unknown
            public FieldInfo Sink;                            // null: no trace point
            public MethodInfo Reset, Digest;                  // null: none, or the one found was the wrong shape
            public readonly List<string> Problems = new List<string>();
            // the digest's proof: the digest read clean, then read after the caller dirtied the state on purpose
            public string Clean, Dirty, ProofWhy = "not tried";
            public bool Proven, CleanRead;                    // CleanRead: a clean read waits for its dirty read
            public bool HasHooks { get { return Sink != null || Reset != null || Digest != null; } }

            public Dictionary<string, object> Row()
            {
                return new Dictionary<string, object>
                {
                    { "mod", Name }, { "build", Build },
                    { "trace", Sink != null ? "yes" : "no trace point" },
                    { "reset", Reset != null ? Reset.DeclaringType.FullName + "." + Reset.Name : "no reset hook" },
                    { "digest", Digest != null ? Digest.DeclaringType.FullName + "." + Digest.Name : "no digest hook" },
                    { "digestProven", Proven }, { "digestProof", ProofWhy },
                    { "problems", new List<object>(Problems) },
                };
            }
        }

        // ============================================================================================ discovery
        /// <summary>Our mods among these assemblies, in name order. An assembly that is not ours is not listed.</summary>
        internal static List<Mod> Discover(IEnumerable<Assembly> assemblies)
        {
            var outl = new List<Mod>();
            var seen = new Dictionary<string, Mod>(StringComparer.OrdinalIgnoreCase);
            foreach (var asm in assemblies)
            {
                if (asm == null || asm.IsDynamic) continue;
                string name;
                Type build, trace;
                try
                {
                    name = asm.GetName().Name;
                    build = asm.GetType(BuildType, false);
                    trace = asm.GetType(TraceType, false);
                }
                catch (Exception) { continue; }               // an assembly that cannot say its name or types is not one of ours
                if (build == null && trace == null && !name.StartsWith(NamePrefix, StringComparison.Ordinal)) continue;
                var m = new Mod { Name = name, Asm = asm };
                Mod twin;
                if (seen.TryGetValue(name, out twin))
                {
                    m.Name = name + "#" + (outl.Count(x => x.Asm.GetName().Name == name) + 1);
                    m.Problems.Add("two loaded assemblies are named " + name + ": this one is listed as " + m.Name);
                }
                else seen[name] = m;
                Read(m, build, trace);
                outl.Add(m);
            }
            outl.Sort((a, b) => string.CompareOrdinal(a.Name, b.Name));
            return outl;
        }

        static void Read(Mod m, Type build, Type trace)
        {
            if (build == null && trace == null) return;       // a mod with no hook: Build stays "none"
            if (build == null) { m.Build = "unknown"; m.Problems.Add(BuildType + " is missing: the build cannot say if it is PROOF or RELEASE"); }
            else
            {
                m.Build = ConstText(build, "Kind") ?? "unknown";
                if (m.Build != "PROOF" && m.Build != "RELEASE") { m.Problems.Add("RMTestHooksBuild.Kind is '" + m.Build + "', not PROOF or RELEASE"); m.Build = "unknown"; }
                string c = ConstText(build, "Contract");
                if (c != Contract.ToString()) m.Problems.Add("RMTestHooksBuild.Contract is " + (c ?? "missing") + "; this companion knows " + Contract + ": build the mod against the shared file of this commit");
            }
            if (trace != null)
            {
                var f = trace.GetField("Sink", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
                if (f == null) m.Problems.Add("RMTrace has no static field Sink");
                else if (f.FieldType != typeof(Action<string, string, string>)) m.Problems.Add("RMTrace.Sink is a " + f.FieldType.FullName + ", not an Action<string, string, string>");
                else if (f.IsInitOnly || f.IsLiteral) m.Problems.Add("RMTrace.Sink is read-only");
                else m.Sink = f;
            }
            Type[] types;
            try { types = m.Asm.GetTypes(); }
            catch (ReflectionTypeLoadException e)
            {
                types = e.Types.Where(t => t != null).ToArray();
                m.Problems.Add("some types of " + m.Name + " did not load (" + e.LoaderExceptions.Length + "): a hook in them is not seen");
            }
            const BindingFlags all = BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
            var resets = new List<MethodInfo>();
            var digests = new List<MethodInfo>();
            foreach (var t in types)
            {
                MethodInfo[] ms;
                try { ms = t.GetMethods(all); } catch (Exception) { continue; }
                foreach (var mi in ms)
                {
                    string kind = HookKind(mi);
                    if (kind == null) continue;
                    string label = (kind == ResetAttr ? "RMReset" : "RMDigest") + " on " + t.FullName + "." + mi.Name;
                    string bad = WrongShape(mi);
                    if (bad != null) { m.Problems.Add(label + ": must be " + Shape.Replace(" M(", " " + mi.Name + "(") + "; it " + bad); continue; }
                    (kind == ResetAttr ? resets : digests).Add(mi);
                }
            }
            m.Reset = One(m, "RMReset", resets);
            m.Digest = One(m, "RMDigest", digests);
        }

        static MethodInfo One(Mod m, string what, List<MethodInfo> found)
        {
            if (found.Count == 1) return found[0];
            if (found.Count > 1) m.Problems.Add("one " + what + " hook per mod; found " + found.Count + ": " + string.Join(", ", found.Select(x => x.DeclaringType.FullName + "." + x.Name)));
            return null;
        }

        static string HookKind(MethodInfo mi)
        {
            IList<CustomAttributeData> attrs;
            try { attrs = mi.GetCustomAttributesData(); } catch (Exception) { return null; }
            foreach (var a in attrs)
            {
                var at = a.AttributeType;
                if (at.Namespace == Ns && (at.Name == ResetAttr || at.Name == DigestAttr)) return at.Name;
            }
            return null;
        }

        /// <summary>Null when the method is `public static string M(string)`, else what is wrong with it.</summary>
        internal static string WrongShape(MethodInfo mi)
        {
            var p = mi.GetParameters();
            var wrong = new List<string>();
            if (!mi.IsStatic) wrong.Add("is not static");
            if (!mi.IsPublic) wrong.Add("is not public");
            if (mi.ContainsGenericParameters) wrong.Add("is generic");
            if (mi.ReturnType != typeof(string)) wrong.Add("returns " + mi.ReturnType.Name);
            if (p.Length != 1 || p[0].ParameterType != typeof(string)) wrong.Add("takes (" + string.Join(", ", p.Select(x => x.ParameterType.Name)) + ")");
            return wrong.Count == 0 ? null : string.Join(", ", wrong);
        }

        static string ConstText(Type t, string field)
        {
            var f = t.GetField(field, BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
            if (f == null) return null;
            try { var v = f.IsLiteral ? f.GetRawConstantValue() : f.GetValue(null); return v == null ? null : Convert.ToString(v, System.Globalization.CultureInfo.InvariantCulture); }
            catch (Exception) { return null; }
        }

        // ============================================================================================ the registry
        /// <summary>What the run sees: the mods, found once; the sinks of a run; the digest proofs. Main thread only.</summary>
        internal sealed class Registry : T.IRunWatch
        {
            readonly Func<IEnumerable<Assembly>> _source;
            List<Mod> _mods;
            readonly List<Mod> _armed = new List<Mod>();
            public long Said, Late;                           // records written; records that came when no run was live
            public int StaleAtArm;                            // sinks found set at an arm (a run that never ended)

            public Registry(Func<IEnumerable<Assembly>> source) { _source = source; }

            public IList<Mod> Mods { get { if (_mods == null) _mods = Discover(_source()); return _mods; } }
            public int Armed { get { return _armed.Count; } }

            public Mod Find(string name)
            {
                foreach (var m in Mods) if (string.Equals(m.Name, (name ?? "").Trim(), StringComparison.OrdinalIgnoreCase)) return m;
                return null;
            }

            public List<object> Rows() { return Mods.Select(m => (object)m.Row()).ToList(); }

            // -------------------------------------------------------------------------------- the run
            /// <summary>Each mod's sink says through `say(mod, name, key, value)`. Answers the number of sinks set.</summary>
            public int Arm(Action<string, string, string, string> say)
            {
                Leave();
                foreach (var m in Mods)
                {
                    if (m.Sink == null) continue;
                    if (m.Sink.GetValue(null) != null) StaleAtArm++;
                    string mod = m.Name;
                    Action<string, string, string> sink = (n, k, v) => { Said++; say(mod, n, k, v); };
                    m.Sink.SetValue(null, sink);
                    _armed.Add(m);
                }
                return _armed.Count;
            }

            /// <summary>Every sink this registry set is null again. Answers how many were cleared.</summary>
            public int Leave()
            {
                int n = 0;
                foreach (var m in _armed)
                {
                    try { m.Sink.SetValue(null, null); n++; }
                    catch (Exception) { /* a field that cannot be written now could be written at the arm: it is read back below */ }
                }
                _armed.Clear();
                foreach (var m in Mods) if (m.Sink != null && m.Sink.GetValue(null) != null) m.Sink.SetValue(null, null);
                return n;
            }

            void T.IRunWatch.Armed(T.SceneRun run, long tick)
            {
                Arm((mod, n, k, v) => { if (!run.ModSays(mod, n, k, v)) Late++; });
            }

            void T.IRunWatch.Ended(T.SceneRun run, long tick) { Leave(); }

            // -------------------------------------------------------------------------------- admit
            /// <summary>The refusals of a run of this purpose (acceptance | explore). An empty list admits it.</summary>
            public List<string> Admit(string purpose)
            {
                var outl = new List<string>();
                if (!string.Equals((purpose ?? "").Trim(), "acceptance", StringComparison.OrdinalIgnoreCase)) return outl;
                foreach (var m in Mods)
                {
                    if (!m.HasHooks && m.Build == "none") continue;
                    if (m.Build == "RELEASE") continue;
                    outl.Add("PROOF_BUILD: " + m.Name + " is a " + m.Build + " build: its hooks are not evidence for an acceptance run; deploy its RELEASE build");
                }
                return outl;
            }

            // -------------------------------------------------------------------------------- digest and reset
            /// <summary>Call one hook. Null and the answer, or the error.</summary>
            static string Call(MethodInfo mi, string scope, out string error)
            {
                error = null;
                try { return (string)mi.Invoke(null, new object[] { scope ?? "" }); }
                catch (TargetInvocationException e) { var x = e.InnerException ?? e; error = "the hook threw " + x.GetType().Name + ": " + x.Message; }
                catch (Exception e) { error = "the hook could not be called: " + e.GetType().Name + ": " + e.Message; }
                return null;
            }

            static Dictionary<string, object> No(string name, string message, string repair)
            {
                return new Dictionary<string, object> { { "success", false }, { "refused", name }, { "message", message }, { "repair", repair } };
            }

            Mod Need(string name, bool digest, out Dictionary<string, object> no)
            {
                no = null;
                var m = Find(name);
                if (m == null) { no = No("UNKNOWN_MOD", "no mod assembly is named '" + name + "'", "action=list names them"); return null; }
                if (digest && m.Digest == null) { no = No("NO_DIGEST_HOOK", m.Name + " has no digest hook", "add an [RMDigest] method to the mod (RMTestHooks.cs)"); return null; }
                return m;
            }

            /// <summary>step clean: read the digest of the clean state. step dirty: read it again after the caller dirtied the state on
            /// purpose; the digest is accepted only when the two differ.</summary>
            public Dictionary<string, object> Prove(string name, string step, string scope)
            {
                Dictionary<string, object> no;
                var m = Need(name, true, out no);
                if (m == null) return no;
                string err, d = Call(m.Digest, scope, out err);
                if (err != null) { m.Proven = false; m.CleanRead = false; m.ProofWhy = "the digest could not be read: " + err; return Answer(m); }
                switch ((step ?? "").Trim().ToLowerInvariant())
                {
                    case "clean":
                        m.Clean = d; m.Dirty = null; m.Proven = false; m.CleanRead = true;
                        m.ProofWhy = "clean read; dirty the state on purpose, then step=dirty";
                        break;
                    case "dirty":
                        if (!m.CleanRead)
                            return No("NO_CLEAN_READ", "step=dirty needs a step=clean read first, with nothing between but the dirtying", "step=clean, dirty the state, step=dirty");
                        m.Dirty = d; m.CleanRead = false;
                        if (d == null || m.Clean == null) { m.Proven = false; m.ProofWhy = "the digest answered null: it digests nothing"; }
                        else if (d == m.Clean) { m.Proven = false; m.ProofWhy = "the digest did not change when the state was dirtied ('" + Cut(d) + "' both times): it cannot tell a reset from no reset"; }
                        else { m.Proven = true; m.ProofWhy = "differs: clean '" + Cut(m.Clean) + "', dirtied '" + Cut(d) + "'"; }
                        break;
                    default:
                        return No("BAD_ARGS", "step is clean or dirty, not '" + step + "'", "correct it");
                }
                return Answer(m);
            }

            /// <summary>Call the mod's reset hook, then read its digest: `verified` when the digest is proven and equals the clean read,
            /// `differs` when it is proven and does not, `unproven` when the digest was never seen to differ (or there is none).</summary>
            public Dictionary<string, object> Reset(string name, string scope)
            {
                Dictionary<string, object> no;
                var m = Need(name, false, out no);
                if (m == null) return no;
                if (m.Reset == null) return No("NO_RESET_HOOK", m.Name + " has no reset hook", "add an [RMReset] method to the mod (RMTestHooks.cs)");
                string err, said = Call(m.Reset, scope, out err);
                var r = Answer(m);
                r["cleared"] = said;
                if (err != null) { r["success"] = false; r["refused"] = "HOOK_THREW"; r["message"] = err; r["repair"] = "fix the mod's reset hook"; r["reset"] = "failed"; return r; }
                string after = null, derr = null;
                if (m.Digest != null) after = Call(m.Digest, scope, out derr);
                r["digestAfter"] = after;
                r["reset"] = derr != null ? "unproven: the digest could not be read: " + derr
                           : !m.Proven ? "unproven: " + (m.Digest == null ? "no digest hook" : m.ProofWhy)
                           : after == m.Clean ? "verified" : "differs: clean '" + Cut(m.Clean) + "', after the reset '" + Cut(after) + "'";
                return r;
            }

            static Dictionary<string, object> Answer(Mod m)
            {
                var r = m.Row();
                r["success"] = true;
                r["clean"] = m.Clean;
                r["dirty"] = m.Dirty;
                return r;
            }

            static string Cut(string s) { return s == null ? "null" : s.Length <= 120 ? s : s.Substring(0, 120) + "..."; }
        }
    }
}
