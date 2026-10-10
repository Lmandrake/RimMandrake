using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Property
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for RimProperty.
    //
    // Eight independently-gateable mechanics, found by reading every .cs
    // file in this mod before writing this (walkable commerce, pickpocket,
    // hire-the-placeless, and bribes/bought-rounds added by
    // SETTLEMENT_VERBS_WAVE_1):
    //   1. Perception/propagation (PropertyEngine.RollPerceptionAndPropagate)
    //      — witnesses seeing a theft and telling their faction.
    //   2. Animal theft (AnimalTheftUtility.FindStealTarget, the single
    //      choke point both JobGiver_RM_TrainedSteal and JobGiver_RM_WildSteal
    //      call through).
    //   3. Theft Hauler (FloatMenuOptionProvider_TheftHaulUninstall) — the
    //      right-click "steal and haul away this building" order.
    //   4. Salvage claim fees (FloatMenuOptionProvider_PaySalvageClaim /
    //      SalvageClaimFeeUtility) — the right-click "pay off a claim" order.
    //   5. Walkable commerce (FloatMenuOptionProvider_BuyMerchandise /
    //      BuyMerchandiseUtility) — the right-click "buy this from its
    //      current owner" order.
    //   6. Pickpocket (FloatMenuOptionProvider_Pickpocket /
    //      PickpocketUtility) — the right-click "lift something from their
    //      inventory" order.
    //   7. Hire the placeless (FloatMenuOptionProvider_HirePlaceless /
    //      HirePlacelessUtility) — the right-click "hire this faction-less
    //      pawn/droid" order.
    //   8. Bribes / bought rounds (FloatMenuOptionProvider_Bribe /
    //      BribeUtility) — the right-click "buy a round" order that cools
    //      off a faction's own suspicion record (FactionRecord.
    //      DampenSuspicion), no TakingEvent involved.
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

        // --- Walkable commerce (SETTLEMENT_VERBS_WAVE_1) -----------------------
        public static bool walkableCommerceEnabled = true;
        public static float walkableCommerceMarkup = PropertyTuning.WalkableCommerceMarkup;

        // --- Pickpocket (SETTLEMENT_VERBS_WAVE_1, crime-suite pass) -------------
        public static bool pickpocketEnabled = true;
        public static float pickpocketMinItemValueSilver = PropertyTuning.PickpocketMinItemValueSilver;

        // --- Hire the placeless (SETTLEMENT_VERBS_WAVE_1, social-fabric pass) --
        public static bool hirePlacelessEnabled = true;
        public static float hirePlacelessFeeSilver = PropertyTuning.HirePlacelessFeeSilver;

        // --- Bribes / bought rounds (SETTLEMENT_VERBS_WAVE_1, social-fabric pass) --
        public static bool bribeEnabled = true;
        public static float bribeFeeSilver = PropertyTuning.BribeFeeSilver;
        public static float bribeDampenFraction = PropertyTuning.BribeDampenFraction;

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
            Scribe_Values.Look(ref walkableCommerceEnabled, "walkableCommerceEnabled", true);
            Scribe_Values.Look(ref walkableCommerceMarkup, "walkableCommerceMarkup", PropertyTuning.WalkableCommerceMarkup);
            Scribe_Values.Look(ref pickpocketEnabled, "pickpocketEnabled", true);
            Scribe_Values.Look(ref pickpocketMinItemValueSilver, "pickpocketMinItemValueSilver", PropertyTuning.PickpocketMinItemValueSilver);
            Scribe_Values.Look(ref hirePlacelessEnabled, "hirePlacelessEnabled", true);
            Scribe_Values.Look(ref hirePlacelessFeeSilver, "hirePlacelessFeeSilver", PropertyTuning.HirePlacelessFeeSilver);
            Scribe_Values.Look(ref bribeEnabled, "bribeEnabled", true);
            Scribe_Values.Look(ref bribeFeeSilver, "bribeFeeSilver", PropertyTuning.BribeFeeSilver);
            Scribe_Values.Look(ref bribeDampenFraction, "bribeDampenFraction", PropertyTuning.BribeDampenFraction);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(PropertySettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(PropertySettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1200f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10).</summary>
        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards" : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Getting caught", RimMandrake.Shared.SettingScope.Now, new[] { "perceptionEnabled", "witnessRadius", "witnessConfidence", "suspicionHalfLifeDays" }))
            {
                list.CheckboxLabeled("Witnesses notice unauthorized takings", ref perceptionEnabled,
                    "Off: taking someone else's stuff is never witnessed or reported to their faction. "
                  + "Claims are still tracked underneath, just never enforced by suspicion.");
                list.Label("How far a witness can see it happen: " + witnessRadius.ToString("0") + " tiles");
                witnessRadius = list.Slider(witnessRadius, 5f, 40f);
                list.Label("Chance a witness's account sticks: " + (witnessConfidence * 100f).ToString("0") + "%");
                witnessConfidence = list.Slider(witnessConfidence, 0f, 1f);
                list.Label("How long suspicion lingers: " + suspicionHalfLifeDays.ToString("0") + " days");
                suspicionHalfLifeDays = list.Slider(suspicionHalfLifeDays, 5f, 180f);
                list.GapLine();
            }

            if (Group(list, "Claim memory", RimMandrake.Shared.SettingScope.Now, new[] { "claimLifetimeMultiplier" }))
            {
                list.Label("Claim memory: " + claimLifetimeMultiplier.ToString("0.00") + "x");
                list.Label("How long an ownership claim is remembered before it fades. 1x is the default "
                  + "(a plain item is forgotten in days, a named/valuable one for years).");
                claimLifetimeMultiplier = list.Slider(claimLifetimeMultiplier, 0.25f, 4f);
                list.GapLine();
            }

            if (Group(list, "Animal theft", RimMandrake.Shared.SettingScope.Now, new[] { "animalTheftEnabled", "animalTheftMaxItemMassKg", "animalTheftSearchRadius", "animalTheftFrequencyMultiplier" }))
            {
                list.CheckboxLabeled("Animal theft", ref animalTheftEnabled,
                    "Trained pets and wild animals can be prompted or opportunistically grab small "
                  + "unattended items. Off: animals never do this.");
                list.Label("  Heaviest item an animal will grab: " + animalTheftMaxItemMassKg.ToString("0.0") + " kg");
                animalTheftMaxItemMassKg = list.Slider(animalTheftMaxItemMassKg, 0.5f, 10f);
                list.Label("  Search range: " + animalTheftSearchRadius.ToString("0") + " tiles");
                animalTheftSearchRadius = list.Slider(animalTheftSearchRadius, 6f, 48f);
                list.Label("  Frequency: " + animalTheftFrequencyMultiplier.ToString("0.00") + "x "
                  + "(can only reduce it below the animal's own default checking rate)");
                animalTheftFrequencyMultiplier = list.Slider(animalTheftFrequencyMultiplier, 0f, 1f);
                list.GapLine();
            }

            if (Group(list, "Theft Hauler", RimMandrake.Shared.SettingScope.Now, new[] { "theftHaulerEnabled" }))
            {
                list.CheckboxLabeled("Theft Hauler (steal and haul away a building)", ref theftHaulerEnabled,
                    "A pawn with the theft-hauler marker can right-click any building to uninstall and "
                  + "carry it off. Off: that order never appears.");
                list.GapLine();
            }

            if (Group(list, "Salvage claim fees", RimMandrake.Shared.SettingScope.Now, new[] { "salvageClaimFeeEnabled", "salvageClaimFeeMultiplier" }))
            {
                list.CheckboxLabeled("Salvage claim fees (pay off a claim)", ref salvageClaimFeeEnabled,
                    "Lets a pawn right-click something to pay a fee that settles a lingering ownership "
                  + "claim on it. Off: that order never appears.");
                list.Label("  Fee amount: " + salvageClaimFeeMultiplier.ToString("0.00") + "x");
                salvageClaimFeeMultiplier = list.Slider(salvageClaimFeeMultiplier, 0.25f, 3f);
                list.GapLine();
            }

            if (Group(list, "Walkable commerce", RimMandrake.Shared.SettingScope.Now, new[] { "walkableCommerceEnabled", "walkableCommerceMarkup" }))
            {
                list.CheckboxLabeled("Walkable commerce (buy merchandise on the spot)", ref walkableCommerceEnabled,
                    "Lets a pawn right-click something someone else already owns to buy it on the spot, "
                  + "priced off its market value. Records the purchase as a legal provenance record. "
                  + "Off: that order never appears.");
                list.Label("  Price markup: " + walkableCommerceMarkup.ToString("0.00") + "x market value");
                walkableCommerceMarkup = list.Slider(walkableCommerceMarkup, 0.5f, 3f);
                list.GapLine();
            }

            if (Group(list, "Pickpocket", RimMandrake.Shared.SettingScope.Now, new[] { "pickpocketEnabled", "pickpocketMinItemValueSilver" }))
            {
                list.CheckboxLabeled("Pickpocket (lift an item from someone's own inventory)", ref pickpocketEnabled,
                    "Lets a pawn right-click another pawn to lift something out of their carried inventory. "
                  + "Never their equipped weapon or worn apparel. Risk of being noticed uses the same "
                  + "witness settings above. Off: that order never appears.");
                list.Label("  Not worth the risk below: " + pickpocketMinItemValueSilver.ToString("0") + " silver");
                pickpocketMinItemValueSilver = list.Slider(pickpocketMinItemValueSilver, 0f, 50f);
                list.GapLine();
            }

            if (Group(list, "Hire the placeless", RimMandrake.Shared.SettingScope.Now, new[] { "hirePlacelessEnabled", "hirePlacelessFeeSilver" }))
            {
                list.CheckboxLabeled("Hire the placeless (pay a faction-less pawn or droid to work for you)", ref hirePlacelessEnabled,
                    "Lets a pawn right-click a faction-less wanderer or masterless droid nobody else claims "
                  + "and pay a flat hiring advance. Records the hire as a legal provenance record — no job, "
                  + "schedule or following behavior yet. Off: that order never appears.");
                list.Label("  Hiring advance: " + hirePlacelessFeeSilver.ToString("0") + " silver");
                hirePlacelessFeeSilver = list.Slider(hirePlacelessFeeSilver, 0f, 100f);
                list.GapLine();
            }

            if (Group(list, "Bribes and bought rounds", RimMandrake.Shared.SettingScope.Now, new[] { "bribeEnabled", "bribeFeeSilver", "bribeDampenFraction" }))
            {
                list.CheckboxLabeled("Bribes / bought rounds (cool off a faction's suspicion)", ref bribeEnabled,
                    "Lets a pawn right-click a factioned pawn from a different faction and pay for a round, "
                  + "cooling off some of whatever that faction already knows about the payer. Never reveals "
                  + "whether there was anything to cool off. Off: that order never appears.");
                list.Label("  Cost per round: " + bribeFeeSilver.ToString("0") + " silver");
                bribeFeeSilver = list.Slider(bribeFeeSilver, 0f, 100f);
                list.Label("  Suspicion cooled per round: " + (bribeDampenFraction * 100f).ToString("0") + "%");
                bribeDampenFraction = list.Slider(bribeDampenFraction, 0f, 1f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
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
