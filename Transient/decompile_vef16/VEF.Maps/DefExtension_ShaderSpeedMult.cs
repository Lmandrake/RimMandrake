using System;
using Verse;

namespace VEF.Maps;

public class DefExtension_ShaderSpeedMult : DefExtensionActive
{
	private float timeMult = 1f;

	public override void DoWork(TerrainDef def)
	{
		def.waterDepthMaterial.SetFloat("_GameSeconds", (float)Find.TickManager.TicksGame * timeMult);
	}

	public override void DoWork(ThingDef def)
	{
		throw new NotImplementedException();
	}
}
