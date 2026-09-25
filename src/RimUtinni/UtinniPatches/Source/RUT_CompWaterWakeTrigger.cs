using RimWorld;
using Verse;

namespace RimMandrake.Utinni.UtinniPatches
{
	// CRACKED_LANDS_SEALED_WAKE_MECHANISM_1 — the genuinely-new piece
	// RUT_SealedSleeper.xml's own header deferred: "a small rare-tick comp
	// that activates CompWakeUpDormant when a nearby cell turns to real
	// (non-boil) water terrain, plus the gather-crack-wax-after-wake job."
	//
	// MECHANISM, read not guessed (rimsage, CompCanBeDormant.cs full read
	// this pass): CompCanBeDormant.WakeUp() is public and already does
	// everything a wake needs to do — ends any dormancy job, updates the
	// attack-target cache, notifies the Lord. No stock comp offers a
	// terrain-triggered wake (CompWakeUpDormant's only triggers are
	// wakeUpOnDamage / wakeUpOnThingConstructedRadius /
	// wakeUpIfAnyTargetClose), so this comp supplies just the missing
	// trigger and calls straight into the stock wake path rather than
	// reimplementing any of it.
	//
	// "Real (non-boil) water" reuses this mod's own existing convention for
	// telling scalding water terrain apart from ordinary water —
	// RUT_IncidentWorker_WalkerSurfacing.cs (EnvironmentalHazards, not
	// touched by this file) already tests `terrain.IsWater &&
	// terrain.burnDamage > 0` for the opposite case (a creature that wants
	// hot water); this comp wants the complement.
	//
	// The "gather crack-wax off the flats after a wake" job: RUT_CrackWax
	// (ParentName="ResourceBase", ThingDefs_Items/RUT_CrackedLandsItems.xml)
	// is already alwaysHaulable by inheritance from ResourceBase like every
	// other raw resource in this mod (RUT_Bitumen etc.) — dropping it on the
	// ground next to the wakened sleeper is enough for the vanilla hauling
	// WorkGiver to pick it up as an ordinary "gather" job. No bespoke
	// WorkGiver/JobDriver is authored here: that would duplicate the stock
	// hauling system for no behavioural gain the item's own title asks for.
	public class CompProperties_WaterWakeTrigger : CompProperties
	{
		// How far out (in cells) the comp looks for water terrain each check.
		public float checkRadius = 3f;

		// How often (in ticks) the comp re-checks. Deliberately coarse —
		// "small rare-tick comp" per the item title; there is no gameplay
		// reason to check every tick for a terrain change that itself only
		// happens on a flood/liquid event.
		public int checkIntervalTicks = 2000;

		public ThingDef crackWaxDef;

		public IntRange crackWaxCountRange = new IntRange(1, 3);

		public CompProperties_WaterWakeTrigger()
		{
			compClass = typeof(CompWaterWakeTrigger);
		}
	}

	public class CompWaterWakeTrigger : ThingComp
	{
		// Scribed so a save/load mid-dormancy does not re-fire the wake
		// (and re-drop crack-wax) the next time the check happens to land on
		// a tick where water is still present.
		private bool triggered;

		public CompProperties_WaterWakeTrigger Props => (CompProperties_WaterWakeTrigger)props;

		public override void CompTick()
		{
			base.CompTick();
			if (triggered || !parent.Spawned)
			{
				return;
			}
			if (!parent.IsHashIntervalTick(Props.checkIntervalTicks))
			{
				return;
			}
			CheckForWater();
		}

		private void CheckForWater()
		{
			CompCanBeDormant dormant = parent.GetComp<CompCanBeDormant>();
			if (dormant == null)
			{
				// Nothing to wake; stop checking rather than spin forever on
				// a def that forgot the comp.
				triggered = true;
				return;
			}
			if (dormant.Awake)
			{
				// Already woken by one of the interim stock triggers
				// (wakeUpOnDamage / wakeUpOnThingConstructedRadius) —
				// nothing left for this comp to do.
				triggered = true;
				return;
			}

			Map map = parent.Map;
			foreach (IntVec3 cell in GenRadial.RadialCellsAround(parent.Position, Props.checkRadius, useCenter: true))
			{
				if (!cell.InBounds(map))
				{
					continue;
				}
				TerrainDef terrain = cell.GetTerrain(map);
				if (terrain != null && terrain.IsWater && !(terrain.burnDamage > 0f))
				{
					Trigger(dormant);
					return;
				}
			}
		}

		private void Trigger(CompCanBeDormant dormant)
		{
			triggered = true;
			dormant.WakeUp();
			DropCrackWax();
		}

		private void DropCrackWax()
		{
			if (Props.crackWaxDef == null || parent.Map == null)
			{
				return;
			}
			Thing wax = ThingMaker.MakeThing(Props.crackWaxDef);
			wax.stackCount = Props.crackWaxCountRange.RandomInRange;
			GenPlace.TryPlaceThing(wax, parent.Position, parent.Map, ThingPlaceMode.Near);
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref triggered, "triggered", false);
		}
	}
}
