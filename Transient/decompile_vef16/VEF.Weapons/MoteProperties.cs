using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class MoteProperties : DefModExtension
{
	private const float MoteSizer = 32f;

	public FloatRange? angleRange;

	public FleckDef fleckDef;

	public ThingDef moteDef;

	public int numTimesThrown = 1;

	public FloatRange? rotationRange;

	public float size = -1f;

	public float velocity = -1f;

	public float Velocity
	{
		get
		{
			if (!(velocity > 0f))
			{
				return Rand.Range(0.5f, 0.7f);
			}
			return velocity;
		}
	}

	public float Angle
	{
		get
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			FloatRange? val = angleRange;
			if (val.HasValue)
			{
				FloatRange value = angleRange.Value;
				return ((FloatRange)(ref value)).RandomInRange;
			}
			return Rand.Range(30, 40);
		}
	}

	public float Rotation
	{
		get
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			FloatRange? val = rotationRange;
			if (val.HasValue)
			{
				FloatRange value = rotationRange.Value;
				return ((FloatRange)(ref value)).RandomInRange;
			}
			return Rand.Range(-30f, 30f);
		}
	}

	public float Size(int damage)
	{
		if (!(size > 0f))
		{
			return Mathf.Clamp01((float)damage / 32f);
		}
		return size;
	}

	public override IEnumerable<string> ConfigErrors()
	{
		foreach (string item in _003C_003En__0())
		{
			yield return item;
		}
		if (moteDef == null && fleckDef == null)
		{
			yield return "Either <color=teal>moteDef</color> or <color=teal>fleckDef</color> must be provided.";
		}
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<string> _003C_003En__0()
	{
		return ((DefModExtension)this).ConfigErrors();
	}
}
