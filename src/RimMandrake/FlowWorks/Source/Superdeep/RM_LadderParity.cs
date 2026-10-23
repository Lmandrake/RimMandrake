using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LADDER_PARITY_BUILD_NO_KEYS_REQUIRED — the Verse half (rules: RM_LadderParityMath; design:
	/// design/RimMandrake/ladder_parity_2026-10-23.md). Owner by card 2026-10-23, (4) "Full parity both ways": <i>"Both sides
	/// should be able to use each other's ladders: makes NO sense otherwise (what are they locked with a key?)."</i>
	///
	/// No keys: RM_LadderRules.MayClimb reads RM_LadderParityMath.MayClimbLowered (a raised wall ladder is still nobody's).
	/// Pick up and move: the portable ladder is alwaysUninstallable (colonists uninstall anyone's); a ladderless raider takes one
	/// (JobDriver_RM_RaiderTakeLadder). Carried ladders: a share of some raids arrive with one minified in the inventory
	/// (RM_Patch_Raid_LadderCarriers) and set it fast (RM_RaiderTrench's ladder job, TakeCarried). Repair: every raider fill
	/// leaves a breach scar (RM_BreachScars) that Designator_RM_RepairBreach turns into a dig-to order. Walls: a portable ladder
	/// against a single unroofed wall carries a pawn over it one way (CanClimbAt, read by RM_WallClimb's seams and job).
	/// </summary>
	public static class RM_LadderParity
	{
		// ── owner Q1 2026-10-23: who can climb a ladder at all ─────────────
		internal struct ClimberTraits
		{
			public bool wheeled, arms, jumps, slithers;
			public int over;
		}

		private static readonly Dictionary<ThingDef, ClimberTraits> traitCache = new Dictionary<ThingDef, ClimberTraits>();

		/// <summary>A race's ladder traits, read once from its body (part tags and names), never from a name list: arms = a
		/// ManipulationLimbCore part that is not a mouth (EatingSource), or a humanlike; legs = a MovingLimbCore part other than
		/// the core part (a snake's body is its own moving limb); wheeled = a part whose def name or label
		/// says wheel/tread/track; slithers = no legs, not wheeled, and it moves; jumps = RM_PitTravelExtension.jumps;
		/// over = an RM_LadderClimber extension (1 climbs, 0 never, -1 none).</summary>
		internal static ClimberTraits TraitsOf(ThingDef race)
		{
			if (race == null)
			{
				return new ClimberTraits { over = 0 };
			}
			if (traitCache.TryGetValue(race, out ClimberTraits t))
			{
				return t;
			}
			t = new ClimberTraits { over = -1 };
			RM_LadderClimber ext = race.GetModExtension<RM_LadderClimber>();
			if (ext != null)
			{
				t.over = ext.climbs ? 1 : 0;
			}
			t.jumps = race.GetModExtension<RM_PitTravelExtension>()?.jumps ?? false;
			bool legs = false;
			List<BodyPartRecord> parts = race.race?.body?.AllParts;
			if (parts != null)
			{
				for (int i = 0; i < parts.Count; i++)
				{
					BodyPartDef d = parts[i].def;
					if (d?.tags == null)
					{
						continue;
					}
					// a mouth or beak is tagged ManipulationLimbCore too (vanilla SnakeMouth: EatingSource + ManipulationLimbCore):
					// jaws are not arms
					t.arms |= d.tags.Contains(BodyPartTagDefOf.ManipulationLimbCore) && !d.tags.Contains(BodyPartTagDefOf.EatingSource);
					// a body that IS its moving limb (vanilla SnakeBody: the core part, MovingLimbCore) slithers; legs hang off it
					legs |= d.tags.Contains(BodyPartTagDefOf.MovingLimbCore) && parts[i] != race.race.body.corePart;
					string n = (d.defName + " " + d.label + " " + parts[i].customLabel).ToLowerInvariant();
					t.wheeled |= n.Contains("wheel") || n.Contains("tread") || n.Contains("track");
				}
			}
			t.arms |= race.race != null && race.race.Humanlike;
			t.slithers = !legs && !t.wheeled && race.race != null && !race.race.doesntMove && parts != null && parts.Count > 0;
			traitCache[race] = t;
			return t;
		}

		/// <summary>Can this creature climb a ladder at all (owner Q1)? Flyers never need one (FreePitTraveller).</summary>
		public static bool ClimbEligible(Pawn p)
		{
			if (p == null)
			{
				return false;
			}
			ClimberTraits t = TraitsOf(p.def);
			return RM_LadderParityMath.ClimbEligible(p.BodySize, RM_LadderParitySettings.ladderMaxClimberBodySize, t.wheeled, t.arms,
				t.jumps, t.slithers, t.over);
		}

		// ── owner Q2 2026-10-23: chop a tree for the wood, then build ───────
		/// <summary>The wood one portable ladder costs (its def's WoodLog cost; 12 if none is listed).</summary>
		public static int LadderWoodNeeded()
		{
			List<ThingDefCountClass> cost = RimMandrakeFlowWorks_DefOf.RM_LadderPortable?.CostList;
			if (cost != null)
			{
				for (int i = 0; i < cost.Count; i++)
				{
					if (cost[i].thingDef == ThingDefOf.WoodLog)
					{
						return cost[i].count;
					}
				}
			}
			return 12;
		}

		public static int WoodCarried(Pawn p)
		{
			ThingOwner<Thing> inv = p?.inventory?.innerContainer;
			return inv == null ? 0 : inv.TotalStackCountOfDef(ThingDefOf.WoodLog);
		}

		public static bool HasLadderWood(Pawn p)
		{
			return WoodCarried(p) >= LadderWoodNeeded();
		}

		/// <summary>Takes one ladder's wood out of the inventory; false (nothing taken) when there is not enough.</summary>
		public static bool SpendLadderWood(Pawn p)
		{
			int need = LadderWoodNeeded();
			if (WoodCarried(p) < need)
			{
				return false;
			}
			ThingOwner<Thing> inv = p.inventory.innerContainer;
			for (int i = inv.Count - 1; i >= 0 && need > 0; i--)
			{
				Thing t = inv[i];
				if (t.def != ThingDefOf.WoodLog)
				{
					continue;
				}
				int take = Mathf.Min(need, t.stackCount);
				Thing part = t.SplitOff(take);
				part.Destroy();
				need -= take;
			}
			return true;
		}

		/// <summary>The nearest standing tree this raider can fell for ladder wood (grown enough to yield wood), within the
		/// chop radius, reachable and unreserved; null when none.</summary>
		public static Job ChopForLadderJob(Pawn p)
		{
			if (RM_LadderParityDefOf.RM_RaiderChopForLadder == null || RM_LadderParitySettings.raiderChopRadius <= 0)
			{
				return null;
			}
			Map map = p.Map;
			int r = RM_LadderParitySettings.raiderChopRadius;
			Plant best = null;
			int bestD = int.MaxValue;
			foreach (IntVec3 c in GenRadial.RadialCellsAround(p.Position, r, true))
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				Plant pl = c.GetPlant(map);
				if (pl == null || pl.def.plant == null || !pl.def.plant.IsTree || pl.def.plant.isStump || pl.def.plant.harvestedThingDef != ThingDefOf.WoodLog
					|| !pl.HarvestableNow || pl.YieldNow() <= 0)
				{
					continue;
				}
				int d = c.DistanceToSquared(p.Position);
				if (d >= bestD || !p.CanReserve(pl) || !p.CanReach(pl, PathEndMode.Touch, Danger.Deadly))
				{
					continue;
				}
				best = pl;
				bestD = d;
				break;   // RadialCellsAround runs nearest-first: the first good tree is the nearest
			}
			return best == null ? null : JobMaker.MakeJob(RM_LadderParityDefOf.RM_RaiderChopForLadder, best);
		}

		/// <summary>The job that gets this raider a ladder it does not yet have (owner Q2's order), or null with
		/// <paramref name="canBuild"/> true when it may build one now (it carries a ladder or the wood), false when nothing is
		/// in reach (no ladder: fill or jump).</summary>
		public static Job LadderSupplyJob(Pawn p, ICollection<IntVec3> keep, out bool canBuild)
		{
			bool carries = CarriedLadder(p) != null;
			Job take = carries ? null : TakeLadderJob(p, keep);
			bool wood = !carries && take == null && HasLadderWood(p);
			Job chop = carries || take != null || wood ? null : ChopForLadderJob(p);
			canBuild = false;
			switch (RM_LadderParityMath.ChooseLadderSource(carries, take != null, wood, chop != null))
			{
				case RM_LadderParityMath.LadderSource.SetCarried:
				case RM_LadderParityMath.LadderSource.Build:
					canBuild = true;
					return null;
				case RM_LadderParityMath.LadderSource.Take:
					return take;
				case RM_LadderParityMath.LadderSource.Chop:
					return chop;
				default:
					return null;
			}
		}

		/// <summary>A minified portable ladder in this pawn's inventory, or null.</summary>
		public static MinifiedThing CarriedLadder(Pawn p)
		{
			ThingDef def = RimMandrakeFlowWorks_DefOf.RM_LadderPortable;
			ThingOwner<Thing> inv = p?.inventory?.innerContainer;
			if (def == null || inv == null)
			{
				return null;
			}
			for (int i = 0; i < inv.Count; i++)
			{
				if (inv[i] is MinifiedThing m && m.InnerThing?.def == def)
				{
					return m;
				}
			}
			return null;
		}

		/// <summary>Takes the carried ladder out of the inventory and returns the (unspawned) ladder inside it, or null.</summary>
		public static Thing TakeCarried(Pawn p)
		{
			MinifiedThing m = CarriedLadder(p);
			if (m == null)
			{
				return null;
			}
			Thing inner = m.InnerThing;
			p.inventory.innerContainer.Remove(m);
			m.InnerThing = null;
			m.Destroy();
			return inner;
		}

		/// <summary>A standing portable ladder on undug ground hung toward the wall square in front of it.</summary>
		public static bool LeansOnWall(Thing ladder)
		{
			if (!RM_LadderParitySettings.ladderOverWalls || ladder == null || !ladder.Spawned
				|| ladder.def != RimMandrakeFlowWorks_DefOf.RM_LadderPortable || RM_LadderUtility.MaxLevelsOf(ladder.def) < 0)
			{
				return false;
			}
			Map map = ladder.Map;
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			if (eng != null && eng.ClimbDepthAt(ladder.Position) != 0)
			{
				return false;
			}
			return RM_WallClimb.ClimbableWallAt(map, ladder.Position + ladder.Rotation.FacingCell) != null;
		}

		/// <summary>The ladder leaning on <paramref name="wallCell"/> from <paramref name="foot"/>, or null.</summary>
		public static Thing LadderLeaningAt(Map map, IntVec3 foot, IntVec3 wallCell)
		{
			Thing l = RM_LadderUtility.LadderAt(map, foot);
			return l != null && RM_LadderUtility.HangsToward(l, wallCell) && LeansOnWall(l) ? l : null;
		}

		/// <summary>Worth asking CanClimbAt for this pawn at all (the seams' cheap gate): climbing gear, or the ladder setting on
		/// and either the player's pawn (it may find a ladder leaning there) or a pawn carrying one.</summary>
		public static bool MightClimb(Pawn p)
		{
			if (RM_WallClimb.CanClimb(p))
			{
				return true;
			}
			if (!RM_LadderParitySettings.ladderOverWalls || p == null || !p.Spawned || p.Downed || p.Dead)
			{
				return false;
			}
			return p.Faction == Faction.OfPlayer || CarriedLadder(p) != null;
		}

		/// <summary>May this pawn go over the wall at <paramref name="wallCell"/> from <paramref name="foot"/>, a crossing
		/// RM_WallClimb.TryCrossing has already found open (<paramref name="squares"/> wall squares)? Gear: any crossing. Else a
		/// ladder: one leaning there (one way), or one it carries and sets there, over ONE wall square, and the ladder rule lets
		/// it climb (no keys).</summary>
		public static bool CanClimbAt(Pawn p, IntVec3 foot, IntVec3 wallCell, int squares)
		{
			if (RM_WallClimb.CanClimb(p))
			{
				return true;
			}
			if (p?.Map == null || !RM_LadderParitySettings.ladderOverWalls)
			{
				return false;
			}
			Map map = p.Map;
			bool leaning = LadderLeaningAt(map, foot, wallCell) != null;
			bool canSet = !leaning && RM_LadderUtility.LadderAt(map, foot) == null && CarriedLadder(p) != null
				&& RM_LadderUtility.MaxLevelsOf(RimMandrakeFlowWorks_DefOf.RM_LadderPortable) >= 0
				&& (map.GetComponent<RM_MapComponent_Excavation>()?.ClimbDepthAt(foot) ?? 0) == 0;
			bool usable = !RimMandrakeFlowWorksSettings.ladderPrisonDoorEnabled || RM_LadderRules.MayClimb(p);
			return RM_LadderParityMath.LadderOverWallOpen(true, leaning || canSet, true, usable, squares, false, false, false, true, true);
		}

		/// <summary>The pawn climbs by ladder, not gear (the job's speed and its set-the-ladder step).</summary>
		public static bool ByLadder(Pawn p)
		{
			return !RM_WallClimb.CanClimb(p);
		}

		/// <summary>Sets the pawn's carried ladder at <paramref name="foot"/>, facing the wall. False when there is none or the
		/// square is taken.</summary>
		public static bool SetCarriedAt(Pawn p, IntVec3 foot, IntVec3 wallCell)
		{
			Map map = p.Map;
			if (RM_LadderUtility.LadderAt(map, foot) != null || CarriedLadder(p) == null)
			{
				return false;
			}
			Thing ladder = TakeCarried(p);
			if (ladder == null)
			{
				return false;
			}
			if (ladder.def.CanHaveFaction && p.Faction != null)
			{
				ladder.SetFaction(p.Faction);
			}
			GenSpawn.Spawn(ladder, foot, map, Rot4.FromIntVec3(wallCell - foot));
			return true;
		}

		/// <summary>"Can pick up each other's ladders": a standing portable ladder (anyone's) a ladderless raider may take, the
		/// nearest it can reach, never one on <paramref name="keep"/> (its own crossing's squares). Null: none.</summary>
		public static Job TakeLadderJob(Pawn p, ICollection<IntVec3> keep)
		{
			ThingDef def = RimMandrakeFlowWorks_DefOf.RM_LadderPortable;
			if (def == null || RM_LadderParityDefOf.RM_RaiderTakeLadder == null || !RM_LadderParitySettings.raiderTakeLadders)
			{
				return null;
			}
			bool carries = CarriedLadder(p) != null;
			Thing best = null;
			int bestD = int.MaxValue;
			List<Thing> all = p.Map.listerThings.ThingsOfDef(def);
			for (int i = 0; i < all.Count; i++)
			{
				Thing l = all[i];
				int d = l.Position.DistanceToSquared(p.Position);
				if (d >= bestD || !RM_LadderParityMath.MayTakeLadder(true, carries, d, RM_LadderParitySettings.raiderTakeLadderRadius,
					keep != null && keep.Contains(l.Position), l.Position.GetFirstPawn(p.Map) != null))
				{
					continue;
				}
				if (!p.CanReserve(l) || !p.CanReach(l, PathEndMode.Touch, Danger.Deadly))
				{
					continue;
				}
				best = l;
				bestD = d;
			}
			return best == null ? null : JobMaker.MakeJob(RM_LadderParityDefOf.RM_RaiderTakeLadder, best);
		}

		/// <summary>Bridge read/act for the live rows (jawa/static_call, type RimMandrake.FlowWorks.RM_LadderParity):
		/// "chance:P" sets the raid-ladder chance to P % (a proof's own setting, restore it after); "carriers" counts the
		/// spawned hostile people and those carrying a ladder; "scar:x,z" reads a breach scar; "repair:x,z" runs the real
		/// Repair breach designator on a square; "climb:pawnId,wallX,wallZ" orders the pawn over that wall (the float menu's
		/// crossing); "may:pawnId,x,z" asks LadderLetsOut for the ladder on (x,z).</summary>
		public static string ProofLadderParity(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null)
			{
				return "REFUSED: no current map";
			}
			string[] parts = (arg ?? "").Split(':');
			var n = new List<int>();
			if (parts.Length > 1)
			{
				foreach (string s in parts[1].Split(','))
				{
					if (!int.TryParse(s.Trim(), out int v))
					{
						return "REFUSED: bad number '" + s + "'";
					}
					n.Add(v);
				}
			}
			Pawn PawnById(int id)
			{
				foreach (Pawn q in map.mapPawns.AllPawnsSpawned)
				{
					if (q.thingIDNumber == id)
					{
						return q;
					}
				}
				return null;
			}
			switch (parts[0])
			{
				case "chance":
					if (n.Count != 1)
					{
						return "REFUSED: chance:P";
					}
					float was = RM_LadderParitySettings.raidLadderChance;
					RM_LadderParitySettings.raidLadderChance = Mathf.Clamp01(n[0] / 100f);
					return "chance was=" + Mathf.RoundToInt(was * 100f) + " now=" + Mathf.RoundToInt(RM_LadderParitySettings.raidLadderChance * 100f);
				case "carriers":
				{
					int people = 0;
					var carriers = new List<int>();
					foreach (Pawn q in map.mapPawns.AllPawnsSpawned)
					{
						if (q.Faction == null || Faction.OfPlayer == null || !q.Faction.HostileTo(Faction.OfPlayer) || !RM_RaiderTrench.ToolUser(q))
						{
							continue;
						}
						people++;
						if (CarriedLadder(q) != null)
						{
							carriers.Add(q.thingIDNumber);
						}
					}
					return "raiders=" + people + " carriers=" + carriers.Count + " ids=" + string.Join(",", carriers);
				}
				case "scar":
				case "repair":
				{
					if (n.Count != 2)
					{
						return "REFUSED: " + parts[0] + ":x,z";
					}
					var c = new IntVec3(n[0], 0, n[1]);
					RM_BreachScars s = map.GetComponent<RM_BreachScars>();
					RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
					string head = "scar=" + (s?.ScarAt(c) ?? -1) + " depth=" + (eng?.ExcavatedDepthAt(c) ?? -1);
					if (parts[0] == "scar")
					{
						return head;
					}
					var d = new Designator_RM_RepairBreach();
					AcceptanceReport ok = d.CanDesignateCell(c);
					if (ok.Accepted)
					{
						d.DesignateSingleCell(c);
					}
					return head + " accepted=" + ok.Accepted + " reason=" + (ok.Reason ?? "") + " designated="
						+ (map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal) != null)
						+ " digTarget=" + (eng?.DigTargetAt(c) ?? -1);
				}
				case "climb":
				{
					Pawn p = n.Count == 3 ? PawnById(n[0]) : null;
					if (p == null)
					{
						return "REFUSED: climb:pawnId,wallX,wallZ (pawn spawned)";
					}
					var wall = new IntVec3(n[1], 0, n[2]);
					if (!RM_WallClimb.TryBestCrossing(p, wall, false, out IntVec3 from, out IntVec3 landing, out bool roofed))
					{
						return "NO_CROSSING roofed=" + roofed + " mightClimb=" + MightClimb(p);
					}
					bool taken = p.jobs.TryTakeOrderedJob(RM_WallClimb.MakeClimbJob(from, wall, landing), JobTag.Misc);
					return "ORDERED taken=" + taken + " from=" + from + " landing=" + landing + " byLadder=" + ByLadder(p);
				}
				case "may":
				{
					Pawn p = n.Count == 3 ? PawnById(n[0]) : null;
					if (p == null)
					{
						return "REFUSED: may:pawnId,x,z (pawn spawned)";
					}
					var c = new IntVec3(n[1], 0, n[2]);
					Thing l = RM_LadderUtility.LadderAt(map, c);
					return "ladder=" + (l?.def.defName ?? "none") + " faction=" + (l?.Faction?.Name ?? "none") + " mayClimb="
						+ RM_LadderRules.MayClimb(p) + " letsOut=" + RM_LadderRules.LadderLetsOut(map, c, p);
				}
				default:
					return "REFUSED: chance:P | carriers | scar:x,z | repair:x,z | climb:pawnId,wallX,wallZ | may:pawnId,x,z";
			}
		}
	}

	[DefOf]
	public static class RM_LadderParityDefOf
	{
		public static JobDef RM_RaiderTakeLadder;
		public static JobDef RM_RaiderChopForLadder;

		static RM_LadderParityDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RM_LadderParityDefOf));
		}
	}

	/// <summary>A raider takes a standing portable ladder (anyone's) down and into its inventory: walk to it, work it loose
	/// (its uninstall work), minify it.</summary>
	public class JobDriver_RM_RaiderTakeLadder : JobDriver
	{
		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedOrNull(TargetIndex.A);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
			Toil work = ToilMaker.MakeToil("RM_RaiderTakeLadder");
			work.initAction = delegate
			{
				pawn.pather.StopDead();
			};
			work.defaultCompleteMode = ToilCompleteMode.Delay;
			work.defaultDuration = 120;
			work.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			work.WithProgressBarToilDelay(TargetIndex.A);
			yield return work;
			Toil take = ToilMaker.MakeToil("RM_RaiderTakeLadder_Done");
			take.initAction = delegate
			{
				Thing l = job.targetA.Thing;
				if (l == null || !l.Spawned || RM_LadderParity.CarriedLadder(pawn) != null || l.Position.GetFirstPawn(Map) != null)
				{
					return;
				}
				MinifiedThing m = l.MakeMinified();
				if (m != null && !pawn.inventory.innerContainer.TryAdd(m))
				{
					GenPlace.TryPlaceThing(m, pawn.Position, Map, ThingPlaceMode.Near);
				}
			};
			take.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return take;
		}
	}

	/// <summary>Owner Q2 2026-10-23 ("they look for something to chop down, get the wood, then build it. Destructive."): fell
	/// a tree as vanilla's cut does (harvestWork at PlantWorkSpeed), PlantCollected as a chop (the stump stays), and keep
	/// the logs it yields in the inventory for the ladder.</summary>
	public class JobDriver_RM_RaiderChopForLadder : JobDriver
	{
		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedOrNull(TargetIndex.A);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
			Toil cut = ToilMaker.MakeToil("RM_RaiderChopForLadder");
			cut.initAction = delegate
			{
				pawn.pather.StopDead();
			};
			cut.tickAction = delegate
			{
				pawn.rotationTracker.FaceTarget(job.targetA);
			};
			cut.defaultCompleteMode = ToilCompleteMode.Delay;
			Plant tree = job.targetA.Thing as Plant;
			float speed = StatDefOf.PlantWorkSpeed.Worker.IsDisabledFor(pawn) ? 0.1f : pawn.GetStatValue(StatDefOf.PlantWorkSpeed);
			cut.defaultDuration = RM_LadderParityMath.ChopTicks(tree?.def.plant?.harvestWork ?? 800f, speed);
			cut.handlingFacing = true;
			cut.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			cut.WithProgressBarToilDelay(TargetIndex.A);
			yield return cut;
			Toil fell = ToilMaker.MakeToil("RM_RaiderChopForLadder_Fell");
			fell.initAction = delegate
			{
				if (!(job.targetA.Thing is Plant pl) || !pl.Spawned)
				{
					return;
				}
				int yield = pl.YieldNow();
				ThingDef wood = pl.def.plant.harvestedThingDef;
				pl.PlantCollected(pawn, PlantDestructionMode.Chop);
				while (yield > 0 && wood != null)
				{
					Thing logs = ThingMaker.MakeThing(wood);
					logs.stackCount = Mathf.Min(yield, wood.stackLimit);
					yield -= logs.stackCount;
					if (!pawn.inventory.innerContainer.TryAdd(logs))
					{
						GenPlace.TryPlaceThing(logs, pawn.Position, Map, ThingPlaceMode.Near);
					}
				}
			};
			fell.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return fell;
		}
	}

	/// <summary>Owner Q1 2026-10-23: a per-def judgment on who climbs ladders, beating the body rule
	/// (RM_LadderParityMath.ClimbEligible). On a race ThingDef: &lt;li Class="RimMandrake.FlowWorks.RM_LadderClimber"&gt;
	/// &lt;climbs&gt;false&lt;/climbs&gt;&lt;/li&gt;. Table and borderline cases: design/RimMandrake/ladder_climbers_2026-10-23.md.</summary>
	public class RM_LadderClimber : DefModExtension
	{
		public bool climbs = true;
	}

	/// <summary>"Raiders should show up with ladders sometimes but not always, and certainly not on every raider": a stable
	/// roll per raid (RaidBringsLadders), then PickCarriers among its tool-using people; each carrier gets one minified
	/// portable ladder in its inventory. Never a siege.</summary>
	[HarmonyPatch(typeof(IncidentWorker_Raid), "PostProcessSpawnedPawns")]
	[RimMandrake.Shared.PatchFeature("Raiders arrive with ladders")]
	public static class RM_Patch_Raid_LadderCarriers
	{
		[HarmonyPostfix]
		public static void Postfix(IncidentParms parms, List<Pawn> pawns)
		{
			ThingDef def = RimMandrakeFlowWorks_DefOf.RM_LadderPortable;
			if (def == null || RM_LadderParitySettings.raidLadderChance <= 0f || RM_LadderUtility.MaxLevelsOf(def) < 0
				|| pawns == null || pawns.Count < 2 || !(parms?.target is Map) || parms.raidStrategy?.Worker is RaidStrategyWorker_Siege
				|| parms.faction == null || parms.faction == Faction.OfPlayer)
			{
				return;
			}
			var people = new List<int>();
			var byId = new Dictionary<int, Pawn>();
			int seed = int.MaxValue;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				if (p?.inventory == null || !RM_RaiderTrench.ToolUser(p))
				{
					continue;
				}
				people.Add(p.thingIDNumber);
				byId[p.thingIDNumber] = p;
				seed = Mathf.Min(seed, p.thingIDNumber);
			}
			if (people.Count < 2 || !RM_LadderParityMath.RaidBringsLadders(seed, RM_LadderParitySettings.raidLadderChance))
			{
				return;
			}
			foreach (int id in RM_LadderParityMath.PickCarriers(people, RM_LadderParitySettings.raidLadderCarrierShare))
			{
				Pawn p = byId[id];
				Thing ladder = ThingMaker.MakeThing(def);
				var m = (MinifiedThing)ThingMaker.MakeThing(def.minifiedDef ?? ThingDefOf.MinifiedThing);
				m.InnerThing = ladder;
				if (!p.inventory.innerContainer.TryAdd(m))
				{
					m.Destroy();
				}
			}
		}
	}

	/// <summary>"A way to repair damage caused by people digging their way into a pit": the depth a square had before raiders
	/// first shovelled into it (scribed), until it is dug that deep again.</summary>
	public class RM_BreachScars : MapComponent
	{
		private Dictionary<int, int> scars = new Dictionary<int, int>();
		private List<int> keys;
		private List<int> values;

		public RM_BreachScars(Map map) : base(map)
		{
		}

		public int Count => scars.Count;

		/// <summary>Called before each raider fill of <paramref name="c"/>.</summary>
		public static void NoteFill(Map map, IntVec3 c)
		{
			RM_BreachScars s = map?.GetComponent<RM_BreachScars>();
			RM_MapComponent_Excavation eng = map?.GetComponent<RM_MapComponent_Excavation>();
			if (s == null || eng == null || !c.InBounds(map))
			{
				return;
			}
			int i = map.cellIndices.CellToIndex(c);
			s.scars.TryGetValue(i, out int had);
			s.scars[i] = RM_LadderParityMath.ScarAfterFill(had, eng.ExcavatedDepthAt(c));
		}

		/// <summary>The scar depth of a square (0: none); a healed scar is dropped on read.</summary>
		public int ScarAt(IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return 0;
			}
			int i = map.cellIndices.CellToIndex(c);
			if (!scars.TryGetValue(i, out int s))
			{
				return 0;
			}
			int now = map.GetComponent<RM_MapComponent_Excavation>()?.ExcavatedDepthAt(c) ?? s;
			if (RM_LadderParityMath.ScarHealed(s, now))
			{
				scars.Remove(i);
				return 0;
			}
			return s;
		}

		public IEnumerable<IntVec3> AllScars()
		{
			foreach (int i in new List<int>(scars.Keys))
			{
				IntVec3 c = map.cellIndices.IndexToCell(i);
				if (ScarAt(c) > 0)
				{
					yield return c;
				}
			}
		}

		public override void ExposeData()
		{
			Scribe_Collections.Look(ref scars, "RM_breachScars", LookMode.Value, LookMode.Value, ref keys, ref values);
			if (Scribe.mode == LoadSaveMode.PostLoadInit && scars == null)
			{
				scars = new Dictionary<int, int>();
			}
		}
	}

	/// <summary>Orders → "Repair breach": on a square raiders shovelled into, an ordinary dig-to order back to the depth it had
	/// (colonists assigned to Mining dig it at the normal cost). Drag over a causeway; only scarred squares take it.</summary>
	public class Designator_RM_RepairBreach : Designator_DigCanal
	{
		public Designator_RM_RepairBreach()
		{
			defaultLabel = "Repair breach";
			defaultDesc = "Dig a causeway raiders shovelled into your trench or pit back out to the depth it had. Only squares "
				+ "raiders filled take the order; colonists assigned to Mining do the work, at the normal digging cost.";
			hotKey = null;
		}

		public override string Label => defaultLabel;

		public override bool Visible => RM_LadderParitySettings.breachRepairEnabled && base.Visible;

		private int TargetFor(IntVec3 c)
		{
			RM_BreachScars s = Map.GetComponent<RM_BreachScars>();
			RM_MapComponent_Excavation eng = Map.GetComponent<RM_MapComponent_Excavation>();
			if (s == null || eng == null)
			{
				return 0;
			}
			return RM_LadderParityMath.RepairTarget(s.ScarAt(c), eng.ExcavatedDepthAt(c));
		}

		public override AcceptanceReport CanDesignateCell(IntVec3 c)
		{
			if (!RM_LadderParitySettings.breachRepairEnabled || !c.InBounds(Map))
			{
				return false;
			}
			int target = TargetFor(c);
			if (target <= 0)
			{
				return "Raiders did not fill this square (or it is repaired).";
			}
			return CanDigCell(c, target);
		}

		public override void DesignateSingleCell(IntVec3 c)
		{
			int target = TargetFor(c);
			if (target <= 0)
			{
				return;
			}
			Map.designationManager.TryRemoveDesignation(c, RimMandrakeFlowWorks_DefOf.RM_FillInCanal);
			if (Map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal) == null)
			{
				Map.designationManager.AddDesignation(new Designation(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal));
			}
			Map.GetComponent<RM_MapComponent_Excavation>()?.SetDigTarget(c, target);
		}

		public override void SelectedUpdate()
		{
			base.SelectedUpdate();
			RM_BreachScars s = Map?.GetComponent<RM_BreachScars>();
			if (s != null && s.Count > 0)
			{
				GenDraw.DrawFieldEdges(new List<IntVec3>(s.AllScars()), Color.yellow);
			}
		}
	}

	/// <summary>LADDER_PARITY_BUILD_NO_KEYS_REQUIRED Mod Settings. Defaults are the owner's 2026-10-23 ruling; all off = the
	/// behaviour before it (prison-door keys, raiders build every ladder, no carriers, no repair order, no wall ladders).</summary>
	public static class RM_LadderParitySettings
	{
		public static bool ladderNoKeys = true;
		/// <summary>Owner Q1: "as long as they fit in a 1x1 cell area" (PROVISIONAL size).</summary>
		public static float ladderMaxClimberBodySize = RM_LadderParityMath.DefaultMaxClimberBodySize;
		/// <summary>Owner Q2: how far a ladderless raider looks for a tree to chop.</summary>
		public static int raiderChopRadius = 30;
		/// <summary>PROVISIONAL: "sometimes but not always".</summary>
		public static float raidLadderChance = 0.35f;
		/// <summary>PROVISIONAL: "certainly not on every raider".</summary>
		public static float raidLadderCarrierShare = 0.25f;
		public static bool raiderTakeLadders = true;
		public static int raiderTakeLadderRadius = 25;
		public static bool breachRepairEnabled = true;
		public static bool ladderOverWalls = true;
		public static float wallLadderSlowFactor = RM_LadderParityMath.DefaultWallLadderSlowFactor;

		// FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING: MUST stay below the LAST public setting field.
		private static readonly Dictionary<string, object> shippedDefaults = RM_SettingsReset.Snapshot(typeof(RM_LadderParitySettings));

		public static void ResetAll()
		{
			RM_SettingsReset.ResetAll(typeof(RM_LadderParitySettings), shippedDefaults);
		}

		public static void ExposeData()
		{
			Scribe_Values.Look(ref ladderNoKeys, "ladderNoKeys", true);
			Scribe_Values.Look(ref ladderMaxClimberBodySize, "ladderMaxClimberBodySize", RM_LadderParityMath.DefaultMaxClimberBodySize);
			Scribe_Values.Look(ref raiderChopRadius, "raiderChopRadius", 30);
			Scribe_Values.Look(ref raidLadderChance, "raidLadderChance", 0.35f);
			Scribe_Values.Look(ref raidLadderCarrierShare, "raidLadderCarrierShare", 0.25f);
			Scribe_Values.Look(ref raiderTakeLadders, "raiderTakeLadders", true);
			Scribe_Values.Look(ref raiderTakeLadderRadius, "raiderTakeLadderRadius", 25);
			Scribe_Values.Look(ref breachRepairEnabled, "breachRepairEnabled", true);
			Scribe_Values.Look(ref ladderOverWalls, "ladderOverWalls", true);
			Scribe_Values.Look(ref wallLadderSlowFactor, "wallLadderSlowFactor", RM_LadderParityMath.DefaultWallLadderSlowFactor);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Ladders: no keys");
			RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, ResetAll);
			list.CheckboxLabeled("Ladders have no keys", ref ladderNoKeys,
				"On, a lowered ladder is an open door: every creature that can climb one climbs it, yours or the raiders', "
			  + "prisoners and wild animals too (a prison ladder left down is a prison door left open). Raise a wall ladder to "
			  + "shut it (raised, nobody climbs it). Off: hostiles climb only their own raid's ladders, wild animals never, "
			  + "prisoners only in a prison break.");
			list.Label("  Biggest creature that climbs a ladder: body size " + ladderMaxClimberBodySize.ToString("0.0"), tooltip:
				"A ladder is one square wide. A creature climbs one if it is no bigger than this, has no wheels, and has arms, "
			  + "jumps, or slithers (no legs). A person is 1.0. Some creatures carry their own yes/no.");
			ladderMaxClimberBodySize = Mathf.Round(list.Slider(ladderMaxClimberBodySize, 0.5f, 3f) * 10f) / 10f;
			list.Label("  Raids that bring ladders: " + Mathf.RoundToInt(raidLadderChance * 100f) + "%", tooltip:
				"This share of raids (never a siege) arrive with portable ladders. 0% = raiders build every ladder on the spot.");
			raidLadderChance = Mathf.Round(list.Slider(raidLadderChance, 0f, 1f) * 20f) / 20f;
			list.Label("  Raiders in such a raid who carry one: " + Mathf.RoundToInt(raidLadderCarrierShare * 100f) + "%", tooltip:
				"At least one, never every raider. A carried ladder is set in about 4 s; one built on the spot takes about 10 s plus 1 s a metre.");
			raidLadderCarrierShare = Mathf.Round(list.Slider(raidLadderCarrierShare, 0.05f, 0.9f) * 20f) / 20f;
			list.CheckboxLabeled("  Raiders take ladders they find", ref raiderTakeLadders,
				"A raider who needs a ladder and carries none takes down a portable ladder (anyone's) near it and sets it where "
			  + "it needs one. Your colonists can uninstall raiders' portable ladders like their own.");
			list.Label("  How far a raider goes for one: " + raiderTakeLadderRadius + " squares");
			raiderTakeLadderRadius = Mathf.RoundToInt(list.Slider(raiderTakeLadderRadius, 5f, 60f));
			list.Label("  How far a raider goes to chop a tree for ladder wood: " + raiderChopRadius + " squares", tooltip:
				"Raiders carry no wood: one with no ladder to carry or take fells the nearest grown tree, keeps the logs and "
			  + "builds the ladder (12 wood). 0 = never; with no tree in reach they breach by filling instead.");
			raiderChopRadius = Mathf.RoundToInt(list.Slider(raiderChopRadius, 0f, 60f));
			list.CheckboxLabeled("Repair breach order", ref breachRepairEnabled,
				"Orders → Repair breach: dig a causeway raiders shovelled into a trench back to the depth it had.");
			list.CheckboxLabeled("Ladders go over walls", ref ladderOverWalls,
				"A portable ladder can stand against a single built wall (not a door or rock) and carries whoever stands on it "
			  + "over to the far side, one way, when the wall and both sides are open to the sky. Right-click the wall. "
			  + "Raiders with no way in who carry a ladder set it and go over.");
			list.Label("  Ladder over a wall: x" + wallLadderSlowFactor.ToString("0") + " a step", tooltip:
				"How many of the climber's own steps the climb takes (climbing gear: see Climbing over walls).");
			wallLadderSlowFactor = Mathf.Round(list.Slider(wallLadderSlowFactor, 1f, 20f));
		}
	}
}
