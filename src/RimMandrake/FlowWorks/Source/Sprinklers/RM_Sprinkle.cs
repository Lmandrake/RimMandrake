using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.Machinery;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Sprinklers
{
	/// <summary>
	/// SPRINKLER_HEADS_BUILD_PUMP_REQUIRED (design §4): the ONE pulse both heads call. The native head and the adapted VFE head
	/// only choose the cells; this draws the litres from the pipe net (all-or-nothing, conserving: RM_LiquidTransfer.Move from
	/// the draw plan's tanks to a Sink), marks the cells sprinkled, and applies the ruled non-water effects (OQ-S5).
	/// Pressure (OQ-S2): a working Building_LiquidPump must be a machine on one of the head's net components.
	/// </summary>
	public static class RM_Sprinkle
	{
		public sealed class Result
		{
			public RM_SprinklerState state;
			public LiquidDef liquid;
			public int units, cells, need, available;
		}

		/// <summary>The liquid's key in the wet registry: its canal FluidDef's defName (what ExplosiveGrowth's accept sets hold,
		/// e.g. RM_Fluid_Water), else its own defName.</summary>
		public static string KeyOf(LiquidDef l) => l == null ? null : l.canalFluid?.defName ?? l.defName;

		public static bool ThickOrHeavy(LiquidDef l) =>
			l != null && (l.viscosityClass == LiquidViscosityClass.Thick || l.viscosityClass == LiquidViscosityClass.Heavy);

		/// <summary>OQ-S2: a working pump on any of the head's (non-refused) network components.</summary>
		public static bool HasPressure(Thing head)
		{
			if (head?.Map == null) return false;
			foreach (RM_NetComponent c in RM_LiquidNet.Components(head.Map).ComponentsOf(head))
			{
				if (c.Refused) continue;
				foreach (object m in c.Machines)
				{
					if (m is Building_LiquidPump p && p.Spawned && p.Working) return true;
				}
			}
			return false;
		}

		/// <summary>§2: the liquid the net holds most of (RM_SprinklerKernel.PickLiquid, ties by defName).</summary>
		public static LiquidDef MostHeld(Thing head, out int held)
		{
			held = 0;
			var parts = new List<KeyValuePair<string, int>>();
			var byName = new Dictionary<string, LiquidDef>();
			foreach (Building_LiquidTank t in RM_LiquidNet.TanksFor(head))
			{
				// owner Q12 part 2, 2026-10-17: "Sprinklers shouldn't offer spraying brine" (nor salt water): never picked
				if (t.Empty || !t.GivesToMachines || t.storedLiquid.neverSprayed) continue;
				parts.Add(new KeyValuePair<string, int>(t.storedLiquid.defName, t.storedUnits));
				byName[t.storedLiquid.defName] = t.storedLiquid;
			}
			string pick = RM_SprinklerKernel.PickLiquid(parts);
			if (pick == null) return null;
			LiquidDef l = byName[pick];
			held = Thirst.RM_DrinkReserve.Spendable(head, l);   // Q10: drinkers first
			return l;
		}

		/// <summary>§1.5 + OQ-S7: cells within <paramref name="radius"/> the spray reaches: in bounds, not a wall, in line of sight
		/// from the head.</summary>
		public static List<IntVec3> Covered(Thing head, float radius)
		{
			var list = new List<IntVec3>();
			Map map = head.Map;
			IntVec3 o = head.Position;
			foreach (IntVec3 c in GenRadial.RadialCellsAround(o, radius, true))
			{
				if (!c.InBounds(map) || c.Impassable(map)) continue;
				if (c != o && !GenSight.LineOfSight(o, c, map, true)) continue;
				list.Add(c);
			}
			return list;
		}

		/// <summary>H1: a basin or pot (a plant grower building) holds its own water; never charged.</summary>
		public static bool Sealed(IntVec3 c, Map map) => c.GetEdifice(map) is Building_PlantGrower;

		public static Result Pulse(ThingWithComps head, List<IntVec3> cells, bool enabled, bool switchOn)
		{
			var r = new Result { cells = cells?.Count ?? 0 };
			bool pressure = enabled && switchOn && HasPressure(head);
			LiquidDef liquid = pressure ? MostHeld(head, out r.available) : null;
			r.liquid = liquid;
			float lpc = RM_SprinklerSettings.sprinklerLitresPerCellHour;
			r.need = RM_SprinklerKernel.UnitsFor(r.cells, lpc, RM_Volume.UnitsPerLitre);
			r.state = RM_SprinklerKernel.Decide(enabled, switchOn, pressure, liquid != null, ThickOrHeavy(liquid), r.cells, r.need, r.available);
			if (r.state != RM_SprinklerState.Spraying) return r;

			List<(Building_LiquidTank tank, int units)> plan = RM_LiquidNet.DrawPlan(head, liquid, r.need);
			if (plan == null)
			{
				r.state = RM_SprinklerState.Dry;
				return r;
			}
			Map map = head.Map;
			bool effects = RM_SprinklerSettings.sprinklerNonWaterEffects;
			RM_TransferLeg source = RM_TransferLeg.Split(plan.Count, i => plan[i].units, (i, k) => plan[i].tank.CanProvide(k),
				(i, k) => plan[i].tank.TryRemoveLiquid(k), (i, k) => plan[i].tank.TryAddLiquid(liquid, k));
			RM_TransferLeg sink = RM_TransferLeg.Sink(k =>
			{
				if (effects && liquid.flammable) SpillFuel(map, cells, liquid, k);
			});
			if (RM_LiquidTransfer.Move(r.need, source, sink, out RM_MoveOutcome _) == r.need)
			{
				foreach ((Building_LiquidTank tank, int units) p in plan) RM_LiquidNet.Credit(head, p.tank, liquid, p.units, RM_SprinklerKernel.PulseTicks);   // credit site: sprinkler draw
			}
			else
			{
				r.state = RM_SprinklerState.Dry;
				return r;
			}
			r.units = r.need;
			int now = Find.TickManager.TicksGame;
			RM_MapComponent_Sprinklers.Of(map)?.Wet(cells, KeyOf(liquid), RM_SprinklerKernel.WetUntil(now), head.thingIDNumber);
			RM_MapComponent_Sprinklers.Pulses++;
			RM_MapComponent_Sprinklers.SprayedUnits += r.units;
			if (effects) HurtPawns(map, cells, liquid, head);
			return r;
		}

		/// <summary>OQ-S5: a flammable liquid lays its spill filth on the sprayed ground (RM_LiquidSpill's normal rate), spread
		/// over up to four covered cells. The units already left the net through the Sink; Spill only places filth.</summary>
		private static void SpillFuel(Map map, List<IntVec3> cells, LiquidDef liquid, int units)
		{
			if (cells.Count == 0 || units <= 0) return;
			int parts = Mathf.Min(4, cells.Count);
			int each = units / parts, rest = units - each * parts;
			for (int i = 0; i < parts; i++)
			{
				RM_LiquidSpill.Spill(map, cells.RandomElement(), liquid, each + (i == 0 ? rest : 0));
			}
		}

		/// <summary>OQ-S5: acid and scalding liquids apply their contact harm to each pawn in the spray, once per pulse.</summary>
		private static void HurtPawns(Map map, List<IntVec3> cells, LiquidDef liquid, Thing head)
		{
			DamageDef dd = liquid.damageOnContact?.damageDef;
			float amount = liquid.damageOnContact?.amount ?? 0f;
			if (dd == null && liquid.hot)
			{
				dd = DamageDefOf.Burn;
				amount = 2f;   // PROVISIONAL: a scald from a boiling spray with no contact spec of its own
			}
			if (dd == null || amount <= 0f) return;
			foreach (IntVec3 c in cells)
			{
				List<Thing> things = c.GetThingList(map);
				for (int i = things.Count - 1; i >= 0; i--)
				{
					if (things[i] is Pawn p && !p.Dead)
					{
						p.TakeDamage(new DamageInfo(dd, amount, 0f, -1f, head));
					}
				}
			}
		}
	}
}
