using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Sarlacc
{
    /// <summary>
    /// Fork 5 — the breach is the ONLY kill. No hit-point bar (RSW_SarlaccCistern is
    /// useHitPoints=false, destroyable=false): the sole way to end a cistern is this
    /// interact-to-breach action, run from inside per the draft ("standing on the
    /// shore of level 3, with a charge"). Pattern copied from vanilla's own
    /// CompDestroyHeart (FleshmassHeart) — a CompInteractable subclass.
    ///
    /// v1 SCOPE CUT (see ThingDefs_SarlaccCistern.xml's header and the item file):
    /// this runs a SIMPLIFIED version of draft §4.4's flood/ecosystem-death/
    /// conversion sequence directly on the surface building, because the pocket-map
    /// dungeon interior (press/gallery/reservoir) this action is meant to happen
    /// inside does not exist yet anywhere in this repo. Messages describe the full
    /// sequence; only the surface puddle and the landmark conversion are mechanical.
    /// </summary>
    public class CompSarlaccCisternBreach : CompInteractable
    {
        protected override void OnInteracted(Pawn caster)
        {
            Breach(caster);
        }

        private void Breach(Pawn caster)
        {
            if (!parent.Spawned)
            {
                return;
            }
            Map map = parent.Map;
            IntVec3 pos = parent.Position;

            Messages.Message(
                caster.LabelShort.CapitalizeFirst()
              + " cuts into the sarlacc's reservoir wall. The levels flood upward — water,"
              + " not fire, this time — and the mouth overflows onto the surface.",
                new TargetInfo(pos, map),
                MessageTypeDefOf.ThreatBig);

            if (RSW_SarlaccSettings.breachFloodVisualEnabled)
            {
                ThingDef waterFilth = ThingDef.Named("Filth_Water");
                foreach (IntVec3 cell in GenRadial.RadialCellsAround(pos, 4.5f, useCenter: true))
                {
                    if (cell.InBounds(map) && cell.Standable(map))
                    {
                        FilthMaker.TryMakeFilth(cell, map, waterFilth);
                    }
                }
                Messages.Message(
                    "The struck well is exactly as big as the tanks you brought — this flood is"
                  + " cosmetic pending real water-need integration (owed, see the item file).",
                    MessageTypeDefOf.NeutralEvent);
            }

            Messages.Message(
                "The dew ring is gone. Whatever this cistern's ecosystem depended on it for is"
              + " dying with it, and the Sun-Debt holding that tithed here will not forgive"
              + " who did this.",
                MessageTypeDefOf.NegativeEvent);

            ThingDef throatDef = ThingDef.Named("RSW_SarlaccThroat");
            parent.Destroy(DestroyMode.KillFinalize);
            Thing throat = ThingMaker.MakeThing(throatDef);
            GenSpawn.Spawn(throat, pos, map);

            Messages.Message(
                "The cistern is a throat now — drained, dry, and exactly what a clan digs"
              + " archaeology out of, not what it fears.",
                new TargetInfo(pos, map),
                MessageTypeDefOf.NeutralEvent);
        }
    }
}
