using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_GENOME_ORGAN_GROWING_1 — the mechanism the item asked for:
    // "inject the genome of a colonist into one of the amoeba-like entities
    // within the contagion to produce a plethora of organs and limbs from
    // that individual." Host = AA_RedGoo (Alpha Animals' Contagion "body"
    // roster row, §4 of the_contagion.md: "the weapon's tissue... buds new
    // forms every Bloom" — the one roster entry that reads as amoeba-like
    // rather than insect/reptile/bird-like). Consumable per owner ruling
    // 2026-09-22: the host dies producing exactly one batch.
    //
    // CONTAGION_GENOME_LIMB_AND_MATCH_BONUS_1: the batch pool now includes
    // RM_GrownLeg/RM_GrownArm alongside the four vanilla organs -- "organs
    // AND LIMBS," the owner's own words on the original ruling, deferred out
    // of v1 until the limb mechanism existed.
    public static class AmoebaHostUtility
    {
        // AA_OcularJelly/etc. are all sarg.alphaanimals defNames; RedGoo is
        // the one named "the body" in the sheet's own ruled table. Looked up
        // by string so this mod carries no hard Alpha Animals dependency.
        public const string HostDefName = "AA_RedGoo";

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

        public static bool TryBeginGestation(Pawn host, int sourcePawnID, string sourcePawnName)
        {
            if (!IsEligibleHost(host))
            {
                return false;
            }
            Hediff hediff = HediffMaker.MakeHediff(RM_ContagionDefOf.RM_AmoebaGestation, host);
            (hediff as Hediff_AmoebaGestation)?.Setup(sourcePawnID, sourcePawnName);
            host.health.AddHediff(hediff);
            Messages.Message(
                "The amoeba begins gestating a batch of organs matched to " + sourcePawnName + "'s genome. It will not survive producing them.",
                host,
                MessageTypeDefOf.PositiveEvent,
                historical: false);
            return true;
        }

        // Called by Hediff_AmoebaGestation.PostTick once severity peaks.
        // The host is consumed producing exactly one batch — no long-cycle
        // reuse, per the owner's ruling (declined, not deferred).
        public static void CompleteGestation(Pawn host, int sourcePawnID, string sourcePawnName)
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
            for (int i = 0; i < count && organPool.Count > 0; i++)
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

        static RM_OrganDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_OrganDefOf));
        }
    }
}
