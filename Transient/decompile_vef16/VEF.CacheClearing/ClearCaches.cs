using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace VEF.CacheClearing;

public static class ClearCaches
{
	private static readonly Type[] TypesWithClearMethod = new Type[3]
	{
		typeof(ICollection<>),
		typeof(Queue<>),
		typeof(Stack<>)
	};

	public static HashSet<Type> clearCacheTypes = new HashSet<Type>();

	public static event Action<HashSet<object>> OnClearCache;

	internal static void ClearCache()
	{
		foreach (Type clearCacheType in clearCacheTypes)
		{
			ClearFields(clearCacheType, null, BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
		}
		if (ClearCaches.OnClearCache == null)
		{
			return;
		}
		HashSet<object> hashSet = new HashSet<object>();
		ClearCaches.OnClearCache(hashSet);
		foreach (object item in hashSet.Where((object x) => x != null))
		{
			ClearFields(item.GetType(), item, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
		}
	}

	public static void ClearFields(Type type, object instance, BindingFlags flags)
	{
		try
		{
			FieldInfo[] fields = type.GetFields(flags);
			foreach (FieldInfo fieldInfo in fields)
			{
				if (GenAttribute.HasAttribute<NoCacheClearingAttribute>((MemberInfo)fieldInfo))
				{
					break;
				}
				Type fieldType = fieldInfo.FieldType;
				if (typeof(IDictionary).IsAssignableFrom(fieldType))
				{
					(fieldInfo.GetValue(instance) as IDictionary)?.Clear();
				}
				else if (typeof(IList).IsAssignableFrom(fieldType))
				{
					(fieldInfo.GetValue(instance) as IList)?.Clear();
				}
				else if (typeof(Queue).IsAssignableFrom(fieldType))
				{
					(fieldInfo.GetValue(instance) as Queue)?.Clear();
				}
				else if (typeof(Stack).IsAssignableFrom(fieldType))
				{
					(fieldInfo.GetValue(instance) as Stack)?.Clear();
				}
				else if (fieldType.IsGenericType && fieldType.GetGenericArguments().Length == 1 && TypesWithClearMethod.Any((Type typeWithClear) => typeWithClear.MakeGenericType(fieldType.GetGenericArguments()).IsAssignableFrom(fieldType)))
				{
					object value = fieldInfo.GetValue(instance);
					if (value != null)
					{
						AccessTools.Method(value.GetType(), "Clear", Array.Empty<Type>(), (Type[])null)?.Invoke(value, Array.Empty<object>());
					}
				}
			}
		}
		catch (Exception ex)
		{
			if (instance == null)
			{
				Log.ErrorOnce($"Failed clearing cache for type {GeneralExtensions.FullDescription(type)}, exception:\n{ex}", type.GetHashCode());
			}
			else
			{
				Log.ErrorOnce($"Failed clearing cache for type {GeneralExtensions.FullDescription(type)} with instance {instance}, exception:\n{ex}", Gen.HashCombineInt(type.GetHashCode(), instance.GetHashCode()));
			}
		}
	}
}
