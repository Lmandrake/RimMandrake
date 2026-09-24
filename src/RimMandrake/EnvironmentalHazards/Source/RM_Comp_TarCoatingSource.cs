using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_TAR_NASTINESS_1 (item spec §1). The first real consumer of
    // RM_TarCoatingUtility: a generic ThingComp any Thing can carry to
    // splash a filth coating over the ground around it, either once on
    // spawn (a belch event's short-lived epicenter marker) or repeatedly
    // on an interval (a beast that keeps tracking while it lairs nearby).
    // Generic and RM-tier, not Sump-specific — matches this assembly's own
    // posture for every other reusable mechanism (RM_CompFloodIgniter,
    // RM_CompTimedTerrainBurn, etc.): "compiles now, a real content def
    // wires it the moment the belch event / beast set-piece is authored."
    // SUMP_TAR_BELCH_EVENT_1 (named by this item's own header as the first
    // intended consumer) is not yet a filed item as of this build — flagged
    // here rather than guessed at.
    public class CompProperties_TarCoatingSource : CompProperties
    {
        public ThingDef filthDef;

        public float radius = 3f;

        public int thicknessPerCell = 1;

        // A splash the instant this Thing spawns (a belch's epicenter
        // marker, a beast bulge the moment it surfaces). False for a Thing
        // that should only ever pulse on its own tick interval below.
        public bool splashOnSpawn = true;

        // 0 = one-shot (splashOnSpawn only, or an external caller invoking
        // Splash() directly — a belch IncidentWorker/GenStep triggering
        // this comp's Splash() once at the moment it places the marker).
        // >0 = also re-splash every this-many ticks while spawned (a beast
        // that keeps tracking tar while it sits near the surface).
        public int pulseIntervalTicks;

        public CompProperties_TarCoatingSource()
        {
            compClass = typeof(RM_Comp_TarCoatingSource);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (filthDef == null)
            {
                yield return "CompProperties_TarCoatingSource has no filthDef — this comp would do nothing.";
            }
            else if (filthDef.filth == null)
            {
                yield return "CompProperties_TarCoatingSource.filthDef (" + filthDef.defName + ") is not a Filth ThingDef (no <filth> block).";
            }

            if (radius <= 0f)
            {
                yield return "CompProperties_TarCoatingSource.radius must be > 0.";
            }
        }
    }

    public class RM_Comp_TarCoatingSource : ThingComp
    {
        public CompProperties_TarCoatingSource Props => (CompProperties_TarCoatingSource)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);

            // Only on a genuinely fresh placement, same "not on load" guard
            // every other spawn-triggered mechanism in this kit uses
            // (RM_CompLivingBoleMarker's own registration is the precedent)
            // — a save/reload must never re-splash tar that was already
            // laid down the first time this Thing spawned.
            if (Props.splashOnSpawn && !respawningAfterLoad)
            {
                Splash();
            }
        }

        public override void CompTick()
        {
            base.CompTick();

            if (Props.pulseIntervalTicks <= 0)
            {
                return;
            }

            if (!parent.Spawned)
            {
                return;
            }

            if (Find.TickManager.TicksGame % Props.pulseIntervalTicks == 0)
            {
                Splash();
            }
        }

        // Public: an external caller (a belch event's own worker, placing
        // this Thing as a short-lived epicenter marker) can invoke this
        // directly instead of waiting on spawn/tick timing.
        public void Splash()
        {
            if (!RM_EnvironmentalHazardsSettings.tarCoatingEnabled)
            {
                return; // mod option: tar-coating sources go inert; the Thing itself is untouched
            }

            if (parent?.Map == null || Props.filthDef == null)
            {
                return;
            }

            RM_TarCoatingUtility.CoatRadius(parent.Map, parent.Position, Props.radius, Props.filthDef, Props.thicknessPerCell);
        }
    }
}
