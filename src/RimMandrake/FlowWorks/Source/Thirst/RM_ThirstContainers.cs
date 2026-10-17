using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Thirst
{
	/// <summary>THIRST_RULES_BUILD_SALT_OFF_THE_MENU (04-merged.md §8.2 step 3): buckets and barrels are drinkable, a 1.5 L
	/// draw at a time, so a container remembers how much has been drawn from it (§1: "partial draws from buckets/barrels
	/// need a saved litres state on the container"). Every reader of a container's contents goes through
	/// RM_ContainerMaterials.UnitsIn, which subtracts what was drawn, so a part-drunk bucket pours only what is left. A
	/// part-drawn container never stacks (two buckets with different contents are not one stack).</summary>
	public class CompProperties_RM_DrawnLitres : CompProperties
	{
		public CompProperties_RM_DrawnLitres()
		{
			compClass = typeof(CompRM_DrawnLitres);
		}
	}

	public class CompRM_DrawnLitres : ThingComp
	{
		/// <summary>Tank units (decilitres) already drawn from this one container.</summary>
		public int drawnUnits;

		public static int DrawnUnits(Thing t)
		{
			return t?.TryGetComp<CompRM_DrawnLitres>()?.drawnUnits ?? 0;
		}

		public override void PostExposeData()
		{
			Scribe_Values.Look(ref drawnUnits, "drawnUnits", 0);
		}

		public override bool AllowStackWith(Thing other)
		{
			return drawnUnits == 0 && DrawnUnits(other) == 0;
		}

		public override string CompInspectStringExtra()
		{
			if (drawnUnits <= 0)
			{
				return null;
			}
			return "Partly drunk: " + RM_Volume.Litres(drawnUnits).ToString("0.#") + " L taken out.";
		}
	}

	/// <summary>Drink 1.5 L from a filled bucket or barrel lying on the map. One container of a stack is split off and
	/// marked; when nothing is left in it, it becomes the dirty (or empty) container, like a drunk bottle.</summary>
	public class JobDriver_RM_DrinkFromContainer : JobDriver
	{
		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, 1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
			Toil drink = Toils_General.Wait(RM_ThirstMath.TankDrinkTicks).WithProgressBarToilDelay(TargetIndex.A);
			drink.FailOnCannotTouch(TargetIndex.A, PathEndMode.ClosestTouch);
			yield return drink;
			Toil finish = ToilMaker.MakeToil("RM_DrinkFromContainer");
			finish.initAction = delegate
			{
				Thing stack = job.targetA.Thing;
				RM_BottledLiquidExtension ext = stack?.def.GetModExtension<RM_BottledLiquidExtension>();
				if (ext?.liquid == null || !stack.Spawned)
				{
					return;
				}
				IntVec3 at = stack.Position;
				Thing one = stack.stackCount > 1 ? stack.SplitOff(1) : stack;
				CompRM_DrawnLitres comp = one.TryGetComp<CompRM_DrawnLitres>();
				int left = RM_ContainerMaterials.UnitsIn(one, ext.liquid, ext.size);
				int take = System.Math.Min(left, RM_Volume.Units(RM_ThirstMath.TankDrinkLitres));
				if (comp == null || take <= 0)
				{
					if (one != stack && !one.Spawned)
					{
						RM_LiquidBottleUtility.PlacePaidFor(one, at, Map);
					}
					return;
				}
				comp.drawnUnits += take;
				if (take >= left)
				{
					// drunk dry: the dirty (or empty) container of the same size and material takes its place
					ThingDef residue = RimMandrakeFlowWorksSettings.bottleDirtyStageEnabled
						? RM_LiquidBottleUtility.DirtyDefFor(ext.size) : RM_LiquidBottleUtility.EmptyDefFor(ext.size);
					Thing empty = RM_LiquidBottleUtility.MakeContainer(residue, one);
					one.Destroy();
					RM_LiquidBottleUtility.PlacePaidFor(empty, at, Map);
				}
				else if (one != stack)
				{
					RM_LiquidBottleUtility.PlacePaidFor(one, at, Map);
				}
				RM_ThirstUtility.Drink(pawn, ext.liquid, RM_Volume.Litres(take), null, RM_DrinkSource.Container);
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}

	public static class RM_ThirstContainerUtility
	{
		private static List<ThingDef> drinkableContainers;

		/// <summary>Every filled bucket and barrel holding a liquid with a thirstQuality.</summary>
		public static List<ThingDef> DrinkableContainers
		{
			get
			{
				if (drinkableContainers == null)
				{
					drinkableContainers = new List<ThingDef>();
					foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
					{
						RM_BottledLiquidExtension ext = d.GetModExtension<RM_BottledLiquidExtension>();
						if (ext?.liquid != null && ext.size != RM_ContainerSize.Bottle && ext.liquid.thirstQuality.HasValue
							&& d.HasComp(typeof(CompRM_DrawnLitres)))
						{
							drinkableContainers.Add(d);
						}
					}
				}
				return drinkableContainers;
			}
		}

		/// <summary>The best bucket or barrel on the map this pawn may drink from (use class, quality, distance), with a
		/// drink's worth or less left in it.</summary>
		public static Thing BestContainer(Pawn pawn, float level, out RM_DrinkUse use, out RM_WaterQuality quality,
			out float dist, RM_DrinkUse? only = null)
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
			foreach (ThingDef def in DrinkableContainers)
			{
				List<Thing> things = map.listerThings.ThingsOfDef(def);
				for (int i = 0; i < things.Count; i++)
				{
					Thing t = things[i];
					LiquidDef l = t.def.GetModExtension<RM_BottledLiquidExtension>().liquid;
					if (!RM_ThirstUtility.MayDrink(pawn, l, level, only))
					{
						continue;
					}
					RM_DrinkUse u = RM_ThirstUtility.UseOf(l);
					RM_WaterQuality q = RM_ThirstUtility.Effective(l);
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
}
