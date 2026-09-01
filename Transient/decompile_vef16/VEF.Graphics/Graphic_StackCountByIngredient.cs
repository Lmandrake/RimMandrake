using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class Graphic_StackCountByIngredient : Graphic_Collection
{
	public int cachedOffset = -1;

	public override Material MatSingle => base.subGraphics[base.subGraphics.Length - 1].MatSingle;

	public override Graphic GetColoredVersion(Shader newShader, Color newColor, Color newColorTwo)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		return GraphicDatabase.Get<Graphic_StackCount>(((Graphic)this).path, newShader, ((Graphic)this).drawSize, newColor, newColorTwo, ((Graphic)this).data, (string)null);
	}

	public override Material MatAt(Rot4 rot, Thing thing = null)
	{
		if (thing == null)
		{
			return ((Graphic)this).MatSingle;
		}
		return ((Graphic)this).MatSingleFor(thing);
	}

	public override Material MatSingleFor(Thing thing)
	{
		if (thing == null)
		{
			return ((Graphic)this).MatSingle;
		}
		return SubGraphicFor(thing).MatSingle;
	}

	public Graphic SubGraphicFor(Thing thing)
	{
		return SubGraphicForStackCount(thing.stackCount, thing.def, thing);
	}

	public override void DrawWorker(Vector3 loc, Rot4 rot, ThingDef thingDef, Thing thing, float extraRotation)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		((thing == null) ? base.subGraphics[0] : SubGraphicFor(thing)).DrawWorker(loc, rot, thingDef, thing, extraRotation);
	}

	public Graphic SubGraphicForStackCount(int stackCount, ThingDef def, Thing thing)
	{
		int graphicNumberOffset = cachedOffset;
		if (graphicNumberOffset == -1)
		{
			graphicNumberOffset = GetGraphicNumberOffset(thing);
		}
		if (stackCount == 1)
		{
			return base.subGraphics[graphicNumberOffset * 3];
		}
		if (stackCount == def.stackLimit)
		{
			return base.subGraphics[2 + graphicNumberOffset * 3];
		}
		return base.subGraphics[1 + graphicNumberOffset * 3];
	}

	public override string ToString()
	{
		return "StackCount(path=" + ((Graphic)this).path + ", count=" + base.subGraphics.Length + ")";
	}

	public static int GetGraphicNumberOffset(Thing thing)
	{
		CompIngredients val = ThingCompUtility.TryGetComp<CompIngredients>(thing);
		if (val != null && StaticCollectionsClass.graphicOffsets.ContainsKey(thing.def))
		{
			foreach (ThingDef ingredient in val.ingredients)
			{
				if (StaticCollectionsClass.graphicOffsets[thing.def].ContainsKey(ingredient))
				{
					return StaticCollectionsClass.graphicOffsets[thing.def][ingredient];
				}
			}
		}
		return 0;
	}
}
