using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_Spawner : HediffComp
{
	private int ticksUntilSpawn;

	public HediffCompProperties_Spawner PropsSpawner => (HediffCompProperties_Spawner)(object)base.props;

	public override string CompLabelInBracketsExtra => GetLabel();

	public override void CompPostMake()
	{
		((HediffComp)this).CompPostMake();
		ticksUntilSpawn = PropsSpawner.initialSpawnWait;
	}

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		TickInterval(delta);
	}

	private void TickInterval(int interval)
	{
		if (((Thing)((Hediff)base.parent).pawn).Spawned && ((Thing)((Hediff)base.parent).pawn).Map != null)
		{
			ticksUntilSpawn -= interval;
			CheckShouldSpawn();
		}
	}

	private void CheckShouldSpawn()
	{
		if (ticksUntilSpawn <= 0)
		{
			ResetCountdown();
			TryDoSpawn();
		}
	}

	public bool TryDoSpawn()
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0194: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_0205: Unknown result type (might be due to invalid IL or missing references)
		//IL_020a: Unknown result type (might be due to invalid IL or missing references)
		//IL_020f: Unknown result type (might be due to invalid IL or missing references)
		if (!((Thing)((Hediff)base.parent).pawn).Spawned)
		{
			return false;
		}
		if (PropsSpawner.spawnMaxAdjacent >= 0)
		{
			int num = 0;
			for (int i = 0; i < 9; i++)
			{
				IntVec3 val = ((Thing)((Hediff)base.parent).pawn).Position + GenAdj.AdjacentCellsAndInside[i];
				if (!GenGrid.InBounds(val, ((Thing)((Hediff)base.parent).pawn).Map))
				{
					continue;
				}
				List<Thing> thingList = GridsUtility.GetThingList(val, ((Thing)((Hediff)base.parent).pawn).Map);
				for (int j = 0; j < thingList.Count; j++)
				{
					if (thingList[j].def == PropsSpawner.thingToSpawn)
					{
						num += thingList[j].stackCount;
						if (num >= PropsSpawner.spawnMaxAdjacent)
						{
							return false;
						}
					}
				}
			}
		}
		if (TryFindSpawnCell((Thing)(object)((Hediff)base.parent).pawn, PropsSpawner.thingToSpawn, PropsSpawner.spawnCount, out var result))
		{
			Thing val2 = ThingMaker.MakeThing(PropsSpawner.thingToSpawn, (ThingDef)null);
			val2.stackCount = PropsSpawner.spawnCount;
			if (val2 == null)
			{
				Log.Error("Could not spawn anything for " + (object)base.parent);
			}
			if (PropsSpawner.inheritFaction && val2.Faction != ((Thing)((Hediff)base.parent).pawn).Faction)
			{
				val2.SetFaction(((Thing)((Hediff)base.parent).pawn).Faction, (Pawn)null);
			}
			Thing val3 = default(Thing);
			GenPlace.TryPlaceThing(val2, result, ((Thing)((Hediff)base.parent).pawn).Map, (ThingPlaceMode)0, ref val3, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
			if (PropsSpawner.spawnForbidden)
			{
				ForbidUtility.SetForbidden(val3, true, true);
			}
			if (PropsSpawner.showMessageIfOwned && ((Thing)((Hediff)base.parent).pawn).Faction == Faction.OfPlayer)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCompSpawnerSpawnedItem", NamedArgument.op_Implicit(((Def)PropsSpawner.thingToSpawn).LabelCap))), LookTargets.op_Implicit(val2), MessageTypeDefOf.PositiveEvent, true);
			}
			return true;
		}
		return false;
	}

	public static bool TryFindSpawnCell(Thing parent, ThingDef thingToSpawn, int spawnCount, out IntVec3 result)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Invalid comparison between Unknown and I4
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Invalid comparison between Unknown and I4
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		foreach (IntVec3 item in GenCollection.InRandomOrder<IntVec3>(GenAdj.CellsAdjacent8Way(parent), (IList<IntVec3>)null))
		{
			if (!GenGrid.Walkable(item, parent.Map))
			{
				continue;
			}
			Building edifice = GridsUtility.GetEdifice(item, parent.Map);
			if (edifice != null && EdificeUtility.IsEdifice((BuildableDef)(object)thingToSpawn))
			{
				continue;
			}
			Building_Door val = (Building_Door)(object)((edifice is Building_Door) ? edifice : null);
			if ((val != null && !val.FreePassage) || ((int)((BuildableDef)parent.def).passability != 2 && !GenSight.LineOfSight(parent.Position, item, parent.Map)))
			{
				continue;
			}
			bool flag = false;
			List<Thing> thingList = GridsUtility.GetThingList(item, parent.Map);
			for (int i = 0; i < thingList.Count; i++)
			{
				Thing val2 = thingList[i];
				if ((int)val2.def.category == 2 && (val2.def != thingToSpawn || val2.stackCount > thingToSpawn.stackLimit - spawnCount))
				{
					flag = true;
					break;
				}
			}
			if (!flag)
			{
				result = item;
				return true;
			}
		}
		result = IntVec3.Invalid;
		return false;
	}

	private void ResetCountdown()
	{
		ticksUntilSpawn = ((IntRange)(ref PropsSpawner.spawnIntervalRange)).RandomInRange;
	}

	public override void CompExposeData()
	{
		((HediffComp)this).CompExposeData();
		string text = (GenText.NullOrEmpty(PropsSpawner.saveKeysPrefix) ? null : (PropsSpawner.saveKeysPrefix + "_"));
		Scribe_Values.Look<int>(ref ticksUntilSpawn, text + "ticksUntilSpawn", 0, false);
	}

	public string GetLabel()
	{
		return GenDate.ToStringTicksToPeriod(ticksUntilSpawn, true, false, true, true, false);
	}
}
