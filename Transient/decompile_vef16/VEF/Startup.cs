using System.Collections.Generic;
using UnityEngine;
using VEF.AestheticScaling;
using VEF.Factions;
using VEF.Pawns;
using VEF.Research;
using Verse;

namespace VEF;

[StaticConstructorOnStartup]
public static class Startup
{
	public static Mesh plane20Flip;

	static Startup()
	{
		plane20Flip = MeshMakerPlanes.NewPlaneMesh(2f, true);
		CachedPawnDataExtensions.prepatched = ModLister.AnyModActiveNoSuffix(new List<string>(1) { "zetrith.prepatcher" });
		PawnShieldGenerator.Reset();
		ScenPartUtility.SetCache();
		ResearchProjectUtility.AutoAssignRules();
	}
}
