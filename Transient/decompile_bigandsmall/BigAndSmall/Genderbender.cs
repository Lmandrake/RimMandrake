using System;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class Genderbender : CompAbilityEffect
{
	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn == null)
		{
			pawn = ((LocalTargetInfo)(ref dest)).Pawn;
		}
		if (pawn != null)
		{
			GenderBend(pawn);
		}
	}

	public static void GenderBend(Pawn pawn)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Invalid comparison between Unknown and I4
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			if ((int)pawn.gender == 1)
			{
				pawn.gender = (Gender)2;
			}
			else
			{
				pawn.gender = (Gender)1;
			}
			HumanoidPawnScaler.GetCache(pawn, forceRefresh: true);
			GenderMethods.UpdateBodyHeadAndBeardPostGenderChange(pawn, banNarrow: false, force: true);
		}
		catch (Exception ex)
		{
			Log.Error("Error when gender-bending " + ((Entity)pawn).LabelShortCap + "\n" + ex.Message + "\n" + ex.StackTrace);
		}
		pawn.Drawer.renderer.SetAllGraphicsDirty();
	}
}
