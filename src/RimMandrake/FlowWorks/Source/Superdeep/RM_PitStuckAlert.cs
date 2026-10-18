using System.Collections.Generic;
using System.Text;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_ALERT_BUILD_RED_MEANS_HELP (owner card Q12, 2026-10-18: "Stuck alert → standard red alert"): a red alert in the
	/// corner when one of our colonists is held in a pit (RM_SuperdeepTrap.IsHeld: a jumper, or anyone with "your own pit
	/// takes your own people" on) and cannot reach food or a bed because of it. Not a marker on the ground (2026-10-12 Q4).
	/// The decision is RM_PitRoomMath.StuckAlert (selftested); this is its Verse half. Reach is re-measured every 250 ticks.
	/// </summary>
	public class Alert_ColonistStuckInPit : Alert_Critical
	{
		private const int RecheckTicks = 250;

		private readonly List<Thing> culprits = new List<Thing>();
		private int checkedAt = -RecheckTicks;

		public Alert_ColonistStuckInPit()
		{
			defaultLabel = "Colonist stuck in a pit";
		}

		private List<Thing> Culprits()
		{
			int now = Find.TickManager?.TicksGame ?? 0;
			if (now - checkedAt < RecheckTicks && now >= checkedAt)
			{
				return culprits;
			}
			checkedAt = now;
			culprits.Clear();
			if (!RimMandrakeFlowWorksSettings.pitStuckAlertEnabled || Find.Maps == null)
			{
				return culprits;
			}
			foreach (Map m in Find.Maps)
			{
				foreach (Pawn p in m.mapPawns.FreeColonistsSpawned)
				{
					if (!RM_SuperdeepTrap.IsHeld(p))
					{
						continue;   // the cheap test first: almost nobody is ever held
					}
					bool needsFood = p.needs?.food != null;
					bool needsRest = p.needs?.rest != null;
					bool food = needsFood && FoodReachable(p);
					bool bed = needsRest && RestUtility.FindBedFor(p) != null;
					if (RM_PitRoomMath.StuckAlert(true, true, true, needsFood, food, needsRest, bed))
					{
						culprits.Add(p);
					}
				}
			}
			return culprits;
		}

		private static bool FoodReachable(Pawn p)
		{
			return GenClosest.ClosestThingReachable(p.Position, p.Map, ThingRequest.ForGroup(ThingRequestGroup.FoodSourceNotPlantOrTree),
				PathEndMode.ClosestTouch, TraverseParms.For(p), 9999f, t => t.def.IsNutritionGivingIngestible && !t.IsForbidden(p)) != null;
		}

		public override TaggedString GetExplanation()
		{
			var sb = new StringBuilder("These colonists are down a pit they cannot climb out of, and cannot reach food or a bed:\n");
			foreach (Thing t in culprits)
			{
				sb.Append("\n  - ").Append(t.LabelShortCap);
			}
			sb.Append("\n\nLower a ladder into the pit, or dig a ramp out.");
			return sb.ToString();
		}

		public override AlertReport GetReport()
		{
			return RimMandrakeFlowWorksSettings.pitStuckAlertEnabled ? AlertReport.CulpritsAre(Culprits()) : AlertReport.Inactive;
		}
	}
}
