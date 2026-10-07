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
	/// LADDER_PRISON_DOOR_1 — owner Q1, 2026-10-02 (by card): a lowered ladder works like a prison door. Your own
	/// people (and non-hostile visitors) climb it; trapped enemies and wild things do not; prisoners only during a
	/// prison break.
	///
	/// FLOWWORKS_LADDER_RAISE_LOWER_1 — owner, 2026-10-06: <i>"Ladders should be able to be raised and lowered (two
	/// states for the ladder)... The ladder should be clickable by the user: ladder up, ladder down. No need to have
	/// the colonists automatically move them up and down."</i> Lowered: pawns path down into the pit by it and back
	/// out, and haulers fetch what lies on the floor (RM_PitPathing's entry veto credits only a usable ladder).
	/// Raised: nobody climbs it, either way. Only the player's gizmo moves it; no job or AI ever does. Scribed.
	/// </summary>
	public class RM_CompProperties_Ladder : CompProperties
	{
		/// <summary>The raised state's own art. Null = the def's graphic in both states (art pending).</summary>
		public GraphicData raisedGraphicData;

		public RM_CompProperties_Ladder()
		{
			compClass = typeof(RM_CompLadder);
		}
	}

	public class RM_CompLadder : ThingComp
	{
		public bool raised;
		private Graphic raisedGraphic;

		public RM_CompProperties_Ladder Props => (RM_CompProperties_Ladder)props;

		/// <summary>Raised as far as the rules are concerned (the setting off = always lowered).</summary>
		public bool EffectivelyRaised => raised && RimMandrakeFlowWorksSettings.ladderRaiseLowerEnabled;

		public Graphic RaisedGraphic
		{
			get
			{
				if (raisedGraphic == null && Props.raisedGraphicData != null)
				{
					raisedGraphic = Props.raisedGraphicData.GraphicColoredFor(parent);
				}
				return raisedGraphic;
			}
		}

		/// <summary>The one writer of the state: the gizmo (and the bridge proof tool, which calls this).</summary>
		public void SetRaised(bool value)
		{
			if (raised == value)
			{
				return;
			}
			raised = value;
			if (parent.Spawned)
			{
				parent.Map.mapDrawer.MapMeshDirty(parent.Position, (ulong)MapMeshFlagDefOf.Buildings | (ulong)MapMeshFlagDefOf.Things);
				// Routes and reachability planned against the old state are stale now.
				parent.Map.reachability.ClearCache();
			}
		}

		public override IEnumerable<Gizmo> CompGetGizmosExtra()
		{
			foreach (Gizmo g in base.CompGetGizmosExtra())
			{
				yield return g;
			}
			if (parent.Faction != Faction.OfPlayer || !RimMandrakeFlowWorksSettings.ladderRaiseLowerEnabled)
			{
				yield break;
			}
			yield return new Command_Toggle
			{
				defaultLabel = (raised ? "RMFlow_LadderUp" : "RMFlow_LadderDown").Translate(),
				defaultDesc = "RMFlow_LadderToggleDesc".Translate(),
				icon = raised ? TexCommand.ForbidOn : TexCommand.ForbidOff,
				isActive = () => !raised,
				toggleAction = () => SetRaised(!raised),
			};
		}

		public override string CompInspectStringExtra()
		{
			if (!RimMandrakeFlowWorksSettings.ladderRaiseLowerEnabled && !RimMandrakeFlowWorksSettings.ladderPrisonDoorEnabled)
			{
				return null;
			}
			if (EffectivelyRaised)
			{
				return "RMFlow_LadderRaisedInspect".Translate();
			}
			return RimMandrakeFlowWorksSettings.ladderPrisonDoorEnabled
				? "RMFlow_LadderLoweredPrisonInspect".Translate()
				: "RMFlow_LadderLoweredInspect".Translate();
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref raised, "rmLadderRaised", false);
		}
	}

	/// <summary>Draws the raised art while raised (Building_PowerSwitch's shape).</summary>
	public class RM_Building_Ladder : Building
	{
		public override Graphic Graphic
		{
			get
			{
				RM_CompLadder comp = GetComp<RM_CompLadder>();
				Graphic g = comp != null && comp.EffectivelyRaised ? comp.RaisedGraphic : null;
				return g ?? base.Graphic;
			}
		}
	}

	public static class RM_LadderRules
	{
		/// <summary>Does the ladder in this cell (if any) let THIS pawn climb it, down or up?</summary>
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
				RM_CompLadder comp = things[i].TryGetComp<RM_CompLadder>();
				return RM_PitTrapMath.LadderUsable(RimMandrakeFlowWorksSettings.ladderRaiseLowerEnabled,
					comp != null && comp.raised, RimMandrakeFlowWorksSettings.ladderPrisonDoorEnabled, MayClimb(p));
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
