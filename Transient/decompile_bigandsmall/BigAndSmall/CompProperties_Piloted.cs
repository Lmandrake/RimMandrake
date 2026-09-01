using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using BigAndSmall.Utilities;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_Piloted : HediffCompProperties
{
	[CompilerGenerated]
	private sealed class _003CConfigErrors_003Ed__23 : IEnumerable<string>, IEnumerable, IEnumerator<string>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private string _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public CompProperties_Piloted _003C_003E4__this;

		private HediffDef parentDef;

		public HediffDef _003C_003E3__parentDef;

		private IEnumerator<string> _003C_003E7__wrap1;

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
		public _003CConfigErrors_003Ed__23(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			int num = _003C_003E1__state;
			if (num == -3 || num == 1)
			{
				try
				{
				}
				finally
				{
					_003C_003Em__Finally1();
				}
			}
			_003C_003E7__wrap1 = null;
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			try
			{
				int num = _003C_003E1__state;
				CompProperties_Piloted compProperties_Piloted = _003C_003E4__this;
				switch (num)
				{
				default:
					return false;
				case 0:
					_003C_003E1__state = -1;
					_003C_003E7__wrap1 = compProperties_Piloted._003C_003En__0(parentDef).GetEnumerator();
					_003C_003E1__state = -3;
					goto IL_0075;
				case 1:
					_003C_003E1__state = -3;
					goto IL_0075;
				case 2:
					{
						_003C_003E1__state = -1;
						break;
					}
					IL_0075:
					if (_003C_003E7__wrap1.MoveNext())
					{
						string current = _003C_003E7__wrap1.Current;
						_003C_003E2__current = current;
						_003C_003E1__state = 1;
						return true;
					}
					_003C_003Em__Finally1();
					_003C_003E7__wrap1 = null;
					if (compProperties_Piloted.xenotypeToApplyOnRemove != null && compProperties_Piloted.restoreXenotypeOnRemove)
					{
						_003C_003E2__current = "Cannot apply xenotype on remove and restore xenotype on remove at the same time.";
						_003C_003E1__state = 2;
						return true;
					}
					break;
				}
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
			if (_003C_003E7__wrap1 != null)
			{
				_003C_003E7__wrap1.Dispose();
			}
		}

		[DebuggerHidden]
		void IEnumerator.Reset()
		{
			throw new NotSupportedException();
		}

		[DebuggerHidden]
		IEnumerator<string> IEnumerable<string>.GetEnumerator()
		{
			_003CConfigErrors_003Ed__23 _003CConfigErrors_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CConfigErrors_003Ed__ = this;
			}
			else
			{
				_003CConfigErrors_003Ed__ = new _003CConfigErrors_003Ed__23(0)
				{
					_003C_003E4__this = _003C_003E4__this
				};
			}
			_003CConfigErrors_003Ed__.parentDef = _003C_003E3__parentDef;
			return _003CConfigErrors_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<string>)this).GetEnumerator();
		}
	}

	public bool pilotRequired = true;

	public int pilotCapacity = 1;

	public float baseCapacity = 0.51f;

	public float pilotConsciousnessOffset = 0.25f;

	public bool inheritPilotSkills;

	public bool inheritPilotMentalTraits;

	public float flatBonusIfPiloted;

	public bool inheritRelationShips;

	public bool removeIfNoPilot;

	public bool temporarilySwapIdeology;

	public bool temporarilySwapFaction;

	public bool temporarilySwapName;

	public int? injuryOnRemoval;

	public bool canAutoEjectIfColonist = true;

	public XenotypeDef xenotypeToApplyOnApply;

	public bool restoreXenotypeOnRemove;

	public XenotypeDef xenotypeToApplyOnRemove;

	public List<HediffChance> hediffsToApplyOnEnter;

	public List<HediffChance> hediffsToApplyOnRemove;

	public bool pilotInheritMentalTraitsOnRemove;

	public bool killOnRemove;

	public float? pilotLearnSkills;

	public CompProperties_Piloted()
	{
		base.compClass = typeof(PilotedCompProps);
	}

	[IteratorStateMachine(typeof(_003CConfigErrors_003Ed__23))]
	public override IEnumerable<string> ConfigErrors(HediffDef parentDef)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CConfigErrors_003Ed__23(-2)
		{
			_003C_003E4__this = this,
			_003C_003E3__parentDef = parentDef
		};
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<string> _003C_003En__0(HediffDef parentDef)
	{
		return ((HediffCompProperties)this).ConfigErrors(parentDef);
	}
}
