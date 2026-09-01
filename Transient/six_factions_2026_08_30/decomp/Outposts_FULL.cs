using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
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
using Verse.Sound;

[assembly: CompilationRelaxations(8)]
[assembly: RuntimeCompatibility(WrapNonExceptionThrows = true)]
[assembly: Debuggable(DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints)]
[assembly: AssemblyTitle("Outposts")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("Outposts")]
[assembly: AssemblyCopyright("Copyright c  2021")]
[assembly: AssemblyTrademark("")]
[assembly: ComVisible(false)]
[assembly: Guid("F2D422F4-D722-47CC-BC03-CC656C20CDEA")]
[assembly: AssemblyFileVersion("1.0.0.0")]
[assembly: TargetFramework(".NETFramework,Version=v4.7.2", FrameworkDisplayName = ".NET Framework 4.7.2")]
[assembly: SecurityPermission(SecurityAction.RequestMinimum, SkipVerification = true)]
[assembly: AssemblyVersion("3.0.0.0")]
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
	[AttributeUsage(AttributeTargets.Assembly, AllowMultiple = true)]
	internal sealed class IgnoresAccessChecksToAttribute : Attribute
	{
		internal IgnoresAccessChecksToAttribute(string assemblyName)
		{
		}
	}
}
namespace Outposts
{
	public class Dialog_CreateCamp : Window
	{
		private const float LINE_HEIGHT = 100f;

		private readonly Caravan creator;

		private readonly Dictionary<WorldObjectDef, Pair<string, string>> validity;

		private float? prevHeight;

		private Vector2 scrollPosition = new Vector2(0f, 0f);

		public override Vector2 InitialSize => new Vector2(800f, Mathf.Min(1000f, (float)UI.screenHeight - 200f));

		public Dialog_CreateCamp(Caravan creator)
			: base((IWindowDrawing)null)
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_0126: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
			//IL_0184: Unknown result type (might be due to invalid IL or missing references)
			//IL_014b: Unknown result type (might be due to invalid IL or missing references)
			base.doCloseButton = true;
			base.doCloseX = true;
			base.doWindowBackground = true;
			this.creator = creator;
			validity = new Dictionary<WorldObjectDef, Pair<string, string>>();
			foreach (WorldObjectDef outpost in OutpostsMod.Outposts)
			{
				MethodInfo method = outpost.worldObjectClass.GetMethod("CanSpawnOnWith", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic, null, new Type[2]
				{
					typeof(PlanetTile),
					typeof(List<Pawn>)
				}, null);
				MethodInfo method2 = outpost.worldObjectClass.GetMethod("RequirementsString", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic, null, new Type[2]
				{
					typeof(PlanetTile),
					typeof(List<Pawn>)
				}, null);
				OutpostExtension modExtension = ((Def)outpost).GetModExtension<OutpostExtension>();
				string text = modExtension?.CanSpawnOnWithExt(((WorldObject)creator).Tile, creator.HumanColonists()) ?? ((string)method?.Invoke(null, new object[2]
				{
					((WorldObject)creator).Tile,
					creator.HumanColonists()
				}));
				string text2 = GenText.TrimEndNewlines(modExtension?.RequirementsStringBase(((WorldObject)creator).Tile, creator.HumanColonists()) ?? ((string)method2?.Invoke(null, new object[2]
				{
					((WorldObject)creator).Tile,
					creator.HumanColonists()
				})) ?? "");
				validity.Add(outpost, new Pair<string, string>(text, text2));
			}
		}

