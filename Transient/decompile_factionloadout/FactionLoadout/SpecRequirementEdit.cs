using FactionLoadout.Util;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class SpecRequirementEdit : IExposable, IDeepCopyable<SpecRequirementEdit>
{
	public ThingDef Thing;

	public ThingDef Material;

	public ThingStyleDef Style;

	public QualityCategory? Quality;

	public bool Biocode;

	public Color Color;

	public ApparelSelectionMode SelectionMode;

	public float SelectionChance = 1f;

	public SpecRequirementEdit DeepClone()
	{
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		return new SpecRequirementEdit
		{
			Thing = Thing,
			Material = Material,
			Style = Style,
			Quality = Quality,
			Biocode = Biocode,
			Color = Color,
			SelectionMode = SelectionMode,
			SelectionChance = SelectionChance
		};
	}

	public void ExposeData()
	{
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		Scribe_Defs.Look<ThingDef>(ref Thing, "thing");
		Scribe_Defs.Look<ThingDef>(ref Material, "material");
		Scribe_Defs.Look<ThingStyleDef>(ref Style, "style");
		Scribe_Values.Look<QualityCategory?>(ref Quality, "quality", (QualityCategory?)null, false);
		Scribe_Values.Look<bool>(ref Biocode, "biocode", false, false);
		Scribe_Values.Look<Color>(ref Color, "color", default(Color), false);
		Scribe_Values.Look<ApparelSelectionMode>(ref SelectionMode, "selectionMode", ApparelSelectionMode.AlwaysTake, false);
		Scribe_Values.Look<float>(ref SelectionChance, "selectionChance", 0f, false);
	}
}
