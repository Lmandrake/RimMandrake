using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class PawnRenderNode_UltimateApparel : PawnRenderNode_Apparel, IUltimateRendering
{
	[CompilerGenerated]
	private sealed class _003CGraphicsFor_003Ed__20 : IEnumerable<Graphic>, IEnumerable, IEnumerator<Graphic>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Graphic _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public PawnRenderNode_UltimateApparel _003C_003E4__this;

		private Pawn pawn;

		public Pawn _003C_003E3__pawn;

		private IEnumerator<Graphic> _003C_003E7__wrap1;

		Graphic IEnumerator<Graphic>.Current
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
		public _003CGraphicsFor_003Ed__20(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			int num = _003C_003E1__state;
			if (num == -3 || num == 2)
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
				PawnRenderNode_UltimateApparel pawnRenderNode_UltimateApparel = _003C_003E4__this;
				switch (num)
				{
				default:
					return false;
				case 0:
					_003C_003E1__state = -1;
					if (((PawnRenderNode)pawnRenderNode_UltimateApparel).HasGraphic(((PawnRenderNode)pawnRenderNode_UltimateApparel).tree.pawn))
					{
						_003C_003E2__current = ((PawnRenderNode)pawnRenderNode_UltimateApparel).GraphicFor(pawn);
						_003C_003E1__state = 1;
						return true;
					}
					_003C_003E7__wrap1 = pawnRenderNode_UltimateApparel._003C_003En__0(pawn).GetEnumerator();
					_003C_003E1__state = -3;
					goto IL_00ae;
				case 1:
					_003C_003E1__state = -1;
					break;
				case 2:
					{
						_003C_003E1__state = -3;
						goto IL_00ae;
					}
					IL_00ae:
					if (_003C_003E7__wrap1.MoveNext())
					{
						Graphic current = _003C_003E7__wrap1.Current;
						_003C_003E2__current = current;
						_003C_003E1__state = 2;
						return true;
					}
					_003C_003Em__Finally1();
					_003C_003E7__wrap1 = null;
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
		IEnumerator<Graphic> IEnumerable<Graphic>.GetEnumerator()
		{
			_003CGraphicsFor_003Ed__20 _003CGraphicsFor_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CGraphicsFor_003Ed__ = this;
			}
			else
			{
				_003CGraphicsFor_003Ed__ = new _003CGraphicsFor_003Ed__20(0)
				{
					_003C_003E4__this = _003C_003E4__this
				};
			}
			_003CGraphicsFor_003Ed__.pawn = _003C_003E3__pawn;
			return _003CGraphicsFor_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<Graphic>)this).GetEnumerator();
		}
	}

	public PawnRenderNode Base => (PawnRenderNode)(object)this;

	public bool ScaleSet { get; set; }

	public Vector2 CachedScale { get; set; } = Vector2.one;

	public ShaderTypeDef ShaderOverride { get; set; }

	private PawnRenderingProps_Ultimate UProps => (PawnRenderingProps_Ultimate)(object)((PawnRenderNode)this).props;

	public PawnRenderNode_UltimateApparel(Pawn pawn, PawnRenderingProps_Ultimate props, PawnRenderTree tree)
		: base(pawn, (PawnRenderNodeProperties)(object)props, tree, (Apparel)null)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		base.useHeadMesh = ((PawnRenderNodeProperties)props).parentTagDef == PawnRenderNodeTagDefOf.ApparelHead;
		((PawnRenderNode)this).meshSet = ((PawnRenderNode)this).MeshSetFor(pawn);
	}

	public PawnRenderNode_UltimateApparel(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree, Apparel apparel)
		: base(pawn, props, tree, apparel)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		((PawnRenderNode)this).apparel = apparel;
		base.useHeadMesh = props.parentTagDef == PawnRenderNodeTagDefOf.ApparelHead;
		((PawnRenderNode)this).meshSet = ((PawnRenderNode)this).MeshSetFor(pawn);
	}

	public PawnRenderNode_UltimateApparel(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree, Apparel apparel, bool useHeadMesh)
		: base(pawn, props, tree, apparel, useHeadMesh)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		((PawnRenderNode)this).apparel = apparel;
		base.useHeadMesh = props.parentTagDef == PawnRenderNodeTagDefOf.ApparelHead;
		((PawnRenderNode)this).meshSet = ((PawnRenderNode)this).MeshSetFor(pawn);
	}

	public override string TexPathFor(Pawn pawn)
	{
		throw new NotImplementedException("TexPath is not meant to be used with this RenderNode." + string.Format("Use {0} ({1}) instead.", "GraphicSet", typeof(ConditionalGraphicsSet)));
	}

	[IteratorStateMachine(typeof(_003CGraphicsFor_003Ed__20))]
	protected override IEnumerable<Graphic> GraphicsFor(Pawn pawn)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CGraphicsFor_003Ed__20(-2)
		{
			_003C_003E4__this = this,
			_003C_003E3__pawn = pawn
		};
	}

	public override Graphic GraphicFor(Pawn pawn)
	{
		return PRN_Ultimate.GraphicFor(pawn, this, UProps);
	}

	public override Mesh GetMesh(PawnDrawParms parms)
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		if (((Rot4)(ref parms.facing)).IsHorizontal && UProps.invertEastWest)
		{
			parms.facing = ((Rot4)(ref parms.facing)).Opposite;
		}
		return ((PawnRenderNode)this).GetMesh(parms);
	}

	public override GraphicMeshSet MeshSetFor(Pawn pawn)
	{
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		if (((PawnRenderNode)this).apparel == null)
		{
			return ((PawnRenderNode_Apparel)this).MeshSetFor(pawn);
		}
		if (((PawnRenderNode)this).Props.overrideMeshSize.HasValue)
		{
			return MeshPool.GetMeshSetForSize(((PawnRenderNode)this).Props.overrideMeshSize.Value.x, ((PawnRenderNode)this).Props.overrideMeshSize.Value.y);
		}
		if (base.useHeadMesh)
		{
			return HumanlikeMeshPoolUtility.GetHumanlikeHeadSetForPawn(pawn, 1f, 1f);
		}
		return HumanlikeMeshPoolUtility.GetHumanlikeBodySetForPawn(pawn, 1f, 1f);
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Graphic> _003C_003En__0(Pawn pawn)
	{
		return ((PawnRenderNode_Apparel)this).GraphicsFor(pawn);
	}
}
