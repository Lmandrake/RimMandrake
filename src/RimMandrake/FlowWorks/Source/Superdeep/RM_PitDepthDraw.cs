using System;
using HarmonyLib;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_DEPTH_DRAW_OFFSET_1 — a pawn is drawn lower the deeper the dug cell it stands
	/// in, and rises again as it walks out. LAW 2 (depth never touches sight; its only effect on shooting is
	/// trench cover, RM_TrenchCover):
	/// the patched getter, Pawn_DrawTracker.DrawPos, is also what vanilla launches shots from
	/// (Verb_LaunchProjectile.TryCastShot's caster.DrawPos, arc-spray, beam and spray aim), so
	/// the sink is switched OFF while a verb fires (<see cref="RM_Patch_PitDepthDrawCombatOrigin"/>):
	/// every shot leaves from where the pawn would stand unsunk, and shield-bubble and intercept
	/// tests see the unsunk origin.
	///
	/// Reads the HOLLOW depth (<see cref="RM_MapComponent_Excavation.HollowDepthAt"/>: dug, or a dry pond bed's, POND_BED step 2), not
	/// <c>DepthAt</c>: natural water reads through as SUPERDEEP there, and a pawn wading a
	/// vanilla river must not vanish 1.2 cells into it — vanilla draws its own swimming.
	/// Fluid in a canal does not lift a WADER: the occupant stays down on the floor
	/// (<c>slime_occupant_below_surface</c>); a pawn that floats (head under, swimmable water) is drawn at the surface
	/// (<see cref="DrawHollow"/>, DEEP_PIT_SWIM_FIX_FIVE_METRES_WALKS).
	///
	/// Flying pawns are skipped (vanilla lifts them; a flier over a pit is above it).
	/// Numbers are PROVISIONAL — see <see cref="RM_PitDrawMath"/>; live check owed.
	/// Harmony bootstrap: RM_FlowWorksHarmony's PatchApplier.Apply in RM_Patch_SuperdeepShooting.cs.
	/// </summary>
	[HarmonyPatch(typeof(Pawn_DrawTracker), nameof(Pawn_DrawTracker.DrawPos), MethodType.Getter)]
	[RimMandrake.Shared.PatchFeature("Pawns sink into dug channels", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitDepthDrawOffsetEnabled")]
	public static class RM_Patch_PitDepthDrawOffset
	{
		private static readonly AccessTools.FieldRef<Pawn_DrawTracker, Pawn> PawnRef =
			AccessTools.FieldRefAccess<Pawn_DrawTracker, Pawn>("pawn");

		private static Map cachedMap;

		private static RM_MapComponent_Excavation cachedComp;

		[HarmonyPostfix]
		public static void Postfix(Pawn_DrawTracker __instance, ref Vector3 __result)
		{
			if (!RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled || RM_Patch_PitDepthDrawCombatOrigin.Firing > 0)
			{
				return;   // off, or a verb is firing: shots leave from the unsunk position (no height advantage)
			}
			Pawn pawn = PawnRef(__instance);
			if (pawn == null || !pawn.Spawned || pawn.Flying)
			{
				return;
			}
			ClimbOnLadderSpan(pawn, ref __result);
			float sink = SinkOf(pawn, __result);
			if (sink > 0f)
			{
				__result.z -= sink;
			}
		}

		/// <summary>RIMMANDRAKE_FIX_CLIMB_SLOW_OUTLASTS_LADDER (owner 2026-11-12: pawns "remain in the slowed/climbing mode long
		/// after they visually leave the ladder ... should be altered to only correspond when they are crossing the ladder
		/// texture itself"). A ladder climb is ONE path step (pit floor to lip) costing RM_PitStepCost's ladder cost, and vanilla
		/// tweens the pawn along it at one steady pace, so with the sink the slow crawl covered 1 + sink cells (2.2 at depth 4)
		/// while the ladder's picture spans 0.6. The step's time is left as it is; only where the pawn is DRAWN within it moves:
		/// walking pace off the ladder's span, all the rest of the time on it (RM_PitDrawMath.ClimbProgress). The drawn
		/// position is moved along the step before the sink is read, so the sink follows the same progress.</summary>
		private static void ClimbOnLadderSpan(Pawn pawn, ref Vector3 drawPos)
		{
			Pawn_PathFollower pather = pawn.pather;
			if (pather == null || !pather.Moving || !pather.nextCell.IsValid || pather.nextCellCostTotal <= 0f)
			{
				return;
			}
			IntVec3 from = pawn.Position, to = pather.nextCell;
			if (from.x != to.x && from.z != to.z || from == to || ExcavationOf(pawn.Map) == null)
			{
				return;
			}
			Thing ladder = ClimbLadderOf(pawn.Map, from, to);
			bool alongZ = from.x == to.x;
			if (!LadderArtSpan(ladder, alongZ, out float lo, out float hi))
			{
				return;
			}
			Vector3 a = from.ToVector3Shifted(), b = to.ToVector3Shifted();
			// the drawn centre's path on the step axis: the sink moves it on z only
			float pa = alongZ ? a.z - RestingSinkAt(pawn, from) : a.x;
			float pb = alongZ ? b.z - RestingSinkAt(pawn, to) : b.x;
			if (!RM_PitDrawMath.LadderSpanOnStep(pa, pb, lo, hi, out float u0, out float u1))
			{
				return;
			}
			float r = RM_PitDrawMath.WalkShare(Math.Abs(pb - pa), pawn.TicksPerMoveCardinal, pather.nextCellCostTotal);
			// t: where vanilla's (sprung) tween draws it along the step; u: where it belongs at this share of the step's time
			float t = RM_PitDrawMath.StepProgress(a.x, a.z, b.x, b.z, drawPos.x, drawPos.z);
			float u = RM_PitDrawMath.ClimbProgress(pather.MovePercentage, u0, u1, r);
			drawPos.x += (b.x - a.x) * (u - t);
			drawPos.z += (b.z - a.z) * (u - t);
		}

		/// <summary>The lowered ladder a step from <paramref name="from"/> to <paramref name="to"/> climbs: one in either end, hung
		/// on the wall toward the other (up and down alike), or null. Public for the proof read (ProofLadderClimbDraw).</summary>
		public static Thing ClimbLadderOf(Map map, IntVec3 from, IntVec3 to)
		{
			if (RM_ClimbJoins.LoweredLadderAt(map, from) && RM_LadderUtility.HangsToward(RM_LadderUtility.LadderAt(map, from), to))
			{
				return RM_LadderUtility.LadderAt(map, from);
			}
			if (RM_ClimbJoins.LoweredLadderAt(map, to) && RM_LadderUtility.HangsToward(RM_LadderUtility.LadderAt(map, to), from))
			{
				return RM_LadderUtility.LadderAt(map, to);
			}
			return null;
		}

		/// <summary>The ladder art's opaque extent in world cells on the climb's axis (z when <paramref name="alongZ"/>, else x):
		/// the def's climbSpan for its facing over the quad its graphic is drawn on.</summary>
		public static bool LadderArtSpan(Thing ladder, bool alongZ, out float lo, out float hi)
		{
			lo = hi = 0f;
			RM_CompProperties_Ladder props = ladder?.def.GetCompProperties<RM_CompProperties_Ladder>();
			Graphic g = ladder?.Graphic;
			if (props == null || g == null)
			{
				return false;
			}
			Vector3 centre = ladder.Position.ToVector3Shifted() + g.DrawOffset(ladder.Rotation);
			float size = alongZ ? g.drawSize.y : g.drawSize.x;
			float edge = (alongZ ? centre.z : centre.x) - size * 0.5f;
			FloatRange span = props.ClimbSpan(ladder.Rotation);
			lo = edge + span.min * size;
			hi = edge + span.max * size;
			return true;
		}

		/// <summary>The current sink of a spawned pawn, in cells. Public so a companion
		/// [Tool] can state-read it for the northstar bars without a frame.</summary>
		public static float SinkOf(Pawn pawn, Vector3 drawPos)
		{
			RM_MapComponent_Excavation ex = ExcavationOf(pawn.Map);
			if (ex == null)
			{
				return 0f;
			}
			float perLevel = RimMandrakeFlowWorksSettings.pitSinkPerLevel;
			IntVec3 from = pawn.Position;
			// SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD: on a suspension deck the pawn sinks to the deck's height (none at the
			// surface), under it (floor band) to the hole's floor
			int dFrom = Pits.RM_SuspensionUnderpass.DrawDepth(pawn, from, DrawHollow(pawn, ex, from));
			if (pawn.pather == null || !pawn.pather.Moving)
			{
				// PIT_BOAR_FIX_SUNBATHES_ON_THE_WALL: the tween may lag (or, paused, freeze) behind Position: hold the drawn centre
				return Held(Clamped(ex, pawn.Map, from, dFrom, perLevel), drawPos, dFrom);
			}
			IntVec3 to = pawn.pather.nextCell;
			int dTo = to.IsValid ? Pits.RM_SuspensionUnderpass.DrawDepth(pawn, to, DrawHollow(pawn, ex, to)) : dFrom;
			if (dFrom == 0 && dTo == 0)
			{
				return 0f;
			}
			Vector3 a = from.ToVector3Shifted();
			Vector3 b = to.ToVector3Shifted();
			float t = RM_PitDrawMath.StepProgress(a.x, a.z, b.x, b.z, drawPos.x, drawPos.z);
			float sa = Clamped(ex, pawn.Map, from, dFrom, perLevel);
			float sb = to.IsValid ? Clamped(ex, pawn.Map, to, dTo, perLevel) : sa;
			// the shallower end's lip, so a step onto a shelf eases instead of popping; 0 (stepping in from ground) holds nothing
			return Held(sa + (sb - sa) * t, drawPos, Math.Min(dFrom, dTo));
		}

		/// <summary>DEEP_PIT_SWIM_FIX_FIVE_METRES_WALKS: the hole depth the sink reads on <paramref name="c"/>. A pawn that floats
		/// there (Swimming.RM_Patch_Pawn_SwimPose.SwimsAt: head under, swimmable water) is drawn at the water's SURFACE
		/// (RM_SwimMath.SurfaceDrawDepth); a wader or a pawn on a dry floor stays down on the floor, as before.</summary>
		public static int DrawHollow(Pawn pawn, RM_MapComponent_Excavation ex, IntVec3 c)
		{
			int h = ex.HollowDepthAt(c);
			if (h <= 0 || !Swimming.RM_Patch_Pawn_SwimPose.SwimsAt(pawn, c))
			{
				return h;
			}
			return RM_SwimMath.SurfaceDrawDepth(h, (int)(ex.WaterDlAt(c) / RM_LevelSolve.U));
		}

		/// <summary>PIT_CLICK_FIX_SHIFTED_ONE_DOWN: the sink of <paramref name="pawn"/> standing still at the centre of
		/// <paramref name="c"/> (the drafted-move click remap reads it; no tween, so no drawn-centre hold).</summary>
		public static float RestingSinkAt(Pawn pawn, IntVec3 c)
		{
			RM_MapComponent_Excavation ex = ExcavationOf(pawn?.Map);
			if (ex == null || !c.InBounds(pawn.Map) || !RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled || pawn.Flying)
			{
				return 0f;
			}
			int d = Pits.RM_SuspensionUnderpass.DrawDepth(pawn, c, DrawHollow(pawn, ex, c));
			return d > 0 ? Clamped(ex, pawn.Map, c, d, RimMandrakeFlowWorksSettings.pitSinkPerLevel) : 0f;
		}

		/// <summary>Sink on cell <paramref name="c"/> of dug depth <paramref name="d"/>, held so the drawn centre
		/// stays north of the near lip in that column (<see cref="RM_PitDrawMath.ClampSinkToLip"/>).</summary>
		private static float Clamped(RM_MapComponent_Excavation ex, Map map, IntVec3 c, int d, float perLevel)
		{
			float sink = RM_PitDrawMath.SinkFor(d, perLevel);
			if (!(sink > 0f))
			{
				return 0f;
			}
			if (!RimMandrakeFlowWorksSettings.pitSinkClampEnabled)
			{
				return sink;
			}
			float lipZ = RM_PitDrawMath.LipZBelow(c.x, c.z, d, SeenDepth, RM_PitDrawMath.SinkCapLevels * 2);
			return RM_PitDrawMath.ClampSinkToLip(sink, c.z + 0.5f, lipZ);
		}

		/// <summary>The drawn-centre hold (RM_PitDrawMath.HoldToDrawnLip) under the same switch as the per-cell clamp: with the
		/// clamp off (validation_v2's X rows measure the sink by depth) the sink is left whole.</summary>
		private static float Held(float sink, Vector3 drawPos, int d)
		{
			return RimMandrakeFlowWorksSettings.pitSinkClampEnabled ? RM_PitDrawMath.HoldToDrawnLip(sink, drawPos.x, drawPos.z, d, SeenDepth) : sink;
		}

		/// <summary>The lip finder's depth lookup (RM_PitDrawMath.LipZBelow) on the map <see cref="ExcavationOf"/> last cached
		/// (SinkOf caches its pawn's map before any lip is looked for): -1 off the map, else the depth the square SHOWS (an
		/// intact lid is ground). One delegate, no allocation per pawn per frame.</summary>
		private static readonly Func<int, int, int> SeenDepth = (x, z) =>
		{
			IntVec3 q = new IntVec3(x, 0, z);
			return cachedComp != null && q.InBounds(cachedMap) ? Pits.RM_SuspensionUnderpass.SeenDepthAt(cachedMap, cachedComp, q) : -1;
		};

		private static RM_MapComponent_Excavation ExcavationOf(Map map)
		{
			if (map == null)
			{
				return null;
			}
			if (map != cachedMap)
			{
				cachedMap = map;
				cachedComp = map.GetComponent<RM_MapComponent_Excavation>();
			}
			return cachedComp;
		}
	}

	/// <summary>PIT_CLICK_FIX_SHIFTED_ONE_DOWN — a drafted "go here" click inside a pit means the square the pawn would be
	/// DRAWN at the click, not the square under the mouse (RM_PitDrawMath.PickRowForDrawnClick over
	/// RM_Patch_PitDepthDrawOffset.RestingSinkAt of the first selected pawn). The clicked cell is swapped for the option's
	/// build only and restored after (the option's delegate keeps vanilla's clicked cell for its exit-grid check).</summary>
	[HarmonyPatch(typeof(RimWorld.FloatMenuOptionProvider_DraftedMove), "GetSingleOption")]
	[RimMandrake.Shared.PatchFeature("Pawns sink into dug channels", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitDepthDrawOffsetEnabled")]
	public static class RM_Patch_PitClickDrawnRow
	{
		private static readonly AccessTools.FieldRef<RimWorld.FloatMenuContext, IntVec3> ClickedRef =
			AccessTools.FieldRefAccess<RimWorld.FloatMenuContext, IntVec3>("cachedClickedCell");

		[HarmonyPrefix]
		public static void Prefix(RimWorld.FloatMenuContext context, out IntVec3 __state)
		{
			__state = IntVec3.Invalid;
			if (context == null || context.map == null || !RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled)
			{
				return;
			}
			Pawn pawn = context.FirstSelectedPawn;
			IntVec3 c = ClickedRef(context);
			if (pawn == null || pawn.Map != context.map || !c.InBounds(context.map))
			{
				return;
			}
			Map map = context.map;
			int z = RM_PitDrawMath.PickRowForDrawnClick(c.z, context.clickPosition.z, row =>
			{
				IntVec3 q = new IntVec3(c.x, 0, row);
				return q.InBounds(map) ? RM_Patch_PitDepthDrawOffset.RestingSinkAt(pawn, q) : float.NaN;
			}, RM_PitDrawMath.SinkCapLevels / 2);
			if (z != c.z)
			{
				__state = c;
				ClickedRef(context) = new IntVec3(c.x, 0, z);
			}
		}

		[HarmonyFinalizer]
		public static void Finalizer(RimWorld.FloatMenuContext context, IntVec3 __state)
		{
			if (__state.IsValid && context != null)
			{
				ClickedRef(context) = __state;
			}
		}
	}

	/// <summary>RIMMANDRAKE_FIX_DRAFTED_MOVE_IN_BIG_PIT_WALKS_SOUTH (owner 2026-11-13: "when you click on a drafted pawn to go
	/// to a place in a large pit like this: it shows you where you can go correctly, but then they go to a different place
	/// usually more south than intended"). 1.6 sends a drafted right-click through MultiPawnGotoController, not the float
	/// menu RM_Patch_PitClickDrawnRow remaps: its ghost was drawn unsunk on the destination square, and the pawn, arriving
	/// there, was drawn its pit sink (up to 2.4 squares) further south. Now each destination in a pit is the square whose
	/// RESTING drawn centre is nearest the square pointed at (the same RM_PitDrawMath.PickRowForDrawnClick), kept only if
	/// the pawn can stand on and reach it and no other pawn has it, else the nearest such row back toward the pointed one;
	/// and the ghost and its circle are drawn sunk on that square (<see cref="RM_Patch_PitGotoGhostSunk"/>), so the pawn
	/// arrives on the previewed square, drawn where the preview stood.</summary>
	[HarmonyPatch(typeof(RimWorld.MultiPawnGotoController), nameof(RimWorld.MultiPawnGotoController.RecomputeDestinations))]
	[RimMandrake.Shared.PatchFeature("Pawns sink into dug channels (drafted move)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitDepthDrawOffsetEnabled")]
	public static class RM_Patch_PitGotoDrawnRow
	{
		internal static readonly AccessTools.FieldRef<RimWorld.MultiPawnGotoController, System.Collections.Generic.List<Pawn>> PawnsRef =
			AccessTools.FieldRefAccess<RimWorld.MultiPawnGotoController, System.Collections.Generic.List<Pawn>>("pawns");
		internal static readonly AccessTools.FieldRef<RimWorld.MultiPawnGotoController, System.Collections.Generic.List<IntVec3>> DestsRef =
			AccessTools.FieldRefAccess<RimWorld.MultiPawnGotoController, System.Collections.Generic.List<IntVec3>>("dests");

		[HarmonyPostfix]
		public static void Postfix(RimWorld.MultiPawnGotoController __instance)
		{
			if (!RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled)
			{
				return;
			}
			System.Collections.Generic.List<Pawn> pawns = PawnsRef(__instance);
			System.Collections.Generic.List<IntVec3> dests = DestsRef(__instance);
			for (int i = 0; i < pawns.Count && i < dests.Count; i++)
			{
				Pawn p = pawns[i];
				if (p != null && p.Spawned && dests[i].IsValid)
				{
					dests[i] = DrawnRowCell(p, dests[i], dests);
				}
			}
		}

		/// <summary>The square <paramref name="p"/> is sent to so it is DRAWN at the centre of <paramref name="c"/>.</summary>
		internal static IntVec3 DrawnRowCell(Pawn p, IntVec3 c, System.Collections.Generic.List<IntVec3> taken)
		{
			Map map = p.Map;
			int z = RM_PitDrawMath.PickRowForDrawnClick(c.z, c.z + 0.5f, row =>
			{
				IntVec3 q = new IntVec3(c.x, 0, row);
				return q.InBounds(map) ? RM_Patch_PitDepthDrawOffset.RestingSinkAt(p, q) : float.NaN;
			}, RM_PitDrawMath.SinkCapLevels / 2);
			for (IntVec3 n = new IntVec3(c.x, 0, z); n.z > c.z; n.z--)
			{
				if (n.Standable(map) && !taken.Contains(n) && p.CanReach(n, PathEndMode.OnCell, Danger.Deadly))
				{
					return n;
				}
			}
			return c;
		}
	}

	/// <summary>The drafted-move ghost and its circle, drawn sunk on a pit square as the pawn will be drawn standing there
	/// (RM_Patch_PitDepthDrawOffset.RestingSinkAt); vanilla's own draw when no destination is sunk.</summary>
	[HarmonyPatch(typeof(RimWorld.MultiPawnGotoController), nameof(RimWorld.MultiPawnGotoController.Draw))]
	[RimMandrake.Shared.PatchFeature("Pawns sink into dug channels (drafted move)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitDepthDrawOffsetEnabled")]
	public static class RM_Patch_PitGotoGhostSunk
	{
		private static readonly AccessTools.FieldRef<RimWorld.MultiPawnGotoController, IntVec3> StartRef =
			AccessTools.FieldRefAccess<RimWorld.MultiPawnGotoController, IntVec3>("start");
		private static readonly AccessTools.FieldRef<RimWorld.MultiPawnGotoController, IntVec3> EndRef =
			AccessTools.FieldRefAccess<RimWorld.MultiPawnGotoController, IntVec3>("end");
		// vanilla's own look (MultiPawnGotoController's private constants)
		private static readonly Color Feedback = GenColor.FromBytes(153, 207, 135);
		private static Material circle, line;

		[HarmonyPrefix]
		public static bool Prefix(RimWorld.MultiPawnGotoController __instance)
		{
			if (!RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled || !__instance.Active)
			{
				return true;
			}
			System.Collections.Generic.List<Pawn> pawns = RM_Patch_PitGotoDrawnRow.PawnsRef(__instance);
			System.Collections.Generic.List<IntVec3> dests = RM_Patch_PitGotoDrawnRow.DestsRef(__instance);
			bool sunk = false;
			for (int i = 0; i < pawns.Count && i < dests.Count && !sunk; i++)
			{
				sunk = pawns[i] != null && pawns[i].Spawned && dests[i].IsValid && RM_Patch_PitDepthDrawOffset.RestingSinkAt(pawns[i], dests[i]) > 0f;
			}
			if (!sunk)
			{
				return true;
			}
			circle = circle ?? MaterialPool.MatFrom("UI/Overlays/Circle75Solid", ShaderDatabase.Transparent, Feedback * new Color(1f, 1f, 1f, 0.4f));
			line = line ?? MaterialPool.MatFrom("UI/Overlays/ThickLine", ShaderDatabase.Transparent, Feedback * new Color(1f, 1f, 1f, 0.18f));
			Vector3 s = new Vector3(1.7f, 1f, 1.7f);
			float alt = AltitudeLayer.MetaOverlays.AltitudeFor();
			for (int i = 0; i < pawns.Count && i < dests.Count; i++)
			{
				Pawn pawn = pawns[i];
				IntVec3 c = dests[i];
				if (c.IsValid && pawn.Spawned && !c.Fogged(pawn.Map))
				{
					float sink = RM_Patch_PitDepthDrawOffset.RestingSinkAt(pawn, c);
					Vector3 at = c.ToVector3ShiftedWithAltitude(alt);
					at.z -= sink;
					pawn.Drawer.renderer.RenderPawnAt(at, Rot4.South);
					Vector3 pos = c.ToVector3ShiftedWithAltitude(alt + 0.03658537f);
					pos.z -= sink;
					Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(pos, Quaternion.identity, s), circle, 0);
				}
			}
			GenDraw.DrawLineBetween(StartRef(__instance).ToVector3ShiftedWithAltitude(alt - 0.03658537f),
				EndRef(__instance).ToVector3ShiftedWithAltitude(alt - 0.03658537f), line, 0.9f);
			return false;
		}
	}

	/// <summary>
	/// FLOWWORKS_VISUAL_PRINCIPLES_1 — owner, 2026-10-05, looking at a sunk colonist in game: <i>"Is there a way to
	/// stop the shadow of a person showing through like this?"</i>
	///
	/// 1.6 draws a standing pawn's ground shadow in PawnRenderer.DrawShadowInternal (decompiled, read via RimSage):
	/// the race's specialShadowData blob, else the body graphic's ShadowGraphic, at the pawn's (sunk) draw position —
	/// so it lands below the near bank and shows through. Vanilla itself skips it for a swimming pawn. This skips it
	/// the same way for anything sunk in a dug cell (humans, animals, mechs; filled or dry cut). Flying pawns keep
	/// vanilla's flight shadow (that branch is not ours: a flier is above the pit). Setting off, or no sink: vanilla.
	/// </summary>
	[HarmonyPatch(typeof(PawnRenderer), "DrawShadowInternal")]
	[RimMandrake.Shared.PatchFeature("No ground shadow in a cut", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitHidesShadowEnabled")]
	public static class RM_Patch_PitHidesShadow
	{
		private static readonly AccessTools.FieldRef<PawnRenderer, Pawn> PawnOf =
			AccessTools.FieldRefAccess<PawnRenderer, Pawn>("pawn");

		[HarmonyPrefix]
		public static bool Prefix(PawnRenderer __instance, Vector3 drawLoc)
		{
			if (!RimMandrakeFlowWorksSettings.pitHidesShadowEnabled || !RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled)
			{
				return true;
			}
			Pawn pawn = PawnOf(__instance);
			if (pawn == null || !pawn.Spawned || pawn.Flying)
			{
				return true;
			}
			return !(RM_Patch_PitDepthDrawOffset.SinkOf(pawn, drawLoc) > 0f);
		}
	}

	/// <summary>No height advantage from the sink (LAW 2): while any verb fires a shot (Verb.TryCastNextBurstShot, which runs every verb's
	/// TryCastShot), DrawPos is read unsunk, so a projectile's origin, a beam's or spray's aim and the interceptor
	/// tests that start from that origin are exactly what they would be with no pit. Drawing is untouched: frames are
	/// never rendered inside a shot. A counter, not a bool, so a shot that triggers another verb nests safely.</summary>
	[HarmonyPatch(typeof(Verb), "TryCastNextBurstShot")]
	[RimMandrake.Shared.PatchFeature("Sunk pawns still shoot from their cell")]
	public static class RM_Patch_PitDepthDrawCombatOrigin
	{
		public static int Firing;

		[HarmonyPrefix]
		public static void Prefix()
		{
			Firing++;
		}

		[HarmonyFinalizer]
		public static void Finalizer()
		{
			if (Firing > 0)
			{
				Firing--;
			}
		}
	}
}
