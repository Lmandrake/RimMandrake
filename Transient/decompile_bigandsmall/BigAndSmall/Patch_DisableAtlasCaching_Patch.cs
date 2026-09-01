using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class Patch_DisableAtlasCaching_Patch
{
	[CompilerGenerated]
	private sealed class _003CTargetMethods_003Ed__2 : IEnumerable<MethodBase>, IEnumerable, IEnumerator<MethodBase>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private MethodBase _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		private string[] _003Cmethods_003E5__2;

		private int _003Ci_003E5__3;

		MethodBase IEnumerator<MethodBase>.Current
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
		public _003CTargetMethods_003Ed__2(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			_003Cmethods_003E5__2 = null;
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			int num = _003C_003E1__state;
			if (num != 0)
			{
				if (num != 1)
				{
					return false;
				}
				_003C_003E1__state = -1;
				goto IL_0060;
			}
			_003C_003E1__state = -1;
			_003Cmethods_003E5__2 = vfeMethods;
			_003Ci_003E5__3 = 0;
			goto IL_0070;
			IL_0060:
			_003Ci_003E5__3++;
			goto IL_0070;
			IL_0070:
			if (_003Ci_003E5__3 < _003Cmethods_003E5__2.Length)
			{
				MethodInfo methodInfo = AccessTools.Method(_003Cmethods_003E5__2[_003Ci_003E5__3], (Type[])null, (Type[])null);
				if (!(methodInfo == null))
				{
					_003C_003E2__current = methodInfo;
					_003C_003E1__state = 1;
					return true;
				}
				goto IL_0060;
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
		IEnumerator<MethodBase> IEnumerable<MethodBase>.GetEnumerator()
		{
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				return this;
			}
			return new _003CTargetMethods_003Ed__2(0);
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<MethodBase>)this).GetEnumerator();
		}
	}

	private static readonly string[] vfeMethods = new string[1] { "VFECore.Patch_RenderPawnAt:ShouldDisableCaching" };

	public static bool Prepare()
	{
		string[] array = vfeMethods;
		for (int i = 0; i < array.Length; i++)
		{
			if (!(AccessTools.Method(array[i], (Type[])null, (Type[])null) == null))
			{
				return true;
			}
		}
		return false;
	}

	[IteratorStateMachine(typeof(_003CTargetMethods_003Ed__2))]
	public static IEnumerable<MethodBase> TargetMethods()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CTargetMethods_003Ed__2(-2);
	}

	public static void Postfix(ref bool __result, Pawn pawn)
	{
		if (BigSmallMod.settings.disableTextureCaching)
		{
			__result = true;
		}
	}
}
