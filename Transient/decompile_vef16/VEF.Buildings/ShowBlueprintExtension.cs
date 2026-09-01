using System;
using Verse;

namespace VEF.Buildings;

[Obsolete("Use GhostGraphicExtension instead")]
public class ShowBlueprintExtension : DefModExtension
{
	private static readonly ShowBlueprintExtension DefaultValues = new ShowBlueprintExtension();

	public bool showBlueprintInGhostMode = true;

	public static ShowBlueprintExtension Get(Def def)
	{
		return def.GetModExtension<ShowBlueprintExtension>() ?? DefaultValues;
	}

	public override void ResolveReferences(Def parentDef)
	{
		((DefModExtension)this).ResolveReferences(parentDef);
		object[] obj = new object[4] { parentDef, null, null, null };
		ModContentPack modContentPack = parentDef.modContentPack;
		obj[1] = ((modContentPack != null) ? modContentPack.Name : null);
		obj[2] = "ShowBlueprintExtension";
		obj[3] = "GhostGraphicExtension";
		Log.Warning(string.Format("{0} ({1}) is using {2}, which is now obsolete. Please replace it with {3}. This DefModExtension will still work for the time being, but may be removed in the future.", obj));
		GhostGraphicExtension ghostGraphicExtension = new GhostGraphicExtension
		{
			ghostMode = GhostGraphicExtension.CustomGhostMode.Blueprint
		};
		int index = parentDef.modExtensions.IndexOf((DefModExtension)(object)this);
		parentDef.modExtensions[index] = (DefModExtension)(object)ghostGraphicExtension;
		((DefModExtension)ghostGraphicExtension).ResolveReferences(parentDef);
	}
}
