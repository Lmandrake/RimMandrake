// Unit groups for JawaBenchReceiptCore.cs, JawaBenchCalmCore.cs and JawaBenchFirstExceptionCore.cs (the PRODUCTION files).
// Prints "U <group>.<name> ok|FAIL why" per check and "U-count n"; exit 1 when any check fails. One group per promise of the
// three pages; driven by src/RimMandrake/Utils/live_tools_units.py. With RM_PLANT=<fault> a planted fault is put in the
// data a group reads; that group must then go red (the Python selftests run each plant).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using C = JawaBench.BridgeTools.JawaBenchCalmCore;
using E = JawaBench.BridgeTools.JawaBenchFirstExceptionCore;
using R = JawaBench.BridgeTools.JawaBenchReceiptCore;

namespace JawaBench.BridgeTools
{
    internal static class Program
    {
        static int _n, _bad;
        internal static readonly string Plant = Environment.GetEnvironmentVariable("RM_PLANT") ?? "";

        internal static void Check(string name, Func<bool> f)
        {
            _n++;
            bool ok; string w = "";
            try { ok = f(); } catch (Exception e) { ok = false; w = e.GetType().Name + ": " + e.Message; }
            if (!ok) _bad++;
            Console.WriteLine("U " + name + " " + (ok ? "ok" : "FAIL " + w));
        }

        static C.Reading Rd(string n, string st, params string[] things) => new C.Reading(n, st, "d", things);

        static List<C.Reading> AllHeld() => C.Controls.Select(n => Rd(n, n == C.Hostiles || n == C.Fires ? C.Calm : C.Held)).ToList();

        static int Main(string[] args)
        {
            if (args.Length > 1 && args[0] == "fingerprint")
            {
                Console.WriteLine(R.Fingerprint(args[1].Length == 0 ? new string[0] : args[1].Split(',')));
                return 0;
            }
            Receipt();
            Calm();
            FirstException();
            CanonicalGuardUnits.Run();
            Console.WriteLine("U-count " + _n);
            return _bad == 0 ? 0 : 1;
        }

        static void Receipt()
        {
            // ---- game key
            Check("gamekey.named_instance", () => R.GameKey("ARCHMAGI", @"D:\ClaudeWork\rimmandrake\instances\b", @"D:\x\instances\b\game") == "archmagi.b");
            Check("gamekey.trailing_slash_and_case", () => R.GameKey("Archmagi", "d:/x/Instances/B/", null) == "archmagi.b");
            Check("gamekey.own_install_without_savedata", () => R.GameKey("archmagi", @"C:\Users\M\AppData\LocalLow\L\R", @"D:\x\instances\b\game") == "archmagi.b");
            Check("gamekey.steam_install_is_the_machine", () => R.GameKey("archmagi", @"C:\Users\M\AppData\LocalLow\Ludeon", @"C:\Steam\common\RimWorld") == "archmagi");
            Check("gamekey.letter_a_is_the_machine", () => R.GameKey("archmagi", @"D:\x\instances\a", null) == "archmagi");
            Check("gamekey.no_machine_no_key", () => R.GameKey("", @"D:\x\instances\b", null) == null && R.GameKey(null, null, null) == null);
            Check("gamekey.a_folder_called_instances_elsewhere", () => R.GameKey("m", @"D:\instances\backup", null) == "m" && R.GameKey("m", @"D:\x\instances\b\other", null) == "m");

            // ---- mvid
            var self = typeof(Program).Assembly;
            var raw = File.ReadAllBytes(self.Location);
            var mvid = self.ManifestModule.ModuleVersionId;
            if (Plant == "mvid") mvid = Guid.NewGuid();
            Check("mvid.own_file_holds_it", () => R.HoldsMvid(raw, mvid) == true);
            Check("mvid.another_id_is_not_there", () => R.HoldsMvid(raw, Guid.NewGuid()) == false);
            Check("mvid.empty_file_is_could_not_read", () => R.HoldsMvid(new byte[0], mvid) == null && R.HoldsMvid(null, mvid) == null && R.HoldsMvid(raw, Guid.Empty) == null);
            Check("mvid.at_the_very_end", () => R.HoldsMvid(new byte[] { 1, 2 }.Concat(mvid.ToByteArray()).ToArray(), mvid) == true);
            Check("mvid.cut_by_one_byte", () => R.HoldsMvid(mvid.ToByteArray().Take(15).ToArray(), mvid) == false);

            // ---- mod state
            const string F = @"C:\Mods\A";
            R.AsmFact A(string loc, bool? h = true) => new R.AsmFact { Name = "A", Location = loc, FileHoldsLoaded = h };
            string S(string[] files, params R.AsmFact[] a) { string w; return R.JudgeMod(F, files, a, out w); }
            var dll = new[] { @"C:\Mods\A\Assemblies\A.dll" };
            Check("modstate.loaded", () => S(dll, A(@"C:\Mods\A\Assemblies\A.dll", Plant == "filechanged" ? false : true)) == R.Loaded);
            Check("modstate.case_and_slash", () => S(dll, A(@"c:/mods/a/assemblies/a.DLL")) == R.Loaded);
            Check("modstate.file_changed", () => S(dll, A(dll[0], false)) == R.FileChanged);
            Check("modstate.not_loaded", () => S(new[] { dll[0], @"C:\Mods\A\Assemblies\B.dll" }, A(dll[0])) == R.DllNotLoaded && S(dll) == R.DllNotLoaded);
            Check("modstate.foreign_copy", () => S(dll, A(@"C:\Mods\AB\Assemblies\A.dll")) == R.ForeignCopy);
            Check("modstate.no_assembly", () => S(new string[0]) == R.NoAssembly);
            Check("modstate.could_not_read", () => S(null, A(dll[0])) == R.CouldNotRead && S(dll, A(null)) == R.CouldNotRead && S(dll, A(dll[0], null)) == R.CouldNotRead);
            Check("modstate.unknown_folder", () => { string w; return R.JudgeMod("", dll, new[] { A(dll[0]) }, out w) == R.CouldNotRead && w != null; });
        }

