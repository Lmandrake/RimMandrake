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

		/// <summary>Called after a cut lands at <paramref name="newDepth"/>.</summary>
		public void OnCut(Map map, IntVec3 c, int newDepth, Pawn digger)
		{
			if (!RimMandrakeFlowWorksSettings.digFindsEnabled || map == null || !c.InBounds(map))
			{
				// a cut happened: an armed debug force is spent on it, never carried into a later, unrelated cut
				ForceNextRoll = false;
				return;
			}
			Ensure(map);
			int i = map.cellIndices.CellToIndex(c);
			if (!RM_DigDiscoveryMath.RollsAt(rolledDepth[i], newDepth))
			{
				return;
			}
			rolledDepth[i] = (byte)newDepth;
			bool forced = ForceNextRoll;
			ForceNextRoll = false;
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
			budgetLeft -= cost;
			Thing made = ThingMaker.MakeThing(def);
			made.stackCount = count;
			IntVec3 lip = RM_DigDiscovery.LipCellNear(map, c);
			if (!GenPlace.TryPlaceThing(made, lip, map, ThingPlaceMode.Near))
			{
				return;
			}
			Finds++;
			LastFind = def.defName + " x" + count + " @" + c.x + "," + c.z + " D=" + newDepth;
			if (!rockChunk && RimMandrakeFlowWorksSettings.digFindLetterEnabled && found.Add(def))
			{
				Find.LetterStack.ReceiveLetter("RMFlow_DigFindLetterLabel".Translate(def.LabelCap),
					"RMFlow_DigFindLetterText".Translate(def.label, digger?.LabelShort ?? ""),
					LetterDefOf.PositiveEvent, made);
			}
			else
			{
				Messages.Message("RMFlow_DigFindMessage".Translate(digger?.LabelShort ?? "", count, def.label),
					made, MessageTypeDefOf.PositiveEvent, false);
			}
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

		/// <summary>The weighted local pool: every resource rock on the map counted by cells (cached per map
		/// per 2500 ticks — mining changes it slowly).</summary>
		private static Map poolMap;
		private static int poolTick = -99999;
		private static readonly Dictionary<ThingDef, float> pool = new Dictionary<ThingDef, float>();

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

	/// <summary>static_call surface: "" reports; "force" makes the next cut roll with certainty.</summary>
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
			return ex.DigDiscovery.Report(map);
		}
	}
}
