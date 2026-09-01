using UnityEngine;

namespace VEF.Hediffs;

public class MoteAttached_TargetingLockFixed : MoteAttached_TargetingLock
{
	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
		DrawTargetingLock(0.2f);
	}
}
