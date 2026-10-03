using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.KeelHoist
{
    // HOIST_SHIP_PART_BUILD_1 (design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md §2, RULED 2026-10-01).
    // Every toggle degrades to "the hoist simply does less", never to an error.
    public class KeelHoistSettings : ModSettings
    {
        public static bool masterEnabled = true;
        public static bool requireGravEngine = true;
        public static bool tetherLock = true;
        public static bool colonistsMayRide = true;
        public static bool downedStrangersAndBeasts = true;
        public static bool openLineMeter = true;
        public static float cycleTimeMultiplier = 1f;
        public static float cableRange = 14f;
        public static float restraintHours = 24f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref requireGravEngine, "requireGravEngine", true);
            Scribe_Values.Look(ref tetherLock, "tetherLock", true);
            Scribe_Values.Look(ref colonistsMayRide, "colonistsMayRide", true);
            Scribe_Values.Look(ref downedStrangersAndBeasts, "downedStrangersAndBeasts", true);
            Scribe_Values.Look(ref openLineMeter, "openLineMeter", true);
            Scribe_Values.Look(ref cycleTimeMultiplier, "cycleTimeMultiplier", 1f);
            Scribe_Values.Look(ref cableRange, "cableRange", 14f);
            Scribe_Values.Look(ref restraintHours, "restraintHours", 24f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);
            list.CheckboxLabeled("Keel hoist enabled", ref masterEnabled,
                "Shipped default: ON. Off: a keel hoist cannot lower its cable, take cargo or raise its cradle. "
              + "Anything already in transit still arrives.");
            list.CheckboxLabeled("Only buildable on a gravship", ref requireGravEngine,
                "Shipped default: ON. The hoist must stand on substructure of a map that carries a grav engine. "
              + "Off: buildable anywhere (it still needs research and power).");
            list.CheckboxLabeled("Tether lock (safety rule)", ref tetherLock,
                "Shipped default: ON. The ship refuses to launch while any keel hoist on its substructure has its "
              + "cable down. Off: the ship may launch, and a hoist whose cable was down simply reels in on arrival.");
            list.CheckboxLabeled("Colonists may ride the cradle awake", ref colonistsMayRide,
                "Shipped default: ON (owner ruling 2026-10-01). Off: only cargo, animals, prisoners and the downed ride.");
            list.CheckboxLabeled("Downed strangers and wild beasts can be lowered (arrive captured)", ref downedStrangersAndBeasts,
                "Shipped default: ON. A downed stranger arrives as your prisoner; a downed wild animal arrives in the "
              + "restraint cradle, bound for the hours set below. Off: only what a vanilla portal sends.");
            list.CheckboxLabeled("Open Line meter", ref openLineMeter,
                "Shipped default: ON. A per-map count that rises every hour a cable is down and slowly falls when "
              + "reeled in. It never limits what the hoist carries; sites will read it later.");
            list.Gap();
            list.Label("Cycle time multiplier: " + cycleTimeMultiplier.ToStringPercent());
            cycleTimeMultiplier = list.Slider(cycleTimeMultiplier, 0.25f, 4f);
            list.Label("Cable reach (cells): " + Mathf.RoundToInt(cableRange));
            cableRange = Mathf.Round(list.Slider(cableRange, 4f, 40f));
            list.Label("Restraint cradle holds a wild beast for (hours): " + Mathf.RoundToInt(restraintHours));
            restraintHours = Mathf.Round(list.Slider(restraintHours, 1f, 72f));
            list.End();
        }
    }

    public class KeelHoistMod : Mod
    {
        public const string HarmonyId = "mandrake.rm.keelhoist";
        public static KeelHoistSettings settings;

        public KeelHoistMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<KeelHoistSettings>();
            new Harmony(HarmonyId).PatchAll(Assembly.GetExecutingAssembly());
        }

        public override string SettingsCategory() => "Keel Hoist";

        public override void DoSettingsWindowContents(Rect inRect) => settings.DoWindowContents(inRect);
    }

    [DefOf]
    public static class KeelHoistDefOf
    {
        public static ThingDef RM_KeelHoist;
        public static HediffDef RM_HoistRestraint;

        static KeelHoistDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(KeelHoistDefOf));
        }
    }
}
