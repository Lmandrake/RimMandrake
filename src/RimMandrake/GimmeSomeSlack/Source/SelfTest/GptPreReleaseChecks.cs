// GSS pre-release GPT consult 2026-10-15 (Transient/release_push_2026-10-15/gpt_GSS/TRIAGE.md): one offline row per fixed
// finding whose logic is Verse-free. Each row carries a can-fail: the old rule beside the new one gives the wrong answer.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class GptPreReleaseChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "gpt-prerelease: " + msg);

        public static void Run()
        {
            FallenShock();
        }

        // ------------------------------------------------------------------ GSS_FALLEN_LINE_FIX_SHOCKS_THIN_AIR (C3, C6)
        private static void FallenShock()
        {
            Func<int, int, bool> open = (x, z) => true;
            var basePt = new P2(10.5, 10.5);
            var top = new P2(10.5 + 0.087, 10.5 + 3.22);                  // insulator 3.22 cells up: screen z fakes height
            var brk = new P2(16.5, 10.5);                                  // the break lies due east
            FallenLay f = AerialMath.LayFallen(top, basePt, brk, 6.3, 42, open);
            List<P2> ground = AerialMath.GroundPts(f).ToList();
            // C3: every contact point lies on the ground path (base -> break, bow <= 0.22), never north of the mast
            Check(f.TipGrounded && ground.Count > 0 && ground.All(p => Math.Abs(p.Z - 10.5) <= 0.25) && P2.Dist(ground[ground.Count - 1], f.Tip) < 1e-12,
                  "C3 contact points are the grounded part only (" + ground.Count + " of " + f.Pts.Count + ")");
            Check(f.Pts.Any(p => Math.Floor(p.Z) >= 12), "C3 can-fail: the old rule (every Pts point) reaches cells 1-3 north of the mast");
            // a cable stopped at once by a wall still hangs: it touches nothing
            FallenLay hung = AerialMath.LayFallen(top, basePt, basePt, 6.3, 42, open);   // a coil at the anchor: nothing laid
            Check(!hung.TipGrounded && !AerialMath.GroundPts(hung).Any(), "C3 a cable with no ground run (coiled at the anchor) has no contact cells and no live tip");

            // C6: mid-strand on an east-west wire (contacts on dz == 0) the pawn is thrown off the wire, not along it
            Func<int, int, bool> offWire = (dx, dz) => dz != 0;
            var d = AerialMath.KnockbackDir(5, 0, 0, offWire);
            Check(d != null && d.Value.dz != 0, "C6 mid-strand knockback leaves the wire (" + d + ")");
            Check(!offWire(Math.Sign(5), 0), "C6 can-fail: the old rule (straight away from the tip) steps onto the next contact cell");
            Check(AerialMath.KnockbackDir(5, 0, 0, (dx, dz) => true) == (1, 0), "C6 a clear 'away from the tip' is still preferred");
            Check(AerialMath.KnockbackDir(0, 0, 3, (dx, dz) => true) == AerialMath.Ring8[3], "C6 on the tip: the fallback direction");
            Check(AerialMath.KnockbackDir(1, 0, 0, (dx, dz) => false) == null, "C6 boxed in: no knockback");
            // the turn order never repeats a direction and reaches all eight
            var seen = new HashSet<(int, int)>();
            AerialMath.KnockbackDir(1, 0, 0, (dx, dz) => { seen.Add((dx, dz)); return false; });
            Check(seen.Count == 8, "C6 all eight neighbours are tried (" + seen.Count + ")");
        }
    }
}
