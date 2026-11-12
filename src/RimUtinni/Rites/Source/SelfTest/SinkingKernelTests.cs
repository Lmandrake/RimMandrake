// SUMP_SINKING_RITE_BUILD_1: offline cases for Kernel/SinkingKernel.cs (the production file, compiled in directly).
// One named case per acceptance criterion the kernel decides, and one per Mod Settings toggle: with toggle X off,
// effect X is absent and every other effect is identical to the all-on run. Run: SelfTest.dll --sinking
using System;
using System.Collections.Generic;

namespace RimMandrake.Utinni.Rites.SelfTest
{
    public static class SinkingKernelTests
    {
        private static int fails, passes;

        private static void Case(string name, bool ok, string detail = "")
        {
            if (ok) passes++; else fails++;
            Console.WriteLine((ok ? "PASS  " : "FAIL  ") + "sinking/" + name + (ok ? "" : "  " + detail));
        }

        // the production constants of OfferingUtility / EventMagnitude (Offerings.cs, EventMagnitude.cs)
        private const float VS = 200f, VL = 3000f, MS = 3f, ML = 15f;

        private static SinkingOfferingFacts Pitch() { return new SinkingOfferingFacts { defName = "RM_Bitumen", marketValue = 150f }; }
        private static SinkingOfferingFacts Dig() { return new SinkingOfferingFacts { defName = "RM_PreservedDrawJoint", inLotteryTable = true, marketValue = 900f }; }
        private static SinkingOfferingFacts Goods() { return new SinkingOfferingFacts { defName = "Silver", marketValue = 400f }; }

        private static SinkingPlan P(SinkingOfferingFacts f, SinkingConfig c) { return SinkingKernel.Plan(f, c, VS, VL, MS, ML); }

