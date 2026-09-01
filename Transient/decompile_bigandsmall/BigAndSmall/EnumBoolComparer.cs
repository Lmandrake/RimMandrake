using System;

namespace BigAndSmall;

public static class EnumBoolComparer
{
	public static bool CompareEnumBoolOutcome<TEnum1, TEnum2>(EnumBool<TEnum1> first, EnumBool<TEnum2> second) where TEnum1 : Enum where TEnum2 : Enum
	{
		bool? flag = EnumBool<TEnum1>.AsPureBool(first);
		bool? flag2 = EnumBool<TEnum2>.AsPureBool(second);
		bool? flag3 = flag;
		if (flag3.HasValue && flag2.HasValue)
		{
			return flag3.Value == flag2.Value;
		}
		return false;
	}
}
