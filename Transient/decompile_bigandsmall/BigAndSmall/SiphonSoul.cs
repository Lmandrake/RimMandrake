using System.Runtime.CompilerServices;
using System.Text;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public record SiphonSoul
{
	public string SiphonSoulDescription
	{
		get
		{
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Unknown result type (might be due to invalid IL or missing references)
			//IL_0066: Unknown result type (might be due to invalid IL or missing references)
			StringBuilder stringBuilder = new StringBuilder();
			TaggedString val = Translator.Translate(type switch
			{
				SiphonType.KillingBlow => "BS_SiphonSoulOnHit", 
				SiphonType.ConsumeSoul => "BS_SiphonSoul", 
				SiphonType.Influence => "BS_SiphonInfluence", 
				SiphonType.Lovin => "BS_SiphonLovin", 
				SiphonType.Custom => "BS_SiphonCustom", 
				_ => "BS_SiphonUnknown", 
			});
			stringBuilder.AppendLine(TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst()));
			return stringBuilder.ToString();
		}
	}

	public SiphonType type;

	public float gainFactor = 0.01f;

	public float gainOffset;

	public float gainSkill;

	public float architeGeneFactor = 1f;

	public float maxXPDrain = 10000f;

	public float maxXpDrainPercent = 0.2f;

	public float fromTargetSoulFactor = 1f;

	public float fromTargetPsyfocusFactor = 1f;

	public float fromTargetPsyfocusFactor_Max = 1.5f;

	public float targetPsyFocusOffset = -0.8f;

	public float minimumBaseGain = 0.05f;

	public SiphonSoul FuseWith(SiphonSoul other)
	{
		return this with
		{
			gainOffset = Mathf.Max(gainOffset, other.gainOffset),
			gainFactor = Mathf.Max(gainFactor, other.gainFactor),
			gainSkill = Mathf.Max(gainSkill, other.gainSkill),
			architeGeneFactor = Mathf.Max(architeGeneFactor, other.architeGeneFactor),
			maxXPDrain = Mathf.Max(maxXPDrain, other.maxXPDrain),
			maxXpDrainPercent = Mathf.Max(maxXpDrainPercent, other.maxXpDrainPercent),
			fromTargetSoulFactor = Mathf.Max(fromTargetSoulFactor, other.fromTargetSoulFactor),
			fromTargetPsyfocusFactor = Mathf.Max(fromTargetPsyfocusFactor, other.fromTargetPsyfocusFactor),
			fromTargetPsyfocusFactor_Max = Mathf.Max(fromTargetPsyfocusFactor_Max, other.fromTargetPsyfocusFactor_Max),
			targetPsyFocusOffset = Mathf.Max(targetPsyFocusOffset, other.targetPsyFocusOffset),
			minimumBaseGain = Mathf.Max(minimumBaseGain, other.minimumBaseGain)
		};
	}

	[CompilerGenerated]
	protected virtual bool PrintMembers(StringBuilder builder)
	{
		RuntimeHelpers.EnsureSufficientExecutionStack();
		builder.Append("type = ");
		builder.Append(type.ToString());
		builder.Append(", gainFactor = ");
		builder.Append(gainFactor.ToString());
		builder.Append(", gainOffset = ");
		builder.Append(gainOffset.ToString());
		builder.Append(", gainSkill = ");
		builder.Append(gainSkill.ToString());
		builder.Append(", architeGeneFactor = ");
		builder.Append(architeGeneFactor.ToString());
		builder.Append(", maxXPDrain = ");
		builder.Append(maxXPDrain.ToString());
		builder.Append(", maxXpDrainPercent = ");
		builder.Append(maxXpDrainPercent.ToString());
		builder.Append(", fromTargetSoulFactor = ");
		builder.Append(fromTargetSoulFactor.ToString());
		builder.Append(", fromTargetPsyfocusFactor = ");
		builder.Append(fromTargetPsyfocusFactor.ToString());
		builder.Append(", fromTargetPsyfocusFactor_Max = ");
		builder.Append(fromTargetPsyfocusFactor_Max.ToString());
		builder.Append(", targetPsyFocusOffset = ");
		builder.Append(targetPsyFocusOffset.ToString());
		builder.Append(", minimumBaseGain = ");
		builder.Append(minimumBaseGain.ToString());
		builder.Append(", SiphonSoulDescription = ");
		builder.Append((object)SiphonSoulDescription);
		return true;
	}
}
