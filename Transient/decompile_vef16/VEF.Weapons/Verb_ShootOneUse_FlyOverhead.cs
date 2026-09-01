using RimWorld;
using Verse;

namespace VEF.Weapons;

public class Verb_ShootOneUse_FlyOverhead : Verb_ShootOneUse
{
	public override void OrderForceTarget(LocalTargetInfo target)
	{
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		if (VerbUtility.ProjectileFliesOverhead((Verb)(object)this))
		{
			Thing caster = ((Verb)this).caster;
			if (caster != null)
			{
				Map map = caster.Map;
				if (map != null)
				{
					IntVec3 position = caster.Position;
					if (((IntVec3)(ref position)).IsValid)
					{
						RoofGrid roofGrid = map.roofGrid;
						if (roofGrid != null && roofGrid.Roofed(position))
						{
							object arg = Translator.Translate("CannotFire");
							TaggedString val = Translator.Translate("Roofed");
							Messages.Message($"{arg}: {((TaggedString)(ref val)).CapitalizeFirst()}", MessageTypeDefOf.RejectInput, false);
							return;
						}
					}
				}
			}
		}
		((Verb)this).OrderForceTarget(target);
	}
}
