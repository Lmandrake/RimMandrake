using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SCALD_FLOOR_VENT_FIELDS_1 (owner sitting 2026-10-02, Q3 = vent fields on the floor).
    // Generates a vent field on the Scald's floor map: a few RUT_ScaldVent geysers, a ring of vent
    // flora (RM_Glasskelle, RM_Pulsebead) around each, and a few RM_Noohm bubble-sailors riding each
    // vent's bubble line. Everything is resolved by name and skipped when missing, so the step never
    // throws on a partial mod set.
    //
    // Scope: listed only on RM_SeaDiveGenerator_TheScald and refuses any map whose biome is not the
    // Scald (hatch pocket map, RM_TheScald) or the Scald floor biome (RM_SeabedFloor_TheScald). The
    // live RM_SeabedLayer has no per-sea floor map generator yet; when it gets one, list the step there.
    // All counts and radii below are first guesses, not measurements.
    public class GenStep_ScaldVentField : GenStep
    {
        private const int VentMin = 3;
        private const int VentMax = 5;
        private const int VentSpacing = 14;
        private const int ExitKeepOutPad = 3;
        private const int GlasskelleMin = 3;
        private const int GlasskelleMax = 8;
        private const float GlasskelleRadius = 4f;
        private const int PulsebeadMin = 5;
        private const int PulsebeadMax = 12;
        private const float PulsebeadRadius = 5f;
        private const int SailorsMin = 2;
        private const int SailorsMax = 3;

        public override int SeedPart => 7203115;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_MapComponent_ScaldVentForecast.IsScaldFloorMap(map) || !RM_DivingSettings.masterEnabled
                || !RM_DivingSettings.scaldVentFieldsEnabled)
            {
                return;
            }

            ThingDef ventDef = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_ScaldVent");
            if (ventDef == null)
            {
                return;
            }

            List<CellRect> keepOut = ExitKeepOut(map);
            List<IntVec3> vents = PlaceVents(map, ventDef, keepOut);
            ThingDef glass = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Glasskelle");
            ThingDef bead = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Pulsebead");
            PawnKindDef sailor = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Noohm");
            foreach (IntVec3 v in vents)
            {
                if (glass != null)
                {
                    Ring(map, v, glass, Rand.RangeInclusive(GlasskelleMin, GlasskelleMax), GlasskelleRadius, true);
                }
                if (bead != null)
                {
                    Ring(map, v, bead, Rand.RangeInclusive(PulsebeadMin, PulsebeadMax), PulsebeadRadius, false);
                }
                if (sailor != null)
                {
                    Sailors(map, v, sailor, Rand.RangeInclusive(SailorsMin, SailorsMax));
                }
            }
        }

        private static List<CellRect> ExitKeepOut(Map map)
        {
            List<CellRect> rects = new List<CellRect>();
            ThingDef exitDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SeaDiveExit");
            if (exitDef == null)
            {
                return rects;
            }
            foreach (Thing exit in map.listerThings.ThingsOfDef(exitDef))
            {
                rects.Add(exit.OccupiedRect().ExpandedBy(ExitKeepOutPad));
            }
            return rects;
        }

        private static bool FootprintFree(Map map, CellRect rect, List<CellRect> keepOut)
        {
            foreach (CellRect k in keepOut)
            {
                if (k.Overlaps(rect))
                {
                    return false;
                }
            }
            foreach (IntVec3 c in rect)
            {
                if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null)
                {
                    return false;
                }
            }
            return true;
        }

        private static List<IntVec3> PlaceVents(Map map, ThingDef ventDef, List<CellRect> keepOut)
        {
            List<IntVec3> placed = new List<IntVec3>();
            int want = Rand.RangeInclusive(VentMin, VentMax);
            int margin = 6;
            for (int attempt = 0; attempt < 400 && placed.Count < want; attempt++)
            {
                IntVec3 c = new IntVec3(Rand.RangeInclusive(margin, map.Size.x - margin),
                                        0, Rand.RangeInclusive(margin, map.Size.z - margin));
                CellRect rect = GenAdj.OccupiedRect(c, Rot4.North, ventDef.size);
                bool tooClose = false;
                foreach (IntVec3 p in placed)
                {
                    if ((p - c).LengthHorizontal < VentSpacing)
                    {
                        tooClose = true;
                        break;
                    }
                }
                if (tooClose || !FootprintFree(map, rect, keepOut))
                {
                    continue;
                }
                Thing vent = ThingMaker.MakeThing(ventDef);
                GenSpawn.Spawn(vent, c, map);
                placed.Add(c);
            }
            return placed;
        }

        private static void Ring(Map map, IntVec3 center, ThingDef plantDef, int count, float radius, bool mixMature)
        {
            for (int i = 0; i < count; i++)
            {
                for (int tries = 0; tries < 12; tries++)
                {
                    IntVec3 c = center + GenRadial.RadialPattern[Rand.Range(1, GenRadial.NumCellsInRadius(radius))];
                    if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null
                        || c.GetPlant(map) != null || (c - center).LengthHorizontal < 2f)
                    {
                        continue;
                    }
                    Plant p = ThingMaker.MakeThing(plantDef) as Plant;
                    if (p == null)
                    {
                        return;
                    }
                    p.Growth = mixMature && Rand.Chance(0.3f) ? 1f : Rand.Range(0.4f, 0.9f);
                    GenSpawn.Spawn(p, c, map);
                    break;
                }
            }
        }

        private static void Sailors(Map map, IntVec3 center, PawnKindDef kind, int count)
        {
            for (int i = 0; i < count; i++)
            {
                for (int tries = 0; tries < 12; tries++)
                {
                    IntVec3 c = center + GenRadial.RadialPattern[Rand.Range(1, GenRadial.NumCellsInRadius(5f))];
                    if (!c.InBounds(map) || !c.Standable(map) || (c - center).LengthHorizontal < 3f)
                    {
                        continue;
                    }
                    PawnGenerationRequest request = new PawnGenerationRequest(
                        kind,
                        null,
                        PawnGenerationContext.NonPlayer,
                        forceGenerateNewPawn: true,
                        canGeneratePawnRelations: false);
                    Pawn pawn = PawnGenerator.GeneratePawn(request);
                    GenSpawn.Spawn(pawn, c, map);
                    break;
                }
            }
        }
    }
}
