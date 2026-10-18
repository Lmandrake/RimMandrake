using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP (plan P11, owner R10 + R11, 2026-10-17). Owner, R11, verbatim: <i>"Vary it. Some
	/// lakes will be shallow and silted up. Others will be deep and chasm-like. Depends on the biome. The more mountainous, the
	/// deeper in general. The more plains-like, the smoother/shallower. They should also have some variation down there, not
	/// just a radial crater."</i> Replaces §9.4's radial slope (0.5 m every 4 squares) and its fixed 10/20/50 m numbers.
	///
	/// One natural lake's floor, in notches (0.5 m), recorded once when the lake is formed (at map creation, or once on the
	/// first load of an older save) and never re-rolled: <see cref="Floor"/> is a pure function of the footprint, which squares
	/// hold deep water, the map's seed, the lake's key (its lowest square index, so the order lakes are found in never matters)
	/// and the map's roughness. Verse-free, so Source/SelfTest/ compiles this production file and the preview tool runs it.
	///
	/// <list type="number">
	/// <item>Roughness r in [0, 1]: the world tile's hilliness (as the map generator used it) plus a per-biome bias (our biomes
	/// carry their design character: canyons and craters deeper, swamps, sumps and plains shallower).</item>
	/// <item>A depth band by r (<see cref="Bands"/>, PROVISIONAL, his to approve): the per-lake range of the deepest floor, a
	/// cap, the chance a lake is silted up, how steep its walls are, and how rough its floor is. 50 m sits only in the
	/// mountain and chasm bands.</item>
	/// <item>Per lake, seeded: a draw inside the range (some lakes shallow, some deep), silted or not, the floor's grain
	/// direction, terraces, a silt-flat bottom.</item>
	/// <item>Per square: a bowl by distance from shore whose wall width follows r (plains a saucer, mountains a sheer-sided
	/// chasm), times multi-scale value noise, plus ridged trenches and a few holes, so the floor is never a radial crater.</item>
	/// <item>The shore shelf (Mod Setting, default OFF): the outermost ring of the lake may be a shallow beach. Owner card
	/// 2026-10-18 (BEACH_RING_RETIRE_DRAINED_MEANS_DRY): no ring by default, "drained means dry".</item>
	/// <item>The way out: every floor square keeps a walked route to dry land whose every N/S/E/W step is no bigger than
	/// <see cref="Params.wayOutNotches"/> (default 1 m, what a person climbs), so a drained lake never holds a person
	/// (owner ruling 4, 2026-10-12: <i>"no chance to fall in and get stuck"</i>). Chasm walls stay sheer everywhere except along
	/// one scree ramp grown from the lowest saddle. 0 = off: true chasms that can strand what falls in.</item>
	/// <item>One basin: a hole with no downhill route to the deep water is silted up to its sill, so a drawn-down lake never
	/// splits into pools the level solver would treat as one (a pond is one node, one surface).</item>
	/// </list>
	/// Water terrain is never written here: a full lake keeps its vanilla look (R10); only the books know its floor.
	/// </summary>
	public static class RM_LakeFloorMath
	{
		/// <summary>Shallow-water squares keep today's 1 m floor (ruling 2026-10-12); deep water starts at 2 m.</summary>
		public const int ShallowNotches = 2;
		public const int DeepNotches = 4;

		/// <summary>Mod Setting defaults (PROVISIONAL, veto list in Transient/fw_scenes/p11_build_log.md).</summary>
		public const float DefaultDepthScale = 1f;
		public const float DefaultRoughnessScale = 1f;
		public const int DefaultShelfNotches = 0;      // no beach ring: owner 2026-10-18, drained means dry
		public const int DefaultWayOutNotches = 2;     // 1 m: the person band climbs it (RM_PitTrapMath.ClimbLimit K 2)
		public const int DefaultCeilingNotches = 100;  // 50 m: only the mountain and chasm bands reach it

		/// <summary>Everything the generator reads besides the lake itself.</summary>
		public struct Params
		{
			public int seed;               // the map's (world persistent value x map's constant seed)
			public float roughness;        // 0 plains .. 1 chasm country (Roughness)
			public float depthScale;       // Mod Setting "lakeDepthScale": multiplies the band's range and cap
			public float roughnessScale;   // Mod Setting "lakeFloorRoughness": multiplies the floor's noise, trenches, holes
			public int ceilingNotches;     // Mod Setting "deepBedMaxDepth": no floor deeper (≤ 250 = 125 m)
			public int shelfNotches;       // Mod Setting "lakeShoreShelf": the outer ring's floor (0 = off: 1 m / 2 m as before)
			public int wayOutNotches;      // Mod Setting "lakeWayOut": the biggest step on the guaranteed route out (0 = off)

			public static Params Defaults(int seed, float roughness)
			{
				return new Params
				{
					seed = seed,
					roughness = roughness,
					depthScale = DefaultDepthScale,
					roughnessScale = DefaultRoughnessScale,
					ceilingNotches = DefaultCeilingNotches,
					shelfNotches = DefaultShelfNotches,
					wayOutNotches = DefaultWayOutNotches,
				};
			}
		}

		/// <summary>One row of the roughness table (PROVISIONAL tuning, shown to the owner with the floor-variety look).</summary>
		public struct Band
		{
			public string name;
			public float r;              // the anchor roughness (the hilliness bases below)
			public float lowM, highM;    // the deepest floor of a non-silted lake is drawn in [lowM, highM] (skewed shallow); a
			                             // highM past capM makes the cap a depth some lakes really reach (chasm: about 1 in 8)
			public float capM;           // never deeper in this band (before the depth scale; the ceiling setting caps after)
			public float siltChance;     // the chance a lake is silted up: deepest 2 to 2.5 m, a flat floor
			public float siltFlatChance; // the chance a non-silted lake has a flat silt bottom (its deep part levelled)
			public float wallWidth;      // fraction of the lake's inradius over which the floor falls to its full depth
			public float noiseAmp;       // how much of the depth the floor's grain can take away (0..1)
			public float trench;         // ridged trenches' extra depth (fraction of full)
			public float terraceChance;  // chance of 2 to 4 shelves (terraces) in the floor
		}

		public static readonly Band[] Bands =
		{
			new Band { name = "plains",     r = 0.05f, lowM = 2.0f, highM = 5f,  capM = 8f,  siltChance = 0.45f, siltFlatChance = 0.55f, wallWidth = 0.85f, noiseAmp = 0.30f, trench = 0.05f, terraceChance = 0.10f },
			new Band { name = "low hills",  r = 0.30f, lowM = 3.0f, highM = 10f, capM = 15f, siltChance = 0.30f, siltFlatChance = 0.40f, wallWidth = 0.60f, noiseAmp = 0.40f, trench = 0.12f, terraceChance = 0.25f },
			new Band { name = "hills",      r = 0.55f, lowM = 5.0f, highM = 20f, capM = 30f, siltChance = 0.15f, siltFlatChance = 0.25f, wallWidth = 0.40f, noiseAmp = 0.45f, trench = 0.20f, terraceChance = 0.40f },
			new Band { name = "mountains",  r = 0.80f, lowM = 8.0f, highM = 35f, capM = 50f, siltChance = 0.08f, siltFlatChance = 0.15f, wallWidth = 0.22f, noiseAmp = 0.50f, trench = 0.30f, terraceChance = 0.50f },
			new Band { name = "chasm",      r = 0.95f, lowM = 12f,  highM = 56f, capM = 50f, siltChance = 0.05f, siltFlatChance = 0.10f, wallWidth = 0.14f, noiseAmp = 0.50f, trench = 0.35f, terraceChance = 0.50f },
		};

		/// <summary>Roughness of a world tile's hilliness (RimWorld.Planet.Hilliness as a byte: 0 Undefined, 1 Flat, 2 SmallHills,
		/// 3 LargeHills, 4 Mountainous, 5 Impassable). The band anchors sit on these.</summary>
		public static float HillinessRoughness(int hilliness)
		{
			switch (hilliness)
			{
				case 1: return 0.05f;
				case 2: return 0.30f;
				case 3: return 0.55f;
				case 4: return 0.80f;
				case 5: return 0.95f;
				default: return 0.30f;
			}
		}

		/// <summary>Per-biome bias on roughness (PROVISIONAL; from each biome's own description). Unlisted biomes: 0. Our biomes
		/// are listed in both tiers (RM_ the mod's own, RUT_ the Utinni twin).</summary>
		public static readonly Dictionary<string, float> BiomeBias = new Dictionary<string, float>
		{
			// deeper: canyons, craters, ridges, voids, mountains
			{ "RM_Abyss", 0.25f }, { "RUT_Abyss", 0.25f },                   // obsidian twisted into shapes no wind carved
			{ "RM_FloodedCanyon", 0.20f }, { "RUT_CrackedLands", 0.20f },    // mesas, hoodoos, slot canyons
			{ "RM_TheScald", 0.25f }, { "RUT_TheScald", 0.25f },             // a perched ocean in a vast crater
			{ "RM_TheForge", 0.20f }, { "RUT_TheForge", 0.20f },             // one mountain
			{ "RM_Contagion", 0.15f }, { "RUT_Contagion", 0.15f },           // a valley on a scalded mountain
			{ "RM_WeepingStones", 0.15f }, { "RUT_WeepingStones", 0.15f },   // high stone, ridge and shoulder
			{ "RM_LanternDeeps", 0.20f },                                     // voids under the thickest crust
			{ "RM_ChillCrater", 0.10f },                                      // a basin of black glass
			{ "RM_NightsideIce", 0.10f }, { "RUT_NightsideIce", 0.10f },     // ice that flows and fractures
			{ "RM_Warscar", 0.10f }, { "RUT_Scarlands", 0.10f },             // crater fields
			// shallower: swamps, sumps, plains, pans, mud
			{ "RM_TheSump", -0.25f }, { "RUT_Sump", -0.25f },                // flat black pools, the lowest basin
			{ "RM_FeverWood", -0.25f }, { "RUT_FeverWood", -0.25f },         // shallow surface pools, deep mud beneath
			{ "RM_Miasma", -0.20f }, { "RUT_Miasma", -0.20f },               // brackish channels
			{ "RM_Wasteland", -0.20f }, { "RUT_Wasteland", -0.20f },         // salt and brine where rivers die
			{ "RM_Stillsand", -0.20f }, { "RUT_ExtremeDesert", -0.20f },     // a corrugated plain to every horizon
			{ "RM_LeaningScrub", -0.20f }, { "RUT_AridShrubland", -0.20f },  // fuzz to every horizon
			{ "RM_Greentide", -0.15f }, { "RUT_Greentide", -0.15f },         // mud deep enough to swallow a boot
			{ "RM_Pyrelands", -0.15f },                                       // savanna
			{ "RM_RustCathedral", -0.15f }, { "RUT_RustCathedral", -0.15f }, // a flat plateau of deck plate
			{ "RM_GreySea", -0.10f }, { "RUT_GreySea", -0.10f },             // a shrinking terminal sea
			{ "RM_TwilightSea", -0.10f }, { "RUT_TwilightSea", -0.10f },
			{ "RM_BlueDesert", -0.10f }, { "RUT_BlueDesert", -0.10f },       // an ice plateau
			{ "RM_Cauldron", -0.10f }, { "RUT_Cauldron", -0.10f },           // a low wet forest
			// vanilla and DLC
			{ "TemperateSwamp", -0.20f }, { "TropicalSwamp", -0.20f }, { "ColdBog", -0.20f },
			{ "Grasslands", -0.15f }, { "GlacialPlain", -0.10f },
		};

		public static float Roughness(int hilliness, string biomeDefName)
		{
			float r = HillinessRoughness(hilliness);
			if (biomeDefName != null && BiomeBias.TryGetValue(biomeDefName, out float b))
			{
				r += b;
			}
			return Clamp01(r);
		}

		/// <summary>The band at roughness r, interpolated linearly between the anchors (the name is the nearest anchor's).</summary>
		public static Band BandAt(float r)
		{
			r = Clamp01(r);
			if (r <= Bands[0].r)
			{
				return Bands[0];
			}
			for (int i = 1; i < Bands.Length; i++)
			{
				if (r <= Bands[i].r)
				{
					Band a = Bands[i - 1], b = Bands[i];
					float t = (r - a.r) / (b.r - a.r);
					return new Band
					{
						name = t < 0.5f ? a.name : b.name,
						r = r,
						lowM = Lerp(a.lowM, b.lowM, t),
						highM = Lerp(a.highM, b.highM, t),
						capM = Lerp(a.capM, b.capM, t),
						siltChance = Lerp(a.siltChance, b.siltChance, t),
						siltFlatChance = Lerp(a.siltFlatChance, b.siltFlatChance, t),
						wallWidth = Lerp(a.wallWidth, b.wallWidth, t),
						noiseAmp = Lerp(a.noiseAmp, b.noiseAmp, t),
						trench = Lerp(a.trench, b.trench, t),
						terraceChance = Lerp(a.terraceChance, b.terraceChance, t),
					};
				}
			}
			return Bands[Bands.Length - 1];
		}

		/// <summary>What the per-lake draw decided (for the readout, the log line and the preview's captions).</summary>
		public struct Traits
		{
			public string band;
			public float roughness;
			public float targetDeepestM;   // the draw, before the shelf, the way out and quantising
			public bool silted;
			public float siltCap;          // 1 = no silt flat
			public int terraces;           // 0 = none
			public float grainAngle;       // radians
			public int inradius;           // squares from the shore to the deepest-inland square
			public int deepestNotches;     // the floor as recorded
			public long sumNotches;
			public int wayOutRaised;       // squares the way-out pass moved
			public int basinFilled;        // squares the one-basin pass raised to their sill
			public int shelfSquares;
		}

		/// <summary>The lake's key: its lowest square index. Independent of which square the lake was first touched at.</summary>
		public static int LakeKey(IList<int> footprint)
		{
			int k = int.MaxValue;
			for (int i = 0; i < footprint.Count; i++)
			{
				if (footprint[i] < k)
				{
					k = footprint[i];
				}
			}
			return footprint.Count == 0 ? 0 : k;
		}

		/// <summary>The floor of every footprint square in notches, into <paramref name="outNotches"/> (parallel to
		/// <paramref name="footprint"/>, cell index z × width + x). <paramref name="deep"/>: the square holds deep water today.
		/// Squares outside the footprint (and out of the map) are shore.</summary>
		public static Traits Floor(int width, int height, IList<int> footprint, Func<int, bool> deep, Params p, int[] outNotches)
		{
			var tr = new Traits();
			int n = footprint.Count;
			if (n == 0)
			{
				return tr;
			}
			// Work in the footprint's bounding box grown by one (so its shore ring is inside the box).
			int x0 = int.MaxValue, z0 = int.MaxValue, x1 = int.MinValue, z1 = int.MinValue;
			for (int k = 0; k < n; k++)
			{
				int x = footprint[k] % width, z = footprint[k] / width;
				if (x < x0) x0 = x;
				if (z < z0) z0 = z;
				if (x > x1) x1 = x;
				if (z > z1) z1 = z;
			}
			x0 -= 1; z0 -= 1; x1 += 1; z1 += 1;
			int bw = x1 - x0 + 1, bh = z1 - z0 + 1;
			int[] slot = new int[bw * bh];          // footprint position + 1; 0 = shore
			bool[] isDeep = new bool[n];
			for (int k = 0; k < n; k++)
			{
				int x = footprint[k] % width, z = footprint[k] / width;
				slot[(z - z0) * bw + (x - x0)] = k + 1;
				isDeep[k] = deep(footprint[k]);
			}
			// 4-way squares to the shore: 1 = touches land (or the map edge).
			int[] dist = new int[n];
			var q = new Queue<int>();
			for (int k = 0; k < n; k++)
			{
				int x = footprint[k] % width, z = footprint[k] / width;
				bool shore = x == 0 || z == 0 || x == width - 1 || z == height - 1;
				for (int d = 0; d < 4 && !shore; d++)
				{
					shore = slot[(z - z0 + DZ[d]) * bw + (x - x0 + DX[d])] == 0;
				}
				if (shore)
				{
					dist[k] = 1;
					q.Enqueue(k);
				}
			}
			int R = 1;
			while (q.Count > 0)
			{
				int k = q.Dequeue();
				int x = footprint[k] % width, z = footprint[k] / width;
				for (int d = 0; d < 4; d++)
				{
					int s = slot[(z - z0 + DZ[d]) * bw + (x - x0 + DX[d])];
					if (s != 0 && dist[s - 1] == 0)
					{
						dist[s - 1] = dist[k] + 1;
						if (dist[s - 1] > R) R = dist[s - 1];
						q.Enqueue(s - 1);
					}
				}
			}
			tr.inradius = R;

			// ── the per-lake draw ──
			float rough = Clamp01(p.roughness);
			Band band = BandAt(rough);
			uint key = (uint)LakeKey(footprint);
			uint seed = (uint)p.seed;
			float rs = p.roughnessScale > 0f ? p.roughnessScale : 0f;
			float scale = p.depthScale > 0f ? p.depthScale : 1f;
			tr.band = band.name;
			tr.roughness = rough;
			tr.silted = U01(seed, key, 1, 0) < band.siltChance;
			double u = U01(seed, key, 2, 0);
			double deepest = tr.silted
				? 2.0 + 0.5 * U01(seed, key, 3, 0)
				: band.lowM + (band.highM - band.lowM) * u * Math.Sqrt(u);   // u^1.5: most lakes nearer the low end
			// A small pond cannot hold a mountain lake's depth: full depth from an inradius of 7 squares.
			double sizeFactor = Math.Min(1.0, 0.35 + R / 10.0);
			deepest = 2.0 + (deepest - 2.0) * sizeFactor * scale;
			double capM = band.capM * scale;
			int ceiling = Math.Max(1, Math.Min(p.ceilingNotches > 0 ? p.ceilingNotches : DefaultCeilingNotches, RM_BedMath.MaxStorableDepth));
			deepest = Math.Min(deepest, Math.Min(capM, ceiling * 0.5));
			if (deepest < 2.0) deepest = 2.0;
			tr.targetDeepestM = (float)deepest;
			tr.siltCap = !tr.silted && U01(seed, key, 4, 0) < band.siltFlatChance ? (float)(0.55 + 0.3 * U01(seed, key, 5, 0)) : 1f;
			tr.terraces = U01(seed, key, 6, 0) < band.terraceChance ? 2 + (int)(U01(seed, key, 7, 0) * 3) : 0;
			double angle = U01(seed, key, 8, 0) * Math.PI * 2;
			tr.grainAngle = (float)angle;
			double stretch = 1.0 + 1.5 * rough;              // the grain runs along one axis: rifts in mountains
			double ca = Math.Cos(angle), sa = Math.Sin(angle);
			double lambda = Math.Max(5.0, Math.Min(48.0, R * 0.9));
			double amp = Math.Min(0.9, band.noiseAmp * rs);
			double trench = band.trench * rs;
			double holes = (tr.silted ? 0.25 : 0.35) * rs;
			double wall = Math.Max(0.05, band.wallWidth);
			uint nk = Mix(seed, key);

			// ── the shape, per deep square (s in [0, 1] after normalising) ──
			double[] shape = new double[n];
			double sMax = 0;
			for (int k = 0; k < n; k++)
			{
				if (!isDeep[k])
				{
					continue;
				}
				int x = footprint[k] % width, z = footprint[k] / width;
				double t = dist[k] / (double)R;
				double a = Math.Min(1.0, t / wall);
				double bowl = 1.0 - (1.0 - a) * (1.0 - a);
				double gu = (x * ca + z * sa) / stretch, gv = -x * sa + z * ca;
				double grain = Fbm(nk, gu / lambda, gv / lambda);                      // ~[-1, 1]
				double s = bowl * (1.0 - amp * (0.5 - 0.5 * grain));
				double ridge = 1.0 - Math.Abs(Fbm(nk + 7919u, gu / (lambda * 0.8), gv / (lambda * 0.8)));
				double r6 = ridge * ridge * ridge; r6 *= r6;
				s += trench * r6 * Math.Min(1.0, 2.0 * a);
				if (tr.terraces > 0)
				{
					s = Terrace(s, tr.terraces + 1);
				}
				if (tr.siltCap < 1f || tr.silted)
				{
					double cap = tr.silted ? 0.35 : tr.siltCap;
					s = Math.Min(s, cap) / cap;
				}
				double hole = Value(nk + 104729u, gu / 4.0, gv / 4.0);                 // [0, 1] small-scale
				if (hole > 0.82)
				{
					s += holes * (hole - 0.82) / 0.18 * a;
				}
				shape[k] = s;
				if (s > sMax) sMax = s;
			}
			int[] f = outNotches;
			for (int k = 0; k < n; k++)
			{
				if (!isDeep[k])
				{
					f[k] = ShallowNotches;
					continue;
				}
				double s = sMax > 0 ? shape[k] / sMax : 0.0;
				double m = 2.0 + (deepest - 2.0) * s;
				int notches = (int)Math.Round(m * 2.0, MidpointRounding.AwayFromZero);
				f[k] = Math.Max(DeepNotches, Math.Min(notches, ceiling));
			}
			// ── the shore shelf ──
			if (p.shelfNotches > 0)
			{
				for (int k = 0; k < n; k++)
				{
					if (dist[k] == 1 && f[k] > p.shelfNotches)
					{
						f[k] = p.shelfNotches;
						tr.shelfSquares++;
					}
				}
			}
			for (int k = 0; k < n; k++)
			{
				f[k] = Math.Max(1, Math.Min(f[k], ceiling));
			}
			// ── one basin, then the way out (each only moves a floor shallower, so the pair settles; a few rounds at most) ──
			for (int round = 0; round < 8; round++)
			{
				int moved = SingleBasin(width, height, footprint, f);
				int stairs = p.wayOutNotches > 0 ? WayOut(width, height, footprint, f, p.wayOutNotches) : 0;
				tr.basinFilled += moved;
				tr.wayOutRaised += stairs;
				if (stairs == 0)
				{
					break;
				}
			}
			long sum = 0;
			int max = 0;
			for (int k = 0; k < n; k++)
			{
				sum += f[k];
				if (f[k] > max) max = f[k];
			}
			tr.sumNotches = sum;
			tr.deepestNotches = max;
			return tr;
		}

		/// <summary>The way-out pass, in place: afterwards every footprint square has a route of N/S/E/W steps to a square
		/// outside the footprint (dry land at 0) on which no step is bigger than <paramref name="step"/> notches. A flood from the
		/// land takes every step within the limit; when it stalls, the smallest over-limit step anywhere on its frontier is
		/// closed by moving that one square to within the limit of the floor it is reached from (a stair), and the flood goes on.
		/// So walls stay sheer except along the ramp grown from the lowest saddle. Deterministic (ties by square index). Returns
		/// how many squares moved.</summary>
		public static int WayOut(int width, int height, IList<int> footprint, int[] f, int step)
		{
			int n = footprint.Count;
			if (n == 0 || step <= 0)
			{
				return 0;
			}
			var slotOf = new Dictionary<int, int>(n);
			for (int k = 0; k < n; k++)
			{
				slotOf[footprint[k]] = k;
			}
			bool[] seen = new bool[n];
			var q = new Queue<int>();          // footprint slots reached, to expand
			var frontier = new SortedSet<(int over, int cell, int from)>();
			int moved = 0, done = 0;
			// Seeds: every lake square beside land (or the map edge, which a lake on a sealed edge treats as its shore).
			for (int k = 0; k < n; k++)
			{
				int c = footprint[k], x = c % width, z = c / width;
				for (int d = 0; d < 4; d++)
				{
					int X = x + DX[d], Z = z + DZ[d];
					bool land = X < 0 || Z < 0 || X >= width || Z >= height || !slotOf.ContainsKey(Z * width + X);
					if (!land)
					{
						continue;
					}
					if (f[k] <= step)
					{
						if (!seen[k]) { seen[k] = true; done++; q.Enqueue(k); }
					}
					else
					{
						frontier.Add((f[k] - step, c, 0));
					}
				}
			}
			while (done < n)
			{
				while (q.Count > 0)
				{
					int k = q.Dequeue();
					int c = footprint[k], x = c % width, z = c / width;
					for (int d = 0; d < 4; d++)
					{
						int X = x + DX[d], Z = z + DZ[d];
						if (X < 0 || Z < 0 || X >= width || Z >= height || !slotOf.TryGetValue(Z * width + X, out int m) || seen[m])
						{
							continue;
						}
						int gap = Math.Abs(f[m] - f[k]);
						if (gap <= step)
						{
							seen[m] = true;
							done++;
							q.Enqueue(m);
						}
						else
						{
							frontier.Add((gap - step, footprint[m], f[k]));
						}
					}
				}
				if (done >= n)
				{
					break;
				}
				// stalled: close the smallest over-limit step on the frontier
				bool advanced = false;
				while (frontier.Count > 0)
				{
					var e = frontier.Min;
					frontier.Remove(e);
					int m = slotOf[e.cell];
					if (seen[m])
					{
						continue;
					}
					f[m] = f[m] > e.from ? e.from + step : Math.Max(1, e.from - step);
					seen[m] = true;
					done++;
					moved++;
					q.Enqueue(m);
					advanced = true;
					break;
				}
				if (!advanced)
				{
					break;   // unreachable: every unseen square sits behind a frontier entry
				}
			}
			return moved;
		}

		/// <summary>One basin, in place: afterwards every footprint square has a route of N/S/E/W steps to the lake's deepest
		/// square on which the floor never gets shallower, so every depth's "below this" set is ONE connected piece. The level
		/// solver keeps a pond as one node with one surface (RM_LevelSolve: a pond is its floor histogram), which is exact only
		/// when a drawn-down lake cannot split into pools behind an inner sill; a hole with no such route is silted up to its
		/// sill (priority flood from the deepest square, deepest first). Holes and trenches that run down to the deep water
		/// keep their depth. Deterministic (ties by square index). Returns how many squares moved.</summary>
		public static int SingleBasin(int width, int height, IList<int> footprint, int[] f)
		{
			int n = footprint.Count;
			if (n == 0)
			{
				return 0;
			}
			var slotOf = new Dictionary<int, int>(n);
			int start = 0;
			for (int k = 0; k < n; k++)
			{
				slotOf[footprint[k]] = k;
				if (f[k] > f[start] || (f[k] == f[start] && footprint[k] < footprint[start]))
				{
					start = k;
				}
			}
			bool[] seen = new bool[n];
			var pq = new SortedSet<(int negDepth, int cell)>();
			seen[start] = true;
			pq.Add((-f[start], footprint[start]));
			int moved = 0;
			while (pq.Count > 0)
			{
				var e = pq.Min;
				pq.Remove(e);
				int k = slotOf[e.cell];
				int c = e.cell, x = c % width, z = c / width;
				for (int d = 0; d < 4; d++)
				{
					int X = x + DX[d], Z = z + DZ[d];
					if (X < 0 || Z < 0 || X >= width || Z >= height || !slotOf.TryGetValue(Z * width + X, out int m) || seen[m])
					{
						continue;
					}
					seen[m] = true;
					if (f[m] > f[k])
					{
						f[m] = f[k];
						moved++;
					}
					pq.Add((-f[m], footprint[m]));
				}
			}
			return moved;
		}

		/// <summary>The fraction of deep squares whose floor is at least <paramref name="offNotches"/> from the mean floor of
		/// all deep squares at the same distance from the shore: 0 for a floor that is a function of that distance alone (a
		/// radial crater). The verify row's irregularity measure.</summary>
		public static double OffRadial(int width, int height, IList<int> footprint, Func<int, bool> deep, int[] f, int offNotches)
		{
			int n = footprint.Count;
			var slotOf = new Dictionary<int, int>(n);
			for (int k = 0; k < n; k++) slotOf[footprint[k]] = k;
			int[] dist = new int[n];
			var q = new Queue<int>();
			for (int k = 0; k < n; k++)
			{
				int c = footprint[k], x = c % width, z = c / width;
				for (int d = 0; d < 4; d++)
				{
					int X = x + DX[d], Z = z + DZ[d];
					if (X < 0 || Z < 0 || X >= width || Z >= height || !slotOf.ContainsKey(Z * width + X))
					{
						dist[k] = 1;
						q.Enqueue(k);
						break;
					}
				}
			}
			while (q.Count > 0)
			{
				int k = q.Dequeue();
				int c = footprint[k], x = c % width, z = c / width;
				for (int d = 0; d < 4; d++)
				{
					if (slotOf.TryGetValue((z + DZ[d]) * width + x + DX[d], out int m) && x + DX[d] >= 0 && x + DX[d] < width && dist[m] == 0)
					{
						dist[m] = dist[k] + 1;
						q.Enqueue(m);
					}
				}
			}
			var sum = new Dictionary<int, double>();
			var cnt = new Dictionary<int, int>();
			for (int k = 0; k < n; k++)
			{
				if (!deep(footprint[k])) continue;
				sum.TryGetValue(dist[k], out double s); sum[dist[k]] = s + f[k];
				cnt.TryGetValue(dist[k], out int c2); cnt[dist[k]] = c2 + 1;
			}
			int off = 0, all = 0;
			for (int k = 0; k < n; k++)
			{
				if (!deep(footprint[k])) continue;
				all++;
				if (Math.Abs(f[k] - sum[dist[k]] / cnt[dist[k]]) >= offNotches) off++;
			}
			return all == 0 ? 0.0 : off / (double)all;
		}

		// ── deterministic noise (no System.Random: its sequence is a runtime's choice; this is ours) ──

		private static readonly int[] DX = { 1, -1, 0, 0 };
		private static readonly int[] DZ = { 0, 0, 1, -1 };

		internal static uint Mix(uint a, uint b)
		{
			unchecked
			{
				ulong h = a * 0x9E3779B97F4A7C15UL ^ (b + 0x632BE59BD9B4E019UL + ((ulong)a << 6) + ((ulong)a >> 2));
				h ^= h >> 30; h *= 0xBF58476D1CE4E5B9UL;
				h ^= h >> 27; h *= 0x94D049BB133111EBUL;
				h ^= h >> 31;
				return (uint)(h ^ (h >> 32));
			}
		}

		/// <summary>A uniform draw in [0, 1) from four integers.</summary>
		internal static double U01(uint seed, uint key, uint salt, uint extra)
		{
			uint h = Mix(Mix(seed, key), Mix(salt, extra));
			return (h >> 8) / 16777216.0;
		}

		private static double Lattice(uint k, int x, int z)
		{
			unchecked { return (Mix(k, Mix((uint)x, (uint)z)) >> 8) / 16777216.0; }
		}

		/// <summary>Smooth value noise in [0, 1].</summary>
		internal static double Value(uint k, double x, double z)
		{
			int ix = (int)Math.Floor(x), iz = (int)Math.Floor(z);
			double fx = x - ix, fz = z - iz;
			double sx = fx * fx * (3 - 2 * fx), sz = fz * fz * (3 - 2 * fz);
			double a = Lattice(k, ix, iz), b = Lattice(k, ix + 1, iz), c = Lattice(k, ix, iz + 1), d = Lattice(k, ix + 1, iz + 1);
			double top = a + (b - a) * sx, bot = c + (d - c) * sx;
			return top + (bot - top) * sz;
		}

		/// <summary>Three octaves of value noise, about [-1, 1].</summary>
		internal static double Fbm(uint k, double x, double z)
		{
			double v = 0.6 * Value(k, x, z) + 0.3 * Value(k + 1u, x * 2.3 + 17.1, z * 2.3 - 5.7) + 0.15 * Value(k + 2u, x * 5.1 - 3.3, z * 5.1 + 11.9);
			return (v / 1.05) * 2.0 - 1.0;
		}

		/// <summary>Soft terraces: <paramref name="levels"/> flat shelves joined by short steep risers.</summary>
		internal static double Terrace(double s, int levels)
		{
			if (s <= 0) return s;
			double v = s * levels;
			double i = Math.Floor(v), fr = v - i;
			double rise = fr < 0.75 ? 0.0 : (fr - 0.75) / 0.25;
			rise = rise * rise * (3 - 2 * rise);
			return (i + rise) / levels;
		}

		private static float Lerp(float a, float b, float t) => a + (b - a) * t;
		private static float Clamp01(float v) => v < 0f ? 0f : (v > 1f ? 1f : v);
	}
}
