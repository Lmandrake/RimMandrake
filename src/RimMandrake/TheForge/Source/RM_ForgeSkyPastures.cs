using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.TheForge
{
    // FORGE_SKY_PASTURES_1. The vapour-column pastures made visible and made to matter.
    // The column FIELD is EnvironmentalHazards' (RM_MapComponent_VaporColumns, hourly rebuild, public InColumn): this file only reads
    // it, so nothing outside TheForge changes.
    //   stage 1  grid      : SectionLayer_RM_SkyColumns, a static mesh printed per 17x17 section (faint haze, brighter rim)
    //   stage 2  spirals   : ash flecks winding up inside columns near the camera
    //   stage 3  hunting   : column-aware prey score + the jossur stoop (see the end of this file)
    //   stage 4  highlight : outline of the columns a selected column-bound flier can reach, drawn per frame, nothing otherwise
    //   stage 5  pasture   : the wander that actually puts the sky creatures in the columns (RM_JobGiver_SkyPastureWander,
    //                        Defs/ThinkTreeDefs/RM_ThinkTree_ForgeSkyPasture.xml) and the dhokkur's vent-to-vent walk
    // Design record: Transient/work_SKY_PASTURES_20261003.md.

    /// <summary>Prints the haze for the column cells owned by this section. Mesh rebuilds only when RM_SkyColumns dirties
    /// the section (the component does that when the field's signature changes), so it costs nothing per frame.</summary>
    public class SectionLayer_RM_SkyColumns : SectionLayer
    {
        private static Material hazeMat;
        private static Material rimMat;
        public static int LastPrintedCells;

        public SectionLayer_RM_SkyColumns(Section section) : base(section)
        {
            relevantChangeTypes = (ulong)RM_TheForgeDefOf.RM_SkyColumns;
        }

        // The setting only hides the draw, so flipping it back needs no regeneration.
        public override bool Visible
        {
            get { return RM_TheForgeSettings.Active(RM_TheForgeSettings.skyColumnGridEnabled); }
        }

        private static Material Haze
        {
            get
            {
                if (hazeMat == null)
                {
                    hazeMat = SolidColorMaterials.NewSolidColorMaterial(new Color(0.92f, 0.93f, 0.96f, 0.07f), ShaderDatabase.Transparent);
                }
                return hazeMat;
            }
        }

        private static Material Rim
        {
            get
            {
                if (rimMat == null)
                {
                    rimMat = SolidColorMaterials.NewSolidColorMaterial(new Color(0.95f, 0.92f, 0.85f, 0.16f), ShaderDatabase.Transparent);
                }
                return rimMat;
            }
        }

        public override void Regenerate()
        {
            ClearSubMeshes(MeshParts.All);
            RM_MapComponent_VaporColumns cols = Map.GetComponent<RM_MapComponent_VaporColumns>();
            int printed = 0;
            if (cols != null)
            {
                float y = AltitudeLayer.Conduits.AltitudeFor();
                Vector2 one = new Vector2(1f, 1f);
                foreach (IntVec3 c in section.CellRect)
                {
                    if (!cols.InColumn(c))
                    {
                        continue;
                    }
                    bool edge = !cols.InColumn(c + IntVec3.North) || !cols.InColumn(c + IntVec3.South)
                        || !cols.InColumn(c + IntVec3.East) || !cols.InColumn(c + IntVec3.West);
                    Vector3 center = c.ToVector3Shifted();
                    center.y = y;
                    Printer_Plane.PrintPlane(this, center, one, edge ? Rim : Haze);
                    printed++;
                }
            }
            LastPrintedCells = printed;
            FinalizeMesh(MeshParts.All);
        }
    }

    public class AshMote
    {
        public float cx, cz, phase, spin;
        public int age;
    }

    public class RM_MapComponent_SkyPastures : MapComponent
    {
        public const int PollTicks = 2500;
        public const int MoteStepTicks = RM_SkyKernel.MoteStepTicks;
        public const int MoteLifeTicks = RM_SkyKernel.MoteLifeTicks;
        public const int MaxMotes = 36;
        public const int MaxHighlightCells = 2500;

        private List<int> columnCells = new List<int>();
        private int signature = -1;
        private int nextPoll = 120;
        private readonly List<AshMote> motes = new List<AshMote>();

        // highlight
        private readonly List<IntVec3> highlight = new List<IntVec3>();
        private Pawn highlightFor;
        private int highlightFrame = -999;

        public int StatPolls, StatDirtyBursts, StatMotesSpawned, StatFlecks, StatStoops;

        public RM_MapComponent_SkyPastures(Map map) : base(map) { }

        public static RM_MapComponent_SkyPastures Of(Map map)
        {
            return map == null ? null : map.GetComponent<RM_MapComponent_SkyPastures>();
        }

        public int ColumnCellCount { get { return columnCells.Count; } }
        public int HighlightCount { get { return highlight.Count; } }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            nextPoll = Find.TickManager.TicksGame + 120;
        }

        // Re-reads the field through its public InColumn; when the cell set changed, dirties every section once.
        public void PollNow()
        {
            RM_MapComponent_VaporColumns cols = map.GetComponent<RM_MapComponent_VaporColumns>();
            StatPolls++;
            if (cols == null)
            {
                columnCells.Clear();
                return;
            }
            List<int> fresh = new List<int>(columnCells.Count + 16);
            int sig = 17;
            CellIndices ci = map.cellIndices;
            foreach (IntVec3 c in map.AllCells)
            {
                if (cols.InColumn(c))
                {
                    int i = ci.CellToIndex(c);
                    fresh.Add(i);
                    sig = unchecked(sig * 31 + i);
                }
            }
            columnCells = fresh;
            if (sig != signature)
            {
                signature = sig;
                DirtyAllSections();
            }
        }

        // A section whose array slot is not built yet regenerates on its own, so skipping it is correct
        // (the MessyConduit live finding, 2026-10-02: MapMeshDirty throws on a null slot during first load).
        private void DirtyAllSections()
        {
            if (RM_TheForgeDefOf.RM_SkyColumns == null)
            {
                return;
            }
            StatDirtyBursts++;
            for (int x = 0; x < map.Size.x; x += Section.Size)
            {
                for (int z = 0; z < map.Size.z; z += Section.Size)
                {
                    IntVec3 loc = new IntVec3(x, 0, z);
                    try
                    {
                        if (map.mapDrawer.SectionAt(loc) == null)
                        {
                            continue;
                        }
                    }
                    catch (System.NullReferenceException)
                    {
                        return;
                    }
                    map.mapDrawer.MapMeshDirty(loc, RM_TheForgeDefOf.RM_SkyColumns);
                }
            }
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            int now = Find.TickManager.TicksGame;
            if (now >= nextPoll)
            {
                nextPoll = now + PollTicks;
                PollNow();
            }
            if (map.IsHashIntervalTick(MoteStepTicks))
            {
                StepMotes();
            }
        }

        // ---- stage 2: ash spirals --------------------------------------------------------------------------
        private void StepMotes()
        {
            if (!RM_TheForgeSettings.Active(RM_TheForgeSettings.skyAshSpiralsEnabled) || columnCells.Count == 0
                || Find.CurrentMap != map || Find.CameraDriver == null)
            {
                if (motes.Count > 0)
                {
                    motes.Clear();
                }
                return;
            }
            CellRect view = Find.CameraDriver.CurrentViewRect.ExpandedBy(6);
            // advance + throw
            for (int i = motes.Count - 1; i >= 0; i--)
            {
                AshMote m = motes[i];
                m.age += MoteStepTicks;
                if (!RM_SkyKernel.MoteAlive(m.age))
                {
                    motes.RemoveAt(i);
                    continue;
                }
                float t = m.age / (float)MoteLifeTicks;
                RM_SkyKernel.MotePos(m.cx, m.cz, m.phase, m.spin, m.age, out float mx, out float mz);
                Vector3 v = new Vector3(mx, 0f, mz);
                if (v.ToIntVec3().InBounds(map))
                {
                    FleckMaker.ThrowDustPuffThick(v, map, Rand.Range(0.7f, 1.3f) * (1f - 0.4f * t), new Color(0.42f, 0.40f, 0.38f, 0.55f * (1f - t * 0.6f)));
                    StatFlecks++;
                }
            }
            // spawn: a random column cell that is on screen (a few tries; the field is mostly off screen)
            if (motes.Count < MaxMotes && Rand.Chance(0.6f))
            {
                for (int tries = 0; tries < 8; tries++)
                {
                    IntVec3 c = map.cellIndices.IndexToCell(columnCells[Rand.Range(0, columnCells.Count)]);
                    if (view.Contains(c))
                    {
                        motes.Add(new AshMote
                        {
                            cx = c.x + 0.5f,
                            cz = c.z + 0.5f,
                            phase = Rand.Range(0f, Mathf.PI * 2f),
                            spin = Rand.Chance(0.5f) ? 7.5f : -7.5f
                        });
                        StatMotesSpawned++;
                        break;
                    }
                }
            }
        }

        // ---- stage 4: the flier-selected highlight ---------------------------------------------------------
        public override void MapComponentUpdate()
        {
            base.MapComponentUpdate();
            if (!RM_TheForgeSettings.Active(RM_TheForgeSettings.skyColumnHighlightEnabled) || Find.CurrentMap != map
                || Find.Selector == null)
            {
                return;
            }
            Pawn sel = Find.Selector.SingleSelectedThing as Pawn;
            RM_CompVaporDrifter d = sel == null ? null : sel.TryGetComp<RM_CompVaporDrifter>();
            if (d == null || !sel.Spawned || sel.Map != map)
            {
                highlightFor = null;
                if (highlight.Count > 0)
                {
                    highlight.Clear();
                }
                return;
            }
            // recompute on a new selection and twice a second afterwards; a flier moves, the columns do not
            if (sel != highlightFor || Time.frameCount - highlightFrame > 30)
            {
                highlightFor = sel;
                highlightFrame = Time.frameCount;
                RebuildHighlight(sel, d.Props);
            }
            if (highlight.Count > 0)
            {
                GenDraw.DrawFieldEdges(highlight, new Color(0.98f, 0.86f, 0.45f, 0.9f));
            }
        }

        // The columns it can use: column cells within its own search radius (the same radius RM_JobGiver_ColumnWander uses to
        // pick a wander root), nearest first so the cap drops the far ones.
        private void RebuildHighlight(Pawn p, CompProperties_VaporDrifter props)
        {
            highlight.Clear();
            float reach = RM_SkyKernel.HighlightReach(props.columnSearchRadius);
            float r2 = reach * reach;
            IntVec3 at = p.Position;
            CellIndices ci = map.cellIndices;
            for (int i = 0; i < columnCells.Count; i++)
            {
                IntVec3 c = ci.IndexToCell(columnCells[i]);
                if ((c - at).LengthHorizontalSquared <= r2)
                {
                    highlight.Add(c);
                }
            }
            // columnCells is in map order, so the cap must cut by distance, not by position in the list
            if (highlight.Count > MaxHighlightCells)
            {
                highlight.Sort((a, b) => (a - at).LengthHorizontalSquared.CompareTo((b - at).LengthHorizontalSquared));
                highlight.RemoveRange(MaxHighlightCells, highlight.Count - MaxHighlightCells);
            }
        }

        public string DebugReport()
        {
            return "skyColumnCells=" + columnCells.Count + " skyPolls=" + StatPolls + " skyDirtyBursts=" + StatDirtyBursts
                + " skyMotesLive=" + motes.Count + " skyMotesSpawned=" + StatMotesSpawned + " skyFlecks=" + StatFlecks
                + " skyStoops=" + StatStoops + " skyHighlightCells=" + highlight.Count
                + " skyGridPrinted=" + SectionLayer_RM_SkyColumns.LastPrintedCells + " " + PastureReport();
        }

        // Stage 5 read-back: the wild pawns the pasture wander governs right now (awake, unsealed), and how many of them stand
        // where that wander would put them (a column cell, or within their own leash of one). A live proof reads these two.
        public string PastureReport()
        {
            RM_MapComponent_VaporColumns cols = map.GetComponent<RM_MapComponent_VaporColumns>();
            int governed = 0, home = 0, dhokkur = 0, dhokkurHome = 0, flock = 0, flockHome = 0;
            // the flock's current jobs (diagnostic: which think node holds a bird that is not home, e.g. LayDown or Ingest)
            SortedDictionary<string, int> jobs = new SortedDictionary<string, int>();
            if (cols != null)
            {
                IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
                for (int i = 0; i < pawns.Count; i++)
                {
                    Pawn p = pawns[i];
                    if (!RM_JobGiver_SkyPastureWander.Leash(p, out float search, out float leash, out bool isDhokkur))
                    {
                        continue;
                    }
                    bool ok = RM_JobGiver_SkyPastureWander.AtHome(cols, p.Position, leash);
                    governed++;
                    if (ok) home++;
                    if (testFlock.Contains(p))
                    {
                        flock++;
                        if (ok) flockHome++;
                        string jd = p.CurJobDef == null ? "none" : p.CurJobDef.defName;
                        jobs[jd] = jobs.TryGetValue(jd, out int jn) ? jn + 1 : 1;
                    }
                    if (isDhokkur)
                    {
                        dhokkur++;
                        if (ok) dhokkurHome++;
                    }
                }
            }
            return "skyPastureGoverned=" + governed + " skyPastureHome=" + home + " skyDhokkurGoverned=" + dhokkur
                + " skyDhokkurHome=" + dhokkurHome + " skyPastureWanders=" + StatPastureWanders
                + " skyFlockGoverned=" + flock + " skyFlockHome=" + flockHome + " skyFlockWanders=" + StatFlockWanders
                + " skyPastureHomings=" + StatPastureHomings + " skyFlockHomings=" + StatFlockHomings
                + " skyFlockJobs=" + (jobs.Count == 0 ? "none" : string.Join(",", jobs.Select(kv => kv.Key + ":" + kv.Value)));
        }

        public int StatPastureWanders, StatFlockWanders, StatPastureHomings, StatFlockHomings;

        // The pawns the last test flock set down (debug/proof only, not saved): the live bar measures THESE, never the map.
        private readonly HashSet<Pawn> testFlock = new HashSet<Pawn>();

        /// <summary>Debug/proof only: destroys whatever of the last test flock is still spawned, so a proof leaves the map as
        /// it found it.</summary>
        public string RemoveTestFlock()
        {
            int removed = 0;
            foreach (Pawn p in testFlock)
            {
                if (p == null)
                {
                    continue;
                }
                if (p.Spawned)
                {
                    p.Destroy(DestroyMode.Vanish);
                    removed++;
                }
                else if (p.Dead && p.Corpse != null && p.Corpse.Spawned)
                {
                    p.Corpse.Destroy(DestroyMode.Vanish);   // a bird that died out on the ash leaves no debris either
                    removed++;
                }
            }
            testFlock.Clear();
            return "skyFlockRemoved=" + removed;
        }

        public void NotePastureWander(Pawn p)
        {
            StatPastureWanders++;
            if (testFlock.Contains(p))
            {
                StatFlockWanders++;
            }
        }

        public void NotePastureHoming(Pawn p)
        {
            StatPastureHomings++;
            if (testFlock.Contains(p))
            {
                StatFlockHomings++;
            }
        }

        public static readonly string[] TestFlockKinds = { "RM_FleetFlier", "RM_FleetFlier", "RM_FleetFlier", "RM_FleetFlier", "RM_Bulloo", "RM_Bulloo" };

        /// <summary>Debug/proof only: spawns the test flock, wild, on standable cells 18-30 cells from one column cell and
        /// outside every column and leash, and returns a tagged line (skyFlockSpawned=0 when the map has no column).</summary>
        public string SpawnTestFlock()
        {
            PollNow();
            RM_MapComponent_VaporColumns cols = map.GetComponent<RM_MapComponent_VaporColumns>();
            if (cols == null || columnCells.Count == 0)
            {
                return "skyFlockSpawned=0 skyFlockWhy=no_column_cells";
            }
            IntVec3 anchor = map.cellIndices.IndexToCell(columnCells[Rand.Range(0, columnCells.Count)]);
            List<IntVec3> spots = new List<IntVec3>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(anchor, 30f, false))
            {
                float d = (c - anchor).LengthHorizontal;
                if (d < 18f || !c.InBounds(map) || !c.Standable(map) || c.Fogged(map) || cols.InColumn(c)
                    || cols.NearestColumnCell(c, 12.5f).IsValid)
                {
                    continue;
                }
                spots.Add(c);
            }
            int spawned = 0;
            RemoveTestFlock();   // a second spawn never strands the first flock outside the tracking
            StatFlockWanders = 0;
            StatFlockHomings = 0;
            for (int i = 0; i < TestFlockKinds.Length && spots.Count > 0; i++)
            {
                PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(TestFlockKinds[i]);
                if (kind == null)
                {
                    continue;
                }
                IntVec3 at = spots[Rand.Range(0, spots.Count)];
                Pawn bird = PawnGenerator.GeneratePawn(kind, null);
                GenSpawn.Spawn(bird, at, map);
                testFlock.Add(bird);
                spawned++;
            }
            return "skyFlockSpawned=" + spawned + " skyFlockSpots=" + spots.Count + " skyFlockAnchor=" + anchor.x + "," + anchor.z
                + " " + DebugReport();
        }
    }

    // ---- stage 3: column-aware hunting and the jossur stoop ---------------------------------------------------

    // XML: <li Class="RimMandrake.TheForge.CompProperties_JossurStoop"> on the jossur.
    public class CompProperties_JossurStoop : CompProperties
    {
        public float stoopMinDistance = 8f;     // closer than this it simply runs the prey down
        public float stoopMaxDistance = 32f;    // farther than this the hunt is still a walk-up
        public int checkIntervalTicks = 20;

        public CompProperties_JossurStoop()
        {
            compClass = typeof(RM_CompJossurStoop);
        }
    }

    // A hunting jossur takes to the air for the run at its prey. Vanilla PredatorHunt does not ask to fly (its JobDef has no
    // tryStartFlying), so the comp starts the flight with the stock Pawn_FlightTracker.StartFlying (gated by the MaxFlightTime stat
    // and FlightCooldown, so a spent flier stays on the ground) and marks the job as flying. Vanilla then lands it when the
    // next job starts. Flight stats and the flightSpeedFactor are the def's own; nothing here hunts for a live frame of it.
    public class RM_CompJossurStoop : ThingComp
    {
        public CompProperties_JossurStoop Props { get { return (CompProperties_JossurStoop)props; } }

        public override void CompTick()
        {
            base.CompTick();
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || !pawn.IsHashIntervalTick(Props.checkIntervalTicks)
                || !RM_TheForgeSettings.Active(RM_TheForgeSettings.jossurStoopEnabled))
            {
                return;
            }
            Job job = pawn.CurJob;
            if (job == null || job.def != JobDefOf.PredatorHunt || pawn.Downed || pawn.flight == null
                || pawn.flight.Flying || !pawn.flight.CanFlyNow)
            {
                return;
            }
            Pawn prey = job.targetA.Thing as Pawn;
            if (prey == null || !prey.Spawned)
            {
                return;
            }
            float dist = (pawn.Position - prey.Position).LengthHorizontal;
            if (!RM_SkyKernel.StoopBand(dist, Props.stoopMinDistance, Props.stoopMaxDistance))
            {
                return;
            }
            pawn.flight.StartFlying();
            if (pawn.flight.Flying)
            {
                job.flying = true;
                RM_MapComponent_SkyPastures c = RM_MapComponent_SkyPastures.Of(pawn.Map);
                if (c != null)
                {
                    c.StatStoops++;
                }
            }
        }
    }

    // Column-aware hunting: a column-bound predator (anything carrying the vapour-drifter comp) scores prey inside the columns
    // higher and prey out on the open ash well lower, beyond its own forage range. Vanilla BestPawnToHunt still picks, through this
    // public scoring function, so reachability, fences and the rest of vanilla's rules are untouched.
    [HarmonyPatch(typeof(FoodUtility), nameof(FoodUtility.GetPreyScoreFor))]
    [RimMandrake.Shared.PatchFeature("Forge sky column hunt", typeof(RM_TheForgeSettings), "skyColumnHuntEnabled")]
    public static class RM_Patch_ColumnPreyScore
    {
        public const float InColumnBonus = RM_SkyKernel.InColumnBonus;
        public const float OpenAshPenalty = RM_SkyKernel.OpenAshPenalty;

        public static void Postfix(Pawn predator, Pawn prey, ref float __result)
        {
            if (!RM_TheForgeSettings.Active(RM_TheForgeSettings.skyColumnHuntEnabled) || predator == null || prey == null)
            {
                return;
            }
            RM_CompVaporDrifter d = predator.TryGetComp<RM_CompVaporDrifter>();
            if (d == null || !prey.Spawned || prey.Map != predator.Map)
            {
                return;
            }
            RM_MapComponent_VaporColumns cols = predator.Map.GetComponent<RM_MapComponent_VaporColumns>();
            if (cols == null)
            {
                return;
            }
            bool inColumn = cols.InColumn(prey.Position);
            __result += RM_SkyKernel.PreyScoreDelta(inColumn, d.Props.forageRadiusBeyondColumns,
                !inColumn && d.Props.forageRadiusBeyondColumns > 0f && cols.NearestColumnCell(prey.Position, d.Props.forageRadiusBeyondColumns).IsValid);
        }
    }

    // ---- stage 5: the pasture itself ------------------------------------------------------------------------------
    // Until this stage nothing put a sky creature IN a column: EnvironmentalHazards' RM_JobGiver_ColumnWander was wired into no
    // think tree, so drifters wandered like any animal. This JobGiver sits at vanilla's Animal_PreWander tag (after needs,
    // hunting and fleeing, before the stock wander) and returns null for every pawn it does not govern, so every other animal
    // and every map without a column in reach falls through to vanilla wander the same tick.
    //   governed: a WILD (no faction) pawn carrying RM_CompVaporDrifter (fleet flier, jossur, bulloo = the ruled Fumerider)
    //             while skyColumnWanderEnabled; and an awake wild dhokkur (RM_DhokkurColumnsExtension) while dhokkurColumnsEnabled.
    //   root    : the nearest column cell within the pawn's search radius; destinations must be in a column or within the
    //             pawn's leash of one (RM_SkyKernel.WanderDestOk).
    // The dhokkur (owner card 2026-10-09: "the dhokkur gets a column behaviour"): awake in the boiling rain it walks vent to
    // vent, drinking the scald where it is thickest, so its polished tracks (RM_ForgeDhokkurWays path memory) come to run
    // between the vents. Every number INVENTED.
    public class RM_DhokkurColumnsExtension : DefModExtension
    {
        public float searchRadius = 45f;
        public float leash = 6f;
    }

    public class RM_JobGiver_SkyPastureWander : JobGiver_Wander
    {
        public RM_JobGiver_SkyPastureWander()
        {
            wanderRadius = 8f;
            ticksBetweenWandersRange = new IntRange(120, 300);
            wanderDestValidator = DestOk;
        }

        /// <summary>Whether this wander governs the pawn now, and with what search radius and leash.</summary>
        public static bool Leash(Pawn pawn, out float search, out float leash, out bool isDhokkur)
        {
            search = 0f;
            leash = 0f;
            isDhokkur = false;
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !pawn.RaceProps.Animal)
            {
                return false;
            }
            RM_CompVaporDrifter d = pawn.TryGetComp<RM_CompVaporDrifter>();
            RM_DhokkurColumnsExtension ext = d == null ? pawn.def.GetModExtension<RM_DhokkurColumnsExtension>() : null;
            RM_CompForgeCycleDormancy dorm = ext == null ? null : pawn.TryGetComp<RM_CompForgeCycleDormancy>();
            if (!RM_SkyKernel.PastureGoverns(pawn.Faction == null,
                    d != null, RM_TheForgeSettings.Active(RM_TheForgeSettings.skyColumnWanderEnabled),
                    ext != null, RM_TheForgeSettings.Active(RM_TheForgeSettings.dhokkurColumnsEnabled), dorm != null && dorm.IsSealed))
            {
                return false;
            }
            if (d != null)
            {
                search = d.Props.columnSearchRadius;
                leash = d.Props.forageRadiusBeyondColumns;
            }
            else
            {
                search = ext.searchRadius;
                leash = ext.leash;
                isDhokkur = true;
            }
            return true;
        }

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!Leash(pawn, out float search, out _, out _))
            {
                return null;
            }
            RM_MapComponent_VaporColumns cols = pawn.Map.GetComponent<RM_MapComponent_VaporColumns>();
            if (cols == null || !cols.NearestColumnCell(pawn.Position, search).IsValid)
            {
                return null; // no column in reach: the stock wander takes it
            }
            Job job = base.TryGiveJob(pawn);
            if (job != null)
            {
                RM_MapComponent_SkyPastures c = RM_MapComponent_SkyPastures.Of(pawn.Map);
                if (c != null)
                {
                    c.NotePastureWander(pawn);
                }
            }
            return job;
        }

        protected override IntVec3 GetWanderRoot(Pawn pawn)
        {
            RM_MapComponent_VaporColumns cols = pawn.Map?.GetComponent<RM_MapComponent_VaporColumns>();
            if (cols == null || !Leash(pawn, out float search, out _, out _))
            {
                return pawn.Position;
            }
            IntVec3 nearest = cols.NearestColumnCell(pawn.Position, search);
            return nearest.IsValid ? nearest : pawn.Position;
        }

        private static bool DestOk(Pawn pawn, IntVec3 dest, IntVec3 root) // engine order: (pawn, candidate, root)
        {
            RM_MapComponent_VaporColumns cols = pawn.Map?.GetComponent<RM_MapComponent_VaporColumns>();
            if (cols == null || !Leash(pawn, out _, out float leash, out _))
            {
                return true;
            }
            return AtHome(cols, dest, leash);
        }

        /// <summary>Whether a cell is home for a pawn with this leash: a column cell, or within the leash of one.</summary>
        public static bool AtHome(RM_MapComponent_VaporColumns cols, IntVec3 c, float leash)
        {
            bool inCol = cols.InColumn(c);
            return RM_SkyKernel.WanderDestOk(inCol, leash, !inCol && leash > 0f && cols.NearestColumnCell(c, leash).IsValid);
        }
    }

    // ---- stage 5b: the pasture homing -----------------------------------------------------------------------------------
    // LIVE 2026-11-04 (FORGE_SKY_PASTURES_1 A1 run): the Animal_PreWander insert alone gave a fresh flock 2 jobs in 5000 ticks.
    // Vanilla's need nodes outrank it (decompiled 1.6: JobGiver_GetRest.GetPriority gives EVERY non-humanlike priority 8 from
    // hour 22 to hour 6 at any rest level, and JobGiver_GetFood 9.5 below FoodLevelPercentageWantEat, with wild animals
    // spawning at food 0.5-0.9), so a bird that landed away from the columns slept and grazed where it landed. This node sits at
    // Animal_PreMain, ahead of the needs: a governed pawn away from home walks to a column first and then eats and sleeps in
    // the pasture; an urgent need (urgently hungry, starving, exhausted) still wins (RM_SkyKernel.HomingWanted).
    public class RM_JobGiver_SkyPastureHoming : ThinkNode_JobGiver
    {
        public float destRadius = 6f;

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_JobGiver_SkyPastureWander.Leash(pawn, out float search, out float leash, out _) || pawn.Downed)
            {
                return null;
            }
            RM_MapComponent_VaporColumns cols = pawn.Map.GetComponent<RM_MapComponent_VaporColumns>();
            if (cols == null)
            {
                return null;
            }
            bool atHome = RM_JobGiver_SkyPastureWander.AtHome(cols, pawn.Position, leash);
            IntVec3 root = atHome ? IntVec3.Invalid : cols.NearestColumnCell(pawn.Position, search);
            bool hungry = pawn.needs?.food != null && pawn.needs.food.CurCategory >= HungerCategory.UrgentlyHungry;
            bool tired = pawn.needs?.rest != null && pawn.needs.rest.CurCategory >= RestCategory.Exhausted;
            if (!RM_SkyKernel.HomingWanted(true, atHome, root.IsValid, hungry, tired))
            {
                return null;
            }
            // RandomWanderDestFor's last fallbacks drop the validator (and finally return the pawn's own cell), so the result is
            // re-checked: homing never sends a pawn anywhere that is not home, and no reachable home means no job.
            IntVec3 dest = RCellFinder.RandomWanderDestFor(pawn, root, destRadius,
                (Pawn p, IntVec3 c, IntVec3 r) => RM_JobGiver_SkyPastureWander.AtHome(cols, c, leash), Danger.Some);
            if (!dest.IsValid || dest == pawn.Position || !RM_JobGiver_SkyPastureWander.AtHome(cols, dest, leash))
            {
                dest = root;
                if (!dest.Standable(pawn.Map) || !pawn.CanReach(dest, PathEndMode.OnCell, Danger.Some))
                {
                    return null;
                }
            }
            Job job = JobMaker.MakeJob(JobDefOf.GotoWander, dest);
            job.locomotionUrgency = LocomotionUrgency.Jog;
            RM_MapComponent_SkyPastures c2 = RM_MapComponent_SkyPastures.Of(pawn.Map);
            if (c2 != null)
            {
                c2.NotePastureHoming(pawn);
            }
            return job;
        }
    }
}
