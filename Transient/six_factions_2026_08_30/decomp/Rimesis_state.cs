using RimWorld;

namespace Rimesis;

public static class RimesisRaidGenerationContext
{
	private static IncidentParms active;

	private static IncidentWorker_Raid activeWorker;

	public static IncidentParms Active => active;

	public static bool IsDireRaid => RimesisDireRaidsCompatibility.IsDireRaid(activeWorker);

	public static void Begin(IncidentParms parms, IncidentWorker_Raid worker = null)
	{
		active = parms;
		activeWorker = worker;
	}

	public static void End()
	{
		active = null;
		activeWorker = null;
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.0.0.9375' (yours is '9.0.0.7889')
using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace Rimesis;

public sealed class RimesisRaidPlan
{
	private const int StandardMaximum = 3;

	private const int AbsoluteMaximum = 10;

	private const float ExtraCountChance = 0.04f;

	private static readonly Dictionary<int, RimesisRaidPlan> plans = new Dictionary<int, RimesisRaidPlan>();

	private static readonly Dictionary<int, int> forcedCounts = new Dictionary<int, int>();

	private static readonly Dictionary<int, List<int>> forcedRecordPawnIds = new Dictionary<int, List<int>>();

	public Faction faction;

	public List<RimesisRecord> records = new List<RimesisRecord>();

	public int createdTick;

	public ColonyDefenseProfile colonyProfile;

	public bool retaliationPointsCaptured;

	public float retaliationPointsBefore;

	public float retaliationPointsAfter;

	public float retaliationPointMultiplier;

	public bool retaliationArmed;

	private bool extrasClaimed;

	public static bool ExpandedCountsEnabled
	{
		get
		{
			if (Prefs.DevMode)
			{
				return RimesisMod.Settings?.allowMoreThanThreeRimesisPerRaid ?? false;
			}
			return false;
		}
	}

	public static int MaximumRimesisPerRaid
	{
		get
		{
			int num = Math.Max(1, Math.Min(10, RimesisMod.Settings?.maxPerFaction ?? 3));
			int result = Math.Max(1, Math.Min(num, RimesisMod.Settings?.maxPerRaid ?? 3));
			if (!ExpandedCountsEnabled)
			{
				return Math.Min(3, num);
			}
			return result;
		}
	}

	public static RimesisRaidPlan For(Faction faction)
	{
		if (faction == null)
		{
			return null;
		}
		int loadID = faction.loadID;
		if (plans.TryGetValue(loadID, out var value) && Find.TickManager.TicksGame - value.createdTick < 2500)
		{
			return value;
		}
		RimesisWorldComponent current = RimesisWorldComponent.Current;
		RetaliationRecord retaliationRecord = (BrightArchotechFacilityRaidContext.IsActiveForFaction(faction) ? null : current?.PendingRetaliation(faction));
		if (retaliationRecord != null)
		{
			current.EnsureRetaliationLeader(faction);
		}
		bool flag = retaliationRecord != null && !retaliationRecord.awaitingSettlementResolution;
		List<RimesisRecord> list = current?.EligibleForRaid(faction) ?? new List<RimesisRecord>();
		List<RimesisRecord> list2 = null;
		int num;
		int value3;
		if (forcedRecordPawnIds.TryGetValue(loadID, out var value2))
		{
			forcedRecordPawnIds.Remove(loadID);
			forcedCounts.Remove(loadID);
			Dictionary<int, int> idOrder = value2.Select((int pawnId, int index) => new { pawnId, index }).ToDictionary(pair => pair.pawnId, pair => pair.index);
			list2 = (from record in list
				where record?.pawn != null && idOrder.ContainsKey(((Thing)record.pawn).thingIDNumber)
				orderby idOrder[((Thing)record.pawn).thingIDNumber]
				select record).Take(MaximumRimesisPerRaid).ToList();
			num = list2.Count;
		}
		else if (forcedCounts.TryGetValue(loadID, out value3))
		{
			num = value3;
			forcedCounts.Remove(loadID);
		}
		else
		{
			num = RollNaturalCount(Rand.Value, MaximumRimesisPerRaid);
		}
		if (flag && list.Count > 0)
		{
			num = Math.Max(1, num);
		}
		RimesisRaidPlan rimesisRaidPlan = new RimesisRaidPlan
		{
			faction = faction,
			records = (list2 ?? list.Take(Math.Min(num, list.Count)).ToList()),
			createdTick = Find.TickManager.TicksGame,
			colonyProfile = ((num > 0 && list.Count > 0) ? ColonyDefenseProfile.Scan() : null)
		};
		if (flag && rimesisRaidPlan.records.Count == 0 && list.Count > 0)
		{
			rimesisRaidPlan.records.Add(list[0]);
		}
		rimesisRaidPlan.retaliationArmed = flag && rimesisRaidPlan.records.Count > 0;
		plans[loadID] = rimesisRaidPlan;
		return rimesisRaidPlan;
	}

	internal static int RollNaturalCount(float roll, int maximum)
	{
		maximum = Math.Max(1, Math.Min(10, maximum));
		float num = 0f;
		for (int num2 = maximum; num2 >= 4; num2--)
		{
			num += 0.04f;
			if (roll < num)
			{
				return num2;
			}
		}
		num += 0.07f;
		if (roll < num)
		{
			return Math.Min(3, maximum);
		}
		num += 0.28f;
		if (roll < num)
		{
			return Math.Min(2, maximum);
		}
		float num3 = 0.5f - (float)Math.Max(0, maximum - 3) * 0.04f;
		num += num3;
		return (roll < num) ? 1 : 0;
	}

	public static void Consume(Faction faction)
	{
		if (faction != null)
		{
			plans.Remove(faction.loadID);
		}
	}

	public static void ForceNext(Faction faction, int count)
	{
		if (faction != null)
		{
			int loadID = faction.loadID;
			plans.Remove(loadID);
			forcedRecordPawnIds.Remove(loadID);
			forcedCounts[loadID] = Math.Max(0, Math.Min(MaximumRimesisPerRaid, count));
		}
	}

	public static void ForceNext(Faction faction, IEnumerable<RimesisRecord> exactRecords)
	{
		if (faction != null)
		{
			List<int> value = (from record in exactRecords?.Where((RimesisRecord record) => record?.pawn != null && record.faction == faction)
				select ((Thing)record.pawn).thingIDNumber).Distinct().Take(MaximumRimesisPerRaid).ToList() ?? new List<int>();
			int loadID = faction.loadID;
			plans.Remove(loadID);
			forcedCounts.Remove(loadID);
			forcedRecordPawnIds[loadID] = value;
		}
	}

	public static void Invalidate(Faction faction)
	{
		if (faction != null)
		{
			plans.Remove(faction.loadID);
		}
	}

	public static void CancelForced(Faction faction)
	{
		if (faction != null)
		{
			int loadID = faction.loadID;
			plans.Remove(loadID);
			forcedCounts.Remove(loadID);
			forcedRecordPawnIds.Remove(loadID);
		}
	}

	public List<RimesisRecord> ClaimRecords()
	{
		if (extrasClaimed)
		{
			return new List<RimesisRecord>();
		}
		extrasClaimed = true;
		return records.ToList();
	}

	public void RememberRetaliationPoints(float before, float after, float multiplier)
	{
		retaliationPointsCaptured = true;
		retaliationPointsBefore = before;
		retaliationPointsAfter = after;
		retaliationPointMultiplier = multiplier;
	}

	public static void Clear()
	{
		plans.Clear();
		forcedCounts.Clear();
		forcedRecordPawnIds.Clear();
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.0.0.9375' (yours is '9.0.0.7889')
