// C# unit group for the TPS record (BRIDGE_TPS_REVIEW2_FIXES_1). Runs against the PRODUCTION files the
// companion compiles (JawaBenchTpsMath.cs, JawaBenchTpsWriter.cs, JawaBenchTpsWatchdog.cs, ...), never a
// copy. Driven by the `U` line of selftest_tps_record.py; every test prints one line
//     U <name> ok          or          U <name> FAIL <why>
// and `J <name> <json line>` lines carry production-composed record lines for the Python side to parse
// strictly (duplicate keys rejected).
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static readonly List<Action> All = new List<Action>();
        private static string _cur;
        private static readonly List<string> Fails = new List<string>();

        internal static void Check(bool cond, string why)
        {
            if (!cond) Fails.Add(why);
        }

        internal static string TempDir()
        {
            string d = Path.Combine(Path.GetTempPath(), "tpsunit_" + Guid.NewGuid().ToString("N").Substring(0, 8));
            Directory.CreateDirectory(d);
            return d;
        }

        internal static void Emit(string name, string jsonLine)
        {
            Console.WriteLine("J " + name + " " + jsonLine);
        }

        internal static void Run()
        {
            var tests = typeof(Units).GetMethods(System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic)
                .Where(m => m.Name.StartsWith("T_", StringComparison.Ordinal) && m.GetParameters().Length == 0)
                .OrderBy(m => m.Name, StringComparer.Ordinal).ToList();
            foreach (var m in tests)
            {
                _cur = m.Name.Substring(2);
                Fails.Clear();
                try { m.Invoke(null, null); }
                catch (Exception e)
                {
                    var ie = e is System.Reflection.TargetInvocationException && e.InnerException != null ? e.InnerException : e;
                    Fails.Add("threw " + ie.GetType().Name + ": " + ie.Message);
                }
                Console.WriteLine("U " + _cur + (Fails.Count == 0 ? " ok" : " FAIL " + string.Join(" | ", Fails).Replace("\n", " ")));
            }
            Console.WriteLine("U-count " + tests.Count);
        }
    }
}
