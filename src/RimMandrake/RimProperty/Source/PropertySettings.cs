using UnityEngine;
using Verse;

namespace RimMandrake.Property
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for RimProperty.
    //
    // Four independently-gateable mechanics, found by reading every .cs
    // file in this mod before writing this:
    //   1. Perception/propagation (PropertyEngine.RollPerceptionAndPropagate)
    //      — witnesses seeing a theft and telling their faction.
    //   2. Animal theft (AnimalTheftUtility.FindStealTarget, the single
    //      choke point both JobGiver_RM_TrainedSteal and JobGiver_RM_WildSteal
    //      call through).
    //   3. Theft Hauler (FloatMenuOptionProvider_TheftHaulUninstall) — the
    //      right-click "steal and haul away this building" order.
    //   4. Salvage claim fees (FloatMenuOptionProvider_PaySalvageClaim /
    //      SalvageClaimFeeUtility) — the right-click "pay off a claim" order.
    //
    // The claim engine itself (ClaimEngine/ClaimDecay/GameComponent_
    // PropertyLedger/PropertyEngine.Fire's WasAuthorized resolution) is left
    // ungated: RaidRedesigner's Patch_CaravanRobbed Harmony-postfixes
    // PropertyEngine.Fire and reads its resolved TakingEvent, so turning the
    // ledger itself off would silently break another shipped mod's capture
    // hook. Perception/propagation is the part that is safe and meaningful
    // to disable on its own (it only affects whether anyone ever notices).
    //
    // Precedent: src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    // ════════════════════════════════════════════════════════════════════
    public class PropertySettings : ModSettings
    {
        // --- Perception / propagation --------------------------------------
        public static bool perceptionEnabled = true;
        public static float witnessRadius = PropertyTuning.DefaultWitnessRadius;
        public static float witnessConfidence = PropertyTuning.DefaultWitnessConfidence;
        public static float suspicionHalfLifeDays = PropertyTuning.SuspicionHalfLifeDays;

        // --- Claim memory length --------------------------------------------
        // Scales both PropertyTuning.MinClaimLifetimeDays and
        // MaxClaimLifetimeDays together, read by ClaimDecay.LifetimeTicks.
        public static float claimLifetimeMultiplier = 1f;

        // --- Animal theft ----------------------------------------------------
        public static bool animalTheftEnabled = true;
        public static float animalTheftMaxItemMassKg = PropertyTuning.AnimalTheftMaxItemMassKg;
        public static float animalTheftSearchRadius = PropertyTuning.AnimalTheftSearchRadius;
        // The animal's own ThinkTree ChancePerHour node decides how often
        // TryGiveJob is even called — this can only throttle it FURTHER,
        // never make it happen more than the AI's own check interval allows.
        public static float animalTheftFrequencyMultiplier = 1f;

        // --- Theft Hauler ------------------------------------------------------
        public static bool theftHaulerEnabled = true;

        // --- Salvage claim fee --------------------------------------------------
        public static bool salvageClaimFeeEnabled = true;
        public static float salvageClaimFeeMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref perceptionEnabled, "perceptionEnabled", true);
            Scribe_Values.Look(ref witnessRadius, "witnessRadius", PropertyTuning.DefaultWitnessRadius);
            Scribe_Values.Look(ref witnessConfidence, "witnessConfidence", PropertyTuning.DefaultWitnessConfidence);
            Scribe_Values.Look(ref suspicionHalfLifeDays, "suspicionHalfLifeDays", PropertyTuning.SuspicionHalfLifeDays);
            Scribe_Values.Look(ref claimLifetimeMultiplier, "claimLifetimeMultiplier", 1f);
            Scribe_Values.Look(ref animalTheftEnabled, "animalTheftEnabled", true);
            Scribe_Values.Look(ref animalTheftMaxItemMassKg, "animalTheftMaxItemMassKg", PropertyTuning.AnimalTheftMaxItemMassKg);
            Scribe_Values.Look(ref animalTheftSearchRadius, "animalTheftSearchRadius", PropertyTuning.AnimalTheftSearchRadius);
            Scribe_Values.Look(ref animalTheftFrequencyMultiplier, "animalTheftFrequencyMultiplier", 1f);
            Scribe_Values.Look(ref theftHaulerEnabled, "theftHaulerEnabled", true);
            Scribe_Values.Look(ref salvageClaimFeeEnabled, "salvageClaimFeeEnabled", true);
            Scribe_Values.Look(ref salvageClaimFeeMultiplier, "salvageClaimFeeMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Getting caught");
            list.CheckboxLabeled("Witnesses notice unauthorized takings", ref perceptionEnabled,
                "Off: taking someone else's stuff is never witnessed or reported to their faction. "
              + "Claims are still tracked underneath, just never enforced by suspicion.");
            if (perceptionEnabled)
            {
                list.Label("How far a witness can see it happen: " + witnessRadius.ToString("0") + " tiles");
                witnessRadius = list.Slider(witnessRadius, 5f, 40f);
                list.Label("Chance a witness's account sticks: " + (witnessConfidence * 100f).ToString("0") + "%");
                witnessConfidence = list.Slider(witnessConfidence, 0f, 1f);
                list.Label("How long suspicion lingers: " + suspicionHalfLifeDays.ToString("0") + " days");
                suspicionHalfLifeDays = list.Slider(suspicionHalfLifeDays, 5f, 180f);
            }
            list.GapLine();

            list.Label("Claim memory: " + claimLifetimeMultiplier.ToString("0.00") + "x");
            list.Label("How long an ownership claim is remembered before it fades. 1x is the default "
              + "(a plain item is forgotten in days, a named/valuable one for years).");
            claimLifetimeMultiplier = list.Slider(claimLifetimeMultiplier, 0.25f, 4f);
            list.GapLine();

            list.CheckboxLabeled("Animal theft", ref animalTheftEnabled,
                "Trained pets and wild animals can be prompted or opportunistically grab small "
              + "unattended items. Off: animals never do this.");
            if (animalTheftEnabled)
            {
                list.Label("  Heaviest item an animal will grab: " + animalTheftMaxItemMassKg.ToString("0.0") + " kg");
                animalTheftMaxItemMassKg = list.Slider(animalTheftMaxItemMassKg, 0.5f, 10f);
                list.Label("  Search range: " + animalTheftSearchRadius.ToString("0") + " tiles");
                animalTheftSearchRadius = list.Slider(animalTheftSearchRadius, 6f, 48f);
                list.Label("  Frequency: " + animalTheftFrequencyMultiplier.ToString("0.00") + "x "
                  + "(can only reduce it below the animal's own default checking rate)");
                animalTheftFrequencyMultiplier = list.Slider(animalTheftFrequencyMultiplier, 0f, 1f);
            }
            list.GapLine();

            list.CheckboxLabeled("Theft Hauler (steal and haul away a building)", ref theftHaulerEnabled,
                "A pawn with the theft-hauler marker can right-click any building to uninstall and "
              + "carry it off. Off: that order never appears.");
            list.Gap();

            list.CheckboxLabeled("Salvage claim fees (pay off a claim)", ref salvageClaimFeeEnabled,
                "Lets a pawn right-click something to pay a fee that settles a lingering ownership "
              + "claim on it. Off: that order never appears.");
            if (salvageClaimFeeEnabled)
            {
                list.Label("  Fee amount: " + salvageClaimFeeMultiplier.ToString("0.00") + "x");
                salvageClaimFeeMultiplier = list.Slider(salvageClaimFeeMultiplier, 0.25f, 3f);
            }

            list.End();
        }
    }

    public class PropertyOptionsMod : Mod
    {
        public static PropertySettings settings;

        public PropertyOptionsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<PropertySettings>();
        }

        public override string SettingsCategory()
        {
            return "RimProperty";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
