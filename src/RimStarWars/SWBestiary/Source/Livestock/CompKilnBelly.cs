using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Livestock
{
    // LIVESTOCK_STARTER_TRIO_1 - onnik's kiln-cycle feed mechanic
    // (design/Jawa/proposals/ludicrous_livestock_deep_design.md "Onnik - the
    // kiln-belly"). Doc's own numbers, not invented: 3 spaced doses over a
    // day fire a good batch; a rushed dump fires cracked/worthless ceramic;
    // underfed more than a day and the kiln cools, losing progress; ~4 days
    // between batches.
    //
    // Zero new job types: feeding is the ordinary "this animal eats this
    // food" loop (RSW_KilnClay carries CompKilnFeed, whose PostIngested
    // hook - the same vanilla Thing.Ingested -> ThingComp.PostIngested
    // pipeline CompDrug uses, confirmed against RimWorld/CompDrug.cs and
    // Verse/Thing.cs via RimSage) notifies the eater's CompKilnBelly. No
    // harvest job either - firing spawns product directly beside the animal
    // (GenPlace.TryPlaceThing, the same call CompDWPartDropper already uses
    // in this mod), so nothing waits on a colonist's Shear/Milk-style job.
    //
    // Data-tuned per the item file's own instruction ("keep it one comp,
    // data-tuned, so drassik (v2) reuses it") - every number lives in
    // CompProperties_KilnBelly, not hardcoded, so a v2 drassik-smelter comp
    // can reuse this class with its own feed/product defs and windows.
    //
    // Two implementation decisions the doc's prose doesn't pin down, made
    // here and flagged rather than hidden:
    //   1. "Spaced doses" vs "a single dump" is read as: the span between
    //      the FIRST and LAST of the 3 doses must be at least a quarter-day
    //      (rushedSpanTicks) and at most a full day (doseWindowTicks). Doses
    //      that land within a quarter-day of each other count as the dump.
    //   2. Onnik's diet is NOT restricted to RSW_KilnClay exclusively this
    //      pass (it shares the VegetarianRoughAnimal foodType so it can
    //      survive on ordinary hay/kibble if a colonist forgets to supply
    //      clay) - only eating THIS specific def registers a dose. A
    //      strict clay-exclusive diet is a tightening left for later if the
    //      owner wants it.
    //
    // NOT live-verified this pass (offline build only, per this item's own
    // precedent on karrask - see LIVESTOCK_STARTER_TRIO_1's item file).
    public class CompProperties_KilnBelly : CompProperties
    {
        public ThingDef doseFeedDef;
        public int dosesNeeded = 3;
        public int doseWindowTicks = GenDate.TicksPerDay;
        public int rushedSpanTicks = GenDate.TicksPerDay / 4;
        public int fireCooldownTicks = GenDate.TicksPerDay * 4;

        public ThingDef goodProductDef;
        public int goodProductCount = 6;
        public ThingDef badProductDef;
        public int badProductCount = 2;

        public CompProperties_KilnBelly() => compClass = typeof(CompKilnBelly);
    }

    public class CompKilnBelly : ThingComp
    {
        private CompProperties_KilnBelly Props => (CompProperties_KilnBelly)props;

        private List<int> doseTicks = new List<int>();
        private int nextFireReadyTick = -1;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Collections.Look(ref doseTicks, "doseTicks", LookMode.Value);
            Scribe_Values.Look(ref nextFireReadyTick, "nextFireReadyTick", -1);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && doseTicks == null)
            {
                doseTicks = new List<int>();
            }
        }

        // Called by CompKilnFeed.PostIngested on the feed item this pawn
        // just ate. Kept as a public entry point rather than a Notify_*
        // override because there is no vanilla "this pawn ate this def"
        // hook on Pawn itself - only on the eaten Thing's own comps.
        public void RegisterDose()
        {
            int now = Find.TickManager.TicksGame;

            // Kiln is between batches (post-fire cooldown/reheat) - this
            // feeding doesn't start a new cycle early. "you cannot
            // batch-produce by stockpiling clay and dumping it all in."
            if (now < nextFireReadyTick)
            {
                return;
            }

            // Prior partial progress went cold before this dose arrived -
            // start the count over rather than splicing a stale dose onto
            // a fresh attempt.
            if (doseTicks.Count > 0 && now - doseTicks[doseTicks.Count - 1] > Props.doseWindowTicks)
            {
                doseTicks.Clear();
            }

            doseTicks.Add(now);

            if (doseTicks.Count >= Props.dosesNeeded)
            {
                Fire(now);
            }
        }

        public override void CompTickRare()
        {
            // "The kiln cools if underfed for more than a day and must be
            // reheated from scratch" - partial progress with no dose in
            // over a day is lost silently (no product, no message; the
            // player finds out by noticing nothing ever comes out).
            if (doseTicks.Count > 0 && Find.TickManager.TicksGame - doseTicks[doseTicks.Count - 1] > Props.doseWindowTicks)
            {
                doseTicks.Clear();
            }
        }

        private void Fire(int now)
        {
            int span = doseTicks[doseTicks.Count - 1] - doseTicks[0];
            bool spaced = span >= Props.rushedSpanTicks && span <= Props.doseWindowTicks;

            ThingDef productDef = spaced ? Props.goodProductDef : Props.badProductDef;
            int count = spaced ? Props.goodProductCount : Props.badProductCount;

            if (productDef != null && count > 0 && parent.SpawnedOrAnyParentSpawned)
            {
                Thing product = ThingMaker.MakeThing(productDef);
                product.stackCount = count;
                GenPlace.TryPlaceThing(product, parent.PositionHeld, parent.MapHeld, ThingPlaceMode.Near);
            }

            doseTicks.Clear();
            nextFireReadyTick = now + Props.fireCooldownTicks;
        }
    }

    // The feed-side half: a trivial marker comp on RSW_KilnClay (or any
    // future kiln-belly feed item) that forwards the vanilla Ingested
    // pipeline to the eater's CompKilnBelly. Deliberately dumb - all the
    // decision-making lives on the animal's own comp per creature.
    public class CompProperties_KilnFeed : CompProperties
    {
        public CompProperties_KilnFeed() => compClass = typeof(CompKilnFeed);
    }

    public class CompKilnFeed : ThingComp
    {
        public override void PostIngested(Pawn ingester)
        {
            base.PostIngested(ingester);
            ingester?.TryGetComp<CompKilnBelly>()?.RegisterDose();
        }
    }
}
