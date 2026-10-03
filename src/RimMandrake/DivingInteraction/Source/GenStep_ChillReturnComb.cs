using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // CHILL_RETURN_COMB_LANDMARK_1 (owner sitting 2026-10-02, Q4 = Return Comb as scenery and lore
    // only, NO tracing puzzle). Lays one horseshoe of water-ice rock cut by radial black busbars on
    // the Chill floor, with a few inspection studs on the inner rim and two busbar trunks running
    // out of the horseshoe's tips toward the map edge ("machinery continuing beyond both map
    // edges"). Everything is inert: no comps, no map component, no power, no jobs. Studs carry the
    // lore in their descriptions only.
    //
    // Scope: listed on RM_SeaDiveGenerator_TheChill only (the hatch pocket map). The live
    // RM_SeabedLayer has no per-sea floor generator yet; when it gets one, list RM_ChillReturnComb
    // there. Skips quietly when no free site exists. Shapes and counts are first guesses.
    public class GenStep_ChillReturnComb : GenStep
    {
        private const int InnerR = 6;
        private const int OuterR = 9;
        private const float GapHalfAngle = 38f;      // opening of the horseshoe, degrees each side of "open" direction
        private const float BusbarEveryDeg = 22f;
        private const int StudCount = 7;
        private const int TrunkLength = 22;
        private const int Margin = OuterR + 3;
        private const int ExitPad = 4;

        public override int SeedPart => 7203201;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_ChillFireGate.IsChillSeabedMap(map) || !RM_DivingSettings.masterEnabled
                || !RM_DivingSettings.chillReturnCombEnabled)
            {
                return;
            }
            ThingDef iceDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ReturnCombIce");
            ThingDef busDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ReturnCombBusbar");
            ThingDef studDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ReturnCombStud");
            if (iceDef == null || busDef == null || studDef == null)
            {
                return;
            }
            IntVec3 center;
            if (!FindSite(map, out center))
            {
                Log.Warning("[RM] Return Comb: no free site on the Chill floor map; skipped.");
                return;
            }

            float open = Rand.Range(0f, 360f);       // direction the horseshoe opens toward
            float openRad = open * Mathf.Deg2Rad;
            for (int dx = -OuterR; dx <= OuterR; dx++)
            {
                for (int dz = -OuterR; dz <= OuterR; dz++)
                {
                    float r = Mathf.Sqrt(dx * dx + dz * dz);
                    if (r < InnerR || r > OuterR)
                    {
                        continue;
                    }
                    float ang = Mathf.Atan2(dz, dx) * Mathf.Rad2Deg;
                    if (Mathf.Abs(Mathf.DeltaAngle(ang, open)) < GapHalfAngle)
                    {
                        continue;
                    }
                    // Radial black busbars cut the ice at fixed angular spacing (measured from the opening).
                    float fromOpen = Mathf.Repeat(ang - open + 360f, 360f);
                    float nearest = Mathf.Abs(Mathf.DeltaAngle(fromOpen, Mathf.Round(fromOpen / BusbarEveryDeg) * BusbarEveryDeg));
                    float halfWidthDeg = Mathf.Rad2Deg * 0.5f / Mathf.Max(r, 1f);
                    bool bus = nearest <= halfWidthDeg;
                    TrySpawn(map, bus ? busDef : iceDef, center + new IntVec3(dx, 0, dz));
                }
            }

            // Inspection studs on the inner rim, spaced around the arc.
            int placed = 0;
            for (int i = 0; i < StudCount; i++)
            {
                float a = open + (GapHalfAngle + 12f) + i * ((360f - 2f * (GapHalfAngle + 12f)) / Mathf.Max(StudCount - 1, 1));
                float rad = a * Mathf.Deg2Rad;
                IntVec3 c = center + new IntVec3(Mathf.RoundToInt((InnerR - 1) * Mathf.Cos(rad)), 0,
                                                 Mathf.RoundToInt((InnerR - 1) * Mathf.Sin(rad)));
                if (TrySpawn(map, studDef, c))
                {
                    placed++;
                }
            }

            // Trunks: one busbar run out of each tip, along the tip's outward tangent-ish radial line.
            for (int side = -1; side <= 1; side += 2)
            {
                float a = (open + side * GapHalfAngle) * Mathf.Deg2Rad;
                Vector2 dir = new Vector2(Mathf.Cos(a), Mathf.Sin(a));
                for (int k = InnerR; k < OuterR + TrunkLength; k++)
                {
                    IntVec3 c = center + new IntVec3(Mathf.RoundToInt(dir.x * k), 0, Mathf.RoundToInt(dir.y * k));
                    if (!c.InBounds(map))
                    {
                        break;
                    }
                    TrySpawn(map, busDef, c);
                }
            }
            Log.Message("[RM] Return Comb laid at " + center + ", " + placed + " studs.");
        }

        private static bool TrySpawn(Map map, ThingDef def, IntVec3 c)
        {
            if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null)
            {
                return false;
            }
            GenSpawn.Spawn(ThingMaker.MakeThing(def), c, map);
            return true;
        }

        private static bool FindSite(Map map, out IntVec3 site)
        {
            List<CellRect> keepOut = new List<CellRect>();
            ThingDef exitDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SeaDiveExit");
            if (exitDef != null)
            {
                foreach (Thing exit in map.listerThings.ThingsOfDef(exitDef))
                {
                    keepOut.Add(exit.OccupiedRect().ExpandedBy(ExitPad));
                }
            }
            int lo = Margin, hiX = map.Size.x - Margin, hiZ = map.Size.z - Margin;
            for (int attempt = 0; attempt < 400 && hiX > lo && hiZ > lo; attempt++)
            {
                IntVec3 c = new IntVec3(Rand.RangeInclusive(lo, hiX), 0, Rand.RangeInclusive(lo, hiZ));
                CellRect box = CellRect.CenteredOn(c, OuterR);
                bool bad = false;
                foreach (CellRect k in keepOut)
                {
                    if (k.Overlaps(box)) { bad = true; break; }
                }
                if (bad) { continue; }
                int free = 0, total = 0;
                foreach (IntVec3 cell in box)
                {
                    total++;
                    if (cell.InBounds(map) && cell.Standable(map) && cell.GetEdifice(map) == null) { free++; }
                }
                if (free >= total * 0.85f)
                {
                    site = c;
                    return true;
                }
            }
            site = IntVec3.Invalid;
            return false;
        }
    }
}
