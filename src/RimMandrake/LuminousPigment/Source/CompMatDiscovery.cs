using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §2.3: discovery trigger for the hidden RM_DeepfireRefining
    // project. Sits on RM_Crowncarpet (the plant is Plant : ThingWithComps
    // in this engine, so it can carry a comp).
    //
    // ⚠️ DEVIATION FROM SPEC, MEASURED: the spec asks for a check "every 250
    // ticks while spawned". Plants in this engine tick at tickerType Long
    // (RimSage-verified against Plant_Ambrosia, TickLongInterval = 2000
    // ticks, ~33 real seconds) — there is no faster tick a plant receives at
    // all, so this comp checks every Long tick instead of inventing a
    // separate scheduler. A ~33s worst-case delay before the discovery
    // letter fires is not worth a custom ticking mechanism.
    public class CompProperties_MatDiscovery : CompProperties
    {
        public CompProperties_MatDiscovery()
        {
            compClass = typeof(CompMatDiscovery);
        }
    }

    public class CompMatDiscovery : ThingComp
    {
        private const int SightRadius = 20;
        private bool checkedAlready;

        public override void CompTickLong()
        {
            base.CompTickLong();
            if (checkedAlready) return;
            if (!parent.Spawned) return;

            Map map = parent.Map;
            if (map == null) return;
            if (parent.Position.Fogged(map)) return;

            GameComponent_Deepfire gc = GameComponent_Deepfire.Instance;
            if (gc == null) return;
            if (gc.matSeen)
            {
                checkedAlready = true;
                return;
            }

            foreach (Pawn pawn in map.mapPawns.FreeColonistsAndPrisonersSpawned)
            {
                if (pawn.Position.DistanceTo(parent.Position) <= SightRadius)
                {
                    gc.matSeen = true;
                    checkedAlready = true;
                    Messages.Message(
                        "Crowncarpet on the shore -- a rainbow bacterial mat, source of the pigment called deepfire.",
                        parent, MessageTypeDefOf.NeutralEvent, false);
                    return;
                }
            }
        }
    }
}
