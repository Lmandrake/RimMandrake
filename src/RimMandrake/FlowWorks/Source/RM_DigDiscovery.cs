using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FLOWWORKS_QUARRY_DIGGING_1 — canal-dig discovery (the FlowWorks half; sluice box and panning are River
	/// Works'). Design: design/RimMandrake/flowworks_quarry_sluice_panning_design_2026-10-03.md §2a, with the
	/// owner's card answers (2026-10-03): a find drops as a lump on the bank with a message, and a letter on the
	/// first find of each material per map; deep and superdeep cuts can reach deep-drill minerals; in a
	/// mineral-less place, digging yields chunks of local rock (consistent with quarries).
	///
	/// 🔑 "Local" without the registry. The design draws from MineralRegistry.QuarryDraw(map), which does not
	/// exist yet (MINERALS_WHERE_THEY_BELONG_1; its per-biome numbers await the owner's review sheet). Until it
	/// lands, the pool is THIS MAP'S OWN GEOLOGY — the ores actually in its rock (every resource rock on the
	/// map, weighted by how many cells of it there are), plus, for a Deep/Superdeep cut, whatever the deep
	/// resource grid holds under that very cell. That is local by construction and inherits whatever the
	/// registry later does to placement. Components and plasteel never come out of a hole (the owner's
	/// "absurd thing in Vanilla"): manufactured resources are excluded.
	///
	/// Exploit guard: a per-cell rolled-depth grid — a cut rolls only past the deepest level that cell has
	/// already rolled, so dig → fill → re-dig pays nothing twice. Ceiling: a per-map loose-find budget, a
	/// share of the units in the map's own resource rock (setting), so digging the whole map never out-mines
	/// the land. Every number is PROVISIONAL (design §2a defaults: 1.5% per cell-level cut, 10–25 units).
	/// </summary>
	public class RM_DigDiscoveryState : IExposable
	{
		private byte[] rolledDepth;
		private float budgetLeft = -1f;
		private HashSet<ThingDef> found = new HashSet<ThingDef>();
		public int Finds;
		public string LastFind = "";

		public float BudgetLeft => budgetLeft;

		public void ExposeData()
		{
			DataExposeUtility.LookByteArray(ref rolledDepth, "RM_digRolledDepth");
			Scribe_Values.Look(ref budgetLeft, "RM_digBudgetLeft", -1f);
			Scribe_Collections.Look(ref found, "RM_digFound", LookMode.Def);
			Scribe_Values.Look(ref Finds, "RM_digFinds", 0);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				if (found == null)
				{
					found = new HashSet<ThingDef>();
				}
				found.RemoveWhere(d => d == null);
			}
		}

		private void Ensure(Map map)
		{
			int n = map.cellIndices.NumGridCells;
			if (rolledDepth == null || rolledDepth.Length != n)
			{
				rolledDepth = new byte[n];
			}
			if (budgetLeft < 0f)
			{
				budgetLeft = RM_DigDiscovery.MapBudget(map);
			}
		}

		/// <summary>Dev surface (RM_NorthstarProofs.ProofResetRect): forget every rolled depth in <paramref name="r"/>, so a
		/// proof plot re-dug on the same map rolls again (DIG_RESET_REPAIR_ROLLED_DEPTH_REMEMBERS). Returns the cells that
		/// had rolled. Never called by the game: in play the exploit guard must remember.</summary>
		public int ResetRolled(Map map, CellRect r)
		{
			if (map == null || rolledDepth == null || rolledDepth.Length != map.cellIndices.NumGridCells)
			{
				return 0;
			}
			int n = 0;
			foreach (IntVec3 c in r.ClipInsideMap(map))
			{
				int i = map.cellIndices.CellToIndex(c);
				if (rolledDepth[i] != 0)
				{
					rolledDepth[i] = 0;
					n++;
				}
			}
			return n;
		}

		/// <summary>Called after a cut lands at <paramref name="newDepth"/>.</summary>
		public void OnCut(Map map, IntVec3 c, int newDepth, Pawn digger)
		{
			if ((!RimMandrakeFlowWorksSettings.digFindsEnabled && !RimMandrakeFlowWorksSettings.digRockChunksEnabled) || map == null || !c.InBounds(map))
			{
				// a cut happened: an armed debug force is spent on it, never carried into a later, unrelated cut
				ForceNextRoll = false;
				return;
			}
			Ensure(map);
			int i = map.cellIndices.CellToIndex(c);
			// spent on this cut whether or not it rolls (a re-dig of an already-rolled depth included)
			bool forced = ForceNextRoll;
			ForceNextRoll = false;
			if (!RM_DigDiscoveryMath.RollsAt(rolledDepth[i], newDepth))
			{
				return;
			}
			rolledDepth[i] = (byte)newDepth;
			// DIG_ROCK_TUNE_STONE_FIGHTS_BACK: the chunk roll is its own roll, under the same rolled-depth guard.
			RollRockChunk(map, c, newDepth, digger);
			if (!RimMandrakeFlowWorksSettings.digFindsEnabled)
			{
				return;
			}
			if (!forced && !Rand.Chance(RM_DigDiscoveryMath.Chance(RimMandrakeFlowWorksSettings.digFindChanceMultiplier)))
			{
				return;
			}
			ThingDef def = RM_DigDiscovery.Draw(map, c, newDepth, out bool rockChunk);
			if (def == null)
			{
				return;
			}
			int count = rockChunk ? 1 : RM_DigDiscoveryMath.LumpSize(Rand.Value, def.stackLimit);
			float cost = rockChunk ? 0f : count;
			if (!rockChunk && budgetLeft < cost)
			{
				// The land's loose share is spent: what is left is chunks of the rock itself.
				def = RM_DigDiscovery.LocalRockChunk(map);
				if (def == null)
				{
					return;
				}
				rockChunk = true;
				count = 1;
				cost = 0f;
			}
			Thing made = ThingMaker.MakeThing(def);
			made.stackCount = count;
			IntVec3 lip = RM_DigDiscovery.LipCellNear(map, c);
			// `placed` is the stack the find ended up in: absorbed into an earlier lump of the same ore, `made` is destroyed
			// and a letter or message aimed at it would jump nowhere.
			if (!GenPlace.TryPlaceThing(made, lip, map, ThingPlaceMode.Near, out Thing placed))
			{
				// C5-F12: a failed Near placement may already have merged part of the find into a stack; that part was
				// found and is charged in proportion. The unplaced rest is discarded (never dropped, never debited).
				int left = made.Destroyed ? 0 : made.stackCount;
				if (left < count)
				{
					budgetLeft -= cost * (count - left) / count;
				}
				if (!made.Destroyed)
				{
					made.Destroy();
				}
				return;
			}
			Thing target = placed != null && !placed.Destroyed ? placed : made;
			budgetLeft -= cost;
			Finds++;
			LastFind = def.defName + " x" + count + " @" + c.x + "," + c.z + " D=" + newDepth;
			if (!rockChunk && RimMandrakeFlowWorksSettings.digFindLetterEnabled && found.Add(def))
			{
				Find.LetterStack.ReceiveLetter("RMFlow_DigFindLetterLabel".Translate(def.LabelCap),
					"RMFlow_DigFindLetterText".Translate(def.label, digger?.LabelShort ?? ""),
					LetterDefOf.PositiveEvent, target);
			}
			else
			{
				Messages.Message("RMFlow_DigFindMessage".Translate(digger?.LabelShort ?? "", count, def.label),
					target, MessageTypeDefOf.PositiveEvent, false);
			}
		}

		/// <summary>DIG_ROCK_TUNE_STONE_FIGHTS_BACK (owner 2026-10-16): a cut through ROCK ground rolls a chunk of that rock at
		/// vanilla's wall-mining rate; a cut through anything else very rarely rolls a chunk of the local rock. Not budgeted:
		/// a chunk is the land itself, as the mineral roll's own rock fallback is.</summary>
		private void RollRockChunk(Map map, IntVec3 c, int newDepth, Pawn digger)
		{
			if (!RimMandrakeFlowWorksSettings.digRockChunksEnabled)
			{
				return;
			}
			ThingDef chunk;
			float chance;
			ThingDef rock = RM_DigDiscovery.RockGroundAt(map, c);
			// PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS: at superdeep and below the cut is through the deep stratum, rock
			// whatever lay on top, so it rolls that stone at the wall-mining rate.
			ThingDef deep = RimMandrakeFlowWorksSettings.digDeepStoneEnabled
				&& RM_DigDiscoveryMath.StrikesDeepStone(newDepth, RM_ExcavationDepth.Superdeep) ? RM_DeepStone.RockFor(map) : null;
			if (deep != null)
			{
				rock = deep;
			}
			if (rock != null)
			{
				chunk = rock.building.mineableThing;
				chance = RM_DigDiscoveryMath.RockChunkChance(rock.building.mineableDropChance, RimMandrakeFlowWorksSettings.digRockChunkMultiplier);
			}
			else
			{
				chunk = RM_DigDiscovery.LocalRockChunk(map);
				chance = RM_DigDiscoveryMath.SoilChunkChance(RimMandrakeFlowWorksSettings.digSoilChunkPercent);
			}
			if (chunk == null || !Rand.Chance(chance))
			{
				return;
			}
			Thing made = ThingMaker.MakeThing(chunk);
			made.stackCount = 1;
			if (!GenPlace.TryPlaceThing(made, RM_DigDiscovery.LipCellNear(map, c), map, ThingPlaceMode.Near, out Thing placed))
			{
				if (!made.Destroyed)
				{
					made.Destroy();
				}
				return;
			}
			Finds++;
			LastFind = chunk.defName + " x1 @" + c.x + "," + c.z + " D=" + newDepth
				+ (deep != null ? " (deep stone)" : rock != null ? " (rock ground)" : " (chunk, non-rock)");
			Thing target = placed != null && !placed.Destroyed ? placed : made;
			if (deep != null && RimMandrakeFlowWorksSettings.digFindLetterEnabled && found.Add(chunk))
			{
				// the first deep stone a map turns up is news: the pit has broken through to a new layer
				Find.LetterStack.ReceiveLetter("RMFlow_DeepStoneLetterLabel".Translate(chunk.LabelCap),
					"RMFlow_DeepStoneLetterText".Translate(chunk.label, digger?.LabelShort ?? ""),
					LetterDefOf.PositiveEvent, target);
				return;
			}
			Messages.Message("RMFlow_DigFindMessage".Translate(digger?.LabelShort ?? "", 1, chunk.label),
				target, MessageTypeDefOf.PositiveEvent, false);
		}

		public string Report(Map map)
		{
			return "DIGFINDS finds " + Finds + " | budget " + (budgetLeft < 0 ? "unset" : budgetLeft.ToString("F0"))
				+ " | first-found " + found.Count + " | last " + LastFind;
		}

		/// <summary>Debug/bridge: the next cut on any cell rolls with certainty.</summary>
		public static bool ForceNextRoll;
	}

	public static class RM_DigDiscovery
	{
		/// <summary>Vanilla resources that are made, not dug — never a find.</summary>
		private static readonly HashSet<string> NeverDug = new HashSet<string> { "ComponentIndustrial", "ComponentSpacer", "Plasteel" };

		public static bool Diggable(ThingDef d)
		{
			if (d == null || NeverDug.Contains(d.defName))
			{
				return false;
			}
			if (d.thingCategories != null)
			{
				foreach (ThingCategoryDef cat in d.thingCategories)
				{
					if (cat.defName == "Manufactured")
					{
						return false;
					}
				}
			}
			return true;
		}

		private static Dictionary<TerrainDef, ThingDef> rockByTerrain;

		/// <summary>DIG_ROCK_TUNE_STONE_FIGHTS_BACK: the natural rock a terrain is the ground of, or null. Read from the defs,
		/// never by name: each non-resource natural rock's naturalTerrain (rough), leaveTerrain (rough-hewn) and the
		/// smoothedTerrain of either (smoothed) -- the same links TerrainDefGenerator_Stone builds.</summary>
		public static ThingDef RockOfTerrain(TerrainDef t)
		{
			if (t == null)
			{
				return null;
			}
			if (rockByTerrain == null)
			{
				Dictionary<TerrainDef, ThingDef> m = new Dictionary<TerrainDef, ThingDef>();
				foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
				{
					if (d.building == null || !d.IsNonResourceNaturalRock)
					{
						continue;
					}
					foreach (TerrainDef g in new[] { d.building.naturalTerrain, d.building.leaveTerrain })
					{
						if (g == null)
						{
							continue;
						}
						if (!m.ContainsKey(g)) m[g] = d;
						if (g.smoothedTerrain != null && !m.ContainsKey(g.smoothedTerrain)) m[g.smoothedTerrain] = d;
					}
				}
				rockByTerrain = m;
			}
			ThingDef r;
			return rockByTerrain.TryGetValue(t, out r) ? r : null;
		}

		/// <summary>The rock a cut at <paramref name="c"/> goes through: the terrain it had before FlowWorks first dug it, else
		/// what is on top now. Null for soil, sand, gravel, a player floor or anything else.</summary>
		public static ThingDef RockGroundAt(Map map, IntVec3 c)
		{
			TerrainDef t = map.GetComponent<RM_MapComponent_Excavation>()?.OriginalTerrainAt(c)
				?? (map.terrainGrid.FoundationAt(c) ?? map.terrainGrid.TopTerrainAt(c));
			return RockOfTerrain(t);
		}

		/// <summary>The weighted local pool: every resource rock on the map counted by cells (cached per map
		/// per 2500 ticks — mining changes it slowly).</summary>
		private static Map poolMap;
		private static int poolTick = -99999;
		private static readonly Dictionary<ThingDef, float> pool = new Dictionary<ThingDef, float>();

		/// <summary>C5-F3: forget the pooled map once it is gone, so this static does not pin it.</summary>
		public static void PruneDeadMaps()
		{
			if (poolMap != null && (Find.Maps == null || !Find.Maps.Contains(poolMap)))
			{
				poolMap = null;
				pool.Clear();
			}
		}

		private static Dictionary<ThingDef, float> LocalPool(Map map)
		{
			int now = Find.TickManager.TicksGame;
			if (ReferenceEquals(map, poolMap) && now - poolTick < 2500)
			{
				return pool;
			}
			poolMap = map;
			poolTick = now;
			pool.Clear();
			foreach (Thing t in map.listerThings.AllThings)
			{
				if (t.def.building != null && t.def.building.isResourceRock)
				{
					Add(t.def);
				}
			}
			return pool;
		}

		private static void Add(ThingDef rockDef)
		{
			BuildingProperties b = rockDef?.building;
			if (b == null || !b.isResourceRock || b.mineableThing == null || !Diggable(b.mineableThing))
			{
				return;
			}
			pool.TryGetValue(b.mineableThing, out float w);
			pool[b.mineableThing] = w + 1f;
		}

		private static readonly List<ThingDef> globalOres = new List<ThingDef>();

		private static List<ThingDef> GlobalOres()
		{
			if (globalOres.Count == 0)
			{
				foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
				{
					if (d.building != null && d.building.isResourceRock && d.building.mineableThing != null
						&& Diggable(d.building.mineableThing) && !globalOres.Contains(d.building.mineableThing))
					{
						globalOres.Add(d.building.mineableThing);
					}
				}
			}
			return globalOres;
		}

		/// <summary>One find. Deep cuts first try what lies in the deep resource grid under the cell.</summary>
		public static ThingDef Draw(Map map, IntVec3 c, int depth, out bool rockChunk)
		{
			rockChunk = false;
			if (RM_DigDiscoveryMath.ReachesDeep(depth) && map.deepResourceGrid != null)
			{
				ThingDef deep = map.deepResourceGrid.ThingDefAt(c);
				if (deep != null && Diggable(deep) && Rand.Chance(RM_DigDiscoveryMath.DeepShare))
				{
					return deep;
				}
			}
			if (!RimMandrakeFlowWorksSettings.digFindsLocalOnly)
			{
				List<ThingDef> all = GlobalOres();
				if (all.Count > 0)
				{
					return all.RandomElement();
				}
			}
			Dictionary<ThingDef, float> p = LocalPool(map);
			if (p.Count > 0)
			{
				return p.Keys.RandomElementByWeight(d => p[d]);
			}
			rockChunk = true;
			return LocalRockChunk(map);
		}

		/// <summary>A chunk of the map's own rock (owner card: a mineral-less place yields local rock).</summary>
		public static ThingDef LocalRockChunk(Map map)
		{
			IEnumerable<ThingDef> src = Find.World != null ? Find.World.NaturalRockTypesIn(map.Tile) : null;
			if (src == null)
			{
				return null;
			}
			List<ThingDef> chunks = new List<ThingDef>();
			foreach (ThingDef rock in src)
			{
				ThingDef chunk = rock?.building?.mineableThing;
				if (chunk != null)
				{
					chunks.Add(chunk);
				}
			}
			return chunks.Count > 0 ? chunks.RandomElement() : null;
		}

		/// <summary>The loose-find budget: a share (setting, % ) of the units in the map's resource rock.</summary>
		public static float MapBudget(Map map)
		{
			float units = 0f;
			foreach (Thing t in map.listerThings.AllThings)
			{
				BuildingProperties b = t.def.building;
				if (b != null && b.isResourceRock && b.mineableThing != null && Diggable(b.mineableThing))
				{
					units += b.EffectiveMineableYield;
				}
			}
			return RM_DigDiscoveryMath.Budget(units, RimMandrakeFlowWorksSettings.digFindBudgetPercent);
		}

		/// <summary>The nearest standable cell that is not dug — the bank the lump is thrown onto.</summary>
		public static IntVec3 LipCellNear(Map map, IntVec3 c)
		{
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			foreach (IntVec3 n in GenRadial.RadialCellsAround(c, 6f, false))
			{
				if (n.InBounds(map) && n.Standable(map) && (eng == null || !eng.IsExcavated(n)))
				{
					return n;
				}
			}
			return c;
		}
	}

	/// <summary>PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS: a BiomeDef's deep stratum, the stone a superdeep cut breaks
	/// through (rulings 12_rocks_design.md idea 6: basalt under the Pyrelands, ice under the night side, wreck layers under
	/// Warscar). <c>deepRocks</c> names natural rock buildings (the ThingDef whose mineableThing is the chunk); a tile draws
	/// one of them, stably. A biome that names none gets the fallback in <see cref="RM_DeepStone.RockFor"/>.</summary>
	public class RM_DeepStoneExtension : DefModExtension
	{
		public List<ThingDef> deepRocks;
	}

	/// <summary>PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS (owner card 2026-10-19, "deeper stone at superdeep pits"): which
	/// stone lies under a map. The biome's own <see cref="RM_DeepStoneExtension"/> list wins. Otherwise (PROVISIONAL, until
	/// BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND gives each biome its stones) a natural stone the tile does NOT show on its
	/// surface, allowed in that biome by vanilla's own rule, picked stably from the tile's hash: so the deep layer is always
	/// something new, and the same planet square always holds the same one. Null when no such stone exists.</summary>
	public static class RM_DeepStone
	{
		// The answer is a pure function of the tile and its biome (and the def database), so the cache is keyed on those,
		// never on the Map: nothing here pins a map that is gone.
		private static int cacheTile = int.MinValue;
		private static BiomeDef cacheBiome;
		private static ThingDef cacheRock;

		public static ThingDef RockFor(Map map)
		{
			if (map == null)
			{
				return null;
			}
			int tile = map.Tile.GetHashCode();
			if (tile == cacheTile && ReferenceEquals(map.Biome, cacheBiome))
			{
				return cacheRock;
			}
			cacheRock = Resolve(map);
			cacheTile = tile;
			cacheBiome = map.Biome;
			return cacheRock;
		}

		private static bool IsStone(ThingDef rock)
		{
			ThingDef chunk = rock?.building?.mineableThing;
			if (chunk == null || !rock.IsNonResourceNaturalRock || rock.building.isResourceRock)
			{
				return false;
			}
			if (chunk.thingCategories != null)
			{
				foreach (ThingCategoryDef cat in chunk.thingCategories)
				{
					if (cat == ThingCategoryDefOf.StoneChunks)
					{
						return true;
					}
				}
			}
			return false;
		}

		private static ThingDef Resolve(Map map)
		{
			int seed = map.Tile.GetHashCode() ^ 0x5D33;
			BiomeDef biome = map.Biome;
			List<ThingDef> own = new List<ThingDef>();
			List<ThingDef> named = biome?.GetModExtension<RM_DeepStoneExtension>()?.deepRocks;
			if (named != null)
			{
				foreach (ThingDef d in named)
				{
					if (d?.building?.mineableThing != null)
					{
						own.Add(d);
					}
				}
			}
			if (own.Count > 0)
			{
				return own[RM_DigDiscoveryMath.PickIndex(seed, own.Count)];
			}
			HashSet<ThingDef> surface = new HashSet<ThingDef>();
			IEnumerable<ThingDef> src = Find.World != null ? Find.World.NaturalRockTypesIn(map.Tile) : null;
			if (src != null)
			{
				foreach (ThingDef d in src)
				{
					if (d != null) surface.Add(d);
				}
			}
			List<ThingDef> pool = new List<ThingDef>();
			foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
			{
				if (!IsStone(d) || surface.Contains(d))
				{
					continue;
				}
				// vanilla's RockAllowedInBiome: a biome-specific rock lies only under the biomes that list it
				if (d.building.biomeSpecific && (biome == null || !biome.extraRockTypes.NotNullAndContains(d)))
				{
					continue;
				}
				pool.Add(d);
			}
			// definition order is load order; sort by name so a mod-list reshuffle never moves a tile's stone
			pool.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));
			return pool.Count > 0 ? pool[RM_DigDiscoveryMath.PickIndex(seed, pool.Count)] : null;
		}

		/// <summary>static_call surface (RM_DigDiscoveryProof "deepstone"): what lies under the current map and why.</summary>
		public static string Report(Map map)
		{
			ThingDef r = RockFor(map);
			bool own = map?.Biome?.GetModExtension<RM_DeepStoneExtension>()?.deepRocks?.Count > 0;
			return "DEEPSTONE " + (r == null ? "none" : r.defName + " chunk=" + r.building.mineableThing.defName)
				+ " | source " + (own ? "biome" : "fallback") + " | enabled " + RimMandrakeFlowWorksSettings.digDeepStoneEnabled;
		}
	}

	/// <summary>static_call surface: "" reports; "force" makes the next cut roll with certainty; "deepstone" names the
	/// stone a superdeep cut on this map breaks through.</summary>
	public static class RM_DigDiscoveryProof
	{
		public static string ProofReport(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null)
			{
				return "REFUSED: no excavation component on the current map";
			}
			if (arg == "force")
			{
				RM_DigDiscoveryState.ForceNextRoll = true;
				return "ARMED: the next canal cut rolls with certainty | " + ex.DigDiscovery.Report(map);
			}
			if (arg == "deepstone")
			{
				return RM_DeepStone.Report(map);
			}
			return ex.DigDiscovery.Report(map);
		}
	}
}
