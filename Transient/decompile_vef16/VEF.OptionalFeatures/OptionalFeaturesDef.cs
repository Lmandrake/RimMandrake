using System;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace VEF.OptionalFeatures;

public class OptionalFeaturesDef : Def
{
	public string feature;

	public Type activationClass;

	[Unsaved(false)]
	public MethodInfo activationMethod;

	public string harmonyCategory;

	public bool IsActive { get; private set; }

	public override void ResolveReferences()
	{
		((Def)this).ResolveReferences();
		if (activationClass != null)
		{
			activationMethod = activationClass.GetMethod("ApplyFeature", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic, null, new Type[1] { typeof(Harmony) }, null);
		}
	}

	public void Activate()
	{
		if (!IsActive)
		{
			IsActive = true;
			if (activationClass != null && harmonyCategory != null)
			{
				Log.WarningOnce(string.Format("Feature {0} has both {1} and {2} specified, only {3} will be used. Category: {4}, type: {5}.", feature, "activationClass", "harmonyCategory", "harmonyCategory", harmonyCategory, activationClass), feature.GetHashCode());
			}
			if (!GenText.NullOrEmpty(harmonyCategory))
			{
				VEF_Mod.harmonyInstance.PatchCategory(harmonyCategory);
			}
			else if (activationMethod == null)
			{
				Log.ErrorOnce("Feature " + feature + " with type " + Gen.ToStringSafe<Type>(activationClass) + " does not have ApplyFeature method or does not specify a harmony category", feature.GetHashCode());
			}
			else
			{
				activationMethod.Invoke(null, new object[1] { VEF_Mod.harmonyInstance });
			}
		}
	}
}
