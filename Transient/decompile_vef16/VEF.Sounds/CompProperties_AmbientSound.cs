using Verse;

namespace VEF.Sounds;

public class CompProperties_AmbientSound : CompProperties
{
	public SoundDef ambientSound;

	public CompProperties_AmbientSound()
	{
		base.compClass = typeof(CompAmbientSound);
	}
}
