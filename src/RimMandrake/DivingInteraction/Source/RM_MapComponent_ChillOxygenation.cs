using System.Collections.Generic;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_FIRE_BAN_1 — the oxygenated-zone OVERRIDE INTERFACE.
    // 2026-10-08 (DESIGN_PASS DI-2): the pump now exists. It is Odyssey's own
    // oxygen pump carrying RM_CompChillAirSupply, which writes through
    // SetProviderCells/ClearProvider below (per-provider counts). The
    // manual SetCellOxygenated set remains for scripted routes.
    // "Fire exists below only where someone pumps air down — this is the
    // hook the war-lab burn routes hang on" (CHILL_WARLAB_ROUTES_1, not
    // this item's job to consume). This component IS that hook: nothing
    // in this item marks any cell oxygenated, but a future air-pump
    // building's comp calls this directly, e.g. from its own
    // CompTick/PostSpawnSetup/PostDeSpawn:
    //
    //   RM_MapComponent_ChillOxygenation ox = parent.Map.GetComponent<RM_MapComponent_ChillOxygenation>();
    //   ox?.SetRectOxygenated(GenRadial.RadialCellsAround(parent.Position, pumpRadius, true), true);
    //   // ... and false again on shutdown/deconstruction.
    //
    // Cheap by construction: a HashSet, empty on every map that is not
    // the Chill seabed (RM_ChillFireGate.IsIgnitionAllowed short-circuits
    // on the biome/pocket-map check before ever touching this component,
    // so an empty set on 999 other maps costs nothing beyond the
    // MapComponent's own per-map instantiation — same accepted cost as
    // MapComponent_BrineCrystallisation and MapComponent_GasSaturationTracker).
    //
    // No ticker: this is a passive data store a caller marks up and reads,
    // not a sweep. The Chill's ignition patches (Patch_ChillFireBan.cs)
    // query it once per ignition attempt, which is rare by design (that IS
    // the ban).
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_ChillOxygenation : MapComponent
    {
        private HashSet<IntVec3> oxygenatedCells = new HashSet<IntVec3>();

        // DESIGN_PASS DI-2 (CHILL_AIR_PUMP_1): cells covered by live air providers (RM_CompChillAirSupply on the
        // Odyssey oxygen pump), counted per provider so overlapping pumps never cancel. Deliberately NOT scribed:
        // every pump re-registers on its first rare tick after load, so a saved count could only double up.
        private readonly RM_OxygenLedgerKernel providers = new RM_OxygenLedgerKernel();

        public void SetProviderCells(Thing provider, IEnumerable<IntVec3> cells)
        {
            if (provider == null)
            {
                return;
            }
            List<int> idx = new List<int>();
            if (cells != null)
            {
                foreach (IntVec3 c in cells)
                {
                    if (c.InBounds(map))
                    {
                        idx.Add(map.cellIndices.CellToIndex(c));
                    }
                }
            }
            providers.Set(provider.thingIDNumber, idx);
        }

        public void ClearProvider(Thing provider)
        {
            if (provider != null)
            {
                providers.Clear(provider.thingIDNumber);
            }
        }

        public int ProviderCount => providers.ProviderCount;

        public RM_MapComponent_ChillOxygenation(Map map) : base(map)
        {
        }

        public bool IsCellOxygenated(IntVec3 c)
        {
            if (oxygenatedCells.Contains(c))
            {
                return true;
            }
            return c.InBounds(map) && providers.Covered(map.cellIndices.CellToIndex(c));
        }

        public void SetCellOxygenated(IntVec3 c, bool oxygenated)
        {
            if (oxygenated)
            {
                oxygenatedCells.Add(c);
            }
            else
            {
                oxygenatedCells.Remove(c);
            }
        }

        /// <summary>
        /// Convenience for a future pump building: mark (or clear) every
        /// cell in a region in one call, e.g. GenRadial.RadialCellsAround
        /// or a CellRect covering the pump's influence.
        /// </summary>
        public void SetRegionOxygenated(IEnumerable<IntVec3> cells, bool oxygenated)
        {
            if (cells == null)
            {
                return;
            }
            foreach (IntVec3 c in cells)
            {
                SetCellOxygenated(c, oxygenated);
            }
        }

        public int OxygenatedCellCount => oxygenatedCells.Count + providers.CoveredCellCount;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref oxygenatedCells, "oxygenatedCells", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && oxygenatedCells == null)
            {
                oxygenatedCells = new HashSet<IntVec3>();
            }
        }
    }
}
