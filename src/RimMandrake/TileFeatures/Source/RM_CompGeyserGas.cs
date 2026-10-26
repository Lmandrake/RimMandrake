using RimWorld;
using Verse;

namespace RimMandrake.TileFeatures
{
    public class RM_CompProperties_GeyserGas : CompProperties
    {
        public GasType gasType = GasType.ToxGas;
        public IntRange activeTicksRange = new IntRange(1500, 3000);
        public IntRange inactiveTicksRange = new IntRange(30000, 90000);
        public int gasPerRareTick = 1020;

        public RM_CompProperties_GeyserGas()
        {
            compClass = typeof(RM_CompGeyserGas);
        }
    }

    /// <summary>A natural vent: quiet for a while, then releases vanilla grid gas from its centre for a while.
    /// The parent must tick rarely (tickerType Rare).</summary>
    public class RM_CompGeyserGas : ThingComp
    {
        private bool active;
        private int ticksLeft = -1;

        public RM_CompProperties_GeyserGas Props => (RM_CompProperties_GeyserGas)props;

        public bool Active => active;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!respawningAfterLoad && ticksLeft < 0) ticksLeft = Props.inactiveTicksRange.RandomInRange;
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            Map map = parent.Map;
            if (map == null) return;
            ticksLeft -= GenTicks.TickRareInterval;
            if (ticksLeft <= 0)
            {
                active = !active;
                ticksLeft = active ? Props.activeTicksRange.RandomInRange : Props.inactiveTicksRange.RandomInRange;
            }
            if (active && RM_TileFeaturesSettings.ventsEnabled && Props.gasPerRareTick > 0)
                GasUtility.AddGas(parent.OccupiedRect().CenterCell, map, Props.gasType, Props.gasPerRareTick);
        }

        public override string CompInspectStringExtra()
        {
            return active ? "Venting gas." : "Dormant.";
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref active, "rmVentActive", false);
            Scribe_Values.Look(ref ticksLeft, "rmVentTicksLeft", -1);
        }
    }
}
