using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace Outposts;

[StaticConstructorOnStartup]
public static class HarmonyPatches
{
	[CompilerGenerated]
	private sealed class _003C_003Ec__DisplayClass1_0
	{
		public Caravan __instance;

		internal bool _003CAddCaravanGizmos_003Eb__0(Outpost outpost)
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			return Find.WorldGrid.IsNeighborOrSame(((WorldObject)__instance).Tile, ((WorldObject)outpost).Tile);
		}

		internal void _003CAddCaravanGizmos_003Eb__2()
		{
			Find.WindowStack.Add((Window)(object)new Dialog_CreateCamp(__instance));
		}
	}

	[CompilerGenerated]
	private sealed class _003CAddCaravanGizmos_003Ed__1 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Gizmo _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		private Caravan __instance;

		public Caravan _003C_003E3____instance;

		private IEnumerable<Gizmo> gizmos;

		public IEnumerable<Gizmo> _003C_003E3__gizmos;

		private _003C_003Ec__DisplayClass1_0 _003C_003E8__1;

		private IEnumerator<Gizmo> _003C_003E7__wrap1;

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
		public _003CAddCaravanGizmos_003Ed__1(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			int num = _003C_003E1__state;
			if (num == -3 || num == 1)
			{
				try
				{
				}
				finally
				{
					_003C_003Em__Finally1();
				}
			}
			_003C_003E8__1 = null;
			_003C_003E7__wrap1 = null;
			_003C_003E1__state = -2;
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
				switch (_003C_003E1__state)
				{
				default:
					return false;
				case 0:
					_003C_003E1__state = -1;
					_003C_003E8__1 = new _003C_003Ec__DisplayClass1_0();
					_003C_003E8__1.__instance = __instance;
					_003C_003E7__wrap1 = gizmos.GetEnumerator();
					_003C_003E1__state = -3;
					goto IL_008b;
				case 1:
					_003C_003E1__state = -3;
					goto IL_008b;
				case 2:
					_003C_003E1__state = -1;
					break;
				case 3:
					{
						_003C_003E1__state = -1;
						break;
					}
					IL_008b:
					if (_003C_003E7__wrap1.MoveNext())
					{
						Gizmo current = _003C_003E7__wrap1.Current;
						_003C_003E2__current = current;
						_003C_003E1__state = 1;
						return true;
					}
					_003C_003Em__Finally1();
					_003C_003E7__wrap1 = null;
					if (Find.WorldObjects.AnySettlementBaseAtOrAdjacent(((WorldObject)_003C_003E8__1.__instance).Tile) || Find.WorldObjects.AllWorldObjects.OfType<Outpost>().Any((Outpost outpost) => Find.WorldGrid.IsNeighborOrSame(((WorldObject)_003C_003E8__1.__instance).Tile, ((WorldObject)outpost).Tile)))
					{
						_003C_003E2__current = (Gizmo)new Command_Action
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
						_003C_003E1__state = 2;
						return true;
					}
					_003C_003E2__current = (Gizmo)new Command_Action
					{
						action = delegate
						{
							Find.WindowStack.Add((Window)(object)new Dialog_CreateCamp(_003C_003E8__1.__instance));
						},
						defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Create.Label")),
						defaultDesc = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Create.Desc")),
						icon = (Texture)(object)TexOutposts.CreateTex
					};
					_003C_003E1__state = 3;
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

		private void _003C_003Em__Finally1()
		{
			_003C_003E1__state = -1;
			if (_003C_003E7__wrap1 != null)
			{
				_003C_003E7__wrap1.Dispose();
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
			_003CAddCaravanGizmos_003Ed__1 _003CAddCaravanGizmos_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CAddCaravanGizmos_003Ed__ = this;
			}
			else
			{
				_003CAddCaravanGizmos_003Ed__ = new _003CAddCaravanGizmos_003Ed__1(0);
			}
			_003CAddCaravanGizmos_003Ed__.gizmos = _003C_003E3__gizmos;
			_003CAddCaravanGizmos_003Ed__.__instance = _003C_003E3____instance;
			return _003CAddCaravanGizmos_003Ed__;
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

	[IteratorStateMachine(typeof(_003CAddCaravanGizmos_003Ed__1))]
	public static IEnumerable<Gizmo> AddCaravanGizmos(IEnumerable<Gizmo> gizmos, Caravan __instance)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CAddCaravanGizmos_003Ed__1(-2)
		{
			_003C_003E3__gizmos = gizmos,
			_003C_003E3____instance = __instance
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
