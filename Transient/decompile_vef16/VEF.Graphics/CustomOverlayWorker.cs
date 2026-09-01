using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class CustomOverlayWorker(CustomOverlayDef def)
{
	private static readonly List<Material> EmptyList = new List<Material>();

	public readonly CustomOverlayDef def = def;

	public virtual Material MaterialForThing(Thing thing)
	{
		return def.CachedMaterial;
	}

	public virtual List<Material> ExtraMaterialsForThing(Thing thing)
	{
		return EmptyList;
	}

	public virtual Vector3 CustomOffsetForThing(Thing thing)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		return def.customOffset;
	}
}
