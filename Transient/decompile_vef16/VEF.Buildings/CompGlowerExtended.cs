using System.Collections.Generic;
using HarmonyLib;
using PipeSystem;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class CompGlowerExtended : ThingComp
{
	[HarmonyPatch(typeof(CompGlower), "SetGlowColorInternal")]
	public static class CompGlower_SetGlowColorInternal_Patch
	{
		public static void Postfix(CompGlower __instance, ColorInt? color)
		{
			CompGlowerExtended compGlowerExtended = ((ThingComp)__instance).parent.GetComp<CompGlowerExtended>();
			if (compGlowerExtended == null && ((ThingComp)__instance).parent is DummyGlower dummyGlower)
			{
				compGlowerExtended = dummyGlower.parentComp;
			}
			if (compGlowerExtended != null)
			{
				compGlowerExtended.glowColorOverride = color;
				compGlowerExtended.UpdateGlower(compGlowerExtended.currentColorInd, compGlowerExtended.ShouldBeLitNow);
			}
		}
	}

	private static readonly FieldRef<CompGlower, bool> glowOnIntField = AccessTools.FieldRefAccess<CompGlower, bool>("glowOnInt");

	private static readonly FieldRef<Thing, Graphic> graphicIntField = AccessTools.FieldRefAccess<Thing, Graphic>("graphicInt");

	private ColorOption currentColor;

	public int currentColorInd;

	public CompGlower compGlower;

	private bool dirty;

	private ColorInt? glowColorOverride;

	private static ThingDef dummyDef;

	public CompProperties_GlowerExtended Props => (CompProperties_GlowerExtended)(object)base.props;

	public virtual ColorInt GlowColor
	{
		get
		{
			//IL_002e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			return (ColorInt)(((_003F?)glowColorOverride) ?? Props.colorOptions[currentColorInd].glowColor);
		}
		set
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			glowColorOverride = value;
		}
	}

	private bool ShouldBeLitNow
	{
		get
		{
			if (!((Thing)base.parent).Spawned)
			{
				return false;
			}
			if (!FlickUtility.WantsToBeOn((Thing)(object)base.parent))
			{
				return false;
			}
			CompPowerTrader val = ThingCompUtility.TryGetComp<CompPowerTrader>((Thing)(object)base.parent);
			if (val != null && !val.PowerOn)
			{
				return false;
			}
			CompRefuelable val2 = ThingCompUtility.TryGetComp<CompRefuelable>((Thing)(object)base.parent);
			if (val2 != null && !val2.HasFuel)
			{
				return false;
			}
			CompSendSignalOnCountdown val3 = ThingCompUtility.TryGetComp<CompSendSignalOnCountdown>((Thing)(object)base.parent);
			if (val3 != null && val3.ticksLeft <= 0)
			{
				return false;
			}
			CompSendSignalOnMotion val4 = ThingCompUtility.TryGetComp<CompSendSignalOnMotion>((Thing)(object)base.parent);
			if (val4 != null && val4.Sent)
			{
				return false;
			}
			CompLoudspeaker val5 = ThingCompUtility.TryGetComp<CompLoudspeaker>((Thing)(object)base.parent);
			if (val5 != null && !val5.Active)
			{
				return false;
			}
			CompHackable val6 = ThingCompUtility.TryGetComp<CompHackable>((Thing)(object)base.parent);
			if (val6 != null && val6.IsHacked && !val6.Props.glowIfHacked)
			{
				return false;
			}
			CompRitualSignalSender val7 = ThingCompUtility.TryGetComp<CompRitualSignalSender>((Thing)(object)base.parent);
			if (val7 != null && !val7.ritualTarget)
			{
				return false;
			}
			ThingWithComps parent = base.parent;
			Building_Crate val8;
			if ((val8 = (Building_Crate)(object)((parent is Building_Crate) ? parent : null)) != null && !((Building_Casket)val8).HasAnyContents)
			{
				return false;
			}
			foreach (CompResourceTrader comp in base.parent.GetComps<CompResourceTrader>())
			{
				if (comp != null && !comp.ResourceOn)
				{
					return false;
				}
			}
			return true;
		}
	}

	public override string TransformLabel(string label)
	{
		if (!GenText.NullOrEmpty(currentColor?.colorLabel))
		{
			return ((ThingComp)this).TransformLabel(label) + " (" + currentColor.colorLabel + ")";
		}
		return ((ThingComp)this).TransformLabel(label);
	}

	public void UpdateLit()
	{
		bool shouldBeLitNow = ShouldBeLitNow;
		if (shouldBeLitNow)
		{
			UpdateGlower(currentColorInd);
			ChangeGraphic();
		}
		else if (compGlower != null && compGlower.Glows != shouldBeLitNow)
		{
			if (!shouldBeLitNow)
			{
				RemoveGlower(((Thing)base.parent).Map);
				return;
			}
			UpdateGlower(currentColorInd);
			ChangeGraphic();
		}
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		currentColor = Props.colorOptions[currentColorInd];
		dirty = true;
		UpdateGlower(currentColorInd, ShouldBeLitNow);
	}

	public override void PostPostMake()
	{
		((ThingComp)this).PostPostMake();
		currentColor = Props.colorOptions[currentColorInd];
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		RemoveGlower(map);
		((ThingComp)this).PostDeSpawn(map, mode);
	}

	public override void PostDestroy(DestroyMode mode, Map previousMap)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		RemoveGlower(previousMap);
		((ThingComp)this).PostDestroy(mode, previousMap);
	}

	public override void CompTick()
	{
		((ThingComp)this).CompTick();
		if (dirty)
		{
			bool shouldBeLitNow = ShouldBeLitNow;
			UpdateGlower(currentColorInd, shouldBeLitNow);
			if (shouldBeLitNow)
			{
				ChangeGraphic();
			}
			else
			{
				RemoveGlower(((Thing)base.parent).Map);
			}
			dirty = false;
		}
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		if (((Thing)base.parent).Faction == Faction.OfPlayer && Props.colorOptions.Count > 1)
		{
			Command_Action val = new Command_Action();
			((Gizmo)val).Disabled = !ShouldBeLitNow;
			((Gizmo)val).disabledReason = TaggedString.op_Implicit(Translator.Translate("VFE.ColorSwitchPowerOff"));
			val.action = delegate
			{
				SwitchColor();
			};
			((Command)val).defaultLabel = TaggedString.op_Implicit(Translator.Translate("VFE.SwitchLightColor"));
			((Command)val).defaultDesc = TaggedString.op_Implicit(Translator.Translate("VFE.SwitchLightColorDesc"));
			((Command)val).hotKey = KeyBindingDefOf.Misc8;
			((Command)val).icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Gizmo/LampColourSwitch", true);
			yield return (Gizmo)(object)val;
		}
		if (compGlower == null)
		{
			yield break;
		}
		foreach (Gizmo item in ((ThingComp)compGlower).CompGetGizmosExtra())
		{
			yield return item;
		}
	}

	private void SwitchColor()
	{
		if (currentColorInd == Props.colorOptions.Count - 1)
		{
			UpdateGlower(0, ShouldBeLitNow);
			ChangeGraphic();
		}
		else
		{
			UpdateGlower(currentColorInd + 1, ShouldBeLitNow);
			ChangeGraphic();
		}
	}

	public void RemoveGlower(Map map)
	{
		if (compGlower != null)
		{
			GlowGrid glowGrid = map.glowGrid;
			if (glowGrid != null)
			{
				glowGrid.DeRegisterGlower(compGlower);
			}
		}
	}

	public static ThingDef GetDummyDef()
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Expected O, but got Unknown
		//IL_005a: Expected O, but got Unknown
		if (dummyDef == null)
		{
			dummyDef = new ThingDef
			{
				defName = "WallLightDummyWorkaround",
				thingClass = typeof(DummyGlower),
				altitudeLayer = (AltitudeLayer)7,
				rotatable = false,
				passability = (Traversability)0,
				category = (ThingCategory)3,
				building = new BuildingProperties
				{
					isEdifice = false
				}
			};
		}
		return dummyDef;
	}

	public void UpdateGlower(int colorOptionInd, bool enableLight = true)
	{
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Expected O, but got Unknown
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0136: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Expected O, but got Unknown
		//IL_0172: Unknown result type (might be due to invalid IL or missing references)
		RemoveGlower(((Thing)base.parent).Map);
		ColorOption colorOption = (currentColor = Props.colorOptions[colorOptionInd]);
		currentColorInd = colorOptionInd;
		compGlower = new CompGlower();
		ThingWithComps val = null;
		if (Props.spawnGlowerInFacedCell)
		{
			Thing obj = ThingMaker.MakeThing(GetDummyDef(), (ThingDef)null);
			val = (ThingWithComps)(object)((obj is ThingWithComps) ? obj : null);
			((DummyGlower)(object)val).parentComp = this;
			IntVec3 position = ((Thing)base.parent).Position;
			Rot4 rotation = ((Thing)base.parent).Rotation;
			IntVec3 val2 = position + ((Rot4)(ref rotation)).FacingCell;
			GenSpawn.Spawn((Thing)(object)val, val2, ((Thing)base.parent).Map, (WipeMode)0);
			if (((Thing)base.parent).Faction != null)
			{
				((Thing)val).SetFaction(((Thing)base.parent).Faction, (Pawn)null);
			}
			((ThingComp)compGlower).parent = val;
		}
		else
		{
			((ThingComp)compGlower).parent = base.parent;
		}
		((ThingComp)compGlower).Initialize((CompProperties)new CompProperties_Glower
		{
			glowColor = (ColorInt)(((_003F?)glowColorOverride) ?? colorOption.glowColor),
			glowRadius = colorOption.glowRadius,
			overlightRadius = colorOption.overlightRadius,
			colorPickerEnabled = colorOption.colorPickerEnabled,
			darklightToggle = colorOption.darklightToggle
		});
		if (enableLight)
		{
			glowOnIntField.Invoke(compGlower) = true;
			((Thing)base.parent).Map.mapDrawer.MapMeshDirty(((Thing)base.parent).Position, MapMeshFlagDef.op_Implicit(MapMeshFlagDefOf.Things));
			((Thing)base.parent).Map.glowGrid.RegisterGlower(compGlower);
		}
		if (Props.spawnGlowerInFacedCell)
		{
			((Entity)val).DeSpawn((DestroyMode)0);
		}
	}

	public void ChangeGraphic()
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		if (!GenText.NullOrEmpty(currentColor.texPath))
		{
			Graphic val = new GraphicData
			{
				graphicClass = ((Thing)base.parent).def.graphicData.graphicClass,
				texPath = currentColor.texPath,
				shaderType = ((Thing)base.parent).def.graphicData.shaderType,
				drawSize = ((Thing)base.parent).def.graphicData.drawSize,
				color = ((Thing)base.parent).def.graphicData.color,
				colorTwo = ((Thing)base.parent).def.graphicData.colorTwo
			}.GraphicColoredFor((Thing)(object)base.parent);
			graphicIntField.Invoke((Thing)(object)base.parent) = val;
			((Thing)base.parent).Map.mapDrawer.MapMeshDirty(((Thing)base.parent).Position, MapMeshFlagDef.op_Implicit(MapMeshFlagDefOf.Things));
		}
	}

	public override void ReceiveCompSignal(string signal)
	{
		switch (signal)
		{
		case "RanOutOfFuel":
		case "ScheduledOff":
		case "MechClusterDefeated":
		case "RitualTargetChanged":
		case "PowerTurnedOn":
		case "PowerTurnedOff":
		case "FlickedOn":
		case "FlickedOff":
		case "Refueled":
		case "ScheduledOn":
		case "Hackend":
		case "CrateContentsChanged":
			UpdateLit();
			break;
		}
		if (CachedSignals.IsResourceSignal(signal))
		{
			UpdateLit();
		}
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<int>(ref currentColorInd, "currentColorInd", 0, false);
		currentColor = Props.colorOptions[currentColorInd];
		Scribe_Values.Look<ColorInt?>(ref glowColorOverride, "glowColorOverride", (ColorInt?)null, false);
	}
}
