using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class ConditionalGraphicProperties : ConditionalGraphic
{
	public Vector2? drawSize;

	public ShaderTypeDef shader;

	public List<ConditionalGraphicProperties> alts = new List<ConditionalGraphicProperties>();

	public ConditionalGraphicProperties GetGraphicProperties(BSCache cache)
	{
		foreach (ConditionalGraphicProperties alt in alts)
		{
			if (alt.GetState(cache.pawn))
			{
				ConditionalGraphicProperties graphicProperties = alt.GetGraphicProperties(cache);
				if (graphicProperties != null)
				{
					return graphicProperties;
				}
			}
		}
		ConditionalGraphicProperties target = this;
		foreach (GraphicsOverride graphicOverride in GetGraphicOverrides(cache.pawn))
		{
			CollectionExtensions.Do<ConditionalGraphicProperties>(from x in graphicOverride.graphics.OfType<ConditionalGraphicProperties>()
				where x != null
				select x, (Action<ConditionalGraphicProperties>)delegate(ConditionalGraphicProperties x)
			{
				target = x;
			});
		}
		return target;
	}
}
