using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Apparels;

[StaticConstructorOnStartup]
public class CompSwitchApparel : ThingComp
{
	public CompProperties_SwitchApparel Props => (CompProperties_SwitchApparel)(object)base.props;

	public override IEnumerable<Gizmo> CompGetWornGizmosExtra()
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Expected O, but got Unknown
		if (!Object.op_Implicit((Object)(object)ContentFinder<Texture2D>.Get(Props.graphicPath, true)))
		{
			Log.Error("No Gizmo texture found");
		}
		return ((ThingComp)this).CompGetWornGizmosExtra().Append((Gizmo)new Command_Action
		{
			defaultLabel = "Switch",
			defaultDesc = "Switch to " + ((Def)Props.SwitchTo).label + " \n" + Props.Label,
			icon = (Texture)(object)ContentFinder<Texture2D>.Get(Props.graphicPath, true),
			action = delegate
			{
				//IL_0023: Unknown result type (might be due to invalid IL or missing references)
				//IL_0028: Unknown result type (might be due to invalid IL or missing references)
				//IL_0065: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
				//IL_00ab: Expected O, but got Unknown
				//IL_0095: Unknown result type (might be due to invalid IL or missing references)
				ThingWithComps parent = base.parent;
				Pawn wearer = ((Apparel)((parent is Apparel) ? parent : null)).Wearer;
				int hitPoints = ((Thing)base.parent).HitPoints;
				Color drawColor = ((Thing)base.parent).DrawColor;
				ThingDef val = null;
				if (((Thing)base.parent).Stuff != null)
				{
					val = ((Thing)base.parent).Stuff;
				}
				Thing val2 = ThingMaker.MakeThing(Props.SwitchTo, val);
				if (val2 != null)
				{
					val2.HitPoints = hitPoints;
					val2.DrawColor = drawColor;
					QualityCategory val3 = default(QualityCategory);
					if (QualityUtility.TryGetQuality((Thing)(object)base.parent, ref val3))
					{
						CompQuality val4 = ((ThingWithComps)(((val2 is ThingWithComps) ? val2 : null)?)).compQuality;
						if (val4 != null)
						{
							val4.SetQuality(val3, (ArtGenerationContext?)(ArtGenerationContext)1);
						}
					}
					Apparel val5 = (Apparel)val2;
					((Thing)base.parent).Destroy((DestroyMode)0);
					wearer.apparel.Wear(val5, true, false);
				}
			}
		});
	}
}
