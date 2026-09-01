using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;

namespace BigAndSmall;

public static class ListHelpers
{
	[CompilerGenerated]
	private sealed class _003CFilterAndTransform_003Ed__2<TSource, TResult> : IEnumerable<TResult>, IEnumerable, IEnumerator<TResult>, IDisposable, IEnumerator where TResult : struct
	{
		private int _003C_003E1__state;

		private TResult _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		private IEnumerable<TSource> source;

		public IEnumerable<TSource> _003C_003E3__source;

		private Func<TSource, TResult?> selector;

		public Func<TSource, TResult?> _003C_003E3__selector;

		private IEnumerator<TSource> _003C_003E7__wrap1;

		TResult IEnumerator<TResult>.Current
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
		public _003CFilterAndTransform_003Ed__2(int _003C_003E1__state)
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
				switch (_003C_003E1__state)
				{
				default:
					return false;
				case 0:
					_003C_003E1__state = -1;
					_003C_003E7__wrap1 = source.GetEnumerator();
					_003C_003E1__state = -3;
					break;
				case 1:
					_003C_003E1__state = -3;
					break;
				}
				while (_003C_003E7__wrap1.MoveNext())
				{
					TSource current = _003C_003E7__wrap1.Current;
					TResult? val = selector(current);
					if (val.HasValue)
					{
						_003C_003E2__current = val.Value;
						_003C_003E1__state = 1;
						return true;
					}
				}
				_003C_003Em__Finally1();
				_003C_003E7__wrap1 = null;
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
		IEnumerator<TResult> IEnumerable<TResult>.GetEnumerator()
		{
			_003CFilterAndTransform_003Ed__2<TSource, TResult> _003CFilterAndTransform_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CFilterAndTransform_003Ed__ = this;
			}
			else
			{
				_003CFilterAndTransform_003Ed__ = new _003CFilterAndTransform_003Ed__2<TSource, TResult>(0);
			}
			_003CFilterAndTransform_003Ed__.source = _003C_003E3__source;
			_003CFilterAndTransform_003Ed__.selector = _003C_003E3__selector;
			return _003CFilterAndTransform_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<TResult>)this).GetEnumerator();
		}
	}

	public static List<T> IntersectNullableLists<T>(this List<T> list1, List<T> list2)
	{
		if (list1 != null && list2 != null)
		{
			List<T> obj = (List<T>)Activator.CreateInstance(list1.GetType());
			obj.AddRange(list1.Intersect(list2));
			return obj;
		}
		return list1 ?? list2;
	}

	public static List<T> UnionNullableLists<T>(this List<T> list1, List<T> list2)
	{
		if (list1 != null && list2 != null)
		{
			List<T> obj = (List<T>)Activator.CreateInstance(list1.GetType());
			obj.AddRange(list1.Union(list2));
			return obj;
		}
		return list1 ?? list2;
	}

	[IteratorStateMachine(typeof(_003CFilterAndTransform_003Ed__2<, >))]
	public static IEnumerable<TResult> FilterAndTransform<TSource, TResult>(this IEnumerable<TSource> source, Func<TSource, TResult?> selector) where TResult : struct
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CFilterAndTransform_003Ed__2<TSource, TResult>(-2)
		{
			_003C_003E3__source = source,
			_003C_003E3__selector = selector
		};
	}

	public static void AddDistinctRange<T>(this IList<T> list, IEnumerable<T> items)
	{
		foreach (T item in items)
		{
			if (!list.Contains(item))
			{
				list.Add(item);
			}
		}
	}
}
