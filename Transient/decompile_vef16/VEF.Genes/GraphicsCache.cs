using System;
using Verse;

namespace VEF.Genes;

[StaticConstructorOnStartup]
public static class GraphicsCache
{
	public static Type cachedTextureType = typeof(CachedTexture);

	public static readonly object GeneBackground_Xenogene = Activator.CreateInstance(cachedTextureType, "UI/Icons/Genes/GeneBackground_Xenogene");

	public static readonly object GeneBackground_Endogene = Activator.CreateInstance(cachedTextureType, "UI/Icons/Genes/GeneBackground_Endogene");

	public static readonly object GeneBackground_Archite = Activator.CreateInstance(cachedTextureType, "UI/Icons/Genes/GeneBackground_ArchiteGene");
}
