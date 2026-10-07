using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_GENOME_ORGAN_GROWING_1 — the mechanism the item asked for:
    // "inject the genome of a colonist into one of the amoeba-like entities
    // within the contagion to produce a plethora of organs and limbs from
    // that individual." Host = RM_BloodyMess, the Contagion's "body" roster
    // row (§4 of the_contagion.md: "the weapon's tissue... buds new forms
    // every Bloom"), our own port of the donor AA_RedGoo per the grotesque
    // cast bible. The Wombpod's harvested sac hatches one. Consumable per owner ruling
    // 2026-09-22: the host dies producing exactly one batch.
    //
    // CONTAGION_GENOME_LIMB_AND_MATCH_BONUS_1: the batch pool now includes
    // RM_GrownLeg/RM_GrownArm alongside the four vanilla organs -- "organs
    // AND LIMBS," the owner's own words on the original ruling, deferred out
    // of v1 until the limb mechanism existed.
    public static class AmoebaHostUtility
    {
        // The sample an inject job uses: a carried Monstrous sample first, so
        // a Normal one can never be spent ahead of it. The float menu and the
        // job driver both call this, so they always agree.
        public static Thing FindSampleToInject(Pawn actor)
        {
            if (actor?.inventory == null)
            {
                return null;
            }
            Thing normal = null;
            foreach (Thing t in actor.inventory.innerContainer)
            {
                if (t.def != RM_ContagionDefOf.RM_GenomeSample)
                {
                    continue;
                }
                CompGenomeSample comp = t.TryGetComp<CompGenomeSample>();
                if (comp != null && comp.monstrous)
                {
                    return t;
                }
                if (normal == null)
                {
                    normal = t;
                }
            }
            return normal;
        }

        // Our own race (Defs/ThingDefs_Races/RM_ContagionFauna.xml); matched
        // by defName string so the check stays a cheap comparison.
        public const string HostDefName = "RM_BloodyMess";

        private static readonly IntRange OrganCountRange = new IntRange(2, 4);

        public static bool IsEligibleHost(Pawn candidate)
        {
            if (candidate == null || candidate.Dead || !candidate.Spawned)
            {
                return false;
            }
            if (candidate.def == null || candidate.def.defName != HostDefName)
            {
                return false;
            }
            return !candidate.health.hediffSet.HasHediff(RM_ContagionDefOf.RM_AmoebaGestation);
        }

        public static bool TryBeginGestation(Pawn host, int sourcePawnID, string sourcePawnName, bool monstrous = false)
        {
            if (!IsEligibleHost(host))
            {
                return false;
            }
            Hediff hediff = HediffMaker.MakeHediff(RM_ContagionDefOf.RM_AmoebaGestation, host);
            Hediff_AmoebaGestation gestation = hediff as Hediff_AmoebaGestation;
            gestation?.Setup(sourcePawnID, sourcePawnName);
            if (gestation != null)
            {
                gestation.monstrous = monstrous;
            }
            host.health.AddHediff(hediff);
            Messages.Message(
                monstrous
                    ? "The amoeba begins gestating monstrous tissue. It will not survive producing a single grown limb."
                    : "The amoeba begins gestating a batch of organs matched to " + sourcePawnName + "'s genome. It will not survive producing them.",
                host,
                MessageTypeDefOf.PositiveEvent,
                historical: false);
            return true;
        }

        // Called by Hediff_AmoebaGestation.PostTick once severity peaks.
        // The host is consumed producing exactly one batch — no long-cycle
        // reuse, per the owner's ruling (declined, not deferred).
        public static void CompleteGestation(Pawn host, int sourcePawnID, string sourcePawnName, bool monstrous = false)
        {
            if (host == null || host.Dead)
            {
                return;
            }
            Map map = host.MapHeld;
            IntVec3 pos = host.PositionHeld;
            if (map == null)
            {
                // Host left the map mid-gestation (e.g. caravan/despawn) —
                // nothing to spawn into and nowhere to place it; the batch is
                // lost along with the expedition. Matches "another harvest
                // means finding and reaching another amoeba."
                return;
            }

            // CONTAGION_GROWN_LIMBS_BUILD_1: a Monstrous sample grows ONE grown
            // limb, rolled at random from the built limbs, no organs, no donor
            // stamp (so the genome-match mood bonus never applies to it).
            // With grown limbs switched off it falls through to the normal batch.
            List<ThingDef> limbPool = new List<ThingDef>
            {
                RM_OrganDefOf.RM_PillarArmItem,
                RM_OrganDefOf.RM_LashItem,
                RM_OrganDefOf.RM_EyeburstItem,
                RM_OrganDefOf.RM_CaudalSpringItem,
                RM_OrganDefOf.RM_BellowsItem
            }.Where(d => d != null).ToList();
            if (RM_DraftprintKernel.Plan(monstrous, RM_ContagionSettings.grownLimbsEnabled, limbPool.Count) == GestationPlan.OneLimb)
            {
                Thing limb = ThingMaker.MakeThing(limbPool.RandomElement());
                bool placed = GenPlace.TryPlaceThing(limb, pos, map, ThingPlaceMode.Near);
                host.Kill(null);
                if (placed)
                {
                    Messages.Message(
                        "A Contagion amoeba host has died producing a monstrous grown limb: " + limb.LabelCap + ".",
                        new LookTargets(limb),
                        MessageTypeDefOf.PositiveEvent);
                }
                return;
            }

            List<ThingDef> organPool = new List<ThingDef>
            {
                RM_OrganDefOf.Kidney,
                RM_OrganDefOf.Liver,
                RM_OrganDefOf.Lung,
                RM_OrganDefOf.Heart,
                RM_OrganDefOf.RM_GrownLeg,
                RM_OrganDefOf.RM_GrownArm
            }.Where(d => d != null).ToList();

            int count = OrganCountRange.RandomInRange;
            List<Thing> spawned = new List<Thing>();
            count = RM_DraftprintKernel.BatchSize(count, organPool.Count);
            for (int i = 0; i < count; i++)
            {
                ThingDef organDef = organPool.RandomElement();
                Thing organ = ThingMaker.MakeThing(organDef);
                CompGenomeMatched matched = organ.TryGetComp<CompGenomeMatched>();
                matched?.SetSource(sourcePawnID, sourcePawnName);
                if (GenPlace.TryPlaceThing(organ, pos, map, ThingPlaceMode.Near))
                {
                    spawned.Add(organ);
                }
            }

            // The host dies producing the batch — consumable per owner
            // ruling. Kill after spawning so pos/map are still valid.
            host.Kill(null);

            if (spawned.Count > 0)
            {
                Messages.Message(
                    "A Contagion amoeba host has died producing " + spawned.Count + " organ(s) and/or limb(s) grown from " + sourcePawnName + "'s genome.",
                    new LookTargets(spawned),
                    MessageTypeDefOf.PositiveEvent);
            }
        }
    }

    // Vanilla organ ThingDefs — resolved by convention-matched field name via
    // [DefOf], never invented as new defs of our own (see CompGenomeMatched's
    // header for why: a new ThingDef would not fit vanilla's existing
    // install-organ recipes). RM_GrownLeg/RM_GrownArm (CONTAGION_GENOME_
    // LIMB_AND_MATCH_BONUS_1) are the one exception — vanilla has no natural
    // leg/arm ThingDef to reuse at all, so those two ARE new defs of our own
    // (Defs/ThingDefs/RM_GrownLimbs.xml).
    [DefOf]
    public static class RM_OrganDefOf
    {
        public static ThingDef Kidney;
        public static ThingDef Liver;
        public static ThingDef Lung;
        public static ThingDef Heart;
        public static ThingDef RM_GrownLeg;
        public static ThingDef RM_GrownArm;
        // CONTAGION_GROWN_LIMBS_BUILD_1
        public static ThingDef RM_PillarArmItem;
        public static ThingDef RM_LashItem;
        // CONTAGION_GROWN_LIMBS_REST_1
        public static ThingDef RM_EyeburstItem;
        public static ThingDef RM_CaudalSpringItem;
        public static ThingDef RM_BellowsItem;

        static RM_OrganDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_OrganDefOf));
        }
    }
}
