using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompDigWhenHungry : ThingComp
{
	public int stopdiggingcounter;

	private Effecter effecter;

	public bool diggingOn = true;

	public CompProperties_DigWhenHungry Props => (CompProperties_DigWhenHungry)(object)base.props;

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
		//IL_0154: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0361: Unknown result type (might be due to invalid IL or missing references)
		//IL_0425: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_03f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_047f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0486: Unknown result type (might be due to invalid IL or missing references)
		//IL_028a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0313: Unknown result type (might be due to invalid IL or missing references)
		//IL_031a: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (!AnimalBehaviours_Settings.flagDigWhenHungry || ((Thing)val).Map == null || !RestUtility.Awake(val) || (Props.digOnlyOnGrowingSeason && (!Props.digOnlyOnGrowingSeason || !(((Thing)val).Map.mapTemperature.OutdoorTemp > (float)Props.minTemperature) || !(((Thing)val).Map.mapTemperature.OutdoorTemp < (float)Props.maxTemperature))))
		{
			return;
		}
		Pawn_NeedsTracker needs = val.needs;
		float? obj;
		if (needs == null)
		{
			obj = null;
		}
		else
		{
			Need_Food food = needs.food;
			obj = ((food != null) ? new float?(((Need)food).CurLevelPercentage) : ((float?)null));
		}
		float? num = obj;
		Pawn_NeedsTracker needs2 = val.needs;
		float? obj2;
		if (needs2 == null)
		{
			obj2 = null;
		}
		else
		{
			Need_Food food2 = needs2.food;
			obj2 = ((food2 != null) ? new float?(food2.PercentageThreshHungry) : ((float?)null));
		}
		if (!(num < obj2) && (!Props.digAnywayEveryXTicks || !Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.timeToDigForced, delta)))
		{
			return;
		}
		if (diggingOn)
		{
			if (!GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map).affordances.Contains(VEFDefOf.Diggable))
			{
				return;
			}
			if (stopdiggingcounter <= 0)
			{
				if (Props.acceptedTerrains != null)
				{
					if (Props.acceptedTerrains.Contains(((Def)GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map)).defName))
					{
						Thing val3;
						if (Props.isFrostmite)
						{
							PawnKindDef obj3 = PawnKindDef.Named("WildMan");
							Faction val2 = FactionUtility.DefaultFactionFrom(obj3.defaultFactionDef);
							val3 = GenSpawn.Spawn((Thing)(object)PawnGenerator.GeneratePawn(obj3, val2, (PlanetTile?)null), ((Thing)val).Position, ((Thing)val).Map, (WipeMode)0);
							val3.Kill((DamageInfo?)null, (Hediff)null);
						}
						else if (Props.customThingsToDig != null)
						{
							string text = GenCollection.RandomElement<string>((IEnumerable<string>)Props.customThingsToDig);
							int index = Props.customThingsToDig.IndexOf(text);
							int stackCount = ((Props.customAmountsToDig == null) ? Props.customAmountToDig : Props.customAmountsToDig[index]);
							val3 = GenSpawn.Spawn(ThingDef.Named(text), ((Thing)val).Position, ((Thing)val).Map, (WipeMode)0);
							val3.stackCount = stackCount;
						}
						else
						{
							val3 = GenSpawn.Spawn(ThingDef.Named(Props.customThingToDig), ((Thing)val).Position, ((Thing)val).Map, (WipeMode)0);
							val3.stackCount = Props.customAmountToDig;
						}
						if (Props.spawnForbidden)
						{
							ForbidUtility.SetForbidden(val3, true, true);
						}
						if (effecter == null)
						{
							effecter = EffecterDefOf.Mine.Spawn();
						}
						effecter.Trigger(TargetInfo.op_Implicit((Thing)(object)val), TargetInfo.op_Implicit(val3), -1);
					}
				}
				else
				{
					Thing val5;
					if (Props.isFrostmite)
					{
						PawnKindDef obj4 = PawnKindDef.Named("WildMan");
						Faction val4 = FactionUtility.DefaultFactionFrom(obj4.defaultFactionDef);
						val5 = GenSpawn.Spawn((Thing)(object)PawnGenerator.GeneratePawn(obj4, val4, (PlanetTile?)null), ((Thing)val).Position, ((Thing)val).Map, (WipeMode)0);
						val5.Kill((DamageInfo?)null, (Hediff)null);
					}
					else if (Props.customThingsToDig != null)
					{
						string text2 = GenCollection.RandomElement<string>((IEnumerable<string>)Props.customThingsToDig);
						int index2 = Props.customThingsToDig.IndexOf(text2);
						int stackCount2 = ((Props.customAmountsToDig == null) ? Props.customAmountToDig : Props.customAmountsToDig[index2]);
						val5 = GenSpawn.Spawn(ThingDef.Named(text2), ((Thing)val).Position, ((Thing)val).Map, (WipeMode)0);
						val5.stackCount = stackCount2;
					}
					else
					{
						val5 = GenSpawn.Spawn(ThingDef.Named(Props.customThingToDig), ((Thing)val).Position, ((Thing)val).Map, (WipeMode)0);
						val5.stackCount = Props.customAmountToDig;
					}
					if (Props.spawnForbidden)
					{
						ForbidUtility.SetForbidden(val5, true, true);
					}
					if (effecter == null)
					{
						effecter = EffecterDefOf.Mine.Spawn();
					}
					effecter.Trigger(TargetInfo.op_Implicit((Thing)(object)val), TargetInfo.op_Implicit(val5), -1);
				}
				stopdiggingcounter = Props.timeToDig;
			}
			stopdiggingcounter -= delta;
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
