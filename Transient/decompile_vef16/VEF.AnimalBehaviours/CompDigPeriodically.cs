using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompDigPeriodically : ThingComp
{
	private Effecter effecter;

	public bool diggingOn = true;

	public CompProperties_DigPeriodically Props => (CompProperties_DigPeriodically)(object)base.props;

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		foreach (Gizmo item in _003C_003En__0())
		{
			yield return item;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (!ModsConfig.OdysseyActive)
		{
			yield break;
		}
		Pawn_TrainingTracker training = val.training;
		if (training == null || !training.HasLearned(InternalDefOf.VEF_DiggingDiscipline))
		{
			yield break;
		}
		if (diggingOn)
		{
			yield return (Gizmo)new Command_Action
			{
				action = delegate
				{
					diggingOn = false;
				},
				hotKey = KeyBindingDefOf.Misc2,
				defaultDesc = TaggedString.op_Implicit(Translator.Translate("VEF_DisableDiggingDesc")),
				icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Abilities/VEF_DiggingDiscipline", true),
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("VEF_DisableDigging"))
			};
		}
		else
		{
			yield return (Gizmo)new Command_Action
			{
				action = delegate
				{
					diggingOn = true;
				},
				hotKey = KeyBindingDefOf.Misc2,
				defaultDesc = TaggedString.op_Implicit(Translator.Translate("VEF_EnableDiggingDesc")),
				icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Abilities/VEF_DiggingDiscipline", true),
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("VEF_EnableDigging"))
			};
		}
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<bool>(ref diggingOn, "diggingOn", true, false);
	}

	public override void CompTickInterval(int delta)
	{
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0176: Unknown result type (might be due to invalid IL or missing references)
		//IL_0332: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0311: Unknown result type (might be due to invalid IL or missing references)
		//IL_0316: Unknown result type (might be due to invalid IL or missing references)
		//IL_031a: Unknown result type (might be due to invalid IL or missing references)
		//IL_020d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0382: Unknown result type (might be due to invalid IL or missing references)
		//IL_0389: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		if (!AnimalBehaviours_Settings.flagDigPeriodically || !Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.ticksToDig, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (diggingOn)
		{
			if (((Thing)val).Map == null || !RestUtility.Awake(val) || val.Downed || val.Dead || (Props.onlyWhenTamed && (!Props.onlyWhenTamed || ((Thing)val).Faction == null || !((Thing)val).Faction.IsPlayer)) || (Props.onlyDigIfPolluted && (!Props.onlyDigIfPolluted || !GridsUtility.IsPolluted(((Thing)val).Position, ((Thing)val).Map))) || !GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map).affordances.Contains(VEFDefOf.Diggable))
			{
				return;
			}
			string text = "";
			int num = 1;
			ThingDef val2 = null;
			if (!Props.digBiomeRocks)
			{
				text = GenCollection.RandomElement<string>((IEnumerable<string>)Props.customThingToDig);
				int index = Props.customThingToDig.IndexOf(text);
				num = Props.customAmountToDig[index];
				val2 = ThingDef.Named(text);
			}
			else
			{
				num = Props.customAmountToDigIfRocksOrBricks;
				IEnumerable<ThingDef> enumerable = Find.World.NaturalRockTypesIn(((Thing)base.parent).Map.Tile);
				List<ThingDef> list = new List<ThingDef>();
				foreach (ThingDef item in enumerable)
				{
					list.Add(item.building.mineableThing);
				}
				val2 = (Props.digBiomeBricks ? GenCollection.FirstOrFallback<ThingDefCountClass>((IEnumerable<ThingDefCountClass>)GenCollection.RandomElementWithFallback<ThingDef>(Find.World.NaturalRockTypesIn(((Thing)base.parent).Map.Tile), (ThingDef)null).building.mineableThing.butcherProducts, (ThingDefCountClass)null).thingDef : GenCollection.RandomElementWithFallback<ThingDef>(Find.World.NaturalRockTypesIn(((Thing)base.parent).Map.Tile), (ThingDef)null).building.mineableThing);
			}
			Thing val3;
			if (Props.resultIsCorpse)
			{
				val3 = (Thing)(object)PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDef.Named(text), (Faction)null, (PawnGenerationContext)2, (PlanetTile?)null, false, false, false, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
				val3.Kill((DamageInfo?)null, (Hediff)null);
				IntVec3 val4 = CellFinder.StandableCellNear(((Thing)base.parent).Position, ((Thing)base.parent).Map, 1f, (Predicate<IntVec3>)null);
				GenSpawn.Spawn(val3, val4, ((Thing)base.parent).Map, (WipeMode)0);
			}
			else
			{
				val3 = GenSpawn.Spawn(val2, ((Thing)val).Position, ((Thing)val).Map, (WipeMode)0);
				val3.stackCount = num;
			}
			if (Props.spawnForbidden)
			{
				ForbidUtility.SetForbidden(val3, true, false);
			}
			if (effecter == null)
			{
				effecter = EffecterDefOf.Mine.Spawn();
			}
			effecter.Trigger(TargetInfo.op_Implicit((Thing)(object)val), TargetInfo.op_Implicit(val3), -1);
			return;
		}
		if (ModsConfig.OdysseyActive)
		{
			Pawn_TrainingTracker training = val.training;
			if (training != null && training.HasLearned(InternalDefOf.VEF_DiggingDiscipline))
			{
				return;
			}
		}
		diggingOn = true;
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((ThingComp)this).CompGetGizmosExtra();
	}
}
