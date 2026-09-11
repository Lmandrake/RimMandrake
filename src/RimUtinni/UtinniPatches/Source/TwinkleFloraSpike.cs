// TWINKLE_FLORA_SPIKE_1 -- owner ruling, 2026-09-10, TIMEBOXED: prove a slow
// glow-pulse on ONE plant, measure the per-plant tick cost, report back
// before any wider use. See infrastructure/state/items/TWINKLE_FLORA_SPIKE_1.md
// for the full feasibility report; this file is the prototype it reports on.
//
// Not wired into any live biome or shipped plant -- RUT_TwinkleSpikeTestPlant
// (Defs/ThingDefs_Plants/RUT_TwinkleSpikeTestPlant.xml) is the only def that
// references this code, and nothing places it in a wildPlants list. Spawn it
// by hand (dev spawner or a bridge call) to observe or measure it.
//
// Mechanism, verified against Source before writing a line of this (never
// guess): Plant is a baked-mesh Thing -- RimWorld prints plants into a
// per-cell map-mesh SECTION once and only re-prints on an explicit
// map.mapDrawer.MapMeshDirty(pos, MapMeshFlagDefOf.Things) call (confirmed
// grep hits: Verse/Thing.cs, RimWorld/Plant.cs, Verse/CompGlower.cs all use
// exactly this call for the same reason -- a thing whose appearance changed
// and needs a redraw). A per-tick color mutation with no dirty call would be
// invisible; the real cost to measure is the dirty-and-reprint operation's
// rate, not a naive per-tick Color.Lerp.
//
// Graphic_Single.GetColoredVersion (Verse/Graphic_Single.cs) routes every
// distinct color through GraphicDatabase.Get<Graphic_Single>(path, shader,
// drawSize, color, colorTwo, data), which is a CACHE keyed on those exact
// values -- a continuously-varying float color would mint a new cached
// Graphic/Material forever and never reuse one. Quantizing the pulse to a
// small fixed step count (PulseSteps below) is load-bearing, not a style
// choice: it bounds that cache to PulseSteps entries per plant instance
// forever, instead of growing without limit for as long as the plant lives.

using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.UtinniPatches
{
	public class CompProperties_GlowPulse : CompProperties
	{
		// "Slow": one full low->high->low cycle in roughly this many ticks.
		// 2500 ticks is one in-game hour; a rise-and-fall of "a few hours"
		// reads as the sheet's "slow" without needing per-tick work.
		public int cyclePeriodTicks = 15000;

		// Bounds the GraphicDatabase cache footprint per instance (see file
		// header) -- never raise this without re-checking that reasoning.
		public int pulseSteps = 12;

		public Color colorLow = new Color(1f, 1f, 1f, 1f);
		public Color colorHigh = new Color(1.35f, 1.2f, 0.75f, 1f);

		public CompProperties_GlowPulse()
		{
			compClass = typeof(CompGlowPulse);
		}
	}

	public class CompGlowPulse : ThingComp
	{
		private int lastStep = -1;

		public CompProperties_GlowPulse Props => (CompProperties_GlowPulse)props;

		public Color CurrentColor { get; private set; }

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			base.PostSpawnSetup(respawningAfterLoad);
			CurrentColor = Props.colorLow;
			lastStep = 0;
		}

		// Rare tick (every 250 ticks) is the measurement subject named in the
		// item title. A naive implementation would run this every normal
		// tick; CompTickRare alone is a 250x reduction before any other
		// optimization, and is the first number the feasibility report owes.
		public override void CompTickRare()
		{
			base.CompTickRare();
			if (!parent.Spawned)
			{
				return;
			}

			int steps = Mathf.Max(1, Props.pulseSteps);
			float phase = (float)(parent.thingIDNumber % 997) / 997f; // per-instance offset so a field doesn't pulse in lockstep
			float t = ((float)(Find.TickManager.TicksGame + parent.thingIDNumber) / Props.cyclePeriodTicks) + phase;
			float wave = (Mathf.Sin(t * 2f * Mathf.PI) + 1f) * 0.5f; // 0..1
			int step = Mathf.Clamp(Mathf.RoundToInt(wave * (steps - 1)), 0, steps - 1);

			if (step == lastStep)
			{
				return; // most rare-ticks land on the same quantized step -- no dirty call needed
			}
			lastStep = step;
			CurrentColor = Color.Lerp(Props.colorLow, Props.colorHigh, (float)step / (steps - 1));
			parent.Map.mapDrawer.MapMeshDirty(parent.Position, MapMeshFlagDefOf.Things);
		}
	}

	// Plant.Graphic is virtual specifically so a subclass can override it;
	// a ThingComp cannot override its parent Thing's members, so the pulse
	// needs this thin subclass rather than living entirely in the comp.
	public class RUT_PlantTwinkle : Plant
	{
		public override Graphic Graphic
		{
			get
			{
				CompGlowPulse comp = GetComp<CompGlowPulse>();
				Graphic baseGraphic = base.Graphic;
				if (comp == null)
				{
					return baseGraphic;
				}
				return baseGraphic.GetColoredVersion(baseGraphic.Shader, comp.CurrentColor, comp.CurrentColor);
			}
		}
	}
}
