using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public abstract class Graphic_FleckCollection : Graphic_Fleck
{
	protected Graphic_Fleck[] subGraphics;

	public override void Init(GraphicRequest req)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		((Graphic)this).data = req.graphicData;
		if (GenText.NullOrEmpty(req.path))
		{
			throw new ArgumentNullException("folderPath");
		}
		if ((Object)(object)req.shader == (Object)null)
		{
			throw new ArgumentNullException("shader");
		}
		((Graphic)this).path = req.path;
		((Graphic)this).maskPath = req.maskPath;
		((Graphic)this).color = req.color;
		((Graphic)this).colorTwo = req.colorTwo;
		((Graphic)this).drawSize = req.drawSize;
		List<Texture2D> list = (from x in ContentFinder<Texture2D>.GetAllInFolder(req.path)
			where !((Object)x).name.EndsWith(Graphic_Single.MaskSuffix)
			orderby ((Object)x).name
			select x).ToList();
		if (GenList.NullOrEmpty<Texture2D>((IList<Texture2D>)list))
		{
			Log.Error("Collection cannot init: No textures found at path " + req.path);
			subGraphics = (Graphic_Fleck[])(object)new Graphic_Fleck[0];
		}
		else
		{
			subGraphics = ((IEnumerable<Texture2D>)list).Select((Func<Texture2D, Graphic_Fleck>)((Texture2D texture2D) => (Graphic_Fleck)GraphicDatabase.Get(typeof(Graphic_Fleck), req.path + "/" + ((Object)texture2D).name, req.shader, ((Graphic)this).drawSize, ((Graphic)this).color, ((Graphic)this).colorTwo, ((Graphic)this).data, req.shaderParameters, (string)null))).ToArray();
		}
	}
}
