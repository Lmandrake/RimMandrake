using System;

namespace BigAndSmall;

public static class MathHelpers
{
	public static bool ApproximatelyEquals(this float f1, float f2, float tolerance = 0.01f)
	{
		return Math.Abs(f1 - f2) < tolerance;
	}

	public static bool Approx(this float f1, float f2, float tolerance = 0.01f)
	{
		return f1.ApproximatelyEquals(f2, tolerance);
	}
}
