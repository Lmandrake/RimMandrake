using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.ColdStorage
{
    /// <summary>
    /// After defs load: index the sealable defs for the rot prefix, set the hopper flag on hopper-capable units from
    /// Mod Settings, and register our units with Replace Stuff when it is loaded (optional; reflection, no reference).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class ColdStorageStartup
    {
        private static readonly List<ThingDef> climateDefs = new List<ThingDef>();

        /// <summary>Indexed by ThingDef.index: the fixed rot multiplier of a preserved item
        /// (ColdStoragePreservedExtension.rotFactor). Null when no def has one other than 1.</summary>
        internal static float[] itemRotFactor;

        public static float ItemRotFactor(Thing thing)
        {
            float[] f = itemRotFactor;
            int i = thing.def.index;
            return f == null || (uint)i >= (uint)f.Length ? 1f : f[i];
        }

        static ColdStorageStartup()
        {
            int max = 0;
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d.index + 1 > max)
                {
                    max = d.index + 1;
                }
            }
            bool[] sealable = new bool[max];
            float[] factors = new float[max];
            bool any = false;
            bool anyFactor = false;
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d.HasComp(typeof(CompSealed)))
                {
                    sealable[d.index] = true;
                    any = true;
                }
                ColdStoragePreservedExtension pres = d.GetModExtension<ColdStoragePreservedExtension>();
                factors[d.index] = pres != null ? pres.rotFactor : 1f;
                if (pres != null && pres.rotFactor != 1f)
                {
                    anyFactor = true;
                }
                if (d.GetCompProperties<CompProperties_StorageClimate>() != null)
                {
                    climateDefs.Add(d);
                }
            }
            CompSealed.sealableByIndex = any ? sealable : null;
            itemRotFactor = anyFactor ? factors : null;
            ApplyHopperFlags();
            HookReplaceStuff();
        }

        /// <summary>Hopper-capable units feed a nutrient paste dispenser while the setting is on. Read live by
        /// StorageGroupUtility.IsHopper, so a settings change applies at once.</summary>
        public static void ApplyHopperFlags()
        {
            foreach (ThingDef d in climateDefs)
            {
                CompProperties_StorageClimate p = d.GetCompProperties<CompProperties_StorageClimate>();
                if (p != null && p.hopperCapable && d.building != null)
                {
                    d.building.isHopper = RM_ColdStorageSettings.unitsActAsHoppers;
                }
            }
        }

        private static bool IsClimateDef(ThingDef d)
        {
            return d != null && d.GetCompProperties<CompProperties_StorageClimate>() != null;
        }

        /// <summary>
        /// Replace Stuff (Memegoddess.ReplaceStuff) lets a player build one storage building over another. Register a
        /// replacement between any two of our units that carries the setpoint and the unit's own temperature across,
        /// as Replace Stuff does for RimFridge. Absent mod, or a changed API: one warning, nothing else.
        /// </summary>
        private static void HookReplaceStuff()
        {
            if (!ModsConfig.IsActive("Memegoddess.ReplaceStuff") || climateDefs.Count == 0)
            {
                return;
            }
            try
            {
                Type host = AccessTools.TypeByName("Replace_Stuff.NewThing.NewThingReplacement");
                Type replacement = host?.GetNestedType("Replacement", BindingFlags.Public | BindingFlags.NonPublic);
                FieldInfo list = host?.GetField("replacements", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static);
                if (replacement == null || list == null)
                {
                    Log.Warning("[RimMandrake.ColdStorage] Replace Stuff is loaded but its replacement list was not found; cold units will not carry their setpoint when replaced.");
                    return;
                }
                Predicate<ThingDef> check = IsClimateDef;
                Action<Thing, Thing> post = CopyClimate;
                object entry = Activator.CreateInstance(replacement, check, check, null, post);
                ((IList)list.GetValue(null)).Add(entry);
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake.ColdStorage] Replace Stuff hook failed: " + e.Message);
            }
        }

        internal static void CopyClimate(Thing newThing, Thing oldThing)
        {
            CompStorageClimate n = (newThing as ThingWithComps)?.GetComp<CompStorageClimate>();
            CompStorageClimate o = (oldThing as ThingWithComps)?.GetComp<CompStorageClimate>();
            if (n == null || o == null)
            {
                return;
            }
            if (!float.IsNaN(o.setpoint))
            {
                n.SetSetpoint(o.setpoint);
            }
            if (!float.IsNaN(o.currentTemp))
            {
                n.currentTemp = o.currentTemp;
            }
        }
    }
}