        static void Calm()
        {
            var none = new HashSet<string>();
            Check("everyread.all_held_is_calm", () => C.Judge(Plant == "unread" ? AllHeld().Skip(1) : AllHeld(), none).IsCalm);
            foreach (var name in C.Controls)
                Check("everyread.missing_" + name, () => { var r = C.Judge(AllHeld().Where(x => x.Name != name), none); return !r.IsCalm && r.Verdict == C.VNotRead && r.Of(C.NotRead).Single().Name == name; });
            Check("everyread.throwing_reading", () => { var l = AllHeld().Where(x => x.Name != C.Weather).ToList(); l.Add(C.Take(C.Weather, () => throw new InvalidOperationException("no map"))); var r = C.Judge(l, none); return r.Verdict == C.VNotRead && r.Of(C.NotRead)[0].Detail.Contains("no map"); });
            Check("everyread.null_reading", () => C.Take("x", () => null).Status == C.NotRead);
            Check("everyread.unknown_status", () => { var l = AllHeld(); l[0] = Rd(C.Storyteller, "FINE"); return C.Judge(l, none).Verdict == C.VNotRead; });
            Check("everyread.null_status", () => { var l = AllHeld(); l[0] = Rd(C.Storyteller, null); return C.Judge(l, none).Verdict == C.VNotRead; });
            Check("everyread.empty_profile", () => { var r = C.Judge(AllHeld(), none, new string[0]); return !r.IsCalm && r.Verdict == C.VNothing; });
            Check("everyread.all_excepted", () => !C.Judge(AllHeld(), new HashSet<string>(C.Controls)).IsCalm);
            Check("everyread.no_readings", () => C.Judge(null, none).Verdict == C.VNotRead);
            Check("everyread.two_readings_the_worse_wins", () => { var l = AllHeld(); l.Add(Rd(C.Weather, C.NotCalm, "rain")); return C.Judge(l, none).Verdict == C.VNotCalm; });
            Check("everyread.second_unread_reading_wins", () => { var l = AllHeld(); l.Add(Rd(C.Weather, C.NotRead)); return C.Judge(l, none).Verdict == C.VNotRead; });
            Check("everyread.calm_that_names_a_thing", () => { var l = AllHeld().Where(x => x.Name != C.Fires).ToList(); l.Add(Rd(C.Fires, C.Calm, "fire at 1,1")); return C.Judge(l, none).Verdict == C.VNotCalm; });

            Check("named.things_are_listed", () => { var l = AllHeld().Where(x => x.Name != C.Hostiles).ToList(); l.Add(Rd(C.Hostiles, Plant == "unnamed" ? C.Held : C.NotCalm, "Human1", "Human2")); var r = C.Judge(l, none).Of(C.NotCalm); return r.Count == 1 && r[0].Name == C.Hostiles && r[0].Things.SequenceEqual(new[] { "Human1", "Human2" }); });
            Check("named.not_covered_is_never_empty", () => C.NotCovered.Length > 0);

            Check("outranks.both_lists_filled", () => { var l = AllHeld(); l[0] = Rd(C.Storyteller, Plant == "outrank" ? C.Held : C.NotCalm, "x"); l[1] = Rd(C.MentalSwitch, C.NotRead); var r = C.Judge(l, none); return r.Verdict == C.VNotCalm && r.Of(C.NotCalm).Count == 1 && r.Of(C.NotRead).Count == 1; });

            string unknown;
            Check("excepted.shown", () => { var r = C.Judge(AllHeld().Where(x => x.Name != C.Weather), new HashSet<string>(Plant == "except" ? new string[0] : new[] { C.Weather })); return r.IsCalm && r.Of(C.Excepted).Single().Name == C.Weather; });
            Check("excepted.case_is_folded", () => C.ParseNames(" Weather , FIRES", C.Controls, out unknown).SetEquals(new[] { C.Weather, C.Fires }) && unknown == null);
            Check("excepted.unknown_is_returned", () => { C.ParseNames("weather,wether", C.Controls, out unknown); return unknown == "wether"; });
            Check("excepted.empty_list", () => C.ParseNames(null, C.Controls, out unknown).Count == 0 && C.ParseNames(" , ", C.Controls, out unknown).Count == 0 && unknown == null);

            var allow = new HashSet<string> { "RaidEnemy" };
            Check("gate.holds", () => C.Holds(Plant != "gate", "ManhunterPack", allow) && C.Holds(true, "ManhunterPack", none) && C.Holds(true, "RaidEnemy", null));
            Check("gate.allowed_any_case", () => !C.Holds(true, "raidenemy", allow) && !C.Holds(true, "RaidEnemy", allow));
            Check("gate.unnamed_incident_is_held", () => C.Holds(true, null, allow));
            Check("gate.off_holds_nothing", () => !C.Holds(false, "ManhunterPack", none));

            Check("breach.exact_past_the_rows", () => { var b = new C.BreachLog(); int n = Plant == "breach" ? 999 : 1000; for (int i = 0; i < n; i++) b.Add("incident_held", i, "x"); b.Add("arrival", 1, "y"); return b.Count("incident_held") == 1000 && b.Count("arrival") == 1 && b.Since(0).Count == C.BreachLog.MaxRows && b.Dropped == 1001 - C.BreachLog.MaxRows && b.LastSeq == 1001; });
            Check("breach.since", () => { var b = new C.BreachLog(); b.Add("a", 1, "x"); b.Add("a", 2, "y"); return b.Since(1).Single().What == "y" && b.Since(2).Count == 0; });
            Check("breach.unknown_kind_is_zero", () => new C.BreachLog().Count("a") == 0);
        }

