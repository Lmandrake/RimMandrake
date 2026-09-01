using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace BigAndSmall.Balancing.VEPatches;

[HarmonyPatch]
public static class VEF_Production
{
	[CompilerGenerated]
	private sealed class _003CTargetMethods_003Ed__2 : IEnumerable<MethodBase>, IEnumerable, IEnumerator<MethodBase>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private MethodBase _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		private string[] _003Cvlfa_methods_003E5__2;

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
			_003Cvlfa_methods_003E5__2 = null;
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
			_003Cvlfa_methods_003E5__2 = VLFA_Methods;
			_003Ci_003E5__3 = 0;
			goto IL_0070;
			IL_0060:
			_003Ci_003E5__3++;
			goto IL_0070;
			IL_0070:
			if (_003Ci_003E5__3 < _003Cvlfa_methods_003E5__2.Length)
			{
				MethodInfo methodInfo = AccessTools.Method(_003Cvlfa_methods_003E5__2[_003Ci_003E5__3], (Type[])null, (Type[])null);
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

	private static readonly string[] VLFA_Methods = new string[1] { "AnimalBehaviours.HediffComp_Spawner:TryDoSpawn" };

	public static FieldInfo spawnCountField = null;

	public static int previousSpawnCount = 1;

	public static HediffCompProperties hediffCP_Spawner = null;

	public static bool Prepare()
	{
		string[] vLFA_Methods = VLFA_Methods;
		for (int i = 0; i < vLFA_Methods.Length; i++)
		{
			if (!(AccessTools.Method(vLFA_Methods[i], (Type[])null, (Type[])null) == null))
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

	public static void Prefix(ref HediffComp __instance)
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Expected O, but got Unknown
		Pawn pawn = ((Hediff)__instance.parent).pawn;
		if (!((Thing)pawn).Spawned)
		{
			return;
		}
		hediffCP_Spawner = (HediffCompProperties)((object)__instance).GetType().GetProperty("PropsSpawner").GetValue(__instance);
		spawnCountField = ((object)hediffCP_Spawner).GetType().GetField("spawnCount");
		if (spawnCountField != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(pawn);
			if (cache != null)
			{
				previousSpawnCount = (int)spawnCountField.GetValue(hediffCP_Spawner);
				float doubleMaxLinear = cache.scaleMultiplier.DoubleMaxLinear;
				int num = Mathf.Max(1, (int)(doubleMaxLinear * (float)previousSpawnCount));
				spawnCountField.SetValue(hediffCP_Spawner, num);
			}
		}
	}

	public static void Postfix(ref HediffComp __instance)
	{
		if (((Thing)((Hediff)__instance.parent).pawn).Spawned && hediffCP_Spawner != null)
		{
			spawnCountField.SetValue(hediffCP_Spawner, previousSpawnCount);
		}
	}
}
