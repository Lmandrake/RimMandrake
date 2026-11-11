using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
namespace RimMandrake.FlowWorks.SelfTest.TheftHarness
{
    internal static class TankTheftCallerChecks
    {
        // Every production stock-changing entry, including the closures run synchronously by Move/Credit.
        private static readonly (string file, string signature, string actor)[] entries = {
            ("LiquidTypes/Building_LiquidPump.cs", "private string TryDraw()", "this"),
            ("LiquidTypes/Building_LiquidPump.cs", "private string TryPour()", "this"),
            ("Machinery/CompLiquidConverter.cs", "public override void CompTickRare()", "parent"),
            ("Machinery/CompLiquidPipeAdapter.cs", "public override void CompTickRare()", "parent"),
            ("Machinery/Kits/RM_LiquidReaction.cs", "public override void CompTickRare()", "parent"),
            ("Machinery/Kits/RM_LiquidBath.cs", "public static void Postfix(Bill_Production __instance)", "__instance.billStack?.billGiver as Thing"),
            ("RM_IceMelter.cs", "public static void Postfix(Bill_Production __instance)", "__instance.billStack?.billGiver as Thing"),
            ("Thirst/Building_RM_PipeFaucet.cs", "public static bool TryPour(Thing faucet, LiquidDef liquid, int units)", "faucet"),
            ("Sprinklers/RM_Sprinkle.cs", "public static Result Pulse(ThingWithComps head, List<IntVec3> cells, bool enabled, bool switchOn)", "head"),
            ("LiquidTypes/JobDriver_FillBottleFromTank.cs", "finish.initAction = delegate", "pawn"),
            ("LiquidTypes/JobDriver_EmptyBottleIntoTank.cs", "finish.initAction = delegate", "pawn"),
            ("Thirst/RM_ThirstJobs.cs", "ToilMaker.MakeToil(\"RM_DrinkFromTank\")", "pawn"),
            ("Machinery/RM_LiquidNet.cs", "Building_LiquidTank src = tanks[si], dst = tanks[di];", "src.EffectiveMode == RM_TankMode.Empty ? src : dst"),
            ("Machinery/RM_LiquidNet.cs", "foreach (Building_LiquidTank tank in dumps.OrderBy(t => t.thingIDNumber))", "tank")
        };
        // Non-entry helpers execute synchronously under the enclosing entry's scope.
        private static readonly (string file, string signature)[] inherited = {
            ("LiquidTypes/Building_LiquidPump.cs", "private string PourToPond("),
            ("LiquidTypes/Building_LiquidPump.cs", "private string PourToOutflow("),
            ("Machinery/RM_LiquidNet.cs", "public static System.Func<int, int> FillFrom(")
        };
        private static readonly (string file, string signature)[] setup = {
            ("RM_NorthstarProofs.cs", "public static string ProofTank("),
            ("Hose/HoseNetProbe.cs", "public static string TryRun("),
            ("Machinery/RM_LiquidWorksRuins.cs", "public override void PostSpawnSetup(")
        };
        private static (int start, int end) Body(string source, string signature)
        {
            int a = source.IndexOf(signature, StringComparison.Ordinal);
            if (a < 0) throw new Exception("missing caller boundary " + signature);
            // The settle's source/destination declaration is already inside the per-move block.
            if (signature.StartsWith("Building_LiquidTank src")) a = source.LastIndexOf('{', a);
            int open = source.IndexOf('{', a + (signature.StartsWith("Building_LiquidTank src") ? 0 : signature.Length));
            int depth = 0;
            for (int i = open; i < source.Length && open >= 0; i++)
            {
                if (source[i] == '{') depth++;
                else if (source[i] == '}' && --depth == 0) return (a, i+1);
            }
            throw new Exception("unbalanced caller " + signature);
        }
        private static List<string> Lint(Dictionary<string,string> files)
        {
            var allowed = new Dictionary<string,List<(int start,int end)>>();
            var bad = new List<string>();
            foreach (var e in entries)
            {
                string s = files[e.file]; var span = Body(s, e.signature);
                string b = s.Substring(span.start, span.end-span.start);
                string expected = "using var theftActor = " + (e.file.StartsWith("LiquidTypes/JobDriver") || e.file == "Thirst/RM_ThirstJobs.cs" ? "Machinery." : "") + "RM_LiquidTheft.As(" + e.actor + ");";
                // Most entries use a full namespace to make their source dependency explicit.
                string full = "using var theftActor = RimMandrake.FlowWorks.Machinery.RM_LiquidTheft.As(" + e.actor + ");";
                int scope = Math.Max(b.IndexOf(expected, StringComparison.Ordinal), b.IndexOf(full, StringComparison.Ordinal));
                var mutation = Regex.Match(b, @"\.Try(?:Add|Remove)Liquid\(");
                if (scope < 0 || mutation.Success && scope > mutation.Index) bad.Add(e.file + " missing/late actor " + e.signature);
                if (!allowed.ContainsKey(e.file)) allowed[e.file] = new(); allowed[e.file].Add(span);
            }
            foreach (var e in inherited.Concat(setup))
            {
                if (!allowed.ContainsKey(e.file)) allowed[e.file] = new(); allowed[e.file].Add(Body(files[e.file],e.signature));
            }
            foreach (var f in files.Where(f => !f.Key.StartsWith("//tags:")))
                foreach (Match m in Regex.Matches(f.Value, @"\.Try(?:Add|Remove)Liquid\("))
                    if (!allowed.TryGetValue(f.Key,out var spans) || !spans.Any(s => s.start <= m.Index && m.Index < s.end)) bad.Add(f.Key + " unscoped mutation " + m.Index);
            return bad;
        }
        public static void Run(Action<string,Action> Case)
        {
            Case("TankTheft_all_production_transfer_callers_have_actor_or_explicit_setup_boundary", () =>
            {
                var files = TransferChecks.ProductionSources();
                var bad = Lint(files);
                if (bad.Count != 0) throw new Exception(string.Join("; ",bad));
                var planted = new Dictionary<string,string>(files);
                planted["Machinery/NewMover.cs"] = "void Run() { tank.TryRemoveLiquid(10); }";
                planted["Machinery/CompLiquidConverter.cs"] += " void Unscoped() { tank.TryAddLiquid(water,10); }";
                if (Lint(planted).Count != 2) throw new Exception("caller guard missed new/existing-file unscoped mutations");
                planted = new Dictionary<string,string>(files);
                planted[entries[0].file] = planted[entries[0].file].Replace("using var theftActor = RimMandrake.FlowWorks.Machinery.RM_LiquidTheft.As(this);", "");
                if (Lint(planted).Count != 2) throw new Exception("caller guard missed removed draw/pour scopes");
                // Helpers do not escape their caller's lexical actor scope.
                string pump = files[entries[0].file];
                var pour = Body(pump, "private string TryPour()");
                foreach (string helper in new[] { "PourToPond(ex", "PourToOutflow(ex" })
                    foreach (Match m in Regex.Matches(pump, Regex.Escape(helper)))
                        if (m.Index < pour.start || m.Index >= pour.end) throw new Exception("unscoped helper call " + helper);
                string net = files["Machinery/RM_LiquidNet.cs"];
                if (!net.Contains("FillOne(r, map, liquid, fillFrom)") || !net.Contains("RM_HoseHold.Fill(ref hl, ref held, r.HeldCap, liquid, take,")) throw new Exception("hose fill boundary changed; trace synchronous credits again");
                string level = files["Machinery/RM_Levelling.cs"];
                if (level.Contains(".TryRemoveLiquid(") || level.Contains(".TryAddLiquid(")) throw new Exception("levelling gained tank path without an actor");
            });
        }
    }
}
