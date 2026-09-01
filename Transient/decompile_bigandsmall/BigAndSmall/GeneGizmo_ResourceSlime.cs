using System.Collections.Generic;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class GeneGizmo_ResourceSlime : GeneGizmo_Resource
{
	private List<Pair<IGeneResourceDrain, float>> tmpDrainGenes = new List<Pair<IGeneResourceDrain, float>>();

	[CompilerGenerated]
	private bool _003CDraggingBar_003Ek__BackingField;

	protected override bool DraggingBar
	{
		get
		{
			return _003CDraggingBar_003Ek__BackingField;
		}
		set
		{
			_003CDraggingBar_003Ek__BackingField = value;
		}
	}

	protected override float Target
	{
		get
		{
			return base.gene.targetValue / base.gene.Max;
		}
		set
		{
			base.gene.SetTargetValuePct(value);
		}
	}

	public GeneGizmo_ResourceSlime(BS_GeneSlimePower spGene, List<IGeneResourceDrain> drainGenes, Color barColor, Color barhighlightColor)
		: base((Gene_Resource)(object)_003CspGene_003EP, drainGenes, barColor, barhighlightColor)
	{
	}//IL_001a: Unknown result type (might be due to invalid IL or missing references)
	//IL_001b: Unknown result type (might be due to invalid IL or missing references)


	protected override string GetTooltip()
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		tmpDrainGenes.Clear();
		string text = $"{ColoredText.Colorize(GenText.CapitalizeFirst(((Gene_Resource)spGene).ResourceLabel), ColoredText.TipSectionTitleColor)}: {base.gene.ValueForDisplay} / {base.gene.MaxForDisplay}\n";
		if (((Gene)spGene).pawn.IsColonistPlayerControlled || ((Gene)spGene).pawn.IsPrisonerOfColony)
		{
			text = text + TaggedString.op_Implicit(Translator.Translate("BS_AccumulateSlimeUntil") + ": ") + ((Gene_Resource)spGene).PostProcessValue(base.gene.targetValue);
		}
		if (!GenText.NullOrEmpty(((Gene)spGene).def.resourceDescription))
		{
			string text2 = text;
			TaggedString val = GrammarResolverSimpleStringExtensions.Formatted(((Gene)spGene).def.resourceDescription, NamedArgumentUtility.Named((object)((Gene)base.gene).pawn, "PAWN"));
			text = text2 + "\n\n" + ((TaggedString)(ref val)).Resolve();
		}
		return text;
	}

	public override GizmoResult GizmoOnGUI(Vector2 topLeft, float maxWidth, GizmoRenderParms parms)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		return ((Gizmo_Slider)this).GizmoOnGUI(topLeft, maxWidth, parms);
	}
}
