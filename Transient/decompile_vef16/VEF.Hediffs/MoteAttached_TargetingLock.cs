using UnityEngine;
using Verse;

namespace VEF.Hediffs;

[HotSwappable]
public class MoteAttached_TargetingLock : MoteAttached
{
	public void DrawTargetingLock(float progress)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		Vector3 exactPosition = ((Mote)this).exactPosition;
		float exactRotation = ((Mote)this).exactRotation;
		for (int i = 0; i < 4; i++)
		{
			((Mote)this).exactRotation = i * 90;
			Vector3 val = Quaternion.AngleAxis(((Mote)this).exactRotation, Vector3.up) * (Vector3.forward * Mathf.Max(0.3f, progress + 0.3f));
			Vector3 val2 = (((Mote)this).exactPosition = exactPosition + val);
			((Mote)this).exactPosition.y = Altitudes.AltitudeFor((AltitudeLayer)28);
			((Thing)this).Graphic.Draw(val2, ((Thing)this).Rotation, (Thing)(object)this, 0f);
		}
		((Mote)this).exactRotation = exactRotation;
		((Mote)this).exactPosition = exactPosition;
	}

	protected override void Tick()
	{
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		((Mote)this).Tick();
		if (((MoteAttachLink)(ref ((Mote)this).link1)).Linked)
		{
			TargetInfo target = ((MoteAttachLink)(ref ((Mote)this).link1)).Target;
			if (!((TargetInfo)(ref target)).ThingDestroyed)
			{
				return;
			}
		}
		((Thing)this).Destroy((DestroyMode)0);
	}
}
