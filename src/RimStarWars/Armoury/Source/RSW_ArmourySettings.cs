using System.Collections.Generic;
using System.Reflection;
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

        // ── Alloy forge durasteel (SHIP_ALLOY_FORGE_1, Patches/RSW_AlloyForge_Durasteel.xml) ──
        public static bool durasteelAlloyEnabled = true;

        // ── Doonium, phrik and aboard slag re-melt (ASTEROID_DESERT_ORES_1, Patches/RSW_Smelter_Alloys.xml) ──
        public static bool dooniumAsteroidEnabled = true;
        public static bool dooniumSmeltEnabled = true;
        public static bool phrikSmeltEnabled = true;
        public static bool slagRemeltAboardEnabled = true;

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

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RSW_ArmourySettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RSW_ArmourySettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

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

            Scribe_Values.Look(ref durasteelAlloyEnabled, "durasteelAlloyEnabled", true, true);
            Scribe_Values.Look(ref dooniumAsteroidEnabled, "dooniumAsteroidEnabled", true, true);
            Scribe_Values.Look(ref dooniumSmeltEnabled, "dooniumSmeltEnabled", true, true);
            Scribe_Values.Look(ref phrikSmeltEnabled, "phrikSmeltEnabled", true, true);
            Scribe_Values.Look(ref slagRemeltAboardEnabled, "slagRemeltAboardEnabled", true, true);

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
            RSW_CombatKernel.InstantHealReuseTicks(instantHealReuseHours);

        /// <summary>How recently a pawn must have been harmed to count as "in danger" (shipped: 2500).</summary>
        public static int InstantHealRecentHarmTicks =>
            RSW_CombatKernel.InstantHealRecentHarmTicks(instantHealRecentHarmHours);

        /// <summary>Scales a squared-distance threshold, so the slider reads as a plain distance factor.</summary>
        public static float ScaleSquaredDistance(float shippedSquared) =>
            RSW_CombatKernel.ScaleSquaredDistance(shippedSquared, jumppackDistanceFactor);

        /// <summary>Ticks between one healed injury and the next, from the tank's own shipped interval.</summary>
        public static int KoltoHealInterval(int shippedTicks) =>
            RSW_KoltoKernel.HealInterval(shippedTicks, koltoHealSpeed);

        private static float settingsViewHeight = 1500f;

        public void DoWindowContents(Rect inRect)
        {
            Rect viewRect = new Rect(0f, 0f, inRect.width - 24f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPosition, viewRect);

            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            list.Label("Every option below is a runtime mechanic. Turning one off makes that "
                     + "mechanic do nothing - the items, buildings and weapons stay in the game. "
                     + "The weapon damage rebalance this mod is built around is part of the item "
                     + "definitions themselves and is always on.");
            list.GapLine();

            if (Group(list, "Extra weapon sounds", RimMandrake.Shared.SettingScope.Now, new[] { "extraSoundsEnabled" }))
            {
                list.CheckboxLabeled("Custom melee hit and miss sounds", ref extraSoundsEnabled,
                    "Weapons and pawn kinds that carry their own melee sounds use them. "
                  + "Off: the game's ordinary melee sounds play instead.");
                list.GapLine();
            }

            if (Group(list, "Lightsaber crystal formations (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "crystalFormationsEnabled", "crystalAbundance" }))
            {
                list.CheckboxLabeled("Crystals grow in caves", ref crystalFormationsEnabled,
                    "Crystal formations are scattered through the cave systems of a newly generated "
                  + "map. Off: no crystals are placed. Maps that already exist never change.");
                list.Label("How many crystals: " + AbundanceLabel());
                crystalAbundance = list.Slider(crystalAbundance, 0.25f, 3f);
                list.GapLine();
            }

            if (Group(list, "Emergency healing gear", RimMandrake.Shared.SettingScope.Now, new[] { "instantHealEnabled", "instantHealReuseHours", "instantHealRecentHarmHours" }))
            {
                list.CheckboxLabeled("Enemies use healing gear when hurt", ref instantHealEnabled,
                    "Pawns who are carrying instant-healing gear reach for it in a fight, the same "
                  + "way they reach for combat drugs. Off: they never use it on their own; you can "
                  + "still trigger it yourself.");
                list.Label("Wait before using it again: " + instantHealReuseHours.ToString("0.0") + " hours");
                instantHealReuseHours = list.Slider(instantHealReuseHours, 0f, 24f);
                list.Label("Counts as \"just been hurt\" for: " + instantHealRecentHarmHours.ToString("0.00") + " hours");
                instantHealRecentHarmHours = list.Slider(instantHealRecentHarmHours, 0.1f, 6f);
                list.GapLine();
            }

            if (Group(list, "Jumppack charges", RimMandrake.Shared.SettingScope.Now, new[] { "jumppackEnabled", "jumppackFlankRanged", "jumppackDistanceFactor" }))
            {
                list.CheckboxLabeled("Enemies jump at you with jumppacks", ref jumppackEnabled,
                    "A hostile melee fighter wearing a jumppack leaps the gap instead of running it. "
                  + "Off: they walk, exactly like a fighter with no jumppack.");
                list.CheckboxLabeled("  Also jump past cover at shooters", ref jumppackFlankRanged,
                    "Enemies jump behind a target who is hiding behind cover. Off: they only jump "
                  + "to close on a melee target.");
                list.Label("How far away they will jump from: " + jumppackDistanceFactor.ToString("0.00") + "x the usual");
                jumppackDistanceFactor = list.Slider(jumppackDistanceFactor, 0.25f, 3f);
                list.GapLine();
            }

            if (Group(list, "Kolto tank", RimMandrake.Shared.SettingScope.Now, new[] { "koltoHealEnabled", "koltoHealSpeed" }))
            {
                list.CheckboxLabeled("Kolto tanks heal the pawn inside", ref koltoHealEnabled,
                    "A powered, fuelled tank cures one injury at a time. Off: the tank still holds "
                  + "a pawn and still works as a container, it just does not heal.");
                list.Label("Healing speed: " + koltoHealSpeed.ToString("0.00") + "x");
                koltoHealSpeed = list.Slider(koltoHealSpeed, 0.25f, 3f);
                list.GapLine();
            }

            if (Group(list, "Mental break suppression", RimMandrake.Shared.SettingScope.Now, new[] { "mentalBreakBlockerEnabled" }))
            {
                list.CheckboxLabeled("Some gear and implants hold a break off", ref mentalBreakBlockerEnabled,
                    "Things that promise to stop a pawn breaking down actually stop it. "
                  + "Off: mental breaks happen normally for everyone.");
                list.GapLine();
            }

            if (Group(list, "Defusing mines", RimMandrake.Shared.SettingScope.Now, new[] { "minePocketEnabled", "minePocketDefuseTime" }))
            {
                list.CheckboxLabeled("Mines can be defused and recovered", ref minePocketEnabled,
                    "A pawn can defuse a planted mine and pick the parts back up. "
                  + "Off: the job is never taken; mines are only removed the ordinary ways.");
                list.Label("Time it takes: " + minePocketDefuseTime.ToString("0.00") + "x");
                minePocketDefuseTime = list.Slider(minePocketDefuseTime, 0.25f, 5f);
                list.GapLine();
            }

            if (Group(list, "Bonus finds while mining", RimMandrake.Shared.SettingScope.Now, new[] { "secondaryYieldEnabled", "secondaryYieldChance", "secondaryYieldAmount" }))
            {
                list.CheckboxLabeled("Rock sometimes gives a second material", ref secondaryYieldEnabled,
                    "Mining certain rock drops an extra item on top of the usual yield. "
                  + "Off: only the normal yield drops.");
                list.Label("Chance of a bonus find: " + secondaryYieldChance.ToString("0.00") + "x");
                secondaryYieldChance = list.Slider(secondaryYieldChance, 0f, 3f);
                list.Label("Size of the bonus find: " + secondaryYieldAmount.ToString("0.00") + "x");
                secondaryYieldAmount = list.Slider(secondaryYieldAmount, 0.25f, 3f);
                list.GapLine();
            }

            if (Group(list, "Ship alloys, doonium and slag re-melt", RimMandrake.Shared.SettingScope.Now, new[] { "durasteelAlloyEnabled", "dooniumAsteroidEnabled", "dooniumSmeltEnabled", "phrikSmeltEnabled", "slagRemeltAboardEnabled" }, "[next game start]"))
            {
                list.CheckboxLabeled("Alloy forge makes durasteel from steel and zersium", ref durasteelAlloyEnabled,
                    "On (shipped default): the ship's alloy forge (VFE Factory) has a durasteel recipe, "
                  + "steel plus zersium ore, as its first alloy. Off: durasteel comes only from salvage "
                  + "and trade.");
                list.CheckboxLabeled("Doonium ore on asteroid maps", ref dooniumAsteroidEnabled,
                    "On (shipped default): Odyssey asteroid maps carry doonium ore. Off: doonium comes only from "
                  + "salvage and trade.");
                list.CheckboxLabeled("Ship smelter makes doonium from ore and glower crust", ref dooniumSmeltEnabled,
                    "On (shipped default): the ship's smelter (VFE Factory) can smelt doonium ore with glower crust.");
                list.CheckboxLabeled("Ship smelter makes phrik from phrikite", ref phrikSmeltEnabled,
                    "On (shipped default): the ship's smelter can smelt phrikite ore into phrik.");
                list.CheckboxLabeled("Ship smelter re-melts plasteel and durasteel slag", ref slagRemeltAboardEnabled,
                    "On (shipped default): salvage slag of plasteel and durasteel melts back into plate on the ship's smelter.");
                list.GapLine();
            }

            if (Group(list, "Gear that buffs its wearer", RimMandrake.Shared.SettingScope.Now, new[] { "selfHediffVerbEnabled", "selfHediffCooldown" }))
            {
                list.CheckboxLabeled("Worn gear can be triggered for an effect", ref selfHediffVerbEnabled,
                    "Apparel with a use-on-yourself button applies its effect. "
                  + "Off: the button refuses and nothing is applied.");
                list.Label("Cooldown between uses: " + selfHediffCooldown.ToString("0.00") + "x");
                selfHediffCooldown = list.Slider(selfHediffCooldown, 0.25f, 3f);
                list.GapLine();
            }

            if (Group(list, "Thrown weapons that come back", RimMandrake.Shared.SettingScope.Now, new[] { "returningWeaponEnabled", "returningWeaponSpeed" }))
            {
                list.CheckboxLabeled("A thrown weapon flies home to its owner", ref returningWeaponEnabled,
                    "The weapon spins out, hits, and returns to the hand that threw it. "
                  + "Off: no return flight is spawned and the weapon stays drawn in hand.");
                list.Label("Return flight speed: " + returningWeaponSpeed.ToString("0.00") + "x");
                returningWeaponSpeed = list.Slider(returningWeaponSpeed, 0.25f, 3f);
                list.GapLine();
            }

            if (Group(list, "Ion and stun damage", RimMandrake.Shared.SettingScope.Now, new[] { "ionDamageEnabled", "ionSeverity", "plasmaGrenadeFires" }))
            {
                list.CheckboxLabeled("Ion weapons stun and disable targets", ref ionDamageEnabled,
                    "Ion and stun hits add their disabling effect on top of the damage. "
                  + "Off: those weapons deal their damage and nothing more.");
                list.Label("Strength of the effect: " + ionSeverity.ToString("0.00") + "x");
                ionSeverity = list.Slider(ionSeverity, 0.25f, 3f);
                list.CheckboxLabeled("Plasma grenades set fires", ref plasmaGrenadeFires,
                    "A plasma blast can ignite what it lands on. Off: it burns targets but starts "
                  + "no fires.");
                list.GapLine();
            }

            settingsViewHeight = list.CurHeight + 20f;
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
