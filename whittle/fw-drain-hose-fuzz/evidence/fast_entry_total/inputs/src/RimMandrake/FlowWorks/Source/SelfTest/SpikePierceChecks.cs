// SPIKES_PIERCE_TUNE_LIKE_VANILLA_TRAP (owner card 2026-10-25: spikes pierce like vanilla). Vanilla 1.6
// Building_TrapDamager.SpringSub (decompiled 2026-10-25): armorPenetration = damage x 0.015 per stab. Offline checks on the
// production rule and the production call site. NOT proven here: a stab landing through armour in game. Live row owed:
// spikes_pierce_armoured_raider (an armoured pawn dropped onto spikes: the DamageInfo carries AP = damage x 0.015).
using System;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class SpikePierceChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("SpikePierce_vanilla_trap_rule_damage_x_0015", () =>
            {
                Assert(RM_PitTrapMath.SpikeArmorPenetrationPerDamage == 0.015f, "vanilla's factor (Building_TrapDamager: num * 0.015f)");
                float human = RM_PitTrapMath.SpikeDamagePerHit(1f, 1f);
                float ap = RM_PitTrapMath.SpikeArmorPenetration(human);
                Assert(Math.Abs(ap - 0.2f) < 1e-4f, "a human's 13.33 stab pierces 0.20 (20%), got " + ap);
                Assert(ap > 0f, "can-fail: the spikes no longer stab at AP 0 (the old default)");
                float thrumbo = RM_PitTrapMath.SpikeArmorPenetration(RM_PitTrapMath.SpikeDamagePerHit(4f, 1f));
                Assert(Math.Abs(thrumbo - 0.8f) < 1e-4f, "scales with the hit like vanilla: a thrumbo-sized hit (53.3) pierces 0.80");
                Assert(RM_PitTrapMath.SpikeArmorPenetration(-5f) == 0f, "can-fail: never negative");
            });

            Case("SpikePierce_descent_passes_the_penetration", () =>
            {
                string src = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Superdeep", "RM_Spikes.cs"));
                Assert(src.Contains("float pierce = RM_PitTrapMath.SpikeArmorPenetration(perHit);"), "the hit's AP comes from the rule");
                Assert(src.Contains("new DamageInfo(DamageDefOf.Stab, perHit, pierce)") && !src.Contains("new DamageInfo(DamageDefOf.Stab, perHit))"),
                    "can-fail: every spike stab carries the penetration");
            });
        }
    }
}
