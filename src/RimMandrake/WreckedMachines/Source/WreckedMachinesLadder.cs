using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.WreckedMachines
{
    // ════════════════════════════════════════════════════════════════════
    // THE GRADE LADDER (owner ruling 2026-09-15, ruling 1).
    //
    //   Wrecked      0.001  inert; a dying power source flickers like a faint LED
    //   Kludged      0.2    works, badly, visibly bodged
    //   Refurbished  0.75   the ceiling a player normally reaches
    //   Original     1.0    the unmodified donor machine; reachable only when
    //                       the "full restoration" Mod Setting is on (default OFF)
    //
    // Nothing equals or exceeds the original (ruling 2). Every ratio is a
    // player-tunable default, applied here to the def from the ORIGINAL def's
    // own number, so the ladder cannot drift from its donor.
    //
    // Stepping is vanilla `replaceTags`: build the next grade over the old
    // footprint. PlaceWorker_BuildOverLowerGrade below makes the ladder the
    // only way in — a Kludged or Refurbished machine must be built over a
    // lower grade of the same line, never on a clean floor.
    // ════════════════════════════════════════════════════════════════════
    public enum MachineGrade
    {
        Wrecked = 0,
        Kludged = 1,
        Refurbished = 2,
        Original = 3,
    }

    public class WreckedMachineGrade : DefModExtension
    {
        public MachineGrade grade = MachineGrade.Wrecked;

        // The ladder this def belongs to; equals the shared replaceTag.
        public string line;

        // The donor def every ratio is taken from. Null for the Original rung
        // itself, and for lines whose capability ratio is not applied
        // (factories: no per-class value has been set for them).
        public ThingDef original;

        // Projects a soothing psychic field (ThoughtWorker_SalvagedEmanatorSoothe).
        public bool emanates;

        public static float RatioFor(MachineGrade grade)
        {
            switch (grade)
            {
                case MachineGrade.Wrecked: return WreckedMachinesSettings.wreckedRatio;
                case MachineGrade.Kludged: return WreckedMachinesSettings.kludgedRatio;
                case MachineGrade.Refurbished: return WreckedMachinesSettings.refurbishedRatio;
                default: return 1f;
            }
        }
    }

    // A Kludged / Refurbished / Original machine is placed only over a lower
    // grade of its own line. Reinstalling an already-built machine (the
    // `thing` argument is set) is always allowed: a relic moved onto a ship is
    // still the same relic.
    public class PlaceWorker_BuildOverLowerGrade : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            if (!WreckedMachinesSettings.requireLowerGradeUnderneath || thing != null)
                return true;
            WreckedMachineGrade ext = checkingDef.GetModExtension<WreckedMachineGrade>();
            if (ext == null || ext.grade == MachineGrade.Wrecked)
                return true;

            List<Thing> things = loc.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                Thing t = things[i];
                if (t == thingToIgnore || t.Position != loc) continue;
                ThingDef d = t.def;
                if (t is Blueprint || t is Frame)
                    d = t.def.entityDefToBuild as ThingDef;
                WreckedMachineGrade other = d?.GetModExtension<WreckedMachineGrade>();
                if (other != null && other.line == ext.line && other.grade < ext.grade)
                    return true;
            }
            return new AcceptanceReport("Must be built over a lower grade of the same machine, in the same place.");
        }
    }

    // The vanilla emanator's ThoughtWorker reads ThingDefOf.PsychicEmanator
    // only (RimSage, ThoughtWorker_PsychicEmanatorSoothe), so a salvaged
    // emanator needs its own worker. Stage 0 = Kludged, stage 1 = Refurbished;
    // the strongest powered emanator within range wins. Wrecked is inert.
    public class ThoughtWorker_SalvagedEmanatorSoothe : ThoughtWorker
    {
        private const float Radius = 15f;

        private static List<ThingDef> emanatorDefs;

        private static List<ThingDef> EmanatorDefs
        {
            get
            {
                if (emanatorDefs == null)
                {
                    emanatorDefs = new List<ThingDef>();
                    foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
                    {
                        WreckedMachineGrade ext = d.GetModExtension<WreckedMachineGrade>();
                        if (ext != null && ext.emanates && ext.grade != MachineGrade.Wrecked)
                            emanatorDefs.Add(d);
                    }
                }
                return emanatorDefs;
            }
        }

        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            if (!p.Spawned || !WreckedMachinesSettings.enableSalvagedEmanators)
                return false;
            int best = -1;
            List<ThingDef> defs = EmanatorDefs;
            for (int d = 0; d < defs.Count; d++)
            {
                int stage = Mathf.Min((int)defs[d].GetModExtension<WreckedMachineGrade>().grade - 1, def.stages.Count - 1);
                if (stage <= best) continue;
                List<Thing> list = p.Map.listerThings.ThingsOfDef(defs[d]);
                for (int i = 0; i < list.Count; i++)
                {
                    CompPowerTrader power = list[i].TryGetComp<CompPowerTrader>();
                    if ((power == null || power.PowerOn) && p.Position.InHorDistOf(list[i].Position, Radius))
                    {
                        best = stage;
                        break;
                    }
                }
            }
            return best >= 0 ? ThoughtState.ActiveAtStage(best) : ThoughtState.Inactive;
        }
    }

    // Applies the ratio settings to the ladder defs. Called from
    // WreckedMachinesPatcher.Apply(), so it re-runs whenever settings close.
    public static class LadderPatcher
    {
        private static readonly FieldInfo BasePowerField =
            typeof(CompProperties_Power).GetField("basePowerConsumption", BindingFlags.Instance | BindingFlags.NonPublic);

        private static readonly ThoughtDef SalvagedSoothe =
            DefDatabase<ThoughtDef>.GetNamedSilentFail("RM_WM_SalvagedEmanatorSoothe");

        private static readonly ThoughtDef VanillaSoothe =
            DefDatabase<ThoughtDef>.GetNamedSilentFail("PsychicEmanatorSoothe");

        // Designation category of each Original-grade def as shipped, so the
        // full-restoration toggle can restore it.
        private static readonly Dictionary<ThingDef, DesignationCategoryDef> OriginalCategories = Capture();

        private static Dictionary<ThingDef, DesignationCategoryDef> Capture()
        {
            var map = new Dictionary<ThingDef, DesignationCategoryDef>();
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                WreckedMachineGrade ext = d.GetModExtension<WreckedMachineGrade>();
                if (ext != null && ext.grade == MachineGrade.Original)
                    map[d] = d.designationCategory;
            }
            return map;
        }

        public static void Apply()
        {
            foreach (KeyValuePair<ThingDef, DesignationCategoryDef> kv in OriginalCategories)
                kv.Key.designationCategory = WreckedMachinesSettings.allowFullRestoration ? kv.Value : null;

            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                WreckedMachineGrade ext = d.GetModExtension<WreckedMachineGrade>();
                if (ext == null || ext.original == null || ext.grade == MachineGrade.Original) continue;
                ScalePowerOutput(d, ext.original, WreckedMachineGrade.RatioFor(ext.grade));
            }

            if (SalvagedSoothe != null && VanillaSoothe != null && VanillaSoothe.stages.Count > 0)
            {
                float baseMood = VanillaSoothe.stages[0].baseMoodEffect;
                if (SalvagedSoothe.stages.Count > 0)
                    SalvagedSoothe.stages[0].baseMoodEffect = baseMood * WreckedMachinesSettings.kludgedRatio;
                if (SalvagedSoothe.stages.Count > 1)
                    SalvagedSoothe.stages[1].baseMoodEffect = baseMood * WreckedMachinesSettings.refurbishedRatio;
            }
        }

        // Only power PRODUCERS scale (a negative basePowerConsumption): a
        // salvaged generator yields its ratio of the original's output. A
        // consumer keeps its own draw, because a bodge is not more efficient.
        private static void ScalePowerOutput(ThingDef def, ThingDef original, float ratio)
        {
            if (BasePowerField == null) return;
            CompProperties_Power mine = def.GetCompProperties<CompProperties_Power>();
            CompProperties_Power theirs = original.GetCompProperties<CompProperties_Power>();
            if (mine == null || theirs == null) return;
            float originalBase = (float)BasePowerField.GetValue(theirs);
            if (originalBase >= 0f) return;
            BasePowerField.SetValue(mine, originalBase * ratio);
        }
    }
}
