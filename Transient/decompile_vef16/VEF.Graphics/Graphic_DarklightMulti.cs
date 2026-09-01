using UnityEngine;
using VEF.Buildings;
using Verse;

namespace VEF.Graphics;

public class Graphic_DarklightMulti : Graphic_Multi
{
	public Graphic darklightGraphic;

	public override Material MatAt(Rot4 rot, Thing thing = null)
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		if (GlowerUtility.IsDarklight(thing))
		{
			return darklightGraphic.MatAt(rot, thing);
		}
		return ((Graphic)this).MatAt(rot, thing);
	}

	public override Material MatSingleFor(Thing thing)
	{
		if (GlowerUtility.IsDarklight(thing))
		{
			return darklightGraphic.MatSingleFor(thing);
		}
		return ((Graphic)this).MatSingleFor(thing);
	}

	public override void TryInsertIntoAtlas(TextureAtlasGroup groupKey)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		((Graphic_Multi)this).TryInsertIntoAtlas(groupKey);
		darklightGraphic.TryInsertIntoAtlas(groupKey);
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
		((Graphic_Multi)this).Init(req);
		req.path += "_dark";
		darklightGraphic = (Graphic)new Graphic_Multi();
		darklightGraphic.Init(req);
	}

	public override Graphic GetColoredVersion(Shader newShader, Color newColor, Color newColorTwo)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		return GraphicDatabase.Get<Graphic_DarklightMulti>(((Graphic)this).path, newShader, ((Graphic)this).drawSize, newColor, newColorTwo, ((Graphic)this).data, ((Graphic)this).maskPath);
	}

	public override string ToString()
	{
		return string.Format("{0}(base=({1}), darklight=({2}))", "Graphic_DarklightMulti", ((Graphic_Multi)this).ToString(), darklightGraphic);
	}
}
