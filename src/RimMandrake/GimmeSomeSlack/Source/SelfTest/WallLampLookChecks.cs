// T_WALL_LAMP_LOOKS_OFFLINE (Gimme Some Slack 0.2.0, bar wall_lamp_takes_looks, design/concepts/GimmeSomeSlack/record.json;
// owner walk 2026-11-20: "the Wall Lamp doesn't even have any yet"; homed in GSS by the design pass he ordered).
// "A wall lamp takes the looks as the standing lamp does: it wears the look of the line it is hooked to unless the player gives
// it its own from its style button, each look reads as that look's wall lamp from every facing, and with the master switch off
// it draws the vanilla wall lamp."
//
// What runs is the SHIPPED decision: ConduitStyles.LampDefs / IsLampDef (the one list every lamp rule reads: the picker's
// registry, RM_MapComponent_ConduitRuns.LampsOf, RestyleLamp, CountMap, the probe), IsRunMemberDef, KeysFor,
// AllStyleDefNames / TryParseStyleDefName, LampsHookedTo and LampFollowsRun; the mod's own Defs/ and Textures/; and a source
// read holding the Verse side (the lamp gate, the master-off graphic) to that list.
//
// Declared range:
//   * defs: both lamp defs (StandingLamp, WallLamp) and the four looks: 8 style defs, every facing Graphic_Multi draws for the
//     wall lamp (north, east, south; west is east mirrored, as vanilla ships it);
//   * following its line: generated lines (seeded, 2000) of 1-8 member cells with 1-4 lamps each, every lamp a standing or a
//     wall lamp, wired to a member of the line, wired to another line, unwired beside a member or unwired far away; wearing
//     no look, the line's look, another look, or a foreign style; the wall lamp must be hooked and follow exactly as a
//     standing lamp in the same place does.
// Left out (why): what the picture looks like (an art judge's call, made: 12 of 12 KEEP, commissions.md) and the drawn result
// with the master switch off (the running renderer: sc_wall_lamp_looks, Stage 6); the wall the lamp hangs on (the vanilla
// place worker's; the hook rule reads only the power connection and the cells).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Xml.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class WallLampLookChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "wall lamp looks: " + msg);
        public const int Cases = 2000;
        // Core WallLamp graphicData (RimSage, read 2026-11-23): the style's picture must hang where the vanilla lamp does
        private static readonly Dictionary<string, string> VanillaOffsets = new Dictionary<string, string>
        {
            ["drawOffsetNorth"] = "(0,0,0.9)", ["drawOffsetSouth"] = "(0,0,-0.9)", ["drawOffsetWest"] = "(-0.9,0,0)", ["drawOffsetEast"] = "(0.9,0,0)",
        };
        private static readonly string[] Facings = { "north", "east", "south" };   // Graphic_Multi: west = east mirrored when no _west

        public static void Run()
        {
            // 1. the wall lamp is a lamp of the picker, styled per look, never a run member
            Check(ConduitStyles.IsLampDef("WallLamp") && ConduitStyles.IsLampDef("StandingLamp"), "WallLamp and StandingLamp are lamp defs of the picker (ConduitStyles.LampDefs)");
            Check(!ConduitStyles.IsRunMemberDef("WallLamp", true), "a wall lamp is not a run member (a lamp ends a run)");
            Check(ConduitStyles.KeysFor("WallLamp").SequenceEqual(AerialStyles.Looks), "the wall lamp carries the four looks and no colour keys (" + string.Join(",", ConduitStyles.KeysFor("WallLamp")) + ")");
            foreach (string look in AerialStyles.Looks)
            {
                string n = ConduitStyles.StyleDefName("WallLamp", look);
                Check(ConduitStyles.AllStyleDefNames().Contains(n), n + " is one of the mod's style def names");
                Check(ConduitStyles.TryParseStyleDefName(n, out string d, out string l, out string c) && d == "WallLamp" && l == look && c == null, n + " parses back to (WallLamp, " + look + ")");
            }

            // 2. the defs and the art: every look, every facing
            string root = LookIconChecks.ModRoot();
            Check(root != null, "found the mod root");
            if (root != null)
            {
                List<string> faults = DefFaults(root, LookIconChecks.TexturesDir(), p => File.Exists(p));
                Console.WriteLine("wall lamp looks: " + AerialStyles.Looks.Length + " looks x " + Facings.Length + " facings read; def/art faults " + faults.Count + " (limit 0)" + (faults.Count > 0 ? "; first: " + faults[0] : ""));
                foreach (string f in faults) Check(false, f);
                Check(faults.Count == 0, "every wall lamp look is a Graphic_Multi style def on its own art, hung at vanilla's offsets, with a picture for every facing");
                // can fail: a look with a missing facing reads red
                string hide = Path.Combine(LookIconChecks.TexturesDir() ?? "", "RimMandrake", "GimmeSomeSlack", "Styles", "Modern", "WallLamp_east.png");
                List<string> planted = DefFaults(root, LookIconChecks.TexturesDir(), p => !string.Equals(Path.GetFullPath(p), Path.GetFullPath(hide), StringComparison.OrdinalIgnoreCase) && File.Exists(p));
                Check(planted.Any(x => x.Contains("Modern") && x.Contains("east")), "can fail: the Modern wall lamp with its east facing missing reads red (" + planted.Count + " faults)");
                string patch = File.ReadAllText(Path.Combine(root, "Patches", "RM_ConduitStyleable.xml"));
                Check(patch.Contains("Defs/ThingDef[defName=\"WallLamp\"]/comps/li[@Class=\"CompProperties_Styleable\"]"), "the guarded CompProperties_Styleable patch covers WallLamp");
            }

            // 3. the wall lamp follows its line as the standing lamp does (generated range)
            Follows(ConduitStyles.IsLampDef, out int worst, out int lamps, out Dictionary<string, int> regimes);
            Console.WriteLine("wall lamp looks: " + Cases + " generated lines, " + lamps + " lamps; wall lamps hooked or following differently from a standing lamp in the same place: worst " + worst + " (limit 0)");
            Console.WriteLine("wall lamp looks: regimes " + string.Join(", ", regimes.OrderBy(k => k.Key).Select(k => k.Key + " " + k.Value)));
            Check(worst == 0, "a wall lamp is hooked and follows its line exactly as a standing lamp in the same place (worst " + worst + ", " + lamps + " lamps)");
            foreach (string r in new[] { "wired to a member", "wired to another line", "unwired beside a member", "unwired far", "no look", "the line's look", "a look of its own", "a foreign style" })
                Check(regimes.TryGetValue(r, out int n) && n >= 100, "range covers '" + r + "' (" + (regimes.TryGetValue(r, out int m) ? m : 0) + " wall lamps, floor 100)");
            Follows(d => d == "StandingLamp", out int worstOld, out _, out _);
            Check(worstOld > 0, "can fail: the 0.1.1 lamp list (StandingLamp only) leaves wall lamps behind (worst " + worstOld + ")");

            Wiring();
        }

        /// <summary>The def and art faults of the wall lamp's looks; <paramref name="exists"/> is the file test (planted in the can-fail).</summary>
        internal static List<string> DefFaults(string root, string tex, Func<string, bool> exists)
        {
            var f = new List<string>();
            string defs = Path.Combine(root, "Defs", "Aerial", "RM_ConduitStyles.xml");
            if (!File.Exists(defs)) { f.Add("no " + defs); return f; }
            if (tex == null || !Directory.Exists(tex)) { f.Add("no Textures/ to read (" + (tex ?? "none") + ")"); return f; }
            Dictionary<string, XElement> styles = XDocument.Load(defs).Root.Elements("ThingStyleDef")
                .GroupBy(e => (string)e.Element("defName")).ToDictionary(g => g.Key, g => g.First());
            foreach (string look in AerialStyles.Looks)
            {
                string n = ConduitStyles.StyleDefName("WallLamp", look);
                if (!styles.TryGetValue(n, out XElement e)) { f.Add(n + ": no ThingStyleDef"); continue; }
                XElement g = e.Element("graphicData");
                string tp = (string)g?.Element("texPath");
                if (tp != "RimMandrake/GimmeSomeSlack/Styles/" + look + "/WallLamp") f.Add(n + ": draws " + (tp ?? "nothing") + ", not its own look's wall lamp");
                if ((string)g?.Element("graphicClass") != "Graphic_Multi") f.Add(n + ": not Graphic_Multi (a wall lamp faces its wall)");
                foreach (KeyValuePair<string, string> o in VanillaOffsets)
                    if (((string)g?.Element(o.Key) ?? "").Replace(" ", "") != o.Value) f.Add(n + ": " + o.Key + " " + ((string)g?.Element(o.Key) ?? "unset") + ", vanilla's is " + o.Value);
                if (tp == null) continue;
                foreach (string facing in Facings)
                {
                    string png = Path.Combine(tex ?? "", (tp + "_" + facing).Replace('/', Path.DirectorySeparatorChar) + ".png");
                    if (!exists(png)) f.Add(n + ": no " + facing + " picture (" + tp + "_" + facing + ".png)");
                }
            }
            return f;
        }

        private sealed class T { public int Id; public string Def; public int X, Z; public T Conn; public string Look; public bool Foreign; }

        /// <summary>Generated lines: each lamp is read as a wall lamp and, in the same place, as a standing lamp; the lamp list is
        /// the things whose def <paramref name="isLamp"/> takes (RM_MapComponent_ConduitRuns.LampsOf: ThingsOfDef over LampDefs).
        /// worst = wall lamps whose hooked or follow outcome differs from the standing lamp's.</summary>
        private static void Follows(Func<string, bool> isLamp, out int worst, out int lamps, out Dictionary<string, int> regimes)
        {
            worst = 0; lamps = 0; regimes = new Dictionary<string, int>();
            var rnd = new Random(20261123);
            string[] looks = AerialStyles.Looks;
            const string D = "Scrapper";
            for (int i = 0; i < Cases; i++)
            {
                int id = 1;
                string lineLook = rnd.Next(4) == 0 ? null : looks[rnd.Next(4)];
                var run = new List<T>();
                int x = 5 + rnd.Next(10), z = 5 + rnd.Next(10), len = 1 + rnd.Next(8);
                for (int k = 0; k < len; k++) run.Add(new T { Id = id++, Def = "PowerConduit", X = x + k, Z = z, Look = lineLook });
                var other = new T { Id = id++, Def = "PowerConduit", X = 40, Z = 40, Look = looks[rnd.Next(4)] };
                int nl = 1 + rnd.Next(4);
                for (int k = 0; k < nl; k++)
                {
                    T m = run[rnd.Next(run.Count)];
                    int how = rnd.Next(4);
                    var lamp = new T { Id = id++, Def = "WallLamp" };
                    string where;
                    if (how == 0) { lamp.Conn = m; lamp.X = m.X; lamp.Z = m.Z + 3; where = "wired to a member"; }
                    else if (how == 1) { lamp.Conn = other; lamp.X = m.X; lamp.Z = m.Z + 1; where = "wired to another line"; }
                    else if (how == 2) { lamp.X = m.X; lamp.Z = m.Z - 1; where = "unwired beside a member"; }
                    else { lamp.X = m.X + 20; lamp.Z = m.Z + 20; where = "unwired far"; }
                    int wear = rnd.Next(4);
                    string worn;
                    if (wear == 0) { lamp.Look = null; worn = "no look"; }
                    else if (wear == 1) { lamp.Look = lineLook ?? D; worn = "the line's look"; }
                    else if (wear == 2) { lamp.Look = looks.First(l => l != (lineLook ?? D)); worn = "a look of its own"; }
                    else { lamp.Look = null; lamp.Foreign = true; worn = "a foreign style"; }
                    regimes[where] = regimes.TryGetValue(where, out int a) ? a + 1 : 1;
                    regimes[worn] = regimes.TryGetValue(worn, out int b) ? b + 1 : 1;
                    var standing = new T { Id = lamp.Id, Def = "StandingLamp", X = lamp.X, Z = lamp.Z, Conn = lamp.Conn, Look = lamp.Look, Foreign = lamp.Foreign };
                    (bool h1, bool f1) = Outcome(run, lamp, isLamp, lineLook, D);
                    (bool h2, bool f2) = Outcome(run, standing, ConduitStyles.IsLampDef, lineLook, D);
                    lamps++;
                    if (h1 != h2 || f1 != f2) worst++;
                }
            }
        }

        private static (bool hooked, bool follows) Outcome(List<T> run, T lamp, Func<string, bool> isLamp, string lineLook, string d)
        {
            var all = new List<T> { lamp }.Where(t => isLamp(t.Def));
            List<T> hooked = ConduitStyles.LampsHookedTo(run, all, t => new[] { (t.X, t.Z) }, t => t.Conn, (p, q) => p.Id.CompareTo(q.Id));
            bool h = hooked.Contains(lamp);
            return (h, h && ConduitStyles.LampFollowsRun(lamp.Look, new HashSet<string> { lineLook ?? d }, true, lamp.Foreign));
        }

        // ------------------------------------------------------------------ the Verse side reads the one lamp list (source read)
        private static void Wiring()
        {
            string dir = SwitchFlipChecks.AerialSourceDir();
            Check(dir != null, "found Source/Aerial");
            if (dir == null) return;
            string picker = File.ReadAllText(Path.Combine(dir, "ConduitStylePicker.cs"));
            string runs = File.ReadAllText(Path.Combine(dir, "RM_MapComponent_ConduitRuns.cs"));
            Check(picker.Contains("defs.AddRange(ConduitStyles.LampDefs);") && picker.Contains("public static bool IsLamp(ThingDef d) => IsOurs(d) && ConduitStyles.IsLampDef(d.defName);"),
                  "the picker registers and recognises every def of ConduitStyles.LampDefs");
            string lo = LookIconChecks.Body(runs, "public List<Thing> LampsOf(");
            Check(lo.Contains("foreach (string dn in ConduitStyles.LampDefs)"), "LampsOf gathers the lamps of every def of ConduitStyles.LampDefs");
            Check(LookIconChecks.Body(runs, "public bool RestyleLamp(").Contains("ConduitStyles.IsLampDef(lamp.def.defName)"), "RestyleLamp takes every lamp def");
            string off = LookIconChecks.Body(picker, "internal static class Patch_Thing_Graphic_LampMasterOff");
            Check(off.Contains("GimmeSomeSlackSettings.enabled || !ConduitStylePicker.IsLamp(__instance.def)") && off.Contains("__result = __instance.DefaultGraphic;"),
                  "with the master switch off every lamp def in one of our looks draws its def's own (vanilla) graphic");
            var named = new List<string>();
            foreach (string f in Directory.GetFiles(dir, "*.cs"))
                foreach (Match m in Regex.Matches(File.ReadAllText(f), "\"(StandingLamp|WallLamp)\""))
                    if (!(Path.GetFileName(f) == "ConduitStyles.cs" && m.Index < File.ReadAllText(f).IndexOf("IsConduitDef(string d)", StringComparison.Ordinal))) named.Add(Path.GetFileName(f));
            Check(named.Count == 0, "no lamp rule in Source/Aerial names a lamp def outside ConduitStyles.LampDefs (" + string.Join(", ", named) + ")");
        }
    }
}
