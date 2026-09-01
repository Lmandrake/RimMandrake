using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI.Group;

namespace VEF.AnimalBehaviours;

public class HediffComp_AsexualReproduction : HediffComp
{
	public int ticksInday = 60000;

	public int asexualFissionCounter;

	public HediffCompProperties_AsexualReproduction Props => (HediffCompProperties_AsexualReproduction)(object)base.props;

	protected int reproductionIntervalDays => Props.reproductionIntervalDays;

	protected string customString => Props.customString;

	protected bool produceEggs => Props.produceEggs;

	protected string eggDef => Props.eggDef;

	public override string CompLabelInBracketsExtra => GetLabel();

	public override void CompExposeData()
	{
		((HediffComp)this).CompExposeData();
		Scribe_Values.Look<int>(ref asexualFissionCounter, "asexualFissionCounter", 0, false);
	}

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_0163: Unknown result type (might be due to invalid IL or missing references)
		//IL_018b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01db: Unknown result type (might be due to invalid IL or missing references)
		//IL_025c: Unknown result type (might be due to invalid IL or missing references)
		//IL_028d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0292: Unknown result type (might be due to invalid IL or missing references)
		//IL_0305: Unknown result type (might be due to invalid IL or missing references)
		//IL_0396: Unknown result type (might be due to invalid IL or missing references)
		//IL_0562: Unknown result type (might be due to invalid IL or missing references)
		//IL_0567: Unknown result type (might be due to invalid IL or missing references)
		//IL_0502: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		Pawn pawn = ((Hediff)base.parent).pawn;
		if (((Thing)pawn).Map == null)
		{
			return;
		}
		if (Props.isGreenGoo)
		{
			asexualFissionCounter += delta;
			if (asexualFissionCounter >= ticksInday * reproductionIntervalDays && ((Thing)pawn).Map != null && ((Thing)pawn).Map.listerThings.ThingsOfDef(ThingDef.Named(Props.GreenGooTarget)).Count < Props.GreenGooLimit)
			{
				Hediff_Pregnant.DoBirthSpawn(pawn, pawn);
				if (((Thing)pawn).Faction == Faction.OfPlayer)
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(Props.asexualCloningMessage, NamedArgument.op_Implicit(GenText.CapitalizeFirst(GenText.LabelIndefinite(pawn))))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.PositiveEvent, true);
				}
				asexualFissionCounter = 0;
			}
			else if (asexualFissionCounter >= ticksInday * reproductionIntervalDays)
			{
				asexualFissionCounter = 0;
			}
		}
		else
		{
			if (((Thing)pawn).Faction != Faction.OfPlayer || !pawn.ageTracker.CurLifeStage.reproductive)
			{
				return;
			}
			asexualFissionCounter += delta;
			if (asexualFissionCounter < ticksInday * reproductionIntervalDays)
			{
				return;
			}
			if (produceEggs)
			{
				GenSpawn.Spawn(ThingDef.Named(eggDef), ((Thing)pawn).Position, ((Thing)pawn).Map, (WipeMode)0);
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(Props.asexualEggMessage, NamedArgument.op_Implicit(GenText.CapitalizeFirst(GenText.LabelIndefinite(pawn))))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.PositiveEvent, true);
				asexualFissionCounter = 0;
				return;
			}
			if (Props.convertsIntoAnotherDef)
			{
				PawnUtility.TrySpawnHatchedOrBornPawn(PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDef.Named(Props.newDef), ((Thing)pawn).Faction, (PawnGenerationContext)2, (PlanetTile?)PlanetTile.op_Implicit(-1), false, true, false, false, true, 1f, false, false, true, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false)), (Thing)(object)pawn, (IntVec3?)null);
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(Props.asexualHatchedMessage, NamedArgument.op_Implicit(GenText.CapitalizeFirst(GenText.LabelIndefinite(pawn))))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.PositiveEvent, true);
				asexualFissionCounter = 0;
				return;
			}
			Pawn pawn2 = ((Hediff)base.parent).pawn;
			int num = ((pawn2.RaceProps.litterSizeCurve == null) ? 1 : Mathf.RoundToInt(Rand.ByCurve(pawn2.RaceProps.litterSizeCurve)));
			if (num < 1)
			{
				num = 1;
			}
			PawnGenerationRequest val = default(PawnGenerationRequest);
			((PawnGenerationRequest)(ref val))._002Ector(pawn2.kindDef, ((Thing)pawn2).Faction, (PawnGenerationContext)2, (PlanetTile?)PlanetTile.op_Implicit(-1), false, false, true, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)1, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false);
			Pawn val2 = null;
			for (int i = 0; i < num; i++)
			{
				val2 = PawnGenerator.GeneratePawn(val);
				if (Props.endogeneTransfer)
				{
					Pawn_GeneTracker genes = pawn2.genes;
					foreach (Gene item in (genes != null) ? genes.Endogenes : null)
					{
						Pawn_GeneTracker genes2 = val2.genes;
						if (genes2 != null)
						{
							genes2.AddGene(item.def, false);
						}
					}
					Pawn_GeneTracker genes3 = pawn2.genes;
					if (((genes3 != null) ? genes3.Xenotype : null) != null)
					{
						Pawn_GeneTracker genes4 = val2.genes;
						if (genes4 != null)
						{
							Pawn_GeneTracker genes5 = pawn2.genes;
							genes4.SetXenotype((genes5 != null) ? genes5.Xenotype : null);
						}
					}
				}
				if (PawnUtility.TrySpawnHatchedOrBornPawn(val2, (Thing)(object)pawn2, (IntVec3?)null))
				{
					if (val2.playerSettings != null && pawn2.playerSettings != null)
					{
						val2.playerSettings.AreaRestrictionInPawnCurrentMap = pawn2.playerSettings.AreaRestrictionInPawnCurrentMap;
					}
					if (val2.RaceProps.IsFlesh)
					{
						val2.relations.AddDirectRelation(PawnRelationDefOf.Parent, pawn2);
					}
					if (((Thing)pawn2).Spawned)
					{
						Lord lord = LordUtility.GetLord(pawn2);
						if (lord != null)
						{
							lord.AddPawn(val2);
						}
					}
				}
				else
				{
					Find.WorldPawns.PassToWorld(val2, (PawnDiscardDecideMode)2);
				}
				TaleRecorder.RecordTale(TaleDefOf.GaveBirth, new object[2] { pawn2, pawn });
			}
			if (((Thing)pawn2).Spawned)
			{
				FilthMaker.TryMakeFilth(((Thing)pawn2).Position, ((Thing)pawn2).Map, ThingDefOf.Filth_AmnioticFluid, GenText.LabelIndefinite(pawn2), 5, (FilthSourceFlags)0);
				if (pawn2.caller != null)
				{
					pawn2.caller.DoCall(false);
				}
				if (pawn.caller != null)
				{
					pawn.caller.DoCall(false);
				}
			}
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(Props.asexualHatchedMessage, NamedArgument.op_Implicit(GenText.CapitalizeFirst(GenText.LabelIndefinite(pawn))))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.PositiveEvent, true);
			asexualFissionCounter = 0;
		}
	}

	public string GetLabel()
	{
		Pawn pawn = ((Hediff)base.parent).pawn;
		if (Props.isGreenGoo)
		{
			float num = (float)asexualFissionCounter / (float)(ticksInday * reproductionIntervalDays);
			return customString + GenText.ToStringPercent(num) + " (" + reproductionIntervalDays + " days)";
		}
		if (((Thing)pawn).Faction == Faction.OfPlayer && pawn.ageTracker.CurLifeStage.reproductive)
		{
			float num2 = (float)asexualFissionCounter / (float)(ticksInday * reproductionIntervalDays);
			return customString + GenText.ToStringPercent(num2) + " (" + reproductionIntervalDays + " days)";
		}
		return "";
	}
}
