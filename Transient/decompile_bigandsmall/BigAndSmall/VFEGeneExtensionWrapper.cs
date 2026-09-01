using System;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

public class VFEGeneExtensionWrapper
{
	private static Type VFEGeneExtType;

	private static FieldInfo backgroundPathEndogenesInfo;

	private static FieldInfo backgroundPathXenogenesInfo;

	private static FieldInfo backgroundPathArchiteInfo;

	private static FieldInfo hideGeneInfo;

	public DefModExtension ext;

	public string BackgroundPathEndogenes
	{
		get
		{
			return (string)backgroundPathEndogenesInfo.GetValue(ext);
		}
		set
		{
			backgroundPathEndogenesInfo.SetValue(ext, value);
		}
	}

	public string BackgroundPathXenogenes
	{
		get
		{
			return (string)backgroundPathXenogenesInfo.GetValue(ext);
		}
		set
		{
			backgroundPathXenogenesInfo.SetValue(ext, value);
		}
	}

	public string BackgroundPathArchite
	{
		get
		{
			return (string)backgroundPathArchiteInfo.GetValue(ext);
		}
		set
		{
			backgroundPathArchiteInfo.SetValue(ext, value);
		}
	}

	public bool HideGene
	{
		get
		{
			return (bool)hideGeneInfo.GetValue(ext);
		}
		set
		{
			hideGeneInfo.SetValue(ext, value);
		}
	}

	public VFEGeneExtensionWrapper(DefModExtension existingInstance = null)
	{
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Expected O, but got Unknown
		if (!VanillaExpanded.VEActive)
		{
			Log.Warning("Attempted to load VFE Gene Extension Wrapper without VFE being active.");
			return;
		}
		Type extensionType = GetExtensionType();
		if (extensionType == null)
		{
			Log.Error("Big and Small: Could not find VanillaGenesExpanded.GeneExtension class.");
			return;
		}
		CacheData();
		if (existingInstance != null)
		{
			ext = existingInstance;
		}
		else
		{
			ext = (DefModExtension)Activator.CreateInstance(extensionType);
		}
	}

	public static void CacheData()
	{
		if ((object)backgroundPathEndogenesInfo == null)
		{
			backgroundPathEndogenesInfo = AccessTools.Field(VFEGeneExtType, "backgroundPathEndogenes");
		}
		if ((object)backgroundPathXenogenesInfo == null)
		{
			backgroundPathXenogenesInfo = AccessTools.Field(VFEGeneExtType, "backgroundPathXenogenes");
		}
		if ((object)backgroundPathArchiteInfo == null)
		{
			backgroundPathArchiteInfo = AccessTools.Field(VFEGeneExtType, "backgroundPathArchite");
		}
		if ((object)hideGeneInfo == null)
		{
			hideGeneInfo = AccessTools.Field(VFEGeneExtType, "hideGene");
		}
	}

	public static Type GetExtensionType()
	{
		if (VFEGeneExtType == null)
		{
			VFEGeneExtType = AccessTools.TypeByName("VanillaGenesExpanded.GeneExtension");
			if (VFEGeneExtType == null)
			{
				Log.Error("Big and Small: Could not find VanillaGenesExpanded.GeneExtension class.");
			}
		}
		return VFEGeneExtType;
	}
}
