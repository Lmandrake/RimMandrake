using System;
using System.Collections;
using System.Collections.Generic;
using Verse;

namespace FactionLoadout.Util;

public static class DeepCopy
{
	public static object Value(object value, Type type)
	{
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Expected O, but got Unknown
		if (value == null)
		{
			return null;
		}
		if (value is IDeepCopyable<object> deepCopyable)
		{
			return deepCopyable.DeepClone();
		}
		SimpleCurve val = (SimpleCurve)((value is SimpleCurve) ? value : null);
		if (val != null)
		{
			return (object)new SimpleCurve((IEnumerable<CurvePoint>)val);
		}
		if (type.IsPrimitive || type.IsEnum || type == typeof(string))
		{
			return value;
		}
		if (typeof(Def).IsAssignableFrom(type))
		{
			return value;
		}
		if (Nullable.GetUnderlyingType(type) != null)
		{
			return value;
		}
		if (type.IsValueType)
		{
			return value;
		}
		if (type.IsGenericType && type.GetGenericTypeDefinition() == typeof(List<>))
		{
			IList obj = (IList)value;
			IList list = (IList)Activator.CreateInstance(type);
			{
				foreach (object item in obj)
				{
					list.Add((item is IDeepCopyable<object> deepCopyable2) ? deepCopyable2.DeepClone() : item);
				}
				return list;
			}
		}
		if (type.IsGenericType && type.GetGenericTypeDefinition() == typeof(Dictionary<, >))
		{
			IDictionary obj2 = (IDictionary)value;
			IDictionary dictionary = (IDictionary)Activator.CreateInstance(type);
			{
				foreach (DictionaryEntry item2 in obj2)
				{
					dictionary.Add(item2.Key, item2.Value);
				}
				return dictionary;
			}
		}
		ModCore.Warn("[DeepCopy] Unhandled field type " + type.FullName + " - using shared reference. Implement IDeepCopyable<T> if deep copy is needed.");
		return value;
	}
}
