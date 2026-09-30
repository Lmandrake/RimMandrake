using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.Wasteland
{
    /// <summary>
    /// Marks a ThingDef as WASTE: the Middenshell is lured by stockpiles holding it and
    /// its tentacle prefers it (WASTELAND_GPT_ENRICHMENT_1 §2). Vanilla's Biotech
    /// Wastepack counts without a marker.
    /// </summary>
    public class RM_WasteMarkerExtension : DefModExtension
    {
    }

    public static class RM_WasteUtility
    {
        private static ThingDef wastepack;
        private static bool wastepackLooked;

        public static bool IsWaste(Thing t)
        {
            if (t == null || t.def == null)
            {
                return false;
            }
            if (!wastepackLooked)
            {
                wastepack = DefDatabase<ThingDef>.GetNamedSilentFail("Wastepack");
                wastepackLooked = true;
            }
            return (wastepack != null && t.def == wastepack) || t.def.HasModExtension<RM_WasteMarkerExtension>();
        }
    }

    /// <summary>
    /// WASTELAND_GPT_ENRICHMENT_1 §2 — the Middenshell Procession's omen. Hours before
    /// the body arrives, the crust trembles (a low rumble, a small camera shake, dust
    /// thrown up across the map) and loose metal creeps toward the one edge it will
    /// arrive by. At the arrival tick the 20-wide body crawls in there and crosses the
    /// map toward the opposite edge (<see cref="Building_Middenshell.BeginProcession"/>).
    /// </summary>
    public class RM_MapComponent_MiddenshellProcession : MapComponent
    {
        private const int OmenIntervalMin = 600;
        private const int OmenIntervalMax = 1400;
        private const int MetalCreepPerOmen = 6;

        private int arrivalTick = -1;
        private IntVec3 arrivalCenter = IntVec3.Invalid;
        private int arrivalHeadingRot = -1;
        private int nextOmenTick = -1;

        public RM_MapComponent_MiddenshellProcession(Map map) : base(map) { }

        public bool Pending => arrivalTick >= 0;
        public int ArrivalTick => arrivalTick;
        /// <summary>The edge it arrives from (the loose metal points this way).</summary>
        public Rot4 ArrivalEdge => new Rot4(Mathf.Max(0, arrivalHeadingRot)).Opposite;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref arrivalTick, "arrivalTick", -1);
            Scribe_Values.Look(ref arrivalCenter, "arrivalCenter", IntVec3.Invalid);
            Scribe_Values.Look(ref arrivalHeadingRot, "arrivalHeadingRot", -1);
            Scribe_Values.Look(ref nextOmenTick, "nextOmenTick", -1);
        }

        /// <summary>Schedule an arrival at <paramref name="center"/> facing <paramref name="heading"/>.</summary>
        public void Schedule(IntVec3 center, Rot4 heading)
        {
            int now = Find.TickManager.TicksGame;
            arrivalTick = now + Mathf.Max(1, RM_WastelandSettings.middenshellOmenHours) * GenDate.TicksPerHour;
            arrivalCenter = center;
            arrivalHeadingRot = heading.AsInt;
            nextOmenTick = now + 60;
        }

        public string OmenLetterSuffix()
        {
            return "The crust is already trembling. Loose metal across the map is creeping toward the "
                 + Building_Middenshell.EdgeName(ArrivalEdge) + " edge: that is where it will come from, in about "
                 + Mathf.Max(1, RM_WastelandSettings.middenshellOmenHours) + " hours. It will cross the map and "
                 + "leave by the far edge. A stockpile holding waste can draw it off its line.";
        }

        public override void MapComponentTick()
        {
            if (arrivalTick < 0)
            {
                return;
            }
            if (!RM_WastelandSettings.wastelandEnabled || !RM_WastelandSettings.middenshellEnabled)
            {
                arrivalTick = -1; // switched off mid-omen: it never comes
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (now >= arrivalTick)
            {
                Arrive();
                return;
            }
            if (now >= nextOmenTick)
            {
                DoOmen();
                nextOmenTick = now + Rand.Range(OmenIntervalMin, OmenIntervalMax);
            }
        }

        /// <summary>One tremor. Public so a debug action / state read can drive it.</summary>
        public int DoOmen()
        {
            if (map == Find.CurrentMap)
            {
                DefDatabase<SoundDef>.GetNamedSilentFail("RM_Middenshell_Tremor")?.PlayOneShotOnCamera(map);
                Find.CameraDriver.shaker.DoShake(0.6f);
                for (int i = 0; i < 12; i++)
                {
                    IntVec3 c = CellFinder.RandomCell(map);
                    if (!c.Fogged(map))
                    {
                        FleckMaker.ThrowDustPuffThick(c.ToVector3Shifted(), map, Rand.Range(1.2f, 2.2f), new Color(0.6f, 0.58f, 0.52f));
                    }
                }
            }
            return CreepMetal();
        }

        /// <summary>Loose metal (not in storage) shuffles one cell toward the arrival edge.</summary>
        private int CreepMetal()
        {
            Rot4 edge = ArrivalEdge;
            List<Thing> loose = new List<Thing>();
            List<Thing> haulables = map.listerThings.ThingsInGroup(ThingRequestGroup.HaulableEver);
            for (int i = 0; i < haulables.Count; i++)
            {
                Thing t = haulables[i];
                if (t.Spawned && !t.IsInAnyStorage() && IsLooseMetal(t) && t.Position.GetFirstPawn(map) == null)
                {
                    loose.Add(t);
                }
            }
            int moved = 0;
            loose.Shuffle();
            for (int i = 0; i < loose.Count && moved < MetalCreepPerOmen; i++)
            {
                Thing t = loose[i];
                IntVec3 dest = t.Position + edge.FacingCell;
                if (!dest.InBounds(map) || !dest.Standable(map) || dest.GetFirstItem(map) != null)
                {
                    continue;
                }
                IntVec3 from = t.Position;
                t.DeSpawn();
                GenSpawn.Spawn(t, dest, map);
                if (map == Find.CurrentMap)
                {
                    FleckMaker.ThrowDustPuff(from, map, 0.6f);
                }
                moved++;
            }
            return moved;
        }

        public static bool IsLooseMetal(Thing t)
        {
            if (t.def.category != ThingCategory.Item)
            {
                return false;
            }
            if (t.def.IsMetal)
            {
                return true;
            }
            return t.Stuff?.stuffProps?.categories != null && t.Stuff.stuffProps.categories.Contains(StuffCategoryDefOf.Metallic);
        }

        /// <summary>The body arrives. Public so a debug action can skip the omen.</summary>
        public Building_Middenshell Arrive()
        {
            ThingDef shellDef = RM_IncidentWorker_MiddenshellArrives.MiddenshellDef;
            IntVec3 center = arrivalCenter;
            Rot4 heading = new Rot4(Mathf.Max(0, arrivalHeadingRot));
            arrivalTick = -1;
            if (shellDef == null || Building_Middenshell.AnyOnMap(map, shellDef))
            {
                return null;
            }
            CellRect rect = GenAdj.OccupiedRect(center, heading, shellDef.Size);
            if (!Building_Middenshell.RectPassableForBody(rect, map, CellRect.Empty)
                && !Building_Middenshell.TryFindEdgeSpawn(map, shellDef, out center, out heading))
            {
                Messages.Message("The trembling stops. Whatever was coming found no way in.", MessageTypeDefOf.NeutralEvent);
                return null;
            }
            Building_Middenshell shell = Building_Middenshell.SpawnAt(map, shellDef, center, heading);
            if (shell == null)
            {
                return null;
            }
            shell.BeginProcession(heading);
            Find.LetterStack.ReceiveLetter("Middenshell procession",
                "The middenshell has arrived at the " + Building_Middenshell.EdgeName(heading.Opposite)
              + " edge and is crossing toward the " + Building_Middenshell.EdgeName(heading)
              + ". It grinds flat whatever lies in its path and leaves a trail of pressed ground, hot "
              + "footprints, shell flakes and the odd small bezoar. Select it to see its route. A "
              + "stockpile holding waste nearby will draw it aside.",
                LetterDefOf.ThreatSmall, new LookTargets(shell));
            return shell;
        }
    }
}
