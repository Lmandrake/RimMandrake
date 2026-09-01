using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[StaticConstructorOnStartup]
public class CompMoteReleaser : ThingComp
{
	private Mote mote;

	public CompProperties_MoteReleaser Props => (CompProperties_MoteReleaser)(object)base.props;

	public override void CompTick()
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)base.parent).Map != null)
		{
			if (mote == null)
			{
				mote = MoteMaker.MakeStaticMote(((Thing)base.parent).DrawPos, ((Thing)base.parent).Map, Props.moteDef, 1f, false, 0f);
				mote.instanceColor = ((Thing)base.parent).DrawColor;
			}
			if (((Thing)mote).def.mote.needsMaintenance)
			{
				mote.Maintain();
			}
		}
	}

	public override void Notify_ColorChanged()
	{
		mote = null;
	}
}
