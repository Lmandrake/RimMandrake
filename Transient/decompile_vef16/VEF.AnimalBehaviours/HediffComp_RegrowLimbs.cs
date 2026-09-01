using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_RegrowLimbs : HediffComp
{
	public HediffCompProperties_RegrowLimbs Props => (HediffCompProperties_RegrowLimbs)(object)base.props;

	public override void CompPostTick(ref float severityAdjustment)
	{
		//IL_01ec: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTick(ref severityAdjustment);
		if (Find.TickManager.TicksGame % 2500 != 0)
		{
			return;
		}
		bool flag = false;
		((Hediff)base.parent).pawn.health.hediffSet.hediffs.OfType<Hediff_Injury>().ToList();
		List<BodyPartRecord> nonMissingParts = ((Hediff)base.parent).pawn.health.hediffSet.GetNotMissingParts((BodyPartHeight)0, (BodyPartDepth)0, (BodyPartTagDef)null, (BodyPartRecord)null).ToList();
		List<BodyPartRecord> list = ((Thing)((Hediff)base.parent).pawn).def.race.body.AllParts.Where((BodyPartRecord x) => ((Hediff)base.parent).pawn.health.hediffSet.PartIsMissing(x) && nonMissingParts.Contains(x.parent) && !((Hediff)base.parent).pawn.health.hediffSet.AncestorHasDirectlyAddedParts(x)).ToList();
		if (GenCollection.Any<BodyPartRecord>(list))
		{
			BodyPartRecord val = GenCollection.RandomElement<BodyPartRecord>((IEnumerable<BodyPartRecord>)list);
			List<Hediff_MissingPart> source = ((Hediff)base.parent).pawn.health.hediffSet.hediffs.OfType<Hediff_MissingPart>().ToList();
			((Hediff)base.parent).pawn.health.RestorePart(val, (Hediff)null, true);
			List<Hediff_MissingPart> currentMissingHediffs2 = ((Hediff)base.parent).pawn.health.hediffSet.hediffs.OfType<Hediff_MissingPart>().ToList();
			foreach (Hediff_MissingPart item in source.Where((Hediff_MissingPart x) => !currentMissingHediffs2.Contains(x)))
			{
				Hediff val2 = HediffMaker.MakeHediff(Props.regeneratingHediff, ((Hediff)base.parent).pawn, ((Hediff)item).Part);
				val2.Severity = ((Hediff)item).Part.def.GetMaxHealth(((Hediff)base.parent).pawn) - 1f;
				((Hediff)base.parent).pawn.health.AddHediff(val2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
			flag = true;
		}
		if (flag)
		{
			FleckMaker.ThrowMetaIcon(((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map, FleckDefOf.HealingCross, 0.42f);
		}
	}
}
