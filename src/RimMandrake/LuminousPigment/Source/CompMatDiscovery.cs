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

            if (!LuminousPigmentSettings.matDiscoveryByEyeOrHand)
            {
                foreach (Pawn pawn in map.mapPawns.FreeColonistsAndPrisonersSpawned)
                {
                    if (pawn.Position.DistanceTo(parent.Position) <= SightRadius)
                    {
                        checkedAlready = MarkSeen(parent);
                        return;
                    }
                }
                return;
            }
            // MAT_DISCOVERY_SIGHT_RULE_1 PROVISIONAL (auto-decided 2026-10-09): a free colonist (never a prisoner)
            // within the radius WITH line of sight. Harvest/haul of fresh mat is the other route (CompMatVitality).
            foreach (Pawn pawn in map.mapPawns.FreeColonistsSpawned)
            {
                if (pawn.Position.DistanceTo(parent.Position) <= SightRadius
                    && GenSight.LineOfSight(pawn.Position, parent.Position, map, skipFirstCell: true))
                {
                    checkedAlready = MarkSeen(parent);
                    return;
                }
            }
        }

        /// <summary>The one discovery: sets matSeen and says so once. Returns true.</summary>
        public static bool MarkSeen(Thing at)
        {
            GameComponent_Deepfire gc = GameComponent_Deepfire.Instance;
            if (gc == null || gc.matSeen) return true;
            gc.matSeen = true;
            Messages.Message(
                "Crowncarpet on the shore -- a rainbow bacterial mat, source of the pigment called deepfire.",
                at, MessageTypeDefOf.NeutralEvent, false);
            return true;
        }
    }
}
