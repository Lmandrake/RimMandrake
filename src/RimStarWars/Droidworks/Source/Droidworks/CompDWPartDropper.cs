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

            switch (chassisClass)
            {
                case 0: // Labour
                    return new[] { leg, manip, motiv, servo, cell };
                case 1: // Protocol
                    return new[] { leg, manip, sensor, motiv, servo, cell };
                case 2: // Astromech - domed, no legs or arms
                    return new[] { sensor, motiv, servo, cell };
                case 3: // Battle
                    return new[] { leg, manip, sensor, motiv, servo, cell };
                case 4: // Heavy
                    return new[] { leg, manip, sensor, motiv, servo, cell };
                case 5: // Probe - small hoverer, no legs or arms
                    return new[] { sensor, motiv, servo, cell };
                case 6: // Power (Gonk) - simple hauler, no arms or sensor
                    return new[] { leg, motiv, servo, cell };
                case 7: // Primitive (G2/Junker) - full limb set, claw hands, own tier
                    return new[] { legP, manipP, sensorP, motivP, servoP, cellP };
                default:
                    return new[] { leg, manip, sensor, motiv, servo, cell };
            }
        }
    }
}
