using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class SoulResourceHediff : Hediff, IResourcePool
{
	[CompilerGenerated]
	private sealed class _003CGetGizmos_003Ed__27 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Gizmo _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public SoulResourceHediff _003C_003E4__this;

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
		public _003CGetGizmos_003Ed__27(int _003C_003E1__state)
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
			int num = _003C_003E1__state;
			SoulResourceHediff resource = _003C_003E4__this;
			switch (num)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				_003C_003E2__current = (Gizmo)(object)new SoulResourceGizmo(resource);
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
		IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
		{
			_003CGetGizmos_003Ed__27 result;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				result = this;
			}
			else
			{
				result = new _003CGetGizmos_003Ed__27(0)
				{
					_003C_003E4__this = _003C_003E4__this
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

	private const int tickRateRegen = 50;

	protected int rechargeCooldown;

	protected int rechargeCooldownMax = 500;

	public int refreshState;

	protected float targetValue = 1f;

	protected float max = 1f;

	protected float cur = 1f;

	public Pawn Pawn => base.pawn;

	public float TargetValue
	{
		get
		{
			return targetValue;
		}
		set
		{
			targetValue = value;
		}
	}

	public float Value
	{
		get
		{
			return cur;
		}
		set
		{
			if (value < cur)
			{
				rechargeCooldown = rechargeCooldownMax;
			}
			cur = Mathf.Clamp(value, 0f, max);
		}
	}

	public float Max
	{
		get
		{
			return max;
		}
		set
		{
			max = value;
		}
	}

	public float ValueForDisplay => (int)(cur * 100f);

	public float MaxForDisplay => (int)(max * 100f);

	public int Increments => 25;

	public float ValuePercent => cur / max;

	public void SetTargetValuePct(float value)
	{
		targetValue = value * Max;
	}

	[IteratorStateMachine(typeof(_003CGetGizmos_003Ed__27))]
	public override IEnumerable<Gizmo> GetGizmos()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CGetGizmos_003Ed__27(-2)
		{
			_003C_003E4__this = this
		};
	}

	public override void Tick()
	{
		rechargeCooldown--;
		if (rechargeCooldown >= 0)
		{
			return;
		}
		if (cur != max)
		{
			Value += max * 0.01f;
		}
		rechargeCooldown = 50;
		refreshState++;
		if (refreshState <= 10)
		{
			return;
		}
		if (cur < 0f)
		{
			cur = 0f;
		}
		float num = max;
		max = StatExtension.GetStatValue((Thing)(object)base.pawn, BSDefs.BS_SoulPower, true, -1);
		if (max == 0f)
		{
			base.pawn.health.RemoveHediff((Hediff)(object)this);
			return;
		}
		if (num != max)
		{
			Value = Value * max / num;
		}
		refreshState = 0;
	}

	public override void ExposeData()
	{
		((Hediff)this).ExposeData();
		Scribe_References.Look<Pawn>(ref base.pawn, "pawn", false);
		Scribe_Values.Look<float>(ref cur, "cur", 0f, false);
		Scribe_Values.Look<float>(ref max, "max", 0f, false);
		Scribe_Values.Look<float>(ref targetValue, "targetValue", 0.5f, false);
	}
}
