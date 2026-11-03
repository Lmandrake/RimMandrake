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
			if (!On || pawn == null || pawn.Flying || RM_PocketGrid.FreePitTraveller(pawn))
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

		/// <summary>RAIL_WALK_PROVE_NOBODY_WALKS_OFF_ANYWAY: the walked-step door's live control (jawa/static_call; dev surface,
		/// nothing in the game calls it). arg "pawnId;lipX,lipZ;dropX,dropZ[;force]". Sets the pawn on the lip (jobs stopped,
		/// the detector told it arrived there), then asks the REAL per-move floor (RM_Patch_PathFollower_SuperdeepFloor.Prefix,
		/// pather.nextCell = the drop cell, restored after) whether the step is walked, and which door refuses it
		/// (RM_FallRailMath.WalkedStepDoor: "rail" on a railed lip; "floor" on an unrailed one with the cliff masks on, because
		/// nobody walks off a lip anyway). With "force" it then makes the step the floor refused, marked WALKED
		/// (NoteWalkedStep, as RM_PitPathing's postfix marks a real step): the stale-walked arrival the detector judges on its
		/// next pass, put back on a railed lip and a fall on an unrailed one (read with RM_NorthstarProofs.ProofTrap).
		/// Writes the pawn's position, its jobs and the detector's arrival marks only.
		/// "WALK rail=b isRail=b guards=b floorRefuses=b prefixPass=b door=D falls=b expect=E forced=b".</summary>
		public static string ProofWalkedStep(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			string[] a = (arg ?? "").Split(';');
			if (map == null || eng == null || a.Length < 3 || a.Length > 4 || (a.Length == 4 && a[3] != "force")
				|| !ProofCell(a[1], out IntVec3 lip) || !ProofCell(a[2], out IntVec3 drop)
				|| !lip.InBounds(map) || !drop.InBounds(map) || !lip.AdjacentTo8Way(drop))
			{
				return "REFUSED: arg must be pawnId;lipX,lipZ;dropX,dropZ[;force], two adjacent in-bounds cells on a map with an excavation engine";
			}
			Pawn p = null;
			foreach (Pawn q in map.mapPawns.AllPawnsSpawned)
			{
				if (q.ThingID == a[0] || q.thingIDNumber.ToString() == a[0])
				{
					p = q;
					break;
				}
			}
			if (p == null || p.pather == null)
			{
				return "REFUSED: no spawned pawn " + a[0];
			}
			p.jobs?.StopAll();
			p.pather.StopDead();
			if (p.Position != lip)
			{
				p.Position = lip;
				p.Notify_Teleported(false, true);
			}
			eng.SuperdeepTrap.NoteHandledArrival(p, lip);
			bool rail = RefusesWalkedStep(p, eng, drop);
			bool floorRefuses = RM_PocketGrid.Relative
				? !RM_Patch_PathFollower_SuperdeepFloor.RelativeStepAllowed(p, eng, drop)
				: RM_PitTrapMath.StepBlocked(RM_SuperdeepTrap.IsHeld(p), Pits.RM_PitCoverUtility.IsCovered(map, drop) ? 0 : eng.ExcavatedDepthAt(drop));
			IntVec3 keep = p.pather.nextCell;
			p.pather.nextCell = drop;
			bool prefixPass;
			try
			{
				prefixPass = RM_Patch_PathFollower_SuperdeepFloor.Prefix(p.pather, p);
			}
			finally
			{
				p.pather.nextCell = keep;
			}
			int fromD = RM_SuperdeepTrap.StepDepthAt(map, eng, lip);
			int toD = RM_SuperdeepTrap.StepDepthAt(map, eng, drop);
			bool climbsDown = RM_PocketGrid.ClimbsOnGear(p) || RM_PitRamp.Joins(map, lip, drop, fromD, toD);
			bool falls = RM_PitTrapMath.DescentFalls(true, RM_LadderRules.LadderLetsOut(map, drop, p) || climbsDown,
				p.Faction == Faction.OfPlayer, RM_SuperdeepTrap.Captures(p));
			bool guards = Guards(map, eng, p, lip, drop);
			string expect = RM_FallRailMath.WalkedArrivalEnds(falls, guards, eng.SuperdeepTrap.IsJumper(p), lip.Standable(map));
			bool forced = a.Length == 4;
			if (forced)
			{
				eng.SuperdeepTrap.NoteWalkedStep(p, drop);
				p.Position = drop;
				p.Notify_Teleported(false, false);
			}
			return "WALK rail=" + rail + " isRail=" + IsRail(map, lip) + " guards=" + guards + " floorRefuses=" + floorRefuses
				+ " prefixPass=" + prefixPass + " door=" + RM_FallRailMath.WalkedStepDoor(rail, floorRefuses) + " falls=" + falls
				+ " expect=" + expect + " forced=" + forced;
		}

		private static bool ProofCell(string s, out IntVec3 c)
		{
			c = IntVec3.Invalid;
			string[] p = (s ?? "").Split(',');
			if (p.Length != 2 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z))
			{
				return false;
			}
			c = new IntVec3(x, 0, z);
			return true;
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
