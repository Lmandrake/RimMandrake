using Verse;

namespace VEF.AnimalBehaviours;

[StaticConstructorOnStartup]
public class CompAttachEffecter : ThingComp
{
	private Effecter effecter;

	public CompProperties_AttachEffecter Props => (CompProperties_AttachEffecter)(object)base.props;

	public override void CompTick()
	{
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)base.parent).Map != null)
		{
			if (effecter == null)
			{
				effecter = Props.effecterDef.SpawnAttached((Thing)(object)base.parent, ((Thing)base.parent).Map, 1f);
			}
			Effecter obj = effecter;
			if (obj != null)
			{
				obj.EffectTick(TargetInfo.op_Implicit((Thing)(object)base.parent), TargetInfo.op_Implicit((Thing)(object)base.parent));
			}
		}
	}
}
