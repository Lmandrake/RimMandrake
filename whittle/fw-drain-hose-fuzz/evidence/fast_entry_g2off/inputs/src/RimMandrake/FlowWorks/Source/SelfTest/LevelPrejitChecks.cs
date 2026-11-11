// LEVELLING_TICK_DIAGNOSE_DRY_GC_SPIKE: the first levelling cycle after a cold launch cost 28.8 ms live, against 2.4 ms for
// the same cycle on a reload in a warm process: the runtime compiling the cycle's call graph on first call. RM_Prejit.cs
// compiles it at start-up. These checks hold the helper (every concrete method of a root and its nested closure classes is
// compiled, open generics and abstracts are skipped, a closed instantiation can be named, nothing throws) and hold the
// start-up root list in RM_Levelling.cs to the types that file calls (a SOURCE TEXT guard: a new callee left out of the
// list fails here instead of quietly coming back as a first-cycle spike).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LevelPrejitChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private abstract class Base
        {
            public abstract int Abs();
            public int Concrete() => 1;
        }

        private sealed class Target : Base
        {
            private int k;
            public Target() { k = 2; }
            public override int Abs() => k;
            public int Closure(int x)
            {
                Func<int, int> f = y => y + x + k;   // a <>c__DisplayClass nested type
                return f(1);
            }
            public IEnumerable<int> Iter() { yield return k; }   // an iterator nested type
            public T Open<T>(T t) => t;              // open generic method: skipped
            private sealed class Inner<U> { public U Get(U u) => u; }   // open generic type: skipped
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("LEVELPREJIT_compiles_concrete_methods_and_closures_skips_open_generics", () =>
            {
                RM_Prejit.Result r = RM_Prejit.Run(new[] { typeof(Target) });
                Assert(r.Failed == 0, "failures: " + r.Failed + " first " + r.FirstFailure);
                // Target + display class + iterator class + Inner<U> at least
                Assert(r.Types >= 4, "nested types not walked: " + r.Types);
                // Target: ctor, Abs, Closure, Iter, plus closure body, iterator MoveNext etc.
                Assert(r.Compiled >= 6, "too few compiled: " + r.Compiled);
                // Open<T> and Inner<U>'s members
                Assert(r.Skipped >= 2, "open generics not skipped: " + r.Skipped);
                Assert(r.Ms >= 0, "time not measured");
            });

            Case("LEVELPREJIT_abstract_skipped_closed_instantiation_compiled_null_safe", () =>
            {
                RM_Prejit.Result b = RM_Prejit.Run(new[] { typeof(Base) });
                Assert(b.Failed == 0 && b.Skipped >= 1 && b.Compiled >= 1, "abstract base: " + b.Compiled + "/" + b.Skipped + "/" + b.Failed);
                var open = typeof(Target).GetMethod("Open");
                Assert(!RM_Prejit.Compilable(open), "open generic method called compilable");
                var closed = open.MakeGenericMethod(typeof(long));
                Assert(RM_Prejit.Compilable(closed), "closed instantiation not compilable");
                RM_Prejit.Result c = RM_Prejit.Run(Array.Empty<Type>(), new System.Reflection.MethodBase[] { closed, null });
                Assert(c.Failed == 0 && c.Compiled == 1, "closed instantiation: " + c.Compiled + "/" + c.Failed);
                RM_Prejit.Result n = RM_Prejit.Run(null, null);
                Assert(n.Compiled == 0 && n.Failed == 0 && n.FirstFailure == "", "null input");
            });

            Case("LEVELPREJIT_startup_roots_cover_every_type_RM_Levelling_calls", () =>
            {
                string src = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_Levelling.cs"));
                int at = src.IndexOf("class RM_LevellingPrejit", StringComparison.Ordinal);
                Assert(at > 0, "RM_LevellingPrejit missing");
                Assert(src.Contains("[StaticConstructorOnStartup] public static class RM_LevellingPrejit"), "not run at start-up");   // Src collapses whitespace
                string body = src.Substring(0, at), boot = src.Substring(at);
                var rooted = new HashSet<string>(Regex.Matches(boot, @"typeof\((RM_\w+)\)").Cast<Match>().Select(m => m.Groups[1].Value));
                // enums and settings fields hold no code on the cycle's path; the helper and the class itself need no root
                var exempt = new HashSet<string> { "RM_LevelLinkState", "RM_FreeEndRole", "RM_HoseSettings", "RM_Prejit", "RM_LevellingPrejit" };
                // a static call (RM_X.) or a construction (new RM_X): both run that type's code on the cycle
                var called = Regex.Matches(body, @"\b(RM_\w+)\.|\bnew (RM_\w+)\b").Cast<Match>()
                    .Select(m => m.Groups[1].Success ? m.Groups[1].Value : m.Groups[2].Value).Where(t => !exempt.Contains(t)).Distinct().ToList();
                Assert(called.Count >= 10, "source scan sees too little: " + called.Count);
                var missing = called.Where(t => !rooted.Contains(t)).ToList();
                Assert(missing.Count == 0, "called but not pre-compiled: " + string.Join(",", missing));
                // the roots listed must be the roots passed: the start-up call hands Run the list the scan read
                Assert(Regex.IsMatch(boot, @"var roots = new System\.Type\[\] \{[^}]*\}; .*Last = RM_Prejit\.Run\(roots, extra\);"), "the root list is not what Run gets");
                Assert(Regex.IsMatch(boot, @"MakeGenericMethod\(typeof\(RM_MapComponent_Excavation\.LevelRunGrid\)\)"), "walk instantiation not named");
            });
        }
    }
}
