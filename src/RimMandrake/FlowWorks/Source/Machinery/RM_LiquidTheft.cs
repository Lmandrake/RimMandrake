using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	[DefOf]
	public static class RM_LiquidTheftDefOf
	{
		public static HistoryEventDef RM_LiquidTheftCaught;
		static RM_LiquidTheftDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(RM_LiquidTheftDefOf));
	}

	/// <summary>
	/// Liquid networks L9 (rev 2 §3.4; owner card Q4: a hose into another faction's tank is allowed, as theft, priced like power
	/// theft; ruling #7: 2 goodwill a day, 12-cell notice). Modelled on Gimme Some Slack's PowerTheftConsequences (copied, never
	/// referenced):
	///   * TOUCHED: once per pump cycle every other faction's tank on the map is compared with the stock last seen; any change is
	///     liquid taken from it or put into it, counted only when the player's net reaches the tank (PlayerReaches, C1-F14). The check is on the tank's stock itself, so no mover (pump, machine, tank job,
	///     hose, colonist with a bottle) can bypass it, and a refused move that was put back changes nothing.
	///   * CAUGHT: a member of that faction (humanlike, awake, not downed, not our prisoner) within liquidTheftSightRange cells
	///     with line of sight to the tank, the first cycle it is touched; once per tank per faction; a letter names who saw it.
	///   * LEAK: a caught tank accrues the ticks of every cycle in which it is touched (an idle tank accrues nothing); every whole
	///     day costs liquidTheftGoodwillPerDay goodwill (vanilla TryAffectGoodwillWith, reason RM_LiquidTheftCaught). A faction
	///     at -100 or permanently hostile is skipped.
	/// Mod Settings: liquidTheftEnabled (off: their tanks never join, so nothing is taken), liquidTheftGoodwillPerDay,
	/// liquidTheftSightRange.
	/// </summary>
	public static class RM_LiquidTheft
	{
		/// <summary>State read (probe, selftests).</summary>
		public static int caught, charges, goodwillCharged;

		public static void TheftTick(Map map)
		{
			if (map == null || !RM_MachinerySettings.liquidTheftEnabled)
			{
				return;
			}
			foreach (Thing th in map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial))
			{
				if (!(th is Building_LiquidTank t) || !RM_LiquidNet.IsForeign(t))
				{
					continue;
				}
				bool touched = t.theftSeenUnits >= 0 && RM_LiquidTheftMath.Touched(t.theftSeenUnits, t.theftSeenLiquid, t.storedUnits, t.storedLiquid);
				t.theftSeenUnits = t.storedUnits;
				t.theftSeenLiquid = t.storedLiquid;
				Faction victim = t.Faction;
				// LIQUID_THEFT_VERIFY_FALSE_ACCUSATION (C1-F14): a change the player's net cannot have made (the owners' own
				// still, a ruin machine) is not theft; only a tank the player's pipes, hoses or touching machines reach is
				if (!touched || victim == null || victim.defeated || !PlayerReaches(t))
				{
					continue;
				}
				if (t.theftCaughtBy != victim)
				{
					Pawn witness = Witness(t, victim);
					if (witness == null)
					{
						continue;
					}
					t.theftCaughtBy = victim;
					t.theftTicks = 0;
					caught++;
					Find.LetterStack.ReceiveLetter("RMFlow_LiquidTheftLetterLabel".Translate(),
						"RMFlow_LiquidTheftLetter".Translate(witness.LabelShortCap, victim.Name, t.LabelShort, RM_MachinerySettings.liquidTheftGoodwillPerDay),
						LetterDefOf.NegativeEvent, new LookTargets(t, witness));
					continue;
				}
				int change = RM_LiquidTheftMath.TheftGoodwillAccrue(ref t.theftTicks, RM_PumpMath.CycleTicks, true,
					RM_MachinerySettings.liquidTheftGoodwillPerDay, GenDate.TicksPerDay);
				if (change >= 0 || victim.PlayerGoodwill <= -100 || victim.def.permanentEnemy)
				{
					continue;
				}
				if (Faction.OfPlayer.TryAffectGoodwillWith(victim, change, canSendMessage: true, canSendHostilityLetter: true,
					RM_LiquidTheftDefOf.RM_LiquidTheftCaught, new GlobalTargetInfo(t)))
				{
					charges++;
					goodwillCharged += change;
				}
			}
		}

		/// <summary>C1-F14: is <paramref name="t"/> on a net with anything of the player's (a machine or tank on one of its
		/// components, a player reel's hose on one, or a player machine touching it)? Only such a tank can be stolen from.</summary>
		public static bool PlayerReaches(Building_LiquidTank t)
		{
			Map map = t?.Map;
			if (map == null)
			{
				return false;
			}
			foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(t))
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				foreach (Thing x in c.GetThingList(map))
				{
					// only a machine draws from a tank it touches (its 8-way touch store); pipes and tanks reach through components
					if (x != t && x.Faction == Faction.OfPlayer && RM_LiquidNet.RoleOfThing(x) == RM_NetRole.Machine)
					{
						return true;
					}
				}
			}
			foreach (RM_NetComponent comp in RM_LiquidNet.Components(map).ComponentsOf(t))
			{
				foreach (object m in comp.Machines)
				{
					if (m is Thing x && x.Faction == Faction.OfPlayer) return true;
				}
				foreach (object m in comp.Tanks)
				{
					if (m is Thing x && x.Faction == Faction.OfPlayer) return true;
				}
				foreach (RM_NetLink l in comp.Links)
				{
					if (l.Reel is Hose.CompHoseReel r && r.parent?.Faction == Faction.OfPlayer) return true;
				}
				foreach (RM_NetPort port in comp.Ports)
				{
					if (port.Reel is Hose.CompHoseReel r && r.parent?.Faction == Faction.OfPlayer) return true;
				}
			}
			return false;
		}

		/// <summary>The first member of <paramref name="victim"/> that can see the tank, or null (Gimme Some Slack's rule).</summary>
		public static Pawn Witness(Thing tank, Faction victim)
		{
			Map map = tank.Map;
			float range = RM_MachinerySettings.liquidTheftSightRange;
			foreach (Pawn p in map.mapPawns.SpawnedPawnsInFaction(victim))
			{
				if (p.RaceProps == null || !p.RaceProps.Humanlike)
				{
					continue;
				}
				float d = (p.Position - tank.Position).LengthHorizontal;
				if (d > range)
				{
					continue;
				}
				bool up = !p.Downed && !p.Dead && RestUtility.Awake(p);
				bool held = p.IsPrisonerOfColony || p.HostFaction == Faction.OfPlayer;
				// LIQUID_THEFT_FIX_TANK_HIDES_ITSELF: aim at the whole footprint. The 3-arg overload ends only at Position, and a
				// 2x2 tank's other cells (fillPercent 1) block the line, so a witness on their side never saw it.
				bool los = GenSight.LineOfSight(p.Position, tank.Position, map, CellRect.SingleCell(p.Position), tank.OccupiedRect());
				if (RM_LiquidTheftMath.TheftSpotted(d, range, los, up, held))
				{
					return p;
				}
			}
			return null;
		}
	}
}
