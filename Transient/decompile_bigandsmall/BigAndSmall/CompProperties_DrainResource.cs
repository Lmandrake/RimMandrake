using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using Verse;

namespace BigAndSmall;

public class CompProperties_DrainResource : HediffCompProperties
{
	[CompilerGenerated]
	private sealed class _003CConfigErrors_003Ed__5 : IEnumerable<string>, IEnumerable, IEnumerator<string>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private string _003C_003E2__current;

		private int _003C_003El__initialThreadId;

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
		public _003CConfigErrors_003Ed__5(int _003C_003E1__state)
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
			if (_003C_003E1__state != 0)
			{
				return false;
			}
			_003C_003E1__state = -1;
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
		IEnumerator<string> IEnumerable<string>.GetEnumerator()
		{
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				return this;
			}
			return new _003CConfigErrors_003Ed__5(0);
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<string>)this).GetEnumerator();
		}
	}

	public const float drainAmount = 0.01f;

	public bool removeOnZero;

	public int ticksBetweenDrain = 1000;

	public bool canCancel;

	public string iconPath = "UI/Designators/Cancel";

	[IteratorStateMachine(typeof(_003CConfigErrors_003Ed__5))]
	public override IEnumerable<string> ConfigErrors(HediffDef parentDef)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CConfigErrors_003Ed__5(-2);
	}
}
