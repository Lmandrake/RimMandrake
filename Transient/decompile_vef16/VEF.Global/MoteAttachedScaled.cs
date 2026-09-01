using UnityEngine;
using Verse;

namespace VEF.Global;

public class MoteAttachedScaled : MoteAttached
{
	public float maxScale;

	protected override void TimeInterval(float deltaTime)
	{
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		((MoteAttached)this).TimeInterval(deltaTime);
		if (!((Thing)this).Destroyed && ((Thing)this).def.mote.growthRate != 0f)
		{
			((Mote)this).linearScale = new Vector3(((Mote)this).linearScale.x + ((Thing)this).def.mote.growthRate * deltaTime, ((Mote)this).linearScale.y, ((Mote)this).linearScale.z + ((Thing)this).def.mote.growthRate * deltaTime);
			((Mote)this).linearScale.x = Mathf.Min(Mathf.Max(((Mote)this).linearScale.x, 0.0001f), maxScale);
			((Mote)this).linearScale.z = Mathf.Min(Mathf.Max(((Mote)this).linearScale.z, 0.0001f), maxScale);
		}
	}

	public override void ExposeData()
	{
		((Thing)this).ExposeData();
		Scribe_Values.Look<float>(ref maxScale, "maxScale", 0f, false);
	}
}
