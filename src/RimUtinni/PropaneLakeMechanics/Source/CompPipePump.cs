using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	public class CompProperties_PipePump : CompProperties
	{
		public CompProperties_PipePump()
		{
			compClass = typeof(CompPipePump);
		}
	}

	/// <summary>
	/// "The pump is very far away" (owner's framing quote, §4) — this is that
	/// pump: a network member whose Running state is what makes the network
	/// pressurized (feeds rupture jets) and what agitates RUT_VWake nearby.
	/// Defaults to running so a freshly-placed pump reads as "the pipe is live"
	/// without an extra click.
	/// </summary>
	public class CompPipePump : ThingComp
	{
		private bool running = true;

		public bool Running => running && parent.Spawned;

		public override IEnumerable<Gizmo> CompGetGizmosExtra()
		{
			foreach (Gizmo g in base.CompGetGizmosExtra())
			{
				yield return g;
			}
			yield return new Command_Toggle
			{
				defaultLabel = "RUT_PipePump_Toggle".Translate(),
				defaultDesc = "RUT_PipePump_ToggleDesc".Translate(),
				icon = TexCommand.DesirePower,
				isActive = () => running,
				toggleAction = delegate
				{
					running = !running;
				}
			};
		}

		public override string CompInspectStringExtra()
		{
			return running ? "RUT_PipePump_Running".Translate() : "RUT_PipePump_Stopped".Translate();
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref running, "running", true);
		}
	}
}
