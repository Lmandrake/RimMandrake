using System.Collections.Generic;
using VEF.Apparels;
using Verse;

namespace VEF.Buildings;

public class ProjectileInterceptorExtension : DefModExtension
{
	public List<HealthColorPoint> healthColorPoints;

	public override void ResolveReferences(Def parentDef)
	{
		((DefModExtension)this).ResolveReferences(parentDef);
		if (!GenList.NullOrEmpty<HealthColorPoint>((IList<HealthColorPoint>)healthColorPoints))
		{
			VanillaExpandedFramework_CompProjectileInterceptor_PostDraw_Patch.patchActive = true;
		}
	}
}
