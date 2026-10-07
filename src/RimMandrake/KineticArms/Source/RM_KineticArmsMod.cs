using System;
using System.Collections.Generic;
using System.Globalization;
using HarmonyLib;
using RimMandrake.ExplosiveKnockback;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.KineticArms
{
    /// <summary>Mod Settings (design §4, build §10). Defaults = shipped behaviour; nothing here affects worldgen.</summary>
    public class RimMandrakeKineticArmsSettings : ModSettings
    {
        public static bool enableThudder = true;
        public static bool enablePalmThumper = true;
        public static bool enableSlamLauncher = true;
        public static bool enableRepulsorRifle = true;
        public static bool enableKickerMine = true;
        public static bool enableThumpShell = true;
        public static bool enablePulseCannon = true;
        public static bool enableGravRam = true;
        public static float kineticStrength = 1f;
        public static bool thumpCannonThrows = true;
        public static float thumpCannonForce = 2.5f;
        public static bool kickerRearms = true;
        public static float kickerFuelPerKick = 10f;
        public static int pulseCapacity = 4;
        public static float pulseRechargeSeconds = 20f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enableThudder, "enableThudder", true);
            Scribe_Values.Look(ref enablePalmThumper, "enablePalmThumper", true);
            Scribe_Values.Look(ref enableSlamLauncher, "enableSlamLauncher", true);
            Scribe_Values.Look(ref enableRepulsorRifle, "enableRepulsorRifle", true);
            Scribe_Values.Look(ref enableKickerMine, "enableKickerMine", true);
            Scribe_Values.Look(ref enableThumpShell, "enableThumpShell", true);
            Scribe_Values.Look(ref enablePulseCannon, "enablePulseCannon", true);
            Scribe_Values.Look(ref enableGravRam, "enableGravRam", true);
            Scribe_Values.Look(ref kineticStrength, "kineticStrength", 1f);
            Scribe_Values.Look(ref thumpCannonThrows, "thumpCannonThrows", true);
            Scribe_Values.Look(ref thumpCannonForce, "thumpCannonForce", 2.5f);
            Scribe_Values.Look(ref kickerRearms, "kickerRearms", true);
            Scribe_Values.Look(ref kickerFuelPerKick, "kickerFuelPerKick", 10f);
            Scribe_Values.Look(ref pulseCapacity, "pulseCapacity", 4);
            Scribe_Values.Look(ref pulseRechargeSeconds, "pulseRechargeSeconds", 20f);
        }
    }

    public class RimMandrakeKineticArmsMod : Mod
    {
        public static RimMandrakeKineticArmsSettings Settings;
        private Vector2 scroll;

        /// <summary>weapon toggle field -> the ThingDefs it governs (the item; for buildings the building).</summary>
        public static readonly (string field, string label, string def)[] Weapons =
        {
            ("enableThudder", "Thudder grenades", "RM_Weapon_ThudderGrenade"),
            ("enablePalmThumper", "Palm thumper", "RM_Gun_PalmThumper"),
            ("enableSlamLauncher", "Slam launcher", "RM_Gun_SlamLauncher"),
            ("enableRepulsorRifle", "Repulsor rifle", "RM_Gun_RepulsorRifle"),
            ("enableKickerMine", "Kicker mine", "RM_KickerMine"),
            ("enableThumpShell", "Thump shell", "RM_Shell_Thump"),
            ("enablePulseCannon", "Pulse cannon", "RM_Turret_PulseCannon"),
            ("enableGravRam", "Grav-ram", "RM_Gun_GravRam"),
        };

        /// <summary>Our per-weapon DamageDefs and their shipped forces (the XML values), captured once at startup.</summary>
        private static readonly Dictionary<DamageDef, float> baseForces = new Dictionary<DamageDef, float>();
        private static readonly Dictionary<ThingDef, (Tradeability trade, List<string> tags, List<string> setTags)> baseAvail
            = new Dictionary<ThingDef, (Tradeability, List<string>, List<string>)>();

        public RimMandrakeKineticArmsMod(ModContentPack content) : base(content)
        {
            Settings = GetSettings<RimMandrakeKineticArmsSettings>();
            new Harmony("mandrake.rm.kineticarms").PatchAll(typeof(RimMandrakeKineticArmsMod).Assembly);
            LongEventHandler.ExecuteWhenFinished(Capture);
        }

        private static void Capture()
        {
            foreach (DamageDef d in DefDatabase<DamageDef>.AllDefs)
            {
                if (d.defName.StartsWith("RM_Concussive_") || d.defName.StartsWith("RM_Repulse_"))
                {
                    RM_KnockbackExtension ext = d.GetModExtension<RM_KnockbackExtension>();
                    if (ext != null)
                    {
                        baseForces[d] = ext.force;
                    }
                }
            }
            foreach (var w in Weapons)
            {
                ThingDef td = DefDatabase<ThingDef>.GetNamedSilentFail(w.def);
                if (td != null)
                {
                    baseAvail[td] = (td.tradeability, td.weaponTags != null ? new List<string>(td.weaponTags) : null,
                        td.thingSetMakerTags != null ? new List<string>(td.thingSetMakerTags) : null);
                }
            }
            ApplySettings();
        }

        public static bool Enabled(string field)
        {
            return (bool)typeof(RimMandrakeKineticArmsSettings).GetField(field).GetValue(null);
        }

        /// <summary>Pushes the settings into the defs: our forces × strength, the Thump force, and per-weapon
        /// availability (off = never traded, never generated on pawns or in reward sets; existing ones keep working).</summary>
        public static void ApplySettings()
        {
            foreach (var kv in baseForces)
            {
                RM_KnockbackExtension ext = kv.Key.GetModExtension<RM_KnockbackExtension>();
                if (ext != null)
                {
                    ext.force = RM_KineticMath.ScaledForce(kv.Value, RimMandrakeKineticArmsSettings.kineticStrength);
                }
            }
            DamageDef thump = DefDatabase<DamageDef>.GetNamedSilentFail("Thump");
            RM_KnockbackExtension te = thump?.GetModExtension<RM_KnockbackExtension>();
            if (te != null)
            {
                te.force = RimMandrakeKineticArmsSettings.thumpCannonThrows ? RimMandrakeKineticArmsSettings.thumpCannonForce : 0f;
            }
            foreach (var w in Weapons)
            {
                ThingDef td = DefDatabase<ThingDef>.GetNamedSilentFail(w.def);
                if (td == null || !baseAvail.TryGetValue(td, out var orig))
                {
                    continue;
                }
                bool on = Enabled(w.field);
                td.tradeability = on ? orig.trade : Tradeability.None;
                td.weaponTags = on ? (orig.tags != null ? new List<string>(orig.tags) : null) : (orig.tags != null ? new List<string>() : null);
                td.thingSetMakerTags = on ? (orig.setTags != null ? new List<string>(orig.setTags) : null) : (orig.setTags != null ? new List<string>() : null);
            }
        }

        public static float ForceOf(string damageDef)
        {
            return DefDatabase<DamageDef>.GetNamedSilentFail(damageDef)?.GetModExtension<RM_KnockbackExtension>()?.force ?? -1f;
        }

        public override string SettingsCategory() => "RimMandrake: Kinetic Arms";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 20f, 720f);
            Widgets.BeginScrollView(inRect, ref scroll, view);
            var l = new Listing_Standard();
            l.Begin(view);
            l.Label("Weapons (off: never traded, carried or given as a reward; ones already in the world keep working)");
            foreach (var w in Weapons)
            {
                var f = typeof(RimMandrakeKineticArmsSettings).GetField(w.field);
                bool v = (bool)f.GetValue(null);
                l.CheckboxLabeled("  " + w.label, ref v);
                f.SetValue(null, v);
            }
            l.GapLine();
            l.Label("Kinetic throw strength: " + RimMandrakeKineticArmsSettings.kineticStrength.ToString("0.00", CultureInfo.InvariantCulture)
                + "x  (multiplies only these weapons' throws, on top of Explosive Knockback's own strength)");
            RimMandrakeKineticArmsSettings.kineticStrength = l.Slider(RimMandrakeKineticArmsSettings.kineticStrength, 0f, 3f);
            l.CheckboxLabeled("Thump cannons throw farther", ref RimMandrakeKineticArmsSettings.thumpCannonThrows,
                "The mechanoid thump cannon's blast throws people (5 cells beside the impact at the default force). Off: vanilla, it throws nothing.");
            l.Label("Thump cannon throw force: " + RimMandrakeKineticArmsSettings.thumpCannonForce.ToString("0.0", CultureInfo.InvariantCulture)
                + "  (a mortar shell is 1.0)");
            RimMandrakeKineticArmsSettings.thumpCannonForce = l.Slider(RimMandrakeKineticArmsSettings.thumpCannonForce, 0f, 4f);
            l.GapLine();
            l.CheckboxLabeled("Kicker mines re-arm", ref RimMandrakeKineticArmsSettings.kickerRearms,
                "On: a kick spends chemfuel and the mine stays. Off: the mine is used up by its first kick.");
            l.Label("Chemfuel per kick: " + RimMandrakeKineticArmsSettings.kickerFuelPerKick.ToString("0", CultureInfo.InvariantCulture));
            RimMandrakeKineticArmsSettings.kickerFuelPerKick = Mathf.Round(l.Slider(RimMandrakeKineticArmsSettings.kickerFuelPerKick, 1f, 30f));
            l.GapLine();
            l.Label("Pulse cannon stored charges: " + RimMandrakeKineticArmsSettings.pulseCapacity);
            RimMandrakeKineticArmsSettings.pulseCapacity = (int)l.Slider(RimMandrakeKineticArmsSettings.pulseCapacity, 1f, 12f);
            l.Label("Pulse cannon seconds to refill one charge (powered): " + RimMandrakeKineticArmsSettings.pulseRechargeSeconds.ToString("0", CultureInfo.InvariantCulture));
            RimMandrakeKineticArmsSettings.pulseRechargeSeconds = Mathf.Round(l.Slider(RimMandrakeKineticArmsSettings.pulseRechargeSeconds, 1f, 120f));
            l.Gap();
            if (l.ButtonText("Reset to defaults"))
            {
                Reset();
            }
            l.End();
            Widgets.EndScrollView();
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            ApplySettings();
        }

        public static void Reset()
        {
            RimMandrakeKineticArmsSettings.enableThudder = true;
            RimMandrakeKineticArmsSettings.enablePalmThumper = true;
            RimMandrakeKineticArmsSettings.enableSlamLauncher = true;
            RimMandrakeKineticArmsSettings.enableRepulsorRifle = true;
            RimMandrakeKineticArmsSettings.enableKickerMine = true;
            RimMandrakeKineticArmsSettings.enableThumpShell = true;
            RimMandrakeKineticArmsSettings.enablePulseCannon = true;
            RimMandrakeKineticArmsSettings.enableGravRam = true;
            RimMandrakeKineticArmsSettings.kineticStrength = 1f;
            RimMandrakeKineticArmsSettings.thumpCannonThrows = true;
            RimMandrakeKineticArmsSettings.thumpCannonForce = 2.5f;
            RimMandrakeKineticArmsSettings.kickerRearms = true;
            RimMandrakeKineticArmsSettings.kickerFuelPerKick = 10f;
            RimMandrakeKineticArmsSettings.pulseCapacity = 4;
            RimMandrakeKineticArmsSettings.pulseRechargeSeconds = 20f;
            ApplySettings();
        }
    }

    /// <summary>Kinetic Arms' own journal of bolt / kick blasts (centre, cell count), read by the proof scenes beside
    /// Explosive Knockback's journal.</summary>
    public static class RM_KineticArmsJournal
    {
        public static readonly List<Dictionary<string, object>> Recs = new List<Dictionary<string, object>>();

        public static void Add(string type, string def, IntVec3 impact, IntVec3 centre, int cells)
        {
            Recs.Add(new Dictionary<string, object>
            {
                ["type"] = type, ["tick"] = Find.TickManager?.TicksGame ?? 0, ["def"] = def,
                ["impact"] = impact, ["centre"] = centre, ["cells"] = cells,
            });
            if (Recs.Count > 2000)
            {
                Recs.RemoveRange(0, 500);
            }
        }
    }
}
