using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Rivers
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
				if (parent != null && parent.Spawned)
				{
					parent.DirtyMapMesh(parent.Map); // the weir's water overlay shows only while it holds
				}
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
	/// occupied rect rather than assuming which end is which. RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS (owner 2026-10-16,
	/// by card: "Weirs join into one continuous wall"): a section standing wholly in moving water is also allowed when it
	/// continues a run end to end on the same axis (a weir, its blueprint or its frame), so sections chain bank to bank.
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
			bool continues = water == 2 && RM_WeirRun.ContinuesRun(map, loc, rot, checkingDef.Size, thingToIgnore);
			if (!RM_RiverMath.WeirPlacementOk(water, bank, continues))
			{
				return new AcceptanceReport(water == 2
					? "A weir out in the current must continue a weir: set it end to end with one, on the same line."
					: "A weir must straddle the bank (one end in moving water, one on solid ground) or continue a weir out into the current.");
			}
			return true;
		}
	}

	/// <summary>
	/// The weir (TWILIGHT_CHANNEL_CURRENT_1 §4, moved here and reworked for SURFACE_RIVER_WEIRS_1).
	/// Owner rulings applied: calms ~8 cells upstream (card 2); catches ONLY what the current carries into it (owner
	/// 2026-10-23, WEIR_CATCH_FIX_NO_FREE_FISH: "they should just capture anything floating downstream. No auto fish
	/// capture." - the fish and biome-drift rolls are gone); a breach washes the held catch a few cells downstream
	/// (ruling 4); the stake-line below it snaps in downstream order. Maintenance rides vanilla Repair (wear) and Haul
	/// (catch) - no new jobs. All numbers PROVISIONAL (settings). Design: design/RimMandrake/weir_review_2026-10-23.md.
	/// </summary>
	public class RM_Building_BankWeir : Building
	{
		private const int WearIntervalTicks = 2000;
		private const int BreachDurationTicks = 2500;
		private const float StakeCascadeRadius = 15f;
		private const float HeldCatchRadius = 2.5f;
		// how often a holding section checks its intake for things the current brought (cheap: a handful of cells)
		private const int CaptureIntervalTicks = 250;
		private const int FoamFrames = 12;

		/// <summary>The sea Compact's own pre-placed weir never breaches (set by TerminalBiomes' genstep).</summary>
		public bool neverBreaches;

		/// <summary>Proof seam only (RM_RiverWorksProofWorks.ProofBreachNoRoom, A2 of
		/// WEIR_WASH_ITEM_LOSS_MEND_PLACE_FIRST): an extra cell validator handed to the wash's Near placement, so a
		/// live probe can make every strand cell refuse through the engine's own search. Null in play; the probe
		/// sets it around one Breach() call and clears it in a finally. Not saved.</summary>
		internal static Predicate<IntVec3> washPlaceValidator;

		private bool breaching;
		private int breachEndTick;
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
			RM_WeirRun.DirtyNeighbours(this, map); // their free-end posts become a joint
		}

		public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
		{
			Map map = Map;
			List<RM_Building_BankWeir> was = RM_WeirRun.Neighbours(this);
			base.DeSpawn(mode);
			map?.GetComponent<RM_MapComponent_RiverCurrent>()?.MarkWorksDirty();
			for (int i = 0; i < was.Count; i++)
			{
				was[i].DirtyMapMesh(map); // the joint they shared is a free end again
			}
		}

		// ── the joined run (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS, owner 2026-10-16 by card) ──

		/// <summary>True when one end of this section stands on solid ground (a bank straddler).</summary>
		public bool Anchored
		{
			get
			{
				if (!Spawned)
				{
					return false;
				}
				foreach (IntVec3 c in this.OccupiedRect())
				{
					if (!RM_RiverWorks.IsWaterCell(Map, c))
					{
						return true;
					}
				}
				return false;
			}
		}

		/// <summary>Every section joined to this one end to end on the same axis (this one first).</summary>
		public List<RM_Building_BankWeir> Run() => RM_RiverMath.WeirRun(this, w => RM_WeirRun.Neighbours(w), RM_WeirRun.MaxRun);

		/// <summary>The one section of the run that rolls the catch and holds it on its bank end.</summary>
		public RM_Building_BankWeir RunHead() => RM_RiverMath.WeirRunHead(Run(), w => w.Anchored, w => w.thingIDNumber);

		/// <summary>The run's pool stands only while every section holds (a gap leaks).</summary>
		public bool RunHolds()
		{
			List<RM_Building_BankWeir> run = Run();
			List<bool> sound = new List<bool>(run.Count);
			for (int i = 0; i < run.Count; i++)
			{
				sound.Add(run[i].ArrestActive && !run[i].Breaching);
			}
			return RM_RiverMath.WeirRunHolds(sound);
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
			if (!RM_RiversSettings.WorksActive)
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
				wearDebt += RM_RiversSettings.wearRateMultiplier;
				int n = (int)wearDebt;
				if (n > 0)
				{
					wearDebt -= n;
					HitPoints = System.Math.Max(1, HitPoints - n); // the current's ordinary gnaw
				}
			}
			if (this.IsHashIntervalTick(600))
			{
				bool sound = HitPoints >= MaxHitPoints * RM_RiversSettings.breachHpFraction;
				if (Arrester != null && !Arrester.Active && sound)
				{
					Arrester.Active = true; // repaired since the breach: catches again
				}
				bool alreadyBroken = Arrester != null && !Arrester.Active;
				if (RM_RiversSettings.breachEnabled && !neverBreaches && !sound && !alreadyBroken
					&& RM_RiverWorks.FloodActive(Map))
				{
					Breach();
					return;
				}
			}
			if (this.IsHashIntervalTick(CaptureIntervalTicks) && ArrestActive)
			{
				CaptureFloating();
			}
		}

		// ── catch: only what the river brings (weir review 2026-10-23) ─────────

		/// <summary>This section's intake cells: in-current cells whose flow step lands on its wall cells, i.e. where the
		/// surface carry stops a drifting thing (RM_RiverMath.WeirIntakeCells).</summary>
		public List<IntVec3> IntakeCells()
		{
			List<IntVec3> cells = new List<IntVec3>();
			RM_MapComponent_RiverCurrent comp = Spawned ? Map.GetComponent<RM_MapComponent_RiverCurrent>() : null;
			if (comp == null)
			{
				return cells;
			}
			List<int[]> wall = new List<int[]>();
			foreach (IntVec3 c in this.OccupiedRect())
			{
				wall.Add(new[] { c.x, c.z });
			}
			foreach (int[] k in RM_RiverMath.WeirIntakeCells(wall, (x, z) => comp.FlowDirAt(new IntVec3(x, 0, z))))
			{
				cells.Add(new IntVec3(k[0], 0, k[1]));
			}
			return cells;
		}

		/// <summary>Lifts every loose item or corpse lying in this section's intake onto the bank end of the run's head, up
		/// to the held-catch cap; past the cap things stay jammed against the wall. Creates nothing and never moves a living
		/// pawn. Placed only on ground with no current, so the catch never drifts off again; a failed placement puts the
		/// thing back where it lay. Public so the first script can force it. Returns how many stacks were lifted.</summary>
		public int CaptureFloating()
		{
			if (!RM_RiversSettings.weirCapturesFloating)
			{
				return 0;
			}
			if (!Spawned || breaching || !RM_RiversSettings.WorksActive)
			{
				return 0;
			}
			Map map = Map;
			List<Thing> offered = new List<Thing>();
			foreach (IntVec3 c in IntakeCells())
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				List<Thing> here = c.GetThingList(map);
				for (int i = 0; i < here.Count; i++)
				{
					Thing t = here[i];
					if (t.def.category == ThingCategory.Item && t.def.EverHaulable && !(t is Pawn) && !offered.Contains(t))
					{
						offered.Add(t);
					}
				}
			}
			if (offered.Count == 0)
			{
				return 0;
			}
			RM_Building_BankWeir head = RunHead() ?? this;
			int held = 0;
			List<Thing> h = head.HeldCatch();
			for (int i = 0; i < h.Count; i++)
			{
				if (!offered.Contains(h[i]))
				{
					held += h[i].stackCount;
				}
			}
			RM_MapComponent_RiverCurrent comp = map.GetComponent<RM_MapComponent_RiverCurrent>();
			Predicate<IntVec3> dry = c => comp == null || !comp.HasCurrent(c);
			int lifted = 0;
			for (int i = 0; i < offered.Count; i++)
			{
				Thing t = offered[i];
				if (RM_RiverMath.WeirCaptureBudget(held, RM_RiversSettings.weirHeldCatchCap, t.stackCount) < t.stackCount)
				{
					break; // full: the rest stays jammed against the wall until the catch is hauled
				}
				IntVec3 from = t.Position;
				int n = t.stackCount;
				t.DeSpawn();
				if (GenPlace.TryPlaceThing(t, head.BankCell, map, ThingPlaceMode.Near, null, dry))
				{
					held += n;
					lifted++;
				}
				else if (!t.Destroyed && !t.Spawned)
				{
					GenSpawn.Spawn(t, from, map); // no dry room: back where it lay, nothing lost
				}
			}
			return lifted;
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

		// ── breach ───────────────────────────────────────────────────────────

		/// <summary>The untended-weir-meets-flood cascade. Public for the first script.</summary>
		public void Breach()
		{
			breaching = true;
			breachEndTick = Find.TickManager.TicksGame + BreachDurationTicks;
			int washed = RM_RiversSettings.breachWashesCatch ? WashCatch() : 0;
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
			// WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME: walk downstream by the best-aligned in-flow neighbour, then strand
			// outside the held disc (RM_RiverMath.WashStrand), so HeldCatch() no longer counts the washed catch.
			Map map = Map;
			IntVec3 wet = WaterCell;
			if (!RM_RiverMath.WashStrand(wet.x, wet.z, Position.x, Position.z, RM_RiversSettings.breachWashCells,
				HeldCatchRadius, (x, z) => comp.FlowDirAt(new IntVec3(x, 0, z)),
				(x, z) => { IntVec3 c = new IntVec3(x, 0, z); return c.InBounds(map) && c.Standable(map); },
				out int sx, out int sz))
			{
				return 0;
			}
			IntVec3 strand = new IntVec3(sx, 0, sz);
			// A failed Near placement leaves the (remaining) stack unspawned; WashHeld puts it back where it
			// sat rather than orphan it. A part already merged into strand stacks still counts.
			return RM_RiverMath.WashHeld(HeldCatch(),
				t => !t.Destroyed && t.Spawned,
				t => t.Position,
				t => t.stackCount,
				t => t.DeSpawn(),
				t => GenPlace.TryPlaceThing(t, strand, Map, ThingPlaceMode.Near, null, washPlaceValidator),
				t => t.Destroyed,
				(t, from) => GenSpawn.Spawn(t, from, Map));
		}

		private void TickBreach()
		{
			if (!this.IsHashIntervalTick(15))
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			if (!RM_RiversSettings.breachEnabled)
			{
				// C6-F5: breach switched off mid-cascade: no further stake snaps, and the breach ends below this pass
				cascadeFireTicks?.Clear();
				cascadeStakes?.Clear();
				breachEndTick = now;
			}
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
					Arrester.Active = HitPoints >= MaxHitPoints * RM_RiversSettings.breachHpFraction;
				}
				cascadeStakes = null;
				cascadeFireTicks = null;
			}
		}

		/// <summary>Proof read (breach.cascade_order): the tick a stake is scheduled to snap at, or -1
		/// when the breach does not reach it.</summary>
		public int CascadeTickFor(Thing stake)
		{
			int i = cascadeStakes != null ? cascadeStakes.IndexOf(stake) : -1;
			return i >= 0 ? cascadeFireTicks[i] : -1;
		}

		public int FlowDirForProof
		{
			get
			{
				return Map?.GetComponent<RM_MapComponent_RiverCurrent>()?.FlowDirAt(WaterCell) ?? -1;
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
				float order = RM_RiverMath.StakeSnapOrder(t.Position.x - Position.x, t.Position.z - Position.z, dir);
				if (order < 0f)
				{
					continue; // upstream of the weir: the breach does not reach it
				}
				cascadeStakes.Add(t);
				cascadeFireTicks.Add(now + Mathf.RoundToInt(order) * RM_RiversSettings.stakeSnapTicksPerCell);
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
		/// from the wet end along the flow (RM_RiverMath.UpstreamWalk: any in-flow neighbour whose step onto
		/// the cell runs with the local current, so a bank-edge lane pools too), taking each step's two lateral
		/// neighbours as well (a 3-wide pool, PROVISIONAL), so a colony can cross or work the river there.</summary>
		public void AddPoolCells(RM_MapComponent_RiverCurrent comp, HashSet<int> into)
		{
			if (!Spawned || !ArrestActive || breaching || RM_RiversSettings.weirPoolLength <= 0 || !RunHolds())
			{
				return;
			}
			Map map = Map;
			Func<int, int, int> dirAt = (x, z) => comp.FlowDirAt(new IntVec3(x, 0, z)); // -1 out of bounds
			// a joined section out in the current has two wet cells: the pool rises behind both, so a run pools its width
			foreach (IntVec3 wet in this.OccupiedRect())
			{
				if (wet != WaterCell && !RM_RiverWorks.IsWaterCell(map, wet))
				{
					continue;
				}
				PoolFrom(comp, into, map, dirAt, wet);
			}
		}

		private static void PoolFrom(RM_MapComponent_RiverCurrent comp, HashSet<int> into, Map map, Func<int, int, int> dirAt, IntVec3 wet)
		{
			RM_RiverMath.UpstreamWalk(wet.x, wet.z, RM_RiversSettings.weirPoolLength, dirAt, (x, z) =>
			{
				IntVec3 up = new IntVec3(x, 0, z);
				into.Add(map.cellIndices.CellToIndex(up));
				int dir = comp.FlowDirAt(up);
				if (dir >= 0)
				{
					int l = (dir + 2) % 8;
					int r = (dir + 6) % 8;
					IntVec3 a = new IntVec3(x + RM_RiverMath.StepX[l], 0, z + RM_RiverMath.StepZ[l]);
					IntVec3 b = new IntVec3(x + RM_RiverMath.StepX[r], 0, z + RM_RiverMath.StepZ[r]);
					if (comp.FlowDirAt(a) >= 0) into.Add(map.cellIndices.CellToIndex(a));
					if (comp.FlowDirAt(b) >= 0) into.Add(map.cellIndices.CellToIndex(b));
				}
			});
		}

		// ── art (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS, owner 2026-10-16: "(1) but in the four art styles") ──
		// A low timber wall per heading (Graphic_Multi _north/_east/_south/_west in the section's look), its facing taken
		// from the current so the spill face is always downstream. Body textures are seamless along the wall, so joined
		// sections read as one wall; a stout post is drawn only at a free end. <look>/RM_BankWeirSpill_<facing> (the sheet
		// over the crest) is printed on water cells while the weir holds. Weir review 2026-10-23 (owner: "Static white water
		// that doesn't match anything. (needs to be an animated effect). A single blue tint above it."): the flat 1x3
		// RM_BankWeirWater strip (pool tint + frozen foam) is gone - the current model has no raised level to tint - and
		// the white water is a real-time flip-book (DrawAt), only where the current crosses the wall, scaled to the flow.

		/// <summary>The facing the art is drawn in (RM_RiverMath.WeirArtRot): the placed axis, its downstream side from the
		/// current at the wet end.</summary>
		public Rot4 ArtRot
		{
			get
			{
				int flow = Spawned ? Map.GetComponent<RM_MapComponent_RiverCurrent>()?.FlowDirAt(WaterCell) ?? -1 : -1;
				return new Rot4(RM_RiverMath.WeirArtRot(Rotation.AsInt, flow));
			}
		}

		public override void Print(SectionLayer layer)
		{
			Graphic g = Graphic;
			Rot4 rot = ArtRot;
			if (g == null || def.dontPrint)
			{
				base.Print(layer);
				return;
			}
			Vector3 center = this.TrueCenter();
			Vector2 size = rot.IsHorizontal ? g.drawSize.Rotated() : g.drawSize;
			bool flip = (rot == Rot4.West && g.WestFlipped) || (rot == Rot4.East && g.EastFlipped);
			Printer_Plane.PrintPlane(layer, center, size, g.MatAt(rot, this), 0f, flip);

			string basePath = StyleDef?.graphicData?.texPath ?? def.graphicData?.texPath;
			bool holding = ArrestActive && !breaching && RM_RiversSettings.WorksActive;
			if (holding)
			{
				Material spill = basePath == null ? null : RM_WeirArt.Mat(basePath + "Spill_" + RM_WeirArt.FacingName(rot), ShaderDatabase.Transparent);
				foreach (IntVec3 c in this.OccupiedRect())
				{
					if (!RM_RiverWorks.IsWaterCell(Map, c))
					{
						continue;
					}
					Vector3 cc = c.ToVector3Shifted();
					if (spill != null)
					{
						Vector3 sc = rot.IsHorizontal ? new Vector3(cc.x, center.y + Altitudes.AltInc * 0.25f, center.z)
							: new Vector3(center.x, center.y + Altitudes.AltInc * 0.25f, cc.z);
						Printer_Plane.PrintPlane(layer, sc, Vector2.one, spill);
					}
				}
			}
			Material cap = basePath == null ? null : RM_WeirArt.Mat(basePath + "Cap", ShaderDatabase.Cutout);
			if (cap != null)
			{
				CellRect r = this.OccupiedRect();
				bool lowJoined = RM_WeirRun.JoinedAt(this, false);
				bool highJoined = RM_WeirRun.JoinedAt(this, true);
				float capY = center.y + Altitudes.AltInc * 0.5f;
				Vector2 capSize = new Vector2(RM_WeirArt.CapSize, RM_WeirArt.CapSize);
				if (rot.IsHorizontal)
				{
					if (!lowJoined) Printer_Plane.PrintPlane(layer, new Vector3(r.minX, capY, center.z + RM_WeirArt.CapLift), capSize, cap);
					if (!highJoined) Printer_Plane.PrintPlane(layer, new Vector3(r.maxX + 1f, capY, center.z + RM_WeirArt.CapLift), capSize, cap);
				}
				else
				{
					if (!lowJoined) Printer_Plane.PrintPlane(layer, new Vector3(center.x, capY, r.minZ + RM_WeirArt.CapLift), capSize, cap);
					if (!highJoined) Printer_Plane.PrintPlane(layer, new Vector3(center.x, capY + Altitudes.AltInc * 0.1f, r.maxZ + 1f + RM_WeirArt.CapLift), capSize, cap);
				}
			}
		}

		/// <summary>The animated white water (drawerType MapMeshAndRealTime: the wall, posts and crest sheet are in the map
		/// mesh; only the foam is drawn per frame, so base.DrawAt is NOT called - it would draw the wall twice). One plane per
		/// wet section cell whose downstream neighbour is water, rotated so the crest edge sits on the wall and the foam runs
		/// downstream; strength, speed and reach from the lane under it (RM_RiverMath.WeirFoam), frame from real time so it
		/// moves like vanilla river water, also while paused.</summary>
		protected override void DrawAt(Vector3 drawLoc, bool flip = false)
		{
			if (RM_RiversSettings.weirWhiteWater && RM_RiversSettings.WorksActive && Spawned && ArrestActive && !breaching)
			{
				DrawWhiteWater();
			}
		}

		private void DrawWhiteWater()
		{
			Map map = Map;
			RM_MapComponent_RiverCurrent comp = map.GetComponent<RM_MapComponent_RiverCurrent>();
			if (comp == null || !RM_RiverMath.WeirFoamStep(Rotation.AsInt, comp.FlowDirAt(WaterCell), out int dx, out int dz))
			{
				return; // the current runs along the wall, or there is none: nothing falls over it
			}
			bool surge = comp.SurgeActive; // read, not recomputed: the component refreshes it every scan
			float y = AltitudeLayer.FloorEmplacement.AltitudeFor();
			// the frames are drawn crest-at-top, falling south (-z); turn them to fall along (dx, dz)
			Quaternion turn = Quaternion.Euler(0f, dz < 0 ? 0f : dz > 0 ? 180f : dx > 0 ? 270f : 90f, 0f);
			RM_RiverMath.WeirFoamLeft(dx, dz, out int lx, out int lz);
			float pace = RM_RiverMath.WeirFoam(RM_RiverMath.LaneCentre, surge).fps;
			foreach (IntVec3 c in this.OccupiedRect())
			{
				if (!FallsAt(map, c, dx, dz))
				{
					continue;
				}
				RM_RiverMath.WeirFoamLook look = RM_RiverMath.WeirFoam(comp.LaneAt(new IntVec3(c.x + dx, 0, c.z + dz)), surge);
				if (look.alpha <= 0f)
				{
					continue;
				}
				// one clock for every section (phase 0, the centre lane's pace): joined sections show the same frame, so the
				// tileable sheet has no seam; the lane changes only how strong the foam reads
				int frame = RM_RiverMath.WeirFoamFrame(Time.realtimeSinceStartup, pace, FoamFrames, 0);
				// an end of the white water (no foam beside it along the wall) is drawn broken, not cut straight
				string end = RM_RiverMath.WeirFoamSuffix(FoamBeside(map, c, lx, lz, dx, dz), FoamBeside(map, c, -lx, -lz, dx, dz));
				Material mat = RM_WeirArt.Foam(frame, end, look.alpha);
				if (mat == null)
				{
					return;
				}
				// the plane starts at the wall's downstream edge and reaches look.length cells downstream
				Vector3 at = c.ToVector3Shifted() + new Vector3(dx, 0f, dz) * (0.5f + look.length * 0.5f);
				at.y = y;
				Vector3 scale = new Vector3(1f, 1f, look.length);
				Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(at, turn, scale), mat, 0);
			}
		}

		/// <summary>Water falls over the wall at cell c: c is wet and so is the cell below it.</summary>
		private static bool FallsAt(Map map, IntVec3 c, int dx, int dz)
		{
			IntVec3 below = new IntVec3(c.x + dx, 0, c.z + dz);
			return c.InBounds(map) && below.InBounds(map) && RM_RiverWorks.IsWaterCell(map, c) && RM_RiverWorks.IsWaterCell(map, below);
		}

		/// <summary>Does white water continue in the cell beside c along the wall (a holding weir section there, water falling)?</summary>
		private static bool FoamBeside(Map map, IntVec3 c, int sx, int sz, int dx, int dz)
		{
			IntVec3 n = new IntVec3(c.x + sx, 0, c.z + sz);
			if (!n.InBounds(map) || !FallsAt(map, n, dx, dz))
			{
				return false;
			}
			List<Thing> things = n.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is RM_Building_BankWeir w && w.ArrestActive && !w.Breaching)
				{
					return true;
				}
			}
			return false;
		}

		public override IEnumerable<Gizmo> GetGizmos()
		{
			foreach (Gizmo g in base.GetGizmos())
			{
				yield return g;
			}
			if (Faction != Faction.OfPlayer || !Machinery.PipeLook.IsStyled(def))
			{
				yield break;
			}
			RM_Building_BankWeir self = this;
			yield return new Command_Action
			{
				defaultLabel = "Choose style",
				defaultDesc = "Change how this weir looks (scrapper, industrial, modern, futuristic): this section, or the whole joined wall. "
					+ "Free and instant; it changes art only, never cost or function.",
				icon = StyleDef?.UIIcon ?? (Texture2D)def.uiIcon,
				action = () =>
				{
					string cur = Machinery.PipeLook.LookOfThing(self);
					List<FloatMenuOption> opts = new List<FloatMenuOption>();
					foreach (string look in Machinery.PipeStyles.Looks)
					{
						ThingStyleDef sd = Machinery.PipeLook.StyleFor(self.def, look);
						if (sd == null)
						{
							continue;
						}
						string l = look;
						opts.Add(new FloatMenuOption(look + (look == cur ? " (current)" : "") + ": this section", () => Machinery.CompTankLook.SetLook(self, l), sd.UIIcon, Color.white));
						opts.Add(new FloatMenuOption(look + ": the whole joined wall", () =>
						{
							foreach (RM_Building_BankWeir w in self.Run())
							{
								Machinery.CompTankLook.SetLook(w, l);
							}
						}, sd.UIIcon, Color.white));
					}
					Find.WindowStack.Add(new FloatMenu(opts));
				}
			};
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			string mine = breaching ? "Breached - the flood is through." : (ArrestActive ? "Holding." : "Broken: repair above "
				+ RM_RiversSettings.breachHpFraction.ToStringPercent() + " to re-arm.");
			if (Spawned)
			{
				int n = Run().Count;
				if (n > 1)
				{
					mine += "\nJoined wall: " + n + " sections" + (RunHolds() ? "" : " - a gap: the pool behind it has drained") + (RunHead() == this ? " (catches for the wall)" : "") + ".";
				}
			}
			return s.NullOrEmpty() ? mine : s + "\n" + mine;
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref neverBreaches, "neverBreaches", false);
			Scribe_Values.Look(ref breaching, "breaching", false);
			Scribe_Values.Look(ref breachEndTick, "breachEndTick", 0);
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

	/// <summary>The joined-wall geometry (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS): a section's two ends are the cells just beyond
	/// its long axis; another weir (or its blueprint or frame, for placement) on the same axis there joins it.</summary>
	public static class RM_WeirRun
	{
		public const int MaxRun = 64;

		/// <summary>The cell beyond the low (min x / min z) or high end of a section's long axis.</summary>
		public static IntVec3 EndCell(IntVec3 loc, Rot4 rot, IntVec2 size, bool high)
		{
			CellRect r = GenAdj.OccupiedRect(loc, rot, size);
			if (rot.IsHorizontal)
			{
				return new IntVec3(high ? r.maxX + 1 : r.minX - 1, 0, r.minZ);
			}
			return new IntVec3(r.minX, 0, high ? r.maxZ + 1 : r.minZ - 1);
		}

		private static bool IsWeirOnAxis(Thing t, bool horizontal)
		{
			ThingDef weir = RM_RiverWorksDefOf.RM_BankWeir;
			if (t == null || weir == null)
			{
				return false;
			}
			bool isWeir = t.def == weir || ((t is Blueprint || t is Frame) && t.def.entityDefToBuild == weir);
			return isWeir && t.Rotation.IsHorizontal == horizontal;
		}

		/// <summary>Placement: does a weir, blueprint or frame on the same axis touch either end?</summary>
		public static bool ContinuesRun(Map map, IntVec3 loc, Rot4 rot, IntVec2 size, Thing ignore = null)
		{
			for (int e = 0; e < 2; e++)
			{
				IntVec3 c = EndCell(loc, rot, size, e == 1);
				if (!c.InBounds(map))
				{
					continue;
				}
				List<Thing> things = c.GetThingList(map);
				for (int i = 0; i < things.Count; i++)
				{
					if (things[i] != ignore && IsWeirOnAxis(things[i], rot.IsHorizontal))
					{
						return true;
					}
				}
			}
			return false;
		}

		/// <summary>The built section joined at one end, or null.</summary>
		public static RM_Building_BankWeir At(RM_Building_BankWeir w, bool high)
		{
			if (w == null || !w.Spawned)
			{
				return null;
			}
			IntVec3 c = EndCell(w.Position, w.Rotation, w.def.Size, high);
			if (!c.InBounds(w.Map))
			{
				return null;
			}
			List<Thing> things = c.GetThingList(w.Map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is RM_Building_BankWeir o && o != w && o.Rotation.IsHorizontal == w.Rotation.IsHorizontal)
				{
					return o;
				}
			}
			return null;
		}

		public static bool JoinedAt(RM_Building_BankWeir w, bool high) => At(w, high) != null;

		public static List<RM_Building_BankWeir> Neighbours(RM_Building_BankWeir w)
		{
			List<RM_Building_BankWeir> n = new List<RM_Building_BankWeir>(2);
			RM_Building_BankWeir lo = At(w, false);
			RM_Building_BankWeir hi = At(w, true);
			if (lo != null) n.Add(lo);
			if (hi != null && hi != lo) n.Add(hi);
			return n;
		}

		public static void DirtyNeighbours(RM_Building_BankWeir w, Map map)
		{
			foreach (RM_Building_BankWeir o in Neighbours(w))
			{
				o.DirtyMapMesh(map);
			}
		}
	}

	/// <summary>The weir's art paths and draw constants; materials are cached per path (null when the texture is absent,
	/// so a missing overlay draws nothing rather than magenta).</summary>
	[StaticConstructorOnStartup]
	public static class RM_WeirArt
	{
		/// <summary>The white-water flip-book, look-free: RM_WeirWhiteWater_00..11 (+ _a/_b/_ab end variants), crest at the
		/// top, falling south.
		/// Source: art_source/Weir/whitewater_frames.py (procedural, seamless in time).</summary>
		public const string FoamRoot = "RimMandrake/FlowWorks/Weir/WhiteWater/RM_WeirWhiteWater_";
		public const float CapSize = 0.7f;
		public const float CapLift = 0.08f;
		private static readonly Dictionary<string, Material> mats = new Dictionary<string, Material>();

		public static string FacingName(Rot4 r) => r == Rot4.North ? "north" : r == Rot4.East ? "east" : r == Rot4.South ? "south" : "west";

		private static readonly Dictionary<int, Material> foam = new Dictionary<int, Material>();

		/// <summary>One foam frame, end variant ("", _a, _b, _ab) and strength (alpha quantised to tenths so the cache stays
		/// tiny); null when the texture is absent (draws nothing rather than magenta).</summary>
		public static Material Foam(int frame, string end, float alpha)
		{
			int a = Mathf.Clamp(Mathf.RoundToInt(alpha * 10f), 1, 10);
			int v = end == "_a" ? 1 : end == "_b" ? 2 : end == "_ab" ? 3 : 0;
			int key = (frame * 4 + v) * 16 + a;
			if (foam.TryGetValue(key, out Material m))
			{
				return m;
			}
			string path = FoamRoot + frame.ToString("00") + end;
			Texture2D tex = ContentFinder<Texture2D>.Get(path, false);
			m = tex == null ? null : MaterialPool.MatFrom(path, ShaderDatabase.Transparent, new Color(1f, 1f, 1f, a / 10f));
			foam[key] = m;
			return m;
		}

		public static Material Mat(string path, Shader shader)
		{
			if (mats.TryGetValue(path, out Material m))
			{
				return m;
			}
			Texture2D tex = ContentFinder<Texture2D>.Get(path, false);
			m = tex == null ? null : MaterialPool.MatFrom(path, shader);
			mats[path] = m;
			return m;
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
