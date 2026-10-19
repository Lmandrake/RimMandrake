using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FALL_GUARDRAILS_BUILD_REAL_OBJECT (owner, 2026-10-18: <i>"build guardrails as a real object with real need (and support
	/// existing fences acting this way too)."</i>). Deep falls can kill (FALL_DAMAGE_BUILD_DEEP_DROPS_KILL), so an unguarded lip
	/// is a hazard. A rail is our RM_PitGuardrail or any building whose def sets building.isFence; it stands on a lip cell and
	/// guards every edge from that cell down a sheer drop (RM_FallRailMath.GuardsEdge).
	///
	/// The doors, all at-event (never per tick):
	/// - a throw (a stun flyer: blast knockback, vanilla's PawnFlyer_Stun) that would land past a guarded edge stops at the rail
	///   (RM_Patch_PawnFlyer_LandInPit); a jump (a flyer with no stun: jump packs, abilities) is deliberate and is not stopped;
	/// - a forced arrival the descent detector sees (any other mover shoving a pawn one cell over the lip) is put back on the
	///   lip (RM_SuperdeepTrapState.Tick / ResolveArrivalNow); the jump-in order (TryJumpInto) marks a jumper and is not;
	/// - a walked step over a guarded edge is refused by the per-move floor (RM_Patch_PathFollower_SuperdeepFloor), the edge
	///   only: walking along the lip, onto the rail cell, or up out of the pit past it is untouched.
	/// What the design note had wrong: with the cliff masks on (the shipped relative rule) A* already holds every walked step
	/// that drops past a pawn's climb as a wall edge (RM_CliffMaskMath.AllowedBits, StepAllowed), so a rail adds no new A* edge;
	/// the walked guard matters for routes A* did not make edge-aware (masks off, stale paths, other mods' movers).
	/// A pit cover giving way (Building_PitCover) is a fall from ON the pit and is unaffected.
	/// Mod Setting pitGuardrailEnabled (off: no cell is a rail, the old behaviour; the building still stands).
	/// </summary>
	public static class RM_FallRails
	{
		public static bool On => RimMandrakeFlowWorksSettings.pitGuardrailEnabled;

		/// <summary>The one predicate: a built rail on this cell (our guardrail, a suspension bridge's railing, or any fence def).</summary>
		public static bool IsRail(Map map, IntVec3 c)
		{
			if (!On || map == null || !c.InBounds(map))
			{
				return false;
			}
			List<Thing> things = map.thingGrid.ThingsListAtFast(c);
			for (int i = 0; i < things.Count; i++)
			{
				Thing t = things[i];
				ThingDef d = t.def;
				if (d.building != null && RM_FallRailMath.IsRailThing(true, t is Building && !(t is Frame),
					d == RimMandrakeFlowWorks_DefOf.RM_PitGuardrail || t is Pits.Building_SuspensionRailing, d.building.isFence))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Is <paramref name="from"/> → <paramref name="to"/> (8-adjacent) a guarded edge for this pawn: a fall for it
		/// (relative rule: down more than it climbs; absolute rule: shallower into an open 2 m cell) leaving a railed cell.
		/// Depths first, the thing-grid read last.</summary>
		public static bool Guards(Map map, RM_MapComponent_Excavation eng, Pawn p, IntVec3 from, IntVec3 to)
		{
			if (!On || map == null || eng == null || !from.InBounds(map) || !to.InBounds(map) || !from.AdjacentTo8Way(to))
			{
				return false;
			}
			bool fall;
			if (RM_PocketGrid.Relative)
			{
				int fromD = RM_SuperdeepTrap.StepDepthAt(map, eng, from);
				int toD = RM_SuperdeepTrap.StepDepthAt(map, eng, to);
				fall = RM_FallRailMath.GuardsEdge(true, fromD, toD, RM_FallRailMath.FallNotchesFor(RM_PocketGrid.ClimbLimitOf(p)));
			}
			else
			{
				fall = RM_PitPathing.IsOpenPit(map, eng, to) && !RM_PitPathing.IsOpenPit(map, eng, from);
			}
			return fall && IsRail(map, from);
		}

		/// <summary>The detector's door: a forced (or stale walked) one-cell arrival over a guarded edge, not by a jumper, back
		/// onto a cell the pawn can stand on.</summary>
		public static bool StopsArrival(Map map, RM_MapComponent_Excavation eng, Pawn p, IntVec3 prev, IntVec3 pos)
		{
			if (!On || p == null)
			{
				return false;
			}
			bool deliberate = eng.SuperdeepTrap.IsJumper(p);
			return RM_FallRailMath.FallBlocked(!deliberate && Guards(map, eng, p, prev, pos), deliberate) && prev.Standable(map);
		}

		/// <summary>Puts a stopped pawn back on the lip: position, tweener and pather reset, job kept.</summary>
		public static void PutBack(Pawn p, IntVec3 cell)
		{
			p.Position = cell;
			p.Notify_Teleported(false, true);
		}

		/// <summary>The walked-step door: refuse a step over a guarded edge unless a ladder or ramp this pawn may use joins it.
		/// Flyers are never refused.</summary>
		public static bool RefusesWalkedStep(Pawn pawn, RM_MapComponent_Excavation eng, IntVec3 next)
		{
			if (!On || pawn == null || pawn.Flying || RM_PocketGrid.CanFly(pawn))
			{
				return false;
			}
			Map map = pawn.Map;
			IntVec3 from = pawn.Position;
			if (!Guards(map, eng, pawn, from, next))
			{
				return false;
			}
			if (RM_PocketGrid.Relative)
			{
				int fromD = RM_SuperdeepTrap.StepDepthAt(map, eng, from);
				int toD = RM_SuperdeepTrap.StepDepthAt(map, eng, next);
				return !RM_ClimbJoins.ForPawn(map, eng, from, next, fromD, toD, pawn, out _, out _);
			}
			return !RM_LadderRules.LadderLetsOut(map, next, pawn);
		}

		/// <summary>The throw's door: where a throw from <paramref name="start"/> to <paramref name="land"/> stops at a rail, or
		/// Invalid when it crosses no guarded edge.</summary>
		public static IntVec3 ThrowStop(Map map, RM_MapComponent_Excavation eng, Pawn p, IntVec3 start, IntVec3 land)
		{
			if (!On || map == null || eng == null || !start.InBounds(map) || !land.InBounds(map) || start == land)
			{
				return IntVec3.Invalid;
			}
			List<(int x, int z)> line = RM_FallRailMath.Line(start.x, start.z, land.x, land.z);
			int i = RM_FallRailMath.ThrowStopIndex(line.Count,
				k => Guards(map, eng, p, new IntVec3(line[k].x, 0, line[k].z), new IntVec3(line[k + 1].x, 0, line[k + 1].z)),
				k => new IntVec3(line[k].x, 0, line[k].z).Standable(map));
			return i < 0 ? IntVec3.Invalid : new IntVec3(line[i].x, 0, line[i].z);
		}

		/// <summary>Placement: a cell beside a sheer drop for a person (the person band's climb), covers read as ground.
		/// Null = accepted, otherwise the refusal reason.</summary>
		public static string PlacementRefusal(Map map, IntVec3 c)
		{
			RM_MapComponent_Excavation eng = map?.GetComponent<RM_MapComponent_Excavation>();
			if (eng == null || !c.InBounds(map))
			{
				return "RMFlow_GuardrailNeedsDrop".Translate();
			}
			bool ok = RM_FallRailMath.HasDropBeside((x, z) =>
			{
				IntVec3 n = new IntVec3(x, 0, z);
				return n.InBounds(map) ? RM_SuperdeepTrap.StepDepthAt(map, eng, n) : -1;
			}, c.x, c.z, RM_FallRailMath.FallNotchesFor(RM_PocketGrid.PersonBand));
			return ok ? null : (string)"RMFlow_GuardrailNeedsDrop".Translate();
		}

		/// <summary>Bridge/proof read: "RAIL rail=b guards=N/8 on=b".</summary>
		public static string ProofRail(Map map, IntVec3 c, Pawn p = null)
		{
			RM_MapComponent_Excavation eng = map?.GetComponent<RM_MapComponent_Excavation>();
			int guarded = 0;
			if (eng != null)
			{
				foreach (IntVec3 n in GenAdj.CellsAdjacent8Way(new TargetInfo(c, map)))
				{
					if (Guards(map, eng, p, c, n))
					{
						guarded++;
					}
				}
			}
			return "RAIL rail=" + IsRail(map, c) + " guards=" + guarded + "/8 on=" + On;
		}
	}

	/// <summary>A guardrail stands only where it guards something: beside a sheer drop (RM_FallRails.PlacementRefusal).</summary>
	public class PlaceWorker_PitGuardrail : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot,
			Map map, Thing thingToIgnore = null, Thing thing = null)
		{
			if (map == null)
			{
				return false;
			}
			string why = RM_FallRails.PlacementRefusal(map, loc);
			return why == null ? AcceptanceReport.WasAccepted : new AcceptanceReport(why);
		}
	}
}
