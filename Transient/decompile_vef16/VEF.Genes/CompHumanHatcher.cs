using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Genes;

public class CompHumanHatcher : ThingComp
{
	private float gestateProgress;

	public Pawn hatcheeParent;

	public Pawn otherParent;

	public Faction hatcheeFaction;

	public List<GeneDef> motherGenes = new List<GeneDef>();

	public List<GeneDef> fatherGenes = new List<GeneDef>();

	public bool maleDominant;

	public bool femaleDominant;

	public CompProperties_HumanHatcher Props => (CompProperties_HumanHatcher)(object)base.props;

	private CompTemperatureRuinable FreezerComp => base.parent.GetComp<CompTemperatureRuinable>();

	public bool TemperatureDamaged
	{
		get
		{
			if (FreezerComp != null)
			{
				return FreezerComp.Ruined;
			}
			return false;
		}
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<float>(ref gestateProgress, "gestateProgress", 0f, false);
		Scribe_Values.Look<bool>(ref maleDominant, "maleDominant", false, false);
		Scribe_Values.Look<bool>(ref femaleDominant, "femaleDominant", false, false);
		Scribe_References.Look<Pawn>(ref hatcheeParent, "hatcheeParent", false);
		Scribe_References.Look<Pawn>(ref otherParent, "otherParent", false);
		Scribe_References.Look<Faction>(ref hatcheeFaction, "hatcheeFaction", false);
		Scribe_Collections.Look<GeneDef>(ref motherGenes, "motherGenes", (LookMode)4, Array.Empty<object>());
		Scribe_Collections.Look<GeneDef>(ref fatherGenes, "fatherGenes", (LookMode)4, Array.Empty<object>());
	}

	public override void CompTick()
	{
		if (!TemperatureDamaged)
		{
			float num = 1f / (Props.hatcherDaystoHatch * 60000f);
			gestateProgress += num;
			if (gestateProgress > 1f)
			{
				Hatch();
			}
		}
	}

