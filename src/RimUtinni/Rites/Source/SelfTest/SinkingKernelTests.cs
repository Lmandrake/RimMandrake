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

        private static SinkingOfferingFacts Pitch() { return new SinkingOfferingFacts { nearTar = true, defName = "RM_Bitumen", marketValue = 150f }; }
        private static SinkingOfferingFacts Dig() { return new SinkingOfferingFacts { nearTar = true, defName = "RM_PreservedDrawJoint", inLotteryTable = true, marketValue = 900f }; }
        private static SinkingOfferingFacts Goods() { return new SinkingOfferingFacts { nearTar = true, defName = "Silver", marketValue = 400f }; }

        private static SinkingPlan P(SinkingOfferingFacts f, SinkingConfig c) { return SinkingKernel.Plan(f, c, VS, VL, MS, ML); }

        public static bool Run()
        {
            fails = passes = 0;
            var on = new SinkingConfig();

            // --- classification and refusals ---
            string why;
            Case("pitch_bitumen_is_pitch", SinkingKernel.Classify(Pitch(), on, out why) == SinkingOfferingKind.Pitch);
            Case("pitch_korveth_is_pitch", SinkingKernel.Classify(new SinkingOfferingFacts { nearTar = true, defName = "RM_KorvethPitch", marketValue = 100f }, on, out why) == SinkingOfferingKind.Pitch);
            Case("dig_find_is_dig_find", SinkingKernel.Classify(Dig(), on, out why) == SinkingOfferingKind.DigFind);
            Case("placeholder_chunk_is_other", SinkingKernel.Classify(new SinkingOfferingFacts { nearTar = true, defName = "ChunkSlagSteel", inLotteryTable = true, marketValue = 100f }, on, out why) == SinkingOfferingKind.Other
                 && SinkingKernel.Classify(new SinkingOfferingFacts { nearTar = true, defName = "ShipChunk", inLotteryTable = true, marketValue = 100f }, on, out why) == SinkingOfferingKind.Other);
            Case("goods_is_other", SinkingKernel.Classify(Goods(), on, out why) == SinkingOfferingKind.Other);
            var pawn = P(new SinkingOfferingFacts { nearTar = true, defName = "Human", isPawn = true, marketValue = 2000f }, on);
            Case("refused_pawn_with_reason", pawn.kind == SinkingOfferingKind.RefusedPawn && !pawn.accepted && !string.IsNullOrEmpty(pawn.reason), pawn.Signature());
            var corpse = P(new SinkingOfferingFacts { nearTar = true, defName = "Corpse_Human", isCorpse = true, marketValue = 2000f }, on);
            Case("refused_corpse_with_reason", corpse.kind == SinkingOfferingKind.RefusedCorpse && !corpse.accepted && !string.IsNullOrEmpty(corpse.reason), corpse.Signature());
            var cheap = P(new SinkingOfferingFacts { nearTar = true, defName = "RM_Bitumen", marketValue = 10f }, on);
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

            // ---- the tar's edge (review fix 2)
            var away = Pitch(); away.nearTar = false;
            var awayPlan = P(away, on);
            Case("away_from_tar_refused", awayPlan.kind == SinkingOfferingKind.RefusedAwayFromTar && !awayPlan.accepted
                 && awayPlan.reason != null && awayPlan.reason.Contains("tar's edge") && !awayPlan.holdOff && !awayPlan.raidLull, awayPlan.Signature() + " " + awayPlan.reason);
            var awayDig = Dig(); awayDig.nearTar = false;
            Case("away_from_tar_refused_dig_too", P(awayDig, on).kind == SinkingOfferingKind.RefusedAwayFromTar);
            var awayPawn = new SinkingOfferingFacts { defName = "Human", isPawn = true, marketValue = 2000f };
            Case("away_from_tar_pawn_still_pawn_refusal", P(awayPawn, on).kind == SinkingOfferingKind.RefusedPawn, P(awayPawn, on).kind.ToString());
            Case("away_from_tar_is_refusal", SinkingKernel.IsRefusal(SinkingOfferingKind.RefusedAwayFromTar));
            Case("tar_terrain_defs", SinkingKernel.IsTarTerrain("RM_TarShallow") && SinkingKernel.IsTarTerrain("RM_TarDeep") && SinkingKernel.IsTarTerrain("RM_TarMoat")
                 && SinkingKernel.IsTarTerrain("RM_Fill_Tar_Trace") && SinkingKernel.IsTarTerrain("RM_Fill_Tar_Superdeep"));
            Case("tar_spent_crust_not_tar", !SinkingKernel.IsTarTerrain("RM_TarSpent") && !SinkingKernel.IsTarTerrain("Soil") && !SinkingKernel.IsTarTerrain(null));
            Case("tar_vault_is_tar_building", SinkingKernel.IsTarBuilding("RM_TarVault") && !SinkingKernel.IsTarBuilding("RM_TarShallow") && !SinkingKernel.IsTarBuilding(null));
            Case("tar_radius_default_3", SinkingKernel.TarRadius(new SinkingConfig()) == 3);
            Case("tar_radius_clamped", SinkingKernel.TarRadius(new SinkingConfig { tarRadius = 0 }) == 1 && SinkingKernel.TarRadius(new SinkingConfig { tarRadius = 99 }) == 10);

            // ---- EmpirePursuit timers under the hold-off (review fix 1)
            const int I = 2500;
            Case("roundup", SinkingKernel.RoundUp(2500, I) == 2500 && SinkingKernel.RoundUp(2501, I) == 5000 && SinkingKernel.RoundUp(1, I) == 2500);
            int now0 = 100000, end0 = now0 + 300000;
            int raid = now0 + 60000, warn = now0 + 30000;
            bool sh = SinkingKernel.ShiftPastHoldOff(now0, end0, I, ref raid, ref warn);
            Case("shift_inside_window_moves_past_end", sh && SinkingKernel.RoundUp(warn, I) > end0 && SinkingKernel.RoundUp(raid, I) > end0, raid + "/" + warn);
            Case("shift_keeps_warning_gap", raid - warn == 30000, (raid - warn).ToString());
            Case("shift_never_sooner", raid >= now0 + 60000 && warn >= now0 + 30000);
            int raid2 = raid, warn2 = warn;
            Case("shift_idempotent", !SinkingKernel.ShiftPastHoldOff(now0, end0, I, ref raid2, ref warn2) && raid2 == raid && warn2 == warn);
            int far = end0 + 50000, farW = end0 + 10000;
            Case("shift_beyond_window_untouched", !SinkingKernel.ShiftPastHoldOff(now0, end0, I, ref far, ref farW) && far == end0 + 50000 && farW == end0 + 10000);
            int past = now0 - 10000, pastW = now0 - 20000;
            Case("shift_past_raid_untouched", !SinkingKernel.ShiftPastHoldOff(now0, end0, I, ref past, ref pastW) && past == now0 - 10000);
            int r3 = now0 + 5000, w3 = now0 - 50000; // warning already sent, raid pending inside the window
            Case("shift_raid_only_when_warning_sent", SinkingKernel.ShiftPastHoldOff(now0, end0, I, ref r3, ref w3) && SinkingKernel.RoundUp(r3, I) > end0 && w3 == now0 - 50000, r3 + "/" + w3);
            int r4 = now0 + 5000, w4 = -1;
            Case("shift_no_warning", SinkingKernel.ShiftPastHoldOff(now0, end0, I, ref r4, ref w4) && SinkingKernel.RoundUp(r4, I) > end0 && w4 == -1);
            int r5 = now0 + 5000, w5 = now0 + 1000;
            Case("shift_holdoff_over_untouched", !SinkingKernel.ShiftPastHoldOff(now0, now0 - 1, I, ref r5, ref w5) && r5 == now0 + 5000);

            // ---- the letter's line comes from what was done (review fix 7)
            string none = SinkingKernel.HoldOffLine(false, 0, 0, 0, 600000);
            Case("letter_none_scheduled", none.Contains("No Imperial raid was scheduled") && none.Contains("10 days"), none);
            string moved = SinkingKernel.HoldOffLine(true, 0, 120000, 600000, 600000);
            Case("letter_moved_old_new", moved.Contains("was due in 2 days") && moved.Contains("now comes in 10 days"), moved);
            string same = SinkingKernel.HoldOffLine(true, 0, 900000, 900000, 600000);
            Case("letter_unchanged_says_as_before", same.Contains("as before") && same.Contains("15 days"), same);

            // ---- droids are their own category (review fix 9)
            Case("droid_before_humanlike", SinkingKernel.PawnCategory(true, false, true) == "Droid");
            Case("humanlike_category", SinkingKernel.PawnCategory(true, false, false) == "Humanlike" && SinkingKernel.PawnCategory(false, true, false) == "Mech"
                 && SinkingKernel.PawnCategory(false, false, false) == "Animal");
            var exDefault = SinkingKernel.ParseExclusions(new SinkingConfig().ownershipExclusions);
            Case("default_exclusions_humanlike_only", exDefault.Contains("Humanlike") && !exDefault.Contains("Droid") && exDefault.Count == 1, string.Join(",", exDefault));

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
