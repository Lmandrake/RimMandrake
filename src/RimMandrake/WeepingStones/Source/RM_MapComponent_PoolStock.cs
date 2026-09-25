using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1 — "the honest hard part" the spec names
	/// (§3's build table): per-pool-body bookkeeping, pattern stolen from
	/// <c>RimMandrake.FlowWorks.RM_LiquidBody</c>/<c>RM_LiquidStock</c> per the
	/// item's own instruction (read that pair before touching this file again).
	/// The steal is the SHAPE — a sticky id per body, one owner class holding a
	/// scribed list plus a derived index, a body that forms once and is never
	/// re-classified from scratch — not the flood-fill itself: a pool body's
	/// footprint is the player-drawn <see cref="RM_Zone_PoolPen"/> (spec §3: "an
	/// Area/zone designator, not a building"), so there is no BFS over raw
	/// terrain here the way LiquidBody discovers a lake on first canal contact.
	///
	/// Wave 2 shipped: zone tracking, a scribed <see cref="RM_PoolBody"/> per
	/// pen, and the READ gauge (population census + Healthy/Thin/Silent/Vhorrin).
	///
	/// Wave 3 adds: the STOCK verb's release target (<see cref="RM_JobDriver_StockPoolPen"/>
	/// spawns a pawn here) and the FEED verb's bookkeeping — <see cref="BodiesNeedingFeed"/>
	/// for <see cref="RM_WorkGiver_FeedPoolPen"/> to find pens that are due, and
	/// <see cref="Notify_Fed"/> for its JobDriver to record delivery. Going unfed
	/// now has a real cost per spec §3's own "what goes wrong" column: 2+ days
	/// forces at least a Thin READ regardless of population, 3+ days adds a small
	/// per-pulse chance of losing one resident (never a vhorrin — it IS the crash
	/// state, not a victim of it).
	///
	/// Wave 4 adds: the vhorrin EMERGENCE trigger, from either of the spec's two
	/// named paths (§2d/§3 OVERDRAW) — a crowded, unculled pen (population at or
	/// above the pen's own cell count) or a crashed one (unfed past the decay
	/// threshold) each carry a small per-pulse chance of converting one resident
	/// into a live RM_Vhorrin; and the vizhik ESCAPE event (§2c/§3 RECAPTURE) — a
	/// pen holding vizhik has a per-pulse chance of one pouring itself out onto
	/// nearby open ground, where <see cref="RM_WorkGiver_NetPoolBreeder"/> (NET)
	/// already knows how to catch it, same as any other wild stockable pawn. Both
	/// HARVEST and CULL ship as their own jobs this wave
	/// (<see cref="RM_JobDriver_HarvestPoolPen"/>/<see cref="RM_JobDriver_CullVhorrin"/>).
	/// Ring-density overlay ART is still owed — the gauge is exposed via the
	/// zone's inspect string in the meantime (a placeholder-art queue item, not a
	/// mechanism gap).
	/// </summary>
	public class RM_MapComponent_PoolStock : MapComponent
	{
		private const int PulseIntervalTicks = 2500;

		/// <summary>Pool fauna standing in a pen's cells is what population reads.
		/// RM_Murrin is included even though its own biome-wiring is owed
		/// elsewhere (FISH_BY_BIOME_1's successor): the spec names murrin rings
		/// as the primary telemetry species (§2.0/§3), and a pen holding none
		/// simply reads a population of zero from this list, same as any other
		/// empty pen — never a crash, never a special case.</summary>
		private static readonly HashSet<string> PoolFaunaDefNames = new HashSet<string>
		{
			"RM_Murrin", "RM_Skarrin", "RM_Karrek", "RM_Vizhik",
			"RM_Loomu", "RM_Huldu", "RM_Ivvol", "RM_Vhorrin",
		};

		/// <summary>Below this fraction of the pen's own cell count, the pool
		/// reads Thin rather than Healthy (spec §3 READ: "thin rings = hungry or
		/// predated"). A flat fraction rather than a per-species curve — tuning
		/// input for a future wave, not a claim this number is final.</summary>
		private const float ThinPopulationFraction = 0.5f;

		private List<RM_PoolBody> bodies = new List<RM_PoolBody>();

		private int nextBodyId = 1;

		/// <summary>Derived, never scribed — rebuilt from <see cref="bodies"/> on load,
		/// same as RM_LiquidStock.cellToBody.</summary>
		private readonly Dictionary<int, RM_PoolBody> byZoneId = new Dictionary<int, RM_PoolBody>();

		public RM_MapComponent_PoolStock(Map map)
			: base(map)
		{
		}

		public override void FinalizeInit()
		{
			base.FinalizeInit();
			RebuildIndex();
		}

		/// <summary>Rebuild the zone-id index and prune any body whose zone is
		/// gone — defensive only; PostDeregister/Notify_ZoneRemoved already
		/// handles the live-session case. A body can go orphaned if a save is
		/// hand-edited or a zone is destroyed by something outside the normal
		/// Delete/RemoveCell path.</summary>
		private void RebuildIndex()
		{
			byZoneId.Clear();
			List<Zone> allZones = map.zoneManager.AllZones;
			for (int i = bodies.Count - 1; i >= 0; i--)
			{
				RM_PoolBody body = bodies[i];
				bool found = false;
				for (int z = 0; z < allZones.Count; z++)
				{
					if (allZones[z] is RM_Zone_PoolPen && allZones[z].ID == body.zoneId)
					{
						found = true;
						break;
					}
				}
				if (!found)
				{
					bodies.RemoveAt(i);
					continue;
				}
				if (body.lastFedTick < 0)
				{
					// A body scribed before wave 3 has no feed record at
					// all -- treat it as "just fed" rather than instantly
					// starving on the very first pulse after this update.
					body.lastFedTick = Find.TickManager.TicksGame;
				}
				byZoneId[body.zoneId] = body;
			}
		}

		/// <summary>Every body whose FEED is due (spec §3's daily cadence).
		/// Read by <see cref="RM_WorkGiver_FeedPoolPen"/>.</summary>
		public IEnumerable<RM_PoolBody> BodiesNeedingFeed(int currentTick)
		{
			for (int i = 0; i < bodies.Count; i++)
			{
				if (bodies[i].NeedsFeed(currentTick))
				{
					yield return bodies[i];
				}
			}
		}

		/// <summary>The live zone a body tracks, or null if orphaned (pruned
		/// on the next RebuildIndex).</summary>
		public Zone ZoneFor(RM_PoolBody body)
		{
			if (body == null)
			{
				return null;
			}
			List<Zone> allZones = map.zoneManager.AllZones;
			for (int i = 0; i < allZones.Count; i++)
			{
				if (allZones[i].ID == body.zoneId)
				{
					return allZones[i];
				}
			}
			return null;
		}

		public void Notify_Fed(RM_PoolBody body, int currentTick)
		{
			if (body != null)
			{
				body.lastFedTick = currentTick;
			}
		}

		public RM_PoolBody BodyFor(RM_Zone_PoolPen zone)
		{
			if (zone == null)
			{
				return null;
			}
			byZoneId.TryGetValue(zone.ID, out RM_PoolBody body);
			return body;
		}

		/// <summary>Form (on first contact, sticky id — ruling 16's idiom) or
		/// keep the body behind a pen. Called whenever the zone registers or its
		/// cells change; a zone that shrinks to zero cells self-deregisters
		/// (Zone.RemoveCell) and arrives here via Notify_ZoneRemoved instead.</summary>
		public void Notify_ZoneChanged(RM_Zone_PoolPen zone)
		{
			if (zone == null || zone.CellCount == 0)
			{
				return;
			}
			if (byZoneId.ContainsKey(zone.ID))
			{
				return;
			}
			RM_PoolBody body = new RM_PoolBody(nextBodyId++)
			{
				zoneId = zone.ID,
				lastFedTick = Find.TickManager.TicksGame, // grace period: a brand-new pen isn't instantly "starving"
			};
			bodies.Add(body);
			byZoneId[zone.ID] = body;
			if (Prefs.DevMode)
			{
				Log.Message("[RimMandrake.WeepingStones] classified pool body #" + body.id
					+ " for zone '" + zone.label + "' (" + zone.CellCount + " cells). "
					+ "Sticky — this never runs again for this zone id.");
			}
		}

		public void Notify_ZoneRemoved(RM_Zone_PoolPen zone)
		{
			if (zone == null)
			{
				return;
			}
			if (byZoneId.TryGetValue(zone.ID, out RM_PoolBody body))
			{
				bodies.Remove(body);
				byZoneId.Remove(zone.ID);
			}
		}

		public override void MapComponentTick()
		{
			base.MapComponentTick();
			if (!RM_WeepingStonesSettings.stockedPoolsEnabled)
			{
				return; // mod option: stocked pools mechanism off — inert, degrades clean
			}
			if (bodies.Count == 0)
			{
				return;
			}
			if (Find.TickManager.TicksGame % PulseIntervalTicks != 0)
			{
				return;
			}
			Pulse();
		}

		/// <summary>Below this many unfed days, FEED's "what goes wrong"
		/// (spec §3) starts to bite: at least Thin regardless of raw
		/// population. At <see cref="UnfedDecayDays"/> the stock curve
		/// itself starts to bend down (a small chance per pulse of losing
		/// one non-vhorrin resident) -- tuning inputs, not a claim these
		/// are final, same honesty as <see cref="ThinPopulationFraction"/>.</summary>
		private const int UnfedThinDays = 2;

		private const int UnfedDecayDays = 3;

		private const float UnfedDeathChancePerPulse = 0.03f;

		/// <summary>Wave 4, vhorrin EMERGENCE (spec §2d/§3 OVERDRAW): "Any
		/// stocked pool left crowded and unculled grows one" — population at
		/// or above the pen's own cell count.</summary>
		private const float VhorrinEmergenceChanceCrowded = 0.02f;

		/// <summary>Wave 4, the OVERDRAW's other named path: "a stressed pool
		/// turns nasty before it turns silent" — a pool already crashed
		/// (unfed past <see cref="UnfedDecayDays"/>) carries a smaller but
		/// real emergence chance too.</summary>
		private const float VhorrinEmergenceChanceCrashed = 0.01f;

		/// <summary>Wave 4, vizhik ESCAPE (spec §2c/§3 RECAPTURE): "At
		/// wind-hour... a vizhik pours itself out of the pen." One pulse is
		/// roughly a wind-hour's worth of game time at this component's pulse
		/// interval, so this fires per pulse rather than per day.</summary>
		private const float VizhikEscapeChance = 0.05f;

		private const int VizhikEscapeSearchRadius = 8;

		/// <summary>One census pass over every spawned pawn, bucketed by which
		/// pen (if any) it stands in — cheaper than one full-map scan per body,
		/// and the same "one owner, one pass" reasoning RM_LiquidStock.Pulse
		/// uses for recession/refill.</summary>
		private void Pulse()
		{
			Dictionary<int, Zone> zoneById = new Dictionary<int, Zone>();
			List<Zone> allZones = map.zoneManager.AllZones;
			for (int i = 0; i < allZones.Count; i++)
			{
				if (allZones[i] is RM_Zone_PoolPen)
				{
					zoneById[allZones[i].ID] = allZones[i];
				}
			}

			Dictionary<int, int> populationByZone = new Dictionary<int, int>();
			Dictionary<int, int> vhorrinByZone = new Dictionary<int, int>();
			Dictionary<int, List<Pawn>> starveCandidatesByZone = new Dictionary<int, List<Pawn>>();
			Dictionary<int, List<Pawn>> vizhikByZone = new Dictionary<int, List<Pawn>>();
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn pawn = pawns[i];
				if (pawn.def == null || !PoolFaunaDefNames.Contains(pawn.def.defName))
				{
					continue;
				}
				Zone zone = map.zoneManager.ZoneAt(pawn.Position);
				if (!(zone is RM_Zone_PoolPen))
				{
					continue;
				}
				populationByZone.TryGetValue(zone.ID, out int count);
				populationByZone[zone.ID] = count + 1;
				if (pawn.def.defName == "RM_Vhorrin")
				{
					vhorrinByZone.TryGetValue(zone.ID, out int vc);
					vhorrinByZone[zone.ID] = vc + 1;
					continue; // never a starvation-decay target -- it IS the crash, not a victim of one
				}
				if (!starveCandidatesByZone.TryGetValue(zone.ID, out List<Pawn> candidates))
				{
					candidates = new List<Pawn>();
					starveCandidatesByZone[zone.ID] = candidates;
				}
				candidates.Add(pawn);
				if (pawn.def.defName == "RM_Vizhik")
				{
					if (!vizhikByZone.TryGetValue(zone.ID, out List<Pawn> vizhikList))
					{
						vizhikList = new List<Pawn>();
						vizhikByZone[zone.ID] = vizhikList;
					}
					vizhikList.Add(pawn);
				}
			}

			int currentTick = Find.TickManager.TicksGame;
			for (int i = 0; i < bodies.Count; i++)
			{
				RM_PoolBody body = bodies[i];
				if (!zoneById.TryGetValue(body.zoneId, out Zone zone))
				{
					continue; // orphaned; RebuildIndex prunes it on the next load
				}
				populationByZone.TryGetValue(body.zoneId, out int population);
				vhorrinByZone.TryGetValue(body.zoneId, out int vhorrinCount);
				int unfedDays = body.UnfedDays(currentTick);
				body.population = population;
				body.state = ClassifyState(population, vhorrinCount, zone.CellCount, unfedDays);

				starveCandidatesByZone.TryGetValue(body.zoneId, out List<Pawn> candidates);

				if (unfedDays >= UnfedDecayDays
					&& candidates != null && candidates.Count > 0
					&& Rand.Chance(UnfedDeathChancePerPulse))
				{
					Pawn victim = candidates[Rand.Range(0, candidates.Count)];
					if (victim.Spawned)
					{
						victim.Kill(null);
					}
				}

				if (vhorrinCount <= 0 && candidates != null && candidates.Count > 0)
				{
					bool crowded = zone.CellCount > 0 && population >= zone.CellCount;
					bool crashed = unfedDays >= UnfedDecayDays;
					float emergenceChance = crowded ? VhorrinEmergenceChanceCrowded
						: crashed ? VhorrinEmergenceChanceCrashed
						: 0f;
					if (emergenceChance > 0f && Rand.Chance(emergenceChance))
					{
						TrySpawnVhorrin(candidates);
					}
				}

				if (vizhikByZone.TryGetValue(body.zoneId, out List<Pawn> vizhikCandidates)
					&& vizhikCandidates.Count > 0
					&& Rand.Chance(VizhikEscapeChance))
				{
					TryEscapeVizhik(vizhikCandidates[Rand.Range(0, vizhikCandidates.Count)]);
				}
			}
		}

		/// <summary>Converts one resident of a crowded or crashed pen into the
		/// mismanagement state made flesh (spec §2d) — the murrin rings thin,
		/// one wide slow ring starts doing all the surfacing. Never picks an
		/// existing vhorrin (candidates never contains one; see the census
		/// pass in <see cref="Pulse"/>).</summary>
		private static void TrySpawnVhorrin(List<Pawn> candidates)
		{
			Pawn victim = candidates[Rand.Range(0, candidates.Count)];
			if (!victim.Spawned)
			{
				return;
			}
			PawnKindDef vhorrinKind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Vhorrin");
			if (vhorrinKind == null)
			{
				return;
			}
			IntVec3 spot = victim.Position;
			Map victimMap = victim.Map;
			victim.Destroy(DestroyMode.Vanish);
			PawnGenerationRequest request = new PawnGenerationRequest(vhorrinKind, null, PawnGenerationContext.NonPlayer,
				forceGenerateNewPawn: true, allowDowned: true, canGeneratePawnRelations: false);
			Pawn vhorrin = PawnGenerator.GeneratePawn(request);
			GenSpawn.Spawn(vhorrin, spot, victimMap);
			if (Prefs.DevMode)
			{
				Log.Message("[RimMandrake.WeepingStones] a vhorrin has emerged at " + spot + " — the pool is turning nasty.");
			}
		}

		/// <summary>Pours one vizhik out of its pen onto nearby open ground
		/// (spec §2c: "crosses open rock on its gill-comb"). Despawn+respawn
		/// is the vanilla-safe teleport idiom (no direct Position setter moves
		/// a spawned pawn between map cells correctly). The destination is
		/// deliberately allowed to be another RM_Zone_PoolPen — the spec's own
		/// flavor text names "the next pool" as a legitimate destination.</summary>
		private void TryEscapeVizhik(Pawn vizhik)
		{
			if (vizhik == null || !vizhik.Spawned)
			{
				return;
			}
			IntVec3 origin = vizhik.Position;
			if (!CellFinder.TryFindRandomCellNear(origin, map, VizhikEscapeSearchRadius,
				c => c.Standable(map) && !(map.zoneManager.ZoneAt(c) is RM_Zone_PoolPen) && c.Walkable(map),
				out IntVec3 dest))
			{
				return;
			}
			vizhik.DeSpawn(DestroyMode.Vanish);
			GenSpawn.Spawn(vizhik, dest, map);
			if (Prefs.DevMode)
			{
				Log.Message("[RimMandrake.WeepingStones] a vizhik escaped its pen at " + origin + ", now traveling near " + dest + ".");
			}
		}

		private static RM_PoolStockState ClassifyState(int population, int vhorrinCount, int cellCount, int unfedDays)
		{
			if (vhorrinCount > 0)
			{
				return RM_PoolStockState.Vhorrin;
			}
			if (population <= 0)
			{
				return RM_PoolStockState.Silent;
			}
			if (unfedDays >= UnfedThinDays)
			{
				return RM_PoolStockState.Thin;
			}
			if (cellCount > 0 && population < cellCount * ThinPopulationFraction)
			{
				return RM_PoolStockState.Thin;
			}
			return RM_PoolStockState.Healthy;
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Collections.Look(ref bodies, "RM_poolBodies", LookMode.Deep);
			Scribe_Values.Look(ref nextBodyId, "RM_nextPoolBodyId", 1);
			if (Scribe.mode == LoadSaveMode.PostLoadInit && bodies == null)
			{
				bodies = new List<RM_PoolBody>();
			}
		}
	}
}
