using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LanternDeeps
{
    // ════════════════════════════════════════════════════════════════════
    // LANTERNDEEPS_WORKING_DEAD_BUILD_1 (slate row 1 of
    // design/Jawa/worldbuilding/biomes/lanterndeeps_bedazzle_review_2026-10-01.md; the sheet's
    // signature image "a blue lantern burning under the mountain, and a dead miner's suit walking
    // toward it", and its access ruling "the dead are well-equipped, and some of them walk").
    //
    //  1. RM_GenStep_WellProvisionedDead: on a new Deep, high-technology remains lie along the
    //     galleries and at the shaft bottom (near the cave exit): desiccated corpses in good gear,
    //     forbidden salvage, slumped dead chassis. Never poorly equipped (sheet hard ban 7).
    //     It also grows the Shard-minds, each with a few dead chassis around it.
    //  2. Building_RM_WorkingDead: a dead chassis. Within reach of a Shard-mind it STANDS and works
    //     at the rock of its own accord (dust at the face, nothing is ever dug: owner on Orun-Ghal,
    //     "I don't think the crystals are too keen mining"), and when light comes near it stops and
    //     turns toward it. Away from a Shard-mind it lies slumped. Its state is on the inspect pane.
    //  3. CompRM_ShardMind: a living colony droid near a Shard-mind sometimes stops and stands
    //     facing it; the job report says so ("stopped, listening to the shard-mind").
    // Nothing moves or vanishes without a readable sign. Free tier, RM_, no Star Wars dependency:
    // a droid is any mechanoid-fleshed pawn or one whose flesh type is the Droidworks droid type.
    // ════════════════════════════════════════════════════════════════════

    public class RM_DeepLoot
    {
        public ThingDef thing;
        public IntRange count = new IntRange(1, 1);
        public float chance = 1f;
    }

    public class RM_GenStep_WellProvisionedDead : GenStep
    {
        public List<PawnKindDef> corpseKinds = new List<PawnKindDef>();
        public List<RM_DeepLoot> loot = new List<RM_DeepLoot>();
        public ThingDef chassisDef;
        public ThingDef shardMindDef;
        public IntRange gallerySites = new IntRange(3, 5);
        public IntRange corpsesPerSite = new IntRange(1, 2);
        public float chassisPerSiteChance = 0.5f;
        public IntRange shardMinds = new IntRange(1, 2);
        public IntRange chassisPerShardMind = new IntRange(2, 4);
        public IntRange corpseAgeDays = new IntRange(400, 4000);
        public float minSiteSpacing = 14f;

        public override int SeedPart => 604117283;

        public override void Generate(Map map, GenStepParams parms)
        {
            Place(map, LanternDeepsSettings.wellProvisionedDeadEnabled, LanternDeepsSettings.shardMindsEnabled);
        }

        /// <summary>"sites=n corpses=n chassis=n minds=n" for what this run placed.</summary>
        public string Place(Map map, bool dead, bool minds)
        {
            int sites = 0, corpses = 0, chassis = 0, mindCount = 0;
            List<IntVec3> used = new List<IntVec3>();
            Thing exit = map.listerThings.ThingsOfDef(ThingDefOf.CaveExit).FirstOrFallback();
            if (dead)
            {
                int want = gallerySites.RandomInRange;
                for (int i = 0; i < want; i++)
                {
                    // the first site is the shaft bottom, the rest are galleries
                    bool shaft = i == 0 && exit != null;
                    if (!TryFindSite(map, used, shaft ? exit.Position : IntVec3.Invalid, shaft, out IntVec3 site)) continue;
                    used.Add(site);
                    sites++;
                    int n = corpsesPerSite.RandomInRange;
                    for (int c = 0; c < n; c++) if (SpawnCorpse(map, site)) corpses++;
                    SpawnLoot(map, site);
                    if (chassisDef != null && Rand.Chance(chassisPerSiteChance) && SpawnNear(map, chassisDef, site, 3)) chassis++;
                }
            }
            if (minds && shardMindDef != null)
            {
                int want = shardMinds.RandomInRange;
                for (int i = 0; i < want; i++)
                {
                    if (!TryFindSite(map, used, IntVec3.Invalid, false, out IntVec3 site)) continue;
                    used.Add(site);
                    Clear(map, site);
                    GenSpawn.Spawn(ThingMaker.MakeThing(shardMindDef), site, map);
                    mindCount++;
                    if (chassisDef == null) continue;
                    int n = chassisPerShardMind.RandomInRange;
                    for (int c = 0; c < n; c++) if (SpawnNear(map, chassisDef, site, 5)) chassis++;
                }
            }
            return "sites=" + sites + " corpses=" + corpses + " chassis=" + chassis + " minds=" + mindCount;
        }

        private bool TryFindSite(Map map, List<IntVec3> used, IntVec3 near, bool useNear, out IntVec3 found)
        {
            float spacing = minSiteSpacing;
            return CellFinder.TryFindRandomCell(map, c =>
            {
                if (!c.Standable(map) || c.DistanceToEdge(map) <= 5) return false;
                if (useNear && !c.InHorDistOf(near, 9f)) return false;
                if (useNear && c.InHorDistOf(near, 3f)) return false;
                for (int i = 0; i < used.Count; i++) if (c.InHorDistOf(used[i], spacing)) return false;
                return true;
            }, out found);
        }

        private bool SpawnCorpse(Map map, IntVec3 site)
        {
            if (corpseKinds.NullOrEmpty()) return false;
            Find.FactionManager.TryGetRandomNonColonyHumanlikeFaction(out Faction faction, tryMedievalOrBetter: true);
            Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(corpseKinds.RandomElement(), faction,
                PawnGenerationContext.NonPlayer, map.Tile));
            pawn.health.SetDead();
            Corpse corpse = pawn.MakeCorpse(null, null);
            corpse.Age = corpseAgeDays.RandomInRange * GenDate.TicksPerDay;
            CompRottable rot = corpse.GetComp<CompRottable>();
            if (rot != null) rot.RotProgress += corpse.Age;
            Find.WorldPawns.PassToWorld(pawn);
            if (!GenPlace.TryPlaceThing(corpse, site, map, ThingPlaceMode.Radius, null, null, null, 2)) return false;
            corpse.SetForbidden(true, false);
            return true;
        }

        private void SpawnLoot(Map map, IntVec3 site)
        {
            foreach (RM_DeepLoot l in loot)
            {
                if (l.thing == null || !Rand.Chance(l.chance)) continue;
                int n = l.count.RandomInRange;
                while (n > 0)
                {
                    Thing t = ThingMaker.MakeThing(l.thing);
                    t.stackCount = Mathf.Min(n, l.thing.stackLimit);
                    n -= t.stackCount;
                    if (!GenPlace.TryPlaceThing(t, site, map, ThingPlaceMode.Radius, null, null, null, 2)) break;
                    t.SetForbidden(true, false);
                }
            }
        }

        private static bool SpawnNear(Map map, ThingDef def, IntVec3 centre, int radius)
        {
            for (int tries = 0; tries < 30; tries++)
            {
                IntVec3 c = centre + GenRadial.RadialPattern[Rand.Range(1, GenRadial.NumCellsInRadius(radius))];
                if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null) continue;
                if (c.GetFirstItem(map) != null || c.GetFirstPawn(map) != null) continue;
                Clear(map, c);
                Thing t = ThingMaker.MakeThing(def);
                t.Rotation = Rot4.Random;
                GenSpawn.Spawn(t, c, map, t.Rotation);
                return true;
            }
            return false;
        }

        private static void Clear(Map map, IntVec3 c)
        {
            foreach (Thing t in new List<Thing>(c.GetThingList(map)))
            {
                if (t is Plant) t.Destroy();
            }
        }
    }

    // ── The dead chassis ─────────────────────────────────────────────────
    public class RM_WorkingDeadExtension : DefModExtension
    {
        public GraphicData slumpedGraphicData;
        public ThingDef shardMindDef;
        public float mindRadius = 7f;
        public float lightRadius = 10f;
        public float colonistGlowAtLeast = 0.3f;
    }

    public class Building_RM_WorkingDead : Building
    {
        private bool standing;
        private bool facingLight;
        private Graphic slumpedGraphic;

        private RM_WorkingDeadExtension Ext => def.GetModExtension<RM_WorkingDeadExtension>();
        public bool Standing => standing;
        public bool FacingLight => facingLight;

        public override Graphic Graphic
        {
            get
            {
                if (standing) return base.Graphic;
                if (slumpedGraphic == null && Ext?.slumpedGraphicData != null)
                {
                    slumpedGraphic = Ext.slumpedGraphicData.Graphic;
                }
                return slumpedGraphic ?? base.Graphic;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref standing, "standing", false);
            Scribe_Values.Look(ref facingLight, "facingLight", false);
        }

        public override void TickRare()
        {
            base.TickRare();
            if (Spawned) Think();
        }

        /// <summary>One decision: stand or slump, then face light or work. Public for the bridge proof.</summary>
        public void Think()
        {
            RM_WorkingDeadExtension ext = Ext;
            bool nearMind = ext != null && LanternDeepsSettings.workingDeadAnimateEnabled && NearShardMind(ext);
            if (nearMind != standing)
            {
                standing = nearMind;
                FleckMaker.ThrowDustPuff(Position, Map, 1.2f);
                if (standing) MoteMaker.ThrowText(DrawPos, Map, "stands up", 3f);
            }
            facingLight = false;
            if (!standing) return;
            if (TryFindLight(ext, out IntVec3 light))
            {
                facingLight = true;
                Rotation = FaceToward(light);
                return;
            }
            // work: face the nearest rock face and worry at it. Nothing is ever mined.
            foreach (IntVec3 adj in GenAdj.CardinalDirections)
            {
                IntVec3 c = Position + adj;
                Building ed = c.InBounds(Map) ? c.GetEdifice(Map) : null;
                if (ed != null && ed.def.building != null && ed.def.building.isNaturalRock)
                {
                    Rotation = Rot4.FromIntVec3(adj);
                    FleckMaker.ThrowDustPuff(c, Map, 0.6f);
                    return;
                }
            }
            if (Rand.Chance(0.25f)) Rotation = Rot4.Random;
        }

        private bool NearShardMind(RM_WorkingDeadExtension ext)
        {
            if (ext.shardMindDef == null) return false;
            foreach (Thing t in Map.listerThings.ThingsOfDef(ext.shardMindDef))
            {
                if (t.Position.InHorDistOf(Position, ext.mindRadius)) return true;
            }
            return false;
        }

        // light = a lit glower belonging to the player, or a colonist standing in light; never the
        // lanternstone, which lights the whole Deep
        private bool TryFindLight(RM_WorkingDeadExtension ext, out IntVec3 at)
        {
            at = IntVec3.Invalid;
            float best = float.MaxValue;
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(Position, Map, ext.lightRadius, true))
            {
                if (t.Faction != Faction.OfPlayer) continue;
                if (t is Pawn p)
                {
                    if (!p.IsColonist || Map.glowGrid.GroundGlowAt(p.Position) < ext.colonistGlowAtLeast) continue;
                }
                else
                {
                    CompGlower g = (t as ThingWithComps)?.GetComp<CompGlower>();
                    if (g == null || !g.Glows) continue;
                }
                float d = t.Position.DistanceToSquared(Position);
                if (d < best) { best = d; at = t.Position; }
            }
            return at.IsValid;
        }

        private Rot4 FaceToward(IntVec3 c)
        {
            IntVec3 d = c - Position;
            if (Mathf.Abs(d.x) > Mathf.Abs(d.z)) return d.x > 0 ? Rot4.East : Rot4.West;
            return d.z >= 0 ? Rot4.North : Rot4.South;
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string mine;
            if (!standing) mine = "Slumped. A thin vein of crystal grows into its open power port.";
            else if (facingLight) mine = "Standing still, turned toward the light.";
            else mine = "Standing. Working at the rock, at a task nobody assigned.";
            return s.NullOrEmpty() ? mine : s + "\n" + mine;
        }
    }

    // ── The Shard-mind ───────────────────────────────────────────────────
    public class CompProperties_RM_ShardMind : CompProperties
    {
        public float droidRadius = 9f;
        public float stopChancePerRareTick = 0.04f;
        public IntRange stopTicks = new IntRange(900, 2400);
        public JobDef listenJob;

        public CompProperties_RM_ShardMind()
        {
            compClass = typeof(CompRM_ShardMind);
        }
    }

    public class CompRM_ShardMind : ThingComp
    {
        private CompProperties_RM_ShardMind Props => (CompProperties_RM_ShardMind)props;

        public static bool IsDroid(Pawn p)
        {
            if (p?.RaceProps == null) return false;
            if (p.RaceProps.IsMechanoid) return true;
            return p.RaceProps.FleshType?.defName == "RSW_DW_FleshType_Droid";
        }

        public override void CompTickRare()
        {
            if (parent.Spawned) Pull(false);
        }

        /// <summary>Stop droids in range (each with the setting's chance, or all when forced). Returns how many.</summary>
        public int Pull(bool force)
        {
            if (!LanternDeepsSettings.shardMindDroidPullEnabled || Props.listenJob == null) return 0;
            int n = 0;
            foreach (Pawn p in parent.Map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer))
            {
                if (!IsDroid(p) || p.Dead || p.Downed || p.Drafted || p.jobs == null) continue;
                if (!p.Position.InHorDistOf(parent.Position, Props.droidRadius)) continue;
                if (p.CurJobDef == Props.listenJob) continue;
                if (!force && !Rand.Chance(Props.stopChancePerRareTick)) continue;
                Job job = JobMaker.MakeJob(Props.listenJob, parent);
                job.expiryInterval = Props.stopTicks.RandomInRange;
                p.jobs.StartJob(job, JobCondition.InterruptForced, null, false, true);
                MoteMaker.ThrowText(p.DrawPos, p.Map, "stops", 3f);
                n++;
            }
            return n;
        }

        public override string CompInspectStringExtra()
        {
            Map map = parent.Map;
            if (map == null) return null;
            int listening = 0, standing = 0;
            foreach (Pawn p in map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer))
            {
                if (p.CurJobDef == Props.listenJob && p.CurJob?.targetA.Thing == parent) listening++;
            }
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(parent.Position, map, 8f, true))
            {
                if (t is Building_RM_WorkingDead wd && wd.Standing) standing++;
            }
            return "Aware. Dead chassis standing nearby: " + standing + ". Living droids stopped, listening: " + listening + ".";
        }
    }

    // A droid stands facing the Shard-mind until the job expires. Drafting or any forced order breaks it.
    public class JobDriver_RM_ListenToShardMind : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            Toil listen = ToilMaker.MakeToil("ListenToShardMind");
            listen.initAction = () => pawn.pather.StopDead();
            listen.tickAction = () => pawn.rotationTracker.FaceTarget(job.targetA);
            listen.defaultCompleteMode = ToilCompleteMode.Delay;
            listen.defaultDuration = job.expiryInterval > 0 ? job.expiryInterval : 1200;
            yield return listen;
        }
    }

    // ── Bridge proofs (jawa/static_call) ─────────────────────────────────
    public static class RM_WorkingDeadProof
    {
        /// <summary>Run the real placement on `map` with both halves on, regardless of settings.</summary>
        public static string ProofPlace(Map map)
        {
            GenStepDef def = DefDatabase<GenStepDef>.GetNamedSilentFail("RM_DeepWellProvisionedDead");
            if (map == null || !(def?.genStep is RM_GenStep_WellProvisionedDead step)) return "REFUSED: no map or no step";
            return step.Place(map, true, true);
        }

        /// <summary>Make every chassis think once; "standing=a facingLight=b slumped=c".</summary>
        public static string ProofAnimate(Map map)
        {
            if (map == null) return "REFUSED: no map";
            int st = 0, fl = 0, sl = 0;
            foreach (Building b in map.listerBuildings.allBuildingsNonColonist)
            {
                if (!(b is Building_RM_WorkingDead wd)) continue;
                wd.Think();
                if (!wd.Standing) sl++;
                else if (wd.FacingLight) fl++;
                else st++;
            }
            return "standing=" + st + " facingLight=" + fl + " slumped=" + sl;
        }

        /// <summary>Force every Shard-mind to stop the player droids in its range; "stopped=n".</summary>
        public static string ProofPull(Map map)
        {
            if (map == null) return "REFUSED: no map";
            int n = 0;
            foreach (Building b in map.listerBuildings.allBuildingsNonColonist)
            {
                CompRM_ShardMind c = b.GetComp<CompRM_ShardMind>();
                if (c != null) n += c.Pull(true);
            }
            return "stopped=" + n;
        }
    }
}
