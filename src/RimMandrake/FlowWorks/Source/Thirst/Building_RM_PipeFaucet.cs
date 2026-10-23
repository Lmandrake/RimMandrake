using System.Collections.Generic;
using System.Text;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.Machinery;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Thirst
{
	/// <summary>PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE: a faucet set ON a universal pipe (PlaceWorker_RM_OnPipe, like a sprinkler
	/// head). It holds nothing itself: colonists drink at it and fill empty containers at it, and every litre comes out of the
	/// tanks on its pipe network (RM_LiquidNet.DrawPlan, the store a machine on that pipe would draw from: Dump tanks never
	/// give). The thirst rules treat it as a tap (RM_DrinkSource.Tank): free at home, awkward out in the field (owner Q1
	/// 2026-10-17, "cups, piped taps, any civilized access"). Mod Setting RM_ThirstSettings.pipeFaucetsEnabled (off: the
	/// faucet stands, dry).</summary>
	public class Building_RM_PipeFaucet : Building
	{
		/// <summary>A new faucet takes the look of the pipe it is set on (FAUCET_REDRAW_BORROWED_BLEED_WELL; art only).</summary>
		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			if (!respawningAfterLoad) Sprinklers.RM_SprinklerLook.MatchPipeUnder(this);
		}

		/// <summary>Distinct liquids the tanks on this faucet's net hold and would give to a machine, most held first.</summary>
		public static List<LiquidDef> NetLiquids(Thing faucet)
		{
			var held = new Dictionary<LiquidDef, int>();
			if (faucet?.Map == null || !faucet.Spawned)
			{
				return new List<LiquidDef>();
			}
			foreach (Building_LiquidTank t in RM_LiquidNet.TanksFor(faucet))
			{
				if (t.Empty || !t.GivesToMachines)
				{
					continue;
				}
				held.TryGetValue(t.storedLiquid, out int u);
				held[t.storedLiquid] = u + t.storedUnits;
			}
			var list = new List<LiquidDef>(held.Keys);
			list.Sort((a, b) => held[b] != held[a] ? held[b].CompareTo(held[a]) : string.CompareOrdinal(a.defName, b.defName));
			return list;
		}

		public static bool Works => RM_ThirstSettings.pipeFaucetsEnabled;

		/// <summary>Can the net give <paramref name="units"/> of <paramref name="liquid"/> through this faucet now?</summary>
		public static bool CanPour(Thing faucet, LiquidDef liquid, int units)
		{
			return Works && liquid != null && units > 0 && RM_LiquidNet.Available(faucet, liquid) >= units;
		}

		/// <summary>Draw exactly <paramref name="units"/> of <paramref name="liquid"/> from the faucet's net, all or nothing
		/// (a split leg puts a short draw back). True when it all came out.</summary>
		public static bool TryPour(Thing faucet, LiquidDef liquid, int units)
		{
			if (!CanPour(faucet, liquid, units))
			{
				return false;
			}
			List<(Building_LiquidTank tank, int units)> plan = RM_LiquidNet.DrawPlan(faucet, liquid, units);
			if (plan == null)
			{
				return false;
			}
			RM_TransferLeg source = RM_TransferLeg.Split(plan.Count, i => plan[i].units, (i, k) => plan[i].tank.CanProvide(k),
				(i, k) => plan[i].tank.TryRemoveLiquid(k), (i, k) => plan[i].tank.TryAddLiquid(liquid, k));
			RM_TransferLeg sink = RM_TransferLeg.Sink(k => { });
			if (RM_LiquidTransfer.Move(units, source, sink, out RM_MoveOutcome _) == units)
			{
				foreach ((Building_LiquidTank tank, int units) p in plan) RM_LiquidNet.Credit(faucet, p.tank, liquid, p.units, 60);   // credit site: faucet draw
				return true;
			}
			return false;
		}

		/// <summary>The liquid <paramref name="pawn"/> would drink here: the best use class, then quality (RM_ThirstMath.Better
		/// at equal distance), of what the net can pour one drink of. Null when nothing drinkable flows.</summary>
		public static LiquidDef DrinkFor(Pawn pawn, Thing faucet, float level, RM_DrinkUse? only, out RM_DrinkUse use,
			out RM_WaterQuality quality)
		{
			use = RM_DrinkUse.Never;
			quality = RM_WaterQuality.Slime;
			LiquidDef best = null;
			if (!Works)
			{
				return null;
			}
			int units = RM_Volume.Units(RM_ThirstMath.TankDrinkLitres);
			foreach (LiquidDef l in NetLiquids(faucet))
			{
				if (!RM_ThirstUtility.MayDrink(pawn, l, level, only) || !CanPour(faucet, l, units))
				{
					continue;
				}
				RM_DrinkUse u = RM_ThirstUtility.UseOf(l);
				RM_WaterQuality q = RM_ThirstUtility.Effective(l);
				if (best == null || RM_ThirstMath.Better(u, q, 0f, use, quality, 0f))
				{
					best = l;
					use = u;
					quality = q;
				}
			}
			return best;
		}

		/// <summary>The nearest reachable faucet of the pawn's faction that pours a drink <paramref name="pawn"/> may take (BestTank's
		/// twin).</summary>
		public static Building_RM_PipeFaucet BestFaucet(Pawn pawn, float level, out RM_DrinkUse use, out RM_WaterQuality quality,
			out float dist, RM_DrinkUse? only = null)
		{
			use = RM_DrinkUse.Never;
			quality = RM_WaterQuality.Slime;
			dist = float.MaxValue;
			Building_RM_PipeFaucet best = null;
			Map map = pawn.Map;
			if (!Works || map == null || pawn.Faction == null)
			{
				return null;
			}
			foreach (Building_RM_PipeFaucet f in map.listerBuildings.AllBuildingsColonistOfClass<Building_RM_PipeFaucet>())
			{
				if (f.Faction != pawn.Faction)
				{
					continue;
				}
				float d = (f.Position - pawn.Position).LengthHorizontalSquared;
				LiquidDef l = DrinkFor(pawn, f, level, only, out RM_DrinkUse u, out RM_WaterQuality q);
				if (l == null || (best != null && !RM_ThirstMath.Better(u, q, d, use, quality, dist)))
				{
					continue;
				}
				if (f.IsForbidden(pawn) || !pawn.CanReach(f, PathEndMode.Touch, Danger.Some))
				{
					continue;
				}
				best = f;
				use = u;
				quality = q;
				dist = d;
			}
			return best;
		}

		/// <summary>A liquid this faucet can fill <paramref name="container"/> with (size form exists, the material holds it, the
		/// net has a full container's worth). Unordered work never draws a liquid that is not auto-gathered (brine, salt: the
		/// tank rule, THIRST_RULES_BUILD_SALT_OFF_THE_MENU).</summary>
		public static LiquidDef FillFor(Thing faucet, Thing container, RM_ContainerSize size, bool ordered, out string refusal)
		{
			refusal = null;
			if (!Works)
			{
				return null;
			}
			foreach (LiquidDef l in NetLiquids(faucet))
			{
				if (!ordered && !l.AutoGathered)
				{
					continue;
				}
				if (l.bottled?.FilledDefFor(size) == null)
				{
					continue;
				}
				if (container != null && !RM_ContainerMaterials.CanHold(container, l))
				{
					if (refusal == null)
					{
						refusal = RM_ContainerMaterials.RefusalReason(container, l);
					}
					continue;
				}
				int units = container != null ? RM_ContainerMaterials.UnitsIn(container, l, size) : l.UnitsFor(size);
				if (CanPour(faucet, l, units))
				{
					refusal = null;
					return l;
				}
			}
			return null;
		}

		public override string GetInspectString()
		{
			var sb = new StringBuilder(base.GetInspectString());
			if (sb.Length > 0)
			{
				sb.AppendLine();
			}
			if (!Works)
			{
				sb.Append("Faucets are switched off in Mod Settings.");
				return sb.ToString();
			}
			List<LiquidDef> liquids = NetLiquids(this);
			if (liquids.Count == 0)
			{
				sb.Append(RM_LiquidNet.HasPipe(Position, Map) ? "Dry: no tank on this pipe network holds anything it will give."
					: "Not on a pipe: build it on a universal pipe.");
				return sb.ToString();
			}
			sb.Append("Pours: ");
			for (int i = 0; i < liquids.Count; i++)
			{
				if (i > 0)
				{
					sb.Append(", ");
				}
				LiquidDef l = liquids[i];
				sb.Append(l.label).Append(" (").Append(RM_Volume.Litres(RM_LiquidNet.Available(this, l)).ToString("0")).Append(" L)");
			}
			return sb.ToString();
		}
	}

	/// <summary>Drink 1.5 L at a pipe faucet (JobDriver_RM_DrinkFromTank's twin; the liquid is re-picked when the drink is
	/// done, so a net that changed while the pawn walked over still pours the best it now has).</summary>
	public class JobDriver_RM_DrinkFromFaucet : JobDriver
	{
		private Thing Faucet => job.targetA.Thing;

		public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
			this.FailOn(() => !Building_RM_PipeFaucet.Works);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
			Toil drink = Toils_General.Wait(RM_ThirstMath.TankDrinkTicks).WithProgressBarToilDelay(TargetIndex.A);
			drink.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			yield return drink;
			Toil finish = ToilMaker.MakeToil("RM_DrinkFromFaucet");
			finish.initAction = delegate
			{
				Thing f = Faucet;
				float level = RM_ThirstUtility.LevelAny(pawn);
				LiquidDef liquid = Building_RM_PipeFaucet.DrinkFor(pawn, f, level, null, out RM_DrinkUse _, out RM_WaterQuality _);
				if (liquid == null || !Building_RM_PipeFaucet.TryPour(f, liquid, RM_Volume.Units(RM_ThirstMath.TankDrinkLitres)))
				{
					return;
				}
				RM_ThirstUtility.Drink(pawn, liquid, RM_ThirstMath.TankDrinkLitres, null, RM_DrinkSource.Tank);
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}

	/// <summary>Any empty container near a working faucet is an invitation to carry it there and fill it
	/// (WorkGiver_FillBottleFromTank's twin, gated by the same tankLoopEnabled switch as the tank loop).</summary>
	public class WorkGiver_RM_FillAtFaucet : WorkGiver_Scanner
	{
		private const float MaxDist = 60f;

		public override PathEndMode PathEndMode => PathEndMode.ClosestTouch;

		public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForGroup(ThingRequestGroup.HaulableEver);

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			return !RimMandrakeFlowWorksSettings.tankLoopEnabled || !Building_RM_PipeFaucet.Works || pawn.Map == null
				|| !pawn.Map.listerBuildings.ColonistsHaveBuilding(t => t is Building_RM_PipeFaucet);
		}

		public static Building_RM_PipeFaucet FindFaucet(Pawn pawn, Thing container, RM_ContainerSize size, bool ordered,
			out LiquidDef liquid, out string refusal)
		{
			liquid = null;
			refusal = null;
			Building_RM_PipeFaucet best = null;
			float bestD = MaxDist * MaxDist;
			foreach (Building_RM_PipeFaucet f in pawn.Map.listerBuildings.AllBuildingsColonistOfClass<Building_RM_PipeFaucet>())
			{
				float d = (f.Position - container.Position).LengthHorizontalSquared;
				if (f.Faction != pawn.Faction || d > bestD || f.IsForbidden(pawn))
				{
					continue;
				}
				LiquidDef l = Building_RM_PipeFaucet.FillFor(f, container, size, ordered, out string why);
				if (l == null)
				{
					refusal = refusal ?? why;
					continue;
				}
				if (!pawn.CanReach(f, PathEndMode.Touch, Danger.Some))
				{
					continue;
				}
				best = f;
				bestD = d;
				liquid = l;
			}
			if (best != null)
			{
				refusal = null;
			}
			return best;
		}

		public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			RM_BottledLiquidExtension ext = t.def.GetModExtension<RM_BottledLiquidExtension>();
			if (ext == null || !ext.IsEmpty || t.IsForbidden(pawn) || !pawn.CanReserve(t, 1, 1, null, forced))
			{
				return false;
			}
			if (FindFaucet(pawn, t, ext.size, forced, out LiquidDef _, out string refusal) != null)
			{
				return true;
			}
			if (refusal != null)
			{
				JobFailReason.Is(refusal);
			}
			return false;
		}

		public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			RM_BottledLiquidExtension ext = t.def.GetModExtension<RM_BottledLiquidExtension>();
			if (ext == null || !ext.IsEmpty)
			{
				return null;
			}
			Building_RM_PipeFaucet f = FindFaucet(pawn, t, ext.size, forced, out LiquidDef _, out string _);
			if (f == null)
			{
				return null;
			}
			Job job = JobMaker.MakeJob(RM_ThirstDefOf.RM_FillAtFaucet, t, f);
			job.count = 1;
			job.playerForced = forced;
			return job;
		}
	}

	/// <summary>Carry one empty container to a faucet and fill it from the faucet's net (JobDriver_FillBottleFromTank's twin).</summary>
	public class JobDriver_RM_FillAtFaucet : JobDriver
	{
		private const int FillTicks = 180;

		private Thing Container => job.targetA.Thing;

		private Thing Faucet => job.targetB.Thing;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(Container, job, 1, 1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			// carried, the container is despawned: destroyed/null/forbidden is the carry-safe condition (tank driver's lesson)
			this.FailOnDestroyedNullOrForbidden(TargetIndex.A);
			this.FailOnDespawnedNullOrForbidden(TargetIndex.B);
			this.FailOn(() => !Building_RM_PipeFaucet.Works);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
			yield return Toils_Haul.StartCarryThing(TargetIndex.A);
			yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.Touch);
			Toil fill = Toils_General.Wait(FillTicks).WithProgressBarToilDelay(TargetIndex.B);
			fill.FailOnCannotTouch(TargetIndex.B, PathEndMode.Touch);
			yield return fill;
			Toil finish = ToilMaker.MakeToil("RM_FillAtFaucet");
			finish.initAction = delegate
			{
				Thing carried = pawn.carryTracker.CarriedThing;
				Thing f = Faucet;
				RM_BottledLiquidExtension ext = carried?.def.GetModExtension<RM_BottledLiquidExtension>();
				if (f == null || ext == null || !ext.IsEmpty)
				{
					return;
				}
				LiquidDef liquid = Building_RM_PipeFaucet.FillFor(f, carried, ext.size, job.playerForced, out string refusal);
				if (liquid == null)
				{
					if (refusal != null)
					{
						Messages.Message(refusal, pawn, MessageTypeDefOf.RejectInput, false);
					}
					return;
				}
				ThingDef filledDef = liquid.bottled?.FilledDefFor(ext.size);
				int units = RM_ContainerMaterials.UnitsIn(carried, liquid, ext.size);
				if (filledDef == null || !Building_RM_PipeFaucet.TryPour(f, liquid, units))
				{
					return;
				}
				Thing filled = RM_LiquidBottleUtility.MakeContainer(filledDef, carried);
				carried.Destroy();
				filled.stackCount = 1;
				RM_LiquidBottleUtility.PlacePaidFor(filled, pawn.Position, Map);   // the net was debited
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}
}
