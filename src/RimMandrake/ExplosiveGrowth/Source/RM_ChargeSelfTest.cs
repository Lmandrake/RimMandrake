using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    /// <summary>
    /// Runs the pure charge clock (RM_MapComponent_ExplosiveGrowth.StepCharge)
    /// through the three regimes at startup and logs one PASS/FAIL line. No map,
    /// no game state — it catches the class of defect found live 2026-09-26
    /// (a branch that zeroes a fresh charge in the pass that created it) on
    /// every load, before anyone has to spend a live session finding it.
    /// </summary>
    public static class RM_ChargeSelfTest
    {
        public static string Run()
        {
            const int dt = RM_MapComponent_ExplosiveGrowth.PassInterval; // 250
            const float chargeTicks = 6f * 2500f;                          // default 6 h
            string fail = null;

            // 1. Soaked but dormant (the live bug): a fresh charge must survive
            //    48 passes (12,000 ticks) unchanged.
            float c = 0.0001f;
            for (int i = 0; i < 48; i++) c = RM_MapComponent_ExplosiveGrowth.StepCharge(c, true, false, dt, chargeTicks, 1f);
            if (!(c > 0f)) fail = "dormant soaked charge was lost (" + c + ")";

            // 2. Soaked and growing: reaches the top in chargeTicks/dt passes
            //    (60 at the defaults), within the ±10% clock jitter band.
            if (fail == null)
            {
                foreach (float clock in new[] { 0.9f, 1f, 1.1f })
                {
                    c = 0.0001f;
                    int passes = 0;
                    while (c < 1f && passes < 1000) { c = RM_MapComponent_ExplosiveGrowth.StepCharge(c, true, true, dt, chargeTicks, clock); passes++; }
                    int expect = (int)System.Math.Ceiling(chargeTicks * clock / dt);
                    if (System.Math.Abs(passes - expect) > 1) { fail = "growing charge took " + passes + " passes, expected ~" + expect + " (clock " + clock + ")"; break; }
                }
            }

            // 3. Dry: a half charge relaxes to zero within chargeTicks*0.25 (15 passes).
            if (fail == null)
            {
                c = 0.5f;
                int passes = 0;
                while (c > 0f && passes < 1000) { c = RM_MapComponent_ExplosiveGrowth.StepCharge(c, false, true, dt, chargeTicks, 1f); passes++; }
                if (passes > 16) fail = "dry charge took " + passes + " passes to relax";
            }

            return fail == null ? "charge clock self-test PASS (dormant holds, growing tops in ~60 passes, dry relaxes)" : "charge clock self-test FAIL: " + fail;
        }
    }
}
