using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class GraphicsOverride : DefModExtension
{
	public FlagStringList replaceFlags = new FlagStringList();

	public List<GraphicsOverride> overrideList = new List<GraphicsOverride>();

	public float priority;

	public List<ConditionalGraphic> graphics = new List<ConditionalGraphic>();

	public Vector2 drawSize = Vector2.one;

	public List<GraphicsOverride> Overrides
	{
		get
		{
			if (GenCollection.Any<GraphicsOverride>(overrideList))
			{
				return (from x in overrideList.SelectMany((GraphicsOverride x) => x.Overrides)
					orderby x.priority descending
					select x).ToList();
			}
			return new List<GraphicsOverride>(1) { this };
		}
	}
}
