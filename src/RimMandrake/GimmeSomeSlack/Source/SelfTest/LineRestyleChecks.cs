// T_LINE_RESTYLE_OFFLINE (Gimme Some Slack 0.2.0, bar restyle_whole_line, design/concepts/GimmeSomeSlack/record.json; owner
// 2026-11-22: "GSS needs 'change everything on this line' (for GSS items). They don't need to change each other's items though.")
// "All connected" from any GSS piece of a line (a floor cord, a power switch, a pole or a wall bracket) takes every GSS piece
// on that line -- cords, switches, poles and brackets, across the overhead spans between them -- and the lamps hooked to it
// that wear its look; a FlowWorks item on the same cells keeps its own look; a cut overhead wire ends the line.
//
// What runs is the SHIPPED decision: ConduitStyles.RunNeighbours (the neighbour rule RM_MapComponent_ConduitRuns.Neighbours
// feeds the map), ConduitStyles.RunMembers (the flood RunOf calls), ConduitStyles.LampsHookedTo (LampsOf), ConduitStyles.
// IsRunMemberDef / IsBridge (ConduitStylePicker's member set, IsBridgeConduit) and LampFollowsRun (RestyleRun), composed as
// RestyleRun composes them (a source read below holds the Verse side to that composition). The oracle is the GENERATOR's
// own construction: it lays each line leg by leg and knows which line every piece belongs to, never by flooding.
//
// Declared range (what the game can vary for this bar; one generated map per case):
//   * seed: every member of every line is pressed in turn (PowerConduit, WaterproofConduit, PowerSwitch alone or over a
//     conduit, RM_AerialMast, RM_AerialLampMast, RM_AerialWallBracket, each anchor on its cord's cell over a conduit or beside it);
//   * shape: 1-4 legs of cardinal cord walks (0-6 cells), legs joined by an overhead span anchor-to-anchor 3-12 cells long in
//     any direction; each span up, cut, or its far anchor gone from the map (despawned) -- the last two split the line;
//   * company: 0-2 other lines nearby (diagonal touches allowed, a cardinal touch would make one power net, so the
//     generator never lays one), a FlowWorks pipe pole (RM_PipePole) on a line's conduit cell or beside an anchor with its
//     own pipe span, FlowWorks pipe (RM_UniversalPipe) on line cells, another mod's power conduit inside a leg (drawn as
//     cords -> a bridge the flood walks through; or unticked in settings -> not drawn, it ends the line);
//   * lamps (StandingLamp) wired to a member of this line, to another mod's conduit drawn in this line (a bridge), to a
//     member of another line, or unwired beside a member or beside nothing;
//     wearing no look, a look the line draws, another look (styled on purpose) or a foreign style;
//   * a wall lamp built before the cord: the drawn hookup moves to the new conduit end, with the battery still its power parent;
//   * member looks: none (legacy, draws the default) or one of the four, sometimes mixed in one line;
//   * lines laid along the map edge (InBounds), thing ids in random order.
// Left out (why): the GSS master switch off (no style button: Patch_Building_GetGizmos_Restyle, so the bar's step never
// happens); power on/off, a switch's position, faction (not inputs of the neighbour rule: source read below); All connected
// from a floor lamp (the bar names cord, switch, pole, bracket); pending links / excluded members / a cut argument (RestyleRun
// drains the queue first and calls RunOf(t) bare); an unstylable PowerSwitch (the mod's own patch; it logs a warning when
// skipped); HiddenConduit (never drawn as cord); walls behind brackets (no joining thing); a lamp wired to an unticked
// foreign conduit (GSS draws no line there, so no line of GSS's to be hooked to).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class LineRestyleChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "line restyle: " + msg);
        private const string D = "Scrapper";                 // the default look a member storing none draws (any of the four works)
        private const int W = 40, H = 40;                     // map size (bounds read by RunNeighbours' InBounds)
        public const int Cases = 3000;                        // generated maps; every member of every line is a seed

        // def facts (read from the defs, not decided here): ours = carries GSS's stage-2 style field (byDef), cord = drawn as cord
        private static readonly Dictionary<string, (bool ours, bool cord)> Facts = new Dictionary<string, (bool, bool)>
        {
            ["PowerConduit"] = (true, true), ["WaterproofConduit"] = (true, true), ["PowerSwitch"] = (true, false),
            ["StandingLamp"] = (true, false),
            ["RM_AerialMast"] = (false, false), ["RM_AerialLampMast"] = (false, false), ["RM_AerialWallBracket"] = (false, false),
            ["RM_PipePole"] = (false, false), ["RM_UniversalPipe"] = (false, false),
            [ForeignCord] = (false, true), [ForeignUnticked] = (false, false),
        };
        // another mod's power conduit (model names: the rule reads only the two facts)
        private const string ForeignCord = "OtherModConduit_DrawnAsCord", ForeignUnticked = "OtherModConduit_Unticked";
        // the bar: "a floor cord, a power switch, a pole or a wall bracket" (the cords are the two stylable conduits)
        private static readonly HashSet<string> BarPieces = new HashSet<string>
            { "PowerConduit", "WaterproofConduit", "PowerSwitch", "RM_AerialMast", "RM_AerialLampMast", "RM_AerialWallBracket" };
        private static readonly string[] Anchors = { "RM_AerialMast", "RM_AerialLampMast", "RM_AerialWallBracket" };

        internal sealed class P
        {
            public int Id; public string Def; public int X, Z; public int Line = -1; public bool Spawned = true;
            public readonly List<(P other, bool up)> Spans = new List<(P, bool)>();
            public P Conn; public string Look; public bool Foreign;
            // the oracle's facts, from the bar's wording and the generator's construction (never the shipped rule, so a fault in
            // the rule cannot move the generator or the oracle with it): a GSS piece of a line, and another mod's drawn conduit
            public bool Member => BarPieces.Contains(Def);
            public bool Bridge => Def == ForeignCord;
            // the shipped rule (what RM_MapComponent_ConduitRuns feeds the flood): ConduitStylePicker.IsMember, IsBridgeConduit
            public bool ShippedMember => ConduitStyles.IsRunMemberDef(Def, Facts[Def].ours);
            public bool ShippedBridge => ConduitStyles.IsBridge(Facts[Def].ours, Facts[Def].cord);
            public bool IsLamp => ConduitStyles.IsLampDef(Def);
            public bool IsFlowWorks => Def == "RM_PipePole" || Def == "RM_UniversalPipe";
            public override string ToString() => Def + "#" + Id + "@" + X + "," + Z + " line " + Line;
        }

        private enum Layer { Building, Conduit, Pipe }
        private static Layer LayerOf(string def) =>
            def == "RM_UniversalPipe" ? Layer.Pipe : ConduitStyles.IsConduitDef(def) || def == ForeignCord || def == ForeignUnticked ? Layer.Conduit : Layer.Building;

        internal sealed class Scene
        {
            public readonly Dictionary<(int, int), List<P>> Grid = new Dictionary<(int, int), List<P>>();
            public readonly List<P> All = new List<P>();
            public int Lines;
            public readonly Dictionary<string, int> Seen = new Dictionary<string, int>();   // regime coverage
            public IList<P> At((int x, int z) c) => Grid.TryGetValue(c, out var l) ? l : (IList<P>)Array.Empty<P>();
            public void Count(string k) { Seen.TryGetValue(k, out int n); Seen[k] = n + 1; }
        }

        // ------------------------------------------------------------------ the shipped decision, composed as RestyleRun does
        internal sealed class Rule
        {
            public bool DropSpans, IgnoreCut, JoinAnything, NoBridgeLamps;   // instrument self-checks only (the can-fails); production = all false
        }

        internal static IEnumerable<P> Nbrs(Scene s, P t, Rule r) => ConduitStyles.RunNeighbours(
            t, new[] { (t.X, t.Z) },
            c => c.x >= 0 && c.z >= 0 && c.x < W && c.z < H,
            c => s.At(c),
            x => r.JoinAnything || x.ShippedMember || x.ShippedBridge,          // production: ConduitStylePicker.IsMember(x.def) || IsBridgeConduit(x.def)
            r.DropSpans ? null : t.Spans.Select(sp => (sp.other, (sp.up || r.IgnoreCut) && sp.other != null && sp.other.Spawned)));

        internal static (List<P> run, List<P> follow) AllConnected(Scene s, P seed, Rule r)
        {
            List<P> run = ConduitStyles.RunMembers(seed, x => Nbrs(s, x, r), null, null, null, (a, b) => false,
                Array.Empty<(P, P)>(), x => x.ShippedBridge, (p, q) => p.Id.CompareTo(q.Id));
            var drew = new ConduitStyles.LookSet(D);
            foreach (P m in run) drew.Add(m.Look, ConduitStyles.IsConduitDef(m.Def), null);
            List<P> lamps = ConduitStyles.LampsHookedTo(run, s.All.Where(p => p.IsLamp && p.Spawned),
                x => new[] { (x.X, x.Z) }, x => x.Conn, (p, q) => p.Id.CompareTo(q.Id),
                r.NoBridgeLamps ? null : (Func<P, IEnumerable<P>>)(x => Nbrs(s, x, r).Where(n => n.ShippedBridge)));
            return (run, lamps.Where(l => ConduitStyles.LampFollowsRun(l.Look, drew.Looks, true, l.Foreign)).ToList());
        }

        // ------------------------------------------------------------------ the oracle: the generator's construction
        private static bool TouchesMemberOf(Scene s, P lamp, int line)
        {
            foreach ((int dx, int dz) in new[] { (0, 0), (0, 1), (1, 0), (0, -1), (-1, 0) })
                foreach (P q in s.At((lamp.X + dx, lamp.Z + dz))) if (q.Spawned && q.Line == line && q.Member) return true;
            return false;
        }

        /// <summary>Bar: hooked to the line (wired to one of its GSS pieces; unwired: standing on or beside one, design D2) and
        /// wearing its look (no look of its own, or a look some piece of the line draws; never a foreign style).</summary>
        private static bool OracleLampFollows(Scene s, P lamp, int line)
        {
            bool hooked = lamp.Conn != null ? (lamp.Conn.Member || lamp.Conn.Bridge) && lamp.Conn.Line == line : TouchesMemberOf(s, lamp, line);
            if (!hooked || lamp.Foreign) return false;
            if (lamp.Look == null) return true;
            return s.All.Any(m => m.Spawned && m.Line == line && m.Member && (m.Look ?? D) == lamp.Look);
        }

        internal sealed class Tally
        {
            public int Scenes, Floods, Worst, WorstFlowWorks, WorstCutCrossed, WorstMissed, WorstLamp;
            public string WorstWhat;
            public readonly Dictionary<string, int> Seeds = new Dictionary<string, int>();
            public readonly Dictionary<string, int> Regimes = new Dictionary<string, int>();
        }

        internal static void Read(Scene s, Rule r, Tally t)
        {
            t.Scenes++;
            foreach (var kv in s.Seen) { t.Regimes.TryGetValue(kv.Key, out int n); t.Regimes[kv.Key] = n + 1; }
            foreach (P seed in s.All.Where(p => p.Spawned && p.Member))
            {
                t.Floods++;
                t.Seeds.TryGetValue(seed.Def, out int sn); t.Seeds[seed.Def] = sn + 1;
                (List<P> run, List<P> follow) = AllConnected(s, seed, r);
                var want = s.All.Where(p => p.Spawned && p.Member && p.Line == seed.Line).ToList();
                var runSet = new HashSet<P>(run);
                int missed = want.Count(p => !runSet.Contains(p));
                int flowWorks = run.Count(p => p.IsFlowWorks);
                int crossed = run.Count(p => p.Line != seed.Line && p.Member);
                int other = run.Count(p => !p.Member && !p.IsFlowWorks);          // a bridge, lamp or anything else painted
                var wantLamps = s.All.Where(p => p.IsLamp && p.Spawned && OracleLampFollows(s, p, seed.Line)).ToList();
                int lampWrong = wantLamps.Count(l => !follow.Contains(l)) + follow.Count(l => !wantLamps.Contains(l));
                int wrong = missed + flowWorks + crossed + other + lampWrong;
                t.WorstMissed = Math.Max(t.WorstMissed, missed);
                t.WorstFlowWorks = Math.Max(t.WorstFlowWorks, flowWorks);
                t.WorstCutCrossed = Math.Max(t.WorstCutCrossed, crossed);
                t.WorstLamp = Math.Max(t.WorstLamp, lampWrong);
                if (wrong > t.Worst)
                {
                    t.Worst = wrong;
                    t.WorstWhat = "seed " + seed + ": missed " + missed + " [" + string.Join(" ", want.Where(p => !runSet.Contains(p)).Take(4)) + "], FlowWorks " + flowWorks +
                                  ", other lines " + crossed + ", non-members " + other + ", lamps wrong " + lampWrong;
                }
            }
        }

        // ------------------------------------------------------------------ the generator
        private static readonly (int dx, int dz)[] Card = { (0, 1), (1, 0), (0, -1), (-1, 0) };

        private static bool Joins(string def) => BarPieces.Contains(def) || def == ForeignCord;   // construction: what carries a GSS line

        /// <summary>May a piece of def go at c for the given line: in bounds, its layer free, and (if it joins runs) no joining
        /// piece of ANOTHER line on or cardinally beside c (that would make one power net, so one line: not what was laid).</summary>
        private static bool Free(Scene s, string def, int x, int z, int line)
        {
            if (x < 0 || z < 0 || x >= W || z >= H) return false;
            Layer ly = LayerOf(def);
            if (s.At((x, z)).Any(q => LayerOf(q.Def) == ly)) return false;
            if (!Joins(def)) return true;
            foreach ((int dx, int dz) in new[] { (0, 0), (0, 1), (1, 0), (0, -1), (-1, 0) })
                foreach (P q in s.At((x + dx, z + dz))) if (Joins(q.Def) && q.Line != line) return false;
            return true;
        }

        private static P Put(Scene s, string def, int x, int z, int line)
        {
            var p = new P { Def = def, X = x, Z = z, Line = line };
            s.All.Add(p);
            if (!s.Grid.TryGetValue((x, z), out var l)) s.Grid[(x, z)] = l = new List<P>();
            l.Add(p);
            return p;
        }

        private static string CordDef(Random rng, Scene s)
        {
            int k = rng.Next(100);
            if (k < 70) return "PowerConduit";
            if (k < 85) return "WaterproofConduit";
            if (k < 95) { s.Count("bridge conduit in a leg"); return ForeignCord; }
            s.Count("unticked foreign conduit in a leg");
            return ForeignUnticked;
        }

        private static void Line(Scene s, Random rng, Dictionary<int, string> lineLook)
        {
            int line = s.Lines++;
            int x, z, tries = 0;
            do
            {
                bool edge = rng.Next(100) < 15;
                x = edge && rng.Next(2) == 0 ? 0 : rng.Next(W); z = edge && x != 0 ? 0 : rng.Next(H);
            } while (!Free(s, "PowerConduit", x, z, line) && ++tries < 50);
            if (tries >= 50) return;
            if (x == 0 || z == 0) s.Count("line on the map edge");
            int legs = 1 + rng.Next(4);
            for (int leg = 0; leg < legs; leg++)
            {
                lineLook[line] = lineLook.TryGetValue(line, out string lk) ? lk : (rng.Next(5) == 0 ? null : AerialStyles.Looks[rng.Next(4)]);
                int len = rng.Next(leg == 0 ? 1 : 0, 7);
                int px = x, pz = z;
                bool laid = false;
                for (int i = 0; i < len; i++)
                {
                    int cx = px, cz = pz;
                    if (i > 0 || leg > 0)
                    {
                        var dirs = Card.OrderBy(_ => rng.Next()).ToList();
                        bool ok = false;
                        foreach ((int dx, int dz) in dirs)
                            if (Free(s, "PowerConduit", px + dx, pz + dz, line)) { cx = px + dx; cz = pz + dz; ok = true; break; }
                        if (!ok) break;
                    }
                    else if (!Free(s, "PowerConduit", cx, cz, line)) break;
                    int k = rng.Next(100);
                    if (k < 8 && Free(s, "PowerSwitch", cx, cz, line)) { Put(s, "PowerSwitch", cx, cz, line); s.Count("switch alone on its cell"); }
                    else
                    {
                        string cd = CordDef(rng, s);
                        Put(s, cd, cx, cz, line);
                        if (cd == ForeignUnticked)
                        {   // not drawn as cord, so not a bridge: GSS's line ends here and the cells beyond are a new line
                            line = s.Lines++;
                            lineLook[line] = rng.Next(5) == 0 ? null : AerialStyles.Looks[rng.Next(4)];
                        }
                        else if (k < 14 && Free(s, "PowerSwitch", cx, cz, line)) { Put(s, "PowerSwitch", cx, cz, line); s.Count("switch over a conduit"); }
                    }
                    px = cx; pz = cz; laid = true;
                }
                if (leg == legs - 1) break;
                // the leg's anchor: on its last cord cell (over the conduit) or beside it
                string ad = Anchors[rng.Next(3)];
                int ax = px, az = pz;
                bool beside = !laid || rng.Next(2) == 0 || !Free(s, ad, ax, az, line);
                if (beside)
                {
                    bool ok = false;
                    foreach ((int dx, int dz) in Card.OrderBy(_ => rng.Next()))
                        if (Free(s, ad, px + dx, pz + dz, line)) { ax = px + dx; az = pz + dz; ok = true; break; }
                    if (!ok) break;
                }
                P a = Put(s, ad, ax, az, line);
                s.Count(beside ? "anchor beside its cord" : "anchor over its conduit");
                // the overhead span to the next anchor
                int state = rng.Next(100);       // <65 up, <90 cut, else the far anchor despawned
                int nline = state < 65 ? line : s.Lines++;
                string bd = Anchors[rng.Next(3)];
                P b = null;
                for (int t2 = 0; t2 < 30 && b == null; t2++)
                {
                    double ang = rng.NextDouble() * 2 * Math.PI; int dist = 3 + rng.Next(10);
                    int bx = ax + (int)Math.Round(Math.Cos(ang) * dist), bz = az + (int)Math.Round(Math.Sin(ang) * dist);
                    if (Free(s, bd, bx, bz, nline)) b = Put(s, bd, bx, bz, nline);
                }
                if (b == null) break;
                bool up = state < 65;
                a.Spans.Add((b, up)); b.Spans.Add((a, up));
                if (state >= 90) { b.Spawned = false; s.Grid[(b.X, b.Z)].Remove(b); s.Count("span partner despawned"); }
                else s.Count(up ? "span up" : "span cut");
                line = nline;
                x = b.X; z = b.Z;
                if (!up) lineLook[line] = rng.Next(5) == 0 ? null : AerialStyles.Looks[rng.Next(4)];
                // next leg starts on the far anchor's cell (a conduit under it) or beside it
                if (rng.Next(2) == 0 && b.Spawned && Free(s, "PowerConduit", x, z, line)) { Put(s, CordDef(rng, s), x, z, line); }
            }
        }

        internal static Scene Generate(int seed)
        {
            var rng = new Random(seed);
            var s = new Scene();
            var lineLook = new Dictionary<int, string>();
            int lines = 1 + rng.Next(3);
            for (int i = 0; i < lines; i++) Line(s, rng, lineLook);
            if (s.Lines > 1) s.Count("several lines on the map");
            // looks: each member its line's look, sometimes its own (a mixed line)
            foreach (P p in s.All.Where(q => q.Member))
            {
                lineLook.TryGetValue(p.Line, out string lk);
                p.Look = rng.Next(100) < 12 ? (rng.Next(4) == 0 ? null : AerialStyles.Looks[rng.Next(4)]) : lk;
            }
            var lineCells = s.All.Where(q => q.Spawned && (q.Member || q.Bridge)).ToList();
            if (lineCells.Count == 0) return s;
            // FlowWorks: pipe poles on a line's conduit cell or beside an anchor, each with its own pipe span; pipe on line cells
            int poles = rng.Next(3);
            for (int i = 0; i < poles; i++)
            {
                P near = lineCells[rng.Next(lineCells.Count)];
                var spots = new List<(int, int)> { (near.X, near.Z) };
                spots.AddRange(Card.Select(d => (near.X + d.dx, near.Z + d.dz)));
                foreach ((int px, int pz) in spots.OrderBy(_ => rng.Next()))
                    if (Free(s, "RM_PipePole", px, pz, -1))
                    {
                        P pp = Put(s, "RM_PipePole", px, pz, -1);
                        s.Count(s.At((px, pz)).Any(q => q.Member || q.Bridge) ? "pipe pole on a line cell" : "pipe pole beside a line");
                        for (int t2 = 0; t2 < 20; t2++)
                        {
                            int qx = px + rng.Next(-8, 9), qz = pz + rng.Next(-8, 9);
                            if ((qx != px || qz != pz) && Free(s, "RM_PipePole", qx, qz, -1))
                            {
                                P q = Put(s, "RM_PipePole", qx, qz, -1);
                                pp.Spans.Add((q, true)); q.Spans.Add((pp, true));
                                s.Count("pipe span up");
                                break;
                            }
                        }
                        break;
                    }
            }
            int pipes = rng.Next(4);
            for (int i = 0; i < pipes; i++)
            {
                P near = lineCells[rng.Next(lineCells.Count)];
                if (Free(s, "RM_UniversalPipe", near.X, near.Z, -1)) { Put(s, "RM_UniversalPipe", near.X, near.Z, -1); s.Count("FlowWorks pipe on a line cell"); }
            }
            // lamps
            var members = s.All.Where(q => q.Spawned && q.Member).ToList();
            int lamps = members.Count == 0 ? 0 : rng.Next(4);
            for (int i = 0; i < lamps; i++)
            {
                P near = members[rng.Next(members.Count)];
                int mode = rng.Next(100);
                (int lx, int lz) spot = (-1, -1);
                var spots = new List<(int, int)> { (near.X, near.Z) };
                spots.AddRange(Card.Select(d => (near.X + d.dx, near.Z + d.dz)));
                if (mode >= 90) spots = Enumerable.Range(0, 20).Select(_ => (rng.Next(W), rng.Next(H))).ToList();   // unwired, far from anything
                foreach ((int px, int pz) in spots.OrderBy(_ => rng.Next())) if (Free(s, "StandingLamp", px, pz, -1)) { spot = (px, pz); break; }
                if (spot.lx < 0) continue;
                P l = Put(s, "StandingLamp", spot.lx, spot.lz, -1);
                if (mode < 55) { l.Conn = members[rng.Next(members.Count)]; s.Count(l.Conn.Line == near.Line ? "lamp wired to a member" : "lamp wired to a member of another line"); }
                else if (mode < 62 && s.All.Any(q => q.Spawned && q.Bridge && q.Line == near.Line))
                {   // wired to another mod's conduit drawn in the line: the power net is the line's, so it is hooked to the line
                    var br = s.All.Where(q => q.Spawned && q.Bridge && q.Line == near.Line).ToList();
                    l.Conn = br[rng.Next(br.Count)]; s.Count("lamp wired to a bridge conduit of the line");
                }
                else if (mode < 70) { var others = members.Where(q => q.Line != near.Line).ToList(); l.Conn = others.Count > 0 ? others[rng.Next(others.Count)] : near; s.Count("lamp wired to a member of another line"); }
                else s.Count(mode < 90 ? "lamp unwired beside a member" : "lamp unwired");
                int lookMode = rng.Next(100);
                if (lookMode < 25) { l.Look = null; s.Count("lamp with no look"); }
                else if (lookMode < 65)
                {
                    int ln = l.Conn?.Line ?? near.Line;
                    var drawn = members.Where(q => q.Line == ln).Select(q => q.Look ?? D).Distinct().ToList();
                    l.Look = drawn.Count > 0 ? drawn[rng.Next(drawn.Count)] : D; s.Count("lamp wearing its line's look");
                }
                else if (lookMode < 90) { l.Look = AerialStyles.Looks[rng.Next(4)]; s.Count("lamp with a look of its own"); }
                else { l.Foreign = true; s.Count("lamp in a foreign style"); }
            }
            if (members.Select(q => q.Look ?? D).Distinct().Count() > 1) s.Count("mixed looks");
            // random thing ids
            var ids = Enumerable.Range(1, s.All.Count).OrderBy(_ => rng.Next()).ToList();
            for (int i = 0; i < s.All.Count; i++) s.All[i].Id = ids[i];
            return s;
        }

        // ------------------------------------------------------------------ the named scene of the test row
        /// <summary>Floor cords, a power switch, two poles joined by an overhead span, a wall bracket, a hooked lamp and a FlowWorks
        /// pipe pole on the line's cells; with the span up, then cut.</summary>
        internal static Scene RowScene(bool cut)
        {
            var s = new Scene { Lines = 2 };
            int id = 1;
            P Add(string def, int x, int z, int line) { P p = Put(s, def, x, z, line); p.Id = id++; p.Look = def == "StandingLamp" || def == "RM_PipePole" ? null : "Industrial"; return p; }
            int far = cut ? 1 : 0;
            Add("PowerConduit", 2, 2, 0); Add("PowerConduit", 3, 2, 0); Add("PowerSwitch", 4, 2, 0); Add("PowerConduit", 5, 2, 0);
            P mast = Add("RM_AerialMast", 6, 2, 0); Add("PowerConduit", 6, 2, 0);
            Add("RM_PipePole", 3, 3, -1);                                  // FlowWorks pipe pole beside the cord
            P pp2 = Add("RM_PipePole", 6, 3, -1);                          // and one beside the mast, on the line's cells
            P lampMast = Add("RM_AerialLampMast", 14, 2, far);
            mast.Spans.Add((lampMast, !cut)); lampMast.Spans.Add((mast, !cut));
            Add("PowerConduit", 14, 3, far); Add("PowerConduit", 14, 4, far); Add("WaterproofConduit", 14, 5, far);
            Add("RM_AerialWallBracket", 14, 6, far);
            P lamp = Add("StandingLamp", 15, 4, -1); lamp.Conn = s.Grid[(14, 4)][0];  // hooked to the far leg, wearing nothing of its own
            P pp1 = s.Grid[(3, 3)][0]; pp1.Spans.Add((pp2, true)); pp2.Spans.Add((pp1, true));
            return s;
        }

        // ------------------------------------------------------------------ run
        public static void Run()
        {
            var prod = new Rule();
            // 1. the test row's own scene, span up: All connected from each member kind takes all 9 GSS pieces + the lamp
            Scene up = RowScene(false);
            foreach (P seed in up.All.Where(p => p.Member))
            {
                (List<P> run, List<P> follow) = AllConnected(up, seed, prod);
                Check(run.Count == 11 && run.All(p => p.Member) && follow.Count == 1,
                      "row scene, span up: All connected from " + seed.Def + " takes " + run.Count + " pieces (want 11: 6 power conduits, waterproof, switch, mast, lamp mast, bracket), FlowWorks " +
                      run.Count(p => p.IsFlowWorks) + ", lamps " + follow.Count + " (want 1)");
            }
            Scene cut = RowScene(true);
            var sides = cut.All.Where(p => p.Member).Select(p => string.Join(",", AllConnected(cut, p, prod).run.Select(q => q.Id))).Distinct().ToList();
            Check(sides.Count == 2, "row scene, span cut: the line splits in two (" + sides.Count + " distinct runs over every seed, want 2)");
            Check(AllConnected(cut, cut.All.First(p => p.Def == "PowerSwitch"), prod).follow.Count == 0 &&
                  AllConnected(cut, cut.All.First(p => p.Def == "RM_AerialWallBracket"), prod).follow.Count == 1,
                  "row scene, span cut: the lamp follows only the leg it is wired to");

            // 2. the generated range
            var t = new Tally();
            for (int i = 0; i < Cases; i++) Read(Generate(7919 * i + 13), prod, t);
            Console.WriteLine("line restyle: " + t.Scenes + " generated maps, " + t.Floods + " All-connected floods (seeds " +
                              string.Join(", ", t.Seeds.OrderBy(k => k.Key).Select(k => k.Key + " " + k.Value)) + ")");
            Console.WriteLine("line restyle: worst wrong pieces per flood " + t.Worst + " (limit 0): missed GSS " + t.WorstMissed + ", FlowWorks taken " + t.WorstFlowWorks +
                              ", across a cut/other line " + t.WorstCutCrossed + ", lamps wrong " + t.WorstLamp + (t.WorstWhat == null ? "" : "; worst: " + t.WorstWhat));
            Console.WriteLine("line restyle: regimes (maps having each): " + string.Join(", ", t.Regimes.OrderBy(k => k.Key).Select(k => k.Key + " " + k.Value)));
            Check(t.Worst == 0, "generated range: every flood takes exactly its line's GSS pieces and following lamps (worst " + t.Worst + ", limit 0, " + t.Floods + " floods)");
            foreach (string d in new[] { "PowerConduit", "WaterproofConduit", "PowerSwitch", "RM_AerialMast", "RM_AerialLampMast", "RM_AerialWallBracket" })
                Check(t.Seeds.TryGetValue(d, out int n) && n >= 100, "range covers All connected from " + d + " (" + (t.Seeds.TryGetValue(d, out int m) ? m : 0) + " floods, floor 100)");
            foreach (string r in new[] { "span up", "span cut", "span partner despawned", "pipe pole on a line cell", "pipe pole beside a line", "FlowWorks pipe on a line cell",
                                         "bridge conduit in a leg", "unticked foreign conduit in a leg", "anchor over its conduit", "anchor beside its cord", "switch alone on its cell",
                                         "switch over a conduit", "lamp wired to a member", "lamp wired to a bridge conduit of the line", "lamp wired to a member of another line", "lamp unwired beside a member", "lamp unwired",
                                         "lamp with no look", "lamp wearing its line's look", "lamp with a look of its own", "lamp in a foreign style", "mixed looks",
                                         "line on the map edge", "several lines on the map" })
                Check(t.Regimes.TryGetValue(r, out int n) && n >= 30, "range covers '" + r + "' (" + (t.Regimes.TryGetValue(r, out int m) ? m : 0) + " maps, floor 30)");

            // 3. can-fail: the same reading over a broken rule must go red (the instrument can see each fault)
            CanFail("a flood that stops at a pole (span partners dropped)", new Rule { DropSpans = true }, x => x.WorstMissed);
            CanFail("a flood that takes anything on its cells (the pipe pole)", new Rule { JoinAnything = true }, x => x.WorstFlowWorks);
            CanFail("a flood across a cut overhead wire", new Rule { IgnoreCut = true }, x => x.WorstCutCrossed);
            CanFail("a lamp wired to another mod's conduit in the line left behind (the 0.2.0 code before this fix)", new Rule { NoBridgeLamps = true }, x => x.WorstLamp, 3000);

            Wiring();
        }

        private static void LampBuiltBeforeCord(bool usesDrawnConnection)
        {
            var world = new CordWorld(W, H);
            var machine = new MachineInfo { Id = "c2", X0 = 14, Z0 = 10, W = 1, H = 1, HasHome = true, HomeX = 14, HomeZ = 11 };
            var battery = new P { Id = 1, Def = "Battery", X = 10, Z = 10 };
            var lamp = new P { Id = 2, Def = "WallLamp", X = 14, Z = 10, Conn = battery, Look = "Industrial" };
            var cord = new List<P>();
            // A lamp wired to a battery has no parent conduit cell. The new cord joins the battery's existing net.
            Check(HookupPick.Pick(world, machine, null, _ => true) == null,
                  "before laying the cord, the wall lamp has no conduit hookup");
            for (int x = 11; x <= 13; x++)
            {
                world.SetConduit(new Cell(x, 10));
                cord.Add(new P { Id = x, Def = "PowerConduit", X = x, Z = 10, Look = "Industrial" });
            }
            List<Cell> hookups = HookupPick.Pick(world, machine, null, _ => true);
            var end = new Cell(13, 10);
            Check(hookups != null && hookups.SequenceEqual(new[] { end }) && lamp.Conn == battery,
                  "after laying the cord, the wall lamp draws to (13,10) with the battery still its power parent");
            machine.Hookups.AddRange(hookups ?? new List<Cell>());
            world.Machines.Add(machine);
            Check(CordGraph.Reduce(world).CordEdges().Any(e => e.Chain().Contains(VId.Mach(machine.Id)) && e.Chain().Contains(VId.C(end))),
                  "the cord graph joins the wall lamp to (13,10)");

            // Compose the shipped hookup and lamp-membership rules, using the connection callback that LampsOf supplies.
            Cell? drawnEnd = usesDrawnConnection ? HookupPick.PickEnd(machine, null, world.IsConduit, c => HookupPick.Degree(world, c), _ => true) : null;
            List<P> hooked = ConduitStyles.LampsHookedTo(cord, new[] { lamp }, p => new[] { (p.X, p.Z) },
                p => drawnEnd.HasValue ? cord.Find(q => new Cell(q.X, q.Z) == drawnEnd.Value) : p.Conn,
                (p, q) => p.Id.CompareTo(q.Id));
            var drewBefore = new HashSet<string>(cord.Select(p => p.Look));
            foreach (P p in cord) p.Look = "Modern";
            foreach (P p in hooked)
                if (ConduitStyles.LampFollowsRun(p.Look, drewBefore, true, p.Foreign)) p.Look = "Modern";
            Check(cord.All(p => p.Look == "Modern") && lamp.Look == "Modern" && lamp.Conn == battery,
                  "All connected on the new cord: cord " + cord[0].Look + ", wall lamp " + lamp.Look + " (want Modern for both, battery still its power parent)");
        }

        private static void CanFail(string what, Rule broken, Func<Tally, int> metric, int maps = 400)
        {
            var t = new Tally();
            for (int i = 0; i < maps; i++) Read(Generate(7919 * i + 13), broken, t);
            Console.WriteLine("line restyle: can fail: " + what + ": worst " + metric(t) + " (must be > 0), " + t.Floods + " floods");
            Check(metric(t) > 0, "can fail: " + what + " reads red (worst " + metric(t) + ", limit 0, " + t.Floods + " floods)");
        }

        // ------------------------------------------------------------------ the Verse side calls the shipped rule (source read)
        private static void Wiring()
        {
            string dir = SwitchFlipChecks.AerialSourceDir();
            Check(dir != null, "found Source/Aerial to read the run component");
            if (dir == null) return;
            string runs = File.ReadAllText(Path.Combine(dir, "RM_MapComponent_ConduitRuns.cs"));
            string picker = File.ReadAllText(Path.Combine(dir, "ConduitStylePicker.cs"));
            string Body(string text, string head)
            {
                int i = text.IndexOf(head, StringComparison.Ordinal);
                if (i < 0) return "";
                int b = text.IndexOf('{', i), depth = 0;
                for (int j = b; j < text.Length; j++)
                {
                    if (text[j] == '{') depth++;
                    else if (text[j] == '}' && --depth == 0) return text.Substring(b, j - b + 1);
                }
                return "";
            }
            string nb = Body(runs, "public IEnumerable<Thing> Neighbours(Thing t)");
            Check(nb.Contains("ConduitStyles.RunNeighbours<Thing>(") && Regex.IsMatch(nb, @"ConduitStylePicker\.IsMember\(x\.def\)\s*\|\|\s*IsBridgeConduit\(x\.def\)") &&
                  Regex.IsMatch(nb, @"s\.state == SpanState\.Up && s\.other\?\.parent != null && s\.other\.Spawned"),
                  "Neighbours feeds the map to ConduitStyles.RunNeighbours: joins = member or bridge, spans up and on the map");
            Check(!Regex.IsMatch(nb, @"Flick|PowerOn|TransmitsPower|Faction"), "the neighbour rule reads no power state, switch position or faction");
            Check(Regex.IsMatch(runs, @"IsBridgeConduit\(ThingDef d\) => d != null && ConduitStyles\.IsBridge\(ConduitStylePicker\.IsOurs\(d\), ConduitVisuals\.IsTarget\(d\)\)"),
                  "IsBridgeConduit is ConduitStyles.IsBridge over (ours, drawn as cord)");
            Check(Regex.IsMatch(Body(runs, "public List<Thing> RunOf("), @"ConduitStyles\.RunMembers\(\s*seed, Neighbours,"), "RunOf floods with ConduitStyles.RunMembers over Neighbours");
            string lo = Body(runs, "public List<Thing> LampsOf(");
            string adapter = File.ReadAllText(Path.Combine(dir, "..", "CordWorldAdapter.cs"));
            string hookup = Body(adapter, "internal static Thing DrawnConnection(");
            LampBuiltBeforeCord(lo.Contains("l => CordWorldAdapter.DrawnConnection(l)") &&
                hookup.Contains("HookupPick.PickEnd(footprint, parentCell, cell => ConduitAt(cell) != null,") &&
                hookup.Contains("cell => map.powerNetGrid.TransmittedPowerNetAt(I(cell)) == net") &&
                hookup.Contains("return end.HasValue ? ConduitAt(end.Value) : parent;"));
            Check(lo.Contains("ConduitStyles.LampsHookedTo(") && lo.Contains("x => Neighbours(x).Where(n => IsBridgeConduit(n.def))"),
                  "LampsOf is ConduitStyles.LampsHookedTo over the map's lamps, with the bridges beside each piece");
            string rr = Body(runs, "public int RestyleRun(");
            Check(rr.Contains("List<Thing> run = RunOf(t);") && rr.Contains("LampsOf(run)") && Regex.IsMatch(rr, @"foreach \(Thing m in run\) Paint\(m,") &&
                  rr.Contains("ConduitStyles.LampFollowsRun(") && !rr.Contains("IsMember"),
                  "RestyleRun paints every piece of RunOf(t) and the following lamps of LampsOf(run), as composed here");
            Check(Regex.IsMatch(picker, @"ConduitStyles\.IsRunMemberDef\(dn, byDef\.ContainsKey\(d\)\)\) members\.Add\(d\)"), "the picker's member set is ConduitStyles.IsRunMemberDef");
            Check(Regex.IsMatch(picker, @"reach == ConduitStyles\.Reach\.Connected\) act = lamp \? .*: \(\) => runs\.RestyleRun\(b, k, true\)"),
                  "All connected on a cord, switch, pole or bracket calls RestyleRun on that piece");
        }
    }
}
