using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class Graphic_RefuelableSingle : Graphic_Single
{
	public Graphic emptyGraphic;

	public override Material MatAt(Rot4 rot, Thing thing = null)
	{
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		CompRefuelable obj = ThingCompUtility.TryGetComp<CompRefuelable>(thing);
		if (obj != null && obj.Fuel <= 0f)
		{
			return emptyGraphic.MatAt(rot, thing);
		}
		return ((Graphic_Single)this).MatAt(rot, thing);
	}

	public override Material MatSingleFor(Thing thing)
	{
		CompRefuelable obj = ThingCompUtility.TryGetComp<CompRefuelable>(thing);
		if (obj != null && obj.Fuel <= 0f)
		{
			return emptyGraphic.MatSingleFor(thing);
		}
		return ((Graphic)this).MatSingleFor(thing);
	}

	public override void TryInsertIntoAtlas(TextureAtlasGroup groupKey)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		((Graphic_Single)this).TryInsertIntoAtlas(groupKey);
		emptyGraphic.TryInsertIntoAtlas(groupKey);
	}

	public override void Init(GraphicRequest req)
	{
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Expected O, but got Unknown
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		ref string maskPath = ref req.maskPath;
		if (maskPath == null)
		{
			maskPath = req.path + Graphic_Single.MaskSuffix;
		}
		((Graphic_Single)this).Init(req);
		req.path += "_empty";
		emptyGraphic = (Graphic)new Graphic_Multi();
		emptyGraphic.Init(req);
	}

	public override Graphic GetColoredVersion(Shader newShader, Color newColor, Color newColorTwo)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		return GraphicDatabase.Get<Graphic_RefuelableSingle>(((Graphic)this).path, newShader, ((Graphic)this).drawSize, newColor, newColorTwo, ((Graphic)this).data, (string)null);
	}

	public override string ToString()
	{
		return string.Format("{0}(base=({1}), empty=({2}))", "Graphic_RefuelableSingle", ((Graphic_Single)this).ToString(), emptyGraphic);
	}
}
