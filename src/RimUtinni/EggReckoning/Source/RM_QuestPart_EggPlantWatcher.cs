using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Utinni.EggReckoning
{
	/// <summary>
	/// WEBWORK_EGG_RECKONING_QUEST_1, §2b: "deliver the egg to a marked cell in
	/// the target's room while the site is not alerted... this is the family's
	/// one C# verb (a small QuestPart watching thing-position + site-alert
	/// state)."
	///
	/// DISCLOSED SIMPLIFICATION from the design's literal "the target's bedroom"
	/// framing: no vanilla mechanism identifies which building inside a
	/// procedurally generated Outpost SitePartDef belongs to a specific NPC (no
	/// SitePartWorker places a single trackable individual the way
	/// DownedRefugee/ItemStash's own site parts do for THEIRS). So "planted" here
	/// means an RM_OllathrixEgg Thing lying roofed and unfogged anywhere on the
	/// site's own map — haul it in, drop it, walk away — rather than a single
	/// pre-marked cell. This is a real, checkable condition, not a placeholder.
	///
	/// "Not alerted" reuses GenHostility.AnyHostileActiveThreatToPlayer, the
	/// same check Site.cs itself uses internally to decide when to fire its own
	/// site.AllEnemiesDefeated/NoActiveThreats signals (confirmed by reading
	/// Source/RimWorld/Planet/Site.cs live) — real vanilla "is there an active
	/// threat right now" semantics, not an invented stealth system, matching the
	/// design's own "no new vision/stealth system" instruction.
	///
	/// Ticks throttled to every CheckInterval ticks; a 60-cell site map costs
	/// nothing to scan that rarely. Enabled by inSignalEnable=site.MapGenerated
	/// (wired by RM_QuestNode_EggPlantWatcher), so it only starts watching once
	/// the player has actually arrived.
	/// </summary>
	public class RM_QuestPart_EggPlantWatcher : QuestPartActivable
	{
		public MapParent site;

		public string outSignalPlanted;

		public string outSignalDiscovered;

		private const int CheckInterval = 30;

		private static ThingDef eggDefCached;

		private static ThingDef EggDef
		{
			get
			{
				if (eggDefCached == null)
				{
					eggDefCached = DefDatabase<ThingDef>.GetNamedSilentFail("RM_OllathrixEgg");
				}
				return eggDefCached;
			}
		}

		public override IEnumerable<GlobalTargetInfo> QuestLookTargets
		{
			get
			{
				foreach (GlobalTargetInfo t in base.QuestLookTargets)
				{
					yield return t;
				}
				if (site != null)
				{
					yield return site;
				}
			}
		}

		public override void QuestPartTick()
		{
			base.QuestPartTick();
			if (site == null || !site.HasMap)
			{
				return;
			}
			if (Find.TickManager.TicksGame % CheckInterval != 0)
			{
				return;
			}

			Map map = site.Map;
			if (EggPlanted(map))
			{
				SendAndComplete(outSignalPlanted);
				return;
			}
			if (GenHostility.AnyHostileActiveThreatToPlayer(map, countDormantPawnsAsHostile: false))
			{
				SendAndComplete(outSignalDiscovered);
			}
		}

		private bool EggPlanted(Map map)
		{
			ThingDef eggDef = EggDef;
			if (eggDef == null)
			{
				return false;
			}
			List<Thing> eggs = map.listerThings.ThingsOfDef(eggDef);
			for (int i = 0; i < eggs.Count; i++)
			{
				Thing egg = eggs[i];
				if (egg == null || !egg.Spawned)
				{
					continue;
				}
				IntVec3 pos = egg.Position;
				if (pos.Roofed(map) && !pos.Fogged(map))
				{
					return true;
				}
			}
			return false;
		}

		private void SendAndComplete(string signal)
		{
			if (!signal.NullOrEmpty())
			{
				Find.SignalManager.SendSignal(new Signal(signal));
			}
			Complete();
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_References.Look(ref site, "site");
			Scribe_Values.Look(ref outSignalPlanted, "outSignalPlanted");
			Scribe_Values.Look(ref outSignalDiscovered, "outSignalDiscovered");
		}
	}
}
