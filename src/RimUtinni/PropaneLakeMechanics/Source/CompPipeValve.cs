using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	public class CompProperties_PipeValve : CompProperties
	{
		public CompProperties_PipeValve()
		{
			compClass = typeof(CompPipeValve);
		}
	}

	/// <summary>
	/// "There should be some valves that can be accessed to manually shut the
	/// pipe down on the map" (owner ruling, propane_gas_deep_design.md §9 row 3).
	/// A colonist-operable toggle; closing it depressurizes the WHOLE network it
	/// sits on (MapComponent_PipeNetworks.IsNetworkPressurized).
	/// </summary>
	public class CompPipeValve : ThingComp
	{
		private bool closed;

		public bool Closed => closed;

		public override IEnumerable<Gizmo> CompGetGizmosExtra()
		{
			foreach (Gizmo g in base.CompGetGizmosExtra())
			{
				yield return g;
			}
			yield return new Command_Toggle
			{
				defaultLabel = "RUT_PipeValve_Toggle".Translate(),
				defaultDesc = "RUT_PipeValve_ToggleDesc".Translate(),
				icon = TexCommand.ToggleVent,
				isActive = () => !closed,
				toggleAction = delegate
				{
					closed = !closed;
				}
			};
		}

		public override string CompInspectStringExtra()
		{
			return closed ? "RUT_PipeValve_Closed".Translate() : "RUT_PipeValve_Open".Translate();
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref closed, "closed");
		}
	}
}
