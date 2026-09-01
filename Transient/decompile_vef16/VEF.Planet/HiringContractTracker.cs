using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Planet;

public class HiringContractTracker : WorldComponent, ICommunicable
{
	public Dictionary<Hireable, List<ExposablePair>> deadCount = new Dictionary<Hireable, List<ExposablePair>>();

	public int endTicks;

	public HireableFactionDef factionDef;

	public Hireable hireable;

	public List<Pawn> pawns = new List<Pawn>();

	public float price;

	public HiringContractTracker(World world)
		: base(world)
	{
	}

	public string GetCallLabel()
	{
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.ContractInfo", NamedArgument.op_Implicit(GenText.CapitalizeFirst(((Def)(factionDef?)).label ?? hireable.Key))));
	}

	public string GetInfoText()
	{
		return "";
	}

	public void TryOpenComms(Pawn negotiator)
	{
		Find.WindowStack.Add((Window)(object)new Dialog_ContractInfo(this));
	}

	public Faction GetFaction()
	{
		return null;
	}

	public FloatMenuOption CommFloatMenuOption(Building_CommsConsole console, Pawn negotiator)
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Expected O, but got Unknown
		return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(GetCallLabel(), (Action)delegate
		{
			console.GiveUseCommsJob(negotiator, (ICommunicable)(object)this);
		}, (MenuOptionPriority)7, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0), negotiator, LocalTargetInfo.op_Implicit((Thing)(object)console), "ReservedBy", (ReservationLayerDef)null);
	}

	public bool IsHired(Pawn pawn)
	{
		return pawns.Contains(pawn);
	}

	public void SetNewContract(int days, List<Pawn> pawns, Hireable hireable, HireableFactionDef faction = null, float price = 0f)
	{
		endTicks = Find.TickManager.TicksAbs + days * 60000;
		this.pawns = pawns;
		this.hireable = hireable;
		factionDef = faction;
		this.price = price;
	}

	public override void WorldComponentTick()
	{
		((WorldComponent)this).WorldComponentTick();
		if (Find.TickManager.TicksAbs % 150 == 0 && Find.TickManager.TicksAbs > endTicks && GenCollection.Any<Pawn>(pawns))
		{
			EndContract();
		}
	}

	public void EndContract()
	{
		//IL_0118: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_012f: Expected O, but got Unknown
		int num = 0;
		IntVec3 val = default(IntVec3);
		for (int num2 = pawns.Count - 1; num2 >= 0; num2--)
		{
			Pawn pawn = pawns[num2];
			if (pawn == null || pawn.Dead || GenCollection.Any<Faction>(Find.FactionManager.AllFactionsListForReading, (Predicate<Faction>)((Faction f) => f.kidnapped.KidnappedPawnsListForReading.Contains(pawn))))
			{
				num++;
				pawns.Remove(pawn);
			}
			else if (pawn.health.capacities.CapableOf(PawnCapacityDefOf.Moving))
			{
				if (((Thing)pawn).Map != null && pawn.CurJobDef != VEFDefOf.VFEC_LeaveMap)
				{
					pawn.jobs.StopAll(false, true);
					if (!CellFinder.TryFindRandomPawnExitCell(pawn, ref val) && !CellFinder.TryFindRandomEdgeCellWith((Predicate<IntVec3>)((IntVec3 c) => !((Thing)pawn).Map.roofGrid.Roofed(c) && GenGrid.WalkableBy(c, ((Thing)pawn).Map, pawn) && ReachabilityUtility.CanReach(pawn, LocalTargetInfo.op_Implicit(c), (PathEndMode)1, (Danger)3, true, true, (TraverseMode)1)), ((Thing)pawn).Map, 0f, ref val))
					{
						BreakContract();
						return;
					}
					pawn.jobs.TryTakeOrderedJob(new Job(VEFDefOf.VFEC_LeaveMap, LocalTargetInfo.op_Implicit(val)), (JobTag?)(JobTag)0, false);
				}
				else if (CaravanUtility.GetCaravan((Thing)(object)pawn) != null)
				{
					CaravanUtility.GetCaravan((Thing)(object)pawn).RemovePawn(pawn);
					pawns.Remove(pawn);
				}
			}
			if (num > 0)
			{
				if (!deadCount.ContainsKey(hireable))
				{
					deadCount.Add(hireable, new List<ExposablePair>());
				}
				deadCount[hireable].Add(new ExposablePair(num, Find.TickManager.TicksAbs + 3600000));
			}
		}
		if (pawns.Count <= 0)
		{
			hireable = null;
		}
	}

	public void BreakContract()
	{
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fa: Expected O, but got Unknown
		if (pawns.Count > 0)
		{
			if (!deadCount.ContainsKey(hireable))
			{
				deadCount.Add(hireable, new List<ExposablePair>());
			}
			deadCount[hireable].Add(new ExposablePair(pawns.Count, Find.TickManager.TicksAbs + 3600000));
			foreach (Pawn pawn in pawns)
			{
				if (!pawn.Dead)
				{
					if (((Thing)pawn).Map != null)
					{
						pawn.jobs.StopAll(false, true);
						((Thing)pawn).SetFaction(Faction.OfAncientsHostile, (Pawn)null);
						RaidStrategyDefOf.ImmediateAttack.Worker.MakeLords(new IncidentParms
						{
							target = (IIncidentTarget)(object)((Thing)pawn).Map,
							faction = Faction.OfAncientsHostile,
							canTimeoutOrFlee = false
						}, new List<Pawn> { pawn });
					}
					else if (CaravanUtility.GetCaravan((Thing)(object)pawn) != null)
					{
						CaravanUtility.GetCaravan((Thing)(object)pawn).RemovePawn(pawn);
					}
				}
			}
		}
		hireable = null;
		pawns.Clear();
	}

	public float GetFactorForHireable(Hireable hireable)
	{
		if (!deadCount.ContainsKey(hireable))
		{
			deadCount.Add(hireable, new List<ExposablePair>());
		}
		List<ExposablePair> list = deadCount[hireable];
		float num = 0f;
		for (int num2 = list.Count - 1; num2 >= 0; num2--)
		{
			if (Find.TickManager.TicksAbs > (int)list[num2].value)
			{
				list.RemoveAt(num2);
			}
			else
			{
				num += 0.05f * (float)(int)list[num2].key;
			}
		}
		return num;
	}

	public override void ExposeData()
	{
		((WorldComponent)this).ExposeData();
		Scribe_Values.Look<int>(ref endTicks, "endTicks", 0, false);
		Scribe_Collections.Look<Pawn>(ref pawns, "pawns", (LookMode)3, Array.Empty<object>());
		Scribe_References.Look<Hireable>(ref hireable, "hireable", false);
		List<Hireable> list = new List<Hireable>(deadCount.Keys);
		Scribe_Collections.Look<Hireable>(ref list, "deadCountKey", (LookMode)3, Array.Empty<object>());
		List<List<ExposablePair>> list2 = new List<List<ExposablePair>>(deadCount.Values);
		for (int i = 0; i < list.Count; i++)
		{
			List<ExposablePair> list3 = ((list2.Count > i) ? list2[i] : new List<ExposablePair>());
			Scribe_Collections.Look<ExposablePair>(ref list3, "exposablePairs" + i, (LookMode)2, Array.Empty<object>());
			if (list2.Count > i)
			{
				list2[i] = list3;
			}
			else
			{
				list2.Add(list3);
			}
		}
		deadCount.Clear();
		for (int j = 0; j < list.Count; j++)
		{
			deadCount.Add(list[j], list2[j]);
		}
		Scribe_Values.Look<float>(ref price, "price", 0f, false);
		Scribe_Defs.Look<HireableFactionDef>(ref factionDef, "faction");
	}
}
