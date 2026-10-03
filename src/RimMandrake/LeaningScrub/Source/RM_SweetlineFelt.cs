using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // SWEETLINE_FELT_COMFORT_BUILD_1 — owner ruling R12 (2026-10-03): the felted mass of
    // everything rubbed into the bark "with the bark's resins becomes a uniquely comfortable
    // material". Spec: design/Jawa/worldbuilding/biomes/sweetline_guardian_spec.md §5.
    //
    // Engine E8: vanilla has no comfort from a material (StatDef Comfort carries only
    // StatPart_Quality; apparel has no comfort stat). Two cheap real channels:
    //   furniture  StatPart_RM_StuffComfort, appended to StatDef Comfort by a patch: +offset
    //              when the thing's Stuff carries RM_StuffComfortExtension.
    //   apparel    ThoughtWorker_RM_StuffComfortApparel (shaped like vanilla
    //              ThoughtWorker_HumanLeatherApparel): one mood stage while wearing at least
    //              one piece of such stuff, never stacked per piece.
    // Data-driven: any stuff that carries the extension gets both.
    // ════════════════════════════════════════════════════════════════════
    public class RM_StuffComfortExtension : DefModExtension
    {
        /// <summary>Added to Comfort on furniture made of this stuff.</summary>
        public float comfortOffset = 0.10f;
    }

    public class StatPart_RM_StuffComfort : StatPart
    {
        private static RM_StuffComfortExtension ExtFor(StatRequest req)
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.sweetlineFeltComfortEnabled))
            {
                return null;
            }
            ThingDef stuff = req.HasThing ? req.Thing.Stuff : req.StuffDef;
            return stuff?.GetModExtension<RM_StuffComfortExtension>();
        }

        public override void TransformValue(StatRequest req, ref float val)
        {
            RM_StuffComfortExtension ext = ExtFor(req);
            if (ext != null)
            {
                val += ext.comfortOffset;
            }
        }

        public override string ExplanationPart(StatRequest req)
        {
            RM_StuffComfortExtension ext = ExtFor(req);
            if (ext == null)
            {
                return null;
            }
            ThingDef stuff = req.HasThing ? req.Thing.Stuff : req.StuffDef;
            return stuff.LabelCap + ": +" + ext.comfortOffset.ToString("0.00");
        }
    }

    public static class RM_SweetlineFeltProof
    {
        /// <summary>
        /// Bridge proof (jawa/static_call): Comfort of `furniture` made of sweetline felt minus the
        /// same furniture made of cloth, from the real stat pipeline. "DELTA 0.10" when the part is armed.
        /// </summary>
        public static string ProofComfortDelta(ThingDef furniture)
        {
            ThingDef felt = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SweetlineWool");
            if (furniture == null || felt == null || !furniture.MadeFromStuff)
            {
                return "REFUSED: needs a stuffable furniture def and RM_SweetlineWool";
            }
            float a = furniture.GetStatValueAbstract(StatDefOf.Comfort, felt);
            float b = furniture.GetStatValueAbstract(StatDefOf.Comfort, ThingDefOf.Cloth);
            return "DELTA " + (a - b).ToString("0.00", System.Globalization.CultureInfo.InvariantCulture);
        }
    }

    public class ThoughtWorker_RM_StuffComfortApparel : ThoughtWorker
    {
        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.sweetlineFeltApparelEnabled) || p.apparel == null)
            {
                return ThoughtState.Inactive;
            }
            List<Apparel> worn = p.apparel.WornApparel;
            for (int i = 0; i < worn.Count; i++)
            {
                if (worn[i].Stuff?.GetModExtension<RM_StuffComfortExtension>() != null)
                {
                    return ThoughtState.ActiveAtStage(0, worn[i].Stuff.label);
                }
            }
            return ThoughtState.Inactive;
        }
    }
}
