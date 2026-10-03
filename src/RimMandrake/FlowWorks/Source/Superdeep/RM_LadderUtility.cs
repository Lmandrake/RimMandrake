using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LADDERS — <i>"a building that makes a dug cell exitable — one boolean
	/// effect; removing the ladder strands whatever is down there."</i>
	///
	/// That is the whole mechanic and it is deliberately the whole mechanic. A
	/// ladder does NOT change pathing cost, passability or line of sight — it
	/// flips one gate in the grid trap rule (RM_SuperdeepTrap.IsHeld: nobody is
	/// held on a cell with a ladder in it), and the jailer mechanic falls out of
	/// it for free.
	/// </summary>
	public static class RM_LadderUtility
	{
		/// <summary>Is there a ladder standing in this cell? O(things-in-cell),
		/// which on an excavated cell is one or two.</summary>
		public static bool HasLadder(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return false;
			}
			ThingDef ladder = RimMandrakeFlowWorks_DefOf.RM_Ladder;
			if (ladder == null)
			{
				return false;
			}
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i].def == ladder)
				{
					return true;
				}
			}
			return false;
		}
	}

	/// <summary>
	/// LADDER_PRISON_DOOR_1 — owner Q1, 2026-10-02 (by card): a ladder works like a prison door.
	/// Lowered: your own people (and non-hostile visitors) climb it freely; trapped enemies and
	/// wild things do not; prisoners only during a prison break. Raised: nobody climbs, your own
	/// people included, so raising it with a colonist below strands them, by design ("jump into
	/// pit... stuck there too"). The state is toggled by the player's command on the ladder; a pawn
	/// standing in the pit has no way to reach it.
	/// </summary>
	public class RM_CompProperties_Ladder : CompProperties
	{
		public RM_CompProperties_Ladder()
		{
			compClass = typeof(RM_CompLadder);
		}
	}

	public class RM_CompLadder : ThingComp
	{
		public bool raised;

		public override IEnumerable<Gizmo> CompGetGizmosExtra()
		{
			foreach (Gizmo g in base.CompGetGizmosExtra())
			{
				yield return g;
			}
			if (parent.Faction != Faction.OfPlayer || !RimMandrakeFlowWorksSettings.ladderPrisonDoorEnabled)
			{
				yield break;
			}
			yield return new Command_Toggle
			{
				defaultLabel = raised ? "Ladder raised" : "Ladder lowered",
				defaultDesc = "Lowered, your people and friendly visitors can climb out of this pit; trapped enemies "
					+ "cannot, and prisoners only during a prison break. Raised, nobody can climb out, your own "
					+ "people included.",
				icon = TexCommand.ForbidOff,
				isActive = () => !raised,
				toggleAction = () => raised = !raised,
			};
		}

		public override string CompInspectStringExtra()
		{
			if (!RimMandrakeFlowWorksSettings.ladderPrisonDoorEnabled)
			{
				return null;
			}
			return raised
				? "Ladder raised: nobody can climb out."
				: "Ladder lowered: your people climb; prisoners only in a prison break.";
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref raised, "rmLadderRaised", false);
		}
	}

	public static class RM_LadderRules
	{
		/// <summary>Does the ladder in this cell (if any) let THIS pawn climb out? Without the prison-door
		/// setting any ladder lets anyone out, the pre-LADDER_PRISON_DOOR_1 rule.</summary>
		public static bool LadderLetsOut(Map map, IntVec3 c, Pawn p)
		{
			if (map == null || !c.InBounds(map))
			{
				return false;
			}
			ThingDef ladderDef = RimMandrakeFlowWorks_DefOf.RM_Ladder;
			if (ladderDef == null)
			{
				return false;
			}
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i].def != ladderDef)
				{
					continue;
				}
				if (!RimMandrakeFlowWorksSettings.ladderPrisonDoorEnabled)
				{
					return true;
				}
				RM_CompLadder comp = things[i].TryGetComp<RM_CompLadder>();
				if (comp != null && comp.raised)
				{
					return false;
				}
				return MayClimb(p);
			}
			return false;
		}

		/// <summary>The prison-door rule for a lowered ladder.</summary>
		public static bool MayClimb(Pawn p)
		{
			if (p == null)
			{
				return false;
			}
			if (p.IsPrisoner)
			{
				return PrisonBreakUtility.IsPrisonBreaking(p);
			}
			if (p.Faction == null)
			{
				return false; // wild animals and factionless pawns stay down
			}
			if (p.Faction == Faction.OfPlayer)
			{
				return true;
			}
			return Faction.OfPlayer != null && !p.Faction.HostileTo(Faction.OfPlayer);
		}
	}

	/// <summary>A ladder belongs in a hole. Refusing it on open ground is not
	/// pedantry — a ladder that can be built anywhere and does nothing anywhere
	/// else is a button that lies.</summary>
	public class PlaceWorker_LadderOnExcavation : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot,
			Map map, Thing thingToIgnore = null, Thing thing = null)
		{
			if (map == null)
			{
				return false;
			}
			RM_MapComponent_Excavation engine = map.GetComponent<RM_MapComponent_Excavation>();
			if (engine == null || !engine.IsExcavated(loc))
			{
				return "RMFlow_LadderNeedsExcavation".Translate();
			}
			return true;
		}
	}
}
