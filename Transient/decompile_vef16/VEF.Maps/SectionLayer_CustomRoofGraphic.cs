using System;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Maps;

[StaticConstructorOnStartup]
public class SectionLayer_CustomRoofGraphic : SectionLayer
{
	private static readonly bool anyRoofUsesCustomGraphic = DefDatabase<RoofDef>.AllDefs.Any((RoofDef def) => ((Def)def).GetModExtension<RoofExtension>()?.EverUsesCustomRoofGraphic ?? false);

	public override bool Visible => anyRoofUsesCustomGraphic;

	public SectionLayer_CustomRoofGraphic(Section section)
		: base(section)
	{
		((MapDrawLayer)this).relevantChangeTypes = MapMeshFlagDef.op_Implicit(MapMeshFlagDefOf.Roofs);
	}

	public override void Regenerate()
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		((MapDrawLayer)this).ClearSubMeshes((MeshParts)63);
		CellRect cellRect = base.section.CellRect;
		Enumerator enumerator = ((CellRect)(ref cellRect)).GetEnumerator();
		try
		{
			while (((Enumerator)(ref enumerator)).MoveNext())
			{
				IntVec3 current = ((Enumerator)(ref enumerator)).Current;
				RoofDef val = ((MapDrawLayer)this).Map.roofGrid.RoofAt(current);
				if (val != null)
				{
					((Def)val).GetModExtension<RoofExtension>()?.customRoofGraphic?.DrawDataAt(((MapDrawLayer)this).Map, current, val)?.Print((MapDrawLayer)(object)this, current);
				}
			}
		}
		finally
		{
			((IDisposable)(Enumerator)(ref enumerator)/*cast due to .constrained prefix*/).Dispose();
		}
		((MapDrawLayer)this).FinalizeMesh((MeshParts)63);
	}
}
