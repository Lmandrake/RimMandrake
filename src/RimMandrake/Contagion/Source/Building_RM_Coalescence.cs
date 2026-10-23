using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Contagion
{
    // CONTAGION_MECHANICS_BUILD_1 Part 2 — the Coalescence.
    //
    // "ONE continuous organism (ruled by card): spawns during long Blooms,
    // absorbs nearby Unfinished (they walk in and despawn into it), grows
    // through 3 staged forms (graphic swaps), continuously emits manhunter
    // Unfinished at everything not absorbed. Cannot leave the storm shadow;
    // ANY Burn kills it (natural or Repulsor-forced) — death collapses it into
    // a mulch + genome-sample bonanza." (item §2)
    //
    // Built as a stationary, faction-less organism-building rather than a
    // pawn: it never moves (so it can never leave the storm shadow it was born
    // in), it is one continuous Thing whose mass carries across all three
    // stages, and its graphic swaps by stage. It is spawned only by
    // RM_MapComponent_ContagionSky (a Contagion-biome gate, long-Bloom rule).
    public class RM_CoalescenceExtension : DefModExtension
    {
        public List<GraphicData> stageGraphics = new List<GraphicData>();
        // Absorbed mass at which each stage begins; [0] must be 0.
        public List<int> stageMass = new List<int> { 0, 6, 15 };
        // Ticks between manhunter emissions, per stage.
        public List<int> emitIntervalTicks = new List<int> { 5000, 3000, 1800 };
        // Live manhunter Unfinished on the map it will not exceed, per stage.
        public List<int> maxManhunters = new List<int> { 2, 4, 6 };
        public float absorbRadius = 18f;
        // One unit of mass accrues by itself this often, so it still grows
        // with the Unfinished spawner switched off.
        public int passiveGrowthTicks = 60000;
        public PawnKindDef unfinishedKind;
        public ThingDef sampleDef;
        // Genome samples per death = base + perStage * stage + mass / massPerSample.
        public int samplesBase = 2;
        public int samplesPerStage = 2;
        public int massPerSample = 4;
        public int samplesMax = 14;
        // Contagion mulch (owner Q4, 2026-10-15) per death = (base + perStage * stage + mass) x the death's factor:
        // 1 for a Burn collapse, killedMulchFactor for a kill by damage. Null mulchDef = none.
        public ThingDef mulchDef;
        public int mulchBase = 10;
        public int mulchPerStage = 10;
        public float killedMulchFactor = 0.5f;
    }

    public class Building_RM_Coalescence : Building
    {
        private int mass;
        private int lastEmitTick = -1;
        private int lastGrowthTick = -1;

        private static readonly Dictionary<GraphicData, Graphic> graphicCache = new Dictionary<GraphicData, Graphic>();

        public RM_CoalescenceExtension Ext => def.GetModExtension<RM_CoalescenceExtension>();

        public int Mass => mass;

        public int Stage
        {
            get
            {
                RM_CoalescenceExtension ext = Ext;
                if (ext == null) return 0;
                return RM_CoalescenceKernel.Stage(mass, ext.stageMass);
            }
        }

        private static int At(List<int> list, int i, int fallback)
        {
            return RM_CoalescenceKernel.At(list, i, fallback);
        }

        public override Graphic Graphic
        {
            get
            {
                RM_CoalescenceExtension ext = Ext;
                if (ext == null || ext.stageGraphics.NullOrEmpty()) return base.Graphic;
                GraphicData gd = ext.stageGraphics[Mathf.Clamp(Stage, 0, ext.stageGraphics.Count - 1)];
                if (!graphicCache.TryGetValue(gd, out Graphic g))
                {
                    g = gd.Graphic;
                    graphicCache[gd] = g;
                }
                return g;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref mass, "rmCoalescenceMass", 0);
            Scribe_Values.Look(ref lastEmitTick, "rmCoalescenceLastEmit", -1);
            Scribe_Values.Look(ref lastGrowthTick, "rmCoalescenceLastGrowth", -1);
        }

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            int now = Find.TickManager.TicksGame;
            if (lastEmitTick < 0) lastEmitTick = now;
            if (lastGrowthTick < 0) lastGrowthTick = now;
        }

        protected override void Tick()
        {
            base.Tick();
            if (!Spawned || !this.IsHashIntervalTick(RM_ContagionSky.Interval)) return;
            RM_CoalescenceExtension ext = Ext;
            if (ext == null) return;

            RM_MapComponent_ContagionSky sky = Map.GetComponent<RM_MapComponent_ContagionSky>();
            if (RM_CoalescenceKernel.Collapses(sky != null && sky.BurnActive))
            {
                Collapse(ext);
                return;
            }
            if (!RM_CoalescenceKernel.Acts(false, RM_ContagionSettings.coalescenceEnabled)) return;

            int now = Find.TickManager.TicksGame;
            if (RM_CoalescenceKernel.PassiveGrowthDue(ext.passiveGrowthTicks, now, lastGrowthTick))
            {
                lastGrowthTick = now;
                Grow(1);
            }

            Absorb(ext);

            int stage = Stage;
            if (RM_CoalescenceKernel.EmitDue(now, lastEmitTick, At(ext.emitIntervalTicks, stage, 3000)))
            {
                lastEmitTick = now;
                TryEmit(ext, stage);
            }
        }

        private void Grow(int amount)
        {
            int before = Stage;
            mass += amount;
            if (Stage > before && Spawned)
            {
                FleckMaker.ThrowDustPuffThick(DrawPos, Map, 3f, new Color(0.45f, 0.05f, 0.08f));
                Messages.Message("The Coalescence heaves and swells — it has grown.", this, MessageTypeDefOf.ThreatSmall);
            }
        }

        private static readonly List<Pawn> tmpPawns = new List<Pawn>();

        private bool IsAbsorbable(Pawn p, RM_CoalescenceExtension ext)
        {
            return p != null && !p.Dead && p.Spawned && ext.unfinishedKind != null
                && p.kindDef == ext.unfinishedKind && p.Faction == null
                && !p.InMentalState; // its own emitted manhunters are not re-eaten
        }

        // Absorb diagnostics, per pass, never scribed (CONTAGION_MECHANICS_BUILD_1 A6: live 2026-10-19e read 0 of 6
        // Unfinished absorbed in ten passes, every survivor on a Wait job, and the old Absorb skipped them in silence).
        // Read live through RM_CoalescenceProof.AbsorbReport. Index = AbsorbWhy.
        public enum AbsorbWhy { Candidate, OutOfRange, Eaten, Downed, AlreadyWalking, NoRingCell, Unreachable, Ordered, OrderLost, Count }
        private readonly int[] lastPassCounts = new int[(int)AbsorbWhy.Count];
        private readonly int[] totalCounts = new int[(int)AbsorbWhy.Count];
        private int absorbPasses;
        // Pawns ordered last pass: one still absorbable, in range, outside the ring and NOT on our Goto this pass lost
        // the order between passes (a pather error ends a Goto into vanilla's Wait 250, then the main think tree, where
        // CreatureBehaviors' sun escape can send it to shade instead).
        private readonly HashSet<int> orderedLastPass = new HashSet<int>();
        private readonly HashSet<int> orderedThisPass = new HashSet<int>();
        private static readonly List<IntVec3> tmpRing = new List<IntVec3>();

        public int AbsorbPasses => absorbPasses;
        public int LastPass(AbsorbWhy w) => lastPassCounts[(int)w];
        public int Total(AbsorbWhy w) => totalCounts[(int)w];

        private void Count(AbsorbWhy w)
        {
            lastPassCounts[(int)w]++;
            totalCounts[(int)w]++;
        }

        private void Absorb(RM_CoalescenceExtension ext)
        {
            absorbPasses++;
            System.Array.Clear(lastPassCounts, 0, lastPassCounts.Length);
            orderedThisPass.Clear();
            tmpPawns.Clear();
            tmpPawns.AddRange(Map.mapPawns.AllPawnsSpawned);
            CellRect ringRect = this.OccupiedRect().ExpandedBy(1);
            for (int i = 0; i < tmpPawns.Count; i++)
            {
                Pawn p = tmpPawns[i];
                if (!IsAbsorbable(p, ext)) continue;
                Count(AbsorbWhy.Candidate);
                if (!p.Position.InHorDistOf(Position, ext.absorbRadius)) { Count(AbsorbWhy.OutOfRange); continue; }

                if (ringRect.Contains(p.Position))
                {
                    FleckMaker.ThrowDustPuffThick(p.DrawPos, Map, 1.5f, new Color(0.45f, 0.05f, 0.08f));
                    p.Destroy(DestroyMode.Vanish);
                    Grow(1);
                    Count(AbsorbWhy.Eaten);
                    continue;
                }

                if (p.Downed || p.jobs == null) { Count(AbsorbWhy.Downed); continue; }
                Job cur = p.CurJob;
                if (cur != null && cur.def == JobDefOf.Goto && cur.targetA.IsValid && ringRect.Contains(cur.targetA.Cell))
                {
                    Count(AbsorbWhy.AlreadyWalking);
                    orderedThisPass.Add(p.thingIDNumber);
                    continue;
                }
                if (orderedLastPass.Contains(p.thingIDNumber)) Count(AbsorbWhy.OrderLost);

                // The NEAREST ring cell this pawn can actually reach. The old code took the nearest standable cell and
                // gave up when that one cell was unreachable (a wall or rock on the near side), with 15 more to try.
                tmpRing.Clear();
                foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(this))
                {
                    if (c.InBounds(Map) && c.Standable(Map)) tmpRing.Add(c);
                }
                if (tmpRing.Count == 0) { Count(AbsorbWhy.NoRingCell); continue; }
                IntVec3 from = p.Position;
                tmpRing.Sort((a, b) => a.DistanceToSquared(from).CompareTo(b.DistanceToSquared(from)));
                IntVec3 dest = IntVec3.Invalid;
                for (int k = 0; k < tmpRing.Count; k++)
                {
                    if (p.CanReach(tmpRing[k], PathEndMode.OnCell, Danger.Deadly)) { dest = tmpRing[k]; break; }
                }
                tmpRing.Clear();
                if (!dest.IsValid) { Count(AbsorbWhy.Unreachable); continue; }
                Job job = JobMaker.MakeJob(JobDefOf.Goto, dest);
                job.locomotionUrgency = LocomotionUrgency.Walk;
                job.expiryInterval = 2500;
                p.jobs.StartJob(job, JobCondition.InterruptForced);
                Count(AbsorbWhy.Ordered);
                orderedThisPass.Add(p.thingIDNumber);
            }
            tmpPawns.Clear();
            orderedLastPass.Clear();
            orderedLastPass.UnionWith(orderedThisPass);
        }

        // One line for the proof hook: "passes=N last[...] total[...]".
        public string AbsorbReport()
        {
            System.Text.StringBuilder sb = new System.Text.StringBuilder();
            sb.Append("passes=").Append(absorbPasses).Append(" mass=").Append(mass).Append(" last[");
            for (int w = 0; w < (int)AbsorbWhy.Count; w++)
            {
                sb.Append(w == 0 ? "" : " ").Append((AbsorbWhy)w).Append('=').Append(lastPassCounts[w]);
            }
            sb.Append("] total[");
            for (int w = 0; w < (int)AbsorbWhy.Count; w++)
            {
                sb.Append(w == 0 ? "" : " ").Append((AbsorbWhy)w).Append('=').Append(totalCounts[w]);
            }
            return sb.Append(']').ToString();
        }

        private void TryEmit(RM_CoalescenceExtension ext, int stage)
        {
            if (ext.unfinishedKind == null) return;
            int live = 0;
            IReadOnlyList<Pawn> all = Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn p = all[i];
                if (p.kindDef == ext.unfinishedKind && p.MentalStateDef == MentalStateDefOf.Manhunter) live++;
            }
            if (!RM_CoalescenceKernel.MayEmit(live, At(ext.maxManhunters, stage, 3))) return;

            IntVec3 cell = IntVec3.Invalid;
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(this).InRandomOrder())
            {
                if (c.InBounds(Map) && c.Standable(Map)) { cell = c; break; }
            }
            if (!cell.IsValid) return;

            Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(ext.unfinishedKind, null));
            GenSpawn.Spawn(pawn, cell, Map);
            pawn.mindState?.mentalStateHandler?.TryStartMentalState(MentalStateDefOf.Manhunter, null, true);
        }

        // Any Burn kills it: it collapses into slime, a spill of genome samples
        // (sourceless — they gestate unmatched organs) and a heap of Contagion
        // mulch: the ruled "mulch + genome-sample bonanza".
        private void Collapse(RM_CoalescenceExtension ext)
        {
            Map map = Map;
            IntVec3 center = Position;
            int stage = Stage;
            int samples = RM_CoalescenceKernel.Samples(ext.samplesBase, ext.samplesPerStage, stage, ext.massPerSample, mass, ext.samplesMax);

            Messages.Message("The Burn catches the Coalescence in the open light — it collapses, spilling novel tissue.",
                new TargetInfo(center, map), MessageTypeDefOf.PositiveEvent);
            Destroy(DestroyMode.Vanish);

            if (ext.sampleDef != null)
            {
                for (int i = 0; i < samples; i++)
                {
                    Thing s = ThingMaker.MakeThing(ext.sampleDef);
                    // CONTAGION_GROWN_LIMBS_BUILD_1: the death-spill is Monstrous grade.
                    CompGenomeSample sampleComp = s.TryGetComp<CompGenomeSample>();
                    if (sampleComp != null)
                    {
                        sampleComp.monstrous = true;
                    }
                    GenPlace.TryPlaceThing(s, center, map, ThingPlaceMode.Near);
                }
            }
            RM_ContagionMulchUtility.Drop(ext.mulchDef, RM_CoalescenceKernel.Mulch(ext.mulchBase, ext.mulchPerStage, stage, mass, 1f), center, map);
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, 2.5f + stage, true))
            {
                if (c.InBounds(map) && c.Standable(map) && Rand.Chance(0.5f))
                {
                    FilthMaker.TryMakeFilth(c, map, ThingDefOf.Filth_Slime);
                }
            }
        }

        // Killed by damage instead of a Burn: no samples (the Burn's light is what fixes the tissue), but the dead goo
        // still leaves a smaller heap of mulch.
        public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
        {
            Map map = Map;
            IntVec3 at = Position;
            bool killed = mode == DestroyMode.KillFinalize && Spawned;
            int stage = Stage;
            RM_CoalescenceExtension ext = Ext;
            base.Destroy(mode);
            if (killed && ext != null)
            {
                RM_ContagionMulchUtility.Drop(ext.mulchDef, RM_CoalescenceKernel.Mulch(ext.mulchBase, ext.mulchPerStage, stage, mass, ext.killedMulchFactor), at, map);
            }
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string line = "Stage " + (Stage + 1) + ", absorbed mass " + mass + ".";
            return s.NullOrEmpty() ? line : s + "\n" + line;
        }
    }

    // jawa/static_call proof hook (validation.py, coalescence chain): what Absorb did with its candidates, so a live
    // "0 absorbed" names its cause (out of range / unreachable / no ring cell / order lost between passes) instead
    // of leaving the harness to guess from the survivors' jobs.
    public static class RM_CoalescenceProof
    {
        public static string AbsorbReport(Thing coalescence)
        {
            Building_RM_Coalescence c = coalescence as Building_RM_Coalescence;
            if (c == null)
            {
                return "UNMEASURED " + (coalescence?.ThingID ?? "null") + " is not a Building_RM_Coalescence";
            }
            if (!c.Spawned)
            {
                return "UNMEASURED " + c.ThingID + " is not spawned";
            }
            return "OK " + c.AbsorbReport();
        }
    }
}
