using Verse;

namespace VEF.Graphics;

public class CompGlower_DirtyMapMesh : CompGlower
{
	protected override void SetGlowColorInternal(ColorInt? color)
	{
		((CompGlower)this).SetGlowColorInternal(color);
		if (((Thing)((ThingComp)this).parent).Spawned)
		{
			((Thing)((ThingComp)this).parent).DirtyMapMesh(((Thing)((ThingComp)this).parent).Map);
		}
	}
}
