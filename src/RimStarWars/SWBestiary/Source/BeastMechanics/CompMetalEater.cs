using System.Collections.Generic;
using Verse;

namespace RimMandrake.StarWars.SWBestiary
{
    // ════════════════════════════════════════════════════════════════════
    // PORTED_BEAST_MECHANICS_REBUILD_1 — the ferroclaw's steel diet.
    //
    // Owner, 2026-09-20: "Rebuild in our c#."
    //
    // DESERT_FAMILY_PORT_EXECUTION_1 ported Alpha Animals' AA_Terramorph to
    // RSW_Ferroclaw and dropped its VEF.AnimalBehaviours.CompProperties_EatWeirdFood,
    // which WAS the creature (it eats iron, nothing else). This is that
    // mechanic rebuilt from the donor's own source, MEASURED at
    // vendor/mod_sources/VanillaExpandedFramework-main/Source/VEF/AnimalBehaviours/
    //   Comps/CompEatWeirdFood.cs, Comps/CompProperties/CompProperties_EatWeirdFood.cs,
    //   AI/JobGivers/JobGiver_GetWeirdFood.cs, AI/JobDrivers/JobDriver_IngestWeird.cs,
    //   Harmony/JobGiver_GetFood_TryGiveJob_Patch.cs
    //
    // TWO DELIBERATE DEPARTURES from the donor, both recorded in the item:
    //
    //  1. NO STATIC REGISTRY. VEF keeps a static HashSet<Thing> of every
    //     weird-eater alive and adds/removes it in PostSpawnSetup/PostDeSpawn/
    //     PostDestroy — a set that outlives the game session. We ask the pawn
    //     for its comp instead (one comp-list lookup, only on the food-seeking
    //     path), so there is no cross-save state to leak or desync.
    //
    //  2. NO WHOLE-TREE COPY. VEF ships a 400-line clone of the vanilla Animal
    //     think tree (VEF_AnimalWeirdEater) and sets race.thinkTreeMain to it,
    //     so any later change to the vanilla tree is silently missed. We insert
    //     one node at the vanilla Animal_PreMain tag instead
    //     (Defs/DesertPort/RSW_DesertPortMechanics.xml), which needs no
    //     thinkTreeMain override at all.
    //
    // The eating behaviour itself is parity: same nutrition-per-feed, same
    // partial-destruction-of-the-stack rule, same dig-when-the-map-is-empty
    // fallback, same block on seeking ordinary food.
    // ════════════════════════════════════════════════════════════════════
    public class CompProperties_MetalEater : CompProperties
    {
        // defNames this creature will eat. A name that no loaded mod defines is
        // skipped silently — same as the donor, so a list may name modded items.
        public List<string> customThingToEat = new List<string>();

        // Nutrition gained per feed. Overrides whatever the eaten thing's own
        // nutrition would be (steel has none).
        public float nutrition = 1f;

        // true: the eaten thing is destroyed outright.
        // false: it takes percentageOfDestruction damage / loses that fraction
        //        of a full stack, and only dies when that runs it out.
        public bool fullyDestroyThing = false;
        public float percentageOfDestruction = 0.2f;

        // Deduct from the stack even for things that track hit points.
        public bool ignoreUseHitPoints = false;

        // When nothing edible is on the map and the creature is hungry, it digs
        // some up rather than starving. This is why the donor creature never
        // starves on a map with no steel.
        public bool digThingIfMapEmpty = false;
        public string thingToDigIfMapEmpty = "";
        public int customAmountToDig = 1;

        // Stop the creature seeking ordinary food (the donor's Harmony prefix).
        // Off means it grazes as well as eating metal.
        public bool blockNormalFood = true;

        public CompProperties_MetalEater()
        {
            compClass = typeof(CompMetalEater);
        }
    }

    // Marker comp. It holds no state: everything it does is read off Props by
    // the job giver, the job driver and the JobGiver_GetFood prefix.
    public class CompMetalEater : ThingComp
    {
        public CompProperties_MetalEater Props => (CompProperties_MetalEater)props;
    }
}
