using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class CompRefuelable_DualFuel : CompRefuelable
{
	private float secondaryFuel;

	private float configuredSecondaryTargetFuelLevel = -1f;

	public bool allowAutoRefuelSecondary = true;

	public CompProperties_Refuelable_DualFuel Props => ((ThingComp)this).props as CompProperties_Refuelable_DualFuel;

	public float SecondaryFuel => secondaryFuel;

	public float SecondaryFuelPercentOfTarget => secondaryFuel / SecondaryTargetFuelLevel;

	public float SecondaryFuelPercentOfMax => secondaryFuel / Props.secondaryFuelCapacity;

	public bool IsSecondaryFull => SecondaryTargetFuelLevel - secondaryFuel < 1f * Props.SecondaryFuelMultiplierCurrentDifficulty;

	public bool HasSecondaryFuel
	{
		get
		{
			if (secondaryFuel > 0f)
			{
				return secondaryFuel >= Props.minimumSecondaryFueledThreshold;
			}
			return false;
		}
	}

	public float SecondaryTargetFuelLevel
	{
		get
		{
			if (configuredSecondaryTargetFuelLevel >= 0f)
			{
				return configuredSecondaryTargetFuelLevel;
			}
			if (Props.targetSecondaryFuelLevelConfigurable)
			{
				return Props.initialConfigurableSecondaryTargetFuelLevel;
			}
			return Props.secondaryFuelCapacity;
		}
		set
		{
			configuredSecondaryTargetFuelLevel = Mathf.Clamp(value, 0f, Props.secondaryFuelCapacity);
		}
	}

	public bool ShouldAutoRefuelSecondaryNow
	{
		get
		{
			if (SecondaryFuelPercentOfTarget <= Props.autoRefuelSecondaryPercent && !IsSecondaryFull && SecondaryTargetFuelLevel > 0f)
			{
				return ShouldAutoRefuelSecondaryNowIgnoringFuelPct;
			}
			return false;
		}
	}

	public bool ShouldAutoRefuelSecondaryNowIgnoringFuelPct
	{
		get
		{
			if (!FireUtility.IsBurning((Thing)(object)((ThingComp)this).parent) && ((Thing)((ThingComp)this).parent).Map.designationManager.DesignationOn((Thing)(object)((ThingComp)this).parent, DesignationDefOf.Flick) == null)
			{
				return ((Thing)((ThingComp)this).parent).Map.designationManager.DesignationOn((Thing)(object)((ThingComp)this).parent, DesignationDefOf.Deconstruct) == null;
			}
			return false;
		}
	}

	public override void PostExposeData()
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Invalid comparison between Unknown and I4
		((CompRefuelable)this).PostExposeData();
		Scribe_Values.Look<float>(ref secondaryFuel, "secondaryFuel", 0f, false);
		Scribe_Values.Look<float>(ref configuredSecondaryTargetFuelLevel, "configuredSecondaryTargetFuelLevel", -1f, false);
		Scribe_Values.Look<bool>(ref allowAutoRefuelSecondary, "allowAutoRefuelSecondary", false, false);
		if ((int)Scribe.mode == 4 && !Props.showAllowAutoRefuelSecondaryToggle)
		{
			allowAutoRefuelSecondary = Props.initialAllowAutoRefuelSecondary;
		}
	}

	public override void Initialize(CompProperties props)
	{
		((CompRefuelable)this).Initialize(props);
		secondaryFuel = Props.secondaryFuelCapacity * Props.initialSecondaryFuelPercent;
	}

	public void ConsumeSecondaryFuel(float amount)
	{
		if (!(secondaryFuel <= 0f))
		{
			secondaryFuel -= amount;
			if (secondaryFuel <= 0f)
			{
				secondaryFuel = 0f;
			}
		}
	}

	public void RefuelSecondary(List<Thing> fuelThings)
	{
		int num = GetSecondaryFuelCountToFullyRefuel();
		while (num > 0 && fuelThings.Count > 0)
		{
			Thing val = GenCollection.Pop<Thing>(fuelThings);
			int num2 = Mathf.Min(num, val.stackCount);
			RefuelSecondary(num2);
			val.SplitOff(num2).Destroy((DestroyMode)0);
			num -= num2;
		}
	}

	public void RefuelSecondary(float amount)
	{
		secondaryFuel += amount * Props.SecondaryFuelMultiplierCurrentDifficulty;
		if (secondaryFuel > Props.secondaryFuelCapacity)
		{
			secondaryFuel = Props.secondaryFuelCapacity;
		}
	}

	public int GetSecondaryFuelCountToFullyRefuel()
	{
		return Mathf.Max(Mathf.CeilToInt((SecondaryTargetFuelLevel - secondaryFuel) / Props.SecondaryFuelMultiplierCurrentDifficulty), 1);
	}

	public override string CompInspectStringExtra()
	{
		string text = ((CompRefuelable)this).CompInspectStringExtra();
		if (!GenText.NullOrEmpty(text))
		{
			text += "\n";
		}
		text = text + Props.SecondaryFuelLabel + ": " + GenText.ToStringDecimalIfSmall(secondaryFuel) + " / " + GenText.ToStringDecimalIfSmall(Props.secondaryFuelCapacity);
		if (!HasSecondaryFuel && !GenText.NullOrEmpty(Props.outOfSecondaryFuelMessage))
		{
			text = text + "\n" + Props.outOfSecondaryFuelMessage;
			text += $" ({GetSecondaryFuelCountToFullyRefuel()}x {((Def)Props.secondaryFuelFilter.AnyAllowedDef).label})";
		}
		return text;
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		foreach (Gizmo item in _003C_003En__0())
		{
			yield return item;
		}
		if (Find.Selector.SelectedObjects.Count == 1)
		{
			yield return (Gizmo)(object)new Gizmo_SetSecondaryFuelLevel(this);
		}
		else if (Props.showAllowAutoRefuelSecondaryToggle)
		{
			string text = TaggedString.op_Implicit(allowAutoRefuelSecondary ? Translator.Translate("On") : Translator.Translate("Off"));
			yield return (Gizmo)new Command_Toggle
			{
				isActive = () => allowAutoRefuelSecondary,
				toggleAction = delegate
				{
					allowAutoRefuelSecondary = !allowAutoRefuelSecondary;
				},
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("VFES_CommandToggleAllowAutoRefuelSecondary")),
				defaultDesc = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CommandToggleAllowAutoRefuelDescMult", NamedArgumentUtility.Named((object)GenText.UncapitalizeFirst(text), "ONOFF"))),
				icon = (Texture)(object)(allowAutoRefuelSecondary ? TexCommand.ForbidOn : TexCommand.ForbidOff),
				Order = 21f
			};
		}
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((CompRefuelable)this).CompGetGizmosExtra();
	}
}
