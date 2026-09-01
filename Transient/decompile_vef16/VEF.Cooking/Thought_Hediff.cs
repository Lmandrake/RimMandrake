using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Cooking;

internal class Thought_Hediff : Thought_Memory
{
	public bool added;

	public override void ExposeData()
	{
		Scribe_Values.Look<bool>(ref added, "added", false, false);
	}

	public override float MoodOffset()
	{
		if (!added)
		{
			if (!ThoughtUtility.ThoughtNullified(((Thought)this).pawn, ((Thought)this).def))
			{
				if (((Thought)this).def.hediff != null)
				{
					((Thought)this).pawn.health.AddHediff(((Thought)this).def.hediff, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
				if (((Def)((Thought)this).def).HasModExtension<Thought_Hediff_Extension>())
				{
					Thought_Hediff_Extension modExtension = ((Def)((Thought)this).def).GetModExtension<Thought_Hediff_Extension>();
					if (modExtension.hediffToAffect != null)
					{
						BodyPartRecord val = ((Thought)this).pawn.RaceProps.body.GetPartsWithDef(modExtension.partToAffect).FirstOrDefault();
						((Thought)this).pawn.health.AddHediff(modExtension.hediffToAffect, val, (DamageInfo?)null, (DamageResult)null);
						Hediff firstHediffOfDef = ((Thought)this).pawn.health.hediffSet.GetFirstHediffOfDef(modExtension.hediffToAffect, false);
						firstHediffOfDef.Severity += modExtension.percentage;
					}
					if (modExtension.secondHediffToAffect != null)
					{
						BodyPartRecord val2 = ((Thought)this).pawn.RaceProps.body.GetPartsWithDef(modExtension.secondPartToAffect).FirstOrDefault();
						((Thought)this).pawn.health.AddHediff(modExtension.secondHediffToAffect, val2, (DamageInfo?)null, (DamageResult)null);
						Hediff firstHediffOfDef2 = ((Thought)this).pawn.health.hediffSet.GetFirstHediffOfDef(modExtension.secondHediffToAffect, false);
						firstHediffOfDef2.Severity += modExtension.secondPercentage;
					}
					if (modExtension.increaseJoy)
					{
						Pawn_NeedsTracker needs = ((Thought)this).pawn.needs;
						if (needs != null)
						{
							Need_Joy joy = needs.joy;
							if (joy != null)
							{
								joy.GainJoy(modExtension.extraJoy, JoyKindDefOf.Gluttonous);
							}
						}
					}
				}
			}
			added = true;
		}
		return ((Thought_Memory)this).MoodOffset();
	}
}
