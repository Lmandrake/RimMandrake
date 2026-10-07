using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.RustCathedral.Hum
{
	// RUSTCATHEDRAL_HULL_BOLTS_BUILD_1 -- hull bolts: living bolts that ride a gravship for good.
	//
	// Boarding: a prefix on GravshipUtility.GenerateGravship (the one call that turns the landed ship into a
	// world object) swaps 0-3 living bolts within 4 cells of the substructure for RM_HullBolt pawns standing
	// on outer substructure cells. The engine's own Gravship.CopyCellContents then carries them like any
	// pawn on the substructure (ThingDef.bringAlongOnGravship defaults true; AddThing takes pawns) -- no
	// custom travel code. RM_CompHullBound keeps them on the outer hull afterwards.
	//
	// Spied on: RM_GameComponent_HullBoltWitness keeps a ledger of RM_CathedralWitnessDef acts while any hull
	// bolt exists; each act makes every hull bolt stop and turn (the tell). The next landing on Rust
	// Cathedral ground starts the hum with min(ledger, cap) irritation and clears the ledger.
	//
	// Realisation / reveal / dilemma: after N days aboard a hull bolt's cells carry a cold-blue mark and its
	// inspect pane says "The hull is cold under it."; M days later the next tell a hum reader sees sends the
	// dilemma letter, after which a colonist can pry a hull bolt off (curiosity + large irritation).
	//
	// Free tier only. Campaign owed (item): Ishko voicing the reveal, Regard posting. OnWitnessed is the hook.
	// All numbers PROVISIONAL (RustCathedralHumSettings, hull-bolt block).

	public enum RM_WitnessKind
	{
		Sell,
		Butcher,
		DestroyHullBolt,
		PryHullBolt
	}

	/// <summary>One kind of act the Cathedral hears through a hull bolt. Data, tunable.</summary>
	public class RM_CathedralWitnessDef : Def
	{
		public RM_WitnessKind kind;
		public List<ThingDef> things = new List<ThingDef>();
		public float weight = 1f;

		public bool Matches(RM_WitnessKind k, ThingDef thing)
		{
			if (k != kind)
			{
				return false;
			}
			if (things == null || things.Count == 0)
			{
				return true;
			}
			return thing != null && things.Contains(thing);
		}
	}

	public static class RM_HullBolts
	{
		public const string HullBoltDefName = "RM_HullBolt";
		public const string LivingBoltDefName = "RM_LivingBolt";
		public const string CuriosityDefName = "RM_BoltShedCuriosity";
		public const float BoardRadius = 4f;

		/// <summary>Campaign hook: (witness def name, weight) as each act is heard. The free tier only logs.</summary>
		public static Action<string, float> OnWitnessed;

		private static ThingDef hullBoltDef;
		private static PawnKindDef hullBoltKind;
		public static ThingDef HullBoltDef => hullBoltDef ?? (hullBoltDef = DefDatabase<ThingDef>.GetNamedSilentFail(HullBoltDefName));
		public static PawnKindDef HullBoltKind => hullBoltKind ?? (hullBoltKind = DefDatabase<PawnKindDef>.GetNamedSilentFail(HullBoltDefName));
		public static JobDef TellJob => DefDatabase<JobDef>.GetNamedSilentFail("RM_HullBoltTell");
		public static JobDef PryJob => DefDatabase<JobDef>.GetNamedSilentFail("RM_PryHullBolt");
		public static ThoughtDef SeenThought => DefDatabase<ThoughtDef>.GetNamedSilentFail("RM_HullBoltsSeen");

		public static bool Active => RustCathedralHumSettings.HullBoltsActive;

		public static bool IsHullBolt(Thing t) => t?.def != null && t.def.defName == HullBoltDefName;

		public static bool IsAnyBolt(ThingDef d) => d != null && (d.defName == HullBoltDefName || d.defName == LivingBoltDefName);

		public static bool IsCathedral(Map map) => map?.Biome != null && map.Biome.defName == RM_HumReading.CathedralBiomeDefName;

		public static Building_GravEngine EngineOn(Map map)
		{
			if (map == null || !ModsConfig.OdysseyActive)
			{
				return null;
			}
			Building_GravEngine e = GravshipUtility.GetPlayerGravEngine_NewTemp(map);
			return e != null && e.Spawned && e.Map == map ? e : null;
		}

		public static List<Pawn> HullBoltsOn(Map map)
		{
			List<Pawn> list = new List<Pawn>();
			ThingDef d = HullBoltDef;
			if (map == null || d == null)
			{
				return list;
			}
			List<Thing> things = map.listerThings.ThingsOfDef(d);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is Pawn p && !p.Dead)
				{
					list.Add(p);
				}
			}
			return list;
		}

		/// <summary>Any hull bolt in the game: spawned on a map, or riding a gravship in flight.</summary>
		public static bool AnyHullBoltExists()
		{
			ThingDef d = HullBoltDef;
			if (d == null)
			{
				return false;
			}
			foreach (Map m in Find.Maps)
			{
				if (m.listerThings.ThingsOfDef(d).Count > 0)
				{
					return true;
				}
			}
			if (ModsConfig.OdysseyActive && Find.CurrentGravship != null)
			{
				foreach (Pawn p in Find.CurrentGravship.Pawns)
				{
					if (p != null && p.def == d && !p.Dead)
					{
						return true;
					}
				}
			}
			return false;
		}

		// ---- the outer hull: substructure cells on the edge, outdoors where possible ----

		private static readonly Dictionary<int, int> edgeCacheTick = new Dictionary<int, int>();
		private static readonly Dictionary<int, List<IntVec3>> edgeCache = new Dictionary<int, List<IntVec3>>();
		private static readonly Dictionary<int, HashSet<IntVec3>> edgeSetCache = new Dictionary<int, HashSet<IntVec3>>();

		public static List<IntVec3> HullCells(Map map)
		{
			if (map == null)
			{
				return new List<IntVec3>();
			}
			int now = Find.TickManager.TicksGame;
			if (edgeCacheTick.TryGetValue(map.uniqueID, out int at) && now - at < 600 && edgeCache.TryGetValue(map.uniqueID, out List<IntVec3> cached))
			{
				return cached;
			}
			List<IntVec3> cells = ComputeHullCells(map, EngineOn(map));
			edgeCache[map.uniqueID] = cells;
			edgeSetCache[map.uniqueID] = new HashSet<IntVec3>(cells);
			edgeCacheTick[map.uniqueID] = now;
			return cells;
		}

		public static bool IsHullCell(IntVec3 c, Map map)
		{
			HullCells(map);
			return edgeSetCache.TryGetValue(map.uniqueID, out HashSet<IntVec3> set) && set.Contains(c);
		}

		public static List<IntVec3> ComputeHullCells(Map map, Building_GravEngine engine)
		{
			List<IntVec3> outdoor = new List<IntVec3>();
			List<IntVec3> any = new List<IntVec3>();
			if (engine == null)
			{
				return outdoor;
			}
			HashSet<IntVec3> sub = engine.ValidSubstructure;
			foreach (IntVec3 c in sub)
			{
				bool edge = false;
				for (int i = 0; i < 4 && !edge; i++)
				{
					edge = !sub.Contains(c + GenAdj.CardinalDirections[i]);
				}
				if (!edge || !c.InBounds(map) || !c.Standable(map))
				{
					continue;
				}
				any.Add(c);
				Room room = c.GetRoom(map);
				if (room == null || room.PsychologicallyOutdoors)
				{
					outdoor.Add(c);
				}
			}
			return outdoor.Count > 0 ? outdoor : any;
		}

		public static IntVec3 NearestHullCell(Map map, IntVec3 from, float maxDist = 9999f)
		{
			IntVec3 best = IntVec3.Invalid;
			float bestD = maxDist * maxDist;
			List<IntVec3> cells = HullCells(map);
			for (int i = 0; i < cells.Count; i++)
			{
				float d = (cells[i] - from).LengthHorizontalSquared;
				if (d < bestD)
				{
					bestD = d;
					best = cells[i];
				}
			}
			return best;
		}

		// ---- part 1: boarding ----

		/// <summary>Swap up to `forcedCount` (or a rolled count) living bolts near the substructure for hull bolts.
		/// Returns the hull bolts made. Called just before the engine captures the ship.</summary>
		public static List<Pawn> Board(Building_GravEngine engine, int forcedCount = -1)
		{
			List<Pawn> made = new List<Pawn>();
			Map map = engine?.Map;
			if (!Active || map == null || !IsCathedral(map) || HullBoltKind == null)
			{
				return made;
			}
			int count = forcedCount;
			if (count < 0)
			{
				count = Rand.Chance(RustCathedralHumSettings.hullBoltNoneChance)
					? 0
					: Rand.RangeInclusive(RustCathedralHumSettings.hullBoltBoardMin, Mathf.Max(RustCathedralHumSettings.hullBoltBoardMin, RustCathedralHumSettings.hullBoltBoardMax));
			}
			if (count <= 0)
			{
				return made;
			}
			HashSet<IntVec3> sub = engine.ValidSubstructure;
			List<Pawn> near = new List<Pawn>();
			ThingDef living = DefDatabase<ThingDef>.GetNamedSilentFail(LivingBoltDefName);
			if (living == null)
			{
				return made;
			}
			foreach (Thing t in map.listerThings.ThingsOfDef(living))
			{
				if (t is Pawn p && p.Spawned && !p.Dead && !p.Downed && NearSubstructure(p.Position, map, sub))
				{
					near.Add(p);
				}
			}
			near.SortBy(p => DistToSub(p.Position, sub));
			List<IntVec3> hull = ComputeHullCells(map, engine);
			for (int i = 0; i < near.Count && made.Count < count; i++)
			{
				IntVec3 cell = IntVec3.Invalid;
				float best = float.MaxValue;
				for (int j = 0; j < hull.Count; j++)
				{
					if (hull[j].GetFirstPawn(map) != null)
					{
						continue;
					}
					float d = (hull[j] - near[i].Position).LengthHorizontalSquared;
					if (d < best)
					{
						best = d;
						cell = hull[j];
					}
				}
				if (!cell.IsValid)
				{
					break;
				}
				Pawn bolt = PawnGenerator.GeneratePawn(HullBoltKind, null);
				near[i].Destroy(DestroyMode.Vanish);
				GenSpawn.Spawn(bolt, cell, map);
				made.Add(bolt);
			}
			if (made.Count > 0)
			{
				Find.LetterStack.ReceiveLetter("Bolts on the hull", "A few of the dancing bolts are still clinging to the hull.",
					LetterDefOf.NeutralEvent, new LookTargets(made));
			}
			return made;
		}

		private static bool NearSubstructure(IntVec3 c, Map map, HashSet<IntVec3> sub)
		{
			int n = GenRadial.NumCellsInRadius(BoardRadius);
			for (int i = 0; i < n; i++)
			{
				if (sub.Contains(c + GenRadial.RadialPattern[i]))
				{
					return true;
				}
			}
			return false;
		}

		private static float DistToSub(IntVec3 c, HashSet<IntVec3> sub)
		{
			int n = GenRadial.NumCellsInRadius(BoardRadius);
			for (int i = 0; i < n; i++)
			{
				if (sub.Contains(c + GenRadial.RadialPattern[i]))
				{
					return GenRadial.RadialPattern[i].LengthHorizontal;
				}
			}
			return BoardRadius + 1f;
		}

		/// <summary>Cathedral bolts drift toward a landed ship's edge: the nearest hull cell within reach, or Invalid.</summary>
		public static IntVec3 ShipEdgeAnchor(Pawn bolt)
		{
			Map map = bolt?.Map;
			if (!Active || map == null || EngineOn(map) == null)
			{
				return IntVec3.Invalid;
			}
			if (!Rand.Chance(RustCathedralHumSettings.hullBoltEdgePull))
			{
				return IntVec3.Invalid;
			}
			return NearestHullCell(map, bolt.Position, 25f);
		}

		// ---- part 3: the witness ----

		public static void Witness(RM_WitnessKind kind, ThingDef thing, Map where, IntVec3 at, Pawn skip = null)
		{
			if (!Active || !RustCathedralHumSettings.hullBoltWitnessEnabled)
			{
				return;
			}
			if (!AnyHullBoltExists())
			{
				return; // nothing aboard to hear it
			}
			List<RM_CathedralWitnessDef> defs = DefDatabase<RM_CathedralWitnessDef>.AllDefsListForReading;
			for (int i = 0; i < defs.Count; i++)
			{
				if (!defs[i].Matches(kind, thing))
				{
					continue;
				}
				float w = defs[i].weight * RustCathedralHumSettings.hullBoltWeightScale;
				RM_GameComponent_HullBoltWitness.Get()?.Record(defs[i], w);
				OnWitnessed?.Invoke(defs[i].defName, w);
				Tell(where, at, skip);
				return;
			}
		}

		/// <summary>Every hull bolt stops its figure and turns toward the act (or toward nothing, off-map).</summary>
		public static void Tell(Map where, IntVec3 at, Pawn skip = null)
		{
			JobDef tell = TellJob;
			if (tell == null)
			{
				return;
			}
			bool readerSaw = false;
			foreach (Map m in Find.Maps)
			{
				List<Pawn> bolts = HullBoltsOn(m);
				if (bolts.Count == 0)
				{
					continue;
				}
				for (int i = 0; i < bolts.Count; i++)
				{
					Pawn b = bolts[i];
					if (b == skip || !b.Spawned || b.Downed || b.jobs == null)
					{
						continue;
					}
					Job job = JobMaker.MakeJob(tell);
					if (m == where && at.IsValid)
					{
						job.targetA = at;
					}
					b.jobs.ClearQueuedJobs();
					b.jobs.StartJob(job, JobCondition.InterruptForced);
				}
				readerSaw |= RM_HumReading.AnyReaderOn(m);
			}
			RM_GameComponent_HullBoltWitness.Get()?.Notify_Tell(readerSaw);
		}

		// ---- part 5: prying ----

		public static bool PryAvailable => Active && (RM_GameComponent_HullBoltWitness.Get()?.revealSent ?? false);

		public static void Pry(Pawn bolt, Pawn by)
		{
			if (bolt == null || bolt.Destroyed)
			{
				return;
			}
			Map map = bolt.MapHeld;
			IntVec3 at = bolt.PositionHeld;
			ThingDef cur = DefDatabase<ThingDef>.GetNamedSilentFail(CuriosityDefName);
			bolt.Destroy(DestroyMode.Vanish);
			if (cur != null && map != null)
			{
				GenPlace.TryPlaceThing(ThingMaker.MakeThing(cur), at, map, ThingPlaceMode.Near);
			}
			// Recorded even if it was the last one: the ledger is the Cathedral's memory, not the bolts'.
			if (Active && RustCathedralHumSettings.hullBoltWitnessEnabled)
			{
				List<RM_CathedralWitnessDef> defs = DefDatabase<RM_CathedralWitnessDef>.AllDefsListForReading;
				for (int i = 0; i < defs.Count; i++)
				{
					if (defs[i].kind == RM_WitnessKind.PryHullBolt)
					{
						float w = defs[i].weight * RustCathedralHumSettings.hullBoltWeightScale;
						RM_GameComponent_HullBoltWitness.Get()?.Record(defs[i], w);
						OnWitnessed?.Invoke(defs[i].defName, w);
						break;
					}
				}
			}
			if (AnyHullBoltExists())
			{
				Tell(map, at);
			}
		}
	}

	// ---- the hull bolt's own comp: confinement, realisation, inspect lines ----

	public class CompProperties_HullBound : CompProperties
	{
		public CompProperties_HullBound()
		{
			compClass = typeof(RM_CompHullBound);
		}
	}

	public class RM_CompHullBound : ThingComp
	{
		public int boardedTick = -1;
		public string lastFigure;
		public readonly List<IntVec3> recentCells = new List<IntVec3>();
		private const int RecentMax = 8;

		private Pawn Bolt => parent as Pawn;

		public bool Realised => boardedTick >= 0 && RustCathedralHumSettings.hullBoltRealiseDays >= 0f
			&& Find.TickManager.TicksGame - boardedTick >= (int)(RustCathedralHumSettings.hullBoltRealiseDays * GenDate.TicksPerDay);

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			base.PostSpawnSetup(respawningAfterLoad);
			if (boardedTick < 0)
			{
				boardedTick = Find.TickManager.TicksGame;
			}
			recentCells.Clear();
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref boardedTick, "boardedTick", -1);
			Scribe_Values.Look(ref lastFigure, "lastFigure");
		}

		public override void CompTickRare()
		{
			base.CompTickRare();
			Pawn p = Bolt;
			if (p == null || !p.Spawned || p.Dead)
			{
				return;
			}
			if (Realised)
			{
				if (recentCells.Count == 0 || recentCells[recentCells.Count - 1] != p.Position)
				{
					recentCells.Add(p.Position);
					if (recentCells.Count > RecentMax)
					{
						recentCells.RemoveAt(0);
					}
				}
				RM_GameComponent_HullBoltWitness.Get()?.Notify_Realised();
			}
			// Confinement: off the hull and not already walking back -> walk to the nearest hull cell.
			if (p.Downed || RM_HullBolts.EngineOn(p.Map) == null || RM_HullBolts.IsHullCell(p.Position, p.Map))
			{
				return;
			}
			if (p.CurJob != null && p.CurJob.def == JobDefOf.Goto && p.CurJob.targetA.IsValid && RM_HullBolts.IsHullCell(p.CurJob.targetA.Cell, p.Map))
			{
				return;
			}
			IntVec3 back = RM_HullBolts.NearestHullCell(p.Map, p.Position);
			if (back.IsValid && p.CanReach(back, PathEndMode.OnCell, Danger.Deadly))
			{
				Job job = JobMaker.MakeJob(JobDefOf.Goto, back);
				job.locomotionUrgency = LocomotionUrgency.Jog;
				p.jobs.ClearQueuedJobs();
				p.jobs.StartJob(job, JobCondition.InterruptForced);
			}
		}

		public override string CompInspectStringExtra()
		{
			List<string> lines = new List<string>();
			if (Realised)
			{
				lines.Add("The hull is cold under it.");
			}
			if (!lastFigure.NullOrEmpty() && RustCathedralHumSettings.humMechanicEnabled && RM_HumReading.AnyReaderOn(parent.MapHeld))
			{
				lines.Add("Its figure: " + lastFigure + ".");
			}
			return lines.Count == 0 ? null : string.Join("\n", lines);
		}
	}

	// ---- the hull dance: the plateau's figures, snapped to the outer hull ----

	public class RM_JobGiver_HullDance : ThinkNode_JobGiver
	{
		public float chance = 0.35f;
		public float radius = 3f;
		public int steps = 5;

		private static readonly string[] FigureNames = { "a slow loop", "a lobed figure, petal by petal", "a straight line paced out and back" };

		public override ThinkNode DeepCopy(bool resolve = true)
		{
			RM_JobGiver_HullDance obj = (RM_JobGiver_HullDance)base.DeepCopy(resolve);
			obj.chance = chance;
			obj.radius = radius;
			obj.steps = steps;
			return obj;
		}

		protected override Job TryGiveJob(Pawn pawn)
		{
			Map map = pawn?.Map;
			if (map == null || pawn.jobs == null || !RustCathedralHumSettings.BoltDisplayActive || !Rand.Chance(chance))
			{
				return null;
			}
			bool onShip = RM_HullBolts.EngineOn(map) != null;
			int shape = Rand.RangeInclusive(0, 2);
			int lobes = Rand.RangeInclusive(2, 3);
			float phase = Rand.Range(0f, Mathf.PI * 2f);
			List<IntVec3> cells = new List<IntVec3>();
			for (int i = 0; i < steps; i++)
			{
				float ang = phase + (float)i / steps * Mathf.PI * 2f;
				float r = shape == 1 ? radius * (0.4f + 0.6f * Mathf.Abs(Mathf.Cos(ang * lobes))) : shape == 2 ? radius * Mathf.Cos(ang) : radius;
				IntVec3 c = pawn.Position + new IntVec3(Mathf.RoundToInt(Mathf.Cos(ang) * r), 0, Mathf.RoundToInt(Mathf.Sin(ang) * r));
				if (onShip)
				{
					c = RM_HullBolts.IsHullCell(c, map) ? c : RM_HullBolts.NearestHullCell(map, c, 3f);
				}
				if (!c.IsValid || c == pawn.Position || !c.InBounds(map) || !c.Standable(map) || cells.Contains(c))
				{
					continue;
				}
				if (!pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
				{
					continue;
				}
				cells.Add(c);
			}
			if (cells.Count == 0)
			{
				return null;
			}
			RM_CompHullBound comp = pawn.TryGetComp<RM_CompHullBound>();
			if (comp != null)
			{
				comp.lastFigure = FigureNames[shape];
			}
			for (int i = 1; i < cells.Count; i++)
			{
				pawn.jobs.jobQueue.EnqueueLast(Step(cells[i]));
			}
			return Step(cells[0]);
		}

		private static Job Step(IntVec3 c)
		{
			Job job = JobMaker.MakeJob(JobDefOf.Goto, c);
			job.locomotionUrgency = LocomotionUrgency.Jog;
			job.expiryInterval = 600;
			return job;
		}
	}

	/// <summary>Idle on the hull: a short wait, or a step to a hull cell nearby. Never into the ship.</summary>
	public class RM_JobGiver_HullIdle : ThinkNode_JobGiver
	{
		protected override Job TryGiveJob(Pawn pawn)
		{
			Map map = pawn?.Map;
			if (map != null && RM_HullBolts.EngineOn(map) != null && Rand.Chance(0.3f))
			{
				IntVec3 c = RM_HullBolts.NearestHullCell(map, pawn.Position + GenRadial.RadialPattern[Rand.RangeInclusive(1, 24)], 4f);
				if (c.IsValid && c != pawn.Position && pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
				{
					Job go = JobMaker.MakeJob(JobDefOf.Goto, c);
					go.locomotionUrgency = LocomotionUrgency.Walk;
					return go;
				}
			}
			Job wait = JobMaker.MakeJob(JobDefOf.Wait);
			wait.expiryInterval = 250;
			return wait;
		}
	}

	/// <summary>The tell: stop, turn toward the act, a few sparks. Nothing explains it.</summary>
	public class JobDriver_HullBoltTell : JobDriver
	{
		public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

		protected override IEnumerable<Toil> MakeNewToils()
		{
			Toil still = ToilMaker.MakeToil("HullBoltTell");
			still.initAction = delegate
			{
				pawn.pather?.StopDead();
				if (job.targetA.IsValid && job.targetA.Cell.IsValid)
				{
					pawn.rotationTracker.FaceCell(job.targetA.Cell);
				}
				if (pawn.Spawned)
				{
					FleckMaker.ThrowMicroSparks(pawn.DrawPos, pawn.Map);
				}
			};
			still.defaultCompleteMode = ToilCompleteMode.Delay;
			still.defaultDuration = 180;
			yield return still;
		}
	}

	/// <summary>Pry a hull bolt off: walk to it, work at it, it comes away as a shed curiosity.</summary>
	public class JobDriver_PryHullBolt : JobDriver
	{
		public const int WorkTicks = 300;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedOrNull(TargetIndex.A);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
			yield return Toils_General.Wait(WorkTicks, TargetIndex.A).WithProgressBarToilDelay(TargetIndex.A);
			Toil finish = ToilMaker.MakeToil("PryHullBoltFinish");
			finish.initAction = delegate
			{
				RM_HullBolts.Pry(job.targetA.Thing as Pawn, pawn);
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}

	public class FloatMenuOptionProvider_PryHullBolt : FloatMenuOptionProvider
	{
		protected override bool Drafted => true;
		protected override bool Undrafted => true;
		protected override bool Multiselect => false;
		protected override bool RequiresManipulation => true;

		protected override FloatMenuOption GetSingleOptionFor(Pawn clickedPawn, FloatMenuContext context)
		{
			if (!RM_HullBolts.IsHullBolt(clickedPawn) || !RM_HullBolts.PryAvailable || RM_HullBolts.PryJob == null)
			{
				return null;
			}
			Pawn worker = context.FirstSelectedPawn;
			if (worker == null || !worker.CanReserveAndReach(clickedPawn, PathEndMode.Touch, Danger.Deadly))
			{
				return new FloatMenuOption("Pry the hull bolt off (cannot reach)", null);
			}
			return new FloatMenuOption("Pry the hull bolt off", delegate
			{
				worker.jobs.TryTakeOrderedJob(JobMaker.MakeJob(RM_HullBolts.PryJob, clickedPawn), JobTag.Misc);
			});
		}
	}

	public class RM_ChoiceLetter_HullBolts : ChoiceLetter
	{
		public override IEnumerable<DiaOption> Choices
		{
			get
			{
				if (ArchivedOnly)
				{
					yield return Option_Close;
					yield break;
				}
				yield return new DiaOption("Pry them off")
				{
					action = delegate
					{
						RM_GameComponent_HullBoltWitness.Get()?.Choose(1);
						Messages.Message("Order a colonist to pry each hull bolt off: right-click the bolt.", MessageTypeDefOf.NeutralEvent, false);
						Find.LetterStack.RemoveLetter(this);
					},
					resolveTree = true
				};
				yield return new DiaOption("Leave them")
				{
					action = delegate
					{
						RM_GameComponent_HullBoltWitness.Get()?.Choose(2);
						Find.LetterStack.RemoveLetter(this);
					},
					resolveTree = true
				};
			}
		}
	}

	// ---- the ledger, the landing, the reveal, the pet memory ----

	public class RM_GameComponent_HullBoltWitness : GameComponent
	{
		public float total;
		public int entries;
		public List<string> log = new List<string>();
		public int markSinceTick = -1;
		public bool revealSent;
		public int choice; // 0 none, 1 remove, 2 leave
		public int lastArrivalTick = -999999;
		public int lastArrivalMapId = -1;
		private List<int> appliedMaps = new List<int>();

		public RM_GameComponent_HullBoltWitness(Game game)
		{
		}

		public static RM_GameComponent_HullBoltWitness Get() => Current.Game?.GetComponent<RM_GameComponent_HullBoltWitness>();

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref total, "total", 0f);
			Scribe_Values.Look(ref entries, "entries", 0);
			Scribe_Collections.Look(ref log, "log", LookMode.Value);
			Scribe_Values.Look(ref markSinceTick, "markSinceTick", -1);
			Scribe_Values.Look(ref revealSent, "revealSent", false);
			Scribe_Values.Look(ref choice, "choice", 0);
			Scribe_Values.Look(ref lastArrivalTick, "lastArrivalTick", -999999);
			Scribe_Values.Look(ref lastArrivalMapId, "lastArrivalMapId", -1);
			Scribe_Collections.Look(ref appliedMaps, "appliedMaps", LookMode.Value);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				log = log ?? new List<string>();
				appliedMaps = appliedMaps ?? new List<int>();
			}
		}

		public void Record(RM_CathedralWitnessDef def, float weight)
		{
			total += weight;
			entries++;
			log.Add(def.defName + " +" + weight.ToString("0.#"));
			if (log.Count > 20)
			{
				log.RemoveAt(0);
			}
		}

		public void Choose(int c) => choice = c;

		public void Notify_Realised()
		{
			if (markSinceTick < 0)
			{
				markSinceTick = Find.TickManager.TicksGame;
			}
		}

		public void Notify_Tell(bool readerSaw)
		{
			if (revealSent || !readerSaw || markSinceTick < 0 || !RM_HullBolts.Active)
			{
				return;
			}
			if (Find.TickManager.TicksGame - markSinceTick < (int)(RustCathedralHumSettings.hullBoltRevealDays * GenDate.TicksPerDay))
			{
				return;
			}
			SendReveal();
		}

		public void SendReveal()
		{
			revealSent = true;
			LetterDef def = DefDatabase<LetterDef>.GetNamedSilentFail("RM_HullBoltsDilemma");
			if (def == null)
			{
				return;
			}
			List<Pawn> bolts = new List<Pawn>();
			foreach (Map m in Find.Maps)
			{
				bolts.AddRange(RM_HullBolts.HullBoltsOn(m));
			}
			ChoiceLetter letter = LetterMaker.MakeLetter("The bolts on the hull",
				"They dance the plateau's figures, far from the plateau.\n\nEvery time something of the plateau's changes hands, they stop and turn to it, wherever the ship is.\n\nThey can be pried off. Or they can stay.",
				def, new LookTargets(bolts));
			Find.LetterStack.ReceiveLetter(letter);
		}

		public override void GameComponentTick()
		{
			int now = Find.TickManager.TicksGame;
			if (now % 250 != 0 || !RM_HullBolts.Active)
			{
				return;
			}
			CheckArrivals(now);
			if (now % 2500 == 0 && RustCathedralHumSettings.hullBoltPetMemoryEnabled)
			{
				PetMemories();
			}
		}

		/// <summary>Part 3, the consequence: a player ship standing on Cathedral ground for the first time since it
		/// landed starts the hum with the ledger already applied (capped), and the ledger clears.</summary>
		public void CheckArrivals(int now)
		{
			foreach (Map m in Find.Maps)
			{
				bool shipHere = RM_HullBolts.EngineOn(m) != null;
				if (!shipHere)
				{
					appliedMaps.Remove(m.uniqueID);
					continue;
				}
				if (appliedMaps.Contains(m.uniqueID) || !RM_HullBolts.IsCathedral(m))
				{
					continue;
				}
				appliedMaps.Add(m.uniqueID);
				ApplyArrival(m, now);
			}
		}

		public float ApplyArrival(Map m, int now)
		{
			if (total <= 0f || !RustCathedralHumSettings.humMechanicEnabled)
			{
				return 0f;
			}
			float applied = Mathf.Min(total, RustCathedralHumSettings.hullBoltIrritationCap);
			RM_MapComponent_BiomeAttitude.AddIrritation(m, applied);
			total = 0f;
			entries = 0;
			log.Clear();
			lastArrivalTick = now;
			lastArrivalMapId = m.uniqueID;
			Find.LetterStack.ReceiveLetter("Uneasy hum", "The hum is already uneasy.", LetterDefOf.NeutralEvent, new LookTargets(RM_HullBolts.EngineOn(m)));
			return applied;
		}

		/// <summary>For the hum reader's readout: within a day of an uneasy arrival on this map.</summary>
		public bool ArrivedUneasy(Map m) => m != null && m.uniqueID == lastArrivalMapId && Find.TickManager.TicksGame - lastArrivalTick < GenDate.TicksPerDay;

		private void PetMemories()
		{
			ThoughtDef seen = RM_HullBolts.SeenThought;
			if (seen == null)
			{
				return;
			}
			foreach (Map m in Find.Maps)
			{
				List<Pawn> bolts = RM_HullBolts.HullBoltsOn(m);
				if (bolts.Count == 0)
				{
					continue;
				}
				foreach (Pawn c in m.mapPawns.FreeColonistsSpawned)
				{
					if (!Rand.Chance(0.15f))
					{
						continue;
					}
					for (int i = 0; i < bolts.Count; i++)
					{
						if (bolts[i].Spawned && c.Position.InHorDistOf(bolts[i].Position, 10f) && GenSight.LineOfSight(c.Position, bolts[i].Position, m))
						{
							c.needs?.mood?.thoughts?.memories?.TryGainMemory(seen);
							break;
						}
					}
				}
			}
		}
	}

	/// <summary>Part 4's mark: a cold-blue tarnish drawn on the cells a realised hull bolt has stood on.</summary>
	public class RM_MapComponent_HullBoltMarks : MapComponent
	{
		private static Material mat;

		public RM_MapComponent_HullBoltMarks(Map map) : base(map)
		{
		}

		public static List<IntVec3> MarkedCells(Map m)
		{
			List<IntVec3> cells = new List<IntVec3>();
			foreach (Pawn b in RM_HullBolts.HullBoltsOn(m))
			{
				RM_CompHullBound comp = b.TryGetComp<RM_CompHullBound>();
				if (comp == null || !comp.Realised || !b.Spawned)
				{
					continue;
				}
				if (!cells.Contains(b.Position))
				{
					cells.Add(b.Position);
				}
				for (int i = 0; i < comp.recentCells.Count; i++)
				{
					if (!cells.Contains(comp.recentCells[i]))
					{
						cells.Add(comp.recentCells[i]);
					}
				}
			}
			return cells;
		}

		public override void MapComponentUpdate()
		{
			if (Find.CurrentMap != map || RM_HullBolts.HullBoltDef == null || map.listerThings.ThingsOfDef(RM_HullBolts.HullBoltDef).Count == 0)
			{
				return;
			}
			if (mat == null)
			{
				mat = SolidColorMaterials.SimpleSolidColorMaterial(new Color(0.55f, 0.75f, 1f, 0.28f));
			}
			float y = AltitudeLayer.FloorEmplacement.AltitudeFor();
			foreach (IntVec3 c in MarkedCells(map))
			{
				Vector3 pos = c.ToVector3Shifted();
				pos.y = y;
				Graphics.DrawMesh(MeshPool.plane10, pos, Quaternion.identity, mat, 0);
			}
		}
	}

	// ---- Harmony: boarding, sales, butchering, destroying ----

	[HarmonyPatch(typeof(GravshipUtility), nameof(GravshipUtility.GenerateGravship))]
	public static class HarmonyPatch_HullBolts_Board
	{
		public static void Prefix(Building_GravEngine engine)
		{
			try
			{
				RM_HullBolts.Board(engine);
			}
			catch (Exception e)
			{
				Log.Error("[RustCathedral] hull bolt boarding failed, launch continues without them: " + e);
			}
		}
	}

	[HarmonyPatch(typeof(Tradeable), nameof(Tradeable.ResolveTrade))]
	public static class HarmonyPatch_HullBolts_Sell
	{
		public static void Prefix(Tradeable __instance)
		{
			if (__instance == null || __instance.ActionToDo != TradeAction.PlayerSells || !RM_HullBolts.Active)
			{
				return;
			}
			Map map = TradeSession.playerNegotiator?.MapHeld;
			IntVec3 at = TradeSession.playerNegotiator?.PositionHeld ?? IntVec3.Invalid;
			RM_HullBolts.Witness(RM_WitnessKind.Sell, __instance.ThingDef, map, at);
		}
	}

	[HarmonyPatch(typeof(Corpse), nameof(Corpse.ButcherProducts))]
	public static class HarmonyPatch_HullBolts_Butcher
	{
		public static void Prefix(Corpse __instance)
		{
			if (__instance?.InnerPawn == null || !RM_HullBolts.IsAnyBolt(__instance.InnerPawn.def))
			{
				return;
			}
			RM_HullBolts.Witness(RM_WitnessKind.Butcher, __instance.InnerPawn.def, __instance.MapHeld, __instance.PositionHeld);
		}
	}

	[HarmonyPatch(typeof(Pawn), nameof(Pawn.Kill))]
	public static class HarmonyPatch_HullBolts_Kill
	{
		public static void Prefix(Pawn __instance, DamageInfo? dinfo)
		{
			if (!RM_HullBolts.IsHullBolt(__instance))
			{
				return;
			}
			Faction f = dinfo?.Instigator?.Faction;
			if (f == null || !f.IsPlayer)
			{
				return;
			}
			RM_HullBolts.Witness(RM_WitnessKind.DestroyHullBolt, __instance.def, __instance.MapHeld, __instance.PositionHeld, __instance);
		}
	}
}