		public override void DoWindowContents(Rect inRect)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0067: Unknown result type (might be due to invalid IL or missing references)
			//IL_006e: Unknown result type (might be due to invalid IL or missing references)
			Rect val = GenUI.ContractedBy(inRect, 5f);
			((Rect)(ref val)).height = ((Rect)(ref val)).height - 45f;
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(0f, 0f, ((Rect)(ref val)).width - 50f, prevHeight ?? ((float)OutpostsMod.Outposts.Count * 110f));
			Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
			Rect inRect2 = default(Rect);
			((Rect)(ref inRect2))..ctor(10f, 0f, ((Rect)(ref val2)).width, 100f);
			foreach (WorldObjectDef outpost in OutpostsMod.Outposts)
			{
				DoOutpostDisplay(ref inRect2, outpost);
				((Rect)(ref inRect2)).y = ((Rect)(ref inRect2)).y + (((Rect)(ref inRect2)).height + 5f);
				Widgets.DrawLineHorizontal(((Rect)(ref inRect2)).x, ((Rect)(ref inRect2)).y, ((Rect)(ref inRect2)).width);
				((Rect)(ref inRect2)).y = ((Rect)(ref inRect2)).y + 5f;
			}
			prevHeight = ((Rect)(ref inRect2)).y;
			Widgets.EndScrollView();
		}

		private void DoOutpostDisplay(ref Rect inRect, WorldObjectDef outpostDef)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0036: Unknown result type (might be due to invalid IL or missing references)
			//IL_0040: Unknown result type (might be due to invalid IL or missing references)
			//IL_0046: Unknown result type (might be due to invalid IL or missing references)
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			//IL_005c: Unknown result type (might be due to invalid IL or missing references)
			//IL_006f: Unknown result type (might be due to invalid IL or missing references)
			//IL_008d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
			//IL_0102: Unknown result type (might be due to invalid IL or missing references)
			//IL_0114: Unknown result type (might be due to invalid IL or missing references)
			//IL_0147: Unknown result type (might be due to invalid IL or missing references)
			//IL_016a: Unknown result type (might be due to invalid IL or missing references)
			//IL_016f: Unknown result type (might be due to invalid IL or missing references)
			//IL_017d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0183: Unknown result type (might be due to invalid IL or missing references)
			//IL_018e: Unknown result type (might be due to invalid IL or missing references)
			//IL_02dd: Unknown result type (might be due to invalid IL or missing references)
			//IL_02e9: Unknown result type (might be due to invalid IL or missing references)
			//IL_02ee: Unknown result type (might be due to invalid IL or missing references)
			//IL_02f7: Unknown result type (might be due to invalid IL or missing references)
			//IL_01b6: Unknown result type (might be due to invalid IL or missing references)
			//IL_01bb: Unknown result type (might be due to invalid IL or missing references)
			//IL_02c3: Unknown result type (might be due to invalid IL or missing references)
			//IL_02c8: Unknown result type (might be due to invalid IL or missing references)
			//IL_0239: Unknown result type (might be due to invalid IL or missing references)
			GameFont font = Text.Font;
			TextAnchor anchor = Text.Anchor;
			Text.Font = (GameFont)0;
			((Rect)(ref inRect)).height = Text.CalcHeight(((Def)outpostDef).description, ((Rect)(ref inRect)).width - 90f) + 60f;
			Rect val = GenUI.LeftPartPixels(inRect, 50f);
			Rect val2 = GenUI.RightPartPixels(inRect, ((Rect)(ref inRect)).width - 60f);
			Texture2D expandingIconTexture = outpostDef.ExpandingIconTexture;
			GUI.color = ((WorldObject)creator).Faction.Color;
			Widgets.DrawTextureFitted(val, (Texture)(object)expandingIconTexture, 1f, new Vector2((float)((Texture)expandingIconTexture).width, (float)((Texture)expandingIconTexture).height), new Rect(0f, 0f, 1f, 1f), 0f, (Material)null, 1f);
			GUI.color = Color.white;
			Text.Font = (GameFont)2;
			Widgets.Label(GenUI.TopPartPixels(val2, 30f), GenText.CapitalizeFirst(((Def)outpostDef).label, (Def)(object)outpostDef));
			Rect val3 = GenUI.LeftPartPixels(GenUI.BottomPartPixels(val2, 30f), 100f);
			Rect val4 = GenUI.RightPartPixels(GenUI.BottomPartPixels(val2, 30f), ((Rect)(ref val2)).width - 120f);
			Text.Font = (GameFont)0;
			Widgets.Label(new Rect(((Rect)(ref val2)).x, ((Rect)(ref val2)).y + 30f, ((Rect)(ref val2)).width, ((Rect)(ref val2)).height - 60f), ((Def)outpostDef).description);
			Text.Font = (GameFont)1;
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(val4, validity[outpostDef].First);
			Text.Font = font;
			Text.Anchor = anchor;
			if (Widgets.ButtonText(val3, TaggedString.op_Implicit(Translator.Translate("Outposts.Dialog.Create")), true, true, true, (TextAnchor?)null))
			{
				if (GenText.NullOrEmpty(validity[outpostDef].First))
				{
					Outpost outpost = (Outpost)(object)WorldObjectMaker.MakeWorldObject(outpostDef);
					outpost.Name = NameGenerator.GenerateName(((WorldObject)creator).Faction.def.settlementNameMaker, from o in Find.WorldObjects.AllWorldObjects.OfType<Outpost>()
						select o.Name, false, (string)null);
					((WorldObject)outpost).Tile = ((WorldObject)creator).Tile;
					((WorldObject)outpost).SetFaction(((WorldObject)creator).Faction);
					Find.WorldObjects.Add((WorldObject)(object)outpost);
					foreach (Pawn item in GenList.ListFullCopy<Pawn>(creator.PawnsListForReading))
					{
						outpost.AddPawn(item);
					}
					((Window)this).Close(true);
					Find.WorldSelector.Select((WorldObject)(object)outpost, true);
				}
				else
				{
					Messages.Message(validity[outpostDef].First, MessageTypeDefOf.RejectInput, false);
				}
			}
			TooltipHandler.TipRegion(inRect, TipSignal.op_Implicit(validity[outpostDef].Second));
		}
	}
	public class Dialog_GiveItems : Window
	{
		private readonly Vector2 BottomButtonSize = new Vector2(160f, 40f);

		private readonly Caravan caravan;

		private readonly Outpost outpost;

		private TransferableOneWayWidget itemsTransfer;

		private List<TransferableOneWay> transferables;

		public override Vector2 InitialSize => new Vector2(1024f, (float)UI.screenHeight - 100f);

		public override float Margin => 17f;

		public Dialog_GiveItems(Outpost outpost, Caravan caravan)
			: base((IWindowDrawing)null)
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			outpost.CheckNoDestroyedOrNoStack();
			this.outpost = outpost;
			this.caravan = caravan;
		}

		public override void DoWindowContents(Rect inRect)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			GUI.BeginGroup(inRect);
			Rect val = GenUI.AtZero(inRect);
			((Rect)(ref val)).yMin = ((Rect)(ref val)).yMin + 30f;
			DoBottomButtons(val);
			itemsTransfer.OnGUI(val);
			GUI.EndGroup();
		}

		private void DoBottomButtons(Rect rect)
		{
			//IL_003d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			//IL_0151: Unknown result type (might be due to invalid IL or missing references)
			//IL_015b: Unknown result type (might be due to invalid IL or missing references)
			//IL_01b5: Unknown result type (might be due to invalid IL or missing references)
			//IL_01bf: Unknown result type (might be due to invalid IL or missing references)
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(((Rect)(ref rect)).width - BottomButtonSize.x, ((Rect)(ref rect)).height - 40f, BottomButtonSize.x, BottomButtonSize.y);
			if (Widgets.ButtonText(val, TaggedString.op_Implicit(Translator.Translate("Outposts.Give")), true, true, true, (TextAnchor?)null))
			{
				foreach (TransferableOneWay transferable in transferables)
				{
					while (((Transferable)transferable).HasAnyThing && ((Transferable)transferable).CountToTransfer > 0)
					{
						Thing val2 = GenCollection.Pop<Thing>(transferable.things);
						if (val2.stackCount <= ((Transferable)transferable).CountToTransfer)
						{
							((Transferable)transferable).AdjustBy(-val2.stackCount);
							ThingOwner holdingOwner = val2.holdingOwner;
							if (holdingOwner != null)
							{
								holdingOwner.Remove(val2);
							}
							outpost.AddItem(val2);
						}
						else
						{
							outpost.AddItem(val2.SplitOff(((Transferable)transferable).CountToTransfer));
							((Transferable)transferable).AdjustTo(0);
							transferable.things.Add(val2);
						}
					}
				}
				((Window)this).Close(true);
			}
			if (Widgets.ButtonText(new Rect(0f, ((Rect)(ref val)).y, BottomButtonSize.x, BottomButtonSize.y), TaggedString.op_Implicit(Translator.Translate("CancelButton")), true, true, true, (TextAnchor?)null))
			{
				((Window)this).Close(true);
			}
			if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).width / 2f - BottomButtonSize.x, ((Rect)(ref val)).y, BottomButtonSize.x, BottomButtonSize.y), TaggedString.op_Implicit(Translator.Translate("ResetButton")), true, true, true, (TextAnchor?)null))
			{
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_Low, (Map)null);
				CalculateAndRecacheTransferables();
			}
		}

		public override void PostOpen()
		{
			((Window)this).PostOpen();
			CalculateAndRecacheTransferables();
		}

		private void CalculateAndRecacheTransferables()
		{
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Expected O, but got Unknown
			//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ed: Expected O, but got Unknown
			transferables = new List<TransferableOneWay>();
			foreach (Thing item in CaravanInventoryUtility.AllInventoryItems(caravan))
			{
				TransferableOneWay val = TransferableUtility.TransferableMatching<TransferableOneWay>(item, transferables, (TransferAsOneMode)1);
				if (val == null)
				{
					val = new TransferableOneWay();
					transferables.Add(val);
				}
				if (val.things.Contains(item))
				{
					Log.Error("Tried to add the same thing twice to TransferableOneWay: " + (object)item);
					return;
				}
				val.things.Add(item);
			}
			itemsTransfer = new TransferableOneWayWidget((IEnumerable<TransferableOneWay>)transferables, caravan.Name, outpost.Name, TaggedString.op_Implicit(Translator.Translate("FormCaravanColonyThingCountTip")), false, (IgnorePawnsInventoryMode)3, false, (Func<float>)null, 0f, false, (PlanetTile?)null, false, false, false, false, false, false, false, false, false, false);
		}
	}
	public class Dialog_TakeItems : Window
	{
		private readonly Vector2 BottomButtonSize = new Vector2(160f, 40f);

		private readonly Caravan caravan;

		private readonly Outpost outpost;

		private TransferableOneWayWidget itemsTransfer;

		private List<TransferableOneWay> transferables;

		public override Vector2 InitialSize => new Vector2(1024f, (float)UI.screenHeight - 100f);

		public override float Margin => 17f;

		public Dialog_TakeItems(Outpost outpost, Caravan caravan)
			: base((IWindowDrawing)null)
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			outpost.CheckNoDestroyedOrNoStack();
			this.outpost = outpost;
			this.caravan = caravan;
		}

		public override void DoWindowContents(Rect inRect)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			GUI.BeginGroup(inRect);
			Rect val = GenUI.AtZero(inRect);
			((Rect)(ref val)).yMin = ((Rect)(ref val)).yMin + 30f;
			DoBottomButtons(val);
			itemsTransfer.OnGUI(val);
			GUI.EndGroup();
		}

		private void DoBottomButtons(Rect rect)
		{
			//IL_003d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			//IL_0161: Unknown result type (might be due to invalid IL or missing references)
			//IL_016b: Unknown result type (might be due to invalid IL or missing references)
			//IL_01c5: Unknown result type (might be due to invalid IL or missing references)
			//IL_01cf: Unknown result type (might be due to invalid IL or missing references)
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(((Rect)(ref rect)).width - BottomButtonSize.x, ((Rect)(ref rect)).height - 40f, BottomButtonSize.x, BottomButtonSize.y);
			if (Widgets.ButtonText(val, TaggedString.op_Implicit(Translator.Translate("Outposts.Take")), true, true, true, (TextAnchor?)null))
			{
				foreach (TransferableOneWay transferable in transferables)
				{
					while (((Transferable)transferable).HasAnyThing && ((Transferable)transferable).CountToTransfer > 0)
					{
						Thing val2 = GenCollection.Pop<Thing>(transferable.things);
						if (val2.stackCount <= ((Transferable)transferable).CountToTransfer)
						{
							((Transferable)transferable).AdjustBy(-val2.stackCount);
							ThingOwner holdingOwner = val2.holdingOwner;
							if (holdingOwner != null)
							{
								holdingOwner.Remove(val2);
							}
							caravan.AddPawnOrItem(outpost.TakeItem(val2), true);
						}
						else
						{
							caravan.AddPawnOrItem(val2.SplitOff(((Transferable)transferable).CountToTransfer), true);
							((Transferable)transferable).AdjustTo(0);
							transferable.things.Add(val2);
						}
					}
				}
				((Window)this).Close(true);
			}
			if (Widgets.ButtonText(new Rect(0f, ((Rect)(ref val)).y, BottomButtonSize.x, BottomButtonSize.y), TaggedString.op_Implicit(Translator.Translate("CancelButton")), true, true, true, (TextAnchor?)null))
			{
				((Window)this).Close(true);
			}
			if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).width / 2f - BottomButtonSize.x, ((Rect)(ref val)).y, BottomButtonSize.x, BottomButtonSize.y), TaggedString.op_Implicit(Translator.Translate("ResetButton")), true, true, true, (TextAnchor?)null))
			{
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_Low, (Map)null);
				CalculateAndRecacheTransferables();
			}
		}

		public override void PostOpen()
		{
			((Window)this).PostOpen();
			CalculateAndRecacheTransferables();
		}

		private void CalculateAndRecacheTransferables()
		{
			//IL_0036: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Expected O, but got Unknown
			//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
			//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e7: Expected O, but got Unknown
			transferables = new List<TransferableOneWay>();
			foreach (Thing thing in outpost.Things)
			{
				TransferableOneWay val = TransferableUtility.TransferableMatching<TransferableOneWay>(thing, transferables, (TransferAsOneMode)1);
				if (val == null)
				{
					val = new TransferableOneWay();
					transferables.Add(val);
				}
				if (val.things.Contains(thing))
				{
					Log.Error("Tried to add the same thing twice to TransferableOneWay: " + (object)thing);
					return;
				}
				val.things.Add(thing);
			}
			itemsTransfer = new TransferableOneWayWidget((IEnumerable<TransferableOneWay>)transferables, outpost.Name, caravan.Name, TaggedString.op_Implicit(Translator.Translate("FormCaravanColonyThingCountTip")), false, (IgnorePawnsInventoryMode)3, false, (Func<float>)null, 0f, false, (PlanetTile?)null, false, false, false, false, false, false, false, false, false, false);
		}
	}
	[StaticConstructorOnStartup]
	public static class HarmonyPatches
	{
		[CompilerGenerated]
		private sealed class <>c__DisplayClass1_0
		{
			public Caravan __instance;

			internal bool <AddCaravanGizmos>b__0(Outpost outpost)
			{
				//IL_000b: Unknown result type (might be due to invalid IL or missing references)
				//IL_0011: Unknown result type (might be due to invalid IL or missing references)
				return Find.WorldGrid.IsNeighborOrSame(((WorldObject)__instance).Tile, ((WorldObject)outpost).Tile);
			}

			internal void <AddCaravanGizmos>b__2()
			{
				Find.WindowStack.Add((Window)(object)new Dialog_CreateCamp(__instance));
			}
		}

		[CompilerGenerated]
		private sealed class <AddCaravanGizmos>d__1 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			private Caravan __instance;

			public Caravan <>3____instance;

			private IEnumerable<Gizmo> gizmos;

			public IEnumerable<Gizmo> <>3__gizmos;

			private <>c__DisplayClass1_0 <>8__1;

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
			public <AddCaravanGizmos>d__1(int <>1__state)
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
				//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
				//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
				//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
				//IL_0116: Unknown result type (might be due to invalid IL or missing references)
				//IL_011c: Unknown result type (might be due to invalid IL or missing references)
				//IL_012b: Unknown result type (might be due to invalid IL or missing references)
				//IL_0131: Unknown result type (might be due to invalid IL or missing references)
				//IL_0140: Unknown result type (might be due to invalid IL or missing references)
				//IL_014b: Unknown result type (might be due to invalid IL or missing references)
				//IL_0152: Unknown result type (might be due to invalid IL or missing references)
				//IL_0158: Unknown result type (might be due to invalid IL or missing references)
				//IL_016c: Expected O, but got Unknown
				//IL_0181: Unknown result type (might be due to invalid IL or missing references)
				//IL_0186: Unknown result type (might be due to invalid IL or missing references)
				//IL_019d: Unknown result type (might be due to invalid IL or missing references)
				//IL_01a3: Unknown result type (might be due to invalid IL or missing references)
				//IL_01b2: Unknown result type (might be due to invalid IL or missing references)
				//IL_01b8: Unknown result type (might be due to invalid IL or missing references)
				//IL_01c7: Unknown result type (might be due to invalid IL or missing references)
				//IL_01d7: Expected O, but got Unknown
				try
				{
					switch (<>1__state)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<>8__1 = new <>c__DisplayClass1_0();
						<>8__1.__instance = __instance;
						<>7__wrap1 = gizmos.GetEnumerator();
						<>1__state = -3;
						goto IL_008b;
					case 1:
						<>1__state = -3;
						goto IL_008b;
					case 2:
						<>1__state = -1;
						break;
					case 3:
						{
							<>1__state = -1;
							break;
						}
						IL_008b:
						if (<>7__wrap1.MoveNext())
						{
							Gizmo current = <>7__wrap1.Current;
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = null;
						if (Find.WorldObjects.AnySettlementBaseAtOrAdjacent(((WorldObject)<>8__1.__instance).Tile) || Find.WorldObjects.AllWorldObjects.OfType<Outpost>().Any((Outpost outpost) => Find.WorldGrid.IsNeighborOrSame(((WorldObject)<>8__1.__instance).Tile, ((WorldObject)outpost).Tile)))
						{
							<>2__current = (Gizmo)new Command_Action
							{
								action = delegate
								{
								},
								defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Create.Label")),
								defaultDesc = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Create.Desc")),
								icon = (Texture)(object)TexOutposts.CreateTex,
								Disabled = true,
								disabledReason = TaggedString.op_Implicit(Translator.Translate("Outposts.TooClose"))
							};
							<>1__state = 2;
							return true;
						}
						<>2__current = (Gizmo)new Command_Action
						{
							action = delegate
							{
								Find.WindowStack.Add((Window)(object)new Dialog_CreateCamp(<>8__1.__instance));
							},
							defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Create.Label")),
							defaultDesc = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Create.Desc")),
							icon = (Texture)(object)TexOutposts.CreateTex
						};
						<>1__state = 3;
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
				<AddCaravanGizmos>d__1 <AddCaravanGizmos>d__;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					<AddCaravanGizmos>d__ = this;
				}
				else
				{
					<AddCaravanGizmos>d__ = new <AddCaravanGizmos>d__1(0);
				}
				<AddCaravanGizmos>d__.gizmos = <>3__gizmos;
				<AddCaravanGizmos>d__.__instance = <>3____instance;
				return <AddCaravanGizmos>d__;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Gizmo>)this).GetEnumerator();
			}
		}

		public static void DoPatches()
		{
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0038: Expected O, but got Unknown
			//IL_0065: Unknown result type (might be due to invalid IL or missing references)
			//IL_0071: Expected O, but got Unknown
			OutpostsMod.Harm.Patch((MethodBase)AccessTools.Method(typeof(Caravan), "GetGizmos", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(HarmonyPatches), "AddCaravanGizmos", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
			OutpostsMod.Harm.Patch((MethodBase)AccessTools.Method(typeof(Caravan), "GetInspectString", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(HarmonyPatches), "AddRestingAtOutpost", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		}

		[IteratorStateMachine(typeof(<AddCaravanGizmos>d__1))]
		public static IEnumerable<Gizmo> AddCaravanGizmos(IEnumerable<Gizmo> gizmos, Caravan __instance)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <AddCaravanGizmos>d__1(-2)
			{
				<>3__gizmos = gizmos,
				<>3____instance = __instance
			};
		}

		public static void AddRestingAtOutpost(Caravan __instance, ref string __result)
		{
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			if (!__instance.pather.MovingNow)
			{
				Outpost outpost = Find.WorldObjects.WorldObjectAt<Outpost>(((WorldObject)__instance).Tile);
				if (outpost != null)
				{
					__result = TaggedString.op_Implicit(__result + ("\n" + TranslatorFormattedStringExtensions.Translate("Outposts.RestingAt", NamedArgument.op_Implicit(outpost.Name))));
				}
			}
		}
	}
	public class LordJob_Deliver : LordJob
	{
		private IntVec3 deliverLoc;

		public LordJob_Deliver()
		{
		}

		public LordJob_Deliver(IntVec3 deliverLoc)
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			this.deliverLoc = deliverLoc;
		}

		public override void ExposeData()
		{
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			((LordJob)this).ExposeData();
			Scribe_Values.Look<IntVec3>(ref deliverLoc, "deliverLoc", default(IntVec3), false);
		}

		public override StateGraph CreateGraph()
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Expected O, but got Unknown
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Unknown result type (might be due to invalid IL or missing references)
			//IL_002f: Expected O, but got Unknown
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Expected O, but got Unknown
			//IL_0053: Unknown result type (might be due to invalid IL or missing references)
			//IL_005d: Expected O, but got Unknown
			//IL_0070: Unknown result type (might be due to invalid IL or missing references)
			//IL_007a: Expected O, but got Unknown
			//IL_007a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0086: Unknown result type (might be due to invalid IL or missing references)
			//IL_008d: Expected O, but got Unknown
			//IL_0094: Unknown result type (might be due to invalid IL or missing references)
			//IL_009e: Expected O, but got Unknown
			//IL_009e: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c2: Expected O, but got Unknown
			//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d3: Expected O, but got Unknown
			//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e8: Expected O, but got Unknown
			//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f9: Expected O, but got Unknown
			//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
			//IL_0103: Expected O, but got Unknown
			StateGraph val = new StateGraph();
			LordToil_Travel val3 = (LordToil_Travel)(object)(val.StartingToil = (LordToil)new LordToil_Travel(deliverLoc)
			{
				maxDanger = (Danger)3,
				useAvoidGrid = true
			});
			LordToil_ExitMap val4 = new LordToil_ExitMap((LocomotionUrgency)0, true, false);
			val.AddToil((LordToil)(object)val4);
			LordToil_Drop lordToil_Drop = new LordToil_Drop();
			val.AddToil((LordToil)(object)lordToil_Drop);
			Transition val5 = new Transition((LordToil)(object)val3, (LordToil)(object)lordToil_Drop, false, true);
			val5.AddTrigger((Trigger)new Trigger_Memo("TravelArrived"));
			val5.AddTrigger((Trigger)new Trigger_PawnHarmed(1f, false, (Faction)null, (DutyDef)null, (int?)null));
			val.AddTransition(val5, false);
			Transition val6 = new Transition((LordToil)(object)lordToil_Drop, (LordToil)(object)val4, false, true);
			val6.AddTrigger((Trigger)new Trigger_Memo("AllDropped"));
			val.AddTransition(val6, false);
			LordToil_GotoDropLoc lordToil_GotoDropLoc = new LordToil_GotoDropLoc();
			val.AddToil((LordToil)(object)lordToil_GotoDropLoc);
			Transition val7 = new Transition((LordToil)(object)lordToil_Drop, (LordToil)(object)lordToil_GotoDropLoc, false, true);
			val7.AddTrigger((Trigger)new Trigger_Memo("AllDropped"));
			val.AddTransition(val7, false);
			Transition val8 = new Transition((LordToil)(object)lordToil_GotoDropLoc, (LordToil)(object)lordToil_Drop, false, true);
			val8.AddTrigger((Trigger)new Trigger_Memo("TravelArrived"));
			val.AddTransition(val8, false);
			return val;
		}
	}
	public class LordToil_Drop : LordToil
	{
		public class LordToilData_Drop : LordToilData
		{
			public int TicksPassed;

			public override void ExposeData()
			{
				Scribe_Values.Look<int>(ref TicksPassed, "ticksPassed", 0, false);
			}
		}

		public const string DROPPED_MEMO = "AllDropped";

		public const string AREAFULL_MEMO = "AreaFull";

		public LordToilData_Drop Data => base.data as LordToilData_Drop;

		public LordToil_Drop()
		{
			base.data = (LordToilData)(object)new LordToilData_Drop
			{
				TicksPassed = 0
			};
		}

		public override void UpdateAllDuties()
		{
			//IL_0024: Unknown result type (might be due to invalid IL or missing references)
			//IL_002e: Expected O, but got Unknown
			foreach (Pawn ownedPawn in base.lord.ownedPawns)
			{
				ownedPawn.mindState.duty = new PawnDuty(Outposts_DefOf.VEF_DropAllInInventory);
			}
			Data.TicksPassed = 0;
		}

		public override void LordToilTick()
		{
			((LordToil)this).LordToilTick();
			if (base.lord.ownedPawns.All((Pawn pawn) => !((IEnumerable<Thing>)pawn.inventory.innerContainer).Any()))
			{
				base.lord.ReceiveMemo("AllDropped");
			}
			Data.TicksPassed++;
			if (Data.TicksPassed > 60)
			{
				base.lord.ReceiveMemo("AreaFull");
			}
		}
	}
	public class LordToil_GotoDropLoc : LordToil_Travel
	{
		public LordToil_GotoDropLoc()
			: base(IntVec3.Zero)
		{
		}//IL_0001: Unknown result type (might be due to invalid IL or missing references)


		public override void UpdateAllDuties()
		{
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			((LordToil_Travel)this).SetDestination(FindDropSpot(((LordToil)this).lord.ownedPawns.First()));
			((LordToil_Travel)this).UpdateAllDuties();
		}

		private IntVec3 FindDropSpot(Pawn pawn)
		{
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_008a: Unknown result type (might be due to invalid IL or missing references)
			//IL_007d: Unknown result type (might be due to invalid IL or missing references)
			IntVec3 result = default(IntVec3);
			if (CellFinder.TryFindRandomReachableCellNearPosition(((Thing)pawn).Position, ((Thing)pawn).Position, ((Thing)pawn).Map, 25.8f, TraverseParms.For(pawn, (Danger)3, (TraverseMode)0, false, false, false, true), (Predicate<IntVec3>)((IntVec3 x) => GenGrid.Walkable(x, ((Thing)pawn).Map) && GenRadial.RadialCellsAround(x, 12.9f, true).Count((IntVec3 c) => GenGrid.Walkable(c, ((Thing)pawn).Map) && !GenCollection.Any<Thing>(GridsUtility.GetThingList(c, ((Thing)pawn).Map), (Predicate<Thing>)((Thing t) => t.def.saveCompressible || (int)t.def.category == 2))) >= GenRadial.NumCellsInRadius(12.9f) / 2), (Predicate<Region>)((Region _) => true), ref result, 999999))
			{
				return result;
			}
			return CellFinder.RandomCell(((Thing)pawn).Map);
		}
	}
	public class JobGiver_DropAll : ThinkNode_JobGiver
	{
		public override Job TryGiveJob(Pawn pawn)
		{
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			if (pawn?.inventory == null)
			{
				return null;
			}
			pawn.inventory.UnloadEverything = true;
			pawn.inventory.DropAllNearPawn(((Thing)pawn).Position, false, true);
			return null;
		}
	}
	public class Outpost : MapParent, IRenameable
	{
		[CompilerGenerated]
		private sealed class <>c__DisplayClass72_0
		{
			public Pawn p;

			public Outpost <>4__this;

			internal void <GetGizmos>b__4()
			{
				//IL_0027: Unknown result type (might be due to invalid IL or missing references)
				CaravanMaker.MakeCaravan(Gen.YieldSingle<Pawn>(<>4__this.RemovePawn(p)), ((Thing)p).Faction, ((WorldObject)<>4__this).Tile, true);
			}
		}

		[CompilerGenerated]
		private sealed class <>c__DisplayClass72_1
		{
			public Map map;

			public Outpost <>4__this;

			internal void <GetGizmos>b__8()
			{
				<>4__this.deliveryMap = map;
			}
		}

		[CompilerGenerated]
		private sealed class <GetGizmos>d__72 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Gizmo <>2__current;

			private int <>l__initialThreadId;

			public Outpost <>4__this;

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
			public <GetGizmos>d__72(int <>1__state)
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
				//IL_030a: Unknown result type (might be due to invalid IL or missing references)
				//IL_030f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0321: Unknown result type (might be due to invalid IL or missing references)
				//IL_0331: Expected O, but got Unknown
				//IL_0347: Unknown result type (might be due to invalid IL or missing references)
				//IL_034c: Unknown result type (might be due to invalid IL or missing references)
				//IL_035e: Unknown result type (might be due to invalid IL or missing references)
				//IL_036e: Expected O, but got Unknown
				//IL_0185: Unknown result type (might be due to invalid IL or missing references)
				//IL_018a: Unknown result type (might be due to invalid IL or missing references)
				//IL_019c: Unknown result type (might be due to invalid IL or missing references)
				//IL_01a2: Unknown result type (might be due to invalid IL or missing references)
				//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
				//IL_01b7: Unknown result type (might be due to invalid IL or missing references)
				//IL_01c6: Unknown result type (might be due to invalid IL or missing references)
				//IL_01d1: Unknown result type (might be due to invalid IL or missing references)
				//IL_01e5: Unknown result type (might be due to invalid IL or missing references)
				//IL_01eb: Unknown result type (might be due to invalid IL or missing references)
				//IL_01ff: Expected O, but got Unknown
				//IL_03d2: Unknown result type (might be due to invalid IL or missing references)
				//IL_03d7: Unknown result type (might be due to invalid IL or missing references)
				//IL_03e2: Unknown result type (might be due to invalid IL or missing references)
				//IL_03e8: Unknown result type (might be due to invalid IL or missing references)
				//IL_03f7: Unknown result type (might be due to invalid IL or missing references)
				//IL_040e: Expected O, but got Unknown
				//IL_038c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0391: Unknown result type (might be due to invalid IL or missing references)
				//IL_03a3: Unknown result type (might be due to invalid IL or missing references)
				//IL_03ae: Unknown result type (might be due to invalid IL or missing references)
				//IL_03be: Expected O, but got Unknown
				//IL_02c2: Unknown result type (might be due to invalid IL or missing references)
				//IL_02c7: Unknown result type (might be due to invalid IL or missing references)
				//IL_02d9: Unknown result type (might be due to invalid IL or missing references)
				//IL_02e4: Unknown result type (might be due to invalid IL or missing references)
				//IL_02f4: Expected O, but got Unknown
				//IL_0235: Unknown result type (might be due to invalid IL or missing references)
				//IL_023a: Unknown result type (might be due to invalid IL or missing references)
				//IL_024c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0252: Unknown result type (might be due to invalid IL or missing references)
				//IL_0261: Unknown result type (might be due to invalid IL or missing references)
				//IL_011e: Unknown result type (might be due to invalid IL or missing references)
				//IL_0123: Unknown result type (might be due to invalid IL or missing references)
				//IL_0135: Unknown result type (might be due to invalid IL or missing references)
				//IL_013b: Unknown result type (might be due to invalid IL or missing references)
				//IL_014a: Unknown result type (might be due to invalid IL or missing references)
				//IL_0150: Unknown result type (might be due to invalid IL or missing references)
				//IL_015f: Unknown result type (might be due to invalid IL or missing references)
				//IL_016f: Expected O, but got Unknown
				//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
				//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
				//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
				//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
				//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
				//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
				//IL_00f6: Unknown result type (might be due to invalid IL or missing references)
				//IL_0106: Expected O, but got Unknown
				//IL_027e: Unknown result type (might be due to invalid IL or missing references)
				//IL_0283: Unknown result type (might be due to invalid IL or missing references)
				//IL_0292: Unknown result type (might be due to invalid IL or missing references)
				//IL_02a2: Expected O, but got Unknown
				try
				{
					int num = <>1__state;
					Outpost CS$<>8__locals29 = <>4__this;
					switch (num)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<>7__wrap1 = CS$<>8__locals29.<>n__0().GetEnumerator();
						<>1__state = -3;
						goto IL_0092;
					case 1:
						<>1__state = -3;
						goto IL_0092;
					case 2:
						<>1__state = -1;
						goto IL_0184;
					case 3:
						<>1__state = -1;
						goto IL_0184;
					case 4:
						<>1__state = -1;
						if (OutpostsMod.Settings.DeliveryMethod != DeliveryMethod.Store && !GenText.NullOrEmpty(CS$<>8__locals29.ProductionString()))
						{
							Command_Action val2 = new Command_Action
							{
								action = delegate
								{
									//IL_008a: Unknown result type (might be due to invalid IL or missing references)
									//IL_0094: Expected O, but got Unknown
									//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
									//IL_00b8: Expected O, but got Unknown
									List<FloatMenuOption> list = new List<FloatMenuOption>();
									using (IEnumerator<Map> enumerator2 = (from m in Find.Maps
										where m.IsPlayerHome
										orderby Find.WorldGrid.ApproxDistanceInTiles(((WorldObject)m.Parent).Tile, ((WorldObject)CS$<>8__locals29).Tile)
										select m).GetEnumerator())
									{
										while (enumerator2.MoveNext())
										{
											<>c__DisplayClass72_1 CS$<>8__locals11 = new <>c__DisplayClass72_1
											{
												<>4__this = CS$<>8__locals29,
												map = enumerator2.Current
											};
											list.Add(new FloatMenuOption(((WorldObject)CS$<>8__locals11.map.Parent).LabelCap, (Action)delegate
											{
												CS$<>8__locals11.<>4__this.deliveryMap = CS$<>8__locals11.map;
											}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
										}
									}
									Find.WindowStack.Add((Window)new FloatMenu(list));
								},
								defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.DeliveryColony.Label"))
							};
							Map deliveryMap = CS$<>8__locals29.deliveryMap;
							((Command)val2).defaultDesc = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.Commands.DeliveryColony.Desc", NamedArgument.op_Implicit((deliveryMap != null) ? ((WorldObject)deliveryMap.Parent).LabelCap : null)));
							((Command)val2).icon = (Texture)(object)SettleUtility.SettleCommandTex;
							<>2__current = (Gizmo)val2;
							<>1__state = 5;
							return true;
						}
						goto IL_02b7;
					case 5:
						<>1__state = -1;
						goto IL_02b7;
					case 6:
						<>1__state = -1;
						<>2__current = (Gizmo)new Command_Action
						{
							action = delegate
							{
								//IL_0038: Unknown result type (might be due to invalid IL or missing references)
								DamageInfo val = default(DamageInfo);
								((DamageInfo)(ref val))..ctor(DamageDefOf.Crush, 10f, 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false);
								((DamageInfo)(ref val)).SetIgnoreInstantKillProtection(true);
								((Thing)GenCollection.RandomElement<Pawn>((IEnumerable<Pawn>)CS$<>8__locals29.occupants)).TakeDamage(val);
							},
							defaultLabel = "Dev: Random pawn takes 10 damage"
						};
						<>1__state = 7;
						return true;
					case 7:
						<>1__state = -1;
						<>2__current = (Gizmo)new Command_Action
						{
							action = delegate
							{
								foreach (Pawn occupant in CS$<>8__locals29.occupants)
								{
									((Need)occupant.needs.food).CurLevel = 0f;
								}
							},
							defaultLabel = "Dev: All pawns 0% food"
						};
						<>1__state = 8;
						return true;
					case 8:
						<>1__state = -1;
						if (CS$<>8__locals29.Packing)
						{
							<>2__current = (Gizmo)new Command_Action
							{
								action = delegate
								{
									CS$<>8__locals29.ticksTillPacked = 1;
								},
								defaultLabel = "Dev: Pack now",
								defaultDesc = "Reduce ticksTillPacked to 1"
							};
							<>1__state = 9;
							return true;
						}
						goto IL_03d1;
					case 9:
						<>1__state = -1;
						goto IL_03d1;
					case 10:
						{
							<>1__state = -1;
							return false;
						}
						IL_0184:
						<>2__current = (Gizmo)new Command_Action
						{
							action = delegate
							{
								//IL_0021: Unknown result type (might be due to invalid IL or missing references)
								//IL_002b: Expected O, but got Unknown
								Find.WindowStack.Add((Window)new FloatMenu(((IEnumerable<Pawn>)CS$<>8__locals29.occupants).Select((Func<Pawn, FloatMenuOption>)delegate(Pawn p)
								{
									//IL_0057: Unknown result type (might be due to invalid IL or missing references)
									//IL_005d: Expected O, but got Unknown
									<>c__DisplayClass72_0 CS$<>8__locals21 = new <>c__DisplayClass72_0
									{
										<>4__this = CS$<>8__locals29,
										p = p
									};
									Name name = CS$<>8__locals21.p.Name;
									return new FloatMenuOption(GenText.CapitalizeFirst(((name != null) ? name.ToStringFull : null) ?? ((Entity)CS$<>8__locals21.p).Label), (Action)delegate
									{
										//IL_0027: Unknown result type (might be due to invalid IL or missing references)
										CaravanMaker.MakeCaravan(Gen.YieldSingle<Pawn>(CS$<>8__locals21.<>4__this.RemovePawn(CS$<>8__locals21.p)), ((Thing)CS$<>8__locals21.p).Faction, ((WorldObject)CS$<>8__locals21.<>4__this).Tile, true);
									}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
								}).ToList()));
							},
							defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Remove.Label")),
							defaultDesc = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Remove.Desc")),
							icon = (Texture)(object)TexOutposts.RemoveTex,
							Disabled = (CS$<>8__locals29.occupants.Count == 1),
							disabledReason = TaggedString.op_Implicit(Translator.Translate("Outposts.Command.Remove.Only1"))
						};
						<>1__state = 4;
						return true;
						IL_0092:
						if (<>7__wrap1.MoveNext())
						{
							Gizmo current = <>7__wrap1.Current;
							<>2__current = current;
							<>1__state = 1;
							return true;
						}
						<>m__Finally1();
						<>7__wrap1 = null;
						if (CS$<>8__locals29.Packing)
						{
							<>2__current = (Gizmo)new Command_Action
							{
								action = delegate
								{
									CS$<>8__locals29.ticksTillPacked = -1;
								},
								defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.StopPack.Label")),
								defaultDesc = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.StopPack.Desc")),
								icon = (Texture)(object)TexOutposts.StopPackTex
							};
							<>1__state = 2;
							return true;
						}
						<>2__current = (Gizmo)new Command_Action
						{
							action = delegate
							{
								CS$<>8__locals29.ticksTillPacked = Mathf.RoundToInt((float)CS$<>8__locals29.TicksToPack * OutpostsMod.Settings.TimeMultiplier);
							},
							defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Pack.Label")),
							defaultDesc = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Pack.Desc")),
							icon = (Texture)(object)TexOutposts.PackTex
						};
						<>1__state = 3;
						return true;
						IL_02b7:
						if (DebugSettings.ShowDevGizmos)
						{
							<>2__current = (Gizmo)new Command_Action
							{
								action = delegate
								{
									CS$<>8__locals29.ticksTillProduction = 10;
								},
								defaultLabel = "Dev: Produce now",
								defaultDesc = "Reduce ticksTillProduction to 10"
							};
							<>1__state = 6;
							return true;
						}
						goto IL_03d1;
						IL_03d1:
						<>2__current = (Gizmo)new Command_Action
						{
							icon = (Texture)(object)TexButton.Rename,
							defaultLabel = TaggedString.op_Implicit(Translator.Translate("Rename")),
							action = delegate
							{
								Find.WindowStack.Add((Window)(object)new Dialog_RenameOutpost(CS$<>8__locals29));
							}
						};
						<>1__state = 10;
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
				<GetGizmos>d__72 result;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					result = this;
				}
				else
				{
					result = new <GetGizmos>d__72(0)
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

		private Material cachedMat;

		private List<Thing> containedItems = new List<Thing>();

		private bool costPaid;

		private OutpostExtension extensionCached;

		public string Name;

		private List<Pawn> occupants = new List<Pawn>();

		private bool skillsDirty = true;

		private int ticksTillPacked = -1;

		private int ticksTillProduction;

		public Map deliveryMap;

		public float raidPoints;

		public Faction raidFaction;

		public static Type VehiclePawnType = AccessTools.TypeByName("Vehicles.VehiclePawn");

		public static MethodInfo VehicleRemoveAllPawns;

		private List<Hediff_Injury> tmpHediffInjuries = new List<Hediff_Injury>();

		private List<Hediff_MissingPart> tmpHediffMissing = new List<Hediff_MissingPart>();

		private readonly Dictionary<SkillDef, int> totalSkills = new Dictionary<SkillDef, int>();

		public virtual float RestPerTickResting => 0.014285715f;

		public IEnumerable<Pawn> AllPawns => occupants;

		public int PawnCount => occupants.Count;

		public override Color ExpandingIconColor => ((WorldObject)this).Faction.Color;

		public virtual int TicksPerProduction => Ext?.TicksPerProduction ?? 900000;

		public override bool HasName => !GenText.NullOrEmpty(Name);

		public override string Label => Name;

		public virtual int TicksToPack => (Ext?.TicksToPack ?? 420000) / occupants.Count;

		public bool Packing => ticksTillPacked > 0;

		public virtual int Range => Ext?.Range ?? (-1);

		public IEnumerable<Thing> Things => containedItems;

		public IEnumerable<Pawn> CapablePawns => AllPawns.Where(IsCapable);

		public string RenamableLabel
		{
			get
			{
				return Name ?? BaseLabel;
			}
			set
			{
				Name = value;
			}
		}

		public string BaseLabel => ((Def)((WorldObject)this).def).label;

		public string InspectLabel => RenamableLabel;

		public override Material Material
		{
			get
			{
				//IL_002a: Unknown result type (might be due to invalid IL or missing references)
				if ((Object)(object)cachedMat == (Object)null)
				{
					cachedMat = MaterialPool.MatFrom(((WorldObject)this).Faction.def.settlementTexturePath, ShaderDatabase.WorldOverlayTransparentLit, ((WorldObject)this).Faction.Color, 3550);
				}
				return cachedMat;
			}
		}

		public virtual ThingDef ProvidedFood => Ext?.ProvidedFood ?? ThingDefOf.MealSimple;

		public OutpostExtension Ext => extensionCached ?? (extensionCached = ((Def)((WorldObject)this).def).GetModExtension<OutpostExtension>());

		public virtual string TimeTillProduction => ColoredText.Colorize(GenDate.ToStringTicksToPeriodVerbose(ticksTillProduction, true, true), ColoredText.DateTimeColor);

		public virtual List<ResultOption> ResultOptions => Ext.ResultOptions;

		public void AddItem(Thing t)
		{
			containedItems.Add(t);
		}

		public Thing TakeItem(Thing t)
		{
			containedItems.Remove(t);
			return t;
		}

		public List<Thing> TakeItems(ThingDef thingDef, int stackCount)
		{
			List<Thing> list = new List<Thing>();
			foreach (Thing containedItem in containedItems)
			{
				if (containedItem.def == thingDef)
				{
					if (stackCount < containedItem.stackCount)
					{
						list.Add(containedItem.SplitOff(stackCount));
						stackCount = 0;
					}
					else
					{
						stackCount = -containedItem.stackCount;
						list.Add(TakeItem(containedItem));
					}
				}
				if (stackCount == 0)
				{
					break;
				}
			}
			return list;
		}

		public override void PostAdd()
		{
			((WorldObject)this).PostAdd();
			ticksTillProduction = Mathf.RoundToInt((float)TicksPerProduction * OutpostsMod.Settings.TimeMultiplier);
		}

		public override void DrawExtraSelectionOverlays()
		{
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			((MapParent)this).DrawExtraSelectionOverlays();
			if (Range > 0)
			{
				GenDraw.DrawWorldRadiusRing(((WorldObject)this).Tile, Range, (Material)null);
			}
		}

		public override void ExposeData()
		{
			((MapParent)this).ExposeData();
			Scribe_Collections.Look<Pawn>(ref occupants, "occupants", (LookMode)2, Array.Empty<object>());
			Scribe_Values.Look<int>(ref ticksTillProduction, "ticksTillProduction", 0, false);
			Scribe_Values.Look<string>(ref Name, "name", (string)null, false);
			Scribe_Collections.Look<Thing>(ref containedItems, "containedItems", (LookMode)2, Array.Empty<object>());
			Scribe_Values.Look<bool>(ref costPaid, "costPaid", false, false);
			Scribe_Values.Look<int>(ref ticksTillPacked, "ticksTillPacked", 0, false);
			Scribe_References.Look<Faction>(ref raidFaction, "raidFaction", false);
			Scribe_Values.Look<float>(ref raidPoints, "raidPoints", 0f, false);
			Scribe_References.Look<Map>(ref deliveryMap, "deliveryMap", false);
			try
			{
				RecachePawnTraits();
			}
			catch (Exception ex)
			{
				Log.Error("Error recaching pawn traits in " + ((WorldObject)this).Label + " - " + ex.ToString());
			}
		}

		public override IEnumerable<FloatMenuOption> GetTransportersFloatMenuOptions(IEnumerable<IThingHolder> pods, Action<PlanetTile, TransportersArrivalAction> launchAction)
		{
			return ((MapParent)this).GetTransportersFloatMenuOptions(pods, launchAction).Concat(TransportPodsArrivalAction_AddToOutpost.GetFloatMenuOptions(pods, launchAction, this));
		}

		public override void Tick()
		{
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_0028: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			((WorldObject)this).Tick();
			if (PawnCount == 0)
			{
				Find.LetterStack.ReceiveLetter(Translator.Translate("Outposts.Abandoned"), TranslatorFormattedStringExtensions.Translate("Outposts.Abandoned.Desc", NamedArgument.op_Implicit(Name)), LetterDefOf.NegativeEvent, (string)null, 0, true);
				((WorldObject)this).Destroy();
			}
			if (((MapParent)this).Map == null)
			{
				SatisfyNeeds();
			}
		}

		public override void TickInterval(int delta)
		{
			//IL_0077: Unknown result type (might be due to invalid IL or missing references)
			((MapParent)this).TickInterval(delta);
			if (Packing)
			{
				ticksTillPacked -= delta;
				if (ticksTillPacked <= 0)
				{
					ConvertToCaravan();
				}
			}
			else if (TicksPerProduction > 0)
			{
				ticksTillProduction -= delta;
				if (ticksTillProduction <= 0)
				{
					ticksTillProduction = Mathf.RoundToInt((float)TicksPerProduction * OutpostsMod.Settings.TimeMultiplier);
					Produce();
				}
			}
			Caravan val = Find.WorldObjects.PlayerControlledCaravanAt(((WorldObject)this).Tile);
			if (val != null && !val.pather.MovingNow)
			{
				foreach (Pawn item in val.PawnsListForReading)
				{
					if (item.needs?.rest == null)
					{
						continue;
					}
					Need_Rest rest = item.needs.rest;
					((Need)rest).CurLevel = ((Need)rest).CurLevel + RestPerTickResting * (float)delta;
					if (!Gen.IsHashIntervalTick((Thing)(object)item, 300, delta))
					{
						continue;
					}
					Need_Food val2 = item.needs?.food;
					if (val2 == null || !(((Need)val2).CurLevelPercentage <= item.RaceProps.FoodLevelPercentageWantEat))
					{
						continue;
					}
					ThingDef providedFood = ProvidedFood;
					if (providedFood != null && providedFood.IsNutritionGivingIngestible && ProvidedFood.ingestible.HumanEdible)
					{
						Thing val3 = ThingMaker.MakeThing(ProvidedFood, (ThingDef)null);
						if (val3.IngestibleNow && item.RaceProps.CanEverEat(val3))
						{
							((Need)val2).CurLevel = ((Need)val2).CurLevel + val3.Ingested(item, val2.NutritionWanted);
						}
					}
				}
			}
			if (((MapParent)this).Map == null)
			{
				SatisfyNeedsInterval(delta);
			}
		}

		public virtual IEnumerable<Thing> ProducedThings()
		{
			return ResultOptions.SelectMany((ResultOption resultOption) => resultOption.Make(CapablePawns.ToList()));
		}

		public virtual void Produce()
		{
			Deliver(ProducedThings());
		}

		public override void SpawnSetup()
		{
			((WorldObject)this).SpawnSetup();
			if (deliveryMap == null)
			{
				deliveryMap = (from m in Find.Maps
					where m.IsPlayerHome
					orderby Find.WorldGrid.ApproxDistanceInTiles(((WorldObject)m.Parent).Tile, ((WorldObject)this).Tile)
					select m).FirstOrDefault();
			}
			RecachePawnTraits();
			OutpostsMod.Notify_Spawned(this);
		}

		public virtual void RecachePawnTraits()
		{
			skillsDirty = true;
			foreach (Pawn item in containedItems.OfType<Pawn>().ToList())
			{
				containedItems.Remove((Thing)(object)item);
				Caravan caravan = CaravanUtility.GetCaravan((Thing)(object)item);
				if (caravan != null)
				{
					caravan.RemovePawn(item);
				}
				AddPawn(item);
			}
		}

		public bool AddPawn(Pawn pawn)
		{
			if (VehiclePawnType != null && VehiclePawnType.IsAssignableFrom(((object)pawn).GetType()))
			{
				if ((object)VehicleRemoveAllPawns == null)
				{
					VehicleRemoveAllPawns = AccessTools.Method(VehiclePawnType, "RemoveAllPawns", (Type[])null, (Type[])null);
				}
				VehicleRemoveAllPawns.Invoke(pawn, null);
				return false;
			}
			if (!Ext.CanAddPawn(pawn, out var _))
			{
				return false;
			}
			Caravan caravan = CaravanUtility.GetCaravan((Thing)(object)pawn);
			if (caravan != null)
			{
				foreach (Thing item in from item in CaravanInventoryUtility.AllInventoryItems(caravan)
					where CaravanInventoryUtility.GetOwnerOf(caravan, item) == pawn
					select item)
				{
					CaravanInventoryUtility.MoveInventoryToSomeoneElse(pawn, item, caravan.PawnsListForReading, new List<Pawn> { pawn }, item.stackCount);
				}
				if (!GenCollection.Except<Pawn>((IEnumerable<Pawn>)caravan.PawnsListForReading, pawn).Any((Pawn p) => p.RaceProps.Humanlike))
				{
					foreach (Thing item2 in CaravanInventoryUtility.AllInventoryItems(caravan).ToList())
					{
						Pawn ownerOf = CaravanInventoryUtility.GetOwnerOf(caravan, item2);
						containedItems.Add(item2);
						((ThingOwner)ownerOf.inventory.innerContainer).Remove(item2);
					}
				}
				pawn.ownership.UnclaimAll();
				caravan.RemovePawn(pawn);
				if (!GenCollection.Any<Pawn>(caravan.PawnsListForReading, (Predicate<Pawn>)((Pawn p) => p.RaceProps.Humanlike)))
				{
					containedItems.AddRange(caravan.AllThings);
					if (!costPaid)
					{
						List<ThingDefCountClass> costToMake = Ext.CostToMake;
						if (costToMake != null && costToMake.Count > 0)
						{
							List<ThingDefCountClass> costs = ((IEnumerable<ThingDefCountClass>)Ext.CostToMake).Select((Func<ThingDefCountClass, ThingDefCountClass>)((ThingDefCountClass tdcc) => new ThingDefCountClass(tdcc.thingDef, tdcc.count))).ToList();
							containedItems.RemoveAll(delegate(Thing thing)
							{
								ThingDefCountClass val = GenCollection.FirstOrDefault<ThingDefCountClass>(costs, (Predicate<ThingDefCountClass>)((ThingDefCountClass tdcc) => tdcc.thingDef == thing.def));
								if (val == null)
								{
									return false;
								}
								if (val.count > thing.stackCount)
								{
									val.count -= thing.stackCount;
									return true;
								}
								if (val.count < thing.stackCount)
								{
									Thing obj = thing;
									obj.stackCount -= val.count;
									costs.Remove(val);
									return false;
								}
								costs.Remove(val);
								return true;
							});
							if (!GenCollection.Any<ThingDefCountClass>(costs))
							{
								costPaid = true;
							}
						}
					}
					if (!((WorldObject)caravan).Destroyed)
					{
						((WorldObject)caravan).Destroy();
					}
				}
			}
			ThingOwner holdingOwner = ((Thing)pawn).holdingOwner;
			if (holdingOwner != null)
			{
				holdingOwner.Remove((Thing)(object)pawn);
			}
			if (Find.WorldPawns.Contains(pawn))
			{
				Find.WorldPawns.RemovePawn(pawn);
			}
			if (!occupants.Contains(pawn))
			{
				occupants.Add(pawn);
			}
			RecachePawnTraits();
			return true;
		}

		public override void PostRemove()
		{
			((MapParent)this).PostRemove();
			OutpostsMod.Notify_Removed(this);
		}

		public void ConvertToCaravan()
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			Caravan val = CaravanMaker.MakeCaravan((IEnumerable<Pawn>)occupants, ((WorldObject)this).Faction, ((WorldObject)this).Tile, true);
			if (containedItems != null)
			{
				foreach (Thing item in containedItems.Except(val.AllThings))
				{
					val.AddPawnOrItem(item, true);
				}
			}
			if (Find.WorldSelector.IsSelected((WorldObject)(object)this))
			{
				Find.WorldSelector.Select((WorldObject)(object)val, false);
			}
			((WorldObject)this).Destroy();
		}

		public override IEnumerable<Gizmo> GetCaravanGizmos(Caravan caravan)
		{
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Unknown result type (might be due to invalid IL or missing references)
			//IL_004c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0052: Unknown result type (might be due to invalid IL or missing references)
			//IL_0061: Unknown result type (might be due to invalid IL or missing references)
			//IL_0071: Expected O, but got Unknown
			//IL_0071: Unknown result type (might be due to invalid IL or missing references)
			//IL_0076: Unknown result type (might be due to invalid IL or missing references)
			//IL_0088: Unknown result type (might be due to invalid IL or missing references)
			//IL_008e: Unknown result type (might be due to invalid IL or missing references)
			//IL_009d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cd: Expected O, but got Unknown
			//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
			//IL_010a: Unknown result type (might be due to invalid IL or missing references)
			//IL_010f: Unknown result type (might be due to invalid IL or missing references)
			//IL_011e: Unknown result type (might be due to invalid IL or missing references)
			//IL_012e: Expected O, but got Unknown
			return ((WorldObject)this).GetCaravanGizmos(caravan).Append((Gizmo)new Command_Action
			{
				action = delegate
				{
					//IL_0039: Unknown result type (might be due to invalid IL or missing references)
					//IL_0043: Expected O, but got Unknown
					Find.WindowStack.Add((Window)new FloatMenu(((IEnumerable<Pawn>)caravan.PawnsListForReading).Select((Func<Pawn, FloatMenuOption>)delegate(Pawn p)
					{
						//IL_0067: Unknown result type (might be due to invalid IL or missing references)
						//IL_006c: Unknown result type (might be due to invalid IL or missing references)
						//IL_006f: Unknown result type (might be due to invalid IL or missing references)
						//IL_0074: Unknown result type (might be due to invalid IL or missing references)
						//IL_0094: Unknown result type (might be due to invalid IL or missing references)
						//IL_009a: Expected O, but got Unknown
						//IL_0034: Unknown result type (might be due to invalid IL or missing references)
						//IL_003e: Unknown result type (might be due to invalid IL or missing references)
						//IL_0044: Unknown result type (might be due to invalid IL or missing references)
						//IL_005b: Unknown result type (might be due to invalid IL or missing references)
						//IL_0061: Expected O, but got Unknown
						if (Ext.CanAddPawn(p, out var reason))
						{
							TaggedString val = p.NameFullColored;
							val = ((TaggedString)(ref val)).CapitalizeFirst();
							return new FloatMenuOption(((TaggedString)(ref val)).Resolve(), (Action)delegate
							{
								AddPawn(p);
							}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
						}
						return new FloatMenuOption(TaggedString.op_Implicit(p.NameFullColored + " - " + reason), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
					}).ToList()));
				},
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.AddPawn.Label")),
				defaultDesc = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.AddPawn.Desc")),
				icon = (Texture)(object)TexOutposts.AddTex
			}).Append((Gizmo)new Command_Action
			{
				action = delegate
				{
					Find.WindowStack.Add((Window)(object)new Dialog_TakeItems(this, caravan));
				},
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.TakeItems.Label")),
				defaultDesc = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.Commands.TakeItems.Desc", NamedArgument.op_Implicit(Name))),
				icon = (Texture)(object)TexOutposts.RemoveItemsTex
			})
				.Append((Gizmo)new Command_Action
				{
					action = delegate
					{
						Find.WindowStack.Add((Window)(object)new Dialog_GiveItems(this, caravan));
					},
					defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.GiveItems.Label")),
					defaultDesc = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.Commands.GiveItems.Desc", NamedArgument.op_Implicit(caravan.Name))),
					icon = (Texture)(object)TexOutposts.RemoveItemsTex
				});
		}

		[IteratorStateMachine(typeof(<GetGizmos>d__72))]
		public override IEnumerable<Gizmo> GetGizmos()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <GetGizmos>d__72(-2)
			{
				<>4__this = this
			};
		}

		public Pawn RemovePawn(Pawn p)
		{
			Caravan caravan = CaravanUtility.GetCaravan((Thing)(object)p);
			if (caravan != null)
			{
				caravan.RemovePawn(p);
			}
			ThingOwner holdingOwner = ((Thing)p).holdingOwner;
			if (holdingOwner != null)
			{
				holdingOwner.Remove((Thing)(object)p);
			}
			occupants.Remove(p);
			RecachePawnTraits();
			return p;
		}

		public override string GetInspectString()
		{
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			//IL_005a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0064: Unknown result type (might be due to invalid IL or missing references)
			//IL_0069: Unknown result type (might be due to invalid IL or missing references)
			string[] obj = new string[6]
			{
				((MapParent)this).GetInspectString(),
				((Def)((WorldObject)this).def).LabelCap.Line(),
				TranslatorFormattedStringExtensions.Translate("Outposts.Contains", NamedArgument.op_Implicit(occupants.Count)).Line(),
				TranslatorFormattedStringExtensions.Translate("Outposts.Packing", NamedArgument.op_Implicit(ColoredText.Colorize(GenDate.ToStringTicksToPeriodVerbose(ticksTillPacked, true, true), ColoredText.DateTimeColor))).Line(Packing),
				ProductionString().Line(!Packing),
				null
			};
			string input = RelevantSkillDisplay();
			OutpostExtension ext = Ext;
			obj[5] = input.Line(ext != null && ext.RelevantSkills?.Count > 0);
			return string.Concat(obj);
		}

		public void Deliver(IEnumerable<Thing> items)
		{
			//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f6: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
			//IL_0100: Unknown result type (might be due to invalid IL or missing references)
			//IL_01f9: Unknown result type (might be due to invalid IL or missing references)
			//IL_0169: Unknown result type (might be due to invalid IL or missing references)
			//IL_014e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0153: Unknown result type (might be due to invalid IL or missing references)
			//IL_0280: Unknown result type (might be due to invalid IL or missing references)
			//IL_0179: Unknown result type (might be due to invalid IL or missing references)
			//IL_0181: Unknown result type (might be due to invalid IL or missing references)
			//IL_0186: Unknown result type (might be due to invalid IL or missing references)
			//IL_0199: Unknown result type (might be due to invalid IL or missing references)
			//IL_0337: Unknown result type (might be due to invalid IL or missing references)
			//IL_033c: Unknown result type (might be due to invalid IL or missing references)
			//IL_034e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0357: Expected O, but got Unknown
			//IL_03a9: Unknown result type (might be due to invalid IL or missing references)
			//IL_03c0: Unknown result type (might be due to invalid IL or missing references)
			//IL_03c5: Unknown result type (might be due to invalid IL or missing references)
			//IL_03f2: Unknown result type (might be due to invalid IL or missing references)
			//IL_0409: Unknown result type (might be due to invalid IL or missing references)
			//IL_040e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0438: Unknown result type (might be due to invalid IL or missing references)
			//IL_043d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0442: Unknown result type (might be due to invalid IL or missing references)
			//IL_044e: Unknown result type (might be due to invalid IL or missing references)
			//IL_045e: Expected O, but got Unknown
			List<Thing> list = items.ToList();
			Map map = deliveryMap ?? (from m in Find.Maps
				where m.IsPlayerHome
				orderby Find.WorldGrid.ApproxDistanceInTiles(((WorldObject)m.Parent).Tile, ((WorldObject)this).Tile)
				select m).FirstOrDefault();
			if (map == null)
			{
				Log.Warning("Vanilla Outpost Expanded Tried to deliver to a null map, storing instead");
				{
					foreach (Thing item2 in list)
					{
						containedItems.Add(item2);
					}
					return;
				}
			}
			TaggedString val = TranslatorFormattedStringExtensions.Translate("Outposts.Letters.Items.Text", NamedArgument.op_Implicit(Name)) + "\n";
			List<ThingDefCountClass> list2 = new List<ThingDefCountClass>();
			List<Thing> lookAt = new List<Thing>();
			Rot4 rotFromTo = Find.WorldGrid.GetRotFromTo(((WorldObject)map.Parent).Tile, ((WorldObject)this).Tile);
			switch (OutpostsMod.Settings.DeliveryMethod)
			{
			case DeliveryMethod.Teleport:
			{
				Building val2 = default(Building);
				IntVec3 val3 = default(IntVec3);
				if (GenCollection.TryRandomElement<Building>((IEnumerable<Building>)map.listerBuildings.AllBuildingsColonistOfDef(Outposts_DefOf.VEF_OutpostDeliverySpot), ref val2))
				{
					val3 = ((Thing)val2).Position;
				}
				else if (!CellFinder.TryFindRandomEdgeCellWith((Predicate<IntVec3>)((IntVec3 x) => !GridsUtility.Fogged(x, map) && GenGrid.Standable(x, map) && GenCollection.Any<Pawn>(map.mapPawns.FreeColonistsSpawned, (Predicate<Pawn>)((Pawn p) => ReachabilityUtility.CanReach(p, LocalTargetInfo.op_Implicit(x), (PathEndMode)1, (Danger)2, false, false, (TraverseMode)0)))), map, rotFromTo, CellFinder.EdgeRoadChance_Always, ref val3))
				{
					val3 = CellFinder.RandomEdgeCell(rotFromTo, map);
				}
				foreach (Thing item3 in list)
				{
					GenPlace.TryPlaceThing(item3, val3, map, (ThingPlaceMode)1, (Action<Thing, int>)delegate(Thing t, int i)
					{
						lookAt.Add(t);
					}, (Predicate<IntVec3>)null, (Rot4?)null, 1);
				}
				break;
			}
			case DeliveryMethod.PackAnimal:
				Deliver_PackAnimal(list, map, rotFromTo, lookAt);
				break;
			case DeliveryMethod.Store:
				foreach (Thing item4 in list)
				{
					containedItems.Add(item4);
				}
				break;
			case DeliveryMethod.ForcePods:
				Deliver_Pods(list, map, lookAt);
				break;
			case DeliveryMethod.PackOrPods:
				if (Outposts_DefOf.TransportPod.IsFinished)
				{
					Deliver_Pods(list, map, lookAt);
				}
				else
				{
					Deliver_PackAnimal(list, map, rotFromTo, lookAt);
				}
				break;
			default:
				throw new ArgumentOutOfRangeException();
			}
			List<Thing> list3 = new List<Thing>();
			QualityCategory val4 = default(QualityCategory);
			foreach (Thing item in list)
			{
				if (((BuildableDef)item.def).MadeFromStuff || (item.def.useHitPoints && item.HitPoints < item.MaxHitPoints) || QualityUtility.TryGetQuality(item, ref val4))
				{
					list3.Add(item);
					continue;
				}
				ThingDefCountClass val5 = list2.Find((ThingDefCountClass cc) => cc.thingDef == item.def);
				if (val5 == null)
				{
					val5 = new ThingDefCountClass
					{
						thingDef = item.def,
						count = 0
					};
					list2.Add(val5);
				}
				ThingDefCountClass obj = val5;
				obj.count += item.stackCount;
			}
			foreach (Thing item5 in list3)
			{
				val += "  - " + ((Entity)item5).LabelCap + "\n";
			}
			foreach (ThingDefCountClass item6 in list2)
			{
				val += "  - " + item6.Summary + "\n";
			}
			Find.LetterStack.ReceiveLetter(TranslatorFormattedStringExtensions.Translate("Outposts.Letters.Items.Label", NamedArgument.op_Implicit(Name)), val, LetterDefOf.PositiveEvent, new LookTargets((IEnumerable<Thing>)lookAt), (Faction)null, (Quest)null, (List<ThingDef>)null, (string)null, 0, true);
		}

		private static void Deliver_Pods(IEnumerable<Thing> items, Map map, List<Thing> lookAt)
		{
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			//IL_0040: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			Building val = default(Building);
			IntVec3 val2;
			if (GenCollection.TryRandomElement<Building>((IEnumerable<Building>)map.listerBuildings.AllBuildingsColonistOfDef(Outposts_DefOf.VEF_OutpostDeliverySpot), ref val))
			{
				lookAt.Add((Thing)(object)val);
				val2 = ((Thing)val).Position;
			}
			else
			{
				val2 = DropCellFinder.TradeDropSpot(map);
			}
			IntVec3 val3 = default(IntVec3);
			foreach (Thing item in items)
			{
				if (!DropCellFinder.TryFindDropSpotNear(val2, map, ref val3, false, false, false, (IntVec2?)null, true))
				{
					val3 = DropCellFinder.RandomDropSpot(map, true);
				}
				TradeUtility.SpawnDropPod(val3, map, item);
			}
		}

		private void Deliver_PackAnimal(IEnumerable<Thing> items, Map map, Rot4 dir, List<Thing> lookAt)
		{
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0082: Unknown result type (might be due to invalid IL or missing references)
			//IL_0089: Unknown result type (might be due to invalid IL or missing references)
			//IL_008e: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
			//IL_0127: Unknown result type (might be due to invalid IL or missing references)
			//IL_012c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0160: Unknown result type (might be due to invalid IL or missing references)
			//IL_0155: Unknown result type (might be due to invalid IL or missing references)
			//IL_015a: Unknown result type (might be due to invalid IL or missing references)
			PawnKindDef muffalo = default(PawnKindDef);
			if (!GenCollection.TryRandomElement<PawnKindDef>(((WorldObject)this).Biome.AllWildAnimals.Where((PawnKindDef x) => x.RaceProps.packAnimal), ref muffalo))
			{
				muffalo = PawnKindDefOf.Muffalo;
			}
			IntVec3 val = default(IntVec3);
			if (!CellFinder.TryFindRandomEdgeCellWith((Predicate<IntVec3>)((IntVec3 x) => !GridsUtility.Fogged(x, map) && GenGrid.Standable(x, map)), map, dir, CellFinder.EdgeRoadChance_Always, ref val) && !RCellFinder.TryFindRandomPawnEntryCell(ref val, map, CellFinder.EdgeRoadChance_Always, false, (Predicate<IntVec3>)null))
			{
				val = CellFinder.RandomEdgeCell(dir, map);
			}
			Pawn animal = PawnGenerator.GeneratePawn(muffalo, Faction.OfPlayer, (PlanetTile?)null);
			lookAt.Add((Thing)(object)animal);
			foreach (Thing item in items)
			{
				animal.inventory.TryAddItemNotForSale(item);
			}
			GenSpawn.Spawn((Thing)(object)animal, val, map, (WipeMode)0);
			Building val2 = default(Building);
			IntVec3 deliverLoc = default(IntVec3);
			if (GenCollection.TryRandomElement<Building>((IEnumerable<Building>)map.listerBuildings.AllBuildingsColonistOfDef(Outposts_DefOf.VEF_OutpostDeliverySpot), ref val2))
			{
				deliverLoc = ((Thing)val2).Position;
			}
			else if (!RCellFinder.TryFindRandomSpotJustOutsideColony(animal, ref deliverLoc))
			{
				deliverLoc = CellFinderLoose.RandomCellWith((Predicate<IntVec3>)((IntVec3 x) => !GridsUtility.Fogged(x, map) && GenGrid.Standable(x, map) && ReachabilityUtility.CanReach(animal, LocalTargetInfo.op_Implicit(x), (PathEndMode)1, (Danger)3, false, false, (TraverseMode)0)), map, 1000);
			}
			LordMaker.MakeNewLord(Faction.OfPlayer, (LordJob)(object)new LordJob_Deliver(deliverLoc), map, (IEnumerable<Pawn>)(object)new Pawn[1] { animal });
		}

		public virtual void SatisfyNeeds()
		{
			for (int i = 0; i < occupants.Count; i++)
			{
				SatisfyNeeds(occupants[i]);
			}
		}

		public virtual void SatisfyNeedsInterval(int delta)
		{
			for (int i = 0; i < occupants.Count; i++)
			{
				SatisfyNeedsInterval(occupants[i], delta);
			}
		}

		public virtual void SatisfyNeeds(Pawn pawn)
		{
			if (pawn != null && !((Thing)pawn).Spawned && !pawn.Dead)
			{
				OutpostHealthTick(pawn);
				if (pawn.Dead)
				{
					occupants.Remove(pawn);
					containedItems.Add((Thing)(object)pawn.Corpse);
				}
			}
		}

		public virtual void SatisfyNeedsInterval(Pawn pawn, int delta)
		{
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			//IL_0024: Unknown result type (might be due to invalid IL or missing references)
			if (pawn == null || ((Thing)pawn).Spawned || pawn.Dead)
			{
				return;
			}
			if (GenLocalDate.HourInteger(((WorldObject)this).Tile) >= 23 || GenLocalDate.HourInteger(((WorldObject)this).Tile) <= 5)
			{
				Pawn_NeedsTracker needs = pawn.needs;
				if (needs != null)
				{
					Need_Rest rest = needs.rest;
					if (rest != null)
					{
						rest.TickResting(0.75f * (float)delta);
					}
				}
			}
			Pawn_AgeTracker ageTracker = pawn.ageTracker;
			if (ageTracker != null)
			{
				ageTracker.AgeTickInterval(delta);
			}
			OutpostHealthTickInterval(pawn, delta);
			if (!Gen.IsHashIntervalTick((Thing)(object)pawn, 300, delta))
			{
				return;
			}
			Need_Food val = pawn.needs?.food;
			if (val != null && ((Need)val).CurLevelPercentage <= pawn.RaceProps.FoodLevelPercentageWantEat)
			{
				ThingDef providedFood = ProvidedFood;
				if (providedFood != null && providedFood.IsNutritionGivingIngestible && ProvidedFood.ingestible.HumanEdible)
				{
					Thing val2 = ThingMaker.MakeThing(ProvidedFood, (ThingDef)null);
					if (val2.IngestibleNow && pawn.RaceProps.CanEverEat(val2))
					{
						((Need)val).CurLevel = ((Need)val).CurLevel + val2.Ingested(pawn, val.NutritionWanted);
					}
				}
			}
			if (pawn.needs == null)
			{
				return;
			}
			foreach (Need need in pawn.needs.needs)
			{
				if ((need is Need_Chemical || need is Need_Chemical_Any) ? true : false)
				{
					need.CurLevel = need.MaxLevel;
				}
			}
		}

		public virtual void OutpostHealthTick(Pawn pawn)
		{
			if (pawn.health?.hediffSet == null || pawn.Dead)
			{
				return;
			}
			bool flag = false;
			Pawn_HealthTracker health = pawn.health;
			for (int num = health.hediffSet.hediffs.Count - 1; num >= 0; num--)
			{
				Hediff val = health.hediffSet.hediffs[num];
				if ((val is Hediff_ChemicalDependency || val is Hediff_Addiction) ? true : false)
				{
					val.Severity = 0f;
				}
				else
				{
					try
					{
						val.Tick();
						val.PostTick();
					}
					catch
					{
						health.RemoveHediff(val);
					}
				}
				if (pawn.Dead)
				{
					return;
				}
				if (val.ShouldRemove)
				{
					health.hediffSet.hediffs.RemoveAt(num);
					val.PostRemoved();
					flag = true;
				}
			}
			if (flag)
			{
				health.Notify_HediffChanged((Hediff)null);
			}
		}

		public virtual void OutpostHealthTickInterval(Pawn pawn, int delta)
		{
			//IL_01d9: Unknown result type (might be due to invalid IL or missing references)
			//IL_0212: Unknown result type (might be due to invalid IL or missing references)
			//IL_0219: Expected O, but got Unknown
			if (pawn.health?.hediffSet == null || pawn.Dead)
			{
				return;
			}
			bool flag = false;
			Pawn_HealthTracker health = pawn.health;
			for (int num = health.hediffSet.hediffs.Count - 1; num >= 0; num--)
			{
				Hediff val = health.hediffSet.hediffs[num];
				if ((!(val is Hediff_ChemicalDependency) && !(val is Hediff_Addiction)) || 1 == 0)
				{
					try
					{
						val.TickInterval(delta);
						val.PostTickInterval(delta);
					}
					catch
					{
						health.RemoveHediff(val);
					}
				}
				if (pawn.Dead)
				{
					return;
				}
				if (val.ShouldRemove)
				{
					health.hediffSet.hediffs.RemoveAt(num);
					val.PostRemoved();
					flag = true;
				}
			}
			if (flag)
			{
				health.Notify_HediffChanged((Hediff)null);
				flag = false;
			}
			health.immunity.ImmunityHandlerTickInterval(delta);
			if (Gen.IsHashIntervalTick((Thing)(object)pawn, 600, delta))
			{
				if (pawn.health.HasHediffsNeedingTend(false))
				{
					Pawn val2 = GenCollection.MaxBy<Pawn, float>(AllPawns.Where((Pawn p) => p.RaceProps.Humanlike && !p.Downed), (Func<Pawn, float>)delegate(Pawn p)
					{
						Pawn_SkillTracker skills = p.skills;
						int? obj2;
						if (skills == null)
						{
							obj2 = null;
						}
						else
						{
							SkillRecord skill = skills.GetSkill(SkillDefOf.Medicine);
							obj2 = ((skill != null) ? new int?(skill.Level) : ((int?)null));
						}
						return ((float?)obj2) ?? (-1f);
					});
					if (val2 != null)
					{
						Medicine val3 = null;
						float num2 = 0f;
						CheckNoDestroyedOrNoStack();
						foreach (Thing item in containedItems.ToList())
						{
							if (item.def.IsMedicine && (pawn.playerSettings == null || MedicalCareUtility.AllowsMedicine(pawn.playerSettings.medCare, item.def)))
							{
								float statValue = StatExtension.GetStatValue(item, StatDefOf.MedicalPotency, true, -1);
								if (statValue > num2 || val3 == null)
								{
									num2 = statValue;
									val3 = (Medicine)TakeItem(item);
								}
							}
						}
						TendUtility.DoTend(val2, pawn, val3);
					}
				}
				if (pawn.health.hediffSet.HasNaturallyHealingInjury())
				{
					float num3 = 16f;
					foreach (Hediff hediff in pawn.health.hediffSet.hediffs)
					{
						HediffStage curStage = hediff.CurStage;
						if (curStage != null && curStage.naturalHealingFactor != -1f)
						{
							num3 *= curStage.naturalHealingFactor;
						}
					}
					pawn.health.hediffSet.GetHediffs<Hediff_Injury>(ref tmpHediffInjuries, (Predicate<Hediff_Injury>)((Hediff_Injury x) => HediffUtility.CanHealNaturally(x)));
					Hediff_Injury val4 = GenCollection.RandomElement<Hediff_Injury>((IEnumerable<Hediff_Injury>)tmpHediffInjuries);
					((Hediff)val4).Heal(num3 * pawn.HealthScale * 0.01f * StatExtension.GetStatValue((Thing)(object)pawn, StatDefOf.InjuryHealingFactor, true, -1));
					if (((Hediff)val4).ShouldRemove)
					{
						pawn.health.hediffSet.hediffs.Remove((Hediff)(object)val4);
						((Hediff)val4).PostRemoved();
						flag = true;
					}
				}
				if (pawn.health.hediffSet.HasTendedAndHealingInjury())
				{
					pawn.health.hediffSet.GetHediffs<Hediff_Injury>(ref tmpHediffInjuries, (Predicate<Hediff_Injury>)((Hediff_Injury x) => HediffUtility.CanHealFromTending(x)));
					Hediff_Injury val5 = GenCollection.RandomElement<Hediff_Injury>((IEnumerable<Hediff_Injury>)tmpHediffInjuries);
					((Hediff)val5).Heal(0.08f * GenMath.LerpDouble(0f, 1f, 0.5f, 1.5f, Mathf.Clamp01(HediffUtility.TryGetComp<HediffComp_TendDuration>((Hediff)(object)val5).tendQuality)) * pawn.HealthScale * StatExtension.GetStatValue((Thing)(object)pawn, StatDefOf.InjuryHealingFactor, true, -1));
					if (((Hediff)val5).ShouldRemove)
					{
						pawn.health.hediffSet.hediffs.Remove((Hediff)(object)val5);
						((Hediff)val5).PostRemoved();
						flag = true;
					}
				}
				if (flag)
				{
					pawn.health.Notify_HediffChanged((Hediff)null);
				}
			}
			if (!Gen.IsHashIntervalTick((Thing)(object)pawn, 15, delta) || !pawn.health.hediffSet.HasRegeneration)
			{
				return;
			}
			float num4 = 0f;
			foreach (Hediff hediff2 in pawn.health.hediffSet.hediffs)
			{
				HediffStage curStage2 = hediff2.CurStage;
				if (curStage2 != null && curStage2.regeneration != -1f)
				{
					num4 += curStage2.regeneration;
				}
			}
			num4 *= 0.00025f;
			if (!(num4 > 0f))
			{
				return;
			}
			pawn.health.hediffSet.GetHediffs<Hediff_Injury>(ref tmpHediffInjuries, (Predicate<Hediff_Injury>)null);
			foreach (Hediff_Injury tmpHediffInjury in tmpHediffInjuries)
			{
				float num5 = Mathf.Min(num4, ((Hediff)tmpHediffInjury).Severity);
				num4 -= num5;
				((Hediff)tmpHediffInjury).Heal(num5);
				pawn.health.hediffSet.Notify_Regenerated(num5);
				if (num4 <= 0f)
				{
					break;
				}
			}
			if (!(num4 > 0f))
			{
				return;
			}
			pawn.health.hediffSet.GetHediffs<Hediff_MissingPart>(ref tmpHediffMissing, (Predicate<Hediff_MissingPart>)((Hediff_MissingPart hediff) => ((Hediff)hediff).Part.parent != null && !GenCollection.Any<Hediff_MissingPart>(tmpHediffMissing, (Predicate<Hediff_MissingPart>)((Hediff_MissingPart x) => ((Hediff)x).Part == ((Hediff)hediff).Part.parent)) && pawn.health.hediffSet.GetFirstHediffMatchingPart<Hediff_MissingPart>(((Hediff)hediff).Part.parent) == null && pawn.health.hediffSet.GetFirstHediffMatchingPart<Hediff_AddedPart>(((Hediff)hediff).Part.parent) == null));
			Hediff_MissingPart val6 = default(Hediff_MissingPart);
			if (GenCollection.TryRandomElement<Hediff_MissingPart>((IEnumerable<Hediff_MissingPart>)tmpHediffMissing, ref val6))
			{
				BodyPartRecord part = ((Hediff)val6).Part;
				pawn.health.RemoveHediff((Hediff)(object)val6);
				Hediff val7 = pawn.health.AddHediff(HediffDefOf.Misc, part, (DamageInfo?)null, (DamageResult)null);
				float partHealth = pawn.health.hediffSet.GetPartHealth(part);
				val7.Severity = Mathf.Max(partHealth - 1f, partHealth * 0.9f);
				pawn.health.hediffSet.Notify_Regenerated(partHealth - val7.Severity);
			}
		}

		public int TotalSkill(SkillDef skill)
		{
			if (skillsDirty)
			{
				foreach (SkillDef allDef in DefDatabase<SkillDef>.AllDefs)
				{
					totalSkills[allDef] = CapablePawns.Sum((Pawn p) => p.skills.GetSkill(skill).Level);
				}
			}
			return totalSkills[skill];
		}

		protected virtual bool IsCapable(Pawn pawn)
		{
			if (!pawn.RaceProps.Humanlike)
			{
				return false;
			}
			if (pawn.skills == null)
			{
				return false;
			}
			return !GenCollection.Any<SkillDef>(Ext.RelevantSkills, (Predicate<SkillDef>)((SkillDef skill) => pawn.skills.GetSkill(skill).TotallyDisabled));
		}

		public bool Has(Pawn pawn)
		{
			return occupants.Contains(pawn);
		}

		public void CheckNoDestroyedOrNoStack()
		{
			if (!GenCollection.Any<Thing>(containedItems, (Predicate<Thing>)((Thing x) => x.Destroyed || x.stackCount == 0)))
			{
				return;
			}
			foreach (Thing item in containedItems.Where((Thing x) => x.Destroyed || x.stackCount == 0).ToList())
			{
				containedItems.Remove(item);
			}
		}

		public virtual string ProductionString()
		{
			//IL_0051: Unknown result type (might be due to invalid IL or missing references)
			//IL_0067: Unknown result type (might be due to invalid IL or missing references)
			//IL_0072: Unknown result type (might be due to invalid IL or missing references)
			//IL_0077: Unknown result type (might be due to invalid IL or missing references)
			//IL_007c: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
			//IL_0103: Unknown result type (might be due to invalid IL or missing references)
			//IL_0119: Unknown result type (might be due to invalid IL or missing references)
			//IL_013b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0140: Unknown result type (might be due to invalid IL or missing references)
			//IL_0145: Unknown result type (might be due to invalid IL or missing references)
			List<ResultOption> resultOptions = ResultOptions;
			if (Ext == null || resultOptions == null || resultOptions.Count <= 0)
			{
				return "";
			}
			TaggedString val;
			switch (resultOptions.Count)
			{
			case 1:
				val = TranslatorFormattedStringExtensions.Translate("Outposts.WillProduce.1", NamedArgument.op_Implicit(resultOptions[0].Amount(CapablePawns.ToList())), NamedArgument.op_Implicit(((Def)resultOptions[0].Thing).label), NamedArgument.op_Implicit(TimeTillProduction));
				return ((TaggedString)(ref val)).RawText;
			case 2:
				val = TranslatorFormattedStringExtensions.Translate("Outposts.WillProduce.2", NamedArgument.op_Implicit(resultOptions[0].Amount(CapablePawns.ToList())), NamedArgument.op_Implicit(((Def)resultOptions[0].Thing).label), NamedArgument.op_Implicit(resultOptions[1].Amount(CapablePawns.ToList())), NamedArgument.op_Implicit(((Def)resultOptions[1].Thing).label), NamedArgument.op_Implicit(TimeTillProduction));
				return ((TaggedString)(ref val)).RawText;
			default:
				val = TranslatorFormattedStringExtensions.Translate("Outposts.WillProduce.N", NamedArgument.op_Implicit(TimeTillProduction), NamedArgument.op_Implicit(GenText.ToLineList(resultOptions.Select((ResultOption ro) => ro.Explain(CapablePawns.ToList())), "  - ", false)));
				return ((TaggedString)(ref val)).RawText;
			}
		}

		public virtual string RelevantSkillDisplay()
		{
			return GenText.ToLineList(Ext.RelevantSkills.Select(delegate(SkillDef skill)
			{
				//IL_000b: Unknown result type (might be due to invalid IL or missing references)
				//IL_0017: Unknown result type (might be due to invalid IL or missing references)
				//IL_001c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0021: Unknown result type (might be due to invalid IL or missing references)
				TaggedString val = TranslatorFormattedStringExtensions.Translate("Outposts.TotalSkill", NamedArgument.op_Implicit(skill.skillLabel), NamedArgument.op_Implicit(TotalSkill(skill)));
				return ((TaggedString)(ref val)).RawText;
			}), (string)null, false);
		}

		[CompilerGenerated]
		[DebuggerHidden]
		private IEnumerable<Gizmo> <>n__0()
		{
			return ((MapParent)this).GetGizmos();
		}
	}
	public class OutpostExtension : DefModExtension
	{
		public List<BiomeDef> AllowedBiomes;

		public List<ThingDefCountClass> CostToMake;

		public List<BiomeDef> DisallowedBiomes;

		public List<SkillDef> DisplaySkills;

		public HistoryEventDef Event;

		[PostToSetings("Outposts.Setting.MinimumPawns", PostToSetingsAttribute.DrawMode.IntSlider, null, 1f, 10f, null, 0)]
		public int MinPawns;

		public ThingDef ProvidedFood;

		[PostToSetings("Outposts.Setting.Range", PostToSetingsAttribute.DrawMode.IntSlider, null, 1f, 30f, null, -1)]
		public int Range = -1;

		public List<AmountBySkill> RequiredSkills;

		public bool RequiresGrowing;

		public List<ResultOption> ResultOptions;

		[PostToSetings("Outposts.Setting.ProductionTime", PostToSetingsAttribute.DrawMode.Time, null, 0f, 0f, null, -1)]
		public int TicksPerProduction = 900000;

		[PostToSetings("Outposts.Setting.PackTime", PostToSetingsAttribute.DrawMode.Time, null, 0f, 0f, null, null)]
		public int TicksToPack = 420000;

		public int TicksToSetUp = -1;

		public List<SkillDef> RelevantSkills => new HashSet<SkillDef>(RequiredSkills.SelectOrEmpty((AmountBySkill rq) => rq.Skill).Concat(ResultOptions.SelectManyOrEmpty((ResultOption ro) => ro.AmountsPerSkills.SelectOrEmpty((AmountBySkill aps) => aps.Skill).Concat(ro.MinSkills.SelectOrEmpty((AmountBySkill ms) => ms.Skill)))).Concat(DisplaySkills.OrEmpty())).ToList();
	}
	public class ResultOption
	{
		public int AmountPerPawn;

		public List<AmountBySkill> AmountsPerSkills;

		public int BaseAmount;

		public List<AmountBySkill> MinSkills;

		public ThingDef Thing;

		public int Amount(List<Pawn> pawns)
		{
			return Mathf.RoundToInt((float)(BaseAmount + AmountPerPawn * pawns.Count + (AmountsPerSkills?.Sum((AmountBySkill x) => x.Amount(pawns)) ?? 0)) * OutpostsMod.Settings.ProductionMultiplier);
		}

		public IEnumerable<Thing> Make(List<Pawn> pawns)
		{
			return Thing.Make(Amount(pawns));
		}

		public string Explain(List<Pawn> pawns)
		{
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			return $"{Amount(pawns)}x {((Def)Thing).LabelCap}";
		}
	}
	public class AmountBySkill
	{
		public int Count;

		public SkillDef Skill;

		public void LoadDataFromXmlCustom(XmlNode xmlRoot)
		{
			if (xmlRoot.ChildNodes.Count != 1)
			{
				Log.Error("Misconfigured AmountBySkill: " + xmlRoot.OuterXml);
				return;
			}
			DirectXmlCrossRefLoader.RegisterObjectWantsCrossRef((object)this, "Skill", xmlRoot.Name, (string)null, (string)null, (Type)null);
			Count = ParseHelper.FromString<int>(xmlRoot.FirstChild.Value);
		}

		public int Amount(List<Pawn> pawns)
		{
			return Count * pawns.Sum((Pawn p) => p.skills.GetSkill(Skill).Level);
		}
	}
	public class OutpostsMod : Mod
	{
		public static List<WorldObjectDef> Outposts;

		public static Harmony Harm;

		public static OutpostsSettings Settings;

		private static Dictionary<Type, List<FieldInfo>> editableFields;

		private float prevHeight = float.MaxValue;

		private Vector2 scrollPos;

		private Dictionary<WorldObjectDef, float> sectionHeights;

		public OutpostsMod(ModContentPack content)
			: base(content)
		{
			LongEventHandler.ExecuteWhenFinished((Action)FindOutposts);
			Settings = ((Mod)this).GetSettings<OutpostsSettings>();
			editableFields = new Dictionary<Type, List<FieldInfo>>();
			foreach (Type item in GenCollection.Concat<Type>(GenCollection.Concat<Type>((IEnumerable<Type>)GenTypes.AllSubclasses(typeof(Outpost)), typeof(Outpost)), typeof(OutpostExtension)).Concat(GenTypes.AllSubclasses(typeof(OutpostExtension))))
			{
				editableFields[item] = new List<FieldInfo>();
				FieldInfo[] fields = item.GetFields(AccessTools.all);
				foreach (FieldInfo fieldInfo in fields)
				{
					if (GenAttribute.HasAttribute<PostToSetingsAttribute>((MemberInfo)fieldInfo))
					{
						editableFields[item].Add(fieldInfo);
					}
				}
			}
		}

		private void FindOutposts()
		{
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_0042: Expected O, but got Unknown
			Outposts = DefDatabase<WorldObjectDef>.AllDefs.Where((WorldObjectDef def) => typeof(Outpost).IsAssignableFrom(def.worldObjectClass)).ToList();
			Harm = new Harmony("vanillaexpanded.outposts");
			sectionHeights = Outposts.ToDictionary((WorldObjectDef o) => o, (WorldObjectDef _) => float.MaxValue);
			if (GenCollection.Any<WorldObjectDef>(Outposts))
			{
				HarmonyPatches.DoPatches();
				((BuildableDef)Outposts_DefOf.VEF_OutpostDeliverySpot).designationCategory = DefDatabase<DesignationCategoryDef>.GetNamed("Misc", true);
			}
		}

		public static void Notify_Spawned(Outpost outpost)
		{
			Setup(outpost);
		}

		private static void Setup(Outpost outpost)
		{
			OutpostsSettings.OutpostSettings outpostSettings = Settings.SettingsFor(((Def)((WorldObject)outpost).def).defName);
			PostToSetingsAttribute postToSetingsAttribute = default(PostToSetingsAttribute);
			foreach (FieldInfo item in editableFields[((object)outpost).GetType()])
			{
				if (GenAttribute.TryGetAttribute<PostToSetingsAttribute>((MemberInfo)item, ref postToSetingsAttribute))
				{
					item.SetValue(outpost, outpostSettings.TryGet(item.DeclaringType.Name + "." + item.Name, item.FieldType, out var value) ? value : (postToSetingsAttribute.Default ?? item.GetValue(outpost)));
				}
			}
			PostToSetingsAttribute postToSetingsAttribute2 = default(PostToSetingsAttribute);
			foreach (FieldInfo item2 in editableFields[((object)outpost.Ext).GetType()])
			{
				if (GenAttribute.TryGetAttribute<PostToSetingsAttribute>((MemberInfo)item2, ref postToSetingsAttribute2))
				{
					item2.SetValue(outpost.Ext, outpostSettings.TryGet(item2.DeclaringType.Name + "." + item2.Name, item2.FieldType, out var value2) ? value2 : (item2.GetValue(outpost.Ext) ?? postToSetingsAttribute2.Default));
				}
			}
		}

		public static void Notify_Removed(Outpost outpost)
		{
		}

		public override string SettingsCategory()
		{
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			return TaggedString.op_Implicit(GenCollection.Any<WorldObjectDef>(Outposts) ? Translator.Translate("Outposts.Settings.Title") : TaggedString.op_Implicit((string)null));
		}

		public override void DoSettingsWindowContents(Rect inRect)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Expected O, but got Unknown
			//IL_0040: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			//IL_006b: Unknown result type (might be due to invalid IL or missing references)
			//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
			//IL_00af: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
			//IL_010d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0163: Unknown result type (might be due to invalid IL or missing references)
			//IL_016d: Expected O, but got Unknown
			//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
			//IL_01bc: Unknown result type (might be due to invalid IL or missing references)
			((Mod)this).DoSettingsWindowContents(inRect);
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(0f, 0f, ((Rect)(ref inRect)).width - 20f, prevHeight);
			Widgets.BeginScrollView(inRect, ref scrollPos, val, true);
			Listing_Standard val2 = new Listing_Standard();
			((Listing)val2).Begin(val);
			val2.Label(TranslatorFormattedStringExtensions.Translate("Outposts.Settings.Multiplier.Production", NamedArgument.op_Implicit(GenText.ToStringPercent(Settings.ProductionMultiplier))), -1f, (string)null);
			Settings.ProductionMultiplier = val2.Slider(Settings.ProductionMultiplier, 0.1f, 10f);
			val2.Label(TranslatorFormattedStringExtensions.Translate("Outposts.Settings.Multiplier.Time", NamedArgument.op_Implicit(GenText.ToStringPercent(Settings.TimeMultiplier))), -1f, (string)null);
			Settings.TimeMultiplier = val2.Slider(Settings.TimeMultiplier, 0.01f, 5f);
			if (val2.ButtonTextLabeled(TaggedString.op_Implicit(Translator.Translate("Outposts.Settings.DeliveryMethod")), TaggedString.op_Implicit(Translator.Translate($"Outposts.Settings.DeliveryMethod.{Settings.DeliveryMethod}")), (TextAnchor)0, (string)null, (string)null))
			{
				Find.WindowStack.Add((Window)new FloatMenu(Enum.GetValues(typeof(DeliveryMethod)).OfType<DeliveryMethod>().Select((Func<DeliveryMethod, FloatMenuOption>)((DeliveryMethod method) => new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate($"Outposts.Settings.DeliveryMethod.{method}")), (Action)delegate
				{
					Settings.DeliveryMethod = method;
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0)))
					.ToList()));
			}
			((Listing)val2).GapLine(12f);
			foreach (WorldObjectDef outpost in Outposts)
			{
				Listing_Standard val3 = val2.BeginSection(sectionHeights[outpost], 4f, 4f);
				val3.Label(((Def)outpost).LabelCap, -1f, (string)null);
				OutpostsSettings.OutpostSettings settings2 = Settings.SettingsFor(((Def)outpost).defName);
				foreach (FieldInfo item in editableFields[outpost.worldObjectClass])
				{
					DoSetting(val3, settings2, item);
				}
				OutpostExtension modExtension = ((Def)outpost).GetModExtension<OutpostExtension>();
				if (modExtension != null)
				{
					foreach (FieldInfo item2 in editableFields[((object)modExtension).GetType()])
					{
						DoSetting(val3, settings2, item2, modExtension);
					}
				}
				sectionHeights[outpost] = ((Listing)val3).CurHeight;
				val2.EndSection(val3);
				((Listing)val2).Gap(12f);
			}
			prevHeight = ((Listing)val2).CurHeight;
			((Listing)val2).End();
			Widgets.EndScrollView();
			static void DoSetting(Listing_Standard listing, OutpostsSettings.OutpostSettings settings, FieldInfo info, object obj = null)
			{
				PostToSetingsAttribute postToSetingsAttribute = default(PostToSetingsAttribute);
				if (GenAttribute.TryGetAttribute<PostToSetingsAttribute>((MemberInfo)info, ref postToSetingsAttribute))
				{
					string key = info.DeclaringType.Name + "." + info.Name;
					object value;
					object current4 = (settings.TryGet(key, info.FieldType, out value) ? value : ((obj == null) ? postToSetingsAttribute.Default : info.GetValue(obj)));
					postToSetingsAttribute.Draw(listing, ref current4);
					if (current4 == postToSetingsAttribute.Default)
					{
						if (settings.Has(key))
						{
							settings.Remove(key);
						}
					}
					else
					{
						settings.Set(key, current4);
					}
				}
			}
		}

		public override void WriteSettings()
		{
			((Mod)this).WriteSettings();
			if (Find.World?.worldObjects == null)
			{
				return;
			}
			foreach (Outpost item in Find.World.worldObjects.AllWorldObjects.OfType<Outpost>())
			{
				Setup(item);
			}
		}
	}
	public class PostToSetingsAttribute : Attribute
	{
		public enum DrawMode
		{
			Checkbox,
			IntSlider,
			Slider,
			Percentage,
			Time
		}

		private readonly object ignore;

		private readonly float max;

		private readonly float min;

		private readonly bool shouldIgnore;

		public object Default;

		public string LabelKey;

		public DrawMode Mode;

		public string TooltipKey;

		public PostToSetingsAttribute(string label, DrawMode mode, object value = null, float min = 0f, float max = 0f, string tooltip = null, object dontShowAt = null)
		{
			LabelKey = label;
			Mode = mode;
			Default = value;
			this.min = min;
			this.max = max;
			TooltipKey = tooltip;
			ignore = dontShowAt;
			shouldIgnore = dontShowAt != null;
		}

		public void Draw(Listing_Standard listing, ref object current)
		{
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0175: Unknown result type (might be due to invalid IL or missing references)
			//IL_017f: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
			//IL_0121: Unknown result type (might be due to invalid IL or missing references)
			//IL_012b: Unknown result type (might be due to invalid IL or missing references)
			//IL_013c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0147: Unknown result type (might be due to invalid IL or missing references)
			//IL_01df: Unknown result type (might be due to invalid IL or missing references)
			//IL_01e9: Unknown result type (might be due to invalid IL or missing references)
			//IL_01fc: Unknown result type (might be due to invalid IL or missing references)
			//IL_0207: Unknown result type (might be due to invalid IL or missing references)
			//IL_006e: Unknown result type (might be due to invalid IL or missing references)
			//IL_01ab: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
			//IL_0087: Unknown result type (might be due to invalid IL or missing references)
			if (shouldIgnore && object.Equals(current, ignore))
			{
				return;
			}
			switch (Mode)
			{
			case DrawMode.Checkbox:
			{
				bool flag = (bool)current;
				string text = TaggedString.op_Implicit(Translator.Translate(LabelKey));
				string tooltipKey = TooltipKey;
				TaggedString? val = ((tooltipKey != null) ? new TaggedString?(Translator.Translate(tooltipKey)) : ((TaggedString?)null));
				listing.CheckboxLabeled(text, ref flag, val.HasValue ? TaggedString.op_Implicit(val.GetValueOrDefault()) : null, 0f, 1f);
				if (flag != (bool)current)
				{
					current = flag;
				}
				break;
			}
			case DrawMode.Slider:
				listing.Label(TaggedString.op_Implicit(Translator.Translate(LabelKey) + ": ") + current, -1f, (TipSignal?)null);
				current = listing.Slider((float)current, min, max);
				break;
			case DrawMode.Percentage:
				listing.Label(Translator.Translate(LabelKey) + ": " + GenText.ToStringPercent((float)current), -1f, (string)null);
				current = listing.Slider((float)current, min, max);
				break;
			case DrawMode.IntSlider:
				listing.Label(TaggedString.op_Implicit(Translator.Translate(LabelKey) + ": ") + current, -1f, (TipSignal?)null);
				current = (int)listing.Slider((float)(int)current, (float)(int)min, (float)(int)max);
				break;
			case DrawMode.Time:
				listing.Label(Translator.Translate(LabelKey) + ": " + GenDate.ToStringTicksToPeriodVerbose((int)current, true, true), -1f, (string)null);
				current = (int)listing.Slider((float)(int)current, 2500f, 3600000f);
				break;
			default:
				throw new ArgumentOutOfRangeException();
			}
		}
	}
	public class OutpostsSettings : ModSettings
	{
		public class OutpostSettings : IExposable
		{
			private Dictionary<string, string> dictionary = new Dictionary<string, string>();

			public void ExposeData()
			{
				Scribe_Collections.Look<string, string>(ref dictionary, "keysToValues", (LookMode)1, (LookMode)1);
			}

			public bool Has(string key)
			{
				return dictionary.ContainsKey(key);
			}

			public void Remove(string key)
			{
				dictionary.Remove(key);
			}

			public bool TryGet(string key, Type type, out object value)
			{
				if (dictionary == null)
				{
					dictionary = new Dictionary<string, string>();
				}
				if (Has(key))
				{
					value = ParseHelper.FromString(dictionary[key], type);
					return true;
				}
				value = null;
				return false;
			}

			public void Set(string key, object value)
			{
				GenCollection.SetOrAdd<string, string>(dictionary, key, value.ToString());
			}
		}

		public DeliveryMethod DeliveryMethod;

		public float ProductionMultiplier = 1f;

		public Dictionary<string, OutpostSettings> SettingsPerOutpost = new Dictionary<string, OutpostSettings>();

		public float TimeMultiplier = 1f;

		public OutpostSettings SettingsFor(string defName)
		{
			if (SettingsPerOutpost == null)
			{
				SettingsPerOutpost = new Dictionary<string, OutpostSettings>();
			}
			if (!SettingsPerOutpost.TryGetValue(defName, out var value) || value == null)
			{
				GenCollection.SetOrAdd<string, OutpostSettings>(SettingsPerOutpost, defName, value = new OutpostSettings());
			}
			return value;
		}

		public override void ExposeData()
		{
			((ModSettings)this).ExposeData();
			Scribe_Values.Look<float>(ref ProductionMultiplier, "productionMultiplier", 1f, false);
			Scribe_Values.Look<float>(ref TimeMultiplier, "timeMultiplier", 1f, false);
			Scribe_Values.Look<DeliveryMethod>(ref DeliveryMethod, "deliveryMethod", DeliveryMethod.Teleport, false);
			Scribe_Collections.Look<string, OutpostSettings>(ref SettingsPerOutpost, "settingsPerOutpost", (LookMode)1, (LookMode)2);
		}
	}
	[DefOf]
	public class Outposts_DefOf
	{
		public static ThingDef VEF_OutpostDeliverySpot;

		public static DutyDef VEF_DropAllInInventory;

		public static ResearchProjectDef TransportPod;
	}
	public enum DeliveryMethod
	{
		Teleport,
		PackAnimal,
		Store,
		ForcePods,
		PackOrPods
	}
	[StaticConstructorOnStartup]
	public static class TexOutposts
	{
		public static readonly Texture2D PackTex = ContentFinder<Texture2D>.Get("UI/Gizmo/AbandonOutpost", true);

		public static readonly Texture2D AddTex = ContentFinder<Texture2D>.Get("UI/Gizmo/AddToOutpost", true);

		public static readonly Texture2D RemoveTex = ContentFinder<Texture2D>.Get("UI/Gizmo/RemovePawnFromOutpost", true);

		public static readonly Texture2D StopPackTex = ContentFinder<Texture2D>.Get("UI/Gizmo/CancelAbandonOutpost", true);

		public static readonly Texture2D RemoveItemsTex = ContentFinder<Texture2D>.Get("UI/Gizmo/RemoveItemsFromOutpost", true);

		public static readonly Texture2D CreateTex = ContentFinder<Texture2D>.Get("UI/Gizmo/SetUpOutpost", true);
	}
	public class Outpost_ChooseResult : Outpost
	{
		[CompilerGenerated]
		private sealed class <GetExtraOptions>d__7 : IEnumerable<ResultOption>, IEnumerable, IEnumerator<ResultOption>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private ResultOption <>2__current;

			private int <>l__initialThreadId;

			ResultOption IEnumerator<ResultOption>.Current
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
			public <GetExtraOptions>d__7(int <>1__state)
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
				if (<>1__state != 0)
				{
					return false;
				}
				<>1__state = -1;
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
			IEnumerator<ResultOption> IEnumerable<ResultOption>.GetEnumerator()
			{
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					return this;
				}
				return new <GetExtraOptions>d__7(0);
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<ResultOption>)this).GetEnumerator();
			}
		}

		private ThingDef choice;

		protected OutpostExtension_Choose ChooseExt => base.Ext as OutpostExtension_Choose;

		public override List<ResultOption> ResultOptions => (from ro in base.Ext.ResultOptions.OrEmpty().Concat(GetExtraOptions())
			where ro.Thing == choice
			select ro).ToList();

		public override IEnumerable<Gizmo> GetGizmos()
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_0059: Unknown result type (might be due to invalid IL or missing references)
			//IL_006f: Expected O, but got Unknown
			return base.GetGizmos().Append((Gizmo)new Command_Action
			{
				action = delegate
				{
					//IL_0036: Unknown result type (might be due to invalid IL or missing references)
					//IL_0040: Expected O, but got Unknown
					Find.WindowStack.Add((Window)new FloatMenu(base.Ext.ResultOptions.OrEmpty().Concat(GetExtraOptions()).Select((Func<ResultOption, FloatMenuOption>)delegate(ResultOption ro)
					{
						//IL_010b: Unknown result type (might be due to invalid IL or missing references)
						//IL_0111: Expected O, but got Unknown
						//IL_008a: Unknown result type (might be due to invalid IL or missing references)
						//IL_008f: Unknown result type (might be due to invalid IL or missing references)
						//IL_0094: Unknown result type (might be due to invalid IL or missing references)
						//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
						//IL_00c7: Expected O, but got Unknown
						List<AmountBySkill> minSkills = ro.MinSkills;
						return (minSkills != null && !minSkills.SatisfiedBy(base.CapablePawns)) ? new FloatMenuOption(TaggedString.op_Implicit(ro.Explain(base.CapablePawns.ToList()) + " - " + TranslatorFormattedStringExtensions.Translate("Outposts.SkillTooLow", NamedArgument.op_Implicit(ro.MinSkills.Max((AmountBySkill abs) => abs.Count)))), (Action)null, ro.Thing, (ThingStyleDef)null, false, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0, (int?)null) : new FloatMenuOption(ro.Explain(base.CapablePawns.ToList()), (Action)delegate
						{
							choice = ro.Thing;
						}, ro.Thing, (ThingStyleDef)null, false, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0, (int?)null);
					})
						.ToList()));
				},
				defaultLabel = TaggedString.op_Implicit(GrammarResolverSimpleStringExtensions.Formatted(ChooseExt.ChooseLabel, NamedArgument.op_Implicit(((Def)choice).label))),
				defaultDesc = ChooseExt.ChooseDesc,
				icon = (Texture)(object)((BuildableDef)choice).uiIcon
			});
		}

		public override void RecachePawnTraits()
		{
			//IL_0095: Unknown result type (might be due to invalid IL or missing references)
			//IL_009b: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
			base.RecachePawnTraits();
			if (choice == null)
			{
				choice = GenCollection.MinBy<ResultOption, float>(base.Ext.ResultOptions.OrEmpty().Concat(GetExtraOptions()), (Func<ResultOption, float>)((ResultOption ro) => ((float?)ro.MinSkills?.Sum((AmountBySkill abs) => abs.Count)) ?? 0f)).Thing;
			}
			ResultOption resultOption = GenCollection.FirstOrDefault<ResultOption>(ResultOptions, (Predicate<ResultOption>)((ResultOption ro) => !(ro.MinSkills?.SatisfiedBy(base.CapablePawns) ?? true)));
			if (resultOption == null)
			{
				return;
			}
			ThingDef thing = resultOption.Thing;
			if (thing == null)
			{
				return;
			}
			string label = ((Def)thing).label;
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.SkillChange", NamedArgument.op_Implicit(Name), NamedArgument.op_Implicit(label))), LookTargets.op_Implicit((WorldObject)(object)this), MessageTypeDefOf.NegativeEvent, true);
			choice = GenCollection.MinBy<ResultOption, float>(base.Ext.ResultOptions.OrEmpty().Concat(GetExtraOptions()), (Func<ResultOption, float>)((ResultOption ro) => ((float?)ro.MinSkills?.Sum((AmountBySkill abs) => abs.Count)) ?? 0f)).Thing;
		}

		[IteratorStateMachine(typeof(<GetExtraOptions>d__7))]
		public virtual IEnumerable<ResultOption> GetExtraOptions()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <GetExtraOptions>d__7(-2);
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Defs.Look<ThingDef>(ref choice, "choice");
		}
	}
	public class OutpostExtension_Choose : OutpostExtension
	{
		public string ChooseDesc;

		public string ChooseLabel;
	}
	public class TransportPodsArrivalAction_AddToOutpost : TransportersArrivalAction
	{
		private Outpost outpost;

		public override bool GeneratesMap => true;

		public TransportPodsArrivalAction_AddToOutpost()
		{
		}

		public TransportPodsArrivalAction_AddToOutpost(Outpost addTo)
		{
			outpost = addTo;
		}

		public override void Arrived(List<ActiveTransporterInfo> transporters, PlanetTile tile)
		{
			//IL_0059: Unknown result type (might be due to invalid IL or missing references)
			//IL_0069: Unknown result type (might be due to invalid IL or missing references)
			//IL_006e: Unknown result type (might be due to invalid IL or missing references)
			List<Thing> list = new List<Thing>();
			foreach (Thing item in transporters.SelectMany((ActiveTransporterInfo pod) => (IEnumerable<Thing>)pod.innerContainer).OfType<Thing>())
			{
				list.Add(item);
				if (item is Pawn)
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.AddedFromTransportPods", NamedArgument.op_Implicit(((Entity)item).LabelShortCap), NamedArgument.op_Implicit(((WorldObject)outpost).LabelCap))), LookTargets.op_Implicit((WorldObject)(object)outpost), MessageTypeDefOf.TaskCompletion, true);
				}
			}
			foreach (Thing item2 in list)
			{
				if (item2 is Pawn)
				{
					outpost.AddPawn((Pawn)(object)((item2 is Pawn) ? item2 : null));
				}
				else
				{
					outpost.AddItem(item2);
				}
			}
		}

		public override void ExposeData()
		{
			((TransportersArrivalAction)this).ExposeData();
			Scribe_References.Look<Outpost>(ref outpost, "outpost", false);
		}

		public override FloatMenuAcceptanceReport StillValid(IEnumerable<IThingHolder> pods, PlanetTile destinationTile)
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			return FloatMenuAcceptanceReport.op_Implicit(((WorldObject)outpost).Tile == destinationTile);
		}

		public static IEnumerable<FloatMenuOption> GetFloatMenuOptions(IEnumerable<IThingHolder> pods, Action<PlanetTile, TransportersArrivalAction> launchAction, Outpost outpost)
		{
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_005e: Unknown result type (might be due to invalid IL or missing references)
			return TransportersArrivalActionUtility.GetFloatMenuOptions<TransportPodsArrivalAction_AddToOutpost>((Func<FloatMenuAcceptanceReport>)(() => FloatMenuAcceptanceReport.op_Implicit(true)), (Func<TransportPodsArrivalAction_AddToOutpost>)(() => new TransportPodsArrivalAction_AddToOutpost(outpost)), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.AddTo", NamedArgument.op_Implicit(((WorldObject)outpost).LabelCap))), launchAction, ((WorldObject)outpost).Tile, (Action<Action>)delegate(Action launch)
			{
				launch();
			});
		}
	}
	public static class Utils
	{
		[CompilerGenerated]
		private sealed class <Make>d__7 : IEnumerable<Thing>, IEnumerable, IEnumerator<Thing>, IDisposable, IEnumerator
		{
			private int <>1__state;

			private Thing <>2__current;

			private int <>l__initialThreadId;

			private ThingDef thingDef;

			public ThingDef <>3__thingDef;

			private ThingDef stuff;

			public ThingDef <>3__stuff;

			private int count;

			public int <>3__count;

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
			public <Make>d__7(int <>1__state)
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
				Thing val2;
				switch (<>1__state)
				{
				default:
					return false;
				case 0:
					<>1__state = -1;
					goto IL_0076;
				case 1:
					<>1__state = -1;
					count -= thingDef.stackLimit;
					goto IL_0076;
				case 2:
					{
						<>1__state = -1;
						return false;
					}
					IL_0076:
					if (count > thingDef.stackLimit)
					{
						Thing val = ThingMaker.MakeThing(thingDef, stuff);
						val.stackCount = thingDef.stackLimit;
						<>2__current = val;
						<>1__state = 1;
						return true;
					}
					val2 = ThingMaker.MakeThing(thingDef, stuff);
					val2.stackCount = count;
					<>2__current = val2;
					<>1__state = 2;
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
			IEnumerator<Thing> IEnumerable<Thing>.GetEnumerator()
			{
				<Make>d__7 <Make>d__;
				if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
				{
					<>1__state = 0;
					<Make>d__ = this;
				}
				else
				{
					<Make>d__ = new <Make>d__7(0);
				}
				<Make>d__.thingDef = <>3__thingDef;
				<Make>d__.count = <>3__count;
				<Make>d__.stuff = <>3__stuff;
				return <Make>d__;
			}

			[DebuggerHidden]
			IEnumerator IEnumerable.GetEnumerator()
			{
				return ((IEnumerable<Thing>)this).GetEnumerator();
			}
		}

		public static bool SatisfiedBy(this List<AmountBySkill> minSkills, IEnumerable<Pawn> pawns)
		{
			return minSkills.All((AmountBySkill abs) => pawns.Sum((Pawn p) => p.skills.GetSkill(abs.Skill).Level) >= abs.Count);
		}

		public static List<Pawn> HumanColonists(this Caravan caravan)
		{
			return caravan.PawnsListForReading.Where((Pawn p) => p.IsFreeColonist).ToList();
		}

		public static IEnumerable<T> OrEmpty<T>(this IEnumerable<T> source)
		{
			return source ?? Enumerable.Empty<T>();
		}

		public static IEnumerable<TResult> SelectOrEmpty<TSource, TResult>(this IEnumerable<TSource> source, Func<TSource, TResult> selector)
		{
			if (source != null)
			{
				return source.Select(selector);
			}
			return Enumerable.Empty<TResult>();
		}

		public static IEnumerable<TResult> SelectManyOrEmpty<TSource, TResult>(this IEnumerable<TSource> source, Func<TSource, IEnumerable<TResult>> selector)
		{
			if (source != null)
			{
				return source.SelectMany(selector);
			}
			return Enumerable.Empty<TResult>();
		}

		public static string Line(this string input, bool show = true)
		{
			if (show && !GenText.NullOrEmpty(input))
			{
				return "\n" + input;
			}
			return "";
		}

		public static string Line(this TaggedString input, bool show = true)
		{
			if (show && !((TaggedString)(ref input)).NullOrEmpty())
			{
				return "\n" + ((TaggedString)(ref input)).RawText;
			}
			return "";
		}

		[IteratorStateMachine(typeof(<Make>d__7))]
		public static IEnumerable<Thing> Make(this ThingDef thingDef, int count, ThingDef stuff = null)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new <Make>d__7(-2)
			{
				<>3__thingDef = thingDef,
				<>3__count = count,
				<>3__stuff = stuff
			};
		}

		public static string Requirement(this string req, bool passed)
		{
			//IL_0024: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			return ColoredText.Colorize((passed ? "û" : "?") + " " + req, passed ? Color.green : Color.red);
		}

		public static string Requirement(this TaggedString req, bool passed)
		{
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			return ColoredText.Colorize((passed ? "û" : "?") + " " + ((TaggedString)(ref req)).RawText, passed ? Color.green : Color.red);
		}

		public static string RequirementsStringBase(this OutpostExtension ext, PlanetTile tileIdx, IEnumerable<Pawn> ps)
		{
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_008d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0194: Unknown result type (might be due to invalid IL or missing references)
			//IL_0199: Unknown result type (might be due to invalid IL or missing references)
			//IL_0110: Unknown result type (might be due to invalid IL or missing references)
			//IL_0296: Unknown result type (might be due to invalid IL or missing references)
			//IL_029b: Unknown result type (might be due to invalid IL or missing references)
			//IL_02e5: Unknown result type (might be due to invalid IL or missing references)
			//IL_0220: Unknown result type (might be due to invalid IL or missing references)
			//IL_0231: Unknown result type (might be due to invalid IL or missing references)
			//IL_0236: Unknown result type (might be due to invalid IL or missing references)
			//IL_0317: Unknown result type (might be due to invalid IL or missing references)
			//IL_031c: Unknown result type (might be due to invalid IL or missing references)
			StringBuilder stringBuilder = new StringBuilder();
			BiomeDef biome = Find.WorldGrid[tileIdx].biome;
			string reason = TaggedString.op_Implicit(Translator.Translate("Outposts.NoValidPawns"));
			List<Pawn> list = ps.Where((Pawn p) => ext.CanAddPawn(p, out reason)).ToList();
			if (list.Count == 0)
			{
				stringBuilder.AppendLine(reason.Requirement(passed: false));
			}
			List<BiomeDef> allowedBiomes = ext.AllowedBiomes;
			if (allowedBiomes != null && allowedBiomes.Count > 0)
			{
				stringBuilder.AppendLine(Translator.Translate("Outposts.AllowedBiomes").Requirement(ext.AllowedBiomes.Contains(biome)));
				stringBuilder.AppendLine(GenText.ToLineList(ext.AllowedBiomes.Select((BiomeDef b) => ((Def)b).label), "  ", true));
			}
			allowedBiomes = ext.DisallowedBiomes;
			if (allowedBiomes != null && allowedBiomes.Count > 0)
			{
				stringBuilder.AppendLine(Translator.Translate("Outposts.DisallowedBiomes").Requirement(!ext.DisallowedBiomes.Contains(biome)));
				stringBuilder.AppendLine(GenText.ToLineList(ext.DisallowedBiomes.Select((BiomeDef b) => ((Def)b).label), "  ", true));
			}
			if (ext.MinPawns > 0)
			{
				stringBuilder.AppendLine(TranslatorFormattedStringExtensions.Translate("Outposts.NumPawns", NamedArgument.op_Implicit(ext.MinPawns)).Requirement(list.Count >= ext.MinPawns));
			}
			List<AmountBySkill> requiredSkills = ext.RequiredSkills;
			if (requiredSkills != null && requiredSkills.Count > 0)
			{
				foreach (AmountBySkill requiredSkill in ext.RequiredSkills)
				{
					stringBuilder.AppendLine(TranslatorFormattedStringExtensions.Translate("Outposts.RequiredSkill", NamedArgument.op_Implicit(requiredSkill.Skill.skillLabel), NamedArgument.op_Implicit(requiredSkill.Count)).Requirement(list.Sum((Pawn p) => p.skills.GetSkill(requiredSkill.Skill).Level) >= requiredSkill.Count));
				}
			}
			if (ext.RequiresGrowing)
			{
				TaggedString req = Translator.Translate("Outposts.GrowingRequired");
				List<Twelfth> list2 = GenTemperature.TwelfthsInAverageTemperatureRange(tileIdx, 6f, 42f);
				stringBuilder.AppendLine(req.Requirement(list2 != null && GenCollection.Any<Twelfth>(list2)));
			}
			List<ThingDefCountClass> costToMake = ext.CostToMake;
			if (costToMake != null && costToMake.Count > 0)
			{
				Caravan val = Find.WorldObjects.PlayerControlledCaravanAt(tileIdx);
				foreach (ThingDefCountClass item in ext.CostToMake)
				{
					stringBuilder.AppendLine(TranslatorFormattedStringExtensions.Translate("Outposts.MustHaveInCaravan", NamedArgument.op_Implicit(item.Label)).Requirement(CaravanInventoryUtility.HasThings(val, item.thingDef, item.count, (Func<Thing, bool>)null)));
				}
			}
			return stringBuilder.ToString();
		}

		public static bool CanAddPawn(this OutpostExtension ext, Pawn pawn, out string reason)
		{
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			if (ext?.Event != null && !IdeoUtility.DoerWillingToDo(ext.Event, pawn))
			{
				reason = TaggedString.op_Implicit(Translator.Translate("IdeoligionForbids"));
				return false;
			}
			reason = null;
			return true;
		}

		public static string CanSpawnOnWithExt(this OutpostExtension ext, PlanetTile tileIdx, IEnumerable<Pawn> ps)
		{
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
			//IL_0128: Unknown result type (might be due to invalid IL or missing references)
			//IL_00df: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
			//IL_0169: Unknown result type (might be due to invalid IL or missing references)
			//IL_016e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0219: Unknown result type (might be due to invalid IL or missing references)
			//IL_025b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0260: Unknown result type (might be due to invalid IL or missing references)
			//IL_01d9: Unknown result type (might be due to invalid IL or missing references)
			//IL_01df: Unknown result type (might be due to invalid IL or missing references)
			//IL_01e4: Unknown result type (might be due to invalid IL or missing references)
			string reason = TaggedString.op_Implicit(Translator.Translate("Outposts.NoValidPawns"));
			List<Pawn> pawns = ps.Where((Pawn p) => ext.CanAddPawn(p, out reason)).ToList();
			if (pawns.Count == 0)
			{
				return reason;
			}
			Tile val = Find.WorldGrid[tileIdx];
			if (val != null)
			{
				BiomeDef biome = val.biome;
				List<BiomeDef> disallowedBiomes = ext.DisallowedBiomes;
				if (disallowedBiomes == null || disallowedBiomes.Count <= 0 || !ext.DisallowedBiomes.Contains(biome))
				{
					disallowedBiomes = ext.AllowedBiomes;
					if (disallowedBiomes == null || disallowedBiomes.Count <= 0 || ext.AllowedBiomes.Contains(biome))
					{
						goto IL_00ef;
					}
				}
				return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.CannotBeMade", NamedArgument.op_Implicit(((Def)biome).label)));
			}
			goto IL_00ef;
			IL_00ef:
			if (Find.WorldObjects.AnySettlementBaseAtOrAdjacent(tileIdx) || Find.WorldObjects.AllWorldObjects.OfType<Outpost>().Any((Outpost outpost) => Find.WorldGrid.IsNeighborOrSame(tileIdx, ((WorldObject)outpost).Tile)))
			{
				return TaggedString.op_Implicit(Translator.Translate("Outposts.TooClose"));
			}
			if (ext.MinPawns > 0 && pawns.Count < ext.MinPawns)
			{
				return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.NotEnoughPawns", NamedArgument.op_Implicit(ext.MinPawns)));
			}
			List<AmountBySkill> requiredSkills = ext.RequiredSkills;
			if (requiredSkills != null && requiredSkills.Count > 0)
			{
				AmountBySkill amountBySkill = GenCollection.FirstOrDefault<AmountBySkill>(ext.RequiredSkills, (Predicate<AmountBySkill>)((AmountBySkill requiredSkill) => pawns.Sum((Pawn p) => p.skills.GetSkill(requiredSkill.Skill).Level) < requiredSkill.Count));
				if (amountBySkill != null)
				{
					SkillDef skill = amountBySkill.Skill;
					if (skill != null)
					{
						string skillLabel = skill.skillLabel;
						int count = amountBySkill.Count;
						return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.NotSkilledEnough", NamedArgument.op_Implicit(skillLabel), NamedArgument.op_Implicit(count)));
					}
				}
			}
			List<ThingDefCountClass> costToMake = ext.CostToMake;
			if (costToMake != null && costToMake.Count > 0)
			{
				Caravan caravan = Find.WorldObjects.PlayerControlledCaravanAt(tileIdx);
				ThingDefCountClass val2 = GenCollection.FirstOrDefault<ThingDefCountClass>(ext.CostToMake, (Predicate<ThingDefCountClass>)((ThingDefCountClass tdcc) => !CaravanInventoryUtility.HasThings(caravan, tdcc.thingDef, tdcc.count, (Func<Thing, bool>)null)));
				if (val2 != null)
				{
					string label = val2.Label;
					return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.MustHaveInCaravan", NamedArgument.op_Implicit(label)));
				}
			}
			return null;
		}

		public static string CheckSkill(this IEnumerable<Pawn> pawns, SkillDef skill, int minLevel)
		{
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0040: Unknown result type (might be due to invalid IL or missing references)
			//IL_0045: Unknown result type (might be due to invalid IL or missing references)
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			return TaggedString.op_Implicit((pawns.Sum((Pawn p) => p.skills.GetSkill(skill).Level) < minLevel) ? TranslatorFormattedStringExtensions.Translate("Outposts.NotSkilledEnough", NamedArgument.op_Implicit(skill.skillLabel), NamedArgument.op_Implicit(minLevel)) : TaggedString.op_Implicit((string)null));
		}
	}
	public class Dialog_RenameOutpost : Dialog_Rename<Outpost>
	{
		private readonly Outpost outpost;

		public Dialog_RenameOutpost(Outpost outpost)
			: base(outpost)
		{
			this.outpost = outpost;
			base.curName = outpost.Name;
		}
	}
	public class WITab_Outpost_Gear : WITab
	{
		private static readonly List<Apparel> tmpApparel = new List<Apparel>();

		private static readonly List<ThingWithComps> tmpExistingEquipment = new List<ThingWithComps>();

		private static readonly List<Apparel> tmpExistingApparel = new List<Apparel>();

		private List<Thing> allThings;

		private Thing draggedItem;

		private Vector2 draggedItemPosOffset;

		private bool droppedDraggedItem;

		private Vector2 leftPaneScrollPosition;

		private float leftPaneScrollViewHeight;

		private float leftPaneWidth;

		private Vector2 rightPaneScrollPosition;

		private float rightPaneScrollViewHeight;

		private float rightPaneWidth;

		public Outpost SelOutpost => ((WITab)this).SelObject as Outpost;

		private List<Pawn> Pawns => SelOutpost.AllPawns.Where((Pawn p) => p.apparel != null && p.equipment != null && p.health != null && p.guest != null).ToList();

		public WITab_Outpost_Gear()
		{
			((InspectTabBase)this).labelKey = "TabCaravanGear";
		}

		public override void UpdateSize()
		{
			((InspectTabBase)this).UpdateSize();
			leftPaneWidth = 469f;
			rightPaneWidth = 345f;
			((InspectTabBase)this).size.x = leftPaneWidth + rightPaneWidth;
			((InspectTabBase)this).size.y = Mathf.Min(550f, ((InspectTabBase)this).PaneTopY - 30f);
		}

		public override void OnOpen()
		{
			((InspectTabBase)this).OnOpen();
			draggedItem = null;
		}

		private void DoLeftPane()
		{
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_005c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0066: Unknown result type (might be due to invalid IL or missing references)
			//IL_0067: Unknown result type (might be due to invalid IL or missing references)
			//IL_0072: Unknown result type (might be due to invalid IL or missing references)
			//IL_0078: Invalid comparison between Unknown and I4
			Rect val = GenUI.ContractedBy(new Rect(0f, 0f, leftPaneWidth, ((InspectTabBase)this).size.y), 10f);
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(0f, 0f, ((Rect)(ref val)).width - 16f, leftPaneScrollViewHeight);
			float curY = 0f;
			Widgets.BeginScrollView(val, ref leftPaneScrollPosition, val2, true);
			DoPawnRows(ref curY, val2, val);
			if ((int)Event.current.type == 8)
			{
				leftPaneScrollViewHeight = curY + 30f;
			}
			Widgets.EndScrollView();
		}

		private void DoPawnRow(ref float curY, Rect viewRect, Rect scrollOutRect, Pawn p)
		{
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			float num = leftPaneScrollPosition.y - 40f;
			float num2 = leftPaneScrollPosition.y + ((Rect)(ref scrollOutRect)).height;
			if (curY > num && curY < num2)
			{
				DoPawnRow(new Rect(0f, curY, ((Rect)(ref viewRect)).width, 40f), p);
			}
			curY += 40f;
		}

		private void DoPawnRow(Rect rect, Pawn p)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0056: Unknown result type (might be due to invalid IL or missing references)
			//IL_0077: Unknown result type (might be due to invalid IL or missing references)
			//IL_008f: Unknown result type (might be due to invalid IL or missing references)
			//IL_00db: Unknown result type (might be due to invalid IL or missing references)
			//IL_011c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0232: Unknown result type (might be due to invalid IL or missing references)
			//IL_025a: Unknown result type (might be due to invalid IL or missing references)
			GUI.BeginGroup(rect);
			Rect val = GenUI.AtZero(rect);
			Widgets.InfoCardButton(((Rect)(ref val)).width - 24f, (((Rect)(ref rect)).height - 24f) / 2f, (Thing)(object)p);
			((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
			bool flag = draggedItem != null && ((Rect)(ref val)).Contains(Event.current.mousePosition) && CurrentWearerOf(draggedItem) != p;
			if ((Mouse.IsOver(val) && draggedItem == null) || flag)
			{
				Widgets.DrawHighlight(val);
			}
			if (flag && droppedDraggedItem)
			{
				TryEquipDraggedItem(p);
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_Tiny, (Map)null);
			}
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(4f, (((Rect)(ref rect)).height - 27f) / 2f, 27f, 27f);
			Widgets.ThingIcon(val2, (Thing)(object)p, 1f, (Rot4?)null, false, 1f, false);
			Rect val3 = default(Rect);
			((Rect)(ref val3))..ctor(((Rect)(ref val2)).xMax + 4f, 11f, 100f, 18f);
			GenMapUI.DrawPawnLabel(p, val3, 1f, 100f, (Dictionary<string, string>)null, (GameFont)1, false, false);
			float curX = ((Rect)(ref val3)).xMax;
			if (p.equipment != null)
			{
				List<ThingWithComps> allEquipmentListForReading = p.equipment.AllEquipmentListForReading;
				for (int i = 0; i < allEquipmentListForReading.Count; i++)
				{
					DoEquippedGear((Thing)(object)allEquipmentListForReading[i], p, ref curX);
				}
			}
			if (p.apparel != null)
			{
				tmpApparel.Clear();
				tmpApparel.AddRange(p.apparel.WornApparel);
				GenCollection.SortBy<Apparel, int, float>(tmpApparel, (Func<Apparel, int>)((Apparel x) => ((Thing)x).def.apparel.LastLayer.drawOrder), (Func<Apparel, float>)((Apparel x) => 0f - ((Thing)x).def.apparel.HumanBodyCoverage));
				for (int j = 0; j < tmpApparel.Count; j++)
				{
					DoEquippedGear((Thing)(object)tmpApparel[j], p, ref curX);
				}
			}
			if (p.Downed)
			{
				GUI.color = new Color(1f, 0f, 0f, 0.5f);
				Widgets.DrawLineHorizontal(0f, ((Rect)(ref rect)).height / 2f, ((Rect)(ref rect)).width);
				GUI.color = Color.white;
			}
			GUI.EndGroup();
		}

		private void DoInventoryRows(ref float curY, Rect scrollViewRect, Rect scrollOutRect)
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			//IL_0088: Unknown result type (might be due to invalid IL or missing references)
			//IL_0089: Unknown result type (might be due to invalid IL or missing references)
			Widgets.ListSeparator(ref curY, ((Rect)(ref scrollViewRect)).width, TaggedString.op_Implicit(Translator.Translate("CaravanWeaponsAndApparel")));
			bool flag = false;
			for (int i = 0; i < allThings.Count; i++)
			{
				Thing val = allThings[i];
				if (IsVisibleWeapon(val.def))
				{
					if (!flag)
					{
						flag = true;
					}
					DoInventoryRow(ref curY, scrollViewRect, scrollOutRect, val);
				}
			}
			bool flag2 = false;
			for (int j = 0; j < allThings.Count; j++)
			{
				Thing val2 = allThings[j];
				if (val2.def.IsApparel)
				{
					if (!flag2)
					{
						flag2 = true;
					}
					DoInventoryRow(ref curY, scrollViewRect, scrollOutRect, val2);
				}
			}
			if (!flag && !flag2)
			{
				Widgets.NoneLabel(ref curY, ((Rect)(ref scrollViewRect)).width, (string)null);
			}
		}

		private void DoEquippedGear(Thing t, Pawn p, ref float curX)
		{
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_0049: Unknown result type (might be due to invalid IL or missing references)
			//IL_006b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0089: Unknown result type (might be due to invalid IL or missing references)
			//IL_0073: Unknown result type (might be due to invalid IL or missing references)
			//IL_007a: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(curX, 4f, 32f, 32f);
			bool flag = Mouse.IsOver(val);
			float num = ((t == draggedItem) ? 0.2f : ((!flag || draggedItem != null) ? 1f : 0.75f));
			Widgets.ThingIcon(val, t, num, (Rot4?)null, false, 1f, false);
			curX += 32f;
			if (Mouse.IsOver(val))
			{
				TooltipHandler.TipRegion(val, TipSignal.op_Implicit(((Entity)t).LabelCap));
			}
			if ((int)Event.current.type == 0 && Event.current.button == 0 && flag)
			{
				draggedItem = t;
				droppedDraggedItem = false;
				draggedItemPosOffset = Event.current.mousePosition - ((Rect)(ref val)).position;
				Event.current.Use();
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Click, (Map)null);
			}
		}

		private void CheckDraggedItemStillValid()
		{
			if (draggedItem != null)
			{
				if (draggedItem.Destroyed)
				{
					draggedItem = null;
				}
				else if (CurrentWearerOf(draggedItem) == null && !allThings.Contains(draggedItem))
				{
					draggedItem = null;
				}
			}
		}

		private void CheckDropDraggedItem()
		{
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Invalid comparison between Unknown and I4
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Invalid comparison between Unknown and I4
			if (draggedItem != null && ((int)Event.current.type == 1 || (int)Event.current.rawType == 1))
			{
				droppedDraggedItem = true;
			}
		}

		private void TryEquipDraggedItem(Pawn p)
		{
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
			//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
			//IL_00af: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
			//IL_0105: Unknown result type (might be due to invalid IL or missing references)
			//IL_010a: Unknown result type (might be due to invalid IL or missing references)
			//IL_022c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0237: Unknown result type (might be due to invalid IL or missing references)
			//IL_023c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0440: Unknown result type (might be due to invalid IL or missing references)
			//IL_044a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0465: Unknown result type (might be due to invalid IL or missing references)
			//IL_0475: Unknown result type (might be due to invalid IL or missing references)
			//IL_047f: Expected O, but got Unknown
			//IL_01bf: Unknown result type (might be due to invalid IL or missing references)
			//IL_0166: Unknown result type (might be due to invalid IL or missing references)
			//IL_0171: Unknown result type (might be due to invalid IL or missing references)
			//IL_0176: Unknown result type (might be due to invalid IL or missing references)
			//IL_02cf: Unknown result type (might be due to invalid IL or missing references)
			//IL_02da: Unknown result type (might be due to invalid IL or missing references)
			//IL_02df: Unknown result type (might be due to invalid IL or missing references)
			//IL_0284: Unknown result type (might be due to invalid IL or missing references)
			//IL_03b5: Unknown result type (might be due to invalid IL or missing references)
			//IL_03c1: Expected O, but got Unknown
			droppedDraggedItem = false;
			string text = default(string);
			if (!EquipmentUtility.CanEquip(draggedItem, p, ref text, true))
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipCustom", NamedArgument.op_Implicit(GenText.CapitalizeFirst(text)))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
				draggedItem = null;
				return;
			}
			if (draggedItem.def.IsWeapon)
			{
				if (p.guest.IsPrisoner)
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipCustom", NamedArgument.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessagePrisonerCannotEquipWeapon", NamedArgumentUtility.Named((object)p, "PAWN"))))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
					draggedItem = null;
					return;
				}
				if (p.WorkTagIsDisabled((WorkTags)8))
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipIncapableOfViolence", NamedArgument.op_Implicit(((Entity)p).LabelShort), NamedArgument.op_Implicit((Thing)(object)p))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
					draggedItem = null;
					return;
				}
				if (p.WorkTagIsDisabled((WorkTags)524288) && draggedItem.def.IsRangedWeapon)
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipIncapableOfShooting", NamedArgument.op_Implicit(((Entity)p).LabelShort), NamedArgument.op_Implicit((Thing)(object)p))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
					draggedItem = null;
					return;
				}
				if (!p.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation))
				{
					Messages.Message(TaggedString.op_Implicit(Translator.Translate("MessageCantEquipIncapableOfManipulation")), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
					draggedItem = null;
					return;
				}
			}
			Thing obj = draggedItem;
			Apparel val = (Apparel)(object)((obj is Apparel) ? obj : null);
			if (val != null && p.apparel != null)
			{
				if (!ApparelUtility.HasPartsToWear(p, ((Thing)val).def))
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantWearApparelMissingBodyParts", NamedArgument.op_Implicit(((Entity)p).LabelShort), NamedArgument.op_Implicit((Thing)(object)p))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
					draggedItem = null;
					return;
				}
				if (CurrentWearerOf((Thing)(object)val) != null && CurrentWearerOf((Thing)(object)val).apparel.IsLocked(val))
				{
					Messages.Message(TaggedString.op_Implicit(Translator.Translate("MessageCantUnequipLockedApparel")), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
					draggedItem = null;
					return;
				}
				if (p.apparel.WouldReplaceLockedApparel(val))
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageWouldReplaceLockedApparel", NamedArgument.op_Implicit(((Entity)p).LabelShort), NamedArgument.op_Implicit((Thing)(object)p))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
					draggedItem = null;
					return;
				}
				tmpExistingApparel.Clear();
				tmpExistingApparel.AddRange(p.apparel.WornApparel);
				for (int i = 0; i < tmpExistingApparel.Count; i++)
				{
					if (!ApparelUtility.CanWearTogether(((Thing)val).def, ((Thing)tmpExistingApparel[i]).def, p.RaceProps.body))
					{
						p.apparel.Remove(tmpExistingApparel[i]);
						SelOutpost.AddItem((Thing)(object)tmpExistingApparel[i]);
					}
				}
				p.apparel.Wear((Apparel)SelOutpost.TakeItem((Thing)(object)val), false, false);
				Pawn_OutfitTracker outfits = p.outfits;
				if (outfits != null)
				{
					outfits.forcedHandler.SetForced(val, true);
				}
			}
			else
			{
				Thing val2 = draggedItem;
				ThingWithComps thingWithComps = (ThingWithComps)(object)((val2 is ThingWithComps) ? val2 : null);
				if (thingWithComps != null && p.equipment != null)
				{
					string personaWeaponConfirmationText = EquipmentUtility.GetPersonaWeaponConfirmationText(draggedItem, p);
					if (!GenText.NullOrEmpty(personaWeaponConfirmationText))
					{
						_ = draggedItem;
						Find.WindowStack.Add((Window)new Dialog_MessageBox(TaggedString.op_Implicit(personaWeaponConfirmationText), TaggedString.op_Implicit(Translator.Translate("Yes")), (Action)delegate
						{
							TryEquipDraggedItem_Equipment(p, thingWithComps);
						}, TaggedString.op_Implicit(Translator.Translate("No")), (Action)null, (string)null, false, (Action)null, (Action)null, (WindowLayer)1));
						draggedItem = null;
						return;
					}
					TryEquipDraggedItem_Equipment(p, thingWithComps);
				}
				else
				{
					Log.Warning(string.Concat("Could not make ", p, " equip or wear ", draggedItem));
				}
			}
			draggedItem = null;
		}

		private void TryEquipDraggedItem_Equipment(Pawn p, ThingWithComps eq)
		{
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_0071: Unknown result type (might be due to invalid IL or missing references)
			//IL_0076: Unknown result type (might be due to invalid IL or missing references)
			//IL_007b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0080: Unknown result type (might be due to invalid IL or missing references)
			//IL_01ee: Unknown result type (might be due to invalid IL or missing references)
			//IL_01f8: Expected O, but got Unknown
			//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
			//IL_0159: Unknown result type (might be due to invalid IL or missing references)
			//IL_010f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0115: Unknown result type (might be due to invalid IL or missing references)
			//IL_011a: Unknown result type (might be due to invalid IL or missing references)
			string text = default(string);
			if (!EquipmentUtility.CanEquip(draggedItem, p, ref text, true))
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipCustom", NamedArgument.op_Implicit(GenText.CapitalizeFirst(text)))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
				draggedItem = null;
				return;
			}
			if (((Thing)eq).def.IsWeapon)
			{
				if (p.guest.IsPrisoner)
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipCustom", NamedArgument.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessagePrisonerCannotEquipWeapon", NamedArgumentUtility.Named((object)p, "PAWN"))))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
					draggedItem = null;
					return;
				}
				if (p.WorkTagIsDisabled((WorkTags)8))
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipIncapableOfViolence", NamedArgument.op_Implicit(((Entity)p).LabelShort), NamedArgument.op_Implicit((Thing)(object)p))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
					draggedItem = null;
					return;
				}
				if (p.WorkTagIsDisabled((WorkTags)524288) && draggedItem.def.IsRangedWeapon)
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipIncapableOfShooting", NamedArgument.op_Implicit(((Entity)p).LabelShort), NamedArgument.op_Implicit((Thing)(object)p))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
					draggedItem = null;
					return;
				}
				if (!p.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation))
				{
					Messages.Message(TaggedString.op_Implicit(Translator.Translate("MessageCantEquipIncapableOfManipulation")), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
					draggedItem = null;
					return;
				}
			}
			tmpExistingEquipment.Clear();
			tmpExistingEquipment.AddRange(p.equipment.AllEquipmentListForReading);
			for (int i = 0; i < tmpExistingEquipment.Count; i++)
			{
				p.equipment.Remove(tmpExistingEquipment[i]);
				SelOutpost.AddItem((Thing)(object)tmpExistingEquipment[i]);
			}
			p.equipment.AddEquipment((ThingWithComps)SelOutpost.TakeItem((Thing)(object)eq));
			draggedItem = null;
		}

		private static bool IsVisibleWeapon(ThingDef t)
		{
			if (t.IsWeapon && t != ThingDefOf.WoodLog)
			{
				return t != ThingDefOf.Beer;
			}
			return false;
		}

		private static Pawn CurrentWearerOf(Thing t)
		{
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Expected O, but got Unknown
			IThingHolder parentHolder = t.ParentHolder;
			if ((parentHolder is Pawn_EquipmentTracker || parentHolder is Pawn_ApparelTracker) ? true : false)
			{
				return (Pawn)parentHolder.ParentHolder;
			}
			return null;
		}

		private void MoveDraggedItemToInventory()
		{
			//IL_007a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0084: Expected O, but got Unknown
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			droppedDraggedItem = false;
			Thing obj = draggedItem;
			Apparel val = (Apparel)(object)((obj is Apparel) ? obj : null);
			Pawn val2 = CurrentWearerOf(draggedItem);
			if (val2 != null)
			{
				if (val != null)
				{
					if (val2.apparel.IsLocked(val))
					{
						Messages.Message(TaggedString.op_Implicit(Translator.Translate("MessageCantUnequipLockedApparel")), LookTargets.op_Implicit((Thing)(object)CurrentWearerOf((Thing)(object)val)), MessageTypeDefOf.RejectInput, false);
						draggedItem = null;
						return;
					}
					val2.apparel.Remove(val);
				}
				else
				{
					val2.equipment.Remove((ThingWithComps)draggedItem);
				}
			}
			SelOutpost.AddItem(draggedItem);
			draggedItem = null;
		}

		private void DoInventoryRow(ref float curY, Rect viewRect, Rect scrollOutRect, Thing t)
		{
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			float num = rightPaneScrollPosition.y - 30f;
			float num2 = rightPaneScrollPosition.y + ((Rect)(ref scrollOutRect)).height;
			if (curY > num && curY < num2)
			{
				DoInventoryRow(new Rect(0f, curY, ((Rect)(ref viewRect)).width, 30f), t);
			}
			curY += 30f;
		}

		private void DoInventoryRow(Rect rect, Thing t)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			//IL_009c: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
			//IL_0112: Unknown result type (might be due to invalid IL or missing references)
			//IL_0121: Unknown result type (might be due to invalid IL or missing references)
			//IL_0134: Unknown result type (might be due to invalid IL or missing references)
			//IL_0155: Unknown result type (might be due to invalid IL or missing references)
			//IL_015a: Unknown result type (might be due to invalid IL or missing references)
			GUI.BeginGroup(rect);
			Rect val = GenUI.AtZero(rect);
			Widgets.InfoCardButton(((Rect)(ref val)).width - 24f, (((Rect)(ref rect)).height - 24f) / 2f, t);
			((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
			if (draggedItem == null && Mouse.IsOver(val))
			{
				Widgets.DrawHighlight(val);
			}
			float num = ((t == draggedItem) ? 0.5f : 1f);
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(4f, (((Rect)(ref rect)).height - 27f) / 2f, 27f, 27f);
			Widgets.ThingIcon(val2, t, num, (Rot4?)null, false, 1f, false);
			GUI.color = new Color(1f, 1f, 1f, num);
			Rect val3 = new Rect(((Rect)(ref val2)).xMax + 4f, 0f, 250f, 30f);
			Text.Anchor = (TextAnchor)3;
			Text.WordWrap = false;
			Widgets.Label(val3, ((Entity)t).LabelCap);
			Text.Anchor = (TextAnchor)0;
			Text.WordWrap = true;
			GUI.color = Color.white;
			if ((int)Event.current.type == 0 && Event.current.button == 0 && Mouse.IsOver(val))
			{
				draggedItem = t;
				droppedDraggedItem = false;
				draggedItemPosOffset = new Vector2(16f, 16f);
				Event.current.Use();
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Click, (Map)null);
			}
			GUI.EndGroup();
		}

		private void DoPawnRows(ref float curY, Rect scrollViewRect, Rect scrollOutRect)
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_002e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_0042: Unknown result type (might be due to invalid IL or missing references)
			//IL_005f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0084: Unknown result type (might be due to invalid IL or missing references)
			//IL_0085: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
			List<Pawn> pawns = Pawns;
			Text.Font = (GameFont)0;
			GUI.color = Color.gray;
			Widgets.Label(new Rect(135f, curY + 6f, 200f, 100f), Translator.Translate("DragToRearrange"));
			GUI.color = Color.white;
			Text.Font = (GameFont)1;
			Widgets.ListSeparator(ref curY, ((Rect)(ref scrollViewRect)).width, TaggedString.op_Implicit(Translator.Translate("CaravanColonists")));
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn val = pawns[i];
				if (val.IsColonist)
				{
					DoPawnRow(ref curY, scrollViewRect, scrollOutRect, val);
				}
			}
			bool flag = false;
			for (int j = 0; j < pawns.Count; j++)
			{
				Pawn val2 = pawns[j];
				if (val2.IsPrisoner)
				{
					if (!flag)
					{
						Widgets.ListSeparator(ref curY, ((Rect)(ref scrollViewRect)).width, TaggedString.op_Implicit(Translator.Translate("CaravanPrisoners")));
						flag = true;
					}
					DoPawnRow(ref curY, scrollViewRect, scrollOutRect, val2);
				}
			}
		}

		public override void ExtraOnGUI()
		{
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_005a: Unknown result type (might be due to invalid IL or missing references)
			//IL_006a: Unknown result type (might be due to invalid IL or missing references)
			((InspectTabBase)this).ExtraOnGUI();
			if (draggedItem != null)
			{
				Vector2 mousePosition = Event.current.mousePosition;
				Rect rect = new Rect(mousePosition.x - draggedItemPosOffset.x, mousePosition.y - draggedItemPosOffset.y, 32f, 32f);
				Find.WindowStack.ImmediateWindow(1283641090, rect, (WindowLayer)3, (Action)delegate
				{
					//IL_000f: Unknown result type (might be due to invalid IL or missing references)
					//IL_0014: Unknown result type (might be due to invalid IL or missing references)
					if (draggedItem != null)
					{
						Widgets.ThingIcon(GenUI.AtZero(rect), draggedItem, 1f, (Rot4?)null, false, 1f, false);
					}
				}, false, false, 0f, (Action)null, false);
			}
			CheckDropDraggedItem();
		}

		private void DoRightPane()
		{
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_009c: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bf: Invalid comparison between Unknown and I4
			//IL_005e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0077: Unknown result type (might be due to invalid IL or missing references)
			Rect val = GenUI.ContractedBy(new Rect(0f, 0f, rightPaneWidth, ((InspectTabBase)this).size.y), 10f);
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(0f, 0f, ((Rect)(ref val)).width - 16f, rightPaneScrollViewHeight);
			if (draggedItem != null && ((Rect)(ref val)).Contains(Event.current.mousePosition) && CurrentWearerOf(draggedItem) != null)
			{
				Widgets.DrawHighlight(val);
				if (droppedDraggedItem)
				{
					MoveDraggedItemToInventory();
					SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_Tiny, (Map)null);
				}
			}
			float curY = 0f;
			Widgets.BeginScrollView(val, ref rightPaneScrollPosition, val2, true);
			DoInventoryRows(ref curY, val2, val);
			if ((int)Event.current.type == 8)
			{
				rightPaneScrollViewHeight = curY + 30f;
			}
			Widgets.EndScrollView();
		}

		public override void FillTab()
		{
			//IL_0078: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
			if (allThings == null)
			{
				allThings = new List<Thing>(SelOutpost.Things.Count());
			}
			allThings.Clear();
			allThings.AddRange(SelOutpost.Things);
			Text.Font = (GameFont)1;
			CheckDraggedItemStillValid();
			CheckDropDraggedItem();
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(0f, 0f, leftPaneWidth, ((InspectTabBase)this).size.y);
			GUI.BeginGroup(val);
			DoLeftPane();
			GUI.EndGroup();
			GUI.BeginGroup(new Rect(((Rect)(ref val)).xMax, 0f, rightPaneWidth, ((InspectTabBase)this).size.y));
			DoRightPane();
			GUI.EndGroup();
			if (draggedItem != null && droppedDraggedItem)
			{
				droppedDraggedItem = false;
				draggedItem = null;
			}
		}
	}
	[StaticConstructorOnStartup]
	public class WITab_Outpost_Health : WITab
	{
		private static readonly List<PawnCapacityDef> capacitiesToDisplay = new List<PawnCapacityDef>();

		private bool compactMode;

		private Vector2 scrollPosition;

		private float scrollViewHeight;

		private Pawn specificHealthTabForPawn;

		public Outpost SelOutpost => ((WITab)this).SelObject as Outpost;

		private List<Pawn> Pawns => SelOutpost.AllPawns.Where((Pawn p) => p.apparel != null && p.equipment != null && p.health != null && p.guest != null).ToList();

		private float SpecificHealthTabWidth
		{
			get
			{
				EnsureSpecificHealthTabForPawnValid();
				if (ThingUtility.DestroyedOrNull((Thing)(object)specificHealthTabForPawn))
				{
					return 0f;
				}
				return 630f;
			}
		}

		private static List<PawnCapacityDef> CapacitiesToDisplay
		{
			get
			{
				capacitiesToDisplay.Clear();
				List<PawnCapacityDef> allDefsListForReading = DefDatabase<PawnCapacityDef>.AllDefsListForReading;
				for (int i = 0; i < allDefsListForReading.Count; i++)
				{
					if (allDefsListForReading[i].showOnCaravanHealthTab)
					{
						capacitiesToDisplay.Add(allDefsListForReading[i]);
					}
				}
				GenCollection.SortBy<PawnCapacityDef, int>(capacitiesToDisplay, (Func<PawnCapacityDef, int>)((PawnCapacityDef x) => x.listOrder));
				return capacitiesToDisplay;
			}
		}

		public WITab_Outpost_Health()
		{
			((InspectTabBase)this).labelKey = "TabCaravanHealth";
		}

		public override void FillTab()
		{
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0036: Unknown result type (might be due to invalid IL or missing references)
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0066: Unknown result type (might be due to invalid IL or missing references)
			//IL_006d: Unknown result type (might be due to invalid IL or missing references)
			//IL_007f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0080: Unknown result type (might be due to invalid IL or missing references)
			//IL_008b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0091: Invalid comparison between Unknown and I4
			EnsureSpecificHealthTabForPawnValid();
			Text.Font = (GameFont)1;
			Rect val = GenUI.ContractedBy(new Rect(0f, 0f, ((InspectTabBase)this).size.x, ((InspectTabBase)this).size.y), 10f);
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(0f, 0f, ((Rect)(ref val)).width - 16f, scrollViewHeight);
			float curY = 0f;
			Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
			DoColumnHeaders(ref curY);
			DoRows(ref curY, val2, val);
			if ((int)Event.current.type == 8)
			{
				scrollViewHeight = curY + 30f;
			}
			Widgets.EndScrollView();
		}

		public override void UpdateSize()
		{
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0042: Unknown result type (might be due to invalid IL or missing references)
			EnsureSpecificHealthTabForPawnValid();
			((InspectTabBase)this).UpdateSize();
			((InspectTabBase)this).size = GetRawSize(compactMode: false);
			if (((InspectTabBase)this).size.x + SpecificHealthTabWidth > (float)UI.screenWidth)
			{
				compactMode = true;
				((InspectTabBase)this).size = GetRawSize(compactMode: true);
			}
			else
			{
				compactMode = false;
			}
		}

		public override void ExtraOnGUI()
		{
			//IL_002e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			//IL_0058: Unknown result type (might be due to invalid IL or missing references)
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			//IL_006d: Unknown result type (might be due to invalid IL or missing references)
			EnsureSpecificHealthTabForPawnValid();
			((InspectTabBase)this).ExtraOnGUI();
			Pawn localSpecificHealthTabForPawn = specificHealthTabForPawn;
			if (localSpecificHealthTabForPawn == null)
			{
				return;
			}
			Rect tabRect = ((InspectTabBase)this).TabRect;
			float specificHealthTabWidth = SpecificHealthTabWidth;
			Rect rect = new Rect(((Rect)(ref tabRect)).xMax - 1f, ((Rect)(ref tabRect)).yMin, specificHealthTabWidth, ((Rect)(ref tabRect)).height);
			Find.WindowStack.ImmediateWindow(1439870015, rect, (WindowLayer)0, (Action)delegate
			{
				//IL_0034: Unknown result type (might be due to invalid IL or missing references)
				//IL_004d: Unknown result type (might be due to invalid IL or missing references)
				//IL_0052: Unknown result type (might be due to invalid IL or missing references)
				if (!ThingUtility.DestroyedOrNull((Thing)(object)localSpecificHealthTabForPawn))
				{
					HealthCardUtility.DrawPawnHealthCard(new Rect(0f, 20f, ((Rect)(ref rect)).width, ((Rect)(ref rect)).height - 20f), localSpecificHealthTabForPawn, false, true, (Thing)(object)localSpecificHealthTabForPawn);
					if (Widgets.CloseButtonFor(GenUI.AtZero(rect)))
					{
						specificHealthTabForPawn = null;
						SoundStarter.PlayOneShotOnCamera(SoundDefOf.TabClose, (Map)null);
					}
				}
			}, true, false, 1f, (Action)null, false);
		}

		private void DoColumnHeaders(ref float curY)
		{
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_0031: Unknown result type (might be due to invalid IL or missing references)
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0067: Unknown result type (might be due to invalid IL or missing references)
			//IL_0073: Unknown result type (might be due to invalid IL or missing references)
			//IL_007e: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
			if (!compactMode)
			{
				float num = 135f;
				Text.Anchor = (TextAnchor)1;
				GUI.color = Widgets.SeparatorLabelColor;
				Widgets.Label(new Rect(num, 3f, 100f, 100f), Translator.Translate("Pain"));
				num += 100f;
				List<PawnCapacityDef> list = CapacitiesToDisplay;
				for (int i = 0; i < list.Count; i++)
				{
					Widgets.Label(new Rect(num, 3f, 100f, 100f), GenText.Truncate(((Def)list[i]).LabelCap, 100f, (Dictionary<string, TaggedString>)null));
					num += 100f;
				}
				Text.Anchor = (TextAnchor)0;
				GUI.color = Color.white;
			}
		}

		private void DoRows(ref float curY, Rect scrollViewRect, Rect scrollOutRect)
		{
			//IL_005f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			//IL_004c: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
			//IL_009f: Unknown result type (might be due to invalid IL or missing references)
			List<Pawn> pawns = Pawns;
			if (specificHealthTabForPawn != null && !pawns.Contains(specificHealthTabForPawn))
			{
				specificHealthTabForPawn = null;
			}
			bool flag = false;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn val = pawns[i];
				if (val.IsColonist)
				{
					if (!flag)
					{
						Widgets.ListSeparator(ref curY, ((Rect)(ref scrollViewRect)).width, TaggedString.op_Implicit(Translator.Translate("CaravanColonists")));
						flag = true;
					}
					DoRow(ref curY, scrollViewRect, scrollOutRect, val);
				}
			}
			bool flag2 = false;
			for (int j = 0; j < pawns.Count; j++)
			{
				Pawn val2 = pawns[j];
				if (!val2.IsColonist)
				{
					if (!flag2)
					{
						Widgets.ListSeparator(ref curY, ((Rect)(ref scrollViewRect)).width, TaggedString.op_Implicit(Translator.Translate("CaravanPrisonersAndAnimals")));
						flag2 = true;
					}
					DoRow(ref curY, scrollViewRect, scrollOutRect, val2);
				}
			}
		}

		private Vector2 GetRawSize(bool compactMode)
		{
			//IL_005e: Unknown result type (might be due to invalid IL or missing references)
			float num = 100f;
			if (!compactMode)
			{
				num += 100f;
				num += (float)CapacitiesToDisplay.Count * 100f;
				num += 40f;
			}
			Vector2 result = default(Vector2);
			result.x = 127f + num + 16f;
			result.y = Mathf.Min(550f, ((InspectTabBase)this).PaneTopY - 30f);
			return result;
		}

		private void DoRow(ref float curY, Rect viewRect, Rect scrollOutRect, Pawn p)
		{
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			float num = scrollPosition.y - 40f;
			float num2 = scrollPosition.y + ((Rect)(ref scrollOutRect)).height;
			if (curY > num && curY < num2)
			{
				DoRow(new Rect(0f, curY, ((Rect)(ref viewRect)).width, 40f), p);
			}
			curY += 40f;
		}

		private void DoRow(Rect rect, Pawn p)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_0067: Unknown result type (might be due to invalid IL or missing references)
			//IL_0074: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
			//IL_007c: Unknown result type (might be due to invalid IL or missing references)
			//IL_022e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0256: Unknown result type (might be due to invalid IL or missing references)
			//IL_0130: Unknown result type (might be due to invalid IL or missing references)
			//IL_01e5: Unknown result type (might be due to invalid IL or missing references)
			GUI.BeginGroup(rect);
			Rect val = GenUI.AtZero(rect);
			Widgets.InfoCardButton(((Rect)(ref val)).width - 24f, (((Rect)(ref rect)).height - 24f) / 2f, (Thing)(object)p);
			((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
			CaravanThingsTabUtility.DoOpenSpecificTabButton(val, p, ref specificHealthTabForPawn);
			((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
			CaravanThingsTabUtility.DoOpenSpecificTabButtonInvisible(val, p, ref specificHealthTabForPawn);
			if (Mouse.IsOver(val))
			{
				Widgets.DrawHighlight(val);
			}
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(4f, (((Rect)(ref rect)).height - 27f) / 2f, 27f, 27f);
			Widgets.ThingIcon(val2, (Thing)(object)p, 1f, (Rot4?)null, false, 1f, false);
			Rect val3 = default(Rect);
			((Rect)(ref val3))..ctor(((Rect)(ref val2)).xMax + 4f, 11f, 100f, 18f);
			GenMapUI.DrawPawnLabel(p, val3, 1f, 100f, (Dictionary<string, string>)null, (GameFont)1, false, false);
			float xMax = ((Rect)(ref val3)).xMax;
			if (!compactMode)
			{
				if (p.RaceProps.IsFlesh)
				{
					DoPain(new Rect(xMax, 0f, 100f, 40f), p);
				}
				xMax += 100f;
				List<PawnCapacityDef> list = CapacitiesToDisplay;
				Rect rect2 = default(Rect);
				for (int i = 0; i < list.Count; i++)
				{
					((Rect)(ref rect2))..ctor(xMax, 0f, 100f, 40f);
					if ((p.RaceProps.Humanlike && !list[i].showOnHumanlikes) || (p.RaceProps.Animal && !list[i].showOnAnimals) || (p.RaceProps.IsMechanoid && !list[i].showOnMechanoids) || !PawnCapacityUtility.BodyCanEverDoCapacity(p.RaceProps.body, list[i]))
					{
						xMax += 100f;
						continue;
					}
					DoCapacity(rect2, p, list[i]);
					xMax += 100f;
				}
			}
			if (p.Downed)
			{
				GUI.color = new Color(1f, 0f, 0f, 0.5f);
				Widgets.DrawLineHorizontal(0f, ((Rect)(ref rect)).height / 2f, ((Rect)(ref rect)).width);
				GUI.color = Color.white;
			}
			GUI.EndGroup();
		}

		private static void DoPain(Rect rect, Pawn pawn)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0053: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			Pair<string, Color> painLabel = HealthCardUtility.GetPainLabel(pawn);
			if (Mouse.IsOver(rect))
			{
				Widgets.DrawHighlight(rect);
			}
			GUI.color = painLabel.Second;
			Text.Anchor = (TextAnchor)4;
			Widgets.Label(rect, painLabel.First);
			GUI.color = Color.white;
			Text.Anchor = (TextAnchor)0;
			if (Mouse.IsOver(rect))
			{
				string painTip = HealthCardUtility.GetPainTip(pawn);
				TooltipHandler.TipRegion(rect, TipSignal.op_Implicit(painTip));
			}
		}

		private static void DoCapacity(Rect rect, Pawn pawn, PawnCapacityDef capacity)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_0028: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Unknown result type (might be due to invalid IL or missing references)
			//IL_0045: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			Pair<string, Color> efficiencyLabel = HealthCardUtility.GetEfficiencyLabel(pawn, capacity);
			if (Mouse.IsOver(rect))
			{
				Widgets.DrawHighlight(rect);
			}
			GUI.color = efficiencyLabel.Second;
			Text.Anchor = (TextAnchor)4;
			Widgets.Label(rect, efficiencyLabel.First);
			GUI.color = Color.white;
			Text.Anchor = (TextAnchor)0;
			if (Mouse.IsOver(rect))
			{
				string pawnCapacityTip = HealthCardUtility.GetPawnCapacityTip(pawn, capacity);
				TooltipHandler.TipRegion(rect, TipSignal.op_Implicit(pawnCapacityTip));
			}
		}

		public override void Notify_ClearingAllMapsMemory()
		{
			((InspectTabBase)this).Notify_ClearingAllMapsMemory();
			specificHealthTabForPawn = null;
		}

		private void EnsureSpecificHealthTabForPawnValid()
		{
			if (specificHealthTabForPawn != null && (((Thing)specificHealthTabForPawn).Destroyed || !SelOutpost.Has(specificHealthTabForPawn)))
			{
				specificHealthTabForPawn = null;
			}
		}
	}
	public class WITab_Outpost_Items : WITab
	{
		private const float SortersSpace = 25f;

		private List<TransferableImmutable> cachedItems = new List<TransferableImmutable>();

		private int cachedItemsCount;

		private int cachedItemsHash;

		private Vector2 scrollPosition;

		private float scrollViewHeight;

		private TransferableSorterDef sorter1;

		private TransferableSorterDef sorter2;

		public Outpost SelOutpost => ((WITab)this).SelObject as Outpost;

		public WITab_Outpost_Items()
		{
			((InspectTabBase)this).labelKey = "TabCaravanItems";
		}

		public override void UpdateSize()
		{
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Unknown result type (might be due to invalid IL or missing references)
			//IL_002e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			((InspectTabBase)this).UpdateSize();
			CheckCacheItems();
			((InspectTabBase)this).size = CaravanItemsTabUtility.GetSize(cachedItems, ((InspectTabBase)this).PaneTopY, true) - new Vector2(0f, 25f);
		}

		public override void FillTab()
		{
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			//IL_007e: Unknown result type (might be due to invalid IL or missing references)
			//IL_008d: Unknown result type (might be due to invalid IL or missing references)
			CheckCreateSorters();
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(0f, 0f, ((InspectTabBase)this).size.x, ((InspectTabBase)this).size.y);
			GUI.BeginGroup(GenUI.ContractedBy(val, 10f));
			TransferableUIUtility.DoTransferableSorters(sorter1, sorter2, (Action<TransferableSorterDef>)delegate(TransferableSorterDef x)
			{
				sorter1 = x;
				CacheItems();
			}, (Action<TransferableSorterDef>)delegate(TransferableSorterDef x)
			{
				sorter2 = x;
				CacheItems();
			});
			GUI.EndGroup();
			((Rect)(ref val)).yMin = ((Rect)(ref val)).yMin + 25f;
			GUI.BeginGroup(val);
			CheckCacheItems();
			DoRows(((Rect)(ref val)).size);
			GUI.EndGroup();
		}

		private void CheckCacheItems()
		{
			List<Thing> list = SelOutpost.Things.ToList();
			if (list.Count != cachedItemsCount)
			{
				CacheItems();
				return;
			}
			int num = 0;
			for (int i = 0; i < list.Count; i++)
			{
				num = Gen.HashCombineInt(num, ((object)list[i]).GetHashCode());
			}
			if (num != cachedItemsHash)
			{
				CacheItems();
			}
		}

		private void CacheItems()
		{
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0045: Expected O, but got Unknown
			CheckCreateSorters();
			cachedItems.Clear();
			List<Thing> list = SelOutpost.Things.ToList();
			int num = 0;
			for (int i = 0; i < list.Count; i++)
			{
				TransferableImmutable val = TransferableUtility.TransferableMatching<TransferableImmutable>(list[i], cachedItems, (TransferAsOneMode)0);
				if (val == null)
				{
					val = new TransferableImmutable();
					cachedItems.Add(val);
				}
				val.things.Add(list[i]);
				num = Gen.HashCombineInt(num, ((object)list[i]).GetHashCode());
			}
			cachedItems = cachedItems.OrderBy((TransferableImmutable tr) => (Transferable)(object)tr, (IComparer<Transferable>)sorter1.Comparer).ThenBy((TransferableImmutable tr) => (Transferable)(object)tr, (IComparer<Transferable>)sorter2.Comparer).ThenBy((Func<TransferableImmutable, float>)TransferableUIUtility.DefaultListOrderPriority)
				.ToList();
			cachedItemsCount = list.Count;
			cachedItemsHash = num;
		}

		[MethodImpl(MethodImplOptions.AggressiveInlining)]
		private void CheckCreateSorters()
		{
			if (sorter1 == null)
			{
				sorter1 = TransferableSorterDefOf.Category;
			}
			if (sorter2 == null)
			{
				sorter2 = TransferableSorterDefOf.MarketValue;
			}
		}

		private void DoRows(Vector2 size)
		{
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0057: Unknown result type (might be due to invalid IL or missing references)
			//IL_0072: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d6: Invalid comparison between Unknown and I4
			//IL_0095: Unknown result type (might be due to invalid IL or missing references)
			//IL_0096: Unknown result type (might be due to invalid IL or missing references)
			Text.Font = (GameFont)1;
			Rect val = GenUI.ContractedBy(new Rect(0f, 0f, size.x, size.y), 10f);
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(0f, 0f, ((Rect)(ref val)).width - 16f, scrollViewHeight);
			Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
			float curY = 0f;
			Widgets.ListSeparator(ref curY, ((Rect)(ref val2)).width, TaggedString.op_Implicit(Translator.Translate("CaravanItems")));
			if (GenCollection.Any<TransferableImmutable>(cachedItems))
			{
				for (int i = 0; i < cachedItems.Count; i++)
				{
					DoRow(ref curY, val2, val, cachedItems[i]);
				}
			}
			else
			{
				Widgets.NoneLabel(ref curY, ((Rect)(ref val2)).width, (string)null);
			}
			if ((int)Event.current.type == 8)
			{
				scrollViewHeight = curY + 30f;
			}
			Widgets.EndScrollView();
		}

		private void DoRow(ref float curY, Rect viewRect, Rect scrollOutRect, TransferableImmutable thing)
		{
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			float num = scrollPosition.y - 30f;
			float num2 = scrollPosition.y + ((Rect)(ref scrollOutRect)).height;
			if (curY > num && curY < num2)
			{
				DoRow(new Rect(0f, curY, ((Rect)(ref viewRect)).width, 30f), thing);
			}
			curY += 30f;
		}

		private void DoRow(Rect rect, TransferableImmutable thing)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_004c: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0063: Unknown result type (might be due to invalid IL or missing references)
			//IL_007c: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
			GUI.BeginGroup(rect);
			Rect val = GenUI.AtZero(rect);
			Widgets.InfoCardButton(((Rect)(ref val)).width - 24f, (((Rect)(ref rect)).height - 24f) / 2f, ((Transferable)thing).AnyThing);
			((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
			Rect val2 = val;
			((Rect)(ref val2)).xMin = ((Rect)(ref val2)).xMax - 60f;
			CaravanThingsTabUtility.DrawMass(thing, val2);
			((Rect)(ref val)).width = ((Rect)(ref val)).width - 60f;
			Widgets.DrawHighlightIfMouseover(val);
			Rect val3 = default(Rect);
			((Rect)(ref val3))..ctor(4f, (((Rect)(ref rect)).height - 27f) / 2f, 27f, 27f);
			Widgets.ThingIcon(val3, ((Transferable)thing).AnyThing, 1f, (Rot4?)null, false, 1f, false);
			Rect val4 = default(Rect);
			((Rect)(ref val4))..ctor(((Rect)(ref val3)).xMax + 4f, 0f, 300f, 30f);
			Text.Anchor = (TextAnchor)3;
			Text.WordWrap = false;
			Widgets.Label(val4, GenText.Truncate(thing.LabelCapWithTotalStackCount, ((Rect)(ref val4)).width, (Dictionary<string, string>)null));
			Text.Anchor = (TextAnchor)0;
			Text.WordWrap = true;
			GUI.EndGroup();
		}
	}
	public class WITab_Outpost_Needs : WITab
	{
		private static readonly List<Need> needsToDisplay = new List<Need>();

		private static readonly List<Thought> thoughtGroupsPresent = new List<Thought>();

		private static readonly List<Thought> thoughtGroup = new List<Thought>();

		private bool doNeeds;

		private Vector2 scrollPosition;

		private float scrollViewHeight;

		private Pawn specificNeedsTabForPawn;

		private Vector2 thoughtScrollPosition;

		public Outpost SelOutpost => ((WITab)this).SelObject as Outpost;

		private float SpecificNeedsTabWidth
		{
			get
			{
				//IL_0013: Unknown result type (might be due to invalid IL or missing references)
				if (!ThingUtility.DestroyedOrNull((Thing)(object)specificNeedsTabForPawn))
				{
					return NeedsCardUtility.GetSize(specificNeedsTabForPawn).x;
				}
				return 0f;
			}
		}

		private List<Pawn> Pawns => SelOutpost.AllPawns.ToList();

		public WITab_Outpost_Needs()
		{
			((InspectTabBase)this).labelKey = "TabCaravanNeeds";
		}

		public override void Notify_ClearingAllMapsMemory()
		{
			((InspectTabBase)this).Notify_ClearingAllMapsMemory();
			specificNeedsTabForPawn = null;
		}

		public override void UpdateSize()
		{
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0053: Unknown result type (might be due to invalid IL or missing references)
			//IL_0058: Unknown result type (might be due to invalid IL or missing references)
			EnsureSpecificNeedsTabForPawnValid();
			((InspectTabBase)this).UpdateSize();
			((InspectTabBase)this).size = CaravanNeedsTabUtility.GetSize(Pawns, ((InspectTabBase)this).PaneTopY, true);
			if (((InspectTabBase)this).size.x + SpecificNeedsTabWidth > (float)UI.screenWidth)
			{
				doNeeds = false;
				((InspectTabBase)this).size = CaravanNeedsTabUtility.GetSize(Pawns, ((InspectTabBase)this).PaneTopY, false);
			}
			else
			{
				doNeeds = true;
			}
			((InspectTabBase)this).size.y = Mathf.Max(((InspectTabBase)this).size.y, NeedsCardUtility.FullSize.y);
		}

		public override void ExtraOnGUI()
		{
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_0059: Unknown result type (might be due to invalid IL or missing references)
			//IL_005e: Unknown result type (might be due to invalid IL or missing references)
			//IL_006e: Unknown result type (might be due to invalid IL or missing references)
			EnsureSpecificNeedsTabForPawnValid();
			((InspectTabBase)this).ExtraOnGUI();
			Pawn localSpecificNeedsTabForPawn = specificNeedsTabForPawn;
			if (localSpecificNeedsTabForPawn == null)
			{
				return;
			}
			Rect tabRect = ((InspectTabBase)this).TabRect;
			float specificNeedsTabWidth = SpecificNeedsTabWidth;
			Rect rect = new Rect(((Rect)(ref tabRect)).xMax - 1f, ((Rect)(ref tabRect)).yMin, specificNeedsTabWidth, ((Rect)(ref tabRect)).height);
			Find.WindowStack.ImmediateWindow(1439870015, rect, (WindowLayer)0, (Action)delegate
			{
				//IL_000f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0014: Unknown result type (might be due to invalid IL or missing references)
				//IL_0030: Unknown result type (might be due to invalid IL or missing references)
				//IL_0035: Unknown result type (might be due to invalid IL or missing references)
				if (!ThingUtility.DestroyedOrNull((Thing)(object)localSpecificNeedsTabForPawn))
				{
					NeedsCardUtility.DoNeedsMoodAndThoughts(GenUI.AtZero(rect), localSpecificNeedsTabForPawn, ref thoughtScrollPosition);
					if (Widgets.CloseButtonFor(GenUI.AtZero(rect)))
					{
						specificNeedsTabForPawn = null;
						SoundStarter.PlayOneShotOnCamera(SoundDefOf.TabClose, (Map)null);
					}
				}
			}, true, false, 1f, (Action)null, false);
		}

		private void EnsureSpecificNeedsTabForPawnValid()
		{
			if (specificNeedsTabForPawn != null && (((Thing)specificNeedsTabForPawn).Destroyed || !SelOutpost.Has(specificNeedsTabForPawn)))
			{
				specificNeedsTabForPawn = null;
			}
		}

		public override void FillTab()
		{
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			EnsureSpecificNeedsTabForPawnValid();
			DoRows(((InspectTabBase)this).size, Pawns);
		}

		private void DoRow(ref float curY, Rect viewRect, Rect scrollOutRect, Pawn pawn)
		{
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			float num = scrollPosition.y - 40f;
			float num2 = scrollPosition.y + ((Rect)(ref scrollOutRect)).height;
			if (curY > num && curY < num2)
			{
				DoRow(new Rect(0f, curY, ((Rect)(ref viewRect)).width, 40f), pawn);
			}
			curY += 40f;
		}

		private void DoRows(Vector2 size, List<Pawn> pawns)
		{
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0040: Unknown result type (might be due to invalid IL or missing references)
			//IL_0046: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_007a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0081: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
			//IL_0146: Unknown result type (might be due to invalid IL or missing references)
			//IL_014c: Invalid comparison between Unknown and I4
			//IL_0128: Unknown result type (might be due to invalid IL or missing references)
			//IL_0129: Unknown result type (might be due to invalid IL or missing references)
			//IL_0113: Unknown result type (might be due to invalid IL or missing references)
			if (specificNeedsTabForPawn != null && (!pawns.Contains(specificNeedsTabForPawn) || specificNeedsTabForPawn.Dead))
			{
				specificNeedsTabForPawn = null;
			}
			Text.Font = (GameFont)1;
			Rect val = GenUI.ContractedBy(new Rect(0f, 0f, size.x, size.y), 10f);
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(0f, 0f, ((Rect)(ref val)).width - 16f, scrollViewHeight);
			Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
			float curY = 0f;
			bool flag = false;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn val3 = pawns[i];
				if (val3.IsColonist)
				{
					if (!flag)
					{
						Widgets.ListSeparator(ref curY, ((Rect)(ref val2)).width, TaggedString.op_Implicit(Translator.Translate("CaravanColonists")));
						flag = true;
					}
					DoRow(ref curY, val2, val, val3);
				}
			}
			bool flag2 = false;
			for (int j = 0; j < pawns.Count; j++)
			{
				Pawn val4 = pawns[j];
				if (!val4.IsColonist)
				{
					if (!flag2)
					{
						Widgets.ListSeparator(ref curY, ((Rect)(ref val2)).width, TaggedString.op_Implicit(Translator.Translate("CaravanPrisonersAndAnimals")));
						flag2 = true;
					}
					DoRow(ref curY, val2, val, val4);
				}
			}
			if ((int)Event.current.type == 8)
			{
				scrollViewHeight = curY + 30f;
			}
			Widgets.EndScrollView();
		}

		private static void GetNeedsToDisplay(Pawn p)
		{
			needsToDisplay.Clear();
			List<Need> allNeeds = p.needs.AllNeeds;
			for (int i = 0; i < allNeeds.Count; i++)
			{
				Need val = allNeeds[i];
				if (val.def.showForCaravanMembers)
				{
					needsToDisplay.Add(val);
				}
			}
			PawnNeedsUIUtility.SortInDisplayOrder(needsToDisplay);
		}

		private void DoRow(Rect rect, Pawn pawn)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_007c: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
			//IL_00eb: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_006f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0221: Unknown result type (might be due to invalid IL or missing references)
			//IL_0249: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a0: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a2: Unknown result type (might be due to invalid IL or missing references)
			//IL_01cc: Unknown result type (might be due to invalid IL or missing references)
			//IL_01d8: Unknown result type (might be due to invalid IL or missing references)
			//IL_0171: Unknown result type (might be due to invalid IL or missing references)
			//IL_017a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0196: Unknown result type (might be due to invalid IL or missing references)
			GUI.BeginGroup(rect);
			Rect val = GenUI.AtZero(rect);
			Widgets.InfoCardButton(((Rect)(ref val)).width - 24f, (((Rect)(ref rect)).height - 24f) / 2f, (Thing)(object)pawn);
			((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
			if (!pawn.Dead)
			{
				CaravanThingsTabUtility.DoOpenSpecificTabButton(val, pawn, ref specificNeedsTabForPawn);
				((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
				CaravanThingsTabUtility.DoOpenSpecificTabButtonInvisible(val, pawn, ref specificNeedsTabForPawn);
			}
			Widgets.DrawHighlightIfMouseover(val);
			Rect val2 = default(Rect);
			((Rect)(ref val2))..ctor(4f, (((Rect)(ref rect)).height - 27f) / 2f, 27f, 27f);
			Widgets.ThingIcon(val2, (Thing)(object)pawn, 1f, (Rot4?)null, false, 1f, false);
			Rect val3 = default(Rect);
			((Rect)(ref val3))..ctor(((Rect)(ref val2)).xMax + 4f, 11f, 100f, 18f);
			GenMapUI.DrawPawnLabel(pawn, val3, 1f, 100f, (Dictionary<string, string>)null, (GameFont)1, false, false);
			if (doNeeds)
			{
				GetNeedsToDisplay(pawn);
				float xMax = ((Rect)(ref val3)).xMax;
				Rect val5 = default(Rect);
				for (int i = 0; i < needsToDisplay.Count; i++)
				{
					Need val4 = needsToDisplay[i];
					int num = 0;
					bool flag = true;
					((Rect)(ref val5))..ctor(xMax, 0f, 100f, 40f);
					Need_Mood mood = (Need_Mood)(object)((val4 is Need_Mood) ? val4 : null);
					if (mood != null)
					{
						num = 1;
						flag = false;
						if (Mouse.IsOver(val5))
						{
							TooltipHandler.TipRegion(val5, new TipSignal((Func<string>)(() => CustomMoodNeedTooltip(mood)), ((object)(Rect)(ref val5)/*cast due to .constrained prefix*/).GetHashCode()));
						}
					}
					Rect val6 = val5;
					((Rect)(ref val6)).yMin = ((Rect)(ref val6)).yMin - 5f;
					((Rect)(ref val6)).yMax = ((Rect)(ref val6)).yMax + 5f;
					val4.DrawOnGUI(val6, num, 10f, false, flag, (Rect?)val5, true);
					xMax = ((Rect)(ref val5)).xMax;
				}
			}
			if (pawn.Downed)
			{
				GUI.color = new Color(1f, 0f, 0f, 0.5f);
				Widgets.DrawLineHorizontal(0f, ((Rect)(ref rect)).height / 2f, ((Rect)(ref rect)).width);
				GUI.color = Color.white;
			}
			GUI.EndGroup();
		}

		private static string CustomMoodNeedTooltip(Need_Mood mood)
		{
			StringBuilder stringBuilder = new StringBuilder();
			stringBuilder.Append(((Need)mood).GetTipString());
			PawnNeedsUIUtility.GetThoughtGroupsInDisplayOrder(mood, thoughtGroupsPresent);
			bool flag = false;
			for (int i = 0; i < thoughtGroupsPresent.Count; i++)
			{
				Thought val = thoughtGroupsPresent[i];
				mood.thoughts.GetMoodThoughts(val, thoughtGroup);
				Thought leadingThoughtInGroup = PawnNeedsUIUtility.GetLeadingThoughtInGroup(thoughtGroup);
				if (leadingThoughtInGroup.VisibleInNeedsTab)
				{
					if (!flag)
					{
						flag = true;
						stringBuilder.AppendLine();
					}
					stringBuilder.Append(leadingThoughtInGroup.LabelCap);
					if (thoughtGroup.Count > 1)
					{
						stringBuilder.Append(" x");
						stringBuilder.Append(thoughtGroup.Count);
					}
					stringBuilder.Append(": ");
					stringBuilder.AppendLine(mood.thoughts.MoodOffsetOfGroup(val).ToString("##0"));
				}
			}
			return stringBuilder.ToString();
		}
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.0.0.9375' (yours is '9.0.0.7889')