        public static bool Run()
        {
            fails = passes = 0;
            var on = new SinkingConfig();

            // --- classification and refusals ---
            string why;
            Case("pitch_bitumen_is_pitch", SinkingKernel.Classify(Pitch(), on, out why) == SinkingOfferingKind.Pitch);
            Case("pitch_korveth_is_pitch", SinkingKernel.Classify(new SinkingOfferingFacts { defName = "RM_KorvethPitch", marketValue = 100f }, on, out why) == SinkingOfferingKind.Pitch);
            Case("dig_find_is_dig_find", SinkingKernel.Classify(Dig(), on, out why) == SinkingOfferingKind.DigFind);
            Case("placeholder_chunk_is_other", SinkingKernel.Classify(new SinkingOfferingFacts { defName = "ChunkSlagSteel", inLotteryTable = true, marketValue = 100f }, on, out why) == SinkingOfferingKind.Other
                 && SinkingKernel.Classify(new SinkingOfferingFacts { defName = "ShipChunk", inLotteryTable = true, marketValue = 100f }, on, out why) == SinkingOfferingKind.Other);
            Case("goods_is_other", SinkingKernel.Classify(Goods(), on, out why) == SinkingOfferingKind.Other);
            var pawn = P(new SinkingOfferingFacts { defName = "Human", isPawn = true, marketValue = 2000f }, on);
            Case("refused_pawn_with_reason", pawn.kind == SinkingOfferingKind.RefusedPawn && !pawn.accepted && !string.IsNullOrEmpty(pawn.reason), pawn.Signature());
            var corpse = P(new SinkingOfferingFacts { defName = "Corpse_Human", isCorpse = true, marketValue = 2000f }, on);
            Case("refused_corpse_with_reason", corpse.kind == SinkingOfferingKind.RefusedCorpse && !corpse.accepted && !string.IsNullOrEmpty(corpse.reason), corpse.Signature());
            var cheap = P(new SinkingOfferingFacts { defName = "RM_Bitumen", marketValue = 10f }, on);
            Case("refused_below_floor_with_reason", cheap.kind == SinkingOfferingKind.RefusedBelowFloor && cheap.reason.Contains("50"), cheap.reason);
            Case("refusal_applies_no_effect", !pawn.holdOff && !pawn.raidLull && !pawn.ownershipErase && pawn.rider == SinkingRider.None && pawn.ishkoDelta == 0f, pawn.Signature());

            // --- pitch rider: the beast lull ---
            var pp = P(Pitch(), on);
            Case("pitch_rider_beast_lull_15_days", pp.rider == SinkingRider.BeastLull && pp.beastLullTicks == 15 * 60000, pp.Signature());
            Case("beast_lull_refuses_construction", !SinkingKernel.WakeAllowed(SinkingWakeCause.Construction, true, true));
            Case("beast_lull_refuses_dig", !SinkingKernel.WakeAllowed(SinkingWakeCause.Dig, true, true));
            Case("beast_lull_refuses_pump", !SinkingKernel.WakeAllowed(SinkingWakeCause.Pump, true, true));
            Case("beast_lull_explosion_wakes", SinkingKernel.WakeAllowed(SinkingWakeCause.Explosion, true, true)
                 && SinkingKernel.WakeAllowed(SinkingWakeCause.Damage, true, true));
            Case("no_lull_every_cause_wakes", SinkingKernel.WakeAllowed(SinkingWakeCause.Construction, false, true)
                 && SinkingKernel.WakeAllowed(SinkingWakeCause.Pump, false, true));

            // --- dig-find rider: the trap fizzle counter ---
            var dp = P(Dig(), on);
            Case("dig_find_trap_counter_reads_3", dp.rider == SinkingRider.TrapFizzle && dp.trapCount == 3, dp.Signature());
            int counter = dp.trapCount;
            bool a = SinkingKernel.FizzleTrap(ref counter, true), b = SinkingKernel.FizzleTrap(ref counter, true), c = SinkingKernel.FizzleTrap(ref counter, true);
            Case("three_trap_rolls_fizzle_counter_0", a && b && c && counter == 0, "counter=" + counter);
            Case("fourth_trap_roll_arms_normally", !SinkingKernel.FizzleTrap(ref counter, true) && counter == 0, "counter=" + counter);
            Case("trap_count_setting_honoured", SinkingKernel.TrapCounterStart(new SinkingConfig { trapCount = 5 }) == 5);
            Case("pitch_does_not_set_trap_counter", pp.trapCount == 0 && dp.beastLullTicks == 0);

            // --- any Sinking: the Empire hold-off ---
            Case("hold_off_is_5x_the_normal_interval", pp.holdOff && pp.holdOffTicks == 5 * 60000 && dp.holdOffTicks == 5 * 60000, pp.Signature());
            Case("hold_off_follows_the_interval_setting", SinkingKernel.HoldOffTicks(new SinkingConfig { normalHoldOffDays = 2f }) == 10 * 60000);
            Case("hold_off_follows_the_multiplier_setting", SinkingKernel.HoldOffTicks(new SinkingConfig { holdOffMultiplier = 3f }) == 3 * 60000);
            Case("next_imperial_incident_moved_out_5x", SinkingKernel.MoveOut(1000, 61000, 5f) == 1000 + 5 * 60000, SinkingKernel.MoveOut(1000, 61000, 5f).ToString());
            Case("past_incident_tick_left_alone", SinkingKernel.MoveOut(1000, 900, 5f) == 900);
            Case("warning_never_after_its_raid", SinkingKernel.MoveOutWarning(0, 50000, 40000, 5f) == 40000);
            Case("move_out_saturates_not_overflows", SinkingKernel.MoveOut(0, int.MaxValue / 2, 5f) == int.MaxValue);

            // --- any Sinking: the non-Empire raid lull ---
            Case("raid_lull_days_and_chance", pp.raidLull && pp.raidLullTicks == 10 * 60000 && Math.Abs(pp.raidChanceMultiplier - 0.5f) < 1e-6, pp.Signature());
            Case("seeded_raid_roll_reads_lowered_chance", !SinkingKernel.RaidRollFires(0.6f, 0.5f) && SinkingKernel.RaidRollFires(0.4f, 0.5f)
                 && SinkingKernel.RaidRollFires(0.99f, SinkingKernel.RaidChanceMultiplier(on, false)));
            Case("raid_lull_strength_setting_honoured", Math.Abs(SinkingKernel.RaidChanceMultiplier(new SinkingConfig { raidLullStrength = 0.8f }, true) - 0.2f) < 1e-6);

            // --- any Sinking: Ishko ---
            Case("ishko_delta_small_at_floor_value", Math.Abs(SinkingKernel.IshkoDelta(100f, VS, VL, MS, ML) - 3f) < 1e-5);
            Case("ishko_delta_large_at_3000", Math.Abs(SinkingKernel.IshkoDelta(5000f, VS, VL, MS, ML) - 15f) < 1e-5);
            Case("ishko_delta_lerps_between", Math.Abs(SinkingKernel.IshkoDelta(1600f, VS, VL, MS, ML) - 9f) < 1e-4);
            Case("ishko_delta_is_positive_on_every_offering", pp.ishkoDelta > 0f && dp.ishkoDelta > 0f && P(Goods(), on).ishkoDelta > 0f);
            Case("ishko_tag_is_the_sinking", SinkingKernel.DeltaTag == "The Sinking");

            // --- any Sinking: ownership erase ---
            var ex = SinkingKernel.ParseExclusions(on.ownershipExclusions);
            Case("ownership_item_is_erased", SinkingKernel.EraseCandidate("Item", true, true, ex));
            Case("ownership_colonist_untouched_by_default", !SinkingKernel.EraseCandidate("Humanlike", true, true, ex));
            Case("ownership_foreign_owned_or_other_map_untouched", !SinkingKernel.EraseCandidate("Item", false, true, ex) && !SinkingKernel.EraseCandidate("Item", true, false, ex));
            Case("ownership_exclusion_list_parsed", SinkingKernel.ParseExclusions("Humanlike, animal;Mech").Contains("Animal")
                 && SinkingKernel.ParseExclusions("").Count == 0);
            Case("ownership_erase_on_every_offering", pp.ownershipErase && dp.ownershipErase);

            // --- toggles: X off removes exactly X ---
            ToggleCase("toggle_holdOffEnabled", c2 => c2.holdOffEnabled = false, Pitch(), e => { e.holdOff = false; e.holdOffTicks = 0; e.holdOffMultiplier = 0f; });
            ToggleCase("toggle_raidLullEnabled", c2 => c2.raidLullEnabled = false, Pitch(), e => { e.raidLull = false; e.raidLullTicks = 0; e.raidChanceMultiplier = 1f; });
            ToggleCase("toggle_ownershipEraseEnabled", c2 => c2.ownershipEraseEnabled = false, Dig(), e => { e.ownershipErase = false; });
            ToggleCase("toggle_beastLullEnabled", c2 => c2.beastLullEnabled = false, Pitch(), e => { e.rider = SinkingRider.None; e.beastLullTicks = 0; });
            ToggleCase("toggle_trapFizzleEnabled", c2 => c2.trapFizzleEnabled = false, Dig(), e => { e.rider = SinkingRider.None; e.trapCount = 0; });
            var offCfg = new SinkingConfig { riteEnabled = false };
            var offPlan = P(Pitch(), offCfg);
            Case("toggle_riteEnabled", offPlan.kind == SinkingOfferingKind.RefusedDisabled && !offPlan.accepted && !offPlan.holdOff && !offPlan.raidLull
                 && !offPlan.ownershipErase && offPlan.rider == SinkingRider.None && offPlan.ishkoDelta == 0f && !string.IsNullOrEmpty(offPlan.reason), offPlan.Signature());
            int disabledCounter = 3;
            Case("toggle_trapFizzleEnabled_off_mid_count_arms", !SinkingKernel.FizzleTrap(ref disabledCounter, false) && disabledCounter == 3);
            Case("toggle_beastLullEnabled_off_mid_lull_wakes", SinkingKernel.WakeAllowed(SinkingWakeCause.Construction, true, false));
            Case("toggle_raidLullEnabled_off_mid_lull_full_chance", SinkingKernel.RaidChanceMultiplier(new SinkingConfig { raidLullEnabled = false }, true) == 1f);

            Console.WriteLine(string.Format("sinking kernel: {0} passed, {1} failed", passes, fails));
            return fails == 0;
        }

        private static void ToggleCase(string name, Action<SinkingConfig> off, SinkingOfferingFacts f, Action<SinkingPlan> strip)
        {
            var allOn = P(f, new SinkingConfig());
            var cfg = new SinkingConfig();
            off(cfg);
            var got = P(f, cfg);
            var expected = P(f, new SinkingConfig());
            strip(expected);
            bool changed = allOn.Signature() != got.Signature();
            Case(name, changed && got.Signature() == expected.Signature(), "got " + got.Signature() + " | want " + expected.Signature());
        }
    }
}
