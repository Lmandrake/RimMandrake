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
                if (passes > 16 || float.IsNaN(c)) fail = "dry charge took " + passes + " passes to relax";
            }

            string head = fail == null ? "charge clock self-test PASS (dormant holds, growing tops in ~60 passes, dry relaxes)" : "charge clock self-test FAIL: " + fail;

            // 4. The ruled rate table at the ruled defaults (spec §2.5): one factor, replacing, never stacking.
            string rf = null;
            RM_RateSettings s = RM_RateSettings.Ruled;
            void Want(string what, float got, float want) { if (rf == null && !(System.Math.Abs(got - want) <= 1e-5f)) rf = what + " " + got + " != " + want; }
            Want("dry wet", RM_ExplosiveGrowthKernel.MoistureFactor(RM_Archetype.DryNative, true, false, false, true, false, false, false, s), 10f);
            Want("dry dry", RM_ExplosiveGrowthKernel.MoistureFactor(RM_Archetype.DryNative, true, false, false, false, false, false, false, s), 0.1f);
            Want("dry tree wet", RM_ExplosiveGrowthKernel.MoistureFactor(RM_Archetype.DryNative, true, false, false, true, false, true, false, s), 6.25f);
            Want("wet native", RM_ExplosiveGrowthKernel.MoistureFactor(RM_Archetype.WetNative, true, false, false, false, false, false, false, s), 4f);
            Want("vanilla dry", RM_ExplosiveGrowthKernel.MoistureFactor(RM_Archetype.Vanilla, true, false, false, false, false, false, false, s), 0.1f);
            Want("vanilla near", RM_ExplosiveGrowthKernel.MoistureFactor(RM_Archetype.Vanilla, true, false, false, false, false, false, true, s), 1f);
            Want("sealed", RM_ExplosiveGrowthKernel.MoistureFactor(RM_Archetype.DryNative, true, false, true, true, false, false, false, s), 1f);
            Want("out of scope", RM_ExplosiveGrowthKernel.MoistureFactor(RM_Archetype.DryNative, false, false, false, true, false, false, false, s), 1f);
            Want("age step at x0.1", 2000 - RM_ExplosiveGrowthKernel.AgeRemoval(0.1f, 0.5f), 200f);
            return head + (rf == null ? " | ruled rates PASS (x10 wet, x0.1 dry, x4 jungle, x6.25 tree, vanilla x0.1/x1, sealed x1, age x0.1)"
                                      : " | ruled rates FAIL: " + rf);
        }
    }
}
