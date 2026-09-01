using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using RimWorld;
using Verse;

namespace FactionLoadout;

public class ForcedIdeoGameComponent : GameComponent
{
	public Dictionary<string, int> refToIdeoId = new Dictionary<string, int>();

	public const int NoFactionBucket = -1;

	[Unsaved(false)]
	public HashSet<string> failedRefs = new HashSet<string>();

	[Unsaved(false)]
	public Dictionary<(int loadId, int defIndex, ForcedIdeoSource source, string key), Ideo> resolvedCache = new Dictionary<(int, int, ForcedIdeoSource, string), Ideo>();

	public static bool AnyIdeologyEditsActive;

	public static ForcedIdeoGameComponent Current
	{
		get
		{
			Game game = Current.Game;
			if (game == null)
			{
				return null;
			}
			return game.GetComponent<ForcedIdeoGameComponent>();
		}
	}

	public static bool ClassicMode => Find.IdeoManager?.classicMode ?? false;

	public ForcedIdeoGameComponent(Game game)
	{
	}

	public static void RecomputeAnyEditsActive()
	{
		foreach (FactionEdit value in FactionEdit.ActiveFactionEdits.Values)
		{
			if (!string.IsNullOrEmpty(value.ForcedPrimaryIdeoKey))
			{
				AnyIdeologyEditsActive = true;
				return;
			}
			foreach (PawnKindEdit kindEdit in value.KindEdits)
			{
				if (!string.IsNullOrEmpty(kindEdit.ForcedIdeoKey))
				{
					AnyIdeologyEditsActive = true;
					return;
				}
			}
		}
		AnyIdeologyEditsActive = false;
	}

	public override void FinalizeInit()
	{
		if (!ModsConfig.IdeologyActive || ClassicMode)
		{
			return;
		}
		RecomputeAnyEditsActive();
		CleanupOrphanedBindings();
		if (!AnyIdeologyEditsActive)
		{
			return;
		}
		WarnMissingSavedFiles();
		foreach (Faction item in Find.FactionManager.AllFactionsListForReading)
		{
			EnsurePrimaryIdeo(item);
		}
		PreRealizeKindRefs();
	}

	public void EnsurePrimaryIdeo(Faction faction)
	{
		if (faction?.ideos == null || faction.IsPlayer || ClassicMode)
		{
			return;
		}
		FactionEdit activeEditFor = FactionEdit.GetActiveEditFor(faction.def);
		if (activeEditFor == null || string.IsNullOrEmpty(activeEditFor.ForcedPrimaryIdeoKey) || activeEditFor.ForcedPrimaryIdeoSourceKind == ForcedIdeoSource.FactionPrimary)
		{
			return;
		}
		Ideo orInjectIdeo = GetOrInjectIdeo(faction, activeEditFor.ForcedPrimaryIdeoSourceKind, activeEditFor.ForcedPrimaryIdeoKey);
		if (orInjectIdeo == null)
		{
			ModCore.Debug($"Forced primary ideology for faction '{faction.Name}' did not resolve ({activeEditFor.ForcedPrimaryIdeoSourceKind} '{activeEditFor.ForcedPrimaryIdeoKey}').");
		}
		else if (!faction.ideos.IsPrimary(orInjectIdeo))
		{
			Ideo primaryIdeo = faction.ideos.PrimaryIdeo;
			faction.ideos.IdeosMinorListForReading.Remove(orInjectIdeo);
			faction.ideos.SetPrimary(orInjectIdeo);
			if (faction.leader?.ideo != null && primaryIdeo != null && faction.leader.Ideo == primaryIdeo)
			{
				faction.leader.ideo.SetIdeo(orInjectIdeo);
			}
			ModCore.Log("Set forced primary ideology '" + orInjectIdeo.name + "' on faction '" + faction.Name + "'.");
		}
	}

