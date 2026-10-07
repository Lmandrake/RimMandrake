using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    public class CompProperties_DWPartDropper : CompProperties
    {
        public CompProperties_DWPartDropper() => compClass = typeof(CompDWPartDropper);
    }

    /// <summary>
    /// DROIDWORKS_FINE_PARTS_1 (packet B4a). On DW_Race_Base, alongside
    /// CompDWHeadDropper - same Notify_Killed hook, same
    /// "the race's own DroidworksExtension sorts LAST" lookup
    /// (CompDroidDetonation's own comment explains why). Rolls each part
    /// type in the dying family's legal set independently at DropChance
    /// (never guaranteed, "never all of them" - section 1.3), quality via
    /// QualityUtility.GenerateQualityTraderItem (the vanilla found-loot
    /// roll, not a hand-built curve).
    ///
    /// The per-family legal-set table is FOUNDRY's own call (nothing in the
    /// design doc enumerates it) - built from each family's real shape:
    /// Astromech/Probe (domed/limbless donor races) never drop Leg or
    /// Manipulator; Power (Gonk) never drops Manipulator or Sensor.
    /// </summary>
    public class CompDWPartDropper : ThingComp
    {
        /// The shipped default. The live value is
        /// RSW_DroidworksSettings.partDropChance, which this seeds.
        public const float DropChance = 0.6f;

        public override void Notify_Killed(Map prevMap, DamageInfo? dinfo = null)
        {
            if (prevMap == null) return;
            // MOD_OPTIONS_RETROFIT_1: off = no salvage parts drop.
            if (!RSW_DroidworksSettings.partDrop) return;
            Pawn pawn = parent as Pawn;
            if (pawn == null) return;
            DroidworksExtension ext = pawn.def.modExtensions?.OfType<DroidworksExtension>().LastOrDefault();
            ThingDef[] legalSet = LegalSetFor(ext?.chassisClass ?? 0);

            foreach (ThingDef partDef in legalSet)
            {
                if (partDef == null) continue;
                if (!Rand.Chance(RSW_DroidworksSettings.partDropChance)) continue;

                Thing part = ThingMaker.MakeThing(partDef);
                CompQuality cq = part.TryGetComp<CompQuality>();
                if (cq != null)
                    cq.SetQuality(QualityUtility.GenerateQualityTraderItem(), ArtGenerationContext.Outsider);
                GenPlace.TryPlaceThing(part, pawn.PositionHeld, prevMap, ThingPlaceMode.Near);
            }
        }

        // chassisClass ints per DroidworksExtension's own comment: 0 labour,
        // 1 protocol, 2 astromech, 3 battle, 4 heavy, 5 probe, 6 power,
        // 7 primitive (DROIDWORKS_PRIMITIVE_TIER_1, packet B9).
        private static ThingDef[] LegalSetFor(int chassisClass)
        {
            ThingDef leg = DroidworksDefOf.RSW_DW_Part_Leg;
            ThingDef manip = DroidworksDefOf.RSW_DW_Part_Manipulator;
            ThingDef sensor = DroidworksDefOf.RSW_DW_Part_Sensor;
            ThingDef motiv = DroidworksDefOf.RSW_DW_Part_Motivator;
            ThingDef servo = DroidworksDefOf.RSW_DW_Part_Servo;
            ThingDef cell = DroidworksDefOf.RSW_DW_Part_PowerCell;

            // Primitive (7) drops its OWN tier of salvage, not the fine
            // parts above - a Jawa/Junker-built chassis sheds Jawa-built
            // junk, never donor-grade salvage (Parts_Droidworks_Primitive.xml).
            ThingDef legP = DroidworksDefOf.RSW_DW_Part_Leg_Primitive;
            ThingDef manipP = DroidworksDefOf.RSW_DW_Part_Manipulator_Primitive;
            ThingDef sensorP = DroidworksDefOf.RSW_DW_Part_Sensor_Primitive;
            ThingDef motivP = DroidworksDefOf.RSW_DW_Part_Motivator_Primitive;
            ThingDef servoP = DroidworksDefOf.RSW_DW_Part_Servo_Primitive;
            ThingDef cellP = DroidworksDefOf.RSW_DW_Part_PowerCell_Primitive;

            // The slot table (which chassis sheds which parts, in drop order) is DroidworksKernel.LegalParts; this
            // only maps a slot onto the fine or the primitive def.
            bool primitive = DroidworksKernel.UsesPrimitiveParts(chassisClass);
            DroidPartSlot slots = DroidworksKernel.LegalParts(chassisClass);
            var set = new System.Collections.Generic.List<ThingDef>();
            if ((slots & DroidPartSlot.Leg) != 0) set.Add(primitive ? legP : leg);
            if ((slots & DroidPartSlot.Manipulator) != 0) set.Add(primitive ? manipP : manip);
            if ((slots & DroidPartSlot.Sensor) != 0) set.Add(primitive ? sensorP : sensor);
            if ((slots & DroidPartSlot.Motivator) != 0) set.Add(primitive ? motivP : motiv);
            if ((slots & DroidPartSlot.Servo) != 0) set.Add(primitive ? servoP : servo);
            if ((slots & DroidPartSlot.PowerCell) != 0) set.Add(primitive ? cellP : cell);
            return set.ToArray();
        }
    }
}
