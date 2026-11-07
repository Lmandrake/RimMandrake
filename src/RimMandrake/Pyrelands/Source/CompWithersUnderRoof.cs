using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Pyrelands
{
    public class CompProperties_WithersUnderRoof : CompProperties
    {
        /// <summary>About how long a plant lasts once roofed over.</summary>
        public int witherTicks = 60000;

        public CompProperties_WithersUnderRoof()
        {
            compClass = typeof(CompWithersUnderRoof);
        }
    }

    /// <summary>
    /// The open-sky grasses wither under a roof. Every room raised on Pyrelands ground was built over a full carpet of grass, and
    /// nothing cleared it: vanilla only cuts what it is told to, and nothing sows under a roof but nothing kills either, so the
    /// floor of a new bedroom stood knee-deep in tinder (map m's room burned on day 2.9; map p's room, day 1.5). Roofed, the
    /// grass now loses its hit points over about a day and is gone. A plant ticks only through CompTickLong.
    /// </summary>
    public class CompWithersUnderRoof : ThingComp
    {
        public CompProperties_WithersUnderRoof Props => (CompProperties_WithersUnderRoof)props;

        private bool Roofed => parent.Spawned && parent.Map != null && parent.Position.Roofed(parent.Map);

        public override void CompTickLong()
        {
            if (!PyrelandsMechanicsGate.On || !Roofed) return;
            int amount = Mathf.Max(1, Mathf.RoundToInt(parent.MaxHitPoints * (float)GenTicks.TickLongInterval / Props.witherTicks));
            parent.TakeDamage(new DamageInfo(DamageDefOf.Rotting, amount));
        }

        public override string CompInspectStringExtra()
        {
            return PyrelandsMechanicsGate.On && Roofed ? "RM_WithersUnderRoof".Translate().Resolve() : null;
        }
    }
}
