using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	public class CompProperties_PipeNetwork : CompProperties
	{
		public CompProperties_PipeNetwork()
		{
			compClass = typeof(CompPipeNetwork);
		}
	}

	/// <summary>
	/// Row 3's network membership marker: RUT_PipeSegment, RUT_PipeValve and
	/// RUT_PipePump all carry this comp so MapComponent_PipeNetworks can group
	/// them into connected networks by simple 4-way adjacency. Deliberately NOT
	/// a copy of vanilla PowerNet's incremental delayed-action registration —
	/// these networks are small, rare, and rebuilt lazily on demand, which is
	/// far less code for the same correctness at this scale.
	/// </summary>
	public class CompPipeNetwork : ThingComp
	{
		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			base.PostSpawnSetup(respawningAfterLoad);
			parent.Map?.GetComponent<MapComponent_PipeNetworks>()?.Notify_MemberChanged();
		}

		public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
		{
			base.PostDeSpawn(map, mode);
			map?.GetComponent<MapComponent_PipeNetworks>()?.Notify_MemberChanged();
		}
	}
}
