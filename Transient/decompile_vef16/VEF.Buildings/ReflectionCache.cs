using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace VEF.Buildings;

public class ReflectionCache
{
	public static readonly FieldRef<Thing, Graphic> buildingGraphic = AccessTools.FieldRefAccess<Thing, Graphic>(AccessTools.Field(typeof(Thing), "graphicInt"));

	public static readonly FieldRef<Thing, Graphic> styleGraphic = AccessTools.FieldRefAccess<Thing, Graphic>(AccessTools.Field(typeof(Thing), "styleGraphicInt"));

	public static readonly FieldRef<ThingDef, List<RecipeDef>> ThingDef_allRecipesCached = AccessTools.FieldRefAccess<ThingDef, List<RecipeDef>>(AccessTools.Field(typeof(ThingDef), "allRecipesCached"));
}
