using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Planet;

public class HireableFactionDef : Def
{
	[Unsaved(false)]
	private Color? cachedColor;

	public Color color;

	public string commTag;

	[Unsaved(false)]
	public string editBuffer;

	public List<PawnKindDef> pawnKinds;

	public FactionDef referencedFaction;

	public string texPath;

	[Unsaved(false)]
	private Texture2D texture;

	public Color Color
	{
		get
		{
			//IL_0059: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_0056: Unknown result type (might be due to invalid IL or missing references)
			//IL_0042: Unknown result type (might be due to invalid IL or missing references)
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_0049: Unknown result type (might be due to invalid IL or missing references)
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			if (referencedFaction != null)
			{
				Color valueOrDefault = cachedColor.GetValueOrDefault();
				if (!cachedColor.HasValue)
				{
					Faction obj = Find.World.factionManager.FirstFactionOfDef(referencedFaction);
					valueOrDefault = ((obj != null) ? obj.Color : color);
					cachedColor = valueOrDefault;
					return valueOrDefault;
				}
				return valueOrDefault;
			}
			return color;
		}
	}

	public Texture2D Texture => texture ?? (texture = ContentFinder<Texture2D>.Get(texPath, true));
}
