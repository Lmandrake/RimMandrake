using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.LiquidTypes
{
	/// <summary>
	/// LIQUID_BOTTLE_LOOP_1 — "revert timer (bottled boiling/icy → fresh)", row data, no per-liquid C#.
	///
	/// A LiquidDef row whose <c>bottled.revertsTo</c> is set (boiling water, icy water) gets this comp on
	/// every container size it ships, injected at startup from the row (RM_LiquidRevertInjector) — so the
	/// registry row is the only place the behaviour is authored. After <c>revertTicks</c> the stack is
	/// replaced, same size and count, by the target liquid's container of that size: a boiling bottle
	/// cools to fresh water, an icy one thaws to it. Age averages across merged stacks like rot does.
	/// Mod Setting: bottleRevertEnabled (off: bottled liquid keeps whatever state it was filled in).
	/// </summary>
	public class CompProperties_LiquidRevert : CompProperties
	{
		public ThingDef revertTo;
		public int revertTicks = 2500;

		public CompProperties_LiquidRevert()
		{
			compClass = typeof(RM_CompLiquidRevert);
		}
	}

	public class RM_CompLiquidRevert : ThingComp
	{
		private int age;

		public CompProperties_LiquidRevert Props => (CompProperties_LiquidRevert)props;

		public int Age => age;

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref age, "RM_revertAge", 0);
		}

		public override void CompTickRare()
		{
			base.CompTickRare();
			Advance(GenTicks.TickRareInterval);
		}

		public override void CompTickLong()
		{
			base.CompTickLong();
			Advance(GenTicks.TickLongInterval);
		}

		public void Advance(int ticks)
		{
			if (!RimMandrakeFlowWorksSettings.bottleRevertEnabled || Props.revertTo == null || parent.Destroyed)
			{
				return;
			}
			age += ticks;
			if (age >= Props.revertTicks)
			{
				Revert();
			}
		}

		public override void PreAbsorbStack(Thing otherStack, int count)
		{
			base.PreAbsorbStack(otherStack, count);
			RM_CompLiquidRevert other = otherStack.TryGetComp<RM_CompLiquidRevert>();
			int total = parent.stackCount + count;
			if (other != null && total > 0)
			{
				age = (int)(((long)age * parent.stackCount + (long)other.age * count) / total);
			}
		}

		public override void PostSplitOff(Thing piece)
		{
			base.PostSplitOff(piece);
			RM_CompLiquidRevert other = piece.TryGetComp<RM_CompLiquidRevert>();
			if (other != null)
			{
				other.age = age;
			}
		}

		public override string CompInspectStringExtra()
		{
			if (!RimMandrakeFlowWorksSettings.bottleRevertEnabled || Props.revertTo == null)
			{
				return null;
			}
			int left = Props.revertTicks - age;
			return "RMFlow_RevertsIn".Translate(Props.revertTo.label, (left < 0 ? 0 : left).ToStringTicksToPeriod());
		}

		private void Revert()
		{
			ThingDef to = Props.revertTo;
			int count = parent.stackCount;
			bool forbidden = parent.IsForbidden(Faction.OfPlayer);
			Thing made = RM_LiquidBottleUtility.MakeContainer(to, parent);
			made.stackCount = count;
			if (parent.Spawned)
			{
				Map map = parent.Map;
				IntVec3 pos = parent.Position;
				parent.Destroy();
				GenPlace.TryPlaceThing(made, pos, map, ThingPlaceMode.Near);
				if (forbidden)
				{
					made.SetForbidden(true, false);
				}
				return;
			}
			ThingOwner owner = parent.holdingOwner;
			if (owner == null)
			{
				return;
			}
			owner.Remove(parent);
			parent.Destroy();
			if (!owner.TryAdd(made))
			{
				made.Destroy();
			}
		}
	}

	/// <summary>Adds CompProperties_LiquidRevert to every filled container of a row with
	/// <c>bottled.revertsTo</c> set, pointing at the target row's container of the SAME size.
	/// A row naming a target that ships no container of that size is reported once and skipped.</summary>
	[StaticConstructorOnStartup]
	public static class RM_LiquidRevertInjector
	{
		public static readonly List<string> Injected = new List<string>();

		static RM_LiquidRevertInjector()
		{
			foreach (LiquidDef liquid in DefDatabase<LiquidDef>.AllDefsListForReading)
			{
				LiquidBottledForm form = liquid.bottled;
				if (form?.revertsTo?.bottled == null || form.revertTicks < 1)
				{
					continue;
				}
				foreach (RM_ContainerSize size in new[] { RM_ContainerSize.Bottle, RM_ContainerSize.Bucket, RM_ContainerSize.Barrel })
				{
					ThingDef from = form.FilledDefFor(size);
					ThingDef to = form.revertsTo.bottled.FilledDefFor(size);
					if (from == null)
					{
						continue;
					}
					if (to == null)
					{
						Log.Warning("[RimMandrake.FlowWorks] " + liquid.defName + " reverts to " + form.revertsTo.defName
							+ " but that liquid has no " + size + "; the " + size + " keeps its contents.");
						continue;
					}
					if (from.comps == null)
					{
						from.comps = new List<CompProperties>();
					}
					if (from.comps.Exists(c => c is CompProperties_LiquidRevert))
					{
						continue;
					}
					from.comps.Add(new CompProperties_LiquidRevert { revertTo = to, revertTicks = form.revertTicks });
					if (from.tickerType == TickerType.Never)
					{
						from.tickerType = TickerType.Rare;
					}
					Injected.Add(from.defName + "->" + to.defName);
				}
			}
		}
	}
}
