using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // DESIGN_PASS DI-2 / CHILL_AIR_PUMP_1 — the air pump for the Chill floor.
    // CHILL_FIRE_BAN_1 (owner, typed): "there's no oxygen down in the sea
    // floor"; fire exists below "only where someone pumps air down". This
    // comp is that pump. It rides Odyssey's own OxygenPump (patched on by
    // Patches/RM_ChillAirPump_OxygenPump.xml) rather than a new building:
    // all DLC is assumed, the pump already reads as "puts air in a room",
    // it is already research-gated (OrbitalTech), wall-mounted and powered.
    //
    // On the Chill seabed only: while powered, switched on and not broken
    // down, it marks every cell of its SEALED room oxygenated through
    // RM_MapComponent_ChillOxygenation's per-provider ledger, so stoves,
    // fuelled heaters and torches in that room light. A room open to the
    // map edge or mostly unroofed is not served; nor is a room bigger than
    // the pooled capacity of the live pumps in it (cellsPerPump × pumps).
    // Two pumps sharing a room keep it lit until both stop.
    //
    // Air costs power: on the seabed it draws the full chillAirPumpWatts.
    // Vanilla's CompLowPowerInSpace (earlier in the comps list) drops the
    // pump to 10% wherever the room is not in vacuum, which the seabed never
    // is; this comp runs after it on the same rare tick and overrides the
    // draw. Vanilla's own "power mode: low" inspect line can therefore read
    // wrong on the seabed; this comp's own line says what it actually does.
    //
    // Off the Chill seabed it does nothing at all: the vanilla pump is
    // untouched everywhere else.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompProperties_ChillAirSupply : CompProperties
    {
        public RM_CompProperties_ChillAirSupply()
        {
            compClass = typeof(RM_CompChillAirSupply);
        }
    }

    public class RM_CompChillAirSupply : ThingComp
    {
        private CompPowerTrader power;
        private CompBreakdownable breakdown;
        private CompFlickable flick;
        private string lastState; // transient: what the inspect line says

        private RM_MapComponent_ChillOxygenation Ledger => parent.Map?.GetComponent<RM_MapComponent_ChillOxygenation>();

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            power = parent.GetComp<CompPowerTrader>();
            breakdown = parent.GetComp<CompBreakdownable>();
            flick = parent.GetComp<CompFlickable>();
        }

        /// <summary>Running on the Chill seabed with the feature on: powered, switched on, not broken down.</summary>
        public bool Live
        {
            get
            {
                if (!parent.Spawned || !RM_DivingSettings.masterEnabled || !RM_DivingSettings.chillAirPumpEnabled
                    || !RM_ChillFireGate.IsChillSeabedMap(parent.Map))
                {
                    return false;
                }
                if (power != null && !power.PowerOn)
                {
                    return false;
                }
                if (flick != null && !flick.SwitchIsOn)
                {
                    return false;
                }
                return breakdown == null || !breakdown.BrokenDown;
            }
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            Refresh();
        }

        private void Refresh()
        {
            Map map = parent.Map;
            if (map == null)
            {
                return;
            }
            bool onSeabed = RM_DivingSettings.masterEnabled && RM_DivingSettings.chillAirPumpEnabled
                && RM_ChillFireGate.IsChillSeabedMap(map);
            if (onSeabed && power != null && !power.Off)
            {
                power.PowerOutput = -RM_DivingSettings.chillAirPumpWatts; // air costs power
            }

            RM_MapComponent_ChillOxygenation ledger = Ledger;
            if (!Live)
            {
                ledger?.ClearProvider(parent);
                lastState = onSeabed ? "RM_ChillAirPump_Idle" : null;
                return;
            }

            Room room = parent.GetRoom();
            bool sealedRoom = room != null && !room.TouchesMapEdge && !room.UsesOutdoorTemperature && !room.IsDoorway;
            int cells = room?.CellCount ?? 0;
            int pumps = sealedRoom ? LivePumpsIn(room) : 0;
            if (RM_OxygenLedgerKernel.RoomServed(sealedRoom, cells, pumps, RM_DivingSettings.chillAirPumpCellsPerPump))
            {
                ledger?.SetProviderCells(parent, room.Cells);
                lastState = "RM_ChillAirPump_Serving";
            }
            else
            {
                ledger?.ClearProvider(parent);
                lastState = sealedRoom ? "RM_ChillAirPump_TooLarge" : "RM_ChillAirPump_NotSealed";
            }
        }

        private int LivePumpsIn(Room room)
        {
            int n = 0;
            foreach (Thing t in room.ContainedAndAdjacentThings)
            {
                RM_CompChillAirSupply other = t.TryGetComp<RM_CompChillAirSupply>();
                if (other != null && other.Live && t.GetRoom() == room)
                {
                    n++;
                }
            }
            return n;
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            map?.GetComponent<RM_MapComponent_ChillOxygenation>()?.ClearProvider(parent);
            base.PostDeSpawn(map, mode);
        }

        public override string CompInspectStringExtra()
        {
            if (lastState == null)
            {
                return null;
            }
            Room room = parent.Spawned ? parent.GetRoom() : null;
            return lastState.Translate(room?.CellCount ?? 0, RM_DivingSettings.chillAirPumpCellsPerPump);
        }
    }
}
