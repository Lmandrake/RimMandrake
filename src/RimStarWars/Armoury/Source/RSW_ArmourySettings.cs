using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Armoury
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Jawa Armoury Rebalance
    // (mandrake.rsw.armoury).
    //
    // Precedent followed exactly: src/RimMandrake/GelatinousSlime/Source/
    // SlimeMod.cs and src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // 🔑 STATIC FIELDS, READ FROM EVERYWHERE, WRITTEN ONLY HERE. Every gate
    // in this assembly sits inside a Harmony patch, a DamageWorker, a
    // ThingComp or a GenStep — none of which has a Mod instance handy — so
    // the values must be statics that survive a settings load.
    //
    // This mod is an "absorbed" bundle: one assembly carrying a dozen
    // otherwise-unrelated runtime mechanisms, each in its own namespace.
    // One toggle per mechanism, plus a slider wherever a real hardcoded
    // number decides the experience.
    //
    // ⛔ NOT gated here: the weapon damage rebalance itself. That is baked
    // into ThingDef XML at load time by a generator + PatchOperations —
    // there is no runtime C# mechanism to short-circuit, so there is
    // nothing a runtime toggle could honestly check against.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_ArmourySettings : ModSettings
    {
        // One vanilla in-game hour. Several shipped numbers below are
        // expressed as hours because that is what the raw tick counts are.
        public const float TicksPerHour = 2500f;

        // ── Extra weapon sounds (CompExtraSounds) ───────────────────────
        public static bool extraSoundsEnabled = true;

        // ── Crystal formations (CrystalFormations, WORLDGEN) ────────────
        public static bool crystalFormationsEnabled = true;
        public static float crystalAbundance = 1f;

        // ── Instant healing drug (InstantHealingDrug) ───────────────────
        public static bool instantHealEnabled = true;
        public static float instantHealReuseHours = 8f;       // 20000 ticks shipped
        public static float instantHealRecentHarmHours = 1f;  //  2500 ticks shipped

        // ── Jumppack for melee AI (JumppackForMeleeAI) ──────────────────
        public static bool jumppackEnabled = true;
        public static bool jumppackFlankRanged = true;
        public static float jumppackDistanceFactor = 1f;

        // ── Kolto tank (KoltoTank) ──────────────────────────────────────
        public static bool koltoHealEnabled = true;
        public static float koltoHealSpeed = 1f;

        // ── Mental break blocker (MentalBreakBlocker) ───────────────────
        public static bool mentalBreakBlockerEnabled = true;

        // ── Mine pocket / defusing (MinePocket) ─────────────────────────
        public static bool minePocketEnabled = true;
        public static float minePocketDefuseTime = 1f;

        // ── Bonus mining yield (SecondaryMineableYield) ─────────────────
        public static bool secondaryYieldEnabled = true;
        public static float secondaryYieldChance = 1f;
        public static float secondaryYieldAmount = 1f;

        // ── Gear self-buff abilities (SelfHediffVerb) ───────────────────
        public static bool selfHediffVerbEnabled = true;
        public static float selfHediffCooldown = 1f;

        // ── Returning thrown weapons (Spinning_Projectile) ──────────────
        public static bool returningWeaponEnabled = true;
        public static float returningWeaponSpeed = 1f;

        // ── Ion / stun damage (guy762_Ionization + guy762_IonizationABF) ─
        public static bool ionDamageEnabled = true;
        public static float ionSeverity = 1f;
        public static bool plasmaGrenadeFires = true;

        private Vector2 scrollPosition;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref extraSoundsEnabled, "extraSoundsEnabled", true, true);

            Scribe_Values.Look(ref crystalFormationsEnabled, "crystalFormationsEnabled", true, true);
            Scribe_Values.Look(ref crystalAbundance, "crystalAbundance", 1f, true);

            Scribe_Values.Look(ref instantHealEnabled, "instantHealEnabled", true, true);
            Scribe_Values.Look(ref instantHealReuseHours, "instantHealReuseHours", 8f, true);
            Scribe_Values.Look(ref instantHealRecentHarmHours, "instantHealRecentHarmHours", 1f, true);

            Scribe_Values.Look(ref jumppackEnabled, "jumppackEnabled", true, true);
            Scribe_Values.Look(ref jumppackFlankRanged, "jumppackFlankRanged", true, true);
            Scribe_Values.Look(ref jumppackDistanceFactor, "jumppackDistanceFactor", 1f, true);

            Scribe_Values.Look(ref koltoHealEnabled, "koltoHealEnabled", true, true);
            Scribe_Values.Look(ref koltoHealSpeed, "koltoHealSpeed", 1f, true);

            Scribe_Values.Look(ref mentalBreakBlockerEnabled, "mentalBreakBlockerEnabled", true, true);

            Scribe_Values.Look(ref minePocketEnabled, "minePocketEnabled", true, true);
            Scribe_Values.Look(ref minePocketDefuseTime, "minePocketDefuseTime", 1f, true);

            Scribe_Values.Look(ref secondaryYieldEnabled, "secondaryYieldEnabled", true, true);
            Scribe_Values.Look(ref secondaryYieldChance, "secondaryYieldChance", 1f, true);
            Scribe_Values.Look(ref secondaryYieldAmount, "secondaryYieldAmount", 1f, true);

            Scribe_Values.Look(ref selfHediffVerbEnabled, "selfHediffVerbEnabled", true, true);
            Scribe_Values.Look(ref selfHediffCooldown, "selfHediffCooldown", 1f, true);

            Scribe_Values.Look(ref returningWeaponEnabled, "returningWeaponEnabled", true, true);
            Scribe_Values.Look(ref returningWeaponSpeed, "returningWeaponSpeed", 1f, true);

            Scribe_Values.Look(ref ionDamageEnabled, "ionDamageEnabled", true, true);
            Scribe_Values.Look(ref ionSeverity, "ionSeverity", 1f, true);
            Scribe_Values.Look(ref plasmaGrenadeFires, "plasmaGrenadeFires", true, true);
        }

        // ── Derived values the mechanisms actually read ─────────────────

        /// <summary>Ticks an AI pawn must wait before reaching for the healing gear again (shipped: 20000).</summary>
        public static int InstantHealReuseTicks =>
            Mathf.Max(0, Mathf.RoundToInt(instantHealReuseHours * TicksPerHour));

        /// <summary>How recently a pawn must have been harmed to count as "in danger" (shipped: 2500).</summary>
        public static int InstantHealRecentHarmTicks =>
            Mathf.Max(1, Mathf.RoundToInt(instantHealRecentHarmHours * TicksPerHour));

        /// <summary>Scales a squared-distance threshold, so the slider reads as a plain distance factor.</summary>
        public static float ScaleSquaredDistance(float shippedSquared) =>
            shippedSquared * jumppackDistanceFactor * jumppackDistanceFactor;

        /// <summary>Ticks between one healed injury and the next, from the tank's own shipped interval.</summary>
        public static int KoltoHealInterval(int shippedTicks) =>
            Mathf.Max(1, Mathf.RoundToInt(shippedTicks / Mathf.Max(0.01f, koltoHealSpeed)));

        public void DoWindowContents(Rect inRect)
        {
            Rect viewRect = new Rect(0f, 0f, inRect.width - 24f, 1500f);
            Widgets.BeginScrollView(inRect, ref scrollPosition, viewRect);

            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width };
            list.Begin(viewRect);

            list.Label("Every option below is a runtime mechanic. Turning one off makes that "
                     + "mechanic do nothing — the items, buildings and weapons stay in the game. "
                     + "The weapon damage rebalance this mod is built around is part of the item "
                     + "definitions themselves and is always on.");
            list.GapLine();

            // ── Extra weapon sounds ─────────────────────────────────────
            list.Label("Extra weapon sounds");
            list.CheckboxLabeled("Custom melee hit and miss sounds", ref extraSoundsEnabled,
                "Weapons and pawn kinds that carry their own melee sounds use them. "
              + "Off: the game's ordinary melee sounds play instead.");
            list.GapLine();

            // ── Crystal formations (worldgen) ───────────────────────────
            list.Label("Lightsaber crystal formations (affects new maps only)");
            list.CheckboxLabeled("Crystals grow in caves", ref crystalFormationsEnabled,
                "Crystal formations are scattered through the cave systems of a newly generated "
              + "map. Off: no crystals are placed. Maps that already exist never change.");
            list.Label("How many crystals: " + AbundanceLabel() + "  (affects new maps only)");
            crystalAbundance = list.Slider(crystalAbundance, 0.25f, 3f);
            list.GapLine();

            // ── Instant healing drug ────────────────────────────────────
            list.Label("Emergency healing gear");
            list.CheckboxLabeled("Enemies use healing gear when hurt", ref instantHealEnabled,
                "Pawns who are carrying instant-healing gear reach for it in a fight, the same "
              + "way they reach for combat drugs. Off: they never use it on their own; you can "
              + "still trigger it yourself.");
            list.Label("Wait before using it again: " + instantHealReuseHours.ToString("0.0") + " hours");
            instantHealReuseHours = list.Slider(instantHealReuseHours, 0f, 24f);
            list.Label("Counts as \"just been hurt\" for: " + instantHealRecentHarmHours.ToString("0.00") + " hours");
            instantHealRecentHarmHours = list.Slider(instantHealRecentHarmHours, 0.1f, 6f);
            list.GapLine();

            // ── Jumppack melee AI ───────────────────────────────────────
            list.Label("Jumppack charges");
            list.CheckboxLabeled("Enemies jump at you with jumppacks", ref jumppackEnabled,
                "A hostile melee fighter wearing a jumppack leaps the gap instead of running it. "
              + "Off: they walk, exactly like a fighter with no jumppack.");
            list.CheckboxLabeled("  Also jump past cover at shooters", ref jumppackFlankRanged,
                "Enemies jump behind a target who is hiding behind cover. Off: they only jump "
              + "to close on a melee target.");
            list.Label("How far away they will jump from: " + jumppackDistanceFactor.ToString("0.00") + "x the usual");
            jumppackDistanceFactor = list.Slider(jumppackDistanceFactor, 0.25f, 3f);
            list.GapLine();

            // ── Kolto tank ──────────────────────────────────────────────
            list.Label("Kolto tank");
            list.CheckboxLabeled("Kolto tanks heal the pawn inside", ref koltoHealEnabled,
                "A powered, fuelled tank cures one injury at a time. Off: the tank still holds "
              + "a pawn and still works as a container, it just does not heal.");
            list.Label("Healing speed: " + koltoHealSpeed.ToString("0.00") + "x");
            koltoHealSpeed = list.Slider(koltoHealSpeed, 0.25f, 3f);
            list.GapLine();

            // ── Mental break blocker ────────────────────────────────────
            list.Label("Mental break suppression");
            list.CheckboxLabeled("Some gear and implants hold a break off", ref mentalBreakBlockerEnabled,
                "Things that promise to stop a pawn breaking down actually stop it. "
              + "Off: mental breaks happen normally for everyone.");
            list.GapLine();

            // ── Mine pocket ─────────────────────────────────────────────
            list.Label("Defusing mines");
            list.CheckboxLabeled("Mines can be defused and recovered", ref minePocketEnabled,
                "A pawn can defuse a planted mine and pick the parts back up. "
              + "Off: the job is never taken; mines are only removed the ordinary ways.");
            list.Label("Time it takes: " + minePocketDefuseTime.ToString("0.00") + "x");
            minePocketDefuseTime = list.Slider(minePocketDefuseTime, 0.25f, 5f);
            list.GapLine();

            // ── Secondary mineable yield ────────────────────────────────
            list.Label("Bonus finds while mining");
            list.CheckboxLabeled("Rock sometimes gives a second material", ref secondaryYieldEnabled,
                "Mining certain rock drops an extra item on top of the usual yield. "
              + "Off: only the normal yield drops.");
            list.Label("Chance of a bonus find: " + secondaryYieldChance.ToString("0.00") + "x");
            secondaryYieldChance = list.Slider(secondaryYieldChance, 0f, 3f);
            list.Label("Size of the bonus find: " + secondaryYieldAmount.ToString("0.00") + "x");
            secondaryYieldAmount = list.Slider(secondaryYieldAmount, 0.25f, 3f);
            list.GapLine();

            // ── Self-hediff verb ────────────────────────────────────────
            list.Label("Gear that buffs its wearer");
            list.CheckboxLabeled("Worn gear can be triggered for an effect", ref selfHediffVerbEnabled,
                "Apparel with a use-on-yourself button applies its effect. "
              + "Off: the button refuses and nothing is applied.");
            list.Label("Cooldown between uses: " + selfHediffCooldown.ToString("0.00") + "x");
            selfHediffCooldown = list.Slider(selfHediffCooldown, 0.25f, 3f);
            list.GapLine();

            // ── Returning thrown weapons ────────────────────────────────
            list.Label("Thrown weapons that come back");
            list.CheckboxLabeled("A thrown weapon flies home to its owner", ref returningWeaponEnabled,
                "The weapon spins out, hits, and returns to the hand that threw it. "
              + "Off: no return flight is spawned and the weapon stays drawn in hand.");
            list.Label("Return flight speed: " + returningWeaponSpeed.ToString("0.00") + "x");
            returningWeaponSpeed = list.Slider(returningWeaponSpeed, 0.25f, 3f);
            list.GapLine();

            // ── Ion damage ──────────────────────────────────────────────
            list.Label("Ion and stun damage");
            list.CheckboxLabeled("Ion weapons stun and disable targets", ref ionDamageEnabled,
                "Ion and stun hits add their disabling effect on top of the damage. "
              + "Off: those weapons deal their damage and nothing more.");
            list.Label("Strength of the effect: " + ionSeverity.ToString("0.00") + "x");
            ionSeverity = list.Slider(ionSeverity, 0.25f, 3f);
            list.CheckboxLabeled("Plasma grenades set fires", ref plasmaGrenadeFires,
                "A plasma blast can ignite what it lands on. Off: it burns targets but starts "
              + "no fires.");

            list.End();
            Widgets.EndScrollView();
        }

        private static string AbundanceLabel()
        {
            if (crystalAbundance < 0.6f) return "scarce (" + crystalAbundance.ToString("0.00") + "x)";
            if (crystalAbundance < 1.6f) return "default (" + crystalAbundance.ToString("0.00") + "x)";
            return "plentiful (" + crystalAbundance.ToString("0.00") + "x)";
        }
    }

    public class RSW_ArmouryMod : Mod
    {
        public static RSW_ArmourySettings settings;

        public RSW_ArmouryMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_ArmourySettings>();
        }

        public override string SettingsCategory()
        {
            return "Jawa Armoury";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
