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
                int s = 0;
                for (int i = 0; i < ext.stageMass.Count; i++)
                {
                    if (mass >= ext.stageMass[i]) s = i;
                }
                return s;
            }
        }

        private static int At(List<int> list, int i, int fallback)
        {
            if (list.NullOrEmpty()) return fallback;
            return list[Mathf.Clamp(i, 0, list.Count - 1)];
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
            if (sky != null && sky.BurnActive)
            {
                Collapse(ext);
                return;
            }
            if (!RM_ContagionSettings.coalescenceEnabled) return;

            int now = Find.TickManager.TicksGame;
            if (ext.passiveGrowthTicks > 0 && now - lastGrowthTick >= ext.passiveGrowthTicks)
            {
                lastGrowthTick = now;
                Grow(1);
            }

            Absorb(ext);

            int stage = Stage;
            if (now - lastEmitTick >= At(ext.emitIntervalTicks, stage, 3000))
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

        private void Absorb(RM_CoalescenceExtension ext)
        {
            tmpPawns.Clear();
            tmpPawns.AddRange(Map.mapPawns.AllPawnsSpawned);
            CellRect rect = this.OccupiedRect();
            for (int i = 0; i < tmpPawns.Count; i++)
            {
                Pawn p = tmpPawns[i];
                if (!IsAbsorbable(p, ext)) continue;
                if (!p.Position.InHorDistOf(Position, ext.absorbRadius)) continue;

                if (rect.ExpandedBy(1).Contains(p.Position))
                {
                    FleckMaker.ThrowDustPuffThick(p.DrawPos, Map, 1.5f, new Color(0.45f, 0.05f, 0.08f));
                    p.Destroy(DestroyMode.Vanish);
                    Grow(1);
                    continue;
                }

                if (p.Downed || p.jobs == null) continue;
                Job cur = p.CurJob;
                if (cur != null && cur.def == JobDefOf.Goto && cur.targetA.IsValid
                    && rect.ExpandedBy(1).Contains(cur.targetA.Cell)) continue;
                IntVec3 dest = IntVec3.Invalid;
                float best = float.MaxValue;
                foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(this))
                {
                    if (!c.InBounds(Map) || !c.Standable(Map)) continue;
                    float d = c.DistanceToSquared(p.Position);
                    if (d < best) { best = d; dest = c; }
                }
                if (!dest.IsValid || !p.CanReach(dest, PathEndMode.OnCell, Danger.Deadly)) continue;
                Job job = JobMaker.MakeJob(JobDefOf.Goto, dest);
                job.locomotionUrgency = LocomotionUrgency.Walk;
                job.expiryInterval = 2500;
                p.jobs.StartJob(job, JobCondition.InterruptForced);
            }
            tmpPawns.Clear();
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
            if (live >= At(ext.maxManhunters, stage, 3)) return;

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

        // Any Burn kills it: it collapses into slime and a spill of genome
        // samples (sourceless — they gestate unmatched organs). The mulch half
        // of the ruled bonanza waits on a Contagion mulch item, which does
        // not exist yet.
        private void Collapse(RM_CoalescenceExtension ext)
        {
            Map map = Map;
            IntVec3 center = Position;
            int stage = Stage;
            int samples = Mathf.Min(ext.samplesMax,
                ext.samplesBase + ext.samplesPerStage * stage + (ext.massPerSample > 0 ? mass / ext.massPerSample : 0));

            Messages.Message("The Burn catches the Coalescence in the open light — it collapses, spilling novel tissue.",
                new TargetInfo(center, map), MessageTypeDefOf.PositiveEvent);
            Destroy(DestroyMode.Vanish);

            if (ext.sampleDef != null)
            {
                for (int i = 0; i < samples; i++)
                {
                    Thing s = ThingMaker.MakeThing(ext.sampleDef);
                    GenPlace.TryPlaceThing(s, center, map, ThingPlaceMode.Near);
                }
            }
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, 2.5f + stage, true))
            {
                if (c.InBounds(map) && c.Standable(map) && Rand.Chance(0.5f))
                {
                    FilthMaker.TryMakeFilth(c, map, ThingDefOf.Filth_Slime);
                }
            }
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string line = "Stage " + (Stage + 1) + ", absorbed mass " + mass + ".";
            return s.NullOrEmpty() ? line : s + "\n" + line;
        }
    }
}
