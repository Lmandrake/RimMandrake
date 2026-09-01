using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class SubEffecterDef_SlideTowardsTarget : SubEffecterDef
{
	public int ticksToEnd = 120;

	public bool ticksToEndOverrideByWeaponWarmup = true;

	public Vector3 endPoint;

	public bool endPointZOverrideByWeapon;

	public FloatRange startPointFactor;

	public FloatRange endPointFactor;

	public FloatRange scaleXByStart;

	public FloatRange scaleYByStart;

	public FloatRange scaleXByEnd;

	public FloatRange scaleYByEnd;

	public FloatRange minimumProgress;

	public SubEffecterDef_SlideTowardsTarget()
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		Vector3 zero = Vector3.zero;
		zero.z = 5f;
		endPoint = zero;
		endPointZOverrideByWeapon = true;
		startPointFactor = new FloatRange(0f);
		endPointFactor = new FloatRange(1f);
		scaleXByStart = new FloatRange(0.8f, 1.2f);
		scaleYByStart = new FloatRange(0.8f, 1.2f);
		scaleXByEnd = new FloatRange(0.8f, 1.2f);
		scaleYByEnd = new FloatRange(0.8f, 1.2f);
		minimumProgress = new FloatRange(0f);
		((SubEffecterDef)this)._002Ector();
		base.subEffecterClass = typeof(SubEffecter_SlideTowardsTarget);
	}
}
