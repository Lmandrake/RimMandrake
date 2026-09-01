using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class SkillAndAptitude
{
	[CompilerGenerated]
	private sealed class _003CAptitudeTranspiler_003Ed__2 : IEnumerable<CodeInstruction>, IEnumerable, IEnumerator<CodeInstruction>, IDisposable, IEnumerator
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
		public _003CAptitudeTranspiler_003Ed__2(int _003C_003E1__state)
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
			//IL_0145: Unknown result type (might be due to invalid IL or missing references)
			//IL_014f: Expected O, but got Unknown
			//IL_0166: Unknown result type (might be due to invalid IL or missing references)
			//IL_0170: Expected O, but got Unknown
			//IL_019c: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a6: Expected O, but got Unknown
			//IL_01f4: Unknown result type (might be due to invalid IL or missing references)
			//IL_01fe: Expected O, but got Unknown
			//IL_0215: Unknown result type (might be due to invalid IL or missing references)
			//IL_021f: Expected O, but got Unknown
			//IL_024b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0255: Expected O, but got Unknown
			//IL_0284: Unknown result type (might be due to invalid IL or missing references)
			//IL_028e: Expected O, but got Unknown
			//IL_02a6: Unknown result type (might be due to invalid IL or missing references)
			//IL_02b0: Expected O, but got Unknown
			//IL_02e9: Unknown result type (might be due to invalid IL or missing references)
			//IL_02f3: Expected O, but got Unknown
			//IL_0320: Unknown result type (might be due to invalid IL or missing references)
			//IL_032a: Expected O, but got Unknown
			//IL_0124: Unknown result type (might be due to invalid IL or missing references)
			//IL_012e: Expected O, but got Unknown
			switch (_003C_003E1__state)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				_003Ccodes_003E5__2 = instructions.ToList();
				_003Cfound_003E5__3 = false;
				_003Ci_003E5__4 = 0;
				break;
			case 1:
				_003C_003E1__state = -1;
				if (!_003Cfound_003E5__3 && _003Ccodes_003E5__2[_003Ci_003E5__4].opcode == OpCodes.Stfld && _003Ccodes_003E5__2[_003Ci_003E5__4].operand is FieldInfo { Name: "aptitudeCached" } fieldInfo && fieldInfo.DeclaringType == typeof(SkillRecord))
				{
					_003Cfound_003E5__3 = true;
					_003C_003E2__current = new CodeInstruction(OpCodes.Ldarg_0, (object)null);
					_003C_003E1__state = 2;
					return true;
				}
				goto IL_033b;
			case 2:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				_003C_003E1__state = 3;
				return true;
			case 3:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				_003C_003E1__state = 4;
				return true;
			case 4:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Ldfld, (object)typeof(SkillRecord).GetField("pawn", BindingFlags.Instance | BindingFlags.NonPublic));
				_003C_003E1__state = 5;
				return true;
			case 5:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Call, (object)typeof(SkillAndAptitude).GetMethod("GetExtAptitude", BindingFlags.Static | BindingFlags.Public, null, new Type[2]
				{
					typeof(SkillRecord),
					typeof(Pawn)
				}, null));
				_003C_003E1__state = 6;
				return true;
			case 6:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				_003C_003E1__state = 7;
				return true;
			case 7:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Ldflda, (object)typeof(SkillRecord).GetField("aptitudeCached", BindingFlags.Instance | BindingFlags.NonPublic));
				_003C_003E1__state = 8;
				return true;
			case 8:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Call, (object)typeof(int?).GetMethod("GetValueOrDefault", Type.EmptyTypes));
				_003C_003E1__state = 9;
				return true;
			case 9:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Add, (object)null);
				_003C_003E1__state = 10;
				return true;
			case 10:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Newobj, (object)typeof(int?).GetConstructor(new Type[1] { typeof(int) }));
				_003C_003E1__state = 11;
				return true;
			case 11:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Stfld, (object)typeof(SkillRecord).GetField("aptitudeCached", BindingFlags.Instance | BindingFlags.NonPublic));
				_003C_003E1__state = 12;
				return true;
			case 12:
				{
					_003C_003E1__state = -1;
					goto IL_033b;
				}
				IL_033b:
				_003Ci_003E5__4++;
				break;
			}
			if (_003Ci_003E5__4 < _003Ccodes_003E5__2.Count)
			{
				_003C_003E2__current = _003Ccodes_003E5__2[_003Ci_003E5__4];
				_003C_003E1__state = 1;
				return true;
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
		IEnumerator<CodeInstruction> IEnumerable<CodeInstruction>.GetEnumerator()
		{
			_003CAptitudeTranspiler_003Ed__2 _003CAptitudeTranspiler_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CAptitudeTranspiler_003Ed__ = this;
			}
			else
			{
				_003CAptitudeTranspiler_003Ed__ = new _003CAptitudeTranspiler_003Ed__2(0);
			}
			_003CAptitudeTranspiler_003Ed__.instructions = _003C_003E3__instructions;
			return _003CAptitudeTranspiler_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<CodeInstruction>)this).GetEnumerator();
		}
	}

	public static int GetExtAptitude(SkillRecord record, Pawn pawn)
	{
		int amount = 0;
		BSCache cacheUltraSpeed = HumanoidPawnScaler.GetCacheUltraSpeed(pawn);
		if (cacheUltraSpeed != null && cacheUltraSpeed.aptitudes != null)
		{
			CollectionExtensions.Do<Aptitude>(cacheUltraSpeed.aptitudes.Where((Aptitude x) => x.skill == record.def), (Action<Aptitude>)delegate(Aptitude x)
			{
				amount = x.level;
			});
		}
		return amount;
	}

	public static MethodBase TargetMethod()
	{
		return typeof(SkillRecord).GetProperty("Aptitude", BindingFlags.DeclaredOnly | BindingFlags.Instance | BindingFlags.Public).GetGetMethod();
	}

	[IteratorStateMachine(typeof(_003CAptitudeTranspiler_003Ed__2))]
	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> AptitudeTranspiler(IEnumerable<CodeInstruction> instructions)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CAptitudeTranspiler_003Ed__2(-2)
		{
			_003C_003E3__instructions = instructions
		};
	}
}
