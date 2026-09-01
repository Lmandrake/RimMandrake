using System.Diagnostics;
using Verse;

namespace BigAndSmall.Utilities;

internal class DebugLog
{
	[Conditional("DEBUG")]
	public static void Message(string message)
	{
		Log.Message("[BigAndSmall] " + message);
	}
}
