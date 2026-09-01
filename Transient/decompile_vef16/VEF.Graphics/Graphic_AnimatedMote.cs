using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class Graphic_AnimatedMote : Graphic_Animated
{
	public override void Init(GraphicRequest req)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		//IL_0149: Unknown result type (might be due to invalid IL or missing references)
		//IL_0289: Unknown result type (might be due to invalid IL or missing references)
		//IL_0290: Unknown result type (might be due to invalid IL or missing references)
		//IL_0296: Unknown result type (might be due to invalid IL or missing references)
		//IL_029c: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0219: Unknown result type (might be due to invalid IL or missing references)
		//IL_0230: Unknown result type (might be due to invalid IL or missing references)
		//IL_0237: Unknown result type (might be due to invalid IL or missing references)
		//IL_023d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0243: Unknown result type (might be due to invalid IL or missing references)
		//IL_024e: Unknown result type (might be due to invalid IL or missing references)
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
			((Graphic_Collection)this).subGraphics = (Graphic[])(object)new Graphic[1] { BaseContent.BadGraphic };
			return;
		}
		List<Graphic> list2 = new List<Graphic>();
		foreach (IGrouping<string, Texture2D> item in from s in list
			group s by ((Object)s).name.Split('_')[0])
		{
			List<Texture2D> list3 = item.ToList();
			string text = req.path + "/" + item.Key;
			bool flag = false;
			for (int num = list3.Count - 1; num >= 0; num--)
			{
				if (((Object)list3[num]).name.Contains("_east") || ((Object)list3[num]).name.Contains("_north") || ((Object)list3[num]).name.Contains("_west") || ((Object)list3[num]).name.Contains("_south"))
				{
					list3.RemoveAt(num);
					flag = true;
				}
			}
			if (list3.Count > 0)
			{
				foreach (Texture2D item2 in list3)
				{
					list2.Add(GraphicDatabase.Get(typeof(Graphic_Mote), req.path + "/" + ((Object)item2).name, req.shader, ((Graphic)this).drawSize, ((Graphic)this).color, ((Graphic)this).colorTwo, ((Graphic)this).data, req.shaderParameters, (string)null));
				}
			}
			if (flag)
			{
				list2.Add(GraphicDatabase.Get(typeof(Graphic_Multi), text, req.shader, ((Graphic)this).drawSize, ((Graphic)this).color, ((Graphic)this).colorTwo, ((Graphic)this).data, req.shaderParameters, (string)null));
			}
		}
		((Graphic_Collection)this).subGraphics = list2.ToArray();
	}
}
