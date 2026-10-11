using System.Collections.Generic;
using System.Text;
using RimMandrake.FlowWorks.Rivers;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Quarry
{
	/// <summary>
	/// FLOWWORKS_QUARRY_DIGGING_1, river half: the sluice box and panning. Design:
	/// design/RimMandrake/flowworks_quarry_sluice_panning_design_2026-10-03.md §2b–2c, with the owner's card answers
	/// (2026-10-03): both live in FlowWorks' Rivers; panning is Mining, ordered through a panning spot on the dry bank;
	/// the mineral registry gains a separate per-biome "what the rivers carry" column.
	///
	/// 🔑 PROVISIONAL POOL. That registry column does not exist yet (MINERALS_WHERE_THEY_BELONG_1: its numbers await
	/// the owner's review sheet, and its C# mod is unbuilt). Until it lands, RM_PlacerDraw is the ONE swap point and
	/// reads THIS MAP'S OWN GEOLOGY: the heavy, durable minerals (RM_PlacerPoolDef.placerThings) in the map's
	/// resource rock, weighted by cells. So until the swap, a river carries gold only where the hills hold gold —
	/// the ruling's "placer gold where hills have none" arrives with the registry, not before.
	///
	/// ONE STOCK PER MAP, not per water body: the design keys it per river water body; a map almost always holds
	/// one river, and keying on Odyssey's WaterBody would need an identity that survives a save. Sluices and
	/// panners share it, so ten sluices earn what a few do.
	/// </summary>
	public class RM_PlacerPoolDef : Def
	{
		/// <summary>Resources that collect in river gravel (heavy, hard-wearing). Never salts, soft rock or made things.</summary>
		public List<ThingDef> placerThings = new List<ThingDef>();

		public static bool IsPlacer(ThingDef d)
		{
			if (d == null)
			{
				return false;
			}
			foreach (RM_PlacerPoolDef p in DefDatabase<RM_PlacerPoolDef>.AllDefsListForReading)
			{
				if (p.placerThings != null && p.placerThings.Contains(d))
				{
					return true;
				}
			}
			return false;
		}
	}

	[DefOf]
	public static class RM_QuarryDefOf
	{
		public static ThingDef RM_SluiceBox;
		public static ThingDef RM_PanningSpot;
		public static JobDef RM_PanForPlacerJob;

		static RM_QuarryDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RM_QuarryDefOf));
		}
	}

	/// <summary>The swap point. When the registry's rivers-carry column exists, Pool() and PlacerUnits() read it.</summary>
	public static class RM_PlacerDraw
	{
		public static Dictionary<ThingDef, float> Pool(Map map)
		{
			Dictionary<ThingDef, float> pool = new Dictionary<ThingDef, float>();
			if (map == null)
			{
				return pool;
			}
			foreach (Thing t in map.listerThings.AllThings)
			{
				BuildingProperties b = t.def.building;
				if (b != null && b.isResourceRock && b.mineableThing != null && RM_PlacerPoolDef.IsPlacer(b.mineableThing))
				{
					pool.TryGetValue(b.mineableThing, out float w);
					pool[b.mineableThing] = w + 1f;
				}
			}
			return pool;
		}

		/// <summary>Units of placer minerals in the map's rock — the base the river's stock is a share of.</summary>
		public static float PlacerUnits(Map map)
		{
			float units = 0f;
			if (map == null)
			{
				return 0f;
			}
			foreach (Thing t in map.listerThings.AllThings)
			{
				BuildingProperties b = t.def.building;
				if (b != null && b.isResourceRock && b.mineableThing != null && RM_PlacerPoolDef.IsPlacer(b.mineableThing))
				{
					units += b.EffectiveMineableYield;
				}
			}
			return units;
		}

		public static ThingDef Draw(Map map)
		{
			Dictionary<ThingDef, float> p = Pool(map);
			if (p.Count == 0)
			{
				return null;
			}
			return p.Keys.RandomElementByWeight(d => p[d]);
		}
	}

	/// <summary>Shallow moving river water — the only water that washes gravel. Calmed (a weir's slack pool) drops a lane.</summary>
	public static class RM_PlacerWater
	{
		public static int LaneAt(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return RM_RiverMath.LaneNone;
			}
			int lane = RM_RiverCurrentLanes.LaneOf(c.GetTerrain(map));
			RM_MapComponent_RiverCurrent comp = map.GetComponent<RM_MapComponent_RiverCurrent>();
			if (lane != RM_RiverMath.LaneNone && comp != null && comp.InPool(c))
			{
				lane = RM_RiverMath.PoolLane(lane);
			}
			return lane;
		}

		/// <summary>Terrain alone (for placement): shallow moving river water.</summary>
		public static bool IsShallowRiver(Map map, IntVec3 c)
		{
			return c.InBounds(map) && RM_RiverCurrentLanes.LaneOf(c.GetTerrain(map)) == RM_RiverMath.LaneMargin;
		}

		public static IntVec3 AdjacentShallowRiver(Map map, IntVec3 c)
		{
			foreach (IntVec3 d in GenAdj.CardinalDirections)
			{
				IntVec3 n = c + d;
				if (IsShallowRiver(map, n))
				{
					return n;
				}
			}
			return IntVec3.Invalid;
		}

		public static float SizeFactor(Map map, IntVec3 c)
		{
			RM_MapComponent_RiverCurrent comp = map?.GetComponent<RM_MapComponent_RiverCurrent>();
			if (comp == null || !RM_RiversSettings.scaleWithRiverSize)
			{
				return 1f;
			}
			comp.FlowDirAt(c); // builds the grid, which sets the size factor
			return comp.SizeFactor;
		}
	}

	/// <summary>The map's one river stock: regrows to its cap over a year, a flood tops it up (setting).</summary>
	public class RM_MapComponent_PlacerStock : MapComponent
	{
		private float stock = -1f;
		private float cap = -1f;
		private int lastTick = -1;
		private bool floodWas;
		public int SluiceUnits;
		public int PanUnits;
		public int Refills;

		public RM_MapComponent_PlacerStock(Map map) : base(map)
		{
		}

		public float Stock
		{
			get
			{
				Ensure();
				return stock;
			}
		}

		public float Cap
		{
			get
			{
				Ensure();
				return cap;
			}
		}

		private void Ensure()
		{
			if (cap < 0f)
			{
				cap = RM_PlacerMath.StockCap(RM_PlacerDraw.PlacerUnits(map), RM_QuarrySettings.placerStockPercent);
				stock = cap;
				lastTick = Find.TickManager.TicksGame;
			}
		}

		public override void ExposeData()
		{
			Scribe_Values.Look(ref stock, "RM_placerStock", -1f);
			Scribe_Values.Look(ref cap, "RM_placerCap", -1f);
			Scribe_Values.Look(ref lastTick, "RM_placerLastTick", -1);
			Scribe_Values.Look(ref floodWas, "RM_placerFloodWas", false);
			Scribe_Values.Look(ref SluiceUnits, "RM_placerSluiceUnits", 0);
			Scribe_Values.Look(ref PanUnits, "RM_placerPanUnits", 0);
			Scribe_Values.Look(ref Refills, "RM_placerRefills", 0);
		}

		public override void MapComponentTick()
		{
			int now = Find.TickManager.TicksGame;
			if (now % 2500 != 0 || cap < 0f)
			{
				return; // nothing to regrow until a sluice or panner first asks
			}
			stock = RM_PlacerMath.Regrow(stock, cap, now - lastTick);
			lastTick = now;
			bool flood = RM_RiverWorks.FloodActive(map);
			if (flood && !floodWas && RM_QuarrySettings.placerFloodRefill)
			{
				Refill();
			}
			floodWas = flood;
		}

		public void Refill()
		{
			Ensure();
			stock = cap;
			Refills++;
		}

		/// <summary>Takes up to <paramref name="want"/> whole units; returns what was taken.</summary>
		public int Take(int want)
		{
			Ensure();
			int n = RM_PlacerMath.Take(stock, want);
			stock -= n;
			return n;
		}

		public static RM_MapComponent_PlacerStock Of(Map map)
		{
			return map?.GetComponent<RM_MapComponent_PlacerStock>();
		}

		public string Report()
		{
			Ensure();
			StringBuilder sb = new StringBuilder("PLACER stock=" + stock.ToString("F1") + " cap=" + cap.ToString("F1")
				+ " sluiced=" + SluiceUnits + " panned=" + PanUnits + " refills=" + Refills + " pool=");
			foreach (KeyValuePair<ThingDef, float> kv in RM_PlacerDraw.Pool(map))
			{
				sb.Append(kv.Key.defName).Append(':').Append(kv.Value.ToString("F0")).Append(',');
			}
			return sb.ToString();
		}
	}

	/// <summary>Design §2b: 1×2 across the bank edge — one end in SHALLOW moving river water, one on solid ground.</summary>
	public class RM_PlaceWorker_SluiceBox : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map,
			Thing thingToIgnore = null, Thing thing = null)
		{
			int water = 0;
			int bank = 0;
			foreach (IntVec3 c in GenAdj.OccupiedRect(loc, rot, checkingDef.Size))
			{
				if (!c.InBounds(map))
				{
					return false;
				}
				if (RM_PlacerWater.IsShallowRiver(map, c))
				{
					water++;
				}
				else if (c.GetAffordances(map).Contains(TerrainAffordanceDefOf.Light))
				{
					bank++;
				}
			}
			if (water != 1 || bank != 1)
			{
				return new AcceptanceReport("A sluice box must straddle the bank: one end in shallow moving river water, one on solid ground.");
			}
			return true;
		}
	}

	/// <summary>Design §2c / owner card: the panning spot is on the dry bank, beside shallow moving water.</summary>
	public class RM_PlaceWorker_PanningSpot : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map,
			Thing thingToIgnore = null, Thing thing = null)
		{
			if (!loc.InBounds(map) || RM_PlacerWater.IsShallowRiver(map, loc))
			{
				return new AcceptanceReport("A panning spot goes on the dry bank, not in the water.");
			}
			if (!RM_PlacerWater.AdjacentShallowRiver(map, loc).IsValid)
			{
				return new AcceptanceReport("A panning spot must be right beside shallow moving river water.");
			}
			return true;
		}
	}

	/// <summary>The sluice box: passive, no pawn, no power. Once a day it washes a little of what the river carries
	/// onto its bank end, from the map's shared stock. Yield scales with river size; calm water washes nothing.</summary>
	public class RM_Building_SluiceBox : Building
	{
		private int nextRollTick = -1;
		public string LastResult = "";

		public IntVec3 WaterCell
		{
			get
			{
				foreach (IntVec3 c in this.OccupiedRect())
				{
					if (RM_PlacerWater.IsShallowRiver(Map, c))
					{
						return c;
					}
				}
				return IntVec3.Invalid;
			}
		}

		public IntVec3 BankCell
		{
			get
			{
				IntVec3 w = WaterCell;
				foreach (IntVec3 c in this.OccupiedRect())
				{
					if (c != w)
					{
						return c;
					}
				}
				return Position;
			}
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref nextRollTick, "RM_sluiceNextRoll", -1);
		}

		protected override void Tick()
		{
			base.Tick();
			if (!this.IsHashIntervalTick(250))
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			if (nextRollTick < 0)
			{
				nextRollTick = now + RM_PlacerMath.SluiceIntervalTicks;
				return;
			}
			if (now >= nextRollTick)
			{
				nextRollTick = now + RM_PlacerMath.SluiceIntervalTicks;
				Wash();
			}
		}

		/// <summary>One day's wash. Public so the first script can force it. Returns what happened.</summary>
		public string Wash()
		{
			if (!RM_QuarrySettings.SluiceActive)
			{
				return LastResult = "sluice=off";
			}
			IntVec3 w = WaterCell;
			if (!w.IsValid)
			{
				return LastResult = "sluice=nowater";
			}
			int lane = RM_PlacerWater.LaneAt(Map, w);
			int want = RM_PlacerMath.SluiceYield(Rand.Value, lane, RM_PlacerWater.SizeFactor(Map, w), RM_QuarrySettings.sluiceYieldMultiplier);
			if (want <= 0)
			{
				return LastResult = "sluice=nothing lane=" + lane;
			}
			ThingDef def = RM_PlacerDraw.Draw(Map);
			if (def == null)
			{
				return LastResult = "sluice=rivercarriesnothing";
			}
			RM_MapComponent_PlacerStock stock = RM_MapComponent_PlacerStock.Of(Map);
			int got = stock?.Take(want) ?? 0;
			if (got <= 0)
			{
				return LastResult = "sluice=stockspent";
			}
			Thing t = ThingMaker.MakeThing(def);
			t.stackCount = Mathf.Min(got, def.stackLimit);
			if (!GenPlace.TryPlaceThing(t, BankCell, Map, ThingPlaceMode.Near))
			{
				return LastResult = "sluice=noroom";
			}
			stock.SluiceUnits += got;
			return LastResult = "sluice=" + def.defName + "x" + got + " lane=" + lane;
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			IntVec3 w = WaterCell;
			string lane = !w.IsValid ? "no water" : (RM_PlacerWater.LaneAt(Map, w) == RM_RiverMath.LaneMargin ? "washing" : "water too calm to wash");
			RM_MapComponent_PlacerStock stock = RM_MapComponent_PlacerStock.Of(Map);
			string line = "Sluice: " + lane + (stock != null ? ", river stock " + stock.Stock.ToString("F0") + "/" + stock.Cap.ToString("F0") : "");
			if (!LastResult.NullOrEmpty())
			{
				line += "\nLast wash: " + LastResult;
			}
			return s.NullOrEmpty() ? line : s + "\n" + line;
		}
	}

	/// <summary>Mining work: pan at a free, reachable panning spot while the river's stock has anything left.</summary>
	public class RM_WorkGiver_PanForPlacer : WorkGiver_Scanner
	{
		public override PathEndMode PathEndMode => PathEndMode.OnCell;

		public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForDef(RM_QuarryDefOf.RM_PanningSpot);

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			if (!RM_QuarrySettings.PanningActive)
			{
				return true;
			}
			RM_MapComponent_PlacerStock stock = RM_MapComponent_PlacerStock.Of(pawn.Map);
			// a map whose rock holds no placer mineral has a cap of 0, so this also skips a river that carries nothing
			return stock == null || stock.Stock < 1f;
		}

		public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			return t.def == RM_QuarryDefOf.RM_PanningSpot && !t.IsForbidden(pawn)
				&& RM_PlacerWater.AdjacentShallowRiver(t.Map, t.Position).IsValid
				&& pawn.CanReserve(t, 1, -1, null, forced)
				&& pawn.CanReach(t, PathEndMode.OnCell, Danger.Some);
		}

		public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			return JobMaker.MakeJob(RM_QuarryDefOf.RM_PanForPlacerJob, t);
		}
	}

	/// <summary>Stand on the spot (the bank — never in the water, which River Works' current would fight), pan for a
	/// session scaled by MiningSpeed, learn a little Mining, then take 0–3 units from the river's stock.</summary>
	public class JobDriver_PanForPlacer : JobDriver
	{
		private const float XpPerTick = 0.04f;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
			this.FailOn(() => !RM_QuarrySettings.PanningActive);
			yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);
			int ticks = RM_PlacerMath.PanTicks(pawn.GetStatValue(StatDefOf.MiningSpeed));
			Toil pan = Toils_General.Wait(ticks).WithProgressBarToilDelay(TargetIndex.A);
			pan.handlingFacing = true;
			pan.tickAction = delegate
			{
				IntVec3 w = RM_PlacerWater.AdjacentShallowRiver(Map, pawn.Position);
				if (w.IsValid)
				{
					pawn.rotationTracker.FaceCell(w);
				}
				pawn.skills?.Learn(SkillDefOf.Mining, XpPerTick);
			};
			yield return pan;
			Toil finish = ToilMaker.MakeToil("PanForPlacerFinish");
			finish.initAction = delegate
			{
				RM_PlacerPanning.Session(pawn);
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}

	public static class RM_PlacerPanning
	{
		/// <summary>One finished session for <paramref name="pawn"/>. Public so the first script can force it.</summary>
		public static string Session(Pawn pawn)
		{
			Map map = pawn?.Map;
			if (map == null || !RM_QuarrySettings.PanningActive)
			{
				return "pan=off";
			}
			int skill = pawn.skills?.GetSkill(SkillDefOf.Mining)?.Level ?? 0;
			int want = RM_PlacerMath.PanSession(Rand.Value, Rand.Value, skill, RM_QuarrySettings.panningYieldMultiplier);
			if (want <= 0)
			{
				return "pan=nothing";
			}
			ThingDef def = RM_PlacerDraw.Draw(map);
			RM_MapComponent_PlacerStock stock = RM_MapComponent_PlacerStock.Of(map);
			if (def == null || stock == null)
			{
				return "pan=rivercarriesnothing";
			}
			int got = stock.Take(want);
			if (got <= 0)
			{
				return "pan=stockspent";
			}
			Thing t = ThingMaker.MakeThing(def);
			t.stackCount = got;
			if (!GenPlace.TryPlaceThing(t, pawn.Position, map, ThingPlaceMode.Near))
			{
				return "pan=noroom";
			}
			stock.PanUnits += got;
			Messages.Message(pawn.LabelShort + " panned " + got + " " + def.label + " out of the river.", t, MessageTypeDefOf.SilentInput, false);
			return "pan=" + def.defName + "x" + got;
		}
	}

	/// <summary>static_call surface. "" reports the stock; "wash" forces every sluice's daily wash; "refill" refills
	/// the stock as a flood would; "drain" empties it; "pan" runs one finished session for the first colonist on a spot.</summary>
	public static class RM_PlacerProof
	{
		public static string ProofReport(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_PlacerStock stock = RM_MapComponent_PlacerStock.Of(map);
			if (stock == null)
			{
				return "REFUSED: no placer stock component on the current map";
			}
			StringBuilder sb = new StringBuilder();
			switch ((arg ?? "").Trim())
			{
				case "wash":
					foreach (Thing t in map.listerThings.ThingsOfDef(RM_QuarryDefOf.RM_SluiceBox))
					{
						if (t is RM_Building_SluiceBox s)
						{
							sb.Append(s.Position).Append(' ').Append(s.Wash()).Append(" | ");
						}
					}
					if (sb.Length == 0)
					{
						return "UNMEASURED: no sluice box on the map | " + stock.Report();
					}
					break;
				case "selfcheck":
					return SelfCheck(map, stock);
				case "refill":
					stock.Refill();
					break;
				case "drain":
					stock.Take(int.MaxValue / 2);
					break;
				case "pan":
					Pawn p = null;
					foreach (Thing spot in map.listerThings.ThingsOfDef(RM_QuarryDefOf.RM_PanningSpot))
					{
						foreach (Thing th in spot.Position.GetThingList(map))
						{
							if (th is Pawn pw && pw.IsColonist)
							{
								p = pw;
							}
						}
					}
					if (p == null)
					{
						return "UNMEASURED: no colonist standing on a panning spot | " + stock.Report();
					}
					sb.Append(p.LabelShort).Append(' ').Append(RM_PlacerPanning.Session(p)).Append(" | ");
					break;
			}
			return sb + stock.Report();
		}

		/// <summary>The first script's one probe: find a legal bank-edge site on the map's own river, spawn a sluice box
		/// there, refill, force five washes, check every output is in the pool and the stock fell by exactly what
		/// came out, wash once with the setting off, pan once with the first free colonist, then remove what it made.</summary>
		private static string SelfCheck(Map map, RM_MapComponent_PlacerStock stock)
		{
			ThingDef def = RM_QuarryDefOf.RM_SluiceBox;
			IntVec3 site = IntVec3.Invalid;
			Rot4 rot = Rot4.North;
			foreach (IntVec3 c in map.AllCells)
			{
				if (!RM_PlacerWater.IsShallowRiver(map, c))
				{
					continue;
				}
				for (int r = 0; r < 4 && !site.IsValid; r++)
				{
					Rot4 rr = new Rot4(r);
					if (GenConstruct.CanPlaceBlueprintAt(def, c, rr, map, false, null, null, null).Accepted
						&& new RM_PlaceWorker_SluiceBox().AllowsPlacing(def, c, rr, map).Accepted)
					{
						site = c;
						rot = rr;
					}
				}
				if (site.IsValid)
				{
					break;
				}
			}
			if (!site.IsValid)
			{
				return "UNMEASURED: no legal sluice site (shallow moving river beside solid bank) on this map | " + stock.Report();
			}
			Dictionary<ThingDef, float> pool = RM_PlacerDraw.Pool(map);
			RM_Building_SluiceBox box = (RM_Building_SluiceBox)GenSpawn.Spawn(ThingMaker.MakeThing(def, GenStuff.DefaultStuffFor(def)), site, map, rot);
			stock.Refill();
			float before = stock.Stock;
			int got = 0;
			bool inPool = true;
			List<string> results = new List<string>();
			List<Thing> made = new List<Thing>();
			HashSet<Thing> already = new HashSet<Thing>(map.listerThings.AllThings);
			for (int i = 0; i < 5; i++)
			{
				string res = box.Wash();
				results.Add(res);
				int x = res.IndexOf('x');
				if (res.StartsWith("sluice=") && x > 0 && res.Contains(" lane="))
				{
					string name = res.Substring(7, x - 7);
					ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(name);
					inPool &= d != null && pool.ContainsKey(d);
					int sp = res.IndexOf(' ', x);
					got += int.Parse(res.Substring(x + 1, sp - x - 1));
				}
			}
			float after = stock.Stock;
			bool was = RM_QuarrySettings.sluiceBoxEnabled;
			RM_QuarrySettings.sluiceBoxEnabled = false;
			string off = box.Wash();
			RM_QuarrySettings.sluiceBoxEnabled = was;
			string pan = "pan=nocolonist";
			foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
			{
				pan = RM_PlacerPanning.Session(p);
				break;
			}
			foreach (Thing t in map.listerThings.AllThings)
			{
				if (!already.Contains(t) && t.def.category == ThingCategory.Item)
				{
					made.Add(t);
				}
			}
			foreach (Thing t in made)
			{
				t.Destroy();
			}
			box.Destroy();
			return "site=" + site.x + "," + site.z + " rot=" + rot.AsInt + " poolCount=" + pool.Count + " lane=" + RM_PlacerWater.LaneAt(map, site)
				+ " before=" + before.ToString("F1") + " after=" + after.ToString("F1") + " got=" + got
				+ " drawMatches=" + (System.Math.Abs(before - after - got) < 0.01f) + " inPool=" + inPool
				+ " off=" + off + " pan=" + pan + " washes=" + string.Join(";", results);
		}
	}
}
