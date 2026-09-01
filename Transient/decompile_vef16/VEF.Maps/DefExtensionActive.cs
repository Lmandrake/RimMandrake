using Verse;

namespace VEF.Maps;

public abstract class DefExtensionActive : DefModExtension
{
	public abstract void DoWork(TerrainDef def);

	public abstract void DoWork(ThingDef def);
}
