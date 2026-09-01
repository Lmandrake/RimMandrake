using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class DraculStageProgression : HediffWithComps
{
	public override void PostAdd(DamageInfo? dinfo)
	{
		((HediffWithComps)this).PostAdd(dinfo);
	}

	public override void PostRemoved()
	{
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f4: Unknown result type (might be due to invalid IL or missing references)
		((HediffWithComps)this).PostRemoved();
		int num = 0;
		foreach (HediffComp comp in base.comps)
		{
			HediffComp_Disappears val = (HediffComp_Disappears)(object)((comp is HediffComp_Disappears) ? comp : null);
			if (val != null)
			{
				num = val.ticksToDisappear;
			}
		}
		if (num > 50000)
		{
			Log.Message($"Dracul Stage Progression Removed from {((Hediff)this).pawn.Name} with {num} ticks remaining because it was insufficient to cause a change in stage.");
			return;
		}
		IEnumerable<Gene> source = from x in ((Hediff)this).pawn.GetAllActiveGenes()
			where x is Gene_Deathrest
			select x;
		int num2 = 0;
		if (source.Count() > 0)
		{
			num2 = ((Gene_Deathrest)source.First()).DeathrestCapacity;
		}
		int item = DraculStageExtension.TryGetDraculStage(((Hediff)this).pawn).stage;
		Pawn_GeneTracker genes = ((Hediff)this).pawn.genes;
		float? obj;
		if (genes == null)
		{
			obj = null;
		}
		else
		{
			Gene_Hemogen firstGeneOfType = genes.GetFirstGeneOfType<Gene_Hemogen>();
			obj = ((firstGeneOfType != null) ? new float?(((Gene_Resource)firstGeneOfType).Value) : ((float?)null));
		}
		float? num3 = obj;
		if (((Hediff)this).pawn.IsPrisoner || ((Hediff)this).pawn.IsSlave || SanguophageUtility.ShouldBeDeathrestingOrInComaInsteadOfDead(((Hediff)this).pawn) || (double?)num3 < 0.75)
		{
			DraculStageProgression draculStageProgression = (DraculStageProgression)(object)HediffMaker.MakeHediff(BSDefs.VU_DraculAge, ((Hediff)this).pawn, (BodyPartRecord)null);
			int ticksToDisappear = 60000;
			foreach (HediffComp comp2 in ((HediffWithComps)draculStageProgression).comps)
			{
				HediffComp_Disappears val2 = (HediffComp_Disappears)(object)((comp2 is HediffComp_Disappears) ? comp2 : null);
				if (val2 != null)
				{
					val2.ticksToDisappear = ticksToDisappear;
				}
			}
			((Hediff)this).pawn.health.AddHediff((Hediff)(object)draculStageProgression, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			return;
		}
		string targetXenoType = "VU_Dracul";
		switch (item)
		{
		case 0:
			targetXenoType = "VU_Dracul_Spawn";
			break;
		case 1:
			targetXenoType = "VU_Dracul";
			break;
		case 2:
			targetXenoType = "VU_Dracul_Mature";
			break;
		case 3:
			targetXenoType = "VU_Dracul_Progenitor";
			break;
		default:
			Log.Warning("Failed to set Dracul Stage. Defaulting to " + targetXenoType);
			break;
		}
		IEnumerable<XenotypeDef> source2 = DefDatabase<XenotypeDef>.AllDefsListForReading.Where((XenotypeDef x) => ((Def)x).defName == targetXenoType);
		if (source2.Count() == 1)
		{
			((Hediff)this).pawn.genes.SetXenotype(source2.First());
		}
		source = from x in ((Hediff)this).pawn.GetAllActiveGenes()
			where x is Gene_Deathrest
			select x;
		if (source.Count() > 0)
		{
			Gene_Deathrest val3 = (Gene_Deathrest)source.First();
			if (item == 3)
			{
				num2++;
			}
			if (item == 4)
			{
				num2++;
			}
			val3.OffsetCapacity(num2, true);
		}
	}
}
