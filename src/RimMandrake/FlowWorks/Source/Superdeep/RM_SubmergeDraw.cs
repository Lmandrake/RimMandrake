using System.Collections.Generic;
using System.Globalization;
using System.Text;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL: what stands in a dug square drawn under the liquid in it by ONE rule,
	/// <see cref="RM_UnderLiquid"/> (owner's live look 2026-11-12: "It's as though each case is independently set in these
	/// variables, badly (major fix)"). Map-mesh things (ladders hung or lying flat, the pit ramp, items, minified things,
	/// the swale) are split where they are printed: SectionLayer_ThingsGeneral.TakePrintFrom opens a context for the thing
	/// (<see cref="Begin"/>), and every Printer_Plane.PrintPlane it makes (Graphic.Print, MinifiedThing's crate and its
	/// content, atlas tiles and flips included) is drawn whole, its drowned part covered in up to RM_UnderLiquid.Bands bands
	/// by its silhouette in the liquid's colour at 1 - RM_UnderLiquid.Seen (clear liquids: tinted by depth; opaque: only the
	/// part above the line is drawn); a thing lying on the floor (a vent, filth) is drawn under the liquid's sheet as the floor
	/// is; a print reaching past the pit's rim is cut at it (RM_UnderLiquid.ClipQuad). The realtime gates (RM_FlowDoors) and stakes (RM_Spikes) draw the same split from <see cref="Wet"/>
	/// and <see cref="DrawUnder"/>; the pit's walls and floor (SectionLayer_RMExcavationWalls) use the same level, cut and
	/// law. Setting pitSubmergeCutEnabled (on): off draws them whole over the liquid.
	///
	/// Cost: nothing while dry beyond one note per dug cell a thing was printed on. The note (RM_MapComponent_Excavation.
	/// submergeDrawn, cell index -> RM_UnderLiquid.LevelNote of the true level) is what the cell was printed at; the engine's
	/// picture-writer (ApplyFillTerrain, which every write of a dug square's liquid calls) re-meshes a noted cell whose note
	/// moved (<see cref="FillPictured"/>), and the re-print notes it again. Prints run only on a section rebuild; the split
	/// uses static buffers and cached cover materials.
	/// </summary>
	public static class RM_SubmergeDraw
	{
		public static bool On => RimMandrakeFlowWorksSettings.pitSubmergeCutEnabled;

		/// <summary>The quarter-notch note of the true level (whole notch + part-notch) standing on <paramref name="c"/>.</summary>
		public static int NoteAt(RM_MapComponent_Excavation eng, IntVec3 c)
		{
			return RM_UnderLiquid.LevelNote(eng.WaterDlAt(c) / (double)RM_LevelSolve.U);
		}

		/// <summary>Called by RM_MapComponent_Excavation.ApplyFillTerrain for a dug square while any cell is noted: a cell
		/// printed at another level re-meshes (its things, and the walls layer through RM_WaterLookDraw.LookFlag).</summary>
		public static void FillPictured(RM_MapComponent_Excavation eng, Map map, IntVec3 c, int index)
		{
			if (eng.submergeDrawn.TryGetValue(index, out int drawn) && drawn != NoteAt(eng, c))
			{
				eng.submergeDrawn.Remove(index);
				// the 4-argument form, adjacent squares too: a sluice square's sheet and a dry neighbour's floor reprint read this
				// square's level (RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE: a drained side kept its old picture)
				map.mapDrawer.MapMeshDirty(c, (ulong)MapMeshFlagDefOf.Buildings | (ulong)MapMeshFlagDefOf.Things | RM_WaterLookDraw.LookFlag,
					true, false);
			}
		}

		/// <summary>How clear the liquid on <paramref name="c"/> is (RM_LiquidSurfaceLook.seeThrough: the share of the view
		/// left after 1 m; 0 = opaque): the cell's fluid's look, else its terrain's, else fresh water's.</summary>
		public static float ClarityAt(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			RM_LiquidSurfaceLook look = LookAt(map, eng, c);
			return look != null ? look.seeThrough : 0f;
		}

		public static RM_LiquidSurfaceLook LookAt(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			FluidDef f = eng?.FluidAt(c);
			RM_LiquidSurfaceLook look = f != null ? RM_LiquidLooks.LookOfFluid(f) : null;
			if (look == null)
			{
				look = RM_LiquidSurface.LookFor(map.terrainGrid.TerrainAt(c));
			}
			if (look == null)
			{
				look = RM_LiquidSurface.LookFor(RM_WaterLadderDefs.Freshwater(RM_WaterLadder.Rung.VeryShallow));
			}
			return look;
		}

		/// <summary>The dug depth (notches), the true level (m, never above the floor's depth: no level above the bank) and
		/// the clarity under a thing; false when it stands on no dug square, the setting is off or it is dry. Notes the
		/// level printed at when <paramref name="noteIt"/> (a map-mesh print; a dry print too: the first liquid must re-mesh
		/// it). The realtime drawers pass false.</summary>
		public static bool Wet(Thing t, out int depth, out float levelMetres, out float clarity, bool noteIt = true)
		{
			depth = 0;
			levelMetres = 0f;
			clarity = 0f;
			if (!On || t == null || !t.Spawned)
			{
				return false;
			}
			Map map = t.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null)
			{
				return false;
			}
			IntVec3 c = t.Position;
			// a sunk geyser stands on its seat, the shallowest of its four squares (RM_GeyserPit)
			depth = t is Building_SteamGeyser g && RM_GeyserPit.On ? RM_GeyserPit.Read(g).seat : eng.HollowDepthAt(c);
			if (depth <= 0)
			{
				return false;
			}
			if (Pits.RM_PitCoverUtility.IsCovered(map, c) && !(t is Pawn p && Pits.RM_SuspensionUnderpass.InFloorBand(p)))
			{
				depth = 0;
				return false;   // stands on a deck over the pit, at bank height: dry, and no pit shadow
			}
			int note = NoteAt(eng, c);
			if (noteIt)
			{
				eng.submergeDrawn[map.cellIndices.CellToIndex(c)] = note;
			}
			if (note <= 0)
			{
				return false;
			}
			float lv = RM_UnderLiquid.NoteLevel(note);
			levelMetres = (lv > depth ? depth : lv) * RM_UnderLiquid.Notch;
			clarity = ClarityAt(map, eng, c);
			return true;
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

		/// <summary>The ramp points uphill: its downhill end is the opposite side.</summary>
		private static int RampFrom(int rot) => rot == 0 ? RM_UnderLiquid.FromSouth : rot == 1 ? RM_UnderLiquid.FromWest
			: rot == 2 ? RM_UnderLiquid.FromNorth : RM_UnderLiquid.FromEast;

		private static int RampRise(Thing t, RM_MapComponent_Excavation eng, int d)
		{
			IntVec3 up = t.Position + t.Rotation.FacingCell;
			return up.InBounds(t.Map) ? d - eng.HollowDepthAt(up) : d;
		}

		private static ThingDef swaleDef;
		private static bool swaleResolved;

		private static bool IsSwale(ThingDef d)
		{
			if (!swaleResolved)
			{
				swaleDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Swale");
				swaleResolved = true;
			}
			return d == swaleDef && d != null;
		}

		/// <summary>The drawn height (m) of a thing standing on the floor, or 0 when it is not one this draws.</summary>
		private static float StandingMetres(Thing t)
		{
			if (t is Building)
			{
				return BuildingMetres(t);
			}
			if (t is MinifiedThing)
			{
				return RM_UnderLiquid.MinifiedMetres;
			}
			if (t.def.category == ThingCategory.Item)
			{
				return RM_UnderLiquid.ItemMetres;
			}
			return IsSwale(t.def) ? RM_UnderLiquid.SwaleMetres : 0f;
		}

		/// <summary>RIMMANDRAKE_FIX_BIG_PIT_SCENE_BUILDINGS_STAY_DRY (owner's big-pit look 2026-11-12: "It's easy to see which
		/// items are not going under water"): an installed building stands by its cover (RM_UnderLiquid.BuildingMetres of
		/// fillPercent). 0 for the swale (a floor liner), the realtime gates and stakes (their own drawers) and covers and
		/// decks (they span the pit at bank height).</summary>
		private static float BuildingMetres(Thing t)
		{
			if (IsSwale(t.def))
			{
				return RM_UnderLiquid.SwaleMetres;
			}
			if (t is Building_SteamGeyser && RM_GeyserPit.On)
			{
				return RM_GeyserTubMath.GeyserMetres;   // RIMMANDRAKE_SINK_GEYSER_INTO_PIT_BUBBLING_HOT_TUB: a low vent mound
			}
			if (t is Building_Cooler || t is Building_Vent)
			{
				// RIMMANDRAKE_SINK_COOLER_ARROW_UNDER_TAR (owner 2026-11-13: "the Cooler still keeps its little red arrow icon
				// above the surface"): a wall-slot fitting is a metre high, not a full wall, so its arrow goes under with it
				return RM_UnderLiquid.WallSlotMetres;
			}
			if (t is RM_Building_Ladder || t is RM_Building_PitRamp || t is Building_RM_FlowDoor || t is Building_RM_Spikes
				|| t is Pits.Building_SpanDeck)
			{
				return 0f;
			}
			return RM_UnderLiquid.BuildingMetres(t.def.fillPercent);
		}

		// ── the print context (main thread only: section rebuilds) ──────────────

		private static bool ctxOn, inSplit, ctxWorld, ctxPit, ctxClip, ctxFlat, ctxVent;
		private static Thing ctxThing;
		private static float ctxRx0, ctxRz0, ctxRx1, ctxRz1;
		private static Color ctxCover;
		private static float ctxPitLevel, ctxPitClarity;
		private static int ctxFrom;
		private static float ctxShare, ctxLevel, ctxHeight, ctxClarity, ctxCut, ctxFoot;
		private static IntVec3 ctxCell;

		/// <summary>SectionLayer_ThingsGeneral.TakePrintFrom prefix: opens the split for a thing standing wet in a dug
		/// square (nothing for anything else).</summary>
		public static void Begin(Thing t)
		{
			ctxOn = false;
			ctxPit = false;
			ctxThing = null;
			ctxClip = false;
			ctxFlat = false;
			ctxVent = false;
			if (!On || t == null)
			{
				return;
			}
			bool ladder = t is RM_Building_Ladder, ramp = t is RM_Building_PitRamp;
			bool flat = LiesOnFloor(t), plant = t is Plant;
			float standing = ladder || ramp || flat ? 0f
				: plant ? RM_UnderLiquid.PlantMetres(t.def.graphicData != null ? t.def.graphicData.drawSize.y : 1f) : StandingMetres(t);
			if (!ladder && !ramp && !flat && standing <= 0f)
			{
				return;
			}
			bool wet = Wet(t, out int d, out float levelM, out float clarity);
			if (d > 0 && !ladder && !ramp && !IsSwale(t.def))
			{
				// RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE (owner 2026-11-13: "the chunks don't honor the pit, they overlap its
				// edges unphysically"): a sprite wider than its square is cut at the rim
				OpenClip(t, flat || t.def.category == ThingCategory.Item);
			}
			if (wet && (flat || plant))
			{
				// a vent, filth, a drowned plant: lies on the floor, so it is drawn under the liquid's sheet and seen as the floor
				// is (a plant only once wholly under; one standing partly out is drawn as vanilla does)
				ctxFlat = flat || levelM >= standing;
				ctxVent = t is Building_SteamGeyser;
				return;
			}
			if (plant)
			{
				return;
			}
			if (d > 0 && t is Building && standing > 0f && !IsSwale(t.def) && !(t is Building_SteamGeyser))
			{
				// a building standing in a pit, wet or dry: its vanilla shadows are off and it casts one floor shadow
				ctxPit = true;
				ctxThing = t;
				ctxPitLevel = levelM;
				ctxPitClarity = clarity;
			}
			if (!wet)
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(t.Map);
			ctxWorld = false;
			ctxFrom = RM_UnderLiquid.FromSouth;
			ctxLevel = levelM;
			ctxClarity = clarity;
			ctxCell = t.Position;
			int rot = t.Rotation.AsInt;
			if (ladder && !LiesFlat(t, t.Graphic))
			{
				if (rot == 2)
				{
					return;   // hung on the near wall: only its top above the near rim shows, never under
				}
				int drop = LadderDrop(t, eng, d);
				float cut = RM_UnderLiquid.Waterline(rot, drop, levelM / RM_UnderLiquid.Notch);
				if (cut < 0f)
				{
					return;
				}
				ctxWorld = true;
				ctxFrom = RM_UnderLiquid.HungFrom(rot);
				ctxCut = cut;
				ctxFoot = rot == 0 ? 1f - RM_UnderLiquid.NorthFace(drop)
					: rot == 1 ? 1f - RM_UnderLiquid.SideFace(drop) : RM_UnderLiquid.SideFace(drop);
			}
			else if (ladder)
			{
				ctxHeight = RM_UnderLiquid.LyingLadderMetres;
			}
			else if (ramp)
			{
				ctxFrom = RampFrom(rot);
				ctxHeight = RampRise(t, eng, d) * RM_UnderLiquid.Notch;
			}
			else
			{
				ctxHeight = standing;
			}
			ctxShare = RM_UnderLiquid.Share(levelM, 0f, ctxHeight);
			ctxCover = CoverColour(LookAt(t.Map, eng, t.Position), clarity);
			ctxOn = true;
		}

		public static void End()
		{
			ctxOn = false;
			ctxPit = false;
			ctxThing = null;
			ctxClip = false;
			ctxFlat = false;
			ctxVent = false;
		}

		/// <summary>Lies on the floor with no height of its own: filth, and a geyser sunk in a pit (its vent).</summary>
		private static bool LiesOnFloor(Thing t) => t is Filth || (t is Building_SteamGeyser && RM_GeyserPit.On);

		/// <summary>The rim clip: the rectangle the thing's prints are cut to. Each side reaches out over the dug squares beside
		/// the thing's footprint (every square of the next row dug and uncovered), up to <see cref="ClipReach"/> rows; a side
		/// reaching that far is open. A lying thing is cut on all four sides; a standing one not on the north, where its height
		/// rises out of the pit over the far bank as it should.</summary>
		private static void OpenClip(Thing t, bool fourSides)
		{
			Map map = t.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null)
			{
				return;
			}
			CellRect r = t.OccupiedRect();
			int w = Reach(map, eng, r, 0), e = Reach(map, eng, r, 1), s = Reach(map, eng, r, 2);
			int n = fourSides ? Reach(map, eng, r, 3) : ClipReach;
			ctxRx0 = w >= ClipReach ? float.NegativeInfinity : r.minX - w;
			ctxRx1 = e >= ClipReach ? float.PositiveInfinity : r.maxX + 1 + e;
			ctxRz0 = s >= ClipReach ? float.NegativeInfinity : r.minZ - s;
			ctxRz1 = n >= ClipReach ? float.PositiveInfinity : r.maxZ + 1 + n;
			ctxClip = w < ClipReach || e < ClipReach || s < ClipReach || n < ClipReach;
		}

		/// <summary>Rows of dug squares a sprite may reach past its footprint before the rim clip leaves that side open (no
		/// vanilla sprite overhangs its footprint by two squares).</summary>
		private const int ClipReach = 2;

		/// <summary>Rows (0..ClipReach) of dug, uncovered squares beside <paramref name="r"/> on a side (0 W, 1 E, 2 S, 3 N).</summary>
		private static int Reach(Map map, RM_MapComponent_Excavation eng, CellRect r, int side)
		{
			for (int k = 1; k <= ClipReach; k++)
			{
				bool alongX = side >= 2;
				int fixedAt = side == 0 ? r.minX - k : side == 1 ? r.maxX + k : side == 2 ? r.minZ - k : r.maxZ + k;
				int from = alongX ? r.minX : r.minZ, to = alongX ? r.maxX : r.maxZ;
				for (int i = from; i <= to; i++)
				{
					IntVec3 c = alongX ? new IntVec3(i, 0, fixedAt) : new IntVec3(fixedAt, 0, i);
					if (!c.InBounds(map) || eng.HollowDepthAt(c) <= 0 || Pits.RM_PitCoverUtility.IsCovered(map, c))
					{
						return k - 1;
					}
				}
			}
			return ClipReach;
		}

		/// <summary>Printer_Shadow prefix: no vanilla contact shadow from a building standing in a pit (it would lie on the
		/// liquid's surface); <see cref="FloorShadow"/> draws its one shadow instead.</summary>
		internal static bool InPit => ctxPit && !inSplit;

		/// <summary>How far the floor shadow reaches past a building's footprint on the sun's (south-west) side, and how far
		/// it stops short on the other.</summary>
		private const float ShadowReach = 0.18f, ShadowInset = 0.1f;

		/// <summary>TakePrintFrom finalizer: the one shadow of a building standing in a pit (owner 2026-11-12: "Shadows
		/// should ALWAYS be inside the pit ... it should simply be transparent to them as usual"), on the floor under it,
		/// reaching south-west only over dug cells, at RM_UnderLiquid.ThingShadow (seen through the liquid by the law).</summary>
		internal static void FloorShadow(SectionLayer layer)
		{
			if (!ctxPit || ctxThing == null || layer == null || !ctxThing.Spawned)
			{
				return;
			}
			// a flat thing (a vent, a rug) has no height to cast from (RIMMANDRAKE_REMOVE_DARK_SQUARE_AROUND_SUNK_GEYSER_UNWELCOME_BOX)
			ThingDef def = ctxThing.def;
			if (!RM_UnderLiquid.CastsFloorShadow(def.fillPercent, def.staticSunShadowHeight, def.graphicData?.shadowData != null))
			{
				return;
			}
			int q =(int)(RM_UnderLiquid.ThingShadow(ctxPitClarity, ctxPitLevel) * RM_UnderLiquid.Steps + 0.5f);
			if (q <= 0)
			{
				return;
			}
			Map map = ctxThing.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			CellRect r = ctxThing.OccupiedRect();
			IntVec3 west = new IntVec3(r.minX - 1, 0, r.minZ), south = new IntVec3(r.minX, 0, r.minZ - 1);
			float x0 = r.minX - (west.InBounds(map) && eng.HollowDepthAt(west) > 0 ? ShadowReach : 0f);
			float z0 = r.minZ - (south.InBounds(map) && eng.HollowDepthAt(south) > 0 ? ShadowReach : 0f);
			float x1 = r.maxX + 1f - ShadowInset, z1 = r.maxZ + 1f - ShadowInset;
			inSplit = true;
			try
			{
				Printer_Plane.PrintPlane(layer, new Vector3((x0 + x1) * 0.5f, AltitudeLayer.Shadows.AltitudeFor(), (z0 + z1) * 0.5f),
					new Vector2(x1 - x0, z1 - z0), ShadowMat(q));
			}
			finally
			{
				inSplit = false;
			}
		}

		private static readonly Material[] shadowMats = new Material[RM_UnderLiquid.Steps + 1];

		private static Texture2D featherTex;

		/// <summary>White, its alpha <see cref="RM_UnderLiquid.ShadowFeather"/> across the quad (built once, main thread).</summary>
		private static Texture2D FeatherTex
		{
			get
			{
				if (featherTex == null)
				{
					const int n = 32;
					Texture2D t = new Texture2D(n, n, TextureFormat.RGBA32, false)
					{
						name = "RM_PitFloorShadowFeather",
						wrapMode = TextureWrapMode.Clamp,
						filterMode = FilterMode.Bilinear
					};
					Color[] px = new Color[n * n];
					for (int z = 0; z < n; z++)
					{
						for (int x = 0; x < n; x++)
						{
							px[z * n + x] = new Color(1f, 1f, 1f, RM_UnderLiquid.ShadowFeather((x + 0.5f) / n, (z + 0.5f) / n));
						}
					}
					t.SetPixels(px);
					t.Apply(false, true);
					featherTex = t;
				}
				return featherTex;
			}
		}

		private static Material ShadowMat(int q)
		{
			Material m = shadowMats[q];
			if (m == null)
			{
				// under the liquid's sheet, so the sheet hides it by the law like the floor it lies on (a pooled Transparent
				// material drew it over the water: an untinted dark square under every drowned thing); a soft-edged pool,
				// never a hard rectangle
				m = new Material(MaterialPool.MatFrom(new MaterialRequest(FeatherTex, ShaderDatabase.Transparent,
					new Color(0f, 0f, 0f, (float)q / RM_UnderLiquid.Steps)))) { renderQueue = RM_FaceMaterial.UnderSheetQueue };
				shadowMats[q] = m;
			}
			return m;
		}

		/// <summary>SectionLayer_SunShadows reads the edifice grid through this: a building standing in a pit casts no
		/// vanilla sun shadow (it fell onto the liquid's surface and the bank; owner 2026-11-12), and does not shade its
		/// neighbours' sides.</summary>
		public static Building ShadowCaster(Building b)
		{
			if (b == null || !On || !b.Spawned)
			{
				return b;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(b.Map);
			return eng != null && eng.HollowDepthAt(b.Position) > 0 ? null : b;
		}

		/// <summary>How much of a thing's label (quality, stack count, owner) shows: it fades with the thing's top
		/// (RM_UnderLiquid.LabelAlpha); 1 for anything not standing wet in a pit.</summary>
		public static float LabelAlpha(Thing t)
		{
			if (!On || t == null || !(t.def.category == ThingCategory.Item || t is Building))
			{
				return 1f;
			}
			float h = StandingMetres(t);
			if (h <= 0f || !Wet(t, out int _, out float levelM, out float clarity, false))
			{
				return 1f;
			}
			return RM_UnderLiquid.LabelAlpha(clarity, levelM, h);
		}

		// ── pawns and corpses (realtime): her own picture cut at the surface ─────────────────

		/// <summary>The liquid's colour where it covers a pawn: a clear liquid's body colour (the sheet's,
		/// <see cref="BodyColour"/>), an opaque liquid's own tint.</summary>
		private static Color CoverColour(RM_LiquidSurfaceLook look, float clarity)
		{
			if (!(clarity > 0f))
			{
				return look != null ? look.tint : Color.black;
			}
			return BodyColour(look);
		}

		private static readonly Dictionary<RM_LiquidSurfaceLook, RM_UnderLiquid.Float3> liquidColours =
			new Dictionary<RM_LiquidSurfaceLook, RM_UnderLiquid.Float3>();

		/// <summary>A clear liquid's body colour (RM_UnderLiquid.Body): the colour of the LiquidDef whose look this is (its
		/// own, or its canal fluid's), so each clear liquid keeps its own colour; fresh water's x seeThroughTint when no
		/// LiquidDef owns the look.</summary>
		public static Color BodyColour(RM_LiquidSurfaceLook look)
		{
			RM_UnderLiquid.Float3 b = RM_UnderLiquid.Body(LiquidColour(look));
			return new Color(b.r, b.g, b.b);
		}

		/// <summary>The colour of the liquid a look belongs to (its LiquidDef's colour; fresh water's when none owns it). The
		/// geyser plume bubbles in it (RM_GeyserTubMath.BubbleColour).</summary>
		internal static RM_UnderLiquid.Float3 LiquidColour(RM_LiquidSurfaceLook look)
		{
			if (look == null)
			{
				return RM_UnderLiquid.WaterColour;
			}
			if (liquidColours.TryGetValue(look, out RM_UnderLiquid.Float3 known))
			{
				return known;
			}
			Color? own = null;
			foreach (LiquidTypes.LiquidDef l in DefDatabase<LiquidTypes.LiquidDef>.AllDefsListForReading)
			{
				if (l.surfaceLook == look || (l.canalFluid != null && l.canalFluid.surfaceLook == look))
				{
					own = l.color;
					break;
				}
			}
			Color t = look.seeThroughTint;
			RM_UnderLiquid.Float3 w = RM_UnderLiquid.WaterColour;
			RM_UnderLiquid.Float3 c = own.HasValue ? new RM_UnderLiquid.Float3(own.Value.r, own.Value.g, own.Value.b)
				: new RM_UnderLiquid.Float3(w.r * t.r, w.g * t.g, w.b * t.b);
			liquidColours[look] = c;
			return c;
		}

		/// <summary>The drawn height (m) of a pawn under the law: standing, its climb-size height (RM_Drowning.HeightOf);
		/// lying, downed or dead, RM_UnderLiquid.CorpseMetres.</summary>
		public static float PawnMetres(Pawn p, bool dead) => dead || RM_Drowning.Lying(p) ? RM_UnderLiquid.CorpseMetres : RM_Drowning.HeightOf(p);

		/// <summary>The cut open for the render tree drawing now (PawnRenderTree.Draw, main thread). A tree drawn inside
		/// another (a carried pawn, drawn by her carrier's Carried node) opens its own and restores the outer one after.</summary>
		private struct PawnCutState
		{
			public bool on;
			public RM_PawnCutMath.Mode mode;
			public float lineZ;
			public bool clear;
			public Color tint;
		}

		private static PawnCutState cut;
		private static readonly Stack<PawnCutState> outerCuts = new Stack<PawnCutState>();

		/// <summary>Pawns (thingIDNumber) drawn wet on the last draw: vanilla's far-zoom cached frame (one atlas quad, no render
		/// tree) is turned off for them so the cut can see her nodes. Written on the main thread in the draw phase only; read
		/// by ParallelGetPreRenderResults (worker threads, before that phase; no writer runs then).</summary>
		private static readonly HashSet<int> wetPawns = new HashSet<int>();

		internal static bool NoCachedFrame(Pawn p) => p != null && wetPawns.Contains(p.thingIDNumber);

		/// <summary>PawnRenderer.RenderPawnAt prefix (main thread, every draw): marks a pawn (or a corpse's pawn) standing,
		/// lying or dead wet in a pit, so her next draw skips vanilla's far-zoom atlas (<see cref="NoCachedFrame"/>). The atlas
		/// path never reaches PawnRenderTree.Draw, so a mark set only there was never set for a pawn first seen at far zoom
		/// (live matrix 2026-11-22: every wet colonist read noCache=False).</summary>
		internal static void NoteWet(Pawn pawn)
		{
			if (!On || pawn == null)
			{
				return;
			}
			Corpse corpse = pawn.Spawned ? null : pawn.ParentHolder as Corpse;
			Thing at = pawn.Spawned ? pawn : corpse;
			if (at == null)
			{
				return;   // carried, or a statue's or a preview's pawn: not in a liquid
			}
			if (at.Spawned && !pawn.Swimming && !pawn.Flying && Wet(at, out int _, out float _, out float _, false))
			{
				wetPawns.Add(pawn.thingIDNumber);
			}
			else
			{
				wetPawns.Remove(pawn.thingIDNumber);
			}
		}

		private static readonly AccessTools.FieldRef<PawnRenderTree, List<PawnGraphicDrawRequest>> RequestsOf =
			AccessTools.FieldRefAccess<PawnRenderTree, List<PawnGraphicDrawRequest>>("drawRequests");

		/// <summary>PawnRenderTree.Draw prefix: decides the cut for this pawn by RM_PawnCutMath.Decide (standing: a line at her
		/// body landmarks on her own picture; lying: whole and tinted; carried: whole) and opens it for every node the tree
		/// draws (GenDraw.DrawMeshNowOrLater, <see cref="DrawCutNode"/>). Portraits, the atlas cache, statues and drawNow
		/// renders are never cut.</summary>
		internal static void BeginPawnCut(PawnRenderTree tree, PawnDrawParms parms)
		{
			outerCuts.Push(cut);
			cut = default(PawnCutState);
			Pawn pawn = parms.pawn;
			if (!On || pawn == null || parms.DrawNow || parms.Portrait || parms.Cache || parms.Statue || parms.swimming || pawn.Flying)
			{
				return;
			}
			Corpse corpse = pawn.Spawned ? null : pawn.ParentHolder as Corpse;
			Thing at = pawn.Spawned ? pawn : corpse;   // carried (held by a carry tracker): neither, so whole
			float levelM = 0f, clarity = 0f;
			bool wet = at != null && at.Spawned && Wet(at, out int _, out levelM, out clarity, false);
			if (at != null)
			{
				// a corpse's pawn too: vanilla draws a dead body from the atlas at far zoom as well
				if (wet)
				{
					wetPawns.Add(pawn.thingIDNumber);
				}
				else
				{
					wetPawns.Remove(pawn.thingIDNumber);
				}
			}
			if (!wet || (parms.matrix.Position() - at.DrawPos).MagnitudeHorizontalSquared() > 1f)
			{
				return;   // dry, or drawn somewhere else (a drafted-move preview ghost): not standing in this liquid
			}
			bool lying = corpse != null || parms.dead || RM_Drowning.Lying(pawn);
			List<PawnGraphicDrawRequest> reqs = RequestsOf(tree);
			bool humanlike = pawn.RaceProps.Humanlike && HasHeadNode(reqs);
			RM_PawnCutMath.Mode mode = RM_PawnCutMath.Decide(lying, false, humanlike, levelM, RM_Drowning.HeightOf(pawn),
				RM_UnderLiquid.CorpseMetres, clarity, out float share, out float strength);
			if (mode == RM_PawnCutMath.Mode.Whole)
			{
				return;
			}
			if (mode == RM_PawnCutMath.Mode.Hidden)
			{
				// wholly under an opaque liquid: none of her picture is drawn. The realtime gate (RealtimeRead) usually skips
				// her draw already, but its boundary is strict: a hare in exactly her own height of tar passed it and was drawn
				// whole (live matrix 2026-11-22). Her name label, her alert and a click still find her.
				cut = new PawnCutState { on = true, mode = mode };
				return;
			}
			float lineZ = 0f;
			if (mode == RM_PawnCutMath.Mode.Cut)
			{
				if (!PictureExtent(reqs, out float foot, out float crown))
				{
					return;   // no node to measure: drawn whole rather than cut at a guessed line
				}
				lineZ = RM_PawnCutMath.LineZ(foot, crown, share);
			}
			RM_LiquidSurfaceLook look = LookAt(at.Map, RM_SuperdeepTrap.EngineOf(at.Map), at.Position);
			Color liquid = CoverColour(look, clarity);
			// the drowned part is seen as the floor under the full depth, in the same steps as a print (round 7)
			float seen = clarity > 0f ? (float)RM_UnderLiquid.DrownedStep(clarity, levelM) / RM_UnderLiquid.Steps : 0f;
			RM_UnderLiquid.Float3 k = RM_PawnCutMath.TintFactor(new RM_UnderLiquid.Float3(liquid.r, liquid.g, liquid.b), seen, strength);
			cut = new PawnCutState { on = true, mode = mode, lineZ = lineZ, clear = clarity > 0f, tint = new Color(k.r, k.g, k.b, 1f) };
		}

		/// <summary>PawnRenderTree.Draw finalizer: the outer tree's cut (or none) again.</summary>
		internal static void EndPawnCut()
		{
			cut = outerCuts.Count > 0 ? outerCuts.Pop() : default(PawnCutState);
		}

		private static bool HasHeadNode(List<PawnGraphicDrawRequest> reqs)
		{
			for (int i = 0; i < reqs.Count; i++)
			{
				if (reqs[i].node?.Props?.tagDef == PawnRenderNodeTagDefOf.Head)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Her picture's world z extent: from the lowest to the highest drawn pixel of her body and head nodes (her
		/// own body, so a hat or a pack does not move the line), every drawn node when the tree tags neither (a mechanoid or a
		/// modded body). False when no node could be measured.</summary>
		private static bool PictureExtent(List<PawnGraphicDrawRequest> reqs, out float foot, out float crown)
		{
			foot = float.PositiveInfinity;
			crown = float.NegativeInfinity;
			for (int pass = 0; pass < 2 && foot > crown; pass++)
			{
				for (int i = 0; i < reqs.Count; i++)
				{
					PawnGraphicDrawRequest r = reqs[i];
					if (r.mesh == null || r.material == null)
					{
						continue;
					}
					PawnRenderNodeTagDef tag = r.node?.Props?.tagDef;
					if (pass == 0 && tag != PawnRenderNodeTagDefOf.Body && tag != PawnRenderNodeTagDefOf.Head)
					{
						continue;
					}
					if (!Rows(r.material.mainTexture, out float c0, out float c1))
					{
						continue;
					}
					MeshSpan span = SpanOf(r.mesh);
					Matrix4x4 m = r.preDrawnComputedMatrix;
					RM_PawnCutMath.NodeExtent(span.zMin, span.zMax, span.vMin, span.vMax, c0, c1, m.m22, m.m20 * span.xMid + m.m23,
						out float lo, out float hi);
					foot = Mathf.Min(foot, lo);
					crown = Mathf.Max(crown, hi);
				}
			}
			return foot < crown;
		}

		private struct MeshSpan
		{
			public float zMin, zMax, vMin, vMax, xMid;
			public Vector3[] verts;
			public Vector2[] uvs;
			public int[] tris;
		}

		private static readonly Dictionary<int, MeshSpan> meshSpans = new Dictionary<int, MeshSpan>();

		/// <summary>A pawn mesh's local z and texture-row span, and its arrays (read once per mesh: pawn meshes are MeshPool's
		/// shared planes).</summary>
		private static MeshSpan SpanOf(Mesh mesh)
		{
			int id = mesh.GetInstanceID();
			if (meshSpans.TryGetValue(id, out MeshSpan s))
			{
				return s;
			}
			s.verts = mesh.vertices;
			s.uvs = mesh.uv;
			s.tris = mesh.triangles;
			s.zMin = float.PositiveInfinity;
			s.zMax = float.NegativeInfinity;
			float vAtZMin = 0f, vAtZMax = 1f, xMin = float.PositiveInfinity, xMax = float.NegativeInfinity;
			for (int i = 0; i < s.verts.Length; i++)
			{
				Vector3 v = s.verts[i];
				float tv = i < s.uvs.Length ? s.uvs[i].y : 0f;
				if (v.z < s.zMin)
				{
					s.zMin = v.z;
					vAtZMin = tv;
				}
				if (v.z > s.zMax)
				{
					s.zMax = v.z;
					vAtZMax = tv;
				}
				xMin = Mathf.Min(xMin, v.x);
				xMax = Mathf.Max(xMax, v.x);
			}
			s.vMin = vAtZMin;
			s.vMax = vAtZMax;
			s.xMid = s.verts.Length > 0 ? (xMin + xMax) * 0.5f : 0f;
			meshSpans[id] = s;
			return s;
		}

		/// <summary>Rows (0 bottom .. 1 top) a texture holds drawn pixels in (alpha over 0.1): read once per texture, by a
		/// small blit (game textures are not CPU-readable). False when it holds none or cannot be read.</summary>
		private static readonly Dictionary<int, Vector2> textureRows = new Dictionary<int, Vector2>();

		private static bool Rows(Texture tex, out float c0, out float c1)
		{
			c0 = 0f;
			c1 = 1f;
			if (tex == null)
			{
				return false;
			}
			int id = tex.GetInstanceID();
			if (!textureRows.TryGetValue(id, out Vector2 r))
			{
				r = ReadRows(tex);
				textureRows[id] = r;
			}
			if (!(r.y > r.x))
			{
				return false;
			}
			c0 = r.x;
			c1 = r.y;
			return true;
		}

		private static Vector2 ReadRows(Texture tex)
		{
			int w = Mathf.Clamp(tex.width, 1, 64), h = Mathf.Clamp(tex.height, 1, 128);
			RenderTexture prev = RenderTexture.active;
			RenderTexture rt = RenderTexture.GetTemporary(w, h, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Linear);
			Texture2D read = null;
			try
			{
				UnityEngine.Graphics.Blit(tex, rt);
				RenderTexture.active = rt;
				read = new Texture2D(w, h, TextureFormat.ARGB32, false);
				read.ReadPixels(new Rect(0, 0, w, h), 0, 0, false);
				read.Apply(false);
				Color32[] px = read.GetPixels32();
				int lo = -1, hi = -1;
				for (int y = 0; y < h; y++)
				{
					for (int x = 0; x < w; x++)
					{
						if (px[y * w + x].a > 25)
						{
							if (lo < 0)
							{
								lo = y;
							}
							hi = y;
							break;
						}
					}
				}
				return lo < 0 ? Vector2.zero : new Vector2((float)lo / h, (float)(hi + 1) / h);
			}
			catch (System.Exception e)
			{
				Log.WarningOnce("[FlowWorks] could not read a pawn texture's drawn rows (" + tex.name + "): " + e.Message, tex.GetInstanceID() ^ 0x5C07);
				return Vector2.zero;
			}
			finally
			{
				RenderTexture.active = prev;
				RenderTexture.ReleaseTemporary(rt);
				if (read != null)
				{
					UnityEngine.Object.Destroy(read);
				}
			}
		}

		/// <summary>GenDraw.DrawMeshNowOrLater prefix while a cut is open: true when this drew the node (cut at the line, or
		/// tinted whole), false = vanilla draws it as asked.</summary>
		internal static bool DrawCutNode(Mesh mesh, Matrix4x4 matrix, Material mat, bool drawNow, MaterialPropertyBlock props)
		{
			if (!cut.on || drawNow || mesh == null || mat == null)
			{
				return false;
			}
			if (cut.mode == RM_PawnCutMath.Mode.Hidden)
			{
				return true;   // under an opaque liquid: not drawn
			}
			if (cut.mode == RM_PawnCutMath.Mode.Tinted)
			{
				DrawTinted(mesh, matrix, mat, props);
				return true;
			}
			MeshSpan s = SpanOf(mesh);
			Mesh upper = ClipMesh(mesh, s, matrix, cut.lineZ, true);
			if (upper != null)
			{
				UnityEngine.Graphics.DrawMesh(upper, matrix, mat, 0, null, 0, props);
			}
			if (cut.clear)
			{
				Mesh lower = ClipMesh(mesh, s, matrix, cut.lineZ, false);
				if (lower != null)
				{
					DrawTinted(lower, matrix, mat, props);
				}
			}
			return true;
		}

		/// <summary>PawnOverlayDrawer.DoDrawCall's Graphics.DrawMesh, rerouted (Patch_RM_SubmergePawnOverlay): a wound or
		/// overlay decal on a pawn inside an open cut is cut and tinted with her, as every other part of her is.</summary>
		public static void DrawOverlayMesh(Mesh mesh, Matrix4x4 matrix, Material mat, int layer, Camera camera, int submesh,
			MaterialPropertyBlock props)
		{
			if (!DrawCutNode(mesh, matrix, mat, false, props))
			{
				UnityEngine.Graphics.DrawMesh(mesh, matrix, mat, layer, camera, submesh, props);
			}
		}

		private static readonly MaterialPropertyBlock tintBlock = new MaterialPropertyBlock();

		/// <summary>Draws <paramref name="mesh"/> in its own material with its colours multiplied by the cut's tint (the liquid
		/// over it), through the node's own property block (its colour restored after).</summary>
		private static void DrawTinted(Mesh mesh, Matrix4x4 matrix, Material mat, MaterialPropertyBlock props)
		{
			int colId = ShaderPropertyIDs.Color, twoId = ShaderPropertyIDs.ColorTwo;
			bool hasTwo = mat.HasProperty(twoId);
			if (props == null)
			{
				tintBlock.Clear();
				tintBlock.SetColor(colId, mat.color * cut.tint);
				if (hasTwo)
				{
					tintBlock.SetColor(twoId, mat.GetColor(twoId) * cut.tint);
				}
				UnityEngine.Graphics.DrawMesh(mesh, matrix, mat, 0, null, 0, tintBlock);
				return;
			}
			Color col = props.HasColor(colId) ? props.GetColor(colId) : mat.color;
			bool hadTwo = props.HasColor(twoId);
			Color two = hadTwo ? props.GetColor(twoId) : (hasTwo ? mat.GetColor(twoId) : Color.white);
			props.SetColor(colId, col * cut.tint);
			if (hasTwo || hadTwo)
			{
				props.SetColor(twoId, two * cut.tint);
			}
			UnityEngine.Graphics.DrawMesh(mesh, matrix, mat, 0, null, 0, props);
			props.SetColor(colId, col);
			if (hasTwo || hadTwo)
			{
				props.SetColor(twoId, two);
			}
		}

		// the cut meshes: a pool reused frame by frame (a mesh queued by Graphics.DrawMesh is read at render time, so each is
		// written once per frame)
		private static readonly List<Mesh> cutPool = new List<Mesh>();
		private static int cutPoolUsed, cutPoolFrame = -1;
		private static readonly List<Vector3> cutVerts = new List<Vector3>();
		private static readonly List<Vector2> cutUvs = new List<Vector2>();
		private static readonly List<int> cutTris = new List<int>();
		private static readonly float[] triA = new float[5], triB = new float[5], triC = new float[5];
		private static readonly float[] cutPoly = new float[RM_PawnCutMath.MaxPolyCorners * 5];

		/// <summary>The part of <paramref name="mesh"/> above (<paramref name="keepAbove"/>) or below the world line z =
		/// <paramref name="lineZ"/> once placed by <paramref name="matrix"/>: the mesh itself when all of it is on that side,
		/// null when none is, else a pooled mesh of its clipped triangles (uvs carried, so the picture is cut, not
		/// stretched).</summary>
		private static Mesh ClipMesh(Mesh mesh, MeshSpan s, Matrix4x4 matrix, float lineZ, bool keepAbove)
		{
			float kx = matrix.m20, ky = matrix.m21, kz = matrix.m22, w = matrix.m23 - lineZ;
			int above = 0, n = s.verts.Length;
			for (int i = 0; i < n; i++)
			{
				Vector3 v = s.verts[i];
				if (kx * v.x + ky * v.y + kz * v.z + w >= 0f)
				{
					above++;
				}
			}
			if (above == n)
			{
				return keepAbove ? mesh : null;
			}
			if (above == 0)
			{
				return keepAbove ? null : mesh;
			}
			cutVerts.Clear();
			cutUvs.Clear();
			cutTris.Clear();
			for (int t = 0; t + 2 < s.tris.Length; t += 3)
			{
				Fill(triA, s, s.tris[t]);
				Fill(triB, s, s.tris[t + 1]);
				Fill(triC, s, s.tris[t + 2]);
				int k = RM_PawnCutMath.ClipTriangle(triA, triB, triC, kx, ky, kz, w, keepAbove, cutPoly);
				int b0 = cutVerts.Count;
				for (int i = 0; i < k; i++)
				{
					cutVerts.Add(new Vector3(cutPoly[i * 5], cutPoly[i * 5 + 1], cutPoly[i * 5 + 2]));
					cutUvs.Add(new Vector2(cutPoly[i * 5 + 3], cutPoly[i * 5 + 4]));
				}
				for (int i = 1; i + 1 < k; i++)
				{
					cutTris.Add(b0);
					cutTris.Add(b0 + i);
					cutTris.Add(b0 + i + 1);
				}
			}
			if (cutTris.Count == 0)
			{
				return null;
			}
			if (cutPoolFrame != Time.frameCount)
			{
				cutPoolFrame = Time.frameCount;
				cutPoolUsed = 0;
			}
			if (cutPoolUsed >= cutPool.Count)
			{
				Mesh fresh = new Mesh { name = "RM_PawnCut" };
				fresh.MarkDynamic();
				cutPool.Add(fresh);
			}
			Mesh m = cutPool[cutPoolUsed++];
			m.Clear();
			m.SetVertices(cutVerts);
			m.SetUVs(0, cutUvs);
			m.SetTriangles(cutTris, 0);
			m.RecalculateBounds();
			return m;
		}

		private static void Fill(float[] dst, MeshSpan s, int i)
		{
			Vector3 v = s.verts[i];
			Vector2 uv = i < s.uvs.Length ? s.uvs[i] : Vector2.zero;
			dst[0] = v.x;
			dst[1] = v.y;
			dst[2] = v.z;
			dst[3] = uv.x;
			dst[4] = uv.y;
		}

		/// <summary>Live matrix (northstar/pawn_in_liquid_matrix.py): <see cref="ProofPawnCut"/> for the pawn, or the corpse's
		/// pawn, whose ThingID is <paramref name="id"/> on the current map.</summary>
		public static string ProofPawnCutId(string id)
		{
			Map map = Find.CurrentMap;
			string want = (id ?? "").Trim();
			if (map == null || want.Length == 0)
			{
				return "PAWNCUT none";
			}
			foreach (Thing t in map.listerThings.AllThings)
			{
				Pawn p = t as Pawn ?? (t as Corpse)?.InnerPawn;
				if (p != null && (t.ThingID == want || p.ThingID == want))
				{
					return ProofPawnCut(p);
				}
			}
			return "PAWNCUT " + want + " notfound";
		}

		/// <summary>Live matrix: the player's click at a map point "x,z" (floats) as vanilla's Selector reads it
		/// (GenUI.ThingsUnderMouse at 1 cell with the click's targeting, mustBeSelectable), then selects the first hit as a
		/// click does. "SELECT first=&lt;ThingID|none&gt; selected=&lt;ThingID|none&gt; hits=a,b,...".</summary>
		public static string ProofSelectAt(string arg)
		{
			Map map = Find.CurrentMap;
			string[] p = (arg ?? "").Split(',');
			if (map == null || p.Length < 2 || !float.TryParse(p[0].Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out float x)
				|| !float.TryParse(p[1].Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out float z))
			{
				return "REFUSED: want x,z";
			}
			TargetingParameters clickParams = new TargetingParameters
			{
				mustBeSelectable = true,
				canTargetPawns = true,
				canTargetBuildings = true,
				canTargetItems = true,
				mapObjectTargetsMustBeAutoAttackable = false
			};
			List<Thing> hits = GenUI.ThingsUnderMouse(new Vector3(x, 0f, z), 1f, clickParams);
			Thing first = hits.Count > 0 ? hits[0] : null;
			Find.Selector.ClearSelection();
			if (first != null)
			{
				Find.Selector.Select(first, false, true);
			}
			Thing sel = Find.Selector.SingleSelectedThing;
			StringBuilder sb = new StringBuilder("SELECT first=").Append(first != null ? first.ThingID : "none")
				.Append(" selected=").Append(sel != null ? sel.ThingID : "none").Append(" hits=");
			for (int i = 0; i < hits.Count && i < 8; i++)
			{
				sb.Append(i > 0 ? "," : "").Append(hits[i].ThingID);
			}
			return sb.ToString();
		}

		/// <summary>A proof line for one pawn (the live matrix reads it): the decision, the line and her picture's extent as the
		/// last draw measured them. "PAWNCUT id mode=... share=... level=... height=... clarity=... lying=... foot=... crown=...
		/// line=..." or "PAWNCUT id none".</summary>
		public static string ProofPawnCut(Pawn pawn)
		{
			if (pawn == null)
			{
				return "PAWNCUT none";
			}
			CultureInfo inv = CultureInfo.InvariantCulture;
			Corpse corpse = pawn.Spawned ? null : pawn.ParentHolder as Corpse;
			Thing at = pawn.Spawned ? pawn : corpse;
			if (at == null || !at.Spawned || !Wet(at, out int _, out float levelM, out float clarity, false))
			{
				return "PAWNCUT " + pawn.ThingID + " dry";
			}
			bool lying = corpse != null || RM_Drowning.Lying(pawn);
			PawnRenderTree tree = pawn.Drawer?.renderer?.renderTree;
			List<PawnGraphicDrawRequest> reqs = tree != null ? RequestsOf(tree) : null;
			bool humanlike = pawn.RaceProps.Humanlike && reqs != null && HasHeadNode(reqs);
			float h = RM_Drowning.HeightOf(pawn);
			RM_PawnCutMath.Mode mode = RM_PawnCutMath.Decide(lying, false, humanlike, levelM, h, RM_UnderLiquid.CorpseMetres, clarity,
				out float share, out float strength);
			StringBuilder sb = new StringBuilder("PAWNCUT ").Append(pawn.ThingID).Append(" mode=").Append(mode)
				.Append(" share=").Append(share.ToString("0.###", inv)).Append(" tint=").Append(strength.ToString("0.###", inv))
				.Append(" level=").Append(levelM.ToString("0.###", inv)).Append(" height=").Append(h.ToString("0.###", inv))
				.Append(" clarity=").Append(clarity.ToString("0.###", inv)).Append(" lying=").Append(lying)
				.Append(" humanlike=").Append(humanlike).Append(" noCache=").Append(NoCachedFrame(pawn));
			if (reqs != null && PictureExtent(reqs, out float foot, out float crown))
			{
				sb.Append(" foot=").Append(foot.ToString("0.###", inv)).Append(" crown=").Append(crown.ToString("0.###", inv))
					.Append(" line=").Append(RM_PawnCutMath.LineZ(foot, crown, share).ToString("0.###", inv))
					.Append(" drawZ=").Append(pawn.DrawPos.z.ToString("0.###", inv));
			}
			return sb.ToString();
		}

		// ── the realtime layer (RIMMANDRAKE_SINK_HOSES_AND_OVERLAYS_TORCHES_BURN_IN_TAR) ─────────────────
		// Everything the map draws per frame passes Thing.DynamicDrawPhase (DynamicDrawManager): a Book (RealtimeOnly by the
		// ThingDef default, never printed), a torch's flame (a comp's PostDraw inside its thing's DrawAt), a turret top, a
		// corpse, a pawn. The law is applied there, by layer, not per kind: a thing standing wet in a pit whose top is hidden
		// (RM_UnderLiquid.LabelAlpha 0: an opaque liquid over it) is not drawn at all; one partly seen draws every Graphic it
		// draws through Graphic.DrawMeshInt split and faded like a print (DrawUnder), and a flame under the line is out.
		// Overlays (OverlayDrawer: power off, needs power, broken down, out of fuel, forbidden) take their thing's tint and hide half a metre under (RM_UnderLiquid.OverlayAlpha).

		[System.ThreadStatic] private static bool rtOn;
		private static float rtLevel, rtHeight, rtClarity, rtShare;
		private static Thing rtThing;

		/// <summary>The drawn height (m) the law gives a realtime thing: a pawn's (PawnMetres), a corpse's, else a standing
		/// thing's (StandingMetres); 0 = not one the law draws (motes, fire, projectiles, filth).</summary>
		private static float RealtimeMetres(Thing t)
		{
			if (t is Pawn p)
			{
				return p.Swimming || p.Flying ? 0f : PawnMetres(p, false);
			}
			if (t is Corpse c)
			{
				return c.InnerPawn != null ? PawnMetres(c.InnerPawn, true) : RM_UnderLiquid.CorpseMetres;
			}
			return t.def.category == ThingCategory.Item || t is Building ? StandingMetres(t) : 0f;
		}

		/// <summary>Thing.DynamicDrawPhase prefix (the Draw phase only: the parallel pre-draw runs off the main thread): false =
		/// hidden under the liquid, not drawn; else opens the realtime split for a thing partly seen.</summary>
		internal static bool BeginRealtime(Thing t, DrawPhase phase)
		{
			rtOn = false;
			if (phase != DrawPhase.Draw)
			{
				return true;
			}
			RealtimeVerdict v = RealtimeRead(t, out float share, out float levelM, out float clarity, out float h);
			if (v == RealtimeVerdict.Hidden)
			{
				return false;   // its top is under an opaque liquid: nothing of it shows
			}
			if (v != RealtimeVerdict.Split)
			{
				return true;
			}
			rtShare = share;
			rtLevel = levelM;
			rtHeight = h;
			rtClarity = clarity;
			rtThing = t;
			rtOn = true;
			return true;
		}

		/// <summary>What the realtime gate does with a thing: drawn whole (dry, off a pit, nothing to cut), hidden, drawn as its
		/// own picture cut at the line (a wading or lying body: its render tree's nodes, BeginPawnCut) or split at the line.</summary>
		internal enum RealtimeVerdict { Whole, Hidden, BodyCover, Split }

		/// <summary>The realtime gate's decision for <paramref name="t"/>, read only (BeginRealtime and ProofOverlays share it).</summary>
		internal static RealtimeVerdict RealtimeRead(Thing t, out float share, out float levelM, out float clarity, out float h)
		{
			share = 0f;
			levelM = 0f;
			clarity = 0f;
			h = 0f;
			if (!On || t == null || !t.Spawned)
			{
				return RealtimeVerdict.Whole;
			}
			h = RealtimeMetres(t);
			if (h <= 0f || !Wet(t, out int _, out levelM, out clarity, false))
			{
				return RealtimeVerdict.Whole;
			}
			if (RM_UnderLiquid.LabelAlpha(clarity, levelM, h) <= 0f)
			{
				return RealtimeVerdict.Hidden;
			}
			if (t is Pawn || t is Corpse)
			{
				return RealtimeVerdict.BodyCover;
			}
			share = RM_UnderLiquid.Share(levelM, 0f, h);
			return share <= 0f ? RealtimeVerdict.Whole : RealtimeVerdict.Split;
		}

		internal static void EndRealtime()
		{
			rtOn = false;
		}

		/// <summary>Graphic.DrawMeshInt prefix: inside the realtime split, the mesh is drawn as its part above the line plus its
		/// drowned bands at the law's alpha (DrawUnder); false = drawn here.</summary>
		internal static bool DrawRealtime(Mesh mesh, Vector3 loc, Quaternion quat, Material mat)
		{
			if (!rtOn || mesh == null || mat == null)
			{
				return true;
			}
			Vector3 b = mesh.bounds.size;
			Vector2 size = new Vector2(b.x, b.z);
			bool flip = mesh == MeshPool.GridPlaneFlip(size);
			rtOn = false;   // DrawUnder draws through Graphics directly; nothing re-enters, but never split twice
			try
			{
				DrawUnder(mesh, size, Matrix4x4.TRS(loc, quat, Vector3.one), mat, rtLevel, rtHeight, rtClarity, flip, rtThing);
			}
			finally
			{
				rtOn = true;
			}
			return false;
		}

		/// <summary>How much of a cord or rope lying on the floor at (<paramref name="x"/>, <paramref name="z"/>) shows through
		/// the liquid over it (RM_UnderLiquid.Seen at the level; 1 off a pit, dry, on a deck or with the setting off). Gimme Some
		/// Slack calls it by name (SectionLayer_RM_MessyCords, a section rebuild, main thread) and the cell is noted like any
		/// print, so a level change re-meshes it (FillPictured dirties Buildings, which the cord layer listens to).</summary>
		public static float FloorSeen(Map map, int x, int z) => FloorSeenAt(map, x, z, true);

		/// <summary><see cref="FloorSeen"/>; <paramref name="noteIt"/> false reads without marking the cell printed (a proof).</summary>
		private static float FloorSeenAt(Map map, int x, int z, bool noteIt)
		{
			if (!On || map == null)
			{
				return 1f;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			IntVec3 c = new IntVec3(x, 0, z);
			if (eng == null || !c.InBounds(map))
			{
				return 1f;
			}
			int depth = eng.HollowDepthAt(c);
			if (depth <= 0 || Pits.RM_PitCoverUtility.IsCovered(map, c))
			{
				return 1f;
			}
			int note = NoteAt(eng, c);
			if (noteIt)
			{
				eng.submergeDrawn[map.cellIndices.CellToIndex(c)] = note;
			}
			if (note <= 0)
			{
				return 1f;
			}
			float lv = RM_UnderLiquid.NoteLevel(note);
			return RM_UnderLiquid.Seen(ClarityAt(map, eng, c), (lv > depth ? depth : lv) * RM_UnderLiquid.Notch);
		}

		/// <summary>Graphic_Flicker.DrawWorker prefix: a flame whose thing's top is under the line is out (false).</summary>
		internal static bool FlameShows => !rtOn || rtShare < 1f;

		/// <summary>How much of an overlay on <paramref name="t"/> shows (RIMMANDRAKE_SINK_COOLER_ARROW_UNDER_TAR, owner 2026-11-13:
		/// "if we could put the yellow power disconnect icons under the water too when the item is under water that would be
		/// great"): the icon takes its thing's full-depth tint and is hidden half a metre under (RM_UnderLiquid.OverlayAlpha, 0 = not
		/// drawn); 1 for anything not standing wet in a pit.</summary>
		public static float OverlayAlpha(Thing t)
		{
			if (!On || t == null || !t.Spawned || !(t.def.category == ThingCategory.Item || t is Building))
			{
				return 1f;
			}
			float h = StandingMetres(t);
			if (h <= 0f || !Wet(t, out int _, out float levelM, out float clarity, false))
			{
				return 1f;
			}
			return RM_UnderLiquid.OverlayAlpha(clarity, levelM, h);
		}

		/// <summary>The fade of the overlay OverlayDrawer is rendering now (1 = none): set by its Render* methods (outermost
		/// call), applied to every mesh they hand to the draw batch (<see cref="OverlayMaterial"/>). Main thread only.</summary>
		private static float ovFade = 1f;
		private static Color ovBody = Color.white;
		private static int ovDepth;

		internal static void BeginOverlay(Thing t)
		{
			if (ovDepth++ == 0)
			{
				ovFade = OverlayAlpha(t);
				if (ovFade < 1f && t != null && t.Spawned)
				{
					ovBody = BodyColour(LookAt(t.Map, RM_SuperdeepTrap.EngineOf(t.Map), t.Position));
				}
			}
		}

		internal static void EndOverlay()
		{
			if (ovDepth > 0 && --ovDepth == 0)
			{
				ovFade = 1f;
			}
		}

		/// <summary>DrawBatch.DrawMesh prefix: inside an overlay render, the icon's material at its own alpha x the fade. Vanilla's
		/// FadedMaterialPool.FadedVersionOf sets an absolute alpha, so a pulsing icon (already FadedVersionOf(mat, pulse)) is
		/// faded to pulse x fade here, after vanilla's pulse (faded before it, the pulse overwrote the fade).</summary>
		internal static Material OverlayMaterial(Material m)
		{
			if (ovFade >= 1f || m == null)
			{
				return m;
			}
			return FadedMaterialPool.FadedVersionOf(TintedOverlay(m) ?? m, m.color.a * ovFade);
		}

		private static readonly Dictionary<long, Material> tintedOverlays = new Dictionary<long, Material>();

		/// <summary>Round 7: an overlay icon over a drowned thing shifts toward the liquid as its thing does
		/// (RM_UnderLiquid.OverlayTint at the fade's step), not only fades; cached per texture, shader, step and colour.</summary>
		private static Material TintedOverlay(Material m)
		{
			Texture2D tex = m.mainTexture as Texture2D;
			if (tex == null || m.shader == null)
			{
				return null;
			}
			int q = RM_UnderLiquid.Step(ovFade);
			long rgb = ((long)(byte)(ovBody.r * 255f) << 16) | ((long)(byte)(ovBody.g * 255f) << 8) | (byte)(ovBody.b * 255f);
			long key = ((long)tex.GetInstanceID() << 32) ^ ((long)m.shader.GetInstanceID() << 40) ^ ((long)q << 24) ^ rgb;
			if (tintedOverlays.TryGetValue(key, out Material t) && t != null)
			{
				return t;
			}
			RM_UnderLiquid.Float3 k = RM_UnderLiquid.OverlayTint(new RM_UnderLiquid.Float3(ovBody.r, ovBody.g, ovBody.b), (float)q / RM_UnderLiquid.Steps);
			Color c = m.color;
			t = MaterialPool.MatFrom(new MaterialRequest(tex, m.shader, new Color(c.r * k.r, c.g * k.g, c.b * k.b, 1f)) { renderQueue = m.renderQueue });
			tintedOverlays[key] = t;
			return t;
		}

		/// <summary>RIMMANDRAKE_ADD_OVERLAY_PROOF_HOOK_LAW_CANNOT_SEE_ICONS: [proof] "x,z" -> what the liquid law decides for every
		/// drawer of every thing at the cell, read only (nothing printed, noted or drawn): one line per thing,
		/// "def=&lt;defName&gt; id=&lt;thingID&gt; realtime=whole|hidden|bodycover|split share=&lt;0..1&gt; flame=none|shows|out
		/// overlay=&lt;alpha OverlayDrawer is handed; 0 = not drawn&gt;", then "cords=&lt;FloorSeen: how much of a Gimme Some Slack
		/// cord or rope on the floor shows&gt;". flame is the Graphic_Flicker gate (out once the realtime split is whole under);
		/// overlay covers DrawOverlay (hidden at 0) and the pulsing status icons (faded to it). Drawers that route nowhere (a
		/// battery's charge bar, GenDraw lines) are not in it: a live look owns those. Else "REFUSED: ...".</summary>
		public static string ProofOverlays(string arg)
		{
			Map map = Find.CurrentMap;
			string[] p = (arg ?? "").Split(',');
			if (map == null || p.Length < 2 || !int.TryParse(p[0].Trim(), out int x) || !int.TryParse(p[1].Trim(), out int z))
			{
				return "REFUSED: need a current map and \"x,z\"";
			}
			IntVec3 c = new IntVec3(x, 0, z);
			if (!c.InBounds(map))
			{
				return "REFUSED: cell off the map";
			}
			StringBuilder sb = new StringBuilder();
			List<Thing> list = c.GetThingList(map);
			for (int i = 0; i < list.Count; i++)
			{
				Thing t = list[i];
				RealtimeVerdict v = RealtimeRead(t, out float share, out _, out _, out _);
				bool flicker = t.Graphic is Graphic_Flicker || t.def.graphicData?.graphicClass == typeof(Graphic_Flicker)
					|| t.TryGetComp<CompFireOverlay>() != null;
				string flame = !flicker ? "none" : v == RealtimeVerdict.Hidden || (v == RealtimeVerdict.Split && share >= 1f) ? "out" : "shows";
				sb.Append("def=").Append(t.def.defName).Append(" id=").Append(t.thingIDNumber)
					.Append(" realtime=").Append(v.ToString().ToLowerInvariant()).Append(" share=").Append(F(share))
					.Append(" flame=").Append(flame).Append(" overlay=").Append(F(OverlayAlpha(t))).Append('\n');
			}
			sb.Append("cords=").Append(F(FloorSeenAt(map, x, z, false)));
			return sb.ToString();
		}

		private static readonly float[] Uv0 = new float[8];
		private static readonly float[] Uv = new float[8];
		private static readonly Vector2[] UvBuf = new Vector2[4];

		/// <summary>Printer_Plane.PrintPlane prefix while a context is open: true when this drew the plane (split, covered, cut
		/// at the rim, under the sheet or hidden), false = vanilla prints it as asked.
		/// A drowned part is drawn whole in its own material with a cover in the liquid's colour over it (its silhouette, at
		/// RM_UnderLiquid.CoverAlpha of the law's Seen, banded by depth), so it reads lerp(liquid, own, Seen) as the floor beside it does under the sheet; under an opaque liquid only the part above the line is
		/// drawn. A thing lying on the floor (a vent, filth, a plant wholly under) is drawn under the sheet instead.</summary>
		internal static bool Split(MapDrawLayer layer, Vector3 center, Vector2 size, Material mat, float rot, bool flipUv,
			Vector2[] uvs, Color32[] colors, float bias, float payload)
		{
			if (inSplit || mat == null || !(ctxOn || ctxClip || ctxFlat))
			{
				return false;
			}
			inSplit = true;
			try
			{
				if (ctxFlat && ctxVent)
				{
					// round 7 (owner: "the vent looks on top of the water"): a sunk vent is a floor hole only, under the sheet
					Material hole = SunkVentMat();
					if (hole == null)
					{
						return false;
					}
					float vs = RM_GeyserTubMath.SunkVentDrawSize;
					Emit(layer, center, new Vector2(vs, vs), hole, 0f, false, null, colors, bias, payload);
					return true;
				}
				if (ctxFlat)
				{
					Material under = UnderSheetMat(mat);
					if (under == null)
					{
						return false;
					}
					Emit(layer, center, size, under, rot, flipUv, uvs, colors, bias, payload);
					return true;
				}
				float s = 0f, lo = 0f, hi = 0f;
				bool fromLow = true;
				float x0 = center.x - size.x * 0.5f, x1 = center.x + size.x * 0.5f;
				float z0 = center.z - size.y * 0.5f, z1 = center.z + size.y * 0.5f;
				if (ctxOn)
				{
					bool alongZ = ctxFrom == RM_UnderLiquid.FromSouth || ctxFrom == RM_UnderLiquid.FromNorth;
					fromLow = ctxFrom == RM_UnderLiquid.FromSouth || ctxFrom == RM_UnderLiquid.FromWest;
					lo = alongZ ? z0 - ctxCell.z : x0 - ctxCell.x;
					hi = alongZ ? z1 - ctxCell.z : x1 - ctxCell.x;
					s = ctxWorld ? RM_UnderLiquid.SpanShare(lo, hi, ctxCut, fromLow) : ctxShare;
				}
				bool clear = ctxClarity > 0f;
				if (s <= 0f)
				{
					Emit(layer, center, size, mat, rot, flipUv, uvs, colors, bias, payload);   // dry, or cut at the rim only
					return true;
				}
				if (rot != 0f)
				{
					// a turned sprite (an item's random lie): whole above the line until half of it is under, then whole and
					// covered at the law's alpha for its middle (hidden under an opaque liquid)
					if (s < 0.5f || clear)
					{
						Emit(layer, center, size, mat, rot, flipUv, uvs, colors, bias, payload);
					}
					if (s >= 0.5f && clear)
					{
						Material c = CoverMat(mat, ctxWorld ? RM_UnderLiquid.BandAlphaStep(ctxClarity, MetresOf(0.5f, lo, hi, fromLow))
							: RM_UnderLiquid.DrownedStep(ctxClarity, ctxLevel));
						if (c != null)
						{
							Emit(layer, center + new Vector3(0f, CoverEps, 0f), size, c, rot, flipUv, uvs, colors, bias, payload);
						}
					}
					return true;
				}
				if (uvs != null)
				{
					for (int j = 0; j < 4; j++)
					{
						Uv0[j * 2] = uvs[j].x;
						Uv0[j * 2 + 1] = uvs[j].y;
					}
				}
				else
				{
					// Printer_Plane.DefaultUvs / DefaultUvsFlipped, corner order (-x-z, -x+z, +x+z, +x-z)
					float ul = flipUv ? 1f : 0f, ur = flipUv ? 0f : 1f;
					Uv0[0] = ul; Uv0[1] = 0f; Uv0[2] = ul; Uv0[3] = 1f; Uv0[4] = ur; Uv0[5] = 1f; Uv0[6] = ur; Uv0[7] = 0f;
				}
				if (!clear)
				{
					if (s < 1f)
					{
						Piece(layer, center.y, mat, colors, bias, payload, s, 1f, x0, z0, x1, z1, 0f);
					}
					return true;
				}
				Emit(layer, center, size, mat, 0f, flipUv, uvs, colors, bias, payload);
				if (!ctxWorld)
				{
					// standing on the floor: the whole drowned part is seen as the floor under the full depth (round 7)
					Material whole = CoverMat(mat, RM_UnderLiquid.DrownedStep(ctxClarity, ctxLevel));
					if (whole != null)
					{
						Piece(layer, center.y, whole, colors, bias, payload, 0f, s, x0, z0, x1, z1, CoverEps);
					}
					return true;
				}
				int n = RM_UnderLiquid.BandsFor(ctxClarity, MetresOf(s, lo, hi, fromLow), MetresOf(0f, lo, hi, fromLow));
				for (int b = 0; b < n; b++)
				{
					float a = s * b / n, e = s * (b + 1) / n;
					Material c = CoverMat(mat, RM_UnderLiquid.BandAlphaStep(ctxClarity, MetresOf((a + e) * 0.5f, lo, hi, fromLow)));
					if (c != null)
					{
						Piece(layer, center.y, c, colors, bias, payload, a, e, x0, z0, x1, z1, CoverEps);
					}
				}
				return true;
			}
			finally
			{
				inSplit = false;
			}
		}
		/// <summary>Metres of liquid over the point a share <paramref name="share"/> in from the drowned side of a sprite
		/// spanning [lo, hi] (cell-local): standing things by their drawn height, hung ones between the waterline and their
		/// wall's foot.</summary>
		private static float MetresOf(float share, float lo, float hi, bool fromLow)
		{
			if (!ctxWorld)
			{
				float m = ctxLevel - share * ctxHeight;
				return m < 0f ? 0f : m;
			}
			float pos = fromLow ? lo + share * (hi - lo) : hi - share * (hi - lo);
			return RM_UnderLiquid.MetresAt(pos, ctxCut, ctxFoot, 0f, ctxLevel);
		}

		/// <summary>The slice [a, b] (from the drowned side) of the plane spanning x0..x1, z0..z1, lifted <paramref name="lift"/>
		/// over it. Its top bias is the plane's own across the slice (a slice's foot sits where the whole plane's surface is
		/// there), so a cover laid over the whole plane is never under it by depth.</summary>
		private static void Piece(MapDrawLayer layer, float y, Material mat, Color32[] colors, float bias, float payload,
			float a, float b, float x0, float z0, float x1, float z1, float lift)
		{
			float oz0 = z0, hz = z1 - z0;
			System.Array.Copy(Uv0, Uv, 8);
			RM_UnderLiquid.Slice(ctxFrom, a, b, Uv, ref x0, ref z0, ref x1, ref z1);
			if (x1 - x0 <= 0f || z1 - z0 <= 0f || hz <= 0f)
			{
				return;
			}
			for (int j = 0; j < 4; j++)
			{
				UvBuf[j] = new Vector2(Uv[j * 2], Uv[j * 2 + 1]);
			}
			float t0 = (z0 - oz0) / hz, t1 = (z1 - oz0) / hz;
			Emit(layer, new Vector3((x0 + x1) * 0.5f, y + bias * t0 + lift, (z0 + z1) * 0.5f), new Vector2(x1 - x0, z1 - z0),
				mat, 0f, false, UvBuf, colors, bias * (t1 - t0), payload);
		}

		/// <summary>How far a cover lies over the part it covers (world y): over it by depth, under anything printed above.</summary>
		private const float CoverEps = 0.0005f;

		private static readonly float[] clipOut = new float[RM_UnderLiquid.ClipMaxVerts * RM_UnderLiquid.ClipStride];

		private static readonly Vector2[] PlaneUvs = { new Vector2(0f, 0f), new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(1f, 0f) };
		private static readonly Vector2[] PlaneUvsFlipped = { new Vector2(1f, 0f), new Vector2(1f, 1f), new Vector2(0f, 1f), new Vector2(0f, 0f) };

		/// <summary>Prints a plane as Printer_Plane does, cut to the rim clip when one is open (RM_UnderLiquid.ClipQuad): a plane
		/// wholly inside is printed as asked; a cut one is a fan of the kept polygon, its uvs, colours and top bias carried
		/// bilinearly from the plane's corners; a plane wholly outside prints nothing. Cost: one ClipQuad (four corner tests,
		/// and up to four plane passes over at most eight corners) per print, on a section rebuild only.</summary>
		private static void Emit(MapDrawLayer layer, Vector3 center, Vector2 size, Material mat, float rot, bool flipUv,
			Vector2[] uvs, Color32[] colors, float bias, float payload)
		{
			int n = ctxClip ? RM_UnderLiquid.ClipQuad(center.x, center.z, size.x, size.y, rot, ctxRx0, ctxRz0, ctxRx1, ctxRz1, clipOut) : -1;
			if (n < 0)
			{
				Printer_Plane.PrintPlane(layer, center, size, mat, rot, flipUv, uvs, colors, bias, payload);
				return;
			}
			if (n < 3)
			{
				return;
			}
			if (uvs == null)
			{
				uvs = flipUv ? PlaneUvsFlipped : PlaneUvs;
			}
			LayerSubMesh sm = layer.GetSubMesh(mat);
			int b0 = sm.verts.Count;
			const int k = RM_UnderLiquid.ClipStride;
			for (int i = 0; i < n; i++)
			{
				float s = clipOut[i * k + 2], t = clipOut[i * k + 3];
				sm.verts.Add(new Vector3(clipOut[i * k], center.y + t * bias, clipOut[i * k + 1]));
				Vector2 uv = Vector2.Lerp(Vector2.Lerp(uvs[0], uvs[1], t), Vector2.Lerp(uvs[3], uvs[2], t), s);
				sm.uvs.Add(new Vector3(uv.x, uv.y, payload));
				sm.colors.Add(colors == null ? new Color32(255, 255, 255, 255)
					: Color32.Lerp(Color32.Lerp(colors[0], colors[1], t), Color32.Lerp(colors[3], colors[2], t), s));
			}
			for (int i = 1; i + 1 < n; i++)
			{
				sm.tris.Add(b0);
				sm.tris.Add(b0 + i);
				sm.tris.Add(b0 + i + 1);
			}
		}

		private static readonly Dictionary<long, Material> covers = new Dictionary<long, Material>();

		/// <summary>The cover of a drowned part seen at <paramref name="q"/>/Steps: <paramref name="mat"/>'s silhouette (vanilla's
		/// Silhouette shader: one flat colour through the sprite's own alpha; no depth write) in the context's liquid colour at
		/// RM_UnderLiquid.CoverAlpha(q), in the drowned queue. Null when nothing covers it (q = Steps) or it has no texture.
		/// Cached per material, step and colour.</summary>
		private static Material CoverMat(Material mat, int q) => CoverMat(mat, q, ctxCover);

		/// <summary><see cref="CoverMat(Material, int)"/> in the liquid colour <paramref name="col"/>.</summary>
		private static Material CoverMat(Material mat, int q, Color col)
		{
			if (q >= RM_UnderLiquid.Steps || mat == null)
			{
				return null;
			}
			long rgb = ((long)(byte)(col.r * 255f) << 16) | ((long)(byte)(col.g * 255f) << 8) | (byte)(col.b * 255f);
			long key = ((long)mat.GetInstanceID() << 32) | ((long)(q < 0 ? 0 : q) << 24) | rgb;
			if (covers.TryGetValue(key, out Material m) && m != null)
			{
				return m;
			}
			Texture2D tex = mat.mainTexture as Texture2D;
			if (tex == null)
			{
				return null;
			}
			m = MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Silhouette,
				new Color(col.r, col.g, col.b, RM_UnderLiquid.CoverAlpha(q))) { renderQueue = DrownedQueue });
			covers[key] = m;
			return m;
		}

		private static Material sunkVent;

		/// <summary>RM_SunkVent (a soft dark hole, no ring, no splotch) on the transparent shader under the liquid's sheet: what
		/// a vent under liquid prints instead of vanilla's geyser art (round 7). Null when the art is missing.</summary>
		private static Material SunkVentMat()
		{
			if (sunkVent == null)
			{
				Texture2D tex = ContentFinder<Texture2D>.Get("Things/Building/RM_SunkVent", false);
				if (tex == null)
				{
					return null;
				}
				sunkVent = MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent, Color.white) { renderQueue = RM_FaceMaterial.UnderSheetQueue });
			}
			return sunkVent;
		}

		private static readonly Dictionary<int, Material> underSheet = new Dictionary<int, Material>();

		/// <summary><paramref name="mat"/> (its texture and colour) on the transparent shader in the queue under the liquid's sheet
		/// (RM_FaceMaterial.UnderSheetQueue, as the pit floor's shadow): the sheet then hides it by the law as it hides the floor
		/// it lies on. No depth write, so the sheet is never cut by it. Null when it has no texture.</summary>
		private static Material UnderSheetMat(Material mat)
		{
			int id = mat.GetInstanceID();
			if (underSheet.TryGetValue(id, out Material m) && m != null)
			{
				return m;
			}
			Texture2D tex = mat.mainTexture as Texture2D;
			if (tex == null)
			{
				return null;
			}
			m = MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent, mat.color) { renderQueue = RM_FaceMaterial.UnderSheetQueue });
			underSheet[id] = m;
			return m;
		}

		private static int drownedQueue;

		/// <summary>The render queue of a drowned part's cover (RimMandrake.Shared.Slack.DrawOrder.DrownedQueue): above every
		/// ground-level cord, hose and clamp (the part itself is drawn whole in its own Cutout, which hides what lies under it
		/// by depth as the dry thing does; the cover tints what shows of it), and below the overhead spans.</summary>
		private static int DrownedQueue
		{
			get
			{
				if (drownedQueue == 0)
				{
					Shader tr = ShaderDatabase.Transparent;
					drownedQueue = RimMandrake.Shared.Slack.DrawOrder.DrownedQueue(
						RimMandrake.Shared.Slack.DrawOrder.BaseStrandQueue(tr != null ? tr.renderQueue : 0));
				}
				return drownedQueue;
			}
		}

		// ── realtime drawers (gates, stakes) ───────────────────────────────

		private static readonly Dictionary<long, Mesh> sliceMeshes = new Dictionary<long, Mesh>();

		/// <summary>A realtime plane of <paramref name="size"/> keeping only the slice [a, b] measured from its foot (uvs
		/// lerped; unflipped art). Cached per size and slice (1/128 steps), so a frame allocates nothing.</summary>
		public static Mesh SliceMesh(Vector2 size, float a, float b, bool flip = false)
		{
			int ia = Mathf.RoundToInt(RM_UnderLiquid.Clamp01(a) * 128f), ib = Mathf.RoundToInt(RM_UnderLiquid.Clamp01(b) * 128f);
			if (ib <= ia)
			{
				return null;
			}
			long key = ((long)Mathf.RoundToInt(size.x * 1000f) << 40) | ((long)Mathf.RoundToInt(size.y * 1000f) << 17) | ((long)ia << 9)
				| ((long)ib << 1) | (flip ? 1L : 0L);
			if (sliceMeshes.TryGetValue(key, out Mesh m) && m != null)
			{
				return m;
			}
			float sa = ia / 128f, sb = ib / 128f, hw = size.x * 0.5f, hh = size.y * 0.5f;
			float za = -hh + size.y * sa, zb = -hh + size.y * sb;
			m = new Mesh { name = "RM_SubmergeSlice" };
			m.vertices = new[] { new Vector3(-hw, 0f, za), new Vector3(-hw, 0f, zb), new Vector3(hw, 0f, zb), new Vector3(hw, 0f, za) };
			float u0 = flip ? 1f : 0f, u1 = flip ? 0f : 1f;
			m.uv = new[] { new Vector2(u0, sa), new Vector2(u0, sb), new Vector2(u1, sb), new Vector2(u1, sa) };
			m.triangles = new[] { 0, 1, 2, 0, 2, 3 };
			m.RecalculateNormals();
			m.RecalculateBounds();
			sliceMeshes[key] = m;
			return m;
		}

		/// <summary>A realtime upright sprite (<paramref name="whole"/>, <paramref name="size"/>) whose foot lies
		/// <paramref name="footMetres"/> under the liquid and which spans <paramref name="heightMetres"/> up from there
		/// (<paramref name="flip"/>: the art is mirrored, as on a flipped plane). Under a clear liquid it is drawn whole and its
		/// drowned part covered in bands by its silhouette in the liquid's colour (<paramref name="thing"/>'s cell's; fresh
		/// water's when null) at RM_UnderLiquid.CoverAlpha, so it reads lerp(liquid, own, Seen) as a print does (Split); under
		/// an opaque liquid only the part above the line is drawn. Returns the share drawn under.</summary>
		public static float DrawUnder(Mesh whole, Vector2 size, Matrix4x4 at, Material mat, float footMetres, float heightMetres, float clarity,
			bool flip = false, Thing thing = null)
		{
			float s = RM_UnderLiquid.Share(footMetres, 0f, heightMetres);
			if (s <= 0f)
			{
				UnityEngine.Graphics.DrawMesh(whole, at, mat, 0);
				return 0f;
			}
			if (!(clarity > 0f))
			{
				Mesh kept = s < 1f ? SliceMesh(size, s, 1f, flip) : null;
				if (kept != null)
				{
					UnityEngine.Graphics.DrawMesh(kept, at, mat, 0);
				}
				return s;
			}
			UnityEngine.Graphics.DrawMesh(whole, at, mat, 0);
			Color col = thing != null && thing.Spawned ? CoverColour(LookAt(thing.Map, RM_SuperdeepTrap.EngineOf(thing.Map), thing.Position), clarity)
				: BodyColour(null);
			Matrix4x4 over = at * Matrix4x4.Translate(new Vector3(0f, CoverEps, 0f));
			// the whole drowned part is seen as the floor under the full depth (round 7)
			Material m = CoverMat(mat, RM_UnderLiquid.DrownedStep(clarity, footMetres), col);
			Mesh band = m != null ? SliceMesh(size, 0f, s, flip) : null;
			if (band != null)
			{
				UnityEngine.Graphics.DrawMesh(band, over, m, 0);
			}
			return s;
		}

		/// <summary>Scene helper for pit_fittings_matrix.py: "x,z,w,h,waterM[,FluidDefName]" writes waterM metres of water on every
		/// dug square of the rect through the engine's own driver write (TrySetDriverWaterDlOutcome; default fluid = the map's).
		/// -> "FILL applied=N refused=N notOwned=N fluid=..." or "REFUSED: ...".</summary>
		public static string ProofFillRect(string arg)
		{
			Map map = Find.CurrentMap;
			string[] p = (arg ?? "").Split(',');
			RM_MapComponent_Excavation eng = map?.GetComponent<RM_MapComponent_Excavation>();
			if (eng == null || p.Length < 5 || !int.TryParse(p[0].Trim(), out int x) || !int.TryParse(p[1].Trim(), out int z)
				|| !int.TryParse(p[2].Trim(), out int w) || !int.TryParse(p[3].Trim(), out int h) || !double.TryParse(p[4].Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out double waterM)
				|| w < 1 || h < 1 || w * h > 400)
			{
				return "REFUSED: need a current map with FlowWorks and \"x,z,w,h,waterM[,FluidDefName]\" (w*h <= 400)";
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
				switch (eng.TrySetDriverWaterDlOutcome(c, (long)System.Math.Round(waterM / RM_LevelSolve.MetresPerUnit), fluid))
				{
					case RM_MapComponent_Excavation.DriverFillOutcome.Applied: applied++; break;
					case RM_MapComponent_Excavation.DriverFillOutcome.Refused: refused++; break;
					default: notOwned++; break;
				}
			}
			return "FILL applied=" + applied + " refused=" + refused + " notOwned=" + notOwned + " fluid=" + (fluid?.defName ?? "default");
		}

		private static string F(float v, string fmt = "F3") => v < 0f ? "-" : v.ToString(fmt, CultureInfo.InvariantCulture);

		/// <summary>The waterline the wall layer draws on the face a ladder hangs on, computed the way
		/// SectionLayer_RMExcavationWalls does (Exposed at the true level; N: 1 - NorthFace, E: 1 - SideFace, W: SideFace):
		/// the proof's independent reference for the ladder's cut. -1 when no face shows liquid.</summary>
		private static float FaceWaterline(Thing t, RM_MapComponent_Excavation eng, int d, float lv)
		{
			int rot = t.Rotation.AsInt;
			if (rot == 2 || lv <= 0f)
			{
				return RM_UnderLiquid.NoCut;
			}
			int nb = SectionLayer_RMExcavationWalls.NeighbourLevel(t.Map, eng, t.Position + t.Rotation.FacingCell, d);
			if (d - nb <= 0)
			{
				return RM_UnderLiquid.NoCut;   // hangs on no wall: no face to meet
			}
			if (rot == 0)
			{
				return 1f - RM_UnderLiquid.NorthFaceAt(d, nb, lv);
			}
			float w = RM_UnderLiquid.SideFaceAt(d, nb, lv);
			return rot == 1 ? 1f - w : w;
		}

		/// <summary>
		/// Proof read for wall_art_scene.py's "submerge" and pit_fittings_matrix.py's rows: the first thing at "x,z" this
		/// draws, and what the one rule decides for it.
		/// "def=RM_Ladder class=RM_Building_Ladder kind=hung rot=0 depth=4 fill=3 level=3.25 flat=no cutZ=0.880 faceZ=0.880
		/// share=0.760 clarity=0.450 seenLine=0.756 seenFoot=0.120 printedLevel=3.25 setting=on liquid=WaterDeep tint=0.24,0.24,0.24"
		/// (fill = whole notches; level = the true level, quarter notches, what everything is drawn at; cutZ = the cell-local
		/// waterline the ladder is cut at, faceZ = the one the wall layer draws on its face, "-" for none: they must agree;
		/// share = of the sprite under the line, from its foot (a hung ladder: of its in-pit span, wall foot to rim); clarity
		/// = the liquid's; seenLine / seenFoot = how much of the drowned part is seen just under the line and at its foot (0
		/// opaque); printedLevel = the level the cell was last printed at, "-" for the realtime gates and stakes or when not
		/// printed since the last change; tint = the liquid look's tint).
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
			int d = eng.HollowDepthAt(c);
			string f = RM_LevelSolve.Metres(eng.WaterDlAt(c)).ToString("F4", CultureInfo.InvariantCulture);
			float lv = RM_UnderLiquid.NoteLevel(NoteAt(eng, c));
			if (lv > d)
			{
				lv = d;
			}
			float levelM = lv * RM_UnderLiquid.Notch;
			RM_LiquidSurfaceLook look = lv > 0f ? LookAt(map, eng, c) : null;
			float clarity = look != null ? look.seeThrough : 0f;
			List<Thing> list = c.GetThingList(map);
			for (int i = 0; i < list.Count; i++)
			{
				Thing t = list[i];
				float share, lineM, footM, heightM;
				string kind, faces = "";
				if (t is RM_Building_Ladder && !LiesFlat(t, t.Graphic))
				{
					kind = "hung";
					int drop = d > 0 ? LadderDrop(t, eng, d) : 0;
					float cut = d <= 0 ? RM_UnderLiquid.NoCut : RM_UnderLiquid.Waterline(t.Rotation.AsInt, drop, lv);
					int r = t.Rotation.AsInt;
					// of its in-pit span, wall foot to rim, along its face (N: z up to 1; E: x up to 1; W: x down to 0)
					float side = RM_UnderLiquid.SideFace(drop);
					share = cut < 0f ? 0f : r == 0 ? RM_UnderLiquid.SpanShare(1f - RM_UnderLiquid.NorthFace(drop), 1f, cut, true)
						: r == 1 ? RM_UnderLiquid.SpanShare(1f - side, 1f, cut, true) : RM_UnderLiquid.SpanShare(0f, side, cut, false);
					lineM = 0f;
					footM = share > 0f ? levelM : 0f;
					heightM = drop * RM_UnderLiquid.Notch;
					faces = " flat=no cutZ=" + F(cut) + " faceZ=" + F(d <= 0 ? RM_UnderLiquid.NoCut : FaceWaterline(t, eng, d, lv));
				}
				else if (t is RM_Building_Ladder)
				{
					kind = "flat";
					heightM = RM_UnderLiquid.LyingLadderMetres;
					faces = " flat=yes cutZ=- faceZ=-";
					share = d <= 0 ? 0f : RM_UnderLiquid.Share(levelM, 0f, heightM);
					lineM = levelM - share * heightM; footM = levelM;
				}
				else if (t is RM_Building_PitRamp)
				{
					kind = "ramp";
					heightM = d <= 0 ? 0f : RampRise(t, eng, d) * RM_UnderLiquid.Notch;
					share = d <= 0 ? 0f : RM_UnderLiquid.Share(levelM, 0f, heightM);
					lineM = levelM - share * heightM; footM = levelM;
				}
				else if (t is Building_RM_Spikes)
				{
					kind = "stakes";
					heightM = RM_UnderLiquid.StakeMetres;
					share = d <= 0 ? 0f : RM_UnderLiquid.Share(levelM, 0f, heightM);
					lineM = levelM - share * heightM; footM = levelM;
				}
				else if (t is Building_RM_FlowDoor)
				{
					kind = "gate";
					heightM = RM_UnderLiquid.GateMetres(d);
					share = d <= 0 || !RM_UnderLiquid.GateShowsLiquid(t.Rotation.AsInt) || ((Building_RM_FlowDoor)t).FaceDry() ? 0f
						: RM_UnderLiquid.Share(levelM, 0f, heightM);
					lineM = levelM - share * heightM; footM = levelM;
				}
				else if (t is Pawn || t is Corpse)
				{
					Pawn pw = t as Pawn ?? ((Corpse)t).InnerPawn;
					kind = t is Corpse ? "corpse" : pw.Swimming ? "swimmer" : "pawn";
					heightM = pw == null ? RM_UnderLiquid.CorpseMetres : PawnMetres(pw, t is Corpse);
					share = d <= 0 || pw.Swimming ? 0f : RM_UnderLiquid.Share(levelM, 0f, heightM);
					lineM = levelM - share * heightM; footM = levelM;
				}
				else if ((heightM = StandingMetres(t)) > 0f)
				{
					kind = IsSwale(t.def) ? "swale" : t is Building ? "building" : t is MinifiedThing ? "minified" : "item";
					share = d <= 0 ? 0f : RM_UnderLiquid.Share(levelM, 0f, heightM);
					lineM = levelM - share * heightM; footM = levelM;
				}
				else
				{
					continue;
				}
				if (lineM < 0f)
				{
					lineM = 0f;
				}
				bool wet = share > 0f;
				float seenLine = wet ? RM_UnderLiquid.Seen(clarity, lineM <= 0f ? 0.0001f : lineM) : 1f;
				float seenFoot = wet ? RM_UnderLiquid.Seen(clarity, footM) : 1f;
				bool realtime = t is Building_RM_Spikes || t is Building_RM_FlowDoor || t is Pawn || t is Corpse;
				string printed = realtime || !eng.submergeDrawn.TryGetValue(map.cellIndices.CellToIndex(c), out int pn)
					? "-" : RM_UnderLiquid.NoteLevel(pn).ToString("F2", CultureInfo.InvariantCulture);
				Color tint = look != null ? look.tint : Color.white;
				return "def=" + t.def.defName + " class=" + t.GetType().Name + " kind=" + kind + " rot=" + t.Rotation.AsInt
					+ " depth=" + d + " waterM=" + f + " level=" + lv.ToString("F2", CultureInfo.InvariantCulture) + faces
					+ " share=" + F(share) + " clarity=" + F(clarity) + " seenLine=" + F(seenLine) + " seenFoot=" + F(seenFoot)
					+ " printedLevel=" + printed + " setting=" + (On ? "on" : "off")
					+ " height=" + F(heightM, "F2") + " shadow=" + (kind == "building" && d > 0 ? F(RM_UnderLiquid.ThingShadow(clarity, levelM)) : "-")
					+ " label=" + F(wet ? RM_UnderLiquid.LabelAlpha(clarity, levelM, heightM) : 1f)
					+ " liquid=" + (map.terrainGrid.TerrainAt(c)?.defName ?? "-")
					+ " tint=" + F(tint.r, "F2") + "," + F(tint.g, "F2") + "," + F(tint.b, "F2");
			}
			return "REFUSED: nothing drawn under liquid at " + x + "," + z + " (depth=" + d + " waterM=" + f + ")";
		}
	}

	/// <summary>Opens the under-liquid split for each thing the general things layer prints (RM_SubmergeDraw.Begin).</summary>
	[HarmonyPatch(typeof(SectionLayer_ThingsGeneral), "TakePrintFrom")]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergeTakePrint
	{
		[HarmonyPrefix]
		private static void Prefix(Thing t)
		{
			RM_SubmergeDraw.Begin(t);
		}

		[HarmonyFinalizer]
		private static void Finalizer(SectionLayer_ThingsGeneral __instance)
		{
			try
			{
				RM_SubmergeDraw.FloorShadow(__instance);
			}
			finally
			{
				RM_SubmergeDraw.End();
			}
		}
	}

	/// <summary>No vanilla contact shadow from a building standing in a pit (RM_SubmergeDraw.FloorShadow draws its one
	/// shadow on the floor). The ShadowData overload calls this one.</summary>
	[HarmonyPatch(typeof(Printer_Shadow), nameof(Printer_Shadow.PrintShadow), new[] { typeof(SectionLayer), typeof(Vector3), typeof(Vector3), typeof(Rot4) })]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (shadows)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergeContactShadow
	{
		[HarmonyPrefix]
		private static bool Prefix()
		{
			return !RM_SubmergeDraw.InPit;
		}
	}

	/// <summary>Every edifice read in SectionLayer_SunShadows.Regenerate goes through RM_SubmergeDraw.ShadowCaster: a building
	/// standing in a pit casts no sun shadow onto the liquid's surface or the bank.</summary>
	[HarmonyPatch]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (sun shadows)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergeSunShadows
	{
		// the layer is internal to Verse: reached by name
		private static System.Reflection.MethodBase TargetMethod()
		{
			return AccessTools.Method(AccessTools.TypeByName("Verse.SectionLayer_SunShadows"), "Regenerate");
		}

		[HarmonyTranspiler]
		private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> code)
		{
			System.Reflection.MethodInfo caster = AccessTools.Method(typeof(RM_SubmergeDraw), nameof(RM_SubmergeDraw.ShadowCaster));
			int n = 0;
			foreach (CodeInstruction ins in code)
			{
				yield return ins;
				if (ins.opcode == OpCodes.Ldelem_Ref)
				{
					n++;
					yield return new CodeInstruction(OpCodes.Call, caster);
				}
			}
			if (n != 4)
			{
				Log.Warning("[FlowWorks] SectionLayer_SunShadows.Regenerate read the edifice grid " + n + " times, expected 4: pit things may cast sun shadows");
			}
		}
	}

	/// <summary>A label or stack count over a thing standing wet in a pit fades with the thing (RM_SubmergeDraw.LabelAlpha),
	/// and is not drawn once the thing is hidden.</summary>
	[HarmonyPatch(typeof(GenMapUI), nameof(GenMapUI.DrawThingLabel), new[] { typeof(Thing), typeof(string), typeof(Color) })]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (labels)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergeLabel
	{
		[HarmonyPrefix]
		private static bool Prefix(Thing thing, ref Color textColor)
		{
			float a = RM_SubmergeDraw.LabelAlpha(thing);
			if (a <= 0f)
			{
				return false;
			}
			textColor.a *= a;
			return true;
		}
	}

	/// <summary>RIMMANDRAKE_DRAW_PAWN_OWN_PICTURE_CUT_AT_LIQUID_SURFACE_NOT_ICON: a pawn or corpse standing, lying or dead in a
	/// wet pit is drawn as her own picture cut at the liquid's surface (RM_SubmergeDraw.BeginPawnCut): the cut opens for the
	/// render tree's draw and closes after it.</summary>
	[HarmonyPatch(typeof(PawnRenderTree), nameof(PawnRenderTree.Draw))]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (pawns)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergePawnCut
	{
		[HarmonyPrefix]
		private static void Prefix(PawnRenderTree __instance, PawnDrawParms parms)
		{
			RM_SubmergeDraw.BeginPawnCut(__instance, parms);
		}

		[HarmonyFinalizer]
		private static void Finalizer()
		{
			RM_SubmergeDraw.EndPawnCut();
		}
	}

	/// <summary>Marks a wet pawn before vanilla picks its far-zoom atlas or its render tree (RM_SubmergeDraw.NoteWet).</summary>
	[HarmonyPatch(typeof(PawnRenderer), nameof(PawnRenderer.RenderPawnAt))]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (pawn wet mark)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergePawnWet
	{
		private static readonly AccessTools.FieldRef<PawnRenderer, Pawn> PawnOf = AccessTools.FieldRefAccess<PawnRenderer, Pawn>("pawn");

		[HarmonyPrefix]
		private static void Prefix(PawnRenderer __instance)
		{
			RM_SubmergeDraw.NoteWet(PawnOf(__instance));
		}
	}

	/// <summary>Every node a pawn's render tree draws passes here; inside an open cut it is drawn cut at the line or tinted
	/// (RM_SubmergeDraw.DrawCutNode).</summary>
	[HarmonyPatch(typeof(GenDraw), nameof(GenDraw.DrawMeshNowOrLater), new[] { typeof(Mesh), typeof(Matrix4x4), typeof(Material), typeof(bool), typeof(MaterialPropertyBlock) })]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (pawn nodes)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergePawnNode
	{
		[HarmonyPrefix]
		private static bool Prefix(Mesh mesh, Matrix4x4 matrix, Material mat, bool drawNow, MaterialPropertyBlock properties)
		{
			return !RM_SubmergeDraw.DrawCutNode(mesh, matrix, mat, drawNow, properties);
		}
	}

	/// <summary>Wound and other overlay decals on a pawn (PawnOverlayDrawer.DoDrawCall) draw by Graphics.DrawMesh, outside
	/// GenDraw: that one call is sent through the cut (RM_SubmergeDraw.DrawOverlayMesh), so a wound under tar is not drawn.</summary>
	[HarmonyPatch(typeof(PawnOverlayDrawer), "DoDrawCall")]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (pawn overlays)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergePawnOverlay
	{
		[HarmonyTranspiler]
		private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> code)
		{
			System.Reflection.MethodInfo draw = AccessTools.Method(typeof(UnityEngine.Graphics), nameof(UnityEngine.Graphics.DrawMesh),
				new[] { typeof(Mesh), typeof(Matrix4x4), typeof(Material), typeof(int), typeof(Camera), typeof(int), typeof(MaterialPropertyBlock) });
			System.Reflection.MethodInfo cut = AccessTools.Method(typeof(RM_SubmergeDraw), nameof(RM_SubmergeDraw.DrawOverlayMesh));
			int n = 0;
			foreach (CodeInstruction ins in code)
			{
				if ((ins.opcode == OpCodes.Call || ins.opcode == OpCodes.Callvirt) && ins.operand as System.Reflection.MethodInfo == draw)
				{
					n++;
					yield return new CodeInstruction(OpCodes.Call, cut) { labels = ins.labels, blocks = ins.blocks };
					continue;
				}
				yield return ins;
			}
			if (n != 1)
			{
				Log.Warning("[FlowWorks] PawnOverlayDrawer.DoDrawCall drew " + n + " Graphics.DrawMesh calls, expected 1: wound overlays may not be cut in liquid");
			}
		}
	}

	/// <summary>Vanilla draws a humanlike at far zoom from one cached atlas quad, with no render tree to cut: a pawn that was
	/// wet on her last draw is drawn from her tree instead (RM_SubmergeDraw.NoCachedFrame).</summary>
	[HarmonyPatch(typeof(PawnRenderer), "ParallelGetPreRenderResults")]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (pawn cache)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergePawnNoCache
	{
		private static readonly AccessTools.FieldRef<PawnRenderer, Pawn> PawnOf = AccessTools.FieldRefAccess<PawnRenderer, Pawn>("pawn");

		[HarmonyPrefix]
		private static void Prefix(PawnRenderer __instance, ref bool disableCache)
		{
			if (!disableCache && RM_SubmergeDraw.On && RM_SubmergeDraw.NoCachedFrame(PawnOf(__instance)))
			{
				disableCache = true;
			}
		}
	}

	/// <summary>Draws each plane of a thing in an open split as its part above the line plus its drowned bands.</summary>
	[HarmonyPatch(typeof(Printer_Plane), nameof(Printer_Plane.PrintPlane))]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (planes)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergePrintPlane
	{
		[HarmonyPrefix]
		private static bool Prefix(MapDrawLayer layer, Vector3 center, Vector2 size, Material mat, float rot, bool flipUv,
			Vector2[] uvs, Color32[] colors, float topVerticesAltitudeBias, float uvzPayload)
		{
			return !RM_SubmergeDraw.Split(layer, center, size, mat, rot, flipUv, uvs, colors, topVerticesAltitudeBias, uvzPayload);
		}
	}

	/// <summary>The realtime layer: every per-frame thing draw passes here (RM_SubmergeDraw.BeginRealtime).</summary>
	[HarmonyPatch(typeof(Thing), nameof(Thing.DynamicDrawPhase))]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (realtime things)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergeRealtime
	{
		[HarmonyPrefix]
		private static bool Prefix(Thing __instance, DrawPhase phase)
		{
			return RM_SubmergeDraw.BeginRealtime(__instance, phase);
		}

		[HarmonyFinalizer]
		private static void Finalizer()
		{
			RM_SubmergeDraw.EndRealtime();
		}
	}

	/// <summary>Inside the realtime split, a Graphic's mesh is drawn cut and faded (RM_SubmergeDraw.DrawRealtime). The base
	/// method is the one every Graphic whose DrawWorker is vanilla's draws through (Single, Multi, StackCount, Random, ...).</summary>
	[HarmonyPatch(typeof(Graphic), "DrawMeshInt")]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (realtime things)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergeRealtimeMesh
	{
		[HarmonyPrefix]
		private static bool Prefix(Mesh mesh, Vector3 loc, Quaternion quat, Material mat)
		{
			return RM_SubmergeDraw.DrawRealtime(mesh, loc, quat, mat);
		}
	}

	/// <summary>A flame (torch, campfire, brazier, darklight: every Graphic_Flicker) on a thing whose top is under the line is
	/// out.</summary>
	[HarmonyPatch(typeof(Graphic_Flicker), nameof(Graphic_Flicker.DrawWorker))]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (flames)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergeFlame
	{
		[HarmonyPrefix]
		private static bool Prefix()
		{
			return RM_SubmergeDraw.FlameShows;
		}
	}

	/// <summary>Every overlay OverlayDrawer draws on a thing (power off, needs power, broken down, out of fuel, forbidden,
	/// question mark, ...) is not drawn once its thing's top is hidden under the liquid.</summary>
	[HarmonyPatch(typeof(OverlayDrawer), nameof(OverlayDrawer.DrawOverlay))]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (overlays)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergeOverlay
	{
		[HarmonyPrefix]
		private static bool Prefix(Thing t)
		{
			return RM_SubmergeDraw.OverlayAlpha(t) > 0f;
		}
	}

	/// <summary>Every OverlayDrawer.Render* method that draws an icon on a thing (needs power, power off, broken down,
	/// recharging, out of fuel, the pulsing helpers, forbidden, forbidden big, forbidden refuel, forbidden atomizer, burning
	/// wick, question mark): its icon is faded with the thing (RM_SubmergeDraw.OverlayAlpha). All of them are patched, not
	/// only the pulsing internal one, because the forbidden and wick icons go to the draw batch directly; the outermost call
	/// sets the fade.</summary>
	[HarmonyPatch]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (overlays)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergeOverlayRender
	{
		private static System.Collections.Generic.IEnumerable<System.Reflection.MethodBase> TargetMethods()
		{
			foreach (System.Reflection.MethodInfo m in AccessTools.GetDeclaredMethods(typeof(OverlayDrawer)))
			{
				System.Reflection.ParameterInfo[] ps = m.GetParameters();
				if (m.Name.StartsWith("Render") && !m.IsStatic && ps.Length > 0 && ps[0].ParameterType == typeof(Thing))
				{
					yield return m;
				}
			}
		}

		[HarmonyPrefix]
		private static void Prefix(Thing __0)
		{
			RM_SubmergeDraw.BeginOverlay(__0);
		}

		[HarmonyFinalizer]
		private static void Finalizer()
		{
			RM_SubmergeDraw.EndOverlay();
		}
	}

	/// <summary>DrawBatch.DrawMesh (both overloads): inside an overlay render, the icon's material is faded with its thing
	/// (RM_SubmergeDraw.OverlayMaterial). Outside one: one comparison.</summary>
	[HarmonyPatch]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (overlays)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergeOverlayBatch
	{
		private static System.Collections.Generic.IEnumerable<System.Reflection.MethodBase> TargetMethods()
		{
			foreach (System.Reflection.MethodInfo m in AccessTools.GetDeclaredMethods(typeof(DrawBatch)))
			{
				System.Reflection.ParameterInfo[] ps = m.GetParameters();
				if (m.Name == nameof(DrawBatch.DrawMesh) && ps.Length > 2 && ps[2].ParameterType == typeof(Material))
				{
					yield return m;
				}
			}
		}

		[HarmonyPrefix]
		private static void Prefix(ref Material material)
		{
			material = RM_SubmergeDraw.OverlayMaterial(material);
		}
	}
}
