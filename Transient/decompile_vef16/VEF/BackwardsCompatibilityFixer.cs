using System;
using System.Linq;
using Verse;

namespace VEF;

internal static class BackwardsCompatibilityFixer
{
	internal static void FixSettingsNameOrNamespace(Mod mod, ModSettings settings, string oldNamespace = null, string oldName = null)
	{
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Invalid comparison between Unknown and I4
		LogMessage val = Log.Messages.LastOrDefault();
		if (val != null && (int)val.type == 2 && val.text != null)
		{
			Type type = ((object)settings).GetType();
			if (val.text.StartsWith("Could not find class " + (oldNamespace ?? "VFECore") + "." + (oldName ?? type.Name) + " while resolving node ModSettings. Trying to use " + type.Namespace + "." + type.Name + " instead. Full node: "))
			{
				Log.Error("Settings related error detected, fixing. Feel free to ignore this and previous error, they should be gone the next time you start the game.");
				LongEventHandler.ExecuteWhenFinished((Action)mod.WriteSettings);
			}
		}
	}
}