	public Ideo GetOrInjectIdeo(Faction faction, ForcedIdeoSource source, string key)
	{
		if (!ModsConfig.IdeologyActive || ClassicMode)
		{
			return null;
		}
		if (source == ForcedIdeoSource.FactionPrimary)
		{
			if (faction == null)
			{
				return null;
			}
			FactionIdeosTracker ideos = faction.ideos;
			if (ideos == null)
			{
				return null;
			}
			return ideos.PrimaryIdeo;
		}
		if (string.IsNullOrEmpty(key))
		{
			return null;
		}
		(int, int, ForcedIdeoSource, string) cacheKey = CacheKeyFor(faction, source, key);
		Ideo val = ResolveFromCache(cacheKey, faction);
		if (val != null)
		{
			return val;
		}
		string text = RefKeyFor(faction, source, key);
		Ideo val2 = ResolveFromBinding(text, cacheKey, faction);
		if (val2 != null)
		{
			return val2;
		}
		if (!failedRefs.Contains(text))
		{
			return RealiseNewIdeo(faction, source, key, text, cacheKey);
		}
		return null;
	}

	public Ideo ResolveFromCache((int, int, ForcedIdeoSource, string) cacheKey, Faction faction)
	{
		if (!resolvedCache.TryGetValue(cacheKey, out var value))
		{
			return null;
		}
		if (value != null && Find.IdeoManager.IdeosListForReading.Contains(value))
		{
			EnsureRegisteredWith(faction, value);
			return value;
		}
		resolvedCache.Remove(cacheKey);
		return null;
	}

	public Ideo ResolveFromBinding(string refKey, (int, int, ForcedIdeoSource, string) cacheKey, Faction faction)
	{
		if (!refToIdeoId.TryGetValue(refKey, out var value))
		{
			return null;
		}
		Ideo val = FindById(value);
		if (val != null)
		{
			resolvedCache[cacheKey] = val;
			EnsureRegisteredWith(faction, val);
			return val;
		}
		refToIdeoId.Remove(refKey);
		return null;
	}

