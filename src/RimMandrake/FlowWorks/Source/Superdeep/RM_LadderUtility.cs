using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LADDERS — <i>"a building that makes a dug cell exitable — one boolean
	/// effect; removing the ladder strands whatever is down there."</i>
	///
	/// A USABLE ladder is the exit: one the pawn may climb (lowered, and allowed by
	/// the prison-door rule), read through RM_LadderRules.LadderLetsOut. The trap
	/// (RM_SuperdeepTrap.IsHeldAt) does not hold a pawn on such a cell, and
	/// RM_PitPathing plans routes and vetoes reachability by the same read; a
	/// raised ladder, or one the rule refuses this pawn, frees nobody. A ladder
	/// does not change path cost, passability or line of sight. HasLadder below is
	/// the raw presence read (the JawaBench bridge's), not the trap's gate.
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

		/// <summary>The ladder standing in this cell (a built one), or null.</summary>
		public static Thing LadderAt(Map map, IntVec3 c)
		{
			ThingDef ladder = RimMandrakeFlowWorks_DefOf.RM_Ladder;
			if (map == null || ladder == null || !c.InBounds(map))
			{
				return null;
			}
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i].def == ladder)
				{
					return things[i];
				}
			}
			return null;
		}

		/// <summary>PIT_LADDER_REDRAW_HUNG_ON_THE_WALL: the wall a ladder on this square hangs on, as a Rot4 index — the
		/// placed rotation when it faces a shallower neighbour, else the biggest drop (RM_LadderWallMath.Resolve); -1 when the
		/// square has no wall (or is not dug). Depths are STEP depths (an intact cover reads as ground), the same read the
		/// cliff masks and the pocket grid join by, so a ladder hung toward a covered pit beside it is a wall here too.</summary>
		public static int WallRotAt(Map map, IntVec3 c, Rot4 placed)
		{
			RM_MapComponent_Excavation eng = map?.GetComponent<RM_MapComponent_Excavation>();
			if (eng == null || !c.InBounds(map))
			{
				return -1;
			}
			int d = RM_SuperdeepTrap.StepDepthAt(map, eng, c);
			int[] sideD = new int[4];
			bool[] inB = new bool[4];
			for (int r = 0; r < 4; r++)
			{
				IntVec3 o = new IntVec3(c.x + RM_LadderWallMath.FX[r], 0, c.z + RM_LadderWallMath.FZ[r]);
				inB[r] = o.InBounds(map);
				sideD[r] = inB[r] ? RM_SuperdeepTrap.StepDepthAt(map, eng, o) : d;
			}
			return RM_LadderWallMath.Resolve(placed.AsInt, d, sideD, inB);
		}

		/// <summary>Does this ladder hang on the wall toward <paramref name="other"/> (its rotation faces that cell)? The
		/// depth half of the join is the caller's (the masks pass step depths).</summary>
		public static bool HangsToward(Thing ladder, IntVec3 other)
		{
			return ladder != null && RM_LadderWallMath.Faces(ladder.Rotation.AsInt, other.x - ladder.Position.x, other.z - ladder.Position.z);
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

		/// <summary>PIT_LADDER_REDRAW_HUNG_ON_THE_WALL: this ladder has been turned to its wall once (scribed). A save made
		/// before ladders turned has false, so its first load turns it; after that a reload keeps the saved rotation, so a
		/// ladder whose wall was filled in (or whose sides moved with a setting) does not swing onto another wall on load.</summary>
		public bool hung;
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
				// PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS: a lowered ladder is a structural edge in the cliff masks.
				parent.Map.GetComponent<RM_MapComponent_Excavation>()?.BumpClimbGeneration();
				// The masks re-check the generation only inside vanilla's incremental path update, which runs only on a cell
				// delta; a ladder toggle changes no vanilla cost, so push one (V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT).
				parent.Map.pathFinder?.MapData?.Notify_CellDelta(parent.Position);
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
			Scribe_Values.Look(ref hung, "rmLadderHung", false);
		}
	}

	/// <summary>Draws the raised art while raised (Building_PowerSwitch's shape).</summary>
	public class RM_Building_Ladder : Building
	{
		// V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT: a ladder is a structural edge in the cliff masks and the pocket grid; the climb
		// generation tells the masks. The masks re-check the generation only on a vanilla cell delta. Building.SpawnSetup and
		// DeSpawn already push one (map.events BuildingSpawned/BuildingDespawned -> PathFinderMapData.Notify_BuildingChanged,
		// decompiled 1.6), so the explicit delta here is belt and braces; the raise/lower toggle (SetRaised) has no vanilla
		// delta at all and must push its own. RM_Building_PitRamp relies on the vanilla one (RAMP_MASKS_VERIFY_STALE_SLOPE).
		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			// PIT_LADDER_REDRAW_HUNG_ON_THE_WALL: hang on a wall like a door between rooms. The placed rotation stands when it
			// faces a wall; otherwise (a dev spawn, a pre-rotation save, a blueprint placed before the cut beside it was dug)
			// turn to the wall with the biggest drop. No wall: keep the rotation; the ladder leads nowhere (the inspect says so).
			// A reload keeps a rotation already settled (RM_CompLadder.hung): live, a ladder whose wall is filled in stays
			// leading nowhere, and the reloaded game must agree.
			RM_CompLadder comp = GetComp<RM_CompLadder>();
			if (!respawningAfterLoad || comp == null || !comp.hung)
			{
				int wall = RM_LadderUtility.WallRotAt(map, Position, Rotation);
				if (wall >= 0 && wall != Rotation.AsInt)
				{
					Rotation = new Rot4(wall);
				}
			}
			if (comp != null)
			{
				comp.hung = true;
			}
			base.SpawnSetup(map, respawningAfterLoad);
			map.GetComponent<RM_MapComponent_Excavation>()?.BumpClimbGeneration();
			if (!respawningAfterLoad)
			{
				// The masks re-check the generation only inside vanilla's incremental path update, which runs only on a cell delta.
				map.pathFinder?.MapData?.Notify_CellDelta(Position);
			}
			map.reachability.ClearCache();
		}

		public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
		{
			Map map = Map;
			IntVec3 pos = Position;
			base.DeSpawn(mode);
			map?.GetComponent<RM_MapComponent_Excavation>()?.BumpClimbGeneration();
			map?.pathFinder?.MapData?.Notify_CellDelta(pos);
			map?.reachability.ClearCache();
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			string line = RM_LadderUtility.WallRotAt(Map, Position, Rotation) == Rotation.AsInt
				? "RMFlow_LadderHangsOn".Translate(("RMFlow_LadderWall" + Rotation.AsInt).Translate())
				: "RMFlow_LadderHangsOnNothing".Translate();
			return string.IsNullOrEmpty(s) ? line : s + "\n" + line;
		}

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

		/// <summary>PIT_LADDER_REDRAW_HUNG_ON_THE_WALL: does the ladder on <paramref name="deep"/> hang on the wall toward
		/// <paramref name="other"/> and let THIS pawn climb it? The edge read (the masks' per-pawn join).</summary>
		public static bool LadderLetsOutToward(Map map, IntVec3 deep, IntVec3 other, Pawn p)
		{
			return RM_LadderUtility.HangsToward(RM_LadderUtility.LadderAt(map, deep), other) && LadderLetsOut(map, deep, p);
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

	/// <summary>A ladder belongs in a hole, hung on one of its walls like a door between rooms. Refusing it on open ground
	/// is not pedantry — a ladder that can be built anywhere and does nothing anywhere else is a button that lies.
	/// PIT_LADDER_REDRAW_HUNG_ON_THE_WALL: the square must have a wall (a shallower N/S/E/W neighbour); the placed rotation
	/// picks which when it faces one, else the biggest drop (RM_LadderWallMath.Resolve). The ghost outlines the wall square.</summary>
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
			if (engine == null || engine.ClimbDepthAt(loc) == 0)
			{
				return "RMFlow_LadderNeedsExcavation".Translate();
			}
			// PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS (design §8.4): a square holds a ramp or a ladder, never both.
			if (RM_PitRamp.RampAt(map, loc) != null)
			{
				return "RMFlow_RampNotOnLadder".Translate();
			}
			return RM_LadderUtility.WallRotAt(map, loc, rot) >= 0 ? (AcceptanceReport)true : "RMFlow_LadderNeedsWall".Translate();
		}

		public override void DrawGhost(ThingDef def, IntVec3 center, Rot4 rot, Color ghostCol, Thing thing = null)
		{
			Map map = Find.CurrentMap;
			int wall = RM_LadderUtility.WallRotAt(map, center, rot);
			if (wall >= 0)
			{
				GenDraw.DrawFieldEdges(new List<IntVec3> { center + new Rot4(wall).FacingCell }, Color.white);
			}
		}
	}

	/// <summary>PIT_LADDER_REDRAW_HUNG_ON_THE_WALL: a ladder blueprint turns to its wall when placed, so the blueprint and the
	/// frame already hang where the ladder will (the building re-checks on spawn). Early-outs on every other def.</summary>
	[HarmonyPatch(typeof(GenConstruct), nameof(GenConstruct.PlaceBlueprintForBuild))]
	[RimMandrake.Shared.PatchFeature("Pit ladders turn to the wall they hang on")]
	public static class RM_Patch_LadderBlueprintFacesWall
	{
		public static void Prefix(BuildableDef sourceDef, IntVec3 center, Map map, ref Rot4 rotation)
		{
			if (sourceDef == null || sourceDef != RimMandrakeFlowWorks_DefOf.RM_Ladder)
			{
				return;
			}
			int wall = RM_LadderUtility.WallRotAt(map, center, rotation);
			if (wall >= 0)
			{
				rotation = new Rot4(wall);
			}
		}
	}
}
