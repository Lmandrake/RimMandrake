using System.Collections.Generic;
using System.Linq;
using RimWorld;
using VEF.CacheClearing;
using Verse;

namespace VEF.Weathers;

[StaticConstructorOnStartup]
internal class WeatherOverlay_Effects : WeatherOverlayDualPanner
{
	public Dictionary<Map, int> nextDamageTickForMap = new Dictionary<Map, int>();

	public WeatherOverlay_Effects()
	{
		ClearCaches.OnClearCache += delegate
		{
			nextDamageTickForMap.Clear();
		};
	}

	public override void TickOverlay(Map map, float lerpFactor)
	{
		((WeatherOverlayDualPanner)this).TickOverlay(map, lerpFactor);
		if (VFEGlobal.settings.weatherDamagesOptions.TryGetValue(((Def)map.weatherManager.curWeather).defName, out var value) && !value)
		{
			return;
		}
		WeatherEffectsExtension modExtension = ((Def)map.weatherManager.curWeather).GetModExtension<WeatherEffectsExtension>();
		if (modExtension != null && (modExtension.activeOnWeatherPerceived == null || map.weatherManager.CurWeatherPerceived == modExtension.activeOnWeatherPerceived))
		{
			nextDamageTickForMap.TryGetValue(map, out var value2);
			if (value2 == 0 || Find.TickManager.TicksGame - value2 > modExtension.ticksInterval.max)
			{
				value2 = (nextDamageTickForMap[map] = NextDamageTick(modExtension));
			}
			if (Find.TickManager.TicksGame > value2)
			{
				DoDamage(modExtension, map);
				nextDamageTickForMap[map] = NextDamageTick(modExtension);
			}
		}
	}

	public int NextDamageTick(WeatherEffectsExtension options)
	{
		return Find.TickManager.TicksGame + Rand.RangeInclusive(options.ticksInterval.min, options.ticksInterval.max);
	}

	public void DoDamage(WeatherEffectsExtension options, Map map)
	{
		//IL_012c: Unknown result type (might be due to invalid IL or missing references)
		for (int num = map.listerThings.AllThings.Count - 1; num >= 0; num--)
		{
			Thing val = map.listerThings.AllThings[num];
			if (CanDamage(val, map, options))
			{
				Pawn val2 = (Pawn)(object)((val is Pawn) ? val : null);
				if (val2 != null)
				{
					DoPawnDamage(val2, options);
				}
				else
				{
					DoThingDamage(val, options);
				}
			}
		}
		if (options.damageToApply != null)
		{
			IEnumerable<Pawn> enumerable = map.mapPawns.AllPawns.Where((Pawn x) => CanDamage((Thing)(object)x, map, options));
			List<Pawn> list = RandomlySelectedItems(enumerable, (int)((float)enumerable.Count() * options.percentOfPawnsToDealDamage)).ToList();
			DamageInfo val3 = default(DamageInfo);
			for (int num2 = list.Count - 1; num2 >= 0; num2--)
			{
				((DamageInfo)(ref val3))._002Ector(options.damageToApply, ((FloatRange)(ref options.damageRange)).RandomInRange, 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false);
				((Thing)list[num2]).TakeDamage(val3);
			}
		}
	}

	public bool CanDamage(Thing thing, Map map, WeatherEffectsExtension options)
	{
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val != null && !val.RaceProps.IsFlesh && !options.worksOnNonFleshPawns)
		{
			return false;
		}
		if (!GenGrid.InBounds(thing.Position, map) || (GridsUtility.Roofed(thing.Position, map) && !options.worksIndoors))
		{
			return false;
		}
		return true;
	}

	public void DoPawnDamage(Pawn p, WeatherEffectsExtension options)
	{
		if (options.hediffsToApply == null)
		{
			return;
		}
		foreach (HediffAndStat item in options.hediffsToApply)
		{
			HediffDef val = HediffDef.Named(item.hediff);
			if (val != null)
			{
				float num = item.severityOffset;
				if (item.effectMultiplyingStat != null)
				{
					num *= StatExtension.GetStatValue((Thing)(object)p, item.effectMultiplyingStat, true, -1);
				}
				if (num != 0f)
				{
					HealthUtility.AdjustSeverity(p, val, num);
				}
			}
		}
	}

	public void DoThingDamage(Thing thing, WeatherEffectsExtension options)
	{
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Invalid comparison between Unknown and I4
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Invalid comparison between Unknown and I4
		if (options.killsPlants && thing is Plant)
		{
			if (Rand.Value < options.chanceToKillPlants)
			{
				thing.Kill((DamageInfo?)null, (Hediff)null);
			}
		}
		else if ((int)thing.def.category == 2)
		{
			CompRottable val = ThingCompUtility.TryGetComp<CompRottable>(thing);
			if (options.causesRotting && val != null && (int)val.Stage < 2)
			{
				val.RotProgress += options.rotProgressPerDamage;
			}
		}
	}

	public static IEnumerable<Pawn> RandomlySelectedItems(IEnumerable<Pawn> sequence, int count)
	{
		return GenCollection.InRandomOrder<Pawn>(sequence, (IList<Pawn>)null).Take(count);
	}
}
