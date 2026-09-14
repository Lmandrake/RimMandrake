using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    //   <ThingDef>
    //     <defName>RUT_CrecheMarker</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_CrecheMarker">
    //         <despoiledManhunterFactorDurationDays>10</despoiledManhunterFactorDurationDays>
    //         <despoiledManhunterChanceFactor>1.5</despoiledManhunterChanceFactor>
    //       </li>
    //     </comps>
    //   </ThingDef>
    public class CompProperties_CrecheMarker : CompProperties
    {
        // MIASMA_MECHANICS_1 M6 §8, INVENTED per this item's own assignment
        // ("manhunter-chance factor x1.5 for 10 days — a factor, not an
        // event"). XML-configurable so a future Sump equivalent can tune
        // its own numbers without touching this class.
        public float despoiledManhunterFactorDurationDays = 10f;
        public float despoiledManhunterChanceFactor = 1.5f;

        public CompProperties_CrecheMarker()
        {
            compClass = typeof(RM_CompCrecheMarker);
        }
    }

    // MIASMA_MECHANICS_1 M6 build, §8 "everything living remembers it" —
    // the despoiled-memory mechanic. Lives on RUT_CrecheMarker (the site
    // identity RM_SetPieceElement_SpawnMarker places), not on the warden
    // pawn itself, because the marker is permanent map furniture while the
    // pawn that dies is exactly the event being remembered.
    //
    // Triggered generically via IRM_AnchorDeathListener
    // (RM_CompTerritorialAnchor.cs) — this class never assumes anything
    // about what killed the anchored pawn, only that it did. "Clearing a
    // crèche" (the spec's other named trigger) is, for this pass, the same
    // event as killing its warden: the GenStep only ever anchors the
    // warden-mother pawn to this marker (juveniles wild-spawn separately,
    // per the spec's own "Never random" note, and are not anchored to
    // anything) — distinguishing a broader "cleared the juveniles too"
    // signal is roster-content-shaped (it needs a real juvenile
    // PawnKindDef to watch for) and explicitly owed, not guessed at here;
    // owner card 3 ("marked sites only") already rules out the wider
    // "hunted in open water" case this mechanic must NOT fire on, and nothing
    // here does — only THIS marker's own anchored warden's death despoils
    // THIS marker.
    public class RM_CompCrecheMarker : ThingComp, IRM_AnchorDeathListener
    {
        private bool despoiled;

        public CompProperties_CrecheMarker Props => (CompProperties_CrecheMarker)props;

        public bool Despoiled => despoiled;

        public void Notify_AnchorPawnKilled(Pawn anchoredPawn)
        {
            Despoil();
        }

        public void Despoil()
        {
            if (despoiled)
            {
                return; // idempotent — a marker only ever despoils once
            }

            despoiled = true;

            if (!RM_EnvironmentalHazardsSettings.crecheDespoilMemoryEnabled)
            {
                return; // mod option: marker still flips visually/inspectably, no map-wide effect
            }

            Map map = parent.Map;
            RM_MapComponent_CrecheMemory memory = map?.GetComponent<RM_MapComponent_CrecheMemory>();
            if (memory == null)
            {
                return; // parent already off the map (e.g. mid-teardown) — nothing to register onto
            }

            CompProperties_CrecheMarker props = Props;
            int durationTicks = Mathf.Max(1, (int)(props.despoiledManhunterFactorDurationDays * GenDate.TicksPerDay));
            memory.RegisterDespoil(durationTicks, props.despoiledManhunterChanceFactor);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref despoiled, "despoiled", false);
        }

        public override string CompInspectStringExtra()
        {
            return despoiled ? "RUT_CrecheMarkerDespoiled".Translate() : "RUT_CrecheMarkerIntact".Translate();
        }
    }
}
