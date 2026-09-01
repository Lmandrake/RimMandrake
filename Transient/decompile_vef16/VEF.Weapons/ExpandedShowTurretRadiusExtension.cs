using System;
using Verse;

namespace VEF.Weapons;

public class ExpandedShowTurretRadiusExtension : DefModExtension
{
	public Type allowedVerbClass;

	public bool allowAnyVerb;

	public bool drawMaxRange = true;

	public bool drawMinRange = true;
}
