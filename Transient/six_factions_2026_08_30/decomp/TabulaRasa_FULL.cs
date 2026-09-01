using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Runtime.Versioning;
using System.Security;
using System.Security.Permissions;
using System.Text;
using System.Xml;
using HarmonyLib;
using Microsoft.CodeAnalysis;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;
using Verse.Grammar;
using Verse.Sound;
using Verse.Steam;

[assembly: CompilationRelaxations(8)]
[assembly: RuntimeCompatibility(WrapNonExceptionThrows = true)]
[assembly: Debuggable(DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints)]
[assembly: AssemblyTitle("TabulaRasa")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("TabulaRasa")]
[assembly: AssemblyCopyright("Copyright c  2021")]
[assembly: AssemblyTrademark("")]
[assembly: ComVisible(false)]
[assembly: Guid("78de7258-9b43-4aa0-88ac-4fa70049ef0a")]
[assembly: TargetFramework(".NETFramework,Version=v4.7.2", FrameworkDisplayName = ".NET Framework 4.7.2")]
[assembly: SecurityPermission(SecurityAction.RequestMinimum, SkipVerification = true)]
[assembly: AssemblyVersion("1.6.9701.33495")]
[module: UnverifiableCode]
[module: RefSafetyRules(11)]
namespace Microsoft.CodeAnalysis
{
	[CompilerGenerated]
	[Embedded]
	internal sealed class EmbeddedAttribute : Attribute
	{
	}
}
namespace System.Runtime.CompilerServices
{
	[CompilerGenerated]
	[Embedded]
	[AttributeUsage(AttributeTargets.Module, AllowMultiple = false, Inherited = false)]
	internal sealed class RefSafetyRulesAttribute : Attribute
	{
		public readonly int Version;

		public RefSafetyRulesAttribute(int P_0)
		{
			Version = P_0;
		}
	}
}
namespace TabulaRasa
{
	public class Apparel_Customizable : Apparel
	{
		public bool colorsCalculated;

		public Color drawColorFirst = Color.white;

		public Color drawColorSecond = Color.white;

		public DefModExt_ApparelCustomizable modExtCached;

		public DefModExt_ApparelCustomizable ModExt
		{
			get
			{
				if (modExtCached == null)
				{
					modExtCached = ((Def)((Thing)this).def).GetModExtension<DefModExt_ApparelCustomizable>();
				}
				return modExtCached;
			}
		}

		public void InitColors(Color first, Color second)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			//IL_0009: Unknown result type (might be due to invalid IL or missing references)
			drawColorFirst = first;
			drawColorSecond = second;
		}

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			((ThingWithComps)this).SpawnSetup(map, respawningAfterLoad);
			if (!respawningAfterLoad)
			{
				InitColors(ModExt.defaultColorFirst, ModExt.defaultColorSecond);
			}
		}

		public override void ExposeData()
		{
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			((Apparel)this).ExposeData();
			Scribe_Values.Look<Color>(ref drawColorFirst, "drawColorFirst", Color.white, false);
			Scribe_Values.Look<Color>(ref drawColorSecond, "drawColorSecond", Color.white, false);
		}
	}
	public class DefModExt_ApparelCustomizable : DefModExtension
	{
		public Color defaultColorFirst = Color.white;

		public Color defaultColorSecond = Color.white;
	}
	public class Building_MultiMoverDoor : Building_SupportedDoor
	{
		public DefModExt_MultiMoverDoor modExt;

		public Graphic graphicRightInt;

		public Graphic GraphicRight
		{
			get
			{
				if (graphicRightInt == null)
				{
					if (modExt.rightMoverData == null)
					{
						return BaseContent.BadGraphic;
					}
					graphicRightInt = modExt.rightMoverData.GraphicColoredFor((Thing)(object)this);
				}
				return graphicRightInt;
			}
		}

		public override bool CanDrawMovers => false;

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			((Building_Door)this).SpawnSetup(map, respawningAfterLoad);
			modExt = ((Def)((Thing)this).def).GetModExtension<DefModExt_MultiMoverDoor>();
		}

		public override void DrawAt(Vector3 drawLoc, bool flip = false)
		{
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Unknown result type (might be due to invalid IL or missing references)
			//IL_0040: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0066: Unknown result type (might be due to invalid IL or missing references)
			((Building_Door)this).DoorPreDraw();
			float offsetDist = 0f + 0.45f * ((Building_Door)this).OpenPct;
			DrawMover(drawLoc, offsetDist, ((Thing)this).Graphic, Altitudes.AltitudeFor((AltitudeLayer)14), Vector3.one, ((Thing)this).Graphic.ShadowGraphic, flipped: false);
			DrawMover(drawLoc, offsetDist, GraphicRight, Altitudes.AltitudeFor((AltitudeLayer)14), Vector3.one, GraphicRight.ShadowGraphic, flipped: true);
			((Building_SupportedDoor)this).DrawAt(drawLoc, flip);
		}

		public void DrawMover(Vector3 drawPos, float offsetDist, Graphic graphic, float altitude, Vector3 drawScaleFactor, Graphic_Shadow shadowGraphic, bool flipped)
		{
			//IL_0058: Unknown result type (might be due to invalid IL or missing references)
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0068: Unknown result type (might be due to invalid IL or missing references)
			//IL_006d: Unknown result type (might be due to invalid IL or missing references)
			//IL_006e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0073: Unknown result type (might be due to invalid IL or missing references)
			//IL_0074: Unknown result type (might be due to invalid IL or missing references)
			//IL_0075: Unknown result type (might be due to invalid IL or missing references)
			//IL_007f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0080: Unknown result type (might be due to invalid IL or missing references)
			//IL_0082: Unknown result type (might be due to invalid IL or missing references)
			//IL_0087: Unknown result type (might be due to invalid IL or missing references)
			//IL_008c: Unknown result type (might be due to invalid IL or missing references)
			//IL_008e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0090: Unknown result type (might be due to invalid IL or missing references)
			//IL_0095: Unknown result type (might be due to invalid IL or missing references)
			//IL_0099: Unknown result type (might be due to invalid IL or missing references)
			//IL_00af: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
			Vector3 val = default(Vector3);
			Mesh val2;
			if (!flipped)
			{
				((Vector3)(ref val))..ctor(0f, 0f, (float)(-((Thing)this).def.size.x));
				val2 = MeshPool.plane10;
			}
			else
			{
				((Vector3)(ref val))..ctor(0f, 0f, (float)((Thing)this).def.size.x);
				val2 = MeshPool.plane10Flip;
			}
			Rot4 rotation = ((Thing)this).Rotation;
			((Rot4)(ref rotation)).Rotate((RotationDirection)1);
			val = ((Rot4)(ref rotation)).AsQuat * val;
			Vector3 val3 = drawPos;
			val3.y = altitude;
			val3 += val * offsetDist;
			Mesh obj = val2;
			Vector3 val4 = val3;
			Rot4 rotation2 = ((Thing)this).Rotation;
			Graphics.DrawMesh(obj, Matrix4x4.TRS(val4, ((Rot4)(ref rotation2)).AsQuat, new Vector3((float)((Thing)this).def.size.x * drawScaleFactor.x, drawScaleFactor.y, (float)((Thing)this).def.size.z * drawScaleFactor.z)), graphic.MatAt(((Thing)this).Rotation, (Thing)(object)this), 0);
			if (shadowGraphic != null)
			{
				((Graphic)shadowGraphic).DrawWorker(val3, ((Thing)this).Rotation, ((Thing)this).def, (Thing)(object)this, 0f);
			}
		}
	}
	public class Building_RandomGraphic : Building
	{
		public override void PostMake()
		{
			((ThingWithComps)this).PostMake();
			Graphic graphic = ((Thing)this).Graphic;
			Graphic_Random val = (Graphic_Random)(((object)((graphic is Graphic_Random) ? graphic : null)) ?? ((object)/*isinst with value type is only supported in some contexts*/));
			((Thing)this).overrideGraphicIndex = Rand.RangeInclusive(0, val.SubGraphicsCount);
		}
	}
	public class Building_Switcher : Building
	{
		[CompilerGenerated]
		private sealed class <GetGizmos>d__7 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Building_Switcher <>4__this;

			private IEnumerator<Gizmo> <>7__wrap1;

			Gizmo IEnumerator<Gizmo>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <GetGizmos>d__7(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>7__wrap1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_008c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0091: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
				//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
				//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
				//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
				//IL_00e6: Expected O, but got Unknown
				try
				{
					int num = <>1__state;
					Building_Switcher CS$<>8__locals7 = <>4__this;
					Command_Action val;
					switch (num)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<>7__wrap1 = CS$<>8__locals7.<>n__0().GetEnumerator();
						<>1__state = -3;
						goto IL_0072;
					case 1:
						<>1__state = -3;
						goto IL_0072;
					case 2:
						{
							<>1__state = -1;
							return false;
						}
						IL_0072:
						if (<>7__wrap1.MoveNext())
						{
							Gizmo current = <>7__wrap1.Current;
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = null;
						val = new Command_Action
						{
							action = delegate
							{
								CS$<>8__locals7.SwitchBuilding();
							},
							defaultDesc = CS$<>8__locals7.ModExt.description,
							defaultLabel = CS$<>8__locals7.ModExt.label,
							activateSound = SoundDef.Named("Click"),
							disabled = !CS$<>8__locals7.Active
						};
						if (CS$<>8__locals7.ModExt.icon != null)
						{
							((Command)val).icon = (Texture)(object)ContentFinder<Texture2D>.Get(CS$<>8__locals7.ModExt.icon, true);
						}
						<>2__current = (Gizmo)(object)val;
						<>1__state = 2;
						return true;
					}
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				if (<>7__wrap1 != null)
				{
					<>7__wrap1.Dispose();
				}
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
			{
				<GetGizmos>d__7 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <GetGizmos>d__7(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		public DefModExt_Switcher modExt;

		public CompPowerTrader powerComp;

		public DefModExt_Switcher ModExt
		{
			get
			{
				if (modExt == null)
				{
					modExt = ((Def)((Thing)this).def).GetModExtension<DefModExt_Switcher>();
				}
				return modExt;
			}
		}

		public bool Active
		{
			get
			{
				if (powerComp != null)
				{
					return powerComp.PowerOn;
				}
				return true;
			}
		}

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			((Building)this).SpawnSetup(map, respawningAfterLoad);
			powerComp = ((ThingWithComps)this).GetComp<CompPowerTrader>();
		}

		[IteratorStateMachine(typeof(<GetGizmos>d__7))]
		public override IEnumerable<Gizmo> GetGizmos()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <GetGizmos>d__7(-2)
			{
				<>4__this = this
			};
		}

		public void SwitchBuilding()
		{
			//IL_0067: Unknown result type (might be due to invalid IL or missing references)
			//IL_0073: Unknown result type (might be due to invalid IL or missing references)
			//IL_0056: Unknown result type (might be due to invalid IL or missing references)
			//IL_005c: Unknown result type (might be due to invalid IL or missing references)
			if (Active)
			{
				Thing obj = ThingMaker.MakeThing(ModExt.buildingDef, ((Thing)this).Stuff);
				obj.SetFactionDirect(((Thing)this).Faction);
				obj.HitPoints = ((Thing)this).HitPoints;
				ThingUtility.DestroyedOrNull((Thing)(object)this);
				if (ModExt.activateSound != null)
				{
					SoundStarter.PlayOneShot(ModExt.activateSound, SoundInfo.InMap(TargetInfo.op_Implicit((Thing)(object)this), (MaintenanceType)0));
				}
				GenSpawn.Spawn(obj, ((Thing)this).Position, ((Thing)this).Map, ((Thing)this).Rotation, (WipeMode)0, false, false);
			}
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private IEnumerable<Gizmo> <>n__0()
		{
			return ((Building)this).GetGizmos();
		}
	}
	public class ArchitectSubCatDesignators
	{
		public string category;

		public List<Designator> designators;

		public bool Visible
		{
			get
			{
				if (category != "Orders")
				{
					return GenCollection.Any<Designator>(designators, (Predicate<Designator>)((Designator d) => ((Gizmo)d).Visible));
				}
				return false;
			}
		}
	}
	public class FloatMenuProvider_SlotLoadable : FloatMenuOptionProvider
	{
		public override bool Multiselect => false;

		public override bool RequiresManipulation => true;

		public override bool Drafted => true;

		public override bool Undrafted => true;

		public override bool TargetThingValid(Thing thing, FloatMenuContext context)
		{
			return ThingCompUtility.HasComp<Comp_SlotLoadable>(thing);
		}

		public override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
		{
			//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			//IL_006a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0074: Unknown result type (might be due to invalid IL or missing references)
			//IL_0079: Unknown result type (might be due to invalid IL or missing references)
			//IL_0083: Unknown result type (might be due to invalid IL or missing references)
			//IL_009a: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a0: Expected O, but got Unknown
			//IL_011e: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f0: Unknown result type (might be due to invalid IL or missing references)
			//IL_0107: Unknown result type (might be due to invalid IL or missing references)
			//IL_010d: Expected O, but got Unknown
			//IL_01ab: Unknown result type (might be due to invalid IL or missing references)
			//IL_01b0: Unknown result type (might be due to invalid IL or missing references)
			//IL_01d2: Unknown result type (might be due to invalid IL or missing references)
			//IL_01d8: Expected O, but got Unknown
			//IL_0134: Unknown result type (might be due to invalid IL or missing references)
			//IL_0139: Unknown result type (might be due to invalid IL or missing references)
			//IL_0143: Unknown result type (might be due to invalid IL or missing references)
			//IL_0163: Unknown result type (might be due to invalid IL or missing references)
			//IL_0172: Unknown result type (might be due to invalid IL or missing references)
			//IL_0177: Unknown result type (might be due to invalid IL or missing references)
			//IL_017c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0186: Unknown result type (might be due to invalid IL or missing references)
			//IL_019d: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a3: Expected O, but got Unknown
			Pawn pawn = context.FirstSelectedPawn;
			if (pawn == null)
			{
				return null;
			}
			if (clickedThing == null)
			{
				return null;
			}
			string label = ((Entity)clickedThing).Label;
			if (!pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation))
			{
				return new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CannotEquip", NamedArgument.op_Implicit(label)) + " (" + Translator.Translate("Incapable") + ")"), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
			}
			if (!ReachabilityUtility.CanReach(pawn, LocalTargetInfo.op_Implicit(clickedThing), (PathEndMode)3, (Danger)3, false, false, (TraverseMode)0))
			{
				return new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CannotEquip", NamedArgument.op_Implicit(label)) + " (" + Translator.Translate("NoPath") + ")"), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
			}
			if (!ReservationUtility.CanReserve(pawn, LocalTargetInfo.op_Implicit(clickedThing), 1, -1, (ReservationLayerDef)null, false))
			{
				return new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CannotEquip", NamedArgument.op_Implicit(label)) + " (" + TranslatorFormattedStringExtensions.Translate("ReservedBy", NamedArgument.op_Implicit(((Entity)((Thing)pawn).Map.physicalInteractionReservationManager.FirstReserverOf(LocalTargetInfo.op_Implicit(clickedThing))).LabelShort)) + ")"), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
			}
			return new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Equip", NamedArgument.op_Implicit(label))), (Action)delegate
			{
				//IL_0023: Unknown result type (might be due to invalid IL or missing references)
				//IL_0040: Unknown result type (might be due to invalid IL or missing references)
				ForbidUtility.SetForbidden(clickedThing, false, true);
				pawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(TabulaRasaDefOf.TabulaRasa_GatherSlotItem, LocalTargetInfo.op_Implicit(clickedThing)), (JobTag?)(JobTag)0, false);
				FleckMaker.Static(clickedThing.DrawPos, clickedThing.Map, FleckDefOf.FeedbackEquip, 1f);
			}, (MenuOptionPriority)5, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
		}
	}
	[HarmonyPatch(typeof(ArchitectCategoryTab), "DesignationTabOnGUI")]
	public static class Patch_ArchitectCategoryTab_DesignationTabOnGUI
	{
		[HarmonyPrefix]
		public static bool Prefix(ArchitectCategoryTab __instance, Designator forceActivatedCommand)
		{
			if (((Def)__instance.def).HasModExtension<DefModExt_SubcategoryDisplay>())
			{
				SubcategoryUtil.PopulateArchitectCategoryTab(__instance);
				SubcategoryUtil.DrawSubcategoryWindow(__instance, forceActivatedCommand);
				return false;
			}
			return true;
		}
	}
	[HarmonyPatch(/*Could not decode attribute arguments.*/)]
	public static class Patch_Plant_DyingBecauseExposedToLight
	{
		[HarmonyPostfix]
		public static void Postfix(Plant __instance, ref bool __result)
		{
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			DefModExt_PlantStuff modExtension = ((Def)((Thing)__instance).def).GetModExtension<DefModExt_PlantStuff>();
			if (modExtension == null || !__result)
			{
				return;
			}
			bool flag = ((Thing)__instance).Map.glowGrid.GroundGlowAt(((Thing)__instance).Position, true, false) > 0f;
			if (modExtension.diesInSunlight && flag)
			{
				__result = true;
			}
			else if (modExtension.diesInDarklight.HasValue)
			{
				bool flag2 = DarklightUtility.IsDarklightAt(((Thing)__instance).Position, ((Thing)__instance).Map);
				if (modExtension.diesInDarklight.Value && flag2)
				{
					__result = true;
				}
				else if (!modExtension.diesInDarklight.Value && flag2)
				{
					__result = false;
				}
			}
		}
	}
	public class DefModExt_MultiMoverDoor : DefModExtension
	{
		public GraphicData rightMoverData;
	}
	public class DefModExt_PlantStuff : DefModExtension
	{
		public bool freshWaterPlant;

		public bool oceanWaterPlant;

		public float distToNearestOther = 11.3f;

		public bool diesInSunlight;

		public bool? diesInDarklight = false;
	}
	public class DefModExt_InvisibleWeapon : DefModExtension
	{
	}
	[HarmonyPatch(typeof(PawnRenderUtility), "DrawEquipmentAiming")]
	public static class Patch_PawnRenderUtility_DrawEquipmentAiming
	{
		[HarmonyPrefix]
		public static bool Prefix(Thing eq, Vector3 drawLoc, float aimAngle)
		{
			if (eq != null && ((Def)eq.def).HasModExtension<DefModExt_InvisibleWeapon>())
			{
				return false;
			}
			return true;
		}
	}
	public class DefModExt_SubcategoryDisplay : DefModExtension
	{
		public List<string> subcategories = new List<string>();
	}
	public class PawnRenderNode_FurCustom : PawnRenderNode
	{
		public override Shader DefaultShader => ShaderDatabase.CutoutSkinOverlay;

		public PawnRenderNode_FurCustom(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
			: base(pawn, props, tree)
		{
		}

		public override Graphic GraphicFor(Pawn pawn)
		{
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Unknown result type (might be due to invalid IL or missing references)
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Invalid comparison between Unknown and I4
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			//IL_006b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0070: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Unknown result type (might be due to invalid IL or missing references)
			//IL_0079: Unknown result type (might be due to invalid IL or missing references)
			//IL_007e: Unknown result type (might be due to invalid IL or missing references)
			//IL_009e: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
			if (!ModLister.CheckBiotech("Fur"))
			{
				return null;
			}
			if (pawn.story?.furDef == null)
			{
				return null;
			}
			AttachmentColorType colorType = base.props.colorType;
			Color val = (Color)(((int)colorType == 0) ? (((??)base.props.color) ?? pawn.story.hairColor) : (((int)colorType != 2) ? pawn.story.HairColor : pawn.story.SkinColor));
			Pawn_StoryTracker story = pawn.story;
			return GraphicDatabase.Get<Graphic_Multi>((story != null) ? story.furDef.GetFurBodyGraphicPath(pawn) : null, ((PawnRenderNode)this).ShaderFor(pawn), Vector2.one, val);
		}

		public override Color ColorFor(Pawn pawn)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			return ((PawnRenderNode)this).ColorFor(pawn);
		}
	}
	public class ButcherUtil
	{
		public static void SpawnDrops(Pawn pawn, IntVec3 position, Map map)
		{
			//IL_0083: Unknown result type (might be due to invalid IL or missing references)
			float coverageOfNotMissingNaturalParts = pawn.health.hediffSet.GetCoverageOfNotMissingNaturalParts(pawn.RaceProps.body.corePart);
			foreach (ThingDefCountClass butcherProduct in ((Thing)pawn).def.butcherProducts)
			{
				int num = (int)Math.Ceiling((float)butcherProduct.count * coverageOfNotMissingNaturalParts);
				if (num > 0)
				{
					do
					{
						Thing val = ThingMaker.MakeThing(butcherProduct.thingDef, (ThingDef)null);
						val.stackCount = Math.Min(num, butcherProduct.thingDef.stackLimit);
						num -= val.stackCount;
						GenPlace.TryPlaceThing(val, position, map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
					}
					while (num > 0);
				}
			}
		}
	}
	public class CompProperties_SlotLoadable : CompProperties
	{
		public bool gizmosOnEquip = true;

		public List<SlotLoadableDef> slots = new List<SlotLoadableDef>();

		public CompProperties_SlotLoadable()
		{
			base.compClass = typeof(Comp_SlotLoadable);
		}
	}
	public class CompProperties_TargetEffectApplyHediff : CompProperties
	{
		public HediffDef hediff;

		public CompProperties_TargetEffectApplyHediff()
		{
			base.compClass = typeof(CompTargetEffect_ApplyHediff);
		}
	}
	public class CompTargetable_NotXenotype : CompTargetable
	{
		[CompilerGenerated]
		private sealed class <GetTargets>d__3 : IEnumerable<Thing>, IEnumerable, IEnumerator<Thing>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Thing <>2__current;

			private int <>l__initialThreadId;

			private Thing targetChosenByPlayer;

			public Thing <>3__targetChosenByPlayer;

			Thing IEnumerator<Thing>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <GetTargets>d__3(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				switch (<>1__state)
				{
				default:
					return false;
				case 0:
					<>1__state = -1;
					<>2__current = targetChosenByPlayer;
					<>1__state = 1;
					return true;
				case 1:
					<>1__state = -1;
					return false;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Thing> IEnumerable<Thing>.GetEnumerator()
			{
				<GetTargets>d__3 <GetTargets>d__;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					<GetTargets>d__ = this;
				}
				else
				{
					<GetTargets>d__ = new <GetTargets>d__3(0);
				}
				<GetTargets>d__.targetChosenByPlayer = <>3__targetChosenByPlayer;
				return <GetTargets>d__;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Thing>)this).GetEnumerator();
			}
		}

		public override bool PlayerChoosesTarget => true;

		public override TargetingParameters GetTargetingParameters()
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_0034: Expected O, but got Unknown
			return new TargetingParameters
			{
				canTargetPawns = true,
				canTargetBuildings = false,
				canTargetItems = false,
				mapObjectTargetsMustBeAutoAttackable = false,
				validator = (TargetInfo x) => TargetValidator(((TargetInfo)(ref x)).Thing)
			};
		}

		[IteratorStateMachine(typeof(<GetTargets>d__3))]
		public override IEnumerable<Thing> GetTargets(Thing targetChosenByPlayer = null)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <GetTargets>d__3(-2)
			{
				<>3__targetChosenByPlayer = targetChosenByPlayer
			};
		}

		public bool TargetValidator(Thing t)
		{
			Pawn val = (Pawn)(object)((t is Pawn) ? t : null);
			if (val != null)
			{
				DefModExt_Xenotype modExtension = ((Def)((Thing)((ThingComp)this).parent).def).GetModExtension<DefModExt_Xenotype>();
				if (modExtension != null)
				{
					object obj;
					if (val == null)
					{
						obj = null;
					}
					else
					{
						Pawn_GeneTracker genes = val.genes;
						obj = ((genes != null) ? genes.Xenotype : null);
					}
					if (obj == null || val.genes.Xenotype == modExtension.xenotype)
					{
						return false;
					}
				}
			}
			return true;
		}
	}
	public class CompTargetEffect_ApplyHediff : CompTargetEffect
	{
		public CompProperties_TargetEffectApplyHediff Props => (CompProperties_TargetEffectApplyHediff)(object)((ThingComp)this).props;

		public override void DoEffectOn(Pawn user, Thing target)
		{
			//IL_000a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			if (user.IsColonistPlayerControlled && ReservationUtility.CanReserveAndReach(user, LocalTargetInfo.op_Implicit(target), (PathEndMode)2, (Danger)3, 1, -1, (ReservationLayerDef)null, false))
			{
				Job val = JobMaker.MakeJob(TabulaRasaDefOf.TabulaRasa_UseEffectApplyHediff, LocalTargetInfo.op_Implicit(target), LocalTargetInfo.op_Implicit((Thing)(object)((ThingComp)this).parent));
				val.count = 1;
				((JobDriver_ApplyHediff)(object)val.GetCachedDriver(user)).hediffDef = Props.hediff;
				user.jobs.TryTakeOrderedJob(val, (JobTag?)(JobTag)0, false);
			}
		}
	}
	public class Comp_SlotLoadable : ThingComp
	{
		[CompilerGenerated]
		private sealed class <>c__DisplayClass26_0
		{
			public SlotLoadable slot;

			public Comp_SlotLoadable <>4__this;

			internal void <EquippedGizmos>b__1()
			{
				<>4__this.ProcessInput(slot);
			}

			internal void <EquippedGizmos>b__2()
			{
				<>4__this.ProcessInput(slot);
			}
		}

		[CompilerGenerated]
		private sealed class <EquippedGizmos>d__26 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Comp_SlotLoadable <>4__this;

			private List<SlotLoadable>.Enumerator <>7__wrap1;

			Gizmo IEnumerator<Gizmo>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <EquippedGizmos>d__26(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || (uint)(num - 2) <= 1u)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>7__wrap1 = default(List<SlotLoadable>.Enumerator);
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_0060: Unknown result type (might be due to invalid IL or missing references)
				//IL_0065: Unknown result type (might be due to invalid IL or missing references)
				//IL_006b: Unknown result type (might be due to invalid IL or missing references)
				//IL_007a: Unknown result type (might be due to invalid IL or missing references)
				//IL_0080: Unknown result type (might be due to invalid IL or missing references)
				//IL_008f: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
				//IL_00b7: Expected O, but got Unknown
				//IL_0179: Unknown result type (might be due to invalid IL or missing references)
				//IL_017e: Unknown result type (might be due to invalid IL or missing references)
				//IL_018f: Unknown result type (might be due to invalid IL or missing references)
				//IL_01a0: Unknown result type (might be due to invalid IL or missing references)
				//IL_01b2: Unknown result type (might be due to invalid IL or missing references)
				//IL_01b9: Unknown result type (might be due to invalid IL or missing references)
				//IL_01be: Unknown result type (might be due to invalid IL or missing references)
				//IL_01c3: Unknown result type (might be due to invalid IL or missing references)
				//IL_01da: Expected O, but got Unknown
				//IL_0116: Unknown result type (might be due to invalid IL or missing references)
				//IL_011b: Unknown result type (might be due to invalid IL or missing references)
				//IL_012c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0137: Unknown result type (might be due to invalid IL or missing references)
				//IL_0149: Unknown result type (might be due to invalid IL or missing references)
				//IL_0160: Expected O, but got Unknown
				try
				{
					int num = <>1__state;
					Comp_SlotLoadable CS$<>8__locals16 = <>4__this;
					switch (num)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						if (GenList.NullOrEmpty<SlotLoadable>((IList<SlotLoadable>)CS$<>8__locals16.slots) || !((Thing)CS$<>8__locals16.GetPawn).Faction.IsPlayer)
						{
							break;
						}
						if (CS$<>8__locals16.isGathering)
						{
							<>2__current = (Gizmo)new Command_Action
							{
								defaultLabel = TaggedString.op_Implicit(Translator.Translate("Designator_Cancel")),
								defaultDesc = TaggedString.op_Implicit(Translator.Translate("Designator_CancelDesc")),
								icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Designators/Cancel", true),
								action = delegate
								{
									CS$<>8__locals16.TryCancel();
								}
							};
							<>1__state = 1;
							return true;
						}
						goto IL_00cc;
					case 1:
						<>1__state = -1;
						goto IL_00cc;
					case 2:
						<>1__state = -3;
						goto IL_01ed;
					case 3:
						{
							<>1__state = -3;
							goto IL_01ed;
						}
						IL_00cc:
						<>7__wrap1 = CS$<>8__locals16.slots.GetEnumerator();
						<>1__state = -3;
						goto IL_01ed;
						IL_01ed:
						if (<>7__wrap1.MoveNext())
						{
							<>c__DisplayClass26_0 CS$<>8__locals20 = new <>c__DisplayClass26_0
							{
								<>4__this = CS$<>8__locals16,
								slot = <>7__wrap1.Current
							};
							if (CS$<>8__locals20.slot.IsEmpty())
							{
								<>2__current = (Gizmo)new Command_Action
								{
									defaultLabel = ((Thing)CS$<>8__locals20.slot).LabelNoCount,
									icon = (Texture)(object)Command.BGTex,
									defaultDesc = CS$<>8__locals16.SlotDesc(CS$<>8__locals20.slot),
									action = delegate
									{
										CS$<>8__locals20.<>4__this.ProcessInput(CS$<>8__locals20.slot);
									}
								};
								<>1__state = 2;
								return true;
							}
							<>2__current = (Gizmo)new Command_Action
							{
								defaultLabel = ((Thing)CS$<>8__locals20.slot).LabelNoCount,
								icon = (Texture)(object)CS$<>8__locals20.slot.SlotIcon(),
								defaultDesc = CS$<>8__locals16.SlotDesc(CS$<>8__locals20.slot),
								defaultIconColor = CS$<>8__locals20.slot.SlotColor(),
								action = delegate
								{
									CS$<>8__locals20.<>4__this.ProcessInput(CS$<>8__locals20.slot);
								}
							};
							<>1__state = 3;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = default(List<SlotLoadable>.Enumerator);
						break;
					}
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				((IDisposable)<>7__wrap1/*cast due to .constrained prefix*/).Dispose();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
			{
				<EquippedGizmos>d__26 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <EquippedGizmos>d__26(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		public bool GizmosOnEquip = true;

		public bool isGathering;

		public bool isInitialized;

		public List<SlotLoadable> slots = new List<SlotLoadable>();

		public bool IsInitialized => isInitialized;

		public List<SlotLoadable> Slots => slots;

		public List<SlotLoadableDef> SlotDefs
		{
			get
			{
				List<SlotLoadableDef> list = new List<SlotLoadableDef>();
				if (slots != null)
				{
					foreach (SlotLoadable slot in slots)
					{
						list.Add(((Thing)slot).def as SlotLoadableDef);
					}
				}
				return list;
			}
		}

		public Map GetMap
		{
			get
			{
				Map map = ((Thing)base.parent).Map;
				if (map == null && GetPawn != null)
				{
					map = ((Thing)GetPawn).Map;
				}
				return map;
			}
		}

		public CompEquippable GetEquippable => base.parent.GetComp<CompEquippable>();

		private Pawn GetPawn => GetEquippable.verbTracker.PrimaryVerb.CasterPawn;

		public CompProperties_SlotLoadable Props => (CompProperties_SlotLoadable)(object)base.props;

		public void Initialize()
		{
			if (isInitialized)
			{
				return;
			}
			isInitialized = true;
			if (Props?.slots == null)
			{
				return;
			}
			foreach (SlotLoadableDef slot in Props.slots)
			{
				SlotLoadable item = new SlotLoadable(slot, (Thing)(object)base.parent);
				LogUtil.Message("Added Slot");
				slots.Add(item);
			}
		}

		public override void PostPostMake()
		{
			((ThingComp)this).PostPostMake();
			if (GenList.NullOrEmpty<SlotLoadable>((IList<SlotLoadable>)slots) && Props?.slots != null)
			{
				Initialize();
			}
		}

		public override void CompTick()
		{
			((ThingComp)this).CompTick();
		}

		private void TryCancel(string reason = "")
		{
			Pawn getPawn = GetPawn;
			if (getPawn != null)
			{
				if (getPawn.CurJob.def == TabulaRasaDefOf.TabulaRasa_GatherSlotItem)
				{
					getPawn.jobs.StopAll(false, true);
				}
				isGathering = false;
			}
		}

		private void TryGiveLoadSlotJob(Thing itemToLoad)
		{
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			if (GetPawn != null)
			{
				if (!GetPawn.Drafted)
				{
					isGathering = true;
					Job val = JobMaker.MakeJob(TabulaRasaDefOf.TabulaRasa_GatherSlotItem, LocalTargetInfo.op_Implicit(itemToLoad));
					val.count = 1;
					GetPawn.jobs.TryTakeOrderedJob(val, (JobTag?)(JobTag)0, false);
				}
				else
				{
					Messages.Message($"{((Entity)GetPawn).Label} is drafted.", MessageTypeDefOf.RejectInput, true);
				}
			}
		}

		public virtual bool TryLoadSlot(Thing thing)
		{
			isGathering = false;
			if (slots != null)
			{
				SlotLoadable slotLoadable = GenCollection.FirstOrDefault<SlotLoadable>(slots, (Predicate<SlotLoadable>)((SlotLoadable x) => x.IsEmpty() && x.CanLoad(thing.def)));
				if (slotLoadable == null)
				{
					slotLoadable = GenCollection.FirstOrDefault<SlotLoadable>(slots, (Predicate<SlotLoadable>)((SlotLoadable y) => y.CanLoad(thing.def)));
				}
				if (slotLoadable != null && slotLoadable.TryLoadSlot(thing, emptyIfFilled: true))
				{
					return true;
				}
			}
			return false;
		}

		public void ProcessInput(SlotLoadable slot)
		{
			//IL_0270: Unknown result type (might be due to invalid IL or missing references)
			//IL_027a: Expected O, but got Unknown
			//IL_0260: Unknown result type (might be due to invalid IL or missing references)
			//IL_026a: Expected O, but got Unknown
			//IL_01fc: Unknown result type (might be due to invalid IL or missing references)
			//IL_0203: Expected O, but got Unknown
			//IL_0100: Unknown result type (might be due to invalid IL or missing references)
			//IL_010a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0120: Unknown result type (might be due to invalid IL or missing references)
			//IL_0125: Unknown result type (might be due to invalid IL or missing references)
			//IL_0128: Unknown result type (might be due to invalid IL or missing references)
			//IL_0148: Unknown result type (might be due to invalid IL or missing references)
			//IL_0152: Expected O, but got Unknown
			//IL_0199: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a0: Expected O, but got Unknown
			List<FloatMenuOption> list = new List<FloatMenuOption>();
			if (!isGathering)
			{
				Map map = GetMap;
				if (slot.SlotOccupant == null)
				{
					List<ThingDef> slottableTypes = slot.SlottableTypes;
					if (slottableTypes != null)
					{
						if (slottableTypes.Count > 0)
						{
							foreach (ThingDef item in slottableTypes)
							{
								Thing thingToLoad = GenCollection.FirstOrDefault<Thing>(map.listerThings.ThingsOfDef(item), (Predicate<Thing>)((Thing x) => map.reservationManager.CanReserve(GetPawn, LocalTargetInfo.op_Implicit(x), 1, -1, (ReservationLayerDef)null, false)));
								if (thingToLoad != null)
								{
									TaggedString val = Translator.Translate("Load") + " " + ((Def)thingToLoad.def).label;
									list.Add(new FloatMenuOption(TaggedString.op_Implicit(val), (Action)delegate
									{
										TryGiveLoadSlotJob(thingToLoad);
									}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 29f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
								}
								else
								{
									FloatMenuOption val2 = new FloatMenuOption($"{((Def)item).label} unavailable", (Action)delegate
									{
									}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
									val2.Disabled = true;
									list.Add(val2);
								}
							}
						}
						else
						{
							FloatMenuOption val3 = new FloatMenuOption("No load options available.", (Action)delegate
							{
							}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
							val3.Disabled = true;
							list.Add(val3);
						}
					}
				}
			}
			if (!slot.IsEmpty())
			{
				string text = $"Unload {((Entity)slot.SlotOccupant).Label}";
				list.Add(new FloatMenuOption(text, (Action)delegate
				{
					TryEmptySlot(slot);
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 29f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
			}
			Find.WindowStack.Add((Window)new FloatMenu(list));
		}

		public virtual void TryEmptySlot(SlotLoadable slot)
		{
			slot.TryEmptySlot();
		}

		[IteratorStateMachine(typeof(<EquippedGizmos>d__26))]
		public virtual IEnumerable<Gizmo> EquippedGizmos()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <EquippedGizmos>d__26(-2)
			{
				<>4__this = this
			};
		}

		public virtual string SlotDesc(SlotLoadable slot)
		{
			StringBuilder stringBuilder = new StringBuilder();
			stringBuilder.AppendLine(((Def)((Thing)slot).def).description);
			if (!slot.IsEmpty())
			{
				stringBuilder.AppendLine();
				stringBuilder.AppendLine($"Loaded {((Entity)slot.SlotOccupant).LabelCap}");
			}
			return stringBuilder.ToString();
		}

		public override void PostExposeData()
		{
			Scribe_Values.Look<bool>(ref isInitialized, "isInitialized", false, false);
			Scribe_Values.Look<bool>(ref isGathering, "isGathering", false, false);
			Scribe_Collections.Look<SlotLoadable>(ref slots, "slots", (LookMode)2, Array.Empty<object>());
			((ThingComp)this).PostExposeData();
			if (slots == null)
			{
				slots = new List<SlotLoadable>();
			}
		}
	}
	[HarmonyPatch(typeof(MainTabWindow_Architect), "CacheDesPanels")]
	public static class Patch_MainTabWindow_Architect_CacheDesPanels
	{
		[HarmonyPostfix]
		public static void Postfix(MainTabWindow_Architect __instance)
		{
			List<ArchitectCategoryTab> list = new List<ArchitectCategoryTab>();
			foreach (ArchitectCategoryTab item in __instance.desPanelsCached)
			{
				if (((Def)item.def).HasModExtension<DefModExt_HideArchitectTab>())
				{
					list.Add(item);
				}
			}
			foreach (ArchitectCategoryTab item2 in list)
			{
				__instance.desPanelsCached.Remove(item2);
			}
		}
	}
	public class JobDriver_GatherSlotItem : JobDriver
	{
		[CompilerGenerated]
		private sealed class <MakeNewToils>d__1 : IEnumerable<Toil>, IEnumerable, IEnumerator<Toil>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Toil <>2__current;

			private int <>l__initialThreadId;

			public JobDriver_GatherSlotItem <>4__this;

			Toil IEnumerator<Toil>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <MakeNewToils>d__1(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				<>1__state = -2;
			}

			[DebuggerHidden]
			private bool MoveNext()
			{
				//IL_004d: Unknown result type (might be due to invalid IL or missing references)
				//IL_0052: Unknown result type (might be due to invalid IL or missing references)
				//IL_0064: Unknown result type (might be due to invalid IL or missing references)
				//IL_0066: Unknown result type (might be due to invalid IL or missing references)
				//IL_006c: Expected O, but got Unknown
				//IL_008c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0091: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
				//IL_00af: Expected O, but got Unknown
				int num = <>1__state;
				JobDriver_GatherSlotItem CS$<>8__locals6 = <>4__this;
				switch (num)
				{
				default:
					return false;
				case 0:
					<>1__state = -1;
					<>2__current = Toils_Reserve.Reserve((TargetIndex)1, 1, -1, (ReservationLayerDef)null, false);
					<>1__state = 1;
					return true;
				case 1:
				{
					<>1__state = -1;
					Toil val = new Toil
					{
						initAction = delegate
						{
							//IL_0011: Unknown result type (might be due to invalid IL or missing references)
							((JobDriver)CS$<>8__locals6).pawn.pather.StartPath(LocalTargetInfo.op_Implicit(((JobDriver)CS$<>8__locals6).TargetThingA), (PathEndMode)3);
						},
						defaultCompleteMode = (ToilCompleteMode)2
					};
					ToilFailConditions.FailOnDespawnedNullOrForbidden<Toil>(val, (TargetIndex)1);
					<>2__current = val;
					<>1__state = 2;
					return true;
				}
				case 2:
					<>1__state = -1;
					<>2__current = new Toil
					{
						initAction = delegate
						{
							//IL_0079: Unknown result type (might be due to invalid IL or missing references)
							//IL_008a: Unknown result type (might be due to invalid IL or missing references)
							//IL_008f: Unknown result type (might be due to invalid IL or missing references)
							Thing thing = ((LocalTargetInfo)(ref ((JobDriver)CS$<>8__locals6).job.targetA)).Thing;
							if (thing.def.stackLimit > 1 && thing.stackCount > 1)
							{
								thing.SplitOff(1);
							}
							Pawn_EquipmentTracker equipment = ((JobDriver)CS$<>8__locals6).pawn.equipment;
							if (equipment != null)
							{
								ThingWithComps primary = equipment.Primary;
								if (primary != null)
								{
									Comp_SlotLoadable comp = primary.GetComp<Comp_SlotLoadable>();
									if (comp != null)
									{
										comp.TryLoadSlot(thing);
										if (((Thing)primary).def.soundInteract != null)
										{
											SoundStarter.PlayOneShot(((Thing)primary).def.soundInteract, SoundInfo.op_Implicit(new TargetInfo(((Thing)((JobDriver)CS$<>8__locals6).pawn).Position, ((Thing)((JobDriver)CS$<>8__locals6).pawn).Map, false)));
										}
									}
								}
							}
						},
						defaultCompleteMode = (ToilCompleteMode)1
					};
					<>1__state = 3;
					return true;
				case 3:
					<>1__state = -1;
					return false;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Toil> IEnumerable<Toil>.GetEnumerator()
			{
				<MakeNewToils>d__1 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <MakeNewToils>d__1(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Toil>)this).GetEnumerator();
			}
		}

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return true;
		}

		[IteratorStateMachine(typeof(<MakeNewToils>d__1))]
		[DebuggerHidden]
		public override IEnumerable<Toil> MakeNewToils()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <MakeNewToils>d__1(-2)
			{
				<>4__this = this
			};
		}
	}
	public class DefModExt_HideArchitectTab : DefModExtension
	{
	}
	public class DefModExt_FurDef : DefModExtension
	{
		public bool useSkinColorForFur;

		public bool useMaskForFur;
	}
	[StaticConstructorOnStartup]
	public static class SubcategoryUtil
	{
		public const string orderCat = "Orders";

		public const string uncatCat = "Uncategorized";

		public const float gizmoScale = 75f;

		public const float gizmoMargin = 6f;

		public const float sectionBorder = 10f;

		public const float scrollWidth = 16f;

		public static float orderGizmoScale = (TabulaRasaMod.settings.enableShrunkOrders ? 49.500004f : 75f);

		public static Dictionary<ArchitectCategoryTab, string> currentCatForTab = new Dictionary<ArchitectCategoryTab, string>();

		public static Dictionary<ArchitectCategoryTab, Vector2> scrollPositionForTab;

		public static Dictionary<ArchitectCategoryTab, Vector2> gizmoScrollPositionForTab;

		public static Dictionary<ArchitectCategoryTab, Vector2> nbdScrollPositionForTab;

		public static Dictionary<ArchitectCategoryTab, List<ArchitectSubCatDesignators>> designatorsForTab;

		public static void PopulateArchitectCategoryTab(ArchitectCategoryTab tab)
		{
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_0103: Unknown result type (might be due to invalid IL or missing references)
			//IL_011a: Unknown result type (might be due to invalid IL or missing references)
			//IL_013b: Unknown result type (might be due to invalid IL or missing references)
			if (GenDictionary.NullOrEmpty<ArchitectCategoryTab, List<ArchitectSubCatDesignators>>(designatorsForTab))
			{
				designatorsForTab = new Dictionary<ArchitectCategoryTab, List<ArchitectSubCatDesignators>>();
			}
			if (!designatorsForTab.ContainsKey(tab))
			{
				Dictionary<string, List<Designator>> dictionary = new Dictionary<string, List<Designator>>();
				foreach (Designator resolvedAllowedDesignator in tab.def.ResolvedAllowedDesignators)
				{
					if (resolvedAllowedDesignator is Designator_Build)
					{
						DefModExt_SubcategoryDisplay modExtension = ((Def)((Designator_Place)(Designator_Build)resolvedAllowedDesignator).PlacingDef).GetModExtension<DefModExt_SubcategoryDisplay>();
						if (modExtension != null)
						{
							foreach (string subcategory in modExtension.subcategories)
							{
								if (!dictionary.ContainsKey(subcategory))
								{
									dictionary.Add(subcategory, new List<Designator>());
								}
								dictionary[subcategory].Add(resolvedAllowedDesignator);
							}
						}
						else
						{
							if (!dictionary.ContainsKey("Uncategorized"))
							{
								dictionary.Add("Uncategorized", new List<Designator>());
							}
							dictionary["Uncategorized"].Add(resolvedAllowedDesignator);
						}
					}
					else if (resolvedAllowedDesignator is Designator_Dropdown)
					{
						Designator activeDesignator = ((Designator_Dropdown)resolvedAllowedDesignator).activeDesignator;
						DefModExt_SubcategoryDisplay modExtension2;
						if (activeDesignator is Designator_Build)
						{
							modExtension2 = ((Def)((Designator_Place)(Designator_Build)activeDesignator).PlacingDef).GetModExtension<DefModExt_SubcategoryDisplay>();
						}
						else
						{
							if (!(activeDesignator is Designator_Place))
							{
								continue;
							}
							modExtension2 = ((Def)((Designator_Place)activeDesignator).PlacingDef).GetModExtension<DefModExt_SubcategoryDisplay>();
						}
						if (modExtension2 != null)
						{
							foreach (string subcategory2 in modExtension2.subcategories)
							{
								if (!dictionary.ContainsKey(subcategory2))
								{
									dictionary.Add(subcategory2, new List<Designator>());
								}
								dictionary[subcategory2].Add(resolvedAllowedDesignator);
							}
						}
						else
						{
							if (!dictionary.ContainsKey("Uncategorized"))
							{
								dictionary.Add("Uncategorized", new List<Designator>());
							}
							dictionary["Uncategorized"].Add(resolvedAllowedDesignator);
						}
					}
					else
					{
						if (!dictionary.ContainsKey("Orders"))
						{
							dictionary.Add("Orders", new List<Designator>());
						}
						dictionary["Orders"].Add(resolvedAllowedDesignator);
					}
				}
				List<ArchitectSubCatDesignators> list = new List<ArchitectSubCatDesignators>();
				foreach (KeyValuePair<string, List<Designator>> item in dictionary)
				{
					list.Add(new ArchitectSubCatDesignators
					{
						category = item.Key,
						designators = item.Value
					});
				}
				designatorsForTab.Add(tab, list);
			}
			PopulateTabLists(tab);
		}

		public static void PopulateTabLists(ArchitectCategoryTab tab)
		{
			//IL_005a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			//IL_0091: Unknown result type (might be due to invalid IL or missing references)
			//IL_0097: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
			if (GenDictionary.NullOrEmpty<ArchitectCategoryTab, string>(currentCatForTab))
			{
				currentCatForTab = new Dictionary<ArchitectCategoryTab, string>();
			}
			if (!currentCatForTab.ContainsKey(tab))
			{
				currentCatForTab.Add(tab, null);
			}
			if (GenDictionary.NullOrEmpty<ArchitectCategoryTab, Vector2>(gizmoScrollPositionForTab))
			{
				gizmoScrollPositionForTab = new Dictionary<ArchitectCategoryTab, Vector2>();
			}
			if (!gizmoScrollPositionForTab.ContainsKey(tab))
			{
				gizmoScrollPositionForTab.Add(tab, default(Vector2));
			}
			if (GenDictionary.NullOrEmpty<ArchitectCategoryTab, Vector2>(nbdScrollPositionForTab))
			{
				nbdScrollPositionForTab = new Dictionary<ArchitectCategoryTab, Vector2>();
			}
			if (!nbdScrollPositionForTab.ContainsKey(tab))
			{
				nbdScrollPositionForTab.Add(tab, default(Vector2));
			}
			if (GenDictionary.NullOrEmpty<ArchitectCategoryTab, Vector2>(scrollPositionForTab))
			{
				scrollPositionForTab = new Dictionary<ArchitectCategoryTab, Vector2>();
			}
			if (!scrollPositionForTab.ContainsKey(tab))
			{
				scrollPositionForTab.Add(tab, default(Vector2));
			}
		}

		public static void DrawSubcategoryWindow(ArchitectCategoryTab tab, Designator forceActivatedCommand)
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_007a: Unknown result type (might be due to invalid IL or missing references)
			//IL_02c4: Unknown result type (might be due to invalid IL or missing references)
			//IL_0288: Unknown result type (might be due to invalid IL or missing references)
			//IL_033e: Unknown result type (might be due to invalid IL or missing references)
			//IL_034f: Unknown result type (might be due to invalid IL or missing references)
			//IL_030a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0356: Unknown result type (might be due to invalid IL or missing references)
			float num = (float)UI.screenWidth - 180f - ((MainTabWindow)(MainTabWindow_Architect)MainButtonDefOf.Architect.TabWindow).RequestedTabSize.x;
			float num2 = 81f * TabulaRasaMod.settings.gizmoRowHeight + 24f + 10f;
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(((MainTabWindow)(MainTabWindow_Architect)MainButtonDefOf.Architect.TabWindow).RequestedTabSize.x + 10f, (float)UI.screenHeight - num2 - 45f, num, num2);
			Widgets.DrawWindowBackground(val);
			Text.Font = (GameFont)1;
			bool flag = GenCollection.Any<ArchitectSubCatDesignators>(designatorsForTab[tab], (Predicate<ArchitectSubCatDesignators>)((ArchitectSubCatDesignators c) => c.Visible && c.category != "Uncategorized"));
			bool flag2 = !flag && designatorsForTab[tab].Find((ArchitectSubCatDesignators c) => c.category == "Uncategorized") == null;
			float num3 = (flag ? 216f : 0f);
			Rect rect = default(Rect);
			((Rect)(ref rect))..ctor(((Rect)(ref val)).x, ((Rect)(ref val)).y, num3, ((Rect)(ref val)).height);
			List<Designator> list = ((!GenCollection.Any<ArchitectSubCatDesignators>(designatorsForTab[tab], (Predicate<ArchitectSubCatDesignators>)((ArchitectSubCatDesignators sc) => sc.category == "Orders"))) ? new List<Designator>() : designatorsForTab[tab].Find((ArchitectSubCatDesignators sc) => sc.category == "Orders").designators);
			float num4 = ((!GenList.NullOrEmpty<Designator>((IList<Designator>)list) && !flag2) ? ((TabulaRasaMod.settings.enableShrunkOrders ? (orderGizmoScale * 2f) : orderGizmoScale) + 10f + 16f + 12f) : 0f);
			float num5 = ((Rect)(ref val)).width - ((Rect)(ref rect)).width - num4;
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(((Rect)(ref rect)).xMax, ((Rect)(ref val)).y, num5, ((Rect)(ref val)).height);
			if (!flag2 && GenText.NullOrEmpty(currentCatForTab[tab]))
			{
				currentCatForTab[tab] = (from d in designatorsForTab[tab]
					orderby d.category
					where d.category != "Orders"
					select d).First().category;
			}
			if (flag)
			{
				DrawSubcategoryList(rect, tab, designatorsForTab[tab].OrderBy((ArchitectSubCatDesignators d) => d.category).ToList());
			}
			Designator val3 = DrawMainDesignators(val2, forceActivatedCommand, tab, GetDesignatorsForShow(tab, flag2));
			if (!GenList.NullOrEmpty<Designator>((IList<Designator>)list) && !flag2)
			{
				Designator val4 = DrawOrderDesignators(new Rect(((Rect)(ref val)).xMax - num4 - 5f, ((Rect)(ref val)).y, num4 - 5f, ((Rect)(ref val)).height), tab, list);
				if (val4 != null)
				{
					val3 = val4;
				}
			}
			if (val3 == null && Find.DesignatorManager.SelectedDesignator != null)
			{
				val3 = Find.DesignatorManager.SelectedDesignator;
			}
			tab.DoInfoBox(ArchitectCategoryTab.InfoRect, val3);
			if ((int)Event.current.type == 0 && Mouse.IsOver(val2))
			{
				Event.current.Use();
			}
		}

		public static void DrawSubcategoryList(Rect rect, ArchitectCategoryTab tab, List<ArchitectSubCatDesignators> subcategories)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0069: Unknown result type (might be due to invalid IL or missing references)
			//IL_006e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0070: Unknown result type (might be due to invalid IL or missing references)
			//IL_0071: Unknown result type (might be due to invalid IL or missing references)
			//IL_0079: Unknown result type (might be due to invalid IL or missing references)
			//IL_007c: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
			//IL_0119: Unknown result type (might be due to invalid IL or missing references)
			//IL_0136: Unknown result type (might be due to invalid IL or missing references)
			//IL_017f: Unknown result type (might be due to invalid IL or missing references)
			Rect val = GenUI.ContractedBy(rect, 10f);
			float num = subcategories.Where((ArchitectSubCatDesignators s) => s.Visible).Count();
			float num2 = 35f;
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(((Rect)(ref val)).x, ((Rect)(ref val)).y, ((Rect)(ref val)).width - 16f, num * num2);
			Vector2 scrollPosition = scrollPositionForTab[tab];
			CaptureScrolling(val, val2, ref scrollPosition);
			Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
			float num3 = ((Rect)(ref val2)).y;
			Rect val3 = default(Rect);
			foreach (ArchitectSubCatDesignators subcategory in subcategories)
			{
				if (subcategory.Visible)
				{
					((Rect)(ref val3))..ctor(((Rect)(ref val2)).x, num3, ((Rect)(ref val2)).width, num2 - 3f);
					DrawCategoryBackground(val3, currentCatForTab[tab] == subcategory.category);
					MouseoverSounds.DoRegion(val3);
					Rect val4 = new Rect(((Rect)(ref val3)).x + 8f, ((Rect)(ref val3)).y, ((Rect)(ref val3)).width - 8f, ((Rect)(ref val3)).height);
					Text.Anchor = (TextAnchor)3;
					Widgets.Label(val4, subcategory.category);
					Text.Anchor = (TextAnchor)0;
					if (Widgets.ButtonInvisible(val3, true))
					{
						currentCatForTab[tab] = subcategory.category;
					}
					num3 += num2;
				}
			}
			Widgets.EndScrollView();
			scrollPositionForTab[tab] = scrollPosition;
		}

		public static Designator DrawMainDesignators(Rect rect, Designator forceActivatedCommand, ArchitectCategoryTab tab, List<Designator> visibleDesignators)
		{
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			//IL_0028: Unknown result type (might be due to invalid IL or missing references)
			//IL_0084: Unknown result type (might be due to invalid IL or missing references)
			//IL_0085: Unknown result type (might be due to invalid IL or missing references)
			//IL_008e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0091: Unknown result type (might be due to invalid IL or missing references)
			//IL_0107: Unknown result type (might be due to invalid IL or missing references)
			if (currentCatForTab == null || GenList.NullOrEmpty<Designator>((IList<Designator>)visibleDesignators))
			{
				return null;
			}
			Vector2 scrollPosition = gizmoScrollPositionForTab[tab];
			Rect val = GenUI.ContractedBy(rect, 10f);
			float num = 86f;
			float num2 = Mathf.FloorToInt((((Rect)(ref val)).width - 16f) / 81f);
			float num3 = Mathf.CeilToInt((float)visibleDesignators.Count() / num2);
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(((Rect)(ref val)).x, ((Rect)(ref val)).y, ((Rect)(ref val)).width - 16f, num3 * num);
			CaptureScrolling(val, val2, ref scrollPosition);
			Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
			Designator mouseoverGizmo = null;
			for (int i = 0; i < visibleDesignators.Count(); i++)
			{
				float num4 = Mathf.FloorToInt((float)i / num2);
				float num5 = Mathf.FloorToInt((float)i % num2);
				float curX = ((Rect)(ref val2)).x + num5 * 81f;
				float curY = ((Rect)(ref val2)).y + num4 * num;
				DrawGizmo(curX, curY, visibleDesignators[i], ref mouseoverGizmo);
			}
			Widgets.EndScrollView();
			gizmoScrollPositionForTab[tab] = scrollPosition;
			return mouseoverGizmo;
		}

		public static Designator DrawOrderDesignators(Rect rect, ArchitectCategoryTab tab, List<Designator> designators)
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0086: Unknown result type (might be due to invalid IL or missing references)
			//IL_0087: Unknown result type (might be due to invalid IL or missing references)
			//IL_0090: Unknown result type (might be due to invalid IL or missing references)
			//IL_0093: Unknown result type (might be due to invalid IL or missing references)
			//IL_0135: Unknown result type (might be due to invalid IL or missing references)
			Vector2 scrollPosition = nbdScrollPositionForTab[tab];
			Rect val = GenUI.ContractedBy(rect, 0f, 10f);
			float num = Mathf.FloorToInt((((Rect)(ref val)).width - 16f) / (orderGizmoScale + 6f));
			float num2 = orderGizmoScale + 6f + 5f;
			float num3 = Mathf.CeilToInt((float)designators.Count() / num);
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(((Rect)(ref val)).x, ((Rect)(ref val)).y, ((Rect)(ref val)).width - 16f, num3 * num2);
			CaptureScrolling(val, val2, ref scrollPosition);
			Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
			Designator mouseoverGizmo = null;
			for (int i = 0; i < designators.Count; i++)
			{
				float num4 = Mathf.FloorToInt((float)i / num);
				float num5 = Mathf.FloorToInt((float)i % num);
				float curX = ((Rect)(ref val2)).x + num5 * (orderGizmoScale + 6f);
				float curY = ((Rect)(ref val2)).y + num4 * num2;
				if (TabulaRasaMod.settings.enableShrunkOrders)
				{
					DrawOrderGizmo(curX, curY, designators[i], ref mouseoverGizmo);
				}
				else
				{
					DrawGizmo(curX, curY, designators[i], ref mouseoverGizmo);
				}
			}
			Widgets.EndScrollView();
			nbdScrollPositionForTab[tab] = scrollPosition;
			return mouseoverGizmo;
		}

		public static List<Designator> GetDesignatorsForShow(ArchitectCategoryTab tab, bool showOnlyOrders)
		{
			ArchitectSubCatDesignators architectSubCatDesignators = designatorsForTab[tab].Find((ArchitectSubCatDesignators sc) => sc.category == currentCatForTab[tab]) ?? null;
			if (showOnlyOrders)
			{
				ArchitectSubCatDesignators architectSubCatDesignators2 = designatorsForTab[tab].Find((ArchitectSubCatDesignators sc) => sc.category == "Orders") ?? null;
				if (architectSubCatDesignators2 != null)
				{
					return architectSubCatDesignators2.designators.Where((Designator d) => ((Gizmo)d).Visible).ToList();
				}
				return new List<Designator>();
			}
			if (architectSubCatDesignators != null)
			{
				return architectSubCatDesignators.designators.Where((Designator d) => ((Gizmo)d).Visible).ToList();
			}
			return new List<Designator>();
		}

		public static void DrawOrderGizmo(float curX, float curY, Designator designator, ref Designator mouseoverGizmo)
		{
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Invalid comparison between Unknown and I4
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Invalid comparison between Unknown and I4
			//IL_004a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Invalid comparison between Unknown and I4
			//IL_009d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a7: Expected O, but got Unknown
			Rect butRect = default(Rect);
			((Rect)(ref butRect))..ctor(curX, curY, orderGizmoScale, orderGizmoScale);
			GizmoResult val = designator.OrderGizmoOnGUI(butRect, default(GizmoRenderParms));
			if ((int)((GizmoResult)(ref val)).State >= 1)
			{
				mouseoverGizmo = designator;
			}
			if ((int)((GizmoResult)(ref val)).State == 2)
			{
				((Gizmo)designator).ProcessInput(((GizmoResult)(ref val)).InteractEvent);
			}
			if ((int)((GizmoResult)(ref val)).State != 3)
			{
				return;
			}
			List<FloatMenuOption> list = new List<FloatMenuOption>();
			foreach (FloatMenuOption rightClickFloatMenuOption in ((Gizmo)designator).RightClickFloatMenuOptions)
			{
				list.Add(rightClickFloatMenuOption);
			}
			if (GenCollection.Any<FloatMenuOption>(list))
			{
				Find.WindowStack.Add((Window)new FloatMenu(list));
			}
		}

		public static GizmoResult OrderGizmoOnGUI(this Designator designator, Rect butRect, GizmoRenderParms parms)
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			//IL_0031: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_0063: Unknown result type (might be due to invalid IL or missing references)
			//IL_0074: Unknown result type (might be due to invalid IL or missing references)
			//IL_007f: Unknown result type (might be due to invalid IL or missing references)
			//IL_007c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0089: Unknown result type (might be due to invalid IL or missing references)
			//IL_008a: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
			//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
			//IL_0100: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
			//IL_0105: Unknown result type (might be due to invalid IL or missing references)
			//IL_0110: Unknown result type (might be due to invalid IL or missing references)
			//IL_011f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0145: Unknown result type (might be due to invalid IL or missing references)
			//IL_019f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0168: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a7: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a9: Unknown result type (might be due to invalid IL or missing references)
			//IL_0205: Unknown result type (might be due to invalid IL or missing references)
			//IL_01b2: Unknown result type (might be due to invalid IL or missing references)
			//IL_0210: Unknown result type (might be due to invalid IL or missing references)
			//IL_01bb: Unknown result type (might be due to invalid IL or missing references)
			//IL_01bd: Unknown result type (might be due to invalid IL or missing references)
			//IL_01ce: Unknown result type (might be due to invalid IL or missing references)
			//IL_02c0: Unknown result type (might be due to invalid IL or missing references)
			//IL_02b6: Unknown result type (might be due to invalid IL or missing references)
			//IL_0231: Unknown result type (might be due to invalid IL or missing references)
			//IL_0236: Unknown result type (might be due to invalid IL or missing references)
			//IL_0241: Unknown result type (might be due to invalid IL or missing references)
			//IL_025c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0263: Unknown result type (might be due to invalid IL or missing references)
			//IL_026f: Unknown result type (might be due to invalid IL or missing references)
			//IL_029d: Unknown result type (might be due to invalid IL or missing references)
			//IL_02dc: Unknown result type (might be due to invalid IL or missing references)
			//IL_02e1: Unknown result type (might be due to invalid IL or missing references)
			//IL_0387: Unknown result type (might be due to invalid IL or missing references)
			//IL_037f: Unknown result type (might be due to invalid IL or missing references)
			//IL_034f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0350: Unknown result type (might be due to invalid IL or missing references)
			//IL_044e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0446: Unknown result type (might be due to invalid IL or missing references)
			//IL_030b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0310: Unknown result type (might be due to invalid IL or missing references)
			//IL_031a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0325: Unknown result type (might be due to invalid IL or missing references)
			//IL_032a: Unknown result type (might be due to invalid IL or missing references)
			//IL_040d: Unknown result type (might be due to invalid IL or missing references)
			//IL_03e5: Unknown result type (might be due to invalid IL or missing references)
			//IL_03b9: Unknown result type (might be due to invalid IL or missing references)
			//IL_03c3: Unknown result type (might be due to invalid IL or missing references)
			//IL_03ce: Unknown result type (might be due to invalid IL or missing references)
			//IL_0434: Unknown result type (might be due to invalid IL or missing references)
			//IL_041b: Unknown result type (might be due to invalid IL or missing references)
			//IL_043e: Unknown result type (might be due to invalid IL or missing references)
			Text.Font = (GameFont)0;
			Color val = Color.white;
			bool flag = false;
			if (Mouse.IsOver(butRect))
			{
				flag = true;
				if (!((Gizmo)designator).disabled)
				{
					val = GenUI.MouseoverColor;
				}
			}
			MouseoverSounds.DoRegion(butRect, SoundDefOf.Mouseover_Command);
			if (parms.highLight)
			{
				Widgets.DrawStrongHighlight(GenUI.ExpandedBy(butRect, 4f), (Color?)null);
			}
			if (((Gizmo)designator).disabled)
			{
				parms.lowLight = true;
			}
			Material val2 = (parms.lowLight ? TexUI.GrayscaleGUI : null);
			GUI.color = (parms.lowLight ? Command.LowLightBgColor : val);
			GenUI.DrawTextureWithMaterial(butRect, (Texture)(object)(parms.shrunk ? ((Command)designator).BGTextureShrunk : ((Command)designator).BGTexture), val2, default(Rect));
			GUI.color = val;
			((Command)designator).DrawIcon(butRect, val2, parms);
			bool flag2 = false;
			GUI.color = Color.white;
			if (parms.lowLight)
			{
				GUI.color = Command.LowLightLabelColor;
			}
			Vector2 val3 = (parms.shrunk ? new Vector2(3f, 0f) : new Vector2(5f, 3f));
			Rect val4 = default(Rect);
			((Rect)(ref val4))..ctor(((Rect)(ref butRect)).x + val3.x, ((Rect)(ref butRect)).y + val3.y, ((Rect)(ref butRect)).width - 10f, Text.LineHeight);
			if (SteamDeck.IsSteamDeckInNonKeyboardMode)
			{
				if (parms.isFirst)
				{
					GUI.DrawTexture(new Rect(((Rect)(ref val4)).x, ((Rect)(ref val4)).y, 21f, 21f), (Texture)(object)TexUI.SteamDeck_ButtonA);
					if (KeyBindingDefOf.Accept.KeyDownEvent)
					{
						flag2 = true;
						Event.current.Use();
					}
				}
			}
			else
			{
				KeyCode val5 = (KeyCode)((((Command)designator).hotKey != null) ? ((int)((Command)designator).hotKey.MainKey) : 0);
				if ((int)val5 != 0 && !GizmoGridDrawer.drawnHotKeys.Contains(val5))
				{
					Widgets.Label(val4, GenText.ToStringReadable(val5));
					GizmoGridDrawer.drawnHotKeys.Add(val5);
					if (((Command)designator).hotKey.KeyDownEvent)
					{
						flag2 = true;
						Event.current.Use();
					}
				}
			}
			if (GizmoGridDrawer.customActivator != null && GizmoGridDrawer.customActivator((Gizmo)(object)designator))
			{
				flag2 = true;
			}
			if (Widgets.ButtonInvisible(butRect, true))
			{
				flag2 = true;
			}
			if (!parms.shrunk)
			{
				string topRightLabel = ((Command)designator).TopRightLabel;
				if (!GenText.NullOrEmpty(topRightLabel))
				{
					Vector2 val6 = Text.CalcSize(topRightLabel);
					Rect val7 = default(Rect);
					((Rect)(ref val7))..ctor(((Rect)(ref butRect)).xMax - val6.x - 2f, ((Rect)(ref butRect)).y + 3f, val6.x, val6.y);
					Rect val8 = val7;
					((Rect)(ref val7)).x = ((Rect)(ref val7)).x - 2f;
					((Rect)(ref val7)).width = ((Rect)(ref val7)).width + 3f;
					Text.Anchor = (TextAnchor)2;
					GUI.DrawTexture(val7, (Texture)(object)TexUI.GrayTextBG);
					Widgets.Label(val8, topRightLabel);
					Text.Anchor = (TextAnchor)0;
				}
				GUI.color = Color.white;
			}
			if (Mouse.IsOver(butRect) && ((Command)designator).DoTooltip)
			{
				TipSignal val9 = TipSignal.op_Implicit(((Command)designator).Desc);
				if (((Gizmo)designator).disabled && !GenText.NullOrEmpty(((Gizmo)designator).disabledReason))
				{
					val9.text += ColoredText.Colorize("\n\n" + Translator.Translate("DisabledCommand") + ": " + ((Gizmo)designator).disabledReason, ColorLibrary.RedReadable);
				}
				val9.text += ((Command)designator).DescPostfix;
				TooltipHandler.TipRegion(butRect, val9);
			}
			if (!GenText.NullOrEmpty(((Command)designator).HighlightTag) && (Find.WindowStack.FloatMenu == null || !((Rect)(ref ((Window)Find.WindowStack.FloatMenu).windowRect)).Overlaps(butRect)))
			{
				UIHighlighter.HighlightOpportunity(butRect, ((Command)designator).HighlightTag);
			}
			Text.Font = (GameFont)1;
			if (flag2)
			{
				if (((Gizmo)designator).disabled)
				{
					if (!GenText.NullOrEmpty(((Gizmo)designator).disabledReason))
					{
						Messages.Message(TaggedString.op_Implicit(Translator.Translate("DisabledCommand") + ": " + ((Gizmo)designator).disabledReason), MessageTypeDefOf.RejectInput, false);
					}
					return new GizmoResult((GizmoState)1, (Event)null);
				}
				GizmoResult result = default(GizmoResult);
				if (Event.current.button == 1)
				{
					((GizmoResult)(ref result))..ctor((GizmoState)3, Event.current);
				}
				else
				{
					if (!TutorSystem.AllowAction(EventPack.op_Implicit(((Command)designator).TutorTagSelect)))
					{
						return new GizmoResult((GizmoState)1, (Event)null);
					}
					((GizmoResult)(ref result))..ctor((GizmoState)2, Event.current);
					TutorSystem.Notify_Event(EventPack.op_Implicit(((Command)designator).TutorTagSelect));
				}
				return result;
			}
			if (flag)
			{
				return new GizmoResult((GizmoState)1, (Event)null);
			}
			return new GizmoResult((GizmoState)0, (Event)null);
		}

		public static void DrawGizmo(float curX, float curY, Designator designator, ref Designator mouseoverGizmo)
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_0028: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Unknown result type (might be due to invalid IL or missing references)
			//IL_002e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0031: Unknown result type (might be due to invalid IL or missing references)
			//IL_0037: Invalid comparison between Unknown and I4
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0044: Invalid comparison between Unknown and I4
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Invalid comparison between Unknown and I4
			//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b2: Expected O, but got Unknown
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(curX, curY, 75f, 75f);
			GizmoResult val2 = ((Gizmo)designator).GizmoOnGUI(((Rect)(ref val)).position, 75f, default(GizmoRenderParms));
			if ((int)((GizmoResult)(ref val2)).State >= 1)
			{
				mouseoverGizmo = designator;
			}
			if ((int)((GizmoResult)(ref val2)).State == 2)
			{
				((Gizmo)designator).ProcessInput(((GizmoResult)(ref val2)).InteractEvent);
			}
			if ((int)((GizmoResult)(ref val2)).State != 3)
			{
				return;
			}
			List<FloatMenuOption> list = new List<FloatMenuOption>();
			foreach (FloatMenuOption rightClickFloatMenuOption in ((Gizmo)designator).RightClickFloatMenuOptions)
			{
				list.Add(rightClickFloatMenuOption);
			}
			if (GenCollection.Any<FloatMenuOption>(list))
			{
				Find.WindowStack.Add((Window)new FloatMenu(list));
			}
		}

		public static void CaptureScrolling(Rect outRect, Rect viewRect, ref Vector2 scrollPosition)
		{
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Invalid comparison between Unknown and I4
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			if ((int)Event.current.type == 6 && Mouse.IsOver(outRect))
			{
				scrollPosition.y += Event.current.delta.y * 20f;
				float num = 0f;
				float num2 = ((Rect)(ref viewRect)).height - ((Rect)(ref outRect)).height;
				if (scrollPosition.y < num)
				{
					scrollPosition.y = num;
				}
				if (scrollPosition.y > num2)
				{
					scrollPosition.y = num2;
				}
				Event.current.Use();
			}
		}

		public static void DrawCategoryBackground(Rect rect, bool selected)
		{
			//IL_0036: Unknown result type (might be due to invalid IL or missing references)
			//IL_0003: Unknown result type (might be due to invalid IL or missing references)
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			if (selected)
			{
				GUI.color = Widgets.OptionSelectedBGFillColor;
				GUI.DrawTexture(rect, (Texture)(object)Texture2D.whiteTexture);
				GUI.color = Widgets.OptionSelectedBGBorderColor;
				Widgets.DrawBox(rect, 1, (Texture2D)null);
				GUI.color = Color.white;
			}
			else
			{
				Widgets.DrawOptionUnselected(rect);
			}
			Widgets.DrawHighlightIfMouseover(rect);
		}
	}
	public class WorldDrawLayer_UngeneratedPlanetPartsAsDefaultBiome : WorldDrawLayer
	{
		[CompilerGenerated]
		private sealed class <Regenerate>d__0 : IEnumerable<object>, IEnumerable, IEnumerator<object>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private object <>2__current;

			private int <>l__initialThreadId;

			public WorldDrawLayer_UngeneratedPlanetPartsAsDefaultBiome <>4__this;

			private IEnumerator <>7__wrap1;

			object IEnumerator<object>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <Regenerate>d__0(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>7__wrap1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_0089: Unknown result type (might be due to invalid IL or missing references)
				//IL_008e: Unknown result type (might be due to invalid IL or missing references)
				//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
				//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
				try
				{
					int num = <>1__state;
					WorldDrawLayer_UngeneratedPlanetPartsAsDefaultBiome worldDrawLayer_UngeneratedPlanetPartsAsDefaultBiome = <>4__this;
					switch (num)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<>7__wrap1 = worldDrawLayer_UngeneratedPlanetPartsAsDefaultBiome.<>n__0().GetEnumerator();
						<>1__state = -3;
						break;
					case 1:
						<>1__state = -3;
						break;
					}
					if (<>7__wrap1.MoveNext())
					{
						object current = <>7__wrap1.Current;
						<>2__current = current;
						<>1__state = 1;
						return true;
					}
					<>m__Finally1();
					<>7__wrap1 = null;
					Vector3 viewCenter = ((WorldDrawLayer)worldDrawLayer_UngeneratedPlanetPartsAsDefaultBiome).planetLayer.ViewCenter;
					float viewAngle = ((WorldDrawLayer)worldDrawLayer_UngeneratedPlanetPartsAsDefaultBiome).planetLayer.ViewAngle;
					if (viewAngle < 180f)
					{
						List<Vector3> collection = default(List<Vector3>);
						List<int> collection2 = default(List<int>);
						SphereGenerator.Generate(4, ((WorldDrawLayer)worldDrawLayer_UngeneratedPlanetPartsAsDefaultBiome).planetLayer.Radius + -0.16f, -viewCenter, 180f - Mathf.Min(viewAngle, 180f) + 10f, ref collection, ref collection2);
						LayerSubMesh subMesh = ((WorldDrawLayerBase)worldDrawLayer_UngeneratedPlanetPartsAsDefaultBiome).GetSubMesh(((WorldDrawLayer)worldDrawLayer_UngeneratedPlanetPartsAsDefaultBiome).planetLayer.Def.DefaultBiome.DrawMaterial);
						subMesh.verts.AddRange(collection);
						subMesh.tris.AddRange(collection2);
					}
					((WorldDrawLayerBase)worldDrawLayer_UngeneratedPlanetPartsAsDefaultBiome).FinalizeMesh((MeshParts)63);
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				if (<>7__wrap1 is IDisposable disposable)
				{
					disposable.Dispose();
				}
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<object> IEnumerable<object>.GetEnumerator()
			{
				<Regenerate>d__0 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <Regenerate>d__0(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<object>)this).GetEnumerator();
			}
		}

		[IteratorStateMachine(typeof(<Regenerate>d__0))]
		public override IEnumerable Regenerate()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <Regenerate>d__0(-2)
			{
				<>4__this = this
			};
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private IEnumerable <>n__0()
		{
			return ((WorldDrawLayer)this).Regenerate();
		}
	}
	public class DefModExt_RegrowingPart : DefModExtension
	{
		public string labelText = "Regrowing: ";

		public float growthPerDay = 1f;

		public bool coverageMultiplier = true;
	}
	public class HediffCompProperties_PassiveHealing : HediffCompProperties
	{
		public int healTicks = 60;

		public bool healWounds;

		public bool tendWounds;

		public float tendQuality = 1f;

		public bool healWoundsSeq = true;

		public float healWoundsVal = 0.2f;

		public List<HediffDef> woundBlacklist = new List<HediffDef>();

		public int sickTicks = 60;

		public bool healSickness;

		public bool healSicknessSeq = true;

		public float healSicknessVal = 0.2f;

		public bool preventSicknesses;

		public List<HediffDef> sicknessWhitelist = new List<HediffDef>();

		public List<HediffDef> sicknessBlacklist = new List<HediffDef>();

		public int regrowTicks = 180;

		public bool regrowParts;

		public bool regrowPartsSeq = true;

		public HediffDef regrowingPartDef;

		public HediffCompProperties_PassiveHealing()
		{
			base.compClass = typeof(HediffComp_PassiveHealing);
		}
	}
	public class HediffComp_PassiveHealing : HediffComp
	{
		[CompilerGenerated]
		private sealed class <<TryHealSickness>g__GetSicknessHediffs|4_0>d : IEnumerable<Hediff>, IEnumerable, IEnumerator<Hediff>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Hediff <>2__current;

			private int <>l__initialThreadId;

			public HediffComp_PassiveHealing <>4__this;

			private List<Hediff>.Enumerator <>7__wrap1;

			Hediff IEnumerator<Hediff>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <<TryHealSickness>g__GetSicknessHediffs|4_0>d(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>7__wrap1 = default(List<Hediff>.Enumerator);
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				try
				{
					int num = <>1__state;
					HediffComp_PassiveHealing hediffComp_PassiveHealing = <>4__this;
					if (num != 0)
					{
						if (num != 1)
						{
							return false;
						}
						<>1__state = -3;
					}
					else
					{
						<>1__state = -1;
						List<Hediff> hediffs = ((HediffComp)hediffComp_PassiveHealing).Pawn.health.hediffSet.hediffs;
						if (GenList.NullOrEmpty<Hediff>((IList<Hediff>)hediffs))
						{
							goto IL_00f9;
						}
						<>7__wrap1 = hediffs.GetEnumerator();
						<>1__state = -3;
					}
					while (<>7__wrap1.MoveNext())
					{
						Hediff current = <>7__wrap1.Current;
						if ((GenList.NullOrEmpty<HediffDef>((IList<HediffDef>)hediffComp_PassiveHealing.Props.sicknessWhitelist) ? current.def.makesSickThought : hediffComp_PassiveHealing.Props.sicknessWhitelist.Contains(current.def)) && !hediffComp_PassiveHealing.Props.sicknessBlacklist.Contains(current.def))
						{
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
					}
					<>m__Finally1();
					<>7__wrap1 = default(List<Hediff>.Enumerator);
					goto IL_00f9;
					IL_00f9:
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				((IDisposable)<>7__wrap1/*cast due to .constrained prefix*/).Dispose();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Hediff> IEnumerable<Hediff>.GetEnumerator()
			{
				<<TryHealSickness>g__GetSicknessHediffs|4_0>d result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <<TryHealSickness>g__GetSicknessHediffs|4_0>d(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Hediff>)this).GetEnumerator();
			}
		}

		[CompilerGenerated]
		private sealed class <<TryHealWounds>g__GetHealableHediffs|3_0>d : IEnumerable<Hediff>, IEnumerable, IEnumerator<Hediff>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Hediff <>2__current;

			private int <>l__initialThreadId;

			public HediffComp_PassiveHealing <>4__this;

			private List<Hediff>.Enumerator <>7__wrap1;

			Hediff IEnumerator<Hediff>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <<TryHealWounds>g__GetHealableHediffs|3_0>d(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>7__wrap1 = default(List<Hediff>.Enumerator);
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				try
				{
					int num = <>1__state;
					HediffComp_PassiveHealing hediffComp_PassiveHealing = <>4__this;
					if (num != 0)
					{
						if (num != 1)
						{
							return false;
						}
						<>1__state = -3;
					}
					else
					{
						<>1__state = -1;
						List<Hediff> hediffs = ((HediffComp)hediffComp_PassiveHealing).Pawn.health.hediffSet.hediffs;
						if (GenList.NullOrEmpty<Hediff>((IList<Hediff>)hediffs))
						{
							goto IL_00c3;
						}
						<>7__wrap1 = hediffs.GetEnumerator();
						<>1__state = -3;
					}
					while (<>7__wrap1.MoveNext())
					{
						Hediff current = <>7__wrap1.Current;
						if (current is Hediff_Injury && !hediffComp_PassiveHealing.Props.woundBlacklist.Contains(current.def))
						{
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
					}
					<>m__Finally1();
					<>7__wrap1 = default(List<Hediff>.Enumerator);
					goto IL_00c3;
					IL_00c3:
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				((IDisposable)<>7__wrap1/*cast due to .constrained prefix*/).Dispose();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Hediff> IEnumerable<Hediff>.GetEnumerator()
			{
				<<TryHealWounds>g__GetHealableHediffs|3_0>d result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <<TryHealWounds>g__GetHealableHediffs|3_0>d(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Hediff>)this).GetEnumerator();
			}
		}

		public HediffCompProperties_PassiveHealing Props => (HediffCompProperties_PassiveHealing)(object)base.props;

		public override void CompPostTick(ref float severityAdjustment)
		{
			((HediffComp)this).CompPostTick(ref severityAdjustment);
			if (Find.TickManager.TicksAbs % Props.healTicks == 0 && Props.healWounds)
			{
				TryHealWounds();
			}
			if (Find.TickManager.TicksAbs % Props.sickTicks == 0 && Props.healSickness)
			{
				TryHealSickness();
			}
			if (Find.TickManager.TicksAbs % Props.regrowTicks == 0 && Props.regrowParts)
			{
				TryRegrowParts();
			}
		}

		public void TryHealWounds()
		{
			IEnumerable<Hediff> enumerable = GetHealableHediffs();
			if (GenCollection.EnumerableNullOrEmpty<Hediff>(enumerable))
			{
				return;
			}
			foreach (Hediff item in enumerable)
			{
				item.Heal(Props.healWoundsVal);
				if (item.TendableNow(false) && Props.tendWounds)
				{
					item.Tended(Props.tendQuality, Props.tendQuality, 0);
				}
				if (Props.healWoundsSeq)
				{
					break;
				}
			}
			[IteratorStateMachine(typeof(<<TryHealWounds>g__GetHealableHediffs|3_0>d))]
			IEnumerable<Hediff> GetHealableHediffs()
			{
				//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
				return new <<TryHealWounds>g__GetHealableHediffs|3_0>d(-2)
				{
					<>4__this = this
				};
			}
		}

		public void TryHealSickness()
		{
			IEnumerable<Hediff> enumerable = GetSicknessHediffs();
			if (GenCollection.EnumerableNullOrEmpty<Hediff>(enumerable))
			{
				return;
			}
			foreach (Hediff item in enumerable)
			{
				item.Heal(Props.healSicknessVal);
				if (Props.healSicknessSeq)
				{
					break;
				}
			}
			[IteratorStateMachine(typeof(<<TryHealSickness>g__GetSicknessHediffs|4_0>d))]
			IEnumerable<Hediff> GetSicknessHediffs()
			{
				//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
				return new <<TryHealSickness>g__GetSicknessHediffs|4_0>d(-2)
				{
					<>4__this = this
				};
			}
		}

		public void TryRegrowParts()
		{
			if (Props.regrowingPartDef != null)
			{
				foreach (BodyPartRecord part in ((HediffComp)this).Pawn.GetFirstMatchingBodyparts(((HediffComp)this).Pawn.RaceProps.body.corePart, HediffDefOf.MissingBodyPart, Props.regrowingPartDef, (Hediff hediff) => hediff is Hediff_AddedPart))
				{
					Hediff val = ((HediffComp)this).Pawn.health.hediffSet.hediffs.First((Hediff hediff) => hediff.Part == part && hediff.def == HediffDefOf.MissingBodyPart);
					if (val != null)
					{
						((HediffComp)this).Pawn.health.RemoveHediff(val);
						((HediffComp)this).Pawn.health.AddHediff(Props.regrowingPartDef, part, (DamageInfo?)null, (DamageResult)null);
						((HediffComp)this).Pawn.health.hediffSet.DirtyCache();
					}
				}
				return;
			}
			LogUtil.Error("Hediff " + ((Def)((HediffComp)this).Def).defName + " set to regrow parts but has no HediffDef for the regrowablePart to actually do so.");
		}
	}
	public class Hediff_RegrowingPart : HediffWithComps
	{
		public DefModExt_RegrowingPart modExt;

		public DefModExt_RegrowingPart ModExt
		{
			get
			{
				if (modExt == null)
				{
					modExt = ((Def)((Hediff)this).def).GetModExtension<DefModExt_RegrowingPart>();
				}
				return modExt;
			}
		}

		public override bool ShouldRemove => ((Hediff)this).Severity >= ((Hediff)this).def.maxSeverity;

		public override string Label => ModExt.labelText + GenText.ToStringPercent(((Hediff)this).Severity);

		public override void Tick()
		{
			((Hediff)this).Tick();
			((Hediff)this).Severity = ((Hediff)this).Severity + ModExt.growthPerDay / 60000f * (ModExt.coverageMultiplier ? Mathf.Clamp(1f - ((Hediff)this).part.coverage, 0.1f, 1f) : 1f);
		}

		public override void PostRemoved()
		{
			((HediffWithComps)this).PostRemoved();
		}
	}
	public class JobDriver_ApplyHediff : JobDriver
	{
		[CompilerGenerated]
		private sealed class <MakeNewToils>d__8 : IEnumerable<Toil>, IEnumerable, IEnumerator<Toil>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Toil <>2__current;

			private int <>l__initialThreadId;

			public JobDriver_ApplyHediff <>4__this;

			Toil IEnumerator<Toil>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <MakeNewToils>d__8(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				int num = <>1__state;
				JobDriver_ApplyHediff @object = <>4__this;
				switch (num)
				{
				default:
					return false;
				case 0:
					<>1__state = -1;
					<>2__current = ToilFailConditions.FailOnDespawnedOrNull<Toil>(ToilFailConditions.FailOnDespawnedOrNull<Toil>(Toils_Goto.GotoThing((TargetIndex)2, (PathEndMode)2, false), (TargetIndex)2), (TargetIndex)1);
					<>1__state = 1;
					return true;
				case 1:
					<>1__state = -1;
					<>2__current = Toils_Haul.StartCarryThing((TargetIndex)2, false, false, false, true, false);
					<>1__state = 2;
					return true;
				case 2:
					<>1__state = -1;
					<>2__current = ToilFailConditions.FailOnDespawnedOrNull<Toil>(Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false), (TargetIndex)1);
					<>1__state = 3;
					return true;
				case 3:
				{
					<>1__state = -1;
					Toil val = Toils_General.Wait(600, (TargetIndex)0);
					ToilEffects.WithProgressBarToilDelay(val, (TargetIndex)1, false, -0.5f);
					ToilFailConditions.FailOnDespawnedOrNull<Toil>(val, (TargetIndex)1);
					ToilFailConditions.FailOnCannotTouch<Toil>(val, (TargetIndex)1, (PathEndMode)2);
					<>2__current = val;
					<>1__state = 4;
					return true;
				}
				case 4:
					<>1__state = -1;
					<>2__current = Toils_General.Do((Action)@object.ApplyHediff);
					<>1__state = 5;
					return true;
				case 5:
					<>1__state = -1;
					return false;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Toil> IEnumerable<Toil>.GetEnumerator()
			{
				<MakeNewToils>d__8 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <MakeNewToils>d__8(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Toil>)this).GetEnumerator();
			}
		}

		public int useDuration = -1;

		public Thing destination;

		private const int DurationTicks = 600;

		public HediffDef hediffDef;

		private Thing Item
		{
			get
			{
				//IL_0007: Unknown result type (might be due to invalid IL or missing references)
				//IL_000c: Unknown result type (might be due to invalid IL or missing references)
				LocalTargetInfo target = base.job.GetTarget((TargetIndex)2);
				return ((LocalTargetInfo)(ref target)).Thing;
			}
		}

		public override void ExposeData()
		{
			((JobDriver)this).ExposeData();
			Scribe_Values.Look<int>(ref useDuration, "useDuration", 0, false);
			Scribe_References.Look<Thing>(ref destination, "destination", false);
			Scribe_Defs.Look<HediffDef>(ref hediffDef, "hediffDef");
		}

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_005a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0028: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			//IL_007d: Unknown result type (might be due to invalid IL or missing references)
			Pawn pawn = base.pawn;
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			LocalTargetInfo val;
			if (!(((LocalTargetInfo)(ref target)).Thing is Corpse))
			{
				target = base.job.GetTarget((TargetIndex)1);
				Thing thing = ((LocalTargetInfo)(ref target)).Thing;
				val = LocalTargetInfo.op_Implicit((thing is Pawn) ? thing : null);
			}
			else
			{
				target = base.job.GetTarget((TargetIndex)1);
				Thing thing2 = ((LocalTargetInfo)(ref target)).Thing;
				val = LocalTargetInfo.op_Implicit((thing2 is Corpse) ? thing2 : null);
			}
			if (ReservationUtility.Reserve(pawn, val, base.job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false))
			{
				return ReservationUtility.Reserve(base.pawn, LocalTargetInfo.op_Implicit(Item), base.job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false);
			}
			return false;
		}

		[IteratorStateMachine(typeof(<MakeNewToils>d__8))]
		public override IEnumerable<Toil> MakeNewToils()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <MakeNewToils>d__8(-2)
			{
				<>4__this = this
			};
		}

		public void ApplyHediff()
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			Thing thing = ((LocalTargetInfo)(ref target)).Thing;
			Thing obj = ((thing is Pawn) ? thing : null);
			if (hediffDef == null)
			{
				LogUtil.Error("Trying to apply a null hediff");
			}
			((Pawn)obj).health.AddHediff(hediffDef, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			Item.SplitOff(1).Destroy((DestroyMode)0);
		}
	}
	public class DefModExt_Xenotype : DefModExtension
	{
		public XenotypeDef xenotype;
	}
	public class SlotLoadable : Thing, IThingHolder
	{
		private ThingOwner slot;

		public List<ThingDef> slottableThingDefs;

		public Thing owner;

		public Thing SlotOccupant
		{
			get
			{
				if (slot.Count == 0)
				{
					return null;
				}
				if (slot.Count > 1)
				{
					Log.Error("ContainedThing used on a DropPodInfo holding > 1 thing.");
				}
				return slot[0];
			}
			set
			{
				slot.Clear();
				if (value.holdingOwner != null)
				{
					Thing val = value.holdingOwner.Take(value, 1);
					((Entity)value).DeSpawn((DestroyMode)0);
					slot.TryAdd(val, true);
				}
				else
				{
					slot.TryAdd(value, true);
				}
			}
		}

		public ThingOwner Slot
		{
			get
			{
				return slot;
			}
			set
			{
				slot = value;
			}
		}

		public Pawn Holder
		{
			get
			{
				Pawn result = null;
				if (owner != null)
				{
					CompEquippable val = ThingCompUtility.TryGetComp<CompEquippable>(owner);
					if (val != null && val.PrimaryVerb != null)
					{
						Pawn casterPawn = val.PrimaryVerb.CasterPawn;
						if (casterPawn != null && ((Thing)casterPawn).Spawned)
						{
							result = casterPawn;
						}
					}
				}
				return result;
			}
		}

		public Map ParentMap
		{
			get
			{
				Map result = null;
				if (owner != null)
				{
					if (Holder != null)
					{
						return ((Thing)Holder).Map;
					}
					return owner.Map;
				}
				return result;
			}
		}

		public IntVec3 ParentLoc
		{
			get
			{
				//IL_0000: Unknown result type (might be due to invalid IL or missing references)
				//IL_0005: Unknown result type (might be due to invalid IL or missing references)
				//IL_002e: Unknown result type (might be due to invalid IL or missing references)
				//IL_0028: Unknown result type (might be due to invalid IL or missing references)
				//IL_001c: Unknown result type (might be due to invalid IL or missing references)
				IntVec3 invalid = IntVec3.Invalid;
				if (owner != null)
				{
					if (Holder != null)
					{
						return ((Thing)Holder).Position;
					}
					return owner.Position;
				}
				return invalid;
			}
		}

		public List<ThingDef> SlottableTypes => slottableThingDefs;

		public SlotLoadable()
		{
		}

		public SlotLoadable(Thing newOwner)
		{
			SlotLoadableDef slotLoadableDef = base.def as SlotLoadableDef;
			slottableThingDefs = slotLoadableDef.slottableThingDefs;
			owner = newOwner;
			ThingIDMaker.GiveIDTo((Thing)(object)this);
			slot = (ThingOwner)(object)new ThingOwner<Thing>((IThingHolder)(object)this, false, (LookMode)2, true);
		}

		public SlotLoadable(SlotLoadableDef xmlDef, Thing newOwner)
		{
			base.def = (ThingDef)(object)xmlDef;
			slottableThingDefs = xmlDef.slottableThingDefs;
			owner = newOwner;
			ThingIDMaker.GiveIDTo((Thing)(object)this);
			slot = (ThingOwner)(object)new ThingOwner<Thing>((IThingHolder)(object)this, false, (LookMode)2, true);
		}

		public Texture2D SlotIcon()
		{
			if (SlotOccupant != null && SlotOccupant.def != null)
			{
				return ((BuildableDef)SlotOccupant.def).uiIcon;
			}
			return null;
		}

		public Color SlotColor()
		{
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			if (SlotOccupant != null && SlotOccupant.def != null)
			{
				return ((BuildableDef)SlotOccupant.def).graphic.Color;
			}
			return Color.white;
		}

		public bool IsEmpty()
		{
			if (SlotOccupant != null)
			{
				return false;
			}
			return true;
		}

		public bool CanLoad(ThingDef defType)
		{
			if (slottableThingDefs != null && slottableThingDefs.Contains(defType))
			{
				return true;
			}
			return false;
		}

		public override void ExposeData()
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Invalid comparison between Unknown and I4
			((Thing)this).ExposeData();
			if ((int)Scribe.mode == 1 && base.thingIDNumber == -1)
			{
				ThingIDMaker.GiveIDTo((Thing)(object)this);
			}
			Scribe_Deep.Look<ThingOwner>(ref slot, "slot", new object[1] { this });
			Scribe_Collections.Look<ThingDef>(ref slottableThingDefs, "slottableThingDefs", (LookMode)0, Array.Empty<object>());
			Scribe_References.Look<Thing>(ref owner, "owner", false);
		}

		public Map GetMap()
		{
			return ParentMap;
		}

		public ThingOwner GetInnerContainer()
		{
			return slot;
		}

		public IntVec3 GetPosition()
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			return ParentLoc;
		}

		public void GetChildHolders(List<IThingHolder> outChildren)
		{
			ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, (IList<Thing>)GetDirectlyHeldThings());
		}

		public ThingOwner GetDirectlyHeldThings()
		{
			return slot;
		}

		public virtual bool TryLoadSlot(Thing thingToLoad, bool emptyIfFilled = false)
		{
			if ((SlotOccupant != null && emptyIfFilled) || SlotOccupant == null)
			{
				TryEmptySlot();
				if (thingToLoad != null && slottableThingDefs != null && slottableThingDefs.Contains(thingToLoad.def))
				{
					SlotOccupant = thingToLoad;
					return true;
				}
			}
			else
			{
				Messages.Message($"{((Entity)owner).Label}'s slot is already filled", MessageTypeDefOf.RejectInput, true);
			}
			return false;
		}

		public virtual bool TryEmptySlot()
		{
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			if (!CanEmptySlot())
			{
				return false;
			}
			return slot.TryDropAll(ParentLoc, ParentMap, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, true);
		}

		public virtual bool CanEmptySlot()
		{
			return true;
		}
	}
	public class SlotLoadableDef : ThingDef
	{
		public List<ThingDef> slottableThingDefs;
	}
	public class Recipe_Disassemble : RecipeWorker
	{
		[CompilerGenerated]
		private sealed class <GetPartsToApplyOn>d__0 : IEnumerable<BodyPartRecord>, IEnumerable, IEnumerator<BodyPartRecord>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private BodyPartRecord <>2__current;

			private int <>l__initialThreadId;

			BodyPartRecord IEnumerator<BodyPartRecord>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <GetPartsToApplyOn>d__0(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				switch (<>1__state)
				{
				default:
					return false;
				case 0:
					<>1__state = -1;
					<>2__current = null;
					<>1__state = 1;
					return true;
				case 1:
					<>1__state = -1;
					return false;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<BodyPartRecord> IEnumerable<BodyPartRecord>.GetEnumerator()
			{
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					return this;
				}
				return new <GetPartsToApplyOn>d__0(0);
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<BodyPartRecord>)this).GetEnumerator();
			}
		}

		[IteratorStateMachine(typeof(<GetPartsToApplyOn>d__0))]
		public override IEnumerable<BodyPartRecord> GetPartsToApplyOn(Pawn pawn, RecipeDef recipe)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <GetPartsToApplyOn>d__0(-2);
		}

		public override void ApplyOnPawn(Pawn pawn, BodyPartRecord part, Pawn billDoer, List<Thing> ingredients, Bill bill)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			ButcherUtil.SpawnDrops(pawn, ((Thing)pawn).Position, ((Thing)pawn).Map);
			((Thing)pawn).Destroy((DestroyMode)0);
		}
	}
	public class Command_FloatAction : Command_Action
	{
		public Func<IEnumerable<FloatMenuOption>> floatMenuFunc;

		public override IEnumerable<FloatMenuOption> RightClickFloatMenuOptions => floatMenuFunc?.Invoke();
	}
	public class CompProperties_ClusterGrower : CompProperties
	{
		public List<ClusterPlantClass> clusterPlants = new List<ClusterPlantClass>();

		public int growthTicks = 3000;

		public List<ThingDef> cannotGrowOver = new List<ThingDef>();

		public ThingDef undergrowth;

		public float undergrowthRadius = 5.5f;

		public int undergrowthTicks = 1000;

		public bool undergrowthClears;

		public SimpleCurve undergrowthCurve;

		public CompProperties_ClusterGrower()
		{
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_0053: Unknown result type (might be due to invalid IL or missing references)
			//IL_005e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0069: Unknown result type (might be due to invalid IL or missing references)
			//IL_0074: Unknown result type (might be due to invalid IL or missing references)
			//IL_0084: Expected O, but got Unknown
			SimpleCurve val = new SimpleCurve();
			val.Add(new CurvePoint(0f, 1f), true);
			val.Add(new CurvePoint(2.5f, 1f), true);
			val.Add(new CurvePoint(6f, 0f), true);
			undergrowthCurve = val;
			((CompProperties)this)..ctor();
			base.compClass = typeof(Comp_ClusterGrower);
		}
	}
	public class ClusterPlantClass
	{
		public ThingDef def;

		public int count;

		public FloatRange radius = new FloatRange(0f, 4f);

		public bool matureOnly;

		public bool onUndergrowthOnly;

		public float minDistance;

		public float chance = 1f;
	}
	public class CompProperties_DestroyedLeavings : CompProperties
	{
		public List<ThingDefCountClass> leavings = new List<ThingDefCountClass>();

		public float chance = 1f;

		public FloatRange percentRange = new FloatRange(1f, 1f);

		public bool harvestableOnly;

		public CompProperties_DestroyedLeavings()
		{
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			base.compClass = typeof(Comp_DestroyedLeavings);
		}
	}
	public class Comp_ClusterGrower : ThingComp
	{
		[CompilerGenerated]
		private sealed class <CompGetGizmosExtra>d__24 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Comp_ClusterGrower <>4__this;

			private IEnumerator<Gizmo> <>7__wrap1;

			Gizmo IEnumerator<Gizmo>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <CompGetGizmosExtra>d__24(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>7__wrap1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_008a: Unknown result type (might be due to invalid IL or missing references)
				//IL_008f: Unknown result type (might be due to invalid IL or missing references)
				//IL_009a: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
				//IL_00bc: Expected O, but got Unknown
				try
				{
					int num = <>1__state;
					Comp_ClusterGrower CS$<>8__locals3 = <>4__this;
					switch (num)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<>7__wrap1 = CS$<>8__locals3.<>n__0().GetEnumerator();
						<>1__state = -3;
						goto IL_006f;
					case 1:
						<>1__state = -3;
						goto IL_006f;
					case 2:
						{
							<>1__state = -1;
							return false;
						}
						IL_006f:
						if (<>7__wrap1.MoveNext())
						{
							Gizmo current = <>7__wrap1.Current;
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = null;
						<>2__current = (Gizmo)new Command_Action
						{
							defaultLabel = "DEV: Toggle Debug Info",
							defaultDesc = "Show debug information.",
							action = delegate
							{
								CS$<>8__locals3.showDebugRendering = !CS$<>8__locals3.showDebugRendering;
							}
						};
						<>1__state = 2;
						return true;
					}
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				if (<>7__wrap1 != null)
				{
					<>7__wrap1.Dispose();
				}
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
			{
				<CompGetGizmosExtra>d__24 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <CompGetGizmosExtra>d__24(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		public int lastGrowthTick = -1;

		public int lastUndergrowthTick = -1;

		public bool undergrowthDone;

		public bool showDebugRendering;

		public List<IntVec3> undergrowthCellsRemaining = new List<IntVec3>();

		public CompProperties_ClusterGrower Props => (CompProperties_ClusterGrower)(object)base.props;

		public List<IntVec3> currentViableUndergrowthCells => undergrowthCellsRemaining.Where((IntVec3 c) => HasAdjacentUndergrowth(c, ((Thing)base.parent).Map) && IsValidUndergrowthTarget(c, ((Thing)base.parent).Map)).ToList();

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			//IL_0059: Unknown result type (might be due to invalid IL or missing references)
			//IL_0082: Unknown result type (might be due to invalid IL or missing references)
			((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
			if (respawningAfterLoad)
			{
				return;
			}
			ThingWithComps parent = base.parent;
			Plant val = (Plant)(object)((parent is Plant) ? parent : null);
			if (val != null)
			{
				if (Props.undergrowth != null)
				{
					undergrowthCellsRemaining = GenRadial.RadialCellsAround(((Thing)base.parent).Position, Props.undergrowthRadius, false).ToList();
					if (GridsUtility.GetFirstThing(((Thing)base.parent).Position, ((Thing)base.parent).Map, Props.undergrowth) == null)
					{
						GenerateUndergrowth(((Thing)base.parent).Position, ((Thing)base.parent).Map, forced: true);
					}
				}
				if (!val.sown && val.Growth > 0.2f)
				{
					if (Props.undergrowth != null)
					{
						while (AttemptUndergrowth())
						{
						}
					}
					while (AttemptGrowth(randomGrowth: true))
					{
					}
				}
			}
			lastGrowthTick = Find.TickManager.TicksGame;
		}

		public override void CompTick()
		{
			((ThingComp)this).CompTick();
			Tick();
		}

		public override void CompTickRare()
		{
			((ThingComp)this).CompTickRare();
			Tick();
		}

		public override void CompTickLong()
		{
			((ThingComp)this).CompTickLong();
			Tick();
		}

		public void Tick()
		{
			if (Find.TickManager.TicksGame > lastGrowthTick + Props.growthTicks)
			{
				AttemptGrowth();
				lastGrowthTick = Find.TickManager.TicksGame;
			}
			if (Props.undergrowth != null && Find.TickManager.TicksGame > lastUndergrowthTick + Props.undergrowthTicks)
			{
				if (!GenList.NullOrEmpty<IntVec3>((IList<IntVec3>)undergrowthCellsRemaining))
				{
					AttemptUndergrowth();
				}
				lastUndergrowthTick = Find.TickManager.TicksGame;
			}
		}

		public bool AttemptGrowth(bool randomGrowth = false)
		{
			//IL_0049: Unknown result type (might be due to invalid IL or missing references)
			//IL_007e: Unknown result type (might be due to invalid IL or missing references)
			//IL_008f: Unknown result type (might be due to invalid IL or missing references)
			bool result = false;
			foreach (ClusterPlantClass clusterPlant in Props.clusterPlants)
			{
				ThingWithComps parent = base.parent;
				Plant val = (Plant)(object)((parent is Plant) ? parent : null);
				if ((!clusterPlant.matureOnly || val.HarvestableNow) && CountThingsInRadius(clusterPlant.def, ((Thing)base.parent).Position, ((Thing)base.parent).Map, clusterPlant.radius.max) <= clusterPlant.count && TryGrowThingInRadius(clusterPlant.def, ((Thing)base.parent).Position, ((Thing)base.parent).Map, clusterPlant.radius, clusterPlant.onUndergrowthOnly, randomGrowth, clusterPlant.minDistance))
				{
					result = true;
				}
			}
			return result;
		}

		public bool AttemptUndergrowth()
		{
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			//IL_004c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			IntVec3 val = GenCollection.RandomElementByWeightWithFallback<IntVec3>((IEnumerable<IntVec3>)currentViableUndergrowthCells, (Func<IntVec3, float>)((IntVec3 c) => Props.undergrowthCurve.Evaluate(IntVec3Utility.DistanceTo(c, ((Thing)base.parent).Position))), default(IntVec3));
			if (val != default(IntVec3))
			{
				GenerateUndergrowth(val, ((Thing)base.parent).Map);
			}
			undergrowthCellsRemaining.Remove(val);
			return false;
		}

		public void GenerateUndergrowth(IntVec3 c, Map map, bool forced = false)
		{
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			//IL_0068: Unknown result type (might be due to invalid IL or missing references)
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_004b: Unknown result type (might be due to invalid IL or missing references)
			if (!forced && !Rand.Chance(Props.undergrowthCurve.Evaluate(IntVec3Utility.DistanceTo(c, ((Thing)base.parent).Position))))
			{
				return;
			}
			if (Props.undergrowthClears && c != ((Thing)base.parent).Position)
			{
				Plant plant = GridsUtility.GetPlant(c, map);
				if (plant != null)
				{
					((Thing)plant).Destroy((DestroyMode)0);
				}
			}
			GenSpawn.Spawn(Props.undergrowth, c, map, (WipeMode)0);
		}

		public bool HasAdjacentUndergrowth(IntVec3 c, Map map)
		{
			//IL_0009: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_0024: Unknown result type (might be due to invalid IL or missing references)
			if (!((IntVec3)(ref c)).IsValid || !GenGrid.InBounds(c, map))
			{
				return false;
			}
			foreach (IntVec3 item in GenAdjFast.AdjacentCells8Way(c))
			{
				if (GridsUtility.GetFirstThing(item, map, Props.undergrowth) != null)
				{
					return true;
				}
			}
			return false;
		}

		public bool IsValidUndergrowthTarget(IntVec3 c, Map map)
		{
			//IL_0009: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			if (!((IntVec3)(ref c)).IsValid || !GenGrid.InBounds(c, map))
			{
				return false;
			}
			if (GridsUtility.GetFirstThing(c, map, Props.undergrowth) != null)
			{
				return false;
			}
			if (GridsUtility.GetFirstBuilding(c, map) != null)
			{
				return false;
			}
			return true;
		}

		public bool TryGrowThingInRadius(ThingDef targetDef, IntVec3 center, Map map, FloatRange radiusRange, bool onUndergrowthOnly = false, bool randomGrowth = false, float minDistance = 0f)
		{
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			//IL_0045: Unknown result type (might be due to invalid IL or missing references)
			//IL_009e: Unknown result type (might be due to invalid IL or missing references)
			List<IntVec3> invalidCells = GenRadial.RadialCellsAround(center, radiusRange.min, false).ToList();
			List<IntVec3> list = GenRadial.RadialCellsAround(center, radiusRange.max, false).ToList();
			list.RemoveAll((IntVec3 c) => invalidCells.Contains(c));
			List<IntVec3> list2 = list?.Where((IntVec3 c) => ValidGrowthSpot(targetDef, c, map, onUndergrowthOnly, minDistance))?.ToList();
			if (!GenList.NullOrEmpty<IntVec3>((IList<IntVec3>)list2))
			{
				Thing obj = GenSpawn.Spawn(targetDef, GenCollection.RandomElement<IntVec3>((IEnumerable<IntVec3>)list2), map, (WipeMode)0);
				Plant val = (Plant)(object)((obj is Plant) ? obj : null);
				if (randomGrowth)
				{
					val.Growth = Rand.Range(0f, 1f);
				}
				return true;
			}
			return false;
		}

		public bool ValidGrowthSpot(ThingDef targetDef, IntVec3 c, Map map, bool undergrowthOnly, float minDistance)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0072: Unknown result type (might be due to invalid IL or missing references)
			//IL_009a: Unknown result type (might be due to invalid IL or missing references)
			//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
			if (!GenGrid.InBounds(c, map))
			{
				return false;
			}
			if (GenCollection.Any<Thing>(GridsUtility.GetThingList(c, map), (Predicate<Thing>)((Thing t) => t is Plant)))
			{
				return false;
			}
			if (undergrowthOnly && GridsUtility.GetFirstThing(c, map, Props.undergrowth) == null)
			{
				return false;
			}
			if (GenCollection.Any<Thing>(GridsUtility.GetThingList(c, map), (Predicate<Thing>)((Thing t) => Props.cannotGrowOver.Contains(t.def))))
			{
				return false;
			}
			if (CountThingsInRadius(targetDef, c, map, minDistance) > 0)
			{
				return false;
			}
			DefModExt_PlantStuff modExtension = ((Def)targetDef).GetModExtension<DefModExt_PlantStuff>();
			if (modExtension != null)
			{
				if ((modExtension.freshWaterPlant || modExtension.oceanWaterPlant) && !GridsUtility.GetTerrain(c, map).IsWater)
				{
					return false;
				}
				if ((int)(Plant)GenClosest.ClosestThing_Global(c, (IEnumerable)map.listerThings.ThingsMatching(new ThingRequest
				{
					singleDef = targetDef
				}), modExtension.distToNearestOther, (Predicate<Thing>)null, (Func<Thing, float>)null, false) != 0)
				{
					return false;
				}
			}
			return true;
		}

		public int CountThingsInRadius(ThingDef targetDef, IntVec3 center, Map map, float radius)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			int num = 0;
			foreach (IntVec3 item in GenRadial.RadialCellsAround(center, radius, true))
			{
				if (GenGrid.InBounds(item, map) && GridsUtility.GetFirstThing(item, map, targetDef) != null)
				{
					num++;
				}
			}
			return num;
		}

		public override void PostExposeData()
		{
			((ThingComp)this).PostExposeData();
			Scribe_Values.Look<int>(ref lastGrowthTick, "lastGrowthTick", -1, false);
			Scribe_Values.Look<int>(ref lastUndergrowthTick, "lastUndergrowthTick", -1, false);
			Scribe_Values.Look<bool>(ref undergrowthDone, "undergrowthDone", false, false);
			Scribe_Collections.Look<IntVec3>(ref undergrowthCellsRemaining, "undergrowthCellsRemaining", (LookMode)0, Array.Empty<object>());
		}

		public override void PostDraw()
		{
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			if (showDebugRendering)
			{
				GenDraw.DrawFieldEdges(undergrowthCellsRemaining, Color.white, (float?)null, (HashSet<IntVec3>)null, 2900);
				GenDraw.DrawFieldEdges(currentViableUndergrowthCells, Color.red, (float?)null, (HashSet<IntVec3>)null, 2900);
			}
			((ThingComp)this).PostDraw();
		}

		[IteratorStateMachine(typeof(<CompGetGizmosExtra>d__24))]
		public override IEnumerable<Gizmo> CompGetGizmosExtra()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <CompGetGizmosExtra>d__24(-2)
			{
				<>4__this = this
			};
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private IEnumerable<Gizmo> <>n__0()
		{
			return ((ThingComp)this).CompGetGizmosExtra();
		}
	}
	public class Comp_DestroyedLeavings : ThingComp
	{
		public CompProperties_DestroyedLeavings Props => (CompProperties_DestroyedLeavings)(object)base.props;

		public override void PostDestroy(DestroyMode mode, Map previousMap)
		{
			//IL_0110: Unknown result type (might be due to invalid IL or missing references)
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_0049: Unknown result type (might be due to invalid IL or missing references)
			//IL_004b: Unknown result type (might be due to invalid IL or missing references)
			//IL_009a: Unknown result type (might be due to invalid IL or missing references)
			if (Rand.Chance(Props.chance))
			{
				float randomInRange = ((FloatRange)(ref Props.percentRange)).RandomInRange;
				QualityCategory val4 = default(QualityCategory);
				foreach (ThingDefCountClass leaving in Props.leavings)
				{
					ThingDefCount val = ThingDefCount.op_Implicit(leaving);
					if (!(val != ThingDefCount.op_Implicit((ThingDefCountClass)null)))
					{
						continue;
					}
					Thing val2 = ThingMaker.MakeThing(((ThingDefCount)(ref val)).ThingDef, (ThingDef)null);
					val2.stackCount = Mathf.CeilToInt((float)((ThingDefCount)(ref val)).Count * randomInRange);
					CompQuality val3 = ThingCompUtility.TryGetComp<CompQuality>(val2);
					if (QualityUtility.TryGetQuality((Thing)(object)base.parent, ref val4) && val3 != null)
					{
						val3.SetQuality(val4, (ArtGenerationContext?)(ArtGenerationContext)0);
					}
					if (val2.def.Minifiable)
					{
						val2 = (Thing)(object)MinifyUtility.MakeMinified(val2, (DestroyMode)0);
					}
					ThingWithComps parent = base.parent;
					Plant val5 = (Plant)(object)((parent is Plant) ? parent : null);
					if (val5 != null)
					{
						if (!Props.harvestableOnly || val5.HarvestableNow)
						{
							SpawnThing(val2);
						}
					}
					else
					{
						SpawnThing(val2);
					}
				}
			}
			((ThingComp)this).PostDestroy(mode, previousMap);
		}

		public void SpawnThing(Thing thing)
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			GenPlace.TryPlaceThing(thing, ((Thing)base.parent).Position, ((Thing)base.parent).Map, (ThingPlaceMode)0, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
		}
	}
	public class DefModExt_HiddenResearch : DefModExtension
	{
	}
	public class DefModExt_PreventPlantSpawns : DefModExtension
	{
		public List<ThingDef> allowedPlants = new List<ThingDef>();
	}
	public class Gene_HediffActivator : Gene
	{
		[CompilerGenerated]
		private sealed class <>c__DisplayClass2_0
		{
			public Gene_HediffActivator <>4__this;

			public DefModExt_GeneHediffActivator modExt;

			internal void <GetGizmos>b__0()
			{
				<>4__this.ApplyHediff(modExt.hediff);
				<>4__this.cooldownTicks = modExt.cooldown;
			}
		}

		[CompilerGenerated]
		private sealed class <GetGizmos>d__2 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Gene_HediffActivator <>4__this;

			private <>c__DisplayClass2_0 <>8__1;

			private IEnumerator<Gizmo> <>7__wrap1;

			Gizmo IEnumerator<Gizmo>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <GetGizmos>d__2(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>8__1 = null;
				<>7__wrap1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
				//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
				//IL_00f8: Unknown result type (might be due to invalid IL or missing references)
				//IL_0107: Unknown result type (might be due to invalid IL or missing references)
				//IL_0118: Unknown result type (might be due to invalid IL or missing references)
				//IL_0127: Unknown result type (might be due to invalid IL or missing references)
				//IL_0143: Unknown result type (might be due to invalid IL or missing references)
				//IL_0170: Unknown result type (might be due to invalid IL or missing references)
				//IL_0181: Unknown result type (might be due to invalid IL or missing references)
				//IL_0186: Unknown result type (might be due to invalid IL or missing references)
				//IL_0195: Unknown result type (might be due to invalid IL or missing references)
				//IL_01b1: Expected O, but got Unknown
				try
				{
					int num = <>1__state;
					Gene_HediffActivator gene_HediffActivator = <>4__this;
					switch (num)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<>8__1 = new <>c__DisplayClass2_0();
						<>8__1.<>4__this = <>4__this;
						if (!GenCollection.EnumerableNullOrEmpty<Gizmo>(gene_HediffActivator.<>n__0()))
						{
							<>7__wrap1 = gene_HediffActivator.<>n__0().GetEnumerator();
							<>1__state = -3;
							goto IL_009b;
						}
						goto IL_00b5;
					case 1:
						<>1__state = -3;
						goto IL_009b;
					case 2:
						{
							<>1__state = -1;
							break;
						}
						IL_009b:
						if (<>7__wrap1.MoveNext())
						{
							Gizmo current = <>7__wrap1.Current;
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = null;
						goto IL_00b5;
						IL_00b5:
						<>8__1.modExt = ((Def)((Gene)gene_HediffActivator).def).GetModExtension<DefModExt_GeneHediffActivator>();
						if (gene_HediffActivator.PawnIsCapable(<>8__1.modExt))
						{
							<>2__current = (Gizmo)new Command_Action
							{
								defaultLabel = TaggedString.op_Implicit(Translator.Translate(<>8__1.modExt.labelKey)),
								defaultDesc = TaggedString.op_Implicit(Translator.Translate(<>8__1.modExt.descKey)),
								icon = (Texture)(object)ContentFinder<Texture2D>.Get(<>8__1.modExt.iconTex, true),
								disabled = (gene_HediffActivator.CheckHasHediff(<>8__1.modExt.hediff) && gene_HediffActivator.cooldownTicks <= 0),
								disabledReason = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("TabulaRasa.DisabledByCooldown", NamedArgument.op_Implicit(GenDate.TicksToDays(gene_HediffActivator.cooldownTicks)))),
								action = delegate
								{
									<>8__1.<>4__this.ApplyHediff(<>8__1.modExt.hediff);
									<>8__1.<>4__this.cooldownTicks = <>8__1.modExt.cooldown;
								}
							};
							<>1__state = 2;
							return true;
						}
						break;
					}
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				if (<>7__wrap1 != null)
				{
					<>7__wrap1.Dispose();
				}
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
			{
				<GetGizmos>d__2 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <GetGizmos>d__2(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		public int cooldownTicks;

		public override void Tick()
		{
			((Gene)this).Tick();
			cooldownTicks--;
		}

		[IteratorStateMachine(typeof(<GetGizmos>d__2))]
		public override IEnumerable<Gizmo> GetGizmos()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <GetGizmos>d__2(-2)
			{
				<>4__this = this
			};
		}

		public override void ExposeData()
		{
			((Gene)this).ExposeData();
			Scribe_Values.Look<int>(ref cooldownTicks, "cooldownTicks", 0, false);
		}

		public void ApplyHediff(HediffDef hediff)
		{
			if (!base.pawn.health.hediffSet.HasHediff(hediff, false))
			{
				base.pawn.health.AddHediff(hediff, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null).Severity = 1f;
			}
		}

		public bool CheckHasHediff(HediffDef hediff)
		{
			return base.pawn.health.hediffSet.HasHediff(hediff, false);
		}

		public bool PawnIsCapable(DefModExt_GeneHediffActivator modExt)
		{
			if (!GenList.NullOrEmpty<SkillLevelSetting>((IList<SkillLevelSetting>)modExt.reqSkillLevels))
			{
				foreach (SkillLevelSetting reqSkillLevel in modExt.reqSkillLevels)
				{
					if (base.pawn.skills.GetSkill(reqSkillLevel.skill).Level < reqSkillLevel.level)
					{
						return false;
					}
				}
			}
			if (!GenList.NullOrEmpty<BodyTypeDef>((IList<BodyTypeDef>)modExt.reqBodyTypes) && !modExt.reqBodyTypes.Contains(base.pawn.story.bodyType))
			{
				return false;
			}
			if (!GenList.NullOrEmpty<HediffDef>((IList<HediffDef>)modExt.reqHediffs))
			{
				foreach (HediffDef reqHediff in modExt.reqHediffs)
				{
					if (!CheckHasHediff(reqHediff))
					{
						return false;
					}
				}
			}
			if (!GenList.NullOrEmpty<TraitDef>((IList<TraitDef>)modExt.reqTraits))
			{
				foreach (TraitDef reqTrait in modExt.reqTraits)
				{
					if (!base.pawn.story.traits.HasTrait(reqTrait))
					{
						return false;
					}
				}
			}
			return true;
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private IEnumerable<Gizmo> <>n__0()
		{
			return ((Gene)this).GetGizmos();
		}
	}
	[HarmonyPatch(typeof(WildPlantSpawner), "CheckSpawnWildPlantAt")]
	public static class Patch_WildPlantSpawner_CheckSpawnWildPlantAt
	{
		[HarmonyPrefix]
		public static bool Prefix(WildPlantSpawner __instance, IntVec3 c, float plantDensityFactor, float wholeMapNumDesiredPlants, bool setRandomGrowth = false)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			if (GenCollection.Any<Thing>(GridsUtility.GetThingList(c, __instance.map), (Predicate<Thing>)((Thing t) => ((Def)t.def).HasModExtension<DefModExt_PreventPlantSpawns>())))
			{
				return false;
			}
			return true;
		}
	}
	public class IngestionOutcomeDoer_DrainHediff : IngestionOutcomeDoer
	{
		public HediffDef hediffDef;

		public float severity = 1f;

		public override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
		{
			if (hediffDef != null)
			{
				Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(hediffDef, false);
				if (firstHediffOfDef != null)
				{
					firstHediffOfDef.Severity -= severity;
				}
			}
		}
	}
	public class DefModExt_GeneHediffActivator : DefModExtension
	{
		public string labelKey;

		public string descKey;

		public string iconTex;

		public HediffDef hediff;

		public List<SkillLevelSetting> reqSkillLevels = new List<SkillLevelSetting>();

		public List<BodyTypeDef> reqBodyTypes = new List<BodyTypeDef>();

		public List<HediffDef> reqHediffs = new List<HediffDef>();

		public List<TraitDef> reqTraits = new List<TraitDef>();

		public int cooldown = 60000;
	}
	public class DefModExt_GeneRegeneration : DefModExtension
	{
		public int healTicks = 1000;

		public List<HediffDef> ignoreWhenHealing = new List<HediffDef>();

		public bool regrowParts = true;

		public int cureTicks = 1000;

		public bool removeInfections = true;

		public List<HediffDef> infectionsAllowed = new List<HediffDef>();

		public List<HediffDef> explicitRemovals = new List<HediffDef>();

		public int growthTicks = 1000;

		public string growthText = "Growth: ";

		public HediffDef protoBodyPart;

		public HediffDef curedBodyPart;

		public HediffDef autoHealHediff;
	}
	public class DefModExt_SpecialButchering : DefModExtension
	{
		public List<ThingDefCount> products = new List<ThingDefCount>();

		public bool affectedBySize;

		public bool affectedByDamage;
	}
	public class Gene_Regeneration : Gene
	{
		public int ticksUntilNextHeal = -1;

		public int ticksUntilNextGrow = -1;

		public int ticksUntilNextCure = -1;

		public DefModExt_GeneRegeneration modExt;

		public DefModExt_GeneRegeneration ModExt
		{
			get
			{
				if (modExt == null)
				{
					modExt = ((Def)base.def).GetModExtension<DefModExt_GeneRegeneration>();
				}
				return modExt;
			}
		}

		public override void Tick()
		{
			((Gene)this).Tick();
			if (ModExt != null)
			{
				if (Current.Game.tickManager.TicksGame >= ticksUntilNextHeal)
				{
					HealthUtil.TrySealWounds(base.pawn, ModExt.ignoreWhenHealing);
					HealthUtil.SetNextTick(ticksUntilNextHeal, ModExt.healTicks);
				}
				if (Current.Game.tickManager.TicksGame >= ticksUntilNextGrow && ModExt.regrowParts)
				{
					HealthUtil.TryRegrowBodyparts(base.pawn, ModExt.protoBodyPart);
					HealthUtil.SetNextTick(ticksUntilNextGrow, ModExt.growthTicks);
				}
				if (Current.Game.tickManager.TicksGame >= ticksUntilNextCure && ModExt.removeInfections)
				{
					HealthUtil.TryCureInfections(base.pawn, ModExt.infectionsAllowed, ModExt.explicitRemovals);
					HealthUtil.SetNextTick(ticksUntilNextCure, ModExt.cureTicks);
				}
			}
			else
			{
				LogUtil.Warning("GeneDef " + ((Def)base.def).defName + " has a null DefModExt_GeneRegeneration so regeneration will not function properly.");
			}
		}

		public override void ExposeData()
		{
			((Gene)this).ExposeData();
			Scribe_Values.Look<int>(ref ticksUntilNextGrow, "ticksUntilNextGrow", 0, false);
			Scribe_Values.Look<int>(ref ticksUntilNextHeal, "ticksUntilNextHeal", 0, false);
			Scribe_Values.Look<int>(ref ticksUntilNextCure, "ticksUntilNextCure", 0, false);
		}
	}
	public class MapComp_VisualOverlays : MapComponent
	{
		public List<Hediff_VisualOverlay> hediffOverlays = new List<Hediff_VisualOverlay>();

		public MapComp_VisualOverlays(Map map)
			: base(map)
		{
		}

		public override void MapComponentUpdate()
		{
			((MapComponent)this).MapComponentUpdate();
			for (int i = 0; i < hediffOverlays.Count; i++)
			{
				Hediff_VisualOverlay hediff_VisualOverlay = hediffOverlays[i];
				if (hediff_VisualOverlay == null || ((Hediff)hediff_VisualOverlay).pawn == null || !((Hediff)hediff_VisualOverlay).pawn.health.hediffSet.hediffs.Contains((Hediff)(object)hediff_VisualOverlay))
				{
					hediffOverlays.RemoveAt(i);
					continue;
				}
				Pawn pawn = ((Hediff)hediff_VisualOverlay).pawn;
				if (((pawn != null) ? ((Thing)pawn).MapHeld : null) != null)
				{
					hediff_VisualOverlay.Draw();
				}
			}
		}

		public override void ExposeData()
		{
			((MapComponent)this).ExposeData();
			Scribe_Collections.Look<Hediff_VisualOverlay>(ref hediffOverlays, "hediffOverlays", (LookMode)3, Array.Empty<object>());
		}
	}
	public class DefModExt_Switcher : DefModExtension
	{
		public ThingDef buildingDef;

		public SoundDef activateSound;

		public string label = "Switch";

		public string description = "Switch the building to the target def.";

		public string icon;
	}
	[StaticConstructorOnStartup]
	public abstract class Hediff_VisualOverlay : HediffWithComps
	{
		public MaterialPropertyBlock MatPropertyBlock = new MaterialPropertyBlock();

		private Material material;

		public Material OverlayMat
		{
			get
			{
				if ((Object)(object)material == (Object)null)
				{
					material = MaterialPool.MatFrom(OverlayPath, OverlayShader);
				}
				return material;
			}
		}

		public virtual float OverlaySize => 1f;

		public virtual string OverlayPath { get; }

		public virtual Shader OverlayShader => ShaderDatabase.MoteGlow;

		public virtual void Draw()
		{
		}

		public override void PostAdd(DamageInfo? dinfo)
		{
			((HediffWithComps)this).PostAdd(dinfo);
			Map mapHeld = ((Thing)((Hediff)this).pawn).MapHeld;
			if (mapHeld != null)
			{
				mapHeld.GetComponent<MapComp_VisualOverlays>().hediffOverlays.Add(this);
			}
		}
	}
	public class PawnGroupMaker_Complex : PawnGroupMaker
	{
		public bool limitFactionPoints;

		public int minPoints = int.MinValue;

		public int maxPoints = int.MaxValue;

		public bool limitTemperature;

		public float minTemperature = -999f;

		public float maxTemperature = 999f;

		public bool limitTimeSinceStart;

		public int onlyAfterDays = int.MinValue;

		public int onlyBeforeDays = int.MaxValue;

		public bool requiredPollutionLevel;

		public bool requiredPollutionLevelExact;

		public PollutionLevel pollutionLevel;

		public bool CanGenerate(PawnGroupMakerParms parms)
		{
			//IL_009d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00be: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
			int num = FactionUtil.FactionPoints();
			if (limitFactionPoints && (num < minPoints || num > maxPoints))
			{
				return false;
			}
			if (limitTemperature && (Find.CurrentMap.mapTemperature.OutdoorTemp < minTemperature || Find.CurrentMap.mapTemperature.OutdoorTemp > maxTemperature))
			{
				return false;
			}
			int num2 = Mathf.FloorToInt(GenDate.TicksToDays(Find.TickManager.TicksSinceSettle));
			if (limitTimeSinceStart && (num2 >= onlyBeforeDays || num2 < onlyAfterDays))
			{
				return false;
			}
			if (requiredPollutionLevel && PollutionUtility.PollutionLevel(Find.CurrentMap.TileInfo) >= pollutionLevel)
			{
				return false;
			}
			if (requiredPollutionLevelExact && PollutionUtility.PollutionLevel(Find.CurrentMap.TileInfo) != pollutionLevel)
			{
				return false;
			}
			return true;
		}
	}
	public class WorldComp_FactionWars : WorldComponent
	{
		private Dictionary<AllegianceDef, float> warProgressDict;

		public Dictionary<AllegianceDef, float> WarProgressDict
		{
			get
			{
				if (warProgressDict == null)
				{
					warProgressDict = new Dictionary<AllegianceDef, float>();
				}
				return warProgressDict;
			}
		}

		public WorldComp_FactionWars(World world)
			: base(world)
		{
			foreach (AllegianceDef allDef in DefDatabase<AllegianceDef>.AllDefs)
			{
				if (!WarProgressDict.ContainsKey(allDef))
				{
					WarProgressDict.Add(allDef, 0f);
				}
			}
		}

		public float GetWarProgress(AllegianceDef def)
		{
			return WarProgressDict[def];
		}

		public void SetWarProgress(AllegianceDef def, float value)
		{
			WarProgressDict[def] = Mathf.Clamp(value, -1f, 1f);
		}

		public void AdjustWarProgress(AllegianceDef def, float value)
		{
			WarProgressDict[def] = Mathf.Clamp(WarProgressDict[def] + value, -1f, 1f);
		}

		public override void ExposeData()
		{
			((WorldComponent)this).ExposeData();
			Scribe_Collections.Look<AllegianceDef, float>(ref warProgressDict, "warProgressDict", (LookMode)0, (LookMode)0);
		}
	}
	public class Allegiance : IExposable
	{
		public AllegianceDef def;

		public float level;

		public void ExposeData()
		{
			Scribe_Defs.Look<AllegianceDef>(ref def, "def");
			Scribe_Values.Look<float>(ref level, "level", 0f, false);
		}
	}
	public class AllegianceDef : Def
	{
		public Faction factionLeft;

		public Color? factionLeftColor;

		public Faction factionRight;

		public Color? factionRightColor;
	}
	public class CompProperties_RandomSounds : CompProperties
	{
		public List<SoundDef> soundDefs = new List<SoundDef>();

		public IntRange tickRange = new IntRange(1000, 10000);

		public CompProperties_RandomSounds()
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			base.compClass = typeof(Comp_RandomSounds);
		}
	}
	public class CompProperties_Shield : CompProperties
	{
		public bool interceptAirProjectiles;

		public bool interceptGroundProjectiles;

		public bool interceptNonHostileProjectiles = true;

		public bool interceptOutgoingProjectiles;

		public EffecterDef reactivateEffect;

		public string stressLabel = "Shield Stress Level";

		public int resetTime = 30000;

		public SoundDef startupSound;

		public SoundDef shutdownSound;

		public SoundDef impactSound;

		public SoundDef breakSound;

		public FloatRange powerUsageRange = new FloatRange(0f, 0f);

		public bool useAmbientCooling;

		public float maximumHeatLevel;

		public FloatRange heatGenRange = new FloatRange(0f, 100f);

		public float stressReduction = 1f;

		public float stressPerDamage = 0.003f;

		public float empDamageFactor = 5f;

		public float shieldOverloadThreshold = 0.9f;

		public float shieldOverloadChance = 0.3f;

		public int extraOverloadRange = 3;

		public DamageDef overloadDamageType;

		public bool explodeOnCollapse;

		public bool shieldCanBeOffset;

		public bool shieldCanBeScaled;

		public IntRange shieldScaleLimits = new IntRange(0, 10);

		public int shieldScaleDefault = 5;

		public bool shieldCanBeColored = true;

		public Color shieldColour = Color.white;

		public bool drawInterceptCone;

		public float minAlpha;

		public float idlePulseSpeed;

		public bool podBlocker = true;

		public bool podBlockFriendlies;

		public List<Type> skyfallerClassWhitelist = new List<Type>();

		public override void ResolveReferences(ThingDef parentDef)
		{
			((CompProperties)this).ResolveReferences(parentDef);
			if (startupSound == null)
			{
				startupSound = SoundDefOf.Power_OnSmall;
			}
			if (shutdownSound == null)
			{
				shutdownSound = SoundDefOf.Power_OffSmall;
			}
			if (impactSound == null)
			{
				impactSound = SoundDefOf.EnergyShield_AbsorbDamage;
			}
			if (breakSound == null)
			{
				breakSound = TabulaRasaDefOf.EnergyShield_Broken;
			}
			if (reactivateEffect == null)
			{
				reactivateEffect = EffecterDefOf.ActivatorProximityTriggered;
			}
			if (overloadDamageType == null)
			{
				overloadDamageType = DamageDefOf.EMP;
			}
		}
	}
	[StaticConstructorOnStartup]
	public class Comp_Shield : ThingComp
	{
		[CompilerGenerated]
		private sealed class <CompGetGizmosExtra>d__79 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Comp_Shield <>4__this;

			private IEnumerator<Gizmo> <>7__wrap1;

			Gizmo IEnumerator<Gizmo>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <CompGetGizmosExtra>d__79(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>7__wrap1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_0256: Unknown result type (might be due to invalid IL or missing references)
				//IL_025b: Unknown result type (might be due to invalid IL or missing references)
				//IL_0261: Unknown result type (might be due to invalid IL or missing references)
				//IL_0270: Unknown result type (might be due to invalid IL or missing references)
				//IL_0276: Unknown result type (might be due to invalid IL or missing references)
				//IL_0285: Unknown result type (might be due to invalid IL or missing references)
				//IL_0296: Unknown result type (might be due to invalid IL or missing references)
				//IL_02ad: Expected O, but got Unknown
				//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
				//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
				//IL_00fd: Unknown result type (might be due to invalid IL or missing references)
				//IL_010c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0112: Unknown result type (might be due to invalid IL or missing references)
				//IL_0121: Unknown result type (might be due to invalid IL or missing references)
				//IL_0132: Unknown result type (might be due to invalid IL or missing references)
				//IL_0149: Expected O, but got Unknown
				//IL_02c3: Unknown result type (might be due to invalid IL or missing references)
				//IL_02c8: Unknown result type (might be due to invalid IL or missing references)
				//IL_02ce: Unknown result type (might be due to invalid IL or missing references)
				//IL_02dd: Unknown result type (might be due to invalid IL or missing references)
				//IL_02e3: Unknown result type (might be due to invalid IL or missing references)
				//IL_02f2: Unknown result type (might be due to invalid IL or missing references)
				//IL_0304: Unknown result type (might be due to invalid IL or missing references)
				//IL_0315: Unknown result type (might be due to invalid IL or missing references)
				//IL_032c: Expected O, but got Unknown
				//IL_038f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0394: Unknown result type (might be due to invalid IL or missing references)
				//IL_039f: Unknown result type (might be due to invalid IL or missing references)
				//IL_03b1: Unknown result type (might be due to invalid IL or missing references)
				//IL_03c8: Expected O, but got Unknown
				//IL_016c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0171: Unknown result type (might be due to invalid IL or missing references)
				//IL_0177: Unknown result type (might be due to invalid IL or missing references)
				//IL_0186: Unknown result type (might be due to invalid IL or missing references)
				//IL_018c: Unknown result type (might be due to invalid IL or missing references)
				//IL_019b: Unknown result type (might be due to invalid IL or missing references)
				//IL_01ac: Unknown result type (might be due to invalid IL or missing references)
				//IL_01c3: Expected O, but got Unknown
				//IL_01e9: Unknown result type (might be due to invalid IL or missing references)
				//IL_01ee: Unknown result type (might be due to invalid IL or missing references)
				//IL_01f4: Unknown result type (might be due to invalid IL or missing references)
				//IL_0203: Unknown result type (might be due to invalid IL or missing references)
				//IL_0209: Unknown result type (might be due to invalid IL or missing references)
				//IL_0218: Unknown result type (might be due to invalid IL or missing references)
				//IL_0229: Unknown result type (might be due to invalid IL or missing references)
				//IL_0240: Expected O, but got Unknown
				//IL_0355: Unknown result type (might be due to invalid IL or missing references)
				//IL_035a: Unknown result type (might be due to invalid IL or missing references)
				//IL_0365: Unknown result type (might be due to invalid IL or missing references)
				//IL_037c: Expected O, but got Unknown
				try
				{
					int num = <>1__state;
					Comp_Shield CS$<>8__locals27 = <>4__this;
					switch (num)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<>7__wrap1 = CS$<>8__locals27.<>n__0().GetEnumerator();
						<>1__state = -3;
						goto IL_008e;
					case 1:
						<>1__state = -3;
						goto IL_008e;
					case 2:
						<>1__state = -1;
						if (CS$<>8__locals27.Props.shieldCanBeColored)
						{
							<>2__current = (Gizmo)new Command_Action
							{
								defaultLabel = TaggedString.op_Implicit(Translator.Translate("ShieldGenColorLabel")),
								defaultDesc = TaggedString.op_Implicit(Translator.Translate("ShieldGenColorDescription")),
								icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Buttons/ShieldColor", true),
								action = delegate
								{
									Find.WindowStack.Add((Window)(object)new Popup_ColourPicker(CS$<>8__locals27));
								}
							};
							<>1__state = 3;
							return true;
						}
						goto IL_015e;
					case 3:
						<>1__state = -1;
						goto IL_015e;
					case 4:
						<>1__state = -1;
						goto IL_01d8;
					case 5:
						<>1__state = -1;
						<>2__current = (Gizmo)new Command_Action
						{
							defaultLabel = TaggedString.op_Implicit(Translator.Translate("ShieldGenOffsetYLabel")),
							defaultDesc = TaggedString.op_Implicit(Translator.Translate("ShieldGenOffsetYDescription")),
							icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Buttons/ShieldOffsetY", true),
							action = delegate
							{
								//IL_000a: Unknown result type (might be due to invalid IL or missing references)
								Find.WindowStack.Add((Window)(object)new Popup_IntSlider(TaggedString.op_Implicit(Translator.Translate("ShieldGenOffsetYTitle")), -(CS$<>8__locals27.Props.shieldScaleLimits.max / 2), CS$<>8__locals27.Props.shieldScaleLimits.max / 2, () => CS$<>8__locals27.SetShieldOffsetY, delegate(int size)
								{
									CS$<>8__locals27.SetShieldOffsetY = size;
								}));
							}
						};
						<>1__state = 6;
						return true;
					case 6:
						<>1__state = -1;
						goto IL_02c2;
					case 7:
						<>1__state = -1;
						goto IL_0341;
					case 8:
						<>1__state = -1;
						goto IL_038e;
					case 9:
						{
							<>1__state = -1;
							break;
						}
						IL_015e:
						if (CS$<>8__locals27.Props.shieldCanBeScaled)
						{
							<>2__current = (Gizmo)new Command_Action
							{
								defaultLabel = TaggedString.op_Implicit(Translator.Translate("ShieldGenRadiusLabel")),
								defaultDesc = TaggedString.op_Implicit(Translator.Translate("ShieldGenRadiusDescription")),
								icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Buttons/ShieldRadius", true),
								action = delegate
								{
									//IL_000a: Unknown result type (might be due to invalid IL or missing references)
									Find.WindowStack.Add((Window)(object)new Popup_IntSlider(TaggedString.op_Implicit(Translator.Translate("ShieldGenRadiusTitle")), CS$<>8__locals27.Props.shieldScaleLimits.min, CS$<>8__locals27.Props.shieldScaleLimits.max, () => CS$<>8__locals27.SetShieldRadius, delegate(int size)
									{
										CS$<>8__locals27.SetShieldRadius = size;
									}));
								}
							};
							<>1__state = 4;
							return true;
						}
						goto IL_01d8;
						IL_038e:
						<>2__current = (Gizmo)new Command_Toggle
						{
							defaultLabel = "Dev: Intercept non-hostile",
							isActive = () => CS$<>8__locals27.debugInterceptNonHostileProjectiles,
							toggleAction = delegate
							{
								CS$<>8__locals27.debugInterceptNonHostileProjectiles = !CS$<>8__locals27.debugInterceptNonHostileProjectiles;
							}
						};
						<>1__state = 9;
						return true;
						IL_01d8:
						if (CS$<>8__locals27.Props.shieldCanBeOffset)
						{
							<>2__current = (Gizmo)new Command_Action
							{
								defaultLabel = TaggedString.op_Implicit(Translator.Translate("ShieldGenOffsetXLabel")),
								defaultDesc = TaggedString.op_Implicit(Translator.Translate("ShieldGenOffsetXDescription")),
								icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Buttons/ShieldOffsetX", true),
								action = delegate
								{
									//IL_000a: Unknown result type (might be due to invalid IL or missing references)
									Find.WindowStack.Add((Window)(object)new Popup_IntSlider(TaggedString.op_Implicit(Translator.Translate("ShieldGenOffsetXTitle")), -(CS$<>8__locals27.Props.shieldScaleLimits.max / 2), CS$<>8__locals27.Props.shieldScaleLimits.max / 2, () => CS$<>8__locals27.SetShieldOffsetX, delegate(int size)
									{
										CS$<>8__locals27.SetShieldOffsetX = size;
									}));
								}
							};
							<>1__state = 5;
							return true;
						}
						goto IL_02c2;
						IL_0341:
						if (!Prefs.DevMode)
						{
							break;
						}
						if (CS$<>8__locals27.ticksToReset > 0)
						{
							<>2__current = (Gizmo)new Command_Action
							{
								defaultLabel = "Dev: Reset cooldown",
								action = delegate
								{
									CS$<>8__locals27.ticksToReset = 0;
								}
							};
							<>1__state = 8;
							return true;
						}
						goto IL_038e;
						IL_02c2:
						<>2__current = (Gizmo)new Command_Toggle
						{
							defaultLabel = TaggedString.op_Implicit(Translator.Translate("ShieldGenToggleVisibility")),
							defaultDesc = TaggedString.op_Implicit(Translator.Translate("ShieldGenToggleVisibilityDesc")),
							isActive = () => CS$<>8__locals27.showShieldToggle,
							icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Buttons/ShieldVisibility", true),
							toggleAction = delegate
							{
								CS$<>8__locals27.showShieldToggle = !CS$<>8__locals27.showShieldToggle;
							}
						};
						<>1__state = 7;
						return true;
						IL_008e:
						if (<>7__wrap1.MoveNext())
						{
							Gizmo current = <>7__wrap1.Current;
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = null;
						if (((Thing)((ThingComp)CS$<>8__locals27).parent).Faction == Faction.OfPlayer)
						{
							<>2__current = (Gizmo)(object)new Gizmo_ShieldStatus
							{
								shield = CS$<>8__locals27
							};
							<>1__state = 2;
							return true;
						}
						goto IL_0341;
					}
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				if (<>7__wrap1 != null)
				{
					<>7__wrap1.Dispose();
				}
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
			{
				<CompGetGizmosExtra>d__79 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <CompGetGizmosExtra>d__79(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		private int lastInterceptTicks = -999999;

		private int lastHitByEmpTicks = -999999;

		private float lastInterceptAngle;

		private bool debugInterceptNonHostileProjectiles = true;

		private static readonly Material ForceFieldMat = MaterialPool.MatFrom("Other/ForceField", ShaderDatabase.MoteGlow);

		private static readonly Material ForceFieldConeMat = MaterialPool.MatFrom("Other/ForceFieldCone", ShaderDatabase.MoteGlow);

		private static readonly MaterialPropertyBlock MatPropertyBlock = new MaterialPropertyBlock();

		private static readonly Color InactiveColor = new Color(0.2f, 0.2f, 0.2f);

		private bool showShieldToggle;

		public float CurStressLevel;

		public float MaxStressLevel = 1f;

		public int ticksToReset;

		public bool overloaded;

		public bool activeLastTick;

		public int shieldOffsetX;

		public int shieldOffsetY;

		public int curShieldRadius = -1;

		private CompPowerTrader cachedPowerComp;

		private CompFlickable cachedFlickableComp;

		private CompHeatPusher cachedHeatComp;

		private CompRefuelable cachedFuelComp;

		public float lastTempChange;

		public Color currentColor;

		public Rot4 lastCheckedRotation;

		public CompProperties_Shield Props => (CompProperties_Shield)(object)base.props;

		public virtual bool Active
		{
			get
			{
				if (!overloaded && (PowerTrader == null || PowerTrader.PowerOn) && (FuelComp == null || FuelComp.HasFuel))
				{
					if (Flicker != null)
					{
						return Flicker.SwitchIsOn;
					}
					return true;
				}
				return false;
			}
		}

		public Vector3 CurShieldPosition
		{
			get
			{
				//IL_0006: Unknown result type (might be due to invalid IL or missing references)
				//IL_001d: Unknown result type (might be due to invalid IL or missing references)
				//IL_002d: Unknown result type (might be due to invalid IL or missing references)
				//IL_003e: Unknown result type (might be due to invalid IL or missing references)
				//IL_0043: Unknown result type (might be due to invalid IL or missing references)
				//IL_0046: Unknown result type (might be due to invalid IL or missing references)
				IntVec3 val = new IntVec3(((Thing)base.parent).Position.x + shieldOffsetX, ((Thing)base.parent).Position.y, ((Thing)base.parent).Position.z + shieldOffsetY);
				return ((IntVec3)(ref val)).ToVector3Shifted();
			}
		}

		public int SetShieldRadius
		{
			get
			{
				return curShieldRadius;
			}
			set
			{
				curShieldRadius = Mathf.Clamp(value, Props.shieldScaleLimits.min, Props.shieldScaleLimits.max);
			}
		}

		public int SetShieldOffsetX
		{
			get
			{
				return shieldOffsetX;
			}
			set
			{
				shieldOffsetX = value;
			}
		}

		public int SetShieldOffsetY
		{
			get
			{
				return shieldOffsetY;
			}
			set
			{
				shieldOffsetY = value;
			}
		}

		public bool HasPowerTrader => PowerTrader != null;

		public bool ReactivatedThisTick => Find.TickManager.TicksGame - lastInterceptTicks == Props.resetTime;

		public float ScaleDamageFactor => Mathf.Lerp(0.5f, 2f, GetShieldScalePercentage);

		public float GetShieldScalePercentage
		{
			get
			{
				if (!Props.shieldCanBeScaled)
				{
					return 1f;
				}
				return Mathf.InverseLerp((float)Props.shieldScaleLimits.min, (float)Props.shieldScaleLimits.max, (float)curShieldRadius);
			}
		}

		public CompPowerTrader PowerTrader
		{
			get
			{
				if (cachedPowerComp == null)
				{
					cachedPowerComp = base.parent.GetComp<CompPowerTrader>();
				}
				return cachedPowerComp;
			}
		}

		public CompFlickable Flicker
		{
			get
			{
				if (cachedFlickableComp == null)
				{
					cachedFlickableComp = base.parent.GetComp<CompFlickable>();
				}
				return cachedFlickableComp;
			}
		}

		public CompHeatPusher HeatComp
		{
			get
			{
				if (cachedHeatComp == null)
				{
					cachedHeatComp = base.parent.GetComp<CompHeatPusher>();
				}
				return cachedHeatComp;
			}
		}

		public CompRefuelable FuelComp
		{
			get
			{
				if (cachedFuelComp == null)
				{
					cachedFuelComp = base.parent.GetComp<CompRefuelable>();
				}
				return cachedFuelComp;
			}
		}

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			//IL_0079: Unknown result type (might be due to invalid IL or missing references)
			//IL_0080: Unknown result type (might be due to invalid IL or missing references)
			//IL_008b: Unknown result type (might be due to invalid IL or missing references)
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
			if (!ModLister.CheckRoyalty("Projectile interception"))
			{
				LogUtil.Message("Shield Setup skipped because user lacks Royalty.");
				((Thing)base.parent).Destroy((DestroyMode)0);
				return;
			}
			((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
			if (curShieldRadius < Props.shieldScaleLimits.min)
			{
				SetShieldRadius = Props.shieldScaleDefault;
			}
			if (!respawningAfterLoad)
			{
				currentColor = Props.shieldColour;
				SetShieldRadius = Props.shieldScaleDefault;
			}
			_ = lastCheckedRotation;
			if (lastCheckedRotation != ((Thing)base.parent).Rotation)
			{
				CorrectShieldOffsets();
			}
			else
			{
				lastCheckedRotation = ((Thing)base.parent).Rotation;
			}
			((Thing)base.parent).Map.GetComponent<MapComp_ShieldList>().shieldGenList.Add(base.parent);
		}

		public void CorrectShieldOffsets()
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			//IL_0028: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0052: Unknown result type (might be due to invalid IL or missing references)
			IntVec3 val = IntVec3Utility.RotatedBy(new IntVec3(shieldOffsetX, 0, shieldOffsetY), Rot4.GetRelativeRotation(lastCheckedRotation, ((Thing)base.parent).Rotation));
			shieldOffsetX = val.x;
			shieldOffsetY = val.z;
			lastCheckedRotation = ((Thing)base.parent).Rotation;
		}

		public bool CheckIntercept(Skyfaller skyfaller)
		{
			if (HoldsAnyHostiles(skyfaller))
			{
				return ShouldBeBlocked(skyfaller);
			}
			return false;
		}

		public bool HoldsAnyHostiles(Skyfaller skyfaller)
		{
			foreach (Thing item in (IEnumerable<Thing>)skyfaller.GetDirectlyHeldThings())
			{
				Pawn val = (Pawn)(object)((item is Pawn) ? item : null);
				if (val != null && GenHostility.HostileTo((Thing)(object)val, Faction.OfPlayer))
				{
					if (!val.IsSlaveOfColony && !val.IsPrisonerOfColony)
					{
						return true;
					}
					continue;
				}
				Building val2 = (Building)(object)((item is Building) ? item : null);
				if (val2 != null && (GenHostility.HostileTo((Thing)(object)val2, Faction.OfPlayer) || ((Thing)val2).Faction == Faction.OfMechanoids))
				{
					return true;
				}
			}
			DropPodIncoming val3 = (DropPodIncoming)(object)((skyfaller is DropPodIncoming) ? skyfaller : null);
			if (val3 != null && HoldsAnyHostiles(val3))
			{
				return true;
			}
			return false;
		}

		public bool HoldsAnyHostiles(DropPodIncoming pod)
		{
			Faction faction = ((Thing)pod).Faction;
			if (faction != null && FactionUtility.HostileTo(faction, Faction.OfPlayer))
			{
				return true;
			}
			foreach (Thing item in (IEnumerable<Thing>)pod.Contents.GetDirectlyHeldThings())
			{
				Pawn val = (Pawn)(object)((item is Pawn) ? item : null);
				if (val != null && GenHostility.HostileTo((Thing)(object)val, Faction.OfPlayer))
				{
					if (!val.IsSlaveOfColony && !val.IsPrisonerOfColony)
					{
						return true;
					}
					continue;
				}
				Building val2 = (Building)(object)((item is Building) ? item : null);
				if (val2 != null && (GenHostility.HostileTo((Thing)(object)val2, Faction.OfPlayer) || ((Thing)val2).Faction == Faction.OfMechanoids))
				{
					return true;
				}
			}
			return false;
		}

		public bool ShouldBeBlocked(Skyfaller skyfaller)
		{
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0052: Unknown result type (might be due to invalid IL or missing references)
			if (!GenList.NullOrEmpty<Type>((IList<Type>)Props.skyfallerClassWhitelist) && Props.skyfallerClassWhitelist.Contains(((Thing)skyfaller).def.thingClass))
			{
				return false;
			}
			if (Active && Props.podBlocker && IntVec3Utility.DistanceTo(((Thing)skyfaller).Position, IntVec3Utility.ToIntVec3(CurShieldPosition)) <= (float)curShieldRadius)
			{
				return true;
			}
			return false;
		}

		public bool BombardmentCanStartFireAt(Bombardment bombardment, IntVec3 cell)
		{
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			if (Active && Props.interceptAirProjectiles && ((((OrbitalStrike)bombardment).instigator != null && GenHostility.HostileTo(((OrbitalStrike)bombardment).instigator, (Thing)(object)base.parent)) || debugInterceptNonHostileProjectiles || Props.interceptNonHostileProjectiles))
			{
				return !((IntVec3)(ref cell)).InHorDistOf(((Thing)base.parent).Position, (float)curShieldRadius);
			}
			return true;
		}

		public bool CheckIntercept(Projectile projectile, Vector3 lastExactPos, Vector3 newExactPos)
		{
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_005c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Unknown result type (might be due to invalid IL or missing references)
			//IL_010c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0112: Unknown result type (might be due to invalid IL or missing references)
			//IL_0118: Unknown result type (might be due to invalid IL or missing references)
			//IL_0124: Unknown result type (might be due to invalid IL or missing references)
			//IL_012a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0130: Unknown result type (might be due to invalid IL or missing references)
			//IL_0135: Unknown result type (might be due to invalid IL or missing references)
			//IL_013b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0141: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
			//IL_0150: Unknown result type (might be due to invalid IL or missing references)
			//IL_0157: Unknown result type (might be due to invalid IL or missing references)
			//IL_019e: Unknown result type (might be due to invalid IL or missing references)
			//IL_019f: Unknown result type (might be due to invalid IL or missing references)
			if (!ModLister.CheckRoyalty("Projectile interception"))
			{
				return false;
			}
			Vector3 curShieldPosition = CurShieldPosition;
			float num = (float)curShieldRadius + ((Thing)projectile).def.projectile.SpeedTilesPerTick + 0.1f;
			if ((newExactPos.x - curShieldPosition.x) * (newExactPos.x - curShieldPosition.x) + (newExactPos.z - curShieldPosition.z) * (newExactPos.z - curShieldPosition.z) > num * num)
			{
				return false;
			}
			if (!Active)
			{
				return false;
			}
			if (!InterceptsProjectile(Props, projectile))
			{
				return false;
			}
			if ((projectile.Launcher == null || !GenHostility.HostileTo(projectile.Launcher, (Thing)(object)base.parent)) && !debugInterceptNonHostileProjectiles && Props.interceptNonHostileProjectiles)
			{
				return false;
			}
			if (!Props.interceptOutgoingProjectiles)
			{
				Vector2 val = new Vector2(curShieldPosition.x, curShieldPosition.z) - new Vector2(lastExactPos.x, lastExactPos.z);
				if (((Vector2)(ref val)).sqrMagnitude <= (float)(curShieldRadius * curShieldRadius))
				{
					return false;
				}
			}
			if (!GenGeo.IntersectLineCircleOutline(new Vector2(curShieldPosition.x, curShieldPosition.z), (float)curShieldRadius, new Vector2(lastExactPos.x, lastExactPos.z), new Vector2(newExactPos.x, newExactPos.z)))
			{
				return false;
			}
			lastInterceptAngle = Vector3Utility.AngleToFlat(lastExactPos, GenThing.TrueCenter((Thing)(object)base.parent));
			lastInterceptTicks = Find.TickManager.TicksGame;
			if (((Thing)projectile).def.projectile.damageDef == DamageDefOf.EMP)
			{
				lastHitByEmpTicks = Find.TickManager.TicksGame;
			}
			TriggerEffecter(IntVec3Utility.ToIntVec3(newExactPos));
			UpdateStress(projectile);
			return true;
		}

		public static bool InterceptsProjectile(CompProperties_Shield props, Projectile projectile)
		{
			if (props.interceptGroundProjectiles && !((Thing)projectile).def.projectile.flyOverhead)
			{
				return true;
			}
			if (props.interceptAirProjectiles && ((Thing)projectile).def.projectile.flyOverhead)
			{
				return true;
			}
			return false;
		}

		public void TriggerEffecter(IntVec3 pos)
		{
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_000a: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			Effecter val = new Effecter(EffecterDefOf.Interceptor_BlockedProjectile);
			val.Trigger(new TargetInfo(pos, ((Thing)base.parent).Map, false), TargetInfo.Invalid, -1);
			val.Cleanup();
		}

		public void UpdateStress(bool tickUpdate = false, bool cooling = false)
		{
			if (tickUpdate)
			{
				float num = 0f;
				num = ((!Props.useAmbientCooling) ? (num - Props.stressReduction) : ((!(((Thing)base.parent).AmbientTemperature > Props.maximumHeatLevel) || cooling) ? (num - Props.stressReduction) : (num + Props.stressReduction)));
				if (!Active)
				{
					num = 0f - Props.stressReduction;
				}
				lastTempChange = num * 0.01f / 60f;
				CurStressLevel = Mathf.Clamp(CurStressLevel + lastTempChange, 0f, MaxStressLevel);
			}
			if (CurStressLevel >= MaxStressLevel)
			{
				OverloadShield();
			}
		}

		public void UpdateStress(Projectile projectile)
		{
			float num = (float)projectile.DamageAmount * Props.stressPerDamage / 100f;
			if (((Thing)projectile).def.projectile.damageDef == DamageDefOf.EMP)
			{
				num *= Props.empDamageFactor;
			}
			CurStressLevel = Mathf.Clamp(CurStressLevel + num * ScaleDamageFactor, 0f, MaxStressLevel);
			UpdateStress();
		}

		public void UpdateStress(Skyfaller skyfaller)
		{
			float num = 30000f * Props.stressPerDamage / 100f;
			if (skyfaller is DropPodIncoming)
			{
				num /= 3f;
			}
			CurStressLevel = Mathf.Clamp(CurStressLevel + num * ScaleDamageFactor, 0f, MaxStressLevel);
			UpdateStress();
		}

		public void OverloadShield()
		{
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_0068: Unknown result type (might be due to invalid IL or missing references)
			//IL_0079: Unknown result type (might be due to invalid IL or missing references)
			//IL_008d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0092: Unknown result type (might be due to invalid IL or missing references)
			if (Props.breakSound != null)
			{
				SoundStarter.PlayOneShot(Props.breakSound, SoundInfo.op_Implicit(new TargetInfo(((Thing)base.parent).Position, ((Thing)base.parent).Map, false)));
			}
			FleckMaker.ThrowExplosionInterior(GenThing.TrueCenter((Thing)(object)base.parent), ((Thing)base.parent).Map, FleckDefOf.ExplosionFlash);
			for (int i = 0; i < 6; i++)
			{
				FleckMaker.ThrowDustPuff(GenThing.TrueCenter((Thing)(object)base.parent) + Vector3Utility.HorizontalVectorFromAngle((float)Rand.Range(0, 360)) * Rand.Range(0.3f, 0.6f), ((Thing)base.parent).Map, Rand.Range(0.8f, 1.2f));
			}
			ticksToReset = Props.resetTime;
			overloaded = true;
			CurStressLevel = 0f;
			if (Props.explodeOnCollapse && ThingCompUtility.TryGetComp<CompExplosive>((Thing)(object)base.parent) != null)
			{
				ThingCompUtility.TryGetComp<CompExplosive>((Thing)(object)base.parent).StartWick((Thing)null);
			}
		}

		public void UpdatePowerUsage()
		{
			if (Active)
			{
				PowerTrader.PowerOutput = Mathf.Lerp(Props.powerUsageRange.min, Props.powerUsageRange.max, GetShieldScalePercentage);
			}
			else
			{
				PowerTrader.PowerOutput = 0f;
			}
		}

		public override void CompTick()
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_005c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0061: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
			//IL_00df: Unknown result type (might be due to invalid IL or missing references)
			_ = lastCheckedRotation;
			if (lastCheckedRotation != ((Thing)base.parent).Rotation)
			{
				CorrectShieldOffsets();
			}
			if (Active)
			{
				if (ReactivatedThisTick && Props.reactivateEffect != null)
				{
					Effecter val = new Effecter(Props.reactivateEffect);
					val.Trigger(TargetInfo.op_Implicit((Thing)(object)base.parent), TargetInfo.Invalid, -1);
					val.Cleanup();
				}
				UpdateStress(tickUpdate: true);
				if (CurStressLevel >= Props.shieldOverloadThreshold && Rand.Chance(Props.shieldOverloadChance * (1f - (1f - CurStressLevel) * 10f)))
				{
					CellRect val2 = GenAdj.OccupiedRect((Thing)(object)base.parent);
					val2 = ((CellRect)(ref val2)).ExpandedBy(Props.extraOverloadRange);
					GenExplosion.DoExplosion(((CellRect)(ref val2)).RandomCell, ((Thing)base.parent).Map, 1.9f, DamageDefOf.EMP, (Thing)null, -1, -1f, (SoundDef)null, (ThingDef)null, (ThingDef)null, (Thing)null, (ThingDef)null, 0f, 1, (GasType?)null, (float?)null, 255, false, (ThingDef)null, 0f, 1, 0f, false, (float?)null, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
				}
			}
			UpdateStress(tickUpdate: true);
			if (PowerTrader != null)
			{
				UpdatePowerUsage();
				if (overloaded && PowerTrader.PowerOn)
				{
					ticksToReset--;
					if (ticksToReset <= 0)
					{
						overloaded = false;
					}
				}
			}
			if (HeatComp != null)
			{
				UpdateHeatPusher();
			}
		}

		public void UpdateHeatPusher()
		{
			if (Active)
			{
				HeatComp.Props.heatPerSecond = Mathf.Lerp(Props.heatGenRange.min, Props.heatGenRange.max, CurStressLevel);
			}
			else
			{
				HeatComp.Props.heatPerSecond = 0f;
			}
		}

		public override void PostDraw()
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
			//IL_0100: Unknown result type (might be due to invalid IL or missing references)
			//IL_0109: Unknown result type (might be due to invalid IL or missing references)
			//IL_0111: Unknown result type (might be due to invalid IL or missing references)
			//IL_0128: Unknown result type (might be due to invalid IL or missing references)
			//IL_0158: Unknown result type (might be due to invalid IL or missing references)
			//IL_0167: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_006c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0074: Unknown result type (might be due to invalid IL or missing references)
			//IL_007c: Unknown result type (might be due to invalid IL or missing references)
			//IL_007d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			((ThingComp)this).PostDraw();
			Vector3 curShieldPosition = CurShieldPosition;
			curShieldPosition.y = Altitudes.AltitudeFor((AltitudeLayer)28);
			float currentAlpha = GetCurrentAlpha();
			if (currentAlpha > 0f)
			{
				Color val = ((!Active && Find.Selector.IsSelected((object)base.parent)) ? InactiveColor : currentColor);
				val.a *= currentAlpha;
				MatPropertyBlock.SetColor(ShaderPropertyIDs.Color, val);
				Matrix4x4 val2 = default(Matrix4x4);
				((Matrix4x4)(ref val2)).SetTRS(curShieldPosition, Quaternion.identity, new Vector3((float)curShieldRadius * 2f * 1.1601562f, 1f, (float)curShieldRadius * 2f * 1.1601562f));
				Graphics.DrawMesh(MeshPool.plane10, val2, ForceFieldMat, 0, (Camera)null, 0, MatPropertyBlock);
			}
			float currentConeAlpha_RecentlyIntercepted = GetCurrentConeAlpha_RecentlyIntercepted();
			if (currentConeAlpha_RecentlyIntercepted > 0f)
			{
				Color val3 = currentColor;
				val3.a *= currentConeAlpha_RecentlyIntercepted;
				MatPropertyBlock.SetColor(ShaderPropertyIDs.Color, val3);
				Matrix4x4 val4 = default(Matrix4x4);
				((Matrix4x4)(ref val4)).SetTRS(curShieldPosition, Quaternion.Euler(0f, lastInterceptAngle - 90f, 0f), new Vector3((float)curShieldRadius * 2f * 1.1601562f, 1f, (float)curShieldRadius * 2f * 1.1601562f));
				Graphics.DrawMesh(MeshPool.plane10, val4, ForceFieldConeMat, 0, (Camera)null, 0, MatPropertyBlock);
			}
		}

		private float GetCurrentAlpha()
		{
			return Mathf.Max(Mathf.Max(Mathf.Max(Mathf.Max(GetCurrentAlpha_Idle(), GetCurrentAlpha_Selected()), GetCurrentAlpha_RecentlyIntercepted()), GetCurrentAlpha_RecentlyActivated()), Props.minAlpha);
		}

		private float GetCurrentAlpha_Idle()
		{
			if (!Active)
			{
				return 0f;
			}
			if (((Thing)base.parent).Faction == Faction.OfPlayer && !debugInterceptNonHostileProjectiles)
			{
				return 0f;
			}
			if (Find.Selector.IsSelected((object)base.parent))
			{
				return 0f;
			}
			if (showShieldToggle)
			{
				float num = Mathf.Max(2f, Props.idlePulseSpeed);
				return Mathf.Lerp(0.2f, 0.62f, (Mathf.Sin((float)(Gen.HashCombineInt(((Thing)base.parent).thingIDNumber, 35990913) % 100) + Time.realtimeSinceStartup * num) + 1f) / 2f);
			}
			return Mathf.Lerp(-1.7f, 0.11f, (Mathf.Sin((float)(Gen.HashCombineInt(((Thing)base.parent).thingIDNumber, 96804938) % 100) + Time.realtimeSinceStartup * 0.7f) + 1f) / 2f);
		}

		private float GetCurrentAlpha_Selected()
		{
			float num = Mathf.Max(2f, Props.idlePulseSpeed);
			if (!Find.Selector.IsSelected((object)base.parent))
			{
				return 0f;
			}
			if (!Active)
			{
				return 0.41f;
			}
			return Mathf.Lerp(0.2f, 0.62f, (Mathf.Sin((float)(Gen.HashCombineInt(((Thing)base.parent).thingIDNumber, 35990913) % 100) + Time.realtimeSinceStartup * num) + 1f) / 2f);
		}

		public float GetCurrentAlpha_RecentlyIntercepted()
		{
			int num = Find.TickManager.TicksGame - lastInterceptTicks;
			return Mathf.Clamp01(1f - (float)num / 40f) * 0.09f;
		}

		public float GetCurrentAlpha_RecentlyActivated()
		{
			if (!Active)
			{
				return 0f;
			}
			int num = Find.TickManager.TicksGame - (lastInterceptTicks + Props.resetTime);
			return Mathf.Clamp01(1f - (float)num / 50f) * 0.09f;
		}

		public float GetCurrentConeAlpha_RecentlyIntercepted()
		{
			if (!Props.drawInterceptCone)
			{
				return 0f;
			}
			int num = Find.TickManager.TicksGame - lastInterceptTicks;
			return Mathf.Clamp01(1f - (float)num / 40f) * 0.82f;
		}

		[IteratorStateMachine(typeof(<CompGetGizmosExtra>d__79))]
		public override IEnumerable<Gizmo> CompGetGizmosExtra()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <CompGetGizmosExtra>d__79(-2)
			{
				<>4__this = this
			};
		}

		public override string CompInspectStringExtra()
		{
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			StringBuilder stringBuilder = new StringBuilder();
			if (Active)
			{
				if (ticksToReset > 0)
				{
					stringBuilder.Append(TaggedString.op_Implicit(Translator.Translate("CooldownTime") + ": " + GenDate.ToStringTicksToPeriod(ticksToReset, true, false, true, true, false)));
				}
				else
				{
					stringBuilder.Append("Shield Active");
				}
			}
			else
			{
				stringBuilder.Append("Shield Inactive");
			}
			return stringBuilder.ToString();
		}

		public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			((ThingComp)this).PostPostApplyDamage(dinfo, totalDamageDealt);
			if (((DamageInfo)(ref dinfo)).Def == DamageDefOf.EMP)
			{
				lastHitByEmpTicks = Find.TickManager.TicksGame;
			}
		}

		public override void PostExposeData()
		{
			//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
			//IL_010f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0115: Unknown result type (might be due to invalid IL or missing references)
			((ThingComp)this).PostExposeData();
			Scribe_Values.Look<int>(ref lastInterceptTicks, "lastInterceptTicks", -999999, false);
			Scribe_Values.Look<int>(ref lastHitByEmpTicks, "lastHitByEmpTicks", -999999, false);
			Scribe_Values.Look<bool>(ref showShieldToggle, "showShieldToggle", false, false);
			Scribe_Values.Look<float>(ref CurStressLevel, "curStressLevel", 0f, false);
			Scribe_Values.Look<float>(ref MaxStressLevel, "maxStressLevel", 1f, false);
			Scribe_Values.Look<int>(ref ticksToReset, "ticksToReset", -1, false);
			Scribe_Values.Look<bool>(ref overloaded, "overloaded", false, false);
			Scribe_Values.Look<bool>(ref activeLastTick, "activeLastTick", false, false);
			Scribe_Values.Look<int>(ref shieldOffsetX, "shieldOffsetX", 0, false);
			Scribe_Values.Look<int>(ref shieldOffsetY, "shieldOffsetY", 0, false);
			Scribe_Values.Look<int>(ref curShieldRadius, "curShieldRadius", Props.shieldScaleDefault, false);
			Scribe_Values.Look<Color>(ref currentColor, "currentColor", Props.shieldColour, false);
			Scribe_Values.Look<Rot4>(ref lastCheckedRotation, "lastCheckedRotation", default(Rot4), false);
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private IEnumerable<Gizmo> <>n__0()
		{
			return ((ThingComp)this).CompGetGizmosExtra();
		}
	}
	public class Comp_RandomSounds : ThingComp
	{
		public int nextTick = -1;

		public CompPowerTrader powerComp;

		public CompProperties_RandomSounds Props => (CompProperties_RandomSounds)(object)base.props;

		public bool IsPowered
		{
			get
			{
				if (powerComp != null)
				{
					return powerComp.PowerOn;
				}
				return true;
			}
		}

		public override void PostExposeData()
		{
			((ThingComp)this).PostExposeData();
			Scribe_Values.Look<int>(ref nextTick, "nextTick", -1, false);
		}

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
			powerComp = base.parent.GetComp<CompPowerTrader>();
		}

		public void CheckTick()
		{
			if (IsPowered && Find.TickManager.TicksGame > nextTick)
			{
				PlayRandomSound();
				nextTick = Find.TickManager.TicksGame + ((IntRange)(ref Props.tickRange)).RandomInRange;
			}
		}

		public void PlayRandomSound()
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			SoundStarter.PlayOneShot(GenCollection.RandomElement<SoundDef>((IEnumerable<SoundDef>)Props.soundDefs), SoundInfo.op_Implicit((Thing)(object)base.parent));
		}

		public override void CompTick()
		{
			((ThingComp)this).CompTick();
			CheckTick();
		}

		public override void CompTickLong()
		{
			((ThingComp)this).CompTickLong();
			CheckTick();
		}

		public override void CompTickRare()
		{
			((ThingComp)this).CompTickRare();
			CheckTick();
		}
	}
	public class DamageWorker_AdvExt : DamageWorker_AddInjury
	{
		public override DamageResult Apply(DamageInfo dinfo, Thing thing)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_002e: Unknown result type (might be due to invalid IL or missing references)
			DamageResult val = ((DamageWorker_AddInjury)this).Apply(dinfo, thing);
			DefModExt_DamageAdv modExtension = ((Def)((DamageInfo)(ref dinfo)).Def).GetModExtension<DefModExt_DamageAdv>();
			if (modExtension != null && modExtension.hediff != null)
			{
				Pawn val2 = (Pawn)(object)((thing is Pawn) ? thing : null);
				if (val2 != null)
				{
					ApplyHediffToPawn(val2, modExtension, dinfo, val);
				}
			}
			return val;
		}

		public void ApplyHediffToPawn(Pawn pawn, DefModExt_DamageAdv ext, DamageInfo dinfo, DamageResult damage)
		{
			//IL_0084: Unknown result type (might be due to invalid IL or missing references)
			//IL_014b: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
			FleshTypeDef fleshTypeToAffect = ext.fleshTypeToAffect;
			if (fleshTypeToAffect != null && fleshTypeToAffect != pawn.RaceProps.FleshType)
			{
				return;
			}
			Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(ext.hediff, false);
			if (firstHediffOfDef != null)
			{
				if (ext.increaseSevPerShot > 0f)
				{
					firstHediffOfDef.Severity += ext.increaseSevPerShot;
				}
				return;
			}
			if (ext.wholeBody)
			{
				Hediff val = HediffMaker.MakeHediff(ext.hediff, pawn, (BodyPartRecord)null);
				val.Severity = ext.hediffSev;
				pawn.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)dinfo, (DamageResult)null);
				return;
			}
			if (ext.bodyPart != null)
			{
				foreach (BodyPartRecord item in pawn.RaceProps.body.GetPartsWithDef(ext.bodyPart))
				{
					Hediff val2 = HediffMaker.MakeHediff(ext.hediff, pawn, item);
					val2.Severity = ext.hediffSev;
					pawn.health.AddHediff(val2, item, (DamageInfo?)dinfo, (DamageResult)null);
				}
				return;
			}
			foreach (BodyPartRecord part in damage.parts)
			{
				Hediff val3 = HediffMaker.MakeHediff(ext.hediff, pawn, part);
				val3.Severity = ext.hediffSev;
				pawn.health.AddHediff(val3, part, (DamageInfo?)dinfo, (DamageResult)null);
			}
		}
	}
	public class IngestionOutcomeDoer_GiveHediffAdv : IngestionOutcomeDoer
	{
		public List<AdditionalHediffEntry> hediffDefs = new List<AdditionalHediffEntry>();

		public bool randomChosen;

		public override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
		{
			if (randomChosen)
			{
				TryAddHediffFromEntry(pawn, GenCollection.RandomElementByWeight<AdditionalHediffEntry>((IEnumerable<AdditionalHediffEntry>)hediffDefs, (Func<AdditionalHediffEntry, float>)((AdditionalHediffEntry x) => x.weight)));
				return;
			}
			foreach (AdditionalHediffEntry hediffDef in hediffDefs)
			{
				TryAddHediffFromEntry(pawn, hediffDef);
			}
		}

		public void TryAddHediffFromEntry(Pawn pawn, AdditionalHediffEntry entry)
		{
			Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(entry.hediff, false);
			if (firstHediffOfDef == null)
			{
				Hediff val = HediffMaker.MakeHediff(entry.hediff, pawn, (BodyPartRecord)null);
				val.Severity = ((FloatRange)(ref entry.severityRange)).RandomInRange;
				pawn.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
			else if (firstHediffOfDef.Severity < entry.severityRange.min)
			{
				firstHediffOfDef.Severity = ((FloatRange)(ref entry.severityRange)).RandomInRange;
			}
		}
	}
	public class DefModExt_NeedProvider : DefModExtension
	{
		public SoundDef entrySound;

		public SoundDef exitSound;

		public bool guestsAllowed = true;

		public List<NeedProviderOption> needs = new List<NeedProviderOption>();

		public bool storePawnWhenIdle;
	}
	public class DefModExt_EMPShielding : DefModExtension
	{
	}
	[HarmonyPatch(typeof(Skyfaller), "Tick")]
	public class Patch_Skyfaller_Tick
	{
		[HarmonyPrefix]
		public static bool Prefix(Skyfaller __instance)
		{
			//IL_0069: Unknown result type (might be due to invalid IL or missing references)
			//IL_0075: Unknown result type (might be due to invalid IL or missing references)
			//IL_007a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0085: Unknown result type (might be due to invalid IL or missing references)
			//IL_009e: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
			if (((Thing)__instance).Map != null && __instance.ticksToImpact == 20)
			{
				Faction faction = ((Thing)__instance).Faction;
				if (faction == null || FactionUtility.HostileTo(faction, Faction.OfPlayer))
				{
					List<ThingWithComps> shieldGenList = ((Thing)__instance).Map.GetComponent<MapComp_ShieldList>().shieldGenList;
					for (int i = 0; i < shieldGenList.Count; i++)
					{
						if (!ThingCompUtility.TryGetComp<Comp_Shield>((Thing)(object)shieldGenList[i]).CheckIntercept(__instance))
						{
							continue;
						}
						SoundStarter.PlayOneShot(SoundDefOf.EnergyShield_AbsorbDamage, SoundInfo.op_Implicit(new TargetInfo(((Thing)__instance).Position, ((Thing)__instance).Map, false)));
						foreach (IntVec3 item in ((IEnumerable<IntVec3>)(object)GenAdj.OccupiedRect((Thing)(object)__instance)).ToList())
						{
							IntVec3 current = item;
							FleckMaker.ThrowHeatGlow(current, ((Thing)__instance).Map, 1f);
							FleckMaker.ThrowLightningGlow(((IntVec3)(ref current)).ToVector3Shifted(), ((Thing)__instance).Map, 1f);
							FleckMaker.Static(current, ((Thing)__instance).Map, DefDatabase<FleckDef>.GetNamed("ElectricalSpark", true), 2f);
							FleckMaker.Static(current, ((Thing)__instance).Map, DefDatabase<FleckDef>.GetNamed("PsycastPsychicEffect", true), 2f);
						}
						((Thing)__instance).Destroy((DestroyMode)2);
						return false;
					}
				}
			}
			return true;
		}
	}
	[HarmonyPatch(typeof(Projectile), "CheckForFreeInterceptBetween")]
	public class Patch_Projectile_CheckForFreeInterceptBetween
	{
		[HarmonyPostfix]
		public static void Postfix(Projectile __instance, ref bool __result, Vector3 lastExactPos, Vector3 newExactPos)
		{
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			if (__result)
			{
				return;
			}
			List<ThingWithComps> shieldGenList = ((Thing)__instance).Map.GetComponent<MapComp_ShieldList>().shieldGenList;
			for (int i = 0; i < shieldGenList.Count; i++)
			{
				if (ThingCompUtility.TryGetComp<Comp_Shield>((Thing)(object)shieldGenList[i]).CheckIntercept(__instance, lastExactPos, newExactPos))
				{
					((Thing)__instance).Destroy((DestroyMode)0);
					__result = true;
					break;
				}
			}
		}
	}
	public class DefModExt_DamageAdv : DefModExtension
	{
		public FleshTypeDef fleshTypeToAffect;

		public HediffDef hediff;

		public float hediffSev;

		public float increaseSevPerShot;

		public bool stunPawn;

		public bool wholeBody;

		public BodyPartDef bodyPart;
	}
	public class NeedProviderOption
	{
		public NeedDef need;

		public bool usesPower;

		public bool usesNutrition;

		public float efficiency = 1f;
	}
	public class PawnGroupMaker_PollutionExact : PawnGroupMaker
	{
		public PollutionLevel pollutionLevel;

		public bool CanGenerate(PawnGroupMakerParms parms)
		{
			//IL_000a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			if (PollutionUtility.PollutionLevel(Find.CurrentMap.TileInfo) == pollutionLevel)
			{
				return true;
			}
			return false;
		}
	}
	public class PawnGroupMaker_Pollution : PawnGroupMaker
	{
		public PollutionLevel pollutionLevel;

		public bool CanGenerate(PawnGroupMakerParms parms)
		{
			//IL_000a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			if (PollutionUtility.PollutionLevel(Find.CurrentMap.TileInfo) >= pollutionLevel)
			{
				return true;
			}
			return false;
		}
	}
	public class PlaceWorker_ShowShieldRadius : PlaceWorker
	{
		public override void DrawGhost(ThingDef def, IntVec3 center, Rot4 rot, Color ghostCol, Thing thing = null)
		{
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			CompProperties_Shield compProperties = def.GetCompProperties<CompProperties_Shield>();
			if (compProperties != null)
			{
				GenDraw.DrawCircleOutline(((IntVec3)(ref center)).ToVector3Shifted(), (float)compProperties.shieldScaleLimits.max, (SimpleColor)1);
				GenDraw.DrawCircleOutline(((IntVec3)(ref center)).ToVector3Shifted(), (float)compProperties.shieldScaleDefault, (SimpleColor)0);
				GenDraw.DrawCircleOutline(((IntVec3)(ref center)).ToVector3Shifted(), (float)compProperties.shieldScaleLimits.min, (SimpleColor)2);
			}
		}
	}
	[StaticConstructorOnStartup]
	public class Gizmo_ShieldStatus : Gizmo
	{
		public Comp_Shield shield;

		private static readonly Texture2D FullShieldBarTex = SolidColorMaterials.NewSolidColorTexture(new Color(0.2f, 0.2f, 0.24f));

		private static readonly Texture2D EmptyShieldBarTex = SolidColorMaterials.NewSolidColorTexture(Color.clear);

		public Gizmo_ShieldStatus()
		{
			base.order = -100f;
		}

		public override float GetWidth(float maxWidth)
		{
			return 140f;
		}

		public override GizmoResult GizmoOnGUI(Vector2 topLeft, float maxWidth, GizmoRenderParms parms)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0031: Unknown result type (might be due to invalid IL or missing references)
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0063: Unknown result type (might be due to invalid IL or missing references)
			//IL_0064: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
			//IL_0119: Unknown result type (might be due to invalid IL or missing references)
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(topLeft.x, topLeft.y, ((Gizmo)this).GetWidth(maxWidth), 75f);
			Rect val2 = GenUI.ContractedBy(val, 6f);
			Widgets.DrawWindowBackground(val);
			Rect val3 = val2;
			((Rect)(ref val3)).height = ((Rect)(ref val)).height / 2f;
			Text.Font = (GameFont)0;
			Widgets.Label(val3, shield.Props.stressLabel);
			Rect val4 = val2;
			((Rect)(ref val4)).yMin = ((Rect)(ref val2)).y + ((Rect)(ref val2)).height / 2f;
			float num = shield.CurStressLevel / Mathf.Max(1f, shield.MaxStressLevel);
			Widgets.FillableBar(val4, num, FullShieldBarTex, EmptyShieldBarTex, false);
			Text.Font = (GameFont)1;
			Text.Anchor = (TextAnchor)4;
			Widgets.Label(val4, (shield.CurStressLevel * 100f).ToString("F0") + " / " + (shield.MaxStressLevel * 100f).ToString("F0"));
			Text.Anchor = (TextAnchor)0;
			return new GizmoResult((GizmoState)0);
		}
	}
	public class MapComp_ShieldList : MapComponent
	{
		public List<ThingWithComps> shieldGenList = new List<ThingWithComps>();

		public IEnumerable<ThingWithComps> ActiveShieldGens => shieldGenList.Where((ThingWithComps shieldGen) => (ThingCompUtility.TryGetComp<Comp_Shield>((Thing)(object)shieldGen)?.Active).Value);

		public MapComp_ShieldList(Map map)
			: base(map)
		{
		}
	}
	public class DefModExt_OutputFromEdible : DefModExtension
	{
		public ThingDef outputThing;

		public float chance = 1f;

		public int multiplier = 1;

		public GeneDef geneRequired;
	}
	[HarmonyPatch(typeof(Thing), "Ingested")]
	public static class Patch_Thing_Ingested
	{
		[HarmonyPrefix]
		public static bool Prefix(ref Thing __instance, Pawn ingester, float nutritionWanted)
		{
			//IL_006c: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
			DefModExt_OutputFromEdible modExtension = ((Def)__instance.def).GetModExtension<DefModExt_OutputFromEdible>();
			if (modExtension != null && (modExtension.geneRequired == null || (ingester.genes.HasActiveGene(modExtension.geneRequired) && Rand.Chance(modExtension.chance))))
			{
				Thing val = ThingMaker.MakeThing(modExtension.outputThing, (ThingDef)null);
				if (modExtension.multiplier > 1)
				{
					val.stackCount *= modExtension.multiplier;
				}
				if (!GenPlace.TryPlaceThing(val, ((Thing)ingester).Position, ((Thing)ingester).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1))
				{
					Log.Error(string.Concat(ingester, " could not drop product ", val, " near ", ((Thing)ingester).Position));
				}
			}
			return true;
		}
	}
	public class Building_GraveAdv : Building_Grave
	{
		[CompilerGenerated]
		private sealed class <GetGizmos>d__19 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Building_GraveAdv <>4__this;

			private IEnumerable<Gizmo> <gizmos>5__2;

			private IEnumerator<Gizmo> <>7__wrap2;

			Gizmo IEnumerator<Gizmo>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <GetGizmos>d__19(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				switch (<>1__state)
				{
				case -3:
				case 1:
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
					break;
				case -4:
				case 2:
					try
					{
					}
					finally
					{
						<>m__Finally2();
					}
					break;
				}
				<gizmos>5__2 = null;
				<>7__wrap2 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
				try
				{
					int num = <>1__state;
					Building_GraveAdv building_GraveAdv = <>4__this;
					switch (num)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<gizmos>5__2 = building_GraveAdv.<>n__0();
						if (!building_GraveAdv.<>n__1() && building_GraveAdv.StorageTabVisible)
						{
							<>7__wrap2 = StorageSettingsClipboard.CopyPasteGizmosFor(((Building_CorpseCasket)building_GraveAdv).GetStoreSettings()).GetEnumerator();
							<>1__state = -3;
							goto IL_0093;
						}
						goto IL_00ad;
					case 1:
						<>1__state = -3;
						goto IL_0093;
					case 2:
						{
							<>1__state = -4;
							break;
						}
						IL_00ad:
						<>7__wrap2 = <gizmos>5__2.GetEnumerator();
						<>1__state = -4;
						break;
						IL_0093:
						if (<>7__wrap2.MoveNext())
						{
							Gizmo current = <>7__wrap2.Current;
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
						<>m__Finally1();
						<>7__wrap2 = null;
						goto IL_00ad;
					}
					while (<>7__wrap2.MoveNext())
					{
						Gizmo current2 = <>7__wrap2.Current;
						if (((Command)(((current2 is Command_Action) ? current2 : null)?)).defaultLabel != TaggedString.op_Implicit(Translator.Translate("CommandGraveAssignColonistLabel")))
						{
							<>2__current = current2;
							<>1__state = 2;
							return true;
						}
					}
					<>m__Finally2();
					<>7__wrap2 = null;
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				if (<>7__wrap2 != null)
				{
					<>7__wrap2.Dispose();
				}
			}

			private void <>m__Finally2()
			{
				<>1__state = -1;
				if (<>7__wrap2 != null)
				{
					<>7__wrap2.Dispose();
				}
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
			{
				<GetGizmos>d__19 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <GetGizmos>d__19(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		public int nextDissolveTick = -1;

		public DefModExt_GraveAdv modExt => ((Def)((Thing)this).def).GetModExtension<DefModExt_GraveAdv>();

		public int CorpseCount => ((Building_Casket)this).innerContainer.Count;

		public bool CanAcceptCorpses => CorpseCount < modExt.capacity;

		public int MaxAssignedPawnsCount => Math.Max(1, modExt.capacity - CorpseCount);

		public bool StorageTabVisible => CanAcceptCorpses;

		public override void ExposeData()
		{
			((Building_CorpseCasket)this).ExposeData();
			Scribe_Values.Look<int>(ref nextDissolveTick, "nextDissolveTick", 0, false);
		}

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			((Building_Casket)this).SpawnSetup(map, respawningAfterLoad);
			if (nextDissolveTick < 0)
			{
				ResetDissolveTimer();
			}
		}

		public override void TickRare()
		{
			((ThingWithComps)this).TickRare();
			if (nextDissolveTick < 0)
			{
				ResetDissolveTimer();
			}
			if (modExt.dissolveCorpses && nextDissolveTick < Find.TickManager.TicksGame)
			{
				DissolveFirstCorpse();
				ResetDissolveTimer();
			}
		}

		public void DissolveFirstCorpse()
		{
			if (CorpseCount > 0)
			{
				((IEnumerable<Thing>)((Building_Casket)this).innerContainer).First().Destroy((DestroyMode)0);
			}
		}

		public void ResetDissolveTimer()
		{
			nextDissolveTick = Find.TickManager.TicksGame + modExt.dissolveTicks;
		}

		public override bool Accepts(Thing thing)
		{
			if (!((Building_Casket)this).innerContainer.CanAcceptAnyOf(thing, true))
			{
				return false;
			}
			if (!CanAcceptCorpses)
			{
				return false;
			}
			if (((Building_Grave)this).AssignedPawn != null)
			{
				Corpse val = (Corpse)(object)((thing is Corpse) ? thing : null);
				if (val == null)
				{
					return false;
				}
				if (val.InnerPawn != ((Building_Grave)this).AssignedPawn)
				{
					return false;
				}
			}
			else if (!((Building_CorpseCasket)this).GetStoreSettings().AllowedToAccept(thing))
			{
				return false;
			}
			return true;
		}

		public override void Notify_HauledTo(Pawn worker, Thing thing, int count)
		{
			((Building_Grave)this).Notify_HauledTo(worker, thing, count);
			ResetDissolveTimer();
		}

		public override string GetInspectString()
		{
			StringBuilder stringBuilder = new StringBuilder();
			stringBuilder.Append(((ThingWithComps)this).InspectStringPartsFromComps());
			stringBuilder.Append("\nCapacity: " + CorpseCount + "/" + modExt.capacity);
			if (modExt.dissolveCorpses && CorpseCount > 0)
			{
				stringBuilder.Append($"\nTime till next corpse dissolves: {GenDate.TicksToDays(nextDissolveTick - Find.TickManager.TicksGame)}");
			}
			return stringBuilder.ToString();
		}

		[IteratorStateMachine(typeof(<GetGizmos>d__19))]
		public override IEnumerable<Gizmo> GetGizmos()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <GetGizmos>d__19(-2)
			{
				<>4__this = this
			};
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private IEnumerable<Gizmo> <>n__0()
		{
			return ((Building_Grave)this).GetGizmos();
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private bool <>n__1()
		{
			return ((Building_Grave)this).StorageTabVisible;
		}
	}
	public class Building_ThingProducer : Building
	{
		public CompPowerTrader powerComp;

		public DefModExt_ThingProducer producerProps;

		protected bool contentsKnown;

		public int storedThingCount;

		public int currentWork;

		public float secondsTillNext => GenTicks.TicksToSeconds(producerProps.productionTime);

		public bool HasAnyContents => storedThingCount > 0;

		public string ContainedThing => (storedThingCount != 0) + ((Def)producerProps.thingDef).label;

		public override void ExposeData()
		{
			((Building)this).ExposeData();
			Scribe_Values.Look<int>(ref currentWork, "currentWork", 0, false);
			Scribe_Values.Look<bool>(ref contentsKnown, "contentsKnown", false, false);
			Scribe_Values.Look<int>(ref storedThingCount, "storedThingCount", 0, false);
		}

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			((Building)this).SpawnSetup(map, respawningAfterLoad);
			powerComp = ((ThingWithComps)this).GetComp<CompPowerTrader>();
			producerProps = ((Def)((Thing)this).def).GetModExtension<DefModExt_ThingProducer>();
			if (((Thing)this).Faction != null && ((Thing)this).Faction.IsPlayer)
			{
				contentsKnown = true;
			}
			currentWork = producerProps.productionTime;
		}

		public override void Tick()
		{
			((ThingWithComps)this).Tick();
			if (((Thing)this).Spawned && storedThingCount < producerProps.maxThings)
			{
				if (currentWork <= 0)
				{
					storedThingCount++;
					currentWork = producerProps.productionTime;
				}
				if (currentWork > 0)
				{
					currentWork--;
				}
			}
		}

		public override IEnumerable<FloatMenuOption> GetFloatMenuOptions(Pawn myPawn)
		{
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0061: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Unknown result type (might be due to invalid IL or missing references)
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Expected O, but got Unknown
			//IL_0077: Unknown result type (might be due to invalid IL or missing references)
			//IL_008e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0094: Expected O, but got Unknown
			//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d7: Expected O, but got Unknown
			//IL_0108: Unknown result type (might be due to invalid IL or missing references)
			//IL_010d: Unknown result type (might be due to invalid IL or missing references)
			//IL_012f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0136: Expected O, but got Unknown
			if (!ReservationUtility.CanReserve(myPawn, LocalTargetInfo.op_Implicit((Thing)(object)this), 1, -1, (ReservationLayerDef)null, false))
			{
				FloatMenuOption item = new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("CannotUseReserved")), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
				return new List<FloatMenuOption> { item };
			}
			if (!ReachabilityUtility.CanReach(myPawn, LocalTargetInfo.op_Implicit((Thing)(object)this), (PathEndMode)1, (Danger)2, false, false, (TraverseMode)0))
			{
				FloatMenuOption item2 = new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("CannotUseNoPath")), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
				return new List<FloatMenuOption> { item2 };
			}
			if (storedThingCount <= 0)
			{
				FloatMenuOption item3 = new FloatMenuOption("No available " + ((Def)producerProps.thingDef).label, (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
				return new List<FloatMenuOption> { item3 };
			}
			if (storedThingCount > 0)
			{
				FloatMenuOption item4 = new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(producerProps.retrievalString, NamedArgument.op_Implicit(((Def)producerProps.thingDef).label))), (Action)delegate
				{
					//IL_000b: Unknown result type (might be due to invalid IL or missing references)
					//IL_0010: Unknown result type (might be due to invalid IL or missing references)
					//IL_0016: Expected O, but got Unknown
					//IL_0022: Unknown result type (might be due to invalid IL or missing references)
					Job val = new Job(TabulaRasaDefOf.TabulaRasa_TakeFromProducer, LocalTargetInfo.op_Implicit((Thing)(object)this));
					ReservationUtility.Reserve(myPawn, LocalTargetInfo.op_Implicit((Thing)(object)this), val, 1, -1, (ReservationLayerDef)null, true, false);
					myPawn.jobs.TryTakeOrderedJob(val, (JobTag?)(JobTag)0, false);
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
				return new List<FloatMenuOption> { item4 };
			}
			return null;
		}

		public override string GetInspectString()
		{
			string text = ((ThingWithComps)this).GetInspectString();
			string text2 = (contentsKnown ? (storedThingCount + "x " + ((Def)producerProps.thingDef).label) : "Contents Unknown");
			if (!GenText.NullOrEmpty(text))
			{
				text += "\n";
			}
			return text + "Contains: " + GenText.CapitalizeFirst(text2);
		}

		public void TakeItem(Pawn doer)
		{
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			if (storedThingCount > 0)
			{
				GenPlace.TryPlaceThing(ThingMaker.MakeThing(producerProps.thingDef, (ThingDef)null), ((Thing)doer).Position, ((Thing)doer).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
				storedThingCount--;
			}
		}
	}
	public class Building_TurretGunSmart : Building_TurretGun
	{
		public bool PlayerControlled => ((Thing)this).Faction == Faction.OfPlayer;
	}
	public class Building_RefundOnDeconstruct : Building
	{
		public override void Destroy(DestroyMode mode = 0)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0002: Invalid comparison between Unknown and I4
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			if ((int)mode == 4)
			{
				mode = (DestroyMode)7;
			}
			((Building)this).Destroy(mode);
		}
	}
	public class CompProperties_AdvFireOverlay : CompProperties_FireOverlay
	{
		public List<Rot4> showRotations = new List<Rot4>();

		public CompProperties_AdvFireOverlay()
		{
			((CompProperties)this).compClass = typeof(Comp_AdvFireOverlay);
		}

		public override void ResolveReferences(ThingDef parentDef)
		{
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			((CompProperties)this).ResolveReferences(parentDef);
			if (showRotations.Count <= 0)
			{
				showRotations.Add(Rot4.North);
				showRotations.Add(Rot4.South);
				showRotations.Add(Rot4.East);
				showRotations.Add(Rot4.West);
			}
		}
	}
	public class CompProperties_Renameable : CompProperties
	{
		public CompProperties_Renameable()
		{
			base.compClass = typeof(Comp_Renameable);
		}
	}
	public class CompProperties_TransformThing : CompProperties
	{
		public ThingDef thingDef;

		public string texPath;

		public string label;

		public string desc;

		public bool onlyWhenHealthFull = true;

		public FleckDef fleck;

		public CompProperties_TransformThing()
		{
			base.compClass = typeof(Comp_TransformThing);
		}
	}
	public class CompProperties_Mining : CompProperties
	{
		public MiningSettings defaultMiningSettings;

		public float tickCostMultiplier = 1f;

		public float costDebuffPercent = 0.2f;

		public int maxDebuffCount = 4;

		public float outputCountMultiplier = 1f;

		public CompProperties_Mining()
		{
			base.compClass = typeof(Comp_Mining);
		}
	}
	public class CompProperties_PawnSpawner : CompProperties
	{
		public int timer = -1;

		public bool repeatSpawn;

		public IntRange repeatCount = new IntRange(0, 1);

		public bool deleteWhenDone = true;

		public PawnKindDef pawnKind;

		public List<PawnKindDef> pawnKinds = new List<PawnKindDef>();

		public bool purgeSkillsBeforeSetting = true;

		public List<SkillLevelSetting> skillSettings = new List<SkillLevelSetting>();

		public bool newborn;

		public bool purgeTraits;

		public bool canGeneratePawnRelations;

		public bool purgeApparel;

		public CompProperties_PawnSpawner()
		{
			//IL_000a: Unknown result type (might be due to invalid IL or missing references)
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			base.compClass = typeof(Comp_PawnSpawner);
		}
	}
	public class CompProperties_AdvancedHatcher : CompProperties
	{
		public float daysToHatch = 1f;

		public PawnKindDef pawnKind;

		public List<PawnKindDef> pawnKinds = new List<PawnKindDef>();

		public CompProperties_AdvancedHatcher()
		{
			base.compClass = typeof(Comp_AdvancedHatcher);
		}
	}
	public class CompProperties_HologramProjection : CompProperties_Glower
	{
		public Vector2 size = new Vector2(1f, 1f);

		public Vector3 offset = new Vector3(0f, 0f, 0f);

		public List<string> hologramTags = new List<string>();

		public string holobeam;

		public float radius;

		public float recreationPerDay;

		public float certaintyPerDay;

		public Material Holobeam => MaterialPool.MatFrom(holobeam, ShaderDatabase.TransparentPostLight);

		public CompProperties_HologramProjection()
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			((CompProperties)this).compClass = typeof(Comp_HologramProjection);
		}
	}
	public class CompProperties_ExtraGraphics : CompProperties
	{
		public List<ExtraGraphicDetails> extraGraphics = new List<ExtraGraphicDetails>();

		public CompProperties_ExtraGraphics()
		{
			base.compClass = typeof(Comp_ExtraGraphics);
		}
	}
	public class CompProperties_UseHealthPack : CompProperties_UseEffect
	{
		public List<HediffDef> ignoredHediffs = new List<HediffDef>();
	}
	public class CompProperties_AutoResearch : CompProperties
	{
		public bool requiresPower;

		public bool totalPawnsAffectSpeed;

		public float bonusPerPawn = 0.1f;

		public float researchSpeedFactor = 1f;

		public PawnKindDef pawnKind;

		public XenotypeDef xenotype;

		public CompProperties_AutoResearch()
		{
			base.compClass = typeof(Comp_AutoResearch);
		}

		public override void ResolveReferences(ThingDef parentDef)
		{
			((CompProperties)this).ResolveReferences(parentDef);
			if (pawnKind == null)
			{
				pawnKind = PawnKindDefOf.Colonist;
			}
			if (xenotype == null)
			{
				xenotype = XenotypeDefOf.Baseliner;
			}
		}
	}
	public class CompProperties_AlienBodyCorrection : CompProperties
	{
		public List<BodyTypeDef> maleBodyTypes = new List<BodyTypeDef>();

		public List<BodyTypeDef> femaleBodyTypes = new List<BodyTypeDef>();

		public CompProperties_AlienBodyCorrection()
		{
			base.compClass = typeof(Comp_AlienBodyCorrection);
		}
	}
	public class CompProperties_IdeoIconOverlay : CompProperties
	{
		public bool showSouth = true;

		public bool showNorth = true;

		public bool showEast = true;

		public bool showWest = true;

		public Vector3 offsetSouth = new Vector3(0f, 0f, 0f);

		public Vector3 offsetNorth = new Vector3(0f, 0f, 0f);

		public Vector3 offsetEast = new Vector3(0f, 0f, 0f);

		public Vector3 offsetWest = new Vector3(0f, 0f, 0f);

		public Vector2 drawSize = new Vector2(1f, 1f);

		public CompProperties_IdeoIconOverlay()
		{
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0031: Unknown result type (might be due to invalid IL or missing references)
			//IL_0046: Unknown result type (might be due to invalid IL or missing references)
			//IL_004b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			//IL_0065: Unknown result type (might be due to invalid IL or missing references)
			//IL_007a: Unknown result type (might be due to invalid IL or missing references)
			//IL_007f: Unknown result type (might be due to invalid IL or missing references)
			//IL_008f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0094: Unknown result type (might be due to invalid IL or missing references)
			base.compClass = typeof(Comp_IdeoIconOverlay);
		}
	}
	public class CompProperties_TraitsOverTime : CompProperties
	{
		public int maxTraits = 3;

		public IntRange timeBetweenTraits = new IntRange(30000, 60000);

		public List<TraitEntryAdvanced> traitWhitelist = new List<TraitEntryAdvanced>();

		public List<TraitEntryAdvanced> traitBlacklist = new List<TraitEntryAdvanced>();

		public CompProperties_TraitsOverTime()
		{
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			base.compClass = typeof(Comp_TraitsOverTime);
		}
	}
	public class Comp_AlienBodyCorrection : ThingComp
	{
		public bool completed;

		public CompProperties_AlienBodyCorrection Props => (CompProperties_AlienBodyCorrection)(object)base.props;

		public override void PostExposeData()
		{
			((ThingComp)this).PostExposeData();
			Scribe_Values.Look<bool>(ref completed, "completed", false, false);
		}

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
			if (!completed)
			{
				CorrectBodyNow();
			}
		}

		public void CorrectBodyNow()
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0013: Invalid comparison between Unknown and I4
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Invalid comparison between Unknown and I4
			//IL_005c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Invalid comparison between Unknown and I4
			ThingWithComps parent = base.parent;
			Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
			if ((int)val.DevelopmentalStage == 8)
			{
				if ((int)val.gender == 1)
				{
					if (!Props.maleBodyTypes.Contains(val.story.bodyType))
					{
						val.story.bodyType = GenCollection.RandomElement<BodyTypeDef>((IEnumerable<BodyTypeDef>)Props.maleBodyTypes);
					}
				}
				else if ((int)val.gender == 2 && !Props.femaleBodyTypes.Contains(val.story.bodyType))
				{
					val.story.bodyType = GenCollection.RandomElement<BodyTypeDef>((IEnumerable<BodyTypeDef>)Props.femaleBodyTypes);
				}
			}
			completed = true;
		}
	}
	public class Comp_IdeoIconOverlay : ThingComp
	{
		private Texture2D iconTexture;

		private Color ideoColor = Color.white;

		public CompProperties_IdeoIconOverlay Props => (CompProperties_IdeoIconOverlay)(object)base.props;

		private Material Graphic
		{
			get
			{
				//IL_0033: Unknown result type (might be due to invalid IL or missing references)
				if ((Object)(object)iconTexture == (Object)null)
				{
					iconTexture = Find.FactionManager.OfPlayer.ideos.PrimaryIdeo.Icon;
				}
				return MaterialPool.MatFrom(new MaterialRequest((Texture)(object)iconTexture));
			}
		}

		private bool ShouldDraw
		{
			get
			{
				//IL_0006: Unknown result type (might be due to invalid IL or missing references)
				//IL_000b: Unknown result type (might be due to invalid IL or missing references)
				//IL_0029: Unknown result type (might be due to invalid IL or missing references)
				//IL_002e: Unknown result type (might be due to invalid IL or missing references)
				//IL_004c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0051: Unknown result type (might be due to invalid IL or missing references)
				//IL_006f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0074: Unknown result type (might be due to invalid IL or missing references)
				if (((Thing)base.parent).Rotation == Rot4.South)
				{
					return Props.showSouth;
				}
				if (((Thing)base.parent).Rotation == Rot4.North)
				{
					return Props.showNorth;
				}
				if (((Thing)base.parent).Rotation == Rot4.East)
				{
					return Props.showEast;
				}
				if (((Thing)base.parent).Rotation == Rot4.West)
				{
					return Props.showWest;
				}
				return false;
			}
		}

		private Vector3 CurrentOffset
		{
			get
			{
				//IL_0006: Unknown result type (might be due to invalid IL or missing references)
				//IL_000b: Unknown result type (might be due to invalid IL or missing references)
				//IL_0029: Unknown result type (might be due to invalid IL or missing references)
				//IL_002e: Unknown result type (might be due to invalid IL or missing references)
				//IL_001d: Unknown result type (might be due to invalid IL or missing references)
				//IL_004c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0051: Unknown result type (might be due to invalid IL or missing references)
				//IL_0040: Unknown result type (might be due to invalid IL or missing references)
				//IL_006f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0074: Unknown result type (might be due to invalid IL or missing references)
				//IL_0063: Unknown result type (might be due to invalid IL or missing references)
				//IL_009b: Unknown result type (might be due to invalid IL or missing references)
				//IL_0086: Unknown result type (might be due to invalid IL or missing references)
				if (((Thing)base.parent).Rotation == Rot4.South)
				{
					return Props.offsetSouth;
				}
				if (((Thing)base.parent).Rotation == Rot4.North)
				{
					return Props.offsetNorth;
				}
				if (((Thing)base.parent).Rotation == Rot4.East)
				{
					return Props.offsetEast;
				}
				if (((Thing)base.parent).Rotation == Rot4.West)
				{
					return Props.offsetWest;
				}
				return new Vector3(0f, 0f, 0f);
			}
		}

		private Color GetIdeoColor => Find.FactionManager.OfPlayer.ideos.PrimaryIdeo.Color;

		public override void CompTickRare()
		{
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			((ThingComp)this).CompTickRare();
			iconTexture = null;
			ideoColor = GetIdeoColor;
		}

		public override void PostDraw()
		{
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Expected O, but got Unknown
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			//IL_0065: Unknown result type (might be due to invalid IL or missing references)
			//IL_006b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0070: Unknown result type (might be due to invalid IL or missing references)
			//IL_007a: Unknown result type (might be due to invalid IL or missing references)
			//IL_007f: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_004b: Unknown result type (might be due to invalid IL or missing references)
			((ThingComp)this).PostDraw();
			if (ModsConfig.IdeologyActive && ShouldDraw)
			{
				MaterialPropertyBlock val = new MaterialPropertyBlock();
				if (((Thing)base.parent).Stuff != null)
				{
					_ = ((Thing)base.parent).Stuff.stuffProps.color;
					val.SetColor(ShaderPropertyIDs.Color, ideoColor);
				}
				Matrix4x4 val2 = default(Matrix4x4);
				((Matrix4x4)(ref val2)).SetTRS(((Thing)base.parent).DrawPos + CurrentOffset, Quaternion.AngleAxis(0f, Vector3.up), new Vector3(Props.drawSize.x, 1f, Props.drawSize.y));
				Graphics.DrawMesh(MeshPool.plane10, val2, Graphic, 0, (Camera)null, 0, val);
			}
		}
	}
	public class Comp_TraitsOverTime : ThingComp
	{
		public int nextAttemptTimer = -1;

		public CompProperties_TraitsOverTime Props => (CompProperties_TraitsOverTime)(object)base.props;

		public Pawn pawn
		{
			get
			{
				ThingWithComps parent = base.parent;
				return (Pawn)(object)((parent is Pawn) ? parent : null);
			}
		}

		public int CurrentTraitCount => pawn.story.traits.allTraits.Count();

		public override void CompTick()
		{
			((ThingComp)this).CompTick();
			if (CurrentTraitCount < Props.maxTraits && nextAttemptTimer <= 0)
			{
				AddRandomTrait();
				ResetTimer();
			}
			nextAttemptTimer--;
		}

		public void AddRandomTrait()
		{
			//IL_007d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0088: Expected O, but got Unknown
			if (!GenList.NullOrEmpty<TraitEntryAdvanced>((IList<TraitEntryAdvanced>)Props.traitWhitelist))
			{
				bool flag = false;
				while (!flag)
				{
					TraitEntryAdvanced traitEntryAdvanced = GenCollection.RandomElementByWeight<TraitEntryAdvanced>((IEnumerable<TraitEntryAdvanced>)Props.traitWhitelist, (Func<TraitEntryAdvanced, float>)((TraitEntryAdvanced x) => x.chance));
					TraitDef def = traitEntryAdvanced.def;
					if (!pawn.story.traits.HasTrait(def))
					{
						pawn.story.traits.GainTrait(new Trait(def, traitEntryAdvanced.degree, false), false);
						flag = true;
					}
				}
			}
			else if (!GenList.NullOrEmpty<TraitEntryAdvanced>((IList<TraitEntryAdvanced>)Props.traitBlacklist))
			{
				new NotImplementedException();
			}
		}

		public void ResetTimer()
		{
			nextAttemptTimer = ((IntRange)(ref Props.timeBetweenTraits)).RandomInRange;
		}
	}
	public class Comp_AutoResearch : ThingComp
	{
		public CompPowerTrader powerComp;

		public Pawn researchingPawnCached;

		public Pawn worstPawnCached;

		public CompProperties_AutoResearch Props => (CompProperties_AutoResearch)(object)base.props;

		public Pawn ResearchingPawn
		{
			get
			{
				if (researchingPawnCached == null)
				{
					List<Pawn> viablePawns = GetViablePawns();
					if (!GenList.NullOrEmpty<Pawn>((IList<Pawn>)viablePawns))
					{
						Pawn val = null;
						float num = 0f;
						foreach (Pawn item in viablePawns)
						{
							if (item != val)
							{
								int level = item.skills.skills.Find((SkillRecord s) => s.def == SkillDefOf.Intellectual).Level;
								if (val == null || (float)level > num)
								{
									val = item;
									num = level;
								}
							}
						}
						if (val != null)
						{
							researchingPawnCached = val;
						}
					}
				}
				return researchingPawnCached;
			}
		}

		public Pawn WorstPawn
		{
			get
			{
				if (worstPawnCached == null)
				{
					List<Pawn> viablePawns = GetViablePawns();
					if (Props.totalPawnsAffectSpeed && !GenList.NullOrEmpty<Pawn>((IList<Pawn>)viablePawns))
					{
						Pawn val = null;
						float num = 0f;
						foreach (Pawn item in viablePawns)
						{
							if (item != val)
							{
								int level = item.skills.skills.Find((SkillRecord s) => s.def == SkillDefOf.Intellectual).Level;
								if (val == null || (float)level < num)
								{
									val = item;
									num = level;
								}
							}
						}
						if (val != null)
						{
							worstPawnCached = val;
						}
					}
				}
				return worstPawnCached;
			}
		}

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
			powerComp = ThingCompUtility.TryGetComp<CompPowerTrader>((Thing)(object)base.parent);
		}

		public override void CompTick()
		{
			((ThingComp)this).CompTick();
			if (HasPower() && ResearchingPawn != null && Find.ResearchManager.currentProj != null)
			{
				float statValue = StatExtension.GetStatValue((Thing)(object)ResearchingPawn, StatDefOf.ResearchSpeed, true, -1);
				statValue = ((!Props.totalPawnsAffectSpeed) ? (statValue * Props.researchSpeedFactor) : (statValue * Props.researchSpeedFactor + Props.bonusPerPawn * (float)((Thing)base.parent).Map.mapPawns.ColonistsSpawnedCount));
				Find.ResearchManager.ResearchPerformed(statValue, ResearchingPawn);
				ResearchingPawn.skills.Learn(SkillDefOf.Intellectual, 0.1f, false, false);
			}
		}

		public bool HasPower()
		{
			if (Props.requiresPower && powerComp != null && !powerComp.PowerOn)
			{
				return false;
			}
			return true;
		}

		public List<Pawn> GetViablePawns()
		{
			List<Pawn> list = new List<Pawn>();
			if (Props.pawnKind != PawnKindDefOf.Colonist)
			{
				foreach (Pawn item in ((Thing)base.parent).Map.mapPawns.FreeColonistsSpawned)
				{
					if (((Thing)item).def == Props.pawnKind.race)
					{
						list.Add(item);
					}
				}
			}
			else if (Props.xenotype != XenotypeDefOf.Baseliner)
			{
				foreach (Pawn item2 in ((Thing)base.parent).Map.mapPawns.FreeColonistsSpawned)
				{
					if (item2.genes.Xenotype == Props.xenotype)
					{
						list.Add(item2);
					}
				}
			}
			else
			{
				list = ((Thing)base.parent).Map.mapPawns.FreeColonistsSpawned;
			}
			return list;
		}
	}
	public class Comp_UseHealthPack : CompUseEffect
	{
		public CompProperties_UseHealthPack Props => (CompProperties_UseHealthPack)(object)((ThingComp)this).props;

		public override void DoEffect(Pawn usedBy)
		{
			((CompUseEffect)this).DoEffect(usedBy);
			HealthUtil.TrySealWounds(usedBy, Props.ignoredHediffs);
		}
	}
	public class Comp_ExtraGraphics : ThingComp
	{
		[CompilerGenerated]
		private sealed class <CompGetGizmosExtra>d__9 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Comp_ExtraGraphics <>4__this;

			Gizmo IEnumerator<Gizmo>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <CompGetGizmosExtra>d__9(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_0051: Unknown result type (might be due to invalid IL or missing references)
				//IL_0056: Unknown result type (might be due to invalid IL or missing references)
				//IL_005c: Unknown result type (might be due to invalid IL or missing references)
				//IL_006b: Unknown result type (might be due to invalid IL or missing references)
				//IL_0071: Unknown result type (might be due to invalid IL or missing references)
				//IL_0080: Unknown result type (might be due to invalid IL or missing references)
				//IL_0091: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a8: Expected O, but got Unknown
				int num = <>1__state;
				Comp_ExtraGraphics CS$<>8__locals4 = <>4__this;
				switch (num)
				{
				default:
					return false;
				case 0:
					<>1__state = -1;
					if (((Thing)((ThingComp)CS$<>8__locals4).parent).Faction != null && ((Thing)((ThingComp)CS$<>8__locals4).parent).Faction.IsPlayer && ((Thing)((ThingComp)CS$<>8__locals4).parent).StyleDef == null)
					{
						<>2__current = (Gizmo)new Command_Action
						{
							defaultLabel = TaggedString.op_Implicit(Translator.Translate("O21_ChangeGraphic")),
							defaultDesc = TaggedString.op_Implicit(Translator.Translate("O21_ChangeGraphicDesc")),
							icon = (Texture)(object)ContentFinder<Texture2D>.Get("Toolbox/UI/Cycle", true),
							action = delegate
							{
								CS$<>8__locals4.SelectableGraphicListing();
							}
						};
						<>1__state = 1;
						return true;
					}
					break;
				case 1:
					<>1__state = -1;
					break;
				}
				return false;
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
			{
				<CompGetGizmosExtra>d__9 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <CompGetGizmosExtra>d__9(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		public Thing thingToGrab;

		public Graphic_Multi newGraphic;

		public Graphic_Single newGraphicSingle;

		public string newGraphicPath = "";

		public string newGraphicSinglePath = "";

		public CompProperties_ExtraGraphics Props => (CompProperties_ExtraGraphics)(object)base.props;

		public override void PostExposeData()
		{
			Scribe_Values.Look<string>(ref newGraphicPath, "newGraphicPath", (string)null, false);
			Scribe_Values.Look<string>(ref newGraphicSinglePath, "newGraphicSinglePath", (string)null, false);
		}

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			thingToGrab = (Thing)(object)base.parent;
			LongEventHandler.ExecuteWhenFinished((Action)delegate
			{
				ChangeGraphic(respawningAfterLoad);
			});
		}

		[IteratorStateMachine(typeof(<CompGetGizmosExtra>d__9))]
		public override IEnumerable<Gizmo> CompGetGizmosExtra()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <CompGetGizmosExtra>d__9(-2)
			{
				<>4__this = this
			};
		}

		public void SelectableGraphicListing()
		{
			//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c3: Expected O, but got Unknown
			//IL_008d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0097: Expected O, but got Unknown
			List<FloatMenuOption> list = new List<FloatMenuOption>();
			int num = 0;
			foreach (ExtraGraphicDetails egd in Props.extraGraphics)
			{
				string text;
				if (GenText.NullOrEmpty(egd.label))
				{
					text = "Option (" + num + ")";
					num++;
				}
				else
				{
					text = egd.label;
				}
				list.Add(new FloatMenuOption(text, (Action)delegate
				{
					//IL_0031: Unknown result type (might be due to invalid IL or missing references)
					SetGraphic(egd);
					((Thing)base.parent).Map.mapDrawer.MapMeshDirty(((Thing)base.parent).Position, MapMeshFlagDef.op_Implicit(MapMeshFlagDefOf.Things) | MapMeshFlagDef.op_Implicit(MapMeshFlagDefOf.Buildings));
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 29f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
			}
			Find.WindowStack.Add((Window)new FloatMenu(list));
		}

		public void SetGraphic(ExtraGraphicDetails egd)
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00db: Expected O, but got Unknown
			//IL_0077: Unknown result type (might be due to invalid IL or missing references)
			//IL_0078: Unknown result type (might be due to invalid IL or missing references)
			//IL_007e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0088: Expected O, but got Unknown
			try
			{
				Vector2 drawSize = ((Thing)base.parent).Graphic.drawSize;
				Color color = ((Thing)base.parent).Graphic.color;
				ShaderTypeDef shaderType = ((Thing)base.parent).def.graphicData.shaderType;
				if (((Thing)base.parent).def.graphicData.graphicClass == typeof(Graphic_Multi))
				{
					newGraphicPath = egd.path;
					newGraphic = (Graphic_Multi)GraphicDatabase.Get<Graphic_Multi>(newGraphicPath, shaderType.Shader, drawSize, color);
					typeof(Thing).GetField("graphicInt", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(thingToGrab, newGraphic);
				}
				else
				{
					newGraphicSinglePath = egd.path;
					newGraphicSingle = (Graphic_Single)GraphicDatabase.Get<Graphic_Single>(newGraphicSinglePath, shaderType.Shader, drawSize, color);
					typeof(Thing).GetField("graphicInt", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(thingToGrab, newGraphicSingle);
				}
			}
			catch
			{
				Log.Warning("Caught an exeption changing graphic. Most likely a misconfigured def.");
			}
		}

		public void ChangeGraphic(bool reloading = false)
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_015c: Unknown result type (might be due to invalid IL or missing references)
			//IL_015d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0163: Unknown result type (might be due to invalid IL or missing references)
			//IL_016d: Expected O, but got Unknown
			//IL_013c: Unknown result type (might be due to invalid IL or missing references)
			//IL_013d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0143: Unknown result type (might be due to invalid IL or missing references)
			//IL_014d: Expected O, but got Unknown
			//IL_02a1: Unknown result type (might be due to invalid IL or missing references)
			//IL_02a2: Unknown result type (might be due to invalid IL or missing references)
			//IL_02a8: Unknown result type (might be due to invalid IL or missing references)
			//IL_02b2: Expected O, but got Unknown
			//IL_0281: Unknown result type (might be due to invalid IL or missing references)
			//IL_0282: Unknown result type (might be due to invalid IL or missing references)
			//IL_0288: Unknown result type (might be due to invalid IL or missing references)
			//IL_0292: Expected O, but got Unknown
			//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ff: Expected O, but got Unknown
			//IL_0233: Unknown result type (might be due to invalid IL or missing references)
			//IL_0234: Unknown result type (might be due to invalid IL or missing references)
			//IL_023a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0244: Expected O, but got Unknown
			try
			{
				Vector2 drawSize = ((Thing)base.parent).Graphic.drawSize;
				Color color = ((Thing)base.parent).Graphic.color;
				ShaderTypeDef shaderType = ((Thing)base.parent).def.graphicData.shaderType;
				if (((Thing)base.parent).Faction == null || !((Thing)base.parent).Faction.IsPlayer)
				{
					return;
				}
				if (((Thing)base.parent).def.graphicData.graphicClass == typeof(Graphic_Multi))
				{
					if (!reloading)
					{
						int num = Props.extraGraphics.FindIndex((ExtraGraphicDetails egi) => egi.path == newGraphicPath);
						num = ((num + 1 <= Props.extraGraphics.Count - 1) ? (num + 1) : 0);
						newGraphicPath = Props.extraGraphics[num].path;
						newGraphic = (Graphic_Multi)GraphicDatabase.Get<Graphic_Multi>(newGraphicPath, shaderType.Shader, drawSize, color);
					}
					else
					{
						if (newGraphicPath == "")
						{
							newGraphicPath = Props.extraGraphics[0].path;
							newGraphic = (Graphic_Multi)GraphicDatabase.Get<Graphic_Multi>(newGraphicPath, shaderType.Shader, drawSize, color);
						}
						else
						{
							newGraphic = (Graphic_Multi)GraphicDatabase.Get<Graphic_Multi>(newGraphicPath, shaderType.Shader, drawSize, color);
						}
						reloading = false;
					}
					typeof(Thing).GetField("graphicInt", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(thingToGrab, newGraphic);
				}
				else
				{
					if (!(((Thing)base.parent).def.graphicData.graphicClass == typeof(Graphic_Single)))
					{
						return;
					}
					if (!reloading)
					{
						int num2 = Props.extraGraphics.FindIndex((ExtraGraphicDetails egi) => egi.path == newGraphicPath);
						num2 = ((num2 + 1 <= Props.extraGraphics.Count - 1) ? (num2 + 1) : 0);
						newGraphicSinglePath = Props.extraGraphics[num2].path;
						newGraphicSingle = (Graphic_Single)GraphicDatabase.Get<Graphic_Single>(newGraphicSinglePath, shaderType.Shader, drawSize, color);
					}
					else
					{
						if (newGraphicSinglePath == "")
						{
							newGraphicSinglePath = Props.extraGraphics[0].path;
							newGraphicSingle = (Graphic_Single)GraphicDatabase.Get<Graphic_Single>(newGraphicSinglePath, shaderType.Shader, drawSize, color);
						}
						else
						{
							newGraphicSingle = (Graphic_Single)GraphicDatabase.Get<Graphic_Single>(newGraphicSinglePath, shaderType.Shader, drawSize, color);
						}
						reloading = false;
					}
					typeof(Thing).GetField("graphicInt", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(thingToGrab, newGraphicSingle);
				}
			}
			catch
			{
				LogUtil.Message("Probably added mid-save. Ignoring load error.");
			}
		}
	}
	public class Comp_HologramProjection : CompGlower
	{
		public HologramDef holoDef;

		public List<HologramDef> viableHolos = new List<HologramDef>();

		public Dictionary<int, Color> hologramColors = new Dictionary<int, Color>();

		public CompProperties_HologramProjection props => (CompProperties_HologramProjection)(object)((CompGlower)this).Props;

		public override void PostExposeData()
		{
			((CompGlower)this).PostExposeData();
			Scribe_Defs.Look<HologramDef>(ref holoDef, "holoDef");
			Scribe_Collections.Look<int, Color>(ref hologramColors, "hologramColors", (LookMode)0, (LookMode)0);
		}

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			((CompGlower)this).PostSpawnSetup(respawningAfterLoad);
			if (GenList.NullOrEmpty<HologramDef>((IList<HologramDef>)viableHolos))
			{
				viableHolos = DefDatabase<HologramDef>.AllDefs.Where((HologramDef hd) => GenCollection.Any<string>(hd.hologramTags, (Predicate<string>)((string hdt) => props.hologramTags.Contains(hdt)))).ToList();
			}
			if (holoDef == null)
			{
				if (!GenList.NullOrEmpty<HologramDef>((IList<HologramDef>)viableHolos))
				{
					holoDef = viableHolos.First();
					ResetHoloColors();
				}
				else
				{
					LogUtil.Error(((Def)((Thing)((ThingComp)this).parent).def).defName + " has no viable hologram defs! Make sure the tags match!");
				}
			}
		}

		public override void PostDraw()
		{
			((ThingComp)this).PostDraw();
			if (!GenText.NullOrEmpty(props.holobeam))
			{
				DrawHoloBeam();
			}
			for (int i = 0; i < holoDef.hologramLayers.Count; i++)
			{
				DrawHoloLayer(holoDef.hologramLayers[i], i);
			}
		}

		public void DrawHoloBeam()
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Expected O, but got Unknown
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0070: Unknown result type (might be due to invalid IL or missing references)
			//IL_007f: Unknown result type (might be due to invalid IL or missing references)
			MaterialPropertyBlock val = new MaterialPropertyBlock();
			val.SetColor(ShaderPropertyIDs.Color, hologramColors[0]);
			Matrix4x4 val2 = default(Matrix4x4);
			((Matrix4x4)(ref val2)).SetTRS(((Thing)((ThingComp)this).parent).DrawPos, Quaternion.AngleAxis(0f, Vector3.up), new Vector3(((Thing)((ThingComp)this).parent).Graphic.drawSize.x, 1f, ((Thing)((ThingComp)this).parent).Graphic.drawSize.y));
			Graphics.DrawMesh(MeshPool.plane10, val2, props.Holobeam, 0, (Camera)null, 0, val);
		}

		public void DrawHoloLayer(HologramLayer layer, int layerInt)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Expected O, but got Unknown
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_004c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0076: Unknown result type (might be due to invalid IL or missing references)
			//IL_0085: Unknown result type (might be due to invalid IL or missing references)
			MaterialPropertyBlock val = new MaterialPropertyBlock();
			val.SetColor(ShaderPropertyIDs.Color, hologramColors[layerInt]);
			Matrix4x4 val2 = default(Matrix4x4);
			((Matrix4x4)(ref val2)).SetTRS(((Thing)((ThingComp)this).parent).DrawPos + props.offset, Quaternion.AngleAxis(0f, Vector3.up), new Vector3(props.size.x, 1f, props.size.y));
			Graphics.DrawMesh(MeshPool.plane10, val2, layer.Hologram, 0, (Camera)null, 0, val);
		}

		public void ResetHoloColors()
		{
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			hologramColors.Clear();
			int num = 0;
			foreach (HologramLayer hologramLayer in holoDef.hologramLayers)
			{
				hologramColors.Add(num, (Color)(((??)hologramLayer.defaultColor) ?? Color.white));
				num++;
			}
			UpdateGlower();
		}

		public void SetHoloColor(int layer, Color color)
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			hologramColors[layer] = color;
			if (layer == 0)
			{
				UpdateGlower();
			}
		}

		public void UpdateGlower()
		{
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0024: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Unknown result type (might be due to invalid IL or missing references)
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			if (!GenDictionary.NullOrEmpty<int, Color>(hologramColors))
			{
				((CompProperties_Glower)props).glowColor = ColorIntUtility.AsColorInt(Color32.op_Implicit(hologramColors[0]));
				((Thing)((ThingComp)this).parent).Map.mapDrawer.MapMeshDirty(((Thing)((ThingComp)this).parent).Position, MapMeshFlagDef.op_Implicit(MapMeshFlagDefOf.Things));
			}
		}
	}
	public class Comp_AdvancedHatcher : ThingComp
	{
		public float gestateProgress;

		public Pawn hatcheeParent;

		public Pawn otherParent;

		public Faction hatcheeFaction = Faction.OfPlayer;

		public CompProperties_AdvancedHatcher Props => (CompProperties_AdvancedHatcher)(object)base.props;

		public CompTemperatureRuinable FreezerComp => ThingCompUtility.TryGetComp<CompTemperatureRuinable>((Thing)(object)base.parent);

		public bool TemperatureDamaged
		{
			get
			{
				if (FreezerComp != null)
				{
					return FreezerComp.Ruined;
				}
				return false;
			}
		}

		public override void CompTick()
		{
			if (!TemperatureDamaged)
			{
				float num = 1f / (Props.daysToHatch * 60000f);
				gestateProgress += num;
				if (gestateProgress >= 1f)
				{
					Hatch();
				}
			}
		}

		public void Hatch()
		{
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			//IL_00de: Unknown result type (might be due to invalid IL or missing references)
			//IL_01e6: Unknown result type (might be due to invalid IL or missing references)
			//IL_018e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0199: Unknown result type (might be due to invalid IL or missing references)
			for (int i = 0; i < ((Thing)base.parent).stackCount; i++)
			{
				PawnKindDef val = null;
				if (Props.pawnKind != null)
				{
					val = Props.pawnKind;
				}
				if (!GenList.NullOrEmpty<PawnKindDef>((IList<PawnKindDef>)Props.pawnKinds))
				{
					val = GenCollection.RandomElement<PawnKindDef>((IEnumerable<PawnKindDef>)Props.pawnKinds);
				}
				if (val != null)
				{
					PawnKindDef obj = val;
					Faction obj2 = hatcheeFaction;
					PlanetTile? val2 = PlanetTile.op_Implicit(-1);
					float? num = 0f;
					Pawn val3 = PawnGenerator.GeneratePawn(new PawnGenerationRequest(obj, obj2, (PawnGenerationContext)2, val2, true, false, false, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, num, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
					if (PawnUtility.TrySpawnHatchedOrBornPawn(val3, (Thing)(object)base.parent, (IntVec3?)null))
					{
						if (val3 != null)
						{
							if (hatcheeParent != null)
							{
								if (val3.playerSettings != null && hatcheeParent.playerSettings != null && ((Thing)hatcheeParent).Faction == hatcheeFaction)
								{
									val3.playerSettings.allowedAreas = hatcheeParent.playerSettings.allowedAreas;
								}
								if (val3.RaceProps.IsFlesh)
								{
									val3.relations.AddDirectRelation(PawnRelationDefOf.Parent, hatcheeParent);
								}
							}
							if (otherParent != null && (hatcheeParent == null || hatcheeParent.gender != otherParent.gender) && val3.RaceProps.IsFlesh)
							{
								val3.relations.AddDirectRelation(PawnRelationDefOf.Parent, otherParent);
							}
						}
						if (((Thing)base.parent).Spawned && (val3 == null || val3.RaceProps.IsFlesh))
						{
							FilthMaker.TryMakeFilth(((Thing)base.parent).Position, ((Thing)base.parent).Map, ThingDefOf.Filth_AmnioticFluid, 1, (FilthSourceFlags)0, true);
						}
					}
					else
					{
						Find.WorldPawns.PassToWorld(val3, (PawnDiscardDecideMode)2);
					}
				}
				else
				{
					LogUtil.Error("Failed to hatch egg of def: " + ((Def)((Thing)base.parent).def).defName + " due to no viable pawnKind or pawnKinds listed. Destroying item to prevent further errors.");
				}
				((Thing)base.parent).Destroy((DestroyMode)0);
			}
		}

		public override void PreAbsorbStack(Thing otherStack, int count)
		{
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			float num = (float)count / (float)(((Thing)base.parent).stackCount + count);
			float num2 = ((ThingWithComps)otherStack).GetComp<Comp_AdvancedHatcher>().gestateProgress;
			gestateProgress = Mathf.Lerp(gestateProgress, num2, num);
		}

		public override void PostSplitOff(Thing piece)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			Comp_AdvancedHatcher comp = ((ThingWithComps)piece).GetComp<Comp_AdvancedHatcher>();
			comp.gestateProgress = gestateProgress;
			comp.hatcheeParent = hatcheeParent;
			comp.otherParent = otherParent;
			comp.hatcheeFaction = hatcheeFaction;
		}

		public override void PrePreTraded(TradeAction action, Pawn playerNegotiator, ITrader trader)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0009: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Invalid comparison between Unknown and I4
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_000f: Invalid comparison between Unknown and I4
			((ThingComp)this).PrePreTraded(action, playerNegotiator, trader);
			if ((int)action != 1)
			{
				if ((int)action == 2)
				{
					hatcheeFaction = trader.Faction;
				}
			}
			else
			{
				hatcheeFaction = Faction.OfPlayer;
			}
		}

		public override void PostPostGeneratedForTrader(TraderKindDef trader, PlanetTile forTile, Faction forFaction)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			((ThingComp)this).PostPostGeneratedForTrader(trader, forTile, forFaction);
			hatcheeFaction = forFaction;
		}

		public override string CompInspectStringExtra()
		{
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_007c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0081: Unknown result type (might be due to invalid IL or missing references)
			//IL_0086: Unknown result type (might be due to invalid IL or missing references)
			if (!TemperatureDamaged)
			{
				return TaggedString.op_Implicit(Translator.Translate("EggProgress") + ": " + GenText.ToStringPercent(gestateProgress) + "\n" + Translator.Translate("HatchesIn") + ": " + TranslatorFormattedStringExtensions.Translate("PeriodDays", NamedArgument.op_Implicit((Props.daysToHatch * (1f - gestateProgress)).ToString("F1"))));
			}
			return null;
		}

		public override void PostExposeData()
		{
			((ThingComp)this).PostExposeData();
			Scribe_Values.Look<float>(ref gestateProgress, "gestateProgress", 0f, false);
			Scribe_References.Look<Pawn>(ref hatcheeParent, "hatcheeParent", false);
			Scribe_References.Look<Pawn>(ref otherParent, "otherParent", false);
			Scribe_References.Look<Faction>(ref hatcheeFaction, "hatcheeFaction", false);
		}
	}
	public class Comp_PawnSpawner : ThingComp
	{
		public int tickToSpawn = -1;

		public int spawnMax = -1;

		public int spawnTotal;

		public CompProperties_PawnSpawner Props => base.props as CompProperties_PawnSpawner;

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
			if (!respawningAfterLoad)
			{
				if (Props.timer > 0)
				{
					tickToSpawn = Props.timer;
				}
				spawnMax = ((IntRange)(ref Props.repeatCount)).RandomInRange;
			}
		}

		public override void CompTick()
		{
			if (((Thing)base.parent).def.plant != null)
			{
				ThingWithComps parent = base.parent;
				if (((Plant)((parent is Plant) ? parent : null)).HarvestableNow)
				{
					SpawnThenDeleteOrRepeat(isPlant: true);
				}
			}
			else if (tickToSpawn <= 0)
			{
				SpawnThenDeleteOrRepeat();
			}
			tickToSpawn--;
		}

		public void SpawnThenDeleteOrRepeat(bool isPlant = false)
		{
			SpawnPawn();
			spawnTotal++;
			if (Props.repeatSpawn && spawnTotal < spawnMax)
			{
				if (isPlant)
				{
					ThingWithComps parent = base.parent;
					((Plant)((parent is Plant) ? parent : null)).Age = 0;
				}
				else
				{
					tickToSpawn = Props.timer;
				}
			}
			else if (Props.deleteWhenDone)
			{
				((Thing)base.parent).Destroy((DestroyMode)0);
			}
		}

		public void SpawnPawn()
		{
			//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
			//IL_0243: Unknown result type (might be due to invalid IL or missing references)
			if (Props.pawnKind != null)
			{
				_ = Props.pawnKind;
			}
			else
			{
				GenCollection.RandomElement<PawnKindDef>((IEnumerable<PawnKindDef>)Props.pawnKinds);
			}
			float? num = null;
			if (Props.newborn)
			{
				num = 0f;
			}
			PawnKindDef pawnKind = Props.pawnKind;
			Faction ofPlayer = Faction.OfPlayer;
			float? num2 = num;
			bool canGeneratePawnRelations = Props.canGeneratePawnRelations;
			Pawn val = PawnGenerator.GeneratePawn(new PawnGenerationRequest(pawnKind, ofPlayer, (PawnGenerationContext)2, (PlanetTile?)null, true, false, false, canGeneratePawnRelations, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, num2, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
			if (!GenList.NullOrEmpty<SkillLevelSetting>((IList<SkillLevelSetting>)Props.skillSettings))
			{
				if (Props.purgeSkillsBeforeSetting)
				{
					val.skills.skills.ForEach(delegate(SkillRecord s)
					{
						s.Level = 0;
					});
				}
				foreach (SkillLevelSetting skill in Props.skillSettings)
				{
					val.skills.skills.Find((SkillRecord sr) => sr.def == skill.skill).Level = skill.level;
				}
			}
			if (Props.purgeTraits && !GenList.NullOrEmpty<Trait>((IList<Trait>)val.story.traits.allTraits))
			{
				val.story.traits.allTraits.RemoveAll((Trait t) => t != null);
			}
			if (Props.purgeApparel && val.apparel.AnyApparel)
			{
				val.apparel.DestroyAll((DestroyMode)0);
			}
			PreSpawnHook(val);
			GenSpawn.Spawn((Thing)(object)val, ((Thing)base.parent).Position, ((Thing)base.parent).Map, (WipeMode)0);
			PostSpawnHook(val);
		}

		public virtual void PreSpawnHook(Pawn pawn)
		{
		}

		public virtual void PostSpawnHook(Pawn pawn)
		{
		}
	}
	public class Comp_Mining : ThingComp
	{
		public CompFlickable compFlickable;

		public CompPowerTrader compPower;

		public CompRefuelable compRefuelable;

		public MiningSettings mineableThings;

		public ThingDef currentlyMining;

		public int mineTicksRemaining = -1;

		public CompProperties_Mining Props => (CompProperties_Mining)(object)base.props;

		public override void PostExposeData()
		{
			((ThingComp)this).PostExposeData();
			Scribe_Deep.Look<MiningSettings>(ref mineableThings, "mineableThings", new object[1] { this });
			Scribe_Defs.Look<ThingDef>(ref currentlyMining, "currentlyMining");
			Scribe_Values.Look<int>(ref mineTicksRemaining, "mineTicksRemaining", 0, false);
		}

		public override void PostPostMake()
		{
			((ThingComp)this).PostPostMake();
			mineableThings = new MiningSettings(this);
			if (Props.defaultMiningSettings != null)
			{
				mineableThings.CopyFrom(Props.defaultMiningSettings);
			}
		}

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
			compFlickable = ThingCompUtility.TryGetComp<CompFlickable>((Thing)(object)base.parent);
			compPower = ThingCompUtility.TryGetComp<CompPowerTrader>((Thing)(object)base.parent);
			compRefuelable = ThingCompUtility.TryGetComp<CompRefuelable>((Thing)(object)base.parent);
		}

		public override void CompTick()
		{
			((ThingComp)this).CompTick();
			if (!compPower.PowerOn || !compFlickable.SwitchIsOn)
			{
				return;
			}
			if (mineTicksRemaining > 0)
			{
				mineTicksRemaining--;
				return;
			}
			if (currentlyMining != null)
			{
				GenerateResult(currentlyMining);
				currentlyMining = null;
				return;
			}
			MiningSettings miningSettings = mineableThings;
			bool? obj;
			if (miningSettings == null)
			{
				obj = null;
			}
			else
			{
				MiningFilter filter = miningSettings.filter;
				if (filter == null)
				{
					obj = null;
				}
				else
				{
					HashSet<ThingDef> allowedDefs = filter.allowedDefs;
					obj = ((allowedDefs != null) ? new bool?(!GenCollection.EnumerableNullOrEmpty<ThingDef>((IEnumerable<ThingDef>)allowedDefs)) : ((bool?)null));
				}
			}
			bool? flag = obj;
			if (flag == true)
			{
				currentlyMining = GetRandomAllowedMineable();
				float num = Props.tickCostMultiplier * (currentlyMining.BaseMarketValue * 1000f);
				float num2 = num * (Props.costDebuffPercent * Mathf.Clamp((float)(Props.maxDebuffCount - mineableThings.filter.allowedDefs.Count), 0f, 3f));
				mineTicksRemaining = Mathf.RoundToInt(num + num2);
			}
		}

		public void GenerateResult(ThingDef d)
		{
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			if (d != null)
			{
				Thing val = ThingMaker.MakeThing(d, (ThingDef)null);
				_ = d.deepLumpSizeRange;
				val.stackCount = Mathf.CeilToInt((float)((IntRange)(ref d.deepLumpSizeRange)).RandomInRange * Props.outputCountMultiplier);
				GenPlace.TryPlaceThing(val, ((Thing)base.parent).InteractionCell, ((Thing)base.parent).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
			}
		}

		public ThingDef GetRandomAllowedMineable()
		{
			return GenCollection.RandomElementByWeight<ThingDef>((IEnumerable<ThingDef>)mineableThings.filter.allowedDefs, (Func<ThingDef, float>)((ThingDef d) => d.deepCommonality));
		}

		public override string CompInspectStringExtra()
		{
			if (currentlyMining != null)
			{
				return "Mining: " + ((Def)currentlyMining).label + "\nTime remaining: " + GenDate.ToStringTicksToPeriod(mineTicksRemaining, true, false, true, true, false);
			}
			return "Mining Inactive";
		}
	}
	public class Comp_TransformThing : ThingComp
	{
		[CompilerGenerated]
		private sealed class <>c__DisplayClass2_0
		{
			public Comp_TransformThing <>4__this;

			public Building building;

			internal void <CompGetGizmosExtra>b__0()
			{
				if (<>4__this.Props.fleck != null)
				{
					<>4__this.SpawnFleck(<>4__this.Props.fleck, building);
				}
				<>4__this.Transform(building, <>4__this.Props.thingDef);
			}
		}

		[CompilerGenerated]
		private sealed class <CompGetGizmosExtra>d__2 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Comp_TransformThing <>4__this;

			private <>c__DisplayClass2_0 <>8__1;

			private IEnumerator<Gizmo> <>7__wrap1;

			Gizmo IEnumerator<Gizmo>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <CompGetGizmosExtra>d__2(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>8__1 = null;
				<>7__wrap1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
				//IL_0103: Unknown result type (might be due to invalid IL or missing references)
				//IL_0114: Unknown result type (might be due to invalid IL or missing references)
				//IL_0125: Unknown result type (might be due to invalid IL or missing references)
				//IL_013c: Unknown result type (might be due to invalid IL or missing references)
				//IL_015e: Unknown result type (might be due to invalid IL or missing references)
				//IL_0164: Unknown result type (might be due to invalid IL or missing references)
				//IL_0173: Unknown result type (might be due to invalid IL or missing references)
				//IL_018f: Expected O, but got Unknown
				try
				{
					int num = <>1__state;
					Comp_TransformThing comp_TransformThing = <>4__this;
					ref Building reference;
					ThingWithComps parent;
					switch (num)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<>8__1 = new <>c__DisplayClass2_0();
						<>8__1.<>4__this = <>4__this;
						<>7__wrap1 = comp_TransformThing.<>n__0().GetEnumerator();
						<>1__state = -3;
						goto IL_008e;
					case 1:
						<>1__state = -3;
						goto IL_008e;
					case 2:
						{
							<>1__state = -1;
							break;
						}
						IL_008e:
						if (<>7__wrap1.MoveNext())
						{
							Gizmo current = <>7__wrap1.Current;
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = null;
						if (comp_TransformThing.Props.thingDef == null)
						{
							break;
						}
						reference = ref <>8__1.building;
						parent = ((ThingComp)comp_TransformThing).parent;
						reference = (Building)(object)((parent is Building) ? parent : null);
						if (((Thing)<>8__1.building).Faction == null || !((Thing)<>8__1.building).Faction.IsPlayer)
						{
							break;
						}
						<>2__current = (Gizmo)new Command_Action
						{
							defaultLabel = comp_TransformThing.Props.label,
							defaultDesc = comp_TransformThing.Props.desc,
							icon = (Texture)(object)ContentFinder<Texture2D>.Get(comp_TransformThing.Props.texPath, true),
							disabled = comp_TransformThing.Disabled((Thing)(object)<>8__1.building, comp_TransformThing.Props.onlyWhenHealthFull),
							disabledReason = TaggedString.op_Implicit(Translator.Translate("TabulaRasa_CantTransformDamaged")),
							action = delegate
							{
								if (<>8__1.<>4__this.Props.fleck != null)
								{
									<>8__1.<>4__this.SpawnFleck(<>8__1.<>4__this.Props.fleck, <>8__1.building);
								}
								<>8__1.<>4__this.Transform(<>8__1.building, <>8__1.<>4__this.Props.thingDef);
							}
						};
						<>1__state = 2;
						return true;
					}
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				if (<>7__wrap1 != null)
				{
					<>7__wrap1.Dispose();
				}
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
			{
				<CompGetGizmosExtra>d__2 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <CompGetGizmosExtra>d__2(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		public CompProperties_TransformThing Props => (CompProperties_TransformThing)(object)base.props;

		[IteratorStateMachine(typeof(<CompGetGizmosExtra>d__2))]
		public override IEnumerable<Gizmo> CompGetGizmosExtra()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <CompGetGizmosExtra>d__2(-2)
			{
				<>4__this = this
			};
		}

		public bool Disabled(Thing building, bool maxHealth)
		{
			if (maxHealth)
			{
				return building.HitPoints < building.MaxHitPoints;
			}
			return false;
		}

		public void SpawnFleck(FleckDef fleck, Building building)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0009: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			IntVec3 position = ((Thing)building).Position;
			FleckCreationData dataStatic = FleckMaker.GetDataStatic(((IntVec3)(ref position)).ToVector3(), ((Thing)building).Map, fleck, 1f);
			dataStatic.rotationRate = 0.2f;
			((Thing)building).Map.flecks.CreateFleck(dataStatic);
		}

		public void Transform(Building building, ThingDef thingDef)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			IntVec3 position = ((Thing)building).Position;
			Map map = ((Thing)building).Map;
			((Thing)building).Destroy((DestroyMode)0);
			GenSpawn.Spawn(thingDef, position, map, (WipeMode)0).SetFactionDirect(Faction.OfPlayer);
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private IEnumerable<Gizmo> <>n__0()
		{
			return ((ThingComp)this).CompGetGizmosExtra();
		}
	}
	public class Comp_Renameable : ThingComp
	{
		[CompilerGenerated]
		private sealed class <CompGetGizmosExtra>d__10 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Comp_Renameable <>4__this;

			private IEnumerator<Gizmo> <>7__wrap1;

			Gizmo IEnumerator<Gizmo>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <CompGetGizmosExtra>d__10(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>7__wrap1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_008d: Unknown result type (might be due to invalid IL or missing references)
				//IL_0092: Unknown result type (might be due to invalid IL or missing references)
				//IL_009d: Unknown result type (might be due to invalid IL or missing references)
				//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
				//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
				//IL_00ea: Expected O, but got Unknown
				try
				{
					int num = <>1__state;
					Comp_Renameable CS$<>8__locals3 = <>4__this;
					switch (num)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<>7__wrap1 = CS$<>8__locals3.<>n__0().GetEnumerator();
						<>1__state = -3;
						goto IL_0072;
					case 1:
						<>1__state = -3;
						goto IL_0072;
					case 2:
						{
							<>1__state = -1;
							return false;
						}
						IL_0072:
						if (<>7__wrap1.MoveNext())
						{
							Gizmo current = <>7__wrap1.Current;
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = null;
						<>2__current = (Gizmo)new Command_Action
						{
							defaultLabel = "Rename",
							defaultDesc = "Changes the name of this " + ((Def)((Thing)((ThingComp)CS$<>8__locals3).parent).def).label.ToString(),
							icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Buttons/Rename", true),
							action = delegate
							{
								CS$<>8__locals3.Rename();
							}
						};
						<>1__state = 2;
						return true;
					}
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				if (<>7__wrap1 != null)
				{
					<>7__wrap1.Dispose();
				}
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
			{
				<CompGetGizmosExtra>d__10 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <CompGetGizmosExtra>d__10(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		public string customLabel;

		private CompProperties_Renameable Props => (CompProperties_Renameable)(object)base.props;

		public string CustomLabel
		{
			get
			{
				if (customLabel == null)
				{
					return ((Entity)base.parent).Label.ToString();
				}
				return customLabel;
			}
			set
			{
				customLabel = value;
			}
		}

		public override void PostExposeData()
		{
			((ThingComp)this).PostExposeData();
			Scribe_Values.Look<string>(ref customLabel, "customLabel", (string)null, false);
		}

		public override string TransformLabel(string label)
		{
			if (customLabel != null)
			{
				return customLabel;
			}
			return ((ThingComp)this).TransformLabel(label);
		}

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
			if (!respawningAfterLoad)
			{
				Rename();
			}
		}

		public void Rename()
		{
			Find.WindowStack.Add((Window)(object)new Dialog_NameThing((Thing)(object)base.parent));
		}

		[IteratorStateMachine(typeof(<CompGetGizmosExtra>d__10))]
		public override IEnumerable<Gizmo> CompGetGizmosExtra()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <CompGetGizmosExtra>d__10(-2)
			{
				<>4__this = this
			};
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private IEnumerable<Gizmo> <>n__0()
		{
			return ((ThingComp)this).CompGetGizmosExtra();
		}
	}
	[StaticConstructorOnStartup]
	public class Comp_AdvFireOverlay : CompFireOverlay
	{
		public CompPowerTrader compPower;

		public CompFlickable compFlickable;

		public List<Rot4> showList = new List<Rot4>();

		public CompProperties_AdvFireOverlay Props => (CompProperties_AdvFireOverlay)(object)((ThingComp)this).props;

		public bool Powered
		{
			get
			{
				if ((compPower == null || compPower.PowerOn) && (compFlickable == null || compFlickable.SwitchIsOn))
				{
					if (compFlickable != null)
					{
						return compFlickable.SwitchIsOn;
					}
					return true;
				}
				return false;
			}
		}

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			((CompFireOverlay)this).PostSpawnSetup(respawningAfterLoad);
			showList = Props.showRotations;
			compFlickable = ((ThingComp)this).parent.GetComp<CompFlickable>();
			compPower = ((ThingComp)this).parent.GetComp<CompPowerTrader>();
		}

		public void DrawCall()
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			Vector3 drawPos = ((Thing)((ThingComp)this).parent).DrawPos;
			drawPos.y += 3f / 64f;
			CompFireOverlay.FireGraphic.Draw(drawPos, Rot4.North, (Thing)(object)((ThingComp)this).parent, 0f);
		}

		public override void PostDraw()
		{
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			foreach (Rot4 show in showList)
			{
				if (show == ((Thing)((ThingComp)this).parent).Rotation && Powered)
				{
					DrawCall();
				}
			}
		}
	}
	public sealed class WeightedRaceChoice : IExposable
	{
		public ThingDef race;

		public float weight;

		public string Label => $"Race: {race} :: Weight: {weight}";

		public string LabelCap => GenText.CapitalizeFirst(Label, (Def)(object)race);

		public string Summary => weight + "x " + ((race != null) ? ((Def)race).label : "null");

		public WeightedRaceChoice()
		{
		}

		public WeightedRaceChoice(ThingDef thingDef, float count)
		{
			if (count < 0f)
			{
				Log.Warning("Tried to set ThingDefCountClass count to " + count + ". thingDef=" + (object)thingDef);
				count = 0f;
			}
			race = thingDef;
			weight = count;
		}

		public void ExposeData()
		{
			Scribe_Defs.Look<ThingDef>(ref race, "thingDef");
			Scribe_Values.Look<float>(ref weight, "count", 1f, false);
		}

		public void LoadDataFromXmlCustom(XmlNode xmlRoot)
		{
			if (xmlRoot.ChildNodes.Count != 1)
			{
				Log.Error("Misconfigured WeightedRaceChoice: " + xmlRoot.OuterXml);
				return;
			}
			DirectXmlCrossRefLoader.RegisterObjectWantsCrossRef((object)this, "thingDef", xmlRoot.Name, (string)null, (string)null, (Type)null);
			weight = ParseHelper.FromString<int>(xmlRoot.FirstChild.Value);
		}

		public override string ToString()
		{
			return "(" + weight + "x " + ((race != null) ? ((Def)race).defName : "null") + ")";
		}

		public override int GetHashCode()
		{
			return ((Def)race).shortHash + (int)weight << 16;
		}

		public static implicit operator WeightedRaceChoice(ThingDefCount t)
		{
			return new WeightedRaceChoice(((ThingDefCount)(ref t)).ThingDef, ((ThingDefCount)(ref t)).Count);
		}
	}
	public enum EnergyCategory
	{
		Full,
		GettingLow,
		Desperate,
		EmergencyPower
	}
	public class ExtraGraphicDetails
	{
		public string label = "";

		public string path;
	}
	public class DeathActionWorker_InstantDessication : DeathActionWorker
	{
		public override void PawnDied(Corpse corpse, Lord prevLord)
		{
			//IL_0069: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			if (corpse == null || ((Thing)corpse).Map == null)
			{
				return;
			}
			CompRottable val = ThingCompUtility.TryGetComp<CompRottable>((Thing)(object)corpse);
			if (val != null)
			{
				val.RotImmediately((RotStage)1);
				if (((Thing)corpse.InnerPawn).def.race.BloodDef != null)
				{
					FilthMaker.TryMakeFilth(((Thing)corpse).Position, ((Thing)corpse).Map, ((Thing)corpse.InnerPawn).def.race.BloodDef, 5, (FilthSourceFlags)0, true);
				}
				FleckMaker.AttachedOverlay((Thing)(object)corpse, FleckDefOf.DustPuffThick, Vector3.zero, 10f, -1f);
			}
			else
			{
				LogUtil.Warning("Tried using DeathActionWorker_InstantDessication on " + ((Def)((Thing)corpse.InnerPawn).def).defName + " which cannot rot.");
			}
		}
	}
	public class ExtendedApparelDef : ThingDef
	{
		public float carryCapBuff;
	}
	[HarmonyPatch(typeof(DebugWindowsOpener), "DrawButtons")]
	public static class Patch_DebugWindowsOpener_DrawButtons
	{
		[CompilerGenerated]
		private sealed class <Transpiler>d__2 : IEnumerable<CodeInstruction>, IEnumerable, IEnumerator<CodeInstruction>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private CodeInstruction <>2__current;

			private int <>l__initialThreadId;

			private IEnumerable<CodeInstruction> instructions;

			public IEnumerable<CodeInstruction> <>3__instructions;

			private FieldInfo <widgetRowField>5__2;

			private CodeInstruction[] <>7__wrap2;

			private int <>7__wrap3;

			private CodeInstruction <inst>5__5;

			CodeInstruction IEnumerator<CodeInstruction>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <Transpiler>d__2(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				<widgetRowField>5__2 = null;
				<>7__wrap2 = null;
				<inst>5__5 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_00db: Unknown result type (might be due to invalid IL or missing references)
				//IL_00e5: Expected O, but got Unknown
				//IL_010c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0116: Expected O, but got Unknown
				//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
				//IL_00bf: Expected O, but got Unknown
				switch (<>1__state)
				{
				default:
					return false;
				case 0:
				{
					<>1__state = -1;
					patched = false;
					CodeInstruction[] array = instructions.ToArray();
					<widgetRowField>5__2 = AccessTools.Field(typeof(DebugWindowsOpener), "widgetRow");
					CodeInstruction[] array2 = array;
					<>7__wrap2 = array2;
					<>7__wrap3 = 0;
					goto IL_015d;
				}
				case 1:
					<>1__state = -1;
					<>2__current = new CodeInstruction(OpCodes.Ldfld, (object)<widgetRowField>5__2);
					<>1__state = 2;
					return true;
				case 2:
					<>1__state = -1;
					<>2__current = new CodeInstruction(OpCodes.Call, (object)new Action<WidgetRow>(DrawToolboxButtons).Method);
					<>1__state = 3;
					return true;
				case 3:
					<>1__state = -1;
					patched = true;
					goto IL_012c;
				case 4:
					{
						<>1__state = -1;
						<inst>5__5 = null;
						<>7__wrap3++;
						goto IL_015d;
					}
					IL_015d:
					if (<>7__wrap3 < <>7__wrap2.Length)
					{
						<inst>5__5 = <>7__wrap2[<>7__wrap3];
						if (!patched && <widgetRowField>5__2 != null && <inst>5__5.opcode == OpCodes.Bne_Un_S)
						{
							<>2__current = new CodeInstruction(OpCodes.Ldarg_0, (object)null);
							<>1__state = 1;
							return true;
						}
						goto IL_012c;
					}
					<>7__wrap2 = null;
					return false;
					IL_012c:
					<>2__current = <inst>5__5;
					<>1__state = 4;
					return true;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<CodeInstruction> IEnumerable<CodeInstruction>.GetEnumerator()
			{
				<Transpiler>d__2 <Transpiler>d__;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					<Transpiler>d__ = this;
				}
				else
				{
					<Transpiler>d__ = new <Transpiler>d__2(0);
				}
				<Transpiler>d__.instructions = <>3__instructions;
				return <Transpiler>d__;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<CodeInstruction>)this).GetEnumerator();
			}
		}

		public static bool patched;

		[HarmonyPrepare]
		public static bool Prepare()
		{
			LongEventHandler.ExecuteWhenFinished((Action)delegate
			{
				if (!patched)
				{
					LogUtil.Warning("DebugWindowsOpener_Patch could not be applied.");
				}
			});
			return true;
		}

		[IteratorStateMachine(typeof(<Transpiler>d__2))]
		[HarmonyTranspiler]
		public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <Transpiler>d__2(-2)
			{
				<>3__instructions = instructions
			};
		}

		public static void DrawToolboxButtons(WidgetRow widgets)
		{
			//IL_0095: Unknown result type (might be due to invalid IL or missing references)
			//IL_009f: Expected O, but got Unknown
			if (!ModLister.BiotechInstalled || !TabulaRasaMod.settings.showXenotypeEditorMenu || !widgets.ButtonIcon(TexTabulaRasa.DebugXenotypeEditor, "Open the Xenotype Editor. \n\nThis lets you edit Xenotypes without having to dive several pages into a new game.", (Color?)null, (Color?)null, (Color?)null, true, -1f))
			{
				return;
			}
			WindowStack windowStack = Find.WindowStack;
			if (windowStack.IsOpen<Dialog_CreateXenotype>())
			{
				windowStack.TryRemove(typeof(Dialog_CreateXenotype), true);
				return;
			}
			windowStack.Add((Window)new Dialog_CreateXenotype(-1, (Action)delegate
			{
				windowStack.TryRemove(typeof(Dialog_CreateXenotype), true);
			}));
		}
	}
	[HarmonyPatch(typeof(MassUtility), "Capacity")]
	public static class Patch_MassUtility_Capacity
	{
		[HarmonyPostfix]
		public static void PostFix(Pawn p, StringBuilder explanation, ref float __result)
		{
			bool? obj;
			if (p == null)
			{
				obj = null;
			}
			else
			{
				Pawn_ApparelTracker apparel = p.apparel;
				obj = ((apparel != null) ? new bool?(GenList.NullOrEmpty<Apparel>((IList<Apparel>)apparel.WornApparel)) : ((bool?)null));
			}
			if (obj ?? true)
			{
				return;
			}
			foreach (Apparel item in p.apparel.WornApparel)
			{
				if (((Thing)item).def is ExtendedApparelDef extendedApparelDef)
				{
					__result += extendedApparelDef.carryCapBuff;
					explanation?.AppendLine($"{((Thing)item).LabelCapNoCount}: +{extendedApparelDef.carryCapBuff}");
				}
			}
		}
	}
	public class DefModExt_HeadTypeStuff : DefModExtension
	{
		public bool useSkinShader = true;

		public ShaderTypeDef shaderType;
	}
	[HarmonyPatch(typeof(HeadTypeDef), "GetGraphic")]
	public static class Patch_HeadTypeDef_GetGraphic
	{
		[HarmonyPostfix]
		public static void Postfix(HeadTypeDef __instance, Pawn pawn, Color color, ref Graphic_Multi __result)
		{
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bc: Expected O, but got Unknown
			//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
			DefModExt_HeadTypeStuff modExtension = ((Def)__instance).GetModExtension<DefModExt_HeadTypeStuff>();
			if (modExtension == null)
			{
				return;
			}
			Shader val = ShaderUtility.GetSkinShader(pawn);
			if (!modExtension.useSkinShader)
			{
				ShaderTypeDef shaderType = modExtension.shaderType;
				val = ((shaderType != null) ? shaderType.Shader : null) ?? ShaderDatabase.Cutout;
			}
			for (int i = 0; i < __instance.graphics.Count; i++)
			{
				if (GenColor.IndistinguishableFrom(color, __instance.graphics[i].Key) && (Object)(object)((Graphic)__instance.graphics[i].Value).Shader == (Object)(object)val)
				{
					__result = __instance.graphics[i].Value;
				}
			}
			Graphic_Multi val2 = (Graphic_Multi)GraphicDatabase.Get<Graphic_Multi>(__instance.graphicPath, val, Vector2.one, color);
			__instance.graphics.Add(new KeyValuePair<Color, Graphic_Multi>(color, val2));
			__result = val2;
		}
	}
	public class DefModExt_GeneEffecter : DefModExtension
	{
		public EffecterDef effecter;
	}
	public class Gene_Effecter : Gene
	{
		public Effecter effecter;

		public override void Tick()
		{
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0068: Unknown result type (might be due to invalid IL or missing references)
			((Gene)this).Tick();
			if (((Thing)base.pawn).Spawned)
			{
				if (effecter == null)
				{
					effecter = ((Def)base.def).GetModExtension<DefModExt_GeneEffecter>().effecter.SpawnAttached((Thing)(object)base.pawn, ((Thing)base.pawn).MapHeld, 1f);
				}
				Effecter obj = effecter;
				if (obj != null)
				{
					obj.EffectTick(TargetInfo.op_Implicit((Thing)(object)base.pawn), TargetInfo.op_Implicit((Thing)(object)base.pawn));
				}
			}
			else
			{
				Effecter obj2 = effecter;
				if (obj2 != null)
				{
					obj2.Cleanup();
				}
				effecter = null;
			}
		}
	}
	[HarmonyPatch(typeof(PawnGenerator), "GenerateGenes")]
	public static class Patch_PawnGen_GenerateGenes
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, XenotypeDef xenotype, PawnGenerationRequest request)
		{
			DefModExt_PawnKindExtended modExtension = ((Def)pawn.kindDef).GetModExtension<DefModExt_PawnKindExtended>();
			if (modExtension != null && !pawn.Dead && !GenList.NullOrEmpty<GeneGroup>((IList<GeneGroup>)modExtension.geneGroups) && Rand.Chance(modExtension.geneGroupChance))
			{
				AddGenesFromGroup(GetGeneGroup(pawn.kindDef), pawn);
			}
		}

		public static void AddGenesFromGroup(GeneGroup entry, Pawn pawn)
		{
			for (int i = 0; i < entry.genes.Count; i++)
			{
				GeneDef val = entry.genes[i];
				if (entry.heritable && !pawn.genes.HasEndogene(val))
				{
					pawn.genes.AddGene(val, false);
				}
				else if (!pawn.genes.HasActiveGene(val))
				{
					pawn.genes.AddGene(val, true);
				}
			}
		}

		public static GeneGroup GetGeneGroup(PawnKindDef pawnkind)
		{
			if (((Def)pawnkind).HasModExtension<DefModExt_PawnKindExtended>())
			{
				DefModExt_PawnKindExtended modExtension = ((Def)pawnkind).GetModExtension<DefModExt_PawnKindExtended>();
				if (!GenList.NullOrEmpty<GeneGroup>((IList<GeneGroup>)modExtension.geneGroups))
				{
					Func<GeneGroup, float> func = (GeneGroup x) => x.commonality;
					return GenCollection.RandomElementByWeight<GeneGroup>((IEnumerable<GeneGroup>)modExtension.geneGroups, func);
				}
			}
			return null;
		}
	}
	public class DefModExt_RecipeExtender : DefModExtension
	{
		public HediffDef requiredHediff;

		public string requiredHediffAnyPawnMsg = "TR_RequiredHediffAnyPawnMsg";

		public string requiredHediffMissingMsg = "TR_RequiredHediffMissingMsg";
	}
	public class GeneGroup
	{
		public float commonality = 100f;

		public bool heritable;

		public List<GeneDef> genes = new List<GeneDef>();
	}
	[HarmonyPatch(typeof(Dialog_BillConfig), "GeneratePawnRestrictionOptions")]
	public static class Patch_Dialog_BillConfig_GeneratePawnRestrictionOptions
	{
		[CompilerGenerated]
		private sealed class <>c__DisplayClass1_0
		{
			public Bill bill;

			public DefModExt_RecipeExtender modExt;

			public Func<Pawn, bool> <>9__1;

			internal void <PassThroughHediffRequirement>b__0()
			{
				bill.SetAnyPawnRestriction();
			}

			internal bool <PassThroughHediffRequirement>b__1(Pawn p)
			{
				return p.health.hediffSet.HasHediff(modExt.requiredHediff, false);
			}
		}

		[CompilerGenerated]
		private sealed class <PassThroughHediffRequirement>d__1 : IEnumerable<DropdownMenuElement<Pawn>>, IEnumerable, IEnumerator<DropdownMenuElement<Pawn>>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private DropdownMenuElement<Pawn> <>2__current;

			private int <>l__initialThreadId;

			private Bill bill;

			public Bill <>3__bill;

			private DefModExt_RecipeExtender modExt;

			public DefModExt_RecipeExtender <>3__modExt;

			private <>c__DisplayClass1_0 <>8__1;

			private IEnumerator<DropdownMenuElement<Pawn>> <>7__wrap1;

			DropdownMenuElement<Pawn> IEnumerator<DropdownMenuElement<Pawn>>.Current
			{
				[DebuggerHidden]
				get
				{
					//IL_0001: Unknown result type (might be due to invalid IL or missing references)
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					//IL_0001: Unknown result type (might be due to invalid IL or missing references)
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <PassThroughHediffRequirement>d__1(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 2)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>8__1 = null;
				<>7__wrap1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_0057: Unknown result type (might be due to invalid IL or missing references)
				//IL_006f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0096: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a0: Expected O, but got Unknown
				//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
				//IL_011c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0121: Unknown result type (might be due to invalid IL or missing references)
				//IL_0124: Unknown result type (might be due to invalid IL or missing references)
				//IL_0126: Unknown result type (might be due to invalid IL or missing references)
				try
				{
					switch (<>1__state)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<>8__1 = new <>c__DisplayClass1_0();
						<>8__1.bill = bill;
						<>8__1.modExt = modExt;
						<>2__current = new DropdownMenuElement<Pawn>
						{
							option = new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate(<>8__1.modExt.requiredHediffAnyPawnMsg)), (Action)delegate
							{
								<>8__1.bill.SetAnyPawnRestriction();
							}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
							payload = null
						};
						<>1__state = 1;
						return true;
					case 1:
						<>1__state = -1;
						<>7__wrap1 = BillDialogUtility.GetPawnRestrictionOptionsForBill(<>8__1.bill, (Func<Pawn, bool>)((Pawn p) => p.health.hediffSet.HasHediff(<>8__1.modExt.requiredHediff, false))).GetEnumerator();
						<>1__state = -3;
						break;
					case 2:
						<>1__state = -3;
						break;
					}
					if (<>7__wrap1.MoveNext())
					{
						DropdownMenuElement<Pawn> current = <>7__wrap1.Current;
						<>2__current = current;
						<>1__state = 2;
						return true;
					}
					<>m__Finally1();
					<>7__wrap1 = null;
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				if (<>7__wrap1 != null)
				{
					<>7__wrap1.Dispose();
				}
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<DropdownMenuElement<Pawn>> IEnumerable<DropdownMenuElement<Pawn>>.GetEnumerator()
			{
				<PassThroughHediffRequirement>d__1 <PassThroughHediffRequirement>d__;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					<PassThroughHediffRequirement>d__ = this;
				}
				else
				{
					<PassThroughHediffRequirement>d__ = new <PassThroughHediffRequirement>d__1(0);
				}
				<PassThroughHediffRequirement>d__.bill = <>3__bill;
				<PassThroughHediffRequirement>d__.modExt = <>3__modExt;
				return <PassThroughHediffRequirement>d__;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<DropdownMenuElement<Pawn>>)this).GetEnumerator();
			}
		}

		[HarmonyPrefix]
		public static bool Prefix(ref Dialog_BillConfig __instance, ref IEnumerable<DropdownMenuElement<Pawn>> __result)
		{
			DefModExt_RecipeExtender modExtension = ((Def)((Bill)__instance.bill).recipe).GetModExtension<DefModExt_RecipeExtender>();
			if (modExtension != null && modExtension.requiredHediff != null)
			{
				__result = PassThroughHediffRequirement((Bill)(object)__instance.bill, modExtension);
				return false;
			}
			return true;
		}

		[IteratorStateMachine(typeof(<PassThroughHediffRequirement>d__1))]
		public static IEnumerable<DropdownMenuElement<Pawn>> PassThroughHediffRequirement(Bill bill, DefModExt_RecipeExtender modExt)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <PassThroughHediffRequirement>d__1(-2)
			{
				<>3__bill = bill,
				<>3__modExt = modExt
			};
		}
	}
	[HarmonyPatch(typeof(Bill), "PawnAllowedToStartAnew")]
	public static class Patch_Bill_PawnAllowedToStartAnew
	{
		[HarmonyPostfix]
		public static void PostFix(ref Bill __instance, Pawn p, ref bool __result)
		{
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			if (__result)
			{
				DefModExt_RecipeExtender modExtension = ((Def)__instance.recipe).GetModExtension<DefModExt_RecipeExtender>();
				if (modExtension != null && modExtension.requiredHediff != null && !p.health.hediffSet.HasHediff(modExtension.requiredHediff, false))
				{
					JobFailReason.Is(TaggedString.op_Implicit(Translator.Translate(modExtension.requiredHediffMissingMsg)), (string)null);
					__result = false;
				}
			}
		}
	}
	public class DefModExt_SubCategoryBuilding : DefModExtension
	{
		public DesignatorSubCategoryDef subCategory;

		public bool showOnlyInCategory;
	}
	public class DefModExt_GraveAdv : DefModExtension
	{
		public int capacity = 1;

		public bool dissolveCorpses;

		public int dissolveTicks = 60000;
	}
	[HarmonyPatch(typeof(GeneCategoryDef), "ConfigErrors")]
	public static class Patch_GeneCategoryDef_ConfigErrors
	{
		[HarmonyPrefix]
		public static void Prefix(GeneCategoryDef __instance)
		{
			while (DefDatabase<GeneCategoryDef>.AllDefs.Any((GeneCategoryDef x) => x != __instance && x.displayPriorityInXenotype == __instance.displayPriorityInXenotype))
			{
				GeneCategoryDef obj = __instance;
				obj.displayPriorityInXenotype += 1f;
			}
		}
	}
	public class Popup_ColourPicker : Window
	{
		private Comp_Shield shield;

		private Color color;

		private float colorHue;

		private float colorSaturation;

		private float colorValue;

		private Color oldColor;

		private string bufferColorCode;

		public override Vector2 InitialSize => new Vector2(500f, 380f);

		public Popup_ColourPicker(Comp_Shield shield)
			: base((IWindowDrawing)null)
		{
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			this.shield = shield;
			color = shield.currentColor;
			Color.RGBToHSV(color, ref colorHue, ref colorSaturation, ref colorValue);
			UpdateBufferColorCode();
			base.optionalTitle = TaggedString.op_Implicit(Translator.Translate("ShieldGenColorTitle"));
			base.forcePause = true;
			base.absorbInputAroundWindow = true;
			base.closeOnClickedOutside = true;
		}

		public override void DoWindowContents(Rect inRect)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0077: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
			//IL_0138: Unknown result type (might be due to invalid IL or missing references)
			//IL_0179: Unknown result type (might be due to invalid IL or missing references)
			//IL_01ba: Unknown result type (might be due to invalid IL or missing references)
			//IL_01f9: Unknown result type (might be due to invalid IL or missing references)
			//IL_01fe: Unknown result type (might be due to invalid IL or missing references)
			//IL_021d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0227: Unknown result type (might be due to invalid IL or missing references)
			//IL_0246: Unknown result type (might be due to invalid IL or missing references)
			//IL_0265: Unknown result type (might be due to invalid IL or missing references)
			//IL_0299: Unknown result type (might be due to invalid IL or missing references)
			//IL_0107: Unknown result type (might be due to invalid IL or missing references)
			//IL_02d8: Unknown result type (might be due to invalid IL or missing references)
			//IL_02dd: Unknown result type (might be due to invalid IL or missing references)
			//IL_02bb: Unknown result type (might be due to invalid IL or missing references)
			//IL_02c1: Invalid comparison between Unknown and I4
			//IL_02c8: Unknown result type (might be due to invalid IL or missing references)
			//IL_02cf: Invalid comparison between Unknown and I4
			oldColor = color;
			Text.Font = (GameFont)2;
			color.r = Widgets.HorizontalSlider(new Rect(160f, 0f, 200f, 30f), color.r, 0f, 1f, false, "R", (string)null, (string)null, -1f);
			color.g = Widgets.HorizontalSlider(new Rect(160f, 30f, 200f, 30f), color.g, 0f, 1f, false, "G", (string)null, (string)null, -1f);
			color.b = Widgets.HorizontalSlider(new Rect(160f, 60f, 200f, 30f), color.b, 0f, 1f, false, "B", (string)null, (string)null, -1f);
			if (color != oldColor)
			{
				Color.RGBToHSV(color, ref colorHue, ref colorSaturation, ref colorValue);
			}
			colorHue = Widgets.HorizontalSlider(new Rect(160f, 110f, 200f, 30f), colorHue, 0f, 1f, false, "H", (string)null, (string)null, -1f);
			colorSaturation = Widgets.HorizontalSlider(new Rect(160f, 140f, 200f, 30f), colorSaturation, 0f, 1f, false, "S", (string)null, (string)null, -1f);
			colorValue = Widgets.HorizontalSlider(new Rect(160f, 170f, 200f, 30f), colorValue, 0f, 1f, false, "V", (string)null, (string)null, -1f);
			color = Color.HSVToRGB(colorHue, colorSaturation, colorValue);
			Text.Font = (GameFont)1;
			Widgets.Label(new Rect(160f, 220f, 120f, 25f), Translator.Translate("ShieldGenHexLabel"));
			HexColorCodeField(new Rect(280f, 218f, 100f, 25f));
			DrawColourSquare(new Rect(13f, 36f, 128f, 128f));
			if (Widgets.ButtonText(new Rect(((Rect)(ref inRect)).width / 2f - 50f, ((Rect)(ref inRect)).height - 40f, 100f, 40f), "OK", true, false, true, (TextAnchor?)null) || ((int)Event.current.type == 4 && (int)Event.current.keyCode == 13))
			{
				shield.currentColor = color;
				Find.WindowStack.TryRemove((Window)(object)this, true);
			}
			Text.Font = (GameFont)2;
		}

		private void DrawColourSquare(Rect rect)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			GUI.color = color;
			Texture2D val = ContentFinder<Texture2D>.Get("UI/Shield/ColorPicker", true);
			GUI.DrawTexture(rect, (Texture)(object)val);
			GUI.color = Color.white;
		}

		private void HexColorCodeField(Rect rect)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Unknown result type (might be due to invalid IL or missing references)
			//IL_0058: Unknown result type (might be due to invalid IL or missing references)
			//IL_0051: Unknown result type (might be due to invalid IL or missing references)
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			//IL_007e: Unknown result type (might be due to invalid IL or missing references)
			//IL_008a: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
			if (oldColor != color)
			{
				UpdateBufferColorCode();
			}
			bufferColorCode = Widgets.TextField(rect, bufferColorCode);
			Color white = Color.white;
			bool flag = ColorUtility.TryParseHtmlString(bufferColorCode, ref white);
			Color val = (Color)(flag ? Widgets.NormalOptionColor : new Color(0.5f, 0.5f, 0.5f));
			if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).xMax + 15f, ((Rect)(ref rect)).y, 70f, ((Rect)(ref rect)).height), "OK", false, false, val, true, (TextAnchor?)null))
			{
				if (flag)
				{
					color = white;
					Color.RGBToHSV(color, ref colorHue, ref colorSaturation, ref colorValue);
				}
				else
				{
					Messages.Message(TaggedString.op_Implicit(Translator.Translate("ShieldGenHexColorCodeIsIllFormed")), MessageTypeDefOf.CautionInput, true);
				}
			}
		}

		private void UpdateBufferColorCode()
		{
			int num = (int)(color.r * 255f);
			int num2 = (int)(color.g * 255f);
			int num3 = (int)(color.b * 255f);
			bufferColorCode = "#" + (num * 65536 + num2 * 256 + num3).ToString("X6");
		}
	}
	public class Popup_IntSlider : Window
	{
		public const float width = 215f;

		public const float height = 75f;

		public string label;

		public int floor;

		public int ceiling;

		public Func<int> current;

		public Action<int> callback;

		public override Vector2 InitialSize => new Vector2(215f, 75f);

		public Popup_IntSlider(string label, int floor, int ceiling, Func<int> current, Action<int> callback)
			: base((IWindowDrawing)null)
		{
			this.label = label;
			this.floor = floor;
			this.ceiling = ceiling;
			this.current = current;
			this.callback = callback;
			base.closeOnClickedOutside = true;
		}

		public override void SetInitialSizeAndPosition()
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0031: Unknown result type (might be due to invalid IL or missing references)
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0065: Unknown result type (might be due to invalid IL or missing references)
			//IL_006b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0072: Unknown result type (might be due to invalid IL or missing references)
			//IL_007d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0087: Unknown result type (might be due to invalid IL or missing references)
			//IL_008c: Unknown result type (might be due to invalid IL or missing references)
			Vector2 mousePositionOnUIInverted = UI.MousePositionOnUIInverted;
			mousePositionOnUIInverted.x = Mathf.Clamp(mousePositionOnUIInverted.x, 0f, (float)UI.screenWidth - ((Window)this).InitialSize.x);
			mousePositionOnUIInverted.y = Mathf.Clamp(mousePositionOnUIInverted.y - ((Window)this).InitialSize.y, 0f, (float)UI.screenHeight - ((Window)this).InitialSize.y);
			base.windowRect = new Rect(mousePositionOnUIInverted.x, mousePositionOnUIInverted.y, ((Window)this).InitialSize.x, ((Window)this).InitialSize.y);
		}

		public override void DoWindowContents(Rect rect)
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_004c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			if (!((Rect)(ref rect)).Contains(Event.current.mousePosition) && GenUI.DistFromRect(rect, Event.current.mousePosition) > 75f)
			{
				((Window)this).Close(false);
			}
			else
			{
				callback((int)Widgets.HorizontalSlider(new Rect(5f, 10f, 165f, 25f), (float)current(), (float)floor, (float)ceiling, false, current() + "/" + ceiling, label, (string)null, -1f));
			}
		}
	}
	public static class PosUtil
	{
		public static Rot4 FromAngleFlat2(float angle)
		{
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			//IL_0031: Unknown result type (might be due to invalid IL or missing references)
			//IL_0045: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			angle = GenMath.PositiveMod(angle, 360f);
			if (angle <= 45f)
			{
				return Rot4.North;
			}
			if (angle <= 135f)
			{
				return Rot4.East;
			}
			if (angle < 225f)
			{
				return Rot4.South;
			}
			if (angle <= 315f)
			{
				return Rot4.West;
			}
			return Rot4.North;
		}

		public static IntVec3 PositionOffset(this IntVec3 fromCenter, IntVec3 toCenter)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_0028: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Unknown result type (might be due to invalid IL or missing references)
			//IL_004e: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_0061: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			IntVec3 val = fromCenter - toCenter;
			Rot4 val2 = FromAngleFlat2(((IntVec3)(ref val)).AngleFlat);
			if (val2 == Rot4.North)
			{
				return IntVec3.North;
			}
			if (val2 == Rot4.East)
			{
				return IntVec3.East;
			}
			if (val2 == Rot4.South)
			{
				return IntVec3.South;
			}
			if (val2 == Rot4.West)
			{
				return IntVec3.West;
			}
			return IntVec3.Zero;
		}
	}
	[StaticConstructorOnStartup]
	public static class TexTabulaRasa
	{
		public static readonly Texture2D DebugXenotypeEditor = ContentFinder<Texture2D>.Get("TabulaRasa/UI/XenotypeEditor", true);

		public static readonly Texture2D UpdateMarkAsRead = ContentFinder<Texture2D>.Get("TabulaRasa/UI/Bin", true);

		public static readonly Texture2D Hyperlink = ContentFinder<Texture2D>.Get("TabulaRasa/UI/Hyperlink", true);
	}
	public class Dialog_NameThing : Window
	{
		private string curLabel;

		private Thing thing;

		protected virtual int MaxNameLength => 28;

		public override Vector2 InitialSize => new Vector2(280f, 175f);

		public Dialog_NameThing(Thing thing)
			: base((IWindowDrawing)null)
		{
			base.forcePause = true;
			base.doCloseX = true;
			base.closeOnClickedOutside = true;
			base.absorbInputAroundWindow = true;
			base.closeOnClickedOutside = true;
			curLabel = ((Entity)thing).Label;
			this.thing = thing;
		}

		protected virtual AcceptanceReport NameIsValid(string name)
		{
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_0009: Unknown result type (might be due to invalid IL or missing references)
			if (name.Length == 0)
			{
				return AcceptanceReport.op_Implicit(false);
			}
			return AcceptanceReport.op_Implicit(true);
		}

		public override void DoWindowContents(Rect inRect)
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0013: Invalid comparison between Unknown and I4
			//IL_004a: Unknown result type (might be due to invalid IL or missing references)
			//IL_007d: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Invalid comparison between Unknown and I4
			//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
			//IL_0101: Unknown result type (might be due to invalid IL or missing references)
			//IL_011f: Unknown result type (might be due to invalid IL or missing references)
			Text.Font = (GameFont)2;
			bool flag = false;
			if ((int)Event.current.type == 4 && (int)Event.current.keyCode == 13)
			{
				flag = true;
				Event.current.Use();
			}
			string text = curLabel;
			Widgets.Label(new Rect(15f, 15f, 500f, 50f), text);
			Text.Font = (GameFont)1;
			string text2 = Widgets.TextField(new Rect(15f, 50f, ((Rect)(ref inRect)).width - 15f - 15f, 35f), curLabel);
			if (text2.Length < MaxNameLength)
			{
				curLabel = text2;
			}
			if (!(Widgets.ButtonText(new Rect(15f, ((Rect)(ref inRect)).height - 35f - 15f, ((Rect)(ref inRect)).width - 15f - 15f, 35f), "OK", true, false, true, (TextAnchor?)null) || flag))
			{
				return;
			}
			AcceptanceReport val = NameIsValid(curLabel);
			if (!((AcceptanceReport)(ref val)).Accepted)
			{
				if (GenText.NullOrEmpty(((AcceptanceReport)(ref val)).Reason))
				{
					Messages.Message(TaggedString.op_Implicit(Translator.Translate("NameIsInvalid")), MessageTypeDefOf.RejectInput, false);
				}
				else
				{
					Messages.Message(((AcceptanceReport)(ref val)).Reason, MessageTypeDefOf.RejectInput, false);
				}
				return;
			}
			if (string.IsNullOrEmpty(curLabel))
			{
				curLabel = ((Entity)thing).Label.ToString();
			}
			ThingCompUtility.TryGetComp<Comp_Renameable>(thing).customLabel = curLabel;
			Find.WindowStack.TryRemove((Window)(object)this, true);
			Messages.Message("Successfully renamed " + ((Def)thing.def).label + " to '" + curLabel + "'", LookTargets.op_Implicit(thing), MessageTypeDefOf.PositiveEvent, false);
		}
	}
	public class DefModExt_PlaceNearThing : DefModExtension
	{
		public int radius;

		public List<ThingDef> thingDefs;

		public bool allThings;

		public bool blacklist;
	}
	public class DefModExt_PlaceOnThing : DefModExtension
	{
		public List<ThingDef> viableThings;
	}
	public class DefModExt_MineableThing : DefModExtension
	{
		public int defaultMiningTicks = -1;
	}
	public class PlaceWorker_PlaceNearThing : PlaceWorker
	{
		private List<Thing> buildingsInRange = new List<Thing>();

		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
		{
			//IL_0157: Unknown result type (might be due to invalid IL or missing references)
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			//IL_014c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0125: Unknown result type (might be due to invalid IL or missing references)
			//IL_0145: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
			buildingsInRange.Clear();
			DefModExt_PlaceNearThing modExtension = ((Def)checkingDef).GetModExtension<DefModExt_PlaceNearThing>();
			if (modExtension != null)
			{
				foreach (ThingDef thingDef in ((Def)checkingDef).GetModExtension<DefModExt_PlaceNearThing>().thingDefs)
				{
					foreach (Thing item in map.listerThings.ThingsOfDef(thingDef))
					{
						if (IntVec3Utility.DistanceTo(loc, item.Position) < (float)modExtension.radius)
						{
							buildingsInRange.Add(item);
						}
					}
					foreach (Thing item2 in map.listerThings.ThingsOfDef(((BuildableDef)thingDef).blueprintDef))
					{
						if (IntVec3Utility.DistanceTo(loc, item2.Position) < (float)modExtension.radius)
						{
							buildingsInRange.Add(item2);
						}
					}
				}
				if (!modExtension.blacklist && GenList.NullOrEmpty<Thing>((IList<Thing>)buildingsInRange))
				{
					return AcceptanceReport.op_Implicit("Must be placed near specific thing(s), check building description for more info.");
				}
				if (modExtension.blacklist && !GenList.NullOrEmpty<Thing>((IList<Thing>)buildingsInRange))
				{
					return AcceptanceReport.op_Implicit("Must be placed away from specific thing(s), check building description for more info.");
				}
				return AcceptanceReport.op_Implicit(true);
			}
			return AcceptanceReport.op_Implicit("Building has PlaceWorker_PlaceNearThing but lacks a DefModExt_PlaceNearThing to tell it what it can or cannot place nearby.");
		}

		public override void DrawGhost(ThingDef def, IntVec3 center, Rot4 rot, Color ghostCol, Thing thing = null)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0003: Unknown result type (might be due to invalid IL or missing references)
			//IL_0004: Unknown result type (might be due to invalid IL or missing references)
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			((PlaceWorker)this).DrawGhost(def, center, rot, ghostCol, thing);
			DefModExt_PlaceNearThing modExtension = ((Def)def).GetModExtension<DefModExt_PlaceNearThing>();
			if (modExtension != null && modExtension.radius > 0)
			{
				GenDraw.DrawRadiusRing(center, (float)modExtension.radius);
			}
		}
	}
	public class PlaceWorker_PlaceOnThing : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
		{
			//IL_008b: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0080: Unknown result type (might be due to invalid IL or missing references)
			//IL_0079: Unknown result type (might be due to invalid IL or missing references)
			//IL_0049: Unknown result type (might be due to invalid IL or missing references)
			//IL_004e: Unknown result type (might be due to invalid IL or missing references)
			bool flag = false;
			if (((Def)checkingDef).GetModExtension<DefModExt_PlaceOnThing>() != null)
			{
				foreach (ThingDef viableThing in ((Def)checkingDef).GetModExtension<DefModExt_PlaceOnThing>().viableThings)
				{
					Thing val = map.thingGrid.ThingAt(loc, viableThing);
					if (val != null && !(val.Position != loc) && (val != null || val.Position == loc))
					{
						flag = true;
					}
				}
				if (!flag)
				{
					return AcceptanceReport.op_Implicit("Must be placed on specific thing(s), check building details for more info.");
				}
				return AcceptanceReport.op_Implicit(true);
			}
			return AcceptanceReport.op_Implicit("Building has PlaceWorker_PlaceOnThing but lacks a DefModExtension_PlaceOnThing to tell it what it can place on.");
		}
	}
	public class ITab_Mining : ITab
	{
		public Vector2 scrollPosition;

		public static readonly Vector2 WinSize = new Vector2(300f, 480f);

		public Thing SelectedMiner
		{
			get
			{
				object selObject = ((ITab)this).SelObject;
				return (Thing)((selObject is Thing) ? selObject : null);
			}
		}

		public ITab_Mining()
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			((InspectTabBase)this).size = WinSize;
			((InspectTabBase)this).labelKey = "TabMining";
			((InspectTabBase)this).tutorTag = "QuarryMining";
		}

		public override void FillTab()
		{
			//IL_0036: Unknown result type (might be due to invalid IL or missing references)
			//IL_0040: Unknown result type (might be due to invalid IL or missing references)
			//IL_0045: Unknown result type (might be due to invalid IL or missing references)
			//IL_0046: Unknown result type (might be due to invalid IL or missing references)
			//IL_0076: Unknown result type (might be due to invalid IL or missing references)
			MiningSettings miningSettings = ThingCompUtility.TryGetComp<Comp_Mining>(SelectedMiner)?.mineableThings;
			Rect val = GenUI.ContractedBy(new Rect(0f, 0f, ITab_Storage.WinSize.x, ITab_Storage.WinSize.y), 10f);
			GUI.BeginGroup(val);
			MiningFilter parentFilter = null;
			if (miningSettings != null)
			{
				parentFilter = miningSettings.filter;
			}
			DoThingFilterConfigWindow(new Rect(0f, 20f, ((Rect)(ref val)).width, ((Rect)(ref val)).height - 20f), ref scrollPosition, miningSettings.filter, parentFilter, 8);
			PlayerKnowledgeDatabase.KnowledgeDemonstrated(ConceptDefOf.StorageTab, (KnowledgeAmount)1);
			GUI.EndGroup();
		}

		public static void DoThingFilterConfigWindow(Rect rect, ref Vector2 scrollPosition, MiningFilter filter, MiningFilter parentFilter = null, int openMask = 1, IEnumerable<ThingDef> forceHiddenDefs = null, IEnumerable<SpecialThingFilterDef> forceHiddenFilters = null, bool forceHideHitPointsConfig = false, List<ThingDef> suppressSmallVolumeTags = null, Map map = null)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
			//IL_0120: Unknown result type (might be due to invalid IL or missing references)
			//IL_0122: Unknown result type (might be due to invalid IL or missing references)
			//IL_0156: Unknown result type (might be due to invalid IL or missing references)
			//IL_0173: Unknown result type (might be due to invalid IL or missing references)
			//IL_0179: Invalid comparison between Unknown and I4
			Widgets.DrawMenuSection(rect);
			Text.Font = (GameFont)0;
			float num = ((Rect)(ref rect)).width - 2f;
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(((Rect)(ref rect)).x + 1f, ((Rect)(ref rect)).y + 1f, num / 2f, 24f);
			if (Widgets.ButtonText(val, TaggedString.op_Implicit(Translator.Translate("ClearAll")), true, true, true, (TextAnchor?)null))
			{
				filter.SetDisallowAll();
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Checkbox_TurnedOff, (Map)null);
			}
			if (Widgets.ButtonText(new Rect(((Rect)(ref val)).xMax + 1f, ((Rect)(ref val)).y, ((Rect)(ref rect)).xMax - 1f - (((Rect)(ref val)).xMax + 1f), 24f), TaggedString.op_Implicit(Translator.Translate("AllowAll")), true, true, true, (TextAnchor?)null))
			{
				filter.SetAllowAll();
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Checkbox_TurnedOn, (Map)null);
			}
			Text.Font = (GameFont)1;
			((Rect)(ref rect)).yMin = ((Rect)(ref val)).yMax;
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(0f, 0f, ((Rect)(ref rect)).width - 16f, ThingFilterUI.viewHeight);
			Widgets.BeginScrollView(rect, ref scrollPosition, val2, true);
			float num2 = 2f;
			float num3 = num2;
			Rect val3 = default(Rect);
			((Rect)(ref val3))..ctor(0f, num2, ((Rect)(ref val2)).width, 9999f);
			Listing_TreeMiningFilter listing_TreeMiningFilter = new Listing_TreeMiningFilter(filter, parentFilter);
			((Listing)listing_TreeMiningFilter).Begin(val3);
			listing_TreeMiningFilter.DoCategoryChildren(0, map);
			((Listing)listing_TreeMiningFilter).End();
			if ((int)Event.current.type == 8)
			{
				ThingFilterUI.viewHeight = num3 + ((Listing)listing_TreeMiningFilter).CurHeight + 90f;
			}
			Widgets.EndScrollView();
		}
	}
	public class Listing_TreeMiningFilter : Listing_Tree
	{
		public MiningFilter filter;

		public MiningFilter parentFilter;

		public Listing_TreeMiningFilter(MiningFilter filter, MiningFilter parentFilter)
		{
			this.filter = filter;
			this.parentFilter = parentFilter;
		}

		public void DoCategoryChildren(int indentLevel, Map map)
		{
			foreach (ThingDef item in MiningUtility.CachedMineableThings.OrderBy((ThingDef n) => ((Def)n).label))
			{
				DoThingDef(item, indentLevel, map);
			}
		}

		private void DoThingDef(ThingDef tDef, int nestLevel, Map map)
		{
			//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_006f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0083: Unknown result type (might be due to invalid IL or missing references)
			//IL_009a: Unknown result type (might be due to invalid IL or missing references)
			string descriptionDetailed = tDef.DescriptionDetailed;
			float num = -4f;
			num -= 19f;
			if (map != null)
			{
				int count = map.resourceCounter.GetCount(tDef);
				if (count > 0)
				{
					string text = GenString.ToStringCached(count);
					Rect val = new Rect(0f, ((Listing)this).curY, ((Listing_Tree)this).LabelWidth + num, 40f);
					Text.Font = (GameFont)0;
					Text.Anchor = (TextAnchor)2;
					GUI.color = new Color(0.5f, 0.5f, 0.1f);
					Widgets.Label(val, text);
					num -= Text.CalcSize(text).x;
					GenUI.ResetLabelAlign();
					Text.Font = (GameFont)1;
					GUI.color = Color.white;
				}
			}
			((Listing_Tree)this).LabelLeft(TaggedString.op_Implicit(((Def)tDef).LabelCap), descriptionDetailed, nestLevel, num, (Color?)null, 0f);
			bool flag = filter.Allows(tDef);
			bool flag2 = flag;
			Widgets.Checkbox(new Vector2(((Listing_Tree)this).LabelWidth, ((Listing)this).curY), ref flag, ((Listing_Lines)this).lineHeight, false, true, (Texture2D)null, (Texture2D)null);
			if (flag != flag2)
			{
				filter.SetAllow(tDef, flag);
			}
			((Listing_Lines)this).EndLine();
		}
	}
	public class MiningFilter : IExposable
	{
		[Unsaved(false)]
		public HashSet<ThingDef> allowedDefs = new HashSet<ThingDef>();

		public MiningFilter()
		{
			allowedDefs = MiningUtility.CachedMineableThings.ToHashSet();
		}

		public virtual void CopyAllowancesFrom(MiningFilter other)
		{
			allowedDefs.Clear();
			foreach (ThingDef cachedMineableThing in MiningUtility.CachedMineableThings)
			{
				SetAllow(cachedMineableThing, other.Allows(cachedMineableThing));
			}
		}

		public void SetAllow(ThingDef thingDef, bool allow)
		{
			if (allow != Allows(thingDef))
			{
				if (allow)
				{
					allowedDefs.Add(thingDef);
				}
				else
				{
					allowedDefs.Remove(thingDef);
				}
			}
		}

		public void SetAllowAll()
		{
			allowedDefs.Clear();
			allowedDefs = MiningUtility.CachedMineableThings.ToHashSet();
		}

		public void SetDisallowAll()
		{
			allowedDefs.Clear();
		}

		public bool Allows(ThingDef def)
		{
			return allowedDefs.Contains(def);
		}

		public virtual void ExposeData()
		{
			Scribe_Collections.Look<ThingDef>(ref allowedDefs, "allowedDefs", (LookMode)0);
		}
	}
	public class MiningSettings : IExposable
	{
		public Comp_Mining parent;

		public MiningFilter filter;

		public MiningSettings()
		{
			filter = new MiningFilter();
		}

		public MiningSettings(Comp_Mining q)
		{
			parent = q;
			filter = new MiningFilter();
		}

		public void CopyFrom(MiningSettings other)
		{
			filter.CopyAllowancesFrom(other.filter);
		}

		public void ExposeData()
		{
			Scribe_Deep.Look<MiningFilter>(ref filter, "filter", Array.Empty<object>());
		}
	}
	[StaticConstructorOnStartup]
	public class MiningUtility
	{
		public static List<ThingDef> cachedMineableThings = new List<ThingDef>();

		public static List<ThingDef> CachedMineableThings
		{
			get
			{
				if (GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)cachedMineableThings))
				{
					IEnumerable<ThingDef> enumerable = DefDatabase<ThingDef>.AllDefs.Where((ThingDef def) => def.deepCommonality > 0f);
					if (GenCollection.EnumerableNullOrEmpty<ThingDef>(enumerable))
					{
						LogUtil.Error("Comp_Mining: cachedMineableThings list is empty, this is something that should never happen, vanilla contains many of these items.");
					}
					return cachedMineableThings = enumerable.ToList();
				}
				return cachedMineableThings;
			}
		}
	}
	public class DefModExt_GasHediffGiver : DefModExtension
	{
		public float radius;

		public HediffDef hediffDef;

		public int ticksBeforeApply;

		public int adjustSeverity;

		public bool checkToxicSensitivity = true;
	}
	public class Gas_HediffGiver : Gas
	{
		public const int tickRate = 30;

		public Dictionary<Pawn, int> affectedPawns = new Dictionary<Pawn, int>();

		public List<Pawn> pawnKeys;

		public List<int> intValues;

		public DefModExt_GasHediffGiver modExt => ((Def)((Thing)this).def).GetModExtension<DefModExt_GasHediffGiver>();

		public override void ExposeData()
		{
			((Gas)this).ExposeData();
			Scribe_Collections.Look<Pawn, int>(ref affectedPawns, "affectedPawns", (LookMode)3, (LookMode)1, ref pawnKeys, ref intValues, true, false, false);
		}

		public override void Tick()
		{
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			((Entity)this).Tick();
			if (!Gen.IsHashIntervalTick((Thing)(object)this, 30))
			{
				return;
			}
			if (affectedPawns == null)
			{
				affectedPawns = new Dictionary<Pawn, int>();
			}
			List<Pawn> touchedPawns = new List<Pawn>();
			foreach (Thing item in GenRadial.RadialDistinctThingsAround(((Thing)this).Position, ((Thing)this).Map, modExt.radius, true))
			{
				if (item == null)
				{
					continue;
				}
				Pawn val = (Pawn)(object)((item is Pawn) ? item : null);
				if (val != null)
				{
					touchedPawns.Add(val);
					if (affectedPawns.ContainsKey(val))
					{
						affectedPawns[val] += 30;
					}
					else
					{
						affectedPawns[val] = 30;
					}
				}
			}
			GenCollection.RemoveAll<Pawn, int>(affectedPawns, (Predicate<KeyValuePair<Pawn, int>>)((KeyValuePair<Pawn, int> x) => !touchedPawns.Contains(x.Key)));
			foreach (Pawn item2 in affectedPawns.Keys.ToList())
			{
				if (affectedPawns[item2] >= modExt.ticksBeforeApply)
				{
					affectedPawns[item2] -= modExt.ticksBeforeApply;
					if (modExt.checkToxicSensitivity)
					{
						HealthUtility.AdjustSeverity(item2, modExt.hediffDef, (float)modExt.adjustSeverity * StatExtension.GetStatValue((Thing)(object)item2, StatDefOf.ToxicEnvironmentResistance, true, -1));
					}
					else
					{
						HealthUtility.AdjustSeverity(item2, modExt.hediffDef, (float)modExt.adjustSeverity);
					}
				}
			}
		}
	}
	public class DefModExt_IntelligentAnimal : DefModExtension
	{
		public List<WorkTypeDef> enabledWorkTypeDefs = new List<WorkTypeDef>();

		public List<SkillLevelSetting> skillSettings = new List<SkillLevelSetting>();

		public bool automaticTraining;
	}
	public class DefModExt_RaceProperties : DefModExtension
	{
		public bool infectionsEnabled = true;

		public bool diseasesEnabled = true;

		public bool trainingDecays = true;
	}
	public class DesignatorSubCategoryDef : Def
	{
		public DesignationCategoryDef designationCategory;

		public bool enabled;

		public string iconPath;

		public Texture2D Icon => ContentFinder<Texture2D>.Get((!GenText.NullOrEmpty(iconPath)) ? iconPath : BaseContent.BadTexPath, true);
	}
	[HarmonyPatch(/*Could not decode attribute arguments.*/)]
	public static class Patch_Designator_Build_Visible
	{
		[HarmonyPrefix]
		public static bool Prefix(ref Designator_Build __instance, ref bool __result)
		{
			DefModExt_SubCategoryBuilding modExtension = ((Def)__instance.entDef).GetModExtension<DefModExt_SubCategoryBuilding>();
			if (modExtension != null)
			{
				DesignationCategoryDef val = Find.WindowStack.WindowOfType<MainTabWindow_Architect>()?.selectedDesPanel?.def ?? null;
				if (val != null && val.specialDesignatorClasses.Contains(typeof(Designator_SubCategory)) && modExtension.subCategory != null && val == modExtension.subCategory.designationCategory)
				{
					if (!WorldComp_ArchitectSubCategory.SelectedSubCategory.ContainsKey(val) || WorldComp_ArchitectSubCategory.SelectedSubCategory[val] == null)
					{
						if (modExtension.showOnlyInCategory)
						{
							__result = false;
							return false;
						}
					}
					else if (WorldComp_ArchitectSubCategory.SelectedSubCategory[val] != modExtension.subCategory)
					{
						__result = false;
						return false;
					}
				}
			}
			return true;
		}
	}
	[HarmonyPatch(typeof(HediffComp_Infecter), "CheckMakeInfection")]
	public static class Patch_HediffComp_Infecter_CheckMakeInfection
	{
		[HarmonyPrefix]
		public static bool PreFix(ref HediffComp_Infecter __instance)
		{
			DefModExt_RaceProperties modExtension = ((Def)((Thing)((HediffComp)__instance).Pawn).def).GetModExtension<DefModExt_RaceProperties>();
			if (modExtension != null && !modExtension.infectionsEnabled)
			{
				return false;
			}
			return true;
		}
	}
	[HarmonyPatch(typeof(Pawn_TrainingTracker), "TrainingTrackerTickRare")]
	public static class Patch_Pawn_TrainingTracker_TrainingTrackerTickRare
	{
		[HarmonyPrefix]
		public static bool PreFix(ref Pawn ___pawn)
		{
			DefModExt_RaceProperties modExtension = ((Def)((Thing)___pawn).def).GetModExtension<DefModExt_RaceProperties>();
			if (modExtension != null && !modExtension.trainingDecays)
			{
				return false;
			}
			return true;
		}
	}
	[HarmonyPatch(typeof(IncidentWorker_Disease), "PotentialVictims")]
	public static class Patch_IncidentWorker_Disease_PotentialVictims
	{
		[HarmonyPostfix]
		public static void PostFix(ref IEnumerable<Pawn> __result)
		{
			List<Pawn> list = new List<Pawn>();
			foreach (Pawn item in __result)
			{
				DefModExt_RaceProperties modExtension = ((Def)((Thing)item).def).GetModExtension<DefModExt_RaceProperties>();
				if (modExtension != null && !modExtension.diseasesEnabled)
				{
					list.Add(item);
				}
			}
			if (GenList.NullOrEmpty<Pawn>((IList<Pawn>)list))
			{
				return;
			}
			List<Pawn> list2 = __result.ToList();
			foreach (Pawn item2 in list)
			{
				list2.Remove(item2);
			}
			__result = list2;
		}
	}
	[HarmonyPatch(typeof(WorkGiver_Warden_DeliverFood), "JobOnThing")]
	public static class Patch_WardenDeliverFood_JobOnThing
	{
		[HarmonyPrefix]
		public static bool Prefix(ref WorkGiver_Warden_DeliverFood __instance, Pawn pawn, Thing t, bool forced, ref Job __result)
		{
			Pawn val = (Pawn)(object)((t is Pawn) ? t : null);
			if (val != null && !((Thing)val).def.race.EatsFood)
			{
				return false;
			}
			return true;
		}
	}
	[HarmonyPatch(typeof(WorkGiver_Warden_Feed), "JobOnThing")]
	public static class Patch_WardenFeed_JobOnThing
	{
		[HarmonyPrefix]
		public static bool Prefix(ref WorkGiver_Warden_Feed __instance, Pawn pawn, Thing t, bool forced)
		{
			Pawn val = (Pawn)(object)((t is Pawn) ? t : null);
			if (val != null && !((Thing)val).def.race.EatsFood)
			{
				return false;
			}
			return true;
		}
	}
	public class DefModExt_GrownBuilding : DefModExtension
	{
		public ThingDef matureInto;
	}
	public class Plant_GrownBuilding : Plant
	{
		public override void Tick()
		{
			((ThingWithComps)this).Tick();
			if (Gen.IsHashIntervalTick((Thing)(object)this, 2000))
			{
				((Entity)this).TickLong();
			}
		}

		public override void TickLong()
		{
			//IL_0079: Unknown result type (might be due to invalid IL or missing references)
			//IL_007f: Invalid comparison between Unknown and I4
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bb: Invalid comparison between Unknown and I4
			//IL_018c: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
			//IL_01fe: Unknown result type (might be due to invalid IL or missing references)
			//IL_0203: Unknown result type (might be due to invalid IL or missing references)
			//IL_020e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0216: Unknown result type (might be due to invalid IL or missing references)
			((Plant)this).TickLong();
			if (((Thing)this).Destroyed)
			{
				return;
			}
			DefModExt_GrownBuilding modExtension = ((Def)((Thing)this).def).GetModExtension<DefModExt_GrownBuilding>();
			if (modExtension != null && modExtension.matureInto != null && ((Plant)this).Growth >= 1f)
			{
				IntVec3 position = ((Thing)this).Position;
				Map map = ((Thing)this).Map;
				GenSpawn.Spawn(modExtension.matureInto, position, map, (WipeMode)0).SetFaction(Faction.OfPlayer, (Pawn)null);
				return;
			}
			if (PlantUtility.GrowthSeasonNow(((Thing)this).Map, ((Thing)this).def))
			{
				float growthInt = base.growthInt;
				bool num = (int)((Plant)this).LifeStage == 2;
				base.growthInt += ((Plant)this).GrowthPerTick * 2000f;
				if (base.growthInt > 1f)
				{
					base.growthInt = 1f;
				}
				if (((!num && (int)((Plant)this).LifeStage == 2) || (int)(growthInt * 10f) != (int)(base.growthInt * 10f)) && ((Plant)this).CurrentlyCultivated())
				{
					((Thing)this).Map.mapDrawer.MapMeshDirty(((Thing)this).Position, MapMeshFlagDef.op_Implicit(MapMeshFlagDefOf.Things));
				}
			}
			if (!((Plant)this).HasEnoughLightToGrow)
			{
				base.unlitTicks += 2000;
			}
			else
			{
				base.unlitTicks = 0;
			}
			base.ageInt += 2000;
			if (((Plant)this).Dying)
			{
				Map map2 = ((Thing)this).Map;
				bool isCrop = ((Plant)this).IsCrop;
				bool harvestableNow = ((Plant)this).HarvestableNow;
				bool dyingBecauseExposedToLight = ((Plant)this).DyingBecauseExposedToLight;
				int num2 = Mathf.CeilToInt(((Plant)this).CurrentDyingDamagePerTick * 2000f);
				((Thing)this).TakeDamage(new DamageInfo(DamageDefOf.Rotting, (float)num2, 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
				if (((Thing)this).Destroyed)
				{
					if (isCrop && ((Thing)this).def.plant.Harvestable && MessagesRepeatAvoider.MessageShowAllowed("MessagePlantDiedOfRot-" + ((Def)((Thing)this).def).defName, 240f))
					{
						Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(harvestableNow ? "MessagePlantDiedOfRot_LeftUnharvested" : ((!dyingBecauseExposedToLight) ? "MessagePlantDiedOfRot" : "MessagePlantDiedOfRot_ExposedToLight"), NamedArgument.op_Implicit(((Thing)this).GetCustomLabelNoCount(false)))), LookTargets.op_Implicit(new TargetInfo(((Thing)this).Position, map2, false)), MessageTypeDefOf.NegativeEvent, true);
					}
					return;
				}
			}
			base.cachedLabelMouseover = null;
		}
	}
	public class Designator_SubCategory : Designator
	{
		public DesignationCategoryDef CurrentCategory => Find.WindowStack.WindowOfType<MainTabWindow_Architect>().selectedDesPanel.def;

		public Designator_SubCategory()
		{
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			SetDefaultGizmoData();
			((Command)this).defaultDesc = TaggedString.op_Implicit(Translator.Translate("TabulaRasa.SubCatDesc"));
			base.soundDragSustain = SoundDefOf.Designate_DragAreaAdd;
			base.soundDragChanged = null;
			base.soundSucceeded = SoundDefOf.Designate_ZoneAdd;
			base.soundDragSustain = SoundDefOf.Designate_DragStandard;
			base.soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
			base.useMouseIcon = true;
			((Gizmo)this).order = -100f;
		}

		public void SetDefaultGizmoData()
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			((Command)this).defaultLabel = TaggedString.op_Implicit(Translator.Translate("TabulaRasa.SubCatLabel"));
			((Command)this).icon = (Texture)(object)ContentFinder<Texture2D>.Get("Toolbox/UI/CategoryNone", true);
		}

		public void UpdateGizmoData()
		{
			//IL_0031: Unknown result type (might be due to invalid IL or missing references)
			SetDefaultGizmoData();
			if (CurrentCategory != null && WorldComp_ArchitectSubCategory.SelectedSubCategory.ContainsKey(CurrentCategory))
			{
				((Command)this).defaultLabel = TaggedString.op_Implicit(((Def)WorldComp_ArchitectSubCategory.SelectedSubCategory[CurrentCategory]).LabelCap);
				if (!GenText.NullOrEmpty(WorldComp_ArchitectSubCategory.SelectedSubCategory[CurrentCategory].iconPath))
				{
					((Command)this).icon = (Texture)(object)WorldComp_ArchitectSubCategory.SelectedSubCategory[CurrentCategory].Icon;
				}
			}
		}

		public override void ProcessInput(Event ev)
		{
			if (((Designator)this).CheckCanInteract())
			{
				MakeFloatMenu(delegate(DesignatorSubCategoryDef def)
				{
					WorldComp_ArchitectSubCategory.SetSubCategoryForDesingationCat(CurrentCategory, def);
					UpdateGizmoData();
				});
			}
		}

		public void MakeFloatMenu(Action<DesignatorSubCategoryDef> selAction)
		{
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			//IL_0042: Unknown result type (might be due to invalid IL or missing references)
			//IL_004c: Expected O, but got Unknown
			//IL_0187: Unknown result type (might be due to invalid IL or missing references)
			//IL_0191: Expected O, but got Unknown
			//IL_0138: Unknown result type (might be due to invalid IL or missing references)
			//IL_015b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0165: Expected O, but got Unknown
			//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
			//IL_0111: Unknown result type (might be due to invalid IL or missing references)
			//IL_0124: Unknown result type (might be due to invalid IL or missing references)
			//IL_012e: Expected O, but got Unknown
			List<FloatMenuOption> list = new List<FloatMenuOption>();
			list.Add(new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("None")), (Action)delegate
			{
				selAction(null);
			}, (MenuOptionPriority)5, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
			List<DesignatorSubCategoryDef> list2 = DefDatabase<DesignatorSubCategoryDef>.AllDefs.Where((DesignatorSubCategoryDef sc) => sc.designationCategory == CurrentCategory).ToList();
			list2.OrderBy((DesignatorSubCategoryDef c) => ((Def)c).LabelCap);
			if (!GenList.NullOrEmpty<DesignatorSubCategoryDef>((IList<DesignatorSubCategoryDef>)list2))
			{
				foreach (DesignatorSubCategoryDef subCat in list2)
				{
					if (!subCat.enabled)
					{
						continue;
					}
					if (!GenText.NullOrEmpty(subCat.iconPath))
					{
						list.Add(new FloatMenuOption(TaggedString.op_Implicit(((Def)subCat).LabelCap), (Action)delegate
						{
							selAction(subCat);
						}, subCat.Icon, Color.white, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0, (HorizontalJustification)0, false));
					}
					else
					{
						list.Add(new FloatMenuOption(TaggedString.op_Implicit(((Def)subCat).LabelCap), (Action)delegate
						{
							selAction(subCat);
						}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
					}
				}
			}
			Find.WindowStack.Add((Window)new FloatMenu(list));
		}

		public override AcceptanceReport CanDesignateCell(IntVec3 loc)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			return AcceptanceReport.op_Implicit(true);
		}
	}
	public class WorldComp_ArchitectSubCategory : WorldComponent
	{
		public static Dictionary<DesignationCategoryDef, DesignatorSubCategoryDef> SelectedSubCategory = new Dictionary<DesignationCategoryDef, DesignatorSubCategoryDef>();

		public WorldComp_ArchitectSubCategory(World world)
			: base(world)
		{
		}

		public static void SetSubCategoryForDesingationCat(DesignationCategoryDef mainCat, DesignatorSubCategoryDef subCat)
		{
			if (subCat == null)
			{
				if (SelectedSubCategory.ContainsKey(mainCat))
				{
					SelectedSubCategory.Remove(mainCat);
				}
			}
			else if (SelectedSubCategory.ContainsKey(mainCat))
			{
				SelectedSubCategory[mainCat] = subCat;
			}
			else
			{
				SelectedSubCategory.Add(mainCat, subCat);
			}
		}
	}
	public class DefModExt_CustomMeteoriteStrike : DefModExtension
	{
		public ThingDef skyfaller;

		public ThingSetMakerDef thingSetMaker;
	}
	[HarmonyPatch(typeof(CompSchedule), "RecalculateAllowed")]
	public static class Patch_CompSchedule_RecalculateAllowed
	{
		[HarmonyPrefix]
		public static bool Prefix(CompSchedule __instance)
		{
			float num = GenLocalDate.DayPercent((Thing)(object)((ThingComp)__instance).parent);
			if (((Def)((Thing)((ThingComp)__instance).parent).def).HasModExtension<DefModExt_Nightlight>())
			{
				__instance.Allowed = !(num > __instance.Props.startTime) || !(num < __instance.Props.endTime);
				return false;
			}
			return true;
		}
	}
	[HarmonyPatch(/*Could not decode attribute arguments.*/)]
	public static class Patch_Caravan_NightResting
	{
		[HarmonyPrefix]
		public static bool Prefix(ref bool __result, ref Caravan __instance)
		{
			if (GenCollection.Any<Pawn>(__instance.pawns.InnerListForReading, (Predicate<Pawn>)((Pawn pawn) => ((Thing)pawn).def.race.needsRest)))
			{
				return true;
			}
			__result = false;
			return false;
		}
	}
	[HarmonyPatch(typeof(DaysWorthOfFoodCalculator), "ApproxDaysWorthOfFood", new Type[]
	{
		typeof(List<Pawn>),
		typeof(List<ThingDefCount>),
		typeof(PlanetTile),
		typeof(IgnorePawnsInventoryMode),
		typeof(Faction),
		typeof(WorldPath),
		typeof(float),
		typeof(int),
		typeof(bool)
	})]
	public static class Patch_DaysWorthOfFoodCalculator_ApproxDaysWorthOfFood
	{
		[HarmonyPrefix]
		public static bool Prefix(ref List<Pawn> pawns, List<ThingDefCount> extraFood, PlanetTile tile, IgnorePawnsInventoryMode ignoreInventory, Faction faction, WorldPath path, float nextTileCostLeft, int caravanTicksPerMove, bool assumeCaravanMoving)
		{
			List<Pawn> list = new List<Pawn>(pawns);
			list.RemoveAll((Pawn pawn) => !pawn.RaceProps.EatsFood);
			pawns = list;
			return true;
		}
	}
	public class HologramDef : Def
	{
		public List<string> hologramTags = new List<string>();

		public List<HologramLayer> hologramLayers = new List<HologramLayer>();
	}
	public class HologramLayer
	{
		public string texPath;

		public bool canChangeColor = true;

		public Color? defaultColor;

		public Material Hologram => MaterialPool.MatFrom(texPath, ShaderDatabase.TransparentPostLight);
	}
	public class IncidentWorker_CustomMeteoriteStrike : IncidentWorker
	{
		public override bool CanFireNowSub(IncidentParms parms)
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Expected O, but got Unknown
			Map map = (Map)parms.target;
			DefModExt_CustomMeteoriteStrike modExtension = ((Def)base.def).GetModExtension<DefModExt_CustomMeteoriteStrike>();
			IntVec3 cell;
			return TryFindCell(out cell, map, modExtension.skyfaller);
		}

		public override bool TryExecuteWorker(IncidentParms parms)
		{
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			//IL_0018: Expected O, but got Unknown
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
			//IL_0105: Unknown result type (might be due to invalid IL or missing references)
			//IL_010d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0110: Unknown result type (might be due to invalid IL or missing references)
			DefModExt_CustomMeteoriteStrike modExtension = ((Def)base.def).GetModExtension<DefModExt_CustomMeteoriteStrike>();
			Map val = (Map)parms.target;
			if (!TryFindCell(out var cell, val, modExtension.skyfaller))
			{
				return false;
			}
			List<Thing> list = modExtension.thingSetMaker.root.Generate();
			SkyfallerMaker.SpawnSkyfaller(modExtension.skyfaller, (IEnumerable<Thing>)list, cell, val);
			LetterDef val2 = ((list[0]?.def?.building?.isResourceRock).Value ? LetterDefOf.PositiveEvent : LetterDefOf.NeutralEvent);
			string text = GenText.CapitalizeFirst(string.Format(base.def.letterText, ((Def)list[0].def).label));
			((IncidentWorker)this).SendStandardLetter(base.def.letterLabel + ": " + ((Def)list[0].def).LabelCap, TaggedString.op_Implicit(text), val2, parms, LookTargets.op_Implicit(new TargetInfo(cell, val, false)), Array.Empty<NamedArgument>());
			return true;
		}

		public bool TryFindCell(out IntVec3 cell, Map map, ThingDef skyfaller)
		{
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			return CellFinderLoose.TryFindSkyfallerCell(skyfaller, map, TerrainAffordanceDefOf.Heavy, ref cell, 10, default(IntVec3), -1, false, false, false, false, true, true, (Predicate<IntVec3>)null);
		}
	}
	public class ITab_Hologram : ITab
	{
		public static readonly Vector2 WinSize = new Vector2(420f, 300f);

		public Building SelHolo => (Building)((ITab)this).SelThing;

		public Comp_HologramProjection HoloComp => ThingCompUtility.TryGetComp<Comp_HologramProjection>((Thing)(object)SelHolo);

		public ITab_Hologram()
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			((InspectTabBase)this).size = WinSize;
			((InspectTabBase)this).labelKey = "TabulaRasa.ITab_Hologram";
		}

		public override void FillTab()
		{
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0028: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			Rect rect = GenUI.ContractedBy(new Rect(0f, 0f, WinSize.x, WinSize.y), 10f);
			Func<List<FloatMenuOption>> hologramOptionsMaker = delegate
			{
				//IL_003a: Unknown result type (might be due to invalid IL or missing references)
				//IL_005c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0066: Expected O, but got Unknown
				//IL_008d: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
				//IL_00ae: Expected O, but got Unknown
				List<FloatMenuOption> list = new List<FloatMenuOption>();
				foreach (HologramDef def in HoloComp.viableHolos)
				{
					list.Add(new FloatMenuOption(TaggedString.op_Implicit(((Def)def).LabelCap), (Action)delegate
					{
						HoloComp.holoDef = def;
						HoloComp.ResetHoloColors();
					}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
				}
				if (!GenCollection.Any<FloatMenuOption>(list))
				{
					list.Add(new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("NoneBrackets")), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
				}
				return list;
			};
			DrawInformation(rect, hologramOptionsMaker);
		}

		public void DrawInformation(Rect rect, Func<List<FloatMenuOption>> hologramOptionsMaker)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0086: Unknown result type (might be due to invalid IL or missing references)
			//IL_0053: Unknown result type (might be due to invalid IL or missing references)
			//IL_005d: Expected O, but got Unknown
			//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
			//IL_0125: Unknown result type (might be due to invalid IL or missing references)
			//IL_012c: Expected O, but got Unknown
			//IL_012e: Unknown result type (might be due to invalid IL or missing references)
			//IL_013c: Unknown result type (might be due to invalid IL or missing references)
			//IL_015a: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a5: Unknown result type (might be due to invalid IL or missing references)
			GUI.BeginGroup(rect);
			Text.Font = (GameFont)1;
			if (Widgets.ButtonText(new Rect(0f, 0f, 150f, 29f), TaggedString.op_Implicit(Translator.Translate("TabulaRasa.ITab_HologramSelect")), true, false, true, (TextAnchor?)null))
			{
				Find.WindowStack.Add((Window)new FloatMenu(hologramOptionsMaker()));
			}
			HologramDef holoDef = HoloComp.holoDef;
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(0f, 45f, ((Rect)(ref rect)).width, 260f);
			GUI.BeginGroup(val);
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(4f, 4f, 128f, 128f);
			for (int i = 0; i < holoDef.hologramLayers.Count(); i++)
			{
				GUI.DrawTexture(val2, (Texture)(object)ContentFinder<Texture2D>.Get(holoDef.hologramLayers[i].texPath, true), (ScaleMode)2, true, 0f, HoloComp.hologramColors[i], 0f, 0f);
			}
			Rect val3 = default(Rect);
			((Rect)(ref val3))..ctor(136f, 4f, ((Rect)(ref val)).width - 128f, 260f);
			Listing_Standard val4 = new Listing_Standard();
			((Listing)val4).Begin(val3);
			val4.Label($"Current Holo: {((Def)holoDef).LabelCap}", -1f, (TipSignal?)null);
			((Listing)val4).GapLine(12f);
			for (int j = 0; j < holoDef.hologramLayers.Count(); j++)
			{
				if (holoDef.hologramLayers[j].canChangeColor)
				{
					val4.AddHoloColorPickerButton($"Layer {j}", HoloComp.hologramColors[j], HoloComp, j);
				}
			}
			((Listing)val4).End();
			GUI.EndGroup();
			GUI.EndGroup();
		}
	}
	public class DefModExt_Nightlight : DefModExtension
	{
	}
	[HarmonyPatch(typeof(HealthAIUtility), "FindBestMedicine")]
	public static class HealthAIUtility_FindBestMedicine
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn healer, Pawn patient, ref Thing __result)
		{
			//IL_0069: Unknown result type (might be due to invalid IL or missing references)
			//IL_009d: Unknown result type (might be due to invalid IL or missing references)
			if (__result != null && ThingCompUtility.TryGetComp<Comp_UseHealthPack>(__result) != null && HealthUtil.CanSealWounds(patient))
			{
				Predicate<Thing> predicate = (Thing m) => !ForbidUtility.IsForbidden(m, healer) && MedicalCareUtility.AllowsMedicine(patient.playerSettings.medCare, m.def) && ReservationUtility.CanReserve(healer, LocalTargetInfo.op_Implicit(m), 10, 1, (ReservationLayerDef)null, false) && ThingCompUtility.TryGetComp<Comp_UseHealthPack>(m) != null;
				Func<Thing, float> func = (Thing t) => StatExtension.GetStatValueAbstract((BuildableDef)(object)t.def, StatDefOf.MedicalPotency, (ThingDef)null);
				__result = GenClosest.ClosestThing_Global_Reachable(((Thing)patient).Position, ((Thing)patient).Map, (IEnumerable<Thing>)((Thing)patient).Map.listerThings.ThingsInGroup((ThingRequestGroup)14), (PathEndMode)3, TraverseParms.For(healer, (Danger)3, (TraverseMode)0, false, false, false, true), 9999f, predicate, func, false);
			}
		}
	}
	[HarmonyPatch(typeof(TendUtility), "DoTend")]
	internal static class Patch_TendUtility_DoTend
	{
		[HarmonyPrefix]
		public static bool Prefix(Pawn doctor, Pawn patient, Medicine medicine)
		{
			if (medicine != null && ThingCompUtility.TryGetComp<Comp_UseHealthPack>((Thing)(object)medicine) != null)
			{
				HealthUtil.TrySealWounds(patient, new List<HediffDef>());
				HealthUtil.TendAdditional(doctor, patient);
				if (medicine != null)
				{
					if (((Thing)medicine).stackCount > 1)
					{
						((Thing)medicine).stackCount = ((Thing)medicine).stackCount - 1;
					}
					if (!((Thing)medicine).Destroyed)
					{
						((Thing)medicine).Destroy((DestroyMode)0);
					}
				}
				return false;
			}
			return true;
		}
	}
	public class DefModExt_Fireproof : DefModExtension
	{
	}
	[HarmonyPatch(typeof(Thing), "TakeDamage")]
	public static class Patch_Thing_TakeDamage
	{
		[HarmonyPrefix]
		public static bool Prefix(DamageInfo dinfo, ref Thing __instance, ref DamageResult __result)
		{
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Expected O, but got Unknown
			Thing obj = __instance;
			Pawn val = (Pawn)(object)((obj is Pawn) ? obj : null);
			if (val != null && ((Def)((Thing)val).def).HasModExtension<DefModExt_Fireproof>() && ((DamageInfo)(ref dinfo)).Def == DamageDefOf.Flame)
			{
				__result = new DamageResult();
				return false;
			}
			return true;
		}
	}
	[HarmonyPatch(typeof(ResearchProjectDef), "CanBeResearchedAt")]
	public static class Patch_ResearchProjectDef_CanBeResearchedAt
	{
		[HarmonyPostfix]
		public static void Postfix(ResearchProjectDef __instance, ref bool __result, Building_ResearchBench bench, bool ignoreResearchBenchPowerStatus)
		{
			if (__result)
			{
				return;
			}
			if (!ignoreResearchBenchPowerStatus)
			{
				CompPowerTrader comp = ((ThingWithComps)bench).GetComp<CompPowerTrader>();
				if (comp != null && !comp.PowerOn)
				{
					return;
				}
			}
			DefModExt_ResearchBenchSubstitutes modExtension = ((Def)((Thing)bench).def).GetModExtension<DefModExt_ResearchBenchSubstitutes>();
			if (modExtension == null)
			{
				return;
			}
			if (modExtension.actLikeResearchBench.Contains(__instance.requiredResearchBuilding))
			{
				__result = true;
			}
			if (GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)__instance.requiredResearchFacilities))
			{
				return;
			}
			bool flag = true;
			foreach (ThingDef requiredResearchFacility in __instance.requiredResearchFacilities)
			{
				if (!modExtension.actLikeResearchFacility.Contains(requiredResearchFacility))
				{
					flag = false;
				}
			}
			__result = flag;
		}
	}
	public class DefModExt_ResearchBenchSubstitutes : DefModExtension
	{
		public TechLevel techLevel;

		public List<ThingDef> actLikeResearchBench = new List<ThingDef>();

		public List<ThingDef> actLikeResearchFacility = new List<ThingDef>();
	}
	public class DefModExt_AutoHealProps : DefModExtension
	{
		public int healTicks = 1000;

		public List<HediffDef> ignoreWhenHealing = new List<HediffDef>();

		public bool regrowParts = true;

		public int cureTicks = 1000;

		public bool removeInfections = true;

		public List<HediffDef> infectionsAllowed = new List<HediffDef>();

		public List<HediffDef> explicitRemovals = new List<HediffDef>();

		public int growthTicks = 1000;

		public string growthText = "Growth: ";

		public HediffDef protoBodyPart;

		public HediffDef curedBodyPart;

		public HediffDef autoHealHediff;
	}
	[Obsolete]
	public class Hediff_GrowingPart : Hediff_AddedPart
	{
		public override bool ShouldRemove => ((Hediff)this).Severity >= ((Hediff)this).def.maxSeverity;

		public override string TipStringExtra
		{
			get
			{
				StringBuilder stringBuilder = new StringBuilder();
				stringBuilder.Append(((HediffWithComps)this).TipStringExtra);
				stringBuilder.AppendLine(((Def)((Hediff)this).def).GetModExtension<DefModExt_AutoHealProps>().growthText + GenText.ToStringPercent(((Hediff)this).Severity));
				return stringBuilder.ToString();
			}
		}

		public override void ExposeData()
		{
			((Hediff_Implant)this).ExposeData();
		}

		public override void PostRemoved()
		{
			((HediffWithComps)this).PostRemoved();
			if (!(((Hediff)this).Severity >= 1f))
			{
				return;
			}
			Pawn pawn = ((Hediff)this).pawn;
			object obj;
			if (pawn == null)
			{
				obj = null;
			}
			else
			{
				Pawn_HealthTracker health = pawn.health;
				if (health == null)
				{
					obj = null;
				}
				else
				{
					HediffSet hediffSet = health.hediffSet;
					obj = ((hediffSet == null) ? null : hediffSet.GetFirstHediffOfDef(((Def)((Hediff)this).def).GetModExtension<DefModExt_AutoHealProps>().autoHealHediff, false)?.def);
				}
			}
			if (obj == null)
			{
				obj = null;
			}
			if (obj == null)
			{
				((Hediff)this).pawn.ReplaceHediffFromBodypart(((Hediff)this).Part, HediffDefOf.MissingBodyPart, TabulaRasaDefOf.TabulaRasa_RemovableHediff);
			}
			DefModExt_AutoHealProps modExtension = ((Def)obj).GetModExtension<DefModExt_AutoHealProps>();
			if (modExtension != null && modExtension.curedBodyPart != null)
			{
				((Hediff)this).pawn.ReplaceHediffFromBodypart(((Hediff)this).Part, HediffDefOf.MissingBodyPart, ((Def)((Hediff)this).pawn.health.hediffSet.GetFirstHediffOfDef(((Def)((Hediff)this).def).GetModExtension<DefModExt_AutoHealProps>().autoHealHediff, false).def).GetModExtension<DefModExt_AutoHealProps>().curedBodyPart);
			}
			else
			{
				((Hediff)this).pawn.ReplaceHediffFromBodypart(((Hediff)this).Part, HediffDefOf.MissingBodyPart, TabulaRasaDefOf.TabulaRasa_RemovableHediff);
			}
		}
	}
	public class Hediff_Removable : Hediff
	{
		public override bool ShouldRemove => true;
	}
	public class DefModExt_BasicConversion : DefModExtension
	{
		public XenotypeDef xenotype;

		public ThingDef structure;

		public bool structureOnMapChangesFaction;

		public bool forceDropEquipment;

		public bool killPawn;

		public PawnKindDef defaultPawnKind;
	}
	public class Hediff_BasicConversion : HediffWithComps
	{
		[CompilerGenerated]
		private sealed class <GetGizmos>d__0 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Hediff_BasicConversion <>4__this;

			private IEnumerator<Gizmo> <>7__wrap1;

			Gizmo IEnumerator<Gizmo>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <GetGizmos>d__0(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>7__wrap1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_009e: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
				//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
				//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
				//IL_00d0: Expected O, but got Unknown
				try
				{
					int num = <>1__state;
					Hediff_BasicConversion CS$<>8__locals3 = <>4__this;
					switch (num)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						if (!GenCollection.EnumerableNullOrEmpty<Gizmo>(CS$<>8__locals3.<>n__0()))
						{
							<>7__wrap1 = CS$<>8__locals3.<>n__0().GetEnumerator();
							<>1__state = -3;
							goto IL_007c;
						}
						goto IL_0096;
					case 1:
						<>1__state = -3;
						goto IL_007c;
					case 2:
						{
							<>1__state = -1;
							break;
						}
						IL_007c:
						if (<>7__wrap1.MoveNext())
						{
							Gizmo current = <>7__wrap1.Current;
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = null;
						goto IL_0096;
						IL_0096:
						if (DebugSettings.godMode)
						{
							<>2__current = (Gizmo)new Command_Action
							{
								defaultLabel = "DEV: Convert Now",
								defaultDesc = "Instantly converts the pawn right now.",
								action = delegate
								{
									CS$<>8__locals3.TryConvert();
								}
							};
							<>1__state = 2;
							return true;
						}
						break;
					}
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				if (<>7__wrap1 != null)
				{
					<>7__wrap1.Dispose();
				}
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
			{
				<GetGizmos>d__0 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <GetGizmos>d__0(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		[IteratorStateMachine(typeof(<GetGizmos>d__0))]
		public override IEnumerable<Gizmo> GetGizmos()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <GetGizmos>d__0(-2)
			{
				<>4__this = this
			};
		}

		public override void Tick()
		{
			((Hediff)this).Tick();
			if ((double)((Hediff)this).Severity >= 1.0)
			{
				TryConvert();
			}
		}

		public void TryConvert()
		{
			DefModExt_BasicConversion modExtension = ((Def)((Hediff)this).def).GetModExtension<DefModExt_BasicConversion>();
			if (modExtension.xenotype != null)
			{
				DoConversion(modExtension);
			}
			else if (modExtension.defaultPawnKind != null)
			{
				DoBasicConvert(modExtension);
			}
		}

		public void DoConversion(DefModExt_BasicConversion modExt)
		{
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Invalid comparison between Unknown and I4
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Invalid comparison between Unknown and I4
			List<Gene> endogenes = ((Hediff)this).pawn.genes.Endogenes;
			for (int num = endogenes.Count - 1; num >= 0; num--)
			{
				Gene val = endogenes[num];
				if ((int)val.def.endogeneCategory != 1 && (int)val.def.endogeneCategory != 2)
				{
					((Hediff)this).pawn.genes.RemoveGene(val);
				}
			}
			((Hediff)this).pawn.genes.SetXenotype(modExt.xenotype);
			((Hediff)this).pawn.health.RemoveHediff((Hediff)(object)this);
			if (modExt.structure == null)
			{
				return;
			}
			Pawn pawn = ((Hediff)this).pawn;
			object obj;
			if (pawn == null)
			{
				obj = null;
			}
			else
			{
				Map map = ((Thing)pawn).Map;
				if (map == null)
				{
					obj = null;
				}
				else
				{
					ListerBuildings listerBuildings = map.listerBuildings;
					obj = ((listerBuildings == null) ? null : listerBuildings.AllBuildingsColonistOfDef(modExt.structure)?.ToList());
				}
			}
			List<Building> list = (List<Building>)obj;
			if (!GenList.NullOrEmpty<Building>((IList<Building>)list))
			{
				Building val2 = list.First();
				if (val2 != null && modExt.structureOnMapChangesFaction)
				{
					((Thing)((Hediff)this).pawn).SetFaction(((Thing)val2).Faction, (Pawn)null);
				}
			}
		}

		public void DoBasicConvert(DefModExt_BasicConversion modExt)
		{
			//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
			//IL_0107: Unknown result type (might be due to invalid IL or missing references)
			//IL_0131: Unknown result type (might be due to invalid IL or missing references)
			//IL_015c: Unknown result type (might be due to invalid IL or missing references)
			PawnKindDef defaultPawnKind = modExt.defaultPawnKind;
			Faction ofPlayer = Faction.OfPlayer;
			float? num = ((Hediff)this).pawn.ageTracker.AgeBiologicalYearsFloat;
			float? num2 = ((Hediff)this).pawn.ageTracker.AgeChronologicalYearsFloat;
			GenPlace.TryPlaceThing((Thing)(object)PawnGenerator.GeneratePawn(new PawnGenerationRequest(defaultPawnKind, ofPlayer, (PawnGenerationContext)2, (PlanetTile?)null, true, false, false, false, false, 0f, false, true, false, false, false, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, num, num2, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false)), ((Thing)((Hediff)this).pawn).Position, ((Thing)((Hediff)this).pawn).Map, (ThingPlaceMode)0, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
			if (modExt.forceDropEquipment)
			{
				if (((Hediff)this).pawn.inventory != null)
				{
					((Hediff)this).pawn.inventory.DropAllNearPawn(((Thing)((Hediff)this).pawn).Position, false, false);
				}
				if (((Hediff)this).pawn.apparel != null)
				{
					((Hediff)this).pawn.apparel.DropAll(((Thing)((Hediff)this).pawn).Position, true, true, (Predicate<Apparel>)null);
				}
				if (((Hediff)this).pawn.equipment != null)
				{
					((Hediff)this).pawn.equipment.DropAllEquipment(((Thing)((Hediff)this).pawn).Position, true, false);
				}
			}
			if (modExt.killPawn)
			{
				((Thing)((Hediff)this).pawn).Kill((DamageInfo?)null, (Hediff)(object)this);
			}
			((Thing)((Hediff)this).pawn).Destroy((DestroyMode)0);
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private IEnumerable<Gizmo> <>n__0()
		{
			return ((HediffWithComps)this).GetGizmos();
		}
	}
	public class DefModExt_ThingProducer : DefModExtension
	{
		public ThingDef thingDef;

		public int productionTime = 1000;

		public int maxThings = 1;

		public string retrievalString = "Take Item";

		public bool requiresPower;
	}
	public class HediffGiver_Racial : HediffGiver
	{
		public override void OnIntervalPassed(Pawn pawn, Hediff cause)
		{
			((HediffGiver)this).TryApply(pawn, (List<Hediff>)null);
		}
	}
	public class HediffCompProperties_TooltipDescription : HediffCompProperties
	{
		public HediffCompProperties_TooltipDescription()
		{
			base.compClass = typeof(HediffComp_TooltipDescription);
		}
	}
	public class HediffComp_TooltipDescription : HediffComp
	{
		public override string CompTipStringExtra => ((Def)((Hediff)base.parent).def).description;
	}
	public class JobDriver_TakeFromProducer : JobDriver
	{
		[CompilerGenerated]
		private sealed class <>c__DisplayClass5_0
		{
			public Toil enter;

			internal void <MakeNewToils>b__0()
			{
				<>c__DisplayClass5_1 <>c__DisplayClass5_ = default(<>c__DisplayClass5_1);
				<>c__DisplayClass5_.actor = enter.actor;
				<>c__DisplayClass5_.producer = (Building_ThingProducer)(object)((LocalTargetInfo)(ref <>c__DisplayClass5_.actor.CurJob.targetA)).Thing;
				<MakeNewToils>g__action|5_1(ref <>c__DisplayClass5_);
			}
		}

		[StructLayout(LayoutKind.Auto)]
		[CompilerGenerated]
		private struct <>c__DisplayClass5_1
		{
			public Building_ThingProducer producer;

			public Pawn actor;
		}

		[CompilerGenerated]
		private sealed class <MakeNewToils>d__5 : IEnumerable<Toil>, IEnumerable, IEnumerator<Toil>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Toil <>2__current;

			private int <>l__initialThreadId;

			public JobDriver_TakeFromProducer <>4__this;

			private <>c__DisplayClass5_0 <>8__1;

			Toil IEnumerator<Toil>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <MakeNewToils>d__5(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				<>8__1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_009e: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a8: Expected O, but got Unknown
				//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
				int num = <>1__state;
				JobDriver_TakeFromProducer jobDriver_TakeFromProducer = <>4__this;
				switch (num)
				{
				default:
					return false;
				case 0:
					<>1__state = -1;
					<>8__1 = new <>c__DisplayClass5_0();
					ToilFailConditions.FailOnDespawnedOrNull<JobDriver_TakeFromProducer>(jobDriver_TakeFromProducer, (TargetIndex)1);
					<>2__current = Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)4, false);
					<>1__state = 1;
					return true;
				case 1:
				{
					<>1__state = -1;
					Toil val = Toils_General.Wait(500, (TargetIndex)0);
					ToilFailConditions.FailOnCannotTouch<Toil>(val, (TargetIndex)1, (PathEndMode)4);
					ToilEffects.WithProgressBarToilDelay(val, (TargetIndex)1, false, -0.5f);
					<>2__current = val;
					<>1__state = 2;
					return true;
				}
				case 2:
					<>1__state = -1;
					<>8__1.enter = new Toil();
					<>8__1.enter.initAction = delegate
					{
						<>c__DisplayClass5_1 <>c__DisplayClass5_ = default(<>c__DisplayClass5_1);
						<>c__DisplayClass5_.actor = <>8__1.enter.actor;
						<>c__DisplayClass5_.producer = (Building_ThingProducer)(object)((LocalTargetInfo)(ref <>c__DisplayClass5_.actor.CurJob.targetA)).Thing;
						<MakeNewToils>g__action|5_1(ref <>c__DisplayClass5_);
					};
					<>8__1.enter.defaultCompleteMode = (ToilCompleteMode)1;
					<>2__current = <>8__1.enter;
					<>1__state = 3;
					return true;
				case 3:
					<>1__state = -1;
					return false;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Toil> IEnumerable<Toil>.GetEnumerator()
			{
				<MakeNewToils>d__5 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <MakeNewToils>d__5(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Toil>)this).GetEnumerator();
			}
		}

		public float WorkTotal { get; private set; }

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			Pawn pawn = base.pawn;
			LocalTargetInfo targetA = base.job.targetA;
			Job job = base.job;
			return ReservationUtility.Reserve(pawn, targetA, job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false);
		}

		[IteratorStateMachine(typeof(<MakeNewToils>d__5))]
		public override IEnumerable<Toil> MakeNewToils()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <MakeNewToils>d__5(-2)
			{
				<>4__this = this
			};
		}

		[CompilerGenerated]
		internal static void <MakeNewToils>g__action|5_1(ref <>c__DisplayClass5_1 P_0)
		{
			P_0.producer.TakeItem(P_0.actor);
		}
	}
	public class DefModExt_ExtraStrings : DefModExtension
	{
		public string extraReportString;
	}
	[HarmonyPatch(typeof(Pawn_HealthTracker), "AddHediff", new Type[]
	{
		typeof(Hediff),
		typeof(BodyPartRecord),
		typeof(DamageInfo?),
		typeof(DamageResult)
	})]
	public static class Patch_Pawn_HealthTracker_AddHediff
	{
		[HarmonyPrefix]
		public static bool Prefix(Pawn_HealthTracker __instance, Pawn ___pawn, Hediff hediff, BodyPartRecord part = null, DamageInfo? dinfo = null, DamageResult result = null)
		{
			DefModExt_DiseaseImmunity modExtension = ((Def)((Thing)___pawn).def).GetModExtension<DefModExt_DiseaseImmunity>();
			if (modExtension != null && !GenList.NullOrEmpty<HediffDef>((IList<HediffDef>)modExtension.hediffs) && modExtension.hediffs.Contains(hediff.def))
			{
				return false;
			}
			object obj;
			if (___pawn == null)
			{
				obj = null;
			}
			else
			{
				Pawn_HealthTracker health = ___pawn.health;
				if (health == null)
				{
					obj = null;
				}
				else
				{
					HediffSet hediffSet = health.hediffSet;
					if (hediffSet == null)
					{
						obj = null;
					}
					else
					{
						List<Hediff> hediffs = hediffSet.hediffs;
						if (hediffs == null)
						{
							obj = null;
						}
						else
						{
							Hediff obj2 = hediffs.Find((Hediff h) => HediffUtility.TryGetComp<HediffComp_PassiveHealing>(h) != null);
							obj = ((obj2 != null) ? HediffUtility.TryGetComp<HediffComp_PassiveHealing>(obj2) : null);
						}
					}
				}
			}
			HediffComp_PassiveHealing hediffComp_PassiveHealing = (HediffComp_PassiveHealing)obj;
			if (hediffComp_PassiveHealing != null && hediffComp_PassiveHealing.Props.preventSicknesses && ((GenList.NullOrEmpty<HediffDef>((IList<HediffDef>)hediffComp_PassiveHealing.Props.sicknessWhitelist) && hediff.def.makesSickThought) || hediffComp_PassiveHealing.Props.sicknessWhitelist.Contains(hediff.def)))
			{
				return false;
			}
			return true;
		}
	}
	[Obsolete]
	public class HediffCompProperties_AutoHeal : HediffCompProperties
	{
		public int healTicks = 1000;

		public List<HediffDef> ignoreWhenHealing = new List<HediffDef>();

		public bool regrowParts = true;

		public int cureTicks = 1000;

		public bool removeInfections = true;

		public List<HediffDef> infectionsAllowed = new List<HediffDef>();

		public List<HediffDef> explicitRemovals = new List<HediffDef>();

		public int growthTicks = 1000;

		public string growthText = "Growth: ";

		public HediffDef protoBodyPart;

		public HediffDef curedBodyPart;

		public HediffDef autoHealHediff;

		public HediffCompProperties_AutoHeal()
		{
			base.compClass = typeof(HediffComp_AutoHeal);
		}
	}
	[Obsolete]
	public class HediffComp_AutoHeal : HediffComp
	{
		public int ticksUntilNextHeal;

		public int ticksUntilNextGrow;

		public int ticksUntilNextCure;

		public HediffCompProperties_AutoHeal Props => (HediffCompProperties_AutoHeal)(object)base.props;

		public override void CompExposeData()
		{
			((HediffComp)this).CompExposeData();
			Scribe_Values.Look<int>(ref ticksUntilNextGrow, "ticksUntilNextGrow", 0, false);
			Scribe_Values.Look<int>(ref ticksUntilNextHeal, "ticksUntilNextHeal", 0, false);
			Scribe_Values.Look<int>(ref ticksUntilNextCure, "ticksUntilNextCure", 0, false);
		}

		public override void CompPostMake()
		{
			((HediffComp)this).CompPostMake();
			HealthUtil.SetNextTick(ticksUntilNextHeal, Props.healTicks);
			HealthUtil.SetNextTick(ticksUntilNextGrow, Props.growthTicks);
			HealthUtil.SetNextTick(ticksUntilNextCure, Props.cureTicks);
		}

		public override void CompPostTick(ref float severityAdjustment)
		{
			((HediffComp)this).CompPostTick(ref severityAdjustment);
			if (Current.Game.tickManager.TicksGame >= ticksUntilNextHeal)
			{
				HealthUtil.TrySealWounds(((Hediff)base.parent).pawn, Props.ignoreWhenHealing);
				HealthUtil.SetNextTick(ticksUntilNextHeal, Props.healTicks);
			}
			if (Current.Game.tickManager.TicksGame >= ticksUntilNextGrow && Props.regrowParts)
			{
				HealthUtil.TryRegrowBodyparts(((Hediff)base.parent).pawn, Props.protoBodyPart);
				HealthUtil.SetNextTick(ticksUntilNextGrow, Props.growthTicks);
			}
			if (Current.Game.tickManager.TicksGame >= ticksUntilNextCure && Props.removeInfections)
			{
				HealthUtil.TryCureInfections(((Hediff)base.parent).pawn, Props.infectionsAllowed, Props.explicitRemovals);
				HealthUtil.SetNextTick(ticksUntilNextCure, Props.cureTicks);
			}
		}
	}
	public class DefModExt_DiseaseImmunity : DefModExtension
	{
		public List<HediffDef> hediffs = new List<HediffDef>();
	}
	public class DefModExt_EnergyNeed : DefModExtension
	{
		public bool canConsumeBatteries = true;

		public bool canChargeWirelessly = true;

		public bool canChargeFromSocket = true;

		public bool canHibernate = true;
	}
	[HarmonyPatch(/*Could not decode attribute arguments.*/)]
	public static class Patch_Building_Door_DoorPowerOn
	{
		[HarmonyPostfix]
		public static void Postfix(ref bool __result, Building_Door __instance)
		{
			if (((Def)((Thing)__instance).def).HasModExtension<DefModExt_SelfPoweredDoor>())
			{
				__result = true;
			}
		}
	}
	public struct Condition : IEquatable<Condition>
	{
		public ConditionType condition;

		public object data;

		public Condition(ConditionType condition, object data)
		{
			this.condition = condition;
			this.data = data;
		}

		public override string ToString()
		{
			return $"Condition_{condition}_{data}";
		}

		public bool Equals(Condition other)
		{
			if (data == other.data)
			{
				return condition == other.condition;
			}
			return false;
		}

		public bool Passes(object toCheck)
		{
			switch (condition)
			{
			case ConditionType.IsType:
				if (toCheck.GetType().ToString() == "Psychology.PsychologyPawn" && data.ToString() == "Verse.Pawn")
				{
					return true;
				}
				if (toCheck.GetType() == data.GetType() || object.Equals(toCheck.GetType(), data))
				{
					return true;
				}
				break;
			case ConditionType.IsTypeStringMatch:
				if (toCheck.GetType().ToString() == (string)toCheck)
				{
					return true;
				}
				break;
			case ConditionType.ThingHasComp:
			{
				string dataTypeString = data?.ToString();
				ThingWithComps val = (ThingWithComps)((toCheck is ThingWithComps) ? toCheck : null);
				if (val != null && GenCollection.Any<ThingComp>(val.AllComps, (Predicate<ThingComp>)delegate(ThingComp comp)
				{
					Type type = comp?.props?.compClass;
					return (object)type != null && (type.ToString() == dataTypeString || type.BaseType?.ToString() == dataTypeString);
				}))
				{
					return true;
				}
				break;
			}
			}
			return false;
		}
	}
	public enum ConditionType
	{
		IsType,
		IsTypeStringMatch,
		ThingHasComp,
		HediffHasComp
	}
	public abstract class FloatMenuPatch
	{
		public abstract IEnumerable<KeyValuePair<Condition, Func<Vector3, Pawn, Thing, List<FloatMenuOption>>>> GetFloatMenus();
	}
	public class DefModExt_ApparelAlts : DefModExtension
	{
		public List<ApparelAlts> apparelAlts = new List<ApparelAlts>();

		public Dictionary<string, ApparelAlts> apparelAltData;

		public ApparelAlts TryGetAltApparelData(string headTypeDef)
		{
			if (apparelAltData == null)
			{
				apparelAltData = new Dictionary<string, ApparelAlts>();
				foreach (ApparelAlts apparelAlt in apparelAlts)
				{
					for (int i = 0; i < apparelAlt.headTypeDef.Count; i++)
					{
						string text = apparelAlt.headTypeDef[i];
						if (string.IsNullOrWhiteSpace(text))
						{
							LogUtil.Error("Missing <headTypeDef> tag in apparelAlts list item.");
							continue;
						}
						if (apparelAltData.ContainsKey(text))
						{
							LogUtil.Error("Duplicate apparel data for " + text);
						}
						if (DefDatabase<HeadTypeDef>.GetNamedSilentFail(text) == null)
						{
							LogUtil.Warning("Could not find def for headTypeDef named '" + text + "'.");
						}
						apparelAltData.Add(text, apparelAlt);
					}
				}
			}
			if (headTypeDef == null)
			{
				return null;
			}
			return GenCollection.TryGetValue<string, ApparelAlts>((IReadOnlyDictionary<string, ApparelAlts>)apparelAltData, headTypeDef, (ApparelAlts)null);
		}
	}
	[HarmonyPatch(typeof(ApparelGraphicRecordGetter), "TryGetGraphicApparel")]
	public static class Patch_ApparelGraphicRecordGetter_TryGetGraphicApparel
	{
		public static string curHeadTypeDef;

		[HarmonyPostfix]
		public static void Postfix(Apparel apparel, BodyTypeDef bodyType, ref ApparelGraphicRecord rec, bool __result)
		{
			//IL_023a: Unknown result type (might be due to invalid IL or missing references)
			//IL_023f: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a7: Unknown result type (might be due to invalid IL or missing references)
			//IL_01ad: Unknown result type (might be due to invalid IL or missing references)
			if (curHeadTypeDef == null || !__result)
			{
				return;
			}
			ApparelAlts apparelAlts = ((Def)((Thing)apparel).def).GetModExtension<DefModExt_ApparelAlts>()?.TryGetAltApparelData(curHeadTypeDef);
			if (apparelAlts == null)
			{
				return;
			}
			string text = ((Def)(((Thing)apparel).StyleDef?)).defName;
			text = text?.Substring(0, text.IndexOf('_'));
			bool flag = text != null && !string.IsNullOrEmpty(((Thing)apparel).StyleDef.wornGraphicPath) && apparelAlts.affectStyles && apparelAlts.path != null && apparelAlts.IsAllowedStyle(text);
			string text2;
			if (((Thing)apparel).def.apparel.LastLayer == ApparelLayerDefOf.Overhead || ((Thing)apparel).def.apparel.LastLayer == ApparelLayerDefOf.EyeCover || PawnRenderUtility.RenderAsPack(apparel) || apparel.WornGraphicPath == BaseContent.PlaceholderImagePath || apparel.WornGraphicPath == BaseContent.PlaceholderGearImagePath)
			{
				text2 = apparelAlts.path ?? (apparel.WornGraphicPath + "_" + curHeadTypeDef);
				if (flag)
				{
					text2 = text2 + "_" + text;
				}
			}
			else
			{
				text2 = ((apparelAlts.path != null) ? (apparelAlts.path + "_" + ((Def)bodyType).defName) : (apparel.WornGraphicPath + "_" + curHeadTypeDef + "_" + ((Def)bodyType).defName));
				if (flag)
				{
					text2 = text2 + "_" + text;
				}
			}
			Shader val = ShaderDatabase.Cutout;
			if (((Thing)apparel).def.apparel.useWornGraphicMask)
			{
				val = ShaderDatabase.CutoutComplex;
			}
			Graphic val2;
			try
			{
				val2 = GraphicDatabase.Get<Graphic_Multi>(text2, val, ((Thing)apparel).def.graphicData.drawSize, ((Thing)apparel).DrawColor);
			}
			catch
			{
				val2 = null;
			}
			if (val2 == null || (Object)(object)val2.MatSingle == (Object)null)
			{
				LogUtil.Warning("Could not find alternate head apparel textures at '" + text2 + "' for head '" + curHeadTypeDef + "' and apparel '" + ((Def)((Thing)apparel).def).defName + " (" + ((Def)((Thing)apparel).def).fileName + ")'.");
			}
			else
			{
				rec = new ApparelGraphicRecord(val2, apparel);
			}
		}
	}
	public class TraitEntryAdvanced
	{
		public TraitDef def;

		public int degree;

		public float chance = 100f;

		public float commonalityMale = -1f;

		public float commonalityFemale = -1f;
	}
	public class ApparelAlts
	{
		public List<string> headTypeDef;

		public string path;

		public bool affectStyles = true;

		public List<string> styleWhitelist = new List<string>();

		public static HashSet<string> whitelist;

		public List<string> styleBlacklist = new List<string>();

		public static HashSet<string> blacklist;

		public bool IsAllowedStyle(string styleName)
		{
			if (blacklist == null)
			{
				blacklist = new HashSet<string>();
				GenCollection.AddRange<string>(blacklist, styleBlacklist);
			}
			return blacklist.Contains(styleName);
		}
	}
	public class DefModExt_SelfPoweredDoor : DefModExtension
	{
	}
	public class Win_HologramColorPicker : Window
	{
		private enum Controls
		{
			colourPicker,
			huePicker,
			alphaPicker,
			none
		}

		private Controls _activeControl = Controls.none;

		private Texture2D _colourPickerBG;

		private Texture2D _huePickerBG;

		private Texture2D _alphaPickerBG;

		private Texture2D _tempPreviewBG;

		private Texture2D _previewBG;

		private Texture2D _pickerAlphaBG;

		private Texture2D _sliderAlphaBG;

		private Texture2D _previewAlphaBG;

		private Color _alphaBGColorA = Color.white;

		private Color _alphaBGColorB = new Color(0.85f, 0.85f, 0.85f);

		private int _pickerSize = 300;

		private int _sliderWidth = 15;

		private int _alphaBGBlockSize = 10;

		private int _previewSize = 90;

		private int _handleSize = 10;

		private float _margin = 6f;

		private float _fieldHeight = 30f;

		private float _huePosition;

		private float _alphaPosition;

		private float _unitsPerPixel;

		private float _H;

		private float _S = 1f;

		private float _V = 1f;

		private float _A = 1f;

		private Vector2 _position = Vector2.zero;

		private string _hexOut;

		private string _hexIn;

		private Action<Color> _callback;

		public Color curColour = Color.blue;

		public Color tempColour = Color.white;

		private Vector2? _initialPosition;

		public static bool first;

		public Comp_HologramProjection holoComp;

		public int colorLayer;

		public override Vector2 InitialSize => new Vector2((float)_pickerSize + 3f * _margin + (float)(2 * _sliderWidth) + (float)(2 * _previewSize) + 36f, (float)_pickerSize + 36f);

		public Vector2 InitialPosition => (Vector2)(((??)_initialPosition) ?? (new Vector2((float)UI.screenWidth - ((Window)this).InitialSize.x, (float)UI.screenHeight - ((Window)this).InitialSize.y) / 2f));

		public float UnitsPerPixel
		{
			get
			{
				if (_unitsPerPixel == 0f)
				{
					_unitsPerPixel = 1f / (float)_pickerSize;
				}
				return _unitsPerPixel;
			}
		}

		public float H
		{
			get
			{
				return _H;
			}
			set
			{
				_H = Mathf.Clamp(value, 0f, 1f);
				NotifyHSVUpdated();
				CreateColourPickerBG();
				CreateAlphaPickerBG();
			}
		}

		public float S
		{
			get
			{
				return _S;
			}
			set
			{
				_S = Mathf.Clamp(value, 0f, 1f);
				NotifyHSVUpdated();
				CreateAlphaPickerBG();
			}
		}

		public float V
		{
			get
			{
				return _V;
			}
			set
			{
				_V = Mathf.Clamp(value, 0f, 1f);
				NotifyHSVUpdated();
				CreateAlphaPickerBG();
			}
		}

		public float A
		{
			get
			{
				return _A;
			}
			set
			{
				_A = Mathf.Clamp(value, 0f, 1f);
				NotifyHSVUpdated();
				CreateColourPickerBG();
			}
		}

		public Texture2D ColourPickerBG
		{
			get
			{
				if ((Object)(object)_colourPickerBG == (Object)null)
				{
					CreateColourPickerBG();
				}
				return _colourPickerBG;
			}
		}

		public Texture2D HuePickerBG
		{
			get
			{
				if ((Object)(object)_huePickerBG == (Object)null)
				{
					CreateHuePickerBG();
				}
				return _huePickerBG;
			}
		}

		public Texture2D AlphaPickerBG
		{
			get
			{
				if ((Object)(object)_alphaPickerBG == (Object)null)
				{
					CreateAlphaPickerBG();
				}
				return _alphaPickerBG;
			}
		}

		public Texture2D TempPreviewBG
		{
			get
			{
				//IL_0016: Unknown result type (might be due to invalid IL or missing references)
				if ((Object)(object)_tempPreviewBG == (Object)null)
				{
					CreatePreviewBG(ref _tempPreviewBG, tempColour);
				}
				return _tempPreviewBG;
			}
		}

		public Texture2D PreviewBG
		{
			get
			{
				//IL_0016: Unknown result type (might be due to invalid IL or missing references)
				if ((Object)(object)_previewBG == (Object)null)
				{
					CreatePreviewBG(ref _previewBG, curColour);
				}
				return _previewBG;
			}
		}

		public Texture2D PickerAlphaBG
		{
			get
			{
				if ((Object)(object)_pickerAlphaBG == (Object)null)
				{
					CreateAlphaBG(ref _pickerAlphaBG, _pickerSize, _pickerSize);
				}
				return _pickerAlphaBG;
			}
		}

		public Texture2D SliderAlphaBG
		{
			get
			{
				if ((Object)(object)_sliderAlphaBG == (Object)null)
				{
					CreateAlphaBG(ref _sliderAlphaBG, _sliderWidth, _pickerSize);
				}
				return _sliderAlphaBG;
			}
		}

		public Texture2D PreviewAlphaBG
		{
			get
			{
				if ((Object)(object)_previewAlphaBG == (Object)null)
				{
					CreateAlphaBG(ref _previewAlphaBG, _previewSize, _previewSize);
				}
				return _previewAlphaBG;
			}
		}

		public Win_HologramColorPicker(Color color, Comp_HologramProjection comp, int layer, Action<Color> callback = null, Vector2? position = null)
			: base((IWindowDrawing)null)
		{
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			//IL_008f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0094: Unknown result type (might be due to invalid IL or missing references)
			//IL_009a: Unknown result type (might be due to invalid IL or missing references)
			//IL_009f: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
			//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
			_callback = callback;
			_initialPosition = position;
			curColour = color;
			holoComp = comp;
			colorLayer = layer;
			NotifyRGBUpdated();
		}

		public void NotifyHSVUpdated()
		{
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			tempColour = HSV.ToRGBA(H, S, V);
			tempColour.a = A;
			CreatePreviewBG(ref _tempPreviewBG, tempColour);
			_hexOut = (_hexIn = RGBtoHex(tempColour));
		}

		public void NotifyRGBUpdated()
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
			HSV.ToHSV(tempColour, out _H, out _S, out _V);
			_A = tempColour.a;
			CreateColourPickerBG();
			CreateHuePickerBG();
			CreateAlphaPickerBG();
			_huePosition = (1f - _H) / UnitsPerPixel;
			_position.x = _S / UnitsPerPixel;
			_position.y = (1f - _V) / UnitsPerPixel;
			_alphaPosition = (1f - _A) / UnitsPerPixel;
			CreatePreviewBG(ref _tempPreviewBG, tempColour);
			_hexOut = (_hexIn = RGBtoHex(tempColour));
		}

		public void SetColor()
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Unknown result type (might be due to invalid IL or missing references)
			curColour = tempColour;
			holoComp.hologramColors[colorLayer] = curColour;
			CreatePreviewBG(ref _previewBG, tempColour);
		}

		private void SwapTexture(ref Texture2D tex, Texture2D newTex)
		{
			Object.Destroy((Object)(object)tex);
			tex = newTex;
		}

		private void CreateColourPickerBG()
		{
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Expected O, but got Unknown
			//IL_0053: Unknown result type (might be due to invalid IL or missing references)
			int pickerSize = _pickerSize;
			int pickerSize2 = _pickerSize;
			float unitsPerPixel = UnitsPerPixel;
			float unitsPerPixel2 = UnitsPerPixel;
			Texture2D val = new Texture2D(pickerSize, pickerSize2);
			for (int i = 0; i < pickerSize; i++)
			{
				for (int j = 0; j < pickerSize2; j++)
				{
					float s = (float)i * unitsPerPixel;
					float v = (float)j * unitsPerPixel2;
					val.SetPixel(i, j, HSV.ToRGBA(H, s, v, A));
				}
			}
			val.Apply();
			SwapTexture(ref _colourPickerBG, val);
		}

		private void CreateHuePickerBG()
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000d: Expected O, but got Unknown
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			Texture2D val = new Texture2D(1, _pickerSize);
			int pickerSize = _pickerSize;
			float num = 1f / (float)pickerSize;
			for (int i = 0; i < pickerSize; i++)
			{
				val.SetPixel(0, i, HSV.ToRGBA(num * (float)i, 1f, 1f));
			}
			val.Apply();
			SwapTexture(ref _huePickerBG, val);
		}

		private void CreateAlphaPickerBG()
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000d: Expected O, but got Unknown
			//IL_0049: Unknown result type (might be due to invalid IL or missing references)
			Texture2D val = new Texture2D(1, _pickerSize);
			int pickerSize = _pickerSize;
			float num = 1f / (float)pickerSize;
			for (int i = 0; i < pickerSize; i++)
			{
				val.SetPixel(0, i, new Color(tempColour.r, tempColour.g, tempColour.b, (float)i * num));
			}
			val.Apply();
			SwapTexture(ref _alphaPickerBG, val);
		}

		private void CreateAlphaBG(ref Texture2D bg, int width, int height)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0008: Expected O, but got Unknown
			//IL_0024: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Unknown result type (might be due to invalid IL or missing references)
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			//IL_005c: Unknown result type (might be due to invalid IL or missing references)
			Texture2D val = new Texture2D(width, height);
			Color[] array = (Color[])(object)new Color[_alphaBGBlockSize * _alphaBGBlockSize];
			for (int i = 0; i < array.Length; i++)
			{
				array[i] = _alphaBGColorA;
			}
			Color[] array2 = (Color[])(object)new Color[_alphaBGBlockSize * _alphaBGBlockSize];
			for (int j = 0; j < array2.Length; j++)
			{
				array2[j] = _alphaBGColorB;
			}
			int num = 0;
			for (int k = 0; k < width; k += _alphaBGBlockSize)
			{
				int num2 = num;
				for (int l = 0; l < height; l += _alphaBGBlockSize)
				{
					val.SetPixels(k, l, _alphaBGBlockSize, _alphaBGBlockSize, (num2 % 2 == 0) ? array : array2);
					num2++;
				}
				num++;
			}
			val.Apply();
			SwapTexture(ref bg, val);
		}

		public void CreatePreviewBG(ref Texture2D bg, Color col)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			SwapTexture(ref bg, SolidColorMaterials.NewSolidColorTexture(col));
		}

		public void PickerAction(Vector2 pos)
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			_S = UnitsPerPixel * pos.x;
			_V = 1f - UnitsPerPixel * pos.y;
			CreateAlphaPickerBG();
			NotifyHSVUpdated();
			_position = pos;
		}

		public void HueAction(float pos)
		{
			H = 1f - UnitsPerPixel * pos;
			_huePosition = pos;
		}

		public void AlphaAction(float pos)
		{
			A = 1f - UnitsPerPixel * pos;
			_alphaPosition = pos;
		}

		public override void SetInitialSizeAndPosition()
		{
			//IL_0003: Unknown result type (might be due to invalid IL or missing references)
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			//IL_0051: Unknown result type (might be due to invalid IL or missing references)
			//IL_0068: Unknown result type (might be due to invalid IL or missing references)
			//IL_0078: Unknown result type (might be due to invalid IL or missing references)
			//IL_008f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0095: Unknown result type (might be due to invalid IL or missing references)
			//IL_009b: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
			Vector2 val = default(Vector2);
			((Vector2)(ref val))..ctor(Mathf.Min(((Window)this).InitialSize.x, (float)UI.screenWidth), Mathf.Min(((Window)this).InitialSize.y, (float)UI.screenHeight - 35f));
			Vector2 val2 = default(Vector2);
			((Vector2)(ref val2))..ctor(Mathf.Max(0f, Mathf.Min(InitialPosition.x, (float)UI.screenWidth - val.x)), Mathf.Max(0f, Mathf.Min(InitialPosition.y, (float)UI.screenHeight - val.y)));
			base.windowRect = new Rect(val2.x, val2.y, val.x, val.y);
		}

		public override void PreOpen()
		{
			((Window)this).PreOpen();
			NotifyHSVUpdated();
			_alphaPosition = curColour.a / UnitsPerPixel;
		}

		public static string RGBtoHex(Color col)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			int num = (int)Mathf.Clamp(col.r * 256f, 0f, 255f);
			int num2 = (int)Mathf.Clamp(col.g * 256f, 0f, 255f);
			int num3 = (int)Mathf.Clamp(col.b * 256f, 0f, 255f);
			int num4 = (int)Mathf.Clamp(col.a * 256f, 0f, 255f);
			return "#" + num.ToString("X2") + num2.ToString("X2") + num3.ToString("X2") + num4.ToString("X2");
		}

		public static bool TryGetColorFromHex(string hex, out Color col)
		{
			//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
			Color val = default(Color);
			((Color)(ref val))..ctor(0f, 0f, 0f);
			if (hex != null && hex.Length == 9)
			{
				try
				{
					string text = hex.Substring(1, hex.Length - 1);
					val.r = (float)int.Parse(text.Substring(0, 2), NumberStyles.AllowHexSpecifier) / 255f;
					val.g = (float)int.Parse(text.Substring(2, 2), NumberStyles.AllowHexSpecifier) / 255f;
					val.b = (float)int.Parse(text.Substring(4, 2), NumberStyles.AllowHexSpecifier) / 255f;
					if (text.Length == 8)
					{
						val.a = (float)int.Parse(text.Substring(6, 2), NumberStyles.AllowHexSpecifier) / 255f;
					}
					else
					{
						val.a = 1f;
					}
				}
				catch (Exception)
				{
					col = Color.white;
					return false;
				}
				col = val;
				return true;
			}
			col = Color.white;
			return false;
		}

		public override void DoWindowContents(Rect inRect)
		{
			//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
			//IL_01bf: Unknown result type (might be due to invalid IL or missing references)
			//IL_01cb: Unknown result type (might be due to invalid IL or missing references)
			//IL_01d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_01e3: Unknown result type (might be due to invalid IL or missing references)
			//IL_01ef: Unknown result type (might be due to invalid IL or missing references)
			//IL_01fb: Unknown result type (might be due to invalid IL or missing references)
			//IL_0207: Unknown result type (might be due to invalid IL or missing references)
			//IL_0213: Unknown result type (might be due to invalid IL or missing references)
			//IL_02f2: Unknown result type (might be due to invalid IL or missing references)
			//IL_02f7: Unknown result type (might be due to invalid IL or missing references)
			//IL_0304: Unknown result type (might be due to invalid IL or missing references)
			//IL_0311: Unknown result type (might be due to invalid IL or missing references)
			//IL_031d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0327: Unknown result type (might be due to invalid IL or missing references)
			//IL_0330: Unknown result type (might be due to invalid IL or missing references)
			//IL_0340: Unknown result type (might be due to invalid IL or missing references)
			//IL_0359: Unknown result type (might be due to invalid IL or missing references)
			//IL_03a4: Unknown result type (might be due to invalid IL or missing references)
			//IL_044f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0500: Unknown result type (might be due to invalid IL or missing references)
			//IL_03c3: Unknown result type (might be due to invalid IL or missing references)
			//IL_03c9: Invalid comparison between Unknown and I4
			//IL_037d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0390: Unknown result type (might be due to invalid IL or missing references)
			//IL_0395: Unknown result type (might be due to invalid IL or missing references)
			//IL_039a: Unknown result type (might be due to invalid IL or missing references)
			//IL_039d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0528: Unknown result type (might be due to invalid IL or missing references)
			//IL_046e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0474: Invalid comparison between Unknown and I4
			//IL_03d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_03fa: Unknown result type (might be due to invalid IL or missing references)
			//IL_0549: Unknown result type (might be due to invalid IL or missing references)
			//IL_0482: Unknown result type (might be due to invalid IL or missing references)
			//IL_04a5: Unknown result type (might be due to invalid IL or missing references)
			//IL_0433: Unknown result type (might be due to invalid IL or missing references)
			//IL_04de: Unknown result type (might be due to invalid IL or missing references)
			//IL_05b0: Unknown result type (might be due to invalid IL or missing references)
			//IL_05c2: Unknown result type (might be due to invalid IL or missing references)
			//IL_057f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0584: Unknown result type (might be due to invalid IL or missing references)
			//IL_05a5: Unknown result type (might be due to invalid IL or missing references)
			//IL_0596: Unknown result type (might be due to invalid IL or missing references)
			//IL_0598: Unknown result type (might be due to invalid IL or missing references)
			_ = first;
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(((Rect)(ref inRect)).xMin, ((Rect)(ref inRect)).yMin, (float)_pickerSize, (float)_pickerSize);
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(((Rect)(ref val)).xMax + _margin, ((Rect)(ref inRect)).yMin, (float)_sliderWidth, (float)_pickerSize);
			Rect val3 = default(Rect);
			((Rect)(ref val3))..ctor(((Rect)(ref val2)).xMax + _margin, ((Rect)(ref inRect)).yMin, (float)_sliderWidth, (float)_pickerSize);
			Rect val4 = default(Rect);
			((Rect)(ref val4))..ctor(((Rect)(ref val3)).xMax + _margin, ((Rect)(ref inRect)).yMin, (float)_previewSize, (float)_previewSize);
			Rect val5 = new Rect(((Rect)(ref val4)).xMax, ((Rect)(ref inRect)).yMin, (float)_previewSize, (float)_previewSize);
			Rect val6 = default(Rect);
			((Rect)(ref val6))..ctor(((Rect)(ref val3)).xMax + _margin, ((Rect)(ref inRect)).yMax - _fieldHeight, (float)(_previewSize * 2), _fieldHeight);
			Rect val7 = default(Rect);
			((Rect)(ref val7))..ctor(((Rect)(ref val3)).xMax + _margin, ((Rect)(ref inRect)).yMax - 2f * _fieldHeight - _margin, (float)_previewSize - _margin / 2f, _fieldHeight);
			Rect val8 = default(Rect);
			((Rect)(ref val8))..ctor(((Rect)(ref val7)).xMax + _margin, ((Rect)(ref val7)).yMin, (float)_previewSize - _margin / 2f, _fieldHeight);
			Rect val9 = default(Rect);
			((Rect)(ref val9))..ctor(((Rect)(ref val3)).xMax + _margin, ((Rect)(ref inRect)).yMax - 3f * _fieldHeight - 2f * _margin, (float)(_previewSize * 2), _fieldHeight);
			GUI.DrawTexture(val, (Texture)(object)PickerAlphaBG);
			GUI.DrawTexture(val3, (Texture)(object)SliderAlphaBG);
			GUI.DrawTexture(val4, (Texture)(object)PreviewAlphaBG);
			GUI.DrawTexture(val5, (Texture)(object)PreviewAlphaBG);
			GUI.DrawTexture(val, (Texture)(object)ColourPickerBG);
			GUI.DrawTexture(val2, (Texture)(object)HuePickerBG);
			GUI.DrawTexture(val3, (Texture)(object)AlphaPickerBG);
			GUI.DrawTexture(val4, (Texture)(object)TempPreviewBG);
			GUI.DrawTexture(val5, (Texture)(object)PreviewBG);
			Rect val10 = default(Rect);
			((Rect)(ref val10))..ctor(((Rect)(ref val2)).xMin - 3f, ((Rect)(ref val2)).yMin + _huePosition - (float)(_handleSize / 2), (float)_sliderWidth + 6f, (float)_handleSize);
			Rect val11 = default(Rect);
			((Rect)(ref val11))..ctor(((Rect)(ref val3)).xMin - 3f, ((Rect)(ref val3)).yMin + _alphaPosition - (float)(_handleSize / 2), (float)_sliderWidth + 6f, (float)_handleSize);
			Rect val12 = new Rect(((Rect)(ref val)).xMin + _position.x - (float)(_handleSize / 2), ((Rect)(ref val)).yMin + _position.y - (float)(_handleSize / 2), (float)_handleSize, (float)_handleSize);
			GUI.DrawTexture(val10, (Texture)(object)TempPreviewBG);
			GUI.DrawTexture(val11, (Texture)(object)TempPreviewBG);
			GUI.DrawTexture(val12, (Texture)(object)TempPreviewBG);
			GUI.color = Color.gray;
			Widgets.DrawBox(val10, 1, (Texture2D)null);
			Widgets.DrawBox(val11, 1, (Texture2D)null);
			Widgets.DrawBox(val12, 1, (Texture2D)null);
			GUI.color = Color.white;
			if (Input.GetMouseButtonUp(0))
			{
				_activeControl = Controls.none;
			}
			if (Mouse.IsOver(val))
			{
				if (Input.GetMouseButtonDown(0))
				{
					_activeControl = Controls.colourPicker;
				}
				if (_activeControl == Controls.colourPicker)
				{
					Vector2 pos = Event.current.mousePosition - new Vector2(((Rect)(ref val)).xMin, ((Rect)(ref val)).yMin);
					PickerAction(pos);
				}
			}
			if (Mouse.IsOver(val2))
			{
				if (Input.GetMouseButtonDown(0))
				{
					_activeControl = Controls.huePicker;
				}
				if ((int)Event.current.type == 6)
				{
					H -= Event.current.delta.y * UnitsPerPixel;
					_huePosition = Mathf.Clamp(_huePosition + Event.current.delta.y, 0f, (float)_pickerSize);
					Event.current.Use();
				}
				if (_activeControl == Controls.huePicker)
				{
					float pos2 = Event.current.mousePosition.y - ((Rect)(ref val2)).yMin;
					HueAction(pos2);
				}
			}
			if (Mouse.IsOver(val3))
			{
				if (Input.GetMouseButtonDown(0))
				{
					_activeControl = Controls.alphaPicker;
				}
				if ((int)Event.current.type == 6)
				{
					A -= Event.current.delta.y * UnitsPerPixel;
					_alphaPosition = Mathf.Clamp(_alphaPosition + Event.current.delta.y, 0f, (float)_pickerSize);
					Event.current.Use();
				}
				if (_activeControl == Controls.alphaPicker)
				{
					float pos3 = Event.current.mousePosition.y - ((Rect)(ref val3)).yMin;
					AlphaAction(pos3);
				}
			}
			Text.Font = (GameFont)1;
			if (Widgets.ButtonText(val6, "OK", true, false, true, (TextAnchor?)null))
			{
				SetColor();
				((Window)this).Close(true);
			}
			if (Widgets.ButtonText(val7, "Apply", true, false, true, (TextAnchor?)null))
			{
				SetColor();
			}
			if (Widgets.ButtonText(val8, "Cancel", true, false, true, (TextAnchor?)null))
			{
				((Window)this).Close(true);
			}
			if (_hexIn != _hexOut)
			{
				Color col = tempColour;
				if (TryGetColorFromHex(_hexIn, out col))
				{
					tempColour = col;
					NotifyRGBUpdated();
				}
				else
				{
					GUI.color = Color.red;
				}
			}
			_hexIn = Widgets.TextField(val9, _hexIn);
			GUI.color = Color.white;
		}
	}
	public static class OnDemandUtil
	{
		public static void FixOnDemandDefs(string prefix, ModContentPack mcp)
		{
			foreach (ThingDef allDef in DefDatabase<ThingDef>.AllDefs)
			{
				if (((Def)allDef).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef).fileName))
				{
					FixMissingMCPData((Def)(object)allDef, mcp);
				}
			}
			foreach (IncidentDef allDef2 in DefDatabase<IncidentDef>.AllDefs)
			{
				if (((Def)allDef2).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef2).fileName))
				{
					FixMissingMCPData((Def)(object)allDef2, mcp);
				}
			}
			foreach (QuestScriptDef allDef3 in DefDatabase<QuestScriptDef>.AllDefs)
			{
				if (((Def)allDef3).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef3).fileName))
				{
					FixMissingMCPData((Def)(object)allDef3, mcp);
				}
			}
			foreach (GameConditionDef allDef4 in DefDatabase<GameConditionDef>.AllDefs)
			{
				if (((Def)allDef4).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef4).fileName))
				{
					FixMissingMCPData((Def)(object)allDef4, mcp);
				}
			}
			foreach (WeatherDef allDef5 in DefDatabase<WeatherDef>.AllDefs)
			{
				if (((Def)allDef5).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef5).fileName))
				{
					FixMissingMCPData((Def)(object)allDef5, mcp);
				}
			}
			foreach (FactionDef allDef6 in DefDatabase<FactionDef>.AllDefs)
			{
				if (((Def)allDef6).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef6).fileName))
				{
					FixMissingMCPData((Def)(object)allDef6, mcp);
				}
			}
			foreach (PawnKindDef allDef7 in DefDatabase<PawnKindDef>.AllDefs)
			{
				if (((Def)allDef7).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef7).fileName))
				{
					FixMissingMCPData((Def)(object)allDef7, mcp);
				}
			}
			foreach (WorkGiverDef allDef8 in DefDatabase<WorkGiverDef>.AllDefs)
			{
				if (((Def)allDef8).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef8).fileName))
				{
					FixMissingMCPData((Def)(object)allDef8, mcp);
				}
			}
			foreach (TerrainDef allDef9 in DefDatabase<TerrainDef>.AllDefs)
			{
				if (((Def)allDef9).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef9).fileName))
				{
					FixMissingMCPData((Def)(object)allDef9, mcp);
				}
			}
			foreach (RecipeDef allDef10 in DefDatabase<RecipeDef>.AllDefs)
			{
				if (((Def)allDef10).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef10).fileName))
				{
					FixMissingMCPData((Def)(object)allDef10, mcp);
				}
			}
			foreach (ResearchProjectDef allDef11 in DefDatabase<ResearchProjectDef>.AllDefs)
			{
				if (((Def)allDef11).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef11).fileName))
				{
					FixMissingMCPData((Def)(object)allDef11, mcp);
				}
			}
			foreach (PreceptDef allDef12 in DefDatabase<PreceptDef>.AllDefs)
			{
				if (((Def)allDef12).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef12).fileName))
				{
					FixMissingMCPData((Def)(object)allDef12, mcp);
				}
			}
			foreach (GatheringDef allDef13 in DefDatabase<GatheringDef>.AllDefs)
			{
				if (((Def)allDef13).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef13).fileName))
				{
					FixMissingMCPData((Def)(object)allDef13, mcp);
				}
			}
			foreach (InteractionDef allDef14 in DefDatabase<InteractionDef>.AllDefs)
			{
				if (((Def)allDef14).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef14).fileName))
				{
					FixMissingMCPData((Def)(object)allDef14, mcp);
				}
			}
			foreach (JoyGiverDef allDef15 in DefDatabase<JoyGiverDef>.AllDefs)
			{
				if (((Def)allDef15).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef15).fileName))
				{
					FixMissingMCPData((Def)(object)allDef15, mcp);
				}
			}
			foreach (ThoughtDef allDef16 in DefDatabase<ThoughtDef>.AllDefs)
			{
				if (((Def)allDef16).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef16).fileName))
				{
					FixMissingMCPData((Def)(object)allDef16, mcp);
				}
			}
			foreach (TraitDef allDef17 in DefDatabase<TraitDef>.AllDefs)
			{
				if (((Def)allDef17).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef17).fileName))
				{
					FixMissingMCPData((Def)(object)allDef17, mcp);
				}
			}
			foreach (AbilityDef allDef18 in DefDatabase<AbilityDef>.AllDefs)
			{
				if (((Def)allDef18).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef18).fileName))
				{
					FixMissingMCPData((Def)(object)allDef18, mcp);
				}
			}
			foreach (HediffDef allDef19 in DefDatabase<HediffDef>.AllDefs)
			{
				if (((Def)allDef19).defName.StartsWith(prefix) && GenText.NullOrEmpty(((Def)allDef19).fileName))
				{
					FixMissingMCPData((Def)(object)allDef19, mcp);
				}
			}
		}

		public static void FixMissingMCPData(Def def, ModContentPack mcp)
		{
			if (mcp.AllDefs.Contains(def))
			{
				LogUtil.Warning(mcp.Name + " already contains def: " + def.defName);
				def.modContentPack = mcp;
				def.fileName = mcp.Name;
			}
			else
			{
				mcp.AddDef(def, mcp.Name);
			}
		}
	}
	public class PatchOperation_ReplaceThingCount : PatchOperationPathed
	{
		public string replacement;

		public override bool ApplyWorker(XmlDocument xml)
		{
			XmlNode[] array = xml.SelectNodes(base.xpath).Cast<XmlNode>().ToArray();
			foreach (XmlNode xmlNode in array)
			{
				XmlNode xmlNode2 = xmlNode.OwnerDocument.CreateElement(replacement);
				xmlNode2.InnerXml = xmlNode.InnerXml;
				xmlNode2.InnerText = xmlNode.InnerText;
				xmlNode.ParentNode.InsertBefore(xmlNode2, xmlNode);
				xmlNode.ParentNode.RemoveChild(xmlNode);
			}
			return true;
		}
	}
	public class RaceSpawningDef : Def
	{
		public List<ThingDef> races = new List<ThingDef>();

		[Obsolete]
		public List<FactionDef> factions = new List<FactionDef>();

		public List<PawnKindDef> pawnKinds = new List<PawnKindDef>();

		public float weight = 100f;
	}
	public static class BigBoxUtil
	{
		public static DefModExt_BigBox GetModExtensionBigBox(this Def def)
		{
			List<DefModExtension> modExtensions = def.modExtensions;
			if (modExtensions == null)
			{
				return null;
			}
			int i = 0;
			for (int count = modExtensions.Count; i < count; i++)
			{
				if (modExtensions[i] is DefModExt_BigBox result)
				{
					return result;
				}
			}
			return null;
		}
	}
	public class CompProperties_RecipesFromFacilities : CompProperties
	{
		public List<FacilityRecipeListing> facilityLinkRecipes = new List<FacilityRecipeListing>();
	}
	public class Comp_RecipesFromFacilities : CompAffectedByFacilities
	{
		public List<RecipeDef> originalRecipeDefs = new List<RecipeDef>();

		public CompProperties_RecipesFromFacilities Props => (CompProperties_RecipesFromFacilities)(object)((ThingComp)this).props;

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			((CompAffectedByFacilities)this).PostSpawnSetup(respawningAfterLoad);
			originalRecipeDefs = ((Thing)((ThingComp)this).parent).def.AllRecipes;
		}

		public static void UpdateRecipes(CompAffectedByFacilities facilityComp)
		{
			//IL_0074: Unknown result type (might be due to invalid IL or missing references)
			//IL_0085: Unknown result type (might be due to invalid IL or missing references)
			//IL_0088: Unknown result type (might be due to invalid IL or missing references)
			List<RecipeDef> list = new List<RecipeDef>();
			if (ThingCompUtility.TryGetComp<Comp_RecipesFromFacilities>((Thing)(object)((ThingComp)facilityComp).parent) == null)
			{
				return;
			}
			Comp_RecipesFromFacilities comp_RecipesFromFacilities = ThingCompUtility.TryGetComp<Comp_RecipesFromFacilities>((Thing)(object)((ThingComp)facilityComp).parent);
			QualityCategory val = default(QualityCategory);
			foreach (FacilityRecipeListing facilityLinkRecipe in comp_RecipesFromFacilities.Props.facilityLinkRecipes)
			{
				bool flag = false;
				foreach (Thing item in facilityComp.LinkedFacilitiesListForReading)
				{
					if (item.def != facilityLinkRecipe.facility)
					{
						continue;
					}
					if (ThingCompUtility.TryGetComp<CompQuality>(item) != null && (int)facilityLinkRecipe.minQuality != 0)
					{
						QualityUtility.TryGetQuality(item, ref val);
						if (val < facilityLinkRecipe.minQuality)
						{
							continue;
						}
					}
					flag = true;
				}
				if (!flag)
				{
					continue;
				}
				foreach (RecipeDef recipe in facilityLinkRecipe.recipes)
				{
					if (!list.Contains(recipe))
					{
						list.Add(recipe);
					}
				}
			}
			((Thing)((ThingComp)facilityComp).parent).def.AllRecipes.Clear();
			((Thing)((ThingComp)facilityComp).parent).def.AllRecipes.AddRange(comp_RecipesFromFacilities.originalRecipeDefs);
			foreach (RecipeDef item2 in list)
			{
				if (!((Thing)((ThingComp)facilityComp).parent).def.AllRecipes.Contains(item2))
				{
					((Thing)((ThingComp)facilityComp).parent).def.AllRecipes.Add(item2);
				}
			}
		}
	}
	public class DefModExt_BigBox : DefModExtension
	{
		public Vector2 size;

		public Vector3 offset;

		public bool directionBased;

		public Vector2 westSize;

		public Vector3 westOffset;

		public Vector2 northSize;

		public Vector3 northOffset;

		public Vector2 eastSize;

		public Vector3 eastOffset;

		public Vector2 southSize;

		public Vector3 southOffset;
	}
	public class FacilityRecipeListing
	{
		public ThingDef facility;

		public List<RecipeDef> recipes;

		public QualityCategory minQuality;
	}
	[HarmonyPatch(typeof(CompAffectedByFacilities), "Notify_LinkRemoved")]
	public static class Patch_CompAffectedByFacilities_Notify_LinkRemoved
	{
		[HarmonyPostfix]
		public static void Postfix(Thing thing, CompAffectedByFacilities __instance)
		{
			Comp_RecipesFromFacilities.UpdateRecipes(__instance);
		}
	}
	[HarmonyPatch(typeof(CompAffectedByFacilities), "Notify_NewLink")]
	public static class Patch_CompAffectedByFacilities_Notify_NewLink
	{
		[HarmonyPostfix]
		public static void Postfix(Thing facility, CompAffectedByFacilities __instance)
		{
			Comp_RecipesFromFacilities.UpdateRecipes(__instance);
		}
	}
	[HarmonyPatch(typeof(SelectionDrawer), "DrawSelectionBracketFor")]
	public static class Patch_SelectionDrawer_DrawSelectionBracketFor
	{
		[HarmonyPrefix]
		public static bool Prefix(object obj, Vector3[] ___bracketLocs, Material ___SelectionBracketMat, Dictionary<object, float> ___selectTimes)
		{
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Unknown result type (might be due to invalid IL or missing references)
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_0077: Unknown result type (might be due to invalid IL or missing references)
			//IL_007c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Unknown result type (might be due to invalid IL or missing references)
			//IL_0067: Unknown result type (might be due to invalid IL or missing references)
			//IL_006c: Unknown result type (might be due to invalid IL or missing references)
			//IL_006e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0073: Unknown result type (might be due to invalid IL or missing references)
			//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
			//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00df: Unknown result type (might be due to invalid IL or missing references)
			//IL_009f: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
			//IL_0088: Unknown result type (might be due to invalid IL or missing references)
			//IL_008a: Unknown result type (might be due to invalid IL or missing references)
			//IL_008f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0094: Unknown result type (might be due to invalid IL or missing references)
			//IL_0096: Unknown result type (might be due to invalid IL or missing references)
			//IL_009b: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
			//IL_00be: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
			//IL_0103: Unknown result type (might be due to invalid IL or missing references)
			//IL_0108: Unknown result type (might be due to invalid IL or missing references)
			//IL_0112: Unknown result type (might be due to invalid IL or missing references)
			//IL_0117: Unknown result type (might be due to invalid IL or missing references)
			ThingWithComps val = (ThingWithComps)((obj is ThingWithComps) ? obj : null);
			if (val != null)
			{
				DefModExt_BigBox defModExt_BigBox = ((Def)(object)((Thing)val).def)?.GetModExtensionBigBox();
				if (defModExt_BigBox != null)
				{
					Vector3 drawPos = ((Thing)val).DrawPos;
					Vector2 val2;
					if (!defModExt_BigBox.directionBased)
					{
						drawPos += defModExt_BigBox.offset;
						val2 = defModExt_BigBox.size;
					}
					else if (((Thing)val).Rotation == Rot4.East)
					{
						drawPos += defModExt_BigBox.eastOffset;
						val2 = defModExt_BigBox.eastSize;
					}
					else if (((Thing)val).Rotation == Rot4.North)
					{
						drawPos += defModExt_BigBox.northOffset;
						val2 = defModExt_BigBox.northSize;
					}
					else if (((Thing)val).Rotation == Rot4.West)
					{
						drawPos += defModExt_BigBox.westOffset;
						val2 = defModExt_BigBox.westSize;
					}
					else
					{
						drawPos += defModExt_BigBox.southOffset;
						val2 = defModExt_BigBox.southSize;
					}
					SelectionDrawerUtility.CalculateSelectionBracketPositionsWorld<object>(___bracketLocs, (object)val, drawPos, val2, ___selectTimes, Vector2.one, 1f, 1f);
					int num = 0;
					for (int i = 0; i < 4; i++)
					{
						Quaternion val3 = Quaternion.AngleAxis((float)num, Vector3.up);
						Graphics.DrawMesh(MeshPool.plane10, ___bracketLocs[i], val3, ___SelectionBracketMat, 0);
						num -= 90;
					}
					return false;
				}
			}
			return true;
		}
	}
	[HarmonyPatch(typeof(PawnGenerator), "FinalLevelOfSkill")]
	public static class Patch_PawnGenerator_FinalLevelOfSkill
	{
		[HarmonyPostfix]
		public static void Postfix(ref int __result, Pawn pawn, SkillDef sk)
		{
			DefModExt_PawnKindExtended modExtension = ((Def)pawn.kindDef).GetModExtension<DefModExt_PawnKindExtended>();
			if (modExtension == null || GenList.NullOrEmpty<SkillLevelSetting>((IList<SkillLevelSetting>)modExtension.skillSettings))
			{
				return;
			}
			if (!GenCollection.EnumerableNullOrEmpty<SkillLevelSetting>(modExtension.skillSettings.Where((SkillLevelSetting sr) => sr.skill == sk)))
			{
				__result = modExtension.skillSettings.Find((SkillLevelSetting sr) => sr.skill == sk).level;
			}
			else if (modExtension.flattenSkills)
			{
				__result = 0;
			}
		}
	}
	[HarmonyPatch(typeof(PawnGenerator), "GenerateInitialHediffs")]
	public static class Patch_PawnGen_GenerateInitialHediffs
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, PawnGenerationRequest request)
		{
			DefModExt_PawnKindExtended modExtension = ((Def)pawn.kindDef).GetModExtension<DefModExt_PawnKindExtended>();
			if (modExtension == null || pawn.Dead)
			{
				return;
			}
			if (!GenList.NullOrEmpty<AdditionalHediffEntry>((IList<AdditionalHediffEntry>)modExtension.additionalHediffs))
			{
				if (modExtension.randomAdditionalHediff)
				{
					AdditionalHediffEntry hediffEntry = GetHediffEntry(pawn.kindDef);
					if (hediffEntry != null)
					{
						GiveHediffEntry(hediffEntry, pawn);
					}
				}
				else
				{
					foreach (AdditionalHediffEntry additionalHediff in modExtension.additionalHediffs)
					{
						GiveHediffEntry(additionalHediff, pawn);
					}
				}
			}
			List<Hediff> hediffs = pawn.health.hediffSet.hediffs;
			if (modExtension.clearChronicIllness)
			{
				for (int i = 0; i < hediffs.Count(); i++)
				{
					if (hediffs[i].def.chronic)
					{
						pawn.health.RemoveHediff(hediffs[i]);
					}
				}
			}
			if (modExtension.clearAddictions)
			{
				for (int j = 0; j < hediffs.Count(); j++)
				{
					if (hediffs[j].def.IsAddiction)
					{
						pawn.health.RemoveHediff(hediffs[j]);
					}
				}
			}
			if (!modExtension.replaceMissingParts)
			{
				return;
			}
			for (int k = 0; k < hediffs.Count(); k++)
			{
				if (pawn.health.hediffSet.PartIsMissing(hediffs[k].part))
				{
					pawn.health.RestorePart(hediffs[k].part, (Hediff)null, true);
				}
			}
		}

		public static void GiveHediffEntry(AdditionalHediffEntry entry, Pawn pawn)
		{
			Hediff val = HediffMaker.MakeHediff(entry.hediff, pawn, (BodyPartRecord)null);
			val.Severity = ((FloatRange)(ref entry.severityRange)).RandomInRange;
			pawn.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}

		public static AdditionalHediffEntry GetHediffEntry(PawnKindDef pawnkind)
		{
			if (((Def)pawnkind).HasModExtension<DefModExt_PawnKindExtended>())
			{
				DefModExt_PawnKindExtended modExtension = ((Def)pawnkind).GetModExtension<DefModExt_PawnKindExtended>();
				if (!GenList.NullOrEmpty<AdditionalHediffEntry>((IList<AdditionalHediffEntry>)modExtension.additionalHediffs))
				{
					Func<AdditionalHediffEntry, float> func = (AdditionalHediffEntry x) => x.weight;
					return GenCollection.RandomElementByWeight<AdditionalHediffEntry>((IEnumerable<AdditionalHediffEntry>)modExtension.additionalHediffs, func);
				}
			}
			return null;
		}
	}
	[HarmonyPatch(typeof(PawnGenerator), "GeneratePawn", new Type[] { typeof(PawnGenerationRequest) })]
	public class Patch_PawnGenerator_GeneratePawn
	{
		[HarmonyPostfix]
		public static void Postfix(PawnGenerationRequest request, Pawn __result)
		{
			DefModExt_PawnKindExtended modExtension = ((Def)__result.kindDef).GetModExtension<DefModExt_PawnKindExtended>();
			if (modExtension != null && modExtension.clearApparel)
			{
				for (int i = 0; i < __result.apparel.WornApparel.Count(); i++)
				{
					__result.apparel.Remove(__result.apparel.WornApparel[i]);
				}
			}
		}
	}
	[HarmonyPatch(typeof(PawnGenerator), "GenerateSkills")]
	public static class Patch_PawnGen_GenerateSkills
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn pawn)
		{
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			DefModExt_PawnKindExtended modExtension = ((Def)pawn.kindDef).GetModExtension<DefModExt_PawnKindExtended>();
			if (modExtension != null && modExtension.clearPassions)
			{
				for (int i = 0; i < pawn.skills.skills.Count(); i++)
				{
					pawn.skills.skills[i].passion = (Passion)0;
				}
			}
		}
	}
	public class AdditionalHediffEntry
	{
		public HediffDef hediff;

		public FloatRange severityRange;

		public float weight;
	}
	public class CompProperties_AreaEffects : CompProperties
	{
		public bool roomBased = true;

		public bool roomRequiresRoof = true;

		public int radius;

		public List<HediffSeverityPairing> applyHediffs = new List<HediffSeverityPairing>();

		public int ticksBetweenRuns = 250;
	}
	public class CompProperties_Named : CompProperties
	{
		public RulePackDef nameMaker;

		public ThingNameFormat nameFormat = ThingNameFormat.Bracketed;

		public CompProperties_Named()
		{
			base.compClass = typeof(Comp_Named);
		}
	}
	public class CompProperties_VerbSwitch : CompProperties
	{
		public ResearchProjectDef requiredResearch;

		public List<VerbSwitchPair> requiredResearchSpecific = new List<VerbSwitchPair>();

		public bool useCooldown = true;

		public CompProperties_VerbSwitch()
		{
			base.compClass = typeof(Comp_VerbSwitch);
		}
	}
	public class DefModExt_PawnKindRaces : DefModExtension
	{
		public List<WeightedRaceChoice> altRaces = new List<WeightedRaceChoice>();
	}
	public class DefModExt_PawnKindExtended : DefModExtension
	{
		public bool flattenSkills;

		public bool clearPassions;

		public bool clearApparel;

		public List<SkillLevelSetting> skillSettings = new List<SkillLevelSetting>();

		public List<AdditionalHediffEntry> additionalHediffs = new List<AdditionalHediffEntry>();

		public bool randomAdditionalHediff;

		public bool clearChronicIllness;

		public bool clearAddictions;

		public bool replaceMissingParts;

		public List<GeneGroup> geneGroups = new List<GeneGroup>();

		public float geneGroupChance = 1f;
	}
	public class DefModExt_FactionExtension : DefModExtension
	{
		public int spreadsMoreSettlements;

		public RulePackDef nameMaker;

		public bool acceptsGifts = true;

		public IntRange? acceptsGiftRange;

		public List<FactionDef> hatedFactions = new List<FactionDef>();
	}
	public enum ThingNameFormat
	{
		Prefix,
		Suffix,
		Bracketed,
		Replace
	}
	public class SkillLevelSetting
	{
		public SkillDef skill;

		public int level;

		public bool setPassion;

		public Passion passionLevel;
	}
	public class PawnGroupMaker_AprilFools : PawnGroupMaker
	{
		public bool CanGenerate(PawnGroupMakerParms parms)
		{
			if (TabulaRasaMod.settings.specialOccasions && DateTime.Today.Month == 4 && DateTime.Today.Day == 1)
			{
				return true;
			}
			return false;
		}
	}
	public class PawnGroupMaker_PrideMonth : PawnGroupMaker
	{
		public bool CanGenerate(PawnGroupMakerParms parms)
		{
			if (TabulaRasaMod.settings.specialOccasions && DateTime.Now.Month == 6)
			{
				return true;
			}
			return false;
		}
	}
	public class ScenPart_ReinforcementJoins : ScenPart
	{
		private const float IntervalMidpoint = 30f;

		private const float IntervalDeviation = 15f;

		public float intervalDays;

		public bool repeat;

		public string intervalDaysBuffer;

		public float occurTick;

		public bool isFinished;

		public int maxPawns;

		public string maxPawnsBuffer;

		public PlayerPawnsArriveMethod arrivalMode = (PlayerPawnsArriveMethod)1;

		public PawnKindDef pawnKind;

		public FactionDef faction;

		public float IntervalTicks => 60000f * intervalDays;

		public bool MaxPawnsReached
		{
			get
			{
				if (maxPawns > 0)
				{
					return Find.World.PlayerPawnsForStoryteller.Count() >= maxPawns;
				}
				return false;
			}
		}

		public override void Tick()
		{
			((ScenPart)this).Tick();
			if (Find.AnyPlayerHomeMap == null || MaxPawnsReached || isFinished)
			{
				return;
			}
			if (pawnKind == null)
			{
				Log.Error("Trying to tick ScenPart_SpecificPawnKindJoins but the pawnKind is null");
				isFinished = true;
			}
			else if ((float)Find.TickManager.TicksGame >= occurTick && SendPawn())
			{
				if (repeat && intervalDays > 0f)
				{
					occurTick += IntervalTicks;
				}
				else
				{
					isFinished = true;
				}
			}
		}

		public bool SendPawn()
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_004a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_005a: Unknown result type (might be due to invalid IL or missing references)
			//IL_005f: Unknown result type (might be due to invalid IL or missing references)
			//IL_006a: Unknown result type (might be due to invalid IL or missing references)
			//IL_006f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0075: Unknown result type (might be due to invalid IL or missing references)
			//IL_0080: Unknown result type (might be due to invalid IL or missing references)
			//IL_0085: Unknown result type (might be due to invalid IL or missing references)
			//IL_008a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0095: Unknown result type (might be due to invalid IL or missing references)
			//IL_009a: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
			Map anyPlayerHomeMap = Find.AnyPlayerHomeMap;
			if ((int)arrivalMode == 0)
			{
				if (!CanSpawnJoiner(anyPlayerHomeMap))
				{
					return false;
				}
			}
			else if (!CanSpawnDropPod(anyPlayerHomeMap))
			{
				return false;
			}
			Pawn val = GeneratePawn();
			if ((int)arrivalMode == 0)
			{
				SpawnJoiner(anyPlayerHomeMap, val);
			}
			else
			{
				SpawnDropPodJoiner(anyPlayerHomeMap, val);
			}
			TaggedString val2 = GrammarResolverSimpleStringExtensions.Formatted(Translator.Translate("TabulaRasa_LetterLabel_PawnKindJoins"), NamedArgumentUtility.Named((object)val, "PAWN"));
			TaggedString label = ((TaggedString)(ref val2)).AdjustedFor(val, "PAWN", true);
			val2 = GrammarResolverSimpleStringExtensions.Formatted(Translator.Translate("TabulaRasa_LetterText_PawnKindJoins"), NamedArgumentUtility.Named((object)val, "PAWN"));
			TaggedString text = ((TaggedString)(ref val2)).AdjustedFor(val, "PAWN", true);
			PawnRelationUtility.TryAppendRelationsWithColonistsInfo(ref text, ref label, val);
			SendLetter(label, text, LetterDefOf.PositiveEvent, LookTargets.op_Implicit((Thing)(object)val));
			return true;
		}

		public void SendLetter(TaggedString label, TaggedString text, LetterDef letterDef, LookTargets lookTargets)
		{
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			if (((TaggedString)(ref label)).NullOrEmpty() || ((TaggedString)(ref text)).NullOrEmpty())
			{
				Log.Error("Sending standard incident letter with no label or text.");
			}
			ChoiceLetter val = LetterMaker.MakeLetter(label, text, letterDef, lookTargets, (Faction)null, (Quest)null, (List<ThingDef>)null);
			Find.LetterStack.ReceiveLetter((Letter)(object)val, (string)null, 0, true);
		}

		public void SpawnDropPodJoiner(Map map, Pawn pawn)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			DropPodUtility.MakeDropPodAt(DropCellFinder.TradeDropSpot(map), map, MakeDropPodInfo(pawn), (Faction)null);
		}

		public ActiveTransporterInfo MakeDropPodInfo(Pawn pawn)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Expected O, but got Unknown
			ActiveTransporterInfo val = new ActiveTransporterInfo();
			val.innerContainer.TryAdd((Thing)(object)pawn, true);
			return val;
		}

		public bool CanSpawnDropPod(Map map)
		{
			if (MaxPawnsReached)
			{
				return false;
			}
			if (faction != null)
			{
				Faction val = Find.FactionManager.FirstFactionOfDef(faction);
				if (val != null && !FactionUtility.AllyOrNeutralTo(val, Faction.OfPlayer))
				{
					return false;
				}
			}
			return true;
		}

		public bool CanSpawnJoiner(Map map)
		{
			if (!CanSpawnDropPod(map))
			{
				return false;
			}
			IntVec3 cell;
			return TryFindEntryCell(map, out cell);
		}

		public void SpawnJoiner(Map map, Pawn pawn)
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			TryFindEntryCell(map, out var cell);
			GenSpawn.Spawn((Thing)(object)pawn, cell, map, (WipeMode)0);
		}

		public bool TryFindEntryCell(Map map, out IntVec3 cell)
		{
			return CellFinder.TryFindRandomEdgeCellWith((Predicate<IntVec3>)((IntVec3 c) => map.reachability.CanReachColony(c) && !GridsUtility.Fogged(c, map)), map, CellFinder.EdgeRoadChance_Neutral, ref cell);
		}

		public Pawn GeneratePawn()
		{
			//IL_008c: Unknown result type (might be due to invalid IL or missing references)
			return PawnGenerator.GeneratePawn(new PawnGenerationRequest(pawnKind, Faction.OfPlayer, (PawnGenerationContext)2, (PlanetTile?)null, false, false, false, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
		}

		public override void PostGameStart()
		{
			((ScenPart)this).PostGameStart();
			occurTick = (float)Find.TickManager.TicksGame + IntervalTicks;
		}

		public override void Randomize()
		{
			//IL_007b: Unknown result type (might be due to invalid IL or missing references)
			((ScenPart)this).Randomize();
			intervalDays = 15f * Rand.Gaussian(0f, 1f) + 30f;
			if (intervalDays < 0f)
			{
				intervalDays = 0f;
			}
			maxPawns = Rand.Range(0, 14);
			repeat = Rand.Range(0, 100) < 50;
			pawnKind = PawnKindDefOf.Colonist;
			arrivalMode = (PlayerPawnsArriveMethod)(Rand.Value < 0.5f);
		}

		public override void DoEditInterface(Listing_ScenEdit listing)
		{
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00db: Unknown result type (might be due to invalid IL or missing references)
			//IL_0126: Unknown result type (might be due to invalid IL or missing references)
			//IL_0130: Unknown result type (might be due to invalid IL or missing references)
			//IL_017b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0185: Unknown result type (might be due to invalid IL or missing references)
			//IL_01c5: Unknown result type (might be due to invalid IL or missing references)
			//IL_01cb: Unknown result type (might be due to invalid IL or missing references)
			//IL_01f3: Unknown result type (might be due to invalid IL or missing references)
			//IL_01dc: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b1: Expected O, but got Unknown
			//IL_01ff: Unknown result type (might be due to invalid IL or missing references)
			//IL_0232: Unknown result type (might be due to invalid IL or missing references)
			//IL_0254: Unknown result type (might be due to invalid IL or missing references)
			//IL_025e: Expected O, but got Unknown
			//IL_026a: Unknown result type (might be due to invalid IL or missing references)
			//IL_028c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0296: Expected O, but got Unknown
			//IL_02de: Unknown result type (might be due to invalid IL or missing references)
			//IL_02e8: Expected O, but got Unknown
			float num = 5f;
			Rect scenPartRect = listing.GetScenPartRect((ScenPart)(object)this, ScenPart.RowHeight * num);
			if (Widgets.ButtonText(new Rect(((Rect)(ref scenPartRect)).x, ((Rect)(ref scenPartRect)).y, ((Rect)(ref scenPartRect)).width, ((Rect)(ref scenPartRect)).height / num), TaggedString.op_Implicit(((Def)pawnKind).LabelCap), true, true, true, (TextAnchor?)null))
			{
				List<FloatMenuOption> list = new List<FloatMenuOption>();
				list.AddRange(DefDatabase<PawnKindDef>.AllDefsListForReading.Where((PawnKindDef s) => s.RaceProps.Humanlike).Select((Func<PawnKindDef, FloatMenuOption>)((PawnKindDef pkd) => new FloatMenuOption($"{GenText.CapitalizeFirst(((Def)pkd).label)} | {((Def)pkd.race).LabelCap}", (Action)delegate
				{
					pawnKind = pkd;
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0))));
				Find.WindowStack.Add((Window)new FloatMenu(list));
			}
			Widgets.TextFieldNumericLabeled<float>(new Rect(((Rect)(ref scenPartRect)).x, ((Rect)(ref scenPartRect)).y + ScenPart.RowHeight, ((Rect)(ref scenPartRect)).width, ScenPart.RowHeight), TaggedString.op_Implicit(Translator.Translate("intervalDays")), ref intervalDays, ref intervalDaysBuffer, 0f, 1E+09f);
			Widgets.TextFieldNumericLabeled<int>(new Rect(((Rect)(ref scenPartRect)).x, ((Rect)(ref scenPartRect)).y + ScenPart.RowHeight * 2f, ((Rect)(ref scenPartRect)).width, ScenPart.RowHeight), TaggedString.op_Implicit(Translator.Translate("TabulaRasa.MaxPawns")), ref maxPawns, ref maxPawnsBuffer, 0f, 1E+09f);
			Widgets.CheckboxLabeled(new Rect(((Rect)(ref scenPartRect)).x, ((Rect)(ref scenPartRect)).y + ScenPart.RowHeight * 3f, ((Rect)(ref scenPartRect)).width, ScenPart.RowHeight), TaggedString.op_Implicit(Translator.Translate("repeat")), ref repeat, false, (Texture2D)null, (Texture2D)null, false, false);
			Rect val = new Rect(((Rect)(ref scenPartRect)).x, ((Rect)(ref scenPartRect)).y + ScenPart.RowHeight * 4f, ((Rect)(ref scenPartRect)).width, ScenPart.RowHeight);
			if ((int)arrivalMode == 0)
			{
				TaggedString.op_Implicit(GrammarResolverSimpleStringExtensions.Formatted("PlayerPawnsArriveMethod_Standing", Array.Empty<NamedArgument>()));
			}
			else
			{
				TaggedString.op_Implicit(GrammarResolverSimpleStringExtensions.Formatted("PlayerPawnsArriveMethod_DropPods", Array.Empty<NamedArgument>()));
			}
			if (!Widgets.ButtonText(val, PlayerPawnsArriveMethodExtension.ToStringHuman(arrivalMode), true, true, true, (TextAnchor?)null))
			{
				return;
			}
			List<FloatMenuOption> list2 = new List<FloatMenuOption>();
			list2.Add(new FloatMenuOption(TaggedString.op_Implicit(GrammarResolverSimpleStringExtensions.Formatted("PlayerPawnsArriveMethod_Standing", Array.Empty<NamedArgument>())), (Action)delegate
			{
				//IL_0002: Unknown result type (might be due to invalid IL or missing references)
				arrivalMode = (PlayerPawnsArriveMethod)0;
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
			list2.Add(new FloatMenuOption(TaggedString.op_Implicit(GrammarResolverSimpleStringExtensions.Formatted("PlayerPawnsArriveMethod_DropPods", Array.Empty<NamedArgument>())), (Action)delegate
			{
				//IL_0002: Unknown result type (might be due to invalid IL or missing references)
				arrivalMode = (PlayerPawnsArriveMethod)1;
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
			list2.AddRange(DefDatabase<PawnKindDef>.AllDefsListForReading.Where((PawnKindDef s) => s.RaceProps.Humanlike).Select((Func<PawnKindDef, FloatMenuOption>)((PawnKindDef pkd) => new FloatMenuOption($"{GenText.CapitalizeFirst(((Def)pkd).label)} | {((Def)pkd.race).LabelCap}", (Action)delegate
			{
				pawnKind = pkd;
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0))));
			Find.WindowStack.Add((Window)new FloatMenu(list2));
		}

		public override string Summary(Scenario scen)
		{
			//IL_005a: Unknown result type (might be due to invalid IL or missing references)
			string text = "\nA " + GenText.CapitalizeFirst(((Def)pawnKind).label) + " will join the colony ";
			text = ((!repeat) ? (text + "after ") : (text + "every "));
			text = text + intervalDays + " days.";
			text = (((int)arrivalMode != 0) ? (text + " They will arrive by drop pod.") : (text + " They will arrive at the edge of the colony map."));
			if (maxPawns > 0)
			{
				text = text + "\nThese pawns will stop arriving if the colony has " + maxPawns + " or more colonists already.";
			}
			if (faction != null)
			{
				text = text + "\nThese pawns will stop arriving if relations with " + faction.fixedName + " become hostile.";
			}
			return text;
		}

		public override void ExposeData()
		{
			//IL_008a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0090: Invalid comparison between Unknown and I4
			((ScenPart)this).ExposeData();
			Scribe_Values.Look<float>(ref intervalDays, "intervalDays", 0f, false);
			Scribe_Values.Look<bool>(ref repeat, "repeat", false, false);
			Scribe_Values.Look<float>(ref occurTick, "occurTick", 0f, false);
			Scribe_Values.Look<bool>(ref isFinished, "isFinished", false, false);
			Scribe_Values.Look<int>(ref maxPawns, "maxPawns", 0, false);
			Scribe_Values.Look<PlayerPawnsArriveMethod>(ref arrivalMode, "arrivalMode", (PlayerPawnsArriveMethod)0, false);
			Scribe_Defs.Look<PawnKindDef>(ref pawnKind, "pawnKind");
			if ((int)Scribe.mode == 4 && pawnKind == null)
			{
				pawnKind = PawnKindDefOf.Colonist;
				Log.Error("ScenPart has null pawnKind reference after loading. Changing to " + Gen.ToStringSafe<PawnKindDef>(pawnKind));
			}
			Scribe_Defs.Look<FactionDef>(ref faction, "faction");
		}
	}
	[StaticConstructorOnStartup]
	public static class FactionUtil
	{
		static FactionUtil()
		{
		}

		public static int FactionPoints()
		{
			return (int)Find.World.worldObjects.Settlements.Sum((Settlement s) => ((float?)((Def)((WorldObject)s).def).GetModExtension<DefModExt_FactionExtension>()?.spreadsMoreSettlements) ?? 0f);
		}
	}
	[HarmonyPatch(typeof(PawnGroupMaker), "CanGenerateFrom")]
	public class Patch_PawnGroupMaker_CanGenerateFrom
	{
		[HarmonyPostfix]
		public static void Postfix(PawnGroupMaker __instance, PawnGroupMakerParms parms, ref bool __result)
		{
			if (__instance is PawnGroupMaker_FactionPoints pawnGroupMaker_FactionPoints)
			{
				__result &= pawnGroupMaker_FactionPoints.CanGenerate(parms);
			}
			else if (__instance is PawnGroupMaker_Temperature pawnGroupMaker_Temperature)
			{
				__result &= pawnGroupMaker_Temperature.CanGenerate(parms);
			}
		}
	}
	[HarmonyPatch(typeof(Ideo), "SetIcon")]
	public static class Patch_Ideo_SetIcon
	{
		[HarmonyPostfix]
		public static void PostFix(Ideo __instance, IdeoIconDef iconDef, ColorDef colorDef, bool clearPrimaryFactionColor)
		{
			if (__instance.culture != null && ((Def)__instance.culture).HasModExtension<DefModExt_CultureExtended>())
			{
				DefModExt_CultureExtended modExtension = ((Def)__instance.culture).GetModExtension<DefModExt_CultureExtended>();
				if (modExtension.ideoIconDef != null)
				{
					__instance.iconDef = modExtension.ideoIconDef;
				}
				if (modExtension.ideoIconColor != null)
				{
					__instance.colorDef = modExtension.ideoIconColor;
				}
			}
		}
	}
	public class JobDriver_PlaySounds : JobDriver_WatchBuilding
	{
		public override void WatchTickAction(int delta)
		{
			//IL_004a: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			DefModExt_Sounds modExtension = ((Def)((JobDriver)this).job.def).GetModExtension<DefModExt_Sounds>();
			if (Gen.IsHashIntervalTick((Thing)(object)((JobDriver)this).pawn, 400 + Rand.Range(0, 100)) && !GenList.NullOrEmpty<SoundDef>((IList<SoundDef>)modExtension.soundDefs))
			{
				SoundStarter.PlayOneShot(GenCollection.RandomElement<SoundDef>((IEnumerable<SoundDef>)modExtension.soundDefs), SoundInfo.op_Implicit(new TargetInfo(((Thing)((JobDriver)this).pawn).Position, ((Thing)((JobDriver)this).pawn).Map, false)));
			}
			((JobDriver_WatchBuilding)this).WatchTickAction(delta);
		}
	}
	public class HediffSeverityPairing
	{
		public HediffDef hediff;

		public float severityInitial = 0.01f;

		public float severityIncrease = 0.01f;
	}
	public class DefModExt_AutomatedLinkables : DefModExtension
	{
		public List<string> linkableTags = new List<string>();
	}
	public class DefModExt_CultureExtended : DefModExtension
	{
		public IdeoIconDef ideoIconDef;

		public ColorDef ideoIconColor;
	}
	public class DefModExt_DoorAdv : DefModExtension
	{
		public GraphicData asyncDoorGraphic;

		public GraphicData doorOverlayGraphic;

		public bool isSingle;
	}
	public class DefModExt_Sounds : DefModExtension
	{
		public SoundDef soundDef;

		public List<SoundDef> soundDefs = new List<SoundDef>();
	}
	public class DefModExt_VerbSwitchIcon : DefModExtension
	{
		public string gizmoIcon;
	}
	public class PawnGroupMaker_FactionPoints : PawnGroupMaker
	{
		public int minPoints;

		public int maxPoints = int.MaxValue;

		public bool CanGenerate(PawnGroupMakerParms parms)
		{
			int num = FactionUtil.FactionPoints();
			if (num > minPoints)
			{
				return num < maxPoints;
			}
			return false;
		}
	}
	public class PawnGroupMaker_Temperature : PawnGroupMaker
	{
		public float minTemperature = -999f;

		public float maxTemperature = 999f;

		public bool CanGenerate(PawnGroupMakerParms parms)
		{
			if (Find.CurrentMap.mapTemperature.OutdoorTemp >= minTemperature && Find.CurrentMap.mapTemperature.OutdoorTemp <= maxTemperature)
			{
				return true;
			}
			return false;
		}
	}
	[StaticConstructorOnStartup]
	public static class TabulaRasaStartup
	{
		static TabulaRasaStartup()
		{
			TabulaRasaSettings settings = TabulaRasaMod.settings;
			EnableNeededSubCategories();
			FillLinkablesAutomatically();
			try
			{
				if (ModLister.RoyaltyInstalled)
				{
					FixRoyaltyHostility(settings);
				}
			}
			catch (Exception ex)
			{
				Log.Message(":: Tabula Rasa :: Empire Hostility Fix Failed: " + ex.Message);
			}
		}

		public static void EnableNeededSubCategories()
		{
			foreach (ThingDef item in DefDatabase<ThingDef>.AllDefsListForReading)
			{
				DefModExt_SubCategoryBuilding modExtension = ((Def)item).GetModExtension<DefModExt_SubCategoryBuilding>();
				if (modExtension != null)
				{
					if (modExtension.subCategory == null)
					{
						LogUtil.Error(((Def)item).defName + " has a misconfigured DefModExt_SubCategoryBuilding, subCategory MUST be assigned.");
					}
					else
					{
						modExtension.subCategory.enabled = true;
					}
				}
			}
		}

		public static void FixRoyaltyHostility(TabulaRasaSettings settings)
		{
			if (GenDictionary.NullOrEmpty<string, bool>(settings.empireHostilityFixedFactions))
			{
				settings.empireHostilityFixedFactions = new Dictionary<string, bool>();
			}
			foreach (FactionDef item in DefDatabase<FactionDef>.AllDefs.Where((FactionDef f) => f.isPlayer))
			{
				if (!settings.empireHostilityFixedFactions.ContainsKey(((Def)item).defName))
				{
					settings.empireHostilityFixedFactions.Add(((Def)item).defName, value: true);
				}
			}
			FactionDef namedSilentFail = DefDatabase<FactionDef>.GetNamedSilentFail("Empire");
			if (namedSilentFail == null || GenList.NullOrEmpty<FactionDef>((IList<FactionDef>)namedSilentFail.permanentEnemyToEveryoneExcept))
			{
				return;
			}
			foreach (FactionDef item2 in DefDatabase<FactionDef>.AllDefs.Where((FactionDef d) => d.isPlayer))
			{
				if (!namedSilentFail.permanentEnemyToEveryoneExcept.Contains(item2))
				{
					namedSilentFail.permanentEnemyToEveryoneExcept.Add(item2);
				}
			}
		}

		public static void CheckIfSettingsExistAndFix(RaceSpawningDef rsd)
		{
			if (GenDictionary.NullOrEmpty<string, bool>(TabulaRasaMod.settings.raceSpawningSettings))
			{
				TabulaRasaMod.settings.raceSpawningSettings = new Dictionary<string, bool>();
			}
			if (!TabulaRasaMod.settings.raceSpawningSettings.ContainsKey(((Def)rsd).defName))
			{
				TabulaRasaMod.settings.raceSpawningSettings.Add(((Def)rsd).defName, value: true);
			}
			if (GenDictionary.NullOrEmpty<string, float>(TabulaRasaMod.settings.raceSpawningWeights))
			{
				TabulaRasaMod.settings.raceSpawningWeights = new Dictionary<string, float>();
			}
			if (!TabulaRasaMod.settings.raceSpawningWeights.ContainsKey(((Def)rsd).defName))
			{
				TabulaRasaMod.settings.raceSpawningWeights.Add(((Def)rsd).defName, rsd.weight);
			}
		}

		public static bool DealWithRaceSpawningSettings(RaceSpawningDef rsd)
		{
			bool result = true;
			if (TabulaRasaMod.settings.raceSpawningSettings.ContainsKey(((Def)rsd).defName))
			{
				result = GenCollection.TryGetValue<string, bool>((IReadOnlyDictionary<string, bool>)TabulaRasaMod.settings.raceSpawningSettings, ((Def)rsd).defName, false);
			}
			if (TabulaRasaMod.settings.raceSpawningWeights.ContainsKey(((Def)rsd).defName))
			{
				rsd.weight = GenCollection.TryGetValue<string, float>((IReadOnlyDictionary<string, float>)TabulaRasaMod.settings.raceSpawningWeights, ((Def)rsd).defName, 0f);
			}
			return result;
		}

		public static void FillLinkablesAutomatically()
		{
			List<ThingDef> list = DefDatabase<ThingDef>.AllDefs.Where((ThingDef def) => def.HasComp(typeof(CompProperties_AffectedByFacilities)) && ((Def)def).HasModExtension<DefModExt_AutomatedLinkables>()).ToList();
			List<ThingDef> list2 = DefDatabase<ThingDef>.AllDefs.Where((ThingDef def) => def.HasComp(typeof(CompProperties_Facility)) && ((Def)def).HasModExtension<DefModExt_AutomatedLinkables>()).ToList();
			for (int i = 0; i < list.Count(); i++)
			{
				ThingDef val = list[i];
				DefModExt_AutomatedLinkables modExtension = ((Def)val).GetModExtension<DefModExt_AutomatedLinkables>();
				if (GenList.NullOrEmpty<string>((IList<string>)modExtension.linkableTags))
				{
					continue;
				}
				for (int j = 0; j < list2.Count(); j++)
				{
					ThingDef val2 = list2[j];
					DefModExt_AutomatedLinkables modExtension2 = ((Def)val2).GetModExtension<DefModExt_AutomatedLinkables>();
					if (!GenList.NullOrEmpty<string>((IList<string>)modExtension2.linkableTags) && !GenCollection.EnumerableNullOrEmpty<string>(modExtension2.linkableTags.Intersect(modExtension.linkableTags)) && !val.GetCompProperties<CompProperties_AffectedByFacilities>().linkableFacilities.Contains(val2))
					{
						val.GetCompProperties<CompProperties_AffectedByFacilities>().linkableFacilities.Add(val2);
					}
				}
			}
		}
	}
	public static class NeedsUtil
	{
		public static WorldComp_EnergyNeed GetEnergyNeedWorldComp
		{
			get
			{
				if (Find.World.GetComponent(typeof(WorldComp_EnergyNeed)) is WorldComp_EnergyNeed result)
				{
					return result;
				}
				LogUtil.Error("Could not find WorldComponent_EnergyNeed.");
				return null;
			}
		}

		public static bool InWirelessChargerRange(this Pawn pawn)
		{
			WorldComp_EnergyNeed getEnergyNeedWorldComp = GetEnergyNeedWorldComp;
			if (((Thing)pawn).Spawned && !GenList.NullOrEmpty<Building>((IList<Building>)getEnergyNeedWorldComp.wirelessChargers))
			{
				List<Building> list = getEnergyNeedWorldComp.wirelessChargers.Where((Building wc) => ((Thing)wc).Map != null && ((Thing)wc).Map == ((Thing)pawn).Map).ToList();
				if (!GenList.NullOrEmpty<Building>((IList<Building>)list) && GenCollection.Any<Building>(list, (Predicate<Building>)((Building wc) => IntVec3Utility.DistanceTo(((Thing)pawn).Position, ((Thing)wc).Position) <= ((BuildableDef)((Thing)wc).def).specialDisplayRadius)))
				{
					return true;
				}
			}
			return false;
		}

		public static List<Building> GetLocalChargingSockets(Pawn pawn)
		{
			WorldComp_EnergyNeed getEnergyNeedWorldComp = GetEnergyNeedWorldComp;
			if (((Thing)pawn).Spawned && !GenList.NullOrEmpty<Building>((IList<Building>)getEnergyNeedWorldComp.chargingSockets))
			{
				return getEnergyNeedWorldComp?.chargingSockets?.Where((Building wc) => ((Thing)wc).Map != null && ((Thing)wc).Map == ((Thing)pawn).Map)?.ToList() ?? new List<Building>();
			}
			return new List<Building>();
		}

		public static Building GetClosestPowerSocket(Pawn pawn)
		{
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0045: Unknown result type (might be due to invalid IL or missing references)
			//IL_0051: Unknown result type (might be due to invalid IL or missing references)
			//IL_005c: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
			//IL_0105: Unknown result type (might be due to invalid IL or missing references)
			//IL_0107: Unknown result type (might be due to invalid IL or missing references)
			Building val = null;
			List<Building> localChargingSockets = GetLocalChargingSockets(pawn);
			if (!GenList.NullOrEmpty<Building>((IList<Building>)localChargingSockets))
			{
				for (int i = 0; i < localChargingSockets.Count(); i++)
				{
					Building val2 = localChargingSockets[i];
					if ((val != null && !(IntVec3Utility.DistanceTo(((Thing)val).Position, ((Thing)pawn).Position) > IntVec3Utility.DistanceTo(((Thing)val2).Position, ((Thing)pawn).Position))) || !(val.PowerComp.PowerNet.CurrentStoredEnergy() > 50f))
					{
						continue;
					}
					foreach (IntVec3 item in from selector in GenAdj.CellsAdjacentCardinal((Thing)(object)val2)
						orderby IntVec3Utility.DistanceTo(selector, ((Thing)pawn).Position) descending
						select selector)
					{
						if (GenGrid.Walkable(item, ((Thing)pawn).Map) && ForbidUtility.InAllowedArea(item, pawn) && ReservationUtility.CanReserve(pawn, new LocalTargetInfo(item), 1, -1, (ReservationLayerDef)null, false) && ReachabilityUtility.CanReach(pawn, LocalTargetInfo.op_Implicit(item), (PathEndMode)1, (Danger)3, false, false, (TraverseMode)0))
						{
							val = val2;
							break;
						}
					}
				}
			}
			return val;
		}
	}
	public static class SettingsUtil
	{
		public static void CheckboxEnhanced(this Listing_Standard listing, string name, string explanation, ref bool value, string tooltip = null)
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0042: Unknown result type (might be due to invalid IL or missing references)
			//IL_005c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0085: Unknown result type (might be due to invalid IL or missing references)
			//IL_008a: Unknown result type (might be due to invalid IL or missing references)
			//IL_00af: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
			float curHeight = ((Listing)listing).CurHeight;
			Text.Font = (GameFont)1;
			GUI.color = Color.white;
			listing.CheckboxLabeled(name, ref value, (string)null, 0f, 1f);
			Text.Font = (GameFont)0;
			((Listing)listing).ColumnWidth = ((Listing)listing).ColumnWidth - 34f;
			GUI.color = Color.gray;
			listing.Label(explanation, -1f, (TipSignal?)null);
			((Listing)listing).ColumnWidth = ((Listing)listing).ColumnWidth + 34f;
			Text.Font = (GameFont)1;
			Rect rect = ((Listing)listing).GetRect(0f, 1f);
			((Rect)(ref rect)).height = ((Listing)listing).CurHeight - curHeight;
			((Rect)(ref rect)).y = ((Rect)(ref rect)).y - ((Rect)(ref rect)).height;
			if (Mouse.IsOver(rect))
			{
				Widgets.DrawHighlight(rect);
				if (!GenText.NullOrEmpty(tooltip))
				{
					TooltipHandler.TipRegion(rect, TipSignal.op_Implicit(tooltip));
				}
			}
			GUI.color = Color.white;
			((Listing)listing).Gap(6f);
		}

		public static void Note(this Listing_Standard listing, string name, GameFont font = 1)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			Text.Font = font;
			((Listing)listing).ColumnWidth = ((Listing)listing).ColumnWidth - 34f;
			GUI.color = Color.white;
			listing.Label(name, -1f, (TipSignal?)null);
			((Listing)listing).ColumnWidth = ((Listing)listing).ColumnWidth + 34f;
			Text.Font = (GameFont)1;
		}

		public static void TextContent(this Listing_Standard listing, string text, GameFont font = 1)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			Text.Font = font;
			GUI.color = Color.white;
			listing.Label(text, -1f, (TipSignal?)null);
			Text.Font = (GameFont)1;
		}

		public static void ValueLabeled<T>(this Listing_Standard listing, string name, string explanation, ref T value, string tooltip = null)
		{
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			//IL_007b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0058: Unknown result type (might be due to invalid IL or missing references)
			//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
			//IL_0117: Unknown result type (might be due to invalid IL or missing references)
			//IL_01e0: Unknown result type (might be due to invalid IL or missing references)
			//IL_0122: Unknown result type (might be due to invalid IL or missing references)
			//IL_0131: Unknown result type (might be due to invalid IL or missing references)
			//IL_0134: Unknown result type (might be due to invalid IL or missing references)
			//IL_0161: Unknown result type (might be due to invalid IL or missing references)
			float curHeight = ((Listing)listing).CurHeight;
			Rect rect = ((Listing)listing).GetRect(Text.LineHeight + ((Listing)listing).verticalSpacing, 1f);
			Text.Font = (GameFont)1;
			GUI.color = Color.white;
			TextAnchor anchor = Text.Anchor;
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(rect, name);
			Text.Anchor = (TextAnchor)5;
			if (typeof(T).IsEnum)
			{
				Widgets.Label(rect, value.ToString().Replace("_", " "));
			}
			else
			{
				Widgets.Label(rect, value.ToString());
			}
			Text.Anchor = anchor;
			Text.Font = (GameFont)0;
			((Listing)listing).ColumnWidth = ((Listing)listing).ColumnWidth - 34f;
			GUI.color = Color.gray;
			listing.Label(explanation, -1f, (TipSignal?)null);
			((Listing)listing).ColumnWidth = ((Listing)listing).ColumnWidth + 34f;
			Text.Font = (GameFont)1;
			rect = ((Listing)listing).GetRect(0f, 1f);
			((Rect)(ref rect)).height = ((Listing)listing).CurHeight - curHeight;
			((Rect)(ref rect)).y = ((Rect)(ref rect)).y - ((Rect)(ref rect)).height;
			if (Mouse.IsOver(rect))
			{
				Widgets.DrawHighlight(rect);
				if (!GenText.NullOrEmpty(tooltip))
				{
					TooltipHandler.TipRegion(rect, TipSignal.op_Implicit(tooltip));
				}
				if (Event.current.isMouse && Event.current.button == 0 && (int)Event.current.type == 0)
				{
					T[] array = Enum.GetValues(typeof(T)).Cast<T>().ToArray();
					for (int i = 0; i < array.Length; i++)
					{
						T val = array[(i + 1) % array.Length];
						if (array[i].ToString() == value.ToString())
						{
							value = val;
							break;
						}
					}
					Event.current.Use();
				}
			}
			GUI.color = Color.white;
			((Listing)listing).Gap(6f);
		}

		public static void SettingsDropdown(this Listing_Standard listing, string name, string explanation, ref TabulaRasaSettingsPage value, float width)
		{
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			//IL_005f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0143: Unknown result type (might be due to invalid IL or missing references)
			//IL_0161: Unknown result type (might be due to invalid IL or missing references)
			//IL_017c: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a5: Unknown result type (might be due to invalid IL or missing references)
			//IL_01aa: Unknown result type (might be due to invalid IL or missing references)
			//IL_01cf: Unknown result type (might be due to invalid IL or missing references)
			//IL_010f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0119: Expected O, but got Unknown
			//IL_0139: Unknown result type (might be due to invalid IL or missing references)
			//IL_0143: Expected O, but got Unknown
			float curHeight = ((Listing)listing).CurHeight;
			Rect rect = ((Listing)listing).GetRect(Text.LineHeight + ((Listing)listing).verticalSpacing, 1f);
			Text.Font = (GameFont)1;
			GUI.color = Color.white;
			TextAnchor anchor = Text.Anchor;
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(rect, name);
			Text.Anchor = (TextAnchor)5;
			if (Widgets.ButtonText(new Rect(width - 150f, 0f, 150f, 29f), value.ToString().Replace("_", " "), true, true, true, (TextAnchor?)null))
			{
				List<FloatMenuOption> list = new List<FloatMenuOption>();
				foreach (TabulaRasaSettingsPage enumValue in Enum.GetValues(typeof(TabulaRasaSettingsPage)).Cast<TabulaRasaSettingsPage>().ToList())
				{
					list.Add(new FloatMenuOption(enumValue.ToString().Replace("_", " "), (Action)delegate
					{
						TabulaRasaMod.mod.currentPage = enumValue;
					}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
				}
				Find.WindowStack.Add((Window)new FloatMenu(list));
			}
			Text.Anchor = anchor;
			Text.Font = (GameFont)0;
			((Listing)listing).ColumnWidth = ((Listing)listing).ColumnWidth - 34f;
			GUI.color = Color.gray;
			listing.Label(explanation, -1f, (TipSignal?)null);
			((Listing)listing).ColumnWidth = ((Listing)listing).ColumnWidth + 34f;
			Text.Font = (GameFont)1;
			rect = ((Listing)listing).GetRect(0f, 1f);
			((Rect)(ref rect)).height = ((Listing)listing).CurHeight - curHeight;
			((Rect)(ref rect)).y = ((Rect)(ref rect)).y - ((Rect)(ref rect)).height;
			GUI.color = Color.white;
			((Listing)listing).Gap(6f);
		}

		public static void LabelBacked(this Listing_Standard list, string inputText, Color color, GameFont font = 2, bool translate = false)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_004a: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_0056: Unknown result type (might be due to invalid IL or missing references)
			//IL_0097: Unknown result type (might be due to invalid IL or missing references)
			//IL_009d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
			Text.Font = font;
			string text = (translate ? TaggedString.op_Implicit(Translator.Translate(inputText)) : inputText);
			TextAnchor anchor = Text.Anchor;
			Text.Anchor = (TextAnchor)3;
			float num = Text.CalcHeight(text, ((Listing)list).ColumnWidth - 3f - 6f) + 6f;
			Rect val = GenUI.Rounded(((Listing)list).GetRect(num, 1f));
			Color color2 = color;
			color2.r *= 0.25f;
			color2.g *= 0.25f;
			color2.b *= 0.25f;
			color2.a *= 0.2f;
			GUI.color = color2;
			Rect val2 = GenUI.ContractedBy(val, 1f);
			((Rect)(ref val2)).yMax = ((Rect)(ref val2)).yMax - 2f;
			GUI.DrawTexture(val2, (Texture)(object)BaseContent.WhiteTex);
			GUI.color = color;
			((Rect)(ref val)).xMin = ((Rect)(ref val)).xMin + 6f;
			Widgets.Label(val, text);
			GUI.color = Color.white;
			Text.Anchor = anchor;
			Text.Font = (GameFont)1;
		}

		public static void LabelBackedHeader(this Listing_Standard list, string inputText, Color color, ref bool collapsed, GameFont font = 2, bool translate = false)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_004b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_0056: Unknown result type (might be due to invalid IL or missing references)
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			//IL_0098: Unknown result type (might be due to invalid IL or missing references)
			//IL_009e: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00be: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
			//IL_010f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0129: Unknown result type (might be due to invalid IL or missing references)
			//IL_0155: Unknown result type (might be due to invalid IL or missing references)
			//IL_018b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0196: Unknown result type (might be due to invalid IL or missing references)
			//IL_015d: Unknown result type (might be due to invalid IL or missing references)
			Text.Font = font;
			string text = (translate ? TaggedString.op_Implicit(Translator.Translate(inputText)) : inputText);
			TextAnchor anchor = Text.Anchor;
			Text.Anchor = (TextAnchor)3;
			float num = Text.CalcHeight(text, ((Listing)list).ColumnWidth - 3f - 6f) + 6f;
			Rect val = GenUI.Rounded(((Listing)list).GetRect(num, 1f));
			Color color2 = color;
			color2.r *= 0.25f;
			color2.g *= 0.25f;
			color2.b *= 0.25f;
			color2.a *= 0.2f;
			GUI.color = color2;
			Rect val2 = GenUI.ContractedBy(val, 1f);
			((Rect)(ref val2)).yMax = ((Rect)(ref val2)).yMax - 2f;
			GUI.DrawTexture(val2, (Texture)(object)BaseContent.WhiteTex);
			GUI.color = color;
			((Rect)(ref val)).xMin = ((Rect)(ref val)).xMin + 6f;
			GUI.DrawTexture(new Rect(((Rect)(ref val)).x, ((Rect)(ref val)).y + (((Rect)(ref val)).height - 18f) / 2f, 18f, 18f), (Texture)(object)(collapsed ? TexButton.Reveal : TexButton.Collapse));
			if (Widgets.ButtonInvisible(val, true))
			{
				collapsed = !collapsed;
				if (collapsed)
				{
					SoundStarter.PlayOneShotOnCamera(SoundDefOf.TabClose, (Map)null);
				}
				else
				{
					SoundStarter.PlayOneShotOnCamera(SoundDefOf.TabOpen, (Map)null);
				}
			}
			if (Mouse.IsOver(val))
			{
				Widgets.DrawHighlight(val);
			}
			Widgets.Label(new Rect(((Rect)(ref val)).x + 18f, ((Rect)(ref val)).y, ((Rect)(ref val)).width - 18f, ((Rect)(ref val)).height), text);
			GUI.color = Color.white;
			Text.Anchor = anchor;
			Text.Font = (GameFont)1;
		}

		public static void DoImage(this Listing_Standard listing, Texture2D image)
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			GUI.DrawTexture(GenUI.Rounded(((Listing)listing).GetRect((float)((Texture)image).height, 1f)), (Texture)(object)image);
			((Listing)listing).Gap(4f);
		}
	}
	public static class EnhancedListingStandard
	{
		public class LabeledRadioValue<T>
		{
			private T val;

			private string label;

			public T Value
			{
				get
				{
					return val;
				}
				set
				{
					val = value;
				}
			}

			public string Label
			{
				get
				{
					return label;
				}
				set
				{
					label = value;
				}
			}

			public LabeledRadioValue(string label, T val)
			{
				Label = label;
				Value = val;
			}
		}

		private static float gap = 12f;

		private static float lineGap = 3f;

		public static float Gap
		{
			get
			{
				return gap;
			}
			set
			{
				gap = value;
			}
		}

		public static float LineGap
		{
			get
			{
				return lineGap;
			}
			set
			{
				lineGap = value;
			}
		}

		public static Listing_Standard BeginListingStandard(this Rect rect, int columns = 1)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0026: Expected O, but got Unknown
			Listing_Standard val = new Listing_Standard
			{
				ColumnWidth = ((Rect)(ref rect)).width / (float)columns - (float)columns * 5f
			};
			((Listing)val).Begin(rect);
			return val;
		}

		public static void AddHorizontalLine(this Listing_Standard listing_Standard, float? gap = null)
		{
			((Listing)listing_Standard).Gap(gap ?? lineGap);
			((Listing)listing_Standard).GapLine(gap ?? lineGap);
		}

		public static void AddLabelLine(this Listing_Standard listing_Standard, string label, float? height = null)
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			((Listing)listing_Standard).Gap(Gap);
			Widgets.Label(listing_Standard.GetRect(height), label);
		}

		public static Rect GetRect(this Listing_Standard listing_Standard, float? height = null)
		{
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			return ((Listing)listing_Standard).GetRect(height ?? Text.LineHeight, 1f);
		}

		public static Rect LineRectSpilter(this Listing_Standard listing_Standard, out Rect leftHalf, float leftPartPct = 0.5f, float? height = null)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_0009: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			Rect rect = listing_Standard.GetRect(height);
			leftHalf = GenUI.Rounded(GenUI.LeftPart(rect, leftPartPct));
			return rect;
		}

		public static Rect LineRectSpilter(this Listing_Standard listing_Standard, out Rect leftHalf, out Rect rightHalf, float leftPartPct = 0.5f, float? height = null)
		{
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_000a: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			Rect val = listing_Standard.LineRectSpilter(out leftHalf, leftPartPct, height);
			rightHalf = GenUI.Rounded(GenUI.RightPart(val, 1f - leftPartPct));
			return val;
		}

		public static Rect LineRectSpilter(this Listing_Standard listing_Standard, out Rect leftRect, out Rect midRect, out Rect rightRect)
		{
			//IL_000a: Unknown result type (might be due to invalid IL or missing references)
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0064: Unknown result type (might be due to invalid IL or missing references)
			//IL_0069: Unknown result type (might be due to invalid IL or missing references)
			//IL_0087: Unknown result type (might be due to invalid IL or missing references)
			//IL_008c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0091: Unknown result type (might be due to invalid IL or missing references)
			Rect rect = listing_Standard.GetRect(null);
			float num = ((Rect)(ref rect)).width * 0.33f;
			leftRect = new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, num, ((Rect)(ref rect)).height);
			midRect = new Rect(((Rect)(ref rect)).x + num + 4f, ((Rect)(ref rect)).y, num - 4f, ((Rect)(ref rect)).height);
			rightRect = new Rect(((Rect)(ref rect)).width - num, ((Rect)(ref rect)).y, num, ((Rect)(ref rect)).height);
			return rect;
		}

		public static void AddLabeledRadioList(this Listing_Standard listing_Standard, string header, string[] labels, ref string val, float? headerHeight = null)
		{
			((Listing)listing_Standard).Gap(Gap);
			listing_Standard.AddLabelLine(header, headerHeight);
			listing_Standard.AddRadioList(GenerateLabeledRadioValues(labels), ref val, null);
		}

		public static void AddLabeledRadioList<T>(this Listing_Standard listing_Standard, string header, Dictionary<string, T> dict, ref T val, float? headerHeight = null)
		{
			((Listing)listing_Standard).Gap(Gap);
			listing_Standard.AddLabelLine(header, headerHeight);
			listing_Standard.AddRadioList(GenerateLabeledRadioValues(dict), ref val, null);
		}

		private static void AddRadioList<T>(this Listing_Standard listing_Standard, List<LabeledRadioValue<T>> items, ref T val, float? height = null)
		{
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			foreach (LabeledRadioValue<T> item in items)
			{
				((Listing)listing_Standard).Gap(Gap);
				if (Widgets.RadioButtonLabeled(listing_Standard.GetRect(height), item.Label, EqualityComparer<T>.Default.Equals(item.Value, val), false))
				{
					val = item.Value;
				}
			}
		}

		private static List<LabeledRadioValue<string>> GenerateLabeledRadioValues(string[] labels)
		{
			List<LabeledRadioValue<string>> list = new List<LabeledRadioValue<string>>();
			foreach (string text in labels)
			{
				list.Add(new LabeledRadioValue<string>(text, text));
			}
			return list;
		}

		private static List<LabeledRadioValue<T>> GenerateLabeledRadioValues<T>(Dictionary<string, T> dict)
		{
			List<LabeledRadioValue<T>> list = new List<LabeledRadioValue<T>>();
			foreach (KeyValuePair<string, T> item in dict)
			{
				list.Add(new LabeledRadioValue<T>(item.Key, item.Value));
			}
			return list;
		}

		public static void AddLabeledTextField(this Listing_Standard listing_Standard, string label, ref string settingsValue, float leftPartPct = 0.5f)
		{
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Unknown result type (might be due to invalid IL or missing references)
			((Listing)listing_Standard).Gap(Gap);
			listing_Standard.LineRectSpilter(out var leftHalf, out var rightHalf, leftPartPct, null);
			Widgets.Label(leftHalf, label);
			string text = settingsValue.ToString();
			settingsValue = Widgets.TextField(rightHalf, text);
		}

		public static void AddLabeledNumericalTextField<T>(this Listing_Standard listing_Standard, string label, ref T settingsValue, float leftPartPct = 0.5f, float minValue = 1f, float maxValue = 100000f) where T : struct
		{
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			((Listing)listing_Standard).Gap(Gap);
			listing_Standard.LineRectSpilter(out var leftHalf, out var rightHalf, leftPartPct, null);
			Widgets.Label(leftHalf, label);
			string text = settingsValue.ToString();
			Widgets.TextFieldNumeric<T>(rightHalf, ref settingsValue, ref text, minValue, maxValue);
		}

		public static void AddVector2TextFields<T>(this Listing_Standard listing, string label, ref T valueX, ref T valueY, float minValue = -1f, float maxValue = 1f) where T : struct
		{
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0058: Unknown result type (might be due to invalid IL or missing references)
			listing.Label(label, -1f, (TipSignal?)null);
			listing.LineRectSpilter(out var leftHalf, out var rightHalf, 0.5f, null);
			string text = valueX.ToString();
			Widgets.TextFieldNumeric<T>(leftHalf, ref valueX, ref text, minValue, maxValue);
			string text2 = valueY.ToString();
			Widgets.TextFieldNumeric<T>(rightHalf, ref valueY, ref text2, minValue, maxValue);
		}

		public static void AddVector3TextFields<T>(this Listing_Standard listing, string label, ref T valueX, ref T valueY, ref T valueZ, float minValue = -1f, float maxValue = 1f) where T : struct
		{
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0031: Unknown result type (might be due to invalid IL or missing references)
			//IL_004c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0068: Unknown result type (might be due to invalid IL or missing references)
			listing.Label(label, -1f, (TipSignal?)null);
			listing.LineRectSpilter(out var leftRect, out var midRect, out var rightRect);
			string text = valueX.ToString();
			Widgets.TextFieldNumeric<T>(leftRect, ref valueX, ref text, minValue, maxValue);
			string text2 = valueY.ToString();
			Widgets.TextFieldNumeric<T>(midRect, ref valueY, ref text2, minValue, maxValue);
			string text3 = valueZ.ToString();
			Widgets.TextFieldNumeric<T>(rightRect, ref valueZ, ref text3, minValue, maxValue);
		}

		public static void AddLabeledCheckbox(this Listing_Standard listing_Standard, string label, ref bool settingsValue)
		{
			((Listing)listing_Standard).Gap(Gap);
			listing_Standard.CheckboxLabeled(label, ref settingsValue, (string)null, 0f, 1f);
		}

		public static void AddLabeledSlider(this Listing_Standard listing_Standard, string label, ref float value, float leftValue, float rightValue, string leftAlignedLabel = null, string rightAlignedLabel = null, float roundTo = -1f, bool middleAlignment = false)
		{
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0024: Unknown result type (might be due to invalid IL or missing references)
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Unknown result type (might be due to invalid IL or missing references)
			((Listing)listing_Standard).Gap(Gap);
			listing_Standard.LineRectSpilter(out var leftHalf, out var rightHalf, 0.5f, null);
			Widgets.Label(leftHalf, label);
			float num = value;
			value = Widgets.HorizontalSlider(GenUI.BottomPart(rightHalf, 0.7f), num, leftValue, rightValue, middleAlignment, (string)null, leftAlignedLabel, rightAlignedLabel, roundTo);
		}

		public static void AddColorPickerButton(this Listing_Standard listing_Standard, string label, Color color, Action<Color> callback, string buttonText = "Change")
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			//IL_008d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0093: Unknown result type (might be due to invalid IL or missing references)
			//IL_009b: Unknown result type (might be due to invalid IL or missing references)
			//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00be: Unknown result type (might be due to invalid IL or missing references)
			//IL_0077: Unknown result type (might be due to invalid IL or missing references)
			((Listing)listing_Standard).Gap(Gap);
			Rect rect = listing_Standard.GetRect(null);
			float num = Text.CalcSize(buttonText).x + 10f;
			float num2 = num + 5f + ((Rect)(ref rect)).height;
			Rect val = GenUI.RightPartPixels(rect, num + 5f + ((Rect)(ref rect)).height);
			if (Widgets.ButtonText(GenUI.LeftPartPixels(val, num), buttonText, true, false, true, (TextAnchor?)null))
			{
				Find.WindowStack.Add((Window)(object)new Dialog_ColourPicker(color, callback, null));
			}
			GUI.color = color;
			GUI.DrawTexture(GenUI.RightPartPixels(val, ((Rect)(ref val)).height), (Texture)(object)BaseContent.WhiteTex);
			GUI.color = Color.white;
			Widgets.Label(GenUI.LeftPartPixels(rect, ((Rect)(ref rect)).width - num2), label);
		}

		public static void AddHoloColorPickerButton(this Listing_Standard listing_Standard, string label, Color color, Comp_HologramProjection comp, int layer, string buttonText = "Change")
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			//IL_0090: Unknown result type (might be due to invalid IL or missing references)
			//IL_0096: Unknown result type (might be due to invalid IL or missing references)
			//IL_009e: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
			//IL_0077: Unknown result type (might be due to invalid IL or missing references)
			((Listing)listing_Standard).Gap(Gap);
			Rect rect = listing_Standard.GetRect(null);
			float num = Text.CalcSize(buttonText).x + 10f;
			float num2 = num + 5f + ((Rect)(ref rect)).height;
			Rect val = GenUI.RightPartPixels(rect, num + 5f + ((Rect)(ref rect)).height);
			if (Widgets.ButtonText(GenUI.LeftPartPixels(val, num), buttonText, true, false, true, (TextAnchor?)null))
			{
				Find.WindowStack.Add((Window)(object)new Win_HologramColorPicker(color, comp, layer, null, null));
			}
			GUI.color = color;
			GUI.DrawTexture(GenUI.RightPartPixels(val, ((Rect)(ref val)).height), (Texture)(object)BaseContent.WhiteTex);
			GUI.color = Color.white;
			Widgets.Label(GenUI.LeftPartPixels(rect, ((Rect)(ref rect)).width - num2), label);
		}

		public static void AddColorPickerButton(this Listing_Standard listing_Standard, string label, Color color, string fieldName, object colorContainer, string buttonText = "Change")
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			listing_Standard.AddColorPickerButton(label, color, delegate
			{
				//IL_001d: Unknown result type (might be due to invalid IL or missing references)
				colorContainer.GetType().GetField(fieldName).SetValue(colorContainer, color);
			}, buttonText);
		}

		public static float Slider(this Listing_Standard listing_Standard, float val, float min, float max, string label = null, string leftAlignedLabel = null, string rightAlignedLabel = null, float roundTo = -1f, bool middleAlignment = false)
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			float result = Widgets.HorizontalSlider(((Listing)listing_Standard).GetRect(22f, 1f), val, min, max, middleAlignment, label, leftAlignedLabel, rightAlignedLabel, roundTo);
			((Listing)listing_Standard).Gap(((Listing)listing_Standard).verticalSpacing);
			return result;
		}

		public static void AddLabeledSlider<T>(this Listing_Standard listing_Standard, string label, ref T value) where T : Enum
		{
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			object value2 = value;
			((Listing)listing_Standard).Gap(10f);
			listing_Standard.LineRectSpilter(out var leftHalf, out var rightHalf, 0.5f, null);
			Widgets.Label(leftHalf, label);
			float num = Convert.ToInt32(value2);
			float num2 = Widgets.HorizontalSlider(GenUI.BottomPart(rightHalf, 0.7f), num, 0f, (float)(Enum.GetValues(typeof(T)).Length - 1), true, Enum.GetName(typeof(T), value), (string)null, (string)null, 1f);
			value = (T)Enum.ToObject(typeof(T), (int)num2);
		}
	}
	public class ColourWrapper
	{
		public Color Color { get; set; }

		public ColourWrapper(Color color)
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			Color = color;
		}
	}
	public class Dialog_ColourPicker : Window
	{
		private enum Controls
		{
			colourPicker,
			huePicker,
			alphaPicker,
			none
		}

		private Controls _activeControl = Controls.none;

		private Texture2D _colourPickerBG;

		private Texture2D _huePickerBG;

		private Texture2D _alphaPickerBG;

		private Texture2D _tempPreviewBG;

		private Texture2D _previewBG;

		private Texture2D _pickerAlphaBG;

		private Texture2D _sliderAlphaBG;

		private Texture2D _previewAlphaBG;

		private Color _alphaBGColorA = Color.white;

		private Color _alphaBGColorB = new Color(0.85f, 0.85f, 0.85f);

		private int _pickerSize = 300;

		private int _sliderWidth = 15;

		private int _alphaBGBlockSize = 10;

		private int _previewSize = 90;

		private int _handleSize = 10;

		private float _margin = 6f;

		private float _fieldHeight = 30f;

		private float _huePosition;

		private float _alphaPosition;

		private float _unitsPerPixel;

		private float _H;

		private float _S = 1f;

		private float _V = 1f;

		private float _A = 1f;

		private Vector2 _position = Vector2.zero;

		private string _hexOut;

		private string _hexIn;

		private Action<Color> _callback;

		public Color curColour = Color.blue;

		public Color tempColour = Color.white;

		private Vector2? _initialPosition;

		public static bool first;

		public override Vector2 InitialSize => new Vector2((float)_pickerSize + 3f * _margin + (float)(2 * _sliderWidth) + (float)(2 * _previewSize) + 36f, (float)_pickerSize + 36f);

		public Vector2 InitialPosition => (Vector2)(((??)_initialPosition) ?? (new Vector2((float)UI.screenWidth - ((Window)this).InitialSize.x, (float)UI.screenHeight - ((Window)this).InitialSize.y) / 2f));

		public float UnitsPerPixel
		{
			get
			{
				if (_unitsPerPixel == 0f)
				{
					_unitsPerPixel = 1f / (float)_pickerSize;
				}
				return _unitsPerPixel;
			}
		}

		public float H
		{
			get
			{
				return _H;
			}
			set
			{
				_H = Mathf.Clamp(value, 0f, 1f);
				NotifyHSVUpdated();
				CreateColourPickerBG();
				CreateAlphaPickerBG();
			}
		}

		public float S
		{
			get
			{
				return _S;
			}
			set
			{
				_S = Mathf.Clamp(value, 0f, 1f);
				NotifyHSVUpdated();
				CreateAlphaPickerBG();
			}
		}

		public float V
		{
			get
			{
				return _V;
			}
			set
			{
				_V = Mathf.Clamp(value, 0f, 1f);
				NotifyHSVUpdated();
				CreateAlphaPickerBG();
			}
		}

		public float A
		{
			get
			{
				return _A;
			}
			set
			{
				_A = Mathf.Clamp(value, 0f, 1f);
				NotifyHSVUpdated();
				CreateColourPickerBG();
			}
		}

		public Texture2D ColourPickerBG
		{
			get
			{
				if ((Object)(object)_colourPickerBG == (Object)null)
				{
					CreateColourPickerBG();
				}
				return _colourPickerBG;
			}
		}

		public Texture2D HuePickerBG
		{
			get
			{
				if ((Object)(object)_huePickerBG == (Object)null)
				{
					CreateHuePickerBG();
				}
				return _huePickerBG;
			}
		}

		public Texture2D AlphaPickerBG
		{
			get
			{
				if ((Object)(object)_alphaPickerBG == (Object)null)
				{
					CreateAlphaPickerBG();
				}
				return _alphaPickerBG;
			}
		}

		public Texture2D TempPreviewBG
		{
			get
			{
				//IL_0016: Unknown result type (might be due to invalid IL or missing references)
				if ((Object)(object)_tempPreviewBG == (Object)null)
				{
					CreatePreviewBG(ref _tempPreviewBG, tempColour);
				}
				return _tempPreviewBG;
			}
		}

		public Texture2D PreviewBG
		{
			get
			{
				//IL_0016: Unknown result type (might be due to invalid IL or missing references)
				if ((Object)(object)_previewBG == (Object)null)
				{
					CreatePreviewBG(ref _previewBG, curColour);
				}
				return _previewBG;
			}
		}

		public Texture2D PickerAlphaBG
		{
			get
			{
				if ((Object)(object)_pickerAlphaBG == (Object)null)
				{
					CreateAlphaBG(ref _pickerAlphaBG, _pickerSize, _pickerSize);
				}
				return _pickerAlphaBG;
			}
		}

		public Texture2D SliderAlphaBG
		{
			get
			{
				if ((Object)(object)_sliderAlphaBG == (Object)null)
				{
					CreateAlphaBG(ref _sliderAlphaBG, _sliderWidth, _pickerSize);
				}
				return _sliderAlphaBG;
			}
		}

		public Texture2D PreviewAlphaBG
		{
			get
			{
				if ((Object)(object)_previewAlphaBG == (Object)null)
				{
					CreateAlphaBG(ref _previewAlphaBG, _previewSize, _previewSize);
				}
				return _previewAlphaBG;
			}
		}

		public Dialog_ColourPicker(Color color, Action<Color> callback = null, Vector2? position = null)
			: base((IWindowDrawing)null)
		{
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			//IL_008f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0094: Unknown result type (might be due to invalid IL or missing references)
			//IL_009a: Unknown result type (might be due to invalid IL or missing references)
			//IL_009f: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
			//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
			_callback = callback;
			_initialPosition = position;
			curColour = color;
			NotifyRGBUpdated();
		}

		public void NotifyHSVUpdated()
		{
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			tempColour = HSV.ToRGBA(H, S, V);
			tempColour.a = A;
			CreatePreviewBG(ref _tempPreviewBG, tempColour);
			_hexOut = (_hexIn = RGBtoHex(tempColour));
		}

		public void NotifyRGBUpdated()
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
			HSV.ToHSV(tempColour, out _H, out _S, out _V);
			_A = tempColour.a;
			CreateColourPickerBG();
			CreateHuePickerBG();
			CreateAlphaPickerBG();
			_huePosition = (1f - _H) / UnitsPerPixel;
			_position.x = _S / UnitsPerPixel;
			_position.y = (1f - _V) / UnitsPerPixel;
			_alphaPosition = (1f - _A) / UnitsPerPixel;
			CreatePreviewBG(ref _tempPreviewBG, tempColour);
			_hexOut = (_hexIn = RGBtoHex(tempColour));
		}

		public void SetColor()
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			curColour = tempColour;
			_callback?.Invoke(curColour);
			CreatePreviewBG(ref _previewBG, tempColour);
		}

		private void SwapTexture(ref Texture2D tex, Texture2D newTex)
		{
			Object.Destroy((Object)(object)tex);
			tex = newTex;
		}

		private void CreateColourPickerBG()
		{
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Expected O, but got Unknown
			//IL_0053: Unknown result type (might be due to invalid IL or missing references)
			int pickerSize = _pickerSize;
			int pickerSize2 = _pickerSize;
			float unitsPerPixel = UnitsPerPixel;
			float unitsPerPixel2 = UnitsPerPixel;
			Texture2D val = new Texture2D(pickerSize, pickerSize2);
			for (int i = 0; i < pickerSize; i++)
			{
				for (int j = 0; j < pickerSize2; j++)
				{
					float s = (float)i * unitsPerPixel;
					float v = (float)j * unitsPerPixel2;
					val.SetPixel(i, j, HSV.ToRGBA(H, s, v, A));
				}
			}
			val.Apply();
			SwapTexture(ref _colourPickerBG, val);
		}

		private void CreateHuePickerBG()
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000d: Expected O, but got Unknown
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			Texture2D val = new Texture2D(1, _pickerSize);
			int pickerSize = _pickerSize;
			float num = 1f / (float)pickerSize;
			for (int i = 0; i < pickerSize; i++)
			{
				val.SetPixel(0, i, HSV.ToRGBA(num * (float)i, 1f, 1f));
			}
			val.Apply();
			SwapTexture(ref _huePickerBG, val);
		}

		private void CreateAlphaPickerBG()
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000d: Expected O, but got Unknown
			//IL_0049: Unknown result type (might be due to invalid IL or missing references)
			Texture2D val = new Texture2D(1, _pickerSize);
			int pickerSize = _pickerSize;
			float num = 1f / (float)pickerSize;
			for (int i = 0; i < pickerSize; i++)
			{
				val.SetPixel(0, i, new Color(tempColour.r, tempColour.g, tempColour.b, (float)i * num));
			}
			val.Apply();
			SwapTexture(ref _alphaPickerBG, val);
		}

		private void CreateAlphaBG(ref Texture2D bg, int width, int height)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0008: Expected O, but got Unknown
			//IL_0024: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Unknown result type (might be due to invalid IL or missing references)
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			//IL_005c: Unknown result type (might be due to invalid IL or missing references)
			Texture2D val = new Texture2D(width, height);
			Color[] array = (Color[])(object)new Color[_alphaBGBlockSize * _alphaBGBlockSize];
			for (int i = 0; i < array.Length; i++)
			{
				array[i] = _alphaBGColorA;
			}
			Color[] array2 = (Color[])(object)new Color[_alphaBGBlockSize * _alphaBGBlockSize];
			for (int j = 0; j < array2.Length; j++)
			{
				array2[j] = _alphaBGColorB;
			}
			int num = 0;
			for (int k = 0; k < width; k += _alphaBGBlockSize)
			{
				int num2 = num;
				for (int l = 0; l < height; l += _alphaBGBlockSize)
				{
					val.SetPixels(k, l, _alphaBGBlockSize, _alphaBGBlockSize, (num2 % 2 == 0) ? array : array2);
					num2++;
				}
				num++;
			}
			val.Apply();
			SwapTexture(ref bg, val);
		}

		public void CreatePreviewBG(ref Texture2D bg, Color col)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			SwapTexture(ref bg, SolidColorMaterials.NewSolidColorTexture(col));
		}

		public void PickerAction(Vector2 pos)
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			_S = UnitsPerPixel * pos.x;
			_V = 1f - UnitsPerPixel * pos.y;
			CreateAlphaPickerBG();
			NotifyHSVUpdated();
			_position = pos;
		}

		public void HueAction(float pos)
		{
			H = 1f - UnitsPerPixel * pos;
			_huePosition = pos;
		}

		public void AlphaAction(float pos)
		{
			A = 1f - UnitsPerPixel * pos;
			_alphaPosition = pos;
		}

		public override void SetInitialSizeAndPosition()
		{
			//IL_0003: Unknown result type (might be due to invalid IL or missing references)
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			//IL_0051: Unknown result type (might be due to invalid IL or missing references)
			//IL_0068: Unknown result type (might be due to invalid IL or missing references)
			//IL_0078: Unknown result type (might be due to invalid IL or missing references)
			//IL_008f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0095: Unknown result type (might be due to invalid IL or missing references)
			//IL_009b: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
			Vector2 val = default(Vector2);
			((Vector2)(ref val))..ctor(Mathf.Min(((Window)this).InitialSize.x, (float)UI.screenWidth), Mathf.Min(((Window)this).InitialSize.y, (float)UI.screenHeight - 35f));
			Vector2 val2 = default(Vector2);
			((Vector2)(ref val2))..ctor(Mathf.Max(0f, Mathf.Min(InitialPosition.x, (float)UI.screenWidth - val.x)), Mathf.Max(0f, Mathf.Min(InitialPosition.y, (float)UI.screenHeight - val.y)));
			base.windowRect = new Rect(val2.x, val2.y, val.x, val.y);
		}

		public override void PreOpen()
		{
			((Window)this).PreOpen();
			NotifyHSVUpdated();
			_alphaPosition = curColour.a / UnitsPerPixel;
		}

		public static string RGBtoHex(Color col)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			int num = (int)Mathf.Clamp(col.r * 256f, 0f, 255f);
			int num2 = (int)Mathf.Clamp(col.g * 256f, 0f, 255f);
			int num3 = (int)Mathf.Clamp(col.b * 256f, 0f, 255f);
			int num4 = (int)Mathf.Clamp(col.a * 256f, 0f, 255f);
			return "#" + num.ToString("X2") + num2.ToString("X2") + num3.ToString("X2") + num4.ToString("X2");
		}

		public static bool TryGetColorFromHex(string hex, out Color col)
		{
			//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
			Color val = default(Color);
			((Color)(ref val))..ctor(0f, 0f, 0f);
			if (hex != null && hex.Length == 9)
			{
				try
				{
					string text = hex.Substring(1, hex.Length - 1);
					val.r = (float)int.Parse(text.Substring(0, 2), NumberStyles.AllowHexSpecifier) / 255f;
					val.g = (float)int.Parse(text.Substring(2, 2), NumberStyles.AllowHexSpecifier) / 255f;
					val.b = (float)int.Parse(text.Substring(4, 2), NumberStyles.AllowHexSpecifier) / 255f;
					if (text.Length == 8)
					{
						val.a = (float)int.Parse(text.Substring(6, 2), NumberStyles.AllowHexSpecifier) / 255f;
					}
					else
					{
						val.a = 1f;
					}
				}
				catch (Exception)
				{
					col = Color.white;
					return false;
				}
				col = val;
				return true;
			}
			col = Color.white;
			return false;
		}

		public override void DoWindowContents(Rect inRect)
		{
			//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
			//IL_01bf: Unknown result type (might be due to invalid IL or missing references)
			//IL_01cb: Unknown result type (might be due to invalid IL or missing references)
			//IL_01d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_01e3: Unknown result type (might be due to invalid IL or missing references)
			//IL_01ef: Unknown result type (might be due to invalid IL or missing references)
			//IL_01fb: Unknown result type (might be due to invalid IL or missing references)
			//IL_0207: Unknown result type (might be due to invalid IL or missing references)
			//IL_0213: Unknown result type (might be due to invalid IL or missing references)
			//IL_02f2: Unknown result type (might be due to invalid IL or missing references)
			//IL_02f7: Unknown result type (might be due to invalid IL or missing references)
			//IL_0304: Unknown result type (might be due to invalid IL or missing references)
			//IL_0311: Unknown result type (might be due to invalid IL or missing references)
			//IL_031d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0327: Unknown result type (might be due to invalid IL or missing references)
			//IL_0330: Unknown result type (might be due to invalid IL or missing references)
			//IL_0340: Unknown result type (might be due to invalid IL or missing references)
			//IL_0359: Unknown result type (might be due to invalid IL or missing references)
			//IL_03a4: Unknown result type (might be due to invalid IL or missing references)
			//IL_044f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0500: Unknown result type (might be due to invalid IL or missing references)
			//IL_03c3: Unknown result type (might be due to invalid IL or missing references)
			//IL_03c9: Invalid comparison between Unknown and I4
			//IL_037d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0390: Unknown result type (might be due to invalid IL or missing references)
			//IL_0395: Unknown result type (might be due to invalid IL or missing references)
			//IL_039a: Unknown result type (might be due to invalid IL or missing references)
			//IL_039d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0528: Unknown result type (might be due to invalid IL or missing references)
			//IL_046e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0474: Invalid comparison between Unknown and I4
			//IL_03d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_03fa: Unknown result type (might be due to invalid IL or missing references)
			//IL_0549: Unknown result type (might be due to invalid IL or missing references)
			//IL_0482: Unknown result type (might be due to invalid IL or missing references)
			//IL_04a5: Unknown result type (might be due to invalid IL or missing references)
			//IL_0433: Unknown result type (might be due to invalid IL or missing references)
			//IL_04de: Unknown result type (might be due to invalid IL or missing references)
			//IL_05b0: Unknown result type (might be due to invalid IL or missing references)
			//IL_05c2: Unknown result type (might be due to invalid IL or missing references)
			//IL_057f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0584: Unknown result type (might be due to invalid IL or missing references)
			//IL_05a5: Unknown result type (might be due to invalid IL or missing references)
			//IL_0596: Unknown result type (might be due to invalid IL or missing references)
			//IL_0598: Unknown result type (might be due to invalid IL or missing references)
			_ = first;
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(((Rect)(ref inRect)).xMin, ((Rect)(ref inRect)).yMin, (float)_pickerSize, (float)_pickerSize);
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(((Rect)(ref val)).xMax + _margin, ((Rect)(ref inRect)).yMin, (float)_sliderWidth, (float)_pickerSize);
			Rect val3 = default(Rect);
			((Rect)(ref val3))..ctor(((Rect)(ref val2)).xMax + _margin, ((Rect)(ref inRect)).yMin, (float)_sliderWidth, (float)_pickerSize);
			Rect val4 = default(Rect);
			((Rect)(ref val4))..ctor(((Rect)(ref val3)).xMax + _margin, ((Rect)(ref inRect)).yMin, (float)_previewSize, (float)_previewSize);
			Rect val5 = new Rect(((Rect)(ref val4)).xMax, ((Rect)(ref inRect)).yMin, (float)_previewSize, (float)_previewSize);
			Rect val6 = default(Rect);
			((Rect)(ref val6))..ctor(((Rect)(ref val3)).xMax + _margin, ((Rect)(ref inRect)).yMax - _fieldHeight, (float)(_previewSize * 2), _fieldHeight);
			Rect val7 = default(Rect);
			((Rect)(ref val7))..ctor(((Rect)(ref val3)).xMax + _margin, ((Rect)(ref inRect)).yMax - 2f * _fieldHeight - _margin, (float)_previewSize - _margin / 2f, _fieldHeight);
			Rect val8 = default(Rect);
			((Rect)(ref val8))..ctor(((Rect)(ref val7)).xMax + _margin, ((Rect)(ref val7)).yMin, (float)_previewSize - _margin / 2f, _fieldHeight);
			Rect val9 = default(Rect);
			((Rect)(ref val9))..ctor(((Rect)(ref val3)).xMax + _margin, ((Rect)(ref inRect)).yMax - 3f * _fieldHeight - 2f * _margin, (float)(_previewSize * 2), _fieldHeight);
			GUI.DrawTexture(val, (Texture)(object)PickerAlphaBG);
			GUI.DrawTexture(val3, (Texture)(object)SliderAlphaBG);
			GUI.DrawTexture(val4, (Texture)(object)PreviewAlphaBG);
			GUI.DrawTexture(val5, (Texture)(object)PreviewAlphaBG);
			GUI.DrawTexture(val, (Texture)(object)ColourPickerBG);
			GUI.DrawTexture(val2, (Texture)(object)HuePickerBG);
			GUI.DrawTexture(val3, (Texture)(object)AlphaPickerBG);
			GUI.DrawTexture(val4, (Texture)(object)TempPreviewBG);
			GUI.DrawTexture(val5, (Texture)(object)PreviewBG);
			Rect val10 = default(Rect);
			((Rect)(ref val10))..ctor(((Rect)(ref val2)).xMin - 3f, ((Rect)(ref val2)).yMin + _huePosition - (float)(_handleSize / 2), (float)_sliderWidth + 6f, (float)_handleSize);
			Rect val11 = default(Rect);
			((Rect)(ref val11))..ctor(((Rect)(ref val3)).xMin - 3f, ((Rect)(ref val3)).yMin + _alphaPosition - (float)(_handleSize / 2), (float)_sliderWidth + 6f, (float)_handleSize);
			Rect val12 = new Rect(((Rect)(ref val)).xMin + _position.x - (float)(_handleSize / 2), ((Rect)(ref val)).yMin + _position.y - (float)(_handleSize / 2), (float)_handleSize, (float)_handleSize);
			GUI.DrawTexture(val10, (Texture)(object)TempPreviewBG);
			GUI.DrawTexture(val11, (Texture)(object)TempPreviewBG);
			GUI.DrawTexture(val12, (Texture)(object)TempPreviewBG);
			GUI.color = Color.gray;
			Widgets.DrawBox(val10, 1, (Texture2D)null);
			Widgets.DrawBox(val11, 1, (Texture2D)null);
			Widgets.DrawBox(val12, 1, (Texture2D)null);
			GUI.color = Color.white;
			if (Input.GetMouseButtonUp(0))
			{
				_activeControl = Controls.none;
			}
			if (Mouse.IsOver(val))
			{
				if (Input.GetMouseButtonDown(0))
				{
					_activeControl = Controls.colourPicker;
				}
				if (_activeControl == Controls.colourPicker)
				{
					Vector2 pos = Event.current.mousePosition - new Vector2(((Rect)(ref val)).xMin, ((Rect)(ref val)).yMin);
					PickerAction(pos);
				}
			}
			if (Mouse.IsOver(val2))
			{
				if (Input.GetMouseButtonDown(0))
				{
					_activeControl = Controls.huePicker;
				}
				if ((int)Event.current.type == 6)
				{
					H -= Event.current.delta.y * UnitsPerPixel;
					_huePosition = Mathf.Clamp(_huePosition + Event.current.delta.y, 0f, (float)_pickerSize);
					Event.current.Use();
				}
				if (_activeControl == Controls.huePicker)
				{
					float pos2 = Event.current.mousePosition.y - ((Rect)(ref val2)).yMin;
					HueAction(pos2);
				}
			}
			if (Mouse.IsOver(val3))
			{
				if (Input.GetMouseButtonDown(0))
				{
					_activeControl = Controls.alphaPicker;
				}
				if ((int)Event.current.type == 6)
				{
					A -= Event.current.delta.y * UnitsPerPixel;
					_alphaPosition = Mathf.Clamp(_alphaPosition + Event.current.delta.y, 0f, (float)_pickerSize);
					Event.current.Use();
				}
				if (_activeControl == Controls.alphaPicker)
				{
					float pos3 = Event.current.mousePosition.y - ((Rect)(ref val3)).yMin;
					AlphaAction(pos3);
				}
			}
			Text.Font = (GameFont)1;
			if (Widgets.ButtonText(val6, "OK", true, false, true, (TextAnchor?)null))
			{
				SetColor();
				((Window)this).Close(true);
			}
			if (Widgets.ButtonText(val7, "Apply", true, false, true, (TextAnchor?)null))
			{
				SetColor();
			}
			if (Widgets.ButtonText(val8, "Cancel", true, false, true, (TextAnchor?)null))
			{
				((Window)this).Close(true);
			}
			if (_hexIn != _hexOut)
			{
				Color col = tempColour;
				if (TryGetColorFromHex(_hexIn, out col))
				{
					tempColour = col;
					NotifyRGBUpdated();
				}
				else
				{
					GUI.color = Color.red;
				}
			}
			_hexIn = Widgets.TextField(val9, _hexIn);
			GUI.color = Color.white;
		}
	}
	internal class HSV
	{
		public static Color ToRGBA(float H, float S, float V, float A = 1f)
		{
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0184: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a0: Unknown result type (might be due to invalid IL or missing references)
			//IL_01bc: Unknown result type (might be due to invalid IL or missing references)
			//IL_01ed: Unknown result type (might be due to invalid IL or missing references)
			if (S == 0f)
			{
				return new Color(V, V, V, A);
			}
			if (V == 0f)
			{
				return new Color(0f, 0f, 0f, A);
			}
			Color black = Color.black;
			float num = H * 6f;
			int num2 = Mathf.FloorToInt(num);
			float num3 = num - (float)num2;
			float num4 = V * (1f - S);
			float num5 = V * (1f - S * num3);
			float num6 = V * (1f - S * (1f - num3));
			switch (num2)
			{
			case -1:
				black.r = V;
				black.g = num4;
				black.b = num5;
				break;
			case 0:
				black.r = V;
				black.g = num6;
				black.b = num4;
				break;
			case 1:
				black.r = num5;
				black.g = V;
				black.b = num4;
				break;
			case 2:
				black.r = num4;
				black.g = V;
				black.b = num6;
				break;
			case 3:
				black.r = num4;
				black.g = num5;
				black.b = V;
				break;
			case 4:
				black.r = num6;
				black.g = num4;
				black.b = V;
				break;
			case 5:
				black.r = V;
				black.g = num4;
				black.b = num5;
				break;
			case 6:
				black.r = V;
				black.g = num6;
				black.b = num4;
				break;
			}
			black.r = Mathf.Clamp(black.r, 0f, 1f);
			black.g = Mathf.Clamp(black.g, 0f, 1f);
			black.b = Mathf.Clamp(black.b, 0f, 1f);
			black.a = Mathf.Clamp(A, 0f, 1f);
			return black;
		}

		public static void ToHSV(Color rgbColor, out float H, out float S, out float V)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0042: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_006f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0075: Unknown result type (might be due to invalid IL or missing references)
			//IL_007b: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			if (rgbColor.b > rgbColor.g && rgbColor.b > rgbColor.r)
			{
				RGBToHSVHelper(4f, rgbColor.b, rgbColor.r, rgbColor.g, out H, out S, out V);
			}
			else if (rgbColor.g > rgbColor.r)
			{
				RGBToHSVHelper(2f, rgbColor.g, rgbColor.b, rgbColor.r, out H, out S, out V);
			}
			else
			{
				RGBToHSVHelper(0f, rgbColor.r, rgbColor.g, rgbColor.b, out H, out S, out V);
			}
		}

		private static void RGBToHSVHelper(float offset, float dominantcolor, float colorone, float colortwo, out float H, out float S, out float V)
		{
			V = dominantcolor;
			if (V != 0f)
			{
				float num = ((!(colorone > colortwo)) ? colorone : colortwo);
				float num2 = V - num;
				if (num2 != 0f)
				{
					S = num2 / V;
					H = offset + (colorone - colortwo) / num2;
				}
				else
				{
					S = 0f;
					H = offset + (colorone - colortwo);
				}
				H /= 6f;
				if (H < 0f)
				{
					H += 1f;
				}
			}
			else
			{
				S = 0f;
				H = 0f;
			}
		}
	}
	public class ApparelUtil
	{
		public static Pawn WearerOf(ThingComp comp)
		{
			IThingHolder parentHolder = comp.ParentHolder;
			return ((Pawn_ApparelTracker)(((parentHolder is Pawn_ApparelTracker) ? parentHolder : null)?)).pawn;
		}
	}
	public class CompProperties_Teleporter : CompProperties
	{
		public TeleporterType teleporterType = TeleporterType.world;

		public List<string> networkTags = new List<string>();

		public TeleporterDirection direction = TeleporterDirection.both;

		public bool needsPower;

		public int energyCost;

		public bool usesFuel;

		public float fuelCost;

		public bool receiverMustBeActive;

		public int useDuration = 20;

		public bool isPad;

		public bool canSendNonPawns;

		public IntVec2 teleportArea;

		public SoundDef sound;

		public CompProperties_Teleporter()
		{
			base.compClass = typeof(Comp_Teleporter);
		}
	}
	public enum TeleporterType
	{
		local,
		world
	}
	public enum TeleporterDirection
	{
		transmitter,
		receiver,
		both
	}
	public class Comp_Named : ThingComp
	{
		private string name;

		public CompProperties_Named Props => (CompProperties_Named)(object)base.props;

		public override void PostExposeData()
		{
			((ThingComp)this).PostExposeData();
			Scribe_Values.Look<string>(ref name, "name", (string)null, false);
		}

		public override void Initialize(CompProperties props)
		{
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			((ThingComp)this).Initialize(props);
			GrammarRequest val = default(GrammarRequest);
			((GrammarRequest)(ref val)).Includes.Add(Props.nameMaker);
			name = GenText.CapitalizeAsTitle(GrammarResolver.Resolve("name", val, (string)null, false, (string)null, (List<string>)null, (List<string>)null, true));
		}

		public override string TransformLabel(string label)
		{
			if (Props.nameFormat == ThingNameFormat.Prefix)
			{
				return name + " " + label;
			}
			if (Props.nameFormat == ThingNameFormat.Suffix)
			{
				return label + " " + name;
			}
			if (Props.nameFormat == ThingNameFormat.Bracketed)
			{
				return label + " (" + name + ")";
			}
			return name;
		}
	}
	public class Comp_VerbSwitch : ThingComp
	{
		[CompilerGenerated]
		private sealed class <VerbSwitchGizmos>d__16 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Comp_VerbSwitch <>4__this;

			Gizmo IEnumerator<Gizmo>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <VerbSwitchGizmos>d__16(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
				//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
				//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
				//IL_00db: Unknown result type (might be due to invalid IL or missing references)
				//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
				//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
				//IL_0104: Expected O, but got Unknown
				int num = <>1__state;
				Comp_VerbSwitch CS$<>8__locals16 = <>4__this;
				switch (num)
				{
				default:
					return false;
				case 0:
					<>1__state = -1;
					if (!CS$<>8__locals16.IsWorn)
					{
						_ = ((ThingComp)CS$<>8__locals16).parent;
					}
					else
					{
						_ = CS$<>8__locals16.GetUser;
					}
					if (Find.Selector.SingleSelectedThing == CS$<>8__locals16.GetUser && CS$<>8__locals16.GetUser.Drafted && ((Thing)CS$<>8__locals16.GetUser).Faction == Faction.OfPlayer)
					{
						Texture2D icon = ((!((Def)CS$<>8__locals16.Active.defaultProjectile).HasModExtension<DefModExt_VerbSwitchIcon>()) ? ((BuildableDef)CS$<>8__locals16.Active.defaultProjectile).uiIcon : ContentFinder<Texture2D>.Get(((Def)CS$<>8__locals16.Active.defaultProjectile).GetModExtension<DefModExt_VerbSwitchIcon>().gizmoIcon, true));
						Command_Action val = new Command_Action
						{
							icon = (Texture)(object)icon,
							defaultLabel = "Mode: " + CS$<>8__locals16.Active.label,
							defaultDesc = "Switch weapon mode.",
							activateSound = SoundDefOf.Click,
							action = delegate
							{
								Find.WindowStack.Add((Window)(object)CS$<>8__locals16.VerbSelectionList());
							}
						};
						if (CS$<>8__locals16.Props.requiredResearch != null && !CS$<>8__locals16.Props.requiredResearch.IsFinished)
						{
							((Gizmo)val).Disable(CS$<>8__locals16.Active.label + " (Requires Research: " + ((Def)CS$<>8__locals16.Props.requiredResearch).label + ")");
						}
						else if (CS$<>8__locals16.GetUser.stances.curStance.StanceBusy)
						{
							((Gizmo)val).Disable("Cannot switch while busy.");
						}
						<>2__current = (Gizmo)(object)val;
						<>1__state = 1;
						return true;
					}
					break;
				case 1:
					<>1__state = -1;
					break;
				}
				return false;
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
			{
				<VerbSwitchGizmos>d__16 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <VerbSwitchGizmos>d__16(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		public int fireMode;

		public CompProperties_VerbSwitch Props => base.props as CompProperties_VerbSwitch;

		public CompEquippable Equippable => ThingCompUtility.TryGetComp<CompEquippable>((Thing)(object)base.parent);

		protected virtual bool IsWorn => GetUser != null;

		protected virtual Pawn GetUser
		{
			get
			{
				//IL_0020: Unknown result type (might be due to invalid IL or missing references)
				//IL_0026: Expected O, but got Unknown
				if (((ThingComp)this).ParentHolder != null && ((ThingComp)this).ParentHolder is Pawn_EquipmentTracker)
				{
					return (Pawn)((ThingComp)this).ParentHolder.ParentHolder;
				}
				return null;
			}
		}

		public VerbProperties Active
		{
			get
			{
				if (base.parent != null && base.parent != null)
				{
					return ((Thing)base.parent).def.Verbs[fireMode];
				}
				return null;
			}
		}

		public override void PostExposeData()
		{
			((ThingComp)this).PostExposeData();
			Scribe_Values.Look<int>(ref fireMode, "fireMode", 0, false);
		}

		public Comp_VerbSwitch()
		{
			if (!(base.props is CompProperties_VerbSwitch))
			{
				base.props = (CompProperties)(object)new CompProperties_VerbSwitch();
			}
		}

		public override void CompTick()
		{
			((ThingComp)this).CompTick();
		}

		public void SwitchFireMode(int x)
		{
			//IL_0046: Unknown result type (might be due to invalid IL or missing references)
			//IL_0056: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Expected O, but got Unknown
			fireMode = x;
			if (Props.useCooldown)
			{
				GetUser.stances.SetStance((Stance)new Stance_Cooldown(Active.AdjustedCooldownTicks(Equippable.PrimaryVerb, GetUser), Equippable.PrimaryVerb.CurrentTarget, Equippable.PrimaryVerb));
			}
		}

		public FloatMenu VerbSelectionList()
		{
			//IL_0081: Unknown result type (might be due to invalid IL or missing references)
			//IL_0088: Expected O, but got Unknown
			//IL_0122: Unknown result type (might be due to invalid IL or missing references)
			//IL_0128: Expected O, but got Unknown
			List<FloatMenuOption> list = new List<FloatMenuOption>();
			foreach (VerbProperties verb in ((Thing)base.parent).def.Verbs)
			{
				int verbIndex = ((Thing)base.parent).def.Verbs.IndexOf(verb);
				if (fireMode == verbIndex)
				{
					continue;
				}
				FloatMenuOption val = new FloatMenuOption(verb.label, (Action)delegate
				{
					SwitchFireMode(verbIndex);
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
				if (Props.requiredResearchSpecific.Exists((VerbSwitchPair pair) => pair.index == verbIndex))
				{
					ResearchProjectDef research = Props.requiredResearchSpecific.Find((VerbSwitchPair pair) => pair.index == verbIndex).research;
					if (!research.IsFinished)
					{
						val.Label = verb.label + " (Requires Research: " + ((Def)research).label + ")";
						val.Disabled = true;
					}
				}
				list.Add(val);
			}
			return new FloatMenu(list);
		}

		[IteratorStateMachine(typeof(<VerbSwitchGizmos>d__16))]
		public IEnumerable<Gizmo> VerbSwitchGizmos()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <VerbSwitchGizmos>d__16(-2)
			{
				<>4__this = this
			};
		}
	}
	public class VerbSwitchPair
	{
		public int index;

		public ResearchProjectDef research;
	}
	public class Comp_AreaEffects : ThingComp
	{
		public int tickTimer = -1;

		public CompProperties_AreaEffects Props => (CompProperties_AreaEffects)(object)base.props;

		public override void PostExposeData()
		{
			((ThingComp)this).PostExposeData();
			Scribe_Values.Look<int>(ref tickTimer, "tickTimer", -1, false);
		}

		public override void CompTick()
		{
			((ThingComp)this).CompTick();
			if (tickTimer < 0)
			{
				ApplyHediffsToPawns(GetNearbyPawns());
				tickTimer = Props.ticksBetweenRuns;
			}
			tickTimer--;
		}

		public void ApplyHediffsToPawns(List<Pawn> pawns)
		{
			//IL_007e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0084: Expected O, but got Unknown
			if (GenList.NullOrEmpty<Pawn>((IList<Pawn>)pawns))
			{
				return;
			}
			for (int i = 0; i < pawns.Count; i++)
			{
				foreach (HediffSeverityPairing applyHediff in Props.applyHediffs)
				{
					if (pawns[i].health.hediffSet.HasHediff(applyHediff.hediff, false))
					{
						Hediff firstHediffOfDef = pawns[i].health.hediffSet.GetFirstHediffOfDef(applyHediff.hediff, false);
						firstHediffOfDef.Severity += applyHediff.severityIncrease;
						continue;
					}
					Hediff val = new Hediff();
					val.def = applyHediff.hediff;
					val.Severity = applyHediff.severityInitial;
					pawns[i].health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
			}
		}

		public List<Pawn> GetNearbyPawns()
		{
			//IL_00da: Unknown result type (might be due to invalid IL or missing references)
			//IL_0101: Unknown result type (might be due to invalid IL or missing references)
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			List<Pawn> list = new List<Pawn>();
			if (Props.roomBased)
			{
				Room room = RegionAndRoomQuery.GetRoom((Thing)(object)base.parent, (RegionType)15);
				if (room != null && (!Props.roomRequiresRoof || room.PsychologicallyOutdoors))
				{
					List<IntVec3> list2 = room.Cells.ToList();
					for (int i = 0; i < list2.Count; i++)
					{
						foreach (Thing thing in GridsUtility.GetThingList(list2[i], ((Thing)base.parent).Map))
						{
							if (thing is Pawn && !((IEnumerable<Thing>)list).Contains(thing))
							{
								list.Add((Pawn)(object)((thing is Pawn) ? thing : null));
							}
						}
					}
					return list;
				}
			}
			if (Props.radius > 0)
			{
				List<IntVec3> list3 = GenRadial.RadialCellsAround(((Thing)base.parent).Position, (float)Props.radius, true).ToList();
				for (int j = 0; j < list3.Count; j++)
				{
					foreach (Thing thing2 in GridsUtility.GetThingList(list3[j], ((Thing)base.parent).Map))
					{
						if (thing2 is Pawn && !((IEnumerable<Thing>)list).Contains(thing2))
						{
							list.Add((Pawn)(object)((thing2 is Pawn) ? thing2 : null));
						}
					}
				}
				return list;
			}
			return list;
		}
	}
	public class Comp_Recall : ThingComp
	{
		[CompilerGenerated]
		private sealed class <>c__DisplayClass10_0
		{
			public Thing receiver;

			public Comp_Recall <>4__this;

			internal void <DestinationFloatMenuOptions>b__0()
			{
				<>4__this.target = receiver;
			}
		}

		[CompilerGenerated]
		private sealed class <CompGetWornGizmosExtra>d__8 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Comp_Recall <>4__this;

			private IEnumerator<Gizmo> <>7__wrap1;

			Gizmo IEnumerator<Gizmo>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <CompGetWornGizmosExtra>d__8(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>7__wrap1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
				//IL_00de: Unknown result type (might be due to invalid IL or missing references)
				//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
				//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
				try
				{
					int num = <>1__state;
					Comp_Recall CS$<>8__locals12 = <>4__this;
					string text;
					switch (num)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<>7__wrap1 = CS$<>8__locals12.<>n__0().GetEnumerator();
						<>1__state = -3;
						goto IL_0074;
					case 1:
						<>1__state = -3;
						goto IL_0074;
					case 2:
						{
							<>1__state = -1;
							break;
						}
						IL_0074:
						if (<>7__wrap1.MoveNext())
						{
							Gizmo current = <>7__wrap1.Current;
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = null;
						text = "";
						if (CS$<>8__locals12.compReloadable != null && !((CompApparelVerbOwner)CS$<>8__locals12.compReloadable).CanBeUsed(ref text))
						{
							break;
						}
						<>2__current = (Gizmo)(object)new Command_FloatAction
						{
							defaultLabel = TaggedString.op_Implicit((CS$<>8__locals12.target != null) ? TranslatorFormattedStringExtensions.Translate("TabulaRasa.RecallDest", NamedArgument.op_Implicit(((Entity)CS$<>8__locals12.target).LabelCap)) : Translator.Translate("TabulaRasa.RecallLabel")),
							defaultDesc = TaggedString.op_Implicit(Translator.Translate("TabulaRasa.RecallDesc")),
							activateSound = SoundDefOf.Click,
							icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Buttons/Drop", true),
							action = delegate
							{
								//IL_005f: Unknown result type (might be due to invalid IL or missing references)
								//IL_0064: Unknown result type (might be due to invalid IL or missing references)
								//IL_006f: Unknown result type (might be due to invalid IL or missing references)
								if (CS$<>8__locals12.target == null)
								{
									Messages.Message("No destination selected. Right click the gizmo to select one.", MessageTypeDefOf.CautionInput, true);
								}
								else if (CS$<>8__locals12.Props.receiverMustBeActive && !ThingCompUtility.TryGetComp<Comp_Teleporter>(CS$<>8__locals12.target).IsActive)
								{
									Messages.Message("Selected destination is currently inactive, cannot recall to.", MessageTypeDefOf.CautionInput, true);
								}
								else
								{
									CS$<>8__locals12.GetPawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(TabulaRasaDefOf.TabulaRasa_UseRecall, LocalTargetInfo.op_Implicit(((Thing)CS$<>8__locals12.GetPawn).Position), LocalTargetInfo.op_Implicit((Thing)(object)((ThingComp)CS$<>8__locals12).parent)), (JobTag?)(JobTag)0, false);
								}
							},
							floatMenuFunc = CS$<>8__locals12.DestinationFloatMenuOptions
						};
						<>1__state = 2;
						return true;
					}
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				if (<>7__wrap1 != null)
				{
					<>7__wrap1.Dispose();
				}
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
			{
				<CompGetWornGizmosExtra>d__8 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <CompGetWornGizmosExtra>d__8(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		[CompilerGenerated]
		private sealed class <DestinationFloatMenuOptions>d__10 : IEnumerable<FloatMenuOption>, IEnumerable, IEnumerator<FloatMenuOption>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private FloatMenuOption <>2__current;

			private int <>l__initialThreadId;

			public Comp_Recall <>4__this;

			private List<Thing>.Enumerator <>7__wrap1;

			FloatMenuOption IEnumerator<FloatMenuOption>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <DestinationFloatMenuOptions>d__10(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 2)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>7__wrap1 = default(List<Thing>.Enumerator);
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_0072: Unknown result type (might be due to invalid IL or missing references)
				//IL_0079: Expected O, but got Unknown
				//IL_01b5: Unknown result type (might be due to invalid IL or missing references)
				//IL_01bc: Expected O, but got Unknown
				//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
				//IL_00fe: Expected O, but got Unknown
				try
				{
					int num = <>1__state;
					Comp_Recall comp_Recall = <>4__this;
					switch (num)
					{
					default:
						return false;
					case 0:
					{
						<>1__state = -1;
						string text = "";
						if (comp_Recall.compReloadable == null || ((CompApparelVerbOwner)comp_Recall.compReloadable).CanBeUsed(ref text))
						{
							if (GenList.NullOrEmpty<Thing>((IList<Thing>)comp_Recall.GetAllViableTeleporters()))
							{
								FloatMenuOption val = new FloatMenuOption("No destinations to choose from.", (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
								<>2__current = val;
								<>1__state = 1;
								return true;
							}
							<>7__wrap1 = comp_Recall.GetAllViableTeleporters().GetEnumerator();
							<>1__state = -3;
							goto IL_017f;
						}
						FloatMenuOption val2 = new FloatMenuOption("No uses remaining.", (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
						<>2__current = val2;
						<>1__state = 3;
						return true;
					}
					case 1:
						<>1__state = -1;
						break;
					case 2:
						<>1__state = -3;
						goto IL_017f;
					case 3:
						{
							<>1__state = -1;
							break;
						}
						IL_017f:
						if (<>7__wrap1.MoveNext())
						{
							<>c__DisplayClass10_0 CS$<>8__locals5 = new <>c__DisplayClass10_0
							{
								<>4__this = comp_Recall,
								receiver = <>7__wrap1.Current
							};
							Comp_Teleporter comp_Teleporter = ThingCompUtility.TryGetComp<Comp_Teleporter>(CS$<>8__locals5.receiver);
							FloatMenuOption val3 = new FloatMenuOption((string)null, (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
							if (comp_Recall.Props.receiverMustBeActive && !comp_Teleporter.IsActive)
							{
								val3.Label = "Destination Inactive: " + ((Entity)CS$<>8__locals5.receiver).Label;
							}
							else
							{
								val3.Label = "Set Destination: " + ((Entity)CS$<>8__locals5.receiver).Label;
								val3.action = delegate
								{
									CS$<>8__locals5.<>4__this.target = CS$<>8__locals5.receiver;
								};
							}
							<>2__current = val3;
							<>1__state = 2;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = default(List<Thing>.Enumerator);
						break;
					}
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				((IDisposable)<>7__wrap1/*cast due to .constrained prefix*/).Dispose();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<FloatMenuOption> IEnumerable<FloatMenuOption>.GetEnumerator()
			{
				<DestinationFloatMenuOptions>d__10 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <DestinationFloatMenuOptions>d__10(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<FloatMenuOption>)this).GetEnumerator();
			}
		}

		public CompApparelReloadable compReloadable;

		public Thing target;

		public CompProperties_Teleporter Props => (CompProperties_Teleporter)(object)base.props;

		public Pawn GetPawn => ApparelUtil.WearerOf((ThingComp)(object)this);

		public Comp_Recall()
		{
			compReloadable = ThingCompUtility.TryGetComp<CompApparelReloadable>((Thing)(object)base.parent);
		}

		public override void PostExposeData()
		{
			((ThingComp)this).PostExposeData();
			Scribe_References.Look<Thing>(ref target, "target", false);
		}

		[IteratorStateMachine(typeof(<CompGetWornGizmosExtra>d__8))]
		public override IEnumerable<Gizmo> CompGetWornGizmosExtra()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <CompGetWornGizmosExtra>d__8(-2)
			{
				<>4__this = this
			};
		}

		private List<Thing> GetAllViableTeleporters(bool needPad = false)
		{
			List<Thing> list = new List<Thing>();
			if (Props.teleporterType == TeleporterType.world)
			{
				foreach (Map map in Current.Game.Maps)
				{
					foreach (Thing item in map.GetComponent<MapComp_Teleporter>().allMapTeleports.Where((Thing t) => t != base.parent))
					{
						Comp_Teleporter comp_Teleporter = ThingCompUtility.TryGetComp<Comp_Teleporter>(item);
						if (comp_Teleporter != null && !GenList.NullOrEmpty<string>((IList<string>)comp_Teleporter.Props.networkTags.Where((string t) => Props.networkTags.Contains(t)).ToList()) && comp_Teleporter.Props.direction != 0 && (!needPad || Props.isPad || comp_Teleporter.Props.isPad))
						{
							list.Add(item);
						}
					}
				}
			}
			else if (Props.teleporterType == TeleporterType.local)
			{
				foreach (Thing allMapTeleport in ((Thing)base.parent).Map.GetComponent<MapComp_Teleporter>().allMapTeleports)
				{
					Comp_Teleporter comp_Teleporter2 = ThingCompUtility.TryGetComp<Comp_Teleporter>(allMapTeleport);
					if (comp_Teleporter2 != null && !GenList.NullOrEmpty<string>((IList<string>)comp_Teleporter2.Props.networkTags.Where((string t) => Props.networkTags.Contains(t)).ToList()) && comp_Teleporter2.Props.direction != 0 && (!needPad || Props.isPad || comp_Teleporter2.Props.isPad))
					{
						list.Add(allMapTeleport);
					}
				}
			}
			return list;
		}

		[IteratorStateMachine(typeof(<DestinationFloatMenuOptions>d__10))]
		private IEnumerable<FloatMenuOption> DestinationFloatMenuOptions()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <DestinationFloatMenuOptions>d__10(-2)
			{
				<>4__this = this
			};
		}

		public void TeleportEffect(Pawn actor)
		{
			TeleportEffect((Thing)(object)actor);
		}

		public void TeleportEffect(Thing thing)
		{
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0066: Unknown result type (might be due to invalid IL or missing references)
			//IL_006b: Unknown result type (might be due to invalid IL or missing references)
			//IL_006e: Unknown result type (might be due to invalid IL or missing references)
			//IL_007f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0084: Unknown result type (might be due to invalid IL or missing references)
			//IL_0087: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Unknown result type (might be due to invalid IL or missing references)
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			IntVec3 position;
			if (Props.sound != null)
			{
				position = thing.Position;
				IntVec2 toIntVec = ((IntVec3)(ref position)).ToIntVec2;
				SoundInfo val = SoundInfo.InMap(new TargetInfo(((IntVec2)(ref toIntVec)).ToIntVec3, thing.Map, false), (MaintenanceType)0);
				SoundStarter.PlayOneShot(Props.sound, val);
			}
			position = thing.Position;
			FleckMaker.ThrowSmoke(((IntVec3)(ref position)).ToVector3(), thing.Map, 1.5f);
			position = thing.Position;
			FleckMaker.ThrowMicroSparks(((IntVec3)(ref position)).ToVector3(), thing.Map);
			position = thing.Position;
			FleckMaker.ThrowLightningGlow(((IntVec3)(ref position)).ToVector3(), thing.Map, 1.5f);
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private IEnumerable<Gizmo> <>n__0()
		{
			return ((ThingComp)this).CompGetWornGizmosExtra();
		}
	}
	public class Comp_Teleporter : ThingComp
	{
		[CompilerGenerated]
		private sealed class <>c__DisplayClass16_0
		{
			public Comp_Teleporter <>4__this;

			public Pawn selPawn;
		}

		[CompilerGenerated]
		private sealed class <>c__DisplayClass16_1
		{
			public Thing receiver;

			public <>c__DisplayClass16_0 CS$<>8__locals1;

			internal void <CompFloatMenuOptions>b__0()
			{
				//IL_003b: Unknown result type (might be due to invalid IL or missing references)
				CS$<>8__locals1.<>4__this.target = receiver;
				CS$<>8__locals1.selPawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(TabulaRasaDefOf.TabulaRasa_UseTeleporter, LocalTargetInfo.op_Implicit((Thing)(object)((ThingComp)CS$<>8__locals1.<>4__this).parent)), (JobTag?)(JobTag)0, false);
			}
		}

		[CompilerGenerated]
		private sealed class <>c__DisplayClass22_0
		{
			public Thing receiver;

			public Comp_Teleporter <>4__this;

			internal void <DestinationFloatMenuOptions>b__0()
			{
				<>4__this.TeleportToDestination(receiver);
			}
		}

		[CompilerGenerated]
		private sealed class <CompFloatMenuOptions>d__16 : IEnumerable<FloatMenuOption>, IEnumerable, IEnumerator<FloatMenuOption>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private FloatMenuOption <>2__current;

			private int <>l__initialThreadId;

			public Comp_Teleporter <>4__this;

			private Pawn selPawn;

			public Pawn <>3__selPawn;

			private <>c__DisplayClass16_0 <>8__1;

			private List<Thing>.Enumerator <>7__wrap1;

			private IEnumerator<FloatMenuOption> <>7__wrap2;

			FloatMenuOption IEnumerator<FloatMenuOption>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <CompFloatMenuOptions>d__16(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				switch (<>1__state)
				{
				case -3:
				case 3:
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
					break;
				case -4:
				case 5:
					try
					{
					}
					finally
					{
						<>m__Finally2();
					}
					break;
				}
				<>8__1 = null;
				<>7__wrap1 = default(List<Thing>.Enumerator);
				<>7__wrap2 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_0263: Unknown result type (might be due to invalid IL or missing references)
				//IL_026a: Expected O, but got Unknown
				//IL_0083: Unknown result type (might be due to invalid IL or missing references)
				//IL_0099: Unknown result type (might be due to invalid IL or missing references)
				//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
				//IL_00b6: Expected O, but got Unknown
				//IL_0180: Unknown result type (might be due to invalid IL or missing references)
				//IL_0187: Expected O, but got Unknown
				//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
				//IL_0102: Expected O, but got Unknown
				//IL_0202: Unknown result type (might be due to invalid IL or missing references)
				try
				{
					int num = <>1__state;
					Comp_Teleporter comp_Teleporter = <>4__this;
					switch (num)
					{
					default:
						return false;
					case 0:
					{
						<>1__state = -1;
						<>8__1 = new <>c__DisplayClass16_0();
						<>8__1.<>4__this = <>4__this;
						<>8__1.selPawn = selPawn;
						if (comp_Teleporter.IsActive)
						{
							if (!ReachabilityUtility.CanReach(<>8__1.selPawn, LocalTargetInfo.op_Implicit((Thing)(object)((ThingComp)comp_Teleporter).parent), (PathEndMode)4, (Danger)3, false, false, (TraverseMode)0))
							{
								FloatMenuOption val = new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("CannotUseNoPath")), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
								<>2__current = val;
								<>1__state = 1;
								return true;
							}
							List<Thing> allViableTeleporters = comp_Teleporter.GetAllViableTeleporters(needPad: false);
							if (GenList.NullOrEmpty<Thing>((IList<Thing>)allViableTeleporters))
							{
								FloatMenuOption val2 = new FloatMenuOption("No destinations to choose from.", (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
								<>2__current = val2;
								<>1__state = 2;
								return true;
							}
							<>7__wrap1 = allViableTeleporters.GetEnumerator();
							<>1__state = -3;
							goto IL_022d;
						}
						FloatMenuOption val3 = new FloatMenuOption("Teleporter not active", (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
						<>2__current = val3;
						<>1__state = 4;
						return true;
					}
					case 1:
						<>1__state = -1;
						goto IL_0284;
					case 2:
						<>1__state = -1;
						goto IL_0284;
					case 3:
						<>1__state = -3;
						goto IL_022d;
					case 4:
						<>1__state = -1;
						goto IL_0284;
					case 5:
						{
							<>1__state = -4;
							break;
						}
						IL_0284:
						<>7__wrap2 = comp_Teleporter.<>n__0(<>8__1.selPawn).GetEnumerator();
						<>1__state = -4;
						break;
						IL_022d:
						if (<>7__wrap1.MoveNext())
						{
							<>c__DisplayClass16_1 CS$<>8__locals8 = new <>c__DisplayClass16_1
							{
								CS$<>8__locals1 = <>8__1,
								receiver = <>7__wrap1.Current
							};
							Comp_Teleporter comp_Teleporter2 = ThingCompUtility.TryGetComp<Comp_Teleporter>(CS$<>8__locals8.receiver);
							FloatMenuOption val4 = new FloatMenuOption((string)null, (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
							if (comp_Teleporter.Props.receiverMustBeActive && !comp_Teleporter2.IsActive)
							{
								val4.Label = "Destination Inactive: " + ((Entity)CS$<>8__locals8.receiver).Label;
							}
							else
							{
								val4.Label = "Teleport To: " + ((Entity)CS$<>8__locals8.receiver).Label;
								val4.action = delegate
								{
									//IL_003b: Unknown result type (might be due to invalid IL or missing references)
									CS$<>8__locals8.CS$<>8__locals1.<>4__this.target = CS$<>8__locals8.receiver;
									CS$<>8__locals8.CS$<>8__locals1.selPawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(TabulaRasaDefOf.TabulaRasa_UseTeleporter, LocalTargetInfo.op_Implicit((Thing)(object)((ThingComp)CS$<>8__locals8.CS$<>8__locals1.<>4__this).parent)), (JobTag?)(JobTag)0, false);
								};
							}
							<>2__current = FloatMenuUtility.DecoratePrioritizedTask(val4, CS$<>8__locals8.CS$<>8__locals1.selPawn, LocalTargetInfo.op_Implicit((Thing)(object)((ThingComp)comp_Teleporter).parent), "ReservedBy", (ReservationLayerDef)null);
							<>1__state = 3;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = default(List<Thing>.Enumerator);
						goto IL_0284;
					}
					if (<>7__wrap2.MoveNext())
					{
						FloatMenuOption current = <>7__wrap2.Current;
						<>2__current = current;
						<>1__state = 5;
						return true;
					}
					<>m__Finally2();
					<>7__wrap2 = null;
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				((IDisposable)<>7__wrap1/*cast due to .constrained prefix*/).Dispose();
			}

			private void <>m__Finally2()
			{
				<>1__state = -1;
				if (<>7__wrap2 != null)
				{
					<>7__wrap2.Dispose();
				}
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<FloatMenuOption> IEnumerable<FloatMenuOption>.GetEnumerator()
			{
				<CompFloatMenuOptions>d__16 <CompFloatMenuOptions>d__;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					<CompFloatMenuOptions>d__ = this;
				}
				else
				{
					<CompFloatMenuOptions>d__ = new <CompFloatMenuOptions>d__16(0)
					{
						<>4__this = <>4__this
					};
				}
				<CompFloatMenuOptions>d__.selPawn = <>3__selPawn;
				return <CompFloatMenuOptions>d__;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<FloatMenuOption>)this).GetEnumerator();
			}
		}

		[CompilerGenerated]
		private sealed class <CompGetGizmosExtra>d__21 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Comp_Teleporter <>4__this;

			private IEnumerator<Gizmo> <>7__wrap1;

			Gizmo IEnumerator<Gizmo>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <CompGetGizmosExtra>d__21(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>7__wrap1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_009a: Unknown result type (might be due to invalid IL or missing references)
				//IL_009f: Unknown result type (might be due to invalid IL or missing references)
				//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
				//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
				//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
				//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
				//IL_00e8: Expected O, but got Unknown
				try
				{
					int num = <>1__state;
					Comp_Teleporter CS$<>8__locals3 = <>4__this;
					switch (num)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<>7__wrap1 = CS$<>8__locals3.<>n__1().GetEnumerator();
						<>1__state = -3;
						goto IL_0072;
					case 1:
						<>1__state = -3;
						goto IL_0072;
					case 2:
						{
							<>1__state = -1;
							break;
						}
						IL_0072:
						if (<>7__wrap1.MoveNext())
						{
							Gizmo current = <>7__wrap1.Current;
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = null;
						if (CS$<>8__locals3.Props.canSendNonPawns)
						{
							<>2__current = (Gizmo)new Command_Action
							{
								defaultLabel = "Send",
								defaultDesc = "Teleports everything on the teleporter to the selected destination.",
								activateSound = SoundDefOf.Click,
								icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Buttons/Drop", true),
								action = delegate
								{
									//IL_0011: Unknown result type (might be due to invalid IL or missing references)
									//IL_001b: Expected O, but got Unknown
									Find.WindowStack.Add((Window)new FloatMenu(CS$<>8__locals3.DestinationFloatMenuOptions(sending: true).ToList()));
								}
							};
							<>1__state = 2;
							return true;
						}
						break;
					}
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				if (<>7__wrap1 != null)
				{
					<>7__wrap1.Dispose();
				}
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
			{
				<CompGetGizmosExtra>d__21 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <CompGetGizmosExtra>d__21(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		[CompilerGenerated]
		private sealed class <DestinationFloatMenuOptions>d__22 : IEnumerable<FloatMenuOption>, IEnumerable, IEnumerator<FloatMenuOption>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private FloatMenuOption <>2__current;

			private int <>l__initialThreadId;

			public Comp_Teleporter <>4__this;

			private bool sending;

			public bool <>3__sending;

			private List<Thing>.Enumerator <>7__wrap1;

			FloatMenuOption IEnumerator<FloatMenuOption>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <DestinationFloatMenuOptions>d__22(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 2)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<>7__wrap1 = default(List<Thing>.Enumerator);
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_01eb: Unknown result type (might be due to invalid IL or missing references)
				//IL_01f2: Expected O, but got Unknown
				//IL_005d: Unknown result type (might be due to invalid IL or missing references)
				//IL_0063: Expected O, but got Unknown
				//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
				//IL_00e7: Expected O, but got Unknown
				try
				{
					int num = <>1__state;
					Comp_Teleporter comp_Teleporter = <>4__this;
					switch (num)
					{
					default:
						return false;
					case 0:
					{
						<>1__state = -1;
						if (comp_Teleporter.IsActive)
						{
							if (GenList.NullOrEmpty<Thing>((IList<Thing>)comp_Teleporter.GetAllViableTeleporters(needPad: true)))
							{
								FloatMenuOption val = new FloatMenuOption("No destinations to choose from.", (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
								<>2__current = val;
								<>1__state = 1;
								return true;
							}
							<>7__wrap1 = comp_Teleporter.GetAllViableTeleporters(needPad: true).GetEnumerator();
							<>1__state = -3;
							goto IL_01b5;
						}
						FloatMenuOption val2 = new FloatMenuOption("Teleporter not active", (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
						<>2__current = val2;
						<>1__state = 3;
						return true;
					}
					case 1:
						<>1__state = -1;
						break;
					case 2:
						<>1__state = -3;
						goto IL_01b5;
					case 3:
						{
							<>1__state = -1;
							break;
						}
						IL_01b5:
						if (<>7__wrap1.MoveNext())
						{
							<>c__DisplayClass22_0 CS$<>8__locals6 = new <>c__DisplayClass22_0
							{
								<>4__this = comp_Teleporter,
								receiver = <>7__wrap1.Current
							};
							Comp_Teleporter comp_Teleporter2 = ThingCompUtility.TryGetComp<Comp_Teleporter>(CS$<>8__locals6.receiver);
							FloatMenuOption val3 = new FloatMenuOption((string)null, (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
							if (comp_Teleporter.Props.receiverMustBeActive && !comp_Teleporter2.IsActive)
							{
								val3.Label = "Destination Inactive: " + ((Entity)CS$<>8__locals6.receiver).Label;
							}
							else if (sending)
							{
								val3.Label = "Teleport To: " + ((Entity)CS$<>8__locals6.receiver).Label;
								val3.action = delegate
								{
									CS$<>8__locals6.<>4__this.TeleportToDestination(CS$<>8__locals6.receiver);
								};
							}
							else
							{
								val3.Label = "Teleport From: " + ((Entity)CS$<>8__locals6.receiver).Label;
								val3.action = delegate
								{
								};
							}
							<>2__current = val3;
							<>1__state = 2;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = default(List<Thing>.Enumerator);
						break;
					}
					return false;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				((IDisposable)<>7__wrap1/*cast due to .constrained prefix*/).Dispose();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<FloatMenuOption> IEnumerable<FloatMenuOption>.GetEnumerator()
			{
				<DestinationFloatMenuOptions>d__22 <DestinationFloatMenuOptions>d__;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					<DestinationFloatMenuOptions>d__ = this;
				}
				else
				{
					<DestinationFloatMenuOptions>d__ = new <DestinationFloatMenuOptions>d__22(0)
					{
						<>4__this = <>4__this
					};
				}
				<DestinationFloatMenuOptions>d__.sending = <>3__sending;
				return <DestinationFloatMenuOptions>d__;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<FloatMenuOption>)this).GetEnumerator();
			}
		}

		public CompPowerTrader powerComp;

		public CompFlickable flickComp;

		public CompRefuelable fuelComp;

		public MapComp_Teleporter mapComp;

		public Thing target;

		public CompProperties_Teleporter Props => (CompProperties_Teleporter)(object)base.props;

		public bool IsActive
		{
			get
			{
				if (Props.needsPower && !IsPowered)
				{
					if (Props.usesFuel)
					{
						return HasFuel;
					}
					return true;
				}
				return true;
			}
		}

		public bool IsPowered
		{
			get
			{
				if (powerComp == null || !powerComp.PowerOn)
				{
					return powerComp == null;
				}
				return true;
			}
		}

		public bool HasFuel
		{
			get
			{
				if (fuelComp != null)
				{
					return fuelComp.Fuel > Props.fuelCost;
				}
				return false;
			}
		}

		public override void PostExposeData()
		{
			((ThingComp)this).PostExposeData();
		}

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
			powerComp = ThingCompUtility.TryGetComp<CompPowerTrader>((Thing)(object)base.parent);
			flickComp = ThingCompUtility.TryGetComp<CompFlickable>((Thing)(object)base.parent);
			fuelComp = ThingCompUtility.TryGetComp<CompRefuelable>((Thing)(object)base.parent);
			mapComp = ((Thing)base.parent).Map.GetComponent<MapComp_Teleporter>();
			mapComp.RegisterTeleporter((Thing)(object)base.parent);
		}

		public override void PostDestroy(DestroyMode mode, Map previousMap)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			((ThingComp)this).PostDestroy(mode, previousMap);
			mapComp.UnregisterTeleporter((Thing)(object)base.parent);
		}

		[IteratorStateMachine(typeof(<CompFloatMenuOptions>d__16))]
		public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <CompFloatMenuOptions>d__16(-2)
			{
				<>4__this = this,
				<>3__selPawn = selPawn
			};
		}

		private bool CanBeUsedBy(Pawn p)
		{
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			List<ThingComp> allComps = base.parent.AllComps;
			for (int i = 0; i < allComps.Count; i++)
			{
				ThingComp obj = allComps[i];
				CompUseEffect val = (CompUseEffect)(object)((obj is CompUseEffect) ? obj : null);
				if (val != null && !AcceptanceReport.op_Implicit(val.CanBeUsedBy(p)))
				{
					return false;
				}
			}
			return true;
		}

		private List<Thing> GetAllViableTeleporters(bool needPad)
		{
			List<Thing> list = new List<Thing>();
			if (Props.teleporterType == TeleporterType.world)
			{
				foreach (Map map in Current.Game.Maps)
				{
					foreach (Thing item in map.GetComponent<MapComp_Teleporter>().allMapTeleports.Where((Thing t) => t != base.parent))
					{
						Comp_Teleporter comp_Teleporter = ThingCompUtility.TryGetComp<Comp_Teleporter>(item);
						if (comp_Teleporter != null && !GenList.NullOrEmpty<string>((IList<string>)comp_Teleporter.Props.networkTags.Where((string t) => Props.networkTags.Contains(t)).ToList()) && comp_Teleporter.Props.direction != 0 && (!needPad || Props.isPad || comp_Teleporter.Props.isPad))
						{
							list.Add(item);
						}
					}
				}
			}
			else if (Props.teleporterType == TeleporterType.local)
			{
				foreach (Thing allMapTeleport in ((Thing)base.parent).Map.GetComponent<MapComp_Teleporter>().allMapTeleports)
				{
					Comp_Teleporter comp_Teleporter2 = ThingCompUtility.TryGetComp<Comp_Teleporter>(allMapTeleport);
					if (comp_Teleporter2 != null && !GenList.NullOrEmpty<string>((IList<string>)comp_Teleporter2.Props.networkTags.Where((string t) => Props.networkTags.Contains(t)).ToList()) && comp_Teleporter2.Props.direction != 0 && (!needPad || Props.isPad || comp_Teleporter2.Props.isPad))
					{
						list.Add(allMapTeleport);
					}
				}
			}
			return list;
		}

		public void TeleportEffect(Pawn actor)
		{
			TeleportEffect((Thing)(object)actor);
		}

		public void TeleportEffect(Thing thing)
		{
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0066: Unknown result type (might be due to invalid IL or missing references)
			//IL_006b: Unknown result type (might be due to invalid IL or missing references)
			//IL_006e: Unknown result type (might be due to invalid IL or missing references)
			//IL_007f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0084: Unknown result type (might be due to invalid IL or missing references)
			//IL_0087: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Unknown result type (might be due to invalid IL or missing references)
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			IntVec3 position;
			if (Props.sound != null)
			{
				position = thing.Position;
				IntVec2 toIntVec = ((IntVec3)(ref position)).ToIntVec2;
				SoundInfo val = SoundInfo.InMap(new TargetInfo(((IntVec2)(ref toIntVec)).ToIntVec3, thing.Map, false), (MaintenanceType)0);
				SoundStarter.PlayOneShot(Props.sound, val);
			}
			position = thing.Position;
			FleckMaker.ThrowSmoke(((IntVec3)(ref position)).ToVector3(), thing.Map, 1.5f);
			position = thing.Position;
			FleckMaker.ThrowMicroSparks(((IntVec3)(ref position)).ToVector3(), thing.Map);
			position = thing.Position;
			FleckMaker.ThrowLightningGlow(((IntVec3)(ref position)).ToVector3(), thing.Map, 1.5f);
		}

		[IteratorStateMachine(typeof(<CompGetGizmosExtra>d__21))]
		public override IEnumerable<Gizmo> CompGetGizmosExtra()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <CompGetGizmosExtra>d__21(-2)
			{
				<>4__this = this
			};
		}

		[IteratorStateMachine(typeof(<DestinationFloatMenuOptions>d__22))]
		public IEnumerable<FloatMenuOption> DestinationFloatMenuOptions(bool sending)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <DestinationFloatMenuOptions>d__22(-2)
			{
				<>4__this = this,
				<>3__sending = sending
			};
		}

		public static CellRect TeleportRect(IntVec3 center, Rot4 rot, IntVec2 size)
		{
			//IL_0004: Unknown result type (might be due to invalid IL or missing references)
			//IL_000a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			GenAdj.AdjustForRotation(ref center, ref size, rot);
			return new CellRect(center.x - (size.x - 1) / 2, center.z - (size.z - 1) / 2, size.x, size.z);
		}

		public void TeleportToDestination(Thing destination)
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			//IL_0040: Unknown result type (might be due to invalid IL or missing references)
			CellRect val = TeleportRect(((Thing)base.parent).Position, ((Thing)base.parent).Rotation, Props.teleportArea);
			List<IntVec3> list = ((CellRect)(ref val)).Cells.ToList();
			List<Thing> list2 = new List<Thing>();
			for (int i = 0; i < list.Count; i++)
			{
				List<Thing> list3 = GridsUtility.GetThingList(list[i], ((Thing)base.parent).Map).ToList();
				if (GenList.NullOrEmpty<Thing>((IList<Thing>)list3))
				{
					continue;
				}
				foreach (Thing item in list3)
				{
					if (item != base.parent && item != destination)
					{
						list2.Add(item);
					}
				}
			}
			foreach (Thing item2 in list2)
			{
				TeleportThing(item2, destination);
			}
		}

		public void TeleportThing(Thing thing, Thing destination)
		{
			//IL_0042: Unknown result type (might be due to invalid IL or missing references)
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_007f: Unknown result type (might be due to invalid IL or missing references)
			if (!IsPowered || !ThingCompUtility.TryGetComp<Comp_Teleporter>(destination).IsPowered || thing == base.parent || thing == destination)
			{
				return;
			}
			CellRect val = GenAdj.OccupiedRect(destination);
			List<IntVec3> list = ((CellRect)(ref val)).Cells.Where((IntVec3 c) => GenCollection.EnumerableNullOrEmpty<Thing>(from t in GridsUtility.GetThingList(c, destination.Map)
				where t != destination && t.def.thingClass != typeof(Filth)
				select t)).ToList();
			if (!GenList.NullOrEmpty<IntVec3>((IList<IntVec3>)list))
			{
				TeleportEffect(thing);
				((Entity)thing).DeSpawn((DestroyMode)0);
				GenSpawn.Spawn(thing, GenCollection.RandomElement<IntVec3>((IEnumerable<IntVec3>)list), destination.Map, (WipeMode)0);
				ThingCompUtility.TryGetComp<Comp_Teleporter>(destination).TeleportEffect(thing);
			}
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private IEnumerable<FloatMenuOption> <>n__0(Pawn selPawn)
		{
			return ((ThingComp)this).CompFloatMenuOptions(selPawn);
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private IEnumerable<Gizmo> <>n__1()
		{
			return ((ThingComp)this).CompGetGizmosExtra();
		}
	}
	public class JobDriver_UseRecall : JobDriver
	{
		[CompilerGenerated]
		private sealed class <>c__DisplayClass5_0
		{
			public Toil use;

			public JobDriver_UseRecall <>4__this;

			internal void <MakeNewToils>b__0()
			{
				<>c__DisplayClass5_1 obj = new <>c__DisplayClass5_1
				{
					CS$<>8__locals1 = this,
					actor = use.actor
				};
				obj.sendTeleporter = ((LocalTargetInfo)(ref obj.actor.CurJob.targetB)).Thing;
				((Action)delegate
				{
					//IL_004a: Unknown result type (might be due to invalid IL or missing references)
					if (obj.CS$<>8__locals1.<>4__this.destination != null)
					{
						ThingCompUtility.TryGetComp<Comp_Recall>(obj.sendTeleporter).TeleportEffect(obj.actor);
						((Entity)obj.actor).DeSpawn((DestroyMode)0);
						GenSpawn.Spawn((Thing)(object)obj.actor, obj.CS$<>8__locals1.<>4__this.destination.Position, obj.CS$<>8__locals1.<>4__this.destination.Map, (WipeMode)0);
						ThingCompUtility.TryGetComp<Comp_Teleporter>(obj.CS$<>8__locals1.<>4__this.destination).TeleportEffect(obj.actor);
					}
					else
					{
						Messages.Message("Teleport destination no longer valid.", MessageTypeDefOf.CautionInput, true);
					}
				})();
			}
		}

		[CompilerGenerated]
		private sealed class <>c__DisplayClass5_1
		{
			public Thing sendTeleporter;

			public Pawn actor;

			public <>c__DisplayClass5_0 CS$<>8__locals1;

			internal void <MakeNewToils>b__1()
			{
				//IL_004a: Unknown result type (might be due to invalid IL or missing references)
				if (CS$<>8__locals1.<>4__this.destination != null)
				{
					ThingCompUtility.TryGetComp<Comp_Recall>(sendTeleporter).TeleportEffect(actor);
					((Entity)actor).DeSpawn((DestroyMode)0);
					GenSpawn.Spawn((Thing)(object)actor, CS$<>8__locals1.<>4__this.destination.Position, CS$<>8__locals1.<>4__this.destination.Map, (WipeMode)0);
					ThingCompUtility.TryGetComp<Comp_Teleporter>(CS$<>8__locals1.<>4__this.destination).TeleportEffect(actor);
				}
				else
				{
					Messages.Message("Teleport destination no longer valid.", MessageTypeDefOf.CautionInput, true);
				}
			}
		}

		[CompilerGenerated]
		private sealed class <MakeNewToils>d__5 : IEnumerable<Toil>, IEnumerable, IEnumerator<Toil>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Toil <>2__current;

			private int <>l__initialThreadId;

			public JobDriver_UseRecall <>4__this;

			private <>c__DisplayClass5_0 <>8__1;

			Toil IEnumerator<Toil>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <MakeNewToils>d__5(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				<>8__1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
				//IL_00b4: Expected O, but got Unknown
				//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
				int num = <>1__state;
				JobDriver_UseRecall jobDriver_UseRecall = <>4__this;
				switch (num)
				{
				default:
					return false;
				case 0:
					<>1__state = -1;
					<>8__1 = new <>c__DisplayClass5_0();
					<>8__1.<>4__this = <>4__this;
					ToilFailConditions.FailOnIncapable<JobDriver_UseRecall>(jobDriver_UseRecall, PawnCapacityDefOf.Manipulation);
					<>2__current = Toils_Goto.GotoCell((TargetIndex)1, (PathEndMode)1);
					<>1__state = 1;
					return true;
				case 1:
				{
					<>1__state = -1;
					Toil val = Toils_General.Wait(jobDriver_UseRecall.useDuration, (TargetIndex)0);
					ToilEffects.WithProgressBarToilDelay(val, (TargetIndex)1, false, -0.5f);
					<>2__current = val;
					<>1__state = 2;
					return true;
				}
				case 2:
					<>1__state = -1;
					<>8__1.use = new Toil();
					<>8__1.use.initAction = delegate
					{
						<>c__DisplayClass5_1 obj = new <>c__DisplayClass5_1
						{
							CS$<>8__locals1 = <>8__1,
							actor = <>8__1.use.actor
						};
						obj.sendTeleporter = ((LocalTargetInfo)(ref obj.actor.CurJob.targetB)).Thing;
						((Action)delegate
						{
							//IL_004a: Unknown result type (might be due to invalid IL or missing references)
							if (obj.CS$<>8__locals1.<>4__this.destination != null)
							{
								ThingCompUtility.TryGetComp<Comp_Recall>(obj.sendTeleporter).TeleportEffect(obj.actor);
								((Entity)obj.actor).DeSpawn((DestroyMode)0);
								GenSpawn.Spawn((Thing)(object)obj.actor, obj.CS$<>8__locals1.<>4__this.destination.Position, obj.CS$<>8__locals1.<>4__this.destination.Map, (WipeMode)0);
								ThingCompUtility.TryGetComp<Comp_Teleporter>(obj.CS$<>8__locals1.<>4__this.destination).TeleportEffect(obj.actor);
							}
							else
							{
								Messages.Message("Teleport destination no longer valid.", MessageTypeDefOf.CautionInput, true);
							}
						})();
					};
					<>8__1.use.defaultCompleteMode = (ToilCompleteMode)1;
					<>2__current = <>8__1.use;
					<>1__state = 3;
					return true;
				case 3:
					<>1__state = -1;
					return false;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Toil> IEnumerable<Toil>.GetEnumerator()
			{
				<MakeNewToils>d__5 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <MakeNewToils>d__5(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Toil>)this).GetEnumerator();
			}
		}

		private int useDuration = -1;

		private Thing destination;

		public override void ExposeData()
		{
			((JobDriver)this).ExposeData();
			Scribe_Values.Look<int>(ref useDuration, "useDuration", 0, false);
			Scribe_References.Look<Thing>(ref destination, "destination", false);
		}

		public override void Notify_Starting()
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			((JobDriver)this).Notify_Starting();
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)2);
			Comp_Recall comp_Recall = ThingCompUtility.TryGetComp<Comp_Recall>(((LocalTargetInfo)(ref target)).Thing);
			useDuration = comp_Recall.Props.useDuration;
			destination = comp_Recall.target;
		}

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return true;
		}

		[IteratorStateMachine(typeof(<MakeNewToils>d__5))]
		public override IEnumerable<Toil> MakeNewToils()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <MakeNewToils>d__5(-2)
			{
				<>4__this = this
			};
		}
	}
	public class JobDriver_UseTeleporter : JobDriver
	{
		[CompilerGenerated]
		private sealed class <>c__DisplayClass5_0
		{
			public Toil use;

			public JobDriver_UseTeleporter <>4__this;

			internal void <MakeNewToils>b__0()
			{
				<>c__DisplayClass5_1 obj = new <>c__DisplayClass5_1
				{
					CS$<>8__locals1 = this,
					actor = use.actor
				};
				obj.sendTeleporter = ((LocalTargetInfo)(ref obj.actor.CurJob.targetA)).Thing;
				((Action)delegate
				{
					//IL_004a: Unknown result type (might be due to invalid IL or missing references)
					if (obj.CS$<>8__locals1.<>4__this.destination != null)
					{
						ThingCompUtility.TryGetComp<Comp_Teleporter>(obj.sendTeleporter).TeleportEffect(obj.actor);
						((Entity)obj.actor).DeSpawn((DestroyMode)0);
						GenSpawn.Spawn((Thing)(object)obj.actor, obj.CS$<>8__locals1.<>4__this.destination.Position, obj.CS$<>8__locals1.<>4__this.destination.Map, (WipeMode)0);
						ThingCompUtility.TryGetComp<Comp_Teleporter>(obj.CS$<>8__locals1.<>4__this.destination).TeleportEffect(obj.actor);
					}
					else
					{
						Messages.Message("Teleport destination no longer valid.", MessageTypeDefOf.CautionInput, true);
					}
				})();
			}
		}

		[CompilerGenerated]
		private sealed class <>c__DisplayClass5_1
		{
			public Thing sendTeleporter;

			public Pawn actor;

			public <>c__DisplayClass5_0 CS$<>8__locals1;

			internal void <MakeNewToils>b__1()
			{
				//IL_004a: Unknown result type (might be due to invalid IL or missing references)
				if (CS$<>8__locals1.<>4__this.destination != null)
				{
					ThingCompUtility.TryGetComp<Comp_Teleporter>(sendTeleporter).TeleportEffect(actor);
					((Entity)actor).DeSpawn((DestroyMode)0);
					GenSpawn.Spawn((Thing)(object)actor, CS$<>8__locals1.<>4__this.destination.Position, CS$<>8__locals1.<>4__this.destination.Map, (WipeMode)0);
					ThingCompUtility.TryGetComp<Comp_Teleporter>(CS$<>8__locals1.<>4__this.destination).TeleportEffect(actor);
				}
				else
				{
					Messages.Message("Teleport destination no longer valid.", MessageTypeDefOf.CautionInput, true);
				}
			}
		}

		[CompilerGenerated]
		private sealed class <MakeNewToils>d__5 : IEnumerable<Toil>, IEnumerable, IEnumerator<Toil>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Toil <>2__current;

			private int <>l__initialThreadId;

			public JobDriver_UseTeleporter <>4__this;

			private <>c__DisplayClass5_0 <>8__1;

			Toil IEnumerator<Toil>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <MakeNewToils>d__5(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				<>8__1 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
				//IL_00ce: Expected O, but got Unknown
				//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
				int num = <>1__state;
				JobDriver_UseTeleporter jobDriver_UseTeleporter = <>4__this;
				switch (num)
				{
				default:
					return false;
				case 0:
					<>1__state = -1;
					<>8__1 = new <>c__DisplayClass5_0();
					<>8__1.<>4__this = <>4__this;
					ToilFailConditions.FailOnIncapable<JobDriver_UseTeleporter>(jobDriver_UseTeleporter, PawnCapacityDefOf.Manipulation);
					ToilFailConditions.FailOnDespawnedNullOrForbidden<JobDriver_UseTeleporter>(jobDriver_UseTeleporter, (TargetIndex)1);
					<>2__current = Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false);
					<>1__state = 1;
					return true;
				case 1:
				{
					<>1__state = -1;
					Toil val = Toils_General.Wait(jobDriver_UseTeleporter.useDuration, (TargetIndex)0);
					ToilEffects.WithProgressBarToilDelay(val, (TargetIndex)1, false, -0.5f);
					ToilFailConditions.FailOnCannotTouch<Toil>(val, (TargetIndex)1, (PathEndMode)2);
					ToilFailConditions.FailOnDespawnedNullOrForbidden<Toil>(val, (TargetIndex)1);
					<>2__current = val;
					<>1__state = 2;
					return true;
				}
				case 2:
					<>1__state = -1;
					<>8__1.use = new Toil();
					<>8__1.use.initAction = delegate
					{
						<>c__DisplayClass5_1 obj = new <>c__DisplayClass5_1
						{
							CS$<>8__locals1 = <>8__1,
							actor = <>8__1.use.actor
						};
						obj.sendTeleporter = ((LocalTargetInfo)(ref obj.actor.CurJob.targetA)).Thing;
						((Action)delegate
						{
							//IL_004a: Unknown result type (might be due to invalid IL or missing references)
							if (obj.CS$<>8__locals1.<>4__this.destination != null)
							{
								ThingCompUtility.TryGetComp<Comp_Teleporter>(obj.sendTeleporter).TeleportEffect(obj.actor);
								((Entity)obj.actor).DeSpawn((DestroyMode)0);
								GenSpawn.Spawn((Thing)(object)obj.actor, obj.CS$<>8__locals1.<>4__this.destination.Position, obj.CS$<>8__locals1.<>4__this.destination.Map, (WipeMode)0);
								ThingCompUtility.TryGetComp<Comp_Teleporter>(obj.CS$<>8__locals1.<>4__this.destination).TeleportEffect(obj.actor);
							}
							else
							{
								Messages.Message("Teleport destination no longer valid.", MessageTypeDefOf.CautionInput, true);
							}
						})();
					};
					<>8__1.use.defaultCompleteMode = (ToilCompleteMode)1;
					<>2__current = <>8__1.use;
					<>1__state = 3;
					return true;
				case 3:
					<>1__state = -1;
					return false;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<Toil> IEnumerable<Toil>.GetEnumerator()
			{
				<MakeNewToils>d__5 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <MakeNewToils>d__5(0)
					{
						<>4__this = <>4__this
					};
				}
				return result;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Toil>)this).GetEnumerator();
			}
		}

		private int useDuration = -1;

		private Thing destination;

		public override void ExposeData()
		{
			((JobDriver)this).ExposeData();
			Scribe_Values.Look<int>(ref useDuration, "useDuration", 0, false);
			Scribe_References.Look<Thing>(ref destination, "destination", false);
		}

		public override void Notify_Starting()
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			((JobDriver)this).Notify_Starting();
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			Comp_Teleporter comp_Teleporter = ThingCompUtility.TryGetComp<Comp_Teleporter>(((LocalTargetInfo)(ref target)).Thing);
			useDuration = comp_Teleporter.Props.useDuration;
			destination = comp_Teleporter.target;
		}

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return true;
		}

		[IteratorStateMachine(typeof(<MakeNewToils>d__5))]
		public override IEnumerable<Toil> MakeNewToils()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <MakeNewToils>d__5(-2)
			{
				<>4__this = this
			};
		}
	}
	public class MapComp_Teleporter : MapComponent
	{
		public List<Thing> allMapTeleports = new List<Thing>();

		public override void ExposeData()
		{
			((MapComponent)this).ExposeData();
			Scribe_Collections.Look<Thing>(ref allMapTeleports, "allMapTeleports", (LookMode)3, Array.Empty<object>());
		}

		public MapComp_Teleporter(Map map)
			: base(map)
		{
		}

		public void RegisterTeleporter(Thing thing)
		{
			if (!allMapTeleports.Contains(thing))
			{
				allMapTeleports.Add(thing);
			}
		}

		public void UnregisterTeleporter(Thing thing)
		{
			if (allMapTeleports.Contains(thing))
			{
				allMapTeleports.Remove(thing);
			}
		}
	}
	public static class HealthUtil
	{
		[CompilerGenerated]
		private sealed class <GetFirstMatchingBodyparts>d__10 : IEnumerable<BodyPartRecord>, IEnumerable, IEnumerator<BodyPartRecord>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private BodyPartRecord <>2__current;

			private int <>l__initialThreadId;

			private Pawn pawn;

			public Pawn <>3__pawn;

			private BodyPartRecord startingPart;

			public BodyPartRecord <>3__startingPart;

			private HediffDef[] hediffExceptionDefs;

			public HediffDef[] <>3__hediffExceptionDefs;

			private HediffDef hediffDef;

			public HediffDef <>3__hediffDef;

			private List<Hediff> <hediffs>5__2;

			private List<BodyPartRecord> <currentSet>5__3;

			private List<BodyPartRecord> <nextSet>5__4;

			private List<BodyPartRecord>.Enumerator <>7__wrap4;

			private BodyPartRecord <part>5__6;

			private bool <matchingPart>5__7;

			BodyPartRecord IEnumerator<BodyPartRecord>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <GetFirstMatchingBodyparts>d__10(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<hediffs>5__2 = null;
				<currentSet>5__3 = null;
				<nextSet>5__4 = null;
				<>7__wrap4 = default(List<BodyPartRecord>.Enumerator);
				<part>5__6 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				try
				{
					int num = <>1__state;
					if (num != 0)
					{
						if (num != 1)
						{
							return false;
						}
						<>1__state = -3;
						goto IL_0147;
					}
					<>1__state = -1;
					<hediffs>5__2 = pawn.health.hediffSet.hediffs;
					<currentSet>5__3 = new List<BodyPartRecord>();
					<nextSet>5__4 = new List<BodyPartRecord>();
					<nextSet>5__4.Add(startingPart);
					goto IL_0061;
					IL_0061:
					<currentSet>5__3.AddRange(<nextSet>5__4);
					<nextSet>5__4.Clear();
					<>7__wrap4 = <currentSet>5__3.GetEnumerator();
					<>1__state = -3;
					goto IL_0194;
					IL_0147:
					if (!<matchingPart>5__7)
					{
						for (int i = 0; i < <part>5__6.parts.Count; i++)
						{
							<nextSet>5__4.Add(<part>5__6.parts[i]);
						}
					}
					<part>5__6 = null;
					goto IL_0194;
					IL_0194:
					if (<>7__wrap4.MoveNext())
					{
						<part>5__6 = <>7__wrap4.Current;
						<matchingPart>5__7 = false;
						for (int j = <hediffs>5__2.Count - 1; j >= 0; j--)
						{
							Hediff val = <hediffs>5__2[j];
							if (val.Part == <part>5__6)
							{
								if (hediffExceptionDefs.Contains(val.def))
								{
									<matchingPart>5__7 = true;
									break;
								}
								if (val.def == hediffDef)
								{
									<matchingPart>5__7 = true;
									<>2__current = <part>5__6;
									<>1__state = 1;
									return true;
								}
							}
							val = null;
						}
						goto IL_0147;
					}
					<>m__Finally1();
					<>7__wrap4 = default(List<BodyPartRecord>.Enumerator);
					<currentSet>5__3.Clear();
					if (<nextSet>5__4.Count <= 0)
					{
						return false;
					}
					goto IL_0061;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				((IDisposable)<>7__wrap4/*cast due to .constrained prefix*/).Dispose();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<BodyPartRecord> IEnumerable<BodyPartRecord>.GetEnumerator()
			{
				<GetFirstMatchingBodyparts>d__10 <GetFirstMatchingBodyparts>d__;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					<GetFirstMatchingBodyparts>d__ = this;
				}
				else
				{
					<GetFirstMatchingBodyparts>d__ = new <GetFirstMatchingBodyparts>d__10(0);
				}
				<GetFirstMatchingBodyparts>d__.pawn = <>3__pawn;
				<GetFirstMatchingBodyparts>d__.startingPart = <>3__startingPart;
				<GetFirstMatchingBodyparts>d__.hediffDef = <>3__hediffDef;
				<GetFirstMatchingBodyparts>d__.hediffExceptionDefs = <>3__hediffExceptionDefs;
				return <GetFirstMatchingBodyparts>d__;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<BodyPartRecord>)this).GetEnumerator();
			}
		}

		[CompilerGenerated]
		private sealed class <GetFirstMatchingBodyparts>d__11 : IEnumerable<BodyPartRecord>, IEnumerable, IEnumerator<BodyPartRecord>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private BodyPartRecord <>2__current;

			private int <>l__initialThreadId;

			private Pawn pawn;

			public Pawn <>3__pawn;

			private BodyPartRecord startingPart;

			public BodyPartRecord <>3__startingPart;

			private HediffDef[] hediffDefs;

			public HediffDef[] <>3__hediffDefs;

			private List<Hediff> <hediffs>5__2;

			private List<BodyPartRecord> <currentSet>5__3;

			private List<BodyPartRecord> <nextSet>5__4;

			private List<BodyPartRecord>.Enumerator <>7__wrap4;

			private BodyPartRecord <part>5__6;

			private bool <matchingPart>5__7;

			BodyPartRecord IEnumerator<BodyPartRecord>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <GetFirstMatchingBodyparts>d__11(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<hediffs>5__2 = null;
				<currentSet>5__3 = null;
				<nextSet>5__4 = null;
				<>7__wrap4 = default(List<BodyPartRecord>.Enumerator);
				<part>5__6 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				try
				{
					int num = <>1__state;
					if (num != 0)
					{
						if (num != 1)
						{
							return false;
						}
						<>1__state = -3;
						goto IL_012f;
					}
					<>1__state = -1;
					<hediffs>5__2 = pawn.health.hediffSet.hediffs;
					<currentSet>5__3 = new List<BodyPartRecord>();
					<nextSet>5__4 = new List<BodyPartRecord>();
					<nextSet>5__4.Add(startingPart);
					goto IL_0061;
					IL_0061:
					<currentSet>5__3.AddRange(<nextSet>5__4);
					<nextSet>5__4.Clear();
					<>7__wrap4 = <currentSet>5__3.GetEnumerator();
					<>1__state = -3;
					goto IL_017f;
					IL_012f:
					if (!<matchingPart>5__7)
					{
						for (int i = 0; i < <part>5__6.parts.Count; i++)
						{
							<nextSet>5__4.Add(<part>5__6.parts[i]);
						}
					}
					<part>5__6 = null;
					goto IL_017f;
					IL_017f:
					if (<>7__wrap4.MoveNext())
					{
						<part>5__6 = <>7__wrap4.Current;
						<matchingPart>5__7 = false;
						for (int j = <hediffs>5__2.Count - 1; j >= 0; j--)
						{
							Hediff val = <hediffs>5__2[j];
							if (val.Part == <part>5__6 && hediffDefs.Contains(val.def))
							{
								<matchingPart>5__7 = true;
								<>2__current = <part>5__6;
								<>1__state = 1;
								return true;
							}
							val = null;
						}
						goto IL_012f;
					}
					<>m__Finally1();
					<>7__wrap4 = default(List<BodyPartRecord>.Enumerator);
					<currentSet>5__3.Clear();
					if (<nextSet>5__4.Count <= 0)
					{
						return false;
					}
					goto IL_0061;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				((IDisposable)<>7__wrap4/*cast due to .constrained prefix*/).Dispose();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<BodyPartRecord> IEnumerable<BodyPartRecord>.GetEnumerator()
			{
				<GetFirstMatchingBodyparts>d__11 <GetFirstMatchingBodyparts>d__;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					<GetFirstMatchingBodyparts>d__ = this;
				}
				else
				{
					<GetFirstMatchingBodyparts>d__ = new <GetFirstMatchingBodyparts>d__11(0);
				}
				<GetFirstMatchingBodyparts>d__.pawn = <>3__pawn;
				<GetFirstMatchingBodyparts>d__.startingPart = <>3__startingPart;
				<GetFirstMatchingBodyparts>d__.hediffDefs = <>3__hediffDefs;
				return <GetFirstMatchingBodyparts>d__;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<BodyPartRecord>)this).GetEnumerator();
			}
		}

		[CompilerGenerated]
		private sealed class <GetFirstMatchingBodyparts>d__7 : IEnumerable<BodyPartRecord>, IEnumerable, IEnumerator<BodyPartRecord>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private BodyPartRecord <>2__current;

			private int <>l__initialThreadId;

			private Pawn pawn;

			public Pawn <>3__pawn;

			private BodyPartRecord startingPart;

			public BodyPartRecord <>3__startingPart;

			private HediffDef hediffDef;

			public HediffDef <>3__hediffDef;

			private List<Hediff> <hediffs>5__2;

			private List<BodyPartRecord> <currentSet>5__3;

			private List<BodyPartRecord> <nextSet>5__4;

			private List<BodyPartRecord>.Enumerator <>7__wrap4;

			private BodyPartRecord <part>5__6;

			private bool <matchingPart>5__7;

			private int <i>5__8;

			BodyPartRecord IEnumerator<BodyPartRecord>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <GetFirstMatchingBodyparts>d__7(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<hediffs>5__2 = null;
				<currentSet>5__3 = null;
				<nextSet>5__4 = null;
				<>7__wrap4 = default(List<BodyPartRecord>.Enumerator);
				<part>5__6 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				try
				{
					int num = <>1__state;
					if (num != 0)
					{
						if (num != 1)
						{
							return false;
						}
						<>1__state = -3;
						goto IL_011f;
					}
					<>1__state = -1;
					<hediffs>5__2 = pawn.health.hediffSet.hediffs;
					<currentSet>5__3 = new List<BodyPartRecord>();
					<nextSet>5__4 = new List<BodyPartRecord>();
					<nextSet>5__4.Add(startingPart);
					goto IL_0061;
					IL_0187:
					if (<>7__wrap4.MoveNext())
					{
						<part>5__6 = <>7__wrap4.Current;
						<matchingPart>5__7 = false;
						<i>5__8 = <hediffs>5__2.Count - 1;
						goto IL_0131;
					}
					<>m__Finally1();
					<>7__wrap4 = default(List<BodyPartRecord>.Enumerator);
					<currentSet>5__3.Clear();
					if (<nextSet>5__4.Count <= 0)
					{
						return false;
					}
					goto IL_0061;
					IL_0131:
					Hediff val;
					if (<i>5__8 >= 0)
					{
						val = <hediffs>5__2[<i>5__8];
						if (val.Part == <part>5__6 && val.def == hediffDef)
						{
							<matchingPart>5__7 = true;
							<>2__current = <part>5__6;
							<>1__state = 1;
							return true;
						}
						goto IL_011f;
					}
					if (!<matchingPart>5__7)
					{
						for (int i = 0; i < <part>5__6.parts.Count; i++)
						{
							<nextSet>5__4.Add(<part>5__6.parts[i]);
						}
					}
					<part>5__6 = null;
					goto IL_0187;
					IL_0061:
					<currentSet>5__3.AddRange(<nextSet>5__4);
					<nextSet>5__4.Clear();
					<>7__wrap4 = <currentSet>5__3.GetEnumerator();
					<>1__state = -3;
					goto IL_0187;
					IL_011f:
					val = null;
					<i>5__8--;
					goto IL_0131;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				((IDisposable)<>7__wrap4/*cast due to .constrained prefix*/).Dispose();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<BodyPartRecord> IEnumerable<BodyPartRecord>.GetEnumerator()
			{
				<GetFirstMatchingBodyparts>d__7 <GetFirstMatchingBodyparts>d__;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					<GetFirstMatchingBodyparts>d__ = this;
				}
				else
				{
					<GetFirstMatchingBodyparts>d__ = new <GetFirstMatchingBodyparts>d__7(0);
				}
				<GetFirstMatchingBodyparts>d__.pawn = <>3__pawn;
				<GetFirstMatchingBodyparts>d__.startingPart = <>3__startingPart;
				<GetFirstMatchingBodyparts>d__.hediffDef = <>3__hediffDef;
				return <GetFirstMatchingBodyparts>d__;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<BodyPartRecord>)this).GetEnumerator();
			}
		}

		[CompilerGenerated]
		private sealed class <GetFirstMatchingBodyparts>d__8 : IEnumerable<BodyPartRecord>, IEnumerable, IEnumerator<BodyPartRecord>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private BodyPartRecord <>2__current;

			private int <>l__initialThreadId;

			private Pawn pawn;

			public Pawn <>3__pawn;

			private BodyPartRecord startingPart;

			public BodyPartRecord <>3__startingPart;

			private HediffDef hediffExceptionDef;

			public HediffDef <>3__hediffExceptionDef;

			private HediffDef hediffDef;

			public HediffDef <>3__hediffDef;

			private List<Hediff> <hediffs>5__2;

			private List<BodyPartRecord> <currentSet>5__3;

			private List<BodyPartRecord> <nextSet>5__4;

			private List<BodyPartRecord>.Enumerator <>7__wrap4;

			private BodyPartRecord <part>5__6;

			private bool <matchingPart>5__7;

			BodyPartRecord IEnumerator<BodyPartRecord>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <GetFirstMatchingBodyparts>d__8(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<hediffs>5__2 = null;
				<currentSet>5__3 = null;
				<nextSet>5__4 = null;
				<>7__wrap4 = default(List<BodyPartRecord>.Enumerator);
				<part>5__6 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				try
				{
					int num = <>1__state;
					if (num != 0)
					{
						if (num != 1)
						{
							return false;
						}
						<>1__state = -3;
						goto IL_013f;
					}
					<>1__state = -1;
					<hediffs>5__2 = pawn.health.hediffSet.hediffs;
					<currentSet>5__3 = new List<BodyPartRecord>();
					<nextSet>5__4 = new List<BodyPartRecord>();
					<nextSet>5__4.Add(startingPart);
					goto IL_0061;
					IL_0061:
					<currentSet>5__3.AddRange(<nextSet>5__4);
					<nextSet>5__4.Clear();
					<>7__wrap4 = <currentSet>5__3.GetEnumerator();
					<>1__state = -3;
					goto IL_018c;
					IL_013f:
					if (!<matchingPart>5__7)
					{
						for (int i = 0; i < <part>5__6.parts.Count; i++)
						{
							<nextSet>5__4.Add(<part>5__6.parts[i]);
						}
					}
					<part>5__6 = null;
					goto IL_018c;
					IL_018c:
					if (<>7__wrap4.MoveNext())
					{
						<part>5__6 = <>7__wrap4.Current;
						<matchingPart>5__7 = false;
						for (int j = <hediffs>5__2.Count - 1; j >= 0; j--)
						{
							Hediff val = <hediffs>5__2[j];
							if (val.Part == <part>5__6)
							{
								if (val.def == hediffExceptionDef)
								{
									<matchingPart>5__7 = true;
									break;
								}
								if (val.def == hediffDef)
								{
									<matchingPart>5__7 = true;
									<>2__current = <part>5__6;
									<>1__state = 1;
									return true;
								}
							}
							val = null;
						}
						goto IL_013f;
					}
					<>m__Finally1();
					<>7__wrap4 = default(List<BodyPartRecord>.Enumerator);
					<currentSet>5__3.Clear();
					if (<nextSet>5__4.Count <= 0)
					{
						return false;
					}
					goto IL_0061;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				((IDisposable)<>7__wrap4/*cast due to .constrained prefix*/).Dispose();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<BodyPartRecord> IEnumerable<BodyPartRecord>.GetEnumerator()
			{
				<GetFirstMatchingBodyparts>d__8 <GetFirstMatchingBodyparts>d__;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					<GetFirstMatchingBodyparts>d__ = this;
				}
				else
				{
					<GetFirstMatchingBodyparts>d__ = new <GetFirstMatchingBodyparts>d__8(0);
				}
				<GetFirstMatchingBodyparts>d__.pawn = <>3__pawn;
				<GetFirstMatchingBodyparts>d__.startingPart = <>3__startingPart;
				<GetFirstMatchingBodyparts>d__.hediffDef = <>3__hediffDef;
				<GetFirstMatchingBodyparts>d__.hediffExceptionDef = <>3__hediffExceptionDef;
				return <GetFirstMatchingBodyparts>d__;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<BodyPartRecord>)this).GetEnumerator();
			}
		}

		[CompilerGenerated]
		private sealed class <GetFirstMatchingBodyparts>d__9 : IEnumerable<BodyPartRecord>, IEnumerable, IEnumerator<BodyPartRecord>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private BodyPartRecord <>2__current;

			private int <>l__initialThreadId;

			private Pawn pawn;

			public Pawn <>3__pawn;

			private BodyPartRecord startingPart;

			public BodyPartRecord <>3__startingPart;

			private HediffDef hediffExceptionDef;

			public HediffDef <>3__hediffExceptionDef;

			private Predicate<Hediff> extraExceptionPredicate;

			public Predicate<Hediff> <>3__extraExceptionPredicate;

			private HediffDef hediffDef;

			public HediffDef <>3__hediffDef;

			private List<Hediff> <hediffs>5__2;

			private List<BodyPartRecord> <currentSet>5__3;

			private List<BodyPartRecord> <nextSet>5__4;

			private List<BodyPartRecord>.Enumerator <>7__wrap4;

			private BodyPartRecord <part>5__6;

			private bool <matchingPart>5__7;

			BodyPartRecord IEnumerator<BodyPartRecord>.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			object IEnumerator.Current
			{
				[DebuggerHidden]
				get
				{
					return <>2__current;
				}
			}

			[DebuggerHidden]
			public <GetFirstMatchingBodyparts>d__9(int <>1__state)
			{
				this.<>1__state = <>1__state;
				<>l__initialThreadId = Environment.CurrentManagedThreadId;
			}

			[DebuggerHidden]
			void IDisposable.Dispose()
			{
				int num = <>1__state;
				if (num == -3 || num == 1)
				{
					try
					{
					}
					finally
					{
						<>m__Finally1();
					}
				}
				<hediffs>5__2 = null;
				<currentSet>5__3 = null;
				<nextSet>5__4 = null;
				<>7__wrap4 = default(List<BodyPartRecord>.Enumerator);
				<part>5__6 = null;
				<>1__state = -2;
			}

			private bool MoveNext()
			{
				try
				{
					int num = <>1__state;
					if (num != 0)
					{
						if (num != 1)
						{
							return false;
						}
						<>1__state = -3;
						goto IL_0154;
					}
					<>1__state = -1;
					<hediffs>5__2 = pawn.health.hediffSet.hediffs;
					<currentSet>5__3 = new List<BodyPartRecord>();
					<nextSet>5__4 = new List<BodyPartRecord>();
					<nextSet>5__4.Add(startingPart);
					goto IL_0061;
					IL_0061:
					<currentSet>5__3.AddRange(<nextSet>5__4);
					<nextSet>5__4.Clear();
					<>7__wrap4 = <currentSet>5__3.GetEnumerator();
					<>1__state = -3;
					goto IL_01a1;
					IL_0154:
					if (!<matchingPart>5__7)
					{
						for (int i = 0; i < <part>5__6.parts.Count; i++)
						{
							<nextSet>5__4.Add(<part>5__6.parts[i]);
						}
					}
					<part>5__6 = null;
					goto IL_01a1;
					IL_01a1:
					if (<>7__wrap4.MoveNext())
					{
						<part>5__6 = <>7__wrap4.Current;
						<matchingPart>5__7 = false;
						for (int j = <hediffs>5__2.Count - 1; j >= 0; j--)
						{
							Hediff val = <hediffs>5__2[j];
							if (val.Part == <part>5__6)
							{
								if (val.def == hediffExceptionDef || extraExceptionPredicate(val))
								{
									<matchingPart>5__7 = true;
									break;
								}
								if (val.def == hediffDef)
								{
									<matchingPart>5__7 = true;
									<>2__current = <part>5__6;
									<>1__state = 1;
									return true;
								}
							}
							val = null;
						}
						goto IL_0154;
					}
					<>m__Finally1();
					<>7__wrap4 = default(List<BodyPartRecord>.Enumerator);
					<currentSet>5__3.Clear();
					if (<nextSet>5__4.Count <= 0)
					{
						return false;
					}
					goto IL_0061;
				}
				catch
				{
					//try-fault
					((IDisposable)this).Dispose();
					throw;
				}
			}

			bool IEnumerator.MoveNext()
			{
				//ILSpy generated this explicit interface implementation from .override directive in MoveNext
				return this.MoveNext();
			}

			private void <>m__Finally1()
			{
				<>1__state = -1;
				((IDisposable)<>7__wrap4/*cast due to .constrained prefix*/).Dispose();
			}

			[DebuggerHidden]
			void IEnumerator.Reset()
			{
				throw new NotSupportedException();
			}

			[DebuggerHidden]
			IEnumerator<BodyPartRecord> IEnumerable<BodyPartRecord>.GetEnumerator()
			{
				<GetFirstMatchingBodyparts>d__9 <GetFirstMatchingBodyparts>d__;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					<GetFirstMatchingBodyparts>d__ = this;
				}
				else
				{
					<GetFirstMatchingBodyparts>d__ = new <GetFirstMatchingBodyparts>d__9(0);
				}
				<GetFirstMatchingBodyparts>d__.pawn = <>3__pawn;
				<GetFirstMatchingBodyparts>d__.startingPart = <>3__startingPart;
				<GetFirstMatchingBodyparts>d__.hediffDef = <>3__hediffDef;
				<GetFirstMatchingBodyparts>d__.hediffExceptionDef = <>3__hediffExceptionDef;
				<GetFirstMatchingBodyparts>d__.extraExceptionPredicate = <>3__extraExceptionPredicate;
				return <GetFirstMatchingBodyparts>d__;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<BodyPartRecord>)this).GetEnumerator();
			}
		}

		public static void SetNextTick(int ticks, int setTicks)
		{
			ticks = Current.Game.tickManager.TicksGame + setTicks;
		}

		public static void TrySealWounds(Pawn pawn, List<HediffDef> ignoredHediffs)
		{
			IEnumerable<Hediff> enumerable = pawn.health.hediffSet.hediffs.Where((Hediff hd) => hd.TendableNow(false) && !ignoredHediffs.Contains(hd.def));
			if (enumerable == null)
			{
				return;
			}
			foreach (Hediff item in enumerable)
			{
				if (item == null)
				{
					continue;
				}
				HediffWithComps val = (HediffWithComps)(object)((item is HediffWithComps) ? item : null);
				if (val != null)
				{
					HediffComp_TendDuration val2 = HediffUtility.TryGetComp<HediffComp_TendDuration>((Hediff)(object)val);
					if (val2 != null)
					{
						val2.tendQuality = 2f;
						val2.tendTicksLeft = Find.TickManager.TicksGame;
					}
					pawn.health.Notify_HediffChanged(item);
				}
				Hediff_MissingPart val3 = (Hediff_MissingPart)(object)((item is Hediff_MissingPart) ? item : null);
				if (val3 != null)
				{
					((Hediff)val3).Tended(2f, 2f, 0);
					pawn.health.Notify_HediffChanged(item);
				}
			}
		}

		public static bool CanSealWounds(Pawn pawn)
		{
			IEnumerable<Hediff> enumerable = pawn.health.hediffSet.hediffs.Where((Hediff hd) => hd.TendableNow(false));
			if (enumerable != null)
			{
				List<Hediff> list = enumerable.ToList();
				for (int i = 0; i < list.Count; i++)
				{
					if (list[i] != null && !list[i].def.makesSickThought && !list[i].def.chronic)
					{
						if (list[i].def.hediffClass == typeof(Hediff_MissingPart))
						{
							return false;
						}
						if (!HediffUtility.IsPermanent(list[i]) && list[i].def.everCurableByItem)
						{
							return false;
						}
					}
				}
			}
			return true;
		}

		public static void TrySealWounds(Pawn patient)
		{
			TrySealWounds(patient, new List<HediffDef>());
		}

		public static void TryCureInfections(Pawn pawn, List<HediffDef> hediffList, List<HediffDef> explicitRemovals)
		{
			IEnumerable<Hediff> enumerable = pawn.health.hediffSet.hediffs.Where((Hediff hd) => hd.def.makesSickThought || explicitRemovals.Contains(hd.def));
			if (enumerable == null)
			{
				return;
			}
			foreach (Hediff item in enumerable.ToList())
			{
				if (item != null)
				{
					HediffWithComps hediffWithComps = (HediffWithComps)(object)((item is HediffWithComps) ? item : null);
					if (hediffWithComps != null && !GenCollection.Any<HediffDef>(hediffList, (Predicate<HediffDef>)((HediffDef h) => ((Hediff)hediffWithComps).def == h)))
					{
						pawn.health.RemoveHediff(item);
						pawn.health.hediffSet.DirtyCache();
					}
				}
			}
		}

		public static void TryRegrowBodyparts(Pawn pawn, HediffDef protoBodyPart)
		{
			if (protoBodyPart != null)
			{
				foreach (BodyPartRecord part in pawn.GetFirstMatchingBodyparts(pawn.RaceProps.body.corePart, HediffDefOf.MissingBodyPart, protoBodyPart, (Hediff hediff) => hediff is Hediff_AddedPart))
				{
					Hediff val = pawn.health.hediffSet.hediffs.First((Hediff hediff) => hediff.Part == part && hediff.def == HediffDefOf.MissingBodyPart);
					if (val != null)
					{
						pawn.health.RemoveHediff(val);
						pawn.health.AddHediff(protoBodyPart, part, (DamageInfo?)null, (DamageResult)null);
						pawn.health.hediffSet.DirtyCache();
					}
				}
				return;
			}
			foreach (BodyPartRecord part2 in pawn.GetFirstMatchingBodyparts(pawn.RaceProps.body.corePart, HediffDefOf.MissingBodyPart, protoBodyPart, (Hediff hediff) => hediff is Hediff_AddedPart))
			{
				Hediff val2 = pawn.health.hediffSet.hediffs.First((Hediff hediff) => hediff.Part == part2 && hediff.def == HediffDefOf.MissingBodyPart);
				if (val2 != null)
				{
					pawn.health.RemoveHediff(val2);
					pawn.health.AddHediff(protoBodyPart, part2, (DamageInfo?)null, (DamageResult)null);
					pawn.health.hediffSet.DirtyCache();
				}
			}
		}

		public static void TendAdditional(Pawn doctor, Pawn patient)
		{
			//IL_01a0: Unknown result type (might be due to invalid IL or missing references)
			if (doctor != null && ((Thing)doctor).Faction == Faction.OfPlayer && ((Thing)patient).Faction != ((Thing)doctor).Faction && !patient.IsPrisoner && ((Thing)patient).Faction != null)
			{
				Pawn_MindState mindState = patient.mindState;
				mindState.timesGuestTendedToByPlayer++;
			}
			if (doctor != null && ((Thing)doctor).Faction == Faction.OfPlayer && ((Thing)patient).Faction != ((Thing)doctor).Faction && !patient.IsPrisoner && ((Thing)patient).Faction != null)
			{
				Pawn_MindState mindState2 = patient.mindState;
				mindState2.timesGuestTendedToByPlayer++;
			}
			if (doctor != null && doctor.RaceProps.Humanlike && patient.RaceProps.Animal && patient.RaceProps.playerCanChangeMaster && RelationsUtility.TryDevelopBondRelation(doctor, patient, 0.004f) && ((Thing)doctor).Faction != null && ((Thing)doctor).Faction != ((Thing)patient).Faction)
			{
				InteractionWorker_RecruitAttempt.DoRecruit(doctor, patient, false);
			}
			patient.records.Increment(RecordDefOf.TimesTendedTo);
			if (doctor != null)
			{
				doctor.records.Increment(RecordDefOf.TimesTendedOther);
			}
			if (doctor == patient && !doctor.Dead)
			{
				doctor.mindState.Notify_SelfTended();
			}
			if (ModsConfig.IdeologyActive && doctor != null && doctor.Ideo != null)
			{
				Precept_Role role = doctor.Ideo.GetRole(doctor);
				if (role != null && ((Precept)role).def.roleEffects != null)
				{
					foreach (RoleEffect roleEffect in ((Precept)role).def.roleEffects)
					{
						roleEffect.Notify_Tended(doctor, patient);
					}
				}
			}
			if (doctor != null && ((Thing)doctor).Faction == Faction.OfPlayer && doctor != patient)
			{
				QuestUtility.SendQuestTargetSignals(((Thing)patient).questTags, "PlayerTended", NamedArgumentUtility.Named((object)patient, "SUBJECT"));
			}
		}

		[IteratorStateMachine(typeof(<GetFirstMatchingBodyparts>d__7))]
		public static IEnumerable<BodyPartRecord> GetFirstMatchingBodyparts(this Pawn pawn, BodyPartRecord startingPart, HediffDef hediffDef)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <GetFirstMatchingBodyparts>d__7(-2)
			{
				<>3__pawn = pawn,
				<>3__startingPart = startingPart,
				<>3__hediffDef = hediffDef
			};
		}

		[IteratorStateMachine(typeof(<GetFirstMatchingBodyparts>d__8))]
		public static IEnumerable<BodyPartRecord> GetFirstMatchingBodyparts(this Pawn pawn, BodyPartRecord startingPart, HediffDef hediffDef, HediffDef hediffExceptionDef)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <GetFirstMatchingBodyparts>d__8(-2)
			{
				<>3__pawn = pawn,
				<>3__startingPart = startingPart,
				<>3__hediffDef = hediffDef,
				<>3__hediffExceptionDef = hediffExceptionDef
			};
		}

		[IteratorStateMachine(typeof(<GetFirstMatchingBodyparts>d__9))]
		public static IEnumerable<BodyPartRecord> GetFirstMatchingBodyparts(this Pawn pawn, BodyPartRecord startingPart, HediffDef hediffDef, HediffDef hediffExceptionDef, Predicate<Hediff> extraExceptionPredicate)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <GetFirstMatchingBodyparts>d__9(-2)
			{
				<>3__pawn = pawn,
				<>3__startingPart = startingPart,
				<>3__hediffDef = hediffDef,
				<>3__hediffExceptionDef = hediffExceptionDef,
				<>3__extraExceptionPredicate = extraExceptionPredicate
			};
		}

		[IteratorStateMachine(typeof(<GetFirstMatchingBodyparts>d__10))]
		public static IEnumerable<BodyPartRecord> GetFirstMatchingBodyparts(this Pawn pawn, BodyPartRecord startingPart, HediffDef hediffDef, HediffDef[] hediffExceptionDefs)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <GetFirstMatchingBodyparts>d__10(-2)
			{
				<>3__pawn = pawn,
				<>3__startingPart = startingPart,
				<>3__hediffDef = hediffDef,
				<>3__hediffExceptionDefs = hediffExceptionDefs
			};
		}

		[IteratorStateMachine(typeof(<GetFirstMatchingBodyparts>d__11))]
		public static IEnumerable<BodyPartRecord> GetFirstMatchingBodyparts(this Pawn pawn, BodyPartRecord startingPart, HediffDef[] hediffDefs)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <GetFirstMatchingBodyparts>d__11(-2)
			{
				<>3__pawn = pawn,
				<>3__startingPart = startingPart,
				<>3__hediffDefs = hediffDefs
			};
		}

		public static void ReplaceHediffFromBodypart(this Pawn pawn, BodyPartRecord startingPart, HediffDef hediffDef, HediffDef replaceWithDef)
		{
			List<Hediff> hediffs = pawn.health.hediffSet.hediffs;
			List<BodyPartRecord> list = new List<BodyPartRecord>();
			List<BodyPartRecord> list2 = new List<BodyPartRecord>();
			list2.Add(startingPart);
			do
			{
				list.AddRange(list2);
				list2.Clear();
				foreach (BodyPartRecord item2 in list)
				{
					for (int num = hediffs.Count - 1; num >= 0; num--)
					{
						Hediff val = hediffs[num];
						if (val.Part == item2 && val.def == hediffDef)
						{
							Hediff val2 = hediffs[num];
							hediffs.RemoveAt(num);
							val2.PostRemoved();
							Hediff item = HediffMaker.MakeHediff(replaceWithDef, pawn, item2);
							hediffs.Insert(num, item);
						}
					}
					for (int i = 0; i < item2.parts.Count; i++)
					{
						list2.Add(item2.parts[i]);
					}
				}
				list.Clear();
			}
			while (list2.Count > 0);
		}
	}
	public class PatchOperation_FindModByID : PatchOperation
	{
		public List<string> mods;

		public bool requireAll;

		public PatchOperation match;

		public PatchOperation nomatch;

		public override bool ApplyWorker(XmlDocument xml)
		{
			bool flag = false;
			if (!requireAll && ModLister.AnyFromListActive(mods))
			{
				flag = true;
			}
			else
			{
				int num = 0;
				foreach (string mod in mods)
				{
					if (ModLister.GetActiveModWithIdentifier(mod, false) != null)
					{
						num++;
					}
				}
				if (num >= mods.Count)
				{
					flag = true;
				}
			}
			if (flag)
			{
				if (match != null)
				{
					return match.Apply(xml);
				}
			}
			else if (nomatch != null)
			{
				return nomatch.Apply(xml);
			}
			return true;
		}
	}
	[HarmonyPatch(typeof(MainMenuDrawer), "MainMenuOnGUI")]
	public static class Patch_MainMenuDrawer_MainMenuOnGUI
	{
		[HarmonyPostfix]
		public static void Postfix()
		{
			UpdateUtil.DoUpdateListing();
		}
	}
	public class UpdateDef : Def
	{
		public string date = "0000/00/00";

		public string banner;

		public string content;

		public List<UpdateItem> contentList = new List<UpdateItem>();

		public string linkUrl;

		public List<UpdateLink> links;

		public bool important;
	}
	public class UpdateItem
	{
		public string header;

		public string image;

		public string text;
	}
	public class UpdateLink
	{
		public string linkLabel;

		public string linkUrl;

		public string linkTex;
	}
	[DefOf]
	public static class TabulaRasaDefOf
	{
		public static JobDef TabulaRasa_TakeFromProducer;

		public static JobDef TabulaRasa_UseTeleporter;

		public static JobDef TabulaRasa_UseRecall;

		public static JobDef TabulaRasa_UseEffectApplyHediff;

		public static JobDef TabulaRasa_GatherSlotItem;

		public static HediffDef TabulaRasa_RemovableHediff;

		public static SoundDef EnergyShield_Broken;

		static TabulaRasaDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(TabulaRasaDefOf));
		}
	}
	public static class UpdateUtil
	{
		public static UpdateDef selectedUpdate;

		public static Vector2 updateScrollPosition;

		public static float updateViewRectHeight;

		public static List<UpdateDef> allUpdatesCached;

		public static List<UpdateDef> AllUpdates
		{
			get
			{
				if (GenList.NullOrEmpty<UpdateDef>((IList<UpdateDef>)allUpdatesCached))
				{
					allUpdatesCached = new List<UpdateDef>();
					foreach (UpdateDef item in DefDatabase<UpdateDef>.AllDefsListForReading)
					{
						if (item.InPastThreeMonths() || TabulaRasaMod.settings.showOldUpdates)
						{
							allUpdatesCached.Add(item);
						}
					}
					GenCollection.SortBy<UpdateDef, string>(allUpdatesCached, (Func<UpdateDef, string>)((UpdateDef x) => x.date));
					allUpdatesCached.Reverse();
					if (!GenList.NullOrEmpty<string>((IList<string>)TabulaRasaMod.settings.markedAsSeen))
					{
						int i;
						for (i = 0; i < TabulaRasaMod.settings.markedAsSeen.Count(); i++)
						{
							if (GenCollection.Any<UpdateDef>(allUpdatesCached, (Predicate<UpdateDef>)((UpdateDef x) => ((Def)x).defName == TabulaRasaMod.settings.markedAsSeen[i])))
							{
								allUpdatesCached.Remove(DefDatabase<UpdateDef>.GetNamed(TabulaRasaMod.settings.markedAsSeen[i], true));
							}
						}
					}
					if (GenCollection.Any<UpdateDef>(allUpdatesCached, (Predicate<UpdateDef>)((UpdateDef u) => GenList.NullOrEmpty<UpdateItem>((IList<UpdateItem>)u.contentList))))
					{
						allUpdatesCached.RemoveAll((UpdateDef u) => GenList.NullOrEmpty<UpdateItem>((IList<UpdateItem>)u.contentList));
					}
				}
				return allUpdatesCached;
			}
		}

		public static bool InPastThreeMonths(this UpdateDef def)
		{
			return DateTime.ParseExact(def.date, "yyyy/M/d", null).AddMonths(3) > DateTime.Now;
		}

		public static void DoUpdateListing()
		{
			//IL_0052: Unknown result type (might be due to invalid IL or missing references)
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Unknown result type (might be due to invalid IL or missing references)
			//IL_0067: Unknown result type (might be due to invalid IL or missing references)
			//IL_006e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0075: Expected O, but got Unknown
			//IL_0077: Unknown result type (might be due to invalid IL or missing references)
			//IL_0080: Unknown result type (might be due to invalid IL or missing references)
			//IL_009b: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
			//IL_0103: Unknown result type (might be due to invalid IL or missing references)
			//IL_010a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0118: Unknown result type (might be due to invalid IL or missing references)
			if (UI.screenHeight >= 768 && UI.screenWidth >= 1366 && TabulaRasaMod.settings.modUpdates && !GenList.NullOrEmpty<UpdateDef>((IList<UpdateDef>)AllUpdates))
			{
				float num = 500f;
				float num2 = 300f;
				Rect val = new Rect(8f, (float)UI.screenHeight - (num + 120f), num2, num);
				Widgets.DrawWindowBackground(val);
				Rect val2 = GenUI.ContractedBy(val, 16f);
				float num3 = 0f;
				Listing_Standard val3 = new Listing_Standard();
				((Listing)val3).Begin(val2);
				val3.font = (GameFont)2;
				val3.Label("Mod Updates", -1f, (TipSignal?)null);
				num3 += Text.CalcHeight("Mod Updates", ((Rect)(ref val2)).width);
				val3.font = (GameFont)1;
				((Listing)val3).GapLine(12f);
				num3 += 12f;
				int num4 = Mathf.Min(6, AllUpdates.Count());
				Rect val4 = default(Rect);
				Rect val5 = default(Rect);
				for (int i = 0; i < num4; i++)
				{
					((Rect)(ref val4))..ctor(0f, num3, ((Rect)(ref val2)).width, 64f);
					((Rect)(ref val5))..ctor(val4);
					DoUpdateSelection(val4, AllUpdates[i], Mouse.IsOver(val5));
					num3 += 68f;
				}
				((Listing)val3).End();
				MainMenuDrawer.DoExpansionIcons();
				if (selectedUpdate != null)
				{
					DoSelectedUpdateInfo(selectedUpdate);
				}
			}
		}

		public static void RemoveSelection(string defName)
		{
			if (GenList.NullOrEmpty<string>((IList<string>)TabulaRasaMod.settings.markedAsSeen))
			{
				TabulaRasaMod.settings.markedAsSeen = new List<string>();
			}
			TabulaRasaMod.settings.markedAsSeen.Add(defName);
			((Mod)TabulaRasaMod.mod).WriteSettings();
			allUpdatesCached.Clear();
		}

		public static void DoUpdateSelection(Rect rect, UpdateDef info, bool highlight = false)
		{
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			//IL_0046: Unknown result type (might be due to invalid IL or missing references)
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Expected O, but got Unknown
			//IL_004e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0056: Unknown result type (might be due to invalid IL or missing references)
			//IL_0076: Unknown result type (might be due to invalid IL or missing references)
			//IL_007e: Unknown result type (might be due to invalid IL or missing references)
			//IL_00da: Unknown result type (might be due to invalid IL or missing references)
			if (info.important)
			{
				Widgets.DrawWindowBackgroundTutor(rect);
			}
			else
			{
				Widgets.DrawWindowBackground(rect);
				if (highlight || selectedUpdate == info)
				{
					GUI.DrawTexture(rect, (Texture)(object)TexUI.HighlightTex);
				}
			}
			if (Widgets.ButtonInvisible(rect, true))
			{
				selectedUpdate = info;
			}
			Rect val = GenUI.ContractedBy(rect, 8f);
			Listing_Standard val2 = new Listing_Standard();
			((Listing)val2).Begin(val);
			val2.font = (GameFont)2;
			val2.Label(((Def)info).modContentPack.Name, -1f, (TipSignal?)null);
			val2.font = (GameFont)1;
			string[] array = info.date.Split(new char[1] { '/' }, StringSplitOptions.RemoveEmptyEntries);
			string text = array[2] + "-" + array[1] + "-" + array[0];
			val2.Label(text, -1f, (TipSignal?)null);
			((Listing)val2).End();
		}

		public static void DoSelectedUpdateInfo(UpdateDef info)
		{
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			//IL_005e: Unknown result type (might be due to invalid IL or missing references)
			//IL_006c: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e0: Expected O, but got Unknown
			//IL_0103: Unknown result type (might be due to invalid IL or missing references)
			float num = 500f;
			float num2 = 500f;
			Rect val = new Rect(316f, (float)UI.screenHeight - (num + 120f), num2, num);
			Widgets.DrawWindowBackground(val);
			Rect val2 = GenUI.ContractedBy(val, 16f);
			((Rect)(ref val2)).y = ((Rect)(ref val2)).y + 12f;
			((Rect)(ref val2)).height = ((Rect)(ref val2)).height - 12f;
			if (CloseButtonFor(val))
			{
				selectedUpdate = null;
			}
			if (TrashButtonFor(val))
			{
				RemoveSelection(((Def)info).defName);
				selectedUpdate = null;
			}
			DoLinkIcons(val, info);
			bool flag = updateViewRectHeight > ((Rect)(ref val2)).height;
			Rect val3 = default(Rect);
			((Rect)(ref val3))..ctor(((Rect)(ref val2)).x, ((Rect)(ref val2)).y, ((Rect)(ref val2)).width - (flag ? 26f : 0f), updateViewRectHeight);
			Widgets.BeginScrollView(val2, ref updateScrollPosition, val3, true);
			Listing_Standard val4 = new Listing_Standard();
			Rect val5 = default(Rect);
			((Rect)(ref val5))..ctor(((Rect)(ref val3)).x, ((Rect)(ref val3)).y, ((Rect)(ref val3)).width, 999999f);
			((Listing)val4).Begin(val5);
			if (!GenText.NullOrEmpty(info.banner))
			{
				Texture2D val6 = ContentFinder<Texture2D>.Get(info.banner, false);
				if ((Object)(object)val6 != (Object)null)
				{
					val4.DoImage(val6);
					((Listing)val4).GapLine(12f);
				}
			}
			if (!GenText.NullOrEmpty(info.content))
			{
				DoLegacyUpdateContents(val4, info);
			}
			if (!GenList.NullOrEmpty<UpdateItem>((IList<UpdateItem>)info.contentList))
			{
				DoUpdateContents(val4, info);
			}
			updateViewRectHeight = ((Listing)val4).CurHeight;
			((Listing)val4).End();
			Widgets.EndScrollView();
		}

		public static void DoLinkIcons(Rect rect, UpdateDef info)
		{
			//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
			if (GenList.NullOrEmpty<UpdateLink>((IList<UpdateLink>)info.links))
			{
				return;
			}
			List<UpdateLink> list = info.links ?? new List<UpdateLink>();
			if (!GenText.NullOrEmpty(info.linkUrl))
			{
				list.Add(new UpdateLink
				{
					linkUrl = info.linkUrl
				});
			}
			for (int i = 0; i < list.Count; i++)
			{
				UpdateLink updateLink = list[i];
				if (!GenText.NullOrEmpty(updateLink.linkUrl))
				{
					Texture2D icon = (GenText.NullOrEmpty(updateLink.linkTex) ? TexTabulaRasa.Hyperlink : ContentFinder<Texture2D>.Get(updateLink.linkTex, false));
					if (DoLinkButton(new Rect(((Rect)(ref rect)).x + ((Rect)(ref rect)).width - 22f * (float)(3 + i), ((Rect)(ref rect)).y + 4f, 18f, 18f), icon, updateLink.linkLabel))
					{
						Application.OpenURL(updateLink.linkUrl);
					}
				}
			}
		}

		public static bool DoLinkButton(Rect rect, Texture2D icon, string tooltip = null)
		{
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0003: Unknown result type (might be due to invalid IL or missing references)
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			if (tooltip != null)
			{
				TooltipHandler.TipRegion(rect, TipSignal.op_Implicit(tooltip));
			}
			return Widgets.ButtonImage(rect, icon, true, (string)null);
		}

		public static void DoLegacyUpdateContents(Listing_Standard listing, UpdateDef info)
		{
			listing.Note(info.content, (GameFont)1);
		}

		public static void DoUpdateContents(Listing_Standard listing, UpdateDef info)
		{
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			foreach (UpdateItem content in info.contentList)
			{
				if (!GenText.NullOrEmpty(content.header))
				{
					listing.LabelBacked(content.header, Color.white, (GameFont)1);
				}
				if (!GenText.NullOrEmpty(content.text))
				{
					listing.TextContent(content.text, (GameFont)1);
				}
				if (!GenText.NullOrEmpty(content.image))
				{
					Texture2D val = ContentFinder<Texture2D>.Get(content.image, false);
					if ((Object)(object)val != (Object)null)
					{
						listing.DoImage(val);
					}
				}
			}
		}

		public static bool CloseButtonFor(Rect rect)
		{
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			return DoLinkButton(new Rect(((Rect)(ref rect)).x + ((Rect)(ref rect)).width - 18f - 4f, ((Rect)(ref rect)).y + 4f, 18f, 18f), TexButton.CloseXSmall, "Close");
		}

		public static bool TrashButtonFor(Rect rect)
		{
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			return DoLinkButton(new Rect(((Rect)(ref rect)).x + ((Rect)(ref rect)).width - 36f - 8f, ((Rect)(ref rect)).y + 4f, 18f, 18f), TexTabulaRasa.UpdateMarkAsRead, "Mark as Read");
		}
	}
	public static class LogUtil
	{
		public static readonly Color msgColor = new Color(0.266f, 0.58f, 0.89f);

		public static readonly Color wrnColor = new Color(0.796f, 0.325f, 0.878f);

		public static readonly Color errColor = new Color(0.901f, 0.192f, 0.152f);

		public static readonly Color dbgColor = new Color(0.411f, 0.749f, 0.666f);

		public static readonly string msgPrefix = ":: Tabula Rasa ::";

		public static readonly bool debugEnabled = false;

		public static void Message(string msg)
		{
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Expected O, but got Unknown
			if (!Log.PreventLogging)
			{
				Debug.Log((object)msg);
				Log.messageQueue.Enqueue(new LogMessage((LogMessageType)0, ColoredText.Colorize(msgPrefix, msgColor) + " " + msg, StackTraceUtility.ExtractStackTrace()));
				Log.PostMessage();
			}
		}

		public static void Warning(string msg)
		{
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Expected O, but got Unknown
			if (!Log.PreventLogging)
			{
				Debug.Log((object)msg);
				Log.messageQueue.Enqueue(new LogMessage((LogMessageType)1, ColoredText.Colorize(msgPrefix, wrnColor) + " " + msg, StackTraceUtility.ExtractStackTrace()));
				Log.PostMessage();
			}
		}

		public static void Error(string msg)
		{
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Expected O, but got Unknown
			if (!Log.PreventLogging)
			{
				Debug.Log((object)msg);
				Log.messageQueue.Enqueue(new LogMessage((LogMessageType)2, ColoredText.Colorize(msgPrefix, errColor) + " " + msg, StackTraceUtility.ExtractStackTrace()));
				Log.PostMessage();
			}
		}

		public static void Debug(string msg)
		{
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0044: Expected O, but got Unknown
			if (!Log.PreventLogging && debugEnabled)
			{
				Debug.Log((object)msg);
				Log.messageQueue.Enqueue(new LogMessage((LogMessageType)1, ColoredText.Colorize(msgPrefix, dbgColor) + " Debug :: " + msg, StackTraceUtility.ExtractStackTrace()));
				Log.PostMessage();
			}
		}
	}
	public class PatchOperation_SettingActive : PatchOperation
	{
		public List<string> settings;

		public PatchOperation active;

		public PatchOperation inactive;

		public override bool ApplyWorker(XmlDocument xml)
		{
			bool flag = false;
			_ = ((Mod)TabulaRasaMod.mod).Content;
			for (int i = 0; i < settings.Count(); i++)
			{
				if (!TabulaRasaMod.settings.IsValidSetting(settings[i]))
				{
					LogUtil.Error("Configuration error in patch, { settings[i]} is not an existing setting in this mod. This can only check existing boolean settings.");
				}
				if (TabulaRasaMod.settings.GetEnabledSettings.Contains(settings[i]))
				{
					flag = true;
					break;
				}
			}
			if (flag)
			{
				if (active != null)
				{
					return active.Apply(xml);
				}
			}
			else if (inactive != null)
			{
				return inactive.Apply(xml);
			}
			return true;
		}
	}
	public class TabulaRasaMod : Mod
	{
		public static TabulaRasaMod mod;

		public static TabulaRasaSettings settings;

		public TabulaRasaSettingsPage currentPage;

		public Vector2 optionsScrollPosition;

		public float optionsViewRectHeight;

		internal static string VersionDir => Path.Combine(((Mod)mod).Content.ModMetaData.RootDir.FullName, "Version.txt");

		public static string CurrentVersion { get; private set; }

		public TabulaRasaMod(ModContentPack content)
			: base(content)
		{
			//IL_0087: Unknown result type (might be due to invalid IL or missing references)
			mod = this;
			settings = ((Mod)this).GetSettings<TabulaRasaSettings>();
			Version version = Assembly.GetExecutingAssembly().GetName().Version;
			CurrentVersion = $"{version.Major}.{version.Minor}.{version.Build}";
			LogUtil.Message(CurrentVersion + " ::");
			if (Prefs.DevMode)
			{
				File.WriteAllText(VersionDir, CurrentVersion);
			}
			new Harmony("Neronix17.TabulaRasa.RimWorld").PatchAll(Assembly.GetExecutingAssembly());
		}

		public override string SettingsCategory()
		{
			return "Tabula Rasa";
		}

		public override void DoSettingsWindowContents(Rect inRect)
		{
			//IL_0042: Unknown result type (might be due to invalid IL or missing references)
			//IL_0049: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0056: Expected O, but got Unknown
			//IL_0078: Unknown result type (might be due to invalid IL or missing references)
			bool flag = optionsViewRectHeight > ((Rect)(ref inRect)).height;
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y, ((Rect)(ref inRect)).width - (flag ? 26f : 0f), optionsViewRectHeight);
			Widgets.BeginScrollView(inRect, ref optionsScrollPosition, val, true);
			Listing_Standard val2 = new Listing_Standard();
			Rect val3 = default(Rect);
			((Rect)(ref val3))..ctor(((Rect)(ref val)).x, ((Rect)(ref val)).y, ((Rect)(ref val)).width, 999999f);
			((Listing)val2).Begin(val3);
			DoOptionsCategoryContents(val2);
			optionsViewRectHeight = ((Listing)val2).CurHeight;
			((Listing)val2).End();
			Widgets.EndScrollView();
		}

		public void DoOptionsCategoryContents(Listing_Standard listing)
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0075: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
			//IL_0139: Unknown result type (might be due to invalid IL or missing references)
			//IL_0184: Unknown result type (might be due to invalid IL or missing references)
			//IL_022a: Unknown result type (might be due to invalid IL or missing references)
			listing.LabelBacked("Mod Update Settings", Color.white, (GameFont)2);
			if (listing.ButtonTextLabeled("Unmarks all updates you've previously marked as seen, letting you see them again.", "Unmark All Updates", (TextAnchor)0, (string)null, (string)null))
			{
				settings.markedAsSeen = new List<string>();
				UpdateUtil.allUpdatesCached = new List<UpdateDef>();
			}
			listing.CheckboxLabeled("Show Old Mod Updates", ref settings.showOldUpdates, "By default, mod updates older than three months are hidden automatically, if you enable this, you'll see them regardless of how old they are.", 0f, 1f);
			((Listing)listing).Gap(12f);
			listing.LabelBacked("Incident Settings", Color.white, (GameFont)2);
			listing.CheckboxLabeled("Special Occasions", ref settings.specialOccasions, "Some features may only happen during specific special occasions, like April Fools, so this option exists so those can be disabled.", 0f, 1f);
			((Listing)listing).Gap(12f);
			listing.LabelBacked("Subcategories", Color.white, (GameFont)2);
			listing.AddLabeledSlider($"Row Count: {settings.gizmoRowHeight}", ref settings.gizmoRowHeight, 1f, 6f, null, null, 1f);
			listing.CheckboxLabeled("Shrunken Orders (Experimental)", ref settings.enableShrunkOrders, "If enabled, the orders portion of the subcategories menu will be scaled down so more can fit on screen.\n\nRequires game restart to properly take effect.\n\nFor half scale orders inside subcategories, a patch overriding the hardcoded height for those buttons had to be made, this toggle is here in case this causes unforseen issues.", 0f, 1f);
			((Listing)listing).Gap(12f);
			if (ModLister.BiotechInstalled)
			{
				listing.LabelBacked("Biotech Specific", Color.white, (GameFont)2);
				listing.CheckboxLabeled("Show Xenotype Editor Debug Option", ref settings.showXenotypeEditorMenu, "If Enabled, an icon will be displayed at the top of the screen along with other DevMode icons as long as DevMode is enabled, allowing access to the Xenotype editor from places other than the starter pawn loadout screen.", 0f, 1f);
				((Listing)listing).Gap(12f);
			}
			if (!ModLister.RoyaltyInstalled)
			{
				return;
			}
			listing.LabelBacked("Royalty Specific", Color.white, (GameFont)2);
			listing.CheckboxLabeled("Prevent Empire Hostility", ref settings.preventEmpireHostility, "If Enabled, automatically patches any player faction defs not be always hostile with the Empire from Royalty. Having to do them manually every time because Ludeon chose to make it that way is bullshit and I'm sick of it.", 0f, 1f);
			if (!settings.preventEmpireHostility)
			{
				return;
			}
			((Listing)listing).GapLine(12f);
			listing.Note("The following is a list of player faction defs, these can be toggled so they they are not affected by the faction hostility change in the case where a player faction is intended to be hostile towards them.", (GameFont)1);
			foreach (FactionDef item in DefDatabase<FactionDef>.AllDefs.Where((FactionDef f) => f.isPlayer))
			{
				bool value = settings.empireHostilityFixedFactions[((Def)item).defName];
				listing.CheckboxLabeled(TaggedString.op_Implicit(((Def)item).LabelCap), ref value, (string)null, 0f, 1f);
				settings.empireHostilityFixedFactions[((Def)item).defName] = value;
			}
		}
	}
	public enum TabulaRasaSettingsPage
	{
		General,
		Race_Spawning
	}
	public class TabulaRasaSettings : ModSettings
	{
		public bool onlyReplaceHumans = true;

		public Dictionary<string, bool> raceSpawningSettings = new Dictionary<string, bool>();

		public Dictionary<string, float> raceSpawningWeights = new Dictionary<string, float>();

		public bool modUpdates = true;

		public bool showOldUpdates;

		public List<string> markedAsSeen = new List<string>();

		public bool specialOccasions = true;

		public bool showXenotypeEditorMenu = true;

		public bool preventEmpireHostility = true;

		public Dictionary<string, bool> empireHostilityFixedFactions = new Dictionary<string, bool>();

		public float gizmoRowHeight = 3f;

		public bool enableShrunkOrders;

		public IEnumerable<string> GetEnabledSettings => from p in ((object)this).GetType().GetFields()
			where p.FieldType == typeof(bool) && (bool)p.GetValue(this)
			select p.Name;

		public override void ExposeData()
		{
			((ModSettings)this).ExposeData();
			Scribe_Collections.Look<string, bool>(ref raceSpawningSettings, "raceSpawningSettings", (LookMode)0, (LookMode)0);
			Scribe_Collections.Look<string, float>(ref raceSpawningWeights, "raceSpawningWeights", (LookMode)0, (LookMode)0);
			Scribe_Values.Look<bool>(ref modUpdates, "modUpdates", true, false);
			Scribe_Collections.Look<string>(ref markedAsSeen, "markedAsSeen", (LookMode)0, Array.Empty<object>());
			Scribe_Values.Look<bool>(ref specialOccasions, "specialPawnGroupMakers", true, false);
			Scribe_Values.Look<bool>(ref preventEmpireHostility, "preventEmpireHostility", true, false);
			Scribe_Collections.Look<string, bool>(ref empireHostilityFixedFactions, "empireHostilityFixedFactions", (LookMode)0, (LookMode)0);
			Scribe_Values.Look<float>(ref gizmoRowHeight, "gizmoRowHeight", 3f, false);
			Scribe_Values.Look<bool>(ref enableShrunkOrders, "disableShrunkOrders", false, false);
		}

		public bool IsValidSetting(string input)
		{
			if ((from p in ((object)this).GetType().GetFields()
				where p.FieldType == typeof(bool)
				select p).Any((FieldInfo i) => i.Name == input))
			{
				return true;
			}
			return false;
		}
	}
	public class WorldComp_EnergyNeed : WorldComponent
	{
		public List<Building> chargingSockets = new List<Building>();

		public List<Building> wirelessChargers = new List<Building>();

		public List<Building> wirelessChargersGlobal = new List<Building>();

		public WorldComp_EnergyNeed(World world)
			: base(world)
		{
		}

		public void AddWirelessCharger(Building building, bool global)
		{
			wirelessChargers.Add(building);
			if (global)
			{
				wirelessChargersGlobal.Add(building);
			}
		}

		public void RemoveWirelessCharger(Building building, bool global)
		{
			wirelessChargers.Remove(building);
			if (global)
			{
				wirelessChargersGlobal.Remove(building);
			}
		}
	}
	public class WorldComp_Blueprints : WorldComponent
	{
		public WorldComp_Blueprints(World world)
			: base(world)
		{
		}
	}
}
namespace TabulaRasa.Hediffs
{
	public class HediffCompProperties_GeneticConversion : HediffCompProperties
	{
		public IntRange tickRange = new IntRange(0, 0);

		public XenotypeDef xenotype;

		public bool overwriteGenes;

		public bool convertPawn;

		public FactionDef faction;

		public HediffCompProperties_GeneticConversion()
		{
			//IL_0003: Unknown result type (might be due to invalid IL or missing references)
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			base.compClass = typeof(HediffComp_GeneticConversion);
		}
	}
	public class HediffComp_GeneticConversion : HediffComp
	{
		public Faction faction;

		public int finishingTick = -1;

		public HediffCompProperties_GeneticConversion Props => (HediffCompProperties_GeneticConversion)(object)base.props;

		public override void CompPostMake()
		{
			((HediffComp)this).CompPostMake();
			if (finishingTick < 0)
			{
				finishingTick = ((IntRange)(ref Props.tickRange)).RandomInRange;
			}
		}

		public override void CompPostTick(ref float severityAdjustment)
		{
			((HediffComp)this).CompPostTick(ref severityAdjustment);
			if (Find.TickManager.TicksAbs > finishingTick)
			{
				BeginConversion();
			}
		}

		public void BeginConversion()
		{
			if (Props.overwriteGenes)
			{
				((HediffComp)this).Pawn.genes.ClearXenogenes();
			}
			if (Props.xenotype != null)
			{
				((HediffComp)this).Pawn.genes.SetXenotypeDirect(Props.xenotype);
			}
			if (!Props.convertPawn)
			{
				return;
			}
			if (faction != null)
			{
				((Thing)((HediffComp)this).Pawn).SetFaction(faction, (Pawn)null);
			}
			else if (Props.faction != null)
			{
				Faction val = Find.FactionManager.FirstFactionOfDef(Props.faction);
				if (val != null)
				{
					((Thing)((HediffComp)this).Pawn).SetFaction(val, (Pawn)null);
				}
			}
		}
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.0.0.9375' (yours is '9.0.0.7889')
