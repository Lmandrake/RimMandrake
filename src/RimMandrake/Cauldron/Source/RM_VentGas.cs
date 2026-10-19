using System.Collections.Generic;
using LudeonTK;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Cauldron
{
    // ════════════════════════════════════════════════════════════════════
    // CAULDRON_MECHANICS_BUILD_1 part 3 — THE GAS. Owner: "The gas is highly flammable with toxic smoke and should be
    // stopped. It can also be refined for valuable liquid reagents." Rulings 2026-10-15/16: Q1 "Drifting gas clouds plus
    // the native gas system already built into rimworld"; N2 by card, "A brand-new gas type".
    //
    // A NEW GAS TYPE WITHOUT TOUCHING THE OLD ONES. Verse.GasGrid stores its four gases in one packed uint per cell and has
    // no room for a fifth (see Kernel/RM_VentGasKernel.cs). So vent gas has its own byte grid on this MapComponent, moved
    // by vanilla's own rules (the kernel ports GasGrid's diffusion/dissipation verbatim and asks vanilla's
    // GasGrid.GasCanMoveTo for walls and doors), drawn by RM_SectionLayer_VentGas (a SectionLayer_Gas subclass the engine
    // instantiates for every map section on its own), and burnt into vanilla ToxGas, which then does everything tox gas
    // does (the toxic smoke). There is NO Harmony patch here and Verse.GasGrid's storage is only ever written through its
    // public AddGas: a vanilla gas or another mod's gas cannot be changed by this file (guard row: vents.vent_gas_isolated).
    //
    // DRIFT. Calm air diffuses like vanilla gas; wind (WindManager.WindSpeed) also pushes a quarter of a thick cell one
    // step along the map's drift heading, which changes once a day (RM_VentGasKernel.Heading).
    //
    // BURNING. Every 30 ticks, every Fire on the map looks at its own cell and its 8 neighbours; a cell at least
    // IgniteMin thick burns: its vent gas is consumed, vanilla ToxGas is added there (ToxFromBurn), and a Fire is set in
    // it carrying the SAME instigator, so the vexxiss fire warden (RM_CompVexxissBehaviour) goes for whoever lit the
    // first spark. The new fires are Fires too, so a cloud burns outward from the spark over a few scans.
    //
    // Maps without vents never get gas: the grid stays empty and every sweep is skipped (NonZero == 0).
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_VentGas : MapComponent
    {
        private RM_VentGasCells cells;
        private int cycleDiffusion;
        private int cycleDissipation;
        private readonly int[] order = { 0, 1, 2, 3 };
        private System.Func<int, bool> canMoveTo;
        private System.Action<int> dirty;

        // Read by validation.py through the vent's inspect string; also the dev readout.
        public int IgnitionsTotal;
        public int ToxAddedTotal;

        public RM_MapComponent_VentGas(Map map) : base(map)
        {
            cells = new RM_VentGasCells(map.Size.x, map.Size.z);
            canMoveTo = i => map.gasGrid.GasCanMoveTo(CellIndicesUtility.IndexToCell(i, map.Size.x));
            dirty = i => map.mapDrawer.MapMeshDirty(CellIndicesUtility.IndexToCell(i, map.Size.x), MapMeshFlagDefOf.Gas);
        }

        public static RM_MapComponent_VentGas For(Map map) { return map?.GetComponent<RM_MapComponent_VentGas>(); }

        // The map's drift heading right now (one seed expression for the tick and the readout below).
        public int HeadingNow => RM_VentGasKernel.Heading(Find.TickManager.TicksGame, map.uniqueID * 7919 + 17);

        // The drift chance the tick is using right now: 0 when the setting is off, else the wind law.
        public float DriftChanceNow => RM_CauldronSettings.ventGasDrifts ? RM_VentGasKernel.DriftChance(map.windManager.WindSpeed) : 0f;

        // ── jawa/static_call readouts (validation.py drift.gas_cloud_moves_along_heading) ──────────────────────
        // No other tool reads a cell's vent-gas density, so the cloud's movement had no state read. These are the read and
        // the two fixtures the row needs; each answers one text line, "REFUSED: ..." when it cannot act.

        // "total=T cells=N cx=X cz=Z heading=H wind=W chance=C ticks=K" over the square of `radius` around `center`
        // (radius < 0: the whole map). cx/cz are -1 when the window holds no gas.
        public static string CentroidOf(Map map, IntVec3 center, int radius)
        {
            RM_MapComponent_VentGas comp = For(map);
            if (comp == null) return "REFUSED: no RM_MapComponent_VentGas on this map";
            int x0 = 0, z0 = 0, x1 = map.Size.x - 1, z1 = map.Size.z - 1;
            if (radius >= 0) { x0 = center.x - radius; z0 = center.z - radius; x1 = center.x + radius; z1 = center.z + radius; }
            long total = comp.cells.CentroidIn(x0, z0, x1, z1, out double cx, out double cz, out int n);
            var inv = System.Globalization.CultureInfo.InvariantCulture;
            return string.Format(inv, "total={0} cells={1} cx={2:0.000} cz={3:0.000} heading={4} wind={5:0.000} chance={6:0.000} ticks={7}",
                total, n, cx, cz, comp.HeadingNow, map.windManager.WindSpeed, comp.DriftChanceNow, Find.TickManager.TicksGame);
        }

        // Puts `amount` of vent gas in every cell within `radius` of `center` (through AddGas, so walls refuse it as they
        // refuse the vents' own gas). "seeded=N total=T".
        public static string SeedCloud(Map map, IntVec3 center, int radius, int amount)
        {
            RM_MapComponent_VentGas comp = For(map);
            if (comp == null) return "REFUSED: no RM_MapComponent_VentGas on this map";
            if (!center.InBounds(map) || radius < 0 || radius >= GenRadial.MaxRadialPatternRadius || amount <= 0)
                return "REFUSED: bad center/radius/amount (radius 0.." + GenRadial.MaxRadialPatternRadius + ")";
            long before = comp.cells.Total();
            int n = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, radius, true))
            {
                if (!c.InBounds(map) || !map.gasGrid.GasCanMoveTo(c)) continue;
                comp.AddGas(c, amount);
                n++;
            }
            return "seeded=" + n + " total=" + (comp.cells.Total() - before);
        }

        // Empties the map's vent gas (the row's clean slate). "cleared=T".
        public static string ClearOf(Map map)
        {
            RM_MapComponent_VentGas comp = For(map);
            if (comp == null) return "REFUSED: no RM_MapComponent_VentGas on this map";
            long t = comp.cells.Total();
            comp.ClearAll();
            return "cleared=" + t;
        }

        public bool AnyGas => cells.NonZero > 0;
        public int CellsWithGas => cells.NonZero;

        public int DensityAt(IntVec3 c)
        {
            if (!c.InBounds(map)) return 0;
            return cells.Density[CellIndicesUtility.CellToIndex(c, map.Size.x)];
        }

        // Adds gas at a cell; what does not fit spills into the passable neighbours (vanilla floods 40 cells; a vent only
        // ever spills a few units, so one ring is enough), and anything left after that is lost.
        public void AddGas(IntVec3 c, int amount)
        {
            if (amount <= 0 || !c.InBounds(map) || !map.gasGrid.GasCanMoveTo(c)) return;
            int i = CellIndicesUtility.CellToIndex(c, map.Size.x);
            int over = cells.Add(i, amount);
            dirty(i);
            for (int k = 0; k < 8 && over > 0; k++)
            {
                IntVec3 n = c + GenAdj.AdjacentCells[k];
                if (!n.InBounds(map) || !map.gasGrid.GasCanMoveTo(n)) continue;
                int j = CellIndicesUtility.CellToIndex(n, map.Size.x);
                over = cells.Add(j, over);
                dirty(j);
            }
        }

        public override void MapComponentTick()
        {
            if (cells.NonZero == 0) return;
            int area = map.Area;
            List<IntVec3> random = map.cellsInRandomOrder.GetAll();
            // PROVISIONAL: half vanilla's sweep rate (vanilla diffuses area/32 and dissipates area/64 cells a tick) — the
            // vents keep this grid populated on every Cauldron map, where vanilla's grid is usually empty.
            int nDiss = Mathf.CeilToInt(area / 128f);
            for (int k = 0; k < nDiss; k++)
            {
                if (cycleDissipation >= area) cycleDissipation = 0;
                IntVec3 c = random[cycleDissipation++];
                int i = CellIndicesUtility.CellToIndex(c, map.Size.x);
                if (cells.Density[i] == 0) continue;
                if (cells.Dissipate(i, RM_VentGasKernel.DissipateStep(c.Roofed(map), c.GetVacuum(map)))) dirty(i);
                else if ((k & 7) == 0) dirty(i);   // thinning shows, at an eighth of the visits
            }

            float chance = DriftChanceNow;
            int heading = HeadingNow;
            int nDiff = Mathf.CeilToInt(area / 64f);
            for (int k = 0; k < nDiff; k++)
            {
                if (cycleDiffusion >= area) cycleDiffusion = 0;
                IntVec3 c = random[cycleDiffusion++];
                int i = CellIndicesUtility.CellToIndex(c, map.Size.x);
                if (cells.Density[i] < RM_VentGasKernel.MinDiffusion) continue;
                order.Shuffle();
                cells.DiffuseFrom(i, order, canMoveTo, dirty);
                if (chance > 0f && Rand.Chance(chance)) cells.Drift(i, heading, canMoveTo, dirty);
            }

            if (map.IsHashIntervalTick(RM_VentGasKernel.BurnScanIntervalTicks)) BurnScan();
        }

        // Every fire lights the gas in and around its cell.
        private readonly List<Fire> firesTmp = new List<Fire>();

        private void BurnScan()
        {
            if (!RM_CauldronSettings.ventGasIgnites) return;
            List<Thing> fires = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            if (fires == null || fires.Count == 0) return;
            firesTmp.Clear();
            for (int k = 0; k < fires.Count; k++) if (fires[k] is Fire f && f.Spawned) firesTmp.Add(f);
            int lit = 0;
            for (int k = 0; k < firesTmp.Count && lit < RM_VentGasKernel.MaxIgnitionsPerScan; k++)
            {
                Fire f = firesTmp[k];
                IntVec3 at = f.Position;
                for (int n = -1; n < 8 && lit < RM_VentGasKernel.MaxIgnitionsPerScan; n++)
                {
                    IntVec3 c = n < 0 ? at : at + GenAdj.AdjacentCells[n];
                    if (Ignite(c, f.instigator)) lit++;
                }
            }
        }

        // Burns one cell if it is thick enough. Public so a dev action and a future ignition source can call it.
        public bool Ignite(IntVec3 c, Thing instigator)
        {
            if (!c.InBounds(map)) return false;
            int i = CellIndicesUtility.CellToIndex(c, map.Size.x);
            if (!RM_VentGasKernel.Ignites(RM_CauldronSettings.ventGasIgnites, cells.Density[i])) return false;
            int burned = cells.Burn(i);
            dirty(i);
            IgnitionsTotal++;
            int tox = RM_VentGasKernel.ToxFromBurn(burned, RM_CauldronSettings.ventGasToxicSmoke && ModsConfig.BiotechActive);
            if (tox > 0)
            {
                map.gasGrid.AddGas(c, GasType.ToxGas, tox);
                ToxAddedTotal += tox;
            }
            FleckMaker.ThrowFireGlow(c.ToVector3Shifted(), map, 1.2f);
            // Deliberately NOT FireUtility.TryStartFireIn: that refuses cells with nothing flammable (bare ground, stone
            // floor), and burning gas burns wherever it is. With no fuel under it the fire dies down on its own.
            TerrainDef t = c.GetTerrain(map);
            if (!c.ContainsStaticFire(map) && (t == null || !t.IsWater))
            {
                Fire fire = (Fire)ThingMaker.MakeThing(ThingDefOf.Fire);
                fire.fireSize = RM_VentGasKernel.FireSize(burned);
                fire.instigator = instigator;
                GenSpawn.Spawn(fire, c, map, Rot4.North);
            }
            return true;
        }

        // Cells within `radius` of `center` holding gas, and the thickest of them (for the vent's inspect line).
        public void Survey(IntVec3 center, float radius, out int cellsWithGas, out int peak, out int toxCells)
        {
            cellsWithGas = 0; peak = 0; toxCells = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, radius, true))
            {
                if (!c.InBounds(map)) continue;
                int d = cells.Density[CellIndicesUtility.CellToIndex(c, map.Size.x)];
                if (d > 0) { cellsWithGas++; if (d > peak) peak = d; }
                if (ModsConfig.BiotechActive && map.gasGrid.DensityAt(c, GasType.ToxGas) > 0) toxCells++;
            }
        }

        public void ClearAll()
        {
            cells.Clear();
            map.mapDrawer.WholeMapChanged(MapMeshFlagDefOf.Gas);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            byte[] arr = cells.Density;
            DataExposeUtility.LookByteArray(ref arr, "rmVentGas");
            if (Scribe.mode == LoadSaveMode.LoadingVars)
            {
                cells = new RM_VentGasCells(map.Size.x, map.Size.z);
                if (arr != null && arr.Length == cells.Count) cells.Density = arr;
                cells.Recount();
            }
            Scribe_Values.Look(ref cycleDiffusion, "rmVentGasCycleDiffusion", 0);
            Scribe_Values.Look(ref cycleDissipation, "rmVentGasCycleDissipation", 0);
            Scribe_Values.Look(ref IgnitionsTotal, "rmVentGasIgnitions", 0);
            Scribe_Values.Look(ref ToxAddedTotal, "rmVentGasToxAdded", 0);
        }
    }

    // Drawn with vanilla's own gas material and mesh builder (SectionLayer_Gas.AddCell). Vanilla reads the vertex colour
    // as (smoke, tox, rot stink, deadlife) densities; vent gas is written as a smoke/tox blend so it reads as a dull
    // yellow-grey haze, unlike pure tox gas. Densities go in raw (0..255), exactly as vanilla's own layer passes them, so
    // the colour saturates the same way vanilla tox gas does. PROVISIONAL look: the visual bar "vent gas reads as a drifting cloud" is
    // judged live; the blend is the one knob.
    public class RM_SectionLayer_VentGas : SectionLayer_Gas
    {
        private const float SmokeShare = 0.35f;
        private const float ToxShare = 0.65f;

        public RM_SectionLayer_VentGas(Section section) : base(section)
        {
            relevantChangeTypes = MapMeshFlagDefOf.Gas;
        }

        private RM_MapComponent_VentGas comp;   // fetched once per Regenerate, not once per cell

        public override Vector4 DensityAt(IntVec3 cell)
        {
            if (comp == null) comp = RM_MapComponent_VentGas.For(Map);
            float d = comp == null ? 0f : comp.DensityAt(cell);
            return new Vector4(d * SmokeShare, d * ToxShare, 0f, 0f);
        }

        public override void Regenerate()
        {
            ClearSubMeshes(MeshParts.All);
            comp = RM_MapComponent_VentGas.For(Map);
            if (comp == null || !comp.AnyGas) return;
            LayerSubMesh subMesh = GetSubMesh(Mat);
            float altitude = AltitudeLayer.Gas.AltitudeFor();
            int num = section.botLeft.x;
            foreach (IntVec3 c in section.CellRect)
            {
                if (comp.DensityAt(c) > 0) AddCell(c, num, subMesh.verts.Count, subMesh, altitude);
                num++;
            }
            if (subMesh.verts.Count > 0) subMesh.FinalizeMesh(MeshParts.All);
        }
    }

    // Dev-mode actions for BENCH's live round: put gas down, light it, clear it.
    public static class RM_VentGasDebug
    {
        [DebugAction("RimMandrake", "Cauldron: vent gas 200 (radius 3)", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void AddGasHere()
        {
            Map map = Find.CurrentMap;
            var comp = RM_MapComponent_VentGas.For(map);
            if (comp == null) return;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(UI.MouseCell(), 3f, true)) comp.AddGas(c, 200);
        }

        [DebugAction("RimMandrake", "Cauldron: ignite vent gas here", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void IgniteHere()
        {
            RM_MapComponent_VentGas.For(Find.CurrentMap)?.Ignite(UI.MouseCell(), null);
        }

        [DebugAction("RimMandrake", "Cauldron: clear all vent gas", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ClearAll()
        {
            RM_MapComponent_VentGas.For(Find.CurrentMap)?.ClearAll();
        }
    }
}
