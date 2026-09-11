using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    public class CompProperties_IgniteCraterOnDestroy : CompProperties
    {
        public CompProperties_IgniteCraterOnDestroy()
        {
            compClass = typeof(CompIgniteCraterOnDestroy);
        }
    }

    // Attach to whichever Thing ends up representing the ignition event --
    // "a dropped reactor core" is the concrete trigger wasteland.md §10 option 4
    // names. Local-map spectacle (fire, terrain swap, roof breach) is the war
    // lab dungeon's own build and NOT wired here; this comp's only job is to
    // fire the worldmap-tile mutation the instant its parent thing is
    // destroyed, wherever that ends up happening.
    public class CompIgniteCraterOnDestroy : ThingComp
    {
        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            WarLabCraterMutation.Ignite();
        }
    }
}
