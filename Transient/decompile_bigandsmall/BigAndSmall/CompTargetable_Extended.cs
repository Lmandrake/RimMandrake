using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Reflection;
using System.Runtime.CompilerServices;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompTargetable_Extended : CompTargetable
{
	[CompilerGenerated]
	private sealed class _003CGetTargets_003Ed__4 : IEnumerable<Thing>, IEnumerable, IEnumerator<Thing>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Thing _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		private Thing targetChosenByPlayer;

		public Thing _003C_003E3__targetChosenByPlayer;

		Thing IEnumerator<Thing>.Current
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
		public _003CGetTargets_003Ed__4(int _003C_003E1__state)
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
			switch (_003C_003E1__state)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				_003C_003E2__current = targetChosenByPlayer;
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
		IEnumerator<Thing> IEnumerable<Thing>.GetEnumerator()
		{
			_003CGetTargets_003Ed__4 _003CGetTargets_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CGetTargets_003Ed__ = this;
			}
			else
			{
				_003CGetTargets_003Ed__ = new _003CGetTargets_003Ed__4(0);
			}
			_003CGetTargets_003Ed__.targetChosenByPlayer = _003C_003E3__targetChosenByPlayer;
			return _003CGetTargets_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<Thing>)this).GetEnumerator();
		}
	}

	public CompProperties_TargetableExtended PropsE => (CompProperties_TargetableExtended)(object)((ThingComp)this).props;

	protected override bool PlayerChoosesTarget => true;

	[IteratorStateMachine(typeof(_003CGetTargets_003Ed__4))]
	public override IEnumerable<Thing> GetTargets(Thing targetChosenByPlayer = null)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CGetTargets_003Ed__4(-2)
		{
			_003C_003E3__targetChosenByPlayer = targetChosenByPlayer
		};
	}

	protected override TargetingParameters GetTargetingParameters()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		TargetingParameters val = new TargetingParameters();
		FieldInfo[] fields = typeof(TargetingParameters).GetFields();
		foreach (FieldInfo fieldInfo in fields)
		{
			fieldInfo.SetValue(val, fieldInfo.GetValue(PropsE.targetInfo));
		}
		if (PropsE.animalsOnly)
		{
			val.canTargetHumans = false;
			val.canTargetSubhumans = false;
			val.canTargetMechs = false;
			val.canTargetBuildings = false;
		}
		else if (PropsE.humanlikeOnly)
		{
			val.canTargetAnimals = false;
			val.canTargetMechs = false;
			val.canTargetBuildings = false;
		}
		return val;
	}

	public override bool ValidateTarget(LocalTargetInfo target, bool showMessages = true)
	{
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		if (PropsE.playerOwnedOnly && ((LocalTargetInfo)(ref target)).Thing.Faction != Faction.OfPlayerSilentFail)
		{
			if (showMessages)
			{
				Messages.Message(TaggedString.op_Implicit(Translator.Translate("CannotOrderNonControlled")), MessageTypeDefOf.RejectInput, false);
			}
			return false;
		}
		return ((CompTargetable)this).ValidateTarget(target, showMessages);
	}
}
