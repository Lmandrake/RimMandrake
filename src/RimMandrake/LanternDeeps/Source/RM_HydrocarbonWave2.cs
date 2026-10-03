using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.LanternDeeps
{
    // ════════════════════════════════════════════════════════════════════
    // LANTERNDEEPS_HYDROCARBON_WAVE2_BUILD_1 (split from LANTERNDEEPS_HYDROCARBON_FAUNA_BUILD_1): slick,
    // blinker, knocker. Concepts: design/Jawa/worldbuilding/biomes/rosters/
    // lantern_deeps_repopulation_proposals.md §5, §8, §11 (owner: "Yes all 7 and ensure hydrocarbon").
    //
    //  RM_CompTrailFilth   the slick sweats pentane: each cell it leaves gets Filth_Fuel, which is
    //                      vanilla flammable filth, so a spark runs the corridor like a fuse.
    //  RM_CompFlashOnHurt  the blinker, hurt, flashes: a short-lived radius-20 glower thing (the ruled
    //                      light-draw answers it with no extra code) and RM_BlinkerDazzled on every
    //                      other pawn within 8 that can see it.
    //  RM_CompKnocker      the knocker hears rock before it fails: when the Deep's collapse warning
    //                      (RM_MapComponent_DeepCollapse) holds cells within 15 it drums, flees the
    //                      cells, and a tame one names the danger. A tame knocker on the map also
    //                      lengthens every warning window (knockerWarningFactor).
    // ════════════════════════════════════════════════════════════════════

    public class RM_CompProperties_TrailFilth : CompProperties
    {
        public ThingDef filth;
        public float chance = 1f;

        public RM_CompProperties_TrailFilth()
        {
            compClass = typeof(RM_CompTrailFilth);
        }
    }

    public class RM_CompTrailFilth : ThingComp
    {
        private IntVec3 last = IntVec3.Invalid;

        public override void CompTick()
        {
            if (parent.Spawned && parent.IsHashIntervalTick(15))
            {
                Step();
            }
        }

        // One look at where it stands: if it moved, the cell it left gets the filth.
        public bool Step()
        {
            if (!parent.Spawned)
            {
                return false;
            }
            IntVec3 pos = parent.Position;
            if (pos == last)
            {
                return false;
            }
            IntVec3 left = last;
            last = pos;
            RM_CompProperties_TrailFilth p = (RM_CompProperties_TrailFilth)props;
            if (!LanternDeepsSettings.slickTrailEnabled || p.filth == null || !left.IsValid || !left.InBounds(parent.Map))
            {
                return false;
            }
            return Rand.Chance(p.chance) && FilthMaker.TryMakeFilth(left, parent.Map, p.filth);
        }
    }

    public class RM_CompProperties_FlashOnHurt : CompProperties
    {
        public ThingDef flare;
        public HediffDef dazzle;
        public float dazzleRadius = 8f;
        public int cooldownTicks = 600;

        public RM_CompProperties_FlashOnHurt()
        {
            compClass = typeof(RM_CompFlashOnHurt);
        }
    }

    public class RM_CompFlashOnHurt : ThingComp
    {
        public int lastFlashTick = -999999;

        private RM_CompProperties_FlashOnHurt Props => (RM_CompProperties_FlashOnHurt)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastFlashTick, "lastFlashTick", -999999);
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            if (!LanternDeepsSettings.blinkerFlashEnabled || totalDamageDealt <= 0f || !parent.Spawned)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (now - lastFlashTick < Props.cooldownTicks)
            {
                return;
            }
            lastFlashTick = now;
            Flash();
        }

        public int Flash()
        {
            Map map = parent.Map;
            IntVec3 at = parent.Position;
            if (Props.flare != null)
            {
                GenSpawn.Spawn(ThingMaker.MakeThing(Props.flare), at, map);
            }
            FleckMaker.ThrowLightningGlow(at.ToVector3Shifted(), map, 6f);
            int dazzled = 0;
            if (Props.dazzle == null)
            {
                return 0;
            }
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
            {
                if (p == parent || p.def == parent.def || p.Dead || p.Position.DistanceTo(at) > Props.dazzleRadius)
                {
                    continue;
                }
                if (!p.Awake() || !GenSight.LineOfSight(p.Position, at, map))
                {
                    continue;
                }
                Hediff h = p.health.hediffSet.GetFirstHediffOfDef(Props.dazzle);
                if (h == null)
                {
                    p.health.AddHediff(Props.dazzle);
                }
                else
                {
                    h.TryGetComp<HediffComp_Disappears>()?.ResetElapsedTicks();
                }
                dazzled++;
            }
            return dazzled;
        }
    }

    public class RM_CompProperties_Knocker : CompProperties
    {
        public float hearRadius = 15f;
        public SoundDef drum;

        public RM_CompProperties_Knocker()
        {
            compClass = typeof(RM_CompKnocker);
        }
    }

    public class RM_CompKnocker : ThingComp
    {
        private int lastMessageTick = -999999;

        private RM_CompProperties_Knocker Props => (RM_CompProperties_Knocker)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastMessageTick, "lastMessageTick", -999999);
        }

        public static bool TameKnockerOn(Map map)
        {
            if (!LanternDeepsSettings.knockerAlarmEnabled || map == null)
            {
                return false;
            }
            foreach (Pawn p in map.mapPawns.SpawnedColonyAnimals)
            {
                if (!p.Dead && p.TryGetComp<RM_CompKnocker>() != null)
                {
                    return true;
                }
            }
            return false;
        }

        public override void CompTick()
        {
            if (!(parent is Pawn p) || !p.Spawned || !p.IsHashIntervalTick(120) || p.Downed || !LanternDeepsSettings.knockerAlarmEnabled)
            {
                return;
            }
            Hear(p);
        }

        // Returns the number of failing cells heard (the proof reads it).
        public int Hear(Pawn p)
        {
            RM_MapComponent_DeepCollapse comp = p.Map.GetComponent<RM_MapComponent_DeepCollapse>();
            if (comp == null)
            {
                return 0;
            }
            List<IntVec3> heard = comp.PendingCells.Where(c => c.DistanceTo(p.Position) <= Props.hearRadius).ToList();
            if (heard.Count == 0)
            {
                return 0;
            }
            Map map = p.Map;
            Props.drum?.PlayOneShot(new TargetInfo(p.Position, map));
            MoteMaker.ThrowText(p.DrawPos, map, "RM_KnockerDrumText".Translate());
            foreach (IntVec3 c in heard.Take(12))
            {
                FleckMaker.Static(c, map, FleckDefOf.FeedbackGoto);
            }
            // run for the sound side: away from the failing cells
            if (p.CurJobDef != JobDefOf.Flee && !p.InMentalState)
            {
                if (CellFinder.TryFindRandomReachableNearbyCell(p.Position, map, 16f, TraverseParms.For(p),
                        c => c.Standable(map) && heard.All(h => h.DistanceTo(c) > 8f), null, out IntVec3 dest))
                {
                    p.jobs.StartJob(JobMaker.MakeJob(JobDefOf.Flee, dest), JobCondition.InterruptForced);
                }
            }
            if (p.Faction == Faction.OfPlayer && Find.TickManager.TicksGame - lastMessageTick > 600)
            {
                lastMessageTick = Find.TickManager.TicksGame;
                Messages.Message("RM_KnockerDrums".Translate(p.LabelShort),
                    new LookTargets(heard.Take(10).Select(c => new TargetInfo(c, map))), MessageTypeDefOf.ThreatBig);
            }
            return heard.Count;
        }
    }

    // jawa/static_call proofs (validation.py, hydrocarbon_wave2).
    public static class RM_HydrocarbonWave2Proof
    {
        private static Pawn Spawn(string kindName, out string err)
        {
            err = null;
            Map map = Find.CurrentMap;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(kindName);
            if (map == null || kind == null)
            {
                err = "no map or kind " + kindName;
                return null;
            }
            if (!CellFinder.TryFindRandomCell(map, c => c.Standable(map) && c.DistanceToEdge(map) > 10, out IntVec3 cell))
            {
                err = "no cell";
                return null;
            }
            Pawn p = PawnGenerator.GeneratePawn(kind);
            GenSpawn.Spawn(p, cell, map);
            return p;
        }

        // Walks a slick three cells by teleport and counts Filth_Fuel left behind.
        public static string ProofSlick(string unused)
        {
            Pawn p = Spawn("RM_Slick", out string err);
            if (p == null)
            {
                return err;
            }
            Map map = p.Map;
            RM_CompTrailFilth comp = p.TryGetComp<RM_CompTrailFilth>();
            ThingDef fuel = ((RM_CompProperties_TrailFilth)comp?.props)?.filth;
            IntVec3 start = p.Position;
            int moved = 0;
            comp?.Step();
            for (int i = 0; i < 3; i++)
            {
                IntVec3 next = p.Position + IntVec3.East;
                if (!next.Standable(map))
                {
                    break;
                }
                p.Position = next;
                moved++;
                comp?.Step();
            }
            int filth = 0;
            for (int i = 0; i <= moved; i++)
            {
                IntVec3 c = start + new IntVec3(i, 0, 0);
                if (fuel != null && c.GetFirstThing(map, fuel) != null)
                {
                    filth++;
                }
            }
            return "moved=" + moved + " fuelCells=" + filth + " comp=" + (comp != null);
        }

        // Spawns a blinker beside a muffalo and flashes it.
        public static string ProofBlinker(string unused)
        {
            Pawn p = Spawn("RM_Blinker", out string err);
            if (p == null)
            {
                return err;
            }
            PawnKindDef muff = DefDatabase<PawnKindDef>.GetNamedSilentFail("Muffalo");
            if (muff != null && CellFinder.TryFindRandomCellNear(p.Position, p.Map, 3, c => c.Standable(p.Map) && GenSight.LineOfSight(c, p.Position, p.Map), out IntVec3 near))
            {
                GenSpawn.Spawn(PawnGenerator.GeneratePawn(muff), near, p.Map);
            }
            RM_CompFlashOnHurt comp = p.TryGetComp<RM_CompFlashOnHurt>();
            if (comp == null)
            {
                return "no comp";
            }
            int dazzled = comp.Flash();
            ThingDef flare = ((RM_CompProperties_FlashOnHurt)comp.props).flare;
            bool flareUp = flare != null && p.Position.GetFirstThing(p.Map, flare) != null;
            return "dazzled=" + dazzled + " flare=" + flareUp;
        }

        // Holds a roof cell for its warning beside a knocker and lets it hear.
        public static string ProofKnocker(string unused)
        {
            Pawn p = Spawn("RM_Knocker", out string err);
            if (p == null)
            {
                return err;
            }
            Map map = p.Map;
            RM_MapComponent_DeepCollapse comp = map.GetComponent<RM_MapComponent_DeepCollapse>();
            if (comp == null)
            {
                return "no collapse comp (only on a Deep)";
            }
            if (!CellFinder.TryFindRandomCellNear(p.Position, map, 6, c => c.Roofed(map) && c.Standable(map) && c.GetFirstPawn(map) == null, out IntVec3 cell))
            {
                return "no roofed cell near";
            }
            map.roofCollapseBuffer.MarkToCollapse(cell);
            map.roofCollapseBufferResolver.CollapseRoofsMarkedToCollapse();
            int heard = p.TryGetComp<RM_CompKnocker>()?.Hear(p) ?? -1;
            return "pending=" + comp.Pending + " heard=" + heard + " job=" + p.CurJobDef?.defName;
        }
    }
}
