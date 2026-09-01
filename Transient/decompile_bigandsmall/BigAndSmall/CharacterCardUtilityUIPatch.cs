using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class CharacterCardUtilityUIPatch
{
	[CompilerGenerated]
	private sealed class _003CDoTopStack_Transpiler_003Ed__4 : IEnumerable<CodeInstruction>, IEnumerable, IEnumerator<CodeInstruction>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private CodeInstruction _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		private IEnumerable<CodeInstruction> instructions;

		public IEnumerable<CodeInstruction> _003C_003E3__instructions;

		private List<CodeInstruction> _003Ccodes_003E5__2;

		private bool _003Cfound_003E5__3;

		private int _003Ci_003E5__4;

		CodeInstruction IEnumerator<CodeInstruction>.Current
		{
			[DebuggerHidden]
			get
			{
				return _003C_003E2__current;
			}
		}

		object IEnumerator.Current
		{
			[DebuggerHidden]
			get
			{
				return _003C_003E2__current;
			}
		}

		[DebuggerHidden]
		public _003CDoTopStack_Transpiler_003Ed__4(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			_003Ccodes_003E5__2 = null;
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			//IL_00eb: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f5: Expected O, but got Unknown
			//IL_010c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0116: Expected O, but got Unknown
			//IL_0142: Unknown result type (might be due to invalid IL or missing references)
			//IL_014c: Expected O, but got Unknown
			//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bf: Expected O, but got Unknown
			switch (_003C_003E1__state)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				_003Ccodes_003E5__2 = instructions.ToList();
				_003Cfound_003E5__3 = false;
				_003Ci_003E5__4 = 0;
				goto IL_0193;
			case 1:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(CharacterCardUtilityUIPatch), "InsertPawnMutationWindow", (Type[])null, (Type[])null));
				_003C_003E1__state = 2;
				return true;
			case 2:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				_003C_003E1__state = 3;
				return true;
			case 3:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(CharacterCardUtilityUIPatch), "InsertEditPawnApperanceWindow", (Type[])null, (Type[])null));
				_003C_003E1__state = 4;
				return true;
			case 4:
				_003C_003E1__state = -1;
				goto IL_015c;
			case 5:
				{
					_003C_003E1__state = -1;
					_003Ci_003E5__4++;
					goto IL_0193;
				}
				IL_0193:
				if (_003Ci_003E5__4 < _003Ccodes_003E5__2.Count)
				{
					if (!_003Cfound_003E5__3 && _003Ccodes_003E5__2[_003Ci_003E5__4].opcode == OpCodes.Ldc_R4 && (float)_003Ccodes_003E5__2[_003Ci_003E5__4].operand == 44f)
					{
						_003Cfound_003E5__3 = true;
						_003C_003E2__current = new CodeInstruction(OpCodes.Ldarg_0, (object)null);
						_003C_003E1__state = 1;
						return true;
					}
					goto IL_015c;
				}
				if (!_003Cfound_003E5__3)
				{
					Log.Error("[BigAndSmall] Failed to apply CharacterCardUtilityUI transpiler.");
				}
				return false;
				IL_015c:
				_003C_003E2__current = _003Ccodes_003E5__2[_003Ci_003E5__4];
				_003C_003E1__state = 5;
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
			_003CDoTopStack_Transpiler_003Ed__4 _003CDoTopStack_Transpiler_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CDoTopStack_Transpiler_003Ed__ = this;
			}
			else
			{
				_003CDoTopStack_Transpiler_003Ed__ = new _003CDoTopStack_Transpiler_003Ed__4(0);
			}
			_003CDoTopStack_Transpiler_003Ed__.instructions = _003C_003E3__instructions;
			return _003CDoTopStack_Transpiler_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<CodeInstruction>)this).GetEnumerator();
		}
	}

	public static readonly Color StackElementBackground = new Color(1f, 1f, 1f, 0.1f);

	[CompilerGenerated]
	private static string _003CBSEditPawnTooltip_003Ek__BackingField;

	public static string BSEditPawnTooltip => _003CBSEditPawnTooltip_003Ek__BackingField ?? (_003CBSEditPawnTooltip_003Ek__BackingField = TaggedString.op_Implicit(Translator.Translate("BS_EditPawnTooltip")));

	[IteratorStateMachine(typeof(_003CDoTopStack_Transpiler_003Ed__4))]
	[HarmonyPatch(typeof(CharacterCardUtility), "DoTopStack")]
	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> DoTopStack_Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CDoTopStack_Transpiler_003Ed__4(-2)
		{
			_003C_003E3__instructions = instructions
		};
	}

	public static void InsertEditPawnApperanceWindow(Pawn pawn)
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Expected O, but got Unknown
		if (!BigSmall.ShowPalette)
		{
			return;
		}
		CharacterCardUtility.tmpStackElements.Add(new AnonymousStackElement
		{
			drawer = delegate(Rect inRect)
			{
				//IL_0000: Unknown result type (might be due to invalid IL or missing references)
				//IL_000a: Unknown result type (might be due to invalid IL or missing references)
				//IL_0012: Unknown result type (might be due to invalid IL or missing references)
				//IL_001c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0031: Unknown result type (might be due to invalid IL or missing references)
				//IL_004f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0055: Unknown result type (might be due to invalid IL or missing references)
				//IL_005f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0067: Unknown result type (might be due to invalid IL or missing references)
				GUI.color = StackElementBackground;
				Widgets.DrawBox(inRect, 1, (Texture2D)null);
				GUI.color = Color.white;
				Widgets.DrawTextureFitted(inRect, (Texture)(object)Textures.ColorPawn_Icon, 1f, 1f);
				if (Widgets.ButtonInvisible(inRect, true))
				{
					Find.WindowStack.Add((Window)(object)new EditPawnWindow((ILoadReferenceable)(object)pawn));
				}
				TooltipHandler.TipRegion(inRect, TipSignal.op_Implicit(BSEditPawnTooltip));
				if (Mouse.IsOver(inRect))
				{
					Widgets.DrawHighlight(inRect);
				}
			},
			width = 22f
		});
	}

	public static void InsertPawnMutationWindow(Pawn pawn)
	{
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Expected O, but got Unknown
		if (((Thing)pawn).def == ThingDefOf.Human || !BigSmall.ShowRaceButton)
		{
			return;
		}
		CharacterCardUtility.tmpStackElements.Add(new AnonymousStackElement
		{
			drawer = delegate(Rect inRect)
			{
				//IL_0000: Unknown result type (might be due to invalid IL or missing references)
				//IL_000a: Unknown result type (might be due to invalid IL or missing references)
				//IL_0012: Unknown result type (might be due to invalid IL or missing references)
				//IL_001c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0031: Unknown result type (might be due to invalid IL or missing references)
				//IL_004f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0066: Unknown result type (might be due to invalid IL or missing references)
				//IL_006e: Unknown result type (might be due to invalid IL or missing references)
				GUI.color = StackElementBackground;
				Widgets.DrawBox(inRect, 1, (Texture2D)null);
				GUI.color = Color.white;
				Widgets.DrawTextureFitted(inRect, (Texture)(object)Textures.AlienIcon_Icon, 1f, 1f);
				if (Widgets.ButtonInvisible(inRect, true))
				{
					Find.WindowStack.Add((Window)(object)new Dialog_ViewMutations(pawn));
				}
				TooltipHandler.TipRegion(inRect, (Func<string>)delegate
				{
					//IL_0010: Unknown result type (might be due to invalid IL or missing references)
					//IL_0020: Unknown result type (might be due to invalid IL or missing references)
					//IL_0025: Unknown result type (might be due to invalid IL or missing references)
					//IL_002a: Unknown result type (might be due to invalid IL or missing references)
					//IL_002f: Unknown result type (might be due to invalid IL or missing references)
					TaggedString val = TranslatorFormattedStringExtensions.Translate("BS_ShowPawnRaceTooltip", NamedArgument.op_Implicit(((Entity)pawn).LabelCap), NamedArgument.op_Implicit(((Def)((Thing)pawn).def).LabelCap));
					return ((TaggedString)(ref val)).Resolve();
				}, 1289589431);
				if (Mouse.IsOver(inRect))
				{
					Widgets.DrawHighlight(inRect);
				}
			},
			width = 22f
		});
	}
}