	public void Hatch()
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0156: Unknown result type (might be due to invalid IL or missing references)
		//IL_0161: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			PawnGenerationRequest val = default(PawnGenerationRequest);
			((PawnGenerationRequest)(ref val))._002Ector(hatcheeParent.kindDef, hatcheeFaction, (PawnGenerationContext)2, (PlanetTile?)PlanetTile.op_Implicit(-1), false, false, true, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)1, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false);
			for (int i = 0; i < ((Thing)base.parent).stackCount; i++)
			{
				Pawn val2 = PawnGenerator.GeneratePawn(val);
				if (PawnUtility.TrySpawnHatchedOrBornPawn(val2, (Thing)(object)base.parent, (IntVec3?)null))
				{
					if (val2 != null)
					{
						if (hatcheeParent != null)
						{
							if (val2.playerSettings != null && hatcheeParent.playerSettings != null && ((Thing)hatcheeParent).Faction == hatcheeFaction)
							{
								val2.playerSettings.AreaRestrictionInPawnCurrentMap = hatcheeParent.playerSettings.AreaRestrictionInPawnCurrentMap;
							}
							if (val2.RaceProps.IsFlesh)
							{
								val2.relations.AddDirectRelation(PawnRelationDefOf.Parent, hatcheeParent);
							}
						}
						if (otherParent != null && (hatcheeParent == null || hatcheeParent.gender != otherParent.gender) && val2.RaceProps.IsFlesh)
						{
							val2.relations.AddDirectRelation(PawnRelationDefOf.Parent, otherParent);
						}
					}
					if (((Thing)base.parent).Spawned)
					{
						FilthMaker.TryMakeFilth(((Thing)base.parent).Position, ((Thing)base.parent).Map, ThingDefOf.Filth_AmnioticFluid, 1, (FilthSourceFlags)0, true);
					}
					Find.LetterStack.ReceiveLetter(TranslatorFormattedStringExtensions.Translate("VGE_EggHatchedLabel", NamedArgument.op_Implicit(val2.NameShortColored)), TranslatorFormattedStringExtensions.Translate("VGE_EggHatched", NamedArgument.op_Implicit(val2.NameShortColored)), LetterDefOf.PositiveEvent, LookTargets.op_Implicit(TargetInfo.op_Implicit((Thing)(object)val2)), (Faction)null, (Quest)null, (List<ThingDef>)null, (string)null, 0, true);
					if (maleDominant)
					{
						List<GeneDef> list = fatherGenes;
						if (list == null || list.Count <= 0)
						{
							continue;
						}
						foreach (GeneDef fatherGene in fatherGenes)
						{
							val2.genes.AddGene(fatherGene, false);
						}
						continue;
					}
					if (femaleDominant)
					{
						List<GeneDef> list2 = motherGenes;
						if (list2 == null || list2.Count <= 0)
						{
							continue;
						}
						foreach (GeneDef motherGene in motherGenes)
						{
							val2.genes.AddGene(motherGene, false);
						}
						continue;
					}
					Random random = new Random();
					List<GeneDef> list3 = new List<GeneDef>();
					foreach (GeneDef motherGene2 in motherGenes)
					{
						if (fatherGenes.Contains(motherGene2))
						{
							list3.Add(motherGene2);
						}
						else if (random.NextDouble() > 0.5)
						{
							list3.Add(motherGene2);
						}
					}
					foreach (GeneDef fatherGene2 in fatherGenes)
					{
						if (!motherGenes.Contains(fatherGene2) && random.NextDouble() > 0.5 && !list3.Contains(fatherGene2))
						{
							list3.Add(fatherGene2);
						}
					}
					foreach (GeneDef item in list3)
					{
						val2.genes.AddGene(item, false);
					}
				}
				else
				{
					Find.WorldPawns.PassToWorld(val2, (PawnDiscardDecideMode)2);
				}
			}
		}
		finally
		{
			((Thing)base.parent).Destroy((DestroyMode)0);
		}
	}

	public override bool AllowStackWith(Thing other)
	{
		return false;
	}

	public override void PreAbsorbStack(Thing otherStack, int count)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		float num = (float)count / (float)(((Thing)base.parent).stackCount + count);
		float num2 = ((ThingWithComps)otherStack).GetComp<CompHumanHatcher>().gestateProgress;
		gestateProgress = Mathf.Lerp(gestateProgress, num2, num);
	}

	public override void PostSplitOff(Thing piece)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		CompHumanHatcher comp = ((ThingWithComps)piece).GetComp<CompHumanHatcher>();
		comp.gestateProgress = gestateProgress;
		comp.hatcheeParent = hatcheeParent;
		comp.otherParent = otherParent;
		comp.hatcheeFaction = hatcheeFaction;
	}

	public override void PrePreTraded(TradeAction action, Pawn playerNegotiator, ITrader trader)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Invalid comparison between Unknown and I4
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Invalid comparison between Unknown and I4
		((ThingComp)this).PrePreTraded(action, playerNegotiator, trader);
		if ((int)action != 1)
		{
			if ((int)action == 2)
			{
				hatcheeFaction = trader.Faction;
			}
		}
		else
		{
			hatcheeFaction = Faction.OfPlayer;
		}
	}

	public override void PostPostGeneratedForTrader(TraderKindDef trader, PlanetTile forTile, Faction forFaction)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostPostGeneratedForTrader(trader, forTile, forFaction);
		hatcheeFaction = forFaction;
	}

	public override string CompInspectStringExtra()
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		if (!TemperatureDamaged)
		{
			return TaggedString.op_Implicit(Translator.Translate("EggProgress") + ": " + GenText.ToStringPercent(gestateProgress) + "\n" + Translator.Translate("HatchesIn") + ": " + TranslatorFormattedStringExtensions.Translate("PeriodDays", NamedArgument.op_Implicit((Props.hatcherDaystoHatch * (1f - gestateProgress)).ToString("F1"))));
		}
		return null;
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		foreach (Gizmo item in _003C_003En__0())
		{
			yield return item;
		}
		if (DebugSettings.ShowDevGizmos)
		{
			Command_Action val = new Command_Action();
			((Command)val).defaultLabel = "DEV: Finish hatching";
			val.action = delegate
			{
				gestateProgress = 1f;
			};
			yield return (Gizmo)(object)val;
		}
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((ThingComp)this).CompGetGizmosExtra();
	}
}
