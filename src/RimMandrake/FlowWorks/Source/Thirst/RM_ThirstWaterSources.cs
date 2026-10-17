using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Thirst
{
	// THIRST_RULES_BUILD_SALT_OFF_THE_MENU, the rest of the source adapter and owner Q12 (2026-10-17, design
	// 04-merged.md §8.3): water items other mods already ship, snow and ice gathered into water, and blood for sanguophages.

	/// <summary>On a water ITEM another mod ships (blue-ice meltwater, distilled water, stilled water, melted stonewater; by
	/// patch, Patches/Thirst/RM_WaterItems.xml): a thirsty pawn drinks one as <see cref="litres"/> of <see cref="liquid"/>,
	/// at <see cref="quality"/> when set (distilled grade), under that row's use class. "The meltwater can is folded into the
	/// registry as a potable water item" (§8.3).</summary>
	public class RM_WaterItemExtension : DefModExtension
	{
		public LiquidDef liquid;
		public float litres = 1f;
		public LiquidThirstQuality? quality;
	}

	public static class RM_WaterItemUtility
	{
		private static List<ThingDef> waterItems;

		public static List<ThingDef> WaterItems
		{
			get
			{
				if (waterItems == null)
				{
					waterItems = new List<ThingDef>();
					foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
					{
						if (d.GetModExtension<RM_WaterItemExtension>()?.liquid != null)
						{
							waterItems.Add(d);
						}
					}
				}
				return waterItems;
			}
		}

		public static RM_WaterQuality QualityOf(RM_WaterItemExtension ext)
		{
			RM_WaterQuality q = ext.quality.HasValue ? (RM_WaterQuality)(int)ext.quality.Value : RM_ThirstUtility.Effective(ext.liquid);
			return RM_ThirstMath.Effective(q, RM_ThirstSettings.waterQualityEffects);
		}

		/// <summary>The best water item on the map this pawn may drink (use class, quality, distance).</summary>
		public static Thing BestItem(Pawn pawn, float level, out RM_DrinkUse use, out RM_WaterQuality quality, out float dist,
			RM_DrinkUse? only = null)
		{
			use = RM_DrinkUse.Never;
			quality = RM_WaterQuality.Slime;
			dist = float.MaxValue;
			Thing best = null;
			Map map = pawn.Map;
			if (map == null)
			{
				return null;
			}
			float maxSq = RM_ThirstUtility.SearchRadius * RM_ThirstUtility.SearchRadius * 4f;
			foreach (ThingDef def in WaterItems)
			{
				RM_WaterItemExtension ext = def.GetModExtension<RM_WaterItemExtension>();
				if (!RM_ThirstUtility.MayDrink(pawn, ext.liquid, level, only))
				{
					continue;
				}
				RM_DrinkUse u = RM_ThirstUtility.UseOf(ext.liquid);
				RM_WaterQuality q = QualityOf(ext);
				List<Thing> things = map.listerThings.ThingsOfDef(def);
				for (int i = 0; i < things.Count; i++)
				{
					Thing t = things[i];
					float d = (t.Position - pawn.Position).LengthHorizontalSquared;
					if (d > maxSq || (best != null && !RM_ThirstMath.Better(u, q, d, use, quality, dist)))
					{
						continue;
					}
					if (t.IsForbidden(pawn) || !pawn.CanReserveAndReach(t, PathEndMode.ClosestTouch, Danger.Some, 1, 1))
					{
						continue;
					}
					best = t;
					use = u;
					quality = q;
					dist = d;
				}
			}
			return best;
		}
	}

	/// <summary>Drink one water item where it lies.</summary>
	public class JobDriver_RM_DrinkWaterItem : JobDriver
	{
		private const int DrinkTicks = 90;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, 1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
			Toil drink = Toils_General.Wait(DrinkTicks).WithProgressBarToilDelay(TargetIndex.A);
			drink.FailOnCannotTouch(TargetIndex.A, PathEndMode.ClosestTouch);
			yield return drink;
			Toil finish = ToilMaker.MakeToil("RM_DrinkWaterItem");
			finish.initAction = delegate
			{
				Thing t = job.targetA.Thing;
				RM_WaterItemExtension ext = t?.def.GetModExtension<RM_WaterItemExtension>();
				if (ext?.liquid == null || !t.Spawned)
				{
					return;
				}
				Thing one = t.SplitOff(1);
				RM_ThirstUtility.Drink(pawn, ext.liquid, ext.litres, one, RM_DrinkSource.Bottle, RM_WaterItemUtility.QualityOf(ext));
				one.Destroy();
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}

	/// <summary>Owner, 2026-10-17 (card write-in): "blood absolutely counts as hemogen fully" -- for a sanguophage (any pawn
	/// with a hemogen gene) a hemogen pack also quenches thirst as one full drink (a 1.5 L bottle's worth). Patched onto
	/// HemogenPack's outcome doers (Patches/Thirst/RM_SanguophageBlood.xml); vanilla's own hemogen doer still runs.</summary>
	public class IngestionOutcomeDoer_RM_BloodQuench : IngestionOutcomeDoer
	{
		protected override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
		{
			if (pawn?.genes == null || !RM_ThirstSettings.sanguophageBloodQuenches || pawn.genes.GetFirstGeneOfType<Gene_Hemogen>() == null)
			{
				return;
			}
			RM_ThirstUtility.Drink(pawn, RimMandrakeFlowWorks_DefOf.RM_Liquid_FreshWater,
				RM_ThirstMath.TankDrinkLitres * System.Math.Max(1, ingestedCount), ingested);
		}
	}

	// ── snow and ice (owner write-in, Q12: "Ice/snow should be gatherable and turn into water (ice/snow buckets, ice
	// blocks, etc. There is already an ice block you can mine on the night side for example)") ─────────────────────────

	/// <summary>A bucket of snow (or ice chips) melts into a bucket of fresh water after enough time above 0 °C (vanilla
	/// temperature only, one kind of heat); a stove bill melts it at once (Defs/Thirst/RM_Thirst_SnowIce.xml).</summary>
	public class CompProperties_RM_Melt : CompProperties
	{
		public ThingDef meltsTo;
		public int ticksAboveZero = 5000;

		public CompProperties_RM_Melt()
		{
			compClass = typeof(CompRM_Melt);
		}
	}

	public class CompRM_Melt : ThingComp
	{
		private int warmTicks;

		private CompProperties_RM_Melt Props => (CompProperties_RM_Melt)props;

		public override void CompTickRare()
		{
			if (Props.meltsTo == null || parent.MapHeld == null)
			{
				return;
			}
			if (parent.AmbientTemperature > 0f)
			{
				warmTicks += GenTicks.TickRareInterval;
			}
			if (warmTicks < Props.ticksAboveZero)
			{
				return;
			}
			Map map = parent.MapHeld;
			IntVec3 at = parent.PositionHeld;
			int n = parent.stackCount;
			if (parent.Spawned)
			{
				Thing water = RM_LiquidBottleUtility.MakeContainer(Props.meltsTo, parent);
				water.stackCount = n;
				parent.Destroy();
				RM_LiquidBottleUtility.PlacePaidFor(water, at, map);
			}
			else if (parent.holdingOwner != null)
			{
				ThingOwner owner = parent.holdingOwner;
				Thing water = RM_LiquidBottleUtility.MakeContainer(Props.meltsTo, parent);
				water.stackCount = n;
				parent.Destroy();
				owner.TryAdd(water);
			}
		}

		public override void PostExposeData()
		{
			Scribe_Values.Look(ref warmTicks, "warmTicks", 0);
		}

		public override bool AllowStackWith(Thing other)
		{
			return true;
		}

		public override void PreAbsorbStack(Thing otherStack, int count)
		{
			// the warmer pile sets the clock: a merged stack never melts later than its warmer half would have
			CompRM_Melt o = otherStack.TryGetComp<CompRM_Melt>();
			if (o != null && o.warmTicks > warmTicks)
			{
				warmTicks = o.warmTicks;
			}
		}

		public override void PostSplitOff(Thing piece)
		{
			CompRM_Melt p = piece.TryGetComp<CompRM_Melt>();
			if (p != null)
			{
				p.warmTicks = warmTicks;
			}
		}

		public override string CompInspectStringExtra()
		{
			if (Props.ticksAboveZero <= 0)
			{
				return null;
			}
			return warmTicks > 0
				? "Melting: " + (100f * warmTicks / Props.ticksAboveZero).ToString("F0") + "%"
				: "Frozen (melts above 0°C)";
		}
	}

	/// <summary>On a melt RecipeDef: the filled container the bucket among its ingredients becomes.</summary>
	public class RM_FillBucketRecipeExtension : DefModExtension
	{
		public ThingDef filled;
	}

	/// <summary>Melt bills (ice blocks + an empty bucket, or a bucket of snow) make a bucket of water. A vanilla product
	/// cannot do it: a stuffed bucket made by a bill takes its stuff from the "dominant ingredient" (an ice block, which is
	/// no stuff), so the bucket among the ingredients is turned into the filled one as it is consumed instead, keeping its
	/// own material and look. Use "do X times" bills: the recipe lists no product to count.</summary>
	public class RecipeWorker_RM_FillBucket : RecipeWorker
	{
		public override void ConsumeIngredient(Thing ingredient, RecipeDef recipe, Map map)
		{
			ThingDef filled = recipe.GetModExtension<RM_FillBucketRecipeExtension>()?.filled;
			RM_BottledLiquidExtension ext = ingredient.def.GetModExtension<RM_BottledLiquidExtension>();
			bool isBucket = ingredient.def == RM_ThirstDefOf.RM_BucketSnow || (ext != null && ext.IsEmpty && ext.size == RM_ContainerSize.Bucket);
			if (filled != null && isBucket && map != null)
			{
				IntVec3 at = ingredient.PositionHeld;
				for (int i = 0; i < ingredient.stackCount; i++)
				{
					Thing water = RM_LiquidBottleUtility.MakeContainer(filled, ingredient);
					RM_LiquidBottleUtility.PlacePaidFor(water, at, map);
				}
			}
			base.ConsumeIngredient(ingredient, recipe, map);
		}
	}

	public static class RM_SnowUtility
	{
		/// <summary>Snow this deep or more is worth a bucket; a gathered bucket takes this much off the cell.</summary>
		public const float GatherDepth = 0.4f;
		public const float Radius = 40f;

		/// <summary>Snow deep enough, or an ice floor (vanilla Ice: frozen water, never used up), in the open.</summary>
		public static bool Gatherable(Map map, IntVec3 c)
		{
			if (!c.InBounds(map) || !c.Standable(map))
			{
				return false;
			}
			if (map.snowGrid.GetDepth(c) >= GatherDepth)
			{
				return true;
			}
			TerrainDef t = map.terrainGrid.TerrainAt(c);
			return t == TerrainDefOf.Ice;
		}

		private static readonly Dictionary<int, (int tick, IntVec3 cell)> cache = new Dictionary<int, (int, IntVec3)>();
		private const int NothingMarkTicks = 600;

		/// <summary>The nearest reachable gatherable cell: one radial walk per pawn per tick, and a pawn that found nothing
		/// is not searched again for 600 ticks (a snowless map must not pay a walk per empty bucket per scan).</summary>
		public static IntVec3 FindCell(Pawn pawn)
		{
			int now = Find.TickManager.TicksGame;
			if (cache.TryGetValue(pawn.thingIDNumber, out var hit) && (hit.tick == now
				|| (!hit.cell.IsValid && now > hit.tick && now - hit.tick < NothingMarkTicks)))
			{
				return hit.cell;
			}
			IntVec3 found = IntVec3.Invalid;
			Map map = pawn.Map;
			int fails = 0;
			foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, Radius, true))
			{
				if (!Gatherable(map, c))
				{
					continue;
				}
				if (c.IsForbidden(pawn) || !pawn.CanReserveAndReach(c, PathEndMode.Touch, Danger.Some))
				{
					if (++fails > 40)
					{
						break;
					}
					continue;
				}
				found = c;
				break;
			}
			cache[pawn.thingIDNumber] = (now, found);
			return found;
		}
	}

	/// <summary>Snow and ice are potable water (Q12), so they are gathered unasked, but only where no liquid fresh water
	/// can fill the bucket (a pond within reach always wins): an empty bucket is carried to snow or an ice floor and
	/// filled with snow.</summary>
	public class WorkGiver_RM_GatherSnow : WorkGiver_Scanner
	{
		public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForDef(RimMandrakeFlowWorks_DefOf.RM_BucketEmpty);

		public override PathEndMode PathEndMode => PathEndMode.ClosestTouch;

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			return !RM_ThirstSettings.snowGathering || RM_ThirstDefOf.RM_BucketSnow == null || pawn.Map == null;
		}

		public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			if (t.IsForbidden(pawn) || !pawn.CanReserve(t, 1, 1, null, forced))
			{
				return false;
			}
			if (!forced && RM_LiquidBottleUtility.TryFindFillCell(pawn, t, out _, out _, out _, false))
			{
				return false;   // liquid fresh water in reach: the ordinary fill job takes this bucket
			}
			return RM_SnowUtility.FindCell(pawn).IsValid;
		}

		public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			IntVec3 cell = RM_SnowUtility.FindCell(pawn);
			if (!cell.IsValid)
			{
				return null;
			}
			Job job = JobMaker.MakeJob(RM_ThirstDefOf.RM_GatherSnow, t, cell);
			job.count = 1;
			return job;
		}
	}

	public class JobDriver_RM_GatherSnow : JobDriver
	{
		private const int ScoopTicks = 240;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, 1, null, errorOnFailed)
				&& pawn.Reserve(job.targetB, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDestroyedNullOrForbidden(TargetIndex.A);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
			yield return Toils_Haul.StartCarryThing(TargetIndex.A);
			yield return Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.Touch);
			Toil scoop = Toils_General.Wait(ScoopTicks).WithProgressBarToilDelay(TargetIndex.B);
			scoop.FailOn(() => !RM_SnowUtility.Gatherable(Map, job.targetB.Cell));
			yield return scoop;
			Toil finish = ToilMaker.MakeToil("RM_GatherSnow");
			finish.initAction = delegate
			{
				Thing carried = pawn.carryTracker.CarriedThing;
				IntVec3 c = job.targetB.Cell;
				if (carried == null || !RM_SnowUtility.Gatherable(Map, c))
				{
					return;
				}
				if (Map.snowGrid.GetDepth(c) >= RM_SnowUtility.GatherDepth)
				{
					Map.snowGrid.AddDepth(c, -RM_SnowUtility.GatherDepth);
				}
				Thing snow = RM_LiquidBottleUtility.MakeContainer(RM_ThirstDefOf.RM_BucketSnow, carried);
				pawn.carryTracker.innerContainer.Remove(carried);
				carried.Destroy();
				RM_LiquidBottleUtility.PlacePaidFor(snow, pawn.Position, Map);
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}
}
