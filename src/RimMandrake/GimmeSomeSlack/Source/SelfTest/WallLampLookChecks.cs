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
//     wall lamp (north, east, south; west is east mirrored), each read from its pixels: base on the wall's face, head out of it;
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
        private static readonly string[] Facings = { "north", "east", "south" };   // Graphic_Multi: west = east mirrored when no _west

        // Where each look's lamp is DRAWN against its wall (owner's walk of 2026-11-24: "Lamps are shown to be pointed INTO the wall rather than OUT OF the
        // wall ... This is true for every look shown"). The check this replaces held the style defs to vanilla's own offsets and to a file per facing: it
        // never read which way a picture's lamp points, so it passed pictures named for the wrong side of their wall.
        // Rot4 North = the wall is NORTH of the lamp's cell (GenConstruct.GetWallAttachedTo: pos + CardinalDirections[rot]).
        /// <summary>The base's outer edge lies within this much past the face line (cells): on the face, not through the wall.</summary>
        public const double SideBaseMax = 0.10, SouthBaseMax = WallMount_SouthBand, NorthBaseMax = 0.08;
        private const double WallMount_SouthBand = Core.WallMount.SouthBand;
        /// <summary>The head reaches at least this far out of the wall, cells.</summary>
        public const double HeadOutMin = 0.2;
        /// <summary>Rows read at each edge of the picture's own box; the base is the widest (a lamp's back plate is wider than its head in all 12).</summary>
        private const int EdgeRows = 4;

        private const string LampClass = "RimMandrake.GimmeSomeSlack.Aerial.Graphic_WallLampLook";

        internal struct Drawn { public string Picture; public bool Flipped; public double BaseAlong, HeadAlong, MidAlong; public string BaseSide; public string Fault; }

        /// <summary>A look's lamp as the engine draws it at <paramref name="rot"/> (0 N, 1 E, 2 S, 3 W): the Graphic_Multi picture and flip, the def's offset, a 1x1 quad.
        /// Distances are cells past the wall's face line, negative = out over the open floor.</summary>
        internal static Drawn DrawnAt(XElement g, string tex, int rot, Func<string, bool> exists)
        {
            string tp = (string)g.Element("texPath");
            string File4(string f) { string q = Path.Combine(tex, (tp + "_" + f).Replace('/', Path.DirectorySeparatorChar) + ".png"); return exists(q) ? q : null; }
            string n = File4("north"), e = File4("east"), s = File4("south"), w = File4("west");
            string pic = null; bool flip = false;
            // the plain Graphic_Multi draws its facing's own picture (the walked build); ours the shipped rule's
            switch ((string)g.Element("graphicClass") == LampClass ? Core.WallLampFacing.PictureRot(rot) : rot)
            {
                case 0: pic = n; break;
                case 1: pic = e ?? w; flip = e == null && w != null; break;
                case 2: pic = s ?? n; break;
                default: pic = w ?? e; flip = w == null && e != null; break;
            }
            var d = new Drawn { Picture = pic == null ? null : Path.GetFileNameWithoutExtension(pic), Flipped = flip };
            if (pic == null) { d.Fault = "no picture"; return d; }
            string[] names = { "drawOffsetNorth", "drawOffsetEast", "drawOffsetSouth", "drawOffsetWest" };
            string ot = (string)g.Element(names[rot]);
            double[] o = ot == null ? new double[] { 0, 0, 0 } : ot.Trim('(', ')', ' ').Split(',').Select(x => double.Parse(x.Trim(), System.Globalization.CultureInfo.InvariantCulture)).ToArray();
            PngAlpha p = PngAlpha.Read(pic);
            int x0 = p.W, x1 = -1, y0 = p.H, y1 = -1;
            for (int y = 0; y < p.H; y++) for (int x = 0; x < p.W; x++) if (p.A(x, y) > 128) { x0 = Math.Min(x0, x); x1 = Math.Max(x1, x); y0 = Math.Min(y0, y); y1 = Math.Max(y1, y); }
            if (x1 < 0) { d.Fault = "an empty picture"; return d; }
            int Span(bool row, int from) { int c = 0; for (int i = 0; i < (row ? p.W : p.H); i++) for (int k = 0; k < EdgeRows; k++) if ((row ? p.A(i, from + k) : p.A(from + k, i)) > 128) { c++; break; } return c; }
            var sides = new Dictionary<string, int> { ["top"] = Span(true, y0), ["bottom"] = Span(true, y1 - EdgeRows + 1), ["left"] = Span(false, x0), ["right"] = Span(false, x1 - EdgeRows + 1) };
            string bs = sides.OrderByDescending(k => k.Value).First().Key;
            // the box in cells about the lamp's cell centre (north up), flipped as drawn
            double l = x0 / (double)p.W - 0.5, r = (x1 + 1) / (double)p.W - 0.5, t = 0.5 - y0 / (double)p.H, b = 0.5 - (y1 + 1) / (double)p.H;
            if (flip) { (l, r) = (-r, -l); bs = bs == "left" ? "right" : bs == "right" ? "left" : bs; }
            l += o[0]; r += o[0]; t += o[2]; b += o[2];
            d.BaseSide = bs;
            string wall = new[] { "top", "right", "bottom", "left" }[rot];
            double wallEdge = rot == 0 ? t : rot == 1 ? r : rot == 2 ? -b : -l, farEdge = rot == 0 ? b : rot == 1 ? l : rot == 2 ? -t : -r;
            d.BaseAlong = wallEdge - 0.5; d.HeadAlong = farEdge - 0.5; d.MidAlong = (d.BaseAlong + d.HeadAlong) / 2;
            double max = rot == 0 ? SouthBaseMax : rot == 2 ? NorthBaseMax : SideBaseMax;
            var f = new List<string>();
            if (bs != wall) f.Add("its base is at the picture's " + bs + ", its wall is " + wall + " (the lamp points " + (d.HeadAlong > 0.02 ? "into the wall" : "the wrong way") + ")");
            if (d.BaseAlong < 0 || d.BaseAlong > max) f.Add("its wall side lies " + F(d.BaseAlong) + " past the face (want 0.." + F(max) + ")");
            if (d.HeadAlong > -HeadOutMin) f.Add("its far side lies " + F(d.HeadAlong) + " past the face (want " + F(-HeadOutMin) + " or further out)");
            if (d.MidAlong > 0) f.Add("more of it lies in the wall than out of it");
            d.Fault = f.Count == 0 ? null : string.Join("; ", f);
            return d;
        }

        private static string F(double v) => v.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture);

        /// <summary>The style def's graphicData of a look's wall lamp.</summary>
        internal static XElement GraphicOf(string root, string look) => XDocument.Load(Path.Combine(root, "Defs", "Aerial", "RM_ConduitStyles.xml")).Root.Elements("ThingStyleDef")
            .First(e => (string)e.Element("defName") == ConduitStyles.StyleDefName("WallLamp", look)).Element("graphicData");

        private static void PointsOut(string root, string tex)
        {
            int bad = 0, read = 0;
            foreach (string look in AerialStyles.Looks)
                for (int rot = 0; rot < 4; rot++)
                {
                    Drawn d = DrawnAt(GraphicOf(root, look), tex, rot, File.Exists);
                    read++;
                    if (d.Fault != null) bad++;
                    Console.WriteLine($"wall lamp looks: {look}, wall to the {new[] { "north", "east", "south", "west" }[rot]}: {d.Picture}{(d.Flipped ? " mirrored" : "")}, base at its {d.BaseSide}; base edge {F(d.BaseAlong)} past the face, head {F(d.HeadAlong)}: {d.Fault ?? "ok"}");
                }
            Check(read == 16 && bad == 0, "each look's lamp sits on its wall's face and points out of the wall, all four facings (" + bad + " of " + read + " do not)");
            // can fail: the walked build's pictures and offsets (ad72a3cec3), made again from today's: the picture of the other side, hung at vanilla's 0.9
            XElement old = new XElement(GraphicOf(root, "Industrial"));
            foreach (var kv in new Dictionary<string, string> { ["drawOffsetNorth"] = "(0,0,0.9)", ["drawOffsetSouth"] = "(0,0,-0.9)", ["drawOffsetWest"] = "(-0.9,0,0)", ["drawOffsetEast"] = "(0.9,0,0)" }) old.SetElementValue(kv.Key, kv.Value);
            int planted = Enumerable.Range(0, 4).Count(k => DrawnAt(old, tex, k, File.Exists).Fault != null);
            Check(planted == 4, "can fail: a lamp hung at vanilla's offsets reads red at every facing (" + planted + " of 4)");
            // and the picture of the other side at today's offset: the base is then at the wrong edge
            XElement plain = new XElement(GraphicOf(root, "Industrial"));
            plain.SetElementValue("graphicClass", "Graphic_Multi");
            int turned = Enumerable.Range(0, 4).Count(k => (DrawnAt(plain, tex, k, File.Exists).Fault ?? "").Contains("its base is at"));
            Check(turned == 4, "can fail: a plain Graphic_Multi (the walked build's class) reads its base at the wrong side at every facing (" + turned + " of 4)");
            string gr = File.ReadAllText(Path.Combine(SwitchFlipChecks.AerialSourceDir(), "Graphic_WallLampLook.cs"));
            Check(gr.Contains("class Graphic_WallLampLook : Graphic_Multi") && gr.Contains("WallLampFacing.PictureRot(rot)") && gr.Contains("MatNorth => Pic(0)") && gr.Contains("MatEast => Pic(1)")
                  && gr.Contains("MatSouth => Pic(2)") && gr.Contains("MatWest => Pic(3)") && gr.Contains("EastFlipped => Flip(1)") && gr.Contains("WestFlipped => Flip(3)"), "the mod's graphic draws by the rule read here (WallLampFacing.PictureRot)");
        }

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
                Check(faults.Count == 0, "every wall lamp look is a Graphic_WallLampLook style def on its own art, with a picture for every facing");
                PointsOut(root, LookIconChecks.TexturesDir());
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
                if ((string)g?.Element("graphicClass") != LampClass) f.Add(n + ": not " + LampClass + " (a wall lamp points away from its wall)");
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
            // a wall lamp (BuildingOnTop) hangs in front of a cord's plate in the same wall cell: the plates, holes and what is drawn on them (up to FaceLift + 0.004)
            // lie under that layer (the walked build drew the plate over the lamp's base, station 33)
            string sec = File.ReadAllText(Path.Combine(Path.GetDirectoryName(dir), "SectionLayer_RM_MessyCords.cs"));
            Match lift = Regex.Match(sec, @"public const float FaceLift = (-?[0-9.]+)f;");
            Check(lift.Success && double.Parse(lift.Groups[1].Value, System.Globalization.CultureInfo.InvariantCulture) + 0.004 < 0 && sec.Contains("AltitudeLayer.BuildingOnTop.AltitudeFor() + FaceLift"),
                  "a wall plate is drawn behind a wall lamp in its cell (FaceLift " + (lift.Success ? lift.Groups[1].Value : "not found") + ", want under -0.004)");
            var named = new List<string>();
            foreach (string f in Directory.GetFiles(dir, "*.cs"))
                foreach (Match m in Regex.Matches(File.ReadAllText(f), "\"(StandingLamp|WallLamp)\""))
                    if (!(Path.GetFileName(f) == "ConduitStyles.cs" && m.Index < File.ReadAllText(f).IndexOf("IsConduitDef(string d)", StringComparison.Ordinal))) named.Add(Path.GetFileName(f));
            Check(named.Count == 0, "no lamp rule in Source/Aerial names a lamp def outside ConduitStyles.LampDefs (" + string.Join(", ", named) + ")");
        }
    }
}
