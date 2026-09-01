using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class ThoughtWorker_AlienApperance : ThoughtWorker
{
	protected override ThoughtState CurrentSocialStateInternal(Pawn observingPawn, Pawn targetPawn)
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_017a: Unknown result type (might be due to invalid IL or missing references)
		//IL_017f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_019e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01be: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b2: Unknown result type (might be due to invalid IL or missing references)
		if (!targetPawn.RaceProps.Humanlike || !RelationsUtility.PawnsKnowEachOther(observingPawn, targetPawn))
		{
			return ThoughtState.op_Implicit(false);
		}
		if (PawnUtility.IsBiologicallyOrArtificiallyBlind(observingPawn))
		{
			return ThoughtState.op_Implicit(false);
		}
		bool flag = false;
		if (ModsConfig.IdeologyActive)
		{
			Ideo ideo = observingPawn.Ideo;
			if (ideo != null && ideo.HasPrecept(BSDefs.BS_AlienAppearanceTolerance_FullTolerance))
			{
				return ThoughtState.op_Implicit(false);
			}
			Ideo ideo2 = observingPawn.Ideo;
			flag = ideo2 != null && ideo2.HasPrecept(BSDefs.BS_AlienAppearanceTolerance_SomeTolerance);
		}
		if (observingPawn.story?.traits != null && (observingPawn.story.traits.HasTrait(TraitDefOf.Kind) || observingPawn.story.traits.HasTrait(TraitDefOf.Transhumanist)))
		{
			if (flag)
			{
				return ThoughtState.op_Implicit(false);
			}
			flag = true;
		}
		if (targetPawn.genes != null && observingPawn.genes != null)
		{
			HashSet<GeneDef> allActiveGeneDefs = GeneHelpers.GetAllActiveGeneDefs(targetPawn);
			HashSet<GeneDef> allActiveGeneDefs2 = GeneHelpers.GetAllActiveGeneDefs(observingPawn);
			AlienApperanceUtils.AlienState alienState = AlienApperanceUtils.AlienState.Neutral;
			if (allActiveGeneDefs.Contains(BSDefs.BS_AlienApperanceStandards))
			{
				alienState = AlienApperanceUtils.AlienState.VeryAlien;
			}
			else if (allActiveGeneDefs.Contains(BSDefs.BS_AlienApperanceStandards_Lesser))
			{
				alienState = AlienApperanceUtils.AlienState.LittleAlien;
			}
			AlienApperanceUtils.AlienState alienState2 = AlienApperanceUtils.AlienState.Neutral;
			if (allActiveGeneDefs2.Contains(BSDefs.BS_AlienApperanceStandards))
			{
				alienState2 = AlienApperanceUtils.AlienState.VeryAlien;
			}
			else if (allActiveGeneDefs2.Contains(BSDefs.BS_AlienApperanceStandards_Lesser))
			{
				alienState2 = AlienApperanceUtils.AlienState.LittleAlien;
			}
			if (alienState != AlienApperanceUtils.AlienState.Neutral || alienState != alienState2)
			{
				bool flag2 = alienState == AlienApperanceUtils.AlienState.VeryAlien || alienState2 == AlienApperanceUtils.AlienState.VeryAlien;
				int offset = 0;
				if (flag2 && !flag)
				{
					offset = 6;
					int num = (int)StatExtension.GetStatValue((Thing)(object)targetPawn, StatDefOf.PawnBeauty, true, -1);
					if (num > 0)
					{
						offset = 6 * num + 6;
					}
				}
				ThoughtState result = AlienApperanceUtils.GetAlienApperanceThoughtState(allActiveGeneDefs.ToList(), alienState, allActiveGeneDefs2.ToList(), alienState2, offset);
				if (flag && ((ThoughtState)(ref result)).StageIndex > 1)
				{
					if (((ThoughtState)(ref result)).StageIndex > 4 && flag2)
					{
						result = ThoughtState.ActiveAtStage(3);
					}
					else
					{
						if (((ThoughtState)(ref result)).StageIndex == 2)
						{
							return ThoughtState.op_Implicit(false);
						}
						result = ThoughtState.ActiveAtStage(2);
					}
				}
				return result;
			}
		}
		return ThoughtState.op_Implicit(false);
	}
}
