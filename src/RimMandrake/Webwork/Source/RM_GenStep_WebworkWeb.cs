using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Webwork
{
	/// <summary>
	/// WEBWORK_TERRAIN_WEATHER_PASS_1. Lays a Webwork map's web at map generation (GenStepDef RM_WebworkWebScatter, order 326).
	/// Owner, 2026-10-12: "it should still look like a jungle with web shit through it. Thick powerful cables running through
	/// are the main portions with thinner local webs and the finer carpet where the spiders have "sites" they use."
	///
	///   sites    the nest (RM_Webwork_NestWall, placed at 324) plus two or three more, spaced and inside a margin
	///            (RM_WebNetKernel.PlanSites).
	///   carpet   RM_Webwork_SilkCarpet within 4-6 cells of each site, a rough rim one further (siteCarpetEnabled).
	///   cables   RM_Webwork_Cable along a spanning tree of the sites plus two through-cables edge to edge, each a sagging
	///            8-connected line; a cell holding rock, a building, an item or water is skipped (the cable passes over it).
	///   strands  RM_Webwork_Strand, the local web, within three cells of a cable or site cell (localWebDensityMultiplier).
	///
	/// Gated on the biome (RM_Webwork only) and on webNetworkEnabled. The layout is the kernel's; this class only asks the
	/// map what a cell holds and spawns. PlaceWeb is public so RM_WebworkProof can run it on a quicktest map.
	/// </summary>
	public class RM_GenStep_WebworkWeb : GenStep
	{
		public const string CableDefName = "RM_Webwork_Cable";
		public const string StrandDefName = "RM_Webwork_Strand";
		public const string CarpetDefName = "RM_Webwork_SilkCarpet";

		public override int SeedPart => 611024977;

		public sealed class Result
		{
			public bool placed;
			public string why = "";
			public List<IntVec3> sites = new List<IntVec3>();
			public List<int> carpetRadii = new List<int>();
			public List<IntVec3> carpetCells = new List<IntVec3>();
			public int cables, strands;

			public override string ToString()
			{
				return placed
					? "placed True | sites " + sites.Count + " | carpet " + carpetCells.Count + " | cables " + cables + " | strands " + strands
					: "placed False | " + why;
			}
		}

		public override void Generate(Map map, GenStepParams parms)
		{
			if (map.Biome == null || map.Biome.defName != RM_GenStep_WebworkNest.WebworkBiomeDefName)
			{
				return;
			}
			Result r = PlaceWeb(map);
			if (r.placed)
			{
				Log.Message("[RM Webwork] RM_GenStep_WebworkWeb: " + r + " on " + map.Biome.defName + ".");
			}
		}

		public Result PlaceWeb(Map map)
		{
			var r = new Result();
			if (!RM_WebworkSettings.webNetworkEnabled)
			{
				r.why = "webNetworkEnabled off";
				return r; // map-generation-affecting master toggle
			}
			ThingDef cableDef = DefDatabase<ThingDef>.GetNamedSilentFail(CableDefName);
			ThingDef strandDef = DefDatabase<ThingDef>.GetNamedSilentFail(StrandDefName);
			TerrainDef carpetDef = DefDatabase<TerrainDef>.GetNamedSilentFail(CarpetDefName);
			if (cableDef == null || strandDef == null || carpetDef == null)
			{
				r.why = "defs missing";
				Log.Warning("[RM Webwork] RM_GenStep_WebworkWeb: " + CableDefName + "/" + StrandDefName + "/" + CarpetDefName
					+ " not found; web skipped.");
				return r;
			}

			var rng = new Random(Rand.Int);
			int w = map.Size.x, h = map.Size.z;

			(int x, int z)? nest = null;
			ThingDef wallDef = DefDatabase<ThingDef>.GetNamedSilentFail(RM_GenStep_WebworkNest.NestWallDefName);
			if (wallDef != null)
			{
				foreach (Thing t in map.listerThings.ThingsOfDef(wallDef))
				{
					nest = (t.Position.x, t.Position.z);
					break;
				}
			}
			int extra = rng.Next(RM_WebNetKernel.ExtraSitesMin, RM_WebNetKernel.ExtraSitesMax + 1);
			List<(int x, int z)> sites = RM_WebNetKernel.PlanSites(nest, w, h, extra, rng,
				(x, z) => new IntVec3(x, 0, z).Standable(map));
			foreach (var s in sites)
			{
				r.sites.Add(new IntVec3(s.x, 0, s.z));
			}

			// carpet at each site
			foreach (IntVec3 site in r.sites)
			{
				int radius = RM_WebNetKernel.CarpetRadius(rng);
				r.carpetRadii.Add(radius);
				if (!RM_WebworkSettings.siteCarpetEnabled)
				{
					continue;
				}
				foreach (IntVec3 c in GenRadial.RadialCellsAround(site, radius + 1.5f, true))
				{
					if (!c.InBounds(map) || !RM_WebNetKernel.CarpetAt(c.x - site.x, c.z - site.z, radius, c.GetHashCode()))
					{
						continue;
					}
					TerrainDef t = c.GetTerrain(map);
					if (t == null || !t.natural || t.IsWater || t.passability == Traversability.Impassable || c.GetEdifice(map) != null
						|| t == carpetDef)
					{
						continue;
					}
					map.terrainGrid.SetTerrain(c, carpetDef);
					r.carpetCells.Add(c);
				}
			}

			// cables
			var segments = new List<((int x, int z) a, (int x, int z) b)>();
			foreach (var e in RM_WebNetKernel.SpanningEdges(sites))
			{
				segments.Add((sites[e.a], sites[e.b]));
			}
			segments.AddRange(RM_WebNetKernel.ThroughSegments(sites, w, h, RM_WebNetKernel.ThroughCables, rng));
			var cableCells = new List<IntVec3>();
			foreach (var seg in segments)
			{
				int len = (int)Math.Sqrt(RM_WebNetKernel.Dist2(seg.a.x, seg.a.z, seg.b.x, seg.b.z));
				float sag = RM_WebNetKernel.Sag(len, rng.NextDouble(), rng.Next(2) == 0);
				foreach (var p in RM_WebNetKernel.Raster(seg.a.x, seg.a.z, seg.b.x, seg.b.z, sag))
				{
					var c = new IntVec3(p.x, 0, p.z);
					if (CanHold(map, c, cableDef, strandDef))
					{
						GenSpawn.Spawn(ThingMaker.MakeThing(cableDef), c, map);
						cableCells.Add(c);
						r.cables++;
					}
				}
			}

			// local webs near cables and sites
			var anchors = new List<IntVec3>(cableCells);
			anchors.AddRange(r.sites);
			int budget = RM_WebNetKernel.StrandBudget(w, h, RM_WebworkSettings.localWebDensityMultiplier);
			for (int i = 0; i < budget * 4 && r.strands < budget && anchors.Count > 0; i++)
			{
				IntVec3 a = anchors[rng.Next(anchors.Count)];
				var off = RM_WebNetKernel.StrandOffset(rng);
				var c = new IntVec3(a.x + off.dx, 0, a.z + off.dz);
				if (CanHold(map, c, cableDef, strandDef))
				{
					GenSpawn.Spawn(ThingMaker.MakeThing(strandDef), c, map);
					r.strands++;
				}
			}

			r.placed = true;
			return r;
		}

		/// <summary>A cell a cable or strand may be laid in: in bounds, standable ground (no rock, no deep water), no building, item
		/// or pawn there already (nothing is wiped), and no web of ours yet.</summary>
		private static bool CanHold(Map map, IntVec3 c, ThingDef cableDef, ThingDef strandDef)
		{
			if (!c.InBounds(map) || !c.Standable(map))
			{
				return false;
			}
			TerrainDef t = c.GetTerrain(map);
			if (t == null || t.IsWater)
			{
				return false;
			}
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				Thing th = things[i];
				if (th.def == cableDef || th.def == strandDef || th.def.category == ThingCategory.Building
					|| th.def.category == ThingCategory.Item || th.def.category == ThingCategory.Pawn)
				{
					return false;
				}
			}
			return true;
		}
	}
}
