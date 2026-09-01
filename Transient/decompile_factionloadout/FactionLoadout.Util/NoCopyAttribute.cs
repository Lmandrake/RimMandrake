using System;

namespace FactionLoadout.Util;

[AttributeUsage(AttributeTargets.Field)]
public sealed class NoCopyAttribute : Attribute
{
}
