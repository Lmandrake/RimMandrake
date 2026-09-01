using RimWorld;
using Verse;

namespace VEF.Buildings;

public class CompThrowMote : ThingComp
{
	public int ticksSinceLastEmitted;

	public ThingDef customizedMoteDef;

	private CompProperties_ThrowMote Props => (CompProperties_ThrowMote)(object)base.props;

	public override void PostPostMake()
	{
		((ThingComp)this).PostPostMake();
		if (Props.fadeOutTime != -1 || Props.solidTime != -1)
		{
			customizedMoteDef = Props.mote;
			if (Props.fadeOutTime != -1)
			{
				customizedMoteDef.mote.fadeOutTime = Props.fadeOutTime;
			}
			if (Props.solidTime != -1)
			{
				customizedMoteDef.mote.solidTime = Props.solidTime;
			}
		}
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
	}

	public override void CompTick()
	{
		CompRefuelable comp = base.parent.GetComp<CompRefuelable>();
		CompFlickable comp2 = base.parent.GetComp<CompFlickable>();
		if ((comp == null || comp.HasFuel) && (comp2 == null || comp2.SwitchIsOn))
		{
			if (ticksSinceLastEmitted >= Props.emissionInterval)
			{
				Throw();
				ticksSinceLastEmitted = 0;
			}
			else
			{
				ticksSinceLastEmitted++;
			}
		}
	}

	protected void Throw()
	{
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Expected O, but got Unknown
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Expected O, but got Unknown
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		MoteThrown val = ((customizedMoteDef == null) ? ((MoteThrown)ThingMaker.MakeThing(Props.mote, (ThingDef)null)) : ((MoteThrown)ThingMaker.MakeThing(customizedMoteDef, (ThingDef)null)));
		((Mote)val).Scale = 1.9f * (float)Props.moteScale;
		((Mote)val).rotationRate = Rand.Range(Props.rotationRange.min, Props.rotationRange.max);
		((Mote)val).exactPosition = GenThing.TrueCenter((Thing)(object)base.parent);
		val.SetVelocity(Rand.Range(Props.angleRange.min, Props.angleRange.max), Rand.Range(Props.speedRange.min, Props.speedRange.max));
		GenSpawn.Spawn((Thing)(object)val, IntVec3Utility.ToIntVec3(GenThing.TrueCenter((Thing)(object)base.parent)), ((Thing)base.parent).Map, (WipeMode)0);
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<int>(ref ticksSinceLastEmitted, "ticksSinceLastEmitted", 0, false);
		Scribe_Defs.Look<ThingDef>(ref customizedMoteDef, "customizedMoteDef");
	}
}
