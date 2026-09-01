using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using Verse;
using Verse.AI;

namespace BigAndSmall;

public class JobDriver_EnterPilotable : JobDriver
{
	[CompilerGenerated]
	private sealed class _003CMakeNewToils_003Ed__1 : IEnumerable<Toil>, IEnumerable, IEnumerator<Toil>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Toil _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public JobDriver_EnterPilotable _003C_003E4__this;

		Toil IEnumerator<Toil>.Current
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
		public _003CMakeNewToils_003Ed__1(int _003C_003E1__state)
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
			//IL_0081: Unknown result type (might be due to invalid IL or missing references)
			//IL_0086: Unknown result type (might be due to invalid IL or missing references)
			//IL_009d: Expected O, but got Unknown
			int num = _003C_003E1__state;
			JobDriver_EnterPilotable CS_0024_003C_003E8__locals3 = _003C_003E4__this;
			switch (num)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				ToilFailConditions.FailOnDestroyedNullOrForbidden<JobDriver_EnterPilotable>(CS_0024_003C_003E8__locals3, (TargetIndex)1);
				_003C_003E2__current = Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false);
				_003C_003E1__state = 1;
				return true;
			case 1:
				_003C_003E1__state = -1;
				_003C_003E2__current = ToilEffects.WithProgressBarToilDelay(Toils_General.Wait(150, (TargetIndex)0), (TargetIndex)1, false, -0.5f);
				_003C_003E1__state = 2;
				return true;
			case 2:
				_003C_003E1__state = -1;
				_003C_003E2__current = new Toil
				{
					initAction = delegate
					{
						//IL_0001: Unknown result type (might be due to invalid IL or missing references)
						//IL_0006: Unknown result type (might be due to invalid IL or missing references)
						LocalTargetInfo targetA = ((JobDriver)CS_0024_003C_003E8__locals3).TargetA;
						Thing thing = ((LocalTargetInfo)(ref targetA)).Thing;
						Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
						if (val != null)
						{
							Hediff val2 = val?.health?.hediffSet?.hediffs?.Where((Hediff x) => x is Piloted).FirstOrDefault();
							if (val2 != null && val2 is Piloted piloted)
							{
								piloted.AddPilot((Thing)(object)((JobDriver)CS_0024_003C_003E8__locals3).pawn);
							}
						}
					}
				};
				_003C_003E1__state = 3;
				return true;
			case 3:
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
		IEnumerator<Toil> IEnumerable<Toil>.GetEnumerator()
		{
			_003CMakeNewToils_003Ed__1 result;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				result = this;
			}
			else
			{
				result = new _003CMakeNewToils_003Ed__1(0)
				{
					_003C_003E4__this = _003C_003E4__this
				};
			}
			return result;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<Toil>)this).GetEnumerator();
		}
	}

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		return ReservationUtility.Reserve(base.pawn, base.job.GetTarget((TargetIndex)1), base.job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false);
	}

	[IteratorStateMachine(typeof(_003CMakeNewToils_003Ed__1))]
	protected override IEnumerable<Toil> MakeNewToils()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CMakeNewToils_003Ed__1(-2)
		{
			_003C_003E4__this = this
		};
	}
}
