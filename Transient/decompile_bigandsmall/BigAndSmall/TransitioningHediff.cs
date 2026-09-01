using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class TransitioningHediff : HediffWithComps
{
	public TransitioningHediffProps properties;

	private bool? statWasActive;

	private List<TransitioningHediffProps.SeverityTrigger> SeverityTriggers { get; set; } = new List<TransitioningHediffProps.SeverityTrigger>();

	public override void ExposeData()
	{
		Scribe_Values.Look<bool?>(ref statWasActive, "TransitioningHediffProps_StatWasActive", (bool?)null, false);
		((HediffWithComps)this).ExposeData();
		TrySetup();
		for (int num = SeverityTriggers.Count - 1; num >= 0; num--)
		{
			TransitioningHediffProps.SeverityTrigger severityTrigger = SeverityTriggers[num];
			if (severityTrigger.severity < ((Hediff)this).Severity)
			{
				SeverityTriggers.Remove(severityTrigger);
			}
		}
	}

	public override void PostAdd(DamageInfo? dinfo)
	{
		((HediffWithComps)this).PostAdd(dinfo);
		TrySetup();
		TransitioningHediffProps.Trigger onHediffAdded = properties.onHediffAdded;
		if (properties.onHediffAdded != null)
		{
			DoEffects(onHediffAdded);
		}
	}

	private void TrySetup()
	{
		if (properties != null)
		{
			return;
		}
		properties = ((Def)((Hediff)this).def).GetModExtension<TransitioningHediffProps>();
		if (properties == null)
		{
			throw new Exception("TransitioningHediff class has no TransitioningHediffProps. It needs to be added to the XML.");
		}
		if (properties.onSeverity != null)
		{
			SeverityTriggers = properties.onSeverity.Where((TransitioningHediffProps.SeverityTrigger x) => true).ToList();
		}
		else
		{
			SeverityTriggers = new List<TransitioningHediffProps.SeverityTrigger>();
		}
	}

	public override void PostRemoved()
	{
		((HediffWithComps)this).PostRemoved();
		TrySetup();
		TransitioningHediffProps.Trigger onHediffRemoved = properties.onHediffRemoved;
		if (properties.onHediffAdded != null)
		{
			DoEffects(onHediffRemoved);
		}
	}

	public override void PostTick()
	{
		try
		{
			((HediffWithComps)this).PostTick();
			TrySetup();
			if (properties.onSeverity != null)
			{
				for (int num = SeverityTriggers.Count - 1; num >= 0; num--)
				{
					TransitioningHediffProps.SeverityTrigger severityTrigger = SeverityTriggers[num];
					if (((Hediff)this).Severity >= severityTrigger.severity)
					{
						DoEffects(severityTrigger.trigger);
						SeverityTriggers.Remove(severityTrigger);
					}
				}
			}
			bool? flag = null;
			if (properties.onStat != null || properties.onStatRemoved != null)
			{
				flag = ConditionalManager.TestConditionals(((Hediff)this).pawn, properties.onStat.conditionals);
			}
			if (properties.onStat != null && statWasActive != true && flag == true)
			{
				DoEffects(properties.onStat.trigger);
			}
			if (properties.onStatRemoved != null && statWasActive != false && flag == false)
			{
				DoEffects(properties.onStat.trigger);
			}
			statWasActive = flag;
		}
		catch (Exception ex)
		{
			Log.Error("Error in TransitioningHediff.PostTick: " + ex.Message + "\n" + ex.StackTrace);
		}
	}

	private void DoEffects(TransitioningHediffProps.Trigger trigger)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Expected O, but got Unknown
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Expected O, but got Unknown
		if (trigger.perfectResurrect)
		{
			ResurrectionUtility.TryResurrect(((Hediff)this).pawn, new ResurrectionParams
			{
				restoreMissingParts = true
			});
		}
		else if (trigger.resurrect)
		{
			ResurrectionUtility.TryResurrect(((Hediff)this).pawn, new ResurrectionParams
			{
				restoreMissingParts = false
			});
		}
		else if (trigger.xenoTypeToAdd != null)
		{
			GeneHelpers.AddAllXenotypeGenes(((Hediff)this).pawn, trigger.xenoTypeToAdd, ((Def)trigger.xenoTypeToAdd).label, trigger.xenogene);
		}
		else if (trigger.xenoTypeToReplace != null)
		{
			((Hediff)this).pawn.genes.SetXenotype(trigger.xenoTypeToAdd);
		}
		foreach (GeneDef gene in trigger.geneDefsToAdd)
		{
			if (!GenCollection.Any<Gene>(((Hediff)this).pawn.genes.GenesListForReading, (Predicate<Gene>)((Gene x) => ((Def)x.def).defName == ((Def)gene).defName)))
			{
				((Hediff)this).pawn.genes.AddGene(gene, trigger.xenogene);
			}
		}
		foreach (GeneDef gene2 in trigger.geneDefsToRemove)
		{
			foreach (Gene item in ((Hediff)this).pawn.genes.GenesListForReading.Where((Gene x) => ((Def)x.def).defName == ((Def)gene2).defName))
			{
				((Hediff)this).pawn.genes.RemoveGene(item);
			}
		}
		foreach (HediffDef item2 in trigger.hediffsToAdd)
		{
			((Hediff)this).pawn.health.AddHediff(item2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
		foreach (HediffDef item3 in trigger.hediffsToRemove)
		{
			item3.TryRemoveAllOfType(((Hediff)this).pawn);
		}
	}
}
