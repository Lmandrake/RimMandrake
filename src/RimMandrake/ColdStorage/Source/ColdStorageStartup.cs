using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
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

        /// <summary>Every def with a storage-climate comp, in def order (the Mod Settings unit list).</summary>
        public static IReadOnlyList<ThingDef> ClimateDefs => climateDefs;

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
            StripEmptyFuel();
            ApplyFuelAlternatives();
            ApplyHopperFlags();
            ApplyWallFlags();
            HookReplaceStuff();
            HookWreckedMachinesGrades();
        }

        // Wrecked Machines grade signal (optional; reflection, no reference): def -> boxed MachineGrade, and its static
        // WreckedMachineGrade.RatioFor(MachineGrade), read live so the player's ladder sliders apply at once.
        private static readonly Dictionary<ThingDef, object> gradeOf = new Dictionary<ThingDef, object>();
        private static MethodInfo ratioFor;

        /// <summary>The stasis strength a unit's Wrecked Machines grade gives it (Kludged 0.2, Refurbished 0.75, Original 1
        /// on the default ladder; owner ruling 2026-10-26), or NaN when the def has no grade or the mod is absent.</summary>
        public static float GradeStrength(ThingDef def)
        {
            if (ratioFor == null || def == null || !gradeOf.TryGetValue(def, out object grade))
            {
                return float.NaN;
            }
            try
            {
                return (float)ratioFor.Invoke(null, new[] { grade });
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RimMandrake.ColdStorage] Wrecked Machines grade read failed; units use their def stasis factor: " + e.Message, 0x5C01D57);
                ratioFor = null;
                return float.NaN;
            }
        }

        private static void HookWreckedMachinesGrades()
        {
            if (climateDefs.Count == 0)
            {
                return;
            }
            Type ext = AccessTools.TypeByName("RimMandrake.WreckedMachines.WreckedMachineGrade");
            if (ext == null)
            {
                return;
            }
            FieldInfo gradeField = ext.GetField("grade", BindingFlags.Public | BindingFlags.Instance);
            MethodInfo ratio = ext.GetMethod("RatioFor", BindingFlags.Public | BindingFlags.Static);
            if (gradeField == null || ratio == null || ratio.ReturnType != typeof(float))
            {
                Log.Warning("[RimMandrake.ColdStorage] Wrecked Machines is loaded but its grade API was not found; graded stasis units use their def factor.");
                return;
            }
            foreach (ThingDef d in climateDefs)
            {
                if (d.modExtensions == null)
                {
                    continue;
                }
                foreach (DefModExtension m in d.modExtensions)
                {
                    if (ext.IsInstanceOfType(m))
                    {
                        gradeOf[d] = gradeField.GetValue(m);
                    }
                }
            }
            ratioFor = gradeOf.Count > 0 ? ratio : null;
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

        /// <summary>Wall units take their light and airtight flags from Mod Settings. Building.IsAirtight and the light
        /// grid read the def live, so a change applies to built units as the map next rebuilds rooms and light.</summary>
        public static void ApplyWallFlags()
        {
            foreach (ThingDef d in climateDefs)
            {
                CompProperties_StorageClimate p = d.GetCompProperties<CompProperties_StorageClimate>();
                if (p != null && p.wallMounted && d.building != null)
                {
                    d.blockLight = RM_ColdStorageSettings.wallUnitsBlockLight;
                    d.building.isAirtight = RM_ColdStorageSettings.wallUnitsAirtight;
                }
            }
        }

        /// <summary>A unit whose water or fuel comes only from an optional mod (a MayRequire filter entry) loses its
        /// refuelable comp when that mod is absent, and works as a plain passive unit instead of starving.</summary>
        private static void StripEmptyFuel()
        {
            foreach (ThingDef d in climateDefs)
            {
                CompProperties_Refuelable r = d.GetCompProperties<CompProperties_Refuelable>();
                if (r != null && (r.fuelFilter == null || !r.fuelFilter.AllowedThingDefs.Any()))
                {
                    d.comps.Remove(r);
                    Log.Message("[ColdStorage] " + d.defName + ": no fuel def is loaded, so it runs without one.");
                }
            }
        }

        /// <summary>Units the player set to burn fuel (Mod Settings, applies after a restart): the power comp is swapped
        /// for a refuelable comp. ConnectToPower, HasComp and the Refuelable request group read comps live.</summary>
        private static void ApplyFuelAlternatives()
        {
            foreach (ThingDef d in climateDefs)
            {
                CompProperties_StorageClimate p = d.GetCompProperties<CompProperties_StorageClimate>();
                if (p == null || p.fuelAlternative == null || !RM_ColdStorageSettings.UnitBurnsFuel(d)
                    || d.GetCompProperties<CompProperties_Refuelable>() != null)
                {
                    continue;
                }
                d.comps.RemoveAll(c => c is CompProperties_Power);
                CompProperties_Refuelable r = new CompProperties_Refuelable
                {
                    fuelConsumptionRate = p.fuelAlternativePerDay,
                    fuelCapacity = p.fuelAlternativeCapacity,
                    consumeFuelOnlyWhenUsed = true,
                    fuelFilter = new ThingFilter(),
                    showAllowAutoRefuelToggle = true,
                };
                r.fuelFilter.SetAllow(p.fuelAlternative, true);
                d.comps.Add(r);
                r.ResolveReferences(d);
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
