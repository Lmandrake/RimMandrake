using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class PawnRenderNode_HAnimalBody : PawnRenderNode_HAnimalPart
{
	[CompilerGenerated]
	private sealed class _003CStateGraphicsFor_003Ed__1 : IEnumerable<(GraphicStateDef state, Graphic graphic)>, IEnumerable, IEnumerator<(GraphicStateDef state, Graphic graphic)>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private (GraphicStateDef state, Graphic graphic) _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public PawnRenderNode_HAnimalBody _003C_003E4__this;

		private Pawn pawn;

		public Pawn _003C_003E3__pawn;

		private IEnumerator<(GraphicStateDef state, Graphic graphic)> _003C_003E7__wrap1;

		(GraphicStateDef state, Graphic graphic) IEnumerator<(GraphicStateDef, Graphic)>.Current
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
		public _003CStateGraphicsFor_003Ed__1(int _003C_003E1__state)
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
			//IL_0115: Unknown result type (might be due to invalid IL or missing references)
			//IL_011b: Invalid comparison between Unknown and I4
			try
			{
				int num = _003C_003E1__state;
				PawnRenderNode_HAnimalBody pawnRenderNode_HAnimalBody = _003C_003E4__this;
				HumanlikeAnimal value;
				PawnKindLifeStage val;
				switch (num)
				{
				default:
					return false;
				case 0:
					_003C_003E1__state = -1;
					_003C_003E7__wrap1 = pawnRenderNode_HAnimalBody._003C_003En__0(pawn).GetEnumerator();
					_003C_003E1__state = -3;
					goto IL_007a;
				case 1:
					_003C_003E1__state = -3;
					goto IL_007a;
				case 2:
					{
						_003C_003E1__state = -1;
						break;
					}
					IL_007a:
					if (_003C_003E7__wrap1.MoveNext())
					{
						(GraphicStateDef, Graphic) current = _003C_003E7__wrap1.Current;
						_003C_003E2__current = current;
						_003C_003E1__state = 1;
						return true;
					}
					_003C_003Em__Finally1();
					_003C_003E7__wrap1 = null;
					HumanlikeAnimalGenerator.humanlikeAnimals.TryGetValue(((Thing)pawn).def, out value);
					if (value == null)
					{
						Log.ErrorOnce("No HumanlikeAnimal found for " + ((Def)((Thing)pawn).def).defName, 123456333);
						return false;
					}
					val = value.animalKind.lifeStages[value.GetLifeStageIndex(pawn)];
					if (val.swimmingGraphicData != null)
					{
						Graphic val2 = val.swimmingGraphicData.Graphic;
						if ((int)pawn.gender == 2 && val.femaleSwimmingGraphicData != null)
						{
							val2 = val.femaleSwimmingGraphicData.Graphic;
						}
						AlternateGraphic val3 = default(AlternateGraphic);
						int num2 = default(int);
						if (PawnGraphicUtils.TryGetAlternate(pawn, ref val3, ref num2))
						{
							val2 = val3.GetSwimmingGraphic(val2);
						}
						_003C_003E2__current = (state: GraphicStateDefOf.Swimming, graphic: val2);
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
		IEnumerator<(GraphicStateDef state, Graphic graphic)> IEnumerable<(GraphicStateDef, Graphic)>.GetEnumerator()
		{
			_003CStateGraphicsFor_003Ed__1 _003CStateGraphicsFor_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CStateGraphicsFor_003Ed__ = this;
			}
			else
			{
				_003CStateGraphicsFor_003Ed__ = new _003CStateGraphicsFor_003Ed__1(0)
				{
					_003C_003E4__this = _003C_003E4__this
				};
			}
			_003CStateGraphicsFor_003Ed__.pawn = _003C_003E3__pawn;
			return _003CStateGraphicsFor_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<(GraphicStateDef, Graphic)>)this).GetEnumerator();
		}
	}

	public PawnRenderNode_HAnimalBody(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
		: base(pawn, props, tree)
	{
	}

	[IteratorStateMachine(typeof(_003CStateGraphicsFor_003Ed__1))]
	protected override IEnumerable<(GraphicStateDef state, Graphic graphic)> StateGraphicsFor(Pawn pawn)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CStateGraphicsFor_003Ed__1(-2)
		{
			_003C_003E4__this = this,
			_003C_003E3__pawn = pawn
		};
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<(GraphicStateDef state, Graphic graphic)> _003C_003En__0(Pawn pawn)
	{
		return ((PawnRenderNode)this).StateGraphicsFor(pawn);
	}
}
