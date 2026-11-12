using System.Collections.Generic;
using System.Globalization;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL: the liquid standing in a pit covers the fittings in it up to its level
	/// (rules: RM_SubmergeMath). Ladders (RM_Ladder, RM_LadderSteel, RM_LadderPortable: lowered, raised and lying-flat art)
	/// and the ramp (RM_PitRamp) are map-mesh things: their Print draws the uncovered part of the vanilla sprite (Graphic.Print
	/// mirrored, decompiled 1.6, with the atlas uvs lerped so a static atlas tile cuts the same). The spikes (RM_Spikes,
	/// realtime) cut each stake in Building_RM_Spikes.DrawAt. Setting pitSubmergeCutEnabled (on): off draws as before.
	///
	/// Cost: nothing while dry. A map-mesh fitting notes the key it was printed at (RM_MapComponent_Excavation.submergeDrawn,
	/// cell index -> RM_SubmergeMath.DrawnKey: a hung ladder's face fill, the same whole-notch FillAt its wall face is drawn
	/// with; the ramp's quarter notches of the TRUE level); the excavation engine's picture-writer (ApplyFillTerrain, which
	/// every write of a dug square's liquid calls) re-meshes a noted cell whose key moved and drops its note, and the
	/// re-print notes it again. Stale notes
	/// (a fitting gone) cost one extra re-mesh on that square's next change. Prints run only on a section rebuild: the cut uses
	/// static buffers, no allocation.
	/// </summary>
	public static class RM_SubmergeDraw
	{
		private static readonly float[] Uv = new float[8];
		private static readonly Vector2[] UvBuf = new Vector2[4];
		private static readonly Color32[] ColBuf = new Color32[4];

		public static bool On => RimMandrakeFlowWorksSettings.pitSubmergeCutEnabled;

		/// <summary>ThingWithComps.Print's CompsPreventDrawing (private): a comp hiding the parent leaves it to vanilla.</summary>
		public static bool CompsHide(ThingWithComps t)
		{
			List<ThingComp> comps = t.AllComps;
			for (int i = 0; i < comps.Count; i++)
			{
				if (comps[i].DontDrawParent())
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>The rest of ThingWithComps.Print once the body is drawn (or hidden) here: every comp prints its own part.</summary>
		public static void PrintComps(ThingWithComps t, SectionLayer layer)
		{
			List<ThingComp> comps = t.AllComps;
			for (int i = 0; i < comps.Count; i++)
			{
				comps[i].PostPrintOnto(layer);
			}
		}

		/// <summary>The quarter-notch note of the true level (whole notch + part-notch) standing on <paramref name="c"/>.</summary>
		public static int NoteAt(RM_MapComponent_Excavation eng, IntVec3 c)
		{
			return RM_SubmergeMath.LevelNote(eng.WaterDlAt(c) / (double)RM_LevelSolve.U);
		}

		/// <summary>The redraw key a fitting on <paramref name="c"/> would print at now (RM_SubmergeMath.DrawnKey): a hung
		/// ladder's face fill, else the true level's quarter-notch note.</summary>
		public static int KeyAt(RM_MapComponent_Excavation eng, IntVec3 c, bool face)
		{
			return RM_SubmergeMath.DrawnKey(face, eng.FillAt(c), eng.WaterDlAt(c) / (double)RM_LevelSolve.U);
		}

		/// <summary>Called by RM_MapComponent_Excavation.ApplyFillTerrain for a dug square while any fitting is noted.</summary>
		public static void FillPictured(RM_MapComponent_Excavation eng, Map map, IntVec3 c, int index)
		{
			if (eng.submergeDrawn.TryGetValue(index, out int drawn) && drawn != KeyAt(eng, c, (drawn & RM_SubmergeMath.FaceKind) != 0))
			{
				eng.submergeDrawn.Remove(index);
				map.mapDrawer.MapMeshDirty(c, (ulong)MapMeshFlagDefOf.Buildings | (ulong)MapMeshFlagDefOf.Things);
			}
		}

		/// <summary>The dug depth and the drawn level (notches) under a fitting: for a hung ladder (<paramref name="face"/>) the
		/// whole-notch fill its wall face is drawn with, else the true level in quarter notches; false when it stands on no dug
		/// square, the setting is off or it is dry. Notes the key printed at (a dry print too: the first liquid must re-mesh it).</summary>
		private static bool Wet(Thing t, bool face, out RM_MapComponent_Excavation eng, out int d, out float f)
		{
			eng = null;
			d = 0;
			f = 0f;
			if (!On || !t.Spawned)
			{
				return false;
			}
			eng = t.Map.GetComponent<RM_MapComponent_Excavation>();
			if (eng == null)
			{
				return false;
			}
			IntVec3 c = t.Position;
			d = eng.HollowDepthAt(c);
			if (d <= 0)
			{
				return false;
			}
			int key = KeyAt(eng, c, face);
			eng.submergeDrawn[t.Map.cellIndices.CellToIndex(c)] = key;
			f = RM_SubmergeMath.KeyLevel(key);
			return f > 0f;
		}

		/// <summary>The levels a ladder's wall drops (its own depth when it hangs on none).</summary>
		private static int LadderDrop(Thing t, RM_MapComponent_Excavation eng, int d)
		{
			int drop = d - SectionLayer_RMExcavationWalls.NeighbourLevel(t.Map, eng, t.Position + t.Rotation.FacingCell, d);
			return drop > 0 ? drop : d;
		}

		private static bool LiesFlat(Thing t, Graphic g)
		{
			RM_CompLadder comp = t.TryGetComp<RM_CompLadder>();
			return comp != null && g == comp.ShortGraphic;
		}

		/// <summary>RM_Building_Ladder.Print: true when this drew (or hid) the ladder; false = vanilla prints it whole.</summary>
		public static bool PrintLadder(Thing t, SectionLayer layer)
		{
			if (!Wet(t, true, out RM_MapComponent_Excavation eng, out int d, out float f))
			{
				return false;
			}
			Graphic g = t.Graphic;
			if (LiesFlat(t, g))
			{
				return true;   // lying on the floor: under the liquid from its first level
			}
			int rot = t.Rotation.AsInt;
			float cut = LadderCut(t, eng, d);
			if (cut < 0f)
			{
				return false;
			}
			return PrintCut(t, layer, g, RM_SubmergeMath.LadderFrom(rot), cut, -1f);
		}

		/// <summary>A hung ladder's cell-local waterline: its wall face's own (RM_SubmergeMath.HungLadderLevel of FillAt).
		/// PrintLadder and ProofSubmerge both read this.</summary>
		public static float LadderCut(Thing t, RM_MapComponent_Excavation eng, int d)
		{
			return RM_SubmergeMath.LadderWaterline(t.Rotation.AsInt, LadderDrop(t, eng, d),
				RM_SubmergeMath.HungLadderLevel(eng.FillAt(t.Position)));
		}

		/// <summary>The waterline the wall layer draws on the face a ladder hangs on, computed the way
		/// SectionLayer_RMExcavationWalls does (ExposedDrop with FillAt; N: 1 - NorthFaceHeight, E: 1 - SideFaceWidth,
		/// W: SideFaceWidth): the proof's independent reference for <see cref="LadderCut"/>. -1 when no face shows liquid.</summary>
		public static float FaceWaterline(Thing t, RM_MapComponent_Excavation eng, int d)
		{
			int rot = t.Rotation.AsInt, f = eng.FillAt(t.Position);
			if (rot == 2 || f <= 0)
			{
				return RM_SubmergeMath.NoCut;
			}
			int nb = SectionLayer_RMExcavationWalls.NeighbourLevel(t.Map, eng, t.Position + t.Rotation.FacingCell, d);
			if (RM_WallFaceMath.ExposedDrop(d, nb, 0) <= 0)
			{
				return RM_SubmergeMath.NoCut;   // hangs on no wall: no face to meet
			}
			int exposed = RM_WallFaceMath.ExposedDrop(d, nb, f);
			if (rot == 0)
			{
				return 1f - RM_WallFaceMath.NorthFaceHeight(exposed);
			}
			float w = RM_WallFaceMath.SideFaceWidth(exposed);
			return rot == 1 ? 1f - w : w;
		}

		/// <summary>RM_Building_PitRamp.Print: covered from the downhill end by level / rise.</summary>
		public static bool PrintRamp(Thing t, SectionLayer layer)
		{
			if (!Wet(t, false, out RM_MapComponent_Excavation eng, out int d, out float f))
			{
				return false;
			}
			return PrintCut(t, layer, t.Graphic, RampFrom(t.Rotation.AsInt), -1f, RM_SubmergeMath.RampShare(f, RampRise(t, eng, d)));
		}

		/// <summary>The ramp points uphill: its downhill end is the opposite side.</summary>
		private static int RampFrom(int rot) => rot == 0 ? RM_SubmergeMath.FromSouth : rot == 1 ? RM_SubmergeMath.FromWest
			: rot == 2 ? RM_SubmergeMath.FromNorth : RM_SubmergeMath.FromEast;

		private static int RampRise(Thing t, RM_MapComponent_Excavation eng, int d)
		{
			IntVec3 up = t.Position + t.Rotation.FacingCell;
			return up.InBounds(t.Map) ? d - eng.HollowDepthAt(up) : d;
		}

		/// <summary>Graphic.Print (1.6) with the sprite's covered part cut away: by a cell-local waterline
		/// <paramref name="cut"/> (z for a South/North start, x for West/East), or by a direct <paramref name="share"/> of the
		/// sprite when cut is negative. False when there is nothing to cut (vanilla prints it whole).</summary>
		private static bool PrintCut(Thing t, SectionLayer layer, Graphic g, int from, float cut, float share)
		{
			if (g == null || g.ShouldDrawRotated)
			{
				return false;
			}
			Rot4 rot = t.Rotation;
			bool flip = (rot == Rot4.West && g.WestFlipped) || (rot == Rot4.East && g.EastFlipped);
			if (flip && g.data != null && g.data.flipExtraRotation != 0f)
			{
				return false;
			}
			Vector2 size = rot.IsHorizontal ? g.drawSize.Rotated() : g.drawSize;
			Vector3 center = t.TrueCenter() + g.DrawOffset(rot);
			float x0 = center.x - size.x * 0.5f, x1 = center.x + size.x * 0.5f;
			float z0 = center.z - size.y * 0.5f, z1 = center.z + size.y * 0.5f;
			if (cut >= 0f)
			{
				bool alongZ = from == RM_SubmergeMath.FromSouth || from == RM_SubmergeMath.FromNorth;
				bool fromLow = from == RM_SubmergeMath.FromSouth || from == RM_SubmergeMath.FromWest;
				IntVec3 c = t.Position;
				share = alongZ ? RM_SubmergeMath.SpanShare(z0 - c.z, z1 - c.z, cut, fromLow)
					: RM_SubmergeMath.SpanShare(x0 - c.x, x1 - c.x, cut, fromLow);
			}
			if (share <= 0f)
			{
				return false;
			}
			if (share >= 1f)
			{
				return true;   // wholly under: nothing shows
			}
			Material mat = g.MatAt(rot, t);
			Graphic.TryGetTextureAtlasReplacementInfo(mat, t.def.category.ToAtlasGroup(), flip, true, out mat, out Vector2[] uvs, out Color32 vc);
			if (uvs != null)
			{
				for (int j = 0; j < 4; j++)
				{
					Uv[j * 2] = uvs[j].x;
					Uv[j * 2 + 1] = uvs[j].y;
				}
			}
			else
			{
				// Printer_Plane.DefaultUvs / DefaultUvsFlipped, corner order (-x-z, -x+z, +x+z, +x-z)
				float ul = flip ? 1f : 0f, ur = flip ? 0f : 1f;
				Uv[0] = ul; Uv[1] = 0f; Uv[2] = ul; Uv[3] = 1f; Uv[4] = ur; Uv[5] = 1f; Uv[6] = ur; Uv[7] = 0f;
			}
			RM_SubmergeMath.Cut(from, share, Uv, ref x0, ref z0, ref x1, ref z1);
			for (int j = 0; j < 4; j++)
			{
				UvBuf[j] = new Vector2(Uv[j * 2], Uv[j * 2 + 1]);
				ColBuf[j] = vc;
			}
			Printer_Plane.PrintPlane(layer, new Vector3((x0 + x1) * 0.5f, center.y, (z0 + z1) * 0.5f), new Vector2(x1 - x0, z1 - z0),
				mat, 0f, flip, UvBuf, ColBuf);
			g.ShadowGraphic?.Print(layer, t, 0f);
			return true;
		}

		/// <summary>Scene helper for pit_fittings_matrix.py: "x,z,w,h,fill[,FluidDefName]" writes that whole-notch fill on every
		/// dug square of the rect through the engine's own driver write (TrySetDriverFillOutcome; default fluid = the map's).
		/// -> "FILL applied=N refused=N notOwned=N fluid=..." or "REFUSED: ...".</summary>
		public static string ProofFillRect(string arg)
		{
			Map map = Find.CurrentMap;
			string[] p = (arg ?? "").Split(',');
			RM_MapComponent_Excavation eng = map?.GetComponent<RM_MapComponent_Excavation>();
			if (eng == null || p.Length < 5 || !int.TryParse(p[0].Trim(), out int x) || !int.TryParse(p[1].Trim(), out int z)
				|| !int.TryParse(p[2].Trim(), out int w) || !int.TryParse(p[3].Trim(), out int h) || !int.TryParse(p[4].Trim(), out int fill)
				|| w < 1 || h < 1 || w * h > 400)
			{
				return "REFUSED: need a current map with FlowWorks and \"x,z,w,h,fill[,FluidDefName]\" (w*h <= 400)";
			}
			FluidDef fluid = null;
			if (p.Length > 5 && p[5].Trim().Length > 0)
			{
				fluid = DefDatabase<FluidDef>.GetNamedSilentFail(p[5].Trim());
				if (fluid == null)
				{
					return "REFUSED: no FluidDef " + p[5].Trim();
				}
			}
			int applied = 0, refused = 0, notOwned = 0;
			foreach (IntVec3 c in new CellRect(x, z, w, h))
			{
				switch (eng.TrySetDriverFillOutcome(c, fill, fluid))
				{
					case RM_MapComponent_Excavation.DriverFillOutcome.Applied: applied++; break;
					case RM_MapComponent_Excavation.DriverFillOutcome.Refused: refused++; break;
					default: notOwned++; break;
				}
			}
			return "FILL applied=" + applied + " refused=" + refused + " notOwned=" + notOwned + " fluid=" + (fluid?.defName ?? "default");
		}

		private static string Z(float z) => z < 0f ? "-" : z.ToString("F3", CultureInfo.InvariantCulture);

		/// <summary>
		/// Proof read for wall_art_scene.py's "submerge" and pit_fittings_matrix.py's rows: the fitting at "x,z" and the covered
		/// share the drawers use.
		/// "def=RM_Ladder class=RM_Building_Ladder rot=0 depth=4 fill=3 level=4.00 flat=no cutZ=0.880 faceZ=0.880 share=0.760
		/// printedLevel=3.00 setting=on" (fill = whole notches, what the wall faces are drawn with; level = the true level,
		/// quarter notches; a hung ladder is cut at its face's fill, the ramp and spikes at the level; cutZ = the cell-local
		/// waterline the ladder is cut at, faceZ = the waterline the wall layer draws on its face, "-" for none: they must
		/// agree; ladder share = of its in-pit span, wall foot to rim; spikes = of each stake; ramp = of the ramp from its
		/// downhill end; printedLevel = the level the map mesh last printed it at, "-" for the realtime spikes or when not
		/// printed since the last change).
		/// Else "REFUSED: ...".
		/// </summary>
		public static string ProofSubmerge(string arg)
		{
			Map map = Find.CurrentMap;
			string[] p = (arg ?? "").Split(',');
			if (map == null || p.Length < 2 || !int.TryParse(p[0].Trim(), out int x) || !int.TryParse(p[1].Trim(), out int z))
			{
				return "REFUSED: need a current map and \"x,z\"";
			}
			IntVec3 c = new IntVec3(x, 0, z);
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			if (!c.InBounds(map) || eng == null)
			{
				return "REFUSED: cell off the map or no excavation engine";
			}
			int d = eng.HollowDepthAt(c), f = eng.FillAt(c);
			float lv = RM_SubmergeMath.NoteLevel(NoteAt(eng, c));
			List<Thing> list = c.GetThingList(map);
			for (int i = 0; i < list.Count; i++)
			{
				Thing t = list[i];
				float share;
				string kind = t.GetType().Name, faces = "";
				if (t is RM_Building_Ladder)
				{
					float lf = RM_SubmergeMath.HungLadderLevel(f);
					bool flat = LiesFlat(t, t.Graphic);
					share = d <= 0 || lf <= 0f ? 0f : flat ? 1f
						: RM_SubmergeMath.LadderInPitShare(t.Rotation.AsInt, LadderDrop(t, eng, d), lf);
					faces = " flat=" + (flat ? "yes" : "no") + " cutZ=" + Z(d <= 0 || flat ? RM_SubmergeMath.NoCut : LadderCut(t, eng, d))
						+ " faceZ=" + Z(d <= 0 ? RM_SubmergeMath.NoCut : FaceWaterline(t, eng, d));
				}
				else if (t is RM_Building_PitRamp)
				{
					share = d <= 0 ? 0f : RM_SubmergeMath.RampShare(lv, RampRise(t, eng, d));
				}
				else if (t is Building_RM_Spikes)
				{
					share = d <= 0 ? 0f : RM_SubmergeMath.StakeShare(lv);
				}
				else
				{
					continue;
				}
				string printed = t is Building_RM_Spikes || !eng.submergeDrawn.TryGetValue(map.cellIndices.CellToIndex(c), out int pf)
					? "-" : RM_SubmergeMath.KeyLevel(pf).ToString("F2", CultureInfo.InvariantCulture);
				return "def=" + t.def.defName + " class=" + kind + " rot=" + t.Rotation.AsInt + " depth=" + d + " fill=" + f
					+ " level=" + lv.ToString("F2", CultureInfo.InvariantCulture) + faces + " share=" + share.ToString("F3", CultureInfo.InvariantCulture) + " printedLevel=" + printed + " setting=" + (On ? "on" : "off");
			}
			return "REFUSED: no ladder, ramp or spikes at " + x + "," + z + " (depth=" + d + " fill=" + f + ")";
		}
	}

	public partial class RM_Building_Ladder
	{
		public override void Print(SectionLayer layer)
		{
			// Thing.Print / ThingWithComps.Print with the body cut by the liquid; anything else is vanilla's
			if (def.dontPrint || RM_SubmergeDraw.CompsHide(this) || !RM_SubmergeDraw.PrintLadder(this, layer))
			{
				base.Print(layer);
				return;
			}
			RM_SubmergeDraw.PrintComps(this, layer);
		}
	}

	public partial class RM_Building_PitRamp
	{
		public override void Print(SectionLayer layer)
		{
			// Thing.Print / ThingWithComps.Print with the body cut by the liquid; anything else is vanilla's
			if (def.dontPrint || RM_SubmergeDraw.CompsHide(this) || !RM_SubmergeDraw.PrintRamp(this, layer))
			{
				base.Print(layer);
				return;
			}
			RM_SubmergeDraw.PrintComps(this, layer);
		}
	}
}
