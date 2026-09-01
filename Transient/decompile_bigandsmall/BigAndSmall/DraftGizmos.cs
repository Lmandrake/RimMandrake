using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
[StaticConstructorOnStartup]
public static class DraftGizmos
{
	[CompilerGenerated]
	private sealed class _003C_003CGetGizmosPostfix_003Eg__UpdateEnumerable_007C10_0_003Ed : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Gizmo _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		private IEnumerable<Gizmo> gizmos;

		public IEnumerable<Gizmo> _003C_003E3__gizmos;

		private List<Command_ToggleWithRClick> commands;

		public List<Command_ToggleWithRClick> _003C_003E3__commands;

		private IEnumerator<Gizmo> _003C_003E7__wrap1;

		private List<Command_ToggleWithRClick>.Enumerator _003C_003E7__wrap2;

		Gizmo IEnumerator<Gizmo>.Current
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
		public _003C_003CGetGizmosPostfix_003Eg__UpdateEnumerable_007C10_0_003Ed(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			int num = _003C_003E1__state;
			if ((uint)(num - -4) <= 1u || (uint)(num - 1) <= 2u)
			{
				try
				{
					if (num == -4 || num == 2)
					{
						try
						{
						}
						finally
						{
							_003C_003Em__Finally2();
						}
					}
				}
				finally
				{
					_003C_003Em__Finally1();
				}
			}
			_003C_003E7__wrap1 = null;
			_003C_003E7__wrap2 = default(List<Command_ToggleWithRClick>.Enumerator);
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			try
			{
				switch (_003C_003E1__state)
				{
				default:
					return false;
				case 0:
					_003C_003E1__state = -1;
					_003C_003E7__wrap1 = gizmos.GetEnumerator();
					_003C_003E1__state = -3;
					break;
				case 1:
					_003C_003E1__state = -3;
					_003C_003E7__wrap2 = commands.GetEnumerator();
					_003C_003E1__state = -4;
					goto IL_00d7;
				case 2:
					_003C_003E1__state = -4;
					goto IL_00d7;
				case 3:
					{
						_003C_003E1__state = -3;
						break;
					}
					IL_00d7:
					if (_003C_003E7__wrap2.MoveNext())
					{
						Command_ToggleWithRClick current = _003C_003E7__wrap2.Current;
						_003C_003E2__current = (Gizmo)(object)current;
						_003C_003E1__state = 2;
						return true;
					}
					_003C_003Em__Finally2();
					_003C_003E7__wrap2 = default(List<Command_ToggleWithRClick>.Enumerator);
					break;
				}
				if (_003C_003E7__wrap1.MoveNext())
				{
					Gizmo current2 = _003C_003E7__wrap1.Current;
					Command_Toggle val = (Command_Toggle)(object)((current2 is Command_Toggle) ? current2 : null);
					if (val != null && (Object)(object)((Command)val).icon == (Object)(object)TexCommand.Draft)
					{
						_003C_003E2__current = (Gizmo)(object)val;
						_003C_003E1__state = 1;
						return true;
					}
					_003C_003E2__current = current2;
					_003C_003E1__state = 3;
					return true;
				}
				_003C_003Em__Finally1();
				_003C_003E7__wrap1 = null;
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

		private void _003C_003Em__Finally1()
		{
			_003C_003E1__state = -1;
			if (_003C_003E7__wrap1 != null)
			{
				_003C_003E7__wrap1.Dispose();
			}
		}

		private void _003C_003Em__Finally2()
		{
			_003C_003E1__state = -3;
			((IDisposable)_003C_003E7__wrap2/*cast due to .constrained prefix*/).Dispose();
		}

		[DebuggerHidden]
		void IEnumerator.Reset()
		{
			throw new NotSupportedException();
		}

		[DebuggerHidden]
		IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
		{
			_003C_003CGetGizmosPostfix_003Eg__UpdateEnumerable_007C10_0_003Ed _003C_003CGetGizmosPostfix_003Eg__UpdateEnumerable_007C10_0_003Ed;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003C_003CGetGizmosPostfix_003Eg__UpdateEnumerable_007C10_0_003Ed = this;
			}
			else
			{
				_003C_003CGetGizmosPostfix_003Eg__UpdateEnumerable_007C10_0_003Ed = new _003C_003CGetGizmosPostfix_003Eg__UpdateEnumerable_007C10_0_003Ed(0);
			}
			_003C_003CGetGizmosPostfix_003Eg__UpdateEnumerable_007C10_0_003Ed.gizmos = _003C_003E3__gizmos;
			_003C_003CGetGizmosPostfix_003Eg__UpdateEnumerable_007C10_0_003Ed.commands = _003C_003E3__commands;
			return _003C_003CGetGizmosPostfix_003Eg__UpdateEnumerable_007C10_0_003Ed;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<Gizmo>)this).GetEnumerator();
		}
	}

	public static readonly Texture2D AutoCastIcon = ContentFinder<Texture2D>.Get("BS_UI/Auto_Tiny", true);

	public static readonly Texture2D HuntIcon = ContentFinder<Texture2D>.Get("BS_UI/Hunt", true);

	public static readonly Texture2D TakeCoverIcon = ContentFinder<Texture2D>.Get("BS_UI/TakeCover", true);

	public static readonly Texture2D MeleeChargeIcon = ContentFinder<Texture2D>.Get("BS_UI/MeleeCharge", true);

	public static readonly Texture2D AIControlIcon = ContentFinder<Texture2D>.Get("BS_UI/AIControl", true);

	public static readonly Texture2D AutoUseAllIcon = ContentFinder<Texture2D>.Get("BS_UI/Auto_Large", true);

	private static bool? autoCombatModEnabled = null;

	public static bool AutoCombatEnabled
	{
		get
		{
			bool valueOrDefault = autoCombatModEnabled == true;
			if (!autoCombatModEnabled.HasValue)
			{
				valueOrDefault = ModsConfig.IsActive("RedMattis.AutoCombat");
				autoCombatModEnabled = valueOrDefault;
			}
			if (autoCombatModEnabled != true)
			{
				return BigSmall.IsAutoCombatEnabled;
			}
			return true;
		}
	}

	public static bool IsDraftedPlayerPawn(Pawn pawn)
	{
		if (((pawn != null) ? ((Thing)pawn).Faction : null) == Faction.OfPlayerSilentFail)
		{
			return pawn.Drafted;
		}
		return false;
	}

	[HarmonyPatch(typeof(Pawn_DraftController), "GetGizmos")]
	[HarmonyPostfix]
	[HarmonyPriority(200)]
	public static IEnumerable<Gizmo> GetGizmosPostfix(IEnumerable<Gizmo> __result, Pawn_DraftController __instance)
	{
		Pawn pawn = __instance.pawn;
		if (AutoCombatEnabled && IsDraftedPlayerPawn(pawn))
		{
			Command_ToggleWithRClick item = AddHuntGizmo(pawn);
			List<Command_ToggleWithRClick> list = new List<Command_ToggleWithRClick>(1) { item };
			DraftedActionData data = DraftedActionHolder.GetData(pawn);
			if (data.hunt)
			{
				if (BS.Settings.showTakeCoverBtn)
				{
					Command_ToggleWithRClick item2 = AddCoverGizmo(pawn);
					list.Add(item2);
				}
				if (BS.Settings.showMeleeChargeBtn)
				{
					Command_ToggleWithRClick item3 = AddChargeGizmo(pawn, data.fullAIControl);
					list.Add(item3);
				}
				if (BS.Settings.showAutoUseAllAbilitiesBtn)
				{
					Command_ToggleWithRClick item4 = AddToggleAllAbilitiesButton(pawn);
					list.Add(item4);
				}
				if (BS.Settings.showFullAIControlBtn)
				{
					Command_ToggleWithRClick item5 = AddAIControlGizmo(pawn);
					list.Add(item5);
				}
				return UpdateEnumerable(__result, list);
			}
			return UpdateEnumerable(__result, new List<Command_ToggleWithRClick>(1) { item });
		}
		return __result;
		[IteratorStateMachine(typeof(_003C_003CGetGizmosPostfix_003Eg__UpdateEnumerable_007C10_0_003Ed))]
		static IEnumerable<Gizmo> UpdateEnumerable(IEnumerable<Gizmo> gizmos, List<Command_ToggleWithRClick> commands)
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new _003C_003CGetGizmosPostfix_003Eg__UpdateEnumerable_007C10_0_003Ed(-2)
			{
				_003C_003E3__gizmos = gizmos,
				_003C_003E3__commands = commands
			};
		}
	}

	private static Command_ToggleWithRClick AddToggleAllAbilitiesButton(Pawn pawn)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		return new Command_ToggleWithRClick
		{
			defaultLabel = TaggedString.op_Implicit(Translator.Translate("BS_AutoUseAllAbilitiesLabel")),
			defaultDesc = TaggedString.op_Implicit(Translator.Translate("BS_AutoUseAllAbilitiesDescription")),
			icon = (Texture)(object)AutoUseAllIcon,
			isActive = () => !GenCollection.Empty<AbilityDef>(DraftedActionHolder.GetData(pawn).autocastAbilities),
			toggleAction = delegate
			{
				DraftedActionHolder.GetData(pawn).ToggleAutoForAll(null);
			},
			rightClickAction = delegate
			{
			},
			activateSound = SoundDefOf.Click,
			groupKey = 6173616,
			hotKey = KeyBindingDefOf.Misc6
		};
	}

	private static Command_ToggleWithRClick AddChargeGizmo(Pawn pawn, bool disabled)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		Command_ToggleWithRClick obj = new Command_ToggleWithRClick
		{
			defaultLabel = TaggedString.op_Implicit(Translator.Translate("BS_MeleeChargeLabel")),
			defaultDesc = TaggedString.op_Implicit(Translator.Translate("BS_MeleeChargeDescription")),
			icon = (Texture)(object)MeleeChargeIcon,
			isActive = () => DraftedActionHolder.GetData(pawn).meleeCharge,
			toggleAction = delegate
			{
				DraftedActionHolder.GetData(pawn).ToggleMeleeCharge(null);
			},
			rightClickAction = delegate
			{
			}
		};
		((Gizmo)obj).Disabled = disabled;
		((Command)obj).activateSound = SoundDefOf.Click;
		((Command)obj).groupKey = 6173615;
		((Command)obj).hotKey = KeyBindingDefOf.Misc5;
		return obj;
	}

	private static Command_ToggleWithRClick AddCoverGizmo(Pawn pawn)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		return new Command_ToggleWithRClick
		{
			defaultLabel = TaggedString.op_Implicit(Translator.Translate("BS_TakeCoverLabel")),
			defaultDesc = TaggedString.op_Implicit(Translator.Translate("BS_TakeCoverDescription")),
			icon = (Texture)(object)TakeCoverIcon,
			isActive = () => DraftedActionHolder.GetData(pawn).takeCover,
			toggleAction = delegate
			{
				DraftedActionHolder.GetData(pawn).ToggleCoverMode(null);
			},
			rightClickAction = delegate
			{
			},
			activateSound = SoundDefOf.Click,
			groupKey = 6173614
		};
	}

	private static Command_ToggleWithRClick AddHuntGizmo(Pawn pawn)
	{
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		Action rightClickAction = ((!BS.Settings.rightClickAutoCombatShowsMenu) ? ((Action)delegate
		{
			DraftedActionHolder.GetData(pawn).ToggleAutoForAll(null);
		}) : ((Action)delegate
		{
			ShowHuntContextMenu(pawn);
		}));
		return new Command_ToggleWithRClick
		{
			defaultLabel = TaggedString.op_Implicit(Translator.Translate("BS_DraftHuntLabel")),
			defaultDesc = TaggedString.op_Implicit(Translator.Translate("BS_HuntDescription")),
			icon = (Texture)(object)HuntIcon,
			isActive = () => DraftedActionHolder.GetData(pawn).hunt,
			toggleAction = delegate
			{
				DraftedActionHolder.GetData(pawn).ToggleHuntMode();
			},
			rightClickAction = rightClickAction,
			activateSound = SoundDefOf.Click,
			groupKey = 6173613,
			hotKey = KeyBindingDefOf.Misc3
		};
	}

	private static Command_ToggleWithRClick AddAIControlGizmo(Pawn pawn)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		return new Command_ToggleWithRClick
		{
			defaultLabel = TaggedString.op_Implicit(Translator.Translate("BS_FullAIControlLabel")),
			defaultDesc = TaggedString.op_Implicit(Translator.Translate("BS_FullAIControlDescription")),
			icon = (Texture)(object)AIControlIcon,
			isActive = () => DraftedActionHolder.GetData(pawn).fullAIControl,
			toggleAction = delegate
			{
				DraftedActionHolder.GetData(pawn).ToggleFullAIControl(null);
			},
			rightClickAction = delegate
			{
			},
			activateSound = SoundDefOf.Click,
			groupKey = 6173612,
			hotKey = KeyBindingDefOf.Misc4
		};
	}

	private static void ShowHuntContextMenu(Pawn pawn)
	{
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Expected O, but got Unknown
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00de: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Expected O, but got Unknown
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_011f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_0136: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Unknown result type (might be due to invalid IL or missing references)
		//IL_017c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0186: Expected O, but got Unknown
		//IL_018c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0196: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f0: Expected O, but got Unknown
		//IL_01f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0201: Expected O, but got Unknown
		bool takeCoverActive = DraftedActionHolder.GetData(pawn).takeCover;
		bool meleeChargeActive = DraftedActionHolder.GetData(pawn).meleeCharge;
		bool autoUseAllAbilitiesActive = DraftedActionHolder.GetData(pawn).autocastAbilities.Count > 0;
		List<FloatMenuOption> list = new List<FloatMenuOption>(4)
		{
			new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("BS_TakeCoverLabel") + " " + (DraftedActionHolder.GetData(pawn).takeCover ? Translator.Translate("BS_IsEnabledP") : Translator.Translate("BS_IsDisabledP"))), (Action)delegate
			{
				foreach (Pawn selectedPawn in Find.Selector.SelectedPawns)
				{
					DraftedActionHolder.GetData(selectedPawn).ToggleCoverMode(!takeCoverActive);
				}
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
			new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("BS_MeleeChargeLabel") + " " + (DraftedActionHolder.GetData(pawn).meleeCharge ? Translator.Translate("BS_IsEnabledP") : Translator.Translate("BS_IsDisabledP"))), (Action)delegate
			{
				foreach (Pawn selectedPawn2 in Find.Selector.SelectedPawns)
				{
					DraftedActionHolder.GetData(selectedPawn2).ToggleMeleeCharge(!meleeChargeActive);
				}
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
			new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("BS_FullAIControlLabel") + " " + (DraftedActionHolder.GetData(pawn).fullAIControl ? Translator.Translate("BS_IsEnabledP") : Translator.Translate("BS_IsDisabledP"))), (Action)delegate
			{
				foreach (Pawn selectedPawn3 in Find.Selector.SelectedPawns)
				{
					DraftedActionHolder.GetData(selectedPawn3).ToggleFullAIControl(!DraftedActionHolder.GetData(selectedPawn3).fullAIControl);
				}
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
			new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("BS_AutoUseAllAbilitiesLabel") + " " + ((DraftedActionHolder.GetData(pawn).autocastAbilities.Count > 0) ? Translator.Translate("BS_IsEnabledP") : Translator.Translate("BS_IsDisabledP"))), (Action)delegate
			{
				foreach (Pawn selectedPawn4 in Find.Selector.SelectedPawns)
				{
					DraftedActionHolder.GetData(selectedPawn4).ToggleAutoForAll(!autoUseAllAbilitiesActive);
				}
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0)
		};
		Find.WindowStack.Add((Window)new FloatMenu(list));
	}

	[HarmonyPatch(typeof(Command), "GizmoOnGUIInt")]
	[HarmonyPostfix]
	public static void GizmoOnGUIPostfix(Command __instance, GizmoResult __result, Rect butRect, GizmoRenderParms parms)
	{
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Invalid comparison between Unknown and I4
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		if (!(((object)__instance).GetType() == typeof(Command_Ability)))
		{
			return;
		}
		Command_Ability val = (Command_Ability)(object)((__instance is Command_Ability) ? __instance : null);
		Pawn pawn = val.Pawn;
		if (IsDraftedPlayerPawn(pawn) && AutoCombatEnabled)
		{
			DraftedActionData data = DraftedActionHolder.GetData(pawn);
			if (data.AutoCastFor(val.Ability.def))
			{
				float num = (parms.shrunk ? 12f : 24f);
				GUI.DrawTexture(new Rect(((Rect)(ref butRect)).x + ((Rect)(ref butRect)).width - num, ((Rect)(ref butRect)).y, num, num), (Texture)(object)AutoCastIcon);
			}
			if ((int)((GizmoResult)(ref __result)).State == 3)
			{
				data.ToggleAutoCastFor(val.Ability.def);
			}
		}
	}

	[HarmonyPatch(typeof(PriorityWork), "ClearPrioritizedWorkAndJobQueue")]
	[HarmonyPostfix]
	public static void ClearPrioritizedWorkAndJobQueuePostfix(PriorityWork __instance)
	{
		if (BigSmallMod.settings.autoCombatResets && !__instance.pawn.Drafted)
		{
			DraftedActionData data = DraftedActionHolder.GetData(__instance.pawn);
			if (data != null)
			{
				data.hunt = false;
			}
		}
		if (BigSmallMod.settings.autoCombatResetsLongCharge && !__instance.pawn.Drafted)
		{
			DraftedActionData data2 = DraftedActionHolder.GetData(__instance.pawn);
			if (data2 != null)
			{
				data2.meleeCharge = false;
			}
		}
	}
}
