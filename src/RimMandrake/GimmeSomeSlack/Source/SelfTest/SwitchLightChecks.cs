// T_SWITCH_LIGHT_OFFLINE (bar switch_light_reads_state; RIMMANDRAKE_LIGHT_SLACK_SWITCH_GREEN_RED_DARK_WHEN_UNPOWERED, owner 2026-11-20):
// a powered switch's lamp glows green when closed and red when open; an unpowered switch's lamp is dark; the setting switchLight off
// leaves every lamp dark. The shipped rule (Core/SwitchLight) decides, fed exactly as SwitchLightDraw feeds it from the map.
//
// The range of situations (what the game can vary for this bar):
//   sides     which of the four cardinal side cells carry a transmitter, and which net each belongs to (each side its own net while the
//             switch is open; closed, the switch joins every side into one net, as PowerNetMaker does);
//   power     per net: no source, a source that is not active (an empty battery, a generator off: PowerNet.hasPowerSource true but
//             HasActivePowerSource false), or an active source;
//   state     closed or open; the setting on or off;
//   sequence  power lost while open, power restored while open, a flick while unpowered, a flick with power on the far side only.
// Size: SizeOk, half the radius the owner saw at his walk of 2026-11-22. Left out: the draw itself (position, colour on screen: the art judge and the
// live row sc_switch_light read those) and a
// switch of another size (vanilla's is 1x1).
//
// --switchlight-plant runs the checks against planted wrong rules; each must be caught (a check that cannot fail proves nothing).
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class SwitchLightChecks
    {
        /// <summary>The Mod Settings key this bar's setting flip reads (GimmeSomeSlackSettings.switchLight; the settings sweep finds it here).</summary>
        internal const string SettingKey = "switchLight";

        internal enum Src { None, Dead, Live }

        /// <summary>A switch and its four sides. side[i] = the source state of the net on side i, or null (no transmitter there).</summary>
        internal sealed class Scene
        {
            public Src?[] Side = new Src?[4];
            public bool Closed;
            public bool Setting = true;

            /// <summary>The map read SwitchLightDraw makes. Closed: the switch and every side are one net, live if any part is active.
            /// Open: no own net; each side its own.</summary>
            public (bool own, bool[] sides) Read(bool useHasSourceInsteadOfActive = false)
            {
                bool Live(Src s) => useHasSourceInsteadOfActive ? s != Src.None : s == Src.Live;
                bool[] sides = Side.Select(s => s.HasValue && Live(s.Value)).ToArray();
                if (!Closed) return (false, sides);
                bool joined = sides.Any(x => x);
                return (joined, Side.Select(s => s.HasValue && joined).ToArray());
            }
        }

        /// <summary>A lamp rule under test: (scene) -> lamp. The shipped one reads the scene through Core/SwitchLight.</summary>
        internal delegate SwitchLamp Rule(Scene s);

        internal static SwitchLamp Shipped(Scene s)
        {
            var (own, sides) = s.Read();
            return SwitchLight.Of(s.Setting, s.Closed, SwitchLight.AnySidePowered(own, sides));
        }

        private static int fails, checks;
        private static Action<bool, string> report;

        private static void Check(bool ok, string msg)
        {
            checks++;
            if (!ok) fails++;
            report?.Invoke(ok, "switch light: " + msg);
        }

        private static string Name(Scene s) =>
            (s.Closed ? "closed" : "open") + (s.Setting ? "" : " " + SettingKey + "-off") + " sides[" +
            string.Join(",", s.Side.Select(x => x.HasValue ? x.Value.ToString() : "-")) + "]";

        private static SwitchLamp Expect(Scene s)
        {
            if (!s.Setting) return SwitchLamp.Dark;
            bool anyLive = s.Side.Any(x => x == Src.Live);
            if (!anyLive) return SwitchLamp.Dark;
            return s.Closed ? SwitchLamp.Green : SwitchLamp.Red;
        }

        /// <summary>Every side combination (each side absent / no source / dead source / live source: 4^4), closed and open, setting
        /// on and off: the lamp equals the bar's sentence. Then the sequences. Returns the number of failed checks.</summary>
        internal static int RunWith(Rule rule, Action<bool, string> rep)
        {
            fails = 0; checks = 0; report = rep;
            var opts = new Src?[] { null, Src.None, Src.Dead, Src.Live };
            int n = 0;
            foreach (var a in opts) foreach (var b in opts) foreach (var c in opts) foreach (var d in opts)
                foreach (bool closed in new[] { true, false })
                    foreach (bool setting in new[] { true, false })
                    {
                        var s = new Scene { Side = new[] { a, b, c, d }, Closed = closed, Setting = setting };
                        SwitchLamp got = rule(s), want = Expect(s);
                        Check(got == want, Name(s) + ": lamp " + got + ", the bar says " + want);
                        n++;
                    }
            Check(n == 4 * 4 * 4 * 4 * 2 * 2, "the census covered every case (" + n + ")");

            // the named cases of the brief, each on its own line so a red names it
            var named = new (string name, Scene s, SwitchLamp want)[]
            {
                ("closed + powered", new Scene { Closed = true, Side = new Src?[] { Src.Live, null, Src.None, null } }, SwitchLamp.Green),
                ("open + powered on the north side only", new Scene { Closed = false, Side = new Src?[] { Src.Live, null, Src.None, null } }, SwitchLamp.Red),
                ("open + powered on the south side only", new Scene { Closed = false, Side = new Src?[] { Src.None, null, Src.Live, null } }, SwitchLamp.Red),
                ("open + powered on the west side only (a side port)", new Scene { Closed = false, Side = new Src?[] { null, null, null, Src.Live } }, SwitchLamp.Red),
                ("no power either side", new Scene { Closed = false, Side = new Src?[] { Src.None, null, Src.None, null } }, SwitchLamp.Dark),
                ("no power either side, closed", new Scene { Closed = true, Side = new Src?[] { Src.None, null, Src.None, null } }, SwitchLamp.Dark),
                ("an empty battery is no power", new Scene { Closed = true, Side = new Src?[] { Src.Dead, null, Src.None, null } }, SwitchLamp.Dark),
                ("an empty battery is no power, open", new Scene { Closed = false, Side = new Src?[] { Src.Dead, null, Src.Dead, null } }, SwitchLamp.Dark),
                ("a lone switch, no conduit", new Scene { Closed = true }, SwitchLamp.Dark),
                ("setting off, closed + powered", new Scene { Closed = true, Setting = false, Side = new Src?[] { Src.Live, null, null, null } }, SwitchLamp.Dark),
                ("setting off, open + powered", new Scene { Closed = false, Setting = false, Side = new Src?[] { Src.Live, null, null, null } }, SwitchLamp.Dark),
            };
            foreach (var (name, s, want) in named)
            {
                SwitchLamp got = rule(s);
                Check(got == want, name + ": lamp " + got + ", want " + want);
            }

            // sequences: the lamp is a function of the state now, so every step reads afresh (no stale lamp)
            var q = new Scene { Closed = false, Side = new Src?[] { Src.Live, null, Src.None, null } };
            Check(rule(q) == SwitchLamp.Red, "power lost while open: before, red");
            q.Side[0] = Src.Dead;   // the battery on the north side runs dry
            Check(rule(q) == SwitchLamp.Dark, "power lost while open: after, dark (no stale red)");
            q.Side[0] = Src.Live;
            Check(rule(q) == SwitchLamp.Red, "power back while open: red again");

            // polish (art judge 2026-11-20): the Futuristic closed art's own cyan glow stayed lit on a switch with no power
            Check(SwitchLight.GlowOut("Futuristic", true, false) && !SwitchLight.GlowOut("Futuristic", true, true) && !SwitchLight.GlowOut("Futuristic", false, false) &&
                  !SwitchLight.GlowOut("Modern", true, false) && !SwitchLight.GlowOut(null, true, false),
                  "the Futuristic closed switch draws its glow out when no side has power, and only then");
            Check(SwitchLight.UnlitName(15) == "PowerSwitch_Unlit" && SwitchLight.UnlitName(5) == "PowerSwitch_Unlit_p5", "the unlit picture follows the stubs drawn (PowerSwitch_Unlit, PowerSwitch_Unlit_p5)");

            var u = new Scene { Closed = true, Side = new Src?[] { Src.None, null, Src.None, null } };
            Check(rule(u) == SwitchLamp.Dark, "flick while unpowered: closed, dark");
            u.Closed = false;
            Check(rule(u) == SwitchLamp.Dark, "flick while unpowered: open, dark");
            u.Closed = true;
            Check(rule(u) == SwitchLamp.Dark, "flick while unpowered: closed again, dark");

            var f = new Scene { Closed = false, Side = new Src?[] { Src.None, null, Src.Live, null } };
            Check(rule(f) == SwitchLamp.Red, "power on the far side only, open: red");
            f.Closed = true;
            Check(rule(f) == SwitchLamp.Green, "flick closed with power on the far side only: green (the joined net is live)");
            f.Closed = false;
            Check(rule(f) == SwitchLamp.Red, "flick open again: red (no stale green)");

            var t = new Scene { Closed = true, Side = new Src?[] { Src.Live, null, null, null } };
            Check(rule(t) == SwitchLamp.Green, "setting flip: on, green");
            t.Setting = false;
            Check(rule(t) == SwitchLamp.Dark, "setting flip: off, dark");
            t.Setting = true;
            Check(rule(t) == SwitchLamp.Green, "setting flip: back on, green (no restart)");
            report = null;
            return fails;
        }

        /// <summary>Wrong rules a careless build could ship. Each must turn the run red.</summary>
        internal static readonly (string name, Rule rule)[] Planted =
        {
            ("the base before this item: no lamp, so every switch reads dark", s => SwitchLamp.Dark),
            ("colours swapped (real-switchgear red = closed)", s => { var r = Shipped(s); return r == SwitchLamp.Green ? SwitchLamp.Red : r == SwitchLamp.Red ? SwitchLamp.Green : r; }),
            ("open reads only its own net (no sides): open is always dark", s => { var (own, _) = s.Read(); return SwitchLight.Of(s.Setting, s.Closed, own); }),
            ("reads the north side only", s => { var (own, sides) = s.Read(); return SwitchLight.Of(s.Setting, s.Closed, own || sides[0]); }),
            ("the setting is ignored", s => { var (own, sides) = s.Read(); return SwitchLight.Of(true, s.Closed, SwitchLight.AnySidePowered(own, sides)); }),
            ("hasPowerSource read for HasActivePowerSource (an empty battery lights)", s => { var (own, sides) = s.Read(true); return SwitchLight.Of(s.Setting, s.Closed, SwitchLight.AnySidePowered(own, sides)); }),
            ("unpowered open shows red", s => { var (own, sides) = s.Read(); bool p = SwitchLight.AnySidePowered(own, sides); return !s.Setting ? SwitchLamp.Dark : !s.Closed ? SwitchLamp.Red : p ? SwitchLamp.Green : SwitchLamp.Dark; }),
        };

        /// <summary>The light's drawn size (RIMMANDRAKE_SHRINK_SLACK_SWITCH_LIGHT_TWICE_TOO_WIDE_AT_HIS_WALK; the owner at his walk of 2026-11-22: "twice as large
        /// in radius as it should be"): lens and halo at no more than half the radius he saw, the halo still wider than the lens, and the lens no smaller than the
        /// LED cap it sits beside (a lamp so small it reads as no lamp would break the bar the other way).</summary>
        internal static bool SizeOk(float lens, float halo) =>
            lens <= SwitchLampArt.WalkLensCells / 2 + 1e-4f && halo <= SwitchLampArt.WalkHaloCells / 2 + 1e-4f && halo > lens && lens >= SwitchLampArt.LedCapCells;

        /// <summary>T_CORE entry: the shipped rule, every check through Program.Check.</summary>
        internal static void Run()
        {
            Program.Check(SizeOk(SwitchLampArt.LensCells, SwitchLampArt.HaloCells), "switch light: lens " + SwitchLampArt.LensCells + " and halo " + SwitchLampArt.HaloCells +
                " cells are at most half the size at his walk (" + SwitchLampArt.WalkLensCells + ", " + SwitchLampArt.WalkHaloCells + ")");
            int f = RunWith(Shipped, (ok, msg) => Program.Check(ok, msg));
            Console.WriteLine("switch light: " + (checks - f) + "/" + checks + " checks passed (T_SWITCH_LIGHT_OFFLINE)");
        }

        /// <summary>--switchlight-plant: each planted rule must fail at least one check; the shipped rule must fail none.</summary>
        internal static void Plant()
        {
            int shipped = RunWith(Shipped, null);
            Program.Check(shipped == 0, "switch light plant: the shipped rule passes (" + shipped + " fails)");
            // the size check: the walk's own size, and a lamp shrunk to nothing, are each caught
            bool walkCaught = !SizeOk(SwitchLampArt.WalkLensCells, SwitchLampArt.WalkHaloCells), tinyCaught = !SizeOk(0.02f, 0.05f);
            Console.WriteLine("planted [the size at his walk, 0.16/0.52]: " + (walkCaught ? "CAUGHT" : "NOT CAUGHT") + "; [a lamp shrunk to nothing]: " + (tinyCaught ? "CAUGHT" : "NOT CAUGHT"));
            Program.Check(walkCaught && tinyCaught, "switch light plant: the size check catches the walk's size and a vanished lamp");
            foreach (var (name, rule) in Planted)
            {
                int f = RunWith(rule, null);
                Console.WriteLine("planted [" + name + "]: " + (f > 0 ? "CAUGHT (" + f + " checks red)" : "NOT CAUGHT"));
                Program.Check(f > 0, "switch light plant: " + name + " is caught");
            }
        }
    }
}
