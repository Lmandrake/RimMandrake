using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery.Logistics
{
	/// <summary>
	/// Sluice gate hardware (FLOWWORKS_BUILD_PROGRAM_1 Phase 8; PIT_SUPERDEEP_COLLAPSE_1). NOT the RM_Sluice
	/// door (FLOWWORKS_DOOR_FAMILY_1), which is a pawn door that passes liquid while closed. This gate is the
	/// opposite: a pawn-irrelevant valve on a canal cell. Shut = no level crosses the cell in the depth engine
	/// (RM_MapComponent_Excavation component walk + donor pick) and the legacy flood walk refuses the cell;
	/// open = the channel flows as if it were not there.
	///
	/// Cranked by a colonist via vanilla CompFlickable (switch ON = gate OPEN; ships open). After the crank the
	/// gate travels for RM_SluiceGateSettings' open/close delay before the flow state changes.
	/// Pawns: walkable as a catwalk in both states (PROVISIONAL, def passability PassThroughOnly).
	/// </summary>
	public class Building_RM_SluiceGate : Building
	{
		private bool flowOpen = true;
		private int travelTicksLeft = -1;
		private CompFlickable flickCache;

		private CompFlickable Flick => flickCache ?? (flickCache = GetComp<CompFlickable>());

		/// <summary>True when liquid may cross this cell (the gate's ACTUAL state, not the crank's wish).</summary>
		public bool FlowOpen => flowOpen;

		public bool BlocksFlow => RM_SluiceGateMath.BlocksFlow(RM_SluiceGateSettings.sluiceGatesEnabled, flowOpen);

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref flowOpen, "sluiceGateFlowOpen", true);
			Scribe_Values.Look(ref travelTicksLeft, "sluiceGateTravelTicksLeft", -1);
		}

		protected override void Tick()
		{
			base.Tick();
			CompFlickable f = Flick;
			if (f == null)
			{
				return;
			}
			flowOpen = RM_SluiceGateMath.StepTravel(f.SwitchIsOn, flowOpen, ref travelTicksLeft, 1,
				RM_SluiceGateSettings.sluiceGateOpenDelayTicks, RM_SluiceGateSettings.sluiceGateCloseDelayTicks);
		}

		/// <summary>Debug/bridge setter: force the crank AND the gate to a state now, no pawn, no delay.</summary>
		public void ForceState(bool open)
		{
			CompFlickable f = Flick;
			if (f != null)
			{
				f.SwitchIsOn = open;
				// keep wantSwitchOn in step so no flick designation is left behind
				if (f.WantsFlick())
				{
					Traverse_SetWant(f, open);
				}
			}
			flowOpen = open;
			travelTicksLeft = -1;
		}

		private static void Traverse_SetWant(CompFlickable f, bool open)
		{
			HarmonyLib.Traverse.Create(f).Field("wantSwitchOn").SetValue(open);
			FlickUtility.UpdateFlickDesignation(f.parent);
		}

		public override string GetInspectString()
		{
			StringBuilder sb = new StringBuilder(base.GetInspectString());
			if (sb.Length > 0)
			{
				sb.AppendLine();
			}
			if (!RM_SluiceGateSettings.sluiceGatesEnabled)
			{
				sb.Append("Sluice gates are off in Mod Settings: liquid passes.");
			}
			else if (travelTicksLeft >= 0)
			{
				sb.Append(flowOpen ? "Shutting" : "Opening").Append(" (")
					.Append((travelTicksLeft / 60f).ToString("F1")).Append(" s)");
			}
			else
			{
				sb.Append(flowOpen ? "Open: liquid flows through." : "Shut: holding back liquid.");
			}
			return sb.ToString();
		}
	}

	/// <summary>The engine-facing hooks. Every call is one array lookup (the edifice grid).</summary>
	public static class RM_SluiceGates
	{
		public static bool IsShutGateAt(Map map, IntVec3 c)
		{
			if (!RM_SluiceGateSettings.sluiceGatesEnabled || map == null || !c.InBounds(map))
			{
				return false;
			}
			return c.GetEdifice(map) is Building_RM_SluiceGate g && g.BlocksFlow;
		}

		/// <summary>Depth engine hook: may a level move between cardinal neighbours a and b?</summary>
		public static bool BlocksBetween(Map map, IntVec3 a, IntVec3 b)
		{
			if (!RM_SluiceGateSettings.sluiceGatesEnabled)
			{
				return false;
			}
			return RM_SluiceGateMath.PairBlocked(IsShutGateAt(map, a), IsShutGateAt(map, b));
		}

		/// <summary>Legacy flood walk hook: an OPEN gate does not refuse the flood the way an edifice does.</summary>
		public static bool PassesLegacyFlood(Building edifice)
		{
			return edifice is Building_RM_SluiceGate g && !g.BlocksFlow;
		}

		private static Building_RM_SluiceGate GateAt(Map map, IntVec3 c)
		{
			return map == null || !c.InBounds(map) ? null : c.GetEdifice(map) as Building_RM_SluiceGate;
		}

		/// <summary>Bridge proof (jawa/static_call): gate state and the depth/fill on it and its four neighbours.
		/// "GATE open=False blocks=True travel=-1 | here d2 f0 | N d2 f2 | E d0 f0 | S d2 f0 | W d0 f0".</summary>
		public static string ProofState(Map map, IntVec3 cell)
		{
			Building_RM_SluiceGate g = GateAt(map, cell);
			if (g == null)
			{
				return "REFUSED: no sluice gate at " + cell;
			}
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			StringBuilder sb = new StringBuilder();
			sb.Append("GATE open=").Append(g.FlowOpen).Append(" blocks=").Append(g.BlocksFlow);
			sb.Append(" | here ").Append(Cell(eng, cell));
			string[] names = { "N", "E", "S", "W" };
			for (int i = 0; i < 4; i++)
			{
				IntVec3 n = cell + GenAdj.CardinalDirections[i];
				sb.Append(" | ").Append(names[i]).Append(' ').Append(n.InBounds(map) ? Cell(eng, n) : "oob");
			}
			return sb.ToString();
		}

		private static string Cell(RM_MapComponent_Excavation eng, IntVec3 c)
		{
			return eng == null ? "noengine" : "d" + eng.DepthAt(c) + " f" + eng.FillAt(c);
		}

		/// <summary>Bridge setter (jawa/static_call): force the gate at cell open or shut now.</summary>
		public static string ProofForce(Map map, IntVec3 cell, bool open)
		{
			Building_RM_SluiceGate g = GateAt(map, cell);
			if (g == null)
			{
				return "REFUSED: no sluice gate at " + cell;
			}
			g.ForceState(open);
			return ProofState(map, cell);
		}
	}
}
