using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.RiverWorks
{
	/// <summary>
	/// The weir's arrest marker (moved from TerminalBiomes' CompChannelArrester, slice 2). A spawned
	/// thing carrying an Active one stops the carry dead on every cell it occupies, on the surface
	/// current AND on the sea's channel current (TerminalBiomes reads this comp).
	/// </summary>
	public class RM_CompProperties_RiverArrester : CompProperties
	{
		public RM_CompProperties_RiverArrester()
		{
			compClass = typeof(RM_CompRiverArrester);
		}
	}

	public class RM_CompRiverArrester : ThingComp
	{
		private bool active = true;

		public bool Active
		{
			get => active;
			set
			{
				if (active == value)
				{
					return;
				}
				active = value;
				parent?.MapHeld?.GetComponent<RM_MapComponent_RiverCurrent>()?.MarkWorksDirty();
			}
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref active, "riverArresterActive", true);
		}

		public static bool CellArrested(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return false;
			}
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				RM_CompRiverArrester comp = (things[i] as ThingWithComps)?.GetComp<RM_CompRiverArrester>();
				if (comp != null && comp.Active)
				{
					return true;
				}
			}
			return false;
		}
	}

	/// <summary>
	/// Design §3.3: the weir straddles the bank edge like the watermill - exactly one cell in moving
	/// water, exactly one on solid (Light-affordance) ground. Rotation-agnostic: it counts the
	/// occupied rect rather than assuming which end is which.
	/// </summary>
	public class RM_PlaceWorker_RiverWeir : PlaceWorker
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
				if (RM_RiverWorks.IsWaterCell(map, c))
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
				return new AcceptanceReport("A weir must straddle the bank: one end in moving water, one on solid ground.");
			}
			return true;
		}
	}

	/// <summary>
	/// The weir (TWILIGHT_CHANNEL_CURRENT_1 §4, moved here and reworked for SURFACE_RIVER_WEIRS_1).
	/// Owner rulings applied: calms ~8 cells upstream (card 2); catches fish from the river's own stock
	/// plus BIOME-RELEVANT drift (card 2, RM_RiverDriftDef); a breach washes the held catch a few cells
	/// downstream (ruling 4); the stake-line below it snaps in downstream order. Maintenance rides
	/// vanilla Repair (wear) and Haul (catch) - no new jobs. All numbers PROVISIONAL (settings).
	/// </summary>
	public class RM_Building_BankWeir : Building
	{
		private const int WearIntervalTicks = 2000;
		private const int BreachDurationTicks = 2500;
		private const float StakeCascadeRadius = 15f;
		private const float HeldCatchRadius = 2.5f;
		// PROVISIONAL: chance of a fish per catch interval at full stock; scales with stock fraction.
		private const float CatchChanceAtFullStock = 0.8f;
		private const float UncommonFishChance = 0.1f;

		/// <summary>The sea Compact's own pre-placed weir never breaches (set by TerminalBiomes' genstep).</summary>
		public bool neverBreaches;

		private bool breaching;
		private int breachEndTick;
		private int nextCatchTick = -1;
		private float wearDebt;
		private List<Thing> cascadeStakes;
		private List<int> cascadeFireTicks;

		private IntVec3 waterCell = IntVec3.Invalid;
		private IntVec3 bankCell = IntVec3.Invalid;

		private RM_CompRiverArrester arrester;

		public RM_CompRiverArrester Arrester => arrester ?? (arrester = GetComp<RM_CompRiverArrester>());

		public bool ArrestActive => Arrester == null || Arrester.Active;

		public bool Breaching => breaching;

		public IntVec3 WaterCell
		{
			get
			{
				ResolveEnds();
				return waterCell;
			}
		}

		public IntVec3 BankCell
		{
			get
			{
				ResolveEnds();
				return bankCell;
			}
		}

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			waterCell = IntVec3.Invalid;
			map.GetComponent<RM_MapComponent_RiverCurrent>()?.MarkWorksDirty();
		}

		public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
		{
			Map map = Map;
			base.DeSpawn(mode);
			map?.GetComponent<RM_MapComponent_RiverCurrent>()?.MarkWorksDirty();
		}

		private void ResolveEnds()
		{
			if (waterCell.IsValid || !Spawned)
			{
				return;
			}
			foreach (IntVec3 c in this.OccupiedRect())
			{
				if (!waterCell.IsValid && RM_RiverWorks.IsWaterCell(Map, c))
				{
					waterCell = c;
				}
				else
				{
					bankCell = c;
				}
			}
			if (!waterCell.IsValid)
			{
				waterCell = Position; // a genstep-placed sea weir on dry bed: both ends are "the weir"
			}
			if (!bankCell.IsValid)
			{
				bankCell = Position;
			}
		}

		protected override void Tick()
		{
			base.Tick();
			if (!RM_RiverWorksSettings.WorksActive)
			{
				return;
			}
			if (breaching)
			{
				TickBreach();
				return;
			}
			if (this.IsHashIntervalTick(WearIntervalTicks) && HitPoints > 1)
			{
				wearDebt += RM_RiverWorksSettings.wearRateMultiplier;
				int n = (int)wearDebt;
				if (n > 0)
				{
					wearDebt -= n;
					HitPoints = System.Math.Max(1, HitPoints - n); // the current's ordinary gnaw
				}
			}
			if (this.IsHashIntervalTick(600))
			{
				bool sound = HitPoints >= MaxHitPoints * RM_RiverWorksSettings.breachHpFraction;
				if (Arrester != null && !Arrester.Active && sound)
				{
					Arrester.Active = true; // repaired since the breach: catches again
				}
				bool alreadyBroken = Arrester != null && !Arrester.Active;
				if (RM_RiverWorksSettings.breachEnabled && !neverBreaches && !sound && !alreadyBroken
					&& RM_RiverWorks.FloodActive(Map))
				{
					Breach();
					return;
				}
			}
			int now = Find.TickManager.TicksGame;
			if (nextCatchTick < 0)
			{
				nextCatchTick = now + CatchIntervalTicks();
			}
			else if (now >= nextCatchTick)
			{
				nextCatchTick = now + CatchIntervalTicks();
				if (ArrestActive)
				{
					TryCatch();
				}
			}
		}

		private static int CatchIntervalTicks()
		{
			return Mathf.Max(250, Mathf.RoundToInt(RM_RiverWorksSettings.weirCatchIntervalHours * 2500f));
		}

		// ── catch ────────────────────────────────────────────────────────────

		/// <summary>One catch roll. Public so the first script can force it. Returns what happened.</summary>
		public string TryCatch()
		{
			string fishResult = "fish=off";
			if (RM_RiverWorksSettings.weirCatchesFish)
			{
				fishResult = TryCatchFish();
			}
			string driftResult = "drift=off";
			if (RM_RiverWorksSettings.weirCatchesDrift)
			{
				driftResult = Rand.Chance(RM_RiverWorksSettings.weirDriftChance) ? TryCatchDrift() : "drift=missed";
			}
			return fishResult + " " + driftResult;
		}

		private string TryCatchFish()
		{
			WaterBodyTracker tracker = Map.waterBodyTracker;
			WaterBody body = tracker?.WaterBodyAt(WaterCell);
			if (body == null || !body.HasFish)
			{
				return "fish=nostock";
			}
			float pct = Mathf.Clamp01(tracker.PopulationPercentAt(WaterCell));
			if (!Rand.Chance(CatchChanceAtFullStock * pct))
			{
				return "fish=missed";
			}
			ThingDef fish = null;
			if (Rand.Chance(UncommonFishChance))
			{
				body.UncommonFish.TryRandomElement(out fish);
			}
			if (fish == null)
			{
				body.CommonFish.TryRandomElement(out fish);
			}
			if (fish == null)
			{
				return "fish=nofishtype";
			}
			int count = Rand.RangeInclusive(2, 5); // PROVISIONAL
			int placed = Deposit(fish, count);
			if (placed <= 0)
			{
				return "fish=full";
			}
			// One stock, two drains: the fishing zone on this river now finds less.
			tracker.Notify_Fished(WaterCell, placed);
			return "fish=" + fish.defName + "x" + placed;
		}

		private string TryCatchDrift()
		{
			RM_RiverDriftEntry e = RM_RiverDriftDef.RollFor(Map.Biome);
			if (e == null || e.thing == null)
			{
				return "drift=nonefor:" + Map.Biome?.defName;
			}
			int placed = Deposit(e.thing, e.count.RandomInRange);
			return placed > 0 ? "drift=" + e.thing.defName + "x" + placed : "drift=full";
		}

		/// <summary>Everything loose within reach of the weir counts as its held catch.</summary>
		public List<Thing> HeldCatch()
		{
			List<Thing> held = new List<Thing>();
			if (!Spawned)
			{
				return held;
			}
			foreach (Thing t in GenRadial.RadialDistinctThingsAround(Position, Map, HeldCatchRadius, true))
			{
				if (t.def.EverHaulable && !(t is Pawn) && t.def.category == ThingCategory.Item)
				{
					held.Add(t);
				}
			}
			return held;
		}

		private int Deposit(ThingDef def, int count)
		{
			int held = 0;
			List<Thing> h = HeldCatch();
			for (int i = 0; i < h.Count; i++)
			{
				held += h[i].stackCount;
			}
			int room = RM_RiverWorksSettings.weirHeldCatchCap - held;
			if (room <= 0 || count <= 0)
			{
				return 0;
			}
			Thing t = ThingMaker.MakeThing(def);
			t.stackCount = Mathf.Min(count, room, def.stackLimit);
			int n = t.stackCount;
			return GenPlace.TryPlaceThing(t, BankCell, Map, ThingPlaceMode.Near) ? n : 0;
		}

		// ── breach ───────────────────────────────────────────────────────────

		/// <summary>The untended-weir-meets-flood cascade. Public for the first script.</summary>
		public void Breach()
		{
			breaching = true;
			breachEndTick = Find.TickManager.TicksGame + BreachDurationTicks;
			int washed = RM_RiverWorksSettings.breachWashesCatch ? WashCatch() : 0;
			if (Arrester != null)
			{
				Arrester.Active = false; // pool and arrest off; on the sea the channel re-carries what sat here
			}
			Messages.Message(LabelShortCap + " has breached - untended, and the flood found it."
				+ (washed > 0 ? " Its catch is washing downstream." : ""), this, MessageTypeDefOf.ThreatBig);
			ScheduleStakeCascade();
			RevertNearbySiltTraps();
		}

		/// <summary>Owner ruling 4: the held catch rides the current a few cells and strands on the
		/// nearest bank. Needs the surface flow; on the sea (no river flow here) it is left for the
		/// channel current to carry, exactly as before the move.</summary>
		private int WashCatch()
		{
			RM_MapComponent_RiverCurrent comp = Map.GetComponent<RM_MapComponent_RiverCurrent>();
			if (comp == null || comp.FlowDirAt(WaterCell) < 0)
			{
				return 0;
			}
			IntVec3 end = WaterCell;
			for (int i = 0; i < RM_RiverWorksSettings.breachWashCells; i++)
			{
				int dir = comp.FlowDirAt(end);
				if (dir < 0)
				{
					break;
				}
				IntVec3 next = new IntVec3(end.x + RM_RiverMath.StepX[dir], 0, end.z + RM_RiverMath.StepZ[dir]);
				if (!next.InBounds(Map))
				{
					break;
				}
				end = next;
			}
			IntVec3 strand = IntVec3.Invalid;
			foreach (IntVec3 c in GenRadial.RadialCellsAround(end, 8f, true))
			{
				if (c.InBounds(Map) && c.Standable(Map) && comp.FlowDirAt(c) < 0)
				{
					strand = c;
					break;
				}
			}
			if (!strand.IsValid)
			{
				return 0;
			}
			List<Thing> held = HeldCatch();
			int moved = 0;
			for (int i = 0; i < held.Count; i++)
			{
				Thing t = held[i];
				if (t.Destroyed || !t.Spawned)
				{
					continue;
				}
				t.DeSpawn();
				if (GenPlace.TryPlaceThing(t, strand, Map, ThingPlaceMode.Near))
				{
					moved++;
				}
			}
			return moved;
		}

		private void TickBreach()
		{
			if (!this.IsHashIntervalTick(15))
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			if (cascadeFireTicks != null)
			{
				for (int i = cascadeFireTicks.Count - 1; i >= 0; i--)
				{
					if (now < cascadeFireTicks[i])
					{
						continue;
					}
					Thing stake = cascadeStakes[i];
					if (stake != null && !stake.Destroyed)
					{
						stake.TakeDamage(new DamageInfo(DamageDefOf.Deterioration, stake.MaxHitPoints));
					}
					cascadeStakes.RemoveAt(i);
					cascadeFireTicks.RemoveAt(i);
				}
			}
			if (now >= breachEndTick && (cascadeFireTicks == null || cascadeFireTicks.Count == 0))
			{
				breaching = false;
				if (Arrester != null)
				{
					Arrester.Active = HitPoints >= MaxHitPoints * RM_RiverWorksSettings.breachHpFraction;
				}
				cascadeStakes = null;
				cascadeFireTicks = null;
			}
		}

		/// <summary>The stake-line below the weir snaps post by post, nearest-downstream first. With a
		/// surface flow direction, stakes are ordered by how far downstream they lie (upstream ones are
		/// spared); with none (the sea), by distance, as before the move.</summary>
		private void ScheduleStakeCascade()
		{
			cascadeStakes = new List<Thing>();
			cascadeFireTicks = new List<int>();
			ThingDef stakeDef = RM_RiverWorksDefOf.RM_BankStake;
			if (Map == null || stakeDef == null)
			{
				return;
			}
			RM_MapComponent_RiverCurrent comp = Map.GetComponent<RM_MapComponent_RiverCurrent>();
			int dir = comp?.FlowDirAt(WaterCell) ?? -1;
			int now = Find.TickManager.TicksGame;
			foreach (Thing t in GenRadial.RadialDistinctThingsAround(Position, Map, StakeCascadeRadius, true))
			{
				if (t.def != stakeDef)
				{
					continue;
				}
				float order;
				if (dir >= 0)
				{
					order = RM_RiverMath.DownstreamDistance(t.Position.x - Position.x, t.Position.z - Position.z, dir);
					if (order < -1f)
					{
						continue; // upstream of the weir: the breach does not reach it
					}
					order = Mathf.Max(0f, order);
				}
				else
				{
					order = t.Position.DistanceTo(Position);
				}
				cascadeStakes.Add(t);
				cascadeFireTicks.Add(now + Mathf.RoundToInt(order) * RM_RiverWorksSettings.stakeSnapTicksPerCell);
			}
		}

		private void RevertNearbySiltTraps()
		{
			foreach (Thing t in GenRadial.RadialDistinctThingsAround(Position, Map, StakeCascadeRadius, true))
			{
				if (t is RM_Building_SiltTrap trap)
				{
					trap.Clog();
				}
			}
		}

		// ── the slack pool ───────────────────────────────────────────────────

		/// <summary>Owner card 2: the weir calms a long stretch (~8 cells) upstream. Walks upstream
		/// from the wet end along the flow, taking each step's two lateral neighbours too (a 3-wide
		/// pool, PROVISIONAL), so a colony can cross or work the river there.</summary>
		public void AddPoolCells(RM_MapComponent_RiverCurrent comp, HashSet<int> into)
		{
			if (!Spawned || !ArrestActive || breaching || RM_RiverWorksSettings.weirPoolLength <= 0)
			{
				return;
			}
			IntVec3 cur = WaterCell;
			for (int k = 0; k < RM_RiverWorksSettings.weirPoolLength; k++)
			{
				IntVec3 up = Upstream(comp, cur);
				if (!up.IsValid)
				{
					break;
				}
				int dir = comp.FlowDirAt(up);
				into.Add(Map.cellIndices.CellToIndex(up));
				if (dir >= 0)
				{
					int l = (dir + 2) % 8;
					int r = (dir + 6) % 8;
					IntVec3 a = new IntVec3(up.x + RM_RiverMath.StepX[l], 0, up.z + RM_RiverMath.StepZ[l]);
					IntVec3 b = new IntVec3(up.x + RM_RiverMath.StepX[r], 0, up.z + RM_RiverMath.StepZ[r]);
					if (a.InBounds(Map) && comp.FlowDirAt(a) >= 0) into.Add(Map.cellIndices.CellToIndex(a));
					if (b.InBounds(Map) && comp.FlowDirAt(b) >= 0) into.Add(Map.cellIndices.CellToIndex(b));
				}
				cur = up;
			}
		}

		private IntVec3 Upstream(RM_MapComponent_RiverCurrent comp, IntVec3 cur)
		{
			int curDir = comp.FlowDirAt(cur);
			IntVec3 best = IntVec3.Invalid;
			for (int i = 0; i < 8; i++)
			{
				IntVec3 n = cur + GenAdj.AdjacentCells[i];
				if (!n.InBounds(Map))
				{
					continue;
				}
				int d = comp.FlowDirAt(n);
				if (d < 0 || n.x + RM_RiverMath.StepX[d] != cur.x || n.z + RM_RiverMath.StepZ[d] != cur.z)
				{
					continue;
				}
				if (d == curDir)
				{
					return n;
				}
				if (!best.IsValid)
				{
					best = n;
				}
			}
			if (!best.IsValid && curDir >= 0)
			{
				IntVec3 back = new IntVec3(cur.x - RM_RiverMath.StepX[curDir], 0, cur.z - RM_RiverMath.StepZ[curDir]);
				if (back.InBounds(Map) && comp.FlowDirAt(back) >= 0)
				{
					best = back;
				}
			}
			return best;
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			string mine = breaching ? "Breached - the flood is through." : (ArrestActive ? "Holding." : "Broken: repair above "
				+ RM_RiverWorksSettings.breachHpFraction.ToStringPercent() + " to re-arm.");
			return s.NullOrEmpty() ? mine : s + "\n" + mine;
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref neverBreaches, "neverBreaches", false);
			Scribe_Values.Look(ref breaching, "breaching", false);
			Scribe_Values.Look(ref breachEndTick, "breachEndTick", 0);
			Scribe_Values.Look(ref nextCatchTick, "nextCatchTick", -1);
			Scribe_Values.Look(ref wearDebt, "wearDebt", 0f);
			Scribe_Collections.Look(ref cascadeStakes, "cascadeStakes", LookMode.Reference);
			Scribe_Collections.Look(ref cascadeFireTicks, "cascadeFireTicks", LookMode.Value);
			if (Scribe.mode == LoadSaveMode.PostLoadInit && cascadeStakes != null)
			{
				// a stake destroyed before the save loads back as null; drop it with its timer
				for (int i = cascadeStakes.Count - 1; i >= 0; i--)
				{
					if (cascadeStakes[i] == null && cascadeFireTicks != null && i < cascadeFireTicks.Count)
					{
						cascadeStakes.RemoveAt(i);
						cascadeFireTicks.RemoveAt(i);
					}
				}
			}
		}
	}

	[DefOf]
	public static class RM_RiverWorksDefOf
	{
		public static ThingDef RM_BankStake;
		public static ThingDef RM_BankWeir;
		public static ThingDef RM_SiltTrap;
		public static ThingDef RM_FerryPost;

		static RM_RiverWorksDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RM_RiverWorksDefOf));
		}
	}
}