        static void FirstException()
        {
            string Exc(int i) => "Exception ticking Thing" + i + ": System.NullReferenceException: x\n  at A.B" + i + " () [0x0]";
            Check("flood.first_kept_20000", () =>
            {
                var t = new E.Tap();
                t.Note("Log.Error", Exc(-1), false, false, e => e.Tick = 77);
                for (int i = 0; i < (Plant == "flood" ? 19999 : 20000); i++) t.Note("Log.Error", Exc(i), false, false, e => e.Tick = 1000 + i);
                return t.SessionException.Tick == 77 && t.WindowException.Tick == 77 && t.SessionException.Seq == 1 && t.Exceptions == 20001 && t.Errors == 0;
            });
            Check("flood.one_repeated", () => { var t = new E.Tap(); for (int i = 0; i < 5000; i++) t.Note("s", Exc(1), false, false, null); return t.Kept().Count == 1 && t.Kept()[0].Repeats == 5000 && t.DistinctKeys == 1 && t.NotKept == 0; });

            Check("plainerror.not_the_first_exception", () => { var t = new E.Tap(); t.Note("Log.Error", Plant == "plainerror" ? Exc(0) : "Could not find def X", false, false, null); t.Note("Log.Error", Exc(1), false, false, null); return t.SessionException.Text == Exc(1) && t.SessionError.Text == "Could not find def X" && t.Errors == 1 && t.Exceptions == 1; });
            Check("plainerror.unity_exception_without_the_word", () => { var t = new E.Tap(); t.Note("unity Exception", "boom", true, false, null); return t.SessionException != null && t.SessionException.IsException; });
            Check("plainerror.null_text", () => { var t = new E.Tap(); t.Note("s", null, false, false, null); return t.SessionError != null && t.Errors == 1; });
            Check("plainerror.words", () => E.IsExceptionText("System.InvalidOperationException: x") && E.IsExceptionText("Exception in X") && !E.IsExceptionText("an exceptional case") && !E.IsExceptionText("Exceptional"));

            Check("window.arm_keeps_session", () => { var t = new E.Tap(); t.Note("s", Exc(1), false, false, null); if (Plant != "window") t.NewWindow("scene", "u"); return t.SessionException.Text == Exc(1) && t.WindowException == null && t.WindowExceptions == 0 && t.Exceptions == 1 && t.Window == "scene"; });
            Check("window.a_repeat_is_the_new_windows_first", () => { var t = new E.Tap(); t.Note("s", Exc(1), false, false, e => e.Tick = 1); t.NewWindow("b", "u"); t.Note("s", Exc(1), false, false, e => e.Tick = 9); return t.SessionException.Tick == 1 && t.WindowException.Tick == 9; });
            Check("window.error_too", () => { var t = new E.Tap(); t.Note("s", "bad", false, false, null); t.NewWindow("b", "u"); return t.SessionError != null && t.WindowError == null && t.WindowErrors == 0; });

            var ok = new List<string>(); var blind = new List<string> { "unity off" };
            Check("state.not_armed", () => E.State(Plant == "state", false, ok) == E.NotArmed && E.State(false, false, blind) == E.NotArmed);
            Check("state.partial", () => E.State(true, false, blind) == E.NonePartial);
            Check("state.none", () => E.State(true, false, ok) == E.NoneSeen);
            Check("state.seen_whatever_else", () => E.State(false, true, blind) == E.Seen && E.State(true, true, ok) == E.Seen);

            Check("roads.copy_inside_log_error", () => { var r = new E.Roads(); if (Plant != "roads") r.EnterError(); bool c = r.UnityIsACopy; r.ExitError(); return c && !r.UnityIsACopy; });
            Check("roads.nested", () => { var r = new E.Roads(); r.EnterError(); r.EnterError(); r.ExitError(); bool c = r.UnityIsACopy; r.ExitError(); return c && !r.UnityIsACopy; });
            Check("roads.exit_without_enter", () => { var r = new E.Roads(); r.ExitError(); return !r.UnityIsACopy; });
            Check("roads.once_that_passed_is_not_silent", () => { var r = new E.Roads(); r.EnterOnce(); r.EnterError(); r.ExitError(); return !r.ExitOnce(); });
            Check("roads.once_kept_silent", () => { var r = new E.Roads(); r.EnterOnce(); return r.ExitOnce() && !r.ExitOnce(); });
            Check("roads.silenced_can_be_first", () => { var t = new E.Tap(); t.Note("once", Exc(1), false, true, null); return t.SessionException != null && t.Silenced == 1 && t.Exceptions == 1; });

            Check("bounded.kept_keys_text", () =>
            {
                var t = new E.Tap();
                int n = Plant == "bounded" ? 10 : 1000;
                for (int i = 0; i < n; i++) t.Note("s", Exc(i) + new string('x', 20000), false, false, e => e.Stack = new string('y', 20000));
                return t.Kept().Count == E.MaxKept && t.NotKept == 1000 - E.MaxKept && t.DistinctKeys == E.MaxKeys && t.KeysDropped == 1000 - E.MaxKeys &&
                       t.Kept().All(e => e.Text.Length < E.MaxText + 60 && e.Stack.Length < E.MaxText + 60) && t.SessionException.Text.Contains("more characters");
            });
            Check("bounded.a_throwing_fill_is_kept", () => { var t = new E.Tap(); t.Note("s", Exc(1), false, false, e => throw new Exception("x")); return t.SessionException != null && t.SessionException.Stack.StartsWith("stack could not be read"); });
            Check("bounded.fill_runs_only_for_kept", () => { var t = new E.Tap(); int f = 0; for (int i = 0; i < 500; i++) t.Note("s", Exc(i), false, false, e => f++); return f == E.MaxKept; });
        }
    }
}
