using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
{
    // ════════════════════════════════════════════════════════════════════
    // PYRELANDS_SAND_TERRAIN_YIELD_1 — "Shovel sand". The Pyrelands' RM_FE_Ground_Sand is plain terrain, not a
    // MovingDunes sandGrid drift, so the dune clear-yield never reaches it. CHOICE (recorded on the item): a DIG
    // DESIGNATION, not a terrain clear-yield -- vanilla has no clear action for natural terrain to hang a yield on.
    // Generic by data: any TerrainDef carrying RM_TerrainDigYieldExtension can be shovelled; the cell yields the
    // extension's item and becomes its `leaves` terrain (Pyrelands sand -> RM_FE_Ground_Gravel), so a sand patch is
    // a finite deposit. Work type Mining. Shape mirrors vanilla Designator_SmoothFloors + WorkGiver + JobDriver,
    // as FlowWorks' Designator_DigCanal does.
    // ════════════════════════════════════════════════════════════════════

    public class RM_TerrainDigYieldExtension : DefModExtension
    {
        public ThingDef yield;
        public int count = 5;
        public int workTicks = 400;
        public TerrainDef leaves;
    }

    [DefOf]
    public static class RM_TerrainDigDefOf
    {
        public static DesignationDef RM_ShovelTerrain;
        public static JobDef RM_ShovelTerrain_Job;

        static RM_TerrainDigDefOf() { DefOfHelper.EnsureInitializedInCtor(typeof(RM_TerrainDigDefOf)); }
    }

    public static class RM_TerrainDig
    {
        public static RM_TerrainDigYieldExtension ExtAt(IntVec3 c, Map map)
        {
            if (map == null || !c.InBounds(map)) return null;
            return c.GetTerrain(map)?.GetModExtension<RM_TerrainDigYieldExtension>();
        }

        public static int YieldCount(RM_TerrainDigYieldExtension ext) =>
            ext == null ? 0 : Mathf.Max(1, Mathf.RoundToInt(ext.count * RM_PyrelandsSettings.sandShovelYieldMultiplier));

        /// <summary>Completes a dig on one cell: spawns the yield, swaps the terrain, clears the order. Returns the
        /// stack placed (null when the cell no longer carries the extension).</summary>
        public static Thing Complete(IntVec3 c, Map map)
        {
            RM_TerrainDigYieldExtension ext = ExtAt(c, map);
            map.designationManager.TryRemoveDesignation(c, RM_TerrainDigDefOf.RM_ShovelTerrain);
            if (ext?.yield == null) return null;
            if (ext.leaves != null) map.terrainGrid.SetTerrain(c, ext.leaves);
            Thing t = ThingMaker.MakeThing(ext.yield);
            t.stackCount = YieldCount(ext);
            GenPlace.TryPlaceThing(t, c, map, ThingPlaceMode.Near, out Thing placed);
            return placed ?? t;
        }
    }

    public class Designator_RM_ShovelTerrain : Designator_Cells
    {
        public Designator_RM_ShovelTerrain()
        {
            defaultLabel = "Shovel sand";
            defaultDesc = "Dig out loose sand for glass sand. The cell is shovelled down to what lies beneath (gravel), "
                + "so a sand patch is a finite deposit. Done by miners.";
            icon = ContentFinder<Texture2D>.Get("UI/Designators/Mine", true);
            useMouseIcon = true;
            soundDragSustain = SoundDefOf.Designate_DragStandard;
            soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
            soundSucceeded = SoundDefOf.Designate_Mine;
        }

        protected override DesignationDef Designation => RM_TerrainDigDefOf.RM_ShovelTerrain;

        public override bool Visible => RM_PyrelandsSettings.sandShovelEnabled;

        public override AcceptanceReport CanDesignateCell(IntVec3 c)
        {
            if (!RM_PyrelandsSettings.sandShovelEnabled) return false;
            if (!c.InBounds(Map) || c.Fogged(Map)) return false;
            if (Map.designationManager.DesignationAt(c, Designation) != null) return "Already ordered.";
            if (RM_TerrainDig.ExtAt(c, Map)?.yield == null) return "Not loose sand.";
            if (c.GetEdifice(Map) != null) return "Must designate open ground.";
            return true;
        }

        public override void DesignateSingleCell(IntVec3 c)
        {
            Map.designationManager.AddDesignation(new Designation(c, Designation));
        }

        public override void SelectedUpdate()
        {
            GenUI.RenderMouseoverBracket();
        }
    }

    public class WorkGiver_RM_ShovelTerrain : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override IEnumerable<IntVec3> PotentialWorkCellsGlobal(Pawn pawn)
        {
            foreach (Designation d in pawn.Map.designationManager.SpawnedDesignationsOfDef(RM_TerrainDigDefOf.RM_ShovelTerrain))
            {
                yield return d.target.Cell;
            }
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false) =>
            !RM_PyrelandsSettings.sandShovelEnabled || !pawn.Map.designationManager.AnySpawnedDesignationOfDef(RM_TerrainDigDefOf.RM_ShovelTerrain);

        public override bool HasJobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
        {
            if (pawn.Map.designationManager.DesignationAt(c, RM_TerrainDigDefOf.RM_ShovelTerrain) == null) return false;
            if (RM_TerrainDig.ExtAt(c, pawn.Map)?.yield == null) return false;
            if (c.IsForbidden(pawn)) return false;
            return pawn.CanReserve(c, 1, -1, null, forced) && pawn.CanReach(c, PathEndMode.Touch, pawn.NormalMaxDanger());
        }

        public override Job JobOnCell(Pawn pawn, IntVec3 c, bool forced = false) =>
            JobMaker.MakeJob(RM_TerrainDigDefOf.RM_ShovelTerrain_Job, c);
    }

    public class JobDriver_RM_ShovelTerrain : JobDriver
    {
        private float workLeft = -1f;

        public override bool TryMakePreToilReservations(bool errorOnFailed) =>
            pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOn(() => !RM_PyrelandsSettings.sandShovelEnabled
                || Map.designationManager.DesignationAt(TargetA.Cell, RM_TerrainDigDefOf.RM_ShovelTerrain) == null);
            yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.Touch);
            Toil dig = ToilMaker.MakeToil("RM_ShovelTerrain");
            dig.initAction = delegate
            {
                RM_TerrainDigYieldExtension ext = RM_TerrainDig.ExtAt(TargetA.Cell, Map);
                workLeft = ext?.workTicks ?? 400;
            };
            dig.tickAction = delegate
            {
                float speed = pawn.GetStatValue(StatDefOf.MiningSpeed);
                workLeft -= Mathf.Max(0.1f, speed);
                pawn.skills?.Learn(SkillDefOf.Mining, 0.06f);
                if (workLeft <= 0f)
                {
                    RM_TerrainDig.Complete(TargetA.Cell, Map);
                    ReadyForNextToil();
                }
            };
            dig.defaultCompleteMode = ToilCompleteMode.Never;
            dig.WithEffect(EffecterDefOf.Mine, TargetIndex.A);
            dig.WithProgressBar(TargetIndex.A, () =>
            {
                int total = RM_TerrainDig.ExtAt(TargetA.Cell, Map)?.workTicks ?? 400;
                return 1f - Mathf.Clamp01(workLeft / total);
            });
            dig.activeSkill = () => SkillDefOf.Mining;
            yield return dig;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref workLeft, "workLeft", -1f);
        }
    }

    /// <summary>static_call proof (PYRELANDS_SAND_TERRAIN_YIELD_1): on the current map, lays a cell of
    /// RM_FE_Ground_Sand, checks the designator accepts it (and refuses with the setting off), completes the dig.
    /// "SHOVEL accepts B | offRefuses B | yield DEF xN | terrain T".</summary>
    public static class RM_TerrainDigProof
    {
        public static string ProofShovel()
        {
            Map map = Find.CurrentMap;
            TerrainDef sand = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_FE_Ground_Sand");
            if (map == null || sand == null) return "REFUSED: no map or no RM_FE_Ground_Sand";
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 30, c => c.Standable(map) && c.GetEdifice(map) == null
                    && c.GetFirstItem(map) == null && !c.Fogged(map), out IntVec3 cell))
                return "REFUSED: no clear cell";
            TerrainDef before = cell.GetTerrain(map);
            bool was = RM_PyrelandsSettings.sandShovelEnabled;
            try
            {
                map.terrainGrid.SetTerrain(cell, sand);
                var des = new Designator_RM_ShovelTerrain();
                RM_PyrelandsSettings.sandShovelEnabled = false;
                bool offRefuses = !des.CanDesignateCell(cell).Accepted;
                RM_PyrelandsSettings.sandShovelEnabled = true;
                bool accepts = des.CanDesignateCell(cell).Accepted;
                if (accepts) des.DesignateSingleCell(cell);
                Thing got = RM_TerrainDig.Complete(cell, map);
                string terrain = cell.GetTerrain(map).defName;
                bool orderGone = map.designationManager.DesignationAt(cell, RM_TerrainDigDefOf.RM_ShovelTerrain) == null;
                string res = "SHOVEL accepts " + accepts + " | offRefuses " + offRefuses + " | yield "
                    + (got == null ? "none" : got.def.defName + " x" + got.stackCount) + " | terrain " + terrain + " | orderGone " + orderGone;
                if (got != null && got.Spawned) got.Destroy();
                return res;
            }
            finally
            {
                RM_PyrelandsSettings.sandShovelEnabled = was;
                map.terrainGrid.SetTerrain(cell, before);
            }
        }
    }
}
