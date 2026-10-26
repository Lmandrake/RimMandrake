using System;

namespace RimMandrake.LeaningScrub.SelfTest
{
    // SHIRREL_DECIDE_GALE_GLIDE: table checks of the shirrel's Gale-glide kernel (RM_GlideKernel). Offline and deterministic:
    // the glide is never flown here (owner: no live flight test without him present).
    internal static class LeaningScrubGlideCheck
    {
        public static bool Run()
        {
            int bad = 0;
            void Eq(string n, object got, object want) { if (!Equals(got, want)) { bad++; Console.Error.WriteLine("FAIL glide " + n + " " + got + " != " + want); } }
            void Near(string n, float got, float want) { if (Math.Abs(got - want) > 1e-4f) { bad++; Console.Error.WriteLine("FAIL glide " + n + " " + got + " != " + want); } }

            // the CanFlyNow gate: a glider flies only inside its own launch; everyone else keeps vanilla's answer
            Eq("glider grounded outside launch", RM_GlideKernel.CanFlyNow(true, true, false), false);
            Eq("glider flies in launch", RM_GlideKernel.CanFlyNow(true, true, true), true);
            Eq("launch cannot beat cooldown", RM_GlideKernel.CanFlyNow(false, true, true), false);
            Eq("other flyer untouched", RM_GlideKernel.CanFlyNow(true, false, false), true);
            Eq("other grounded untouched", RM_GlideKernel.CanFlyNow(false, false, true), false);

            // ShouldGlide: all gates true + roll under chance -> glide; each single gate flipped -> no glide
            bool[] ok = { true, true, true, true, true, true, false, false, true, true };
            Eq("all gates glide", G(ok, 0.1f, 0.5f), true);
            Eq("roll at chance no glide", G(ok, 0.5f, 0.5f), false);
            string[] names = { "feature off", "no gale", "no wind", "tame", "busy", "asleep", "downed", "mental", "no tree", "cooldown" };
            for (int k = 0; k < ok.Length; k++)
            {
                bool[] b = (bool[])ok.Clone();
                b[k] = !b[k];
                Eq(names[k] + " no glide", G(b, 0.1f, 0.5f), false);
            }

            // per-check chance: 1 - exp(-interval / (mtb * 2500))
            Near("chance 1.5h/250", RM_GlideKernel.ChancePerCheck(1.5f, 250), (float)(1 - Math.Exp(-250.0 / 3750.0)));
            Eq("chance zero mtb", RM_GlideKernel.ChancePerCheck(0f, 250), 0f);
            Eq("chance zero interval", RM_GlideKernel.ChancePerCheck(1.5f, 0), 0f);

            // hop length
            Near("hop min", RM_GlideKernel.HopDistance(10f, 16f, 0f), 10f);
            Near("hop max", RM_GlideKernel.HopDistance(10f, 16f, 1f), 16f);
            Near("hop clamped roll", RM_GlideKernel.HopDistance(10f, 16f, 7f), 16f);
            Near("hop swapped", RM_GlideKernel.HopDistance(16f, 10f, 0.5f), 10f);
            Near("hop floor 1", RM_GlideKernel.HopDistance(-5f, 0f, 0.5f), 1f);

            // landing aim: downwind, rounded, inside the margin
            RM_GlideKernel.HopTarget(50, 50, 1f, 0f, 12f, 250, 250, 3, out int tx, out int tz);
            Eq("east hop x", tx, 62); Eq("east hop z", tz, 50);
            RM_GlideKernel.HopTarget(50, 50, 0f, -2f, 12f, 250, 250, 3, out tx, out tz);
            Eq("south hop unnormalised dir", tz, 38); Eq("south hop x", tx, 50);
            RM_GlideKernel.HopTarget(245, 5, 1f, -1f, 16f, 250, 250, 3, out tx, out tz);
            Eq("edge clamp x", tx, 246); Eq("edge clamp z", tz, 3);
            RM_GlideKernel.HopTarget(50, 50, 0f, 0f, 12f, 250, 250, 3, out tx, out tz);
            Eq("no wind stays", tx * 1000 + tz, 50050);

            // inspect line
            Eq("describe off", RM_GlideKernel.Describe(false, true, "sweetline tree", true), null);
            Eq("describe bound", RM_GlideKernel.Describe(true, true, "Sweetline tree", false), "Home: Sweetline tree.");
            Eq("describe unbound gliding", RM_GlideKernel.Describe(true, false, null, true), "No sweetline tree on this map. Gliding on the Gale.");

            if (bad == 0) Console.WriteLine("LeaningScrubGlideCheck PASS");
            return bad == 0;
        }

        private static bool G(bool[] g, float roll, float chance)
        {
            return RM_GlideKernel.ShouldGlide(g[0], g[1], g[2], g[3], g[4], g[5], g[6], g[7], g[8], g[9], roll, chance);
        }
    }
}
