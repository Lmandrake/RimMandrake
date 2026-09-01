using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public abstract class CompProperties_PoolCost : CompProperties_AbilityEffect
{
	[CompilerGenerated]
	private sealed class _003CExtraStatSummary_003Ed__2 : IEnumerable<string>, IEnumerable, IEnumerator<string>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private string _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public CompProperties_PoolCost _003C_003E4__this;

		string IEnumerator<string>.Current
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
		public _003CExtraStatSummary_003Ed__2(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			//IL_0024: Unknown result type (might be due to invalid IL or missing references)
			//IL_002e: Unknown result type (might be due to invalid IL or missing references)
			int num = _003C_003E1__state;
			CompProperties_PoolCost compProperties_PoolCost = _003C_003E4__this;
			switch (num)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				_003C_003E2__current = TaggedString.op_Implicit(Translator.Translate("AbilityPoolCost") + ": ") + Mathf.RoundToInt(compProperties_PoolCost.resourceCost * 100f);
				_003C_003E1__state = 1;
				return true;
			case 1:
				_003C_003E1__state = -1;
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
		IEnumerator<string> IEnumerable<string>.GetEnumerator()
		{
			_003CExtraStatSummary_003Ed__2 result;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				result = this;
			}
			else
			{
				result = new _003CExtraStatSummary_003Ed__2(0)
				{
					_003C_003E4__this = _003C_003E4__this
				};
			}
			return result;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<string>)this).GetEnumerator();
		}
	}

	public float resourceCost;

	public CompProperties_PoolCost()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_PoolCost);
	}

	[IteratorStateMachine(typeof(_003CExtraStatSummary_003Ed__2))]
	public override IEnumerable<string> ExtraStatSummary()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CExtraStatSummary_003Ed__2(-2)
		{
			_003C_003E4__this = this
		};
	}
}
