namespace RimMandrake.FlowWorks.Machinery.Logistics
{
	/// <summary>Sluice gate decisions, Verse-free so the FlowWorks C# selftest runs the production code.</summary>
	public static class RM_SluiceGateMath
	{
		/// <summary>Does a gate in this state stop liquid crossing its cell? Only when the mechanic is on and
		/// the gate has finished shutting. A gate mid-travel keeps its previous state.</summary>
		public static bool BlocksFlow(bool enabled, bool flowOpen)
		{
			return enabled && !flowOpen;
		}

		/// <summary>May a level move between two cardinal neighbours? Not if either is a shut gate: the gate cell
		/// is sealed on all four sides, so liquid already in it stays put until it opens.</summary>
		public static bool PairBlocked(bool aIsShutGate, bool bIsShutGate)
		{
			return aIsShutGate || bIsShutGate;
		}

		/// <summary>Advance the gate's travel by <paramref name="elapsed"/> ticks. <paramref name="ticksLeft"/> is
		/// -1 while idle. Returns the new flowOpen. Reversing the crank mid-travel simply cancels the travel.</summary>
		public static bool StepTravel(bool wantOpen, bool flowOpen, ref int ticksLeft, int elapsed, int openDelay, int closeDelay)
		{
			if (wantOpen == flowOpen)
			{
				ticksLeft = -1;
				return flowOpen;
			}
			if (ticksLeft < 0)
			{
				ticksLeft = wantOpen ? (openDelay < 0 ? 0 : openDelay) : (closeDelay < 0 ? 0 : closeDelay);
			}
			ticksLeft -= elapsed;
			if (ticksLeft <= 0)
			{
				ticksLeft = -1;
				return wantOpen;
			}
			return flowOpen;
		}
	}
}
