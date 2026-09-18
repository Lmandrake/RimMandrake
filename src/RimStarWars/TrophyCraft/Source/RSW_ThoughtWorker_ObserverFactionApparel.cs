using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.TrophyCraft
{
    // WYYYSCHOKK_FANG_PENDANT_1, spec option (a): a plain ThoughtWorker, no
    // Harmony, no ideoligion precept. `p` is the OBSERVER forming the
    // opinion (checked against the faction list); `otherPawn` is the WEARER
    // (checked against the apparel). Verified against vanilla's own
    // ThoughtWorker_Precept_GroinUncovered_Social, which checks otherPawn's
    // body, not p's — same p/otherPawn roles here.
    public class RSW_ThoughtWorker_ObserverFactionApparel : ThoughtWorker
    {
        protected override ThoughtState CurrentSocialStateInternal(Pawn p, Pawn otherPawn)
        {
            if (!RSW_TrophyCraftSettings.socialConsequenceEnabled)
            {
                return ThoughtState.Inactive;
            }
            if (p?.Faction?.def?.defName == null)
            {
                return ThoughtState.Inactive;
            }
            if (otherPawn?.apparel == null)
            {
                return ThoughtState.Inactive;
            }

            RSW_FactionApparelThoughtExtension ext = def.GetModExtension<RSW_FactionApparelThoughtExtension>();
            if (ext == null || ext.factionDefNames.NullOrEmpty() || ext.apparelDefName.NullOrEmpty())
            {
                return ThoughtState.Inactive;
            }
            if (!ext.factionDefNames.Contains(p.Faction.def.defName))
            {
                return ThoughtState.Inactive;
            }

            ThingDef apparelDef = DefDatabase<ThingDef>.GetNamedSilentFail(ext.apparelDefName);
            if (apparelDef == null)
            {
                return ThoughtState.Inactive;
            }
            if (!otherPawn.apparel.WornApparel.Any((Apparel a) => a.def == apparelDef))
            {
                return ThoughtState.Inactive;
            }

            return ThoughtState.ActiveAtStage(0);
        }
    }

    // A single global +opinion multiplier (Mod Settings slider) applied on
    // top of the ThoughtDef's own baseOpinionOffset. thoughtClass is set to
    // this subclass rather than vanilla Thought_SituationalSocial for
    // exactly this hook.
    public class RSW_Thought_ObserverBraveFang : Thought_SituationalSocial
    {
        public override float OpinionOffset()
        {
            return base.OpinionOffset() * RSW_TrophyCraftSettings.opinionMultiplier;
        }
    }
}
