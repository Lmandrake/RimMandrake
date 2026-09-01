using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public abstract class Comp_DrainsResource : HediffComp
{
	[CompilerGenerated]
	private sealed class _003CCompGetGizmos_003Ed__7 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Gizmo _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public Comp_DrainsResource _003C_003E4__this;

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
		public _003CCompGetGizmos_003Ed__7(int _003C_003E1__state)
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
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_005c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Unknown result type (might be due to invalid IL or missing references)
			//IL_0071: Unknown result type (might be due to invalid IL or missing references)
			//IL_007d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0084: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b7: Expected O, but got Unknown
			int num = _003C_003E1__state;
			Comp_DrainsResource CS_0024_003C_003E8__locals5 = _003C_003E4__this;
			switch (num)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				if (CS_0024_003C_003E8__locals5.Props.canCancel)
				{
					_003C_003E2__current = (Gizmo)new Command_Action
					{
						defaultLabel = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_StopSomething", NamedArgument.op_Implicit(((Hediff)((HediffComp)CS_0024_003C_003E8__locals5).parent).LabelCap))),
						defaultDesc = TaggedString.op_Implicit(Translator.Translate("BS_StopActiveDesc")),
						icon = (Texture)(object)CS_0024_003C_003E8__locals5.Icon,
						groupable = true,
						groupKey = 43214 + ((object)((Hediff)((HediffComp)CS_0024_003C_003E8__locals5).parent).def).GetHashCode(),
						action = delegate
						{
							((Hediff)((HediffComp)CS_0024_003C_003E8__locals5).parent).Severity = 0f;
						}
					};
					_003C_003E1__state = 1;
					return true;
				}
				break;
			case 1:
				_003C_003E1__state = -1;
				break;
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
		IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
		{
			_003CCompGetGizmos_003Ed__7 result;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				result = this;
			}
			else
			{
				result = new _003CCompGetGizmos_003Ed__7(0)
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

	[CompilerGenerated]
	private Texture2D _003CIcon_003Ek__BackingField;

	public CompProperties_DrainResource Props => (CompProperties_DrainResource)(object)base.props;

	public Texture2D Icon => _003CIcon_003Ek__BackingField ?? (_003CIcon_003Ek__BackingField = ContentFinder<Texture2D>.Get(Props.iconPath, true));

	public override void CompPostTick(ref float severityAdjustment)
	{
		if (Find.TickManager.TicksGame % Props.ticksBetweenDrain == 0)
		{
			DrainResource();
		}
	}

	protected abstract void DrainResource();

	[IteratorStateMachine(typeof(_003CCompGetGizmos_003Ed__7))]
	public override IEnumerable<Gizmo> CompGetGizmos()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CCompGetGizmos_003Ed__7(-2)
		{
			_003C_003E4__this = this
		};
	}
}
