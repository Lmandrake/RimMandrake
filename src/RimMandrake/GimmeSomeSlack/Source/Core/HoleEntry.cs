// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// The one rule for a cord that enters a hole (owner's walk of 0.2.0, 2026-11-24: "You do not show cables going INTO the hole in the wall to the
// north, just leading up to it"; "rock entry still shows cables leading up to the rock wall but not entering into the darkness of the hole";
// 2026-11-20: "extending the cable art a little longer into the black before it's cut off and disappears in").
// A laid strand ends just under its wall or rock (CordBuilder.PastFaceDepth) and is drawn at conduit height, so the wall and the plate or hole decal
// cover its end. Wherever a piece draws a StubWall / StubRock decal, each strand ending there gets a short lead drawn OVER the decal, the
// strand's own line run on into the black. Derived from the finished piece: no lay, no audit and no cache key changes.
using System;
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    internal static class HoleEntry
    {
        /// <summary>The black of the hole along the art's X (u), the part that is black in EVERY look's picture (measured over all 16 Stub PNGs,
        /// luminance under 26 around the hole's middle; HoleEntryChecks.Pictures reads the PNGs against these).</summary>
        public const double WallDark0 = 0.469, WallDark1 = 0.562, RockDark0 = 0.453, RockDark1 = 0.656;
        /// <summary>How far through the black that is drawn the cord is cut off.</summary>
        public const double InFrac = 0.75;
        /// <summary>The lead starts this far out on the floor, on the strand, so nothing of the wall's dark outline shows between them.</summary>
        public const double Back = 0.04;
        /// <summary>A strand end this near a plate's face line (along, across) is that plate's cord.</summary>
        private const double EndAlong = 0.12, EndAcross = 0.2;

        /// <summary>A drawn hole: its face point, the way in, and where its drawn black begins and ends (cells past the face line).</summary>
        internal struct Hole { public V2 Face, Into; public double Near, Far; public double Target => Near + (Far - Near) * InFrac; }

        internal struct Lead { public List<V2> Pts; public double S0, Shift; public int Strand; public bool AtStart; public int Decal; }

        internal static bool Is(CordDecal d) => (d.Kind == DecalKind.StubWall || d.Kind == DecalKind.StubRock) && d.Cropped;

        internal static Hole Of(CordDecal d)
        {
            bool rock = d.Kind == DecalKind.StubRock;
            double d0 = rock ? RockDark0 : WallDark0, d1 = rock ? RockDark1 : WallDark1;
            V2 into = new V2(Math.Cos(d.Angle), Math.Sin(d.Angle));
            double near = WallMount.FaceMargin, k = d.ScaleX / (d.U1 - d.U0);
            double At(double u) => near + (Math.Min(Math.Max(u, d.U0), d.U1) - d.U0) * k;
            return new Hole { Into = into, Face = d.Pos - into * (near + d.ScaleX / 2), Near = At(d0), Far = At(d1) };
        }

        internal static double Along(Hole h, V2 q) => (q.X - h.Face.X) * h.Into.X + (q.Z - h.Face.Z) * h.Into.Z;
        internal static double Across(Hole h, V2 q) => (q.Z - h.Face.Z) * h.Into.X - (q.X - h.Face.X) * h.Into.Z;

        /// <summary>Does this strand's end go into this hole (the end at its start or its last point)?</summary>
        internal static bool EndsAt(Hole h, CordStrand s, bool atStart)
        {
            if (s.OverFace || s.Lifted || s.Pts == null || s.Pts.Count < 2) return false;
            V2 t = atStart ? s.Pts[0] : s.Pts[s.Pts.Count - 1];
            return Math.Abs(Along(h, t)) <= EndAlong && Math.Abs(Across(h, t)) <= EndAcross;
        }

        /// <summary>The leads of a finished piece: per drawn hole, per strand that ends at it, the strand's last <see cref="Back"/> before the face and its line run on
        /// to the hole's target, in the strand's own direction, its texture running on from the strand's.</summary>
        internal static List<Lead> Leads(LaidPiece p)
        {
            var res = new List<Lead>();
            for (int i = 0; i < p.Decals.Count; i++)
            {
                if (!Is(p.Decals[i])) continue;
                Hole h = Of(p.Decals[i]);
                for (int si = 0; si < p.Strands.Count; si++)
                    foreach (bool at in new[] { true, false })
                    {
                        CordStrand s = p.Strands[si];
                        if (!EndsAt(h, s, at)) continue;
                        // out of the hole, along the strand: the target, the tip, and the strand's points as far as Back outside the face
                        int n = s.Pts.Count;
                        V2 P(int k) => at ? s.Pts[k] : s.Pts[n - 1 - k];
                        V2 tip = P(0);
                        double a = Along(h, tip), off = Across(h, tip), add = h.Target - a;
                        var o = new List<V2>();
                        double ext = 0;
                        if (add > 1e-4)
                        {
                            int steps = Math.Max(1, (int)Math.Ceiling(add / 0.03));
                            V2 side = new V2(-h.Into.Z, h.Into.X);
                            for (int k = 0; k < steps; k++)
                            {
                                double f = 1 - (double)k / steps;           // 1 at the target, 0 at the tip: a cord off the middle comes in to it
                                o.Add(tip + h.Into * (add * f) - side * (off * f));
                            }
                        }
                        double cut = 0;                                     // a strand laid on past the target (a thin edge-on hole) is cut back to it
                        if (add >= -1e-4) o.Add(tip);
                        ext = Geo.Length(o);
                        for (int k = 1; k < n; k++)
                        {
                            V2 q = P(k), b = P(k - 1);
                            double al = Along(h, q), bl = Along(h, b);
                            if (o.Count == 0)
                            {
                                if (al > h.Target) { cut += V2.Dist(b, q); continue; }
                                double t0 = (bl - h.Target) / Math.Max(1e-9, bl - al);
                                V2 c = b + (q - b) * Math.Max(0, Math.Min(1, t0));
                                cut += V2.Dist(b, c);
                                o.Add(c);
                            }
                            if (al > -Back) { o.Add(q); continue; }
                            double t = (bl + Back) / Math.Max(1e-9, bl - al);
                            o.Add(b + (q - b) * Math.Max(0, Math.Min(1, t)));
                            break;
                        }
                        if (o.Count < 2) continue;
                        double total = Geo.Length(o), strand = Geo.Length(s.Pts);
                        if (!at) o.Reverse();
                        // S0 is in quarter repeats of the texture (RibbonInto: u = S0 * 4 + length / (width * aspect)); held here as a length, turned into S0 where it is printed
                        res.Add(new Lead { Pts = o, S0 = s.S0, Shift = at ? cut - ext : strand - cut - (total - ext), Strand = si, AtStart = at, Decal = i });
                    }
            }
            return res;
        }

        internal sealed class Read
        {
            public int Holes, Ends, NotIn, NoBlack, Bare;
            public double WorstShort;
            /// <summary>Per kind and face: how deep past the face the cord is drawn, and the black's span.</summary>
            public readonly SortedDictionary<string, List<(double End, double Near, double Far)>> By = new SortedDictionary<string, List<(double, double, double)>>(StringComparer.Ordinal);
            public readonly List<string> Bad = new List<string>();
        }

        /// <summary>The least black a hole may show, and how far off its middle line a cord may end, cells.</summary>
        public const double BlackMin = 0.02, OffMax = 0.03;

        /// <summary>Reads where each cord at a plate or hole is DRAWN to end: the deepest point of what is drawn over the decal; with nothing over it, the face
        /// line (the wall and the decal cover the strand from there).</summary>
        internal static void Audit(Read r, LaidPiece p, List<Lead> leads, Func<CordDecal, bool> keep = null)
        {
            for (int i = 0; i < p.Decals.Count; i++)
            {
                if (!Is(p.Decals[i]) || keep != null && !keep(p.Decals[i])) continue;
                Hole h = Of(p.Decals[i]);
                r.Holes++;
                string kind = p.Decals[i].Kind + " " + WallMount.FaceOf(h.Into);
                if (h.Far - h.Near < BlackMin) { r.NoBlack++; r.Bad.Add($"{p.EndA}|{p.EndB} {kind}: the hole shows {h.Far - h.Near:0.000} cell of black (least {BlackMin})"); }
                int here = 0;
                for (int si = 0; si < p.Strands.Count; si++)
                    foreach (bool at in new[] { true, false })
                    {
                        if (!EndsAt(h, p.Strands[si], at)) continue;
                        here++; r.Ends++;
                        double end = 0, off = 0;
                        foreach (Lead l in leads)
                        {
                            if (l.Strand != si || l.AtStart != at || l.Decal != i) continue;
                            V2 e = at ? l.Pts[0] : l.Pts[l.Pts.Count - 1];
                            end = Along(h, e); off = Math.Abs(Across(h, e));
                        }
                        if (!r.By.TryGetValue(kind, out var list)) r.By[kind] = list = new List<(double, double, double)>();
                        list.Add((end, h.Near, h.Far));
                        if (end > h.Near + 0.005 && end <= h.Far && off <= OffMax) continue;
                        r.NotIn++;
                        r.WorstShort = Math.Max(r.WorstShort, h.Near - end);
                        r.Bad.Add($"{p.EndA}|{p.EndB} {kind}: the cord is drawn to {end:0.000} past the face, {off:0.000} off the middle; the black is {h.Near:0.000}..{h.Far:0.000}");
                    }
                if (here == 0) { r.Bare++; r.Bad.Add($"{p.EndA}|{p.EndB} {kind}: no cord ends at the hole"); }
            }
        }
    }
}
