using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using VEF.Factions;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace VEF.Planet;

public class LordToil_SiegeCustom : LordToil
{
	private const float BaseRadiusMin = 14f;

	private const float BaseRadiusMax = 25f;

	private static readonly FloatRange NutritionRangePerRaider = new FloatRange(0.9f, 2.7f);

	private const int StartBuildingDelay = 450;

	private static readonly FloatRange BuilderCountFraction = new FloatRange(0.25f, 0.4f);

	private const int InitalShellsPerCannon = 5;

	private const int ReplenishAtShells = 4;

	private const int ShellReplenishCount = 10;

	private const int ReplenishAtMeals = 5;

	private const int MealReplenishCount = 12;

	public Dictionary<Pawn, DutyDef> rememberedDuties = new Dictionary<Pawn, DutyDef>();

	public override IntVec3 FlagLoc => ((LordToilData_Siege)Data).siegeCenter;

	private LordToilData_SiegeCustom Data => (LordToilData_SiegeCustom)(object)base.data;

	private SiegeParameterSetDef CustomParams => FactionDefExtension.Get((Def)(object)base.lord.faction.def).siegeParameterSetDef;

	private IEnumerable<Frame> Frames
	{
		get
		{
			LordToilData_SiegeCustom data = Data;
			float radSquared = (((LordToilData_Siege)data).baseRadius + 10f) * (((LordToilData_Siege)data).baseRadius + 10f);
			List<Thing> framesList = ((LordToil)this).Map.listerThings.ThingsInGroup((ThingRequestGroup)11);
			if (framesList.Count == 0)
			{
				yield break;
			}
			for (int i = 0; i < framesList.Count; i++)
			{
				Frame val = (Frame)framesList[i];
				if (((Thing)val).Faction == base.lord.faction)
				{
					IntVec3 val2 = ((Thing)val).Position - ((LordToilData_Siege)data).siegeCenter;
					if ((float)((IntVec3)(ref val2)).LengthHorizontalSquared < radSquared)
					{
						yield return val;
					}
				}
			}
		}
	}

