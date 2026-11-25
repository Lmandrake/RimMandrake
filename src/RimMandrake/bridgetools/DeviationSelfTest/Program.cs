using System;
using System.Collections.Generic;
using System.IO;
using D = JawaBench.BridgeTools.JawaBenchDeviationCore;

internal static partial class SettingsHost
{
    internal static D.Record Record;
    private static string CanonicalRefusal() => null;
    private static void InstallSaveHook() { }
    private static void InstallSettingsGuard(D.Entry[] entries) { }
    private static class JawaBenchVitals
    {
        internal static void EnsureDriver() { }
        internal const string DriverStatus = "monobehaviour";
    }
    private static class JawaBenchHands
    {
        internal static bool Busy => false;
        internal static bool SettingsSessionOpen => false;
    }
    private static class Time { internal static float realtimeSinceStartup; }
    private static class Current { internal static object Game => null; }
    private static class Find { internal static TestTicks TickManager => null; }
    private enum TimeSpeed { Paused }
    private sealed class TestTicks { internal TimeSpeed CurTimeSpeed { get; set; } }

    internal static void AdvancePastDefaultLease()
    {
        Time.realtimeSinceStartup += JawaBenchHandsCore.DefaultLeaseS + 1;
        Frame();
    }
}

internal static class Program
{
    public const int Constant = 3;
    public static readonly int Readonly = 4;
    private sealed class InstanceSettings { public readonly int Readonly = 5; }

