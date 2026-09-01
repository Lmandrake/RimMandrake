using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class ConditionalGraphicSet
{
	public enum CGTrigger
	{
		Humanlike,
		SlaveOrPrisoner,
		Colonist,
		NonColonist,
		Slave,
		Prisoner,
		OfColony,
		HostileToPlayer,
		NeutralToPlayer,
		AlliedToPlayer,
		HasFaction,
		HasIdeo,
		Dead,
		Rotted,
		Dessicated,
		Downed,
		RoyaltyDLC,
		Psycaster,
		IdeologyDLC,
		BiotechDLC,
		Bloodfeeder,
		AnomalyDLC,
		Mutant,
		Ghoul
	}

	public List<ConditionalGraphicSet> alts = new List<ConditionalGraphicSet>();

	public List<CGTrigger> requirements = new List<CGTrigger>();

	public List<MemeDef> requiredMemes = new List<MemeDef>();

	public List<string> tagRequirements = new List<string>();

	public bool twoClrMask = true;

	protected AdvancedColor colorA;

	protected AdvancedColor colorB;

	public ShaderTypeDef shader;

	public bool useSkinShader;

	public bool useFactionRNGSeed;

	public bool useSimplePawnSeed;

	[NoTranslate]
	public string texPath;

	[NoTranslate]
	public List<string> texPaths;

	[NoTranslate]
	public string texPathFemale;

	[NoTranslate]
	public List<string> texPathsFemale;

	[NoTranslate]
	public string maskPath;

	[NoTranslate]
	public List<string> maskPaths;

	public List<BodyTypeGraphicData> bodyTypeGraphicPaths;

	public ConditionalGraphicSet GetActiveGraphicsSet(Pawn pawn, PawnRenderNode node)
	{
		ConditionalGraphicSet result = this;
		foreach (ConditionalGraphicSet alt in alts)
		{
			if (alt.GetState(pawn, node))
			{
				result = alt;
				break;
			}
		}
		return result;
	}

	public Color GetColorA(PawnRenderNode renderNode, Color fallback)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		if (colorA != null)
		{
			return colorA.GetColor(renderNode, fallback);
		}
		return fallback;
	}

	public Color GetColorB(PawnRenderNode renderNode, Color fallback)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		if (colorB != null)
		{
			return colorB.GetColor(renderNode, fallback);
		}
		return fallback;
	}

	public unsafe bool GetState(Pawn pawn, PawnRenderNode node)
	{
		if (GenList.NullOrEmpty<CGTrigger>((IList<CGTrigger>)requirements) && GenList.NullOrEmpty<string>((IList<string>)tagRequirements) && GenList.NullOrEmpty<MemeDef>((IList<MemeDef>)requiredMemes))
		{
			return true;
		}
		Dictionary<CGTrigger, Func<bool>> dictionary = new Dictionary<CGTrigger, Func<bool>>
		{
			{
				CGTrigger.Humanlike,
				() => pawn.RaceProps.Humanlike
			},
			{
				CGTrigger.SlaveOrPrisoner,
				() => pawn.IsSlave || pawn.IsPrisoner
			},
			{
				CGTrigger.Colonist,
				() => pawn.IsColonist
			},
			{
				CGTrigger.NonColonist,
				() => !pawn.IsColonist
			},
			{
				CGTrigger.Slave,
				() => pawn.IsSlave
			},
			{
				CGTrigger.Prisoner,
				() => pawn.IsPrisoner
			},
			{
				CGTrigger.OfColony,
				() => ((Thing)pawn).Faction == Faction.OfPlayerSilentFail
			},
			{
				CGTrigger.HasFaction,
				() => ((Thing)pawn).Faction != null
			},
			{
				CGTrigger.HasIdeo,
				() => pawn.Ideo != null
			},
			{
				CGTrigger.Dead,
				() => pawn.Dead
			},
			{
				CGTrigger.Rotted,
				delegate
				{
					//IL_0006: Unknown result type (might be due to invalid IL or missing references)
					//IL_000b: Unknown result type (might be due to invalid IL or missing references)
					RotStage rotStage = RottableUtility.GetRotStage((Thing)(object)pawn);
					return ((object)(RotStage)(ref rotStage)/*cast due to .constrained prefix*/).Equals((object)(RotStage)1);
				}
			},
			{
				CGTrigger.Dessicated,
				delegate
				{
					//IL_0006: Unknown result type (might be due to invalid IL or missing references)
					//IL_000b: Unknown result type (might be due to invalid IL or missing references)
					RotStage rotStage2 = RottableUtility.GetRotStage((Thing)(object)pawn);
					return ((object)(RotStage)(ref rotStage2)/*cast due to .constrained prefix*/).Equals((object)(RotStage)2);
				}
			},
			{
				CGTrigger.Downed,
				() => pawn.Downed
			},
			{
				CGTrigger.HostileToPlayer,
				() => GenHostility.HostileTo((Thing)(object)pawn, Faction.OfPlayerSilentFail)
			},
			{
				CGTrigger.NeutralToPlayer,
				delegate
				{
					//IL_0016: Unknown result type (might be due to invalid IL or missing references)
					//IL_001c: Invalid comparison between Unknown and I4
					Faction faction = ((Thing)pawn).Faction;
					return faction != null && (int)faction.RelationKindWith(Faction.OfPlayerSilentFail) == 1;
				}
			},
			{
				CGTrigger.AlliedToPlayer,
				delegate
				{
					//IL_0016: Unknown result type (might be due to invalid IL or missing references)
					//IL_001c: Invalid comparison between Unknown and I4
					Faction faction2 = ((Thing)pawn).Faction;
					return faction2 != null && (int)faction2.RelationKindWith(Faction.OfPlayerSilentFail) == 2;
				}
			},
			{
				CGTrigger.RoyaltyDLC,
				() => ModsConfig.RoyaltyActive
			},
			{
				CGTrigger.Psycaster,
				() => PawnUtility.GetPsylinkLevel(pawn) > 0
			},
			{
				CGTrigger.IdeologyDLC,
				() => ModsConfig.IdeologyActive
			},
			{
				CGTrigger.BiotechDLC,
				() => ModsConfig.BiotechActive
			},
			{
				CGTrigger.Bloodfeeder,
				new Func<bool>(pawn, (nint)(delegate*<Pawn, bool>)(&GeneUtility.IsBloodfeeder))
			},
			{
				CGTrigger.AnomalyDLC,
				() => ModsConfig.AnomalyActive
			},
			{
				CGTrigger.Mutant,
				() => pawn.IsMutant
			},
			{
				CGTrigger.Ghoul,
				() => pawn.IsGhoul
			}
		};
		foreach (CGTrigger requirement in requirements)
		{
			if (dictionary.TryGetValue(requirement, out var value) && !value())
			{
				return false;
			}
		}
		foreach (string tagRequirement in tagRequirements)
		{
			if (!((Thing)(object)pawn).HasTagged(tagRequirement))
			{
				return false;
			}
		}
		if (ModsConfig.IdeologyActive && !GenList.NullOrEmpty<MemeDef>((IList<MemeDef>)requiredMemes))
		{
			return false;
		}
		foreach (MemeDef requiredMeme in requiredMemes)
		{
			Ideo ideo = pawn.Ideo;
			if (ideo != null && !ideo.memes.Contains(requiredMeme))
			{
				return false;
			}
		}
		return true;
	}

	public Shader ShaderFor(Pawn pawn)
	{
		ShaderTypeDef obj = shader;
		if ((Object)(object)((obj != null) ? obj.Shader : null) != (Object)null)
		{
			return shader.Shader;
		}
		if (useSkinShader)
		{
			Shader skinShader = ShaderUtility.GetSkinShader(pawn);
			if ((Object)(object)skinShader != (Object)null)
			{
				return skinShader;
			}
		}
		return ShaderTypeDefOf.CutoutComplex.Shader;
	}

	public string MaskPathFor(Pawn pawn, PawnRenderNode node)
	{
		if (!GenList.NullOrEmpty<string>((IList<string>)maskPaths))
		{
			RandBlock val = default(RandBlock);
			((RandBlock)(ref val))._002Ector(TexSeedFor(pawn, node, useFactionRNGSeed));
			try
			{
				return GenCollection.RandomElement<string>((IEnumerable<string>)maskPaths);
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
			}
		}
		return maskPath;
	}

	public string TexPathFor(Pawn pawn, PawnRenderNode node)
	{
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Invalid comparison between Unknown and I4
		if (bodyTypeGraphicPaths != null)
		{
			foreach (BodyTypeGraphicData bodyTypeGraphicPath in bodyTypeGraphicPaths)
			{
				if (pawn.story.bodyType == bodyTypeGraphicPath.bodyType)
				{
					return bodyTypeGraphicPath.texturePath;
				}
			}
		}
		RandBlock val = default(RandBlock);
		if ((int)pawn.gender == 2)
		{
			if (!GenList.NullOrEmpty<string>((IList<string>)texPathsFemale))
			{
				((RandBlock)(ref val))._002Ector(TexSeedFor(pawn, node, useFactionRNGSeed));
				try
				{
					return GenCollection.RandomElement<string>((IEnumerable<string>)texPathsFemale);
				}
				finally
				{
					((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
				}
			}
			if (!GenText.NullOrEmpty(texPathFemale))
			{
				return texPathFemale;
			}
		}
		if (!GenList.NullOrEmpty<string>((IList<string>)texPaths))
		{
			((RandBlock)(ref val))._002Ector(TexSeedFor(pawn, node, useFactionRNGSeed));
			try
			{
				return GenCollection.RandomElement<string>((IEnumerable<string>)texPaths);
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
			}
		}
		return texPath;
	}

	protected virtual int TexSeedFor(Pawn pawn, PawnRenderNode node, bool useFactionSeed)
	{
		if (useSimplePawnSeed)
		{
			return ((Thing)pawn).thingIDNumber;
		}
		if (useFactionSeed)
		{
			int num = 0;
			Faction faction = ((Thing)pawn).Faction;
			if (faction != null)
			{
				num += faction.GetUniqueLoadID().GetHashCode();
				FactionIdeosTracker ideos = faction.ideos;
				Ideo val = ((ideos != null) ? ideos.PrimaryIdeo : null);
				if (val != null)
				{
					num += val.GetUniqueLoadID().GetHashCode();
				}
			}
			return num;
		}
		int texSeed = node.Props.texSeed;
		texSeed += ((Thing)pawn).thingIDNumber;
		if (node.hediff != null)
		{
			texSeed += node.hediff.loadID;
		}
		if (node.apparel != null)
		{
			texSeed += ((Thing)node.apparel).thingIDNumber;
		}
		if (node.trait != null)
		{
			texSeed += ((Def)node.trait.def).index;
		}
		if (node.gene != null)
		{
			texSeed += node.gene.loadID;
		}
		return texSeed;
	}
}
