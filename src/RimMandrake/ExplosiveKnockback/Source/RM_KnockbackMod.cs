using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    /// <summary>A DamageDef's throw strength (design §3.1). Bomb ships 1.0; Flame, EMP, Smoke, Extinguish and
    /// ToxGas ship an explicit 0. Other mods' explosive DamageDefs get one by patch, never by guess.
    /// maxThrowCells: this blast's own maximum throw (cells); 0 = the global "Maximum throw distance".
    /// impactFactor: scales wall / pawn / door impact damage for this blast (0 = no impact: an arrest tool).
    /// immuneBodySizeOverride: replaces the global "too big to throw" body size for this blast (0 = unset); eligibility is
    /// "body size below it", so 3.6 throws a 3.5 body.
    /// Lookup (design §2.1): the explosion's PROJECTILE ThingDef, then its WEAPON ThingDef, then its DamageDef; the first
    /// that carries this extension supplies the whole configuration.</summary>
    public class RM_KnockbackExtension : DefModExtension
    {
        public float force = 1f;
        public int maxThrowCells = 0;
        public float impactFactor = 1f;
        public float immuneBodySizeOverride = 0f;

        public KbConfig ToConfig()
        {
            return new KbConfig { force = force, ownCap = maxThrowCells, impactFactor = impactFactor, immuneOverride = immuneBodySizeOverride };
        }
    }

    [DefOf]
    public static class RM_KnockbackDefOf
    {
        public static ThingDef RM_PawnFlyer_Knockback;

        static RM_KnockbackDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_KnockbackDefOf));
        }
    }

    /// <summary>Mod Settings (design §5). Defaults = the owner's rulings of 2026-10-06 (§11); all off = vanilla.
    /// Nothing here affects worldgen.</summary>
    public class RimMandrakeExplosiveKnockbackSettings : ModSettings
    {
        public static bool enabled = true;
        public static float strength = 1f;
        public static int maxThrowCells = 6;
        public static float ownCapScale = 1f;
        public static float unpatchedHarmfulPercent = 0f;
        public static bool throwDowned = true;
        public static bool throwAnimals = true;
        public static bool throwMechanoids = true;
        public static float immuneBodySize = 2.5f;
        public static bool throwItems = true;
        public static bool throwCorpses = true;
        public static float lightMassLimit = 75f;
        public static bool sandbagsStopThrow = false;
        public static bool impactDamageEnabled = true;
        public static float impactDamagePerCell = 4f;
        public static int landingStunMin = 60;
        public static int landingStunMax = 120;
        public static bool doorsTakeDamage = true;
        public static bool throwIntoPits = true;
        public static int maxThrowsPerExplosion = 40;
        public static int maxItemThrowsPerMapTick = 60;
        public static bool debugDrawVectors = false;
        public static int recoveryWindowTicks = 120;
        public static bool shieldsAbsorbThrow = true;
        public static float shieldDebitPerForce = 10f;

        /// <summary>Per-request kernel settings for one blast's configuration (never mutates the shared settings).</summary>
        public static KbSettings Kernel(KbConfig c)
        {
            return KbLookup.Apply(Kernel(), c, maxThrowCells, ownCapScale);
        }

        public static KbSettings Kernel(int ownCap = 0)
        {
            return new KbSettings
            {
                globalMultiplier = strength,
                maxCells = RM_KnockbackMath.CapFor(ownCap, maxThrowCells, ownCapScale),
                immuneBodySize = immuneBodySize,
                lightMassLimit = lightMassLimit,
                impactEnabled = impactDamageEnabled,
                impactPerCell = impactDamagePerCell,
                sandbagsStop = sandbagsStopThrow,
                intoPits = throwIntoPits,
            };
        }

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref strength, "strength", 1f);
            Scribe_Values.Look(ref maxThrowCells, "maxThrowCells", 6);
            Scribe_Values.Look(ref ownCapScale, "ownCapScale", 1f);
            Scribe_Values.Look(ref unpatchedHarmfulPercent, "unpatchedHarmfulPercent", 0f);
            Scribe_Values.Look(ref throwDowned, "throwDowned", true);
            Scribe_Values.Look(ref throwAnimals, "throwAnimals", true);
            Scribe_Values.Look(ref throwMechanoids, "throwMechanoids", true);
            Scribe_Values.Look(ref immuneBodySize, "immuneBodySize", 2.5f);
            Scribe_Values.Look(ref throwItems, "throwItems", true);
            Scribe_Values.Look(ref throwCorpses, "throwCorpses", true);
            Scribe_Values.Look(ref lightMassLimit, "lightMassLimit", 75f);
            Scribe_Values.Look(ref sandbagsStopThrow, "sandbagsStopThrow", false);
            Scribe_Values.Look(ref impactDamageEnabled, "impactDamageEnabled", true);
            Scribe_Values.Look(ref impactDamagePerCell, "impactDamagePerCell", 4f);
            Scribe_Values.Look(ref landingStunMin, "landingStunMin", 60);
            Scribe_Values.Look(ref landingStunMax, "landingStunMax", 120);
            Scribe_Values.Look(ref doorsTakeDamage, "doorsTakeDamage", true);
            Scribe_Values.Look(ref throwIntoPits, "throwIntoPits", true);
            Scribe_Values.Look(ref maxThrowsPerExplosion, "maxThrowsPerExplosion", 40);
            Scribe_Values.Look(ref maxItemThrowsPerMapTick, "maxItemThrowsPerMapTick", 60);
            Scribe_Values.Look(ref debugDrawVectors, "debugDrawVectors", false);
            Scribe_Values.Look(ref recoveryWindowTicks, "recoveryWindowTicks", 120);
            Scribe_Values.Look(ref shieldsAbsorbThrow, "shieldsAbsorbThrow", true);
            Scribe_Values.Look(ref shieldDebitPerForce, "shieldDebitPerForce", 10f);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        private static Vector2 scroll;
        private static float settingsViewHeight = 1100f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 20f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Mod switch", RimMandrake.Shared.SettingScope.Now, new[] { "enabled" }))
            {
                list.CheckboxLabeled("Enable explosive knockback", ref enabled,
                    "Every blast throws pawns, items and corpses near it straight away from its centre. Off: vanilla.");
                list.GapLine();
            }

            if (Group(list, "Throw strength and range", RimMandrake.Shared.SettingScope.Now, new[] { "strength", "maxThrowCells", "ownCapScale", "unpatchedHarmfulPercent" }))
            {
                list.Label("Throw strength: " + strength.ToString("0.00")
                    + "x  (1.0 = a mortar shell beside a person throws them 3 cells)");
                strength = list.Slider(strength, 0f, 3f);
                list.Label("Maximum throw distance: " + maxThrowCells
                    + " cells  (blasts that do not set their own maximum: vanilla and most modded explosions)");
                maxThrowCells = (int)list.Slider(maxThrowCells, 1f, 10f);
                list.Label("Weapons that set their own maximum throw: " + ownCapScale.ToString("0.00")
                    + "x their maximum  (1.0 = as designed, e.g. grav-ram 10 cells, thump cannon 8)");
                ownCapScale = list.Slider(ownCapScale, 0.25f, 2f);
                list.Label("Explosions from other mods with no knockback setting throw at: "
                    + unpatchedHarmfulPercent.ToString("0") + "%");
                unpatchedHarmfulPercent = list.Slider(unpatchedHarmfulPercent, 0f, 100f);
                list.GapLine();
            }

            if (Group(list, "What gets thrown", RimMandrake.Shared.SettingScope.Now, new[] { "throwDowned", "throwAnimals", "throwMechanoids", "immuneBodySize", "throwItems", "throwCorpses", "lightMassLimit" }))
            {
                list.CheckboxLabeled("Throw downed pawns", ref throwDowned);
                list.CheckboxLabeled("Throw animals", ref throwAnimals);
                list.CheckboxLabeled("Throw mechanoids", ref throwMechanoids);
                list.Label("Too big to throw at body size: " + immuneBodySize.ToString("0.0"));
                immuneBodySize = list.Slider(immuneBodySize, 1f, 5f);
                list.CheckboxLabeled("Throw items", ref throwItems);
                list.CheckboxLabeled("Throw corpses", ref throwCorpses);
                list.Label("Items and corpses heavier than " + lightMassLimit.ToString("0") + " kg stay put");
                lightMassLimit = list.Slider(lightMassLimit, 5f, 200f);
                list.GapLine();
            }

            if (Group(list, "Impact and landing", RimMandrake.Shared.SettingScope.Now, new[] { "sandbagsStopThrow", "impactDamageEnabled", "impactDamagePerCell", "landingStunMin", "landingStunMax", "recoveryWindowTicks", "doorsTakeDamage", "throwIntoPits" }))
            {
                list.CheckboxLabeled("Sandbags and barricades stop a throw", ref sandbagsStopThrow,
                    "Off (the default): people are thrown over sandbags and barricades.");
                list.CheckboxLabeled("Impact damage on hitting a wall or another pawn", ref impactDamageEnabled);
                list.Label("Impact damage per cell not travelled: " + impactDamagePerCell.ToString("0.0"));
                impactDamagePerCell = list.Slider(impactDamagePerCell, 0f, 15f);
                list.Label("Landing stun: " + landingStunMin + "-" + landingStunMax + " ticks");
                landingStunMin = (int)list.Slider(landingStunMin, 0f, 300f);
                landingStunMax = (int)list.Slider(landingStunMax, 0f, 300f);
                landingStunMax = Mathf.Max(landingStunMin, landingStunMax);
                list.Label("Recovery after a throw: " + recoveryWindowTicks
                    + " ticks after the landing stun ends before the same pawn can be thrown again  (0 = chain throws allowed)");
                recoveryWindowTicks = (int)list.Slider(recoveryWindowTicks, 0f, 600f);
                list.CheckboxLabeled("Doors take impact damage", ref doorsTakeDamage);
                list.CheckboxLabeled("Throw into FlowWorks pits", ref throwIntoPits,
                    "Off: an open pit stops a throw like a wall.");
                list.GapLine();
            }

            if (Group(list, "Shield belts", RimMandrake.Shared.SettingScope.Now, new[] { "shieldsAbsorbThrow", "shieldDebitPerForce" }))
            {
                list.CheckboxLabeled("Shield belts absorb the throw", ref shieldsAbsorbThrow,
                    "On: a pawn whose shield absorbed the blast is not thrown, and the shield pays extra charge for it (a strong throw can pop it). Off: shields stop the wound, never the shove.");
                list.Label("Extra shield drain per point of throw force: " + shieldDebitPerForce.ToString("0")
                    + " damage-equivalents");
                shieldDebitPerForce = Mathf.Round(list.Slider(shieldDebitPerForce, 0f, 50f));
                list.GapLine();
            }

            if (Group(list, "Performance caps and debug", RimMandrake.Shared.SettingScope.Now, new[] { "maxThrowsPerExplosion", "maxItemThrowsPerMapTick", "debugDrawVectors" }))
            {
                list.Label("Max throws per explosion: " + maxThrowsPerExplosion);
                maxThrowsPerExplosion = (int)list.Slider(maxThrowsPerExplosion, 1f, 200f);
                list.Label("Max item throws per map tick: " + maxItemThrowsPerMapTick);
                maxItemThrowsPerMapTick = (int)list.Slider(maxItemThrowsPerMapTick, 1f, 500f);
                if (Prefs.DevMode)
                {
                    list.CheckboxLabeled("Debug: draw throw vectors", ref debugDrawVectors);
                }
                list.GapLine();
            }

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RimMandrakeExplosiveKnockbackSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RimMandrakeExplosiveKnockbackSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

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
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }
    }

    public class RimMandrakeExplosiveKnockbackMod : Mod
    {
        public static RimMandrakeExplosiveKnockbackSettings Settings;

        public RimMandrakeExplosiveKnockbackMod(ModContentPack content) : base(content)
        {
            Settings = GetSettings<RimMandrakeExplosiveKnockbackSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.explosiveknockback"), typeof(RimMandrakeExplosiveKnockbackMod).Assembly, "RimMandrake.ExplosiveKnockback", "RimMandrake.ExplosiveKnockback");
            LongEventHandler.ExecuteWhenFinished(RM_KnockbackCompat.Init);
        }

        public override string SettingsCategory() => "RimMandrake: Explosive Knockback";

        public override void DoSettingsWindowContents(Rect inRect) => Settings.DoWindowContents(inRect);

        public static void Reset()
        {
            RimMandrakeExplosiveKnockbackSettings.enabled = true;
            RimMandrakeExplosiveKnockbackSettings.strength = 1f;
            RimMandrakeExplosiveKnockbackSettings.maxThrowCells = 6;
            RimMandrakeExplosiveKnockbackSettings.ownCapScale = 1f;
            RimMandrakeExplosiveKnockbackSettings.unpatchedHarmfulPercent = 0f;
            RimMandrakeExplosiveKnockbackSettings.throwDowned = true;
            RimMandrakeExplosiveKnockbackSettings.throwAnimals = true;
            RimMandrakeExplosiveKnockbackSettings.throwMechanoids = true;
            RimMandrakeExplosiveKnockbackSettings.immuneBodySize = 2.5f;
            RimMandrakeExplosiveKnockbackSettings.throwItems = true;
            RimMandrakeExplosiveKnockbackSettings.throwCorpses = true;
            RimMandrakeExplosiveKnockbackSettings.lightMassLimit = 75f;
            RimMandrakeExplosiveKnockbackSettings.sandbagsStopThrow = false;
            RimMandrakeExplosiveKnockbackSettings.impactDamageEnabled = true;
            RimMandrakeExplosiveKnockbackSettings.impactDamagePerCell = 4f;
            RimMandrakeExplosiveKnockbackSettings.landingStunMin = 60;
            RimMandrakeExplosiveKnockbackSettings.landingStunMax = 120;
            RimMandrakeExplosiveKnockbackSettings.doorsTakeDamage = true;
            RimMandrakeExplosiveKnockbackSettings.throwIntoPits = true;
            RimMandrakeExplosiveKnockbackSettings.maxThrowsPerExplosion = 40;
            RimMandrakeExplosiveKnockbackSettings.maxItemThrowsPerMapTick = 60;
            RimMandrakeExplosiveKnockbackSettings.debugDrawVectors = false;
            RimMandrakeExplosiveKnockbackSettings.recoveryWindowTicks = 120;
            RimMandrakeExplosiveKnockbackSettings.shieldsAbsorbThrow = true;
            RimMandrakeExplosiveKnockbackSettings.shieldDebitPerForce = 10f;
        }
    }
}
