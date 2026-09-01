using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(CompHasGatherableBodyResource), "Gathered")]
public static class CompHasGatherableBodyResourcePatches
{
	[CompilerGenerated]
	private sealed class _003CGathered_Transpiler_003Ed__2 : IEnumerable<CodeInstruction>, IEnumerable, IEnumerator<CodeInstruction>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private CodeInstruction _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		private IEnumerable<CodeInstruction> instructions;

		public IEnumerable<CodeInstruction> _003C_003E3__instructions;

		private MethodInfo _003CresourceAmountGetter_003E5__2;

		private IEnumerator<CodeInstruction> _003C_003E7__wrap2;

		private CodeInstruction _003Cinstruction_003E5__4;

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
		public _003CGathered_Transpiler_003Ed__2(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			int num = _003C_003E1__state;
			if (num == -3 || (uint)(num - 1) <= 3u)
			{
				try
				{
				}
				finally
				{
					_003C_003Em__Finally1();
				}
			}
			_003CresourceAmountGetter_003E5__2 = null;
			_003C_003E7__wrap2 = null;
			_003Cinstruction_003E5__4 = null;
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fb: Expected O, but got Unknown
			//IL_0119: Unknown result type (might be due to invalid IL or missing references)
			//IL_0123: Expected O, but got Unknown
			//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c1: Expected O, but got Unknown
			try
			{
				switch (_003C_003E1__state)
				{
				default:
					return false;
				case 0:
					_003C_003E1__state = -1;
					_003CresourceAmountGetter_003E5__2 = AccessTools.PropertyGetter(typeof(CompHasGatherableBodyResource), "ResourceAmount");
					_003C_003E7__wrap2 = instructions.GetEnumerator();
					_003C_003E1__state = -3;
					break;
				case 1:
					_003C_003E1__state = -3;
					if (CodeInstructionExtensions.Calls(_003Cinstruction_003E5__4, _003CresourceAmountGetter_003E5__2))
					{
						_003C_003E2__current = new CodeInstruction(OpCodes.Ldarg_0, (object)null);
						_003C_003E1__state = 2;
						return true;
					}
					goto IL_0136;
				case 2:
					_003C_003E1__state = -3;
					_003C_003E2__current = new CodeInstruction(OpCodes.Ldfld, (object)AccessTools.Field(typeof(ThingComp), "parent"));
					_003C_003E1__state = 3;
					return true;
				case 3:
					_003C_003E1__state = -3;
					_003C_003E2__current = new CodeInstruction(OpCodes.Call, (object)newResourceAmountMI);
					_003C_003E1__state = 4;
					return true;
				case 4:
					{
						_003C_003E1__state = -3;
						goto IL_0136;
					}
					IL_0136:
					_003Cinstruction_003E5__4 = null;
					break;
				}
				if (_003C_003E7__wrap2.MoveNext())
				{
					_003Cinstruction_003E5__4 = _003C_003E7__wrap2.Current;
					_003C_003E2__current = _003Cinstruction_003E5__4;
					_003C_003E1__state = 1;
					return true;
				}
				_003C_003Em__Finally1();
				_003C_003E7__wrap2 = null;
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
			if (_003C_003E7__wrap2 != null)
			{
				_003C_003E7__wrap2.Dispose();
			}
		}

		[DebuggerHidden]
		void IEnumerator.Reset()
		{
			throw new NotSupportedException();
		}

		[DebuggerHidden]
		IEnumerator<CodeInstruction> IEnumerable<CodeInstruction>.GetEnumerator()
		{
			_003CGathered_Transpiler_003Ed__2 _003CGathered_Transpiler_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CGathered_Transpiler_003Ed__ = this;
			}
			else
			{
				_003CGathered_Transpiler_003Ed__ = new _003CGathered_Transpiler_003Ed__2(0);
			}
			_003CGathered_Transpiler_003Ed__.instructions = _003C_003E3__instructions;
			return _003CGathered_Transpiler_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<CodeInstruction>)this).GetEnumerator();
		}
	}

	private static MethodInfo newResourceAmountMI = AccessTools.Method(typeof(CompHasGatherableBodyResourcePatches), "GetModifiedProductionAmount", (Type[])null, (Type[])null);

	public static int GetModifiedProductionAmount(int resourceAmount, ThingWithComps thing)
	{
		if (thing != null)
		{
			Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
			if (val != null)
			{
				return ProductionGene.ModifyProductionBasedOnSize(resourceAmount, val);
			}
		}
		Log.Warning("GetModifiedProductionAmount could not modify production amount because " + ((Entity)thing).Label + " is not a Pawn. Returning original resource amount.");
		return resourceAmount;
	}

	[IteratorStateMachine(typeof(_003CGathered_Transpiler_003Ed__2))]
	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> Gathered_Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CGathered_Transpiler_003Ed__2(-2)
		{
			_003C_003E3__instructions = instructions
		};
	}
}
