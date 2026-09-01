using System;

namespace BigAndSmall;

public struct EnumBool<TEnum> where TEnum : Enum
{
	private readonly bool _value;

	private readonly bool _isBool;

	public TEnum Outcome { get; private set; }

	private EnumBool(bool value)
	{
		_isBool = false;
		_value = value;
		Outcome = (TEnum)Enum.GetValues(typeof(TEnum)).GetValue(value ? 1 : 0);
	}

	private EnumBool(TEnum outcome)
	{
		Outcome = outcome;
		int num = Convert.ToInt32(outcome);
		_value = num != 0;
		_isBool = num < 2;
	}

	public static implicit operator EnumBool<TEnum>(bool value)
	{
		return new EnumBool<TEnum>(value);
	}

	public static implicit operator EnumBool<TEnum>(TEnum outcome)
	{
		return new EnumBool<TEnum>(outcome);
	}

	public static bool operator ==(EnumBool<TEnum> left, EnumBool<TEnum> right)
	{
		return left.Outcome.Equals(right.Outcome);
	}

	public static bool operator !=(EnumBool<TEnum> left, EnumBool<TEnum> right)
	{
		return !left.Outcome.Equals(right.Outcome);
	}

	public static bool operator ==(EnumBool<TEnum> left, bool right)
	{
		return left._value == right;
	}

	public static bool operator !=(EnumBool<TEnum> left, bool right)
	{
		return left._value != right;
	}

	public static bool AsBool(EnumBool<TEnum> value)
	{
		return value._value;
	}

	public static bool? AsPureBool(EnumBool<TEnum> value)
	{
		if (!value._isBool)
		{
			return null;
		}
		return value._value;
	}

	public override readonly bool Equals(object obj)
	{
		if (obj == null)
		{
			return false;
		}
		if (obj is EnumBool<TEnum> enumBool)
		{
			return Outcome.Equals(enumBool.Outcome);
		}
		if (obj is bool flag)
		{
			return _value == flag;
		}
		return false;
	}

	public override readonly int GetHashCode()
	{
		if (!_isBool)
		{
			return _value.GetHashCode() ^ Outcome.GetHashCode();
		}
		return _value ? 1 : 0;
	}

	public override readonly string ToString()
	{
		return Outcome.ToString();
	}
}
