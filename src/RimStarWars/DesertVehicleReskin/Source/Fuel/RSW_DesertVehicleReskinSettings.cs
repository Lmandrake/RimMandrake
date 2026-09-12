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

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Allow any vegetable food to fuel draught carts", ref allowAnyVegetableFuel,
                "On: a chariot, cart or carriage will burn any nutrition-giving vegetable-type "
              + "food (produce, meals, seeds — never meat, animal products or drugs) in addition "
              + "to whatever it already declared. Off: restores Alpha Vehicles - Neolithic's "
              + "original behavior — each vehicle burns only its single declared fuel def "
              + "(Hay, or Kibble for the DogSled).");

            list.End();
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
