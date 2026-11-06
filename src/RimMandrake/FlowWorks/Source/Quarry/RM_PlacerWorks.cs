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
		/// <summary>The placer units the map's rock held when the stock was first asked for: the saved base. The cap is
		/// derived from it LIVE with the current "River stock" setting, so moving that slider applies to running maps.</summary>
		private float units = -1f;
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
				return CapNow;
			}
		}

		private float CapNow => RM_PlacerMath.StockCap(units, RM_QuarrySettings.placerStockPercent);

		private int poolCheckedTick = int.MinValue;
		private bool poolAny;

		/// <summary>PANNING_SPOT_VERIFY_EMPTY_RIVER (GPT C5-F7): does the map's rock still hold a placer mineral to draw
		/// (RM_PlacerDraw.Draw)? The stock's cap is saved, so mining every placer rock leaves stock but nothing to draw, and
		/// panning was offered forever for "rivercarriesnothing". Re-measured at most every 2500 ticks (a whole-map lister walk).</summary>
		public bool PoolAny
		{
			get
			{
				int now = Find.TickManager.TicksGame;
				if (poolCheckedTick == int.MinValue || now - poolCheckedTick >= 2500 || now < poolCheckedTick)
				{
					poolCheckedTick = now;
					poolAny = RM_PlacerDraw.Pool(map).Count > 0;
				}
				return poolAny;
			}
		}

		private void Ensure()
		{
			if (units < 0f)
			{
				units = RM_PlacerDraw.PlacerUnits(map);   // a fresh map, or an old save whose cap could not be inverted
			}
			float cap = CapNow;
			if (stock < 0f)
			{
				stock = cap;
				lastTick = Find.TickManager.TicksGame;
			}
			else if (stock > cap)
			{
				stock = cap;   // the setting was lowered
			}
		}

		public override void ExposeData()
		{
			Scribe_Values.Look(ref stock, "RM_placerStock", -1f);
			Scribe_Values.Look(ref units, "RM_placerUnits", -1f);
			if (Scribe.mode == LoadSaveMode.LoadingVars && units < 0f)
			{
				// A save from before the base was scribed holds only the cap; recover the base from it rather than
				// re-basing on whatever rock is still standing now (mining since would shrink the cap silently).
				float legacyCap = -1f;
				Scribe_Values.Look(ref legacyCap, "RM_placerCap", -1f);
				units = RM_PlacerMath.UnitsFromCap(legacyCap, RM_QuarrySettings.placerStockPercent);
			}
			Scribe_Values.Look(ref lastTick, "RM_placerLastTick", -1);
			Scribe_Values.Look(ref floodWas, "RM_placerFloodWas", false);
			Scribe_Values.Look(ref SluiceUnits, "RM_placerSluiceUnits", 0);
			Scribe_Values.Look(ref PanUnits, "RM_placerPanUnits", 0);
			Scribe_Values.Look(ref Refills, "RM_placerRefills", 0);
		}

		public override void MapComponentTick()
		{
			int now = Find.TickManager.TicksGame;
			if (now % 2500 != 0 || stock < 0f)
			{
				return; // nothing to regrow until a sluice or panner first asks
			}
			Ensure();
			stock = RM_PlacerMath.Regrow(stock, CapNow, now - lastTick);
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
			stock = CapNow;
			Refills++;
		}

		/// <summary>How many of <paramref name="want"/> whole units the stock could give, without taking them.</summary>
		public int Available(int want)
		{
			Ensure();
			return RM_PlacerMath.Take(stock, want);
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
			StringBuilder sb = new StringBuilder("PLACER stock=" + stock.ToString("F1") + " cap=" + CapNow.ToString("F1")
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
			// place first, debit after: a full bank keeps its units in the river, and only what was placed is taken
			int got = stock?.Available(want) ?? 0;
			if (got <= 0)
			{
				return LastResult = "sluice=stockspent";
			}
			Thing t = ThingMaker.MakeThing(def);
			t.stackCount = Mathf.Min(got, def.stackLimit);
			got = t.stackCount;
			bool placedAll = GenPlace.TryPlaceThing(t, BankCell, Map, ThingPlaceMode.Near);
			if (!placedAll)
			{
				// Near can merge part of the stack and still return false: charge what landed, refuse only if nothing did
				got -= t.Destroyed ? 0 : t.stackCount;
				if (got <= 0)
				{
					return LastResult = "sluice=noroom";
				}
			}
			stock.Take(got);
			stock.SluiceUnits += got;
			return LastResult = "sluice=" + def.defName + "x" + got + " lane=" + lane;
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			IntVec3 w = WaterCell;
			string lane = !w.IsValid ? "no water" : (RM_PlacerWater.LaneAt(Map, w) == RM_RiverMath.LaneMargin ? "washing" : "water too calm to wash");
			RM_MapComponent_PlacerStock stock = RM_MapComponent_PlacerStock.Of(Map);
			string line = "Sluice box: " + lane + (stock != null ? ", river stock " + stock.Stock.ToString("F0") + "/" + stock.Cap.ToString("F0") : "");
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
			return stock == null || stock.Stock < 1f || !stock.PoolAny;
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
			AddFinishAction(cond => RM_PanWatch.Ended(job, cond));
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
				RM_PanWatch.PanTick(job, pawn);
			};
			yield return pan;
			Toil finish = ToilMaker.MakeToil("PanForPlacerFinish");
			finish.initAction = delegate
			{
				// the watch reads the stock book across exactly this session (the 2500-tick regrow cannot land inside it)
				RM_MapComponent_PlacerStock st = RM_MapComponent_PlacerStock.Of(Map);
				float s0 = st?.Stock ?? 0f;
				int p0 = st?.PanUnits ?? 0;
				string res = RM_PlacerPanning.Session(pawn);
				RM_PanWatch.Finished(job, res, st == null ? float.NaN : s0 - st.Stock, st == null ? -1 : st.PanUnits - p0);
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}

	/// <summary>GOLD_PANNING_PROVE_THE_COLONIST_STAYS: what ONE armed pan job did, tick by tick, so the placer chain can read
	/// that a colonist the WorkGiver sent stood on the bank cell for the whole session, finished it once, and what landed.
	/// Unarmed (JobId -1, the shipped state) every hook is one int compare.</summary>
	public static class RM_PanWatch
	{
		public static int JobId = -1;
		public static int PanTicks;
		public static int OnSpot;
		public static int OffSpot;
		public static int Sessions;
		public static string Result = "none";
		public static float Fell = float.NaN;
		public static int BookPanned = -1;
		public static readonly List<string> Ends = new List<string>();

		public static void Arm(Job job)
		{
			JobId = job.loadID;
			PanTicks = OnSpot = OffSpot = Sessions = 0;
			Result = "none";
			Fell = float.NaN;
			BookPanned = -1;
			Ends.Clear();
		}

		public static void Disarm()
		{
			JobId = -1;
		}

		public static void PanTick(Job job, Pawn pawn)
		{
			if (job.loadID != JobId)
			{
				return;
			}
			PanTicks++;
			if (pawn.Position == job.targetA.Cell)
			{
				OnSpot++;
			}
			else
			{
				OffSpot++;
			}
		}

		public static void Finished(Job job, string result, float fell, int bookPanned)
		{
			if (job.loadID == JobId)
			{
				Sessions++;
				Result = result;
				Fell = fell;
				BookPanned = bookPanned;
			}
		}

		public static void Ended(Job job, JobCondition cond)
		{
			if (job.loadID == JobId)
			{
				Ends.Add(cond.ToString());
			}
		}

		public static string Report()
		{
			return "panTicks=" + PanTicks + " onSpot=" + OnSpot + " offSpot=" + OffSpot + " sessions=" + Sessions
				+ " result=" + Result + " fell=" + Fell.ToString("F2") + " bookPanned=" + BookPanned + " ends=" + (Ends.Count == 0 ? "-" : string.Join(",", Ends));
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
			// place first, debit after (as the sluice): a failed placement leaves the stock untouched
			int got = stock.Available(want);
			if (got <= 0)
			{
				return "pan=stockspent";
			}
			Thing t = ThingMaker.MakeThing(def);
			t.stackCount = Mathf.Min(got, def.stackLimit);
			got = t.stackCount;
			if (!GenPlace.TryPlaceThing(t, pawn.Position, map, ThingPlaceMode.Near))
			{
				// Near can merge part of the stack and still return false: charge what landed, refuse only if nothing did
				got -= t.Destroyed ? 0 : t.stackCount;
				if (got <= 0)
				{
					return "pan=noroom";
				}
			}
			stock.Take(got);
			stock.PanUnits += got;
			Messages.Message(pawn.LabelShort + " panned " + got + " " + def.label + " out of the river.", t, MessageTypeDefOf.SilentInput, false);
			return "pan=" + def.defName + "x" + got;
		}
	}

	/// <summary>static_call surface. "" reports the stock; "wash" forces every sluice's daily wash; "refill" refills
	/// the stock as a flood would; "drain" empties it; "pan" runs one finished session for the first colonist on a spot;
	/// "jobstart" / "jobread" / "jobclean" stage, read and remove one REAL pan job (the WorkGiver's offer, walked and waited).</summary>
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
				case "jobstart":
					return JobStart(map, stock);
				case "jobread":
					return JobRead(map, stock);
				case "jobclean":
					return JobClean(map, stock);
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

		private static Pawn jobPawn;
		private static Thing jobSpot;
		private static int jobPriorityWas;
		private static HashSet<Thing> jobAlready;

		/// <summary>"jobstart": the live pan job (GOLD_PANNING_PROVE_THE_COLONIST_STAYS). Picks the nearest legal bank
		/// cell to a free colonist who can mine, builds a panning spot there, refills the stock, gives the colonist
		/// Mining priority 1 and full needs (so hunger or sleep does not pull them off mid-test), asks the REAL
		/// WorkGiver (ShouldSkip / HasJobOnThing / JobOnThing) and starts the job it offers, armed in RM_PanWatch.
		/// The caller then advances ticks and reads "jobread"; "jobclean" removes the spot and what was panned.</summary>
		private static string JobStart(Map map, RM_MapComponent_PlacerStock stock)
		{
			if (jobSpot != null)
			{
				JobClean(map, stock);
			}
			ThingDef def = RM_QuarryDefOf.RM_PanningSpot;
			WorkGiverDef wgd = DefDatabase<WorkGiverDef>.GetNamedSilentFail("RM_PanForPlacer");
			RM_WorkGiver_PanForPlacer wg = wgd?.Worker as RM_WorkGiver_PanForPlacer;
			if (wg == null)
			{
				return "REFUSED: WorkGiverDef RM_PanForPlacer has no RM_WorkGiver_PanForPlacer worker";
			}
			Pawn pawn = null;
			IntVec3 site = IntVec3.Invalid;
			int best = int.MaxValue;
			foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
			{
				if (p.Downed || p.Drafted || p.InMentalState || p.WorkTypeIsDisabled(WorkTypeDefOf.Mining) || p.workSettings == null)
				{
					continue;
				}
				foreach (IntVec3 c in map.AllCells)
				{
					int d = (c - p.Position).LengthHorizontalSquared;
					if (d >= best || !c.Standable(map) || c.Fogged(map)
						|| !new RM_PlaceWorker_PanningSpot().AllowsPlacing(def, c, Rot4.North, map).Accepted
						|| !GenConstruct.CanPlaceBlueprintAt(def, c, Rot4.North, map, false, null, null, null).Accepted
						|| !p.CanReach(c, PathEndMode.OnCell, Danger.Some))
					{
						continue;
					}
					best = d;
					site = c;
					pawn = p;
				}
				if (pawn != null)
				{
					break;
				}
			}
			if (pawn == null)
			{
				return "UNMEASURED: no free colonist able to mine reaches a legal panning bank cell | " + stock.Report();
			}
			jobAlready = new HashSet<Thing>(map.listerThings.AllThings);
			Thing spot = ThingMaker.MakeThing(def, GenStuff.DefaultStuffFor(def));
			spot.SetFaction(Faction.OfPlayer);
			jobSpot = GenSpawn.Spawn(spot, site, map, Rot4.North);
			jobPawn = pawn;
			stock.Refill();
			jobPriorityWas = pawn.workSettings.GetPriority(WorkTypeDefOf.Mining);
			pawn.workSettings.SetPriority(WorkTypeDefOf.Mining, 1);
			if (pawn.needs != null)
			{
				foreach (Need n in pawn.needs.AllNeeds)
				{
					if (n is Need_Food || n is Need_Rest || n is Need_Joy)
					{
						n.CurLevelPercentage = 1f;
					}
				}
			}
			bool skip = wg.ShouldSkip(pawn, false);
			bool has = !skip && wg.HasJobOnThing(pawn, jobSpot, false);
			string head = "jobstart pawn=" + pawn.LabelShort.Replace(' ', '_') + " spot=" + site.x + "," + site.z
				+ " dist=" + Mathf.Sqrt(best).ToString("F1") + " mining=" + (pawn.skills?.GetSkill(SkillDefOf.Mining)?.Level ?? 0)
				+ " ticksWanted=" + RM_PlacerMath.PanTicks(pawn.GetStatValue(StatDefOf.MiningSpeed))
				+ " shouldSkip=" + skip + " hasJob=" + has;
			if (!has)
			{
				return head + " started=False | " + stock.Report();
			}
			Job job = wg.JobOnThing(pawn, jobSpot, false);
			job.workGiverDef = wgd;
			RM_PanWatch.Arm(job);
			pawn.jobs.StartJob(job, JobCondition.InterruptForced, null, false, true);
			bool started = pawn.CurJob == job;
			return head + " started=" + started + " | " + stock.Report();
		}

		/// <summary>"jobread": the armed job's watch plus where the colonist is and what they are doing now.</summary>
		private static string JobRead(Map map, RM_MapComponent_PlacerStock stock)
		{
			if (jobPawn == null || jobSpot == null || !jobSpot.Spawned || jobSpot.Map != map)
			{
				return "UNMEASURED: no pan job staged on this map (call jobstart first) | " + stock.Report();
			}
			return "jobread curJob=" + (jobPawn.CurJobDef?.defName ?? "none") + " onSpotNow=" + (jobPawn.Position == jobSpot.Position)
				+ " " + RM_PanWatch.Report() + " | " + stock.Report();
		}

		/// <summary>"jobclean": end the job if it still runs, restore the Mining priority, remove the spot and the items
		/// that appeared since jobstart, disarm the watch.</summary>
		private static string JobClean(Map map, RM_MapComponent_PlacerStock stock)
		{
			string watch = RM_PanWatch.Report();
			RM_PanWatch.Disarm();
			int removed = 0;
			// statics outlive a game load: touch only what is still spawned on THIS map
			if (jobPawn != null && jobPawn.Spawned && jobPawn.Map == map)
			{
				if (jobPawn.CurJobDef == RM_QuarryDefOf.RM_PanForPlacerJob)
				{
					jobPawn.jobs.EndCurrentJob(JobCondition.InterruptForced);
				}
				jobPawn.workSettings?.SetPriority(WorkTypeDefOf.Mining, jobPriorityWas);
			}
			if (jobAlready != null && jobSpot != null && jobSpot.Spawned && jobSpot.Map == map)
			{
				List<Thing> made = new List<Thing>();
				foreach (Thing t in map.listerThings.AllThings)
				{
					if (!jobAlready.Contains(t) && t.def.category == ThingCategory.Item)
					{
						made.Add(t);
					}
				}
				foreach (Thing t in made)
				{
					t.Destroy();
					removed++;
				}
			}
			if (jobSpot != null && jobSpot.Spawned && jobSpot.Map == map)
			{
				jobSpot.Destroy();
			}
			jobPawn = null;
			jobSpot = null;
			jobAlready = null;
			return "jobclean removed=" + removed + " " + watch + " | " + stock.Report();
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
				// "sluice=<defName>x<count> lane=<n>": the count's 'x' is the LAST one before " lane=" (a defName may hold an x)
				int sp = res.IndexOf(" lane=");
				int x = sp > 0 ? res.LastIndexOf('x', sp) : -1;
				if (res.StartsWith("sluice=") && x > 7)
				{
					string name = res.Substring(7, x - 7);
					ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(name);
					inPool &= d != null && pool.ContainsKey(d);
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
