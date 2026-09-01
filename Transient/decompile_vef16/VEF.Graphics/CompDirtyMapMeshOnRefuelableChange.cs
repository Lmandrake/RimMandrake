using Verse;

namespace VEF.Graphics;

public class CompDirtyMapMeshOnRefuelableChange : ThingComp
{
	public override void ReceiveCompSignal(string signal)
	{
		((ThingComp)this).ReceiveCompSignal(signal);
		bool flag = ((signal == "RanOutOfFuel" || signal == "Refueled") ? true : false);
		if (flag && ((Thing)base.parent).Spawned)
		{
			((Thing)base.parent).DirtyMapMesh(((Thing)base.parent).Map);
		}
	}
}
