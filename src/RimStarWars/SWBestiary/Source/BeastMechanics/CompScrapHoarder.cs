using System.Collections.Generic;
using Verse;

namespace RimMandrake.StarWars.SWBestiary
{
    // ════════════════════════════════════════════════════════════════════
    // SHRUBLAND_SCRAPNEST_BIRDS_1 — the scrap-nest bird's hoarding drive.
    //
    // design/Jawa/worldbuilding/biomes/arid_shrubland.md §4: "The bird-analogs
    // are scavengers too: they line their nests in the vine with glittering
    // scrap — wire, lens-glass, chips of hull — beautiful creations, and a
    // treasure worth seeking for a Jawa."
    //
    // ══ WHAT WAS SURVEYED BEFORE ANY OF THIS WAS WRITTEN ═════════════════
    // The item suggested vanilla's `JobGiver_ScarabsToObelisk` or a
    // squirrel-style hoard as a model. MEASURED against the decompiled 1.6
    // source: NEITHER EXISTS. There is no `JobGiver_ScarabsToObelisk`
    // (0 hits), and no vanilla animal hoards anything — the closest vanilla
    // gets to "an animal made a lootable structure" is `Hive`, which does not
    // haul: it SPAWNS insect jelly in place (`CompProperties_Spawner`) and
    // pays out `killedLeavings` when smashed.
    //
    // So this splits along that measured line, and it is why the build is
    // small:
    //   * the nest AND its restock are pure vanilla defs — the Hive pattern,
    //     no C# at all (Defs/ScrapNest/RSW_ScrapNest.xml);
    //   * only the HAULING — a bird carrying loose scrap home — is C#, and it
    //     is assembled entirely out of vanilla's own `Toils_Haul` toils rather
    //     than a bespoke carry.
    //
    // The shape (marker comp + ThinkNode_JobGiver inserted at the vanilla
    // `Animal_PreMain` tag + JobDriver) is this assembly's own established one
    // — see CompMetalEater.cs, whose header records why an inserted node beats
    // cloning the vanilla animal think tree.
    //
    // 🔴 ONE DELIBERATE OMISSION, and it is a ruling, not an oversight.
    // arid_shrubland.md's own text ends that paragraph with "(Candidate: the
    // birds also steal from player bases.)" — a CANDIDATE, never ruled. So
    // JobGiver_HoardScrap refuses anything inside a player home area or in any
    // storage, and this comp carries no switch to turn that off. Base-stealing
    // is filed for the owner as SCRAPNEST_BIRD_BASE_THEFT_1 and must be ruled
    // before it is built.
    // ════════════════════════════════════════════════════════════════════
    public class CompProperties_ScrapHoarder : CompProperties
    {
        // The nest ThingDef this creature hauls to, and builds when it has
        // none. A name no loaded mod defines disables the whole behaviour for
        // this creature rather than erroring.
        public string nestDef = "RSW_ScrapNest";

        // defNames that count as "glittering scrap". Any name no loaded mod
        // defines is skipped silently — same convention as CompMetalEater's
        // customThingToEat, so the list may safely name modded items.
        public List<string> hoardableDefs = new List<string>();

        // How far the bird will range from itself looking for loose scrap.
        public float scrapSearchRadius = 40f;

        // A nest further than this from the bird is not "its" nest and it will
        // consider building a new one.
        public float nestSearchRadius = 40f;

        // Ceiling on nests per map, and the minimum gap between two of them.
        // Without both, a flock of five would carpet a thicket in nests.
        public int maxNestsPerMap = 4;
        public float minNestSpacing = 18f;

        // Nest-building is deliberately NOT on a random timer. A bird with no
        // nest in range builds one the next time it wants to hoard, so a
        // shrubland map has its nests soon after its birds — which is the
        // world state the sheet describes, and is also what makes this
        // testable inside one quicktest rather than one in-game season. The
        // two caps above are what stop a flock carpeting a thicket.

        public CompProperties_ScrapHoarder()
        {
            compClass = typeof(CompScrapHoarder);
        }
    }

    // Marker comp. Like CompMetalEater it holds no state: the job giver and
    // the job driver read everything off Props, so there is nothing to save
    // and nothing to desync across a load.
    public class CompScrapHoarder : ThingComp
    {
        public CompProperties_ScrapHoarder Props => (CompProperties_ScrapHoarder)props;
    }
}
