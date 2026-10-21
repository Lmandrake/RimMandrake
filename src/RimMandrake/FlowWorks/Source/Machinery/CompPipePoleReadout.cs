using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 7 (design §P9): the pipe pole's own inspect line, under GSS's
	/// "Pipe spans: n/3": whether the spans it holds up carry the liquid net (a pipe at the pole, RM_PipePoles.JoinCells) or
	/// carry nothing. Text: RM_LineReadoutMath.PoleLine.</summary>
	public class CompProperties_PipePoleReadout : CompProperties
	{
		public CompProperties_PipePoleReadout()
		{
			compClass = typeof(CompPipePoleReadout);
		}
	}

	public class CompPipePoleReadout : ThingComp
	{
		/// <summary>The strung pipe spans with this pole at one end (RM_PipePoles.UpSpans lists each once, either way round).</summary>
		public int StrungSpans()
		{
			if (!parent.Spawned)
			{
				return 0;
			}
			int n = 0;
			foreach (var sp in RM_PipePoles.UpSpans(parent.Map))
			{
				if (sp.Key == parent || sp.Value == parent)
				{
					n++;
				}
			}
			return n;
		}

		public override string CompInspectStringExtra()
		{
			if (!parent.Spawned || !RM_MachinerySettings.pipePolesEnabled)
			{
				return null;
			}
			return RM_LineReadoutMath.PoleLine(StrungSpans(), RM_PipePoles.JoinCells(parent).Count > 0);
		}
	}
}
