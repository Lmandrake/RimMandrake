using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS — teleportation (owner 2026-10-18: "... allow entrance/exit immediately, and
	/// teleportation, etc."): a skip into a pit lands without a fall. A skip OUT of a pit already works (a skip is a position
	/// change; nothing in the trap stops it). The tick detector would otherwise see a forced arrival on its next pass, so the
	/// arrival is marked handled. Setting pitTeleportLandsSafe.
	/// </summary>
	[HarmonyPatch(typeof(CompAbilityEffect_Teleport), nameof(CompAbilityEffect_Teleport.Apply))]
	[RimMandrake.Shared.PatchFeature("Teleports land safely in pits", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitTeleportLandsSafe")]
	public static class RM_Patch_TeleportLandsInPit
	{
		[HarmonyPostfix]
		public static void Postfix(LocalTargetInfo target)
		{
			if (!(target.Thing is Pawn p) || !p.Spawned || p.Dead
				|| !RM_PitAccessMath.LandsSafely(false, false, true, RimMandrakeFlowWorksSettings.pitTeleportLandsSafe))
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(p.Map);
			if (eng == null || !RM_SuperdeepTrap.AnyHole(eng))
			{
				return;
			}
			eng.SuperdeepTrap.NoteHandledArrival(p, p.Position);
		}
	}

	/// <summary>
	/// PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS — pit rescue (owner by card, 2026-10-18: "any colonist who can climb back out
	/// goes; if nobody can, a ladder job is queued first").
	///
	/// The first half is vanilla's rescue: our reachability (RM_SuperdeepTrap.RelativeVeto, the cliff masks) already lets only
	/// pawns who can climb down and back out reach the pit floor (climbing gear, a bigger creature, a usable ladder). This is
	/// the second half: every 250 ticks, a colonist lying downed in a pit no other colonist can reach, or stuck in a pit they
	/// cannot climb out of (RM_SuperdeepTrap.IsTrapped), gets a ladder job at the nearest wall of that pit, unless a ladder
	/// (built, framed or blueprinted) already stands in it. The choice is RM_PitAccessMath.ChooseRescueLadder (selftested):
	/// a spare portable ladder carried there (install), else a new portable one, else (too deep) the fixed wall ladder.
	/// Colonists then build it as any job; a ladder in a raised state already in that pit is the player's (the jailer
	/// mechanic), so none is added. Setting pitRescueLadderEnabled. Nothing scribed: the blueprints are the record.
	/// </summary>
	public class RM_MapComponent_PitRescueLadder : MapComponent
	{
		private const int CheckTicks = 250;
		private const int RequeueTicks = 2500;
		private const int SearchCap = 4000;

		private readonly Dictionary<Pawn, int> queuedAt = new Dictionary<Pawn, int>();
		private readonly List<Pawn> scratch = new List<Pawn>();

		public RM_MapComponent_PitRescueLadder(Map map) : base(map)
		{
		}

		public override void MapComponentTick()
		{
			int now = Find.TickManager.TicksGame;
			if (!RimMandrakeFlowWorksSettings.pitRescueLadderEnabled || (now + map.uniqueID) % CheckTicks != 0)
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null || !RM_SuperdeepTrap.AnyHole(eng) || RimMandrakeFlowWorks_DefOf.RM_Ladder == null)
			{
				return;
			}
			scratch.Clear();
			scratch.AddRange(map.mapPawns.FreeColonistsSpawned);
			for (int i = 0; i < scratch.Count; i++)
			{
				Pawn p = scratch[i];
				if (p.Dead || !p.Spawned || eng.ClimbDepthAt(p.Position) == 0
					|| (queuedAt.TryGetValue(p, out int at) && now - at < RequeueTicks))
				{
					continue;
				}
				TryQueueFor(p, eng, now);
			}
		}

		/// <summary>Queue a ladder job for this colonist if the owner's rule says so. Returns what it queued (for the bridge).</summary>
		public RM_PitAccessMath.RescueLadder TryQueueFor(Pawn p, RM_MapComponent_Excavation eng, int now)
		{
			bool downed = p.Downed;
			bool needsHelp = downed || RM_SuperdeepTrap.IsTrapped(p);
			if (!needsHelp)
			{
				return RM_PitAccessMath.RescueLadder.None;
			}
			// The pocket: the rescuers' (a person's) for a downed colonist, the colonist's own when it is stuck on its feet.
			int k = downed ? RM_PocketGrid.PersonBand : RM_PocketGrid.ClimbLimitOf(p);
			RM_PocketGrid g = RM_PocketGrid.For(map);
			int comp = g.ComponentOf(k, p.Position);
			if (comp < 0 || !g.ComponentIsPocket(k, comp))
			{
				return RM_PitAccessMath.RescueLadder.None;
			}
			bool anyone = downed && AnyRescuerReaches(p);
			if (anyone)
			{
				return RM_PitAccessMath.RescueLadder.None;
			}
			bool pending = LadderPendingIn(g, k, comp);
			if (!FindWall(eng, g, k, comp, p.Position, out IntVec3 cell, out Rot4 rot, out int drop))
			{
				return RM_PitAccessMath.RescueLadder.None;
			}
			int reach = RimMandrakeFlowWorksSettings.portableLadderMaxLevels;
			MinifiedThing spare = SparePortable(p);
			RM_PitAccessMath.RescueLadder choice = RM_PitAccessMath.ChooseRescueLadder(true, false, pending, drop, reach,
				spare != null, RimMandrakeFlowWorksSettings.portableLadderEnabled && RimMandrakeFlowWorks_DefOf.RM_LadderPortable != null);
			bool placed = false;
			switch (choice)
			{
				case RM_PitAccessMath.RescueLadder.InstallPortable:
					if (GenConstruct.CanPlaceBlueprintAt(RimMandrakeFlowWorks_DefOf.RM_LadderPortable, cell, rot, map, false, spare).Accepted)
					{
						GenConstruct.PlaceBlueprintForInstall(spare, cell, map, rot, Faction.OfPlayer);
						placed = true;
					}
					break;
				case RM_PitAccessMath.RescueLadder.BuildPortable:
					placed = PlaceBuild(RimMandrakeFlowWorks_DefOf.RM_LadderPortable, cell, rot);
					break;
				case RM_PitAccessMath.RescueLadder.BuildFixed:
					placed = PlaceBuild(RimMandrakeFlowWorks_DefOf.RM_Ladder, cell, rot);
					break;
			}
			queuedAt[p] = now;
			if (!placed)
			{
				return RM_PitAccessMath.RescueLadder.None;
			}
			Messages.Message("RMFlow_RescueLadderQueued".Translate(p.LabelShortCap), new TargetInfo(cell, map),
				MessageTypeDefOf.CautionInput, false);
			return choice;
		}

		private bool PlaceBuild(ThingDef def, IntVec3 cell, Rot4 rot)
		{
			if (def == null || !GenConstruct.CanPlaceBlueprintAt(def, cell, rot, map).Accepted)
			{
				return false;
			}
			GenConstruct.PlaceBlueprintForBuild(def, cell, map, rot, Faction.OfPlayer, null);
			return true;
		}

		/// <summary>Some other colonist on its feet reaches the downed one: vanilla's rescue sends them (they can climb back out,
		/// since our reachability is the same both ways).</summary>
		private bool AnyRescuerReaches(Pawn downed)
		{
			foreach (Pawn c in map.mapPawns.FreeColonistsSpawned)
			{
				if (c != downed && !c.Downed && !c.Dead && !c.InMentalState
					&& c.CanReach(downed, PathEndMode.ClosestTouch, Danger.Deadly))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>A ladder of either def, built, framed or blueprinted, already in this pocket.</summary>
		private bool LadderPendingIn(RM_PocketGrid g, int k, int comp)
		{
			foreach (Thing t in RM_LadderUtility.AllLadders(map, new List<Thing>()))
			{
				if (RM_LadderUtility.Reaches(t) && g.ComponentOf(k, t.Position) == comp)
				{
					return true;
				}
			}
			foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.Blueprint))
			{
				if (RM_LadderUtility.IsLadderDef(t.def.entityDefToBuild) && g.ComponentOf(k, t.Position) == comp)
				{
					return true;
				}
			}
			foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingFrame))
			{
				if (RM_LadderUtility.IsLadderDef(t.def.entityDefToBuild) && g.ComponentOf(k, t.Position) == comp)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>The nearest square of the pocket (breadth first from the colonist) with a shallower N/S/E/W neighbour
		/// outside the pocket: the wall a ladder hangs on. Prefers a wall a portable ladder reaches when there is one.</summary>
		private bool FindWall(RM_MapComponent_Excavation eng, RM_PocketGrid g, int k, int comp, IntVec3 start,
			out IntVec3 cell, out Rot4 rot, out int drop)
		{
			cell = IntVec3.Invalid;
			rot = Rot4.North;
			drop = 0;
			int reach = RimMandrakeFlowWorksSettings.portableLadderEnabled ? RimMandrakeFlowWorksSettings.portableLadderMaxLevels : 0;
			var seen = new HashSet<IntVec3> { start };
			var queue = new Queue<IntVec3>();
			queue.Enqueue(start);
			bool haveAny = false;
			while (queue.Count > 0 && seen.Count < SearchCap)
			{
				IntVec3 c = queue.Dequeue();
				int d = RM_SuperdeepTrap.StepDepthAt(map, eng, c);
				for (int r = 0; r < 4; r++)
				{
					IntVec3 o = c + new Rot4(r).FacingCell;
					if (!o.InBounds(map))
					{
						continue;
					}
					if (g.ComponentOf(k, o) == comp)
					{
						if (seen.Add(o))
						{
							queue.Enqueue(o);
						}
						continue;
					}
					int od = RM_SuperdeepTrap.StepDepthAt(map, eng, o);
					if (od >= d || !c.Standable(map) || RM_PitRamp.RampAt(map, c) != null || RM_LadderUtility.HasLadder(map, c))
					{
						continue;
					}
					bool portableFits = reach > 0 && d - od <= reach;
					if (!haveAny || (portableFits && drop > reach))
					{
						cell = c;
						rot = new Rot4(r);
						drop = d - od;
						haveAny = true;
						if (portableFits || reach <= 0)
						{
							return true;
						}
					}
				}
			}
			return haveAny;
		}

		/// <summary>A portable ladder lying about (minified), not forbidden and not already promised to an install job.</summary>
		private MinifiedThing SparePortable(Pawn forPawn)
		{
			ThingDef portable = RimMandrakeFlowWorks_DefOf.RM_LadderPortable;
			if (portable == null)
			{
				return null;
			}
			foreach (Thing t in map.listerThings.ThingsOfDef(ThingDefOf.MinifiedThing))
			{
				if (t is MinifiedThing m && m.InnerThing?.def == portable && m.Spawned && !m.IsForbidden(Faction.OfPlayer)
					&& InstallBlueprintUtility.ExistingBlueprintFor(m) == null)
				{
					return m;
				}
			}
			return null;
		}
	}
}
