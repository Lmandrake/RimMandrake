using System;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using HarmonyLib;
using RimMandrake.ExplosiveKnockback;
using RimWorld;
using UnityEngine;
using Verse;
using static RimMandrake.KineticArms.RimMandrakeKineticArmsSettings;

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
        public static bool lootedOnRaiders = true;
        public static float lootedChancePercent = 2f;
        public static bool foundInRuins = true;
        public static float ruinsChancePercent = 35f;   // PROVISIONAL: per ancient-danger temple
        public static bool foundInComplexes = true;      // Ideology ancient complexes: room loot + security crates
        public static bool kickerHidden = true;
        public static float pulsePowerDraw = 350f;
        public static bool kineticCutsCords = false;    // owner Q3: kinetic blasts sway cords, never cut them

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
            Scribe_Values.Look(ref lootedOnRaiders, "lootedOnRaiders", true);
            Scribe_Values.Look(ref lootedChancePercent, "lootedChancePercent", 2f);
            Scribe_Values.Look(ref foundInRuins, "foundInRuins", true);
            Scribe_Values.Look(ref ruinsChancePercent, "ruinsChancePercent", 35f);
            Scribe_Values.Look(ref foundInComplexes, "foundInComplexes", true);
            Scribe_Values.Look(ref kickerHidden, "kickerHidden", true);
            Scribe_Values.Look(ref pulsePowerDraw, "pulsePowerDraw", 350f);
            Scribe_Values.Look(ref kineticCutsCords, "kineticCutsCords", false);
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
        private static readonly Dictionary<DamageDef, RM_KineticBlastExtension> cordMarkers = new Dictionary<DamageDef, RM_KineticBlastExtension>();
        private static readonly Dictionary<ThingDef, (Tradeability trade, List<string> tags, List<string> setTags)> baseAvail
            = new Dictionary<ThingDef, (Tradeability, List<string>, List<string>)>();

        public RimMandrakeKineticArmsMod(ModContentPack content) : base(content)
        {
            Settings = GetSettings<RimMandrakeKineticArmsSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.kineticarms"), typeof(RimMandrakeKineticArmsMod).Assembly, "RimMandrake.KineticArms");
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
                    RM_KineticBlastExtension mk = d.GetModExtension<RM_KineticBlastExtension>();
                    if (mk != null)
                    {
                        cordMarkers[d] = mk;
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
            // owner Q3: the marker makes Gimme Some Slack's explosion hook spare cords; "cut cords" on removes it
            foreach (var kv in cordMarkers)
            {
                if (kv.Key.modExtensions == null)
                {
                    kv.Key.modExtensions = new List<DefModExtension>();
                }
                bool has = kv.Key.modExtensions.Contains(kv.Value);
                if (RimMandrakeKineticArmsSettings.kineticCutsCords && has)
                {
                    kv.Key.modExtensions.Remove(kv.Value);
                }
                else if (!RimMandrakeKineticArmsSettings.kineticCutsCords && !has)
                {
                    kv.Key.modExtensions.Add(kv.Value);
                }
            }
            ThingDef pulse = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Turret_PulseCannon");
            CompProperties_Power pp = pulse?.GetCompProperties<CompProperties_Power>();
            if (pp != null)
            {
                BasePower(pp) = Mathf.Max(0f, RimMandrakeKineticArmsSettings.pulsePowerDraw); // private field in 1.6
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

        private static readonly AccessTools.FieldRef<CompProperties_Power, float> BasePower =
            AccessTools.FieldRefAccess<CompProperties_Power, float>("basePowerConsumption");

        public static float ForceOf(string damageDef)
        {
            return DefDatabase<DamageDef>.GetNamedSilentFail(damageDef)?.GetModExtension<RM_KnockbackExtension>()?.force ?? -1f;
        }

        public override string SettingsCategory() => "RimMandrake: Kinetic Arms";

        public override void DoSettingsWindowContents(Rect inRect) => DoWindowContents(inRect);

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 20f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Weapons", RimMandrake.Shared.SettingScope.Now, new[] { "enableThudder", "enablePalmThumper", "enableSlamLauncher", "enableRepulsorRifle", "enableKickerMine", "enableThumpShell", "enablePulseCannon", "enableGravRam" }))
            {
                list.Label("Off: never traded, carried or given as a reward; ones already in the world keep working");
                list.CheckboxLabeled("  Thudder grenades", ref enableThudder);
                list.CheckboxLabeled("  Palm thumper", ref enablePalmThumper);
                list.CheckboxLabeled("  Slam launcher", ref enableSlamLauncher);
                list.CheckboxLabeled("  Repulsor rifle", ref enableRepulsorRifle);
                list.CheckboxLabeled("  Kicker mine", ref enableKickerMine);
                list.CheckboxLabeled("  Thump shell", ref enableThumpShell);
                list.CheckboxLabeled("  Pulse cannon", ref enablePulseCannon);
                list.CheckboxLabeled("  Grav-ram", ref enableGravRam);
                list.GapLine();
            }

            if (Group(list, "Throw strength, thump cannons and cords", RimMandrake.Shared.SettingScope.Now, new[] { "kineticStrength", "thumpCannonThrows", "thumpCannonForce", "kineticCutsCords" }))
            {
                list.Label("Kinetic throw strength: " + kineticStrength.ToString("0.00", CultureInfo.InvariantCulture)
                    + "x  (multiplies only these weapons' throws, on top of Explosive Knockback's own strength)");
                kineticStrength = list.Slider(kineticStrength, 0f, 3f);
                list.CheckboxLabeled("Thump cannons throw farther", ref thumpCannonThrows,
                    "The mechanoid thump cannon's blast throws people (5 cells beside the impact at the default force). Off: vanilla, it throws nothing.");
                list.Label("Thump cannon throw force: " + thumpCannonForce.ToString("0.0", CultureInfo.InvariantCulture)
                    + "  (a mortar shell is 1.0)");
                thumpCannonForce = list.Slider(thumpCannonForce, 0f, 4f);
                list.CheckboxLabeled("Kinetic blasts cut aerial cords", ref kineticCutsCords,
                    "Off (default): with Gimme Some Slack, a kinetic blast sways overhead cords and leaves them whole; only real explosions cut them. On: kinetic blasts cut cords like any other blast.");
                list.Label("Throw recovery window, shield belts vs throws: see Explosive Knockback's settings.");
                list.GapLine();
            }

            if (Group(list, "Kicker mines", RimMandrake.Shared.SettingScope.Now, new[] { "kickerRearms", "kickerFuelPerKick", "kickerHidden" }))
            {
                list.CheckboxLabeled("Kicker mines re-arm", ref kickerRearms,
                    "On: a kick spends chemfuel and the mine stays. Off: the mine is used up by its first kick.");
                list.Label("Chemfuel per kick: " + kickerFuelPerKick.ToString("0", CultureInfo.InvariantCulture));
                kickerFuelPerKick = Mathf.Round(list.Slider(kickerFuelPerKick, 1f, 30f));
                list.CheckboxLabeled("Kicker mines hidden from enemies", ref kickerHidden,
                    "On: like any trap, raiders do not see it. Off: raiders know where every kicker mine is and walk around it.");
                list.GapLine();
            }

            if (Group(list, "Pulse cannon", RimMandrake.Shared.SettingScope.Now, new[] { "pulseCapacity", "pulseRechargeSeconds", "pulsePowerDraw" }))
            {
                list.Label("Pulse cannon stored charges: " + pulseCapacity);
                pulseCapacity = (int)list.Slider(pulseCapacity, 1f, 12f);
                list.Label("Pulse cannon seconds to refill one charge (powered): " + pulseRechargeSeconds.ToString("0", CultureInfo.InvariantCulture));
                pulseRechargeSeconds = Mathf.Round(list.Slider(pulseRechargeSeconds, 1f, 120f));
                list.Label("Pulse cannon power draw: " + pulsePowerDraw.ToString("0", CultureInfo.InvariantCulture) + " W");
                pulsePowerDraw = Mathf.Round(list.Slider(pulsePowerDraw, 0f, 1500f) / 10f) * 10f;
                list.GapLine();
            }

            if (Group(list, "Raiders carrying looted weapons", RimMandrake.Shared.SettingScope.NextPulse, new[] { "lootedOnRaiders", "lootedChancePercent" }))
            {
                list.CheckboxLabeled("Pirate raiders sometimes carry kinetic weapons looted from ruins", ref lootedOnRaiders,
                    "Off: these weapons are found in ruins only. No other faction ever carries them.");
                list.Label("Chance a pirate gunner carries a looted one: " + lootedChancePercent.ToString("0.0", CultureInfo.InvariantCulture)
                    + "%  (grenadiers get thudder grenades; others a weapon they could afford)");
                lootedChancePercent = list.Slider(lootedChancePercent, 0f, 20f);
                list.GapLine();
            }

            if (Group(list, "Ruins and complexes loot (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "foundInRuins", "ruinsChancePercent", "foundInComplexes" }))
            {
                list.CheckboxLabeled("Kinetic weapons are found in ancient ruins", ref foundInRuins,
                    "Ancient Danger temples can hold one kinetic weapon (or a stack of thump shells) among their loot. Off: nothing places them in ruins.");
                list.Label("Chance an ancient temple holds one: " + ruinsChancePercent.ToString("0", CultureInfo.InvariantCulture) + "%");
                ruinsChancePercent = Mathf.Round(list.Slider(ruinsChancePercent, 0f, 100f));
                list.CheckboxLabeled("Kinetic weapons are found in ancient complexes", ref foundInComplexes,
                    "Ancient complex room loot and security crates can hold one kinetic weapon (a rare draw, about as rare as spacer components). Off: complexes never hold them. Grav-rams are the rarest find everywhere.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 12f;
            list.End();
            Widgets.EndScrollView();
        }

        private static float viewHeight = 1080f;

        public override void WriteSettings()
        {
            base.WriteSettings();
            ApplySettings();
        }

        /// <summary>Resets every setting (the old whole-screen reset); kept for callers outside the screen.</summary>
        public static void Reset() => ResetFields(AllNames);

        private static readonly string[] AllNames =
        {
            "enableThudder", "enablePalmThumper", "enableSlamLauncher", "enableRepulsorRifle", "enableKickerMine", "enableThumpShell",
            "enablePulseCannon", "enableGravRam", "kineticStrength", "thumpCannonThrows", "thumpCannonForce", "kickerRearms",
            "kickerFuelPerKick", "pulseCapacity", "pulseRechargeSeconds", "lootedOnRaiders", "lootedChancePercent", "foundInRuins",
            "ruinsChancePercent", "foundInComplexes", "kickerHidden", "pulsePowerDraw", "kineticCutsCords",
        };

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RimMandrakeKineticArmsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        /// <summary>Restores the named settings to their shipped values, then re-pushes them into the defs (forces, power draw,
        /// weapon availability) exactly as closing the settings window does.</summary>
        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RimMandrakeKineticArmsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
            ApplySettings();
        }

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): weapon toggles, forces, cords, power draw and
        /// the kicker/pulse numbers are pushed into the defs by ApplySettings when the window closes or read per use (now);
        /// the looted-raider chance is read when a pawn's weapon is generated (next pulse); ruin/complex loot is read when a
        /// site map's loot is generated (new maps only).</summary>
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
