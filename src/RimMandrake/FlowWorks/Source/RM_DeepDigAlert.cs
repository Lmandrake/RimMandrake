using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// DEEP_DIG_EXPLAIN_WAITING_ON_NO_DROID (UX review 2026-10-22): a dig order past the colonist limit waits for machine labour
	/// (RM_DigLabor). With no machine on the map that can mine, it waited silently. This alert names those squares and says why.
	/// Re-measured every 250 ticks.
	/// </summary>
	public class Alert_DeepDigWaitsForMachine : Alert
	{
		private const int RecheckTicks = 250;

		private readonly List<GlobalTargetInfo> culprits = new List<GlobalTargetInfo>();
		private int checkedAt = -RecheckTicks;

		public Alert_DeepDigWaitsForMachine()
		{
			defaultLabel = "Deep dig waiting for a machine";
			defaultPriority = AlertPriority.Medium;
		}

		/// <summary>True when a colony pawn on <paramref name="map"/> is machine labour that may do Mining work.</summary>
		public static bool HasMachineDigger(Map map)
		{
			if (map == null || Faction.OfPlayerSilentFail == null)
			{
				return false;
			}
			foreach (Pawn p in map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer))
			{
				if (RM_DigLabor.IsMachineLabour(p) && !p.Downed && !p.WorkTypeIsDisabled(WorkTypeDefOf.Mining))
				{
					return true;
				}
			}
			return false;
		}

		private List<GlobalTargetInfo> Culprits()
		{
			int now = Find.TickManager?.TicksGame ?? 0;
			if (now - checkedAt < RecheckTicks && now >= checkedAt)
			{
				return culprits;
			}
			checkedAt = now;
			culprits.Clear();
			if (Find.Maps == null || RM_DigLabor.DesignationCap <= RimMandrakeFlowWorksSettings.MaxDigDepth)
			{
				return culprits;   // machines may dig no deeper than colonists: no order can be waiting for one
			}
			int colonistCap = RimMandrakeFlowWorksSettings.MaxDigDepth;
			foreach (Map m in Find.Maps)
			{
				if (!m.IsPlayerHome || !m.designationManager.AnySpawnedDesignationOfDef(RimMandrakeFlowWorks_DefOf.RM_DigCanal))
				{
					continue;
				}
				RM_MapComponent_Excavation eng = m.GetComponent<RM_MapComponent_Excavation>();
				if (eng == null || HasMachineDigger(m))
				{
					continue;
				}
				foreach (Designation d in m.designationManager.SpawnedDesignationsOfDef(RimMandrakeFlowWorks_DefOf.RM_DigCanal))
				{
					IntVec3 c = d.target.Cell;
					int depth = eng.ExcavatedDepthAt(c);
					bool colonistsCannot = depth == RM_ExcavationDepth.Surface
						? eng.FirstCutDepthAt(c, colonistCap) < 0 && eng.FirstCutDepthAt(c) >= 0
						: !RM_DigDepthMath.MayDeepen(depth, colonistCap) && RM_DigDepthMath.MayDeepen(depth, RM_DigLabor.DesignationCap);
					if (colonistsCannot)
					{
						culprits.Add(new GlobalTargetInfo(c, m));
					}
				}
			}
			return culprits;
		}

		public override TaggedString GetExplanation()
		{
			return "These dig orders are deeper than colonists may dig (" + RM_Volume.FormatFloorMetres(RimMandrakeFlowWorksSettings.MaxDigDepth)
				+ "). Only machine labour (a mechanoid or a droid that can do Mining) digs past that, and none is here, so they wait.\n\n"
				+ "Bring a digging machine, cancel the orders, or raise \"Deepest colonist dig\" in the Flow Works settings ("
				+ Culprits().Count + " square(s) waiting).";
		}

		public override AlertReport GetReport()
		{
			return AlertReport.CulpritsAre(Culprits());
		}
	}
}
