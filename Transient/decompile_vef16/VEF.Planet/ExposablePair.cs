using Verse;

namespace VEF.Planet;

public class ExposablePair : IExposable
{
	public object key;

	public object value;

	public ExposablePair(object key, object value)
	{
		this.key = key;
		this.value = value;
	}

	public void ExposeData()
	{
		Scribe_Values.Look<object>(ref key, "key", (object)null, false);
		Scribe_Values.Look<object>(ref value, "value", (object)null, false);
	}
}
