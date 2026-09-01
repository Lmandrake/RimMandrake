using System;
using System.Collections;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class JobGiver_Harvest : ThinkNode
{
	public bool emergency;

	public override ThinkNode DeepCopy(bool resolve = true)
	{
		return (ThinkNode)(object)(JobGiver_Harvest)(object)((ThinkNode)this).DeepCopy(resolve);
	}

	public override float GetPriority(Pawn pawn)
	{
		return 9f;
	}

	public override ThinkResult TryIssueJobPackage(Pawn pawn, JobIssueParams jobParams)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_058b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_050f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0591: Unknown result type (might be due to invalid IL or missing references)
		//IL_054f: Unknown result type (might be due to invalid IL or missing references)
		//IL_052a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0535: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_0325: Unknown result type (might be due to invalid IL or missing references)
		//IL_032a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0238: Unknown result type (might be due to invalid IL or missing references)
		//IL_0250: Unknown result type (might be due to invalid IL or missing references)
		//IL_0255: Unknown result type (might be due to invalid IL or missing references)
		//IL_025d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0262: Unknown result type (might be due to invalid IL or missing references)
		//IL_0276: Unknown result type (might be due to invalid IL or missing references)
		//IL_0280: Unknown result type (might be due to invalid IL or missing references)
		//IL_0285: Unknown result type (might be due to invalid IL or missing references)
		//IL_0294: Unknown result type (might be due to invalid IL or missing references)
		//IL_0296: Unknown result type (might be due to invalid IL or missing references)
		//IL_0298: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		//IL_020e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_015f: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Unknown result type (might be due to invalid IL or missing references)
		//IL_0194: Unknown result type (might be due to invalid IL or missing references)
		//IL_019e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_01af: Unknown result type (might be due to invalid IL or missing references)
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_034b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0350: Unknown result type (might be due to invalid IL or missing references)
		//IL_0355: Unknown result type (might be due to invalid IL or missing references)
		//IL_0357: Unknown result type (might be due to invalid IL or missing references)
		//IL_0359: Unknown result type (might be due to invalid IL or missing references)
		//IL_035e: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0378: Unknown result type (might be due to invalid IL or missing references)
		//IL_0400: Unknown result type (might be due to invalid IL or missing references)
		//IL_0396: Unknown result type (might be due to invalid IL or missing references)
		//IL_0454: Unknown result type (might be due to invalid IL or missing references)
		//IL_0462: Unknown result type (might be due to invalid IL or missing references)
		//IL_0467: Unknown result type (might be due to invalid IL or missing references)
		//IL_041b: Unknown result type (might be due to invalid IL or missing references)
		//IL_03da: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_03af: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_03bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_042f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0431: Unknown result type (might be due to invalid IL or missing references)
		//IL_043c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0441: Unknown result type (might be due to invalid IL or missing references)
		int num = -999;
		TargetInfo val = TargetInfo.Invalid;
		WorkGiver_Scanner val2 = null;
		WorkGiver worker = DefDatabase<WorkGiverDef>.GetNamed("GrowerHarvest", true).Worker;
		if ((worker.def.priorityInType == num || !((TargetInfo)(ref val)).IsValid) && PawnCanUseWorkGiver(pawn, worker))
		{
			try
			{
				Job val3 = worker.NonScanJob(pawn);
				if (val3 != null)
				{
					return new ThinkResult(val3, (ThinkNode)(object)this, (JobTag?)worker.def.tagToGive, false);
				}
				WorkGiver_Scanner scanner = (WorkGiver_Scanner)(object)((worker is WorkGiver_Scanner) ? worker : null);
				if (scanner != null)
				{
					if (((WorkGiver)scanner).def.scanThings)
					{
						Predicate<Thing> predicate = (Thing t) => !ForbidUtility.IsForbidden(t, pawn) && scanner.HasJobOnThing(pawn, t, false);
						IEnumerable<Thing> enumerable = scanner.PotentialWorkThingsGlobal(pawn);
						Thing val4;
						if (scanner.Prioritized)
						{
							IEnumerable<Thing> enumerable2 = enumerable;
							if (enumerable2 == null)
							{
								enumerable2 = ((Thing)pawn).Map.listerThings.ThingsMatching(scanner.PotentialWorkThingRequest);
							}
							if (scanner.AllowUnreachable)
							{
								IntVec3 position = ((Thing)pawn).Position;
								IEnumerable<Thing> enumerable3 = enumerable2;
								Predicate<Thing> predicate2 = predicate;
								val4 = GenClosest.ClosestThing_Global(position, (IEnumerable)enumerable3, 99999f, predicate2, (Func<Thing, float>)((Thing x) => scanner.GetPriority(pawn, TargetInfo.op_Implicit(x))), false);
							}
							else
							{
								IntVec3 position2 = ((Thing)pawn).Position;
								Map map = ((Thing)pawn).Map;
								IEnumerable<Thing> enumerable4 = enumerable2;
								PathEndMode pathEndMode = scanner.PathEndMode;
								TraverseParms val5 = TraverseParms.For(pawn, scanner.MaxPathDanger(pawn), (TraverseMode)0, false, false, false, true);
								Predicate<Thing> predicate3 = predicate;
								val4 = GenClosest.ClosestThing_Global_Reachable(position2, map, enumerable4, pathEndMode, val5, 9999f, predicate3, (Func<Thing, float>)((Thing x) => scanner.GetPriority(pawn, TargetInfo.op_Implicit(x))), false);
							}
						}
						else if (scanner.AllowUnreachable)
						{
							IEnumerable<Thing> enumerable5 = enumerable;
							if (enumerable5 == null)
							{
								enumerable5 = ((Thing)pawn).Map.listerThings.ThingsMatching(scanner.PotentialWorkThingRequest);
							}
							IntVec3 position3 = ((Thing)pawn).Position;
							IEnumerable<Thing> enumerable6 = enumerable5;
							Predicate<Thing> predicate4 = predicate;
							val4 = GenClosest.ClosestThing_Global(position3, (IEnumerable)enumerable6, 99999f, predicate4, (Func<Thing, float>)null, false);
						}
						else
						{
							IntVec3 position4 = ((Thing)pawn).Position;
							Map map2 = ((Thing)pawn).Map;
							ThingRequest potentialWorkThingRequest = scanner.PotentialWorkThingRequest;
							PathEndMode pathEndMode2 = scanner.PathEndMode;
							TraverseParms val6 = TraverseParms.For(pawn, scanner.MaxPathDanger(pawn), (TraverseMode)0, false, false, false, true);
							Predicate<Thing> predicate5 = predicate;
							bool flag = enumerable != null;
							val4 = GenClosest.ClosestThingReachable(position4, map2, potentialWorkThingRequest, pathEndMode2, val6, 9999f, predicate5, enumerable, 0, scanner.MaxRegionsToScanBeforeGlobalSearch, flag, (RegionType)14, false, false);
						}
						if (val4 != null)
						{
							val = TargetInfo.op_Implicit(val4);
							val2 = scanner;
						}
					}
					if (((WorkGiver)scanner).def.scanCells)
					{
						IntVec3 position5 = ((Thing)pawn).Position;
						float num2 = 99999f;
						float num3 = float.MinValue;
						bool prioritized = scanner.Prioritized;
						bool allowUnreachable = scanner.AllowUnreachable;
						Danger val7 = scanner.MaxPathDanger(pawn);
						foreach (IntVec3 item in scanner.PotentialWorkCellsGlobal(pawn))
						{
							bool flag2 = false;
							IntVec3 val8 = item - position5;
							float num4 = ((IntVec3)(ref val8)).LengthHorizontalSquared;
							float num5 = 0f;
							if (prioritized)
							{
								if (!ForbidUtility.IsForbidden(item, pawn) && scanner.HasJobOnCell(pawn, item, false))
								{
									if (!allowUnreachable && !ReachabilityUtility.CanReach(pawn, LocalTargetInfo.op_Implicit(item), scanner.PathEndMode, val7, false, false, (TraverseMode)0))
									{
										continue;
									}
									num5 = scanner.GetPriority(pawn, item);
									if (num5 > num3 || (num5 == num3 && num4 < num2))
									{
										flag2 = true;
									}
								}
							}
							else if (num4 < num2 && !ForbidUtility.IsForbidden(item, pawn) && scanner.HasJobOnCell(pawn, item, false))
							{
								if (!allowUnreachable && !ReachabilityUtility.CanReach(pawn, LocalTargetInfo.op_Implicit(item), scanner.PathEndMode, val7, false, false, (TraverseMode)0))
								{
									continue;
								}
								flag2 = true;
							}
							if (flag2)
							{
								val = new TargetInfo(item, ((Thing)pawn).Map, false);
								val2 = scanner;
								num2 = num4;
								num3 = num5;
							}
						}
					}
				}
			}
			catch (Exception ex)
			{
				Log.Error(string.Concat(pawn, " threw exception in WorkGiver ", ((Def)worker.def).defName, ": ", ex.ToString()));
			}
			if (((TargetInfo)(ref val)).IsValid)
			{
				Job val9 = ((!((TargetInfo)(ref val)).HasThing) ? val2.JobOnCell(pawn, ((TargetInfo)(ref val)).Cell, false) : val2.JobOnThing(pawn, ((TargetInfo)(ref val)).Thing, false));
				if (val9 != null)
				{
					return new ThinkResult(val9, (ThinkNode)(object)this, (JobTag?)worker.def.tagToGive, false);
				}
				Log.ErrorOnce(string.Concat(val2, " provided target ", val, " but yielded no actual job for pawn ", pawn, ". The CanGiveJob and JobOnX methods may not be synchronized."), 6112651);
			}
			num = worker.def.priorityInType;
		}
		return ThinkResult.NoJob;
	}

	private bool PawnCanUseWorkGiver(Pawn pawn, WorkGiver giver)
	{
		if (giver.MissingRequiredCapacity(pawn) == null)
		{
			return !giver.ShouldSkip(pawn, false);
		}
		return false;
	}

	private Job GiverTryGiveJobPrioritized(Pawn pawn, WorkGiver giver, IntVec3 cell)
	{
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		if (!PawnCanUseWorkGiver(pawn, giver))
		{
			return null;
		}
		try
		{
			Job val = giver.NonScanJob(pawn);
			if (val != null)
			{
				return val;
			}
			WorkGiver_Scanner scanner = (WorkGiver_Scanner)(object)((giver is WorkGiver_Scanner) ? giver : null);
			if (scanner != null)
			{
				if (giver.def.scanThings)
				{
					Predicate<Thing> predicate = (Thing t) => !ForbidUtility.IsForbidden(t, pawn) && scanner.HasJobOnThing(pawn, t, false);
					List<Thing> thingList = GridsUtility.GetThingList(cell, ((Thing)pawn).Map);
					for (int i = 0; i < thingList.Count; i++)
					{
						Thing val2 = thingList[i];
						ThingRequest potentialWorkThingRequest = scanner.PotentialWorkThingRequest;
						if (((ThingRequest)(ref potentialWorkThingRequest)).Accepts(val2) && predicate(val2))
						{
							return scanner.JobOnThing(pawn, val2, false);
						}
					}
				}
				if (giver.def.scanCells && !ForbidUtility.IsForbidden(cell, pawn) && scanner.HasJobOnCell(pawn, cell, false))
				{
					return scanner.JobOnCell(pawn, cell, false);
				}
			}
		}
		catch (Exception ex)
		{
			Log.Error(string.Concat(pawn, " threw exception in GiverTryGiveJobTargeted on WorkGiver ", ((Def)giver.def).defName, ": ", ex.ToString()));
		}
		return null;
	}
}
