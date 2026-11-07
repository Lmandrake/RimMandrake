// cords_never_repeat (GSS_SHAPE_PROBE_MEASURE_NO_TWO_ALIKE): eight parallel runs of one length, no two the same drawn curve; a planted
// copy of one cord on another's ends reads as identical, so the instrument can fail.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class CordShapeChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "cord-shape: " + msg);

        /// <summary>Eight separate straight runs of one length, three cells apart, in open floor.</summary>
        private static CordWorld Room()
        {
            var w = new CordWorld(40, 44);
            for (int k = 0; k < 8; k++)
                for (int x = 6; x <= 30; x++) w.SetConduit(new Cell(x, 6 + 4 * k));
            return w;
        }

        public static void Run()
        {
            int alike = 0, cords = 0;
            double worst = double.MaxValue;
            foreach (ulong seed in new ulong[] { 1, 2, 3, 7, 19 })
            {
                List<LaidPiece> ps = new CordBuilder().Build(Room(), new BuildOptions { Seed = seed }, c => true);
                List<ShapeClass> t = CordShape.Table(ps);
                alike += t.Sum(c => c.TooAlike);
                cords += t.Sum(c => c.Cords);
                worst = Math.Min(worst, t.Where(c => c.Pairs > 0).Select(c => c.MinDistance).DefaultIfEmpty(double.MaxValue).Min());
            }
            Check(cords >= 40, $"the room lays {cords} cords over 5 seeds");
            Check(alike == 0, $"{alike} pairs of one length class under {CordShape.TooAlikeBelow} cells apart; closest pair {worst:0.00}");
            Console.WriteLine($"  cord shape: {cords} cords over 5 seeds, closest pair {worst:0.00} cells apart, {alike} too alike");

            // planted: the same drawn vertices on two distinct edges, one laid again turned, moved and running the other way
            {
                List<LaidPiece> ps = new CordBuilder().Build(Room(), new BuildOptions(), c => true);
                LaidPiece a = ps.First(p => p.EndA != null && p.Owner.Z == 6);
                var moved = new List<V2>();
                foreach (V2 q in Enumerable.Reverse(a.Strands[0].Pts)) moved.Add(CordAudit.Rot(q, 1.1) + new V2(3, 40));
                var twin = new LaidPiece { Key = "twin", EndA = "planted:0,0", EndB = "planted:1,1", PathLen = a.PathLen };
                twin.Strands.Add(new CordStrand { Pts = moved });
                List<ShapeClass> t = CordShape.Table(new[] { a, twin });
                Check(t.Count == 1 && t[0].TooAlike == 1 && t[0].MinDistance < 0.05, $"planted: a cord and its moved, turned, reversed copy read {(t.Count > 0 ? t[0].MinDistance : -1):0.000} apart");
            }
        }
    }
}
