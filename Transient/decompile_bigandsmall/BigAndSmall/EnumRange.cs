using System;
using System.Collections.Generic;
using System.Globalization;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public struct EnumRange<T> : IEquatable<EnumRange<T>> where T : Enum
{
	public T min;

	public T max;

	public static EnumRange<T> zero => new EnumRange<T>(default(T), default(T));

	public static EnumRange<T> one => new EnumRange<T>((T)Enum.ToObject(typeof(T), 1), (T)Enum.ToObject(typeof(T), 1));

	public readonly T TrueMin
	{
		get
		{
			if (Comparer<T>.Default.Compare(min, max) >= 0)
			{
				return max;
			}
			return min;
		}
	}

	public readonly T TrueMax
	{
		get
		{
			if (Comparer<T>.Default.Compare(min, max) <= 0)
			{
				return max;
			}
			return min;
		}
	}

	public readonly float Average => ((float)Convert.ToInt32(min) + (float)Convert.ToInt32(max)) / 2f;

	public readonly T RandomInRange => (T)Enum.ToObject(typeof(T), Rand.RangeInclusive(Convert.ToInt32(min), Convert.ToInt32(max)));

	public EnumRange(T min, T max)
	{
		this.min = min;
		this.max = max;
	}

	public readonly T Lerped(float lerpFactor)
	{
		int num = Convert.ToInt32(min);
		int num2 = Convert.ToInt32(max);
		int value = num + Mathf.RoundToInt(lerpFactor * (float)(num2 - num));
		return (T)Enum.ToObject(typeof(T), value);
	}

	public static EnumRange<T> FromString(string s)
	{
		_ = CultureInfo.InvariantCulture;
		string[] array = s.Split('~', StringSplitOptions.None);
		if (array.Length == 1)
		{
			T obj = (T)Enum.Parse(typeof(T), array[0], ignoreCase: true);
			return new EnumRange<T>(obj, obj);
		}
		T obj2 = (GenText.NullOrEmpty(array[0]) ? ((T)Enum.ToObject(typeof(T), int.MinValue)) : ((T)Enum.Parse(typeof(T), array[0], ignoreCase: true)));
		T val = (GenText.NullOrEmpty(array[1]) ? ((T)Enum.ToObject(typeof(T), int.MaxValue)) : ((T)Enum.Parse(typeof(T), array[1], ignoreCase: true)));
		return new EnumRange<T>(obj2, val);
	}

	public override readonly string ToString()
	{
		return min?.ToString() + "~" + max;
	}

	public override readonly int GetHashCode()
	{
		return Gen.HashCombineInt(min.GetHashCode(), max.GetHashCode());
	}

	public override bool Equals(object obj)
	{
		if (!(obj is EnumRange<T>))
		{
			return false;
		}
		return Equals((EnumRange<T>)obj);
	}

	public readonly bool Equals(EnumRange<T> other)
	{
		if (EqualityComparer<T>.Default.Equals(min, other.min))
		{
			return EqualityComparer<T>.Default.Equals(max, other.max);
		}
		return false;
	}

	public static bool operator ==(EnumRange<T> lhs, EnumRange<T> rhs)
	{
		return lhs.Equals(rhs);
	}

	public static bool operator !=(EnumRange<T> lhs, EnumRange<T> rhs)
	{
		return !(lhs == rhs);
	}

	internal readonly bool Includes(T val)
	{
		int num = Convert.ToInt32(val);
		if (num >= Convert.ToInt32(min))
		{
			return num <= Convert.ToInt32(max);
		}
		return false;
	}
}