	private IEnumerable<Building_TurretGun> Artillery => ((LordToil)this).Map.listerThings.ThingsInGroup((ThingRequestGroup)10).Where(delegate(Thing b)
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		if (b.Faction == base.lord.faction)
		{
			IntVec3 position = b.Position;
			if (((IntVec3)(ref position)).InHorDistOf(((LordToil)this).FlagLoc, ((LordToilData_Siege)Data).baseRadius))
			{
				return b.def.building.IsMortar;
			}
		}
		return false;
	}).Cast<Building_TurretGun>();

	public override bool ForceHighStoryDanger => true;

	public LordToil_SiegeCustom(IntVec3 siegeCenter, float blueprintPoints)
	{
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		base.data = (LordToilData)(object)new LordToilData_SiegeCustom();
		((LordToilData_Siege)Data).siegeCenter = siegeCenter;
		((LordToilData_Siege)Data).blueprintPoints = blueprintPoints;
	}

	public override void Init()
	{
		//IL_0180: Unknown result type (might be due to invalid IL or missing references)
		//IL_0185: Unknown result type (might be due to invalid IL or missing references)
		//IL_018b: Unknown result type (might be due to invalid IL or missing references)
		//IL_030d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0312: Unknown result type (might be due to invalid IL or missing references)
		//IL_0386: Unknown result type (might be due to invalid IL or missing references)
		//IL_038c: Invalid comparison between Unknown and I4
		//IL_0394: Unknown result type (might be due to invalid IL or missing references)
		//IL_0446: Unknown result type (might be due to invalid IL or missing references)
		//IL_044b: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0400: Unknown result type (might be due to invalid IL or missing references)
		((LordToil)this).Init();
		SiegeParameterSetDef customParams = CustomParams;
		((LordToilData_Siege)Data).baseRadius = Mathf.InverseLerp(14f, 25f, (float)base.lord.ownedPawns.Count / 50f);
		((LordToilData_Siege)Data).baseRadius = Mathf.Clamp(((LordToilData_Siege)Data).baseRadius, 14f, 25f);
		List<Thing> list = new List<Thing>();
		List<Blueprint_Build> list2 = CustomSiegeUtility.PlaceBlueprints(Data, ((LordToil)this).Map, base.lord.faction).ToList();
		for (int i = 0; i < list2.Count; i++)
		{
			Blueprint_Build val = list2[i];
			((LordToilData_Siege)Data).blueprints.Add((Blueprint)(object)val);
			foreach (ThingDefCountClass cost in ((Blueprint)val).TotalMaterialCost())
			{
				Thing val2 = GenCollection.FirstOrDefault<Thing>(list, (Predicate<Thing>)((Thing t) => t.def == cost.thingDef));
				if (val2 != null)
				{
					val2.stackCount += cost.count;
					continue;
				}
				Thing val3 = ThingMaker.MakeThing(cost.thingDef, (ThingDef)null);
				val3.stackCount = cost.count;
				list.Add(val3);
			}
			BuildableDef entityDefToBuild = ((Thing)val).def.entityDefToBuild;
			ThingDef val4 = (ThingDef)(object)((entityDefToBuild is ThingDef) ? entityDefToBuild : null);
			if (val4 != null)
			{
				bool flag = false;
				TechLevel techLevel = base.lord.faction.def.techLevel;
				ThingDef val5 = TurretGunUtility.TryFindRandomShellDef(val4, flag, false, true, techLevel, false, 250f, (Faction)null);
				if (val5 != null)
				{
					Thing val6 = ThingMaker.MakeThing(val5, (ThingDef)null);
					val6.stackCount = 5;
					list.Add(val6);
				}
			}
		}
		for (int j = 0; j < list.Count; j++)
		{
			list[j].stackCount = Mathf.CeilToInt((float)list[j].stackCount * Rand.Range(1f, 1.2f));
		}
		List<List<Thing>> list3 = new List<List<Thing>>();
		for (int k = 0; k < list.Count; k++)
		{
			while (list[k].stackCount > list[k].def.stackLimit)
			{
				int num = Mathf.CeilToInt((float)list[k].def.stackLimit * Rand.Range(0.9f, 0.999f));
				Thing val7 = ThingMaker.MakeThing(list[k].def, (ThingDef)null);
				val7.stackCount = num;
				Thing obj = list[k];
				obj.stackCount -= num;
				list.Add(val7);
			}
		}
		List<Thing> list4 = new List<Thing>();
		for (int l = 0; l < list.Count; l++)
		{
			list4.Add(list[l]);
			if (l % 2 == 1 || l == list.Count - 1)
			{
				list3.Add(list4);
				list4 = new List<Thing>();
			}
		}
		List<Thing> list5 = new List<Thing>();
		FloatRange val8 = NutritionRangePerRaider;
		int num2 = Mathf.RoundToInt(((FloatRange)(ref val8)).RandomInRange / StatExtension.GetStatValueAbstract((BuildableDef)(object)customParams.mealDef, StatDefOf.Nutrition, (ThingDef)null) * (float)base.lord.ownedPawns.Count);
		for (int m = 0; m < num2; m++)
		{
			Thing item = ThingMaker.MakeThing(customParams.mealDef, (ThingDef)null);
			list5.Add(item);
		}
		list3.Add(list5);
		if ((int)base.lord.faction.def.techLevel >= 4)
		{
			DropPodUtility.DropThingGroupsNear(((LordToilData_Siege)Data).siegeCenter, ((LordToil)this).Map, list3, 110, false, false, true, true, true, false, (Faction)null);
		}
		else
		{
			IntVec3 val9 = default(IntVec3);
			for (int n = 0; n < list3.Count; n++)
			{
				List<Thing> list6 = list3[n];
				if (DropCellFinder.TryFindDropSpotNear(((LordToilData_Siege)Data).siegeCenter, ((LordToil)this).Map, ref val9, false, false, true, (IntVec2?)null, true))
				{
					for (int num3 = 0; num3 < list6.Count; num3++)
					{
						Thing obj2 = list6[num3];
						ForbidUtility.SetForbidden(obj2, true, false);
						GenPlace.TryPlaceThing(obj2, val9, ((LordToil)this).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
					}
				}
			}
		}
		LordToilData_SiegeCustom data = Data;
		val8 = BuilderCountFraction;
		((LordToilData_Siege)data).desiredBuilderFraction = ((FloatRange)(ref val8)).RandomInRange;
	}

	public override void UpdateAllDuties()
	{
		LordToilData_SiegeCustom data = Data;
		if (base.lord.ticksInToil < 450)
		{
			for (int i = 0; i < base.lord.ownedPawns.Count; i++)
			{
				SetAsDefender(base.lord.ownedPawns[i]);
			}
			return;
		}
		rememberedDuties.Clear();
		int num = Mathf.RoundToInt((float)base.lord.ownedPawns.Count * ((LordToilData_Siege)data).desiredBuilderFraction);
		if (num <= 0)
		{
			num = 1;
		}
		int num2 = ((LordToil)this).Map.listerThings.ThingsInGroup((ThingRequestGroup)10).Where(delegate(Thing b)
		{
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			if (b.def.hasInteractionCell && b.Faction == base.lord.faction)
			{
				IntVec3 position = b.Position;
				return ((IntVec3)(ref position)).InHorDistOf(((LordToil)this).FlagLoc, ((LordToilData_Siege)data).baseRadius);
			}
			return false;
		}).Count();
		if (num < num2)
		{
			num = num2;
		}
		int num3 = 0;
		for (int j = 0; j < base.lord.ownedPawns.Count; j++)
		{
			Pawn val = base.lord.ownedPawns[j];
			if (val.mindState.duty.def == DutyDefOf.Build)
			{
				rememberedDuties.Add(val, DutyDefOf.Build);
				SetAsBuilder(val);
				num3++;
			}
		}
		int num4 = num - num3;
		Pawn val2 = default(Pawn);
		for (int k = 0; k < num4; k++)
		{
			if (GenCollection.TryRandomElement<Pawn>(base.lord.ownedPawns.Where((Pawn pa) => !rememberedDuties.ContainsKey(pa) && CanBeBuilder(pa)), ref val2))
			{
				rememberedDuties.Add(val2, DutyDefOf.Build);
				SetAsBuilder(val2);
				num3++;
			}
		}
		for (int l = 0; l < base.lord.ownedPawns.Count; l++)
		{
			Pawn val3 = base.lord.ownedPawns[l];
			if (!rememberedDuties.ContainsKey(val3))
			{
				SetAsDefender(val3);
				rememberedDuties.Add(val3, DutyDefOf.Defend);
			}
		}
		if (num3 == 0)
		{
			base.lord.ReceiveMemo("NoBuilders");
		}
	}

	public override void Notify_PawnLost(Pawn victim, PawnLostCondition cond)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		((LordToil)this).UpdateAllDuties();
		((LordToil)this).Notify_PawnLost(victim, cond);
	}

	public override void Notify_ConstructionFailed(Pawn pawn, Frame frame, Blueprint_Build newBlueprint)
	{
		((LordToil)this).Notify_ConstructionFailed(pawn, frame, newBlueprint);
		if (((Thing)frame).Faction == base.lord.faction && newBlueprint != null)
		{
			((LordToilData_Siege)Data).blueprints.Add((Blueprint)(object)newBlueprint);
		}
	}

	private bool CanBeBuilder(Pawn p)
	{
		if (!p.WorkTypeIsDisabled(WorkTypeDefOf.Construction))
		{
			return !p.WorkTypeIsDisabled(WorkTypeDefOf.Firefighter);
		}
		return false;
	}

	private void SetAsBuilder(Pawn p)
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Expected O, but got Unknown
		LordToilData_SiegeCustom data = Data;
		SiegeParameterSetDef customParams = CustomParams;
		p.mindState.duty = new PawnDuty(DutyDefOf.Build, LocalTargetInfo.op_Implicit(((LordToilData_Siege)data).siegeCenter), -1f)
		{
			radius = ((LordToilData_Siege)data).baseRadius
		};
		int num = Mathf.Max(((BuildableDef)customParams.coverDef).constructionSkillPrerequisite, customParams.maxArtilleryConstructionSkill);
		p.skills.GetSkill(SkillDefOf.Construction).EnsureMinLevelWithMargin(num);
		p.workSettings.EnableAndInitialize();
		List<WorkTypeDef> allDefsListForReading = DefDatabase<WorkTypeDef>.AllDefsListForReading;
		for (int i = 0; i < allDefsListForReading.Count; i++)
		{
			WorkTypeDef val = allDefsListForReading[i];
			if (val == WorkTypeDefOf.Construction)
			{
				p.workSettings.SetPriority(val, 1);
			}
			else
			{
				p.workSettings.Disable(val);
			}
		}
	}

	private void SetAsDefender(Pawn p)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Expected O, but got Unknown
		LordToilData_SiegeCustom data = Data;
		p.mindState.duty = new PawnDuty(DutyDefOf.Defend, LocalTargetInfo.op_Implicit(((LordToilData_Siege)data).siegeCenter), -1f)
		{
			radius = ((LordToilData_Siege)data).baseRadius
		};
	}

	public override void LordToilTick()
	{
		//IL_013f: Unknown result type (might be due to invalid IL or missing references)
		//IL_014b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0150: Unknown result type (might be due to invalid IL or missing references)
		//IL_0155: Unknown result type (might be due to invalid IL or missing references)
		//IL_0157: Unknown result type (might be due to invalid IL or missing references)
		//IL_0169: Unknown result type (might be due to invalid IL or missing references)
		//IL_022a: Unknown result type (might be due to invalid IL or missing references)
		//IL_022f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0280: Unknown result type (might be due to invalid IL or missing references)
		((LordToil)this).LordToilTick();
		SiegeParameterSetDef customParams = CustomParams;
		LordToilData_SiegeCustom data = Data;
		if (base.lord.ticksInToil == 450)
		{
			base.lord.CurLordToil.UpdateAllDuties();
		}
		if (base.lord.ticksInToil > 450 && base.lord.ticksInToil % 500 == 0)
		{
			((LordToil)this).UpdateAllDuties();
		}
		if (Find.TickManager.TicksGame % 500 != 0)
		{
			return;
		}
		if (!Frames.Where((Frame frame) => !((Thing)frame).Destroyed).Any() && !((LordToilData_Siege)data).blueprints.Where((Blueprint blue) => !((Thing)blue).Destroyed).Any() && !GenCollection.Any<Thing>(((LordToil)this).Map.listerThings.ThingsInGroup((ThingRequestGroup)10), (Predicate<Thing>)((Thing b) => b.Faction == base.lord.faction && b.def.building.buildingTags.Contains("Artillery"))))
		{
			base.lord.ReceiveMemo("NoArtillery");
			return;
		}
		IEnumerable<Building_TurretGun> artillery = Artillery;
		int num = 0;
		int num2 = 0;
		for (int i = 0; i < GenRadial.NumCellsInRadius(20f); i++)
		{
			IntVec3 val = ((LordToilData_Siege)data).siegeCenter + GenRadial.RadialPattern[i];
			if (!GenGrid.InBounds(val, ((LordToil)this).Map))
			{
				continue;
			}
			List<Thing> thingList = GridsUtility.GetThingList(val, ((LordToil)this).Map);
			for (int j = 0; j < thingList.Count; j++)
			{
				Thing curThing = thingList[j];
				if (artillery.Any((Building_TurretGun a) => CustomSiegeUtility.AcceptsShell(a, curThing.def)))
				{
					num += curThing.stackCount;
				}
				if (curThing.def == customParams.mealDef)
				{
					num2 += curThing.stackCount;
				}
			}
		}
		if (artillery.Any() && num < 4)
		{
			bool flag = false;
			TechLevel techLevel = base.lord.faction.def.techLevel;
			List<ThingDef> list = data.artilleryCounts.Keys.ToList();
			Dictionary<ThingDef, int> dictionary = new Dictionary<ThingDef, int>();
			for (int k = 0; k < 10; k++)
			{
				ThingDef val2 = TurretGunUtility.TryFindRandomShellDef(GenCollection.RandomElementByWeight<ThingDef>((IEnumerable<ThingDef>)list, (Func<ThingDef, float>)((ThingDef a) => data.artilleryCounts[a])), flag, false, true, techLevel, false, 250f, (Faction)null);
				if (val2 != null)
				{
					if (dictionary.ContainsKey(val2))
					{
						dictionary[val2]++;
					}
					else
					{
						dictionary.Add(val2, 1);
					}
				}
			}
			foreach (KeyValuePair<ThingDef, int> item in dictionary)
			{
				DropSupplies(item.Key, item.Value);
			}
		}
		if (num2 < FoodUtility.StackCountForNutrition(5f, StatExtension.GetStatValueAbstract((BuildableDef)(object)customParams.mealDef, StatDefOf.Nutrition, (ThingDef)null)))
		{
			DropSupplies(customParams.mealDef, FoodUtility.StackCountForNutrition(12f, StatExtension.GetStatValueAbstract((BuildableDef)(object)customParams.mealDef, StatDefOf.Nutrition, (ThingDef)null)));
		}
	}

	private void DropSupplies(ThingDef thingDef, int count)
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Invalid comparison between Unknown and I4
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		List<Thing> list = new List<Thing>();
		Thing val = ThingMaker.MakeThing(thingDef, (ThingDef)null);
		val.stackCount = count;
		list.Add(val);
		if ((int)base.lord.faction.def.techLevel >= 4)
		{
			DropPodUtility.DropThingsNear(((LordToilData_Siege)Data).siegeCenter, ((LordToil)this).Map, (IEnumerable<Thing>)list, 110, false, false, true, true, true, (Faction)null);
			return;
		}
		for (int i = 0; i < list.Count; i++)
		{
			GenPlace.TryPlaceThing(list[i], ((LordToilData_Siege)Data).siegeCenter, ((LordToil)this).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
		}
	}

	public override void Cleanup()
	{
		LordToilData_SiegeCustom data = Data;
		((LordToilData_Siege)data).blueprints.RemoveAll((Blueprint blue) => ((Thing)blue).Destroyed);
		for (int i = 0; i < ((LordToilData_Siege)data).blueprints.Count; i++)
		{
			((Thing)((LordToilData_Siege)data).blueprints[i]).Destroy((DestroyMode)6);
		}
		List<Frame> list = Frames.ToList();
		for (int j = 0; j < list.Count; j++)
		{
			((Thing)list[j]).Destroy((DestroyMode)6);
		}
	}
}
