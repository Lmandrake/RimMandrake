using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompAsexualReproduction : ThingComp
{
	public int ticksInday = 60000;

	public int asexualFissionCounter;

	public CompProperties_AsexualReproduction Props => (CompProperties_AsexualReproduction)(object)base.props;

	protected int reproductionIntervalDays => Props.reproductionIntervalDays;

	protected string customString => Props.customString;

	protected bool produceEggs => Props.produceEggs;

	protected string eggDef => Props.eggDef;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<int>(ref asexualFissionCounter, "asexualFissionCounter", 0, false);
	}

	public override void CompTickInterval(int delta)
	{
		//IL_019c: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_030b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0310: Unknown result type (might be due to invalid IL or missing references)
		//IL_0214: Unknown result type (might be due to invalid IL or missing references)
		//IL_0295: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_02cb: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (((Thing)val).Map == null || !AnimalBehaviours_Settings.flagAsexualReproduction)
		{
			return;
		}
		if (ModsConfig.OdysseyActive)
		{
			Pawn_TrainingTracker training = val.training;
			if (training != null && training.HasLearned(InternalDefOf.VEF_CycleSeverance))
			{
				return;
			}
		}
		if (Props.isGreenGoo)
		{
			asexualFissionCounter += delta;
			if (asexualFissionCounter >= ticksInday * reproductionIntervalDays && ((Thing)base.parent).Map != null && ((Thing)base.parent).Map.listerThings.ThingsOfDef(ThingDef.Named(Props.GreenGooTarget)).Count < Props.GreenGooLimit)
			{
				Hediff_Pregnant.DoBirthSpawn(val, val);
				if (((Thing)val).Faction == Faction.OfPlayer)
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(Props.asexualCloningMessage, NamedArgument.op_Implicit(GenText.CapitalizeFirst(GenText.LabelIndefinite(val))))), LookTargets.op_Implicit((Thing)(object)val), MessageTypeDefOf.PositiveEvent, true);
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
			if (((Thing)val).Faction != Faction.OfPlayer || !val.ageTracker.CurLifeStage.reproductive)
			{
				return;
			}
			asexualFissionCounter += delta;
			if (asexualFissionCounter >= ticksInday * reproductionIntervalDays)
			{
				if (produceEggs)
				{
					GenSpawn.Spawn(ThingDef.Named(eggDef), ((Thing)val).Position, ((Thing)val).Map, (WipeMode)0);
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(Props.asexualEggMessage, NamedArgument.op_Implicit(GenText.CapitalizeFirst(GenText.LabelIndefinite(val))))), LookTargets.op_Implicit((Thing)(object)val), MessageTypeDefOf.PositiveEvent, true);
					asexualFissionCounter = 0;
				}
				else if (Props.convertsIntoAnotherDef)
				{
					PawnUtility.TrySpawnHatchedOrBornPawn(PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDef.Named(Props.newDef), ((Thing)val).Faction, (PawnGenerationContext)2, (PlanetTile?)PlanetTile.op_Implicit(-1), false, true, false, false, true, 1f, false, false, true, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false)), (Thing)(object)val, (IntVec3?)null);
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(Props.asexualHatchedMessage, NamedArgument.op_Implicit(GenText.CapitalizeFirst(GenText.LabelIndefinite(val))))), LookTargets.op_Implicit((Thing)(object)val), MessageTypeDefOf.PositiveEvent, true);
					asexualFissionCounter = 0;
				}
				else
				{
					Hediff_Pregnant.DoBirthSpawn(val, val);
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(Props.asexualHatchedMessage, NamedArgument.op_Implicit(GenText.CapitalizeFirst(GenText.LabelIndefinite(val))))), LookTargets.op_Implicit((Thing)(object)val), MessageTypeDefOf.PositiveEvent, true);
					asexualFissionCounter = 0;
				}
			}
		}
	}

	public override string CompInspectStringExtra()
	{
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		if (AnimalBehaviours_Settings.flagAsexualReproduction)
		{
			ThingWithComps parent = base.parent;
			Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
			if (Props.isGreenGoo)
			{
				float num = (float)asexualFissionCounter / (float)(ticksInday * reproductionIntervalDays);
				return customString + GenText.ToStringPercent(num) + " (" + reproductionIntervalDays + " days)";
			}
			if (((Thing)val).Faction == Faction.OfPlayer && val.ageTracker.CurLifeStage.reproductive)
			{
				float num2 = (float)asexualFissionCounter / (float)(ticksInday * reproductionIntervalDays);
				return customString + GenText.ToStringPercent(num2) + " (" + reproductionIntervalDays + " days)";
			}
			return "";
		}
		return TaggedString.op_Implicit(Translator.Translate("VFE_AsexualReproductionDisabled"));
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		if (DebugSettings.ShowDevGizmos && ((Thing)base.parent).Faction == Faction.OfPlayer)
		{
			yield return (Gizmo)new Command_Action
			{
				defaultLabel = "DEV: Reproduce now",
				defaultDesc = "Set asexual reproduction to trigger now",
				action = delegate
				{
					asexualFissionCounter = ticksInday * reproductionIntervalDays;
				}
			};
		}
	}
}
