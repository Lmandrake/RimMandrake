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
	/// L9: successful player-caused tank mutations, netted per liquid per pump cycle.
	/// Machine/pawn/job entry scopes supply the actor; tank mutation methods record the
	/// signed change, so transfer put-backs cancel, including partial split rollback.
	/// Reachability and total stock changes are not actor evidence: owner activity may
	/// reach player equipment or exactly replenish a real withdrawal. Witness/caught
	/// state and the power-theft goodwill rule remain unchanged. Pending changes are
	/// saved with each tank; unscoped setup/debug writes are not player transfers.
	/// </summary>
	public static class RM_LiquidTheft
	{
		/// <summary>State read (probe, selftests).</summary>
		public static int caught, charges, goodwillCharged;

        [System.ThreadStatic] private static Thing actor;

        /// <summary>Lexical main-thread actor boundary, including credits/hose fills.
        /// Always restore the previous actor, even on early returns and exceptions.
        /// Owner/unowned nested entries mask an outer player's scope.</summary>
        public struct ActorScope : System.IDisposable
        {
            private readonly Thing previous;
            public ActorScope(Thing current)
            {
                previous = actor;
                actor = current;
            }
            public void Dispose() { actor = previous; }
        }

        public static ActorScope As(Thing current)
        {
            return new ActorScope(current);
        }

        /// <summary>Called only after a tank mutation passed validation, before an
        /// emptying removal clears its liquid identity. Undo uses the same actor.
        /// No component/global tank set is credited; only this tank changed.</summary>
        public static void Record(Building_LiquidTank tank, LiquidDef liquid, int delta)
        {
            if (!RM_MachinerySettings.liquidTheftEnabled)
            {
                tank.theftPlayerChanges.Clear();
                tank.theftPendingVictim = null;
                return;
            }
            if (actor?.Faction != Faction.OfPlayer || actor.Map != tank.Map || !RM_LiquidNet.IsForeign(tank)) return;
            if (tank.theftPendingVictim != tank.Faction)
            {
                tank.theftPlayerChanges.Clear();
                tank.theftPendingVictim = tank.Faction;
            }
            RM_LiquidTheftMath.RecordChange(tank.theftPlayerChanges, liquid, delta);
        }

		public static void TheftTick(Map map)
		{
			if (map == null)
			{
				return;
			}
			foreach (Thing th in map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial))
			{
                if (!(th is Building_LiquidTank t)) continue;
                Faction victim = t.Faction;
                bool touched = t.theftPendingVictim == victim && RM_LiquidTheftMath.HasChanges(t.theftPlayerChanges);
                // Consume on every pass, even disabled, claimed, defeated or unwitnessed.
                // Thus a witness arriving later cannot catch a past, unseen move.
                t.theftPlayerChanges.Clear();
                t.theftPendingVictim = null;
                if (!RM_MachinerySettings.liquidTheftEnabled || !RM_LiquidNet.IsForeign(t)
                    || !touched || victim == null || victim.defeated)
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

        /// <summary>Paused dev proof adapter: "x,z;read|tick|prime". Read is observational;
        /// tick invokes the real map TheftTick, bypassing only its 250-tick scheduling.
        /// Prime requires an already-caught tank and sets only the remainder to one
        /// cycle short of a day, allowing a real next transfer to test vanilla goodwill
        /// without advancing a populated site for a day. No transfer/witness is fabricated.</summary>
        public static string Proof(string arg)
        {
            string[] a = (arg ?? "").Split(';');
            string[] pos = a[0].Split(',');
            Map map = Find.CurrentMap;
            if (a.Length != 2 || pos.Length != 2 || !int.TryParse(pos[0], out int x) || !int.TryParse(pos[1], out int z)
                || map == null || (a[1] != "read" && a[1] != "tick" && a[1] != "prime")) return "REFUSED: x,z;read|tick|prime";
            IntVec3 c = new IntVec3(x, 0, z);
            Building_LiquidTank tank = c.InBounds(map) ? c.GetFirstBuilding(map) as Building_LiquidTank : null;
            if (tank == null) return "REFUSED: tank required";
            if (a[1] != "read")
            {
                if (!Prefs.DevMode || !Find.TickManager.Paused) return "REFUSED: paused dev mode required";
                if (a[1] == "prime")
                {
                    if (tank.theftCaughtBy == null || tank.theftCaughtBy != tank.Faction) return "REFUSED: caught tank required";
                    tank.theftTicks = GenDate.TicksPerDay - RM_PumpMath.CycleTicks;
                }
                else TheftTick(map);
            }
            Pawn witness = tank.Faction == null ? null : Witness(tank, tank.Faction);
            string pending = string.Join(",", System.Linq.Enumerable.Select(tank.theftPlayerChanges, p => p.Key.defName + ":" + p.Value));
            return "THEFT tank=" + tank.ThingID + " faction=" + tank.Faction?.GetUniqueLoadID()
                + " units=" + tank.storedUnits + " liquid=" + (tank.storedLiquid?.defName ?? "none")
                + " pending=[" + pending + "] caughtBy=" + (tank.theftCaughtBy?.GetUniqueLoadID() ?? "none")
                + " ticks=" + tank.theftTicks + " caught=" + caught + " charges=" + charges + " goodwill=" + goodwillCharged
                + " victimGoodwill=" + (tank.Faction?.PlayerGoodwill ?? 0) + " reach=" + PlayerReaches(tank)
                + " witness=" + (witness?.ThingID ?? "none");
        }

		/// <summary>C1-F14: is <paramref name="t"/> on a net with anything of the player's (a machine or tank on one of its
		/// components, a player reel's hose on one, or a player machine touching it)? Opportunity diagnostic only; never attribution.</summary>
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
