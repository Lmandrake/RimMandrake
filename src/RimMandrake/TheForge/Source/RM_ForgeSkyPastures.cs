using System.Collections.Generic;
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
            for (int i = 0; i < columnCells.Count && highlight.Count < MaxHighlightCells; i++)
            {
                IntVec3 c = ci.IndexToCell(columnCells[i]);
                if ((c - at).LengthHorizontalSquared <= r2)
                {
                    highlight.Add(c);
                }
            }
        }

        public string DebugReport()
        {
            return "skyColumnCells=" + columnCells.Count + " skyPolls=" + StatPolls + " skyDirtyBursts=" + StatDirtyBursts
                + " skyMotesLive=" + motes.Count + " skyMotesSpawned=" + StatMotesSpawned + " skyFlecks=" + StatFlecks
                + " skyStoops=" + StatStoops + " skyHighlightCells=" + highlight.Count
                + " skyGridPrinted=" + SectionLayer_RM_SkyColumns.LastPrintedCells;
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
}