    static void Main(string[] args)
    {
        var path = Path.Combine(args[0], "journal.json");
        void Check(string name, Action test)
        {
            try { test(); Console.WriteLine("U " + name + " ok"); }
            catch (Exception e) { Console.WriteLine("U " + name + " " + e.Message); }
        }
        void Need(bool ok, string why) { if (!ok) throw new Exception(why); }
        D.Record Fresh() { File.Delete(path); return new D.Record(() => path); }
        var values = new Dictionary<string, object> { { "x", 0 }, { "y", "" }, { "z", 3 } };
        var writes = new List<string>();
        D.Entry Setting(string key, object value, Action<object> extra = null) =>
            new D.Entry("overlay", "PUT BACK", "process", key, "Mod", value, () => values[key], v =>
            { writes.Add(key + "=" + v); values[key] = v; extra?.Invoke(v); });

        Check("order", () =>
        {
            var r = Fresh();
            var error = r.Apply("a", "batch", new[] { Setting("x", 1), Setting("y", "yes", v =>
                { if (Equals(v, "yes")) throw new IOException("second"); }), Setting("z", 9) });
            Need(error != null && error.Contains("second") && !r.Spoiled, "apply did not report its failed entry: " + error);
            Need(string.Join(",", writes) == "x=1,y=yes,y=,x=0" && Equals(values["x"], 0) && Equals(values["y"], ""), "writes were not undone in reverse order");
            Need(!File.Exists(path), "a paid debt stayed on disk");
        });
        Check("spoiled", () =>
        {
            var r = Fresh();
            r.Apply("a", "batch", new[] { Setting("x", 1, v => { if (Equals(v, 0)) throw new IOException("revert"); }),
                Setting("y", "yes", v => { if (Equals(v, "yes")) throw new IOException("second"); }) });
            Need(r.Spoiled && File.Exists(path) && r.BlocksSettings("Mod"), "failed revert lost SPOILED or its debt");
        });
        Check("taint", () =>
        {
            var r = Fresh();
            Need(r.Apply("a", "test", new[] { Setting("x", 1) }) == null && r.Revert("a") == null, "could not apply and revert");
            Need(r.Tainted, "revert dropped the taint");
        });
        Check("none", () =>
        {
            var r = Fresh();
            r.Apply("a", "test", new[] { Setting("x", 1) });
            r.Revert("a");
            var receipt = r.Receipt();
            Need(Equals(receipt["overlay"], "none") && Equals(receipt["clean"], false), "an empty overlay made a tainted process clean");
        });
        Check("receipt", () =>
        {
            var r = Fresh();
            r.Apply("a", "record", new[] {
                new D.Entry("calm", "GIVEN BACK", "station", "incidents", null, 1, () => 1, v => {}),
                new D.Entry("force", "NOT UNDONE", "station", "job", null, null, null, null),
                Setting("x", 2),
                new D.Entry("time and rate", "PUT BACK", "station", "rate", null, 0, () => 0, v => {}) });
            var rows = (IEnumerable<Dictionary<string, object>>)r.Receipt()["entries"];
            var kinds = new List<string>();
            foreach (var row in rows) kinds.Add(row["kind"] + ":" + row["class"]);
            Need(string.Join(",", kinds) == "calm:GIVEN BACK,force:NOT UNDONE,overlay:PUT BACK,time and rate:PUT BACK", "receipt lost an entry or class");
            Need(r.OverlayStamp.StartsWith("record ") && r.OverlayStamp.Length > "record ".Length, "overlay has no name and hash");
            r.Revert("a");
        });
        Check("save", () =>
        {
            var r = Fresh();
            r.Apply("a", "run", new[] { new D.Entry("force", "NOT UNDONE", "save", "job", null, null, null, null) });
            r.Revert("a");
            Need(r.SaveDirty, "save reach was lost on leave");
            r.Load(false);
            Need(!r.SaveDirty, "fixture did not clear save reach");
        });
        Check("process", () =>
        {
            var r = Fresh();
            r.Apply("a", "run", new[] { new D.Entry("force", "NOT UNDONE", "process", "counter", null, null, null, null) });
            r.Revert("a");
            r.Load(false);
            Need(r.ProcessDirty && Equals(r.Receipt()["clean"], false), "fixture cleared process reach");
        });
        Check("const", () => Need((D.FieldRefusal(typeof(Program).GetField("Constant")) ?? "").Contains("const Constant"), "const Constant was not refused by name"));
        Check("readonly", () => Need((D.FieldRefusal(typeof(Program).GetField("Readonly")) ?? "").Contains("static readonly Readonly"), "static readonly Readonly was not refused by name"));
        Check("canonical", () =>
        {
            var r = Fresh();
            var before = values["x"];
            Need(r.Apply("a", "test", new[] { Setting("x", 1) }, canonical: true) != null && Equals(values["x"], before) &&
                !r.Tainted && !File.Exists(path), "canonical refusal touched the game");
        });
        Check("holder", () =>
        {
            var r = Fresh();
            r.Apply("a", "test", new[] { Setting("x", 1) });
            Need(r.Apply("b", "test", new[] { Setting("x", 2) }) != null && Equals(values["x"], 1), "second holder wrote a value");
            r.Revert("a");
        });
        Check("journal", () =>
        {
            var r = Fresh();
            var error = r.Apply("a", "test", new[] { Setting("x", 1, v =>
                { if (Equals(v, 1)) Need(File.Exists(path) && File.ReadAllText(path).Contains("\"before\""), "journal was missing on first write"); }) });
            Need(error == null, error);
            Need(new D.Record(() => path).PriorJournal != null, "next handshake lost the outstanding journal");
            r.Revert("a");
        });
        Check("disk", () =>
        {
            var r = Fresh();
            Need(!r.BlocksSettings("Mod"), "idle record blocked settings");
            r.Apply("a", "test", new[] { Setting("x", 1) });
            Need(r.BlocksSettings("Mod") && !r.BlocksSettings("Other"), "settings block has the wrong reach");
            r.Revert("a");
            Need(!r.BlocksSettings("Mod"), "paid entry still blocks settings");
        });
        Check("override-body", () =>
        {
            // A set with no session (the LuminousPigment, BlueDesert and FlowWorks callers) leaves the disk write open.
            var r = Fresh();
            r.Apply(null, null, new[] { Setting("x", 2) });
            Need(!r.BlocksSettings("Mod"), "a standalone set blocked the mod's settings write");
            r.Revert(null);
        });
        Check("default", () =>
        {
            var r = Fresh();
            int actual = 0;
            r.ObserveDefault("setting", 0, () => actual);
            actual = 3;
            var diff = (IEnumerable<Dictionary<string, object>>)r.Receipt()["differsFromDefault"];
            foreach (var row in diff)
                if (Equals(row["target"], "setting") && Equals(row["default"], 0) && Equals(row["value"], 3)) return;
            throw new Exception("external write missing from default comparison");
        });
        Check("standalone-lease", () =>
        {
            values["x"] = 0;
            SettingsHost.Record = Fresh();
            var error = SettingsHost.ApplySettings(null, null, Setting("x", 7));
            Need(error == null && Equals(values["x"], 7), "standalone set did not take: " + error);
            SettingsHost.AdvancePastDefaultLease();
            Need(Equals(values["x"], 7), "standalone read-back was " + values["x"] + " after the default lease");
            Need(SettingsHost.Revert(null) == null && Equals(values["x"], 0), "explicit revert did not restore the original value");
        });
        Check("standalone-callers", () =>
        {
            SettingsHost.Record = Fresh();
            var first = SettingsHost.ApplySettings("caller a", null, Setting("x", 8));
            var second = SettingsHost.ApplySettings("caller b", null, Setting("y", "set"));
            Need(first == null, "first standalone caller refused: " + first);
            Need(second == null, "second standalone caller refused: " + second);
            Need(Equals(values["x"], 8) && Equals(values["y"], "set"), "standalone callers did not retain both writes");
        });
        Check("instance-readonly", () => Need(D.FieldRefusal(typeof(InstanceSettings).GetField("Readonly")) == null,
            "an instance readonly field acquired a refusal"));
    }
}
