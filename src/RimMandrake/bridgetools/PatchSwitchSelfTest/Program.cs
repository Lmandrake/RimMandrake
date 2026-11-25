// Units of the patch switch's pure core (JawaBenchPatchSwitchCore.cs), compiled on plain .NET by selftest_patch_switch.py.
// Each line "U <name> ok" is one promise of the boundary page section THE PATCH SWITCH.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using P = JawaBench.BridgeTools.JawaBenchPatchSwitchCore;

internal static class Program
{
    static P.Row Row(string kind, string type, string method, string owner = "mandrake.rm.explosiveknockback",
                     bool ours = true, bool self = false, int slots = 1, string orig = "Verse.AI.Pawn_JobTracker",
                     string origMethod = "CheckForJobOverride", string origParams = "Single")
        => new P.Row
        {
            Kind = kind, PatchType = type, PatchMethod = method, OrigType = orig, OrigMethod = origMethod, OrigParams = origParams,
            Owner = owner, Mod = ours ? "mandrake.rm.explosiveknockback" : "someone.else", Priority = 400, Index = 0,
            Slots = slots, Originals = 1, Ours = ours, SelfAssembly = self
        };

    static void Main()
    {
        void Check(string name, Action test)
        {
            try { test(); Console.WriteLine("U " + name + " ok"); }
            catch (Exception e) { Console.WriteLine("U " + name + " " + e.Message); }
        }
        void Need(bool ok, string why) { if (!ok) throw new Exception(why); }
        string Name(string refusal) => (refusal ?? "null").Split(':')[0];

        var ek = Row("prefix", "RimMandrake.ExplosiveKnockback.RM_Patch_JobTracker_KnockbackLandingNoSearch", "Prefix");
        var ek2 = Row("prefix", "RimMandrake.ExplosiveKnockback.RM_Patch_PawnFlyer_KnockbackNoRedirect", "Prefix",
                      orig: "RimWorld.PawnFlyer", origMethod: "RespawnPawn", origParams: "");
        var foreign = Row("postfix", "Other.Mod.Patch", "Postfix", owner: "other.mod", ours: false);
        var bench = Row("prefix", "JawaBench.BridgeTools.JawaBenchPatchSwitch", "CountOriginalPre",
                        owner: "mandrake.jawabench.patchswitch", self: true);
        var rows = new List<P.Row> { ek, ek2, foreign, bench };

        Check("id", () =>
        {
            Need(ek.Id == "prefix:RimMandrake.ExplosiveKnockback.RM_Patch_JobTracker_KnockbackLandingNoSearch.Prefix@Verse.AI.Pawn_JobTracker.CheckForJobOverride(Single)",
                 "the id is not kind:Type.Method@OrigType.OrigMethod(params): " + ek.Id);
            Need(ek.Id != Row("postfix", ek.PatchType, "Prefix").Id && ek.Id != Row("prefix", ek.PatchType, "Prefix", origParams: "").Id,
                 "two patches that differ in kind or overload share one id");
        });
        Check("select", () =>
        {
            Need(P.Select(rows, ek.Id, out _) == ek, "the exact id did not pick its patch");
            Need(P.Select(rows, "  " + ek.Id + " ", out _) == ek, "a padded id did not pick its patch");
            Need(P.Select(rows, ek2.PatchName, out _) == ek2, "Type.Method did not pick its patch");
            Need(P.Select(rows, "Postfix", out _) == foreign, "a unique bare method name did not pick its patch");
            Need(P.Select(rows, "Prefix", out string amb) == null && Name(amb) == "AMBIGUOUS" && amb.Contains(ek.Id) && amb.Contains(ek2.Id),
                 "a bare name of two patches was not refused AMBIGUOUS with both ids: " + amb);
            Need(P.Select(rows, "NoSuchPatch", out string unk) == null && Name(unk) == "UNKNOWN_PATCH", "an unknown name was not UNKNOWN_PATCH: " + unk);
            Need(P.Select(rows, null, out string none) == null && Name(none) == "UNKNOWN_PATCH", "no name was not UNKNOWN_PATCH: " + none);
        });
        Check("ours", () =>
        {
            Need(P.IsOurs(new[] { "Mandrake.RM.ExplosiveKnockback" }) && P.IsOurs(new[] { "other.mod", "mandrake.rut.x" }),
                 "a mandrake.* packageId was not ours");
            Need(!P.IsOurs(new[] { "notmandrake.rm.x", "other.mandrake." }) && !P.IsOurs(new string[0]) && !P.IsOurs(null),
                 "a packageId that only contains mandrake. was read as ours");
        });
        Check("jawabench", () =>
        {
            Need(P.IsJawaBench("mandrake.jawabench.patchswitch", false) && P.IsJawaBench("JawaBench.Tps", false) &&
                 P.IsJawaBench("mandrake.jawabench", false) && P.IsJawaBench("mandrake.rm.x", true), "a JawaBench patch was not marked");
            Need(!P.IsJawaBench("mandrake.rm.explosiveknockback", false) && !P.IsJawaBench("jawabenchy", false) && !P.IsJawaBench(null, false),
                 "a patch that is not JawaBench's was marked");
        });
        Check("off-refusals", () =>
        {
            int looked = 0;
            Func<string> canonical = () => { looked++; return "CANONICAL_SAVE: overlay refused on ArchSmall"; };
            Need(Name(P.OffRefusal(bench, canonical)) == "JAWABENCH", "a JawaBench patch was not refused JAWABENCH");
            Need(Name(P.OffRefusal(foreign, canonical)) == "NOT_OURS", "a foreign patch was not refused NOT_OURS");
            Need(Name(P.OffRefusal(Row("prefix", "A", "B", slots: 2), canonical)) == "AMBIGUOUS", "a patch in two slots was not refused");
            Need(looked == 0, "the save was read for a patch that was refused by name first");
            Need(Name(P.OffRefusal(ek, canonical)) == "CANONICAL_SAVE" && looked == 1, "a canonical save did not refuse off");
            Need(Name(P.OffRefusal(ek, () => "COULD_NOT_LOOK: no save")) == "COULD_NOT_LOOK", "a save that could not be read did not refuse off");
            Need(P.OffRefusal(ek, () => null) == null && P.OffRefusal(ek, null) == null, "our patch on a test save was refused");
            var off = Row("prefix", "A", "B"); off.Off = true;
            Need(Name(P.OffRefusal(off, () => null)) == "ALREADY_OFF", "a patch that is off was not refused ALREADY_OFF");
            Need(Name(P.OffRefusal(null, () => null)) == "UNKNOWN_PATCH", "no patch was not UNKNOWN_PATCH");
        });
        Check("on-refusals", () =>
        {
            var off = Row("prefix", "A", "B"); off.Off = true;
            Need(P.OnRefusal(off) == null, "a patch that is off was refused on");
            Need(Name(P.OnRefusal(ek)) == "ALREADY_ON", "a patch that is on was not refused ALREADY_ON");
        });
        Check("count-refusals", () =>
        {
            Need(Name(P.CountRefusal(Row("transpiler", "A", "Transpiler"))) == "TRANSPILER_NOT_COUNTABLE", "a transpiler was counted");
            Need(Name(P.CountRefusal(bench)) == "JAWABENCH", "a JawaBench hook was counted");
            Need(P.CountRefusal(ek) == null && P.CountRefusal(foreign) == null && P.CountRefusal(Row("finalizer", "A", "F")) == null,
                 "a prefix, postfix or finalizer was refused a counter");
        });
        Check("counters", () =>
        {
            var c = new P.Counters();
            Need(c.Read(7) == -1 && !c.Armed(7), "a counter that was never armed did not read -1");
            c.Hit(7);
            Need(c.Read(7) == -1, "a hit on an unarmed key made a row");
            c.Arm(7);
            Need(c.Read(7) == 0 && c.Armed(7), "an armed counter did not start at 0");
            c.Hit(7); c.Hit(7); c.Arm(7);
            Need(c.Read(7) == 2, "a second arm reset or lost the count");
            c.Arm(8);
            const int threads = 8, each = 200000;
            var workers = Enumerable.Range(0, threads).Select(i => new Thread(() =>
                { for (int n = 0; n < each; n++) { c.Hit(8); if (n % 1000 == 0) c.Hit(9); } })).ToList();
            workers.ForEach(t => t.Start());
            workers.ForEach(t => t.Join());
            Need(c.Read(8) == (long)threads * each, "threads lost hits: " + c.Read(8) + " of " + (long)threads * each);
            Need(c.Read(9) == -1, "threads made a row for an unarmed key");
            c.Fault(); c.Fault();
            Need(c.Faults == 2, "faults were not counted");
        });
        Check("order-kept", () =>
        {
            Need(P.OrderKept(new[] { "a", "b" }, new List<string> { "a", "b" }), "the same order read as moved");
            Need(!P.OrderKept(new[] { "a", "b" }, new[] { "b", "a" }) && !P.OrderKept(new[] { "a", "b" }, new[] { "a" }) &&
                 !P.OrderKept(null, new[] { "a" }), "a moved or lost patch read as the same order");
        });
    }
}
