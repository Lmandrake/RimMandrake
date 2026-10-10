using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.DesertVehicleReskin
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Desert Vehicle Reskin.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields read
    // from everywhere, Scribe_Values in ExposeData, a DoWindowContents helper
    // called from the Mod subclass).
    //
    // The texture reskin itself is loose PNGs at the donor's texPath — no
    // runtime mechanism, nothing to gate. The one real mechanism is the
    // Harmony fuel-widening in VehicleFuelPatches/VegetableFuel: without it,
    // Alpha Vehicles - Neolithic's draught carts each accept exactly one
    // ThingDef (Hay, or Kibble for DogSled). VegetableFuel widens that to any
    // nutrition-giving vegetable-type food. There is no numeric knob here —
    // fuel is stored as a single scalar float with no per-def value or
    // efficiency multiplier (see VehicleFuelPatches' NOT-PATCHED note on
    // Refunds/EjectFuel) — so the one honest setting is the on/off gate
    // VegetableFuel.Accepts already reads.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_DesertVehicleReskinSettings : ModSettings
    {
        // Default ON: matches shipped VEHICLE_FUEL_ACCEPTS_VEGETABLES_1 behavior.
        public static bool allowAnyVegetableFuel = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref allowAnyVegetableFuel, "allowAnyVegetableFuel", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RSW_DesertVehicleReskinSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RSW_DesertVehicleReskinSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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
                ? " changes take effect the next time the game starts or a save loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 400f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Vegetable fuel for draught carts", RimMandrake.Shared.SettingScope.Now, new[] { "allowAnyVegetableFuel" }))
            {
                list.CheckboxLabeled("Allow any vegetable food to fuel draught carts", ref allowAnyVegetableFuel,
                    "On: a chariot, cart or carriage will burn any nutrition-giving vegetable-type "
                  + "food (produce, meals, seeds - never meat, animal products or drugs) in addition "
                  + "to whatever it already declared. Off: restores Alpha Vehicles - Neolithic's "
                  + "original behavior - each vehicle burns only its single declared fuel def "
                  + "(Hay, or Kibble for the DogSled).");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RSW_DesertVehicleReskinMod : Mod
    {
        public static RSW_DesertVehicleReskinSettings settings;

        public RSW_DesertVehicleReskinMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_DesertVehicleReskinSettings>();
        }

        public override string SettingsCategory()
        {
            return "Desert Vehicle Reskin";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
