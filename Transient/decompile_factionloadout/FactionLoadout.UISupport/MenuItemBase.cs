using System;
using UnityEngine;

namespace FactionLoadout.UISupport;

public abstract class MenuItemBase : IComparable<MenuItemBase>
{
	public object Payload { get; set; }

	public T GetPayload<T>()
	{
		return (T)Payload;
	}

	public abstract bool Matches(string search);

	public abstract int CompareTo(MenuItemBase other);

	public abstract Vector2 Draw(Vector2 pos);

	public abstract Vector2 GetSize();

	public virtual void SetWidth(float width)
	{
	}
}
