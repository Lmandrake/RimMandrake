using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Scarlands
{
    // WARSCAR_MARK_TRADE_BUILD_1 (WARSCAR_SNAP_MARK_1 spec 3, 4, 5, 7; design
    // warscar_turn3_development_2026-09-30.md section 2.6). The franchise-free mark: a pawn on a
    // Warscar map accrues RM_WarscarMark every hour (0.0125 by default = +0.3/day gross, against
    // the hediff's own -0.1/day fade, so +0.2/day net on the map); once it has passed 0.5 it never
    // fades below 0.25 (about eight days arms the floor). The pay is the stages' statOffsets
    // (hacking, mechanoid butchery, smelting). Done here in Warscar's own C#, not through
    // EnvironmentalHazards' weather condition, because mandrake.rm.warscar does not depend on that
    // mod. The RUT twin (RUT_ScarlandsMark) is frozen: this lock skips a pawn carrying any other
    // hediff tagged RM_WarscarMarkFamily, or the twin itself; the twin's lock now skips ours (SC-1: skipHediffIfCarryingOtherTagged);
    // no stacking either way.

    public class RM_HediffCompProperties_WarscarMarkFloor : HediffCompProperties
    {
        public float floorTriggerThreshold = 0.5f;
        public float floorValue = 0.25f;

        public RM_HediffCompProperties_WarscarMarkFloor()
        {
            compClass = typeof(RM_HediffComp_WarscarMarkFloor);
        }
    }

    public class RM_HediffComp_WarscarMarkFloor : HediffComp
    {
        public bool armed;

        private RM_HediffCompProperties_WarscarMarkFloor Props => (RM_HediffCompProperties_WarscarMarkFloor)props;

        public override void CompPostTick(ref float severityAdjustment)
        {
            if (!RM_WarscarSettings.markFloorEnabled)
            {
                return;
            }
            float next = parent.Severity + severityAdjustment;
            if (!armed && next >= Props.floorTriggerThreshold)
            {
                armed = true;
            }
            if (armed && next < Props.floorValue)
            {
                severityAdjustment = Props.floorValue - parent.Severity;
            }
        }

        public override void CompExposeData()
        {
            Scribe_Values.Look(ref armed, "rmWarscarMarkFloorArmed", false);
        }

        public override string CompDebugString()
        {
            return "floor armed: " + armed;
        }
    }

    public static class RM_WarscarMark
    {
        public const string FamilyTag = "RM_WarscarMarkFamily";
        public const int IntervalTicks = 2500;

        private static HediffDef markDef;
        private static BiomeDef warscar;

        public static HediffDef MarkDef => markDef ?? (markDef = DefDatabase<HediffDef>.GetNamedSilentFail("RM_WarscarMark"));
        public static BiomeDef Warscar => warscar ?? (warscar = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Warscar"));

        public static bool Marks(Pawn p)
        {
            return p != null && !p.Dead && p.Spawned && p.RaceProps != null && p.RaceProps.Humanlike
                && !p.RaceProps.IsMechanoid;
        }

        /// <summary>No stacking (ruled): a pawn carrying the other mark of the family is skipped.</summary>
        public static bool CarriesOtherMark(Pawn p)
        {
            List<Hediff> hs = p.health?.hediffSet?.hediffs;
            if (hs == null)
            {
                return false;
            }
            for (int i = 0; i < hs.Count; i++)
            {
                HediffDef d = hs[i].def;
                if (d == MarkDef)
                {
                    continue;
                }
                if (d.defName == "RUT_ScarlandsMark" || (d.tags != null && d.tags.Contains(FamilyTag)))
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>One hour's accrual on one pawn. Returns true when it was marked.</summary>
        public static bool Accrue(Pawn p)
        {
            if (!RM_WarscarSettings.markEnabled || MarkDef == null || !Marks(p) || CarriesOtherMark(p))
            {
                return false;
            }
            float amount = RM_WarscarSettings.markAccrualPerDay * IntervalTicks / 60000f;
            if (amount <= 0f)
            {
                return false;
            }
            HealthUtility.AdjustSeverity(p, MarkDef, amount);
            return true;
        }

        /// <summary>Bridge proof (jawa/static_call): <paramref name="hours"/> hourly accruals on the
        /// first free colonist of the map, with no fade in between (the fade is the vanilla
        /// SeverityPerDay comp). "PAWN Human123 hours 24 severity 0.30 stage mild mark floor armed=False
        /// | HackingSpeed 1.15".</summary>
        public static string ProofAccrue(Map map, int hours)
        {
            if (map == null)
            {
                return "REFUSED: no map";
            }
            Pawn p = null;
            foreach (Pawn c in map.mapPawns.FreeColonistsSpawned)
            {
                p = c;
                break;
            }
            if (p == null)
            {
                return "REFUSED: no free colonist on the map";
            }
            int marked = 0;
            for (int i = 0; i < hours; i++)
            {
                if (Accrue(p))
                {
                    marked++;
                }
            }
            Hediff h = MarkDef == null ? null : p.health.hediffSet.GetFirstHediffOfDef(MarkDef);
            if (h == null)
            {
                return "PAWN " + p.ThingID + " hours " + hours + " marked " + marked + " | NO MARK";
            }
            RM_HediffComp_WarscarMarkFloor floor = h.TryGetComp<RM_HediffComp_WarscarMarkFloor>();
            if (floor != null && h.Severity >= 0.5f && RM_WarscarSettings.markFloorEnabled)
            {
                floor.armed = true;   // CompPostTick arms it on the next tick; the proof reads it now
            }
            return "PAWN " + p.ThingID + " hours " + hours + " marked " + marked
                + " severity " + h.Severity.ToString("0.###") + " stage " + (h.CurStage?.label ?? "-")
                + " floor armed=" + (floor != null && floor.armed)
                + " | HackingSpeed " + p.GetStatValue(StatDefOf.HackingSpeed).ToString("0.##")
                + " | SmeltingSpeed " + p.GetStatValue(DefDatabase<StatDef>.GetNamed("SmeltingSpeed")).ToString("0.##");
        }
    }

    /// <summary>The lock: hourly accrual on every humanlike on a Warscar map, roofed or not
    /// ("every colonist who walks the Warscar"; a roof does not un-mark you).</summary>
    public class RM_MapComponent_WarscarMark : MapComponent
    {
        public RM_MapComponent_WarscarMark(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (!RM_WarscarSettings.markEnabled || Find.TickManager.TicksGame % RM_WarscarMark.IntervalTicks != 37)
            {
                return;
            }
            if (map.Biome == null || map.Biome != RM_WarscarMark.Warscar)
            {
                return;
            }
            List<Pawn> pawns = map.mapPawns.AllHumanlikeSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                RM_WarscarMark.Accrue(pawns[i]);
            }
        }
    }

    /// <summary>Trade bonuses off: strip the mark stages' statOffsets at startup (restart to apply).</summary>
    [StaticConstructorOnStartup]
    public static class RM_WarscarMarkStartup
    {
        static RM_WarscarMarkStartup()
        {
            if (RM_WarscarSettings.markTradeBonusesEnabled || RM_WarscarMark.MarkDef?.stages == null)
            {
                return;
            }
            foreach (HediffStage s in RM_WarscarMark.MarkDef.stages)
            {
                s.statOffsets = null;
            }
        }
    }
}
