using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 1. See CompProperties_ActiveGasEmitter for
    // the XML surface and why the parent needs tickerType Normal.
    //
    // Cadence: a manual countdown inside CompTick, matching the precedent
    // already in this codebase (RimMandrake.ProximityHatch.CompProximityHatch,
    // RimMandrake.Pits.CompPitCoverTrigger). CompTickRare is NOT usable here:
    // the engine only calls a comp's CompTickRare when the parent Thing's own
    // tickerType is Rare, and a gas emitter's parent is normally a building
    // that ticks Normal for unrelated reasons (power, fuel, refuelable).
    public class CompActiveGasEmitter : ThingComp
    {
        private int ticksUntilBurst;

        private CompPowerTrader cachedPower;
        private bool powerLookedUp;

        public CompProperties_ActiveGasEmitter Props => (CompProperties_ActiveGasEmitter)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);

            // Stagger emitters relative to each other so a field of vents
            // does not spike the frame every tickIntervalTicks in lockstep.
            if (!respawningAfterLoad)
            {
                ticksUntilBurst = Rand.RangeInclusive(1, Props.tickIntervalTicks);
            }
        }

        public override void CompTick()
        {
            base.CompTick();

            if (!parent.Spawned)
            {
                return;
            }

            if (--ticksUntilBurst > 0)
            {
                return;
            }

            ticksUntilBurst = Props.tickIntervalTicks;
            Burst();
        }

        // Split out so a bridge/quicktest can drive one deterministic burst
        // without stepping ticks and hoping the cadence lined up — the same
        // shape as CompProximityHatch.RunScan in this codebase.
        public void Burst()
        {
            if (!parent.Spawned || Props.gasType == null)
            {
                return;
            }

            Map map = parent.Map;
            if (map == null)
            {
                return;
            }

            if (Props.requiresPower && !HasPower())
            {
                return;
            }

            IntVec3 origin = parent.Position;

            if (Props.requiresUnroofed && origin.Roofed(map))
            {
                return;
            }

            foreach (IntVec3 cell in GenRadial.RadialCellsAround(origin, Props.radius, useCenter: true))
            {
                if (!cell.InBounds(map))
                {
                    continue;
                }

                if (Props.rate < 1f && !Rand.Chance(Props.rate))
                {
                    continue;
                }

                TrySpawnGasAt(cell, map);
            }
        }

        private void TrySpawnGasAt(IntVec3 cell, Map map)
        {
            // Filled() is vanilla's own "a wall/rock/solid edifice occupies
            // this cell" test — gas must not appear inside solid matter.
            if (cell.Filled(map))
            {
                return;
            }

            // Verse.Gas destroys any pre-existing gas in its cell on spawn
            // (Gas.SpawnSetup does this unconditionally). Re-spawning over an
            // identical gas every burst would therefore reset its expiry and
            // make the cloud immortal, which is not what "rate" means. Skip
            // any cell that already holds this same gas def; a DIFFERENT gas
            // def is still allowed to displace it, which is vanilla behaviour.
            List<Thing> things = cell.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i].def == Props.gasType)
                {
                    return;
                }
            }

            GenSpawn.Spawn(Props.gasType, cell, map);
        }

        private bool HasPower()
        {
            if (!powerLookedUp)
            {
                cachedPower = parent.TryGetComp<CompPowerTrader>();
                powerLookedUp = true;
            }

            return cachedPower != null && cachedPower.PowerOn;
        }

        public override string CompInspectStringExtra()
        {
            if (Props.gasType == null)
            {
                return null;
            }

            // Literal, not a translation key: this mod ships no Languages/
            // folder, and a missing key renders as a red error string in the
            // inspect pane rather than degrading quietly.
            if (Props.requiresPower && !HasPower())
            {
                return "Gas emitter: no power";
            }

            return null;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksUntilBurst, "ticksUntilBurst", 0);
        }
    }
}
