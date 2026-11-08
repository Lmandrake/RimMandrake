using System;
using System.Globalization;
using HarmonyLib;
using UnityEngine;
using Verse;

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
			float sink = SinkOf(pawn, __result);
			if (sink > 0f)
			{
				__result.z -= sink;
				// PIT_SINK_FIX_LIP_PAWN_UNHIDES_OCCUPANT: below the near-lip cover, which is below everyone on the ground
				__result.y -= RM_WallFaceMath.SunkAltitudeDrop;
			}
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
		/// stays north of the near lip in that column (<see cref="RM_PitDrawMath.ClampSinkToLip"/>).
		/// PIT_DEPTH_ONE_DRAWING: with the clamp on, the sink is first eased into the column's opening by the far face's own
		/// cap (RM_PitDrawMath.OccupantSink), so on the north row the occupant's floor line is the face's foot; the lip is
		/// riser-aware (a shallower hole south of him has its own floor drawn lower) and the drawn centre is held
		/// pitSinkHoldAbove over it.</summary>
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
			// = RM_PitDrawMath.OccupantSink(d, perLevel, run, ObliqueMinFloor) without computing SinkFor twice
			sink = RM_PitDrawMath.SoftCap(sink, RM_PitDrawMath.OpeningRoom(OpeningRun(ex, map, c), RM_PitLookMath.ObliqueMinFloor));
			float lipZ = RM_PitDrawMath.LipZBelow(c.x, c.z, d, SeenDepth, RM_PitDrawMath.SinkCapLevels * 2, perLevel);
			return RM_PitDrawMath.ClampSinkToLip(sink, c.z + 0.5f, lipZ, RimMandrakeFlowWorksSettings.pitSinkHoldAbove);
		}

		private const int RunSlots = 64;

		// a small direct-mapped memo of each square's opening run, per thread (pawns are drawn in parallel, ParallelPreDraw):
		// allocated once a thread, never per frame; an entry is good for one map, one excavation generation and one tick
		[ThreadStatic] private static int[] runKeys;
		[ThreadStatic] private static int[] runGens;
		[ThreadStatic] private static int[] runTicks;
		[ThreadStatic] private static float[] runVals;
		[ThreadStatic] private static int runMapId;

		/// <summary>The opening over <paramref name="c"/>'s column (SectionLayer_RMExcavationWalls.OpeningRunAt), memoised:
		/// DrawPos is read several times a frame per pawn.</summary>
		private static float OpeningRun(RM_MapComponent_Excavation ex, Map map, IntVec3 c)
		{
			int[] keys = runKeys;
			if (keys == null)
			{
				keys = runKeys = new int[RunSlots];
				runGens = new int[RunSlots];
				runTicks = new int[RunSlots];
				runVals = new float[RunSlots];
				runMapId = map.uniqueID;
			}
			else if (runMapId != map.uniqueID)
			{
				Array.Clear(keys, 0, RunSlots);
				runMapId = map.uniqueID;
			}
			int idx = map.cellIndices.CellToIndex(c);
			int slot = idx & (RunSlots - 1);
			int gen = ex.ClimbGeneration;
			int tick = Find.TickManager != null ? Find.TickManager.TicksGame : 0;
			if (keys[slot] == idx + 1 && runGens[slot] == gen && runTicks[slot] == tick)
			{
				return runVals[slot];
			}
			float run = SectionLayer_RMExcavationWalls.OpeningRunAt(map, ex, c);
			keys[slot] = idx + 1;
			runGens[slot] = gen;
			runTicks[slot] = tick;
			runVals[slot] = run;
			return run;
		}

		/// <summary>The drawn-centre hold (RM_PitDrawMath.HoldToDrawnLip) under the same switch as the per-cell clamp: with the
		/// clamp off (validation_v2's X rows measure the sink by depth) the sink is left whole.</summary>
		private static float Held(float sink, Vector3 drawPos, int d)
		{
			return RimMandrakeFlowWorksSettings.pitSinkClampEnabled
				? RM_PitDrawMath.HoldToDrawnLip(sink, drawPos.x, drawPos.z, d, SeenDepth, RimMandrakeFlowWorksSettings.pitSinkPerLevel,
					RimMandrakeFlowWorksSettings.pitSinkHoldAbove)
				: sink;
		}

		/// <summary>The lip finder's depth lookup (RM_PitDrawMath.LipZBelow) on the map <see cref="ExcavationOf"/> last cached
		/// (SinkOf caches its pawn's map before any lip is looked for): -1 off the map, else the depth the square SHOWS (an
		/// intact lid is ground). One delegate, no allocation per pawn per frame.</summary>
		private static readonly Func<int, int, int> SeenDepth = (x, z) =>
		{
			IntVec3 q = new IntVec3(x, 0, z);
			return cachedComp != null && q.InBounds(cachedMap) ? Pits.RM_SuspensionUnderpass.SeenDepthAt(cachedMap, cachedComp, q) : -1;
		};

		/// <summary>PIT_DEPTH_ONE_DRAWING: one pawn's depth drawing as text (RM_PitDepthDraw.DepthDrawState). The drawn z is
		/// read from the real getter, the sink as the unsunk getter (sink switched off as when a verb fires) less it.</summary>
		internal static string StateOf(Pawn pawn)
		{
			float k = RimMandrakeFlowWorksSettings.pitSinkPerLevel;
			float hold = RimMandrakeFlowWorksSettings.pitSinkHoldAbove;
			RM_MapComponent_Excavation ex = pawn != null && pawn.Spawned ? ExcavationOf(pawn.Map) : null;
			if (ex == null)
			{
				return RM_PitDepthDraw.FormatState(float.NaN, float.NaN, float.NaN, float.NaN, float.NaN, float.NaN, float.NaN, hold, k);
			}
			IntVec3 c = pawn.Position;
			int d = Pits.RM_SuspensionUnderpass.DrawDepth(pawn, c, DrawHollow(pawn, ex, c));
			Vector3 drawn = pawn.DrawPos;
			Vector3 unsunk;
			RM_Patch_PitDepthDrawCombatOrigin.Firing++;
			try
			{
				unsunk = pawn.DrawPos;
			}
			finally
			{
				RM_Patch_PitDepthDrawCombatOrigin.Firing--;
			}
			ExcavationOf(pawn.Map);   // the lip lookup reads the cached map
			float lipZ = d > 0
				? RM_PitDrawMath.LipZBelow(Mathf.FloorToInt(unsunk.x), Mathf.FloorToInt(unsunk.z), d, SeenDepth, RM_PitDrawMath.SinkCapLevels * 2, k)
				: float.NaN;
			float face = d > 0 ? SectionLayer_RMExcavationWalls.ObliqueFaceAt(pawn.Map, ex, c, out _, out _) : float.NaN;
			return RM_PitDepthDraw.FormatState(c.x, c.z, d, unsunk.z - drawn.z, drawn.z, lipZ, face, hold, k);
		}

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

	/// <summary>PIT_DEPTH_ONE_DRAWING: the depth drawing's handles for the bridge (jawa/static_call, type
	/// RimMandrake.FlowWorks.RM_PitDepthDraw): read one pawn's sink, lip and face, and set the sink scale and the hold.
	/// Not a patch.</summary>
	public static class RM_PitDepthDraw
	{
		/// <summary>"cell=x,z depth=D sink=S drawnZ=Z lipZ=L face=F hold=H k=K" for the spawned pawn with thingIDNumber
		/// <paramref name="thingIdNumber"/> (the current map first, then any map): depth in notches as the sink reads it, sink
		/// and drawn z as drawn this frame, the riser-aware near lip in the drawn column, the oblique far face over his square
		/// (cells). NaN where a value is not found (no such pawn, no lip, not in a hole).</summary>
		public static string DepthDrawState(int thingIdNumber)
		{
			return RM_Patch_PitDepthDrawOffset.StateOf(FindPawn(thingIdNumber));
		}

		/// <summary>Set the sink scale k (setting pitSinkPerLevel; the 2 m sink is 4k) and redraw the pit faces, which hang
		/// on the same curve. Not saved to the settings file (DepthDrawState reads it back).</summary>
		public static void SetSinkPerLevel(float k)
		{
			RimMandrakeFlowWorksSettings.pitSinkPerLevel = k < 0f ? 0f : k;
			SectionLayer_RMExcavationWalls.RedrawAll();
		}

		/// <summary>Set how far (cells) the drawn centre is held above the near lip (setting pitSinkHoldAbove). Not saved to
		/// the settings file (DepthDrawState reads it back).</summary>
		public static void SetSinkHoldAbove(float cells)
		{
			RimMandrakeFlowWorksSettings.pitSinkHoldAbove = cells < 0f ? 0f : cells;
		}

		internal static string FormatState(float x, float z, float depth, float sink, float drawnZ, float lipZ, float face, float hold, float k)
		{
			CultureInfo inv = CultureInfo.InvariantCulture;
			string cell = float.IsNaN(x) ? "NaN" : ((int)x).ToString(inv) + "," + ((int)z).ToString(inv);
			return "cell=" + cell
				+ " depth=" + (float.IsNaN(depth) ? "NaN" : ((int)depth).ToString(inv))
				+ " sink=" + sink.ToString("0.0###", inv)
				+ " drawnZ=" + drawnZ.ToString("0.0###", inv)
				+ " lipZ=" + lipZ.ToString("0.0###", inv)
				+ " face=" + face.ToString("0.0###", inv)
				+ " hold=" + hold.ToString("0.0###", inv)
				+ " k=" + k.ToString("0.0###", inv);
		}

		private static Pawn FindPawn(int id)
		{
			Pawn hit = PawnOn(Verse.Find.CurrentMap, id);
			if (hit != null || Verse.Find.Maps == null)
			{
				return hit;
			}
			foreach (Map m in Verse.Find.Maps)
			{
				hit = PawnOn(m, id);
				if (hit != null)
				{
					return hit;
				}
			}
			return null;
		}

		private static Pawn PawnOn(Map map, int id)
		{
			if (map?.mapPawns == null)
			{
				return null;
			}
			foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
			{
				if (p.thingIDNumber == id)
				{
					return p;
				}
			}
			return null;
		}
	}
}
