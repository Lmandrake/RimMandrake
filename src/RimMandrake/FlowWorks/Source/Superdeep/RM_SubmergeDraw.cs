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
	/// Cost: nothing while dry. A map-mesh fitting notes the level it was printed at (RM_MapComponent_Excavation.submergeDrawn,
	/// cell index -> RM_SubmergeMath.LevelNote, quarter notches of the TRUE level: whole notch + part-notch); the excavation
	/// engine's picture-writer (ApplyFillTerrain, which every write of a dug square's liquid calls) re-meshes a noted cell
	/// whose note moved and drops its note, and the re-print notes it again. Stale notes
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

		/// <summary>Called by RM_MapComponent_Excavation.ApplyFillTerrain for a dug square while any fitting is noted.</summary>
		public static void FillPictured(RM_MapComponent_Excavation eng, Map map, IntVec3 c, int index)
		{
			if (eng.submergeDrawn.TryGetValue(index, out byte drawn) && drawn != NoteAt(eng, c))
			{
				eng.submergeDrawn.Remove(index);
				map.mapDrawer.MapMeshDirty(c, (ulong)MapMeshFlagDefOf.Buildings | (ulong)MapMeshFlagDefOf.Things);
			}
		}

		/// <summary>The dug depth and the drawn level (notches, quarter steps) under a fitting; false when it stands on no dug
		/// square, the setting is off or it is dry. Notes the level printed at (a dry print too: the first liquid must re-mesh it).</summary>
		private static bool Wet(Thing t, out RM_MapComponent_Excavation eng, out int d, out float f)
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
			int note = NoteAt(eng, c);
			eng.submergeDrawn[t.Map.cellIndices.CellToIndex(c)] = (byte)note;
			f = RM_SubmergeMath.NoteLevel(note);
			return note > 0;
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
			if (!Wet(t, out RM_MapComponent_Excavation eng, out int d, out float f))
			{
				return false;
			}
			Graphic g = t.Graphic;
			if (LiesFlat(t, g))
			{
				return true;   // lying on the floor: under the liquid from its first level
			}
			int rot = t.Rotation.AsInt;
			float cut = RM_SubmergeMath.LadderWaterline(rot, LadderDrop(t, eng, d), f);
			if (cut < 0f)
			{
				return false;
			}
			return PrintCut(t, layer, g, RM_SubmergeMath.LadderFrom(rot), cut, -1f);
		}

		/// <summary>RM_Building_PitRamp.Print: covered from the downhill end by level / rise.</summary>
		public static bool PrintRamp(Thing t, SectionLayer layer)
		{
			if (!Wet(t, out RM_MapComponent_Excavation eng, out int d, out float f))
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

		/// <summary>
		/// Proof read for wall_art_scene.py's "submerge" rows: the fitting at "x,z" and the covered share the drawers use.
		/// "def=RM_Ladder rot=0 depth=4 fill=2 level=2.00 share=0.540 printedLevel=2.00 setting=on" (fill = whole notches;
		/// level = the true level drawn, quarter notches; ladder share = of its in-pit span, wall foot to rim; spikes = of each
		/// stake; ramp = of the ramp from its downhill end; printedLevel = the level the map mesh last printed it at, "-" for
		/// the realtime spikes or when not printed since the last change).
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
				string kind = t.GetType().Name;
				if (t is RM_Building_Ladder)
				{
					share = d <= 0 || lv <= 0f ? 0f : LiesFlat(t, t.Graphic) ? 1f
						: RM_SubmergeMath.LadderInPitShare(t.Rotation.AsInt, LadderDrop(t, eng, d), lv);
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
				string printed = t is Building_RM_Spikes || !eng.submergeDrawn.TryGetValue(map.cellIndices.CellToIndex(c), out byte pf)
					? "-" : RM_SubmergeMath.NoteLevel(pf).ToString("F2", CultureInfo.InvariantCulture);
				return "def=" + t.def.defName + " class=" + kind + " rot=" + t.Rotation.AsInt + " depth=" + d + " fill=" + f
					+ " level=" + lv.ToString("F2", CultureInfo.InvariantCulture) + " share=" + share.ToString("F3", CultureInfo.InvariantCulture) + " printedLevel=" + printed + " setting=" + (On ? "on" : "off");
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
