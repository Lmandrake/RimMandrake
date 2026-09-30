using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Wasteland
{
    /// <summary>
    /// WASTELAND_MECHANICS_BUILD_1 §3 — the ambient-dose comp family (Smolderback;
    /// the Middenshell's aura reuses it at larger radius/strength). A creature that
    /// carries it doses the pawns around it with vanilla ToxicBuildup through
    /// ToxicUtility.DoPawnToxicDamage — the Biotech-era toxic mechanism, so
    /// ToxicResistance and ToxicEnvironmentResistance both apply (ruling
    /// 2026-09-28: the dose rides the pollution mechanism, no parallel radiation
    /// system). The dose is AMBIENT, never an attack: no damage, no aggression.
    ///
    /// Indoors (the source's room does not use outdoor temperature) it doses its
    /// whole ROOM — "heats a shelter all winter, doses it the whole time".
    /// Outdoors it doses within <c>radius</c>, strongest at the body and falling
    /// to <c>edgeFactor</c> at the rim. Its own kind is dosed too (they cook each
    /// other — the solitary's reason); only the source itself is skipped.
    ///
    /// Creature-level, not a map-wide roll: a tamed Smolderback carried to another
    /// biome keeps dosing its room, which is the trade the description promises.
    /// </summary>
    public class RM_CompProperties_AmbientDose : CompProperties
    {
        public float radius = 6f;

        /// <summary>extraFactor on vanilla's per-check toxic dose (1 = toxic-fallout rate),
        /// at the body / anywhere inside the shared room.</summary>
        public float toxicFactor = 0.5f;

        /// <summary>Multiplier reached at the rim of <c>radius</c> outdoors (1 = flat).</summary>
        public float edgeFactor = 1f;

        /// <summary>When the source is inside a room, dose that room instead of a radius.</summary>
        public bool doseRoomWhenIndoors = true;

        /// <summary>Ticks between doses. Default = vanilla ToxicUtility.CheckInterval.</summary>
        public int checkIntervalTicks = ToxicUtility.CheckInterval;

        public RM_CompProperties_AmbientDose()
        {
            compClass = typeof(RM_CompAmbientDose);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (radius <= 0f)
            {
                yield return "RM_CompProperties_AmbientDose.radius must be > 0.";
            }
            if (toxicFactor < 0f || edgeFactor < 0f)
            {
                yield return "RM_CompProperties_AmbientDose factors must be >= 0.";
            }
            if (checkIntervalTicks < 60)
            {
                yield return "RM_CompProperties_AmbientDose.checkIntervalTicks must be >= 60.";
            }
        }
    }

    public class RM_CompAmbientDose : ThingComp
    {
        public RM_CompProperties_AmbientDose Props => (RM_CompProperties_AmbientDose)props;

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.IsHashIntervalTick(Props.checkIntervalTicks))
            {
                return;
            }
            if (!RM_WastelandSettings.wastelandEnabled || !RM_WastelandSettings.ambientDoseEnabled)
            {
                return;
            }
            DoDose();
        }

        /// <summary>One dose pass. Returns how many pawns were dosed (debug/state read).</summary>
        public int DoDose()
        {
            if (!parent.Spawned)
            {
                return 0;
            }
            Pawn self = parent as Pawn;
            if (self != null && self.Dead)
            {
                return 0;
            }
            float mult = RM_WastelandSettings.ambientDoseMultiplier;
            if (mult <= 0f || Props.toxicFactor <= 0f)
            {
                return 0;
            }

            Map map = parent.Map;
            IntVec3 pos = parent.Position;
            Room room = Props.doseRoomWhenIndoors ? pos.GetRoom(map) : null;
            bool indoors = room != null && !room.UsesOutdoorTemperature;
            float r = Props.radius;
            float r2 = r * r;

            int dosed = 0;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == parent || p.Dead)
                {
                    continue;
                }
                float factor = Props.toxicFactor;
                if (indoors)
                {
                    if (p.GetRoom() != room)
                    {
                        continue;
                    }
                }
                else
                {
                    float d2 = (p.Position - pos).LengthHorizontalSquared;
                    if (d2 > r2)
                    {
                        continue;
                    }
                    factor *= Mathf.Lerp(1f, Props.edgeFactor, Mathf.Sqrt(d2) / r);
                }
                ToxicUtility.DoPawnToxicDamage(p, factor * mult);
                dosed++;
            }
            return dosed;
        }
    }

    /// <summary>
    /// WASTELAND_MECHANICS_BUILD_1 §3 — the living furnace's heat. Vanilla
    /// CompHeatPusher (used via <c>compClass</c> on a CompProperties_HeatPusher),
    /// gated by the Mod Settings toggle and silenced on a dead body.
    /// </summary>
    public class RM_CompRadiothermalHeat : CompHeatPusher
    {
        public override bool ShouldPushHeatNow
        {
            get
            {
                if (!RM_WastelandSettings.wastelandEnabled || !RM_WastelandSettings.radiothermalHeatEnabled)
                {
                    return false;
                }
                Pawn pawn = parent as Pawn;
                if (pawn != null && pawn.Dead)
                {
                    return false;
                }
                return base.ShouldPushHeatNow;
            }
        }
    }
}