	public Ideo RealiseNewIdeo(Faction faction, ForcedIdeoSource source, string key, string refKey, (int, int, ForcedIdeoSource, string) cacheKey)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		if ((int)Scribe.mode != 0)
		{
			ModCore.Debug($"Deferring forced ideology realisation for '{refKey}': Scribe is {Scribe.mode}.");
			return null;
		}
		Rand.PushState();
		Ideo val;
		try
		{
			val = (Ideo)(source switch
			{
				ForcedIdeoSource.SavedFile => LoadFromFile(key, refKey), 
				ForcedIdeoSource.Preset => GenerateFromPreset(key, refKey, faction?.def), 
				_ => null, 
			});
			Ideo val2 = val;
			if (val2 == null)
			{
				val = null;
			}
			else
			{
				Find.IdeoManager.Add(val2);
				refToIdeoId[refKey] = val2.id;
				resolvedCache[cacheKey] = val2;
				EnsureRegisteredWith(faction, val2);
				ModCore.Log(string.Format("Realised forced ideology '{0}' from {1} '{2}' for faction '{3}' (id {4}).", val2.name, source, key, ((faction != null) ? faction.Name : null) ?? "<none>", val2.id));
				val = val2;
			}
		}
		finally
		{
			Rand.PopState();
		}
		return val;
	}

	public static void EnsureRegisteredWith(Faction faction, Ideo ideo)
	{
		if (faction?.ideos != null && !faction.ideos.Has(ideo))
		{
			faction.ideos.IdeosMinorListForReading.Add(ideo);
		}
	}

	public static (int, int, ForcedIdeoSource, string) CacheKeyFor(Faction faction, ForcedIdeoSource source, string key)
	{
		if (source != 0)
		{
			return (faction?.loadID ?? (-1), -1, source, key);
		}
		return (-1, ((int?)((Def)(faction?.def?)).index) ?? (-1), source, key);
	}

	public static string RefKeyFor(Faction faction, ForcedIdeoSource source, string key)
	{
		if (source == ForcedIdeoSource.SavedFile)
		{
			return "def:" + (((Def)(faction?.def?)).defName ?? "none") + ":" + source.ToString() + ":" + key;
		}
		return (faction?.loadID ?? (-1)) + ":" + source.ToString() + ":" + key;
	}

	public Ideo LoadFromFile(string fileName, string refKey)
	{
		string text = GenFilePaths.AbsPathForIdeo(fileName);
		if (!File.Exists(text))
		{
			failedRefs.Add(refKey);
			return null;
		}
		Ideo val = default(Ideo);
		if (!GameDataSaveLoader.TryLoadIdeo(text, ref val) || val == null)
		{
			failedRefs.Add(refKey);
			ModCore.Warn("Forced ideology file '" + fileName + "' exists but could not be loaded (invalid .rid file).");
			return null;
		}
		IdeoGenerator.InitLoadedIdeo(val);
		return val;
	}

	public Ideo GenerateFromPreset(string defName, string refKey, FactionDef forFaction)
	{
		//IL_016b: Unknown result type (might be due to invalid IL or missing references)
		IdeoPresetDef namedSilentFail = DefDatabase<IdeoPresetDef>.GetNamedSilentFail(defName);
		if (namedSilentFail == null)
		{
			failedRefs.Add(refKey);
			ModCore.Warn("Forced ideology preset def '" + defName + "' not found (mod removed?).");
			return null;
		}
		FactionDef fac = forFaction ?? Faction.OfPlayerSilentFail?.def ?? DefDatabase<FactionDef>.AllDefsListForReading.FirstOrDefault();
		foreach (MemeDef meme in namedSilentFail.memes)
		{
			if (!IdeoUtility.IsMemeAllowedFor(meme, fac))
			{
				ModCore.Warn("Forced ideology preset '" + defName + "' contains meme '" + ((Def)meme).defName + "' which faction def '" + ((Def)(fac?)).defName + "' does not normally allow.");
			}
		}
		List<MemeDef> list = namedSilentFail.memes.ToList();
		MemeDef item = default(MemeDef);
		if (!GenCollection.Any<MemeDef>(list, (Predicate<MemeDef>)((MemeDef m) => (int)m.category == 1)) && GenCollection.TryRandomElement<MemeDef>(DefDatabase<MemeDef>.AllDefsListForReading.Where((MemeDef m) => (int)m.category == 1 && IdeoUtility.IsMemeAllowedFor(m, fac)), ref item))
		{
			list.Add(item);
		}
		return IdeoGenerator.GenerateIdeo(new IdeoGenerationParms(fac, false, (List<PreceptDef>)null, (List<MemeDef>)null, list, namedSilentFail.classicPlus, true, false, false, "", (List<StyleCategoryDef>)null, (List<DeityPreset>)null, false, "", false));
	}

	public static Ideo FindById(int id)
	{
		return Find.IdeoManager.IdeosListForReading.FirstOrDefault((Ideo t) => t.id == id);
	}

	public HashSet<string> BuildValidRefKeys()
	{
		HashSet<string> valid = new HashSet<string>();
		List<Faction> allFactionsListForReading = Find.FactionManager.AllFactionsListForReading;
		foreach (KeyValuePair<string, FactionEdit> pair in FactionEdit.ActiveFactionEdits)
		{
			List<Faction> instances = allFactionsListForReading.Where((Faction f) => ((Def)f.def).defName == pair.Key).ToList();
			bool synthetic = instances.Count == 0;
			AddRef(pair.Value.ForcedPrimaryIdeoSourceKind, pair.Value.ForcedPrimaryIdeoKey);
			foreach (PawnKindEdit kindEdit in pair.Value.KindEdits)
			{
				AddRef(kindEdit.ForcedIdeoSourceKind, kindEdit.ForcedIdeoKey);
			}
			void AddRef(ForcedIdeoSource source, string key)
			{
				if (!string.IsNullOrEmpty(key) && source != ForcedIdeoSource.FactionPrimary)
				{
					if (!synthetic)
					{
						foreach (Faction item in instances)
						{
							valid.Add(RefKeyFor(item, source, key));
						}
						return;
					}
					valid.Add(RefKeyFor(null, source, key));
				}
			}
		}
		return valid;
	}

	public void CleanupOrphanedBindings()
	{
		if (refToIdeoId.Count == 0)
		{
			return;
		}
		HashSet<string> valid = BuildValidRefKeys();
		List<string> list = refToIdeoId.Keys.Where((string k) => !valid.Contains(k)).ToList();
		foreach (string item in list)
		{
			Ideo val = FindById(refToIdeoId[item]);
			refToIdeoId.Remove(item);
			if (val == null)
			{
				continue;
			}
			foreach (Faction item2 in Find.FactionManager.AllFactionsListForReading)
			{
				if (item2.ideos != null && !item2.ideos.IsPrimary(val))
				{
					item2.ideos.IdeosMinorListForReading.Remove(val);
				}
			}
			ModCore.Log("Unbound orphaned forced ideology '" + val.name + "' (ref '" + item + "' no longer in active preset).");
		}
		if (list.Count > 0)
		{
			resolvedCache.Clear();
		}
	}

	public void WarnMissingSavedFiles()
	{
		List<string> missing = new List<string>();
		foreach (FactionEdit value in FactionEdit.ActiveFactionEdits.Values)
		{
			Check(value.ForcedPrimaryIdeoSourceKind, value.ForcedPrimaryIdeoKey);
			foreach (PawnKindEdit kindEdit in value.KindEdits)
			{
				Check(kindEdit.ForcedIdeoSourceKind, kindEdit.ForcedIdeoKey);
			}
		}
		if (!GenList.NullOrEmpty<string>((IList<string>)missing))
		{
			ModCore.Warn("Forced ideology saved file(s) not found on this machine: " + string.Join(", ", missing) + ". Affected pawns keep their faction's ideology until the file(s) exist in the Ideos folder.");
		}
		void Check(ForcedIdeoSource source, string key)
		{
			if (source == ForcedIdeoSource.SavedFile && !string.IsNullOrEmpty(key) && !File.Exists(GenFilePaths.AbsPathForIdeo(key)) && !missing.Contains(key))
			{
				missing.Add(key);
			}
		}
	}

	public void PreRealizeKindRefs()
	{
		List<Faction> allFactionsListForReading = Find.FactionManager.AllFactionsListForReading;
		foreach (KeyValuePair<string, FactionEdit> pair in FactionEdit.ActiveFactionEdits)
		{
			List<Faction> list = allFactionsListForReading.Where((Faction f) => ((Def)f.def).defName == pair.Key).ToList();
			foreach (PawnKindEdit kindEdit in pair.Value.KindEdits)
			{
				if (string.IsNullOrEmpty(kindEdit.ForcedIdeoKey) || kindEdit.ForcedIdeoSourceKind == ForcedIdeoSource.FactionPrimary)
				{
					continue;
				}
				if (list.Count == 0)
				{
					GetOrInjectIdeo(null, kindEdit.ForcedIdeoSourceKind, kindEdit.ForcedIdeoKey);
					continue;
				}
				foreach (Faction item in list)
				{
					GetOrInjectIdeo(item, kindEdit.ForcedIdeoSourceKind, kindEdit.ForcedIdeoKey);
				}
			}
		}
	}

	public override void ExposeData()
	{
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Invalid comparison between Unknown and I4
		Scribe_Collections.Look<string, int>(ref refToIdeoId, "refToIdeoId", (LookMode)1, (LookMode)1);
		if ((int)Scribe.mode == 4 && refToIdeoId == null)
		{
			refToIdeoId = new Dictionary<string, int>();
		}
	}
}
