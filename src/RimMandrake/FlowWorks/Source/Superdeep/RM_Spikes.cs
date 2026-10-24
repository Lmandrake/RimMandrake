using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// CANAL_BOTTOM_SPIKES_1 — spikes are per-cell hardware on a pit floor, the same
	/// shape as the ladder (a Thing in the cell, a placeworker, a one-line cell query). Owner Q2,
	/// 2026-10-02 (by card): spikes only in the deepest pits; restated relative by owner R7 (2026-10-17, by card;
	/// form V4): any square with a sheer drop of 2 m or more to a neighbour.
	///
	/// They fire on DESCENT into the cell only (RM_SuperdeepTrap.PitDescent, raised after the
	/// fall): never on walking up to the lip, never on moving between two D = 4 cells. Spikes key
	/// on the descent, not on being held, so a creature too wide for its pit still takes them on
	/// the way in (owner Q4 interplay). A flying pawn does not land on them.
	/// </summary>
	public static class RM_SpikeUtility
	{
		public static bool HasSpikes(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return false;
			}
			ThingDef spikes = RimMandrakeFlowWorks_DefOf.RM_Spikes;
			if (spikes == null)
			{
				return false;
			}
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i].def == spikes)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>The setting "Spikes need a sheer drop of N m", in notches (2 m shipped).</summary>
		public static int MinDropNotches => RM_RelativeRulesMath.Notches(RimMandrakeFlowWorksSettings.spikeMinDropMetres, 1);

		/// <summary>The tallest wall over a dug square: how many notches its highest neighbour stands above it (climb depths;
		/// out of bounds skipped).</summary>
		public static int TallestWallOver(RM_MapComponent_Excavation engine, IntVec3 c)
		{
			Map map = engine.map;
			return RM_RelativeRulesMath.TallestWallOver((x, z) =>
			{
				IntVec3 n = new IntVec3(x, 0, z);
				return n.InBounds(map) ? engine.ClimbDepthAt(n) : -1;
			}, c.x, c.z);
		}

		/// <summary>PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE (owner R7, V4): spikes stand on a DUG square with a sheer drop of
		/// MinDropNotches (2 m) or more to a neighbour, at any absolute depth (was "D = 4 only", the deepest pit of 2026-10-02).
		/// Null = accepted, otherwise the refusal reason.</summary>
		public static string PlacementRefusal(RM_MapComponent_Excavation engine, IntVec3 c)
		{
			int need = MinDropNotches;
			if (engine == null || !engine.IsExcavated(c))
			{
				return "RMFlow_SpikesNeedDrop".Translate(RM_Volume.FormatMetres(0), RM_Volume.FormatMetres(need));
			}
			int wall = TallestWallOver(engine, c);
			return wall >= need ? null : (string)"RMFlow_SpikesNeedDrop".Translate(RM_Volume.FormatMetres(wall), RM_Volume.FormatMetres(need));
		}

		/// <summary>Lands the spike hits on a pawn that just dropped into <paramref name="cell"/>.
		/// Returns the number of hits landed (0 when the cell is unspiked, the setting is off, or
		/// the pawn is flying).</summary>
		public static int ApplyDescent(Pawn p, IntVec3 cell)
		{
			if (p == null || p.Dead || !p.Spawned || !RimMandrakeFlowWorksSettings.spikesEnabled
				|| p.Flying || !HasSpikes(p.Map, cell))
			{
				return 0;
			}
			float perHit = RM_PitTrapMath.SpikeDamagePerHit(p.BodySize, RimMandrakeFlowWorksSettings.spikeDamageMultiplier);
			int landed = 0;
			for (int i = 0; i < RM_PitTrapMath.SpikeHits; i++)
			{
				if (p.Dead || p.Destroyed)
				{
					break;
				}
				p.TakeDamage(new DamageInfo(DamageDefOf.Stab, perHit));
				landed++;
			}
			return landed;
		}

		/// <summary>Bridge proof (jawa/static_call): would RM_Spikes be accepted on this cell?
		/// "ACCEPT depth N" or "REFUSE depth N: reason".</summary>
		public static string ProofPlacement(Map map, IntVec3 cell)
		{
			RM_MapComponent_Excavation engine = map?.GetComponent<RM_MapComponent_Excavation>();
			int depth = engine != null && engine.IsExcavated(cell) ? engine.ExcavatedDepthAt(cell) : 0;
			int wall = engine != null && engine.IsExcavated(cell) ? TallestWallOver(engine, cell) : 0;
			string why = PlacementRefusal(engine, cell);
			return (why == null ? "ACCEPT depth " : "REFUSE depth ") + depth + " drop " + wall + (why == null ? "" : ": " + why);
		}

		/// <summary>Bridge proof (jawa/static_call): the descent hook, fired directly on the pawn
		/// standing on <paramref name="cell"/> (the pit's descent detector is the live route; this
		/// isolates the spike half). Returns "HITS n | INJURIES Stab k" for the first pawn there.</summary>
		public static string ProofDescent(Map map, IntVec3 cell)
		{
			if (map == null)
			{
				return "REFUSED: no map";
			}
			foreach (Thing t in cell.GetThingList(map))
			{
				if (t is Pawn p)
				{
					int hits = ApplyDescent(p, cell);
					int stabs = 0;
					foreach (Hediff h in p.health.hediffSet.hediffs)
					{
						if (h is Hediff_Injury && h.def == DamageDefOf.Stab.hediff)
						{
							stabs++;
						}
					}
					return "HITS " + hits + " | INJURIES Stab " + stabs + " | bodySize " + p.BodySize.ToString("0.##");
				}
			}
			return "REFUSED: no pawn at " + cell;
		}
	}

	[StaticConstructorOnStartup]
	public static class RM_SpikesHook
	{
		static RM_SpikesHook()
		{
			RM_SuperdeepTrap.PitDescent += (p, cell) => RM_SpikeUtility.ApplyDescent(p, cell);
		}
	}

	/// <summary>Spikes belong at the foot of a sheer drop (owner R7, V4: 2 m or more to a neighbour, at any depth): refused on
	/// open ground and on gentle slopes, with the drop in the reason.</summary>
	public class PlaceWorker_SpikesOnSuperdeep : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot,
			Map map, Thing thingToIgnore = null, Thing thing = null)
		{
			if (map == null)
			{
				return false;
			}
			string why = RM_SpikeUtility.PlacementRefusal(map.GetComponent<RM_MapComponent_Excavation>(), loc);
			return why == null ? AcceptanceReport.WasAccepted : new AcceptanceReport(why);
		}
	}

	/// <summary>PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE: the spikes drawn as the variant's own stakes laid on the floor the pit's
	/// walls leave visible (RM_SpikeDrawMath.FloorRect / Layout), never over the far-wall face, the side bevels or the
	/// outline, and fading out under water (SubmergedAlpha: gone at 1 m). drawerType RealtimeOnly (the fill changes without
	/// a map-mesh rebuild). The variant is the one Graphic_Random already picks for this thing, so saves keep their look;
	/// an unknown texture falls back to the plain sprite.</summary>
	public class Building_RM_Spikes : Building
	{
		private const int AlphaSteps = 32;
		private Mesh mesh;
		private int meshKey = -1;
		private int variant = -2;
		private Texture2D tex;
		private static readonly List<float> Quads = new List<float>();

		protected override void DrawAt(Vector3 drawLoc, bool flip = false)
		{
			RM_MapComponent_Excavation eng = Map?.GetComponent<RM_MapComponent_Excavation>();
			if (variant == -2)
			{
				Graphic g = Graphic is Graphic_Random r ? r.SubGraphicFor(this) : null;
				tex = g?.MatSingle?.mainTexture as Texture2D;
				variant = tex != null ? RM_SpikeDrawMath.VariantOf(tex.name) : -1;
			}
			IntVec3 c = Position;
			int d = eng != null ? eng.HollowDepthAt(c) : 0;
			if (variant < 0 || d <= 0)
			{
				base.DrawAt(drawLoc, flip);
				return;
			}
			float alpha = RM_SpikeDrawMath.SubmergedAlpha(eng.FillAt(c));
			int a = Mathf.RoundToInt(alpha * AlphaSteps);
			if (a <= 0)
			{
				return;
			}
			Map map = Map;
			int north = SectionLayer_RMExcavationWalls.NeighbourLevel(map, eng, c + IntVec3.North, d);
			int south = SectionLayer_RMExcavationWalls.NeighbourLevel(map, eng, c + IntVec3.South, d);
			int west = SectionLayer_RMExcavationWalls.NeighbourLevel(map, eng, c + IntVec3.West, d);
			int east = SectionLayer_RMExcavationWalls.NeighbourLevel(map, eng, c + IntVec3.East, d);
			bool faces = RimMandrakeFlowWorksSettings.excavationWallFacesEnabled, outline = RimMandrakeFlowWorksSettings.pitOutlineEnabled;
			int key = Key(d) | Key(d - north) << 4 | Key(d - south) << 8 | Key(d - west) << 12 | Key(d - east) << 16
				| (faces ? 1 << 20 : 0) | (outline ? 1 << 21 : 0);
			if (mesh == null || key != meshKey)
			{
				Rebuild(d, north, south, west, east, faces, outline);
				meshKey = key;
			}
			if (mesh == null)
			{
				return;
			}
			Material mat = MaterialPool.MatFrom(tex, ShaderDatabase.Transparent, new Color(1f, 1f, 1f, (float)a / AlphaSteps));
			Graphics.DrawMesh(mesh, new Vector3(c.x, drawLoc.y, c.z), Quaternion.identity, mat, 0);
		}

		/// <summary>A drop as a 4-bit key field (negative = a neighbour deeper than us: no wall, same as 0).</summary>
		private static int Key(int v) => v <= 0 ? 0 : (v > 15 ? 15 : v);

		private void Rebuild(int d, int north, int south, int west, int east, bool faces, bool outline)
		{
			RM_SpikeDrawMath.FloorRect(d, north, south, west, east, faces, outline, out float x0, out float z0, out float x1, out float z1);
			int n = RM_SpikeDrawMath.Layout(variant, thingIDNumber, x0, z0, x1, z1, Quads);
			if (mesh != null)
			{
				UnityEngine.Object.Destroy(mesh);
				mesh = null;
			}
			if (n == 0)
			{
				return;
			}
			var verts = new List<Vector3>(n * 4);
			var uv = new List<Vector2>(n * 4);
			var tris = new int[n * 6];
			for (int i = 0; i < n; i++)
			{
				int o = i * RM_SpikeDrawMath.Out;
				float x = Quads[o], z = Quads[o + 1], w = Quads[o + 2], h = Quads[o + 3];
				float u0 = Quads[o + 4], v0 = Quads[o + 5], u1 = Quads[o + 6], v1 = Quads[o + 7];
				int q = i * 4;
				// one mesh draws its triangles in order, so Layout's far-first sort puts nearer stakes on top
				verts.Add(new Vector3(x, 0f, z));
				verts.Add(new Vector3(x, 0f, z + h));
				verts.Add(new Vector3(x + w, 0f, z + h));
				verts.Add(new Vector3(x + w, 0f, z));
				uv.Add(new Vector2(u0, v0));
				uv.Add(new Vector2(u0, v1));
				uv.Add(new Vector2(u1, v1));
				uv.Add(new Vector2(u1, v0));
				int t = i * 6;
				tris[t] = q; tris[t + 1] = q + 1; tris[t + 2] = q + 2;
				tris[t + 3] = q; tris[t + 4] = q + 2; tris[t + 5] = q + 3;
			}
			mesh = new Mesh { name = "RM_Spikes_stakes" };
			mesh.SetVertices(verts);
			mesh.SetUVs(0, uv);
			mesh.triangles = tris;
			mesh.RecalculateBounds();
		}

		public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
		{
			if (mesh != null)
			{
				UnityEngine.Object.Destroy(mesh);
				mesh = null;
			}
			base.DeSpawn(mode);
		}
	}
}
