using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    /// <summary>A DamageDef's throw strength (design §3.1). Bomb ships 1.0; Flame, EMP, Smoke, Extinguish and
    /// ToxGas ship an explicit 0. Other mods' explosive DamageDefs get one by patch, never by guess.</summary>
    public class RM_KnockbackExtension : DefModExtension
    {
        public float force = 1f;
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

        public static KbSettings Kernel()
        {
            return new KbSettings
            {
                globalMultiplier = strength,
                maxCells = maxThrowCells,
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
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref strength, "strength", 1f);
            Scribe_Values.Look(ref maxThrowCells, "maxThrowCells", 6);
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
        }
    }

    public class RimMandrakeExplosiveKnockbackMod : Mod
    {
        public static RimMandrakeExplosiveKnockbackSettings Settings;
        private Vector2 scroll;

        public RimMandrakeExplosiveKnockbackMod(ModContentPack content) : base(content)
        {
            Settings = GetSettings<RimMandrakeExplosiveKnockbackSettings>();
            new Harmony("mandrake.rm.explosiveknockback").PatchAll(typeof(RimMandrakeExplosiveKnockbackMod).Assembly);
            LongEventHandler.ExecuteWhenFinished(RM_KnockbackCompat.Init);
        }

        public override string SettingsCategory() => "RimMandrake: Explosive Knockback";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 20f, 900f);
            Widgets.BeginScrollView(inRect, ref scroll, view);
            var l = new Listing_Standard();
            l.Begin(view);
            l.CheckboxLabeled("Enable explosive knockback", ref RimMandrakeExplosiveKnockbackSettings.enabled,
                "Every blast throws pawns, items and corpses near it straight away from its centre. Off: vanilla.");
            l.Label("Throw strength: " + RimMandrakeExplosiveKnockbackSettings.strength.ToString("0.00")
                + "x  (1.0 = a mortar shell beside a person throws them 3 cells)");
            RimMandrakeExplosiveKnockbackSettings.strength = l.Slider(RimMandrakeExplosiveKnockbackSettings.strength, 0f, 3f);
            l.Label("Maximum throw distance: " + RimMandrakeExplosiveKnockbackSettings.maxThrowCells + " cells");
            RimMandrakeExplosiveKnockbackSettings.maxThrowCells = (int)l.Slider(RimMandrakeExplosiveKnockbackSettings.maxThrowCells, 1f, 10f);
            l.Label("Explosions from other mods with no knockback setting throw at: "
                + RimMandrakeExplosiveKnockbackSettings.unpatchedHarmfulPercent.ToString("0") + "%");
            RimMandrakeExplosiveKnockbackSettings.unpatchedHarmfulPercent = l.Slider(RimMandrakeExplosiveKnockbackSettings.unpatchedHarmfulPercent, 0f, 100f);
            l.CheckboxLabeled("Throw downed pawns", ref RimMandrakeExplosiveKnockbackSettings.throwDowned);
            l.CheckboxLabeled("Throw animals", ref RimMandrakeExplosiveKnockbackSettings.throwAnimals);
            l.CheckboxLabeled("Throw mechanoids", ref RimMandrakeExplosiveKnockbackSettings.throwMechanoids);
            l.Label("Too big to throw at body size: " + RimMandrakeExplosiveKnockbackSettings.immuneBodySize.ToString("0.0"));
            RimMandrakeExplosiveKnockbackSettings.immuneBodySize = l.Slider(RimMandrakeExplosiveKnockbackSettings.immuneBodySize, 1f, 5f);
            l.CheckboxLabeled("Throw items", ref RimMandrakeExplosiveKnockbackSettings.throwItems);
            l.CheckboxLabeled("Throw corpses", ref RimMandrakeExplosiveKnockbackSettings.throwCorpses);
            l.Label("Items and corpses heavier than " + RimMandrakeExplosiveKnockbackSettings.lightMassLimit.ToString("0") + " kg stay put");
            RimMandrakeExplosiveKnockbackSettings.lightMassLimit = l.Slider(RimMandrakeExplosiveKnockbackSettings.lightMassLimit, 5f, 200f);
            l.CheckboxLabeled("Sandbags and barricades stop a throw", ref RimMandrakeExplosiveKnockbackSettings.sandbagsStopThrow,
                "Off (the default): people are thrown over sandbags and barricades.");
            l.CheckboxLabeled("Impact damage on hitting a wall or another pawn", ref RimMandrakeExplosiveKnockbackSettings.impactDamageEnabled);
            l.Label("Impact damage per cell not travelled: " + RimMandrakeExplosiveKnockbackSettings.impactDamagePerCell.ToString("0.0"));
            RimMandrakeExplosiveKnockbackSettings.impactDamagePerCell = l.Slider(RimMandrakeExplosiveKnockbackSettings.impactDamagePerCell, 0f, 15f);
            l.Label("Landing stun: " + RimMandrakeExplosiveKnockbackSettings.landingStunMin + "-" + RimMandrakeExplosiveKnockbackSettings.landingStunMax + " ticks");
            RimMandrakeExplosiveKnockbackSettings.landingStunMin = (int)l.Slider(RimMandrakeExplosiveKnockbackSettings.landingStunMin, 0f, 300f);
            RimMandrakeExplosiveKnockbackSettings.landingStunMax = Mathf.Max(RimMandrakeExplosiveKnockbackSettings.landingStunMin,
                (int)l.Slider(RimMandrakeExplosiveKnockbackSettings.landingStunMax, 0f, 300f));
            l.CheckboxLabeled("Doors take impact damage", ref RimMandrakeExplosiveKnockbackSettings.doorsTakeDamage);
            l.CheckboxLabeled("Throw into FlowWorks pits", ref RimMandrakeExplosiveKnockbackSettings.throwIntoPits,
                "Off: an open pit stops a throw like a wall.");
            l.Label("Max throws per explosion: " + RimMandrakeExplosiveKnockbackSettings.maxThrowsPerExplosion);
            RimMandrakeExplosiveKnockbackSettings.maxThrowsPerExplosion = (int)l.Slider(RimMandrakeExplosiveKnockbackSettings.maxThrowsPerExplosion, 1f, 200f);
            l.Label("Max item throws per map tick: " + RimMandrakeExplosiveKnockbackSettings.maxItemThrowsPerMapTick);
            RimMandrakeExplosiveKnockbackSettings.maxItemThrowsPerMapTick = (int)l.Slider(RimMandrakeExplosiveKnockbackSettings.maxItemThrowsPerMapTick, 1f, 500f);
            if (Prefs.DevMode)
            {
                l.CheckboxLabeled("Debug: draw throw vectors", ref RimMandrakeExplosiveKnockbackSettings.debugDrawVectors);
            }
            if (l.ButtonText("Reset to defaults"))
            {
                Reset();
            }
            l.End();
            Widgets.EndScrollView();
        }

        public static void Reset()
        {
            RimMandrakeExplosiveKnockbackSettings.enabled = true;
            RimMandrakeExplosiveKnockbackSettings.strength = 1f;
            RimMandrakeExplosiveKnockbackSettings.maxThrowCells = 6;
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
        }
    }
}
