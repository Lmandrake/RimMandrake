using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace VEF.Storyteller;

public class QuestChainDef : Def
{
	public string iconPath;

	public Texture2D icon;

	public Type workerClass;

	private QuestChainWorker cachedWorker;

	public List<PawnKindDef> uniqueCharacters;

	public QuestChainWorker Worker => cachedWorker;

	public QuestChainState State => GameComponent_QuestChains.Instance?.GetStateFor(this);

	public override void PostLoad()
	{
		((Editable)this).PostLoad();
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			if (!GenText.NullOrEmpty(iconPath))
			{
				icon = ContentFinder<Texture2D>.Get(iconPath, true);
			}
		});
		if (workerClass == null)
		{
			workerClass = typeof(QuestChainWorker);
		}
		cachedWorker = (QuestChainWorker)Activator.CreateInstance(workerClass);
		cachedWorker.def = this;
	}
}
